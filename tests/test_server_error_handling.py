from __future__ import annotations

import asyncio
import json
import logging


def test_suppress_unknown_event_type_filter():
    """_SuppressUnknownEventType must block the noisy SDK warning."""
    from vectorclaw_mcp.server import _SuppressUnknownEventType

    f = _SuppressUnknownEventType()

    noisy = logging.LogRecord(
        name="anki_vector.events.EventHandler",
        level=logging.WARNING,
        pathname="",
        lineno=0,
        msg="Unknown Event type: 42",
        args=(),
        exc_info=None,
    )
    assert f.filter(noisy) is False

    normal = logging.LogRecord(
        name="anki_vector.events.EventHandler",
        level=logging.WARNING,
        pathname="",
        lineno=0,
        msg="Some other warning",
        args=(),
        exc_info=None,
    )
    assert f.filter(normal) is True


def test_suppress_filter_registered_on_sdk_logger():
    """The filter must be attached to the anki_vector.events.EventHandler logger.

    Importing server triggers the module-level addFilter() call, so this test
    verifies registration as a side-effect of that import.
    """
    from vectorclaw_mcp import server  # noqa: F401 — import for side-effect registration

    from vectorclaw_mcp.server import _SuppressUnknownEventType

    sdk_logger = logging.getLogger("anki_vector.events.EventHandler")
    assert any(
        isinstance(f, _SuppressUnknownEventType) for f in sdk_logger.filters
    ), "Expected _SuppressUnknownEventType to be registered on the SDK logger"


def test_call_tool_exception_becomes_error(mock_robot, monkeypatch):
    from vectorclaw_mcp import server
    from vectorclaw_mcp import tools as tools_mod

    monkeypatch.setattr(tools_mod, "vector_status", lambda: 1 / 0)

    result = asyncio.run(server.call_tool("vector_status", {}))
    data = json.loads(result[0].text)

    assert data["status"] == "error"
    assert "division by zero" in data["message"]
