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
    speed: int = 50,
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

    import anki_vector.util as util  # noqa: PLC0415 — installed via wirepod_vector_sdk (or legacy anki_vector)

    robot = _robot()
    if distance_mm is not None:
        robot.behavior.drive_straight(util.distance_mm(distance_mm), util.speed_mmps(speed))
    if angle_deg is not None:
        robot.behavior.turn_in_place(util.degrees(angle_deg))

    return {"status": "ok", "distance_mm": distance_mm, "speed": speed, "angle_deg": angle_deg}


def vector_look() -> dict:
    """Capture an image from the robot's front camera.

    The camera feed is initialised once per connection and reused on subsequent
    calls.

    Returns:
        A dict containing ``image_base64`` — a base64-encoded JPEG — and
        ``content_type`` set to ``"image/jpeg"``.
    """
    robot = _robot()
    if not robot_manager._camera_initialized:
        robot.camera.init_camera_feed()
        robot_manager._camera_initialized = True
    pil_image = robot.camera.latest_image
    if pil_image is None:
        return {"status": "error", "message": "No camera image available"}

    with io.BytesIO() as buf:
        pil_image.raw_image.save(buf, format="JPEG")
        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return {"status": "ok", "image_base64": encoded, "content_type": "image/jpeg"}


def vector_face(image_base64: str, duration_sec: float = 5.0) -> dict:
    """Display a custom image on the robot's face screen.

    The image will be resized to 144 × 108 pixels (Vector's screen resolution)
    and converted to RGB before being sent.

    Args:
        image_base64: A base64-encoded image in any format supported by Pillow.
        duration_sec: How long to display the image in seconds (default: 5.0,
            must be between 0.1 and 60.0).

    Returns:
        A dict with a ``status`` key confirming success or an error message.
    """
    if not (0.1 <= duration_sec <= 60.0):
        return {
            "status": "error",
            "message": "duration_sec must be between 0.1 and 60.0",
        }

    from PIL import Image  # lazy import

    try:
        image_bytes = base64.b64decode(image_base64)
        with io.BytesIO(image_bytes) as src_buf:
            img = Image.open(src_buf).convert("RGB").resize((144, 108))
            with io.BytesIO() as dst_buf:
                img.save(dst_buf, format="JPEG")
                raw_bytes = dst_buf.getvalue()
    except Exception as exc:
        return {"status": "error", "message": f"Invalid image data: {exc}"}

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

    cube = robot.world.connected_light_cube
    if action in {"dock", "pickup", "roll"} and cube is None:
        return {
            "status": "error",
            "message": "No cube is connected; please connect a cube before using this action.",
        }

    if action == "dock":
        robot.behavior.dock_with_cube(cube)
    elif action == "pickup":
        robot.behavior.pick_up_object(cube)
    elif action == "drop":
        robot.behavior.place_object_on_ground_here()
    elif action == "roll":
        robot.behavior.roll_cube(cube)
    else:
        return {"status": "error", "message": f"Unknown cube action: {action!r}"}

    return {"status": "ok", "action": action}


def vector_status() -> dict:
    """Get the robot's current status.

    Returns:
        A dict containing ``battery_level``, ``is_charging``, and
        ``is_carrying_block``.
    """
    robot = _robot()
    battery = robot.get_battery_state()
    return {
        "status": "ok",
        "battery_level": battery.battery_level,
        "is_charging": robot.status.is_charging,
        "is_carrying_block": robot.status.is_carrying_block,
    }

def vector_drive_off_charger() -> dict:
    """Drive Vector off the charger.
    
    Use this first if Vector is on the charger and you want to drive.
    
    Returns:
        A dict with status and any error message.
    """
    robot = _robot()
    try:
        robot.behavior.drive_off_charger()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Head angle safe range (degrees)
_HEAD_ANGLE_MIN = -22.0
_HEAD_ANGLE_MAX = 45.0

# Lift height safe range (normalised 0.0–1.0)
_LIFT_HEIGHT_MIN = 0.0
_LIFT_HEIGHT_MAX = 1.0


def vector_head(angle_deg: float) -> dict:
    """Set Vector's head angle.

    The requested angle is clamped to the safe hardware range
    (``-22.0`` to ``45.0`` degrees) before being applied.

    Args:
        angle_deg: Desired head angle in degrees.  Values outside the safe
            range are silently clamped.

    Returns:
        A dict with ``status`` and the ``angle_deg`` that was applied after
        clamping.
    """
    import anki_vector.util as util  # noqa: PLC0415

    clamped = max(_HEAD_ANGLE_MIN, min(_HEAD_ANGLE_MAX, angle_deg))
    robot = _robot()
    robot.behavior.set_head_angle(util.degrees(clamped))
    return {"status": "ok", "angle_deg": clamped}


def vector_lift(height: float) -> dict:
    """Set Vector's lift/arm height.

    The requested height is clamped to the valid range (``0.0`` to ``1.0``)
    before being applied.

    Args:
        height: Desired lift height as a normalised value where ``0.0`` is the
            lowest position and ``1.0`` is the highest.  Values outside this
            range are silently clamped.

    Returns:
        A dict with ``status`` and the ``height`` that was applied after
        clamping.
    """
    clamped = max(_LIFT_HEIGHT_MIN, min(_LIFT_HEIGHT_MAX, height))
    robot = _robot()
    robot.behavior.set_lift_height(clamped)
    return {"status": "ok", "height": clamped}
