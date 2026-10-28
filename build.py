#!/usr/bin/env python3
"""
Builds the Otorithm website into ./dist (static HTML, no dependencies beyond Python 3.8+).

  python3 build.py              # production build into dist/
  python3 build.py --artifact   # also writes artifact/index.html for the Claude preview

Copy lives in content.py; styles and scripts in assets/.

Besides the HTML pages, the build writes what search engines and AI assistants read:
sitemap.xml (with lastmod), robots.txt, llms.txt, llms-full.txt, a Markdown copy of every page
(<page>.md), an RSS feed for Insights, the web app manifest, /.well-known/security.txt and the
IndexNow key file. Page dates for the sitemap are tracked in lastmod.json: a page's date moves
only when its content changes. Run the build locally and commit lastmod.json with your edits.
"""
import datetime
import hashlib
import html
import json
import os
import posixpath
import re
import shutil
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin

import content as C

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
ASSETS = ['styles.css', 'site.js', 'constellation.js', 'favicon.svg']
ASSET_DIRS = ['images', 'og', 'icons', 'fonts']   # copied as-is into dist/assets/
LASTMOD = os.path.join(ROOT, 'lastmod.json')
TODAY = datetime.date.today().isoformat()
DOMAIN = C.SITE['domain']
ROBOTS_DEFAULT = 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1'


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


def file_ver(path):
    """Short content hash for any file under the repo root, for cache-busting query strings."""
    with open(os.path.join(ROOT, path), 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


def page_url(p):
    """Canonical absolute URL of a built page."""
    return DOMAIN + '/' + ('' if p == 'index.html' else p)


def md_path(p):
    """The Markdown twin of a page: about.html -> about.md, index.html -> index.md."""
    return p[:-len('.html')] + '.md'


def og_image(m):
    """Absolute URL of the page's share image: its own if one was rendered, otherwise the default."""
    key = m.get('og') or 'default'
    path = f'assets/og/{key}.png'
    if not os.path.exists(os.path.join(ROOT, path)):
        path = 'assets/og/default.png'
    return f'{DOMAIN}/{path}?v={file_ver(path)}'


def human_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f'{d.day} {d.strftime("%B %Y")}'


ARROW ='<span class="arrow" aria-hidden="true">→</span>'
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
    linkedin = next((u for u in C.SITE.get('same_as', []) if 'linkedin.com' in u), '')
    linkedin = f'<li><a href="{esc(linkedin)}" rel="me noopener" target="_blank">LinkedIn</a></li>' if linkedin else ''
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
        {linkedin}
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


def page_hero(p, label, title, lead, formation=None, actions='', crumb=None, label_href=None, h1_prefix=None):
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
      <h1 class="h1">{f'<span class="sr-only">{esc(h1_prefix)}: </span>' if h1_prefix else ''}{esc(title)}</h1>
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


def faq_list(faqs):
    return ''.join(
        f'<details><summary>{esc(q)}<span class="plus" aria-hidden="true"></span></summary><div class="answer"><p class="small">{esc(a)}</p></div></details>'
        for q, a in faqs
    )


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
# ---------------------------------------------------------------------------
# Structured data (schema.org JSON-LD), one connected @graph per page
# ---------------------------------------------------------------------------
ORG_ID = DOMAIN + '/#organization'
SITE_ID = DOMAIN + '/#website'


def org_node():
    S = C.SITE
    services = [
        {'@type': 'Offer', 'itemOffered': service_ref(s)}
        for _, slugs in C.SERVICE_GROUPS for s in slugs
    ]
    node = {
        '@type': 'Organization', '@id': ORG_ID, 'name': S['name'], 'legalName': S['legal'],
        'alternateName': 'System One Technologies',
        'url': DOMAIN + '/', 'email': S['email'],
        'logo': {'@type': 'ImageObject', '@id': DOMAIN + '/#logo', 'url': DOMAIN + '/assets/icons/logo-512.png',
                 'contentUrl': DOMAIN + '/assets/icons/logo-512.png', 'width': 512, 'height': 512, 'caption': 'Otorithm'},
        'image': {'@id': DOMAIN + '/#logo'},
        'description': S['tagline'],
        'slogan': C.HOME['title'],
        'address': {'@type': 'PostalAddress', 'addressLocality': 'Gurugram', 'addressRegion': 'Haryana', 'addressCountry': 'IN'},
        'areaServed': S['area_served'],
        'knowsAbout': S['knows_about'],
        'contactPoint': [
            {'@type': 'ContactPoint', 'contactType': 'sales', 'email': S['email'], 'availableLanguage': ['English'],
             'areaServed': S['area_served'], 'url': page_url('contact.html')},
            {'@type': 'ContactPoint', 'contactType': 'recruiting', 'email': S['careers_email'], 'availableLanguage': ['English'],
             'url': page_url('careers.html')},
        ],
        'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': 'Otorithm services', 'itemListElement': services},
    }
    if S.get('same_as'):
        node['sameAs'] = S['same_as']
    return node


