---
name: test-docs
description: Validate the Mintlify docs build after editing files under docs/. Runs python scripts/run.py to catch broken links, code-embed misses, and navigation issues before commit.
---

# Test the Mintlify docs

Run these from the repo root after editing anything under `docs/`.

## Local preview

```bash
cd docs && npm install && npm run dev   # http://localhost:3000
```

## Validate and build

- **Validate** (broken links, code-embed misses, navigation issues): `python scripts/run.py`
- **Build**: `python scripts/run.py --build`

Run the validate step before committing docs changes. The code-embed check fails when an MDX `{/* @embed ... */}` points at a missing file or section, so it catches the most common docs regression.
