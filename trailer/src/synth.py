"""Small numpy synthesis toolkit for the trailer score and sound design."""
import numpy as np
from scipy import signal

SR = 48000
RNG = np.random.default_rng(1234)


def n_of(d): return int(round(d * SR))
def tt(d): return np.arange(n_of(d), dtype=np.float32) / SR
def midi(m): return 440.0 * 2 ** ((m - 69) / 12.0)
def db(x): return 10 ** (x / 20.0)


NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def nm(s):
    """'A4' -> midi"""
    name = s[:-1]; octv = int(s[-1])
    return 12 * (octv + 1) + NOTE[name]


def hz(s): return midi(nm(s))


# ------------------------------------------------------------------ envelopes
def adsr(n, a, d, s, r, peak=1.0):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    e = np.full(n, s, dtype=np.float32)
    if a_n > 0:
        e[:min(a_n, n)] = np.linspace(0, peak, a_n, dtype=np.float32)[:min(a_n, n)]
    if d_n > 0 and a_n < n:
        seg = np.linspace(peak, s, d_n, dtype=np.float32)
        e[a_n:a_n + d_n] = seg[:max(0, min(d_n, n - a_n))]
    if r_n > 0:
        r_n = min(r_n, n)
        e[-r_n:] *= np.linspace(1, 0, r_n, dtype=np.float32) ** 1.5
    return e


def fade(x, fi=0.005, fo=0.02):
    x = x.copy()
    a, b = int(fi * SR), int(fo * SR)
    if a > 0: x[:a] *= np.linspace(0, 1, a)[:, None] if x.ndim == 2 else np.linspace(0, 1, a)
    if b > 0: x[-b:] *= np.linspace(1, 0, b)[:, None] if x.ndim == 2 else np.linspace(1, 0, b)
    return x


# ------------------------------------------------------------------ oscillators
def _polyblep(t, dt):
    y = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    y[m] = x + x - x * x - 1.0
    m2 = t > 1.0 - dt
    x = (t[m2] - 1.0) / dt[m2]
    y[m2] = x * x + x + x + 1.0
    return y


def saw(freq, n, phase0=None):
    freq = np.broadcast_to(np.asarray(freq, dtype=np.float64), (n,))
    dt = freq / SR
    ph = (np.cumsum(dt) + (RNG.uniform() if phase0 is None else phase0)) % 1.0
    return (2 * ph - 1 - _polyblep(ph, dt)).astype(np.float32)


def sine(freq, n, phase0=0.0):
    freq = np.broadcast_to(np.asarray(freq, dtype=np.float64), (n,))
    ph = np.cumsum(freq / SR) + phase0
    return np.sin(2 * np.pi * ph).astype(np.float32)


def noise(n):
    return RNG.standard_normal(n).astype(np.float32)


# ------------------------------------------------------------------ filters
def lp(x, fc, order=2):
    sos = signal.butter(order, min(fc, SR * 0.45), 'low', fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=0).astype(np.float32)


def hp(x, fc, order=2):
    sos = signal.butter(order, fc, 'high', fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=0).astype(np.float32)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, min(hi, SR * 0.45)], 'band', fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=0).astype(np.float32)


def tv_filter(x, fc, kind='low', q=0.707, block=256):
    """Time-varying biquad (cutoff per block)."""
    fc = np.broadcast_to(np.asarray(fc, dtype=np.float64), (len(x),))
    y = np.zeros_like(x)
    z = np.zeros((1, 2))
    for i in range(0, len(x), block):
        f = float(np.clip(fc[i], 20, SR * 0.45))
        w0 = 2 * np.pi * f / SR
        al = np.sin(w0) / (2 * q)
        c = np.cos(w0)
        if kind == 'low':
            b = np.array([(1 - c) / 2, 1 - c, (1 - c) / 2])
        elif kind == 'high':
            b = np.array([(1 + c) / 2, -(1 + c), (1 + c) / 2])
        else:  # band (constant peak)
            b = np.array([al, 0.0, -al])
        a = np.array([1 + al, -2 * c, 1 - al])
        sos = np.concatenate([b / a[0], a / a[0]])[None, :]
        seg, z = signal.sosfilt(sos, x[i:i + block], zi=z)
        y[i:i + block] = seg
    return y.astype(np.float32)


