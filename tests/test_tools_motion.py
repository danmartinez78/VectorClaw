from __future__ import annotations


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


def test_vector_drive_on_charger_timeout(mock_robot):
    import threading

    from vectorclaw_mcp.tools_motion import vector_drive_on_charger

    ready = threading.Event()

    def _blocking():
        ready.wait()

    mock_robot.behavior.drive_on_charger.side_effect = _blocking

    result = vector_drive_on_charger(timeout_sec=0.05)
    ready.set()  # unblock the background thread so it can exit cleanly

    assert result["status"] == "error"
    assert result.get("timed_out") is True
    assert "timed" in result["message"]
    mock_robot.motors.stop_all_motors.assert_called_once()


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
