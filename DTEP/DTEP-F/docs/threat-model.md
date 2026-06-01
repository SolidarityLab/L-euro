# DTEP-F Threat Model

**Version:** 0.1-draft
**Status:** Specification in progress
**Date:** 2026-06-01
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document defines the threat model for DTEP-F. It identifies trust boundaries, adversarial actors, attack surfaces, and protocol mitigations for each identified threat.

The threat model covers the full protocol chain: Peppol Corner 4 → Corner 5 Middleware → Taler Exchange → DRRDB → Central VIES → Analytical Layer.

---

## 2. Trust Boundaries

```
Peppol Corner 4 (trusted — accredited Access Point)
        │
        │  EN 16931 XML signed per AS4
        ▼
Corner 5 Middleware (partially trusted — no signing keys)
        │
        │  raw invoice data
        ▼
Taler Exchange (trusted — sole signing authority)
        │
        ├─ Artifact A (Exchange custody — protected)
        │
        │  signed public DTEP JSON
        ▼
DRRDB (partially trusted — append-only, auditor-verified)
        │
        │  public M0–M5 feed
        ▼
Central VIES (trusted — EC infrastructure)
Analytical Layer (trusted — operates on public data only)
```

Key trust anchor: Taler Exchange. The protocol is designed so that the security model is maintained even if Corner 5 Middleware is fully compromised, as long as Exchange is not.

---

## 3. Adversarial Actors

### 3.1 Fraudulent Verifier (VAT fraud actor)

A business entity attempting to generate DRR records for transactions that did not occur, or to manipulate transaction attributes to reduce VAT liability or claim fraudulent refunds.

### 3.2 Compromised Corner 5 Middleware

An attacker who has gained control of the Corner 5 Middleware application layer, attempting to forge DRR records, suppress legitimate records, or exfiltrate subject data before DD-18 scrubbing.

### 3.3 Passive Attacker

An attacker intercepting communications between protocol components, attempting to read subject data or correlate public DRRDB records with real entities.

### 3.4 Insider — Tax Administration

A tax administration employee attempting to access DRRDB protected level data beyond their authorised Audit Request scope.

### 3.5 Carousel Fraud Consortium

A coordinated group of entities constructing a closed transaction cycle to generate fraudulent VAT refund claims.

### 3.6 Oracle Manipulator

An actor with influence over the reference price oracle R(c,t), attempting to suppress legitimate anomaly signals by manipulating the reference price.

---

## 4. Threat Analysis

### T1 — DRR record forgery

**Threat:** Fraudulent Verifier submits a forged EN 16931 invoice to generate a DRR record for a transaction that did not occur.

**Attack surface:** Corner 5 Middleware input; Exchange signing.

**Mitigation:** Exchange signs only objects that originate from Corner 4 via authenticated AS4 transport. A forged submission without valid Corner 4 AS4 authentication will not receive an Exchange signature. Corner 4 accreditation is controlled by the national Peppol Authority.

**Residual risk:** Collusion between a fraudulent entity and an accredited Corner 4 Access Point. Detected at Audit Request level through Artifact A cross-reference with the Issuer's VAT registry.

---

### T2 — DRR record suppression

**Threat:** Compromised Corner 5 Middleware suppresses legitimate invoices — prevents them from reaching Exchange, reducing the entity's reported transaction volume.

**Attack surface:** Corner 5 Middleware processing pipeline.

**Mitigation:** Peppol AS4 transport provides delivery confirmation to Corner 4. Suppressed invoices are detectable as delivery confirmations without corresponding DRR records. The Taler auditor protocol continuously verifies completeness of the Exchange-DRRDB relationship — a missing record is deterministically detectable.

**Residual risk:** Short-term suppression window before auditor detection. Acceptable given the periodic auditor verification cycle.

---

### T3 — Subject data exfiltration before scrubbing

**Threat:** Compromised Corner 5 Middleware reads EN 16931 XML before DD-18 scrubbing, exfiltrating subject identifiers.

**Attack surface:** Corner 5 Middleware memory; network interfaces before Exchange submission.

**Mitigation:** Corner 5 Middleware is a zero-retention component — EN 16931 XML is transmitted to Exchange immediately on receipt without local storage. Exfiltration requires active memory access during the transit window. Standard OS-level memory protection applies.

**Residual risk:** Memory scraping during the transit window. Addressed by deploying Corner 5 Middleware in a hardened environment (TEE or equivalent) in high-security deployments. Defined as an open issue for v0.2.

---

### T4 — Public DRRDB de-anonymisation

**Threat:** Passive Attacker correlates public M0–M5 records with known transaction data to identify business entities.

**Attack surface:** DRRDB public level query API.

