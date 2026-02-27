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
- `battery_level`
- `is_charging`
- `is_carrying_block`
- `is_carrying_object`
- `is_on_charger_platform`
- `is_cliff_detected`
- `is_picked_up`

---

### `vector_charger_status` *(pending hardware validation)*
Return charger and battery state.

**Input:** none

**Output fields:**
- `is_charging`
- `battery_level`
- `is_on_charger_platform`

---

### `vector_touch_status` *(pending hardware validation)*
Return touch-sensor reading from Vector's back capacitive sensor.

**Input:** none

**Output fields:**
- `is_being_touched`
- `raw_touch_value`

---

### `vector_proximity_status` *(pending hardware validation)*
Return proximity sensor reading from Vector's front IR sensor.

**Input:** none

**Output fields:**
- `distance_mm`
- `found_object`
- `is_lift_in_fov`

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

---

### `vector_drive_on_charger` *(experimental — pending MCP registration)*

Drive Vector back onto its charger. Includes a configurable timeout; if the
maneuver does not complete in time a motor stop is attempted as a best-effort
fallback (the stop itself may fail, which is reflected in the response).

> **Status:** module-only lane — not yet registered in the MCP tool registry.

**Input:**
- `timeout_sec` (number, optional, default `10.0`): seconds to wait before triggering the motor-stop fallback; must be `>= 0`

**Example response (success):**
```json
{"status": "ok"}
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

### `vector_emergency_stop` *(pending MCP registration)*

Immediately stop all Vector motors using `motors.stop_all_motors`.

> **Status:** module-only lane — not yet registered in the MCP tool registry.

**Input:** none

**Example response:**
```json
{"status": "ok"}
```
