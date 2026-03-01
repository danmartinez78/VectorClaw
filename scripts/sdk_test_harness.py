#!/usr/bin/env python3

"""
Vector SDK Interactive Test Harness

An interactive script that connects to a Vector robot and lets you select
SDK functions from a categorized menu. Results are printed to the console.

Usage:
    python sdk_test_harness.py
    python sdk_test_harness.py -s <serial>
"""

import os
import sys
import time
import traceback

# Ensure the SDK package is importable when running from the examples directory
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import anki_vector
from anki_vector.util import degrees, distance_mm, speed_mmps

# ---------------------------------------------------------------------------
# Animation list cache — loaded lazily on first use instead of at startup.
# Wire-Pod environments may not respond to ListAnimations/ListAnimationTriggers
# within the default 10s gRPC deadline, so we never block connect() on it.
# ---------------------------------------------------------------------------
_anim_cache_attempted = False


def _ensure_anim_cache(robot):
    """Best-effort lazy load of animation lists. Warns but does not raise."""
    global _anim_cache_attempted
    if _anim_cache_attempted:
        return
    _anim_cache_attempted = True
    print("  (Loading animation lists from robot — this may take a moment ...)")
    for loader_name in ("load_animation_list", "load_animation_trigger_list"):
        try:
            fut = getattr(robot.anim, loader_name)()
            if hasattr(fut, "result"):
                fut.result()  # blocks, but only once and only when user asks
        except Exception as e:
            print(f"  WARNING: {loader_name} failed: {e}")
            print("  Animation listing may be unavailable.  Direct play-by-name still works.")


# ---------------------------------------------------------------------------
# Menu definition
# Each category has entries: (label, callable_taking_robot)
# ---------------------------------------------------------------------------

def _safe_input(prompt, default=None):
    """Get user input with an optional default."""
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    val = input(prompt).strip()
    return val if val else default


# ---- Robot Info -----------------------------------------------------------

def info_battery(robot):
    """Get battery state (voltage, level, charging)."""
    b = robot.get_battery_state()
    print(f"  Battery voltage : {b.battery_volts:.2f} V")
    print(f"  Battery level   : {b.battery_level}")
    print(f"  Is charging     : {b.is_charging}")
    print(f"  Is on charger   : {b.is_on_charger}")
    print(f"  Suggested charger sec: {b.suggested_charger_sec}")

def info_version(robot):
    """Get firmware / engine version info."""
    v = robot.get_version_state()
    print(f"  OS version       : {v.os_version}")
    print(f"  Engine build id  : {v.engine_build_id}")

def info_pose(robot):
    """Print current robot pose."""
    p = robot.pose
    print(f"  Pose             : {p}")
    print(f"  Pose angle (rad) : {robot.pose_angle_rad}")
    print(f"  Pose pitch (rad) : {robot.pose_pitch_rad}")

def info_sensors(robot):
    """Print accelerometer, gyro, wheel speeds."""
    print(f"  Accel            : {robot.accel}")
    print(f"  Gyro             : {robot.gyro}")
    print(f"  Left wheel speed : {robot.left_wheel_speed_mmps} mm/s")
    print(f"  Right wheel speed: {robot.right_wheel_speed_mmps} mm/s")
    print(f"  Head angle (rad) : {robot.head_angle_rad}")
    print(f"  Lift height (mm) : {robot.lift_height_mm}")

def info_status_flags(robot):
    """Print all robot status flags."""
    s = robot.status
    flags = [
        ("is_being_held",       s.is_being_held),
        ("is_charging",         s.is_charging),
        ("is_on_charger",       s.is_on_charger),
        ("are_motors_moving",   s.are_motors_moving),
        ("is_carrying_block",   s.is_carrying_block),
        ("is_animating",        s.is_animating),
        ("is_pathing",          s.is_pathing),
        ("is_cliff_detected",   s.is_cliff_detected),
        ("are_wheels_moving",   s.are_wheels_moving),
        ("is_robot_moving",     s.is_robot_moving),
        ("is_button_pressed",   s.is_button_pressed),
        ("calm_power_mode",     s.calm_power_mode),
    ]
    for name, val in flags:
        print(f"  {name:25s}: {val}")


# ---- Speech ---------------------------------------------------------------

