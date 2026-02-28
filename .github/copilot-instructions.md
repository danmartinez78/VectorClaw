# Copilot Instructions for VectorClaw

## Project Context

- This repository provides an MCP server that controls Anki Vector robots.
- Python package source lives under `src/vectorclaw_mcp`.
- Tests live under `tests/`.

## ⚠️ CRITICAL: SDK Surface Documentation

**Before implementing or modifying ANY tool that interacts with the SDK, you MUST:**

1. **Read the authoritative SDK surface reference:** `docs/WIREPOD_SDK_SURFACE_REFERENCE.md`
2. **Verify all property names, method signatures, and behavior against this doc**
3. **Do NOT assume field names or behavior** — check the reference

**During code review, verify:**
- All SDK property names match the reference doc exactly
- All method calls use correct signatures from the reference doc
- All behavior expectations align with SDK documentation

**Common mistakes to avoid:**
- `is_carrying_object` → wrong (use `is_carrying_block`)
- `is_on_charger_platform` → wrong (use `is_on_charger`)
- Assuming perception tools work without enabling vision modes
- Assuming `found_object` in proximity sensor means "distance changed"

**When in doubt, search the SDK surface doc first.**

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
