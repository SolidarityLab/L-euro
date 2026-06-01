# DTEP-S Credential Schema Specification

**Version:** 0.1-draft  
**Status:** Specification in progress  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document specifies the credential schema for DTEP-S entitlement credentials. The schema defines the minimum required fields and extension points for any credential issued within the DTEP-S protocol, regardless of domain, entitlement type, or delivery modality.

The schema does not prescribe specific entitlement types, goods categories, or delivery parameters. These are Issuer-defined extensions conformant with the base schema.

---

## 2. Design Principles

**Minimality** — the base schema contains only what the protocol requires to function. Everything else is an extension.

**Extensibility** — any Issuer-defined parameter set is valid if it conforms to the base schema invariants.

**Domain neutrality** — the schema makes no assumptions about the nature of the entitlement. Humanitarian accommodation, food delivery, healthcare access, school canteen subscriptions, and any other fund- or subscription-based entitlement model are equivalent configurations.

**Device independence** — the schema is valid regardless of how the Holder presents it: digital wallet, physical QR card, or central registry lookup.

**Verifier autonomy** — a Verifier can validate any DTEP-S credential using only the Issuer's public key and the base schema. No domain-specific knowledge is required for protocol-level validation.

---

## 3. Base Schema

### 3.1 Credential envelope

All DTEP-S credentials are W3C Verifiable Credentials 2.0 documents.

Required fields:

```
@context          array     must include W3C VC v2 context
                            and DTEP-S context
type              array     must include "VerifiableCredential"
                            and "DTEPEntitlementCredential"
id                string    globally unique credential identifier
                            recommended: urn:uuid:{uuid}
issuer            object    issuer DID and optional metadata
issuanceDate      string    ISO-8601 datetime
expirationDate    string    ISO-8601 datetime — required,
                            must be explicitly set by Issuer
credentialSubject object    see section 3.2
proof             object    see section 3.4
```

### 3.2 credentialSubject — required fields

```
id                string    subject identifier
                            may be a DID, a pseudonym, or an
                            Issuer-assigned opaque identifier
                            real identity is never required
                            in the credential itself

entitlement       object    see section 3.3

biometricBinding  object    optional — present if biometric
                            enrollment was performed
                            see section 3.5
```

### 3.3 entitlement object — required fields

```
type              string    Issuer-defined entitlement type
                            free string — protocol does not
                            constrain values
                            examples: "humanitarian.accommodation"
                            "social.food_delivery"
                            "education.canteen"
                            "health.pharmacy"

issuerRef         string    Issuer-internal reference
                            links credential to Issuer registry

validFrom         string    ISO-8601 datetime
                            entitlement validity start

validUntil        string    ISO-8601 datetime
                            entitlement validity end
                            must equal or precede
                            credential expirationDate

redemptionPolicy  object    see section 3.3.1

allowedVerifiers  object    optional — see section 3.3.2

extensions        object    optional — Issuer-defined
                            domain-specific parameters
                            no schema constraints
                            must not conflict with
                            base schema field names
```

### 3.3.1 redemptionPolicy object

Defines the rules under which a Redemption Event is valid for this credential.

```
maxRedemptions    integer   optional
                            maximum total redemptions allowed
                            omit for unlimited

frequency         object    optional
                            controls redemption rate

  period          string    "hour" | "day" | "week" | "month"
  maxPerPeriod    integer   maximum redemptions per period

quantityPerEvent  object    optional
                            controls quantity per single redemption

  min             number    minimum quantity per event
  max             number    maximum quantity per event
  unit            string    Issuer-defined unit string
                            examples: "night" "meal" "kg" "unit"
                            omit if not applicable

requiresPresence  boolean   default: true
                            if true: Holder must be physically
                            present at delivery point
                            if false: proxy or delivery
                            without Holder is permitted
```

### 3.3.2 allowedVerifiers object

Optional constraint on which Verifiers may redeem this credential.

```
accreditationScheme   string    Issuer-defined scheme identifier
                                example: "BG-MOT-2026"
                                (Bulgaria Ministry of Tourism
                                accreditation scheme)

accreditationIds      array     optional list of specific
                                accreditation identifiers
                                omit to allow any Verifier
                                accredited under the scheme

verifierCategories    array     optional list of Issuer-defined
                                category strings
                                example: ["hotel" "hostel"]
                                omit to allow all categories
```

### 3.4 proof object

```
type              string    "DataIntegrityProof"

cryptosuite       string    "eddsa-rdfc-2022" — required
                            Ed25519 signature over
                            canonicalised credential

created           string    ISO-8601 datetime of signing

verificationMethod string   Issuer key identifier
                            must resolve to Issuer's
                            public key

proofPurpose      string    "assertionMethod"

proofValue        string    base58btc-encoded Ed25519 signature
```

### 3.5 biometricBinding object

Present only when Holder has enrolled biometric data. Absence of this object indicates no biometric enrollment — Verifier must use an alternative presentation path.

```
templateId        string    opaque identifier of enrolled template
                            does not contain or allow
                            reconstruction of biometric data

templateLocation  string    "credential" | "verifier-local"
                            "credential": protected template
                            vector stored in this credential
                            "verifier-local": template stored
                            in Verifier device registry,
                            referenced by templateId

templateVersion   string    pipeline version string
                            identifies the biometric pipeline
                            used for enrollment
                            example: "dtep-s-bio-v0.1"

enrolledAt        string    ISO-8601 datetime of enrollment

enrollmentAssurance string  "HIGH" | "MEDIUM"
                            HIGH: supervised enrollment
                            at accredited enrollment point
                            MEDIUM: self-enrollment
                            with institutional verification
```

