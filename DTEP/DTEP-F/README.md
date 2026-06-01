# DTEP-F / Taler Corner5

> **Digital Transaction Evidence Protocol — Fiscal Layer**
> **Status:** Specification in progress | NGI TALER open call 

DTEP-F (Digital Transaction Evidence Protocol — Fiscal Layer), positioned as Taler Corner5, is an open protocol specification and reference implementation for privacy-preserving processing of transaction evidence at the fifth corner of the Peppol ViDA architecture, built on GNU Taler.

---

## The Problem

The ViDA package, adopted on 11 March 2025, introduces mandatory Digital Reporting Requirements for B2B transactions in real time to Member State tax administrations, with full enforcement from 1 July 2030. The Peppol 5-corner model defines the transport architecture to Corner 5 — the tax authority. But it does not define what happens inside Corner 5: how transaction data is stored, analysed, and proven with privacy-by-design. This is the structurally vacant field.

Existing approaches — EU Transaction Network Analysis, SAF-T, national DRR databases — are either batch-based and retrospective, or operate on subject identifiers in real time without privacy guarantees. None is an open protocol.

---

## What DTEP-F / Taler Corner5 Does

The protocol accepts EN 16931 invoice data from the Peppol Access Point at Corner 5 and processes it through a six-layer architecture:

```
LAYER 1 — Regulatory Context
eIDAS 2.0 / EUDI Wallet subject identification

LAYER 2 — Peppol Transport
BIS Billing 3.0 / AS4 / 5-corner model
Corner 1-4: standard Peppol B2B exchange
Corner 5: entry point into DTEP-F

LAYER 3 — Transformation (GNU Taler DD-18)
Forgettable fields scrubbing
EN 16931 XML → two artifacts:
  - Full encrypted JSON (audit record)
  - Public DTEP JSON (M0–M5 hypergraph object)

LAYER 4 — Taler Exchange Signing
M0 = Taler coin commitment (replaces SHA512)
Cryptographic unlinkability
Ed25519 signature over public object

LAYER 5 — DRRDB
Layered storage on Taler auditor protocol
Public level → Central VIES queries
Protected level → EUDI Wallet access

LAYER 6 — Analytical Layer
Four real-time fraud detection primitives
over public sets M0–M5
```

In parallel, the M0 coin commitment serves as a reference for GNU Taler B2B payment — the business receives a wallet interface for advance or subsequent invoice payment, cryptographically bound to the DRR record. One action closes both the DRR obligation and the payment.

---

## Key Architectural Innovation

Conventional transaction graphs use subject nodes — an N × N adjacency matrix where N is the number of taxpayers. At national scale N reaches millions; the matrix is computationally intractable and subject identifiers are personal data even when pseudonymised.

DTEP-F applies a seemingly trivial inversion: **nodes are time moments, not subjects**. Hyperedges connect time moments through transaction attributes without subject identifiers in the graph structure. With hourly quantisation the matrix is T × T = 8,760 × 8,760 regardless of the number of taxpayers.

The consequences are non-trivial in three directions simultaneously:

- **Computability:** from O(N²) to O(T²) — orders of magnitude difference at N = 5 million taxpayers vs T = 8,760 time buckets
- **Privacy:** time nodes are not personal data by any definition — subject identifiers are absent from the graph structure entirely, not pseudonymised
- **Carousel fraud detection:** a cycle in a temporal graph violates the irreversibility of time — physically impossible under normal commerce. τ(H) acyclicity is a deterministic signal, not a probabilistic threshold

---

## The Six Ontological Sets

Every transaction is modelled as an oriented hyperedge:

```
e = (h, t, c, ns, nb, s) ∈ M0 × M1 × M2 × M3 × M4 × M5
```

| Set | Content | Role |
|---|---|---|
| M0 | Taler coin commitment | Invoice identifier — unlinkable |
| M1 | ISO 8601 timestamp (hourly bucket) | Temporal node |
| M2 | CPV code | Commodity type |
| M3 | NACE code (seller) | Sector classification |
| M4 | NACE code (buyer) | Sector classification |
| M5 | Amount in EUR | Transaction value |

