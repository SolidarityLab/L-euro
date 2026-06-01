# DTEP-F ViDA Positioning

**Version:** 0.1-draft
**Status:** Specification in progress
**Date:** 2026-06-01
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document positions DTEP-F within the ViDA regulatory framework, the Peppol 5-corner architecture, and the current state of Central VIES development. The goal is to show precisely at which level DTEP-F intervenes and what remains outside its scope.

DTEP-F does not compete with ViDA or Peppol. It implements the internal protocol of Corner 5 in accordance with ViDA requirements.

---

## 2. ViDA Regulatory Framework

The ViDA package (Directive 2025/516, adopted 11 March 2025) introduces three principal changes:

**Electronic invoicing** — mandatory structured electronic invoicing for intra-Community B2B transactions from 1 July 2030. EN 16931 is the reference semantic model.

**Digital Reporting Requirements (DRR)** — mandatory real-time reporting of transaction data to Member State tax administrations. The Peppol 5-corner model is the reference transport architecture.

**Single VAT registration platform** — simplification of VAT registration for cross-border supplies.

DTEP-F addresses DRR — the second of the three changes. Electronic invoicing (Peppol Corner 1–4) and single registration are outside DTEP-F scope.

---

## 3. Peppol 5-Corner Model and Corner 5

Peppol defines the transport architecture to Corner 5:

```
Corner 1 — Seller
Corner 2 — Seller Access Point
Corner 3 — Buyer Access Point
Corner 4 — Buyer
Corner 5 — Tax Administration
```

Corner 5 receives a copy of invoice data in real time for monitoring and audit. The Peppol ViDA Pilot (launched December 2024) tests the transport architecture to Corner 5 with over 100 participants and 20 tax administrations.

**What Peppol does not define:** the internal protocol of Corner 5 — how data is stored, analysed, and proven once it arrives. This is the structurally vacant field that DTEP-F fills.

---

## 4. DTEP-F Positioning

```
Peppol Corner 1–4    ← standard Peppol infrastructure (unchanged)
        │
        ▼
Peppol Corner 5      ← entry point
        │
        ▼
DTEP-F               ← internal protocol of Corner 5
  Layer 3: Taler DD-18 transformation
  Layer 4: Taler Exchange signing
  Layer 5: DRRDB on Taler auditor protocol
  Layer 6: four analytical primitives
        │
        ▼
Central VIES         ← output to EC infrastructure
```

DTEP-F replaces neither Peppol nor ViDA. It implements the internal protocol of Corner 5 in accordance with ViDA DRR requirements, receiving input from standard Peppol infrastructure and producing output compatible with Central VIES.

---

## 5. Central VIES and the VIES Adapter

The European Commission is developing Central VIES as a centralised platform for cross-border VAT data. The current VIES API supports VAT number validation. A ViDA-aligned DRR API is under development.

DTEP-F proposes a VIES Adapter as a reference configuration for compatibility:

- Current compatibility with the VIES VAT validation API
- Extension points for future ViDA DRR API versions
- Versioned independently of the DRRDB core

```
DRRDB public level
        │
        ▼
VIES Adapter (versioned)
  ├─ Current: VIES VAT validation API format
  └─ Extension: ViDA DRR real-time reporting format
        │
        ▼
Central VIES
```

This positions DTEP-F as a reference implementation that national tax systems can adopt incrementally — current VIES API compatibility from day one, ViDA DRR compliance as the standard evolves.

---

## 6. National Context — Bulgaria

Bulgaria has a national Peppol Authority (NRA / НАП). The NRA is the natural institutional partner for DTEP-F sandbox deployment in Period 3 of the project.

Current state: the NRA operates a national e-invoice system (e-Invoice.bg) based on Peppol BIS Billing 3.0. A Corner 5 component has not been implemented. DTEP-F offers a reference implementation of Corner 5 compatible with the e-Invoice.bg infrastructure.

Standardisation trajectory: CSDT is a member of BIS and participates in TC84. The DTEP-F draft specification has been submitted to TC84. The standardisation contribution at project completion will be accompanied by a functioning national sandbox deployment.

---

## 7. ViDA DRR Requirements Compliance

| ViDA DRR requirement | DTEP-F implementation |
|---|---|
| Real-time reporting | Layer 5 DRRDB — real-time ingestion from Corner 5 |
| Structured data | EN 16931 → M0–M5 ontological sets |
| Security and integrity | Ed25519 signature by Taler Exchange |
| Privacy | DD-18 scrubbing — subject identifiers excluded from public layer |
| Auditability | Taler auditor protocol — mathematically provable completeness |
| Cross-border | VIES Adapter — compatibility with Central VIES |
| Fraud detection | Four analytical primitives including deterministic carousel fraud signal |

---

## 8. Relation to Existing National DRR Implementations

Member States have implemented DRR under various national models predating ViDA:

| Member State | System | Relation to DTEP-F |
|---|---|---|
| Italy | SdI (Sistema di Interscambio) | Centralised clearance model — DTEP-F is decentralised corner model |
| France | Chorus Pro | Public procurement focus — DTEP-F is general B2B |
| Spain | SII (Suministro Inmediato de Información) | Real-time VAT ledger — compatible input format |
| Bulgaria | e-Invoice.bg (Peppol) | No Corner 5 — DTEP-F fills the gap directly |

DTEP-F is designed as a technology-neutral Corner 5 protocol. Compatibility with national models requires specific adapters, not changes to the core. The reference implementation targets the Bulgarian national context as entry point; the protocol is replicable across Member States.

---

## 9. Open Issues

**Central VIES API finalisation**
The ViDA DRR API specification for Central VIES is under active development by EC DG TAXUD. The DTEP-F VIES Adapter tracks API evolution through a versioned abstraction layer. Specific API parameters will be specified upon finalisation of Central VIES documentation.

**Jurisdictional ownership of Corner 5**
For a cross-border transaction, which national tax administration receives the DRR record — the seller's or the buyer's? ViDA defines the obligation but does not define the jurisdictional model under conflict. DTEP-F monitors Peppol ViDA Pilot developments on this question.

**Compatibility with national DRR implementations**
Member States operate DRR under different national models. DTEP-F is designed as a technology-neutral Corner 5 protocol — compatibility with national models requires specific adapters without changes to the core. The adapter specification is an open issue for v0.3.

**ViDA implementation timeline and transitional arrangements**
ViDA DRR becomes mandatory from 1 July 2030. Transitional arrangements for Member States with existing national systems are under negotiation. DTEP-F sandbox deployment targets the 2026–2029 window as a voluntary early adoption reference implementation.

---

## References

- ViDA Directive 2025/516: https://eur-lex.europa.eu/eli/dir/2025/516
- Peppol ViDA Pilot: https://peppol.org/peppol-vida-pilot/
- Central VIES: https://ec.europa.eu/taxation_customs/vies/
- EN 16931-1:2025: https://www.cen.eu/work/areas/ict/ebusiness/pages/ws-einvoicing.aspx
- EC DG TAXUD: https://taxation-customs.ec.europa.eu/
- Bulgarian NRA e-Invoice: https://www.nap.bg/
