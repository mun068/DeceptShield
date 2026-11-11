"""Optional integration test; CI runs it with an isolated PostgreSQL service."""

import os

import pytest

from deceptshield.health import database_is_ready


@pytest.mark.skipif(
    os.getenv("DECEPTSHIELD_TEST_DB") != "1",
    reason="Enable only with DECEPTSHIELD_TEST_DB=1 and dedicated PG* settings",
)
def test_postgres_is_ready():
    assert database_is_ready() is True
