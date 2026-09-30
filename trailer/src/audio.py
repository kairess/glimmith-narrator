"""Score, sound design and final mix for the trailer."""
import os, subprocess, json
import numpy as np
from scipy.io import wavfile
from scipy import signal

import synth as S
from synth import SR, hz, n_of
import timeline as TL

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')
VOICES = os.path.join(HERE, '..', '..', 'voices')
os.makedirs(BUILD, exist_ok=True)


class Bus:
    def __init__(self, dur):
        self.x = np.zeros((n_of(dur) + SR, 2), np.float32)

    def add(self, sig, t, gain=1.0, p=0.0):
        if sig.ndim == 1:
            sig = S.pan(sig, p)
        i0 = n_of(t)
        if i0 < 0:
            sig = sig[-i0:]; i0 = 0
        e = min(len(self.x), i0 + len(sig))
        if e > i0:
            self.x[i0:e] += sig[:e - i0] * gain


def peak_norm(x, target=1.0):
    m = np.abs(x).max()
    return x * (target / m) if m > 0 else x


# ------------------------------------------------------------------ voice
_clip_cache = {}
LINE_GAIN = {'N22[1]': 1.6, 'N55[2]': 1.15, 'N49[2]': 1.1}


def load_clip(k):
    if k not in _clip_cache:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(VOICES, k + '.mp3'), '-ac', '1', '-ar', str(SR),
                              '-f', 'f32le', '-'], capture_output=True, check=True).stdout
        _clip_cache[k] = np.frombuffer(raw, dtype=np.float32).copy()
    return _clip_cache[k]


def refine(x, s0, s1, nxt=None):
    """Trim to real speech onset/offset near whisper times using short-time energy."""
    hop = int(0.005 * SR)
    fr = np.sqrt(np.convolve(x ** 2, np.ones(hop * 4) / (hop * 4), mode='same') + 1e-12)
    thr = max(fr.max() * 0.02, 1e-4)
    a = max(0, n_of(s0 - 0.15))
    b = min(len(x), n_of(s0 + 0.25))
    idx = np.where(fr[a:b] > thr)[0]
    on = a + (idx[0] if len(idx) else n_of(0.15))
    on = max(0, on - n_of(0.035))
    lim = len(x) if nxt is None else min(len(x), n_of(nxt - 0.03))
    c = n_of(s1 - 0.1)
    d = min(lim, n_of(s1 + 0.45))
    idx = np.where(fr[c:d] > thr)[0]
    off = c + (idx[-1] if len(idx) else n_of(0.1)) + n_of(0.09)
    off = min(off, lim)
    return on, off


def voice_track(dur):
    bus = Bus(dur)
    env = np.zeros(len(bus.x), np.float32)
    placed = []
    for v in TL.VOICE:
        x = load_clip(v['clip'])
        ss = TL.sentences(v['clip'])
        last = v['sents'][-1]
        nxt = ss[last + 1][0]['s'] if last + 1 < len(ss) else None
        on, off = refine(x, v['src0'], v['src1'], nxt)
        seg = x[on:off].copy()
        seg = S.fade(seg, 0.012, 0.06)
        # align: src0 lands on v['t']
        t_start = v['t'] + (on / SR - v['src0'])
        bus.add(seg, t_start, LINE_GAIN.get(v['clip'] + str(v['sents']), 1.0))
        placed.append((t_start, t_start + len(seg) / SR))
    y = bus.x[:, 0]
    y = S.hp(y, 75)
    # presence + a touch of warmth
    y = y + 0.25 * S.bp(y, 2500, 5000) + 0.15 * S.lp(y, 250)
    # gentle compression (RMS follower)
    rms = np.sqrt(signal.lfilter([0.002], [1, -0.998], y ** 2) + 1e-9)
    thr = 0.08
    gain = np.where(rms > thr, (thr / rms) ** (1 - 1 / 2.5), 1.0).astype(np.float32)
    y = y * gain
    y = peak_norm(y, 0.62)
    env = signal.lfilter([0.01], [1, -0.99], np.abs(y))
    env = env / (env.max() + 1e-9)
    return np.stack([y, y], axis=1).astype(np.float32), env.astype(np.float32), placed


