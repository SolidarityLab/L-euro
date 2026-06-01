# DTEP-F Transformation Layer

**Version:** 0.1-draft
**Status:** Specification in progress
**Date:** 2026-06-01
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

The transformation layer (Layers 3 and 4 as an atomic operation) is the central cryptographic component of DTEP-F. It accepts EN 16931 XML invoice data from Peppol Corner 4 and produces two cryptographically bound artifacts: a full encrypted JSON audit record and a public DTEP JSON object with the six ontological sets M0–M5.

The two layers are not sequential — they constitute one atomic Taler Exchange operation. GNU Taler Exchange is the sole trust anchor in the transformation.

---

## 2. GNU Taler DD-18 — Context and Extension

GNU Taler Design Document DD-18 defines the forgettable fields mechanism as a cryptographic primitive for confidential JSON data storage: specifically formatted fields are marked for potential erasure by replacing their values with a salted hash, while the structural validity of the document is preserved and can be verified without access to the original value.

DTEP-F is the first implementation of DD-18 in a tax reporting context. The extension is in two directions:

**First** — the salt for DD-18 scrubbing is derived from the M0 coin commitment, not an independent random value. This cryptographically binds the scrubbing to the invoice identifier.

**Second** — DD-18 scrubbing and coin commitment generation are unified in one atomic Exchange operation, not sequential steps. Taler Exchange is the sole entity that holds the salt.

---

## 3. The Atomic Taler Exchange Operation

On receipt of EN 16931 XML from Corner 4, the Corner 5 Middleware submits the object to Taler Exchange. Exchange executes the following atomic operation:

### Step 1 — Coin commitment for M0

Exchange generates a Taler blind signature coin commitment over the invoice identifier. The coin commitment is non-deterministic: even with a known invoice identifier, the output is unpredictable without Exchange participation. The M0 element is produced.

### Step 2 — DD-18 salt derivation

A DD-18 salt is derived from the M0 coin commitment via HKDF (RFC 5869). The salt is unique per transaction and is not stored outside Exchange.

### Step 3 — DD-18 scrubbing

All forgettable fields in the EN 16931 XML — VAT numbers, entity names, addresses, IBANs — are replaced with SHA512(salt ∥ original_value). The document structure is preserved. Original values are stored encrypted by Exchange only.

### Step 4 — JCS canonicalisation (RFC 8785)

The scrubbed JSON object is canonicalised per RFC 8785 for deterministic output independent of key ordering.

### Step 5 — Extraction of M1–M5

The ontological sets are extracted from the canonicalised object:
- M1: timestamp → hourly bucket (YYYY-MM-DDThh:00:00Z)
- M2: CPV code
- M3: NACE code (seller)
- M4: NACE code (buyer)
- M5: amount in EUR

### Step 6 — Ed25519 signature (RFC 8032)

Exchange signs the public DTEP JSON object (M0–M5) with the institutional Ed25519 key.

### Output — two artifacts

**Artifact A — Full encrypted JSON:** original forgettable field values, encrypted with a key derived from the salt. Stored by Exchange. Accessible on Audit Request.

**Artifact B — Public DTEP JSON:** the six ontological sets M0–M5, signed by Exchange. Transmitted to the DRRDB public level.

```
EN 16931 XML (Corner 4)
        │
        ▼
Taler Exchange [atomic operation]
        │
        ├─ Step 1: coin commitment → M0
        ├─ Step 2: HKDF(M0) → salt
        ├─ Step 3: SHA512(salt ∥ field) → scrubbed fields
        ├─ Step 4: JCS canonicalisation (RFC 8785)
        ├─ Step 5: extract M1–M5
        └─ Step 6: Ed25519 sign (RFC 8032)
        │
        ├─────────────────────────┐
        ▼                         ▼
Artifact A                  Artifact B
Full encrypted JSON         Public DTEP JSON
(Exchange custody)          (DRRDB public level)
```

---

## 4. Cryptographic Properties

### Atomicity

It is impossible for a valid public DTEP JSON to exist without a corresponding encrypted audit record in Exchange. The two artifacts are inseparable by construction. A middleware compromise does not affect the audit record.

### Unlinkability

