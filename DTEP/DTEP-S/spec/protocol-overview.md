# DTEP-S Protocol Overview

**Version:** 0.1-draft  
**Status:** Specification in progress  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document defines the DTEP-S (Digital Transaction Evidence Protocol — Social Layer) protocol. DTEP-S specifies the data model, participant roles, interaction flows, and evidence requirements for cryptographically verifiable delivery of institutional entitlements to beneficiaries who may not possess any digital device.

DTEP-S is the Social Layer of the DTEP protocol family. The Fiscal Layer (DTEP-F) addresses e-invoicing and VAT monitoring and is specified separately.

---

## 2. Definitions

**Entitlement** — a right issued by an authorised institution to a specific beneficiary, granting access to defined goods or services from accredited providers within defined conditions (time, quantity, provider category).

**Credential** — a W3C Verifiable Credential 2.0 encoding an entitlement, cryptographically signed by the Issuer.

**Redemption Event** — a machine-verifiable record that a specific entitlement was exercised at a specific delivery point at a specific time, signed by the Verifier device.

**Evidence Chain** — the ordered sequence: Credential issuance → Holder verification → Redemption Event → Audit Record.

**Assurance Level** — the confidence level of Holder verification, declared in every Redemption Event. Values: HIGH (biometric TEE), MEDIUM (QR + PIN), LOW (documentary lookup).

---

## 3. Protocol Participants

### 3.1 Issuer

An authorised institution that issues entitlement credentials to beneficiaries. The Issuer:

- Maintains the authoritative registry of entitlement rights
- Issues W3C VC 2.0 credentials signed with its institutional key
- Defines the credential schema, validity period, and redemption conditions
- Receives settlement evidence from the Auditor

In the Bulgarian humanitarian programme context: Agency for Social Assistance (АСП).

### 3.2 Holder

The beneficiary of the entitlement. The Holder:

- Receives the credential in one of three forms:
  - Digital wallet (EUDIW or compatible) — where device is available
  - Physical QR card — printed credential for device-independent use
  - Central registry entry — lookup by identifier, no physical token required
- Presents the credential at a delivery point
- Is NOT required to possess a device

### 3.3 Verifier

An accredited provider of goods or services. The Verifier:

- Operates a DTEP-S compliant merchant application on a mobile device
- Verifies the Holder's credential and identity
- Generates and signs Redemption Events
- Transmits evidence to the Auditor (online) or stores locally (offline)

In the Bulgarian humanitarian programme context: Ministry of Tourism-accredited accommodation and food providers.

### 3.4 Auditor

The institutional oversight authority. The Auditor:

- Receives Redemption Events from Verifiers
- Validates evidence chain integrity
- Processes settlement payments to Verifiers
- Reports to fiscal authorities

In the Bulgarian humanitarian programme context: Ministry of Tourism / Ministry of Finance.

### 3.5 Excluded Participants

DTEP-S is designed with minimal institutional footprint. The following entities are structurally NOT required in the operational chain:

- State Agency for Refugees (ДАБ) — not in the entitlement chain; exclusion avoids mandate overlap and perception barriers
- National Revenue Agency (НАП) — fiscal crossmatch not required for humanitarian entitlement verification
- Ministry of Interior (МВР) — not in the humanitarian delivery chain; exclusion avoids GDPR crossmatch risks

---

## 4. Protocol Chain

```
┌─────────────────────────────────────────────────┐
│                    ISSUER                        │
│  1. Assesses entitlement right                  │
│  2. Issues W3C VC 2.0 credential                │
│  3. Delivers credential to Holder               │
│     (wallet / QR card / registry)               │
└───────────────────┬─────────────────────────────┘
                    │ credential
                    ▼
┌─────────────────────────────────────────────────┐
│                    HOLDER                        │
│  Presents credential at delivery point          │
│  (no device required)                           │
└───────────────────┬─────────────────────────────┘
                    │ presentation
                    ▼
┌─────────────────────────────────────────────────┐
│                   VERIFIER                       │
│  4. Reads credential                            │
│  5. Verifies Issuer signature                   │
│  6. Verifies Holder identity                    │
│     (biometric / QR+PIN / documentary)          │
│  7. TEE generates Redemption Event              │
│  8. Verifier device signs Redemption Event      │
└───────────────────┬─────────────────────────────┘
                    │ redemption event
                    ▼
┌─────────────────────────────────────────────────┐
│               EVIDENCE LAYER                     │
│  Cryptographically signed delivery proof        │
│  Immutable audit log                            │
└───────────────────┬─────────────────────────────┘
                    │ audit record
                    ▼
┌─────────────────────────────────────────────────┐
│                   AUDITOR                        │
│  9. Validates evidence chain                    │
│  10. Processes settlement to Verifier           │
└─────────────────────────────────────────────────┘
```

