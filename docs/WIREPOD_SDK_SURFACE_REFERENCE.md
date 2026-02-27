# Wire-Pod SDK Surface Reference (Comprehensive)

Purpose: canonical reference of **available SDK surface area** in `wirepod_vector_sdk` (`anki_vector` namespace), generated from source so we can reason about MCP exposure without repeatedly re-parsing upstream docs/code.

_Generated: 2026-02-27T08:11:10_

## Scope and method
- Source analyzed: local clone `wirepod-vector-python-sdk/anki_vector/*.py`
- Extraction method: Python AST parse of public module-level functions, classes, and public class methods
- This document enumerates **what exists** in the SDK surface; it does **not** imply recommended MCP exposure.

## High-value component index (for MCP planning)
### `behavior.BehaviorComponent` (23 methods)
```
app_intent, change_locale, dock_with_cube, drive_off_charger, drive_on_charger, drive_straight, find_faces, go_to_object, go_to_pose, look_around_in_place, pickup_object, place_object_on_ground_here, pop_a_wheelie, roll_cube, roll_visible_cube, say_localized_text, say_text, set_eye_color, set_head_angle, set_lift_height, turn_in_place, turn_towards_face, update_settings
```

### `robot.Robot` (37 methods)
```
accel, anim, audio, behavior, camera, carrying_object_id, conn, connect, disconnect, enable_audio_feed, events, faces, force_async, get_battery_state, get_version_state, gyro, head_angle_rad, head_tracking_object_id, last_image_time_stamp, left_wheel_speed_mmps, lift_height_mm, localized_to_object_id, motors, nav_map, photos, pose, pose_angle_rad, pose_pitch_rad, proximity, right_wheel_speed_mmps, screen, status, touch, viewer, viewer_3d, vision, world
```

### `world.World` (21 methods)
```
all_objects, charger, close, connect_cube, connected_light_cube, create_custom_fixed_object, custom_object_archetypes, define_custom_box, define_custom_cube, define_custom_wall, delete_custom_objects, disconnect_cube, flash_cube_lights, forget_preferred_cube, get_face, get_object, light_cube, set_preferred_cube, visible_custom_objects, visible_faces, visible_objects
```

### `camera.CameraComponent` (16 methods)
```
capture_single_image, close_camera_feed, config, enable_auto_exposure, exposure_ms, gain, get_camera_config, image_annotator, image_streaming_enabled, init_camera_feed, is_auto_exposure_enabled, latest_image, latest_image_id, set_config, set_manual_exposure, update_state
```

### `animation.AnimationComponent` (6 methods)
```
anim_list, anim_trigger_list, load_animation_list, load_animation_trigger_list, play_animation, play_animation_trigger
```

### `vision.VisionComponent` (10 methods)
```
close, detect_custom_objects, detect_faces, detect_motion, disable_all_vision_modes, display_camera_feed_on_face, enable_custom_object_detection, enable_display_camera_feed_on_face, enable_face_detection, enable_motion_detection
```

### `audio.AudioComponent` (2 methods)
```
set_master_volume, stream_wav_file
```

### `motors.MotorComponent` (4 methods)
```
set_head_motor, set_lift_motor, set_wheel_motors, stop_all_motors
```

### `screen.ScreenComponent` (2 methods)
```
set_screen_to_color, set_screen_with_image_data
```

### `objects.LightCube` (19 methods)
```
descriptive_name, factory_id, is_connected, is_moving, last_moved_robot_timestamp, last_moved_start_robot_timestamp, last_moved_start_time, last_moved_time, last_tapped_robot_timestamp, last_tapped_time, last_up_axis_changed_robot_timestamp, last_up_axis_changed_time, object_id, set_light_corners, set_lights, set_lights_off, teardown, top_face_orientation_rad, up_axis
```

### `faces.FaceComponent` (4 methods)
```
erase_all_enrolled_faces, erase_enrolled_face_by_id, request_enrolled_names, update_enrolled_face_by_id
```

### `photos.PhotographComponent` (4 methods)
```
get_photo, get_thumbnail, load_photo_info, photo_info
```

### `touch.TouchComponent` (2 methods)
```
close, last_sensor_reading
```

### `proximity.ProximityComponent` (2 methods)
```
close, last_sensor_reading
```

## Full module inventory
### `anki_vector.animation`
- Module functions: none
- Classes (1):
  - `AnimationComponent` (6 methods)
    - `anim_list`, `anim_trigger_list`, `load_animation_list`, `load_animation_trigger_list`, `play_animation`, `play_animation_trigger`

