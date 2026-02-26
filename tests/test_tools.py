"""Basic tests for VectorClaw MCP tools.

These tests mock the anki_vector SDK so they can run without a real robot.
"""

from __future__ import annotations

import base64
import io
import json
import sys
import types
from unittest.mock import MagicMock, patch, PropertyMock

import pytest


# ---------------------------------------------------------------------------
# Helpers to build a minimal fake anki_vector SDK
# ---------------------------------------------------------------------------

def _make_fake_sdk() -> types.ModuleType:
    """Return a lightweight mock of the anki_vector package."""
    sdk = types.ModuleType("anki_vector")

    # anki_vector.util sub-module with distance_mm / degrees helpers
    util = types.ModuleType("anki_vector.util")
    util.distance_mm = lambda v: v
    util.degrees = lambda v: v
    sdk.util = util
    sys.modules.setdefault("anki_vector", sdk)
    sys.modules.setdefault("anki_vector.util", util)
    return sdk


_fake_sdk = _make_fake_sdk()


def _make_robot() -> MagicMock:
    """Return a mock robot with the attributes our tools use."""
    robot = MagicMock()

    # Pose
    robot.pose.position.x = 10.0
    robot.pose.position.y = 20.0
    robot.pose.position.z = 0.0
    robot.pose.rotation.angle_z.degrees = 45.0

    # Battery
    battery = MagicMock()
    battery.battery_level = 2
    robot.get_battery_state.return_value = battery
    robot.status.is_charging = False
    robot.status.is_carrying_object = False

    # Camera — latest_image wraps a PIL-like object
    from PIL import Image as PILImage

    pil_img = PILImage.new("RGB", (320, 240), color=(128, 128, 128))
    img_wrapper = MagicMock()
    img_wrapper.raw_image = pil_img
    robot.camera.latest_image = img_wrapper

    return robot


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_robot_manager():
    """Ensure the robot_manager singleton is reset between tests."""
    from vectorclaw_mcp.robot import robot_manager

    robot_manager._robot = None
    yield
    robot_manager._robot = None


@pytest.fixture()
def mock_robot(monkeypatch):
    """Patch robot_manager.connect() to return a fake robot."""
    robot = _make_robot()
    from vectorclaw_mcp import robot as robot_mod

    monkeypatch.setattr(robot_mod.robot_manager, "connect", lambda: robot)
    return robot


# ---------------------------------------------------------------------------
# vector_say
# ---------------------------------------------------------------------------

def test_vector_say(mock_robot):
    from vectorclaw_mcp.tools import vector_say

    result = vector_say("Hello, world!")

    mock_robot.behavior.say_text.assert_called_once_with("Hello, world!")
    assert result["status"] == "ok"
    assert result["said"] == "Hello, world!"


# ---------------------------------------------------------------------------
# vector_animate
# ---------------------------------------------------------------------------

def test_vector_animate(mock_robot):
    from vectorclaw_mcp.tools import vector_animate

    result = vector_animate("anim_eyepose_happy_content_01")

    mock_robot.anim.play_animation.assert_called_once_with(
        "anim_eyepose_happy_content_01"
    )
    assert result["status"] == "ok"
    assert result["animation"] == "anim_eyepose_happy_content_01"


# ---------------------------------------------------------------------------
# vector_drive
# ---------------------------------------------------------------------------

def test_vector_drive_straight(mock_robot):
    from vectorclaw_mcp.tools import vector_drive

    result = vector_drive(distance_mm=200)

    mock_robot.behavior.drive_straight.assert_called_once_with(200)
    mock_robot.behavior.turn_in_place.assert_not_called()
    assert result["status"] == "ok"
    assert result["distance_mm"] == 200


def test_vector_drive_turn(mock_robot):
    from vectorclaw_mcp.tools import vector_drive

    result = vector_drive(angle_deg=90)

    mock_robot.behavior.drive_straight.assert_not_called()
    mock_robot.behavior.turn_in_place.assert_called_once_with(90)
    assert result["status"] == "ok"


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


# ---------------------------------------------------------------------------
# vector_look
# ---------------------------------------------------------------------------

def test_vector_look(mock_robot):
    from vectorclaw_mcp.tools import vector_look

    result = vector_look()

    assert result["status"] == "ok"
    assert "image_base64" in result
    assert result["content_type"] == "image/jpeg"
    # Verify the base64 string is valid
    decoded = base64.b64decode(result["image_base64"])
    assert len(decoded) > 0


# ---------------------------------------------------------------------------
# vector_face
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# vector_pose
# ---------------------------------------------------------------------------

def test_vector_pose(mock_robot):
    from vectorclaw_mcp.tools import vector_pose

    result = vector_pose()

    assert result["status"] == "ok"
    assert result["x"] == 10.0
    assert result["y"] == 20.0
    assert result["z"] == 0.0
    assert result["angle_deg"] == 45.0


# ---------------------------------------------------------------------------
# vector_cube
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# vector_status
# ---------------------------------------------------------------------------

def test_vector_status(mock_robot):
    from vectorclaw_mcp.tools import vector_status

    result = vector_status()

    assert result["status"] == "ok"
    assert "battery_level" in result
    assert "is_charging" in result
    assert "is_carrying_object" in result


# ---------------------------------------------------------------------------
# RobotManager
# ---------------------------------------------------------------------------

def test_robot_manager_requires_serial(monkeypatch):
    """connect() raises RuntimeError when VECTOR_SERIAL is not set."""
    monkeypatch.delenv("VECTOR_SERIAL", raising=False)
    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(RuntimeError, match="VECTOR_SERIAL"):
        mgr.connect()


def test_robot_manager_disconnect_noop():
    """disconnect() is a no-op when not connected."""
    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    mgr.disconnect()  # should not raise
    assert not mgr.is_connected
