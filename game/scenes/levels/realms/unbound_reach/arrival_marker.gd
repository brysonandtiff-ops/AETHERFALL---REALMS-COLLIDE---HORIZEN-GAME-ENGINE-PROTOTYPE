extends Marker3D
## An arrival marker moves the player start, never the reference footprint.
## Child _ready runs before range _ready, so initial spawn and fall recovery agree.
@export var destination: String = "Hub"

func _ready() -> void:
	var level = get_parent()
	if not level.stops.has(destination):
		push_error("Unknown range destination: " + destination)
		return
	var arrivals: Dictionary = level.stops.duplicate()
	arrivals[destination] = position
	level.stops = arrivals
