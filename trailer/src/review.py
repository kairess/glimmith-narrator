"""Sample frames from a rendered video into contact sheets + flag abrupt intra-shot changes."""
import sys, os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
import timeline as TL
TL.build()
vid = sys.argv[1]; step = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
out = 'stills/review'; os.makedirs(out, exist_ok=True)
for f in os.listdir(out): os.remove(os.path.join(out, f))
W, H = 480, 270
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', vid, '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
print('frames', len(fr))
cuts = sorted(set(round(s['t0'] * TL.FPS) for s in TL.SHOTS))
d = np.abs(fr[1:].astype(np.int16) - fr[:-1].astype(np.int16)).mean(axis=(1, 2, 3))
flag = []
for i, v in enumerate(d):
    n = i + 1
    if any(abs(n - c) <= 1 for c in cuts): continue
    if v > 18: flag.append((n / TL.FPS, float(v)))
print('abrupt intra-shot changes (t, mean abs diff):', [(round(a, 2), round(b, 1)) for a, b in flag[:40]])
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf', 16)
idx = [int(t * TL.FPS) for t in np.arange(0.5, len(fr) / TL.FPS, step)]
per = 24
for si in range(0, len(idx), per):
    chunk = idx[si:si + per]
    rows = (len(chunk) + 3) // 4
    sheet = Image.new('RGB', (4 * W, rows * H), (30, 30, 30))
    for j, n in enumerate(chunk):
        im = Image.fromarray(fr[n]); dr = ImageDraw.Draw(im); dr.text((5, 3), f'{n / TL.FPS:.1f}s', fill=(255, 255, 0), font=font)
        sheet.paste(im, ((j % 4) * W, (j // 4) * H))
    sheet.save(f'{out}/sheet_{si // per:02d}.png')
print('sheets', len(range(0, len(idx), per)))
