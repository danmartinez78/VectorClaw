# Phase 1 SDK Compliance Audit

**Audit date:** 2026-02-28  
**Auditor:** Copilot  
**Reference:** `docs/WIREPOD_SDK_SURFACE_REFERENCE.md`  
**Scope:** All tools registered in `src/vectorclaw_mcp/tool_registry.py`

---

## Summary

| Tool | Discrepancies | Severity |
|------|---------------|----------|
| `vector_status` | None | — |
| `vector_charger_status` | None | — |
| `vector_proximity_status` | `found_object` semantics clarification needed | Low |
| `vector_touch_status` | None | — |
| `vector_list_visible_faces` | Face detection mode not enabled before reading | Medium |
| `vector_face_detection` | Face detection mode not enabled; expression estimation not enabled | Medium |
| `vector_list_visible_objects` | None | — |
| `vector_drive_on_charger` | None | — |
| `vector_drive_off_charger` | None | — |
| `vector_say` | None | — |
| `vector_drive` | None | — |
| `vector_head` | Head-angle constants are hardcoded, not imported from SDK | Low |
| `vector_look` | None | — |
| `vector_pose` | `Position.x/y/z` not formally documented in SDK reference | Low |
| `vector_scan` | None | — |
| `vector_find_faces` | None | — |
| `vector_capture_image` | None | — |
| `vector_vision_reset` | None | — |
| `vector_animate` | None | — |
| `vector_face` | Passes JPEG bytes to `set_screen_with_image_data`; SDK expects rgb565 format | High |
| `vector_cube` | None | — |
| `vector_lift` | None | — |
| `vector_emergency_stop` | None | — |

Previously-reported bugs (`is_carrying_object`, `is_on_charger_platform`) are **already fixed** in the current codebase.

---

## Per-tool Findings

### Tool: `vector_status`
- **SDK reference section:** `anki_vector.status.RobotStatus` (lines 1407–1464); `Robot.get_battery_state` (line 1355)
- **Properties used:**
  - `robot.get_battery_state()` → `battery.battery_level`
  - `robot.status.is_charging`
  - `robot.status.is_carrying_block`
  - `robot.status.is_on_charger`
  - `robot.status.is_cliff_detected`
  - `robot.status.is_picked_up`
- **Properties valid per SDK:**
  - `robot.get_battery_state()` — SDK line 1355 ✅
  - `robot.status` → `RobotStatus` — SDK line 1340 ✅
  - `is_charging` — SDK line 1450 ✅
  - `is_carrying_block` — SDK line 1417 ✅
  - `is_on_charger` — SDK line 1447 ✅
  - `is_cliff_detected` — SDK line 1453 ✅
  - `is_picked_up` — SDK line 1423 ✅
  - `battery.battery_level` — `protocol.BatteryStateResponse` field; not detailed in SDK reference but used consistently across SDK examples
- **Discrepancies:** None. Previously invalid names (`is_carrying_object`, `is_on_charger_platform`) have already been corrected.
- **Recommended fix:** None.

---

### Tool: `vector_charger_status`
- **SDK reference section:** `anki_vector.status.RobotStatus` (lines 1407–1464); `Robot.get_battery_state` (line 1355)
- **Properties used:**
  - `robot.get_battery_state()` → `battery.battery_level`
  - `robot.status.is_charging`
  - `robot.status.is_on_charger`
