#version 330
//#include common
//#include rose
in vec2 vUV;
out vec4 fragColor;

uniform vec2  uCamPos;     // world position of screen centre
uniform float uCamH;       // world units spanned by screen height
uniform float uCamRot;
uniform float uShape;      // lead/tracery reveal (0..1)
uniform float uColor;      // colour fill (0..1)
uniform float uBleed;      // the Bleeding (0..1)
uniform float uLight;      // backlight intensity
uniform vec2  uLightPos;   // sun behind the glass (window space)
uniform float uVoice;      // voice envelope 0..1 (memory glass "speaks")
uniform float uHole;       // 1 = glass gone, show the light behind
uniform float uTexMode;    // 1 = render the glass disc only (for shard texture)
uniform float uWall;       // wall visibility
uniform float uSat;        // saturation of the glass
uniform float uDim;        // darken everything but the glass (night)
uniform float uMotes;      // floating memory motes
uniform float uRain;       // rain running down the glass
uniform float uHoleBright;

vec3 glassAt(vec2 p, out float alpha){
    RoseHit h = rose(p);
    float r = length(p);
    float px = uPxWorld;

    // reveal wavefront for the tracery
    float ang = atan(p.x, p.y);
    float rho = r * 0.92 + 0.035 * sin(ang * 6.0) + 0.03;
    float drawn = smoothstep(rho - 0.01, rho + 0.01, uShape * 1.12);
    float tip = exp(-pow((rho - uShape * 1.12) / 0.018, 2.0)) * step(0.001, uShape) * (1.0 - step(1.0, uShape));

    // colour arrival
    float fill = smoothstep(h.order, h.order + 0.07, uColor * 1.08);
    float pop  = exp(-pow((uColor * 1.08 - h.order - 0.02) / 0.03, 2.0)) * step(0.001, uColor) * (1.0 - step(0.999, uColor));

    // base glass colour
    vec3 col = roseColor(h.key, h.piece);
    // the Bleeding: colours cross the cames
    if(uBleed > 0.0){
        vec2 w = vec2(fbm(p * 3.5 + vec2(uTime * 0.07, 1.3)), fbm(p * 3.5 + vec2(5.2, -uTime * 0.06))) - 0.5;
        RoseHit hb = rose(p + w * 0.22 * uBleed);
        vec3 cb = roseColor(hb.key, hb.piece);
        float m = smoothstep(0.35, 0.75, fbm(p * 2.0 - uTime * 0.05) + uBleed * 0.35);
        col = mix(col, cb, m * uBleed);
        float stain = smoothstep(0.45, 0.8, fbm(p * 1.7 + vec2(0.0, -uTime * 0.04)) + 0.25 * uBleed);
        col = mix(col, vec3(0.55, 0.01, 0.03) * (0.5 + 0.7 * h.piece), stain * uBleed * 0.8);
        col *= 1.0 - 0.35 * uBleed;
    }
    float sat = uSat;
    vec3 clearGlass = vec3(0.78, 0.80, 0.84) * (0.75 + 0.35 * h.piece);
    col = mix(vec3(luma(col)) * 1.2, col, sat);
    col = mix(clearGlass * 0.55, col, fill);

    // glass body texture: streaks, seeds, thickness
    float ca = hash11(h.piece * 17.0) * PI;
    vec2 sp = rot(ca) * p;
    float streak = fbm(sp * vec2(3.0, 38.0) + h.piece * 10.0);
    float thick = fbm(p * 9.0 + h.piece * 4.0);
    float body = 0.45 + 0.75 * thick + 0.35 * (streak - 0.5);
    // painted grisaille: faint dark smudges that give the glass its age
    body *= 0.8 + 0.2 * smoothstep(0.35, 0.65, fbm(p * 22.0 + h.piece * 3.0));
    float seed = smoothstep(0.985, 1.0, vnoise(p * 140.0 + h.piece * 30.0)) * 0.8;

    // backlight: bright sun blob + moving cloud modulation
    vec2 dl = p - uLightPos;
    float sun = exp(-dot(dl, dl) / 0.22);
    float halo = exp(-dot(dl, dl) / 1.6);
    float clouds = 0.7 + 0.45 * fbm(p * 1.3 + vec2(uTime * 0.03, 0.0));
    float back = (0.28 + 0.8 * halo + 2.6 * sun) * clouds;

    float lum = uLight * back * body * (1.0 + 0.55 * uVoice);
    vec3 glass = col * lum * 1.35 + seed * lum * vec3(1.0, 0.95, 0.85);
    // edges of each piece slightly darker (thicker glass near the cames)
    glass *= mix(0.35, 1.0, smoothstep(0.0, 0.03, min(h.dLead, h.dStone)));
    glass += pop * vec3(1.4, 1.2, 0.9) * 1.6;

    // lead cames
    float lw = 0.0034;
    float lead = 1.0 - smoothstep(lw - px, lw + px, h.dLead);
    // stone tracery
    float sw = 0.0115;
    float stone = 1.0 - smoothstep(sw - px, sw + px, h.dStone);
    if(h.zone > 5.5) stone = 1.0;

    vec3 leadCol = vec3(0.010, 0.009, 0.008) + vec3(0.03, 0.025, 0.02) * pow(max(0.0, 1.0 - h.dLead / lw), 3.0);
    float st = fbm(p * 30.0);
    float bevel = pow(max(0.0, 1.0 - h.dStone / sw), 1.5);
    vec3 stoneCol = vec3(0.045, 0.038, 0.034) * (0.6 + 0.7 * st) * (0.4 + 0.6 * uLight);
    stoneCol += vec3(0.05, 0.04, 0.03) * bevel * uLight;

    // before the tracery is drawn: nothing but darkness
    glass *= drawn;
    vec3 c = glass;
    c = mix(c, leadCol * drawn, lead);
    c = mix(c, stoneCol * mix(0.0, 1.0, drawn), stone);
    // the drawing tip: molten gold running through the tracery
    c += tip * max(lead, stone) * vec3(3.2, 2.0, 0.8) * 1.4;
    c += tip * vec3(0.6, 0.35, 0.1) * 0.25;

    // bleeding veins
    if(uBleed > 0.0){
        float v = 1.0 - abs(2.0 * fbm(p * 5.0 + vec2(0.0, uTime * 0.08)) - 1.0);
        float grow = smoothstep(0.0, 1.0, uBleed * 1.6 - r * 0.8);
        float veins = pow(v, 14.0) * grow;
        float flick = 0.8 + 0.4 * sin(uTime * 23.0 + r * 40.0) * sin(uTime * 7.0);
        c += veins * vec3(3.0, 0.06, 0.08) * flick * (1.0 - stone * 0.5);
    }

    alpha = step(r, 1.0);
    return c;
}

