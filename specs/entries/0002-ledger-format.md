---
title: Spec ledger format
date: 2026-06-10
---

## Why

Genesis entry: the entry grammar and fold semantics that the spec-ledger
skill defines and that this repository itself follows.

## Feature: LEDGER — Ledger format and fold semantics

An append-only ledger of spec entries: numbered files, newest wins, one
consistent folded view.

- **LEDGER-1**: Ledger entries MUST be files matching `NNNN-slug.md` under
  `specs/ledger/`, and the fold MUST replay them in ascending numeric order.
- **LEDGER-2**: Merged entries MUST NOT be edited; every spec change is a new
  appended entry.
- **LEDGER-3**: A requirement MUST be written as `- **PREFIX-N**: statement`
  — a bold, uppercase-prefixed ID with a colon or dash separator — and
  continuation lines indented two spaces join the statement.
- **LEDGER-4**: Re-declaring an active requirement ID redefines it; the
  newest text MUST win in the folded view.
- **LEDGER-5**: A requirement declared with `(supersedes ID, ...)` MUST close
  the listed IDs and record the new ID as their replacement.
- **LEDGER-6**: IDs listed under a `## Retires` heading MUST be closed
  without replacement, keeping the stated reason.
- **LEDGER-7**: Closed IDs MUST never be redefined or reused; a ledger that
  revives one MUST fail validation.
- **LEDGER-8**: A `## Feature: PREFIX — Title` block sets the title and
  description of that prefix's section in the folded view; the newest block
  per prefix MUST win.
