extends Node3D
## Visual-only seeded scenery. The static environment owns the only Sky resource.
const CLOUD_CODE := """
shader_type spatial;
render_mode unshaded,cull_front,depth_draw_never,fog_disabled;
varying vec3 direction;
float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float n(vec2 p){vec2 i=floor(p),u=fract(p);u=u*u*(3.0-2.0*u);return mix(mix(h(i),h(i+vec2(1,0)),u.x),mix(h(i+vec2(0,1)),h(i+vec2(1)),u.x),u.y);}
float fb(vec2 p){float v=0.0;float a=0.54;for(int i=0;i<4;i++){v+=a*n(p);p=mat2(vec2(1.70,1.11),vec2(-1.11,1.70))*p+12.6;a*=0.47;}return v;}
void vertex(){direction=VERTEX;}
void fragment(){vec3 d=normalize(direction);float y=d.y;
 vec3 air=mix(vec3(.54,.69,.80),vec3(.10,.28,.50),smoothstep(-.03,.79,y));
 vec2 q=d.xz/(max(abs(y),.027)+.15);
 float cloud=fb(q*3.8+vec2(11.,5.));float small=fb(q*9.+18.);
 vec3 mist=mix(vec3(.25,.40,.54),vec3(.95,.94,.88),smoothstep(.25,.73,cloud+.09*small));
 if(y<0.){air=mix(air,mist,smoothstep(.005,.14,-y));}
 else{float a=smoothstep(.44,.65,cloud+.08*small)*smoothstep(.01,.12,y);air=mix(air,mix(vec3(.60,.69,.76),vec3(.94,.92,.84),small),a*.85);}
 ALBEDO=air;}
"""
var rng := RandomNumberGenerator.new()
var groups := {}
var meshes := {}

func batch(key: String, m: Mesh, color: Color) -> void:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = 0.92
	meshes[key] = [m,mat]
	groups[key] = []

func put(key: String, p: Vector3, size: Vector3, yaw: float = 0.0, lean: float = 0.0) -> void:
	var basis3 := Basis(Vector3.UP,yaw)*Basis(Vector3.FORWARD,lean)*Basis.from_scale(size)
	groups[key].append(Transform3D(basis3,p))

func facet(top: float, bottom: float, sides: int) -> CylinderMesh:
	var m := CylinderMesh.new()
	m.radial_segments = sides; m.rings = 0
	m.height = 1.0; m.top_radius = top; m.bottom_radius = bottom
	return m

func tree(p: Vector3, s: float) -> void:
	put("Bark",p+Vector3.UP*s*.47,Vector3(s*.12,s*.94,s*.12),s)
	for j in range(3):
		var v := Vector3(cos(j*2.1)*s*.28,s*(0.85+j*.075),sin(j*2.1)*s*.28)
		put("CanopyLight" if j==2 else "Canopy",p+v,Vector3(s*.93,s*.46,s*.72),2.4*j)

func _ready() -> void:
	call_deferred("build")

func build() -> void:
	var w = get_parent()
	var shader := Shader.new(); shader.code = CLOUD_CODE
	var sm := ShaderMaterial.new(); sm.shader = shader
	var globe := SphereMesh.new(); globe.height = 536.0; globe.radius = 268.0; globe.radial_segments=40; globe.rings=16
	var clouds := MeshInstance3D.new(); clouds.name="CloudHorizon"; clouds.mesh=globe; clouds.material_override=sm
	clouds.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(clouds)
	var bulb := SphereMesh.new(); bulb.radial_segments=7; bulb.rings=3; bulb.height=1; bulb.radius=.5
	batch("Cliff",facet(.50,.22,7),Color("65747c"))
	batch("Strata",facet(.48,.38,7),Color("87969a"))
	batch("Spur",facet(.1,.48,5),Color("758689"))
	batch("BrokenBed",facet(.46,.37,9),Color("657955"))
	batch("Bark",facet(.31,.48,5),Color("584d40"))
	batch("Canopy",bulb,Color("456447")); batch("CanopyLight",bulb,Color("73935a"))
	batch("Goldstone",facet(.37,.50,6),Color("ac9e83")); batch("Pinnacle",facet(.01,.48,6),Color("a9bab7"))
	rng.seed = 240177
	for i in range(18):
		var x := (1.0 if i%2==0 else -1.0)*rng.randf_range(67.0,105.0)
		var p := Vector3(x,rng.randf_range(-7.0,7.0),-101.0+floorf(i/2.0)*17.0)
		var r := rng.randf_range(7.5,16.0)
		for j in range(5):
			var a := j*2.40
			var v := p+Vector3(cos(a)*r*.56,rng.randf_range(-1.,1.),sin(a)*r*.53)
			var depth := rng.randf_range(10.0,25.0)
			put("Cliff",v-Vector3.UP*depth*.5,Vector3(r,depth,r*.8),a)
			put("Strata",v-Vector3.UP*2.2,Vector3(r*1.01,1.2,r*.82),a)
			put("BrokenBed",v+Vector3.UP*.12,Vector3(r*1.02,.95,r*.85),a)
			put("Spur",v-Vector3.UP*(depth*.74),Vector3(r*.4,depth*.56,r*.30),a,.16)
			if j%2==0: tree(v+Vector3.UP*.58,rng.randf_range(1.5,3.6))
		if i%3==0:
			put("Goldstone",p+Vector3.UP*2.5,Vector3(2.2,5.0,2.1),0.3)
			put("Pinnacle",p+Vector3.UP*6.65,Vector3(1.9,3.4,1.8),0.3)
	for key in ["A","B","C","D","Arch","Rescue"]:
		var p: Vector3 = w.stops[key]
		var dir := Vector3(p.x,0,p.z).normalized()
		var side := Vector3(-dir.z,0,dir.x)
		var radius := 10.7 if key=="Rescue" else (7.0 if key=="Arch" else 5.8)
		for k in range(3): tree(p+dir*(radius-.4)+side*(k-1)*1.6,rng.randf_range(1.2,2.2))
	for k in range(30):
		var a := TAU*k/30.0
		var ht := rng.randf_range(18.,56.)
		var p := Vector3(cos(a)*216,-19+ht*.5,sin(a)*193-24)
		put("Spur",p,Vector3(rng.randf_range(32.,65.),ht,rng.randf_range(20.,48.)),a,.19)
	for key: String in groups:
		var transforms: Array = groups[key]
		var mm := MultiMesh.new(); mm.transform_format=MultiMesh.TRANSFORM_3D; mm.mesh=meshes[key][0]; mm.instance_count=transforms.size()
		for i in range(transforms.size()): mm.set_instance_transform(i,transforms[i])
		var node := MultiMeshInstance3D.new(); node.name=key; node.multimesh=mm; node.material_override=meshes[key][1]
		add_child(node)
