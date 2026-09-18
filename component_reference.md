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

## Redirects

When renaming/moving pages, add to `docs.json`:
```json
{ "redirects": [{ "source": "/old/path", "destination": "/new/path" }] }
```

## Images

Store in `docs/images/` with descriptive names. Reference: `![Alt text](/images/dashboard-products-list.png)`.
