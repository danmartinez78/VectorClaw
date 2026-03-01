---
name: vectorclaw-mcp
description: "MCP tools for Anki Vector: speech, motion, camera, sensors, and automation workflows."
openclaw:
  emoji: "🤖"
  requires:
    bins: ["python3"]
    env: ["VECTOR_SERIAL"]
  install:
    - id: pip
      kind: pip
      package: vectorclaw-mcp
      label: "Install VectorClaw MCP (pip)"
  mcp:
    servers:
      vectorclaw:
        command: python3
        args:
          - "-m"
          - "vectorclaw_mcp.server"
        env:
          VECTOR_SERIAL: "${VECTOR_SERIAL}"
---

# VectorClaw MCP

VectorClaw connects OpenClaw to an Anki / Digital Dream Labs Vector robot through MCP.
It provides practical robot control primitives for speech, movement, camera capture, and status/sensor reads.

## What you can do

- Speak text with `vector_say`
- Move and position with `vector_drive`, `vector_head`, `vector_lift`
- Capture camera images with `vector_look` and `vector_capture_image`
- Read robot state with `vector_status`, `vector_pose`, `vector_proximity_status`, `vector_touch_status`
- Build look → reason → act workflows

## Vision requirement for look → reason → act

For see → reason → act workflows, the agent must either be vision-capable itself (e.g., a VLM) or have access to a separate vision model/image-interpretation tool to analyze camera images before choosing actions.

## Requirements

- Vector robot configured and reachable
- Wire-Pod running
- SDK configured at `~/.anki_vector/sdk_config.ini`
- `VECTOR_SERIAL` environment variable set

## Quick setup

1. Install package: `pip install vectorclaw-mcp`
2. Configure SDK: `python3 -m anki_vector.configure`
3. Export robot serial: `export VECTOR_SERIAL=your-serial`
4. Add MCP server:

```json
{
  "mcpServers": {
    "vectorclaw": {
      "command": "python3",
      "args": ["-m", "vectorclaw_mcp.server"],
      "env": { "VECTOR_SERIAL": "${VECTOR_SERIAL}" }
    }
  }
}
```

## Tool coverage

**Hardware-verified core tools**
`vector_say`, `vector_drive_off_charger`, `vector_drive`, `vector_emergency_stop`, `vector_head`, `vector_lift`, `vector_look`, `vector_capture_image`, `vector_face`, `vector_scan`, `vector_vision_reset`, `vector_pose`, `vector_status`, `vector_charger_status`, `vector_touch_status`, `vector_proximity_status`

**Experimental tools**
`vector_animate`, `vector_drive_on_charger`, `vector_find_faces`, `vector_list_visible_faces`, `vector_face_detection`, `vector_list_visible_objects`, `vector_cube`

## Current limitations

- Charger return (`vector_drive_on_charger`) is currently unreliable
- Face/object detection is currently inconsistent
- Visual interpretation requires the vision capability described above

## Documentation

- MCP API: `docs/MCP_API_REFERENCE.md`
- SDK Reference: `docs/VECTOR_SDK_REFERENCE.md`
- Hardware log: `docs/HARDWARE_SMOKE_LOG.md`
- Repo: https://github.com/danmartinez78/VectorClaw
