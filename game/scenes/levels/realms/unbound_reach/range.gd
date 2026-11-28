extends "res://scenes/levels/realms/unbound_reach/terrain.gd"
## Range-only instrumentation. No competitive rules or canonical hero kits.
const DEST := ["Arena","A","Rescue","Arch","B","C","D"]
var pad := preload("res://scenes/levels/realms/unbound_reach/range_pad.gd").new()
var stops := STOPS
var player := CharacterBody3D.new()
var camera := Camera3D.new()
var hud := Label.new()
var normal_hud := Control.new()
var settings_panel := PanelContainer.new()
var settings_text := Label.new()
var portal_hint := Label.new()
var control_hint := Label.new()
var action_hint := Label.new()
var sight := Label.new()
var drones: Array[Node3D] = []
var pods: Array[Node3D] = []
var brawlers: Array[Node3D] = []
var terminals: Array[Node3D] = []
var hits := 0
var shots := 0
var rescued := 0
var destination := 0
var tempo := 1
var clock := 0.0
var pitch := 0.0
var jump_requested := false
var fire_requested := false
var use_requested := false
var notice := ""
var notice_until := 0.0
var previous_hud := ""

func _ready() -> void:
	pad.load_profile()
	Input.joy_connection_changed.connect(_pad_connection)
	get_window().focus_exited.connect(pad_reset)
	make_world()
	add_child(player)
	player.name = "PracticeBody"
	player.floor_snap_length = 0.4
	player.floor_max_angle = deg_to_rad(48)
	player.floor_constant_speed = true
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.37
	capsule.height = 1.8
	var cs := CollisionShape3D.new()
	cs.shape = capsule
	cs.position.y = 0.9
	player.add_child(cs)
	player.add_child(camera)
	camera.position.y = 1.62
	camera.fov = 78.0
	camera.far = 360
	camera.current = true
	for i in range(3):
		var p := Vector3((i-1)*4.1,28,56)
		var console := box("Console",p+Vector3.UP*0.57,Vector3(1.55,1.14,0.92),DARK)
		box("HoloGlass",p+Vector3.UP*1.22,Vector3(1.48,0.14,0.66),CYAN,false,true)
		terminals.append(console)
		label3(p+Vector3.UP*2.4,["PRACTICE MODE","CUSTOM DRILLS","QUICK PORTALS"][i],CYAN,0.009)
	for i in range(4):
		var x := -4.0 if i%2==0 else 4.0
		var z := -5.0 if i<2 else 5.0
		var bot := drum("BrawlTarget",Vector3(x,1.1,z),0.50,2.2,RED,true)
		brawlers.append(bot)
		var p := Vector3(33+x,6,z)
		drum("RescuePad",p+Vector3.UP*0.06,1.25,0.12,DARK)
		ring(p+Vector3.UP*0.14,1.05,0.08,GREEN)
		var pod := drum("AllyPod",p+Vector3.UP*1.0,0.57,2,GREEN,true)
		pods.append(pod)
	for rail in range(2):
		for j in range(8):
			var a := TAU*j/8
			var hoop := ring(rail_at(rail,a),1.55,0.075,CYAN)
			var tangent := (rail_at(rail,a+0.01)-rail_at(rail,a-0.01)).normalized()
			hoop.quaternion = Quaternion(Vector3.UP,tangent)
		for j in range(6):
			var target := drum("Drone",rail_at(rail,TAU*j/6),0.65,0.58,CYAN,true)
			drones.append(target)
			for side in [-1,1]:
				var wing := MeshInstance3D.new()
				var m := BoxMesh.new()
				m.size = Vector3(0.95,0.12,0.43)
				wing.mesh = m
				wing.material_override = material(DARK)
				target.add_child(wing)
				wing.position = Vector3(side*0.65,0,0)
	var overlay := CanvasLayer.new()
	add_child(overlay)
	overlay.add_child(normal_hud)
	normal_hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	normal_hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud_plate(normal_hud, hud, Control.PRESET_TOP_LEFT, Vector4(16,16,395,100), 17)
	hud_plate(normal_hud, portal_hint, Control.PRESET_BOTTOM_LEFT, Vector4(16,-82,238,-18), 16)
	hud_plate(normal_hud, action_hint, Control.PRESET_CENTER_BOTTOM, Vector4(-178,-82,178,-20), 17)
	hud_plate(normal_hud, control_hint, Control.PRESET_BOTTOM_RIGHT, Vector4(-292,-82,-16,-18), 15)
	normal_hud.add_child(sight)
	sight.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	sight.offset_left = -10
	sight.offset_top = -19
	sight.offset_right = 12
	sight.offset_bottom = 13
	sight.text = "+"
	sight.add_theme_font_size_override("font_size",26)
	sight.add_theme_color_override("font_color",Color("d6faff"))
	sight.add_theme_constant_override("outline_size",4)
	sight.add_theme_color_override("font_outline_color",Color("14121d"))
	overlay.add_child(settings_panel)
	settings_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	settings_panel.offset_left = -285
	settings_panel.offset_top = -213
	settings_panel.offset_right = 285
	settings_panel.offset_bottom = 213
	settings_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	settings_panel.add_theme_stylebox_override("panel",hud_style())
	settings_panel.add_child(settings_text)
	settings_text.add_theme_font_size_override("font_size",20)
	settings_text.add_theme_color_override("font_color",Color("f0e5ff"))
	settings_text.mouse_filter = Control.MOUSE_FILTER_IGNORE
	settings_panel.hide()
	warp("Hub")

