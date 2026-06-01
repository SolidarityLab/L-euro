# DTEP-S Threat Model

**Version:** 0.1-draft  
**Status:** Specification in progress  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document defines the threat model for the DTEP-S protocol. It identifies
the trust boundaries, adversarial actors, attack surfaces, and the protocol's
mitigations for each identified threat.

The threat model covers the four-element evidence chain:
Right → Identification → Act of Delivery → Payment

---

## 2. Trust Boundaries

```
ISSUER (trusted — institutional key)
    │
    │  W3C VC signed with Issuer key
    ▼
HOLDER (untrusted — identity verified at presentation)
    │
    │  presentation at delivery point
    ▼
VERIFIER DEVICE (partially trusted — TEE is trust anchor)
    │
    │  signed Redemption Event
    ▼
AUDITOR (trusted — settlement authority)
```

Key trust anchor: the Verifier device TEE. The protocol is designed so that
the security model degrades gracefully if the application layer of the Verifier
device is compromised, as long as the TEE is not.

---

## 3. Adversarial Actors

### 3.1 Fraudulent Holder

A person attempting to claim an entitlement they do not hold, or to claim the
same entitlement multiple times.

### 3.2 Fraudulent Verifier

An accredited provider attempting to generate Redemption Events for deliveries
that did not occur, or for beneficiaries who did not present.

### 3.3 Compromised Verifier Application

An attacker who has gained control of the Verifier device application layer
(malware, rooted device) attempting to forge Redemption Events.

### 3.4 Passive Attacker

An attacker intercepting communications between Verifier and Auditor attempting
to read beneficiary data or replay captured events.

### 3.5 Insider — Issuer

An employee of the Issuer institution attempting to issue fraudulent credentials
or modify the entitlement registry.

### 3.6 Collusion — Holder and Verifier

A Holder and Verifier acting together to generate Redemption Events for
deliveries that did not occur.

---

## 4. Threat Analysis

### T1 — Credential forgery

**Threat:** Fraudulent Holder presents a forged or modified credential.

**Attack surface:** Credential content; Issuer signature.

**Mitigation:** All credentials are W3C VC 2.0 signed with the Issuer's
institutional key. Verifier application verifies Issuer signature before
proceeding. A forged credential without a valid Issuer signature will fail
verification. Mitigation is cryptographically strong provided the Issuer key
is not compromised.

**Residual risk:** Issuer key compromise. Addressed by standard key management
practices (HSM storage, rotation policy) outside DTEP-S scope.

---

### T2 — Credential replay

**Threat:** A valid credential is presented multiple times to claim the same
entitlement repeatedly.

**Attack surface:** Redemption Event generation; Auditor deduplication.

**Mitigation:** Each Redemption Event carries a unique UUID and timestamp.
Credential schemas define maximum redemption frequency (e.g. one meal per day,
one accommodation night per calendar day). The Auditor validates all incoming
events against the deduplication index before processing settlement. Offline
Verifiers queue events locally; the Auditor applies deduplication on batch
receipt.

**Residual risk:** In offline scenarios with multiple Verifiers for the same
credential, duplicate events may be generated before the Auditor reconciles.
Detected and rejected at settlement; delivery may have occurred. Acceptable
given the humanitarian context where false rejection is more harmful than
duplicate detection.

---

### T3 — Redemption Event forgery without biometric verification

**Threat:** A Fraudulent Verifier or Compromised Verifier Application generates
a signed Redemption Event without performing biometric verification of the
Holder.

**Attack surface:** Verifier application logic; signing key access.

**Mitigation:** The signing key is held in the device TEE (Android StrongBox or
equivalent). The TEE releases the signing key only after a successful biometric
match computed within the TEE. The application layer cannot access the signing
key directly. Forgery requires TEE compromise, which is outside the application
threat model.

**Residual risk:** Devices without StrongBox fall back to software TEE or
application-layer signing. On such devices, the assurance level is declared as
MEDIUM or LOW in the Redemption Event. Auditors may apply differential scrutiny
based on assurance level.

---

### T4 — Credential substitution after verification

