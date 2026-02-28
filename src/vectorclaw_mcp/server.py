"""MCP server entry point for VectorClaw.

Run with::

    python -m vectorclaw_mcp

or via the ``vectorclaw-mcp`` console script installed by *pyproject.toml*.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

# ---------------------------------------------------------------------------
# SDK noise suppression
# ---------------------------------------------------------------------------
# The Wire-Pod SDK emits "Unknown Event type" warnings whenever Wire-Pod sends
# a gRPC event whose type is not present in the SDK's protobuf definitions.
# This is a known SDK/Wire-Pod version-mismatch behaviour (not a bug in our
# code) and is non-fatal.  We suppress it here to keep MCP server logs clean.
# See: anki_vector/events.py EventHandler._handle_event_stream()

class _SuppressUnknownEventType(logging.Filter):
    """Drop the non-fatal 'Unknown Event type' warning emitted by the SDK."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        return "Unknown Event type" not in record.getMessage()


logging.getLogger("anki_vector.events.EventHandler").addFilter(
    _SuppressUnknownEventType()
)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .compat import check_runtime_compatibility
from .robot import robot_manager
from .tool_registry import TOOLS, build_dispatch

logger = logging.getLogger(__name__)

app = Server("vectorclaw-mcp")

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of available tools."""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Dispatch a tool call to the appropriate implementation.

    Tool functions are synchronous (the Vector SDK is synchronous), so we run
    them in a thread pool executor to avoid blocking the event loop.
    """
    loop = asyncio.get_running_loop()

    dispatch: dict[str, Any] = build_dispatch(arguments)

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
    check_runtime_compatibility()
    try:
        asyncio.run(_run())
    finally:
        robot_manager.disconnect()


if __name__ == "__main__":
    main()
