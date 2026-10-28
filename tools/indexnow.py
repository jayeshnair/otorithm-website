#!/usr/bin/env python3
"""
Tells IndexNow search engines (Bing, Yandex, Seznam, Naver and others that share submissions)
that pages on otorithm.com are new or changed, so they are recrawled within minutes instead of days.
Bing's index also feeds ChatGPT search and Microsoft Copilot. Google does not use IndexNow; it
reads sitemap.xml, which Search Console should know about (see README).

Reads the live sitemap, so run it after a deploy (the GitHub workflow does):

  python3 tools/indexnow.py            # pages whose lastmod is within the last 3 days
  python3 tools/indexnow.py --all      # every page in the sitemap

Needs only the Python 3 standard library. The key lives in content.py (SITE['indexnow_key']) and
build.py publishes it at https://otorithm.com/<key>.txt, which is how IndexNow verifies ownership.
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import content as C  # noqa: E402

DOMAIN = C.SITE['domain']
KEY = C.SITE.get('indexnow_key', '')
NS = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
UA = {'User-Agent': 'otorithm-indexnow/1.0 (+https://otorithm.com)'}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read().decode('utf-8')


def main():
    if not KEY:
        sys.exit('No SITE["indexnow_key"] in content.py')
    key_url = f'{DOMAIN}/{KEY}.txt'
    if get(key_url).strip() != KEY:
        sys.exit(f'{key_url} does not contain the key yet; deploy the site first')

    root = ET.fromstring(get(f'{DOMAIN}/sitemap.xml'))
    since = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
    urls = []
    for u in root.findall('sm:url', NS):
        loc, lastmod = u.findtext('sm:loc', namespaces=NS), u.findtext('sm:lastmod', default='', namespaces=NS)
        if '--all' in sys.argv or lastmod >= since:
            urls.append(loc)
    if not urls:
        print('No pages changed in the last 3 days; nothing to submit.')
        return

    host = DOMAIN.split('://', 1)[1]
    body = json.dumps({'host': host, 'key': KEY, 'keyLocation': key_url, 'urlList': urls}).encode()
    req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, method='POST',
                                 headers={**UA, 'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f'IndexNow accepted {len(urls)} URL(s): HTTP {r.status}')
    except urllib.error.HTTPError as e:
        # 403: key not found at keyLocation; 422: URLs do not belong to the host; 429: too many requests
        sys.exit(f'IndexNow refused the submission: HTTP {e.code} {e.read().decode(errors="replace")[:200]}')
    for u in urls:
        print('  ' + u)


if __name__ == '__main__':
    main()
