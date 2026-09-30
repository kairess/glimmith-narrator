#version 330
in vec2 vUV; out vec4 f;
uniform sampler2D uSrc; uniform vec2 uTexel;
void main(){
    vec2 t = uTexel;
    vec3 c = texture(uSrc, vUV).rgb*4.0;
    c += texture(uSrc, vUV+vec2(-t.x,-t.y)).rgb + texture(uSrc, vUV+vec2(t.x,-t.y)).rgb
       + texture(uSrc, vUV+vec2(-t.x,t.y)).rgb + texture(uSrc, vUV+vec2(t.x,t.y)).rgb;
    f = vec4(c/8.0, 1.0);
}
