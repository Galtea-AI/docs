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

## Validate

**`python scripts/run.py --build` is the validation command** (it runs `mint validate`, strict: broken links, navigation issues). Run it before committing docs changes.

Do **not** use bare `python scripts/run.py` to validate: it runs `mint dev`, a hot-reload preview server that never exits, so it will hang until you kill it. Use `--embed-only` when you want just the clone plus code-embed pass with no `mint` step.

The code-embed check fails when an MDX `{/* @embed ... */}` points at a missing file or section, so it catches the most common docs regression.

On Windows, prefix the command with `PYTHONIOENCODING=utf-8`. The script prints a `→`, which the default cp1252 console cannot encode, so it dies on a `UnicodeEncodeError` traceback that looks like a docs failure but is not.
