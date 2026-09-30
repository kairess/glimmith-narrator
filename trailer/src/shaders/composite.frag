#version 330
in vec2 vUV; out vec4 f;
uniform sampler2D uSrc, uB0, uB1, uB2, uB3, uB4, uRays, uOver;
uniform float uHasOver;
uniform vec2 uRes;
uniform float uExposure, uBloom, uRaysAmt, uVignette, uGrain, uCA, uLetterbox, uFade, uFlash, uSat, uContrast, uTime;
uniform float uBlur, uTiltShift, uFocusY;
uniform vec3 uFlashCol, uTint, uLift;
uniform vec2 uShake;

float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
vec3 aces(vec3 x){ const float a=2.51,b=0.03,c=2.43,d=0.59,e=0.14; return clamp((x*(a*x+b))/(x*(c*x+d)+e),0.0,1.0); }

void main(){
    vec2 uv = vUV;
    // letterbox 2.39:1
    float barH = (1.0 - (uRes.x/2.39)/uRes.y) * 0.5 * uLetterbox;
    vec2 suv = (uv - 0.5) * (1.0 - 0.02*length(uShake)) + 0.5 + uShake;
    // chromatic aberration grows toward the edges
    vec2 cd = (suv - 0.5);
    float ca = uCA * (0.3 + 1.2*dot(cd,cd)*4.0);
    vec3 c;
    c.r = texture(uSrc, suv + cd*ca).r;
    c.g = texture(uSrc, suv).g;
    c.b = texture(uSrc, suv - cd*ca).b;
    vec3 bl = texture(uB0, suv).rgb*0.35 + texture(uB1, suv).rgb*0.3 + texture(uB2, suv).rgb*0.22
            + texture(uB3, suv).rgb*0.18 + texture(uB4, suv).rgb*0.15;
    // defocus: lean on the blurred pyramid (bloom levels hold bright energy only, so re-blur via mip of src is unavailable;
    // approximate with a wide tap of the source)
    float dof = clamp(uBlur + uTiltShift * pow(abs(uv.y - uFocusY)*2.0, 1.5), 0.0, 1.0);
    if(dof > 0.001){
        vec3 acc = vec3(0.0); float wsum = 0.0;
        float rad = dof * 14.0;
        for(int i=0;i<24;i++){
            float a = float(i)*2.39996;
            float r = sqrt(float(i)+0.5)/sqrt(24.0);
            vec2 o = vec2(cos(a), sin(a)) * r * rad / uRes;
            acc += texture(uSrc, suv + o).rgb; wsum += 1.0;
        }
        c = mix(c, acc/wsum, smoothstep(0.0, 0.3, dof));
    }
    c += bl * uBloom;
    c += texture(uRays, suv).rgb * uRaysAmt;
    c *= uExposure * uTint;
    c = aces(c);
    // grade
    c = pow(c, vec3(1.0/1.0));
    float l = dot(c, vec3(0.2126,0.7152,0.0722));
    c = mix(vec3(l), c, uSat);
    c = (c - 0.5) * uContrast + 0.5;
    c = c + uLift * (1.0 - c);
    // vignette
    vec2 vd = (uv - 0.5) * vec2(uRes.x/uRes.y, 1.0);
    c *= 1.0 - uVignette * smoothstep(0.35, 1.05, length(vd));
    c = clamp(c, 0.0, 1.0);
    // flash
    c = mix(c, uFlashCol, clamp(uFlash, 0.0, 1.0));
    c *= uFade;
    // grain (luma-weighted, stronger in mids)
    float g = h(uv*uRes + fract(uTime*7.13)*100.0) - 0.5;
    c += g * uGrain * (0.35 + 0.65*(1.0 - abs(l*2.0-1.0)));
    // letterbox bars
    float bar = step(uv.y, barH) + step(1.0 - barH, uv.y);
    c = mix(c, vec3(0.0), clamp(bar, 0.0, 1.0));
    // sRGB-ish encode (ACES output treated as display-linear -> gamma)
    c = pow(clamp(c,0.0,1.0), vec3(1.0/2.2));
    // overlay text (premultiplied, display space)
    if(uHasOver > 0.5){
        vec4 o = texture(uOver, vec2(uv.x, 1.0 - uv.y));
        c = mix(c, o.rgb, o.a);
    }
    // dither
    c += (h(uv*uRes + 17.0) - 0.5) / 255.0;
    f = vec4(c, 1.0);
}
