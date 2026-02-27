# Wire-Pod SDK → MCP Integration Priorities

Purpose: convert the full SDK surface into an actionable MCP roadmap.

Source catalog: `WIREPOD_SDK_SURFACE_REFERENCE.md`

## Decision rubric

- **MCP Value**: High / Medium / Low
- **Risk**: Low / Medium / High
- **Integration shape**:
  - **Direct** = one SDK call maps to one MCP tool
  - **Composed** = multiple SDK calls/state checks in one MCP tool
- **Decision**:
  - **Now** = include in current implementation wave
  - **Later** = useful but defer
  - **Skip** = not currently worth exposing

---

## Section 1 — Behavior + World (highest leverage)

| SDK Surface | Use Case | MCP Value | Risk | Shape | Proposed MCP Tool | Decision | Notes |
|---|---|---:|---:|---|---|---|---|
| `behavior.drive_on_charger` | Return robot to charger | High | Medium | Composed | `vector_drive_on_charger` | Now (experimental) | High lifecycle value; implement with explicit best-effort semantics, timeout, and actionable fallback errors. |
| `behavior.drive_off_charger` | Leave charger before motion | High | Low | Direct | `vector_drive_off_charger` | Now (already) | Keep as core precondition helper. |
| `behavior.go_to_pose` | Relative/absolute movement goal | High | High | Composed | `vector_go_to_pose` | Later | Requires strong safety envelope and robust coordinate assumptions. |
| `behavior.go_to_object` | Move to visible object | Medium | Medium | Composed | `vector_go_to_object` | Later | Needs object identity + visibility checks. |
| `behavior.look_around_in_place` | Active scan behavior | Medium | Low | Direct | `vector_scan` | Now | Useful for perception workflows and human-observable behavior. |
| `behavior.find_faces` | Trigger face search | Medium | Low | Direct | `vector_find_faces` | Now | Pairs naturally with `world.visible_faces`. |
| `behavior.turn_towards_face` | Orient to detected face | Medium | Medium | Composed | `vector_turn_towards_face` | Later | Depends on stable face target selection. |
| `behavior.set_eye_color` | UX/personality feedback | Medium | Low | Direct | `vector_set_eye_color` | Now | Low risk, high UX payoff. |
| `behavior.change_locale` / `say_localized_text` | Localized interaction | Low | Medium | Direct | `vector_set_locale` / `vector_say_localized` | Skip | Nice-to-have; not core to v1 operator control. |
| `behavior.pickup_object` / `place_object_on_ground_here` | Object manipulation | Medium | High | Composed | `vector_pickup_cube` / `vector_place_object` | Later | Requires robust object state checks and safety constraints. |
| `behavior.roll_cube` / `roll_visible_cube` | Cube interaction | Low | Medium | Direct | `vector_roll_cube` | Later | Keep after core mobility + sensing hardening. |
| `world.visible_faces` | Face list for decisioning | High | Low | Direct | `vector_list_visible_faces` | Now | Strong utility for composed behavior tools. |
| `world.visible_objects` / `visible_custom_objects` | Object awareness | High | Medium | Direct | `vector_list_visible_objects` | Now | Key for planning and safe action gating. |
| `world.charger` | Charger object state | High | Low | Direct | `vector_charger_status` | Now | Enables smarter charger workflows. |
| `world.connect_cube` / `disconnect_cube` | Cube pairing control | Medium | Medium | Direct | `vector_connect_cube` / `vector_disconnect_cube` | Later | Useful but not blocking for current milestones. |
| `world.get_object` / `get_face` | Query specific entity | Medium | Medium | Direct | `vector_get_object` / `vector_get_face` | Later | Add when identity lifecycle is clearly modeled. |

---

## Section 2 — Camera + Vision

