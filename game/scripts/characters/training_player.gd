extends CharacterBody3D
## Temporary geometry-only test pilot. This is not an approved AETHERFALL hero.
## Touch, keyboard/mouse and joypad all feed the same gameplay methods.

signal training_hit(total_hits: int)

const WALK_SPEED := 6.5
const JUMP_SPEED := 6.8
const FALL_ACCELERATION := 22.0
const FIRE_INTERVAL := 0.18
const DASH_RECHARGE := 2.0

var touch_move := Vector2.ZERO
var touch_actions: Dictionary = {}
var shots_fired := 0
var targets_hit := 0
var dash_cooldown := 0.0

var _camera: Camera3D
var _pitch := 0.0
var _fire_timer := 0.0
var _dash_time := 0.0
var _jump_was_down := false
var _dash_was_down := false


func _ready() -> void:
    collision_layer = 2
    collision_mask = 1
    var capsule := CapsuleShape3D.new()
    capsule.height = 1.8
    capsule.radius = 0.38
    var collision := CollisionShape3D.new()
    collision.shape = capsule
    add_child(collision)

    _camera = Camera3D.new()
    _camera.name = "PlayerCamera"
    _camera.position = Vector3(0.0, 0.61, 0.0)
    _camera.fov = 78.0
    _camera.current = true
    add_child(_camera)

    if not OS.has_feature("mobile") and DisplayServer.get_name() != "headless":
        Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func set_touch_move(axis: Vector2) -> void:
    touch_move = axis.limit_length(1.0)


func set_touch_action(action: String, pressed: bool) -> void:
    if action in ["fire", "jump", "dash", "aim"]:
        touch_actions[action] = pressed


func apply_look(delta_pixels: Vector2) -> void:
    rotation.y -= delta_pixels.x * 0.004
    _pitch = clampf(_pitch - delta_pixels.y * 0.004, -1.34, 1.34)
    if is_instance_valid(_camera):
        _camera.rotation.x = _pitch


func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
        apply_look(event.relative)
    elif event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_ESCAPE:
        Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
    elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        if Input.mouse_mode == Input.MOUSE_MODE_VISIBLE and not OS.has_feature("mobile"):
            Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _physics_process(delta: float) -> void:
    var gamepad := _connected_pad()
    var moving := _movement_axis(gamepad)
    var planar := transform.basis * Vector3(moving.x, 0.0, moving.y)
    planar.y = 0.0
    if planar.length_squared() > 1.0:
        planar = planar.normalized()

    if gamepad >= 0:
        var aim := Vector2(Input.get_joy_axis(gamepad, JOY_AXIS_RIGHT_X), Input.get_joy_axis(gamepad, JOY_AXIS_RIGHT_Y))
        if aim.length() > 0.18:
            apply_look(aim * 450.0 * delta)

    dash_cooldown = maxf(0.0, dash_cooldown - delta)
    _fire_timer = maxf(0.0, _fire_timer - delta)
    _dash_time = maxf(0.0, _dash_time - delta)

    var dash_down := _action_down("dash", gamepad)
    if dash_down and not _dash_was_down and dash_cooldown <= 0.0 and moving.length() > 0.1:
        _dash_time = 0.25
        dash_cooldown = DASH_RECHARGE
    _dash_was_down = dash_down

    var speed := WALK_SPEED * (2.3 if _dash_time > 0.0 else 1.0)
    velocity.x = planar.x * speed
    velocity.z = planar.z * speed

    if is_on_floor():
        if velocity.y < 0.0:
            velocity.y = 0.0
    else:
        velocity.y -= FALL_ACCELERATION * delta

    var jump_down := _action_down("jump", gamepad)
    if jump_down and not _jump_was_down and is_on_floor():
        velocity.y = JUMP_SPEED
    _jump_was_down = jump_down

    move_and_slide()

    if _action_down("fire", gamepad) and _fire_timer <= 0.0:
        _fire_timer = FIRE_INTERVAL
        fire_once()

    _camera.fov = lerpf(_camera.fov, 57.0 if _action_down("aim", gamepad) else 78.0, minf(1.0, delta * 10.0))


func fire_once() -> void:
    ## Physics-ray target check. No network authority, ammo or hero damage yet.
    shots_fired += 1
    var origin := _camera.global_position
    var endpoint := origin - _camera.global_transform.basis.z * 85.0
    var query := PhysicsRayQueryParameters3D.create(origin, endpoint, 1, [get_rid()])
    var hit := get_world_3d().direct_space_state.intersect_ray(query)
    if hit.has("collider") and is_instance_valid(hit["collider"]):
        var object: Object = hit["collider"]
        if object.has_method("take_hit"):
            object.call("take_hit")
            targets_hit += 1
            training_hit.emit(targets_hit)


func _movement_axis(gamepad: int) -> Vector2:
    if touch_move.length() > 0.02:
        return touch_move.limit_length(1.0)

    var keys := Vector2(
        int(Input.is_key_pressed(KEY_D)) - int(Input.is_key_pressed(KEY_A)),
        int(Input.is_key_pressed(KEY_S)) - int(Input.is_key_pressed(KEY_W))
    )
    if keys.length_squared() > 0.0:
        return keys.normalized()

    if gamepad >= 0:
        var stick := Vector2(Input.get_joy_axis(gamepad, JOY_AXIS_LEFT_X), Input.get_joy_axis(gamepad, JOY_AXIS_LEFT_Y))
        if stick.length() > 0.17:
            return stick.limit_length(1.0)
    return Vector2.ZERO


func _action_down(action: String, gamepad: int) -> bool:
    if touch_actions.get(action, false):
        return true
    match action:
        "fire":
            return Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) or (gamepad >= 0 and Input.get_joy_axis(gamepad, JOY_AXIS_TRIGGER_RIGHT) > 0.55)
        "jump":
            return Input.is_key_pressed(KEY_SPACE) or (gamepad >= 0 and Input.is_joy_button_pressed(gamepad, JOY_BUTTON_A))
        "dash":
            return Input.is_key_pressed(KEY_SHIFT) or (gamepad >= 0 and Input.is_joy_button_pressed(gamepad, JOY_BUTTON_B))
        "aim":
            return Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) or (gamepad >= 0 and Input.is_joy_button_pressed(gamepad, JOY_BUTTON_LEFT_SHOULDER))
    return false


func _connected_pad() -> int:
    var pads := Input.get_connected_joypads()
    if pads.is_empty():
        return -1
    return pads[0]


func _exit_tree() -> void:
    if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
        Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
