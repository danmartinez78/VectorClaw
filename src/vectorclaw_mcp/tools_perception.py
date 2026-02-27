"""Perception, status, and display-adjacent tools."""

from __future__ import annotations

import base64
import io
from typing import Optional

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
    }


def vector_capture_image() -> dict:
    robot = _robot()
    try:
        image = robot.camera.capture_single_image()
    except Exception as exc:
        return {"status": "error", "message": f"Failed to capture image: {exc}"}
    if image is None:
        return {"status": "error", "message": "No camera image available"}

    with io.BytesIO() as buf:
        image.raw_image.save(buf, format="JPEG")
        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return {"status": "ok", "image_base64": encoded, "content_type": "image/jpeg"}


def vector_face_detection(scan_duration_sec: float = 1.0) -> dict:
    import time

    robot = _robot()
    try:
        robot.vision.enable_face_detection(detect_faces=True)
    except Exception as exc:
        return {"status": "error", "message": f"Failed to enable face detection: {exc}"}

    disable_error: Optional[Exception] = None
    try:
        if scan_duration_sec > 0:
            time.sleep(scan_duration_sec)
        faces = list(robot.world.visible_faces)
    finally:
        try:
            robot.vision.disable_face_detection()
        except Exception as exc:
            disable_error = exc

    if disable_error is not None:
        return {"status": "error", "message": f"Failed to disable face detection: {disable_error}"}

    detections = [
        {"face_id": face.face_id, "name": face.name if face.name else None}
        for face in faces
    ]
    return {"status": "ok", "face_count": len(detections), "faces": detections}


def vector_vision_reset() -> dict:
    robot = _robot()
    try:
        robot.vision.disable_all_vision_modes()
    except Exception as exc:
        return {"status": "error", "message": f"Failed to reset vision modes: {exc}"}
    return {"status": "ok"}
