"""OpenClaw setup skill for VectorClaw MCP.

Provides guided installation, configuration, and validation for new users.
Can be invoked as an MCP tool (``vector_setup``) or run directly as an
interactive CLI wizard via the ``vectorclaw-setup`` console script.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from .robot import RobotManager

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OPENCLAW_CONFIG_PATH: Path = (
    Path.home() / ".openclaw" / "workspace" / "config" / "mcporter.json"
)

WIREPOD_SDK_PYPI_NAME = "wirepod_vector_sdk"
WIREPOD_SDK_FIX_CMD = (
    "pip install git+https://github.com/kercre123/wirepod-vector-python-sdk.git"
    "@065fc197d592d76a164d64dcf0a768183ab37855"
)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def validate_python_version() -> dict[str, Any]:
    """Return a check result for the current Python version."""
    py = sys.version_info[:2]
    version_str = f"{py[0]}.{py[1]}"

    if py < (3, 10):
        return {
            "passed": False,
            "check": "python_version",
            "detail": (
                f"Python {version_str} is below the minimum required version (3.10)."
            ),
            "fix": (
                "Install Python 3.11 or newer: https://python.org/downloads"
            ),
        }
    if py < (3, 11):
        return {
            "passed": True,
            "check": "python_version",
            "detail": (
                f"Python {version_str} meets minimum requirements (3.10+), "
                "but Python 3.11+ is strongly recommended."
            ),
            "fix": (
                "Consider upgrading to Python 3.11 for best SDK compatibility."
            ),
        }
    return {
        "passed": True,
        "check": "python_version",
        "detail": f"Python {version_str} is fully compatible.",
        "fix": None,
    }


def validate_sdk() -> dict[str, Any]:
    """Return a check result confirming the Vector SDK can be imported."""
    try:
        import anki_vector  # noqa: PLC0415

        version = getattr(anki_vector, "__version__", "unknown")
        return {
            "passed": True,
            "check": "sdk_import",
            "detail": f"anki_vector SDK imported successfully (version: {version}).",
            "fix": None,
        }
    except ImportError as exc:
        return {
            "passed": False,
            "check": "sdk_import",
            "detail": f"Failed to import anki_vector: {exc}",
            "fix": f"Install the SDK:\n  {WIREPOD_SDK_FIX_CMD}",
        }


def install_sdk() -> dict[str, Any]:
    """Install ``wirepod_vector_sdk`` via pip and return a check result."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", WIREPOD_SDK_PYPI_NAME],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return {
                "passed": True,
                "check": "sdk_install",
                "detail": "wirepod_vector_sdk installed successfully.",
                "fix": None,
            }
        return {
            "passed": False,
            "check": "sdk_install",
            "detail": f"SDK installation failed: {result.stderr.strip()}",
            "fix": f"Install manually:\n  {WIREPOD_SDK_FIX_CMD}",
        }
    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "check": "sdk_install",
            "detail": "SDK installation timed out after 120 seconds.",
            "fix": f"Install manually:\n  {WIREPOD_SDK_FIX_CMD}",
        }
    except Exception as exc:
        return {
            "passed": False,
            "check": "sdk_install",
            "detail": f"SDK installation error: {exc}",
            "fix": f"Install manually:\n  {WIREPOD_SDK_FIX_CMD}",
        }


def write_openclaw_config(
    serial: str,
    host: str | None = None,
    *,
    config_path: Path | None = None,
) -> dict[str, Any]:
    """Write VECTOR_SERIAL (and optional VECTOR_HOST) to the OpenClaw config.

    Merges into any existing ``mcporter.json`` without destroying unrelated keys.
    Pass *config_path* to override the default location (useful in tests).
    """
    target = config_path if config_path is not None else OPENCLAW_CONFIG_PATH
    try:
        target.parent.mkdir(parents=True, exist_ok=True)

        existing: dict = {}
        if target.exists():
            try:
                existing = json.loads(target.read_text())
            except json.JSONDecodeError:
                pass  # Start fresh if the file is corrupt

        env: dict = existing.get("env", {})
        env["VECTOR_SERIAL"] = serial
        if host:
            env["VECTOR_HOST"] = host
        elif "VECTOR_HOST" in env:
            del env["VECTOR_HOST"]
        existing["env"] = env

        target.write_text(json.dumps(existing, indent=2))
        return {
            "passed": True,
            "check": "write_config",
            "detail": f"Configuration written to {target}",
            "fix": None,
        }
    except OSError as exc:
        return {
            "passed": False,
            "check": "write_config",
            "detail": f"Failed to write config to {target}: {exc}",
            "fix": (
                f"Ensure you have write access to {target.parent}, or set "
                "VECTOR_SERIAL (and optionally VECTOR_HOST) as environment variables."
            ),
        }


