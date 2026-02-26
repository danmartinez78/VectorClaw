# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project follows Semantic Versioning.

## [Unreleased]

### Added

- TestPyPI publishing workflow (`.github/workflows/release-testpypi.yml`) for safe release validation.
- Contributor and governance docs (`CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, PR/issue templates).
- GitHub automation for CI, devcontainer validation, release publishing, Dependabot, and CodeQL.

### Changed

- Repository line-ending policy now enforces LF via `.gitattributes` and `.editorconfig`.
- Contribution guidance now includes devcontainer-first setup and release process.

### Fixed

- Normalized line-ending noise in the repository workflow.
