"""Response schema cho /api/wip/kpi — mọi con số đã tính sẵn ở backend.

Nguồn gốc: COMPUTED — xem CLAUDE.md mục 5.3. TV và PC dùng chung endpoint này
nên không bao giờ hiện hai con số khác nhau cho cùng chỉ tiêu.
"""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class AreaBreakdown(BaseModel):
    area: str | None  # None nghĩa là dòng dữ liệu gốc không có Area (có thật trong dữ liệu)
    trolley_count: int
    total_qty: int


class AgeBucket(BaseModel):
    label: str  # "0-3" | "4-7" | "8-14" | ">14"
    trolley_count: int
    total_qty: int


class TopAgingItem(BaseModel):
    mo_no: str
    cust_style: str
    max_age_days: int
    trolley_count: int
    total_qty: int


class LoadingTrendPoint(BaseModel):
    date: date
    trolley_count: int
    total_qty: int


class WipKpi(BaseModel):
    total_trolley: int
    total_qty: int
    area_breakdown: list[AreaBreakdown]
    age_buckets: list[AgeBucket]
    top_aging: list[TopAgingItem]
    loading_trend: list[LoadingTrendPoint]
