from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_data_source
from app.config import settings
from app.datasource.base import DataSource
from app.models.meta import SnapshotInfo

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    datasource: str
    snapshot: SnapshotInfo


@router.get("/health", response_model=HealthResponse)
def health(source: DataSource = Depends(get_data_source)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        datasource=settings.datasource,
        snapshot=source.get_snapshot_info(),
    )
