# DTEP-S Threat Model

**Version:** 0.1-draft  
**Status:** Specification in progress  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document defines the threat model for DTEP-S. It identifies assets, trust boundaries, threat actors, attack vectors, and the protocol's mitigations and residual risks.

The threat model covers the four-element evidence chain: Right → Identification → Act of Delivery → Payment.

The threat model covers the protocol specification. Implementation-specific threats (e.g. specific TEE vulnerabilities, network infrastructure attacks) are out of scope but are referenced where relevant.

---

## 2. Assets

| Asset | Description | Criticality |
|---|---|---|
| Entitlement credential | W3C VC encoding Holder's right | HIGH — forgery enables fraudulent redemption |
| Biometric template | One-way transformed enrollment vector | HIGH — compromise enables impersonation |
| Redemption Event | Signed delivery proof | HIGH — forgery enables fraudulent settlement |
| Audit trail | Merkle-chained event log | HIGH — tampering invalidates audit |
| Issuer signing key | Ed25519 key pair | CRITICAL — compromise enables unlimited credential forgery |
| Verifier device key | Ed25519 key pair in TEE | HIGH — compromise enables event forgery |
| Holder subject ID mapping | Issuer registry linking pseudonym to real identity | HIGH — breach enables deanonymisation |

---

## 3. Trust Boundaries

```
TRUST BOUNDARY 1: Issuer internal systems
  Inside: Holder real identity, subject ID mapping,
          entitlement registry, signing key
  Outside: Everything else

TRUST BOUNDARY 2: Verifier TEE
  Inside: Biometric match computation, signing key,
          signing operation
  Outside: Merchant application, network, storage

TRUST BOUNDARY 3: Auditor systems
  Inside: Event log, audit trail, settlement logic
  Outside: Verifier submissions, public trail roots

TRUST BOUNDARY 4: Credential
  Inside: Entitlement claim, subject ID,
          optional biometric binding
  Outside: Transport layer, presentation channel
```

**Key trust anchor:** The Verifier device TEE. The protocol is designed so that the security model degrades gracefully if the application layer of the Verifier device is compromised, as long as the TEE is not.

---

## 4. Threat Actors

**TA1 — Fraudulent Holder:** A person attempting to redeem an entitlement they do not hold, or to redeem beyond their entitlement limits.

**TA2 — Fraudulent Verifier:** An accredited provider attempting to claim payment for deliveries not made, or deliveries made to ineligible persons.

**TA3 — Colluding Holder and Verifier:** A Holder and Verifier cooperating to generate fraudulent Redemption Events.

**TA4 — Compromised Verifier Device:** An attacker with physical or remote access to a Verifier device attempting to extract keys or forge events.

**TA5 — Compromised Auditor:** An Auditor attempting to suppress, modify, or fabricate audit trail entries.

**TA6 — Passive Adversary:** An attacker observing protocol traffic attempting to deanonymise Holders or infer entitlement patterns.

**TA7 — Credential Forger:** An attacker attempting to create or modify credentials without Issuer signing key.

**TA8 — Issuer Insider:** An employee of the Issuer institution attempting to create fraudulent credentials for non-existent beneficiaries or modify entitlement conditions in the registry.

---

## 5. Attack Vectors and Mitigations

### 5.1 Credential forgery (TA7)

**Attack:** Attacker creates a credential for an ineligible Holder, or modifies an existing credential to extend its validity or entitlement parameters.

**Mitigation:** Credentials are signed with Issuer Ed25519 key. Verifier validates Issuer signature before any redemption. Forgery without the Issuer private key is computationally infeasible under current cryptographic assumptions.

**Residual risk:** Negligible — conditional on Issuer key security.

**Dependency:** Issuer key management practices. Issuer key compromise (outside protocol scope) invalidates this mitigation.

---

### 5.2 Biometric impersonation (TA1)

**Attack:** Attacker presents a fraudulent biometric to match an enrolled template and obtain a signed Redemption Event.

**Mitigation:** The biometric pipeline (Tensor RPCA → Fourier-Mellin → Neural extractor → cosine similarity in TEE) is designed to resist presentation attacks through multi-sample capture and noise separation. The TEE executes the match — the merchant application cannot inject a pre-computed result.

**Residual risk:** Low. Dependent on biometric pipeline implementation quality and similarity threshold calibration. Presentation attack detection (PAD) is not specified in v0.1 and should be addressed in v0.2.

---

### 5.3 Redemption Event forgery (TA2, TA4)

**Attack:** A Verifier generates a signed Redemption Event without performing actual Holder verification or delivery.

