# Troubleshooting

## Quick Triage
1. Confirm Wire-Pod service is running
2. Confirm Vector serial/env values are set
3. Run a lightweight tool first (`vector_status`)
4. Check CI + local tests (`pytest tests/ -v`)

## Common Problems

### 1) `Unknown Event type` warnings in logs
- **Symptom:** repeated `events.EventHandler WARNING Unknown Event type`
- **Impact:** warnings suppressed in v1.0.0 via SDK event filter
- **Action:** if still seeing these, verify you're on vectorclaw-mcp >= 1.0.0

### 2) `vector_face` fails with expected byte-length error
- **Symptom:** `set_screen_with_image_data expected 35328 bytes`
- **Cause:** payload format mismatch (compressed bytes vs expected raw screen format)
- **Status:** fixed in v1.0.0 (uses rgb565 format)
- **Action:** upgrade to vectorclaw-mcp >= 1.0.0

### 3) Robot won’t connect
- **Check:**
  - `VECTOR_SERIAL` present
  - network path to robot/Wire-Pod is valid
  - SDK import works in current Python env
- **Action:** re-run setup flow and verify cert/runtime context

### 4) Contributor-only: merge conflict fallout in perception tests
- **Symptom:** CI fails unexpectedly after conflict resolution
- **Cause:** stale conflict markers or broken assertions
- **Action:**
  - search for `<<<<<<<`, `=======`, `>>>>>>>`
  - validate test contracts against actual return payloads

### 5) Perception tools return empty results
- **Symptom:** `vector_find_faces`, `vector_list_visible_faces`, `vector_face_detection`, or `vector_list_visible_objects` always return empty arrays even when objects/faces are present.
- **Cause (precondition):** Vision modes must be active for these tools to populate results. Vision modes are enabled automatically at connect time; however, calling `vector_vision_reset` disables them for the remainder of the session.
- **Action:**
  - Do **not** call `vector_vision_reset` before using perception tools in the same session.
  - If `vector_vision_reset` was already called, reconnect the MCP server to restore vision mode enablement.
  - Confirm the robot camera has line-of-sight to the subject (correct head angle, adequate lighting).

### 6) `vector_drive_on_charger` times out with no robot motion
- **Symptom:** Tool returns `timed_out: true` and motors stop, but Vector never approached the charger.
- **Cause (precondition):** `drive_on_charger` requires the charger to be present in Vector's recently-observed world model. If Vector has not seen the charger in the current session the SDK command has nothing to navigate to.
- **Action:**
  1. Place the charger in Vector's field of view.
  2. Call `vector_scan` to let Vector observe and register the charger in its world model.
  3. Then call `vector_drive_on_charger`.
- **Note:** Calling `vector_drive_on_charger` while already docked returns `{status: ok, already_on_charger: true}` immediately — this is expected behavior.

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
