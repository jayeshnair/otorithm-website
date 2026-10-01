# otorithm.com

Static, multi-page website for Otorithm. No framework and no npm: a small Python script turns
`content.py` into plain HTML pages, served by Nginx in Docker.

## Edit and preview

```bash
# edit copy in content.py (styles in assets/styles.css)
python3 build.py                                  # writes dist/
python3 -m http.server 8080 --directory dist      # http://localhost:8080
```

## Pages

| Page | File |
|---|---|
| Home | `index.html` |
| Services overview + 6 service pages | `services.html`, `services/*.html` |
| Industries | `industries.html` |
| Approach (delivery loop, models, security, time zones) | `approach.html` |
| Work (engagement blueprints) | `work.html` |
| Insights + 3 articles | `insights.html`, `insights/*.html` |
| About, Careers, Contact, Privacy, 404 | `about.html` … `404.html` |

`sitemap.xml` and `robots.txt` are generated too.

## Before launch

- `SITE['form_endpoint']` in `content.py`: set a form backend URL (Formspree, Basin or your own API)
  so the contact form posts. Left empty, the form composes the message for the visitor to email.
- Create the contact@ and careers@ mailboxes.
- Check every claim in `content.py` against how you actually operate (timelines, security practices,
  response times, open roles).
- Add a LinkedIn link to the footer once the company page exists.

## Hero video

`assets/hero.mp4` is a generated placeholder. To use an AI-generated clip, follow
`tools/ai-video-prompts.md`, then run `tools/prepare_hero_video.sh clip.mp4 pingpong` and rebuild.

## Deploy (Docker on the VPS)

The `Dockerfile` runs `build.py` in a Python stage and copies `dist/` into `nginx:alpine`.
`deploy/` holds compose files for Traefik, Nginx Proxy Manager, Caddy or host Nginx, and
`.github/workflows/deploy.yml` builds the image on every push to `main`, publishes it to
`ghcr.io/jayeshnair/otorithm-web`, and restarts it on the VPS once these repository secrets exist
(Settings → Secrets and variables → Actions):

- `VPS_HOST`: the VPS IP address
- `VPS_SSH_KEY`: a private key for the `deploy` user on the VPS

Until the secrets are set, the workflow builds and publishes the image and skips the VPS step.

```bash
docker build -t otorithm-web .
docker run --rm -p 8080:80 otorithm-web      # http://localhost:8080
```
