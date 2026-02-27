from __future__ import annotations

import asyncio
import json


def test_call_tool_exception_becomes_error(mock_robot, monkeypatch):
    from vectorclaw_mcp import server
    from vectorclaw_mcp import tools as tools_mod

    monkeypatch.setattr(tools_mod, "vector_status", lambda: 1 / 0)

    result = asyncio.run(server.call_tool("vector_status", {}))
    data = json.loads(result[0].text)

    assert data["status"] == "error"
    assert "division by zero" in data["message"]
