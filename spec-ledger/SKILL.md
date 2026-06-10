---
name: spec-ledger
description: >-
  Spec-driven development with an append-only spec ledger. The spec is the
  source of truth: code implements what the spec says, every behavior-changing
  PR carries a numbered ledger entry under specs/ledger/, and specs/SPEC.md is
  the generated, always-consistent view of the whole ledger. Use this skill
  whenever the repo contains a specs/ledger/ directory — every feature request,
  behavior change, bug fix, or "what should X do" question in such a repo goes
  through it, even if the user never says "spec". Also use it when the user
  mentions spec-driven development, writing or updating specs or requirements
  before coding, keeping specs in sync with code, auditing code against a
  spec, or adopting specs in an existing codebase.
---

# Spec Ledger

Spec-driven development where the spec works like a bank ledger: entries are
**append-only**, newer entries **override** older ones, and serializing
(folding) the ledger always yields one **consistent current view**. Code
exists to implement that view.

## The contract

1. **The spec is the source of truth.** When code and spec disagree, the spec
   wins: fix the code — or, if the new behavior is actually desired, append an
   entry that changes the spec. Never let code drift silently.
2. **The ledger is append-only.** Files in `specs/ledger/` are never edited
   after they merge. To change a requirement, append a new entry that
   redefines or retires it. Why this matters: reviewers approved those entries
   as written. Editing one rewrites history people already relied on — exactly
   like editing a posted bank transaction. Corrections are new transactions.
3. **`specs/SPEC.md` is generated, never hand-edited.** It is the fold of the
   ledger. Regenerate it with `python specs/fold_spec.py fold` after appending
   an entry.
4. **Spec and code travel together.** A behavior-changing PR contains: the new
   ledger entry, the regenerated `SPEC.md`, the implementation, and tests that
   cite the requirement IDs they verify.

## Recognizing the situation

| Situation | Do this |
| --- | --- |
| Repo has `specs/ledger/` and the user asks for any feature, change, or fix | **Making a change** below — even if they never mention specs |
| User wants spec-driven development in a brand-new project | **Init** below |
| Existing codebase without a ledger; user wants to adopt specs | **Bootstrap** — read [references/bootstrap.md](references/bootstrap.md) |
| "Does the code still match the spec?" | **Audit** below |
| "What is X supposed to do?" | Read `specs/SPEC.md` and answer, citing requirement IDs |

## Does this change need a ledger entry?

An entry is needed **iff the change alters what the system should do** —
behavior added, changed, or removed.

- New feature, changed limit, different response shape, removed capability → entry.
- Refactor, perf work with identical observable behavior, dependency bump → no entry.
- Bug fix where the spec already says the right thing → no entry. The code was
  simply wrong; cite the violated requirement ID in the commit/PR instead.
- Bug fix that reveals the spec is silent or wrong → entry (clarify the spec)
  shipped together with the fix.

## Making a change

1. **Read the current view.** Run `python specs/fold_spec.py check`, then read
   `specs/SPEC.md`. If check reports staleness, run `fold` and inspect the
   diff before trusting the view.
2. **Decide** whether an entry is needed (rule above). If not, implement and
   cite the relevant requirement IDs in the commit message.
3. **Draft the entry.** `python specs/fold_spec.py new "Short title"`
   scaffolds the next-numbered file. Fill in Why and Requirements. Mint new
   IDs with `next-id <PREFIX>`; reuse an existing ID to redefine it; list
   removals under `## Retires`. Format essentials below; full details in
   [references/entry-format.md](references/entry-format.md).
4. **Fold.** `python specs/fold_spec.py fold` — fix any validation errors.
   The resulting `SPEC.md` diff is the contract for this change; it should
   read exactly like what the user asked for.
5. **Sync with the user.** In an interactive session, show the entry (or the
   SPEC.md diff) before implementing — correcting a sentence is far cheaper
   than correcting an implementation. Working autonomously, proceed, and put
   the entry front and center in your summary.
6. **Implement to the folded spec.** Satisfy every requirement you added or
   redefined; delete code for anything retired.
7. **Test against IDs.** Every new or changed MUST requirement gets at least
   one test that cites its ID — put `[API-7]` in the test name or docstring.
   This is what makes audits mechanical later.
8. **Close the loop.** `python specs/fold_spec.py check` passes, the test
   suite passes, and the commit/PR message references the entry number and
   the requirement IDs it touched.

## Entry format (essentials)

`specs/ledger/0007-rate-limiting.md`:

```markdown
---
title: Rate limiting for the public API
date: 2026-06-10
---

## Why

Abuse incidents on /search; we need per-key limits.

## Requirements

- **API-9**: Public endpoints MUST enforce a rate limit of 100 requests
  per minute per API key.
- **API-10**: Rate-limited responses MUST return HTTP 429 with a
  Retry-After header.
- **API-3**: Search results MUST be capped at 50 items per page.
- **API-11** (supersedes API-4, API-5): Authentication failures MUST return
  401 with a machine-readable error code.

## Retires

- **API-6**: CSV export is removed from the public API.
```

The override semantics, in ledger terms:

- New ID (`API-9`, `API-10`) → **new requirement**. Mint with `next-id API`.
- Existing ID (`API-3`) → **redefinition**; at fold time the newest text wins.
- `(supersedes API-4, API-5)` → those requirements are **closed and replaced**
  by this one. Use when restructuring, not for simple edits.
- `## Retires` → behavior **removed** with no replacement.
- IDs are never reused or revived once closed — mint a fresh one. The fold
  script validates all of this and refuses to serialize an inconsistent ledger.

Requirement style: one testable behavior per ID; MUST/SHOULD/MAY; concrete
values; describe *what* the system does, not how it's implemented. Read
[references/entry-format.md](references/entry-format.md) before writing your
first entry of a session, and whenever an entry involves supersedes, retires,
or feature description blocks.

## The fold script

`specs/fold_spec.py` is self-contained (Python 3.8+, stdlib only). If a
ledger repo is missing it, copy it from this skill's `scripts/fold_spec.py`.

```
python specs/fold_spec.py new "Title here"   # scaffold the next-numbered entry
python specs/fold_spec.py next-id API        # next free requirement number for a prefix
python specs/fold_spec.py validate           # lint: duplicate/revived/unknown IDs, parse problems
python specs/fold_spec.py fold               # validate + regenerate specs/SPEC.md
python specs/fold_spec.py check              # validate + fail if SPEC.md is stale (CI-friendly)
```

## Init (new project)

1. Create `specs/ledger/` and copy this skill's `scripts/fold_spec.py` to
   `specs/fold_spec.py`.
2. Write `0001-<project-slug>.md` capturing the initial intended behavior —
   even if it's three requirements. The first entry is just the first
   transaction, not a grand design document.
3. `python specs/fold_spec.py fold`, then implement to the view.
4. Offer CI: a job running `python specs/fold_spec.py check` plus the test
   suite keeps ledger, view, and code from drifting on every PR.

## Audit (code ↔ spec drift)

1. `python specs/fold_spec.py check` — the view must match the ledger before
   anything else is checked against it.
2. For every active requirement in `SPEC.md`, look for evidence: implementing
   code, and tests citing the ID. Grep for the IDs first; read the code where
   grep comes up empty.
3. Classify each requirement: **implemented** (code + citing test) /
   **untested** (code, but no test cites it) / **missing** (no code) /
   **divergent** (code does something else).
4. Report a table with file:line evidence per requirement. Then resolve:
   the spec wins, so fix divergent and missing code — unless the user declares
   the current behavior correct, in which case append a corrective entry.
   Never edit old entries or hand-edit SPEC.md to make an audit pass.
