# DTEP-S — Digital Transaction Evidence Protocol: Social Layer

> **Status:** Specification in progress | NGI Zero Commons Fund proposal submitted June 2026

DTEP-S is an open protocol specification and reference implementation for cryptographically verifiable delivery of social entitlements to digitally excluded beneficiaries — without requiring the beneficiary to possess any device.

## The Problem

Existing digital identity infrastructure (EUDIW, W3C VC ecosystems) structurally assumes a Holder with a smartphone. Persons under temporary protection, socially vulnerable individuals, and homebound persons are excluded from this infrastructure by design — not by choice.

At the same time, institutions issuing entitlement rights (social protection agencies, humanitarian programme administrators) and providers delivering goods and services have no machine-verifiable link between:

```
Right → Identification → Act of Delivery → Payment
```

The absence of this link generates systemic audit failures documented by the European Court of Auditors and national audit bodies across multiple Member States.

## What DTEP-S Does

DTEP-S defines the missing protocol layer connecting these four elements into a continuous, verifiable, auditable chain — designed to work with **any form of holder identification**:

- Biometric (fingerprint via merchant-side scanner)
- QR-based (physical card issued by institution)
- Documentary (identity document + central lookup)
- Digital wallet (W3C VC / EUDIW, where available)

The protocol is applicable to any domain where an institution issues a right, a provider realises it, and an auditor verifies the chain: humanitarian accommodation, social deliveries, school canteens, healthcare services, or any subscription/fund-based model for authorised access to goods and services.

## Architecture Overview

```
ISSUER (Institution)
e.g. Agency for Social Assistance
        │
        │ issues W3C VC 2.0 entitlement credential
        │ (stored in wallet, QR card, or central registry)
        ▼
HOLDER (Beneficiary)
No device required
        │
        │ presents credential at delivery point
        │ (biometric / QR / document / lookup)
        ▼
VERIFIER (Provider / Merchant)
e.g. accommodation provider, food delivery
        │
        │ verifies credential
        │ biometric match in TEE → atomic signing
        │ generates redemption event
        ▼
EVIDENCE LAYER (DTEP-S core)
Cryptographically signed delivery proof
        │
        │ audit trail → settlement
        ▼
AUDITOR (Institutional oversight)
e.g. Ministry of Tourism / Ministry of Finance
```

## Biometric Pipeline

For device-independent holder verification, DTEP-S defines an open biometric verification pipeline:

```
3× fingerprint scan
        ↓
Tensor RPCA (noise separation)
        ↓
Fourier-Mellin transform (rotation/scale normalisation)
        ↓
Neural feature extractor (verification vector)
        ↓
TEE: cosine similarity match
        ↓
[match] → merchant device signs redemption event
[no match] → signing capability not released
```

Enrolled templates are stored as one-way transformed vectors — no centralised biometric database, no raw biometric reconstruction possible.

## Relation to Existing Standards

| Standard / Initiative | Relation to DTEP-S |
|---|---|
| W3C VC 2.0 | DTEP-S uses W3C VC as credential format |
| eIDAS 2.0 / EUDIW | DTEP-S is a device-independent complement |
| ISO/IEC 18013-5 (mDL) | Referenced for proximity presentation |
| DC4EU (LSP social security) | DTEP-S extends with delivery evidence layer |
| EN 16931 / DTEP-F | Sibling protocol for fiscal layer |

## Repository Structure

```
dtep-s/
├── README.md                  ← this file
├── LICENSE                    ← EUPL-1.2
├── spec/
│   ├── protocol-overview.md   ← formal protocol model
│   ├── credential-schema.md   ← W3C VC entitlement credential
│   ├── presentation-flows.md  ← all holder presentation paths
│   ├── redemption-event.md    ← delivery proof specification
│   └── audit-trail.md         ← evidence chain and settlement
├── schema/
│   ├── entitlement-credential.json
│   ├── redemption-event.json
│   └── audit-record.json
├── diagrams/
│   ├── protocol-chain.mermaid
│   ├── system-actors.mermaid
│   ├── biometric-pipeline.mermaid
│   └── deployment-scenarios.mermaid
└── docs/
    ├── gdpr-analysis.md
    ├── threat-model.md
    └── deployment-guide.md
```

## Real-World Context

The immediate deployment context is Bulgaria's third humanitarian accommodation programme for persons under temporary protection (Council Directive 2001/55/EC):

- **Issuer:** Agency for Social Assistance — maintains beneficiary case files
- **Verifier:** Ministry of Tourism-accredited accommodation providers
- **Auditor:** Ministry of Tourism / Ministry of Finance
- **Governance:** Council of Ministers decisions

The absence of a verifiable protocol between these actors has generated documented audit failures affecting tens of thousands of beneficiaries and hundreds of millions of euros in programme funds.

The identical structural problem exists for social delivery programmes to homebound and vulnerable persons administered by the Agency for Social Assistance.

## Background

Council Directive 2001/55/EC was activated for the 
first time in its history in March 2022, in response 
to displacement from Ukraine. Over 100,000 persons 
accessed humanitarian support through Bulgaria alone.

Four years later, the administrative chain between 
the institution assessing the right and the institution 
paying for delivered support remains unconnected by any 
verifiable protocol. The result is documented by the 
European Court of Auditors and the Bulgarian National 
Audit Office: systemic discrepancies, thousands of 
unresolved provider objections, and funds absorbed by 
the national budget due to the impossibility of 
auditable delivery proof.

The problem is architectural, not administrative. 
The four elements of the chain — Right, Identification, 
Act of Delivery, Payment — are implemented in 
non-communicating systems designed for different 
purposes. Each corrective measure adds a new 
administrative layer without removing the old one.

DTEP-S addresses the architectural root, not the 
administrative symptom. It defines the missing protocol 
layer connecting these four elements into a continuous, 
verifiable, auditable chain — designed to work with or 
without beneficiary devices, and to function under 
partial institutional adoption.

## Funding

This project is submitted to the **NGI Zero Commons Fund** (13th call, deadline June 1, 2026) by the **Centre for Solidary Digital Transformation (CSDT)**, a Bulgarian public benefit association and member of the Bulgarian Institute for Standardisation (BIS).

- Applicant organisation: CSDT / SolidarityLab (EIK 208569411)
- Protocol Architect: Valeri Kostov
- Mathematics / Architecture: Nikola Obreshkov
- Backend / DevOps: Valentin Ivanov

## Standardisation

Protocol outputs will be submitted as a standardisation contribution to the Bulgarian Institute for Standardisation (BIS) with the aim of subsequent proposal to CEN/CENELEC.

Relevant W3C work item: [Verifiable Credentials over Wireless](https://github.com/w3c-ccg/community/issues/251) (W3C Credentials Community Group, July 2025).

## License

[EUPL-1.2](LICENSE) — European Union Public Licence v1.2

Compatible with GPL, LGPL, AGPL. Legally valid across all EU official languages.

## Contributing

The project is in specification phase. Contributions, reviews, and issue reports are welcome — particularly from implementers in the humanitarian, social protection, and digital identity domains.
