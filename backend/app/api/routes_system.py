"""Trang `/pc/system` xem trạng thái + log **không cần Terminal** (PLAN.md
Bước 7). Bảo vệ bằng token vì log chứa **tên thật nhân viên** (`Relaxed_3.1.xlsx`,
xem CLAUDE.md mục 4.1) — không được xem không cần xác thực. `FLAP_SYSTEM_TOKEN`
rỗng = tắt hẳn endpoint (503), không mặc định mở "cho tiện test".
"""
from __future__ import annotations

import hmac
import time
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.deps import get_data_source
from app.config import settings
from app.datasource.base import DataSource
from app.models.system import LogTail, SystemStatus

router = APIRouter()

_START_TIME = time.monotonic()
_TAIL_LINES = 200
_LOG_FILES = ("app.log", "access.log", "error.log", "data-events.log", "crash.log")


def _require_token(token: str | None) -> None:
    if not settings.system_token:
        raise HTTPException(status_code=503, detail="FLAP_SYSTEM_TOKEN chưa được cấu hình")
    if not token or not hmac.compare_digest(token, settings.system_token):
        raise HTTPException(status_code=403, detail="Token không hợp lệ")


def _tail(path: Path, n: int) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-n:]


@router.get("/status", response_model=SystemStatus)
def status(
    request: Request,
    token: str | None = None,
    source: DataSource = Depends(get_data_source),
) -> SystemStatus:
    _require_token(token)
    watcher = request.app.state.watcher
    logs = [LogTail(name=name, lines=_tail(settings.log_dir / name, _TAIL_LINES)) for name in _LOG_FILES]
    return SystemStatus(
        status="ok",
        datasource=settings.datasource,
        uptime_seconds=time.monotonic() - _START_TIME,
        watcher_running=watcher.is_running,
        snapshot=source.get_snapshot_info(),
        logs=logs,
    )
