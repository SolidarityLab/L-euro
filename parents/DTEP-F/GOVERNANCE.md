# Governance

## Institutional Holder

DTEP-F is developed and maintained by the **Centre for Solidary Digital Transformation (CSDT / SolidarityLab)**, a Bulgarian public benefit association (EIK 208569411) and member of the Bulgarian Institute for Standardisation (BIS).

CSDT holds the protocol specification, the repository, and the standardisation trajectory (BIS/TC84 → CEN/CENELEC). The EUPL-1.2 licence ensures that the protocol remains open regardless of CSDT's institutional continuity.

---

## Decision-Making Model

DTEP-F follows a **BDFL Delegate** model:

**Protocol Architect (Valeri Kostov)** holds veto authority over protocol-level decisions:
- Changes to the six-layer architecture
- Changes to the six ontological sets M0–M5
- Changes to the four analytical primitives
- Breaking changes to JSON schemas
- Standardisation submission content

**Core Contributors** (Nikola Obreshkov, Valentin Ivanov) hold consensus authority over implementation-level decisions:
- Reference implementation architecture
- Test vector design
- CI/CD and tooling
- Non-breaking schema extensions

**External Contributors** may propose changes via pull requests. All pull requests require review by at least one Core Contributor and approval by the Protocol Architect for protocol-level changes.

---

## Merge Rights

| Change type | Required approvals |
|---|---|
| Protocol specification (spec/) | Protocol Architect |
| JSON Schema (schema/) | Protocol Architect + 1 Core Contributor |
| Reference implementation (src/) | 1 Core Contributor |
| Documentation (docs/) | 1 Core Contributor |
| Administrative (SECURITY, GOVERNANCE, etc.) | Protocol Architect |

---

## Release Process

Releases follow **Semantic Versioning** (SemVer):

- **MAJOR** (1.0.0): breaking protocol changes — requires Protocol Architect sign-off and BIS/TC84 notification
- **MINOR** (0.2.0): new features, non-breaking extensions — requires Core Contributor consensus
- **PATCH** (0.1.1): bug fixes, clarifications — requires 1 Core Contributor approval

Release tags are signed by the Protocol Architect with a GPG key published in the repository.

---

## Protocol Change Process

**Non-breaking changes** (clarifications, additional examples, new open issues):
- Pull request → Core Contributor review → merge

**Breaking changes** (architecture, schema, analytical primitives):
1. Open a GitHub Issue labelled `breaking-change` with full rationale
2. 14-day comment period for community and Taler ecosystem feedback
3. Protocol Architect decision with written rationale
4. BIS/TC84 notification if the change affects the standardisation draft
5. CHANGELOG entry with migration guidance

---

## Relation to BIS/TC84 Standardisation

The open source repository and the BIS/TC84 standardisation track are parallel and complementary:

- The repository is the **technical reference** — it moves faster and contains implementation detail
- The BIS/TC84 draft is the **technology-neutral standard** — it abstracts implementation specifics

Protocol Architect coordinates between the two tracks. Breaking changes in the repository that affect the standardisation draft are communicated to TC84 within 30 days.

---

## Contact

CSDT / SolidarityLab
https://solidaritylab.eu
office@solidaritylab.eu
