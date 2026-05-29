# DTEP-S Redemption Event Specification

**Version:** 0.1-draft  
**Status:** Specification in progress  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document specifies the Redemption Event — the core evidence artifact of the DTEP-S protocol. A Redemption Event is a cryptographically signed record that a specific entitlement credential was exercised at a specific delivery point at a specific time, under a specific verification modality.

The Redemption Event is the protocol's answer to the structural gap between the Act of Delivery and the Payment elements of the chain:

```
Right → Identification → Act of Delivery → Payment
                              ↑
                     Redemption Event
                     is generated here
```

Every Redemption Event must be independently verifiable by any Auditor holding the Verifier's public key — without access to any other system.

---

## 2. Design Principles

**Self-contained evidence** — a Redemption Event carries all information necessary for audit validation without requiring access to external systems at validation time.

**Atomic generation** — the Redemption Event is generated and signed in a single atomic operation within the Verifier's Trusted Execution Environment. It cannot be produced without a preceding successful Holder verification.

**Assurance transparency** — every event declares the verification modality and assurance level used. The Auditor always knows how the Holder was verified.

**Offline first** — events are generated and cryptographically valid without network connectivity. Transmission to the Auditor is asynchronous.

**Non-repudiation** — a signed Redemption Event cannot be denied by either the Verifier (who signed it) or the Holder (whose credential was exercised).

**Minimal Holder data** — the event references the Holder by credential subject ID only. Real identity resolution is the Issuer's responsibility and is never required in the event itself.

---

## 3. Redemption Event Structure

### 3.1 Envelope

```
@context          array     must include W3C VC v2 context
                            and DTEP-S context

type              array     must include
                            "VerifiablePresentation"
                            and "DTEPRedemptionEvent"

id                string    globally unique event identifier
                            required: urn:uuid:{uuid-v4}
                            generated fresh for every event
                            must never be reused

generatedAt       string    ISO-8601 datetime with timezone
                            timestamp of event generation
                            set by Verifier device clock
                            within TEE — not modifiable
                            after signing

holder            string    credentialSubject.id from
                            the presented credential

verifier          object    see section 3.2

credential        object    see section 3.3

verification      object    see section 3.4

delivery          object    see section 3.5

proof             object    see section 3.6
```

### 3.2 verifier object

```
id                string    Verifier DID
                            resolves to Verifier device
                            public key

accreditationId   string    Verifier's accreditation identifier
                            within the scheme declared in
                            the credential's allowedVerifiers

deviceId          string    opaque stable device identifier
                            used for anomaly detection
                            must not be a hardware serial
                            number or other PII-linked id

softwareVersion   string    DTEP-S Verifier application
                            version string
```

### 3.3 credential object

```
id                string    credential id from presented
                            credential

issuer            string    credential issuer DID

entitlementType   string    credentialSubject.entitlement.type
                            from presented credential
                            copied verbatim — not interpreted

issuerRef         string    credentialSubject.entitlement
                            .issuerRef from presented credential
                            enables Issuer-side lookup
                            without credential re-presentation

credentialHash    string    SHA-256 hash of canonical
                            credential JSON-LD
                            enables integrity check without
                            storing full credential in event
```

### 3.4 verification object

Declares how the Holder was verified. This object is set within the TEE and is part of the signed payload — it cannot be modified after signing.

```
path              string    "biometric" | "qr-pin" | "documentary"
                            the presentation path used

assuranceLevel    string    "HIGH" | "MEDIUM" | "LOW"
                            derived from path:
                            biometric     → HIGH
                            qr-pin        → MEDIUM
                            documentary   → LOW

teeAttestation    string    present only when path is "biometric"
                            TEE-generated attestation proving
                            that signing occurred within
                            secure enclave after successful
                            biometric match
                            format: platform-specific
                            (Android StrongBox / iOS Secure
                            Enclave attestation)

pinAttempts       integer   present only when path is "qr-pin"
                            number of PIN attempts before
                            success — always 1, 2, or 3
                            value above 3 is impossible
                            (credential locked on 3rd failure)

documentType      string    present only when path is
                            "documentary"
                            Issuer-defined document type string
                            example: "national-id" "passport"
                            "residence-permit"
```

### 3.5 delivery object

Records what was delivered. The protocol does not constrain the content of this object beyond the required fields — Issuer-defined entitlement parameters determine what is meaningful here.

