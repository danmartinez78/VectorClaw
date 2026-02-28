from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest


def test_robot_manager_requires_serial(monkeypatch):
    monkeypatch.delenv("VECTOR_SERIAL", raising=False)
    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(RuntimeError, match="VECTOR_SERIAL"):
        mgr.connect()


def test_robot_manager_connect_enables_vision_modes(monkeypatch):
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "0")

    fake_robot = MagicMock()
    fake_sdk = MagicMock()
    fake_sdk.Robot.return_value = fake_robot
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    mgr.connect()

    fake_robot.vision.enable_face_detection.assert_called_once_with(estimate_expression=True)
    fake_robot.vision.enable_custom_object_detection.assert_called_once_with()


def test_robot_manager_connect_vision_failure_does_not_break_connection(monkeypatch):
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "0")

    fake_robot = MagicMock()
    fake_robot.vision.enable_face_detection.side_effect = RuntimeError("vision unavailable")
    fake_sdk = MagicMock()
    fake_sdk.Robot.return_value = fake_robot
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    robot = mgr.connect()

    assert mgr.is_connected
    assert robot is fake_robot


def test_robot_manager_disconnect_noop():
    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    mgr.disconnect()
    assert not mgr.is_connected


def test_robot_manager_connect_retries_on_transient_failure(monkeypatch):
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "2")
    monkeypatch.setenv("VECTOR_CONNECT_DELAY", "0")

    call_count = 0

    def fake_robot_factory(**kwargs):
        nonlocal call_count
        call_count += 1
        r = MagicMock()
        if call_count < 3:
            r.connect.side_effect = ConnectionError("transient")
        else:
            r.connect.return_value = None
        return r

    fake_sdk = MagicMock()
    fake_sdk.Robot.side_effect = fake_robot_factory
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    mgr.connect()
    assert mgr.is_connected
    assert call_count == 3


def test_robot_manager_connect_raises_after_all_retries(monkeypatch):
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "2")
    monkeypatch.setenv("VECTOR_CONNECT_DELAY", "0")

    fake_sdk = MagicMock()
    fake_sdk.Robot.return_value.connect.side_effect = ConnectionError("always fails")
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(ConnectionError, match="always fails"):
        mgr.connect()
    assert fake_sdk.Robot.call_count == 3


def test_robot_manager_connect_no_retry_for_missing_serial(monkeypatch):
    monkeypatch.delenv("VECTOR_SERIAL", raising=False)
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "3")

    fake_sdk = MagicMock()
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(RuntimeError, match="VECTOR_SERIAL"):
        mgr.connect()
    fake_sdk.Robot.assert_not_called()


def test_robot_manager_connect_runtime_error_not_retried(monkeypatch):
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "3")
    monkeypatch.setenv("VECTOR_CONNECT_DELAY", "0")

    fake_sdk = MagicMock()
    fake_sdk.Robot.return_value.connect.side_effect = RuntimeError("sdk config error")
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(RuntimeError, match="sdk config error"):
        mgr.connect()
    fake_sdk.Robot.assert_called_once()


def test_robot_manager_connect_invalid_retries(monkeypatch):
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "-1")

    fake_sdk = MagicMock()
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(RuntimeError, match="VECTOR_CONNECT_RETRIES"):
        mgr.connect()
    fake_sdk.Robot.assert_not_called()


def test_robot_manager_connect_invalid_delay(monkeypatch):
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "2")
    monkeypatch.setenv("VECTOR_CONNECT_DELAY", "-0.5")

    fake_sdk = MagicMock()
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(RuntimeError, match="VECTOR_CONNECT_DELAY"):
        mgr.connect()
    fake_sdk.Robot.assert_not_called()


def test_robot_manager_connect_cleanup_on_failure(monkeypatch):
    monkeypatch.setenv("VECTOR_SERIAL", "test-serial")
    monkeypatch.setenv("VECTOR_CONNECT_RETRIES", "1")
    monkeypatch.setenv("VECTOR_CONNECT_DELAY", "0")

    robots_created = []

    def fake_robot_factory(**kwargs):
        r = MagicMock()
        r.connect.side_effect = OSError("network unreachable")
        robots_created.append(r)
        return r

    fake_sdk = MagicMock()
    fake_sdk.Robot.side_effect = fake_robot_factory
    monkeypatch.setitem(sys.modules, "anki_vector", fake_sdk)

    from vectorclaw_mcp.robot import RobotManager

    mgr = RobotManager()
    with pytest.raises(OSError):
        mgr.connect()
    for r in robots_created:
        r.disconnect.assert_called_once()
