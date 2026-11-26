# L-euro Protocol Specification — v0.1 (draft)

- **Release:** 0.1.0-draft, 2026-11-26 (specification text v0.1; schema field `"v": "0.1"`)
- **Status:** Working draft for public comment. Not stable. Sections marked
  *TODO* are placeholders.
- **Editor:** Center for Solidarity Digital Transformation Association (CSDT), Sofia, Bulgaria, UIC 208569411
- **Licence:** CC BY 4.0 (text). Schemas referenced here are under EUPL 1.2.
- **Version history:** see [CHANGELOG.md](../CHANGELOG.md)

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 [RFC 2119] [RFC 8174]
when, and only when, they appear in all capitals, as shown here.

L-euro is not related to the digital euro and is not a currency.

## 0. Structure: protocol layers

This specification is the single normative source for the L-euro protocol.
Other documents (position paper, presentations, READMEs) summarise it and
refer to a version of it.

| Layer | Content | Where |
|---|---|---|
| P0 Model | forms, roles, attributes, cover modes | §1–5, `schemas/entitlement.schema.json` |
| P1 Register (holder accounts, *партида*) | accounts, events, idempotency, extracts for authorities | §6, `schemas/event.schema.json` |
| P2 Offers | the acceptor's catalogue and signed offer versions; `offerHash` | §8 (informative in v0.1) |
| P3 Presentation | channels A–D, passkey, evidence | §7, `schemas/redemption-request.schema.json` |
| P4 Cover, settlement and invoicing | cover custodian separate from the register; payment rails; e-invoicing | §9 |
| P5 Interfaces | APIs for issuer, acceptor and authority | *TODO (v0.2)* |
| Cross-cutting | conformance, security and privacy, governance | §10–11, GOVERNANCE.md |

## 1. Scope

This specification defines a common data model, lifecycle and roles for
**entitlements** (rights to a performance): claims of a holder against an
acceptance network for a defined class of goods or services, covered by a
payer. An entitlement is not money: it MUST NOT be convertible to money
unless the issuing programme explicitly allows it.

Out of scope: electronic money, payment accounts, money credit, issuance of
identity (PID) or other attributes, holding of cover by the depositary (§4),
fiscal receipts, and the acceptor's catalogue, stock and sales systems (§8).

## 2. Terms and definitions

| Term | Definition |
|---|---|
| Entitlement | A right of a holder to receive goods or services of a defined class from an acceptance network, covered by a payer. |
| Form | One of: `voucher`, `coupon`, `ticket`, `discount`. |
| Programme | The legal or contractual regime under which an entitlement is issued. |
| Cover | The value or capacity that secures an entitlement. |
| Holder account (*партида*) | A pseudonymous account of a holder at the depositary. It holds the holder's entitlements, their balances and the holder's passkey public keys. It is not a payment account within the meaning of Directive (EU) 2015/2366. |
| Depositary | The role that keeps the register: holder accounts, acceptor keys, offer hashes and the event log. It acts as a dispatcher. It does not issue entitlements, identity or attributes, does not hold the cover, and is not a party to the entitlement. |
| Acceptor (supplier) | The party that delivers goods or services against an entitlement. "Supplier" is used as a synonym in informative text. |
| Cover custodian | The role that holds the cover of a programme (funds or capacity), for example a bank, a payment institution, an operator or a public fund. It is separate from the depositary and replaceable. |
| Offer | An acceptor's promise of specific goods or a service at a price, published in the acceptor's own system. |
| Offer version | An immutable, signed text of an offer. Its hash (`offerHash`) is what the holder confirms and what the event log records. |

*TODO: align terminology with EUDI ARF and with a legal review of the word "depositary"; Bulgarian–English glossary.*

## 3. Forms

| Form | What is promised | Unit | Divisible |
|---|---|---|---|
| Voucher | Value in a class of goods, at many acceptors | EUR | yes |
| Coupon | One portion of a normed good, at one acceptor | count | no |
| Ticket | A place at an event with set time and place | count | no |
| Discount | A lower price on purchase | percent or EUR | no |

## 4. Roles

| Role | Function |
|---|---|
| Issuer | Creates the entitlement and is responsible for it. |
| Payer | Provides the cover. One or more, with shares, including in kind. |
| Holder | Holds and uses the entitlement. MAY act through a representative or as a group. |
| Acceptor | Delivers the goods or service against the entitlement. |
| Depositary | Keeps the register (holder accounts, keys, offer hashes, events). Does not hold the cover. |
| Cover custodian | Holds the cover of a programme and pays acceptors at settlement. Defined per programme, not per entitlement. |

One party MAY hold more than one role. Implementations MUST keep the roles
separable in the data. The depositary and the cover custodian SHOULD be
different parties; where one party holds both roles, the register and the
cover MUST be kept in separate systems and accounts, so that either can be
replaced without changing the other.

