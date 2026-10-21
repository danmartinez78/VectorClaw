"""Guard against agents replaying the same actuating tool call in a loop.

Small/local models sometimes re-issue a call that already succeeded (they
re-read the user request instead of the tool result).  For a perception tool
that is harmless; for ``vector_drive`` it means the robot keeps driving —
possibly off a table.

The guard refuses an *identical* actuating call (same tool, same arguments)
that already succeeded as the most recent actuating call within a short
window, and returns a result telling the agent the action is done. Different
arguments, failed calls, and non-actuating tools are never blocked.

Configure the window with ``VECTOR_REPEAT_GUARD_SECONDS`` (default 10);
set it to ``0`` to disable the guard.
"""

from __future__ import annotations

import json
import os
import threading
import time
from typing import Any, Callable

DEFAULT_WINDOW_S = 10.0

# Tools that make the robot move, speak, or change what it displays.
ACTUATING_TOOLS = frozenset({
    "vector_say",
    "vector_animate",
    "vector_drive",
    "vector_drive_off_charger",
    "vector_drive_on_charger",
    "vector_face",
    "vector_cube",
    "vector_head",
    "vector_lift",
})


def _window_from_env() -> float:
    raw = os.environ.get("VECTOR_REPEAT_GUARD_SECONDS")
    if raw is None or raw.strip() == "":
        return DEFAULT_WINDOW_S
    try:
        return max(0.0, float(raw))
    except ValueError:
        return DEFAULT_WINDOW_S


class RepeatGuard:
    """Track recent successful actuating calls and refuse identical replays."""

    def __init__(
        self,
        window_s: float | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.window_s = _window_from_env() if window_s is None else window_s
        self._clock = clock
        self._lock = threading.Lock()
        self._last: tuple[tuple[str, str], float] | None = None
        self._pending: dict[tuple[str, str], int] = {}
        self._generation = 0

    @staticmethod
    def _key(name: str, arguments: dict[str, Any] | None) -> tuple[str, str]:
        return name, json.dumps(arguments or {}, sort_keys=True, default=str)

    def check(self, name: str, arguments: dict[str, Any] | None) -> dict[str, Any] | None:
        """Return a ``skipped`` result if this call is a recent replay, else ``None``."""
        if self.window_s <= 0 or name not in ACTUATING_TOOLS:
            return None
        key = self._key(name, arguments)
        now = self._clock()
        with self._lock:
            if key in self._pending:
                return self._skipped(name, "is already in progress")
            last = self._last
        if last is None or last[0] != key or now - last[1] >= self.window_s:
            return None
        return self._skipped(name, f"already succeeded {now - last[1]:.1f}s ago")

    @staticmethod
    def _skipped(name: str, reason: str) -> dict[str, Any]:
        return {
            "status": "skipped",
            "reason": "duplicate_call",
            "message": (
                f"Identical {name} call {reason}, so it was NOT repeated. "
                "Wait for its result or report the completed action to the user."
            ),
        }

    def begin(self, name: str, arguments: dict[str, Any] | None) -> dict[str, Any] | None:
        """Atomically reject replays or reserve an actuating call before dispatch."""
        if self.window_s <= 0 or name not in ACTUATING_TOOLS:
            return None
        key = self._key(name, arguments)
        now = self._clock()
        with self._lock:
            if key in self._pending:
                return self._skipped(name, "is already in progress")
            if (
                self._last is not None
                and self._last[0] == key
                and now - self._last[1] < self.window_s
            ):
                return self._skipped(name, f"already succeeded {now - self._last[1]:.1f}s ago")
            self._generation += 1
            self._last = None
            self._pending[key] = self._generation
        return None

    def finish(
        self,
        name: str,
        arguments: dict[str, Any] | None,
        result: dict[str, Any] | None,
    ) -> None:
        """Release a reservation and remember its result if it is still current."""
        if self.window_s <= 0 or name not in ACTUATING_TOOLS:
            return
        key = self._key(name, arguments)
        with self._lock:
            generation = self._pending.pop(key, None)
            if (
                generation is not None
                and generation == self._generation
                and isinstance(result, dict)
                and result.get("status") == "ok"
            ):
                self._last = (key, self._clock())

    def record(self, name: str, arguments: dict[str, Any] | None, result: dict[str, Any]) -> None:
        """Remember a successful actuating call."""
        if self.window_s <= 0 or name not in ACTUATING_TOOLS:
            return
        if not isinstance(result, dict) or result.get("status") != "ok":
            return
        with self._lock:
            self._generation += 1
            self._last = (self._key(name, arguments), self._clock())

    def reset(self) -> None:
        with self._lock:
            self._generation += 1
            self._last = None
            self._pending.clear()


repeat_guard = RepeatGuard()
