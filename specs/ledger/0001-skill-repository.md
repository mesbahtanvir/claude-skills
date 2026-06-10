---
title: Skill repository conventions
date: 2026-06-10
---

## Why

Genesis entry: records how this repository is organized as of commit 77aeb2f
(the commit that added the spec-ledger skill).

## Feature: REPO — Skill repository conventions

claude-skills is a collection of Claude Code skills, one directory per skill,
governed by this spec ledger.

- **REPO-1**: Every skill MUST live in its own top-level directory containing
  a SKILL.md whose YAML frontmatter declares `name` and `description`.
- **REPO-2**: A skill's frontmatter `name` MUST equal its directory name.
- **REPO-3**: Skill resources SHOULD follow the standard layout: `references/`
  for documentation loaded on demand, `scripts/` for executable helpers,
  `assets/` for files used in output.
- **REPO-4**: Every PR that changes what this repository's contents should do
  MUST append a spec ledger entry under `specs/ledger/` and regenerate
  `specs/SPEC.md`.
- **REPO-5**: `specs/fold_spec.py` MUST be byte-identical to
  `spec-ledger/scripts/fold_spec.py` — the skill ships the canonical copy,
  and this repo eats its own dogfood.
