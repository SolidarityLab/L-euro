# DTEP-F Conformance Testing

**Version:** 0.1-draft
**Status:** Specification in progress
**Date:** 2026-06-01
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document defines the conformance requirements and test profiles for DTEP-F implementations. An implementation claiming DTEP-F conformance must satisfy all SHALL requirements in the relevant layers. Test vectors are defined in [tests/vectors/test_vectors.json](../tests/vectors/test_vectors.json).

---

## 2. Conformance Levels

**Level 1 — Core** (Layers 3–4): Transformation and signing only. Minimum viable Corner 5 implementation.

**Level 2 — Storage** (Layers 3–5): Core + DRRDB with Taler auditor protocol.

**Level 3 — Full** (Layers 3–6): Storage + analytical primitives and fraud detection.

---

## 3. Layer 3 — Transformation Conformance

### Mandatory Requirements

- SHALL accept EN 16931 UBL 2.1 XML as input
- SHALL perform JCS canonicalisation (RFC 8785) before hashing
- SHALL replace all designated forgettable fields with SHA512(salt ∥ original_value)
- SHALL derive salt via HKDF-SHA512 (RFC 5869) from M0 coin commitment
- SHALL produce exactly two output artifacts: Artifact A (encrypted) and Artifact B (public DTEP JSON)
- SHALL extract M1 as ISO 8601 hourly bucket (YYYY-MM-DDThh:00:00Z)
- SHALL extract M2 as eight-digit CPV code
- SHALL extract M3 as NACE Rev. 2 code for seller
- SHALL extract M4 as NACE Rev. 2 code for buyer
- SHALL extract M5 as tax-exclusive amount in EUR (EN 16931 BT-109)
- SHALL decompose multi-CPV invoices into separate hyperedges with proportional M5

### Test Profile

| Test | Input | Expected output |
|---|---|---|
| T3-01 | Valid EN 16931 XML with all mandatory fields | Valid Artifact A and Artifact B |
| T3-02 | EN 16931 XML with BT-27 seller name | BT-27 replaced by SHA512 hash in Artifact B |
| T3-03 | EN 16931 XML with timestamp 2026-08-15T14:37:00Z | M1 = 2026-08-15T14:00:00Z |
| T3-04 | EN 16931 XML missing BT-109 | Error: missing mandatory field |
| T3-05 | EN 16931 XML with two CPV codes | Two hyperedges with proportional M5 |
| T3-06 | Same invoice submitted twice | Identical M1–M5, different M0 (non-deterministic) |

---

## 4. Layer 4 — Signing Conformance

### Mandatory Requirements

- SHALL use Ed25519 (RFC 8032) for all signatures
- SHALL sign the JCS-canonicalised public DTEP JSON (RFC 8785)
- SHALL include verification method reference to Exchange signing key
- SHALL verify signing key certificate against Exchange master key before signing
- SHALL record signing key identifier in Artifact A for long-term verification

### Test Profile

| Test | Input | Expected output |
|---|---|---|
| T4-01 | Valid public DTEP JSON | Valid Ed25519 signature verifiable against Exchange public key |
| T4-02 | Tampered public DTEP JSON | Signature verification failure |
| T4-03 | Expired signing key | Signing rejected; key rotation required |
| T4-04 | Offline batch of 100 invoices | All signed with key valid at signing time |

---

## 5. Layer 5 — DRRDB Conformance

### Mandatory Requirements

- SHALL enforce append-only semantics — no modification or deletion of signed records
- SHALL maintain deduplication index on M0 coin commitments
- SHALL reject duplicate M0 submissions with error code DUPLICATE_M0
- SHALL verify Ed25519 signature on every incoming DRR record before storage
- SHALL implement Taler auditor protocol invariant: every public record has a corresponding Artifact A
- SHALL expose public query API supporting filters on M1, M2, M3, M4, M5

### Test Profile

| Test | Input | Expected output |
|---|---|---|
| T5-01 | Valid signed DRR record | Record stored; query returns record |
| T5-02 | Duplicate M0 submission | Error: DUPLICATE_M0 |
| T5-03 | DRR record with invalid signature | Record rejected; incident logged |
| T5-04 | Auditor protocol check | All public records have Artifact A; no orphan records |
| T5-05 | Query by M2 CPV code | Returns all records matching CPV |
| T5-06 | Query by M1 time window | Returns all records in hourly range |

---

## 6. Layer 6 — Analytical Primitives Conformance

### Mandatory Requirements

- SHALL compute δ(e) for every new hyperedge using the configured R(c,t) oracle
- SHALL maintain L(t) Leontief matrix with incremental update on every new hyperedge
- SHALL execute τ(H) acyclicity verification on every new hyperedge
- SHALL generate Audit Request on S_structural signal immediately and unconditionally
- SHALL generate Audit Request on S_price ∧ S_macro combined signal
- SHALL NOT generate Audit Request on isolated S_price or S_macro signal

### Test Profile

| Test | Input | Expected output |
|---|---|---|
| T6-01 | Hyperedge with amount 10× R(c,t) | S_price anomaly signal; log entry |
| T6-02 | Hyperedge with amount 10× R(c,t) + L(t) deviation | S_price ∧ S_macro; Audit Request |
| T6-03 | Cyclic hyperedge sequence A→B→C→A | τ(H) = cyclic; immediate Audit Request |
| T6-04 | Normal transaction sequence | No anomaly signals |
| T6-05 | L(t) incremental update | Coefficient a_{ns,nb}(t) updated without full recomputation |
| T6-06 | τ(H) on self-loop (t_issuance = t_tax_event) | τ(H) = acyclic; no signal |

---

## 7. Interoperability Matrix

The following combinations are targeted for interoperability testing in the national sandbox (Period 3):

| Peppol Access Point | DRRDB Implementation | Status |
|---|---|---|
| e-Invoice.bg (НАП) | DTEP-F reference implementation | Target — Period 3 |
| OpenPeppol test AP | DTEP-F reference implementation | Target — Period 2 |

---

## 8. Open Issues

- [ ] Formal test suite automation framework (v0.2)
- [ ] Interoperability testing with OpenPeppol conformance test bed (v0.3)
- [ ] Third-party certification process for Level 3 conformance (v0.9)
