#version 330
//#include common
in vec2 vUV;
out vec4 fragColor;
uniform vec2  uCamPos;
uniform float uCamH;
uniform sampler2D uTree;    // tree silhouette (alpha)
uniform float uVoice;
uniform float uPane;        // glowing memory pane on the chair
uniform float uMist;
uniform float uMoon;
uniform float uFireflies;
uniform vec3  uTint;

float PX;
float chairSDF(vec2 p){
    // three-quarter view wooden chair, seat at y = 0 (back legs sit higher = further away)
    float seat = max(sdBox(p - vec2(0.0, 0.0), vec2(0.070, 0.007)), -0.0);
    float seatTop = sdBox(p - vec2(0.012, 0.009), vec2(0.060, 0.004));
    float legFL = sdBox(p - vec2(-0.058, -0.052), vec2(0.005, 0.052));
    float legFR = sdBox(p - vec2(0.060, -0.052), vec2(0.005, 0.052));
    float legBL = sdBox(p - vec2(-0.030, -0.040), vec2(0.0038, 0.040));
    float legBR = sdBox(p - vec2(0.078, -0.040), vec2(0.0038, 0.040));
    float postL = sdBox(p - vec2(-0.030, 0.070), vec2(0.0045, 0.070));
    float postR = sdBox(p - vec2(0.078, 0.070), vec2(0.0045, 0.070));
    float rail1 = sdBox(p - vec2(0.024, 0.132), vec2(0.056, 0.008));
    float rail2 = sdBox(p - vec2(0.024, 0.090), vec2(0.054, 0.004));
    float slat = sdBox(vec2(abs(p.x - 0.024) - 0.018, p.y - 0.110), vec2(0.0035, 0.022));
    float stretch = sdBox(p - vec2(0.0, -0.07), vec2(0.058, 0.0025));
    float d = min(min(min(seat, legFL), min(legFR, legBL)), min(min(legBR, postL), min(postR, rail1)));
    d = min(d, min(min(rail2, slat), min(stretch, seatTop)));
    return d;
}

vec3 sky(vec2 p){
    vec3 top = vec3(0.004, 0.007, 0.016), hor = vec3(0.035, 0.045, 0.065);
    vec3 c = mix(hor, top, smoothstep(-0.1, 0.6, p.y));
    vec2 mp = p - vec2(-0.50, 0.24);
    float md = length(mp);
    c += vec3(0.55, 0.62, 0.75) * (exp(-md * 7.0) * 0.5 + exp(-md * 2.2) * 0.12) * uMoon;
    c += vec3(1.2, 1.25, 1.3) * smoothstep(0.034, 0.03, md) * uMoon * 2.0;
    return c;
}

void main(){
    PX = uCamH / uRes.y;
    vec2 sp = (vUV - 0.5) * vec2(uRes.x / uRes.y, 1.0);
    vec2 p = sp * uCamH + uCamPos;
    vec3 c = sky(p);
    vec3 fog = vec3(0.055, 0.07, 0.095);
    // far tree line
    vec2 pf = p + uCamPos * (0.3 - 1.0);
    float tl = -0.02 + 0.07 * fbm(vec2(pf.x * 3.0, 1.0)) + 0.05 * pow(fbm(vec2(pf.x * 9.0, 4.0)), 2.0);
    if(pf.y < tl) c = mix(vec3(0.02, 0.03, 0.045), fog, 0.55);
    // ground
    float ground = -0.24 + 0.01 * fbm(vec2(p.x * 4.0, 0.0));
    if(p.y < ground){
        float g = fbm(p * vec2(40.0, 90.0));
        c = vec3(0.012, 0.022, 0.02) * (0.6 + 0.7 * g);
        c += vec3(0.2, 0.25, 0.3) * 0.05 * uMoon;
    }
    // big old tree (texture) on the right
    vec2 tuv = (p - vec2(-0.42, -0.30)) / vec2(1.3, 0.95);
    if(tuv.x > 0.0 && tuv.x < 1.0 && tuv.y > 0.0 && tuv.y < 1.0){
        float a = texture(uTree, vec2(tuv.x, 1.0 - tuv.y)).a;
        vec3 tc = vec3(0.006, 0.009, 0.012);
        c = mix(c, tc, a);
    }
    // chair
    vec2 cp = p - vec2(-0.10, -0.172);
    float d = chairSDF(cp);
    float m = 1.0 - smoothstep(-PX, PX, d);
    vec3 chairCol = vec3(0.012, 0.010, 0.010);
    vec2 moonDir = normalize(vec2(-0.50, 0.24) - p);
    float rim = step(0.0, chairSDF(cp + moonDir * 0.0025)) * m;
    chairCol += vec3(0.35, 0.42, 0.55) * rim * 0.25 * uMoon;
    // the last piece of memory glass resting on the seat
    vec2 gp = cp - vec2(0.022, 0.040);
    gp = rot(0.10) * gp;
    float pane = sdBox(gp, vec2(0.022, 0.028));
    float paneArc = length(gp - vec2(0.0, 0.028)) - 0.022;
    float pd = min(pane, max(paneArc, -(gp.y - 0.028)));
    float pm = (1.0 - smoothstep(-PX, PX, pd)) * uPane;
    float pulse = 0.75 + 0.6 * uVoice;
    vec3 vo = voronoi(gp * 110.0, 0.9);
    vec3 glassC = jewel(floor(vo.z * 8.0)) * 0.5 + vec3(0.55, 0.5, 0.45);
    glassC *= (1.0 - 0.8 * (1.0 - smoothstep(0.0, 0.07, vo.y)));
    c = mix(c, chairCol, m);
    c = mix(c, glassC * 2.2 * pulse, pm);
    c += vec3(1.0, 0.85, 0.6) * exp(-length(gp) / 0.07) * 0.35 * pulse * uPane;
    c += vec3(1.0, 0.8, 0.55) * exp(-length(gp) / 0.25) * 0.08 * pulse * uPane;
    // mist layers drifting across
    float mist = 0.0;
    for(int k = 0; k < 3; k++){
        float fk = float(k);
        vec2 mp = p * vec2(1.2 + fk * 0.6, 4.0 + fk * 2.0) + vec2(uTime * (0.03 + 0.02 * fk), fk * 3.1);
        float band = exp(-pow((p.y - (-0.20 + fk * 0.06)) / (0.10 + 0.05 * fk), 2.0));
        mist += fbm(mp) * band;
    }
    c = mix(c, fog * (1.0 + uMoon * 0.4), clamp(mist * 0.55 * uMist, 0.0, 0.85));
    // fireflies / memory motes
    if(uFireflies > 0.0){
        vec2 q = p * 7.0 + vec2(uTime * 0.05, sin(uTime * 0.2) * 0.3);
        vec2 ip = floor(q);
        vec2 h = hash22(ip);
        vec2 o = fract(q) - 0.5 - (h - 0.5) * 0.7 - 0.15 * vec2(sin(uTime * 0.9 + h.x * 20.0), cos(uTime * 0.7 + h.y * 30.0));
        float f = exp(-dot(o, o) / 0.0012) * step(0.7, hash21(ip + 4.0)) * (0.5 + 0.5 * sin(uTime * 2.0 + h.x * 40.0));
        c += vec3(1.0, 0.85, 0.5) * f * uFireflies * smoothstep(0.2, -0.2, p.y);
    }
    c *= uTint;
    fragColor = vec4(c, 1.0);
}
