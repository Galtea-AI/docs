# syntax=docker/dockerfile:1

# ─── Stage 1: Embed code snippets ────────────────────────────────────────────
# Runs run.py --embed-only which clones docs/ to .build/ and inlines all
# @embed placeholders. No external Python dependencies are required.
FROM python:3.12-slim AS builder

WORKDIR /docs-src

COPY . .

RUN python scripts/run.py --embed-only

# ─── Stage 2: Serve with Mintlify dev server ──────────────────────────────────
FROM node:24.14.0-alpine AS runtime

WORKDIR /app

# Install Mintlify CLI and pre-fetch its dependencies during the build so that
# container startup is fast and does not require internet access at runtime.
RUN npm install mintlify@4.2.397

# Copy the embedded docs output from the builder stage
COPY --from=builder /docs-src/.build .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
  CMD wget -q --spider http://localhost:3000/ || exit 1

CMD ["sh", "-c", "node_modules/.bin/mintlify dev --port 3000 < /dev/null"]