## 5. Data model

The minimum attribute set has 22 attributes in 7 groups. The normative schema
is [`schemas/entitlement.schema.json`](../schemas/entitlement.schema.json).

| Group | Attribute | Required |
|---|---|---|
| Identity | `id`, `form`, `programme` | yes |
| Parties | `issuer`, `payers[]`, `holder` (reference to the holder account), `acceptanceNetwork` | yes |
| Subject | `unit`, `nominal` / `balance`, `goodsClass`, `divisible` | yes |
| Conditions | `validFrom` (event: loading to holder), `validUntil`, `transferable` / `convertible` | yes |
| Cover | `coverMode` (`prepaid`, `guaranteed`, `creditLine`, `capacity`), `remainderRule` | yes |
| Regime | `taxTreatment` | optional |
| Proof | `status`, `signature`, `revocationUri` | yes |

`creditLine` means a credit line of the payer towards the cover custodian; no
credit is extended to the holder.

*TODO: choice of goods classification (COICOP is proposed) and its level of detail.*

## 6. Lifecycle and events

Every entitlement passes through the same eight steps (nine event types, as
`expire` and `revoke` are separate), and each event MUST be recorded
separately:

1. `request` (recorded even if no entitlement is issued)
2. `issue`
3. `load` — validity starts here
4. `present`
5. `redeem`
6. `settle` (optional under capacity cover)
7. `expire` or `revoke`
8. `remainder`

Reporting to a competent authority SHOULD be produced as an extract of the
event log.

### 6.1 Event record (draft)

The normative schema is [`schemas/event.schema.json`](../schemas/event.schema.json).

- The event log is append-only. An event MUST NOT be changed or deleted;
  a correction is a new event that refers to the earlier one.
- Every event MUST carry an `eventId`, the entitlement, the holder account
  (as a pseudonymous reference), a per-account sequence number `seq`, and
  `prevHash`, the hash of the previous event of the same account. The log of
  one account is therefore a hash chain.
- A repeated request with the same idempotency key (for `redeem`, the
  `nonce` of the redemption request) MUST return the original result and
  MUST NOT create a second debit.
- A `redeem` event MUST carry the evidence listed in 7.6.

*TODO: ordering across accounts; return and cancellation of a redeemed offer
(not covered by the eight events); retention periods.*

## 7. Presentation and selective disclosure

At presentation the acceptor MUST be able to verify form, goods class,
validity and whether the balance covers the amount, and SHOULD learn nothing
else about the holder, issuer or payer.

The balance is mutable and is recorded by the depositary. Every presentation
channel below is therefore an *online* check against the depositary, except
the offline fallback in 7.5.

### 7.1 Channels

| Channel | Direction | Holder steps | Status in v0.1 |
|---|---|---|---|
| A. Acceptor-presented request (QR or NFC tag) + holder passkey | acceptor → holder | scan or tap, then user verification | primary |
| B. NFC card emulation by the holder app | holder → acceptor terminal | tap, then user verification | optional |
| C. Holder-presented signed code (barcode / QR) | holder → acceptor | show code | fallback, offline |
| D. EUDI Wallet presentation (OpenID4VP) | holder → acceptor | wallet consent | future, *TODO* |

Implementations MUST support channel A. Third-party wallets (e.g. Google or
Apple Wallet passes) MAY be offered as display surfaces for channel C but are
not a source of truth for the balance.

User verification means the device's own check: biometric or device PIN
(WebAuthn `userVerification: "required"`). Emergency access with an external
sensor is a research topic outside this specification
([docs/research-emergency-access.md](../docs/research-emergency-access.md)).

### 7.2 Holder authentication (passkey)

- When an entitlement is loaded (`load`), the holder registers a WebAuthn
  credential (passkey) bound to the holder account (*партида*) at the depositary.
- The private key and any biometric data MUST stay on the holder device.
  The depositary MUST store only the public key, the credential ID and the
  signature counter. It MUST NOT store biometric templates or hashes of them.
- The level of assurance of the holder's identity is set by the issuer at
  enrolment. The passkey only proves that the same holder is present later.
- Programmes that need it MAY require device-bound (non-synced) credentials
  and MAY require authenticator attestation.

### 7.3 Acceptor-presented redemption request (channel A)

The acceptor's own system (point of sale, booking or records system) creates a
**redemption request** for the specific goods or service. It shows the request
as a QR code or writes it to an NFC tag (NDEF URI record). Both carry the same
payload. The normative schema is
[`schemas/redemption-request.schema.json`](../schemas/redemption-request.schema.json).

A request MUST contain:

