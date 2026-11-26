# DTEP-S Settlement Integration Notes

**Version:** 0.1-draft  
**Status:** Exploratory — not part of core protocol  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document explores integration options for the settlement layer of DTEP-S — the mechanism by which Auditors initiate payments to Verifiers after verified delivery evidence is produced.

Settlement is explicitly outside the DTEP-S core protocol scope. The protocol produces signed Redemption Events and Audit Reports. What happens after the Audit Report is implementation-defined. This document analyses options.

---

## 2. Current State

In the immediate deployment context (Bulgaria humanitarian programmes), settlement follows existing administrative procedures:

1. Verifier submits reimbursement claim to Ministry of Tourism
2. Ministry of Tourism cross-references claim with programme registry
3. Payment initiated via standard government payment infrastructure
4. Disputes resolved through administrative appeal procedures

DTEP-S Audit Reports replace steps 1–2 with cryptographically verifiable evidence. Steps 3–4 remain unchanged in the current deployment model.

---

## 3. GNU Taler — Candidate Integration

GNU Taler is a privacy-preserving payment protocol developed within the NGI ecosystem, with active EU pilot deployment (NGI Taler Pilot, 2023–2026).

### Relevant properties

- Buyer anonymity with seller accountability — aligned with DTEP-S pseudonymous Holder design
- Built-in Auditor component for financial consistency verification
- Open protocol, AGPL licensed, NGI-funded — aligned with DTEP-S commons philosophy
- EU pilot deployment underway — institutional familiarity within NGI ecosystem

### Integration point

The DTEP-S Audit Report is the natural input to a Taler-based settlement flow:

```
DTEP-S Audit Report
(signed by Auditor, covers period X)
        ↓
Taler Exchange
(Auditor holds institutional funds as Taler reserve)
        ↓
Taler coin transfer to Verifier merchant wallet
(amount = verified deliveries × unit rate)
        ↓
Verifier redeems coins
(Taler Exchange records withdrawal — auditable)
```

### Open questions

- GDPR implications of combining DTEP-S delivery evidence (pseudonymous) with Taler payment records (financial)
- Taler merchant integration requirements for Verifier onboarding
- Exchange operator role — who operates the Taler Exchange in institutional deployment?
- Cross-border settlement for multi-Member-State deployments

**Status:** Deferred to v0.4. Requires dedicated analysis and consultation with GNU Taler team.

---

## 4. Traditional Payment Rail Integration

For deployments where Taler adoption is not feasible, DTEP-S Audit Reports can integrate with standard payment infrastructure:

### SEPA Credit Transfer

Audit Report → Auditor generates SEPA CT batch file → bank payment to Verifier IBANs. Suitable for EU institutional deployment. Adds 1–3 business days settlement latency.

### Government payment systems

For national government deployments, Audit Reports can integrate with existing government payment infrastructure (e.g. Bulgaria's СЕБРА system) via standard data exchange formats. Requires mapping between DTEP-S Verifier accreditation IDs and government supplier registry entries.

---

## 5. Recommendation

For v0.1 deployment (Bulgaria humanitarian programme):

**Use existing МТ payment procedures**, augmented by DTEP-S Audit Reports as the evidentiary input. This minimises integration complexity and builds institutional trust in the protocol before introducing additional technology dependencies.

For v1.0 and beyond:

**Evaluate GNU Taler integration** as the preferred settlement layer for new deployments, particularly for cross-border social protection scenarios where a neutral payment infrastructure is preferable to national government payment systems.

---

## References

- GNU Taler: https://taler.net
- NGI Taler Pilot: https://taler.net/en/news/2023-06.html
- DTEP-S Audit Trail Specification: ../spec/audit-trail.md
- DTEP-S Deployment Guide: ./deployment-guide.md
