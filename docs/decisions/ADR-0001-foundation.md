# ADR-0001 — GP2 modular-monolith foundation

**Status:** Proposed — supervisor/team approval pending

**Context:** The GP1 design is a bounded single-server deception prototype. Independent design reviews identify unresolved source provenance, imported occurrence identities, transaction/concurrency semantics, exact-byte evidence coverage, privacy filtering, time/freshness gaps, and API authorization details.

**Decision candidate:**
- One Linux host with Docker Compose, FastAPI, PostgreSQL, React/TypeScript, and one primary processing worker.
- Three Core sources with direct rules R-01/R-02/R-03 and deterministic fixed-window grouping; R-04/R-05 remain conditional context-only features.
- Start with a small health-only backend. Do not accidentally define or ship ingestion, scoring, authorization, or evidence claims by creating placeholder endpoints.
- Keep Windows read-access auditing as a separately evaluated extension; native file-watcher events alone are not proof of file reads.

**Why this path:** Deliver an independently testable Core with fewer services and clearer correctness guarantees than a distributed architecture would afford a three-student team.

**Requirements before the first ingestion endpoint:**
1. Source registry and cryptographic versus imported-source trust/provenance.
2. Unique occurrence identity independent of parser version/content hash.
3. Strict, size-bounded JSON and HMAC verification over the original request bytes.
4. Atomic PostgreSQL commit of accepted raw bytes, digest and processing job before acknowledgment.
5. First-insert-safe incident grouping and precise half-open fixed window semantics.
6. Disclosure of stale event rejection, lost coverage, sanitization boundary and retained accepted bytes.
7. Adversarial evidence verifier and API role matrix.

**Consequences:** No claim of implemented detection or validation until code plus run evidence exists. Any change to agreed GP1 scope requires formal team/supervisor change control.

**Open at B1:** approve event contract v1, timestamp/retry policy, first ingestion source and database schema; pin validated software versions and image digests.
