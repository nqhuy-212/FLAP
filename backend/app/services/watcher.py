"""Watcher chống file ghi dở — xem CLAUDE.md quyết định #4.

Excel xuất thủ công, file có thể đang copy hoặc đang mở. Xử lý:
- Debounce (mặc định 2s): gộp nhiều event liên tiếp khi copy thành 1 lần kiểm tra.
- Retry khi `PermissionError` (file đang bị khoá lúc copy dở).
- Bỏ qua `~$*.xlsx` (file khoá tạm của Excel).
- So **hash nội dung**, không chỉ mtime — tránh đẩy sự kiện giả khi nội dung
  không đổi (vd mở rồi đóng file mà không sửa gì).
- Poll dự phòng (mặc định 30s): copy qua network drive đôi khi không sinh event.
"""
from __future__ import annotations

import hashlib
import logging
import threading
import time
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from app.core.events import DataChangedEvent, EventBus

WATCHED_FILENAMES = frozenset(
    {
        "WIP Report_1.1.xlsx",
        "DeliveryPanel_2.1.xlsx",
        "Heat_7.1.xlsx",
        "order_8.1.xlsx",
        "Relaxed_3.1.xlsx",
    }
)

DEFAULT_DEBOUNCE_SECONDS = 2.0
DEFAULT_POLL_INTERVAL_SECONDS = 30.0
READ_RETRY_ATTEMPTS = 5
READ_RETRY_DELAY_SECONDS = 0.5


def _hash_file(path: Path) -> str | None:
    """Đọc + hash nội dung file, retry khi bị khoá. None nếu không đọc được."""
    for _ in range(READ_RETRY_ATTEMPTS):
        try:
            return hashlib.sha256(path.read_bytes()).hexdigest()
        except PermissionError:
            time.sleep(READ_RETRY_DELAY_SECONDS)
        except FileNotFoundError:
            return None
    return None


class ExcelWatcher:
    """Theo dõi thư mục Excel, đẩy DataChangedEvent qua EventBus khi nội dung đổi thật."""

    def __init__(
        self,
        data_dir: Path,
        event_bus: EventBus,
        on_changed: Callable[[str], None] | None = None,
        logger: logging.Logger | None = None,
        debounce_seconds: float = DEFAULT_DEBOUNCE_SECONDS,
        poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.event_bus = event_bus
        self.on_changed = on_changed
        self.logger = logger or logging.getLogger("flap.data_events")
        self.debounce_seconds = debounce_seconds
        self.poll_interval_seconds = poll_interval_seconds

        self._hashes: dict[str, str] = {}
        self._debounce_timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()
        self._observer: Observer | None = None
        self._poll_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        self._seed_hashes()

        self._observer = Observer()
        self._observer.schedule(_Handler(self), str(self.data_dir), recursive=False)
        self._observer.start()

        self._stop_event.clear()
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()

    @property
    def is_running(self) -> bool:
        return self._observer is not None and self._observer.is_alive()

    def stop(self) -> None:
        self._stop_event.set()
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=5)
        with self._lock:
            for timer in self._debounce_timers.values():
                timer.cancel()
            self._debounce_timers.clear()

    def _seed_hashes(self) -> None:
        """Ghi nhận hash hiện tại khi khởi động — không đẩy sự kiện cho dữ liệu đã có sẵn."""
        for name in WATCHED_FILENAMES:
            path = self.data_dir / name
            if path.exists():
                h = _hash_file(path)
                if h is not None:
                    self._hashes[name] = h

    def _poll_loop(self) -> None:
        while not self._stop_event.wait(self.poll_interval_seconds):
            for name in WATCHED_FILENAMES:
                self._check_file(name)

    def notify_path_changed(self, path: Path) -> None:
        name = path.name
        if name.startswith("~$") or name not in WATCHED_FILENAMES:
            return
        with self._lock:
            existing = self._debounce_timers.get(name)
            if existing is not None:
                existing.cancel()
            timer = threading.Timer(self.debounce_seconds, self._check_file, args=(name,))
            timer.daemon = True
            self._debounce_timers[name] = timer
            timer.start()

    def _check_file(self, name: str) -> None:
        path = self.data_dir / name
        new_hash = _hash_file(path)
        if new_hash is None:
            return
        if self._hashes.get(name) == new_hash:
            return  # nội dung không đổi thật -> không đẩy sự kiện giả
        self._hashes[name] = new_hash
        self.logger.info("file=%s hash=%s", name, new_hash[:12])
        self.event_bus.publish(DataChangedEvent(file=name))
        if self.on_changed is not None:
            self.on_changed(name)


class _Handler(FileSystemEventHandler):
    def __init__(self, watcher: ExcelWatcher) -> None:
        self._watcher = watcher

    def on_created(self, event) -> None:
        if not event.is_directory:
            self._watcher.notify_path_changed(Path(event.src_path))

    def on_modified(self, event) -> None:
        if not event.is_directory:
            self._watcher.notify_path_changed(Path(event.src_path))

    def on_moved(self, event) -> None:
        if not event.is_directory:
            self._watcher.notify_path_changed(Path(event.dest_path))
