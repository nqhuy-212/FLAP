"""Trạng thái vận hành cho trang /pc/system — xem PLAN.md Bước 7."""
from __future__ import annotations

from pydantic import BaseModel

from app.models.meta import SnapshotInfo


class LogTail(BaseModel):
    name: str
    lines: list[str]


class SystemStatus(BaseModel):
    status: str
    datasource: str
    uptime_seconds: float
    watcher_running: bool
    snapshot: SnapshotInfo
    logs: list[LogTail]
