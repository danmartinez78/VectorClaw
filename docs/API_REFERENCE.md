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

## Perception Discovery Helpers *(pending registry — draft)*

> **Note:** The tools below are implemented in `tools_perception.py` but are not yet wired into the central tool registry or server. They are available as importable Python functions and will be registered in a follow-up issue.

### `vector_scan`
Look around in place to survey the environment.

**Input:** none

**Example response:**
```json
{"status": "ok"}
```

---

### `vector_find_faces`
Actively search for faces in the current environment.

**Input:** none

**Example response:**
```json
{"status": "ok"}
```

---

### `vector_list_visible_faces`
Return a list of faces currently visible to Vector.

**Input:** none

**Output fields:**
- `faces` — array of face objects, each with:
  - `face_id` (integer)
  - `name` (string or null if unrecognised)

**Example response (faces detected):**
```json
{"status": "ok", "faces": [{"face_id": 1, "name": "Alice"}, {"face_id": 2, "name": null}]}
```

**Example response (no faces):**
```json
{"status": "ok", "faces": []}
```

---

### `vector_list_visible_objects`
Return a list of objects (standard and custom) currently visible to Vector.

**Input:** none

**Output fields:**
- `objects` — array of object entries (both `world.visible_objects` and `world.visible_custom_objects`), each with:
  - `object_id` (integer)
  - `object_type` (string)

**Example response (objects detected):**
```json
{"status": "ok", "objects": [{"object_id": 10, "object_type": "LightCube"}]}
```

**Example response (no objects):**
```json
{"status": "ok", "objects": []}
```
