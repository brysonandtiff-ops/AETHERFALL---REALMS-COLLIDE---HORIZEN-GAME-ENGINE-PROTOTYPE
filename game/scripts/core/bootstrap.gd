extends Node3D
## Start the isolated training test scene; preserve the existing bootstrap identity.

const PRACTICE_LAB := "res://scenes/levels/arenas/unbound_reach_mechanics_lab.tscn"


func _ready() -> void:
    $BootstrapOverlay/Root/Center/Message/PlayRange.pressed.connect(_enter_practice_lab)


func _enter_practice_lab() -> void:
    get_tree().change_scene_to_file(PRACTICE_LAB)
