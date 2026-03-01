# VectorClaw v1.0.0 Release Notes

## Highlights
- 12 MCP tools for robot control: speech, motion, perception, status
- Wire-Pod SDK integration (>= 0.8.0)
- MCP registration integration for all tools
- Test architecture split for parallel feature development
- Hardware smoke validation process standardized

## New Capability Areas (implemented and MCP-registered)

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

## Resolved Issues
- SDK `Unknown Event type` warnings — suppressed via event filter
- `vector_face` payload format — fixed (rgb565 format)

## Validation
- CI matrix: Python 3.11 + 3.12 experimental
- Hardware smoke: baseline command set validated; expanded matrix execution in progress for newly registered tools

## Upgrade Notes
- Existing users should review updated API docs for new tool registrations and payload shapes
- Re-run smoke baseline after upgrade in each environment
