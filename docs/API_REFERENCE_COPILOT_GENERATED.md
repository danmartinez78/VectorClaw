# Wirepod Vector Python SDK — Comprehensive API Reference

> **SDK Version:** 0.8.1  
> **Protocol:** gRPC over TLS (protobuf)  
> **Python:** 3.6+

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Getting Started](#2-getting-started)
3. [Robot — Entry Point](#3-robot--entry-point)
4. [Connection & Control System](#4-connection--control-system)
5. [Behavior — Movement & Actions](#5-behavior--movement--actions)
6. [Animation](#6-animation)
7. [Motors — Low-Level Control](#7-motors--low-level-control)
8. [Camera & Vision](#8-camera--vision)
9. [Screen — Face Display](#9-screen--face-display)
10. [Audio](#10-audio)
11. [Coordinate System, Pose & Spatial Math](#11-coordinate-system-pose--spatial-math)
12. [World Model & Object Detection](#12-world-model--object-detection)
13. [Custom Objects & Markers](#13-custom-objects--markers)
14. [Navigation Map](#14-navigation-map)
15. [Face Recognition](#15-face-recognition)
16. [Proximity Sensor](#16-proximity-sensor)
17. [Touch Sensor](#17-touch-sensor)
18. [Photos](#18-photos)
19. [Events System](#19-events-system)
20. [User Intent (Voice Commands)](#20-user-intent-voice-commands)
21. [Status Flags](#21-status-flags)
22. [Image Annotation](#22-image-annotation)
23. [Viewers (2D & 3D)](#23-viewers-2d--3d)
24. [Lights & Colors](#24-lights--colors)
25. [Utilities](#25-utilities)
26. [Exceptions](#26-exceptions)
27. [Async API](#27-async-api)

---

## 1. Architecture Overview

The SDK is structured as a component-based system centered on the `Robot` class. Each functional domain (camera, motors, behavior, etc.) is encapsulated in a `Component` subclass that holds a back-reference to the robot and its gRPC connection.

```
┌──────────────────────────────────────────────────┐
│                    Robot                         │
│                                                  │
│  ┌─────────┐  ┌──────────┐  ┌────────────────┐  │
│  │Connection│  │EventHandler│ │  World Model  │  │
│  │ (gRPC)  │  │(pub/sub) │  │(faces,objects) │  │
│  └────┬────┘  └─────┬────┘  └───────┬────────┘  │
│       │             │               │            │
│  ┌────┴─────────────┴───────────────┴─────────┐  │
│  │              Components                    │  │
│  │  Behavior · Animation · Motors · Camera    │  │
│  │  Vision · Audio · Screen · NavMap · Photos │  │
│  │  Proximity · Touch · Faces · Viewer        │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
         │
         │ gRPC / TLS
         ▼
   ┌───────────┐
   │  Vector   │
   │  Robot    │
   └───────────┘
```

**Communication flow:** The SDK connects to the robot via gRPC over TLS. A persistent event stream delivers robot state updates, observed object/face data, and sensor readings. Commands are sent as individual RPCs.

**Threading model:** The `Connection` owns a dedicated asyncio event loop running on a background thread. All gRPC calls execute on that thread. The synchronous `Robot` class transparently marshals calls between the caller's thread and the connection thread via `concurrent.futures.Future`.

---

## 2. Getting Started

### Minimal Example

```python
import anki_vector

with anki_vector.Robot() as robot:
    robot.behavior.say_text("Hello World!")
```

### Prerequisites

1. Run `python3 -m anki_vector.configure` (or `configure_pod` for wirepod) to set up authentication.  
2. This creates a config file at `~/.anki_vector/sdk_config.ini` containing the robot's name, IP, certificate path, and auth GUID.

### Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `serial` | `str` | `None` | Robot serial number (underside of Vector). Selects config section. |
| `ip` | `str` | `None` | Override IP address (otherwise read from config). |
| `name` | `str` | `None` | Robot name (e.g. `"Vector-A1B2"`) for mDNS discovery. |
| `config` | `dict` | `None` | Override config values: `cert`, `name`, `guid`, `port`. |
| `default_logging` | `bool` | `True` | Set up SDK logging to stderr. |
| `behavior_activation_timeout` | `int` | `10` | Seconds to wait for behavior control. |
| `cache_animation_lists` | `bool` | `False` | Pre-load animation lists on connect. |
| `enable_face_detection` | `bool` | `False` | Start face detection on connect. |
| `estimate_facial_expression` | `bool` | `False` | Enable expression estimation (reduces face event frequency). |
| `enable_audio_feed` | `bool` | `False` | Start audio feed on connect. |
| `enable_custom_object_detection` | `bool` | `False` | Start custom object detection on connect. |
| `enable_nav_map_feed` | `bool` | `None` | Start nav map updates on connect (auto-enabled with 3D viewer). |
| `show_viewer` | `bool` | `False` | Open the 2D camera viewer window. |
| `show_3d_viewer` | `bool` | `False` | Open the 3D world viewer window. |
| `behavior_control_level` | `ControlPriorityLevel` | `DEFAULT_PRIORITY` | Control priority. `None` = no control. |

---

## 3. Robot — Entry Point

**Module:** `anki_vector.robot`

### `Robot`

The main synchronous interface. All component methods block until complete and return results directly.

**Context manager usage (recommended):**
```python
with anki_vector.Robot() as robot:
    robot.behavior.drive_straight(distance_mm(100), speed_mmps(50))
```

**Manual connection:**
```python
robot = anki_vector.Robot()
robot.connect()
# ... use robot ...
robot.disconnect()
```

#### Methods

| Method | Returns | Description |
|---|---|---|
| `connect(timeout=10)` | — | Opens gRPC connection, starts event stream, initializes components. |
| `disconnect()` | — | Closes connection and cleans up all components. |
| `get_battery_state()` | `BatteryStateResponse` | Battery level, voltage, charging state, and charger status. |
| `get_version_state()` | `VersionStateResponse` | OS version and engine build ID. |

#### Live State Properties

These are updated continuously via the robot state event stream:

| Property | Type | Description |
|---|---|---|
| `pose` | `Pose` | Current position and orientation in the world. |
| `pose_angle_rad` | `float` | Heading angle in the X-Y plane (radians). |
| `pose_pitch_rad` | `float` | Pitch angle (radians). |
| `left_wheel_speed_mmps` | `float` | Left wheel speed (mm/s). |
| `right_wheel_speed_mmps` | `float` | Right wheel speed (mm/s). |
| `head_angle_rad` | `float` | Head motor angle (radians). |
| `lift_height_mm` | `float` | Lift height from ground (mm). |
| `accel` | `Vector3` | Accelerometer reading (x, y, z). |
| `gyro` | `Vector3` | Gyroscope reading (x, y, z). |
| `carrying_object_id` | `int` | ID of carried object (-1 if none). |
| `head_tracking_object_id` | `int` | ID of object being tracked (-1 if none). |
| `localized_to_object_id` | `int` | ID of object used for localization (-1 if none). |
| `last_image_time_stamp` | `int` | Timestamp of the last camera image. |
| `status` | `RobotStatus` | Bitfield of status flags (see [Status Flags](#21-status-flags)). |

#### Component Accessors

| Property | Type | Description |
|---|---|---|
| `conn` | `Connection` | The active gRPC connection. |
| `events` | `EventHandler` | Event subscription manager. |
| `anim` | `AnimationComponent` | Play animations and triggers. |
| `audio` | `AudioComponent` | Speaker and microphone control. |
| `behavior` | `BehaviorComponent` | High-level actions (drive, turn, say, etc.). |
| `camera` | `CameraComponent` | Camera feed and settings. |
| `faces` | `FaceComponent` | Face enrollment management. |
| `motors` | `MotorComponent` | Direct motor control. |
| `nav_map` | `NavMapComponent` | Navigation memory map. |
| `screen` | `ScreenComponent` | Face screen display. |
| `photos` | `PhotographComponent` | Access stored photos. |
| `proximity` | `ProximityComponent` | Time-of-flight distance sensor. |
| `touch` | `TouchComponent` | Capacitive touch sensor on back. |
| `viewer` | `ViewerComponent` | 2D camera viewer window. |
| `viewer_3d` | `Viewer3DComponent` | 3D world viewer window. |
| `vision` | `VisionComponent` | Vision mode toggles. |
| `world` | `World` | World model (all known objects and faces). |

---

## 4. Connection & Control System

**Module:** `anki_vector.connection`

### Behavior Control

Vector has an internal behavior system that autonomously controls the robot (exploring, reacting to stimuli, etc.). The SDK must request *control* to command Vector. Without control, most movement and action commands will fail.

#### `ControlPriorityLevel` (Enum)

| Value | Description |
|---|---|
| `DEFAULT_PRIORITY` | Standard control level. Runs below mandatory physical reactions (e.g. fall protection) but above trigger-word detection. **Default for normal use.** |
| `OVERRIDE_BEHAVIORS_PRIORITY` | Highest priority. Overrides even physical reactions — Vector will drive off tables, ignore low battery, work in darkness. **Use with caution.** |
| `RESERVE_CONTROL` | Holds control before/after other SDK connections. Disables idle behaviors. Not for regular behavior control. |

#### Connection Lifecycle

```python
# Control is requested automatically in the Robot context manager.
# To operate without control (e.g. just observing):
robot = anki_vector.Robot(behavior_control_level=None)
robot.connect()
# Can still read state and sensor data, but cannot command movement.
```

#### Manual Control Request/Release

```python
# Temporarily release control so Vector can act autonomously:
robot.conn.release_control()

# Re-request control:
robot.conn.request_control()
```

### `Connection`

| Method | Description |
|---|---|
| `connect(timeout=10)` | Establish gRPC channel and authenticate. |
| `close()` | terminate the connection and clean up. |
| `request_control(behavior_control_level, timeout=10)` | Request behavior control at the given priority. |
| `release_control(timeout=10)` | Release behavior control back to the robot. |
| `run_coroutine(coro)` | Run an async coroutine on the connection thread. Returns result. |
| `run_soon(coro)` | Schedule a coroutine on the connection thread (fire-and-forget). |

| Property | Type | Description |
|---|---|---|
| `loop` | `asyncio.BaseEventLoop` | The connection's event loop. |
| `thread` | `threading.Thread` | The connection's background thread. |
| `grpc_interface` | `ExternalInterfaceStub` | Raw gRPC stub for direct protobuf calls. |
| `requires_behavior_control` | `bool` | Whether control was requested. |
| `control_granted_event` | `asyncio.Event` | Set when control is acquired. |
| `control_lost_event` | `asyncio.Event` | Set when control is lost (higher priority behavior). |

### `@on_connection_thread` Decorator

Internal decorator used on component methods to ensure they run on the connection's asyncio thread. Key parameters:

| Parameter | Default | Description |
|---|---|---|
| `log_messaging` | `True` | Log the gRPC request/response. |
| `requires_control` | `True` | Raise `VectorControlException` if behavior control is not held. |
| `is_cancellable` | `None` | Whether the action can be cancelled (`CANCELLABLE_ACTION` or `CANCELLABLE_BEHAVIOR`). |

---

## 5. Behavior — Movement & Actions

**Module:** `anki_vector.behavior`

The `BehaviorComponent` provides high-level robot actions. All methods require behavior control (they are decorated with `@on_connection_thread(requires_control=True)` unless noted).

### Physical Limits

| Constant | Value | Description |
|---|---|---|
| `MIN_HEAD_ANGLE` | -22.0° | Minimum head angle (looking down). |
| `MAX_HEAD_ANGLE` | 45.0° | Maximum head angle (looking up). |
| `MIN_LIFT_HEIGHT_MM` | 32.0 mm | Lowest lift position. |
| `MAX_LIFT_HEIGHT_MM` | 92.0 mm | Highest lift position. |

### Movement Methods

#### `drive_straight(distance, speed, should_play_anim=True, num_retries=0)`

Drives Vector in a straight line.

| Parameter | Type | Description |
|---|---|---|
| `distance` | `Distance` | How far to drive. Positive = forward, negative = backward. |
| `speed` | `Speed` | Driving speed in mm/s. |
| `should_play_anim` | `bool` | Play driving animation. |
| `num_retries` | `int` | Number of retry attempts. |

```python
from anki_vector.util import distance_mm, speed_mmps
robot.behavior.drive_straight(distance_mm(200), speed_mmps(100))
```

#### `turn_in_place(angle, speed=0, accel=0, angle_tolerance=0, is_absolute=False, num_retries=0)`

Turns Vector in place.

| Parameter | Type | Description |
|---|---|---|
| `angle` | `Angle` | Amount to turn. Positive = counter-clockwise (left), negative = clockwise (right). |
| `speed` | `Angle` | Angular speed (0 = default). |
| `accel` | `Angle` | Angular acceleration (0 = default). |
| `angle_tolerance` | `Angle` | Acceptable error margin. |
| `is_absolute` | `bool` | If `True`, turn to absolute angle rather than relative. |

```python
from anki_vector.util import degrees
robot.behavior.turn_in_place(degrees(90))   # turn left 90°
robot.behavior.turn_in_place(degrees(-45))  # turn right 45°
```

#### `go_to_pose(pose, relative_to_robot=False, num_retries=0)`

Drives Vector to an absolute pose in the world.

| Parameter | Type | Description |
|---|---|---|
| `pose` | `Pose` | Target position and orientation. |
| `relative_to_robot` | `bool` | If `True`, `pose` is relative to Vector's current position. |

```python
from anki_vector.util import Pose, degrees
# Drive 50mm forward from current position:
robot.behavior.go_to_pose(Pose(x=50, y=0, z=0, angle_z=degrees(0)), relative_to_robot=True)
```

#### `go_to_object(target_object, distance_from_object, num_retries=0)`

Drives Vector to a position near an observed object.

| Parameter | Type | Description |
|---|---|---|
| `target_object` | `LightCube` | The object to approach. |
| `distance_from_object` | `Distance` | Desired standoff distance from the object. |

### Head & Lift

#### `set_head_angle(angle, accel=10.0, max_speed=10.0, duration=0.0, num_retries=0)`

| Parameter | Type | Description |
|---|---|---|
| `angle` | `Angle` | Target head angle. Clamped to [-22°, 45°]. |
| `accel` | `float` | Acceleration (rad/s²). |
| `max_speed` | `float` | Maximum speed (rad/s). |

```python
robot.behavior.set_head_angle(degrees(20))  # look slightly up
```

#### `set_lift_height(height, accel=10.0, max_speed=10.0, duration=0.0, num_retries=0)`

| Parameter | Type | Description |
|---|---|---|
| `height` | `float` | Fraction of max lift height: 0.0 (lowest) to 1.0 (highest). |

```python
robot.behavior.set_lift_height(0.0)  # lower lift
robot.behavior.set_lift_height(1.0)  # raise lift fully
```

### Speech

#### `say_text(text, use_vector_voice=True, duration_scalar=1.0)`

Makes Vector speak the given text using text-to-speech.

| Parameter | Type | Description |
|---|---|---|
| `text` | `str` | The text to speak. |
| `use_vector_voice` | `bool` | Use Vector's characteristic voice processing. |
| `duration_scalar` | `float` | Speed multiplier (1.0 = normal, <1.0 faster, >1.0 slower). |

```python
robot.behavior.say_text("I am Vector!")
```

### Cube Interactions

| Method | Description |
|---|---|
| `dock_with_cube(target_object, approach_angle=None, alignment_type=..., distance_from_marker=None, num_retries=0)` | Drive to and dock with the cube. |
| `roll_cube(target_object, approach_angle=None, num_retries=0)` | Drive to the cube and roll it. |
| `pickup_object(target_object, use_pre_dock_pose=True, num_retries=0)` | Pick up the cube. |
| `pop_a_wheelie(target_object, approach_angle=None, num_retries=0)` | Use the cube to pop a wheelie. |
| `roll_visible_cube()` | Find and roll a visible cube. |

### Charger

| Method | Description |
|---|---|
| `drive_off_charger()` | Drive off the charger. |
| `drive_on_charger()` | Drive onto the charger. |

### Face Interaction

| Method | Description |
|---|---|
| `find_faces()` | Actively look for faces. |
| `look_around_in_place()` | Look around without moving. |
| `turn_towards_face(face, num_retries=0)` | Turn to face a detected `Face` instance. |

### Appearance

#### `set_eye_color(hue, saturation)`

Changes Vector's eye color.

| Parameter | Type | Description |
|---|---|---|
| `hue` | `float` | Color hue (0.0 – 1.0). |
| `saturation` | `float` | Color saturation (0.0 – 1.0). |

```python
robot.behavior.set_eye_color(0.05, 0.95)  # orange eyes
```

### Settings

| Method | Description |
|---|---|
| `app_intent(intent, param=None)` | Send an app intent command. |
| `change_locale(locale)` | Change the robot's locale (e.g. `"en_US"`). |
| `update_settings(settings)` | Update robot settings with a dict. |

---

## 6. Animation

**Module:** `anki_vector.animation`

### `AnimationComponent`

Vector has a library of built-in animations (body movements, sounds, screen images).

#### Properties

| Property | Type | Description |
|---|---|---|
| `anim_list` | `list[str]` | Available animation names (populated after `load_animation_list()`). |
| `anim_trigger_list` | `list[str]` | Available animation trigger names. |

#### Methods

| Method | Description |
|---|---|
| `load_animation_list()` | Fetch available animations from the robot. |
| `load_animation_trigger_list()` | Fetch available animation triggers from the robot. |
| `play_animation(anim, loop_count=1, ignore_body_track=False, ignore_head_track=False, ignore_lift_track=False)` | Play a named animation. |
| `play_animation_trigger(anim_trigger, loop_count=1, use_lift_safe=False, ignore_body_track=False, ignore_head_track=False, ignore_lift_track=False)` | Play an animation trigger (robot picks a suitable animation from the group). |

**Track flags:** The `ignore_*_track` parameters let you prevent an animation from controlling specific motors, useful for composing animations with manual motor control.

```python
# List and play animations
robot.anim.load_animation_trigger_list()
for trigger in robot.anim.anim_trigger_list:
    print(trigger)

robot.anim.play_animation_trigger("GreetAfterLongTime")
robot.anim.play_animation("anim_pounce_success_02")
```

---

## 7. Motors — Low-Level Control

**Module:** `anki_vector.motors`

### `MotorComponent`

Direct motor control for when you need frame-by-frame movement commands (e.g. joystick control, custom path following).

| Method | Description |
|---|---|
| `set_wheel_motors(left_wheel_speed, right_wheel_speed, left_wheel_accel=0.0, right_wheel_accel=0.0)` | Set individual wheel speeds in mm/s. Acceleration in mm/s². |
| `set_head_motor(speed)` | Set head motor speed in rad/s. |
| `set_lift_motor(speed)` | Set lift motor speed in rad/s. |
| `stop_all_motors()` | Immediately stop all motors. |

**Differential drive:** Vector uses two independently driven wheels. Setting different speeds creates turning:

```python
# Drive forward
robot.motors.set_wheel_motors(100, 100)

# Spin in place (clockwise)
robot.motors.set_wheel_motors(50, -50)

# Gentle left curve
robot.motors.set_wheel_motors(100, 50)

# Stop
robot.motors.stop_all_motors()
```

---

## 8. Camera & Vision

### Camera

**Module:** `anki_vector.camera`

#### `CameraComponent`

| Method | Description |
|---|---|
| `init_camera_feed()` | Start receiving camera images from Vector. |
| `close_camera_feed()` | Stop the camera feed. |
| `capture_single_image(enable_high_resolution=False)` | Capture one image without starting the persistent feed. Returns `CameraImage`. |
| `enable_auto_exposure(enable=True)` | Toggle auto-exposure. |
| `set_manual_exposure(exposure_ms, gain)` | Set manual exposure time and gain within `CameraConfig` limits. |
| `get_camera_config()` | Retrieve camera calibration/configuration data. |

| Property | Type | Description |
|---|---|---|
| `latest_image` | `CameraImage` | Most recent camera frame. |
| `latest_image_id` | `int` | ID of the most recent frame. |
| `config` | `CameraConfig` | Camera calibration data. |
| `image_annotator` | `ImageAnnotator` | Annotation engine for drawing on images. |
| `is_auto_exposure_enabled` | `bool` | Current auto-exposure state. |
| `gain` | `float` | Current sensor gain. |
| `exposure_ms` | `int` | Current exposure time in milliseconds. |

#### `CameraImage`

| Property | Type | Description |
|---|---|---|
| `raw_image` | `PIL.Image.Image` | The raw image as a Pillow Image object. |
| `image_id` | `int` | Unique identifier for this image. |
| `image_recv_time` | `float` | Time the image was received. |

| Method | Description |
|---|---|
| `annotate_image(scale=None, fit_size=None, resample_mode=NEAREST)` | Returns a copy of the image with annotations (detected faces, objects) drawn on it. |

#### `CameraConfig`

Camera intrinsic parameters used for image-space to world-space projection:

| Property | Type | Description |
|---|---|---|
| `focal_length` | `Vector2` | Focal length in pixels (fx, fy). |
| `center` | `Vector2` | Principal point / optical center in pixels (cx, cy). |
| `fov_x` | `Angle` | Horizontal field of view. |
| `fov_y` | `Angle` | Vertical field of view. |
| `min_gain` / `max_gain` | `float` | Sensor gain range. |
| `min_exposure_time_ms` / `max_exposure_time_ms` | `int` | Exposure range. |

```python
robot.camera.init_camera_feed()
import time; time.sleep(1)
image = robot.camera.latest_image
image.raw_image.save("vector_photo.png")
```

### Vision

**Module:** `anki_vector.vision`

#### `VisionComponent`

Controls what Vector's vision system looks for. These modes can be toggled independently. **Disabling unneeded modes reduces CPU load on the robot.**

| Method | Description |
|---|---|
| `enable_face_detection(detect_faces=True, estimate_expression=False)` | Toggle face detection. Expression estimation adds eye, nose, mouth landmarks but reduces frame rate. |
| `enable_custom_object_detection(detect_custom_objects=True)` | Toggle detection of user-defined custom objects (see [Custom Objects](#13-custom-objects--markers)). |
| `enable_motion_detection(detect_motion=True)` | Toggle motion detection — fires `robot_observed_motion` events. |
| `enable_display_camera_feed_on_face(enable=True)` | Mirror mode — displays the camera feed on Vector's face screen. |
| `disable_all_vision_modes()` | Turn off all vision processing. |

| Property | Type | Description |
|---|---|---|
| `detect_faces` | `bool` | Whether face detection is active. |
| `detect_custom_objects` | `bool` | Whether custom object detection is active. |
| `detect_motion` | `bool` | Whether motion detection is active. |
| `display_camera_feed_on_face` | `bool` | Whether mirror mode is active. |

**How object detection works:** Vector uses a marker-based detection system. The robot's camera feed is analyzed for known visual markers (fiducial patterns). When a marker is seen, the robot uses the known physical size of the marker and the camera's intrinsic parameters (`CameraConfig.focal_length`, `CameraConfig.center`) to compute the marker's 3D pose via a Perspective-n-Point (PnP) algorithm. The detected pose is expressed in Vector's world coordinate frame (see [Coordinate System](#11-coordinate-system-pose--spatial-math)).

---

## 9. Screen — Face Display

**Module:** `anki_vector.screen`

Vector's face is a 184×96 pixel color LCD screen. You can display custom images or solid colors.

### Constants

| Constant | Value |
|---|---|
| `SCREEN_WIDTH` | 184 |
| `SCREEN_HEIGHT` | 96 |

### Functions

| Function | Description |
|---|---|
| `dimensions()` | Returns `(184, 96)`. |
| `convert_image_to_screen_data(pil_image)` | Converts a Pillow Image to Vector's screen data format (RGB565). |
| `convert_pixels_to_screen_data(pixel_data, width, height)` | Convert raw pixel data (list of RGB tuples) to screen data. |

### `ScreenComponent`

| Method | Description |
|---|---|
| `set_screen_with_image_data(image_data, duration_sec, interrupt_running=True)` | Display an image on Vector's face. `image_data` must be bytes from `convert_image_to_screen_data()`. |
| `set_screen_to_color(solid_color, duration_sec, interrupt_running=True)` | Fill the screen with a solid `Color`. |

```python
from PIL import Image
from anki_vector.screen import convert_image_to_screen_data, SCREEN_WIDTH, SCREEN_HEIGHT

image = Image.open("my_image.png").resize((SCREEN_WIDTH, SCREEN_HEIGHT))
screen_data = convert_image_to_screen_data(image)
robot.screen.set_screen_with_image_data(screen_data, 5.0)
```

---

## 10. Audio

**Module:** `anki_vector.audio`

### `RobotVolumeLevel` (Enum)

| Value | Description |
|---|---|
| `LOW` | Quietest setting. |
| `MEDIUM_LOW` | Below-average volume. |
| `MEDIUM` | Default volume. |
| `MEDIUM_HIGH` | Above-average volume. |
| `HIGH` | Loudest setting. |

### `AudioComponent`

| Method | Description |
|---|---|
| `set_master_volume(volume)` | Set the speaker volume. `volume` is a `RobotVolumeLevel`. |
| `stream_wav_file(filename, volume=50)` | Stream a WAV file to Vector's speaker. File must be 16-bit PCM, and is chunked at 1024 bytes per gRPC message. |

### Constants

| Constant | Value | Description |
|---|---|---|
| `MAX_ROBOT_AUDIO_CHUNK_SIZE` | 1024 | Maximum bytes per audio stream chunk. |
| `DEFAULT_FRAME_SIZE` | 512 | Default audio frame size. |

```python
from anki_vector.audio import RobotVolumeLevel
robot.audio.set_master_volume(RobotVolumeLevel.MEDIUM_HIGH)
robot.audio.stream_wav_file("notification.wav")
```

---

## 11. Coordinate System, Pose & Spatial Math

**Module:** `anki_vector.util`

### Coordinate Frame Conventions

Vector uses a **right-handed coordinate system** with the origin at the ground point between Vector's two front wheels **at the time of localization**:

```
        Z (up)
        │
        │   X (forward)
        │  ╱
        │ ╱
        │╱
        └──────── Y (left)
```

- **X axis:** Vector's forward direction.
- **Y axis:** Vector's left direction.
- **Z axis:** Up.
- **Units:** All positions are in **millimeters (mm)**.
- **Angles:** Counter-clockwise rotation around Z is positive (following the right-hand rule).
- **Rotation convention:** Quaternions use the Hamilton convention `(w, x, y, z)` = `(q0, q1, q2, q3)`.

### Origin ID and Delocalization

Every `Pose` carries an `origin_id` integer. This ID represents which coordinate frame the pose belongs to.

**When Vector is delocalized** (picked up, kidnapped, or loses track of where he is), he creates a new origin with a new `origin_id` and resets his pose to `(0, 0, 0)`. After delocalization, all previously recorded poses (e.g. the cube's pose, the charger's pose) will have a stale `origin_id` and **cannot be meaningfully compared** with the robot's new pose.

```python
# Check if two poses are in the same coordinate frame:
if robot.pose.is_comparable(cube.pose):
    # Safe to compute relative positions
    pass
```

### `Pose`

Represents a position and orientation in 3D space.

```python
Pose(x, y, z, q0=None, q1=None, q2=None, q3=None, angle_z=None, origin_id=-1)
```

**Construction:** Provide either `(q0, q1, q2, q3)` for full quaternion rotation, or `angle_z` for a simple rotation around the Z axis (most common for ground robots).

| Property | Type | Description |
|---|---|---|
| `position` | `Position` | 3D position (x, y, z) in mm. |
| `rotation` | `Quaternion` | Rotation as a quaternion. |
| `origin_id` | `int` | Coordinate frame ID. |
| `is_valid` | `bool` | `True` if `origin_id >= 0`. |

| Method | Returns | Description |
|---|---|---|
| `define_pose_relative_this(new_pose)` | `Pose` | Transforms `new_pose` so that `self` is treated as the origin. This applies a rigid body transformation: rotates `new_pose.position` by `self.rotation.angle_z`, translates by `self.position`, and sums the Z-rotation angles. The result inherits `self.origin_id`. |
| `is_comparable(other_pose)` | `bool` | Returns `True` if both poses are valid and share the same `origin_id`. |
| `to_matrix()` | `Matrix44` | Converts this pose to a 4×4 homogeneous transformation matrix. |
| `to_proto_pose_struct()` | `PoseStruct` | Serializes to protobuf format (internal use). |

**Relative pose math in detail:**

`define_pose_relative_this(new_pose)` performs a 2D rigid body transformation (rotation + translation). Given:
- `self` at position $(x_s, y_s, z_s)$ with heading $\theta_s$
- `new_pose` at position $(x_n, y_n, z_n)$ with heading $\theta_n$

The result is:

$$x_r = x_s + x_n \cos(\theta_s) - y_n \sin(\theta_s)$$
$$y_r = y_s + x_n \sin(\theta_s) + y_n \cos(\theta_s)$$
$$z_r = z_s + z_n$$
$$\theta_r = \theta_s + \theta_n$$

This is equivalent to computing the position of `new_pose` in the world frame, given that `new_pose` was specified in the local frame of `self`.

### `Position` (extends `Vector3`)

A 3D position in millimeters. Same interface as `Vector3` but semantically represents a world position.

### `Quaternion`

Represents a 3D rotation. Internally stored as $(q_0, q_1, q_2, q_3)$ where $q_0$ is the scalar (real/w) component and $(q_1, q_2, q_3)$ are the vector (imaginary/x,y,z) components.

```python
Quaternion(q0=None, q1=None, q2=None, q3=None, angle_z=None)
```

| Property | Type | Description |
|---|---|---|
| `q0` | `float` | Scalar / w component. |
| `q1` | `float` | x component. |
| `q2` | `float` | y component. |
| `q3` | `float` | z component. |
| `angle_z` | `Angle` | Euler angle Z-axis rotation extracted from the quaternion: $\theta_z = \text{atan2}(2(q_1 q_2 + q_0 q_3),\ 1 - 2(q_2^2 + q_3^2))$ |
| `q0_q1_q2_q3` | `tuple` | All four components. |

| Method | Returns | Description |
|---|---|---|
| `to_matrix(pos_x=0, pos_y=0, pos_z=0)` | `Matrix44` | Convert to a 4×4 rotation/translation matrix using the standard quaternion-to-rotation-matrix formula. |

**Quaternion to rotation matrix:** The `to_matrix` method uses the standard conversion:

$$R = \begin{bmatrix}
q_0^2+q_1^2-q_2^2-q_3^2 & 2(q_1q_2+q_0q_3) & 2(q_1q_3-q_0q_2) \\
2(q_1q_2-q_0q_3) & q_0^2-q_1^2+q_2^2-q_3^2 & 2(q_0q_1+q_2q_3) \\
2(q_0q_2+q_1q_3) & 2(q_2q_3-q_0q_1) & q_0^2-q_1^2-q_2^2+q_3^2
\end{bmatrix}$$

### `angle_z_to_quaternion(angle_z)`

Converts a Z-axis Euler angle to a quaternion. Since only the Z rotation is specified (X and Y Euler angles are 0):

$$q_0 = \cos(\theta_z / 2), \quad q_1 = 0, \quad q_2 = 0, \quad q_3 = \sin(\theta_z / 2)$$

### `Matrix44`

A 4×4 homogeneous transformation matrix. Stored in column-major layout with elements `m00`–`m33`.

```
┌                         ┐
│ m00  m01  m02  m03      │   Row 0: forward direction + tx
│ m10  m11  m12  m13      │   Row 1: left direction    + ty
│ m20  m21  m22  m23      │   Row 2: up direction      + tz
│ m30  m31  m32  m33      │   Row 3: position          + 1
└                         ┘
```

| Property | Returns | Description |
|---|---|---|
| `forward_xyz` | `(float, float, float)` | The forward (X) basis vector — row 0. |
| `left_xyz` | `(float, float, float)` | The left (Y) basis vector — row 1. |
| `up_xyz` | `(float, float, float)` | The up (Z) basis vector — row 2. |
| `pos_xyz` | `(float, float, float)` | The position vector — row 3. |
| `in_row_order` | `tuple[16 floats]` | Matrix elements in row-major order. |
| `in_column_order` | `tuple[16 floats]` | Matrix elements in column-major order. |

### `Angle`

Represents an angle with both degree and radian access.

```python
Angle(radians=None, degrees=None)  # provide exactly one
```

| Property | Type | Description |
|---|---|---|
| `radians` | `float` | The angle in radians. |
| `degrees` | `float` | The angle in degrees. |
| `abs_value` | `Angle` | Absolute value. |

Supports arithmetic (`+`, `-`, `*`, `/`) and comparison operators with other `Angle` instances.

**Convenience constructors:**
```python
from anki_vector.util import degrees, radians
a = degrees(90)     # Angle at 90°
b = radians(1.57)   # Angle at ~90°
```

### `Vector2` / `Vector3`

General-purpose 2D and 3D vector types.

| `Vector2` Property | Description |
|---|---|
| `x`, `y` | Components. |
| `x_y` | Tuple `(x, y)`. |

| `Vector3` Property | Description |
|---|---|
| `x`, `y`, `z` | Components. |
| `x_y_z` | Tuple `(x, y, z)`. |
| `magnitude` | Euclidean magnitude: $\sqrt{x^2 + y^2 + z^2}$ |
| `magnitude_squared` | $x^2 + y^2 + z^2$ |
| `normalized` | Unit vector in same direction. |

| `Vector3` Method | Description |
|---|---|
| `dot(other)` | Dot product. |
| `cross(other)` | Cross product. |

Both support arithmetic with matching types (`+`, `-`) and scalar multiplication/division (`*`, `/`).

### `Distance` / `Speed`

Type-safe wrappers for distance and speed values.

```python
from anki_vector.util import distance_mm, distance_inches, speed_mmps
d = distance_mm(100)        # 100 millimeters
d = distance_inches(3.94)   # ~100 millimeters
s = speed_mmps(50)           # 50 mm/s
```

| `Distance` Property | Description |
|---|---|
| `distance_mm` | Distance in millimeters. |
| `distance_inches` | Distance in inches (computed from mm). |

| `Speed` Property | Description |
|---|---|
| `speed_mmps` | Speed in millimeters per second. |

### `ImageRect`

Defines a bounding box in image coordinates  (used for reporting where objects/faces appear in camera frames).

| Property | Type | Description |
|---|---|---|
| `x_top_left` | `float` | Left edge of the bounding box (pixels). |
| `y_top_left` | `float` | Top edge of the bounding box (pixels). |
| `width` | `float` | Width (pixels). |
| `height` | `float` | Height (pixels). |

---

## 12. World Model & Object Detection

**Module:** `anki_vector.world`, `anki_vector.objects`

### The World Model

The `World` class maintains Vector's understanding of what's around him: faces, the light cube, the charger, and custom objects. It's automatically updated via event subscriptions as Vector observes things.

#### Properties

| Property | Type | Description |
|---|---|---|
| `all_objects` | generator | All tracked objects (cube, charger, custom objects). |
| `visible_faces` | generator of `Face` | Faces currently visible (seen within `FACE_VISIBILITY_TIMEOUT`). |
| `visible_objects` | generator of `ObservableObject` | Objects currently visible. |
| `visible_custom_objects` | generator of `CustomObject` | Custom objects currently visible. |
| `connected_light_cube` | `LightCube` or `None` | The cube if connected via BLE. |
| `light_cube` | `LightCube` or `None` | The cube object regardless of connection state (if observed). |
| `charger` | `Charger` or `None` | Most recently observed charger. |
| `custom_object_archetypes` | generator of `CustomObjectArchetype` | Defined custom object templates. |

#### Methods

| Method | Description |
|---|---|
| `connect_cube()` | Connect to Vector's light cube via BLE. |
| `disconnect_cube()` | Disconnect from the cube. |
| `flash_cube_lights()` | Play the default cube connection animation. |
| `forget_preferred_cube()` | Forget preferred cube — next connection will pick strongest signal. |
| `set_preferred_cube(factory_id)` | Set a preferred cube by hardware ID. |
| `get_object(object_id)` | Look up an object by its ID. |
| `get_face(face_id)` | Look up a face by its ID. |
| `define_custom_box(...)` | Define a custom box object (6 unique markers, dimensions). See [Custom Objects](#13-custom-objects--markers). |
| `define_custom_cube(...)` | Define a custom cube (1 marker on all sides, uniform size). |
| `define_custom_wall(...)` | Define a custom wall (1 marker, width × height, fixed 10mm depth). |
| `create_custom_fixed_object(pose, x_size_mm, y_size_mm, z_size_mm, relative_to_robot=False, use_robot_origin=True)` | Place an invisible obstacle in the world (stays fixed, never observed). |
| `delete_custom_objects(...)` | Remove custom object definitions and/or instances. |

### Object Detection Pipeline

1. **Marker Recognition:** Vector's on-board vision system continuously scans the camera feed for known visual markers (fiducial patterns). Three categories of markers exist:
   - **Built-in markers:** The LightCube's concentric-circle pattern and the charger's marker.
   - **Custom markers:** 16 printable marker designs (circles, diamonds, hexagons, triangles) for user-defined objects.

2. **Pose Estimation:** When a marker is detected, the robot uses the marker's known physical size (in mm) and the camera's intrinsic parameters to solve for the marker's 6-DOF pose (position + orientation) relative to the camera, then transforms it into the world coordinate frame.

3. **SDK Events:** The robot sends `robot_observed_object` events over gRPC. The SDK's `World` class receives these and:
   - Creates or updates `LightCube`, `Charger`, or `CustomObject` instances.
   - Updates each object's `pose`, `last_observed_time`, `image_rect`.
   - Dispatches `object_appeared` / `object_observed` / `object_disappeared` SDK events.

4. **Visibility Timeout:** An object is considered visible for `OBJECT_VISIBILITY_TIMEOUT` (0.8 seconds) after its last observation. If not re-observed within that window, an `object_disappeared` event fires and `is_visible` becomes `False`.

### `ObservableObject` (Base Class)

Base type for anything Vector can see. Inherited by `LightCube`, `Charger`, `CustomObject`.

| Property | Type | Description |
|---|---|---|
| `pose` | `Pose` | Object's position and orientation in the world frame. `None` if never observed. |
| `is_visible` | `bool` | `True` if observed within the last 0.8 seconds. |
| `last_observed_time` | `float` | SDK timestamp of last observation. |
| `last_observed_robot_timestamp` | `int` | Robot's internal timestamp of last observation. |
| `time_since_last_seen` | `float` | Seconds since last seen (`math.inf` if never). |
| `last_observed_image_rect` | `ImageRect` | Where in the camera frame the object was last seen. |
| `last_event_time` | `float` | Timestamp of last event (any type). |

### `LightCube`

Vector's physical cube with 4 corner LEDs, an accelerometer, and BLE connectivity.

**Additional properties beyond `ObservableObject`:**

| Property | Type | Description |
|---|---|---|
| `object_id` | `int` | Robot-assigned ID. |
| `factory_id` | `str` | Unique hardware serial number. |
| `is_connected` | `bool` | BLE connection active. |
| `is_moving` | `bool` | Cube accelerometer detects motion. |
| `up_axis` | `UpAxis` | Which axis is pointing up. |
| `top_face_orientation_rad` | `float` | Angular distance from the reported up axis. |
| `last_tapped_time` / `last_tapped_robot_timestamp` | `float` / `int` | Last tap event time. |
| `last_moved_time` / `last_moved_robot_timestamp` | `float` / `int` | Last movement end time. |
| `last_moved_start_time` / `last_moved_start_robot_timestamp` | `float` / `int` | Movement start time. |
| `last_up_axis_changed_time` / `last_up_axis_changed_robot_timestamp` | `float` / `int` | Last orientation change. |

**LED control methods:**

| Method | Description |
|---|---|
| `set_lights(light, color_profile=WHITE_BALANCED_CUBE_PROFILE)` | Set all 4 LEDs to the same light. |
| `set_light_corners(l1, l2, l3, l4, color_profile=...)` | Set each corner LED independently. |
| `set_lights_off(color_profile=...)` | Turn off all LEDs. |

### `Charger`

Vector's charging platform. Inherits from `ObservableObject` with no additional functionality beyond observation.

---

## 13. Custom Objects & Markers

Custom objects allow you to teach Vector to recognize printed markers and associate them with 3D shapes. Vector will then report their position and orientation when seen.

### Workflow

1. **Define the archetype** — tell Vector what shape and markers to expect:
   ```python
   robot.world.define_custom_cube(
       custom_object_type=CustomObjectTypes.CustomType00,
       marker=CustomObjectMarkers.Circles2,
       size_mm=50.0,
       marker_width_mm=40.0,
       marker_height_mm=40.0
   )
   ```

2. **Print and place markers** — print the marker images at the exact physical dimensions you specified.

3. **Enable detection:**
   ```python
   # Either via constructor:
   robot = anki_vector.Robot(enable_custom_object_detection=True)
   # Or at runtime:
   robot.vision.enable_custom_object_detection()
   ```

4. **Observe objects** — subscribe to events or poll `robot.world.visible_custom_objects`.

### `CustomObjectTypes` (16 slots)

`CustomType00` through `CustomType16` — each slot can hold exactly one archetype definition.

### `CustomObjectMarkers` (16 markers)

Printable fiducial marker patterns:

| Marker | Pattern |
|---|---|
| `Circles2` – `Circles5` | 2 to 5 concentric circles. |
| `Diamonds2` – `Diamonds5` | 2 to 5 diamond shapes. |
| `Hexagons2` – `Hexagons5` | 2 to 5 hexagons. |
| `Triangles2` – `Triangles5` | 2 to 5 triangles. |

### Shape Definitions

| Method | Use Case |
|---|---|
| `define_custom_cube(type, marker, size_mm, marker_width_mm, marker_height_mm, is_unique=True)` | Same marker on all 6 faces, uniform size. |
| `define_custom_box(type, marker_front/back/top/bottom/left/right, depth/width/height_mm, marker_width/height_mm, is_unique=True)` | Different marker on each face, custom dimensions (depth=X, width=Y, height=Z). |
| `define_custom_wall(type, marker, width_mm, height_mm, marker_width/height_mm, is_unique=True)` | Flat surface (fixed 10mm depth), same marker front and back. |

### `FixedCustomObject`

A virtual obstacle placed in Vector's world model that he cannot observe but will path-plan around. Created via `create_custom_fixed_object()`.

| Property | Type | Description |
|---|---|---|
| `pose` | `Pose` | Fixed position in world. |
| `object_id` | `int` | Assigned ID. |
| `x_size_mm` / `y_size_mm` / `z_size_mm` | `float` | Dimensions. |

```python
from anki_vector.util import Pose, degrees

# Place a virtual wall 200mm in front of Vector
robot.world.create_custom_fixed_object(
    Pose(200, 0, 0, angle_z=degrees(0)),
    x_size_mm=10, y_size_mm=200, z_size_mm=100,
    relative_to_robot=True
)
```

---

## 14. Navigation Map

**Module:** `anki_vector.nav_map`

Vector builds a **navigation memory map** of his environment as he drives around. This is **not** a probabilistic occupancy grid; rather, it encodes **what type of content** exists at each map cell.

### How the Nav Map Works

The map is stored as a **quad-tree** — a hierarchical spatial data structure where the root node covers the entire map area and each internal node is recursively subdivided into 4 equal children. Leaf nodes store content type.

```
         ┌─────────┐
         │  Root    │  (largest square, ~1250mm)
         └────┬────┘
        ┌─────┼─────┐
   ┌────┴───┐ │  ┌──┴───┐
   │ Quad 0 │ │  │Quad 2│   Depth 1: 4 children
   └────────┘ │  └──────┘
          ┌───┴───┐
          │Quad 1 │ ... etc.
          └───────┘
```

**Child node layout** (top-down XY view):

```
┌───┬───┐
│ 2 │ 0 │   Y ↑
├───┼───┤     │
│ 3 │ 1 │    X →
└───┴───┘
```

### `NavNodeContentTypes` (Enum)

| Value | Description |
|---|---|
| `Unknown` | Content unknown — not yet explored. |
| `ClearOfObstacle` | No obstacles seen, but may contain a cliff (not yet driven over). |
| `ClearOfCliff` | Confirmed clear — safe to drive through. |
| `ObstacleCube` | Contains a Light Cube. |
| `ObstacleProximity` | Obstacle detected by proximity sensor (unexplored). |
| `ObstacleProximityExplored` | Proximity obstacle that has been further explored. |
| `ObstacleUnrecognized` | Unrecognized obstacle. |
| `Cliff` | Cliff / sharp drop detected. |
| `InterestingEdge` | Visible edge detected in camera feed (sudden color change). |
| `NonInterestingEdge` | Non-interesting edge (internal use). |

### `NavMapGrid`

Top-level navigation map object.

| Property | Type | Description |
|---|---|---|
| `origin_id` | `int` | Coordinate frame ID — only compare with poses of same origin. |
| `root_node` | `NavMapGridNode` | Root of the quad-tree. |
| `size` | `float` | Side length of the map square (mm). |
| `center` | `Vector3` | Center position of the map. |

| Method | Description |
|---|---|
| `contains_point(x, y)` | Check if point is within map bounds. |
| `get_node(x, y)` | Get the smallest node containing the point. |
| `get_content(x, y)` | Get the content type at the given position. Returns `Unknown` if out of bounds. |

### `NavMapGridNode`

Individual node in the quad-tree.

| Property | Type | Description |
|---|---|---|
| `depth` | `int` | Depth in the tree (root is deepest). |
| `size` | `float` | Side length of this node's square (mm). |
| `center` | `Vector3` | Center position in world coordinates. |
| `parent` | `NavMapGridNode` | Parent node (`None` for root). |
| `children` | `list[NavMapGridNode]` or `None` | 4 children if subdivided, `None` for leaves. |
| `content` | `NavNodeContentType` | Content type (only on leaf nodes). |

| Method | Description |
|---|---|
| `contains_point(x, y)` | Test if point falls within this node. |
| `get_node(x, y)` | Get the smallest child node containing the point. |
| `get_content(x, y)` | Get content at point (recurses through children). |

### `NavMapComponent`

| Method | Description |
|---|---|
| `init_nav_map_feed(frequency=0.5)` | Start receiving nav map updates at the given frequency (Hz). |
| `close_nav_map_feed()` | Stop the nav map feed. |

| Property | Type | Description |
|---|---|---|
| `latest_nav_map` | `NavMapGrid` | Most recently received map. |

```python
with anki_vector.Robot(enable_nav_map_feed=True) as robot:
    import time; time.sleep(5)
    nav = robot.nav_map.latest_nav_map
    if nav:
        content = nav.get_content(100, 0)  # Check 100mm in front of origin
        print(content)
```

---

## 15. Face Recognition

**Module:** `anki_vector.faces`

### How Face Detection Works

When face detection is enabled, Vector's vision system looks for human faces in each camera frame. For each face:
- A bounding box (`ImageRect`) is reported for where the face appears in the image.
- A 3D `Pose` is estimated for the face's position in world space.
- If expression estimation is enabled, facial landmarks (eyes, nose, mouth) and an expression classification are provided.
- If the face has been enrolled (named), the name is returned with each observation.

Face detection is controlled via `robot.vision.enable_face_detection()` or the `enable_face_detection` constructor parameter.

### Constants

| Constant | Value | Description |
|---|---|---|
| `FACE_VISIBILITY_TIMEOUT` | 0.8 seconds | Time after last observation before a face is considered no longer visible. |

### `Expression` (Enum)

| Value | Description |
|---|---|
| `UNKNOWN` | Expression could not be determined. |
| `NEUTRAL` | Neutral expression. |
| `HAPPINESS` | Happy / smiling. |
| `SURPRISE` | Surprised. |
| `ANGER` | Angry. |
| `SADNESS` | Sad. |

### `Face`

Represents a detected face.

| Property | Type | Description |
|---|---|---|
| `face_id` | `int` | Identifier for this face instance. |
| `name` | `str` | Enrolled name, or empty string if unknown. |
| `expression` | `Expression` | Detected facial expression. |
| `expression_score` | `list[int]` | Confidence scores for each expression category. |
| `left_eye` | `list[Point]` | Outline points for the left eye. |
| `right_eye` | `list[Point]` | Outline points for the right eye. |
| `nose` | `list[Point]` | Outline points for the nose. |
| `mouth` | `list[Point]` | Outline points for the mouth. |
| `pose` | `Pose` | 3D position/orientation of the face in world space. |
| `last_observed_time` | `float` | SDK time the face was last seen. |
| `last_observed_robot_timestamp` | `int` | Robot time the face was last seen. |
| `last_observed_image_rect` | `ImageRect` | Bounding box in the camera image. |
| `is_visible` | `bool` | Seen within last 0.8 seconds. |
| `time_since_last_seen` | `float` | Seconds since last observation. |
| `has_updated_face_id` | `bool` | Whether the face_id was changed (merged with another). |
| `updated_face_id` | `int` | New face_id if changed. |

| Method | Description |
|---|---|
| `name_face(name)` | Enroll this face with the given name. Vector will remember and recognize this person. |

### `FaceComponent`

| Method | Description |
|---|---|
| `request_enrolled_names()` | Get all enrolled face names. |
| `update_enrolled_face_by_id(face_id, old_name, new_name)` | Rename an enrolled face. |
| `erase_enrolled_face_by_id(face_id)` | Delete a face enrollment. |

### Face Events

| Event | Class | Description |
|---|---|---|
| `Events.face_observed` | `EvtFaceObserved` | Continuously dispatched while a face is visible. Properties: `face`, `image_rect`, `name`, `pose`. |
| `Events.face_appeared` | `EvtFaceAppeared` | Dispatched once when a face first becomes visible. |
| `Events.face_disappeared` | `EvtFaceDisappeared` | Dispatched when a face is no longer visible. Property: `face`. |

```python
import time
import anki_vector
from anki_vector.events import Events
from anki_vector.util import degrees

def on_face(robot, event_type, event):
    print(f"Saw face: {event.face.name or 'unknown'} at {event.face.pose}")

with anki_vector.Robot(enable_face_detection=True) as robot:
    robot.behavior.set_head_angle(degrees(20))
    robot.events.subscribe(on_face, Events.face_appeared)
    time.sleep(10)
```

---

## 16. Proximity Sensor

**Module:** `anki_vector.proximity`

Vector has a time-of-flight infrared distance sensor on his front that detects objects directly ahead.

### `ProximitySensorData`

| Property | Type | Description |
|---|---|---|
| `distance` | `Distance` | Measured distance to the nearest object. |
| `signal_quality` | `float` | Signal quality from 0.0 (poor) to 1.0 (strong). Low values = unreliable reading. |
| `found_object` | `bool` | `True` if an object was detected within sensor range. |
| `unobstructed` | `bool` | `True` if no obstacles detected (clear path ahead). |
| `is_lift_in_fov` | `bool` | `True` if Vector's lift is in the sensor's field of view (blocking the reading). |

### `ProximityComponent`

| Property | Type | Description |
|---|---|---|
| `last_sensor_reading` | `ProximitySensorData` | Most recent proximity reading (updated via robot state stream). |

```python
with anki_vector.Robot() as robot:
    prox = robot.proximity.last_sensor_reading
    if prox is not None:
        print(f"Distance: {prox.distance.distance_mm} mm")
        print(f"Object found: {prox.found_object}")
        print(f"Signal quality: {prox.signal_quality}")
```

---

## 17. Touch Sensor

**Module:** `anki_vector.touch`

Vector has a capacitive touch sensor on his back (the gold contact area).

### `TouchSensorData`

| Property | Type | Description |
|---|---|---|
| `raw_touch_value` | `int` | Raw capacitance reading from the sensor. |
| `is_being_touched` | `bool` | `True` if the robot is being actively touched (thresholded from raw value). |

### `TouchComponent`

| Property | Type | Description |
|---|---|---|
| `last_sensor_reading` | `TouchSensorData` | Most recent touch reading. |

```python
with anki_vector.Robot() as robot:
    touch = robot.touch.last_sensor_reading
    print(f"Being touched: {touch.is_being_touched}")
```

---

## 18. Photos

**Module:** `anki_vector.photos`

Access photos stored on Vector's internal memory.

### `PhotographComponent`

| Method | Description |
|---|---|
| `load_photo_info()` | Fetch the list of stored photo metadata. Populates `photo_info`. |
| `get_photo(photo_id)` | Download a full-resolution photo by ID. |
| `get_thumbnail(photo_id)` | Download a thumbnail for a photo by ID. |

| Property | Type | Description |
|---|---|---|
| `photo_info` | `list[PhotoInfo]` | List of photo metadata (populated after `load_photo_info()`). |

```python
with anki_vector.Robot() as robot:
    robot.photos.load_photo_info()
    for info in robot.photos.photo_info:
        photo = robot.photos.get_photo(info.photo_id)
        # photo contains image data
```

---

## 19. Events System

**Module:** `anki_vector.events`

The SDK uses a publish/subscribe event system for asynchronous notifications from the robot.

### `EventHandler`

| Method | Description |
|---|---|
| `subscribe(func, event_type, *args, **kwargs)` | Register a callback for an event type. Callback signature: `func(robot, event_type, event_data)`. |
| `subscribe_by_name(func, event_name, *args, **kwargs)` | Subscribe using a string event name. |
| `unsubscribe(func, event_type)` | Remove a previously registered callback. |
| `unsubscribe_by_name(func, event_name)` | Unsubscribe by name. |
| `dispatch_event(event_data, event_type)` | Manually dispatch an event (internal use). |

**Special kwarg:** Pass `_on_connection_thread=True` to have the callback invoked on the gRPC event loop thread (for internal use by other components).

### `Events` (Enum — Complete List)

#### Robot Events (from gRPC stream)

| Event Name | Description |
|---|---|
| `robot_state` | Robot state update (pose, sensors, status). Fires continuously (~15 Hz). |
| `robot_observed_face` | Face observed by robot. |
| `robot_changed_observed_face_id` | Face ID changed (merge). |
| `robot_erased_enrolled_face` | Enrolled face deleted. |
| `robot_renamed_enrolled_face` | Enrolled face renamed. |
| `robot_observed_object` | Object observed by robot. |
| `robot_observed_motion` | Motion detected in camera frame. |
| `object_available` | Object availability broadcast. |
| `object_connection_state` | Object BLE connection changed (cube connect/disconnect). |
| `object_moved` | Object started moving (accelerometer). |
| `object_stopped_moving` | Object stopped moving. |
| `object_up_axis_changed` | Object orientation changed. |
| `object_tapped` | Object was tapped. |
| `cube_connection_lost` | Cube BLE connection lost. |
| `unexpected_movement` | Unexpected physical disturbance. |
| `wake_word` | "Hey Vector" detected. |
| `user_intent` | Voice command recognized (see [User Intent](#20-user-intent-voice-commands)). |
| `mirror_mode_disabled` | Mirror mode was auto-disabled. |
| `vision_modes_auto_disabled` | Vision modes were auto-disabled. |
| `camera_settings_update` | Camera settings changed. |
| `audio_send_mode_changed` | Audio mode changed. |

#### SDK Events (locally generated)

| Event Name | Description |
|---|---|
| `face_observed` | SDK-dispatched face observation (continuous while visible). |
| `face_appeared` | SDK-dispatched: face first became visible. |
| `face_disappeared` | SDK-dispatched: face no longer visible. |
| `object_observed` | SDK-dispatched object observation. |
| `object_appeared` | SDK-dispatched: object first appeared. |
| `object_disappeared` | SDK-dispatched: object no longer visible. |
| `object_finished_move` | SDK-dispatched: object stopped moving (includes `move_duration`). |
| `nav_map_update` | New navigation map received. |
| `new_raw_camera_image` | Raw camera image received (`PIL.Image`). |
| `new_camera_image` | Processed camera image received (`CameraImage`). |

### Usage Pattern

```python
import anki_vector
from anki_vector.events import Events

def on_wake_word(robot, event_type, event):
    print("Vector heard 'Hey Vector'!")

with anki_vector.Robot(behavior_control_level=None) as robot:
    robot.events.subscribe(on_wake_word, Events.wake_word)
    import time; time.sleep(30)
```

---

## 20. User Intent (Voice Commands)

**Module:** `anki_vector.user_intent`

When a user says "Hey Vector" followed by a command, the robot recognizes the intent and sends a `user_intent` event.

### `UserIntentEvent` (Enum — 42 intents)

| Intent | Trigger Example |
|---|---|
| `character_age` | "How old are you?" |
| `check_timer` | "Check the timer" |
| `explore_start` | "Go explore" |
| `global_stop` | "Stop" |
| `greeting_goodbye` | "Goodbye" |
| `greeting_goodmorning` | "Good morning" |
| `greeting_hello` | "Hello" |
| `imperative_abuse` | (abusive command) |
| `imperative_affirmative` | "Yes" / "Good boy" |
| `imperative_apology` | "I'm sorry" |
| `imperative_come` | "Come here" |
| `imperative_dance` | "Dance" |
| `imperative_fetchcube` | "Fetch your cube" |
| `imperative_findcube` | "Find your cube" |
| `imperative_lookatme` | "Look at me" |
| `imperative_love` | "I love you" |
| `imperative_praise` | "Good robot" |
| `imperative_negative` | "No" / "Bad robot" |
| `imperative_scold` | "Bad boy" |
| `imperative_volumelevel` | "Volume [level]" |
| `imperative_volumeup` | "Volume up" |
| `imperative_volumedown` | "Volume down" |
| `movement_forward` | "Go forward" |
| `movement_backward` | "Go backward" |
| `movement_turnleft` | "Turn left" |
| `movement_turnright` | "Turn right" |
| `movement_turnaround` | "Turn around" |
| `knowledge_question` | "I have a question" |
| `names_ask` | "What's my name?" |
| `play_anygame` | "Play a game" |
| `play_anytrick` | "Do a trick" |
| `play_blackjack` | "Play blackjack" |
| `play_fistbump` | "Fist bump" |
| `play_pickupcube` | "Pick up your cube" |
| `play_popawheelie` | "Pop a wheelie" |
| `play_rollcube` | "Roll your cube" |
| `seasonal_happyholidays` | "Happy holidays" |
| `seasonal_happynewyear` | "Happy new year" |
| `set_timer` | "Set a timer" |
| `show_clock` | "What time is it?" |
| `take_a_photo` | "Take a photo" |
| `weather_response` | "What's the weather?" |

### `UserIntent`

| Property | Type | Description |
|---|---|---|
| `intent_event` | `UserIntentEvent` | The recognized intent. |
| `intent_data` | `str` | JSON-formatted data associated with the intent. |

```python
from anki_vector.events import Events

def on_intent(robot, event_type, event):
    print(f"Intent: {event.intent_event}, Data: {event.intent_data}")

with anki_vector.Robot(behavior_control_level=None) as robot:
    robot.events.subscribe(on_intent, Events.user_intent)
    import time; time.sleep(30)
```

---

## 21. Status Flags

**Module:** `anki_vector.status`

### `RobotStatus`

A bitfield updated continuously via the robot state stream. Access individual flags as boolean properties:

| Property | Description |
|---|---|
| `are_motors_moving` | Any motor is currently active. |
| `is_carrying_block` | Vector is carrying the cube. |
| `is_docking_to_marker` | Vector is actively docking with a marker. |
| `is_picked_up` | Vector has been picked up. |
| `is_button_pressed` | Back button is pressed. |
| `is_falling` | Vector is falling. |
| `is_animating` | An animation is playing. |
| `is_pathing` | Following a path (driving to a waypoint). |
| `is_lift_in_pos` | Lift has reached target position. |
| `is_head_in_pos` | Head has reached target position. |
| `is_in_calm_power_mode` | Vector is in low-power/calm mode. |
| `is_on_charger` | Vector is on the charger. |
| `is_charging` | Battery is actively charging. |
| `is_cliff_detected` | Cliff sensor triggered. |
| `are_wheels_moving` | Wheels are in motion. |
| `is_being_held` | Vector detects being held in the air. |
| `is_robot_moving` | Vector is in motion (translation or rotation). |

```python
with anki_vector.Robot() as robot:
    print(f"On charger: {robot.status.is_on_charger}")
    print(f"Picked up:  {robot.status.is_picked_up}")
    print(f"Moving:     {robot.status.is_robot_moving}")
```

---

## 22. Image Annotation

**Module:** `anki_vector.annotate`

The annotation system draws visual overlays (bounding boxes, labels) onto camera images to highlight detected faces and objects.

### Constants

| Constant | Value |
|---|---|
| `RESAMPLE_MODE_NEAREST` | Fastest resampling (nearest-neighbor). |
| `RESAMPLE_MODE_BILINEAR` | Smoother resampling (linear interpolation). |

### `AnnotationPosition` (Enum)

Controls where text labels appear relative to bounding boxes:

`TOP_LEFT`, `TOP_RIGHT`, `BOTTOM_LEFT`, `BOTTOM_RIGHT`

### `ImageAnnotator`

The main annotation engine. Accessed via `robot.camera.image_annotator`. It collects annotators (one for faces, one for objects, plus any custom annotators) and applies them all to produce an annotated image.

### Built-in Annotators

| Annotator | Description |
|---|---|
| `FaceAnnotator` | Draws bounding boxes and names around detected faces. |
| `ObjectAnnotator` | Draws bounding boxes around detected objects (uses `DEFAULT_OBJECT_COLORS`). |
| `TextAnnotator` | Draws arbitrary text at specified positions. |

### `DEFAULT_OBJECT_COLORS`

| Object Type | Color |
|---|---|
| `LightCube` | Yellow |
| `CustomObject` | Purple |
| Default | Red |

### `@annotator` Decorator

Used to register custom annotation functions:

```python
from anki_vector.annotate import annotator

@annotator
def my_custom_annotator(image, scale, annotator, world, **kwargs):
    # Draw custom overlays on image
    pass
```

---

## 23. Viewers (2D & 3D)

**Module:** `anki_vector.viewer`

### `ViewerComponent` (2D Camera Viewer)

Displays Vector's camera feed in a separate window.

| Method | Description |
|---|---|
| `show(timeout=10.0, force_on_top=True)` | Open the viewer window. |
| `close()` | Close the viewer window. |
| `enqueue_frame(image)` | Push a custom image to the viewer. |

### `Viewer3DComponent` (3D World Viewer)

Displays a 3D rendering of Vector, his cube, charger, and navigation map using OpenGL.

| Method | Description |
|---|---|
| `show(show_viewer_controls=True)` | Open the 3D viewer. |
| `close()` | Close the 3D viewer. |
| `add_render_call(render_function, *args)` | Inject a custom OpenGL render function. |
| `connect_to_cube()` | Connect to cube (convenience wrapper). |

**Usage:**
```python
with anki_vector.Robot(show_viewer=True, show_3d_viewer=True, enable_nav_map_feed=True) as robot:
    import time; time.sleep(30)  # view for 30 seconds
```

---

## 24. Lights & Colors

**Module:** `anki_vector.lights`, `anki_vector.color`

### `Color`

```python
Color(int_color)
```

| Property | Type | Description |
|---|---|---|
| `int_color` | `int` | RGBA integer (alpha forced to 0xFF). |
| `rgb565_bytepair` | `bytes` | Color in RGB565 format (for screen). |

**Predefined colors:** `green`, `red`, `blue`, `cyan`, `magenta`, `yellow`, `white`, `off`

### `Light`

Represents an LED light configuration with on/off color cycling.

```python
Light(on_color, off_color=off, on_period_ms=250, off_period_ms=0,
      transition_on_period_ms=0, transition_off_period_ms=0)
```

| Property | Type | Description |
|---|---|---|
| `on_color` | `Color` | Color when the LED is in the "on" state. |
| `off_color` | `Color` | Color during the "off" state (for blinking). |
| `on_period_ms` | `int` | Duration of "on" state (ms). |
| `off_period_ms` | `int` | Duration of "off" state (ms). Set > 0 for blinking. |
| `transition_on_period_ms` | `int` | Fade-in duration (ms). |
| `transition_off_period_ms` | `int` | Fade-out duration (ms). |

**Predefined lights:** `blue_light`, `cyan_light`, `green_light`, `magenta_light`, `off_light`, `red_light`, `white_light`, `yellow_light`

### `ColorProfile`

Applies per-channel brightness multipliers to correct for LED characteristics.

| Predefined Profile | Description |
|---|---|
| `MAX_COLOR_PROFILE` | Maximum brightness (all multipliers = 1.0). |
| `WHITE_BALANCED_CUBE_PROFILE` | Adjusted for natural-looking white on the cube LEDs (default for cube). |

```python
import anki_vector

with anki_vector.Robot() as robot:
    robot.world.connect_cube()
    cube = robot.world.connected_light_cube
    if cube:
        # Blinking red light
        blink = anki_vector.lights.Light(
            on_color=anki_vector.color.red,
            off_color=anki_vector.color.off,
            on_period_ms=500,
            off_period_ms=500
        )
        cube.set_lights(blink)
```

---

## 25. Utilities

**Module:** `anki_vector.util`

### Convenience Constructors

| Function | Returns | Description |
|---|---|---|
| `degrees(d)` | `Angle` | Create an `Angle` from degrees. |
| `radians(r)` | `Angle` | Create an `Angle` from radians. |
| `distance_mm(mm)` | `Distance` | Create a `Distance` from millimeters. |
| `distance_inches(inches)` | `Distance` | Create a `Distance` from inches. |
| `speed_mmps(mmps)` | `Speed` | Create a `Speed` from mm/s. |

### Logging

| Function | Description |
|---|---|
| `setup_basic_logging(custom_handler=None, general_log_level=None, target=None)` | Configure SDK logging. Reads `VECTOR_LOG_LEVEL` environment variable if level not specified. |
| `get_class_logger(module, obj)` | Create a namespaced logger for a class. |

### CLI Argument Parsing

```python
args = anki_vector.util.parse_command_args()
# Adds: -s/--serial (overrides ANKI_ROBOT_SERIAL env var)
```

### `@block_while_none(interval=0.1, max_iterations=50)` Decorator

Property decorator that retries until the property returns a non-`None` value. Used internally for robot state properties that take a moment to populate after connection.

Raises `VectorPropertyValueNotReadyException` if max iterations exceeded.

### `Component` (Base Class)

All functional components inherit from this. Provides:

| Property | Type | Description |
|---|---|---|
| `robot` | `Robot` | Back-reference to the owning Robot. |
| `conn` | `Connection` | Shortcut to `robot.conn`. |
| `grpc_interface` | `ExternalInterfaceStub` | Shortcut to the gRPC stub. |
| `logger` | `Logger` | Namespaced logger. |

---

## 26. Exceptions

**Module:** `anki_vector.exceptions`

All exceptions derive from `VectorException`.

| Exception | When It's Raised |
|---|---|
| `VectorException` | Base class for all SDK exceptions. |
| `VectorAsyncException` | Error in an async operation. |
| `VectorBehaviorControlException` | Control system error. |
| `VectorCameraFeedException` | Camera feed not initialized before use. |
| `VectorCameraImageCaptureException` | Image capture failed. |
| `VectorConfigurationException` | SDK config file missing or malformed. |
| `VectorConnectionException` | gRPC connection error (wraps `grpc.RpcError`). |
| `VectorControlException` | Behavior control required but not held. |
| `VectorControlTimeoutException` | Timed out waiting for behavior control. |
| `VectorInvalidVersionException` | SDK version incompatible with robot firmware. |
| `VectorNotFoundException` | Robot not found via mDNS. |
| `VectorNotReadyException` | Component accessed before initialization. |
| `VectorPropertyValueNotReadyException` | Robot state property not yet populated. |
| `VectorTimeoutException` | Generic operation timeout. |
| `VectorUnauthenticatedException` | Authentication failed (bad GUID/certificate). |
| `VectorUnavailableException` | Robot unreachable (powered off, network issue). |
| `VectorUnimplementedException` | Feature not implemented in current firmware. |
| `VectorUnreliableEventStreamException` | Event stream unreliable. |
| `VectorExternalAudioPlaybackException` | Audio playback failed. |

---

## 27. Async API

### `AsyncRobot`

`AsyncRobot` is identical to `Robot` except that all component methods return `concurrent.futures.Future` objects instead of blocking.

```python
import anki_vector

async_robot = anki_vector.AsyncRobot()
async_robot.connect()

# Non-blocking — returns immediately with a Future:
future = async_robot.behavior.say_text("Hello")

# Do other things...

# Block until the action completes:
result = future.result()

async_robot.disconnect()
```

All properties that read live state (e.g. `pose`, `status`) work identically. Only action methods (those decorated with `@on_connection_thread`) return futures.

### Direct Coroutine Execution

You can also run custom async coroutines on the connection thread:

```python
async def my_coroutine(robot):
    req = protocol.SayTextRequest(text="Direct gRPC call")
    return await robot.conn.grpc_interface.SayText(req)

result = robot.conn.run_coroutine(my_coroutine(robot))
```

---

## Appendix: Module → File Map

| Module | File | Primary Classes/Functions |
|---|---|---|
| `anki_vector` | `__init__.py` | `Robot`, `AsyncRobot` |
| `anki_vector.robot` | `robot.py` | `Robot`, `AsyncRobot` |
| `anki_vector.connection` | `connection.py` | `Connection`, `ControlPriorityLevel` |
| `anki_vector.behavior` | `behavior.py` | `BehaviorComponent` |
| `anki_vector.animation` | `animation.py` | `AnimationComponent` |
| `anki_vector.audio` | `audio.py` | `AudioComponent`, `RobotVolumeLevel` |
| `anki_vector.camera` | `camera.py` | `CameraComponent`, `CameraImage`, `CameraConfig` |
| `anki_vector.color` | `color.py` | `Color` |
| `anki_vector.events` | `events.py` | `EventHandler`, `Events` |
| `anki_vector.exceptions` | `exceptions.py` | All exception classes |
| `anki_vector.faces` | `faces.py` | `Face`, `FaceComponent`, `Expression` |
| `anki_vector.lights` | `lights.py` | `Light`, `ColorProfile` |
| `anki_vector.motors` | `motors.py` | `MotorComponent` |
| `anki_vector.nav_map` | `nav_map.py` | `NavMapComponent`, `NavMapGrid`, `NavMapGridNode` |
| `anki_vector.objects` | `objects.py` | `LightCube`, `Charger`, `CustomObject`, `CustomObjectTypes`, `CustomObjectMarkers` |
| `anki_vector.photos` | `photos.py` | `PhotographComponent` |
| `anki_vector.proximity` | `proximity.py` | `ProximityComponent`, `ProximitySensorData` |
| `anki_vector.screen` | `screen.py` | `ScreenComponent` |
| `anki_vector.status` | `status.py` | `RobotStatus` |
| `anki_vector.touch` | `touch.py` | `TouchComponent`, `TouchSensorData` |
| `anki_vector.user_intent` | `user_intent.py` | `UserIntent`, `UserIntentEvent` |
| `anki_vector.util` | `util.py` | `Pose`, `Quaternion`, `Angle`, `Vector3`, `Matrix44`, `Distance`, `Speed` |
| `anki_vector.viewer` | `viewer.py` | `ViewerComponent`, `Viewer3DComponent` |
| `anki_vector.vision` | `vision.py` | `VisionComponent` |
| `anki_vector.world` | `world.py` | `World` |
| `anki_vector.annotate` | `annotate.py` | `ImageAnnotator`, `FaceAnnotator`, `ObjectAnnotator` |
| `anki_vector.version` | `version.py` | `__version__` |
| `anki_vector.mdns` | `mdns.py` | `VectorMdns` |
