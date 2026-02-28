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
    from vectorclaw_mcp import server

    for logger_name in ("anki_vector.events.EventHandler", "events.EventHandler"):
        sdk_logger = logging.getLogger(logger_name)

        # Verify our specific filter type is registered on the logger.
        suppression_filters = [
            f for f in sdk_logger.filters
            if isinstance(f, server._SuppressUnknownEventType)
        ]
        assert suppression_filters, (
            f"Expected a _SuppressUnknownEventType filter on logger {logger_name!r}"
        )

        filt = suppression_filters[0]

        # The matching SDK warning must be rejected (filter returns False).
        matching = logging.LogRecord(
            name=logger_name,
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="Unknown Event type",
            args=(),
            exc_info=None,
        )
        assert not filt.filter(matching), (
            "Filter should suppress 'Unknown Event type' records"
        )

        # An unrelated warning must pass through (filter returns True).
        unrelated = logging.LogRecord(
            name=logger_name,
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="Connection lost",
            args=(),
            exc_info=None,
        )
        assert filt.filter(unrelated), (
            "Filter must not suppress unrelated warning messages"
        )
