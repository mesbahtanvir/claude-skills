# Specification

> **Generated — do not edit.** This file is the fold of `specs/entries/`.
> To change the spec, append a new entry and run `python specs/fold_spec.py fold`.

_6 spec entries folded (latest: 0006) — 23 active requirements, 8 closed._

## FOLD — The fold script

`python specs/fold_spec.py <command>` — deterministic serialization plus the guardrails that keep the spec consistent.

- **FOLD-1** — `fold` MUST regenerate `specs/SPEC.md` from the spec entries alone, deterministically — identical entries MUST fold to byte-identical views. _[0003 → 0004]_
- **FOLD-2** — Each active requirement in SPEC.md MUST carry provenance: the entry that introduced it and, when different, the entry that last modified it. _[0003]_
- **FOLD-3** — SPEC.md MUST list closed requirements together with what closed them — the superseding ID, or the retirement entry and reason. _[0003]_
- **FOLD-4** — `check` MUST exit nonzero when SPEC.md is missing or differs from the fold of the current entries. _[0003 → 0004]_
- **FOLD-5** — `validate` MUST exit nonzero on duplicate entry numbers, duplicate IDs within an entry, revival of closed IDs, or superseding or retiring an unknown or already-closed ID. _[0003]_
- **FOLD-6** — `new TITLE` MUST create the next-numbered entry file from the template and print its path. _[0003]_
- **FOLD-7** — `next-id PREFIX` MUST print the smallest number greater than every number ever used for that prefix, across active and closed IDs alike. _[0003]_
- **FOLD-8** — The script MUST run with the Python 3.8+ standard library only. _[0003]_

## REPO — Skill repository conventions

claude-skills is a collection of Claude Code skills, one directory per skill, governed by this spec.

- **REPO-1** — Every skill MUST live in its own directory under `skills/`, containing a SKILL.md whose YAML frontmatter declares `name` and `description`. _[0001 → 0005]_
- **REPO-2** — A skill's frontmatter `name` MUST equal its directory name. _[0001]_
- **REPO-3** — Skill resources SHOULD follow the standard layout: `references/` for documentation loaded on demand, `scripts/` for executable helpers, `assets/` for files used in output. _[0001]_
- **REPO-4** — Every PR that changes what this repository's contents should do MUST append a spec entry under `specs/entries/` and regenerate `specs/SPEC.md`. _[0001 → 0004]_
- **REPO-5** — `specs/fold_spec.py` MUST be byte-identical to `skills/spec-driven/scripts/fold_spec.py` — the skill ships the canonical copy, and this repo eats its own dogfood. _[0001 → 0005]_
- **REPO-6** — `.claude-plugin/marketplace.json` MUST parse as JSON, declare the marketplace name `mesbahtanvir`, and list a plugin named `claude-skills` whose source resolves to a directory of this repository containing the `skills/` tree. _[0005 → 0006]_
- **REPO-7** — `.claude-plugin/plugin.json` MUST declare the plugin name `claude-skills` and a semantic version (MAJOR.MINOR.PATCH). _[0005]_

## SPEC — Spec entries and fold semantics

Append-only spec entries: numbered files, newest wins, one consistent folded view.

- **SPEC-1** — Spec entries MUST be files matching `NNNN-slug.md` under `specs/entries/`, and the fold MUST replay them in ascending numeric order. _[0004]_
- **SPEC-2** — Merged entries MUST NOT be edited; every spec change is a new appended entry. _[0004]_
- **SPEC-3** — A requirement MUST be written as `- **PREFIX-N**: statement` — a bold, uppercase-prefixed ID with a colon or dash separator — and continuation lines indented two spaces join the statement. _[0004]_
- **SPEC-4** — Re-declaring an active requirement ID redefines it; the newest text MUST win in the folded view. _[0004]_
- **SPEC-5** — A requirement declared with `(supersedes ID, ...)` MUST close the listed IDs and record the new ID as their replacement. _[0004]_
- **SPEC-6** — IDs listed under a `## Retires` heading MUST be closed without replacement, keeping the stated reason. _[0004]_
- **SPEC-7** — Closed IDs MUST never be redefined or reused; a spec history that revives one MUST fail validation. _[0004]_
- **SPEC-8** — A `## Feature: PREFIX — Title` block sets the title and description of that prefix's section in the folded view; the newest block per prefix MUST win. _[0004]_

## Closed requirements

- **LEDGER-1** — superseded by **SPEC-1** in 0004
- **LEDGER-2** — superseded by **SPEC-2** in 0004
- **LEDGER-3** — superseded by **SPEC-3** in 0004
- **LEDGER-4** — superseded by **SPEC-4** in 0004
- **LEDGER-5** — superseded by **SPEC-5** in 0004
- **LEDGER-6** — superseded by **SPEC-6** in 0004
- **LEDGER-7** — superseded by **SPEC-7** in 0004
- **LEDGER-8** — superseded by **SPEC-8** in 0004
