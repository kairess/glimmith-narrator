// ---------- common utilities ----------
#define PI 3.14159265359
#define TAU 6.28318530718

uniform vec2  uRes;
uniform float uTime;      // global time (s)
uniform float uT;         // shot-local time (s)

float hash11(float p){ p = fract(p*.1031); p *= p+33.33; p *= p+p; return fract(p); }
float hash21(vec2 p){ vec3 p3 = fract(vec3(p.xyx)*.1031); p3 += dot(p3, p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
vec2  hash22(vec2 p){ vec3 p3 = fract(vec3(p.xyx)*vec3(.1031,.1030,.0973)); p3 += dot(p3, p3.yzx+33.33); return fract((p3.xx+p3.yz)*p3.zy); }
vec3  hash31(float p){ vec3 p3 = fract(vec3(p)*vec3(.1031,.1030,.0973)); p3 += dot(p3, p3.yzx+33.33); return fract((p3.xxy+p3.yzz)*p3.zyx); }

float vnoise(vec2 p){
    vec2 i = floor(p), f = fract(p);
    vec2 u = f*f*(3.0-2.0*f);
    return mix(mix(hash21(i), hash21(i+vec2(1,0)), u.x),
               mix(hash21(i+vec2(0,1)), hash21(i+vec2(1,1)), u.x), u.y);
}
float fbm(vec2 p){
    float a = 0.5, s = 0.0;
    mat2 m = mat2(1.6, 1.2, -1.2, 1.6);
    for(int i=0;i<5;i++){ s += a*vnoise(p); p = m*p; a *= 0.5; }
    return s;
}
float fbm3(vec2 p){
    float a = 0.5, s = 0.0;
    mat2 m = mat2(1.6, 1.2, -1.2, 1.6);
    for(int i=0;i<3;i++){ s += a*vnoise(p); p = m*p; a *= 0.5; }
    return s;
}

mat2 rot(float a){ float c=cos(a), s=sin(a); return mat2(c,-s,s,c); }

float sdCircle(vec2 p, float r){ return length(p)-r; }
float sdBox(vec2 p, vec2 b){ vec2 d = abs(p)-b; return length(max(d,0.0))+min(max(d.x,d.y),0.0); }
float sdSeg(vec2 p, vec2 a, vec2 b){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/dot(ba,ba),0.,1.); return length(pa-ba*h); }
// pointed (gothic) arch: width 2*w, straight part height h (from y=0 to y=h), pointed top above
// equilateral arch: circles of radius 2w centred on the opposite springing points
float sdGothicArch(vec2 p, float w, float h){
    vec2 q = vec2(abs(p.x) + w, max(p.y - h, 0.0));
    return max(length(q) - 2.0*w, -p.y);
}

// jewel palette for stained glass (linear light)
vec3 jewel(float k){
    int i = int(mod(floor(k), 8.0));
    if(i==0) return vec3(0.80, 0.06, 0.08);   // ruby
    if(i==1) return vec3(0.06, 0.20, 0.85);   // cobalt
    if(i==2) return vec3(1.00, 0.52, 0.06);   // amber
    if(i==3) return vec3(0.06, 0.55, 0.22);   // emerald
    if(i==4) return vec3(0.48, 0.10, 0.62);   // violet
    if(i==5) return vec3(1.00, 0.80, 0.30);   // gold
    if(i==6) return vec3(0.05, 0.48, 0.55);   // teal
    return vec3(0.80, 0.30, 0.10);            // copper
}

float luma(vec3 c){ return dot(c, vec3(0.2126,0.7152,0.0722)); }

// voronoi: returns (F1 distance, edge distance, cell id hash)
vec3 voronoi(vec2 x, float jitter){
    vec2 n = floor(x), f = fract(x);
    vec2 mg, mr; float md = 8.0;
    for(int j=-1;j<=1;j++) for(int i=-1;i<=1;i++){
        vec2 g = vec2(i,j);
        vec2 o = 0.5 + jitter*(hash22(n+g)-0.5);
        vec2 r = g + o - f;
        float d = dot(r,r);
        if(d<md){ md=d; mr=r; mg=g; }
    }
    float ed = 8.0;
    for(int j=-2;j<=2;j++) for(int i=-2;i<=2;i++){
        vec2 g = mg + vec2(i,j);
        vec2 o = 0.5 + jitter*(hash22(n+g)-0.5);
        vec2 r = g + o - f;
        if(dot(mr-r,mr-r)>0.00001) ed = min(ed, dot(0.5*(mr+r), normalize(r-mr)));
    }
    return vec3(sqrt(md), ed, hash21(n+mg));
}
