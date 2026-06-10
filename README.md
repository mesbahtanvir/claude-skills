# claude-skills

Custom skills for Claude Code — and the first testbed for one of them: this
repository is governed by its own spec ledger ([spec-ledger](spec-ledger/),
dogfooded).

## Skills

| Skill | What it does |
| --- | --- |
| [spec-ledger](spec-ledger/) | Spec-driven development with an append-only spec ledger: numbered entries are the source of truth, `SPEC.md` is the serialized consistent view, and code + tests implement the folded spec. |

## The spec for this repo

- [specs/SPEC.md](specs/SPEC.md) — the current consistent view (generated; never edit by hand)
- [specs/ledger/](specs/ledger/) — append-only entries, the source of truth
- `python specs/fold_spec.py check` — verifies the view matches the ledger (runs in CI alongside the tests)

To change what this repo's contents should do: append an entry
(`python specs/fold_spec.py new "Title"`), fold, implement, and cite the
requirement IDs in tests — see [spec-ledger/SKILL.md](spec-ledger/SKILL.md).

## Using a skill

Clone this repo and point Claude Code at the skills you want, or symlink them
into `~/.claude/skills/`.
