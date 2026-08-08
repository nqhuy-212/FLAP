"""Lưu snapshot Parquet vào data/history/ — xem CLAUDE.md quyết định #7.

Excel bị ghi đè mỗi lần MES xuất lại nên quá khứ mất vĩnh viễn nếu không lưu.
Lưu cả `WipSummary` vì `Cut_Qty`/`Deduct_Qty`/`Qty_After_Deduct` là SOURCE —
không tính lại được từ `WipTrolley` (xem CLAUDE.md mục 5.3).
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from app.models.wip import WipSummary, WipTrolley


def save_wip_snapshot(
    trolleys: list[WipTrolley],
    summaries: list[WipSummary],
    history_dir: Path,
    at: datetime | None = None,
) -> tuple[Path, Path]:
    at = at or datetime.now()
    history_dir = Path(history_dir)
    history_dir.mkdir(parents=True, exist_ok=True)

    stamp = at.strftime("%Y%m%d_%H%M%S")
    detail_path = history_dir / f"wip_detail_{stamp}.parquet"
    summary_path = history_dir / f"wip_summary_{stamp}.parquet"

    pd.DataFrame([t.model_dump() for t in trolleys]).to_parquet(
        detail_path, engine="pyarrow", index=False
    )
    pd.DataFrame([s.model_dump() for s in summaries]).to_parquet(
        summary_path, engine="pyarrow", index=False
    )
    return detail_path, summary_path
