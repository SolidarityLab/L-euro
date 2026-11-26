# DTEP-F Standardisation Roadmap

**Version:** 0.1-draft  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab  
**Note:** This document describes the standardisation roadmap for DTEP-F (Fiscal Layer). It is included here as a cross-reference to illustrate the shared standardisation trajectory of the DTEP protocol family. The DTEP-S (Social Layer) roadmap is at [standardisation-roadmap.md](./standardisation-roadmap.md).

---

## 1. Principle

DTEP-F follows the **open source first, standardisation second** model. The open source implementation is the technical reference. The standard abstracts implementation specifics into technology-neutral requirements. The standard follows the implementation — not the reverse.

---

## 2. Current Status

### BIS/TC84 draft submission

CSDT submitted a draft technical specification to the Bulgarian Institute for Standardisation (BIS), Technical Committee TC84 (Electronic Transactions) in May 2026. The draft establishes the regulatory context, the six-layer architecture, and the four analytical primitives as the basis for a national standardisation contribution.

**Status:** Submitted, under TC84 review.

### NGI TALER open source implementation

The DTEP-F repository constitutes the open source reference implementation submitted to the NGI TALER open call (August 2026). It is the technical evidence base for the standardisation track.

---

## 3. Standardisation Trajectory

```
BIS/TC84 national draft
        │
        │ national approval
        ▼
CEN Workshop Agreement (CWA)
        │
        │ CWA publication
        ▼
CEN/CENELEC Technical Specification (TS)
        │
        │ TS → EN proposal
        ▼
European Standard (EN)
```

**Parallel track — ISO/IEC JTC1:** Upon CEN/CENELEC TS publication, CSDT will explore submission to ISO/IEC JTC1 SC38 (Cloud Computing and Distributed Platforms) for international standardisation. Timeline dependent on EN track progress.

---

## 4. Timeline

| Milestone | Target | Dependency |
|---|---|---|
| BIS/TC84 draft approved | Q4 2026 | NGI TALER project start |
| Open source reference implementation v1.0 | Q2 2027 | NGI TALER project completion |
| National sandbox deployment (НАП pilot) | Q3 2027 | TC84 approval + НАП engagement |
| CEN Workshop Agreement proposal | Q4 2027 | v1.0 implementation + sandbox evidence |
| CEN/CENELEC Technical Specification | Q2 2028 | CWA publication |
| European Standard proposal | Q4 2028 | TS publication |
| ViDA DRR mandatory enforcement | 2030-07-01 | Standard must precede enforcement |

The 2028 target for CEN/CENELEC TS is the critical milestone: national tax administrations need 18–24 months for implementation before ViDA mandatory enforcement on 1 July 2030.

---

## 5. Relation to ViDA Enforcement

ViDA DRR becomes mandatory for all EU Member States on 1 July 2030. For DTEP-F to serve as the reference protocol for Corner 5:

- A recognised European standard must exist before 2030
- National tax administrations must have time to implement (18–24 months)
- Therefore, CEN/CENELEC TS must be published by Q2 2028

This timeline is achievable if the BIS/TC84 track and the open source implementation proceed in parallel as planned.

---

## 6. DG TAXUD Positioning

DTEP-F is positioned as a reference implementation for **Central VIES 2.0** — the EC infrastructure currently under development by DG TAXUD for real-time cross-border VAT data exchange.

CSDT will engage DG TAXUD through the following channels:

- Peppol ViDA Pilot participation (Corner 5 reference implementer)
- CEN/CENELEC standardisation process (national expert contribution)
- NGI TALER project outputs (open source evidence base)

The VIES Adapter defined in the DTEP-F specification is the technical interface toward Central VIES 2.0.

---

## 7. BIS Membership and TC84

CSDT is a member of the Bulgarian Institute for Standardisation and participates in:

- **TC84** — Electronic Transactions (DTEP-F primary committee)
- Banking transactions committee — e-invoicing standards (DTEP-F adjacent)

BIS membership provides direct participation rights in CEN/CENELEC mirror committees, enabling national expert status in the European standardisation process.

This membership also underpins the DTEP-S standardisation track — see [standardisation-roadmap.md](./standardisation-roadmap.md).

---

## 8. DTEP Protocol Family — Shared Standardisation Infrastructure

DTEP-F and DTEP-S share:

- The same institutional channel (BIS TC84 → CEN/CENELEC)
- The same applicant organisation (CSDT)
- The same open-first philosophy
- Complementary but non-overlapping scope:
  - DTEP-F: EN 16931 → ViDA/CTC → real-time VAT monitoring (fiscal domain)
  - DTEP-S: institutional entitlement → device-independent delivery → settlement evidence (social domain)

Joint presentation to CEN/CENELEC as a protocol family is planned for Q4 2027, subject to TC84 approval of both submissions.

---

## 9. Open Issues

- [ ] TC84 review outcome and feedback integration (Q4 2026)
- [ ] CEN Workshop Agreement scope definition (Q3 2027)
- [ ] DG TAXUD formal engagement strategy (Q2 2027)
- [ ] ISO/IEC JTC1 feasibility assessment (Q4 2028)
- [ ] Joint DTEP-F + DTEP-S CEN presentation format (Q3 2027)

---

## References

- DTEP-F repository: https://github.com/SolidarityLab/L-euro/tree/main/DTEP/DTEP-F
- DTEP-S Standardisation Roadmap: ./standardisation-roadmap.md
- BIS (Bulgarian Institute for Standardisation): https://www.bds-bg.org
- CEN/TC 434 (Electronic invoicing): https://www.cencenelec.eu/committees/cen-tc-434/
- ViDA package: https://ec.europa.eu/taxation_customs/taxation/value-added-tax/digital-economy_en
- Central VIES 2.0: https://ec.europa.eu/taxation_customs/vies/
