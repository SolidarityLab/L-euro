# SPDX-License-Identifier: EUPL-1.2
"""L-euro reference depositary: a minimal register for a test pilot.

Implements spec v0.1: holder accounts (партида) with passkeys (7.2), an
append-only hash-chained event log (6.1), and redemption over channel A
(7.3) with the evidence of 7.6. Not production software: see README.md.
"""
import json
from contextlib import asynccontextmanager
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import jsonschema
import psycopg
import segno
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from . import crypto

HERE = Path(__file__).parent
SCHEMAS = Path(os.environ.get("LEURO_SCHEMAS", HERE.parent / "schemas"))
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql:///leuro")
DOMAIN = os.environ.get("DOMAIN", "localhost")
ORIGIN = os.environ.get("ORIGIN", f"https://{DOMAIN}")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
DEMO = os.environ.get("DEMO", "1") == "1"
DEMO_MAX_ACCOUNTS = int(os.environ.get("DEMO_MAX_ACCOUNTS", "1000"))
MAX_WINDOW = timedelta(seconds=300)
SKEW = timedelta(seconds=30)
CEREMONY = timedelta(seconds=180)

DEMO_ACCEPTOR = "urn:l-euro:demo:acceptor:canteen"
DEMO_GOODS = {"scheme": "COICOP-2018", "code": "11.1"}
DEMO_MENU = [
    {"ref": "demo-lunch-1", "version": "1", "text": "Обедно меню 1: супа и основно", "amount": 5.2},
    {"ref": "demo-lunch-2", "version": "1", "text": "Обедно меню 2: вегетарианско", "amount": 4.8},
    {"ref": "demo-soup", "version": "1", "text": "Супа на деня", "amount": 2.0},
]


def _schema(name):
    s = json.loads((SCHEMAS / name).read_text())
    return jsonschema.Draft202012Validator(s, format_checker=jsonschema.FormatChecker())


REQUEST_SCHEMA = _schema("redemption-request.schema.json")
ENTITLEMENT_SCHEMA = _schema("entitlement.schema.json")
EVENT_SCHEMA = _schema("event.schema.json")

@asynccontextmanager
async def lifespan(_app):
    startup()
    yield


app = FastAPI(title="L-euro reference depositary", version="0.0.1", lifespan=lifespan,
              docs_url="/v0/docs", openapi_url="/v0/openapi.json", redoc_url=None)


# --- helpers ----------------------------------------------------------------

def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def num(x) -> float | int:
    d = Decimal(str(x)).quantize(Decimal("0.01"))
    return int(d) if d == d.to_integral_value() else float(d)


def new_id(prefix: str) -> str:
    return f"{prefix}{crypto.b64u(secrets.token_bytes(16))}"


def db():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def fail(status: int, code: str, msg: str):
    raise HTTPException(status, {"error": code, "message": msg})


def require_admin(authorization: str | None):
    if not ADMIN_TOKEN:
        fail(403, "admin_disabled", "admin API is disabled on this node")
    if not secrets.compare_digest(authorization or "", f"Bearer {ADMIN_TOKEN}"):
        fail(401, "unauthorized", "bad admin token")


def valid_until(spec: str, start: datetime) -> datetime:
    m = re.fullmatch(r"P(\d+)([DM])", spec or "")
    if m:
        n = int(m.group(1))
        return start + (timedelta(days=n) if m.group(2) == "D" else timedelta(days=30 * n))
    return parse_time(spec)


def append_event(cur, account: str, etype: str, entitlement: str, actor: str,
                 occurred: datetime | None = None, **extra) -> dict:
    """Append one event to the account's hash chain (spec 6.1)."""
    cur.execute("SELECT last_seq, last_hash FROM accounts WHERE ref=%s FOR UPDATE", (account,))
    acc = cur.fetchone()
    t = now()
    doc = {
        "v": "0.1",
        "eventId": new_id("urn:l-euro:event:"),
        "type": etype,
        "entitlement": entitlement,
        "account": account,
        "seq": acc["last_seq"] + 1,
        "prevHash": acc["last_hash"],
        "occurredAt": iso(occurred or t),
        "recordedAt": iso(t),
        "actor": actor,
        **extra,
    }
    EVENT_SCHEMA.validate(doc)
    h = crypto.hash_obj(doc)
    cur.execute("INSERT INTO events (event_id, account_ref, seq, doc, hash) VALUES (%s,%s,%s,%s,%s)",
                (doc["eventId"], account, doc["seq"], Jsonb(doc), h))
    cur.execute("UPDATE accounts SET last_seq=%s, last_hash=%s WHERE ref=%s", (doc["seq"], h, account))
    return doc


