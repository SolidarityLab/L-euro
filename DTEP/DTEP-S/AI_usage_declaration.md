# AI Usage Declaration
## DTEP-S — Digital Transaction Evidence Protocol: Social Layer
## NGI Zero Commons Fund — 13th Call — Submitted June 1, 2026

---

## Model and Session

**Model:** Claude Sonnet 4.6 (Anthropic)  
**Dates:** May 26–28, 2026  
**Session language:** Bulgarian (research session conducted in applicant's native language)  
**Full session:** Available at the URL provided separately to the NLnet review team upon request.

---

## Nature of Use

The AI was used exclusively as a **research verification and structuring tool** during proposal preparation. It did not generate the protocol concept, the institutional context, the architectural decisions, or the strategic positioning. These are the intellectual work of the applicant, grounded in three years of direct operational experience with the subject matter.

Specifically: the applicant has served since 2022 as external technical expert to Bulgaria's Ministry of Tourism on humanitarian accommodation programmes under Council Directive 2001/55/EC, including coordination of European Court of Auditors audit missions. The eleven-defect diagnostic of the administrative chain, the identification of the structural gap between Act of Delivery and Payment, and the protocol concept itself predate and exist independently of this AI session.

---

## What the AI Was Used For

**1. Regulatory landscape verification**

Queries confirmed the current status of:
- NGI Zero Commons Fund 13th call parameters and deadline
- Eurodac Regulation 2024/1358 — scope, implementation date, and explicit exclusion of temporary protection beneficiaries until ~2029
- EUDIW / eIDAS 2.0 Architecture and Reference Framework — credential types, presentation protocols, device assumptions
- DC4EU Large Scale Pilot — scope, results, and gap analysis
- W3C Verifiable Credentials Data Model 2.0 — official standard status (May 2025)
- NLnet GenAI policy — requirements for proposal and implementation disclosure

**2. Ecosystem gap analysis**

The AI was used to verify that the specific combination addressed by DTEP-S — EU regulatory context + W3C VC architecture + analogue Holder without device + physical delivery + cryptographically verifiable evidence + open protocol — is not covered by any existing funded project or standard. Five solutions were systematically compared: EBT, EUDIW, DC4EU, Simprints, and the NGI-funded Peppol bootstrapping project.

**3. Biometric pipeline architecture review**

The AI was used to verify prior art for the proposed biometric preprocessing approach (tensor aggregation, Fourier-Mellin normalisation, neural feature extraction). Finding: the individual components are documented in academic literature; their composition as an open, privacy-preserving, credential-bound pipeline for field conditions is not. The architectural decision to use merchant-side TEE signing rather than fuzzy extractor key binding was reached through this review.

**4. Proposal structuring**

The AI assisted in structuring the proposal text across the six NLnet form fields. The content — institutional context, technical challenges, ecosystem actors, comparison with existing solutions — was provided by the applicant. The AI organised and expressed it in proposal-appropriate form.

**5. Specification drafting**

The AI assisted in drafting the five specification files and three JSON schema files now in the repository. The protocol architecture, validation rules, and design decisions were determined by the applicant. The AI expressed them in formal specification language and identified internal consistency issues.

---

## What the AI Did Not Do

- Did not generate the protocol concept (DTEP-S)
- Did not identify the real-world problem context (Bulgarian humanitarian programmes)
- Did not make architectural decisions (these were reached through applicant-AI dialogue with applicant making final determinations)
- Did not produce the eleven-defect diagnostic document (pre-existing, human-authored)
- Did not select the standards stack (W3C VC 2.0, eIDAS 2.0, EUPL-1.2)

---

## Planned Use During Project Execution

AI-assisted code generation tools (code assistants) will be used during implementation phases. All AI-assisted code contributions will be disclosed per commit in the repository following NLnet GenAI policy:

- Commit messages will identify AI-assisted contributions
- Model and version will be recorded
- Prompts and unedited outputs will be referenced or attached per commit

Specification updates during the project will follow the same disclosure practice as this declaration.

---

## Unedited Output Availability

The full session — including all prompts and unedited AI responses — is available in the Claude.ai conversation history and can be provided to the NLnet review team upon request. The session is in Bulgarian; an English summary is provided in this document.

Key unedited outputs that directly informed the proposal:

- Eurodac 2024/1358 gap analysis (explicit exclusion of temporary protection beneficiaries)
- EUDIW device-independence gap identification
- DC4EU completion layer gap identification
- Biometric prior art review (fuzzy extractor vs. neural extractor decision)
- NLnet GenAI policy requirements summary

Full session available at: https://claude.ai/share/fed6c0b8-867b-4e4c-8eed-31fd34275a9d — 
Session conducted in Bulgarian (applicant's native language). English summary provided in the AI Usage Declaration attachment.
