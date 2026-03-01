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
    assert set(result.keys()) == {"status", "image_base64", "content_type"}
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
    import anki_vector.screen as screen_mod
    from PIL import Image as PILImage
    from vectorclaw_mcp.tools import vector_face

    img = PILImage.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")

    result = vector_face(encoded)

    screen_w, screen_h = screen_mod.dimensions.return_value
    screen_mod.convert_image_to_screen_data.assert_called_once()
    called_img = screen_mod.convert_image_to_screen_data.call_args[0][0]
    assert called_img.size == (screen_w, screen_h)
    assert called_img.mode == "RGB"
    rgb565_data = screen_mod.convert_image_to_screen_data.return_value
    assert len(rgb565_data) == screen_w * screen_h * 2
    mock_robot.screen.set_screen_with_image_data.assert_called_once_with(
        rgb565_data, duration_sec=5.0
    )
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
    assert result["origin_id"] == 1
    assert result["is_picked_up"] is False
    assert result["localized_to_object_id"] is None


def test_vector_pose_localized_to_object(mock_robot):
    from vectorclaw_mcp.tools import vector_pose

    mock_robot.localized_to_object_id = 42

    result = vector_pose()

    assert result["status"] == "ok"
    assert result["localized_to_object_id"] == 42


@pytest.mark.parametrize("action", ["dock", "pickup", "drop", "roll"])
def test_vector_cube_valid_actions(mock_robot, action):
    from vectorclaw_mcp.tools import vector_cube

    result = vector_cube(action)

    assert result["status"] == "ok"
    assert result["action"] == action


def test_vector_cube_pickup_uses_sdk_method(mock_robot):
    """Verify that the 'pickup' action uses the correct SDK method name: pickup_object."""
    from vectorclaw_mcp.tools import vector_cube

    result = vector_cube("pickup")

    mock_robot.behavior.pickup_object.assert_called_once_with(mock_robot.world.connected_light_cube)
    assert result["status"] == "ok"


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
    assert "is_on_charger" in result
    assert "is_picked_up" in result
    assert "is_carrying_object" not in result
    assert "is_on_charger_platform" not in result
    assert "is_cliff_detected" in result


# ---------------------------------------------------------------------------
# vector_scan
# ---------------------------------------------------------------------------

