# DTEP-S GDPR Analysis

**Version:** 0.1-draft  
**Status:** Specification in progress  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document analyses the GDPR compliance framework for the DTEP-S protocol.
It identifies the categories of personal data processed, the applicable legal
bases, the data subjects' rights, and the technical and organisational measures
implementing privacy by design.

This analysis covers the operational chain: Issuer → Holder → Verifier → Auditor.

---

## 2. Data Categories Processed

### 2.1 Entitlement credential data

**Content:** Credential subject identifier (pseudonymous DID or registry
reference), entitlement type, validity period, redemption conditions, Issuer
identifier.

**Classification:** Personal data (pseudonymous). Not directly identifying
without access to the Issuer's beneficiary registry.

**Controller:** Issuer institution.

---

### 2.2 Biometric data (Path A — HIGH assurance only)

**Content:** Fingerprint-derived feature vector (one-way transformed). Raw
fingerprint images are never stored.

**Classification:** Special category personal data under Article 9 GDPR.

**Controller:** Issuer institution (enrollment); Verifier (local template
storage for matching, if applicable).

**Key technical property:** The enrolled template is a one-way transformed
neural feature vector. Reconstruction of the original fingerprint from the
stored vector is not technically feasible with current methods. This is a
technical guarantee of data minimisation, not a policy commitment.

---

### 2.3 Redemption Event data

**Content:** Pseudonymous credential subject ID, Verifier identifier,
timestamp, delivery type and quantity, assurance level, optional geolocation,
Ed25519 signature.

**Classification:** Personal data (pseudonymous). Not directly identifying
without access to the Issuer's beneficiary registry.

**Controller:** Verifier (generation); Auditor (storage and processing).

---

### 2.4 Audit trail data

**Content:** Merkle tree of Redemption Event hashes, periodic trail roots,
anchoring proofs. No additional personal data beyond what is in Redemption
Events.

**Classification:** Personal data (pseudonymous) — inherits classification from
Redemption Events.

**Controller:** Auditor.

---

## 3. Legal Bases

### 3.1 Non-biometric processing

Processing of entitlement credentials, Redemption Events, and audit trail data:

**Article 6(1)(e) GDPR** — processing is necessary for the performance of a
task carried out in the public interest or in the exercise of official authority
vested in the controller.

Applicable for Issuer (social protection mandate), Verifier (accredited provider
under public programme), and Auditor (Ministry-level oversight).

**Article 6(1)(c) GDPR** — processing is necessary for compliance with a legal
obligation.

Applicable for settlement and audit obligations under Council of Ministers
decisions governing humanitarian programmes.

---

### 3.2 Biometric data processing

Biometric data is special category data under Article 9(1) GDPR. Processing
requires an explicit Article 9(2) basis.

**Primary basis — Article 9(2)(b) GDPR:**
Processing is necessary for the purposes of carrying out the obligations and
exercising specific rights of the controller or of the data subject in the field
of employment and social security and social protection law, in so far as it is
authorised by Union or Member State law providing for appropriate safeguards.

Applicable for: verification of entitlement delivery under social protection
programmes (humanitarian accommodation, social assistance deliveries).

**Secondary basis — Article 9(2)(d) GDPR:**
Processing is carried out in the course of its legitimate activities with
appropriate safeguards by a foundation, association or any other not-for-profit
body with a political, philosophical, religious or trade union aim, provided the
processing relates solely to members or former members of that body or to persons
who have regular contact with it in connection with its purposes, and the
personal data are not disclosed outside that body.

Applicable for: CSDT in its capacity as protocol developer and reference
implementation operator during sandbox phase.

**Important constraint:** In the humanitarian context, data subjects (persons
under temporary protection, social assistance recipients) are in a potentially
vulnerable position. Article 7(4) GDPR applies — consent shall not be freely
given if its refusal results in detriment to the data subject. Therefore:

- Biometric enrollment MUST be offered as an option, not a requirement
- Access to the entitlement MUST be available through non-biometric paths
  (QR+PIN or documentary lookup) regardless of biometric enrollment status
- This is enforced at protocol level: Path B and Path C are always available

---

## 4. Data Subject Rights

### 4.1 Right of access (Article 15)

Data subjects may request access to their personal data. The Issuer maintains
the authoritative record linking pseudonymous credential subject IDs to
real identities. Verifiers and Auditors hold pseudonymous data only.

**Implementation:** Issuer implements a subject access mechanism mapping
credential subject ID to all associated Redemption Events via the Auditor's
index. This is outside DTEP-S protocol scope but required for GDPR compliance
of the overall system.