def website_node():
    return {'@type': 'WebSite', '@id': SITE_ID, 'url': DOMAIN + '/', 'name': 'Otorithm', 'alternateName': 'otorithm.com',
            'description': C.SITE['tagline'], 'publisher': {'@id': ORG_ID}, 'inLanguage': 'en'}


def service_ref(slug):
    """A self-contained pointer to a service: enough to stand alone on pages that do not describe it."""
    url = page_url(svc_path(slug))
    return {'@type': 'Service', '@id': url + '#service', 'name': C.SERVICES[slug]['name'], 'url': url}


def faq_node_items(faqs, url):
    return [{'@type': 'Question', '@id': f'{url}#faq-{i}', 'name': q,
             'acceptedAnswer': {'@type': 'Answer', 'text': a}} for i, (q, a) in enumerate(faqs, 1)]


def service_node(slug):
    S = C.SERVICES[slug]
    url = page_url(svc_path(slug))
    return {'@type': 'Service', '@id': url + '#service', 'name': S['name'], 'serviceType': S['name'],
            'description': S['short'], 'url': url, 'provider': {'@id': ORG_ID}, 'areaServed': C.SITE['area_served'],
            'category': svc_group(slug), 'image': og_image({'og': f'service-{slug}'}),
            'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': S['deliver_title'],
                                'itemListElement': [{'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': t, 'description': d}}
                                                    for t, d in S['deliver']]}}


