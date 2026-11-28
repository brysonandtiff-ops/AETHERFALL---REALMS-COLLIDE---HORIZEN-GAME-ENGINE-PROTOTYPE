extends Node3D
## Geometry only. Y is up, -Z is north. All walk surfaces have matching physics.
const SAND := Color("d8b98c")
const STONE := Color("797f83")
const DARK := Color("334451")
const MOSS := Color("8b9c58")
const GOLD := Color("d4a552")
const RED := Color("fa513c")
const VIOLET := Color("b366ec")
const GREEN := Color("56e38e")
const CYAN := Color("55daf5")
const STOPS := {"Hub": Vector3(0,28,62), "Arena": Vector3(0,0,0), "Arch": Vector3(-32,2,0), "Rescue": Vector3(33,6,0), "A": Vector3(-36,14,-32), "B": Vector3(36,12,-32), "C": Vector3(-36,8,32), "D": Vector3(36,10,32)}
var materials := {}
var scenery := RandomNumberGenerator.new()

func material(c: Color, glow: bool = false) -> StandardMaterial3D:
	var key := c.to_html() + str(glow)
	if materials.has(key): return materials[key]
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.roughness = 0.82
	if glow:
		m.emission_enabled = true
		m.emission = c
		m.emission_energy_multiplier = 1.15
	materials[key] = m
	return m

func piece(label: String, mesh: PrimitiveMesh, pos: Vector3, col: Color, shape: Shape3D = null, glow: bool = false) -> Node3D:
	var view := MeshInstance3D.new()
	view.mesh = mesh
	view.material_override = material(col, glow)
	if not shape:
		view.name = label
		add_child(view, true)
		view.position = pos
		return view
	var body := StaticBody3D.new()
	body.name = label
	add_child(body, true)
	body.position = pos
	var collision := CollisionShape3D.new()
	collision.shape = shape
	body.add_child(collision)
	body.add_child(view)
	return body

func box(label: String, p: Vector3, size: Vector3, c: Color, solid: bool = true, glow: bool = false) -> Node3D:
	var mesh := BoxMesh.new()
	mesh.size = size
	var shape: BoxShape3D = null
	if solid:
		shape = BoxShape3D.new()
		shape.size = size
	return piece(label, mesh, p, c, shape, glow)

func drum(label: String, p: Vector3, rad: float, height: float, c: Color, solid: bool = false) -> Node3D:
	var mesh := CylinderMesh.new()
	mesh.top_radius = rad
	mesh.bottom_radius = rad
	mesh.height = height
	mesh.radial_segments = 40
	var shape: CylinderShape3D = null
	if solid:
		shape = CylinderShape3D.new()
		shape.radius = rad
		shape.height = height
	return piece(label, mesh, p, c, shape)

func shard(p: Vector3, r: float, h: float, c: Color, glow: bool = false) -> Node3D:
	var m := CylinderMesh.new()
	m.radial_segments = 5
	m.top_radius = 0.02
	m.bottom_radius = r
	m.height = h
	return piece("Shard", m, p + Vector3.UP*h/2, c, null, glow)

func ring(p: Vector3, radius: float, thickness: float, c: Color, upright: bool = false) -> Node3D:
	var m := TorusMesh.new()
	m.inner_radius = radius - thickness
	m.outer_radius = radius + thickness
	m.rings = 40
	m.ring_segments = 6
	var n := piece("Inlay",m,p,c,null,true)
	if upright: n.rotation.x = PI/2
	return n

func label3(p: Vector3, words: String, c: Color, pixels: float = 0.016) -> void:
	var t := Label3D.new()
	t.text = words
	t.font_size = 42
	t.pixel_size = pixels
	t.modulate = c
	t.outline_size = 8
	t.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	t.no_depth_test = false
	add_child(t)
	t.position = p

