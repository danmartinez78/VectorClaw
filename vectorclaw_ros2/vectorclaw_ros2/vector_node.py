"""VectorClaw ROS2 Bridge Node.

Bridges the Anki Vector robot to the ROS2 ecosystem by:
  - Publishing sensor/status data as standard ROS2 topics
  - Subscribing to command topics that drive the robot
  - Exposing emergency-stop and charger control as ROS2 services

Architecture
------------
The node reuses the VectorClaw tool functions directly
(vectorclaw_mcp.tools_motion, tools_perception, etc.).  All SDK calls are
dispatched to worker ThreadPoolExecutors so they never block the rclpy spin
loop.  Telemetry polls are coalesced (at most one outstanding job per stream)
and run on a pool separate from command dispatch.  Actuation is tagged with a
generation counter: emergency stop / zero cmd_vel / shutdown bump it, so any
queued or in-progress multi-step command is abandoned instead of moving the
robot after the stop.  Service callbacks run in a reentrant callback group on a
MultiThreadedExecutor so /vector/emergency_stop stays available while another
service call is blocked.

TF frames
---------
  <world_frame_id>  (default 'vector_world')  parent of the robot base
  <frame_id>        (default 'vector')        robot base; pose is world -> base
  <frame_id>_proximity / <frame_id>_camera_optical  sensor frames (static TF)

Topics Published
----------------
  /vector/status        std_msgs/String        (JSON)  1 Hz
  /vector/pose          geometry_msgs/PoseStamped       1 Hz  (meters, world frame)
  /vector/proximity     sensor_msgs/Range               5 Hz
  /vector/camera        sensor_msgs/Image               5 Hz
  /vector/touch         std_msgs/Bool                   5 Hz

Topics Subscribed
-----------------
  /vector/cmd_vel       geometry_msgs/Twist   velocity (linear.x m/s, angular.z rad/s)
  /vector/cmd_say       std_msgs/String       TTS
  /vector/cmd_head      std_msgs/Float32      head angle degrees
  /vector/cmd_lift      std_msgs/Float32      lift height 0.0–1.0
  /vector/cmd_animate   std_msgs/String       animation name

Services
--------
  /vector/emergency_stop      std_srvs/Trigger
  /vector/drive_off_charger   std_srvs/Trigger

Usage
-----
  ros2 run vectorclaw_ros2 vectorclaw_node
"""

from __future__ import annotations

import base64
import io
import json
import logging
import math
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped, Quaternion, TransformStamped, Twist
from sensor_msgs.msg import Image, Range
from std_msgs.msg import Bool, Float32, String
from std_srvs.srv import Trigger
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster

# ---------------------------------------------------------------------------
# Import VectorClaw tool functions.
# The vectorclaw_mcp package must be installed (pip install vectorclaw-mcp or
# the dev-editable install: pip install -e path/to/VectorClaw).
# ---------------------------------------------------------------------------
try:
    from vectorclaw_mcp.tools_motion import (
        vector_drive,
        vector_drive_off_charger,
        vector_emergency_stop,
        vector_head,
        vector_lift,
    )
    from vectorclaw_mcp.tools_perception import (
        vector_capture_image,
        vector_proximity_status,
        vector_status,
        vector_touch_status,
    )
    from vectorclaw_mcp.tools import (  # type: ignore[import]
        vector_animate,
        vector_pose,
        vector_say,
    )
    from vectorclaw_mcp.robot import robot_manager
except ImportError as exc:
    sys.exit(
        f"[vectorclaw_ros2] Cannot import vectorclaw_mcp: {exc}\n"
        "Install it with: pip install vectorclaw-mcp   (or pip install -e /path/to/VectorClaw)"
    )

logger = logging.getLogger(__name__)

