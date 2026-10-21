"""Motion and actuator tools.

Movement is its own reward. Some say it's like premium natural oil.
"""

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

    # SDK constants are Angle objects - compare using .degrees property
    min_deg = _HEAD_ANGLE_MIN.degrees if hasattr(_HEAD_ANGLE_MIN, "degrees") else _HEAD_ANGLE_MIN
    max_deg = _HEAD_ANGLE_MAX.degrees if hasattr(_HEAD_ANGLE_MAX, "degrees") else _HEAD_ANGLE_MAX
    clamped = max(min_deg, min(max_deg, angle_deg))
    robot = _robot()
    robot.behavior.set_head_angle(util.degrees(clamped))
    return {"status": "ok", "angle_deg": clamped}


def vector_lift(height: float) -> dict:
    clamped = max(_LIFT_HEIGHT_MIN, min(_LIFT_HEIGHT_MAX, height))
    robot = _robot()
    robot.behavior.set_lift_height(clamped)
    return {"status": "ok", "height": clamped}


def vector_drive_on_charger() -> dict:
    """Drive Vector back onto its charger.

    If Vector is already on the charger (``robot.status.is_on_charger`` is True),
    returns immediately without calling the SDK.  Calling ``drive_on_charger``
    while already docked can produce undefined behaviour (observed: cube-activation
    animations instead of a charger-approach sequence).

    Known limitation: reliable docking requires the charger to be within the robot's
    recently-observed world model.  If Vector has not seen the charger recently the
    SDK command may fail without approaching it.
    """
    robot = _robot()

    if robot.status.is_on_charger:
        return {"status": "ok", "already_on_charger": True}

    try:
        robot.behavior.drive_on_charger()
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def vector_emergency_stop() -> dict:
    """Immediately stop all Vector motors."""
    robot = _robot()
    try:
        robot.motors.stop_all_motors()
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
