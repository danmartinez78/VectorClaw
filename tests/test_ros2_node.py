import importlib
import sys
import threading
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add the vectorclaw_ros2 package root so importlib can find it without a colcon install
_ROS2_PKG_ROOT = Path(__file__).resolve().parent.parent / "vectorclaw_ros2"

_ALL_FNS = [
    "vector_say", "vector_animate", "vector_pose",
    "vector_drive", "vector_drive_off_charger", "vector_emergency_stop",
    "vector_head", "vector_lift",
    "vector_status", "vector_proximity_status",
    "vector_touch_status", "vector_capture_image",
]

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
            self.published_tf: list = []

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
                "world_frame_id": "vector_world",
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

        def create_service(self, srv_type, name, cb, callback_group=None):
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
            cls = type(n, (MagicMock,), {})
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

    class _Header:
        stamp = None
        frame_id = ""

    class _Tf:
        def __init__(self):
            self.header = _Header()
            self.child_frame_id = ""
            self.transform = MagicMock()

    geo.TransformStamped = _Tf

    sensor = _simple("sensor_msgs.msg", "Image", "Range")
    sensor.Range.INFRARED = 1

    return stubs


def _make_extra_stubs(rclpy: types.ModuleType) -> dict[str, types.ModuleType]:
    cbg = types.ModuleType("rclpy.callback_groups")
    cbg.ReentrantCallbackGroup = MagicMock
    exe = types.ModuleType("rclpy.executors")
    exe.MultiThreadedExecutor = MagicMock
    tf2 = types.ModuleType("tf2_ros")
    tf2.TransformBroadcaster = lambda node: MagicMock()
    tf2.StaticTransformBroadcaster = lambda node: MagicMock()
    return {
        "rclpy.callback_groups": cbg,
        "rclpy.executors": exe,
        "tf2_ros": tf2,
    }


@pytest.fixture
def ros2_env(monkeypatch):
    """Install ROS2 stubs and mock tool functions for one test only.

    Everything is installed through ``monkeypatch`` so ``sys.modules`` and the
    real ``vectorclaw_mcp`` tool modules are restored afterwards.
    """
    import vectorclaw_mcp.tools as tools_mod
    import vectorclaw_mcp.tools_motion as motion_mod
    import vectorclaw_mcp.tools_perception as perception_mod

    rclpy = _make_rclpy_stub()
    modules = {"rclpy": rclpy, "rclpy.node": rclpy.node}
    modules.update(_make_msg_stubs())
    modules.update(_make_extra_stubs(rclpy))
    for name, mod in modules.items():
        monkeypatch.setitem(sys.modules, name, mod)

    for fn in _ALL_FNS:
        mock = MagicMock(return_value={"status": "ok"})
        for mod in (tools_mod, motion_mod, perception_mod):
            if hasattr(mod, fn):
                monkeypatch.setattr(mod, fn, mock)

    monkeypatch.syspath_prepend(str(_ROS2_PKG_ROOT))
    monkeypatch.delitem(sys.modules, "vectorclaw_ros2.vector_node", raising=False)
    monkeypatch.delitem(sys.modules, "vectorclaw_ros2", raising=False)
    vn = importlib.import_module("vectorclaw_ros2.vector_node")
    yield vn
    sys.modules.pop("vectorclaw_ros2.vector_node", None)
    sys.modules.pop("vectorclaw_ros2", None)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def _twist(x=0.0, z=0.0):
    t = MagicMock()
    t.linear.x = x
    t.angular.z = z
    return t


def _drain(node):
    node._executor.shutdown(wait=True)
    node._stop_executor.shutdown(wait=True)
    node._poll_executor.shutdown(wait=True)


class TestNodeCreation:
    def test_publishers_created(self, ros2_env):
        node = ros2_env.VectorClawNode()
        topics = [p.topic for p in node._publishers]
        for t in ("status", "pose", "proximity", "touch", "camera"):
            assert f"/vector/{t}" in topics

    def test_subscriptions_created(self, ros2_env):
        node = ros2_env.VectorClawNode()
        topics = [s.topic for s in node._subscriptions]
        for t in ("cmd_vel", "cmd_say", "cmd_head", "cmd_lift", "cmd_animate"):
            assert f"/vector/{t}" in topics

    def test_services_created(self, ros2_env):
        node = ros2_env.VectorClawNode()
        names = [s.name for s in node._services]
        assert "/vector/emergency_stop" in names
        assert "/vector/drive_off_charger" in names

    def test_timers_created(self, ros2_env):
        node = ros2_env.VectorClawNode()
        assert len(node._timers) == 5


