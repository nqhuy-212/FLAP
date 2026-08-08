"""Test _make_history_on_changed trong main.py — cầu nối watcher -> Parquet + log.

CLAUDE.md mục 6.2 yêu cầu data-events.log phải có số dòng, không chỉ hash.
"""
import logging
from pathlib import Path
from unittest.mock import Mock

from app.main import _make_history_on_changed
from app.models.wip import WipSummary, WipTrolley

WIP_REPORT_FILENAME = "WIP Report_1.1.xlsx"


def _trolley() -> WipTrolley:
    return WipTrolley(
        trolley_code="T1",
        wb_code="WB1",
        area="CCT",
        so_no="SO1",
        mo_no="MO1",
        cust_style="S1",
        flower_code="A",
        color_code="00W",
        print_to_edge=None,
        bed_no=[],
        size_no=[],
        qty=10,
        loading_ws="WS1",
        loading_date=None,
        in_vap_date=None,
        back_cct_date=None,
        wip_cct=1,
        wip_vap=None,
        pdc_wip=None,
    )


def _summary() -> WipSummary:
    return WipSummary(
        cust_style="S1",
        graphic="A",
        mo_no="MO1",
        total_trolley=1,
        cut_qty=10,
        deduct_qty=0,
        qty_after_deduct=10,
        total_qty=10,
        avg_wip_cct=1.0,
        avg_wip_vap=None,
        avg_wip_pdc=None,
    )


def test_saves_snapshot_and_logs_row_count(tmp_path, monkeypatch):
    trolleys = [_trolley(), _trolley()]
    summaries = [_summary()]
    data_source = Mock()
    data_source.get_wip_trolleys.return_value = trolleys
    data_source.get_wip_summary.return_value = summaries
    logger = logging.getLogger("test.data_events")
    logger.info = Mock()

    import app.main as main_module

    monkeypatch.setattr(main_module.settings, "history_dir", tmp_path)

    on_changed = _make_history_on_changed(data_source, logger)
    on_changed(WIP_REPORT_FILENAME)

    saved = list(Path(tmp_path).glob("wip_detail_*.parquet"))
    assert len(saved) == 1
    logger.info.assert_called_once_with("file=%s rows=%d snapshot=saved", WIP_REPORT_FILENAME, 2)


def test_ignores_files_other_than_wip_report():
    data_source = Mock()
    logger = Mock()

    on_changed = _make_history_on_changed(data_source, logger)
    on_changed("DeliveryPanel_2.1.xlsx")

    data_source.get_wip_trolleys.assert_not_called()
    logger.info.assert_not_called()
