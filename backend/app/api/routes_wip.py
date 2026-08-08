from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_data_source
from app.datasource.base import DataSource
from app.models.kpi import WipKpi
from app.models.wip import WipSummary, WipTrolley
from app.services.kpi import compute_wip_kpi

router = APIRouter()


@router.get("/detail", response_model=list[WipTrolley])
def get_wip_detail(source: DataSource = Depends(get_data_source)) -> list[WipTrolley]:
    return source.get_wip_trolleys()


@router.get("/summary", response_model=list[WipSummary])
def get_wip_summary(source: DataSource = Depends(get_data_source)) -> list[WipSummary]:
    return source.get_wip_summary()


@router.get("/kpi", response_model=WipKpi)
def get_wip_kpi(source: DataSource = Depends(get_data_source)) -> WipKpi:
    return compute_wip_kpi(source.get_wip_trolleys())
