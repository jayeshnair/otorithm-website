#!/usr/bin/env python3
"""
Builds the Otorithm website into ./dist (static HTML, no dependencies beyond Python 3.8+).

  python3 build.py              # production build into dist/
  python3 build.py --artifact   # also writes artifact/index.html for the Claude preview

Copy lives in content.py; styles and scripts in assets/.
"""
import hashlib
import html
import json
import os
import posixpath
import shutil
import sys

import content as C

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
ASSETS = ['styles.css', 'site.js', 'constellation.js', 'favicon.svg']


def video_assets():
    v = C.SITE['hero_video']['file']
    return [f'videos/{v}.mp4', f'videos/{v}.jpg']


def esc(s):
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def rel(frm, to):
    """Relative URL from page `frm` to site path `to` (both relative to the site root)."""
    base = posixpath.dirname(frm) or '.'
    target, _, frag = to.partition('#')
    out = posixpath.relpath(target, base) if target else posixpath.basename(frm)
    return out + ('#' + frag if frag else '')


def asset_versions():
    v = {}
    for name in ASSETS + video_assets():
        with open(os.path.join(ROOT, 'assets', name), 'rb') as f:
            v[name] = hashlib.sha1(f.read()).hexdigest()[:8]
    return v


VERSIONS = {}

ARROW = '<span class="arrow" aria-hidden="true">→</span>'
COPY_ICON = (
    '<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true">'
    '<rect x="3.5" y="3.5" width="7.5" height="7.5" rx="1.2"></rect>'
    '<path d="M8.5 1H2.2C1.54 1 1 1.54 1 2.2v6.3"></path></svg>'
)


def mark(size):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 120 120" aria-hidden="true" focusable="false">'
        '<path d="M104 48 H16 V96 H60 V48" fill="none" stroke-width="12" stroke-linejoin="miter" style="stroke: var(--fg)"></path>'
        '<path d="M84 20 V102" fill="none" stroke-width="12" style="stroke: var(--accent)"></path></svg>'
    )


def lockup(p, size=34, small=False):
    style = ' style="font-size: 21px"' if small else ''
    return f'<a href="{rel(p, "index.html")}" class="lockup" aria-label="Otorithm home">{mark(size)}<span class="wordmark"{style}>otorithm</span></a>'


def copy_btn(value, cls='ghost copy'):
    return f'<button type="button" class="{cls}" data-copy="{esc(value)}"><span data-copy-label>{esc(value)}</span>{COPY_ICON}</button>'


def ghost(href, text):
    return f'<a href="{href}" class="ghost">{esc(text)} {ARROW}</a>'


def canvas(formation, ambient=0, fill=0.72):
    amb = f' data-ambient="{ambient}"' if ambient else ''
    return f'<canvas data-formation="{formation}"{amb} data-fill="{fill}"></canvas>'


def band(p, key):
    """Full-width image band: the image if one is set in content.IMAGES, otherwise a placeholder."""
    im = C.IMAGES[key]
    src = im.get('src')
    if src and os.path.exists(os.path.join(ROOT, src)):
        def url(path):
            with open(os.path.join(ROOT, path), 'rb') as f:
                return rel(p, path) + '?v=' + hashlib.sha1(f.read()).hexdigest()[:8]
        small = src.replace('.jpg', '-1200.jpg')
        srcset = f' srcset="{url(small)} 1200w, {url(src)} 2400w" sizes="100vw"' if os.path.exists(os.path.join(ROOT, small)) else ''
        pos = f' style="object-position: {esc(im["pos"])}"' if im.get('pos') else ''
        inner = (f'<img src="{url(src)}"{srcset} alt="{esc(im.get("alt", ""))}" width="2400" height="400" '
                 f'loading="lazy" decoding="async"{pos}>')
    else:
        inner = (f'<div class="band-ph" role="img" aria-label="Image placeholder: {esc(im["hint"])}">'
                 f'<span class="band-tag"><span class="band-label">Image · 2400 × 400</span><span class="band-hint">{esc(im["hint"])}</span></span></div>')
    return f'<figure class="band">{inner}</figure>'


def svc_path(slug):
    return f'services/{slug}.html'


def svc_group(slug):
    for g, slugs in C.SERVICE_GROUPS:
        if slug in slugs:
            return g
    return ''


# ---------------------------------------------------------------------------
# Chrome: header, menu, footer
# ---------------------------------------------------------------------------
NAV = [
    ('Industries', 'industries.html'),
    ('Approach', 'approach.html'),
    ('Work', 'work.html'),
    ('Insights', 'insights.html'),
    ('Company', 'about.html'),
]


def header(p, active):
    def cur(key):
        return ' aria-current="page"' if active == key else ''

    groups = ''
    for g, slugs in C.SERVICE_GROUPS:
        links = ''.join(
            f'<a class="panel-link" href="{rel(p, svc_path(s))}"><strong>{esc(C.SERVICES[s]["name"])}</strong>'
            f'<span>{esc(C.SERVICES[s]["nav"])}</span></a>'
            for s in slugs
        )
        groups += f'<div class="panel-group"><p class="label">{esc(g)}</p>{links}</div>'

    panel = (
        '<div class="panel"><div class="wrap panel-grid">'
        '<div class="panel-intro"><p class="h4">Six services, one AI-native delivery model.</p>'
        '<p class="small">Start where you are today. Most clients combine two as the work grows.</p>'
        f'{ghost(rel(p, "services.html"), "All services")}</div>'
        f'{groups}</div></div>'
    )
    items = (
        '<div class="nav-item has-panel">'
        f'<a class="nav-link" href="{rel(p, "services.html")}"{cur("services")}>Services <span class="chev" aria-hidden="true"></span></a>'
        f'{panel}</div>'
    )
    for label, href in NAV:
        key = href.split('.')[0]
        items += f'<div class="nav-item"><a class="nav-link" href="{rel(p, href)}"{cur(key)}>{label}</a></div>'

    menu_main = ''.join(
        f'<a href="{rel(p, h)}" tabindex="-1">{l}</a>'
        for l, h in [('Services', 'services.html')] + NAV + [('Careers', 'careers.html'), ('Contact', 'contact.html')]
    )
    menu_sub = ''.join(
        f'<a href="{rel(p, svc_path(s))}" tabindex="-1">{esc(C.SERVICES[s]["name"])}</a>'
        for _, slugs in C.SERVICE_GROUPS for s in slugs
    )
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="nav">
  <div class="wrap nav-inner">
    {lockup(p)}
    <nav class="nav-links" aria-label="Primary">{items}</nav>
    <a href="{rel(p, 'contact.html')}" class="btn btn-sm nav-cta">Talk to us</a>
    <button type="button" class="burger" id="burger" aria-label="Open menu" aria-expanded="false" aria-controls="menu"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="menu" id="menu" aria-hidden="true">
  <div class="menu-inner">
    <nav class="menu-main" aria-label="Mobile">{menu_main}</nav>
    <div class="menu-sub"><p class="label">Services</p>{menu_sub}</div>
    <a href="{rel(p, 'contact.html')}" class="btn" tabindex="-1" style="align-self: flex-start">Talk to us</a>
  </div>
