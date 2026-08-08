"""Tính KPI từ entity thô WipTrolley — COMPUTED, không phụ thuộc Excel hay SQL.

Chạy thuần trên list[WipTrolley] (đã chuẩn hoá qua DataSource) nên khi đổi
sang SqlServerDataSource ở Bước 9, toàn bộ hàm này giữ nguyên không cần sửa.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date

from app.models.kpi import AgeBucket, AreaBreakdown, LoadingTrendPoint, TopAgingItem, WipKpi
from app.models.wip import WipTrolley

_AGE_BUCKET_ORDER = ["0-3", "4-7", "8-14", ">14"]


def _age_days(trolley: WipTrolley) -> int | None:
    """Tuổi WIP = bộ đếm ngày ứng với khu vực trolley đang đứng (CCT/VAP/PDC).

    Mỗi trolley có cả 3 cột Wip_CCT/Wip_VAP/PDC_WIP nhưng chỉ cột khớp với
    `Area` hiện tại phản ánh đúng "đang chờ ở đây bao lâu" — các cột còn lại
    là số ngày đã trải qua ở giai đoạn trước đó, không phải tuổi hiện tại.
    """
    return {"CCT": trolley.wip_cct, "VAP": trolley.wip_vap, "PDC": trolley.pdc_wip}.get(
        trolley.area
    )


def _age_bucket_label(days: int) -> str:
    if days <= 3:
        return "0-3"
    if days <= 7:
        return "4-7"
    if days <= 14:
        return "8-14"
    return ">14"


def _sum_qty(trolleys: list[WipTrolley]) -> int:
    return sum(t.qty for t in trolleys if t.qty is not None)


def compute_area_breakdown(trolleys: list[WipTrolley]) -> list[AreaBreakdown]:
    groups: dict[str | None, list[WipTrolley]] = defaultdict(list)
    for t in trolleys:
        groups[t.area].append(t)
    return [
        AreaBreakdown(area=area, trolley_count=len(group), total_qty=_sum_qty(group))
        # None (thiếu Area) không so sánh được với str -> sort theo (is_none, area)
        for area, group in sorted(groups.items(), key=lambda kv: (kv[0] is None, kv[0]))
    ]


def compute_age_buckets(trolleys: list[WipTrolley]) -> list[AgeBucket]:
    buckets: dict[str, list[WipTrolley]] = {label: [] for label in _AGE_BUCKET_ORDER}
    for t in trolleys:
        age = _age_days(t)
        if age is None:
            continue
        buckets[_age_bucket_label(age)].append(t)
    return [
        AgeBucket(label=label, trolley_count=len(group), total_qty=_sum_qty(group))
        for label, group in buckets.items()
    ]


def compute_top_aging(trolleys: list[WipTrolley], limit: int = 10) -> list[TopAgingItem]:
    groups: dict[tuple[str, str], list[WipTrolley]] = defaultdict(list)
    for t in trolleys:
        groups[(t.mo_no, t.cust_style)].append(t)

    items: list[TopAgingItem] = []
    for (mo_no, cust_style), group in groups.items():
        ages = [age for age in (_age_days(t) for t in group) if age is not None]
        if not ages:
            continue
        items.append(
            TopAgingItem(
                mo_no=mo_no,
                cust_style=cust_style,
                max_age_days=max(ages),
                trolley_count=len(group),
                total_qty=_sum_qty(group),
            )
        )
    items.sort(key=lambda item: item.max_age_days, reverse=True)
    return items[:limit]


def compute_loading_trend(trolleys: list[WipTrolley]) -> list[LoadingTrendPoint]:
    groups: dict[date, list[WipTrolley]] = defaultdict(list)
    for t in trolleys:
        if t.loading_date is None:
            continue
        groups[t.loading_date.date()].append(t)
    return [
        LoadingTrendPoint(date=day, trolley_count=len(group), total_qty=_sum_qty(group))
        for day, group in sorted(groups.items())
    ]


def compute_wip_kpi(trolleys: list[WipTrolley]) -> WipKpi:
    return WipKpi(
        total_trolley=len(trolleys),
        total_qty=_sum_qty(trolleys),
        area_breakdown=compute_area_breakdown(trolleys),
        age_buckets=compute_age_buckets(trolleys),
        top_aging=compute_top_aging(trolleys),
        loading_trend=compute_loading_trend(trolleys),
    )
