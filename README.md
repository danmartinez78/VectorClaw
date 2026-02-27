# VectorClaw

**Anki Vector + OpenClaw integration via MCP.**  
Give your AI assistant a body. VectorClaw is an MCP server that exposes Anki Vector robot capabilities as tools for AI assistants like OpenClaw.

```
┌─────────────┐    stdio MCP    ┌──────────────────┐    SDK/WiFi    ┌─────────┐
│  AI Agent   │ ─────────────── │  vectorclaw-mcp  │ ─────────────── │  Vector │
│  (OpenClaw) │                 │  (Python)        │   gRPC/WiFi     │  Robot  │
└─────────────┘                 └──────────────────┘                 └─────────┘
```

## Setup

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
| `vector_look` | Capture an image from the front camera |
| `vector_face` | Display a custom image on the face screen |
| `vector_pose` | Get current position and orientation |
| `vector_cube` | Interact with the cube accessory (dock/pickup/drop/roll) |
| `vector_status` | Get battery level and charging status |

## Future Considerations

- Audio recording from microphones
- Object detection via camera
- Multiple robot support
- Personality modes (curious, shy, energetic)

## License

MIT — see [LICENSE](LICENSE).
