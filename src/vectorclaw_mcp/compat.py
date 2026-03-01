"""Runtime compatibility guardrails for VectorClaw.

Validates that the wirepod_vector_sdk is installed and Python version is supported.
"""

from __future__ import annotations

import sys
import warnings
from importlib.util import find_spec

from packaging.version import InvalidVersion, Version

_MINIMUM_PYTHON = (3, 11)
_MINIMUM_SDK = Version("0.8.0")

_COMPAT_MSG = (
    "VectorClaw requires wirepod_vector_sdk. "
    "Install with: pip install wirepod_vector_sdk"
)


def _get_distribution_for_module(module_name: str) -> str | None:
    """Get the distribution name that provides the given module.

    Returns 'wirepod_vector_sdk' or 'anki_vector' or None.
    If both distributions are present, prefers wirepod_vector_sdk.
    """
    try:
        # Python 3.8+
        from importlib.metadata import packages_distributions
        dists = packages_distributions()
        dist_names = dists.get(module_name) or []
        # Prefer wirepod_vector_sdk over legacy anki_vector if both are present.
        for preferred in ("wirepod_vector_sdk", "anki_vector"):
            if preferred in dist_names:
                return preferred
        return None
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


def _get_sdk_version() -> str | None:
    """Get the installed SDK version.

    Returns None if the module is not available.
    Raises SystemExit if import fails with a non-ImportError exception
    (e.g., dependency/protobuf issues).
    """
    try:
        import anki_vector  # noqa: PLC0415
        return getattr(anki_vector, "__version__", None)
    except ImportError:
        # Module genuinely not available; let the caller handle via _sdk_available()
        return None
    except Exception as exc:
        # Other import-time failures (e.g., dependency/protobuf issues) should surface as
        # a clear startup error rather than a long traceback.
        raise SystemExit(
            "Error while importing the 'anki_vector' SDK module.\n"
            f"  Underlying error: {exc}\n"
            f"  {_COMPAT_MSG}\n"
            "  If the SDK is already installed, try upgrading it:\n"
            "    pip install --upgrade wirepod_vector_sdk"
        ) from exc


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

    # Verify SDK version >= 0.8.0 using robust version comparison
    version = _get_sdk_version()
    if version is None:
        # No __version__ attribute - fail closed
        raise SystemExit(
            "VectorClaw requires wirepod_vector_sdk >= 0.8.0.\n"
            "  Could not determine SDK version (no __version__ attribute).\n"
            "  Upgrade with: pip install wirepod_vector_sdk --upgrade"
        )

    try:
        parsed_version = Version(version)
        if parsed_version < _MINIMUM_SDK:
            raise SystemExit(
                f"VectorClaw requires wirepod_vector_sdk >= {_MINIMUM_SDK}.\n"
                f"  Detected: {version}\n"
                "  Upgrade with: pip install wirepod_vector_sdk --upgrade"
            )
    except InvalidVersion:
        # Unknown version format - fail closed
        raise SystemExit(
            f"VectorClaw requires wirepod_vector_sdk >= {_MINIMUM_SDK}.\n"
            f"  Could not parse SDK version: {version}\n"
            "  Upgrade with: pip install wirepod_vector_sdk --upgrade"
        )

    # Python 3.12+ warning (not officially tested yet)
    if py >= (3, 12):
        warnings.warn(
            f"Python {py_str} with wirepod_vector_sdk is not officially tested. "
            f"Consider using Python {_MINIMUM_PYTHON[0]}.{_MINIMUM_PYTHON[1]} for best compatibility.",
            RuntimeWarning,
            stacklevel=2,
        )
