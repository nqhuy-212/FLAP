"""Log xoay vòng UTF-8. Xem CLAUDE.md mục 6.2.

`data-events.log` làm từ Bước 3 (bằng chứng lần watcher phát hiện dữ liệu
đổi). `app.log`/`access.log`/`error.log`/`crash.log` nối vào ở Bước 7 —
`configure_logging()` được gọi từ `create_app()` nên có hiệu lực bất kể chạy
bằng `python -m app.main` (dev) hay `run_server.py` (production, pythonw).
`crash.log` không xoay vòng — mở trực tiếp bằng `open()` trong `run_server.py`
vì phải sẵn sàng trước khi bất kỳ import nào khác có thể ném lỗi.
"""
from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler

from app.config import settings

_FORMATTER = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

_data_events_logger: logging.Logger | None = None
_configured = False


def get_data_events_logger() -> logging.Logger:
    global _data_events_logger
    if _data_events_logger is not None:
        return _data_events_logger

    settings.log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("flap.data_events")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = TimedRotatingFileHandler(
        settings.log_dir / "data-events.log",
        when="midnight",
        backupCount=90,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(handler)

    _data_events_logger = logger
    return logger


def get_app_logger() -> logging.Logger:
    """Logger `flap.app` — nhật ký ứng dụng chung (khởi động, tắt, cảnh báo)."""
    return logging.getLogger("flap.app")


def configure_logging() -> None:
    """Bật `app.log`/`access.log`/`error.log`. Gọi 1 lần, idempotent trong 1 process."""
    global _configured
    if _configured:
        return
    _configured = True

    settings.log_dir.mkdir(parents=True, exist_ok=True)

    # app.log: nhật ký ứng dụng (flap.app), giữ 30 ngày.
    app_logger = get_app_logger()
    app_logger.setLevel(logging.INFO)
    app_handler = TimedRotatingFileHandler(
        settings.log_dir / "app.log", when="midnight", backupCount=30, encoding="utf-8"
    )
    app_handler.setFormatter(_FORMATTER)
    app_logger.addHandler(app_handler)
    # propagate=True (mặc định): WARNING+ của flap.app vẫn lên root -> error.log.

    # access.log: log truy cập HTTP của uvicorn, giữ 14 ngày — tách khỏi
    # console/crash.log vì dưới pythonw stdout đã bị chiếm cho crash.log.
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers.clear()
    access_logger.propagate = False
    access_handler = TimedRotatingFileHandler(
        settings.log_dir / "access.log", when="midnight", backupCount=14, encoding="utf-8"
    )
    access_handler.setFormatter(_FORMATTER)
    access_logger.addHandler(access_handler)

    # error.log: mọi logger có propagate=True, từ WARNING trở lên, giữ 90 ngày.
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    error_handler = TimedRotatingFileHandler(
        settings.log_dir / "error.log", when="midnight", backupCount=90, encoding="utf-8"
    )
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(_FORMATTER)
    root_logger.addHandler(error_handler)
