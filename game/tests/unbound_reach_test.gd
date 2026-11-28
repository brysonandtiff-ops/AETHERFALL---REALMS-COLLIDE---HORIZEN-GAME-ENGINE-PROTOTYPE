extends SceneTree
## Run with the pinned native Godot binary: --headless --path game --script res://tests/unbound_reach_test.gd
var failures := PackedStringArray()

func check(ok: bool, label: String) -> void:
	if not ok:
		failures.append(label)
		push_error(label)

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
	for i in range(40):
		await physics_frame
	check(level.player.is_on_floor(), "Hub spawn must settle on collision")
	check(absf(level.player.position.y - 28.0) < 0.2, "Hub floor elevation")
	check(level.drones.size() == 12, "Two groups of six drones")
	check(level.pods.size() == 4, "Four rescue pods")
	check(level.brawlers.size() == 4, "Four arena drills")
	var start: Vector3 = level.drones[0].position
	for i in range(10):
		await physics_frame
	check(start.distance_to(level.drones[0].position) > 0.01, "Drone movement")
	for zone in ["Arena", "Rescue", "Arch", "A", "B", "C", "D", "Hub"]:
		level.warp(zone)
		for i in range(36):
			await physics_frame
		check(level.player.is_on_floor(), "Land on " + zone)
		check(absf(level.player.position.y - level.stops[zone].y) < 0.22, "Correct deck height: " + zone)
	level.warp("Arena")
	for i in range(4):
		await physics_frame
	var dummy = level.brawlers[0]
	level.camera.look_at(dummy.global_position, Vector3.UP)
	level.shoot()
	check(level.hits == 1, "Aim ray registers a real collider hit")
	level.warp("Rescue")
	for pod in level.pods:
		level.player.position = pod.position + Vector3(0, -1.0, 1.5)
		level.interact()
	check(level.rescued == 4, "All four rescue interactions")
	level.reset_drill()
	check(level.rescued == 0 and level.hits == 0, "Repeatable drill reset")
	level.player.position.y = -50.0
	for i in range(5):
		await physics_frame
	check(level.player.position.distance_to(level.stops["Hub"]) < 2.0, "Fall recovery")
	if failures.is_empty():
		print("UNBOUND_REACH_NATIVE_PASS: spawn, destinations, 12 moving drones, hitscan, rescue, reset, fall recovery")
	quit(0 if failures.is_empty() else 1)
