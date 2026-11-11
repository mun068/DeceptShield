# G0 / B1 Contract review — evidence and approval record

**Status: PROPOSED, awaiting supervisor/team decision.** This document is a review artifact, not an implemented feature.

| Gate | Reviewer decision | Evidence required |
| --- | --- | --- |
| R-01/R-02/R-03 scope unchanged | Pending | GP1 rule-pack alignment |
| Custom exact-body HMAC authenticated envelope | Pending | Synthetic test vectors; secure key registry design |
| JSON size, duplicate keys, metadata allowlist | Pending | Bounded parser tests |
| UTC freshness +/- 300 sec and coverage gaps | Pending | Clocks/offline retry test policy |
| Imported OpenCanary occurrence provenance | Pending | Registered collector and immutable capture identifiers |
| Raw accepted bytes and durable processing job | Pending | PostgreSQL schema and crash tests |
| Grouping-key first-insert race | Pending | Concurrent 20-event replay |
| Ed25519 full export and external key verification | Pending | Adversarial offline verifier tests |
| RBAC at API/object level | Pending | Endpoint permission test matrix |
| 40 Core scenarios independent of extensions | Pending | Versioned corpus/holdout |

## What offline tests do prove

Contract spike helpers reject altered signed bytes, duplicated JSON members, unknown keys, unsupported event types, overly large bodies, unsafe HTTP metadata and out-of-window timestamps for the tested synthetic examples. Occurrence tuple examples distinguish repeated import lines by immutable ordinal.

## What these tests do not prove

They do not demonstrate a deployed ingest API, trusted TLS, registered real sensors, durable event/job commits, crash safety, real OpenCanary parsing, privacy policy enforcement across logs, incident grouping or real attack detection.

## Approval metadata (fill in after review)

- Supervisor decision: PENDING
- Team decision: PENDING
- Date: PENDING
- Approved contract version: PENDING
- Changed GP1 requirement identifiers: PENDING
- Known exceptions and residual risk: PENDING
- Test evidence/build SHA: PENDING

No live ingestion endpoint should be added before this gate is documented.
