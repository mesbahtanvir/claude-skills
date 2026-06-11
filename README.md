# claude-skills

Custom skills for Claude Code — and the first testbed for one of them: this
repository is governed by its own spec ([spec-driven](skills/spec-driven/),
dogfooded).

## Install

In any Claude Code session:

```
/plugin marketplace add mesbahtanvir/claude-skills
/plugin install claude-skills@claude-skills
```

Skills trigger automatically when a request matches their description; invoke
one explicitly with `/claude-skills:spec-driven`.

Manual alternative: clone the repo and symlink a skill into your personal
skills directory —

```
ln -s "$(pwd)/skills/spec-driven" ~/.claude/skills/spec-driven
```

## Skills

| Skill | What it does |
| --- | --- |
| [spec-driven](skills/spec-driven/) | Spec-driven development: append-only, numbered spec entries are the source of truth, `SPEC.md` is the serialized consistent view, and code + tests implement the folded spec. |

## The spec for this repo

- [specs/SPEC.md](specs/SPEC.md) — the current consistent view (generated; never edit by hand)
- [specs/entries/](specs/entries/) — append-only entries, the source of truth
- `python specs/fold_spec.py check` — verifies the view matches the entries (runs in CI alongside the tests)

To change what this repo's contents should do: append an entry
(`python specs/fold_spec.py new "Title"`), fold, implement, and cite the
requirement IDs in tests — see [skills/spec-driven/SKILL.md](skills/spec-driven/SKILL.md).
