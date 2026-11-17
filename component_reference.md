# Mintlify Component Reference

## Callouts

```mdx
<Note>Important information.</Note>
<Tip>Helpful tips.</Tip>
<Warning>Caution about potential issues.</Warning>
<Info>Additional context.</Info>
```

## Tabs

```mdx
<Tabs>
  <Tab title="Python">
{/* @embed path="code/python/my_file.py" lang="python" section="my_section" */}
  </Tab>
</Tabs>
```

## Cards

```mdx
<CardGroup cols={2}>
  <Card title="Getting Started" icon="rocket" href="/quickstart">
    Quick introduction to Galtea
  </Card>
</CardGroup>
```

## SDK API Reference Page Template

```mdx
---
title: "create"
description: "Create a new product"
---

## Usage
{/* @embed path="code/python/sdk_api_product_create.py" lang="python" section="usage" */}

## Parameters
<ParamField path="name" type="str" required>The name of the product.</ParamField>
<ParamField path="description" type="str">Optional description.</ParamField>

## Returns
<ResponseField name="Product" type="Product">The created product object.</ResponseField>

## Example
{/* @embed path="code/python/sdk_api_product_create.py" lang="python" section="example" */}
```

### Documenting a second exception

`<EntityNotFound />` is not a table row. `docs/snippets/entity-not-found.mdx` emits its own `## Errors` heading **and** a complete `| Error | Cause |` table. A second table written below it gives the page one heading and two tables with the same header row.

To document a second exception, drop the snippet and write one table that holds both rows. `docs/sdk/api/job/cancel.mdx` is the pattern to copy. Remove the `import EntityNotFound` line too.

## Version tags

The SDK reference serves every compatible SDK version, so it tags what an older SDK cannot do. Import both tags from the snippet on each page that uses one, and write each as a block.

```mdx
import { Deprecated, Requires } from '/snippets/version-tags.mdx';

<Deprecated name="test_id" removal="2028-01-17" replacement="dataset_id">
</Deprecated>

<Requires sdk=">5.18">
</Requires>
```

- `Deprecated`: `name` is the deprecated name exactly as the SDK writes it, and `removal` is its SDK removal date (`python3 .github/scripts/release-calendar.py removal-date` on the day it was deprecated). Leave out `replacement` when there is none. Keep the tag until that date.
- `Requires`: a new SDK item. `sdk` is `>` plus the newest release line when you write the page:
  `{ gh api --paginate repos/Galtea-AI/monorepo/git/matching-refs/heads/releases/ --jq '.[].ref'; gh api --paginate repos/Galtea-AI/monorepo/git/matching-refs/tags/ --jq '.[].ref'; } | python3 .github/scripts/newest-release-line.py`.
  Remove the tag once every compatible major has the item.
- `python scripts/version_tags.py` (from `docs/`) fails on a tag that is not on its own line, on one line with double-quoted attributes, a missing import, a removal that is not a release window, and a `Deprecated` tag that no SDK deprecation backs with the same name and date. In a pull request it also warns on an added `Requires` value below the newest release line; a backfill for an older item keeps its lower value.

## Redirects

When renaming/moving pages, add to `docs.json`:
```json
{ "redirects": [{ "source": "/old/path", "destination": "/new/path" }] }
```

## Images

Store in `docs/images/` with descriptive names. Reference: `![Alt text](/images/dashboard-products-list.png)`.
