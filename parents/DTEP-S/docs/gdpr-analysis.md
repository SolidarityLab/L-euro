# DTEP-S GDPR Analysis

**Version:** 0.1-draft  
**Status:** Specification in progress  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document analyses the GDPR compliance framework for the DTEP-S protocol. It identifies the categories of personal data processed at each stage of the protocol, the applicable legal bases, the data subjects' rights, and the technical and organisational measures implementing privacy by design.

This analysis covers the full operational chain: Issuer → Holder → Verifier → Auditor.

This analysis covers the protocol specification. Implementations must conduct their own Data Protection Impact Assessments (DPIA) in accordance with Article 35 GDPR, particularly when processing biometric data at scale. This document provides analytical input for the DPIA but does not constitute the DPIA itself.

---

## 2. Personal Data in DTEP-S

### 2.1 Credential issuance (Issuer)

| Data element | Category | Necessity |
|---|---|---|
| Holder real identity (name, ID number) | Personal data (Art. 4) | Required by Issuer for entitlement assessment. NOT present in credential or events. |
| Issuer-assigned subject ID | Pseudonymous identifier | Present in credential. Links credential to Issuer registry. |
| Entitlement parameters | Non-personal (domain-specific) | Present in credential. Validity period, redemption conditions, Issuer identifier. |
| Biometric template (if enrolled) | Special category (Art. 9) | Optional. One-way transformed vector only. Raw fingerprint images never stored. |

**Key design decision:** The credential contains a pseudonymous subject ID — not the Holder's real identity. Real identity is retained only by the Issuer in their internal registry. This is structural — not a policy choice.

**Controller:** Issuer institution.

### 2.2 Redemption Event (Verifier)

| Data element | Category | Necessity |
|---|---|---|
| Holder subject ID | Pseudonymous identifier | Links event to credential. Real identity not present. |
| Delivery timestamp | Temporal data | Required for audit. |
| Delivery type and quantity | Non-personal (domain-specific) | Required for settlement. |
| Assurance level | Technical metadata | Required for audit. |
| Delivery location | Potentially personal | Optional. `verifierPremises` preferred to avoid location tracking. |
| Verifier device ID | Pseudonymous identifier | Required for anomaly detection. Not linked to natural person. |
| TEE attestation | Technical proof | Present only in biometric path. Contains no biometric data. |

**Key design decision:** Redemption Events do not contain biometric data, real identity, or reconstructable personal identifiers. A sequence of events for the same subject ID constitutes a transaction history — see section 5.1 on re-identification risk.

**Controllers:** Verifier (generation); Auditor (storage and processing).

### 2.3 Audit trail (Auditor)

| Data element | Category | Necessity |
|---|---|---|
| Merkle leaf hashes | Non-personal | Cryptographic integrity only. |
| Trail root documents | Non-personal | Published commitments. No personal data. |
| Audit reports | Aggregated / pseudonymous | Pseudonymous subject IDs in anomaly records only. |

The audit trail contains hashes of Redemption Events — not the events themselves. It inherits the pseudonymous classification of Redemption Events.

**Controller:** Auditor.

---

## 3. Legal Bases

### 3.1 Non-biometric processing

Processing of entitlement credentials, Redemption Events, and audit trail data is based on:

**Article 6(1)(e) GDPR** — processing necessary for the performance of a task carried out in the public interest or in the exercise of official authority vested in the controller. Applicable for Issuer (social protection mandate), Verifier (accredited provider under public programme), and Auditor (Ministry-level oversight).

**Article 6(1)(c) GDPR** — processing necessary for compliance with a legal obligation. Applicable for settlement and audit obligations under Council of Ministers decisions governing humanitarian programmes.

**Article 6(1)(b) GDPR** — processing necessary for the performance of a contract or in order to take steps at the request of the data subject, where the entitlement constitutes a contractual or quasi-contractual right.

### 3.2 Biometric processing (Path A enrollment)

Biometric data is a special category under Article 9(1) GDPR. Processing in DTEP-S is based on:

**Article 9(2)(b) GDPR** — processing necessary for the purposes of carrying out the obligations and exercising specific rights of the controller or of the data subject in the field of employment and social security and social protection law, insofar as it is authorised by Union or Member State law providing for appropriate safeguards. Applicable for verification of entitlement delivery under social protection programmes (humanitarian accommodation, social assistance deliveries).

**Article 9(2)(d) GDPR** — processing carried out in the course of its legitimate activities with appropriate safeguards by a foundation, association, or any other not-for-profit body, provided that the processing relates solely to members or to persons who have regular contact with it in connection with its purposes and that the personal data are not disclosed outside that body without the consent of the data subjects. Applicable for CSDT in its capacity as protocol developer and reference implementation operator during sandbox phase.

**Critical constraint:** Biometric enrollment must not be made a condition for accessing entitlement rights. The protocol structurally supports this through mandatory alternative presentation paths (Path B and Path C). An Issuer or Verifier that refuses to serve a Holder who declines biometric enrollment is in violation of this constraint. This is enforced at protocol level — Path B and Path C are always available.

