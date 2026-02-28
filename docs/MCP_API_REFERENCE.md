# VectorClaw API Reference (MCP Tools)

## Overview
VectorClaw exposes robot controls as MCP tools. All tools return JSON with a `status` field.

- `status: "ok"` for successful execution
- `status: "error"` with a `message` when a command fails

## Tools

### `vector_drive_off_charger`
Drive Vector off the charger before movement actions.

**Input:** none

**Example response:**
```json
{"status":"ok"}
```

---

### `vector_drive`
Drive straight and/or turn in place.

**Input:**
- `distance_mm` (number, optional): positive forward, negative reverse
- `speed` (number, optional, default `50` mm/s)
- `angle_deg` (number, optional): positive left turn

At least one of `distance_mm` or `angle_deg` should be provided.

**Charger precondition:** Vector must be off the charger before motion commands are
accepted.  If it is on the charger the tool returns an actionable error rather than
silently failing:

```json
{
  "status": "error",
  "on_charger": true,
  "action_required": "call vector_drive_off_charger first",
  "message": "Vector is on the charger; drive it off before sending motion commands"
}
```

**Auto drive-off-charger:** Set the environment variable
`VECTOR_AUTO_DRIVE_OFF_CHARGER=1` (or `true` / `yes`) to have the tool
automatically call the `vector_drive_off_charger` tool (which uses
`robot.behavior.drive_off_charger()` in the SDK) and continue when the precheck
detects a charger state. If the auto-drive itself fails the error is still surfaced
with the same `on_charger` and `action_required` fields.

**Example:**
```json
{"distance_mm":100,"speed":50}
```

---

### `vector_say`
Speak text aloud.

**Input:**
- `text` (string, required)

---

### `vector_look`
Capture a camera image.

**Input:** none

**Output:**
- `image_base64` (JPEG payload)
- `content_type` (`image/jpeg`)

---

### `vector_pose`
Return current pose.

**Input:** none

**Output fields:**
- `x`, `y`, `z` — Position coordinates in millimeters
- `angle_deg` — Heading angle in degrees
- `origin_id` — Pose frame-of-reference identifier (integer). Changes when the robot is picked up and set down, causing relocalization. Poses with different `origin_id` values cannot be directly compared.
- `is_picked_up` — `true` when Vector is currently picked up off the ground.
- `localized_to_object_id` — ID of the object the robot's pose is localized to (integer or `null` when not localized to a specific object).

**Reference frame semantics:**
- Robot body frame origin: Point on ground between Vector's front wheels
- X: forward, Y: left, Z: up
- World frame origin: Established at initialization
- **Delocalization:** When picked up, robot creates new `origin_id` and resets pose to (0,0,0)
- **Warning:** Poses with different `origin_id` values cannot be compared. Use `pose.is_comparable(other_pose)` to check.

**SDK source:** `anki_vector/util.py` - `class Pose`

---

### `vector_status`
Return robot status.

**Input:** none

**Output fields:**
- `battery_level`
- `is_charging`
- `is_carrying_block`
- `is_carrying_object`
- `is_on_charger`
- `is_cliff_detected`
- `is_picked_up`

---

### `vector_charger_status`
Return charger and battery state.

**Input:** none

**Output fields:**
- `is_charging`
- `battery_level`
- `is_on_charger`

---

### `vector_touch_status`
Return touch-sensor reading from Vector's back capacitive sensor.

**Input:** none

**Output fields:**
- `is_being_touched`
- `raw_touch_value`

---

### `vector_proximity_status`
Return proximity sensor reading from Vector's time-of-flight sensor.

**Input:** none

**Output fields:**
- `distance_mm` — Measured distance to nearest object in millimeters
- `signal_quality` — Quality of the detected object (float as reported by SDK)
- `unobstructed` — True when sensor confirmed nothing detected up to max range
- `found_object` — True when sensor detected object in valid operating range
- `is_lift_in_fov` — True when Vector's lift is blocking the sensor

**Sensor specs:**
- Type: Time-of-flight distance sensor
- Usable range: 30mm to 1200mm (max useful ~300mm)
- Field of view: 25 degrees
- Location: Between front wheels, facing forward

**Field semantics:**
- `found_object`: Firmware-provided boolean from robot state. **Empirically unreliable in current setup** (remained `false` across far/mid/close/object-touching tests while `distance_mm` and `signal_quality` changed correctly).
- `unobstructed`: Sensor confirmed no object up to max range (~1200mm); empirically flipped `true` when path was clear.
- `signal_quality`: Likelihood-like metric from firmware. **Do not assume 0.0–1.0 bounds**; empirical readings exceeded 1.0 (observed up to ~11.7).
- `is_lift_in_fov`: When true, distance readings may not be useful for object detection
- Updates with every RobotState broadcast