def speech_say_text(robot):
    """Say arbitrary text."""
    text = _safe_input("  Enter text to say", "Hello from the SDK test harness!")
    print(f"  Saying: {text!r}")
    result = robot.behavior.say_text(text)
    print(f"  Result: {result}")

def speech_say_localized(robot):
    """Say text in a specific language (en/de/fr/ja)."""
    text = _safe_input("  Enter text", "Hallo Welt")
    lang = _safe_input("  Language (en/de/fr/ja)", "de")
    result = robot.behavior.say_localized_text(text, language=lang)
    print(f"  Result: {result}")


# ---- Movement / Behavior --------------------------------------------------

def move_drive_off_charger(robot):
    """Drive off charger."""
    result = robot.behavior.drive_off_charger()
    print(f"  Result: {result}")

def move_drive_on_charger(robot):
    """Drive onto charger."""
    result = robot.behavior.drive_on_charger()
    print(f"  Result: {result}")

def move_drive_straight(robot):
    """Drive straight a given distance (mm) at a speed (mm/s)."""
    dist = float(_safe_input("  Distance (mm, negative=backward)", "100"))
    spd = float(_safe_input("  Speed (mm/s)", "50"))
    print(f"  Driving {dist} mm at {spd} mm/s ...")
    result = robot.behavior.drive_straight(distance_mm(dist), speed_mmps(spd))
    print(f"  Result: {result}")

def move_turn_in_place(robot):
    """Turn in place by a given angle (degrees)."""
    angle = float(_safe_input("  Angle (degrees, positive=CCW)", "90"))
    print(f"  Turning {angle} degrees ...")
    result = robot.behavior.turn_in_place(degrees(angle))
    print(f"  Result: {result}")

def move_set_head_angle(robot):
    """Set head angle (degrees). Range roughly -22 to 45."""
    angle = float(_safe_input("  Head angle (degrees)", "20"))
    result = robot.behavior.set_head_angle(degrees(angle))
    print(f"  Result: {result}")

def move_set_lift_height(robot):
    """Set lift height (0.0 = low, 1.0 = high)."""
    height = float(_safe_input("  Lift height (0.0 - 1.0)", "0.5"))
    result = robot.behavior.set_lift_height(height)
    print(f"  Result: {result}")

def move_look_around(robot):
    """Look around in place (scan surroundings)."""
    print("  Looking around ...")
    result = robot.behavior.look_around_in_place()
    print(f"  Result: {result}")

def move_find_faces(robot):
    """Turn in place looking for faces."""
    print("  Searching for faces ...")
    result = robot.behavior.find_faces()
    print(f"  Result: {result}")

def move_drive_square(robot):
    """Drive in a square (200mm sides)."""
    side = float(_safe_input("  Side length (mm)", "200"))
    spd = float(_safe_input("  Speed (mm/s)", "50"))
    for i in range(4):
        print(f"  Side {i+1}/4 ...")
        robot.behavior.drive_straight(distance_mm(side), speed_mmps(spd))
        robot.behavior.turn_in_place(degrees(90))
    print("  Square complete!")


# ---- Motors (low-level) ---------------------------------------------------

def motors_wheels(robot):
    """Set wheel motors directly (mm/s). 0 = stop/unlock."""
    left = float(_safe_input("  Left wheel speed (mm/s)", "50"))
    right = float(_safe_input("  Right wheel speed (mm/s)", "50"))
    dur = float(_safe_input("  Duration (seconds)", "2"))
    print(f"  Running wheels L={left} R={right} for {dur}s ...")
    robot.motors.set_wheel_motors(left, right)
    time.sleep(dur)
    robot.motors.set_wheel_motors(0, 0)
    print("  Stopped.")

def motors_head(robot):
    """Move head motor at speed (rad/s). 0 = stop."""
    speed = float(_safe_input("  Head speed (rad/s, positive=up)", "2"))
    dur = float(_safe_input("  Duration (seconds)", "1"))
    robot.motors.set_head_motor(speed)
    time.sleep(dur)
    robot.motors.set_head_motor(0)
    print("  Stopped.")

