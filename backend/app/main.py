from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import routes_meta, routes_stream, routes_system, routes_wip
from app.config import PROJECT_ROOT, settings
from app.core.events import EventBus
from app.datasource.excel_source import ExcelDataSource, WIP_REPORT_FILENAME
from app.logging_config import configure_logging, get_app_logger, get_data_events_logger
from app.services.history import save_wip_snapshot
from app.services.watcher import ExcelWatcher

FRONTEND_OUT_DIR = PROJECT_ROOT / "frontend" / "out"


def _make_history_on_changed(data_source: ExcelDataSource, logger: logging.Logger):
    def _on_changed(filename: str) -> None:
        # Chỉ WIP Report đã hiện thực đọc — 4 file còn lại chờ Bước 8, gọi
        # get_wip_trolleys()/get_wip_summary() cho chúng sẽ raise NotImplementedError.
        if filename != WIP_REPORT_FILENAME:
            return
        trolleys = data_source.get_wip_trolleys()
        summaries = data_source.get_wip_summary()
        save_wip_snapshot(trolleys, summaries, settings.history_dir)
        # CLAUDE.md mục 6.2: data-events.log phải có số dòng, không chỉ hash.
        logger.info("file=%s rows=%d snapshot=saved", filename, len(trolleys))

    return _on_changed


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger = get_app_logger()
    app.state.event_bus.bind_loop(asyncio.get_running_loop())
    app.state.watcher.start()
    app_logger.info("watcher started, datasource=%s port=%d", settings.datasource, settings.port)
    try:
        yield
    finally:
        app.state.watcher.stop()
        app_logger.info("watcher stopped")


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="FLAP Dashboard API", root_path=settings.base_path, lifespan=lifespan)

    if settings.cors_origins_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,
            allow_methods=["GET"],
            allow_headers=["*"],
        )

    data_source = ExcelDataSource(settings.data_dir)
    event_bus = EventBus()
    data_events_logger = get_data_events_logger()
    watcher = ExcelWatcher(
        data_dir=settings.data_dir,
        event_bus=event_bus,
        on_changed=_make_history_on_changed(data_source, data_events_logger),
        logger=data_events_logger,
    )

    app.state.data_source = data_source
    app.state.event_bus = event_bus
    app.state.watcher = watcher

    app.include_router(routes_meta.router, prefix="/api/meta", tags=["meta"])
    app.include_router(routes_wip.router, prefix="/api/wip", tags=["wip"])
    app.include_router(routes_stream.router, prefix="/api", tags=["stream"])
    app.include_router(routes_system.router, prefix="/api/system", tags=["system"])

    # Mount SAU CÙNG: frontend build tĩnh (`next build`, output:'export') phục
    # vụ tại "/" — chỉ khớp những path chưa route nào ở trên xử lý, nên không
    # che các endpoint /api/*. Không tồn tại khi chạy dev backend đơn lẻ trước
    # khi build frontend lần đầu — bỏ qua, không phải lỗi.
    if FRONTEND_OUT_DIR.is_dir():
        app.mount("/", StaticFiles(directory=str(FRONTEND_OUT_DIR), html=True), name="frontend")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    # reload_dirs="app": mặc định uvicorn theo dõi CẢ thư mục cwd (backend/),
    # kể cả .venv/ — cache .pyc sinh ra lúc chạy thật (vd pyarrow chạy lần đầu)
    # bị hiểu nhầm là đổi code, worker bị restart ngầm, rớt kết nối SSE đang mở
    # (bug thật gặp ở Bước 5: SSE hoạt động qua curl/test nhưng im lặng sau vài
    # phút chạy — event vẫn phát ở watcher/log nhưng không tới client nào).
    # log_config=None: xem giải thích trong run_server.py — giữ nguyên
    # access.log do configure_logging() thiết lập, không để uvicorn ghi đè.
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        reload_dirs=["app"],
        log_config=None,
    )
