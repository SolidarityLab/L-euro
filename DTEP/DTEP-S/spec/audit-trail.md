# DTEP-S Audit Trail Specification

**Version:** 0.1-draft  
**Status:** Specification in progress  
**Date:** 2026-06-01  
**Authors:** CSDT / SolidarityLab

---

## 1. Scope

This document specifies the audit trail mechanism for DTEP-S. The audit trail provides cryptographic proof of the integrity and completeness of the Redemption Event sequence — making it structurally impossible to delete, modify, or insert events retroactively without detection.

The audit trail is the protocol's answer to the structural gap between the Act of Delivery and the Payment elements of the chain at the Auditor level:

```
Right → Identification → Act of Delivery → Payment
                                               ↑
                                      Audit Trail
                                      validates here
```

The audit trail does not replace the individual Redemption Event proofs. It adds a second layer of integrity — the sequence itself is verifiable, not only individual events.

---

## 2. Design Principles

**Append-only** — events are added to the audit trail but never removed or modified. Any attempt to alter the trail is cryptographically detectable.

**Incremental verification** — any party holding the Auditor's public key can verify the integrity of the trail at any point without access to all preceding events.

**Tamper-evidence without central trust** — the Merkle structure makes it impossible for even the Auditor to modify historical records without invalidating the trail root, which is published periodically.

**Separation of concerns** — the audit trail proves sequence integrity. Settlement logic is outside the trail's scope and is implementation-defined.

**Offline compatibility** — trail construction tolerates gaps from offline Verifiers. Late-arriving events are appended in transmission order with declared latency metadata.

---

## 3. Merkle Tree Structure

The DTEP-S audit trail is an append-only Merkle tree where each leaf is a Redemption Event.

### 3.1 Leaf construction

Each leaf in the Merkle tree is constructed as:

```
leaf(n) = SHA-256(
    event.id
    || event.generatedAt
    || event.proof.proofValue
    || leaf(n-1).hash
)
```

The chaining of `leaf(n-1).hash` into each leaf makes the tree a hash chain — each leaf cryptographically binds all preceding leaves. This is equivalent to a Merkle-chained log, analogous to W3C Verifiable Credentials Data Integrity hash chaining and Certificate Transparency logs.

### 3.2 Tree construction

Leaves are grouped into batches. Each batch produces a Merkle root.

```
Batch B(k):
  leaves: [leaf(n), leaf(n+1), ..., leaf(n+m)]
  root: MerkleRoot(B(k))
  previousBatchRoot: MerkleRoot(B(k-1))
  batchIndex: k
  batchTimestamp: ISO-8601 datetime of root computation
```

The batch root is computed as a standard binary Merkle tree over the batch leaves. Uneven batches are padded with a null leaf (SHA-256 of zero bytes).

### 3.3 Trail root

The trail root is a signed document published by the Auditor at defined intervals:

```
DTEPTrailRoot
  id              urn:uuid — unique root document identifier
  auditor         auditor DID
  batchIndex      integer — index of this batch
  batchRoot       hex-encoded Merkle root of this batch
  previousRoot    hex-encoded trail root of previous batch
                  null for first batch
  eventCount      integer — cumulative event count
  firstEventId    urn:uuid — first event in this batch
  lastEventId     urn:uuid — last event in this batch
  generatedAt     ISO-8601 datetime
  proof           DataIntegrityProof signed by Auditor key
```

The trail root is the **public commitment** of the Auditor to the state of the trail at a given moment. Once published, it cannot be altered without invalidating the proof.

---

## 4. Publication and Anchoring

### 4.1 Publication interval

The Auditor publishes trail roots at a defined interval — recommended minimum: once per 24 hours during active programme operation. The interval is declared in the Auditor's configuration and must be consistent.

### 4.2 Anchoring

Trail roots should be anchored to an external verifiable registry to prevent Auditor-side tampering with the publication timestamp. Recommended anchoring options in order of preference:

```
1. BIS / national standardisation body registry
   (for programmes with formal institutional mandate)

2. OpenTimestamps (Bitcoin or Ethereum anchoring)
   — available as free public infrastructure

3. Issuer-countersigned root
   — Issuer signs the trail root alongside Auditor
   — mutual accountability without external dependency

4. Multi-party publication
   — trail root published simultaneously to
     Auditor, Issuer, and a designated third party
```

Anchoring mechanism is implementation-defined. The protocol requires that at least one anchoring mechanism is declared in the Auditor configuration and consistently applied.

### 4.3 Public registry

Trail roots should be published to a publicly accessible append-only log. This allows any party — including beneficiaries, providers, oversight bodies, or civil society — to independently verify that the audit trail has not been tampered with.

The public registry is implementation-defined. Minimum requirement: HTTPS-accessible, append-only, with roots retrievable by batch index and by date range.

---

## 5. Verification Procedures

### 5.1 Single event verification

To verify that a specific Redemption Event is included in the audit trail:

```
1. Obtain the event's leaf hash: leaf(n)

2. Obtain the Merkle proof for leaf(n):
   the sibling hashes along the path
   from leaf(n) to the batch root

3. Recompute the batch root from leaf(n)
   and the Merkle proof

4. Compare with published batch root
   for the batch containing event n

5. Verify Auditor signature on trail root document

6. Verify trail root anchoring (if applicable)
```

If all steps succeed: the event is confirmed as unmodified and included in the trail at the declared position.

### 5.2 Sequence completeness verification

To verify that no events have been deleted from a sequence:

```
1. Obtain all trail roots for the period

2. Verify each trail root signature

3. Verify previousRoot chain is unbroken
   from first to last batch

4. Verify eventCount is monotonically increasing

5. Verify firstEventId and lastEventId
   are consistent with event timestamps
   in adjacent batches
```

