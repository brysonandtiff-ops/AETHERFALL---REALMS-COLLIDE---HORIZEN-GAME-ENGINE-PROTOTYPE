extends SceneTree
## Native Godot headless gameplay-movement smoke, never physical-device or visual proof.

func _initialize() -> void:
    call_deferred("_run_test")


func _run_test() -> void:
    var packed: PackedScene = load("res://scenes/levels/arenas/unbound_reach_mechanics_lab.tscn")
    if packed == null:
        _fail("Practice scene did not load")
        return

    var lab := packed.instantiate()
    root.add_child(lab)
    current_scene = lab
    await process_frame
    await physics_frame

    var pilot := lab.get_node_or_null("TrainingPlayer")
    var hud := lab.get_node_or_null("MobileControls/TouchHUD")
    var target := lab.get_node_or_null("CentralTrainingTarget")
    if pilot == null or hud == null or target == null:
        _fail("Missing player, HUD or training target")
        return

    var start: Vector3 = pilot.global_position
    pilot.set_touch_move(Vector2(0.0, -1.0))
    for i in range(18):
        await physics_frame
    pilot.set_touch_move(Vector2.ZERO)
    if pilot.global_position.z >= start.z - 0.5:
        _fail("Simulated mobile movement did not move pilot forward")
        return

    var before_shots: int = pilot.shots_fired
    pilot.set_touch_action("fire", true)
    for i in range(18):
        await physics_frame
    pilot.set_touch_action("fire", false)
    if pilot.shots_fired <= before_shots:
        _fail("Simulated mobile fire did not trigger raycast")
        return
    if pilot.targets_hit < 1 or target.hit_count < 1:
        _fail("Raycast never reached the central hittable target")
        return

    if hud.player != pilot:
        _fail("Touch HUD was not bound to the gameplay pilot")
        return

    pilot.set_touch_action("dash", false)
    pilot.set_touch_move(Vector2(0.0, -1.0))
    await physics_frame
    pilot.set_touch_action("dash", true)
    await physics_frame
    if pilot.dash_cooldown <= 0.0:
        _fail("Simulated mobile dash did not start cooldown")
        return
    pilot.set_touch_action("dash", false)
    pilot.set_touch_move(Vector2.ZERO)

    print("PASS: native Godot headless scene, simulated touch move/fire/hit/dash, HUD wiring")
    print("NOT_TESTED: physical touchscreen, Android/iOS export, FPS, controller hardware, visuals")
    quit(0)


func _fail(message: String) -> void:
    printerr("FAIL: " + message)
    quit(1)
