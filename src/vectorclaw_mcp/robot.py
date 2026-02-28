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

        The ``anki_vector`` module namespace is provided by installing
        ``wirepod_vector_sdk`` (recommended) or the legacy ``anki_vector``
        package — both expose the same ``anki_vector`` Python namespace.

        The robot serial number is read from the ``VECTOR_SERIAL`` environment
        variable.  An optional IP address may be supplied via ``VECTOR_HOST``.

        Connection attempts are retried on transient network failures
        (``ConnectionError``, ``TimeoutError``, ``OSError``).  The maximum
        number of retries is controlled by ``VECTOR_CONNECT_RETRIES`` (default
        ``3``) and the initial delay between attempts by ``VECTOR_CONNECT_DELAY``
        (default ``1.0`` seconds).  Each successive delay is doubled (exponential
        backoff).  ``RuntimeError`` and other non-transient exceptions are
        re-raised immediately without retrying.

        Returns:
            A connected ``anki_vector.Robot`` object.

        Raises:
            RuntimeError: If ``VECTOR_SERIAL`` is not set, or if
                ``VECTOR_CONNECT_RETRIES``/``VECTOR_CONNECT_DELAY`` contain
                invalid (negative) values.
            ConnectionError | TimeoutError | OSError: If the robot is
                unreachable after all retry attempts.
        """
        with self._lock:
            if self._robot is not None:
                return self._robot

            import anki_vector  # noqa: PLC0415 — installed via wirepod_vector_sdk (or legacy anki_vector)

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
            if max_retries < 0:
                raise RuntimeError(
                    f"Invalid VECTOR_CONNECT_RETRIES={max_retries!r}: value must be >= 0."
                )
            if delay < 0:
                raise RuntimeError(
                    f"Invalid VECTOR_CONNECT_DELAY={delay!r}: value must be >= 0."
                )

            last_exc: Exception = OSError("Connection failed.")
            for attempt in range(max_retries + 1):
                robot = anki_vector.Robot(**kwargs)
                try:
                    robot.connect()
                    try:
                        robot.vision.enable_face_detection(estimate_expression=True)
                    except Exception:
                        logger.warning(
                            "Face detection enablement failed; face detection may be unavailable.",
                            exc_info=True,
                        )
                    try:
                        robot.vision.enable_custom_object_detection()
                    except Exception:
                        logger.warning(
                            "Custom object detection enablement failed; object detection may be unavailable.",
                            exc_info=True,
                        )
                    self._robot = robot
                    return robot
                except (ConnectionError, TimeoutError, OSError) as exc:
                    last_exc = exc
                    try:
                        robot.disconnect()
                    except Exception:
                        pass
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
