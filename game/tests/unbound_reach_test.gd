extends SceneTree
## Native level integration and traversal; synthetic keys drive the normal player physics.
var failures := PackedStringArray()

func check(ok: bool, label: String) -> void:
	if not ok:
		failures.append(label)
		push_error(label)

func press(code: Key, down: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = down
	Input.parse_input_event(event)
	Input.flush_buffered_events()

func ticks(count: int) -> void:
	for i in range(count):
		await physics_frame

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var scene := load(ProjectSettings.get_setting("application/run/main_scene")) as PackedScene
	if scene == null:
		quit(1)
		return
	var level = scene.instantiate()
	root.add_child(level)
	await process_frame
	if not level.has_method("warp"):
		push_error("Startup must instantiate The Unbound Reach, not the scaffold.")
		quit(1)
		return
	await ticks(40)
	check(level.player.is_on_floor(), "Hub spawn must settle on collision")
	check(absf(level.player.position.y - 28.0) < 0.2, "Hub floor elevation")
	check(level.drones.size() == 12, "Two groups of six drones")
	check(level.pods.size() == 4, "Four rescue pods")
	check(level.brawlers.size() == 4, "Four arena drills")
	var start: Vector3 = level.drones[0].position
	await ticks(10)
	check(start.distance_to(level.drones[0].position) > 0.01, "Drone movement")
	for zone in ["Arena", "Rescue", "Arch", "A", "B", "C", "D", "Hub"]:
		level.warp(zone)
		await ticks(36)
		check(level.player.is_on_floor(), "Land on " + zone)
		check(absf(level.player.position.y - level.stops[zone].y) < 0.22, "Correct deck height: " + zone)
	for index in range(3):
		level.player.position = level.terminals[index].position + Vector3(0, -0.57, 1.7)
		level.interact()
	check(level.destination == 1 and level.tempo == 2, "Hub selectors change destination and drill tempo")
	check(level.player.position.distance_to(level.stops[level.DEST[level.destination]]) < 1.0, "Quick portal transfers to the selected deck")
	level.warp("Arena")
	await ticks(10)
	press(KEY_S, true)
	await ticks(310)
	press(KEY_S, false)
	var junction: Vector3 = level.player.position
	check(junction.distance_to(Vector3(0,0,31)) < 1.4, "Walk through arena breach and across south bridge: %s" % junction)
	press(KEY_D, true)
	await ticks(365)
	press(KEY_D, false)
	await ticks(6)
	var ledge: Vector3 = level.player.position
	check(level.player.is_on_floor() and ledge.distance_to(level.stops.D)<4.0, "Climb onto D without jumping or warping: %s" % ledge)
	print("WALK_TRACE: south junction=",junction,"; southeast ledge=",ledge)
	level.warp("Arena")
	await ticks(4)
	var dummy = level.brawlers[0]
	level.camera.look_at(dummy.global_position, Vector3.UP)
	level.shoot()
	check(level.hits == 1, "Aim ray registers a real collider hit")
	level.warp("Rescue")
	for pod in level.pods:
		level.player.position = pod.position + Vector3(0, -1.0, 1.5)
		for i in range(3):
			level.interact()
		check(pod.get_meta("health",0) == 2, "Revive, heal and clamp at full")
	check(level.rescued == 4, "All four rescue interactions; repeat heals do not double count")
	level.reset_drill()
	check(level.rescued == 0 and level.hits == 0, "Repeatable drill reset")
	level.player.position.y = -50.0
	await ticks(5)
	check(level.player.position.distance_to(level.stops["Hub"]) < 2.0, "Fall recovery")
	if failures.is_empty():
		print("UNBOUND_REACH_NATIVE_PASS: spawn, eight destinations, hub console selection and transport, walked arena bridge and ledge D ramp, 12 moving drones, hitscan, full revive/heal, reset, fall recovery")
	quit(0 if failures.is_empty() else 1)