func bridge_segment(a: Vector3,b: Vector3,w: float,solid: bool) -> void:
	var basis3 := Basis.looking_at((b-a).normalized(),Vector3.UP)
	var mid := (a+b)/2 - basis3.y*0.25
	var body := box("Causeway",mid,Vector3(w,0.5,a.distance_to(b)+0.10),SAND,solid)
	body.basis = basis3
	for side in [-1,1]:
		var trim := box("EdgeInlay",mid+basis3.x*side*(w/2-0.15)+basis3.y*0.26,Vector3(0.16,0.05,a.distance_to(b)),GOLD,false)
		trim.basis = basis3

func bridge(a: Vector3, b: Vector3, w: float) -> void:
	if is_equal_approx(a.y,b.y):
		bridge_segment(a,b,w,true)
		return
	var low := a if a.y<b.y else b
	var high := b if a.y<b.y else a
	var forward := Vector3(high.x-low.x,0,high.z-low.z).normalized()
	var side := forward.cross(Vector3.UP).normalized()*w*0.5
	# Reach full height before the capsule meets the vertical wall of the circular deck.
	var crest := high-forward*clampf(Vector2(high.x-low.x,high.z-low.z).length()*0.10,0.65,1.5)
	var end := high+forward*0.75
	bridge_segment(low,crest,w,false)
	bridge_segment(crest,end,w,false)
	var points := PackedVector3Array()
	for offset in [-side,side]:
		for station in [low,crest,end]: points.append(station+offset)
		points.append(low+offset-Vector3.UP*0.50)
		points.append(Vector3(end.x,low.y-0.50,end.z)+offset)
	var shape := ConvexPolygonShape3D.new()
	shape.points = points
	var body := StaticBody3D.new()
	body.name = "SlopeAndLanding"
	var collision := CollisionShape3D.new()
	collision.shape = shape
	body.add_child(collision)
	add_child(body,true)

func island(p: Vector3, radius: float, depth: float, top: Color) -> void:
	drum("Deck",p-Vector3.UP*0.5,radius,1,top,true)
	for i in range(15):
		var a := TAU*i/15
		var d := scenery.randf_range(0.65,1.0)*depth
		var m := CylinderMesh.new()
		m.radial_segments = 5 + i%3
		m.top_radius = radius*scenery.randf_range(0.22,0.35)
		m.bottom_radius = 0.22
		m.height = d
		var n := piece("Basalt",m,p+Vector3(cos(a)*radius*0.73,-0.85-d/2,sin(a)*radius*0.73),STONE.darkened(scenery.randf_range(0.08,0.53)))
		n.rotation.y = a
	for i in range(3):
		var a := 0.55 + i*2.15
		var v := Vector3(cos(a),0,sin(a))
		for j in range(3):
			var drop := 4.0 + j*2.5
			box("Cascade",p+v*(radius-0.16)+Vector3(v.z*j*0.25,-drop/2,-v.x*j*0.25),Vector3(0.28,drop,0.29),Color("8ccbd4"),false)

