"""Tests for vectorclaw_mcp.compat — runtime compatibility guardrails."""

from __future__ import annotations

import sys
import warnings
from importlib.util import find_spec
from unittest.mock import patch

import pytest

from vectorclaw_mcp.compat import check_runtime_compatibility, _COMPAT_MSG


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _py(major: int, minor: int):
    """Return a fake sys.version_info tuple for (major, minor)."""
    return (major, minor, 0, "final", 0)


def _make_find_spec(sdk_available: bool):
    """Create a fake find_spec that returns anki_vector module if available."""
    def fake_find_spec(name):
        if name == "anki_vector" and sdk_available:
            return object()  # truthy
        return None

    return fake_find_spec


def _make_get_dist(dist_name: str | None):
    """Create a fake _get_distribution_for_module that returns the given distribution."""
    def fake_get_dist(module_name: str) -> str | None:
        if module_name == "anki_vector":
            return dist_name
        return None
    return fake_get_dist


def _make_get_version(version: str | None):
    """Create a fake _get_sdk_version that returns the given version."""
    def fake_get_version():
        return version
    return fake_get_version


# ---------------------------------------------------------------------------
# Below-minimum Python version (now 3.11)
# ---------------------------------------------------------------------------

def test_below_minimum_python_raises_systemexit(monkeypatch):
    """Python < 3.11 should raise SystemExit with Python version message."""
    monkeypatch.setattr(sys, "version_info", _py(3, 10))
    monkeypatch.setattr(sys, "version", "3.10.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", return_value=None):
        with pytest.raises(SystemExit) as exc_info:
            check_runtime_compatibility()

    # Should mention Python version requirement, not SDK
    msg = str(exc_info.value)
    assert "Python 3.11" in msg or "3.11+" in msg
    assert "3.10.0" in msg


def test_below_minimum_python_mentions_supported_version(monkeypatch):
    """The SystemExit message should mention the minimum Python version."""
    monkeypatch.setattr(sys, "version_info", _py(3, 9))
    monkeypatch.setattr(sys, "version", "3.9.18 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", return_value=None):
        with pytest.raises(SystemExit) as exc_info:
            check_runtime_compatibility()

    assert "3.11" in str(exc_info.value)


# ---------------------------------------------------------------------------
# wirepod_vector_sdk present (recommended path)
# ---------------------------------------------------------------------------

def test_wirepod_sdk_python311_ok(monkeypatch):
    """Python 3.11 + wirepod_vector_sdk should succeed silently."""
    monkeypatch.setattr(sys, "version_info", _py(3, 11))
    monkeypatch.setattr(sys, "version", "3.11.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", side_effect=_make_find_spec(True)):
        with patch("vectorclaw_mcp.compat._get_distribution_for_module", side_effect=_make_get_dist("wirepod_vector_sdk")):
            with patch("vectorclaw_mcp.compat._get_sdk_version", side_effect=_make_get_version("0.8.1")):
                check_runtime_compatibility()  # must not raise


def test_wirepod_sdk_python312_warns(monkeypatch):
    """Python 3.12 + wirepod_vector_sdk should emit a RuntimeWarning."""
    monkeypatch.setattr(sys, "version_info", _py(3, 12))
    monkeypatch.setattr(sys, "version", "3.12.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", side_effect=_make_find_spec(True)):
        with patch("vectorclaw_mcp.compat._get_distribution_for_module", side_effect=_make_get_dist("wirepod_vector_sdk")):
            with patch("vectorclaw_mcp.compat._get_sdk_version", side_effect=_make_get_version("0.8.1")):
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    check_runtime_compatibility()

    assert any(
        issubclass(w.category, RuntimeWarning) and "3.12" in str(w.message)
        for w in caught
    ), "Expected a RuntimeWarning mentioning Python 3.12"


def test_wirepod_sdk_old_version_raises(monkeypatch):
    """SDK version < 0.8.0 should raise SystemExit."""
    monkeypatch.setattr(sys, "version_info", _py(3, 11))
    monkeypatch.setattr(sys, "version", "3.11.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", side_effect=_make_find_spec(True)):
        with patch("vectorclaw_mcp.compat._get_distribution_for_module", side_effect=_make_get_dist("wirepod_vector_sdk")):
            with patch("vectorclaw_mcp.compat._get_sdk_version", side_effect=_make_get_version("0.6.0")):
                with pytest.raises(SystemExit) as exc_info:
                    check_runtime_compatibility()

    msg = str(exc_info.value)
    assert "0.8.0" in msg
    assert "upgrade" in msg.lower()


