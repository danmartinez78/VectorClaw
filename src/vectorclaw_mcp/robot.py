"""Robot connection management for VectorClaw MCP."""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)


class RobotManager:
    """Manages a single shared connection to an Anki Vector robot.

    The connection is established lazily on the first tool call and reused
    for subsequent calls.  Call :meth:`disconnect` to release the connection
    when the server shuts down.

    Thread-safety: :meth:`connect` is protected by a lock so that concurrent
    tool calls (dispatched via ``run_in_executor``) cannot race to create
    multiple robot connections.
    """

    def __init__(self) -> None:
        self._robot: Optional[object] = None
        self._camera_initialized: bool = False
        self._lock = threading.Lock()

    def connect(self) -> object:
        """Return an active :class:`anki_vector.Robot` instance.

        The robot serial number is read from the ``VECTOR_SERIAL`` environment
        variable.  An optional IP address may be supplied via ``VECTOR_HOST``.

        Connection attempts are retried on transient failures.  The maximum
        number of retries is controlled by ``VECTOR_CONNECT_RETRIES`` (default
        ``3``) and the initial delay between attempts by ``VECTOR_CONNECT_DELAY``
        (default ``1.0`` seconds).  Each successive delay is doubled (exponential
        backoff).

        Returns:
            A connected ``anki_vector.Robot`` object.

        Raises:
            RuntimeError: If ``VECTOR_SERIAL`` is not set.
            Exception: If the robot SDK raises during connection after all retries.
        """
        with self._lock:
            if self._robot is not None:
                return self._robot

            import anki_vector  # imported lazily so unit tests don't require the SDK

            serial = os.environ.get("VECTOR_SERIAL")
            if not serial:
                raise RuntimeError(
                    "VECTOR_SERIAL environment variable is required but not set."
                )

            host = os.environ.get("VECTOR_HOST")
            kwargs: dict = {"serial": serial}
            if host:
                kwargs["ip"] = host

            max_retries = int(os.environ.get("VECTOR_CONNECT_RETRIES", "3"))
            delay = float(os.environ.get("VECTOR_CONNECT_DELAY", "1.0"))

            last_exc: Exception = RuntimeError("No connection attempt was made.")
            for attempt in range(max_retries + 1):
                try:
                    robot = anki_vector.Robot(**kwargs)
                    robot.connect()
                    self._robot = robot
                    return robot
                except RuntimeError:
                    raise
                except Exception as exc:
                    last_exc = exc
                    if attempt < max_retries:
                        logger.warning(
                            "Failed to connect to robot (attempt %d/%d): %s. "
                            "Retrying in %.1fs…",
                            attempt + 1,
                            max_retries + 1,
                            exc,
                            delay,
                        )
                        time.sleep(delay)
                        delay *= 2
                    else:
                        logger.error(
                            "Failed to connect to robot after %d attempt(s): %s",
                            max_retries + 1,
                            exc,
                        )
            raise last_exc

    def disconnect(self) -> None:
        """Disconnect from the robot if currently connected."""
        with self._lock:
            if self._robot is not None:
                try:
                    self._robot.disconnect()
                except Exception:
                    logger.exception("Error while disconnecting from robot")
                finally:
                    self._robot = None
                    self._camera_initialized = False

    def reset(self) -> None:
        """Reset the manager to a disconnected state without calling disconnect.

        Intended for use in tests only.
        """
        with self._lock:
            self._robot = None
            self._camera_initialized = False

    @property
    def is_connected(self) -> bool:
        """Return ``True`` if the robot connection is currently active."""
        return self._robot is not None


# Module-level singleton used by tool implementations.
robot_manager = RobotManager()