```
timestamp         string    ISO-8601 datetime of delivery
                            may differ from generatedAt
                            if event is generated after
                            physical delivery completes
                            must not precede generatedAt
                            by more than the Issuer-defined
                            delivery window

location          object    optional

  type            string    "coordinates" | "address"
                            | "verifierPremises"
  value           string    location value in declared type
                            "verifierPremises" requires no
                            value — Verifier's registered
                            address is used

items             array     one or more delivery items
                            see section 3.5.1

extensions        object    optional
                            Issuer-defined delivery parameters
                            no schema constraints
```

### 3.5.1 delivery item object

```
type              string    Issuer-defined item type string
                            must correspond to entitlement
                            type declared in credential
                            protocol does not validate
                            this correspondence —
                            Auditor responsibility

quantity          number    quantity delivered
                            must be positive

unit              string    Issuer-defined unit string
                            must match unit declared in
                            credential redemptionPolicy
                            if policy is present

periodCovered     object    optional
                            for time-based entitlements

  from            string    ISO-8601 date
  until           string    ISO-8601 date
```

### 3.6 proof object

```
type              string    "DataIntegrityProof"

cryptosuite       string    "eddsa-rdfc-2022"

created           string    ISO-8601 datetime
                            must equal envelope generatedAt

verificationMethod string   Verifier device key identifier
                            resolves to Verifier device
                            public key

proofPurpose      string    "assertionMethod"

proofValue        string    base58btc-encoded Ed25519 signature
                            over canonicalised event JSON-LD
```

---

## 4. Validation Rules

A Redemption Event is **protocol-valid** if and only if:

```
R1  @context includes W3C VC v2 and DTEP-S context URIs

R2  type includes "VerifiablePresentation"
    and "DTEPRedemptionEvent"

R3  id is present, follows urn:uuid: pattern,
    and has not been seen before in Auditor log

R4  generatedAt is present and syntactically valid ISO-8601

R5  holder is present and non-empty

R6  verifier.id is present and resolvable DID

R7  verifier.accreditationId is present

R8  credential.id is present

R9  credential.issuer is present

R10 credential.entitlementType is present and non-empty

R11 credential.credentialHash is present
    and matches SHA-256 of presented credential
    when credential is available for cross-check

R12 verification.path is one of the three defined values

R13 verification.assuranceLevel corresponds to
    verification.path per the defined mapping

R14 verification.teeAttestation is present
    when verification.path is "biometric"

R15 delivery.timestamp is present and valid ISO-8601

R16 delivery.items contains at least one item

R17 each delivery item has type, quantity, and unit

R18 delivery item quantity is positive

R19 proof.cryptosuite is "eddsa-rdfc-2022"

R20 proof.created equals envelope generatedAt

R21 proof.proofValue verifies against Verifier device
    public key resolved from proof.verificationMethod
```

Events failing R3 (duplicate ID) must be flagged as potential replay attacks.
Events failing R21 (invalid signature) must be rejected and flagged.
Events failing R14 (missing TEE attestation for biometric path) must be downgraded to assuranceLevel LOW and flagged for review.

---

## 5. Generation Flow

The following sequence is mandatory for protocol-compliant event generation. Steps 1–6 execute within the TEE.

```
1. Verifier application reads credential
   (from wallet / QR scan / API lookup)

2. Verifier application verifies Issuer signature
   on credential (R19-R21 equivalent for credential)
   → if invalid: abort, log failure

3. Verifier application checks credential validity:
   - current datetime within validFrom–validUntil
   - allowedVerifiers satisfied (if present)
   → if invalid: abort, log failure

4. Verifier application executes Holder verification:
   → biometric path: pipeline → TEE match
   → qr-pin path: PIN entry → TEE verify
   → documentary path: visual confirmation → record

5. TEE constructs Redemption Event with:
   - fresh urn:uuid id
   - generatedAt = current TEE clock
   - verification object reflecting outcome of step 4
   - teeAttestation if biometric path

6. TEE signs event with Verifier device key
   → signing key never leaves TEE

7. Signed event written to local event queue

8. Event transmitted to Auditor endpoint
   (immediately if online / queued if offline)
```

Steps 5 and 6 are atomic — if signing fails, the event is discarded entirely. A partial event must never be stored or transmitted.

---

## 6. Transmission and Storage

### 6.1 Online transmission

