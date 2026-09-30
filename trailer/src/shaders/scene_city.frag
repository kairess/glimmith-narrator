#version 330
//#include common
in vec2 vUV;
out vec4 fragColor;

#define NB 200
#define NF 24
#define NL 40

uniform vec2  uCamPos;
uniform float uCamH;
uniform vec4  uB[NB];     // x, halfwidth, height, type(0 flat,1 gable,2 spire,3 dome,4 castle tower)
uniform vec4  uB2[NB];    // base y, layer(0 front,1 back,2 castle,3 far), seed, window density
uniform int   uNB;
uniform vec4  uF[NF];     // feature windows: x, y, radius, seed
uniform int   uNF;
uniform vec4  uL[NL];     // links: ax, ay, bx, by
uniform int   uNL;

uniform vec3  uSkyTop, uSkyMid, uSkyHor;
uniform vec2  uSunPos;
uniform vec3  uSunCol;
uniform float uStars;
uniform float uLamps;      // 0..1 lamps turning on
uniform float uFeat;       // feature window glow
uniform float uLinks;      // 0..1 link reveal
uniform float uBleed;      // 0..1 links turn crimson
uniform float uShatter;    // seconds since the shattering wave began (<0 = not yet)
uniform float uShatterX;
uniform float uBroken;     // 1 = the city after the shattering (feature windows dark)
uniform float uShips;      // seconds of airship departure (<0 = none)
uniform float uGhost;      // city made of memory glass
uniform float uBench;      // Mara's bench visible
uniform float uFore;       // foreground overlook visible
uniform vec2  uFgOff;      // foreground offset (screen-anchored layer)
uniform float uFog;
uniform float uHaze;
uniform float uVoice;
uniform float uCloud;
uniform float uSmoke;
uniform float uArchive;    // one lamp still burning in the archive after everyone left
uniform vec2  uArchivePos;
uniform float uAsh;        // ash drifting down after the shattering

const float WATER = -0.30;
float PX;

vec3 skyColor(vec2 p){
    float y = p.y;
    vec3 c = mix(uSkyHor, uSkyMid, smoothstep(-0.08, 0.30, y));
    c = mix(c, uSkyTop, smoothstep(0.25, 1.1, y));
    vec2 d = p - uSunPos;
    float sd = length(d * vec2(0.55, 1.0));
    c += uSunCol * (exp(-sd * 2.5) * 0.55 + exp(-sd * 14.0) * 1.2 + exp(-sd * 60.0) * 3.0);
    // clouds: long streaks lit from the sun side
    float cl = fbm(vec2(p.x * 0.7 + uTime * 0.008, p.y * 3.2) + 3.0);
    float band = smoothstep(0.02, 0.5, y) * (1.0 - smoothstep(0.9, 1.5, y));
    float cm = smoothstep(0.5, 0.78, cl) * band * uCloud;
    vec3 lit = uSunCol * 0.9 + uSkyHor * 0.3;
    vec3 cc = mix(uSkyTop * 0.5 + uSkyMid * 0.2, lit, exp(-sd * 1.2) * 0.9);
    float edge = smoothstep(0.5, 0.62, cl) - smoothstep(0.62, 0.78, cl);
    c = mix(c, cc, cm * 0.85);
    c += lit * edge * band * uCloud * exp(-sd * 1.5) * 0.35;
    if(uStars > 0.0){
        vec2 sp = p * 90.0;
        vec2 ip = floor(sp);
        float h = hash21(ip);
        vec2 o = hash22(ip) - 0.5;
        float d2 = length(fract(sp) - 0.5 - o * 0.6);
        float tw = 0.6 + 0.4 * sin(uTime * (2.0 + h * 3.0) + h * 40.0);
        float s = smoothstep(0.07, 0.0, d2) * step(0.94, h) * tw * (0.4 + 0.6 * hash21(ip + 9.0));
        c += vec3(0.9, 0.95, 1.1) * s * uStars * smoothstep(0.0, 0.5, y) * (1.0 - cm);
    }
    return c;
}

float mountains(float x){
    return 0.0 + 0.20 * fbm(vec2(x * 0.55, 1.7)) + 0.09 * fbm(vec2(x * 2.2, 5.1));
}

