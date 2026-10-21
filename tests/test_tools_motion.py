from __future__ import annotations

import sys
from unittest.mock import sentinel


def test_vector_say(mock_robot):
    from vectorclaw_mcp.tools import vector_say

    result = vector_say("Hello, world!")

    mock_robot.behavior.say_text.assert_called_once_with("Hello, world!")
    assert result["status"] == "ok"
    assert result["said"] == "Hello, world!"


def test_vector_drive_straight(mock_robot):
    from vectorclaw_mcp.tools import vector_drive

    result = vector_drive(distance_mm=200)

    mock_robot.behavior.drive_straight.assert_called_once_with(200, 50)
    mock_robot.behavior.turn_in_place.assert_not_called()
    assert result["status"] == "ok"
    assert result["distance_mm"] == 200


def test_vector_drive_turn(mock_robot):
    from vectorclaw_mcp.tools import vector_drive

    result = vector_drive(angle_deg=90)

    mock_robot.behavior.drive_straight.assert_not_called()
    mock_robot.behavior.turn_in_place.assert_called_once_with(90)
    assert result["status"] == "ok"
    assert result["angle_deg"] == 90


def test_vector_drive_both(mock_robot):
    from vectorclaw_mcp.tools import vector_drive

    result = vector_drive(distance_mm=100, angle_deg=45)

    mock_robot.behavior.drive_straight.assert_called_once()
    mock_robot.behavior.turn_in_place.assert_called_once()
    assert result["status"] == "ok"


def test_vector_drive_no_args(mock_robot):
    from vectorclaw_mcp.tools import vector_drive

    result = vector_drive()

    assert result["status"] == "error"


def test_vector_drive_with_custom_speed(mock_robot):
    from vectorclaw_mcp.tools import vector_drive

    result = vector_drive(distance_mm=200, speed=100)

    mock_robot.behavior.drive_straight.assert_called_once_with(200, 100)
    assert result["status"] == "ok"
    assert result["speed"] == 100


def test_vector_drive_off_charger_success(mock_robot):
    from vectorclaw_mcp.tools import vector_drive_off_charger

    result = vector_drive_off_charger()

    mock_robot.behavior.drive_off_charger.assert_called_once()
    assert result == {"status": "ok"}


def test_vector_drive_off_charger_error(mock_robot):
    from vectorclaw_mcp.tools import vector_drive_off_charger

    mock_robot.behavior.drive_off_charger.side_effect = RuntimeError("charger comms error")

    result = vector_drive_off_charger()

    assert result["status"] == "error"
    assert "charger comms error" in result["message"]


def test_vector_head_normal(mock_robot):
    from vectorclaw_mcp.tools import vector_head

    result = vector_head(20.0)

    mock_robot.behavior.set_head_angle.assert_called_once_with(20.0)
    assert result["status"] == "ok"
    assert result["angle_deg"] == 20.0


def test_vector_head_clamp_high(mock_robot):
    from vectorclaw_mcp.tools import vector_head

    result = vector_head(90.0)

    assert result["status"] == "ok"
    assert result["angle_deg"] == 45.0
    mock_robot.behavior.set_head_angle.assert_called_once_with(45.0)


def test_vector_head_clamp_low(mock_robot):
    from vectorclaw_mcp.tools import vector_head

    result = vector_head(-90.0)

    assert result["status"] == "ok"
    assert result["angle_deg"] == -22.0
    mock_robot.behavior.set_head_angle.assert_called_once_with(-22.0)


def test_vector_head_at_min_bound(mock_robot):
    from anki_vector.behavior import MIN_HEAD_ANGLE

    from vectorclaw_mcp.tools import vector_head

    result = vector_head(MIN_HEAD_ANGLE)

    assert result["status"] == "ok"
    assert result["angle_deg"] == MIN_HEAD_ANGLE
    mock_robot.behavior.set_head_angle.assert_called_once_with(MIN_HEAD_ANGLE)


