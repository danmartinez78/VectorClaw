# SDK Semantics Research

**Status:** In Progress
**Created:** 2026-02-28
**Issue:** #115

---

## Purpose

Investigate SDK semantics that are unclear from the surface doc alone. Document findings for API documentation updates.

---

## Research Method

1. **SDK source investigation** - Read `.venv/lib/python3.11/site-packages/anki_vector/`
2. **Code comments/docstrings** - Extract semantic explanations
3. **Examples** - Look for usage patterns
4. **Empirical testing** - For things we can't determine from code

---

## Findings

### Pose Reference Frame 🔍 INVESTIGATING

**Source:** `anki_vector/util.py` - `class Pose`

**Two different pose concepts:**

| Type | Reference Frame | Use Case |
|------|-----------------|----------|
| **Object pose** | Robot body frame | "Cube is 100mm forward of me" |
| **Robot pose** | World frame (instantiated at init) | "I've moved 200mm from where I started" |

**Robot body frame:**
- Origin: Point on ground between Vector's two front wheels
- X: forward, Y: left, Z: up
- Units: millimeters

**World frame (for robot pose) — HYPOTHESES:**

| Hypothesis | Description | Test Method |
|------------|-------------|-------------|
| **Dock-referenced** | World origin at charger dock (detectable marker) | Check pose after dock approach |
| **Init-referenced** | World origin at connection/localization time | Check pose immediately after connect |
| **Delocalization-reset** | New world frame each time robot is picked up | Pick up, put down, check origin_id |

**Delocalization (kidnapped robot problem):**
- Robot picked up → loses tracking
- SDK term: "delocalized"
- `origin_id` increments
- **Unknown:** Does world frame reset? Do cached poses become invalid?

**Critical caveat:**
> "Only poses of the same origin_id can safely be compared or operated on."

**Open questions:**
- [ ] Is the charger dock the world frame origin? (makes sense — visual marker, robot starts there)
- [ ] When is world frame first established? (dock? connection? first localization?)
- [ ] Does picking up robot reset world frame to (0,0,0)?
- [ ] Can we detect delocalization via `origin_id` changes?
- [ ] How long does localization take after being set down?
- [ ] Do object poses (LightCube, charger) share the same world frame?

---

### Visibility Timeout ✅ SOLVED

**Source:** `anki_vector/objects.py`, `anki_vector/faces.py`

**Constants:**
- `OBJECT_VISIBILITY_TIMEOUT = 0.8` seconds
- `FACE_VISIBILITY_TIMEOUT = OBJECT_VISIBILITY_TIMEOUT` (same value)

**Behavior:**
Objects and faces remain "visible" for 0.8 seconds after last observation. After that, they're removed from `visible_objects` / `visible_faces`.

---

### Proximity Sensor Semantics ✅ PARTIALLY SOLVED

**Source:** `anki_vector/proximity.py` (176 lines)

#### Hardware Specs (from module docstring, lines 16-20)
```
File: .venv/lib/python3.11/site-packages/anki_vector/proximity.py
Lines: 16-20
Type: Module docstring
```
- **Sensor type:** Time-of-flight distance sensor
- **Usable range:** 30 mm to 1200 mm
- **Max useful range:** "closer to 300mm for Vector"
- **Field of view:** 25 degrees
- **Location:** Near bottom of Vector, between two front wheels, facing forward

#### Field Semantics (from class docstrings, lines 31-116)

| Field | Type | Definition | Source Lines |
|-------|------|------------|--------------|
| `distance` | `Distance` | "distance between the sensor and a detected object" | 50-60 |
| `signal_quality` | `float` | "likelihood of the reported distance being a solid surface" | 62-74 |
| `unobstructed` | `bool` | "sensor has confirmed it has not detected anything up to its max range" | 76-86 |
| `found_object` | `bool` | "sensor detected an object in the valid operating range" | 88-98 |
| `is_lift_in_fov` | `bool` | "lift is blocking the time-of-flight sensor" | 100-116 |