Events are transmitted to the Auditor endpoint via HTTPS POST as JSON-LD documents. The Auditor returns a receipt acknowledging event ID and timestamp. Transmission is considered successful only upon receipt of acknowledgement.

### 6.2 Offline operation

When Auditor endpoint is unreachable, events are stored in the local Verifier event queue — an append-only log on the Verifier device. The queue is encrypted at rest using the Verifier device key.

Queued events are transmitted in chronological order when connectivity is restored. The Auditor must accept events with generatedAt timestamps preceding transmission time, up to the Issuer-defined maximum queue window (default: 30 days).

### 6.3 Auditor storage

The Auditor stores events in an append-only log indexed by:
- event id (for duplicate detection)
- credential.issuerRef (for settlement aggregation)
- verifier.id (for per-verifier reporting)
- delivery.timestamp (for period-based reporting)

Events must be retained for the period defined by applicable audit regulations. The protocol does not prescribe a retention period — this is Auditor jurisdiction.

---

## 7. Batch Export

For Auditor scenarios without real-time connectivity (Deployment Scenario 2 and 4 from protocol-overview), Verifiers may export events as a signed batch:

```
DTEPBatchExport
  id              urn:uuid — batch identifier
  exportedAt      ISO-8601 datetime
  verifier        verifier object (same as in events)
  eventCount      integer — number of events in batch
  events          array of Redemption Event objects
  batchProof      Ed25519 signature over canonical
                  batch document by Verifier device key
```

Individual event proofs remain valid within the batch. The batch proof provides additional integrity guarantee over the complete set.

---

## 8. Anomaly Indicators

The following patterns must be flagged for Auditor review. They do not automatically invalidate events but indicate potential misuse:

```
A1  Duplicate event id
    → potential replay attack

A2  Multiple events for same credential.id
    within a period shorter than
    redemptionPolicy.frequency.period

A3  Events exceeding redemptionPolicy.maxRedemptions
    for a credential

A4  High event volume from single verifier.deviceId
    within short time window

A5  Events with assuranceLevel LOW for credential
    that has biometricBinding present in credential
    → Holder enrolled biometrics but biometric path
      was not used — may indicate card sharing

A6  Events with delivery.timestamp significantly
    preceding generatedAt
    → may indicate batch fabrication

A7  Events transmitted long after generatedAt
    without documented offline queue explanation
```

Anomaly detection logic is an Auditor implementation responsibility. The protocol defines the indicators — not the thresholds or response procedures.

---

## 9. Privacy Considerations

**Holder pseudonymity** — the event references Holder by credential subject ID. If the Issuer uses opaque pseudonymous identifiers as subject IDs, the Auditor cannot link events to real identities without Issuer cooperation.

**Minimal location data** — location field is optional. When present, "verifierPremises" is preferred over coordinates as it avoids recording Holder movement patterns.

**No biometric data in events** — biometric data never appears in Redemption Events. The teeAttestation proves that biometric verification occurred within the TEE — it does not contain or allow reconstruction of biometric data.

**Aggregation risk** — sequences of events for the same credential subject ID constitute a transaction history. Issuers and Auditors must implement appropriate access controls to prevent unauthorised profiling.

---

## 10. Open Issues

- [ ] TEE attestation format per platform — Android StrongBox and iOS Secure Enclave (v0.2)
- [ ] Auditor endpoint API specification (v0.2)
- [ ] Batch export format — detailed schema (v0.2)
- [ ] Credential revocation check at event generation (v0.3)
- [ ] Cross-Issuer event validation for multi-programme scenarios (v0.4)
- [ ] Formal JSON Schema for machine validation (v0.2)
- [ ] Maximum queue window — default value rationale (v0.2)

---

## References

- W3C Verifiable Credentials Data Model v2.0: https://www.w3.org/TR/vc-data-model-2.0/
- W3C DID Core: https://www.w3.org/TR/did-core/
- Data Integrity EdDSA Cryptosuites v1.0: https://www.w3.org/TR/vc-di-eddsa/
- DTEP-S Credential Schema Specification: ./credential-schema.md
- DTEP-S Protocol Overview: ./protocol-overview.md
- Android StrongBox Keymaster: https://source.android.com/docs/security/features/keystore
- Apple Secure Enclave: https://support.apple.com/guide/security/secure-enclave-sec59b0b31ff/web
