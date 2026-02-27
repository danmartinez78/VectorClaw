<div align="center">

# 🤖 VectorClaw

**Give your AI assistant a body.**

VectorClaw is an [MCP](https://modelcontextprotocol.io) server that bridges [Anki Vector](https://www.digitaldreamlabs.com/pages/vector) robots and AI assistants like OpenClaw, exposing the robot's full capabilities as composable tools.

[![PyPI](https://img.shields.io/pypi/v/vectorclaw-mcp?color=blue&label=PyPI)](https://pypi.org/project/vectorclaw-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/vectorclaw-mcp)](https://pypi.org/project/vectorclaw-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/protocol-MCP-8A2BE2)](https://modelcontextprotocol.io)

</div>

---

## Table of Contents

- [How It Works](#how-it-works)
- [Quick Start](#quick-start)
- [Development](#development)
- [MCP Client Configuration](#mcp-client-configuration)
- [Available Tools](#available-tools)
- [Roadmap](#roadmap)
- [Community](#community)
- [License](#license)

---

## How It Works

```
┌─────────────┐    stdio MCP    ┌──────────────────┐    SDK/WiFi    ┌─────────┐
│  AI Agent   │ ─────────────── │  vectorclaw-mcp  │ ─────────────── │  Vector │
│  (OpenClaw) │                 │  (Python)        │   gRPC/WiFi     │  Robot  │
└─────────────┘                 └──────────────────┘                 └─────────┘
```

The MCP server sits between your AI agent and the robot. The agent calls tools (e.g. `vector_say`, `vector_drive`) over stdio; the server translates each call into Anki Vector SDK commands sent to the robot over WiFi.

---

## Quick Start

### 1. Install

```bash
pip install vectorclaw-mcp
```

### 2. Configure Vector (Wire-Pod — recommended)

[Wire-Pod](https://github.com/kercre123/wire-pod) is the canonical, self-hosted server
for Vector. Install `wirepod_vector_sdk` (the recommended SDK distribution), then run
the configuration wizard once to authenticate with your robot:

```bash
pip install wirepod_vector_sdk
python -m anki_vector.configure
```

> **Note:** `wirepod_vector_sdk` installs under the `anki_vector` Python namespace, so
> all imports and CLI commands use `anki_vector`.

> **Legacy cloud path (best-effort only):** The legacy `anki_vector` package
> (`pip install "vectorclaw-mcp[legacy]"`) ties you to DDL cloud servers, which are
> brittle on modern Python runtimes. Prefer `wirepod_vector_sdk` for reliable,
> cloud-independent operation.

For a full walkthrough (Wire-Pod setup, firmware, WiFi, troubleshooting) see
[docs/SETUP.md](docs/SETUP.md).

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

---

## Development

> **Devcontainer First** — the devcontainer is the canonical dev environment.

1. Open this repo in VS Code.
2. Run **Dev Containers: Reopen in Container**.
3. Wait for `postCreateCommand` to finish (`pip install -e .[dev]`).
4. Run the test suite:

```bash
pytest -q
```

Host-level installs are optional and mainly for quick one-off checks.

---

## MCP Client Configuration

Add the following to your `mcporter.json` (or equivalent MCP client config).

**Recommended — `uvx`** (no prior installation needed):

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

**Alternative — `pip install`** (if you installed the package locally):

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

| Tool | Description |
|------|-------------|
| `vector_say` | 🔊 Make the robot speak text aloud |
| `vector_animate` | 🎭 Play a named animation |
| `vector_drive` | 🚗 Drive straight and/or turn in place |
| `vector_look` | 📷 Capture an image from the front camera |
| `vector_face` | 🖥️ Display a custom image on the face screen |
| `vector_pose` | 📍 Get current position and orientation |
| `vector_cube` | 🧊 Interact with the cube accessory (dock/pickup/drop/roll) |
| `vector_status` | 🔋 Get battery level and charging status |

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the full milestone plan. Highlights:

- 🔬 **v0.2** — Hardware validation (all 8 tools on real robot)
- 🛠️ **v0.3** — Code quality & test coverage ≥ 80%
- 🔒 **v0.4** — Security hardening
- 🚀 **v1.0** — Public release on PyPI

**Future ideas:** audio recording · object detection · multi-robot support · personality modes · ROS2 integration

---

## Community

| Resource | Link |
|----------|------|
| Contribution guide | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |
| Code of Conduct | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |
| Security policy | [SECURITY.md](SECURITY.md) |

---

## License

MIT — see [LICENSE](LICENSE).
