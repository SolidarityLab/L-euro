# DTEP-S Presentation Flows Specification

**Version:** 0.1-draft  
**Status:** Specification in progress  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document specifies the three Holder presentation paths defined in DTEP-S. A presentation path is the complete sequence of interactions between Holder, Verifier device, and optionally a central registry — from credential reading to successful Redemption Event generation.

All three paths produce a protocol-valid Redemption Event. They differ in:

- how the credential reaches the Verifier
- how the Holder's identity is verified
- the assurance level declared in the resulting event
- the infrastructure prerequisites required

The choice of path is determined by what the Holder has available and what the Verifier supports. Where multiple paths are available, the Verifier should prefer the highest assurance level path.

---

## 2. Common Prerequisites

All three paths share the following prerequisites:

**Verifier device:** A mobile device (Android or iOS) running a DTEP-S compliant Verifier application. The device must have:

- A valid Verifier DID with key pair stored in TEE
- A valid accreditation identifier within the Issuer's accreditation scheme
- The Issuer's public key or a means to resolve it
- Local event queue storage (encrypted at rest)

**Issuer public key resolution:** The Verifier must be able to resolve the Issuer's DID to their public key at credential verification time. Resolution may be:

- Online: DID resolution via network at time of presentation
- Cached: Issuer public key cached locally with defined TTL
- Pre-loaded: Issuer public key distributed out-of-band at Verifier onboarding

Offline operation requires cached or pre-loaded key resolution.

**Event queue:** All paths write the signed Redemption Event to the local event queue. Transmission to the Auditor endpoint is asynchronous and outside the presentation flow.

---

## 3. Path A — Biometric Presentation

**Assurance level:** HIGH  
**Infrastructure prerequisite:** Biometric enrollment at a DTEP-S enrollment point  
**Holder requirement:** None — no device, no card, no document required at delivery point  
**Verifier requirement:** Fingerprint scanner (integrated or peripheral)

### 3.1 Precondition

The Holder has previously enrolled at a DTEP-S enrollment point. Enrollment produced:

- A biometric template stored as a one-way transformed vector
- A credential with `biometricBinding` object present
- Template location: either in credential (`templateLocation: "credential"`) or in Verifier local registry (`templateLocation: "verifier-local"`)

### 3.2 Flow

```
Step 1 — Holder identification
  Holder provides any reference to their credential:
  - verbal statement of subject ID or issuerRef
  - presentation of any document containing identifier
  - Verifier looks up credential by identifier

Step 2 — Credential retrieval
  Verifier application retrieves credential:
  - from local cache if previously presented
  - from central registry API if connectivity available
  - from Holder's wallet via QR or NFC if available

Step 3 — Credential validation
  Verifier application verifies:
  - credential schema compliance (R1–R13)
  - Issuer signature validity
  - credential is ACTIVE (within validFrom–validUntil)
  - allowedVerifiers satisfied (if present)
  - biometricBinding object is present
  If any check fails: abort, log failure, present
  alternative path to Holder if available

Step 4 — Template retrieval
  If templateLocation is "credential":
    extract protectedTemplate from credential
  If templateLocation is "verifier-local":
    retrieve template from local registry
    using biometricBinding.templateId
  If template not found: abort, present
  alternative path

Step 5 — Biometric capture
  Verifier application prompts Holder to place
  finger on scanner
  Capture sequence:
    scan 1 → raw image
    scan 2 → raw image
    scan 3 → raw image
  All three captures passed to pipeline

Step 6 — Pipeline execution (within TEE)
  3× raw images →
  Tensor RPCA (noise separation) →
  Fourier-Mellin transform (rotation/scale normalisation) →
  Neural feature extractor →
  verification vector V

Step 7 — Similarity computation (within TEE)
  cosine_similarity(V, enrolled_template)
  If similarity ≥ threshold:
    proceed to Step 8
  If similarity < threshold:
    log failed attempt
    if attempts < 3: return to Step 5
    if attempts = 3: abort
      present alternative path if available
      log max attempts reached

Step 8 — Redemption Event construction (within TEE)
  TEE constructs event with:
    id: fresh urn:uuid-v4
    generatedAt: TEE clock timestamp
    holder: credential.credentialSubject.id
    verification.path: "biometric"
    verification.assuranceLevel: "HIGH"
    verification.teeAttestation: TEE attestation proof
    delivery: from Verifier application input
      (quantity, type, timestamp)

Step 9 — Signing (within TEE)
  TEE signs event with Verifier device key
  Signing key never leaves TEE
  Partial events are never produced:
    if signing fails → event discarded entirely

Step 10 — Event queuing
  Signed event written to local event queue
  Verifier application displays confirmation
  to Holder and operator
```

### 3.3 Failure modes

| Failure | Handling |
|---|---|
| Credential not found | Abort — present alternative path |
| Credential expired | Abort — inform Holder to contact Issuer |
| Issuer signature invalid | Abort — log security event |
| Template not found | Abort — present alternative path |
| Biometric match failed (3 attempts) | Abort — present alternative path |
| TEE attestation failed | Abort — log device integrity event |
| Scanner unavailable | Fall through to Path B or C |

