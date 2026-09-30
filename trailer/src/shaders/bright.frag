#version 330
in vec2 vUV; out vec4 f;
uniform sampler2D uSrc; uniform float uThresh; uniform vec2 uRes;
void main(){
    vec2 t = 1.0/uRes*0.5;
    vec3 c = texture(uSrc, vUV+vec2(-t.x,-t.y)).rgb + texture(uSrc, vUV+vec2(t.x,-t.y)).rgb
           + texture(uSrc, vUV+vec2(-t.x,t.y)).rgb + texture(uSrc, vUV+vec2(t.x,t.y)).rgb;
    c *= 0.25;
    float l = max(c.r, max(c.g, c.b));
    float k = 0.5;
    float soft = clamp(l - uThresh + k, 0.0, 2.0*k); soft = soft*soft/(4.0*k+1e-4);
    float w = max(soft, l - uThresh) / max(l, 1e-4);
    f = vec4(min(c*w, vec3(40.0)), 1.0);
}
