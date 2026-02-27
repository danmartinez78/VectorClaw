"""Motion and actuator tools."""

from __future__ import annotations

from typing import Optional

from .tools_common import (
    _HEAD_ANGLE_MAX,
    _HEAD_ANGLE_MIN,
    _LIFT_HEIGHT_MAX,
    _LIFT_HEIGHT_MIN,
    _motion_precheck,
    _robot,
)


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


def vector_drive_on_charger() -> dict:
    """Best-effort attempt to drive Vector back onto its charger."""
    robot = _robot()
    if robot.status.is_charging:
        return {"status": "ok", "already_on_charger": True}
    try:
        robot.behavior.drive_on_charger()
        return {"status": "ok", "already_on_charger": False}
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return {
            "status": "error",
            "message": f"drive_on_charger failed: {exc}",
            "action_required": "manually place Vector on charger",
        }


def vector_emergency_stop() -> dict:
    """Immediately stop all motors (idempotent, safe to call repeatedly)."""
    robot = _robot()
    try:
        robot.motors.stop_all_motors()
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return {"status": "error", "message": str(exc)}
