"""Render the trailer frames from the timeline."""
import os, sys, subprocess, time, argparse
import numpy as np
import moderngl
from PIL import Image

from engine import Engine
from shards import ShardRenderer, camera_for
from scenes import city_uniforms, set_city_arrays
import timeline as TL
import typo

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')
os.makedirs(BUILD, exist_ok=True)

ROSE_DEFAULTS = dict(uHoleBright=1.0, uCamPos=(0.0, 0.0), uCamH=2.6, uCamRot=0.0, uShape=1.2, uColor=1.2, uBleed=0.0, uLight=1.0,
                     uLightPos=(0.25, 0.35), uVoice=0.0, uHole=0.0, uTexMode=0.0, uWall=1.0, uSat=1.0, uDim=0.0,
                     uMotes=0.0, uRain=0.0)
POST_DEFAULTS = dict(thresh=0.9, uBloom=0.7, rays=0.0)


def vnoise1(x, seed=0.0):
    i = np.floor(x); f = x - i
    def h(n): return (np.sin(n * 127.1 + seed * 311.7) * 43758.5453) % 1.0
    u = f * f * (3 - 2 * f)
    return (h(i) * (1 - u) + h(i + 1) * u) * 2 - 1


class Renderer:
    def __init__(self):
        self.E = Engine()
        E = self.E
        self.W, self.H = E.W, E.H
        self.S = ShardRenderer(E.ctx)
        bake = dict(ROSE_DEFAULTS, uTime=3.0, uT=3.0, uShape=1.2, uColor=1.2, uLight=1.0, uMotes=0.0)
        self.S.bake_window(E, 'clean', **dict(bake, uBleed=0.0))
        self.S.bake_window(E, 'tainted', **dict(bake, uBleed=0.55, uTime=12.0))
        tree = typo.make_tree()
        self.tree = E.ctx.texture(tree.size, 4, np.asarray(tree).tobytes())
        self.tree.build_mipmaps(); self.tree.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        m = typo.title_mask('글리미스 이야기')
        self.title = E.ctx.texture((self.W, self.H), 4, m.tobytes())
        self.title.filter = (moderngl.LINEAR, moderngl.LINEAR)
        p, _ = E.prog('scene_city.frag')
        set_city_arrays(p)
        self.voice_env = None
        env_path = os.path.join(BUILD, 'voice_env.npy')
        if os.path.exists(env_path):
            self.voice_env = np.load(env_path)

    def venv(self, gt):
        if self.voice_env is None:
            return 0.0
        i = int(gt * TL.FPS)
        return float(self.voice_env[min(max(i, 0), len(self.voice_env) - 1)])

    # ------------------------------------------------------------ scenes
    def draw_scene(self, spec, gt):
        E = self.E
        W, H = self.W, self.H
        res = (float(W), float(H))
        sc = spec['scene']
        u = spec.get('u', {})
        if sc == 'black':
            E.fb_hdr.use(); E.fb_hdr.clear(0, 0, 0, 1)
        elif sc == 'void':
            E.draw('scene_void.frag', E.fb_hdr, uRes=res, uTime=gt, uT=gt, **u)
        elif sc == 'rose':
            uu = dict(ROSE_DEFAULTS); uu.update(u)
            if 'uVoice' in u:
                uu['uVoice'] = u['uVoice'] * self.venv(gt)
            E.draw('scene_rose.frag', E.fb_hdr, uRes=res, uTime=gt, uT=gt, uPxWorld=uu['uCamH'] / H, **uu)
        elif sc == 'city':
            uu = city_uniforms(spec.get('sky', 'dusk'), **u)
            uu['uVoice'] = self.venv(gt) * 0.6
            E.draw('scene_city.frag', E.fb_hdr, uRes=res, uTime=gt, uT=gt, **uu)
        elif sc == 'garden':
            self.tree.use(1)
            E.draw('scene_garden.frag', E.fb_hdr, uRes=res, uTime=gt, uT=gt, uTree=1, uVoice=self.venv(gt), **u)
        elif sc == 'title':
            self.title.use(1)
            E.draw('scene_title.frag', E.fb_hdr, uRes=res, uTime=gt, uT=gt, uMask=1, **u)
        elif sc == 'shards':
            camPos, camH = u['camPos'], u['camH']
            if u.get('bg') == 'rose':
                rr = dict(ROSE_DEFAULTS, uCamPos=camPos, uCamH=camH, uHole=u.get('hole', 0.0), uLight=u.get('light', 1.0),
                          uBleed=u.get('bleed', 0.55), uWall=1.0, uHoleBright=u.get('holeBright', 1.0))
                E.draw('scene_rose.frag', E.fb_hdr, uRes=res, uTime=gt, uT=gt, uPxWorld=camH / H, **rr)
            else:
                E.draw('scene_void.frag', E.fb_hdr, uRes=res, uTime=gt, uT=gt, uBeam=u.get('beam', 0.3), uBeamX=0.2, uBeamTilt=0.25,
                       uDust=0.5, uBeamCol=(0.8, 0.85, 1.0), uBg=(0.003, 0.003, 0.005), uGlowR=0.0, uGlowCol=(0, 0, 0))
            VP, eye = camera_for(camPos, camH, W / H, tilt=u.get('tilt', (0, 0)), dolly=u.get('dolly', 0.0), roll=u.get('roll', 0.0))
            win = 'clean' if (u.get('clean', 0) or u.get('bg') != 'rose') else 'tainted'
            self.S.draw(E.fb_hdr, VP, eye, u['tau'], drift=u.get('drift', 0.0), crackR=u.get('crackR', 0.0),
                        crackGlow=u.get('crackGlow', 0.0), gain=u.get('gain', 1.0), key=u.get('key', (0.3, 0.6, 1.0)),
                        edgeGlow=u.get('edge', 0.8), flash=u.get('flash', 0.0), glitter=u.get('glitter', 1.0),
                        spread=u.get('spread', 1.0), H=H, win=win)
        else:
            raise ValueError(sc)

    # ------------------------------------------------------------ overlays
    def overlay(self, gt):
        # cache: subtitles are static between fades, so most frames reuse the previous overlay
        key = []
        for v in TL.VOICE:
            t0 = v['t'] - 0.08
            t1 = v['t'] + (v['src1'] - v['src0']) + 0.3
            if t0 <= gt <= t1:
                a = min(1.0, (gt - t0) / 0.12, (t1 - gt) / 0.18)
                sp = bool(v.get('split')) and gt >= v['t'] + v['split'][1] - 0.05
                key.append((id(v), sp, round(a * 16)))
        for c in TL.CARDS:
            if 0 <= gt - c['t0'] <= c['dur']:
                key.append((id(c), round(gt * TL.FPS)))
        key = tuple(key)
        if getattr(self, '_ov_key', None) == key:
            return self._ov_val
        val = self._overlay(gt)
        self._ov_key, self._ov_val = key, val
        return val

    def _overlay(self, gt):
        ov = typo.Overlay()
        # subtitles
        for v in TL.VOICE:
            t0 = v['t'] - 0.08
            t1 = v['t'] + (v['src1'] - v['src0']) + 0.3
            if t0 <= gt <= t1:
                text = v['ko']
                if v.get('split'):
                    text2, at = v['split']
                    if gt >= v['t'] + at - 0.05:
                        text = text2
                a = min(1.0, (gt - t0) / 0.12, (t1 - gt) / 0.18)
                typo.draw_subtitle(ov, text, max(0.0, a))
        # cards
        for c in TL.CARDS:
            lt = gt - c['t0']
            if 0 <= lt <= c['dur']:
                st = c.get('style', 'card')
                if st == 'card':
                    typo.draw_card(ov, c['text'], lt, c['dur'], size=60, weight=400, track0=0.16, track1=0.26)
                elif st == 'chapter':
                    typo.draw_card(ov, c['text'], lt, c['dur'], size=124, weight=700, color=(236, 44, 52), glow_col=(255, 30, 40),
                                   glow_amt=1.2, track0=0.28, track1=0.44, fade_in=0.35, fade_out=0.8)
                elif st == 'subtitle_title':
                    typo.draw_card(ov, c['text'], lt, c['dur'], size=44, weight=600, y=typo.H * 0.635, color=(245, 212, 150),
                                   glow_col=(255, 190, 110), glow_amt=0.5, track0=0.34, track1=0.44, fade_in=1.2, fade_out=1.0,
                                   fontname='Cinzel.ttf')
        return ov.result()

    # ------------------------------------------------------------ frame
    def frame(self, gt):
        shot = None
        for s in TL.SHOTS:
            if s['t0'] <= gt < s['t1']:
                shot = s
        if shot is None:
            shot = TL.SHOTS[-1] if gt >= TL.SHOTS[-1]['t0'] else TL.SHOTS[0]
        u = gt - shot['t0']
        d = shot['t1'] - shot['t0']
        spec = shot['fn'](u, d, gt)
        self.draw_scene(spec, gt)
        P = dict(POST_DEFAULTS)
        P.update(spec.get('post', {}))
        # camera shake
        amt = P.pop('uShakeAmt', 0.0)
        hit_shake = 0.0
        for key in ('hit1', 'hit2', 'braam1', 'boom0'):
            ht = TL.CUES.get(key)
            if ht is not None and gt >= ht:
                hit_shake += (1.2 if key == 'hit2' else 0.6) * np.exp(-(gt - ht) * 6.0)
        amt += hit_shake
        if amt > 0:
            P['uShake'] = (float(vnoise1(gt * 28.0, 1.0) * 0.006 * amt), float(vnoise1(gt * 28.0, 7.0) * 0.006 * amt))
            P['uCA'] = P.get('uCA', 0.0015) + 0.004 * min(amt, 1.0)
        # a white pop on the first hammer blow
        h1 = TL.CUES.get('hit1')
        if h1 is not None and h1 <= gt < h1 + 0.25:
            P['uFlash'] = max(P.get('uFlash', 0.0), 0.35 * (1 - (gt - h1) / 0.25))
        P['uTime'] = gt
        return self.E.post(self.E.hdr, P, overlay=self.overlay(gt))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stills', type=str, default='')
    ap.add_argument('--start', type=float, default=0.0)
    ap.add_argument('--end', type=float, default=-1)
    ap.add_argument('--out', type=str, default=os.path.join(BUILD, 'video.mp4'))
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--preset', type=str, default='slow')
    ap.add_argument('--crf', type=str, default='18')
    a = ap.parse_args()
    end = TL.build()
    R = Renderer()
    if a.stills:
        os.makedirs(os.path.join(HERE, 'stills', 'tl'), exist_ok=True)
        for s in a.stills.split(','):
            t = float(s)
            img = R.frame(t)
            Image.fromarray(img).save(os.path.join(HERE, 'stills', 'tl', f't{t:07.2f}.png'))
        return
    t_end = end if a.end < 0 else a.end
    n0 = int(round(a.start * TL.FPS)); n1 = int(round(t_end * TL.FPS))
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{R.W}x{R.H}', '-r', str(TL.FPS),
           '-i', '-', '-c:v', 'libx264', '-preset', a.preset, '-crf', a.crf, '-tune', 'film', '-pix_fmt', 'yuv420p',
           '-x264-params', 'aq-mode=3', a.out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for n in range(n0, n1):
        gt = n / TL.FPS
        img = R.frame(gt)
        ff.stdin.write(img.tobytes())
        if n % 120 == 0:
            el = time.time() - t0
            done = n - n0 + 1
            print(f'frame {n}/{n1} t={gt:6.2f}s  {done / el:5.1f} fps', flush=True, file=sys.stderr)
    ff.stdin.close()
    ff.wait()
    print('done', time.time() - t0)


if __name__ == '__main__':
    main()
