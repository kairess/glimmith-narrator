"""Shatter geometry: Voronoi shards of the rose window + a GL renderer that animates them on the GPU."""
import numpy as np
import moderngl
from scipy.spatial import Voronoi

IMPACT = np.array([0.52, -0.50])


def _clip(poly, cx, cy, nx, ny, d):
    """Clip convex polygon by half-plane n.p <= d."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        da = a[0] * nx + a[1] * ny - d
        db = b[0] * nx + b[1] * ny - d
        if da <= 0:
            out.append(a)
        if da * db < 0:
            t = da / (da - db)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def make_shards(seed=3, n_uniform=150, n_radial=190):
    rng = np.random.default_rng(seed)
    pts = []
    # radial crack pattern around the impact point
    rays = 17
    for k in range(rays):
        ang = k / rays * 2 * np.pi + rng.uniform(-0.12, 0.12)
        r = 0.035
        while r < 2.2:
            jitter = rng.normal(0, 0.05) * r
            a2 = ang + rng.uniform(-0.09, 0.09)
            pts.append(IMPACT + np.array([np.cos(a2), np.sin(a2)]) * r + rng.normal(0, 0.012, 2))
            r *= rng.uniform(1.28, 1.5)
    # uniform fill
    while len(pts) < n_radial + n_uniform:
        p = rng.uniform(-1, 1, 2)
        if np.hypot(*p) < 1.0:
            pts.append(p)
    pts = np.array([p for p in pts if np.hypot(*p) < 1.08])
    # mirror points to bound the diagram
    far = np.array([[5, 5], [-5, 5], [5, -5], [-5, -5], [0, 6], [0, -6], [6, 0], [-6, 0]])
    vor = Voronoi(np.vstack([pts, far]))
    circle = [(np.cos(a), np.sin(a)) for a in np.linspace(0, 2 * np.pi, 160, endpoint=False)]
    shards = []
    for i in range(len(pts)):
        reg = vor.regions[vor.point_region[i]]
        if -1 in reg or len(reg) == 0:
            continue
        poly = [tuple(vor.vertices[v]) for v in reg]
        # ensure CCW
        ar = 0.5 * sum(poly[j][0] * poly[(j + 1) % len(poly)][1] - poly[(j + 1) % len(poly)][0] * poly[j][1] for j in range(len(poly)))
        if ar < 0:
            poly = poly[::-1]
        # clip by the disc (tangent half-planes)
        for a in np.linspace(0, 2 * np.pi, 96, endpoint=False):
            nx, ny = np.cos(a), np.sin(a)
            poly = _clip(poly, 0, 0, nx, ny, 1.0)
            if len(poly) < 3:
                break
        if len(poly) >= 3:
            shards.append(np.array(poly))
    return shards


def build_vbo(shards, rng_seed=11):
    rng = np.random.default_rng(rng_seed)
    rows = []
    for s in shards:
        c = s.mean(axis=0)
        seed = rng.uniform(0, 1, 4)
        n = len(s)
        for j in range(n):
            a, b = s[j], s[(j + 1) % n]
            e = b - a
            L = np.hypot(*e) + 1e-9
            nrm = np.array([e[1], -e[0]]) / L
            dc = abs(np.dot(c - a, nrm))
            for p, ed in ((c, dc), (a, 0.0), (b, 0.0)):
                rows.append([p[0], p[1], c[0], c[1], ed, *seed])
    return np.array(rows, dtype='f4')


SHARD_VS = """#version 330
in vec2 aPos; in vec2 aCen; in float aEdge; in vec4 aSeed;
uniform mat4 uVP;
uniform float uTau;        // explosion time (slow-motion seconds)
uniform float uDrift;      // extra idle tumbling
uniform vec2  uImpact;
uniform float uCrackR;
uniform float uSpread;     // scales explosion distances
out vec2 vUV; out float vEdge; out vec3 vN; out vec3 vW; out float vCracked; out vec4 vSeed;

