# VectorClaw v1.0.0-rc1 Release Notes (Draft)

## Highlights
- Expanded implementation surface for perception, vision, motion safety, and sensors
- MCP registration integration for new tools is tracked in issue #67
- Test architecture split for parallel feature development (`tests/` modularized)
- Runtime/tool registration architecture split for lower merge-conflict risk
- Hardware smoke validation process standardized

## New Capability Areas (implemented; MCP exposure pending #67)

### Perception Discovery
- `vector_scan`
- `vector_find_faces`
- `vector_list_visible_faces`
- `vector_list_visible_objects`

### Motion Safety
- `vector_drive_on_charger` (experimental)
- `vector_emergency_stop`

### Vision Controls
- `vector_capture_image`
- `vector_face_detection`
- `vector_vision_reset`

### Status/Sensor Expansion
- `vector_charger_status`
- `vector_touch_status`
- `vector_proximity_status`
- expanded `vector_status` payload

## Setup / Compatibility
- Confirmed working against upstream Wire-Pod SDK (`wirepod_vector_sdk` 0.8.1) for baseline functionality
- No custom SDK fork required for baseline functionality

## Known Issues
- #39: Non-fatal `Unknown Event type` warnings in logs
- #41: `vector_face` payload format mismatch on hardware

## Validation
- CI matrix: Python 3.11 + 3.12 experimental
- Hardware smoke: baseline command set validated; expanded matrix pending post-integration run

## Upgrade Notes
- Existing users should review updated API docs for new tool registrations and payload shapes
- Re-run smoke baseline after upgrade in each environment
