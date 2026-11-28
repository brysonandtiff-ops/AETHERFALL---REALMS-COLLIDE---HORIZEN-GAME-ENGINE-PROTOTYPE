extends RefCounted
## First-level input adapter. Uses Godot logical controls, not device-specific raw IDs.
const BUTTONS := {JOY_BUTTON_A:"A", JOY_BUTTON_B:"B", JOY_BUTTON_X:"X", JOY_BUTTON_Y:"Y", JOY_BUTTON_LEFT_SHOULDER:"LB", JOY_BUTTON_RIGHT_SHOULDER:"RB", JOY_BUTTON_LEFT_STICK:"LS", JOY_BUTTON_RIGHT_STICK:"RS", JOY_BUTTON_DPAD_UP:"D-up", JOY_BUTTON_DPAD_DOWN:"D-down", JOY_BUTTON_DPAD_LEFT:"D-left", JOY_BUTTON_DPAD_RIGHT:"D-right", JOY_BUTTON_BACK:"View", JOY_BUTTON_START:"Menu"}
const BINDS := {"Aim":"LT", "Fire":"RT", "Jump":"A", "Interact":"X", "Sprint":"LS", "Hub":"Y", "Reset drill":"D-down"}
const TOKENS := ["A","B","X","Y","LB","RB","LT","RT","LS","RS","D-up","D-down","D-left","D-right","View"]
# label: [default, minimum, maximum, adjustment step]
const NUM := {"Move deadzone":[0.15,0.0,0.6,0.01],"Look deadzone":[0.10,0.0,0.6,0.01],"Horizontal speed":[190.0,20.0,440.0,5.0],"Vertical speed":[145.0,20.0,440.0,5.0],"ADS multiplier":[0.45,0.05,1.0,0.01],"Aim curve":[1.6,1.0,3.0,0.1],"LT threshold":[0.25,0.1,0.95,0.01],"RT threshold":[0.35,0.1,0.95,0.01]}
const FLAGS := ["Swap sticks","Invert X","Invert Y","Toggle aim","Toggle sprint"]
const PRESETS := ["Standard","Bumper jumper","Southpaw"]
var binds: Dictionary
var settings: Dictionary
var preset := 0
var file_path := "user://unbound_reach_pad_v1.cfg"
var menu := false
var device := -1
var active := false
var held := {}
var axes := PackedFloat32Array([0,0,0,0])
var aim_latch := false
var sprint_latch := false
var row := 0
var note := ""

func _init() -> void:
	defaults()

func defaults() -> void:
	binds = BINDS.duplicate()
	settings = {}
	for key in NUM: settings[key] = NUM[key][0]
	for key in FLAGS: settings[key] = false
	preset = 0

func clear_state() -> void:
	held.clear()
	axes.fill(0)
	aim_latch = false
	sprint_latch = false

func reset_device() -> void:
	clear_state()
	device = -1
	active = false
	menu = false

func glyph(action: String) -> String:
	return str(binds.get(action,"—"))

func rebind(action: String, token: String) -> void:
	if not binds.has(action) or token not in TOKENS: return
	var other: Variant = binds.find_key(token)
	if other != null: binds[other] = binds[action]
	binds[action] = token
	aim_latch = false
	sprint_latch = false

func load_profile() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(file_path) != OK or cfg.get_value("profile","version",0) != 1: return
	var seen := {}
	var next := {}
	for a in BINDS:
		var t: Variant = cfg.get_value("binds",a,"")
		if typeof(t) != TYPE_STRING or t not in TOKENS or seen.has(t): return
		seen[t] = true
		next[a] = t
	binds = next
	for k in NUM:
		var v: Variant = cfg.get_value("settings",k,NUM[k][0])
		if typeof(v) in [TYPE_FLOAT,TYPE_INT] and is_finite(float(v)):
			settings[k] = clampf(float(v),float(NUM[k][1]),float(NUM[k][2]))
	for k in FLAGS:
		var v: Variant = cfg.get_value("settings",k,false)
		if typeof(v) == TYPE_BOOL: settings[k] = v
	var index: Variant = cfg.get_value("profile","preset",0)
	if typeof(index) == TYPE_INT: preset = clampi(int(index),0,PRESETS.size()-1)

func save_profile() -> Error:
	var cfg := ConfigFile.new()
	cfg.set_value("profile","version",1)
	cfg.set_value("profile","preset",preset)
	for a in binds: cfg.set_value("binds",a,binds[a])
	for k in settings: cfg.set_value("settings",k,settings[k])
	return cfg.save(file_path)

func stick(first: int, deadzone: float, exponent: float) -> Vector2:
	var raw := Vector2(axes[first],axes[first+1])
	var length := raw.length()
	if menu or length <= deadzone: return Vector2.ZERO
	return raw.normalized() * pow(clampf((length-deadzone)/(1.0-deadzone),0,1),exponent)