mat3 axisAngle(vec3 a, float ang){
    float c = cos(ang), s = sin(ang), t = 1.0 - c;
    return mat3(t*a.x*a.x + c,     t*a.x*a.y + s*a.z, t*a.x*a.z - s*a.y,
                t*a.x*a.y - s*a.z, t*a.y*a.y + c,     t*a.y*a.z + s*a.x,
                t*a.x*a.z + s*a.y, t*a.y*a.z - s*a.x, t*a.z*a.z + c);
}
void main(){
    vec2 rel = aCen - uImpact;
    float dist = length(rel);
    float delay = dist * 0.10;
    float t = max(uTau - delay, 0.0);
    float k = 0.55;
    float travel = (1.0 - exp(-k * t)) / k;
    vec2 dir = normalize(rel + (aSeed.xy - 0.5) * 0.25);
    float sp = (0.25 + 0.75 * aSeed.x) / (0.35 + dist) * 0.9;
    vec3 v = vec3(dir * sp, 0.8 + 2.2 * aSeed.y) * uSpread;
    vec3 pos = vec3(aCen, 0.0) + v * travel + vec3(0.0, -0.10, 0.0) * t * t * uSpread;
    vec3 ax = normalize(aSeed.zwx * 2.0 - 1.0 + vec3(0.0, 0.0, 0.001));
    float ang = (1.2 + 5.0 * aSeed.z) * travel * 0.9 + uDrift * (0.15 + 0.35 * aSeed.w) * step(0.001, uTau);
    mat3 R = axisAngle(ax, ang);
    float cracked = step(dist, uCrackR);
    // cracked shards sag a hair before they fly
    vec3 local = vec3(aPos - aCen, 0.0) * (1.0 - 0.012 * cracked * step(uTau, 0.0001));
    vec3 w = pos + R * local;
    w.xy += cracked * (aSeed.xy - 0.5) * 0.004 * step(uTau, 0.0001);
    gl_Position = uVP * vec4(w, 1.0);
    vUV = aPos * 0.5 + 0.5;
    vEdge = aEdge;
    vN = R * vec3(0.0, 0.0, 1.0);
    vW = w;
    vCracked = cracked;
    vSeed = aSeed;
}
"""

SHARD_FS = """#version 330
in vec2 vUV; in float vEdge; in vec3 vN; in vec3 vW; in float vCracked; in vec4 vSeed;
out vec4 f;
uniform sampler2D uWin;
uniform vec3 uCamW;
uniform vec3 uKeyDir;
uniform float uGlassGain;
uniform float uTau;
uniform float uCrackGlow;
uniform float uEdgeGlow;
uniform float uFlash;
void main(){
    vec3 g = texture(uWin, vUV).rgb;
    vec3 n = normalize(vN);
    vec3 V = normalize(uCamW - vW);
    if(dot(n, V) < 0.0) n = -n;
    float facing = abs(dot(n, V));
    vec3 col = g * uGlassGain * (0.45 + 0.55 * facing);
    // specular glints from the key light as the shard tumbles
    vec3 R = reflect(-V, n);
    float spec = pow(max(dot(R, normalize(uKeyDir)), 0.0), 60.0);
    float fres = pow(1.0 - facing, 4.0);
    col += vec3(1.0, 0.95, 0.88) * (spec * 9.0 + fres * 0.6) * step(0.0001, uTau);
    // broken edges catch the light
    float px = fwidth(vEdge) * 1.2;
    float edge = 1.0 - smoothstep(0.0, px + 0.002, vEdge);
    col += vec3(1.0, 0.95, 0.85) * edge * uEdgeGlow * step(0.0001, uTau);
    // cracks before the break
    float crack = edge * vCracked * step(uTau, 0.0001);
    col = mix(col, vec3(3.0, 2.8, 2.5) * uCrackGlow, crack * min(uCrackGlow, 1.0));
    col += vec3(1.0, 0.9, 0.8) * uFlash;
    f = vec4(col, 1.0);
}
"""

GLITTER_VS = """#version 330
in vec4 aSeed; in vec2 aOrig;
uniform mat4 uVP; uniform float uTau; uniform vec2 uImpact; uniform float uPx; uniform float uSpread;
out float vB; out vec3 vC;
float h(float x){ return fract(sin(x*127.1)*43758.5453); }
void main(){
    float t = max(uTau - length(aOrig - uImpact) * 0.1, 0.0);
    float k = 0.45;
    float travel = (1.0 - exp(-k * t)) / k;
    vec2 dir = normalize(aOrig - uImpact + (aSeed.xy - 0.5) * 0.8);
    vec3 v = vec3(dir * (0.2 + 1.6 * aSeed.x), 0.4 + 3.0 * aSeed.y) * uSpread;
    vec3 w = vec3(aOrig, 0.0) + v * travel + vec3(0.0, -0.18, 0.0) * t * t * uSpread;
    gl_Position = uVP * vec4(w, 1.0);
    float tw = 0.5 + 0.5 * sin(uTau * (8.0 + 20.0 * aSeed.z) + aSeed.w * 60.0);
    vB = step(0.0001, uTau) * tw * exp(-t * 0.25);
    gl_PointSize = uPx * (1.0 + 2.5 * aSeed.w) / max(gl_Position.w, 0.3);
    vC = mix(vec3(1.0, 0.92, 0.8), vec3(0.6 + 0.4 * h(aSeed.z * 9.0), 0.4 + 0.5 * h(aSeed.w * 7.0), 0.3 + 0.7 * h(aSeed.x * 5.0)), 0.55);
}
"""
GLITTER_FS = """#version 330
in float vB; in vec3 vC; out vec4 f;
void main(){
    vec2 d = gl_PointCoord - 0.5;
    float a = exp(-dot(d, d) * 14.0);
    f = vec4(vC * vB * a * 2.5, 1.0);
}
"""


def perspective(fovy, aspect, near, far):
    f = 1.0 / np.tan(fovy / 2)
    m = np.zeros((4, 4), dtype='f4')
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = 2 * far * near / (near - far)
    m[3, 2] = -1
    return m


def look_at(eye, target, up=(0, 1, 0)):
    eye, target, up = map(lambda v: np.array(v, dtype='f4'), (eye, target, up))
    z = eye - target
    z /= np.linalg.norm(z)
    x = np.cross(up, z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    m = np.eye(4, dtype='f4')
    m[0, :3], m[1, :3], m[2, :3] = x, y, z
    m[:3, 3] = -m[:3, :3] @ eye
    return m


FOV = np.radians(40.0)


def camera_for(camPos, camH, aspect, tilt=(0.0, 0.0), dolly=0.0, roll=0.0):
    """Perspective camera whose z=0 plane matches the flat scene camera (camPos, camH)."""
    D = (camH / 2) / np.tan(FOV / 2)
    eye = np.array([camPos[0] + tilt[0], camPos[1] + tilt[1], D - dolly])
    target = np.array([camPos[0], camPos[1], -dolly])
    up = (np.sin(roll), np.cos(roll), 0.0)
    V = look_at(eye, target, up)
    P = perspective(FOV, aspect, 0.02, 60.0)
    return P @ V, eye


class ShardRenderer:
    def __init__(self, ctx, tex_size=4096):
        self.ctx = ctx
        self.shards = make_shards()
        data = build_vbo(self.shards)
        self.n = len(data)
        self.vbo = ctx.buffer(data.tobytes())
        self.prog = ctx.program(vertex_shader=SHARD_VS, fragment_shader=SHARD_FS)
        self.vao = ctx.vertex_array(self.prog, [(self.vbo, '2f 2f 1f 4f', 'aPos', 'aCen', 'aEdge', 'aSeed')])
        rng = np.random.default_rng(5)
        N = 6000
        orig = rng.uniform(-1, 1, (N * 2, 2))
        orig = orig[np.hypot(orig[:, 0], orig[:, 1]) < 1.0][:N]
        g = np.hstack([rng.uniform(0, 1, (len(orig), 4)), orig]).astype('f4')
        self.gvbo = ctx.buffer(g.tobytes())
        self.gprog = ctx.program(vertex_shader=GLITTER_VS, fragment_shader=GLITTER_FS)
        self.gvao = ctx.vertex_array(self.gprog, [(self.gvbo, '4f 2f', 'aSeed', 'aOrig')])
        self.ng = len(g)
        self.tex_size = tex_size
        self.wins = {}
        self.win = None

    def bake_window(self, engine, name='default', **u):
        """Render the rose window (glass only) into a named shard texture."""
        tex = self.ctx.texture((self.tex_size, self.tex_size), 4, dtype='f2')
        fbo = self.ctx.framebuffer([tex])
        self.wins[name] = tex
        self.win = tex
        p, vao = engine.prog('scene_rose.frag')
        fbo.use()
        self.ctx.viewport = (0, 0, self.tex_size, self.tex_size)
        u = dict(u); u.update(uRes=(float(self.tex_size), float(self.tex_size)), uTexMode=1.0, uPxWorld=2.0 / self.tex_size)
        engine.set(p, **u)
        vao.render(moderngl.TRIANGLE_STRIP)
        self.ctx.viewport = (0, 0, engine.W, engine.H)
        tex.build_mipmaps()
        tex.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        tex.anisotropy = 8.0

    def draw(self, fbo, VP, eye, tau, drift=0.0, crackR=0.0, crackGlow=0.0, gain=1.0, key=(0.3, 0.6, 1.0),
             edgeGlow=0.8, flash=0.0, glitter=1.0, spread=1.0, H=1080, win='default'):
        ctx = self.ctx
        fbo.use()
        fbo.depth_mask = True
        fbo.color_mask = (False, False, False, False)
        fbo.clear(depth=1.0)
        fbo.color_mask = (True, True, True, True)
        fbo.use()
        ctx.enable(moderngl.DEPTH_TEST)
        self.wins[win].use(0)
        p = self.prog
        p['uVP'].write(VP.T.astype('f4').tobytes())
        for k, v in dict(uTau=tau, uDrift=drift, uImpact=tuple(IMPACT), uCrackR=crackR, uWin=0,
                         uCamW=tuple(eye), uKeyDir=key, uGlassGain=gain, uCrackGlow=crackGlow,
                         uEdgeGlow=edgeGlow, uFlash=flash, uSpread=spread).items():
            if k in p:
                p[k].value = v
        self.vao.render(moderngl.TRIANGLES)
        if glitter > 0 and tau > 0:
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.ONE, moderngl.ONE
            ctx.enable(moderngl.PROGRAM_POINT_SIZE)
            fbo.depth_mask = False
            gp = self.gprog
            gp['uVP'].write(VP.T.astype('f4').tobytes())
            for k, v in dict(uTau=tau, uImpact=tuple(IMPACT), uPx=2.2 * H / 1080 * glitter, uSpread=spread).items():
                if k in gp:
                    gp[k].value = v
            self.gvao.render(moderngl.POINTS)
            ctx.disable(moderngl.BLEND)
            fbo.depth_mask = True
        ctx.disable(moderngl.DEPTH_TEST)