# ------------------------------------------------------------------ score
def score(dur):
    C = TL.CUES
    M = Bus(dur)      # music (ducked under voice)
    X = Bus(dur)      # sound design / impacts (not ducked much)
    A = Bus(dur)      # ambience (ducked)

    def bells(notes, t0, step, vel=0.8, gain=1.0, p0=-0.3, p1=0.3, dur_=4.0):
        for i, s in enumerate(notes):
            if s is None: continue
            p = p0 + (p1 - p0) * (i / max(len(notes) - 1, 1))
            M.add(S.bell(hz(s), dur_, vel), t0 + i * step, gain, p)

    def piano_notes(notes, t0, step, vel=0.6, gain=1.0, dur_=5.0, p=0.0):
        for i, s in enumerate(notes):
            if s is None: continue
            if isinstance(s, (list, tuple)):
                for q in s:
                    M.add(S.piano(hz(q), dur_, vel), t0 + i * step, gain, p)
            else:
                M.add(S.piano(hz(s), dur_, vel), t0 + i * step, gain, p)

    def pad(notes, t0, d, gain=1.0, cutoff=1800, a=1.5, r=2.0):
        M.add(S.chord_pad(notes, d + r, cutoff=cutoff, a=a, r=r), t0, gain)

    def strings(notes, t0, d, gain=1.0, a=1.2, r=2.0, cutoff=3200):
        x = None
        for s in notes:
            y = S.supersaw(hz(s), d + r, voices=6, detune=0.1, cutoff=cutoff, a=a, r=r, vib=0.003, vib_rate=5.5)
            x = y if x is None else x + y
        M.add(x / np.sqrt(len(notes)), t0, gain)

    def choir(notes, t0, d, gain=1.0, a=1.2, r=2.5, vowel='ah'):
        M.add(S.choir(notes, d + r, a=a, r=r, vowel=vowel), t0, gain)

    # ============================================================ ACT 0: cold open
    b0 = C['boom0']
    M.add(S.fade(S.drone(b0 + 0.05, ('D1', 'A1', 'D2'), gain=1.0, cutoff=320), 3.0, 0.08), 0.0, 1.0)
    A.add(S.fade(S.wind(b0 + 0.1, 0.9), 2.0, 0.1), 0.0, 1.0)
    for t0, s, p in ((C['chime0'], 'A5', -0.3), (6.2, 'E6', 0.4), (10.7, 'D6', -0.5), (14.1, 'F5', 0.2), (15.6, 'A6', 0.5)):
        M.add(S.bell(hz(s), 6.0, 0.6), t0, 0.9, p)
    choir(['D5', 'A5'], 8.0, b0 - 8.0 - 0.1, gain=0.10, a=5.0, r=0.1, vowel='oo')
    X.add(S.reverse_swell(1.6, 1.0), b0 - 1.6, 0.9)
    X.add(S.boom(5.0, 70, 24), b0, 1.4)
    X.add(S.braam('D1', 4.0, 0.7), b0, 0.8)

    # ============================================================ ACT 1: welcome / wonder
    draw, fill = C['draw'], C['fill']
    X.add(S.riser(fill - draw, 0.8, 600, 7000), draw, 0.5)
    # sparkling arpeggio following the molten lines
    arp = ['D5', 'F5', 'A5', 'D6', 'E6', 'F6', 'A6', 'D7']
    bells(arp, draw + 0.2, (fill - draw - 0.3) / len(arp), vel=0.5, gain=0.55, p0=-0.6, p1=0.6, dur_=3.0)
    # colour bloom
    X.add(S.tinkles(3.0, 90, 0.8, 1.2, 3000, 9000, seed=21), fill, 0.5)
    M.add(S.piano(hz('D2'), 6.0, 0.7), fill, 1.0)
    bells(['A6', 'F6', 'D6', 'A5', 'F5', 'D5'], fill + 0.05, 0.12, vel=0.6, gain=0.5, p0=0.5, p1=-0.5)
    # theme progression: Dm(add9) - Bbmaj7 - F/A - Csus
    prog = [['D3', 'F3', 'A3', 'E4'], ['Bb2', 'D3', 'F3', 'A3'], ['A2', 'C3', 'F3', 'A3'], ['C3', 'F3', 'G3', 'C4']]
    arp_pat = {0: ['D4', 'A4', 'E5', 'F5'], 1: ['Bb3', 'F4', 'A4', 'D5'], 2: ['A3', 'F4', 'C5', 'F5'], 3: ['C4', 'G4', 'C5', 'F5']}
    chord_len = 3.75
    t = fill
    peak = C['act1_peak']
    k = 0
    while t < peak - 0.5:
        d = min(chord_len, peak + 1.5 - t)
        pad(prog[k % 4], t, d, gain=0.55, cutoff=1400 + 800 * min(1, (t - fill) / 30), a=1.2, r=1.8)
        # felt piano broken chord
        piano_notes(arp_pat[k % 4] * 2, t, chord_len / 8, vel=0.4, gain=0.42, dur_=3.0, p=0.1)
        M.add(S.piano(hz(prog[k % 4][0]) / 2, 5.0, 0.6), t, 0.7)
        t += chord_len; k += 1
    # leitmotif on the glass celesta during "Our first memory glass..."
    motif = ['A5', 'D6', 'E6', 'F6', 'E6', 'D6', 'C6', 'D6']
    bells(motif, C['act1'] + 12.2, 0.55, vel=0.7, gain=0.6, p0=-0.2, p1=0.2, dur_=4.0)
    # rain
    r0, r1 = C['rain']
    A.add(S.fade(S.rain(r1 - r0 + 1.0, 0.8), 1.5, 1.5), r0, 1.0)
    # links: swell to the first peak
    lk = C['links']
    strings(['D3', 'A3', 'F4', 'A4'], lk, peak - lk, gain=0.35, a=3.0, r=2.0)
    choir(['A3', 'D4', 'F4'], lk + 1.5, peak - lk - 1.5, gain=0.25, a=3.0, r=2.2)
    bells(motif, lk + 1.0, 0.45, vel=0.6, gain=0.55, dur_=3.0)
    for i in range(int((peak - lk) / 0.9375)):
        X.add(S.taiko(0.5 + 0.5 * i / 8), lk + 0.6 + i * 0.9375, 0.35)
    X.add(S.reverse_swell(2.0, 1.0, 7000), peak - 2.0, 0.5)
    X.add(S.boom(3.0, 60, 30), peak, 0.6)
    bells(['D6', 'A6', 'D7'], peak, 0.08, vel=0.7, gain=0.6)

    # ============================================================ ACT 2: the Bleeding
    a2 = C['act2']
    slam = C['slam']
    M.add(S.fade(S.drone(slam - a2, ('D1', 'Eb2'), gain=0.8, cutoff=380), 2.0, 0.03), a2, 1.0)
    # sick high cluster that wavers
    n = n_of(slam - a2)
    tt = np.arange(n) / SR
    cl = (np.sin(2 * np.pi * hz('D6') * tt) + np.sin(2 * np.pi * hz('Eb6') * tt * (1 + 0.002 * np.sin(tt * 0.7)))) * 0.03
    cl *= np.clip((tt - 1.0) / 6.0, 0, 1) * (0.6 + 0.4 * np.sin(tt * 1.3))
    M.add(S.fade(np.stack([cl, np.roll(cl, 300)], 1).astype(np.float32), 0.5, 0.03), a2, 1.0)
    bw = C['bleed_word']
    ch = C['chapter']
    X.add(S.reverse_swell(1.8, 1.0), ch - 1.8, 0.8)
    X.add(S.boom(4.0, 60, 25), ch, 1.2)
    X.add(S.braam('D1', 3.5, 0.9, open_t=0.15), ch, 0.9)
    X.add(S.tinkles(2.5, 60, 0.6, 0.8, 1500, 5000, seed=33), ch, 0.5)
    # heartbeat, accelerating
    h0 = C['heart'][0]
    t = h0
    while t < slam - 0.2:
        k = (t - h0) / (slam - h0)
        period = 1.05 - 0.5 * k
        X.add(S.heartbeat(0.7 + 0.6 * k), t, 0.75)
        t += period
    # dark ostinato
    t = h0 + 6.0
    while t < slam - 0.1:
        k = (t - h0) / (slam - h0)
        note = 'D2' if int((t - h0) / 0.3) % 4 != 3 else 'Eb2'
        s = S.supersaw(hz(note), 0.28, voices=3, cutoff=900 + 1400 * k, a=0.005, r=0.15)
        M.add(s, t, 0.22 + 0.3 * k)
        t += 0.3 - 0.08 * k
    # clock ticks with the notebooks line
    t0, t1 = C['tick']
    t = t0; i = 0
    while t < t1:
        X.add(S.tick(0.8, 3200 if i % 2 == 0 else 2600), t, 0.4, 0.3 if i % 2 else -0.3)
        t += 0.5; i += 1
    rs, re = C['riser']
    X.add(S.riser(re - rs + 0.8, 1.2, 150, 5000), rs - 0.8, 0.9)
    M.add(S.fade(S.chord_pad(['D4', 'Eb4', 'A4', 'Bb4'], re - rs + 0.8, cutoff=4000, a=2.0, r=0.02), 2.0, 0.01), rs - 0.8, 0.35)
    # stutter hits in the frantic montage
    for dt in (0.0, 0.45, 0.8, 1.1, 1.4, 1.65, 1.85, 2.05, 2.2, 2.33, 2.45):
        X.add(S.taiko(0.6), rs + dt, 0.4)
        X.add(S.whoosh(0.25, 0.8, 1000, 6000), rs + dt - 0.05, 0.25)
    X.add(S.hammer(1.0), slam, 0.6)

    # ============================================================ ACT 3: the Shattering
    a3 = C['act3']
    b1 = C['braam1']
    M.add(S.fade(S.drone(b1 - a3 + 0.1, ('D1', 'A1'), gain=0.7, cutoff=240), 1.5, 0.05), a3, 1.0)
    choir(['D4', 'Eb4'], a3 + 1.0, b1 - a3 - 1.0, gain=0.08, a=3.0, r=0.3, vowel='oo')
    X.add(S.reverse_swell(1.2, 1.0), b1 - 1.2, 0.7)
    X.add(S.braam('D1', 6.0, 1.3, 0.3), b1, 1.0)
    X.add(S.boom(5.0, 65, 24), b1, 1.2)
    h1, h2 = C['hit1'], C['hit2']
    # tension bed in the cleared room
    M.add(S.fade(S.drone(h2 - b1, ('D1', 'D2', 'Ab2'), gain=1.0, cutoff=380), 2.0, 0.05), b1 + 0.5, 1.0)
    t = b1 + 2.0; i = 0
    while t < h1 - 0.8:
        k = (t - b1) / (h1 - b1)
        note = ['D2', 'Eb2'][i % 2]
        M.add(S.supersaw(hz(note), 0.3, voices=3, cutoff=700 + 900 * k, a=0.01, r=0.2), t, 0.25 + 0.2 * k)
        t += 0.42; i += 1
    # high tremolo string swell toward the first blow
    n = n_of(h1 - b1 - 2.0)
    tt = np.arange(n) / SR
    trem = S.supersaw(hz('D5'), (h1 - b1 - 2.0), voices=4, cutoff=5000, a=4.0, r=0.02)
    trem *= (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 9 * tt)))[:, None]
    M.add(trem, b1 + 2.0, 0.16)
    # hammer blows
    X.add(S.hammer(1.3), h1, 1.0)
    X.add(S.crack(1.4), h1 + 0.02, 1.0)
    X.add(S.tinkles(1.2, 25, 0.5, 0.3, 2500, 8000, seed=41), h1 + 0.05, 0.5)
    X.add(S.reverse_swell(0.9, 1.0), h2 - 0.9, 0.9)
    X.add(S.hammer(1.5), h2, 1.1)
    X.add(S.shatter(1.0, 6.0), h2 + 0.01, 0.9)
    X.add(S.braam('D1', 7.0, 1.4, 0.2), h2, 1.1)
    X.add(S.boom(6.0, 70, 22), h2, 1.4)
    # slow-motion: tragic choir + strings
    wv = C['wave']
    sm = h2 + 0.4
    seq = [(['D3', 'A3', 'D4', 'F4'], 2.6), (['Bb2', 'F3', 'D4', 'F4'], 2.6), (['G2', 'D3', 'Bb3', 'G4'], 2.6), (['A2', 'E3', 'C#4', 'A4'], wv - sm - 7.8)]
    t = sm
    for notes, d in seq:
        choir(notes, t, d, gain=0.45, a=0.6, r=1.5)
        strings([n_ for n_ in notes], t, d, gain=0.28, a=0.5, r=1.5, cutoff=2600)
        t += d
    X.add(S.tinkles(8.0, 220, 0.8, 2.5, 1800, 7000, seed=51), h2 + 0.3, 0.4)
    # city-wide wave: staggered glass bursts + drums
    X.add(S.braam('D1', 5.0, 1.1), wv, 0.9)
    rng = np.random.default_rng(77)
    for i in range(18):
        tb = wv + 0.08 + rng.exponential(0.9)
        if tb > C['cut_black'] - 0.2: continue
        X.add(S.shatter(0.35 + 0.3 * rng.uniform(), 2.5), tb, 0.2, rng.uniform(-0.8, 0.8))
    for i in range(8):
        X.add(S.taiko(0.9), wv + i * 0.5, 0.38)
    choir(['D3', 'A3', 'D4', 'F4', 'A4'], wv, C['cut_black'] - wv, gain=0.5, a=0.3, r=0.05)
    strings(['D2', 'A2', 'D3'], wv, C['cut_black'] - wv, gain=0.4, a=0.3, r=0.05, cutoff=1500)
    cb = C['cut_black']
    X.add(S.boom(3.5, 55, 20), cb, 0.8)
    A.add(S.fade(S.wind(C['act4'] - cb + 1.0, 0.6, seed=8), 1.5, 1.0), cb + 0.3, 1.0)
    M.add(S.piano(hz('D1'), 7.0, 0.8), cb + 3.6, 0.9)

    # ============================================================ ACT 4: aftermath
    a4 = C['act4']
    a5 = C['act5']
    A.add(S.fade(S.wind(a5 - a4 + 1.0, 0.8, seed=12), 2.0, 2.0), a4, 1.0)
    # distant airship engines
    n = n_of(a5 - a4)
    tt = np.arange(n) / SR
    eng = S.lp(S.saw(52 * (1 + 0.01 * np.sin(tt * 0.4)), n), 160) * 0.5 + S.lp(S.noise(n), 120) * 0.2
    eng *= (0.5 + 0.5 * np.sin(2 * np.pi * 7.3 * tt) ** 2)
    A.add(S.fade(S.pan(eng.astype(np.float32), 0.3), 3.0, 3.0), a4, 0.35)
    # sparse felt piano: the motif, slowly, in D minor
    step = 1.25
    melody = ['A4', 'D5', 'E5', 'F5', None, 'E5', 'D5', 'C5', 'D5', None, None, 'A4', 'Bb4', 'A4', 'G4', 'F4', 'E4', None, 'D4']
    piano_notes(melody, a4 + 1.5, step, vel=0.5, gain=0.8, dur_=4.0, p=0.1)
    lh = [('D2', 'A2'), None, None, None, ('Bb1', 'F2'), None, None, None, ('G1', 'D2'), None, None, None, ('A1', 'E2'), None, None, None, ('D2', 'A2')]
    piano_notes(lh, a4 + 1.5, step, vel=0.45, gain=0.7, dur_=6.0, p=-0.1)
    for i, notes in enumerate([['D3', 'F3', 'A3'], ['Bb2', 'D3', 'F3'], ['G2', 'Bb2', 'D3'], ['A2', 'C#3', 'E3'], ['D3', 'F3', 'A3']]):
        pad(notes, a4 + 1.5 + i * step * 4, step * 4, gain=0.22, cutoff=900, a=2.0, r=2.5)

    # ============================================================ ACT 5: restoration & reveal
    X.add(S.whoosh(1.5, 0.8, 300, 5000), a5 - 0.2, 0.4)
    M.add(S.bell(hz('D6'), 6.0, 0.6), a5 + 0.3, 0.7)
    asm = C['assembled']
    re_start = a5 + 3.8
    # the shatter, reversed: glass flying back together
    rev = S.tinkles(asm - re_start, 380, 1.2, 1.4, 2000, 8500, seed=91)[::-1].copy()
    X.add(rev, re_start, 0.55)
    X.add(S.reverse_swell(asm - re_start, 1.0, 9000), re_start, 0.35)
    X.add(S.boom(4.0, 60, 30), asm, 0.8)
    bells(['D5', 'A5', 'D6', 'F6', 'A6'], asm, 0.06, vel=0.8, gain=0.7)
    # build: pulses + rising progression
    drop = C['drop']
    beat = 0.625
    prog5 = [['Bb2', 'F3', 'Bb3', 'D4'], ['F2', 'C3', 'F3', 'A3'], ['G2', 'D3', 'G3', 'Bb3'], ['C3', 'G3', 'C4', 'E4']]
    t = re_start; k = 0
    while t < drop - 0.1:
        d = min(beat * 8, drop - t)
        prog_notes = prog5[k % 4]
        lvl = min(1.0, (t - re_start) / (drop - re_start))
        pad(prog_notes, t, d, gain=0.35 + 0.25 * lvl, cutoff=1200 + 2200 * lvl, a=0.6, r=0.4 if t + d >= drop - 0.1 else 1.5)
        for j in range(int(d / (beat / 2))):
            nn = prog_notes[1 + (j % 3)]
            M.add(S.piano(hz(nn) * 2, 1.5, 0.35 + 0.3 * lvl), t + j * beat / 2, 0.26 + 0.2 * lvl)
        if lvl > 0.35:
            for j in range(int(d / beat)):
                X.add(S.taiko(0.4 + 0.6 * lvl), t + j * beat, 0.25 + 0.3 * lvl)
        t += d; k += 1
    gh = C['ghost']
    choir(['F3', 'A3', 'C4', 'F4'], gh, drop - gh - 0.1, gain=0.35, a=2.0, r=0.1)
    strings(['F4', 'A4', 'C5'], gh + 1.0, drop - gh - 1.1, gain=0.25, a=2.5, r=0.1)
    X.add(S.riser(2.5, 0.9, 400, 6000), drop - 2.5, 0.6)
    # the drop: silence, then wind and one high tone
    sw = C['swell']
    A.add(S.fade(S.wind(sw - drop + 8.0, 0.6, seed=19), 2.5, 3.0), drop + 0.2, 1.0)
    n = n_of(sw - drop - 1.0)
    tt = np.arange(n) / SR
    tone = np.sin(2 * np.pi * hz('A5') * tt * (1 + 0.002 * np.sin(2 * np.pi * 4.5 * tt))) * 0.04
    tone *= np.clip(tt / 4.0, 0, 1)
    M.add(S.fade(tone.astype(np.float32), 0.5, 1.5), drop + 1.0, 1.0)
    # piano returns for Mara's laugh
    e = TL.VOICE[[v['clip'] + str(v['sents']) for v in TL.VOICE].index('N83[1]')]['t']
    piano_notes(['D4', 'F4', 'A4', None, 'C5', 'Bb4', 'A4', None], e - 0.8, 0.9, vel=0.4, gain=0.7, dur_=4.0)
    piano_notes([('D2', 'A2'), None, None, None, ('Bb1', 'F2'), None, None, None], e - 0.8, 0.9, vel=0.4, gain=0.6, dur_=6.0)
    # the swell into the title: Bb - C - D major
    ti = C['title']
    seg_ = (ti - sw) / 3.0
    for i, notes in enumerate([['Bb2', 'F3', 'Bb3', 'D4', 'F4'], ['C3', 'G3', 'C4', 'E4', 'G4'], ['D3', 'A3', 'D4', 'F#4', 'A4']]):
        strings(notes, sw + i * seg_, seg_ + (0.3 if i < 2 else 0.0), gain=0.3 + 0.12 * i, a=1.0 if i == 0 else 0.3, r=0.6)
        choir(notes[1:], sw + i * seg_, seg_, gain=0.25 + 0.1 * i, a=1.0, r=0.6)
        M.add(S.piano(hz(notes[0]) / 2, 4.0, 0.7), sw + i * seg_, 0.9)
    bells(['A5', 'D6', 'E6', 'F#6', 'E6', 'D6', 'C#6', 'D6'], sw + 0.4, (ti - sw - 0.6) / 8, vel=0.7, gain=0.65)
    X.add(S.reverse_swell(2.2, 1.0, 8000), ti - 2.2, 0.8)

    # ============================================================ TITLE + FINAL
    X.add(S.braam('D1', 7.0, 1.5, 0.35), ti, 1.1)
    X.add(S.boom(6.0, 70, 22), ti, 1.3)
    choir(['D3', 'A3', 'D4', 'F#4', 'A4'], ti, 5.5, gain=0.55, a=0.2, r=3.0)
    strings(['D2', 'A2', 'D3', 'F#3', 'A3'], ti, 5.5, gain=0.45, a=0.2, r=3.0, cutoff=2400)
    bells(['D6', 'F#6', 'A6', 'D7'], ti + 0.05, 0.1, vel=0.8, gain=0.6)
    X.add(S.tinkles(4.0, 120, 0.6, 1.5, 3000, 9000, seed=101), ti + 1.6, 0.5)
    fin = C['final']
    fl = C['flood']
    end = C['end']
    pad(['D3', 'F#3', 'A3', 'E4'], fin + 0.3, end - fin, gain=0.3, cutoff=1300, a=3.0, r=3.0)
    X.add(S.riser(1.2, 0.6, 1000, 8000), fl - 1.1, 0.35)
    X.add(S.tinkles(3.5, 160, 0.9, 1.0, 3000, 9500, seed=121), fl, 0.6)
    bells(['A5', 'D6', 'E6', 'F#6', 'E6', 'D6', 'C#6', 'D6'], fl + 0.1, 0.42, vel=0.75, gain=0.7, dur_=6.0)
    strings(['D3', 'A3', 'D4', 'F#4', 'A4'], fl, end - fl + 0.5, gain=0.35, a=2.0, r=3.0)
    choir(['A3', 'D4', 'F#4'], fl + 0.5, end - fl, gain=0.22, a=2.5, r=3.0, vowel='oo')
    M.add(S.piano(hz('D2'), 8.0, 0.6), fl, 0.8)
    M.add(S.bell(hz('D7'), 8.0, 0.6), end - 2.6, 0.5)
    return M.x, X.x, A.x


