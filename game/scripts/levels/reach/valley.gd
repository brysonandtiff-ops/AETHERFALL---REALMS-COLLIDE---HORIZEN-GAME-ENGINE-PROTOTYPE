extends Node3D
# Units: metres, Y up. Named modular blockout pieces; no canonical hero art.
const STONE := Color("776a6b")
const PALE := Color("bf9580")
const DARK := Color("474252")
const TRIM := Color("b7a491")
const MOSS := Color("506663")
const GOLD := Color("dba76a")
const BLUE := Color("70dce1")
var mats: Dictionary = {}
var rng := RandomNumberGenerator.new()

func mat(tint: Color, glow: bool = false) -> StandardMaterial3D:
    var key := tint.to_html() + str(glow)
    if mats.has(key): return mats[key]
    var m := StandardMaterial3D.new()
    m.albedo_color = tint
    m.roughness = 0.86
    if glow:
        m.emission_enabled = true
        m.emission = tint
        m.emission_energy_multiplier = 1.2
    mats[key] = m
    return m

func mesh_part(tag: String, shape: Mesh, p: Vector3, tint: Color, glow: bool = false) -> MeshInstance3D:
    var item := MeshInstance3D.new()
    item.name = tag
    item.mesh = shape
    item.material_override = mat(tint, glow)
    item.position = p
    add_child(item, true)
    return item

func block(tag: String, p: Vector3, size: Vector3, tint: Color, solid: bool = false, roll: float = 0.0) -> MeshInstance3D:
    var box := BoxMesh.new()
    box.size = size
    var item := mesh_part(tag, box, p, tint)
    item.rotation.z = roll
    if solid:
        var body := StaticBody3D.new()
        var c := CollisionShape3D.new()
        var s := BoxShape3D.new()
        s.size = size
        c.shape = s
        item.add_child(body)
        body.add_child(c)
    return item

func column(tag: String, p: Vector3, base: float, tip: float, height: float, tint: Color, sides: int = 6, glow: bool = false) -> MeshInstance3D:
    var m := CylinderMesh.new()
    m.radial_segments = sides
    m.rings = 0
    m.bottom_radius = base
    m.top_radius = tip
    m.height = height
    return mesh_part(tag, m, p, tint, glow)

func arch(x: float, z: float, scale_factor: float, tint: Color) -> void:
    var s := scale_factor
    for side in [-1.0, 1.0]:
        var px: float = x + float(side)*3.0*s
        block("Plinth", Vector3(px,0.32*s,z),Vector3(1.8,0.64,1.8)*s,DARK,true)
        column("FlutedPier",Vector3(px,2.9*s,z),0.71*s,0.55*s,5.2*s,tint,8)
        block("Capital",Vector3(px,5.5*s,z),Vector3(1.55,0.45,1.55)*s,TRIM)
        for j in range(5):
            var t := (j+0.5)/5.0
            var xx: float = x + float(side)*(3.0-2.96*t)*s
            var yy := (5.6+2.8*sin(t*1.12))*s
            block("Voussoir",Vector3(xx,yy,z),Vector3(0.98,0.60,1.05)*s,tint,false,-float(side)*0.66)
        column("Pinnacle",Vector3(px,6.18*s,z),0.42*s,0.03*s,1.4*s,PALE,4)
    column("Keystone",Vector3(x,8.3*s,z),0.46*s,0.12*s,1.35*s,GOLD,4)

func crystal(p: Vector3, h: float, tint: Color) -> void:
    column("CrystalBase",p+Vector3.UP*h*0.24,h*0.23,h*0.19,h*0.48,tint,5)
    column("CrystalTip",p+Vector3.UP*h*0.74,h*0.19,0.0,h*0.52,tint,5,true)