</div>'''


def footer(p):
    svc = ''.join(
        f'<li><a href="{rel(p, svc_path(s))}">{esc(C.SERVICES[s]["name"])}</a></li>'
        for _, slugs in C.SERVICE_GROUPS for s in slugs
    )
    company = ''.join(
        f'<li><a href="{rel(p, h)}">{l}</a></li>'
        for l, h in [('About', 'about.html'), ('Approach', 'approach.html'), ('Industries', 'industries.html'),
                     ('Work', 'work.html'), ('Insights', 'insights.html'), ('Careers', 'careers.html')]
    )
    return f'''<footer class="footer">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        {lockup(p, 28, small=True)}
        <p>{esc(C.SITE['tagline'])}</p>
        <div>{copy_btn(C.SITE['email'])}</div>
      </div>
      <div class="foot-col"><h2>Services</h2><ul>{svc}</ul></div>
      <div class="foot-col"><h2>Company</h2><ul>{company}</ul></div>
      <div class="foot-col"><h2>Contact</h2><ul>
        <li><a href="{rel(p, 'contact.html')}">Start a conversation</a></li>
        <li>{esc(C.SITE['email'])}</li>
        <li>{esc(C.SITE['careers_email'])}</li>
        <li>{esc(C.SITE['city'])}</li>
      </ul></div>
    </div>
    <div class="foot-legal">
      <span>© 2026 {esc(C.SITE['legal'])}. Otorithm is a brand of {esc(C.SITE['legal'])}.</span>
      <a href="{rel(p, 'privacy.html')}">Privacy notice</a>
    </div>
  </div>
</footer>
<div class="sr-only" aria-live="polite" id="live-status"></div>'''


def cta_band(p, title='What are we building?', body='Tell us about the problem. An engineer, not a sales team, will reply.'):
    return f'''<section class="cta-band">
  <div class="wrap stack">
    <h2 class="display">{esc(title)}</h2>
    <p class="lead">{esc(body)}</p>
    <div class="actions">
      <a href="{rel(p, 'contact.html')}" class="btn">Talk to us</a>
      {copy_btn(C.SITE['email'])}
    </div>
  </div>
</section>'''


def page_hero(p, label, title, lead, formation=None, actions='', crumb=None, label_href=None):
    if crumb:
        lab = '<div class="crumb">' + '<span class="sep" aria-hidden="true">/</span>'.join(
            f'<a class="label" href="{rel(p, h)}">{esc(t)}</a>' if h else f'<span class="label">{esc(t)}</span>'
            for t, h in crumb
        ) + '</div>'
    else:
        lab = f'<p class="label">{esc(label)}</p>'
    visual = f'<div class="visual" aria-hidden="true">{canvas(formation, 0, 0.84)}</div>' if formation else ''
    grid_cls = 'page-hero-grid has-visual' if formation else 'page-hero-grid'
    act = f'<div class="actions">{actions}</div>' if actions else ''
    return f'''<section class="page-hero">
  <div class="wrap {grid_cls}">
    <div class="stack">
      {lab}
      <h1 class="h1">{esc(title)}</h1>
      <p class="lead">{esc(lead)}</p>
      {act}
    </div>
    {visual}
  </div>
</section>'''


def sec_head(label, title, body=None, h='h2'):
    b = f'<p class="body">{esc(body)}</p>' if body else '<span></span>'
    return f'''<div class="sec-head">
  <div class="stack-sm"><p class="label">{esc(label)}</p><h2 class="{h}">{esc(title)}</h2></div>
  {b}
</div>'''


def models_table(keys):
    rows = ''.join(
        f'<tr><td>{esc(C.MODELS[k]["name"])}</td><td class="term">{esc(C.MODELS[k]["term"])}</td>'
        f'<td>{esc(C.MODELS[k]["what"])}</td><td>{esc(C.MODELS[k]["best"])}</td></tr>'
        for k in keys
    )
    return f'''<div class="table-wrap"><table class="table">
  <thead><tr><th scope="col">Model</th><th scope="col">Term</th><th scope="col">What it is</th><th scope="col">Best for</th></tr></thead>
  <tbody>{rows}</tbody>
</table></div>'''


def article_rows(p, articles):
    return '<div class="rows">' + ''.join(
        f'''<a class="row" href="{rel(p, f"insights/{a['slug']}.html")}">
  <div class="stack-sm"><p class="label">{esc(a['topic'])}</p><h3 class="h3">{esc(a['title'])}</h3></div>
  <div><p class="small">{esc(a['summary'])}</p><div class="row-meta"><span class="meta">{a['minutes']} min read</span></div></div>
  {ARROW}
