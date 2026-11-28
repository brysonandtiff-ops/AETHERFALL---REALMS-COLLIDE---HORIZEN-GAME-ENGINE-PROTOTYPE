extends Node3D
# AF-RANGE-001: one repeatable local training trial, no hero canon changes.
const Valley = preload("res://scripts/levels/reach/valley.gd")
const Pilot = preload("res://scripts/levels/reach/pilot.gd")
const Interface = preload("res://scripts/levels/reach/hud.gd")
const Gallery = preload("res://scripts/levels/reach/target_gallery.gd")
const RIGS := ["WARDEN", "STRIKER", "MENDER"]
const TEAL := Color("72e7cf")
const RED := Color("fa775e")
var valley := Valley.new()
var pilot := Pilot.new()
var hud := Interface.new()
var gallery := Gallery.new()
var ally := Node3D.new()
var ally_core: MeshInstance3D
var ward: MeshInstance3D
var drones: Array[StaticBody3D] = []
var charge: Array[float] = [0.75,1.35]
var disabled: Array[float] = [0.0,0.0]
var integrity: Array[int] = [3,3]
var mode := 0
var phase := "READY"
var checkpoint := Vector3(0,0.04,12.2)
var heading := 0.0
var saved_pitch := -0.055
var ally_hp := 100
var prevented := 0
var restored := 0
var shots := 0
var hits := 0
var elapsed := 0.0
var fire_delay := 0.0
var pulse_delay := 0.0
var clock := 0.0
var touch_guard := false
var message := "Follow the teal courier across the bridge."
var last_result := "No completed trial"

func _ready() -> void:
    add_child(valley)
    valley.build()
    var env := Environment.new()
    env.background_mode = Environment.BG_SKY
    env.sky = Sky.new()
    var sky_mat := ProceduralSkyMaterial.new()
    sky_mat.sky_top_color = Color("374368")
    sky_mat.sky_horizon_color = Color("d6a28b")
    sky_mat.ground_horizon_color = Color("bd998f")
    sky_mat.ground_bottom_color = Color("3d3d51")
    env.sky.sky_material = sky_mat
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color("c0c4d6")
    env.ambient_light_energy = 0.72
    env.fog_enabled = true
    env.fog_light_color = Color("afa2b3")
    env.fog_density = 0.006
    var atmosphere := WorldEnvironment.new()
    atmosphere.environment = env
    add_child(atmosphere)
    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-43,-37,0)
    sun.light_color = Color("ffddaa")
    sun.light_energy = 1.5
    sun.shadow_enabled = true
    sun.directional_shadow_max_distance = 55
    add_child(sun)
    pilot.name = "TestRig"
    add_child(pilot)
    ally.name = "Courier"
    add_child(ally)
    ally_core = gem(ally,0.53,TEAL)
    ring(ally,0.69,TEAL)
    ward = ring(ally,1.17,Color("b0f7ff"))
    for n in range(2):
        var body := StaticBody3D.new()
        body.name = "Sentry%d" % n
        drones.append(body)
        add_child(body)
        var col := CollisionShape3D.new()
        var sphere := SphereShape3D.new()
        sphere.radius = 0.9
        col.shape = sphere
        body.add_child(col)
        gem(body,0.75,RED)
        ring(body,1.04,GOLD_COLOR())
    add_child(gallery)
    add_child(hud)
    hud.setup(self)
    reset_trial()

func GOLD_COLOR() -> Color:
    return Color("e4af75")

func gem(parent: Node3D, radius: float, tint: Color) -> MeshInstance3D:
    var core := MeshInstance3D.new()
    var s := SphereMesh.new()
    s.radius = radius
    s.height = radius*2.38
    s.radial_segments = 5
    s.rings = 2
    core.mesh = s
    core.material_override = valley.mat(tint,true)
    parent.add_child(core)
    return core

