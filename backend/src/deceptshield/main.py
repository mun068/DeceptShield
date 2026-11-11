"""Minimal health-only API; detection contracts are deliberately not frozen yet."""

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from deceptshield import health

app = FastAPI(
    title="DeceptShield API",
    version="0.1.0",
    description="GP2 foundation. No event ingestion or incident detection yet.",
)


class LiveStatus(BaseModel):
    status: Literal["healthy"]
    service: Literal["deceptshield-api"]


class ReadyStatus(LiveStatus):
    database: Literal["connected"]


@app.get("/health/live", response_model=LiveStatus, tags=["health"])
def liveness() -> LiveStatus:
    """Process liveness; intentionally does not check external dependencies."""
    return LiveStatus(status="healthy", service="deceptshield-api")


@app.get("/health/ready", response_model=ReadyStatus, tags=["health"])
def readiness() -> ReadyStatus:
    """Return 503 if PostgreSQL is not available; never expose connection secrets."""
    if not health.database_is_ready():
        raise HTTPException(status_code=503, detail="service not ready")
    return ReadyStatus(
        status="healthy",
        service="deceptshield-api",
        database="connected",
    )