def formant(x, freqs=(800, 1150, 2900), gains=(1.0, 0.5, 0.25), bw=(80, 90, 120)):
    out = np.zeros_like(x)
    for f, g, b in zip(freqs, gains, bw):
        out += g * bp(x, f - b, f + b, order=2)
    return out


# ------------------------------------------------------------------ stereo helpers
def pan(x, p=0.0):
    """equal-power pan, p in [-1,1]"""
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1).astype(np.float32)


def widen(xl, xr):
    return np.stack([xl, xr], axis=1).astype(np.float32)


# ------------------------------------------------------------------ reverb
def make_ir(dur=4.0, decay=2.2, damp=4000.0, predelay=0.02, seed=7, bright_tail=0.35):
    rng = np.random.default_rng(seed)
    n = n_of(dur)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2), dtype=np.float32)
    for ch in range(2):
        w = rng.standard_normal(n).astype(np.float32)
        dark = lp(w, damp * 0.35)
        bright = lp(w, damp)
        env = np.exp(-t * 6.9 / decay)
        env_b = np.exp(-t * 6.9 / (decay * bright_tail))
        ir[:, ch] = dark * env + bright * env_b * 0.6
    pd = n_of(predelay)
    ir = np.concatenate([np.zeros((pd, 2), np.float32), ir])
    ir /= np.sqrt((ir ** 2).sum(axis=0, keepdims=True))
    return ir


def convolve(x, ir):
    """x: (N,2) or (N,), ir: (M,2) -> (N,2) same length"""
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    out = np.zeros_like(x)
    for ch in range(2):
        out[:, ch] = signal.oaconvolve(x[:, ch], ir[:, ch])[:len(x)]
    return out


# ------------------------------------------------------------------ instruments
def supersaw(f, dur, voices=5, detune=0.12, cutoff=2500.0, a=1.0, r=1.5, vib=0.0, vib_rate=5.0, drift=True):
    n = n_of(dur)
    t = np.arange(n) / SR
    L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
    for v in range(voices):
        cents = (v - (voices - 1) / 2) / max((voices - 1) / 2, 1) * detune * 100 / 2
        ff = f * 2 ** (cents / 1200)
        if vib > 0:
            ff = ff * (1 + vib * np.sin(2 * np.pi * vib_rate * t + RNG.uniform(0, 6)))
        if drift:
            ff = ff * (1 + 0.0015 * np.sin(2 * np.pi * RNG.uniform(0.05, 0.2) * t + RNG.uniform(0, 6)))
        s = saw(ff, n)
        pv = (v / max(voices - 1, 1)) * 2 - 1
        L += s * np.cos((pv * 0.8 + 1) * np.pi / 4)
        R += s * np.sin((pv * 0.8 + 1) * np.pi / 4)
    L = lp(L, cutoff); R = lp(R, cutoff)
    e = adsr(n, a, 0.0, 1.0, r)
    return widen(L * e, R * e) / voices


def chord_pad(notes, dur, **kw):
    out = None
    for s in notes:
        x = supersaw(hz(s) if isinstance(s, str) else s, dur, **kw)
        out = x if out is None else out + x
    return out / np.sqrt(len(notes))


def choir(notes, dur, a=1.2, r=2.0, vowel='ah'):
    F = {'ah': ((750, 1150, 2800), (1.0, 0.55, 0.3)), 'oo': ((350, 800, 2600), (1.0, 0.35, 0.15)),
         'eh': ((550, 1800, 2600), (1.0, 0.45, 0.25))}[vowel]
    out = None
    for s in notes:
        f = hz(s) if isinstance(s, str) else s
        x = supersaw(f, dur, voices=7, detune=0.18, cutoff=5000, a=a, r=r, vib=0.004, vib_rate=5.2)
        y = np.stack([formant(x[:, 0], F[0], F[1]), formant(x[:, 1], F[0], F[1])], axis=1)
        br = hp(noise(len(x)), 3000) * 0.02 * adsr(len(x), a, 0, 1, r)
        y += np.stack([br, br], axis=1)
        out = y if out is None else out + y
    return out * 3.0 / np.sqrt(len(notes))


