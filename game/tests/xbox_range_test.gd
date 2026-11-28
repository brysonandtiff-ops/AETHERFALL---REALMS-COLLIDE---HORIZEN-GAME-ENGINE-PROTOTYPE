extends SceneTree
## Synthetic controller packets in the native engine; no hardware is implied.
var failed := 0

func check(value: bool, description: String) -> void:
	if not value:
		push_error(description)
		failed += 1

func button(level: Node, id: int, down: bool) -> void:
	var e := InputEventJoypadButton.new()
	e.device = 42
	e.button_index = id as JoyButton
	e.pressed = down
	level._unhandled_input(e)

func axis(level: Node, id: int, value: float) -> void:
	var e := InputEventJoypadMotion.new()
	e.device = 42
	e.axis = id as JoyAxis
	e.axis_value = value
	level._unhandled_input(e)

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var scene := load(str(ProjectSettings.get_setting("application/run/main_scene"))) as PackedScene
	var level = scene.instantiate()
	root.add_child(level)
	await process_frame
	if not level.has_method("pad_reset"):
		push_error("Missing controller integration in the first level")
		quit(1)
		return
	level.pad_reset()
	level.pad.file_path = "user://xbox_range_ci_test.cfg"
	level.pad.defaults()
	axis(level, JOY_AXIS_RIGHT_X, 0.03)
	check(level.pad.look().is_zero_approx(), "resting stick noise rejected")
	axis(level, JOY_AXIS_LEFT_Y, -0.51)
	check(level.pad.move().y < -0.1 and level.pad.move().y > -0.8, "partial stick produces partial movement")
	axis(level, JOY_AXIS_TRIGGER_LEFT, 0.7)
	await physics_frame
	await physics_frame
	check(level.pad.aiming() and level.camera.fov < 78.0, "LT precision view applied")
	axis(level, JOY_AXIS_TRIGGER_RIGHT, 0.8)
	axis(level, JOY_AXIS_TRIGGER_RIGHT, 0.9)
	await physics_frame
	await physics_frame
	check(level.shots == 1, "one shot per trigger pull")
	axis(level, JOY_AXIS_TRIGGER_RIGHT, 0.0)
	axis(level, JOY_AXIS_TRIGGER_RIGHT, 0.8)
	await physics_frame
	await physics_frame
	check(level.shots == 2, "rearmed trigger after release")
	button(level, JOY_BUTTON_START, true)
	axis(level, JOY_AXIS_TRIGGER_RIGHT, 0.0)
	axis(level, JOY_AXIS_TRIGGER_RIGHT, 0.9)
	await physics_frame
	await physics_frame
	check(level.pad.menu and level.shots == 2, "menu consumes fire")
	level.pad.rebind("Interact", "Y")
	check(level.pad.glyph("Interact") == "Y" and level.pad.glyph("Hub") == "X", "swap conflicts and update prompt")
	check(level.pad.save_profile() == OK, "save settings")
	level.pad.defaults()
	level.pad.load_profile()
	check(level.pad.glyph("Interact") == "Y", "remap survives reload")
	level.pad_reset()
	check(not level.pad.aiming() and level.pad.move().is_zero_approx(), "disconnect clears held actions")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(level.pad.file_path))
	if failed == 0: print("XBOX_RANGE_NATIVE_PASS: synthetic packets, analog movement, ADS, trigger edges, menu isolation, remap and persistence")
	quit(0 if failed == 0 else 1)
