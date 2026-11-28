extends SceneTree
# AF-RANGE-002: synthetic touch events and actual range HUD nodes.
# Tests mobile interactions in native Godot headless; not physical Android proof.
var failed: Array[String] = []

func check(ok: bool, name: String) -> void:
    print("AF_MOBILE_TEST ", "PASS " if ok else "FAIL ", name)
    if not ok: failed.append(name)

func frames(count: int) -> void:
    for i in range(count):
        await physics_frame

func touch(index: int, position: Vector2, pressed: bool) -> InputEventScreenTouch:
    var e := InputEventScreenTouch.new()
    e.index = index
    e.position = position
    e.pressed = pressed
    return e

func drag(index: int, position: Vector2, movement: Vector2) -> InputEventScreenDrag:
    var e := InputEventScreenDrag.new()
    e.index = index
    e.position = position
    e.relative = movement
    return e

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    var packed := load("res://scenes/levels/arenas/unbound_reach.tscn") as PackedScene
    if packed == null:
        check(false,"real practice range scene loads")
        quit(1)
        return
    var level = packed.instantiate()
    root.add_child(level)
    await frames(12)
    var pilot = level.pilot
    var hud = level.hud
    check(hud.touch_enabled and hud.touch_actions.size() >= 7,"touch controls built")
    check(root.content_scale_aspect == Window.CONTENT_SCALE_ASPECT_EXPAND,"mobile viewport expands without letterboxing")
    check(root.content_scale_size.x == root.content_scale_size.y,"square touch design basis")

    check(hud.touch_actions.has("BEGIN") and hud.touch_actions.has("RESET"),"begin and reset reachable by touch")
    for viewport_size in [Vector2(844,390), Vector2(390,844), Vector2(1280,800)]:
        hud.layout_touch(viewport_size)
        var safe := true
        for action in hud.touch_actions.values():
            var r := Rect2(action.position,action.size)
            if r.position.x < 0 or r.position.y < 0 or r.end.x > viewport_size.x or r.end.y > viewport_size.y:
                safe = false
        check(safe,"buttons stay within %dx%d viewport" % [int(viewport_size.x),int(viewport_size.y)])
    hud.layout_touch(Vector2(1280,720))
    var camera_yaw: float = pilot.rotation.y
    pilot._unhandled_input(touch(0,Vector2(110,610),true))
    pilot._unhandled_input(drag(0,Vector2(165,570),Vector2(55,-40)))
    check(pilot.touch_move.x > 0.3 and pilot.touch_move.y < -0.2,"left stick processes analog drag")
    pilot._unhandled_input(touch(1,Vector2(950,400),true))
    pilot._unhandled_input(drag(1,Vector2(990,400),Vector2(40,0)))
    check(absf(pilot.rotation.y-camera_yaw)>0.07,"right touch looks independently while moving")
    pilot._unhandled_input(touch(0,Vector2(165,570),false))
    check(pilot.touch_move.length()<0.01,"release stops analog movement")
    pilot._unhandled_input(touch(1,Vector2(990,400),false))
    level.pilot.position = level.ally.position + Vector3(0,0,1)
    hud.touch_actions["BEGIN"].pressed.emit()
    await frames(2)
    check(level.phase=="RUNNING","tap begin starts real trial")
    hud.touch_actions["TOOL"].button_down.emit()
    check(level.touch_guard,"holding mobile tool guards courier")
    hud.touch_actions["TOOL"].button_up.emit()
    check(not level.touch_guard,"tool release cancels shield")
    hud.touch_actions["RESET"].pressed.emit()
    check(level.phase=="READY","touch reset replays trial")
    hud.touch_actions["RIG"].pressed.emit()
    check(level.mode==1,"touch cycles test rig")
    print("AF_MOBILE_RESULT ", "PASS" if failed.is_empty() else str(failed))
    quit(0 if failed.is_empty() else 1)
