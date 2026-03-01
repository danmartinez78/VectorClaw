# 🤖 VectorClaw

<div align="center">

[![CI](https://github.com/danmartinez78/VectorClaw/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/danmartinez78/VectorClaw/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status: v1.0.0](https://img.shields.io/badge/status-v1.0.0-brightgreen.svg)](ROADMAP.md)

**Give your AI assistant a body.**

VectorClaw is an MCP server that exposes [Anki Vector](https://github.com/kercre123/wire-pod) robot capabilities as tools for AI assistants like OpenClaw — bridging natural language to real-world robot actions over a fully local, cloud-free stack.

</div>

---

## Architecture

```
┌─────────────┐    stdio MCP    ┌──────────────────┐    gRPC/WiFi    ┌─────────┐
│  AI Agent   │ ─────────────── │  vectorclaw-mcp  │ ─────────────── │  Vector │
│  (OpenClaw) │                 │  (Python 3.11+)  │                 │  Robot  │
└─────────────┘                 └──────────────────┘                 └─────────┘
```

All communication is **local-only** — no cloud dependency at runtime (Wire-Pod setup path).

See [Security Architecture](docs/SECURITY_ARCHITECTURE.md) for the full trust model.

---

## Table of Contents

- [Current Status](#current-status)
- [Quickstart](#quickstart)
- [MCP Client Configuration](#mcp-client-configuration)
- [Available Tools](#available-tools)
- [Contributing](#contributing)
- [Docs Map](#docs-map)

---

## Current Status

> **v1.0.0 Released** · 2026-03-01

**16 tools verified ✅** on hardware | **7 tools experimental ⚠️**

**Known limitations:**
- `vector_drive_on_charger` — activates cube but no reliable charger approach
- Perception detections — often returns empty lists; SDK semantics under investigation
- Idle behaviors — Vector's autonomous animations can overlap with commanded behaviors

See [ROADMAP.md](ROADMAP.md) for the full milestone plan.

---

## Quickstart

**Requirements:** Python 3.11+ · [Wire-Pod](https://github.com/kercre123/wire-pod) running · Vector on local WiFi

> For the complete walkthrough (Wire-Pod install, robot auth, WiFi config, troubleshooting) see **[docs/SETUP.md](docs/SETUP.md)**.

### Guided Setup (recommended for new users)

The `vectorclaw-setup` wizard handles configuration, SDK validation, connectivity
check, and a smoke test in one go:

```bash
pip install vectorclaw-mcp
vectorclaw-setup
```

You will be prompted for your robot's serial number and optional IP address.
On success you'll see a clear **SETUP PASSED** message and the next-steps command.
On failure every step includes an exact remediation hint.

→ Full details in **[docs/OPENCLAW_SETUP_SKILL.md](docs/OPENCLAW_SETUP_SKILL.md)**

---

### Manual Setup

**Step 1 — Install VectorClaw**

```bash
pip install vectorclaw-mcp
```

**Step 2 — Configure Vector SDK**

[Wire-Pod](https://github.com/kercre123/wire-pod) is the canonical self-hosted server for Vector.
Install the SDK distribution and run the one-time auth wizard:

```bash
pip install wirepod_vector_sdk
python -m anki_vector.configure
```

> **Note:** `wirepod_vector_sdk` installs under the `anki_vector` Python namespace, so all imports and CLI commands use `anki_vector`.

<details>
<summary>Legacy cloud path (best-effort only)</summary>

The standalone `anki_vector` package requires working DDL cloud servers and is brittle on modern Python runtimes.

```bash
pip install "vectorclaw-mcp[legacy]"
python -m anki_vector.configure
```

Prefer `wirepod_vector_sdk` for reliable, cloud-independent operation.
</details>

### Step 3 — Set environment variables

```bash
export VECTOR_SERIAL="your-robot-serial"   # required — printed on underside of robot
export VECTOR_HOST="192.168.x.x"           # optional — auto-discovered if omitted
```

### Step 4 — Run the server

```bash
vectorclaw-mcp
# or
python -m vectorclaw_mcp
```

---

## MCP Client Configuration

Add the following block to your `mcporter.json` (or equivalent MCP client config).

**With `uvx`** *(recommended — no prior install needed)*

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

**With `pip install`** *(if installed locally)*

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

---

## Available Tools

| Tool | Category | Description | Status |
|------|----------|-------------|--------|
| `vector_say` | 🎙️ Speech | Make the robot speak text aloud | ✅ |
| `vector_animate` | 🎭 Expression | Play a named animation | ⚠️ |
| `vector_drive_off_charger` | 🏎️ Motion | Drive the robot off its charger | ✅ |
| `vector_drive` | 🏎️ Motion | Drive straight and/or turn in place | ✅ |
| `vector_drive_on_charger` | 🏎️ Motion | Drive Vector back onto its charger | ⚠️ |
| `vector_emergency_stop` | 🏎️ Motion | Stop all motion immediately | ✅ |
| `vector_head` | 🦾 Actuation | Set head angle (−22° – 45°) | ✅ |
| `vector_lift` | 🦾 Actuation | Set lift height (0.0 – 1.0) | ✅ |
| `vector_look` | 👀 Perception | Capture image from front camera | ✅ |
| `vector_capture_image` | 👀 Perception | One-shot image capture | ✅ |
| `vector_face` | 🖼️ Display | Display custom image on face screen | ✅ |
| `vector_scan` | 🔍 Perception | Head scan for environment | ✅ |
| `vector_find_faces` | 🔍 Perception | Scan for faces | ⚠️ |
| `vector_list_visible_faces` | 🔍 Perception | List currently visible faces | ⚠️ |
| `vector_face_detection` | 🔍 Perception | Get face detection summary | ⚠️ |
| `vector_list_visible_objects` | 🔍 Perception | List currently visible objects | ⚠️ |
| `vector_cube` | 🎲 Interaction | Interact with cube (dock/pickup/drop/roll) | ⚠️ |
| `vector_vision_reset` | 👀 Perception | Disable all vision modes | ✅ |
| `vector_pose` | 📍 Sensing | Get current position and orientation | ✅ |
| `vector_status` | 📊 Status | Get battery level and charging status | ✅ |
| `vector_charger_status` | 📊 Status | Get charger connection state | ✅ |
| `vector_touch_status` | 📊 Status | Get touch sensor state | ✅ |
| `vector_proximity_status` | 📊 Status | Get proximity sensor reading | ✅ |

**Status legend:** ✅ Verified on hardware | ⚠️ Experimental (limited/reliable issues)

> ⚠️ **Charger prerequisite:** `vector_drive` requires the robot to be off the charger.
> Call `vector_drive_off_charger` first, or set `VECTOR_AUTO_DRIVE_OFF_CHARGER=1` for automatic undocking.

See [docs/MCP_API_REFERENCE.md](docs/MCP_API_REFERENCE.md) for full parameter details and response schemas.

---

## Contributing

1. 🌿 **Branch:** branch off `dev`, use `<type>/<short-description>` naming (e.g. `fix/vector-face-payload`, `feat/vector-scan`)
2. 🧪 **Tests:** add or update tests under `tests/`; all tests use the mocked SDK — no hardware required
3. ✅ **CI:** Python 3.11 is required and must pass; Python 3.12 is experimental/informational — run `pytest tests/ -v` locally before opening a PR
4. 🤖 **Hardware:** if your change touches a tool or connection layer, record a smoke-test run in [Hardware Smoke Log](docs/HARDWARE_SMOKE_LOG.md) following the [Hardware Test Playbook](docs/HARDWARE_TEST_PLAYBOOK.md)
5. 🎯 **PR scope:** keep PRs focused — separate docs, feature, and refactor changes to reduce merge-conflict risk with parallel lanes

---

## Docs Map

### 🛠️ Setup & Runtime
| Document | Description |
|----------|-------------|
| [Setup Guide](docs/SETUP.md) | Wire-Pod install, robot auth, WiFi, SDK config, troubleshooting |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common runtime failures, smoke baseline, and escalation path |
| [Runtime Support](docs/RUNTIME_SUPPORT.md) | Supported Python versions and CI policy |
| [OpenClaw Setup Skill Plan](docs/OPENCLAW_SKILL_PLAN.md) | Design plan for foolproof guided setup flow |

### 📡 API & SDK
| Document | Description |
|----------|-------------|
| [API Reference](docs/MCP_API_REFERENCE.md) | MCP tool signatures, parameters, response schemas |
| [Wire-Pod SDK Surface Reference](docs/VECTOR_SDK_REFERENCE.md) | Full SDK capability catalog |
| [Wire-Pod SDK Implementation Guide](docs/WIREPOD_SDK_IMPLEMENTATION_GUIDE.md) | Implementation patterns and SDK usage notes |
| [Wire-Pod SDK → MCP Integration Priorities](docs/WIREPOD_SDK_MCP_INTEGRATION_PRIORITIES.md) | Now/Later/Skip decision table for future tools |
| [SDK → MCP Coverage Matrix](docs/SDK_TO_MCP_COVERAGE_MATRIX.md) | Current mapping of SDK calls to MCP tools |
| [SDK Patch Notes](docs/SDK_PATCH_NOTES.md) | Current SDK patch status (baseline: no fork required) |

### 🔬 Hardware Validation
| Document | Description |
|----------|-------------|
| [Hardware Test Playbook](docs/HARDWARE_TEST_PLAYBOOK.md) | Repeatable on-robot validation protocol and PR checklist |
| [Hardware Smoke Log](docs/HARDWARE_SMOKE_LOG.md) | Running record of real-world smoke tests |
| [Tool Docking Prerequisites](docs/TOOL_DOCKING_PREREQUISITES.md) | Which tools require undocked state |
| [Hardware Validation (2026-02-26)](docs/HARDWARE_VALIDATION_2026-02-26.md) | Initial hardware validation session record |

### 🔒 Security
| Document | Description |
|----------|-------------|
| [Security Architecture](docs/SECURITY_ARCHITECTURE.md) | Threat model, credential handling, input validation, network posture |

---

## License

MIT — see [LICENSE](LICENSE).

<!-- If you found this: yes, premium natural oil is appreciated. -->
