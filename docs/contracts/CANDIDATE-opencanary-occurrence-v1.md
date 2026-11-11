# Candidate OpenCanary import occurrence identity (NOT APPROVED)

**Problem from independent GP2 audits:** repeated identical vendor log records may be independent observations; parser changes must not generate new source occurrences. Imported OpenCanary records have provenance **different from HMAC-authenticated custom sensors**.

**Candidate identity tuple:**

```text
(registered_ingest_source_id, immutable_acquisition_id, immutable_record_ordinal)
```

The acquisition identifier must be stable when the same immutable capture is reimported and must be assigned by the authenticated/registered acquisition path. The ordinal/record locator must identify a unique physical or logical record position within the capture, not just its content hash. Two identical log lines with distinct ordinals are distinct occurrences; reimport of the same capture and ordinal is idempotent.

The **parser profile/version and raw log content hash are not part of the identity**. They remain separate provenance/interpretation metadata. Changes in parser may change the derived normalized interpretation, and require controlled reprocessing; they must not mint new source observations.

This proposal does NOT imply cryptographic proof of authenticity for OpenCanary's upstream log. The collector must sanitize credential-bearing fields **before accepted raw storage**, and must distinguish accepted sanitized bytes from original upstream bytes.

The helper `imported_occurrence_key` in the offline contract spike only demonstrates these identity properties; it is not a collector, sanitizer, deduplication store, or database enforcement. Both registry/collector mapping and format compatibility require independent acceptance tests.

**Sign-off needed:** identity lookup rule, verified registration, capture durability, ordinal behavior for rotated/replayed files, and sanitized-byte provenance. GP1 R-03 must map to a registered acquisition source, not a fabricated custom-sensor HMAC identity.
