# DeceptShield — Project Status / سجل حالة المشروع

> **Source of truth:** This file is the current project checkpoint. Update it when a meaningful stage or release gate is completed. Historical checkpoints belong in [docs/progress/PROGRESS_HISTORY.md](docs/progress/PROGRESS_HISTORY.md). Do not mark work "implemented" merely because it is documented or planned.
>
> **Snapshot date:** 2026-11-11 (Asia/Amman)  
> **Working branch:** `feature/b1-event-contract-candidate`  
> **Status:** Sprint 0 runs locally; B1 contracts are a tested *offline candidate*, not approved live ingestion.  
> **Repository:** https://github.com/mun068/DeceptShield

## Executive checkpoint

- **Last verified local milestone:** Docker Compose started FastAPI + PostgreSQL successfully on Windows / Docker Desktop WSL2; liveness and readiness returned HTTP 200. With PostgreSQL stopped, readiness returned HTTP 503; after restoring DB, readiness returned HTTP 200.
- **Last verified CI milestone:** GitHub Actions B1 branch workflow completed successfully: **20 pytest tests passed**, Ruff passed (https://github.com/mun068/DeceptShield/actions/runs/42994033570).
- **Current work:** review candidate custom sensor event/HMAC contract, OpenCanary occurrence identity and acceptance criteria; gate G0/B1 **not approved yet**.
- **Immediate next action:** verify B1 tests locally, approve or revise event contract with team/supervisor, then implement transactional raw-event + processing-job persistence in a new reviewed PR. **Do not add live ingestion before approval.**
- **Important local difference:** `compose.yaml` on user's Windows machine has an *uncommitted* port override `127.0.0.1:18000:8000`; this local modification is not yet in the GitHub branch.

## Current implementation and evidence

| Item | Status | Evidence / limitation |
| --- | --- | --- |
| Private GitHub repo and branch structure | Implemented | `main`, `feature/sprint-0-foundation`, `feature/b1-event-contract-candidate` |
| Docker Compose dev stack | Implemented and locally tested | API + PostgreSQL running and healthy |
| FastAPI `/health/live` | Implemented and locally tested | HTTP 200 |
| FastAPI `/health/ready` | Implemented and locally tested | HTTP 200 with DB; HTTP 503 without DB; recovers to 200 |
| CI quality/testing | Implemented and CI verified | 20 tests passed, Ruff passed on B1; not all tests run locally yet |
| Offline HMAC candidate verifier | Implemented **as experimental helper only** | Synthetic tests; not wired into FastAPI or production registry |
| OpenCanary occurrence-key helper | Implemented **as experimental helper only** | Synthetic ordinal/reimport tests; no actual collector |
| Approved B1 contracts | **Pending approval** | https://github.com/mun068/DeceptShield/issues/2 |
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
| 1A — B1 contract | Approved event shapes, authentication boundary, provenance, tests, changes | **Offline candidate tests passed; sign-off pending** |
| 1B — Durable ingestion | Registered sources, body MAC, raw+job atomic commit, idempotency, 503/rollback tests | Not started |
| 2 — Sensors | Canary File Agent (modify/rename/delete), HTTP Decoy, pinned OpenCanary adapter | Not started |
| 3 — Rules/incident engine | R-01/R-02/R-03, deterministic fixed window, first-insert concurrency proof, scoring | Not started |
| 4 — Evidence | Full accepted-byte export, Ed25519 signed manifest, trusted offline verifier | Not started |
| 5 — Access/UI | API-level Admin/Analyst/Viewer RBAC; Simple/Analyst views | Not started |
| 6 — Context/reporting | Context extensions, operational health, reporting and selected alerts | Planned; priority after Core |
| 7 — Evaluation | Frozen 40 Core + separate 10 optional scenarios, security/load/recovery results | Not started |
| 8 — Release/demo | Single-server lab deployment, hardening, documented scope/residual risk, handover | Not started |

## Open pull requests and engineering tasks

- **PR #1 — Sprint 0 foundation:** https://github.com/mun068/DeceptShield/pull/1 — open **draft**, targets `main`.
- **PR #5 — B1 candidate contract:** https://github.com/mun068/DeceptShield/pull/5 — open **draft**, targets `feature/sprint-0-foundation` (stacked; retarget after PR #1 merges).
- **Issue #2 — Contract approval gate:** https://github.com/mun068/DeceptShield/issues/2 — open.
- **Issue #3 — Local verification:** https://github.com/mun068/DeceptShield/issues/3 — open; CI, local running, and DB outage/recovery documented; independent review pending.
- **Issue #4 — Evaluation corpus:** https://github.com/mun068/DeceptShield/issues/4 — open.

## Immediate next tasks (prioritized)

1. **P0 — Review contracts:** validate B1 against GP1 and audit evidence; close ambiguous fields (registration/key custody, 8192-byte trial cap, event vocabulary, replay/freshness, malformed JSON behavior). Obtain explicit supervisor/team sign-off in issue #2.
2. **P0 — Local B1 validation:** run local Ruff/pytest and record sanitized output; use CI result as separate evidence rather than claiming local success prematurely.
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
