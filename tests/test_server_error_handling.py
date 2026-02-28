from __future__ import annotations

import asyncio
import json
import logging


def test_call_tool_exception_becomes_error(mock_robot, monkeypatch):
    from vectorclaw_mcp import server
    from vectorclaw_mcp import tools as tools_mod

    monkeypatch.setattr(tools_mod, "vector_status", lambda: 1 / 0)

    result = asyncio.run(server.call_tool("vector_status", {}))
    data = json.loads(result[0].text)

    assert data["status"] == "error"
    assert "division by zero" in data["message"]


def test_unknown_event_type_warning_is_suppressed():
    """The SDK emits 'Unknown Event type' for unrecognised Wire-Pod events.

    This is known SDK behaviour (not a VectorClaw bug).  server.py installs a
    logging.Filter on the anki_vector.events.EventHandler logger to suppress
    the message so it doesn't pollute MCP server output.
    """
    # Importing server ensures the filter is installed.
    import vectorclaw_mcp.server  # noqa: F401

    sdk_logger = logging.getLogger("anki_vector.events.EventHandler")

    # Build a dummy LogRecord that mimics what the SDK emits.
    record = logging.LogRecord(
        name="anki_vector.events.EventHandler",
        level=logging.WARNING,
        pathname="",
        lineno=0,
        msg="Unknown Event type",
        args=(),
        exc_info=None,
    )

    # At least one installed filter must reject (return False for) the record.
    assert any(not f.filter(record) for f in sdk_logger.filters), (
        "Expected a filter to suppress the 'Unknown Event type' record"
    )