def check_connectivity(
    serial: str | None = None,
    host: str | None = None,
) -> dict[str, Any]:
    """Validate robot connectivity with a lightweight status call.

    Uses *serial* and *host* when provided; falls back to the ``VECTOR_SERIAL``
    and ``VECTOR_HOST`` environment variables otherwise.
    """
    effective_serial = serial or os.environ.get("VECTOR_SERIAL")
    effective_host = host or os.environ.get("VECTOR_HOST")

    if not effective_serial:
        return {
            "passed": False,
            "check": "connectivity",
            "detail": "VECTOR_SERIAL is not set. Cannot check connectivity.",
            "fix": (
                "Provide your robot's serial number. "
                "Find it in the Vector app under Settings → My Vector → Serial Number, "
                "or on the label under the robot."
            ),
        }

    try:
        import anki_vector  # noqa: PLC0415, F401
    except ImportError:
        return {
            "passed": False,
            "check": "connectivity",
            "detail": "anki_vector SDK is not importable. Cannot check connectivity.",
            "fix": f"Install the SDK first:\n  {WIREPOD_SDK_FIX_CMD}",
        }

    # Temporarily override environment for the isolated connection attempt.
    original_serial = os.environ.get("VECTOR_SERIAL")
    original_host = os.environ.get("VECTOR_HOST")
    try:
        os.environ["VECTOR_SERIAL"] = effective_serial
        if effective_host:
            os.environ["VECTOR_HOST"] = effective_host
        elif "VECTOR_HOST" in os.environ:
            del os.environ["VECTOR_HOST"]

        temp_manager = RobotManager()
        temp_manager.connect()
        temp_manager.disconnect()

        return {
            "passed": True,
            "check": "connectivity",
            "detail": f"Successfully connected to robot {effective_serial}.",
            "fix": None,
        }
    except RuntimeError as exc:
        return {
            "passed": False,
            "check": "connectivity",
            "detail": str(exc),
            "fix": (
                "Check that VECTOR_SERIAL matches your robot's serial number. "
                "Find it in the Vector app under Settings → My Vector → Serial Number."
            ),
        }
    except (ConnectionError, TimeoutError, OSError) as exc:
        host_hint = f" at {effective_host}" if effective_host else ""
        return {
            "passed": False,
            "check": "connectivity",
            "detail": f"Could not reach robot{host_hint}: {exc}",
            "fix": (
                "Ensure Wire-Pod is running and the robot is on the same network. "
                "If using VECTOR_HOST, verify the IP address is reachable. "
                "See docs/SETUP.md for full troubleshooting steps."
            ),
        }
    finally:
        # Restore the original environment exactly.
        if original_serial is not None:
            os.environ["VECTOR_SERIAL"] = original_serial
        elif "VECTOR_SERIAL" in os.environ:
            del os.environ["VECTOR_SERIAL"]
        if original_host is not None:
            os.environ["VECTOR_HOST"] = original_host
        elif "VECTOR_HOST" in os.environ:
            del os.environ["VECTOR_HOST"]


