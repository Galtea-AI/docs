# syntax=docker/dockerfile:1

# ─── Stage 1: Embed code snippets ────────────────────────────────────────────
# Runs run.py --embed-only which clones docs/ to .build/ and inlines all
# @embed placeholders. No external Python dependencies are required.
FROM python:3.12-slim AS builder

WORKDIR /docs-src

COPY . .

# DASHBOARD_URL is the canonical tenant name (issue #2229).
ARG GALTEA_API_URL=""
ARG DASHBOARD_URL=""
ARG SHOW_PLATFORM_ASSISTANT=""
ENV GALTEA_API_URL=$GALTEA_API_URL
ENV DASHBOARD_URL=$DASHBOARD_URL
ENV SHOW_PLATFORM_ASSISTANT=$SHOW_PLATFORM_ASSISTANT

RUN python scripts/run.py --embed-only

# ─── Stage 2: Serve with Mint dev server ──────────────────────────────────────
FROM node:24.21.0-alpine3.24 AS runtime

WORKDIR /app

# Install Mint CLI (the renamed Mintlify CLI). Even the newest mint pins
# @modelcontextprotocol/sdk, adm-zip, axios, body-parser, esbuild, image-size,
# js-yaml, re2js, sharp and zod 4 below the releases that fix their CVEs, so the
# overrides lift them; drop each one once mint ships it. The other overrides hold the version every other Galtea image
# uses for that package, since this install has no lockfile.
COPY <<'EOF' package.json
{
  "private": true,
  "dependencies": {
    "mint": "4.2.1125"
  },
  "overrides": {
    "@modelcontextprotocol/sdk": "1.32.0",
    "adm-zip": "0.6.1",
    "axios": "1.20.0",
    "body-parser@^1": "1.20.9",
    "body-parser@^2": "2.4.0",
    "brace-expansion@^1": "1.1.20",
    "esbuild": "0.28.2",
    "express-rate-limit@^8": "8.5.1",
    "image-size@^2": "2.0.4",
    "ip-address@^10": "10.3.1",
    "js-yaml@^4": "4.3.2",
    "minimatch@^3": "3.1.4",
    "nanoid@^3": "3.3.18",
    "picomatch@^4": "4.0.4",
    "re2js": "2.8.7",
    "sharp": "0.35.5",
    "zod@^4": "4.6.7"
  }
}
EOF
RUN npm install --no-audit --no-fund

# The runtime starts node_modules/.bin/mint directly and never calls a package
# manager, so npm, npx and corepack are removed with the dependencies they
# bundle, which carry CVEs no npm release fixes yet.
RUN rm -rf /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/corepack \
    /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack /root/.npm

# Pin the Mintlify client (the Next.js app `mint dev` serves). Pinning the CLI
# does not pin it: without --client-version, every container start fetches
# whatever client releases.mintlify.com calls latest into ~/.mintlify. Replicas
# started on different days then serve different chunk hashes, so a page
# rendered by one pod requests chunks another pod 404s on ("Error loading
# page"). With --client-version the CLI re-downloads exactly this version on
# start, and falls back to the copy baked here if the download fails. That
# baked path depends on the port, so --port 3000 uses ~/.mintlify/previews/3000.
ENV MINT_CLIENT_VERSION=0.0.3965
RUN mkdir -p /root/.mintlify/previews/3000 \
  && wget -qO- "https://releases.mintlify.com/mint-${MINT_CLIENT_VERSION}.tar.gz" \
    | tar -xz -C /root/.mintlify/previews/3000 \
  && printf '%s' "$MINT_CLIENT_VERSION" > /root/.mintlify/previews/3000/mint/mint-version.txt

# Copy the embedded docs output from the builder stage
COPY --from=builder /docs-src/.build .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
  CMD wget -q --spider http://localhost:3000/ || exit 1

# Without --host, mint dev listens on ::1 only and the Service cannot reach the pod.
CMD ["sh", "-c", "node_modules/.bin/mint dev --host --port 3000 --client-version \"$MINT_CLIENT_VERSION\" < /dev/null"]
