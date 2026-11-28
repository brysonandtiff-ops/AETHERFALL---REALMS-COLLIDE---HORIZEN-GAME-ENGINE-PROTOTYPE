extends CanvasLayer
# One responsive interface; neutral training rigs, not canonical hero HUD.
const INK := Color("121927eb")
const MINT := Color("a6f8e3")
const GOLD := Color("dfc095")
const LIGHT := Color("f4f2f2")
var root: Control = Control.new()
var info_frame: PanelContainer
var state: Label = Label.new()
var hp: ProgressBar = ProgressBar.new()
var numbers: Label = Label.new()
var last: Label = Label.new()
var hint: Label = Label.new()
var touch_enabled := false
var touch_actions: Dictionary = {}
var joystick_base: Control
var joystick_knob: PanelContainer
var last_view := Vector2.ZERO

func style(bg: Color, border: Color = Color.TRANSPARENT, rounded: int = 8) -> StyleBoxFlat:
    var s := StyleBoxFlat.new()
    s.bg_color = bg
    s.border_color = border
    s.border_width_left = 2 if border != Color.TRANSPARENT else 0
    s.border_width_right = s.border_width_left
    s.border_width_top = s.border_width_left
    s.border_width_bottom = s.border_width_left
    s.corner_radius_top_left = rounded
    s.corner_radius_top_right = rounded
    s.corner_radius_bottom_left = rounded
    s.corner_radius_bottom_right = rounded
    s.content_margin_left = 10
    s.content_margin_right = 10
    s.content_margin_top = 7
    s.content_margin_bottom = 7
    return s

func label(parent: Node, text: String, size: int, tint: Color) -> Label:
    var l := Label.new()
    l.text = text
    l.add_theme_color_override("font_color",tint)
    l.add_theme_font_size_override("font_size",size)
    l.mouse_filter = Control.MOUSE_FILTER_IGNORE
    parent.add_child(l)
    return l

func action(name: String, title: String, cb: Callable) -> Button:
    var b := Button.new()
    b.name = name
    b.text = title
    b.focus_mode = Control.FOCUS_NONE
    b.mouse_filter = Control.MOUSE_FILTER_STOP
    b.custom_minimum_size = Vector2(62,48)
    b.add_theme_font_size_override("font_size",16)
    b.add_theme_color_override("font_color",LIGHT)
    b.add_theme_stylebox_override("normal",style(Color("29374be5"),Color("79bdc1"),13))
    b.add_theme_stylebox_override("hover",style(Color("36556bef"),MINT,13))
    b.add_theme_stylebox_override("pressed",style(Color("54838df5"),MINT,13))
    b.pressed.connect(cb)
    root.add_child(b)
    touch_actions[name] = b
    return b

func setup(s) -> void:
    add_child(root)
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    root.mouse_filter = Control.MOUSE_FILTER_IGNORE
    info_frame = PanelContainer.new()
    info_frame.name = "Stats"
    info_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
    info_frame.add_theme_stylebox_override("panel",style(INK,Color("72aaa9"),8))
    root.add_child(info_frame)
    var column := VBoxContainer.new()
    column.mouse_filter = Control.MOUSE_FILTER_IGNORE
    info_frame.add_child(column)
    label(column,"A E T H E R F A L L   /   FIELD LAB 01",12,MINT)
    label(column,"The Unbound Reach",24,LIGHT)
    column.add_child(state)
    state.mouse_filter = Control.MOUSE_FILTER_IGNORE
    state.add_theme_color_override("font_color",GOLD)
    column.add_child(hp)
    hp.show_percentage = false
    hp.custom_minimum_size.y = 6
    hp.max_value = 100
    hp.mouse_filter = Control.MOUSE_FILTER_IGNORE
    var fill := StyleBoxFlat.new()
    fill.bg_color = MINT
    hp.add_theme_stylebox_override("fill",fill)
    column.add_child(numbers)
    numbers.add_theme_font_size_override("font_size",13)
    numbers.mouse_filter = Control.MOUSE_FILTER_IGNORE
    column.add_child(last)
    last.add_theme_font_size_override("font_size",12)
    last.modulate = Color("c9d0d4")
    last.mouse_filter = Control.MOUSE_FILTER_IGNORE
    touch_enabled = DisplayServer.is_touchscreen_available() or OS.get_environment("AF_FORCE_TOUCH_UI") == "1"
    if touch_enabled:
        hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        hint.add_theme_font_size_override("font_size",12)
        hint.add_theme_color_override("font_color",MINT)
        hint.custom_minimum_size.x = 190
        hint.mouse_filter = Control.MOUSE_FILTER_IGNORE
        column.add_child(hint)
        setup_touch(s)
    else:
        info_frame.position = Vector2(18,18)
        info_frame.custom_minimum_size.x = 315
        var cross := label(root,"+",24,LIGHT)
        cross.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
        var footer := PanelContainer.new()
        footer.mouse_filter = Control.MOUSE_FILTER_IGNORE
        footer.add_theme_stylebox_override("panel",style(INK))
        root.add_child(footer)
        footer.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
        footer.offset_top = -68
        footer.offset_bottom = 0
        var box := VBoxContainer.new()
        footer.add_child(box)
        box.add_child(hint)
        hint.add_theme_color_override("font_color",MINT)
        hint.add_theme_font_size_override("font_size",14)
        label(box,"WASD move | Mouse/arrows look | Space jump | X/fire shoot | E tool | 1–3 rig | F begin | C checkpoint | R reset",13,Color("e2ddde"))
    last_view = Vector2.ZERO
    refresh(s)

