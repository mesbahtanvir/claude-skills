---
title: Drop the ledger vocabulary
date: 2026-06-10
---

## Why

The system sheds its ledger branding: the skill is now `spec-driven` and
entries live under `specs/entries/`. Mechanics are unchanged — this entry
carries the rename by superseding the LEDGER-* requirements with SPEC-* ones
and redefining the requirements that referenced the old names and paths.

## Feature: REPO — Skill repository conventions

claude-skills is a collection of Claude Code skills, one directory per
skill, governed by this spec.

## Feature: FOLD — The fold script

`python specs/fold_spec.py <command>` — deterministic serialization plus
the guardrails that keep the spec consistent.

## Feature: SPEC — Spec entries and fold semantics

Append-only spec entries: numbered files, newest wins, one consistent
folded view.

- **SPEC-1** (supersedes LEDGER-1): Spec entries MUST be files matching
  `NNNN-slug.md` under `specs/entries/`, and the fold MUST replay them in
  ascending numeric order.
- **SPEC-2** (supersedes LEDGER-2): Merged entries MUST NOT be edited; every
  spec change is a new appended entry.
- **SPEC-3** (supersedes LEDGER-3): A requirement MUST be written as
  `- **PREFIX-N**: statement` — a bold, uppercase-prefixed ID with a colon or
  dash separator — and continuation lines indented two spaces join the
  statement.
- **SPEC-4** (supersedes LEDGER-4): Re-declaring an active requirement ID
  redefines it; the newest text MUST win in the folded view.
- **SPEC-5** (supersedes LEDGER-5): A requirement declared with
  `(supersedes ID, ...)` MUST close the listed IDs and record the new ID as
  their replacement.
- **SPEC-6** (supersedes LEDGER-6): IDs listed under a `## Retires` heading
  MUST be closed without replacement, keeping the stated reason.
- **SPEC-7** (supersedes LEDGER-7): Closed IDs MUST never be redefined or
  reused; a spec history that revives one MUST fail validation.
- **SPEC-8** (supersedes LEDGER-8): A `## Feature: PREFIX — Title` block sets
  the title and description of that prefix's section in the folded view; the
  newest block per prefix MUST win.

## Requirements

- **REPO-4**: Every PR that changes what this repository's contents should do
  MUST append a spec entry under `specs/entries/` and regenerate
  `specs/SPEC.md`.
- **REPO-5**: `specs/fold_spec.py` MUST be byte-identical to
  `spec-driven/scripts/fold_spec.py` — the skill ships the canonical copy,
  and this repo eats its own dogfood.
- **FOLD-1**: `fold` MUST regenerate `specs/SPEC.md` from the spec entries
  alone, deterministically — identical entries MUST fold to byte-identical
  views.
- **FOLD-4**: `check` MUST exit nonzero when SPEC.md is missing or differs
  from the fold of the current entries.