- **Properties valid per SDK:**
  - `robot.get_battery_state()` — SDK line 1355 ✅
  - `is_charging` — SDK line 1450 ✅
  - `is_on_charger` — SDK line 1447 ✅
  - `battery.battery_level` — `protocol.BatteryStateResponse` field; not detailed in SDK reference but used consistently
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_proximity_status`
- **SDK reference section:** `anki_vector.proximity` (lines 1203–1236)
- **Properties used:**
  - `robot.proximity` → `ProximityComponent`
  - `robot.proximity.last_sensor_reading` → `ProximitySensorData`
  - `prox.distance.distance_mm`
  - `prox.found_object`
  - `prox.is_lift_in_fov`
- **Properties valid per SDK:**
  - `robot.proximity` — SDK line 1283 ✅
  - `last_sensor_reading` — SDK line 1234 ✅
  - `distance` → `util.Distance` — SDK line 1211 ✅
  - `distance.distance_mm` — SDK line 1764 ✅
  - `found_object` — SDK line 1220 ✅
  - `is_lift_in_fov` — SDK line 1223 ✅
- **Discrepancies:**
  - **Semantic clarification (Low):** `found_object` is documented as "The sensor detected an object in the valid operating range" (SDK line 1222). It indicates object detection within valid range, not proximity changes or relative distance. The current tool passes the value through without interpretation, which is correct, but the tool's output description should clarify this to prevent caller misinterpretation.
- **Recommended fix:** Clarify in tool description or return value documentation that `found_object` means the sensor detected an object within its valid operating range, not that a proximity change occurred.

---

### Tool: `vector_touch_status`
- **SDK reference section:** `anki_vector.touch` (lines 1467–1491)
- **Properties used:**
  - `robot.touch` → `TouchComponent`
  - `robot.touch.last_sensor_reading` → `TouchSensorData`
  - `touch.is_being_touched`
  - `touch.raw_touch_value`
- **Properties valid per SDK:**
  - `robot.touch` — SDK line 1286 ✅
  - `last_sensor_reading` — SDK line 1490 ✅ returns `TouchSensorData`
  - `is_being_touched` — SDK line 1478 ✅
  - `raw_touch_value` — SDK line 1475 ✅
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_list_visible_faces`
- **SDK reference section:** `anki_vector.world.World` (lines 1905–2002); `anki_vector.faces.Face` (lines 707–749); `anki_vector.vision.VisionComponent` (lines 1865–1902)
- **Properties used:**
  - `robot.world.visible_faces`
  - `f.face_id`
  - `f.name`
- **Properties valid per SDK:**
  - `robot.world` — SDK line 1298 ✅
  - `world.visible_faces` — SDK line 1920 ✅ generator yielding `Face` instances
  - `face.face_id` — SDK line 717 ✅
  - `face.name` — SDK line 729 ✅
- **Discrepancies:**
  - **Vision mode not enabled (Medium):** The tool reads `robot.world.visible_faces` without first calling `robot.vision.enable_face_detection()` (SDK line 1894). The SDK's `VisionComponent` exposes `enable_face_detection(detect_faces: bool=True, estimate_expression: bool=False)` to activate face detection. Without this call, the robot's internal image processor may not be running face detection, meaning `visible_faces` will consistently return an empty iterable even when faces are present in camera view.
- **Recommended fix:** Call `robot.vision.enable_face_detection()` before reading `robot.world.visible_faces`, or document that the caller is responsible for enabling face detection mode before calling this tool.

---

### Tool: `vector_face_detection`
- **SDK reference section:** `anki_vector.world.World` (lines 1905–2002); `anki_vector.faces.Face` (lines 707–749); `anki_vector.vision.VisionComponent` (lines 1865–1902)
- **Properties used:**
  - `robot.world.visible_faces`
  - `f.face_id`
  - `f.expression`
- **Properties valid per SDK:**
  - `world.visible_faces` — SDK line 1920 ✅
  - `face.face_id` — SDK line 717 ✅
  - `face.expression` — SDK line 732 ✅ documented as `-> str`
- **Discrepancies:**
  1. **Vision mode not enabled (Medium):** Same as `vector_list_visible_faces` — `robot.vision.enable_face_detection()` is not called before reading `visible_faces`. Without enabling face detection, faces will not be detected and the list will be empty.
  2. **Expression estimation not enabled (Medium):** `face.expression` will only carry real data when `estimate_expression=True` is passed to `enable_face_detection()` (SDK line 1894: `enable_face_detection(self, detect_faces: bool=True, estimate_expression: bool=False)`). With the default `estimate_expression=False`, `face.expression` will likely be empty or a default value even when a face is visible. The tool reads `f.expression` but never enables expression estimation, so the `expression` field in the returned result will generally be uninformative.
  3. **Defensive Enum handling (Informational):** The `_normalize_expression()` helper handles both `str` and Enum-like values for `face.expression`. The SDK reference documents this as `-> str` (line 732), but the defensive handling suggests the actual SDK implementation may return an Enum. This is good defensive code, but the inconsistency between the documented return type and actual behavior is worth noting.
