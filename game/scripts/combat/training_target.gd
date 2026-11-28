extends StaticBody3D
## Primitive target for mechanics testing only; not an approved environment asset.

var target_color := Color(0.85, 0.34, 0.27)
var hit_count := 0
var _visual: MeshInstance3D
var _reset_sequence := 0


func _ready() -> void:
    collision_layer = 1
    collision_mask = 0

    var shape := BoxShape3D.new()
    shape.size = Vector3(1.25, 2.1, 0.3)
    var collider := CollisionShape3D.new()
    collider.shape = shape
    collider.position = Vector3(0.0, 1.05, 0.0)
    add_child(collider)

    _visual = MeshInstance3D.new()
    var mesh := BoxMesh.new()
    mesh.size = shape.size
    _visual.mesh = mesh
    _visual.position = collider.position
    var material := StandardMaterial3D.new()
    material.albedo_color = target_color
    _visual.material_override = material
    add_child(_visual)


func take_hit() -> void:
    hit_count += 1
    _reset_sequence += 1
    var sequence := _reset_sequence
    var material := _visual.material_override as StandardMaterial3D
    material.albedo_color = Color(0.35, 0.96, 0.65)
    get_tree().create_timer(0.16).timeout.connect(func():
        if is_instance_valid(_visual) and sequence == _reset_sequence:
            material.albedo_color = target_color
    )
