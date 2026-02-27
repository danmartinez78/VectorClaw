from __future__ import annotations

import base64
import io

import pytest


def test_vector_animate(mock_robot):
    from vectorclaw_mcp.tools import vector_animate

    result = vector_animate("anim_eyepose_happy_content_01")

    mock_robot.anim.play_animation.assert_called_once_with(
        "anim_eyepose_happy_content_01"
    )
    assert result["status"] == "ok"
    assert result["animation"] == "anim_eyepose_happy_content_01"


def test_vector_look(mock_robot):
    from vectorclaw_mcp.tools import vector_look

    result = vector_look()

    assert result["status"] == "ok"
    assert "image_base64" in result
    assert result["content_type"] == "image/jpeg"
    decoded = base64.b64decode(result["image_base64"])
    assert len(decoded) > 0


def test_vector_look_no_latest_image(mock_robot):
    from vectorclaw_mcp.tools import vector_look

    mock_robot.camera.latest_image = None

    result = vector_look()

    assert result["status"] == "error"
    assert "No camera image" in result["message"]


def test_vector_look_initialises_camera_feed_once(mock_robot):
    from vectorclaw_mcp.tools import vector_look

    vector_look()
    vector_look()

    mock_robot.camera.init_camera_feed.assert_called_once()


def test_vector_face(mock_robot):
    from PIL import Image as PILImage
    from vectorclaw_mcp.tools import vector_face

    img = PILImage.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")

    result = vector_face(encoded)

    mock_robot.screen.set_screen_with_image_data.assert_called_once()
    assert result["status"] == "ok"


def test_vector_face_invalid_base64(mock_robot):
    from vectorclaw_mcp.tools import vector_face

    result = vector_face("not-valid-base64!!!")

    assert result["status"] == "error"
    assert "Invalid image data" in result["message"]


def test_vector_face_invalid_duration(mock_robot):
    import base64 as b64
    from PIL import Image as PILImage
    from vectorclaw_mcp.tools import vector_face

    img = PILImage.new("RGB", (10, 10))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = b64.b64encode(buf.getvalue()).decode("ascii")

    result = vector_face(encoded, duration_sec=-1.0)

    assert result["status"] == "error"
    assert "duration_sec" in result["message"]


def test_vector_pose(mock_robot):
    from vectorclaw_mcp.tools import vector_pose

    result = vector_pose()

    assert result["status"] == "ok"
    assert result["x"] == 10.0
    assert result["y"] == 20.0
    assert result["z"] == 0.0
    assert result["angle_deg"] == 45.0


@pytest.mark.parametrize("action", ["dock", "pickup", "drop", "roll"])
def test_vector_cube_valid_actions(mock_robot, action):
    from vectorclaw_mcp.tools import vector_cube

    result = vector_cube(action)

    assert result["status"] == "ok"
    assert result["action"] == action


def test_vector_cube_invalid_action(mock_robot):
    from vectorclaw_mcp.tools import vector_cube

    result = vector_cube("fly")

    assert result["status"] == "error"


def test_vector_cube_no_cube_connected(mock_robot):
    from vectorclaw_mcp.tools import vector_cube

    mock_robot.world.connected_light_cube = None

    result = vector_cube("dock")

    assert result["status"] == "error"
    assert "No cube is connected" in result["message"]


def test_vector_status(mock_robot):
    from vectorclaw_mcp.tools import vector_status

    result = vector_status()

    assert result["status"] == "ok"
    assert "battery_level" in result
    assert "is_charging" in result
    assert "is_carrying_block" in result


def test_vector_status_expanded_fields(mock_robot):
    from vectorclaw_mcp.tools import vector_status

    result = vector_status()

    assert result["status"] == "ok"
    assert result["battery_level"] == 2
    assert result["battery_voltage"] == 3.8
    assert result["is_charging"] is False
    assert result["is_carrying_block"] is False
    assert result["is_on_charger_platform"] is False
    assert result["is_cliff_detected"] is False
    assert result["is_moving"] is False
    assert result["firmware_version"] == "1.7.0.3175"


def test_vector_status_firmware_version_unavailable(mock_robot):
    from vectorclaw_mcp.tools import vector_status

    mock_robot.get_version_state.side_effect = Exception("unavailable")

    result = vector_status()

    assert result["status"] == "ok"
    assert result["firmware_version"] is None


def test_vector_charger_status(mock_robot):
    from vectorclaw_mcp.tools import vector_charger_status

    result = vector_charger_status()

    assert result["status"] == "ok"
    assert result["is_charging"] is False
    assert result["is_on_charger_platform"] is False
    assert result["battery_level"] == 2
    assert result["battery_voltage"] == 3.8
    assert "suggested_charger_sec" in result


def test_vector_touch_status(mock_robot):
    from vectorclaw_mcp.tools import vector_touch_status

    mock_robot.touch.last_sensor_reading.is_being_touched = True
    mock_robot.touch.last_sensor_reading.raw_touch_value = 42

    result = vector_touch_status()

    assert result["status"] == "ok"
    assert result["is_being_touched"] is True
    assert result["raw_touch_value"] == 42


def test_vector_touch_status_unavailable(mock_robot):
    from vectorclaw_mcp.tools import vector_touch_status

    mock_robot.touch.last_sensor_reading = None

    result = vector_touch_status()

    assert result["status"] == "error"
    assert "unavailable" in result["message"].lower()


def test_vector_proximity_status(mock_robot):
    from vectorclaw_mcp.tools import vector_proximity_status

    result = vector_proximity_status()

    assert result["status"] == "ok"
    assert result["distance_mm"] == 100.0
    assert result["found_object"] is False
    assert result["is_lift_in_fov"] is False
    assert result["signal_quality"] == 1.0
    assert result["unobstructed"] is True


def test_vector_proximity_status_unavailable(mock_robot):
    from vectorclaw_mcp.tools import vector_proximity_status

    mock_robot.proximity.last_sensor_reading = None

    result = vector_proximity_status()

    assert result["status"] == "error"
    assert "unavailable" in result["message"].lower()
