#!/usr/bin/env python3
"""
Crops the home-page photos into full-width bands (6:1) and writes
assets/images/<name>.jpg (2400x400) and <name>-1200.jpg (1200x200).

Each band is a crop of the source around its subject. Where the subject cannot be placed
as wanted inside the photo (e.g. centred, or fully in frame), the photo's out-of-focus
background is extended sideways: edge colours, heavily blurred, feathered into the photo.

  python3 tools/make_bands.py            # sources in source/images/
Needs: Python 3, numpy, Pillow.
"""
import os

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source', 'images')
OUT = os.path.join(ROOT, 'assets', 'images')
RATIO = 6.0

# crop: (top, bottom) rows of the source to keep, full width unless 'left'/'right' given.
# center_x: source x to place at the band's centre (extends the background as needed).
# pad: (left, right) share of extra width when only the height is fixed and no centre is given.
ONLY = None  # set to a band name to rebuild just that one
BANDS = [
    {'name': 'home-different', 'file': 'different.jpg', 'crop': (630, 1270)},               # face centred
    # paper plane centred; the right-hand extension reuses the photo's own foliage bokeh (x 0-2400)
    {'name': 'home-services', 'file': 'services.jpg', 'crop': (560, 2240), 'center_x': 3902,
     'borrow_right': (0, 2400), 'borrow_left': (0, 1600)},
    {'name': 'home-engage', 'file': 'engage.jpg', 'crop': (735, 1735)},                    # sitting figure, sun rays
    {'name': 'home-industries', 'file': 'industries.jpg', 'crop': (520, 1192)},            # lighthouse lantern, sea
    {'name': 'home-insights', 'file': 'insights.jpg', 'crop': (70, 1232), 'pad': (0.5, 0.5)},  # whole brain, collar out of frame
]


def textured_fill(region, width, side, borrow):
    """Fill of `width` px for one side, made from real columns region[:, a:b], colour-matched
    to the photo strip next to that seam and mirror-tiled to length."""
    a, b = borrow
    src = region[:, a:b].astype(np.float32)
    strip = region[:, -600:] if side == 'right' else region[:, :600]
    strip = strip.astype(np.float32)
    ms, ss = src.reshape(-1, 3).mean(0), src.reshape(-1, 3).std(0) + 1e-3
    mt, st = strip.reshape(-1, 3).mean(0), strip.reshape(-1, 3).std(0)
    matched = (src - ms) / ss * st + mt
    tiles, n = [], 0
    flip = False
    while n < width:
        tiles.append(matched[:, ::-1] if flip else matched)
        n += matched.shape[1]
        flip = not flip
    fill = np.concatenate(tiles, axis=1)[:, :width]
    if side == 'left':
        fill = fill[:, ::-1]
    img = Image.fromarray(np.clip(fill, 0, 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(region.shape[0] * 0.012)), dtype=np.uint8)


def extend(region, pad_left, pad_right, feather, borrow_right=None, borrow_left=None):
    """Widen `region` (HxWx3 uint8) with blurred edge colours, feathered into the photo."""
    h, w, _ = region.shape
    canvas = np.pad(region, ((0, 0), (pad_left, pad_right), (0, 0)), mode='edge')
    radius = max(12, h * 0.06)
    soft = np.asarray(Image.fromarray(canvas).filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32)
    # Second, wider pass for the far extension so it reads as deep background blur
    softer = np.asarray(Image.fromarray(canvas).filter(ImageFilter.GaussianBlur(radius * 2.2)), dtype=np.float32)

    x = np.arange(canvas.shape[1], dtype=np.float32)
    inside_l, inside_r = pad_left, pad_left + w
    # weight of the real photo: 1 well inside, ramps to 0 at the seams over `feather` px
    real = np.clip(np.minimum(x - inside_l, inside_r - 1 - x) / max(feather, 1), 0, 1)
    real = real * real * (3 - 2 * real)
    # mix the two blur strengths: further from the photo, softer
    dist = np.maximum(inside_l - x, x - (inside_r - 1)).clip(min=0)
    far = np.clip(dist / max(h * 0.8, 1), 0, 1)[None, :, None]
    synth = soft * (1 - far) + softer * far
    rng = np.random.default_rng(3)
    synth += rng.normal(0, 2.2, synth.shape).astype(np.float32) * (1 - real)[None, :, None]

    if borrow_right and pad_right:
        tex = textured_fill(region, pad_right, 'right', borrow_right).astype(np.float32)
        tex += rng.normal(0, 1.5, tex.shape).astype(np.float32)
        # Just outside the seam the fill starts as the blurred edge (continuous with the photo),
        # then crossfades into the borrowed texture over 1.2 x feather.
        span = int(feather * 1.2)
        t = np.clip(np.arange(pad_right, dtype=np.float32) / max(span, 1), 0, 1)
        t = (t * t * (3 - 2 * t))[None, :, None]
        synth[:, inside_r:] = synth[:, inside_r:] * (1 - t) + tex * t
    if borrow_left and pad_left:
        tex = textured_fill(region, pad_left, 'left', borrow_left).astype(np.float32)
        tex += rng.normal(0, 1.5, tex.shape).astype(np.float32)
        span = int(feather * 1.2)
        t = np.clip(np.arange(pad_left, dtype=np.float32)[::-1] / max(span, 1), 0, 1)
        t = (t * t * (3 - 2 * t))[None, :, None]
        synth[:, :inside_l] = synth[:, :inside_l] * (1 - t) + tex * t
    out = canvas.astype(np.float32) * real[None, :, None] + synth * (1 - real[None, :, None])
    return np.clip(out, 0, 255).astype(np.uint8)


def make(band):
    img = Image.open(os.path.join(SRC, band['file'])).convert('RGB')
    W, H = img.size
    top, bottom = band['crop']
    h = bottom - top
    target_w = int(round(h * RATIO))
    region = np.asarray(img.crop((0, top, W, bottom)))

    if 'center_x' in band:
        cx = band['center_x']
        left = max(0, int(round(target_w / 2 - cx)))
        right = max(0, target_w - left - W)
        x0 = max(0, int(round(cx - target_w / 2)))
        region = region[:, x0:x0 + (target_w - left - right)]
        result = extend(region, left, right, feather=int(h * 0.35), borrow_right=band.get('borrow_right'), borrow_left=band.get('borrow_left')) if (left or right) else region
    elif target_w > W:
        extra = target_w - W
        pl, pr = band.get('pad', (0.5, 0.5))
        left = int(round(extra * pl / (pl + pr)))
        result = extend(region, left, extra - left, feather=int(h * 0.35))
    else:
        x0 = (W - target_w) // 2
        result = region[:, x0:x0 + target_w]

    pic = Image.fromarray(result)
    os.makedirs(OUT, exist_ok=True)
    for width, suffix in ((2400, ''), (1200, '-1200')):
        out = pic.resize((width, int(round(width / RATIO))), Image.LANCZOS)
        path = os.path.join(OUT, f"{band['name']}{suffix}.jpg")
        out.save(path, quality=80, optimize=True, progressive=True)
        print(f'{os.path.relpath(path, ROOT)}  {out.size[0]}x{out.size[1]}  {os.path.getsize(path) / 1e3:.0f} KB')


if __name__ == '__main__':
    import sys
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for b in BANDS:
        if only in (None, b['name']):
            make(b)