func move() -> Vector2:
	return stick(2 if settings["Swap sticks"] else 0, settings["Move deadzone"], 1.0)

func look() -> Vector2:
	var v := stick(0 if settings["Swap sticks"] else 2, settings["Look deadzone"], settings["Aim curve"])
	v.x *= -1 if settings["Invert X"] else 1
	v.y *= -1 if settings["Invert Y"] else 1
	return v

func aiming() -> bool:
	return not menu and (aim_latch if settings["Toggle aim"] else bool(held.get(glyph("Aim"),false)))

func running() -> bool:
	return not menu and (sprint_latch if settings["Toggle sprint"] else bool(held.get(glyph("Sprint"),false)))

func rows() -> Array:
	return ["Layout"] + binds.keys() + NUM.keys() + FLAGS

func adjust(key: String, direction: int) -> void:
	if key == "Layout":
		preset = posmod(preset+direction,PRESETS.size())
		binds = BINDS.duplicate()
		settings["Swap sticks"] = preset == 2
		if preset == 1: rebind("Jump","LB")
	elif binds.has(key): rebind(key,TOKENS[posmod(TOKENS.find(glyph(key))+direction,TOKENS.size())])
	elif NUM.has(key): settings[key] = clampf(float(settings[key])+direction*float(NUM[key][3]),float(NUM[key][1]),float(NUM[key][2]))
	elif key in FLAGS: settings[key] = not settings[key]

func menu_text() -> String:
	var entries := rows()
	var text := "CONTROLLER SETTINGS   •   THE UNBOUND REACH\nD-pad ↑↓ select   ←→ change   A / Menu save   B cancel\n\n"
	var start := clampi(row-3,0,maxi(entries.size()-7,0))
	for i in range(start,mini(start+7,entries.size())):
		var key: String = entries[i]
		var val := ""
		if key == "Layout": val = str(PRESETS[preset]) + " (base)"
		elif binds.has(key): val = glyph(key)
		elif key in FLAGS: val = "On" if settings[key] else "Off"
		else: val = "%.2f" % float(settings[key])
		text += ("▶  " if i == row else "     ") + key + "   :   " + val + "\n"
	return text + "\n%d / %d    %s" % [row+1,entries.size(),note]

func set_menu(value: bool) -> void:
	menu = value
	axes.fill(0)
	aim_latch = false
	sprint_latch = false
	# Block anything held across the transition until a fresh release.
	for token in held.keys():
		if held[token]: blocked[token] = true
	held.clear()

var blocked := {}
var snapshot := {}

func packet(e: InputEvent) -> String:
	if not (e is InputEventJoypadButton or e is InputEventJoypadMotion): return ""
	var token := ""
	var down := false
	if e is InputEventJoypadMotion:
		if device == -1 and absf(e.axis_value)<0.2: return ""
		if device != -1 and device != e.device: return ""
		if int(e.axis) in [0,1,2,3]:
			if not menu: axes[int(e.axis)] = e.axis_value
			if absf(e.axis_value)>0.2:
				device = e.device
				active = true
			return ""
		if e.axis not in [JOY_AXIS_TRIGGER_LEFT,JOY_AXIS_TRIGGER_RIGHT]: return ""
		token = "LT" if e.axis == JOY_AXIS_TRIGGER_LEFT else "RT"
		var gate := float(settings[token+" threshold"])
		var latched := bool(held.get(token,false)) or blocked.has(token)
		down = e.axis_value >= (gate - 0.08 if latched else gate)
	elif e is InputEventJoypadButton:
		token = str(BUTTONS.get(e.button_index,""))
		down = e.pressed
	if token.is_empty() or (device != -1 and device != e.device): return ""
	if down:
		device = e.device
		active = true
	if blocked.has(token):
		if not down: blocked.erase(token)
		return ""
	if bool(held.get(token,false)) == down: return ""
	held[token] = down
	if not down: return ""
	if menu:
		match token:
			"D-up": row = posmod(row-1,rows().size())
			"D-down": row = posmod(row+1,rows().size())
			"D-left", "D-right": adjust(str(rows()[row]),1 if token == "D-right" else -1)
			"A", "Menu":
				if save_profile() == OK: set_menu(false)
				else: note = "Save failed; B cancels"
			"B":
				binds = snapshot["binds"].duplicate()
				settings = snapshot["settings"].duplicate()
				preset = int(snapshot["preset"])
				set_menu(false)
		return ""
	if token == "Menu":
		snapshot = {"binds":binds.duplicate(),"settings":settings.duplicate(),"preset":preset}
		note = ""
		set_menu(true)
		return ""
	var action: Variant = binds.find_key(token)
	if action == null: return ""
	if action == "Aim" and settings["Toggle aim"]: aim_latch = not aim_latch
	if action == "Sprint" and settings["Toggle sprint"]: sprint_latch = not sprint_latch
	return str(action)