def structured_data(p, m):
    url = page_url(p)
    graph = [org_node(), website_node()]
    page = {'@type': m.get('type', 'WebPage'), '@id': url + '#webpage', 'url': url, 'name': m['title'],
            'description': m['desc'], 'isPartOf': {'@id': SITE_ID}, 'inLanguage': 'en',
            'primaryImageOfPage': {'@type': 'ImageObject', 'url': og_image(m), 'width': 1200, 'height': 630},
            'dateModified': m['lastmod']}
    if p in ('index.html', 'about.html'):
        page['about'] = {'@id': ORG_ID}
    if p == 'about.html':
        page['mainEntity'] = {'@id': ORG_ID}
    crumbs = m.get('crumbs') or []
    if crumbs:
        trail = [('Home', 'index.html')] + crumbs
        graph.append({'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': n, 'item': page_url(h)} for i, (n, h) in enumerate(trail, 1)]})
        page['breadcrumb'] = {'@id': url + '#breadcrumb'}
    faqs = m.get('faqs')
    if faqs:
        page['@type'] = [page['@type'], 'FAQPage'] if page['@type'] != 'FAQPage' else 'FAQPage'
        page['mainEntity'] = faq_node_items(faqs, url)
    if m.get('service'):
        graph.append(service_node(m['service']))
        page['about'] = {'@id': url + '#service'}
    if p == 'services.html':
        page['mainEntity'] = {'@type': 'ItemList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'item': {'@id': page_url(svc_path(s)) + '#service'}}
            for i, s in enumerate([s for _, slugs in C.SERVICE_GROUPS for s in slugs], 1)]}
        graph += [service_node(s) for _, slugs in C.SERVICE_GROUPS for s in slugs]
    if p == 'insights.html':
        page['mainEntity'] = {'@type': 'ItemList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'url': page_url(f"insights/{a['slug']}.html"), 'name': a['title']}
            for i, a in enumerate(C.ARTICLES, 1)]}
    art = m.get('article')
    if art:
        graph.append({
            '@type': 'BlogPosting', '@id': url + '#article', 'headline': art['title'], 'description': art['summary'],
            'datePublished': art['published'], 'dateModified': art['updated'], 'inLanguage': 'en',
            'author': {'@type': 'Organization', 'name': 'Otorithm Engineering', 'url': page_url('about.html'), 'parentOrganization': {'@id': ORG_ID}},
            'publisher': {'@id': ORG_ID}, 'image': og_image(m), 'mainEntityOfPage': {'@id': url + '#webpage'},
            'articleSection': art['topic'], 'keywords': art.get('keywords', []),
            'wordCount': len(re.sub('<[^>]+>', ' ', art['html']).split()),
            'about': [service_ref(s) for s in art['services']],
            'isAccessibleForFree': True,
        })
        page['mainEntity'] = {'@id': url + '#article'}
        page['datePublished'] = art['published']
    graph.append(page)
    return json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def shell(p, m, body, extra_head='', artifact_index=False):
    title, desc, active = m['title'], m['desc'], m.get('active')
    canonical = page_url(p)
    v = VERSIONS
    a = lambda name: rel(p, f'assets/{name}') + f'?v={v[name]}'
    f = lambda path: rel(p, path) + f'?v={file_ver(path)}'
    img = og_image(m)
    art = m.get('article')
    og_type = 'article' if art else 'website'
    article_meta = (f'<meta property="article:published_time" content="{art["published"]}">\n'
                    f'<meta property="article:modified_time" content="{art["updated"]}">\n'
                    f'<meta property="article:section" content="{esc(art["topic"])}">\n'
                    f'<meta property="article:author" content="Otorithm Engineering">\n') if art else ''
    verify = ''.join(
        f'<meta name="{n}" content="{esc(c)}">\n'
        for n, c in (('google-site-verification', C.SITE['verification'].get('google')),
                     ('msvalidate.01', C.SITE['verification'].get('bing'))) if c
    )
    md_link = (f'<link rel="alternate" type="text/markdown" href="{rel(p, md_path(p))}" title="{esc(title)} (Markdown)">\n'
               if m.get('markdown', True) else '')
    head = f'''<title>{esc('Otorithm Website' if artifact_index else title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{esc(m.get('robots') or ROBOTS_DEFAULT)}">
<link rel="canonical" href="{canonical}">
{md_link}<link rel="alternate" type="application/rss+xml" href="{rel(p, 'insights/feed.xml')}" title="Otorithm Insights">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Otorithm">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(title)}">
{article_meta}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{img}">
<meta name="twitter:image:alt" content="{esc(title)}">
{verify}<meta name="theme-color" content="#ffffff">
<meta name="author" content="Otorithm">
<link rel="icon" type="image/svg+xml" href="{a('favicon.svg')}">
<link rel="icon" type="image/png" sizes="48x48" href="{f('assets/icons/favicon-48.png')}">
<link rel="apple-touch-icon" href="{f('assets/icons/apple-touch-icon.png')}">
<link rel="manifest" href="{rel(p, 'manifest.json')}">
<link rel="preload" href="{rel(p, 'assets/fonts/sora-latin.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{a('styles.css')}">
<script type="application/ld+json">{structured_data(p, m)}</script>
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
  <video class="hero-media" id="hero-video" src="{v_src}" poster="{v_poster}" muted loop playsinline preload="metadata" aria-hidden="true" tabindex="-1"></video>
  <div class="hero-scrim" aria-hidden="true"></div>
  <div class="wrap hero-inner">
    <div class="hero-copy">
      <p class="label" aria-hidden="true">{esc(H['label'])}</p>
      <h1 class="display"><span class="sr-only">Otorithm: {esc(H['label'])}. </span>{esc(H['title'])}</h1>
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

<section class="section ruled" id="faq">
  <div class="wrap split">
    <div class="stack-sm"><p class="label">FAQ</p><h2 class="h2">Otorithm in brief.</h2>
      <p class="body">Straight answers to the questions we hear most about who we are and how we work.</p></div>
    <div class="faq">{faq_list(H['faq'])}</div>
  </div>
</section>

{cta_band(p)}'''
    # One full-width image band at the top of each main section, in page order
    for key in ['home-different', 'home-services', 'home-engage', 'home-industries', 'home-why', 'home-insights']:
        marker = '<section class="section ruled">'
        assert marker in body, key
        body = body.replace(marker, f'<section class="section ruled has-band">\n  {band(p, key)}', 1)
    # The video poster is the largest element in the first viewport: fetch it early
    extra = f'<link rel="preload" as="image" href="{v_poster}" fetchpriority="high">'
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
    faqs = faq_list(S['faqs'])
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
        crumb=[('Services', 'services.html'), (S['name'], None)], h1_prefix=S['name'],
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
    updated = (f' · Updated <time datetime="{art["updated"]}">{human_date(art["updated"])}</time>'
               if art['updated'] != art['published'] else '')
    takeaways = ''
    if art.get('takeaways'):
        takeaways = ('<aside class="takeaways" aria-label="Key takeaways"><p class="label">Key takeaways</p><ul>'
                     + ''.join(f'<li>{esc(t)}</li>' for t in art['takeaways']) + '</ul></aside>')
    body = f'''<section class="article-head">
  <div class="wrap stack">
    <div class="crumb"><a class="label" href="{rel(p, 'insights.html')}">Insights</a><span class="sep" aria-hidden="true">/</span><span class="label">{esc(art['topic'])}</span></div>
    <h1 class="h1">{esc(art['title'])}</h1>
    <p class="lead">{esc(art['summary'])}</p>
    <p class="meta">Otorithm Engineering · <time datetime="{art['published']}">{human_date(art['published'])}</time>{updated} · {art['minutes']} min read</p>
  </div>
</section>
<div class="wrap article-layout">
  <article class="prose">{takeaways}{art['html']}</article>
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
    return body, ''


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
    """Every page with its search metadata. Titles stay within ~60 characters and descriptions
    within ~160, so search results show them whole."""
    def pg(path, title, desc, fn, active=None, **m):
        return dict(path=path, title=title, desc=desc, fn=fn, active=active, **m)

    out = [
        pg('index.html', 'Otorithm | AI-Native Software Engineering Consultancy',
           'Otorithm builds AI products and agents, modernizes legacy systems and provides forward-deployed '
           'engineers and staff augmentation for India, Europe and the US.',
           page_home, 'home', faqs=C.HOME['faq']),
        pg('services.html', 'AI Engineering & Software Development Services | Otorithm',
           'AI product engineering, platform and data engineering, legacy modernization, AI consulting, '
           'forward-deployed engineers and staff augmentation.',
           page_services, 'services', type='CollectionPage', crumbs=[('Services', 'services.html')]),
    ]
    for slug, S in C.SERVICES.items():
        out.append(pg(svc_path(slug), S['seo_title'], S['seo_desc'], lambda p, s=slug: page_service(p, s), 'services',
                      crumbs=[('Services', 'services.html'), (S['name'], svc_path(slug))],
                      faqs=S['faqs'], service=slug, og=f'service-{slug}'))
    out += [
        pg('industries.html', 'Industries: Fintech, Banking, SaaS & Logistics | Otorithm',
           'AI and software engineering for fintech and payments, banking and financial services, marketplaces, '
           'B2B SaaS, logistics and healthcare operations.',
           page_industries, 'industries', crumbs=[('Industries', 'industries.html')]),
        pg('approach.html', 'How We Deliver Software with AI in the Loop | Otorithm',
           'How Otorithm delivers software with AI in the loop: the delivery loop, principles, engagement models, '
           'security, data protection and time-zone overlap.',
           page_approach, 'approach', crumbs=[('Approach', 'approach.html')]),
        pg('work.html', 'Engagement Blueprints: How Our Projects Run | Otorithm',
           'Week-by-week engagement blueprints: AI pilot to production, document digitization, legacy replacement, '
           'enterprise-ready SaaS, AI copilots and team extension.',
           page_work, 'work', crumbs=[('Work', 'work.html')]),
        pg('insights.html', 'Insights on AI Engineering & Modernization | Otorithm',
           'Field notes on AI engineering, LLM evals, legacy modernization and engagement models, written by '
           'Otorithm engineers.',
           page_insights, 'insights', type='CollectionPage', crumbs=[('Insights', 'insights.html')]),
        pg('about.html', 'About Otorithm | AI-Native Engineering Consultancy',
           'Otorithm is an AI-native software engineering consultancy for product companies and enterprises in '
           'India, Europe and North America, headquartered in Gurugram.',
           page_about, 'about', type='AboutPage', crumbs=[('About', 'about.html')]),
        pg('careers.html', 'Careers: Senior Engineering Roles in India | Otorithm',
           'Senior engineering roles at Otorithm in Gurugram and remote across India: backend, AI, forward-deployed, '
           'data, frontend and platform engineers.',
           page_careers, 'careers', crumbs=[('Careers', 'careers.html')]),
        pg('contact.html', 'Contact Otorithm | Talk to an Engineer',
           'Tell Otorithm what you are building. An engineer, not a sales team, replies, usually within one business '
           'day. Email contact@otorithm.com or use the form.',
           page_contact, 'contact', type='ContactPage', crumbs=[('Contact', 'contact.html')]),
        pg('privacy.html', 'Privacy Notice | Otorithm',
           'How System One Technologies Private Limited (Otorithm) handles personal data sent through otorithm.com, '
           "in line with GDPR and India's DPDP Act.",
           page_privacy, None, crumbs=[('Privacy notice', 'privacy.html')]),
        pg('404.html', 'Page not found | Otorithm', 'This page does not exist.', page_404, None,
           robots='noindex, follow', sitemap=False, markdown=False),
    ]
    for a in C.ARTICLES:
        path = f"insights/{a['slug']}.html"
        title = a['title'] if len(a['title']) > 49 else f"{a['title']} | Otorithm"
        out.append(pg(path, title, a['summary'], lambda p, art=a: page_article(p, art), 'insights',
                      crumbs=[('Insights', 'insights.html'), (a['title'], path)], article=a, og=f"insight-{a['slug']}"))
    too_long = [(m['path'], len(m['title']), len(m['desc'])) for m in out if len(m['title']) > 70 or len(m['desc']) > 160]
    assert not too_long, f'Shorten these titles (max 70) or descriptions (max 160): {too_long}'
    return out


# ---------------------------------------------------------------------------
# Markdown twins of each page, for AI assistants and LLM crawlers
# ---------------------------------------------------------------------------
class _Node:
    __slots__ = ('tag', 'attrs', 'children')

    def __init__(self, tag, attrs):
        self.tag, self.attrs, self.children = tag, dict(attrs), []


class _Tree(HTMLParser):
    VOID = {'br', 'img', 'input', 'meta', 'link', 'hr', 'source', 'wbr', 'col', 'area'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node('root', [])
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(_Node(tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


class Markdown:
    """Small HTML-to-Markdown converter for this site's own markup (not a general converter).
    Decorative and interactive parts (canvases, video, forms, aria-hidden elements, section labels)
    are dropped; copy-to-clipboard buttons become the value they copy; links become absolute."""
    SKIP = {'script', 'style', 'svg', 'canvas', 'video', 'form', 'select', 'textarea', 'noscript', 'figure', 'template', 'iframe', 'img', 'input'}
    SKIP_CLASSES = {'label', 'crumb', 'num', 'skip', 'plus', 'arrow', 'video-toggle', 'chev', 'band'}
    INLINE = {'a', 'strong', 'b', 'em', 'i', 'span', 'code', 'time', 'small', 'abbr', 'br', 'button', 'sup', 'sub', 'mark'}
    HEADINGS = {'h1': 1, 'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5, 'h6': 6}

    def __init__(self, page_path):
        self.base = page_url(page_path)

    def convert(self, html_text):
        t = _Tree()
        t.feed(html_text)
        out = '\n\n'.join(b for b in self.blocks(t.root) if b.strip())
        out = re.sub(r'\)\[', ') · [', out)          # adjacent links (pills, tags) get a separator
        return re.sub(r'\n{3,}', '\n\n', out).strip() + '\n'

    def skipped(self, n):
        if n.tag in self.SKIP or n.attrs.get('aria-hidden') == 'true' or n.attrs.get('hidden') is not None and 'hidden' in n.attrs:
            return True
        cls = set((n.attrs.get('class') or '').split())
        if n.tag == 'button' and 'data-copy' in n.attrs:
            return False
        if n.tag == 'button':
            return True
        if cls & self.SKIP_CLASSES and 'sr-only' not in cls:
            return n.tag != 'p' or 'label' in cls
        return False

    def href(self, h):
        if not h:
            return ''
        if h.startswith(('http://', 'https://', 'mailto:', 'tel:')):
            return h
        return urljoin(self.base, h).replace('/index.html', '/')

    def is_block(self, n):
        return isinstance(n, _Node) and n.tag not in self.INLINE

    def has_block(self, n):
        return any(isinstance(c, _Node) and (self.is_block(c) and not self.skipped(c) or self.has_block(c)) for c in n.children)

    def inline(self, n):
        if isinstance(n, str):
            return re.sub(r'\s+', ' ', n)
        if self.skipped(n):
            return ''
        if n.tag == 'br':
            return '\n'
        if n.tag == 'button':   # copy-to-clipboard button: its visible label, e.g. the email address
            label = re.sub(r'\s+', ' ', ''.join(self.inline(c) for c in n.children)).strip()
            return ' ' + (label or n.attrs.get('data-copy', '')) + ' '
        inner = ''.join(self.inline(c) for c in n.children)
        if n.tag in ('strong', 'b'):
            return f'**{inner.strip()}**' if inner.strip() else ''
        if n.tag in ('em', 'i'):
            return f'_{inner.strip()}_' if inner.strip() else ''
        if n.tag == 'code':
            return f'`{inner}`'
        if n.tag == 'a':
            text, url = inner.strip(), self.href(n.attrs.get('href'))
            return f'[{text}]({url})' if text and url else text
        if self.is_block(n):
            return ' ' + inner + ' '
        return inner

    def text(self, n):
        return re.sub(r'[ \t]+', ' ', self.inline(n)).strip()

    def blocks(self, n):
        out, run = [], []

        def flush():
            s = re.sub(r'[ \t]+', ' ', ''.join(run)).strip()
            if s:
                out.append(s)
            run.clear()

        kids = [c for c in n.children if not (isinstance(c, str) and not c.strip())]
        for i, c in enumerate(kids):
            if isinstance(c, str) or not self.is_block(c) and not (c.tag == 'a' and self.has_block(c)):
                run.append(self.inline(c))
                continue
            flush()
            if c.tag == 'p' and 'label' in (c.attrs.get('class') or '').split():
                nxt = next((k for k in kids[i + 1:] if isinstance(k, _Node)), None)
                if nxt is None or nxt.tag not in self.HEADINGS:
                    t = ''.join(self.inline(x) for x in c.children).strip()
                    if t:
                        out.append(f'**{t}**')
                continue
            out.extend(self.block(c))
        flush()
        return out

    def block(self, n):
        if self.skipped(n):
            return []
        tag = n.tag
        if tag in self.HEADINGS:
            t = self.text(n)
            return [f"{'#' * self.HEADINGS[tag]} {t}"] if t else []
        if tag == 'a':   # a card-style link wrapping a heading and text
            url = self.href(n.attrs.get('href'))
            inner = self.blocks(n)
            for i, b in enumerate(inner):
                if b.startswith('#'):
                    hashes, _, t = b.partition(' ')
                    inner[i] = f'{hashes} [{t}]({url})'
                    return inner
            return [f'[{inner[0]}]({url})'] + inner[1:] if inner else []
        if tag in ('ul', 'ol'):
            items = [c for c in n.children if isinstance(c, _Node) and c.tag == 'li' and not self.skipped(c)]
            lines = []
            for i, li in enumerate(items, 1):
                parts = []
                for b in self.blocks(li):
                    parts.append(f"**{b.lstrip('#').strip()}**:" if b.startswith('#') else b.replace('\n', ' '))
                item = ' '.join(parts).rstrip(':')
                lines.append(f"{f'{i}.' if tag == 'ol' else '-'} {item}")
            return ['\n'.join(lines)] if lines else []
        if tag == 'table':
            rows = []
            for tr in self.find(n, 'tr'):
                cells = [self.text(c).replace('|', '\\|') for c in tr.children if isinstance(c, _Node) and c.tag in ('th', 'td')]
                if cells:
                    rows.append(cells)
            if not rows:
                return []
            w = max(len(r) for r in rows)
            rows = [r + [''] * (w - len(r)) for r in rows]
            lines = ['| ' + ' | '.join(rows[0]) + ' |', '|' + '---|' * w] + ['| ' + ' | '.join(r) + ' |' for r in rows[1:]]
            return ['\n'.join(lines)]
        if tag == 'details':
            summary = next((c for c in n.children if isinstance(c, _Node) and c.tag == 'summary'), None)
            q = self.text(summary) if summary else ''
            rest = [b for c in n.children if isinstance(c, _Node) and c.tag != 'summary' for b in self.block(c)]
            return ([f'**{q}**'] if q else []) + rest
        if tag == 'blockquote':
            return ['\n'.join('> ' + line for b in self.blocks(n) for line in b.split('\n'))]
        if tag == 'tr':
            return [' · '.join(self.text(c) for c in n.children if isinstance(c, _Node))]
        return self.blocks(n)

    def find(self, n, tag):
        for c in n.children:
            if isinstance(c, _Node):
                if c.tag == tag:
                    yield c
                else:
                    yield from self.find(c, tag)


def page_markdown(m, body):
    url = page_url(m['path'])
    front = [
        '---', f"title: {json.dumps(m['title'], ensure_ascii=False)}", f"description: {json.dumps(m['desc'], ensure_ascii=False)}",
        f'url: {url}', f"last_updated: {m['lastmod']}",
    ]
    art = m.get('article')
    if art:
        front += [f"published: {art['published']}", f"author: Otorithm Engineering"]
    front += ['source: Otorithm (otorithm.com), System One Technologies Private Limited', '---', '']
    md = Markdown(m['path']).convert(body)
    if art and art.get('takeaways'):
        pass  # takeaways are part of the article markup and come through the converter
    return '\n'.join(front) + md


# ---------------------------------------------------------------------------
# Files for crawlers and assistants
# ---------------------------------------------------------------------------
AI_CRAWLERS = [
    # Search engines (their AI answers draw on these indexes)
    'Googlebot', 'Bingbot', 'Applebot', 'DuckDuckBot', 'YandexBot',
    # AI search and assistants fetching pages to answer and cite
    'OAI-SearchBot', 'ChatGPT-User', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Perplexity-User',
    'DuckAssistBot', 'MistralAI-User', 'meta-externalfetcher', 'Meta-WebIndexer', 'YouBot',
    # Model training (lets future models know who Otorithm is)
    'GPTBot', 'ClaudeBot', 'Google-Extended', 'Applebot-Extended', 'meta-externalagent', 'Amazonbot',
    'CCBot', 'cohere-ai', 'Bytespider',
]


def robots_txt():
    agents = '\n'.join(f'User-agent: {a}' for a in AI_CRAWLERS)
    return f'''# otorithm.com: search engines and AI assistants are welcome to crawl, index, cite and learn from this site.
