"""Typography: Korean subtitles, trailer cards and title masks (Pillow)."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', 'fonts')
W, H = 1920, 1080
BAR = int(round((H - W / 2.39) / 2))  # letterbox bar height

_font_cache = {}


def font(name, size, weight):
    key = (name, size, weight)
    if key not in _font_cache:
        f = ImageFont.truetype(os.path.join(FONTS, name), size)
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
        _font_cache[key] = f
    return _font_cache[key]


def text_layer(text, fnt, fill=(255, 255, 255), tracking=0.0):
    """Render a single line with custom letter spacing. Returns RGBA image tight-ish around the text."""
    asc, desc = fnt.getmetrics()
    widths = [fnt.getlength(ch) for ch in text]
    total = sum(widths) + tracking * fnt.size * max(len(text) - 1, 0)
    pad = int(fnt.size * 0.8)
    img = Image.new('RGBA', (int(total) + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = pad
    for ch, w in zip(text, widths):
        d.text((x, pad), ch, font=fnt, fill=fill + (255,))
        x += w + tracking * fnt.size
    return img


def glow(img, radius, strength=1.0, color=None):
    a = img.split()[3].filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        a = a.point(lambda v: min(255, int(v * strength)))
    c = color or (255, 220, 170)
    g = Image.new('RGBA', img.size, c + (0,))
    g.putalpha(a)
    return g


class Overlay:
    """Accumulates elements for one frame, then returns a premultiplied RGBA uint8 array."""

    def __init__(self):
        self.canvas = None

    def _ensure(self):
        if self.canvas is None:
            self.canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))

    def paste(self, layer, cx, cy, alpha=1.0):
        self._ensure()
        if alpha <= 0.001:
            return
        if alpha < 0.999:
            lut = [int(v * alpha) for v in range(256)]
            a = layer.getchannel('A').point(lut)
            layer = layer.copy()
            layer.putalpha(a)
        x = int(round(cx - layer.width / 2))
        y = int(round(cy - layer.height / 2))
        self.canvas.alpha_composite(layer, (max(x, 0), max(y, 0)),
                                    (max(-x, 0), max(-y, 0)))

    def result(self):
        if self.canvas is None:
            return None
        return np.asarray(self.canvas)  # straight alpha; blended on the GPU


# ------------------------------------------------------------------ subtitles
SUB_FONT = ('NotoSerifKR.ttf', 36, 500)
_sub_cache = {}


def subtitle_layer(text):
    if text in _sub_cache:
        return _sub_cache[text]
    f = font(*SUB_FONT)
    lines = text.split('\n')
    layers = [text_layer(l, f, fill=(238, 232, 220), tracking=0.02) for l in lines]
    lh = int(f.size * 1.45)
    wmax = max(l.width for l in layers)
    hsum = layers[0].height + lh * (len(layers) - 1)
    img = Image.new('RGBA', (wmax, hsum), (0, 0, 0, 0))
    for i, l in enumerate(layers):
        img.alpha_composite(l, ((wmax - l.width) // 2, i * lh))
    # soft dark halo for legibility over bright frames
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sh.putalpha(img.split()[3].filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.8)))
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.alpha_composite(sh)
    out.alpha_composite(img)
    _sub_cache[text] = out
    return out


def draw_subtitle(ov, text, alpha):
    lay = subtitle_layer(text)
    nlines = text.count('\n') + 1
    cy = H - BAR / 2 - 2 if nlines == 1 else H - BAR / 2 - 8
    ov.paste(lay, W / 2, cy, alpha)


# ------------------------------------------------------------------ trailer cards
_card_cache = {}


def card_layer(text, size, weight, tracking, color, glow_col, glow_amt, fontname='NotoSerifKR.ttf'):
    key = (text, size, weight, round(tracking, 3), color, glow_col, round(glow_amt, 2), fontname)
    if key in _card_cache:
        return _card_cache[key]
    f = font(fontname, size, weight)
    base = text_layer(text, f, fill=color, tracking=tracking)
    out = Image.new('RGBA', base.size, (0, 0, 0, 0))
    if glow_amt > 0:
        out.alpha_composite(glow(base, size * 0.35, glow_amt, glow_col))
    out.alpha_composite(base)
    if len(_card_cache) > 400:
        _card_cache.clear()
    _card_cache[key] = out
    return out


def draw_card(ov, text, t, dur, size=58, weight=400, y=H / 2, color=(240, 232, 218), glow_col=(255, 200, 140),
              glow_amt=0.6, track0=0.10, track1=0.22, fade_in=0.9, fade_out=0.7, blur_in=True, fontname='NotoSerifKR.ttf'):
    """Classic trailer card: slow tracking expansion, blur-in, fade."""
    if t < 0 or t > dur:
        return
    u = t / dur
    tracking = track0 + (track1 - track0) * u
    a = min(1.0, t / fade_in) if fade_in > 0 else 1.0
    a = min(a, (dur - t) / fade_out) if fade_out > 0 else a
    a = max(0.0, a) ** 1.2
    lay = card_layer(text, size, weight, tracking, color, glow_col, glow_amt, fontname)
    if blur_in and t < fade_in:
        r = (1.0 - t / fade_in) * size * 0.12
        if r > 0.3:
            lay = lay.filter(ImageFilter.GaussianBlur(r))
    ov.paste(lay, W / 2, y + (1.0 - min(1.0, t / (fade_in * 1.5))) * 6, a)


# ------------------------------------------------------------------ title mask for the glass title
def title_mask(text, size=168, weight=600, y=H * 0.46):
    f = font('NotoSerifKR.ttf', size, weight)
    lay = text_layer(text, f, fill=(255, 255, 255), tracking=0.12)
    canvas = Image.new('L', (W, H), 0)
    x = (W - lay.width) // 2
    yy = int(y - lay.height / 2)
    canvas.paste(lay.split()[3], (x, yy))
    fill = canvas
    dil = canvas.filter(ImageFilter.MaxFilter(9))
    ero = canvas.filter(ImageFilter.MinFilter(7))
    outline = Image.fromarray(np.clip(np.asarray(dil, np.int16) - np.asarray(ero, np.int16), 0, 255).astype(np.uint8))
    fill_inner = ero
    glowm = canvas.filter(ImageFilter.GaussianBlur(28))
    rgba = Image.merge('RGBA', (canvas, outline, glowm, canvas))
    return np.asarray(rgba)


# ------------------------------------------------------------------ tree silhouette for the garden
def make_tree(seed=4, size=(2048, 1500)):
    rng = np.random.default_rng(seed)
    S = 2
    img = Image.new('L', (size[0] * S, size[1] * S), 0)
    d = ImageDraw.Draw(img)
    Wt, Ht = img.size

    def branch(x, y, ang, length, width, depth):
        segs = 7
        px, py = x, y
        a = ang
        for i in range(segs):
            a += rng.normal(0, 0.12)
            a += (np.pi / 2 - a) * 0.015  # slight phototropism
            nx = px + np.cos(a) * length / segs
            ny = py - np.sin(a) * length / segs
            w = width * (1 - 0.4 * i / segs)
            d.line([(px, py), (nx, ny)], fill=255, width=max(1, int(w)))
            d.ellipse([nx - w / 2, ny - w / 2, nx + w / 2, ny + w / 2], fill=255)
            # small twigs along the way
            if depth <= 3 and rng.uniform() < 0.5:
                ta = a + rng.choice([-1, 1]) * rng.uniform(0.5, 1.1)
                tl = length * rng.uniform(0.12, 0.25)
                d.line([(nx, ny), (nx + np.cos(ta) * tl, ny - np.sin(ta) * tl)], fill=255, width=max(1, int(w * 0.4)))
            px, py = nx, ny
        if depth == 0 or width < 1.5:
            return
        n = 2 if depth > 6 else int(rng.integers(2, 4))
        for k in range(n):
            na = a + rng.uniform(-0.8, 0.8) + (0.3 if k == 0 else -0.3)
            branch(px, py, na, length * rng.uniform(0.6, 0.78), width * 0.6, depth - 1)

    # trunk rising from the lower right, leaning left over the garden
    branch(Wt * 0.74, Ht * 1.02, np.radians(106), Ht * 0.30, 52 * S, 9)
    img = img.filter(ImageFilter.GaussianBlur(1.2 * S)).resize(size, Image.LANCZOS)
    rgba = Image.new('RGBA', size, (0, 0, 0, 0))
    rgba.putalpha(img)
    return rgba