---

## 5. Holder Presentation Paths

DTEP-S defines three Holder presentation paths with decreasing assurance levels. All paths produce a Redemption Event with a declared assurance level.

### 5.1 Path A — Biometric (Assurance Level: HIGH)

Prerequisites: Holder enrolled at an DTEP-S enrollment point. Enrolled template stored as one-way transformed vector in credential or local Verifier registry.

Flow:
1. Holder presents any form of credential reference (wallet / QR / verbal identifier)
2. Verifier merchant application requests fingerprint scan
3. Pipeline: 3× scan → Tensor RPCA → Fourier-Mellin → Neural extractor → feature vector
4. TEE: cosine similarity against enrolled vector
5. If similarity > threshold: TEE releases signing key → Redemption Event generated and signed
6. If similarity ≤ threshold: signing key not released → event not generated

### 5.2 Path B — QR Card + PIN (Assurance Level: MEDIUM)

Prerequisites: Issuer has produced a physical QR card containing the compressed W3C VC. Holder knows a 4-digit PIN registered at enrollment.

Flow:
1. Verifier scans QR code on physical card
2. Verifier application decodes and verifies credential (Issuer signature)
3. Verifier application prompts for PIN
4. If PIN matches: Redemption Event generated and signed by merchant device
5. If PIN fails (3 attempts): event not generated, incident logged

### 5.3 Path C — Central Lookup (Assurance Level: LOW)

Prerequisites: Issuer maintains a central registry accessible via API. Holder presents identity document.

Flow:
1. Verifier reads identifier from identity document (manual or OCR)
2. Verifier application queries central registry API
3. If entitlement found and valid: credential data returned
4. Verifier visually confirms Holder identity against document photo
5. Redemption Event generated and signed by merchant device
6. Visual confirmation recorded as attestation in event

---

## 6. Redemption Event Structure

