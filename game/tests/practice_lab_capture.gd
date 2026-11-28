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

    print("PASS: native Godot rendered viewport saved to " + path)
    print("SOURCE: CI virtual display, Godot graphics renderer. NOT smartphone/tablet proof.")
    quit(0)


func _fail(message: String) -> void:
    printerr("CAPTURE_NOT_VERIFIED: " + message)
    quit(1)
