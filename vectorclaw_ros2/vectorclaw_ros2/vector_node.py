"""VectorClaw ROS2 Bridge Node.

Bridges the Anki Vector robot to the ROS2 ecosystem by:
  - Publishing sensor/status data as standard ROS2 topics
  - Subscribing to command topics that drive the robot
  - Exposing emergency-stop and charger control as ROS2 services

Architecture
------------
The node reuses the VectorClaw tool functions directly
(vectorclaw_mcp.tools_motion, tools_perception, etc.).  All SDK calls are
dispatched to a ThreadPoolExecutor so they never block the rclpy spin loop.

Topics Published
----------------
  /vector/status        std_msgs/String        (JSON)  1 Hz
  /vector/pose          geometry_msgs/PoseStamped       1 Hz
  /vector/proximity     sensor_msgs/Range               5 Hz
  /vector/camera        sensor_msgs/Image               5 Hz
  /vector/touch         std_msgs/Bool                   5 Hz

Topics Subscribed
-----------------
  /vector/cmd_vel       geometry_msgs/Twist   drive (linear.x mm/s, angular.z deg/s)
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
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped, Quaternion, Twist
from sensor_msgs.msg import Image, Range
from std_msgs.msg import Bool, Float32, String
from std_srvs.srv import Trigger

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
except ImportError as exc:
    sys.exit(
        f"[vectorclaw_ros2] Cannot import vectorclaw_mcp: {exc}\n"
        "Install it with: pip install vectorclaw-mcp   (or pip install -e /path/to/VectorClaw)"
    )

logger = logging.getLogger(__name__)


def _yaw_to_quaternion(yaw_deg: float) -> Quaternion:
    """Convert a yaw angle (degrees) to a geometry_msgs/Quaternion."""
    import math

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
    frame_id   (str, default 'vector') — TF frame_id used in stamped messages
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

        status_hz: float = self.get_parameter("status_hz").value
        sensor_hz: float = self.get_parameter("sensor_hz").value
        self._camera_enabled: bool = self.get_parameter("camera_enabled").value
        self._frame_id: str = self.get_parameter("frame_id").value

        # SDK calls are synchronous — run them off the spin thread
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="vclaw")

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
        self.create_service(Trigger, "/vector/emergency_stop", self._emergency_stop_srv)
        self.create_service(
            Trigger, "/vector/drive_off_charger", self._drive_off_charger_srv
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

    def _status_timer_cb(self) -> None:
        self._executor.submit(self._publish_status)

    def _pose_timer_cb(self) -> None:
        self._executor.submit(self._publish_pose)

    def _proximity_timer_cb(self) -> None:
        self._executor.submit(self._publish_proximity)

    def _touch_timer_cb(self) -> None:
        self._executor.submit(self._publish_touch)

    def _camera_timer_cb(self) -> None:
        self._executor.submit(self._publish_camera)

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
            msg = PoseStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = self._frame_id
            msg.pose.position.x = float(data.get("x", 0.0)) / 1000.0
            msg.pose.position.y = float(data.get("y", 0.0)) / 1000.0
            msg.pose.position.z = float(data.get("z", 0.0)) / 1000.0
            msg.pose.orientation = _yaw_to_quaternion(float(data.get("angle_deg", 0.0)))
            self._pub_pose.publish(msg)
        except Exception:
            self.get_logger().warning("Failed to publish /vector/pose", once=True)

    def _publish_proximity(self) -> None:
        try:
            data = vector_proximity_status()
            msg = Range()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = self._frame_id
            msg.radiation_type = Range.INFRARED
            msg.field_of_view = 0.4363  # ~25 degrees in radians
            msg.min_range = 0.03        # 30 mm
            msg.max_range = 0.30        # 300 mm
            msg.range = float(data.get("distance_mm", 0.0)) / 1000.0  # mm → m
            self._pub_proximity.publish(msg)
        except Exception:
            self.get_logger().warning("Failed to publish /vector/proximity", once=True)

    def _publish_touch(self) -> None:
        try:
            data = vector_touch_status()
            msg = Bool()
            msg.data = bool(data.get("is_being_touched", False))
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
            msg.header.frame_id = self._frame_id
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

    def _cmd_vel_cb(self, msg: Twist) -> None:
        """Map Twist → vector_drive.

        linear.x  : forward speed in mm/s  (treated as distance for one-shot drive)
        angular.z : turn rate in deg/s      (treated as angle for one-shot turn)

        For continuous velocity control, publish at your desired control rate
        and the node will issue repeated drive commands.
        """
        distance_mm = float(msg.linear.x) if abs(msg.linear.x) > 0.1 else None
        angle_deg = float(msg.angular.z) if abs(msg.angular.z) > 0.1 else None

        if distance_mm is None and angle_deg is None:
            return  # dead-zone: ignore zero commands

        speed = max(10, min(300, int(abs(distance_mm)))) if distance_mm else 50
        self._executor.submit(
            vector_drive, speed=speed, distance_mm=distance_mm, angle_deg=angle_deg
        )

    def _cmd_say_cb(self, msg: String) -> None:
        text = msg.data.strip()
        if text:
            self._executor.submit(vector_say, text)

    def _cmd_head_cb(self, msg: Float32) -> None:
        self._executor.submit(vector_head, float(msg.data))

    def _cmd_lift_cb(self, msg: Float32) -> None:
        self._executor.submit(vector_lift, float(msg.data))

    def _cmd_animate_cb(self, msg: String) -> None:
        name = msg.data.strip()
        if name:
            self._executor.submit(vector_animate, name)

    # ---------------------------------------------------------------------- #
    # Service callbacks
    # ---------------------------------------------------------------------- #

    def _emergency_stop_srv(
        self, _request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        result = vector_emergency_stop()
        response.success = result.get("status") == "ok"
        response.message = result.get("message", "")
        return response

    def _drive_off_charger_srv(
        self, _request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        result = vector_drive_off_charger()
        response.success = result.get("status") == "ok"
        response.message = result.get("message", "")
        return response

    def destroy_node(self) -> None:
        """Shutdown the thread pool before destroying the node."""
        self._executor.shutdown(wait=False)
        super().destroy_node()


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = VectorClawNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