vec3 wallAt(vec2 p){
    float r = length(p);
    // outer stone archivolt with cusps
    float ang = atan(p.x, p.y);
    float cusp = 0.012 * pow(abs(cos(ang * 24.0)), 0.5);
    float frame = step(1.0, r) * (1.0 - step(1.13 + cusp, r));
    // ashlar blocks
    vec2 bp = p / vec2(0.42, 0.21);
    float row = floor(bp.y);
    bp.x += mod(row, 2.0) * 0.5;
    vec2 bf = fract(bp);
    float mortar = smoothstep(0.0, 0.03, bf.x) * smoothstep(1.0, 0.97, bf.x) * smoothstep(0.0, 0.05, bf.y) * smoothstep(1.0, 0.95, bf.y);
    float bid = hash21(floor(bp));
    float tex = fbm(p * 12.0) * 0.6 + 0.4 * fbm(p * 40.0);
    vec3 stone = vec3(0.105, 0.09, 0.08) * (0.55 + 0.45 * bid) * (0.6 + 0.5 * tex) * (0.35 + 0.65 * mortar);
    // radial frame mouldings
    float ring = 0.5 + 0.5 * cos((r - 1.0) * 140.0);
    vec3 frameCol = vec3(0.10, 0.09, 0.08) * (0.7 + 0.3 * ring) * (0.6 + 0.5 * tex);
    vec3 w = mix(stone, frameCol, frame);
    // spill light from the window (tinted by the glass)
    float spill = uLight * 0.9 / (1.0 + 5.0 * pow(max(r - 1.0, 0.0), 1.5) * 6.0);
    vec3 tint = mix(vec3(0.75, 0.68, 0.8), vec3(0.9, 0.3, 0.3), uBleed);
    w *= 0.25 + spill * tint * 1.8;
    return w * uWall;
}

