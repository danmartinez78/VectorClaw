"""Tool metadata and dispatch construction for the MCP server."""

from __future__ import annotations

from typing import Any

from mcp.types import Tool

from . import setup_skill as _setup_skill
from . import tools as _tools
from . import tools_motion as _tools_motion
from . import tools_perception as _tools_perception


TOOLS: list[Tool] = [
    Tool(
        name="vector_setup",
        description=(
            "Run the VectorClaw setup wizard: validate Python compatibility, "
            "install the Vector SDK if missing, write OpenClaw config, "
            "check robot connectivity, and run smoke tests. "
            "Returns a structured PASS/FAIL report with actionable remediation steps. "
            "Call this tool first when setting up VectorClaw for a new user."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "serial": {
                    "type": "string",
                    "description": (
                        "Robot serial number (required if VECTOR_SERIAL env var not set). "
                        "Find it in the Vector app under Settings → My Vector → Serial Number."
                    ),
                },
                "host": {
                    "type": "string",
                    "description": (
                        "Robot IP address (optional). "
                        "Only needed when auto-discovery via Wire-Pod does not work."
                    ),
                },
                "write_config": {
                    "type": "boolean",
                    "description": (
                        "Write VECTOR_SERIAL/VECTOR_HOST to "
                        "~/.openclaw/workspace/config/mcporter.json (default: true)."
                    ),
                },
                "install_sdk": {
                    "type": "boolean",
                    "description": (
                        "Attempt to install wirepod_vector_sdk when the SDK is absent "
                        "(default: true)."
                    ),
                },
                "run_connectivity": {
                    "type": "boolean",
                    "description": "Run a live connectivity check against the robot (default: true).",
                },
                "run_smoke": {
                    "type": "boolean",
                    "description": (
                        "Run a status read and harmless head-move as a final smoke test "
                        "(default: true)."
                    ),
                },
            },
        },
    ),
    Tool(
        name="vector_say",
        description="Make the Anki Vector robot speak text aloud.",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text for the robot to speak"},
            },
            "required": ["text"],
        },
    ),
    Tool(
        name="vector_animate",
        description="Play a named animation on the robot.",
        inputSchema={
            "type": "object",
            "properties": {
                "animation_name": {
                    "type": "string",
                    "description": "Animation identifier, e.g. 'anim_eyepose_happy_content_01'",
                },
            },
            "required": ["animation_name"],
        },
    ),
    Tool(
        name="vector_drive",
        description="Move the robot straight and/or turn it in place.",
        inputSchema={
            "type": "object",
            "properties": {
                "distance_mm": {
                    "type": "number",
                    "description": "Distance in millimetres (positive = forward)",
                },
                "speed": {
                    "type": "number",
                    "description": "Drive speed in mm/s (default: 50)",
                },
                "angle_deg": {
                    "type": "number",
                    "description": "Turn angle in degrees (positive = left)",
                },
            },
        },
    ),
    Tool(
        name="vector_drive_off_charger",
        description="Drive the robot off its charger.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_drive_on_charger",
        description=(
            "Drive Vector back onto its charger. "
            "Returns immediately (already_on_charger: true) if Vector is already docked. "
            "Requires the charger to be in Vector's recent world model; use vector_scan first "
            "if the charger may not have been recently observed."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_emergency_stop",
        description="Immediately stop all Vector motors.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_look",
        description="Capture an image from the robot's front camera.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_face",
        description="Display a custom image on the robot's face screen (144×108).",
        inputSchema={
            "type": "object",
            "properties": {
                "image_base64": {
                    "type": "string",
                    "description": "Base64-encoded image to display on the robot's face",
                },
                "duration_sec": {
                    "type": "number",
                    "description": "How long to display the image in seconds (default: 5.0)",
                },
            },
            "required": ["image_base64"],
        },
    ),
    Tool(
        name="vector_pose",
        description="Get the robot's current position and orientation.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_cube",
        description="Interact with Vector's cube accessory.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["dock", "pickup", "drop", "roll"],
                    "description": "Action to perform with the cube",
                },
            },
            "required": ["action"],
        },
    ),
    Tool(
        name="vector_status",
        description="Get robot status (battery level, charging state, etc.).",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_head",
        description=(
            "Set Vector's head angle in degrees. "
            "Input is clamped to the safe range (-22.0 to 45.0 degrees)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "angle_deg": {
                    "type": "number",
                    "description": "Head angle in degrees (-22.0 to 45.0; clamped if out of range)",
                },
            },
            "required": ["angle_deg"],
        },
    ),
    Tool(
        name="vector_lift",
        description=(
            "Set Vector's lift/arm height (0.0 = lowest, 1.0 = highest). "
            "Input is clamped to the valid range 0.0–1.0."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "height": {
                    "type": "number",
                    "description": "Lift height as a normalised value (0.0–1.0; clamped if out of range)",
                },
            },
            "required": ["height"],
        },
    ),
    Tool(
        name="vector_scan",
        description="Make Vector look around in place to scan the environment.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_find_faces",
        description="Make Vector actively search for faces in the environment.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_list_visible_faces",
        description="Return the list of faces currently visible to Vector.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_list_visible_objects",
        description="Return the list of objects currently visible to Vector.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_capture_image",
        description="Capture a single camera frame via camera.capture_single_image.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_face_detection",
        description="Return a summary of currently visible faces (no raw image data).",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_enable_face_detection",
        description="Enable or disable face detection on Vector's vision system.",
        inputSchema={
            "type": "object",
            "properties": {
                "enable": {
                    "type": "boolean",
                    "description": "True to enable face detection, False to disable (default: true)",
                },
            },
        },
    ),
    Tool(
        name="vector_enable_motion_detection",
        description="Enable or disable motion detection on Vector's vision system.",
        inputSchema={
            "type": "object",
            "properties": {
                "enable": {
                    "type": "boolean",
                    "description": "True to enable motion detection, False to disable (default: true)",
                },
            },
        },
    ),
    Tool(
        name="vector_vision_status",
        description="Return current vision mode status flags (face detection, motion detection, etc.).",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_vision_reset",
        description="Disable all active vision modes via vision.disable_all_vision_modes.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_charger_status",
        description="Return charger and battery state.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_touch_status",
        description="Return touch-sensor reading from Vector's back capacitive sensor.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_proximity_status",
        description="Return proximity sensor reading from Vector's front IR sensor.",
        inputSchema={"type": "object", "properties": {}},
    ),
]


