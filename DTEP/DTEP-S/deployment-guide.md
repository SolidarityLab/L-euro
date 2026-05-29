# DTEP-S Deployment Guide

**Version:** 0.1-draft  
**Status:** Specification in progress  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document provides guidance for institutions and organisations deploying
DTEP-S in operational or sandbox contexts. It covers participant roles,
minimum requirements per deployment scenario, and the incremental adoption path.

For the full protocol specification see `spec/protocol-overview.md`.
For the threat model see `docs/threat-model.md`.
For GDPR compliance requirements see `docs/gdpr-analysis.md`.

---

## 2. Deployment Scenarios

DTEP-S supports four deployment scenarios with increasing institutional
coverage. Each scenario is independently viable. No scenario requires all
participants to be present simultaneously.

### Scenario 1 — Full chain

All four participants (Issuer, Verifier, Evidence layer, Auditor) implement
DTEP-S. Redemption Events flow in real time from Verifier to Auditor.
Settlement is automated.

**Minimum requirements:**
- Issuer: W3C VC 2.0 credential issuance system; DID key pair; enrollment API
- Verifier: DTEP-S merchant application; TEE-capable device; connectivity
- Auditor: DTEP-S audit endpoint; deduplication index; settlement system

**Target state** for national sandbox deployment.

---

### Scenario 2 — Issuer + Verifier, no central Auditor

Verifier stores Redemption Events locally. Evidence exported as signed batch
on demand. Auditor processes batch offline.

**Minimum requirements:**
- Issuer: credential issuance (as Scenario 1)
- Verifier: DTEP-S merchant application; local event storage; batch export
- Auditor: batch import capability; no real-time endpoint required

**Practical entry point** for programmes without existing Auditor infrastructure.

---

### Scenario 3 — Verifier only, legacy Issuer

Verifier accepts credentials from a legacy system via a DTEP-S import adapter.
Redemption Events generated normally. Upgrades automatically when Issuer
adopts DTEP-S.

**Minimum requirements:**
- Legacy Issuer: any existing credential or registry — accessed via adapter
- Verifier: DTEP-S merchant application; import adapter for legacy credential format
- Auditor: optional at this stage

**Lowest barrier to entry.** A single accredited provider can deploy without
waiting for institutional adoption.

---

### Scenario 4 — Auditor + batch import, retroactive evidence

Existing paper or digital records imported as DTEP-S audit records. Partial
evidence chain established. Full chain activated incrementally as Issuers and
Verifiers adopt DTEP-S.

**Minimum requirements:**
- Auditor: DTEP-S batch import tool; existing records in any structured format
- No Issuer or Verifier adoption required at this stage

**Entry point for audit bodies** beginning evidence trail reconstruction from
existing programme records.

---

## 3. Upgrade Path

Deployment scenarios connect into an automatic upgrade path. No retroactive
data migration is required when new participants are added.

```
Single provider (Scenario 3)
        │
        │ add Auditor endpoint
        ▼
Multiple providers, shared Auditor (Scenario 2)
        │
        │ add Issuer W3C VC issuance
        ▼
Full national sandbox (Scenario 1)
        │
        │ replicate specification and adapter
        ▼
Cross-border deployment
```

Evidence records generated at each stage remain valid at all subsequent stages.
The cryptographic signatures are permanent — no re-signing or re-issuance is
required as the deployment expands.

---

## 4. Verifier Device Requirements

### 4.1 Minimum hardware

- Android device with API level 28+ (Android 9)
- For HIGH assurance (biometric path): Android StrongBox Keymaster (available
  on most mid-range and flagship devices from 2019 onward)
- Fingerprint scanner: integrated (preferred) or external USB/Bluetooth
- Camera: for QR card scanning (Path B)
- Network: any — offline operation is fully supported

### 4.2 Fallback for devices without StrongBox

Devices without StrongBox may operate in MEDIUM assurance mode (QR+PIN path)
or LOW assurance mode (documentary path). The assurance level is declared in
every Redemption Event. Auditors may apply differential scrutiny or settlement
conditions based on assurance level.

### 4.3 Connectivity model

