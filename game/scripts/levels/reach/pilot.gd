extends CharacterBody3D
# Neutral first-person test rig. No hero identity or asset is implied.
var camera := Camera3D.new()
var pitch := -0.055
var touch_move := Vector2.ZERO
var look_finger := -1
var jump_queued := false

func _ready() -> void:
    var col := CollisionShape3D.new()
    var shape := CapsuleShape3D.new()
    shape.radius = 0.36
    shape.height = 1.7
    col.shape = shape
    col.position.y = 0.85
    add_child(col)
    add_child(camera)
    camera.position.y = 1.58
    camera.fov = 74
    camera.rotation.x = pitch
    camera.current = true
    floor_snap_length = 0.3
    var module := MeshInstance3D.new()
    var prism := CylinderMesh.new()
    prism.radial_segments = 6
    prism.top_radius = 0.055
    prism.bottom_radius = 0.085
    prism.height = 0.44
    module.mesh = prism
    module.position = Vector3(0.25,-0.21,-0.42)
    module.rotation.x = PI/2.0
    var casing := StandardMaterial3D.new()
    casing.albedo_color = Color("696577")
    casing.metallic = 0.4
    module.material_override = casing
    camera.add_child(module)
    var lens := MeshInstance3D.new()
    var orb := SphereMesh.new()
    orb.radius = 0.047
    orb.height = 0.094
    lens.mesh = orb
    lens.position = Vector3(0.25,-0.16,-0.55)
    var light := StandardMaterial3D.new()
    light.albedo_color = Color("9ce5dc")
    light.emission_enabled = true
    light.emission = Color("9ce5dc")
    lens.material_override = light
    camera.add_child(lens)

func look(dx: float, dy: float) -> void:
    rotate_y(-dx)
    pitch = clampf(pitch-dy,-1.35,1.35)
    camera.rotation.x = pitch

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
        look(event.relative.x*0.0023,event.relative.y*0.0023)
    elif event is InputEventScreenTouch:
        if event.pressed and event.position.x > get_viewport().size.x*0.48 and look_finger < 0:
            look_finger = event.index
        elif not event.pressed and event.index == look_finger:
            look_finger = -1
    elif event is InputEventScreenDrag and event.index == look_finger:
        look(event.relative.x*0.004,event.relative.y*0.004)
    elif event is InputEventKey and event.keycode == KEY_SPACE and event.pressed and not event.echo:
        jump_queued = true

func _physics_process(dt: float) -> void:
    var axis := Vector2(float(Input.is_physical_key_pressed(KEY_D))-float(Input.is_physical_key_pressed(KEY_A)),float(Input.is_physical_key_pressed(KEY_S))-float(Input.is_physical_key_pressed(KEY_W))) + touch_move
    var dir := transform.basis*Vector3(axis.x,0,axis.y).limit_length(1.0)
    var speed := 8.0 if Input.is_physical_key_pressed(KEY_SHIFT) else 5.8
    velocity.x = dir.x*speed
    velocity.z = dir.z*speed
    if is_on_floor() and jump_queued: velocity.y = 6.3
    jump_queued = false
    velocity.y -= 18.0*dt
    var yaw_input := float(Input.is_physical_key_pressed(KEY_RIGHT))-float(Input.is_physical_key_pressed(KEY_LEFT))
    var pitch_input := float(Input.is_physical_key_pressed(KEY_DOWN))-float(Input.is_physical_key_pressed(KEY_UP))
    look(yaw_input*1.6*dt,pitch_input*1.4*dt)
    move_and_slide()
