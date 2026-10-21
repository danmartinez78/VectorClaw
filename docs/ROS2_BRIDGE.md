# ROS2 Bridge for VectorClaw

This document describes how to build, run, and interact with the VectorClaw
ROS2 bridge — a standard `rclpy` node that exposes the Anki Vector robot as
first-class ROS2 topics and services.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **ROS2 Jazzy** | `source /opt/ros/jazzy/setup.bash` |
| **Python 3.11+** | Matches VectorClaw's requirement |
| **vectorclaw-mcp** | `pip install vectorclaw-mcp` (or editable install) |
| **Pillow** | Installed automatically with vectorclaw-mcp |
| `VECTOR_SERIAL` env var | Printed on the underside of the robot |
| Vector on WiFi + Wire-Pod running | See [SETUP.md](SETUP.md) |

---

## Build & Install

```bash
# 1. Source ROS2 Jazzy
source /opt/ros/jazzy/setup.bash

# 2. Go to the repo root (not into vectorclaw_ros2/)
cd /path/to/VectorClaw

# 3. Build with colcon
colcon build --packages-select vectorclaw_ros2

# 4. Source the install overlay
source install/setup.bash
```

> **Tip:** Add both `source` lines to your `~/.bashrc` to avoid repeating them.

---

## Running the Node

```bash
export VECTOR_SERIAL=your-robot-serial-here
ros2 run vectorclaw_ros2 vectorclaw_node
```

### Optional Parameters

All parameters are set with `--ros-args -p name:=value`:

```bash
ros2 run vectorclaw_ros2 vectorclaw_node \
  --ros-args \
  -p status_hz:=1.0 \
  -p sensor_hz:=10.0 \
  -p camera_enabled:=true \
  -p frame_id:=vector
```

| Parameter | Default | Description |
|---|---|---|
| `status_hz` | `1.0` | Publish rate (Hz) for `/vector/status` and `/vector/pose` |
| `sensor_hz` | `5.0` | Publish rate (Hz) for proximity, touch, and camera |
| `camera_enabled` | `true` | Enables `/vector/camera` publishing (uses ~30% CPU) |
| `frame_id` | `"vector"` | Robot base frame. Sensor frames are `<frame_id>_proximity` and `<frame_id>_camera_optical` |
| `world_frame_id` | `"vector_world"` | Frame in which `/vector/pose` is expressed (TF `world_frame_id` → `frame_id` is broadcast) |

---

## Topics Published

| Topic | Type | Rate | Description |
|---|---|---|---|
| `/vector/status` | `std_msgs/String` | 1 Hz | JSON with battery, charging, cliff, carried, picked-up state |
| `/vector/pose` | `geometry_msgs/PoseStamped` | 1 Hz | Position in **meters** (SDK millimeters ÷ 1000) and yaw as quaternion, in `world_frame_id` |
| `/vector/proximity` | `sensor_msgs/Range` | 5 Hz | Front IR sensor (range in **meters**), in `<frame_id>_proximity`; skipped when the reading is unavailable |
| `/vector/camera` | `sensor_msgs/Image` | 5 Hz | Raw RGB8 camera frame (144×108), in `<frame_id>_camera_optical` |
| `/vector/touch` | `std_msgs/Bool` | 5 Hz | Capacitive back-touch sensor; skipped when the reading is unavailable |

### Example: monitor status

```bash
ros2 topic echo /vector/status
```

```json
{"status": "ok", "battery_level": 3, "is_charging": false, "is_on_charger": false, ...}
```

---

## Topics Subscribed (Commands)

| Topic | Type | Description |
|---|---|---|
| `/vector/cmd_vel` | `geometry_msgs/Twist` | `linear.x` → forward velocity in m/s · `angular.z` → yaw rate in rad/s (zero Twist stops the robot) |
| `/vector/cmd_say` | `std_msgs/String` | Robot speaks the `data` string |
| `/vector/cmd_head` | `std_msgs/Float32` | Set head angle in degrees (−22 to 45) |
| `/vector/cmd_lift` | `std_msgs/Float32` | Set lift height (0.0 = low, 1.0 = high) |
| `/vector/cmd_animate` | `std_msgs/String` | Play animation by name |

### Example: drive forward at 0.1 m/s

```bash
ros2 topic pub --rate 5 /vector/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.1, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

### Example: make Vector speak

```bash
ros2 topic pub --once /vector/cmd_say std_msgs/msg/String "data: 'Hello from ROS2'"
```

### Example: turn left at ~0.5 rad/s

```bash
ros2 topic pub --rate 5 /vector/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

### Example: stop

```bash
ros2 topic pub --once /vector/cmd_vel geometry_msgs/msg/Twist "{}"
```

---

## Services

| Service | Type | Description |
|---|---|---|
| `/vector/emergency_stop` | `std_srvs/Trigger` | Stop all motors immediately |
| `/vector/drive_off_charger` | `std_srvs/Trigger` | Drive off charger |

### Example: emergency stop

```bash
ros2 service call /vector/emergency_stop std_srvs/srv/Trigger
```

---

## Viewing the Camera in rviz2

1. Launch rviz2: `rviz2`
2. Add → **By topic** → `/vector/camera` → **Image**
3. The live robot camera feed will appear in rviz2.

> The camera topic uses `sensor_msgs/Image` (encoding: `rgb8`), compatible
> with any standard ROS2 image viewer or `cv_bridge` pipeline.

---

## `cmd_vel` Mapping Notes

`/vector/cmd_vel` uses SI units: `linear.x` in m/s and `angular.z` in rad/s.
The Vector SDK only offers blocking, distance-based drive calls, so the node
converts the **latest** command to mm/s and deg/s and executes short (0.25 s)
drive steps for as long as commands keep arriving. If no new `cmd_vel` arrives
within 0.5 s, motion stops, so publish at ≥ 5 Hz (as teleop / Nav2 do).
A zero Twist, `/vector/emergency_stop`, or node shutdown immediately stops the
robot and discards any queued or in-progress motion. Forward speed is clamped
to 10–200 mm/s. When both linear and angular components are set, each step
drives and then turns (an approximation of an arc). `linear.y` is ignored.

---

## Integration with the MCP Server

The ROS2 bridge and MCP server are fully independent — they can run
simultaneously, both connecting to the robot. The robot SDK allows only one
active connection at a time, so **do not run both at once against the same
robot** unless you add connection-sharing logic.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Cannot import vectorclaw_mcp` | `pip install vectorclaw-mcp` in the same venv that colcon uses |
| `VECTOR_SERIAL not set` | `export VECTOR_SERIAL=your-serial` before running the node |
| Topics publish but robot doesn't move | Robot may still be on charger — call `/vector/drive_off_charger` first |
| Camera topic missing | Check `camera_enabled:=true` parameter; also ensure Wire-Pod is running |
