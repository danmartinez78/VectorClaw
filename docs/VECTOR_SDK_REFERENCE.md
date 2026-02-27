# Vector SDK Reference (Quick Implementation Guide)

Purpose: practical reference for implementing new MCP tools on top of the Python Vector SDK (`anki_vector` namespace, distributed via `wirepod_vector_sdk`).

> This is an implementation-focused cheat sheet, not full upstream docs.

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
- **Args:**
  - `text` (string)
- **Returns:** behavior response object
- **Notes:** Audible confirmation is good for smoke tests.

#### `drive_off_charger()`
- **Use for:** motion precondition when Vector is on charger
- **Args:** none
- **Returns:** behavior response object
- **Common failure reason:** already off charger / charger state transitions.

#### `drive_straight(distance, speed, should_play_anim=True, num_retries=0, ...)`
- **Use for:** forward/reverse motion
- **Args:**
  - `distance`: `util.distance_mm(x)` (`x>0` forward, `x<0` reverse)
  - `speed`: `util.speed_mmps(v)` (positive)
  - `should_play_anim` (optional bool)
- **Returns:** `DriveStraightResponse`
- **Critical precondition:** Vector must be off charger
- **Observed response code when violated:** `SHOULDNT_DRIVE_ON_CHARGER`

#### `turn_in_place(angle, ...)`
- **Use for:** in-place turning
- **Args:**
  - `angle`: `util.degrees(x)` (`x>0` left, `x<0` right)
- **Returns:** `TurnInPlaceResponse`
- **Note:** Signature differs by SDK version; avoid unsupported kwargs unless verified.

#### `set_head_angle(angle, ...)`
- **Use for:** head pitch control
- **Args:**
  - `angle`: `util.degrees(x)`
- **Returns:** behavior response
- **Recommended:** clamp input range in MCP layer.

#### `set_lift_height(height, ...)`
- **Use for:** lift/arm control
- **Args:**
  - `height` (float, generally normalized range 0.0–1.0)
- **Returns:** behavior response
- **Recommended:** validate/clamp range in MCP layer.

---

### Pose and status

#### `robot.pose`
- **Use for:** position/orientation
- **Common fields used in MCP:**
  - `position.x`, `position.y`, `position.z`
  - `rotation.angle_z.degrees`

#### `robot.get_battery_state()`
- **Use for:** battery information
- **Common fields:**
  - `battery_level`

#### `robot.status`
- **Use for:** robot state flags
- **Common fields:**
  - `is_charging`
  - `is_carrying_block` (SDK-correct field)

---

### Camera (`robot.camera`)

#### `latest_image`
- **Use for:** last camera frame
- **Pattern:** convert PIL image to JPEG bytes/base64 in MCP tool
- **Validation tip:** confirm payload non-empty and decodable.

---

### Face display (`robot.screen`)

#### `set_screen_with_image_data(...)` / helpers
- **Use for:** custom face image display
- **Input requirements:** format/size constraints apply (Vector face dimensions)
- **MCP recommendation:** validate base64 decode + image shape before SDK call.

---

### Animation (`robot.anim`)

#### `play_animation(name)` / triggers
- **Use for:** predefined motion/eye animation sequences
- **Dependency:** animation list/trigger availability
- **Observed caveat:** animation-list loading can timeout in some Wire-Pod + SDK combos.
- **Current mitigation in validation:** `cache_animation_lists=False` for core motion path.

---

### Cube / world (`robot.world`)

- Cube actions depend on cube availability/pairing.
- MCP tools should return explicit actionable errors when cube not connected.

## Known compatibility notes from validation

1. `wirepod_vector_sdk` package installs under `anki_vector` namespace.
2. Modern Python compatibility may require SDK fork patches (see `SDK_FORK_PATCH_NOTES.md`).
3. Charger preconditions must be handled explicitly for movement reliability.

## MCP implementation patterns that worked

- One-command-at-a-time hardware tests with human confirmation.
- Movement tools should expose clear parameters and defaults:
  - `distance_mm`, `speed`, `angle_deg`
- Add charger helper tool (`drive_off_charger`) for deterministic motion tests.
