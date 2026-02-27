"""Motion and actuator tools."""

from __future__ import annotations

import threading
from typing import Optional

from .tools_common import (
    _HEAD_ANGLE_MAX,
    _HEAD_ANGLE_MIN,
    _LIFT_HEIGHT_MAX,
    _LIFT_HEIGHT_MIN,
    _motion_precheck,
    _robot,
)

_DRIVE_ON_CHARGER_TIMEOUT_SEC = 30.0


def vector_drive(
    speed: int = 50,
    distance_mm: Optional[float] = None,
    angle_deg: Optional[float] = None,
) -> dict:
    if distance_mm is None and angle_deg is None:
        return {"status": "error", "message": "distance_mm or angle_deg is required"}

    import anki_vector.util as util  # noqa: PLC0415

    robot = _robot()
    precheck = _motion_precheck(robot)
    if precheck is not None:
        return precheck
    if distance_mm is not None:
        robot.behavior.drive_straight(util.distance_mm(distance_mm), util.speed_mmps(speed))
    if angle_deg is not None:
        robot.behavior.turn_in_place(util.degrees(angle_deg))

    return {"status": "ok", "distance_mm": distance_mm, "speed": speed, "angle_deg": angle_deg}


def vector_drive_off_charger() -> dict:
    robot = _robot()
    try:
        robot.behavior.drive_off_charger()
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return {"status": "error", "message": str(exc)}


def vector_head(angle_deg: float) -> dict:
    import anki_vector.util as util  # noqa: PLC0415

    clamped = max(_HEAD_ANGLE_MIN, min(_HEAD_ANGLE_MAX, angle_deg))
    robot = _robot()
    robot.behavior.set_head_angle(util.degrees(clamped))
    return {"status": "ok", "angle_deg": clamped}


def vector_lift(height: float) -> dict:
    clamped = max(_LIFT_HEIGHT_MIN, min(_LIFT_HEIGHT_MAX, height))
    robot = _robot()
    robot.behavior.set_lift_height(clamped)
    return {"status": "ok", "height": clamped}


def vector_drive_on_charger(timeout_sec: float = _DRIVE_ON_CHARGER_TIMEOUT_SEC) -> dict:
    """Best-effort helper to drive Vector onto the charger.

    If Vector is already on the charger the call is a no-op and returns
    ``{"status": "ok", "already_on_charger": true}``.

    The underlying ``behavior.drive_on_charger()`` call is executed with a
    wall-clock *timeout_sec* deadline.  If the call does not complete within
    that deadline – or if the robot appears to still be off the charger
    afterward – an actionable error payload is returned.

    Args:
        timeout_sec: Maximum seconds to wait for ``drive_on_charger`` to
            return.  Defaults to ``_DRIVE_ON_CHARGER_TIMEOUT_SEC`` (30 s).

    Returns:
        A dict with ``status`` ``"ok"`` on success or ``"error"`` with
        ``action_required`` guidance on failure.
    """
    robot = _robot()

    if robot.status.is_charging:
        return {"status": "ok", "already_on_charger": True}

    result: dict = {}
    exc_holder: list = []

    def _do_drive() -> None:
        try:
            robot.behavior.drive_on_charger()
        except Exception as exc:  # noqa: BLE001
            exc_holder.append(exc)

    thread = threading.Thread(target=_do_drive, daemon=True)
    thread.start()
    thread.join(timeout=timeout_sec)

    if thread.is_alive():
        return {
            "status": "error",
            "timed_out": True,
            "action_required": "check charger placement and retry vector_drive_on_charger",
            "message": f"drive_on_charger did not complete within {timeout_sec}s",
        }

    if exc_holder:
        return {
            "status": "error",
            "action_required": "check charger placement and retry vector_drive_on_charger",
            "message": str(exc_holder[0]),
        }

    if not robot.status.is_charging:
        return {
            "status": "error",
            "still_off_charger": True,
            "action_required": "manually place Vector on charger and retry",
            "message": "drive_on_charger completed but Vector is still off the charger",
        }

    return {"status": "ok"}


def vector_emergency_stop() -> dict:
    """Immediately stop all Vector motors.

    This is idempotent and safe to call repeatedly; it will always attempt
    ``motors.stop_all_motors()`` regardless of the current motion state.

    Returns:
        ``{"status": "ok"}`` on success, or ``{"status": "error", "message": …}``
        if the SDK call raises.
    """
    robot = _robot()
    try:
        robot.motors.stop_all_motors()
        return {"status": "ok"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}
