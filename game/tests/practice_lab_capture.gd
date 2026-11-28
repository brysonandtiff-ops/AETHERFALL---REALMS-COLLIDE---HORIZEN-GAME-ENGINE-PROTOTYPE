extends SceneTree
## Real Godot render capture in a CI virtual display, not a device screenshot.
## This script never generates an image illustration or changes approved artwork.

func _initialize() -> void:
    call_deferred("_capture")


func _capture() -> void:
    var packed: PackedScene = load("res://scenes/levels/arenas/unbound_reach_mechanics_lab.tscn")
    if packed == null:
        _fail("Scene not loadable")
        return

    var scene := packed.instantiate()
    root.add_child(scene)
    current_scene = scene
    root.size = Vector2i(1280, 720)

    for frame in range(5):
        await process_frame
    await RenderingServer.frame_post_draw

    var image: Image = root.get_texture().get_image()
    if image == null or image.is_empty() or image.get_width() < 640 or image.get_height() < 360:
        _fail("Real 3D viewport image is unavailable")
        return
    var directory := "/tmp/aetherfall-evidence"
    if DirAccess.make_dir_recursive_absolute(directory) != OK:
        _fail("Failed to create evidence directory")
        return
    var path := directory + "/practice-lab-native.png"
    if image.save_png(path) != OK:
        _fail("Failed to save engine viewport PNG")
        return

    # Record only real rendered frames after exercising the shared gameplay inputs.
    var pilot = scene.get_node_or_null("TrainingPlayer")
    var frames_dir := directory + "/frames"
    if pilot == null or DirAccess.make_dir_recursive_absolute(frames_dir) != OK:
        _fail("Cannot prepare real game motion frames")
        return

    pilot.set_touch_move(Vector2(0.0, -1.0))
    pilot.set_touch_action("fire", true)
    for frame in range(96):
        if frame == 54:
            pilot.set_touch_action("fire", false)
            pilot.set_touch_move(Vector2(0.9, -0.2))
        if frame == 75:
            pilot.set_touch_action("dash", true)
        if frame == 77:
            pilot.set_touch_action("dash", false)
        await process_frame
        await RenderingServer.frame_post_draw
        if frame % 3 == 0:
            var frame_image: Image = root.get_texture().get_image()
            if frame_image == null or frame_image.is_empty():
                _fail("Real gameplay frame missing")
                return
            var frame_path := frames_dir + ("/frame_%03d.png" % int(frame / 3.0))
            if frame_image.save_png(frame_path) != OK:
                _fail("Could not save real gameplay frame")
                return

    pilot.set_touch_move(Vector2.ZERO)
    pilot.set_touch_action("fire", false)
    pilot.set_touch_action("dash", false)
    print("PASS: native Godot rendered viewport saved to " + path)
    print("PASS: 32 real native game frames captured after movement, firing and dash input")
    print("SOURCE: CI virtual display, Godot graphics renderer. NOT smartphone/tablet proof.")
    quit(0)


func _fail(message: String) -> void:
    printerr("CAPTURE_NOT_VERIFIED: " + message)
    quit(1)
