# DeceptShield — Project Status / سجل حالة المشروع

> **Source of truth:** This file is the current project checkpoint. Update it when a meaningful stage or release gate is completed. Historical checkpoints belong in [docs/progress/PROGRESS_HISTORY.md](docs/progress/PROGRESS_HISTORY.md). Do not mark work "implemented" merely because it is documented or planned.
>
> **Snapshot date:** 2026-11-11 (Asia/Amman)  
> **Working branch:** `feature/b1-event-contract-candidate`  
> **Status:** Sprint 0 runs locally; B1 contracts are a tested *offline candidate*, not approved live ingestion.  
> **Repository:** https://github.com/mun068/DeceptShield

## Executive checkpoint

- **Last verified local milestone:** Docker Compose started FastAPI + PostgreSQL successfully on Windows / Docker Desktop WSL2; readiness returned HTTP 503 when PostgreSQL was stopped and recovered to HTTP 200. **Latest local B1 suite:** 2026-11-11, a disposable Python 3.12 container ran Ruff with `--ignore EXE002` and pytest: **19 passed, 1 skipped, 1 warning**, no failed tests.
- **Last verified CI milestone:** GitHub Actions B1 branch workflow completed successfully: **20 pytest tests passed**, Ruff passed (https://github.com/mun068/DeceptShield/actions/runs/42994033570).
- **Current work:** ADR-0002 records the adopted working engineering direction and **P0 flaws** in the existing B1 candidate (source-to-event authorization, decoy/asset target binding, HTTP metadata privacy, stale duplicate policy). The v1 wire contract and deployed ingress remain **unfrozen / unimplemented**.
- **Immediate next action:** patch candidate contract and negative tests for ADR-0002 P0 defects; then add registered source/key/target schema and atomic raw+job persistence in a scoped PR. Wire live ingestion **only after** the versioned protocol and security cases pass, while keeping staged PR changes reviewable.
- **Important local difference:** `compose.yaml` on user's Windows machine has an *uncommitted* port override `127.0.0.1:18000:8000`; this local modification is not yet in the GitHub branch.

## Current implementation and evidence

| Item | Status | Evidence / limitation |
| --- | --- | --- |
| Private GitHub repo and branch structure | Implemented | `main`, `feature/sprint-0-foundation`, `feature/b1-event-contract-candidate` |
| Docker Compose dev stack | Implemented and locally tested | API + PostgreSQL running and healthy |
| FastAPI `/health/live` | Implemented and locally tested | HTTP 200 |
| FastAPI `/health/ready` | Implemented and locally tested | HTTP 200 with DB; HTTP 503 without DB; recovers to 200 |
| CI quality/testing | Implemented; CI and local tests verified | GitHub Actions: 20 passed and Ruff passed; Windows bind-mounted container: 19 passed, 1 skipped (DB test), Ruff passed with `EXE002` ignored |
| Offline HMAC candidate verifier | Implemented **as experimental helper only** | Synthetic tests; not wired into FastAPI or production registry |
| OpenCanary occurrence-key helper | Implemented **as experimental helper only** | Synthetic ordinal/reimport tests; no actual collector |
| B1 engineering direction / frozen wire contract | **Working direction adopted; wire contract not frozen** | ADR-0002 lists P0 fixes and explicit next gate: https://github.com/mun068/DeceptShield/blob/feature/b1-event-contract-candidate/docs/decisions/ADR-0002-B1-working-engineering-baseline.md |
| Event intake and database acceptance | Not implemented | No `POST /api/v1/sensor-events`; no durable raw+job transaction |
| Real sensors: Canary File / HTTP Decoy / OpenCanary | Not implemented | R-01/R-02/R-03 remain design scope |
| Detection engine / grouping / scoring | Not implemented | Concurrency safety and fixed 300-sec window not yet verified |
| Signed evidence package and independent verifier | Not implemented | No Ed25519 evidence delivery yet |
| RBAC / admin and analyst dashboard | Not implemented | No UI and no access-control implementation |
| Context adapters, alerts and optional read auditing | Planned/conditional | Must not block Core |
| 40 Core + 10 extension evaluation scenarios | Not yet frozen or executed | https://github.com/mun068/DeceptShield/issues/4 |

## Stage gates — completion means **evidence plus review**, not just code

| Stage | Deliverable / exit gate | Current state |
| --- | --- | --- |
| 0 — Foundation | Reproducible dev/CI stack, health failure/recovery checks, review and merge | **Technically validated; PR review/merge pending** |
| 1A — B1 contract | Final event shapes, authenticated source/target binding, privacy boundaries, tests and change record | **Working approach adopted; P0 candidate fixes and wire freeze pending** |
| 1B — Durable ingestion | Registered sources, body MAC, raw+job atomic commit, idempotency, 503/rollback tests | Not started |
| 2 — Sensors | Canary File Agent (modify/rename/delete), HTTP Decoy, pinned OpenCanary adapter | Not started |
| 3 — Rules/incident engine | R-01/R-02/R-03, deterministic fixed window, first-insert concurrency proof, scoring | Not started |
| 4 — Evidence | Full accepted-byte export, Ed25519 signed manifest, trusted offline verifier | Not started |
| 5 — Access/UI | API-level Admin/Analyst/Viewer RBAC; Simple/Analyst views | Not started |
| 6 — Context/reporting | Context extensions, operational health, reporting and selected alerts | Planned; priority after Core |
| 7 — Evaluation | Frozen 40 Core + separate 10 optional scenarios, security/load/recovery results | Not started |
| 8 — Release/demo | Single-server lab deployment, hardening, documented scope/residual risk, handover | Not started |

## B1 engineering decision — 2026-11-11

- Internal working baseline recorded in [ADR-0002](docs/decisions/ADR-0002-B1-working-engineering-baseline.md): **single-server modular monolith, PostgreSQL-backed worker, R-02 first, no added Core scope**.
- **P0 gaps confirmed from current offline helper:** no registered source-type-to-event-type mapping; no registered target decoy/asset validation; limited HTTP path privacy filtering and missing `host`; no explicit accepted-retransmit-after-300-seconds semantics.
- The architecture direction is adopted for implementation planning, **not** an approved or implemented live wire/API contract; no code changes to production intake were made during this milestone.
- Immediate next code milestone: update schemas and adversarial fixtures, then DB source/target registry and atomic raw+job commit, then controlled API endpoint.

## Local B1 verification — 2026-11-11

- Environment: Windows PowerShell, Docker Desktop/WSL2, temporary `python:3.12-slim` container; `backend` mounted from Windows at `/work`.
- Command: `python -m pip install --no-cache-dir -e ".[dev]" && ruff check --ignore EXE002 . && pytest -q`.
- Result observed in user-provided console log: **Ruff "All checks passed!"**, **19 passed, 1 skipped, 1 warning in 0.63s**. The skipped PostgreSQL integration check requires `DECEPTSHIELD_TEST_DB=1` plus dedicated `PG*` variables; it was exercised in CI instead.
- First local Ruff attempt without the exclusion reported eight `EXE002` findings on Python source/test files in the Windows bind-mounted directory; therefore the local success is explicitly **with this one lint rule excluded**. GitHub Actions ran Ruff without this exclusion.
- Warnings: Starlette/FastAPI test-client deprecation warning; `pip` running as root inside a disposable container. Neither is a test failure. Dependency resolution was not lockfile-pinned; flag this for a reproducibility follow-up.
- Scope of result: offline synthetic envelope validation and existing health checks only. **No live ingestion, sensor registration, durable event storage, incident correlation, or signed evidence was tested.**

## Open pull requests and engineering tasks

- **PR #1 — Sprint 0 foundation:** https://github.com/mun068/DeceptShield/pull/1 — open **draft**, targets `main`.
- **PR #5 — B1 candidate contract:** https://github.com/mun068/DeceptShield/pull/5 — open **draft**, targets `feature/sprint-0-foundation` (stacked; retarget after PR #1 merges).
- **Issue #2 — Contract approval gate:** https://github.com/mun068/DeceptShield/issues/2 — open.
- **Issue #3 — Local verification:** https://github.com/mun068/DeceptShield/issues/3 — open; CI, local running, and DB outage/recovery documented; independent review pending.
- **Issue #4 — Evaluation corpus:** https://github.com/mun068/DeceptShield/issues/4 — open.

## Immediate next tasks (prioritized)

1. **P0 — Fix contract flaws (ADR-0002):** add source-event-type and configured-target authorization, safe host/path/route metadata with privacy tests, and stale duplicate versus genuinely late new event behavior. Keep unchanged GP1 claims and document any variance.
2. **P0 — B1 test reproducibility:** Local synthetic tests have passed (19 passed, 1 DB integration skipped). Before release, rerun DB integration with a dedicated test database and resolve the Windows bind-mount `EXE002` lint portability discrepancy without suppressing unrelated rules.
3. **P0 — PR review and hygiene:** second student review; merge PR #1 only after acceptance; retarget PR #5 when dependency merges; ensure local `compose.yaml` port override is preserved or explicitly documented.
4. **P0 — Transactional event storage:** PostgreSQL migrations with one transaction for accepted source bytes, SHA-256 digest, unique occurrence, processing obligation; no response before commit.
5. **P0 — Adversarial intake acceptance:** test HMAC modifications, duplicate JSON members, unknown keys, stale timestamps, identical retry vs conflicting occurrence, rollback, crash recovery and credential minimization.
6. **P1 — First vertical slice:** HTTP Decoy -> registered authenticated event -> atomic persistence -> worker -> R-02 incident -> verified evidence; introduce UI only when backed by real API facts.
7. **P1 — Core completeness:** Canary File, OpenCanary adapter, RBAC, incident rules, signed exports, deterministic scenario corpus and tests.

## Stage completion rule (repeat after every phase)

When a phase actually completes, perform **all** of the following in the same work session:

1. Update this file with UTC or Asia/Amman date, branch, **implemented / planned / unverified / out-of-scope** distinctions.
2. Record exactly which tests ran, on which environment/commit, with results and links. Never invent pass results.
3. Record the last achieved checkpoint, unfinished tasks, blockers, residual risks and next action.
4. Append a dated summary to `docs/progress/PROGRESS_HISTORY.md` so previous states remain recoverable.
5. Link relevant PRs, commits and issues; keep acceptance gates open until someone actually reviews and signs off.
6. Commit status updates to an active feature branch / PR; **do not claim they are merged in `main`** until merged.

**Important:** Status updates happen when we actively work on the project together; this document is not an automatic background monitor.
