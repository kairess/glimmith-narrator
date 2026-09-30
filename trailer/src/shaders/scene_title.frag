#version 330
//#include common
in vec2 vUV;
out vec4 fragColor;
uniform sampler2D uMask;   // r: fill, g: outline, b: soft glow
uniform float uReveal;     // glass pieces appear
uniform float uSweep;      // light sweep position (-0.5 .. 1.5)
uniform float uGlow;
uniform float uBeam;
void main(){
    vec2 sp = (vUV - 0.5) * vec2(uRes.x / uRes.y, 1.0);
    vec4 m = texture(uMask, vec2(vUV.x, 1.0 - vUV.y));
    vec3 c = vec3(0.004, 0.004, 0.007) * (1.0 - length(sp));
    // soft beam behind
    float shaft = exp(-pow(sp.x / (0.25 + 0.3 * (0.5 - sp.y)), 2.0)) * smoothstep(-0.5, 0.5, sp.y);
    c += vec3(0.9, 0.8, 0.65) * shaft * 0.06 * uBeam;
    // letters assemble from glass fragments, then light passes through them
    vec3 vo = voronoi(sp * 34.0, 0.95);
    float order = hash11(vo.z * 37.0);
    float on = smoothstep(order, order + 0.08, uReveal * 1.1);
    float sweep = exp(-pow((sp.x + sp.y * 0.35 - (uSweep - 0.5) * 2.2) / 0.16, 2.0));
    float yv = vUV.y - 0.46;
    vec3 ivory = mix(vec3(0.95, 0.72, 0.42), vec3(1.25, 1.1, 0.9), smoothstep(-0.05, 0.05, yv));
    vec3 jc = jewel(floor(vo.z * 8.0 + 0.5));
    vec3 letter = ivory * (0.9 + 0.2 * fbm(sp * 60.0));
    letter = mix(letter, jc * 2.2 + ivory * 0.3, sweep * 0.75);
    letter *= 1.0 - 0.55 * (1.0 - smoothstep(0.0, 0.05, vo.y)) * sweep;   // cames visible in the light
    letter *= 1.0 + 1.6 * sweep;
    c = mix(c, letter, m.r * on);
    c += vec3(1.0, 0.75, 0.45) * m.b * uGlow * (0.25 + 1.2 * sweep) * smoothstep(0.3, 1.0, uReveal);
    fragColor = vec4(c, 1.0);
}
