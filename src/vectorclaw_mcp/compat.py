"""Runtime compatibility guardrails for VectorClaw.

Validates that the wirepod_vector_sdk is installed and Python version is supported.
"""

from __future__ import annotations

import sys
import warnings
from importlib.util import find_spec

_MINIMUM_PYTHON = (3, 10)
_RECOMMENDED_PYTHON = (3, 11)

_COMPAT_MSG = (
    "VectorClaw requires wirepod_vector_sdk. "
    "Install with: pip install wirepod_vector_sdk"
)


def _get_distribution_for_module(module_name: str) -> str | None:
    """Get the distribution name that provides the given module.

    Returns 'wirepod_vector_sdk' or 'anki_vector' or None.
    """
    try:
        # Python 3.8+
        from importlib.metadata import packages_distributions
        dists = packages_distributions()
        return dists.get(module_name, [None])[0]
    except (ImportError, AttributeError):
        # Fallback: try importlib.metadata.version on known candidates
        try:
            from importlib import metadata
            for dist_name in ("wirepod_vector_sdk", "anki_vector"):
                try:
                    metadata.version(dist_name)
                    return dist_name
                except metadata.PackageNotFoundError:
                    continue
        except Exception:
            pass
    return None


def _sdk_available() -> bool:
    """Check if wirepod_vector_sdk is installed.

    Note: wirepod_vector_sdk installs under the 'anki_vector' namespace,
    but the legacy anki_vector package also provides this module.
    We verify the distribution name to ensure it's wirepod.
    """
    if find_spec("anki_vector") is None:
        return False

    # Verify it's actually wirepod_vector_sdk, not legacy anki_vector
    dist = _get_distribution_for_module("anki_vector")
    return dist == "wirepod_vector_sdk"


def _get_sdk_version() -> str | None:
    """Get the installed SDK version."""
    try:
        import anki_vector  # noqa: PLC0415
        return getattr(anki_vector, "__version__", None)
    except ImportError:
        return None


def check_runtime_compatibility() -> None:
    """Check Python version and SDK availability.

    This function should be called once at process startup (from
    :func:`vectorclaw_mcp.server.main`).

    Raises:
        SystemExit: If SDK is not available or Python version is too old.
    """
    py = sys.version_info[:2]
    py_str = sys.version.split()[0]

    # Python below minimum declared requirement
    if py < _MINIMUM_PYTHON:
        raise SystemExit(
            f"VectorClaw requires Python {_MINIMUM_PYTHON[0]}.{_MINIMUM_PYTHON[1]}+.\n"
            f"  Detected: Python {py_str}"
        )

    # Check if anki_vector module exists
    if find_spec("anki_vector") is None:
        raise SystemExit(
            f"{_COMPAT_MSG}\n"
            "  No Vector SDK found.\n"
            "  The wirepod_vector_sdk package provides the 'anki_vector' module."
        )

    # Verify it's wirepod_vector_sdk distribution, not legacy anki_vector
    dist = _get_distribution_for_module("anki_vector")
    if dist != "wirepod_vector_sdk":
        raise SystemExit(
            f"VectorClaw requires wirepod_vector_sdk, not the legacy anki_vector package.\n"
            f"  Detected distribution: {dist or 'unknown'}\n"
            "  Uninstall legacy: pip uninstall anki_vector\n"
            "  Install wirepod:  pip install wirepod_vector_sdk"
        )

    # Verify SDK version >= 0.8.0
    version = _get_sdk_version()
    if version and version.startswith("0."):
        try:
            parts = version.split(".")
            minor = int(parts[1]) if len(parts) > 1 else 0
            if minor < 8:
                raise SystemExit(
                    f"VectorClaw requires wirepod_vector_sdk >= 0.8.0.\n"
                    f"  Detected: {version}\n"
                    "  Upgrade with: pip install wirepod_vector_sdk --upgrade"
                )
        except (ValueError, IndexError):
            pass  # Unknown version format, assume OK

    # Python 3.12+ warning (not officially tested yet)
    if py >= (3, 12):
        warnings.warn(
            f"Python {py_str} with wirepod_vector_sdk is not officially tested. "
            "Consider using Python 3.11 for best compatibility.",
            RuntimeWarning,
            stacklevel=2,
        )
