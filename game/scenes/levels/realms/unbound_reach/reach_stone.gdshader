shader_type spatial;
render_mode specular_disabled;
uniform vec4 stone : source_color = vec4(0.55, 0.54, 0.48, 1.0);
uniform int surface_kind = 0; // 0 cut stone, 1 natural cliff, 2 planted deck, 3 alloy
varying vec3 wp;
varying vec3 wn;
float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise2(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p); f = f*f*(3.0-2.0*f);
    return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);
}
void vertex() { wp = (MODEL_MATRIX * vec4(VERTEX,1.0)).xyz; wn = normalize(MODEL_NORMAL_MATRIX * NORMAL); }
void fragment() {
    vec3 n = abs(wn);
    vec2 uv = n.y > 0.65 ? wp.xz : (n.x > n.z ? wp.zy : wp.xy);
    float grain = noise2(uv*3.7)*0.12 + noise2(uv*0.44)*0.20;
    vec3 c = stone.rgb * (0.72 + grain);
    if(surface_kind==0 || surface_kind==3) {
        vec2 p = uv / (surface_kind==3 ? vec2(2.5,1.35) : vec2(2.15,1.05));
        p.x += 0.5*mod(floor(p.y),2.0);
        vec2 edge = min(fract(p), 1.0-fract(p));
        vec2 aa = max(fwidth(p),vec2(0.002));
        float joint = min(smoothstep(0.007,0.012+aa.x,edge.x),smoothstep(0.009,0.02+aa.y,edge.y));
        c *= mix(0.53, 0.91 + 0.16*h(floor(p)),joint);
    } else if(surface_kind==1) {
        float band = sin((wp.y+noise2(wp.xz*0.28)*1.5)*2.6);
        c *= 0.85+0.15*band;
    } else {
        float patch = smoothstep(0.40,0.70,noise2(wp.xz*0.62));
        c = mix(c * vec3(0.70,0.85,0.58), vec3(0.15,0.17,0.10), patch*0.72);
    }
    ALBEDO = c;
    ROUGHNESS = surface_kind==3 ? 0.53 : 0.91;
}
