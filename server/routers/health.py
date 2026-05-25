"""Health-Endpoint.

Story: PQC-19 (SKL-1), Acceptance Criterion AC-3.

Liefert einen kompakten Status, ueber den nginx und Docker-Compose-Healthchecks
verifizieren koennen, dass der Service ready ist. In spaeteren Sprints kann
hier zusaetzlich der Status von DB, Redis und der Crypto-Registry hineingehen
(siehe NFR-Ops-3).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from config import Settings, get_settings

router = APIRouter(tags=["meta"])


class HealthResponse(BaseModel):
    """Antwort-Body fuer GET /health."""

    status: str
    version: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness und Version",
    description="Liefert 200 OK mit dem aktuellen Service-Status und der Version.",
)
def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    return HealthResponse(status="ok", version=settings.version)
