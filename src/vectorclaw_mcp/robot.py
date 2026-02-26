"""Robot connection management for VectorClaw MCP."""

from __future__ import annotations

import logging
import os
import threading
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

        Returns:
            A connected ``anki_vector.Robot`` object.

        Raises:
            RuntimeError: If ``VECTOR_SERIAL`` is not set.
            Exception: If the robot SDK raises during connection.
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

            robot = anki_vector.Robot(**kwargs)
            robot.connect()
            self._robot = robot
            return robot

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