An observer of the DRRDB public level cannot link two M0 elements to the same invoice without access to Exchange. The coin commitment is non-deterministic — knowledge of the invoice identifier does not predict the M0 value.

### Single trust anchor

Only Exchange holds the salt. Corner 5 Middleware, DRRDB, and the analytical layer have no access to it. This is a structural guarantee, not a policy commitment.

### Verification without disclosure

The structural validity of the public DTEP JSON can be verified by any party without access to forgettable fields. The Ed25519 signature is publicly verifiable. The scrubbed field values can be verified by any party holding the salt — without that party needing access to the full encrypted record.

### Selective audit

On Audit Request, the tax authority receives the salt from Exchange for a specific M0 element — and only for that element. Not for the full DRRDB dataset. The scope of disclosure is bounded by the audit trigger.

---

## 5. Forgettable Fields in EN 16931 Context

The following EN 16931 semantic elements are designated as forgettable fields and are subject to DD-18 scrubbing:

| EN 16931 Element | Content | Scrubbing |
|---|---|---|
| BT-27 Seller name | Legal entity name | SHA512(salt ∥ value) |
| BT-29 Seller identifier | VAT number / EIK | SHA512(salt ∥ value) |
| BT-44 Buyer name | Legal entity name | SHA512(salt ∥ value) |
| BT-46 Buyer identifier | VAT number / EIK | SHA512(salt ∥ value) |
| BT-34 Seller IBAN | Bank account | SHA512(salt ∥ value) |
| BT-35 Seller address | Street address | SHA512(salt ∥ value) |
| BT-50 Buyer address | Street address | SHA512(salt ∥ value) |

Elements retained in the public DTEP JSON without scrubbing: BT-2 (invoice date → M1), BT-158 (CPV → M2), BT-29-scheme (NACE seller → M3), BT-46-scheme (NACE buyer → M4), BT-109 (tax exclusive amount → M5).

The complete forgettable fields mapping for EN 16931-1:2025 semantic elements is an open issue for v0.2.

---

## 6. Invoice Lifecycle and Coin Commitment

EN 16931 defines four invoice lifecycle events: issuance, cancellation, correction, credit note. Each event generates a new coin commitment in M0 and a new DD-18 scrubbing with a new salt.

The relationship between linked lifecycle events is maintained in the DRRDB protected level through Exchange reference — not in the public layer. The public layer treats each event as an independent transaction with an independent M0.

This preserves the unlinkability property in the public layer: an observer cannot establish that two M0 elements are related by cancellation or correction of the same invoice.

---

## 7. Relation to Taler Ecosystem

| Taler Component | Role in Transformation Layer |
|---|---|
| DD-18 forgettable fields | Scrubbing mechanism for subject identifiers |
| Blind signature scheme | Coin commitment generation for M0 |
| Exchange Ed25519 key | Signing authority for public DTEP JSON |
| Exchange audit API | Salt custody and selective disclosure on Audit Request |
| HKDF (RFC 5869) | Salt derivation from M0 coin commitment |

DTEP-F extends the DD-18 mechanism in two ways not present in existing Taler implementations: salt derivation from coin commitment (binding scrubbing to invoice identity) and application in a tax reporting regulatory context (selective disclosure to tax authority on audit trigger rather than to payment counterparty).

---

## 8. Open Issues

- [ ] Formal specification of coin commitment scheme for M0 in invoice identifier context (v0.2)
- [ ] HKDF parameters for DD-18 salt derivation — hash function, length, info string (v0.2)
- [ ] Complete forgettable fields mapping for EN 16931-1:2025 semantic elements (v0.2)
- [ ] Lifecycle referencing scheme in protected level for cancellation and credit note (v0.3)
- [ ] Exchange API specification for Audit Request salt disclosure (v0.3)

---

## References

- GNU Taler DD-18: https://docs.taler.net/design-documents/018-forgettable-json.html
- RFC 8785 JCS: https://www.rfc-editor.org/rfc/rfc8785
- RFC 8032 Ed25519: https://www.rfc-editor.org/rfc/rfc8032
- RFC 5869 HKDF: https://www.rfc-editor.org/rfc/rfc5869
- EN 16931-1:2025: https://www.cen.eu/work/areas/ict/ebusiness/pages/ws-einvoicing.aspx