#### Update Mechanism (lines 119-176)
```
File: .venv/lib/python3.11/site-packages/anki_vector/proximity.py
Lines: 119-176
Type: ProximityComponent class
```
- Updated with every broadcast `RobotState`
- Subscribe to `Events.robot_state`
- `last_sensor_reading` property returns `ProximitySensorData`

#### Answered Questions

| Question | Answer | Source |
|----------|--------|--------|
| Max range for `unobstructed`? | ~1200 mm (usable range per module doc) | Lines 16-20 |
| Sensor location? | Between front wheels, facing forward | Lines 23-24 |
| Field of view? | 25 degrees | Line 18 |
| Update frequency? | Every RobotState broadcast | Lines 145-146 |

#### Open Questions (Need Empirical Testing)

| Question | Test Method | Priority |
|----------|-------------|----------|
| What is "valid operating range" for `found_object`? | Place object at various distances, observe `found_object` flag | HIGH |
| `signal_quality` value range? | Observe values across different surfaces/distances | MEDIUM |
| Can `found_object` and `unobstructed` both be false? | Edge case testing | MEDIUM |
| Does `signal_quality` correlate with surface type? | Test different materials (matte, glossy, dark, light) | LOW |

---

---

### Visible Objects ✅ SOLVED

**Source:** `anki_vector/objects.py` (1782 lines), `anki_vector/world.py` (899 lines)

#### Object Types (from module docstring, lines 16-35)
```
File: .venv/lib/python3.11/site-packages/anki_vector/objects.py
Lines: 16-35
Type: Module docstring
```
- **LightCube** — Ships with robot, BLE connection, controllable lights, tap/move sensors
- **Charger** — Robot's charging dock
- **CustomObject** — User-created objects with printed markers
- **FixedCustomObject** — Fixed objects defined by SDK

**Marker requirement:**
> "All observable objects have a marker of a known size attached to them, which allows Vector to recognize the object and its position and rotation ('pose')."

#### `visible_objects` Implementation
```
File: .venv/lib/python3.11/site-packages/anki_vector/world.py
Lines: 199-213
Type: Property method
```
```python
def visible_objects(self) -> Iterable[objects.ObservableObject]:
    """A generator yielding Charger, LightCube and CustomObject instances"""
    for obj in self._objects.values():
        if obj.is_visible:
            yield obj
```

**Behavior:**
- Yields objects where `obj.is_visible` is `True`
- Visibility expires after `OBJECT_VISIBILITY_TIMEOUT = 0.8` seconds
- Requires object to be observed within last 0.8s

#### `connect_cube` Requirement
```
File: .venv/lib/python3.11/site-packages/anki_vector/world.py
Lines: 345-367
Type: Async method
```
```python
async def connect_cube(self) -> protocol.ConnectCubeResponse:
    """Attempt to connect to a cube. If a cube is currently connected, this will do nothing."""
```

**Critical:** LightCube will NOT appear in `visible_objects` until `connect_cube()` is called.

#### Answered Questions

| Question | Answer | Source |
|----------|--------|--------|
| What object types appear in `visible_objects`? | LightCube, Charger, CustomObject | world.py:205 |
| Visibility timeout? | 0.8 seconds | objects.py:60 |
| Why is cube not visible? | Must call `connect_cube()` first | world.py:345 |
| How are objects recognized? | Visual markers of known size | objects.py:28-30 |

---

### Visible Faces ✅ SOLVED

**Source:** `anki_vector/faces.py` (819 lines)

#### Face Recognition & Enrollment
```
File: .venv/lib/python3.11/site-packages/anki_vector/faces.py
Lines: 16-26
Type: Module docstring
```
- Vector can recognize human faces, track pose, assign names via enrollment
- Face names persist between SDK runs
- Enrollment distance: 1.5 to 2 feet (lines 277)

