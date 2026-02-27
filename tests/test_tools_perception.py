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


def test_vector_scan(mock_robot):
    from vectorclaw_mcp.tools import vector_scan

    result = vector_scan()

    mock_robot.behavior.look_around_in_place.assert_called_once()
    assert result == {"status": "ok"}


def test_vector_find_faces(mock_robot):
    from vectorclaw_mcp.tools import vector_find_faces

    result = vector_find_faces()

    mock_robot.behavior.find_faces.assert_called_once()
    assert result == {"status": "ok"}


def test_vector_list_visible_faces(mock_robot):
    from unittest.mock import MagicMock
    from vectorclaw_mcp.tools import vector_list_visible_faces

    face1 = MagicMock()
    face1.face_id = 1
    face1.name = "Alice"
    face2 = MagicMock()
    face2.face_id = 2
    face2.name = ""
    mock_robot.world.visible_faces = [face1, face2]

    result = vector_list_visible_faces()

    assert result["status"] == "ok"
    assert len(result["faces"]) == 2
    assert result["faces"][0] == {"face_id": 1, "name": "Alice"}
    assert result["faces"][1] == {"face_id": 2, "name": None}


def test_vector_list_visible_faces_empty(mock_robot):
    from vectorclaw_mcp.tools import vector_list_visible_faces

    mock_robot.world.visible_faces = []

    result = vector_list_visible_faces()

    assert result["status"] == "ok"
    assert result["faces"] == []


def test_vector_list_visible_objects(mock_robot):
    from unittest.mock import MagicMock
    from vectorclaw_mcp.tools import vector_list_visible_objects

    obj1 = MagicMock()
    obj1.object_id = 10
    obj1.object_type = "LightCube"
    custom1 = MagicMock()
    custom1.object_id = 20
    custom1.object_type = "CustomBox"
    mock_robot.world.visible_objects = [obj1]
    mock_robot.world.visible_custom_objects = [custom1]

    result = vector_list_visible_objects()

    assert result["status"] == "ok"
    assert len(result["objects"]) == 2
    assert result["objects"][0] == {"object_id": 10, "object_type": "LightCube"}
    assert result["objects"][1] == {"object_id": 20, "object_type": "CustomBox"}


def test_vector_list_visible_objects_enum_type(mock_robot):
    from enum import Enum
    from unittest.mock import MagicMock
    from vectorclaw_mcp.tools import vector_list_visible_objects

    class ObjectType(Enum):
        LightCube = 1

    obj1 = MagicMock()
    obj1.object_id = 10
    obj1.object_type = ObjectType.LightCube
    mock_robot.world.visible_objects = [obj1]
    mock_robot.world.visible_custom_objects = []

    result = vector_list_visible_objects()

    assert result["status"] == "ok"
    assert result["objects"][0] == {"object_id": 10, "object_type": "LightCube"}


def test_vector_list_visible_objects_empty(mock_robot):
    from vectorclaw_mcp.tools import vector_list_visible_objects

    mock_robot.world.visible_objects = []
    mock_robot.world.visible_custom_objects = []

    result = vector_list_visible_objects()

    assert result["status"] == "ok"
    assert result["objects"] == []
