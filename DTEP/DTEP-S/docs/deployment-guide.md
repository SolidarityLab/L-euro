# DTEP-S Deployment Guide

**Version:** 0.1-draft  
**Status:** Specification in progress  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This guide describes the deployment architecture for DTEP-S in the four supported scenarios. It is intended for technical teams planning an implementation and for institutional stakeholders evaluating deployment options.

For the full protocol specification see `spec/protocol-overview.md`. For the threat model see `docs/threat-model.md`. For GDPR compliance requirements see `docs/gdpr-analysis.md`.

This is a specification-phase guide. Reference implementation components are under development and will be documented in detail in v0.2.

---

## 2. Component Overview

A DTEP-S deployment consists of up to four components corresponding to the four protocol participants:

```
┌─────────────────┐     ┌─────────────────┐
│  ISSUER         │     │  AUDITOR        │
│  COMPONENT      │     │  COMPONENT      │
│                 │     │                 │
│ - Credential    │     │ - Event log     │
│   issuance      │     │ - Trail root    │
│ - Subject ID    │     │   publication   │
│   registry      │     │ - Audit reports │
│ - Key management│     │ - Settlement    │
└────────┬────────┘     └────────┬────────┘
         │ credential             │ trail roots
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  HOLDER         │     │  VERIFIER       │
│  (no component) │     │  COMPONENT      │
│                 │     │                 │
│  Credential     │     │ - Android/iOS   │
│  stored in:     │     │   application   │
│  - Wallet       │     │ - TEE signing   │
│  - QR card      │     │ - Local event   │
│  - Registry     │     │   queue         │
└─────────────────┘     └─────────────────┘
```

The Holder does not run a component. The credential is external to the Holder's device.

---

## 3. Deployment Scenarios

DTEP-S supports four deployment scenarios with increasing institutional coverage. Each scenario is independently viable. No scenario requires all participants to be present simultaneously.

### Scenario 1 — Full chain

All four participants (Issuer, Verifier, Evidence layer, Auditor) implement DTEP-S. Redemption Events flow in real time from Verifier to Auditor. Settlement is automated.

**Minimum requirements:**
- Issuer: W3C VC 2.0 credential issuance system; DID key pair; enrollment API; server with key management and subject ID registry
- Verifier: DTEP-S merchant application; Android 9+ or iOS 14+ device with StrongBox/Secure Enclave; connectivity; fingerprint scanner (if biometric path)
- Auditor: DTEP-S audit endpoint; deduplication index; settlement system; trail root publication endpoint; public registry

**Connectivity:** Verifier requires periodic connectivity (minimum once per cache TTL for Path C). Path A and Path B operate fully offline.

Target state for national sandbox deployment.

### Scenario 2 — Issuer + Verifier, no central Auditor

Verifier stores Redemption Events locally. Evidence exported as signed batch on demand. Auditor processes batch offline.

**Minimum requirements:**
- Issuer: credential issuance as Scenario 1
- Verifier: DTEP-S merchant application; extended local event storage; batch export capability
- Auditor: batch import capability; no real-time endpoint required

Practical entry point for programmes without existing Auditor infrastructure. Suitable for pilot programmes.

### Scenario 3 — Verifier only, legacy Issuer

Verifier accepts credentials from a legacy system via a DTEP-S import adapter. Redemption Events generated normally. Upgrades automatically when Issuer adopts DTEP-S.

**Minimum requirements:**
- Legacy Issuer: any existing credential or registry — accessed via adapter
- Verifier: DTEP-S merchant application; import adapter for legacy credential format
- Auditor: optional at this stage

Lowest barrier to entry. A single accredited provider can deploy without waiting for institutional adoption.

### Scenario 4 — Auditor only, batch import

Existing paper or digital records imported as DTEP-S audit records. Partial evidence chain established. Full chain activated incrementally as Issuers and Verifiers adopt DTEP-S.

**Minimum requirements:**
- Auditor: DTEP-S batch import tool; existing records in any structured format
- No Issuer or Verifier adoption required at this stage

Entry point for audit bodies beginning evidence trail reconstruction from existing programme records.

---

## 4. Upgrade Path

Deployment scenarios connect into an automatic upgrade path. No retroactive data migration is required when new participants are added.

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

Evidence records generated at each stage remain valid at all subsequent stages. The cryptographic signatures are permanent — no re-signing or re-issuance is required as the deployment expands.

---

## 5. Verifier Application Requirements

The Verifier application is the component with the most constrained deployment environment.

### 5.1 Minimum hardware

