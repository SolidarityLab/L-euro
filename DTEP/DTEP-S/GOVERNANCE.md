# Governance

## Project Status

DTEP-S is in active specification phase (v0.1-draft). The governance model reflects the current scale and stage of the project and will evolve as the community grows.

---

## Decision Authority

**CSDT (Centre for Solidary Digital Transformation)** is the founding organisation and current maintainer of the DTEP-S specification. CSDT holds decision authority over:

- Protocol specification content and versioning
- Schema definitions and validation rules
- Repository structure and contribution policy
- Standardisation submissions (BIS, CEN/CENELEC, W3C)

Decision authority will be distributed to a broader governance body when the project reaches v1.0 or when multiple independent implementations exist.

---

## Maintainers

| Name | Role | Scope |
|---|---|---|
| Valeri Kostov | Protocol Architect / Lead Maintainer | Specification, standardisation, institutional coordination |
| Nikola Obreshkov | Mathematics / Architecture Maintainer | Biometric pipeline, formal verification, cryptographic primitives |
| Valentin Ivanov | Implementation Maintainer | Reference implementation, TEE integration, sandbox deployment |

---

## Contribution Process

### Specification changes

Changes to specification files (`spec/`, `schema/`) follow this process:

1. Open an issue describing the proposed change and its motivation
2. Discussion period — minimum 7 days for non-trivial changes
3. Maintainer review and decision
4. Pull request with specification update
5. Maintainer approval and merge

Breaking changes — those that invalidate existing protocol-compliant implementations — require explicit version increment and are documented in CHANGELOG.md.

### Documentation and tooling changes

Changes to `docs/`, `tests/`, `diagrams/`, and non-specification files may be merged with lighter process — issue optional, maintainer review required.

### Security issues

Do not open public issues for security vulnerabilities. See [SECURITY.md](SECURITY.md).

---

## Versioning Policy

DTEP-S follows semantic versioning adapted for protocol specifications:

**MAJOR** — breaking changes to the protocol. Implementations compliant with v(N) are not guaranteed to be compliant with v(N+1).

**MINOR** — backward-compatible additions. New optional fields, new presentation paths, new deployment scenarios.

**PATCH** — clarifications, corrections, and editorial changes that do not alter protocol behaviour.

Current version: **0.1-draft** — the specification is unstable. Breaking changes are expected before v1.0.

---

## Standardisation

Protocol outputs are submitted as standardisation contributions to:

- **BIS (Bulgarian Institute for Standardisation)** — national level, Technical Committee on Electronic Transactions
- **CEN/CENELEC** — European level, subsequent to BIS submission
- **W3C Credentials Community Group** — for device-independent VC presentation work item

Standardisation submissions are coordinated by the Lead Maintainer and documented in [docs/standardisation-roadmap.md](docs/standardisation-roadmap.md).

---

## Funding

The project is submitted to the NGI Zero Commons Fund (13th call) by CSDT. Infrastructure costs are covered by CSDT independently of external funding. The protocol and all outputs are and will remain open under EUPL-1.2 regardless of funding outcome.

---

## Amendments

This governance document may be amended by the Lead Maintainer with 14 days notice in the repository. Amendments are recorded in CHANGELOG.md.