### 3.3 Displaced persons and vulnerable populations

Persons under temporary protection are in a vulnerable position as defined in Recital 75 GDPR. Article 7(4) GDPR applies — consent shall not be freely given if its refusal results in detriment to the data subject. Specifically, consent may not satisfy the "freely given" requirement where:

- The data subject is in a position of dependency relative to the controller
- There is a clear imbalance of power between the data subject and the controller
- Refusal of consent would result in denial of a benefit to which the data subject is entitled

For this reason, DTEP-S does not rely on consent as the legal basis for any processing. The legal bases identified in sections 3.1 and 3.2 apply. Consent is not collected and is not required.

---

## 4. Privacy by Design Mechanisms

DTEP-S embeds the following privacy protections as structural protocol properties — not as implementation options or policy choices.

### 4.1 Biometric data minimisation

Raw biometric data (fingerprint images) is processed only in memory during pipeline execution. It is never written to storage, never transmitted, and never present in any protocol artifact. This is enforced by the TEE execution model — the pipeline executes within the secure enclave and the only output is the one-way transformed template vector.

### 4.2 Template irreversibility

Enrolled templates are one-way transformed vectors. The three-scan aggregation with Tensor RPCA and Fourier-Mellin normalisation produces a representation that captures verification-relevant features without preserving reconstruction-relevant information. Specifically:

- The original biometric measurement cannot be reconstructed from the template
- The template cannot be matched against biometric databases using standard biometric matching algorithms
- A compromised template cannot be used to forge a biometric authentication on a different system

This is a technical guarantee of data minimisation, not a policy commitment.

### 4.3 No central biometric database

