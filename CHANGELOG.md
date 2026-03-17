# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project follows Semantic Versioning.

## [Unreleased]

### Added

- **ROS2 bridge** (`vectorclaw_ros2`): new `ament_python` package exposing the Vector robot as a standard ROS2 node. Publishes `/vector/status`, `/vector/pose`, `/vector/proximity`, `/vector/camera`, and `/vector/touch` topics; subscribes to `/vector/cmd_vel`, `/vector/cmd_say`, `/vector/cmd_head`, `/vector/cmd_lift`, and `/vector/cmd_animate`; exposes `/vector/emergency_stop` and `/vector/drive_off_charger` services. Compatible with ROS2 Jazzy and newer. See `docs/ROS2_BRIDGE.md` for setup and usage.

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
