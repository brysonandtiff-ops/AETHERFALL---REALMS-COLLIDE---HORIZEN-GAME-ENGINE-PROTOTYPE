extends Node
# Visual landmarks for this engineering blockout. Labels are not hero art or canon.
var last_phase := ""

func _ready() -> void:
    call_deferred("finish_lighting")

func _process(_dt: float) -> void:
    var s = get_parent()
    if s.phase != last_phase:
        last_phase = s.phase
        print("AF_RANGE_STATE ",last_phase," / ",s.RIGS[s.mode]," / ally ",s.ally_hp)

func finish_lighting() -> void:
    var s = get_parent()
    var v = s.valley
    var env: Environment = s.get_world_3d().environment
    if env != null:
        env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
        env.tonemap_exposure = 0.90
        env.ambient_light_energy = 0.50
        env.fog_density = 0.004
        env.fog_light_color = Color("827b91")
        var sky_mat: ProceduralSkyMaterial = env.sky.sky_material
        sky_mat.sky_horizon_color = Color("9b8589")
        sky_mat.sky_top_color = Color("263655")
    for child in s.get_children():
        if child is DirectionalLight3D:
            child.light_energy = 0.95
            child.rotation_degrees = Vector3(-34,-37,0)
    for mat in v.mats.values():
        if mat.emission_enabled: mat.emission_energy_multiplier = 0.25
    for z in [-7.0,1.0,6.0]:
        for side in [-1,1]:
            v.block("BrassKerb",Vector3(side*2.72,0.025,z),Vector3(0.12,0.03,3.0),Color("ad8250"))
    # Split pennants mark the end of the crossing. They flank, never block, the route.
    for side in [-1,1]:
        var x: float = side*4.1
        v.column("SignalMast",Vector3(x,2.3,-14.3),0.10,0.065,4.6,Color("665142"),8)
        v.block("SignalCrossbar",Vector3(x,4.36,-14.3),Vector3(1.55,0.085,0.11),Color("b89768"))
        v.block("RescuePennant",Vector3(x,3.47,-14.3),Vector3(1.18,1.66,0.07),Color("236d68"))
        v.block("PennantChevron",Vector3(x-0.16,3.46,-14.24),Vector3(0.11,0.52,0.05),Color("d3bf92"),false,-0.58)
        v.block("PennantChevron",Vector3(x+0.16,3.46,-14.24),Vector3(0.11,0.52,0.05),Color("d3bf92"),false,0.58)
    for j in range(7):
        v.block("CrownStair",Vector3(0,0.05+j*0.095,-19.2-j*0.72),Vector3(8.0,0.10+j*0.19,0.75),Color("8c7370"),true)
    for j in range(4):
        var x := 16.0+j*2.9
        v.arch(x,-31,0.5,Color("887581"))
    # Each region has a shape and a word as well as a color.
    marker(s,Vector3(0,3.0,-16.0),"RESCUE  /  01",Color("b7f1d4"))
    marker(s,Vector3(-22,4.1,-11.5),"RIDGE  /  02",Color("e0c3f0"))
    marker(s,Vector3(15,3.0,20),"MARKET  /  03",Color("e8c3a2"))
    marker(s,Vector3(0,4.1,26),"DRONE TRACKS  /  04",Color("f6d39e"))
    for i in range(3):
        var x := (float(i)-1.0)*10.0
        v.block("TargetLaneRail",Vector3(x,0.06,26.5),Vector3(4.6,0.12,5.1),Color("796779"),false)
        v.block("TargetLaneMark",Vector3(x,0.14,24.7),Vector3(4.6,0.06,0.26),Color("e0b083"),false)

func marker(scene, where: Vector3, text: String, tint: Color) -> void:
    var l := Label3D.new()
    l.text = text
    l.font_size = 40
    l.pixel_size = 0.015
    l.modulate = tint
    l.outline_size = 9
    l.outline_modulate = Color("272638")
    l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
    l.position = where
    scene.add_child(l)
