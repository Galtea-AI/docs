# Documentation File Renames and URL Redirects

## Context

Documentation page filenames in `docs/` determine their public URL paths (e.g., `sdk/tutorials/create-evaluation.mdx` serves at `docs.galtea.ai/sdk/tutorials/create-evaluation`). As features evolve, page titles and content diverge from their original filenames, creating misleading URLs that no longer reflect what the page covers.

Renaming files fixes the URL but breaks all existing links: bookmarks, external blog posts, SDK docstrings, changelogs, and cross-references within the docs themselves.

Old changelogs (`docs/snippets/changelog/`) are historical records and must **not** be updated when a page is renamed. Their links were correct at the time of writing; the redirect handles them transparently. That reasoning covers the path only. A redirect cannot repair a URL fragment (`#some-heading`), because the browser resolves the fragment after the redirect has already run.

An entity rename can also make a new page claim a path that an old redirect already occupies. A path cannot be both a redirect `source` and a real page, so the two rules above collide and one has to give.

## Decision

When a documentation page's filename no longer matches its title or content, apply this process:

1. **Rename the file** to match the current title (kebab-case).
2. **Update `docs.json` navigation**: replace the old path in the `pages` array.
3. **Add a redirect in `docs.json`**: add an entry to the `redirects` array mapping the old path to the new one:
   ```json
   {
     "source": "/sdk/tutorials/old-name",
     "destination": "/sdk/tutorials/new-name"
   }
   ```
4. **Update internal references**: search all `.mdx` and `.json` files for the old path and replace with the new one, **except**:
   - Redirect `source` entries in `docs.json` (these must keep the old path)
   - Old changelog files in `docs/snippets/changelog/` (these are historical records and should not be modified)
5. **Never delete redirects**: even if no known links use the old path, external sites may reference it. One exception: **path reclamation**. When a new page must serve a path an existing redirect occupies, delete that redirect, because Mintlify cannot serve one path as both a redirect `source` and a real page. Links to that path then resolve to the new page instead of the redirect's old destination, so check what they meant before you accept the change, and list the reclaimed paths in the PR description.
6. **Fix the old anchor when a rename changes a heading**: no `redirects` entry can do it, so search the whole tree for the old `#fragment` and update every hit. This is the only edit allowed inside `docs/snippets/changelog/`: change the fragment token alone and leave the visible link text as written.

## Consequences

- **Positive:** URLs accurately reflect page content; users and search engines find the right page via descriptive paths.
- **Positive:** Old links continue working via Mintlify's redirect system: no 404s.
- **Positive:** Historical changelogs remain accurate snapshots of their original publication.
- **Trade-off:** The `redirects` array in `docs.json` grows over time. This is acceptable. Mintlify handles redirects efficiently and the list serves as a rename history.
- **Trade-off:** Requires searching the entire `docs/` tree for references on each rename. Use `Grep` for the old path across `*.mdx` and `*.json` to ensure nothing is missed.
- **Trade-off:** A reclaimed path silently changes where old links land. A changelog that linked the path meaning the old entity now sends the reader to the new page. Rewriting those links would falsify the historical record, so they stay as written and the PR description names them.
