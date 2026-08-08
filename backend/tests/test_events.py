"""Test EventBus — chạy loop thủ công, không cần pytest-asyncio/anyio."""
import asyncio

from app.core.events import DataChangedEvent, EventBus


def test_publish_delivers_to_subscriber():
    bus = EventBus()
    loop = asyncio.new_event_loop()
    try:
        bus.bind_loop(loop)
        queue = bus.subscribe()
        bus.publish(DataChangedEvent(file="a.xlsx"))
        loop.run_until_complete(asyncio.sleep(0))  # để call_soon_threadsafe chạy
        event = loop.run_until_complete(queue.get())
        assert event.file == "a.xlsx"
    finally:
        loop.close()


def test_publish_without_bound_loop_is_noop():
    bus = EventBus()
    bus.publish(DataChangedEvent(file="a.xlsx"))  # không raise


def test_unsubscribe_stops_delivery():
    bus = EventBus()
    loop = asyncio.new_event_loop()
    try:
        bus.bind_loop(loop)
        queue = bus.subscribe()
        bus.unsubscribe(queue)
        bus.publish(DataChangedEvent(file="a.xlsx"))
        loop.run_until_complete(asyncio.sleep(0))
        assert queue.empty()
    finally:
        loop.close()


def test_multiple_subscribers_all_receive():
    bus = EventBus()
    loop = asyncio.new_event_loop()
    try:
        bus.bind_loop(loop)
        q1 = bus.subscribe()
        q2 = bus.subscribe()
        bus.publish(DataChangedEvent(file="x.xlsx"))
        loop.run_until_complete(asyncio.sleep(0))
        assert loop.run_until_complete(q1.get()).file == "x.xlsx"
        assert loop.run_until_complete(q2.get()).file == "x.xlsx"
    finally:
        loop.close()