float bldSDF(vec2 p, vec4 b, vec4 b2){
    float x = b.x, hw = b.y, h = b.z; int t = int(b.w + 0.5);
    float base = b2.x;
    vec2 q = p - vec2(x, base);
    float d = sdBox(q - vec2(0.0, h * 0.5), vec2(hw, h * 0.5));
    vec2 r = q - vec2(0.0, h);
    if(t == 1){ // steep gable + chimney
        float slope = 1.35;
        float tri = max((abs(r.x) * slope + r.y - hw * slope * 1.02) / 1.6, -r.y);
        d = min(d, tri);
        float ch = sdBox(r - vec2(hw * 0.45, hw * 0.6), vec2(0.006, hw * 0.45));
        d = min(d, ch);
    } else if(t == 2){ // church spire
        float sh = h * 1.05 + 0.12;
        float k = sh / (hw * 0.7);
        float cone = max((abs(r.x) * k + r.y - sh) / k, -r.y);
        d = min(d, cone);
        d = min(d, sdBox(r - vec2(0.0, sh + 0.02), vec2(0.0012, 0.03)));
        d = min(d, sdBox(r - vec2(0.0, sh + 0.03), vec2(0.008, 0.0012)));
        vec2 rp = vec2(abs(r.x) - hw * 0.95, r.y);
        d = min(d, max((abs(rp.x) * 6.0 + rp.y - 0.05) / 6.0, -rp.y));
    } else if(t == 3){ // onion dome
        vec2 rr = r - vec2(0.0, hw * 0.25);
        float dome = length(rr * vec2(1.0, 0.9)) - hw * 0.8;
        float tip = max((abs(r.x) * 3.0 + (r.y - hw * 0.9) - hw * 0.9) / 3.0, -(r.y - hw * 0.8));
        d = min(d, max(min(dome, tip), -r.y));
        d = min(d, sdBox(r - vec2(0.0, hw * 1.9), vec2(0.0012, 0.02)));
    } else if(t == 4){ // castle tower with tall conical roof
        float sh = hw * 3.8;
        float k = sh / (hw * 1.3);
        float cone = max((abs(r.x) * k + r.y - sh) / k, -r.y);
        d = min(d, cone);
        d = min(d, sdBox(r - vec2(0.0, sh + 0.025), vec2(0.0012, 0.03)));
        d = min(d, sdBox(r - vec2(0.004, sh + 0.045), vec2(0.008, 0.005)));
    } else { // flat with crenellations
        float cr = sdBox(vec2(mod(r.x + 0.011, 0.022) - 0.011, r.y - 0.007), vec2(0.0055, 0.007));
        d = min(d, max(cr, abs(r.x) - hw));
    }
    return d;
}

float featBreakT(int i){
    vec4 f = uF[i];
    return abs(f.x - uShatterX) * 0.45 + hash11(f.w * 13.0) * 0.35;
}

vec3 featureGlass(vec2 p, vec4 f){
    vec2 q = (p - f.xy) / f.z;
    float r = length(q);
    float a = atan(q.x, q.y);
    float s = floor(a / (TAU / 8.0));
    float ring = step(0.5, r);
    vec3 c = jewel(s * 3.0 + ring * 5.0 + floor(f.w * 7.0));
    float sp = abs(fract(a / (TAU / 8.0)) - 0.5) * 2.0;
    float lead = (1.0 - smoothstep(0.0, 0.12 / max(r, 0.2), sp)) * step(0.18, r);
    lead = max(lead, 1.0 - smoothstep(0.03, 0.08, abs(r - 0.5)));
    lead = max(lead, smoothstep(0.86, 0.92, r));
    vec3 g = c * (1.8 + 1.0 * uVoice) * (1.0 - 0.9 * lead);
    g += vec3(1.0, 0.85, 0.6) * 0.5 * exp(-r * 3.0);
    return g;
}