**Threat:** A Compromised Verifier Application verifies one credential
biometrically, then substitutes a different credential before signing the
Redemption Event.

**Attack surface:** Data flow between biometric verification and signing within
the Verifier application.

**Mitigation:** The TEE receives the credential identifier as input to the
signing operation atomically with the biometric verification result. The
credential identifier is bound into the signed Redemption Event inside the TEE.
Substitution after TEE input is not possible without TEE compromise.

**Residual risk:** Same as T3 — devices without full TEE support reduce
atomicity guarantees. Declared in assurance level.

---

### T5 — Biometric template theft

**Threat:** An attacker extracts enrolled biometric templates from the Verifier
device or credential, reconstructing raw biometric data.

**Attack surface:** Template storage on Verifier device; credential payload.

**Mitigation:** Enrolled templates are stored as one-way transformed feature
vectors. The transformation is not reversible — raw biometric data cannot be
reconstructed from the stored vector. No central biometric database exists.
Templates are stored locally on the Verifier device within the TEE-protected
storage, or encrypted within the credential payload.

**Residual risk:** Compromise of the one-way transformation algorithm. Addressed
by using published, peer-reviewed neural feature extraction architectures.
Algorithm selection documented in the biometric pipeline specification.

---

### T6 — Communication interception

**Threat:** A Passive Attacker intercepts Redemption Events in transit between
Verifier and Auditor, reading beneficiary data or replaying events.

**Attack surface:** Network communication channel.

**Mitigation:** All Verifier-to-Auditor communication is over TLS 1.3.
Redemption Events are signed end-to-end; tampering is detectable at the Auditor.
Replay is prevented by UUID deduplication (T2). Beneficiary data in transit is
pseudonymised by credential subject ID — real identity is not transmitted.

**Residual risk:** Low. Standard TLS threat model applies.

---

### T7 — Collusion between Holder and Verifier

**Threat:** A Holder and Verifier collude to generate Redemption Events for
deliveries that did not occur (e.g. the Holder presents but does not receive
the goods; the Verifier claims payment).

**Attack surface:** The delivery act itself — outside cryptographic control.

**Mitigation:** Redemption Event metadata (timestamp, geolocation if available,
verifier ID) enables statistical anomaly detection at Auditor level. Unusual
patterns — same Holder at multiple geographically distant Verifiers on the same
day, unusually high redemption rates for a given Verifier — are flagged for
review. The anomaly detection ruleset is defined in the audit trail specification.

**Residual risk:** Collusion that falls within statistical norms is not detectable
by the protocol alone. Residual risk is equivalent to, and not greater than,
existing paper-based systems. The protocol provides a forensic audit trail that
does not exist in current administrative practice.

---

### T8 — Issuer insider fraud

**Threat:** An employee of the Issuer institution creates fraudulent credentials
for non-existent beneficiaries or modifies entitlement conditions.

**Attack surface:** Issuer credential issuance system; entitlement registry.

**Mitigation:** DTEP-S does not specify Issuer internal controls — these are
within the Issuer's own security perimeter. The protocol provides an immutable
audit trail that makes fraudulent credential use detectable at Auditor level:
credentials not present in the Issuer's registry at settlement time will fail
reconciliation. Cross-referencing with beneficiary case files (Issuer's own
records) is a settlement-layer control outside DTEP-S scope.

**Residual risk:** Issuer insider fraud at issuance is outside the protocol's
direct threat surface. Detectable at settlement.

---

## 5. Security Properties Summary

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

---

## 6. Out of Scope

The following are explicitly outside the DTEP-S threat model:

- Issuer internal key management and HSM security
- Auditor internal systems security
- Physical security of the delivery point
- Social engineering of Verifier staff
- Nation-state level TEE attacks

---

## 7. Open Issues

- [ ] Formal threat analysis for QR card physical theft scenario (v0.2)
- [ ] Anomaly detection threshold definition (v0.3)
- [ ] TEE attestation verification procedure at Auditor (v0.2)
- [ ] Security audit scope based on this threat model (v0.9)