# A Markdown copy of every page sits next to it (index.md, services.md, ...), listed in /llms.txt.

User-agent: *
Content-Signal: search=yes, ai-input=yes, ai-train=yes
Allow: /

# Named explicitly so the intent is unambiguous for each crawler
{agents}
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
'''


def llms_txt(built):
    S, H = C.SITE, C.HOME
    by = {m['path']: m for m in built}

    def link(path, title=None, note=None):
        m = by[path]
        return f"- [{title or m['title'].split(' | ')[0]}]({DOMAIN}/{md_path(path)}): {note or m['desc']}"

    svc_lines = '\n'.join(link(svc_path(s), C.SERVICES[s]['name'], C.SERVICES[s]['short'])
                          for _, slugs in C.SERVICE_GROUPS for s in slugs)
    art_lines = '\n'.join(link(f"insights/{a['slug']}.html", a['title'], a['summary']) for a in C.ARTICLES)
    models = '; '.join(f"{v['name']} ({v['term']})" for k, v in C.MODELS.items())
    inds = ', '.join(i['name'] for i in C.INDUSTRIES)
    return f'''# Otorithm

> Otorithm is an AI-native software engineering consultancy headquartered in Gurugram, India, and a brand of {S['legal']}. It builds AI products and agents, modernizes legacy systems and workflows, and provides forward-deployed engineering pods and senior staff augmentation for product companies and enterprises in India, Europe and North America. Senior engineers lead every engagement, and AI is used throughout delivery, with a named engineer reviewing and owning every change.

