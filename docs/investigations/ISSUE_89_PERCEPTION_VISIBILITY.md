# Issue #89: Perception Visibility Reliability Investigation

**Status:** Investigation in progress
**Created:** 2026-02-28
**Issue:** https://github.com/danmartinez78/VectorClaw/issues/89

---

## Problem Statement

During MCP hardware smoke tests, perception query tools frequently return empty lists under conditions where positive detections are expected:

- `vector_face_detection` returns `faces: []` while robot is held in front of a human face
- `vector_list_visible_objects` returns `objects: []` with cube placed in front of robot

**Key observation:** Actuation/search commands (`vector_find_faces`, `vector_scan`) execute and move as expected, but query/result paths remain sparse or empty.

---

## Root Cause Analysis

### Finding 1: Face Detection Not Enabled by Default

**SDK behavior:** The `anki_vector.Robot` constructor defaults to `enable_face_detection=False`:

```python
def __init__(self,
             ...
             enable_face_detection: bool = False,
             estimate_facial_expression: bool = False,
             enable_custom_object_detection: bool = False,
             ...):
```

**VectorClaw implementation:** Current `robot.py` connects without enabling vision modes:

```python
robot = anki_vector.Robot(**kwargs)  # No enable_face_detection=True
robot.connect()
```

**Result:** `robot.world.visible_faces` will always be empty because face detection is disabled.

### Finding 2: Object Detection Requires Marker Detection

**SDK behavior:** Custom object detection requires explicit enablement via `enable_custom_object_detection=True` or `robot.vision.enable_custom_object_detection(True)`.

**Cube detection:** Light cubes should be detected automatically when connected, but visibility depends on:
- Cube being powered on and connected
- Cube being in robot's field of view
- Robot's internal object tracking state being up-to-date

### Finding 3: Query Timing

**SDK pattern:** The SDK uses event-based updates for perception data:
- Face observations trigger `Events.robot_observed_face`
- Object observations update `robot.world._objects` dictionary

**Issue:** If queries happen before the robot has processed the scene, results will be empty. The robot needs time to:
1. Capture camera frame
2. Run detection algorithms
3. Update world state

---

## Proposed Fixes

### Option A: Enable Vision Modes at Connection Time

**Change:** Add vision mode parameters to robot connection:

```python
# In robot.py
robot = anki_vector.Robot(
    serial=serial,
    enable_face_detection=True,
    estimate_facial_expression=True,
    enable_custom_object_detection=True,
)
```

**Pros:**
- Simple, one-time setup
- All perception tools work immediately

**Cons:**
- Always-on vision processing (higher CPU/battery on robot)
- User can't opt out if they don't need perception

### Option B: Lazy Vision Mode Enablement

**Change:** Add a tool to enable/disable vision modes on demand:

```python
def vector_enable_perception(
    enable_faces: bool = True,
    enable_objects: bool = True,
    estimate_expressions: bool = False,
) -> dict:
    robot = _robot()
    if enable_faces:
        robot.vision.enable_face_detection(True, estimate_expressions)
    if enable_objects:
        robot.vision.enable_custom_object_detection(True)
    return {"status": "ok"}
```

**Pros:**
- User controls when vision is active
- Lower resource usage when perception not needed

**Cons:**
- Requires explicit enablement step before perception queries
- More complex user experience

### Option C: Auto-Enable on First Perception Query

**Change:** Detect first perception query and enable vision modes automatically:

```python
def vector_list_visible_faces() -> dict:
    robot = _robot()
    if not robot_manager._face_detection_enabled:
        robot.vision.enable_face_detection(True)
        robot_manager._face_detection_enabled = True
    faces = [...]
    return {"status": "ok", "faces": faces}
```

**Pros:**
- Transparent to user
- Vision only enabled when needed

**Cons:**
- First query may have delayed results
- Hidden side effects

---

## Recommended Approach: Option B (Lazy Enablement)

**Rationale:**
1. Gives operator explicit control over robot resource usage
2. Clear contract: call `vector_enable_perception` before using perception tools
3. Can document expected behavior in API reference
4. Allows fine-grained control (faces only, objects only, etc.)

**Implementation plan:**
1. Add `vector_enable_perception` tool
2. Update perception tool docs to require enablement
3. Add `vector_perception_status` tool to check current state
4. Update API_REFERENCE.md with enablement contract

---

## Interim Operator Guidance

Until fix is implemented:

1. **For face detection:**
   - Run `vector_find_faces()` first (activates face search behavior)
   - Wait 2-3 seconds for robot to process scene
   - Then query `vector_list_visible_faces()` or `vector_face_detection()`

2. **For object detection:**
   - Ensure cube is powered on and connected
   - Run `vector_scan()` to prompt robot to look around
   - Wait 2-3 seconds for object tracking to update
   - Then query `vector_list_visible_objects()`

3. **Expected behavior:**
   - Empty results are normal if vision modes not enabled
   - Use search/scan behaviors as workaround to trigger detection

---

## Test Protocol

**Preconditions:**
- Robot serial: `00a1546c`
- Wire-Pod: active/running
- Human face available for testing
- Light cube powered on and connected

**Test cases:**

| Scenario | Tool Sequence | Expected Result |
|----------|---------------|-----------------|
| Faces without enablement | `vector_list_visible_faces()` | `faces: []` (current behavior) |
| Faces with scan | `vector_scan()` → wait 3s → `vector_list_visible_faces()` | May return faces |
| Faces with find_faces | `vector_find_faces()` → wait 3s → `vector_face_detection()` | May return faces |
| Objects without scan | `vector_list_visible_objects()` | May be empty |
| Objects with scan | `vector_scan()` → wait 3s → `vector_list_visible_objects()` | Should return cube if visible |

---

## Next Steps

- [ ] Validate hypotheses with hardware testing
- [ ] Decide on fix approach (A, B, or C)
- [ ] Implement chosen approach
- [ ] Update API_REFERENCE.md with perception enablement contract
- [ ] Add hardware smoke test protocol for perception validation

---

## References

- SDK docs: `anki_vector.robot.Robot.__init__` (vision mode parameters)
- SDK docs: `anki_vector.vision.VisionComponent.enable_face_detection`
- Related issues: #87 (object visibility), #85 (schema validation)