- `acceptor` – identifier registered at the depositary;
- `offer` – the acceptor's item reference, its version, and `offerHash`, the
  SHA-256 hash of the canonical offer text that the holder sees;
- `amount` and `unit`;
- `goodsClass` of the offer;
- `nonce`, `issuedAt` and `expiresAt` (a short validity window, RECOMMENDED
  120 seconds or less);
- `acceptorSignature` – a JWS with detached payload (RFC 7515, Appendix F) over
  the JCS (RFC 8785) serialisation of the request object without the
  `acceptorSignature` member, made with a key the acceptor registered at the
  depositary.

Flow:

1. The holder scans the QR or taps the tag. The URI opens the L-euro app
   (Android App Link or iOS Universal Link) or, failing that, the web app.
2. The app sends the request to the depositary. The depositary verifies the
   acceptor signature, the time window, that the nonce is unused, and that the
   holder has an entitlement covering `goodsClass` and `amount`. It then
   returns the display text and a WebAuthn challenge.
3. The challenge MUST be `SHA-256(JCS(request) || entitlement id ||
   depositary nonce)`. The holder's signature thus binds this exact version
   of the offer at this moment.
4. The app shows acceptor, offer and amount. The holder confirms with user
   verification on the device (biometric or device PIN; WebAuthn
   `userVerification: "required"`).
5. The depositary verifies the assertion and debits the balance atomically.
   The `nonce` is the idempotency key. The depositary records a `redeem`
   event (see 7.6) and notifies the acceptor system by webhook.

Visibility at the depositary: the depositary MAY relay the display text of
the offer to the holder app, but it MUST retain only `offerHash` and the
fields in 7.6. It MUST NOT disclose offer contents or baskets to the issuer
or the payer.

*TODO: evaluate W3C Secure Payment Confirmation so that the browser itself
displays payee and amount before the biometric step.*

### 7.4 NFC card emulation (channel B)

The native app MAY act as a contactless card towards an acceptor terminal
(Android HCE; iOS host card emulation where the platform allows it in the
EEA). The terminal sends the redemption request over ISO 7816 APDUs. The rest
of the flow is as in 7.3. This channel does not depend on proprietary wallet
programmes such as Smart Tap.

*TODO: APDU profile and AID; platform entitlement conditions on iOS.*

### 7.5 Holder-presented signed code (channel C, offline fallback)

When the acceptor system has no screen or no network, the holder app shows a
short-lived code signed by the depositary (JWS or CWT in a QR or barcode).
The code covers a stated maximum amount. The acceptor verifies the signature
offline with the depositary's published key and uploads the redemption for
reconciliation later. Programmes MUST set the maximum offline amount and the
upload deadline.

### 7.6 Evidence in the event log

A `redeem` event produced by channels A or B MUST record:
`offerHash`, `acceptorSignature`, the WebAuthn `credentialId`,
`authenticatorData`, `clientDataJSON` and `signature`, the amount, and the
balance after the event. Together these show who confirmed which version of
which offer, and when.

### 7.7 Mapping to EUDI attestations

*TODO: mapping to an EUDI Wallet attestation format (SD-JWT VC / mdoc) for
channel D. The attestation states the right; the balance stays in the
register and is checked on presentation.*

## 8. Offers and the acceptor interface (informative in v0.1)

*This section summarises a working draft and is not yet normative. It is
proposed for v0.2.*

An acceptor (supplier) publishes what it offers in its own system. The
depositary does not hold catalogues: it learns only the acceptor's key, the
hashes of offer versions, the redemption requests and, under capacity cover,
the availability.

The proposed core (L-euro Offer API) has eight objects in four pairs. In each
pair the first object is lasting (agreed with the issuer before any
redemption) and the second is momentary (what the holder meets at a given
time and place).

| Pair | Lasting | Momentary |
|---|---|---|
| Who | `Supplier` (legal entity and its key) | `Location` (place of redemption) |
| Collection | `Catalogue` (all offers) | `Listing` (offers for a period: a menu, a festival programme) |
| Promise | `Offer` (identity of the offer) | `OfferVersion` (immutable, signed text with `offerHash`) |
| Measure | `Availability` (promised capacity) | `RedemptionRequest` (§7.3) |

Rules proposed for v0.2:

- Any change of text, price, portion or composition creates a new
  `OfferVersion` with a new `offerHash`. Old versions are kept, because
  `redeem` events refer to them.
- The canonical text is what the holder sees before confirming; the hash is
  computed over its JCS (RFC 8785) form.
- A multi-line redemption request (`lines[]`, `basketHash`) covers baskets and
  split payment, with the goods class checked per line.
- Domain modules (events and tickets, kitchens and coupons, shops and baskets)
  add fields on top of the core. A module that needs a new check at the
  depositary is a change to this specification, not to the module.

