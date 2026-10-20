from __future__ import annotations

import asyncio
import json

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
