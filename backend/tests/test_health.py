"""Contract-level health tests that do not require a database."""

from fastapi.testclient import TestClient

from deceptshield import health
from deceptshield.main import app

client = TestClient(app)


def test_liveness_is_independent_of_database(monkeypatch):
    monkeypatch.setattr(health, "database_is_ready", lambda: False)
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "deceptshield-api"}


def test_readiness_succeeds_with_database(monkeypatch):
    monkeypatch.setattr(health, "database_is_ready", lambda: True)
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "deceptshield-api",
        "database": "connected",
    }


def test_readiness_fails_closed(monkeypatch):
    monkeypatch.setattr(health, "database_is_ready", lambda: False)
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "service not ready"}
