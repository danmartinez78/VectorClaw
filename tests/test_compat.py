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


def _make_find_spec(sdk_available: bool, version: str | None = "0.8.1"):
    """Create a fake find_spec that returns anki_vector module if available."""
    def fake_find_spec(name):
        if name == "anki_vector" and sdk_available:
            return object()  # truthy
        return None

    return fake_find_spec


def _make_get_version(version: str | None):
    """Create a fake _get_sdk_version that returns the given version."""
    def fake_get_version():
        return version
    return fake_get_version


# ---------------------------------------------------------------------------
# Below-minimum Python version
# ---------------------------------------------------------------------------

def test_below_minimum_python_raises_systemexit(monkeypatch):
    """Python < 3.10 should raise SystemExit with the compatibility message."""
    monkeypatch.setattr(sys, "version_info", _py(3, 9))
    monkeypatch.setattr(sys, "version", "3.9.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", return_value=None):
        with pytest.raises(SystemExit) as exc_info:
            check_runtime_compatibility()

    assert _COMPAT_MSG in str(exc_info.value)
    assert "3.9.0" in str(exc_info.value)


def test_below_minimum_python_mentions_supported_version(monkeypatch):
    """The SystemExit message should mention the recommended Python version."""
    monkeypatch.setattr(sys, "version_info", _py(3, 8))
    monkeypatch.setattr(sys, "version", "3.8.18 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", return_value=None):
        with pytest.raises(SystemExit) as exc_info:
            check_runtime_compatibility()

    assert "3.10" in str(exc_info.value)


# ---------------------------------------------------------------------------
# wirepod_vector_sdk present (recommended path)
# Note: wirepod_vector_sdk installs as the 'anki_vector' namespace
# ---------------------------------------------------------------------------

def test_wirepod_sdk_python311_ok(monkeypatch):
    """Python 3.11 + wirepod_vector_sdk should succeed silently."""
    monkeypatch.setattr(sys, "version_info", _py(3, 11))
    monkeypatch.setattr(sys, "version", "3.11.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", side_effect=_make_find_spec(True, "0.8.1")):
        with patch("vectorclaw_mcp.compat._get_sdk_version", side_effect=_make_get_version("0.8.1")):
            check_runtime_compatibility()  # must not raise


def test_wirepod_sdk_python312_warns(monkeypatch):
    """Python 3.12 + wirepod_vector_sdk should emit a RuntimeWarning."""
    monkeypatch.setattr(sys, "version_info", _py(3, 12))
    monkeypatch.setattr(sys, "version", "3.12.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", side_effect=_make_find_spec(True, "0.8.1")):
        with patch("vectorclaw_mcp.compat._get_sdk_version", side_effect=_make_get_version("0.8.1")):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                check_runtime_compatibility()

    assert any(
        issubclass(w.category, RuntimeWarning) and "3.12" in str(w.message)
        for w in caught
    ), "Expected a RuntimeWarning mentioning Python 3.12"


def test_wirepod_sdk_python310_ok(monkeypatch):
    """Python 3.10 + wirepod_vector_sdk should succeed silently."""
    monkeypatch.setattr(sys, "version_info", _py(3, 10))
    monkeypatch.setattr(sys, "version", "3.10.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", side_effect=_make_find_spec(True, "0.8.1")):
        with patch("vectorclaw_mcp.compat._get_sdk_version", side_effect=_make_get_version("0.8.1")):
            check_runtime_compatibility()  # must not raise


def test_wirepod_sdk_old_version_raises(monkeypatch):
    """SDK version < 0.8.0 should raise SystemExit."""
    monkeypatch.setattr(sys, "version_info", _py(3, 11))
    monkeypatch.setattr(sys, "version", "3.11.0 (default)")

    with patch("vectorclaw_mcp.compat.find_spec", side_effect=_make_find_spec(True, "0.6.0")):
        with patch("vectorclaw_mcp.compat._get_sdk_version", side_effect=_make_get_version("0.6.0")):
            with pytest.raises(SystemExit) as exc_info:
                check_runtime_compatibility()

    msg = str(exc_info.value)
    assert "0.8.0" in msg
    assert "upgrade" in msg.lower()


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
