# Mintlify Documentation Guidelines

> **SCOPE:** These rules apply when working on files under `docs/`.

## Project Structure

```
docs/
├── docs.json              # Mintlify configuration (navigation, theme)
├── concepts/              # Concept documentation
├── sdk/                   # SDK documentation (api/, tutorials/)
├── code/                  # Code snippets (Python scripts)
├── snippets/              # Reusable MDX snippets
├── images/                # Documentation images
└── logo/                  # Logo assets
```

## Critical Rule: Code Embeds

**NEVER write inline Python code blocks in `.mdx` files.** All code examples live in standalone Python scripts under `docs/code/` so they can be tested in CI/CD.

Snippets are validated against the mocked docker-compose stack on every PR and push to main (`.github/workflows/docs-snippets-mocked.yml`) and on prod releases (`deploy-services.yml` via the reusable `_docs-snippets-mocked.yml`); the nightly `e2e.yml` run validates all of them against the live environment, the only coverage for the `docs/mocked_ci_skip.txt` entries (#3587).

### How it works

1. Code files live in `docs/code/python/` as full, runnable Python scripts with section markers:
   ```python
   # @start section_name
   result = galtea.products.create(name="My Product")
   # @end section_name
   ```
2. MDX files embed sections:
   ```mdx
   {/* @embed path="code/python/my_file.py" lang="python" section="section_name" */}
   ```

### Code file rules

- Section names: descriptive `snake_case` (e.g., `usage_and_cost_info`)
- File naming: `sdk_api_<service>_<method>.py`, `sdk_tutorials_<topic>.py`, `concepts_<topic>.py`
- Before creating a new code file, check if an existing one covers the topic; add a section to it instead.

## Verify Prose Claims Against the Code

No hand-written page is the API contract: the wire-level contract is the generated OpenAPI reference (the `openapi` entry in `docs.json`). `concepts/` pages describe product fields as display labels ("Stopping Reason") in SDK vocabulary, so their field names do not track the API's. Two traps follow.

- **Absolute claims.** Before writing "every", "always", or "never", check the field in `api/prisma/schema.prisma` and `api/src/swagger.ts`, not only the SDK method. The API often accepts what the SDK does not expose: `SessionInput.status` lets a caller create an already-closed session, while `session_service.create()` has no such parameter.
- **Contrasting two settings.** Confirm **both** still exist. A removed field is easy to describe from memory and yields prose that contradicts the page it links to, as happened with a per-Monitor inactivity window documented after #3379 deleted it.

## Adding a New Page

1. Create the MDX file with frontmatter (`title`, `description`, `icon`)
2. Add the page path to `docs.json` navigation

## Component and Template Reference

Component usage (Callouts, Tabs, Cards), SDK API reference page template, redirects, and image conventions are documented in `docs/component_reference.md`.

## Architecture Decision Records

Docs-specific ADRs live in `docs/adr/`. Consult them before making structural changes to the documentation.

| ADR | Topic |
|-----|-------|
| `0001-docs-file-renames-and-redirects.md` | Rename file, update `docs.json` nav, add a permanent redirect, update internal links (changelogs excluded); never delete redirects |

## Local Development

Whenever you preview, validate, or build the docs site, use the `test-docs` skill (`npm run dev`, then `python scripts/run.py` to validate and `python scripts/run.py --build` to build).