**Boundary of the protocol.** The protocol covers only what the depositary
must verify: signature, hash, goods class, amount, and availability under
capacity cover. How an offer is produced (recipes, stock, cost, sales,
invoices) is outside L-euro. Products built on the Offer API, such as a recipe
book for kitchens, a booking system, stock or till software, are separate
products of partners and reach the protocol only as `OfferVersion` and
`RedemptionRequest`.

*TODO (v0.2): `offer.schema.json`; extension of
`redemption-request.schema.json` for baskets; whether registering an offer
hash before redemption is mandatory for programmes with an offer whitelist.*

## 9. Cover, settlement and invoicing

*Principles for v0.1; details TODO.*

- **Cover is held by the cover custodian, not by the depositary** (§4). The
  depositary instructs settlement from the event log; the custodian pays.
- **Settlement is independent of the payment rail.** Payment to the acceptor
  MAY run over SEPA, an instant payment scheme, GNU Taler or any other rail.
- **The pseudonymous transaction layer (P1) is strictly separate from invoicing (P4).**
  The register (P1) records deliveries to pseudonymous holder accounts.
  Settlement (P4) receives only a signed aggregate per acceptor, programme,
  payer and period: number of redemptions, amounts per VAT rate and goods
  class, and a hash commitment (for example a Merkle root) over the `redeem`
  events of the period. Holder account identifiers, keys and individual
  timestamps MUST NOT cross into settlement or invoicing.
- **Invoices are issued at settlement, not by the register.** An e-invoice to
  the payer (EN 16931) is produced from the aggregate by a replaceable module
  or by the acceptor's own software.
- **Aggregation threshold.** A cell of the aggregate (acceptor, goods class,
  day) with fewer than *k* redemptions SHOULD be merged into a longer period.
  *TODO: value of k.*
- **No fiscal till.** L-euro does not issue fiscal receipts and is not sales
  management software in the sense of national fiscal rules. The acceptor's
  own certified till records the sale with the payment method "voucher /
  L-euro". Integration with till vendors is through an open module that
  creates and confirms redemption requests.

*TODO: cover modes per custodian; settlement cycle; reconciliation of channel C;
legal status of the custodian (limited network exclusion under Directive (EU)
2015/2366, art. 3(k), or e-money); VAT treatment (single- or multi-purpose
voucher under Council Directive (EU) 2016/1065); e-invoicing to public payers
under Directive 2014/55/EU.*

## 10. Conformance

*TODO: open conformance test suite; conformance classes per role.*

## 11. Security and privacy considerations

- No biometric data is stored in the register (§7.2).
- The depositary can link all redemptions of one holder account. L-euro v0.1
  offers pseudonymity towards acceptors, issuers and payers, not
  unlinkability towards the depositary.
- Event records in the register are pseudonymous personal data and MUST be
  protected accordingly (data protection by design). The aggregate passed to
  settlement SHOULD NOT allow re-identification (§9).
- Each layer uses its own keys. The settlement and invoicing layer has no key
  that links an aggregate to a holder account.

*TODO: threat model; key management; audit of the register.*

## Annex A. Open questions

- Goods classification and level of detail.
- Attestation format in the wallet; mutable balance vs immutable attestation.
- Synced vs device-bound passkeys per programme; iOS NFC entitlement conditions.
- Maximum offline amount and reconciliation rules for channel C.
- Legal status of the depositary and of the cover custodian; payment-services
  and e-money rules.
- VAT treatment of entitlements (single- or multi-purpose voucher).
- Whether payers accept an aggregate without a named list of beneficiaries,
  especially in social programmes.
- The name "L-euro" suggests a currency while the protocol insists rights are not money.
- Tickets and coupons are checked only against existing schemes; validation pending.
- `goodsClass` holds one code, while a meal voucher often covers several
  classes (e.g. COICOP 01.1 and 11.1).
- `status` has no value for a partly used divisible voucher; settlement is
  aggregated per period rather than per entitlement.

## Annex B. References

- RFC 2119 and RFC 8174 (BCP 14): key words.
- RFC 7515: JSON Web Signature. RFC 8785: JSON Canonicalization Scheme.
- W3C Web Authentication (WebAuthn) Level 3.
- OpenID for Verifiable Presentations 1.0; EUDI Wallet Architecture and
  Reference Framework (channel D, planned).
- Regulation (EU) 2024/1183 (eIDAS 2.0). Regulation (EU) 2016/679 (GDPR).
- Directive (EU) 2015/2366 (PSD2). Council Directive (EU) 2016/1065 (VAT on
  vouchers). Directive 2014/55/EU (e-invoicing in public procurement);
  EN 16931.
- Regulation (EU) 2024/903 (Interoperable Europe Act).
