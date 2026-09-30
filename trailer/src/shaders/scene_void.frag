#version 330
//#include common
in vec2 vUV;
out vec4 fragColor;
uniform float uBeam;       // light shaft from above
uniform float uBeamX;      // beam top x (screen units, 0 = centre)
uniform float uBeamTilt;
uniform float uDust;
uniform vec3  uBeamCol;
uniform vec3  uBg;
uniform float uGlowR;      // soft glow in the middle (memory light)
uniform vec3  uGlowCol;

float motes(vec2 p, float scale, float speed, float seed, float size){
    vec2 q = p * scale + vec2(sin(uTime * 0.13 + seed) * 0.6, -uTime * speed + seed * 13.0);
    vec2 ip = floor(q), fp = fract(q) - 0.5;
    float acc = 0.0;
    for(int j=-1;j<=1;j++) for(int i=-1;i<=1;i++){
        vec2 g = vec2(i,j);
        vec2 h = hash22(ip + g + seed);
        if(hash21(ip + g + seed * 3.0) < 0.55) continue;
        vec2 o = g + (h - 0.5) * 0.8 + 0.12 * vec2(sin(uTime * 0.7 + h.x * 20.0), cos(uTime * 0.5 + h.y * 20.0)) - fp;
        float d = length(o);
        float tw = 0.55 + 0.45 * sin(uTime * (0.8 + 2.0 * h.y) + h.x * 30.0);
        acc += exp(-d * d / (size * size)) * tw;
    }
    return acc;
}

void main(){
    vec2 sp = (vUV - 0.5) * vec2(uRes.x / uRes.y, 1.0);
    vec3 c = uBg * (1.0 - 0.6 * length(sp));
    // light shaft
    float bx = uBeamX + uBeamTilt * (0.5 - sp.y);
    float w = 0.10 + 0.22 * (0.5 - sp.y);
    float shaft = exp(-pow((sp.x - bx) / w, 2.0)) * smoothstep(-0.6, 0.5, sp.y);
    float vol = 0.6 + 0.4 * fbm(vec2(sp.x * 3.0 - uTime * 0.05, sp.y * 1.5 + uTime * 0.03));
    c += uBeamCol * shaft * vol * uBeam * 0.35;
    // glow
    c += uGlowCol * exp(-dot(sp, sp) / max(uGlowR * uGlowR, 1e-4)) * step(0.0001, uGlowR);
    // dust: three depth layers, brighter inside the shaft
    float lit = 0.15 + 2.5 * shaft * uBeam + 0.6 * exp(-dot(sp, sp) / max(uGlowR * uGlowR * 4.0, 1e-4)) * step(0.0001, uGlowR);
    float m = motes(sp, 9.0, 0.03, 1.0, 0.035) * 0.7 + motes(sp, 5.0, 0.05, 7.0, 0.05) * 0.5 + motes(sp, 2.2, 0.08, 3.0, 0.09) * 0.25;
    c += vec3(1.0, 0.92, 0.8) * m * lit * uDust * 0.8;
    fragColor = vec4(c, 1.0);
}