### `anki_vector.annotate`
- Module functions (3): `add_img_box_to_image`, `add_polygon_to_image`, `annotator`
- Classes (7):
  - `AnnotationPosition` (0 methods)
  - `ImageText` (1 methods)
    - `render`
  - `Annotator` (1 methods)
    - `apply`
  - `ObjectAnnotator` (1 methods)
    - `apply`
  - `FaceAnnotator` (1 methods)
    - `apply`
  - `TextAnnotator` (1 methods)
    - `apply`
  - `ImageAnnotator` (7 methods)
    - `add_annotator`, `add_static_text`, `annotate_image`, `disable_annotator`, `enable_annotator`, `get_annotator`, `remove_annotator`

### `anki_vector.audio`
- Module functions: none
- Classes (2):
  - `RobotVolumeLevel` (0 methods)
  - `AudioComponent` (2 methods)
    - `set_master_volume`, `stream_wav_file`

### `anki_vector.behavior`
- Module functions: none
- Classes (2):
  - `BehaviorComponent` (23 methods)
    - `app_intent`, `change_locale`, `dock_with_cube`, `drive_off_charger`, `drive_on_charger`, `drive_straight`, `find_faces`, `go_to_object`, `go_to_pose`, `look_around_in_place`, `pickup_object`, `place_object_on_ground_here`, `pop_a_wheelie`, `roll_cube`, `roll_visible_cube`, `say_localized_text`, `say_text`, `set_eye_color`, `set_head_angle`, `set_lift_height`, `turn_in_place`, `turn_towards_face`, `update_settings`
  - `ReserveBehaviorControl` (0 methods)

### `anki_vector.camera`
- Module functions: none
- Classes (5):
  - `CameraImage` (4 methods)
    - `annotate_image`, `image_id`, `image_recv_time`, `raw_image`
  - `CameraConfig` (9 methods)
    - `center`, `create_from_message`, `focal_length`, `fov_x`, `fov_y`, `max_exposure_time_ms`, `max_gain`, `min_exposure_time_ms`, `min_gain`
  - `CameraComponent` (16 methods)
    - `capture_single_image`, `close_camera_feed`, `config`, `enable_auto_exposure`, `exposure_ms`, `gain`, `get_camera_config`, `image_annotator`, `image_streaming_enabled`, `init_camera_feed`, `is_auto_exposure_enabled`, `latest_image`, `latest_image_id`, `set_config`, `set_manual_exposure`, `update_state`
  - `EvtNewRawCameraImage` (0 methods)
  - `EvtNewCameraImage` (0 methods)

### `anki_vector.color`
- Module functions: none
- Classes (1):
  - `Color` (2 methods)
    - `int_color`, `rgb565_bytepair`

### `anki_vector.connection`
- Module functions (1): `on_connection_thread`
- Classes (3):
  - `CancelType` (0 methods)
  - `ControlPriorityLevel` (0 methods)
  - `Connection` (13 methods)
    - `behavior_control_level`, `close`, `connect`, `control_granted_event`, `control_lost_event`, `grpc_interface`, `loop`, `release_control`, `request_control`, `requires_behavior_control`, `run_coroutine`, `run_soon`, `thread`

### `anki_vector.events`
- Module functions: none
- Classes (2):
  - `Events` (0 methods)
  - `EventHandler` (8 methods)
    - `close`, `dispatch_event`, `dispatch_event_by_name`, `start`, `subscribe`, `subscribe_by_name`, `unsubscribe`, `unsubscribe_by_name`

### `anki_vector.exceptions`
- Module functions (1): `connection_error`
- Classes (19):
  - `VectorException` (0 methods)
  - `VectorInvalidVersionException` (0 methods)
  - `VectorControlException` (0 methods)
  - `VectorConnectionException` (2 methods)
    - `details`, `status`
  - `VectorUnauthenticatedException` (0 methods)
  - `VectorUnavailableException` (0 methods)
  - `VectorUnimplementedException` (0 methods)
  - `VectorTimeoutException` (0 methods)
  - `VectorAsyncException` (0 methods)
  - `VectorBehaviorControlException` (0 methods)
  - `VectorCameraFeedException` (0 methods)
  - `VectorCameraImageCaptureException` (0 methods)
  - `VectorConfigurationException` (0 methods)
  - `VectorControlTimeoutException` (0 methods)
  - `VectorNotFoundException` (0 methods)
  - `VectorNotReadyException` (0 methods)
  - `VectorPropertyValueNotReadyException` (0 methods)
  - `VectorUnreliableEventStreamException` (0 methods)
  - `VectorExternalAudioPlaybackException` (0 methods)

### `anki_vector.faces`
- Module functions: none
- Classes (6):
  - `EvtFaceObserved` (0 methods)
  - `EvtFaceAppeared` (0 methods)
  - `EvtFaceDisappeared` (0 methods)
  - `Expression` (0 methods)
  - `Face` (12 methods)
    - `expression`, `expression_score`, `face_id`, `has_updated_face_id`, `left_eye`, `mouth`, `name`, `name_face`, `nose`, `right_eye`, `teardown`, `updated_face_id`
  - `FaceComponent` (4 methods)
    - `erase_all_enrolled_faces`, `erase_enrolled_face_by_id`, `request_enrolled_names`, `update_enrolled_face_by_id`

