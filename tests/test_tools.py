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

    robot_manager.reset()
    yield
    robot_manager.reset()


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


def test_robot_manager_connect_retries_on_transient_failure(monkeypatch):
    """connect() retries up to VECTOR_CONNECT_RETRIES times then succeeds."""
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "2")
    monkeypatch.setenv("VECTOR_CONNECT_DELAY", "0")

    fake_robot = MagicMock()
    call_count = 0

    def fake_robot_factory(**kwargs):
        nonlocal call_count
        call_count += 1
        r = MagicMock()
        if call_count < 3:
            r.connect.side_effect = ConnectionError("transient")
        else:
            r.connect.return_value = None
        return r

    fake_sdk = MagicMock()
    fake_sdk.Robot.side_effect = fake_robot_factory
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    result = mgr.connect()
    assert mgr.is_connected
    assert call_count == 3


def test_robot_manager_connect_raises_after_all_retries(monkeypatch):
    """connect() raises the last exception after exhausting all retries."""
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "2")
    monkeypatch.setenv("VECTOR_CONNECT_DELAY", "0")

    fake_sdk = MagicMock()
    fake_sdk.Robot.return_value.connect.side_effect = ConnectionError("always fails")
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(ConnectionError, match="always fails"):
        mgr.connect()
    assert fake_sdk.Robot.call_count == 3  # 1 initial + 2 retries


def test_robot_manager_connect_no_retry_for_missing_serial(monkeypatch):
    """connect() raises RuntimeError immediately without retrying when serial is absent."""
    monkeypatch.delenv("VECTOR_SERIAL", raising=False)
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "3")

    fake_sdk = MagicMock()
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(RuntimeError, match="VECTOR_SERIAL"):
        mgr.connect()
    fake_sdk.Robot.assert_not_called()


def test_robot_manager_connect_runtime_error_not_retried(monkeypatch):
    """connect() propagates RuntimeError from the SDK immediately without retrying."""
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "3")
    monkeypatch.setenv("VECTOR_CONNECT_DELAY", "0")

    fake_sdk = MagicMock()
    fake_sdk.Robot.return_value.connect.side_effect = RuntimeError("sdk config error")
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(RuntimeError, match="sdk config error"):
        mgr.connect()
    fake_sdk.Robot.assert_called_once()  # no retry


def test_robot_manager_connect_invalid_retries(monkeypatch):
    """connect() raises RuntimeError when VECTOR_CONNECT_RETRIES is negative."""
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "-1")

    fake_sdk = MagicMock()
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(RuntimeError, match="VECTOR_CONNECT_RETRIES"):
        mgr.connect()
    fake_sdk.Robot.assert_not_called()


def test_robot_manager_connect_invalid_delay(monkeypatch):
    """connect() raises RuntimeError when VECTOR_CONNECT_DELAY is negative."""
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "2")
    monkeypatch.setenv("VECTOR_CONNECT_DELAY", "-0.5")

    fake_sdk = MagicMock()
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(RuntimeError, match="VECTOR_CONNECT_DELAY"):
        mgr.connect()
    fake_sdk.Robot.assert_not_called()


def test_robot_manager_connect_cleanup_on_failure(monkeypatch):
    """connect() attempts to disconnect the robot on each failed attempt."""
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "1")
    monkeypatch.setenv("VECTOR_CONNECT_DELAY", "0")

    robots_created = []

    def fake_robot_factory(**kwargs):
        r = MagicMock()
        r.connect.side_effect = OSError("network unreachable")
        robots_created.append(r)
        return r

    fake_sdk = MagicMock()
    fake_sdk.Robot.side_effect = fake_robot_factory
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(OSError):
        mgr.connect()
    # Each failed robot instance should have had disconnect() called
    for r in robots_created:
        r.disconnect.assert_called_once()


# ---------------------------------------------------------------------------
# Additional edge-case tests
# ---------------------------------------------------------------------------

def test_vector_look_no_latest_image(mock_robot):
    """vector_look() returns an error when the camera has no image yet."""
    from vectorclaw_mcp.tools import vector_look

    mock_robot.camera.latest_image = None

    result = vector_look()

    assert result["status"] == "error"
    assert "No camera image" in result["message"]


def test_vector_look_initialises_camera_feed_once(mock_robot):
    """The camera feed is initialized only on the first vector_look() call."""
    from vectorclaw_mcp.tools import vector_look

    vector_look()
    vector_look()

    mock_robot.camera.init_camera_feed.assert_called_once()


def test_vector_face_invalid_base64(mock_robot):
    """vector_face() returns an error for invalid base64 input."""
    from vectorclaw_mcp.tools import vector_face

    result = vector_face("not-valid-base64!!!")

    assert result["status"] == "error"
    assert "Invalid image data" in result["message"]


def test_vector_face_invalid_duration(mock_robot):
    """vector_face() returns an error when duration_sec is out of range."""
    import base64 as b64
    import io
    from PIL import Image as PILImage
    from vectorclaw_mcp.tools import vector_face

    img = PILImage.new("RGB", (10, 10))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = b64.b64encode(buf.getvalue()).decode("ascii")

    result = vector_face(encoded, duration_sec=-1.0)

    assert result["status"] == "error"
    assert "duration_sec" in result["message"]


def test_vector_cube_no_cube_connected(mock_robot):
    """vector_cube() returns an error when no cube is connected."""
    from vectorclaw_mcp.tools import vector_cube

    mock_robot.world.connected_light_cube = None

    result = vector_cube("dock")

    assert result["status"] == "error"
    assert "No cube is connected" in result["message"]


def test_call_tool_exception_becomes_error(mock_robot, monkeypatch):
    """Exceptions raised by a tool are caught and returned as error results."""
    import asyncio
    from vectorclaw_mcp import tools as tools_mod, server

    monkeypatch.setattr(tools_mod, "vector_status", lambda: 1 / 0)

    result = asyncio.run(server.call_tool("vector_status", {}))
    data = json.loads(result[0].text)

    assert data["status"] == "error"
    assert "division by zero" in data["message"]