Key facts:

- Website: {DOMAIN}/ (every page also has a Markdown version: replace .html with .md; the home page is {DOMAIN}/index.md)
- Contact: {S['email']} (new work), {S['careers_email']} (careers); hours {S['hours']}
- Headquarters and delivery centre: {S['city']}
- Services: {', '.join(C.SERVICES[s]['name'] for _, slugs in C.SERVICE_GROUPS for s in slugs)}
- AI automation: AI agents and automated workflows for document intake, approvals, data entry, reconciliation and support triage
- Engagement models: {models}
- Industries: {inds}
- Markets: India, Europe and the UK, North America, Middle East, with working-hour overlap agreed per engagement
- Data and IP: code in the client's repositories and cloud; client data never trains models; NDAs and IP assignment in every contract; GDPR and India DPDP Act aligned

## Company

{link('index.html', 'Home', 'What Otorithm does, how it is different, services, engagement models, industries and an FAQ.')}
{link('about.html', 'About')}
{link('approach.html', 'Approach')}
{link('industries.html', 'Industries')}
{link('work.html', 'Engagement blueprints')}
{link('contact.html', 'Contact')}

## Services

{link('services.html', 'All services', 'The six services, a guide to choosing one, and engagement models compared.')}
{svc_lines}

## Insights

