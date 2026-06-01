# Changelog

All notable changes to DTEP-F / Taler Corner5 will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Planned for v0.2
- Taler coin commitment formal schema for M0
- Peppol AS4 input adapter — interface specification between Corner 4 and Corner 5
- Central VIES output API specification
- Taler B2B payment interface — detailed schema for binding coin reference with invoice lifecycle (cancellation, correction, credit note)
- Formal JSON Schema machine validation for all three schema files
- Context document publication at dtep-f.solidaritylab.org/context/v1

---

## [0.1-draft] — 2026-08-01

### Added
- Protocol overview specification — formal model of the six-layer architecture and positioning of DTEP-F as the Corner 5 internal protocol
- Hypergraph model specification — six ontological sets M0–M5, oriented hyperedge, time-oriented adjacency matrix
- Transformation layer specification — GNU Taler DD-18 forgettable fields implementation, JCS canonicalisation RFC 8785, two output artifacts
- Signing layer specification — Taler Exchange Ed25519 signing, M0 coin commitment
- DRRDB layer specification — layered storage on Taler auditor protocol, public and protected levels
- Analytical primitives specification — four primitives, combined fraud signal
- Payment interface specification — Taler wallet B2B integration bound to M0
- JSON Schema: dtep-public.json
- JSON Schema: dtep-encrypted.json
- JSON Schema: taler-invoice-ref.json

### Context

DTEP-F v0.1-draft crystallised at the intersection of three concurrent processes in March–May 2026.

**NGI TALER 13th open call** (deadline june 2026) provided the immediate funding opportunity and the open source framing within the Taler ecosystem.

**The ViDA package**, adopted on 11 March 2025 and introducing mandatory DRR from 1 July 2030, defines the regulatory mandate. The Peppol ViDA Pilot, launched December 2024 with over 100 organisations and 20 tax administrations, demonstrates the transport architecture to Corner 5 — but does not define the internal protocol of Corner 5. DTEP-F is precisely that protocol.

**BIS/TC84 draft specification** — the parallel standardisation process, initiated by CSDT as a member of the Bulgarian Institute for Standardisation. DTEP-F follows the open source first, standardisation second model: the TC84 draft defines the regulatory requirements; the present open source implementation realises them technically. The standard follows the implementation — not the reverse.

---

## Prior work

DTEP-F builds on institutional and technical groundwork accumulated since 2022:

- 2022–2025: External technical expert role at Bulgaria's Ministry of Tourism on humanitarian accommodation programmes under Council Directive 2001/55/EC — direct operational experience with the structural gap between transaction evidence and settlement
- 2025: CSDT constituted as a public benefit association and member of the Bulgarian Institute for Standardisation
- 2025–2026: DTEP-F protocol concept developed and submitted to BIS TC84
- 2026: DTEP-S (Social Layer) submitted to NGI Zero Commons Fund 13th call — the complementary social layer of the DTEP protocol family, sharing the same cryptographic core
- 2026: DTEP protocol family conceptualised on operational experience from three successive humanitarian accommodation programmes


[Unreleased]: https://github.com/SolidarityLab/dtep-f/compare/v0.1-draft...HEAD
[0.1-draft]: https://github.com/SolidarityLab/dtep-f/releases/tag/v0.1-draft
