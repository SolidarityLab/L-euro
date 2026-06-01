# DTEP-F Analytical Primitives

**Version:** 0.1-draft
**Status:** Specification in progress
**Date:** 2026-06-01
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

The analytical layer (Layer 6) applies four primitives over the public sets M0–M5 of the DTEP hypergraph. The primitives operate exclusively on the public level of DRRDB — without access to subject identifiers, without access to the protected level. The results are three anomaly signals and one deterministic fraud signal. When at least two anomaly signals coincide for one M0 element, an Audit Request is generated.

---

## 2. Primitive 1 — Reference Price Function R(c,t)

```
R: M2 × M1 → ℝ₊
```

The function maps CPV code c ∈ M2 and time moment t ∈ M1 to an expected market price per unit of goods or services.

R(c,t) is an external oracle injected as a configuration parameter. It is not computed by the protocol — the protocol defines the interface, not the specific oracle. Reference sources for implementation: Eurostat HICP by COICOP category, TED (Tenders Electronic Daily) public procurement by CPV, ECB price indices.

R(c,t) is a necessary prerequisite for Primitive 2 and for the derivation of quantity q = s / R(c,t) from M5.

---

## 3. Primitive 2 — Price Deviation δ(e)

```
δ: E → ℝ
```

For hyperedge e = (h, t, c, ns, nb, s):

```
q     = s / R(c, t)
δ(e)  = (s/q − R(c,t)) / R(c,t)  =  s / (q · R(c,t)) − 1
```

Under normal commercial activity |δ(e)| < θ(c), where θ(c) is a threshold specific to the CPV category. The threshold accounts for normal price volatility for the corresponding goods or service type.

**Price anomaly signal:** |δ(e)| ≥ θ(c)

An isolated price signal is not sufficient for an Audit Request — coincidence with at least one of the other two signals (structural or macroeconomic) is required.

---

## 4. Primitive 3 — Real-Time Leontief Matrix L(t)

```
L: M1 → ℝ^(K×K)
```

K = number of unique NACE codes in M3 ∪ M4. L(t) is the Leontief technical coefficients matrix, recomputed incrementally at every new hyperedge.

Technical coefficient:

```
a_{ns,nb}(t) = Σ{e: ns(e)=ns, nb(e)=nb, t(e)≤t} s(e)
               ─────────────────────────────────────────
               Σ{e: ns(e)=ns, t(e)≤t} s(e)
```

Interpretation: what share of sector ns sales flows to sector nb up to moment t.

**Macroeconomic anomaly signal:** observed a_{ns,nb}(t) deviates from the expected value per reference Leontief matrix (Eurostat input-output tables) by more than threshold φ(ns,nb).

The classical Leontief matrix is computed over five-year statistical cycles. L(t) is recomputed incrementally at every new hyperedge — eliminating the five-year statistical lag. Computationally feasible only due to the temporal ontology: O(T²) instead of O(N²).

---

## 5. Primitive 4 — Topological Acyclicity τ(H)

```
τ: H → {acyclic, cyclic}
```

τ(H) verifies that the oriented graph of time nodes from M1 is a DAG (Directed Acyclic Graph). Verification is executed locally on every new hyperedge — only newly added edges are checked for cycles.

Algorithm: Kahn's algorithm or DFS in O(V + E), where V = |M1| and E = |E|.

**Deterministic carousel fraud signal:** τ(H) = cyclic

A cycle in the temporal graph requires:

```
t_A < t_B < t_C < t_A
```

This violates the transitivity of the strict order relation < over ℝ. Mathematically impossible under normal commercial activity. This is not a probabilistic threshold — it is a deterministic signal.

On a deterministic signal, an Audit Request is generated immediately, without waiting for coincidence with other signals.

---

## 6. Combined Fraud Signal

Three anomaly signals:

| Signal | Condition | Type |
|---|---|---|
| S_price | \|δ(e)\| ≥ θ(c) | Probabilistic |
| S_macro | deviation of a_{ns,nb}(t) ≥ φ(ns,nb) | Probabilistic |
| S_structural | τ(H) = cyclic | Deterministic |

**Decision rules:**

- S_structural → Audit Request immediately, unconditionally
- S_price ∧ S_macro → Audit Request
- S_price alone → log for monitoring, no Audit Request
- S_macro alone → log for monitoring, no Audit Request

The combined signal reduces the false positive rate: an isolated price or macroeconomic anomaly signal may reflect legitimate market volatility. Coincidence of two independent signals is significantly less probable under legitimate commercial activity.

---

## 7. Incremental Update

On receipt of new hyperedge e:

1. δ(e) computed immediately — O(1)
2. a_{ns,nb}(t) updated incrementally — O(1) for the affected coefficient
3. τ(H) verified locally — O(V + E) for new edges only
4. Combined signal evaluated — O(1)

Full recomputation of L(t) or τ(H) on every new hyperedge is not required.

---

## 8. Open Issues

The following define the research and specification agenda for the analytical layer. They represent the boundary of the current specification and the forward work programme.

**CPV to HICP/COICOP mapping**
The methodology for mapping between CPV eight-digit classification and Eurostat HICP/COICOP categories is not unambiguous. CPV is designed for public procurement; HICP covers consumer prices. B2B transactions span both. The reference mapping requires methodological development with Eurostat participation.

**Threshold calibration θ(c) and φ(ns,nb)**
The price deviation threshold θ(c) and the macroeconomic deviation threshold φ(ns,nb) must be calibrated on real transaction data. Synthetic data is sufficient for v0.1 baseline; real calibration requires access to a national sandbox with real transactions.

**Reference Leontief matrix currency**
Eurostat publishes input-output tables at national level with a five-year lag. Using them as a reference for φ(ns,nb) introduces a structural lag in anomaly detection. A methodology for compensating the statistical lag in real-time detection requires separate specification.

**Multi-sector transactions**
Invoices with more than one CPV code are decomposed into separate hyperedges (hypergraph-model.md, Section 2). Decomposition preserves the M5 sum but may distort δ(e) for individual components under non-uniform price distribution. A methodology for multi-sector decomposition with correct price attribution requires specification.

**Leontief matrix under sparse data in early deployment**
In the early deployment phase, transactions for certain NACE pairs (ns, nb) may be insufficient for statistically significant estimation of a_{ns,nb}(t). Thresholds φ(ns,nb) must be adaptive to observation density — sparse coefficients require wider thresholds or temporary deactivation of the macroeconomic signal.

**Oracle governance for R(c,t)**
The reference price oracle R(c,t) is injected as a configuration parameter. In a national deployment, the governance of the oracle — who updates it, at what frequency, with what audit trail — requires institutional specification. An adversarially manipulated oracle invalidates the price signal entirely.

---

## References

- Eurostat input-output tables: https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables
- Eurostat HICP: https://ec.europa.eu/eurostat/web/hicp
- TED public procurement: https://ted.europa.eu/
- ECB price indices: https://www.ecb.europa.eu/stats/
- Kahn's algorithm: Kahn, A.B. (1962). Topological sorting of large networks. Communications of the ACM, 5(11), 558–562.