func hud_style() -> StyleBoxFlat:
	var box_style := StyleBoxFlat.new()
	box_style.bg_color = Color(0.035,0.029,0.072,0.88)
	box_style.border_color = Color("9160cb")
	box_style.set_border_width_all(2)
	box_style.set_corner_radius_all(7)
	box_style.set_content_margin_all(12)
	return box_style

func hud_plate(parent: Control, text_label: Label, anchor: Control.LayoutPreset, rect: Vector4, font_size: int) -> void:
	var panel := PanelContainer.new()
	parent.add_child(panel)
	panel.set_anchors_and_offsets_preset(anchor)
	panel.offset_left = rect.x
	panel.offset_top = rect.y
	panel.offset_right = rect.z
	panel.offset_bottom = rect.w
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.add_theme_stylebox_override("panel", hud_style())
	panel.add_child(text_label)
	text_label.add_theme_font_size_override("font_size",font_size)
	text_label.add_theme_color_override("font_color",Color("f3eeff"))
	text_label.mouse_filter = Control.MOUSE_FILTER_IGNORE

func rail_at(index: int,a: float) -> Vector3:
	# 60 m major span, two distinct altitudes; the board does not fix the minor axes.
	return Vector3(30*cos(a),10.0 if index==0 else 22.0,(15.0 if index==0 else 21.0)*sin(a) + (-4.0 if index==0 else -11.0))

func warp(zone: String) -> void:
	if not stops.has(zone): return
	player.position = Vector3(stops[zone])+Vector3.UP*0.10
	player.velocity = Vector3.ZERO
	player.rotation.y = 0
	pitch = -0.34 if zone=="Hub" else 0.0
	camera.rotation = Vector3(pitch,0,0)
	if zone in ["A","B","C","D","Arch","Rescue"]:
		player.rotation.y = atan2(player.position.x,player.position.z)
	message("Arrived: "+zone)

func pad_reset() -> void:
	if pad.menu: pad.cancel_menu()
	pad.reset_device()
	pad.blocked.clear()
	jump_requested = false
	fire_requested = false
	use_requested = false
	camera.fov = 78.0

func _pad_connection(id: int, connected: bool) -> void:
	if not connected and id == pad.device:
		pad_reset()
		message("Controller disconnected. Reconnect or use keyboard.")

