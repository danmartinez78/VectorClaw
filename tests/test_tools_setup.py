"""Tests for vectorclaw_mcp.tools_setup — OpenClaw guided setup skill."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _py(major: int, minor: int):
    return (major, minor, 0, "final", 0)


# ---------------------------------------------------------------------------
# _check_python
# ---------------------------------------------------------------------------

class TestCheckPython:
    def test_below_minimum_fails(self, monkeypatch):
        monkeypatch.setattr(sys, "version_info", _py(3, 9))
        from vectorclaw_mcp.tools_setup import _check_python
        result = _check_python()
        assert result["passed"] is False
        assert "3.9" in result["detail"]
        assert "Fix:" in result["detail"]

    def test_recommended_version_passes(self, monkeypatch):
        monkeypatch.setattr(sys, "version_info", _py(3, 11))
        from vectorclaw_mcp.tools_setup import _check_python
        result = _check_python()
        assert result["passed"] is True

    def test_python312_passes_with_warning(self, monkeypatch):
        monkeypatch.setattr(sys, "version_info", _py(3, 12))
        from vectorclaw_mcp.tools_setup import _check_python
        result = _check_python()
        assert result["passed"] is True
        assert "3.12" in result["detail"]
        assert "not officially tested" in result["detail"]


# ---------------------------------------------------------------------------
# _check_sdk
# ---------------------------------------------------------------------------

class TestCheckSdk:
    def test_wirepod_sdk_present(self):
        from vectorclaw_mcp.tools_setup import _check_sdk
        with patch("vectorclaw_mcp.tools_setup.importlib.util.find_spec") as mock_spec:
            mock_spec.side_effect = lambda n: object() if n == "wirepod_vector_sdk" else None
            result = _check_sdk()
        assert result["passed"] is True
        assert "wirepod_vector_sdk" in result["detail"]

    def test_legacy_sdk_on_old_python(self, monkeypatch):
        monkeypatch.setattr(sys, "version_info", _py(3, 9))
        from vectorclaw_mcp.tools_setup import _check_sdk
        with patch("vectorclaw_mcp.tools_setup.importlib.util.find_spec") as mock_spec:
            mock_spec.side_effect = lambda n: object() if n == "anki_vector" else None
            result = _check_sdk()
        assert result["passed"] is True  # old python, no asyncio issue
        assert "Legacy" in result["detail"]

    def test_legacy_sdk_on_python310_fails(self, monkeypatch):
        monkeypatch.setattr(sys, "version_info", _py(3, 10))
        from vectorclaw_mcp.tools_setup import _check_sdk
        with patch("vectorclaw_mcp.tools_setup.importlib.util.find_spec") as mock_spec:
            mock_spec.side_effect = lambda n: object() if n == "anki_vector" else None
            result = _check_sdk()
        assert result["passed"] is False
        assert "Fix:" in result["detail"]

    def test_no_sdk_fails(self):
        from vectorclaw_mcp.tools_setup import _check_sdk
        with patch("vectorclaw_mcp.tools_setup.importlib.util.find_spec", return_value=None):
            result = _check_sdk()
        assert result["passed"] is False
        assert "pip install wirepod_vector_sdk" in result["detail"]


# ---------------------------------------------------------------------------
# _check_import
# ---------------------------------------------------------------------------

class TestCheckImport:
    def test_import_ok(self):
        from vectorclaw_mcp.tools_setup import _check_import
        # anki_vector is already mocked in conftest — import should succeed
        result = _check_import()
        assert result["passed"] is True

    def test_import_fails(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "anki_vector", None)
        from vectorclaw_mcp.tools_setup import _check_import
        result = _check_import()
        assert result["passed"] is False
        assert "Fix:" in result["detail"]


# ---------------------------------------------------------------------------
# _write_openclaw_config
# ---------------------------------------------------------------------------

class TestWriteOpenclawConfig:
    def test_creates_config_with_serial_and_host(self, tmp_path):
        from vectorclaw_mcp.tools_setup import _write_openclaw_config
        cfg = tmp_path / "mcporter.json"
        result = _write_openclaw_config("00a0b1c2", "192.168.1.10", config_path=cfg)
        assert result["passed"] is True
        data = json.loads(cfg.read_text())
        server = data["mcpServers"]["vectorclaw"]
        assert server["env"]["VECTOR_SERIAL"] == "00a0b1c2"
        assert server["env"]["VECTOR_HOST"] == "192.168.1.10"

    def test_creates_config_serial_only(self, tmp_path):
        from vectorclaw_mcp.tools_setup import _write_openclaw_config
        cfg = tmp_path / "mcporter.json"
        result = _write_openclaw_config("00a0b1c2", None, config_path=cfg)
        assert result["passed"] is True
        data = json.loads(cfg.read_text())
        env = data["mcpServers"]["vectorclaw"]["env"]
        assert "VECTOR_HOST" not in env

    def test_merges_into_existing_config(self, tmp_path):
        from vectorclaw_mcp.tools_setup import _write_openclaw_config
        cfg = tmp_path / "mcporter.json"
        existing = {"mcpServers": {"other": {"command": "uvx", "args": ["other-mcp"]}}}
        cfg.write_text(json.dumps(existing))
        result = _write_openclaw_config("00a0b1c2", None, config_path=cfg)
        assert result["passed"] is True
        data = json.loads(cfg.read_text())
        assert "other" in data["mcpServers"]
        assert "vectorclaw" in data["mcpServers"]

    def test_creates_parent_directories(self, tmp_path):
        from vectorclaw_mcp.tools_setup import _write_openclaw_config
        cfg = tmp_path / "deep" / "nested" / "dir" / "mcporter.json"
        result = _write_openclaw_config("00a0b1c2", None, config_path=cfg)
        assert result["passed"] is True
        assert cfg.exists()

    def test_os_error_returns_failure(self, tmp_path):
        from vectorclaw_mcp.tools_setup import _write_openclaw_config
        # Use a path where the parent is a file, not a dir, to trigger OSError
        blocker = tmp_path / "blocker"
        blocker.write_text("not a dir")
        cfg = blocker / "mcporter.json"
        result = _write_openclaw_config("00a0b1c2", None, config_path=cfg)
        assert result["passed"] is False
        assert "Fix:" in result["detail"]


# ---------------------------------------------------------------------------
# _check_connectivity
# ---------------------------------------------------------------------------

class TestCheckConnectivity:
    def _make_sdk(self, connect_exc=None, battery_exc=None):
        sdk = MagicMock()
        robot = MagicMock()
        if connect_exc:
            robot.connect.side_effect = connect_exc
        if battery_exc:
            robot.get_battery_state.side_effect = battery_exc
        sdk.Robot.return_value = robot
        return sdk

    def test_success(self, monkeypatch):
        sdk = self._make_sdk()
        monkeypatch.setitem(sys.modules, "anki_vector", sdk)
        from vectorclaw_mcp.tools_setup import _check_connectivity
        result = _check_connectivity("00a0b1c2", None)
        assert result["passed"] is True

    def test_connection_error(self, monkeypatch):
        sdk = self._make_sdk(connect_exc=ConnectionError("unreachable"))
        monkeypatch.setitem(sys.modules, "anki_vector", sdk)
        from vectorclaw_mcp.tools_setup import _check_connectivity
        result = _check_connectivity("00a0b1c2", "192.168.1.1")
        assert result["passed"] is False
        assert "Fix:" in result["detail"]
        assert "Wire-Pod" in result["detail"]

    def test_timeout_error(self, monkeypatch):
        sdk = self._make_sdk(connect_exc=TimeoutError("timeout"))
        monkeypatch.setitem(sys.modules, "anki_vector", sdk)
        from vectorclaw_mcp.tools_setup import _check_connectivity
        result = _check_connectivity("00a0b1c2", None)
        assert result["passed"] is False

    def test_runtime_error(self, monkeypatch):
        sdk = self._make_sdk(connect_exc=RuntimeError("bad config"))
        monkeypatch.setitem(sys.modules, "anki_vector", sdk)
        from vectorclaw_mcp.tools_setup import _check_connectivity
        result = _check_connectivity("00a0b1c2", None)
        assert result["passed"] is False
        assert "anki_vector.configure" in result["detail"]

    def test_battery_call_fails(self, monkeypatch):
        sdk = self._make_sdk(battery_exc=RuntimeError("battery error"))
        monkeypatch.setitem(sys.modules, "anki_vector", sdk)
        from vectorclaw_mcp.tools_setup import _check_connectivity
        result = _check_connectivity("00a0b1c2", None)
        assert result["passed"] is False
        assert "get_battery_state" in result["detail"]

    def test_no_sdk_returns_failure(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "anki_vector", None)
        from vectorclaw_mcp.tools_setup import _check_connectivity
        result = _check_connectivity("00a0b1c2", None)
        assert result["passed"] is False
        assert "pip install wirepod_vector_sdk" in result["detail"]


# ---------------------------------------------------------------------------
# _smoke_test
# ---------------------------------------------------------------------------

class TestSmokeTest:
    def _make_sdk(self, connect_exc=None, battery_exc=None, head_exc=None):
        sdk = MagicMock()
        util = MagicMock()
        util.degrees = lambda v: v
        sdk.util = util
        robot = MagicMock()
        if connect_exc:
            robot.connect.side_effect = connect_exc
        if battery_exc:
            robot.get_battery_state.side_effect = battery_exc
        if head_exc:
            robot.behavior.set_head_angle.side_effect = head_exc
        sdk.Robot.return_value = robot
        return sdk

    def test_all_pass(self, monkeypatch):
        sdk = self._make_sdk()
        monkeypatch.setitem(sys.modules, "anki_vector", sdk)
        monkeypatch.setitem(sys.modules, "anki_vector.util", sdk.util)
        from vectorclaw_mcp.tools_setup import _smoke_test
        result = _smoke_test("00a0b1c2", None)
        assert result["passed"] is True
        assert len(result["steps"]) == 2

    def test_battery_fail(self, monkeypatch):
        sdk = self._make_sdk(battery_exc=RuntimeError("dead"))
        monkeypatch.setitem(sys.modules, "anki_vector", sdk)
        monkeypatch.setitem(sys.modules, "anki_vector.util", sdk.util)
        from vectorclaw_mcp.tools_setup import _smoke_test
        result = _smoke_test("00a0b1c2", None)
        assert result["passed"] is False
        assert any(not s["passed"] for s in result["steps"])

    def test_connect_fail_returns_failure(self, monkeypatch):
        sdk = self._make_sdk(connect_exc=OSError("network"))
        monkeypatch.setitem(sys.modules, "anki_vector", sdk)
        monkeypatch.setitem(sys.modules, "anki_vector.util", sdk.util)
        from vectorclaw_mcp.tools_setup import _smoke_test
        result = _smoke_test("00a0b1c2", None)
        assert result["passed"] is False
        assert "could not connect" in result["detail"]

    def test_no_sdk_returns_failure(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "anki_vector", None)
        from vectorclaw_mcp.tools_setup import _smoke_test
        result = _smoke_test("00a0b1c2", None)
        assert result["passed"] is False


# ---------------------------------------------------------------------------
# vector_setup (integration-level)
# ---------------------------------------------------------------------------

class TestVectorSetup:
    def _patch_stages(self, monkeypatch, *, python=True, sdk=True, imp=True, config=True, conn=True, smoke=True):
        """Patch all internal stage helpers with pass/fail booleans."""
        import vectorclaw_mcp.tools_setup as mod

        monkeypatch.setattr(mod, "_check_python", lambda: {"passed": python, "detail": "python"})
        monkeypatch.setattr(mod, "_check_sdk", lambda: {"passed": sdk, "detail": "sdk"})
        monkeypatch.setattr(mod, "_check_import", lambda: {"passed": imp, "detail": "import"})
        monkeypatch.setattr(
            mod,
            "_write_openclaw_config",
            lambda serial, host, config_path: {"passed": config, "detail": "config"},
        )
        monkeypatch.setattr(
            mod,
            "_check_connectivity",
            lambda serial, host: {"passed": conn, "detail": "conn"},
        )
        monkeypatch.setattr(
            mod,
            "_smoke_test",
            lambda serial, host: {"passed": smoke, "detail": "smoke", "steps": []},
        )

    def test_missing_serial_returns_error(self):
        from vectorclaw_mcp.tools_setup import vector_setup
        result = vector_setup("")
        assert result["status"] == "error"
        assert "VECTOR_SERIAL" in result["summary"]

    def test_whitespace_serial_returns_error(self):
        from vectorclaw_mcp.tools_setup import vector_setup
        result = vector_setup("   ")
        assert result["status"] == "error"

    def test_all_stages_pass_returns_ok(self, monkeypatch, tmp_path):
        self._patch_stages(monkeypatch)
        from vectorclaw_mcp.tools_setup import vector_setup
        result = vector_setup("00a0b1c2", _config_path=tmp_path / "m.json")
        assert result["status"] == "ok"
        assert "✅" in result["summary"]
        assert len(result["stages"]) == 6

    def test_sdk_failure_propagates(self, monkeypatch, tmp_path):
        self._patch_stages(monkeypatch, sdk=False)
        from vectorclaw_mcp.tools_setup import vector_setup
        result = vector_setup("00a0b1c2", _config_path=tmp_path / "m.json")
        assert result["status"] == "error"
        assert "❌" in result["summary"]

    def test_connectivity_failure_skips_smoke(self, monkeypatch, tmp_path):
        self._patch_stages(monkeypatch, conn=False)
        from vectorclaw_mcp.tools_setup import vector_setup
        result = vector_setup("00a0b1c2", _config_path=tmp_path / "m.json")
        assert result["status"] == "error"
        smoke_stage = next(s for s in result["stages"] if s["stage"] == "smoke_test")
        assert smoke_stage["passed"] is False
        assert "Skipped" in smoke_stage["detail"]

    def test_host_passed_to_stages(self, monkeypatch, tmp_path):
        calls = []

        import vectorclaw_mcp.tools_setup as mod
        monkeypatch.setattr(mod, "_check_python", lambda: {"passed": True, "detail": ""})
        monkeypatch.setattr(mod, "_check_sdk", lambda: {"passed": True, "detail": ""})
        monkeypatch.setattr(mod, "_check_import", lambda: {"passed": True, "detail": ""})
        monkeypatch.setattr(
            mod,
            "_write_openclaw_config",
            lambda serial, host, config_path: {"passed": True, "detail": ""},
        )

        def fake_conn(serial, host):
            calls.append((serial, host))
            return {"passed": True, "detail": ""}

        monkeypatch.setattr(mod, "_check_connectivity", fake_conn)
        monkeypatch.setattr(
            mod,
            "_smoke_test",
            lambda serial, host: {"passed": True, "detail": "", "steps": []},
        )

        from vectorclaw_mcp.tools_setup import vector_setup
        vector_setup("00a0b1c2", "192.168.1.55", _config_path=tmp_path / "m.json")
        assert calls == [("00a0b1c2", "192.168.1.55")]

    def test_next_steps_on_success(self, monkeypatch, tmp_path):
        self._patch_stages(monkeypatch)
        from vectorclaw_mcp.tools_setup import vector_setup
        result = vector_setup("00a0b1c2", _config_path=tmp_path / "m.json")
        assert isinstance(result["next_steps"], list)
        assert len(result["next_steps"]) > 0

    def test_next_steps_on_failure_contain_remediation(self, monkeypatch, tmp_path):
        self._patch_stages(monkeypatch, sdk=False)
        from vectorclaw_mcp.tools_setup import vector_setup
        result = vector_setup("00a0b1c2", _config_path=tmp_path / "m.json")
        # next_steps is populated with the failed stage details
        assert "sdk" in " ".join(result["next_steps"]).lower()

    def test_serial_stripped(self, monkeypatch, tmp_path):
        self._patch_stages(monkeypatch)
        from vectorclaw_mcp.tools_setup import vector_setup
        result = vector_setup("  00a0b1c2  ", _config_path=tmp_path / "m.json")
        assert "00a0b1c2" in result["summary"]


# ---------------------------------------------------------------------------
# Tool registry integration
# ---------------------------------------------------------------------------

def test_vector_setup_registered_in_tool_registry():
    from vectorclaw_mcp.tool_registry import TOOLS
    names = [t.name for t in TOOLS]
    assert "vector_setup" in names


def test_vector_setup_in_tools_module():
    from vectorclaw_mcp import tools
    assert hasattr(tools, "vector_setup")


def test_vector_setup_dispatch(tmp_path, monkeypatch):
    """build_dispatch routes vector_setup correctly."""
    import vectorclaw_mcp.tools_setup as setup_mod

    called_with = []

    def fake_setup(serial, host=None, _config_path=None):
        called_with.append((serial, host))
        return {"status": "ok", "summary": "ok", "stages": [], "next_steps": []}

    monkeypatch.setattr(setup_mod, "vector_setup", fake_setup)
    # Also patch the imported reference in tool_registry
    import vectorclaw_mcp.tool_registry as reg_mod
    monkeypatch.setattr(reg_mod, "_vector_setup", fake_setup)

    from vectorclaw_mcp.tool_registry import build_dispatch
    dispatch = build_dispatch({"serial": "TESTSERIAL", "host": "10.0.0.1"})
    dispatch["vector_setup"]()
    assert called_with == [("TESTSERIAL", "10.0.0.1")]
