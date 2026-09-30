"""GPU rendering engine: scene shaders -> HDR -> bloom / god rays -> graded LDR frame."""
import os, re
import numpy as np
import moderngl

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.join(HERE, 'shaders')

VERT = """#version 330
in vec2 aPos; out vec2 vUV;
void main(){ vUV = aPos*0.5+0.5; gl_Position = vec4(aPos,0.0,1.0); }"""


def load_src(name):
    src = open(os.path.join(SH, name)).read()
    def inc(m):
        return open(os.path.join(SH, m.group(1) + '.glsl')).read()
    for _ in range(3):
        src = re.sub(r'//#include (\w+)', inc, src)
    return src


class Engine:
    def __init__(self, W=1920, H=1080):
        self.W, self.H = W, H
        self.ctx = moderngl.create_standalone_context()
        ctx = self.ctx
        self.quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype='f4'))
        self.progs = {}
        self.vaos = {}
        self.hdr = self._tex(W, H)
        self.hdr2 = self._tex(W, H)
        self.hdr3 = self._tex(W, H)
        self.fb_hdr = ctx.framebuffer([self.hdr], ctx.depth_renderbuffer((W, H)))
        self.fb_hdr2 = ctx.framebuffer([self.hdr2], ctx.depth_renderbuffer((W, H)))
        self.fb_hdr3 = ctx.framebuffer([self.hdr3])
        # bloom pyramid
        self.levels = []
        w, h = W // 2, H // 2
        for i in range(5):
            a, b = self._tex(w, h), self._tex(w, h)
            self.levels.append((a, b, ctx.framebuffer([a]), ctx.framebuffer([b]), w, h))
            w, h = max(w // 2, 1), max(h // 2, 1)
        self.rays = self._tex(W // 2, H // 2)
        self.fb_rays = ctx.framebuffer([self.rays])
        self.ldr = ctx.texture((W, H), 4, dtype='f1')
        self.fb_ldr = ctx.framebuffer([self.ldr])
        self.overlay = ctx.texture((W, H), 4, dtype='f1')
        self.overlay.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.post_src = {}

    def _tex(self, w, h, comps=4):
        t = self.ctx.texture((w, h), comps, dtype='f2')
        t.filter = (moderngl.LINEAR, moderngl.LINEAR)
        t.repeat_x = False
        t.repeat_y = False
        return t

    def prog(self, name):
        if name not in self.progs:
            p = self.ctx.program(vertex_shader=VERT, fragment_shader=load_src(name))
            self.progs[name] = p
            self.vaos[name] = self.ctx.vertex_array(p, [(self.quad, '2f', 'aPos')])
        return self.progs[name], self.vaos[name]

    @staticmethod
    def set(p, **u):
        for k, v in u.items():
            if k in p:
                try:
                    p[k].value = v
                except Exception as e:
                    raise RuntimeError(f'uniform {k}: {e}')

    def draw(self, name, fbo, **u):
        p, vao = self.prog(name)
        fbo.use()
        self.set(p, **u)
        vao.render(moderngl.TRIANGLE_STRIP)

    # ---------------------------------------------------------------- post
    def post(self, src_tex, P, overlay=None):
        """src_tex: HDR scene. P: dict of post params. returns uint8 HxWx3."""
        ctx = self.ctx
        W, H = self.W, self.H
        # bright pass -> level0
        src_tex.use(0)
        a0 = self.levels[0]
        self.draw('bright.frag', a0[2], uSrc=0, uThresh=P.get('thresh', 0.9), uRes=(a0[4], a0[5]))
        # downsample chain + blur each
        for i in range(len(self.levels)):
            a, b, fa, fb, w, h = self.levels[i]
            if i > 0:
                self.levels[i - 1][0].use(0)
                self.draw('down.frag', fa, uSrc=0, uTexel=(1.0 / self.levels[i - 1][4], 1.0 / self.levels[i - 1][5]))
            a.use(0)
            self.draw('blur.frag', fb, uSrc=0, uDir=(1.0 / w, 0.0))
            b.use(0)
            self.draw('blur.frag', fa, uSrc=0, uDir=(0.0, 1.0 / h))
        # god rays from level0 bright
        if P.get('rays', 0.0) > 0.0:
            self.levels[0][0].use(0)
            self.draw('rays.frag', self.fb_rays, uSrc=0, uCenter=P.get('rayCenter', (0.5, 0.5)),
                      uDecay=P.get('rayDecay', 0.965), uLen=P.get('rayLen', 0.85))
        else:
            self.fb_rays.use()
            ctx.clear(0, 0, 0, 0)
        # composite
        src_tex.use(0)
        for i in range(5):
            self.levels[i][0].use(1 + i)
        self.rays.use(6)
        if overlay is not None:
            self.overlay.write(overlay)
            self.overlay.use(7)
        u = dict(uSrc=0, uB0=1, uB1=2, uB2=3, uB3=4, uB4=5, uRays=6, uOver=7,
                 uHasOver=1.0 if overlay is not None else 0.0,
                 uRes=(float(W), float(H)))
        for k, v in P.items():
            if k.startswith('u'):
                u[k] = v
        defaults = dict(uExposure=1.0, uBloom=0.6, uRaysAmt=0.0, uVignette=0.55, uGrain=0.022, uCA=0.0015,
                        uLetterbox=1.0, uFade=1.0, uFlash=0.0, uFlashCol=(1.0, 1.0, 1.0), uTint=(1.0, 1.0, 1.0),
                        uSat=1.0, uContrast=1.0, uLift=(0.0, 0.0, 0.0), uShake=(0.0, 0.0), uTime=0.0,
                        uBlur=0.0, uTiltShift=0.0, uFocusY=0.5)
        for k, v in defaults.items():
            u.setdefault(k, v)
        if P.get('rays', 0.0) > 0.0:
            u['uRaysAmt'] = P['rays']
        self.draw('composite.frag', self.fb_ldr, **u)
        data = self.fb_ldr.read(components=3, dtype='f1')
        img = np.frombuffer(data, dtype=np.uint8).reshape(H, W, 3)
        return img[::-1]
