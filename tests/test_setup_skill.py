"""Tests for the VectorClaw OpenClaw setup skill."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vectorclaw_mcp import setup_skill


# ---------------------------------------------------------------------------
# validate_python_version
# ---------------------------------------------------------------------------


class TestValidatePythonVersion:
    def test_current_python_passes(self):
        result = setup_skill.validate_python_version()
        assert result["passed"] is True
        assert result["check"] == "python_version"
        assert result["fix"] is None or isinstance(result["fix"], str)

    def test_old_python_fails(self, monkeypatch):
        monkeypatch.setattr(sys, "version_info", (3, 9, 0, "final", 0))
        result = setup_skill.validate_python_version()
        assert result["passed"] is False
        assert result["check"] == "python_version"
        assert result["fix"] is not None

    def test_minimum_python_passes_with_warning(self, monkeypatch):
        monkeypatch.setattr(sys, "version_info", (3, 10, 0, "final", 0))
        result = setup_skill.validate_python_version()
        assert result["passed"] is True
        assert result["check"] == "python_version"
        # A "fix" hint is returned even when passed, to nudge upgrade
        assert result["fix"] is not None

    def test_recommended_python_passes_cleanly(self, monkeypatch):
        monkeypatch.setattr(sys, "version_info", (3, 11, 0, "final", 0))
        result = setup_skill.validate_python_version()
        assert result["passed"] is True
        assert result["fix"] is None


# ---------------------------------------------------------------------------
# validate_sdk
# ---------------------------------------------------------------------------


class TestValidateSdk:
    def test_sdk_available_passes(self):
        # conftest installs a mock anki_vector, so the import should succeed
        result = setup_skill.validate_sdk()
        assert result["passed"] is True
        assert result["check"] == "sdk_import"
        assert result["fix"] is None

    def test_sdk_missing_fails(self, monkeypatch):
        # Remove anki_vector from sys.modules so the import raises ImportError
        monkeypatch.delitem(sys.modules, "anki_vector", raising=False)
        with patch.dict(sys.modules, {"anki_vector": None}):
            result = setup_skill.validate_sdk()
        assert result["passed"] is False
        assert result["check"] == "sdk_import"
        assert result["fix"] is not None
        assert "pip install" in result["fix"] or "git+" in result["fix"]


# ---------------------------------------------------------------------------
# install_sdk
# ---------------------------------------------------------------------------


class TestInstallSdk:
    def test_successful_install(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            result = setup_skill.install_sdk()
        assert result["passed"] is True
        assert result["check"] == "sdk_install"

    def test_failed_install(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "No matching distribution found"
        with patch("subprocess.run", return_value=mock_result):
            result = setup_skill.install_sdk()
        assert result["passed"] is False
        assert result["check"] == "sdk_install"
        assert result["fix"] is not None

    def test_install_timeout(self):
        import subprocess

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("pip", 120)):
            result = setup_skill.install_sdk()
        assert result["passed"] is False
        assert "timed out" in result["detail"]

    def test_install_exception(self):
        with patch("subprocess.run", side_effect=OSError("no pip")):
            result = setup_skill.install_sdk()
        assert result["passed"] is False
        assert result["fix"] is not None


# ---------------------------------------------------------------------------
# write_openclaw_config
# ---------------------------------------------------------------------------


class TestWriteOpenclawConfig:
    def test_writes_serial_and_host(self, tmp_path):
        config_path = tmp_path / "mcporter.json"
        result = setup_skill.write_openclaw_config(
            "00e20142", "192.168.1.100", config_path=config_path
        )
        assert result["passed"] is True
        assert result["check"] == "write_config"
        data = json.loads(config_path.read_text())
        assert data["env"]["VECTOR_SERIAL"] == "00e20142"
        assert data["env"]["VECTOR_HOST"] == "192.168.1.100"

    def test_writes_serial_without_host(self, tmp_path):
        config_path = tmp_path / "mcporter.json"
        result = setup_skill.write_openclaw_config("00e20142", config_path=config_path)
        assert result["passed"] is True
        data = json.loads(config_path.read_text())
        assert data["env"]["VECTOR_SERIAL"] == "00e20142"
        assert "VECTOR_HOST" not in data["env"]

    def test_removes_host_when_not_provided(self, tmp_path):
        config_path = tmp_path / "mcporter.json"
        config_path.write_text(
            json.dumps({"env": {"VECTOR_SERIAL": "old", "VECTOR_HOST": "1.2.3.4"}})
        )
        result = setup_skill.write_openclaw_config(
            "00e20142", host=None, config_path=config_path
        )
        assert result["passed"] is True
        data = json.loads(config_path.read_text())
        assert "VECTOR_HOST" not in data["env"]

    def test_merges_into_existing_config(self, tmp_path):
        config_path = tmp_path / "mcporter.json"
        config_path.write_text(
            json.dumps({"other_key": "preserved", "env": {"OTHER": "setting"}})
        )
        result = setup_skill.write_openclaw_config("00e20142", config_path=config_path)
        assert result["passed"] is True
        data = json.loads(config_path.read_text())
        assert data["other_key"] == "preserved"
        assert data["env"]["OTHER"] == "setting"
        assert data["env"]["VECTOR_SERIAL"] == "00e20142"

    def test_recovers_from_corrupt_existing_config(self, tmp_path):
        config_path = tmp_path / "mcporter.json"
        config_path.write_text("not valid json {{{{")
        result = setup_skill.write_openclaw_config("00e20142", config_path=config_path)
        assert result["passed"] is True
        data = json.loads(config_path.read_text())
        assert data["env"]["VECTOR_SERIAL"] == "00e20142"

    def test_creates_parent_directories(self, tmp_path):
        config_path = tmp_path / "deep" / "nested" / "mcporter.json"
        result = setup_skill.write_openclaw_config("00e20142", config_path=config_path)
        assert result["passed"] is True
        assert config_path.exists()

    def test_handles_write_error(self, tmp_path):
        # Point to a path whose parent directory does not exist and cannot be
        # created (simulate permission failure by making parent a file).
        blocker = tmp_path / "blocker"
        blocker.write_text("I am a file, not a directory")
        config_path = blocker / "mcporter.json"
        result = setup_skill.write_openclaw_config("00e20142", config_path=config_path)
        assert result["passed"] is False
        assert result["fix"] is not None


# ---------------------------------------------------------------------------
# check_connectivity
# ---------------------------------------------------------------------------


class TestCheckConnectivity:
    def test_missing_serial_fails(self, monkeypatch):
        monkeypatch.delenv("VECTOR_SERIAL", raising=False)
        result = setup_skill.check_connectivity(serial=None)
        assert result["passed"] is False
        assert result["check"] == "connectivity"
        assert "VECTOR_SERIAL" in result["detail"]
        assert result["fix"] is not None

    def test_sdk_not_importable_fails(self, monkeypatch):
        monkeypatch.delitem(sys.modules, "anki_vector", raising=False)
        with patch.dict(sys.modules, {"anki_vector": None}):
            result = setup_skill.check_connectivity(serial="00e20142")
        assert result["passed"] is False
        assert "SDK" in result["detail"] or "anki_vector" in result["detail"]

    def test_successful_connection(self):
        mock_manager = MagicMock()
        mock_manager.connect.return_value = MagicMock()
        with patch("vectorclaw_mcp.setup_skill.RobotManager", return_value=mock_manager):
            result = setup_skill.check_connectivity(serial="00e20142")
        assert result["passed"] is True
        assert result["check"] == "connectivity"
        mock_manager.connect.assert_called_once()
        mock_manager.disconnect.assert_called_once()

    def test_connection_error_fails(self):
        mock_manager = MagicMock()
        mock_manager.connect.side_effect = ConnectionError("host unreachable")
        with patch("vectorclaw_mcp.setup_skill.RobotManager", return_value=mock_manager):
            result = setup_skill.check_connectivity(serial="00e20142", host="10.0.0.1")
        assert result["passed"] is False
        assert result["fix"] is not None
        assert "Wire-Pod" in result["fix"] or "SETUP" in result["fix"]

    def test_runtime_error_fails(self):
        mock_manager = MagicMock()
        mock_manager.connect.side_effect = RuntimeError("serial invalid")
        with patch("vectorclaw_mcp.setup_skill.RobotManager", return_value=mock_manager):
            result = setup_skill.check_connectivity(serial="bad-serial")
        assert result["passed"] is False
        assert "serial invalid" in result["detail"]

    def test_restores_env_on_success(self, monkeypatch):
        monkeypatch.setenv("VECTOR_SERIAL", "original-serial")
        monkeypatch.delenv("VECTOR_HOST", raising=False)

        mock_manager = MagicMock()
        mock_manager.connect.return_value = MagicMock()
        with patch("vectorclaw_mcp.setup_skill.RobotManager", return_value=mock_manager):
            setup_skill.check_connectivity(serial="temp-serial", host="10.0.0.2")

        import os

        assert os.environ.get("VECTOR_SERIAL") == "original-serial"
        assert "VECTOR_HOST" not in os.environ

    def test_restores_env_on_failure(self, monkeypatch):
        monkeypatch.setenv("VECTOR_SERIAL", "original-serial")
        monkeypatch.setenv("VECTOR_HOST", "original-host")

        mock_manager = MagicMock()
        mock_manager.connect.side_effect = ConnectionError("fail")
        with patch("vectorclaw_mcp.setup_skill.RobotManager", return_value=mock_manager):
            setup_skill.check_connectivity(serial="temp-serial", host="bad-host")

        import os

        assert os.environ.get("VECTOR_SERIAL") == "original-serial"
        assert os.environ.get("VECTOR_HOST") == "original-host"


# ---------------------------------------------------------------------------
# run_smoke_test
# ---------------------------------------------------------------------------


class TestRunSmokeTest:
    def test_all_steps_pass(self, mock_robot):
        mock_robot.get_battery_state.return_value.battery_level = 2
        result = setup_skill.run_smoke_test()
        assert result["check"] == "smoke_test"
        assert isinstance(result["steps"], list)
        assert len(result["steps"]) == 2

    def test_smoke_test_status_failure(self, monkeypatch, mock_robot):
        from vectorclaw_mcp import tools_perception

        monkeypatch.setattr(
            tools_perception,
            "vector_status",
            lambda: {"status": "error", "message": "robot disconnected"},
        )
        result = setup_skill.run_smoke_test()
        status_step = next(s for s in result["steps"] if s["step"] == "status")
        assert status_step["passed"] is False
        assert result["passed"] is False

    def test_smoke_test_head_exception(self, monkeypatch, mock_robot):
        from vectorclaw_mcp import tools_motion

        def _raise_head_jammed(_: float) -> None:
            raise RuntimeError("head jammed")

        monkeypatch.setattr(tools_motion, "vector_head", _raise_head_jammed)
        result = setup_skill.run_smoke_test()
        head_step = next(s for s in result["steps"] if s["step"] == "head_actuation")
        assert head_step["passed"] is False
        assert result["passed"] is False
        assert result["fix"] is not None


# ---------------------------------------------------------------------------
# run_setup (orchestration)
# ---------------------------------------------------------------------------


class TestRunSetup:
    def test_missing_serial_returns_fail(self, monkeypatch):
        monkeypatch.delenv("VECTOR_SERIAL", raising=False)
        report = setup_skill.run_setup(serial=None, write_config=False)
        assert report["status"] == "fail"
        assert "remediation" in report
        assert any(
            r["check"] == "config_validation" for r in report["checks"]
        )

    def test_serial_from_env_var(self, tmp_path, monkeypatch):
        monkeypatch.setenv("VECTOR_SERIAL", "env-serial")
        mock_manager = MagicMock()
        mock_manager.connect.return_value = MagicMock()
        with (
            patch("vectorclaw_mcp.setup_skill.RobotManager", return_value=mock_manager),
            patch(
                "vectorclaw_mcp.setup_skill.run_smoke_test",
                return_value={
                    "passed": True,
                    "check": "smoke_test",
                    "steps": [],
                    "detail": "passed",
                    "fix": None,
                },
            ),
        ):
            report = setup_skill.run_setup(
                serial=None,
                _config_path=tmp_path / "mcporter.json",
                install_sdk_if_missing=False,
            )
        assert report["status"] == "pass"

    def test_full_setup_passes(self, tmp_path, monkeypatch):
        monkeypatch.delenv("VECTOR_SERIAL", raising=False)
        mock_manager = MagicMock()
        mock_manager.connect.return_value = MagicMock()
        with (
            patch("vectorclaw_mcp.setup_skill.RobotManager", return_value=mock_manager),
            patch(
                "vectorclaw_mcp.setup_skill.run_smoke_test",
                return_value={
                    "passed": True,
                    "check": "smoke_test",
                    "steps": [],
                    "detail": "All smoke tests passed.",
                    "fix": None,
                },
            ),
        ):
            report = setup_skill.run_setup(
                serial="00e20142",
                host="192.168.1.100",
                write_config=True,
                install_sdk_if_missing=False,
                run_connectivity=True,
                run_smoke=True,
                _config_path=tmp_path / "mcporter.json",
            )
        assert report["status"] == "pass"
        assert "next_steps" in report
        assert "vectorclaw-mcp" in report["next_steps"]

    def test_connectivity_failure_stops_smoke(self, tmp_path, monkeypatch):
        monkeypatch.delenv("VECTOR_SERIAL", raising=False)
        mock_manager = MagicMock()
        mock_manager.connect.side_effect = ConnectionError("unreachable")
        with patch("vectorclaw_mcp.setup_skill.RobotManager", return_value=mock_manager):
            report = setup_skill.run_setup(
                serial="00e20142",
                write_config=True,
                install_sdk_if_missing=False,
                run_connectivity=True,
                run_smoke=True,
                _config_path=tmp_path / "mcporter.json",
            )
        assert report["status"] == "fail"
        assert "remediation" in report
        # smoke_test should not appear — we stopped after connectivity failure
        assert not any(r["check"] == "smoke_test" for r in report["checks"])

    def test_skips_connectivity_when_disabled(self, tmp_path, monkeypatch):
        monkeypatch.delenv("VECTOR_SERIAL", raising=False)
        with patch(
            "vectorclaw_mcp.setup_skill.run_smoke_test",
            return_value={
                "passed": True,
                "check": "smoke_test",
                "steps": [],
                "detail": "passed",
                "fix": None,
            },
        ):
            report = setup_skill.run_setup(
                serial="00e20142",
                write_config=True,
                install_sdk_if_missing=False,
                run_connectivity=False,
                run_smoke=True,
                _config_path=tmp_path / "mcporter.json",
            )
        assert not any(r["check"] == "connectivity" for r in report["checks"])

    def test_write_config_failure_stops_early(self, tmp_path, monkeypatch):
        monkeypatch.delenv("VECTOR_SERIAL", raising=False)
        # Force write_openclaw_config to fail by using an unwritable path
        blocker = tmp_path / "blocker"
        blocker.write_text("not a dir")
        bad_config_path = blocker / "mcporter.json"
        report = setup_skill.run_setup(
            serial="00e20142",
            write_config=True,
            install_sdk_if_missing=False,
            run_connectivity=False,
            run_smoke=False,
            _config_path=bad_config_path,
        )
        assert report["status"] == "fail"
        assert any(r["check"] == "write_config" for r in report["checks"])

    def test_sdk_install_attempted_when_missing(self, tmp_path, monkeypatch):
        monkeypatch.delenv("VECTOR_SERIAL", raising=False)
        # Simulate SDK missing then available after install
        validate_call_count = 0

        def fake_validate():
            nonlocal validate_call_count
            validate_call_count += 1
            if validate_call_count == 1:
                return {
                    "passed": False,
                    "check": "sdk_import",
                    "detail": "missing",
                    "fix": "install it",
                }
            return {
                "passed": True,
                "check": "sdk_import",
                "detail": "installed",
                "fix": None,
            }

        mock_install = MagicMock(
            return_value={
                "passed": True,
                "check": "sdk_install",
                "detail": "installed",
                "fix": None,
            }
        )
        with (
            patch("vectorclaw_mcp.setup_skill.validate_sdk", side_effect=fake_validate),
            patch("vectorclaw_mcp.setup_skill.install_sdk", mock_install),
        ):
            report = setup_skill.run_setup(
                serial="00e20142",
                write_config=True,
                install_sdk_if_missing=True,
                run_connectivity=False,
                run_smoke=False,
                _config_path=tmp_path / "mcporter.json",
            )
        mock_install.assert_called_once()
        # After install, sdk_import should be passed
        sdk_check = next(r for r in report["checks"] if r["check"] == "sdk_import")
        assert sdk_check["passed"] is True


# ---------------------------------------------------------------------------
# _build_report
# ---------------------------------------------------------------------------


class TestBuildReport:
    def test_all_passed_status(self):
        checks = [
            {"passed": True, "check": "a", "detail": "ok", "fix": None},
            {"passed": True, "check": "b", "detail": "ok", "fix": None},
        ]
        report = setup_skill._build_report(checks)
        assert report["status"] == "pass"
        assert "next_steps" in report
        assert "remediation" not in report

    def test_any_failed_status(self):
        checks = [
            {"passed": True, "check": "a", "detail": "ok", "fix": None},
            {"passed": False, "check": "b", "detail": "bad", "fix": "do this"},
        ]
        report = setup_skill._build_report(checks)
        assert report["status"] == "fail"
        assert "remediation" in report
        assert "b: do this" in report["remediation"]

    def test_summary_contains_check_names(self):
        checks = [
            {"passed": True, "check": "python_version", "detail": "ok", "fix": None},
        ]
        report = setup_skill._build_report(checks)
        assert "python_version" in report["summary"]

    def test_no_remediation_when_no_fixes(self):
        checks = [
            {"passed": False, "check": "a", "detail": "bad", "fix": None},
        ]
        report = setup_skill._build_report(checks)
        assert "remediation" not in report


# ---------------------------------------------------------------------------
# tool_registry integration
# ---------------------------------------------------------------------------


def test_vector_setup_in_tool_list():
    from vectorclaw_mcp.tool_registry import TOOLS

    names = [t.name for t in TOOLS]
    assert "vector_setup" in names


def test_vector_setup_dispatch(tmp_path, monkeypatch):
    """vector_setup dispatches correctly through build_dispatch."""
    monkeypatch.delenv("VECTOR_SERIAL", raising=False)
    from vectorclaw_mcp.tool_registry import build_dispatch

    dispatch = build_dispatch({})
    assert "vector_setup" in dispatch

    # Calling with no serial should return a fail report (not raise)
    with patch(
        "vectorclaw_mcp.setup_skill.write_openclaw_config",
        return_value={"passed": True, "check": "write_config", "detail": "", "fix": None},
    ):
        result = dispatch["vector_setup"]()
    assert result["status"] == "fail"
