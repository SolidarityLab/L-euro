# DTEP-F Signing Layer

**Version:** 0.1-draft
**Status:** Specification in progress
**Date:** 2026-06-01
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

The signing layer (Layer 4) is integrated into the atomic Taler Exchange operation described in [transformation-layer.md](transformation-layer.md). This document formally specifies the key infrastructure, verification model, and key management independently of the transformation context.

The signing layer has one invariant: Corner 5 Middleware holds no signing keys. The sole signing authority is Taler Exchange.

---

## 2. Key Infrastructure

Taler Exchange maintains two key types relevant to DTEP-F:

### Exchange signing key

Ed25519 key pair used for signing public DTEP JSON objects. Short-term key with rotation per Taler Exchange protocol. The public key is accessible from the Exchange /keys endpoint. Validity period: to be defined per deployment context (see Open Issues).

### Exchange master key

Long-term Ed25519 key used for signing signing key certificates. Verification chain:

```
Exchange master key
        │
        └─ signs → signing key certificate
                        │
                        └─ verifies → DTEP JSON signature
```

The master key is held in HSM storage. HSM requirements for institutional deployment are an open issue for v0.2.

---

## 3. Verification Model

Every public DTEP JSON object carries an Ed25519 signature verifiable by any party with access to the Exchange public key. Verification requires no special rights and no access to the DRRDB protected level.

Verification procedure:

**Step 1** — Retrieve signing key from Exchange /keys endpoint.

**Step 2** — Verify signing key certificate against Exchange master key.

**Step 3** — JCS canonicalisation of the public DTEP JSON object (RFC 8785).

**Step 4** — Ed25519 verification of the signature over the canonicalised object.

Verification is public and stateless. Any party — tax authority, auditor, counterparty, or third-party verifier — can independently verify any DRR record without Exchange participation at verification time.

---

## 4. Signing in Offline Scenario

Under Deployment Scenario 2 (batch mode), Corner 5 Middleware accumulates EN 16931 objects locally. On reconnection to Exchange, objects are submitted for atomic processing in batch. Exchange signs each object with the signing key valid at the moment of signing — not at the moment of receipt from Corner 4.

The timestamp in M1 reflects the moment of the tax event — not the moment of signing. The difference between the two moments is recorded in Artifact A and is accessible on Audit Request. The DRR record remains valid regardless of the signing delay.

---

## 5. Key Rotation and Verification Archive

Taler Exchange publishes signing key certificates with a defined validity period. On rotation, expired keys remain in the /keys archive for verification of historically signed objects.

DRRDB maintains a local archive of Exchange signing key certificates at the moment of signing of each DRR record. This guarantees long-term verification independent of Exchange availability — a DRR record signed in 2026 remains verifiable in 2036 without Exchange being online.

---

## 6. Open Issues

The following are active research and specification questions. They define the forward work agenda for the signing layer and are not gaps in the current specification — they are the boundary of the known.

**Cross-border Exchange federation**
In a multi-Member-State deployment, which Exchange instance signs DRR records when seller and buyer are in different jurisdictions? The protocol must define a federation model for mutual recognition of Exchange signing keys between national instances. This is structurally analogous to the Peppol authority federation model but applied to cryptographic signing rather than transport accreditation.

**Revocation under legal proceedings**
When a signing key is compromised, how are already-signed DRR records treated? Taler Exchange has its own revocation model, but its application to tax evidence records with legal consequences requires a separate specification. A compromised key does not invalidate the underlying transaction — it invalidates the cryptographic proof. The protocol must define the evidentiary status of records signed by a revoked key.

**Threshold signing for high-volume deployment**
A single Exchange instance is a potential bottleneck and single point of failure at national transaction volumes. Threshold Ed25519 (multi-party signing requiring k-of-n Exchange instances) is an open research question in the Taler ecosystem. DTEP-F is a concrete use case motivating this work — national DRR infrastructure cannot accept a single point of failure.

**Signing key validity period for tax evidence**
Standard Taler signing key rotation is optimised for payment privacy. DRR records are legal evidence with retention periods defined by national tax law (typically 5–10 years). The signing key validity period and archive retention policy must be aligned with tax law requirements, not payment system defaults.

**HSM requirements for institutional Exchange deployment**
The Exchange master key must be held in HSM storage in any institutional deployment. HSM selection criteria, key ceremony requirements, and audit trail for key operations are outside current Taler documentation and require specification for the DTEP-F deployment context.

---

## References

- GNU Taler Exchange key management: https://docs.taler.net/taler-exchange-manual.html
- RFC 8032 Ed25519: https://www.rfc-editor.org/rfc/rfc8032
- RFC 8785 JCS: https://www.rfc-editor.org/rfc/rfc8785
