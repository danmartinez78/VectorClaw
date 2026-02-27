# Wire-Pod Vector SDK Reference (Implementation Guide)

Purpose: implementation-focused reference for building MCP tools on top of the Python SDK (`anki_vector` namespace, distributed via `wirepod_vector_sdk`).

> This document is **not** the full upstream API documentation. It is a practical, curated guide for VectorClaw contributors.
>
> Upstream API docs: https://github.com/kercre123/wirepod-vector-python-sdk/blob/master/docs/source/api.rst

## Setup assumptions

- Import namespace: `anki_vector`
- Typical robot init:

```python
import anki_vector
robot = anki_vector.Robot(serial, ip=host, cache_animation_lists=False)
robot.connect()
```

- Utility types from `anki_vector.util`:
  - `distance_mm(value)`
  - `speed_mmps(value)`
  - `degrees(value)`

## Core components and methods

### BehaviorComponent (`robot.behavior`)

#### `say_text(text: str)`
- **Use for:** TTS speech output

#### `drive_off_charger()`
- **Use for:** motion precondition when Vector is on charger

#### `drive_straight(distance, speed, should_play_anim=True, num_retries=0, ...)`
- **Use for:** forward/reverse motion
- **Critical precondition:** Vector must be off charger
- **Observed response code when violated:** `SHOULDNT_DRIVE_ON_CHARGER`

#### `turn_in_place(angle, ...)`
- **Use for:** in-place turning
- **Note:** Signature differs by SDK version; avoid unsupported kwargs unless verified.

#### `set_head_angle(angle, ...)`
- **Use for:** head pitch control
- **Recommendation:** clamp input range in MCP layer.

#### `set_lift_height(height, ...)`
- **Use for:** lift/arm control
- **Recommendation:** validate/clamp range in MCP layer.

---

### Pose and status

#### `robot.pose`
- **Use for:** position/orientation
- Common fields:
  - `position.x`, `position.y`, `position.z`
  - `rotation.angle_z.degrees`

#### `robot.get_battery_state()`
- **Use for:** battery information

#### `robot.status`
- **Use for:** robot state flags
- Common fields:
  - `is_charging`
  - `is_carrying_block`

---

### Camera (`robot.camera`)

#### `latest_image`
- **Use for:** last camera frame
- Pattern: convert PIL image to JPEG bytes/base64 in MCP tool.

---

### Face display (`robot.screen`)

#### `set_screen_with_image_data(...)` / helpers
- **Use for:** custom face image display
- **Input requirements:** format/size constraints apply (Vector face dimensions).

---

### Animation (`robot.anim`)

#### `play_animation(name)` / triggers
- **Use for:** predefined motion/eye animation sequences
- **Caveat:** animation-list loading can timeout in some Wire-Pod + SDK combos.

---

### Cube / world (`robot.world`)

- Cube actions depend on cube availability/pairing.
- MCP tools should return explicit actionable errors when cube is unavailable.

## Known compatibility notes

1. `wirepod_vector_sdk` installs under the `anki_vector` namespace.
2. Modern Python compatibility may require SDK fork patches (see `SDK_FORK_PATCH_NOTES.md`).
3. Charger preconditions should be handled explicitly for movement reliability.

## Scope rule

If a capability exists upstream but is not exposed in MCP, treat this as **possible but not promised** until it appears in:
- `API_REFERENCE.md` (implemented MCP contract), and
- `SDK_TO_MCP_COVERAGE_MATRIX.md` (coverage status and rationale).