---

## Four Analytical Primitives

**Primitive 1 — Reference price function R(c,t)**
Maps CPV code × time moment to expected market price. External oracle injected as configuration parameter. Sources: Eurostat HICP, TED public procurement data, ECB price indices.

**Primitive 2 — Price deviation δ(e)**
Normalised deviation of declared transaction amount from reference price. Anomaly signal when |δ(e)| > θ(c).

**Primitive 3 — Real-time Leontief matrix L(t)**
Inter-sectoral input-output matrix recomputed incrementally at every new hyperedge. Eliminates the five-year statistical lag of classical Leontief analysis.

**Primitive 4 — Topological acyclicity τ(H)**
DAG verification over the temporal hypergraph. A cycle A → B → C → A violates time irreversibility — deterministic carousel fraud signal. Verified by Kahn's algorithm or DFS in O(V + E).

**Combined fraud signal:** when at least two of the three anomaly signals (structural, macroeconomic, price) coincide, the analytical layer automatically triggers an Audit Request to the DRRDB protected endpoint.

---

## Relation to GNU Taler

| Taler Component | Role in DTEP-F |
|---|---|
| DD-18 forgettable fields | Subject identifier scrubbing in Layer 3 |
| Coin commitment | M0 invoice identifier with unlinkability |
| Exchange signing | Layer 4 — Ed25519 signature authority |
| Auditor protocol | Layer 5 — DRRDB storage and verification |
| Wallet interface | B2B payment bound to DRR record |

DTEP-F is the first implementation of GNU Taler DD-18 in a tax reporting context. The M0 coin commitment extends Taler Exchange for B2B invoice reference. Results will be contributed to Taler core documentation as a reference implementation of DD-18 in institutional context.

---

## Relation to Existing Standards

| Standard / Initiative | Relation to DTEP-F |
|---|---|
| Peppol BIS Billing 3.0 | Input format at Corner 5 |
| EN 16931-1:2025 | Invoice semantic model |
| ViDA / DRR | Regulatory mandate DTEP-F implements |
| GNU Taler DD-18 | Scrubbing mechanism — Layer 3 |
| eIDAS 2.0 / EUDIW | Subject identification — Layer 1 |
| ISO 20022 | Ed25519 signature compatibility |
| SAF-T | Complementary — retrospective audit layer |

---

## Repository Structure

```
dtep-f/
├── README.md
├── LICENSE                         (EUPL-1.2)
├── CHANGELOG.md
├── CONTRIBUTING.md
├── AI_usage_declaration.md
├── spec/
│   ├── protocol-overview.md
│   ├── hypergraph-model.md
│   ├── transformation-layer.md
│   ├── signing-layer.md
│   ├── drrdb-layer.md
│   ├── analytical-primitives.md
│   └── payment-interface.md
├── schema/
│   ├── dtep-public.json
│   ├── dtep-encrypted.json
│   └── taler-invoice-ref.json
└── docs/
    ├── vida-positioning.md
    ├── gdpr-analysis.md
    └── threat-model.md
```

---

## Standardisation Trajectory

The protocol follows the open source first, standardisation second model. A draft technical specification has been submitted to BIS/TC84 (Bulgarian Institute for Standardisation, Technical Committee on Electronic Transactions). Upon project completion, a standardisation contribution will be submitted to TC84 targeting subsequent CEN/CENELEC proposal.

---

## Funding

This project is submitted to the **NGI TALER open call** by the **Centre for Solidary Digital Transformation (CSDT / SolidarityLab)** (EIK 208569411) — a Bulgarian public benefit association and member of BIS.

- Protocol Architect: Valeri Kostov
- Mathematics / Architecture: Nikola Obreshkov
- Backend / DevOps: Valentin Ivanov

---

## License

[EUPL-1.2](LICENSE) — European Union Public Licence v1.2
