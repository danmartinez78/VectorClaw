"""OpenClaw setup skill for VectorClaw.

Provides a single guided-setup MCP tool (``vector_setup``) that walks a new
user through every step needed to go from "fresh install" to a working
VectorClaw configuration:

1. Auto-configuration  – validates required fields and writes the OpenClaw
   ``mcporter.json`` so the server starts automatically next session.
2. SDK / runtime check – verifies Python compatibility and that
   ``wirepod_vector_sdk`` (or a compatible legacy SDK) is installed.
3. Connectivity check  – performs a lightweight ``get_battery_state`` call to
   confirm the robot is reachable.
4. Post-install smoke test – runs ``vector_status`` and a safe ``set_head_angle``
   actuation, then returns a plain-language pass/fail summary.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_MINIMUM_PYTHON = (3, 10)
_RECOMMENDED_PYTHON = (3, 11)

# Default OpenClaw mcporter config path (can be overridden for tests).
_DEFAULT_MCPORTER_PATH = Path.home() / ".openclaw" / "workspace" / "config" / "mcporter.json"


def _check_python() -> dict:
    """Return a result dict describing Python compatibility."""
    py = sys.version_info[:2]
    py_str = ".".join(str(v) for v in py)
    if py < _MINIMUM_PYTHON:
        return {
            "passed": False,
            "detail": (
                f"Python {py_str} is below the minimum supported version "
                f"{_MINIMUM_PYTHON[0]}.{_MINIMUM_PYTHON[1]}. "
                f"Fix: install Python {_RECOMMENDED_PYTHON[0]}.{_RECOMMENDED_PYTHON[1]} "
                "and recreate your virtual environment."
            ),
        }
    if py >= (3, 12):
        return {
            "passed": True,
            "detail": (
                f"Python {py_str} detected. This version is not officially tested "
                "with wirepod_vector_sdk; consider Python 3.11 if you hit issues."
            ),
        }
    return {"passed": True, "detail": f"Python {py_str} — OK."}


def _check_sdk() -> dict:
    """Verify that a compatible Vector SDK is importable."""
    if importlib.util.find_spec("wirepod_vector_sdk") is not None:
        return {"passed": True, "detail": "wirepod_vector_sdk is installed — OK."}
    if importlib.util.find_spec("anki_vector") is not None:
        py = sys.version_info[:2]
        if py >= (3, 10):
            return {
                "passed": False,
                "detail": (
                    "Legacy anki_vector SDK detected on Python "
                    f"{py[0]}.{py[1]}. "
                    "This combination has known asyncio / protobuf incompatibilities. "
                    "Fix: pip install wirepod_vector_sdk"
                ),
            }
        return {
            "passed": True,
            "detail": (
                "Legacy anki_vector SDK detected. "
                "Upgrade to wirepod_vector_sdk for long-term reliability: "
                "pip install wirepod_vector_sdk"
            ),
        }
    return {
        "passed": False,
        "detail": (
            "No Vector SDK found. "
            "Fix: pip install wirepod_vector_sdk"
        ),
    }


def _check_import() -> dict:
    """Try importing the anki_vector namespace (provided by either SDK)."""
    try:
        import anki_vector  # noqa: F401  # installed by wirepod_vector_sdk or legacy package
        return {"passed": True, "detail": "import anki_vector — OK."}
    except ImportError as exc:
        return {
            "passed": False,
            "detail": (
                f"import anki_vector failed: {exc}. "
                "Fix: pip install wirepod_vector_sdk"
            ),
        }


def _write_openclaw_config(
    serial: str,
    host: Optional[str],
    *,
    config_path: Path = _DEFAULT_MCPORTER_PATH,
) -> dict:
    """Write (or update) the OpenClaw mcporter.json with VectorClaw credentials."""
    env_block: dict = {"VECTOR_SERIAL": serial}
    if host:
        env_block["VECTOR_HOST"] = host

    server_entry = {
        "command": "uvx",
        "args": ["vectorclaw-mcp"],
        "env": env_block,
    }

    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Merge into existing config when present.
        if config_path.exists():
            with config_path.open() as fh:
                existing: dict = json.load(fh)
        else:
            existing = {}

        existing.setdefault("mcpServers", {})
        existing["mcpServers"]["vectorclaw"] = server_entry

        with config_path.open("w") as fh:
            json.dump(existing, fh, indent=2)

        return {
            "passed": True,
            "detail": f"OpenClaw config written to {config_path}.",
        }
    except OSError as exc:
        return {
            "passed": False,
            "detail": (
                f"Could not write OpenClaw config to {config_path}: {exc}. "
                "Fix: ensure the parent directory is writable, or set it manually — "
                "see docs/SETUP.md § Configure mcporter (OpenClaw)."
            ),
        }


def _check_connectivity(serial: str, host: Optional[str]) -> dict:
    """Attempt a lightweight robot connection and battery-state read."""
    try:
        import anki_vector  # noqa: PLC0415
    except ImportError:
        return {
            "passed": False,
            "detail": (
                "Cannot import anki_vector — SDK is not installed. "
                "Fix: pip install wirepod_vector_sdk"
            ),
        }

    kwargs: dict = {"serial": serial}
    if host:
        kwargs["ip"] = host

    robot = anki_vector.Robot(**kwargs)
    try:
        robot.connect()
    except (ConnectionError, TimeoutError, OSError) as exc:
        return {
            "passed": False,
            "detail": (
                f"Could not connect to robot (serial={serial!r}"
                + (f", host={host!r}" if host else "")
                + f"): {exc}. "
                "Fix: ensure Vector is powered on, on the same WiFi network, and "
                "Wire-Pod is running (sudo systemctl start wire-pod)."
            ),
        }
    except RuntimeError as exc:
        return {
            "passed": False,
            "detail": (
                f"SDK configuration error: {exc}. "
                "Fix: run 'python -m anki_vector.configure' to regenerate the SDK config."
            ),
        }

    try:
        robot.get_battery_state()
        result = {"passed": True, "detail": "Robot connection — OK."}
    except Exception as exc:
        result = {
            "passed": False,
            "detail": (
                f"Connected to robot but get_battery_state() failed: {exc}. "
                "Try waking Vector (tap backpack button) and running setup again."
            ),
        }
    finally:
        try:
            robot.disconnect()
        except Exception:
            pass

    return result


def _smoke_test(serial: str, host: Optional[str]) -> dict:
    """Run a status read and a safe head-angle set as a post-install smoke test."""
    try:
        import anki_vector  # noqa: PLC0415
        import anki_vector.util as util  # noqa: PLC0415
    except ImportError:
        return {
            "passed": False,
            "detail": (
                "Cannot import anki_vector for smoke test. "
                "Fix: pip install wirepod_vector_sdk"
            ),
        }

    kwargs: dict = {"serial": serial}
    if host:
        kwargs["ip"] = host

    robot = anki_vector.Robot(**kwargs)
    try:
        robot.connect()
    except Exception as exc:
        return {
            "passed": False,
            "detail": f"Smoke test skipped — could not connect: {exc}.",
        }

    steps: list[dict] = []
    try:
        robot.get_battery_state()
        steps.append({"check": "battery_state", "passed": True})
    except Exception as exc:
        steps.append({"check": "battery_state", "passed": False, "error": str(exc)})

    try:
        robot.behavior.set_head_angle(util.degrees(0))
        steps.append({"check": "set_head_angle(0)", "passed": True})
    except Exception as exc:
        steps.append({"check": "set_head_angle(0)", "passed": False, "error": str(exc)})

    try:
        robot.disconnect()
    except Exception:
        pass

    all_passed = all(s["passed"] for s in steps)
    failed = [s for s in steps if not s["passed"]]
    detail = (
        "All smoke checks passed."
        if all_passed
        else "Smoke check failures: " + "; ".join(f"{s['check']}: {s.get('error', 'failed')}" for s in failed)
    )
    return {"passed": all_passed, "detail": detail, "steps": steps}


# ---------------------------------------------------------------------------
# Public MCP tool
# ---------------------------------------------------------------------------


def vector_setup(
    serial: str,
    host: Optional[str] = None,
    *,
    _config_path: Optional[Path] = None,
) -> dict:
    """Guided VectorClaw setup skill.

    Walks through auto-configuration, SDK validation, connectivity checking,
    and a post-install smoke test.  Returns a plain-language pass/fail summary
    with actionable remediation steps for each failure.

    Args:
        serial: Robot serial number (required). Found on the sticker under Vector
                or in the Wire-Pod "Bot Settings" page.
        host:   Robot IP address (optional). If omitted the SDK will attempt
                auto-discovery via mDNS.

    Returns:
        A dict with:
        - ``status``:  ``"ok"`` if every stage passed, ``"error"`` otherwise.
        - ``stages``:  Per-stage results (name, passed, detail).
        - ``summary``: Plain-language success or failure description.
        - ``next_steps``: What to do after a successful setup.
    """
    if not serial or not serial.strip():
        return {
            "status": "error",
            "summary": (
                "VECTOR_SERIAL is required but was not provided. "
                "Find it on the sticker under your Vector robot "
                "or in the Wire-Pod 'Bot Settings' page."
            ),
            "stages": [],
        }

    serial = serial.strip()
    host = host.strip() if host else None
    host = host or None  # treat whitespace-only host as "not provided"
    config_path: Path = _config_path or _DEFAULT_MCPORTER_PATH

    stages: list[dict] = []

    # ── Stage 1: Python compatibility ────────────────────────────────────────
    py_result = _check_python()
    stages.append({"stage": "python_compatibility", **py_result})

    # ── Stage 2: SDK availability ─────────────────────────────────────────────
    sdk_result = _check_sdk()
    stages.append({"stage": "sdk_availability", **sdk_result})

    # ── Stage 3: anki_vector import ───────────────────────────────────────────
    import_result = _check_import()
    stages.append({"stage": "sdk_import", **import_result})

    # ── Stage 4: OpenClaw config ──────────────────────────────────────────────
    config_result = _write_openclaw_config(serial, host, config_path=config_path)
    stages.append({"stage": "openclaw_config", **config_result})

    # ── Stage 5: Robot connectivity ───────────────────────────────────────────
    conn_result = _check_connectivity(serial, host)
    stages.append({"stage": "robot_connectivity", **conn_result})

    # ── Stage 6: Post-install smoke test ──────────────────────────────────────
    # Only run smoke test when earlier critical stages passed.
    critical_passed = import_result["passed"] and conn_result["passed"]
    if critical_passed:
        smoke_result = _smoke_test(serial, host)
    else:
        smoke_result = {
            "passed": False,
            "detail": "Skipped — earlier stages must pass first.",
        }
    stages.append({"stage": "smoke_test", **smoke_result})

    # ── Final summary ─────────────────────────────────────────────────────────
    failed_stages = [s for s in stages if not s["passed"]]
    all_passed = len(failed_stages) == 0

    if all_passed:
        summary = (
            f"✅ VectorClaw setup complete!  Serial={serial!r}"
            + (f", Host={host!r}" if host else "")
            + ". All checks passed."
        )
        next_steps = [
            "Restart the OpenClaw gateway to pick up the new mcporter.json config.",
            "Ask your assistant: 'What is Vector's battery level?' to verify end-to-end.",
            "Explore available tools with 'What can Vector do?'",
        ]
    else:
        failed_names = ", ".join(s["stage"] for s in failed_stages)
        summary = f"❌ VectorClaw setup encountered failures in: {failed_names}. See stages for details."
        next_steps = [s["detail"] for s in failed_stages]

    return {
        "status": "ok" if all_passed else "error",
        "summary": summary,
        "stages": stages,
        "next_steps": next_steps,
    }
