# DTEP-F GDPR Analysis

**Version:** 0.1-draft
**Status:** Specification in progress
**Date:** 2026-06-01
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document analyses the GDPR compliance framework for the DTEP-F protocol. It identifies the categories of personal data processed, the applicable legal bases, data subjects' rights, and the technical measures implementing privacy by design.

The analysis covers the operational chain: Peppol Corner 4 → Corner 5 Middleware → Taler Exchange → DRRDB → Central VIES → Analytical Layer.

---

## 2. Categories of Data Processed

### 2.1 DRRDB public level (M0–M5)

**M0 — Taler coin commitment:** pseudonymous identifier. Not personal data under GDPR definition in isolation — a coin commitment is a non-deterministic cryptographic construction with no link to a subject without access to Taler Exchange.

**M1 — Time moment (hourly bucket):** not personal data. An astronomical time interval.

**M2 — CPV code:** not personal data. Commodity classification.

**M3 / M4 — NACE codes:** not personal data in isolation. Sectoral classification.

**M5 — Amount in EUR:** not personal data in isolation.

**Key finding:** the DRRDB public level structurally contains no personal data. The combination M0+M1+M2+M3+M4+M5 could theoretically identify a subject for a sufficiently rare transaction — this residual risk is addressed in Section 5.

### 2.2 DRRDB protected level (Artifact A)

Contains scrubbed subject identifiers: VAT numbers, entity names, addresses, IBANs — in encrypted form with a key derived from the DD-18 salt. Classification: personal data (pseudonymous). Controller: the tax administration as Auditor.

### 2.3 Corner 5 Middleware (data in transit)

EN 16931 XML contains personal data before DD-18 scrubbing. Processing is transient — data is not retained in Middleware after transmission to Exchange. Classification: personal data (directly identifying) in transit. Retention: zero — no storage in Middleware.

---

## 3. Legal Bases

### Article 6(1)(c) GDPR — compliance with legal obligation

Applicable for: the DRR obligation under ViDA Directive 2025/516; obligations under national VAT legislation. This is the primary legal basis for the entire protocol chain.

### Article 6(1)(e) GDPR — public interest task

Applicable for: the tax administration as Auditor; the analytical layer for fraud detection in the public interest.

### Special category data

No special category data is processed in the public layer. Artifact A may contain health or other special category data if present in the EN 16931 XML — processing is under the same legal bases (Article 6(1)(c)) with an explicit national legislative basis required.

---

## 4. Data Subject Rights

### 4.1 Right of access (Article 15)

VAT-registered entities have access to their own Artifact A records in the protected level via EUDI Wallet with appropriate credentials. The public level contains no personal data — the right of access does not apply there.

### 4.2 Right to erasure (Article 17)

The append-only audit trail is in direct tension with the right to erasure. The tension is resolved through:

**Article 17(3)(b)** — processing is necessary for the performance of a task carried out in the public interest (tax audit).

**Article 17(3)(e)** — processing is necessary for the establishment, exercise or defence of legal claims (tax proceedings).

Upon retention period expiry: cryptographically verifiable deletion of Artifact A by deactivating the salt in Exchange. The M0 element in the public layer remains — it contains no personal data.

### 4.3 Right to data portability (Article 20)

Not applicable for processing under Article 6(1)(c). Applicable only if national legislation introduces an additional basis.

### 4.4 Right to object (Article 21)

Entities cannot object to DRR processing — it is a legal obligation under ViDA. The right to object does not apply under Article 6(1)(c).

---

## 5. Privacy by Design — Technical Measures

### 5.1 Ontological isolation

The temporal ontology structurally excludes subject identifiers from the public layer. De-anonymisation is mathematically impossible — not merely unauthorised. Time nodes in M1 are not personal data under any GDPR definition.

### 5.2 DD-18 scrubbing

Subject identifiers are replaced with salted SHA512 before publication in the public layer. Original values are accessible only from Exchange on Audit Request. The salt is held exclusively by Exchange — not by Middleware, DRRDB, or the analytical layer.

### 5.3 Data minimisation

The public DTEP JSON contains only the data necessary for DRR and fraud detection: M0–M5. No additional attributes.

### 5.4 Selective audit

An Audit Request discloses Artifact A only for a specific M0 element — not for the full DRRDB. The scope of disclosure is technically bounded, not merely administratively restricted.

### 5.5 Residual risk — rare transaction

The combination M1+M2+M3+M4+M5 could theoretically identify a subject for a unique transaction (the only invoice with a specific CPV in a specific hour from a specific NACE sector). Mitigation: hourly quantisation of M1 aggregates transactions; where only one transaction exists in a bucket, the risk remains.

Additional mitigation through a minimum publication threshold (publish only if at least k transactions exist in the bucket) is an open issue for v0.2 requiring KZLD consultation.

---

## 6. Applicable Law — Bulgarian Context

For the immediate deployment context:

- **GDPR** (Regulation 2016/679) — directly applicable
- **ZZLD** (Закон за защита на личните данни) — Bulgarian implementing law
- **KZLD** (Комисия за защита на личните данни) — supervisory authority
- **ZDDS** (Закон за данък върху добавената стойност) — legal basis for DRR processing
- **ViDA Directive 2025/516** — regulatory mandate

The tax administration (NRA / НАП) is the data controller for DRRDB processing. CSDT is the data processor in its capacity as protocol developer and reference implementation operator during the sandbox phase.

Prior consultation with KZLD under Article 36 GDPR is recommended before operational deployment, given the large-scale processing of transaction data and the novel nature of the temporal ontology approach.

---

## 7. Comparison with Conventional DRR Approaches

| Property | Conventional subject-graph DRR | DTEP-F temporal ontology |
|---|---|---|
| Subject identifiers in analytics | Present (pseudonymised) | Absent by construction |
| De-anonymisation risk | Statistical — mitigated by pseudonymisation | Mathematical impossibility |
| GDPR basis for analytics | Requires explicit basis for personal data | Not required — no personal data |
| Audit disclosure scope | Typically full dataset | Per-M0 selective disclosure |
| Right to erasure conflict | Permanent tension | Resolved by ontological separation |

---

## 8. Open Issues

**Minimum publication threshold for k-anonymity**
For unique transactions in an hourly bucket, the public level may indirectly reveal subject information. A methodology for a k-anonymity publication threshold requires specification and KZLD consultation prior to operational deployment.

**Retention policy and cryptographic deletion**
National tax legislation defines varying retention periods. The procedure for cryptographically verifiable deletion of Artifact A upon retention expiry requires specification in coordination with the Taler Exchange team.

**Special category data in EN 16931 payloads**
EN 16931 allows free-text fields that may contain special category data. A scrubbing policy for free-text fields beyond the designated forgettable fields requires specification for v0.2.

**Data Protection Impact Assessment**
A full DPIA is required before operational deployment by the tax administration as controller. DTEP-F provides this analysis as input to the DPIA process. The DPIA must be conducted by the controller institution — not by CSDT.

---

## References

- GDPR Article 6: https://gdpr-info.eu/art-6-gdpr/
- GDPR Article 17: https://gdpr-info.eu/art-17-gdpr/
- ViDA Directive 2025/516: https://eur-lex.europa.eu/eli/dir/2025/516
- GNU Taler DD-18: https://docs.taler.net/design-documents/018-forgettable-json.html
- KZLD: https://www.cpdp.bg/