| SDK Surface | Use Case | MCP Value | Risk | Shape | Proposed MCP Tool | Decision | Notes |
|---|---|---:|---:|---|---|---|---|
| `camera.capture_single_image` | Deterministic capture | High | Low | Direct | `vector_capture_image` | Now | Preferred over implicit latest-frame reads. |
| `camera.latest_image` / `latest_image_id` | Fast current frame access | High | Low | Direct | `vector_look` (existing) + metadata | Now | Add optional metadata payload for traceability. |
| `camera.set_manual_exposure` / `enable_auto_exposure` / `gain` | Improve image quality | Medium | Medium | Direct | `vector_camera_exposure` | Later | Great for difficult lighting, but tune carefully. |
| `vision.enable_face_detection` / `detect_faces` | Face detection control | High | Medium | Composed | `vector_face_detection` | Now | Start with summarized detections (stable payload), avoid raw/heavy streaming output initially. |
| `vision.enable_motion_detection` / `detect_motion` | Motion trigger workflows | Medium | Medium | Composed | `vector_motion_detection` | Later | Useful for reactive behaviors, not core operator path. |
| `vision.enable_custom_object_detection` | Custom object detection | Medium | High | Composed | `vector_custom_object_detection` | Later | Needs object definition pipeline and calibration docs. |
| `vision.display_camera_feed_on_face` | UX/display behavior | Low | Low | Direct | `vector_face_camera_feed` | Skip | Cool demo, low operational value. |
| `vision.disable_all_vision_modes` | Reset/safety cleanup | Medium | Low | Direct | `vector_vision_reset` | Now | Good hygiene tool after detection sessions. |

---

## Next sections to complete

- *(all core sections now covered; refine decisions and start implementation batching)*

---

## Section 7 — Events / Streaming Patterns

| SDK Surface | Use Case | MCP Value | Risk | Shape | Proposed MCP Tool | Decision | Notes |
|---|---|---:|---:|---|---|---|---|
| `robot.events` + event subscriptions | Reactive workflows from robot events | Medium | High | Composed | `vector_event_subscribe` / `vector_wait_for_event` | Later | Powerful but requires lifecycle management, cancellation semantics, and timeout discipline in MCP context. |
| camera feed streaming (`camera.init_camera_feed`, viewer patterns) | Continuous perception stream | Medium | High | Composed | `vector_camera_stream_start/stop` | Later | High bandwidth/state complexity; defer until stable single-shot capture workflows are complete. |
| audio feed enable (`robot.enable_audio_feed`) | Continuous audio stream processing | Low | High | Composed | `vector_audio_stream_start/stop` | Skip | Not needed for current milestones; increases complexity and policy surface area. |
| nav map / continuous mapping signals | Advanced navigation context | Low | High | Composed | `vector_nav_stream` | Skip | Better aligned with future ROS2/navigation milestone, not v1 MCP scope. |

---

## Section 6 — Photos + Faces + Sensors + Status

| SDK Surface | Use Case | MCP Value | Risk | Shape | Proposed MCP Tool | Decision | Notes |
|---|---|---:|---:|---|---|---|---|
| `photos.load_photo_info` / `photo_info` / `get_photo` / `get_thumbnail` | Retrieve robot photo artifacts | Medium | Medium | Direct | `vector_list_photos`, `vector_get_photo` | Later | Useful, but not core to immediate control loop; adds storage/index selection complexity. |
| `faces.request_enrolled_names` | Known-face identity context | Medium | Low | Direct | `vector_list_enrolled_faces` | Later | Useful context but not blocking for current milestone. |
| `faces.update_enrolled_face_by_id` / erase methods | Face identity mutation | Low | Medium | Direct | `vector_update_face`, `vector_delete_face` | Skip | Defer mutable/destructive identity operations until explicit confirmation UX exists. |
| `touch.last_sensor_reading` | Contact/touch interaction state | Medium | Low | Direct | `vector_touch_status` | Now | Lightweight interaction signal for reactive behavior. |
| `proximity.last_sensor_reading` | Nearby obstacle/range awareness | High | Low | Direct | `vector_proximity_status` | Now | High value safety/context signal for composed movement logic. |
| `robot.status` (expanded fields) | Unified operational observability | Very High | Low | Direct | `vector_status` (expanded) | Now | Core state payload should grow to support composed tools and safety gates. |
| `robot.get_battery_state` / `get_version_state` | Health + runtime compatibility context | High | Low | Direct | `vector_battery_status`, `vector_version_status` (or fold into `vector_status`) | Now | Needed for diagnostics, supportability, and runtime policy checks. |

