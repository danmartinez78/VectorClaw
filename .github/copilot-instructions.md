# Copilot Instructions for VectorClaw

## Project Context

- This repository provides an MCP server that controls Anki Vector robots.
- Python package source lives under `src/vectorclaw_mcp`.
- Tests live under `tests/`.

## Contribution Defaults

- Keep changes minimal and task-focused.
- Preserve existing public tool names and API behavior unless explicitly requested.
- Prefer small pure functions where possible.
- Add or update tests for changed behavior.

## Safety and Runtime Constraints

- Do not execute robot movement by default in tests.
- Keep hardware-dependent logic isolated behind interfaces that can be mocked.
- Avoid adding blocking operations to MCP tool handlers.

## Development Workflow

- Use the devcontainer setup for consistency.
- Run `pytest -q` before finalizing.
- If packaging or dependency metadata changes, validate with `python -m build`.

## Documentation

When behavior changes, update docs in:

- `README.md` for user-facing usage
- `docs/SETUP.md` for setup/runtime details
- `ROADMAP.md` only for planning-level updates