def motors_lift(robot):
    """Move lift motor at speed (rad/s). 0 = stop."""
    speed = float(_safe_input("  Lift speed (rad/s, positive=up)", "2"))
    dur = float(_safe_input("  Duration (seconds)", "1"))
    robot.motors.set_lift_motor(speed)
    time.sleep(dur)
    robot.motors.set_lift_motor(0)
    print("  Stopped.")


# ---- Animations -----------------------------------------------------------

def anim_list_triggers(robot):
    """List all available animation triggers."""
    _ensure_anim_cache(robot)
    triggers = robot.anim.anim_trigger_list
    if not triggers:
        print("  No animation triggers available (list RPC may have failed).")
        return
    print(f"  {len(triggers)} animation trigger(s) available:")
    for i, t in enumerate(triggers, 1):
        print(f"    {i:3d}. {t}")

def anim_list_animations(robot):
    """List all available animations."""
    _ensure_anim_cache(robot)
    anims = robot.anim.anim_list
    if not anims:
        print("  No animations available (list RPC may have failed).")
        return
    print(f"  {len(anims)} animation(s) available:")
    for i, a in enumerate(anims, 1):
        print(f"    {i:3d}. {a}")

def anim_play_trigger(robot):
    """Play an animation trigger by name."""
    name = _safe_input("  Trigger name", "GreetAfterLongTime")
    print(f"  Playing trigger: {name}")
    result = robot.anim.play_animation_trigger(name)
    print(f"  Result: {result}")

def anim_play_animation(robot):
    """Play a specific animation by name."""
    name = _safe_input("  Animation name", "anim_pounce_success_02")
    print(f"  Playing animation: {name}")
    result = robot.anim.play_animation(name)
    print(f"  Result: {result}")


# ---- Appearance -----------------------------------------------------------

def appearance_eye_color(robot):
    """Set eye color (hue 0-1, saturation 0-1)."""
    print("  Presets: teal(0.42,1.0) purple(0.83,0.76) orange(0.05,0.95) green(0.33,1.0) blue(0.57,1.0)")
    hue = float(_safe_input("  Hue (0.0 - 1.0)", "0.83"))
    sat = float(_safe_input("  Saturation (0.0 - 1.0)", "0.76"))
    robot.behavior.set_eye_color(hue=hue, saturation=sat)
    print(f"  Eye color set to hue={hue}, saturation={sat}.")
    print("  (Wait a few seconds to see the change)")
    time.sleep(3)


# ---- Audio ----------------------------------------------------------------

def audio_set_volume(robot):
    """Set master volume level."""
    print("  Volume levels: 0=LOW, 1=MEDIUM_LOW, 2=MEDIUM, 3=MEDIUM_HIGH, 4=HIGH")
    level = int(_safe_input("  Volume level (0-4)", "2"))
    vol_map = {
        0: anki_vector.audio.RobotVolumeLevel.LOW,
        1: anki_vector.audio.RobotVolumeLevel.MEDIUM_LOW,
        2: anki_vector.audio.RobotVolumeLevel.MEDIUM,
        3: anki_vector.audio.RobotVolumeLevel.MEDIUM_HIGH,
        4: anki_vector.audio.RobotVolumeLevel.HIGH,
    }
    vol = vol_map.get(level, anki_vector.audio.RobotVolumeLevel.MEDIUM)
    result = robot.audio.set_master_volume(vol)
    print(f"  Result: {result}")

def audio_play_wav(robot):
    """Play a WAV file on Vector's speaker."""
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds", "vector_bell_whistle.wav")
    path = _safe_input("  WAV file path", default_path)
    if not os.path.isfile(path):
        print(f"  ERROR: File not found: {path}")
        return
    volume = int(_safe_input("  Volume (0-100)", "75"))
    print(f"  Playing {path} ...")
    result = robot.audio.stream_wav_file(path, volume)
    print(f"  Result: {result}")


# ---- Screen ---------------------------------------------------------------

def screen_solid_color(robot):
    """Fill Vector's screen with a solid color."""
    r = int(_safe_input("  Red (0-255)", "0"))
    g = int(_safe_input("  Green (0-255)", "128"))
    b = int(_safe_input("  Blue (0-255)", "255"))
    dur = float(_safe_input("  Duration (seconds)", "3"))
    c = anki_vector.color.Color(rgb=[r, g, b])
    robot.screen.set_screen_to_color(c, dur)
    print(f"  Displaying color ({r},{g},{b}) for {dur}s ...")
    time.sleep(dur)

