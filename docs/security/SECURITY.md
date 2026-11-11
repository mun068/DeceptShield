# Development lab boundaries

- Use synthetic events only. Never ingest real credentials, personal data or unsolicited HTTP request bodies.
- `.env` is local-only and excluded from Git. Do not put production secrets in Compose or workflow YAML.
- Isolate Docker development networks; this Compose file publishes only the API on `127.0.0.1` and does not publish PostgreSQL.
- Before enabling sensors: verify sensitive-field minimization, provenance registry and per-source authentication trust model.
- Readiness endpoints are unprivileged operational checks. There are no incident/administration APIs in Sprint 0.
- The current sample is not suitable for public deployment. Add TLS, authenticated access, audit logging, request bounds, dependency/image digest pinning, tested backups and threat-model review before production-like demonstrations.
- Keep a versioned audit trail of claims, tests, residual risks and the source that supports each claim.