#### `visible_faces` Implementation
```
File: .venv/lib/python3.11/site-packages/anki_vector/world.py
Lines: 109-150
Type: Property method
```
- Requires `enable_face_detection=True` in `Robot()` constructor
- Visibility expires after `FACE_VISIBILITY_TIMEOUT = 0.8` seconds

#### Face Properties (from Face class, lines 211+)
```
File: .venv/lib/python3.11/site-packages/anki_vector/faces.py
Lines: 211-224, 448
Type: Class docstring
```
- `face_id` — Unique identifier
- `name` — Enrolled name (empty if not recognized/enrolled)
- `expression` — Detected expression
- `pose` — Position and rotation
- `last_observed_time` — Timestamp of last observation
- `last_observed_image_rect` — Location in camera view

#### Enrollment Behavior
```
File: .venv/lib/python3.11/site-packages/anki_vector/faces.py
Lines: 273-318
Type: Method docstring
```
- `face.request_enrollment(name)` — Enroll face with name
- Enrollment requires looking at Vector straight-on at 1.5-2 feet
- Names persist across SDK sessions

#### Answered Questions

| Question | Answer | Source |
|----------|--------|--------|
| Does face detection require enrollment? | No — detects faces, enrollment is for naming | faces.py:214-215 |
| Visibility timeout? | 0.8 seconds | faces.py:45 |
| Does `name` persist? | Yes — across SDK runs | faces.py:18 |
| Prerequisite? | `enable_face_detection=True` in Robot() | world.py:123 |

#### Empirical Test Needed

| Question | Test Method | Priority |
|----------|-------------|----------|
| Does expression detection require `estimate_expression=True`? | Check expression field with/without flag | HIGH |
| How many faces can be tracked simultaneously? | Show multiple faces, observe behavior | MEDIUM |

---

### Animation Semantics ✅ SOLVED

**Source:** `anki_vector/animation.py` (272 lines)

#### Two Ways to Play Animations (lines 18-25)
```
File: .venv/lib/python3.11/site-packages/anki_vector/animation.py
Lines: 18-25
Type: Module docstring
```

| Method | Behavior | Stability |
|--------|----------|-----------|
| `play_animation_trigger(name)` | Robot picks from pre-defined group | ✅ Stable across OS versions |
| `play_animation(name)` | Plays exact specific animation | ⚠️ Animations can be renamed/removed |

**SDK recommendation:**
> "We advise you to use play_animation_trigger instead of play_animation, since individual animations can be deleted between Vector OS versions."

#### Trigger Behavior (lines 104-114)
```
File: .venv/lib/python3.11/site-packages/anki_vector/animation.py
Lines: 104-114
Type: Property docstring
```
- Trigger = pre-defined group of animations
- Robot picks which animation to play based on:
  - Vector's mood or emotion
  - Random weighting
- **Same trigger may play different animations** — not deterministic

#### Animation Tracks (lines 16-17)
```
File: .venv/lib/python3.11/site-packages/anki_vector/animation.py
Lines: 16-17
Type: Module docstring
```
Animations control 6 tracks:
1. **Head** — Head movement
2. **Lift** — Lift/arm movement
3. **Treads** — Wheel movement
4. **Face** — Screen display
5. **Audio** — Sounds
6. **Backpack lights** — LED patterns

**Track filtering:** Can ignore specific tracks via `ignore_body_track`, `ignore_head_track`, `ignore_lift_track`

#### Prerequisites (lines 213-214)
```
File: .venv/lib/python3.11/site-packages/anki_vector/animation.py
Lines: 213-214
Type: Method docstring
```
> "Vector must be off of the charger to play an animation."

#### Lazy Loading (lines 58-100)
- Animation lists loaded on first access
- Can pre-load with `load_animation_list()` / `load_animation_trigger_list()`
- Lists are dynamically retrieved from robot at connection time