def screen_display_text(robot):
    """Render text onto Vector's face screen using PIL."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  ERROR: Pillow is required. pip install Pillow")
        return
    text = _safe_input("  Text to display", "Hello!")
    dur = float(_safe_input("  Duration (seconds)", "4"))
    img = Image.new('RGB', (184, 96), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except (IOError, OSError):
        font = ImageFont.load_default()
    draw.text((10, 30), text, fill=(255, 255, 255), font=font)
    screen_data = anki_vector.screen.convert_image_to_screen_data(img)
    robot.screen.set_screen_with_image_data(screen_data, dur)
    print(f"  Displaying text for {dur}s ...")
    time.sleep(dur)


# ---- Vision ---------------------------------------------------------------

def vision_enable_face_detection(robot):
    """Enable/disable face detection."""
    enable = _safe_input("  Enable face detection? (y/n)", "y").lower() == 'y'
    robot.vision.enable_face_detection(detect_faces=enable)
    print(f"  Face detection: {'ON' if enable else 'OFF'}")

def vision_enable_motion_detection(robot):
    """Enable/disable motion detection."""
    enable = _safe_input("  Enable motion detection? (y/n)", "y").lower() == 'y'
    robot.vision.enable_motion_detection(detect_motion=enable)
    print(f"  Motion detection: {'ON' if enable else 'OFF'}")

def vision_camera_on_face(robot):
    """Show camera feed on Vector's face screen."""
    enable = _safe_input("  Show camera on face? (y/n)", "y").lower() == 'y'
    robot.vision.enable_display_camera_feed_on_face(enable=enable)
    print(f"  Camera on face: {'ON' if enable else 'OFF'}")
    if enable:
        dur = float(_safe_input("  Duration (seconds)", "5"))
        time.sleep(dur)
        robot.vision.enable_display_camera_feed_on_face(enable=False)
        print("  Camera on face: OFF")

def vision_status(robot):
    """Show current vision mode statuses."""
    print(f"  Face detection     : {robot.vision.detect_faces}")
    print(f"  Custom obj detect  : {robot.vision.detect_custom_objects}")
    print(f"  Motion detection   : {robot.vision.detect_motion}")
    print(f"  Camera on face     : {robot.vision.display_camera_feed_on_face}")


# ---- Proximity / Touch ----------------------------------------------------

def sensor_proximity(robot):
    """Read latest proximity sensor data."""
    p = robot.proximity.last_sensor_reading
    print(f"  Distance          : {p.distance}")
    print(f"  Signal quality    : {p.signal_quality}")
    print(f"  Unobstructed      : {p.unobstructed}")
    print(f"  Found object      : {p.found_object}")
    print(f"  Lift in FOV       : {p.is_lift_in_fov}")

def sensor_touch(robot):
    """Read latest touch sensor data."""
    t = robot.touch.last_sensor_reading
    print(f"  Raw touch value   : {t.raw_touch_value}")
    print(f"  Is being touched  : {t.is_being_touched}")

def sensor_continuous(robot):
    """Continuously read proximity and touch (press Ctrl+C to stop)."""
    print("  Reading sensors continuously. Press Ctrl+C to stop.")
    try:
        while True:
            p = robot.proximity.last_sensor_reading
            t = robot.touch.last_sensor_reading
            sys.stdout.write(
                f"\r  Prox: {str(p.distance):>20s} | "
                f"Touch: {'YES' if t.is_being_touched else 'no ':>3s} (raw={t.raw_touch_value})"
            )
            sys.stdout.flush()
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n  Stopped.")


# ---- Photos ---------------------------------------------------------------

def photos_list(robot):
    """List stored photos on the robot."""
    robot.photos.load_photo_info()
    photos = robot.photos.photo_info
    if not photos:
        print("  No photos stored on robot.")
        return
    print(f"  {len(photos)} photo(s) found:")
    for p in photos:
        print(f"    ID: {p.photo_id}  Timestamp: {p.timestamp_utc}")


# ---- Camera ---------------------------------------------------------------

