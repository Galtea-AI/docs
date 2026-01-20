# Galtea Docs

## Pre-requisites

To contribute to the Galtea documentation, you need to have the following installed:
- [Node.js](https://nodejs.org/en/download/) (version 18 or later)
  - npm is also needed but comes with Node.js if you install it from the official website so you don't have to do anything.

## Development

Install the [Mintlify CLI](https://www.npmjs.com/package/mintlify) to preview the documentation changes locally. To install, use the following command

```
npm i -g mintlify
```

Run the following command at the root of your documentation (where docs.json is)

```
mintlify dev
```

> Some changes (such as *snippets* modifications) may require a restart of the dev server.

## Publishing Changes

Install our Github App to auto propagate changes from your repo to your deployment. Changes will be deployed to production automatically after pushing to the default branch. Find the link to install on your dashboard. 

### Troubleshooting

- Mintlify dev isn't running - Run `mintlify install` it'll re-install dependencies.
- Page loads as a 404 - Make sure you are running in a folder with `docs.json`
