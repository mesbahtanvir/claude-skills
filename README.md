# claude-skills

Custom skills for Claude Code — and the first testbed for one of them: this
repository is governed by its own spec ([spec-driven](spec-driven/),
dogfooded).

## Skills

| Skill | What it does |
| --- | --- |
| [spec-driven](spec-driven/) | Spec-driven development: append-only, numbered spec entries are the source of truth, `SPEC.md` is the serialized consistent view, and code + tests implement the folded spec. |

## The spec for this repo

- [specs/SPEC.md](specs/SPEC.md) — the current consistent view (generated; never edit by hand)
- [specs/entries/](specs/entries/) — append-only entries, the source of truth
- `python specs/fold_spec.py check` — verifies the view matches the entries (runs in CI alongside the tests)

To change what this repo's contents should do: append an entry
(`python specs/fold_spec.py new "Title"`), fold, implement, and cite the
requirement IDs in tests — see [spec-driven/SKILL.md](spec-driven/SKILL.md).

## Using a skill

Clone this repo and point Claude Code at the skills you want, or symlink them
into `~/.claude/skills/`.
