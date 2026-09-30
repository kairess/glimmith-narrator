import numpy as np, json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.io import wavfile
import timeline as TL
SR = 48000
TL.build()
v = np.load('build/stem_voice.npy'); b = np.load('build/stem_bed.npy')
placed = json.load(open('build/voice_placed.json'))
def db(x): return 10*np.log10(np.mean(x**2)+1e-12)
worst = []
for (t0,t1), ev in zip(placed, TL.VOICE):
    i0,i1 = int(t0*SR), int(t1*SR)
    dv, dbb = db(v[i0:i1]), db(b[i0:i1])
    worst.append((dv-dbb, ev['clip'], ev['sents'], round(t0,1), round(dv,1), round(dbb,1)))
for w in sorted(worst)[:12]: print('V/B %5.1f dB  %s%s @%s  voice %s bed %s' % w)
print('median V/B', np.median([w[0] for w in worst]))
# short-term loudness curves
sr, mix = wavfile.read('build/mix.wav')
mix = mix.astype(np.float32) / (2**31 if mix.dtype==np.int32 else 1)
m = mix.mean(axis=1)
win = int(0.4*SR); hop = int(0.1*SR)
def curve(x):
    n = (len(x)-win)//hop
    return np.array([10*np.log10(np.mean(x[i*hop:i*hop+win]**2)+1e-12) for i in range(n)])
cm, cv, cb = curve(m), curve(v), curve(b)
t = np.arange(len(cm))*hop/SR + 0.2
fig, ax = plt.subplots(2,1, figsize=(22,9))
ax[0].plot(t, cm, lw=0.8, label='final mix'); ax[0].plot(t[:len(cv)], cv[:len(t)], lw=0.6, label='voice'); ax[0].plot(t[:len(cb)], cb[:len(t)], lw=0.6, label='bed')
for k, val in TL.CUES.items():
    tv = val[0] if isinstance(val, tuple) else val
    ax[0].axvline(tv, color='gray', lw=0.4); ax[0].text(tv, -12, k, rotation=90, fontsize=7)
ax[0].set_ylim(-70, -5); ax[0].legend(); ax[0].set_xlim(0, t[-1])
ax[1].specgram(m, NFFT=2048, Fs=SR, noverlap=1024, cmap='magma', vmin=-120)
ax[1].set_ylim(0, 12000); ax[1].set_xlim(0, t[-1])
plt.tight_layout(); plt.savefig('stills/audio_analysis.png', dpi=80)
print('peak final', np.abs(mix).max(), 'rms', db(m))
