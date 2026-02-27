# Functionality Matrix

Status legend:
- ✅ Implemented + validated on hardware
- 🟡 Implemented, pending full hardware validation
- ⚪ Not implemented yet

## Current MCP Tool Coverage

| Capability | Tool | Implementation | Hardware validation | Notes |
|---|---|---:|---:|---|
| Robot status | `vector_status` | ✅ | ✅ | Battery/charging/carrying-block/cliff/moving verified |
| Robot pose | `vector_pose` | ✅ | ✅ | Position/orientation payload returned |
| Camera capture | `vector_look` | ✅ | ✅ | Base64 image returned |
| Camera capture (single) | `vector_capture_image` | ✅ | 🟡 | Uses capture_single_image path |
| Speech | `vector_say` | ✅ | ✅ | Audible speech confirmed |
| Drive linear/turn | `vector_drive` | ✅ | ✅ | Forward/reverse/turn confirmed |
| Drive off charger | `vector_drive_off_charger` | ✅ | ✅ | Added during validation session |
| Drive on charger | `vector_drive_on_charger` | ✅ | 🟡 | Experimental best-effort helper |
| Emergency stop | `vector_emergency_stop` | ✅ | 🟡 | Stops all motors immediately |
| Face display | `vector_face` | ✅ | 🟡 | Needs canonical test images + constraints |
| Cube actions | `vector_cube` | ✅ | 🟡 | No cube available in this run |
| Animations | `vector_animate` | ✅ | 🟡 | Animation-list path needs follow-up |
| Head motion | `vector_head` | ✅ | ✅ | Angle clamped to safe range |
| Lift/arm motion | `vector_lift` | ✅ | ✅ | Height normalised 0.0–1.0 |
| Charger status | `vector_charger_status` | ✅ | 🟡 | is_charging + is_on_charger_platform |
| Touch sensor | `vector_touch_status` | ✅ | 🟡 | last_touch_time + is_being_held |
| Proximity sensor | `vector_proximity_status` | ✅ | 🟡 | distance_mm + found_object |
| Environment scan | `vector_scan` | ✅ | 🟡 | look_around_in_place |
| Face search | `vector_find_faces` | ✅ | 🟡 | behavior.find_faces |
| List visible faces | `vector_list_visible_faces` | ✅ | 🟡 | world.visible_faces |
| List visible objects | `vector_list_visible_objects` | ✅ | 🟡 | world.visible_objects + custom |
| Face detection summary | `vector_face_detection` | ✅ | 🟡 | summarized detections from world state |
| Vision reset | `vector_vision_reset` | ✅ | 🟡 | disable_all_vision_modes |

## Validation Protocol (recommended)

1. Execute one command.
2. Wait for explicit human confirmation.
3. Log result (pass/fail/ambiguous).
4. Move to next command.

This protocol should be used for all future motion-feature validation.
