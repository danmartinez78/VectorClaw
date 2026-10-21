"""Guard against agents replaying the same actuating tool call in a loop.

Small/local models sometimes re-issue a call that already succeeded (they
re-read the user request instead of the tool result).  For a perception tool
that is harmless; for ``vector_drive`` it means the robot keeps driving —
possibly off a table.

The guard refuses an *identical* actuating call (same tool, same arguments)
that already succeeded within a short window, and returns a result telling
the agent the action is done.  Different arguments, failed calls, and
non-actuating tools are never blocked.

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
        self._last: dict[tuple[str, str], float] = {}

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
            last = self._last.get(key)
        if last is None or now - last >= self.window_s:
            return None
        return {
            "status": "skipped",
            "reason": "duplicate_call",
            "message": (
                f"Identical {name} call already succeeded {now - last:.1f}s ago, "
                "so it was NOT repeated. The action is complete; report the "
                "result to the user instead of calling the tool again."
            ),
        }

    def record(self, name: str, arguments: dict[str, Any] | None, result: dict[str, Any]) -> None:
        """Remember a successful actuating call."""
        if self.window_s <= 0 or name not in ACTUATING_TOOLS:
            return
        if not isinstance(result, dict) or result.get("status") != "ok":
            return
        with self._lock:
            now = self._clock()
            self._last = {
                key: timestamp
                for key, timestamp in self._last.items()
                if now - timestamp < self.window_s
            }
            self._last[self._key(name, arguments)] = now

    def reset(self) -> None:
        with self._lock:
            self._last.clear()


repeat_guard = RepeatGuard()
