# Changelog

All notable changes to DTEP-S will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Planned for v0.2
- TEE attestation format per platform (Android StrongBox, iOS Secure Enclave)
- Compact QR representation — detailed byte budget for physical card encoding
- Auditor endpoint API specification
- PIN binding object — formal schema for QR+PIN path
- Formal JSON Schema machine validation for all three schema files
- Context document publication at dtep-s.solidaritylab.org/context/v1

---

## [0.1-draft] — 2026-06-01

### Added
- Protocol overview specification — formal model of the four-element chain: Right → Identification → Act of Delivery → Payment
- Credential schema specification — base schema with extension points, domain-neutral
- Presentation flows specification — three Holder paths: biometric (HIGH), QR+PIN (MEDIUM), documentary (LOW) with full fallback sequences and enrollment flow
- Redemption Event specification — atomic TEE-signed delivery evidence artifact with 21 validation rules and 7 anomaly indicators
- Audit trail specification — append-only Merkle tree with chained leaves, periodic trail roots, and four anchoring options
- JSON Schema: entitlement-credential.json
- JSON Schema: redemption-event.json
- JSON Schema: audit-record.json (DTEPTrailRoot, DTEPMerkleProof, DTEPAuditReport)

### Context

DTEP-S v0.1-draft crystallised at the intersection of three concurrent processes in May–June 2026:

**NGI Zero Commons Fund 13th call** (deadline June 1, 2026) provided the immediate funding opportunity and the open protocol framing.

**DTEP-F submission to TC84 at the Bulgarian Institute for Standardisation** — the parallel fiscal layer of the DTEP protocol family, submitted to the BIS technical committee on electronic transactions. DTEP-S and DTEP-F share the same evidence protocol core and are designed as complementary layers of a common architecture.

**Finalisation of provider objection recalculations for Bulgaria's Humanitarian Accommodation Programme 1** (period 25.02.2022–31.05.2022) — direct operational context. The recalculation work, performed in the capacity of external technical expert to Bulgaria's Ministry of Tourism, produced the eleven-defect diagnostic of the administrative chain that forms the evidential basis for DTEP-S. The structural gap between Act of Delivery and Payment — undocumentable by any existing mechanism — is not hypothetical. It is measured in tens of thousands of disputed accommodation nights across hundreds of providers.

Ongoing: Recalculation of recovery amounts under
Council of Ministers Decision 422/2.6.2023
(List No. 17, period 01.06.2022–31.03.2023)
covering 100 accommodation providers.
The structural discrepancies being recalculated
are direct instances of Defects 7 and 10
documented in CSDT's methodology report —
the same defects DTEP-S is designed to prevent.

The protocol is the answer to the architectural root of those disputes. The timing is not coincidental.

---

## Prior work

DTEP-S builds on institutional and technical groundwork accumulated since 2022:

- 2022–2025: External technical expert role at Bulgaria's Ministry of Tourism across three humanitarian accommodation programmes under Council Directive 2001/55/EC, including coordination of European Court of Auditors mission
- 2025: CSDT constituted as a public benefit association and member of the Bulgarian Institute for Standardisation
- 2025–2026: DTEP-F protocol concept developed and submitted to BIS TC84
- 2026: Methodology report documenting eleven systemic defects in the humanitarian programme administrative chain, prepared for the Ministry of Tourism working group

[Unreleased]: https://github.com/SolidarityLab-CSDT/dtep-s/compare/v0.1-draft...HEAD
[0.1-draft]: https://github.com/SolidarityLab-CSDT/dtep-s/releases/tag/v0.1-draft
