extends SceneTree
## Actual viewport recording with scripted Godot input packets, not physical hardware.
func _initialize() -> void:
	call_deferred("run")

func send(e: InputEvent) -> void:
	e.device = 0
	Input.parse_input_event(e)
	Input.flush_buffered_events()

func button(code: JoyButton, down: bool) -> void:
	var e := InputEventJoypadButton.new()
	e.button_index = code
	e.pressed = down
	send(e)

func axis(code: JoyAxis, value: float) -> void:
	var e := InputEventJoypadMotion.new()
	e.axis = code
	e.axis_value = value
	send(e)

func run() -> void:
	var out := OS.get_environment("AF_CAPTURE_DIR")
	if DisplayServer.get_name()=="headless" or out.is_empty() or not DirAccess.dir_exists_absolute(out):
		push_error("A real renderer and AF_CAPTURE_DIR are required"); quit(1); return
	var packed := load(str(ProjectSettings.get_setting("application/run/main_scene"))) as PackedScene
	var level = packed.instantiate()
	root.add_child(level)
	await process_frame
	if not level.has_method("pad_reset"):
		push_error("Wrong startup scene"); quit(1); return
	level.pad.defaults()
	var aim_seen := false
	var menu_seen := false
	var start: Vector3 = level.player.position
	var moved := false
	for i in range(180):
		match i:
			10: axis(JOY_AXIS_LEFT_Y,-0.75)
			31:
				axis(JOY_AXIS_LEFT_Y,0.0)
				moved = level.player.position.distance_to(start)>0.5
			38: level.warp("Arena")
			44:
				level.camera.look_at(level.brawlers[0].global_position,Vector3.UP)
				axis(JOY_AXIS_TRIGGER_LEFT,0.81)
			52: aim_seen = level.camera.fov < 70.0
			54: axis(JOY_AXIS_TRIGGER_RIGHT,0.9)
			60: axis(JOY_AXIS_TRIGGER_RIGHT,0.0)
			64: axis(JOY_AXIS_TRIGGER_LEFT,0.0)
			67: level.warp("A")
			83: level.camera.look_at(level.drones[0].global_position,Vector3.UP)
			101: level.warp("Rescue")
			107:
				var pod = level.pods[0]
				level.player.position = pod.position+Vector3(0,-0.93,2.0)
				level.camera.look_at(pod.global_position,Vector3.UP)
			116: button(JOY_BUTTON_X,true)
			117: button(JOY_BUTTON_X,false)
			127: button(JOY_BUTTON_X,true)
			128: button(JOY_BUTTON_X,false)
			143: button(JOY_BUTTON_Y,true)
			144: button(JOY_BUTTON_Y,false)
			150: button(JOY_BUTTON_START,true)
			151: button(JOY_BUTTON_START,false)
			156: button(JOY_BUTTON_DPAD_DOWN,true)
			157: button(JOY_BUTTON_DPAD_DOWN,false)
			169: menu_seen = level.pad.menu and level.pad.row == 1 and "CONTROLLER SETTINGS" in level.hud.text
			174: button(JOY_BUTTON_B,true)
			175: button(JOY_BUTTON_B,false)
		await process_frame
		await RenderingServer.frame_post_draw
		var image := root.get_texture().get_image()
		if image==null or image.is_empty() or image.save_png(out.path_join("frame-%03d.png"%i))!=OK:
			push_error("Could not write actual viewport frame %d"%i); quit(1); return
		if i == 169 and image.save_png(out.get_base_dir().path_join("xbox-settings.png")) != OK:
			push_error("Missing controller settings capture"); quit(1); return
	if not moved or not aim_seen or not menu_seen or level.pad.menu or level.hits!=1 or level.rescued!=1 or level.player.position.distance_to(level.stops.Hub)>2.0:
		push_error("Capture assertions failed: move=%s aim=%s menu=%s hits=%d rescue=%d" % [moved,aim_seen,menu_seen,level.hits,level.rescued]); quit(1); return
	print("UNBOUND_REACH_GRAPHICAL_CAPTURE: 180 real viewport frames; synthetic Xbox aim/fire, rescue, return, menu focus and cancel; renderer=", RenderingServer.get_video_adapter_name())
	quit(0)