---

### 4.2 Right to erasure (Article 17)

**Audit trail data:** The immutable Merkle tree audit trail is in direct tension
with the right to erasure. This tension is resolved as follows:

The audit trail contains hashes of Redemption Events, not the events themselves.
Deletion of the underlying Redemption Event renders the corresponding hash
unverifiable but does not require modification of the Merkle tree structure.
The trail root remains valid for all non-deleted events.

For the humanitarian programme context, the right to erasure is restricted
under Article 17(3)(b) — processing is necessary for the performance of a task
carried out in the public interest — and Article 17(3)(e) — processing is
necessary for the establishment, exercise or defence of legal claims (audit and
recovery proceedings).

---

### 4.3 Right to data portability (Article 20)

Not applicable for processing under Article 6(1)(e). Applicable for any
consent-based processing (biometric enrollment where consent is the chosen basis
at Member State level).

---

### 4.4 Right to object (Article 21)

Data subjects may object to processing under Article 6(1)(e). In the
humanitarian programme context, objection to delivery verification processing
effectively constitutes withdrawal from the programme. This must be clearly
communicated at enrollment.

---

## 5. Privacy by Design — Technical Measures

### 5.1 Data minimisation

Redemption Events contain the minimum data required for settlement and audit:
pseudonymous subject ID, verifier ID, timestamp, delivery type and quantity,
assurance level. No name, address, nationality, or case file data is included.

The Auditor receives pseudonymous data. Real identity resolution requires
cross-reference with the Issuer registry, which the Auditor does not hold.

### 5.2 Pseudonymisation

Holder real identity is maintained only by the Issuer. All downstream processing
(Verifier, Auditor) uses the credential subject ID as pseudonymous identifier.
The pseudonymisation is strong: reversal requires access to the Issuer registry,
which is an institutional system with its own access controls.

### 5.3 No central biometric database

Biometric templates are stored locally on the Verifier device within
TEE-protected storage, or within the encrypted credential held by the Holder.
No centralised biometric database is created or required by the protocol.
This is a technical impossibility enforced by architecture, not a policy commitment.

### 5.4 One-way biometric transformation

Raw biometric data (fingerprint images) is processed at enrollment to produce
a feature vector. The transformation is one-way — reconstruction of the original
fingerprint from the stored vector is not technically feasible. The three-scan
aggregation with Tensor RPCA and Fourier-Mellin normalisation produces a
representation that captures verification-relevant features without preserving
reconstruction-relevant information.

### 5.5 Purpose limitation

Redemption Events are generated solely for the purpose of settlement and audit
of entitlement delivery. The protocol does not support secondary use of
Redemption Event data for any other purpose. Auditors receiving Redemption
Events are bound by the purpose limitation in the settlement agreement.

---

## 6. Data Protection Impact Assessment

A full DPIA is required before operational deployment of DTEP-S in any
humanitarian or social protection programme, pursuant to Article 35 GDPR
(processing of special category data on a large scale; systematic monitoring
of data subjects in a public area).

The DPIA must be conducted by the Issuer institution as data controller.
DTEP-S provides the technical architecture and this analysis as inputs to
the DPIA process.

Key DPIA findings anticipated:

- **High risk:** Biometric data processing — mitigated by technical measures
  in Section 5 and non-biometric path availability
- **High risk:** Immutable audit trail — mitigated by pseudonymisation and
  erasure limitation justification in Section 4.2
- **Medium risk:** Cross-border data flows if Auditor is in a different Member
  State from Verifier — standard Chapter V GDPR transfers apply

---

## 7. Applicable Law — Bulgarian Context

For the immediate deployment context (Bulgarian humanitarian accommodation
programme):

- **GDPR** (Regulation 2016/679) — directly applicable
- **ZZLD** (Закон за защита на личните данни) — Bulgarian implementing law
- **KZLD** (Комисия за защита на личните данни) — supervisory authority
- **Council of Ministers decisions** governing the humanitarian programme —
  legal basis for Article 6(1)(c) and Article 9(2)(b) processing

The Issuer (Agency for Social Assistance) is required to consult KZLD prior
to operational deployment pursuant to Article 36 GDPR (prior consultation where
DPIA indicates high residual risk).

---

## 8. Open Issues

- [ ] Consent mechanism specification for biometric enrollment (v0.2)
- [ ] Erasure procedure for Redemption Events (v0.3)
- [ ] Cross-border transfer analysis for multi-Member-State deployment (v0.3)
- [ ] DPIA template for Issuer institutions (v0.9)
