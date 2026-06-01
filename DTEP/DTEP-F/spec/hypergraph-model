# DTEP-F Hypergraph Model

**Version:** 0.1-draft
**Status:** Specification in progress
**Date:** 2026-06-01
**Authors:** CSDT / SolidarityLab

---

## 1. Motivation and Ontological Choice

Conventional modelling of transaction networks for tax analysis uses subject nodes: each taxpayer is a node, each transaction is an edge between two subjects. The adjacency matrix is N × N where N is the number of subjects. At national scale N reaches millions — the matrix is computationally intractable. Furthermore, subject identifiers are personal data even when pseudonymised: statistical de-anonymisation methods are well documented for N × N subject matrices with sufficient density.

DTEP-F applies an ontological inversion: **nodes are time moments, not subjects.** Transactions are oriented hyperedges connecting time moments through transaction attributes. Subject identifiers do not participate in the graph structure — not as pseudonyms, but at all.

This is a seemingly trivial solution with three non-trivial consequences described in Section 5.

---

## 2. The Six Ontological Sets

The DTEP-F implementation indexes transaction data in six independent transversal sets:

### M0 — Taler coin commitments

Contains Taler blind signature coin commitments representing invoice identifiers. Direct plain-text access in the public layer is not permitted. The coin commitment provides cryptographic unlinkability: an observer cannot link two M0 elements to the same invoice without access to Taler Exchange.

### M1 — Time moments

Contains time buckets in ISO 8601 format, quantised to the beginning of the current astronomical hour (YYYY-MM-DDThh:00:00Z). Higher temporal granularity in the public layer is not permitted, to prevent de-anonymisation through temporal analysis. M1 is the set of **nodes** of the hypergraph H.

### M2 — CPV codes

Contains eight-digit commodity codes per Regulation (EC) No 213/2008. The CPV code defines the type of the hyperedge. Invoices with more than one CPV code are decomposed into separate hyperedges with a proportional amount from M5 and a shared M0 element.

### M3 — NACE codes (sellers)

Sectoral classification of suppliers per Regulation (EC) No 1893/2006.

### M4 — NACE codes (buyers)

Sectoral classification of recipients per Regulation (EC) No 1893/2006.

### M5 — Amounts

Transaction value in euros (EUR) per ISO 4217. Commodity quantity q is derived as: q = s / R(c, t), where s ∈ M5 and R(c, t) is the reference price function from Analytical Primitive 1.

---

## 3. The Oriented Hyperedge

Every transaction is defined as an oriented hyperedge — a finite set relation without external attributes:

```
e = (h, t, c, ns, nb, s) ∈ M0 × M1 × M2 × M3 × M4 × M5
```

The direction of the hyperedge is oriented from the moment of issuance toward the moment of the tax event. The system verifies: t_issuance ≤ t_tax_event.

The hyperedge e connects two time nodes from M1: t_issuance and t_tax_event. If they coincide (issuance and tax event in the same hourly bucket), the hyperedge is self-connecting on one node — a valid configuration requiring no special processing mode.

---

## 4. The Hypergraph and Adjacency Matrix

The global transaction model is the hypergraph:

```
H = (M1, E), where E ⊆ M0 × M1 × M2 × M3 × M4 × M5
```

The adjacency matrix is maintained in dense T × T format, where T = |M1| is the number of unique time buckets. With hourly quantisation T = 8,760 for one calendar year.

Element A[i][j] of the matrix represents the total value of all transactions with t_issuance = i and t_tax_event = j.

Conventional N × N subject indexing is not permitted for the real-time analytical layer.

---

## 5. Three Non-Trivial Consequences of the Ontological Inversion

### 5.1 Computability

Subject ontology: complexity O(N²), N = number of taxpayers.
Temporal ontology: complexity O(T²), T = number of time buckets.

At N = 5,000,000 taxpayers and T = 8,760 buckets per year:

| Model | Matrix elements |
|---|---|
| Subject adjacency matrix | 25 × 10¹² |
| Temporal adjacency matrix | 76,737,600 |

The difference is a factor of ~326,000. The temporal matrix is computationally trivial on standard hardware. The subject matrix is intractable in real time at any realistic national scale.

### 5.2 Privacy

Time nodes in M1 are not personal data under any GDPR definition — they are astronomical time intervals. Subject identifiers are processed exclusively in Layer 3 through DD-18 scrubbing and are absent from the graph structure.

Therefore: the analytical layer operates on data that structurally cannot contain personal information — not by policy or pseudonymisation, but by ontological choice. De-anonymisation is mathematically impossible, not merely unauthorised.

### 5.3 Deterministic Carousel Fraud Detection

In a subject graph, the cycle A → B → C → A is difficult to detect under pseudonymisation: it requires identification of subjects to establish cycle closure.

In a temporal graph, the cycle requires:

```
t_A < t_B < t_C < t_A
```

This violates the transitivity of the strict order relation < over the real numbers (ℝ, <). Mathematically impossible under normal commercial activity.

Therefore: τ(H) = cyclic is a **deterministic** carousel fraud signal, not a probabilistic threshold. No legitimate transaction chain can form a cycle in the temporal graph.

---

## 6. Boundary Case: Simultaneous Transactions

Multiple transactions in the same hourly bucket share an identical t ∈ M1. They share one temporal node but differ in the remaining coordinates (M0, M2, M3, M4, M5). Their hyperedges are distinct elements of E.

τ(H) verifies the oriented graph of time nodes from M1 — not individual hyperedges. Simultaneous transactions do not create a cycle in M1 unless they violate the temporal orientation t_issuance ≤ t_tax_event, which is a separate validation check.

---

## 7. Incremental Update

On receipt of a new hyperedge e = (h, t_i, c, ns, nb, s):

1. M0, M2, M3, M4, M5 are updated with the new element
2. If t_i ∉ M1: a new time node is added; the matrix is extended with a new row and column
3. If t_i ∈ M1: A[t_issuance][t_tax_event] += s
4. Leontief technical coefficients are recomputed incrementally for the affected rows
5. τ(H) is verified locally — only newly added edges are checked for cycles

Full recomputation of the matrix on every new hyperedge is not required.

---

## 8. Formal Properties

| Property | Statement |
|---|---|
| Acyclicity invariant | H is a DAG under normal commerce — any cycle is a fraud signal |
| Time irreversibility | t_issuance ≤ t_tax_event is a hard constraint; violation is rejected |
| Subject exclusion | No subject identifier appears in (M1, E) by construction |
| Incremental consistency | Incremental update preserves all analytical primitive results |
| Decomposition invariance | Multi-CPV invoice decomposition preserves total M5 sum and shared M0 |

---

## 9. Open Issues

- [ ] Formal proof of equivalence between subject-ontology and temporal-ontology analytical results (v0.2)
- [ ] Boundary definition for simultaneous transactions within one bucket under τ(H) (v0.2)
- [ ] Coin commitment lifecycle mapping to invoice lifecycle (cancellation, correction, credit note) (v0.2)
- [ ] T × T matrix sparse representation for multi-year deployments (v0.3)