def issue_and_load(cur, account: str, ent: dict, actor: str) -> dict:
    """Record issue and load of an entitlement for an existing account."""
    t = now()
    ent = {**ent, "holder": {"ref": account}, "status": "loaded"}
    ent.setdefault("id", new_id("urn:l-euro:entitlement:"))
    ent.setdefault("balance", ent.get("nominal"))
    ENTITLEMENT_SCHEMA.validate(ent)
    until = valid_until(ent["validUntil"], t)
    cur.execute(
        """INSERT INTO entitlements (id, account_ref, doc, form, unit, balance, divisible,
           goods_scheme, goods_code, valid_until, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (ent["id"], account, Jsonb(ent), ent["form"], ent["unit"], Decimal(str(ent["balance"])),
         ent["divisible"], ent["goodsClass"]["scheme"], ent["goodsClass"]["code"], until, "loaded"))
    append_event(cur, account, "issue", ent["id"], actor, amount=num(ent["nominal"]), unit=ent["unit"])
    append_event(cur, account, "load", ent["id"], actor, amount=num(ent["balance"]), unit=ent["unit"],
                 balanceAfter=num(ent["balance"]))
    return ent


def covers(ent_code: str, offer_code: str) -> bool:
    return offer_code == ent_code or offer_code.startswith(ent_code + ".")


# --- startup ----------------------------------------------------------------

def startup():
    with db() as conn:
        conn.execute((HERE / "schema.sql").read_text())
        if DEMO:
            row = conn.execute("SELECT 1 FROM demo_keys WHERE acceptor_id=%s", (DEMO_ACCEPTOR,)).fetchone()
            if not row:
                priv = ec.generate_private_key(ec.SECP256R1())
                jwk = crypto.public_jwk(priv.public_key())
                pem = priv.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                         serialization.NoEncryption()).decode()
                conn.execute("INSERT INTO acceptors (id, name, jwk, kid) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                             (DEMO_ACCEPTOR, "Демо кухня (тест)", Jsonb(jwk), crypto.jwk_thumbprint(jwk)))
                conn.execute("INSERT INTO demo_keys VALUES (%s,%s)", (DEMO_ACCEPTOR, pem))


@app.exception_handler(jsonschema.ValidationError)
def schema_error(_req: Request, exc: jsonschema.ValidationError):
    return JSONResponse({"detail": {"error": "schema", "message": exc.message,
                                    "path": list(exc.absolute_path)}}, status_code=422)


# --- public -----------------------------------------------------------------

@app.get("/v0/health")
def health():
    with db() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/v0/info")
def info():
    return {"service": "L-euro reference depositary (prototype)", "spec": "0.1", "version": app.version,
            "rpId": DOMAIN, "demo": DEMO, "admin": bool(ADMIN_TOKEN),
            "notice": "Test node. Demo entitlements have no monetary value."}


@app.get("/v0/acceptors/{acceptor_id}")
def get_acceptor(acceptor_id: str):
    with db() as conn:
        row = conn.execute("SELECT id, name, jwk, kid FROM acceptors WHERE id=%s", (acceptor_id,)).fetchone()
    if not row:
        fail(404, "not_found", "unknown acceptor")
    return row


# --- admin (issuer / operator) ---------------------------------------------

@app.post("/v0/acceptors")
def register_acceptor(body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    jwk = body.get("jwk") or {}
    crypto.jwk_to_public(jwk)
    jwk = {k: jwk[k] for k in ("kty", "crv", "x", "y")}
    kid = crypto.jwk_thumbprint(jwk)
    with db() as conn:
        conn.execute("INSERT INTO acceptors (id, name, jwk, kid) VALUES (%s,%s,%s,%s)",
                     (body["id"], body.get("name", body["id"]), Jsonb(jwk), kid))
    return {"id": body["id"], "kid": kid}


@app.post("/v0/accounts")
def create_account(authorization: str | None = Header(None)):
    require_admin(authorization)
    ref = new_id("acct_")
    with db() as conn:
        conn.execute("INSERT INTO accounts (ref) VALUES (%s)", (ref,))
    return {"account": ref}


@app.post("/v0/accounts/{ref}/entitlements")
def issue_entitlement(ref: str, body: dict, authorization: str | None = Header(None)):
    require_admin(authorization)
    with db() as conn, conn.cursor() as cur:
        if not cur.execute("SELECT 1 FROM accounts WHERE ref=%s", (ref,)).fetchone():
            fail(404, "not_found", "unknown account")
        ent = issue_and_load(cur, ref, body, f"issuer:{body.get('issuer', {}).get('id', 'unknown')}")
    return ent


# --- holder: enrolment with passkey (7.2) -----------------------------------

@app.post("/v0/enrol/start")
def enrol_start():
    """Create a holder account and start passkey registration (demo mode)."""
    if not DEMO:
        fail(403, "demo_disabled", "self-service enrolment is only available in demo mode")
    with db() as conn:
        conn.execute("DELETE FROM sessions WHERE expires_at < now()")
        n = conn.execute("SELECT count(*) AS n FROM accounts").fetchone()["n"]
        if n >= DEMO_MAX_ACCOUNTS:
            fail(429, "demo_full", "demo account limit reached")
        ref = new_id("acct_")
        opts = generate_registration_options(
            rp_id=DOMAIN, rp_name="L-euro (тест)", user_id=ref.encode(), user_name="L-euro демо",
            user_display_name="L-euro демо партида", timeout=120000,
            authenticator_selection=AuthenticatorSelectionCriteria(
                resident_key=ResidentKeyRequirement.PREFERRED,
                user_verification=UserVerificationRequirement.REQUIRED))
        sid = new_id("ses_")
        conn.execute("INSERT INTO sessions (id, kind, account_ref, challenge, expires_at) VALUES (%s,'enrol',%s,%s,%s)",
                     (sid, ref, opts.challenge, now() + CEREMONY))
    return {"session": sid, "options": json.loads(options_to_json(opts))}


@app.post("/v0/enrol/finish")
def enrol_finish(body: dict):
    with db() as conn, conn.cursor() as cur:
        s = cur.execute("DELETE FROM sessions WHERE id=%s AND kind='enrol' AND expires_at > now() RETURNING *",
                        (body.get("session"),)).fetchone()
        if not s:
            fail(400, "session", "unknown or expired session")
        try:
            v = verify_registration_response(credential=body["credential"], expected_challenge=s["challenge"],
                                             expected_rp_id=DOMAIN, expected_origin=ORIGIN,
                                             require_user_verification=True)
        except Exception as e:
            fail(400, "webauthn", f"passkey registration failed: {e}")
        ref = s["account_ref"]
        cur.execute("INSERT INTO accounts (ref) VALUES (%s)", (ref,))
        cur.execute("INSERT INTO credentials (id, account_ref, public_key, sign_count) VALUES (%s,%s,%s,%s)",
                    (crypto.b64u(v.credential_id), ref, v.credential_public_key, v.sign_count))
        ent = issue_and_load(cur, ref, {
            "form": "voucher", "programme": "urn:l-euro:programme:demo-meal",
            "issuer": {"id": "urn:l-euro:demo:issuer"},
            "payers": [{"party": {"id": "urn:l-euro:demo:payer"}, "share": 1}],
            "acceptanceNetwork": {"category": "catering"},
            "unit": "EUR", "nominal": 50, "goodsClass": DEMO_GOODS, "divisible": True,
            "validFrom": "load", "validUntil": "P30D", "transferable": False, "convertible": False,
            "coverMode": "prepaid", "remainderRule": "extinguish",
            "signature": "DEMO-UNSIGNED", "revocationUri": f"{ORIGIN}/v0/revocation",
        }, "issuer:urn:l-euro:demo:issuer")
    return {"account": ref, "entitlement": ent["id"]}


@app.get("/v0/accounts/{ref}")
def get_account(ref: str):
    """Holder view. The account ref is an unguessable bearer reference in this prototype."""
    with db() as conn:
        if not conn.execute("SELECT 1 FROM accounts WHERE ref=%s", (ref,)).fetchone():
            fail(404, "not_found", "unknown account")
        ents = conn.execute("SELECT doc, balance, status, valid_until FROM entitlements WHERE account_ref=%s "
                            "ORDER BY created_at", (ref,)).fetchall()
        evs = conn.execute("SELECT doc, hash FROM events WHERE account_ref=%s ORDER BY seq", (ref,)).fetchall()
    return {
        "account": ref,
        "entitlements": [{**e["doc"], "balance": num(e["balance"]), "status": e["status"],
                          "validUntil": iso(e["valid_until"])} for e in ents],
        "events": [{**e["doc"], "hash": e["hash"]} for e in evs],
    }


@app.get("/v0/accounts/{ref}/verify")
def verify_chain(ref: str):
    with db() as conn:
        evs = conn.execute("SELECT doc, hash FROM events WHERE account_ref=%s ORDER BY seq", (ref,)).fetchall()
    prev, problems = "", []
    for i, e in enumerate(evs):
        d = e["doc"]
        if d["seq"] != i:
            problems.append(f"seq {d['seq']} at position {i}")
        if d["prevHash"] != prev:
            problems.append(f"broken link at seq {d['seq']}")
        if crypto.hash_obj(d) != e["hash"]:
            problems.append(f"hash mismatch at seq {d['seq']}")
        prev = e["hash"]
    return {"account": ref, "events": len(evs), "head": prev, "valid": not problems, "problems": problems}


# --- redemption, channel A (7.3) --------------------------------------------

def check_request(conn, req: dict) -> dict:
    REQUEST_SCHEMA.validate(req)
    acc = conn.execute("SELECT * FROM acceptors WHERE id=%s", (req["acceptor"],)).fetchone()
    if not acc:
        fail(400, "acceptor", "acceptor is not registered at this depositary")
    if crypto.jws_kid(req["acceptorSignature"]) not in (None, acc["kid"]):
        fail(400, "signature", "signature key is not the acceptor's registered key")
    if not crypto.verify_detached(crypto.jwk_to_public(acc["jwk"]), req["acceptorSignature"],
                                  crypto.unsigned(req)):
        fail(400, "signature", "acceptor signature is invalid")
    issued, expires, t = parse_time(req["issuedAt"]), parse_time(req["expiresAt"]), now()
    if issued > t + SKEW or expires < t or expires - issued > MAX_WINDOW:
        fail(400, "expired", "the request is outside its validity window")
    return acc


def public_result(result: dict) -> dict:
    """What anyone holding the request may learn: confirmation, not the holder's balance (spec 7)."""
    keep = ("eventId", "acceptor", "offer", "offerHash", "amount", "unit", "recordedAt")
    return {k: result[k] for k in keep}


def find_entitlement(conn, account: str, req: dict):
    rows = conn.execute(
        "SELECT * FROM entitlements WHERE account_ref=%s AND status='loaded' AND unit=%s AND goods_scheme=%s "
        "AND (valid_until IS NULL OR valid_until > now()) AND balance >= %s ORDER BY valid_until NULLS LAST",
        (account, req["unit"], req["goodsClass"]["scheme"], Decimal(str(req["amount"])))).fetchall()
    for r in rows:
        if covers(r["goods_code"], req["goodsClass"]["code"]) and (
                r["divisible"] or Decimal(str(req["amount"])) == Decimal(str(req["amount"])).to_integral_value()):
            return r
    return None


@app.post("/v0/redeem/start")
def redeem_start(body: dict):
    req, account = body.get("request") or {}, body.get("account")
    with db() as conn:
        conn.execute("DELETE FROM sessions WHERE expires_at < now()")
        done = conn.execute("SELECT result FROM redemptions WHERE nonce=%s", (req.get("nonce"),)).fetchone()
        if done:
            return {"status": "redeemed", "result": public_result(done["result"])}
        acc = check_request(conn, req)
        ent = find_entitlement(conn, account, req)
        if not ent:
            fail(402, "not_covered", "no entitlement covers this goods class and amount")
        creds = conn.execute("SELECT id FROM credentials WHERE account_ref=%s", (account,)).fetchall()
        dep_nonce = secrets.token_bytes(16)
        challenge = crypto.sha256(crypto.jcs(req) + ent["id"].encode() + dep_nonce)
        opts = generate_authentication_options(
            rp_id=DOMAIN, challenge=challenge, timeout=120000,
            allow_credentials=[PublicKeyCredentialDescriptor(id=crypto.b64u_dec(c["id"])) for c in creds],
            user_verification=UserVerificationRequirement.REQUIRED)
        sid = new_id("ses_")
        conn.execute("INSERT INTO sessions (id, kind, account_ref, challenge, data, expires_at) "
                     "VALUES (%s,'redeem',%s,%s,%s,%s)",
                     (sid, account, challenge, Jsonb({"request": req, "entitlement": ent["id"],
                                                      "depositaryNonce": crypto.b64u(dep_nonce)}),
                      min(now() + CEREMONY, parse_time(req["expiresAt"]))))
    return {
        "status": "confirm",
        "session": sid,
        "display": {"acceptor": acc["name"], "acceptorId": acc["id"], "offer": req["offer"],
                    "amount": req["amount"], "unit": req["unit"], "balance": num(ent["balance"]),
                    "entitlement": ent["id"]},
        "options": json.loads(options_to_json(opts)),
    }


@app.post("/v0/redeem/finish")
def redeem_finish(body: dict):
    cred = body.get("credential") or {}
    with db() as conn, conn.cursor() as cur:
        s = cur.execute("DELETE FROM sessions WHERE id=%s AND kind='redeem' AND expires_at > now() RETURNING *",
                        (body.get("session"),)).fetchone()
        if not s:
            fail(400, "session", "unknown or expired session")
        req, account = s["data"]["request"], s["account_ref"]
        c = cur.execute("SELECT * FROM credentials WHERE id=%s AND account_ref=%s",
                        (cred.get("id"), account)).fetchone()
        if not c:
            fail(400, "credential", "passkey is not registered for this account")
        try:
            v = verify_authentication_response(
                credential=cred, expected_challenge=s["challenge"], expected_rp_id=DOMAIN,
                expected_origin=ORIGIN, credential_public_key=bytes(c["public_key"]),
                credential_current_sign_count=c["sign_count"], require_user_verification=True)
        except Exception as e:
            fail(400, "webauthn", f"passkey check failed: {e}")
        # Serialise per account, then re-check idempotency and balance.
        cur.execute("SELECT 1 FROM accounts WHERE ref=%s FOR UPDATE", (account,))
        done = cur.execute("SELECT result FROM redemptions WHERE nonce=%s", (req["nonce"],)).fetchone()
        if done:
            return {"status": "redeemed", "result": public_result(done["result"])}
        ent = cur.execute("SELECT * FROM entitlements WHERE id=%s FOR UPDATE", (s["data"]["entitlement"],)).fetchone()
        amount = Decimal(str(req["amount"]))
        if ent["status"] != "loaded" or ent["balance"] < amount:
            fail(402, "not_covered", "balance no longer covers the amount")
        after = ent["balance"] - amount
        status = "loaded" if after > 0 else "redeemed"
        cur.execute("UPDATE entitlements SET balance=%s, status=%s WHERE id=%s", (after, status, ent["id"]))
        cur.execute("UPDATE credentials SET sign_count=%s WHERE id=%s", (v.new_sign_count, c["id"]))
        r = cred.get("response", {})
        ev = append_event(
            cur, account, "redeem", ent["id"], f"acceptor:{req['acceptor']}",
            amount=num(amount), unit=req["unit"], balanceAfter=num(after), idempotencyKey=req["nonce"],
            evidence={"offerHash": req["offer"]["offerHash"], "acceptorSignature": req["acceptorSignature"],
                      "webauthn": {"credentialId": c["id"], "authenticatorData": r.get("authenticatorData", ""),
                                   "clientDataJSON": r.get("clientDataJSON", ""),
                                   "signature": r.get("signature", "")}})
        result = {"eventId": ev["eventId"], "acceptor": req["acceptor"], "offer": req["offer"]["ref"],
                  "offerHash": req["offer"]["offerHash"], "amount": num(amount), "unit": req["unit"],
                  "balanceAfter": num(after), "recordedAt": ev["recordedAt"]}
        cur.execute("INSERT INTO redemptions (nonce, event_id, acceptor_id, result) VALUES (%s,%s,%s,%s)",
                    (req["nonce"], ev["eventId"], req["acceptor"], Jsonb(result)))
    return {"status": "redeemed", "result": result}


@app.get("/v0/redeem/status/{nonce}")
def redeem_status(nonce: str):
    """For the acceptor system: has this request been redeemed? (stands in for the webhook of 7.3)"""
    with db() as conn:
        row = conn.execute("SELECT result FROM redemptions WHERE nonce=%s", (nonce,)).fetchone()
    if not row:
        return {"redeemed": False, "result": None}
    return {"redeemed": True, "result": public_result(row["result"])}


# --- demo acceptor ----------------------------------------------------------

def demo_offer(item: dict) -> dict:
    canonical = {"ref": item["ref"], "version": item["version"], "text": item["text"],
                 "amount": item["amount"], "unit": "EUR", "goodsClass": DEMO_GOODS}
    return {**canonical, "offerHash": crypto.hash_obj(canonical)}


@app.get("/v0/demo/menu")
def demo_menu():
    if not DEMO:
        fail(404, "not_found", "demo disabled")
    return {"acceptor": DEMO_ACCEPTOR, "items": [demo_offer(i) for i in DEMO_MENU]}


@app.post("/v0/demo/request")
def demo_request(body: dict):
    """Acts as the demo kitchen's till: creates and signs a redemption request."""
    if not DEMO:
        fail(404, "not_found", "demo disabled")
    item = next((i for i in DEMO_MENU if i["ref"] == body.get("ref")), None)
    if not item:
        fail(400, "item", "unknown menu item")
    o = demo_offer(item)
    with db() as conn:
        k = conn.execute("SELECT d.private_pem, a.kid FROM demo_keys d JOIN acceptors a ON a.id=d.acceptor_id "
                         "WHERE d.acceptor_id=%s", (DEMO_ACCEPTOR,)).fetchone()
    priv = serialization.load_pem_private_key(k["private_pem"].encode(), None)
    t = now()
    req = {"v": "0.1", "acceptor": DEMO_ACCEPTOR,
           "offer": {"ref": o["ref"], "version": o["version"], "offerHash": o["offerHash"], "text": o["text"]},
           "amount": o["amount"], "unit": "EUR", "goodsClass": DEMO_GOODS,
           "nonce": crypto.b64u(secrets.token_bytes(16)), "issuedAt": iso(t), "expiresAt": iso(t + timedelta(seconds=120))}
    req["acceptorSignature"] = crypto.sign_detached(priv, k["kid"], req)
    url = f"{ORIGIN}/app/#r={crypto.b64u(json.dumps(req, separators=(',', ':'), ensure_ascii=False).encode())}"
    svg = segno.make(url, error="l").svg_inline(scale=4, border=2)
    return {"request": req, "url": url, "qrSvg": svg}


# --- pages ------------------------------------------------------------------

@app.get("/app/")
def holder_page():
    return FileResponse(HERE / "static" / "holder.html", headers={"Cache-Control": "no-store"})


@app.get("/app/acceptor")
def acceptor_page():
    return FileResponse(HERE / "static" / "acceptor.html", headers={"Cache-Control": "no-store"})
