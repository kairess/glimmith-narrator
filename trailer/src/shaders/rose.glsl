// ---------- procedural rose window (window space: glass radius = 1) ----------
// Returns stone-tracery distance, lead distance, a structural colour key and a fill order.
struct RoseHit {
    float dStone;   // distance to heavy stone tracery (world units)
    float dLead;    // distance to thin lead cames (world units)
    float key;      // structural cell key -> colour
    float order;    // 0..1 order in which colour arrives
    float piece;    // hash of the small glass piece
    float zone;
};

uniform float uPxWorld;   // world units per pixel (for derivative-normalised distances)

float nd(float d){ // normalise a warped distance field to world units via screen derivatives
    float g = length(vec2(dFdx(d), dFdy(d)));
    return d / max(g, 1e-5) * uPxWorld;
}

vec3 roseColor(float key, float piece){
    // hand-picked structural palette: deep blue ground with ruby / gold accents
    int k = int(key + 0.5);
    vec3 c;
    if(k==0)       c = vec3(1.00, 0.70, 0.18);  // centre gold
    else if(k==1)  c = vec3(0.78, 0.03, 0.05);  // centre petals ruby
    else if(k==2)  c = vec3(0.03, 0.09, 0.62);  // centre ground cobalt
    else if(k==3)  c = vec3(0.38, 0.05, 0.52);  // ring B violet
    else if(k==4)  c = vec3(0.03, 0.26, 0.60);  // ring B blue
    else if(k==5)  c = vec3(1.00, 0.52, 0.06);  // lancet head amber
    else if(k==6)  c = vec3(0.78, 0.04, 0.06);  // lancet upper ruby
    else if(k==7)  c = vec3(0.03, 0.42, 0.20);  // lancet lower emerald
    else if(k==8)  c = vec3(0.02, 0.07, 0.48);  // spandrel deep blue
    else if(k==9)  c = vec3(1.00, 0.74, 0.25);  // spandrel roundlet gold
    else if(k==10) c = vec3(0.72, 0.04, 0.05);  // band D ruby
    else if(k==11) c = vec3(0.03, 0.34, 0.40);  // band D teal
    else if(k==12) c = vec3(0.82, 0.05, 0.08);  // roundel core ruby
    else if(k==13) c = vec3(0.03, 0.40, 0.18);  // roundel quadrant emerald
    else if(k==14) c = vec3(0.95, 0.45, 0.05);  // roundel quadrant amber
    else if(k==15) c = vec3(1.00, 0.78, 0.32);  // small roundlet gold
    else if(k==16) c = vec3(0.02, 0.08, 0.52);  // outer spandrel cobalt
    else if(k==17) c = vec3(0.34, 0.05, 0.48);  // outer band violet
    else if(k==18) c = vec3(0.03, 0.12, 0.58);  // outer band blue
    else           c = vec3(1.00, 0.62, 0.14);  // outer jewels amber
    // per-piece variation (glass batches are never identical)
    float v = piece;
    c *= 0.62 + 0.7*v*v;
    c = mix(c, c.gbr*0.9 + c*0.1, 0.08*(hash11(piece*91.7)-0.5));
    return c;
}

