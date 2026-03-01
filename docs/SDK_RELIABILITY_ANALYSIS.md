# Wire-Pod Vector SDK: Reliability & Integration Analysis

> Source-level investigation of the Wire-Pod Vector Python SDK — covering perception, behavior control, movement, animation, audio, and all major subsystems for reliable MCP/automation integration.

---

## Key Findings

1. **Perception is largely OFF by default.** Face detection (`enable_face_detection`), custom object detection (`enable_custom_object_detection`), nav map feed (`enable_nav_map_feed`), and audio feed (`enable_audio_feed`) are all disabled at `Robot.__init__`. Charger/cube detection is firmware-autonomous but still requires the camera to see the marker. None of the SDK behaviors pre-validate perception state.

2. **Behavior control is fragile and central.** Nearly every action requires behavior control. Control can be lost at any moment to firmware-priority behaviors ("Hey Vector", safety reactions). When control is lost: all active futures are cancelled (returning `None`), vision modes auto-disable, and the SDK must re-request control. The 10 s control-wait timeout does NOT raise — the gRPC call proceeds without control and may silently fail.

3. **Two tiers of response granularity.** Firmware behaviors (`drive_on_charger`, `find_faces`, `look_around_in_place`, `roll_visible_cube`) return `BehaviorResults` — only 3 coarse states (invalid/complete/won't-activate). Cancellable actions (`go_to_pose`, `drive_straight`, `turn_in_place`, `pickup_object`, etc.) return `ActionResult` with 40+ detailed failure codes. Callers must handle both.

4. **Visibility timeout is 0.8 seconds.** Objects and faces flip to `is_visible=False` after 0.8 s without a follow-up observation event. Any check-then-act pattern is a race. `world.visible_objects` and `world.visible_faces` reflect what the robot sees *right now*, not what exists in the room.

5. **Sync `Robot` blocks indefinitely.** All `on_connection_thread`-decorated methods call `future.result()` without a timeout. A stuck firmware behavior will hang the caller forever. Use `AsyncRobot` with explicit timeouts or wrap calls in threads.

6. **Movement actions conflict with each other.** `go_to_pose`, `drive_straight`, `turn_in_place`, `dock_with_cube`, `pickup_object` all use the wheel tracks. Concurrent use returns `TRACKS_LOCKED`. The SDK does not pre-check — firmware rejects the conflicting action.

7. **Audio and screen have strict format requirements.** WAV files must be 8000–16025 Hz, 16-bit, mono — violations raise `VectorExternalAudioPlaybackException`. Screen data must be exactly 35328 bytes (184×96 pixels, RGB565). No concurrent audio streams.

---

## A) Perception Pipeline

### Why `visible_faces` and `visible_objects` Always Return Empty

This is expected SDK behavior given the default configuration, not a bug. There are **four independent root causes** that stack:

### Root Cause 1: Face detection is OFF by default

`Robot.__init__` sets `enable_face_detection=False` (`robot.py` L120). During `Robot.connect()`, the SDK calls:

```python
# robot.py L687-690
if self.conn.requires_behavior_control:
    face_detection = self.vision.enable_face_detection(
        detect_faces=self.enable_face_detection,    # False by default!
        estimate_expression=self.estimate_facial_expression)
```

This sends `EnableFaceDetectionRequest(enable=False)` to the robot — **explicitly telling firmware to NOT produce `RobotObservedFace` events**. Without these events, `World._on_face_observed` (`world.py` L862) never fires, so `_faces` stays `{}`, and `visible_faces` yields nothing.

**Fix:** Construct the Robot with `enable_face_detection=True`:
```python
with anki_vector.Robot(enable_face_detection=True) as robot:
    ...
```

Or enable at runtime:
```python
robot.vision.enable_face_detection(detect_faces=True)
```

### Root Cause 2: No behavior control = no vision mode enablement at all

If MCP connects with `behavior_control_level=None`, the guard at `robot.py` L686 (`if self.conn.requires_behavior_control`) is `False`, so `enable_face_detection` and `enable_custom_object_detection` are **never called**. The robot uses whatever vision modes it had before the SDK connected — which for face events means nothing is sent to the SDK.

**Fix:** Always connect with behavior control, or call `vision.enable_face_detection()` manually after gaining control (`requires_control=False` on that method — it works without behavior control).

### Root Cause 3: Objects only populate from firmware-sent observation events

`visible_objects` iterates `self._objects` (`world.py` L198–204), which is populated **only** when `_on_object_observed` fires. This handler depends on:

1. The `EventStream` gRPC being active and receiving `ObjectEvent` → `RobotObservedObject` messages
2. The robot's camera actually seeing an object marker (charger, cube, or custom)
3. The robot's head being angled so the marker is in the camera FOV

If Vector is staring at the ceiling, or the charger is behind him, or there's no cube nearby — `_objects` stays `{}`. This is correct behavior: the SDK reflects what the robot **currently sees**, not what exists in the room.

### Root Cause 4: The 0.8-second visibility timeout

Even when objects ARE detected, they become invisible after just 0.8 seconds without a follow-up observation event (`objects.py` L61, L347–350):

```python
OBJECT_VISIBILITY_TIMEOUT = 0.8  # objects.py L61

def _observed_timeout(self):
    self._is_visible = False       # objects.py L349
    self._dispatch_disappeared_event()
```

This means:
- Object is seen in frame N → `is_visible = True`
- Robot turns head slightly, object leaves FOV
- 0.8 seconds later → `is_visible = False`
- Your code checks `visible_objects` → empty

**The generators `visible_faces` and `visible_objects` only yield items where `is_visible == True` — i.e., seen within the last 0.8 seconds.**

### Summary: Requirements for non-empty results

| Collection | Requirements |
|---|---|
| `visible_faces` | 1) `enable_face_detection=True` at Robot init or via `vision.enable_face_detection(True)` 2) A face must be in camera FOV right now 3) Face must have been observed within last 0.8 s |
| `visible_objects` | 1) EventStream must be running (it is, after `connect()`) 2) A charger/cube/custom-object marker must be in camera FOV right now 3) Object must have been observed within last 0.8 s 4) For custom objects: `enable_custom_object_detection=True` and object must be defined via `define_custom_*` |
| `world.charger` (non-None) | Charger must have been observed at least once in this session (but may not be visible anymore) |

