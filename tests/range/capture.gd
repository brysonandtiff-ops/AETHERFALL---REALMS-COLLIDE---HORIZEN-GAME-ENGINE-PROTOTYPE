extends SceneTree
# Deterministic automation of real game controls; no replacement camera or illustration.
var level
func _initialize() -> void:
    call_deferred("record")
func key(code: Key, down: bool) -> void:
    var e := InputEventKey.new()
    e.keycode = code
    e.physical_keycode = code
    e.pressed = down
    Input.parse_input_event(e)
    Input.flush_buffered_events()
func record() -> void:
    var packed := load("res://scenes/levels/arenas/unbound_reach.tscn") as PackedScene
    if packed == null:
        quit(1)
        return
    level = packed.instantiate()
    root.add_child(level)
    var dest := OS.get_environment("AF_CAPTURE_DIR")
    for i in range(460):
        await process_frame
        if i == 14: key(KEY_F,true)
        if i == 15: key(KEY_F,false); key(KEY_E,true)
        if i > 18 and i < 395: key(KEY_W,level.pilot.position.z > level.ally.position.z + 1.3)
        if i == 120 or i == 18 or i == 390:
            await RenderingServer.frame_post_draw
            var image := root.get_texture().get_image()
            var name := "bridge.png" if i == 120 else ("arrival.png" if i == 18 else "result.png")
            if image == null or image.is_empty() or image.save_png(dest.path_join(name)) != OK:
                push_error("Viewport readback failed")
                quit(2)
                return
        if i == 400:
            key(KEY_W,false); key(KEY_E,false)
            if level.phase != "WON" or level.prevented == 0:
                push_error("Recorded trial did not reach win")
                quit(3)
                return
            key(KEY_R,true)
        if i == 401: key(KEY_R,false)
    if level.phase != "READY":
        quit(4)
        return
    var gltf := GLTFDocument.new()
    var state := GLTFState.new()
    if gltf.append_from_scene(level.valley,state) != OK or gltf.write_to_filesystem(state,dest.path_join("unbound-reach-environment.glb")) != OK:
        push_error("Static level export failed")
        quit(5)
        return
    print("AF_CAPTURE_PASS: real rendered input-driven escort, victory, replay, environment export")
    quit(0)
