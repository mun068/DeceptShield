# ADR-0002 — B1 working engineering baseline and pre-ingestion security fixes

**Date:** 2026-11-11  
**Status:** ADOPTED AS A WORKING IMPLEMENTATION DIRECTION (not a frozen wire contract; not deployed)  
**Decision scope:** Internal GP2 development planning. This record is not a supervisor approval, formal GP1 amendment, release acceptance, or proof that any API/data path is secure.

## Decision

Build **one vertical slice** first: HTTP Decoy R-02 -> authenticated event -> atomic PostgreSQL raw-event + pending-job commit -> one DB-backed worker -> deterministic incident correlation -> internal incident read model -> evidence verification. Add Canary File Agent R-01 and pinned OpenCanary adapter R-03 after the shared path is proven. Use a single-server Docker Compose modular monolith, FastAPI, PostgreSQL, one background worker, and later React/TypeScript. No Kafka, Kubernetes, multi-tenancy, AI scoring, broad SIEM integrations, or optional ReadData auditing in the Core critical path.

## Adopted working protocol choices (must be reflected in versioned schemas and tests before live ingress)

1. **Separate provenance classes.** HMAC custom-sensor events and imported OpenCanary acquisitions use distinct identities, policies, and data model boundaries. Imported OpenCanary logs must never inherit upstream cryptographic authenticity merely because their collector was authenticated.
2. **Custom-event envelope.** Retain `sensor_id`, `key_id`, stable UUID `source_event_id`, `observed_at`, `event_type`, `payload`, `schema_version`. Candidate wire version remains `1.0-candidate` until fixtures and migrations use a deliberately frozen identifier. Do not conflate it with the normalized API read-model version from GP1.
3. **HMAC.** HMAC-SHA256 on **exact received UTF-8 request body bytes**, lowercase hex MAC header, per-sensor manually provisioned keys. Validate a strict size bound, content type, JSON duplicate members, enabled registered sensor-key binding, active sensor status, **authorized event family**, allowed target IDs, timestamp and payload schema. The initial parser may read claimed sensor/key hints solely to select the secret; it must not trust them until the MAC passes. Use constant-time digest comparison and bounded generic auth failures.
4. **Size/time limits.** Use **8192 bytes as a provisional measurement-backed trial cap**, not an immutable GP1 fact. GP1's **+/-300 seconds** observed-time freshness applies to **new** custom events. Accepted events have immutable observed_at. Exact duplicate retransmissions after the freshness window may return an existing stable receipt **only after authenticating and matching an already-accepted event and byte digest**; they do not create a new record, job, or incident. Unseen stale arrivals are rejected and counted as a coverage limitation without storing the rejected secret-bearing body. Define key-revocation policy explicitly, including duplicate lookup behavior.
5. **Privacy at source.** HTTP decoy must generate allowlisted sensor-created telemetry **before signing**. No request bodies, query parameters, authorization data, cookie, session IDs, credential-bearing headers, or raw dynamic secret path segments. Include *configured/normalized* host and path/route identity (GP1 mentions host), method, response status, observed peer/source address when valid, decoy_id and observed time. Avoid trusting `X-Forwarded-For` except through explicitly configured trusted proxies. `decoy_id` MUST belong to the registered source; not merely be a syntactically valid UUID. Canary File Agent needs `asset_id` and an approved stable file/decoy identity for incident evidence; the detector still only claims modify/rename/delete.
6. **Durable idempotent intake.** PostgreSQL schema/migration contains registered sources, source keys (secret material external to DB as feasible), immutable raw acceptance record with bytes, digest and provenance, and `processing_job`. For new accepted events, commit **raw+digest+job in one transaction before HTTP 202**. Enforce unique (sensor_id, source_event_id). If already accepted with identical bytes/digest, return prior stable receipt (candidate HTTP 200); if same identity differs, reject/audit (candidate 409). Unavailable DB -> no acceptance receipt (503). Never retry writes in a way that creates duplicates. **Do not claim exactly-once processing without crash/replay evidence.**
7. **Worker and grouping.** One PostgreSQL-backed worker with bounded claim lease and retries. `FOR UPDATE SKIP LOCKED` may select jobs but **does not solve first-insert incident-key races**. Create/lock a stable rule-specific routing-key row in a DB transaction. Use fixed half-open `[t0,t0+300s)` incident grouping by R-01 sensor+asset, R-02 sensor+registered decoy_id, R-03 ingest_source+supported event-type; source IP is never attacker identity. Record immutable disposition per event. Do not slide the five-minute window when related events arrive.
8. **Security controls.** Keep the current host port bound to loopback for local tests; require TLS before remote sensors are connected. Apply ingress size/time limits and rate limits, private secrets, key disable/rotation procedures, structured secret-safe audit events, no credential-bearing error messages, no DB port published. Production deployment needs dependency/image pinning, an RBAC permission matrix enforced on the API, and endpoint/object tests; the current health-only container is not a production deployment.
9. **Evidence/export (later gate).** Retain accepted raw bytes with SHA-256 and export full allowed incident evidence with a signed Ed25519 manifest and an independent trusted-public-key offline verifier; do not claim nonrepudiation, sensor honesty or courtroom admissibility.

