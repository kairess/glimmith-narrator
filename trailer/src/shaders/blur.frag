#version 330
in vec2 vUV; out vec4 f;
uniform sampler2D uSrc; uniform vec2 uDir;
void main(){
    // 9-tap gaussian using linear sampling offsets
    vec3 c = texture(uSrc, vUV).rgb * 0.2270270270;
    c += texture(uSrc, vUV + uDir*1.3846153846).rgb * 0.3162162162;
    c += texture(uSrc, vUV - uDir*1.3846153846).rgb * 0.3162162162;
    c += texture(uSrc, vUV + uDir*3.2307692308).rgb * 0.0702702703;
    c += texture(uSrc, vUV - uDir*3.2307692308).rgb * 0.0702702703;
    f = vec4(c, 1.0);
}