### `anki_vector.lights`
- Module functions (1): `package_request_params`
- Classes (2):
  - `ColorProfile` (4 methods)
    - `augment_color`, `blue_multiplier`, `green_multiplier`, `red_multiplier`
  - `Light` (6 methods)
    - `off_color`, `off_period_ms`, `on_color`, `on_period_ms`, `transition_off_period_ms`, `transition_on_period_ms`

### `anki_vector.mdns`
- Module functions: none
- Classes (1):
  - `VectorMdns` (1 methods)
    - `find_vector`

### `anki_vector.motors`
- Module functions: none
- Classes (1):
  - `MotorComponent` (4 methods)
    - `set_head_motor`, `set_lift_motor`, `set_wheel_motors`, `stop_all_motors`

### `anki_vector.nav_map`
- Module functions: none
- Classes (5):
  - `EvtNavMapUpdate` (0 methods)
  - `NavNodeContentTypes` (0 methods)
  - `NavMapGridNode` (4 methods)
    - `add_child`, `contains_point`, `get_content`, `get_node`
  - `NavMapGrid` (7 methods)
    - `add_quad`, `center`, `contains_point`, `get_content`, `get_node`, `root_node`, `size`
  - `NavMapComponent` (3 methods)
    - `close_nav_map_feed`, `init_nav_map_feed`, `latest_nav_map`

### `anki_vector.objects`
- Module functions: none
- Classes (12):
  - `EvtObjectObserved` (0 methods)
  - `EvtObjectAppeared` (0 methods)
  - `EvtObjectDisappeared` (0 methods)
  - `EvtObjectFinishedMove` (0 methods)
  - `ObservableObject` (7 methods)
    - `is_visible`, `last_event_time`, `last_observed_image_rect`, `last_observed_robot_timestamp`, `last_observed_time`, `pose`, `time_since_last_seen`
  - `LightCube` (19 methods)
    - `descriptive_name`, `factory_id`, `is_connected`, `is_moving`, `last_moved_robot_timestamp`, `last_moved_start_robot_timestamp`, `last_moved_start_time`, `last_moved_time`, `last_tapped_robot_timestamp`, `last_tapped_time`, `last_up_axis_changed_robot_timestamp`, `last_up_axis_changed_time`, `object_id`, `set_light_corners`, `set_lights`, `set_lights_off`, `teardown`, `top_face_orientation_rad`, `up_axis`
  - `Charger` (3 methods)
    - `descriptive_name`, `object_id`, `teardown`
  - `CustomObjectArchetype` (7 methods)
    - `custom_type`, `is_unique`, `marker_height_mm`, `marker_width_mm`, `x_size_mm`, `y_size_mm`, `z_size_mm`
  - `CustomObject` (4 methods)
    - `archetype`, `descriptive_name`, `object_id`, `teardown`
  - `CustomObjectTypes` (0 methods)
  - `CustomObjectMarkers` (0 methods)
  - `FixedCustomObject` (6 methods)
    - `object_id`, `pose`, `teardown`, `x_size_mm`, `y_size_mm`, `z_size_mm`

### `anki_vector.photos`
- Module functions: none
- Classes (1):
  - `PhotographComponent` (4 methods)
    - `get_photo`, `get_thumbnail`, `load_photo_info`, `photo_info`

### `anki_vector.proximity`
- Module functions: none
- Classes (2):
  - `ProximitySensorData` (5 methods)
    - `distance`, `found_object`, `is_lift_in_fov`, `signal_quality`, `unobstructed`
  - `ProximityComponent` (2 methods)
    - `close`, `last_sensor_reading`

### `anki_vector.robot`
- Module functions: none
- Classes (2):
  - `Robot` (37 methods)
    - `accel`, `anim`, `audio`, `behavior`, `camera`, `carrying_object_id`, `conn`, `connect`, `disconnect`, `enable_audio_feed`, `events`, `faces`, `force_async`, `get_battery_state`, `get_version_state`, `gyro`, `head_angle_rad`, `head_tracking_object_id`, `last_image_time_stamp`, `left_wheel_speed_mmps`, `lift_height_mm`, `localized_to_object_id`, `motors`, `nav_map`, `photos`, `pose`, `pose_angle_rad`, `pose_pitch_rad`, `proximity`, `right_wheel_speed_mmps`, `screen`, `status`, `touch`, `viewer`, `viewer_3d`, `vision`, `world`
  - `AsyncRobot` (0 methods)

