"""Perception, status, and display-adjacent tools.

Curiosity is what saves a personality from dying when linked with others.
"""

from __future__ import annotations

import base64
import io

from .robot import robot_manager
from .tools_common import _robot


def vector_animate(animation_name: str) -> dict:
    robot = _robot()
    robot.anim.play_animation(animation_name)
    return {"status": "ok", "animation": animation_name}


def vector_look() -> dict:
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
    if not (0.1 <= duration_sec <= 60.0):
        return {"status": "error", "message": "duration_sec must be between 0.1 and 60.0"}

    from PIL import Image

    try:
        image_bytes = base64.b64decode(image_base64)
        with io.BytesIO(image_bytes) as src_buf:
            import anki_vector.screen as _screen_mod
            screen_w, screen_h = _screen_mod.dimensions()
            img = Image.open(src_buf).convert("RGB").resize((screen_w, screen_h))
    except Exception as exc:
        return {"status": "error", "message": f"Invalid image data: {exc}"}

    screen_data = _screen_mod.convert_image_to_screen_data(img)
    robot = _robot()
    robot.screen.set_screen_with_image_data(screen_data, duration_sec=duration_sec)
    return {"status": "ok"}


def vector_pose() -> dict:
    robot = _robot()
    pose = robot.pose
    return {
        "status": "ok",
        "x": pose.position.x,
        "y": pose.position.y,
        "z": pose.position.z,
        "angle_deg": pose.rotation.angle_z.degrees,
        "origin_id": pose.origin_id,
        "is_picked_up": robot.status.is_picked_up,
        "localized_to_object_id": (
            None
            if robot.localized_to_object_id == -1
            else robot.localized_to_object_id
        ),
    }


def vector_cube(action: str) -> dict:
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
        robot.behavior.pickup_object(cube)
    elif action == "drop":
        robot.behavior.place_object_on_ground_here()
    elif action == "roll":
        robot.behavior.roll_cube(cube)
    else:
        return {"status": "error", "message": f"Unknown cube action: {action!r}"}

    return {"status": "ok", "action": action}


def vector_status() -> dict:
    robot = _robot()
    battery = robot.get_battery_state()
    st = robot.status
    return {
        "status": "ok",
        "battery_level": battery.battery_level,
        "is_charging": st.is_charging,
        "is_carrying_block": st.is_carrying_block,
        "is_on_charger": st.is_on_charger,
        "is_cliff_detected": st.is_cliff_detected,
        "is_picked_up": st.is_picked_up,
    }


def vector_scan() -> dict:
    try:
        robot = _robot()
        robot.behavior.look_around_in_place()
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def vector_find_faces() -> dict:
    try:
        robot = _robot()
        robot.behavior.find_faces()
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def vector_list_visible_faces() -> dict:
    try:
        robot = _robot()
        faces = [{"face_id": f.face_id, "name": f.name} for f in robot.world.visible_faces]
        return {"status": "ok", "faces": faces}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def vector_list_visible_objects() -> dict:
    try:
        robot = _robot()
        objects = [{"object_id": o.object_id} for o in robot.world.visible_objects]
        return {"status": "ok", "objects": objects}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def vector_capture_image() -> dict:
    """Capture a single image from the camera using camera.capture_single_image."""
    robot = _robot()
    try:
        image = robot.camera.capture_single_image()
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

    if image is None:
        return {"status": "error", "message": "No image returned by camera"}

    try:
        with io.BytesIO() as buf:
            image.raw_image.save(buf, format="JPEG")
            encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception as exc:
        return {"status": "error", "message": f"Failed to encode image: {exc}"}

    return {"status": "ok", "image_base64": encoded, "content_type": "image/jpeg"}


def vector_face_detection() -> dict:
    """Return a summary of currently visible faces (no raw image data)."""
    robot = _robot()
    try:
        faces = list(robot.world.visible_faces)
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

    def _normalize_expression(expr) -> str:
        """Normalize face expression values across SDK implementations."""
        # If this is an Enum (or Enum-like), prefer its name in lowercase.
        name = getattr(expr, "name", None)
        if isinstance(name, str):
            return name.lower()
        return str(expr)

    detections = [
        {
            "face_id": f.face_id,
            "expression": _normalize_expression(f.expression),
        }
        for f in faces
    ]
    return {"status": "ok", "face_count": len(detections), "faces": detections}


def vector_enable_face_detection(enable: bool = True) -> dict:
    """Enable or disable face detection via vision.enable_face_detection."""
    robot = _robot()
    try:
        robot.vision.enable_face_detection(detect_faces=enable)
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
    return {"status": "ok", "face_detection_enabled": enable}


def vector_enable_motion_detection(enable: bool = True) -> dict:
    """Enable or disable motion detection via vision.enable_motion_detection."""
    robot = _robot()
    try:
        robot.vision.enable_motion_detection(detect_motion=enable)
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
    return {"status": "ok", "motion_detection_enabled": enable}


def vector_vision_status() -> dict:
    """Return current vision mode status flags."""
    robot = _robot()
    try:
        return {
            "status": "ok",
            "detect_faces": robot.vision.detect_faces,
            "detect_motion": robot.vision.detect_motion,
            "detect_custom_objects": robot.vision.detect_custom_objects,
            "display_camera_feed_on_face": robot.vision.display_camera_feed_on_face,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def vector_vision_reset() -> dict:
    """Disable all vision modes via vision.disable_all_vision_modes."""
    robot = _robot()
    try:
        robot.vision.disable_all_vision_modes()
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
    return {"status": "ok"}

def vector_charger_status() -> dict:
    robot = _robot()
    try:
        battery = robot.get_battery_state()
        return {
            "status": "ok",
            "is_charging": robot.status.is_charging,
            "battery_level": battery.battery_level,
            "is_on_charger": robot.status.is_on_charger,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def vector_touch_status() -> dict:
    robot = _robot()
    try:
        touch = robot.touch.last_sensor_reading
        return {
            "status": "ok",
            "is_being_touched": touch.is_being_touched,
            "raw_touch_value": touch.raw_touch_value,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def vector_proximity_status() -> dict:
    robot = _robot()
    try:
        prox = robot.proximity.last_sensor_reading
        return {
            "status": "ok",
            "distance_mm": prox.distance.distance_mm,
            "signal_quality": prox.signal_quality,
            "unobstructed": prox.unobstructed,
            "found_object": prox.found_object,
            "is_lift_in_fov": prox.is_lift_in_fov,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