def bell(f, dur=4.0, vel=1.0, bright=1.0):
    """glass celesta / bell"""
    n = n_of(dur)
    t = np.arange(n) / SR
    parts = [(1.0, 1.0, 2.4), (2.0, 0.45 * bright, 1.2), (3.0, 0.18 * bright, 0.7), (4.16, 0.22 * bright, 0.45),
             (5.43, 0.12 * bright, 0.3), (6.8, 0.06 * bright, 0.2)]
    x = np.zeros(n, np.float32)
    for r, a, dcy in parts:
        ff = f * r
        if ff > SR * 0.45: continue
        x += a * np.sin(2 * np.pi * ff * t + RNG.uniform(0, 6)) * np.exp(-t / dcy)
    click = hp(noise(n_of(0.01)), 3000) * np.exp(-np.arange(n_of(0.01)) / (SR * 0.002)) * 0.3
    x[:len(click)] += click
    return (x * vel * 0.35).astype(np.float32)


def piano(f, dur=5.0, vel=0.8):
    """soft felt piano"""
    n = n_of(dur)
    t = np.arange(n) / SR
    B = 0.00035
    x = np.zeros(n, np.float32)
    cutoff_n = 3000 * (0.4 + vel)
    for k in range(1, 16):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > cutoff_n or fk > SR * 0.45: break
        amp = (1.0 / k ** 1.15) * np.exp(-fk / (1800 * (0.5 + vel)))
        dcy = 3.2 / (1 + 0.35 * k) * (440 / max(f, 60)) ** 0.25
        det = 1 + RNG.uniform(-0.0004, 0.0004)
        x += amp * (np.sin(2 * np.pi * fk * t) + 0.6 * np.sin(2 * np.pi * fk * det * t + 1.0)) * np.exp(-t / dcy)
    thump = lp(noise(n_of(0.03)), 900) * np.exp(-np.arange(n_of(0.03)) / (SR * 0.006)) * 0.25
    x[:len(thump)] += thump
    a = n_of(0.004)
    x[:a] *= np.linspace(0, 1, a)
    x *= np.exp(-np.maximum(t - dur + 0.5, 0) * 8)
    return (x * vel * 0.3).astype(np.float32)


def braam(root='D1', dur=5.0, gain=1.0, open_t=0.25):
    n = n_of(dur)
    t = np.arange(n) / SR
    f0 = hz(root)
    out = np.zeros(n, np.float32)
    bend = 1 - 0.06 * np.exp(-t / 0.08)
    for ratio, a in ((1, 1.0), (2, 0.8), (3, 0.5), (4, 0.35), (1.5 * 2, 0.3)):
        for det in (-0.15, 0.0, 0.17):
            out += a * saw(f0 * ratio * bend * 2 ** (det / 12), n)
    cut = 120 + 2200 * np.exp(-((t - open_t) / 0.9) ** 2) * (t > 0.02) + 500 * np.exp(-t / 1.5)
    y = tv_filter(out, cut, 'low', q=1.1)
    y = np.tanh(y * 0.6) * 1.2
    sub = np.sin(2 * np.pi * f0 * t) * 0.9
    env = np.minimum(t / 0.03, 1) * np.exp(-t / (dur * 0.45))
    y = (y * 0.55 + sub) * env
    return (y * gain * 0.45).astype(np.float32)


def boom(dur=4.0, f1=65, f2=26, gain=1.0):
    n = n_of(dur); t = np.arange(n) / SR
    f = f2 + (f1 - f2) * np.exp(-t / 0.35)
    x = sine(f, n) * np.exp(-t / 1.4)
    x += lp(noise(n), 200) * np.exp(-t / 0.25) * 0.5
    x += hp(noise(n), 1500) * np.exp(-t / 0.03) * 0.2
    return np.tanh(x * 1.5).astype(np.float32) * gain * 0.7