RoseHit rose(vec2 p){
    RoseHit h;
    float r = length(p);
    float a = atan(p.x, p.y);                 // 0 at top, clockwise
    const float R0=0.13, R1=0.20, R2=0.56, R3=0.62, R4=0.90, R5=1.0;
    float BIG = 1e3;
    float dS = BIG, dL = BIG, key = 0.0, zone = 0.0;

    // ---- sector frames
    float u12 = a / (TAU/12.0); float s12 = floor(u12 + 0.5); float f12 = u12 - s12;   // f in [-.5,.5]
    float u24 = a / (TAU/24.0); float s24 = floor(u24 + 0.5); float f24 = u24 - s24;
    float u48 = a / (TAU/48.0); float s48 = floor(u48 + 0.5); float f48 = u48 - s48;
    float u6  = a / (TAU/6.0);  float s6  = floor(u6 + 0.5);  float f6  = u6 - s6;
    vec2 q12 = r * vec2(sin(f12*TAU/12.0), cos(f12*TAU/12.0));   // local frame, sector axis = +y
    vec2 q6  = r * vec2(sin(f6*TAU/6.0),  cos(f6*TAU/6.0));
    // boundary between 12-sectors (true arc distance)
    float d12b = (0.5 - abs(f12)) * (TAU/12.0) * r;
    float d24b = (0.5 - abs(f24)) * (TAU/24.0) * r;
    float d48b = (0.5 - abs(f48)) * (TAU/48.0) * r;
    // offset 12-frame (sector boundaries centred) for spandrel roundlets
    float u12o = a / (TAU/12.0) + 0.5; float s12o = floor(u12o + 0.5); float f12o = u12o - s12o;
    vec2 q12o = r * vec2(sin(f12o*TAU/12.0), cos(f12o*TAU/12.0));

    // ---- lancet in angularly-normalised frame (width follows the wedge)
    const float RREF = 0.38;
    vec2 ql = vec2(f12 * (TAU/12.0) * RREF, r);
    float lanc = nd(sdGothicArch(ql - vec2(0.0, R1 + 0.022), 0.074, 0.186));
    float lancHead = length(vec2(ql.x*r/RREF, r) - vec2(0.0, 0.438)) - 0.043;
    float spRound = length(q12o - vec2(0.0, 0.48)) - 0.032;

    // ---- roundels
    vec2 qr = q12 - vec2(0.0, 0.76);
    float roundel = length(qr) - 0.118;
    float roundCore = length(qr) - 0.045;
    vec2 qd = vec2(qr.x + qr.y, qr.x - qr.y) * 0.70710678;
    float smallR = length(q12o - vec2(0.0, 0.78)) - 0.05;
    float jewel = length(r*vec2(sin(f48*TAU/48.0), cos(f48*TAU/48.0)) - vec2(0.0, 0.952)) - 0.02;

    // ---- centre rosette
    float centre = r - 0.036;
    float petal = length(q6 - vec2(0.0, 0.072)) - 0.034;

    if(r < R0){
        zone = 0.0;
        dS = min(abs(r - R0), BIG);
        dL = min(abs(centre), centre > 0.0 ? abs(petal) : BIG);
        key = centre < 0.0 ? 0.0 : (petal < 0.0 ? 1.0 : 2.0);
    } else if(r < R1){
        zone = 1.0;
        dS = min(r - R0, R1 - r);
        dL = d12b;
        key = 3.0 + mod(s12, 2.0);
    } else if(r < R2){
        zone = 2.0;
        dS = min(r - R1, R2 - r);
        dS = min(dS, abs(lanc));
        if(lanc < 0.0){
            dL = min(abs(lancHead), abs(r - 0.33));
            key = lancHead < 0.0 ? 5.0 : (r > 0.33 ? 6.0 : 7.0);
            if(mod(s12, 2.0) > 0.5 && key > 5.5) key = 13.0 - key; // swap ruby/emerald on odd spokes
        } else {
            dS = min(dS, abs(spRound));
            dL = spRound < 0.0 ? BIG : d12b;
            key = spRound < 0.0 ? 9.0 : 8.0;
        }
    } else if(r < R3){
        zone = 3.0;
        dS = min(r - R2, R3 - r);
        dL = d24b;
        key = 10.0 + mod(s24, 2.0);
    } else if(r < R4){
        zone = 4.0;
        dS = min(r - R3, R4 - r);
        dS = min(dS, min(abs(roundel), abs(smallR)));
        if(roundel < 0.0){
            dL = min(abs(roundCore), roundCore > 0.0 ? min(abs(qd.x), abs(qd.y)) : BIG);
            key = roundCore < 0.0 ? 12.0 : ((qd.x*qd.y > 0.0) ? 13.0 : 14.0);
        } else if(smallR < 0.0){
            dL = BIG; key = 15.0;
        } else {
            dL = d12b + 0.0*d24b;
            key = 16.0;
        }
    } else if(r < R5){
        zone = 5.0;
        dS = min(r - R4, R5 - r);
        dL = min(d48b, abs(jewel));
        key = jewel < 0.0 ? 19.0 : 17.0 + mod(s48, 2.0);
    } else {
        zone = 6.0;
        dS = r - R5;
        dL = BIG;
        key = 20.0;
    }

    // small glass pieces: voronoi cames within each structural cell
    vec3 vo = voronoi(p * 16.0 + vec2(3.1, 7.7), 0.9);
    float piece = hash11(vo.z * 71.3 + key * 13.1);
    int ki = int(key + 0.5);
    bool large = (ki==2 || ki==6 || ki==7 || ki==8 || ki==13 || ki==14 || ki==16 || ki==17 || ki==18);
    if(large) dL = min(dL, vo.y / 16.0);
    else piece = hash11(key * 5.3 + s12 * 0.77 + s48 * 0.13);

    h.dStone = dS; h.dLead = dL; h.key = key; h.piece = piece; h.zone = zone;
    // colour arrival order: from centre outward with a little per-piece jitter
    h.order = clamp(r * 0.82 + 0.14 * hash11(key * 3.7 + s12 * 1.31) + 0.04 * piece, 0.0, 1.0);
    return h;
}
