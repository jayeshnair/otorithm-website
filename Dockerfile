# syntax=docker/dockerfile:1

# ---- Build stage: generate the static site from content.py ----
FROM python:3.12-alpine AS build
WORKDIR /src
COPY build.py content.py ./
COPY assets ./assets
RUN python3 build.py

# ---- Runtime stage: serve it with Nginx ----
FROM nginx:1.27-alpine
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /src/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1
