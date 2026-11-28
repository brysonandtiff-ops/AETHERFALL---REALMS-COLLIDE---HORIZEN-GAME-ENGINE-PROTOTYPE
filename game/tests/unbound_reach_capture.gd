extends SceneTree
## Graphical evidence recorder. No source artwork, compositing or placeholder frames.
## Run at --fixed-fps 24 with AF_CAPTURE_DIR set to an existing output directory.
func _initialize() -> void:
	call_deferred("run")

func key(code: Key, down: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = down
	Input.parse_input_event(event)
	Input.flush_buffered_events()

func run() -> void:
	var out := OS.get_environment("AF_CAPTURE_DIR")
	if DisplayServer.get_name()=="headless" or out.is_empty() or not DirAccess.dir_exists_absolute(out):
		push_error("A real renderer and AF_CAPTURE_DIR are required")
		quit(1)
		return
	var packed := load(str(ProjectSettings.get_setting("application/run/main_scene"))) as PackedScene
	var level = packed.instantiate()
	root.add_child(level)
	await process_frame
	if not level.has_method("warp"):
		push_error("Wrong startup scene"); quit(1); return
	for i in range(180):
		match i:
			20: key(KEY_W,true)
			31: key(KEY_W,false)
			38: level.warp("Arena")
			44: level.camera.look_at(level.brawlers[0].global_position,Vector3.UP)
			54: level.fire_requested = true
			67: level.warp("A")
			83: level.camera.look_at(level.drones[0].global_position,Vector3.UP)
			101: level.warp("Rescue")
			107:
				var pod = level.pods[0]
				level.player.position = pod.position+Vector3(0,-0.93,2.0)
				level.camera.look_at(pod.global_position,Vector3.UP)
			116: key(KEY_E,true)
			117: key(KEY_E,false)
			127: key(KEY_E,true)
			128: key(KEY_E,false)
			143: key(KEY_R,true)
			144: key(KEY_R,false)
		await process_frame
		await RenderingServer.frame_post_draw
		var image := root.get_texture().get_image()
		if image==null or image.is_empty() or image.save_png(out.path_join("frame-%03d.png"%i))!=OK:
			push_error("Could not write actual viewport frame %d"%i); quit(1); return
	if level.hits!=1 or level.rescued!=1 or level.player.position.distance_to(level.stops.Hub)>2.0:
		push_error("Capture interactions failed; do not treat this as passing interaction proof")
		quit(1); return
	print("UNBOUND_REACH_GRAPHICAL_CAPTURE: 180 actual viewport frames; scripted walker, hit, revive, heal, return; renderer=", RenderingServer.get_video_adapter_name())
	quit(0)