---

## 4. Path B — QR Card + PIN Presentation

**Assurance level:** MEDIUM  
**Infrastructure prerequisite:** Physical QR card issued by Issuer  
**Holder requirement:** Physical QR card + knowledge of 4-digit PIN  
**Verifier requirement:** Camera or QR scanner

### 4.1 Precondition

The Issuer has produced a physical QR card for the Holder containing:

- The credential encoded in compact representation (TinyVC-compatible)
- A 4-digit PIN registered at card issuance and known only to the Holder

The card does not contain the PIN. PIN validation uses a PIN hash stored in the credential's `biometricBinding` extension or a separate PIN binding object.

### 4.2 Flow

```
Step 1 — QR scan
  Holder presents physical QR card
  Verifier application scans QR code
  Decodes compact credential representation
  Expands to full credential JSON-LD

Step 2 — Credential validation
  Verifier application verifies:
  - credential schema compliance (R1–R13)
  - Issuer signature validity
  - credential is ACTIVE
  - allowedVerifiers satisfied (if present)
  If any check fails: abort, log failure

Step 3 — PIN entry
  Verifier application prompts operator
  to request PIN from Holder
  Holder states PIN verbally or enters
  on Verifier device keypad
  PIN is never displayed on screen

Step 4 — PIN validation (within TEE)
  TEE computes SHA-256(PIN + credential.id)
  Compares with PIN hash stored in credential
  If match: proceed to Step 5
  If no match:
    increment attempt counter
    if attempts < 3: return to Step 3
      display attempt count to operator
    if attempts = 3: abort
      lock credential for this Verifier session
      log max PIN attempts

Step 5 — Redemption Event construction (within TEE)
  TEE constructs event with:
    id: fresh urn:uuid-v4
    generatedAt: TEE clock timestamp
    holder: credential.credentialSubject.id
    verification.path: "qr-pin"
    verification.assuranceLevel: "MEDIUM"
    verification.pinAttempts: attempt count
    delivery: from Verifier application input

Step 6 — Signing (within TEE)
  TEE signs event with Verifier device key

Step 7 — Event queuing
  Signed event written to local event queue
  Verifier application displays confirmation
```

### 4.3 Card loss and replacement

If a Holder reports a lost card, the Issuer revokes the credential and issues a replacement with a new PIN. The revocation mechanism is an optional Issuer capability outside the base protocol scope.

### 4.4 Failure modes

| Failure | Handling |
|---|---|
| QR unreadable | Request Holder to present card again |
| Credential expired | Abort — inform Holder to contact Issuer |
| Issuer signature invalid | Abort — log security event |
| PIN failed (3 attempts) | Abort — advise Holder to contact Issuer |
| Card damaged beyond reading | Fall through to Path C |

---

## 5. Path C — Documentary Presentation

**Assurance level:** LOW  
**Infrastructure prerequisite:** Central registry accessible via API (online) or Verifier local cache (offline)  
**Holder requirement:** Any identity document containing a resolvable identifier  
**Verifier requirement:** Camera or OCR capability; connectivity (preferred) or cached registry

### 5.1 Precondition

The Issuer maintains a central registry mapping Holder identifiers (national ID number, passport number, or Issuer-assigned pseudonymous ID) to active entitlement credentials.

### 5.2 Flow

```
Step 1 — Document presentation
  Holder presents identity document
  Accepted document types are Issuer-defined
  Examples: national identity card, passport,
  residence permit, Issuer-issued paper notice

Step 2 — Identifier extraction
  Verifier operator reads identifier from document:
  - manual entry
  - camera OCR (if supported by Verifier application)
  Identifier type recorded for event

Step 3 — Registry lookup
  Verifier application queries central registry API:
    GET /credentials?identifier={id}&type={docType}
  Registry returns:
    - credential JSON-LD if found and active
    - not found / expired / suspended status

  If offline and registry unavailable:
    query local credential cache
    if found in cache and within cache TTL:
      proceed with cached credential
      mark event as "offline-lookup"
    if not in cache: abort

Step 4 — Credential validation
  Verifier application verifies:
  - credential schema compliance (R1–R13)
  - Issuer signature validity
  - credential is ACTIVE
  - allowedVerifiers satisfied (if present)
  If any check fails: abort, log failure

Step 5 — Visual identity confirmation
  Verifier operator visually compares:
  - Holder's face against document photo
  - Document does not appear altered or forged
  Operator confirms or rejects
  If rejected: abort, log

Step 6 — Redemption Event construction (within TEE)
  TEE constructs event with:
    id: fresh urn:uuid-v4
    generatedAt: TEE clock timestamp
    holder: credential.credentialSubject.id
    verification.path: "documentary"
    verification.assuranceLevel: "LOW"
    verification.documentType: Issuer-defined type string
    delivery: from Verifier application input

Step 7 — Signing (within TEE)
  TEE signs event with Verifier device key

Step 8 — Event queuing
  Signed event written to local event queue
  Verifier application displays confirmation
```

