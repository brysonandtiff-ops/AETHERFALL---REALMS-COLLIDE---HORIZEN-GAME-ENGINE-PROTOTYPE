extends Control
## Input-only phone/tablet HUD for the temporary mechanics lab.
## This is NOT the approved final AETHERFALL HUD/artwork.

var player: CharacterBody3D
var _move_finger := -1
var _look_finger := -1
var _move_origin := Vector2.ZERO
var _buttons: Array[Button] = []
var _stats: Label


func _ready() -> void:
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    mouse_filter = Control.MOUSE_FILTER_IGNORE
    _build_interface()


func bind_player(value: CharacterBody3D) -> void:
    player = value


func _build_interface() -> void:
    var heading := _label("AETHERFALL  /  UNBOUND REACH  /  MECHANICS TEST", 21)
    heading.offset_left = 24
    heading.offset_top = 16
    heading.offset_right = 920
    heading.offset_bottom = 52

    var instructions := _label("Move: WASD / left stick / left touch    Aim: mouse / right stick / right touch", 15)
    instructions.offset_left = 24
    instructions.offset_top = 54
    instructions.offset_right = 900
    instructions.offset_bottom = 86

    _stats = _label("SHOTS 0    HITS 0    DASH READY", 20)
    _stats.offset_left = 24
    _stats.offset_top = 94
    _stats.offset_right = 600
    _stats.offset_bottom = 130

    var status := _label("GREYBOX ONLY  |  NOT A FINISHED MAP OR HERO", 15)
    status.anchor_top = 1.0
    status.anchor_bottom = 1.0
    status.offset_left = 22
    status.offset_right = 560
    status.offset_top = -46
    status.offset_bottom = -16

    var move_hint := _label("MOVE", 26)
    move_hint.anchor_top = 1.0
    move_hint.anchor_bottom = 1.0
    move_hint.offset_left = 60
    move_hint.offset_right = 225
    move_hint.offset_top = -175
    move_hint.offset_bottom = -135

    var reticle := _label("+", 38)
    reticle.anchor_left = 0.5
    reticle.anchor_top = 0.5
    reticle.anchor_right = 0.5
    reticle.anchor_bottom = 0.5
    reticle.offset_left = -11
    reticle.offset_top = -32
    reticle.offset_right = 24
    reticle.offset_bottom = 22

    _action_button("FIRE", "fire", -130, -127, -19, -22)
    _action_button("JUMP", "jump", -238, -118, -139, -25)
    _action_button("DASH", "dash", -346, -118, -249, -25)
    _action_button("AIM", "aim", -132, -230, -20, -140)

    var back := Button.new()
    back.text = "BACK"
    back.focus_mode = Control.FOCUS_NONE
    back.anchor_left = 1.0
    back.anchor_right = 1.0
    back.offset_left = -139
    back.offset_right = -20
    back.offset_top = 15
    back.offset_bottom = 65
    back.pressed.connect(_return_to_bootstrap)
    add_child(back)
    _buttons.append(back)


func _label(value: String, font_size: int) -> Label:
    var result := Label.new()
    result.text = value
    result.add_theme_font_size_override("font_size", font_size)
    result.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(result)
    return result


func _action_button(title: String, action: String, left: float, top: float, right: float, bottom: float) -> void:
    var button := Button.new()
    button.text = title
    button.focus_mode = Control.FOCUS_NONE
    button.anchor_left = 1.0
    button.anchor_top = 1.0
    button.anchor_right = 1.0
    button.anchor_bottom = 1.0
    button.offset_left = left
    button.offset_top = top
    button.offset_right = right
    button.offset_bottom = bottom
    button.button_down.connect(func(): _set_button(action, true))
    button.button_up.connect(func(): _set_button(action, false))
    add_child(button)
    _buttons.append(button)


func _set_button(action: String, is_down: bool) -> void:
    if is_instance_valid(player):
        player.set_touch_action(action, is_down)


func _input(event: InputEvent) -> void:
    if not is_instance_valid(player):
        return
    if event is InputEventScreenTouch:
        if event.pressed:
            if _over_button(event.position):
                return
            var viewport_size := get_viewport_rect().size
            if event.position.x < viewport_size.x * 0.44 and event.position.y > viewport_size.y * 0.33 and _move_finger == -1:
                _move_finger = event.index
                _move_origin = event.position
                _move_update(event.position)
            elif event.position.x >= viewport_size.x * 0.44 and _look_finger == -1:
                _look_finger = event.index
        else:
            if event.index == _move_finger:
                _move_finger = -1
                player.set_touch_move(Vector2.ZERO)
            if event.index == _look_finger:
                _look_finger = -1

    elif event is InputEventScreenDrag:
        if event.index == _move_finger:
            _move_update(event.position)
        elif event.index == _look_finger:
            player.apply_look(event.relative * 1.35)


func _over_button(point: Vector2) -> bool:
    for button in _buttons:
        if button.get_global_rect().has_point(point):
            return true
    return false


func _move_update(position: Vector2) -> void:
    var axis := ((position - _move_origin) / 90.0).limit_length(1.0)
    player.set_touch_move(axis)


func _process(_delta: float) -> void:
    if not is_instance_valid(player):
        return
    var dash_label := "READY"
    if player.dash_cooldown > 0.0:
        dash_label = "%.1fs" % player.dash_cooldown
    _stats.text = "SHOTS %d    HITS %d    DASH %s" % [player.shots_fired, player.targets_hit, dash_label]


func _return_to_bootstrap() -> void:
    if is_instance_valid(player):
        player.set_touch_move(Vector2.ZERO)
        for action in ["fire", "jump", "dash", "aim"]:
            player.set_touch_action(action, false)
    get_tree().change_scene_to_file("res://scenes/bootstrap/main.tscn")


func _exit_tree() -> void:
    if is_instance_valid(player):
        player.set_touch_move(Vector2.ZERO)
        for action in ["fire", "jump", "dash", "aim"]:
            player.set_touch_action(action, false)
