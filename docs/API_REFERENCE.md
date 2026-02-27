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
- `x`, `y`, `z`
- `angle_deg`

---

### `vector_status`
Return robot status.

**Input:** none

**Output fields:**
- `battery_level` — integer charge level reported by the SDK
- `battery_voltage` — float voltage reading
- `is_charging` — bool
- `is_carrying_block` — bool
- `is_on_charger_platform` — bool
- `is_cliff_detected` — bool
- `is_moving` — bool
- `firmware_version` — string OS version from the robot, or `null` when unavailable

---

<!-- PENDING REGISTRY: tools below are implemented but not yet registered in tool_registry.py -->

### `vector_charger_status` *(pending registry)*
Return charger and battery state.

**Input:** none

**Output fields:**
- `is_charging` — bool
- `is_on_charger_platform` — bool
- `battery_level` — integer
- `battery_voltage` — float
- `suggested_charger_sec` — float seconds remaining on charger suggested by SDK

---

### `vector_touch_status` *(pending registry)*
Return touch sensor reading.

**Input:** none

**Output fields (success):**
- `is_being_touched` — bool
- `raw_touch_value` — integer raw capacitive sensor value

**Error case:** when the sensor reading is unavailable the tool returns
`{"status": "error", "message": "Touch sensor reading unavailable"}`.

---

### `vector_proximity_status` *(pending registry)*
Return proximity sensor reading.

**Input:** none

**Output fields (success):**
- `distance_mm` — float distance to nearest detected object in mm
- `found_object` — bool whether an object was detected
- `is_lift_in_fov` — bool whether the lift occludes the sensor
- `signal_quality` — float signal quality in range 0.0–1.0
- `unobstructed` — bool whether the sensor path is clear

**Error case:** when the sensor reading is unavailable the tool returns
`{"status": "error", "message": "Proximity sensor reading unavailable"}`.

---

### `vector_face`
Display a custom image on face.

**Input:**
- `image_base64` (required)
- `duration_sec` (optional)

---

### `vector_cube`
Cube interactions.

**Input:**
- `action` (enum): `dock`, `pickup`, `drop`, `roll`

---

### `vector_animate`
Play named animation.

**Input:**
- `animation_name` (string)

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

## Proven Test Pattern
For motion validation, use a one-command-at-a-time protocol with human confirmation between steps.

Recommended sequence:
1. `vector_drive_off_charger`
2. `vector_drive` forward
3. `vector_drive` reverse
4. `vector_drive` turn (e.g., 90°)

This avoids confusion with ambient idle behavior.
