"""EventBus in-memory cho SSE — xem CLAUDE.md quyết định #2 và #9.

Chỉ đúng khi chạy **1 uvicorn worker** (quyết định #9): EventBus sống trong
RAM của một process duy nhất, watcher cũng chỉ chạy một lần. `publish()` an
toàn gọi từ thread khác (watcher chạy trên thread riêng của watchdog).
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class DataChangedEvent:
    file: str


class EventBus:
    def __init__(self) -> None:
        self._subscribers: list[asyncio.Queue[DataChangedEvent]] = []
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Gọi 1 lần lúc FastAPI startup — publish() cần loop để gọi threadsafe."""
        self._loop = loop

    def subscribe(self) -> asyncio.Queue[DataChangedEvent]:
        queue: asyncio.Queue[DataChangedEvent] = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[DataChangedEvent]) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    def publish(self, event: DataChangedEvent) -> None:
        if self._loop is None:
            # Chưa bind loop (vd gọi từ test hoặc trước startup) — bỏ qua an toàn.
            return
        for queue in list(self._subscribers):
            self._loop.call_soon_threadsafe(queue.put_nowait, event)