vec3 city(vec2 pw){
    vec3 col = skyColor(pw);
    vec3 fogCol = mix(uSkyHor, uSkyMid, 0.4);
    // ------- far mountains
    vec2 pm = pw + uCamPos * (0.25 - 1.0);
    float mh = mountains(pm.x) - 0.06;
    if(pm.y < mh){
        vec3 mc = mix(uSkyHor * 0.6, uSkyMid * 0.45, 0.5);
        col = mix(mc, fogCol, 0.5 * uHaze + 0.2) * 0.9;
        col += uSunCol * 0.08 * smoothstep(-0.02, 0.0, pm.y - mh + 0.004);
    }
    // ------- castle hill
    float hill = -0.13 + 0.24 * exp(-pow((pw.x - 1.25) / 0.75, 2.0)) + 0.012 * fbm(vec2(pw.x * 6.0, 0.0));
    // ------- buildings
    int best = -1; float bestLayer = 9.0; float bestD = 1.0;
    for(int i = 0; i < NB; i++){
        if(i >= uNB) break;
        vec4 b = uB[i];
        if(abs(pw.x - b.x) > b.y * 1.7 + 0.01) continue;
        vec4 b2 = uB2[i];
        float layer = b2.y;
        if(layer >= bestLayer) continue;
        float d = bldSDF(pw, b, b2);
        if(d < 0.0){ bestLayer = layer; best = i; bestD = d; }
    }
    bool onHill = pw.y < hill && bestLayer > 2.5;
    if(best >= 0 || onHill){
        float layer = best >= 0 ? bestLayer : 2.2;
        float haze = (layer > 2.5 ? 0.42 : (layer > 1.5 ? 0.22 : (layer > 0.5 ? 0.10 : 0.03))) * uHaze;
        vec3 sil = vec3(0.006, 0.007, 0.012);
        vec3 c = mix(sil, fogCol * 0.55, haze);
        float base = -0.17;
        if(best >= 0){
            vec4 b = uB[best], b2 = uB2[best];
            base = b2.x;
            vec2 q = pw - vec2(b.x, b2.x);
            vec2 sd = normalize(uSunPos - pw) * 0.0035;
            float dR = bldSDF(pw + sd, b, b2);
            float rim = smoothstep(-0.0005, 0.001, dR);
            c += uSunCol * 0.35 * rim * (1.0 - haze);
            vec2 cell = vec2(0.021, 0.034);
            vec2 g = (q - vec2(-b.y + 0.01, 0.016)) / cell;
            vec2 gi = floor(g); vec2 gf = fract(g) - 0.5;
            float inBody = step(0.0, q.y - 0.012) * step(q.y, b.z - 0.018) * step(abs(q.x), b.y - 0.008);
            float wrect = step(abs(gf.x), 0.16) * step(abs(gf.y), 0.24);
            float wid = hash21(gi + b2.z * 17.0);
            float lit = step(wid, b2.w) * step(wid * 0.85 + 0.08, uLamps);
            float jew = step(0.82, hash21(gi * 1.7 + b2.z));
            vec3 wc = jew > 0.5 ? jewel(floor(hash21(gi + 5.0) * 8.0)) * 1.6 : vec3(1.0, 0.56, 0.22) * 1.8;
            float flick = 0.85 + 0.15 * sin(uTime * (1.0 + 3.0 * wid) + wid * 50.0);
            float off = 1.0;
            if(uShatter >= 0.0){
                float tb = abs(b.x - uShatterX) * 0.45 + wid * 0.6;
                off = 1.0 - smoothstep(tb, tb + 0.12, uShatter);
                float burst = exp(-max(uShatter - tb, 0.0) * 7.0) * step(tb, uShatter);
                wc += (wc * 4.0 + vec3(2.0)) * burst;
            }
            off *= 1.0 - uBroken;
            float wlight = wrect * inBody * lit * flick * off * (1.0 - haze * 0.7);
            c += wc * wlight;
            if(uGhost > 0.0){
                vec3 vo = voronoi(pw * 34.0, 0.9);
                vec3 gc = jewel(floor(vo.z * 8.0)) * (0.06 + 0.16 * vo.z * vo.z);
                float cames = 1.0 - smoothstep(0.0, 0.06, vo.y);
                float outline = exp(-abs(bestD) / 0.0018);
                float shimmer = 0.4 + 0.6 * pow(0.5 + 0.5 * sin(uTime * 1.3 + vo.z * 40.0), 3.0);
                float sweep = exp(-pow((pw.x - (-2.5 + mod(uTime * 0.5, 6.0))) / 0.35, 2.0));
                vec3 ghost = gc * shimmer * (1.0 - cames) * (1.0 + 3.0 * sweep) + vec3(0.75, 0.82, 1.0) * (outline * 0.8 + cames * 0.02);
                ghost *= smoothstep(-0.08, 0.3, q.y) * 0.8 + 0.2;
                c = mix(c, ghost, uGhost);
            }
        }
        float hf = exp(-max(pw.y - base, 0.0) / 0.06) * 0.32 * uFog;
        c = mix(c, fogCol * 0.5, hf);
        col = c;
    }
    // ------- smoke after the shattering
    if(uSmoke > 0.0){
        float sm = 0.0;
        for(int k = 0; k < 5; k++){
            float x0 = -2.4 + float(k) * 1.1 + 0.3 * hash11(float(k));
            float w = 0.06 + (pw.y + 0.1) * 0.25;
            float n = fbm(vec2((pw.x - x0) * 4.0 - uTime * 0.1, pw.y * 3.0 - uTime * 0.25));
            sm += smoothstep(w, 0.0, abs(pw.x - x0 + (n - 0.5) * 0.3 * (pw.y + 0.2))) * smoothstep(-0.15, 0.1, pw.y) * n;
        }
        col = mix(col, fogCol * 0.35, clamp(sm, 0.0, 0.8) * uSmoke);
    }
    // ------- feature windows (memory glass)
    for(int i = 0; i < NF; i++){
        if(i >= uNF) break;
        vec4 f = uF[i];
        float d = length(pw - f.xy);
        float intact = 1.0 - uBroken; float flash = 0.0;
        if(uShatter >= 0.0){
            float tb = featBreakT(i);
            intact *= 1.0 - step(tb, uShatter);
            flash = exp(-max(uShatter - tb, 0.0) * 6.0) * step(tb, uShatter);
        }
        if(d < f.z){
            vec3 g = featureGlass(pw, f);
            vec2 q = (pw - f.xy) / f.z;
            float ang = atan(q.x, q.y);
            float rimFrag = step(0.55, vnoise(vec2(ang * 3.0, f.w * 10.0))) * smoothstep(0.62, 0.8, length(q) + 0.15 * vnoise(vec2(ang * 9.0, 1.0)));
            vec3 broken = mix(vec3(0.004, 0.004, 0.006), jewel(floor(ang * 2.0 + f.w * 8.0)) * 0.25, rimFrag);
            col = mix(col, intact > 0.5 ? g : broken, uFeat);
        }
        col += jewel(floor(f.w * 7.0)) * 0.35 * exp(-d / (f.z * 1.2)) * uFeat * intact * (1.0 + uVoice);
        col += vec3(1.0, 0.92, 0.8) * flash * (exp(-d / 0.03) * 6.0 + exp(-d / 0.12) * 1.0 + exp(-d / 0.5) * 0.06);
        if(uShatter >= 0.0){
            float tb = featBreakT(i);
            float tt = uShatter - tb;
            if(tt > 0.0 && tt < 3.0){
                for(int k = 0; k < 26; k++){
                    vec3 hr = hash31(f.w * 31.0 + float(k) * 7.0);
                    float ang = hr.x * TAU;
                    float sp = 0.12 + 0.45 * hr.y;
                    vec2 v = vec2(cos(ang), sin(ang) * 0.7 + 0.35) * sp;
                    vec2 pos = f.xy + v * tt + vec2(0.0, -0.30) * tt * tt;
                    vec2 vel = v + vec2(0.0, -0.60) * tt;
                    vec2 dp = pw - pos;
                    vec2 vn = normalize(vel);
                    float along = dot(dp, vn);
                    float perp = length(dp - vn * along);
                    float streak = exp(-perp * perp / (PX * PX * 1.5)) * exp(-max(-along, 0.0) / (0.015 * length(vel) + 0.002)) * step(along, PX);
                    float life = exp(-tt * (0.9 + hr.z));
                    col += mix(vec3(1.0, 0.85, 0.6), jewel(floor(hr.z * 8.0)), 0.6) * streak * 8.0 * life;
                }
            }
        }
    }
    // ------- links between windows
    if(uLinks > 0.0){
        vec3 gold = vec3(1.0, 0.70, 0.30);
        vec3 crim = vec3(1.0, 0.03, 0.06);
        for(int i = 0; i < NL; i++){
            if(i >= uNL) break;
            vec4 L = uL[i];
            vec2 a = L.xy, b = L.zw;
            vec2 ab = b - a; float len = length(ab);
            float t = clamp(dot(pw - a, ab) / dot(ab, ab), 0.0, 1.0);
            vec2 n = normalize(vec2(-ab.y, ab.x)); if(n.y < 0.0) n = -n;
            float arcH = 0.04 + 0.12 * len;
            vec2 cp = a + ab * t + n * arcH * 4.0 * t * (1.0 - t);
            float d = length(pw - cp);
            if(d > 0.08) continue;
            float hi = hash11(float(i) * 3.7);
            float reveal = clamp(uLinks * 2.2 - hi * 1.2, 0.0, 1.0);
            float vis = step(t, reveal);
            float alive = 1.0;
            if(uShatter >= 0.0){
                float tb = min(abs(a.x - uShatterX), abs(b.x - uShatterX)) * 0.45 + 0.1;
                alive = 1.0 - smoothstep(tb, tb + 0.1, uShatter);
            }
            float bl = smoothstep(hi * 0.5, hi * 0.5 + 0.4, uBleed);
            vec3 lc = mix(gold, crim, bl);
            float flick = 1.0 + bl * 0.7 * sin(uTime * 31.0 + hi * 90.0) * sin(uTime * 7.0 + hi);
            float w = PX * (0.8 + 0.8 * hi) * (1.0 + bl);
            float core = exp(-d * d / (w * w));
            float halo = exp(-d / (0.008 + 0.01 * bl)) * 0.22;
            float speed = 0.22 + 0.9 * bl;
            float s = fract(uTime * speed * (0.6 + hi) + hi);
            float pulse = exp(-pow((t - s) * len / (0.02 + 0.03 * bl), 2.0)) * (1.0 + 2.5 * bl);
            col += lc * (core * 1.1 + halo + pulse * core * 6.0 + pulse * halo * 3.0) * vis * alive * flick * 1.3;
        }
    }
    return col;
}

