# VectorClaw

**Anki Vector + OpenClaw integration via MCP.**  
Give your AI assistant a body. VectorClaw is an MCP server that exposes Anki Vector robot capabilities as tools for AI assistants like OpenClaw.

```
┌─────────────┐    stdio MCP    ┌──────────────────┐    gRPC/WiFi    ┌─────────┐
│  AI Agent   │ ─────────────── │  vectorclaw-mcp  │ ─────────────── │  Vector │
│  (OpenClaw) │                 │  (Python 3.11+)  │                 │  Robot  │
└─────────────┘                 └──────────────────┘                 └─────────┘
```

All communication is local — no cloud dependency at runtime (Wire-Pod setup path).
See [Security Architecture](docs/SECURITY_ARCHITECTURE.md) for the full trust model.

## Current Status

**Alpha — v0.1.0.**  Real-hardware smoke tested 2026-02-27; all core motion, speech, camera, and head/lift tools verified PASS on a production Vector robot with Wire-Pod.

Known open issues:
- `vector_face` has a payload-format bug (issue #41) — fix in progress.
- Occasional non-fatal SDK `Unknown Event type` warning (issue #39) — non-blocking.

See [ROADMAP.md](ROADMAP.md) for the v1.0 milestone plan and near-term work.

## Setup

**Requirements:** Python 3.11+ · Wire-Pod running · Vector on local WiFi

For the full setup walkthrough (Wire-Pod install, robot auth, WiFi config, troubleshooting), see **[docs/SETUP.md](docs/SETUP.md)**.

### 1. Install

```bash
pip install vectorclaw-mcp
```

### 2. Configure Vector (Wire-Pod — recommended)

[Wire-Pod](https://github.com/kercre123/wire-pod) is the canonical, self-hosted server
for Vector.  Install `wirepod_vector_sdk` (the recommended SDK distribution), then run
the configuration wizard once to authenticate with your robot:

```bash
pip install wirepod_vector_sdk
python -m anki_vector.configure
```

> **Note:** `wirepod_vector_sdk` installs under the `anki_vector` Python namespace, so
> all imports and CLI commands use `anki_vector`.

> **Legacy cloud path (best-effort only):** The legacy `anki_vector` package
> (`pip install "vectorclaw-mcp[legacy]"`) ties you to DDL cloud servers, which are
> brittle on modern Python runtimes.  Prefer `wirepod_vector_sdk` for reliable,
> cloud-independent operation.

### 3. Set environment variables

```bash
export VECTOR_SERIAL="your-robot-serial"   # required
export VECTOR_HOST="192.168.x.x"           # optional — auto-discovered if omitted
```

### 4. Run the server

```bash
vectorclaw-mcp
# or
python -m vectorclaw_mcp
```

## OpenClaw / mcporter configuration

Add the following to your `mcporter.json` (or equivalent MCP client config).

**With `uvx`** (no prior installation needed — recommended for MCP clients):

```json
{
  "mcpServers": {
    "vectorclaw": {
      "command": "uvx",
      "args": ["vectorclaw-mcp"],
      "env": {
        "VECTOR_SERIAL": "your-serial-here"
      }
    }
  }
}
```

**With `pip install`** (if you installed the package locally):

```json
{
  "mcpServers": {
    "vectorclaw": {
      "command": "vectorclaw-mcp",
      "env": {
        "VECTOR_SERIAL": "your-serial-here"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `vector_say` | Make the robot speak text aloud |
| `vector_animate` | Play a named animation |
| `vector_drive` | Drive straight and/or turn in place |
| `vector_drive_off_charger` | Drive the robot off its charger |
| `vector_look` | Capture an image from the front camera |
| `vector_face` | Display a custom image on the face screen |
| `vector_head` | Set head angle (clamped −22° – 45°) |
| `vector_lift` | Set lift/arm height (0.0 – 1.0 normalised) |
| `vector_pose` | Get current position and orientation |
| `vector_cube` | Interact with the cube accessory (dock/pickup/drop/roll) |
| `vector_status` | Get battery level and charging status |

> **Charger note:** `vector_drive` requires the robot to be off the charger.
> Call `vector_drive_off_charger` first, or set `VECTOR_AUTO_DRIVE_OFF_CHARGER=1`.
> See [Tool Docking Prerequisites](docs/TOOL_DOCKING_PREREQUISITES.md) for the full matrix.

Full parameter details and response schemas: **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)**.

## Contributing

1. **Branch:** branch off `main`, name your branch `<type>/<short-description>` (e.g. `fix/vector-face-payload`, `feat/vector-scan`).
2. **Tests:** add or update tests under `tests/`; all tests use the mocked SDK so no hardware is required.
3. **CI:** the CI matrix runs on Python 3.11 (required — must pass) and Python 3.12 (experimental — informational).  Run `pytest tests/ -v` locally before opening a PR.
4. **Hardware:** if your change touches a tool or the robot connection layer, record a smoke-test run in [docs/HARDWARE_SMOKE_LOG.md](docs/HARDWARE_SMOKE_LOG.md) and follow the [Hardware Test Playbook](docs/HARDWARE_TEST_PLAYBOOK.md).
5. **PR scope:** keep PRs focused — separate docs, feature, and refactor changes into distinct PRs to reduce merge-conflict risk with parallel lanes.

## Docs Map

### Setup & runtime
- [Setup Guide](docs/SETUP.md) — Wire-Pod install, robot auth, WiFi, SDK config, troubleshooting
- [Runtime Support](docs/RUNTIME_SUPPORT.md) — supported Python versions and CI policy

### API & SDK
- [API Reference](docs/API_REFERENCE.md) — MCP tool signatures, parameters, response schemas
- [Wire-Pod SDK Surface Reference](docs/WIREPOD_SDK_SURFACE_REFERENCE.md) — full SDK capability catalog
- [Wire-Pod SDK Implementation Guide](docs/WIREPOD_SDK_IMPLEMENTATION_GUIDE.md) — implementation patterns and SDK usage notes
- [Wire-Pod SDK → MCP Integration Priorities](docs/WIREPOD_SDK_MCP_INTEGRATION_PRIORITIES.md) — Now/Later/Skip decision table for future tools
- [SDK → MCP Coverage Matrix](docs/SDK_TO_MCP_COVERAGE_MATRIX.md) — current mapping of SDK calls to MCP tools
- [SDK Fork Patch Notes](docs/SDK_FORK_PATCH_NOTES.md) — changes applied to the Wire-Pod SDK fork

### Hardware validation
- [Hardware Test Playbook](docs/HARDWARE_TEST_PLAYBOOK.md) — repeatable on-robot validation protocol and PR checklist
- [Hardware Smoke Log](docs/HARDWARE_SMOKE_LOG.md) — running record of real-world smoke tests
- [Tool Docking Prerequisites](docs/TOOL_DOCKING_PREREQUISITES.md) — which tools require undocked state
- [Hardware Validation (2026-02-26)](docs/HARDWARE_VALIDATION_2026-02-26.md) — initial hardware validation session record

### Security
- [Security Architecture](docs/SECURITY_ARCHITECTURE.md) — threat model, credential handling, input validation, network posture

## License

MIT — see [LICENSE](LICENSE).