### `anki_vector.screen`
- Module functions (3): `convert_image_to_screen_data`, `convert_pixels_to_screen_data`, `dimensions`
- Classes (1):
  - `ScreenComponent` (2 methods)
    - `set_screen_to_color`, `set_screen_with_image_data`

### `anki_vector.status`
- Module functions: none
- Classes (1):
  - `RobotStatus` (18 methods)
    - `are_motors_moving`, `are_wheels_moving`, `is_animating`, `is_being_held`, `is_button_pressed`, `is_carrying_block`, `is_charging`, `is_cliff_detected`, `is_docking_to_marker`, `is_falling`, `is_head_in_pos`, `is_in_calm_power_mode`, `is_lift_in_pos`, `is_on_charger`, `is_pathing`, `is_picked_up`, `is_robot_moving`, `set`

### `anki_vector.touch`
- Module functions: none
- Classes (2):
  - `TouchSensorData` (2 methods)
    - `is_being_touched`, `raw_touch_value`
  - `TouchComponent` (2 methods)
    - `close`, `last_sensor_reading`

### `anki_vector.user_intent`
- Module functions: none
- Classes (2):
  - `UserIntentEvent` (0 methods)
  - `UserIntent` (2 methods)
    - `intent_data`, `intent_event`

### `anki_vector.util`
- Module functions (11): `angle_z_to_quaternion`, `block_while_none`, `degrees`, `distance_inches`, `distance_mm`, `get_class_logger`, `parse_command_args`, `radians`, `read_configuration`, `setup_basic_logging`, `speed_mmps`
- Classes (13):
  - `Vector2` (4 methods)
    - `set_to`, `x`, `x_y`, `y`
  - `Vector3` (10 methods)
    - `cross`, `dot`, `magnitude`, `magnitude_squared`, `normalized`, `set_to`, `x`, `x_y_z`, `y`, `z`
  - `Angle` (3 methods)
    - `abs_value`, `degrees`, `radians`
  - `Matrix44` (11 methods)
    - `forward_xyz`, `in_column_order`, `in_row_order`, `left_xyz`, `pos_xyz`, `set_forward`, `set_left`, `set_pos`, `set_up`, `tabulated_string`, `up_xyz`
  - `Quaternion` (7 methods)
    - `angle_z`, `q0`, `q0_q1_q2_q3`, `q1`, `q2`, `q3`, `to_matrix`
  - `Position` (0 methods)
  - `Pose` (8 methods)
    - `define_pose_relative_this`, `is_comparable`, `is_valid`, `origin_id`, `position`, `rotation`, `to_matrix`, `to_proto_pose_struct`
  - `ImageRect` (5 methods)
    - `height`, `scale_by`, `width`, `x_top_left`, `y_top_left`
  - `Distance` (2 methods)
    - `distance_inches`, `distance_mm`
  - `Speed` (1 methods)
    - `speed_mmps`
  - `BaseOverlay` (2 methods)
    - `line_color`, `line_thickness`
  - `RectangleOverlay` (3 methods)
    - `apply_overlay`, `height`, `width`
  - `Component` (4 methods)
    - `conn`, `force_async`, `grpc_interface`, `robot`

### `anki_vector.version`
- Module functions: none
- Classes: none

### `anki_vector.viewer`
- Module functions: none
- Classes (2):
  - `ViewerComponent` (3 methods)
    - `close`, `enqueue_frame`, `show`
  - `Viewer3DComponent` (5 methods)
    - `add_render_call`, `close`, `connect_to_cube`, `show`, `user_data_queue`

### `anki_vector.vision`
- Module functions: none
- Classes (1):
  - `VisionComponent` (10 methods)
    - `close`, `detect_custom_objects`, `detect_faces`, `detect_motion`, `disable_all_vision_modes`, `display_camera_feed_on_face`, `enable_custom_object_detection`, `enable_display_camera_feed_on_face`, `enable_face_detection`, `enable_motion_detection`

### `anki_vector.world`
- Module functions: none
- Classes (1):
  - `World` (21 methods)
    - `all_objects`, `charger`, `close`, `connect_cube`, `connected_light_cube`, `create_custom_fixed_object`, `custom_object_archetypes`, `define_custom_box`, `define_custom_cube`, `define_custom_wall`, `delete_custom_objects`, `disconnect_cube`, `flash_cube_lights`, `forget_preferred_cube`, `get_face`, `get_object`, `light_cube`, `set_preferred_cube`, `visible_custom_objects`, `visible_faces`, `visible_objects`

## Notes for downstream MCP design
- Keep `API_REFERENCE.md` restricted to implemented MCP tools.
- Use this file as the upstream capability catalog.
- Track decisioning in `SDK_TO_MCP_COVERAGE_MATRIX.md` (include/defer/exclude + rationale).