vec3 behindLight(vec2 p){
    // through the empty frame: a night sky, flooded with light at the moment of breaking
    float sun = exp(-dot(p - uLightPos, p - uLightPos) / 0.25);
    vec3 night = mix(vec3(0.010, 0.014, 0.035), vec3(0.03, 0.04, 0.08), 0.5 - 0.5 * p.y);
    vec2 sp = p * 40.0; vec2 ip = floor(sp);
    float st = step(0.965, hash21(ip)) * smoothstep(0.3, 0.0, length(fract(sp) - 0.5 - (hash22(ip) - 0.5) * 0.5));
    night += vec3(0.8, 0.85, 1.0) * st * 0.6;
    vec3 flash = vec3(1.0, 0.95, 0.85) * 1.2 + sun * vec3(4.0, 3.4, 2.6);
    return mix(night, flash, clamp(uHoleBright, 0.0, 1.0)) * max(uHoleBright, 1.0);
}

void main(){
    vec2 uv = vUV;
    if(uTexMode > 0.5){
        vec2 p = (uv * 2.0 - 1.0) * 1.0;
        float a;
        vec3 g = glassAt(p, a);
        fragColor = vec4(g, a);
        return;
    }
    vec2 sp = (uv - 0.5) * vec2(uRes.x / uRes.y, 1.0);
    vec2 p = rot(uCamRot) * sp * uCamH + uCamPos;
    float r = length(p);
    vec3 c;
    if(r < 1.0){
        if(uHole > 0.5) c = behindLight(p);
        else { float a; c = glassAt(p, a); }
    } else {
        c = wallAt(p);
    }
    // floating memory motes drifting up in front of the glass
    if(uMotes > 0.0){
        vec2 mp = sp * 6.0 + vec2(0.0, -uTime * 0.25);
        vec2 ip = floor(mp);
        vec2 fp = fract(mp) - 0.5;
        vec2 o = hash22(ip) - 0.5;
        float tw = 0.5 + 0.5 * sin(uTime * (1.0 + 2.0 * hash21(ip + 3.0)) + hash21(ip) * TAU);
        float d = length(fp - o * 0.7);
        float m = exp(-d * d / 0.0009) * step(0.55, hash21(ip + 7.0)) * tw;
        vec3 mc = jewel(floor(hash21(ip + 11.0) * 8.0)) * 0.6 + 0.4;
        c += m * mc * 1.8 * uMotes;
    }
    // rain running down the glass (screen space)
    if(uRain > 0.0){
        float cols = 70.0;
        float cx = floor(sp.x * cols);
        float hx = hash11(cx * 1.37);
        float fx = fract(sp.x * cols) - 0.5;
        float spd = 0.25 + 0.35 * hx;
        float y = fract(sp.y * 0.8 + uTime * spd + hx * 7.0);
        float head = exp(-pow((y - 0.05) / 0.012, 2.0)) * exp(-fx * fx / 0.02);
        float trail = smoothstep(0.05, 0.6, y) * (1.0 - smoothstep(0.6, 1.0, y)) * exp(-fx * fx / 0.004) * 0.35;
        float on = step(0.45, hash11(cx * 3.1 + floor(uTime * spd + hx * 7.0 + sp.y * 0.8)));
        float beads = step(0.97, vnoise(sp * 160.0 + vec2(0.0, uTime * 0.2))) * 0.5;
        c *= 1.0 + (head * 2.5 + trail + beads) * on * uRain * 0.8;
        c += vec3(0.6, 0.7, 0.8) * (head * 0.25) * on * uRain;
    }
    c *= mix(1.0, 0.25, uDim * step(1.0, r));
    fragColor = vec4(c, 1.0);
}
