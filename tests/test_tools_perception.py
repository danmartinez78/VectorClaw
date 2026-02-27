from __future__ import annotations

import base64
import io
from unittest.mock import MagicMock

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
    assert "is_cliff_detected" in result
    assert "is_moving" in result


def test_vector_charger_status(mock_robot):
    from vectorclaw_mcp.tools import vector_charger_status

    result = vector_charger_status()

    assert result["status"] == "ok"
    assert result["is_charging"] is False
    assert result["is_on_charger_platform"] is False


def test_vector_touch_status(mock_robot):
    from vectorclaw_mcp.tools import vector_touch_status

    result = vector_touch_status()

    assert result["status"] == "ok"
    assert "last_touch_time" in result
    assert "is_being_held" in result


def test_vector_proximity_status(mock_robot):
    from vectorclaw_mcp.tools import vector_proximity_status

    result = vector_proximity_status()

    assert result["status"] == "ok"
    assert result["distance_mm"] == 150.0
    assert result["found_object"] is True


def test_vector_proximity_status_no_reading(mock_robot):
    from vectorclaw_mcp.tools import vector_proximity_status

    mock_robot.proximity.last_sensor_reading = None

    result = vector_proximity_status()

    assert result["status"] == "ok"
    assert result["distance_mm"] is None
    assert result["found_object"] is False


def test_vector_scan(mock_robot):
    from vectorclaw_mcp.tools import vector_scan

    result = vector_scan(num_rotations=2)

    mock_robot.behavior.look_around_in_place.assert_called_once_with(num_rotations=2)
    assert result["status"] == "ok"
    assert result["num_rotations"] == 2


def test_vector_scan_default_rotations(mock_robot):
    from vectorclaw_mcp.tools import vector_scan

    result = vector_scan()

    mock_robot.behavior.look_around_in_place.assert_called_once_with(num_rotations=1)
    assert result["status"] == "ok"


def test_vector_find_faces(mock_robot):
    from vectorclaw_mcp.tools import vector_find_faces

    result = vector_find_faces()

    mock_robot.behavior.find_faces.assert_called_once()
    assert result["status"] == "ok"


def test_vector_list_visible_faces_empty(mock_robot):
    from vectorclaw_mcp.tools import vector_list_visible_faces

    result = vector_list_visible_faces()

    assert result["status"] == "ok"
    assert result["faces"] == []
    assert result["count"] == 0


def test_vector_list_visible_faces_with_faces(mock_robot):
    from vectorclaw_mcp.tools import vector_list_visible_faces

    face = MagicMock()
    face.face_id = 1
    face.name = "Alice"
    mock_robot.world.visible_faces = [face]

    result = vector_list_visible_faces()

    assert result["status"] == "ok"
    assert result["count"] == 1
    assert result["faces"][0]["face_id"] == 1
    assert result["faces"][0]["name"] == "Alice"


def test_vector_list_visible_objects_empty(mock_robot):
    from vectorclaw_mcp.tools import vector_list_visible_objects

    result = vector_list_visible_objects()

    assert result["status"] == "ok"
    assert result["objects"] == []
    assert result["count"] == 0


def test_vector_capture_image(mock_robot):
    from PIL import Image as PILImage
    from vectorclaw_mcp.tools import vector_capture_image

    pil_img = PILImage.new("RGB", (320, 240), color=(0, 0, 0))
    img_wrapper = MagicMock()
    img_wrapper.raw_image = pil_img
    mock_robot.camera.capture_single_image.return_value = img_wrapper

    result = vector_capture_image()

    mock_robot.camera.capture_single_image.assert_called_once()
    assert result["status"] == "ok"
    assert "image_base64" in result
    assert result["content_type"] == "image/jpeg"


def test_vector_capture_image_returns_none(mock_robot):
    from vectorclaw_mcp.tools import vector_capture_image

    mock_robot.camera.capture_single_image.return_value = None

    result = vector_capture_image()

    assert result["status"] == "error"
    assert "No image captured" in result["message"]


def test_vector_face_detection_empty(mock_robot):
    from vectorclaw_mcp.tools import vector_face_detection

    result = vector_face_detection()

    assert result["status"] == "ok"
    assert result["detected_faces"] == []
    assert result["count"] == 0


def test_vector_face_detection_with_faces(mock_robot):
    from vectorclaw_mcp.tools import vector_face_detection

    face = MagicMock()
    face.face_id = 5
    face.name = "Bob"
    face.expression = "happiness"
    mock_robot.world.visible_faces = [face]

    result = vector_face_detection()

    assert result["status"] == "ok"
    assert result["count"] == 1
    assert result["detected_faces"][0]["face_id"] == 5
    assert result["detected_faces"][0]["name"] == "Bob"


def test_vector_vision_reset(mock_robot):
    from vectorclaw_mcp.tools import vector_vision_reset

    result = vector_vision_reset()

    mock_robot.vision.disable_all_vision_modes.assert_called_once()
    assert result["status"] == "ok"