The protocol does not define, require, or permit a central biometric database. Templates are stored either within the encrypted credential (under the Holder's control) or in the Verifier's local TEE-protected device registry (scoped to that Verifier only). There is no mechanism in the protocol for template aggregation across Verifiers. This is a technical impossibility enforced by architecture, not a policy constraint.

### 4.4 Pseudonymous identifiers throughout

Real identity is present only in the Issuer's internal registry. All protocol artifacts — credentials, Redemption Events, audit trail entries — reference Holders by pseudonymous subject IDs. Deanonymisation requires access to the Issuer's registry and is outside the protocol's data flows. The pseudonymisation is strong: reversal requires access to the Issuer registry, which is an institutional system with its own access controls.

### 4.5 Selective disclosure compatible

The W3C VC 2.0 credential format used by DTEP-S is compatible with selective disclosure mechanisms (SD-JWT, BBS+ signatures). Issuers may implement selective disclosure to allow Holders to present only the entitlement claim without revealing other credential attributes. This is an optional Issuer capability — the base protocol does not require it but does not preclude it.

### 4.6 Location data minimisation

The delivery location field in Redemption Events is optional. When present, the `verifierPremises` location type is specified as preferred — it records that delivery occurred at the Verifier's registered address without recording the Holder's movement pattern or precise coordinates.

### 4.7 Purpose limitation

Redemption Events are generated solely for the purpose of settlement and audit of entitlement delivery. The protocol does not support secondary use of Redemption Event data for any other purpose. Auditors receiving Redemption Events are bound by the purpose limitation in the settlement agreement.

---

## 5. Risk Analysis

### 5.1 Re-identification risk

**Risk:** A sequence of Redemption Events for the same subject ID constitutes a transaction history that could be used to infer the Holder's location, consumption patterns, or presence at specific times.

**Mitigation:** Subject IDs are pseudonymous — deanonymisation requires Issuer cooperation. Access controls on the audit trail must restrict who can query event sequences by subject ID. The protocol requires that Auditors implement appropriate access controls; it does not specify them (implementation responsibility).

**Residual risk:** Medium. Dependent on Auditor access control implementation.

### 5.2 Template extraction

**Risk:** An attacker with access to a Verifier device could attempt to extract enrolled templates from the local registry.

**Mitigation:** Templates are stored in TEE-protected storage. One-way transformation means extracted templates cannot be used for biometric matching on other systems. Physical device seizure does not yield usable biometric data.

**Residual risk:** Low. Dependent on TEE implementation quality.

### 5.3 Aggregation risk

**Risk:** An Auditor with access to multiple Issuer programmes could correlate subject IDs across programmes to build comprehensive profiles.

**Mitigation:** Subject IDs are Issuer-assigned. Different Issuers assign different subject IDs to the same Holder. Cross-programme correlation requires both Issuers to cooperate. The protocol does not define cross-Issuer subject ID linkage.

**Residual risk:** Low within single-Issuer deployment. Medium in multi-Issuer scenarios.

### 5.4 Coercion of biometric enrollment

**Risk:** A Verifier or Issuer could effectively coerce Holders into biometric enrollment by making Path A the only available option in practice, despite the protocol mandating alternatives.

**Mitigation:** The protocol specification is explicit that enrollment is optional and that alternative paths must remain available. This is enforceable as a contractual obligation on Verifiers by the Issuer. It is also enforceable as a GDPR obligation under the special category processing framework.

**Residual risk:** Procedural. Cannot be eliminated by protocol design alone.

### 5.5 Cross-border data flows

**Risk:** If Auditor infrastructure is located in a different Member State from Verifier operations, Chapter V GDPR transfer requirements apply.

**Mitigation:** Standard Chapter V GDPR mechanisms apply. Within the EU/EEA, no additional transfer instrument is required.

**Residual risk:** Medium for multi-Member-State deployment. Requires case-by-case transfer analysis.

---

## 6. Data Subject Rights

DTEP-S is designed to be compatible with the exercise of data subject rights under GDPR Chapter III.

**Right of access (Art. 15):** The Issuer holds the mapping between real identity and subject ID. Data subject access requests are directed to the Issuer. The Verifier holds Redemption Events referenced by subject ID only — the Verifier cannot identify the data subject without Issuer cooperation. The Issuer must implement a subject access mechanism mapping credential subject ID to all associated Redemption Events via the Auditor's index. This is outside DTEP-S protocol scope but required for GDPR compliance of the overall system.

**Right to erasure (Art. 17):** Biometric templates can be deleted from Verifier local registry on request. The credential can be revoked by the Issuer. The audit trail contains hashes of Redemption Events, not the events themselves — deletion of the underlying Redemption Event renders the corresponding hash unverifiable but does not require modification of the Merkle tree structure. The trail root remains valid for all non-deleted events. For the humanitarian programme context, the right to erasure is restricted under Article 17(3)(b) — processing necessary for the performance of a task carried out in the public interest — and Article 17(3)(e) — processing necessary for the establishment, exercise or defence of legal claims (audit and recovery proceedings). The tension between erasure and audit integrity must be addressed in national implementation law for each deployment context.

**Right to data portability (Art. 20):** Not applicable for processing under Article 6(1)(e). The credential is a portable W3C VC document held by or on behalf of the Holder and can be presented to any DTEP-S compliant Verifier. Portability applies to any consent-based processing where implemented at Member State level.

**Right to object (Art. 21):** Where processing is based on Article 6(1)(e), data subjects have the right to object. In the humanitarian programme context, objection to delivery verification processing effectively constitutes withdrawal from the programme. This must be clearly communicated at enrollment. The Issuer must assess each objection on its merits.

---

## 7. Data Protection Impact Assessment

A full DPIA is required before operational deployment of DTEP-S in any humanitarian or social protection programme, pursuant to Article 35 GDPR:

- Processing of special category data (biometric) on a large scale — Art. 35(3)(b)
- Systematic monitoring of data subjects in a public area — Recital 75 and WP29 criteria
- Data concerning vulnerable data subjects at large scale

The DPIA must be conducted by the Issuer institution as data controller. Key anticipated findings:

- **High risk:** Biometric data processing — mitigated by technical measures in Section 4 and non-biometric path availability
- **High risk:** Immutable audit trail in tension with right to erasure — mitigated by pseudonymisation and Art. 17(3) justification in Section 6
- **Medium risk:** Cross-border data flows if Auditor is in a different Member State from Verifier — standard Chapter V GDPR transfers apply

The DPIA must address: the specific biometric pipeline implementation, template storage architecture, access controls on audit trail, retention periods, and data subject rights procedures.

---

## 8. Applicable Law — Bulgarian Context

For the immediate deployment context (Bulgarian humanitarian accommodation programme):

- **GDPR** (Regulation 2016/679) — directly applicable
- **ЗЗЛД** (Закон за защита на личните данни) — Bulgarian implementing law
- **КЗЛД** (Комисия за защита на личните данни) — supervisory authority
- **Council of Ministers decisions** governing the humanitarian programme — legal basis for Article 6(1)(c) and Article 9(2)(b) processing

The Issuer (Agency for Social Assistance) is required to consult КЗЛД prior to operational deployment pursuant to Article 36 GDPR (prior consultation where DPIA indicates high residual risk).

---

## 9. Open Issues

- [ ] Consent mechanism specification for biometric enrollment (v0.2)
- [ ] Erasure procedure for Redemption Events (v0.3)
- [ ] Cross-border transfer analysis for multi-Member-State deployment (v0.3)
- [ ] DPIA template for Issuer institutions (v0.9)

---

## References

- GDPR (Regulation (EU) 2016/679): https://eur-lex.europa.eu/eli/reg/2016/679/oj
- EDPB Guidelines on Data Protection by Design and by Default: https://edpb.europa.eu/sites/default/files/files/file1/edpb_guidelines_201904_dataprotection_by_design_and_by_default_v2.0_en.pdf
- EDPB Guidelines on Biometric Data: https://edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-032019-processing-biometric-data_en
- DTEP-S Protocol Overview: `../spec/protocol-overview.md`
- DTEP-S Presentation Flows: `../spec/presentation-flows.md`
- DTEP-S Threat Model: `./threat-model.md`
