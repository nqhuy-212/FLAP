"""Điểm chạy ngầm bằng `pythonw` — không cửa sổ console, khởi động qua Task
Scheduler (xem `scripts/install-task.ps1`). Xem CLAUDE.md mục 6.1.

⚠️ Dưới `pythonw`, `sys.stdout`/`sys.stderr` là `None`. Bất kỳ `print()` nào
(kể cả từ thư viện bên thứ ba) sẽ ném `AttributeError` và app chết câm lặng,
không để lại dấu vết. Việc ĐẦU TIÊN trong file này — trước cả import
`app.config` — là gán lại `sys.stdout`/`sys.stderr` vào `crash.log`, bật
`faulthandler`, rồi bọc toàn bộ phần còn lại trong `try/except` ghi lại đây.

`crash.log` mở trực tiếp bằng `open()`, không qua `logging_config.py`
(TimedRotatingFileHandler) — phải sẵn sàng trước khi bất kỳ import nào khác
(kể cả `app.config` đọc `.env`) có cơ hội ném lỗi.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
# Trùng giá trị mặc định của FLAP_LOG_DIR. Nếu .env đổi khác, các log xoay
# vòng (app/access/error/data-events) sẽ dùng đúng thư mục thật qua
# `settings.log_dir` trong main() bên dưới — chỗ này chỉ là lưới an toàn sớm
# nhất, trước cả khi Settings() kịp đọc .env.
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

_crash_log = open(LOG_DIR / "crash.log", "a", encoding="utf-8", buffering=1)

if sys.stdout is None:
    sys.stdout = _crash_log
if sys.stderr is None:
    sys.stderr = _crash_log

import faulthandler  # noqa: E402

faulthandler.enable(file=_crash_log)

sys.path.insert(0, str(BACKEND_DIR))


def main() -> None:
    import uvicorn

    from app.config import settings
    from app.logging_config import configure_logging, get_app_logger

    configure_logging()
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    # PID file cho scripts/stop.cmd + scripts/restart.cmd (không có cửa sổ
    # console để Ctrl+C dưới pythonw).
    (settings.log_dir / "flap.pid").write_text(str(os.getpid()), encoding="utf-8")
    get_app_logger().info("run_server: khởi động, pid=%d, port=%d", os.getpid(), settings.port)

    # 1 worker cố ý (CLAUDE.md quyết định #9): EventBus + watcher chỉ được
    # chạy đúng 1 lần trong RAM. reload=False: production, không theo dõi
    # thay đổi mã nguồn. log_config=None: uvicorn mặc định TỰ dictConfig lại
    # toàn bộ logger "uvicorn.access"/"uvicorn.error" SAU KHI app đã import
    # xong (tức sau configure_logging() ở trên) — ghi đè mất handler ghi vào
    # access.log, request vẫn chạy đúng nhưng access.log rỗng im lặng (bug
    # thật gặp khi kiểm chứng Bước 7). log_config=None giữ nguyên cấu hình đã
    # đặt trong configure_logging().
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=False,
        workers=1,
        log_config=None,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc(file=_crash_log)
        _crash_log.flush()
        raise