func ring(parent: Node3D, radius: float, tint: Color) -> MeshInstance3D:
    var rim := MeshInstance3D.new()
    var t := TorusMesh.new()
    t.inner_radius = radius*0.94
    t.outer_radius = radius
    t.rings = 28
    t.ring_segments = 6
    rim.mesh = t
    rim.material_override = valley.mat(tint,true)
    parent.add_child(rim)
    return rim

func switch_rig(n: int) -> void:
    if phase == "RUNNING":
        message = "Reset the trial before changing your rig."
        return
    mode = clampi(n,0,2)
    message = ["Hold E near the courier to absorb incoming hits.","Aim and fire. E fires a heavy disruptor shot.","Press E near the courier to repair its core."][mode]

func reset_trial() -> void:
    phase = "READY"
    ally_hp = 100
    prevented = 0
    restored = 0
    shots = 0
    hits = 0
    elapsed = 0
    clock = 0
    pulse_delay = 0
    fire_delay = 0
    touch_guard = false
    for i in range(2):
        charge[i] = 0.75+i*0.60
        disabled[i] = 0.0
        integrity[i] = 3
        drones[i].visible = true
    ally.visible = true
    ward.visible = false
    gallery.reset()
    ally.position = Vector3(0,1.05,8)
    place_drones()
    recover()
    message = "F begins the crossing. Explore freely before starting."
    hud.refresh(self)

func recover() -> void:
    pilot.position = checkpoint
    pilot.rotation.y = heading
    pilot.pitch = saved_pitch
    pilot.camera.rotation.x = saved_pitch
    pilot.velocity = Vector3.ZERO
    pilot.touch_move = Vector2.ZERO

func start_trial() -> void:
    if phase != "READY": return
    phase = "RUNNING"
    elapsed = 0
    clock = 0
    message = ["Stay within 7 m of the courier and hold E.","Disable the red sentries before they fire.","Stay close and pulse E to repair the courier."][mode]

func save_checkpoint() -> void:
    if phase != "READY" or not pilot.is_on_floor() or pilot.position.y < -0.1:
        message = "Save a checkpoint on solid ground between trials."
        return
    checkpoint = pilot.position
    heading = pilot.rotation.y
    saved_pitch = pilot.pitch
    message = "Position saved. R now replays from this spot."

func place_drones() -> void:
    for i in range(2):
        drones[i].position = Vector3((-1.0 if i == 0 else 1.0)*(7.0+0.8*sin(clock*0.85+i)),3.1+0.55*cos(clock*1.3+i),-2.0-i*5.0+2.6*sin(clock*0.61+i))
        drones[i].rotation.y = clock*0.8

func beam(a: Vector3,b: Vector3,tint: Color) -> void:
    var length := a.distance_to(b)
    if length < 0.05: return
    var m := MeshInstance3D.new()
    var shape := BoxMesh.new()
    shape.size = Vector3(0.035,0.035,length)
    m.mesh = shape
    m.material_override = valley.mat(tint,true)
    m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
    add_child(m)
    m.global_position = (a+b)*0.5
    m.look_at(b,Vector3.UP if absf((a-b).normalized().y)<0.98 else Vector3.RIGHT)
    var tw := create_tween()
    tw.tween_interval(0.14)
    tw.tween_callback(m.queue_free)

func fire(heavy: bool = false) -> void:
    if fire_delay > 0: return
    fire_delay = 0.2 if mode == 1 else 0.4
    shots += 1
    var start := pilot.camera.global_position
    var end := start-pilot.camera.global_transform.basis.z*85.0
    var query := PhysicsRayQueryParameters3D.create(start,end)
    query.exclude = [pilot.get_rid()]
    var hit: Dictionary = get_world_3d().direct_space_state.intersect_ray(query)
    if not hit.is_empty():
        end = hit.position
        var idx := drones.find(hit.collider)
        if idx >= 0 and disabled[idx] <= 0.0:
            hits += 1
            integrity[idx] -= 3 if heavy else 1
            if integrity[idx] <= 0:
                disabled[idx] = 5.0
                drones[idx].visible = false
                message = "Sentry disabled for 5 seconds."
            else: message = "Sentry hit."
        elif gallery.hit(hit.collider):
            hits += 1
            message = "Target track: %d hits, %d knockdowns." % [gallery.total_hits,gallery.scored]
    beam(start-pilot.camera.global_transform.basis.y*0.12,end,TEAL)

