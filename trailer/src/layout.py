"""Procedural layout of the city of Glimmith (buildings, memory windows, links)."""
import numpy as np

def hill(x):
    return -0.13 + 0.24 * np.exp(-((x - 1.25) / 0.75) ** 2)

def city_layout(seed=7):
    rng = np.random.default_rng(seed)
    B = []   # (x, hw, h, type, base, layer, seed, density)
    F = []   # (x, y, r, seed)
    # back row
    x = -3.9
    spires = {-2.35, -0.55, 2.55}
    while x < 3.9:
        hw = rng.uniform(0.035, 0.075)
        h = rng.uniform(0.14, 0.34)
        t = rng.choice([0, 1, 1, 3, 0])
        if 0.55 < x < 1.95:  # castle hill zone: lower houses on the slope
            h *= 0.5
        near = [s for s in spires if abs(s - x) < 0.09]
        if near:
            x = near[0]; hw = 0.05; h = 0.36 + rng.uniform(0, 0.05); t = 2
        base = -0.12 if not (0.55 < x < 1.95) else hill(x) - 0.03
        B.append((x, hw, h, t, base, 1, rng.uniform(0, 100), rng.uniform(0.25, 0.55)))
        if t == 2:
            F.append((x, base + h - 0.07, 0.032, rng.uniform(0, 1)))
        elif h > 0.26 and rng.uniform() < 0.35:
            F.append((x, base + h * 0.6, 0.02, rng.uniform(0, 1)))
        x += hw * 2 + rng.uniform(0.005, 0.03)
    # far row (hazy, behind everything)
    x = -4.2
    while x < 4.2:
        hw = rng.uniform(0.04, 0.09)
        h = rng.uniform(0.18, 0.46)
        t = rng.choice([0, 1, 2, 3, 1])
        if t == 2: hw = 0.035
        B.append((x, hw, h, t, -0.10, 3, rng.uniform(0, 100), rng.uniform(0.1, 0.3)))
        x += hw * 2 + rng.uniform(0.02, 0.12)
    # castle
    cx = 1.25
    cb = hill(cx) - 0.02
    castle = [(0.0, 0.13, 0.28, 0), (-0.17, 0.035, 0.40, 4), (0.17, 0.035, 0.40, 4), (-0.31, 0.03, 0.27, 4),
              (0.31, 0.03, 0.27, 4), (0.0, 0.045, 0.50, 4), (-0.08, 0.025, 0.36, 4), (0.08, 0.025, 0.36, 4),
              (-0.24, 0.06, 0.17, 0), (0.24, 0.06, 0.17, 0)]
    for dx, hw, h, t in castle:
        B.append((cx + dx, hw, h, t, hill(cx + dx) - 0.02, 2, rng.uniform(0, 100), 0.35))
    F.append((cx, cb + 0.19, 0.062, 0.37))
    F.append((cx, cb + 0.42, 0.022, 0.81))
    F.append((cx - 0.17, hill(cx - 0.17) + 0.30, 0.018, 0.11))
    F.append((cx + 0.17, hill(cx + 0.17) + 0.30, 0.018, 0.58))
    # front row
    x = -3.9
    while x < 3.9:
        hw = rng.uniform(0.03, 0.06)
        h = rng.uniform(0.07, 0.19)
        t = rng.choice([1, 1, 0, 1, 3])
        B.append((x, hw, h, t, -0.17, 0, rng.uniform(0, 100), rng.uniform(0.3, 0.6)))
        if h > 0.15 and rng.uniform() < 0.3:
            F.append((x, -0.17 + h * 0.6, 0.017, rng.uniform(0, 1)))
        x += hw * 2 + rng.uniform(0.0, 0.02)
    # order: back first so front overrides via layer compare (shader picks lowest layer id)
    B = B[:200]
    F = F[:24]
    Fa = np.array([f[:2] for f in F])
    links = set()
    for i in range(len(F)):
        d = np.linalg.norm(Fa - Fa[i], axis=1)
        order = np.argsort(d)[1:4]
        for j in order[:2 + (i % 2)]:
            links.add(tuple(sorted((i, int(j)))))
    castle_i = [i for i, f in enumerate(F) if abs(f[0] - cx) < 0.01 and f[2] > 0.05][0]
    for i in rng.choice(len(F), 8, replace=False):
        if i != castle_i:
            links.add(tuple(sorted((castle_i, int(i)))))
    links = sorted(links)[:40]
    L = [(F[a][0], F[a][1], F[b][0], F[b][1]) for a, b in links]
    return B, F, L
