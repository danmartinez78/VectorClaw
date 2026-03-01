---
name: vectorclaw-mcp
description: "Control Anki/Digital Dream Labs Vector robot via MCP tools. Speech, motion, camera, sensors, and basic autonomy workflows. Use when: (1) making Vector speak or animate, (2) driving or positioning the robot, (3) capturing images from camera, (4) reading sensor data (proximity, touch, battery), (5) building look→reason→act autonomy loops with VLM integration. Requires: Wire-Pod server, Vector robot, Python 3.11+."
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

# VectorClaw MCP Skill

Control your Vector robot through OpenClaw using MCP tools. Enables speech, motion, camera capture, sensor reading, and basic autonomy workflows.

## When to Use

✅ **USE this skill when:**

- Making Vector speak text (TTS)
- Driving Vector off/on charger or to positions
- Capturing images from Vector's camera
- Reading sensor data (proximity, touch, battery status)
- Controlling head and lift actuators
- Building visual autonomy loops (look → reason → act)

## When NOT to Use

❌ **DON'T use this skill when:**

- You don't have a Vector robot set up
- Wire-Pod server is not running
- You need advanced navigation (no SLAM/NAV2 yet)
- You need reliable face/object detection (currently limited)
- You need robust charger return behavior (currently unreliable)

## Prerequisites

1. **Vector robot** with firmware configured
2. **Wire-Pod server** running and accessible
3. **SDK authentication** configured (`~/.anki_vector/sdk_config.ini`)
4. **Environment variable:** `VECTOR_SERIAL` set to your robot's serial

## Setup

### 1. Install Wire-Pod
See: https://github.com/kercre123/wire-pod

### 2. Configure Vector SDK
```bash
python3 -m anki_vector.configure
```

### 3. Set environment variable
```bash
export VECTOR_SERIAL=your-serial-here  # e.g., 00a1546c
```

### 4. Add to mcporter.json
```json
{
  "mcpServers": {
    "vectorclaw": {
      "command": "python3",
      "args": ["-m", "vectorclaw_mcp.server"],
      "env": {
        "VECTOR_SERIAL": "${VECTOR_SERIAL}"
      }
    }
  }
}
```

## Supported Tools (MVP)

| Tool | Description | Status |
|------|-------------|--------|
| `vector_status` | Battery, charging state, status flags | ✅ |
| `vector_say` | Text-to-speech | ✅ |
| `vector_drive_off_charger` | Drive off charging dock | ✅ |
| `vector_drive` | Drive straight or turn | ✅ |
| `vector_head` | Control head angle | ✅ |
| `vector_lift` | Control lift height | ✅ |
| `vector_touch_status` | Read touch sensor state | ✅ |
| `vector_charger_status` | Read charger connection state | ✅ |
| `vector_look` | Capture image (feed path) | ✅ |
| `vector_capture_image` | Capture image (one-shot) | ✅ |
| `vector_proximity_status` | Read proximity sensor | ✅ (with caveats) |
| `vector_pose` | Read current pose | ✅ |

## Known Limitations

- **Drive on charger:** Unreliable timeout behavior
- **Perception detections:** Face/object lists often empty
- **Emergency stop:** Limited by sync motion path

## Autonomy Note

For **look → reason → act** workflows, you need a **VLM or image-analysis tool** in your agent loop. Camera tools provide image bytes; interpretation requires separate vision capability.

## Example Workflows

### Basic speech and motion
```
vector_say("Hello! I'm going to drive forward.")
vector_drive_off_charger()
vector_drive(distance_mm=200, speed=50)
```

### Visual loop (requires VLM)
```
# Capture image
image = vector_look()

# Analyze with vision model (separate tool)
analysis = vision_analyze(image)

# Act based on analysis
if "person" in analysis:
    vector_say("I see you!")
```

## Documentation

- **MCP API Reference:** `docs/MCP_API_REFERENCE.md`
- **SDK Reference:** `docs/VECTOR_SDK_REFERENCE.md`
- **Hardware Smoke Log:** `docs/HARDWARE_SMOKE_LOG.md`
- **GitHub:** https://github.com/danmartinez78/VectorClaw

## License

MIT