**SDK source:** `anki_vector/proximity.py`

---

### `vector_face`
Display a custom image on face.

The image is converted to rgb565 format via `anki_vector.screen.convert_image_to_screen_data()` before being sent to the robot's screen.

**Input:**
- `image_base64` (required): Base64-encoded image (any format supported by PIL). Resized to match the robot's screen dimensions via `anki_vector.screen.dimensions()` (typically 184×96 pixels, for a 35328-byte rgb565 buffer).
- `duration_sec` (optional): How long to display the image (0.1–60.0 seconds, default 5.0).

---

### `vector_cube`
Cube interactions.

**Input:**
- `action` (enum): `dock`, `pickup`, `drop`, `roll`

---

### `vector_animate`
Play animation by name or trigger.

**Input:**
- `animation_name` (string) — Specific animation name or trigger name

**Prerequisite:** Vector must be off the charger.

**Trigger vs Name:**
- **Triggers** (recommended): Robot picks from a group of animations based on mood/random weighting. More stable across OS versions.
- **Names**: Play exact specific animation. May be renamed/removed in OS updates.

**Animation tracks:** Head, lift, treads, face, audio, backpack lights

**SDK source:** `anki_vector/animation.py`

---

### `vector_head`
Set Vector's head angle.

**Input:**
- `angle_deg` (number, required): desired angle in degrees; clamped to safe range **-22.0 – 45.0**

**Example:**
```json
{"angle_deg": 20.0}
```

**Example response:**
```json
{"status": "ok", "angle_deg": 20.0}
```

> Values outside the safe range are silently clamped.  The response always reflects the actual applied angle.

---

### `vector_lift`
Set Vector's lift/arm height.

**Input:**
- `height` (number, required): normalised lift height; clamped to **0.0** (lowest) – **1.0** (highest)

**Example:**
```json
{"height": 0.75}
```

**Example response:**
```json
{"status": "ok", "height": 0.75}
```

> Values outside 0.0–1.0 are silently clamped.  The response always reflects the actual applied height.

---

### `vector_capture_image`
Capture a single camera frame via `camera.capture_single_image`.

**Input:** none

**Output:**
- `image_base64` (JPEG payload)
- `content_type` (`image/jpeg`)

**Camera specs:**
- Resolution: 1280 x 720
- Field of view: 90° (horizontal) x 50° (vertical)

**SDK source:** `anki_vector/camera.py`

**Error response example:**
```json
{"status": "error", "message": "camera failure"}
```

---

### `vector_face_detection`
Return a summary of currently visible faces (no raw image data).

> **Vision modes:** Face detection and expression estimation are enabled automatically on a
> best-effort basis at connection time. No manual enablement call is required, but if
> enablement fails the connection may still succeed and this tool may return empty results
> until you reconnect. Calling `vector_vision_reset` can also disable these vision modes
> for the remainder of the session; after a reset, you may need to reconnect to restore
> vision-based results and should likewise expect empty outputs until vision is re-enabled.

**Input:** none

**Output fields:**
- `face_count` (integer)
- `faces` (array of `{face_id, expression}` objects)

**Example response:**
```json
{"status": "ok", "face_count": 1, "faces": [{"face_id": 1, "expression": "happy"}]}
```

---

### `vector_vision_reset`
Disable all active vision modes via `vision.disable_all_vision_modes`.

**Input:** none

**Example response:**
```json
{"status": "ok"}
```

---

## Proven Test Pattern
For motion validation, use a one-command-at-a-time protocol with human confirmation between steps.

Recommended sequence:
1. `vector_drive_off_charger`
2. `vector_drive` forward
3. `vector_drive` reverse
4. `vector_drive` turn (e.g., 90°)

This avoids confusion with ambient idle behavior.

---

### `vector_scan`
Make Vector look around in place to scan the environment.

**Input:** none

**Example response:**
```json
{"status":"ok"}
```

---

### `vector_find_faces`
Make Vector actively search for faces in the environment.

**Input:** none

**Example response:**
```json
{"status":"ok"}
```

---

### `vector_list_visible_faces`
Return the list of faces currently visible to Vector.

> **Vision modes:** Face detection is enabled automatically at connection time via
> `vision.enable_face_detection(estimate_expression=True)`. No manual enablement is
> required before calling this tool.