A Redemption Event is a JSON-LD document signed by the Verifier device key.

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://dtep-s.solidaritylab.org/context/v1"
  ],
  "type": ["VerifiablePresentation", "DTEPRedemptionEvent"],
  "id": "urn:uuid:{event-uuid}",
  "holder": "{credential-subject-id}",
  "verifier": {
    "id": "{verifier-did}",
    "accreditationId": "{ministry-accreditation-id}"
  },
  "credential": {
    "id": "{credential-id}",
    "issuer": "{issuer-did}"
  },
  "delivery": {
    "timestamp": "{ISO-8601}",
    "location": "{optional-geolocation}",
    "goods": [
      {
        "type": "{entitlement-type}",
        "quantity": 1,
        "unit": "night|meal|package|..."
      }
    ]
  },
  "verification": {
    "path": "biometric|qr-pin|documentary",
    "assuranceLevel": "HIGH|MEDIUM|LOW",
    "teeAttestation": "{tee-proof-if-biometric}"
  },
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "eddsa-rdfc-2022",
    "created": "{ISO-8601}",
    "verificationMethod": "{verifier-device-key-did}",
    "proofValue": "{Ed25519-signature}"
  }
}
```

---

## 7. Deployment Scenarios

DTEP-S supports graceful degradation under partial institutional adoption. Each scenario is independently viable.

### Scenario 1 — Full chain (all four participants)
All participants implement DTEP-S. Evidence flows in real time from Verifier to Auditor. Settlement is automated.

### Scenario 2 — Issuer + Verifier (no central Auditor)
Verifier stores Redemption Events locally. Evidence exported as signed batch on demand. Auditor processes batch offline.

### Scenario 3 — Verifier only (legacy Issuer)
Verifier accepts credentials from legacy system via DTEP-S import adapter. Redemption Events generated normally. Upgrades automatically when Issuer adopts DTEP-S.

### Scenario 4 — Auditor + batch import
Existing paper or digital records imported as DTEP-S audit records. Partial evidence chain established. Full chain activated incrementally.

In all scenarios, evidence records are cryptographically signed and immutable once generated. No retroactive data migration is required when new participants are added.

---

## 8. Privacy and Data Protection

### 8.1 Biometric data

- Raw biometric data (fingerprint images) are never stored
- Enrolled templates are one-way transformed vectors; raw biometry cannot be reconstructed
- Templates are stored locally on the Verifier device or within the encrypted credential
- No central biometric database is created or required
- Biometric enrollment is optional; alternative Holder paths (B and C) are always available

### 8.2 GDPR legal basis

Processing of biometric data in DTEP-S relies on:

- **Article 9(2)(b) GDPR** — processing necessary for the purposes of carrying out obligations in the field of social protection law
- **Article 9(2)(d) GDPR** — processing carried out in the course of legitimate activities by a public benefit association with appropriate safeguards

Biometric enrollment must be offered as an option alongside non-biometric alternatives. Consent obtained from persons in vulnerable positions (displaced persons, social assistance recipients) must be documented as freely given and must not condition access to rights.

### 8.3 Data minimisation

Redemption Events contain the minimum data required for settlement and audit. Holder identifying information is pseudonymised by credential subject ID. Real identity is maintained only by the Issuer and is not transmitted to the Auditor.

---

## 9. Security Considerations

See [docs/threat-model.md](../docs/threat-model.md) for full threat model.

Key properties:

**Unforgeability:** Redemption Events are signed by the Verifier device key held in TEE. A valid event cannot be produced without physical access to the enrolled Holder (biometric path) or the physical card and PIN (QR path).

**Non-repudiation:** Every event carries a verifiable signature. Neither Issuer, Holder, nor Verifier can deny a recorded event.

**Replay prevention:** Each Redemption Event carries a unique UUID and timestamp. Credential schemas define maximum redemption frequency (e.g. one meal per day). Auditor validates against duplication.

**Collusion detection:** Event metadata (timestamp, location, verifier ID) enables statistical anomaly detection at Auditor level. Unusual redemption patterns are flagged for review.

**Offline operation:** All three Holder paths support fully offline Verifier operation. Events are queued locally and transmitted when connectivity is restored. Cryptographic integrity is maintained throughout.

---

## 10. Relation to Other Standards

| Standard | Relation |
|---|---|
| W3C VC Data Model 2.0 | DTEP-S credential format |
| W3C DID Core | Issuer, Verifier, and Holder identification |
| OpenID4VCI | Credential issuance where wallet is available |
| OpenID4VP | Credential presentation where wallet is available |
| ISO/IEC 18013-5 | Referenced for proximity presentation (mdoc) |
| ISO/IEC 18013-7 | Referenced for online presentation |
| EUPL-1.2 | Protocol specification and implementation licence |
| Eurodac 2024/1358 | Context: explicitly excludes temporary protection beneficiaries until ~2029 |
| eIDAS 2.0 / EUDIW | DTEP-S is device-independent complement |

---

## 11. Open Issues

The following items are under active specification and will be resolved in subsequent versions:

- [ ] Formal credential schema for entitlement types (v0.2)
- [ ] TEE attestation format specification (v0.2)
- [ ] Central registry API specification (v0.3)
- [ ] Batch export format for offline Auditor scenarios (v0.3)
- [ ] BIS standardisation contribution format (v0.9)
- [ ] Security audit scope definition (v0.9)

---

## References

- W3C Verifiable Credentials Data Model v2.0: https://www.w3.org/TR/vc-data-model-2.0/
- W3C DID Core: https://www.w3.org/TR/did-core/
- eIDAS 2.0 Architecture and Reference Framework: https://eu-digital-identity-wallet.github.io/eudi-doc-architecture-and-reference-framework/
- DC4EU Large Scale Pilot outputs: https://www.dc4eu.eu/outputs/
- Council Directive 2001/55/EC: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:32001L0055
- Eurodac Regulation 2024/1358: https://eur-lex.europa.eu/eli/reg/2024/1358/oj/eng
- GDPR Article 9: https://gdpr-info.eu/art-9-gdpr/