def test_vector_scan_success(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_scan

    result = vector_scan()

    mock_robot.behavior.look_around_in_place.assert_called_once()
    assert result == {"status": "ok"}


def test_vector_scan_error(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_scan

    mock_robot.behavior.look_around_in_place.side_effect = RuntimeError("sdk error")

    result = vector_scan()

    assert result["status"] == "error"
    assert "sdk error" in result["message"]
    assert set(result.keys()) == {"status", "message"}


# ---------------------------------------------------------------------------
# vector_find_faces
# ---------------------------------------------------------------------------

def test_vector_find_faces_success(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_find_faces

    result = vector_find_faces()

    mock_robot.behavior.find_faces.assert_called_once()
    assert result == {"status": "ok"}


def test_vector_find_faces_error(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_find_faces

    mock_robot.behavior.find_faces.side_effect = RuntimeError("face error")

    result = vector_find_faces()

    assert result["status"] == "error"
    assert "face error" in result["message"]
    assert set(result.keys()) == {"status", "message"}


# ---------------------------------------------------------------------------
# vector_list_visible_faces
# ---------------------------------------------------------------------------

def test_vector_list_visible_faces_success(mock_robot):
    from unittest.mock import MagicMock
    from vectorclaw_mcp.tools_perception import vector_list_visible_faces

    face1 = MagicMock()
    face1.face_id = 1
    face1.name = "Alice"
    face2 = MagicMock()
    face2.face_id = 2
    face2.name = ""
    mock_robot.world.visible_faces = [face1, face2]

    result = vector_list_visible_faces()

    assert result["status"] == "ok"
    assert set(result.keys()) == {"status", "faces"}
    assert len(result["faces"]) == 2
    assert result["faces"] == [{"face_id": 1, "name": "Alice"}, {"face_id": 2, "name": ""}]
    assert all(set(face.keys()) == {"face_id", "name"} for face in result["faces"])


def test_vector_list_visible_faces_empty(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_list_visible_faces

    mock_robot.world.visible_faces = []

    result = vector_list_visible_faces()

    assert result["status"] == "ok"
    assert set(result.keys()) == {"status", "faces"}
    assert result["faces"] == []


def test_vector_list_visible_faces_error(mock_robot):
    from unittest.mock import MagicMock
    from vectorclaw_mcp.tools_perception import vector_list_visible_faces

    class _RaisingWorld:
        @property
        def visible_faces(self):
            raise RuntimeError("vision error")

    mock_robot.world = _RaisingWorld()

    result = vector_list_visible_faces()
# ── vector_capture_image ─────────────────────────────────────────────────────

def test_vector_capture_image_success(mock_robot):
    from unittest.mock import MagicMock
    from PIL import Image as PILImage
    from vectorclaw_mcp.tools_perception import vector_capture_image

    pil_img = PILImage.new("RGB", (320, 240), color=(0, 128, 255))
    img_wrapper = MagicMock()
    img_wrapper.raw_image = pil_img
    mock_robot.camera.capture_single_image.return_value = img_wrapper

    result = vector_capture_image()

    mock_robot.camera.capture_single_image.assert_called_once()
    assert result["status"] == "ok"
    assert "image_base64" in result
    assert result["content_type"] == "image/jpeg"
    assert set(result.keys()) == {"status", "image_base64", "content_type"}
    decoded = base64.b64decode(result["image_base64"])
    assert len(decoded) > 0


def test_vector_capture_image_returns_none(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_capture_image

    mock_robot.camera.capture_single_image.return_value = None

    result = vector_capture_image()

    assert result["status"] == "error"
    assert "No image" in result["message"]
    assert set(result.keys()) == {"status", "message"}


def test_vector_capture_image_sdk_error(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_capture_image

    mock_robot.camera.capture_single_image.side_effect = RuntimeError("camera failure")

    result = vector_capture_image()

    assert result["status"] == "error"
    assert "camera failure" in result["message"]
    assert set(result.keys()) == {"status", "message"}


def test_vector_capture_image_encode_error(mock_robot):
    from unittest.mock import MagicMock
    from vectorclaw_mcp.tools_perception import vector_capture_image

    img_wrapper = MagicMock()
    img_wrapper.raw_image.save.side_effect = OSError("disk full")
    mock_robot.camera.capture_single_image.return_value = img_wrapper

    result = vector_capture_image()

    assert result["status"] == "error"
    assert "Failed to encode image" in result["message"]
    assert "disk full" in result["message"]
    assert set(result.keys()) == {"status", "message"}


# ── vector_face_detection ────────────────────────────────────────────────────

def test_vector_face_detection_no_faces(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_face_detection

    mock_robot.world.visible_faces = []

    result = vector_face_detection()

    assert result["status"] == "ok"
    assert result["face_count"] == 0
    assert set(result.keys()) == {"status", "face_count", "faces"}
    assert result["faces"] == []


def test_vector_face_detection_with_faces(mock_robot):
    from unittest.mock import MagicMock
    from vectorclaw_mcp.tools_perception import vector_face_detection

    face1 = MagicMock()
    face1.face_id = 1
    face1.expression = "happy"
    face2 = MagicMock()
    face2.face_id = 2
    face2.expression = "neutral"
    mock_robot.world.visible_faces = [face1, face2]

    result = vector_face_detection()

    assert result["status"] == "ok"
    assert result["face_count"] == 2
    assert len(result["faces"]) == 2
    assert result["faces"][0]["face_id"] == 1
    assert result["faces"][1]["face_id"] == 2
    assert set(result.keys()) == {"status", "face_count", "faces"}
    assert all(set(face.keys()) == {"face_id", "expression"} for face in result["faces"])
    assert result["faces"][0]["expression"] == "happy"
    assert result["faces"][1]["expression"] == "neutral"


def test_vector_face_detection_sdk_error(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_face_detection

    class _ErrorIterable:
        def __iter__(self):
            raise RuntimeError("vision error")

    mock_robot.world.visible_faces = _ErrorIterable()
    result = vector_face_detection()

    assert result["status"] == "error"
    assert "vision error" in result["message"]
    assert set(result.keys()) == {"status", "message"}


# ---------------------------------------------------------------------------
# vector_list_visible_objects
# ---------------------------------------------------------------------------

def test_vector_list_visible_objects_success(mock_robot):
    from unittest.mock import MagicMock
    from vectorclaw_mcp.tools_perception import vector_list_visible_objects

    obj1 = MagicMock()
    obj1.object_id = 42
    mock_robot.world.visible_objects = [obj1]

    result = vector_list_visible_objects()

    assert result["status"] == "ok"
    assert set(result.keys()) == {"status", "objects"}
    assert result["objects"] == [{"object_id": 42}]
    assert set(result["objects"][0].keys()) == {"object_id"}


def test_vector_list_visible_objects_empty(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_list_visible_objects

    mock_robot.world.visible_objects = []

    result = vector_list_visible_objects()

    assert result["status"] == "ok"
    assert set(result.keys()) == {"status", "objects"}
    assert result["objects"] == []


def test_vector_list_visible_objects_error(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_list_visible_objects

    class _RaisingWorld:
        @property
        def visible_objects(self):
            raise RuntimeError("object error")

    mock_robot.world = _RaisingWorld()

    result = vector_list_visible_objects()

    assert result["status"] == "error"
    assert "object error" in result["message"]
# ── vector_vision_reset ──────────────────────────────────────────────────────

def test_vector_vision_reset_success(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_vision_reset

    result = vector_vision_reset()

    mock_robot.vision.disable_all_vision_modes.assert_called_once()
    assert result == {"status": "ok"}
    assert result["status"] == "ok"


def test_vector_vision_reset_sdk_error(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_vision_reset

    mock_robot.vision.disable_all_vision_modes.side_effect = RuntimeError("vision reset failed")

    result = vector_vision_reset()

    assert result["status"] == "error"
    assert "vision reset failed" in result["message"]
    assert set(result.keys()) == {"status", "message"}


def test_vector_charger_status(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_charger_status

    result = vector_charger_status()

    assert result["status"] == "ok"
    assert "is_charging" in result
    assert "battery_level" in result
    assert "is_on_charger" in result


def test_vector_charger_status_error(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_charger_status

    mock_robot.get_battery_state.side_effect = RuntimeError("SDK failure")

    result = vector_charger_status()

    assert result["status"] == "error"
    assert "SDK failure" in result["message"]


def test_vector_touch_status(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_touch_status

    mock_robot.touch.last_sensor_reading.is_being_touched = True
    mock_robot.touch.last_sensor_reading.raw_touch_value = 42

    result = vector_touch_status()

    assert result["status"] == "ok"
    assert result["is_being_touched"] is True
    assert result["raw_touch_value"] == 42


def test_vector_touch_status_not_touched(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_touch_status

    result = vector_touch_status()

    assert result["status"] == "ok"
    assert result["is_being_touched"] is False


def test_vector_touch_status_error(mock_robot):
    from unittest.mock import PropertyMock, patch
    from vectorclaw_mcp.tools_perception import vector_touch_status

    with patch.object(
        type(mock_robot.touch),
        "last_sensor_reading",
        new_callable=PropertyMock,
        side_effect=RuntimeError("touch unavailable"),
        create=True,
    ):
        result = vector_touch_status()

    assert result["status"] == "error"
    assert "touch unavailable" in result["message"]


def test_vector_proximity_status(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_proximity_status

    mock_robot.proximity.last_sensor_reading.distance.distance_mm = 250.0
    mock_robot.proximity.last_sensor_reading.signal_quality = 0.85
    mock_robot.proximity.last_sensor_reading.unobstructed = False
    mock_robot.proximity.last_sensor_reading.found_object = True
    mock_robot.proximity.last_sensor_reading.is_lift_in_fov = False

    result = vector_proximity_status()

    assert result["status"] == "ok"
    assert result["distance_mm"] == 250.0
    assert result["signal_quality"] == 0.85
    assert result["unobstructed"] is False
    assert result["found_object"] is True
    assert result["is_lift_in_fov"] is False


def test_vector_proximity_status_no_object(mock_robot):
    from vectorclaw_mcp.tools_perception import vector_proximity_status

    result = vector_proximity_status()

    assert result["status"] == "ok"
    assert result["found_object"] is False
    assert result["signal_quality"] == 0.0
    assert result["unobstructed"] is True


def test_vector_proximity_status_error(mock_robot):
    from unittest.mock import PropertyMock, patch
    from vectorclaw_mcp.tools_perception import vector_proximity_status

    with patch.object(
        type(mock_robot.proximity),
        "last_sensor_reading",
        new_callable=PropertyMock,
        side_effect=RuntimeError("proximity unavailable"),
        create=True,
    ):
        result = vector_proximity_status()

    assert result["status"] == "error"
    assert "proximity unavailable" in result["message"]
