# Public docs (Mintlify)

## Rules

- `deployment/`, `images/deployment/` and the `Deployment` tab of `docs.json` are published from the `gitops` repository on each deployment-guide release. Edit the source there; a hand edit here is overwritten.
- Never write an inline Python code block in an `.mdx` file. Code lives in runnable scripts under `code/python/`, marked with `# @start <section>` and `# @end <section>`, and a page embeds a section with `{/* @embed path="..." lang="python" section="..." */}`. CI runs every script. Extend an existing script before you add one.
- Put a snippet's assertions after `# @end`, so readers do not copy them. An agent callback run by the simulator must not raise to signal a problem: the simulator turns the error into an empty reply and exits 0. Assert on an observable result instead.
- The generated OpenAPI reference is the API contract, not a prose page. Check an "every", "always" or "never" claim against the API schema, not only the SDK, and confirm both sides of a contrast still exist.
- A term one page defines keeps that meaning on every page that links to it.
- A new page gets frontmatter (`title`, `description`, `icon`) and a `docs.json` navigation entry. A renamed page gets a permanent redirect, and every internal link moves to the new path except in a changelog entry a release shipped. Never delete a redirect unless a new page must reclaim its path.
- A redirect cannot repair a `#fragment`. When a rename changes a heading, search the tree for the old fragment and update every hit. In a shipped changelog entry change the fragment token only.
- Write a component tag as a block: the opening tag on its own line, never followed by body text.
- `.build/docs.json` is rewritten from local env files. Read URLs from the committed `docs.json`.

## Changelog Entries

`scripts/run.py` builds the changelog page from `changelog/entries/`, grouped by the first release whose tag holds each entry. Never write a `changelog.mdx` page by hand.

- One entry per user-facing change, written for users in the PR that makes it visible in production. A feature behind a flag gets its entry in the PR that turns the flag on for everyone. A refactor, a CI change or an internal fix gets none.
- Name: `YYYYMMDD-HHMM-short-name.mdx`, in UTC, when you write it. Body: a `## Title` heading, no frontmatter, then what the user can now do, rarely more than 3 sentences.
- Edit an entry until a release ships it. After that, a change gets a new entry.

## Local checks

Use the `test-docs` skill to preview and build. After editing an MDX file, run `mint validate` from `docs/` (Node 22) and read its output for `parsing error`: it exits 0 on one. `mint broken-links` does not check syntax. Components and templates: `component_reference.md`.