class TestCmdVelCallback:
    def test_forward_velocity_converted_to_si(self, ros2_env):
        node = ros2_env.VectorClawNode()
        calls = []

        def fake_drive(**kw):
            calls.append(kw)
            node._invalidate_motion()  # end the loop after one step
            return {"status": "ok"}

        ros2_env.vector_drive.side_effect = fake_drive
        node._cmd_vel_cb(_twist(x=0.1))
        _drain(node)

        assert len(calls) == 1
        assert calls[0]["speed"] == 100  # 0.1 m/s -> 100 mm/s
        assert calls[0]["distance_mm"] == pytest.approx(25.0)  # 100 mm/s * 0.25 s
        assert calls[0]["angle_deg"] is None

    def test_drive_distance_uses_clamped_speed(self, ros2_env):
        node = ros2_env.VectorClawNode()

        def fake_drive(**kw):
            node._invalidate_motion()
            return {"status": "ok"}

        ros2_env.vector_drive.side_effect = fake_drive
        node._cmd_vel_cb(_twist(x=1.0))
        _drain(node)

        assert ros2_env.vector_drive.call_args.kwargs["speed"] == 200
        assert ros2_env.vector_drive.call_args.kwargs["distance_mm"] == 50.0

    def test_turn_rate_converted_to_degrees(self, ros2_env):
        import math

        node = ros2_env.VectorClawNode()
        calls = []

        def fake_drive(**kw):
            calls.append(kw)
            node._invalidate_motion()
            return {"status": "ok"}

        ros2_env.vector_drive.side_effect = fake_drive
        node._cmd_vel_cb(_twist(z=math.pi / 2))  # 90 deg/s
        _drain(node)

        assert calls[0]["distance_mm"] is None
        assert calls[0]["angle_deg"] == pytest.approx(22.5)
        assert calls[0]["turn_speed_degps"] == pytest.approx(90.0)

    def test_turn_step_and_speed_are_bounded(self, ros2_env):
        node = ros2_env.VectorClawNode()

        def fake_drive(**kw):
            node._invalidate_motion()
            return {"status": "ok"}

        ros2_env.vector_drive.side_effect = fake_drive
        node._cmd_vel_cb(_twist(z=10.0))
        _drain(node)

        assert ros2_env.vector_drive.call_args.kwargs["angle_deg"] == 45.0
        assert ros2_env.vector_drive.call_args.kwargs["turn_speed_degps"] == 180.0

    def test_zero_twist_stops_motors(self, ros2_env):
        node = ros2_env.VectorClawNode()
        stopped = threading.Event()
        ros2_env.vector_emergency_stop.side_effect = (
            lambda: stopped.set() or {"status": "ok"}
        )
        node._cmd_vel_cb(_twist())
        assert stopped.wait(timeout=1)
        _drain(node)
        ros2_env.vector_emergency_stop.assert_called_once()
        ros2_env.vector_drive.assert_not_called()

    def test_zero_twist_invalidates_queued_commands(self, ros2_env):
        node = ros2_env.VectorClawNode()
        gate = threading.Event()
        # Block both workers so later submissions stay queued
        for _ in range(2):
            node._executor.submit(gate.wait)
        node._cmd_head_cb(MagicMock(data=10.0))
        stopped = threading.Event()
        ros2_env.vector_emergency_stop.side_effect = (
            lambda: stopped.set() or {"status": "ok"}
        )
        node._cmd_vel_cb(_twist())  # stop: invalidates the queued head command
        assert stopped.wait(timeout=1)
        gate.set()
        _drain(node)
        ros2_env.vector_emergency_stop.assert_called_once()
        ros2_env.vector_head.assert_not_called()

    def test_fresh_velocity_is_restarted_after_stale_worker_exits(self, ros2_env):
        node = ros2_env.VectorClawNode()
        started = threading.Event()
        release = threading.Event()
        successor_started = threading.Event()
        calls = []

        def fake_drive(**kw):
            calls.append(kw)
            if len(calls) == 1:
                started.set()
                release.wait(timeout=2)
                return {"status": "cancelled"}
            successor_started.set()
            node._invalidate_motion()
            return {"status": "ok"}

        ros2_env.vector_drive.side_effect = fake_drive
        node._cmd_vel_cb(_twist(x=0.1))
        assert started.wait(timeout=1)
        node._cmd_vel_cb(_twist())
        node._cmd_vel_cb(_twist(x=0.2))
        release.set()
        assert successor_started.wait(timeout=1)
        _drain(node)

        assert len(calls) == 2
        assert calls[1]["distance_mm"] == pytest.approx(50.0)
        ros2_env.vector_emergency_stop.assert_called_once()

    def test_velocity_loop_stops_after_error_result(self, ros2_env):
        node = ros2_env.VectorClawNode()
        ros2_env.vector_drive.return_value = {
            "status": "error", "message": "on charger"
        }

        node._cmd_vel_cb(_twist(x=0.1))
        _drain(node)

        ros2_env.vector_drive.assert_called_once()


class TestCmdSayCallback:
    def test_say_forwards_text(self, ros2_env):
        node = ros2_env.VectorClawNode()
        node._cmd_say_cb(MagicMock(data="Hello ROS2"))
        _drain(node)
        ros2_env.vector_say.assert_called_once_with("Hello ROS2")

    def test_empty_say_ignored(self, ros2_env):
        node = ros2_env.VectorClawNode()
        node._cmd_say_cb(MagicMock(data="   "))
        _drain(node)
        ros2_env.vector_say.assert_not_called()