**Input:** none

**Output fields:**
- `faces` (array of `{face_id, name}` objects)

**Example response:**
```json
{"status": "ok", "faces": [{"face_id": 1, "name": "Alice"}]}
```

**Visibility semantics:**
- Faces remain visible for 0.8 seconds after last observation
- `name` is empty if face not enrolled (enrollment is optional, for naming only)
- Enrollment persists across SDK sessions

**SDK source:** `anki_vector/faces.py`, `anki_vector/world.py`

---

### `vector_list_visible_objects`
Return the list of objects currently visible to Vector.

> **Vision modes:** Object detection is enabled automatically at connection time via
> `vision.enable_custom_object_detection()`. No manual enablement is required before
> calling this tool.

**Input:** none

**Output fields:**
- `objects` (array of `{object_id}` objects)

**Example response:**
```json
{"status": "ok", "objects": [{"object_id": 42}]}
```

**Visibility semantics:**
- Objects remain visible for 0.8 seconds after last observation
- Object types: LightCube, Charger, CustomObject
- LightCube requires `connect_cube()` call at connection time (handled automatically)
- Objects recognized via visual markers

**SDK source:** `anki_vector/objects.py`, `anki_vector/world.py`

---

### `vector_drive_on_charger`

Drive Vector back onto its charger. Includes a configurable timeout; if the
maneuver does not complete in time a motor stop is attempted as a best-effort
fallback (the stop itself may fail, which is reflected in the response).

If Vector is already on the charger the SDK call is skipped and a success
response with `already_on_charger: true` is returned immediately.  Invoking
`drive_on_charger` while already docked can produce undefined behaviour
(observed on hardware: cube-activation animations instead of a charger-approach
sequence).

> ⚠️ **Reliability note:** Reliable docking requires the charger to be within
> the robot's recently-observed world model.  If Vector has not seen the charger
> recently the command may time out without the robot approaching it.  Use
> `vector_scan` first to give Vector a chance to locate the charger.

**Input:**
- `timeout_sec` (number, optional, default `10.0`): seconds to wait before triggering the motor-stop fallback; must be `>= 0`

**Example response (success):**
```json
{"status": "ok"}
```

**Example response (already on charger):**
```json
{"status": "ok", "already_on_charger": true}
```

**Example response (timeout — motors stopped successfully):**
```json
{
  "status": "error",
  "timed_out": true,
  "motors_stopped": true,
  "message": "drive_on_charger timed out after 10.0s; motors stopped as fallback"
}
```

**Example response (timeout — motor stop also failed):**
```json
{
  "status": "error",
  "timed_out": true,
  "motors_stopped": false,
  "message": "drive_on_charger timed out after 10.0s; attempted motor stop failed: <error>"
}
```

---

### `vector_emergency_stop`

Immediately stop all Vector motors using `motors.stop_all_motors`.

**Input:** none

**Example response:**
```json
{"status": "ok"}
```

---

## Hardware Smoke Checklist (newly registered tools)

Use the following checklist when validating newly registered tools on hardware.
Execute one command at a time and wait for explicit confirmation before proceeding.

- [ ] `vector_scan` — Vector looks around in place; confirm head/body movement
- [ ] `vector_find_faces` — Vector searches for faces; confirm behavior activation
- [ ] `vector_list_visible_faces` — Returns `faces` array (may be empty if no faces present)
- [ ] `vector_list_visible_objects` — Returns `objects` array (may be empty if no objects present)
- [ ] `vector_drive_on_charger` — Vector drives back onto charger; confirm docking
- [ ] `vector_emergency_stop` — All motors stop immediately; confirm silence
- [ ] `vector_capture_image` — Returns valid JPEG base64 payload
- [ ] `vector_face_detection` — Returns `face_count` and `faces` array
- [ ] `vector_vision_reset` — All vision modes disabled; confirm no active vision LED
- [ ] `vector_charger_status` — Returns `is_charging`, `battery_level`, `is_on_charger`
- [ ] `vector_touch_status` — Returns `is_being_touched`, `raw_touch_value`; verify by touching/not touching sensor
- [ ] `vector_proximity_status` — Returns `distance_mm`, `found_object`, `is_lift_in_fov`; verify by placing/removing object
- [ ] `vector_pose` (on ground) — Returns `origin_id` (integer), `is_picked_up: false`, coordinates
- [ ] `vector_pose` (picked up) — Returns `is_picked_up: true`; `origin_id` changes after set down and relocalization