</a>''' for a in articles
    ) + '</div>'


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------
def shell(p, title, desc, body, active=None, extra_head='', artifact_index=False):
    canonical = C.SITE['domain'] + '/' + ('' if p == 'index.html' else p)
    v = VERSIONS
    a = lambda name: rel(p, f'assets/{name}') + f'?v={v[name]}'
    head = f'''<title>{esc('Otorithm Website' if artifact_index else title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#ffffff">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Otorithm">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/svg+xml" href="{a('favicon.svg')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600&amp;display=swap">
<link rel="stylesheet" href="{a('styles.css')}">
{extra_head}'''
    page = f'''{header(p, active)}
<main id="main">
{body}
</main>
{footer(p)}
<script src="{a('constellation.js')}" defer></script>
<script src="{a('site.js')}" defer></script>'''
    if artifact_index:
        return head + '\n' + page + '\n'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head}
</head>
<body>
{page}
</body>
</html>
'''


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_home(p):
    H = C.HOME
    loop = ''.join(
        f'<li><span class="num">{i:02d}</span><h3 class="h4">{esc(t)}</h3><p class="small">{esc(d)}</p></li>'
        for i, (t, d) in enumerate(C.LOOP, 1)
    )
    svc_rows = ''
    for g, slugs in C.SERVICE_GROUPS:
        for s in slugs:
            S = C.SERVICES[s]
            svc_rows += f'''<a class="row" href="{rel(p, svc_path(s))}">
  <div class="stack-sm"><p class="label">{esc(g)}</p><h3 class="h3">{esc(S['name'])}</h3></div>
  <p class="small">{esc(S['short'])}</p>
  {ARROW}
</a>'''
    models = ''.join(
        f'<div class="feature"><h3 class="h4">{esc(C.MODELS[k]["name"])}</h3><p class="meta">{esc(C.MODELS[k]["term"])}</p>'
        f'<p class="small">{esc(C.MODELS[k]["what"])}</p></div>'
        for k in ['sprint', 'pilot', 'pod', 'extension']
    )
    inds = ''.join(
        f'<a class="feature" href="{rel(p, "industries.html#" + i["id"])}"><h3 class="h4">{esc(i["name"])}</h3>'
        f'<p class="small">{esc(i["intro"])}</p></a>'
        for i in C.INDUSTRIES
    )
    why = ''.join(f'<div class="feature"><h3 class="h4">{esc(t)}</h3><p class="small">{esc(d)}</p></div>' for t, d in H['why'])
    org = {
        '@context': 'https://schema.org', '@type': 'Organization', 'name': 'Otorithm',
        'legalName': C.SITE['legal'], 'url': C.SITE['domain'], 'email': C.SITE['email'],
        'address': {'@type': 'PostalAddress', 'addressLocality': 'Gurugram', 'addressRegion': 'Haryana', 'addressCountry': 'IN'},
        'description': C.SITE['tagline'],
    }
    pills = ''.join(f'<a class="pill" href="{rel(p, h)}">{esc(t)}</a>' for t, h in H['pills'])
    hv = C.SITE['hero_video']
    asset = lambda name: rel(p, f'assets/{name}') + f'?v={VERSIONS[name]}'
    v_src, v_poster = asset(f"videos/{hv['file']}.mp4"), asset(f"videos/{hv['file']}.jpg")
    # Hero particle logo: larger formation and a stronger, swirling response to the cursor
    particles = ('<div class="hero-visual" aria-hidden="true">'
                 '<canvas data-formation="ligature" data-ambient="30" data-fill="0.9" '
                 'data-radius="150" data-force="62" data-swirl="0.45" data-ease="0.075"></canvas></div>') if hv['particles'] else ''
    hero_cls = 'hero has-particles' if hv['particles'] else 'hero'
    body = f'''<section class="{hero_cls}" style="--video-opacity: {hv['opacity']}">
  <video class="hero-media" id="hero-video" src="{v_src}" poster="{v_poster}" muted loop playsinline preload="auto" aria-hidden="true" tabindex="-1"></video>
  <div class="hero-scrim" aria-hidden="true"></div>
  <div class="wrap hero-inner">
    <div class="hero-copy">
      <p class="label">{esc(H['label'])}</p>
      <h1 class="display">{esc(H['title'])}</h1>
      <div class="agent">
        <p class="agent-intro" aria-hidden="true">{esc(H['agent_intro'][0])}<br>{esc(H['agent_intro'][1])}</p>
        <p class="typed" data-typewriter="{esc(H['typed'])}"><span class="sr-only">{esc(H['typed'])}</span><span class="typed-text" aria-hidden="true"></span><span class="cursor" aria-hidden="true"></span></p>
      </div>
      <div class="pills">
        {pills}
        <button type="button" class="pill outline" data-copy="{esc(C.SITE['email'])}"><span data-copy-label>Reach us: {esc(C.SITE['email'])}</span>{COPY_ICON}</button>
      </div>
    </div>
    {particles}
  </div>
  <button type="button" class="video-toggle" id="video-toggle" aria-pressed="false">Pause background</button>
</section>

'''
    body += f'''<section class="section ruled">
  <div class="wrap">
    {sec_head(H['diff_label'], H['diff_title'], H['diff_body'])}
    <ol class="loop">{loop}</ol>
    <div style="margin-top: 40px">{ghost(rel(p, 'approach.html'), 'How our delivery loop works')}</div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap">
    {sec_head('What we do', 'Six services, one way of working.', 'Build new AI products and platforms, transform the processes and systems you already have, or extend your team with senior engineers. Every service runs on the same AI-native delivery model.')}
    <div class="rows">{svc_rows}</div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap">
    {sec_head('Ways to engage', 'Start small. Scale when it works.', 'Most relationships begin with a fixed-scope piece of work and grow from there. Every model is monthly or fixed-fee, with no long lock-in.')}
    <div class="features">{models}</div>
    <div style="margin-top: 40px">{ghost(rel(p, 'approach.html#models'), 'Compare engagement models')}</div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap">
    {sec_head('Industries', 'Built for regulated, high-volume businesses.', 'We work where correctness, scale and audit trails matter: money movement, marketplaces, enterprise software and operations-heavy businesses.')}
    <div class="features three">{inds}</div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap split">
    <div class="stack-sm"><p class="label">Why Otorithm</p><h2 class="h2">Senior by default. Accountable by design.</h2></div>
    <div class="features">{why}</div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap">
    {sec_head('Insights', 'Field notes from production.', 'How we think about AI engineering, modernization and the way engineering teams are changing.')}
    {article_rows(p, C.ARTICLES)}
  </div>
</section>

{cta_band(p)}'''
    # One full-width image band at the top of each main section, in page order
    for key in ['home-different', 'home-services', 'home-engage', 'home-industries', 'home-why', 'home-insights']:
        marker = '<section class="section ruled">'
        assert marker in body, key
        body = body.replace(marker, f'<section class="section ruled has-band">\n  {band(p, key)}', 1)
    extra = f'<script type="application/ld+json">{json.dumps(org)}</script>'
    return body, extra


def page_services(p):
    groups = ''
    intros = {
        'Build': 'New AI products and the platforms they run on.',
        'Transform': 'Change how existing processes and systems work, with AI doing the heavy lifting.',
        'Extend': 'Senior engineers inside your organization, accountable for outcomes or capacity.',
    }
    for g, slugs in C.SERVICE_GROUPS:
        rows = ''.join(
            f'''<a class="row" href="{rel(p, svc_path(s))}">
  <h3 class="h3">{esc(C.SERVICES[s]['name'])}</h3>
  <div><p class="small">{esc(C.SERVICES[s]['short'])}</p><div class="row-meta"><span class="meta">{esc(C.SERVICES[s]['start'])}</span></div></div>
  {ARROW}
</a>''' for s in slugs
        )
        groups += f'''<section class="section tight">
  <div class="wrap">
    <div class="sec-head"><div class="stack-sm"><p class="label">{esc(g)}</p></div><p class="body">{esc(intros[g])}</p></div>
    <div class="rows">{rows}</div>
  </div>
</section>'''
    chooser = ''.join(
        f'<tr><td>{esc(sit)}</td><td><a class="ghost" href="{rel(p, svc_path(s))}">{esc(C.SERVICES[s]["name"])} {ARROW}</a></td></tr>'
        for sit, s in C.CHOOSER
    )
    body = page_hero(
        p, 'Services', 'From first AI pilot to the platform it runs on.',
        'Six services, one delivery model. Pick the one that matches where you are today. Most clients combine two as the work grows.',
        formation='pods',
    ) + groups + f'''
<section class="section ruled">
  <div class="wrap">
    {sec_head('Not sure where to start?', 'Start from the situation you are in.')}
    <div class="table-wrap"><table class="table">
      <thead><tr><th scope="col">If this sounds like you</th><th scope="col">Start with</th></tr></thead>
      <tbody>{chooser}</tbody>
    </table></div>
  </div>
</section>
<section class="section ruled">
  <div class="wrap">
    {sec_head('Engagement models', 'Fixed scope or monthly. Your choice.', 'Every service can start small. Models can change as the work does.')}
    {models_table(C.MODEL_ORDER)}
  </div>
</section>
''' + cta_band(p)
    return body, ''


def page_service(p, slug):
    S = C.SERVICES[slug]
    g = svc_group(slug)
    deliver = ''.join(f'<div class="feature"><h3 class="h4">{esc(t)}</h3><p class="small">{esc(d)}</p></div>' for t, d in S['deliver'])
    phases = ''.join(
        f'''<div class="phase"><span class="label">{i:02d}</span>
  <div class="stack-sm" style="gap: 4px"><h3 class="h4">{esc(n)}</h3><span class="when">{esc(w)}</span></div>
  <p class="small">{esc(d)}</p></div>'''
        for i, (n, w, d) in enumerate(S['phases'], 1)
    )
    ai = ''.join(f'<div class="feature"><h3 class="h4">{esc(t)}</h3><p class="small">{esc(d)}</p></div>' for t, d in S['ai'])
    outcomes = ''.join(f'<li>{esc(o)}</li>' for o in S['outcomes'])
    models = ''.join(
        f'''<div class="row two"><div class="stack-sm" style="gap: 4px"><h3 class="h4">{esc(C.MODELS[k]['name'])}</h3><span class="meta">{esc(C.MODELS[k]['term'])}</span></div>
  <p class="small">{esc(C.MODELS[k]['what'])}</p></div>'''
        for k in S['models']
    )
    faqs = ''.join(
        f'<details><summary>{esc(q)}<span class="plus" aria-hidden="true"></span></summary><div class="answer"><p class="small">{esc(a)}</p></div></details>'
        for q, a in S['faqs']
    )
    related = ''.join(
        f'''<a class="row" href="{rel(p, svc_path(r))}">
  <div class="stack-sm"><p class="label">{esc(svc_group(r))}</p><h3 class="h3">{esc(C.SERVICES[r]['name'])}</h3></div>
  <p class="small">{esc(C.SERVICES[r]['short'])}</p>
  {ARROW}
</a>''' for r in S['related']
    )
    actions = f'<a href="{rel(p, "contact.html")}" class="btn">Talk to us</a>{ghost("#how", "How it runs")}'
    body = page_hero(
        p, None, S['title'], S['lead'], formation=S['formation'], actions=actions,
        crumb=[('Services', 'services.html'), (S['name'], None)],
    ) + f'''
<section class="section ruled">
  <div class="wrap">
    {sec_head(g, S['deliver_title'])}
    <div class="features three">{deliver}</div>
  </div>
</section>

<section class="section ruled" id="how">
  <div class="wrap">
    {sec_head('How it runs', 'From first week to handover.', 'Durations are typical. We agree the actual plan with you during scoping.')}
    <div class="phases">{phases}</div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap">
    {sec_head('AI in the loop', S['ai_title'])}
    <div class="features">{ai}</div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap split">
    <div class="stack"><p class="label">{esc(S['outcomes_title'])}</p><ul class="ticks paper">{outcomes}</ul></div>
    <div class="stack"><p class="label">Ways to engage</p><div class="rows">{models}</div>
      <div>{ghost(rel(p, 'approach.html#models'), 'All engagement models')}</div></div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap split">
    <div class="stack-sm"><p class="label">FAQ</p><h2 class="h2">Questions we hear.</h2></div>
    <div class="faq">{faqs}</div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap">
    {sec_head('Related', 'Often paired with.')}
    <div class="rows">{related}</div>
  </div>
</section>
''' + cta_band(p)
    return body, ''


def page_industries(p):
    jump = '<div class="tags">' + ''.join(f'<a class="tag" href="#{i["id"]}">{esc(i["name"])}</a>' for i in C.INDUSTRIES) + '</div>'
    blocks = ''.join(
        f'''<div class="block" id="{i['id']}">
  <div class="stack-sm"><h2 class="h3">{esc(i['name'])}</h2><p class="small">{esc(i['intro'])}</p></div>
  <div class="cols">
    <div><p class="col-title">What we build</p><ul class="ticks">{''.join(f'<li>{esc(x)}</li>' for x in i['build'])}</ul></div>
    <div><p class="col-title">Where AI helps</p><ul class="ticks">{''.join(f'<li>{esc(x)}</li>' for x in i['ai'])}</ul></div>
  </div>
</div>''' for i in C.INDUSTRIES
    )
    body = page_hero(
        p, 'Industries', 'Built for businesses where mistakes are expensive.',
        'We work in industries with high transaction volumes, real regulatory obligations and processes that still depend on documents and manual checks. That is where careful engineering and practical AI pay off fastest.',
        formation='ligature', actions=jump,
    ) + f'''
<section class="section">
  <div class="wrap">{blocks}</div>
</section>
''' + cta_band(p, 'Working in another industry?', 'The engineering transfers. Tell us about your workflows and constraints and we will say plainly whether we are a fit.')
    return body, ''


def page_approach(p):
    loop = ''.join(
        f'<li><span class="num">{i:02d}</span><h3 class="h4">{esc(t)}</h3><p class="small">{esc(d)}</p></li>'
        for i, (t, d) in enumerate(C.LOOP, 1)
    )
    principles = ''.join(
        f'<div class="row two"><h3 class="h4">{esc(t)}</h3><p class="small">{esc(d)}</p></div>' for t, d in C.PRINCIPLES
    )
    life = ''.join(
        f'<li><span class="num">{i:02d}</span><h3 class="h4">{esc(n)}</h3><p class="small">{esc(d)}</p>'
        f'<p class="small" style="color: var(--fg)">You get: {esc(g)}</p></li>'
        for i, (n, d, g) in enumerate(C.LIFECYCLE, 1)
    )
    security = ''.join(
        f'<div class="row two"><h3 class="h4">{esc(t)}</h3><p class="small">{esc(d)}</p></div>' for t, d in C.SECURITY
    )
    tz = ''.join(f'<tr><td>{esc(r)}</td><td class="term">{esc(z)}</td><td>{esc(o)}</td></tr>' for r, z, o in C.TIMEZONES)
    body = page_hero(
        p, 'Approach', 'How we deliver with AI in the loop.',
        'Our delivery model was designed around AI from the start. Senior engineers set direction and own the result, agents take on drafting, testing and documentation, and every change passes the same gates whoever wrote it.',
        formation='cycle',
    ) + f'''
<section class="section ruled">
  <div class="wrap">
    {sec_head('The delivery loop', 'Five steps, on every change.', 'The loop runs at every scale, from a single pull request to a quarterly release. AI is involved at every step, and an engineer is accountable at every step.')}
    <ol class="loop">{loop}</ol>
  </div>
</section>

<section class="section ruled">
  <div class="wrap split">
    <div class="stack-sm"><p class="label">Principles</p><h2 class="h2">What does not change, whatever the tools.</h2></div>
    <div class="rows">{principles}</div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap">
    {sec_head('Engagement lifecycle', 'How an engagement runs.', 'The same four stages, whether the work is a three-week assessment or a year-long programme.')}
    <ol class="loop four">{life}</ol>
  </div>
</section>

<section class="section ruled" id="models">
  <div class="wrap">
    {sec_head('Engagement models', 'Ways to work with us.', 'Fixed-fee for defined questions, monthly for ongoing work. Every model can change as the work does.')}
    {models_table(C.MODEL_ORDER)}
  </div>
</section>

<section class="section ruled" id="security">
  <div class="wrap split">
    <div class="stack-sm"><p class="label">Security and data</p><h2 class="h2">Safe to let in.</h2><p class="body">Engineers working inside your systems need clear rules. These are agreed in writing before work starts.</p></div>
    <div class="rows">{security}</div>
  </div>
</section>

<section class="section ruled" id="time-zones">
  <div class="wrap">
    {sec_head('Time zones', 'Working hours that overlap yours.', 'Our engineers work from India. Schedules are agreed per engagement so the overlap lands where your team needs it.')}
    <div class="table-wrap"><table class="table">
      <thead><tr><th scope="col">Your team in</th><th scope="col">Time zone</th><th scope="col">Typical overlap</th></tr></thead>
      <tbody>{tz}</tbody>
    </table></div>
  </div>
</section>
''' + cta_band(p)
    return body, ''


def page_work(p):
    jump = '<div class="tags">' + ''.join(f'<a class="tag" href="#{b["id"]}">{esc(b["title"])}</a>' for b in C.BLUEPRINTS) + '</div>'
    blocks = ''
    for b in C.BLUEPRINTS:
        tags = ''.join(f'<a class="tag" href="{rel(p, svc_path(s))}">{esc(C.SERVICES[s]["name"])}</a>' for s in b['services'])
        tl = ''.join(f'<div class="tl"><span class="when">{esc(w)}</span><p>{esc(t)}</p></div>' for w, t in b['steps'])
        end = ''.join(f'<li>{esc(x)}</li>' for x in b['end'])
        blocks += f'''<div class="block" id="{b['id']}">
  <div class="stack">
    <div class="tags">{tags}</div>
    <h2 class="h3">{esc(b['title'])}</h2>
    <div class="stack-sm"><p class="col-title" style="margin: 0">Fits when</p><p class="small">{esc(b['fits'])}</p></div>
  </div>
  <div class="stack">
    <div class="timeline">{tl}</div>
    <div><p class="col-title">You end with</p><ul class="ticks">{end}</ul></div>
  </div>
</div>'''
    body = page_hero(
        p, 'Work', 'What an engagement looks like.',
        'Every engagement is shaped to the problem, but most follow one of a few patterns. These blueprints show how each one runs and what you have at the end. Talk to us about the one closest to your situation.',
        formation='bridge', actions=jump,
    ) + f'''
<section class="section">
  <div class="wrap">{blocks}</div>
</section>
''' + cta_band(p, 'See your situation here?', 'Tell us which blueprint is closest and what is different about yours. We will come back with a plan.')
    return body, ''


def page_insights(p):
    body = page_hero(
        p, 'Insights', 'Field notes from production.',
        'How we think about AI engineering, modernization and engagement models, written by the engineers who do the work.',
    ) + f'''
<section class="section tight">
  <div class="wrap">{article_rows(p, C.ARTICLES)}</div>
</section>
''' + cta_band(p)
    return body, ''


def page_article(p, art):
    others = [a for a in C.ARTICLES if a['slug'] != art['slug']]
    rel_svcs = ''.join(
        f'<li><a href="{rel(p, svc_path(s))}">{esc(C.SERVICES[s]["name"])}</a></li>' for s in art['services']
    )
    body = f'''<section class="article-head">
  <div class="wrap stack">
    <div class="crumb"><a class="label" href="{rel(p, 'insights.html')}">Insights</a><span class="sep" aria-hidden="true">/</span><span class="label">{esc(art['topic'])}</span></div>
    <h1 class="h1">{esc(art['title'])}</h1>
    <p class="lead">{esc(art['summary'])}</p>
    <p class="meta">Otorithm Engineering · {art['minutes']} min read</p>
  </div>
</section>
<div class="wrap article-layout">
  <article class="prose">{art['html']}</article>
  <aside class="aside" aria-label="Related">
    <div class="foot-col"><h2>Related services</h2><ul>{rel_svcs}</ul></div>
    <div class="stack-sm"><p class="h4">Working on something like this?</p><p class="small">Talk to an engineer about your situation.</p>
      <div><a href="{rel(p, 'contact.html')}" class="btn btn-sm">Talk to us</a></div></div>
  </aside>
</div>
<section class="section ruled">
  <div class="wrap">
    {sec_head('More insights', 'Keep reading.')}
    {article_rows(p, others)}
  </div>
</section>'''
    ld = {
        '@context': 'https://schema.org', '@type': 'Article', 'headline': art['title'],
        'description': art['summary'], 'author': {'@type': 'Organization', 'name': 'Otorithm'},
        'publisher': {'@type': 'Organization', 'name': 'Otorithm'},
    }
    return body, f'<script type="application/ld+json">{json.dumps(ld)}</script>'


def page_about(p):
    A = C.ABOUT
    beliefs = ''.join(f'<div class="feature"><h3 class="h4">{esc(t)}</h3><p class="small">{esc(d)}</p></div>' for t, d in A['beliefs'])
    practices = ''.join(f'<div class="row two"><h3 class="h4">{esc(t)}</h3><p class="small">{esc(d)}</p></div>' for t, d in A['practices'])
    responsible = ''.join(f'<li>{esc(x)}</li>' for x in A['responsible'])
    details = ''.join(
        f'<div class="row two"><p class="col-title" style="margin: 0">{esc(k)}</p><p class="small" style="color: var(--fg)">{esc(v)}</p></div>'
        for k, v in [('Legal name', C.SITE['legal']), ('Brand', 'Otorithm'), ('Headquarters', C.SITE['city']),
                     ('Working hours', C.SITE['hours']), ('Contact', C.SITE['email'])]
    )
    body = page_hero(p, 'Company', A['title'], A['lead'], formation='layers') + f'''
<section class="section ruled">
  <div class="wrap">
    {sec_head('What we believe', 'How we think about the work.')}
    <div class="features">{beliefs}</div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap split">
    <div class="stack-sm"><p class="label">How we are organized</p><h2 class="h2">Practices, not departments.</h2>
      <p class="body">Engineers belong to a practice that sets standards, reviews designs and develops people. Every client engagement has a named engagement lead accountable for delivery.</p></div>
    <div class="rows">{practices}</div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap split">
    <div class="stack-sm"><p class="label">Where we work</p><h2 class="h2">One delivery centre, three markets.</h2></div>
    <div class="stack">
      <p class="body">Our delivery centre is in Gurugram, India. We work with clients across India, Europe and North America, with schedules arranged so engineers overlap the hours your team needs.</p>
      <div>{ghost(rel(p, 'approach.html#time-zones'), 'Time-zone overlap')}</div>
    </div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap split">
    <div class="stack-sm"><p class="label">Responsible AI</p><h2 class="h2">Our commitments.</h2>
      <p class="body">How we use AI in client work, in plain terms.</p></div>
    <ul class="ticks paper">{responsible}</ul>
  </div>
</section>

<section class="section ruled">
  <div class="wrap split">
    <div class="stack-sm"><p class="label">Company details</p><h2 class="h3">The essentials.</h2></div>
    <div class="rows">{details}</div>
  </div>
</section>
''' + cta_band(p, 'Work with us, or for us.', 'Clients start a conversation on the contact page. Engineers can see open roles on our careers page.').replace(
        f'<a href="{rel(p, "contact.html")}" class="btn">Talk to us</a>',
        f'<a href="{rel(p, "contact.html")}" class="btn">Talk to us</a>{ghost(rel(p, "careers.html"), "See careers")}',
    )
    return body, ''


def page_careers(p):
    K = C.CAREERS
    why = ''.join(f'<div class="feature"><h3 class="h4">{esc(t)}</h3><p class="small">{esc(d)}</p></div>' for t, d in K['why'])
    proc = ''.join(
        f'<li><span class="num">{i:02d}</span><h3 class="h4">{esc(t)}</h3><p class="small">{esc(d)}</p></li>'
        for i, (t, d) in enumerate(K['process'], 1)
    )
    roles = ''.join(
        f'''<div class="row two"><div class="stack-sm" style="gap: 4px"><h3 class="h4">{esc(r)}</h3><span class="meta">{esc(prac)} · {esc(loc)}</span></div>
  <p class="small">{esc(focus)}</p></div>''' for r, focus, prac, loc in K['roles']
    )
    body = page_hero(p, 'Careers', K['title'], K['lead'], formation='grid',
                     actions=f'<a href="#roles" class="btn">See open roles</a>') + f'''
<section class="section ruled">
  <div class="wrap">
    {sec_head('Why engineers join', 'Work worth doing well.')}
    <div class="features">{why}</div>
  </div>
</section>

<section class="section ruled">
  <div class="wrap">
    {sec_head('How we hire', 'Five steps, about two weeks.', 'We test the way you actually work. That includes how you use AI tools, and how you check what they produce.')}
    <ol class="loop">{proc}</ol>
  </div>
</section>

<section class="section ruled" id="roles">
  <div class="wrap split">
    <div class="stack"><div class="stack-sm"><p class="label">Open roles</p><h2 class="h2">Where we are hiring.</h2></div>
      <p class="body">Email your profile with the role in the subject line. If your role is not listed, send it anyway; we review every profile.</p>
      <div>{copy_btn(C.SITE['careers_email'])}</div>
      <p class="form-note">Otorithm never asks candidates for payment at any stage of hiring.</p></div>
    <div class="rows">{roles}</div>
  </div>
</section>'''
    return body, ''


def page_contact(p):
    opts = ''.join(f'<option>{esc(C.SERVICES[s]["name"])}</option>' for _, slugs in C.SERVICE_GROUPS for s in slugs)
    opts += '<option>Careers</option><option>Something else</option>'
    endpoint = f' data-endpoint="{esc(C.SITE["form_endpoint"])}"' if C.SITE['form_endpoint'] else ''
    next_steps = ''.join(
        f'<li><span class="num">{i:02d}</span><h3 class="h4">{esc(t)}</h3><p class="small">{esc(d)}</p></li>'
        for i, (t, d) in enumerate([
            ('Reply', 'An engineer reads your message and replies, usually within one business day.'),
            ('Conversation', 'A 30-minute call about the problem, your systems and your constraints.'),
            ('Proposal', 'A written proposal with options, timelines and pricing, usually within a week.'),
        ], 1)
    )
    body = page_hero(
        p, 'Contact', 'Tell us what you are building.',
        'Share a little about the problem. An engineer, not a sales team, will read it and reply.',
    ) + f'''
<section class="section tight">
  <div class="wrap split" style="align-items: start">
    <div class="stack">
      <form class="form" id="contact-form" novalidate{endpoint} data-email="{esc(C.SITE['email'])}">
        <div class="field"><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required placeholder="Your name"></div>
        <div class="field"><label for="f-email">Work email</label><input id="f-email" name="email" type="email" autocomplete="email" required placeholder="you@company.com"></div>
        <div class="field"><label for="f-company">Company</label><input id="f-company" name="company" autocomplete="organization" placeholder="Company name"></div>
        <div class="field"><label for="f-interest">Interested in</label><select id="f-interest" name="interest">{opts}</select></div>
        <div class="field full"><label for="f-message">What are you working on?</label><textarea id="f-message" name="message" required placeholder="The problem, the systems involved and any timelines."></textarea></div>
        <div class="full actions"><button type="submit" class="btn">Send message</button><span class="form-note">We use your details only to reply. See our privacy notice.</span></div>
      </form>
      <div class="notice" id="form-result" tabindex="-1" hidden></div>
    </div>
    <div class="stack" style="gap: 36px">
      <div class="rows">
        <div class="row two"><p class="col-title" style="margin: 0">New work</p><div>{copy_btn(C.SITE['email'])}</div></div>
        <div class="row two"><p class="col-title" style="margin: 0">Careers</p><div>{copy_btn(C.SITE['careers_email'])}</div></div>
        <div class="row two"><p class="col-title" style="margin: 0">Office</p><p class="small" style="color: var(--fg)">{esc(C.SITE['city'])}</p></div>
        <div class="row two"><p class="col-title" style="margin: 0">Hours</p><p class="small" style="color: var(--fg)">{esc(C.SITE['hours'])}</p></div>
      </div>
    </div>
  </div>
</section>
<section class="section ruled">
  <div class="wrap">
    {sec_head('What happens next', 'Three steps to a plan.')}
    <ol class="loop four" style="grid-template-columns: repeat(auto-fit, minmax(220px, 1fr))">{next_steps}</ol>
  </div>
</section>'''
    return body, ''


def page_privacy(p):
    body = f'''<section class="article-head">
  <div class="wrap stack">
    <p class="label">Legal</p>
    <h1 class="h1">Privacy notice</h1>
    <p class="meta">Last updated 1 October 2026</p>
  </div>
</section>
<div class="wrap article-layout">
  <article class="prose">
    <p>This notice explains how {esc(C.SITE['legal'])} ("Otorithm", "we") handles personal data collected through otorithm.com.</p>
    <h2>What we collect</h2>
    <p>When you contact us, by email or through the contact form, we receive the details you choose to send: typically your name, work email, company and message. This website does not use advertising or analytics cookies and does not track you across other sites.</p>
    <h2>Why we use it</h2>
    <ul>
      <li>To reply to your enquiry and discuss a possible engagement.</li>
      <li>To consider job applications you send us.</li>
      <li>To meet legal, accounting and contractual obligations once we work together.</li>
    </ul>
    <h2>Legal basis</h2>
    <p>For visitors in the European Economic Area and the UK, we rely on our legitimate interest in responding to enquiries, on steps taken at your request before entering a contract, and on legal obligations. For visitors in India, we process data in line with the Digital Personal Data Protection Act, 2023, for the purpose you provided it.</p>
    <h2>Sharing and transfers</h2>
    <p>We do not sell personal data. We use service providers for email and hosting, who process data on our behalf. Data may be processed in India; where it is transferred from the EEA or UK, we use appropriate safeguards such as Standard Contractual Clauses.</p>
    <h2>How long we keep it</h2>
    <p>Enquiries that do not lead to an engagement are deleted within 24 months. Job applications are kept for up to 12 months unless you ask us to delete them sooner.</p>
    <h2>Your rights</h2>
    <p>You can ask to access, correct or delete your personal data, or object to how we use it, by emailing {esc(C.SITE['email'])}. You also have the right to complain to your local data protection authority.</p>
    <h2>Contact</h2>
    <p>{esc(C.SITE['legal'])}, {esc(C.SITE['city'])}. Email: {esc(C.SITE['email'])}.</p>
  </article>
</div>'''
    return body, ''


def page_404(p):
    links = ''.join(
        f'<a class="row" href="/{h}"><h2 class="h4">{l}</h2><span></span>{ARROW}</a>'
        for l, h in [('Home', ''), ('Services', 'services.html'), ('Insights', 'insights.html'), ('Contact', 'contact.html')]
    )
    body = f'''<section class="page-hero">
  <div class="wrap stack">
    <p class="label">404</p>
    <h1 class="h1">This page does not exist.</h1>
    <p class="lead">The link may be old, or the address may have a typo. These pages will get you back on track.</p>
    <div class="rows" style="max-width: 720px">{links}</div>
  </div>
</section>'''
    return body, ''


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def pages():
    out = [
        ('index.html', 'Otorithm | AI-native engineering consultancy',
         'Otorithm is an AI-native engineering consultancy: AI-first product engineering, forward-deployed engineers, legacy modernization, platform engineering and staff augmentation.',
         page_home, 'home'),
        ('services.html', 'Services | Otorithm',
         'AI-first product engineering, forward-deployed engineering, AI modernization of legacy workflows, platform and data engineering, AI consulting and staff augmentation.',
         page_services, 'services'),
    ]
    for slug, S in C.SERVICES.items():
        out.append((svc_path(slug), f"{S['name']} | Otorithm", S['short'], lambda p, s=slug: page_service(p, s), 'services'))
    out += [
        ('industries.html', 'Industries | Otorithm', 'Engineering and AI for fintech, financial services, marketplaces, B2B SaaS, logistics and healthcare operations.', page_industries, 'industries'),
        ('approach.html', 'Approach | Otorithm', 'How Otorithm delivers software with AI in the loop: the delivery loop, principles, engagement models, security and time zones.', page_approach, 'approach'),
        ('work.html', 'Work | Otorithm', 'Engagement blueprints: how Otorithm engagements run, week by week, and what you have at the end.', page_work, 'work'),
        ('insights.html', 'Insights | Otorithm', 'Field notes on AI engineering, legacy modernization and engagement models from Otorithm engineers.', page_insights, 'insights'),
        ('about.html', 'About | Otorithm', 'Otorithm is an AI-native software engineering consultancy for product companies and enterprises in India, Europe and North America.', page_about, 'about'),
        ('careers.html', 'Careers | Otorithm', 'Senior engineering roles at Otorithm: backend, AI, forward-deployed, data, frontend and platform engineering.', page_careers, 'careers'),
        ('contact.html', 'Contact | Otorithm', 'Tell Otorithm what you are building. An engineer will reply.', page_contact, 'contact'),
        ('privacy.html', 'Privacy notice | Otorithm', 'How Otorithm handles personal data collected through otorithm.com.', page_privacy, None),
        ('404.html', 'Page not found | Otorithm', 'This page does not exist.', page_404, None),
    ]
    for a in C.ARTICLES:
        out.append((f"insights/{a['slug']}.html", f"{a['title']} | Otorithm", a['summary'], lambda p, art=a: page_article(p, art), 'insights'))
    return out


def main():
    artifact = '--artifact' in sys.argv
    VERSIONS.update(asset_versions())
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, 'assets'))
    for name in ASSETS + video_assets():
        os.makedirs(os.path.dirname(os.path.join(DIST, 'assets', name)), exist_ok=True)
        shutil.copy(os.path.join(ROOT, 'assets', name), os.path.join(DIST, 'assets', name))
    images = os.path.join(ROOT, 'assets', 'images')
    if os.path.isdir(images):
        shutil.copytree(images, os.path.join(DIST, 'assets', 'images'), ignore=shutil.ignore_patterns('.gitkeep'))

    built = []
    for path, title, desc, fn, active in pages():
        body, extra = fn(path)
        dest = os.path.join(DIST, path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(shell(path, title, desc, body, active, extra))
        built.append(path)
        if artifact and path == 'index.html':
            os.makedirs(os.path.join(ROOT, 'artifact'), exist_ok=True)
            with open(os.path.join(ROOT, 'artifact', 'index.html'), 'w', encoding='utf-8') as f:
                f.write(shell(path, title, desc, body, active, extra, artifact_index=True))

    urls = ''.join(
        f"  <url><loc>{C.SITE['domain']}/{'' if p == 'index.html' else p}</loc></url>\n"
        for p in built if p != '404.html'
    )
    with open(os.path.join(DIST, 'sitemap.xml'), 'w') as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    with open(os.path.join(DIST, 'robots.txt'), 'w') as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {C.SITE['domain']}/sitemap.xml\n")
    print(f'Built {len(built)} pages into dist/')


if __name__ == '__main__':
    main()
