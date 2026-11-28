extends CanvasLayer
var state := Label.new()
var numbers := Label.new()
var hint := Label.new()
var last := Label.new()
var hp := ProgressBar.new()
var root := Control.new()
var forward := false
var back := false
var leftward := false
var rightward := false
const INK := Color("151b29ed")
const MINT := Color("9ee5d5")

func label(parent: Node, caption: String, size: int, tint: Color) -> Label:
    var item := Label.new()
    item.text = caption
    item.add_theme_font_size_override("font_size",size)
    item.add_theme_color_override("font_color",tint)
    item.mouse_filter = Control.MOUSE_FILTER_IGNORE
    parent.add_child(item)
    return item

func panel(at: Vector2, width: int) -> VBoxContainer:
    var frame := PanelContainer.new()
    var bg := StyleBoxFlat.new()
    bg.bg_color = INK
    bg.border_color = MINT
    bg.border_width_left = 3
    bg.content_margin_left = 15
    bg.content_margin_right = 16
    bg.content_margin_top = 10
    bg.content_margin_bottom = 10
    frame.add_theme_stylebox_override("panel",bg)
    root.add_child(frame)
    frame.position = at
    frame.custom_minimum_size.x = width
    frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
    var box := VBoxContainer.new()
    box.mouse_filter = Control.MOUSE_FILTER_IGNORE
    frame.add_child(box)
    return box

func button(row: Node, title: String, cb: Callable) -> Button:
    var b := Button.new()
    b.text = title
    b.focus_mode = Control.FOCUS_NONE
    b.custom_minimum_size = Vector2(54,38)
    b.pressed.connect(cb)
    row.add_child(b)
    return b

func dir_button(row: Node,title: String, field: String, scene) -> void:
    var b := button(row,title,func(): pass)
    b.button_down.connect(func(): set(field,true); move_touch(scene))
    b.button_up.connect(func(): set(field,false); move_touch(scene))

func move_touch(s) -> void:
    s.pilot.touch_move = Vector2(float(rightward)-float(leftward),float(back)-float(forward))

func setup(s) -> void:
    add_child(root)
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    root.mouse_filter = Control.MOUSE_FILTER_IGNORE
    var info := panel(Vector2(22,18),292)
    label(info,"A E T H E R F A L L    /    FIELD LAB  01",12,MINT)
    label(info,"The Unbound Reach",26,Color.WHITE)
    info.add_child(state)
    info.add_child(hp)
    hp.custom_minimum_size.y = 6
    hp.show_percentage = false
    var fill := StyleBoxFlat.new()
    fill.bg_color = MINT
    hp.add_theme_stylebox_override("fill",fill)
    info.add_child(numbers)
    numbers.add_theme_font_size_override("font_size",14)
    info.add_child(last)
    last.add_theme_font_size_override("font_size",12)
    last.modulate = Color("c9cad6")
    var cross := label(root,"+",22,Color.WHITE)
    cross.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
    var foot := PanelContainer.new()
    root.add_child(foot)
    foot.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
    var bg := StyleBoxFlat.new()
    bg.bg_color = INK
    bg.content_margin_left = 18
    bg.content_margin_top = 7
    bg.content_margin_bottom = 7
    foot.add_theme_stylebox_override("panel",bg)
    var stack := VBoxContainer.new()
    foot.add_child(stack)
    stack.add_child(hint)
    hint.add_theme_color_override("font_color",MINT)
    hint.add_theme_font_size_override("font_size",16)
    var touch := DisplayServer.is_touchscreen_available()
    if touch:
        var row := HBoxContainer.new()
        stack.add_child(row)
        dir_button(row,"◀","leftward",s)
        dir_button(row,"▲","forward",s)
        dir_button(row,"▼","back",s)
        dir_button(row,"▶","rightward",s)
        button(row,"Jump",func(): s.pilot.jump_queued = true)
        button(row,"Fire",s.fire)
        var skill := button(row,"Rig tool",s.use_tool)
        skill.button_down.connect(func(): s.touch_guard = true)
        skill.button_up.connect(func(): s.touch_guard = false)
        button(row,"Rig",func(): s.switch_rig((s.mode+1)%3))
        button(row,"Begin",s.start_trial)
        button(row,"Save spot",s.save_checkpoint)
        button(row,"Reset",s.reset_trial)
    else:
        label(stack,"WASD  Move     Arrows / mouse  Look     Space  Jump     X / click  Fire     E  Rig tool     1–3  Rig     F  Begin     C  Save spot     R  Reset",14,Color("d5d2d7"))
    foot.offset_top = -94 if touch else -65
    foot.offset_bottom = 0

func refresh(s) -> void:
    var status: String = {"READY":"FREE EXPLORE","RUNNING":"ESCORT LIVE","WON":"COURIER SAFE","LOST":"COURIER LOST"}.get(s.phase,s.phase)
    state.text = "%s   /   %s" % [status,s.RIGS[s.mode]]
    hp.value = s.ally_hp
    numbers.text = "ALLY  %d/100    •    BLOCKED  %d    •    HEALED  %d" % [s.ally_hp,s.prevented,s.restored]
    last.text = "Last: %s" % s.last_result
    hint.text = "%s    |    %.1f s    |    Hits %d/%d" % [s.message,s.elapsed,s.hits,s.shots]