---

## Section 5 — Animation

| SDK Surface | Use Case | MCP Value | Risk | Shape | Proposed MCP Tool | Decision | Notes |
|---|---|---:|---:|---|---|---|---|
| `animation.play_animation` | Explicit animation by name | Medium | Medium | Direct | `vector_play_animation` | Later | Defer until core operational surfaces are complete; keep as UX layer. |
| `animation.play_animation_trigger` | Trigger-based animation playback | Medium | Medium | Direct | `vector_play_animation_trigger` | Later | Same defer rationale as above. |
| `animation.load_animation_list` / `anim_list` | Enumerate available animations | Low | High | Direct | `vector_list_animations` | Later | Known timeout path in Wire-Pod flows; do not block core workflows on this. |
| `animation.load_animation_trigger_list` / `anim_trigger_list` | Enumerate trigger names | Low | High | Direct | `vector_list_animation_triggers` | Later | Same timeout caveat; optional utility after stability milestones. |

---

## Section 4 — Motors + Low-Level Control

| SDK Surface | Use Case | MCP Value | Risk | Shape | Proposed MCP Tool | Decision | Notes |
|---|---|---:|---:|---|---|---|---|
| `motors.set_wheel_motors` | Direct wheel velocity control | High | High | Direct | `vector_set_wheel_motors` | Later | Powerful but easy to misuse; requires strict clamps, timeout, and deadman safeguards. |
| `motors.set_head_motor` | Direct head motor control | Medium | Medium | Direct | `vector_set_head_motor` | Later | Prefer higher-level head-angle behavior path first. |
| `motors.set_lift_motor` | Direct lift motor control | Medium | Medium | Direct | `vector_set_lift_motor` | Later | Prefer higher-level lift-height behavior path first. |
| `motors.stop_all_motors` | Immediate motion halt / safety stop | Very High | Low | Direct | `vector_emergency_stop` | Now | Critical safety primitive; include even while low-level motor controls are deferred. |

---


## Section 3 — Audio + Screen

| SDK Surface | Use Case | MCP Value | Risk | Shape | Proposed MCP Tool | Decision | Notes |
|---|---|---:|---:|---|---|---|---|
| `audio.set_master_volume` | Runtime volume control | Medium | Low | Direct | `vector_set_volume` | Now | Clamp to safe range; return prior/current value when possible. |
| `audio.stream_wav_file` | Play pre-existing WAV assets | Medium | Medium | Direct | `vector_play_wav` | Later | Defer until asset pipeline exists (curated corpus and path-policy) + format/size/duration guardrails. |
| `screen.set_screen_to_color` | Fast visual state signaling | Medium | Low | Direct | `vector_screen_color` | Now | Reliable, simple, good for status cues. |
| `screen.set_screen_with_image_data` | Rich visual output on face display | High | Medium | Direct | `vector_face_image` | Now | Useful now because image-generation pipelines are readily available; enforce strict image validation. |
| `vision.display_camera_feed_on_face` | Display camera feed on face | Low | Low | Direct | `vector_face_camera_feed` | Skip | Demo-oriented; low operational value for current milestones. |

---

## Implementation order (proposed)

1. **Now batch A**: `vector_scan`, `vector_find_faces`, `vector_list_visible_faces`, `vector_list_visible_objects`, `vector_charger_status`, `vector_capture_image`, `vector_face_detection`, `vector_vision_reset`, `vector_set_eye_color`
2. **Now batch B**: promote top composed helpers with guardrails
3. **Later batch**: charger return, pose/object-goal, manipulation, custom detection, cube lifecycle tools