{art_lines}

## Optional

{link('careers.html', 'Careers')}
{link('privacy.html', 'Privacy notice')}
- [Everything above in one file]({DOMAIN}/llms-full.txt): the full text of every page, in Markdown.
'''


def rss_xml(built):
    items = ''
    for m in [m for m in built if m.get('article')]:
        a, url = m['article'], page_url(m['path'])
        pub = datetime.datetime.fromisoformat(a['published']).strftime('%a, %d %b %Y 09:00:00 +0530')
        items += (f'  <item>\n    <title>{esc(a["title"])}</title>\n    <link>{url}</link>\n    <guid isPermaLink="true">{url}</guid>\n'
                  f'    <pubDate>{pub}</pubDate>\n    <category>{esc(a["topic"])}</category>\n    <description>{esc(a["summary"])}</description>\n  </item>\n')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>Otorithm Insights</title>
  <link>{page_url('insights.html')}</link>
  <atom:link href="{DOMAIN}/insights/feed.xml" rel="self" type="application/rss+xml"/>
  <description>Field notes on AI engineering, modernization and engagement models from Otorithm engineers.</description>
  <language>en</language>
{items}</channel>
</rss>
'''


def sitemap_xml(built):
    urls = ''.join(
        f"  <url><loc>{page_url(m['path'])}</loc><lastmod>{m['lastmod']}</lastmod></url>\n"
        for m in built if m.get('sitemap', True)
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


def manifest_json():
    return json.dumps({
        'name': 'Otorithm', 'short_name': 'Otorithm', 'description': C.SITE['tagline'], 'start_url': '/',
        'display': 'browser', 'background_color': '#ffffff', 'theme_color': '#ffffff',
        'icons': [{'src': '/assets/icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
                  {'src': '/assets/icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
                  {'src': '/assets/favicon.svg', 'sizes': 'any', 'type': 'image/svg+xml'}],
    }, indent=2) + '\n'


def security_txt():
    expires = (datetime.date.today() + datetime.timedelta(days=365)).isoformat()
    return (f"Contact: mailto:{C.SITE['email']}\nExpires: {expires}T00:00:00.000Z\nPreferred-Languages: en\n"
            f"Canonical: {DOMAIN}/.well-known/security.txt\n")


def load_lastmod():
    try:
        with open(LASTMOD) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def main():
    artifact = '--artifact' in sys.argv
    VERSIONS.update(asset_versions())
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, 'assets'))
    for name in ASSETS + video_assets():
        os.makedirs(os.path.dirname(os.path.join(DIST, 'assets', name)), exist_ok=True)
        shutil.copy(os.path.join(ROOT, 'assets', name), os.path.join(DIST, 'assets', name))
    for d in ASSET_DIRS:
        src = os.path.join(ROOT, 'assets', d)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(DIST, 'assets', d), ignore=shutil.ignore_patterns('.gitkeep', '*.tmp.*'))

    def write(rel_path, text):
        dest = os.path.join(DIST, rel_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(text)

    # Render bodies first, so each page's lastmod can follow changes to its own content
    known, dates, built = load_lastmod(), {}, []
    for m in pages():
        body, extra = m['fn'](m['path'])
        digest = hashlib.sha1((m['title'] + m['desc'] + body).encode()).hexdigest()[:16]
        prev = known.get(m['path'], {})
        m['lastmod'] = prev['date'] if prev.get('hash') == digest else TODAY
        if m.get('article'):   # an article's own updated date wins when it is later
            m['lastmod'] = max(m['lastmod'], m['article']['updated']) if prev.get('hash') == digest else max(TODAY, m['article']['updated'])
        dates[m['path']] = {'hash': digest, 'date': m['lastmod']}
        write(m['path'], shell(m['path'], m, body, extra))
        if m.get('markdown', True):
            write(md_path(m['path']), page_markdown(m, body))
        built.append(m)
        if artifact and m['path'] == 'index.html':
            os.makedirs(os.path.join(ROOT, 'artifact'), exist_ok=True)
            with open(os.path.join(ROOT, 'artifact', 'index.html'), 'w', encoding='utf-8') as f:
                f.write(shell(m['path'], m, body, extra, artifact_index=True))
    if dates != known:
        try:
            with open(LASTMOD, 'w') as f:
                json.dump(dates, f, indent=1, sort_keys=True)
                f.write('\n')
        except OSError:
            pass  # read-only checkout (e.g. a Docker build): keep the computed dates for this build only

    write('sitemap.xml', sitemap_xml(built))
    write('robots.txt', robots_txt())
    write('llms.txt', llms_txt(built))
    order = [m for m in built if m.get('markdown', True)]
    full = f"# Otorithm: full site content\n\n> Every page of {DOMAIN}, in Markdown. Generated {TODAY}. Index: {DOMAIN}/llms.txt\n\n"
    full += '\n\n---\n\n'.join(page_markdown(m, m['fn'](m['path'])[0]) for m in order)
    write('llms-full.txt', full)
    write('insights/feed.xml', rss_xml(built))
    write('manifest.json', manifest_json())
    write('.well-known/security.txt', security_txt())
    key = C.SITE.get('indexnow_key')
    if key:
        write(f'{key}.txt', key + '\n')
    ico = os.path.join(ROOT, 'assets', 'icons', 'favicon.ico')
    if os.path.exists(ico):
        shutil.copy(ico, os.path.join(DIST, 'favicon.ico'))
    print(f'Built {len(built)} pages (+ Markdown twins, sitemap, robots, llms.txt, feed) into dist/')


if __name__ == '__main__':
    main()
