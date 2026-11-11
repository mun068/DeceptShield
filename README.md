# DeceptShield

**Status: GP2 engineering foundation — proposed, not yet merged or supervisor-approved.**

DeceptShield is a bounded, single-server cyber-deception prototype for explainable incident correlation and tamper-evident evidence packages. This repository currently contains only **Sprint 0 scaffolding**. It does not yet implement live sensors, event ingestion, rules, evidence export, or role-based access control.

## First local run

Requirements: Docker Engine with the Compose plugin.

```bash
cp .env.example .env
# Edit .env and replace the example password with a fresh local-only value.
docker compose up --build -d
docker compose ps
curl -fsS http://127.0.0.1:8000/health/live
curl -fsS http://127.0.0.1:8000/health/ready
```

Do not commit `.env`. The API binds to the host loopback interface; PostgreSQL is accessible only to other containers. The sample Compose configuration is **for an isolated development lab**, not internet-facing deployment.

## Development tests

With Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e './backend[dev]'
ruff check backend
pytest -q backend/tests
```

The PostgreSQL integration check is opt-in locally and runs automatically in CI.

## Scope and engineering gates

- Core sources: Windows Canary File Agent (modify, rename, delete), HTTP decoy, version-pinned OpenCanary adapter.
- Direct incident rules: R-01/R-02/R-03, with a five-minute non-sliding grouping window and registered source identity.
- Secure ingestion must resolve HMAC, accepted bytes, occurrence identity, durability, and coverage gaps **before implementation**.
- Backend: FastAPI, PostgreSQL, one primary processing worker.
- UI: Simple and Analyst views, backed by authorization enforced in API endpoints.
- Evidence: accepted-byte export with Ed25519 manifest and independently trusted offline verifier.
- Read-access detection using Windows audit records is **a separately gated extension**, not part of original R-01.

The architecture is a design baseline, **not evidence of implementation or validation**. See `docs/decisions/ADR-0001-foundation.md`, `docs/contracts/README.md`, and `docs/plan/SPRINT-0.md`.

## Collaboration

Work on feature branches and submit pull requests to `main`. Require a second student to review security-sensitive changes. Do not merge solely because a UI demo works. Never commit live secrets, real customer data, credentials, or unredacted OpenCanary logs.
