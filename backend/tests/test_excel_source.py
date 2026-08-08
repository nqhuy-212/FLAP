"""Test đối chiếu ExcelDataSource với file Excel thật trong "EXCEL files/".

Đây là bộ test quan trọng nhất của Bước 1: tự tính KPI từ WIP_Detail rồi so
với WIP_Sammary (đã gộp sẵn từ MES) — bắt đúng loại lỗi nguy hiểm nhất là sai
mẫu số khi tính trung bình (xem CLAUDE.md mục 5.2).
"""
import statistics
from collections import defaultdict
from pathlib import Path

import pytest

from app.datasource.excel_source import ExcelDataSource

DATA_DIR = Path(__file__).resolve().parents[2] / "EXCEL files"

pytestmark = pytest.mark.skipif(
    not (DATA_DIR / "WIP Report_1.1.xlsx").exists(),
    reason='Cần file "EXCEL files/WIP Report_1.1.xlsx" trên máy (không commit lên git)',
)


@pytest.fixture(scope="module")
def source() -> ExcelDataSource:
    return ExcelDataSource(DATA_DIR)


@pytest.fixture(scope="module")
def trolleys(source):
    return source.get_wip_trolleys()


@pytest.fixture(scope="module")
def summaries(source):
    return source.get_wip_summary()


def _mean_ignoring_none(values: list[int | None]) -> float | None:
    present = [v for v in values if v is not None]
    return statistics.fmean(present) if present else None


class TestGetWipTrolleys:
    def test_reads_all_detail_rows(self, trolleys):
        # 352 dòng vật lý trong sheet - 5 dòng banner/header = 347 dòng dữ liệu
        assert len(trolleys) == 347

    def test_dates_are_real_datetimes(self, trolleys):
        with_loading_date = [t for t in trolleys if t.loading_date is not None]
        assert len(with_loading_date) > 0
        for t in with_loading_date:
            assert t.loading_date.year >= 2026

    def test_multi_value_cells_are_split(self, trolleys):
        multi_bed = [t for t in trolleys if len(t.bed_no) > 1]
        assert len(multi_bed) > 0

    def test_no_null_string_leaks_through(self, trolleys):
        for t in trolleys:
            assert t.back_cct_date != "NULL"
            for field in (t.trolley_code, t.mo_no, t.so_no):
                assert field != "NULL"

    def test_area_and_wb_code_are_real_none_not_string_none(self, trolleys):
        # Bug thật gặp ở Bước 2: str(clean_null(x)) biến None thành chuỗi "None".
        # Area/wbCode có ô trống thật trong dữ liệu (5 và 4 dòng) nên phải là
        # None thật, không phải chuỗi "None".
        assert any(t.area is None for t in trolleys)
        assert any(t.wb_code is None for t in trolleys)
        for t in trolleys:
            assert t.area != "None"
            assert t.wb_code != "None"

    def test_all_trolleys_json_serializable(self, trolleys):
        # Nghiệm thu Bước 2: /api/wip/detail từng lỗi 500 vì NaT (ô "In Vap
        # Date" trống) lọt qua dưới dạng datetime hợp lệ khi serialize JSON.
        from pydantic import TypeAdapter

        from app.models.wip import WipTrolley

        TypeAdapter(list[WipTrolley]).dump_json(trolleys)


class TestGetWipSummary:
    def test_reads_all_summary_rows(self, summaries):
        # 41 dòng vật lý - 5 dòng banner/header = 36 dòng dữ liệu
        assert len(summaries) == 36

    def test_mo_no_is_unique_key(self, summaries):
        mo_numbers = [s.mo_no for s in summaries]
        assert len(mo_numbers) == len(set(mo_numbers))


