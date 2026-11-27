# Changelog

## v0.1.1-draft — 2026-11-27

Position paper v0.2 (Bulgarian). The specification and schemas are unchanged.

- New section 5: how L-euro builds on existing standards. L-euro is framed as an
  interoperability profile with a small normative core (L-euro Core) and
  per-standard profiles, each implemented as an open-source module.
- Map of 26 elements against existing standards (annex A): 22 covered, four
  gaps (entitlement model, register semantics, channel A binding, settlement
  aggregate for e-invoicing).
- Section 4.10 extended: only the core is proposed for standardisation;
  sequence pilot → Rolling Plan via BDS → BDS SD or CWA; the specification
  stays under CC BY 4.0 / EUPL-1.2.
- Related initiatives (Rolling Plan, IETF SCITT, W3C SPC), open questions
  (PSR/PSD3) and next steps updated. Sections 5–9 are renumbered 6–10.

## v0.1.0-draft — 2026-11-26

First public draft for comment. Added:

- Specification v0.1: protocol layers P0–P5; four forms; six roles, with the
  depositary as a register (dispatcher) separate from the cover custodian;
  minimum attribute set (22 attributes in 7 groups); lifecycle and append-only,
  hash-chained event record; presentation channels (acceptor-presented QR or
  NFC request with holder passkey as primary, NFC card emulation, offline signed
  code, EUDI Wallet planned); principles for offers, settlement and invoicing;
  first security and privacy considerations.
- Three draft JSON Schemas (entitlement, redemption request, event) with
  examples.
- Position paper in Bulgarian; research note on emergency access.
- Governance and contribution rules (proposed), licences (CC BY 4.0 for text,
  EUPL-1.2 for schemas and code), REUSE metadata, citation metadata.
- `parents/`: the earlier DTEP-S and DTEP-F drafts, unchanged, for reference.
