"""Test services/kpi.py — dữ liệu tổng hợp cho cả TV và PC dùng chung.

Phần lớn dùng WipTrolley tự tạo (không cần file Excel thật) để kiểm tra biên
của từng nhóm tuổi và thứ tự sắp xếp. Cuối file có 1 test đối chiếu tổng số
với dữ liệu thật, tương tự cách làm ở Bước 1.
"""
from datetime import datetime
from pathlib import Path

import pytest

from app.datasource.excel_source import ExcelDataSource
from app.models.wip import WipTrolley
from app.services.kpi import (
    compute_age_buckets,
    compute_area_breakdown,
    compute_loading_trend,
    compute_top_aging,
    compute_wip_kpi,
)

DATA_DIR = Path(__file__).resolve().parents[2] / "EXCEL files"


def _trolley(**overrides) -> WipTrolley:
    base = dict(
        trolley_code="T1",
        wb_code="WB1",
        area="CCT",
        so_no="SO1",
        mo_no="MO1",
        cust_style="STYLE1",
        flower_code="A",
        color_code="00W",
        print_to_edge=None,
        bed_no=[],
        size_no=[],
        qty=100,
        loading_ws="WS1",
        loading_date=None,
        in_vap_date=None,
        back_cct_date=None,
        wip_cct=None,
        wip_vap=None,
        pdc_wip=None,
    )
    base.update(overrides)
    return WipTrolley(**base)


class TestComputeAreaBreakdown:
    def test_groups_by_area_and_sums_qty(self):
        trolleys = [
            _trolley(area="CCT", qty=100),
            _trolley(area="CCT", qty=50),
            _trolley(area="VAP", qty=200),
        ]
        result = {b.area: b for b in compute_area_breakdown(trolleys)}
        assert result["CCT"].trolley_count == 2
        assert result["CCT"].total_qty == 150
        assert result["VAP"].trolley_count == 1
        assert result["VAP"].total_qty == 200

    def test_none_qty_excluded_from_sum_but_trolley_still_counted(self):
        trolleys = [_trolley(area="CCT", qty=None), _trolley(area="CCT", qty=100)]
        result = {b.area: b for b in compute_area_breakdown(trolleys)}
        assert result["CCT"].trolley_count == 2
        assert result["CCT"].total_qty == 100


class TestComputeAgeBuckets:
    def test_uses_counter_matching_current_area(self):
        # Area=CCT -> đọc wip_cct; wip_vap/pdc_wip bị bỏ qua dù có giá trị
        trolleys = [_trolley(area="CCT", wip_cct=2, wip_vap=99, pdc_wip=99, qty=10)]
        buckets = {b.label: b for b in compute_age_buckets(trolleys)}
        assert buckets["0-3"].trolley_count == 1
        assert buckets["4-7"].trolley_count == 0

    @pytest.mark.parametrize(
        "age,expected_label",
        [(0, "0-3"), (3, "0-3"), (4, "4-7"), (7, "4-7"), (8, "8-14"), (14, "8-14"), (15, ">14")],
    )
    def test_bucket_boundaries(self, age, expected_label):
        trolleys = [_trolley(area="VAP", wip_vap=age, qty=10)]
        buckets = {b.label: b for b in compute_age_buckets(trolleys)}
        assert buckets[expected_label].trolley_count == 1

    def test_missing_age_counter_excluded_from_all_buckets(self):
        # Area=PDC nhưng pdc_wip=None -> không xác định được tuổi, không tính
        trolleys = [_trolley(area="PDC", pdc_wip=None, qty=10)]
        buckets = compute_age_buckets(trolleys)
        assert sum(b.trolley_count for b in buckets) == 0


class TestComputeTopAging:
    def test_sorted_descending_by_max_age(self):
        trolleys = [
            _trolley(mo_no="MO_LOW", cust_style="S1", area="CCT", wip_cct=2, qty=10),
            _trolley(mo_no="MO_HIGH", cust_style="S2", area="CCT", wip_cct=20, qty=10),
        ]
        result = compute_top_aging(trolleys)
        assert [item.mo_no for item in result] == ["MO_HIGH", "MO_LOW"]

    def test_limit_respected(self):
        trolleys = [
            _trolley(mo_no=f"MO{i}", cust_style="S", area="CCT", wip_cct=i, qty=10)
            for i in range(15)
        ]
        result = compute_top_aging(trolleys, limit=10)
        assert len(result) == 10
        assert result[0].mo_no == "MO14"  # tuổi cao nhất đứng đầu

    def test_uses_max_age_among_trolleys_in_same_mo(self):
        trolleys = [
            _trolley(mo_no="MO1", cust_style="S1", area="CCT", wip_cct=2, qty=10),
            _trolley(mo_no="MO1", cust_style="S1", area="CCT", wip_cct=9, qty=10),
        ]
        result = compute_top_aging(trolleys)
        assert result[0].max_age_days == 9
        assert result[0].trolley_count == 2


class TestComputeLoadingTrend:
    def test_groups_by_date_ignoring_time(self):
        trolleys = [
            _trolley(loading_date=datetime(2026, 7, 31, 8, 0), qty=10),
            _trolley(loading_date=datetime(2026, 7, 31, 20, 0), qty=20),
            _trolley(loading_date=datetime(2026, 8, 1, 9, 0), qty=5),
        ]
        result = compute_loading_trend(trolleys)
        assert len(result) == 2
        assert result[0].date.isoformat() == "2026-07-31"
        assert result[0].trolley_count == 2
        assert result[0].total_qty == 30
        assert result[1].date.isoformat() == "2026-08-01"

    def test_missing_loading_date_excluded(self):
        trolleys = [_trolley(loading_date=None, qty=10)]
        assert compute_loading_trend(trolleys) == []

    def test_sorted_chronologically(self):
        trolleys = [
            _trolley(loading_date=datetime(2026, 8, 5), qty=1),
            _trolley(loading_date=datetime(2026, 8, 1), qty=1),
        ]
        result = compute_loading_trend(trolleys)
        assert [p.date.isoformat() for p in result] == ["2026-08-01", "2026-08-05"]


class TestComputeWipKpiOnRealData:
    """Đối chiếu tổng KPI với dữ liệu thật — tương tự cách làm ở Bước 1."""

    pytestmark = pytest.mark.skipif(
        not (DATA_DIR / "WIP Report_1.1.xlsx").exists(),
        reason='Cần file "EXCEL files/WIP Report_1.1.xlsx" trên máy (không commit lên git)',
    )

    def test_totals_reconcile_with_raw_trolley_list(self):
        trolleys = ExcelDataSource(DATA_DIR).get_wip_trolleys()
        kpi = compute_wip_kpi(trolleys)

        assert kpi.total_trolley == len(trolleys)
        assert kpi.total_qty == sum(t.qty for t in trolleys if t.qty is not None)

        # Mẫu số đúng: area_breakdown không được bỏ sót/nhân đôi trolley nào
        assert sum(b.trolley_count for b in kpi.area_breakdown) == kpi.total_trolley
        assert sum(b.total_qty for b in kpi.area_breakdown) == kpi.total_qty
