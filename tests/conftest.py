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
    # Always override any existing anki_vector modules to keep tests deterministic
    sys.modules["anki_vector"] = sdk
    sys.modules["anki_vector.util"] = util
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
    battery.battery_voltage = 3.8
    battery.suggested_charger_sec = 0.0
    robot.get_battery_state.return_value = battery
    robot.status.is_charging = False
    robot.status.is_carrying_block = False
    robot.status.is_carrying_object = False
    robot.status.is_on_charger_platform = False
    robot.status.is_cliff_detected = False
    robot.status.is_moving = False

    version_state = MagicMock()
    version_state.os_version = "1.7.0.3175"
    robot.get_version_state.return_value = version_state

    touch_reading = MagicMock()
    touch_reading.is_being_touched = False
    touch_reading.raw_touch_value = 0
    robot.touch.last_sensor_reading = touch_reading

    proximity_reading = MagicMock()
    proximity_reading.distance.distance_mm = 100.0
    proximity_reading.found_object = False
    proximity_reading.is_lift_in_fov = False
    proximity_reading.signal_quality = 1.0
    proximity_reading.unobstructed = True
    robot.proximity.last_sensor_reading = proximity_reading

    from PIL import Image as PILImage

    pil_img = PILImage.new("RGB", (320, 240), color=(128, 128, 128))
    img_wrapper = MagicMock()
    img_wrapper.raw_image = pil_img
    robot.camera.latest_image = img_wrapper
    robot.camera.capture_single_image.return_value = img_wrapper

    return robot


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
