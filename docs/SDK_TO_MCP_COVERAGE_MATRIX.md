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
| Head motion | `vector_head` | ✅ | 🟡 | Angle clamped to -22.0–45.0°; hardware validation pending |
| Lift/arm motion | `vector_lift` | ✅ | 🟡 | Height normalised 0.0–1.0; hardware validation pending |

## High-value SDK Features to Add Next

| Feature | Proposed tool | Status | Rationale |
|---|---|---:|---|
| Charger state helper | `vector_ensure_off_charger` | ⚪ | Better UX before movement calls |
| Motion presets | `vector_motion_preset` | ⚪ | Repeatable demos (square, spin, nod) |
| Idle behavior mode | `vector_idle_mode` | ⚪ | Reduce validation ambiguity |

## Validation Protocol (recommended)

1. Execute one command.
2. Wait for explicit human confirmation.
3. Log result (pass/fail/ambiguous).
4. Move to next command.

This protocol should be used for all future motion-feature validation.