def camera_capture(robot):
    """Capture a single frame from Vector's camera and save to file."""
    try:
        from PIL import Image
    except ImportError:
        print("  ERROR: Pillow is required. pip install Pillow")
        return
    robot.camera.init_camera_feed()
    time.sleep(1)  # allow a frame to arrive
    img = robot.camera.latest_image
    if img is None:
        print("  No image available. Camera may need a moment.")
        robot.camera.close_camera_feed()
        return
    filename = _safe_input("  Save filename", "vector_capture.png")
    img.save(filename)
    print(f"  Image saved to {filename}  (size: {img.size})")
    robot.camera.close_camera_feed()


# ---- World ----------------------------------------------------------------

def world_objects(robot):
    """List all known objects in the world."""
    objs = list(robot.world.all_objects)
    if not objs:
        print("  No objects currently known.")
        return
    print(f"  {len(objs)} object(s):")
    for o in objs:
        print(f"    {o}")

def world_visible(robot):
    """List currently visible objects."""
    objs = list(robot.world.visible_objects)
    if not objs:
        print("  No objects currently visible.")
        return
    print(f"  {len(objs)} visible object(s):")
    for o in objs:
        print(f"    {o}")

def world_cube(robot):
    """Show light cube info."""
    cube = robot.world.light_cube
    if cube is None:
        print("  No light cube known.")
    else:
        print(f"  Light cube: {cube}")
    conn = robot.world.connected_light_cube
    print(f"  Connected cube: {conn}")


# ---- Faces ----------------------------------------------------------------

def faces_known(robot):
    """List known/enrolled faces."""
    names = robot.faces.known_face_names
    count = robot.faces.face_count
    print(f"  {count} known face(s):")
    for n in names:
        print(f"    - {n}")


# ---- Composite tests ------------------------------------------------------

def test_full_motion(robot):
    """Full motion test: drive off charger, move, spin, head, lift."""
    print("  === Full Motion Test ===")
    print("  Driving off charger ...")
    robot.behavior.drive_off_charger()
    print("  Drive forward 100mm ...")
    robot.behavior.drive_straight(distance_mm(100), speed_mmps(50))
    print("  Turn 360 degrees ...")
    robot.behavior.turn_in_place(degrees(360))
    print("  Head up ...")
    robot.behavior.set_head_angle(degrees(40))
    time.sleep(0.5)
    print("  Head down ...")
    robot.behavior.set_head_angle(degrees(-10))
    time.sleep(0.5)
    print("  Lift up ...")
    robot.behavior.set_lift_height(1.0)
    time.sleep(0.5)
    print("  Lift down ...")
    robot.behavior.set_lift_height(0.0)
    print("  Drive backward 100mm ...")
    robot.behavior.drive_straight(distance_mm(-100), speed_mmps(50))
    print("  === Motion test complete ===")

def test_personality(robot):
    """Personality test: say text, play animations, change eyes."""
    print("  === Personality Test ===")
    robot.behavior.say_text("Testing my personality!")
    print("  Playing GreetAfterLongTime ...")
    robot.anim.play_animation_trigger('GreetAfterLongTime')
    print("  Setting eyes to purple ...")
    robot.behavior.set_eye_color(hue=0.83, saturation=0.76)
    time.sleep(2)
    print("  Setting eyes to teal ...")
    robot.behavior.set_eye_color(hue=0.42, saturation=1.0)
    time.sleep(2)
    robot.behavior.say_text("How do I look?")
    print("  === Personality test complete ===")

def test_sensor_report(robot):
    """Full sensor & status report."""
    print("  === Sensor & Status Report ===")
    info_battery(robot)
    print()
    info_pose(robot)
    print()
    info_sensors(robot)
    print()
    info_status_flags(robot)
    print()
    sensor_proximity(robot)
    print()
    sensor_touch(robot)
    print("  === Report complete ===")


# ---------------------------------------------------------------------------
# Menu structure
# ---------------------------------------------------------------------------

