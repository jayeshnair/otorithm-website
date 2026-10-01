#!/usr/bin/env python3
"""
Renders a generated placeholder hero video: assets/videos/placeholder.mp4 + .jpg.
To use it, add an entry with 'file': 'placeholder' to HERO_VIDEOS in content.py.

A light paper field of the brand's square particles. A slow diagonal wave passes through it,
the Ligature mark is formed faintly on the right, and amber "packets" hop across the grid.

Needs: Python 3, numpy, Pillow, ffmpeg on PATH.
  python3 tools/render_hero_video.py
"""
import math
import os
import random
import subprocess

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_MP4 = os.path.join(ROOT, 'assets', 'videos', 'placeholder.mp4')
OUT_POSTER = os.path.join(ROOT, 'assets', 'videos', 'placeholder.jpg')

W, H = 1920, 1080
FPS = 30
SECONDS = 12                     # loop length
FRAMES = FPS * SECONDS

BG = np.array([255, 255, 255], dtype=float)
INK = np.array([17, 20, 24], dtype=float)
AMBER = np.array([194, 122, 44], dtype=float)

STEP = 32                        # grid pitch (px)
SQ = 10                          # particle square size (px)
LINE = 2                         # outline width (px)

# Ligature mark rects in 120x120 units (same as the site's constellation engine).
LIGATURE = [
    (10, 42, 94, 12, False), (10, 42, 12, 60, False), (10, 90, 56, 12, False),
    (54, 42, 12, 60, False), (78, 20, 12, 82, True),
]
MARK_PX = 700                    # mark size on screen
MARK_CX, MARK_CY = W * 0.71, H * 0.53
DRAW_MARK = False             # the site draws the interactive particle logo on top


def color(rgb, a):
    c = BG * (1 - a) + rgb * a
    return tuple(int(round(v)) for v in c)


def main():
    rng = random.Random(7)
    cols, rows = W // STEP + 1, H // STEP + 1
    ox = (W - (cols - 1) * STEP) // 2
    oy = (H - (rows - 1) * STEP) // 2

    # Classify grid cells: field, mark (ink), mark (amber).
    scale = MARK_PX / 120
    mx, my = MARK_CX - MARK_PX / 2, MARK_CY - MARK_PX / 2
    cells = []
    for r in range(rows):
        for c in range(cols):
            x, y = ox + c * STEP, oy + r * STEP
            ux, uy = (x - mx) / scale, (y - my) / scale
            kind = 0
            for_mark = LIGATURE if DRAW_MARK else []
            for (rx, ry, rw, rh, amber) in for_mark:
                if rx <= ux <= rx + rw and ry <= uy <= ry + rh:
                    kind = 2 if amber else max(kind, 1)
            cells.append((c, r, x, y, kind))

    # Packets: cells that hop along a row or column, with a fading trail.
    packets = []
    for i in range(10):
        horizontal = i < 7
        span = (cols if horizontal else rows) + 14
        packets.append({
            'h': horizontal,
            'lane': rng.randrange(2, (rows if horizontal else cols) - 2),
            'start': rng.uniform(0, span),
            'laps': rng.choice([1, 1, 2]),
            'dir': rng.choice([1, -1]),
            'span': span,
        })

    theta = math.radians(28)
    kx, ky = math.cos(theta), math.sin(theta)
    wavelength = 1100.0

    ff = subprocess.Popen(
        ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
         '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '26', '-pix_fmt', 'yuv420p',
         '-movflags', '+faststart', '-an', OUT_MP4],
        stdin=subprocess.PIPE,
    )

    for f in range(FRAMES):
        t = f / FRAMES                      # 0..1, periodic
        img = Image.new('RGB', (W, H), tuple(int(v) for v in BG))
        d = ImageDraw.Draw(img)

        lit = {}
        for p in packets:
            pos = (p['start'] + p['dir'] * p['laps'] * p['span'] * t) % p['span'] - 7
            head = math.floor(pos)
            for k in range(7):
                idx = head - k * p['dir']
                a = 1.0 if k == 0 else 0.55 * (1 - k / 7)
                key = (idx, p['lane']) if p['h'] else (p['lane'], idx)
                lit[key] = max(lit.get(key, 0), a)

        for (c, r, x, y, kind) in cells:
            phase = 2 * math.pi * (t - (x * kx + y * ky) / wavelength)
            w = 0.5 + 0.5 * math.sin(phase)
            if kind == 0:
                a, rgb = 0.05 + 0.16 * w ** 4, INK
            elif kind == 1:
                a, rgb = 0.30 + 0.28 * w, INK
            else:
                a, rgb = 0.55 + 0.35 * w, AMBER
            box = [x - SQ // 2, y - SQ // 2, x + SQ // 2 - 1, y + SQ // 2 - 1]
            pa = lit.get((c, r))
            if pa:
                if pa >= 1.0:
                    d.rectangle(box, fill=color(AMBER, 0.95))
                    continue
                a, rgb = max(a, pa), AMBER
            d.rectangle(box, outline=color(rgb, a), width=LINE)

        if f == 0:
            img.save(OUT_POSTER, quality=84, optimize=True, progressive=True)
        ff.stdin.write(img.tobytes())

    ff.stdin.close()
    ff.wait()
    print(f'wrote {OUT_MP4} ({os.path.getsize(OUT_MP4) / 1e6:.2f} MB) and {OUT_POSTER} ({os.path.getsize(OUT_POSTER) / 1e3:.0f} KB)')


if __name__ == '__main__':
    main()