func use_tool() -> void:
    if phase != "RUNNING" or pulse_delay > 0: return
    if mode == 1:
        if fire_delay <= 0:
            fire(true)
            pulse_delay = 2.5
    elif mode == 2:
        if pilot.position.distance_to(ally.position)>7:
            message = "Move within 7 m to repair."
            return
        var gain := mini(36,100-ally_hp)
        if gain == 0: return
        ally_hp += gain
        restored += gain
        pulse_delay = 1.85
        beam(pilot.camera.global_position,ally.position,TEAL)
        message = "Courier repaired: +%d" % gain

func finish(win: bool) -> void:
    phase = "WON" if win else "LOST"
    last_result = "%s  /  %d HP  /  %.1f s" % [RIGS[mode],ally_hp,elapsed]
    message = "Courier reached the rescue beacon." if win else "Courier lost. Try guarding, disabling or repairing."
    ward.visible = false

func _physics_process(dt: float) -> void:
    if pilot.position.y < -7.2:
        recover()
        message = "Recovered to your checkpoint."
    fire_delay = maxf(0,fire_delay-dt)
    pulse_delay = maxf(0,pulse_delay-dt)
    clock += dt
    place_drones()
    for i in range(2):
        if disabled[i] > 0:
            disabled[i] -= dt
            if disabled[i] <= 0:
                integrity[i] = 3
                charge[i] = 0.9
                drones[i].visible = true
    if Input.is_physical_key_pressed(KEY_X): fire()
    ally_core.rotation.y = clock*1.5
    if phase == "RUNNING":
        elapsed += dt
        ally.position = Vector3(0,1.05+sin(elapsed*3)*0.07,maxf(-14.0,8.0-elapsed*1.9))
        var close := pilot.position.distance_to(ally.position)<7.0
        var guarding := mode == 0 and close and (Input.is_physical_key_pressed(KEY_E) or touch_guard)
        ward.visible = guarding
        for i in range(2):
            if disabled[i] > 0: continue
            charge[i] -= dt
            if charge[i] <= 0:
                charge[i] += 1.65
                beam(drones[i].position,ally.position,TEAL if guarding else RED)
                if guarding: prevented += 9
                ally_hp = maxi(0,ally_hp-(1 if guarding else 10))
        if ally_hp == 0: finish(false)
        elif ally.position.z <= -14.0: finish(true)
    hud.refresh(self)

func _unhandled_input(e: InputEvent) -> void:
    if e is InputEventKey and e.pressed and not e.echo:
        match e.keycode:
            KEY_F: start_trial()
            KEY_R: reset_trial()
            KEY_C: save_checkpoint()
            KEY_1: switch_rig(0)
            KEY_2: switch_rig(1)
            KEY_3: switch_rig(2)
            KEY_E: use_tool()
            KEY_ESCAPE: Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
    elif e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT and e.pressed:
        if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED: fire()
        elif not DisplayServer.is_touchscreen_available(): Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

    elif e is InputEventJoypadButton:
        if e.button_index == JOY_BUTTON_RIGHT_SHOULDER and not e.pressed:
            touch_guard = false
        if e.pressed:
            match e.button_index:
                JOY_BUTTON_A: pilot.jump_queued = true
                JOY_BUTTON_X: fire()
                JOY_BUTTON_RIGHT_SHOULDER:
                    touch_guard = true
                    use_tool()
                JOY_BUTTON_Y: switch_rig((mode+1)%3)
                JOY_BUTTON_START: start_trial()
                JOY_BUTTON_BACK: reset_trial()
