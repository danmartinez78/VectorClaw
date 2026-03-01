# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project follows Semantic Versioning.

## [Unreleased]

### Added

- No notable changes yet.

## [1.0.0] - 2026-03-01

### Added

- 23 MCP tools: 16 verified on hardware, 7 experimental.
- `vector_scan`, `vector_find_faces`, `vector_list_visible_faces`, `vector_face_detection`, `vector_list_visible_objects`, `vector_drive_on_charger`, `vector_emergency_stop`, `vector_capture_image`, `vector_vision_reset`, `vector_charger_status`, `vector_touch_status`, `vector_proximity_status` (new tools since 0.1.0).
- Charger precondition gate for `vector_drive`: actionable error response with `on_charger` and `action_required` fields; auto-undock via `VECTOR_AUTO_DRIVE_OFF_CHARGER` env var.
- `vector_drive_on_charger` already-docked short-circuit: returns `{status: ok, already_on_charger: true}` immediately without issuing a redundant SDK call.
- `vector_pose` expanded with `origin_id`, `is_picked_up`, and `localized_to_object_id` fields.
- `vector_proximity_status` with empirically-validated field semantics: `found_object` documented as firmware-unreliable; `signal_quality` range not bounded at 1.0 (observed up to ~11.7).
- Guided setup wizard (`vectorclaw-setup`) for configuration, SDK validation, and smoke test.
- Hardware Smoke Log, Hardware Test Playbook, Tool Docking Prerequisites, and SDK Reliability Analysis docs.

### Changed

- Known-limitation language updated to reflect empirically observed precondition/timing semantics rather than indeterminate failure states:
  - `vector_drive_on_charger` reliability depends on charger visibility in recent world model; `vector_scan` first is the documented precondition.
  - Perception tools return empty results when vision modes are inactive (disabled-by-design after `vector_vision_reset`), not due to a fundamental SDK defect.
- `vector_face` payload format fixed (rgb565 via `anki_vector.screen.convert_image_to_screen_data()`).
- `Unknown Event type` SDK warnings suppressed via event filter.

### Fixed

- `vector_face` byte-length error: now uses rgb565 format matching the 35328-byte screen buffer.

## [0.1.0] - 2026-02-26

### Added

- Initial MCP server implementation for Anki Vector control.
- Core robot tools including speech, animation, drive, camera capture, face display, pose, cube actions, and status.
- TestPyPI publishing workflow (`.github/workflows/release-testpypi.yml`) for safe release validation.
- Contributor and governance docs (`CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, PR/issue templates).
- GitHub automation for CI, devcontainer validation, release publishing, Dependabot, and CodeQL.

### Changed

- Repository line-ending policy now enforces LF via `.gitattributes` and `.editorconfig`.
- Contribution guidance now includes devcontainer-first setup and release process.

### Fixed

- Normalized line-ending noise in the repository workflow.
