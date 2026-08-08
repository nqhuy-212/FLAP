"""SSE — xem CLAUDE.md quyết định #2: `EventSource` tự kết nối lại khi rớt
mạng, thiết yếu với TV chạy 24/7. Không cần thư viện ngoài — `StreamingResponse`
kèm heartbeat định kỳ để giữ kết nối và giúp client phát hiện rớt mạng sớm.
"""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse

from app.core.events import DataChangedEvent, EventBus

router = APIRouter()

HEARTBEAT_SECONDS = 15.0


async def _event_generator(request: Request, event_bus: EventBus, queue: asyncio.Queue[DataChangedEvent]):
    try:
        while True:
            if await request.is_disconnected():
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=HEARTBEAT_SECONDS)
            except asyncio.TimeoutError:
                yield ": heartbeat\n\n"
                continue
            payload = json.dumps({"file": event.file})
            yield f"event: data_changed\ndata: {payload}\n\n"
    finally:
        event_bus.unsubscribe(queue)


@router.get("/stream")
async def stream(request: Request) -> StreamingResponse:
    event_bus: EventBus = request.app.state.event_bus
    queue = event_bus.subscribe()
    return StreamingResponse(
        _event_generator(request, event_bus, queue),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
