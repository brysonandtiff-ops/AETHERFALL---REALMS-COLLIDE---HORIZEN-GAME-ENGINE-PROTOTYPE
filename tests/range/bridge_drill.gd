extends SceneTree
# Run with Godot --headless --path game --script ../tests/range/bridge_drill.gd.
# Inputs drive the production scene. Fast fixed physics, not wall-clock benchmarks.
var failures: Array[String] = []
var level

func _initialize() -> void:
    call_deferred("exercise")

func check(ok: bool, label: String) -> void:
    if not ok:
        failures.append(label)
    print("AF_TEST ", "PASS " if ok else "FAIL ", label)

func ticks(n: int) -> void:
    for i in range(n):
        await physics_frame

func key(code: Key, down: bool) -> void:
    var event := InputEventKey.new()
    event.physical_keycode = code
    event.keycode = code
    event.pressed = down
    Input.parse_input_event(event)
    Input.flush_buffered_events()

func tap(code: Key) -> void:
    key(code, true)
    await ticks(2)
    key(code, false)
    await ticks(2)

func exercise() -> void:
    var packed = load("res://scenes/levels/arenas/unbound_reach.tscn")
    if not packed is PackedScene:
        check(false, "practice scene loads")
        quit(1)
        return
    level = packed.instantiate()
    root.add_child(level)
    await ticks(12)
    check(level.phase == "READY", "boots at ready state")
    var origin: Vector3 = level.pilot.position
    key(KEY_W, true)
    await ticks(15)
    key(KEY_W, false)
    await ticks(3)
    check(level.pilot.position.z < origin.z - 0.8, "physical W input moves player")
    check(level.pilot.is_on_floor(), "native player collision on bridge approach")
    await tap(KEY_C)
    var saved: Vector3 = level.checkpoint
    await tap(KEY_F)
    check(level.phase == "RUNNING", "F starts the escort")
    await ticks(1000)
    check(level.phase == "LOST" and level.ally_hp == 0, "unprotected escort can lose")
    await tap(KEY_R)
    check(level.phase == "READY" and level.ally_hp == 100 and level.ally.position.z > 7.9, "replay resets actors and encounter")
    check(level.pilot.position.distance_to(saved) < 0.3, "saved checkpoint restores")
    await tap(KEY_3)
    check(level.mode == 2, "support rig selection")
    await tap(KEY_1)
    check(level.mode == 0, "tank rig selection")
    await tap(KEY_F)
    key(KEY_E, true)
    for i in range(950):
        key(KEY_W, level.pilot.position.z > level.ally.position.z + 1.2)
        await ticks(1)
        if level.phase != "RUNNING":
            break
    key(KEY_E, false)
    key(KEY_W, false)
    check(level.phase == "WON" and level.ally_hp > 0 and level.prevented > 0, "following and guarding rescues ally")
    await tap(KEY_R)
    level.pilot.position = Vector3(0, -25, 0)
    await ticks(3)
    check(level.pilot.position.distance_to(saved) < 0.4, "fall returns to checkpoint")
    print("AF_RANGE_RESULT ", "PASS" if failures.is_empty() else str(failures))
    quit(0 if failures.is_empty() else 1)