DTEP-S supports fully offline Verifier operation. Redemption Events are
generated and signed locally, queued in local storage, and transmitted to the
Auditor endpoint when connectivity is restored. Cryptographic integrity is
maintained throughout. The offline queue is bounded by local storage; in
practice, daily batch transmission is sufficient for most deployment contexts.

---

## 5. Issuer Requirements

### 5.1 Credential issuance

The Issuer must be able to issue W3C VC 2.0 credentials signed with an
institutional Ed25519 key pair. The credential schema is defined in
`spec/credential-schema.md` and `schema/entitlement-credential.json`.

Minimum issuance capability:
- Generate credential subject DID or pseudonymous identifier per beneficiary
- Sign credential with Issuer key
- Deliver credential to Holder in at least one of: digital wallet, QR card,
  central registry entry

### 5.2 QR card production

For device-independent Holder access (Path B), the Issuer produces physical
QR cards containing the compressed W3C VC. Minimum card specification:

- QR code: version 10 or higher; error correction level H
- Card material: PVC or equivalent durable material
- PIN: 4-digit, registered at enrollment, not printed on card
- Validity indicator: expiry date printed in human-readable form

### 5.3 Central registry (Path C)

For documentary lookup (Path C), the Issuer exposes a query API accepting
a beneficiary identifier (document number or registry reference) and returning
entitlement status. API specification in `spec/protocol-overview.md` Section 5.3.

---

## 6. Auditor Requirements

### 6.1 Audit endpoint

For real-time operation (Scenario 1), the Auditor exposes a DTEP-S audit
endpoint accepting signed Redemption Events. Minimum requirements:

- TLS 1.3 endpoint
- Signature verification of incoming Redemption Events
- UUID deduplication index
- Storage of verified events with immutable audit trail

### 6.2 Batch import

For offline operation (Scenarios 2 and 4), the Auditor implements a batch
import tool accepting signed Redemption Event packages exported by Verifiers.
Batch format specification in `spec/audit-trail.md`.

### 6.3 Settlement integration

Settlement processing — mapping verified Redemption Events to payment
authorisations for Verifiers — is outside DTEP-S protocol scope. DTEP-S
provides the verified evidence record. The Auditor's settlement system
consumes that record according to programme-specific payment rules.

---

## 7. Bulgarian Humanitarian Programme — Reference Deployment

The reference deployment context for DTEP-S v0.1 is Bulgaria's humanitarian
accommodation programme for persons under temporary protection under
Council Directive 2001/55/EC.

| Role | Institution | System |
|---|---|---|
| Issuer | Agency for Social Assistance (АСП) | Beneficiary case file system |
| Verifier | Ministry of Tourism-accredited providers | DTEP-S merchant application |
| Auditor | Ministry of Tourism / Ministry of Finance | Programme settlement system |
| Governance | Council of Ministers | Programme decisions |

**Entry point for sandbox:** Scenario 2 or 3 — individual accredited providers
can deploy without waiting for АСП credential issuance infrastructure.
Verifiers operate with legacy registry lookup (Path C) generating LOW assurance
Redemption Events. Evidence trail established from day one of deployment.

**Upgrade trigger:** АСП issues QR cards to beneficiaries → Path B available →
MEDIUM assurance → automated settlement becomes viable.

---

## 8. Security Checklist for Deployment

Before operational deployment, the deploying organisation should verify:

- [ ] Issuer key pair generated on HSM; rotation policy defined
- [ ] Verifier device inventory — StrongBox capability documented per device
- [ ] Biometric enrollment consent procedure documented and DPIA completed
- [ ] Offline queue size limit set and monitored
- [ ] Auditor deduplication index initialised
- [ ] TLS certificates valid and auto-renewal configured
- [ ] Incident response procedure for Verifier device loss defined
- [ ] KZLD consultation completed (Bulgarian deployment) or equivalent
      national supervisory authority notified

---

## 9. Open Issues

- [ ] Verifier device key provisioning procedure (v0.2)
- [ ] QR card byte budget specification (v0.2)
- [ ] Central registry API OpenAPI specification (v0.3)
- [ ] Batch export format specification (v0.3)
- [ ] iOS deployment considerations (v0.3)
