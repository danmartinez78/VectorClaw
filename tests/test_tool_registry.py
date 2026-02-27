"""Registry-level tests: no duplicate names, all tools have dispatch entries."""

from __future__ import annotations


def test_no_duplicate_tool_names():
    from vectorclaw_mcp.tool_registry import TOOLS

    names = [t.name for t in TOOLS]
    assert len(names) == len(set(names)), f"Duplicate tool names: {[n for n in names if names.count(n) > 1]}"


def test_all_tools_have_dispatch_entry():
    from vectorclaw_mcp.tool_registry import TOOLS, build_dispatch

    dispatch = build_dispatch({})
    tool_names = {t.name for t in TOOLS}
    dispatch_names = set(dispatch.keys())
    missing = tool_names - dispatch_names
    assert not missing, f"Tools missing from dispatch: {missing}"


def test_no_extra_dispatch_entries():
    from vectorclaw_mcp.tool_registry import TOOLS, build_dispatch

    dispatch = build_dispatch({})
    tool_names = {t.name for t in TOOLS}
    dispatch_names = set(dispatch.keys())
    extra = dispatch_names - tool_names
    assert not extra, f"Dispatch entries without a Tool schema: {extra}"


def test_all_tools_have_input_schema():
    from vectorclaw_mcp.tool_registry import TOOLS

    for tool in TOOLS:
        assert tool.inputSchema is not None, f"Tool {tool.name!r} is missing inputSchema"
        assert tool.inputSchema.get("type") == "object", (
            f"Tool {tool.name!r} inputSchema should be type=object"
        )
