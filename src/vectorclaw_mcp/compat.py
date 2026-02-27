"""Runtime compatibility guardrails for VectorClaw.

Detects known-incompatible Python/SDK combinations and raises a clear,
actionable error message at startup instead of a cryptic failure later
(e.g. protobuf API errors or asyncio ``loop=`` argument removal on 3.10+).
"""

from __future__ import annotations

import sys
import warnings
from importlib.util import find_spec

_MINIMUM_PYTHON = (3, 10)
_RECOMMENDED_PYTHON = (3, 11)

_COMPAT_MSG = (
    "VectorClaw detected an incompatible Vector SDK/runtime combination. "
    "Use Python 3.11 + wirepod_vector_sdk (recommended)."
)


def _wirepod_sdk_available() -> bool:
    return find_spec("wirepod_vector_sdk") is not None


def _legacy_sdk_available() -> bool:
    return find_spec("anki_vector") is not None


def check_runtime_compatibility() -> None:
    """Check Python version and SDK availability for known-incompatible combos.

    This function should be called once at process startup (from
    :func:`vectorclaw_mcp.server.main`).

    Raises:
        SystemExit: If a known-incompatible Python/SDK combination is detected,
            with an actionable message telling the user how to fix it.
    """
    py = sys.version_info[:2]
    py_str = sys.version.split()[0]

    # Python below minimum declared requirement
    if py < _MINIMUM_PYTHON:
        raise SystemExit(
            f"{_COMPAT_MSG}\n"
            f"  Detected:    Python {py_str}\n"
            f"  Supported:   Python {_RECOMMENDED_PYTHON[0]}.{_RECOMMENDED_PYTHON[1]}+"
            f" with wirepod_vector_sdk"
        )

    if _wirepod_sdk_available():
        # wirepod_vector_sdk present — recommended path.
        # Python 3.12+ is not officially tested; emit a warning but continue.
        if py >= (3, 12):
            warnings.warn(
                f"Python {py_str} with wirepod_vector_sdk is not officially tested. "
                "Consider using Python 3.11.",
                RuntimeWarning,
                stacklevel=2,
            )
        return

    if _legacy_sdk_available():
        # Legacy anki_vector SDK only.  Python 3.10+ removed the asyncio ``loop=``
        # keyword argument and changed the protobuf API — both of which the legacy
        # SDK relies on, producing cryptic errors at connection time.
        if py >= (3, 10):
            raise SystemExit(
                f"{_COMPAT_MSG}\n"
                f"  Detected:    Python {py_str} + anki_vector (legacy SDK)\n"
                "  The legacy anki_vector SDK has known incompatibilities with "
                "Python 3.10+\n"
                "  (asyncio loop= argument removal, protobuf API changes).\n"
                "  Fix: pip install wirepod_vector_sdk"
            )
        return

    # No Vector SDK at all
    raise SystemExit(
        f"{_COMPAT_MSG}\n"
        "  No Vector SDK found.\n"
        "  Fix: pip install wirepod_vector_sdk"
    )
