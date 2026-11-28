extends Node3D
## Functional greybox harness for future Unbound Reach; not the approved map/art.
## Nodes and geometry are generated so no locked source assets are replaced.

const PILOT_SCRIPT = preload("res://scripts/characters/training_player.gd")
const TARGET_SCRIPT = preload("res://scripts/combat/training_target.gd")
const TOUCH_HUD_SCRIPT = preload("res://scripts/ui/mobile_lab_hud.gd")

var player: CharacterBody3D


func _ready() -> void:
    _make_lighting()
    _make_geometry()
    _make_player()
    _make_controls()


func _make_lighting() -> void:
    var environment_node := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color(0.038, 0.052, 0.081)
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color(0.35, 0.42, 0.58)
    environment.ambient_light_energy = 1.1
    environment_node.environment = environment
    add_child(environment_node)

    var sunlight := DirectionalLight3D.new()
    sunlight.rotation_degrees = Vector3(-55.0, -34.0, 0.0)
    sunlight.light_energy = 1.3
    add_child(sunlight)


func _make_geometry() -> void:
    _block("TestingFloor", Vector3(0.0, -0.5, 0.0), Vector3(70.0, 1.0, 70.0), Color(0.20, 0.24, 0.29))
    _block("BackBoundary", Vector3(0.0, 1.6, -35.0), Vector3(70.0, 3.2, 0.8), Color(0.12, 0.15, 0.20))
    _block("FrontBoundary", Vector3(0.0, 1.6, 35.0), Vector3(70.0, 3.2, 0.8), Color(0.12, 0.15, 0.20))
    _block("LeftBoundary", Vector3(-35.0, 1.6, 0.0), Vector3(0.8, 3.2, 70.0), Color(0.12, 0.15, 0.20))
    _block("RightBoundary", Vector3(35.0, 1.6, 0.0), Vector3(0.8, 3.2, 70.0), Color(0.12, 0.15, 0.20))

    # Unbound Reach zones are placeholder test markers, not finished level design.
    _pad("BrawlingZoneMarker", Vector3(0.0, 0.025, -11.0), Vector3(18.0, 0.05, 16.0), Color(0.53, 0.25, 0.17))
    _pad("LongRangeMarker", Vector3(-23.0, 0.025, -14.0), Vector3(16.0, 0.05, 22.0), Color(0.28, 0.22, 0.52))
    _pad("SupportZoneMarker", Vector3(22.0, 0.025, 11.0), Vector3(18.0, 0.05, 15.0), Color(0.13, 0.40, 0.31))
    _pad("DroneZoneMarker", Vector3(22.0, 0.025, -17.0), Vector3(18.0, 0.05, 16.0), Color(0.15, 0.40, 0.50))

    _block("BrawlingCoverLeft", Vector3(-5.0, 0.9, -8.0), Vector3(2.5, 1.8, 1.7), Color(0.30, 0.32, 0.37))
    _block("BrawlingCoverRight", Vector3(5.0, 0.9, -8.0), Vector3(2.5, 1.8, 1.7), Color(0.30, 0.32, 0.37))
    _block("LongRangePlatform", Vector3(-23.0, 0.65, -12.0), Vector3(8.0, 1.3, 8.0), Color(0.27, 0.25, 0.37))
    _block("SupportCover", Vector3(20.0, 0.8, 8.0), Vector3(2.0, 1.6, 4.0), Color(0.27, 0.32, 0.30))

    _target("CentralTrainingTarget", Vector3(0.0, 0.0, -9.0))
    _target("BrawlingTargetTwo", Vector3(6.0, 0.0, -16.0))
    _target("LongRangeTarget", Vector3(-24.0, 1.3, -23.0))
    _target("SupportDummyTarget", Vector3(25.0, 0.0, 9.0))
    _target("DroneTrackStaticPlaceholder", Vector3(23.0, 0.0, -20.0))


func _block(title: String, where: Vector3, dimensions: Vector3, tint: Color) -> void:
    var body := StaticBody3D.new()
    body.name = title
    body.position = where
    body.collision_layer = 1
    body.collision_mask = 0

    var shape := BoxShape3D.new()
    shape.size = dimensions
    var collision := CollisionShape3D.new()
    collision.shape = shape
    body.add_child(collision)

    var visual := _box_visual(dimensions, tint)
    body.add_child(visual)
    add_child(body)


func _pad(title: String, where: Vector3, dimensions: Vector3, tint: Color) -> void:
    var visual := _box_visual(dimensions, tint)
    visual.name = title
    visual.position = where
    add_child(visual)


func _box_visual(dimensions: Vector3, tint: Color) -> MeshInstance3D:
    var visual := MeshInstance3D.new()
    var mesh := BoxMesh.new()
    mesh.size = dimensions
    visual.mesh = mesh
    var material := StandardMaterial3D.new()
    material.albedo_color = tint
    visual.material_override = material
    return visual


func _target(title: String, where: Vector3) -> void:
    var target = TARGET_SCRIPT.new()
    target.name = title
    target.position = where
    add_child(target)


func _make_player() -> void:
    player = PILOT_SCRIPT.new()
    player.name = "TrainingPlayer"
    player.position = Vector3(0.0, 1.2, 7.0)
    add_child(player)


func _make_controls() -> void:
    var layer := CanvasLayer.new()
    layer.name = "MobileControls"
    add_child(layer)
    var hud = TOUCH_HUD_SCRIPT.new()
    hud.name = "TouchHUD"
    hud.bind_player(player)
    layer.add_child(hud)
