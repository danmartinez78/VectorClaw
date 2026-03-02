"""Registry wiring validation tests."""

from __future__ import annotations

import pytest


REQUIRED_TOOLS = {
    "vector_say",
    "vector_animate",
    "vector_drive",
    "vector_drive_off_charger",
    "vector_drive_on_charger",
    "vector_emergency_stop",
    "vector_look",
    "vector_face",
    "vector_pose",
    "vector_cube",
    "vector_status",
    "vector_head",
    "vector_lift",
    "vector_scan",
    "vector_find_faces",
    "vector_list_visible_faces",
    "vector_list_visible_objects",
    "vector_capture_image",
    "vector_face_detection",
    "vector_vision_reset",
    "vector_charger_status",
    "vector_touch_status",
    "vector_proximity_status",
}


def test_all_required_tools_registered():
    from vectorclaw_mcp.tool_registry import TOOLS

    registered = {t.name for t in TOOLS}
    missing = REQUIRED_TOOLS - registered
    assert not missing, f"Tools missing from registry: {missing}"


def test_no_duplicate_tool_names():
    from vectorclaw_mcp.tool_registry import TOOLS

    names = [t.name for t in TOOLS]
    duplicates = {n for n in names if names.count(n) > 1}
    assert not duplicates, f"Duplicate tool names in registry: {duplicates}"


@pytest.mark.parametrize("tool_name", sorted(REQUIRED_TOOLS))
def test_dispatch_entry_exists(tool_name):
    from vectorclaw_mcp.tool_registry import build_dispatch

    dispatch = build_dispatch({})
    assert tool_name in dispatch, f"Tool '{tool_name}' missing from build_dispatch"


def test_drive_on_charger_dispatch_no_timeout(mock_robot):
    """Calling the dispatch entry for vector_drive_on_charger must not raise a TypeError.

    Previously the dispatch lambda passed ``timeout_sec`` to the function, which
    would cause a TypeError after the parameter was removed.  This test exercises
    the full dispatch path (schema → function call) to catch wiring regressions.
    """
    from vectorclaw_mcp.tool_registry import build_dispatch

    dispatch = build_dispatch({})
    result = dispatch["vector_drive_on_charger"]()
    assert result["status"] == "ok"
