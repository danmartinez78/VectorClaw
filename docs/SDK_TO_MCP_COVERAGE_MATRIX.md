# Functionality Matrix

Status legend:
- ✅ Implemented + validated on hardware
- 🟡 Implemented, pending full hardware validation
- ⚪ Not implemented yet

## Current MCP Tool Coverage

| Capability | Tool | Implementation | Hardware validation | Notes |
|---|---|---:|---:|---|
| Robot status | `vector_status` | ✅ | ✅ | Battery/charging/carrying-block verified |
| Robot pose | `vector_pose` | ✅ | ✅ | Position/orientation payload returned |
| Camera capture | `vector_look` | ✅ | ✅ | Base64 image returned |
| Speech | `vector_say` | ✅ | ✅ | Audible speech confirmed |
| Drive linear/turn | `vector_drive` | ✅ | ✅ | Forward/reverse/turn confirmed |
| Drive off charger | `vector_drive_off_charger` | ✅ | ✅ | Added during validation session |
| Face display | `vector_face` | ✅ | 🟡 | Needs canonical test images + constraints |
| Cube actions | `vector_cube` | ✅ | 🟡 | No cube available in this run |
| Animations | `vector_animate` | ✅ | 🟡 | Animation-list path needs follow-up |
| Head motion | `vector_head` | ✅ | 🟡 | Clamped to -22.0–45.0 degrees |
| Lift/arm motion | `vector_lift` | ✅ | 🟡 | Normalised 0.0–1.0 range |
| Scan environment | `vector_scan` | ✅ | 🟡 | look_around_in_place behavior |
| Find faces | `vector_find_faces` | ✅ | 🟡 | Active face search behavior |
| List visible faces | `vector_list_visible_faces` | ✅ | 🟡 | Returns face_id and name |
| List visible objects | `vector_list_visible_objects` | ✅ | 🟡 | Returns object_id list |
| Drive on charger | `vector_drive_on_charger` | ✅ | 🟡 | Timeout + motor-stop fallback |
| Emergency stop | `vector_emergency_stop` | ✅ | 🟡 | Stops all motors immediately |
| Capture single image | `vector_capture_image` | ✅ | 🟡 | Via capture_single_image |
| Face detection summary | `vector_face_detection` | ✅ | 🟡 | Returns face_count + expression |
| Vision reset | `vector_vision_reset` | ✅ | 🟡 | Disables all vision modes |
| Charger state | `vector_charger_status` | ✅ | 🟡 | Charging + battery + platform |
| Touch sensor | `vector_touch_status` | ✅ | 🟡 | is_being_touched + raw_touch_value |
| Proximity sensor | `vector_proximity_status` | ✅ | 🟡 | distance_mm + found_object + is_lift_in_fov |

## Validation Protocol (recommended)

1. Execute one command.
2. Wait for explicit human confirmation.
3. Log result (pass/fail/ambiguous).
4. Move to next command.

This protocol should be used for all future motion-feature validation.