**Mitigation:** Signing capability is held exclusively in the TEE. The TEE releases signing only after successful Holder verification within the secure enclave. The merchant application cannot access the signing key directly. On devices without StrongBox, the assurance level is declared as MEDIUM or LOW in the Redemption Event; Auditors may apply differential scrutiny based on assurance level.

**Residual risk:** Low — conditional on TEE integrity. TEE bypass attacks (physical side-channel, firmware exploit) are outside protocol scope but represent a residual hardware-level risk.

---

### 5.4 Credential substitution after verification (TA4)

**Attack:** A compromised Verifier application verifies one credential biometrically, then substitutes a different credential before signing the Redemption Event.

**Mitigation:** The TEE receives the credential identifier as input to the signing operation atomically with the biometric verification result. The credential identifier is bound into the signed Redemption Event inside the TEE. Substitution after TEE input is not possible without TEE compromise.

**Residual risk:** Same as 5.3 — devices without full TEE support reduce atomicity guarantees. Declared in assurance level.

---

### 5.5 Collusion between Holder and Verifier (TA3)

**Attack:** A Holder and Verifier cooperate — the Holder presents their biometric, receives a Redemption Event, but no actual delivery takes place. The Verifier claims settlement from the Auditor.

**Mitigation:** The protocol cannot prevent collusion cryptographically — a genuine biometric match with a genuine credential produces a valid event regardless of whether delivery occurred. Mitigation is statistical: anomaly indicators A1–A7 in the Redemption Event specification enable Auditor-level detection. High event frequency, unusual timing patterns, volume anomalies, and same Holder at multiple geographically distant Verifiers on the same day are detectable.

**Residual risk:** Medium. Collusion that falls within statistical detection thresholds is not detectable by the protocol alone. This is a known limitation. The protocol nonetheless provides a forensic audit trail that does not exist in current administrative practice, making post-hoc detection possible.

---

### 5.6 Replay attack (TA1, TA2)

**Attack:** An attacker captures a valid signed Redemption Event and submits it multiple times to the Auditor to claim multiple settlement payments.

**Mitigation:** Each Redemption Event carries a unique UUID. The Auditor maintains a seen-IDs log and rejects duplicate submissions. Duplicate detection is a mandatory Auditor function. In offline scenarios with multiple Verifiers for the same credential, duplicate events may be generated before the Auditor reconciles — detected and rejected at settlement.

**Residual risk:** Negligible — conditional on Auditor duplicate detection implementation. Acceptable given the humanitarian context where false rejection is more harmful than duplicate detection.

---

### 5.7 Audit trail tampering (TA5)

**Attack:** The Auditor deletes, modifies, or inserts Redemption Events in the audit log to suppress evidence of fraud or to fabricate deliveries.

**Mitigation:** The Merkle chain structure makes any modification to a committed event detectable — the chain of hashes from the modified leaf to the trail root is invalidated. Trail roots are published periodically and optionally anchored to external registries (OpenTimestamps, Issuer countersignature). A published trail root cannot be altered without breaking the cryptographic proof.

**Residual risk:** Low — conditional on trail root publication and anchoring. An Auditor who has not yet published a trail root for a batch retains the ability to suppress events in that batch. Publication frequency is the key control.

---

### 5.8 QR card theft and PIN extraction (TA1)

**Attack:** An attacker steals a Holder's QR card and attempts to determine the PIN through brute force or social engineering.

**Mitigation:** PIN validation locks the credential after 3 failed attempts (Path B specification). A 4-digit PIN space of 10,000 combinations with a 3-attempt lockout makes brute force impractical per interaction. Lost card reporting triggers credential revocation by the Issuer.

**Residual risk:** Low for brute force. Medium for social engineering — PIN disclosure by a vulnerable Holder to a malicious actor is a procedural risk outside the protocol's scope.

---

### 5.9 Biometric template theft (TA4)

**Attack:** An attacker extracts enrolled biometric templates from the Verifier device or credential, reconstructing raw biometric data.

**Mitigation:** Enrolled templates are stored as one-way transformed feature vectors within TEE-protected storage. The transformation is not reversible — raw biometric data cannot be reconstructed from the stored vector. No central biometric database exists. Compromise of a template does not yield usable biometric data for matching on other systems.

**Residual risk:** Low. Dependent on TEE implementation quality and the cryptographic properties of the chosen feature extraction architecture.

---

### 5.10 Deanonymisation (TA6)

