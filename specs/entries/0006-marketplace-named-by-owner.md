---
title: Marketplace named by owner
date: 2026-06-11
---

## Why

`/plugin install claude-skills@claude-skills` read redundantly because the
marketplace and the plugin shared a name. The marketplace is now named after
its owner, so installs read `claude-skills@mesbahtanvir` — package@owner.
The spec was silent on the marketplace name; this entry pins it.

## Requirements

- **REPO-6**: `.claude-plugin/marketplace.json` MUST parse as JSON, declare
  the marketplace name `mesbahtanvir`, and list a plugin named
  `claude-skills` whose source resolves to a directory of this repository
  containing the `skills/` tree.