def run_smoke_test() -> dict[str, Any]:
    """Execute a status read and a harmless head-move as a smoke test."""
    steps: list[dict] = []

    # 1. Status check
    try:
        from .tools_perception import vector_status  # noqa: PLC0415

        status = vector_status()
        steps.append(
            {
                "step": "status",
                "passed": status.get("status") != "error",
                "detail": status.get("message", "Status retrieved successfully."),
            }
        )
    except Exception as exc:
        steps.append(
            {
                "step": "status",
                "passed": False,
                "detail": f"Status check failed: {exc}",
            }
        )

    # 2. Head actuation (harmless: return to neutral position)
    try:
        from .tools_motion import vector_head  # noqa: PLC0415

        result = vector_head(0.0)
        steps.append(
            {
                "step": "head_actuation",
                "passed": result.get("status") != "error",
                "detail": result.get("message", "Head moved to neutral position."),
            }
        )
    except Exception as exc:
        steps.append(
            {
                "step": "head_actuation",
                "passed": False,
                "detail": f"Head actuation failed: {exc}",
            }
        )

    all_passed = all(s["passed"] for s in steps)
    return {
        "passed": all_passed,
        "check": "smoke_test",
        "steps": steps,
        "detail": "All smoke tests passed." if all_passed else "Some smoke tests failed.",
        "fix": (
            None
            if all_passed
            else "Check connectivity and SDK setup before running smoke tests."
        ),
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run_setup(
    serial: str | None = None,
    host: str | None = None,
    write_config: bool = True,
    install_sdk_if_missing: bool = True,
    run_connectivity: bool = True,
    run_smoke: bool = True,
    *,
    _config_path: Path | None = None,
) -> dict[str, Any]:
    """Run the full setup flow and return a structured pass/fail report.

    Parameters
    ----------
    serial:
        Robot serial number.  Falls back to the ``VECTOR_SERIAL`` env var.
    host:
        Optional robot IP address.  Falls back to the ``VECTOR_HOST`` env var.
    write_config:
        Write resolved values to the OpenClaw ``mcporter.json`` config file.
    install_sdk_if_missing:
        Attempt to install ``wirepod_vector_sdk`` when the SDK is absent.
    run_connectivity:
        Attempt a live connectivity check against the robot.
    run_smoke:
        Run a status read and harmless actuation as a final smoke test.
    _config_path:
        Override the default OpenClaw config path (for tests).
    """
    results: list[dict] = []

    # Step 1: Python version
    py_result = validate_python_version()
    results.append(py_result)
    if not py_result["passed"]:
        return _build_report(results)

    # Step 2: Validate required config fields
    effective_serial = serial or os.environ.get("VECTOR_SERIAL")
    if not effective_serial:
        results.append(
            {
                "passed": False,
                "check": "config_validation",
                "detail": "VECTOR_SERIAL is required but was not provided.",
                "fix": (
                    "Provide your robot's serial number as the 'serial' argument or "
                    "set the VECTOR_SERIAL environment variable. "
                    "Find it in the Vector app under Settings → My Vector → Serial Number."
                ),
            }
        )
        return _build_report(results)

    # Step 3: Write OpenClaw config
    if write_config:
        config_result = write_openclaw_config(
            effective_serial, host, config_path=_config_path
        )
        results.append(config_result)
        if not config_result["passed"]:
            return _build_report(results)

    # Step 4: SDK validation (with optional auto-install)
    sdk_result = validate_sdk()
    if not sdk_result["passed"] and install_sdk_if_missing:
        install_result = install_sdk()
        results.append(install_result)
        if install_result["passed"]:
            sdk_result = validate_sdk()
    results.append(sdk_result)
    if not sdk_result["passed"]:
        return _build_report(results)

    # Step 5: Connectivity check
    if run_connectivity:
        conn_result = check_connectivity(effective_serial, host)
        results.append(conn_result)
        if not conn_result["passed"]:
            return _build_report(results)

    # Step 6: Smoke test
    if run_smoke:
        smoke_result = run_smoke_test()
        results.append(smoke_result)

    return _build_report(results)


def _build_report(results: list[dict]) -> dict[str, Any]:
    """Build the final structured PASS/FAIL report from individual check results."""
    all_passed = all(r["passed"] for r in results)
    failed = [r for r in results if not r["passed"]]

    summary_lines: list[str] = []
    for r in results:
        icon = "✅" if r["passed"] else "❌"
        summary_lines.append(f"  {icon} {r['check']}: {r['detail']}")

    report: dict[str, Any] = {
        "status": "pass" if all_passed else "fail",
        "summary": "\n".join(summary_lines),
        "checks": results,
    }

    if failed:
        remediation_lines: list[str] = []
        for r in failed:
            if r.get("fix"):
                remediation_lines.append(f"• {r['check']}: {r['fix']}")
        if remediation_lines:
            report["remediation"] = "\n".join(remediation_lines)

    if all_passed:
        report["next_steps"] = (
            "VectorClaw is configured and ready to use!\n"
            "Start the MCP server with: vectorclaw-mcp\n"
            "Or restart OpenClaw — it will pick up the updated config automatically."
        )

    return report


# ---------------------------------------------------------------------------
# Interactive CLI wizard
# ---------------------------------------------------------------------------


def main() -> None:  # pragma: no cover
    """Interactive setup wizard for VectorClaw (``vectorclaw-setup`` script)."""
    print("=" * 60)
    print("  VectorClaw MCP — Setup Wizard")
    print("=" * 60)
    print()

    # --- Prompt for serial (required) ---
    default_serial = os.environ.get("VECTOR_SERIAL", "")
    while True:
        prompt = (
            f"Robot serial number [{default_serial}]: "
            if default_serial
            else "Robot serial number (required): "
        )
        serial = input(prompt).strip() or default_serial
        if serial:
            break
        print(
            "  ⚠  VECTOR_SERIAL is required.\n"
            "     Find it in the Vector app under Settings → My Vector → Serial Number,\n"
            "     or on the label under the robot."
        )

    # --- Prompt for host (optional) ---
    default_host = os.environ.get("VECTOR_HOST", "")
    host_prompt = (
        f"Robot IP address (optional) [{default_host}]: "
        if default_host
        else "Robot IP address (optional, press Enter to skip): "
    )
    host_input = input(host_prompt).strip()
    host: str | None = host_input or default_host or None

    print()
    print(f"  Serial : {serial}")
    print(f"  Host   : {host or '(auto-discover via Wire-Pod)'}")
    print()

    # --- Run the full setup flow ---
    report = run_setup(
        serial=serial,
        host=host,
        write_config=True,
        install_sdk_if_missing=True,
        run_connectivity=True,
        run_smoke=True,
    )

    print(report["summary"])
    print()

    if report["status"] == "pass":
        print("=" * 60)
        print("  ✅  SETUP PASSED")
        print("=" * 60)
        if "next_steps" in report:
            print()
            print(report["next_steps"])
    else:
        print("=" * 60)
        print("  ❌  SETUP FAILED")
        print("=" * 60)
        if "remediation" in report:
            print()
            print("Remediation steps:")
            print(report["remediation"])

    print()
    sys.exit(0 if report["status"] == "pass" else 1)
