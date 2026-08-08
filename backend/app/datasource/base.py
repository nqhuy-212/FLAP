"""Hợp đồng DataSource — trục xương sống của dự án.

Mọi API chỉ được gọi qua interface này. Excel (giai đoạn 1) và SQL Server
(giai đoạn 2) đều hiện thực đúng Protocol này để đổi nguồn mà không sửa
frontend. Xem CLAUDE.md mục 5.
"""
from __future__ import annotations

from typing import Protocol

from app.models.meta import SnapshotInfo
from app.models.other import (
    DeliveryTrolley,
    MaterialException,
    MaterialIssue,
    PrintOrder,
    RelaxRoll,
    SpreadPlan,
)
from app.models.wip import WipSummary, WipTrolley


class DataSource(Protocol):
    # === Loại 1: entity THÔ — ta tự tính mọi KPI từ đây ===
    def get_wip_trolleys(self) -> list[WipTrolley]: ...
    def get_delivery_trolleys(self) -> list[DeliveryTrolley]: ...
    def get_spread_plans(self) -> list[SpreadPlan]: ...
    def get_print_orders(self) -> list[PrintOrder]: ...
    def get_relax_rolls(self) -> list[RelaxRoll]: ...
    def get_material_issues(self) -> list[MaterialIssue]: ...
    def get_material_exceptions(self) -> list[MaterialException]: ...

    # === Loại 2: entity ĐÃ GỘP SẴN từ nguồn — KHÔNG tái tạo được ===
    def get_wip_summary(self) -> list[WipSummary]: ...

    # === Siêu dữ liệu ===
    def get_snapshot_info(self) -> SnapshotInfo: ...