A gap in the previousRoot chain indicates either a missing batch (Auditor failure) or tampering.

### 5.3 Cross-Verifier completeness

To verify that events from a specific Verifier are complete:

```
1. Request Verifier's local event log
   (Verifier must provide on demand for audit)

2. Verify each event in Verifier log
   is present in Auditor trail

3. Flag any event present in Verifier log
   but absent from Auditor trail
   → potential transmission failure or suppression

4. Flag any event present in Auditor trail
   from Verifier's deviceId
   but absent from Verifier log
   → potential insertion attack
```

---

## 6. Trail Artifacts

### 6.1 Trail root document

Published by Auditor. Structure defined in section 3.3.

### 6.2 Merkle proof

Generated by Auditor on request for any event. Structure:

```
DTEPMerkleProof
  eventId         urn:uuid — the event being proven
  leafHash        hex — SHA-256 leaf hash of the event
  leafIndex       integer — position in batch
  batchIndex      integer — batch containing this event
  siblings        array of hex strings
                  sibling hashes along path to root
  batchRoot       hex — recomputed root (for verification)
  trailRootId     urn:uuid — trail root document this proof
                  corresponds to
```

### 6.3 Audit report

Produced by Auditor for a defined period. Structure:

```
DTEPAuditReport
  id              urn:uuid
  auditor         auditor DID
  period
    from          ISO-8601 date
    until         ISO-8601 date
  summary
    totalEvents         integer
    totalVerifiers      integer
    totalCredentials    integer
    anomalyFlags        integer
    batchesPublished    integer
  trailRootRange
    first         urn:uuid — first trail root in period
    last          urn:uuid — last trail root in period
  anomalies       array of anomaly records
                  see redemption-event.md section 8
  proof           DataIntegrityProof signed by Auditor key
```

The audit report is the primary settlement input document. It summarises the verified delivery evidence for the period and is the basis for Verifier reimbursement.

---

## 7. Offline and Late Event Handling

Events generated offline arrive at the Auditor after a delay. The audit trail handles late events as follows:

```
1. Late events are appended to the trail
   in order of receipt — not order of generatedAt

2. Each late event is tagged with:
   receivedAt    ISO-8601 datetime of receipt
   latencyDays   integer — days between generatedAt
                 and receivedAt

3. Events with latency exceeding Issuer-defined
   maximum queue window (default: 30 days)
   are flagged for manual review
   — not automatically rejected

4. Late events are included in the next
   scheduled batch — not in a retroactive batch

5. The Merkle proof for a late event correctly
   reflects its position in the trail
   (receipt order) — not its generatedAt position
```

This design preserves trail integrity while accommodating legitimate offline operation. The distinction between generatedAt and receivedAt is always visible in the trail.

---

## 8. Relation to Settlement

The audit trail produces verified delivery evidence. Settlement — the payment from Auditor to Verifier — is outside the audit trail's scope.

The audit report (section 6.3) is the handoff point: it summarises verified events for a period and is signed by the Auditor. What happens after the audit report is implementation-defined.

<!-- OPEN ISSUE: GNU Taler as settlement layer
     GNU Taler (https://taler.net) is a privacy-preserving
     payment protocol developed within the NGI ecosystem,
     with a built-in auditor component for financial
     consistency verification. The DTEP-S audit report
     could serve as input to a Taler-based settlement
     flow, where the Auditor initiates payment to
     accredited Verifiers using Taler coins backed by
     institutional funds. This would add provable
     financial auditability to the delivery evidence
     already provided by DTEP-S.
     Deferred to v0.4 — requires analysis of Taler
     merchant/exchange integration and GDPR implications
     of combining delivery evidence with payment records.
-->

---

## 9. Validation Rules

A trail root document is **protocol-valid** if and only if:

```
T1  id is present and follows urn:uuid pattern

T2  auditor is a resolvable DID

T3  batchIndex is a non-negative integer

T4  batchRoot is a valid hex-encoded SHA-256 hash

T5  previousRoot is present for all batches
    except the first (batchIndex = 0)

T6  eventCount is strictly greater than
    the eventCount of the previous batch

T7  generatedAt is present and valid ISO-8601

T8  proof.cryptosuite is "eddsa-rdfc-2022"

T9  proof.proofValue verifies against Auditor
    public key resolved from
    proof.verificationMethod

T10 batchRoot is recomputable from the events
    declared in firstEventId–lastEventId range
```

A trail root failing T9 must be rejected as potentially tampered. A trail root failing T10 indicates either missing events or incorrect batch construction.

---

## 10. Open Issues

- [ ] Anchoring mechanism selection and configuration schema (v0.2)
- [ ] Public registry API specification (v0.2)
- [ ] Batch size optimisation — events per batch vs. publication frequency (v0.2)
- [ ] Merkle proof format — binary vs. JSON encoding (v0.2)
- [ ] Cross-Issuer trail aggregation for multi-programme audits (v0.4)
- [ ] GNU Taler settlement integration — see section 8 comment (v0.4)
- [ ] Post-quantum hash function migration path (v0.5)
- [ ] Formal security proof of trail integrity under defined threat model (v0.9)

---

## References

- RFC 6962 — Certificate Transparency: https://datatracker.ietf.org/doc/html/rfc6962
- W3C Verifiable Credentials Data Integrity: https://www.w3.org/TR/vc-data-integrity/
- OpenTimestamps: https://opentimestamps.org
- GNU Taler: https://taler.net
- DTEP-S Redemption Event Specification: ./redemption-event.md
- DTEP-S Credential Schema Specification: ./credential-schema.md
- DTEP-S Protocol Overview: ./protocol-overview.md