func _unhandled_input(e: InputEvent) -> void:
	if e is InputEventJoypadButton or e is InputEventJoypadMotion:
		var action := pad.packet(e)
		if pad.menu:
			fire_requested = false
			jump_requested = false
			use_requested = false
		else:
			match action:
				"Jump": jump_requested = true
				"Fire": fire_requested = true
				"Interact": use_requested = true
				"Hub": warp("Hub")
				"Reset drill": reset_drill()
		return
	if pad.menu:
		if e is InputEventKey and e.pressed and e.physical_keycode == KEY_ESCAPE:
			pad.cancel_menu()
		return
	if e is InputEventMouseMotion and Input.mouse_mode==Input.MOUSE_MODE_CAPTURED:
		pad.active = false
		player.rotate_y(-e.relative.x*0.0022)
		pitch = clampf(pitch-e.relative.y*0.0022,-1.42,1.42)
		camera.rotation.x = pitch
	elif e is InputEventMouseButton and e.pressed and e.button_index==MOUSE_BUTTON_LEFT:
		pad.active = false
		if Input.mouse_mode!=Input.MOUSE_MODE_CAPTURED: Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		else: fire_requested = true
	elif e is InputEventKey and e.pressed and not e.echo:
		pad.active = false
		match e.physical_keycode:
			KEY_ESCAPE: Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
			KEY_SPACE: jump_requested = true
			KEY_E: use_requested = true
			KEY_R: warp("Hub")
			KEY_T: reset_drill()

func _physics_process(delta: float) -> void:
	var menu_open := pad.menu
	if menu_open:
		jump_requested = false
		fire_requested = false
		use_requested = false
	clock += delta
	for i in range(drones.size()):
		var rail := 0 if i<6 else 1
		var angle := TAU*(i%6)/6 + clock*(0.17 if rail==0 else -0.12)
		var d := drones[i]
		d.position = rail_at(rail,angle)
		d.rotation.y = -angle
		if not d.visible and clock>=float(d.get_meta("restore_at",0.0)):
			d.show()
			(d as StaticBody3D).collision_layer = 1
	var look := pad.look()
	var scale_aim := float(pad.settings["ADS multiplier"]) if pad.aiming() else 1.0
	player.rotate_y(-look.x*deg_to_rad(float(pad.settings["Horizontal speed"]))*scale_aim*delta)
	pitch = clampf(pitch-look.y*deg_to_rad(float(pad.settings["Vertical speed"]))*scale_aim*delta,-1.42,1.42)
	if not is_zero_approx(look.y): camera.rotation.x = pitch
	camera.fov = move_toward(camera.fov,58.0 if pad.aiming() else 78.0,160.0*delta)
	var k := Vector2.ZERO
	if not menu_open:
		k = Vector2(float(Input.is_physical_key_pressed(KEY_D))-float(Input.is_physical_key_pressed(KEY_A)),float(Input.is_physical_key_pressed(KEY_S))-float(Input.is_physical_key_pressed(KEY_W)))
		k = (k+pad.move()).limit_length(1)
	var motion := player.basis * Vector3(k.x,0,k.y) * (9.0 if Input.is_physical_key_pressed(KEY_SHIFT) or pad.running() else 6.0)
	player.velocity.x = motion.x
	player.velocity.z = motion.z
	if not player.is_on_floor(): player.velocity.y -= 21.0*delta
	elif jump_requested: player.velocity.y = 7.0
	jump_requested = false
	player.move_and_slide()
	if player.position.y < -34: warp("Hub")
	if not menu_open and fire_requested: shoot()
	if not menu_open and use_requested: interact()
	fire_requested = false
	use_requested = false
	if menu_open:
		normal_hud.hide()
		settings_panel.show()
		settings_text.text = pad.menu_text()
		hud.text = settings_text.text
		previous_hud = ""
	else:
		settings_panel.hide()
		normal_hud.show()
		update_hud()