**Attack:** A passive adversary observing Redemption Events attempts to link subject IDs to real identities, or to correlate event sequences to infer Holder location and behaviour patterns.

**Mitigation:** Subject IDs are Issuer-assigned pseudonyms. Deanonymisation requires access to the Issuer's internal registry. Protocol artifacts contain no real identity data. Location data in events is optional; `verifierPremises` type is preferred to avoid location tracking.

**Residual risk:** Medium. A sufficiently large sequence of events for the same subject ID at the same Verifier constitutes a behavioural profile. Access controls on the audit trail are the primary mitigation — these are implementation responsibilities.

---

### 5.11 Offline credential staleness (TA1)

**Attack:** A Holder whose credential has been revoked presents at a Verifier operating in offline mode. The Verifier's cached credential copy does not reflect the revocation. The Verifier generates a Redemption Event for a revoked credential.

**Mitigation:** Cache TTL (default 24 hours) limits the staleness window. Events generated via offline lookup are tagged with `offlineLookup: true` and flagged for additional Auditor review.

**Residual risk:** Low-Medium. A revocation that occurs during an offline window will not be detected until the Verifier reconnects. This is a known trade-off between offline availability and revocation immediacy.

---

### 5.12 Issuer insider fraud (TA8)

**Attack:** An employee of the Issuer institution creates fraudulent credentials for non-existent beneficiaries or modifies entitlement conditions in the registry.

**Mitigation:** DTEP-S does not specify Issuer internal controls — these are within the Issuer's own security perimeter. The protocol provides an immutable audit trail that makes fraudulent credential use detectable at Auditor level: credentials not present in the Issuer's registry at settlement time will fail reconciliation. Cross-referencing with beneficiary case files is a settlement-layer control.

**Residual risk:** Medium at issuance — outside the protocol's direct threat surface. Detectable at settlement.

---

## 6. Security Properties Summary

| Property | Mechanism | Strength |
|---|---|---|
| Credential authenticity | Issuer Ed25519 signature | Cryptographic |
| Holder identity binding | Biometric TEE match / QR+PIN / Documentary | HIGH / MEDIUM / LOW |
| Redemption Event integrity | Verifier device Ed25519 signature | Cryptographic |
| Verification-signing atomicity | TEE binding | Hardware (StrongBox) / Declared (fallback) |
| Replay prevention | UUID deduplication at Auditor | Protocol |
| Biometric privacy | One-way feature vector; no central DB | Technical impossibility |
| Communication confidentiality | TLS 1.3 | Standard |
| Collusion detection | Statistical anomaly at Auditor | Probabilistic |
| Audit trail integrity | Merkle chain + trail root publication | Cryptographic |

---

## 7. Out of Scope Threats

The following threats are explicitly out of scope for the protocol specification. They must be addressed at implementation or operational level:

- **Issuer key compromise** — Issuer private key management is outside the protocol. Key compromise invalidates all issued credentials.
- **TEE firmware exploits** — Hardware-level TEE attacks (Spectre-class, physical side-channel) are outside the protocol scope.
- **Social engineering of Holders** — Convincing a Holder to share their PIN or present their biometric under false pretences is an operational risk.
- **Network-level attacks** — TLS attacks, DNS hijacking affecting the central registry API or Auditor endpoint are infrastructure concerns.
- **Issuer registry breach** — Breach of the Issuer's internal registry linking subject IDs to real identities is an Issuer operational security concern.
- **Physical security of delivery point** — Outside protocol scope.
- **Nation-state level TEE attacks** — Outside protocol scope.

---

## 8. Security Invariants

See [SECURITY.md](../SECURITY.md) for the five security invariants (S1–S5) that are non-negotiable in any specification change or implementation.

---

## 9. Open Issues

- [ ] Presentation attack detection (PAD) specification for biometric pipeline (v0.2)
- [ ] Formal threat analysis for QR card physical theft scenario — expanded (v0.2)
- [ ] TEE attestation verification procedure at Auditor (v0.2)
- [ ] Anomaly detection threshold definition (v0.3)
- [ ] Security audit scope based on this threat model (v0.9)

---

## References

- DTEP-S Security Policy: `../SECURITY.md`
- DTEP-S GDPR Analysis: `./gdpr-analysis.md`
- DTEP-S Redemption Event Specification: `../spec/redemption-event.md` (anomaly indicators A1–A7)
- STRIDE threat modelling methodology: https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
- Android StrongBox security: https://source.android.com/docs/security/features/keystore
- Apple Secure Enclave security: https://support.apple.com/guide/security/secure-enclave-sec59b0b31ff/web
