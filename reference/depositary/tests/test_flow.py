# SPDX-License-Identifier: EUPL-1.2
"""End-to-end test of enrolment and channel-A redemption with a software passkey.

Needs a PostgreSQL database in DATABASE_URL (it is wiped).
"""
import json
import os
import secrets
from datetime import datetime, timedelta, timezone

import cbor2
import psycopg
import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

os.environ.setdefault("DOMAIN", "pilot.test")
os.environ.setdefault("ADMIN_TOKEN", "test-admin-token")
os.environ["DEMO"] = "1"

from fastapi.testclient import TestClient  # noqa: E402

from app import crypto, main  # noqa: E402

ORIGIN = f"https://{main.DOMAIN}"


class SoftPasskey:
    """Minimal WebAuthn authenticator: ES256, 'none' attestation, UV set."""

    def __init__(self):
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.cred_id = secrets.token_bytes(16)
        self.count = 0
        self.rp_hash = crypto.sha256(main.DOMAIN.encode())

    def _client_data(self, typ, challenge):
        return json.dumps({"type": typ, "challenge": challenge, "origin": ORIGIN, "crossOrigin": False}).encode()

    def create(self, options):
        n = self.key.public_key().public_numbers()
        cose = cbor2.dumps({1: 2, 3: -7, -1: 1, -2: n.x.to_bytes(32, "big"), -3: n.y.to_bytes(32, "big")})
        auth = (self.rp_hash + bytes([0x45]) + self.count.to_bytes(4, "big") + bytes(16)
                + len(self.cred_id).to_bytes(2, "big") + self.cred_id + cose)
        att = cbor2.dumps({"fmt": "none", "attStmt": {}, "authData": auth})
        cd = self._client_data("webauthn.create", options["challenge"])
        cid = crypto.b64u(self.cred_id)
        return {"id": cid, "rawId": cid, "type": "public-key", "clientExtensionResults": {},
                "response": {"clientDataJSON": crypto.b64u(cd), "attestationObject": crypto.b64u(att)}}

    def get(self, options, uv=True):
        self.count += 1
        auth = self.rp_hash + bytes([0x05 if uv else 0x01]) + self.count.to_bytes(4, "big")
        cd = self._client_data("webauthn.get", options["challenge"])
        sig = self.key.sign(auth + crypto.sha256(cd), ec.ECDSA(hashes.SHA256()))
        cid = crypto.b64u(self.cred_id)
        return {"id": cid, "rawId": cid, "type": "public-key", "clientExtensionResults": {},
                "response": {"clientDataJSON": crypto.b64u(cd), "authenticatorData": crypto.b64u(auth),
                             "signature": crypto.b64u(sig), "userHandle": None}}


@pytest.fixture(scope="module")
def client():
    with psycopg.connect(main.DATABASE_URL, autocommit=True) as c:
        c.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    with TestClient(main.app) as cl:
        yield cl


def enrol(client):
    pk = SoftPasskey()
    s = client.post("/v0/enrol/start").json()
    r = client.post("/v0/enrol/finish", json={"session": s["session"], "credential": pk.create(s["options"])})
    assert r.status_code == 200, r.text
    return pk, r.json()["account"]


def demo_req(client, ref="demo-lunch-1"):
    return client.post("/v0/demo/request", json={"ref": ref}).json()["request"]


def pay(client, pk, account, req, uv=True):
    s = client.post("/v0/redeem/start", json={"account": account, "request": req})
    if s.status_code != 200 or s.json()["status"] != "confirm":
        return s
    return client.post("/v0/redeem/finish", json={"session": s.json()["session"],
                                                   "credential": pk.get(s.json()["options"], uv)})


def test_enrol_gives_demo_voucher(client):
    _, acct = enrol(client)
    a = client.get(f"/v0/accounts/{acct}").json()
    assert a["entitlements"][0]["balance"] == 50
    assert [e["type"] for e in a["events"]] == ["issue", "load"]
    assert client.get(f"/v0/accounts/{acct}/verify").json()["valid"]


def test_redeem_debits_once_and_is_idempotent(client):
    pk, acct = enrol(client)
    req = demo_req(client)
    r = pay(client, pk, acct, req)
    assert r.status_code == 200, r.text
    assert r.json()["result"]["balanceAfter"] == 44.8
    # Same nonce again: original result, no second debit, no balance leak.
    again = client.post("/v0/redeem/start", json={"account": acct, "request": req}).json()
    assert again["status"] == "redeemed" and "balanceAfter" not in again["result"]
    a = client.get(f"/v0/accounts/{acct}").json()
    assert a["entitlements"][0]["balance"] == 44.8
    ev = a["events"][-1]
    assert ev["type"] == "redeem" and ev["idempotencyKey"] == req["nonce"]
    assert ev["evidence"]["offerHash"] == req["offer"]["offerHash"]
    assert ev["evidence"]["webauthn"]["signature"]
    assert client.get(f"/v0/accounts/{acct}/verify").json()["valid"]
    st = client.get(f"/v0/redeem/status/{req['nonce']}").json()
    assert st["redeemed"] and "balanceAfter" not in st["result"]


