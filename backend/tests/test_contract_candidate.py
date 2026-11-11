"""Synthetic offline B1 contract tests; no HTTP ingestion or database writes."""

import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime, timedelta

import pytest

from deceptshield.contract_spikes.custom_event_v1 import (
    ContractError,
    imported_occurrence_key,
    verify_candidate_event,
)

KEY = b"synthetic-fixture-only-do-not-provision"
SENSOR_ID = "da3b1c17-1bbb-47d8-8754-b00f4800822d"
DECOY_ID = "0e75d059-411a-4919-86fb-dfc5ac33dfe1"
COLLECTOR_ID = "09700496-8543-43ce-9ca6-0c16a83af043"
CAPTURE_ID = "9b95fdc6-1784-424f-a255-4ef36483126f"
CLOCK = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)
REGISTRY = {(SENSOR_ID, "lab-v1"): KEY}


def sample_event(*, offset_seconds=0):
    observed = (CLOCK + timedelta(seconds=offset_seconds)).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": "1.0-candidate",
        "sensor_id": SENSOR_ID,
        "key_id": "lab-v1",
        "source_event_id": str(uuid.UUID("3b5f0fc1-13fa-416d-aa38-579a4bb8915b")),
        "observed_at": observed,
        "event_type": "http_decoy.request",
        "payload": {
            "decoy_id": DECOY_ID,
            "method": "GET",
            "path": "/lab/canary",
            "status_code": 200,
            "source_ip": "192.0.2.10",
        },
    }


def encode(event):
    return json.dumps(event, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sign(raw):
    return hmac.new(KEY, raw, hashlib.sha256).hexdigest()


def verify(raw, *, registry=REGISTRY):
    return verify_candidate_event(raw, sign(raw), registry, now=CLOCK)


def test_valid_synthetic_http_event():
    raw = encode(sample_event())
    assert verify(raw)["payload"]["path"] == "/lab/canary"


def test_tampering_even_only_whitespace_breaks_raw_hmac():
    raw = encode(sample_event())
    signed = sign(raw)
    with pytest.raises(ContractError, match="unauthenticated"):
        verify_candidate_event(raw + b" ", signed, REGISTRY, now=CLOCK)


def test_duplicate_json_member_is_rejected_even_if_mac_matches():
    raw = encode(sample_event()).replace(
        b'"schema_version":"1.0-candidate"',
        b'"schema_version":"1.0-candidate","schema_version":"1.0-candidate"',
    )
    with pytest.raises(ContractError, match="duplicate_json_member"):
        verify(raw)


def test_unknown_registered_key_is_not_accepted():
    raw = encode(sample_event())
    with pytest.raises(ContractError, match="unauthenticated"):
        verify(raw, registry={})


@pytest.mark.parametrize("offset_seconds", [-300, 300])
def test_freshness_includes_exact_boundary(offset_seconds):
    assert verify(encode(sample_event(offset_seconds=offset_seconds)))["sensor_id"] == SENSOR_ID


@pytest.mark.parametrize("offset_seconds", [-301, 301])
def test_freshness_excludes_beyond_boundary(offset_seconds):
    with pytest.raises(ContractError, match="outside_freshness_window"):
        verify(encode(sample_event(offset_seconds=offset_seconds)))


def test_oversized_message_is_rejected_before_authentication():
    with pytest.raises(ContractError, match="invalid_body_size"):
        verify(b"x" * 8193)


def test_no_secrets_or_query_strings_in_http_metadata():
    event = sample_event()
    event["payload"]["Authorization"] = "synthetic-secret-marker"
    with pytest.raises(ContractError, match="invalid_http_metadata"):
        verify(encode(event))
    event = sample_event()
    event["payload"]["path"] = "/lab/canary?token=synthetic-secret-marker"
    with pytest.raises(ContractError, match="invalid_http_path"):
        verify(encode(event))


def test_import_ordinal_separates_identical_upstream_lines():
    first = imported_occurrence_key(COLLECTOR_ID, CAPTURE_ID, 0)
    second = imported_occurrence_key(COLLECTOR_ID, CAPTURE_ID, 1)
    replay = imported_occurrence_key(COLLECTOR_ID, CAPTURE_ID, 0)
    assert first != second
    assert first == replay


def test_import_ordinal_cannot_be_negative_or_boolean():
    with pytest.raises(ContractError, match="invalid_record_ordinal"):
        imported_occurrence_key(COLLECTOR_ID, CAPTURE_ID, -1)
    with pytest.raises(ContractError, match="invalid_record_ordinal"):
        imported_occurrence_key(COLLECTOR_ID, CAPTURE_ID, True)


def test_file_reads_remain_unsupported_by_core():
    event = sample_event()
    event["event_type"] = "canary_file.read"
    event["payload"] = {"asset_id": DECOY_ID}
    with pytest.raises(ContractError, match="unsupported_event_type"):
        verify(encode(event))


def test_file_modify_is_allowed_as_candidate_direct_event():
    event = sample_event()
    event["event_type"] = "canary_file.modify"
    event["payload"] = {"asset_id": DECOY_ID}
    assert verify(encode(event))["event_type"] == "canary_file.modify"


def test_boolean_http_status_is_not_accepted_as_integer():
    event = sample_event()
    event["payload"]["status_code"] = True
    with pytest.raises(ContractError, match="invalid_http_status"):
        verify(encode(event))


def test_http_source_ip_must_be_text_not_integer():
    event = sample_event()
    event["payload"]["source_ip"] = 12345
    with pytest.raises(ContractError, match="invalid_source_ip"):
        verify(encode(event))
