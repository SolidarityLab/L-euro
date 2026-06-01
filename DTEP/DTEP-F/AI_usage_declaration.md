# AI Usage Declaration
## DTEP-F / Taler Corner5
## NGI TALER Open Call — Submitted June 2026

---

## Model and Session

**Model:** Claude Sonnet 4.6 (Anthropic)
**Dates:** May 30 – June 1, 2026
**Session language:** Bulgarian (specification session conducted in applicant's native language)
**Full session:** Available upon request to the NLnet review team.

---

## Nature of Use

The AI was used as a research verification, structuring, and specification drafting tool across two consecutive days of intensive technical work. The session was conducted entirely in Bulgarian — the applicant's native language — enabling precise articulation of complex protocol concepts without the friction of a second language.

The working method was iterative and dialogical: each document was first discussed in Bulgarian in the chat, refined through applicant-AI exchange, confirmed by the applicant, and only then generated as a formal English specification file. The AI did not generate content autonomously — it expressed, structured, and verified content determined by the applicant.

The protocol concept, temporal ontology inversion, four analytical primitives, M0 dual-role architecture, and DD-18 extension design are the intellectual work of the applicant. These predate and exist independently of this AI session as design decisions reached through applicant-AI dialogue with the applicant making all final determinations.

---

## What the AI Was Used For

**1. Taler ecosystem research**

Queries confirmed the current state of NGI TALER funded projects, GNU Taler DD-18 design document scope, Taler Contract Terms mechanics, and the boundary between existing Taler implementations and the gap DTEP-F fills. Finding: no existing funded project covers the combination of Peppol Corner 5 internal protocol + GNU Taler cryptographic infrastructure + privacy-preserving real-time fraud detection + B2B payment interface bound to DRR record.

**2. Peppol and ViDA landscape verification**

Queries confirmed: ViDA Directive 2025/516 adoption date and DRR timeline; Peppol 5-corner model and ViDA Pilot status; Central VIES API current state; national DRR implementations (SdI, Chorus Pro, SII, e-Invoice.bg) and their gaps relative to DTEP-F.

**3. Architecture development dialogue**

The following architectural decisions were reached through explicit applicant-AI dialogue, with the applicant making all final determinations:

- The atomic Taler Exchange operation unifying Layers 3 and 4 — DD-18 scrubbing and Ed25519 signing as a single non-separable operation
- HKDF-SHA512 salt derivation from M0 coin commitment (RFC 5869) — binding scrubbing cryptographically to the invoice identifier
- The temporal ontology inversion — nodes are time moments, not subjects — and its three non-trivial consequences (computability, privacy, deterministic carousel fraud detection)
- The VIES Adapter as a versioned abstraction layer between DRRDB and Central VIES
- Taler Contract Terms as the complete payment protocol — eliminating the need for a separate payment specification
- The hybrid graph/relational database requirement for DRRDB — without fixing the implementation

**4. Full repository specification drafting**

The AI assisted in drafting all 28 files in the repository. Each file was reviewed in Bulgarian before generation. The complete file inventory:

*Root:*
README.md, CHANGELOG.md, LICENSE, CONTRIBUTING.md, AI_usage_declaration.md, SECURITY.md, GOVERNANCE.md, CODE_OF_CONDUCT.md

*spec/:*
protocol-overview.md, hypergraph-model.md, transformation-layer.md, signing-layer.md, drrdb-layer.md, analytical-primitives.md, payment-interface.md, conformance-testing.md

*schema/:*
dtep-public.json, dtep-encrypted.json, taler-invoice-ref.json, openapi.yaml

*docs/:*
vida-positioning.md, gdpr-analysis.md, threat-model.md, standardisation-roadmap.md, taler-integration-notes.md, deployment-guide.md

*tests/:*
test_vectors.json

The protocol architecture, formal hypergraph model, validation rules, JSON schema structure, OpenAPI endpoints, conformance test profiles, and test vectors were determined by the applicant. The AI expressed them in formal specification language, maintained cross-document consistency, and identified internal consistency issues during drafting.

**5. Proposal structuring**

The AI assisted in structuring the proposal text across the six NLnet form fields within character limits (Abstract 1200, Experience 2500, Budget 2500, Compare 4000, Challenges 5000, Ecosystem 2500). Content was provided by the applicant; the AI organised and expressed it in proposal-appropriate form and verified character counts.

---

## What the AI Did Not Do

- Did not generate the protocol concept (DTEP-F / Taler Corner5)
- Did not generate the temporal ontology (nodes are time moments, not subjects)
- Did not generate the four analytical primitives (R(c,t), δ(e), L(t), τ(H))
- Did not generate the M0 dual-role architecture (DRR evidence + Taler payment reference)
- Did not generate the DD-18 extension (salt derivation from M0 via HKDF)
- Did not make architectural decisions — these were reached through applicant-AI dialogue with the applicant making all final determinations
- Did not select the standards stack (GNU Taler, Peppol BIS Billing 3.0, EN 16931, ViDA, EUPL-1.2)
- Did not identify the real-world problem context (ViDA Corner 5 gap, Bulgarian e-Invoice.bg deployment)
- Did not produce the BIS/TC84 draft specification (pre-existing, human-authored)

---

## Process Note

The 28-file repository was produced across two days (May 31 – June 1, 2026) in parallel with the NGI Zero Commons Fund submission for DTEP-S (Social Layer), which was submitted on June 1, 2026. The two projects share the same team and the same AI session overlap. The working pace was made possible by the AI's ability to compress specification drafting time — not by substituting the applicant's intellectual contribution.

The honest characterisation: the AI acted as a high-bandwidth specification secretary and research verifier. The protocol is the applicant's work. The repository is the joint product of the applicant's architecture and the AI's drafting capacity.

---

## Planned Use During Project Execution

AI-assisted code generation tools will be used during implementation phases. All AI-assisted code contributions will be disclosed per commit following NLnet GenAI policy:

- Commit messages will identify AI-assisted contributions
- Model and version will be recorded
- Material prompts and unedited outputs will be referenced or attached per commit

---

## Relation to DTEP-S Declaration

A parallel AI usage declaration exists for the DTEP-S (Social Layer) proposal submitted to NGI Zero Commons Fund 13th call (June 2026). The same AI model and session overlap was used for both proposals. The two declarations are independent — each covers only the work relevant to its respective proposal.