// ---------------- airships (bow toward +x)
float airship(vec2 p, float s){
    p /= s;
    vec2 e = p; e.x *= e.x < 0.0 ? 0.86 : 1.0;
    float env = length(e * vec2(1.0, 4.6)) - 0.2;
    float finSpan = 0.028 + max(-0.17 - p.x, 0.0) * 0.55;
    float fin = max(max(-(p.x + 0.228), p.x + 0.16), abs(p.y) - finSpan);
    float gond = sdBox(p - vec2(0.05, -0.058), vec2(0.05, 0.008)) - 0.002;
    float st1 = sdSeg(p, vec2(0.01, -0.036), vec2(0.015, -0.052));
    float st2 = sdSeg(p, vec2(0.09, -0.034), vec2(0.085, -0.052));
    float prop = sdBox(p - vec2(-0.008, -0.058), vec2(0.002, 0.012));
    float d = min(min(env, fin), min(gond, min(min(st1, st2) - 0.0025, prop)));
    return d * s;
}

vec3 ships(vec2 pw, vec3 col){
    if(uShips < 0.0) return col;
    for(int i = 0; i < 7; i++){
        vec3 h = hash31(float(i) * 11.3 + 2.0);
        float depth = 0.25 + 0.75 * h.x;
        float s = 0.30 + 0.8 * depth;
        vec2 start = vec2(-2.4 + 3.0 * h.y, -0.02 + 0.22 * h.z);
        float tt = uShips - h.z * 2.5;
        vec2 pos = start + vec2(0.045 + 0.05 * depth, 0.022 + 0.012 * h.y) * tt;
        vec2 pp = pw + uCamPos * ((0.4 + 0.5 * depth) - 1.0) - pos;
        float d = airship(pp, s * 0.55);
        float m = 1.0 - smoothstep(-PX, PX, d);
        vec3 sc = mix(vec3(0.012, 0.012, 0.02), mix(uSkyHor, uSkyMid, 0.6) * 0.55, 0.65 * (1.0 - depth));
        vec2 sd = normalize(uSunPos - pw) * 0.003;
        float rim = step(0.0, airship(pp + sd, s * 0.55)) * 0.6;
        sc += uSunCol * rim * 0.35 * depth;
        vec2 lp = pp / (s * 0.55);
        float rib = smoothstep(0.35, 0.5, abs(fract(lp.x * 28.0) - 0.5)) * step(-0.045, lp.y);
        sc *= 1.0 + 0.25 * rib * depth;
        vec2 gl = lp - vec2(0.05, -0.058);
        float lamps = 0.0;
        for(int k = 0; k < 4; k++){ vec2 o = gl - vec2(-0.033 + 0.022 * float(k), 0.0); lamps += exp(-dot(o, o) / 0.00002); }
        col = mix(col, sc, m * step(0.0, tt));
        col += vec3(1.0, 0.62, 0.28) * lamps * 1.6 * depth * step(0.0, tt);
    }
    return col;
}

