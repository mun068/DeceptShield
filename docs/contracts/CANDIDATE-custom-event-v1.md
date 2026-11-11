# Candidate B1 contract: custom sensor events (NOT APPROVED)

**Status:** Proposed for GP2 supervisor/team review. This is an **offline prototype only** and must not be presented as a deployed secure ingress service.

## GP1 compatibility boundary

GP1 documents per-sensor HMAC-SHA256 keys; exact UTF-8 request-body bytes covered by MAC; claimed sensor ID/key ID/event ID/observation time/type/payload; a proposed +/- five-minute freshness check. The mandatory direct sources are Canary File Agent, HTTP Decoy, and OpenCanary; OpenCanary imported logs are **not** custom HMAC sensor messages. GP1 Core Canary File Agent is *modify, rename, delete*, **not read detection**. The rule grouping window is distinct from the request freshness window.

**Changes and decisions requiring approval:** the specific field vocabulary and event type strings, exact validation order, candidate maximum of 8192 bytes, envelope version identifier, payload allowlists, key lookup behavior, HTTP status/error codes and accepted-event durability protocol. The term `1.0-candidate` explicitly prevents treating this as finalized v1.

## Proposed custom JSON envelope

```json
{
  "schema_version": "1.0-candidate",
  "sensor_id": "da3b1c17-1bbb-47d8-8754-b00f4800822d",
  "key_id": "lab-v1",
  "source_event_id": "3b5f0fc1-13fa-416d-aa38-579a4bb8915b",
  "observed_at": "2026-11-11T09:00:00Z",
  "event_type": "http_decoy.request",
  "payload": {
    "decoy_id": "0e75d059-411a-4919-86fb-dfc5ac33dfe1",
    "method": "GET",
    "path": "/lab/canary",
    "status_code": 200,
    "source_ip": "192.0.2.10"
  }
}
```

All displayed identifiers, keys and addresses are **synthetic lab fixtures**. No live secret is committed.

## Candidate wire protocol (not implemented)

- Proposed endpoint: `POST /api/v1/sensor-events` over **TLS** in a constrained laboratory environment.
- Body: bounded UTF-8 JSON; mandatory fields exactly those shown above. Currently supported **candidate vocabulary**: `canary_file.modify`, `canary_file.rename`, `canary_file.delete`, `http_decoy.request`.
- Header: `X-DeceptShield-MAC` containing **lowercase hexadecimal HMAC-SHA256 over the exact received body bytes**. Do not reserialize before verification. The source/key values read from the body are *untrusted lookup hints* only until the MAC succeeds.
- Restrict content type and body length at gateway and application layer. Candidate bound is **8192 bytes** (not approved). Parse bounded UTF-8 JSON with strict duplicate-member rejection. On valid registry lookup, verify exact-byte MAC with constant-time comparison. Then validate schema, active key/source binding, event-type allowlist and observed-time freshness.
- Time policy candidate: UTC `Z` timestamp and absolute skew no greater than **300 seconds** from receiving server time. The observed time is never silently rewritten. Old offline retries must be rejected and produce an **observable coverage limitation**, to be specified separately.
- HTTP fields are an allowlist: stable `decoy_id`, method, query-free normalized path, response status, optional source IP. No bodies, Authorization header, cookie, tokens or arbitrary query strings. The actual HTTP sensor must sanitize **before signing**; MAC of unsafe sensor-created bytes is not a privacy control.
- Canary File fields currently contain only stable `asset_id`. Event types represent modify/rename/delete; no read observation claim.
- A valid MAC authenticates possession of a registered key for specific bytes **only**. It does not prove sensor honesty, endpoint safety, or attacker identity.

## Required persistence/receipt semantics (FUTURE; NO CODE YET)

After successful authentication and validation, store accepted exact sensor-produced allowed bytes, SHA-256 digest, immutable source occurrence and one pending processing job **atomically in PostgreSQL before acknowledging**. A true identical retry returns a stable receipt without another job. Reusing the source occurrence identity with different bytes becomes an audited conflict. Never claim exactly-once delivery across crashes without verifying the transactional/idempotency protocol.

Proposed response contract for later review: HTTP 202 for newly accepted events, stable duplicate receipt for byte-identical retry, conflict response for a reused ID with different bytes, and bounded generic failure for unauthorized/invalid records. **No HTTP response contract has yet been implemented or approved.**

## Offline contract spike

`backend/src/deceptshield/contract_spikes/custom_event_v1.py` provides a *local pure function*, not an API. The synthetic tests check exact-byte MAC mutation, duplicate JSON keys, unknown key, 300-second boundaries, size, metadata allowlist, unsupported read operation, and imported record position. They **do not** test TLS, live registries, concurrency, storage or incident grouping.

## Open questions to resolve before implementation

1. Confirm the exact source-event UUID and event-type vocabulary against approved GP1 records.
2. Confirm active source and key registration/provisioning, secret custody and key compromise boundary.
3. Specify real-world clock skew, retry/offline policy and measurable gap reporting.
4. Freeze 8192-byte cap or replace it with validated sensor payload measurements.
5. Align source/target identifiers with the finalized database schema and R-01/R-02 route keys.
6. Define response codes, rate limits, quarantine retention and privacy-specific error policy.
7. Define DB idempotency constraints and atomic raw+job transaction, then test worker crash/recovery.
8. Obtain sign-off and record reference to any approved GP1 change.