CATEGORIES = [
    ("Robot Info", [
        ("Battery state", info_battery),
        ("Firmware / version info", info_version),
        ("Current pose", info_pose),
        ("Accelerometer / gyro / wheel speeds", info_sensors),
        ("Status flags", info_status_flags),
    ]),
    ("Speech", [
        ("Say text", speech_say_text),
        ("Say localized text (en/de/fr/ja)", speech_say_localized),
    ]),
    ("Movement / Behavior", [
        ("Drive off charger", move_drive_off_charger),
        ("Drive on charger", move_drive_on_charger),
        ("Drive straight", move_drive_straight),
        ("Turn in place", move_turn_in_place),
        ("Set head angle", move_set_head_angle),
        ("Set lift height", move_set_lift_height),
        ("Look around in place", move_look_around),
        ("Find faces", move_find_faces),
        ("Drive in a square", move_drive_square),
    ]),
    ("Motors (low-level)", [
        ("Wheel motors", motors_wheels),
        ("Head motor", motors_head),
        ("Lift motor", motors_lift),
    ]),
    ("Animations", [
        ("List animation triggers", anim_list_triggers),
        ("List animations", anim_list_animations),
        ("Play animation trigger", anim_play_trigger),
        ("Play animation by name", anim_play_animation),
    ]),
    ("Appearance", [
        ("Set eye color", appearance_eye_color),
    ]),
    ("Audio", [
        ("Set master volume", audio_set_volume),
        ("Play WAV file", audio_play_wav),
    ]),
    ("Screen", [
        ("Display solid color", screen_solid_color),
        ("Display text on face", screen_display_text),
    ]),
    ("Vision", [
        ("Enable/disable face detection", vision_enable_face_detection),
        ("Enable/disable motion detection", vision_enable_motion_detection),
        ("Camera feed on face", vision_camera_on_face),
        ("Vision status", vision_status),
    ]),
    ("Sensors", [
        ("Proximity reading", sensor_proximity),
        ("Touch reading", sensor_touch),
        ("Continuous sensor monitor (Ctrl+C stops)", sensor_continuous),
    ]),
    ("Camera", [
        ("Capture image to file", camera_capture),
    ]),
    ("Photos", [
        ("List stored photos", photos_list),
    ]),
    ("World", [
        ("All known objects", world_objects),
        ("Currently visible objects", world_visible),
        ("Light cube info", world_cube),
    ]),
    ("Face Recognition", [
        ("Known / enrolled faces", faces_known),
    ]),
    ("Composite Tests", [
        ("Full motion test", test_full_motion),
        ("Personality test (speech + animations + eyes)", test_personality),
        ("Full sensor & status report", test_sensor_report),
    ]),
]


# ---------------------------------------------------------------------------
# Menu display & loop
# ---------------------------------------------------------------------------

def build_flat_menu():
    """Build a flat numbered list from the categorized structure."""
    items = []
    for _cat_name, entries in CATEGORIES:
        for label, func in entries:
            items.append((label, func))
    return items


def print_menu():
    """Print the categorized menu."""
    idx = 1
    print()
    print("=" * 64)
    print("  VECTOR SDK INTERACTIVE TEST HARNESS")
    print("=" * 64)
    for cat_name, entries in CATEGORIES:
        print(f"\n  [{cat_name}]")
        for label, _func in entries:
            print(f"    {idx:3d}. {label}")
            idx += 1
    print(f"\n    {'q':>3s}. Quit")
    print()


def main():
    args = anki_vector.util.parse_command_args()
    flat = build_flat_menu()

    print("\nConnecting to Vector ...")
    # NOTE: cache_animation_lists is False to avoid startup timeout under Wire-Pod.
    # Animation lists are loaded lazily when you first access an animation menu item.
    with anki_vector.Robot(args.serial, cache_animation_lists=False) as robot:
        print("Connected!\n")
        while True:
            print_menu()
            choice = input("  Select a test number (or 'q' to quit): ").strip().lower()
            if choice in ('q', 'quit', 'exit'):
                print("  Goodbye!")
                break
            try:
                num = int(choice)
            except ValueError:
                print("  Invalid input. Enter a number or 'q'.")
                continue
            if num < 1 or num > len(flat):
                print(f"  Number out of range. Choose 1-{len(flat)}.")
                continue

            label, func = flat[num - 1]
            print(f"\n  >>> Running: {label}")
            print(f"      ({func.__doc__})")
            print("-" * 50)
            try:
                func(robot)
            except KeyboardInterrupt:
                print("\n  Interrupted.")
            except Exception:
                print("  ERROR:")
                traceback.print_exc()
            print("-" * 50)
            input("  Press Enter to continue...")


if __name__ == "__main__":
    main()