// ---------------- foreground overlook + Mara's bench (screen-anchored layer)
float groundF(float x){
    return -0.44 + 0.24 * smoothstep(1.1, -0.9, x) + 0.012 * fbm(vec2(x * 8.0, 0.0));
}

vec3 foreground(vec2 sp, vec3 col){
    if(uFore <= 0.0) return col;
    vec2 pf = sp * 1.3 + uFgOff;
    float ground = groundF(pf.x);
    float px = PX * 1.3 / uCamH;
    float g = 1.0 - smoothstep(-px, px, pf.y - ground);
    float gx = pf.x * 180.0;
    float gi = floor(gx);
    float gh = (0.35 + 0.65 * hash11(gi)) * 0.03 * smoothstep(1.1, -0.2, pf.x);
    float yy = (pf.y - ground) / max(gh, 1e-4);
    float lean = (hash11(gi + 3.0) - 0.5) * 0.8 + 0.3 * sin(uTime * 1.3 + gi * 0.3);
    float bx = fract(gx) - 0.5 - lean * yy * 0.6;
    float blade = step(abs(bx), 0.22 * (1.0 - yy)) * step(0.0, yy) * step(yy, 1.0);
    float m = max(g, blade);
    float bm = 0.0; float scarf = 0.0;
    float benchX = -0.2;
    vec2 bp = (pf - vec2(benchX, groundF(benchX) + 0.05)) / 1.5;
    if(uBench > 0.0){
        float seat = sdBox(bp - vec2(0.0, 0.02), vec2(0.13, 0.006));
        float back1 = sdBox(bp - vec2(0.0, 0.078), vec2(0.13, 0.0055));
        float back2 = sdBox(bp - vec2(0.0, 0.055), vec2(0.13, 0.004));
        float leg1 = sdBox(bp - vec2(-0.11, -0.012), vec2(0.005, 0.034));
        float leg2 = sdBox(bp - vec2(0.11, -0.012), vec2(0.005, 0.034));
        float post1 = sdBox(bp - vec2(-0.115, 0.05), vec2(0.004, 0.035));
        float post2 = sdBox(bp - vec2(0.115, 0.05), vec2(0.004, 0.035));
        float arm1 = sdBox(bp - vec2(-0.13, 0.04), vec2(0.012, 0.003));
        float arm2 = sdBox(bp - vec2(0.13, 0.04), vec2(0.012, 0.003));
        float d = min(min(min(seat, back1), min(back2, leg1)), min(min(leg2, post1), min(post2, min(arm1, arm2))));
        bm = (1.0 - smoothstep(-px / 1.5, px / 1.5, d)) * uBench;
        vec2 s2 = bp - vec2(0.05, 0.081);
        float wave = 0.007 * sin(s2.y * 80.0 + uTime * 4.5) * clamp(-s2.y * 18.0, 0.0, 1.0);
        float drape = sdBox(vec2(s2.x - wave + s2.y * 0.35, s2.y + 0.034), vec2(0.0085, 0.034));
        float tail = sdBox(vec2(s2.x + 0.022 - wave * 1.6, s2.y + 0.022), vec2(0.0065, 0.024));
        float wrap = sdBox(s2 - vec2(-0.01, 0.001), vec2(0.022, 0.0065));
        scarf = (1.0 - smoothstep(-px / 1.5, px / 1.5, min(min(drape, tail), wrap))) * uBench;
    }
    vec3 fg = vec3(0.005, 0.005, 0.008);
    float ridge = smoothstep(0.014, 0.0, abs(pf.y - ground));
    fg += uSunCol * 0.14 * ridge;
    col = mix(col, fg, max(m, bm) * uFore);
    // rim light on the bench from the sky
    col += uSunCol * 0.06 * bm * smoothstep(0.0, 0.1, bp.y) * uFore;
    vec3 scol = vec3(0.55, 0.025, 0.035) * (0.35 + 0.9 * uSunCol.r);
    col = mix(col, scol, scarf * uFore);
    return col;
}

