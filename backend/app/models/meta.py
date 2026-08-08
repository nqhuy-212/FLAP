"""Siêu dữ liệu mô tả nguồn dữ liệu hiện tại (Excel hay SQL, lúc nào, mấy dòng)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SourceFileInfo(BaseModel):
    name: str
    generated_at: datetime | None  # đọc từ banner "Date/Time" trong file, None nếu không có
    modified_at: datetime  # mtime của file trên đĩa
    row_count: int


class SnapshotInfo(BaseModel):
    source: str  # "excel" | "sql"
    files: list[SourceFileInfo]