def taiko(gain=1.0, f1=140, f2=48):
    n = n_of(1.8); t = np.arange(n) / SR
    f = f2 + (f1 - f2) * np.exp(-t / 0.05)
    x = sine(f, n) * np.exp(-t / 0.45)
    x += bp(noise(n), 100, 900) * np.exp(-t / 0.05) * 0.6
    return np.tanh(x * 1.6).astype(np.float32) * gain * 0.6


def heartbeat(gain=1.0):
    n = n_of(0.9); t = np.arange(n) / SR
    def thump(t0, a):
        tt_ = np.maximum(t - t0, 0)
        return sine(40 + 30 * np.exp(-tt_ / 0.03), n) * np.exp(-tt_ / 0.09) * (t >= t0) * a
    x = thump(0.0, 1.0) + thump(0.24, 0.7)
    return lp(x, 180).astype(np.float32) * gain


def riser(dur=3.0, gain=1.0, f0=200, f1=3000):
    n = n_of(dur); t = np.arange(n) / SR
    k = t / dur
    fc = f0 * (f1 / f0) ** (k ** 1.5)
    x = tv_filter(noise(n), fc, 'band', q=2.0) * 3.0
    tone = sine(f0 * 0.5 * (f1 / f0 * 0.5) ** (k ** 2), n) * 0.25
    for det in (1.005, 0.995):
        tone += sine(f0 * 0.5 * det * (f1 / f0 * 0.5) ** (k ** 2), n) * 0.12
    env = k ** 2.2
    return ((x + tone) * env * gain * 0.5).astype(np.float32)


def reverse_swell(dur=2.5, gain=1.0, cutoff=5000):
    n = n_of(dur); t = np.arange(n) / SR
    x = lp(hp(noise(n), 400), cutoff) * np.exp(-t / (dur * 0.35))
    return (x[::-1] * gain * 0.4).astype(np.float32)


def whoosh(dur=1.2, gain=1.0, f0=300, f1=4000):
    n = n_of(dur); t = np.arange(n) / SR
    k = t / dur
    fc = f0 * (f1 / f0) ** np.sin(k * np.pi / 2)
    x = tv_filter(noise(n), fc, 'band', q=1.4) * 2.0
    env = np.sin(np.pi * k) ** 2
    return (x * env * gain * 0.5).astype(np.float32)


def tinkles(dur=3.0, count=300, gain=1.0, density_decay=0.8, fmin=2000, fmax=9000, seed=5):
    rng = np.random.default_rng(seed)
    n = n_of(dur)
    out = np.zeros((n, 2), np.float32)
    times = rng.exponential(density_decay, count)
    times = times[times < dur - 0.3]
    for t0 in times:
        f = rng.uniform(fmin, fmax)
        d = rng.uniform(0.02, 0.35)
        m = n_of(d); tt_ = np.arange(m) / SR
        x = (np.sin(2 * np.pi * f * tt_) + 0.5 * np.sin(2 * np.pi * f * 2.76 * tt_)) * np.exp(-tt_ / (d * 0.3))
        a = rng.uniform(0.1, 1.0) * np.exp(-t0 / (dur * 0.6))
        i0 = n_of(t0)
        p = rng.uniform(-0.9, 0.9)
        seg = pan(x.astype(np.float32) * a, p)
        e = min(n, i0 + m)
        out[i0:e] += seg[:e - i0]
    return out * gain * 0.25


def shatter(gain=1.0, dur=4.0):
    n = n_of(dur); t = np.arange(n) / SR
    burst = hp(noise(n), 1800) * np.exp(-t / 0.18) * 0.8
    crunch = bp(noise(n), 300, 3000) * np.exp(-t / 0.07)
    low = sine(55 + 40 * np.exp(-t / 0.05), n) * np.exp(-t / 0.4) * 0.8
    mono = burst + crunch + low
    st = np.stack([mono, mono * 0.95], axis=1)
    st += tinkles(dur, 420, 1.3, 0.55)
    return (st * gain).astype(np.float32)


