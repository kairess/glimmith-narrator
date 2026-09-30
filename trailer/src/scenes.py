"""Scene uniform helpers shared by the stills tester and the full renderer."""
import numpy as np
from layout import city_layout

B, F, L = city_layout()

def _pack(rows, n, w=4):
    a = np.zeros((n, w), dtype='f4')
    for i, r in enumerate(rows[:n]):
        a[i, :len(r)] = r
    return a.tobytes()

CITY_B = _pack([b[:4] for b in B], 200)
CITY_B2 = _pack([b[4:] for b in B], 200)
CITY_F = _pack(F, 24)
CITY_L = _pack(L, 40)

SKIES = {
    'dusk':  dict(uSkyTop=(0.03, 0.04, 0.12), uSkyMid=(0.26, 0.12, 0.24), uSkyHor=(1.15, 0.50, 0.24), uSunCol=(1.0, 0.52, 0.22), uStars=0.3, uCloud=0.8),
    'night': dict(uSkyTop=(0.002, 0.003, 0.010), uSkyMid=(0.010, 0.016, 0.045), uSkyHor=(0.05, 0.055, 0.11), uSunCol=(0.12, 0.14, 0.26), uStars=1.0, uCloud=0.5),
    'blood': dict(uSkyTop=(0.008, 0.0, 0.006), uSkyMid=(0.08, 0.008, 0.014), uSkyHor=(0.24, 0.02, 0.03), uSunCol=(0.45, 0.04, 0.04), uStars=0.3, uCloud=0.8),
    'dawn':  dict(uSkyTop=(0.06, 0.08, 0.16), uSkyMid=(0.30, 0.28, 0.34), uSkyHor=(1.05, 0.62, 0.34), uSunCol=(1.0, 0.66, 0.36), uStars=0.0, uCloud=1.0),
    'grey':  dict(uSkyTop=(0.10, 0.11, 0.13), uSkyMid=(0.22, 0.23, 0.25), uSkyHor=(0.42, 0.41, 0.40), uSunCol=(0.3, 0.28, 0.25), uStars=0.0, uCloud=1.0),
}

def city_uniforms(sky='dusk', **kw):
    u = dict(uNB=len(B[:200]), uNF=len(F[:24]), uNL=len(L[:40]), uSunPos=(-0.6, 0.02),
             uLamps=1.0, uFeat=1.0, uLinks=0.0, uBleed=0.0, uShatter=-1.0, uShatterX=1.25, uShips=-1.0,
             uGhost=0.0, uBench=0.0, uFore=0.0, uFgOff=(0.0, 0.0), uFog=0.5, uHaze=1.0, uVoice=0.0, uBroken=0.0, uSmoke=0.0, uArchive=0.0, uArchivePos=(1.21, 0.17), uAsh=0.0)
    u.update(SKIES[sky])
    u.update(kw)
    return u

def set_city_arrays(prog):
    prog['uB'].write(CITY_B)
    prog['uB2'].write(CITY_B2)
    prog['uF'].write(CITY_F)
    prog['uL'].write(CITY_L)
