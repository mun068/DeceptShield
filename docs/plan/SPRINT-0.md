# Sprint 0 — Engineering foundation

**Status:** Scaffold implementation proposed on feature branch. Run/CI evidence must be checked after the pull request is created.

## Owners (suggested, subject to team agreement)
- Sensors and lab: Windows/HTTP/OpenCanary feasibility, safe fixtures and source provenance.
- Backend and data: contract negotiation, FastAPI health, PostgreSQL and CI.
- UI/evidence/QA: acceptance criteria, workflow review, evidence proof requirements and negative tests.

## Acceptance checklist
- [ ] Supervisor/team approve Option B scope and any GP1 changes.
- [x] Repository organized with isolated `feature/sprint-0-foundation` branch.
- [x] FastAPI health-only service, PostgreSQL dev service and local-only binding defined in files.
- [x] Unit tests and database integration check defined.
- [x] GitHub Actions workflow configured.
- [ ] GitHub Actions actually passes on the branch.
- [ ] Team member reproduces `docker compose up --build -d` on an isolated Linux machine.
- [ ] Local readiness yields 200, and readiness without PostgreSQL yields 503.
- [ ] Validate version pins and document `docker compose config` result without exposing password.
- [ ] Freeze and review source/event contract and rule semantics before implementation.
- [ ] Define 40 Core case registry and separate optional feature gate.

## Local proof
```bash
cp .env.example .env
# Set a fresh lab password in .env before running.
docker compose config --quiet
docker compose up --build -d
docker compose ps
curl -fsS http://127.0.0.1:8000/health/live
curl -fsS http://127.0.0.1:8000/health/ready
```

No current CI pass, local runtime test, security assessment, or supervisor approval is claimed.