# Twist -> SDK drive mapping
_VEL_STEP_SEC = 0.25        # duration of each bounded drive step
_VEL_TIMEOUT_SEC = 0.5      # stop driving if no new cmd_vel arrives within this
_MIN_SPEED_MMPS = 10
_MAX_SPEED_MMPS = 200
_MAX_TURN_STEP_DEG = 45.0
_MAX_TURN_SPEED_DEGPS = 180.0
_EPS = 1e-6


def _yaw_to_quaternion(yaw_deg: float) -> Quaternion:
    """Convert a yaw angle (degrees) to a geometry_msgs/Quaternion."""
    yaw_rad = math.radians(yaw_deg)
    q = Quaternion()
    q.w = math.cos(yaw_rad / 2.0)
    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(yaw_rad / 2.0)
    return q


class VectorClawNode(Node):
    """ROS2 node that bridges the Anki Vector robot to standard ROS2 interfaces.

    Parameters (ROS2 parameters, set via --ros-args -p name:=value)
    ------------------------------------------------------------------
    status_hz  (float, default 1.0)  — publish rate for /vector/status and /vector/pose
    sensor_hz  (float, default 5.0)  — publish rate for /vector/proximity, /camera, /touch
    camera_enabled (bool, default True) — enable camera publishing (costs ~30% CPU)
    frame_id   (str, default 'vector') — robot base frame; sensor frames are
                 '<frame_id>_proximity' and '<frame_id>_camera_optical'
    world_frame_id (str, default 'vector_world') — frame the pose is expressed in
    """

    def __init__(self) -> None:
        super().__init__("vectorclaw_node")

        # ------------------------------------------------------------------ #
        # Parameters
        # ------------------------------------------------------------------ #
        self.declare_parameter("status_hz", 1.0)
        self.declare_parameter("sensor_hz", 5.0)
        self.declare_parameter("camera_enabled", True)
        self.declare_parameter("frame_id", "vector")
        self.declare_parameter("world_frame_id", "vector_world")

        status_hz: float = self.get_parameter("status_hz").value
        sensor_hz: float = self.get_parameter("sensor_hz").value
        self._camera_enabled: bool = self.get_parameter("camera_enabled").value
        self._frame_id: str = self.get_parameter("frame_id").value
        self._world_frame_id: str = self.get_parameter("world_frame_id").value
        self._proximity_frame_id = f"{self._frame_id}_proximity"
        self._camera_frame_id = f"{self._frame_id}_camera_optical"

        # SDK calls are synchronous — run them off the spin thread.
        # Commands and telemetry use separate pools so polling cannot starve control.
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="vclaw-cmd")
        self._stop_executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="vclaw-stop"
        )
        self._poll_executor = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="vclaw-poll"
        )
        self._state_lock = threading.Lock()
        self._motion_lock = threading.Lock()
        self._stop_complete = threading.Event()
        self._stop_complete.set()
        self._pending_stops = 0
        self._generation = 0
        self._shutting_down = False
        self._inflight_polls: set[str] = set()
        self._latest_vel: tuple[float, float, float] | None = None
        self._vel_loop_running = False

        self._tf_broadcaster = TransformBroadcaster(self)
        self._static_tf_broadcaster = StaticTransformBroadcaster(self)
        self._publish_static_transforms()

        # ------------------------------------------------------------------ #
        # Publishers
        # ------------------------------------------------------------------ #
        self._pub_status = self.create_publisher(String, "/vector/status", 10)
        self._pub_pose = self.create_publisher(PoseStamped, "/vector/pose", 10)
        self._pub_proximity = self.create_publisher(Range, "/vector/proximity", 10)
        self._pub_touch = self.create_publisher(Bool, "/vector/touch", 10)
        if self._camera_enabled:
            self._pub_camera = self.create_publisher(Image, "/vector/camera", 10)

        # ------------------------------------------------------------------ #
        # Subscribers
        # ------------------------------------------------------------------ #
        self.create_subscription(Twist, "/vector/cmd_vel", self._cmd_vel_cb, 10)
        self.create_subscription(String, "/vector/cmd_say", self._cmd_say_cb, 10)
        self.create_subscription(Float32, "/vector/cmd_head", self._cmd_head_cb, 10)
        self.create_subscription(Float32, "/vector/cmd_lift", self._cmd_lift_cb, 10)
        self.create_subscription(String, "/vector/cmd_animate", self._cmd_animate_cb, 10)

        # ------------------------------------------------------------------ #
        # Services
        # ------------------------------------------------------------------ #
        # Reentrant group + MultiThreadedExecutor (see main) keeps emergency stop
        # callable while another service call is blocked in the SDK.
        self._srv_group = ReentrantCallbackGroup()
        self.create_service(
            Trigger,
            "/vector/emergency_stop",
            self._emergency_stop_srv,
            callback_group=self._srv_group,
        )
        self.create_service(
            Trigger,
            "/vector/drive_off_charger",
            self._drive_off_charger_srv,
            callback_group=self._srv_group,
        )

        # ------------------------------------------------------------------ #
        # Timers
        # ------------------------------------------------------------------ #
        status_period = 1.0 / max(status_hz, 0.1)
        sensor_period = 1.0 / max(sensor_hz, 0.1)

        self.create_timer(status_period, self._status_timer_cb)
        self.create_timer(status_period, self._pose_timer_cb)
        self.create_timer(sensor_period, self._proximity_timer_cb)
        self.create_timer(sensor_period, self._touch_timer_cb)
        if self._camera_enabled:
            self.create_timer(sensor_period, self._camera_timer_cb)

        self.get_logger().info(
            f"VectorClaw ROS2 node started "
            f"(status_hz={status_hz}, sensor_hz={sensor_hz}, "
            f"camera={'on' if self._camera_enabled else 'off'})"
        )

    # ---------------------------------------------------------------------- #
    # Timer callbacks — publishers
    # ---------------------------------------------------------------------- #

    def _submit_poll(self, key: str, fn: Callable[[], None]) -> None:
        """Run a telemetry poll off-thread, at most one outstanding job per stream."""
        with self._state_lock:
            if self._shutting_down or key in self._inflight_polls:
                return
            self._inflight_polls.add(key)

        def _run() -> None:
            try:
                fn()
            finally:
                with self._state_lock:
                    self._inflight_polls.discard(key)

        try:
            self._poll_executor.submit(_run)
        except RuntimeError:  # executor already shut down
            with self._state_lock:
                self._inflight_polls.discard(key)

    def _status_timer_cb(self) -> None:
        self._submit_poll("status", self._publish_status)

    def _pose_timer_cb(self) -> None:
        self._submit_poll("pose", self._publish_pose)

    def _proximity_timer_cb(self) -> None:
        self._submit_poll("proximity", self._publish_proximity)

    def _touch_timer_cb(self) -> None:
        self._submit_poll("touch", self._publish_touch)

    def _camera_timer_cb(self) -> None:
        self._submit_poll("camera", self._publish_camera)

    # ---------------------------------------------------------------------- #
    # Frames
    # ---------------------------------------------------------------------- #

    def _publish_static_transforms(self) -> None:
        """Publish approximate base -> sensor transforms (meters)."""
        stamp = self.get_clock().now().to_msg()

        prox = TransformStamped()
        prox.header.stamp = stamp
        prox.header.frame_id = self._frame_id
        prox.child_frame_id = self._proximity_frame_id
        prox.transform.translation.x = 0.03
        prox.transform.translation.z = 0.02
        prox.transform.rotation.w = 1.0

        cam = TransformStamped()
        cam.header.stamp = stamp
        cam.header.frame_id = self._frame_id
        cam.child_frame_id = self._camera_frame_id
        cam.transform.translation.x = 0.03
        cam.transform.translation.z = 0.05
        # Optical frame convention: z forward, x right, y down (rpy = -90, 0, -90)
        cam.transform.rotation.x = -0.5
        cam.transform.rotation.y = 0.5
        cam.transform.rotation.z = -0.5
        cam.transform.rotation.w = 0.5

        self._static_tf_broadcaster.sendTransform([prox, cam])

    # ---------------------------------------------------------------------- #
    # Publish helpers (run in thread pool)
    # ---------------------------------------------------------------------- #

    def _publish_status(self) -> None:
        try:
            data: dict[str, Any] = vector_status()
            msg = String()
            msg.data = json.dumps(data)
            self._pub_status.publish(msg)
        except Exception:
            self.get_logger().warning("Failed to publish /vector/status", once=True)

    def _publish_pose(self) -> None:
        try:
            data = vector_pose()
            if data.get("status") != "ok":
                return
            msg = PoseStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = self._world_frame_id
            msg.pose.position.x = float(data.get("x", 0.0)) / 1000.0
            msg.pose.position.y = float(data.get("y", 0.0)) / 1000.0
            msg.pose.position.z = float(data.get("z", 0.0)) / 1000.0
            msg.pose.orientation = _yaw_to_quaternion(float(data.get("angle_deg", 0.0)))
            self._pub_pose.publish(msg)

            tf = TransformStamped()
            tf.header = msg.header
            tf.child_frame_id = self._frame_id
            tf.transform.translation.x = msg.pose.position.x
            tf.transform.translation.y = msg.pose.position.y
            tf.transform.translation.z = msg.pose.position.z
            tf.transform.rotation = msg.pose.orientation
            self._tf_broadcaster.sendTransform(tf)
        except Exception:
            self.get_logger().warning("Failed to publish /vector/pose", once=True)

    def _publish_proximity(self) -> None:
        try:
            data = vector_proximity_status()
            if data.get("status") != "ok" or data.get("distance_mm") is None:
                return
            msg = Range()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = self._proximity_frame_id
            msg.radiation_type = Range.INFRARED
            msg.field_of_view = 0.4363  # ~25 degrees in radians
            msg.min_range = 0.03        # 30 mm
            msg.max_range = 0.30        # 300 mm
            msg.range = float(data["distance_mm"]) / 1000.0  # mm → m
            self._pub_proximity.publish(msg)
        except Exception:
            self.get_logger().warning("Failed to publish /vector/proximity", once=True)

    def _publish_touch(self) -> None:
        try:
            data = vector_touch_status()
            if data.get("status") != "ok" or "is_being_touched" not in data:
                return
            msg = Bool()
            msg.data = bool(data["is_being_touched"])
            self._pub_touch.publish(msg)
        except Exception:
            self.get_logger().warning("Failed to publish /vector/touch", once=True)

    def _publish_camera(self) -> None:
        try:
            data = vector_capture_image()
            if data.get("status") != "ok":
                return
            raw_bytes = base64.b64decode(data["image_base64"])
            from PIL import Image as PILImage  # noqa: PLC0415

            pil_img = PILImage.open(io.BytesIO(raw_bytes)).convert("RGB")
            width, height = pil_img.size
            msg = Image()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = self._camera_frame_id
            msg.height = height
            msg.width = width
            msg.encoding = "rgb8"
            msg.is_bigendian = False
            msg.step = width * 3
            msg.data = pil_img.tobytes()
            self._pub_camera.publish(msg)
        except Exception:
            self.get_logger().warning("Failed to publish /vector/camera", once=True)

    # ---------------------------------------------------------------------- #
    # Subscription callbacks
    # ---------------------------------------------------------------------- #

    def _submit_cmd(self, fn: Callable[..., Any], *args: Any) -> None:
        """Queue an actuation job that is dropped if a stop invalidates it first."""
        with self._state_lock:
            if self._shutting_down:
                return
            gen = self._generation

        def _run() -> None:
            try:
                self._stop_complete.wait()
                with self._motion_lock:
                    if not self._is_current(gen):
                        return
                    fn(*args)
            except Exception:
                self.get_logger().warning(f"Command {fn.__name__} failed", once=True)

        try:
            self._executor.submit(_run)
        except RuntimeError:  # executor already shut down
            pass

    def _invalidate_motion(self) -> None:
        """Abandon all queued and in-progress actuation."""
        with self._state_lock:
            self._generation += 1
            self._latest_vel = None

    def _is_current(self, gen: int) -> bool:
        with self._state_lock:
            return gen == self._generation and not self._shutting_down

    def _velocity_is_current(self, gen: int) -> bool:
        with self._state_lock:
            latest = self._latest_vel
            return (
                gen == self._generation
                and not self._shutting_down
                and latest is not None
                and time.monotonic() - latest[2] <= _VEL_TIMEOUT_SEC
            )

    def _stop_motors(self) -> dict[str, Any]:
        try:
            with self._motion_lock:
                return vector_emergency_stop()
        finally:
            with self._state_lock:
                self._pending_stops -= 1
                if self._pending_stops == 0:
                    self._stop_complete.set()

    def _schedule_stop(self):
        with self._state_lock:
            self._pending_stops += 1
            self._stop_complete.clear()
        try:
            return self._stop_executor.submit(self._stop_motors)
        except RuntimeError:
            with self._state_lock:
                self._pending_stops -= 1
                if self._pending_stops == 0:
                    self._stop_complete.set()
            return None

    def _dispatch_stop(self) -> dict[str, Any]:
        future = self._schedule_stop()
        return future.result() if future is not None else {
            "status": "error",
            "message": "Stop executor is shut down",
        }

    def _cmd_vel_cb(self, msg: Twist) -> None:
        """Map Twist (SI units) -> bounded SDK drive steps.

        linear.x  : forward velocity in m/s   (converted to mm/s)
        angular.z : yaw rate in rad/s         (converted to deg/s)

        The latest command wins.  While commands keep arriving (within
        ``_VEL_TIMEOUT_SEC``) the node executes short drive steps; when they stop
        arriving, or a zero Twist is received, motion stops.
        """
        lin_mmps = float(msg.linear.x) * 1000.0
        ang_dps = math.degrees(float(msg.angular.z))

        if abs(lin_mmps) < _EPS and abs(ang_dps) < _EPS:
            # Zero Twist is the "stop" command: invalidate queued/running motion
            # first, then dispatch the stop on its own worker.
            self._invalidate_motion()
            self._schedule_stop()
            return

        with self._state_lock:
            if self._shutting_down:
                return
            self._latest_vel = (lin_mmps, ang_dps, time.monotonic())
            if self._vel_loop_running:
                return
            self._vel_loop_running = True
            gen = self._generation

        try:
            self._executor.submit(self._vel_loop, gen)
        except RuntimeError:
            with self._state_lock:
                self._vel_loop_running = False

    def _vel_loop(self, gen: int) -> None:
        try:
            while True:
                self._stop_complete.wait()
                with self._state_lock:
                    latest = self._latest_vel
                    current = gen == self._generation and not self._shutting_down
                if not current or latest is None:
                    return
                lin_mmps, ang_dps, stamp = latest
                if time.monotonic() - stamp > _VEL_TIMEOUT_SEC:
                    return

                step_started = time.monotonic()
                kwargs: dict[str, Any] = {
                    "speed": _MIN_SPEED_MMPS,
                    "distance_mm": None,
                    "angle_deg": None,
                    "turn_speed_degps": None,
                }
                if abs(lin_mmps) >= _EPS:
                    speed = int(max(_MIN_SPEED_MMPS, min(_MAX_SPEED_MMPS, abs(lin_mmps))))
                    kwargs["speed"] = speed
                    kwargs["distance_mm"] = math.copysign(
                        speed * _VEL_STEP_SEC, lin_mmps
                    )
                if abs(ang_dps) >= _EPS:
                    turn_speed = min(abs(ang_dps), _MAX_TURN_SPEED_DEGPS)
                    kwargs["turn_speed_degps"] = turn_speed
                    kwargs["angle_deg"] = math.copysign(
                        min(turn_speed * _VEL_STEP_SEC, _MAX_TURN_STEP_DEG),
                        ang_dps,
                    )

                with self._motion_lock:
                    if not self._velocity_is_current(gen):
                        return
                    result = vector_drive(
                        **kwargs,
                        should_cancel=lambda: not self._velocity_is_current(gen),
                    )
                if result.get("status") != "ok":
                    if result.get("status") != "cancelled":
                        self.get_logger().warning("cmd_vel drive failed", once=True)
                    return

                remaining = _VEL_STEP_SEC - (time.monotonic() - step_started)
                if remaining > 0 and self._velocity_is_current(gen):
                    time.sleep(remaining)
        except Exception:
            self.get_logger().warning("cmd_vel drive failed", once=True)
        finally:
            successor_gen: int | None = None
            with self._state_lock:
                latest = self._latest_vel
                if (
                    gen != self._generation
                    and not self._shutting_down
                    and latest is not None
                    and time.monotonic() - latest[2] <= _VEL_TIMEOUT_SEC
                ):
                    successor_gen = self._generation
                else:
                    self._vel_loop_running = False
            if successor_gen is not None:
                try:
                    self._executor.submit(self._vel_loop, successor_gen)
                except RuntimeError:
                    with self._state_lock:
                        self._vel_loop_running = False

    def _cmd_say_cb(self, msg: String) -> None:
        text = msg.data.strip()
        if text:
            self._submit_cmd(vector_say, text)

    def _cmd_head_cb(self, msg: Float32) -> None:
        self._submit_cmd(vector_head, float(msg.data))

    def _cmd_lift_cb(self, msg: Float32) -> None:
        self._submit_cmd(vector_lift, float(msg.data))

    def _cmd_animate_cb(self, msg: String) -> None:
        name = msg.data.strip()
        if name:
            self._submit_cmd(vector_animate, name)

    # ---------------------------------------------------------------------- #
    # Service callbacks (run in a reentrant group on worker threads)
    # ---------------------------------------------------------------------- #

    @staticmethod
    def _fill_response(
        response: Trigger.Response, tool: Callable[[], dict]
    ) -> Trigger.Response:
        try:
            result = tool()
        except Exception as exc:
            response.success = False
            response.message = str(exc)
            return response
        response.success = result.get("status") == "ok"
        response.message = result.get("message", "")
        return response

    def _emergency_stop_srv(
        self, _request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        # Invalidate queued/active actuation before acknowledging so nothing
        # restarts motion after the stop.
        self._invalidate_motion()
        return self._fill_response(response, self._dispatch_stop)

    def _drive_off_charger(self) -> dict[str, Any]:
        self._stop_complete.wait()
        with self._motion_lock:
            with self._state_lock:
                if self._shutting_down:
                    return {"status": "error", "message": "Node is shutting down"}
            return vector_drive_off_charger()

    def _drive_off_charger_srv(
        self, _request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        return self._fill_response(response, self._drive_off_charger)

    def prepare_shutdown(self) -> None:
        """Reject new work and stop the motors before ROS callbacks are drained."""
        with self._state_lock:
            if self._shutting_down:
                return
            self._shutting_down = True
            self._generation += 1
            self._latest_vel = None
        try:
            if robot_manager.is_connected:
                self._dispatch_stop()
        except Exception:
            logger.exception("Failed to stop motors during shutdown")

    def destroy_node(self) -> None:
        """Stop accepting work, halt the robot, drain workers, then disconnect."""
        self.prepare_shutdown()
        self._executor.shutdown(wait=True, cancel_futures=True)
        self._stop_executor.shutdown(wait=True, cancel_futures=True)
        self._poll_executor.shutdown(wait=True, cancel_futures=True)
        try:
            robot_manager.disconnect()
        except Exception:
            logger.exception("Failed to disconnect during shutdown")
        super().destroy_node()


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = VectorClawNode()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.prepare_shutdown()
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
