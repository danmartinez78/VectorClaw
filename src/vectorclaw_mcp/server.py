"""MCP server entry point for VectorClaw.

Run with::

    python -m vectorclaw_mcp

or via the ``vectorclaw-mcp`` console script installed by *pyproject.toml*.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    TextContent,
    Tool,
)

from . import tools as _tools
from .robot import robot_manager

logger = logging.getLogger(__name__)

app = Server("vectorclaw-mcp")

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

_TOOLS: list[Tool] = [
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
                    "description": (
                        "Animation identifier, e.g. 'anim_eyepose_happy_content_01'"
                    ),
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
                "angle_deg": {
                    "type": "number",
                    "description": "Turn angle in degrees (positive = left)",
                },
            },
        },
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
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of available tools."""
    return _TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Dispatch a tool call to the appropriate implementation.

    Tool functions are synchronous (the Vector SDK is synchronous), so we run
    them in a thread pool executor to avoid blocking the event loop.
    """
    loop = asyncio.get_running_loop()

    dispatch: dict[str, Any] = {
        "vector_say": lambda: _tools.vector_say(arguments["text"]),
        "vector_animate": lambda: _tools.vector_animate(arguments["animation_name"]),
        "vector_drive": lambda: _tools.vector_drive(
            distance_mm=arguments.get("distance_mm"),
            angle_deg=arguments.get("angle_deg"),
        ),
        "vector_look": _tools.vector_look,
        "vector_face": lambda: _tools.vector_face(
            arguments["image_base64"],
            duration_sec=arguments.get("duration_sec", 5.0),
        ),
        "vector_pose": _tools.vector_pose,
        "vector_cube": lambda: _tools.vector_cube(arguments["action"]),
        "vector_status": _tools.vector_status,
    }

    try:
        handler = dispatch.get(name)
        if handler is None:
            result: dict[str, Any] = {
                "status": "error",
                "message": f"Unknown tool: {name!r}",
            }
        else:
            result = await loop.run_in_executor(None, handler)
    except Exception as exc:
        logger.exception("Tool %r raised an exception", name)
        result = {"status": "error", "message": str(exc)}

    import json

    return [TextContent(type="text", text=json.dumps(result))]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def _run() -> None:
    """Run the MCP server over stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main() -> None:
    """Synchronous entry point (used by the console script)."""
    try:
        asyncio.run(_run())
    finally:
        robot_manager.disconnect()


if __name__ == "__main__":
    main()
