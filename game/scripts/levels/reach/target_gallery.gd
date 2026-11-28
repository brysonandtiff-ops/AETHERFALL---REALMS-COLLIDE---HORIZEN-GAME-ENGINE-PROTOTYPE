extends Node3D
# Reusable target lane: actual colliders + scoring, no character or gameplay canon.
const START_HP := 3
var targets: Array[StaticBody3D] = []
var health: Array[int] = []
var cooldown: Array[float] = []
var scored := 0
var total_hits := 0
var clock := 0.0

func _ready() -> void:
    name = "DroneTargetTracks"
    for i in range(3):
        var body := StaticBody3D.new()
        body.name = "TargetLane%d" % (i+1)
        var shape := SphereShape3D.new()
        shape.radius = 0.73
        var collision := CollisionShape3D.new()
        collision.shape = shape
        body.add_child(collision)
        var art := MeshInstance3D.new()
        var sphere := SphereMesh.new()
        sphere.radius = 0.72
        sphere.height = 1.44
        sphere.radial_segments = 8
        sphere.rings = 4
        art.mesh = sphere
        var mat := StandardMaterial3D.new()
        mat.albedo_color = Color("e0b27b") if i==0 else (Color("8bc5df") if i==1 else Color("e4a8d0"))
        mat.metallic = 0.32
        mat.roughness = 0.45
        art.material_override = mat
        body.add_child(art)
        var flash := OmniLight3D.new()
        flash.light_color = mat.albedo_color
        flash.light_energy = 0.45
        flash.omni_range = 3.2
        body.add_child(flash)
        targets.append(body)
        health.append(START_HP)
        cooldown.append(0.0)
        add_child(body)
    reset()

func reset() -> void:
    scored = 0
    total_hits = 0
    clock = 0.0
    for i in range(targets.size()):
        health[i] = START_HP
        cooldown[i] = 0.0
        targets[i].visible = true
        targets[i].collision_layer = 1
        position_target(i)

func position_target(i: int) -> void:
    var t := clock * (0.85+0.28*i) + float(i)*1.9
    var x := (float(i)-1.0)*10.0 + sin(t)*1.4
    var z := 26.5 + float(i%2)*1.7
    targets[i].position = Vector3(x,1.62+0.36*sin(t*1.4),z)

func hit(body: Object) -> bool:
    var index := targets.find(body)
    if index < 0 or cooldown[index] > 0.0:
        return false
    total_hits += 1
    health[index] -= 1
    if health[index] <= 0:
        scored += 1
        cooldown[index] = 3.0
        targets[index].visible = false
        targets[index].collision_layer = 0
    return true

func _physics_process(dt: float) -> void:
    clock += dt
    for i in range(targets.size()):
        if cooldown[i] > 0:
            cooldown[i] -= dt
            if cooldown[i] <= 0:
                health[i] = START_HP
                targets[i].visible = true
                targets[i].collision_layer = 1
        position_target(i)
