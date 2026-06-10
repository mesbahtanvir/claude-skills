# Specification

> **Generated — do not edit.** This file is the fold of `specs/ledger/`.
> To change the spec, append a new ledger entry and run `python specs/fold_spec.py fold`.

_3 ledger entries folded (latest: 0003) — 21 active requirements, 0 closed._

## FOLD — The fold script

`python specs/fold_spec.py <command>` — deterministic serialization plus the guardrails that keep the ledger consistent.

- **FOLD-1** — `fold` MUST regenerate `specs/SPEC.md` from the ledger alone, deterministically — identical ledgers MUST fold to byte-identical views. _[0003]_
- **FOLD-2** — Each active requirement in SPEC.md MUST carry provenance: the entry that introduced it and, when different, the entry that last modified it. _[0003]_
- **FOLD-3** — SPEC.md MUST list closed requirements together with what closed them — the superseding ID, or the retirement entry and reason. _[0003]_
- **FOLD-4** — `check` MUST exit nonzero when SPEC.md is missing or differs from the fold of the current ledger. _[0003]_
- **FOLD-5** — `validate` MUST exit nonzero on duplicate entry numbers, duplicate IDs within an entry, revival of closed IDs, or superseding or retiring an unknown or already-closed ID. _[0003]_
- **FOLD-6** — `new TITLE` MUST create the next-numbered entry file from the template and print its path. _[0003]_
- **FOLD-7** — `next-id PREFIX` MUST print the smallest number greater than every number ever used for that prefix, across active and closed IDs alike. _[0003]_
- **FOLD-8** — The script MUST run with the Python 3.8+ standard library only. _[0003]_

## LEDGER — Ledger format and fold semantics

An append-only ledger of spec entries: numbered files, newest wins, one consistent folded view.

- **LEDGER-1** — Ledger entries MUST be files matching `NNNN-slug.md` under `specs/ledger/`, and the fold MUST replay them in ascending numeric order. _[0002]_
- **LEDGER-2** — Merged entries MUST NOT be edited; every spec change is a new appended entry. _[0002]_
- **LEDGER-3** — A requirement MUST be written as `- **PREFIX-N**: statement` — a bold, uppercase-prefixed ID with a colon or dash separator — and continuation lines indented two spaces join the statement. _[0002]_
- **LEDGER-4** — Re-declaring an active requirement ID redefines it; the newest text MUST win in the folded view. _[0002]_
- **LEDGER-5** — A requirement declared with `(supersedes ID, ...)` MUST close the listed IDs and record the new ID as their replacement. _[0002]_
- **LEDGER-6** — IDs listed under a `## Retires` heading MUST be closed without replacement, keeping the stated reason. _[0002]_
- **LEDGER-7** — Closed IDs MUST never be redefined or reused; a ledger that revives one MUST fail validation. _[0002]_
- **LEDGER-8** — A `## Feature: PREFIX — Title` block sets the title and description of that prefix's section in the folded view; the newest block per prefix MUST win. _[0002]_

## REPO — Skill repository conventions

claude-skills is a collection of Claude Code skills, one directory per skill, governed by this spec ledger.

- **REPO-1** — Every skill MUST live in its own top-level directory containing a SKILL.md whose YAML frontmatter declares `name` and `description`. _[0001]_
- **REPO-2** — A skill's frontmatter `name` MUST equal its directory name. _[0001]_
- **REPO-3** — Skill resources SHOULD follow the standard layout: `references/` for documentation loaded on demand, `scripts/` for executable helpers, `assets/` for files used in output. _[0001]_
- **REPO-4** — Every PR that changes what this repository's contents should do MUST append a spec ledger entry under `specs/ledger/` and regenerate `specs/SPEC.md`. _[0001]_
- **REPO-5** — `specs/fold_spec.py` MUST be byte-identical to `spec-ledger/scripts/fold_spec.py` — the skill ships the canonical copy, and this repo eats its own dogfood. _[0001]_
