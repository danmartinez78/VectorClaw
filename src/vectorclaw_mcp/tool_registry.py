"""Tool metadata and dispatch construction for the MCP server."""

from __future__ import annotations

from typing import Any

from mcp.types import Tool

from . import tools as _tools


TOOLS: list[Tool] = [
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
        name="vector_drive_on_charger",
        description=(
            "Best-effort attempt to drive Vector back onto its charger. "
            "Experimental: returns ok with already_on_charger=true if already docked."
        ),
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_emergency_stop",
        description="Immediately stop all of Vector's motors. Idempotent and safe to call repeatedly.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_charger_status",
        description="Return charger-related status (is_charging, is_on_charger_platform).",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_touch_status",
        description="Return touch sensor status (last_touch_time, is_being_held).",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_proximity_status",
        description="Return the latest proximity sensor reading (distance_mm, found_object).",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_scan",
        description="Scan the environment by looking around in place.",
        inputSchema={
            "type": "object",
            "properties": {
                "num_rotations": {
                    "type": "integer",
                    "description": "Number of rotation sweeps to perform (default: 1)",
                },
            },
        },
    ),
    Tool(
        name="vector_find_faces",
        description="Search for faces by running the find-faces behavior.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_list_visible_faces",
        description="Return a list of currently visible faces with face_id and name.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_list_visible_objects",
        description="Return a list of currently visible objects (standard and custom).",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_capture_image",
        description="Capture a single image using the preferred camera.capture_single_image path.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_face_detection",
        description="Return a summary of currently detected faces from world state.",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="vector_vision_reset",
        description="Disable all vision modes to reset vision processing state.",
        inputSchema={"type": "object", "properties": {}},
    ),
]


def build_dispatch(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "vector_say": lambda: _tools.vector_say(arguments["text"]),
        "vector_animate": lambda: _tools.vector_animate(arguments["animation_name"]),
        "vector_drive": lambda: _tools.vector_drive(
            speed=arguments.get("speed", 50),
            distance_mm=arguments.get("distance_mm"),
            angle_deg=arguments.get("angle_deg"),
        ),
        "vector_drive_off_charger": _tools.vector_drive_off_charger,
        "vector_drive_on_charger": _tools.vector_drive_on_charger,
        "vector_emergency_stop": _tools.vector_emergency_stop,
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
        "vector_charger_status": _tools.vector_charger_status,
        "vector_touch_status": _tools.vector_touch_status,
        "vector_proximity_status": _tools.vector_proximity_status,
        "vector_scan": lambda: _tools.vector_scan(
            num_rotations=arguments.get("num_rotations", 1)
        ),
        "vector_find_faces": _tools.vector_find_faces,
        "vector_list_visible_faces": _tools.vector_list_visible_faces,
        "vector_list_visible_objects": _tools.vector_list_visible_objects,
        "vector_capture_image": _tools.vector_capture_image,
        "vector_face_detection": _tools.vector_face_detection,
        "vector_vision_reset": _tools.vector_vision_reset,
    }