class TestCmdHeadLiftCallbacks:
    def test_head_callback(self, ros2_env):
        node = ros2_env.VectorClawNode()
        node._cmd_head_cb(MagicMock(data=15.0))
        _drain(node)
        ros2_env.vector_head.assert_called_once_with(15.0)

    def test_lift_callback(self, ros2_env):
        node = ros2_env.VectorClawNode()
        node._cmd_lift_cb(MagicMock(data=0.75))
        _drain(node)
        ros2_env.vector_lift.assert_called_once_with(0.75)


class TestServices:
    def test_emergency_stop_success(self, ros2_env):
        node = ros2_env.VectorClawNode()
        response = MagicMock()
        node._emergency_stop_srv(MagicMock(), response)
        assert response.success is True

    def test_emergency_stop_failure_propagated(self, ros2_env):
        node = ros2_env.VectorClawNode()
        ros2_env.vector_emergency_stop.return_value = {
            "status": "error", "message": "motors jammed"
        }
        response = MagicMock()
        node._emergency_stop_srv(MagicMock(), response)
        assert response.success is False
        assert response.message == "motors jammed"

    def test_emergency_stop_exception_returned(self, ros2_env):
        node = ros2_env.VectorClawNode()
        ros2_env.vector_emergency_stop.side_effect = RuntimeError("not connected")
        response = MagicMock()
        node._emergency_stop_srv(MagicMock(), response)
        assert response.success is False
        assert response.message == "not connected"

    def test_emergency_stop_cancels_pending_actuation(self, ros2_env):
        node = ros2_env.VectorClawNode()
        gate = threading.Event()
        for _ in range(2):
            node._executor.submit(gate.wait)
        node._cmd_lift_cb(MagicMock(data=1.0))
        node._emergency_stop_srv(MagicMock(), MagicMock())
        gate.set()
        _drain(node)
        ros2_env.vector_lift.assert_not_called()

    def test_drive_off_charger_service(self, ros2_env):
        node = ros2_env.VectorClawNode()
        response = MagicMock()
        node._drive_off_charger_srv(MagicMock(), response)
        assert response.success is True

    def test_drive_off_charger_exception_returned(self, ros2_env):
        node = ros2_env.VectorClawNode()
        ros2_env.vector_drive_off_charger.side_effect = RuntimeError("no config")
        response = MagicMock()
        node._drive_off_charger_srv(MagicMock(), response)
        assert response.success is False
        assert response.message == "no config"


class TestPublishers:
    def test_pose_converted_to_meters_in_world_frame(self, ros2_env):
        node = ros2_env.VectorClawNode()
        ros2_env.vector_pose.return_value = {
            "status": "ok", "x": 100.0, "y": 200.0, "z": 0.0, "angle_deg": 0.0
        }
        node._publish_pose()
        msg = node._pub_pose.publish.call_args.args[0]
        assert msg.pose.position.x == pytest.approx(0.1)
        assert msg.pose.position.y == pytest.approx(0.2)
        assert msg.header.frame_id == "vector_world"

    def test_proximity_error_skipped(self, ros2_env):
        node = ros2_env.VectorClawNode()
        ros2_env.vector_proximity_status.return_value = {"status": "error", "message": "x"}
        node._publish_proximity()
        node._pub_proximity.publish.assert_not_called()

    def test_proximity_published_in_sensor_frame(self, ros2_env):
        node = ros2_env.VectorClawNode()
        ros2_env.vector_proximity_status.return_value = {"status": "ok", "distance_mm": 150.0}
        node._publish_proximity()
        msg = node._pub_proximity.publish.call_args.args[0]
        assert msg.range == pytest.approx(0.15)
        assert msg.header.frame_id == "vector_proximity"

    def test_touch_error_skipped(self, ros2_env):
        node = ros2_env.VectorClawNode()
        ros2_env.vector_touch_status.return_value = {"status": "error", "message": "x"}
        node._publish_touch()
        node._pub_touch.publish.assert_not_called()

    def test_polls_coalesced(self, ros2_env):
        node = ros2_env.VectorClawNode()
        gate = threading.Event()
        ros2_env.vector_status.side_effect = lambda: gate.wait() or {"status": "ok"}
        for _ in range(5):
            node._status_timer_cb()
        gate.set()
        _drain(node)
        assert ros2_env.vector_status.call_count == 1


class TestShutdown:
    def test_destroy_stops_and_disconnects(self, ros2_env):
        node = ros2_env.VectorClawNode()
        ros2_env.robot_manager = MagicMock()
        node.destroy_node()
        ros2_env.robot_manager.disconnect.assert_called_once()
        node._cmd_say_cb(MagicMock(data="late"))
        ros2_env.vector_say.assert_not_called()