def build_dispatch(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "vector_setup": lambda: _setup_skill.run_setup(
            serial=arguments.get("serial"),
            host=arguments.get("host"),
            write_config=arguments.get("write_config", True),
            install_sdk_if_missing=arguments.get("install_sdk", True),
            run_connectivity=arguments.get("run_connectivity", True),
            run_smoke=arguments.get("run_smoke", True),
        ),
        "vector_say": lambda: _tools.vector_say(arguments["text"]),
        "vector_animate": lambda: _tools.vector_animate(arguments["animation_name"]),
        "vector_drive": lambda: _tools.vector_drive(
            speed=arguments.get("speed", 50),
            distance_mm=arguments.get("distance_mm"),
            angle_deg=arguments.get("angle_deg"),
        ),
        "vector_drive_off_charger": _tools.vector_drive_off_charger,
        "vector_drive_on_charger": _tools_motion.vector_drive_on_charger,
        "vector_emergency_stop": _tools_motion.vector_emergency_stop,
        "vector_look": _tools.vector_look,
        "vector_face": lambda: _tools.vector_face(
            arguments["image_base64"],
            duration_sec=arguments.get("duration_sec", 5.0),
        ),
        "vector_pose": _tools.vector_pose,
        "vector_cube": lambda: _tools.vector_cube(arguments["action"]),
        "vector_status": _tools.vector_status,
        "vector_head": lambda: _tools.vector_head(arguments["angle_deg"]),
        "vector_lift": lambda: _tools.vector_lift(arguments["height"]),
        "vector_scan": _tools_perception.vector_scan,
        "vector_find_faces": _tools_perception.vector_find_faces,
        "vector_list_visible_faces": _tools_perception.vector_list_visible_faces,
        "vector_list_visible_objects": _tools_perception.vector_list_visible_objects,
        "vector_capture_image": _tools_perception.vector_capture_image,
        "vector_face_detection": _tools_perception.vector_face_detection,
        "vector_enable_face_detection": lambda: _tools_perception.vector_enable_face_detection(
            enable=arguments.get("enable", True),
        ),
        "vector_enable_motion_detection": lambda: _tools_perception.vector_enable_motion_detection(
            enable=arguments.get("enable", True),
        ),
        "vector_vision_status": _tools_perception.vector_vision_status,
        "vector_vision_reset": _tools_perception.vector_vision_reset,
        "vector_charger_status": _tools_perception.vector_charger_status,
        "vector_touch_status": _tools_perception.vector_touch_status,
        "vector_proximity_status": _tools_perception.vector_proximity_status,
    }
