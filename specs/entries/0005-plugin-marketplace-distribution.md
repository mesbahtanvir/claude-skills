---
title: Plugin marketplace distribution
date: 2026-06-11
---

## Why

The repository becomes publicly installable: it is now a Claude Code plugin
marketplace hosting one plugin (`claude-skills`) that ships every skill in
the repo. Skills move under `skills/` to match the plugin layout.

## Requirements

- **REPO-1**: Every skill MUST live in its own directory under `skills/`,
  containing a SKILL.md whose YAML frontmatter declares `name` and
  `description`.
- **REPO-5**: `specs/fold_spec.py` MUST be byte-identical to
  `skills/spec-driven/scripts/fold_spec.py` — the skill ships the canonical
  copy, and this repo eats its own dogfood.
- **REPO-6**: `.claude-plugin/marketplace.json` MUST parse as JSON and list a
  plugin named `claude-skills` whose source resolves to a directory of this
  repository containing the `skills/` tree.
- **REPO-7**: `.claude-plugin/plugin.json` MUST declare the plugin name
  `claude-skills` and a semantic version (MAJOR.MINOR.PATCH).
