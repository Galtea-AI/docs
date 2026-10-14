---
name: test-docs
description: Validate the Mintlify docs build after editing files under docs/. Runs python scripts/run.py to catch broken links, code-embed misses, and navigation issues before commit.
---

# Test the Mintlify docs

Run these from the repo root after editing anything under `docs/`.

## Local preview

Start the **docs** entry in the Claude Code server list (`.claude/launch.json`), or run it yourself:

```bash
python docs/scripts/run.py   # http://localhost:3000
```

`run.py` finds the docs root from its own path, so it does not care which directory you run it from.

**Mint needs Node 20.17 or higher.** Below that it refuses to start, with `mintlify requires node 20.17 or higher`.

With a version manager (nvm, fnm, asdf, Volta), **an up-to-date `node -v` in your terminal does not mean the same version reaches this command.** Those tools load from your shell rc file, which a non-interactive shell does not read, so it falls back to the system Node. Select the version explicitly in that shell, for example `nvm use default`.

The `docs` launch entry handles this on its own: it sources nvm when nvm is present, and otherwise runs whatever Node is on `PATH`.

**Mint serves on port 3000 and that is not configurable.** `mint dev` has no `--port` flag and ignores `$PORT`, so the `docs` launch entry must keep `autoPort` off, unlike `dashboard-mock`: with it on, the preview tab points at a free port while Mint binds 3000 anyway. When 3000 is taken, free it.

There is no `npm run dev` here: `docs/package.json` is empty and there is no `node_modules`. `run.py` invokes Mint through `npx --yes mint`.

## Validate

**`python scripts/run.py --validate` is the validation command** (it runs `mint validate`, strict: broken links, navigation issues). Run it before committing docs changes.

Do **not** use bare `python scripts/run.py` to validate: it runs `mint dev`, a hot-reload preview server that never exits, so it will hang until you kill it. Use `--embed-only` when you want just the clone plus code-embed pass with no `mint` step.

The code-embed check fails when an MDX `{/* @embed ... */}` points at a missing file or section.

On Windows, prefix the command with `PYTHONIOENCODING=utf-8`. The script prints a `→`, which the default cp1252 console cannot encode, so it dies on a `UnicodeEncodeError` that is not a docs failure.