func make_world() -> void:
	scenery.seed = 775103
	island(Vector3.ZERO,15,25,SAND)
	ring(Vector3(0,0.045,0),4.7,0.07,RED)
	ring(Vector3(0,0.045,0),14.4,0.09,GOLD)
	for i in range(8):
		var a := TAU*(i+0.5)/8
		var p := Vector3(cos(a)*10.4,0,sin(a)*10.4)
		var pillar := box("RadialCover",p+Vector3.UP*1.35,Vector3(2.1,2.7,1.2),SAND.darkened(0.18))
		pillar.rotation.y = -a
		box("Beacon",p+Vector3.UP*2.75,Vector3(0.25,0.12,0.25),RED,false,true)
	for key in ["A","B","C","D"]:
		var p: Vector3 = STOPS[key]
		island(p,7.0,19.0,MOSS)
		ring(p+Vector3.UP*0.05,4.9,0.08,VIOLET)
		label3(p+Vector3.UP*4.6,"SNIPER  /  " + key,VIOLET)
		var outward := Vector3(signf(p.x),0,signf(p.z)).normalized()
		for j in range(4):
			var crystal := shard(p+outward*4.6+Vector3(j*0.55,0,0),0.7,2.2+j*0.5,VIOLET,true)
			crystal.rotation.z = 0.1*j
	var east: Vector3 = STOPS.Rescue
	island(east,12,20,MOSS)
	ring(east+Vector3.UP*0.05,10.8,0.11,GREEN)
	for s in [-1,1]:
		box("MedicalScreen",east+Vector3(6,1.4,s*3.6),Vector3(1,2.8,4.2),STONE)
	var west: Vector3 = STOPS.Arch
	island(west,8,20,MOSS)
	for s in [-1,1]:
		box("ArchPier",west+Vector3(0,2,s*5.5),Vector3(4,4,1),STONE)
	box("ArchLintel",west+Vector3(0,4.4,0),Vector3(4,0.8,12),SAND)
	box("ShelteredWall",west+Vector3(-3,1.9,-3.9),Vector3(7.5,3.8,1.1),STONE)
	ring(west+Vector3(-4,2.15,1),2.05,0.1,CYAN,true)
	for z in [-1,1]:
		var junction := Vector3(0,0,31*z)
		island(junction,5,13,MOSS)
		bridge(Vector3(0,0,14*z),junction,5)
		for x in [-1,1]:
			var key := ("A" if x<0 else "B") if z<0 else ("C" if x<0 else "D")
			var ledge: Vector3 = STOPS[key]
			bridge(junction+Vector3(3.5*x,0,0),ledge-Vector3(x*6.8,0,0),4.6)
			var deck := west if x<0 else east
			bridge(deck+Vector3(0,0,z*(7.8 if x<0 else 11.8)),ledge-Vector3(0,0,z*6.8),4.2)
	bridge(Vector3(14,0,0),east-Vector3(11.8,0,0),5)
	bridge(Vector3(-14,0,0),west+Vector3(7.8,0,0),5)
	var hub: Vector3 = STOPS.Hub
	island(hub,12.5,24,DARK)
	ring(hub+Vector3.UP*0.05,11.6,0.09,CYAN)
	for i in range(12):
		var a := -PI+PI*(float(i)+0.5)/12
		var p := hub+Vector3(cos(a)*11.9,0,sin(a)*11.9)
		var rail := box("ObservationSill",p+Vector3.UP*0.35,Vector3(3.2,0.7,0.32),STONE)
		rail.rotation.y = -a-PI/2
		var glass := box("ObservationGlass",p+Vector3.UP*1.13,Vector3(3.15,0.87,0.10),CYAN,false)
		glass.rotation.y = rail.rotation.y
		var gm := StandardMaterial3D.new()
		gm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		gm.albedo_color = Color(0.45,0.86,0.98,0.16)
		(glass as MeshInstance3D).material_override = gm
		if i%3==0: box("Frame",p+Vector3.UP*2.6,Vector3(0.23,5.2,0.26),DARK)
	island(Vector3(0,1,-105),16,31,MOSS)
	for i in range(7):
		var a := TAU*i/7
		var pos := Vector3(cos(a)*6.8,1,sin(a)*6.8-105)
		box("SanctumPier",pos+Vector3.UP*7,Vector3(2.4,14,2.7),SAND)
		shard(pos+Vector3.UP*14,2.3,12.0+i,STONE)
	shard(Vector3(0,1,-105),5.5,42,SAND)
	shard(Vector3(0,15,-104),1.5,28,CYAN,true)
	for i in range(18):
		var a := TAU*i/18
		var p := Vector3(cos(a)*scenery.randf_range(105,146),scenery.randf_range(-17,12),sin(a)*108)
		var r := scenery.randf_range(2,5)
		var m := CylinderMesh.new()
		m.top_radius = r
		m.bottom_radius = 0.15
		m.radial_segments = 7
		m.height = r*2.3
		piece("HorizonIsle",m,p,STONE)