- Android device with API level 28+ (Android 9) or iOS 14+
- **HIGH assurance (biometric path):** Android StrongBox Keymaster (available on most mid-range and flagship devices from 2019 onward) or Apple Secure Enclave (iOS)
- Fingerprint scanner: integrated (preferred) or external USB/Bluetooth
- Camera: for QR card scanning (Path B and Path C)
- Network: any — offline operation is fully supported
- 2 GB RAM, 32 GB storage

### 5.2 Fallback for devices without StrongBox

Devices without StrongBox may operate in MEDIUM assurance mode (QR+PIN path) or LOW assurance mode (documentary path). The assurance level is declared in every Redemption Event. Auditors may apply differential scrutiny or settlement conditions based on assurance level.

### 5.3 Connectivity model

DTEP-S supports fully offline Verifier operation. Redemption Events are generated and signed locally, queued in local storage, and transmitted to the Auditor endpoint when connectivity is restored. Cryptographic integrity is maintained throughout. The offline queue is bounded by local storage; in practice, daily batch transmission is sufficient for most deployment contexts.

The default offline queue window is 30 days and should be reviewed per deployment. Shorter windows reduce staleness risk; longer windows accommodate extended connectivity outages.

### 5.4 Fingerprint scanner compatibility

- USB HID fingerprint scanners with Android SDK support
- Bluetooth fingerprint scanners with FIDO2 authenticator profile
- Entry-level scanners suitable for deployment are available in the €50–100 range
- Scanner selection affects False Rejection Rate — higher quality scanners reduce failed match rates particularly for elderly or physical-labour populations
- Specific compatible models will be listed in v0.2 based on reference implementation testing

---

## 6. Issuer Requirements

### 6.1 Credential issuance

The Issuer must be able to issue W3C VC 2.0 credentials signed with an institutional Ed25519 key pair. The credential schema is defined in `spec/credential-schema.md`.

**Minimum issuance capability:**
- Generate credential subject DID or pseudonymous identifier per beneficiary
- Sign credential with Issuer key
- Deliver credential to Holder in at least one of: digital wallet, QR card, central registry entry

### 6.2 QR card production

For device-independent Holder access (Path B), the Issuer produces physical QR cards containing the compressed W3C VC.

**Minimum card specification:**
- QR code: version 10 or higher; error correction level H
- Card material: PVC or equivalent durable material
- PIN: 4-digit, registered at enrollment, not printed on card
- Validity indicator: expiry date printed in human-readable form

### 6.3 Central registry (Path C)

For documentary lookup (Path C), the Issuer exposes a query API accepting a beneficiary identifier (document number or registry reference) and returning entitlement status. API specification in `spec/protocol-overview.md` Section 5.3.

---

## 7. Auditor Requirements

### 7.1 Audit endpoint

For real-time operation (Scenario 1), the Auditor exposes a DTEP-S audit endpoint accepting signed Redemption Events.

**Minimum requirements:**
- TLS 1.3 endpoint
- Signature verification of incoming Redemption Events
- UUID deduplication index
- Storage of verified events with immutable audit trail
- Trail root publication endpoint and public registry

### 7.2 Batch import

For offline operation (Scenarios 2 and 4), the Auditor implements a batch import tool accepting signed Redemption Event packages exported by Verifiers. Batch format specification in `spec/audit-trail.md`.

### 7.3 Settlement integration

Settlement processing — mapping verified Redemption Events to payment authorisations for Verifiers — is outside DTEP-S protocol scope. DTEP-S provides the verified evidence record. The Auditor's settlement system consumes that record according to programme-specific payment rules.

---

## 8. Key Management

### 8.1 Issuer signing key

The Issuer holds an Ed25519 key pair used to sign all credentials.

**Requirements:**
- Private key stored in Hardware Security Module (HSM) or equivalent
- Key rotation procedure must be defined before deployment
- Public key published via DID document accessible to Verifiers
- Key compromise response procedure must be defined (credential revocation and reissuance)

### 8.2 Verifier device key

Each Verifier device holds an Ed25519 key pair in TEE.

**Requirements:**
- Key generated within TEE at device enrollment — never exported
- Device enrollment procedure registers device DID with Auditor
- Device decommissioning procedure revokes device DID
- Lost or stolen device: device DID revoked, events from that device flagged for review

### 8.3 Auditor signing key

The Auditor holds an Ed25519 key pair used to sign trail root documents and audit reports.

**Requirements:**
- Private key stored in HSM
- Public key published via DID document
- Trail root signing may be automated with HSM-integrated signing service

---

## 9. Biometric Enrollment Infrastructure

Biometric enrollment requires dedicated enrollment points — separate from delivery points.

