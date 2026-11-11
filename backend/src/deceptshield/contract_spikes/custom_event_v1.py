"""OFFLINE contract spike for HMAC-authenticated custom-sensor messages.

This is a proposed B1 protocol experiment, NOT a production ingest endpoint.
No persistence, idempotency, sensor registration, rate limiting or TLS is provided here.
"""

from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Mapping

MAX_BODY_BYTES = 8192  # B1 candidate only; not an approved GP1 requirement.
MAX_CLOCK_SKEW_SECONDS = 300  # GP1 design value; final retry behavior needs approval.
SCHEMA_VERSION = "1.0-candidate"
_ALLOWED_TOP_LEVEL = frozenset({
    "schema_version",
    "sensor_id",
    "key_id",
    "source_event_id",
    "observed_at",
    "event_type",
    "payload",
})
_ALLOWED_EVENT_TYPES = frozenset({
    "canary_file.modify",
    "canary_file.rename",
    "canary_file.delete",
    "http_decoy.request",
})
_UTC_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$"
)
_KEY_ID = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
_METHOD = re.compile(r"^[A-Z]{1,12}$")


class ContractError(ValueError):
    """Non-sensitive failure code for this local-only prototype."""


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for name, value in pairs:
        if name in obj:
            raise ContractError("duplicate_json_member")
        obj[name] = value
    return obj


def _reject_constant(_value: str) -> None:
    raise ContractError("invalid_json_constant")


def _parse_strict_json(body: bytes) -> dict[str, Any]:
    try:
        content = json.loads(
            body.decode("utf-8", errors="strict"),
            object_pairs_hook=_reject_duplicates,
            parse_constant=_reject_constant,
        )
    except ContractError:
        raise
    except (ValueError, UnicodeDecodeError, RecursionError) as exc:
        raise ContractError("invalid_json") from exc
    if not isinstance(content, dict):
        raise ContractError("invalid_envelope")
    return content


def _require_uuid(value: Any, field: str) -> None:
    if not isinstance(value, str):
        raise ContractError("invalid_" + field)
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ContractError("invalid_" + field) from exc
    if str(parsed) != value:
        raise ContractError("invalid_" + field)


def _validate_payload(event_type: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ContractError("invalid_payload")
    if event_type.startswith("canary_file."):
        # The current GP1 Core does not claim read/open detection.
        if set(payload) != {"asset_id"}:
            raise ContractError("invalid_file_metadata")
        _require_uuid(payload["asset_id"], "asset_id")
        return

    required = {"decoy_id", "method", "path", "status_code"}
    optional = {"source_ip"}
    if not required.issubset(payload) or set(payload) - (required | optional):
        raise ContractError("invalid_http_metadata")
    _require_uuid(payload["decoy_id"], "decoy_id")
    if not isinstance(payload["method"], str) or not _METHOD.fullmatch(payload["method"]):
        raise ContractError("invalid_http_method")
    path = payload["path"]
    if (
        not isinstance(path, str)
        or len(path) > 256
        or not path.startswith("/")
        or any(token in path for token in ("?", "#", "\r", "\n"))
    ):
        raise ContractError("invalid_http_path")
    status = payload["status_code"]
    if type(status) is not int or not 100 <= status <= 599:
        raise ContractError("invalid_http_status")
    if "source_ip" in payload:
        try:
            ipaddress.ip_address(payload["source_ip"])
        except (ValueError, TypeError) as exc:
            raise ContractError("invalid_source_ip") from exc


def verify_candidate_event(
    body: bytes,
    mac_hex: str,
    registered_keys: Mapping[tuple[str, str], bytes],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Verify candidate envelope for a synthetic lab fixture.

    Reads a claimed sensor_id/key_id solely to look up a key; those fields gain
    authenticity only after an HMAC comparison over the UNCHANGED body bytes.
    This result is not a durable acceptance receipt or incident decision.
    """
    if not isinstance(body, bytes) or not 0 < len(body) <= MAX_BODY_BYTES:
        raise ContractError("invalid_body_size")
    message = _parse_strict_json(body)
    sensor_id = message.get("sensor_id")
    key_id = message.get("key_id")
    if not isinstance(sensor_id, str) or not isinstance(key_id, str):
        raise ContractError("unauthenticated")

    secret = registered_keys.get((sensor_id, key_id))
    if (
        not isinstance(secret, bytes)
        or not secret
        or not isinstance(mac_hex, str)
        or re.fullmatch(r"[0-9a-f]{64}", mac_hex) is None
    ):
        raise ContractError("unauthenticated")
    digest = hmac.new(secret, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(digest, mac_hex):
        raise ContractError("unauthenticated")

    if set(message) != _ALLOWED_TOP_LEVEL:
        raise ContractError("invalid_envelope_fields")
    if message["schema_version"] != SCHEMA_VERSION:
        raise ContractError("unsupported_schema_version")
    _require_uuid(sensor_id, "sensor_id")
    if not _KEY_ID.fullmatch(key_id):
        raise ContractError("invalid_key_id")
    _require_uuid(message["source_event_id"], "source_event_id")

    event_type = message["event_type"]
    if not isinstance(event_type, str) or event_type not in _ALLOWED_EVENT_TYPES:
        raise ContractError("unsupported_event_type")
    timestamp = message["observed_at"]
    if not isinstance(timestamp, str) or not _UTC_TIMESTAMP.fullmatch(timestamp):
        raise ContractError("invalid_observed_at")
    try:
        observed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError("invalid_observed_at") from exc
    check_time = now or datetime.now(timezone.utc)
    if check_time.tzinfo is None or check_time.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    skew = abs((observed - check_time.astimezone(timezone.utc)).total_seconds())
    if skew > MAX_CLOCK_SKEW_SECONDS:
        raise ContractError("outside_freshness_window")
    _validate_payload(event_type, message["payload"])
    return message


def imported_occurrence_key(
    ingest_source_id: str, acquisition_id: str, record_ordinal: int
) -> tuple[str, str, int]:
    """Candidate immutable import position; deliberately excludes log bytes/parser version.

    Database constraints, verified collector registry and stable acquisition IDs
    are NOT implemented by this helper.
    """
    _require_uuid(ingest_source_id, "ingest_source_id")
    _require_uuid(acquisition_id, "acquisition_id")
    if type(record_ordinal) is not int or record_ordinal < 0:
        raise ContractError("invalid_record_ordinal")
    return (ingest_source_id, acquisition_id, record_ordinal)
