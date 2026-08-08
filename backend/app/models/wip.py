"""Pydantic models cho WIP Report — loại 1 (entity thô) và loại 2 (đã gộp sẵn).

Xem CLAUDE.md mục 5 (hợp đồng DataSource) và mục 5.3 (bảng nguồn gốc chỉ tiêu).
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class WipTrolley(BaseModel):
    """1 dòng WIP_Detail = 1 trolley. Nguồn gốc: COMPUTED (ta tự tính mọi KPI)."""

    trolley_code: str
    wb_code: str | None
    area: str | None
    so_no: str
    mo_no: str
    cust_style: str
    flower_code: str
    color_code: str
    print_to_edge: str | None
    bed_no: list[str]
    size_no: list[str]
    qty: int | None
    loading_ws: str
    loading_date: datetime | None
    in_vap_date: datetime | None
    back_cct_date: datetime | None
    wip_cct: int | None
    wip_vap: int | None
    pdc_wip: int | None


class WipSummary(BaseModel):
    """1 dòng WIP_Sammary = 1 MO đã gộp sẵn từ MES.

    `cut_qty`, `deduct_qty`, `qty_after_deduct` là SOURCE — không tái tạo được
    từ WIP_Detail (đến từ dữ liệu cắt ở hệ thống khác). Các cột còn lại trùng
    với những gì tính được từ WipTrolley, giữ lại để đối chiếu.
    """

    cust_style: str
    graphic: str
    mo_no: str
    total_trolley: int
    cut_qty: int | None
    deduct_qty: int | None
    qty_after_deduct: int | None
    total_qty: int | None
    avg_wip_cct: float | None
    avg_wip_vap: float | None
    avg_wip_pdc: float | None
