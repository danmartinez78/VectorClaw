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
| `frame_id` | `"vector"` | TF `frame_id` used in all stamped messages |

---

## Topics Published

| Topic | Type | Rate | Description |
|---|---|---|---|
| `/vector/status` | `std_msgs/String` | 1 Hz | JSON with battery, charging, cliff, carried, picked-up state |
| `/vector/pose` | `geometry_msgs/PoseStamped` | 1 Hz | Position (mm) and yaw as quaternion |
| `/vector/proximity` | `sensor_msgs/Range` | 5 Hz | Front IR sensor (range in **meters**) |
| `/vector/camera` | `sensor_msgs/Image` | 5 Hz | Raw RGB8 camera frame (144×108) |
| `/vector/touch` | `std_msgs/Bool` | 5 Hz | Capacitive back-touch sensor |

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
| `/vector/cmd_vel` | `geometry_msgs/Twist` | `linear.x` → forward mm/s · `angular.z` → turn deg/s |
| `/vector/cmd_say` | `std_msgs/String` | Robot speaks the `data` string |
| `/vector/cmd_head` | `std_msgs/Float32` | Set head angle in degrees (−22 to 45) |
| `/vector/cmd_lift` | `std_msgs/Float32` | Set lift height (0.0 = low, 1.0 = high) |
| `/vector/cmd_animate` | `std_msgs/String` | Play animation by name |

### Example: drive forward 200 mm

```bash
ros2 topic pub --once /vector/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 200.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

### Example: make Vector speak

```bash
ros2 topic pub --once /vector/cmd_say std_msgs/msg/String "data: 'Hello from ROS2'"
```

### Example: turn 90 degrees left

```bash
ros2 topic pub --once /vector/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 90.0}}"
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

The `/vector/cmd_vel` topic uses `geometry_msgs/Twist`. Because Vector's SDK
uses **one-shot** drive commands (not continuous velocity), the mapping is:

- `linear.x` → `distance_mm` (mm to drive forward in one command)
- `angular.z` → `angle_deg` (degrees to turn in one command)

For **continuous navigation** (e.g. Nav2 or a joystick teleop), publish at
your control rate — the node will issue repeated drive commands. Keep `linear.x`
values small (e.g. 50–100 mm per command at 5 Hz) for smooth motion.

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
