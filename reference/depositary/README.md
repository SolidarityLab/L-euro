# L-euro reference depositary (prototype)

A minimal register that implements the core of the
[L-euro specification v0.1](../../spec/l-euro-spec-v0.1.md) for a test pilot.
It is **not production software** and demo entitlements have no monetary value.

## What it implements

| Spec | Implemented |
|---|---|
| §5 Data model | Entitlements are validated against `schemas/entitlement.schema.json`. |
| §6.1 Event log | Append-only (enforced by a database trigger), one hash chain per holder account (`seq`, `prevHash`), events validated against `schemas/event.schema.json`. `GET /v0/accounts/{ref}/verify` recomputes the chain. |
| §7.2 Passkey | WebAuthn registration with `userVerification: required`. Only the public key, the credential ID and the counter are stored. |
| §7.3 Channel A | The acceptor's request is validated against `schemas/redemption-request.schema.json`. The depositary checks the detached JWS (ES256 over JCS, RFC 7515 App. F + RFC 8785), the time window (≤ 300 s), the nonce and the goods class. The WebAuthn challenge is `SHA-256(JCS(request) ‖ entitlement id ‖ depositary nonce)`. The debit is atomic, and the nonce is the idempotency key. |
| §7.6 Evidence | A `redeem` event records `offerHash`, `acceptorSignature`, credential ID, `authenticatorData`, `clientDataJSON` and the signature, the amount and the balance after. |
| §7 Disclosure | The acceptor's status endpoint returns the confirmation only, not the holder's balance. |

Not yet implemented:
- channels B–D and the acceptor webhook (the demo till polls `GET /v0/redeem/status/{nonce}` instead);
- `request`, `present`, `settle`, `expire`, `revoke` and `remainder` events;
- settlement aggregates (§9), issuer signatures on entitlements, and passkey enrolment for accounts created through the admin API;
- authentication of holder reads (the account reference is an unguessable bearer reference), rate limiting beyond a cap on demo accounts.

## Demo mode

With `DEMO=1` (the default) the node also offers:
- `/app/`: holder web app. It creates a holder account with a passkey and loads a €50 test voucher (goods class COICOP-2018 11.1, 30 days).
- `/app/acceptor`: demo till of a test kitchen. It signs redemption requests with a key that the node generates for this test acceptor, and shows them as a QR code.

Scan the QR code with the phone camera, confirm with the passkey, and the till shows the payment as confirmed.

## API

The OpenAPI description is served at `/v0/docs`. The admin endpoints (`POST /v0/acceptors`, `POST /v0/accounts`,
`POST /v0/accounts/{ref}/entitlements`) need `Authorization: Bearer $ADMIN_TOKEN` and are disabled when
`ADMIN_TOKEN` is empty.

## Configuration

| Variable | Meaning |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string. The schema is created at start-up. |
| `DOMAIN` | WebAuthn relying-party ID: the host name the app is served on. |
| `ORIGIN` | Expected WebAuthn origin, default `https://$DOMAIN`. |
| `ADMIN_TOKEN` | Enables the admin API. |
| `DEMO` | `1` enables self-service enrolment and the demo till. |

## Run and test

```sh
docker build -f reference/depositary/Dockerfile -t leuro-depositary .   # from the repository root
```

The tests run a software passkey through enrolment and redemption against a scratch database:

```sh
cd reference/depositary
pip install -r requirements.txt pytest httpx cbor2
DATABASE_URL=postgresql:///leuro_test LEURO_SCHEMAS=../../schemas pytest -q tests
```

The test node of the pilot is deployed from
[SolidarityLab/infra](https://github.com/SolidarityLab/infra), which pins a commit of this repository.

Licence: EUPL 1.2.
