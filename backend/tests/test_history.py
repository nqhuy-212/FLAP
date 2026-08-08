"""Test services/history.py — lưu snapshot Parquet."""
from datetime import datetime

import pandas as pd

from app.models.wip import WipSummary, WipTrolley
from app.services.history import save_wip_snapshot


def _trolley(**overrides) -> WipTrolley:
    base = dict(
        trolley_code="T1",
        wb_code="WB1",
        area="CCT",
        so_no="SO1",
        mo_no="MO1",
        cust_style="S1",
        flower_code="A",
        color_code="00W",
        print_to_edge=None,
        bed_no=["1", "2"],
        size_no=["S"],
        qty=10,
        loading_ws="WS1",
        loading_date=None,
        in_vap_date=None,
        back_cct_date=None,
        wip_cct=1,
        wip_vap=None,
        pdc_wip=None,
    )
    base.update(overrides)
    return WipTrolley(**base)


def _summary(**overrides) -> WipSummary:
    base = dict(
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
    base.update(overrides)
    return WipSummary(**base)


def test_saves_two_parquet_files_with_correct_row_counts(tmp_path):
    trolleys = [_trolley(trolley_code=f"T{i}") for i in range(3)]
    summaries = [_summary(mo_no=f"MO{i}") for i in range(2)]
    at = datetime(2026, 8, 7, 10, 30, 0)

    detail_path, summary_path = save_wip_snapshot(trolleys, summaries, tmp_path, at=at)

    assert detail_path.name == "wip_detail_20260807_103000.parquet"
    assert summary_path.name == "wip_summary_20260807_103000.parquet"
    assert detail_path.exists()
    assert summary_path.exists()

    detail_df = pd.read_parquet(detail_path)
    summary_df = pd.read_parquet(summary_path)
    assert len(detail_df) == 3
    assert len(summary_df) == 2
    assert list(detail_df["trolley_code"]) == ["T0", "T1", "T2"]


def test_creates_history_dir_if_missing(tmp_path):
    nested = tmp_path / "a" / "b"
    save_wip_snapshot([], [], nested)
    assert nested.exists()


def test_list_columns_survive_roundtrip(tmp_path):
    # bed_no/size_no là list[str] -> phải chắc pyarrow lưu/đọc lại đúng, không phẳng hoá thành chuỗi
    trolleys = [_trolley(bed_no=["34003", "34004"], size_no=["3XL", "4XL"])]
    detail_path, _ = save_wip_snapshot(trolleys, [], tmp_path)
    df = pd.read_parquet(detail_path)
    assert list(df.loc[0, "bed_no"]) == ["34003", "34004"]
