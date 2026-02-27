"""Perception, status, and display-adjacent tools."""

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
    robot = _robot()
    battery = robot.get_battery_state()
    return {
        "status": "ok",
        "battery_level": battery.battery_level,
        "is_charging": robot.status.is_charging,
        "is_carrying_block": robot.status.is_carrying_block,
        "is_cliff_detected": robot.status.is_cliff_detected,
        "is_moving": robot.status.is_moving,
    }


def vector_charger_status() -> dict:
    """Return charger-related status fields."""
    robot = _robot()
    return {
        "status": "ok",
        "is_charging": robot.status.is_charging,
        "is_on_charger_platform": robot.status.is_on_charger_platform,
    }


def vector_touch_status() -> dict:
    """Return touch sensor status."""
    robot = _robot()
    try:
        last_touch = robot.touch.last_touch_time
        return {
            "status": "ok",
            "last_touch_time": last_touch,
            "is_being_held": robot.status.is_being_held,
        }
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return {"status": "error", "message": str(exc)}


def vector_proximity_status() -> dict:
    """Return proximity sensor reading."""
    robot = _robot()
    reading = robot.proximity.last_sensor_reading
    if reading is None:
        return {"status": "ok", "distance_mm": None, "found_object": False}
    return {
        "status": "ok",
        "distance_mm": reading.distance.distance_mm,
        "found_object": reading.found_object,
    }


def vector_scan(num_rotations: int = 1) -> dict:
    """Scan the environment by looking around in place."""
    robot = _robot()
    try:
        robot.behavior.look_around_in_place(num_rotations=num_rotations)
        return {"status": "ok", "num_rotations": num_rotations}
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return {"status": "error", "message": str(exc)}


def vector_find_faces() -> dict:
    """Search for faces using the find-faces behavior."""
    robot = _robot()
    try:
        robot.behavior.find_faces()
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return {"status": "error", "message": str(exc)}


def vector_list_visible_faces() -> dict:
    """Return a list of currently visible faces."""
    robot = _robot()
    faces = [
        {"face_id": f.face_id, "name": getattr(f, "name", "")}
        for f in robot.world.visible_faces
    ]
    return {"status": "ok", "faces": faces, "count": len(faces)}


def vector_list_visible_objects() -> dict:
    """Return a list of currently visible objects (standard + custom)."""
    robot = _robot()
    objects = [
        {"object_id": str(getattr(o, "object_id", "")), "object_type": type(o).__name__}
        for o in robot.world.visible_objects
    ]
    custom_objects = [
        {"object_id": str(getattr(o, "object_id", "")), "object_type": "custom"}
        for o in robot.world.visible_custom_objects
    ]
    all_objects = objects + custom_objects
    return {"status": "ok", "objects": all_objects, "count": len(all_objects)}


def vector_capture_image() -> dict:
    """Capture a single image via camera.capture_single_image."""
    robot = _robot()
    try:
        pil_image = robot.camera.capture_single_image()
        if pil_image is None:
            return {"status": "error", "message": "No image captured"}
        with io.BytesIO() as buf:
            pil_image.raw_image.save(buf, format="JPEG")
            encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return {"status": "ok", "image_base64": encoded, "content_type": "image/jpeg"}
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return {"status": "error", "message": str(exc)}


def vector_face_detection() -> dict:
    """Return a summary of currently detected faces from world state."""
    robot = _robot()
    faces = list(robot.world.visible_faces)
    summary = [
        {
            "face_id": f.face_id,
            "name": getattr(f, "name", ""),
            "expression": str(getattr(f, "expression", "")),
        }
        for f in faces
    ]
    return {"status": "ok", "detected_faces": summary, "count": len(summary)}


def vector_vision_reset() -> dict:
    """Disable all vision modes to reset vision processing state."""
    robot = _robot()
    try:
        robot.vision.disable_all_vision_modes()
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - defensive runtime handling
        return {"status": "error", "message": str(exc)}
