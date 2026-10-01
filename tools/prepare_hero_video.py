#!/usr/bin/env python3
"""
Prepares a clip for the home hero: grade it to sit on the white site, make it loop,
and write assets/videos/<slug>.mp4 plus a poster frame assets/videos/<slug>.jpg.

  python3 tools/prepare_hero_video.py SRC SLUG [--grade G] [--loop L] [--fade S] [--max-width W]

Grades
  none     leave colours alone
  whiten   lift a light-grey background to white (shading kept)            e.g. AI renders on grey
  soften   desaturate and lift towards white, keep bright highlights        e.g. warm, sunlit footage
  amber    re-colour into the brand amber range (dark rust to light amber)  e.g. vivid textures

Loops
  none      play as is (jumps if first and last frames differ)
  pingpong  forward then backward (seamless, doubles length)
  xfade     crossfade the end into the start (seamless, natural for one-way motion)

Needs ffmpeg and ffprobe on PATH. Then run: python3 build.py
"""
import argparse
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'videos')

GRADES = {
    'none': '',
    'whiten': "curves=all='0/0 0.5/0.56 0.89/1'",
    'soften': "eq=saturation=0.6:gamma=1.05,curves=all='0/0 0.5/0.6 0.86/1'",
    # luminance -> brand amber ramp: #6E3A10 (shadows) .. #F0B66A (highlights)
    'amber': "hue=s=0,eq=contrast=1.35:brightness=0.02,"
             "lutrgb=r='110+(240-110)*val/255':g='58+(182-58)*val/255':b='16+(106-16)*val/255'",
}


def duration(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'default=nw=1:nk=1', path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src')
    ap.add_argument('slug')
    ap.add_argument('--grade', choices=GRADES, default='none')
    ap.add_argument('--loop', choices=['none', 'pingpong', 'xfade'], default='xfade')
    ap.add_argument('--fade', type=float, default=1.0, help='crossfade seconds for --loop xfade')
    ap.add_argument('--max-width', type=int, default=1920)
    ap.add_argument('--crf', type=int, default=24)
    a = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    mp4 = os.path.join(OUT, f'{a.slug}.mp4')
    jpg = os.path.join(OUT, f'{a.slug}.jpg')

    base = (f"scale='min({a.max_width},iw)':-2:flags=lanczos,"
            "crop='trunc(min(iw,ih*16/9)/2)*2':'trunc(min(ih,iw*9/16)/2)*2',format=yuv420p")
    if GRADES[a.grade]:
        base += ',' + GRADES[a.grade] + ',format=yuv420p'

    if a.loop == 'pingpong':
        graph = f"[0:v]{base},split[f][b];[b]reverse[r];[f][r]concat=n=2:v=1:a=0[out]"
    elif a.loop == 'xfade':
        d, f = duration(a.src), a.fade
        if d <= 2 * f:
            raise SystemExit(f'clip is {d:.1f}s; --fade must be under {d / 2:.1f}s')
        # Start at f, play to the end, then crossfade into the first f seconds.
        # The output ends on source frame f, which is where it starts: seamless.
        graph = (f"[0:v]{base},split[x][y];"
                 f"[x]trim=start={f},setpts=PTS-STARTPTS[tail];"
                 f"[y]trim=end={f},setpts=PTS-STARTPTS[head];"
                 f"[tail][head]xfade=transition=fade:duration={f}:offset={d - 2 * f:.3f}[out]")
    else:
        graph = f"[0:v]{base}[out]"

    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', a.src, '-filter_complex', graph, '-map', '[out]', '-an',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', str(a.crf), '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', mp4], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-frames:v', '1', '-q:v', '3', jpg], check=True)
    print(f'{os.path.relpath(mp4, ROOT)}  {os.path.getsize(mp4) / 1e6:.2f} MB  {duration(mp4):.1f}s   '
          f'{os.path.relpath(jpg, ROOT)}  {os.path.getsize(jpg) / 1e3:.0f} KB')


if __name__ == '__main__':
    main()