def test_vector_head_at_max_bound(mock_robot):
    from anki_vector.behavior import MAX_HEAD_ANGLE

    from vectorclaw_mcp.tools import vector_head

    result = vector_head(MAX_HEAD_ANGLE)

    assert result["status"] == "ok"
    assert result["angle_deg"] == MAX_HEAD_ANGLE
    mock_robot.behavior.set_head_angle.assert_called_once_with(MAX_HEAD_ANGLE)


def test_vector_head_passes_angle_type(mock_robot, monkeypatch):
    """set_head_angle must receive a util.Angle object, not a raw float."""
    util_mod = sys.modules["anki_vector.util"]
    monkeypatch.setattr(util_mod, "degrees", lambda v: sentinel.angle_obj)

    from vectorclaw_mcp.tools import vector_head

    vector_head(20.0)

    mock_robot.behavior.set_head_angle.assert_called_once_with(sentinel.angle_obj)


def test_vector_lift_normal(mock_robot):
    from vectorclaw_mcp.tools import vector_lift

    result = vector_lift(0.5)

    mock_robot.behavior.set_lift_height.assert_called_once_with(0.5)
    assert result["status"] == "ok"
    assert result["height"] == 0.5


def test_vector_lift_clamp_high(mock_robot):
    from vectorclaw_mcp.tools import vector_lift

    result = vector_lift(2.0)

    assert result["status"] == "ok"
    assert result["height"] == 1.0
    mock_robot.behavior.set_lift_height.assert_called_once_with(1.0)


def test_vector_lift_clamp_low(mock_robot):
    from vectorclaw_mcp.tools import vector_lift

    result = vector_lift(-0.5)

    assert result["status"] == "ok"
    assert result["height"] == 0.0
    mock_robot.behavior.set_lift_height.assert_called_once_with(0.0)


def test_vector_drive_on_charger_already_on_charger(mock_robot):
    from vectorclaw_mcp.tools_motion import vector_drive_on_charger

    mock_robot.status.is_on_charger = True

    result = vector_drive_on_charger()

    mock_robot.behavior.drive_on_charger.assert_not_called()
    assert result == {"status": "ok", "already_on_charger": True}


def test_vector_drive_on_charger_success(mock_robot):
    from vectorclaw_mcp.tools_motion import vector_drive_on_charger

    result = vector_drive_on_charger()

    mock_robot.behavior.drive_on_charger.assert_called_once()
    assert result == {"status": "ok"}


def test_vector_drive_on_charger_error(mock_robot):
    from vectorclaw_mcp.tools_motion import vector_drive_on_charger

    mock_robot.behavior.drive_on_charger.side_effect = RuntimeError("charger nav error")

    result = vector_drive_on_charger()

    assert result["status"] == "error"
    assert "charger nav error" in result["message"]


def test_vector_drive_on_charger_no_timeout_parameter(mock_robot):
    from vectorclaw_mcp.tools_motion import vector_drive_on_charger

    # Phase 0: no timeout parameter - function signature is simply vector_drive_on_charger()
    import inspect

    sig = inspect.signature(vector_drive_on_charger)
    assert "timeout_sec" not in sig.parameters


def test_vector_drive_on_charger_synchronous_call(mock_robot):
    from vectorclaw_mcp.tools_motion import vector_drive_on_charger

    # Phase 0: no timeout parameter - calling with no args must succeed (not error)
    mock_robot.status.is_on_charger = False
    result = vector_drive_on_charger()
    assert result["status"] == "ok"
    mock_robot.behavior.drive_on_charger.assert_called_once()


def test_vector_emergency_stop_success(mock_robot):
    from vectorclaw_mcp.tools_motion import vector_emergency_stop

    result = vector_emergency_stop()

    mock_robot.motors.stop_all_motors.assert_called_once()
    assert result == {"status": "ok"}


def test_vector_emergency_stop_error(mock_robot):
    from vectorclaw_mcp.tools_motion import vector_emergency_stop

    mock_robot.motors.stop_all_motors.side_effect = RuntimeError("motor fault")

    result = vector_emergency_stop()

    assert result["status"] == "error"
    assert "motor fault" in result["message"]
