# Wire-Pod SDK Surface Reference (Comprehensive + Implementation Detail)

Purpose: implementation-ready reference for the full `wirepod_vector_sdk` API surface (`anki_vector` namespace).

_Generated from source on 2026-02-27T08:16:58_

## How to use this doc
- **Access method** tells you how to call each API from an MCP tool implementation.
- **Signature** is source-derived and shows arguments/defaults/type hints when present.
- **Description/Args/Returns** are extracted from SDK docstrings when available.

## Robot component access map (common MCP entry points)
- `robot.behavior.<method>(...)` → behavior actions (speech, drive, pose-goal, charger, cube interactions)
- `robot.world.<method>(...)` → world/cube/faces/object visibility and charger object access
- `robot.camera.<method/property>` → image capture + camera config
- `robot.anim.<method>(...)` → animation APIs
- `robot.audio.<method>(...)` → volume and WAV playback
- `robot.motors.<method>(...)` → direct motor control
- `robot.screen.<method>(...)` → face/screen rendering
- `robot.vision.<method>(...)` → vision mode toggles and detections
- `robot.faces.<method>(...)` → enrolled face management
- `robot.photos.<method>(...)` → stored photo retrieval
- `robot.touch.<property/method>` + `robot.proximity.<property/method>` → sensor reads


## `anki_vector.animation`
- Module description: Animation related classes, functions, events and values.

### Classes and methods
#### Class `AnimationComponent`
- Access method: `anki_vector.animation.AnimationComponent`
- Description: Play animations on the robot
- Public methods:
  - `anim_list(self)`
    - Access method: `animationcomponent.anim_list(...)` *(or via component property on `Robot` when applicable)*
    - Description: Holds the set of animation names (strings) returned from the robot.
  - `anim_trigger_list(self)`
    - Access method: `animationcomponent.anim_trigger_list(...)` *(or via component property on `Robot` when applicable)*
    - Description: Holds the set of animation trigger names (strings) returned from the robot.
  - `load_animation_list(self)`
    - Access method: `animationcomponent.load_animation_list(...)` *(or via component property on `Robot` when applicable)*
    - Description: Request the list of animations from the robot.
  - `load_animation_trigger_list(self)`
    - Access method: `animationcomponent.load_animation_trigger_list(...)` *(or via component property on `Robot` when applicable)*
    - Description: Request the list of animation triggers from the robot.
  - `play_animation_trigger(self, anim_trigger: str, loop_count: int=1, use_lift_safe: bool=False, ignore_body_track: bool=False, ignore_head_track: bool=False, ignore_lift_track: bool=False)`
    - Access method: `animationcomponent.play_animation_trigger(...)` *(or via component property on `Robot` when applicable)*
    - Description: Starts an animation trigger playing on a robot.
  - `play_animation(self, anim: str, loop_count: int=1, ignore_body_track: bool=False, ignore_head_track: bool=False, ignore_lift_track: bool=False)`
    - Access method: `animationcomponent.play_animation(...)` *(or via component property on `Robot` when applicable)*
    - Description: Starts an animation playing on a robot.


## `anki_vector.annotate`
- Module description: Camera image annotation.

### Module-level functions
#### `add_img_box_to_image(draw: ImageDraw.ImageDraw, box: util.ImageRect, color: str, text: Union[ImageText, Iterable[ImageText]]=None) -> None`
- Access method: `anki_vector.annotate.add_img_box_to_image(...)`
- Description: Draw a box on an image and optionally add text.

#### `add_polygon_to_image(draw: ImageDraw.ImageDraw, poly_points: list, scale: float, line_color: str, fill_color: str=None) -> None`
- Access method: `anki_vector.annotate.add_polygon_to_image(...)`
- Description: Draw a polygon on an image

#### `annotator(f)`
- Access method: `anki_vector.annotate.annotator(...)`
- Description: A decorator for converting a regular function/method into an Annotator.

### Classes and methods
#### Class `AnnotationPosition`
- Access method: `anki_vector.annotate.AnnotationPosition`
- Description: Specifies where the annotation must be rendered.
- Public methods: none

#### Class `ImageText`
- Access method: `anki_vector.annotate.ImageText`
- Description: ImageText represents some text that can be applied to an image.
- Public methods:
  - `render(self, draw: ImageDraw.ImageDraw, bounds: tuple) -> ImageDraw.ImageDraw`
    - Access method: `imagetext.render(...)` *(or via component property on `Robot` when applicable)*
    - Description: Renders the text onto an image within the specified bounding box.

#### Class `Annotator`
- Access method: `anki_vector.annotate.Annotator`
- Description: Annotation base class
- Public methods:
  - `apply(self, image: Image.Image, scale: float)`
    - Access method: `annotator.apply(...)` *(or via component property on `Robot` when applicable)*
    - Description: Applies the annotation to the image.

