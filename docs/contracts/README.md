# Contract freeze checklist (not yet implemented)

These contracts must be agreed and versioned before creating event-ingestion tables or endpoints.

- `custom_event.v1.json`: immutable source_event_id, registry binding, observed_at, key_id, raw body and HMAC canonical rules.
- `opencanary_capture.v1.json`: registered collector and capture ID, immutable record locator, accepted sanitized bytes, parser profile and separate provenance class.
- `incident_grouping.v1.md`: rule-specific key, exact 300-second non-sliding window, concurrency locking and lifecycle behavior.
- `evidence_export.v1.md`: full versus reduced export claims, included accepted bytes, trusted offline public key, signed manifest.
- `authorization_matrix.v1.md`: Admin / Analyst / Viewer actions checked at API/object level.
- `scenario_registry.v1.csv`: 40 Core cases (15 positive, 15 supported negative, 10 confounders) and separate 10 optional extension cases.

**No contract above should be marked approved merely because a placeholder path appears here.**
