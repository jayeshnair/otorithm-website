#!/usr/bin/env python3
"""
Generates the abstract "Why Otorithm" band: assets/images/home-why.jpg (2400x400) + -1200.

The brand's square particles drift in loosely from the left, cool and dim, and lock into a
precise amber-lit grid on the right: scattered effort becoming engineered, accountable work.
Deep ink ground with a warm glow, to sit alongside the photographic bands.

  python3 tools/make_abstract_band.py
Needs: Python 3, numpy, Pillow.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'images')

SS = 2                      # supersampling
W, H = 2400 * SS, 400 * SS
PITCH = 26 * SS             # grid pitch
INK = np.array([24, 28, 34], dtype=np.float32)
INK_WARM = np.array([30, 24, 20], dtype=np.float32)
GREY = np.array([168, 172, 180], dtype=np.float32)
AMBER = np.array([194, 122, 44], dtype=np.float32)
AMBER_HI = np.array([240, 182, 106], dtype=np.float32)


def smooth(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def main():
    rng = np.random.default_rng(11)

    # Ground: ink, warming towards the right, with a soft amber glow behind the ordered grid
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = xx / W
    ground = INK[None, None, :] * (1 - u[..., None] * 0.6) + INK_WARM[None, None, :] * (u[..., None] * 0.6)
    gx, gy, gr = W * 0.72, H * 0.5, W * 0.36
    glow = np.exp(-(((xx - gx) / gr) ** 2 + ((yy - gy) / (gr * 0.55)) ** 2))
    ground += (AMBER * 0.5)[None, None, :] * glow[..., None]
    img = Image.fromarray(np.clip(ground, 0, 255).astype(np.uint8)).convert('RGBA')

    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cols, rows = W // PITCH + 1, H // PITCH + 1
    ox = (W - (cols - 1) * PITCH) / 2
    oy = (H - (rows - 1) * PITCH) / 2
    for r in range(rows):
        for c in range(cols):
            x0, y0 = ox + c * PITCH, oy + r * PITCH
            t = x0 / W
            order = smooth(0.18, 0.78, t + rng.normal(0, 0.04))
            # Disorder: scatter decreases left to right; a gentle flow curve in the loose zone
            scatter = (1 - order) * PITCH * 2.6
            flow = math.sin(y0 / H * math.pi * 1.6 + t * 5.0) * PITCH * 1.4 * (1 - order)
            x = x0 + rng.normal(0, 1) * scatter
            y = y0 + rng.normal(0, 1) * scatter * 0.7 + flow
            if rng.random() < 0.18 * (1 - order):
                continue  # sparser on the left
            heat = order ** 1.6
            col = GREY * (1 - heat) + AMBER * heat
            alpha = (0.42 + 0.45 * order) * (0.7 + 0.3 * rng.random())
            size = (6.5 + 2.5 * rng.random()) * SS * (0.9 + 0.2 * order)
            box = [x - size / 2, y - size / 2, x + size / 2, y + size / 2]
            lit = order > 0.85 and rng.random() < 0.06
            if lit:
                d.rectangle(box, fill=tuple(int(v) for v in AMBER_HI) + (235,))
            else:
                d.rectangle(box, outline=tuple(int(v) for v in col) + (int(alpha * 255),), width=max(1, int(1.25 * SS)))

    # A few "packets" travelling along rows in the ordered zone
    for _ in range(7):
        r = rng.integers(2, rows - 2)
        c0 = rng.integers(int(cols * 0.62), cols - 6)
        for k in range(6):
            x = ox + (c0 + k) * PITCH
            y = oy + r * PITCH
            s = 7.5 * SS
            a = 230 if k == 5 else int(40 + 30 * k)
            d.rectangle([x - s / 2, y - s / 2, x + s / 2, y + s / 2], fill=tuple(int(v) for v in AMBER_HI) + (a,))

    bloom = layer.filter(ImageFilter.GaussianBlur(5 * SS))
    img = Image.alpha_composite(img, bloom)
    img = Image.alpha_composite(img, layer).convert('RGB')

    os.makedirs(OUT, exist_ok=True)
    for width, suffix in ((2400, ''), (1200, '-1200')):
        out = img.resize((width, width // 6), Image.LANCZOS)
        path = os.path.join(OUT, f'home-why{suffix}.jpg')
        out.save(path, quality=84, optimize=True, progressive=True)
        print(f'{os.path.relpath(path, ROOT)}  {out.size[0]}x{out.size[1]}  {os.path.getsize(path) / 1e3:.0f} KB')


if __name__ == '__main__':
    main()
