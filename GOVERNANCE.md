# Governance (draft)

> **Status: proposed.** The bodies described here do not exist yet. Until the
> Implementers' Council is formed, ЦСДТ acts as interim maintainer under the
> rules below.

## Principles

1. **Open to all on equal terms.** Any organisation or person may become an
   implementer or a maintainer under the same conditions.
2. **No fees.** Implementing the protocol requires no licence fee or membership.
3. **Neutrality.** The maintainer has no veto and no commercial preference for
   any integrator, operator or issuer.
4. **Software first.** Changes are accepted with a working implementation or a
   test where possible.

## Roles

| Body | Who | Does |
|---|---|---|
| Implementers' Council | One seat per organisation with a conformant or in-progress implementation | Accepts changes to the specification by rough consensus; falls back to a 2/3 vote |
| Protocol Maintainer | Elected by the Council for a fixed term (proposed: 2 years) | Runs the work, edits, cuts versions. No veto. |
| Contributors | Anyone | Open issues and pull requests, comment on drafts |

Interim: ЦСДТ is the Protocol Maintainer until the Council holds its first
election, and commits to hand over within [TODO: e.g. 12 months] of the
Council forming.

## Decision process

1. A proposal is opened as an issue or pull request.
2. A comment period of at least 14 days applies to normative changes.
3. The Council records consensus or votes. Decisions are logged in the PR.

## Versions

- `v0.x`: drafts, may change without notice.
- `v1.0`: first stable version, after a pilot with several implementers.
- Semantic versioning applies to schemas.

## Relation to standardisation

The specification may be submitted as input to BIS (as a standardisation
document or technical specification), a CEN Workshop Agreement or a working
group at an open-source foundation such as Eclipse. The content and status of any
resulting standard are decided in that procedure, and the project accepts the
changes of its consensus. This document is not part of any standard.

## Changing this document

Changes to GOVERNANCE.md follow the decision process above, with a 30-day
comment period.
