extends Node
## Art pass on the existing range, not an alternate map. Decorative pieces stay out of the four ingress lanes.
const ROCK := preload("res://scenes/levels/realms/unbound_reach/reach_stone.gdshader")
const PALE := Color("b6a282")
const BASE := Color("545b56")
const BRASS := Color("aa8654")
var w
var shades := {}

func _ready() -> void:
	w = get_parent()
	call_deferred("dress")

func pier(p: Vector3, height: float, width: float) -> void:
	w.box("PierFoot",p+Vector3.UP*0.21,Vector3(width*1.45,0.42,width*1.4),BASE)
	w.box("PierShaft",p+Vector3.UP*(height/2.0+0.2),Vector3(width,height,width),PALE)
	w.box("PierCornice",p+Vector3.UP*(height+0.22),Vector3(width*1.44,0.32,width*1.4),BASE)
	w.box("CorniceTrim",p+Vector3.UP*(height+0.40),Vector3(width*1.34,0.12,width*1.3),BRASS,false)

func dress() -> void:
	# Ruin pairs frame eight short parapets; keep the axial routes open.
	for i in range(8):
		var a := TAU*(i+0.5)/8.0
		var p := Vector3(cos(a)*13.85,0,sin(a)*13.85)
		var t := Vector3(-sin(a),0,cos(a))
		pier(p-t*1.5,2.15+i%3*0.6,0.76)
		var wall: Node3D = w.box("BrokenArc",p+Vector3.UP*0.52,Vector3(2.9,1.04,0.75),PALE)
		wall.rotation.y = -a-PI/2
		var cap: Node3D = w.box("ArcCap",p+Vector3.UP*1.09,Vector3(3.10,0.16,0.91),BRASS,false)
		cap.rotation.y = wall.rotation.y
	# On each corner the remnants rise on the outer rim, not in the intended inward sightline.
	for key in ["A","B","C","D"]:
		var p: Vector3 = w.stops[key]
		var outer := Vector3(signf(p.x),0,signf(p.z)).normalized()
		var side := Vector3(-outer.z,0,outer.x)
		for i in range(3): pier(p+outer*(4.0-absf(i-1)*0.2)+side*(i-1)*2.7,3.0+i*1.1,0.82)
	for side in [-1,1]:
		pier(Vector3(33+side*7.25,6,-6.5),4.25,0.85)
		pier(Vector3(-32,2,side*5.5),4.45,1.07)
	# Obsidian hub: side ribs and roof edges leave the forward view clear.
	for side in [-1,1]:
		pier(Vector3(side*8.5,28,59),5.0,0.55)
		pier(Vector3(side*7.4,28,66),5.0,0.65)
		w.box("OverlookRoofWing",Vector3(side*8.1,33.45,62.15),Vector3(2.1,0.40,12.5),BASE,false)
	w.box("OverlookRearLintel",Vector3(0,33.45,66.7),Vector3(15.5,0.38,1.3),BASE,false)
	# Small hanging foliage clusters on the cliff faces; shared low-poly mesh.
	var leaf := SphereMesh.new()
	leaf.radial_segments = 6; leaf.rings = 3; leaf.radius = 0.72; leaf.height = 1.1
	for k in ["A","B","C","D","Rescue","Arch"]:
		var p: Vector3 = w.stops[k]
		var r := 11.6 if k=="Rescue" else (7.8 if k=="Arch" else 6.8)
		for i in range(8):
			var a := (float(i)+0.4)*TAU/8.0
			for j in range(2):
				var foliage: Node3D = w.piece("Tuft",leaf,p+Vector3(cos(a)*r,-0.25-j*0.76,sin(a)*r),Color("57724c").darkened(j*0.10))
				foliage.scale = Vector3(1.9-j*0.45,0.75+j*0.75,1.4-j*0.35)
	# Apply detail without per-object shader compilation or touching emissive role markers / glass.
	for item in w.find_children("*","MeshInstance3D",true,false):
		var mesh := item as MeshInstance3D
		var src := mesh.material_override as StandardMaterial3D
		if src==null or src.emission_enabled or src.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED: continue
		var label := str(mesh.name) if not mesh.get_parent() is StaticBody3D else str(mesh.get_parent().name)
		var kind := 0
		if label.begins_with("Basalt") or label.begins_with("HorizonIsle"): kind = 1
		elif label.begins_with("Deck") and src.albedo_color.g>src.albedo_color.r: kind = 2
		elif label.begins_with("Deck") and src.albedo_color.b>src.albedo_color.r: kind = 3
		elif not (label.begins_with("Deck") or label.begins_with("Causeway") or label.begins_with("Pier") or label.begins_with("Arch") or label.begins_with("RadialCover") or label.begins_with("BrokenArc")): continue
		var id := str(kind)+src.albedo_color.to_html()
		if not shades.has(id):
			var sm := ShaderMaterial.new()
			sm.shader = ROCK
			sm.set_shader_parameter("stone",src.albedo_color)
			sm.set_shader_parameter("surface_kind",kind)
			shades[id] = sm
		mesh.material_override = shades[id]
