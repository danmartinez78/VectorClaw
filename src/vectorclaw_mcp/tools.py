"""Public tool API facade for VectorClaw MCP.

This file intentionally stays thin so parallel feature PRs can avoid merge
conflicts by editing domain modules instead:
- tools_speech.py
- tools_motion.py
- tools_perception.py
"""

from __future__ import annotations

from .tools_motion import vector_drive, vector_drive_off_charger, vector_head, vector_lift
from .tools_perception import (
    vector_animate,
    vector_cube,
    vector_face,
    vector_look,
    vector_pose,
    vector_status,
)
from .tools_setup import vector_setup
from .tools_speech import vector_say

__all__ = [
    "vector_say",
    "vector_animate",
    "vector_drive",
    "vector_drive_off_charger",
    "vector_look",
    "vector_face",
    "vector_pose",
    "vector_cube",
    "vector_status",
    "vector_head",
    "vector_lift",
    "vector_setup",
]
