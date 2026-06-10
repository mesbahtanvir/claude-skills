# Bootstrapping a ledger in an existing codebase

Goal: an existing repo gains `specs/ledger/` whose fold accurately describes
what the code does **today**. The genesis entries are an opening balance, not
a wish list — if the first audit after bootstrap finds drift, the bootstrap
was done wrong.

## 1. Inventory actual behavior

Read, in rough priority order:

- Tests — the closest thing to an existing spec; each asserting test is a
  candidate requirement.
- Public surface — routes, CLI commands, exported functions, config options.
- README / docs — but verify claims against code; docs lie, tests mostly don't.
- Error paths and limits — timeouts, caps, validation rules, defaults. These
  are the requirements people forget to write down and then fight about.

Note behaviors that look accidental or buggy. Do not spec those yet — list
them for the user instead (see step 4).

## 2. Choose feature areas

Group the surface into 2–6 prefixes (`API`, `CLI`, `STORE`, …). Match the
vocabulary the codebase already uses — the spec should read like the project,
not like a template.

## 3. Write genesis entries

One entry per feature area keeps reviews focused: `0001-<area>.md`,
`0002-<area>.md`, … Each starts with a `## Feature:` block, then requirements
for current behavior.

Calibration:

- **Spec the load-bearing.** What users rely on, what tests assert, what
  would be a breaking change if altered. Skip internal helpers and anything
  you'd freely refactor.
- **Describe what IS.** If the code caps pages at 50, write 50 — even if 25
  would be better. Improvements come as ordinary entries afterward, so the
  ledger shows the change happening (that's its job).
- **Small is fine.** A 10-requirement genesis that's accurate beats a
  60-requirement one that's aspirational.

In Why, note it's a genesis entry: "Genesis: records behavior as of <commit>."

## 4. Surface the judgment calls

Ambiguous behaviors — probable bugs, half-built features, accidental
behavior — are decisions, not transcription. Present them to the user:

> The code returns 200 with an empty list for an unknown user ID. Bug or
> contract? If contract, I'll spec it; if bug, I'll leave it out and we fix
> it in a follow-up entry + fix PR.

If working autonomously, spec the behavior that tests assert, leave the rest
unspecced, and list every judgment call prominently in the summary.

## 5. Install and fold

1. Copy the skill's `scripts/fold_spec.py` → `specs/fold_spec.py`.
2. `python specs/fold_spec.py fold` — fix validation errors.
3. Run an audit (SKILL.md) against the fresh SPEC.md. Every requirement
   should come up **implemented** or **untested** — a **missing** or
   **divergent** result means a genesis entry over-claimed; fix the entry
   (pre-merge, so editing is still allowed).
4. Tests that map to requirements: add ID citations (`[API-3]`) to existing
   test names/docstrings where the mapping is clear. Untested requirements
   are normal at bootstrap — note them as candidates for new tests rather
   than blocking on full coverage.
5. Offer the CI check (`python specs/fold_spec.py check` + tests) so the
   ledger discipline holds from the first PR after adoption.

After this, the repo behaves like any ledger repo: changes go through
"Making a change" in SKILL.md, and the genesis entries are never edited again.
