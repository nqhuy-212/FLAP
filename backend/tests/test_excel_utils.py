"""Test hàm thuần trong core/excel_utils.py — không cần file Excel thật."""
from datetime import datetime

import pandas as pd
import pytest

from app.core.excel_utils import (
    clean_null,
    excel_serial_to_datetime,
    select_columns_by_position,
    split_multi_value,
)


class TestExcelSerialToDatetime:
    def test_converts_known_serial(self):
        # CLAUDE.md mục 4.1: ví dụ thực tế 46234.748997
        result = excel_serial_to_datetime(46234.748997)
        assert result == datetime(1899, 12, 30) + pd.Timedelta(days=46234.748997)

    def test_converts_string_serial(self):
        assert excel_serial_to_datetime("46220.7854445602") == datetime(
            1899, 12, 30
        ) + pd.Timedelta(days=46220.7854445602)

    def test_none_for_none(self):
        assert excel_serial_to_datetime(None) is None

    def test_none_for_null_string(self):
        assert excel_serial_to_datetime("NULL") is None
        assert excel_serial_to_datetime("null") is None
        assert excel_serial_to_datetime("  ") is None

    def test_none_for_nan(self):
        assert excel_serial_to_datetime(float("nan")) is None

    def test_none_for_nat(self):
        # pandas.NaT là subclass của datetime — bug thật đã gặp ở Bước 2:
        # cột ngày trống mà pandas tự parse thành datetime64 trả về NaT,
        # bị nhánh isinstance(datetime) coi nhầm là giá trị hợp lệ.
        assert excel_serial_to_datetime(pd.NaT) is None

    def test_passthrough_already_datetime(self):
        dt = datetime(2026, 7, 31, 15, 30)
        assert excel_serial_to_datetime(dt) is dt


class TestCleanNull:
    def test_null_string_becomes_none(self):
        assert clean_null("NULL") is None

    def test_blank_string_becomes_none(self):
        assert clean_null("") is None
        assert clean_null("   ") is None

    def test_nan_becomes_none(self):
        assert clean_null(float("nan")) is None

    def test_real_value_passthrough(self):
        assert clean_null("201965") == "201965"
        assert clean_null(395) == 395

    def test_strips_whitespace(self):
        assert clean_null("  201965  ") == "201965"


class TestSplitMultiValue:
    def test_splits_comma_separated(self):
        assert split_multi_value("34003,34004") == ["34003", "34004"]

    def test_splits_with_spaces(self):
        assert split_multi_value("3XL,4XL,XXL") == ["3XL", "4XL", "XXL"]

    def test_null_becomes_empty_list(self):
        assert split_multi_value("NULL") == []

    def test_blank_becomes_empty_list(self):
        assert split_multi_value("") == []
        assert split_multi_value(None) == []

    def test_single_value_no_separator(self):
        assert split_multi_value("124204") == ["124204"]


class TestSelectColumnsByPosition:
    def test_selects_by_position_not_name(self):
        # Mô phỏng Heat_7.1 Sheet2: cột "RID" xuất hiện ở cả vị trí 2 và 5,
        # phải lấy đúng theo vị trí, không được lấy nhầm cột trùng tên.
        df = pd.DataFrame(
            [
                ["a", "b", "master-RID", "x", "y", "detail-RID"],
                ["a2", "b2", "master-RID-2", "x2", "y2", "detail-RID-2"],
            ]
        )
        result = select_columns_by_position(
            df, {"RID_master": 2, "RID_detail": 5}
        )
        assert result["RID_master"].tolist() == ["master-RID", "master-RID-2"]
        assert result["RID_detail"].tolist() == ["detail-RID", "detail-RID-2"]