class TestReconciliationAgainstSummary:
    """Đối chiếu từng MO: tự gộp từ WIP_Detail rồi so với WIP_Sammary."""

    def test_known_mo_5v2607331001(self, trolleys, summaries):
        # Đối chiếu bằng tay đã kiểm chứng trong CLAUDE.md mục 5.2
        group = [t for t in trolleys if t.mo_no == "5V2607331001"]
        assert len(group) == 7

        total_trolley = len(group)  # đếm CẢ dòng Qty trống — không bỏ null
        total_qty = sum(t.qty for t in group if t.qty is not None)
        avg_wip_cct = _mean_ignoring_none([t.wip_cct for t in group])
        avg_wip_vap = _mean_ignoring_none([t.wip_vap for t in group])

        assert total_trolley == 7
        assert total_qty == 2836
        assert avg_wip_cct == pytest.approx(1.1428571428571428)
        assert avg_wip_vap == pytest.approx(7.666666666666667)

        summary = next(s for s in summaries if s.mo_no == "5V2607331001")
        assert summary.total_trolley == total_trolley
        assert summary.total_qty == total_qty
        assert summary.avg_wip_cct == pytest.approx(avg_wip_cct)
        assert summary.avg_wip_vap == pytest.approx(avg_wip_vap)

    def test_every_mo_reconciles(self, trolleys, summaries):
        """Quét toàn bộ MO trong WIP_Sammary — không chỉ 1 mẫu đã biết.

        Đây là test bắt lỗi mẫu số sai (vd dùng chung len(rows) cho mọi
        phép trung bình) trên toàn bộ dữ liệu thật, không chỉ 1 ca đã kiểm.
        """
        by_mo: dict[str, list] = defaultdict(list)
        for t in trolleys:
            by_mo[t.mo_no].append(t)

        checked = 0
        for summary in summaries:
            group = by_mo.get(summary.mo_no)
            assert group is not None, f"MO {summary.mo_no} có trong Sammary nhưng không có trong Detail"

            computed_total_trolley = len(group)
            computed_total_qty = sum(t.qty for t in group if t.qty is not None)
            computed_avg_cct = _mean_ignoring_none([t.wip_cct for t in group])
            computed_avg_vap = _mean_ignoring_none([t.wip_vap for t in group])

            assert computed_total_trolley == summary.total_trolley, summary.mo_no
            assert computed_total_qty == summary.total_qty, summary.mo_no
            if computed_avg_cct is None:
                assert summary.avg_wip_cct in (None, pytest.approx(0)) or summary.avg_wip_cct is None
            else:
                assert computed_avg_cct == pytest.approx(summary.avg_wip_cct), summary.mo_no
            if computed_avg_vap is None:
                assert summary.avg_wip_vap in (None, pytest.approx(0)) or summary.avg_wip_vap is None
            else:
                assert computed_avg_vap == pytest.approx(summary.avg_wip_vap), summary.mo_no
            checked += 1

        assert checked == len(summaries)

    def test_source_only_fields_present(self, summaries):
        # Cut_Qty / Deduct_Qty / Qty_After_Deduct là SOURCE — không tính lại
        # được, chỉ kiểm tra đã đọc ra giá trị (không phải None hàng loạt).
        with_cut_qty = [s for s in summaries if s.cut_qty is not None]
        assert len(with_cut_qty) > 0


class TestGetSnapshotInfo:
    def test_returns_excel_source(self, source):
        info = source.get_snapshot_info()
        assert info.source == "excel"
        assert len(info.files) == 1
        assert info.files[0].name == "WIP Report_1.1.xlsx"
        assert info.files[0].row_count == 347

    def test_generated_at_parsed_from_banner(self, source):
        info = source.get_snapshot_info()
        # Banner ghi "Date: 31-07-2026 / Time: 03:30:57 PM"
        assert info.files[0].generated_at is not None
        assert info.files[0].generated_at.year == 2026


class TestNotYetImplemented:
    """Các entity chưa khảo sát schema — phải báo lỗi rõ ràng, không âm thầm trả rỗng."""

    @pytest.mark.parametrize(
        "method_name",
        [
            "get_delivery_trolleys",
            "get_spread_plans",
            "get_print_orders",
            "get_relax_rolls",
            "get_material_issues",
            "get_material_exceptions",
        ],
    )
    def test_raises_not_implemented(self, source, method_name):
        with pytest.raises(NotImplementedError):
            getattr(source, method_name)()
