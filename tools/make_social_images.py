#!/usr/bin/env python3
"""
Renders the share images and icons that build.py links from every page:

  assets/og/default.png            1200 x 630  site-wide share image (Open Graph / X / LinkedIn)
  assets/og/<page-key>.png         1200 x 630  one per service and article, titled for that page
  assets/icons/logo-512.png        512 x 512   logo for structured data (Google wants a raster logo)
  assets/icons/icon-192.png        192 x 192   web app manifest
  assets/icons/icon-512.png        512 x 512   web app manifest
  assets/icons/apple-touch-icon.png 180 x 180  iOS home screen
  assets/icons/favicon-48.png      48 x 48     PNG favicon (Google shows favicons at multiples of 48 px)
  assets/icons/favicon.ico         16/32/48    served at /favicon.ico for crawlers that ask for it

Re-run after changing a service name, an article title or the brand mark, then rebuild:

  python3 tools/make_social_images.py && python3 build.py

Needs: Python 3, Pillow, Playwright for Python with Chromium (pip install playwright && playwright install chromium).
"""
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import content as C  # noqa: E402

FONT = os.path.join(ROOT, 'assets', 'fonts', 'sora-latin.woff2')
BG = os.path.join(ROOT, 'assets', 'videos', f"{C.SITE['hero_video']['file']}.jpg")
OG_DIR = os.path.join(ROOT, 'assets', 'og')
ICON_DIR = os.path.join(ROOT, 'assets', 'icons')
INK, WHITE, AMBER, AMBER_TEXT, MUTED = '#111418', '#ffffff', '#c27a2c', '#9a5a1a', '#5b616b'
MARK = ('<path d="M104 48 H16 V96 H60 V48" fill="none" stroke-width="12" stroke-linejoin="miter" stroke="{base}"/>'
        '<path d="M84 20 V102" fill="none" stroke-width="12" stroke="{accent}"/>')


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def page(w, h, body):
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: 'Sora'; src: url('file://{FONT}') format('woff2'); font-weight: 300 600; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: {w}px; height: {h}px; overflow: hidden; background: {WHITE}; }}
body {{ position: relative; font-family: 'Sora', sans-serif; color: {INK}; -webkit-font-smoothing: antialiased; }}
.abs {{ position: absolute; }}
</style></head><body>{body}</body></html>'''


def og_html(label, title, sub):
    w, h = 1200, 630
    size = 68 if len(title) <= 32 else 58 if len(title) <= 52 else 50
    sub_html = f'<p style="font-size:24px; line-height:1.4; color:{MUTED}; max-width:600px">{esc(sub)}</p>' if sub else ''
    body = f'''
<img class="abs" src="file://{BG}" style="right:0; top:0; width:700px; height:{h}px; object-fit:cover; object-position:58% 46%;
  -webkit-mask-image:linear-gradient(90deg, transparent 0%, transparent 18%, rgba(0,0,0,0.35) 40%, rgba(0,0,0,0.8) 62%, #000 78%)">
<div class="abs" style="left:72px; top:64px; display:flex; align-items:center; gap:14px">
  <svg width="46" height="46" viewBox="0 0 120 120">{MARK.format(base=INK, accent=AMBER)}</svg>
  <span style="font-size:36px; font-weight:600; letter-spacing:-0.02em">otorithm</span>
</div>
<div class="abs" style="left:72px; top:150px; bottom:110px; width:640px; display:flex; flex-direction:column; justify-content:center; gap:22px">
  <p style="font-size:19px; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:{AMBER_TEXT}">{esc(label)}</p>
  <h1 style="font-size:{size}px; line-height:1.04; font-weight:400; letter-spacing:-0.035em">{esc(title)}</h1>
  {sub_html}
</div>
<p class="abs" style="left:72px; bottom:58px; font-size:22px; font-weight:600">otorithm.com</p>
<div class="abs" style="left:0; right:0; bottom:0; height:8px; background:{AMBER}"></div>'''
    return page(w, h, body)


def icon_html(size, pad, bg=WHITE):
    # The mark's ink bounding box in its 120-unit space is x 10-104, y 20-102 (centre 57, 61)
    s = (1 - 2 * pad) * size / 94
    tx, ty = size / 2 - 57 * s, size / 2 - 61 * s
    body = (f'<svg class="abs" style="inset:0; background:{bg}" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<g transform="translate({tx:.2f} {ty:.2f}) scale({s:.4f})">{MARK.format(base=INK, accent=AMBER)}</g></svg>')
    return page(size, size, body)


def og_pages():
    yield 'default', C.HOME['label'], C.HOME['title'], 'AI products, legacy modernization, forward-deployed engineers and senior staff augmentation.'
    for slug, s in C.SERVICES.items():
        yield f'service-{slug}', 'Services', s['name'], s['nav']
    for a in C.ARTICLES:
        yield f"insight-{a['slug']}", f"Insights · {a['topic']}", a['title'], None


def main():
    from playwright.sync_api import sync_playwright
    os.makedirs(OG_DIR, exist_ok=True)
    os.makedirs(ICON_DIR, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        def shot(html, path, w, h, scale=2, text=True):
            pg = browser.new_page(viewport={'width': w, 'height': h}, device_scale_factor=scale)
            # Loaded from a file:// page so the local font and background image are allowed to load
            src = path + '.tmp.html'
            with open(src, 'w', encoding='utf-8') as f:
                f.write(html)
            pg.goto('file://' + src, wait_until='load')
            pg.evaluate('document.fonts.ready')
            if text and not pg.evaluate("document.fonts.check('400 20px Sora')"):
                raise SystemExit('Sora did not load: check assets/fonts/sora-latin.woff2')
            tmp = path + '.tmp.png'
            pg.screenshot(path=tmp)
            pg.close()
            Image.open(tmp).convert('RGB').resize((w, h), Image.LANCZOS).save(path, optimize=True)
            os.remove(tmp)
            os.remove(src)
            print(f'{os.path.relpath(path, ROOT):42s} {w}x{h}  {os.path.getsize(path) / 1e3:.0f} KB')

        for key, label, title, sub in og_pages():
            shot(og_html(label, title, sub), os.path.join(OG_DIR, f'{key}.png'), 1200, 630)
        for name, size, pad in [('logo-512', 512, 0.2), ('icon-512', 512, 0.2), ('icon-192', 192, 0.2),
                                ('apple-touch-icon', 180, 0.18), ('favicon-48', 48, 0.08)]:
            shot(icon_html(size, pad), os.path.join(ICON_DIR, f'{name}.png'), size, size, scale=4 if size < 100 else 2, text=False)
        browser.close()
    fav = Image.open(os.path.join(ICON_DIR, 'favicon-48.png'))
    fav.save(os.path.join(ICON_DIR, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
    print('assets/icons/favicon.ico')


if __name__ == '__main__':
    main()