**Mitigation:** M0 coin commitment is non-deterministic — knowledge of the invoice identifier does not predict M0. Subject identifiers are structurally absent from M1–M5. The temporal ontology makes the combination M1+M2+M3+M4+M5 statistically indistinct for common transaction types.

**Residual risk:** Rare transactions where the M1+M2+M3+M4+M5 combination is unique. Addressed by k-anonymity publication threshold (open issue, gdpr-analysis.md Section 8).

---

### T5 — Audit Request scope overreach

**Threat:** Tax administration insider submits Audit Requests beyond authorised scope, using DTEP-F as a bulk surveillance tool.

**Attack surface:** Audit Request authorisation mechanism; Exchange salt disclosure API.

**Mitigation:** Exchange discloses the salt only for the specific M0 element named in the Audit Request. Bulk salt disclosure is not supported by the Exchange API. All Audit Requests are logged with institutional credentials and audit trail.

**Residual risk:** Coordinated insider abuse across multiple individual Audit Requests. Addressed by Audit Request rate limiting and anomaly detection on request patterns (open issue for v0.3).

---

### T6 — Carousel fraud evasion

**Threat:** Carousel Fraud Consortium structures transactions to avoid τ(H) cycle detection — for example by introducing time delays between transactions to break the temporal cycle.

**Attack surface:** τ(H) detection logic; time bucket granularity.

**Mitigation:** τ(H) detects cycles regardless of the time between transactions — a cycle t_A < t_B < t_C < t_A is impossible regardless of the magnitude of the intervals. Time delays do not evade detection; they only delay the cycle completion.

**Residual risk:** Consortium splits the cycle across multiple legal entities to avoid cycle closure. Detectable at Audit Request level through Artifact A cross-reference. Combined with S_price and S_macro signals, split-cycle structures generate anomaly signals even without τ(H) closure.

---

### T7 — Oracle manipulation

**Threat:** Oracle Manipulator influences R(c,t) reference prices to suppress δ(e) price anomaly signals for fraudulent transactions.

**Attack surface:** R(c,t) oracle configuration and update mechanism.

**Mitigation:** R(c,t) is derived from independent public sources (Eurostat HICP, TED, ECB). Oracle updates require institutional authorisation and are logged with full audit trail. Manipulation of a single CPV category price does not affect τ(H) or L(t) signals.

**Residual risk:** Coordinated manipulation of multiple CPV categories across multiple public sources simultaneously. Practically infeasible. Oracle governance specification is an open issue for v0.2.

---

### T8 — Exchange key compromise

**Threat:** Taler Exchange signing key is compromised, allowing an attacker to forge valid DRR record signatures.

**Attack surface:** Exchange master key storage; signing key rotation mechanism.

**Mitigation:** Exchange master key is held in HSM storage. Signing key rotation is periodic per Taler Exchange protocol. Key compromise triggers revocation; affected DRR records enter a disputed evidentiary status (signing-layer.md Open Issues).

**Residual risk:** HSM compromise. Outside the DTEP-F threat surface — addressed by standard HSM security practices.

---

## 5. Security Properties Summary

| Property | Mechanism | Strength |
|---|---|---|
| DRR record authenticity | Taler Exchange Ed25519 signature | Cryptographic |
| Record completeness | Taler auditor protocol invariant | Mathematical |
| Subject unlinkability in public layer | Temporal ontology + DD-18 scrubbing | Structural impossibility |
| M0 unlinkability | Taler coin commitment (non-deterministic) | Cryptographic |
| Replay prevention | UUID deduplication at DRRDB | Protocol |
| Selective audit | Per-M0 salt disclosure by Exchange | Cryptographic |
| Carousel fraud detection | τ(H) acyclicity — temporal irreversibility | Deterministic |
| Price anomaly detection | δ(e) against R(c,t) oracle | Probabilistic |
| Macroeconomic anomaly | L(t) Leontief deviation | Probabilistic |

---

## 6. Out of Scope

The following are explicitly outside the DTEP-F threat model:

- Peppol Corner 1–4 security (AS4 transport security, Access Point accreditation)
- Taler Exchange internal security beyond key management interface
- Central VIES infrastructure security
- Physical security of Corner 5 Middleware deployment
- Nation-state level cryptographic attacks
- Social engineering of tax administration staff

---

## 7. Open Issues

- [ ] Corner 5 Middleware TEE deployment specification for high-security contexts (v0.2)
- [ ] Oracle governance and manipulation detection (v0.2)
- [ ] Audit Request rate limiting and anomaly detection (v0.3)
- [ ] Revocation handling for compromised Exchange signing keys (v0.2 — signing-layer.md)
- [ ] Split-cycle carousel fraud detection across multiple legal entities (v0.3)
