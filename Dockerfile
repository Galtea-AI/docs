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
# @modelcontextprotocol/sdk, adm-zip, axios, js-yaml and sharp below the
# releases that fix their CVEs, so the overrides lift them; drop each one once
# mint ships it. The other overrides hold the version every other Galtea image
# uses for that package, since this install has no lockfile.
COPY <<'EOF' package.json
{
  "private": true,
  "dependencies": {
    "mint": "4.2.935"
  },
  "overrides": {
    "@modelcontextprotocol/sdk": "1.31.0",
    "adm-zip": "0.6.1",
    "axios": "1.20.0",
    "brace-expansion@^1": "1.1.20",
    "express-rate-limit@^8": "8.5.1",
    "ip-address@^10": "10.3.1",
    "js-yaml@^4": "4.3.2",
    "minimatch@^3": "3.1.4",
    "nanoid@^3": "3.3.18",
    "picomatch@^4": "4.0.4",
    "sharp": "0.35.5"
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
ENV MINT_CLIENT_VERSION=0.0.3687
RUN mkdir -p /root/.mintlify/previews/3000 \
  && wget -qO- "https://releases.mintlify.com/mint-${MINT_CLIENT_VERSION}.tar.gz" \
    | tar -xz -C /root/.mintlify/previews/3000 \
  && printf '%s' "$MINT_CLIENT_VERSION" > /root/.mintlify/previews/3000/mint/mint-version.txt

# Copy the embedded docs output from the builder stage
COPY --from=builder /docs-src/.build .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
  CMD wget -q --spider http://localhost:3000/ || exit 1

CMD ["sh", "-c", "node_modules/.bin/mint dev --port 3000 --client-version \"$MINT_CLIENT_VERSION\" < /dev/null"]
