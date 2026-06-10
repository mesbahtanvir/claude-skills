# Spec entry format — full reference

Everything `fold_spec.py` parses, plus authoring guidance. The parser is
deliberately strict: a line that *almost* looks like a requirement is flagged
by `validate` rather than silently ignored, because a requirement that fails
to parse silently disappears from the fold — a lost piece of the contract.

## Contents

- [File naming](#file-naming)
- [Frontmatter](#frontmatter)
- [Sections of an entry](#sections-of-an-entry)
- [Requirement lines](#requirement-lines)
- [The ID lifecycle](#the-id-lifecycle)
- [Feature blocks](#feature-blocks)
- [Retires](#retires)
- [Choosing prefixes](#choosing-prefixes)
- [Writing good requirements](#writing-good-requirements)
- [Worked examples](#worked-examples)
- [Concurrent branches](#concurrent-branches)
- [What does not belong in the spec](#what-does-not-belong-in-the-spec)

## File naming

`specs/entries/NNNN-short-slug.md` — a zero-padded number and a kebab-case
slug. Numbers are unique and strictly ordered; the fold replays entries in
numeric order, so the number IS the timestamp. `fold_spec.py new "Title"`
picks the next number for you.

## Frontmatter

```markdown
---
title: Rate limiting for the public API
date: 2026-06-10
---
```

`title` and `date` (ISO, the date the entry was authored) are the only
expected keys. Anything else is ignored by the parser but allowed — e.g.
`author:` or a ticket link.

## Sections of an entry

```markdown
## Why            ← 1–3 sentences of motivation (strongly encouraged)
## Feature: …     ← optional; sets/replaces a feature's description in SPEC.md
## Requirements   ← requirement bullets (may appear under any heading except Retires)
## Retires        ← removals; ONLY retire bullets are parsed here
```

Headings are organizational except `## Feature:` and `## Retires`, which
change how bullets beneath them are interpreted. Requirement bullets are
recognized under any other heading, so you can group requirements under
feature headings if that reads better. Prose anywhere is fine — the parser
extracts only the structured lines. HTML comments (`<!-- … -->`) are stripped
before parsing, so the scaffold's hints never leak into the fold.

## Requirement lines

Grammar (one per line, wrapped continuations indented by two spaces):

```markdown
- **PREFIX-N**: Statement text.
- **PREFIX-N** (supersedes PREFIX-M, PREFIX-K): Statement text.
```

- The ID is bold, `PREFIX` is uppercase alphanumeric, `N` is an integer.
- Separator after the ID may be `:` or `—`.
- A continuation line is indented two or more spaces and is joined onto the
  requirement text:

  ```markdown
  - **API-9**: Public endpoints MUST enforce a rate limit of 100 requests
    per minute per API key.
  ```

- A blank line ends the requirement.

## The ID lifecycle

```
mint ──▶ active ──▶ (redefined: still active, newest text wins)
                 ──▶ superseded by another ID   ─┐
                 ──▶ retired                     ─┴─▶ closed, forever
```

- **Mint**: first appearance of an ID defines it. Use
  `fold_spec.py next-id PREFIX` — it accounts for closed IDs too, so numbers
  are never reused.
- **Redefine**: a later entry repeats the same ID with new text. The fold
  keeps the newest text and records provenance (`[0002 → 0007]` = born in
  0002, last modified in 0007). This is the normal way to change a
  requirement — the ID is the stable handle, the redefinition is the new
  value.
- **Supersede**: `- **API-11** (supersedes API-4, API-5): …` closes API-4 and
  API-5 and points readers at API-11. Use when restructuring — merging or
  splitting requirements — where "same ID, new text" would be misleading.
- **Retire**: removal with no replacement; see [Retires](#retires).
- **No revival.** Once closed, an ID never comes back; mint a new one. The
  fold treats revival as an error. Why: anything that ever referenced the old
  ID (tests, commits, conversations) must keep meaning the thing that was
  closed, or history stops being trustworthy.

## Feature blocks

```markdown
## Feature: API — Public HTTP API

Everything callers can reach over HTTP. Versioned under /v1.
```

A feature block sets the section title and description for a prefix in
SPEC.md. Like requirements, it folds: the newest feature block for a prefix
wins. It's optional — a prefix with no block still gets a section, titled by
the bare prefix.

## Retires

```markdown
## Retires

- **API-6**: CSV export is removed from the public API.
```

The text after the ID is the reason, shown in SPEC.md's "Closed
requirements" section. Always give one — a removal without a reason invites
someone to reintroduce the behavior later. Retiring an ID that doesn't exist
or is already closed is a validation error.

## Choosing prefixes

A prefix is a feature area: `AUTH`, `API`, `BILLING`, `CLI`. Mint a new
prefix when requirements stop fitting existing areas — no registration
needed, the first use creates it. Prefer a handful of broad prefixes over
many narrow ones; the prefix is for navigation, the requirement text carries
the precision.

## Writing good requirements

One testable behavior per ID, stated as *what*, with concrete values.
RFC-2119 verbs: MUST (hard contract), SHOULD (strong default), MAY
(explicitly permitted).

| | |
| --- | --- |
| ❌ Too vague | **API-9**: The API SHOULD be fast. |
| ✅ | **API-9**: Search requests MUST complete within 500 ms at p95. |
| ❌ Two behaviors | **AUTH-3**: Logins MUST be rate limited and lockouts MUST notify the user. |
| ✅ | **AUTH-3**: Five failed logins within 15 minutes MUST lock the account for 15 minutes. **AUTH-4**: A lockout MUST trigger a notification email to the account owner. |
| ❌ Implementation | **TASK-8**: Tasks MUST be stored in a `tasks` table with a B-tree index. |
| ✅ | **TASK-8**: Task lookups by ID MUST return in O(log n) or better. *(or just leave storage to the code)* |

Implementation detail belongs in the spec only when it IS the contract
(a wire format, a file layout another tool reads, a public URL shape).

## Worked examples

**Add behavior** — new IDs only:

```markdown
## Requirements
- **TASK-9**: Tasks MAY carry up to 10 string tags of 32 characters each.
```

**Change behavior** — redefine the same ID:

```markdown
## Why
Mobile clients struggle with 50-item pages.

## Requirements
- **TASK-3**: Task lists MUST be capped at 25 items per page.
```

**Restructure** — supersede:

```markdown
## Requirements
- **AUTH-7** (supersedes AUTH-2, AUTH-5): All authentication failures MUST
  return 401 with a JSON body {"error": <machine-readable code>}.
```

**Remove behavior** — retire:

```markdown
## Why
The CSV export saw no production use in six months.

## Retires
- **TASK-6**: CSV export removed; JSON export (TASK-5) remains.
```

**Clarify** (spec was silent; a bug dispute settled it) — treat as add or
redefine, and say so in Why:

```markdown
## Why
Bug #142 exposed that ordering of same-priority tasks was unspecified.

## Requirements
- **TASK-10**: Tasks with equal priority MUST be ordered by creation time,
  newest first.
```

## Concurrent branches

Two branches can each append an entry with the same number, or mint the same
requirement ID. Git won't conflict on new files — but the fold will. Whoever
merges second renumbers their entry file and re-mints colliding IDs (the
entry isn't merged yet, so this is not an edit of history), reruns `fold`,
and recommits. `check` in CI is what catches the case where nobody noticed.

## What does not belong in the spec

Task lists, code snippets, schedules, design alternatives that were not
chosen. The spec records *what the system should do*; PRs and design docs
record how and why-not-otherwise. Keeping entries lean is what keeps the
fold readable — it is the document everyone actually lives in.
