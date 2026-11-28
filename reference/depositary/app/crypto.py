# SPDX-License-Identifier: EUPL-1.2
"""Canonical JSON (RFC 8785), hashes and detached JWS (RFC 7515 App. F) with ES256."""
import base64
import hashlib
import json

import rfc8785
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64u_dec(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def jcs(obj) -> bytes:
    return rfc8785.dumps(obj)


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def hash_obj(obj) -> str:
    """base64url SHA-256 of the JCS form of obj (43 characters)."""
    return b64u(sha256(jcs(obj)))


# --- keys -----------------------------------------------------------------

def public_jwk(pub: ec.EllipticCurvePublicKey) -> dict:
    n = pub.public_numbers()
    return {
        "kty": "EC",
        "crv": "P-256",
        "x": b64u(n.x.to_bytes(32, "big")),
        "y": b64u(n.y.to_bytes(32, "big")),
    }


def jwk_to_public(jwk: dict) -> ec.EllipticCurvePublicKey:
    if jwk.get("kty") != "EC" or jwk.get("crv") != "P-256":
        raise ValueError("only EC P-256 keys are supported")
    x = int.from_bytes(b64u_dec(jwk["x"]), "big")
    y = int.from_bytes(b64u_dec(jwk["y"]), "big")
    return ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1()).public_key()


def jwk_thumbprint(jwk: dict) -> str:
    """RFC 7638 thumbprint, used as key id."""
    return hash_obj({k: jwk[k] for k in ("crv", "kty", "x", "y")})


# --- detached JWS -----------------------------------------------------------

def unsigned(request: dict) -> dict:
    return {k: v for k, v in request.items() if k != "acceptorSignature"}


def sign_detached(priv: ec.EllipticCurvePrivateKey, kid: str, payload_obj: dict) -> str:
    header = b64u(json.dumps({"alg": "ES256", "kid": kid}, separators=(",", ":")).encode())
    signing_input = header.encode() + b"." + b64u(jcs(payload_obj)).encode()
    der = priv.sign(signing_input, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    return header + ".." + b64u(r.to_bytes(32, "big") + s.to_bytes(32, "big"))


def jws_kid(jws: str) -> str | None:
    try:
        return json.loads(b64u_dec(jws.split(".")[0])).get("kid")
    except Exception:
        return None


def verify_detached(pub: ec.EllipticCurvePublicKey, jws: str, payload_obj: dict) -> bool:
    try:
        header_b64, empty, sig_b64 = jws.split(".")
        if empty != "":
            return False
        header = json.loads(b64u_dec(header_b64))
        if header.get("alg") != "ES256":
            return False
        raw = b64u_dec(sig_b64)
        if len(raw) != 64:
            return False
        der = encode_dss_signature(int.from_bytes(raw[:32], "big"), int.from_bytes(raw[32:], "big"))
        signing_input = header_b64.encode() + b"." + b64u(jcs(payload_obj)).encode()
        pub.verify(der, signing_input, ec.ECDSA(hashes.SHA256()))
        return True
    except (InvalidSignature, ValueError, KeyError, json.JSONDecodeError):
        return False