def lufs_approx(x):
    """very rough K-weighted loudness for level sanity checks"""
    y = S.hp(x.mean(axis=1) if x.ndim == 2 else x, 100)
    return 10 * np.log10(np.mean(y ** 2) + 1e-12) - 0.691


def main():
    end = TL.build()
    dur = end + 1.5
    voice, venv, placed = voice_track(dur)
    music, sfx, amb = score(dur)
    N = len(voice)
    music, sfx, amb = music[:N], sfx[:N], amb[:N]
    # reverbs
    hall = S.make_ir(4.5, 3.2, 5000, 0.03, seed=3)
    room = S.make_ir(1.8, 1.0, 6000, 0.012, seed=5)
    music_w = music + S.convolve(music, hall) * 0.55
    sfx_w = sfx + S.convolve(sfx, hall) * 0.35
    voice_w = voice + S.convolve(voice, room) * 0.10 + S.convolve(voice, hall) * 0.05
    # ducking under the voice: gate from the placed lines, smoothed
    gate = np.zeros(N, np.float32)
    for t0, t1 in placed:
        gate[max(0, n_of(t0 - 0.12)):min(N, n_of(t1 + 0.15))] = 1.0
    att = 1 - np.exp(-1 / (0.08 * SR)); rel = 1 - np.exp(-1 / (0.35 * SR))
    # asymmetric smoothing: fast attack, slower release (run forward on the gate)
    from scipy.ndimage import maximum_filter1d
    g2 = maximum_filter1d(gate, size=n_of(0.12))
    duck_env = signal.lfilter([rel], [1, -(1 - rel)], g2).astype(np.float32)
    duck_env = np.maximum(duck_env, signal.lfilter([att], [1, -(1 - att)], gate))
    duck_env = np.clip(duck_env, 0, 1)
    dm = (1.0 - 0.68 * duck_env)[:, None]     # music / ambience: about -10 dB under speech
    ds = (1.0 - 0.45 * duck_env)[:, None]     # sound design
    mix = voice_w * 1.0 + music_w * 0.30 * dm + sfx_w * 0.42 * ds + amb * 0.32 * dm
    # master: gentle glue + limiter
    mix = S.hp(mix, 25)
    peak = np.abs(mix).max(axis=1)
    lim = 0.89
    r = np.minimum(1.0, lim / (peak + 1e-9))
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    L = int(0.02 * SR)
    g = uniform_filter1d(minimum_filter1d(r, 2 * L + 1), L + 1)
    mix = mix * g[:, None]
    mix = np.tanh(mix * 1.05) / np.tanh(1.05)
    wavfile.write(os.path.join(BUILD, 'mix_raw.wav'), SR, mix.astype(np.float32))
    np.save(os.path.join(BUILD, 'stem_voice.npy'), voice_w.mean(axis=1).astype(np.float32))
    np.save(os.path.join(BUILD, 'stem_bed.npy'), (music_w * 0.30 * dm + sfx_w * 0.42 * ds + amb * 0.32 * dm).mean(axis=1).astype(np.float32))
    # stems for sanity
    for name, arr in (('voice', voice_w), ('music', music_w * 0.30 * dm), ('sfx', sfx_w * 0.42 * ds), ('amb', amb * 0.32 * dm)):
        print(f'{name:6s} approx loudness {lufs_approx(arr):6.1f} dB  peak {np.abs(arr).max():.2f}')
    # voice envelope per video frame (for the glass glow)
    fr = TL.FPS
    nf = int(np.ceil(end * fr)) + 2
    idx = (np.arange(nf) / fr * SR).astype(int)
    idx = np.clip(idx, 0, len(venv) - 1)
    ve = np.array([venv[max(0, i - 800):i + 800].mean() for i in idx])
    ve = np.clip(ve / (np.percentile(ve[ve > 0.01], 95) if (ve > 0.01).any() else 1.0), 0, 1)
    np.save(os.path.join(BUILD, 'voice_env.npy'), ve.astype(np.float32))
    # loudness normalisation
    out = os.path.join(BUILD, 'mix.wav')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(BUILD, 'mix_raw.wav'), '-af',
                    'loudnorm=I=-15:TP=-1.2:LRA=14:linear=true', '-ar', str(SR), '-c:a', 'pcm_s24le', out], check=True)
    print('wrote', out, 'duration', N / SR)
    json.dump(placed, open(os.path.join(BUILD, 'voice_placed.json'), 'w'))


if __name__ == '__main__':
    main()
