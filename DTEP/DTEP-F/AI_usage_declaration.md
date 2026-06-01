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

The AI was used as a research verification, structuring, and specification drafting tool during proposal and repository preparation. It did not generate the protocol concept, the hypergraph model, the temporal ontology, the analytical primitives, or the Taler integration architecture. These are the intellectual work of the applicant.

Specifically: the temporal ontology inversion (nodes are time moments, not subjects), the four analytical primitives (R(c,t), δ(e), L(t), τ(H)), the M0 coin commitment as simultaneous DRR evidence and Taler payment reference, and the DD-18 salt derivation from M0 via HKDF — all predate and exist independently of this AI session as design decisions reached through applicant-AI dialogue with the applicant making all final determinations.

---

## What the AI Was Used For

**1. Taler ecosystem research**

Queries confirmed the current state of NGI TALER funded projects, GNU Taler DD-18 design document scope, Taler Contract Terms mechanics, and the boundary between existing Taler implementations and the gap DTEP-F fills.

**2. Peppol and ViDA landscape verification**

Queries confirmed: ViDA Directive 2025/516 adoption date and DRR timeline; Peppol 5-corner model and ViDA Pilot status; Central VIES API current state; national DRR implementations (SdI, Chorus Pro, SII, e-Invoice.bg).

**3. Ecosystem gap analysis**

The AI was used to verify that the specific combination addressed by DTEP-F — Peppol Corner 5 internal protocol + GNU Taler cryptographic infrastructure + privacy-preserving real-time fraud detection + B2B payment interface bound to DRR record + open protocol — is not covered by any existing funded project or standard.

**4. Specification drafting**

The AI assisted in drafting the ten specification files, three JSON schema files, and three documentation files in the repository. The protocol architecture, formal model, validation rules, and design decisions were determined by the applicant. The AI expressed them in formal specification language and identified internal consistency issues.

**5. Proposal structuring**

The AI assisted in structuring the proposal text across the six NLnet form fields within character limits. Content was provided by the applicant; the AI organised and expressed it in proposal-appropriate form.

---

## What the AI Did Not Do

- Did not generate the protocol concept (DTEP-F / Taler Corner5)
- Did not generate the temporal ontology (nodes are time moments, not subjects)
- Did not generate the four analytical primitives
- Did not generate the M0 dual-role architecture (DRR evidence + Taler payment reference)
- Did not generate the DD-18 extension (salt derivation from M0 via HKDF)
- Did not make architectural decisions — these were reached through applicant-AI dialogue with the applicant making all final determinations
- Did not select the standards stack (GNU Taler, Peppol BIS Billing 3.0, EN 16931, ViDA, EUPL-1.2)

---

## Planned Use During Project Execution

AI-assisted code generation tools will be used during implementation phases. All AI-assisted code contributions will be disclosed per commit following NLnet GenAI policy:

- Commit messages will identify AI-assisted contributions
- Model and version will be recorded
- Material prompts and unedited outputs will be referenced or attached per commit

---

## Relation to DTEP-S Declaration

A parallel AI usage declaration exists for the DTEP-S (Social Layer) proposal submitted to NGI Zero Commons Fund 13th call (June 2026). The same AI model and session overlap was used for both proposals. The two declarations are independent — each covers only the work relevant to its respective proposal.
