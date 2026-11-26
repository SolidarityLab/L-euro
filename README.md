# L-euro — open protocol for digital entitlements

> **Status: draft v0.1 — for comment, not for implementation.**
> Български: [README.bg.md](README.bg.md)

L-euro is an open protocol for **entitlements to goods or services** that today
are issued as vouchers, coupons, tickets and discounts. One data model describes
every such right, and six separate roles serve it: **issuer, payer, holder,
acceptor, depositary and cover custodian**.

An integrator implements the protocol once and uses it for every programme. The
holder's rights sit in a pseudonymous **holder account** (*партида*) at the
depositary. To use a right, the holder scans a signed QR code or taps an NFC tag
shown by the supplier's own system and confirms with a passkey (fingerprint or
face on their own phone). No biometric data reaches the register, and no
third-party wallet is needed. Presentation from the European Digital Identity
Wallet (EUDI Wallet) is planned as an additional channel.

## Position

- **Entitlements are not money.** A right cannot be converted into money and is
  valid only in the acceptance network and for the class of goods written into it.
  E-money, payment accounts and money credit are out of scope.
- **The depositary is a dispatcher, not an issuer.** It keeps the register:
  holder accounts, supplier keys, offer hashes and the event log. It does not
  issue rights, identity or attributes, and it is not a party to the right.
- **The register is separate from the cover.** The money or capacity behind a
  programme is held by a separate, replaceable cover custodian (a bank, an
  operator or a fund), not by the depositary.
- **The acceptor sees the minimum:** form, class of goods, validity, and whether the
  balance covers the amount. Issuer and payer do not see the basket.
- **The anonymous transaction layer is separate from invoicing.** Settlement and
  e-invoices to the payer use only signed aggregates per supplier and period,
  never holder accounts.
- **Every event is recorded.** Reporting to an authority is an extract of the
  event record, not a separate periodic report.
- **A thin core.** The protocol stops at the Offer API: what the depositary has to
  verify. Catalogues stay with suppliers. Recipe books, booking, stock and till
  software are partner products on top of the API. L-euro does not issue fiscal
  receipts; suppliers keep their certified tills.
- **Software first, standard second.** The project writes and publishes the
  specification itself under an open licence. Standardisation (BIS, a CEN
  Workshop Agreement, or a working group at an open-source foundation such as
  Eclipse) is a legitimation layer: the input is working software, the output is
  a standard.

## What is in this repository

| Path | Content | Licence |
|---|---|---|
| [`spec/`](spec/) | Protocol specification (Markdown) | CC BY 4.0 |
| [`schemas/`](schemas/) | JSON Schemas: entitlement, redemption request, event | EUPL 1.2 |
| [`examples/`](examples/) | Example records | EUPL 1.2 |
| [`docs/`](docs/) | Position paper and notes | CC BY 4.0 |
| [`GOVERNANCE.md`](GOVERNANCE.md) | How the protocol is governed (draft) | CC BY 4.0 |

## Relation to other work

- **EUDI Wallet / ARF:** presentation from the EUDI Wallet is a planned channel
  (spec §7.1, channel D). L-euro does not issue PID or attribute attestations;
  the balance always stays in the register.
- **GNU Taler and payment systems:** L-euro is distinct from them and open to
  integration. Settlement to the acceptor can run over any payment rail.
- **NGI / NLnet conventions:** used as a reference for repository and licensing
  practice.

## Earlier work in this repository

The folder [`parents/`](parents/) holds the earlier DTEP series (June 2026):
DTEP-S (social layer) and DTEP-F (fiscal layer). They are kept unchanged for
reference as predecessors of L-euro. They are not part of the L-euro
specification and are not normative for it.

## Licence

- Specification text and documentation: [CC BY 4.0](LICENSES/CC-BY-4.0.txt)
- Schemas, examples and code: [EUPL 1.2](LICENSES/EUPL-1.2.txt)

See [LICENSE](LICENSE) for the split. Anyone may implement the protocol without fees.

## Contributing and citing

- Comments and proposals: see [CONTRIBUTING.md](CONTRIBUTING.md).
- To cite this work, use the DOI of the release (see [CITATION.cff](CITATION.cff)).

## Maintainer

Maintained by **Center for Solidarity Digital Transformation Association** (ЦСДТ, Център за солидарна дигитална трансформация), Sofia, ЕИК 208569411,
a member of the Bulgarian Institute for Standardization (BIS).
Contact: office@solidaritylab.eu · https://solidaritylab.eu/