#### Answered Questions

| Question | Answer | Source |
|----------|--------|--------|
| Trigger vs animation? | Trigger = group, animation = specific | Lines 18-25 |
| Which to use? | Triggers recommended (more stable) | Lines 22-24 |
| Are triggers deterministic? | No — robot picks based on mood/random | Lines 108-112 |
| Prerequisite? | Robot must be off charger | Lines 213-214 |
| What tracks do animations control? | Head, lift, treads, face, audio, lights | Lines 16-17 |

---

### Camera FOV ✅ SOLVED

**Source:** `anki_vector/camera.py`

#### Hardware Specs (from module docstring, line 24)
```
File: .venv/lib/python3.11/site-packages/anki_vector/camera.py
Line: 24
Type: Module docstring
```
- **Resolution:** 1280 x 720
- **Field of View:** 90° (H) x 50° (V)

#### Runtime Access (lines 240-247)
```
File: .venv/lib/python3.11/site-packages/anki_vector/camera.py
Lines: 240-247
Type: Property methods
```
- `camera.config.fov_x` — Horizontal FOV as `Angle`
- `camera.config.fov_y` — Vertical FOV as `Angle`

#### Answered Questions

| Question | Answer | Source |
|----------|--------|--------|
| Camera resolution? | 1280 x 720 | camera.py:24 |
| Horizontal FOV? | 90° | camera.py:24 |
| Vertical FOV? | 50° | camera.py:24 |
| Runtime access? | `camera.config.fov_x`, `fov_y` | camera.py:240-247 |

---

## Research Summary

### ✅ Fully Solved
| Topic | Key Finding |
|-------|-------------|
| Visibility timeout | 0.8 seconds for objects and faces |
| Visible object types | LightCube, Charger, CustomObject |
| Cube visibility | Requires `connect_cube()` call |
| Face visibility | Requires `enable_face_detection=True` |
| Face enrollment | Optional — for naming, not detection |
| Proximity sensor hardware | ToF, 30-1200mm range, 25° FOV |
| Animation trigger vs name | Trigger = group (stable), name = specific (may be removed) |
| Animation prerequisite | Robot must be off charger |
| Animation tracks | Head, lift, treads, face, audio, backpack lights |
| Camera resolution | 1280 x 720 |
| Camera FOV | 90° (H) x 50° (V) |

### 🔍 Partially Solved (Empirical Testing Needed)
| Topic | Remaining Question | Test Method |
|-------|-------------------|-------------|
| Proximity sensor | Valid operating range for `found_object` | Distance testing |
| Proximity sensor | `signal_quality` value range | Surface/distance testing |
| Face detection | Expression detection flag requirement | Test with/without `estimate_expression` |
| Pose reference frame | World frame origin, delocalization behavior | Pick up robot, observe pose/origin_id |

---

## Research Log

### 2026-02-28 13:35 CST
**Completed SDK source investigation for:**
- Proximity sensor — hardware specs, field semantics, update mechanism
- Visible objects — types, visibility timeout, `connect_cube()` requirement
- Visible faces — prerequisites, enrollment, properties
- Animation semantics — trigger vs name, tracks, prerequisites
- Camera FOV — resolution, horizontal/vertical FOV

**All findings include exact source citations (file, lines, type).**

**Empirical testing flagged for:**
- Proximity sensor operating range
- `signal_quality` value range
- Expression detection flag requirement
- Pose reference frame (world origin, delocalization)

### 2026-02-28 13:15 CST
- Found `OBJECT_VISIBILITY_TIMEOUT = 0.8` in SDK source
- Found pose reference frame documentation in `util.py`
- Discovered `origin_id` concept for pose validity

---

## Output Plan

1. Update `docs/API_REFERENCE.md` with semantic clarifications
2. Consider adding `docs/SDK_SEMANTICS.md` for deeper explanations
3. Close issue #115 when documentation is complete
