"""Speech-focused tools.

Tachikomas love to talk. This one is no exception.
"""

from __future__ import annotations

from .tools_common import _robot


def vector_say(text: str) -> dict:
    """Make the robot speak. Use responsibly — it might develop a personality."""
    robot = _robot()
    robot.behavior.say_text(text)
    return {"status": "ok", "said": text}
