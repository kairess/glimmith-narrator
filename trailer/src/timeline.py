"""The edit: voice placement, Korean subtitles, shots, cards and sync points."""
import json, os, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(HERE, 'align', 'words.json')))
FPS = 24


def sentences(k):
    ws = WORDS[k]['words']; out = []; cur = []
    for w in ws:
        cur.append(w)
        if re.search(r'[.?!]["”]?$', w['w'].strip()):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def word_time(k, word, nth=0):
    """source time (s) of the start of `word` in clip k"""
    hits = [w for w in WORDS[k]['words'] if w['w'].strip().strip('.,').lower() == word.lower()]
    return hits[nth]['s'], hits[nth]['e']


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_in(t): t = clamp(t); return t ** 3
def ease_io(t): t = clamp(t); return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
def seg(u, a, b): return clamp((u - a) / max(b - a, 1e-6))
def lerp2(a, b, t): return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))


VOICE = []   # dict(clip, sents, t, ko, [split])
SHOTS = []   # dict(t0, t1, fn)
CARDS = []   # dict(t0, dur, kind, text, ...)
CUES = {}    # named sync points for audio


def say(clip, sents, t, ko, split=None):
    """Place sentences `sents` of `clip` at timeline time t. Returns (t0, t1)."""
    ss = sentences(clip)
    s0 = ss[sents[0]][0]['s']
    s1 = ss[sents[-1]][-1]['e']
    ev = dict(clip=clip, sents=sents, src0=s0, src1=s1, t=t, ko=ko, split=split)
    VOICE.append(ev)
    return t, t + (s1 - s0)


def shot(t0, t1, fn, **kw):
    SHOTS.append(dict(t0=t0, t1=t1, fn=fn, **kw))


def card(t0, dur, text, **kw):
    CARDS.append(dict(t0=t0, dur=dur, text=text, **kw))


# ================================================================= scene parameter builders
# Each builder returns a function f(u, d, g) -> dict(scene=..., u={uniforms}, post={...})
# u: local time, d: shot duration, g: global time

def void_fn(beam=0.0, dust=0.6, beamX=0.0, tilt=0.15, bg=(0.004, 0.004, 0.006), beamCol=(1.0, 0.85, 0.65),
            glowR=0.0, glowCol=(0, 0, 0), post=None, fade_in=0.0):
    def f(u, d, g):
        b = beam * (ease(u / fade_in) if fade_in > 0 else 1.0)
        return dict(scene='void', u=dict(uBeam=b, uBeamX=beamX, uBeamTilt=tilt, uDust=dust, uBeamCol=beamCol,
                                         uBg=bg, uGlowR=glowR, uGlowCol=glowCol),
                    post=dict(post or {}))
    return f


def black_fn():
    def f(u, d, g):
        return dict(scene='black', u={}, post={})
    return f


GRADE = {
    'cold':   dict(uTint=(0.92, 0.97, 1.08), uSat=0.9, uContrast=1.05, uLift=(0.0, 0.004, 0.012)),
    'warm':   dict(uTint=(1.06, 1.0, 0.92), uSat=1.05, uContrast=1.05, uLift=(0.01, 0.005, 0.0)),
    'blood':  dict(uTint=(1.1, 0.9, 0.9), uSat=0.95, uContrast=1.12, uLift=(0.01, 0.0, 0.0)),
    'night':  dict(uTint=(0.95, 0.98, 1.06), uSat=1.0, uContrast=1.08, uLift=(0.0, 0.003, 0.01)),
    'ash':    dict(uTint=(1.02, 0.98, 0.94), uSat=0.72, uContrast=1.12, uLift=(0.004, 0.004, 0.006)),
    'hope':   dict(uTint=(1.05, 1.0, 0.95), uSat=1.1, uContrast=1.04, uLift=(0.008, 0.004, 0.0)),
    'moon':   dict(uTint=(0.92, 0.98, 1.08), uSat=0.85, uContrast=1.06, uLift=(0.0, 0.004, 0.012)),
}


def with_grade(p, name):
    q = dict(GRADE[name]); q.update(p); return q