---

## 4. Validation Rules

A DTEP-S credential is **protocol-valid** if and only if:

```
R1  @context includes both W3C VC v2 and DTEP-S context URIs

R2  type includes both "VerifiableCredential"
    and "DTEPEntitlementCredential"

R3  id is present and unique within Issuer scope

R4  issuer.id is a resolvable DID

R5  issuanceDate is present and syntactically valid ISO-8601

R6  expirationDate is present, syntactically valid ISO-8601,
    and strictly after issuanceDate

R7  credentialSubject.id is present

R8  credentialSubject.entitlement.type is present
    and non-empty string

R9  credentialSubject.entitlement.issuerRef is present

R10 credentialSubject.entitlement.validFrom is present
    and not before issuanceDate

R11 credentialSubject.entitlement.validUntil is present
    and not after expirationDate

R12 proof.cryptosuite is "eddsa-rdfc-2022"

R13 proof.proofValue verifies against Issuer public key
    resolved from proof.verificationMethod
```

A credential that fails any of R1–R13 must be rejected by the Verifier. Domain-specific extension fields are not subject to protocol-level validation — they are the Issuer's responsibility.

---

## 5. Credential Lifecycle

```
DRAFT       Credential constructed by Issuer, not yet signed
ISSUED      Credential signed and delivered to Holder
ACTIVE      Current datetime is within validFrom–validUntil
SUSPENDED   Issuer has temporarily revoked — optional feature
EXPIRED     Current datetime is after validUntil
EXHAUSTED   maxRedemptions reached — determined by Auditor
REVOKED     Issuer has permanently invalidated
```

State transitions:

```
DRAFT → ISSUED → ACTIVE → EXPIRED
                        → EXHAUSTED
             → SUSPENDED → ACTIVE
             → REVOKED
```

Verifier checks ACTIVE state before accepting any redemption. Revocation and suspension are optional Issuer capabilities — their implementation is outside the base protocol scope.

---

## 6. Presentation Paths and Credential Requirements

The credential schema is identical across all three presentation paths. The presentation path affects only how the credential reaches the Verifier — not what the credential contains.

| Presentation path | Credential transport | Additional requirement |
|---|---|---|
| Digital wallet | OpenID4VP / proximity | wallet signature on presentation |
| Physical QR card | QR scan | credential compressed per TinyVC spec |
| Central lookup | API query | Issuer registry returns credential JSON |

In all paths, the Verifier validates the credential against the base schema and the Issuer signature before proceeding to Holder identity verification.

---

## 7. Extension Mechanism

Issuer-defined extensions are placed in `credentialSubject.entitlement.extensions`. No field name constraints apply within this object except:

- Extension field names must not duplicate base schema field names
- Extension fields must not alter the semantics of base schema fields
- Extensions must not introduce additional validation requirements at protocol level

Example extension for humanitarian accommodation:

```json
"extensions": {
  "programme": "BG-TPD-2026-P3",
  "accommodationType": "collective",
  "mealsIncluded": true,
  "familyUnit": {
    "adults": 1,
    "children": 2
  }
}
```

Example extension for school canteen:

```json
"extensions": {
  "institution": "SU-Sofia-42",
  "mealTypes": ["lunch"],
  "dietaryFlags": ["vegetarian"],
  "academicYear": "2026-2027"
}
```

Both are protocol-valid credentials with identical base schema compliance.

---

## 8. Compact Representation for QR Cards

Physical QR cards require credential compression. DTEP-S adopts the TinyVC approach for QR-compatible serialisation:

- Base schema fields serialised in compact JSON
- Proof reduced to signature bytes only — verification method resolved separately
- Extensions included only if essential for Verifier operation
- Total payload target: under 2953 bytes (QR version 40, binary mode)

Full compact representation specification: to be defined in v0.2.

---

## 9. JSON-LD Context

DTEP-S defines a context document at:

```
https://dtep-s.solidaritylab.org/context/v1
```

This context maps DTEP-S-specific terms to their definitions. The context document will be published alongside the v0.2 specification.

Until the context document is published, implementations should use the inline `@context` extension pattern defined in W3C VC 2.0 section 5.3.

---

## 10. Open Issues

- [ ] Compact QR representation — detailed byte budget (v0.2)
- [ ] Context document publication (v0.2)
- [ ] Revocation mechanism specification — optional Issuer capability (v0.3)
- [ ] Multi-issuer credential support — for cross-border scenarios (v0.4)
- [ ] Formal JSON Schema for machine validation (v0.2)
- [ ] Credential versioning and migration path (v0.3)

---

## References

- W3C Verifiable Credentials Data Model v2.0: https://www.w3.org/TR/vc-data-model-2.0/
- W3C DID Core: https://www.w3.org/TR/did-core/
- Data Integrity EdDSA Cryptosuites v1.0: https://www.w3.org/TR/vc-di-eddsa/
- TinyVC QR-compatible VC compression: https://www.turing.ac.uk/sites/default/files/2023-04/technical_brief_-tinyid_qr_code_based_verifiable_credentials.pdf
- OpenID for Verifiable Presentations: https://openid.net/specs/openid-4-verifiable-presentations-1_0.html