- **Recommended fix:**
  - Call `robot.vision.enable_face_detection(detect_faces=True, estimate_expression=True)` before reading `visible_faces` to ensure both face detection and expression estimation are active.
  - Alternatively, document that this tool requires face detection to have been previously enabled (e.g., by calling `vector_find_faces` first).

---

### Tool: `vector_list_visible_objects`
- **SDK reference section:** `anki_vector.world.World` (lines 1905–2002); `anki_vector.objects` (various)
- **Properties used:**
  - `robot.world.visible_objects`
  - `o.object_id`
- **Properties valid per SDK:**
  - `world.visible_objects` — SDK line 1935 ✅ yields `Charger`, `LightCube`, `CustomObject` instances
  - `object_id` — documented on `LightCube` (line 1074), `Charger` (line 1088), `CustomObject` (line 1131), `FixedCustomObject` (line 1161) ✅
- **Discrepancies:** None. All accessed properties are valid per SDK.
- **Recommended fix:** None. (Note: For objects to appear in `visible_objects`, the cube must be connected via `robot.world.connect_cube()`, which is the caller's responsibility. This is an operational prerequisite, not an SDK contract violation.)

---

### Tool: `vector_drive_on_charger`
- **SDK reference section:** `anki_vector.behavior.BehaviorComponent` (lines 172–333); `anki_vector.motors.MotorComponent` (lines 854–869)
- **Methods used:**
  - `robot.behavior.drive_on_charger()`
  - `robot.motors.stop_all_motors()`
- **Properties valid per SDK:**
  - `behavior.drive_on_charger()` — SDK line 179 ✅
  - `motors.stop_all_motors()` — SDK line 867 ✅
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_drive_off_charger`
- **SDK reference section:** `anki_vector.behavior.BehaviorComponent` (lines 172–333)
- **Methods used:**
  - `robot.behavior.drive_off_charger()`
- **Properties valid per SDK:**
  - `behavior.drive_off_charger()` — SDK line 176 ✅
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_say`
- **SDK reference section:** `anki_vector.behavior.BehaviorComponent` (lines 172–333)
- **Methods used:**
  - `robot.behavior.say_text(text)`
- **Properties valid per SDK:**
  - `behavior.say_text(text, use_vector_voice=True, duration_scalar=1.0)` — SDK line 191 ✅
  - Tool passes only `text`; defaults for `use_vector_voice` and `duration_scalar` are used, which is valid.
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_drive`
- **SDK reference section:** `anki_vector.behavior.BehaviorComponent` (lines 229–248); `anki_vector.util` (lines 1542–1560)
- **Methods/functions used:**
  - `robot.behavior.drive_straight(util.distance_mm(d), util.speed_mmps(s))`
  - `robot.behavior.turn_in_place(util.degrees(a))`
  - `util.distance_mm(...)` — SDK line 1550 ✅
  - `util.speed_mmps(...)` — SDK line 1558 ✅
  - `util.degrees(...)` — SDK line 1542 ✅
- **Properties valid per SDK:**
  - `behavior.drive_straight(distance, speed)` — SDK line 229 ✅
  - `behavior.turn_in_place(angle)` — SDK line 239 ✅
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_head`
- **SDK reference section:** `anki_vector.behavior.BehaviorComponent` (line 249); `anki_vector.util.degrees` (line 1542)
- **Methods used:**
  - `robot.behavior.set_head_angle(util.degrees(clamped))`
- **Properties valid per SDK:**
  - `behavior.set_head_angle(angle)` — SDK line 249 ✅ signature: `set_head_angle(self, angle: util.Angle, ...)`
  - `util.degrees(...)` — SDK line 1542 ✅
- **Discrepancies:**
  - **Hardcoded angle constants (Low):** `tools_common.py` defines `_HEAD_ANGLE_MIN = -22.0` and `_HEAD_ANGLE_MAX = 45.0` as hardcoded constants instead of importing `MIN_HEAD_ANGLE` and `MAX_HEAD_ANGLE` from `anki_vector.behavior` (as shown in SDK reference example at line 257: `from anki_vector.behavior import MIN_HEAD_ANGLE, MAX_HEAD_ANGLE`). If the SDK's valid range ever differs from these hardcoded values, the tool will silently clamp to incorrect bounds.
- **Recommended fix:** Import `MIN_HEAD_ANGLE` and `MAX_HEAD_ANGLE` from `anki_vector.behavior` at runtime instead of hardcoding `-22.0` and `45.0`.

---

### Tool: `vector_look`
- **SDK reference section:** `anki_vector.camera.CameraComponent` (lines 389–435); `anki_vector.camera.CameraImage` (lines 341–354)
- **Properties used:**
  - `robot.camera.init_camera_feed()`
  - `robot.camera.latest_image` → `CameraImage`
  - `pil_image.raw_image` (PIL Image)
- **Properties valid per SDK:**
  - `camera.init_camera_feed()` — SDK line 423 ✅
  - `camera.latest_image` → `CameraImage` — SDK line 414 ✅
  - `CameraImage.raw_image` — SDK line 345 ✅ "The raw unprocessed image from the camera"
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_pose`
- **SDK reference section:** `anki_vector.robot.Robot` (line 1301); `anki_vector.util.Pose` (lines 1705–1738); `anki_vector.util.Quaternion` (lines 1671–1698); `anki_vector.util.Position` (lines 1700–1703)
- **Properties used:**
  - `robot.pose`
  - `pose.position.x`, `pose.position.y`, `pose.position.z`
  - `pose.rotation.angle_z.degrees`
- **Properties valid per SDK:**
  - `robot.pose` → `util.Pose` — SDK line 1301 ✅
  - `pose.position` → `Position` — SDK line 1709 ✅
  - `pose.rotation` → `Quaternion` — SDK line 1712 ✅
  - `quaternion.angle_z` → `Angle` — SDK line 1687 ✅
  - `angle.degrees` — SDK line 1626 ✅
- **Discrepancies:**
  - **`Position.x/y/z` undocumented in SDK reference (Low/Informational):** The `Position` class (SDK line 1700) has "Public methods: none" in the reference. The `.x`, `.y`, `.z` attributes are accessed but are not formally documented in the SDK surface reference. They appear to be data attributes (not methods) on the `Position` object, consistent with the `Vector3` pattern where `.x`, `.y`, `.z` properties are documented (SDK lines 1591–1597). This is almost certainly valid in practice, but the SDK reference does not explicitly document `Position.x/y/z` as accessible.
- **Recommended fix:** Verify empirically that `pose.position.x`, `pose.position.y`, `pose.position.z` are accessible on `Position` instances (they almost certainly are). No code change needed; the SDK reference documentation gap should be noted.

---

### Tool: `vector_scan`
- **SDK reference section:** `anki_vector.behavior.BehaviorComponent` (line 185)
- **Methods used:**
  - `robot.behavior.look_around_in_place()`
- **Properties valid per SDK:**
  - `behavior.look_around_in_place()` — SDK line 185 ✅
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_find_faces`
- **SDK reference section:** `anki_vector.behavior.BehaviorComponent` (line 182)
- **Methods used:**
  - `robot.behavior.find_faces()`
- **Properties valid per SDK:**
  - `behavior.find_faces()` — SDK line 182 ✅
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_capture_image`
- **SDK reference section:** `anki_vector.camera.CameraComponent` (line 432); `anki_vector.camera.CameraImage` (lines 341–354)
- **Methods used:**
  - `robot.camera.capture_single_image()`
  - `image.raw_image`
- **Properties valid per SDK:**
  - `camera.capture_single_image()` — SDK line 432 ✅ signature: `capture_single_image(self, enable_high_resolution: bool=False) -> CameraImage`
  - `CameraImage.raw_image` — SDK line 345 ✅
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_vision_reset`
- **SDK reference section:** `anki_vector.vision.VisionComponent` (lines 1869–1902)
- **Methods used:**
  - `robot.vision.disable_all_vision_modes()`
- **Properties valid per SDK:**
  - `robot.vision` — SDK line 1295 ✅
  - `vision.disable_all_vision_modes()` — SDK line 1888 ✅
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_animate`
- **SDK reference section:** `anki_vector.animation.AnimationComponent` (lines 33–55)
- **Methods used:**
  - `robot.anim.play_animation(animation_name)`
- **Properties valid per SDK:**
  - `robot.anim` → `AnimationComponent` — SDK line 1256 ✅
  - `anim.play_animation(anim)` — SDK line 53 ✅ signature: `play_animation(self, anim: str, loop_count: int=1, ...)`
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_face`
- **SDK reference section:** `anki_vector.screen.ScreenComponent` (lines 1391–1400); `anki_vector.screen` module-level helpers (lines 1378–1388)
- **Methods used:**
  - `robot.screen.set_screen_with_image_data(raw_bytes, duration_sec=duration_sec)`
  - JPEG-encoded bytes are passed as `image_data`
- **Properties valid per SDK:**
  - `robot.screen` → `ScreenComponent` — SDK line 1277 ✅
  - `screen.set_screen_with_image_data(image_data, duration_sec, interrupt_running=True)` — SDK line 1395 ✅
- **Discrepancies:**
  - **Wrong image format (High):** The tool saves the resized PIL image as JPEG and passes the resulting bytes directly to `set_screen_with_image_data()`. The SDK, however, provides explicit helper functions for converting images to the correct display format:
    - `anki_vector.screen.convert_image_to_screen_data(pil_image)` — "Convert an image into the correct format to display on Vector's face" (SDK line 1384). Returns `bytes` of "16bit color in rgb565 format" (SDK line 1388).
    - `anki_vector.screen.convert_pixels_to_screen_data(pixel_data, width, height)` — "Convert a sequence of pixel data to the correct format to display on Vector's face" (SDK line 1379). Also produces rgb565.

    The existence of these helper functions strongly implies that `set_screen_with_image_data()` expects rgb565-encoded bytes, not JPEG or any other compressed format. Passing JPEG bytes would likely produce garbled or corrupted output on the robot's display, since the display driver would interpret compressed JPEG data as raw 16-bit pixel values.
- **Recommended fix:** Replace the JPEG encoding pipeline with a call to `anki_vector.screen.convert_image_to_screen_data(img)` (where `img` is the resized PIL Image), then pass the returned bytes to `set_screen_with_image_data()`. This is a behaviour-impacting bug.

---

### Tool: `vector_cube`
- **SDK reference section:** `anki_vector.behavior.BehaviorComponent` (lines 219–328); `anki_vector.world.World` (line 1940)
- **Methods used:**
  - `robot.world.connected_light_cube` → `LightCube`
  - `robot.behavior.dock_with_cube(cube)` (action: `dock`)
  - `robot.behavior.pickup_object(cube)` (action: `pickup`)
  - `robot.behavior.place_object_on_ground_here()` (action: `drop`)
  - `robot.behavior.roll_cube(cube)` (action: `roll`)
- **Properties valid per SDK:**
  - `world.connected_light_cube` — SDK line 1940 ✅
  - `behavior.dock_with_cube(target_object)` — SDK line 219 ✅
  - `behavior.pickup_object(target_object)` — SDK line 309 ✅
  - `behavior.place_object_on_ground_here()` — SDK line 319 ✅
  - `behavior.roll_cube(target_object)` — SDK line 289 ✅
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_lift`
- **SDK reference section:** `anki_vector.behavior.BehaviorComponent` (line 259)
- **Methods used:**
  - `robot.behavior.set_lift_height(height)`
- **Properties valid per SDK:**
  - `behavior.set_lift_height(height, ...)` — SDK line 259 ✅
- **Discrepancies:** None.
- **Recommended fix:** None.

---

### Tool: `vector_emergency_stop`
- **SDK reference section:** `anki_vector.motors.MotorComponent` (lines 854–869)
- **Methods used:**
  - `robot.motors.stop_all_motors()`
- **Properties valid per SDK:**
  - `robot.motors` → `MotorComponent` — SDK line 1271 ✅
  - `motors.stop_all_motors()` — SDK line 867 ✅
- **Discrepancies:** None.
- **Recommended fix:** None.

---

## Previously-reported Issues (now resolved)

The following discrepancies were mentioned in the original issue but are **already corrected** in the current codebase:

| Field name | Was incorrect | Now correct | Location |
|---|---|---|---|
| `is_carrying_object` | Invalid SDK field | `is_carrying_block` (SDK line 1417) | `tools_perception.py:vector_status` |
| `is_on_charger_platform` | Invalid SDK field | `is_on_charger` (SDK line 1447) | `tools_perception.py:vector_status` |

The existing tests (`test_tools_perception.py:test_vector_status`) confirm these are resolved: they assert `"is_carrying_block" in result` and `"is_carrying_object" not in result`.

---

## Discrepancy Catalogue (Phase 2 Input)

The following discrepancies are identified for Phase 2 categorisation and fix:

### HIGH — Behaviour-impacting bugs

1. **`vector_face`: Wrong image format for `set_screen_with_image_data`**
   - File: `src/vectorclaw_mcp/tools_perception.py`
   - The tool passes JPEG-encoded bytes to `set_screen_with_image_data()`. The SDK provides `convert_image_to_screen_data(pil_image)` which produces the correct rgb565 format the display driver expects.
   - Fix: Replace `img.save(buf, format="JPEG"); raw_bytes = buf.getvalue()` with `raw_bytes = anki_vector.screen.convert_image_to_screen_data(img)`.

### MEDIUM — Logic gaps (missing preconditions)

2. **`vector_list_visible_faces` and `vector_face_detection`: Face detection mode not enabled**
   - File: `src/vectorclaw_mcp/tools_perception.py`
   - Both tools read `robot.world.visible_faces` without calling `robot.vision.enable_face_detection()` first (SDK line 1894). Without this, face detection is inactive and the list will always be empty.
   - Fix: Call `robot.vision.enable_face_detection()` before reading `visible_faces`, or add documentation that this is a caller prerequisite.

3. **`vector_face_detection`: Expression estimation not enabled**
   - File: `src/vectorclaw_mcp/tools_perception.py`
   - The tool reads `f.expression` but `enable_face_detection()` defaults to `estimate_expression=False`. Expression data will be unavailable.
   - Fix: Call `robot.vision.enable_face_detection(detect_faces=True, estimate_expression=True)` instead.

### LOW — Quality / documentation gaps

4. **`vector_head`: Hardcoded angle bounds not imported from SDK constants**
   - File: `src/vectorclaw_mcp/tools_common.py`
   - `_HEAD_ANGLE_MIN = -22.0` and `_HEAD_ANGLE_MAX = 45.0` should be `anki_vector.behavior.MIN_HEAD_ANGLE` / `MAX_HEAD_ANGLE`.
   - Fix: Import constants at runtime to stay in sync with SDK.

5. **`vector_proximity_status`: `found_object` semantics**
   - File: `src/vectorclaw_mcp/tools_perception.py`
   - The field is returned correctly but its semantics ("object detected in valid operating range") should be clarified in the tool description to prevent caller misinterpretation.
   - Fix: Update tool description in `tool_registry.py`.

6. **`vector_pose`: `Position.x/y/z` not documented in SDK reference**
   - The `Position` class (SDK line 1700) has "Public methods: none" but `x`, `y`, `z` are accessed as attributes. This is consistent with how `Vector3` exposes them and almost certainly works, but the SDK reference gap is worth noting.
   - Fix: No code change needed; verify empirically.