void main(){
    PX = uCamH / uRes.y;
    vec2 sp = (vUV - 0.5) * vec2(uRes.x / uRes.y, 1.0);
    vec2 pw = sp * uCamH + uCamPos;
    vec3 col;
    if(pw.y > WATER){
        col = city(pw);
        col = ships(pw, col);
    } else {
        float depth = WATER - pw.y;
        vec2 rp = vec2(pw.x + 0.004 * sin(pw.y * 260.0 + uTime * 2.0) * (1.0 + depth * 8.0) + 0.012 * (fbm(vec2(pw.x * 3.0, pw.y * 60.0 + uTime * 0.5)) - 0.5),
                       2.0 * WATER - pw.y);
        col = city(rp) * 0.45 * vec3(0.8, 0.9, 1.0);
        col = mix(col, uSkyHor * 0.05, smoothstep(0.0, 0.3, depth));
    }
    // bridge across the river (Glimmith Bridge)
    {
        vec2 pb = pw;
        float deck = sdBox(pb - vec2(-0.2, -0.205), vec2(4.2, 0.012));
        float par = sdBox(pb - vec2(-0.2, -0.186), vec2(4.2, 0.007));
        float body = sdBox(pb - vec2(-0.2, -0.26), vec2(4.2, 0.05));
        float ax = mod(pb.x + 0.2, 0.34) - 0.17;
        float arch = length(vec2(ax, (pb.y + 0.305) * 0.85)) - 0.128;
        body = max(body, -arch);
        float d = min(min(deck, par), body);
        float m = 1.0 - smoothstep(-PX, PX, d);
        vec2 lp = vec2(ax, pb.y + 0.163);
        float lamp = exp(-dot(lp, lp) / 0.000012) * 4.0 + exp(-length(lp) / 0.018) * 0.3;
        float lampPost = sdBox(vec2(ax, pb.y + 0.175), vec2(0.001, 0.012));
        m = max(m, 1.0 - smoothstep(-PX, PX, lampPost));
        vec3 bc = vec3(0.008, 0.008, 0.013);
        bc += uSunCol * 0.12 * smoothstep(0.006, 0.0, abs(pb.y + 0.18));
        float lampOn = smoothstep(0.2, 0.5, uLamps) * (1.0 - uBroken);
        if(uShatter >= 0.0) lampOn *= 1.0 - smoothstep(0.0, 1.5, uShatter - abs(pb.x - uShatterX) * 0.45);
        col = mix(col, bc, m);
        col += vec3(1.0, 0.62, 0.28) * lamp * lampOn * step(-0.3, pb.y) * step(pb.y, -0.12);
        if(pw.y < WATER){
            float streak = exp(-ax * ax / 0.00003) * exp(-(WATER - pw.y) * 5.0) * (0.55 + 0.45 * sin(pw.y * 300.0 + uTime * 3.0));
            col += vec3(1.0, 0.6, 0.28) * streak * lampOn * 0.9;
        }
    }
    if(uArchive > 0.0){
        vec2 ad = pw - uArchivePos;
        float win = step(abs(ad.x), 0.004) * step(abs(ad.y), 0.007);
        float fl = 0.85 + 0.15 * sin(uTime * 7.0) * sin(uTime * 3.1);
        col = mix(col, vec3(2.4, 1.3, 0.55) * fl, win * uArchive);
        col += vec3(1.0, 0.55, 0.22) * exp(-length(ad) / 0.02) * 0.35 * uArchive * fl;
    }
    float fogm = exp(-abs(pw.y - (WATER + 0.04)) * 10.0) * uFog;
    col = mix(col, mix(uSkyHor, uSkyMid, 0.35) * 0.55, fogm * (0.4 + 0.6 * fbm(vec2(pw.x * 2.0 + uTime * 0.05, pw.y * 8.0))));
    col = foreground(sp, col);
    if(uAsh > 0.0){
        for(int L = 0; L < 3; L++){
            float fl = float(L);
            float sc = 14.0 + fl * 9.0;
            vec2 q = sp * sc + vec2(sin(uTime * 0.3 + fl) * 0.8, uTime * (0.35 + 0.15 * fl));
            vec2 ip = floor(q);
            vec2 h = hash22(ip + fl * 17.0);
            vec2 o = fract(q) - 0.5 - (h - 0.5) * 0.7 - 0.12 * vec2(sin(uTime * 1.1 + h.x * 30.0), 0.0);
            float r = (0.035 + 0.03 * h.y) * (1.0 + fl * 0.2);
            float f = smoothstep(r, r * 0.4, length(o * vec2(1.0, 1.6))) * step(0.55, hash21(ip + 3.0 + fl));
            col = mix(col, vec3(0.55, 0.55, 0.56) * (0.5 + 0.5 * uSunCol.r), f * uAsh * (0.35 + 0.2 * fl));
        }
    }
    fragColor = vec4(col, 1.0);
}
