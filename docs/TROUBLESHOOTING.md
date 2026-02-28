# Troubleshooting

## Quick Triage
1. Confirm Wire-Pod service is running
2. Confirm Vector serial/env values are set
3. Run a lightweight tool first (`vector_status`)
4. Check CI + local tests (`pytest tests/ -v`)

## Common Problems

### 1) `Unknown Event type` warnings in logs
- **Symptom:** repeated `events.EventHandler WARNING Unknown Event type`
- **Impact:** currently non-fatal in observed runs
- **Action:** continue if tools are functioning; track in issue #39 for cleanup

### 2) `vector_list_visible_objects` returns empty list unexpectedly
- **Symptom:** `{"status": "ok", "objects": []}` even with a nearby object/cube
- **Impact:** usually a perception-state/timing issue, not a hard MCP failure
- **Action:**
  1. Run `vector_scan` to refresh the scene
  2. Re-run `vector_list_visible_objects`
  3. Verify line-of-sight, distance, lighting, and object angle
- **Tracking:** issue #87

### 3) `vector_face` fails with expected byte-length error
- **Symptom:** `set_screen_with_image_data expected 35328 bytes`
- **Cause:** payload format mismatch (compressed bytes vs expected raw screen format)
- **Status:** tracked in issue #41
- **Workaround:** avoid `vector_face` for release smoke until fixed

### 4) Robot won’t connect
- **Check:**
  - `VECTOR_SERIAL` present
  - network path to robot/Wire-Pod is valid
  - SDK import works in current Python env
- **Action:** re-run setup flow and verify cert/runtime context

### 5) Contributor-only: merge conflict fallout in perception tests
- **Symptom:** CI fails unexpectedly after conflict resolution
- **Cause:** stale conflict markers or broken assertions
- **Action:**
  - search for `<<<<<<<`, `=======`, `>>>>>>>`
  - validate test contracts against actual return payloads

## Smoke Test Baseline (Recommended)
- `vector_status`
- `vector_say`
- `vector_drive_off_charger`
- `vector_drive`
- `vector_look`
- `vector_pose`
- `vector_head`
- `vector_lift`

## Escalation
Open or update an issue at:
- https://github.com/danmartinez78/VectorClaw/issues

Include:
- exact command(s) and full output
- robot physical behavior observed
- links to relevant existing issues/threads
