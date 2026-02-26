"""Tool implementations for VectorClaw MCP.

Each public function in this module corresponds to a named MCP tool.  They all
accept plain Python values (already validated by the MCP layer) and return a
``dict`` that will be serialised as the tool result.
"""

from __future__ import annotations

import base64
import io
from typing import Optional

from .robot import robot_manager


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _robot():
    """Return the active robot instance, connecting if necessary."""
    return robot_manager.connect()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

def vector_say(text: str) -> dict:
    """Make the robot speak *text* aloud.

    Args:
        text: The text the robot should say.

    Returns:
        A dict with a ``status`` key confirming success.
    """
    robot = _robot()
    robot.behavior.say_text(text)
    return {"status": "ok", "said": text}


def vector_animate(animation_name: str) -> dict:
    """Play a named animation on the robot.

    Args:
        animation_name: The animation identifier, e.g.
            ``"anim_eyepose_happy_content_01"``.

    Returns:
        A dict with a ``status`` key confirming success.
    """
    robot = _robot()
    robot.anim.play_animation(animation_name)
    return {"status": "ok", "animation": animation_name}


def vector_drive(
    distance_mm: Optional[float] = None,
    angle_deg: Optional[float] = None,
) -> dict:
    """Move the robot.

    At least one of *distance_mm* or *angle_deg* must be provided.

    Args:
        distance_mm: Distance to drive straight in millimetres.  Positive
            values move forward, negative values move backward.
        angle_deg: Angle to turn in place in degrees.  Positive values turn
            left, negative values turn right.

    Returns:
        A dict with a ``status`` key and the executed movement parameters.
    """
    if distance_mm is None and angle_deg is None:
        return {"status": "error", "message": "distance_mm or angle_deg is required"}

    import anki_vector.util as util  # lazy import

    robot = _robot()
    if distance_mm is not None:
        robot.behavior.drive_straight(util.distance_mm(distance_mm))
    if angle_deg is not None:
        robot.behavior.turn_in_place(util.degrees(angle_deg))

    return {"status": "ok", "distance_mm": distance_mm, "angle_deg": angle_deg}


def vector_look() -> dict:
    """Capture an image from the robot's front camera.

    Returns:
        A dict containing ``image_base64`` — a base64-encoded JPEG — and
        ``content_type`` set to ``"image/jpeg"``.
    """
    robot = _robot()
    robot.camera.init_camera_feed()
    pil_image = robot.camera.latest_image
    if pil_image is None:
        return {"status": "error", "message": "No camera image available"}

    buf = io.BytesIO()
    pil_image.raw_image.save(buf, format="JPEG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return {"status": "ok", "image_base64": encoded, "content_type": "image/jpeg"}


def vector_face(image_base64: str, duration_sec: float = 5.0) -> dict:
    """Display a custom image on the robot's face screen.

    The image will be resized to 144 × 108 pixels (Vector's screen resolution)
    and converted to RGB before being sent.

    Args:
        image_base64: A base64-encoded image in any format supported by Pillow.
        duration_sec: How long to display the image in seconds (default: 5.0).

    Returns:
        A dict with a ``status`` key confirming success.
    """
    from PIL import Image  # lazy import

    image_bytes = base64.b64decode(image_base64)
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((144, 108))

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    raw_bytes = buf.getvalue()

    robot = _robot()
    robot.screen.set_screen_with_image_data(raw_bytes, duration_sec=duration_sec)
    return {"status": "ok"}


def vector_pose() -> dict:
    """Get the robot's current position and orientation.

    Returns:
        A dict with ``x``, ``y``, ``z`` coordinates (millimetres) and
        ``angle_deg`` (degrees).
    """
    robot = _robot()
    pose = robot.pose
    return {
        "status": "ok",
        "x": pose.position.x,
        "y": pose.position.y,
        "z": pose.position.z,
        "angle_deg": pose.rotation.angle_z.degrees,
    }


def vector_cube(action: str) -> dict:
    """Interact with Vector's cube accessory.

    Args:
        action: One of ``"dock"``, ``"pickup"``, ``"drop"``, or ``"roll"``.

    Returns:
        A dict with a ``status`` key confirming success.
    """
    robot = _robot()
    action = action.lower()
    if action == "dock":
        robot.behavior.dock_with_cube(robot.world.connected_light_cube)
    elif action == "pickup":
        robot.behavior.pick_up_object(robot.world.connected_light_cube)
    elif action == "drop":
        robot.behavior.place_object_on_ground_here()
    elif action == "roll":
        robot.behavior.roll_cube(robot.world.connected_light_cube)
    else:
        return {"status": "error", "message": f"Unknown cube action: {action!r}"}

    return {"status": "ok", "action": action}


def vector_status() -> dict:
    """Get the robot's current status.

    Returns:
        A dict containing ``battery_level``, ``is_charging``, and
        ``is_carrying_object``.
    """
    robot = _robot()
    battery = robot.get_battery_state()
    return {
        "status": "ok",
        "battery_level": battery.battery_level,
        "is_charging": robot.status.is_charging,
        "is_carrying_object": robot.status.is_carrying_object,
    }
