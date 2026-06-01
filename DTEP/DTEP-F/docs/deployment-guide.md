# DTEP-F Deployment Guide

**Version:** 0.1-draft
**Status:** Specification in progress
**Date:** 2026-06-01
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document provides guidance for organisations deploying DTEP-F Corner 5 infrastructure. It covers participant roles, minimum requirements per deployment scenario, the upgrade path, and the Bulgarian national reference deployment.

For the full protocol specification see [spec/protocol-overview.md](../spec/protocol-overview.md).
For security requirements see [docs/threat-model.md](threat-model.md).
For GDPR compliance requirements see [docs/gdpr-analysis.md](gdpr-analysis.md).
For conformance requirements see [spec/conformance-testing.md](../spec/conformance-testing.md).

---

## 2. Deployment Scenarios

DTEP-F supports four deployment scenarios with increasing institutional coverage. Each is independently viable. No scenario requires all participants simultaneously.

### Scenario 1 — Full chain (real-time)

All components operational: Peppol Access Point → Corner 5 Middleware → Taler Exchange → DRRDB → Central VIES → Analytical Layer.

DRR records flow in real time. Analytical primitives operate continuously. Taler B2B payment interface available.

**Minimum requirements:**
- Corner 5 Middleware: DTEP-F reference implementation; TLS 1.3 endpoint
- Taler Exchange: institutional instance with DTEP commit endpoint (v0.2)
- DRRDB: hybrid graph/relational instance with Taler auditor protocol
- Central VIES: VIES Adapter with current API compatibility

### Scenario 2 — Batch mode (offline Corner 5)

Corner 5 Middleware operates offline. DRR records accumulate locally and are transmitted to DRRDB in batches. Taler Exchange signing executes on reconnection.

**Minimum requirements:**
- Corner 5 Middleware: local storage with signed batch export
- Taler Exchange: available for periodic batch signing
- DRRDB: batch import endpoint

### Scenario 3 — Legacy Peppol input adapter

Existing Peppol Access Point without modification. DTEP-F adapter normalises the AS4 stream before Layer 3. Lowest barrier to entry — a single accredited provider can deploy without waiting for institutional adoption.

**Minimum requirements:**
- Legacy Peppol Access Point: any AS4-compliant implementation
- DTEP-F adapter: format normalisation layer

### Scenario 4 — Analytical layer only

Existing DRR data from a legacy system imported as DTEP-F public objects. Analytical layer activates immediately. Full chain enabled incrementally.

**Minimum requirements:**
- Legacy DRR data: any structured format with M1–M5 equivalent fields
- DTEP-F import tool: legacy format adapter

---

## 3. Upgrade Path

```
Single provider, legacy AP (Scenario 3)
        │
        │ add DRRDB + Taler Exchange
        ▼
Batch mode deployment (Scenario 2)
        │
        │ add real-time connectivity
        ▼
Full chain national sandbox (Scenario 1)
        │
        │ replicate specification and adapter
        ▼
Cross-border deployment
```

Records generated at each stage remain valid at all subsequent stages. No retroactive migration required.

---

## 4. Corner 5 Middleware Requirements

### Minimum hardware

- Any Linux server (Ubuntu 22.04 LTS or equivalent)
- TLS 1.3 termination (nginx or equivalent)
- Minimum 4 GB RAM for batch processing
- No biometric hardware required (fiscal protocol only)

### Network requirements

- Inbound: Peppol AS4 from accredited Access Points
- Outbound: Taler Exchange HTTPS endpoint
- Outbound: DRRDB HTTPS endpoint
- Zero-retention policy: no EN 16931 XML stored after Exchange submission

### Zero-retention enforcement

Corner 5 Middleware must not retain EN 16931 XML after transmission to Taler Exchange. Implementation must:
- Process invoice in memory only
- Transmit to Exchange immediately on receipt
- Confirm Exchange acknowledgement before responding to Peppol AP
- Log only M0 + timestamp + status — no invoice content

---

## 5. Taler Exchange Requirements

### Institutional deployment

- Ed25519 master key pair on HSM (required for production)
- DTEP commit endpoint (v0.2 — see docs/taler-integration-notes.md)
- Signing key rotation policy aligned with tax evidence retention requirements
- Signing key archive for long-term verification

### Minimum viable deployment (sandbox)

- Software-only key storage acceptable for sandbox phase
- Standard Taler Exchange instance with DTEP extension

---

## 6. DRRDB Requirements

### Database

- Hybrid graph/relational architecture (see spec/drrdb-layer.md Section 3)
- Reference configuration: Apache AGE over PostgreSQL
- Append-only enforcement at database level
- Taler auditor protocol integration

### API

- Public query endpoint per OpenAPI specification (schema/openapi.yaml)
- Protected audit endpoint with eIDAS 2.0 credential verification
- VIES Adapter for Central VIES compatibility

---

## 7. Bulgarian National Reference Deployment

The reference deployment context for DTEP-F v1.0 is the Bulgarian Peppol ecosystem.

| Role | Institution | System |
|---|---|---|
| Peppol Authority | НАП (National Revenue Agency) | e-Invoice.bg |
| Corner 5 Middleware | CSDT reference implementation | DTEP-F v1.0 |
| Taler Exchange | To be determined in Period 2 | Institutional instance |
| DRRDB | CSDT reference implementation | Apache AGE / PostgreSQL |
| Central VIES | EC DG TAXUD | VIES Adapter |

**Entry point for sandbox (Period 3):** Scenario 3 — legacy AP adapter for e-Invoice.bg. НАП does not need to modify its existing Peppol infrastructure. DTEP-F adapter accepts the existing AS4 stream.

**Upgrade trigger:** НАП implements native Corner 5 endpoint → Scenario 1.

---

## 8. Security Checklist

Before operational deployment:

- [ ] Taler Exchange master key on HSM; rotation policy defined
- [ ] Corner 5 Middleware zero-retention verified by audit
- [ ] TLS certificates valid and auto-renewal configured
- [ ] DRRDB append-only enforcement verified
- [ ] Audit Request authorisation protocol documented and tested
- [ ] KZLD consultation completed (Bulgarian deployment)
- [ ] DPIA completed by controller institution
- [ ] Incident response procedure defined for Exchange key compromise
- [ ] Conformance testing completed per spec/conformance-testing.md

---

## 9. Open Issues

- [ ] Corner 5 Middleware TEE deployment specification for high-security contexts (v0.2)
- [ ] DTEP commit endpoint specification for Taler Exchange (v0.2)
- [ ] DRRDB technology selection and benchmarking (v0.2)
- [ ] VIES Adapter API version compatibility matrix (v0.3)
- [ ] iOS deployment considerations for Taler wallet B2B interface (v0.3)
