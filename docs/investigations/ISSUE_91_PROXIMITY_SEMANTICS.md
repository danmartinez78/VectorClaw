# Issue #91: Wire-Pod SDK Object-Detection Semantics Investigation

**Status:** Investigation complete
**Created:** 2026-02-28
**Issue:** https://github.com/danmartinez78/VectorClaw/issues/91

---

## Summary

This investigation clarifies the semantics of the proximity sensor fields in the Wire-Pod SDK, specifically the relationship between raw proximity sensing and engine-level object detection/classification flags.

---

## SDK Proximity Sensor Contract

**Source:** `anki_vector.proximity.ProximitySensorData`

| Field | Type | Description |
|-------|------|-------------|
| `distance` | `Distance` | Distance to detected object (in mm) |
| `signal_quality` | `float` | Likelihood of reported distance being a solid surface |
| `unobstructed` | `bool` | Sensor confirmed NO detection up to max range |
| `found_object` | `bool` | Sensor detected object in valid operating range |
| `is_lift_in_fov` | `bool` | Lift is blocking the time-of-flight sensor |

---

## Key Semantic Distinctions

### 1. `distance` vs `found_object`

**`distance.distance_mm`:**
- Raw time-of-flight sensor reading
- Returns a numeric value regardless of whether an "object" is detected
- May return valid distance even when `found_object=False`

**`found_object`:**
- Engine-level classification
- True when sensor detects object in **valid operating range**
- Depends on confidence/quality thresholds
- May be false even when distance changes (e.g., low-quality return)

### 2. `unobstructed` vs `found_object`

These are **mutually exclusive** in ideal conditions:
- `unobstructed=True` → Confirmed no object up to max range
- `found_object=True` → Object detected in valid range
- Both `False` → Uncertain state (low signal quality, edge case)

### 3. `is_lift_in_fov` Implications

When `is_lift_in_fov=True`:
- Lift is blocking the proximity sensor
- Distance readings may be valid but **not useful for object detection**
- Should be filtered out for navigation/object detection purposes

---

## Hardware Observations (2026-02-27 Smoke)

**Test:** `vector_proximity_status` with object placed in front of robot

| Observation | Expected | Actual |
|-------------|----------|--------|
| `distance_mm` changed | ~279mm → ~45mm | ✅ Worked |
| `found_object` flipped to true | True | ❌ Remained false |

**Interpretation:**
- Raw distance sensing works correctly
- `found_object` depends on additional engine-level criteria beyond simple distance change
- Possible causes:
  - Signal quality below threshold
  - Object type not recognized as "valid"
  - Lift position affecting sensor
  - Firmware-level detection logic

---

## Relationship to `visible_objects`

**Proximity sensor (`vector_proximity_status`):**
- Time-of-flight distance measurement
- Single direction (forward-facing)
- Real-time, always available
- Does NOT populate `robot.world.visible_objects`

**Object tracking (`vector_list_visible_objects`):**
- Camera-based object recognition
- Requires vision modes enabled
- Populates `robot.world.visible_objects`
- Includes LightCube, Charger, CustomObjects

**Key insight:** These are **independent systems**. Proximity sensor provides distance data; vision system provides object classification. They do not automatically cross-reference.

---

## Tool Guidance

### `vector_proximity_status`

**Use for:**
- Obstacle avoidance (raw distance)
- Near-field object detection
- Stop-on-approach behaviors

**Do NOT assume:**
- `found_object=True` means object is in `visible_objects`
- Distance reading implies object classification

**Recommended pattern:**
```python
prox = robot.proximity.last_sensor_reading
if prox.is_lift_in_fov:
    # Skip - lift blocking sensor
    return
if prox.distance.distance_mm < 100:
    # Close object detected (use raw distance)
    ...
```

### `vector_list_visible_objects`

**Use for:**
- Identifying specific objects (cube, charger)
- Object-relative navigation
- Docking/pickup behaviors

**Requires:**
- Vision modes enabled (see #89)
- Recent scan of environment

---

## Test Matrix for Future Validation

| Condition | `distance_mm` | `found_object` | `signal_quality` | `unobstructed` |
|-----------|---------------|----------------|------------------|----------------|
| Open space | ~400mm | False | Low | True |
| Hand at 50mm | ~50mm | Varies | High | False |
| Wall at 200mm | ~200mm | True? | High | False |
| Lift raised | Varies | False | Varies | False |
| Dark room | Varies | False | Low | Varies |

**Note:** This matrix should be populated with actual hardware testing.

---

## Recommendations

### For VectorClaw Docs

1. **Clarify `found_object` semantics** in `vector_proximity_status` docs
2. **Document independence** from `visible_objects` system
3. **Add `is_lift_in_fov` check** to usage guidance

### For Tool Contract

Current implementation is correct - returns all fields as-is. No code changes needed, only documentation.

---

## References

- SDK source: `anki_vector/proximity.py`
- Protocol: `anki_vector/messaging/messages.proto` → `ProxData`
- Hardware smoke log: `docs/HARDWARE_SMOKE_LOG.md`
- Issue: https://github.com/danmartinez78/VectorClaw/issues/91