func build() -> void:
    name = "ValleyArchitecture"
    rng.seed = 411702
    # The player can walk either bank, take the bridge, or loop via the west shelf.
    block("SouthLanding",Vector3(0,-1.25,20),Vector3(58,2.5,24),STONE,true)
    block("NorthLanding",Vector3(0,-1.25,-25),Vector3(58,2.5,26),STONE,true)
    block("WestLoop",Vector3(-23,-1.25,-2),Vector3(10,2.5,22),MOSS,true)
    block("BridgeDeck",Vector3(0,-0.57,-2),Vector3(6.4,1.14,21),PALE,true)
    for i in range(12):
        var z := 8.0-i*1.82
        block("ExpansionJoint",Vector3(0,0.013,z),Vector3(6.3,0.018,0.045),DARK)
        if i%2 == 0:
            for s in [-1,1]:
                block("BridgePylon",Vector3(3.1*s,-1.9,z),Vector3(0.48,5.6,0.65),TRIM,true)
                column("Waylight",Vector3(3.1*s,1.0,z),0.14,0.08,0.3,BLUE,6,true)
    block("SunkenChannel",Vector3(0,-8,-2),Vector3(170,0.2,34),Color("31546a"))
    # Fractured basalt ribs support the two cliff lips.
    for i in range(28):
        var x := -30.0+i*2.2
        for z in [-13.9,10.3]:
            column("RiftStratum",Vector3(x,-5.0,z+rng.randf_range(-0.6,0.6)),rng.randf_range(1.2,2.0),1.5,rng.randf_range(6.0,8.0),DARK.lerp(STONE,rng.randf()*0.7),5)
    arch(0,-16,1.0,PALE)
    arch(-16,-26,0.8,TRIM)
    arch(15,20,0.72,PALE)
    for x in [-10.0,10.0]:
        block("TowerFoundation",Vector3(x,0.6,-26),Vector3(6,1.2,7),DARK,true)
        block("Keep",Vector3(x,4,-26),Vector3(4.7,6,4.7),STONE,true)
        for h in [2.0,6.8]:
            block("Cornice",Vector3(x,h,-26),Vector3(5.1,0.32,5.1),TRIM)
        for off in [-1.8,1.8]:
            column("Buttress",Vector3(x+float(off),4.2,-23.8),0.74,0.4,8.5,PALE,5)
            column("Spire",Vector3(x+float(off),9,-23.8),0.65,0,2.7,DARK,5)
        column("SlateRoof",Vector3(x,9.2,-26),3.6,0.15,4.6,DARK,4)
        block("HeraldicBanner",Vector3(x,4.2,-23.61),Vector3(1.12,3.1,0.06),Color("823c62"))
        block("BannerStitch",Vector3(x,4.2,-23.55),Vector3(0.1,2.7,0.04),GOLD)
    # Walkable shallow ridge on the west bank and emerald return station.
    var ramp := block("RidgeRamp",Vector3(-23,1.0,-0.5),Vector3(5.5,0.38,12),TRIM,true)
    ramp.rotation.x = 0.19
    block("VioletOverlook",Vector3(-23,0.98,-10),Vector3(7,1.96,8),DARK,true)
    for j in range(9):
        crystal(Vector3(-26+rng.randf_range(-1,1),1.96,-9+rng.randf_range(-2.4,2.4)),rng.randf_range(1.1,3.4),Color("9864c0"))
    for x in [-3.7,3.7]: crystal(Vector3(x,0,-19),2.15,Color("4bbda4"))
    for j in range(12):
        var x := rng.randf_range(-20,20)
        var z := rng.randf_range(22,30)
        block("MarketCover",Vector3(x,0.52,z),Vector3(1.5,1.04,1.3),PALE,true)
    # Faceted mountains and broken watchtowers form the skyline, outside the play area.
    for j in range(65):
        var phi := TAU*j/65.0
        var rr := rng.randf_range(57,85)
        var h := rng.randf_range(10,27)
        var p := Vector3(sin(phi)*rr,h/2.0-7,cos(phi)*rr)
        var mountain := column("FarCrag",p,rng.randf_range(7,14),rng.randf_range(0.2,2.1),h,DARK.lerp(MOSS,rng.randf()*0.8),5)
        mountain.rotation.y = rng.randf_range(0,PI)
    for j in range(18):
        var p := Vector3(rng.randf_range(-32,32),0,rng.randf_range(-39,-32))
        column("RuinedColonnade",p+Vector3.UP*2,0.65,0.48,rng.randf_range(3,7),STONE,7)
