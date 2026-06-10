---
title: Fold script behavior
date: 2026-06-10
---

## Why

Genesis entry: the observable contract of `specs/fold_spec.py`, the
serializer that turns the ledger into SPEC.md.

## Feature: FOLD — The fold script

`python specs/fold_spec.py <command>` — deterministic serialization plus the
guardrails that keep the ledger consistent.

- **FOLD-1**: `fold` MUST regenerate `specs/SPEC.md` from the ledger alone,
  deterministically — identical ledgers MUST fold to byte-identical views.
- **FOLD-2**: Each active requirement in SPEC.md MUST carry provenance: the
  entry that introduced it and, when different, the entry that last
  modified it.
- **FOLD-3**: SPEC.md MUST list closed requirements together with what closed
  them — the superseding ID, or the retirement entry and reason.
- **FOLD-4**: `check` MUST exit nonzero when SPEC.md is missing or differs
  from the fold of the current ledger.
- **FOLD-5**: `validate` MUST exit nonzero on duplicate entry numbers,
  duplicate IDs within an entry, revival of closed IDs, or superseding or
  retiring an unknown or already-closed ID.
- **FOLD-6**: `new TITLE` MUST create the next-numbered entry file from the
  template and print its path.
- **FOLD-7**: `next-id PREFIX` MUST print the smallest number greater than
  every number ever used for that prefix, across active and closed IDs alike.
- **FOLD-8**: The script MUST run with the Python 3.8+ standard library only.
