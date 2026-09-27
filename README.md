# otorithm-site

Marketing site for otorithm.com: React + TypeScript + Vite + Tailwind CSS v4, Ligature brand.

## Run

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # type-check + production build into dist/
```

## Edit content

All copy, links and team details live in `src/content.ts`.

Before launch, replace:
- `CAL_LINK` with your Cal.com booking URL
- `LINKEDIN_URL` with your company LinkedIn page
- The service claims ("two weeks", "72 hours", "replacement guarantee") if delivery can't back them yet
- Set up hello@otorithm.com and careers@otorithm.com mailboxes

## Structure

```
src/
  content.ts                 all site copy
  lib/constellation.js       particle engine (framework-agnostic) + .d.ts types
  components/                Navbar, Hero, Services, HowWeWork, WhyUs, Careers, Contact, Footer,
                             LigatureMark (mark + lockup), Constellation (engine wrapper), GhostLink
  index.css                  Tailwind v4 @theme tokens + brand type/components
```

## Deploy (Docker on a VPS)

- `Dockerfile` builds the site and serves `dist/` from `nginx:alpine` (config in `docker/nginx.conf`).
- `deploy/` holds one compose file per reverse-proxy setup: Traefik, Nginx Proxy Manager, Caddy, or host Nginx.
- `.github/workflows/deploy.yml` builds the image on every push to `main`, pushes it to GHCR, and runs `docker compose pull && up -d` on the VPS.

Local smoke test:

```bash
docker build -t otorithm-web .
docker run --rm -p 8080:80 otorithm-web   # http://localhost:8080
```