## What is wrong or incomplete in the current offline candidate

- **P0 — Cross-source type authorization missing:** the helper knows only `(sensor_id, key_id) -> bytes`. A key can authenticate a syntactically valid event from any supported family, even when that source should only emit HTTP or Canary File events. Add registered source type/allowed event-type binding and negative tests.
- **P0 — Trusted-target validation missing:** arbitrary well-formed `decoy_id` or `asset_id` is allowed. Bind target identifiers to approved source/configuration. Otherwise authenticated but misconfigured/compromised sensors can fabricate targets.
- **P0 — HTTP privacy contract incomplete:** existing `path` check removes `?`, `#`, CR and LF but still permits credentials in path segments or other control/escape sequences. Candidate lacks the GP1 `host` metadata. Move path normalization/secret masking into the decoy sensor and verify against registered routes; add adversarial fixture coverage.
- **P0 — No state or durability:** no actual API endpoint, active registry, rate limiting, TLS, database constraints, processing job, conflict detection, crash recovery, or incident storage. Existing offline test success cannot be used as evidence for these features.
- **P0 — Missing stale/duplicate policy:** a plain absolute freshness gate can reject an exact older already-accepted retransmission, conflicting with "stable duplicate receipt"; formalize the sequence described above and test it.
- **P1 — Reproducibility and CI parity:** local Windows bind-mount required ignoring Ruff `EXE002`, one PostgreSQL test was skipped locally, dependencies/images are range/tag based rather than fully locked, and a Starlette test-client deprecation warning exists.
- **P1 — Evidence and auth still absent:** API RBAC, source auditability, signed full evidence and independent verifier are future work, not partial implementations.

## Next scoped implementation PR (after schema/test fixture update)

1. Refine `custom_event.v1` fixtures and write failing tests for cross-source impersonation, unknown/disabled targets, tainted path segments, stale exact duplicate, duplicate JSON, invalid key, oversized body, and safe source-IP treatment.
2. Implement source/key/target registry and PostgreSQL migration with `raw_event` + `processing_job` and uniqueness constraints; test one-transaction rollback and race duplicates using dedicated CI PostgreSQL.
3. Wire an ingress endpoint **only after** those code tests pass; verify that the same body HMAC is checked without reserialization and that no acceptance response precedes the commit.
4. Run negative tests under DB failure, concurrent replay, rejected secret-bearing body, key revocation and crash/retry before committing the receipt contract as stable.
5. Preserve draft PR #1 / #5 review lineage; no unreviewed automatic merges to main.

## Acceptance criteria for the next gate

- [ ] Stable, documented event schema with source/target authorization and a reproducible fixture corpus.
- [ ] 100% of supported auth/payload negative cases rejected with no raw rejected sensitive payload stored.
- [ ] Exactly one accepted raw record and processing obligation per immutable custom source occurrence under concurrent same-ID replay.
- [ ] HTTP 202 only after successful atomic commit; deterministic stable receipt on matching retry; conflict on changed bytes.
- [ ] No event/job acknowledged when PostgreSQL is unavailable; recover processing after worker interruption.
- [ ] Successful dedicated PostgreSQL integration CI; portable local lint/test workflow documented.
- [ ] No production/live-detection claims before a real end-to-end isolated-lab scenario is demonstrated.

**References:** GP1 contract/three-rule design, internal B1 contract candidates, Issue #2, B1 test branch, OWASP Logging Cheat Sheet (https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html), PostgreSQL SELECT locking documentation (https://www.postgresql.org/docs/current/sql-select.html).
