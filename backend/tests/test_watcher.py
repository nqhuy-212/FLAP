"""Test ExcelWatcher — dùng tmp_path, không đụng "EXCEL files/" thật.

Gọi thẳng `_check_file`/`_seed_hashes` thay vì chờ watchdog Observer bắn
event thật (chậm và phụ thuộc OS) — vẫn kiểm đúng logic hash/debounce/bỏ qua
file khoá, vốn là phần dễ sai nhất theo CLAUDE.md quyết định #4.
"""
import time

from app.core.events import DataChangedEvent, EventBus
from app.services.watcher import ExcelWatcher, _hash_file

WIP_NAME = "WIP Report_1.1.xlsx"


class _CollectingBus(EventBus):
    """Test double: ghi lại event thay vì gửi qua asyncio queue thật."""

    def __init__(self):
        super().__init__()
        self.published: list[DataChangedEvent] = []

    def publish(self, event: DataChangedEvent) -> None:
        self.published.append(event)


class TestHashFile:
    def test_changes_with_content(self, tmp_path):
        p = tmp_path / WIP_NAME
        p.write_bytes(b"abc")
        h1 = _hash_file(p)
        p.write_bytes(b"abcd")
        h2 = _hash_file(p)
        assert h1 != h2
        assert h1 is not None and h2 is not None

    def test_missing_file_returns_none(self, tmp_path):
        assert _hash_file(tmp_path / "missing.xlsx") is None


class TestCheckFile:
    def test_publishes_on_real_content_change(self, tmp_path):
        path = tmp_path / WIP_NAME
        path.write_bytes(b"v1")
        bus = _CollectingBus()
        changed: list[str] = []
        watcher = ExcelWatcher(tmp_path, bus, on_changed=changed.append)
        watcher._seed_hashes()

        path.write_bytes(b"v2")
        watcher._check_file(WIP_NAME)

        assert [e.file for e in bus.published] == [WIP_NAME]
        assert changed == [WIP_NAME]

    def test_skips_when_content_unchanged(self, tmp_path):
        path = tmp_path / WIP_NAME
        path.write_bytes(b"same")
        bus = _CollectingBus()
        watcher = ExcelWatcher(tmp_path, bus)
        watcher._seed_hashes()

        watcher._check_file(WIP_NAME)  # chưa đổi gì -> không được publish giả

        assert bus.published == []

    def test_no_seed_treats_existing_content_as_new(self, tmp_path):
        # Không seed trước (vd file xuất hiện lần đầu khi watcher đang chạy)
        # -> lần _check_file đầu tiên phải coi là có thay đổi thật.
        path = tmp_path / WIP_NAME
        path.write_bytes(b"first content")
        bus = _CollectingBus()
        watcher = ExcelWatcher(tmp_path, bus)

        watcher._check_file(WIP_NAME)

        assert len(bus.published) == 1


class TestNotifyPathChanged:
    def test_ignores_lock_files(self, tmp_path):
        bus = _CollectingBus()
        watcher = ExcelWatcher(tmp_path, bus, debounce_seconds=0.02)
        watcher.notify_path_changed(tmp_path / f"~${WIP_NAME}")
        time.sleep(0.08)
        assert bus.published == []

    def test_ignores_unwatched_filenames(self, tmp_path):
        bus = _CollectingBus()
        watcher = ExcelWatcher(tmp_path, bus, debounce_seconds=0.02)
        watcher.notify_path_changed(tmp_path / "random_file.txt")
        time.sleep(0.08)
        assert bus.published == []

    def test_debounces_rapid_successive_events_into_one_check(self, tmp_path):
        path = tmp_path / WIP_NAME
        path.write_bytes(b"v1")
        bus = _CollectingBus()
        watcher = ExcelWatcher(tmp_path, bus, debounce_seconds=0.05)
        watcher._seed_hashes()
        path.write_bytes(b"v2")

        for _ in range(5):
            watcher.notify_path_changed(path)
            time.sleep(0.01)
        time.sleep(0.15)

        assert len(bus.published) == 1
