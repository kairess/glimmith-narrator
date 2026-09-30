#version 330
in vec2 vUV; out vec4 f;
uniform sampler2D uSrc; uniform vec2 uCenter; uniform float uDecay; uniform float uLen;
float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
void main(){
    const int N = 72;
    vec2 d = (vUV - uCenter) * uLen / float(N);
    vec2 uv = vUV - d * h(vUV*1000.0);
    float w = 1.0; vec3 acc = vec3(0.0);
    for(int i=0;i<N;i++){ acc += texture(uSrc, uv).rgb * w; w *= uDecay; uv -= d; }
    f = vec4(acc / float(N) * 2.2, 1.0);
}
