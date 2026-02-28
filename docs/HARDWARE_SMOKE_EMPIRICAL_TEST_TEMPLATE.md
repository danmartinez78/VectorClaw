# Hardware Smoke Test + Empirical Investigation Checklist

**Date:** 2026-02-28
**Target:** Validate tools + answer open questions → v1.0.0 release

---

## Pre-flight

- [ ] Wire-Pod server running
- [ ] Robot powered on, Wi-Fi connected
- [ ] `VECTOR_SERIAL` env var set
- [ ] Clear flat surface (≥60cm × 60cm)
- [ ] LightCube available and powered on
- [ ] Operator ready to record observations

---

## Phase 1: Core Tool Validation

### Connectivity
| # | Command | Expected | Pass? |
|---|---------|----------|-------|
| 1.1 | `vector_status` | JSON with battery_level, is_charging | [ ] |
| 1.2 | `vector_pose` | JSON with x, y, z, angle_deg | [ ] |

### Motion (start on charger)
| # | Command | Expected | Pass? |
|---|---------|----------|-------|
| 2.1 | `vector_drive_off_charger` | Robot drives off charger | [ ] |
| 2.2 | `vector_drive` (150mm, 50) | Forward ~15cm | [ ] |
| 2.3 | `vector_drive` (-150mm, 50) | Backward ~15cm | [ ] |
| 2.4 | `vector_drive` (90°) | Turn left ~90° | [ ] |
| 2.5 | `vector_drive` (-90°) | Turn right ~90° | [ ] |

### Speech
| # | Command | Expected | Pass? |
|---|---------|----------|-------|
| 3.1 | `vector_say` ("Test one") | Audible TTS | [ ] |

### Camera
| # | Command | Expected | Pass? |
|---|---------|----------|-------|
| 4.1 | `vector_look` | Non-empty image_base64 | [ ] |

### Proximity (NEW FIELDS!)
| # | Command | Expected | Pass? |
|---|---------|----------|-------|
| 5.1 | `vector_proximity_status` | distance_mm, signal_quality, unobstructed, found_object, is_lift_in_fov | [ ] |
| 5.2 | Place hand 50mm in front | distance_mm ~50, found_object behavior? | [ ] |

### Perception
| # | Command | Expected | Pass? |
|---|---------|----------|-------|
| 6.1 | `vector_list_visible_objects` (cube visible) | Returns cube | [ ] |
| 6.2 | `vector_list_visible_faces` (face visible) | Returns face | [ ] |

### Animation
| # | Command | Expected | Pass? |
|---|---------|----------|-------|
| 7.1 | `vector_animate` ("anim_greeting_happy_01") | Animation plays | [ ] |

---

## Phase 2: Empirical Investigation

### A. Pose Reference Frame

**Questions to answer:**
1. Where is initial world frame origin established?
2. What happens when robot is picked up (delocalization)?

**Test protocol:**

| Step | Action | Observe | Record |
|------|--------|---------|--------|
| A1 | Start robot on charger | `vector_pose` → x, y, z, angle_deg | (0, 0, 0)? or other? |
| A2 | Drive off charger, forward 200mm | `vector_pose` → x, y, z | x ≈ 200? |
| A3 | Pick up robot, set down elsewhere | `vector_pose` → x, y, z, origin_id | origin_id changed? pose reset? |
| A4 | Drive to charger, dock | `vector_pose` after dock | Does pose correlate with dock position? |

**Hypotheses to validate:**
- [ ] Dock-referenced: World origin at charger dock
- [ ] Init-referenced: World origin at connection time
- [ ] Delocalization-reset: New origin_id when picked up

### B. Proximity Sensor Operating Range

**Questions to answer:**
1. What is "valid operating range" for `found_object` (specific mm)?
2. At what distance does `found_object` flip from false to true?

**Test protocol:**

| Step | Action | Observe | Record |
|------|--------|---------|--------|
| B1 | Place object at 30mm | distance_mm, found_object, signal_quality | |
| B2 | Place object at 100mm | distance_mm, found_object, signal_quality | |
| B3 | Place object at 200mm | distance_mm, found_object, signal_quality | |
| B4 | Place object at 300mm | distance_mm, found_object, signal_quality | |
| B5 | Place object at 400mm | distance_mm, found_object, signal_quality | |
| B6 | No object (open space) | distance_mm, found_object, unobstructed | |

**Record threshold:** At what mm does `found_object` first become true?

---

## Phase 3: Findings → Updates

Based on empirical results:

- [ ] Update API_REFERENCE.md with pose reference frame clarification
- [ ] Update API_REFERENCE.md with proximity operating range
- [ ] Update SDK_SEMANTICS_RESEARCH.md with empirical findings
- [ ] Create any needed bug fix issues

---

## Exit Criteria

- [ ] All Phase 1 tools validated
- [ ] Pose reference frame question answered
- [ ] Proximity operating range question answered
- [ ] Docs updated with findings

**Then:** Proceed to CHANGELOG.md → v1.0.0 release
