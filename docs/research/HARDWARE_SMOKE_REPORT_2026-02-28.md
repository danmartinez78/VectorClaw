# VectorClaw Hardware Smoke Report — 2026-02-28

## Scope
Full MCP → SDK → physical robot validation session focused on **test + documentation only**.
No implementation fixes were applied during this run.

- Robot: Vector-S9R3 (`00a1546c`)
- Operator model: Tachi runs commands and validates payloads; Dan verifies physical behavior.
- Environment: `VECTOR_SERIAL=00a1546c`, `.venv/bin/python`

---

## Test Coverage Matrix

### Core control + status
| Tool | Tool-path result | Physical verification | Notes |
|---|---|---|---|
| `vector_status` | PASS | N/A | Stable payload shape across runs |
| `vector_pose` | PASS (payload) | PARTIAL | Good in happy flow; delocalization not fully diagnosable from current fields |
| `vector_drive_off_charger` | PASS | PASS | Repeatedly confirmed |
| `vector_drive` | PASS | PASS (when observed) | Forward movement observed during stop-sequence setup |
| `vector_say` | PASS | PASS | Re-validated in final pass |
| `vector_lift` | PASS | PASS | Re-validated in final pass |
| `vector_head` | FAIL | N/A | `Unsupported type for comparison expected Angle` |
| `vector_emergency_stop` | PASS (tool) | PARTIAL | Returns `ok`; interrupt semantics limited by sync motion path |
| `vector_drive_on_charger` | FAIL/PARTIAL | FAIL/PARTIAL | Timeout path observed; motors stopped fallback |

### Camera / image
| Tool | Tool-path result | Physical verification | Artifact |
|---|---|---|---|
| `vector_capture_image` | PASS | PASS | `hardware_test_2026-02-28/capture_144236.jpg` |
| `vector_look` | PASS | PASS | `hardware_test_2026-02-28/look_153359.jpg` |

### Touch / charger
| Tool | Tool-path result | Physical verification | Notes |
|---|---|---|---|
| `vector_touch_status` (no touch) | PASS | PASS | `is_being_touched=false` |
| `vector_touch_status` (touching) | PASS | PASS | `is_being_touched=true` |
| `vector_charger_status` (off charger) | PASS | PASS | Negative case validated |
| `vector_charger_status` (on charger) | PASS | PASS (earlier in run) | Positive case seen earlier in session |

### Perception
| Tool | Tool-path result | Physical verification | Notes |
|---|---|---|---|
| `vector_scan` | PASS | PARTIAL | Command executes; movement context-dependent on charger state |
| `vector_find_faces` | PASS | FAIL/PARTIAL | Path executes, no detections surfaced |
| `vector_list_visible_faces` | PASS | FAIL | `faces: []` under favorable conditions |
| `vector_face_detection` | PASS | FAIL | `face_count: 0` under favorable conditions |
| `vector_list_visible_objects` | PASS | FAIL | `objects: []` with nearby cube |
| `vector_vision_reset` | PASS | PASS | Returned cleanly |

Additional runtime observation during perception attempts:
- `events.EventHandler ERROR Event callback exception: object_id`

---

## Proximity Empirical Results

### Conditions tested
Far, Mid, Close, Mid (larger cardboard), Close (cardboard touching), No-object clear path.

| Condition | distance_mm | signal_quality | unobstructed | found_object |
|---|---:|---:|:---:|:---:|
| Far object | 180.0 | 0.0317 | false | false |
| Mid object | 92.0 | 0.4383 | false | false |
| Close object | 42.0 | 6.1456 | false | false |
| Mid (larger cardboard) | 97.0 | 1.4551 | false | false |
| Close (touching) | 48.0 | 11.6966 | false | false |
| No-object clear path | 244.0 | 0.0060 | true | false |

### Documented findings
1. `found_object` did not flip true in tested object-present scenarios (current setup reliability concern).
2. `signal_quality` exceeded 1.0 significantly (observed up to ~11.7).
3. `unobstructed` behaved as expected in clear-path case.

---

## Pose / Delocalization Empirical Notes

### What was observed
- Docked baseline was near `(0,0,0)` in some runs.
- Other docked baselines were non-zero in later runs.
- Pickup/setdown cycles changed pose values, but current output lacks metadata needed for robust frame-change diagnosis.

### Why classification is PARTIAL
`vector_pose` currently outputs `x/y/z/angle_deg` only.
Missing frame/state metadata (`origin_id`, `is_picked_up`, optional `localized_to_object_id`) limits delocalization diagnostics.

Related tracking: issue #128.

---

## Confirmed Distinction: `vector_look` vs `vector_capture_image`

From implementation + SDK mapping:
- `vector_look` path uses `camera.init_camera_feed()` + `camera.latest_image` (feed-based snapshot).
- `vector_capture_image` path uses `camera.capture_single_image()` (one-shot capture).

Both paths were validated in this smoke run with saved artifacts.

### Important user-facing requirement (for autonomy workflows)
Camera tools alone only provide image bytes (`image_base64`). To achieve "look → reason → act" behavior, deployment must include a **VLM or separate image-analysis model/tool** in the agent loop.

- Without a vision-capable model/tool: images can be captured but not semantically interpreted.
- With a vision-capable model/tool: agent can convert image data into actionable scene understanding.

This requirement should be explicitly documented in README/release notes so users do not assume that camera capture tools alone provide perception intelligence.

---

## Known Limitations (as tested)

1. `vector_head` currently fails due to Angle comparison type error.
2. Perception detections (faces/objects) are currently non-functional in smoke despite favorable setup.
3. `vector_drive_on_charger` is timeout-prone in this run.
4. Emergency-stop practical utility is constrained by synchronous motion call semantics for true mid-command interruption tests.
5. Pose output is useful for happy flow but insufficient for full delocalization diagnostics without additional metadata.

---

## Evidence Locations

- `docs/HARDWARE_SMOKE_LOG.md` (chronological run log)
- `docs/research/SDK_SEMANTICS_RESEARCH.md` (semantic findings + empirical table)
- Camera artifacts:
  - `hardware_test_2026-02-28/capture_144236.jpg`
  - `hardware_test_2026-02-28/look_153359.jpg`
