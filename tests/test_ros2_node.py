"""Tests for the VectorClaw ROS2 bridge node (vectorclaw_ros2).

These tests mock out both ``rclpy`` and ``vectorclaw_mcp`` so they can run in a
plain pytest environment without a ROS2 installation or a real robot.

Run with:
    pytest tests/test_ros2_node.py -v
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# IMPORTANT: inject stubs at MODULE LOAD TIME — before any pytest fixture
# (including the autouse reset_robot_manager in conftest.py) can run.
# ---------------------------------------------------------------------------
import os
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

# Add the vectorclaw_ros2 package root so importlib can find it without a colcon install
_REPO_ROOT = Path(__file__).resolve().parent.parent
_ROS2_PKG_ROOT = _REPO_ROOT / "vectorclaw_ros2"
if str(_ROS2_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROS2_PKG_ROOT))

# ---- Build and inject vectorclaw_mcp stubs ---------------------------------
# The parent conftest.py has an autouse fixture that does:
#   from vectorclaw_mcp.robot import robot_manager
# If vectorclaw_mcp isn't installed this raises ModuleNotFoundError before our
# own inject_stubs fixture can fire, so we seed sys.modules right here.

_vclaw_mcp = types.ModuleType("vectorclaw_mcp")

_vclaw_robot_mod = types.ModuleType("vectorclaw_mcp.robot")
_fake_robot_manager = MagicMock()
_fake_robot_manager.reset = MagicMock()
_vclaw_robot_mod.robot_manager = _fake_robot_manager

_vclaw_tools = types.ModuleType("vectorclaw_mcp.tools")
_vclaw_motion = types.ModuleType("vectorclaw_mcp.tools_motion")
_vclaw_perception = types.ModuleType("vectorclaw_mcp.tools_perception")

_ALL_FNS = [
    "vector_say", "vector_animate", "vector_pose",
    "vector_drive", "vector_drive_off_charger", "vector_emergency_stop",
    "vector_head", "vector_lift",
    "vector_status", "vector_proximity_status",
    "vector_touch_status", "vector_capture_image",
]
for _mod in (_vclaw_tools, _vclaw_motion, _vclaw_perception):
    for _fn in _ALL_FNS:
        setattr(_mod, _fn, MagicMock(return_value={"status": "ok"}))

sys.modules.setdefault("vectorclaw_mcp", _vclaw_mcp)
sys.modules.setdefault("vectorclaw_mcp.robot", _vclaw_robot_mod)
sys.modules.setdefault("vectorclaw_mcp.tools", _vclaw_tools)
sys.modules.setdefault("vectorclaw_mcp.tools_motion", _vclaw_motion)
sys.modules.setdefault("vectorclaw_mcp.tools_perception", _vclaw_perception)

# ---- Build and inject rclpy stubs ------------------------------------------

def _make_rclpy_stub() -> types.ModuleType:
    rclpy = types.ModuleType("rclpy")
    rclpy.init = MagicMock()
    rclpy.spin = MagicMock()
    rclpy.shutdown = MagicMock()

    node_mod = types.ModuleType("rclpy.node")

    class FakeNode:
        """Minimal rclpy.node.Node stand-in."""

        def __init__(self, name):
            self._name = name
            self._logger = MagicMock()
            self._clock = MagicMock()
            self._clock.now.return_value.to_msg.return_value = MagicMock()
            self._publishers: list = []
            self._subscriptions: list = []
            self._services: list = []
            self._timers: list = []

        def declare_parameter(self, name, default):
            class _P:
                value = default
            return _P()

        def get_parameter(self, name):
            # Return something with a sensible .value based on the node defaults
            defaults = {
                "status_hz": 1.0,
                "sensor_hz": 5.0,
                "camera_enabled": True,
                "frame_id": "vector",
            }
            class _P:
                value = defaults.get(name)
            return _P()

        def create_publisher(self, msg_type, topic, qos):
            pub = MagicMock()
            pub.topic = topic
            pub.msg_type = msg_type
            self._publishers.append(pub)
            return pub

        def create_subscription(self, msg_type, topic, cb, qos):
            sub = MagicMock()
            sub.topic = topic
            sub.callback = cb
            self._subscriptions.append(sub)
            return sub

        def create_service(self, srv_type, name, cb):
            srv = MagicMock()
            srv.name = name
            srv.callback = cb
            self._services.append(srv)
            return srv

        def create_timer(self, period, cb):
            timer = MagicMock()
            timer.period = period
            timer.callback = cb
            self._timers.append(timer)
            return timer

        def get_logger(self):
            return self._logger

        def get_clock(self):
            return self._clock

        def destroy_node(self):
            pass

    node_mod.Node = FakeNode
    rclpy.node = node_mod
    return rclpy


def _make_msg_stubs() -> dict[str, types.ModuleType]:
    stubs: dict[str, types.ModuleType] = {}

    def _simple(mod_name: str, *names: str) -> types.ModuleType:
        mod = types.ModuleType(mod_name)
        for n in names:
            cls = type(n, (), {"__init__": lambda self: None})
            setattr(mod, n, cls)
        stubs[mod_name] = mod
        return mod

    _simple("std_msgs.msg", "String", "Bool", "Float32")
    _simple("std_srvs.srv", "Trigger")

    geo = _simple("geometry_msgs.msg", "PoseStamped", "Quaternion", "Twist")

    class _Vec3:
        x = 0.0; y = 0.0; z = 0.0

    class _Twist:
        linear = _Vec3()
        angular = _Vec3()

    geo.Twist = _Twist

    sensor = _simple("sensor_msgs.msg", "Image", "Range")
    sensor.Range.INFRARED = 1

    return stubs


_rclpy_stub = _make_rclpy_stub()
_msg_stubs = _make_msg_stubs()

sys.modules.setdefault("rclpy", _rclpy_stub)
sys.modules.setdefault("rclpy.node", _rclpy_stub.node)
for _mod_name, _mod in _msg_stubs.items():
    sys.modules.setdefault(_mod_name, _mod)

# ---------------------------------------------------------------------------
# Now it's safe to import pytest and write tests
# ---------------------------------------------------------------------------
import importlib

import pytest


def _fresh_node_class():
    """Re-import VectorClawNode cleanly (clears cached module)."""
    sys.modules.pop("vectorclaw_ros2.vector_node", None)
    sys.modules.pop("vectorclaw_ros2", None)
    vn = importlib.import_module("vectorclaw_ros2.vector_node")
    # Reset all mock call counts so each test starts clean
    for fn in _ALL_FNS:
        for mod in (_vclaw_tools, _vclaw_motion, _vclaw_perception):
            attr = getattr(mod, fn, None)
            if isinstance(attr, MagicMock):
                attr.reset_mock()
                attr.return_value = {"status": "ok"}
    return vn.VectorClawNode


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestNodeCreation:
    def test_publishers_created(self):
        VCN = _fresh_node_class()
        node = VCN()
        topics = [p.topic for p in node._publishers]
        assert "/vector/status" in topics
        assert "/vector/pose" in topics
        assert "/vector/proximity" in topics
        assert "/vector/touch" in topics
        assert "/vector/camera" in topics

    def test_subscriptions_created(self):
        VCN = _fresh_node_class()
        node = VCN()
        topics = [s.topic for s in node._subscriptions]
        assert "/vector/cmd_vel" in topics
        assert "/vector/cmd_say" in topics
        assert "/vector/cmd_head" in topics
        assert "/vector/cmd_lift" in topics
        assert "/vector/cmd_animate" in topics

    def test_services_created(self):
        VCN = _fresh_node_class()
        node = VCN()
        names = [s.name for s in node._services]
        assert "/vector/emergency_stop" in names
        assert "/vector/drive_off_charger" in names

    def test_timers_created(self):
        VCN = _fresh_node_class()
        node = VCN()
        # status_hz=1 → 2 timers (status + pose)
        # sensor_hz=5 → 3 timers (proximity + touch + camera)
        assert len(node._timers) == 5


class TestCmdVelCallback:
    def test_forward_drive_dispatched(self):
        import vectorclaw_ros2.vector_node as vn_mod

        VCN = _fresh_node_class()
        node = VCN()

        class _Twist:
            class _V: x = 150.0; y = 0.0; z = 0.0
            class _A: x = 0.0; y = 0.0; z = 0.0
            linear = _V(); angular = _A()

        node._cmd_vel_cb(_Twist())
        node._executor.shutdown(wait=True)

        vn_mod.vector_drive.assert_called_once()
        kwargs = vn_mod.vector_drive.call_args.kwargs
        assert kwargs["distance_mm"] == 150.0

    def test_zero_command_ignored(self):
        import vectorclaw_ros2.vector_node as vn_mod

        VCN = _fresh_node_class()
        node = VCN()

        class _ZeroTwist:
            class _V: x = 0.0; y = 0.0; z = 0.0
            class _A: x = 0.0; y = 0.0; z = 0.0
            linear = _V(); angular = _A()

        node._cmd_vel_cb(_ZeroTwist())
        node._executor.shutdown(wait=True)
        vn_mod.vector_drive.assert_not_called()

    def test_turn_command_dispatched(self):
        import vectorclaw_ros2.vector_node as vn_mod

        VCN = _fresh_node_class()
        node = VCN()

        class _TurnTwist:
            class _V: x = 0.0; y = 0.0; z = 0.0
            class _A: x = 0.0; y = 0.0; z = 90.0
            linear = _V(); angular = _A()

        node._cmd_vel_cb(_TurnTwist())
        node._executor.shutdown(wait=True)

        kwargs = vn_mod.vector_drive.call_args.kwargs
        assert kwargs["angle_deg"] == 90.0
        assert kwargs["distance_mm"] is None


class TestCmdSayCallback:
    def test_say_forwards_text(self):
        import vectorclaw_ros2.vector_node as vn_mod

        VCN = _fresh_node_class()
        node = VCN()
        msg = MagicMock()
        msg.data = "Hello ROS2"
        node._cmd_say_cb(msg)
        node._executor.shutdown(wait=True)
        vn_mod.vector_say.assert_called_once_with("Hello ROS2")

    def test_empty_say_ignored(self):
        import vectorclaw_ros2.vector_node as vn_mod

        VCN = _fresh_node_class()
        node = VCN()
        msg = MagicMock()
        msg.data = "   "
        node._cmd_say_cb(msg)
        node._executor.shutdown(wait=True)
        vn_mod.vector_say.assert_not_called()


class TestCmdHeadLiftCallbacks:
    def test_head_callback(self):
        import vectorclaw_ros2.vector_node as vn_mod

        VCN = _fresh_node_class()
        node = VCN()
        msg = MagicMock()
        msg.data = 15.0
        node._cmd_head_cb(msg)
        node._executor.shutdown(wait=True)
        vn_mod.vector_head.assert_called_once_with(15.0)

    def test_lift_callback(self):
        import vectorclaw_ros2.vector_node as vn_mod

        VCN = _fresh_node_class()
        node = VCN()
        msg = MagicMock()
        msg.data = 0.75
        node._cmd_lift_cb(msg)
        node._executor.shutdown(wait=True)
        vn_mod.vector_lift.assert_called_once_with(0.75)


class TestServices:
    def test_emergency_stop_success(self):
        import vectorclaw_ros2.vector_node as vn_mod

        VCN = _fresh_node_class()
        node = VCN()
        vn_mod.vector_emergency_stop.return_value = {"status": "ok"}
        response = MagicMock()
        node._emergency_stop_srv(MagicMock(), response)
        assert response.success is True

    def test_emergency_stop_failure_propagated(self):
        import vectorclaw_ros2.vector_node as vn_mod

        VCN = _fresh_node_class()
        node = VCN()
        vn_mod.vector_emergency_stop.return_value = {
            "status": "error", "message": "motors jammed"
        }
        response = MagicMock()
        node._emergency_stop_srv(MagicMock(), response)
        assert response.success is False
        assert response.message == "motors jammed"

    def test_drive_off_charger_service(self):
        import vectorclaw_ros2.vector_node as vn_mod

        VCN = _fresh_node_class()
        node = VCN()
        vn_mod.vector_drive_off_charger.return_value = {"status": "ok"}
        response = MagicMock()
        node._drive_off_charger_srv(MagicMock(), response)
        assert response.success is True