def crack(gain=1.0):
    n = n_of(0.6); t = np.arange(n) / SR
    x = hp(noise(n), 2500) * np.exp(-t / 0.012) * 1.2
    # crackle: sparse impulses
    imp = np.zeros(n, np.float32)
    idx = (RNG.exponential(0.03, 40).cumsum() * SR).astype(int)
    idx = idx[idx < n]
    imp[idx] = RNG.uniform(0.3, 1.0, len(idx)) * np.exp(-idx / (SR * 0.15))
    x += bp(imp, 2000, 9000) * 6.0
    x += sine(1800 + 900 * np.exp(-t / 0.01), n) * np.exp(-t / 0.05) * 0.3
    return (x * gain * 0.6).astype(np.float32)


def hammer(gain=1.0):
    n = n_of(1.2); t = np.arange(n) / SR
    thud = sine(70 + 60 * np.exp(-t / 0.02), n) * np.exp(-t / 0.12)
    knock = bp(noise(n), 250, 1400) * np.exp(-t / 0.025) * 1.2
    ring = (np.sin(2 * np.pi * 1870 * t) * 0.5 + np.sin(2 * np.pi * 2710 * t) * 0.35 + np.sin(2 * np.pi * 4230 * t) * 0.2) * np.exp(-t / 0.22)
    click = hp(noise(n), 4000) * np.exp(-t / 0.004)
    x = thud * 1.2 + knock + ring * 0.35 + click * 0.8
    return np.tanh(x * 1.3).astype(np.float32) * gain * 0.7


def wind(dur, gain=1.0, seed=3):
    rng = np.random.default_rng(seed)
    n = n_of(dur); t = np.arange(n) / SR
    w = rng.standard_normal(n).astype(np.float32)
    mod = 0.55 + 0.45 * np.sin(2 * np.pi * 0.07 * t + 1.0) * np.sin(2 * np.pi * 0.023 * t)
    fc = 350 + 500 * mod
    x = tv_filter(w, fc, 'low', q=0.9, block=1024) * mod
    y = tv_filter(rng.standard_normal(n).astype(np.float32), fc * 1.1, 'low', q=0.9, block=1024) * mod
    return widen(x, y) * gain * 0.35


def rain(dur, gain=1.0, seed=9):
    rng = np.random.default_rng(seed)
    n = n_of(dur)
    bed = hp(lp(rng.standard_normal((n, 2)).astype(np.float32), 7000), 700) * 0.25
    drops = np.zeros((n, 2), np.float32)
    for _ in range(int(dur * 70)):
        i0 = rng.integers(0, max(1, n - 3000))
        f = rng.uniform(1500, 5000)
        m = n_of(rng.uniform(0.005, 0.03))
        tt_ = np.arange(m) / SR
        x = np.sin(2 * np.pi * f * tt_ * (1 + 3 * tt_)) * np.exp(-tt_ / 0.004)
        drops[i0:i0 + m] += pan(x.astype(np.float32) * rng.uniform(0.05, 0.3), rng.uniform(-1, 1))
    return (bed + drops) * gain


def tick(gain=1.0, f=3200):
    n = n_of(0.08); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006) + hp(noise(n), 5000) * np.exp(-t / 0.002) * 0.4
    return (x * gain * 0.4).astype(np.float32)


def drone(dur, notes=('D2', 'A2'), gain=1.0, cutoff=600, seed=0):
    n = n_of(dur); t = np.arange(n) / SR
    out = np.zeros((n, 2), np.float32)
    for s in notes:
        f = hz(s)
        for ch in range(2):
            ff = f * (1 + 0.003 * np.sin(2 * np.pi * (0.05 + 0.03 * ch) * t + ch))
            x = saw(ff, n) * 0.5 + sine(ff * 0.5, n) * 0.5
            out[:, ch] += lp(x, cutoff)
    mod = 0.8 + 0.2 * np.sin(2 * np.pi * 0.09 * t)
    return out * mod[:, None] * gain * 0.25 / len(notes)
