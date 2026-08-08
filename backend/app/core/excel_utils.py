"""Hàm thuần dùng chung cho mọi DataSource đọc Excel.

Các bẫy dữ liệu đã kiểm chứng trên file thật — xem CLAUDE.md mục 4.1.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

EXCEL_EPOCH = datetime(1899, 12, 30)


def excel_serial_to_datetime(value: Any) -> datetime | None:
    """Chuyển serial ngày Excel (hệ 1900, vd 46234.748997) sang datetime.

    Trả None cho giá trị rỗng, chuỗi "NULL", hoặc NaN/NaT. Nếu pandas đã tự
    parse sẵn thành datetime (cột có định dạng ngày trong file) thì giữ nguyên.
    """
    if value is None:
        return None
    # pandas.NaT (ô ngày trống) là subclass của datetime — phải loại trước khi
    # kiểm tra isinstance(datetime), nếu không sẽ bị coi là "đã có giá trị hợp lệ".
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "" or stripped.upper() == "NULL":
            return None
        value = float(stripped)
    return EXCEL_EPOCH + timedelta(days=float(value))


def clean_null(value: Any) -> Any | None:
    """Chuẩn hoá ô trống: chuỗi "NULL", chuỗi rỗng, NaN đều thành None."""
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "" or stripped.upper() == "NULL":
            return None
        return stripped
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def split_multi_value(value: Any, sep: str = ",") -> list[str]:
    """Tách ô chứa nhiều giá trị (vd Bed_No = "34003,34004") thành list.

    Ô trống / "NULL" trả về list rỗng, không phải [None].
    """
    cleaned = clean_null(value)
    if cleaned is None:
        return []
    return [part.strip() for part in str(cleaned).split(sep) if part.strip() != ""]


def read_banner_sheet(
    path: str | Path,
    sheet_name: str,
    header_row: int,
    engine: str = "calamine",
) -> pd.DataFrame:
    """Đọc 1 sheet có banner phía trên header (WIP Report, DeliveryPanel).

    `header_row` là số dòng header tính từ 1 (vd 5 nghĩa là header ở dòng 5).
    pandas tự bỏ mọi dòng phía trên header — không cần tách banner thủ công.
    """
    try:
        return pd.read_excel(
            path, sheet_name=sheet_name, header=header_row - 1, engine=engine
        )
    except Exception:
        # dự phòng: calamine có thể vắng hoặc không đọc được file — dùng openpyxl
        return pd.read_excel(
            path, sheet_name=sheet_name, header=header_row - 1, engine="openpyxl"
        )


_BANNER_DATE_RE = re.compile(r"Date:\s*(\d{2}-\d{2}-\d{4})")
_BANNER_TIME_RE = re.compile(r"Time:\s*(\d{1,2}:\d{2}:\d{2}\s*[AP]M)")


def read_banner_generated_at(
    path: str | Path, sheet_name: str, engine: str = "calamine"
) -> datetime | None:
    """Đọc thời điểm MES xuất báo cáo từ dòng banner "Date: .../Time: ...".

    Dùng cho các sheet có banner 4 dòng (WIP Report, DeliveryPanel). Trả None
    nếu không tìm thấy — không phải lỗi, chỉ là banner không theo mẫu đã biết.
    """
    try:
        raw = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=4, engine=engine)
    except Exception:
        raw = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=4, engine="openpyxl")
    text = " ".join(str(v) for v in raw.to_numpy().flatten() if pd.notna(v))
    date_match = _BANNER_DATE_RE.search(text)
    time_match = _BANNER_TIME_RE.search(text)
    if not date_match or not time_match:
        return None
    return datetime.strptime(f"{date_match.group(1)} {time_match.group(1)}", "%d-%m-%Y %I:%M:%S %p")


def select_columns_by_position(
    df: pd.DataFrame, positions: dict[str, int]
) -> pd.DataFrame:
    """Chọn cột theo VỊ TRÍ (0-indexed), không theo tên.

    Dùng cho sheet có tên cột trùng nhau do bị làm phẳng từ bảng join
    (vd Heat_7.1 Sheet2: RID ở cột C và AS). Tra theo tên trong trường hợp
    này sẽ âm thầm lấy nhầm cột.
    """
    return pd.DataFrame(
        {name: df.iloc[:, pos] for name, pos in positions.items()}
    )