func setup_touch(s) -> void:
    # Independent touch targets avoid the original 11-button horizontal overflow.
    action("BEGIN","BEGIN",s.start_trial)
    action("SAVE","SAVE",s.save_checkpoint)
    action("RESET","RESET",s.reset_trial)
    action("JUMP","JUMP",func(): s.pilot.jump_queued = true)
    action("FIRE","FIRE",func(): s.fire())
    var tool := action("TOOL","GUARD",func(): s.use_tool())
    tool.button_down.connect(func(): s.touch_guard = true)
    tool.button_up.connect(func(): s.touch_guard = false)
    action("RIG","RIG",func(): s.switch_rig((s.mode+1)%3))
    joystick_base = Control.new()
    joystick_base.name = "MovePad"
    joystick_base.mouse_filter = Control.MOUSE_FILTER_IGNORE
    root.add_child(joystick_base)
    var disc := PanelContainer.new()
    disc.mouse_filter = Control.MOUSE_FILTER_IGNORE
    disc.add_theme_stylebox_override("panel",style(Color("254257a3"),Color("9ad1d6c9"),70))
    disc.size = Vector2(148,148)
    joystick_base.add_child(disc)
    joystick_knob = PanelContainer.new()
    joystick_knob.name = "Thumb"
    joystick_knob.mouse_filter = Control.MOUSE_FILTER_IGNORE
    joystick_knob.add_theme_stylebox_override("panel",style(Color("8cc5cbb3"),Color("d2f7f3"),32))
    joystick_base.add_child(joystick_knob)
    joystick_knob.custom_minimum_size = Vector2(42,42)
    joystick_knob.size = Vector2(42,42)
    var mark := label(joystick_base,"MOVE",14,LIGHT)
    mark.position = Vector2(50,10)
    layout_touch(get_viewport().get_visible_rect().size)

func layout_touch(view: Vector2) -> void:
    if not touch_enabled: return
    var w: float = view.x
    var h: float = view.y
    if w < 320 or h < 320: return
    last_view = view
    info_frame.position = Vector2(10,8)
    info_frame.custom_minimum_size.x = minf(305,w-20)
    info_frame.size.x = minf(305,w-20)
    var top_y: float = 10 if w >= 660 else 232
    var top_x: float = w-252 if w >= 660 else 10
    var top_width := 78.0
    for i in range(3):
        var key: String = ["BEGIN","SAVE","RESET"][i]
        var b: Button = touch_actions[key]
        b.position = Vector2(top_x+i*(top_width+6),top_y)
        b.size = Vector2(top_width,48)
    # Four battle actions arranged as a 2x2 cluster, reachable by right thumb.
    var side_x: float = w-184
    var bottom_y: float = h-145
    var names := ["JUMP","FIRE","TOOL","RIG"]
    for i in range(4):
        var b: Button = touch_actions[names[i]]
        b.position = Vector2(side_x+float(i%2)*86,bottom_y+float(i/2)*66)
        b.size = Vector2(80,58)
    joystick_base.position = Vector2(12,h-160)
    joystick_base.size = Vector2(148,148)
    joystick_base.custom_minimum_size = Vector2(148,148)
    joystick_knob.position = Vector2(53,53)
    var layout_receipt := {
        "viewport": [w,h],
        "begin": [touch_actions["BEGIN"].position.x,touch_actions["BEGIN"].position.y],
        "reset": [touch_actions["RESET"].position.x,touch_actions["RESET"].position.y],
        "size": [78,48]
    }
    print("AF_TOUCH_LAYOUT ",JSON.stringify(layout_receipt))

func _process(_dt: float) -> void:
    if touch_enabled:
        var view := get_viewport().get_visible_rect().size
        if view != last_view: layout_touch(view)

func refresh(s) -> void:
    state.text = "%s   /   %s" % [{"READY":"FREE EXPLORE","RUNNING":"ESCORT LIVE","WON":"COURIER SAFE","LOST":"COURIER LOST"}.get(s.phase,s.phase),s.RIGS[s.mode]]
    hp.value = s.ally_hp
    numbers.text = "ALLY %d/100  BLOCKED %d  HEALED %d  TARGETS %d" % [s.ally_hp,s.prevented,s.restored,s.gallery.scored]
    last.text = "Last: %s" % s.last_result
    hint.text = "%s  /  %.1fs  Hits %d/%d" % [s.message,s.elapsed,s.hits,s.shots]
    if touch_enabled:
        touch_actions["TOOL"].text = ["GUARD","DISRUPT","HEAL"][s.mode]
        joystick_knob.position = Vector2(53,53)+s.pilot.touch_move*40.0