func nearest(nodes: Array[Node3D],radius: float) -> int:
	var result := -1
	for i in range(nodes.size()):
		var dist := player.position.distance_to(nodes[i].position)
		if dist<radius:
			result = i
			radius = dist
	return result

func interact() -> void:
	var terminal := nearest(terminals,3.2)
	match terminal:
		0:
			destination = (destination+1)%DEST.size()
			message("Portal destination: "+DEST[destination]); return
		1:
			tempo = tempo%3+1
			message("Drone respawn setting: "+str(tempo)); return
		2:
			warp(DEST[destination]); return
	if player.position.distance_to(Vector3(-36,3,1))<3.5:
		warp("Hub"); return
	var which := nearest(pods,3.0)
	if which<0: return
	var pod := pods[which]
	var health := int(pod.get_meta("health",0))
	if health>=2:
		message("Ally already recovered"); return
	pod.set_meta("health",health+1)
	var mesh := pod.get_child(1) as MeshInstance3D
	mesh.material_override = material(CYAN if health==0 else Color("d4ffee"),true)
	if health==0:
		rescued += 1
		message("Ally revived. Use %s again to heal." % (pad.glyph("Interact") if pad.active else "E"))
	else: message("Ally healed to full")

func shoot() -> void:
	shots += 1
	var origin := camera.global_position
	var ray := PhysicsRayQueryParameters3D.create(origin,origin-camera.global_basis.z*110)
	ray.exclude = [player.get_rid()]
	var hit := get_world_3d().direct_space_state.intersect_ray(ray)
	if hit.is_empty(): return
	var target: Node3D = hit["collider"] as Node3D
	if target in drones and target.visible:
		target.hide()
		(target as StaticBody3D).collision_layer = 0
		target.set_meta("restore_at",clock+(4.0/tempo))
	elif not target in brawlers: return
	hits += 1
	message("Target hit")

func reset_drill() -> void:
	hits = 0; shots = 0; rescued = 0
	for pod in pods:
		pod.set_meta("health",0)
		(pod.get_child(1) as MeshInstance3D).material_override = material(GREEN)
	for d in drones:
		d.show(); (d as StaticBody3D).collision_layer = 1
	message("Drill reset")

func message(s: String) -> void:
	notice = s
	notice_until = clock+2.3

func update_hud() -> void:
	var ctx := ""
	var use_key := pad.glyph("Interact") if pad.active else "E"
	var n := nearest(terminals,3.2)
	if n>=0: ctx = use_key+"   "+["Choose destination", "Change drone respawn delay", "Enter portal → "+DEST[destination]][n]
	elif nearest(pods,3.0)>=0: ctx = use_key+"   Revive / heal ally"
	elif player.position.distance_to(Vector3(-36,3,1))<3.5: ctx = use_key+"   Return to Hero Hub"
	elif clock<notice_until: ctx = notice
	var hints := "WASD MOVE   CLICK FIRE\\nSHIFT RUN   SPACE JUMP"
	if pad.active:
		hints = "%s AIM   %s FIRE\\n%s JUMP   %s USE" % [pad.glyph("Aim"),pad.glyph("Fire"),pad.glyph("Jump"),use_key]
	var text := "THE UNBOUND REACH\\nHITS %d / %d     REVIVES %d / 4" % [hits,shots,rescued]
	if text!=previous_hud:
		hud.text = text
		previous_hud = text
	portal_hint.text = "PRACTICE RANGE\\nPORTAL  /  "+DEST[destination].to_upper()
	control_hint.text = hints
	action_hint.text = ctx if not ctx.is_empty() else ("MENU  •  CONTROLS" if pad.active else "E  •  INTERACT")
	sight.add_theme_color_override("font_color",Color("ce8dff") if pad.aiming() else Color("d6faff"))
