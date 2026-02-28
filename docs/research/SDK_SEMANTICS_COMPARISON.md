# SDK Semantics Comparison: Our Research vs Copilot-Generated Doc

**Date:** 2026-02-28
**Sources:**
- Our research: `docs/research/SDK_SEMANTICS_RESEARCH.md`
- Copilot doc: `docs/API_REFERENCE_COPILOT_GENERATED.md` (upstream dev branch)

---

## Summary

Copilot's comprehensive SDK API reference (1820 lines) is **much more extensive** than our research. It provides deeper detail on coordinate systems, delocalization, face landmarks, and includes code examples throughout.

**Verdict:** Use Copilot's doc as the primary SDK reference. Our research complements it with hardware specs (FOV angles, sensor ranges) that Copilot's doc doesn't include.

---

## Topic-by-Topic Comparison

### 1. Proximity Sensor ✅ NEW INFO FOUND

| Aspect | Our Research | Copilot Doc | Winner |
|--------|--------------|-------------|--------|
| Hardware specs | ToF, 30-1200mm, 25° FOV | Time-of-flight IR sensor | **Ours** (more detail) |
| `signal_quality` | "Likelihood of solid surface" (no range) | **"0.0 (poor) to 1.0 (strong)"** | **Copilot** (answers our question!) |
| `found_object` | "Valid operating range" | "True if object detected within sensor range" | Copilot (clearer) |
| `unobstructed` | "Confirmed no object to max range" | "True if no obstacles detected (clear path ahead)" | Copilot (clearer) |

**Key finding:** `signal_quality` is 0.0-1.0 range — this was one of our open questions!

---

### 2. Pose & Coordinate System ✅ ANSWERS FOUND

| Aspect | Our Research | Copilot Doc | Winner |
|--------|--------------|-------------|--------|
| Reference frame | Robot body vs world frame (hypotheses) | **Full explanation with diagrams** | **Copilot** |
| `origin_id` | "Poses with different origin_id cannot be compared" | **Detailed delocalization explanation** | **Copilot** |
| Delocalization behavior | Unknown (flagged for empirical testing) | **"Creates new origin_id, resets pose to (0,0,0)"** | **Copilot** |
| Comparison method | None documented | **`pose.is_comparable(other_pose)`** | **Copilot** |
| Relative pose math | None | **Full formula for `define_pose_relative_this()`** | **Copilot** |

**Key finding:** Delocalization resets pose to (0,0,0) with new origin_id. Old poses become invalid for comparison. No need for empirical testing on this!

**Key finding:** `is_comparable()` method exists for safe pose comparison.

---

### 3. Face Recognition ✅ NEW INFO

| Aspect | Our Research | Copilot Doc | Winner |
|--------|--------------|-------------|--------|
| Visibility timeout | 0.8s ✅ | 0.8s ✅ | Tie |
| Enrollment | Optional for naming | Optional for naming + `name_face()` method | Copilot (more detail) |
| Expression enum | Not documented | **UNKNOWN, NEUTRAL, HAPPINESS, SURPRISE, ANGER, SADNESS** | **Copilot** |
| Face landmarks | Not documented | **left_eye, right_eye, nose, mouth outlines** | **Copilot** |
| Expression scores | Not documented | **expression_score: list[int] confidence per category** | **Copilot** |

**Key finding:** Face landmarks and expression scores available — we didn't document these.

---

### 4. Animation ✅ TIE

| Aspect | Our Research | Copilot Doc | Winner |
|--------|--------------|-------------|--------|
| Trigger vs name | Trigger = stable, name = may be removed | Same | Tie |
| Tracks | Head, lift, treads, face, audio, lights | Same + track flags explained | Copilot (more detail) |
| Prerequisite | Off charger | Not explicitly stated | **Ours** |
| `use_lift_safe` param | Not documented | **Documented** | **Copilot** |

---

### 5. Camera ✅ TIE

| Aspect | Our Research | Copilot Doc | Winner |
|--------|--------------|-------------|--------|
| Resolution | 1280 x 720 | Not stated | **Ours** |
| FOV | 90° (H) x 50° (V) | Not stated | **Ours** |
| Runtime access | `camera.config.fov_x/y` | `CameraConfig` mentioned | Tie |

---

### 6. World Model & Objects ✅ COPilot WINS

| Aspect | Our Research | Copilot Doc | Winner |
|--------|--------------|-------------|--------|
| Object types | LightCube, Charger, CustomObject | Same + detailed detection pipeline | **Copilot** |
| Visibility timeout | 0.8s ✅ | Implied via is_visible property | Tie |
| `connect_cube()` | Required | **Detailed BLE connection docs** | **Copilot** |
| Marker recognition | Brief mention | **Full pipeline explanation** | **Copilot** |

---

## Questions Resolved by Copilot Doc

| Question | Our Status | Copilot Answer |
|----------|------------|----------------|
| `signal_quality` value range? | 🔍 Empirical testing needed | **0.0 (poor) to 1.0 (strong)** |
| Delocalization behavior? | 🔍 Empirical testing needed | **New origin_id, pose resets to (0,0,0)** |
| Pose comparison safety? | 🔍 Unknown | **Use `pose.is_comparable(other)`** |
| Expression types? | 🔍 Unknown | **6 types: UNKNOWN, NEUTRAL, HAPPINESS, SURPRISE, ANGER, SADNESS** |

---

## Questions Still Need Empirical Testing

| Question | Why Copilot Doc Doesn't Answer |
|----------|-------------------------------|
| What is "valid operating range" for `found_object`? | Doc says "within sensor range" but not specific mm values |
| Where is world frame origin established? | Doc explains origin_id but not where initial origin is |
| How long does localization take after delocalization? | Not documented |

---

## Recommendations

### 1. Adopt Copilot's Doc as Primary Reference
- Much more comprehensive (1820 lines vs our ~150 lines)
- Includes code examples, math formulas, diagrams
- Answers several questions we flagged for empirical testing

### 2. Merge Our Hardware Specs Into Copilot's Doc
Add to Copilot's doc:
- Camera FOV: 90° (H) x 50° (V)
- Camera resolution: 1280 x 720
- Proximity usable range: 30-1200mm (max useful ~300mm)
- Proximity FOV: 25°

### 3. Update Our API_REFERENCE.md
- Add `signal_quality` 0.0-1.0 range
- Add `pose.is_comparable()` method reference
- Add expression enum values
- Add `use_lift_safe` animation parameter

### 4. Reduce Empirical Testing Scope
Questions resolved by Copilot doc:
- ~~`signal_quality` value range~~ → 0.0-1.0
- ~~Delocalization behavior~~ → New origin_id, pose reset
- ~~Pose comparison~~ → Use `is_comparable()`

Still need empirical testing:
- Valid operating range for `found_object` (specific mm)
- World frame origin establishment (initial position)

---

## Action Items

1. **Merge Copilot's doc into our repo** — it's already on dev branch
2. **Update our research doc** with findings from Copilot's doc
3. **Update API_REFERENCE.md** with resolved questions
4. **Reduce empirical test plan** — fewer unknowns now

---

## Conclusion

Copilot's comprehensive SDK doc is excellent and answers several questions we couldn't find in the SDK source. Our research complements it with hardware specs (FOV, ranges) that Copilot's doc doesn't include.

**Best approach:** Use Copilot's doc as the authoritative reference, supplement with our hardware specs.
