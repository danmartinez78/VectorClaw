"""Shared helpers for VectorClaw tool implementations."""

from __future__ import annotations

import os
from typing import Optional

from .robot import robot_manager


def _robot():
    """Return the active robot instance, connecting if necessary."""
    return robot_manager.connect()


def _motion_precheck(robot) -> Optional[dict]:
    """Check preconditions before a motion command.

    If Vector is on the charger and ``VECTOR_AUTO_DRIVE_OFF_CHARGER`` is set to
    a truthy value (``1``, ``true``, or ``yes``), this helper will attempt to
    drive it off automatically. Otherwise an actionable error dict is returned.
    """
    if not robot.status.is_charging:
        return None

    if os.environ.get("VECTOR_AUTO_DRIVE_OFF_CHARGER", "").lower() in ("1", "true", "yes"):
        try:
            robot.behavior.drive_off_charger()
        except Exception:  # pragma: no cover - defensive
            return {
                "status": "error",
                "on_charger": True,
                "action_required": "call vector_drive_off_charger first",
                "message": f"Auto drive-off-charger failed: {exc}",
            }
        if robot.status.is_charging:
            return {
                "status": "error",
                "on_charger": True,
                "action_required": "call vector_drive_off_charger first",
                "message": "Auto drive-off-charger completed but Vector is still on the charger",
            }
        return None

    return {
        "status": "error",
        "on_charger": True,
        "action_required": "call vector_drive_off_charger first",
        "message": "Vector is on the charger; drive it off before sending motion commands",
    }


_HEAD_ANGLE_MIN = -22.0
_HEAD_ANGLE_MAX = 45.0
_LIFT_HEIGHT_MIN = 0.0
_LIFT_HEIGHT_MAX = 1.0
