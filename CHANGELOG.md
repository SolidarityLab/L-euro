# Changelog

## v0.1.0-draft — 2026-MM-DD  [TODO: date of release]

- First public draft: scope, forms, roles, minimum attribute set (18 attributes
  in 7 groups), lifecycle, draft JSON Schema and one example.
- Governance and contribution rules proposed.
- Section 7: presentation channels. Acceptor-presented QR or NFC request with
  holder passkey (primary), NFC card emulation, offline signed code. Redemption
  request schema and example.
- Section 7.8 (research): emergency access with a certified external sensor.

### Consolidation before first release (2026-11-26)

- Section 0: map of protocol layers P0–P5; the specification is the single
  normative source.
- Roles: the depositary keeps only the register (holder accounts, keys, offer
  hashes, events) and acts as a dispatcher. New role **cover custodian** holds
  the cover; register and cover must be separable. Six roles instead of five.
- Holder is a reference to a pseudonymous holder account (*партида*), not to a
  wallet (`entitlement.schema.json`, example).
- Section 6.1 and new `schemas/event.schema.json` with a `redeem` example:
  append-only log, per-account hash chain, idempotency.
- Section 7.3: visibility rule for offer contents at the depositary.
- Section 8 (informative): offers and the acceptor interface, 8 objects in 4
  pairs, protocol boundary at the Offer API.
- Section 9: cover, settlement and invoicing principles; anonymous transaction
  layer separate from invoicing; no fiscal till.
- Section 11: first security and privacy considerations.
- Schema `$id` values changed from example.org URLs to URNs.
- README (EN/BG), CITATION.cff, .zenodo.json and the organisation profile:
  primary channel is the supplier's signed QR/NFC + passkey; EUDI Wallet is a
  planned channel; standardisation named as legitimation only.
- `docs/position-paper.bg.md`: position paper of ЦСДТ, draft.
- Maintainer data filled in from the registry (ЕИК 208569411) and the GitHub
  profile: legal name in Bulgarian and Latin, contact e-mail, website.