### How to verify events are flowing (diagnostic)

```python
import anki_vector
from anki_vector.events import Events
from anki_vector.util import degrees
import time

def on_face(robot, event_type, event):
    print(f"FACE EVENT: id={event.face_id}")

def on_object(robot, event_type, event):
    print(f"OBJECT EVENT: type={event.object_type} id={event.object_id}")

with anki_vector.Robot(enable_face_detection=True) as robot:
    robot.behavior.set_head_angle(degrees(0))
    robot.behavior.set_lift_height(0.0)
    robot.events.subscribe(on_face, Events.robot_observed_face)
    robot.events.subscribe(on_object, Events.robot_observed_object)
    print("Watching for events for 30s — point Vector at faces/charger/cube...")
    time.sleep(30)
```

If no events print, the problem is upstream (firmware vision pipeline, not SDK).
If events print but `visible_faces`/`visible_objects` is empty when you check, the 0.8 s timeout has expired.

---

## B) SDK Architecture

### B1. Behavior control system

All SDK actions flow through the `on_connection_thread` decorator (`connection.py` L711–838):

1. `result()` wraps `func` in `log_handler`
2. `log_handler` checks `requires_control=True` (default) → waits on `conn.control_granted_event` with 10 s timeout
3. Calls the gRPC coroutine via `asyncio.run_coroutine_threadsafe`
4. Future is added to `conn.active_commands` (so control-loss cancels it)
5. Cancel behavior depends on `is_cancellable` type:
   - `CANCELLABLE_BEHAVIOR` → `_abort_behavior()` → `CancelBehaviorRequest`
   - `CANCELLABLE_ACTION` → `_abort_action(action_id)` → `CancelActionByIdTagRequest`
6. For sync `Robot`, `.result()` blocks; for `AsyncRobot`, returns `Future`

**Control loss** (`connection.py` L593–603):
- `_cancel_active()` cancels ALL active futures → they return `None`
- `vision_modes_auto_disabled` event fires → all `VisionComponent` flags reset to `False`
- SDK must re-request control to continue

**10 s control timeout** (`connection.py` L760–762):
- `await asyncio.wait([...], timeout=10)` does **NOT raise** on timeout — the gRPC call proceeds without confirmed control. May succeed if firmware allows it, or may silently fail with `WONT_ACTIVATE`.

### B2. Two response types

| Response Type | Used By | Granularity | Codes |
|---|---|---|---|
| `BehaviorResults` | `drive_on_charger`, `drive_off_charger`, `find_faces`, `look_around_in_place`, `roll_visible_cube` | 3 states | `BEHAVIOR_INVALID_STATE(0)`, `BEHAVIOR_COMPLETE_STATE(1)`, `BEHAVIOR_WONT_ACTIVATE_STATE(2)` |
| `ActionResult` | `go_to_pose`, `drive_straight`, `turn_in_place`, `set_head_angle`, `set_lift_height`, `turn_towards_face`, `go_to_object`, `dock_with_cube`, `roll_cube`, `pop_a_wheelie`, `pickup_object`, `place_object_on_ground_here` | 40+ codes | `SUCCESS`, `RUNNING`, `PATH_PLANNING_FAILED_ABORT`, `TRACKS_LOCKED`, `CHARGER_UNPLUGGED_ABORT`, `STILL_ON_CHARGER`, `VISUAL_OBSERVATION_FAILED`, etc. |
| No result (void) | `say_text`, `change_locale`, `update_settings`, `set_eye_color` | Success/exception only | gRPC `ResponseStatus` |

### B3. Event stream