**Enrollment point requirements:**
- DTEP-S enrollment application (separate from Verifier application)
- Fingerprint scanner (same compatibility requirements as Verifier)
- Connectivity to Issuer credential issuance service
- Trained operator

**Enrollment flow:**
1. Operator verifies Holder identity (documentary)
2. Operator initiates enrollment in application
3. Application captures 3× fingerprint scans
4. Pipeline executes within TEE: Tensor RPCA → Fourier-Mellin → Neural extractor → one-way transform → template
5. Template transmitted to Issuer credential issuance service (or stored locally per `templateLocation` configuration)
6. Issuer updates or issues credential with `biometricBinding`
7. Updated credential delivered to Holder (QR card reprint, wallet update, registry update)

**Operator training requirements:**
- Fingerprint capture technique for diverse populations
- Handling of failed captures (elderly, physical labour, injury)
- Data subject rights procedures
- Incident reporting

---

## 10. Integration with Existing Systems

### 10.1 Bulgarian Humanitarian Programme — Reference Deployment

The reference deployment context for DTEP-S v0.1 is Bulgaria's humanitarian accommodation programme for persons under temporary protection under Council Directive 2001/55/EC.

| Role | Institution | System |
|---|---|---|
| Issuer | Agency for Social Assistance (АСП) | Beneficiary case file system |
| Verifier | Ministry of Tourism-accredited providers | DTEP-S merchant application |
| Auditor | Ministry of Tourism / Ministry of Finance | Programme settlement system |
| Governance | Council of Ministers | Programme decisions |

**Entry point for sandbox:** Scenario 2 or 3 — individual accredited providers can deploy without waiting for АСП credential issuance infrastructure. Verifiers operate with legacy registry lookup (Path C) generating LOW assurance Redemption Events. Evidence trail established from day one of deployment.

**Upgrade trigger:** АСП issues QR cards to beneficiaries → Path B available → MEDIUM assurance → automated settlement becomes viable.

### 10.2 Integration with Agency for Social Assistance (АСП)

- Issuer component queries АСП registry via defined API to verify entitlement before credential issuance
- АСП registry is the authoritative source — DTEP-S does not replicate it
- Subject ID assignment by Issuer component, stored in АСП registry against beneficiary record
- АСП does not participate in the Verifier or Auditor chain

### 10.3 Integration with Ministry of Tourism accreditation

- Verifier onboarding uses МТ accreditation ID as `verifier.accreditationId`
- МТ accreditation scheme identifier configured in credentials as `allowedVerifiers.accreditationScheme`
- Auditor settlement reports map to МТ reimbursement procedures

### 10.4 Generic legacy system integration

For deployments alongside legacy systems:

- Import adapter maps legacy entitlement records to DTEP-S credential schema
- Export adapter maps DTEP-S audit reports to legacy settlement workflows
- Parallel operation period recommended before legacy system decommission

---

## 11. Security Checklist for Deployment

Before operational deployment, the deploying organisation should verify:

- [ ] Issuer key pair generated on HSM; rotation policy defined
- [ ] Verifier device inventory — StrongBox capability documented per device
- [ ] Biometric enrollment consent procedure documented and DPIA completed
- [ ] Offline queue size limit set and monitored
- [ ] Auditor deduplication index initialised
- [ ] TLS certificates valid and auto-renewal configured
- [ ] Incident response procedure for Verifier device loss defined
- [ ] KZLD consultation completed (Bulgarian deployment) or equivalent national supervisory authority notified

---

## 12. Open Issues

- [ ] Reference implementation component documentation (v0.2)
- [ ] Compatible device and scanner list (v0.2)
- [ ] Verifier device key provisioning procedure (v0.2)
- [ ] QR card byte budget specification (v0.2)
- [ ] HSM integration guide for Issuer and Auditor key management (v0.2)
- [ ] DID method selection and publication guide (v0.2)
- [ ] Central registry API OpenAPI specification (v0.3)
- [ ] Batch export format specification (v0.3)
- [ ] АСП and МТ integration API specification — Bulgaria context (v0.3)
- [ ] iOS deployment considerations (v0.3)
- [ ] Multi-deployment coordination for cross-border scenarios (v0.4)

---

## References

- DTEP-S Protocol Overview: `../spec/protocol-overview.md`
- DTEP-S Presentation Flows: `../spec/presentation-flows.md`
- DTEP-S Threat Model: `./threat-model.md`
- DTEP-S GDPR Analysis: `./gdpr-analysis.md`
- Android StrongBox: https://source.android.com/docs/security/features/keystore
- Apple Secure Enclave: https://support.apple.com/guide/security/secure-enclave-sec59b0b31ff/web
- Council Directive 2001/55/EC: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:32001L0055
