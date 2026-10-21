from __future__ import annotations

import asyncio
import json
import threading
import time

import pytest

from vectorclaw_mcp.repeat_guard import DEFAULT_WINDOW_S, RepeatGuard


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


OK = {"status": "ok"}


def test_identical_call_within_window_is_skipped():
    clock = FakeClock()
    guard = RepeatGuard(window_s=10, clock=clock)
    args = {"distance_mm": 100, "speed": 50}

    assert guard.check("vector_drive", args) is None
    guard.record("vector_drive", args, OK)

    clock.now += 3
    skipped = guard.check("vector_drive", args)
    assert skipped is not None
    assert skipped["status"] == "skipped"
    assert skipped["reason"] == "duplicate_call"
    assert "NOT repeated" in skipped["message"]


def test_call_after_window_is_allowed():
    clock = FakeClock()
    guard = RepeatGuard(window_s=10, clock=clock)
    guard.record("vector_say", {"text": "hi"}, OK)

    clock.now += 10
    assert guard.check("vector_say", {"text": "hi"}) is None


def test_different_arguments_are_allowed():
    guard = RepeatGuard(window_s=10, clock=FakeClock())
    guard.record("vector_say", {"text": "hi"}, OK)

    assert guard.check("vector_say", {"text": "bye"}) is None


def test_intervening_actuation_invalidates_previous_success():
    guard = RepeatGuard(window_s=10, clock=FakeClock())

    assert guard.begin("vector_lift", {"height": 0}) is None
    guard.finish("vector_lift", {"height": 0}, OK)
    assert guard.begin("vector_lift", {"height": 1}) is None
    guard.finish("vector_lift", {"height": 1}, OK)
    assert guard.check("vector_lift", {"height": 0}) is None

    assert guard.begin("vector_drive_on_charger", {}) is None
    guard.finish("vector_drive_on_charger", {}, OK)
    assert guard.begin("vector_drive_off_charger", {}) is None
    guard.finish("vector_drive_off_charger", {}, OK)
    assert guard.check("vector_drive_on_charger", {}) is None


def test_scan_movements_invalidate_cached_success_without_being_blocked():
    guard = RepeatGuard(window_s=10, clock=FakeClock())
    arguments = {"distance_mm": 100}

    for name in ("vector_scan", "vector_find_faces"):
        guard.record("vector_drive", arguments, OK)
        assert guard.begin(name, {}) is None
        assert guard.check("vector_drive", arguments) is None


def test_argument_order_does_not_matter():
    guard = RepeatGuard(window_s=10, clock=FakeClock())
    guard.record("vector_drive", {"distance_mm": 100, "speed": 50}, OK)

    assert guard.check("vector_drive", {"speed": 50, "distance_mm": 100}) is not None


def test_failed_calls_are_not_recorded():
    guard = RepeatGuard(window_s=10, clock=FakeClock())
    guard.record("vector_drive", {"distance_mm": 100}, {"status": "error", "message": "x"})

    assert guard.check("vector_drive", {"distance_mm": 100}) is None


def test_non_actuating_tools_are_never_blocked():
    guard = RepeatGuard(window_s=10, clock=FakeClock())
    for name in ("vector_status", "vector_look", "vector_emergency_stop"):
        guard.record(name, {}, OK)
        assert guard.check(name, {}) is None


def test_zero_window_disables_guard():
    guard = RepeatGuard(window_s=0, clock=FakeClock())
    guard.record("vector_say", {"text": "hi"}, OK)

    assert guard.check("vector_say", {"text": "hi"}) is None


def test_window_from_env(monkeypatch):
    monkeypatch.setenv("VECTOR_REPEAT_GUARD_SECONDS", "2.5")
    assert RepeatGuard().window_s == 2.5

    monkeypatch.setenv("VECTOR_REPEAT_GUARD_SECONDS", "0")
    assert RepeatGuard().window_s == 0

    monkeypatch.setenv("VECTOR_REPEAT_GUARD_SECONDS", "not-a-number")
    assert RepeatGuard().window_s == DEFAULT_WINDOW_S

    monkeypatch.delenv("VECTOR_REPEAT_GUARD_SECONDS")
    assert RepeatGuard().window_s == DEFAULT_WINDOW_S


def test_call_tool_skips_duplicate_say(mock_robot):
    from vectorclaw_mcp import server

    first = json.loads(asyncio.run(server.call_tool("vector_say", {"text": "hello"}))[0].text)
    second = json.loads(asyncio.run(server.call_tool("vector_say", {"text": "hello"}))[0].text)

    assert first["status"] == "ok"
    assert second["status"] == "skipped"
    assert mock_robot.behavior.say_text.call_count == 1


def test_call_tool_skips_concurrent_duplicate(monkeypatch):
    from vectorclaw_mcp import server

    calls = []

    def handler():
        calls.append(True)
        time.sleep(0.05)
        return OK

    monkeypatch.setattr(server, "build_dispatch", lambda arguments: {"vector_drive": handler})

    async def invoke_twice():
        return await asyncio.gather(
            server.call_tool("vector_drive", {}),
            server.call_tool("vector_drive", {}),
        )

    results = [json.loads(response[0].text) for response in asyncio.run(invoke_twice())]

    assert len(calls) == 1
    assert [result["status"] for result in results].count("ok") == 1
    assert [result["status"] for result in results].count("skipped") == 1


def test_call_tool_releases_reservation_after_exception(monkeypatch):
    from vectorclaw_mcp import server

    calls = []

    def handler():
        calls.append(True)
        if len(calls) == 1:
            raise RuntimeError("failed")
        return OK

    monkeypatch.setattr(server, "build_dispatch", lambda arguments: {"vector_drive": handler})

    async def invoke_twice():
        return (
            await server.call_tool("vector_drive", {}),
            await server.call_tool("vector_drive", {}),
        )

    first, second = [
        json.loads(response[0].text) for response in asyncio.run(invoke_twice())
    ]

    assert first["status"] == "error"
    assert second["status"] == "ok"
    assert len(calls) == 2


def test_cancelled_call_keeps_reservation_until_worker_finishes(monkeypatch):
    from vectorclaw_mcp import server

    started = threading.Event()
    release = threading.Event()

    def handler():
        started.set()
        release.wait(timeout=2)
        return OK

    monkeypatch.setattr(server, "build_dispatch", lambda arguments: {"vector_drive": handler})

    async def cancel_call():
        task = asyncio.create_task(server.call_tool("vector_drive", {}))
        assert await asyncio.to_thread(started.wait, 1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(cancel_call())

    still_running = json.loads(
        asyncio.run(server.call_tool("vector_drive", {}))[0].text
    )
    assert still_running["status"] == "skipped"
    assert "already in progress" in still_running["message"]

    release.set()
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        completed = server.repeat_guard.check("vector_drive", {})
        if completed is not None and "already succeeded" in completed["message"]:
            break
        time.sleep(0.01)
    assert completed is not None
    assert "already succeeded" in completed["message"]
