# DTEP-F DRRDB Layer

**Version:** 0.1-draft
**Status:** Specification in progress
**Date:** 2026-06-01
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

DRRDB (Digital Reporting Requirements Database) is Layer 5 of DTEP-F. It receives signed public DTEP JSON objects from Taler Exchange and stores them in a two-level architecture: a public level for real-time DRR queries from Central VIES and a protected level accessible on Audit Request.

DRRDB is built on the Taler auditor protocol — not a custom database, but an institutional instance of existing Taler infrastructure extended for the tax reporting context.

The internal database implementation is not fixed by this specification. DRRDB must simultaneously support graph traversal (for the analytical layer) and structured relational queries (for VIES API compatibility). The specification defines requirements; the implementation selects the appropriate database technology.

---

## 2. Two-Level Architecture

### Public level

Contains signed DTEP JSON objects with the six ontological sets M0–M5. Accessible without special rights for:

- Central VIES real-time queries via the VIES Adapter (Section 5)
- Analytical layer (Layer 6) — four primitives operating on the temporal hypergraph
- Third-party verification of Ed25519 signatures

Subject identifiers are absent from the public level — not pseudonymised, but structurally excluded. Time nodes in M1 are the sole index. No query by subject identifier is supported at the public API.

### Protected level

Contains Artifact A — the full encrypted JSON audit record from Taler Exchange. Accessible only for:

- Audit Request from the tax administration — for a specific M0 element only
- Business entity — for its own transactions, via EUDI Wallet with appropriate credentials

The protected level is not accessible to the analytical layer, Corner 5 Middleware, or third parties.

---

## 3. Hybrid Database Architecture

DRRDB requires simultaneous support for three distinct access patterns that cannot be efficiently served by a single database paradigm:

**Graph traversal** — τ(H) acyclicity verification and L(t) Leontief matrix computation require graph operations over the temporal hypergraph. Relational databases are structurally inefficient for this.

**Structured relational queries** — Central VIES queries are structured by M2 (CPV), M3 (NACE seller), M4 (NACE buyer), M1 (time window), M5 (amount range). Graph databases are unsuitable for this query pattern.

**Append-only audit log** — DRR records are immutable once signed. The storage layer must enforce append-only semantics with cryptographic integrity verification.

The reference configuration for the implementation phase is a hybrid architecture combining a graph extension over a relational database (such as Apache AGE over PostgreSQL) with an append-only log layer. The specific technology selection is deferred to the implementation phase — the specification defines the three requirements, not the implementation.

---

## 4. Taler Auditor Protocol as Foundation

The Taler auditor protocol provides mathematically provable completeness of the relationship between Exchange and DRRDB: every signed object in the public level has a corresponding encrypted record in the protected level. A missing record is deterministically detectable by the auditor protocol.

DTEP-F uses Taler auditor in a new role: instead of financial balance verification, the auditor verifies completeness of the DRR evidence chain. Every public DTEP JSON object must have a corresponding Artifact A in Exchange custody. The auditor protocol verifies this invariant continuously.

The formal extension of the Taler auditor protocol for this new invariant is a contribution to Taler core and is an open issue for v0.2 (see Section 8).

---

## 5. VIES Adapter Layer

DRRDB exposes a VIES Adapter as the interface between the public level and Central VIES. The adapter sits between Taler Exchange output and VIES API input — at the boundary between two systems neither of which is fully finalised.

The adapter serves two functions:

**Current VIES API compatibility** — translates DRRDB public level query results into the current VIES VAT validation API format. Supports structured queries by M2, M3, M4, M1 time window, M5 amount range.

**ViDA-aligned extension points** — defines extension interfaces for future Central VIES API versions aligned with ViDA DRR requirements. The adapter is versioned independently of the DRRDB core, allowing VIES API evolution without DRRDB restructuring.

The reference configuration proposed by DTEP-F for VIES compatibility:

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

## 6. Deduplication and Replay Prevention

On receipt of a new DRR record, DRRDB verifies:

- M0 coin commitment is not present in the deduplication index
- Ed25519 signature is valid against the Exchange signing key
- M1 timestamp is within the acceptable window relative to current system time

On duplicate M0 — the record is rejected and the incident is logged. On invalid signature — the record is rejected and an Audit Request is generated automatically.

---

## 7. Audit Request Mechanism

An Audit Request is generated by two triggers:

**Automatic trigger** — combined fraud signal from the analytical layer (Layer 6): at least two of the three anomaly signals (structural, macroeconomic, price) coincide for one M0 element.

**Manual trigger** — the tax administration submits an Audit Request for a specific M0 element with institutional authorisation via EUDI Wallet.

On Audit Request, Exchange provides the salt for the specific M0 — and only for that M0. DRRDB decrypts Artifact A and provides it to the tax administration via a secured EUDI Wallet connection. The scope of disclosure is bounded by the audit trigger — a single Audit Request does not expose the full DRRDB dataset.

---

## 8. Open Issues

The following define the research and specification agenda for the DRRDB layer. They represent the boundary of the current specification and the forward work programme.

**Hybrid database technology selection**
The specification defines three simultaneous requirements (graph traversal, relational queries, append-only log) without mandating a specific technology. The reference implementation phase will evaluate Apache AGE over PostgreSQL, Neo4j + PostgreSQL dual-instance, and other candidates against the three requirements at realistic national transaction volumes.

**Taler auditor extension for DRR evidence completeness**
Taler auditor verifies financial balance. DTEP-F requires verification of evidence chain completeness — a different invariant. The formal extension of the auditor protocol for this context is a contribution to Taler core requiring coordination with the Taler development team.

**VIES API versioning and ViDA alignment**
The Central VIES API is under active development aligned with ViDA DRR requirements. The VIES Adapter must track API evolution without requiring DRRDB restructuring. A versioning strategy and compatibility matrix for VIES API versions is an open specification item for v0.3.

**Retention policy and legal compliance**
National tax law defines mandatory retention periods for tax documents — typically 5–10 years. DRRDB retention policy must align with the longest applicable period across Member States in cross-border deployment. Cryptographically verifiable deletion at retention expiry — as distinct from administrative deletion — requires specification.

**Cross-border DRRDB federation**
For a transaction between entities in different Member States — in which national DRRDB instance is the record stored? The protocol must define a federation model: seller jurisdiction, buyer jurisdiction, dual storage, or a neutral third instance. An analogous unresolved question exists in the Peppol ViDA Pilot for Corner 5 jurisdiction.

**Audit Request authorisation protocol**
The current specification defines Audit Request as institutional access via EUDI Wallet authorisation. The detailed authorisation protocol — required credentials, access logging, disclosure scope limitation — requires separate specification in collaboration with national tax administrations.

**Sparse indexing for multi-year deployment**
The T × T temporal hypergraph matrix grows with deployment duration. Efficient sparse indexing of DRRDB for time-range queries over multi-year datasets is an engineering open issue for the implementation phase.

---

## References

- GNU Taler auditor: https://docs.taler.net/taler-auditor-manual.html
- VIES VAT validation API: https://ec.europa.eu/taxation_customs/vies/
- ViDA Directive 2025/516: https://eur-lex.europa.eu/eli/dir/2025/516
- eIDAS 2.0 ARF: https://eu-digital-identity-wallet.github.io/eudi-doc-architecture-and-reference-framework/
- Apache AGE: https://age.apache.org/