#### Class `ObjectAnnotator`
- Access method: `anki_vector.annotate.ObjectAnnotator`
- Description: Adds object annotations to an Image.
- Public methods:
  - `apply(self, image: Image.Image, scale: float) -> None`
    - Access method: `objectannotator.apply(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_

#### Class `FaceAnnotator`
- Access method: `anki_vector.annotate.FaceAnnotator`
- Description: Adds annotations of currently detected faces to a camera image.
- Public methods:
  - `apply(self, image: Image.Image, scale: float) -> None`
    - Access method: `faceannotator.apply(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_

#### Class `TextAnnotator`
- Access method: `anki_vector.annotate.TextAnnotator`
- Description: Adds simple text annotations to a camera image.
- Public methods:
  - `apply(self, image: Image.Image, scale: int) -> None`
    - Access method: `textannotator.apply(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_

#### Class `ImageAnnotator`
- Access method: `anki_vector.annotate.ImageAnnotator`
- Description: ImageAnnotator applies annotations to the camera image received from the robot.
- Public methods:
  - `add_annotator(self, name: str, new_annotator: Union[Annotator, Callable[..., Annotator]]) -> None`
    - Access method: `imageannotator.add_annotator(...)` *(or via component property on `Robot` when applicable)*
    - Description: Adds a new annotator for display.
  - `remove_annotator(self, name: str) -> None`
    - Access method: `imageannotator.remove_annotator(...)` *(or via component property on `Robot` when applicable)*
    - Description: Remove an annotator.
  - `get_annotator(self, name: str) -> None`
    - Access method: `imageannotator.get_annotator(...)` *(or via component property on `Robot` when applicable)*
    - Description: Return a named annotator.
  - `disable_annotator(self, name: str) -> None`
    - Access method: `imageannotator.disable_annotator(...)` *(or via component property on `Robot` when applicable)*
    - Description: Disable a named annotator.
  - `enable_annotator(self, name: str) -> None`
    - Access method: `imageannotator.enable_annotator(...)` *(or via component property on `Robot` when applicable)*
    - Description: Enabled a named annotator.
  - `add_static_text(self, name: str, text: Union[str, ImageText], color: str='white', position: int=AnnotationPosition.TOP_LEFT) -> None`
    - Access method: `imageannotator.add_static_text(...)` *(or via component property on `Robot` when applicable)*
    - Description: Add some static text to annotated images.
  - `annotate_image(self, image: Image.Image, scale: float=None, fit_size: Tuple[int, int]=None, resample_mode: int=RESAMPLE_MODE_NEAREST) -> Image.Image`
    - Access method: `imageannotator.annotate_image(...)` *(or via component property on `Robot` when applicable)*
    - Description: Called by :class:`~anki_vector.camera.CameraComponent` to annotate camera images.


## `anki_vector.audio`
- Module description: Support for accessing Vector's audio.

### Classes and methods
#### Class `RobotVolumeLevel`
- Access method: `anki_vector.audio.RobotVolumeLevel`
- Description: Use these values for setting the master audio volume.  See :meth:`set_master_volume`
- Public methods: none

#### Class `AudioComponent`
- Access method: `anki_vector.audio.AudioComponent`
- Description: Handles audio on Vector.
- Public methods:
  - `set_master_volume(self, volume: RobotVolumeLevel) -> protocol.MasterVolumeResponse`
    - Access method: `audiocomponent.set_master_volume(...)` *(or via component property on `Robot` when applicable)*
    - Description: Sets Vector's master volume level.
  - `stream_wav_file(self, filename, volume=50)`
    - Access method: `audiocomponent.stream_wav_file(...)` *(or via component property on `Robot` when applicable)*
    - Description: Plays audio using Vector's speakers.


## `anki_vector.behavior`
- Module description: .. _behavior:

### Classes and methods
#### Class `BehaviorComponent`
- Access method: `anki_vector.behavior.BehaviorComponent`
- Description: Run behaviors on Vector
- Public methods:
  - `drive_off_charger(self) -> protocol.DriveOffChargerResponse`
    - Access method: `behaviorcomponent.drive_off_charger(...)` *(or via component property on `Robot` when applicable)*
    - Description: Drive Vector off the charger
  - `drive_on_charger(self) -> protocol.DriveOnChargerResponse`
    - Access method: `behaviorcomponent.drive_on_charger(...)` *(or via component property on `Robot` when applicable)*
    - Description: Drive Vector onto the charger
  - `find_faces(self) -> protocol.FindFacesResponse`
    - Access method: `behaviorcomponent.find_faces(...)` *(or via component property on `Robot` when applicable)*
    - Description: Look around for faces
  - `look_around_in_place(self) -> protocol.LookAroundInPlaceResponse`
    - Access method: `behaviorcomponent.look_around_in_place(...)` *(or via component property on `Robot` when applicable)*
    - Description: Look around in place
  - `roll_visible_cube(self) -> protocol.RollBlockResponse`
    - Access method: `behaviorcomponent.roll_visible_cube(...)` *(or via component property on `Robot` when applicable)*
    - Description: Roll a cube that is currently known to the robot
  - `say_text(self, text: str, use_vector_voice: bool=True, duration_scalar: float=1.0) -> protocol.SayTextResponse`
    - Access method: `behaviorcomponent.say_text(...)` *(or via component property on `Robot` when applicable)*
    - Description: Make Vector speak text.
  - `say_localized_text(self, text: str, use_vector_voice: bool=True, duration_scalar: float=1.0, language: str='en') -> protocol.SayTextResponse`
    - Access method: `behaviorcomponent.say_localized_text(...)` *(or via component property on `Robot` when applicable)*
    - Description: Make Vector speak text with a different localized voice.
  - `app_intent(self, intent: str, param: Union[str, int]=None) -> protocol.AppIntentResponse`
    - Access method: `behaviorcomponent.app_intent(...)` *(or via component property on `Robot` when applicable)*
    - Description: Send Vector an intention to do something.
  - `change_locale(self, locale: str) -> protocol.UpdateSettingsResponse`
    - Access method: `behaviorcomponent.change_locale(...)` *(or via component property on `Robot` when applicable)*
    - Description: Change Vectors voice locale
  - `update_settings(self, settings) -> protocol.UpdateSettingsResponse`
    - Access method: `behaviorcomponent.update_settings(...)` *(or via component property on `Robot` when applicable)*
    - Description: Send Vector an intention to do something.
  - `set_eye_color(self, hue: float, saturation: float) -> protocol.SetEyeColorResponse`
    - Access method: `behaviorcomponent.set_eye_color(...)` *(or via component property on `Robot` when applicable)*
    - Description: Set Vector's eye color.
  - `go_to_pose(self, pose: util.Pose, relative_to_robot: bool=False, num_retries: int=0, _action_id: int=None) -> protocol.GoToPoseResponse`
    - Access method: `behaviorcomponent.go_to_pose(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tells Vector to drive to the specified pose and orientation.
    - Returns details:
      - A response from the robot with status information sent when this request successfully completes or fails.
      - .. testcode::
      - import anki_vector
      - from anki_vector.util import degrees, Angle, Pose
      - with anki_vector.Robot() as robot:
      - pose = Pose(x=50, y=0, z=0, angle_z=Angle(degrees=0))
  - `dock_with_cube(self, target_object: objects.LightCube, approach_angle: util.Angle=None, alignment_type: protocol.AlignmentType=protocol.ALIGNMENT_TYPE_LIFT_PLATE, distance_from_marker: util.Distance=None, num_retries: int=0, _action_id: int=None) -> protocol.DockWithCubeResponse`
    - Access method: `behaviorcomponent.dock_with_cube(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tells Vector to dock with a light cube, optionally using a given approach angle and distance.
    - Returns details:
      - A response from the robot with status information sent when this request successfully completes or fails.
      - .. testcode::
      - import anki_vector
      - with anki_vector.Robot() as robot:
      - robot.world.connect_cube()
      - if robot.world.connected_light_cube:
  - `drive_straight(self, distance: util.Distance, speed: util.Speed, should_play_anim: bool=True, num_retries: int=0, _action_id: int=None) -> protocol.DriveStraightResponse`
    - Access method: `behaviorcomponent.drive_straight(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tells Vector to drive in a straight line.
    - Returns details:
      - A response from the robot with status information sent when this request successfully completes or fails.
      - .. testcode::
      - import anki_vector
      - from anki_vector.util import distance_mm, speed_mmps
      - with anki_vector.Robot() as robot:
      - robot.behavior.drive_straight(distance_mm(200), speed_mmps(100))
  - `turn_in_place(self, angle: util.Angle, speed: util.Angle=util.Angle(0.0), accel: util.Angle=util.Angle(0.0), angle_tolerance: util.Angle=util.Angle(0.0), is_absolute: bool=0, num_retries: int=0, _action_id: int=None) -> protocol.TurnInPlaceResponse`
    - Access method: `behaviorcomponent.turn_in_place(...)` *(or via component property on `Robot` when applicable)*
    - Description: Turn the robot around its current position.
    - Returns details:
      - A response from the robot with status information sent when this request successfully completes or fails.
      - .. testcode::
      - import anki_vector
      - from anki_vector.util import degrees
      - with anki_vector.Robot() as robot:
      - robot.behavior.turn_in_place(degrees(90))
  - `set_head_angle(self, angle: util.Angle, accel: float=10.0, max_speed: float=10.0, duration: float=0.0, num_retries: int=0, _action_id: int=None) -> protocol.SetHeadAngleResponse`
    - Access method: `behaviorcomponent.set_head_angle(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tell Vector's head to move to a given angle.
    - Returns details:
      - A response from the robot with status information sent when this request successfully completes or fails.
      - .. testcode::
      - import anki_vector
      - from anki_vector.util import degrees
      - from anki_vector.behavior import MIN_HEAD_ANGLE, MAX_HEAD_ANGLE
      - with anki_vector.Robot() as robot:
  - `set_lift_height(self, height: float, accel: float=10.0, max_speed: float=10.0, duration: float=0.0, num_retries: int=0, _action_id: int=None) -> protocol.SetLiftHeightResponse`
    - Access method: `behaviorcomponent.set_lift_height(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tell Vector's lift to move to a given height.
    - Returns details:
      - A response from the robot with status information sent when this request successfully completes or fails.
      - .. testcode::
      - import anki_vector
      - with anki_vector.Robot() as robot:
      - robot.behavior.set_lift_height(1.0)
      - robot.behavior.set_lift_height(0.0)
  - `turn_towards_face(self, face: faces.Face, num_retries: int=0, _action_id: int=None) -> protocol.TurnTowardsFaceResponse`
    - Access method: `behaviorcomponent.turn_towards_face(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tells Vector to turn towards this face.
    - Returns details:
      - A response from the robot with status information sent when this request successfully completes or fails.
      - .. testcode::
      - import anki_vector
      - with anki_vector.Robot() as robot:
      - robot.behavior.turn_towards_face(1)
      - Example of cancelling the :meth:`turn_towards_face` behavior:
  - `go_to_object(self, target_object: objects.LightCube, distance_from_object, num_retries: int=0, _action_id: int=None) -> protocol.GoToObjectResponse`
    - Access method: `behaviorcomponent.go_to_object(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tells Vector to drive to his Cube.
    - Returns details:
      - A response from the robot with status information sent when this request successfully completes or fails.
      - .. testcode::
      - import anki_vector
      - from anki_vector.util import distance_mm
      - with anki_vector.Robot() as robot:
      - robot.world.connect_cube()
  - `roll_cube(self, target_object: objects.LightCube, approach_angle: util.Angle=None, num_retries: int=0, _action_id: int=None) -> protocol.RollObjectResponse`
    - Access method: `behaviorcomponent.roll_cube(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tells Vector to roll a specified cube object.
    - Returns details:
      - A response from the robot with status information sent when this request successfully completes or fails.
      - .. testcode::
      - import anki_vector
      - from anki_vector.util import distance_mm
      - with anki_vector.Robot() as robot:
      - robot.world.connect_cube()
  - `pop_a_wheelie(self, target_object: objects.LightCube, approach_angle: util.Angle=None, num_retries: int=0, _action_id: int=None) -> protocol.PopAWheelieResponse`
    - Access method: `behaviorcomponent.pop_a_wheelie(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tells Vector to "pop a wheelie" using his light cube.
    - Returns details:
      - A response from the robot with status information sent when this request successfully completes or fails.
      - .. testcode::
      - import anki_vector
      - from anki_vector.util import distance_mm
      - with anki_vector.Robot() as robot:
      - robot.world.connect_cube()
  - `pickup_object(self, target_object: objects.LightCube, use_pre_dock_pose: bool=True, num_retries: int=0, _action_id: int=None) -> protocol.PickupObjectResponse`
    - Access method: `behaviorcomponent.pickup_object(...)` *(or via component property on `Robot` when applicable)*
    - Description: Instruct the robot to pick up his LightCube.
    - Returns details:
      - A response from the robot with status information sent when this request successfully completes or fails.
      - .. testcode::
      - import anki_vector
      - with anki_vector.Robot() as robot:
      - robot.world.connect_cube()
      - if robot.world.connected_light_cube:
  - `place_object_on_ground_here(self, num_retries: int=0, _action_id: int=None) -> protocol.PlaceObjectOnGroundHereResponse`
    - Access method: `behaviorcomponent.place_object_on_ground_here(...)` *(or via component property on `Robot` when applicable)*
    - Description: Ask Vector to place the object he is carrying on the ground at the current location.
    - Returns details:
      - A response from the robot with status information sent when this request successfully completes or fails.
      - .. testcode::
      - import anki_vector
      - with anki_vector.Robot() as robot:
      - robot.world.connect_cube()
      - if robot.world.connected_light_cube:

#### Class `ReserveBehaviorControl`
- Access method: `anki_vector.behavior.ReserveBehaviorControl`
- Description: A ReserveBehaviorControl object can be used to suppress the ordinary idle behaviors of
- Public methods: none


## `anki_vector.camera`
- Module description: Support for Vector's camera.

### Classes and methods
#### Class `CameraImage`
- Access method: `anki_vector.camera.CameraImage`
- Description: A single image from the robot's camera.
- Public methods:
  - `raw_image(self) -> Image.Image`
    - Access method: `cameraimage.raw_image(...)` *(or via component property on `Robot` when applicable)*
    - Description: The raw unprocessed image from the camera.
  - `image_id(self) -> int`
    - Access method: `cameraimage.image_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: An image number that increments on every new image received.
  - `image_recv_time(self) -> float`
    - Access method: `cameraimage.image_recv_time(...)` *(or via component property on `Robot` when applicable)*
    - Description: The time the image was received and processed by the SDK.
  - `annotate_image(self, scale: float=None, fit_size: tuple=None, resample_mode: int=annotate.RESAMPLE_MODE_NEAREST) -> Image.Image`
    - Access method: `cameraimage.annotate_image(...)` *(or via component property on `Robot` when applicable)*
    - Description: Adds any enabled annotations to the image.

#### Class `CameraConfig`
- Access method: `anki_vector.camera.CameraConfig`
- Description: The fixed properties for Vector's camera.
- Public methods:
  - `create_from_message(cls, msg: protocol.CameraConfigResponse)`
    - Access method: `cameraconfig.create_from_message(...)` *(or via component property on `Robot` when applicable)*
    - Description: Create camera configuration based on Vector's camera configuration from the message sent from the Robot
  - `min_gain(self) -> float`
    - Access method: `cameraconfig.min_gain(...)` *(or via component property on `Robot` when applicable)*
    - Description: The minimum supported camera gain.
  - `max_gain(self) -> float`
    - Access method: `cameraconfig.max_gain(...)` *(or via component property on `Robot` when applicable)*
    - Description: The maximum supported camera gain.
  - `min_exposure_time_ms(self) -> int`
    - Access method: `cameraconfig.min_exposure_time_ms(...)` *(or via component property on `Robot` when applicable)*
    - Description: The minimum supported exposure time in milliseconds.
  - `max_exposure_time_ms(self) -> int`
    - Access method: `cameraconfig.max_exposure_time_ms(...)` *(or via component property on `Robot` when applicable)*
    - Description: The maximum supported exposure time in milliseconds.
  - `focal_length(self)`
    - Access method: `cameraconfig.focal_length(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`anki_vector.util.Vector2`: The focal length of the camera.
  - `center(self)`
    - Access method: `cameraconfig.center(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`anki_vector.util.Vector2`: The focal center of the camera.
  - `fov_x(self)`
    - Access method: `cameraconfig.fov_x(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`anki_vector.util.Angle`: The x (horizontal) field of view.
  - `fov_y(self)`
    - Access method: `cameraconfig.fov_y(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`anki_vector.util.Angle`: The y (vertical) field of view.

#### Class `CameraComponent`
- Access method: `anki_vector.camera.CameraComponent`
- Description: Represents Vector's camera.
- Public methods:
  - `set_config(self, message: protocol.CameraConfigRequest)`
    - Access method: `cameracomponent.set_config(...)` *(or via component property on `Robot` when applicable)*
    - Description: Update Vector's camera configuration from the message sent from the Robot
  - `get_camera_config(self) -> protocol.CameraConfigResponse`
    - Access method: `cameracomponent.get_camera_config(...)` *(or via component property on `Robot` when applicable)*
    - Description: Get Vector's camera configuration
  - `config(self) -> CameraConfig`
    - Access method: `cameracomponent.config(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`anki_vector.camera.CameraConfig`: The read-only config/calibration for the camera
  - `is_auto_exposure_enabled(self) -> bool`
    - Access method: `cameracomponent.is_auto_exposure_enabled(...)` *(or via component property on `Robot` when applicable)*
    - Description: bool: True if auto exposure is currently enabled
  - `gain(self) -> float`
    - Access method: `cameracomponent.gain(...)` *(or via component property on `Robot` when applicable)*
    - Description: float: The current camera gain setting.
  - `exposure_ms(self) -> int`
    - Access method: `cameracomponent.exposure_ms(...)` *(or via component property on `Robot` when applicable)*
    - Description: int: The current camera exposure setting in milliseconds.
  - `update_state(self, _robot, _event_type, msg)`
    - Access method: `cameracomponent.update_state(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `latest_image(self) -> CameraImage`
    - Access method: `cameracomponent.latest_image(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`Image.Image`: The most recently processed image received from the robot.
  - `latest_image_id(self) -> int`
    - Access method: `cameracomponent.latest_image_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: The most recently processed image's id received from the robot.
  - `image_annotator(self) -> annotate.ImageAnnotator`
    - Access method: `cameracomponent.image_annotator(...)` *(or via component property on `Robot` when applicable)*
    - Description: The image annotator used to add annotations to the raw camera images.
  - `init_camera_feed(self) -> None`
    - Access method: `cameracomponent.init_camera_feed(...)` *(or via component property on `Robot` when applicable)*
    - Description: Begin camera feed task.
  - `close_camera_feed(self) -> None`
    - Access method: `cameracomponent.close_camera_feed(...)` *(or via component property on `Robot` when applicable)*
    - Description: Cancel camera feed task.
  - `image_streaming_enabled(self) -> bool`
    - Access method: `cameracomponent.image_streaming_enabled(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if image streaming is enabled on the robot
  - `capture_single_image(self, enable_high_resolution: bool=False) -> CameraImage`
    - Access method: `cameracomponent.capture_single_image(...)` *(or via component property on `Robot` when applicable)*
    - Description: Request to capture a single image from the robot's camera.
  - `enable_auto_exposure(self, enable_auto_exposure=True) -> protocol.SetCameraSettingsResponse`
    - Access method: `cameracomponent.enable_auto_exposure(...)` *(or via component property on `Robot` when applicable)*
    - Description: Enable auto exposure on Vector's Camera.
  - `set_manual_exposure(self, exposure_ms: int, gain: float) -> protocol.SetCameraSettingsResponse`
    - Access method: `cameracomponent.set_manual_exposure(...)` *(or via component property on `Robot` when applicable)*
    - Description: Set manual exposure values for Vector's Camera.

#### Class `EvtNewRawCameraImage`
- Access method: `anki_vector.camera.EvtNewRawCameraImage`
- Description: Dispatched when a new raw image is received from the robot's camera.
- Public methods: none

#### Class `EvtNewCameraImage`
- Access method: `anki_vector.camera.EvtNewCameraImage`
- Description: Dispatched when a new camera image is received and processed from the robot's camera.
- Public methods: none


## `anki_vector.color`
- Module description: Colors to be used with a light or Vector's screen.

### Classes and methods
#### Class `Color`
- Access method: `anki_vector.color.Color`
- Description: A Color to be used with a Light or Vector's screen.
- Public methods:
  - `int_color(self) -> int`
    - Access method: `color.int_color(...)` *(or via component property on `Robot` when applicable)*
    - Description: The encoded integer value of the color.
  - `rgb565_bytepair(self)`
    - Access method: `color.rgb565_bytepair(...)` *(or via component property on `Robot` when applicable)*
    - Description: bytes[]: Two bytes representing an int16 color with rgb565 encoding.


## `anki_vector.connection`
- Module description: Management of the connection to and from Vector.

### Module-level functions
#### `on_connection_thread(log_messaging: bool=True, requires_control: bool=True, is_cancellable: CancelType=None) -> Callable[[Coroutine[util.Component, Any, None]], Any]`
- Access method: `anki_vector.connection.on_connection_thread(...)`
- Description: A decorator generator used internally to denote which functions will run on

### Classes and methods
#### Class `CancelType`
- Access method: `anki_vector.connection.CancelType`
- Description: Enum used to specify cancellation options for behaviors -- internal use only
- Public methods: none

#### Class `ControlPriorityLevel`
- Access method: `anki_vector.connection.ControlPriorityLevel`
- Description: Enum used to specify the priority level for the program.
- Public methods: none

#### Class `Connection`
- Access method: `anki_vector.connection.Connection`
- Description: Creates and maintains a aiogrpc connection including managing the connection thread.
- Public methods:
  - `loop(self) -> asyncio.BaseEventLoop`
    - Access method: `connection.loop(...)` *(or via component property on `Robot` when applicable)*
    - Description: A direct reference to the loop on the connection thread.
  - `thread(self) -> threading.Thread`
    - Access method: `connection.thread(...)` *(or via component property on `Robot` when applicable)*
    - Description: A direct reference to the connection thread. Available to callers to determine if the
  - `grpc_interface(self) -> client.ExternalInterfaceStub`
    - Access method: `connection.grpc_interface(...)` *(or via component property on `Robot` when applicable)*
    - Description: A direct reference to the connected aiogrpc interface.
  - `behavior_control_level(self) -> ControlPriorityLevel`
    - Access method: `connection.behavior_control_level(...)` *(or via component property on `Robot` when applicable)*
    - Description: Returns the specific :class:`ControlPriorityLevel` requested for behavior control.
  - `requires_behavior_control(self) -> bool`
    - Access method: `connection.requires_behavior_control(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if the :class:`Connection` requires behavior control.
  - `control_lost_event(self) -> asyncio.Event`
    - Access method: `connection.control_lost_event(...)` *(or via component property on `Robot` when applicable)*
    - Description: This provides an :class:`asyncio.Event` that a user may :func:`wait()` upon to
  - `control_granted_event(self) -> asyncio.Event`
    - Access method: `connection.control_granted_event(...)` *(or via component property on `Robot` when applicable)*
    - Description: This provides an :class:`asyncio.Event` that a user may :func:`wait()` upon to
  - `request_control(self, behavior_control_level: ControlPriorityLevel=ControlPriorityLevel.DEFAULT_PRIORITY, timeout: float=10.0)`
    - Access method: `connection.request_control(...)` *(or via component property on `Robot` when applicable)*
    - Description: Explicitly request behavior control. Typically used after detecting :func:`control_lost_event`.
  - `release_control(self, timeout: float=10.0)`
    - Access method: `connection.release_control(...)` *(or via component property on `Robot` when applicable)*
    - Description: Explicitly release control. Typically used after detecting :func:`control_lost_event`.
  - `connect(self, timeout: float=10.0) -> None`
    - Access method: `connection.connect(...)` *(or via component property on `Robot` when applicable)*
    - Description: Connect to Vector. This will start the connection thread which handles all messages
  - `close(self)`
    - Access method: `connection.close(...)` *(or via component property on `Robot` when applicable)*
    - Description: Cleanup the connection, and shutdown all the event handlers.
  - `run_soon(self, coro: Awaitable) -> None`
    - Access method: `connection.run_soon(...)` *(or via component property on `Robot` when applicable)*
    - Description: Schedules the given awaitable to run on the event loop for the connection thread.
  - `run_coroutine(self, coro: Awaitable) -> Any`
    - Access method: `connection.run_coroutine(...)` *(or via component property on `Robot` when applicable)*
    - Description: Runs a given awaitable on the connection thread's event loop.


## `anki_vector.events`
- Module description: Event handler used to make functions subscribe to robot events.

### Classes and methods
#### Class `Events`
- Access method: `anki_vector.events.Events`
- Description: List of events available.
- Public methods: none

#### Class `EventHandler`
- Access method: `anki_vector.events.EventHandler`
- Description: Listen for Vector events.
- Public methods:
  - `start(self, connection: Connection)`
    - Access method: `eventhandler.start(...)` *(or via component property on `Robot` when applicable)*
    - Description: Start listening for events. Automatically called by the :class:`anki_vector.robot.Robot` class.
  - `close(self)`
    - Access method: `eventhandler.close(...)` *(or via component property on `Robot` when applicable)*
    - Description: Stop listening for events. Automatically called by the :class:`anki_vector.robot.Robot` class.
  - `dispatch_event_by_name(self, event_data, event_name: str)`
    - Access method: `eventhandler.dispatch_event_by_name(...)` *(or via component property on `Robot` when applicable)*
    - Description: Dispatches event to event listeners by name.
  - `dispatch_event(self, event_data, event_type: Events)`
    - Access method: `eventhandler.dispatch_event(...)` *(or via component property on `Robot` when applicable)*
    - Description: Dispatches event to event listeners.
  - `subscribe_by_name(self, func: Callable, event_name: str, *args, **kwargs)`
    - Access method: `eventhandler.subscribe_by_name(...)` *(or via component property on `Robot` when applicable)*
    - Description: Receive a method call when the specified event occurs.
  - `subscribe(self, func: Callable, event_type: Events, *args, **kwargs)`
    - Access method: `eventhandler.subscribe(...)` *(or via component property on `Robot` when applicable)*
    - Description: Receive a method call when the specified event occurs.
  - `unsubscribe_by_name(self, func: Callable, event_name: str)`
    - Access method: `eventhandler.unsubscribe_by_name(...)` *(or via component property on `Robot` when applicable)*
    - Description: Unregister a previously subscribed method from an event.
  - `unsubscribe(self, func: Callable, event_type: Events)`
    - Access method: `eventhandler.unsubscribe(...)` *(or via component property on `Robot` when applicable)*
    - Description: Unregister a previously subscribed method from an event.


## `anki_vector.exceptions`
- Module description: SDK-specific exception classes for Vector.

### Module-level functions
#### `connection_error(rpc_error: RpcError) -> VectorConnectionException`
- Access method: `anki_vector.exceptions.connection_error(...)`
- Description: Translates grpc-specific errors to user-friendly :class:`VectorConnectionException`.

### Classes and methods
#### Class `VectorException`
- Access method: `anki_vector.exceptions.VectorException`
- Description: Base class of all Vector SDK exceptions.
- Public methods: none

#### Class `VectorInvalidVersionException`
- Access method: `anki_vector.exceptions.VectorInvalidVersionException`
- Description: Your SDK version is not compatible with Vector's version.
- Public methods: none

#### Class `VectorControlException`
- Access method: `anki_vector.exceptions.VectorControlException`
- Description: Unable to run a function which requires behavior control.
- Public methods: none

#### Class `VectorConnectionException`
- Access method: `anki_vector.exceptions.VectorConnectionException`
- Description: _(none)_
- Public methods:
  - `status(self)`
    - Access method: `vectorconnectionexception.status(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `details(self)`
    - Access method: `vectorconnectionexception.details(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_

#### Class `VectorUnauthenticatedException`
- Access method: `anki_vector.exceptions.VectorUnauthenticatedException`
- Description: Failed to authenticate request.
- Public methods: none

#### Class `VectorUnavailableException`
- Access method: `anki_vector.exceptions.VectorUnavailableException`
- Description: Unable to reach Vector.
- Public methods: none

#### Class `VectorUnimplementedException`
- Access method: `anki_vector.exceptions.VectorUnimplementedException`
- Description: Vector does not handle this message.
- Public methods: none

#### Class `VectorTimeoutException`
- Access method: `anki_vector.exceptions.VectorTimeoutException`
- Description: Message took too long to complete.
- Public methods: none

#### Class `VectorAsyncException`
- Access method: `anki_vector.exceptions.VectorAsyncException`
- Description: Invalid asynchronous action attempted.
- Public methods: none

#### Class `VectorBehaviorControlException`
- Access method: `anki_vector.exceptions.VectorBehaviorControlException`
- Description: Invalid behavior control action attempted.
- Public methods: none

#### Class `VectorCameraFeedException`
- Access method: `anki_vector.exceptions.VectorCameraFeedException`
- Description: The camera feed is not open.
- Public methods: none

#### Class `VectorCameraImageCaptureException`
- Access method: `anki_vector.exceptions.VectorCameraImageCaptureException`
- Description: Image capture exception.
- Public methods: none

#### Class `VectorConfigurationException`
- Access method: `anki_vector.exceptions.VectorConfigurationException`
- Description: Invalid or missing configuration data.
- Public methods: none

#### Class `VectorControlTimeoutException`
- Access method: `anki_vector.exceptions.VectorControlTimeoutException`
- Description: Failed to get control of Vector.
- Public methods: none

#### Class `VectorNotFoundException`
- Access method: `anki_vector.exceptions.VectorNotFoundException`
- Description: Unable to establish a connection to Vector.
- Public methods: none

#### Class `VectorNotReadyException`
- Access method: `anki_vector.exceptions.VectorNotReadyException`
- Description: Vector tried to do something before it was ready.
- Public methods: none

#### Class `VectorPropertyValueNotReadyException`
- Access method: `anki_vector.exceptions.VectorPropertyValueNotReadyException`
- Description: Failed to retrieve the value for this property.
- Public methods: none

#### Class `VectorUnreliableEventStreamException`
- Access method: `anki_vector.exceptions.VectorUnreliableEventStreamException`
- Description: The robot event stream is currently unreliable.
- Public methods: none

#### Class `VectorExternalAudioPlaybackException`
- Access method: `anki_vector.exceptions.VectorExternalAudioPlaybackException`
- Description: Failed to play external audio on Vector.
- Public methods: none


## `anki_vector.faces`
- Module description: Face recognition and enrollment.

### Classes and methods
#### Class `EvtFaceObserved`
- Access method: `anki_vector.faces.EvtFaceObserved`
- Description: Triggered whenever a face is visually identified by the robot.
- Public methods: none

#### Class `EvtFaceAppeared`
- Access method: `anki_vector.faces.EvtFaceAppeared`
- Description: Triggered whenever a face is first visually identified by a robot.
- Public methods: none

#### Class `EvtFaceDisappeared`
- Access method: `anki_vector.faces.EvtFaceDisappeared`
- Description: Triggered whenever a face that was previously being observed is no longer visible.
- Public methods: none

#### Class `Expression`
- Access method: `anki_vector.faces.Expression`
- Description: Facial expressions that Vector can distinguish.
- Public methods: none

#### Class `Face`
- Access method: `anki_vector.faces.Face`
- Description: A single face that Vector has detected.
- Public methods:
  - `name_face(self, name: str) -> protocol.EnrollFaceResponse`
    - Access method: `face.name_face(...)` *(or via component property on `Robot` when applicable)*
    - Description: Request to enroll this face with a name. Vector will remember this name between SDK runs.
  - `teardown(self)`
    - Access method: `face.teardown(...)` *(or via component property on `Robot` when applicable)*
    - Description: All faces will be torn down by the world when no longer needed.
  - `face_id(self) -> int`
    - Access method: `face.face_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: The internal ID assigned to the face.
  - `face_id(self, face_id: str)`
    - Access method: `face.face_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `has_updated_face_id(self) -> bool`
    - Access method: `face.has_updated_face_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if this face been updated / superseded by a face with a new ID.
  - `updated_face_id(self) -> int`
    - Access method: `face.updated_face_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: The ID for the face that superseded this one (if any, otherwise :meth:`face_id`)
  - `name(self) -> str`
    - Access method: `face.name(...)` *(or via component property on `Robot` when applicable)*
    - Description: The name Vector has associated with the face.
  - `expression(self) -> str`
    - Access method: `face.expression(...)` *(or via component property on `Robot` when applicable)*
    - Description: The facial expression Vector has recognized on the face.
  - `expression_score(self) -> List[int]`
    - Access method: `face.expression_score(...)` *(or via component property on `Robot` when applicable)*
    - Description: The score/confidence that :attr:`expression` was correct.
  - `left_eye(self) -> List[protocol.CladPoint]`
    - Access method: `face.left_eye(...)` *(or via component property on `Robot` when applicable)*
    - Description: sequence of tuples of float (x,y): points representing the outline of the left eye.
  - `right_eye(self) -> List[protocol.CladPoint]`
    - Access method: `face.right_eye(...)` *(or via component property on `Robot` when applicable)*
    - Description: sequence of tuples of float (x,y): points representing the outline of the right eye.
  - `nose(self) -> List[protocol.CladPoint]`
    - Access method: `face.nose(...)` *(or via component property on `Robot` when applicable)*
    - Description: sequence of tuples of float (x,y): points representing the outline of the nose.
  - `mouth(self) -> List[protocol.CladPoint]`
    - Access method: `face.mouth(...)` *(or via component property on `Robot` when applicable)*
    - Description: sequence of tuples of float (x,y): points representing the outline of the mouth.

#### Class `FaceComponent`
- Access method: `anki_vector.faces.FaceComponent`
- Description: Manage the state of the faces on the robot.
- Public methods:
  - `request_enrolled_names(self) -> protocol.RequestEnrolledNamesResponse`
    - Access method: `facecomponent.request_enrolled_names(...)` *(or via component property on `Robot` when applicable)*
    - Description: Asks the robot for the list of names attached to faces that it can identify.
  - `update_enrolled_face_by_id(self, face_id: int, old_name: str, new_name: str)`
    - Access method: `facecomponent.update_enrolled_face_by_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: Update the name enrolled for a given face.
  - `erase_enrolled_face_by_id(self, face_id: int)`
    - Access method: `facecomponent.erase_enrolled_face_by_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: Erase the enrollment (name) record for the face with this ID.
  - `erase_all_enrolled_faces(self)`
    - Access method: `facecomponent.erase_all_enrolled_faces(...)` *(or via component property on `Robot` when applicable)*
    - Description: Erase the enrollment (name) records for all faces.


## `anki_vector.lights`
- Module description: Helper routines for dealing with Vector's Cube lights and colors.

### Module-level functions
#### `package_request_params(lights, color_profile)`
- Access method: `anki_vector.lights.package_request_params(...)`
- Description: _(none)_

### Classes and methods
#### Class `ColorProfile`
- Access method: `anki_vector.lights.ColorProfile`
- Description: Applies transforms to make Vector's Cube lights and colors appear as
- Public methods:
  - `augment_color(self, original_color)`
    - Access method: `colorprofile.augment_color(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `red_multiplier(self)`
    - Access method: `colorprofile.red_multiplier(...)` *(or via component property on `Robot` when applicable)*
    - Description: float: The multiplier used on the red channel.
  - `green_multiplier(self)`
    - Access method: `colorprofile.green_multiplier(...)` *(or via component property on `Robot` when applicable)*
    - Description: float: The multiplier used on the red channel.
  - `blue_multiplier(self)`
    - Access method: `colorprofile.blue_multiplier(...)` *(or via component property on `Robot` when applicable)*
    - Description: float: The multiplier used on the red channel.

#### Class `Light`
- Access method: `anki_vector.lights.Light`
- Description: Lights are used with Vector's Cube.
- Public methods:
  - `on_color(self) -> Color`
    - Access method: `light.on_color(...)` *(or via component property on `Robot` when applicable)*
    - Description: The color shown when the light is on.
  - `on_color(self, color)`
    - Access method: `light.on_color(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `off_color(self) -> Color`
    - Access method: `light.off_color(...)` *(or via component property on `Robot` when applicable)*
    - Description: The color shown when the light is off.
  - `off_color(self, color)`
    - Access method: `light.off_color(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `on_period_ms(self) -> int`
    - Access method: `light.on_period_ms(...)` *(or via component property on `Robot` when applicable)*
    - Description: The number of milliseconds the light should be "on" for for each cycle.
  - `on_period_ms(self, ms)`
    - Access method: `light.on_period_ms(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `off_period_ms(self) -> int`
    - Access method: `light.off_period_ms(...)` *(or via component property on `Robot` when applicable)*
    - Description: The number of milliseconds the light should be "off" for for each cycle.
  - `off_period_ms(self, ms)`
    - Access method: `light.off_period_ms(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `transition_on_period_ms(self) -> int`
    - Access method: `light.transition_on_period_ms(...)` *(or via component property on `Robot` when applicable)*
    - Description: The number of milliseconds to take to transition the light to the on color.
  - `transition_on_period_ms(self, ms)`
    - Access method: `light.transition_on_period_ms(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `transition_off_period_ms(self) -> int`
    - Access method: `light.transition_off_period_ms(...)` *(or via component property on `Robot` when applicable)*
    - Description: The number of milliseconds to take to transition the light to the off color.
  - `transition_off_period_ms(self, ms)`
    - Access method: `light.transition_off_period_ms(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_


## `anki_vector.mdns`
- Module description: This contains the :class:`VectorMdns` class for discovering Vector (without already knowing

### Classes and methods
#### Class `VectorMdns`
- Access method: `anki_vector.mdns.VectorMdns`
- Description: `VectorMdns` provides a static method for discovering a Vector on the same LAN as
- Public methods:
  - `find_vector(name: str, timeout=5)`
    - Access method: `vectormdns.find_vector(...)` *(or via component property on `Robot` when applicable)*
    - Description: :param name: A name like `"Vector-A1B2"`. If :code:`None`, will search for any Vector.


## `anki_vector.motors`
- Module description: Control the motors of Vector.

### Classes and methods
#### Class `MotorComponent`
- Access method: `anki_vector.motors.MotorComponent`
- Description: Controls the low-level motor functions.
- Public methods:
  - `set_wheel_motors(self, left_wheel_speed: float, right_wheel_speed: float, left_wheel_accel: float=0.0, right_wheel_accel: float=0.0)`
    - Access method: `motorcomponent.set_wheel_motors(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tell Vector to move his wheels / treads at a given speed.
  - `set_head_motor(self, speed: float)`
    - Access method: `motorcomponent.set_head_motor(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tell Vector's head motor to move with a certain speed.
  - `set_lift_motor(self, speed: float)`
    - Access method: `motorcomponent.set_lift_motor(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tell Vector's lift motor to move with a certain speed.
  - `stop_all_motors(self)`
    - Access method: `motorcomponent.stop_all_motors(...)` *(or via component property on `Robot` when applicable)*
    - Description: Tell Vector to stop all motors.


## `anki_vector.nav_map`
- Module description: A 2D navigation memory map of the world around Vector.

### Classes and methods
#### Class `EvtNavMapUpdate`
- Access method: `anki_vector.nav_map.EvtNavMapUpdate`
- Description: Dispatched when a new nav map is received.
- Public methods: none

#### Class `NavNodeContentTypes`
- Access method: `anki_vector.nav_map.NavNodeContentTypes`
- Description: The content types for a :class:`NavMapGridNode`.
- Public methods: none

#### Class `NavMapGridNode`
- Access method: `anki_vector.nav_map.NavMapGridNode`
- Description: A node in a :class:`NavMapGrid`.
- Public methods:
  - `contains_point(self, x: float, y: float) -> bool`
    - Access method: `navmapgridnode.contains_point(...)` *(or via component property on `Robot` when applicable)*
    - Description: Test if the node contains the given x,y coordinates.
    - Returns details:
      - True if the node contains the point, False otherwise.
  - `get_node(self, x: float, y: float) -> 'NavMapGridNode'`
    - Access method: `navmapgridnode.get_node(...)` *(or via component property on `Robot` when applicable)*
    - Description: Get the node at the given x,y coordinates.
    - Returns details:
      - The smallest node that includes the point.
      - Will be ``None`` if the point is outside of the map.
  - `get_content(self, x: float, y: float) -> protocol.NavNodeContentType`
    - Access method: `navmapgridnode.get_content(...)` *(or via component property on `Robot` when applicable)*
    - Description: Get the node's content at the given x,y coordinates.
    - Returns details:
      - The content included at that point. Will be :attr:`NavNodeContentTypes.Unknown`
      - if the point is outside of the map.
  - `add_child(self, content: protocol.NavNodeContentType, depth: int) -> bool`
    - Access method: `navmapgridnode.add_child(...)` *(or via component property on `Robot` when applicable)*
    - Description: Add a child node to the quad tree.
    - Returns details:
      - True if parent should use the next child for future add_child
      - calls.

#### Class `NavMapGrid`
- Access method: `anki_vector.nav_map.NavMapGrid`
- Description: A navigation memory map, stored as a quad-tree.
- Public methods:
  - `root_node(self) -> NavMapGridNode`
    - Access method: `navmapgrid.root_node(...)` *(or via component property on `Robot` when applicable)*
    - Description: The root node for the grid, contains all other nodes.
  - `size(self) -> float`
    - Access method: `navmapgrid.size(...)` *(or via component property on `Robot` when applicable)*
    - Description: The size (width or length) of the square grid.
  - `center(self) -> util.Vector3`
    - Access method: `navmapgrid.center(...)` *(or via component property on `Robot` when applicable)*
    - Description: The center of this map.
  - `contains_point(self, x: float, y: float) -> bool`
    - Access method: `navmapgrid.contains_point(...)` *(or via component property on `Robot` when applicable)*
    - Description: Test if the map contains the given x,y coordinates.
    - Returns details:
      - True if the map contains the point, False otherwise.
  - `get_node(self, x: float, y: float) -> NavMapGridNode`
    - Access method: `navmapgrid.get_node(...)` *(or via component property on `Robot` when applicable)*
    - Description: Get the node at the given x,y coordinates.
    - Returns details:
      - The smallest node that includes the point.
      - Will be ``None`` if the point is outside of the map.
  - `get_content(self, x: float, y: float) -> protocol.NavNodeContentType`
    - Access method: `navmapgrid.get_content(...)` *(or via component property on `Robot` when applicable)*
    - Description: Get the map's content at the given x,y coordinates.
    - Returns details:
      - The content included at that point. Will be :attr:`NavNodeContentTypes.Unknown`
      - if the point is outside of the map.
  - `add_quad(self, content: protocol.NavNodeContentType, depth: int)`
    - Access method: `navmapgrid.add_quad(...)` *(or via component property on `Robot` when applicable)*
    - Description: Adds a new quad to the nav map.

#### Class `NavMapComponent`
- Access method: `anki_vector.nav_map.NavMapComponent`
- Description: Represents Vector's navigation memory map.
- Public methods:
  - `latest_nav_map(self) -> NavMapGrid`
    - Access method: `navmapcomponent.latest_nav_map(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`NavMapGrid`: The most recently processed image received from the robot.
  - `init_nav_map_feed(self, frequency: float=0.5) -> None`
    - Access method: `navmapcomponent.init_nav_map_feed(...)` *(or via component property on `Robot` when applicable)*
    - Description: Begin nav map feed task.
  - `close_nav_map_feed(self) -> None`
    - Access method: `navmapcomponent.close_nav_map_feed(...)` *(or via component property on `Robot` when applicable)*
    - Description: Cancel nav map feed task.


## `anki_vector.objects`
- Module description: Object and Light Cube recognition.

### Classes and methods
#### Class `EvtObjectObserved`
- Access method: `anki_vector.objects.EvtObjectObserved`
- Description: Triggered whenever an object is visually identified by the robot.
- Public methods: none

#### Class `EvtObjectAppeared`
- Access method: `anki_vector.objects.EvtObjectAppeared`
- Description: Triggered whenever an object is first visually identified by a robot.
- Public methods: none

#### Class `EvtObjectDisappeared`
- Access method: `anki_vector.objects.EvtObjectDisappeared`
- Description: Triggered whenever an object that was previously being observed is no longer visible.
- Public methods: none

#### Class `EvtObjectFinishedMove`
- Access method: `anki_vector.objects.EvtObjectFinishedMove`
- Description: Triggered when an active object stops moving.
- Public methods: none

#### Class `ObservableObject`
- Access method: `anki_vector.objects.ObservableObject`
- Description: The base type for anything Vector can see.
- Public methods:
  - `pose(self) -> util.Pose`
    - Access method: `observableobject.pose(...)` *(or via component property on `Robot` when applicable)*
    - Description: The pose of this object in the world.
  - `last_event_time(self) -> float`
    - Access method: `observableobject.last_event_time(...)` *(or via component property on `Robot` when applicable)*
    - Description: Time this object last received an event from Vector.
  - `last_observed_time(self) -> float`
    - Access method: `observableobject.last_observed_time(...)` *(or via component property on `Robot` when applicable)*
    - Description: Time this object was last seen.
  - `last_observed_robot_timestamp(self) -> int`
    - Access method: `observableobject.last_observed_robot_timestamp(...)` *(or via component property on `Robot` when applicable)*
    - Description: Time this object was last seen according to Vector's time.
  - `time_since_last_seen(self) -> float`
    - Access method: `observableobject.time_since_last_seen(...)` *(or via component property on `Robot` when applicable)*
    - Description: Time since this object was last seen. math.inf if never seen.
  - `last_observed_image_rect(self) -> util.ImageRect`
    - Access method: `observableobject.last_observed_image_rect(...)` *(or via component property on `Robot` when applicable)*
    - Description: The location in 2d camera space where this object was last seen.
  - `is_visible(self) -> bool`
    - Access method: `observableobject.is_visible(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if the element has been observed recently, False otherwise.

#### Class `LightCube`
- Access method: `anki_vector.objects.LightCube`
- Description: Represents Vector's Cube.
- Public methods:
  - `teardown(self)`
    - Access method: `lightcube.teardown(...)` *(or via component property on `Robot` when applicable)*
    - Description: All faces will be torn down by the world when no longer needed.
  - `set_light_corners(self, light1: lights.Light, light2: lights.Light, light3: lights.Light, light4: lights.Light, color_profile: lights.ColorProfile=lights.WHITE_BALANCED_CUBE_PROFILE)`
    - Access method: `lightcube.set_light_corners(...)` *(or via component property on `Robot` when applicable)*
    - Description: Set the light for each corner.
  - `set_lights(self, light: lights.Light, color_profile: lights.ColorProfile=lights.WHITE_BALANCED_CUBE_PROFILE)`
    - Access method: `lightcube.set_lights(...)` *(or via component property on `Robot` when applicable)*
    - Description: Set all lights on the cube
  - `set_lights_off(self, color_profile: lights.ColorProfile=lights.WHITE_BALANCED_CUBE_PROFILE)`
    - Access method: `lightcube.set_lights_off(...)` *(or via component property on `Robot` when applicable)*
    - Description: Set all lights off on the cube
  - `last_tapped_time(self) -> float`
    - Access method: `lightcube.last_tapped_time(...)` *(or via component property on `Robot` when applicable)*
    - Description: The time the object was last tapped in SDK time.
  - `last_tapped_robot_timestamp(self) -> float`
    - Access method: `lightcube.last_tapped_robot_timestamp(...)` *(or via component property on `Robot` when applicable)*
    - Description: The time the object was last tapped in robot time.
  - `last_moved_time(self) -> float`
    - Access method: `lightcube.last_moved_time(...)` *(or via component property on `Robot` when applicable)*
    - Description: The time the object was last moved in SDK time.
  - `last_moved_robot_timestamp(self) -> float`
    - Access method: `lightcube.last_moved_robot_timestamp(...)` *(or via component property on `Robot` when applicable)*
    - Description: The time the object was last moved in robot time.
  - `last_moved_start_time(self) -> float`
    - Access method: `lightcube.last_moved_start_time(...)` *(or via component property on `Robot` when applicable)*
    - Description: The time the object most recently started moving in SDK time.
  - `last_moved_start_robot_timestamp(self) -> float`
    - Access method: `lightcube.last_moved_start_robot_timestamp(...)` *(or via component property on `Robot` when applicable)*
    - Description: The time the object more recently started moving in robot time.
  - `last_up_axis_changed_time(self) -> float`
    - Access method: `lightcube.last_up_axis_changed_time(...)` *(or via component property on `Robot` when applicable)*
    - Description: The time the object's orientation last changed in SDK time.
  - `last_up_axis_changed_robot_timestamp(self) -> float`
    - Access method: `lightcube.last_up_axis_changed_robot_timestamp(...)` *(or via component property on `Robot` when applicable)*
    - Description: Time the object's orientation last changed in robot time.
  - `up_axis(self) -> protocol.UpAxis`
    - Access method: `lightcube.up_axis(...)` *(or via component property on `Robot` when applicable)*
    - Description: The object's up_axis value from the last time it changed.
  - `is_moving(self) -> bool`
    - Access method: `lightcube.is_moving(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if the cube's accelerometer indicates that the cube is moving.
  - `is_connected(self) -> bool`
    - Access method: `lightcube.is_connected(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if the cube is currently connected to the robot.
  - `top_face_orientation_rad(self) -> float`
    - Access method: `lightcube.top_face_orientation_rad(...)` *(or via component property on `Robot` when applicable)*
    - Description: Angular distance from the current reported up axis.
  - `factory_id(self) -> str`
    - Access method: `lightcube.factory_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: The unique hardware id of the physical cube.
  - `factory_id(self, value: str)`
    - Access method: `lightcube.factory_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `descriptive_name(self) -> str`
    - Access method: `lightcube.descriptive_name(...)` *(or via component property on `Robot` when applicable)*
    - Description: A descriptive name for this ObservableObject instance.
  - `object_id(self) -> int`
    - Access method: `lightcube.object_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: The internal ID assigned to the object.
  - `object_id(self, value: str)`
    - Access method: `lightcube.object_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_

#### Class `Charger`
- Access method: `anki_vector.objects.Charger`
- Description: Vector's charger object, which the robot can observe and drive toward.
- Public methods:
  - `teardown(self)`
    - Access method: `charger.teardown(...)` *(or via component property on `Robot` when applicable)*
    - Description: All objects will be torn down by the world when the world closes.
  - `object_id(self) -> int`
    - Access method: `charger.object_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: The internal ID assigned to the object.
  - `object_id(self, value: str)`
    - Access method: `charger.object_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `descriptive_name(self) -> str`
    - Access method: `charger.descriptive_name(...)` *(or via component property on `Robot` when applicable)*
    - Description: A descriptive name for this ObservableObject instance.

#### Class `CustomObjectArchetype`
- Access method: `anki_vector.objects.CustomObjectArchetype`
- Description: An object archetype defined by the SDK. It is bound to a specific objectType e.g ``CustomType00``.
- Public methods:
  - `custom_type(self) -> protocol.CustomType`
    - Access method: `customobjectarchetype.custom_type(...)` *(or via component property on `Robot` when applicable)*
    - Description: id of this archetype on the robot.
  - `x_size_mm(self) -> float`
    - Access method: `customobjectarchetype.x_size_mm(...)` *(or via component property on `Robot` when applicable)*
    - Description: Size of this object in its X axis, in millimeters.
  - `y_size_mm(self) -> float`
    - Access method: `customobjectarchetype.y_size_mm(...)` *(or via component property on `Robot` when applicable)*
    - Description: Size of this object in its Y axis, in millimeters.
  - `z_size_mm(self) -> float`
    - Access method: `customobjectarchetype.z_size_mm(...)` *(or via component property on `Robot` when applicable)*
    - Description: Size of this object in its Z axis, in millimeters.
  - `marker_width_mm(self) -> float`
    - Access method: `customobjectarchetype.marker_width_mm(...)` *(or via component property on `Robot` when applicable)*
    - Description: Width in millimeters of the marker on this object.
  - `marker_height_mm(self) -> float`
    - Access method: `customobjectarchetype.marker_height_mm(...)` *(or via component property on `Robot` when applicable)*
    - Description: Height in millimeters of the marker on this object.
  - `is_unique(self) -> bool`
    - Access method: `customobjectarchetype.is_unique(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if there should only be one of this object type in the world.

#### Class `CustomObject`
- Access method: `anki_vector.objects.CustomObject`
- Description: An object defined by the SDK observed by the robot.  The object will
- Public methods:
  - `teardown(self)`
    - Access method: `customobject.teardown(...)` *(or via component property on `Robot` when applicable)*
    - Description: All objects will be torn down by the world when no longer needed.
  - `object_id(self) -> int`
    - Access method: `customobject.object_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: The internal ID assigned to the object.
  - `object_id(self, value: str)`
    - Access method: `customobject.object_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `archetype(self) -> CustomObjectArchetype`
    - Access method: `customobject.archetype(...)` *(or via component property on `Robot` when applicable)*
    - Description: Archetype defining this custom object's properties.
  - `descriptive_name(self) -> str`
    - Access method: `customobject.descriptive_name(...)` *(or via component property on `Robot` when applicable)*
    - Description: A descriptive name for this CustomObject instance.

#### Class `CustomObjectTypes`
- Access method: `anki_vector.objects.CustomObjectTypes`
- Description: Defines all available custom object types.
- Public methods: none

#### Class `CustomObjectMarkers`
- Access method: `anki_vector.objects.CustomObjectMarkers`
- Description: Defines all available custom object markers.
- Public methods: none

#### Class `FixedCustomObject`
- Access method: `anki_vector.objects.FixedCustomObject`
- Description: A fixed object defined by the SDK. It is given a pose and x,y,z sizes.
- Public methods:
  - `teardown(self)`
    - Access method: `fixedcustomobject.teardown(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `object_id(self) -> int`
    - Access method: `fixedcustomobject.object_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: The internal ID assigned to the object.
  - `object_id(self, value: int)`
    - Access method: `fixedcustomobject.object_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `pose(self) -> util.Pose`
    - Access method: `fixedcustomobject.pose(...)` *(or via component property on `Robot` when applicable)*
    - Description: The pose of the object in the world.
  - `x_size_mm(self) -> float`
    - Access method: `fixedcustomobject.x_size_mm(...)` *(or via component property on `Robot` when applicable)*
    - Description: The length of the object in its X axis, in millimeters.
  - `y_size_mm(self) -> float`
    - Access method: `fixedcustomobject.y_size_mm(...)` *(or via component property on `Robot` when applicable)*
    - Description: The length of the object in its Y axis, in millimeters.
  - `z_size_mm(self) -> float`
    - Access method: `fixedcustomobject.z_size_mm(...)` *(or via component property on `Robot` when applicable)*
    - Description: The length of the object in its Z axis, in millimeters.


## `anki_vector.photos`
- Module description: Photo related classes, functions, events and values.

### Classes and methods
#### Class `PhotographComponent`
- Access method: `anki_vector.photos.PhotographComponent`
- Description: Access the photos on Vector.
- Public methods:
  - `photo_info(self) -> List[protocol.PhotoInfo]`
    - Access method: `photographcomponent.photo_info(...)` *(or via component property on `Robot` when applicable)*
    - Description: The information about what photos are stored on Vector.
  - `load_photo_info(self) -> protocol.PhotosInfoResponse`
    - Access method: `photographcomponent.load_photo_info(...)` *(or via component property on `Robot` when applicable)*
    - Description: Request the photo information from the robot.
  - `get_photo(self, photo_id: int) -> protocol.PhotoResponse`
    - Access method: `photographcomponent.get_photo(...)` *(or via component property on `Robot` when applicable)*
    - Description: Download a full-resolution photo from the robot's storage.
  - `get_thumbnail(self, photo_id: int) -> protocol.ThumbnailResponse`
    - Access method: `photographcomponent.get_thumbnail(...)` *(or via component property on `Robot` when applicable)*
    - Description: Download a thumbnail of a given photo from the robot's storage.


## `anki_vector.proximity`
- Module description: Support for Vector's distance sensor.

### Classes and methods
#### Class `ProximitySensorData`
- Access method: `anki_vector.proximity.ProximitySensorData`
- Description: A distance sample from the time-of-flight sensor with metadata describing reliability of the measurement
- Public methods:
  - `distance(self) -> util.Distance`
    - Access method: `proximitysensordata.distance(...)` *(or via component property on `Robot` when applicable)*
    - Description: The distance between the sensor and a detected object
  - `signal_quality(self) -> float`
    - Access method: `proximitysensordata.signal_quality(...)` *(or via component property on `Robot` when applicable)*
    - Description: The quality of the detected object.
  - `unobstructed(self) -> bool`
    - Access method: `proximitysensordata.unobstructed(...)` *(or via component property on `Robot` when applicable)*
    - Description: The sensor has confirmed it has not detected anything up to its max range.
  - `found_object(self) -> bool`
    - Access method: `proximitysensordata.found_object(...)` *(or via component property on `Robot` when applicable)*
    - Description: The sensor detected an object in the valid operating range.
  - `is_lift_in_fov(self) -> bool`
    - Access method: `proximitysensordata.is_lift_in_fov(...)` *(or via component property on `Robot` when applicable)*
    - Description: Whether Vector's lift is blocking the time-of-flight sensor. While

#### Class `ProximityComponent`
- Access method: `anki_vector.proximity.ProximityComponent`
- Description: Maintains the most recent proximity sensor data
- Public methods:
  - `close(self)`
    - Access method: `proximitycomponent.close(...)` *(or via component property on `Robot` when applicable)*
    - Description: Closing the touch component will unsubscribe from robot state updates.
  - `last_sensor_reading(self) -> ProximitySensorData`
    - Access method: `proximitycomponent.last_sensor_reading(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`anki_vector.proximity.ProximitySensorData`: The last reported sensor data.


## `anki_vector.robot`
- Module description: This contains the :class:`Robot` and :class:`AsyncRobot` classes for managing Vector.

### Classes and methods
#### Class `Robot`
- Access method: `anki_vector.robot.Robot`
- Description: The Robot object is responsible for managing the state and connections
- Public methods:
  - `force_async(self) -> bool`
    - Access method: `robot.force_async(...)` *(or via component property on `Robot` when applicable)*
    - Description: A flag used to determine if this is a :class:`Robot` or :class:`AsyncRobot`.
  - `conn(self) -> Connection`
    - Access method: `robot.conn(...)` *(or via component property on `Robot` when applicable)*
    - Description: A reference to the :class:`~anki_vector.connection.Connection` instance.
  - `events(self) -> events.EventHandler`
    - Access method: `robot.events(...)` *(or via component property on `Robot` when applicable)*
    - Description: A reference to the :class:`~anki_vector.events.EventHandler` instance.
  - `anim(self) -> animation.AnimationComponent`
    - Access method: `robot.anim(...)` *(or via component property on `Robot` when applicable)*
    - Description: A reference to the :class:`~anki_vector.animation.AnimationComponent` instance.
  - `audio(self) -> audio.AudioComponent`
    - Access method: `robot.audio(...)` *(or via component property on `Robot` when applicable)*
    - Description: The audio instance used to control Vector's microphone feed and speaker playback.
  - `behavior(self) -> behavior.BehaviorComponent`
    - Access method: `robot.behavior(...)` *(or via component property on `Robot` when applicable)*
    - Description: A reference to the :class:`~anki_vector.behavior.BehaviorComponent` instance.
  - `camera(self) -> camera.CameraComponent`
    - Access method: `robot.camera(...)` *(or via component property on `Robot` when applicable)*
    - Description: The :class:`~anki_vector.camera.CameraComponent` instance used to control Vector's camera feed.
  - `faces(self) -> faces.FaceComponent`
    - Access method: `robot.faces(...)` *(or via component property on `Robot` when applicable)*
    - Description: A reference to the :class:`~anki_vector.faces.FaceComponent` instance.
  - `motors(self) -> motors.MotorComponent`
    - Access method: `robot.motors(...)` *(or via component property on `Robot` when applicable)*
    - Description: A reference to the :class:`~anki_vector.motors.MotorComponent` instance.
  - `nav_map(self) -> nav_map.NavMapComponent`
    - Access method: `robot.nav_map(...)` *(or via component property on `Robot` when applicable)*
    - Description: A reference to the :class:`~anki_vector.nav_map.NavMapComponent` instance.
  - `screen(self) -> screen.ScreenComponent`
    - Access method: `robot.screen(...)` *(or via component property on `Robot` when applicable)*
    - Description: A reference to the :class:`~anki_vector.screen.ScreenComponent` instance.
  - `photos(self) -> photos.PhotographComponent`
    - Access method: `robot.photos(...)` *(or via component property on `Robot` when applicable)*
    - Description: A reference to the :class:`~anki_vector.photos.PhotographComponent` instance.
  - `proximity(self) -> proximity.ProximityComponent`
    - Access method: `robot.proximity(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`~anki_vector.proximity.ProximityComponent` containing state related to object proximity detection.
  - `touch(self) -> touch.TouchComponent`
    - Access method: `robot.touch(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`~anki_vector.touch.TouchComponent` containing state related to object touch detection.
  - `viewer(self) -> ViewerComponent`
    - Access method: `robot.viewer(...)` *(or via component property on `Robot` when applicable)*
    - Description: The :class:`~anki_vector.viewer.ViewerComponent` instance used to render Vector's camera feed.
  - `viewer_3d(self) -> Viewer3DComponent`
    - Access method: `robot.viewer_3d(...)` *(or via component property on `Robot` when applicable)*
    - Description: The :class:`~anki_vector.viewer.Viewer3DComponent` instance used to render Vector's navigation map.
  - `vision(self) -> vision.VisionComponent`
    - Access method: `robot.vision(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`~anki_vector.vision.VisionComponent` containing functionality related to vision based object detection.
  - `world(self) -> world.World`
    - Access method: `robot.world(...)` *(or via component property on `Robot` when applicable)*
    - Description: A reference to the :class:`~anki_vector.world.World` instance, or None if the World is not yet initialized.
  - `pose(self) -> util.Pose`
    - Access method: `robot.pose(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`anki_vector.util.Pose`: The current pose (position and orientation) of Vector.
  - `pose_angle_rad(self) -> float`
    - Access method: `robot.pose_angle_rad(...)` *(or via component property on `Robot` when applicable)*
    - Description: Vector's pose angle (heading in X-Y plane).
  - `pose_pitch_rad(self) -> float`
    - Access method: `robot.pose_pitch_rad(...)` *(or via component property on `Robot` when applicable)*
    - Description: Vector's pose pitch (angle up/down).
  - `left_wheel_speed_mmps(self) -> float`
    - Access method: `robot.left_wheel_speed_mmps(...)` *(or via component property on `Robot` when applicable)*
    - Description: Vector's left wheel speed in mm/sec
  - `right_wheel_speed_mmps(self) -> float`
    - Access method: `robot.right_wheel_speed_mmps(...)` *(or via component property on `Robot` when applicable)*
    - Description: Vector's right wheel speed in mm/sec
  - `head_angle_rad(self) -> float`
    - Access method: `robot.head_angle_rad(...)` *(or via component property on `Robot` when applicable)*
    - Description: Vector's head angle (up/down).
  - `lift_height_mm(self) -> float`
    - Access method: `robot.lift_height_mm(...)` *(or via component property on `Robot` when applicable)*
    - Description: Height of Vector's lift from the ground.
  - `accel(self) -> util.Vector3`
    - Access method: `robot.accel(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`anki_vector.util.Vector3`: The current accelerometer reading (x, y, z)
  - `gyro(self) -> util.Vector3`
    - Access method: `robot.gyro(...)` *(or via component property on `Robot` when applicable)*
    - Description: The current gyroscope reading (x, y, z)
  - `carrying_object_id(self) -> int`
    - Access method: `robot.carrying_object_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: The ID of the object currently being carried (-1 if none)
  - `head_tracking_object_id(self) -> int`
    - Access method: `robot.head_tracking_object_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: The ID of the object the head is tracking to (-1 if none)
  - `localized_to_object_id(self) -> int`
    - Access method: `robot.localized_to_object_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: The ID of the object that the robot is localized to (-1 if none)
  - `last_image_time_stamp(self) -> int`
    - Access method: `robot.last_image_time_stamp(...)` *(or via component property on `Robot` when applicable)*
    - Description: The robot's timestamp for the last image seen.
  - `status(self) -> status.RobotStatus`
    - Access method: `robot.status(...)` *(or via component property on `Robot` when applicable)*
    - Description: A property that exposes various status properties of the robot.
  - `enable_audio_feed(self) -> bool`
    - Access method: `robot.enable_audio_feed(...)` *(or via component property on `Robot` when applicable)*
    - Description: The audio feed enabled/disabled
  - `enable_audio_feed(self, enable) -> None`
    - Access method: `robot.enable_audio_feed(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `connect(self, timeout: int=10) -> None`
    - Access method: `robot.connect(...)` *(or via component property on `Robot` when applicable)*
    - Description: Start the connection to Vector.
  - `disconnect(self) -> None`
    - Access method: `robot.disconnect(...)` *(or via component property on `Robot` when applicable)*
    - Description: Close the connection with Vector.
  - `get_battery_state(self) -> protocol.BatteryStateResponse`
    - Access method: `robot.get_battery_state(...)` *(or via component property on `Robot` when applicable)*
    - Description: Check the current state of the robot and cube batteries.
  - `get_version_state(self) -> protocol.VersionStateResponse`
    - Access method: `robot.get_version_state(...)` *(or via component property on `Robot` when applicable)*
    - Description: Get the versioning information for Vector, including Vector's os_version and engine_build_id.

#### Class `AsyncRobot`
- Access method: `anki_vector.robot.AsyncRobot`
- Description: The AsyncRobot object is just like the Robot object, but allows multiple commands
- Public methods: none


## `anki_vector.screen`
- Module description: Vector's LCD Screen that displays his face.

### Module-level functions
#### `dimensions()`
- Access method: `anki_vector.screen.dimensions(...)`
- Description: Return the dimension (width, height) of the Screen.
- Returns details:
  - A tuple of ints (width, height)

#### `convert_pixels_to_screen_data(pixel_data: list, image_width: int, image_height: int)`
- Access method: `anki_vector.screen.convert_pixels_to_screen_data(...)`
- Description: Convert a sequence of pixel data to the correct format to display on Vector's face.
- Returns details:
  - A :class:`bytes` object representing all of the pixels (16bit color in rgb565 format)

#### `convert_image_to_screen_data(pil_image: Image.Image)`
- Access method: `anki_vector.screen.convert_image_to_screen_data(...)`
- Description: Convert an image into the correct format to display on Vector's face.
- Returns details:
  - A :class:`bytes` object representing all of the pixels (16bit color in rgb565 format)

### Classes and methods
#### Class `ScreenComponent`
- Access method: `anki_vector.screen.ScreenComponent`
- Description: Handles messaging to control Vector's screen
- Public methods:
  - `set_screen_with_image_data(self, image_data: bytes, duration_sec: float, interrupt_running: bool=True)`
    - Access method: `screencomponent.set_screen_with_image_data(...)` *(or via component property on `Robot` when applicable)*
    - Description: Display an image on Vector's Screen (his "face").
  - `set_screen_to_color(self, solid_color: color.Color, duration_sec: float, interrupt_running: bool=True)`
    - Access method: `screencomponent.set_screen_to_color(...)` *(or via component property on `Robot` when applicable)*
    - Description: Set Vector's Screen (his "face"). to a solid color.


## `anki_vector.status`
- Module description: .. _status:

### Classes and methods
#### Class `RobotStatus`
- Access method: `anki_vector.status.RobotStatus`
- Description: A class to expose various status properties of the robot.
- Public methods:
  - `set(self, status: int)`
    - Access method: `robotstatus.set(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `are_motors_moving(self) -> bool`
    - Access method: `robotstatus.are_motors_moving(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector is currently moving any of his motors (head, arm or
  - `is_carrying_block(self) -> bool`
    - Access method: `robotstatus.is_carrying_block(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector is currently carrying a block.
  - `is_docking_to_marker(self) -> bool`
    - Access method: `robotstatus.is_docking_to_marker(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector has seen a marker and is actively heading toward it
  - `is_picked_up(self) -> bool`
    - Access method: `robotstatus.is_picked_up(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector is currently picked up (in the air).
  - `is_button_pressed(self) -> bool`
    - Access method: `robotstatus.is_button_pressed(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector's button is pressed.
  - `is_falling(self) -> bool`
    - Access method: `robotstatus.is_falling(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector is currently falling.
  - `is_animating(self) -> bool`
    - Access method: `robotstatus.is_animating(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector is currently playing an animation.
  - `is_pathing(self) -> bool`
    - Access method: `robotstatus.is_pathing(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector is currently traversing a path.
  - `is_lift_in_pos(self) -> bool`
    - Access method: `robotstatus.is_lift_in_pos(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector's arm is in the desired position (False if still
  - `is_head_in_pos(self) -> bool`
    - Access method: `robotstatus.is_head_in_pos(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector's head is in the desired position (False if still
  - `is_in_calm_power_mode(self) -> bool`
    - Access method: `robotstatus.is_in_calm_power_mode(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector is in calm power mode.  Calm power mode is generally
  - `is_on_charger(self) -> bool`
    - Access method: `robotstatus.is_on_charger(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector is currently on the charger.
  - `is_charging(self) -> bool`
    - Access method: `robotstatus.is_charging(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector is currently charging.
  - `is_cliff_detected(self) -> bool`
    - Access method: `robotstatus.is_cliff_detected(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector detected a cliff using any of his four cliff sensors.
  - `are_wheels_moving(self) -> bool`
    - Access method: `robotstatus.are_wheels_moving(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector's wheels/treads are currently moving.
  - `is_being_held(self) -> bool`
    - Access method: `robotstatus.is_being_held(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector is being held.
  - `is_robot_moving(self) -> bool`
    - Access method: `robotstatus.is_robot_moving(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if Vector is in motion.  This includes any of his motors


## `anki_vector.touch`
- Module description: Support for Vector's touch sensor.

### Classes and methods
#### Class `TouchSensorData`
- Access method: `anki_vector.touch.TouchSensorData`
- Description: A touch sample from the capacitive touch sensor, accompanied with the robot's
- Public methods:
  - `raw_touch_value(self) -> int`
    - Access method: `touchsensordata.raw_touch_value(...)` *(or via component property on `Robot` when applicable)*
    - Description: The detected sensitivity from the touch sensor.
  - `is_being_touched(self) -> bool`
    - Access method: `touchsensordata.is_being_touched(...)` *(or via component property on `Robot` when applicable)*
    - Description: The robot's conclusion on whether the current value is considered

#### Class `TouchComponent`
- Access method: `anki_vector.touch.TouchComponent`
- Description: Maintains the most recent touch sensor data
- Public methods:
  - `close(self)`
    - Access method: `touchcomponent.close(...)` *(or via component property on `Robot` when applicable)*
    - Description: Closing the touch component will unsubscribe from robot state updates.
  - `last_sensor_reading(self) -> TouchSensorData`
    - Access method: `touchcomponent.last_sensor_reading(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`anki_vector.touch.TouchSensorData`: The last reported sensor data.


## `anki_vector.user_intent`
- Module description: Class and enumeration related to voice commands received by Vector.

### Classes and methods
#### Class `UserIntentEvent`
- Access method: `anki_vector.user_intent.UserIntentEvent`
- Description: List of UserIntent events available to the SDK.
- Public methods: none

#### Class `UserIntent`
- Access method: `anki_vector.user_intent.UserIntent`
- Description: Class for containing voice command information from the event stream.
- Public methods:
  - `intent_event(self) -> UserIntentEvent`
    - Access method: `userintent.intent_event(...)` *(or via component property on `Robot` when applicable)*
    - Description: This returns the voice command event as a UserIntentEvent
  - `intent_data(self) -> str`
    - Access method: `userintent.intent_data(...)` *(or via component property on `Robot` when applicable)*
    - Description: This gives access to any voice command specific data in JSON format.


## `anki_vector.util`
- Module description: Utility functions and classes for the Vector SDK.

### Module-level functions
#### `parse_command_args(parser: argparse.ArgumentParser=None)`
- Access method: `anki_vector.util.parse_command_args(...)`
- Description: Parses command line arguments.

#### `block_while_none(interval: float=0.1, max_iterations: int=50)`
- Access method: `anki_vector.util.block_while_none(...)`
- Description: Use this to denote a property that may need some delay before it appears.

#### `setup_basic_logging(custom_handler: logging.Handler=None, general_log_level: str=None, target: object=None)`
- Access method: `anki_vector.util.setup_basic_logging(...)`
- Description: Helper to perform basic setup of the Python logger.

#### `get_class_logger(module: str, obj: object) -> logging.Logger`
- Access method: `anki_vector.util.get_class_logger(...)`
- Description: Helper to create logger for a given class (and module).

#### `angle_z_to_quaternion(angle_z: Angle)`
- Access method: `anki_vector.util.angle_z_to_quaternion(...)`
- Description: This function converts an angle in the z axis (Euler angle z component) to a quaternion.
- Returns details:
  - q0, q1, q2, q3 (float, float, float, float): A tuple with all the members
  - of a quaternion defined by angle_z.

#### `degrees(degrees: float) -> Angle`
- Access method: `anki_vector.util.degrees(...)`
- Description: An Angle instance set to the specified number of degrees.

#### `radians(radians: float) -> Angle`
- Access method: `anki_vector.util.radians(...)`
- Description: An Angle instance set to the specified number of radians.

#### `distance_mm(distance_mm: float)`
- Access method: `anki_vector.util.distance_mm(...)`
- Description: Returns an :class:`anki_vector.util.Distance` instance set to the specified number of millimeters.

#### `distance_inches(distance_inches: float)`
- Access method: `anki_vector.util.distance_inches(...)`
- Description: Returns an :class:`anki_vector.util.Distance` instance set to the specified number of inches.

#### `speed_mmps(speed_mmps: float)`
- Access method: `anki_vector.util.speed_mmps(...)`
- Description: :class:`anki_vector.util.Speed` instance set to the specified millimeters per second speed.

#### `read_configuration(serial: str, name: str, logger: logging.Logger) -> dict`
- Access method: `anki_vector.util.read_configuration(...)`
- Description: Open the default conf file, and read it into a :class:`configparser.ConfigParser`

### Classes and methods
#### Class `Vector2`
- Access method: `anki_vector.util.Vector2`
- Description: Represents a 2D Vector (type/units aren't specified).
- Public methods:
  - `set_to(self, rhs)`
    - Access method: `vector2.set_to(...)` *(or via component property on `Robot` when applicable)*
    - Description: Copy the x and y components of the given Vector2 instance.
  - `x(self) -> float`
    - Access method: `vector2.x(...)` *(or via component property on `Robot` when applicable)*
    - Description: The x component.
  - `y(self) -> float`
    - Access method: `vector2.y(...)` *(or via component property on `Robot` when applicable)*
    - Description: The y component.
  - `x_y(self)`
    - Access method: `vector2.x_y(...)` *(or via component property on `Robot` when applicable)*
    - Description: tuple (float, float): The X, Y elements of the Vector2 (x,y)

#### Class `Vector3`
- Access method: `anki_vector.util.Vector3`
- Description: Represents a 3D Vector (type/units aren't specified).
- Public methods:
  - `set_to(self, rhs)`
    - Access method: `vector3.set_to(...)` *(or via component property on `Robot` when applicable)*
    - Description: Copy the x, y and z components of the given Vector3 instance.
  - `x(self) -> float`
    - Access method: `vector3.x(...)` *(or via component property on `Robot` when applicable)*
    - Description: The x component.
  - `y(self) -> float`
    - Access method: `vector3.y(...)` *(or via component property on `Robot` when applicable)*
    - Description: The y component.
  - `z(self) -> float`
    - Access method: `vector3.z(...)` *(or via component property on `Robot` when applicable)*
    - Description: The z component.
  - `magnitude_squared(self) -> float`
    - Access method: `vector3.magnitude_squared(...)` *(or via component property on `Robot` when applicable)*
    - Description: float: The magnitude of the Vector3 instance
  - `magnitude(self) -> float`
    - Access method: `vector3.magnitude(...)` *(or via component property on `Robot` when applicable)*
    - Description: The magnitude of the Vector3 instance
  - `normalized(self)`
    - Access method: `vector3.normalized(...)` *(or via component property on `Robot` when applicable)*
    - Description: A Vector3 instance with the same direction and unit magnitude
  - `dot(self, other)`
    - Access method: `vector3.dot(...)` *(or via component property on `Robot` when applicable)*
    - Description: The dot product of this and another Vector3 instance
  - `cross(self, other)`
    - Access method: `vector3.cross(...)` *(or via component property on `Robot` when applicable)*
    - Description: The cross product of this and another Vector3 instance
  - `x_y_z(self)`
    - Access method: `vector3.x_y_z(...)` *(or via component property on `Robot` when applicable)*
    - Description: tuple (float, float, float): The X, Y, Z elements of the Vector3 (x,y,z)

#### Class `Angle`
- Access method: `anki_vector.util.Angle`
- Description: Represents an angle.
- Public methods:
  - `radians(self) -> float`
    - Access method: `angle.radians(...)` *(or via component property on `Robot` when applicable)*
    - Description: The angle in radians.
  - `degrees(self) -> float`
    - Access method: `angle.degrees(...)` *(or via component property on `Robot` when applicable)*
    - Description: The angle in degrees.
  - `abs_value(self)`
    - Access method: `angle.abs_value(...)` *(or via component property on `Robot` when applicable)*
    - Description: :class:`anki_vector.util.Angle`: The absolute value of the angle.

#### Class `Matrix44`
- Access method: `anki_vector.util.Matrix44`
- Description: A 4x4 Matrix for representing the rotation and/or position of an object in the world.
- Public methods:
  - `tabulated_string(self) -> str`
    - Access method: `matrix44.tabulated_string(...)` *(or via component property on `Robot` when applicable)*
    - Description: A multi-line string formatted with tabs to show the matrix contents.
  - `in_row_order(self)`
    - Access method: `matrix44.in_row_order(...)` *(or via component property on `Robot` when applicable)*
    - Description: tuple of 16 floats: The contents of the matrix in row order.
  - `in_column_order(self)`
    - Access method: `matrix44.in_column_order(...)` *(or via component property on `Robot` when applicable)*
    - Description: tuple of 16 floats: The contents of the matrix in column order.
  - `forward_xyz(self)`
    - Access method: `matrix44.forward_xyz(...)` *(or via component property on `Robot` when applicable)*
    - Description: tuple of 3 floats: The x,y,z components representing the matrix's forward vector.
  - `left_xyz(self)`
    - Access method: `matrix44.left_xyz(...)` *(or via component property on `Robot` when applicable)*
    - Description: tuple of 3 floats: The x,y,z components representing the matrix's left vector.
  - `up_xyz(self)`
    - Access method: `matrix44.up_xyz(...)` *(or via component property on `Robot` when applicable)*
    - Description: tuple of 3 floats: The x,y,z components representing the matrix's up vector.
  - `pos_xyz(self)`
    - Access method: `matrix44.pos_xyz(...)` *(or via component property on `Robot` when applicable)*
    - Description: tuple of 3 floats: The x,y,z components representing the matrix's position vector.
  - `set_forward(self, x: float, y: float, z: float)`
    - Access method: `matrix44.set_forward(...)` *(or via component property on `Robot` when applicable)*
    - Description: Set the x,y,z components representing the matrix's forward vector.
  - `set_left(self, x: float, y: float, z: float)`
    - Access method: `matrix44.set_left(...)` *(or via component property on `Robot` when applicable)*
    - Description: Set the x,y,z components representing the matrix's left vector.
  - `set_up(self, x: float, y: float, z: float)`
    - Access method: `matrix44.set_up(...)` *(or via component property on `Robot` when applicable)*
    - Description: Set the x,y,z components representing the matrix's up vector.
  - `set_pos(self, x: float, y: float, z: float)`
    - Access method: `matrix44.set_pos(...)` *(or via component property on `Robot` when applicable)*
    - Description: Set the x,y,z components representing the matrix's position vector.

#### Class `Quaternion`
- Access method: `anki_vector.util.Quaternion`
- Description: Represents the rotation of an object in the world.
- Public methods:
  - `q0(self) -> float`
    - Access method: `quaternion.q0(...)` *(or via component property on `Robot` when applicable)*
    - Description: The q0 (w) value of the quaternion.
  - `q1(self) -> float`
    - Access method: `quaternion.q1(...)` *(or via component property on `Robot` when applicable)*
    - Description: The q1 (i) value of the quaternion.
  - `q2(self) -> float`
    - Access method: `quaternion.q2(...)` *(or via component property on `Robot` when applicable)*
    - Description: The q2 (j) value of the quaternion.
  - `q3(self) -> float`
    - Access method: `quaternion.q3(...)` *(or via component property on `Robot` when applicable)*
    - Description: The q3 (k) value of the quaternion.
  - `angle_z(self) -> Angle`
    - Access method: `quaternion.angle_z(...)` *(or via component property on `Robot` when applicable)*
    - Description: An Angle instance representing the z Euler component of the object's rotation.
  - `q0_q1_q2_q3(self)`
    - Access method: `quaternion.q0_q1_q2_q3(...)` *(or via component property on `Robot` when applicable)*
    - Description: tuple of float: Contains all elements of the quaternion (q0,q1,q2,q3)
  - `to_matrix(self, pos_x: float=0.0, pos_y: float=0.0, pos_z: float=0.0)`
    - Access method: `quaternion.to_matrix(...)` *(or via component property on `Robot` when applicable)*
    - Description: Convert the Quaternion to a 4x4 matrix representing this rotation.
    - Returns details:
      - :class:`anki_vector.util.Matrix44`: A matrix representing this Quaternion's
      - rotation, with the provided position (which defaults to 0,0,0).

#### Class `Position`
- Access method: `anki_vector.util.Position`
- Description: Represents the position of an object in the world.
- Public methods: none

#### Class `Pose`
- Access method: `anki_vector.util.Pose`
- Description: Represents where an object is in the world.
- Public methods:
  - `position(self) -> Position`
    - Access method: `pose.position(...)` *(or via component property on `Robot` when applicable)*
    - Description: The position component of this pose.
  - `rotation(self) -> Quaternion`
    - Access method: `pose.rotation(...)` *(or via component property on `Robot` when applicable)*
    - Description: The rotation component of this pose.
  - `origin_id(self) -> int`
    - Access method: `pose.origin_id(...)` *(or via component property on `Robot` when applicable)*
    - Description: An ID maintained by the robot which represents which coordinate frame this pose is in.
  - `define_pose_relative_this(self, new_pose)`
    - Access method: `pose.define_pose_relative_this(...)` *(or via component property on `Robot` when applicable)*
    - Description: Creates a new pose such that new_pose's origin is now at the location of this pose.
    - Returns details:
      - A :class:`anki_vector.util.Pose` object for which the origin was this pose's origin.
  - `is_valid(self) -> bool`
    - Access method: `pose.is_valid(...)` *(or via component property on `Robot` when applicable)*
    - Description: True if this is a valid, usable pose.
  - `is_comparable(self, other_pose) -> bool`
    - Access method: `pose.is_comparable(...)` *(or via component property on `Robot` when applicable)*
    - Description: Checks whether these two poses are comparable.
    - Returns details:
      - True if the two poses are comparable, False otherwise.
  - `to_matrix(self) -> Matrix44`
    - Access method: `pose.to_matrix(...)` *(or via component property on `Robot` when applicable)*
    - Description: Convert the Pose to a Matrix44.
    - Returns details:
      - A matrix representing this Pose's position and rotation.
  - `to_proto_pose_struct(self) -> protocol.PoseStruct`
    - Access method: `pose.to_proto_pose_struct(...)` *(or via component property on `Robot` when applicable)*
    - Description: Converts the Pose into the robot's messaging pose format.

#### Class `ImageRect`
- Access method: `anki_vector.util.ImageRect`
- Description: Defines a bounding box within an image frame.
- Public methods:
  - `x_top_left(self) -> float`
    - Access method: `imagerect.x_top_left(...)` *(or via component property on `Robot` when applicable)*
    - Description: The top left x value of where the object was last visible within Vector's camera view.
  - `y_top_left(self) -> float`
    - Access method: `imagerect.y_top_left(...)` *(or via component property on `Robot` when applicable)*
    - Description: The top left y value of where the object was last visible within Vector's camera view.
  - `width(self) -> float`
    - Access method: `imagerect.width(...)` *(or via component property on `Robot` when applicable)*
    - Description: The width of the object from when it was last visible within Vector's camera view.
  - `height(self) -> float`
    - Access method: `imagerect.height(...)` *(or via component property on `Robot` when applicable)*
    - Description: The height of the object from when it was last visible within Vector's camera view.
  - `scale_by(self, scale_multiplier: Union[int, float]) -> None`
    - Access method: `imagerect.scale_by(...)` *(or via component property on `Robot` when applicable)*
    - Description: Scales the image rectangle by the multiplier provided.

#### Class `Distance`
- Access method: `anki_vector.util.Distance`
- Description: Represents a distance.
- Public methods:
  - `distance_mm(self) -> float`
    - Access method: `distance.distance_mm(...)` *(or via component property on `Robot` when applicable)*
    - Description: The distance in millimeters
  - `distance_inches(self) -> float`
    - Access method: `distance.distance_inches(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_

#### Class `Speed`
- Access method: `anki_vector.util.Speed`
- Description: Represents a speed.
- Public methods:
  - `speed_mmps(self: float) -> float`
    - Access method: `speed.speed_mmps(...)` *(or via component property on `Robot` when applicable)*
    - Description: The speed in millimeters per second (mmps).

#### Class `BaseOverlay`
- Access method: `anki_vector.util.BaseOverlay`
- Description: A base overlay is used as a base class for other forms of overlays that can be drawn on top of an image.
- Public methods:
  - `line_thickness(self) -> int`
    - Access method: `baseoverlay.line_thickness(...)` *(or via component property on `Robot` when applicable)*
    - Description: The thickness of the line being drawn.
  - `line_color(self) -> tuple`
    - Access method: `baseoverlay.line_color(...)` *(or via component property on `Robot` when applicable)*
    - Description: The color of the line to be drawn.

#### Class `RectangleOverlay`
- Access method: `anki_vector.util.RectangleOverlay`
- Description: A rectangle that can be drawn on top of a given image.
- Public methods:
  - `width(self) -> int`
    - Access method: `rectangleoverlay.width(...)` *(or via component property on `Robot` when applicable)*
    - Description: The width of the rectangle to be drawn.
  - `height(self) -> int`
    - Access method: `rectangleoverlay.height(...)` *(or via component property on `Robot` when applicable)*
    - Description: The height of the rectangle to be drawn.
  - `apply_overlay(self, image: Image.Image) -> None`
    - Access method: `rectangleoverlay.apply_overlay(...)` *(or via component property on `Robot` when applicable)*
    - Description: Draw a rectangle on top of the given image.

#### Class `Component`
- Access method: `anki_vector.util.Component`
- Description: Base class for all components.
- Public methods:
  - `robot(self)`
    - Access method: `component.robot(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `conn(self)`
    - Access method: `component.conn(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `force_async(self)`
    - Access method: `component.force_async(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `grpc_interface(self)`
    - Access method: `component.grpc_interface(...)` *(or via component property on `Robot` when applicable)*
    - Description: A direct reference to the connected aiogrpc interface.


## `anki_vector.version`
- Module description: _(none in source docstring)_


## `anki_vector.viewer`
- Module description: Displays camera feed from Vector's camera.

### Classes and methods
#### Class `ViewerComponent`
- Access method: `anki_vector.viewer.ViewerComponent`
- Description: This component opens a window and renders the images obtained from Vector's camera.
- Public methods:
  - `show(self, timeout: float=10.0, force_on_top: bool=True) -> None`
    - Access method: `viewercomponent.show(...)` *(or via component property on `Robot` when applicable)*
    - Description: Render a video stream using the images obtained from
  - `close(self) -> None`
    - Access method: `viewercomponent.close(...)` *(or via component property on `Robot` when applicable)*
    - Description: Stop rendering video of Vector's camera feed and close the viewer process.
  - `enqueue_frame(self, image: Image.Image)`
    - Access method: `viewercomponent.enqueue_frame(...)` *(or via component property on `Robot` when applicable)*
    - Description: Sends a frame to the viewer's rendering process. Sending `None` to the viewer

#### Class `Viewer3DComponent`
- Access method: `anki_vector.viewer.Viewer3DComponent`
- Description: This component opens a window and renders the a 3D view obtained from Vector's navigation map.
- Public methods:
  - `show(self, show_viewer_controls: bool=True)`
    - Access method: `viewer3dcomponent.show(...)` *(or via component property on `Robot` when applicable)*
    - Description: Spawns a background process that shows the navigation map in a 3D view.
  - `user_data_queue(self)`
    - Access method: `viewer3dcomponent.user_data_queue(...)` *(or via component property on `Robot` when applicable)*
    - Description: A queue to send custom data to the 3D viewer process.
  - `add_render_call(self, render_function: callable, *args)`
    - Access method: `viewer3dcomponent.add_render_call(...)` *(or via component property on `Robot` when applicable)*
    - Description: Allows external functions to be injected into the viewer process which
  - `close(self)`
    - Access method: `viewer3dcomponent.close(...)` *(or via component property on `Robot` when applicable)*
    - Description: Closes the background process showing the 3D view.
  - `connect_to_cube(self)`
    - Access method: `viewer3dcomponent.connect_to_cube(...)` *(or via component property on `Robot` when applicable)*
    - Description: Connect to light cube


## `anki_vector.vision`
- Module description: Utility methods for Vector's vision

### Classes and methods
#### Class `VisionComponent`
- Access method: `anki_vector.vision.VisionComponent`
- Description: VisionComponent exposes controls for the robot's internal image processing.
- Public methods:
  - `close(self)`
    - Access method: `visioncomponent.close(...)` *(or via component property on `Robot` when applicable)*
    - Description: Close all the running vision modes and wait for a response.
  - `detect_faces(self)`
    - Access method: `visioncomponent.detect_faces(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `detect_custom_objects(self)`
    - Access method: `visioncomponent.detect_custom_objects(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `detect_motion(self)`
    - Access method: `visioncomponent.detect_motion(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `display_camera_feed_on_face(self)`
    - Access method: `visioncomponent.display_camera_feed_on_face(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `disable_all_vision_modes(self)`
    - Access method: `visioncomponent.disable_all_vision_modes(...)` *(or via component property on `Robot` when applicable)*
    - Description: _(none)_
  - `enable_custom_object_detection(self, detect_custom_objects: bool=True)`
    - Access method: `visioncomponent.enable_custom_object_detection(...)` *(or via component property on `Robot` when applicable)*
    - Description: Enable custom object detection on the robot's camera.
  - `enable_face_detection(self, detect_faces: bool=True, estimate_expression: bool=False)`
    - Access method: `visioncomponent.enable_face_detection(...)` *(or via component property on `Robot` when applicable)*
    - Description: Enable face detection on the robot's camera
  - `enable_motion_detection(self, detect_motion: bool=True)`
    - Access method: `visioncomponent.enable_motion_detection(...)` *(or via component property on `Robot` when applicable)*
    - Description: Enable motion detection on the robot's camera
  - `enable_display_camera_feed_on_face(self, display_camera_feed_on_face: bool=True)`
    - Access method: `visioncomponent.enable_display_camera_feed_on_face(...)` *(or via component property on `Robot` when applicable)*
    - Description: Display the robot's camera feed on its face along with any detections (if enabled)


## `anki_vector.world`
- Module description: Vector's known view of his world.

### Classes and methods
#### Class `World`
- Access method: `anki_vector.world.World`
- Description: Represents the state of the world, as known to Vector.
- Public methods:
  - `all_objects(self)`
    - Access method: `world.all_objects(...)` *(or via component property on `Robot` when applicable)*
    - Description: generator: yields each object in the world.
    - Returns details:
      - A generator yielding :class:`anki_vector.faces.Face`, :class:`anki_vector.faces.LightCube`,
      - :class:`anki_vector.faces.Charger`, :class:`anki_vector.faces.CustomObject` and
      - :class:`anki_vector.faces.FixedCustomObject` instances.
  - `visible_faces(self) -> Iterable[faces.Face]`
    - Access method: `world.visible_faces(...)` *(or via component property on `Robot` when applicable)*
    - Description: generator: yields each face that Vector can currently see.
    - Returns details:
      - A generator yielding :class:`anki_vector.faces.Face` instances.
  - `custom_object_archetypes(self) -> Iterable[objects.CustomObjectArchetype]`
    - Access method: `world.custom_object_archetypes(...)` *(or via component property on `Robot` when applicable)*
    - Description: generator: yields each custom object archetype that Vector will look for.
    - Returns details:
      - A generator yielding CustomObjectArchetype instances
  - `visible_custom_objects(self) -> Iterable[objects.CustomObject]`
    - Access method: `world.visible_custom_objects(...)` *(or via component property on `Robot` when applicable)*
    - Description: generator: yields each custom object that Vector can currently see.
    - Returns details:
      - A generator yielding CustomObject instances
  - `visible_objects(self) -> Iterable[objects.ObservableObject]`
    - Access method: `world.visible_objects(...)` *(or via component property on `Robot` when applicable)*
    - Description: generator: yields each object that Vector can currently see.
    - Returns details:
      - A generator yielding Charger, LightCube and CustomObject instances
  - `connected_light_cube(self) -> objects.LightCube`
    - Access method: `world.connected_light_cube(...)` *(or via component property on `Robot` when applicable)*
    - Description: A light cube connected to Vector, if any.
  - `light_cube(self) -> objects.LightCube`
    - Access method: `world.light_cube(...)` *(or via component property on `Robot` when applicable)*
    - Description: Returns the vector light cube object, regardless of its connection status.
  - `charger(self) -> objects.Charger`
    - Access method: `world.charger(...)` *(or via component property on `Robot` when applicable)*
    - Description: Returns the most recently observed Vector charger object, or None if no chargers have been observed.
  - `close(self)`
    - Access method: `world.close(...)` *(or via component property on `Robot` when applicable)*
    - Description: The world will tear down all its faces and objects.
  - `get_object(self, object_id: int)`
    - Access method: `world.get_object(...)` *(or via component property on `Robot` when applicable)*
    - Description: Fetches an object instance with the given id.
  - `get_face(self, face_id: int) -> faces.Face`
    - Access method: `world.get_face(...)` *(or via component property on `Robot` when applicable)*
    - Description: Fetches a Face instance with the given id.
  - `connect_cube(self) -> protocol.ConnectCubeResponse`
    - Access method: `world.connect_cube(...)` *(or via component property on `Robot` when applicable)*
    - Description: Attempt to connect to a cube.
  - `disconnect_cube(self) -> protocol.DisconnectCubeResponse`
    - Access method: `world.disconnect_cube(...)` *(or via component property on `Robot` when applicable)*
    - Description: Requests a disconnection from the currently connected cube.
  - `flash_cube_lights(self) -> protocol.FlashCubeLightsResponse`
    - Access method: `world.flash_cube_lights(...)` *(or via component property on `Robot` when applicable)*
    - Description: Flash cube lights
  - `forget_preferred_cube(self) -> protocol.ForgetPreferredCubeResponse`
    - Access method: `world.forget_preferred_cube(...)` *(or via component property on `Robot` when applicable)*
    - Description: Forget preferred cube.
  - `set_preferred_cube(self, factory_id: str) -> protocol.SetPreferredCubeResponse`
    - Access method: `world.set_preferred_cube(...)` *(or via component property on `Robot` when applicable)*
    - Description: Set preferred cube.
  - `delete_custom_objects(self, delete_custom_marker_objects: bool=True, delete_fixed_custom_objects: bool=True, delete_custom_object_archetypes: bool=True)`
    - Access method: `world.delete_custom_objects(...)` *(or via component property on `Robot` when applicable)*
    - Description: Causes the robot to forget about custom objects it currently knows about.
  - `define_custom_box(self, custom_object_type: objects.CustomObjectTypes, marker_front: objects.CustomObjectMarkers, marker_back: objects.CustomObjectMarkers, marker_top: objects.CustomObjectMarkers, marker_bottom: objects.CustomObjectMarkers, marker_left: objects.CustomObjectMarkers, marker_right: objects.CustomObjectMarkers, depth_mm: float, width_mm: float, height_mm: float, marker_width_mm: float, marker_height_mm: float, is_unique: bool=True) -> objects.CustomObject`
    - Access method: `world.define_custom_box(...)` *(or via component property on `Robot` when applicable)*
    - Description: Defines a cuboid of custom size and binds it to a specific custom object type.
    - Returns details:
      - CustomObject instance with the specified dimensions.
      - This is None if the definition failed internally.
      - Note: No instances of this object are added to the world until they have been seen.
  - `define_custom_cube(self, custom_object_type: objects.CustomObjectTypes, marker: objects.CustomObjectMarkers, size_mm: float, marker_width_mm: float, marker_height_mm: float, is_unique: bool=True) -> objects.CustomObject`
    - Access method: `world.define_custom_cube(...)` *(or via component property on `Robot` when applicable)*
    - Description: Defines a cube of custom size and binds it to a specific custom object type.
    - Returns details:
      - CustomObject instance with the specified dimensions.
      - This is None if the definition failed internally.
      - Note: No instances of this object are added to the world until they have been seen.
  - `define_custom_wall(self, custom_object_type: objects.CustomObjectTypes, marker: objects.CustomObjectMarkers, width_mm: float, height_mm: float, marker_width_mm: float, marker_height_mm: float, is_unique: bool=True) -> objects.CustomObject`
    - Access method: `world.define_custom_wall(...)` *(or via component property on `Robot` when applicable)*
    - Description: Defines a wall of custom width and height, with a fixed depth of 10mm, and binds it to a specific custom object type.
    - Returns details:
      - CustomObject instance with the specified dimensions.
      - This is None if the definition failed internally.
      - Note: No instances of this object are added to the world until they have been seen.
  - `create_custom_fixed_object(self, pose: util.Pose, x_size_mm: float, y_size_mm: float, z_size_mm: float, relative_to_robot: bool=False, use_robot_origin: bool=True) -> objects.FixedCustomObject`
    - Access method: `world.create_custom_fixed_object(...)` *(or via component property on `Robot` when applicable)*
    - Description: Defines a cuboid of custom size and places it in the world. It cannot be observed.
    - Returns details:
      - FixedCustomObject instance with the specified dimensions and pose.


