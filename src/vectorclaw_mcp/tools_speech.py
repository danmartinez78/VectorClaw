"""Speech-focused tools."""

from __future__ import annotations

from .tools_common import _robot


def vector_say(text: str) -> dict:
    robot = _robot()
    robot.behavior.say_text(text)
    return {"status": "ok", "said": text}