The SDK opens a persistent gRPC `EventStream` (`events.py` L249–250`) and receives server-pushed events. Key events:

| Event | Populated By | Updates |
|---|---|---|
| `robot_state` | Firmware (continuous) | `robot.status`, `robot.pose`, wheel speeds, head/lift angles, accel, gyro |
| `robot_observed_face` | Firmware (when face detection ON) | `world._faces`, face visibility |
| `robot_observed_object` | Firmware (continuous for charger/cube, or when custom detection ON) | `world._objects`, `world._charger`, object visibility |
| `robot_observed_motion` | Firmware (when motion detection ON) | Motion detection events |
| `vision_modes_auto_disabled` | Firmware (on control loss) | Resets all `VisionComponent` flags |
| `nav_map_update` | Firmware (when nav map feed ON) | `nav_map.latest_nav_map` |

**No polling mechanism.** If the EventStream drops events, the SDK has no recovery mechanism.

---

## C) Behavior Categories & Code Paths

### C1. Firmware behaviors (`CANCELLABLE_BEHAVIOR`)

These are fire-and-forget requests to the firmware's behavior system. The SDK sends an empty (or near-empty) request and blocks until the firmware completes the entire behavior autonomously. Response type: `BehaviorResults` (3 coarse states only).

| Method | Request Proto | Notes |
|---|---|---|
| `drive_on_charger()` | `DriveOnChargerRequest()` (empty) | Robot searches for charger, navigates, docks. No SDK pre-validation. |
| `drive_off_charger()` | `DriveOffChargerRequest()` (empty) | Drives forward off charger. |
| `find_faces()` | `FindFacesRequest()` (empty) | Turns in place, moves head to look for faces. |
| `look_around_in_place()` | `LookAroundInPlaceRequest()` (empty) | Scans environment by moving head/body. |
| `roll_visible_cube()` | `RollBlockRequest()` (empty) | Finds and rolls a visible cube. Cube must be in view. |

**Exit conditions for all firmware behaviors:**

| Outcome | Signal | Source |
|---------|--------|--------|
| Success | `BehaviorResults.BEHAVIOR_COMPLETE_STATE (1)` | gRPC response |
| Won't activate | `BehaviorResults.BEHAVIOR_WONT_ACTIVATE_STATE (2)` | gRPC response |
| Invalid | `BehaviorResults.BEHAVIOR_INVALID_STATE (0)` | gRPC response |
| Control lost | Future cancelled → returns `None` | `connection.py` L835 |
| gRPC error | `VectorException` raised | `connection.py` L772 |

**Critical limitation:** The detailed `ActionResult` codes (`PATH_PLANNING_FAILED_ABORT`, `CHARGER_UNPLUGGED_ABORT`, `STILL_ON_CHARGER`, `VISUAL_OBSERVATION_FAILED`, etc. from `messages.proto` L639–700) are **NOT returned** for firmware behaviors. The SDK only gets one of three coarse states.

### C2. Cancellable actions (`CANCELLABLE_ACTION`)

These are specific motor/navigation commands with parameters. Response type varies but generally includes `ActionResult` with detailed status codes. Each action gets a unique `action_id` for cancellation.

| Method | Key Parameters | Request Proto |
|---|---|---|
| `go_to_pose(pose, relative_to_robot, num_retries)` | Target `Pose` | `GoToPoseRequest` |
| `drive_straight(distance, speed, should_play_anim, num_retries)` | `Distance`, `Speed` | `DriveStraightRequest` |
| `turn_in_place(angle, speed, accel, angle_tolerance, is_absolute, num_retries)` | `Angle` (positive=left) | `TurnInPlaceRequest` |
| `set_head_angle(angle, accel, max_speed, duration, num_retries)` | Clamped to −22°..45° | `SetHeadAngleRequest` |
| `set_lift_height(height, accel, max_speed, duration, num_retries)` | 0.0–1.0 → 32mm–92mm | `SetLiftHeightRequest` |
| `turn_towards_face(face, num_retries)` | `Face` object | `TurnTowardsFaceRequest` |
| `go_to_object(target_object, distance_from_object, num_retries)` | `LightCube`, `Distance` | `GoToObjectRequest` |
| `dock_with_cube(target_object, approach_angle, alignment_type, distance_from_marker, num_retries)` | `LightCube` | `DockWithCubeRequest` |
| `roll_cube(target_object, approach_angle, num_retries)` | `LightCube` | `RollObjectRequest` |
| `pop_a_wheelie(target_object, approach_angle, num_retries)` | `LightCube` | `PopAWheelieRequest` |
| `pickup_object(target_object, use_pre_dock_pose, num_retries)` | `LightCube` | `PickupObjectRequest` |
| `place_object_on_ground_here(num_retries)` | — | `PlaceObjectOnGroundHereRequest` |

**All cancellable actions support `future.cancel()` → `_abort_action(action_id)` → `CancelActionByIdTagRequest`.**

### C3. Non-cancellable commands (no cancel type)

| Method | Requires Control | Notes |
|---|---|---|
| `say_text(text, use_vector_voice, duration_scalar)` | Yes | Blocks until speech finishes |
| `say_localized_text(text, ..., language)` | Yes | Switches locale → speaks → switches back. **Blocks even on AsyncRobot** to ensure locale restore. |
| `change_locale(locale)` | Yes | e.g. `'de_DE'`, `'fr_FR'` |
| `update_settings(settings)` | Yes | Keys: `clock_24_hour`, `eye_color`, `locale`, `master_volume`, `temp_is_fahrenheit`, `time_zone` |
| `set_eye_color(hue, saturation)` | Yes | Hue/Sat both 0.0–1.0 |
| `app_intent(intent, param)` | **No** (`requires_control=False`) | For `intent_clock_settimer`, `param` is seconds as `int` |

### C4. No-control-required queries

These work even with `behavior_control_level=None`:

| Method | Component | Returns |
|---|---|---|
| `get_battery_state()` | `robot` | `BatteryStateResponse` — volts, level(1-3), charging, cube battery |
| `get_version_state()` | `robot` | `VersionStateResponse` — `os_version`, `engine_build_id` |
| `request_enrolled_names()` | `robot.faces` | `RequestEnrolledNamesResponse` — all named faces |
| `update_enrolled_face_by_id(...)` | `robot.faces` | Updates a face name on robot |
| `erase_enrolled_face_by_id(...)` | `robot.faces` | Erases a face record |
| `erase_all_enrolled_faces()` | `robot.faces` | **Destructive** — erases all face records |
| `load_animation_list()` | `robot.anim` | Fetches available animation names |
| `load_animation_trigger_list()` | `robot.anim` | Fetches available trigger names |
| `set_master_volume(volume)` | `robot.audio` | `RobotVolumeLevel` enum (LOW=0 through HIGH=4) |
| `enable_face_detection(...)` | `robot.vision` | Can be called without control |

### C5. Motor commands (direct wheel/head/lift control)

| Method | Component | Parameters |
|---|---|---|
| `set_wheel_motors(left_speed, right_speed, left_accel, right_accel)` | `robot.motors` | Speeds in mm/s. `(0,0)` stops and unlocks. |
| `set_head_motor(speed)` | `robot.motors` | rad/s. Positive=up. `0` stops. |
| `set_lift_motor(speed)` | `robot.motors` | rad/s. Positive=up. `0` stops. |
| `stop_all_motors()` | `robot.motors` | Stops wheels, head, lift |

**These are continuous commands** — they keep running until a new command or `(0)` is sent. They conflict with `CANCELLABLE_ACTION` behaviors that use the same tracks.

### C6. Animation system

| Method | Key Parameters | Notes |
|---|---|---|
| `play_animation(anim, loop_count, ignore_*_track)` | Animation name (from `anim_list`) | Validates name exists. **Must be off charger.** Specific anims may be removed across firmware versions. |
| `play_animation_trigger(anim_trigger, loop_count, use_lift_safe, ignore_*_track)` | Trigger name (from `anim_trigger_list`) | Preferred over `play_animation`. **Must be off charger.** |

### C7. Audio streaming

| Method | Key Parameters | Notes |
|---|---|---|
| `stream_wav_file(filename, volume)` | Path to WAV, volume 0–100 | **8000–16025 Hz, 16-bit, mono only.** No concurrent streams. Raises `VectorExternalAudioPlaybackException` on format/overrun errors. |

### C8. Screen display

| Method | Key Parameters | Notes |
|---|---|---|
| `set_screen_with_image_data(data, duration_sec, interrupt_running)` | 35328 bytes (184×96 RGB565) | Exact byte count required. |
| `set_screen_to_color(color, duration_sec, interrupt_running)` | `Color` object | Convenience wrapper. |

### C9. World charger population pipeline

| Step | File + Symbol | Line |
|------|--------------|------|
| **Event source** | gRPC `EventStream` → `Event.object_event.robot_observed_object` | `shared.proto` L57 |
| **Stream handler** | `EventHandler._handle_event_stream` | `events.py` L247 |
| **Event unpackaging** | `EventHandler._unpackage_event` — auto-unpacks `object_event` → `object_event_type` sub-oneof | `events.py` L233 |
| **Dispatch** | `dispatch_event_by_name(data, "robot_observed_object")` | `events.py` L256 |
| **World handler** | `World._on_object_observed` | `world.py` L879 |
| **Charger allocation** | If `msg.object_type == CHARGER_BASIC` and new ID → `World._allocate_charger` | `world.py` L837, L890–892 |
| **Charger instance** | `Charger.__init__` subscribes to `robot_observed_object` for pose updates | `objects.py` L1098–1101 |
| **Visibility tracking** | `Charger._on_object_observed` → `ObservableObject._on_observed` → sets `_is_visible=True`, resets timeout | `objects.py` L1161, L355–370 |
| **Disappearance** | `_observed_timeout` fires after 0.8 s → `_is_visible=False` + `EvtObjectDisappeared` | `objects.py` L347–350 |

### C10. Face detection pipeline

| Step | File + Symbol | Line |
|------|--------------|------|
| **Enable** | `VisionComponent.enable_face_detection` → `EnableFaceDetectionRequest` gRPC | `vision.py` L107 |
| **Auto-enable at connect** | `Robot.connect` — only if `conn.requires_behavior_control` | `robot.py` L687–690 |
| **Event source** | `Event.robot_observed_face` (from EventStream) | `shared.proto` L54 |
| **World handler** | `World._on_face_observed` — creates `Face` if new `face_id` | `world.py` L862 |
| **Face self-update** | `Face._on_face_observed` → `_on_observed()` updates visibility | `faces.py` L710 |
| **Visibility** | Same `OBJECT_VISIBILITY_TIMEOUT (0.8 s)` mechanism | `faces.py` L224 |
| **Auto-disable** | `vision_modes_auto_disabled` event → `VisionComponent._handle_vision_modes_auto_disabled_event` resets all flags to `False` | `vision.py` L63–67 |

---

## D) Preconditions Matrix

### D1. Universal preconditions (all behavior-control-required actions)

| Precondition | Check | Source |
|---|---|---|
| **Behavior control granted** | `robot.conn.control_events.has_control` | `connection.py` L760 — waits 10 s, then proceeds anyway |
| **Not picked up** | `robot.status.is_picked_up` | `status.py` L138 — robot can't path-plan while held |
| **Not being held** | `robot.status.is_being_held` | `status.py` L305 |
| **Not falling** | `robot.status.is_falling` | `status.py` L161 |
| **No cliff detected** | `robot.status.is_cliff_detected` | `status.py` L271 |
| **Connection alive** | gRPC channel open | gRPC errors wrapped as `VectorException` |

### D2. Movement-specific preconditions

| Precondition | Applies To | Check |
|---|---|---|
| **Off charger** | `drive_straight`, `turn_in_place`, `go_to_pose`, all animations, cube interactions | `robot.status.is_on_charger` — firmware may reject or produce unexpected results |
| **Tracks not locked** | All wheel-using actions | `robot.status.are_motors_moving`, `robot.status.is_pathing` — concurrent movement returns `TRACKS_LOCKED` |
| **Target object visible** | `go_to_object`, `dock_with_cube`, `roll_cube`, `pickup_object`, `pop_a_wheelie`, `turn_towards_face` | `target.is_visible` — must be observed within last 0.8 s |

### D3. Charger-specific preconditions

| Precondition | Confidence | Evidence |
|---|---|---|
| **Not already on charger** | Strongly recommended | Returns `BEHAVIOR_WONT_ACTIVATE_STATE`. Check `robot.status.is_on_charger`. |
| **Charger present and powered** | Required (not SDK-checkable) | `CHARGER_UNPLUGGED_ABORT` code exists but isn't returned via `BehaviorResults`. |
| **Charger in visual range** | Strongly recommended | `drive_on_charger` includes firmware-side search, but times out if charger can't be found. Check `world.charger is not None and world.charger.is_visible` as heuristic. |
| **Not carrying object** | Optional | `STILL_CARRYING_OBJECT` code exists. Check `robot.carrying_object_id`. |

### D4. Audio/screen preconditions

| Precondition | Applies To | Check |
|---|---|---|
| **WAV format: 8000–16025 Hz, 16-bit, mono** | `stream_wav_file` | Validated by robot firmware — raises `VectorExternalAudioPlaybackException` |
| **No concurrent audio stream** | `stream_wav_file` | Second stream raises overrun error |
| **Exact 35328 bytes** | `set_screen_with_image_data` | 184×96 pixels × 2 bytes (RGB565) |

### D5. Perception preconditions

| Precondition | Applies To | Check |
|---|---|---|
| **Face detection enabled** | `visible_faces`, `find_faces`, `turn_towards_face` | `robot.vision.detect_faces` — must be `True` |
| **Custom object detection enabled** | Custom marker detection | `robot.vision.detect_custom_objects` — charger/cube don't need this |
| **Nav map feed initialized** | `nav_map.latest_nav_map` | `enable_nav_map_feed=True` at Robot init, or call `init_nav_map_feed()` |
| **Head angle suitable for camera FOV** | All perception-dependent actions | `set_head_angle(degrees(0))` for best forward visibility |

---

## E) Failure Taxonomy

### E1. Control lost during execution

| Attribute | Detail |
|---|---|
| **Trigger** | A higher-priority behavior ("Hey Vector", safety reaction, physical pickup) takes control from SDK |
| **Symptom** | Any in-flight SDK action returns `None` |
| **Signal** | `future.cancelled()` → warning log `"{func_name} cancelled because behavior control was lost"` |
| **Side effect** | Vision modes auto-disabled (`vision_modes_auto_disabled` event). All `VisionComponent` flags reset to `False`. |
| **Applies to** | ALL `requires_control=True` actions |
| **Source** | `connection.py` L593–603 (`_cancel_active`), L835 (returns `None`) |

### E2. `BEHAVIOR_WONT_ACTIVATE_STATE`

| Attribute | Detail |
|---|---|
| **Trigger** | Firmware determines behavior cannot start (conflicting state, already executing, etc.) |
| **Symptom** | Firmware-behavior methods return immediately with `result == 2` |
| **Applies to** | `drive_on_charger`, `drive_off_charger`, `find_faces`, `look_around_in_place`, `roll_visible_cube` |
| **Source** | `messages.proto` L501–503 |

### E3. `BEHAVIOR_INVALID_STATE`

| Attribute | Detail |
|---|---|
| **Trigger** | Internal firmware error or invalid state transition |
| **Symptom** | Firmware-behavior methods return with `result == 0` |
| **Applies to** | Same firmware behaviors as E2 |

### E4. `TRACKS_LOCKED`

| Attribute | Detail |
|---|---|
| **Trigger** | Another action is already using the wheel motors |
| **Symptom** | Action returns failure in `ActionResult` |
| **Applies to** | `go_to_pose`, `drive_straight`, `turn_in_place`, `dock_with_cube`, `pickup_object`, `go_to_object`, and all other track-using actions |
| **Source** | `messages.proto` L705 |

### E5. gRPC transport error

| Attribute | Detail |
|---|---|
| **Trigger** | Network disconnection, robot powered off, connection timeout |
| **Symptom** | `VectorException` raised |
| **Applies to** | ALL SDK methods |
| **Source** | `connection.py` L772 — wraps `grpc.RpcError` |

### E6. Control timeout (10 s wait expires)

| Attribute | Detail |
|---|---|
| **Trigger** | Robot is running a mandatory reaction and won't grant control within 10 s |
| **Symptom** | gRPC call proceeds without confirmed control — may succeed or fail silently |
| **Signal** | No exception raised. `asyncio.wait(timeout=10)` returns without checking if control was granted. |
| **Applies to** | ALL `requires_control=True` actions |
| **Source** | `connection.py` L760–762 |

### E7. Object/target not found

| Attribute | Detail |
|---|---|
| **Trigger** | Target object not visible or never observed |
| **Symptom** | `world.charger is None`, `world.visible_objects` empty, `face.is_visible == False` |
| **Applies to** | `drive_on_charger` (charger not found), `go_to_object`/`dock_with_cube`/`pickup_object` (cube not visible), `turn_towards_face` (face not visible), `roll_visible_cube` (no cube in view) |
| **Details** | Firmware behaviors time out internally; cancellable actions may return `VISUAL_OBSERVATION_FAILED` or similar `ActionResult` codes |

### E8. Audio format rejection

| Attribute | Detail |
|---|---|
| **Trigger** | WAV file is not 8000–16025 Hz, 16-bit, mono |
| **Symptom** | `VectorExternalAudioPlaybackException` raised |
| **Applies to** | `stream_wav_file` only |

### E9. Screen data size mismatch

| Attribute | Detail |
|---|---|
| **Trigger** | Image data is not exactly 35328 bytes |
| **Symptom** | gRPC error or corrupted display |
| **Applies to** | `set_screen_with_image_data` |

### E10. Animation not found

| Attribute | Detail |
|---|---|
| **Trigger** | Animation/trigger name not in `anim_list`/`anim_trigger_list` |
| **Symptom** | Validation error before gRPC call |
| **Applies to** | `play_animation`, `play_animation_trigger` |
| **Note** | Specific animation names may be removed across firmware versions; use triggers (stable) over raw animation names (volatile). |

### E11. Duplicate charger allocation

| Attribute | Detail |
|---|---|
| **Trigger** | Second `CHARGER_BASIC` observation with different `object_id` |
| **Symptom** | Warning logged, second charger **ignored** |
| **Signal** | Log: "Allocating multiple chargers" — `world.charger` stays as first one |
| **Source** | `world.py` L839–843 |

---

## F) Detection Pipeline Details

### F1. What updates `world.visible_objects` / `world.charger` / `world.visible_faces`?

**Objects (charger, cube, custom objects):**

```
EventStream (gRPC)
  → Event.object_event.robot_observed_object (RobotObservedObject proto)
  → EventHandler._handle_event_stream()                    [events.py L247]
  → _unpackage_event('event_type')
    → _unpackage_event('object_event_type')                [events.py L233–244]
  → dispatch_event_by_name("robot_observed_object", msg)
  → World._on_object_observed()                            [world.py L879]
    ├─ CHARGER_BASIC  → _allocate_charger()                [world.py L837]
    ├─ BLOCK_LIGHTCUBE1 → binds existing LightCube         [world.py L883–886]
    └─ CUSTOM_TYPE_*  → _allocate_custom_marker_object()   [world.py L896]
  → Each object subscribes to future robot_observed_object events internally
  → On each observation: _on_observed()                    [objects.py L354]
    → sets _is_visible=True, updates pose, resets 0.8 s timeout
  → After 0.8 s with no observation: _observed_timeout()
    → _is_visible=False                                    [objects.py L347]
```

**Faces:**

```
EventStream
  → Event.robot_observed_face (RobotObservedFace proto)
  → dispatch_event_by_name("robot_observed_face", msg)
  → World._on_face_observed()                              [world.py L862]
    → creates Face instance if new face_id
  → Face._on_face_observed()                               [faces.py L710]
    → _on_observed() → same visibility logic
```

### F2. Polling/event timing expectations

- **Event-driven, not polled.** The SDK opens a persistent gRPC `EventStream` (`events.py` L249–250) and receives server-pushed events.
- **Object observations are continuous** while the object is in camera view. Each frame (or subset of frames) where the robot's vision system recognizes a marker generates a `RobotObservedObject` event.
- **Visibility timeout is 0.8 seconds** (`objects.py` L61). This is hardcoded and very short.
- **There is no periodic polling mechanism** in the SDK. If the EventStream drops events (network lag, processing delay), the SDK has no recovery mechanism to re-query object positions.

### F3. Why collections can remain empty even when humans see targets

| Reason | Explanation | Evidence |
|--------|-------------|----------|
| **Robot camera ≠ human eyes** | Vector's camera has limited FOV, resolution, and marker recognition distance. The charger marker must be visible, well-lit, and within recognition range. | Firmware behavior, not SDK code |
| **Head angle matters** | If Vector's head is angled too high or too low, the charger marker may not be in the camera frame. | No SDK-level auto-adjustment before `drive_on_charger` |
| **Face detection OFF by default** | `enable_face_detection=False` in `Robot.__init__` (`robot.py` L120). No face events are generated unless explicitly enabled. | Source code |
| **Custom object detection OFF by default** | `enable_custom_object_detection=False` (`robot.py` L122). This controls `EnableMarkerDetection` which is for **custom** markers, NOT charger/cube. | `vision.py` L101–106 |
| **Charger detection is firmware-autonomous** | The charger uses a built-in marker (`CHARGER_BASIC` type = 6). Detection happens in the robot firmware's vision pipeline regardless of `EnableMarkerDetection`. Events only flow if the EventStream is active and the robot is looking at the charger. | `cube.proto` L125 |
| **Event stream not started yet** | World subscriptions happen in `Robot.connect()` (`robot.py` L666), but the EventStream starts in `events.start()` (`events.py` L128). If queried too early, no events have arrived. | Source code |
| **Vision modes auto-disabled** | When SDK loses behavior control, `vision_modes_auto_disabled` event fires, resetting all `VisionComponent` flags (`vision.py` L63–67). Face detection stops. **Charger/cube detection is unaffected** (firmware-controlled). | Source code |
| **First observation only creates object** | `World._on_object_observed` uses `if msg.object_id not in self._objects` — the object is allocated only on first observation. If the first event is missed or dropped, the object won't exist. | `world.py` L879–896 |

### F4. Key distinction: Charger detection vs. custom object detection

**Confirmed from code:** `enable_custom_object_detection` controls `EnableMarkerDetectionRequest` (`vision.py` L101–106), which is documented as affecting `RobotObservedObject` for **custom markers only** (`messages.proto` L1114: "When enabled, RobotObservedObject messages will be produced"). The charger has type `CHARGER_BASIC` (not a custom type) and is detected by firmware.

**Hypothesis (inferred):** Charger and cube detection are always-on in firmware and do not require `EnableMarkerDetection`. The custom object detection flag is separate.

---

## G) MCP Guardrail Recommendations

### G1. Universal pre-check (all actions requiring behavior control)

```python
def pre_check_action(robot) -> tuple[bool, str]:
    """Returns (can_proceed, reason_if_not). Check before any behavior-control action."""

    if not robot.conn.control_events.has_control:
        return False, "SDK does not have behavior control"

    if robot.status.is_picked_up:
        return False, "Robot is picked up"

    if robot.status.is_being_held:
        return False, "Robot is being held"

    if robot.status.is_falling:
        return False, "Robot is falling"

    if robot.status.is_cliff_detected:
        return False, "Cliff detected — robot may not navigate safely"

    return True, ""
```

### G2. Movement pre-check (actions using wheels/tracks)

```python
def pre_check_movement(robot) -> tuple[bool, str]:
    """Additional checks for drive/turn/go_to/dock/pickup actions."""

    ok, reason = pre_check_action(robot)
    if not ok:
        return False, reason

    if robot.status.is_on_charger:
        return False, "Robot is on charger — must drive off first"

    if robot.status.is_pathing:
        return False, "Robot is already pathing — TRACKS_LOCKED risk"

    return True, ""
```

### G3. Charger docking pre-check

```python
def pre_check_drive_on_charger(robot) -> tuple[bool, str]:
    """Checks specific to drive_on_charger."""

    ok, reason = pre_check_action(robot)
    if not ok:
        return False, reason

    if robot.status.is_on_charger:
        return False, "Robot is already on charger"

    return True, ""
```

**Pre-dock scan procedure:**

1. `robot.behavior.set_head_angle(degrees(0))` — best charger marker visibility
2. `robot.behavior.set_lift_height(0.0)` — avoid marker occlusion
3. `robot.behavior.look_around_in_place()` — firmware scans environment
4. Check `robot.world.charger is not None and robot.world.charger.is_visible`
5. If not found, retry with `turn_in_place()` between attempts (up to 2 retries)

### G4. Object interaction pre-check

```python
def pre_check_object_action(robot, target_object) -> tuple[bool, str]:
    """Checks for go_to_object, dock_with_cube, pickup_object, roll_cube, pop_a_wheelie."""

    ok, reason = pre_check_movement(robot)
    if not ok:
        return False, reason

    if target_object is None:
        return False, "Target object is None — never observed"

    if not target_object.is_visible:
        return False, "Target object not currently visible (last seen > 0.8 s ago)"

    return True, ""
```

### G5. Face interaction pre-check

```python
def pre_check_face_action(robot, face=None) -> tuple[bool, str]:
    """Checks for turn_towards_face, find_faces."""

    ok, reason = pre_check_action(robot)
    if not ok:
        return False, reason

    if not robot.vision.detect_faces:
        return False, "Face detection is not enabled — call vision.enable_face_detection(True)"

    if face is not None and not face.is_visible:
        return False, "Target face not currently visible"

    return True, ""
```

### G6. Audio pre-check

```python
import wave

def pre_check_audio(filename: str) -> tuple[bool, str]:
    """Validate WAV file before streaming."""
    try:
        with wave.open(filename, 'rb') as wf:
            if wf.getnchannels() != 1:
                return False, f"WAV must be mono, got {wf.getnchannels()} channels"
            if wf.getsampwidth() != 2:
                return False, f"WAV must be 16-bit, got {wf.getsampwidth()*8}-bit"
            rate = wf.getframerate()
            if rate < 8000 or rate > 16025:
                return False, f"WAV sample rate must be 8000-16025 Hz, got {rate}"
    except Exception as e:
        return False, f"Cannot read WAV file: {e}"
    return True, ""
```

### G7. Response handling patterns

**For firmware behaviors** (`drive_on_charger`, `drive_off_charger`, `find_faces`, `look_around_in_place`, `roll_visible_cube`):

```python
response = robot.behavior.some_firmware_behavior()

if response is None:
    error = "Interrupted — behavior control was lost. Retry after re-acquiring control."
elif response.result == 2:  # BEHAVIOR_WONT_ACTIVATE_STATE
    error = "Robot refused to start behavior — conflicting state or already in target state."
elif response.result == 0:  # BEHAVIOR_INVALID_STATE
    error = "Behavior failed with invalid state — internal firmware error."
else:
    # Success — verify expected outcome
    pass
```

**For cancellable actions** (`go_to_pose`, `drive_straight`, `turn_in_place`, etc.):

```python
response = robot.behavior.some_cancellable_action()

if response is None:
    error = "Interrupted — behavior control was lost."
elif hasattr(response, 'result'):
    # ActionResult provides detailed failure codes
    result_code = response.result.code  # e.g. PATH_PLANNING_FAILED_ABORT, TRACKS_LOCKED
    if result_code != ActionResult.ACTION_RESULT_SUCCESS:
        error = f"Action failed: {result_code}"
```

### G8. Timeout policy by behavior category

| Category | Timeout | Rationale |
|----------|---------|-----------|
| **Firmware behaviors** (`drive_on_charger`, `look_around_in_place`, etc.) | 30–45 s | Autonomous searching + navigation |
| **Navigation actions** (`go_to_pose`, `go_to_object`, `dock_with_cube`) | 20–30 s | Path planning + traversal |
| **Simple motion** (`drive_straight`, `turn_in_place`, `set_head_angle`, `set_lift_height`) | 5–10 s | Direct motor control |
| **Speech** (`say_text`) | 10–20 s | Depends on text length + `duration_scalar` |
| **Animation** (`play_animation`, `play_animation_trigger`) | 10–30 s | Depends on animation |
| **Cube interactions** (`pickup_object`, `roll_cube`, `pop_a_wheelie`) | 20–30 s | Approach + manipulation |
| **Audio streaming** (`stream_wav_file`) | File duration + 5 s | Streams in real-time |
| **Queries** (`get_battery_state`, `get_version_state`, etc.) | 5 s | Simple gRPC round-trip |

**Important:** The sync `Robot` blocks indefinitely on ALL actions — it calls `future.result()` without a timeout (`connection.py` L833). Use `AsyncRobot` with explicit timeouts, or wrap calls in threads.

### G9. Error messaging by failure type

| Failure | Improved message |
|---|---|
| Returns `None` (any action) | "Vector's autonomous behavior was interrupted. A higher-priority action (e.g., 'Hey Vector', safety reaction, or being picked up) took control. The action can be retried after the interruption resolves." |
| `BEHAVIOR_WONT_ACTIVATE_STATE` | "Vector refused to start this behavior. Likely causes: already in target state, tracks locked by another action, or conflicting robot state. Status: `is_on_charger={}, is_pathing={}, are_motors_moving={}`" |
| `TRACKS_LOCKED` | "Vector's wheels are already in use by another action. Wait for the current movement to finish, or cancel it first." |
| Target `is None` | "Vector has not detected the target object in the current session. The object must be within camera view. Try `look_around_in_place()` to scan the environment." |
| Target `not is_visible` | "Vector detected this object earlier but it's no longer in camera view (visibility expires after 0.8 s). Point Vector at the target and try again." |
| Audio format error | "WAV file format is incompatible. Required: 8000–16025 Hz, 16-bit, mono. Convert with: `ffmpeg -i input.wav -ar 16000 -ac 1 -sample_fmt s16 output.wav`" |
| gRPC error | "Connection to Vector lost. Check that the robot is powered on and on the same network." |
| Timeout | "Action timed out after N seconds. Vector could not complete the task — the target may be out of reach, obstructed, or the robot may be stuck." |

### G10. Robot constructor recommendations for MCP

```python
# Recommended MCP configuration — enable all perception needed for reliable operation
robot = anki_vector.AsyncRobot(
    enable_face_detection=True,         # Required for face-related actions
    enable_custom_object_detection=True, # If using custom markers
    enable_nav_map_feed=True,           # If using navigation map
    cache_animation_lists=True,         # Avoid re-fetching anim lists
    behavior_control_level=ControlPriorityLevel.DEFAULT_PRIORITY,
)
```