### 5.3 Offline operation

Path C supports fully offline operation when the Verifier has a local credential cache populated during a prior online session. Cache TTL is Issuer-defined (recommended maximum: 24 hours for active programmes).

Events generated via offline Path C lookup are tagged with `offlineLookup: true` in the verification object. These events carry inherently higher staleness risk (credential may have been revoked or expired since last cache update) and should be flagged for additional Auditor review.

### 5.4 Failure modes

| Failure | Handling |
|---|---|
| Identifier not found in registry | Abort — advise Holder to contact Issuer |
| Credential expired | Abort — inform Holder to contact Issuer |
| Registry unavailable, no cache | Abort — log connectivity failure |
| Cache expired | Abort — do not use stale cached credential |
| Visual confirmation rejected | Abort — log operator decision |
| Document type not accepted | Abort — inform Holder of accepted documents |

---

## 6. Path Selection Logic

The Verifier application should present paths in the following preference order, subject to availability:

```
1. Path A (biometric) — if biometricBinding present
   in credential AND fingerprint scanner available

2. Path B (QR + PIN) — if Holder presents QR card

3. Path C (documentary) — if Holder presents
   identity document AND registry available
   (online or cached)

If no path is available:
  Log inability to serve Holder
  Direct Holder to Issuer for credential
  re-issuance or enrollment
```

The Verifier must never refuse service solely because the highest assurance path is unavailable, if a lower assurance path can proceed. Assurance level is recorded in the event — it is the Auditor's responsibility to apply any programme-specific minimum assurance requirements.

---

## 7. Multi-Path Fallback Sequences

The following fallback sequences are explicitly supported:

**Path A → Path B:** Fingerprint scanner unavailable or biometric match failed after 3 attempts. Verifier prompts Holder for QR card.

**Path A → Path C:** No biometric enrollment and no QR card. Holder presents identity document.

**Path B → Path C:** QR card damaged or PIN locked. Holder presents identity document.

**Path A → Path B → Path C:** Full fallback sequence. Each step attempted before proceeding to next.

In all fallback sequences, the assurance level in the final event reflects the path that succeeded — not the highest path attempted. Failed attempts are logged but do not appear in the Redemption Event.

---

## 8. Enrollment Flow (Path A prerequisite)

Biometric enrollment is a prerequisite for Path A. Enrollment is performed once per Holder at an accredited enrollment point — distinct from the delivery point.

```
Step 1 — Identity verification at enrollment point
  Enrollment operator verifies Holder identity
  using documentary path (equivalent to Path C
  but without generating a Redemption Event)
  Enrollment assurance level recorded

Step 2 — Biometric capture
  3× fingerprint scans
  Same pipeline as Path A verification:
  Tensor RPCA → Fourier-Mellin → Neural extractor
  → enrollment vector E

Step 3 — Template storage
  One-way transform applied to E
  → protected template T
  Raw vector E discarded immediately
  T stored per templateLocation configuration:
    "credential": T embedded in credential
    "verifier-local": T stored in Verifier registry,
    templateId recorded in credential

Step 4 — Credential update or issuance
  biometricBinding object added to credential
  Credential re-signed by Issuer with updated content
  New credential delivered to Holder
  (wallet / replacement QR card / registry update)

Step 5 — Confirmation
  Holder confirms enrollment completion
  Enrollment event logged (not a Redemption Event)
  with: enrolledAt, enrollmentAssurance,
  templateVersion, templateLocation
```

Enrollment may be performed at the same session as first credential issuance, or at a later date. The protocol supports both.

---

## 9. Relation to Other Specifications

| Specification | Relation |
|---|---|
| protocol-overview.md | Defines the three paths at summary level |
| credential-schema.md | Defines biometricBinding object used in Path A |
| redemption-event.md | Defines the event generated by all paths |
| audit-trail.md | Consumes events generated by all paths |

---

## 10. Open Issues

- [ ] PIN binding object — formal schema for PIN hash storage in credential (v0.2)
- [ ] Offline cache TTL — default value and Issuer configuration schema (v0.2)
- [ ] NFC presentation for Path B — ISO 18013-5 proximity flow as alternative to QR (v0.3)
- [ ] EUDIW wallet as Path A or B equivalent — OpenID4VP integration (v0.3)
- [ ] Enrollment point accreditation schema (v0.3)
- [ ] Multi-biometric enrollment — fallback to facial recognition where fingerprint unavailable (v0.4)

---

## References

- DTEP-S Protocol Overview: ./protocol-overview.md
- DTEP-S Credential Schema Specification: ./credential-schema.md
- DTEP-S Redemption Event Specification: ./redemption-event.md
- ISO/IEC 18013-5 Mobile Driving Licence: https://www.iso.org/standard/69084.html
- OpenID for Verifiable Presentations: https://openid.net/specs/openid-4-verifiable-presentations-1_0.html
- TinyVC QR-compatible VC: https://www.turing.ac.uk/sites/default/files/2023-04/technical_brief_-tinyid_qr_code_based_verifiable_credentials.pdf
