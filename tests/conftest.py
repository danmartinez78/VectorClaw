from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest


def _make_fake_sdk() -> types.ModuleType:
    """Return a lightweight mock of the anki_vector package."""
    sdk = types.ModuleType("anki_vector")

    util = types.ModuleType("anki_vector.util")
    util.distance_mm = lambda v: v
    util.degrees = lambda v: v
    util.speed_mmps = lambda v: v
    sdk.util = util

    screen = types.ModuleType("anki_vector.screen")
    screen.dimensions = MagicMock(return_value=(184, 96))
    screen.convert_image_to_screen_data = MagicMock(return_value=b"\x00" * (184 * 96 * 2))
    sdk.screen = screen

    # Always override any existing anki_vector modules to keep tests deterministic
    sys.modules["anki_vector"] = sdk
    sys.modules["anki_vector.util"] = util
    sys.modules["anki_vector.screen"] = screen
    return sdk


_fake_sdk = _make_fake_sdk()


def _make_robot() -> MagicMock:
    """Return a mock robot with the attributes our tools use."""
    robot = MagicMock()

    robot.pose.position.x = 10.0
    robot.pose.position.y = 20.0
    robot.pose.position.z = 0.0
    robot.pose.rotation.angle_z.degrees = 45.0

    battery = MagicMock()
    battery.battery_level = 2
    robot.get_battery_state.return_value = battery
    robot.status.is_charging = False
    robot.status.is_carrying_block = False
    robot.status.is_on_charger = False
    robot.status.is_picked_up = False
    robot.status.is_cliff_detected = False

    robot.touch.last_sensor_reading.is_being_touched = False
    robot.touch.last_sensor_reading.raw_touch_value = 0

    robot.proximity.last_sensor_reading.distance.distance_mm = 100.0
    robot.proximity.last_sensor_reading.found_object = False
    robot.proximity.last_sensor_reading.is_lift_in_fov = False

    from PIL import Image as PILImage

    pil_img = PILImage.new("RGB", (320, 240), color=(128, 128, 128))
    img_wrapper = MagicMock()
    img_wrapper.raw_image = pil_img
    robot.camera.latest_image = img_wrapper

    return robot


@pytest.fixture(autouse=True)
def reset_robot_manager():
    """Ensure the robot_manager singleton is reset between tests."""
    from vectorclaw_mcp.robot import robot_manager

    robot_manager.reset()
    _fake_sdk.screen.dimensions.reset_mock()
    _fake_sdk.screen.convert_image_to_screen_data.reset_mock()
    yield
    robot_manager.reset()


@pytest.fixture()
def mock_robot(monkeypatch):
    """Patch robot_manager.connect() to return a fake robot."""
    robot = _make_robot()
    from vectorclaw_mcp import robot as robot_mod

    monkeypatch.setattr(robot_mod.robot_manager, "connect", lambda: robot)
    return robot
