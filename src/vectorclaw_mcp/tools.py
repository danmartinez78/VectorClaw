"""Public tool API facade for VectorClaw MCP.

This file intentionally stays thin so parallel feature PRs can avoid merge
conflicts by editing domain modules instead:
- tools_speech.py
- tools_motion.py
- tools_perception.py
"""

from __future__ import annotations

from .tools_motion import vector_drive, vector_drive_off_charger, vector_head, vector_lift, vector_drive_on_charger, vector_emergency_stop
from .tools_perception import (
    vector_animate,
    vector_cube,
    vector_face,
    vector_look,
    vector_pose,
    vector_status,
    vector_charger_status,
    vector_touch_status,
    vector_proximity_status,
    vector_scan,
    vector_find_faces,
    vector_list_visible_faces,
    vector_list_visible_objects,
    vector_capture_image,
    vector_face_detection,
    vector_vision_reset,
)
from .tools_speech import vector_say

__all__ = [
    "vector_say",
    "vector_animate",
    "vector_drive",
    "vector_drive_off_charger",
    "vector_drive_on_charger",
    "vector_emergency_stop",
    "vector_look",
    "vector_face",
    "vector_pose",
    "vector_cube",
    "vector_status",
    "vector_head",
    "vector_lift",
    "vector_charger_status",
    "vector_touch_status",
    "vector_proximity_status",
    "vector_scan",
    "vector_find_faces",
    "vector_list_visible_faces",
    "vector_list_visible_objects",
    "vector_capture_image",
    "vector_face_detection",
    "vector_vision_reset",
]