# ================================================================= THE EDIT
def build():
    VOICE.clear(); SHOTS.clear(); CARDS.clear(); CUES.clear()

    # ------------------------------------------------------------ ACT 0: cold open
    CUES['drone_in'] = 0.0
    CUES['chime0'] = 1.3
    shot(0.0, 2.2, void_fn(beam=0.0, dust=0.35, post=with_grade({}, 'cold')))

    t = 3.0
    a0, a1 = say('N03', [0], t, '다른 것은 거의 남지 않았는데,\n왜 유리만 이렇게 많은지 궁금할지도 모르겠습니다.')
    b0, b1 = say('N03', [1, 2], a1 + 0.7, '깨뜨리기 쉬운 유리였다는 것만은, 제가 보장하지요.')
    c0, c1 = say('N03', [3], b1 + 0.6, '다만 그 안에 남은 것까지 없애기는… 어려웠습니다.')

    def frozen_a(u, d, g):
        k = u / d
        return dict(scene='shards', u=dict(tau=2.7, drift=1.0 + u * 0.35, camPos=(lerp(-0.25, 0.05, ease(k)), lerp(0.15, 0.0, ease(k))),
                                          camH=2.4, dolly=lerp(-0.6, 0.5, ease_io(k)), tilt=(lerp(-0.5, 0.3, k), 0.3), roll=lerp(0.06, -0.02, k),
                                          gain=lerp(0.35, 0.75, ease(k)), bg='void', beam=0.35, key=(-0.6, 0.8, 0.9), edge=0.6, glitter=0.5, spread=0.5),
                    post=with_grade(dict(uBloom=0.8, thresh=0.7, uFade=ease(u / 1.5)), 'cold'))
    shot(2.2, b0 - 0.35, frozen_a)

    def frozen_b(u, d, g):
        k = u / d
        glow = ease(seg(u, d - 4.0, d - 0.3))
        return dict(scene='shards', u=dict(tau=2.7, drift=3.5 + u * 0.3, camPos=(lerp(0.15, 0.3, k), lerp(0.0, -0.1, k)), camH=2.0,
                                          dolly=lerp(-0.3, 0.25, ease(k)), tilt=(lerp(0.5, 0.15, ease(k)), -0.25), roll=lerp(-0.08, 0.02, k),
                                          gain=0.6 + 1.4 * glow, bg='void', beam=0.2, key=(0.5, 0.7, 0.8), edge=0.6 + glow, glitter=0.7, spread=0.5),
                    post=with_grade(dict(uBloom=0.8 + glow, thresh=0.7, uTiltShift=0.35, uFocusY=0.5), 'cold'))
    shot(b0 - 0.35, c1 + 0.45, frozen_b)
    CUES['boom0'] = c1 + 0.45
    shot(c1 + 0.45, c1 + 1.6, black_fn())

    # ------------------------------------------------------------ ACT 1: welcome / wonder
    t = c1 + 1.6
    CUES['act1'] = t
    CUES['draw'] = t + 0.2
    w0, w1 = say('N01', [0], t + 0.9, '글리미스에 오신 것을 환영합니다, 장인.')
    e0, e1 = say('N01', [1], w1 + 0.55, '저는 창의 도안을 관리하는 엘리아스입니다.')
    fill_t = w1 + 0.1
    CUES['fill'] = fill_t

    def rose_draw(u, d, g, t0=t):
        gg = t0 + u
        shape = ease_io(seg(gg, t0 + 0.2, fill_t - 0.2))
        color = ease_io(seg(gg, fill_t, fill_t + 3.2))
        k = u / d
        return dict(scene='rose', u=dict(uShape=shape, uColor=color, uCamPos=(0.0, lerp(0.02, 0.0, k)), uCamH=lerp(3.3, 2.75, ease_out(k)),
                                        uCamRot=lerp(0.03, 0.0, k), uLight=lerp(0.55, 1.0, color), uLightPos=(0.25, 0.35), uMotes=0.3 * color),
                    post=with_grade(dict(uBloom=0.8, rays=0.25 + 0.3 * color, rayCenter=(0.5, 0.5), uFade=ease(u / 0.8)), 'warm'))
    shot(t, e1 + 0.9, rose_draw)

    t = e1 + 0.9
    card(t + 0.2, 3.6, '유리에 기억을 담던 왕국', style='card')
    shot(t, t + 4.0, void_fn(beam=0.8, dust=0.9, beamX=0.05, fade_in=0.6, post=with_grade({}, 'warm')))
    t += 4.0

    m0, m1 = say('N17', [0], t + 0.5, '처음 만든 기억 유리에는 곡조 하나, 혹은 얼굴 하나가 담겼습니다.')

    def rose_macro(u, d, g):
        k = u / d
        return dict(scene='rose', u=dict(uShape=1.2, uColor=1.2, uCamPos=lerp2((-0.55, 0.30), (-0.25, 0.42), ease_io(k)), uCamH=lerp(0.95, 0.75, k),
                                        uCamRot=lerp(-0.12, -0.05, k), uLight=1.1, uLightPos=(lerp(-0.6, -0.1, k), 0.5), uMotes=1.0, uVoice=1.0),
                    post=with_grade(dict(uBloom=0.9, uTiltShift=0.5, uFocusY=0.52, rays=0.2, rayCenter=(0.3, 0.8)), 'warm'))
    shot(t, m1 + 0.35, rose_macro)
    t = m1 + 0.35
    r0, r1 = say('N17', [1], t + 0.25, '나중에는 지붕에 내리는 빗소리까지,\n방 하나를 통째로 보존했지요.')
    CUES['rain'] = (t + 1.5, r1 + 0.8)

    def rose_rain(u, d, g):
        k = u / d
        return dict(scene='rose', u=dict(uShape=1.2, uColor=1.2, uCamPos=lerp2((0.62, -0.18), (0.50, -0.34), ease_io(k)), uCamH=lerp(0.7, 0.85, k),
                                        uCamRot=lerp(0.1, 0.16, k), uLight=0.85, uLightPos=(0.6, 0.0), uMotes=0.6, uRain=ease(seg(u, 1.0, 3.0)), uVoice=1.0),
                    post=with_grade(dict(uBloom=0.8, uTiltShift=0.4, uFocusY=0.45), 'cold'))
    shot(t, r1 + 0.7, rose_rain)
    t = r1 + 0.7

    p0, p1 = say('N04', [0], t + 0.7, '사람들은 천에 저녁거리를 싸 들고,\n해질녘 이곳에 올라왔습니다.')
    q0, q1 = say('N05', [0], p1 + 0.7, '마라에게는 이곳에 즐겨 앉는 벤치가 있었습니다.')

    def overlook(u, d, g, t0=t):
        k = u / d
        return dict(scene='city', sky='dusk',
                    u=dict(uCamPos=(lerp(-0.25, 0.15, ease_io(k)), 0.12), uCamH=lerp(1.95, 1.8, k), uLamps=lerp(0.05, 0.85, ease(seg(u, 1.0, d - 1.0))),
                           uFore=1.0, uBench=1.0, uFgOff=(lerp(0.15, 0.38, ease_io(k)), 0.0), uLinks=0.0, uSunPos=(-0.6, 0.02), uFog=0.6),
                    post=with_grade(dict(uBloom=0.75, thresh=0.8, rays=0.35, rayCenter=(0.3, 0.52), uFade=ease(u / 0.6)), 'warm'))
    shot(t, q1 + 1.2, overlook)
    t = q1 + 1.2

    l0, l1 = say('N21', [0], t + 0.8, '우리는 창들을 연결해, 기억을 서로 나누기 시작했습니다.')
    CUES['links'] = t + 0.4
    CUES['act1_peak'] = l1 + 0.3

    def links(u, d, g):
        k = u / d
        return dict(scene='city', sky='night',
                    u=dict(uCamPos=(lerp(0.2, 0.55, ease_io(k)), lerp(0.08, 0.16, k)), uCamH=lerp(1.85, 1.6, ease_io(k)), uLamps=0.9,
                           uLinks=ease_io(seg(u, 0.3, 5.0)), uFeat=1.0, uSunPos=(0.9, 0.3), uFog=0.5),
                    post=with_grade(dict(uBloom=0.9, thresh=0.75), 'night'))
    shot(t, l1 + 2.6, links)
    t = l1 + 2.6

    # ------------------------------------------------------------ ACT 2: the Bleeding
    CUES['act2'] = t
    s0_, s1_ = say('N24', [0], t + 0.8, '사람들이 배운 적 없는 노래를 기억하며,\n잠에서 깨기 시작했습니다.')

    def bleed_start(u, d, g):
        k = u / d
        return dict(scene='city', sky='night',
                    u=dict(uCamPos=(lerp(1.05, 1.2, k), lerp(0.18, 0.22, k)), uCamH=lerp(1.1, 0.95, ease(k)), uLamps=0.9, uLinks=1.0,
                           uBleed=0.35 * ease(seg(u, 1.0, d)), uSunPos=(0.9, 0.3), uFog=0.5),
                    post=with_grade(dict(uBloom=0.9, thresh=0.75), 'night'))
    shot(t, s1_ + 0.45, bleed_start)
    t = s1_ + 0.45
    h0, h1 = say('N24', [1], t + 0.2, '첫 보고서들은 새 항목 아래 정리했습니다. 이름하여, ‘스며듦’.')
    CUES['bleed_word'] = h0 + (word_time('N24', 'Bleeding')[0] - sentences('N24')[1][0]['s'])

    def rose_bleed(u, d, g):
        k = u / d
        return dict(scene='rose', u=dict(uShape=1.2, uColor=1.2, uBleed=lerp(0.1, 0.8, ease_in(k)), uCamPos=lerp2((0.1, 0.05), (0.0, 0.0), k), uCamH=lerp(1.4, 1.1, ease(k)),
                                        uLight=lerp(0.9, 0.6, k), uLightPos=(0.2, 0.3), uCamRot=lerp(0.0, 0.05, k)),
                    post=with_grade(dict(uBloom=0.9, uCA=0.002 + 0.004 * k), 'blood'))
    shot(t, h1 + 0.5, rose_bleed)
    t = h1 + 0.5
    card(t + 0.1, 3.2, '스 며 듦', style='chapter')
    CUES['chapter'] = t + 0.1
    shot(t, t + 3.4, void_fn(beam=0.0, dust=0.5, bg=(0.012, 0.0, 0.002), glowR=0.35, glowCol=(0.14, 0.0, 0.01), post=with_grade({}, 'blood')))
    t += 3.4

    CUES['heart'] = (t, None)
    n0, n1 = say('N22', [0], t + 0.5, '그러다 한 여인이 장터에서 돌아와,\n어릴 때 살던 집을 왜 허물었느냐고 물었습니다.')
    n2, n3 = say('N22', [1], n1 + 0.5, '집은, 그대로였습니다.')

    def city_bleed(u, d, g):
        k = u / d
        return dict(scene='city', sky='blood',
                    u=dict(uCamPos=(lerp(-0.6, -0.1, ease_io(k)), lerp(0.1, 0.14, k)), uCamH=lerp(1.6, 1.35, k), uLamps=0.8, uLinks=1.0,
                           uBleed=lerp(0.45, 0.8, k), uSunPos=(0.0, -0.1), uFog=0.6),
                    post=with_grade(dict(uBloom=0.9, thresh=0.75, uCA=0.003), 'blood'))
    shot(t, n3 + 0.55, city_bleed)
    t = n3 + 0.55
    o0, o1 = say('N26', [0], t + 0.25, '기억은 창 사이의 연결을 타고 이동하고 있었습니다.')

    def city_links_close(u, d, g):
        k = u / d
        return dict(scene='city', sky='blood',
                    u=dict(uCamPos=(lerp(0.75, 1.05, ease(k)), lerp(0.3, 0.26, k)), uCamH=lerp(0.62, 0.55, k), uLamps=0.7, uLinks=1.0,
                           uBleed=0.95, uSunPos=(0.0, -0.1), uFog=0.4),
                    post=with_grade(dict(uBloom=1.0, thresh=0.7, uCA=0.004, uTiltShift=0.6, uFocusY=0.55), 'blood'))
    shot(t, o1 + 0.4, city_links_close)
    t = o1 + 0.4
    x0, x1 = say('N34', [0], t + 0.3, '사람들은 자기 이름과 가족을 적은 수첩을\n들고 다니기 시작했습니다.')
    CUES['tick'] = (x0 - 0.2, x1 + 0.2)

    def rose_bleed2(u, d, g):
        k = u / d
        return dict(scene='rose', u=dict(uShape=1.2, uColor=1.2, uBleed=0.95, uCamPos=lerp2((-0.45, -0.52), (-0.3, -0.45), k), uCamH=lerp(0.8, 0.7, k),
                                        uLight=0.55, uLightPos=(-0.3, -0.3), uCamRot=lerp(-0.2, -0.26, k), uSat=0.8),
                    post=with_grade(dict(uBloom=0.9, uCA=0.005, uTiltShift=0.5, uFocusY=0.5), 'blood'))
    shot(t, x1 + 0.35, rose_bleed2)
    t = x1 + 0.35
    y0, y1 = say('N32', [0], t + 0.25, '친어머니가 찾아왔을 때, 그 남자는… 이름을 물었습니다.')

    def city_bleed2(u, d, g):
        k = u / d
        return dict(scene='city', sky='blood',
                    u=dict(uCamPos=(lerp(-1.9, -2.1, k), lerp(0.12, 0.1, k)), uCamH=lerp(1.0, 0.9, k), uLamps=0.6 + 0.3 * np.sin(g * 9.0), uLinks=1.0,
                           uBleed=1.0, uSunPos=(-1.5, -0.1), uFog=0.7),
                    post=with_grade(dict(uBloom=0.9, uCA=0.004, uSat=0.8), 'blood'))
    shot(t, y1 + 0.3, city_bleed2)
    t = y1 + 0.3
    # frantic montage into the riser
    CUES['riser'] = (t, t + 2.6)
    flashes = [('rose', 0.0), ('city', 0.45), ('rose', 0.8), ('city', 1.1), ('rose', 1.4), ('city', 1.65), ('rose', 1.85), ('city', 2.05),
               ('rose', 2.2), ('city', 2.33), ('rose', 2.45)]
    for i, (kind, dt) in enumerate(flashes):
        nxt = flashes[i + 1][1] if i + 1 < len(flashes) else 2.6
        if kind == 'rose':
            def fr(u, d, g, i=i):
                cp = [(0.2, 0.3), (-0.5, 0.1), (0.4, -0.5), (-0.2, -0.3), (0.0, 0.0), (0.6, 0.2)][i % 6]
                return dict(scene='rose', u=dict(uShape=1.2, uColor=1.2, uBleed=1.0, uCamPos=cp, uCamH=0.6 + 0.25 * (i % 3), uLight=0.8, uLightPos=(0.2, 0.2), uCamRot=0.3 * (i % 2 - 0.5)),
                            post=with_grade(dict(uBloom=1.0, uCA=0.008, uContrast=1.25), 'blood'))
            shot(t + dt, t + nxt, fr)
        else:
            def fc(u, d, g, i=i):
                cx = [-1.2, 0.6, 1.3, -0.3, 2.1, -2.4][i % 6]
                return dict(scene='city', sky='blood', u=dict(uCamPos=(cx, 0.15), uCamH=0.7 + 0.2 * (i % 2), uLamps=0.7, uLinks=1.0, uBleed=1.0, uFog=0.5),
                            post=with_grade(dict(uBloom=1.0, uCA=0.008, uContrast=1.25), 'blood'))
            shot(t + dt, t + nxt, fc)
    t += 2.6
    CUES['slam'] = t
    shot(t, t + 1.3, black_fn())
    t += 1.3

    # ------------------------------------------------------------ ACT 3: the Shattering
    CUES['act3'] = t
    z0, z1 = say('N49', [0], t + 0.35, '대파손은, 하룻밤 사이에 도시 전체에서 일어났습니다.')
    z2, z3 = say('N49', [2], z1 + 0.75, '사고는 아니었습니다.')
    CUES['braam1'] = z3 + 0.25

    def city_still(u, d, g):
        k = u / d
        return dict(scene='city', sky='night',
                    u=dict(uCamPos=(lerp(0.9, 1.15, k), lerp(0.14, 0.2, k)), uCamH=lerp(2.1, 1.7, ease(k)), uLamps=0.6, uLinks=1.0, uBleed=1.0,
                           uSunPos=(1.2, 0.3), uFog=0.7, uFeat=1.0),
                    post=with_grade(dict(uBloom=0.85, uFade=ease(u / 0.8)), 'night'))
    shot(t, z3 + 0.25, city_still)
    t = z3 + 0.25

    k0, k1 = say('N51', [1], t + 1.4, '예전에 고친 자리도, 가까이 가져가서는 안 되는 도구도\n모두 알고 있었지요.')
    k2, k3 = say('N51', [2], k1 + 0.6, '누군가 제게, 그 도구 하나를 건넸습니다.')

    def room(u, d, g):
        k = u / d
        return dict(scene='rose', u=dict(uShape=1.2, uColor=1.2, uBleed=0.55, uCamPos=lerp2((0.0, 0.1), (0.25, -0.2), ease_io(k)), uCamH=lerp(3.4, 2.0, ease_io(k)),
                                        uLight=0.45, uLightPos=(0.3, 0.4), uWall=1.0, uSat=0.9, uMotes=0.2),
                    post=with_grade(dict(uBloom=0.8, uVignette=0.8, rays=0.3, rayCenter=(0.5, 0.5), uFade=ease(u / 1.2)), 'night'))
    shot(t, k3 + 0.45, room)
    t = k3 + 0.45

    j0, j1 = say('N52', [0], t + 0.3, '저는 망치로 창을 깼습니다.')
    ss52 = sentences('N52')
    hit_t0 = j1 + 0.7
    i0, i1 = say('N52', [1], hit_t0, '처음엔 모서리에 금만 갔습니다.', split=('그래서, 한 번 더 내리쳐야 했지요.', word_time('N52', 'so')[0] - ss52[1][0]['s']))
    base = ss52[1][0]['s']
    HIT1 = hit_t0 + (word_time('N52', 'cracked')[0] - base) + 0.12
    HIT2 = i1 + 0.42
    CUES['hit1'] = HIT1
    CUES['hit2'] = HIT2

    def corner(u, d, g, t0=t):
        gg = t0 + u
        cr = 0.0 if gg < HIT1 else 0.10 + 0.20 * ease_out((gg - HIT1) / 0.30)
        k = u / d
        sh = 0.0
        return dict(scene='shards', u=dict(tau=0.0, crackR=cr, crackGlow=1.0 if gg >= HIT1 else 0.0, camPos=lerp2((0.3, -0.2), (0.42, -0.36), ease(k)),
                                          camH=lerp(1.4, 1.05, ease(k)), dolly=0.0, tilt=(0.0, 0.0), gain=0.55, bg='rose', hole=0.0, light=0.45, bleed=0.55,
                                          key=(0.3, 0.6, 1.0), edge=0.8, glitter=0.0),
                    post=with_grade(dict(uBloom=0.8, uVignette=0.8), 'night'))
    shot(t, HIT2, corner)
    t = HIT2
    CUES['shatter'] = t
    v0, v1 = say('N52', [2], t + 2.2, '그 순간은, 원치 않을 만큼 선명하게 기억납니다.')

    def explode(u, d, g):
        # time ramp: a fast first beat, then deep slow motion
        tau = 0.55 * ease_out(min(u / 0.35, 1.0)) + max(u - 0.35, 0.0) * 0.28
        k = u / d
        return dict(scene='shards', u=dict(tau=tau, camPos=lerp2((0.42, -0.36), (0.1, -0.1), ease_out(k)), camH=lerp(1.05, 2.4, ease_out(seg(u, 0, 1.4))),
                                          dolly=lerp(0.0, 0.55, ease_io(k)), tilt=(lerp(0.0, -0.3, k), lerp(0.0, 0.18, k)), roll=lerp(0.0, 0.08, k),
                                          gain=0.9, bg='rose', hole=1.0, holeBright=3.5 * np.exp(-u * 3.0) + 0.02, light=lerp(2.0, 0.6, ease_out(seg(u, 0, 1.2))),
                                          key=(0.4, 0.8, 0.9), edge=1.0, glitter=1.0,
                                          flash=max(0.0, 1.0 - u / 0.25) * 2.0, spread=0.85),
                    post=with_grade(dict(uBloom=1.1, thresh=0.8, rays=0.9 * np.exp(-u * 1.5), rayCenter=(0.5, 0.5), uFlash=max(0.0, 0.9 - u * 3.5),
                                         uShakeAmt=max(0.0, 1.0 - u * 1.5)), 'night'))
    shot(t, v1 + 0.9, explode)
    t = v1 + 0.9

    g0, g1 = say('N55', [0], t + 0.3, '저는 글리미스의 모든 작업실에 명령을 보냈습니다.')
    g2, g3 = say('N55', [1], g1 + 0.5, '아침이 오기 전에, 기억 유리를 전부 깨뜨리라고.')
    WAVE = g1 + 0.1
    CUES['wave'] = WAVE

    def city_wave(u, d, g, t0=t):
        gg = t0 + u
        k = u / d
        return dict(scene='city', sky='night',
                    u=dict(uCamPos=(lerp(1.0, 0.1, ease_io(k)), lerp(0.16, 0.12, k)), uCamH=lerp(1.35, 1.9, ease(k)), uLamps=0.75, uLinks=1.0, uBleed=1.0,
                           uShatter=(gg - WAVE) if gg >= WAVE else -1.0, uShatterX=1.25, uSunPos=(1.2, 0.3), uFog=0.6),
                    post=with_grade(dict(uBloom=1.0, thresh=0.75, uShakeAmt=0.35 if gg > WAVE else 0.0), 'night'))
    shot(t, g3 + 1.4, city_wave)
    t = g3 + 1.4
    CUES['cut_black'] = t
    f0, f1 = say('N55', [2], t + 1.1, '제가 내린 명령입니다, 장인.')
    shot(t, f1 + 2.2, void_fn(beam=0.0, dust=0.25))
    t = f1 + 2.2

    # ------------------------------------------------------------ ACT 4: aftermath
    CUES['act4'] = t
    a40, a41 = say('N60', [0], t + 1.0, '몇 주 동안, 비행선들이 사람들을 실어 날랐습니다.')

    def ships(u, d, g):
        k = u / d
        return dict(scene='city', sky='dawn',
                    u=dict(uCamPos=(lerp(0.0, 0.3, k), lerp(0.2, 0.28, k)), uCamH=1.9, uLamps=0.0, uBroken=1.0, uSmoke=0.7, uShips=3.0 + u * 1.2,
                           uSunPos=(0.9, 0.04), uFog=0.5, uFeat=1.0, uHaze=0.8),
                    post=with_grade(dict(uBloom=0.8, rays=0.4, rayCenter=(0.75, 0.5), uFade=ease(u / 1.2)), 'ash'))
    shot(t, a41 + 1.2, ships)
    t = a41 + 1.2
    b40, b41 = say('N59', [1], t + 0.6, '마라는 좋아하던 벤치를 기억하고는,\n누가 가져갔느냐고 물었지요.')
    b42, b43 = say('N59', [2], b41 + 0.55, '제가 답했을 때, 그녀는 저를 알아보지 못했습니다.')

    def empty_overlook(u, d, g):
        k = u / d
        return dict(scene='city', sky='grey',
                    u=dict(uCamPos=(lerp(-0.1, 0.02, k), lerp(0.12, 0.1, k)), uCamH=lerp(1.85, 1.62, ease_io(k)), uLamps=0.0, uBroken=1.0, uFore=1.0, uBench=0.0,
                           uFgOff=(lerp(0.3, 0.4, k), 0.0), uAsh=1.0,
                           uSunPos=(0.4, 0.1), uFog=0.6, uSmoke=0.3, uHaze=0.8),
                    post=with_grade(dict(uBloom=0.6), 'ash'))
    shot(t, b43 + 0.9, empty_overlook)
    t = b43 + 0.9
    c40, c41 = say('N62', [0], t + 0.5, '마지막 비행선에도 제 자리가 있었습니다.')
    c42, c43 = say('N62', [2], c41 + 0.6, '선장은 다음 배는 없다고 했지만,\n저는 남았습니다.')

    def last_ship(u, d, g):
        k = u / d
        return dict(scene='city', sky='dusk',
                    u=dict(uCamPos=(lerp(0.6, 0.8, k), lerp(0.18, 0.22, k)), uCamH=lerp(1.5, 1.35, k), uLamps=0.0, uBroken=1.0, uShips=14.0 + u * 1.0,
                           uArchive=1.0, uSunPos=(-0.8, 0.0), uFog=0.7, uSmoke=0.2),
                    post=with_grade(dict(uBloom=0.8, uSat=0.7), 'ash'))
    shot(t, c43 + 2.2, last_ship)
    t = c43 + 2.2

    # ------------------------------------------------------------ ACT 5: restoration & reveal
    CUES['act5'] = t
    card(t + 0.3, 3.4, '조각이 모이면, 기억이 돌아온다', style='card')
    shot(t, t + 3.8, void_fn(beam=0.7, dust=1.0, beamX=-0.05, fade_in=0.8, post=with_grade({}, 'hope')))
    t += 3.8
    r50, r51 = say('N66', [0], t + 0.4, '기억을 담는 형태는 지키고,\n기억이 빠져나가는 연결은 없앴습니다.')
    r52, r53 = say('N66', [1], r51 + 0.6, '그대가 써 온 도안이, 바로 그것입니다.')
    ASSEMBLED = r53 - 0.2
    CUES['assembled'] = ASSEMBLED

    def reassemble(u, d, g, t0=t):
        gg = t0 + u
        k = seg(gg, t0, ASSEMBLED)
        tau = 2.6 * (1.0 - ease_io(k))
        after = max(0.0, gg - ASSEMBLED)
        return dict(scene='shards', u=dict(tau=tau, drift=4.0 * (1 - k), camPos=lerp2((0.1, 0.05), (0.0, 0.0), ease(k)), camH=lerp(2.3, 2.45, ease(k)),
                                          dolly=lerp(-0.3, 0.0, ease_io(k)), tilt=(lerp(0.6, 0.0, ease_io(k)), lerp(0.35, 0.0, ease_io(k))), roll=lerp(-0.1, 0.0, ease(k)),
                                          gain=lerp(0.5, 1.0, k), bg='void' if k < 0.999 else 'rose', hole=0.0, light=1.0, key=(0.4, 0.8, 0.9),
                                          edge=0.9 * (1 - k), glitter=0.4 * (1 - k), flash=0.7 * np.exp(-after * 5.0) * (after > 0), spread=0.6, clean=1.0),
                    post=with_grade(dict(uBloom=0.9 + 0.35 * np.exp(-after * 3.0) * (after > 0), rays=0.3 + 0.35 * np.exp(-after * 2.0) * (after > 0), rayCenter=(0.5, 0.5)), 'hope'))
    shot(t, r53 + 1.3, reassemble)
    t = r53 + 1.3

    s50, s51 = say('N71', [0], t + 0.4, '그대가 둘러보는 글리미스는,\n그렇게 남은 기억으로 이루어져 있습니다.')
    CUES['ghost'] = t

    def ghost(u, d, g):
        k = u / d
        return dict(scene='city', sky='night',
                    u=dict(uCamPos=(lerp(-0.4, 0.9, ease_io(k)), lerp(0.12, 0.2, k)), uCamH=lerp(1.7, 1.4, k), uLamps=0.5, uGhost=ease(seg(u, 0.0, 2.5)),
                           uFeat=1.0, uSunPos=(0.9, 0.3), uFog=0.5, uLinks=0.0),
                    post=with_grade(dict(uBloom=1.0, thresh=0.7, uFade=ease(u / 0.8)), 'hope'))
    shot(t, s51 + 1.8, ghost)
    t = s51 + 1.8
    CUES['drop'] = t

    d50, d51 = say('N82', [0], t + 1.4, '저는 이곳에서 죽었습니다, 장인.')
    d52, d53 = say('N82', [1], d51 + 0.8, '그대가 따라온 목소리는,\n유리에 남은 엘리아스 비디무스입니다.')

    def garden_wide(u, d, g):
        k = u / d
        return dict(scene='garden', u=dict(uCamPos=(lerp(0.05, -0.02, k), lerp(0.0, -0.02, k)), uCamH=lerp(0.95, 0.82, ease(k)), uPane=1.0, uMist=1.0, uMoon=1.0,
                                          uFireflies=0.8, uTint=(1, 1, 1)),
                    post=with_grade(dict(uBloom=0.9, thresh=0.7, rays=0.45, rayCenter=(0.5 + (-0.5 - 0.0) / 0.9 * 1080 / 1920, 0.5 + 0.24 / 0.9), uFade=ease(u / 1.5)), 'moon'))
    shot(t, d53 + 0.8, garden_wide)
    t = d53 + 0.8
    e50, e51 = say('N83', [1], t + 0.35, '저는 마라의 웃음소리를 남기지 못했습니다.')
    e52, e53 = say('N83', [2], e51 + 0.55, '그것은 그대와 함께 있는 동안 돌아왔지요.')

    def garden_close(u, d, g):
        k = u / d
        return dict(scene='garden', u=dict(uCamPos=lerp2((-0.06, -0.12), (-0.075, -0.13), k), uCamH=lerp(0.34, 0.26, ease(k)), uPane=1.0, uMist=0.8, uMoon=1.0,
                                          uFireflies=1.0, uTint=(1, 1, 1)),
                    post=with_grade(dict(uBloom=1.0, thresh=0.6, uTiltShift=0.3, uFocusY=0.5), 'moon'))
    shot(t, e53 + 0.5, garden_close)
    t = e53 + 0.5
    CUES['swell'] = t
    f50, f51 = say('N83', [3], t + 0.4, '다시는 듣지 못할 줄 알았던 소리를,\n그대가 돌려주었습니다.')

    def bench_back(u, d, g):
        k = u / d
        return dict(scene='city', sky='dusk',
                    u=dict(uCamPos=(lerp(0.0, 0.2, ease_io(k)), 0.12), uCamH=lerp(1.75, 1.85, k), uLamps=0.9, uFore=1.0, uBench=1.0, uFgOff=(lerp(0.36, 0.28, ease_io(k)), 0.0),
                           uSunPos=(-0.6, 0.02), uFog=0.6, uLinks=0.0),
                    post=with_grade(dict(uBloom=0.9, rays=0.45, rayCenter=(0.3, 0.52), uFade=ease(u / 0.6)), 'hope'))
    shot(t, f51 + 1.6, bench_back)
    t = f51 + 1.6

    # ------------------------------------------------------------ TITLE
    CUES['title'] = t

    def title(u, d, g):
        return dict(scene='title', u=dict(uReveal=ease_out(seg(u, 0.1, 2.2)), uSweep=lerp(-0.4, 1.6, ease_io(seg(u, 1.6, 5.0))), uGlow=0.7, uBeam=1.0),
                    post=dict(uBloom=0.9, thresh=0.7, uFade=min(1.0, (d - u) / 1.0)))
    shot(t, t + 6.6, title)
    card(t + 1.8, 4.5, 'TALES OF GLIMMITH', style='subtitle_title')
    t += 6.6
    shot(t, t + 0.6, black_fn())
    t += 0.6

    # ------------------------------------------------------------ FINAL: the colours are yours
    CUES['final'] = t
    h50, h51 = say('N87', [0], t + 1.0, '형태는 우리의 것입니다, 장인.')
    h52, h53 = say('N87', [1], h51 + 0.45, '색은 그대의 것입니다.')
    FLOOD = h53 + 0.15
    CUES['flood'] = FLOOD
    END = FLOOD + 6.5

    def final(u, d, g, t0=t):
        gg = t0 + u
        color = ease_io(seg(gg, FLOOD, FLOOD + 3.4))
        k = u / d
        return dict(scene='rose', u=dict(uShape=1.2, uColor=color, uCamPos=(0.0, 0.0), uCamH=lerp(2.9, 2.6, ease(k)), uLight=lerp(1.1, 1.25, color),
                                        uLightPos=(0.25, 0.35), uMotes=0.5 + 0.5 * color, uSat=1.0),
                    post=with_grade(dict(uBloom=0.9 + 0.3 * color, rays=0.35 + 0.35 * color, rayCenter=(0.5, 0.5), uFade=min(ease(u / 1.2), clamp((END - gg) / 2.2))), 'hope'))
    shot(t, END, final)
    CUES['end'] = END
    return END


if __name__ == '__main__':
    end = build()
    for v in VOICE:
        print(f"{v['t']:7.2f}  {v['clip']}{v['sents']}  {v['src1'] - v['src0']:5.2f}s  {v['ko'].replace(chr(10), ' / ')}")
    print('shots', len(SHOTS), 'end', round(end, 2), f'= {int(end // 60)}:{end % 60:04.1f}')
    for k, v in CUES.items():
        print(k, v)