def test_challenge_binds_request_entitlement_and_nonce(client):
    pk, acct = enrol(client)
    req = demo_req(client)
    s = client.post("/v0/redeem/start", json={"account": acct, "request": req}).json()
    with psycopg.connect(main.DATABASE_URL) as c:
        d = c.execute("SELECT data, challenge FROM sessions WHERE id=%s", (s["session"],)).fetchone()
    data, challenge = d
    expect = crypto.sha256(crypto.jcs(req) + data["entitlement"].encode() + crypto.b64u_dec(data["depositaryNonce"]))
    assert bytes(challenge) == expect
    assert s["options"]["challenge"] == crypto.b64u(expect)


def test_tampered_request_is_rejected(client):
    pk, acct = enrol(client)
    req = demo_req(client)
    req["amount"] = 0.01
    r = client.post("/v0/redeem/start", json={"account": acct, "request": req})
    assert r.status_code == 400 and r.json()["detail"]["error"] == "signature"


def test_expired_request_is_rejected(client):
    pk, acct = enrol(client)
    with psycopg.connect(main.DATABASE_URL) as c:
        pem = c.execute("SELECT private_pem FROM demo_keys").fetchone()[0]
        kid = c.execute("SELECT kid FROM acceptors WHERE id=%s", (main.DEMO_ACCEPTOR,)).fetchone()[0]
    from cryptography.hazmat.primitives import serialization
    priv = serialization.load_pem_private_key(pem.encode(), None)
    req = demo_req(client)
    del req["acceptorSignature"]
    t = datetime.now(timezone.utc) - timedelta(minutes=10)
    req["issuedAt"], req["expiresAt"] = main.iso(t), main.iso(t + timedelta(seconds=120))
    req["acceptorSignature"] = crypto.sign_detached(priv, kid, req)
    r = client.post("/v0/redeem/start", json={"account": acct, "request": req})
    assert r.status_code == 400 and r.json()["detail"]["error"] == "expired"


def test_user_verification_is_required(client):
    pk, acct = enrol(client)
    r = pay(client, pk, acct, demo_req(client), uv=False)
    assert r.status_code == 400 and r.json()["detail"]["error"] == "webauthn"


def test_other_accounts_passkey_is_rejected(client):
    pk1, acct1 = enrol(client)
    pk2, acct2 = enrol(client)
    s = client.post("/v0/redeem/start", json={"account": acct1, "request": demo_req(client)}).json()
    r = client.post("/v0/redeem/finish", json={"session": s["session"], "credential": pk2.get(s["options"])})
    assert r.status_code == 400 and r.json()["detail"]["error"] == "credential"


def test_balance_cannot_go_negative(client):
    pk, acct = enrol(client)
    for _ in range(9):  # 9 x 5.20 = 46.80
        assert pay(client, pk, acct, demo_req(client)).status_code == 200
    r = pay(client, pk, acct, demo_req(client))  # 3.20 left
    assert r.status_code == 402
    assert pay(client, pk, acct, demo_req(client, "demo-soup")).status_code == 200
    a = client.get(f"/v0/accounts/{acct}").json()
    assert a["entitlements"][0]["balance"] == 1.2


def test_event_log_is_append_only(client):
    _, acct = enrol(client)
    with psycopg.connect(main.DATABASE_URL) as c, pytest.raises(psycopg.errors.RaiseException):
        c.execute("UPDATE events SET hash='x' WHERE account_ref=%s", (acct,))


def test_admin_flow_with_registered_acceptor(client):
    h = {"Authorization": "Bearer test-admin-token"}
    key = ec.generate_private_key(ec.SECP256R1())
    jwk = crypto.public_jwk(key.public_key())
    kid = client.post("/v0/acceptors", headers=h, json={"id": "urn:test:acceptor:x", "name": "X", "jwk": jwk}).json()["kid"]
    assert client.post("/v0/accounts").status_code in (401, 403)
    acct = client.post("/v0/accounts", headers=h).json()["account"]
    ent = client.post(f"/v0/accounts/{acct}/entitlements", headers=h, json={
        "form": "coupon", "programme": "urn:test:programme", "issuer": {"id": "urn:test:issuer"},
        "payers": [{"party": {"id": "urn:test:payer"}, "share": 1}], "acceptanceNetwork": {"acceptors": ["urn:test:acceptor:x"]},
        "unit": "count", "nominal": 3, "goodsClass": {"scheme": "COICOP-2018", "code": "11.1"}, "divisible": False,
        "validFrom": "load", "validUntil": "P7D", "transferable": False, "convertible": False,
        "coverMode": "capacity", "remainderRule": "releaseCapacity", "signature": "TEST", "revocationUri": "https://example.org/r"})
    assert ent.status_code == 200, ent.text
    bad = client.post(f"/v0/accounts/{acct}/entitlements", headers=h, json={"form": "nonsense"})
    assert bad.status_code == 422
    # Passkey enrolment for admin-created accounts is not part of this prototype; check signature path only.
    t = datetime.now(timezone.utc)
    req = {"v": "0.1", "acceptor": "urn:test:acceptor:x",
           "offer": {"ref": "meal", "version": "1", "offerHash": crypto.hash_obj({"t": "meal"})},
           "amount": 1, "unit": "count", "goodsClass": {"scheme": "COICOP-2018", "code": "11.1.2"},
           "nonce": secrets.token_hex(16), "issuedAt": main.iso(t), "expiresAt": main.iso(t + timedelta(seconds=60))}
    req["acceptorSignature"] = crypto.sign_detached(key, kid, req)
    s = client.post("/v0/redeem/start", json={"account": acct, "request": req})
    assert s.status_code == 200 and s.json()["display"]["entitlement"] == ent.json()["id"]