def test_wirepod_sdk_missing_version_fails_closed(monkeypatch):
    """Missing __version__ should fail closed with actionable message."""
    monkeypatch.setattr(sys, "version_info", _py(3, 11))
    monkeypatch.setattr(sys, "version", "3.11.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", side_effect=_make_find_spec(True)):
        with patch("vectorclaw_mcp.compat._get_distribution_for_module", side_effect=_make_get_dist("wirepod_vector_sdk")):
            with patch("vectorclaw_mcp.compat._get_sdk_version", side_effect=_make_get_version(None)):
                with pytest.raises(SystemExit) as exc_info:
                    check_runtime_compatibility()

    msg = str(exc_info.value)
    assert "version" in msg.lower()


def test_wirepod_sdk_unparseable_version_fails_closed(monkeypatch):
    """Unparseable version string should fail closed."""
    monkeypatch.setattr(sys, "version_info", _py(3, 11))
    monkeypatch.setattr(sys, "version", "3.11.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", side_effect=_make_find_spec(True)):
        with patch("vectorclaw_mcp.compat._get_distribution_for_module", side_effect=_make_get_dist("wirepod_vector_sdk")):
            with patch("vectorclaw_mcp.compat._get_sdk_version", side_effect=_make_get_version("not-a-version")):
                with pytest.raises(SystemExit) as exc_info:
                    check_runtime_compatibility()

    msg = str(exc_info.value)
    assert "parse" in msg.lower() or "version" in msg.lower()


# ---------------------------------------------------------------------------
# Legacy anki_vector package detection
# ---------------------------------------------------------------------------

def test_legacy_anki_vector_package_rejected(monkeypatch):
    """Legacy anki_vector package should be rejected with helpful message."""
    monkeypatch.setattr(sys, "version_info", _py(3, 11))
    monkeypatch.setattr(sys, "version", "3.11.0 (default)")

    # Module exists but distribution is legacy anki_vector
    with patch("vectorclaw_mcp.compat.find_spec", side_effect=_make_find_spec(True)):
        with patch("vectorclaw_mcp.compat._get_distribution_for_module", side_effect=_make_get_dist("anki_vector")):
            with pytest.raises(SystemExit) as exc_info:
                check_runtime_compatibility()

    msg = str(exc_info.value)
    assert "legacy" in msg.lower()
    assert "wirepod_vector_sdk" in msg
    assert "uninstall" in msg.lower()


def test_unknown_distribution_rejected(monkeypatch):
    """Unknown distribution should be rejected."""
    monkeypatch.setattr(sys, "version_info", _py(3, 11))
    monkeypatch.setattr(sys, "version", "3.11.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", side_effect=_make_find_spec(True)):
        with patch("vectorclaw_mcp.compat._get_distribution_for_module", side_effect=_make_get_dist(None)):
            with pytest.raises(SystemExit) as exc_info:
                check_runtime_compatibility()

    msg = str(exc_info.value)
    assert "wirepod_vector_sdk" in msg


# ---------------------------------------------------------------------------
# No SDK at all
# ---------------------------------------------------------------------------

def test_no_sdk_raises(monkeypatch):
    """With no SDK installed, SystemExit should be raised with install guidance."""
    monkeypatch.setattr(sys, "version_info", _py(3, 11))
    monkeypatch.setattr(sys, "version", "3.11.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", return_value=None):
        with pytest.raises(SystemExit) as exc_info:
            check_runtime_compatibility()

    msg = str(exc_info.value)
    assert _COMPAT_MSG in msg
    assert "wirepod_vector_sdk" in msg


def test_no_sdk_message_suggests_install(monkeypatch):
    """The no-SDK error message should mention pip install."""
    monkeypatch.setattr(sys, "version_info", _py(3, 11))
    monkeypatch.setattr(sys, "version", "3.11.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", return_value=None):
        with pytest.raises(SystemExit) as exc_info:
            check_runtime_compatibility()

    assert "pip install wirepod_vector_sdk" in str(exc_info.value)


# ---------------------------------------------------------------------------
# server.main() calls the guard
# ---------------------------------------------------------------------------

def test_server_main_calls_compat_check(monkeypatch):
    """server.main() must invoke check_runtime_compatibility before running."""
    import vectorclaw_mcp.server as server_mod

    called = []

    def fake_check():
        called.append(True)
        raise SystemExit("stop")  # prevent actually starting the server

    monkeypatch.setattr(server_mod, "check_runtime_compatibility", fake_check)

    with pytest.raises(SystemExit):
        server_mod.main()

    assert called, "check_runtime_compatibility was not called by main()"
