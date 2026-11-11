# DeceptShield — Project Progress History

This append-only log records *verified* milestones and remaining work at each checkpoint. For the latest snapshot, read [PROJECT_STATUS.md](../../PROJECT_STATUS.md). Do not rewrite old milestones to imply later work was already completed.

---

## 2026-11-11 — Checkpoint 0: Foundation and B1 candidate

**Branch:** `feature/b1-event-contract-candidate`  
**Status file commit:** to be identified from the current branch history; no claim of merge to main.

### Completed, with evidence

- Private repository established; feature branch and draft PR workflow started.
- FastAPI health endpoints plus PostgreSQL defined in Docker Compose.
- On a Windows workstation using Docker Desktop/WSL2, `docker compose config --quiet` and `docker compose up --build -d` succeeded; API bound on local `127.0.0.1:18000` (local-only Compose modification); PostgreSQL became `healthy`.
- `/health/live` and `/health/ready` responded HTTP 200 during healthy operation.
- After `docker compose stop db`, `/health/ready` returned HTTP 503, then returned HTTP 200 after `docker compose up -d --wait db`.
- Offline candidate for custom sensor HMAC and imported OpenCanary occurrence identity added with security tests. GitHub Actions B1 branch run https://github.com/mun068/DeceptShield/actions/runs/42994033570 passed **20 tests** and Ruff.
- Project status and follow-up checklist recorded in `PROJECT_STATUS.md`.

### Not yet completed

- PR #1 and PR #5 remain draft/open; no approved merge to `main`.
- B1 acceptance contract is still proposed; supervisor/team review/sign-off pending.
- B1 synthetic test suite has **not yet been evidenced as run locally**.
- Live event-ingestion API, registered sensors and secrets, durable event/job tables and worker, incident rules, UI, RBAC and full signed evidence exporter are not implemented.
- 40 Core / 10 conditional extension scenarios are not frozen, executed or scored.
- Security, concurrency, coverage-gap and worker-crash tests have not run.

### Next approved-sequence work

1. Independently review Sprint 0 and B1 draft PRs; approve contract decisions with named reviewers.
2. Validate the B1 tests locally; record results.
3. Freeze and implement DB durability / source registry in a subsequent scoped PR.
4. Build the first R-02 end-to-end scenario after contract approval; then add remaining Core sensors and safety checks.

### Tracking links

- Foundation PR: https://github.com/mun068/DeceptShield/pull/1
- B1 contract PR: https://github.com/mun068/DeceptShield/pull/5
- Contract gate: https://github.com/mun068/DeceptShield/issues/2
- Local verification: https://github.com/mun068/DeceptShield/issues/3
- Evaluation plan: https://github.com/mun068/DeceptShield/issues/4

### Rule for the next entry

After a real phase acceptance, append a new dated section with **(a)** last checkpoint, **(b)** done + evidence, **(c)** unfinished work, **(d)** blockers/risks, **(e)** the immediate next stage, **(f)** branch/PR/CI links. Update `PROJECT_STATUS.md` to match, but never erase earlier entries.

---

## 2026-11-11 — Checkpoint 1: Local B1 validation (test milestone, **not contract approval**)

**Branch:** `feature/b1-event-contract-candidate`  
**Environment:** Windows PowerShell + Docker Desktop/WSL2; temporary `python:3.12-slim` container with Windows-mounted backend folder.

### Verified since Checkpoint 0

- Installed backend and dev dependencies successfully inside the disposable container.
- `ruff check --ignore EXE002 .` → **All checks passed**.
- `pytest -q` → **19 passed, 1 skipped, 1 warning in 0.63s**.
- The skipped test is the PostgreSQL integration test, disabled by default without a dedicated test DB connection; GitHub Actions B1 run https://github.com/mun068/DeceptShield/actions/runs/42994033570 previously ran the suite with its DB test: **20 passed**.
- The earlier local Ruff run (without exception) reported eight `EXE002` warnings caused by Python files perceived as executable from the Windows bind mount. The accepted local run excluded **only** `EXE002`; GitHub CI lint passed without excluding it.
- The one pytest warning concerns deprecation in the test-client dependency integration. No application/API runtime failure was shown by these tests.

### Still unverified / pending

- Contract sign-off from supervisor/team; PR #1 and PR #5 review and merge.
- Production path: TLS/registry/authenticity, event ingestion endpoint, transactional raw+job persistence, deduplication and retry, worker crash safety, concurrent grouping, signed export verification, RBAC, real sensors and evaluation holdout.
- Local PostgreSQL integration test under a dedicated DB, plus dependency pin/lock and cross-OS lint-parity review.

### Immediate next action

Review and approve the B1 wire contract and GP1 scope alignment in issue #2 before implementing durable ingestion. Coordinate the stacked draft pull requests (#1 then #5); keep the local port override uncommitted or explicitly reconcile it.

**Evidence:** User-provided Windows console output dated 2026-11-11, plus [GitHub Actions B1 results](https://github.com/mun068/DeceptShield/actions/runs/42994033570). No claim of merged code or live ingestion.

---

## 2026-11-11 — Checkpoint 2: Engineering direction and B1 security review (not a release)

**Decision document:** [ADR-0002](../../docs/decisions/ADR-0002-B1-working-engineering-baseline.md)  
**Branch:** `feature/b1-event-contract-candidate`

### Decision reached

- Retain the **single-server FastAPI + PostgreSQL modular monolith**, one DB-backed worker, no distributed queue/cluster/AI additions to Core.
- Make **HTTP Decoy / R-02 the first end-to-end vertical slice**, then Canary File Agent R-01 and pinned OpenCanary adapter R-03.
- Keep exact-byte HMAC-SHA256, per-source key, 8 KiB trial maximum, +/-300-second freshness for **new** events, and durable raw+job commit before receipt as the working approach. Handle already-accepted exact old retransmits without creating a new event; reject truly new stale events and record coverage limitations.
- Keep OpenCanary acquisition identity separate from authenticated custom-sensor occurrence IDs.
- No API ingestion is authorized as tested or production-ready by this document.

### Technical issues identified in current offline verifier

- **P0:** registered key alone cannot restrict source event family (`canary_file.*` vs `http_decoy.request`).
- **P0:** well-formed but unregistered `decoy_id`/`asset_id` values are currently accepted by the pure helper.
- **P0:** HTTP path check does not guarantee secret-free path segments or full control character filtering; candidate omits GP1 `host` field.
- **P0:** stale-new-event and identical-retry-after-window policy needs explicit fixture and durable receipt mechanism.
- **P1:** local Windows lint parity, skipped local PostgreSQL test, pinned dependency/image versions and test-client deprecation need follow-up.

### What remains

No source registry/target registry, live API endpoint, database acceptance migration, job worker, incident engine, key rotation, offline evidence verifier, API RBAC, integrated sensors, or scenario acceptance tests have been completed.

### Next

1. Update candidate contract fixture and add targeted failing/adversarial tests for the above P0 conditions.
2. Implement migrations for enabled sensor/key/decoy registry, immutable accepted bytes + digest + pending processing job, and idempotent receipts.
3. Only then implement and test first HTTP Decoy live ingestion in the isolated lab.
4. Keep separate PR review and CI gates; no premature merges or proof claims.

This is a **planning/design milestone**, not proof of newly implemented detection.
