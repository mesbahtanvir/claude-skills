#!/usr/bin/env python3
"""Fold append-only spec entries into a single consistent view.

A spec-driven repo keeps numbered, append-only entry files
(specs/entries/0001-some-title.md). Each entry adds, redefines, supersedes,
or retires requirements. Folding replays the entries in numeric order —
newest wins — and writes specs/SPEC.md, the current consistent view.

Self-contained: Python 3.8+, standard library only. This file is meant to be
copied into a repo at specs/fold_spec.py and committed alongside the entries.

Commands:
    fold            validate + regenerate SPEC.md
    check           validate + exit 1 if SPEC.md is missing or stale (CI)
    validate        lint the spec entries
    new TITLE...    scaffold the next-numbered entry file
    next-id PREFIX  print the next free requirement number for a prefix
"""

import argparse
import datetime
import re
import sys
from pathlib import Path

ENTRY_FILE_RE = re.compile(r"^(\d+)-(.+)\.md$")
REQ_RE = re.compile(
    r"^-\s+\*\*([A-Z][A-Z0-9]*-\d+)\*\*\s*"
    r"(?:\(\s*supersedes\s+([^)]*)\)\s*)?"
    r"[:—–-]\s+(.+)$"
)
REQ_LOOKSLIKE_RE = re.compile(r"^-\s+\*\*\S+.*\*\*")
RETIRE_RE = re.compile(r"^-\s+\*\*([A-Z][A-Z0-9]*-\d+)\*\*\s*(?:[:—–-]\s+(.+))?$")
FEATURE_HEAD_RE = re.compile(r"^##\s+Feature:\s*([A-Z][A-Z0-9]*)\s*[—–-]+\s*(.+)$")
RETIRES_HEAD_RE = re.compile(r"^##\s+Retire[sd]?\s*$", re.IGNORECASE)
ID_RE = re.compile(r"^([A-Z][A-Z0-9]*)-(\d+)$")
ID_TOKEN_RE = re.compile(r"[A-Z][A-Z0-9]*-\d+")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

NEW_TEMPLATE = """---
title: {title}
date: {date}
---

## Why

<!-- 1-3 sentences: what motivates this change. -->

## Requirements

<!--
- **PREFIX-N**: One testable MUST/SHOULD/MAY statement.
Reuse an existing ID to redefine it (newest text wins at fold time).
`python specs/fold_spec.py next-id PREFIX` mints the next free number.
-->

## Retires

<!-- - **PREFIX-N**: why this behavior is removed. Delete this section if nothing is retired. -->
"""


class Entry:
    def __init__(self, number, path):
        self.number = number
        self.path = path
        self.title = None
        self.date = None
        self.requirements = []  # (id, [superseded ids], text)
        self.retires = []       # (id, reason)
        self.features = {}      # prefix -> {"title": str, "desc": [lines]}


def parse_entry(path, number, warnings):
    entry = Entry(number, path)
    text = COMMENT_RE.sub("", path.read_text(encoding="utf-8"))
    lines = text.splitlines()

    i = 0
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            if ":" in lines[i]:
                key, val = lines[i].split(":", 1)
                key, val = key.strip().lower(), val.strip()
                if key == "title":
                    entry.title = val
                elif key == "date":
                    entry.date = val
            i += 1
        i += 1
    if not entry.title:
        warnings.append(f"{path.name}: no title in frontmatter; using filename slug")
        entry.title = ENTRY_FILE_RE.match(path.name).group(2).replace("-", " ")

    section = None        # None | "retires" | ("feature", prefix)
    last_req = None       # last requirement dict, for continuation lines

    for raw in lines[i:]:
        if not raw.strip():
            last_req = None
            continue

        if raw.lstrip().startswith("#"):
            last_req = None
            line = raw.strip()
            fmatch = FEATURE_HEAD_RE.match(line)
            if fmatch:
                prefix = fmatch.group(1)
                section = ("feature", prefix)
                entry.features[prefix] = {"title": fmatch.group(2).strip(), "desc": []}
            elif RETIRES_HEAD_RE.match(line):
                section = "retires"
            elif line.startswith("##"):
                section = None
            continue

        # Continuation of a wrapped requirement bullet.
        if last_req is not None and raw.startswith("  ") and not raw.lstrip().startswith("- "):
            last_req["text"] += " " + raw.strip()
            continue
        last_req = None

        line = raw.strip()

        if section == "retires":
            rmatch = RETIRE_RE.match(line)
            if rmatch:
                entry.retires.append((rmatch.group(1), (rmatch.group(2) or "").strip()))
            elif REQ_LOOKSLIKE_RE.match(line):
                warnings.append(f"{path.name}: unparseable retire line: {line!r}")
            continue

        rmatch = REQ_RE.match(line)
        if rmatch:
            rid, sup_raw, rtext = rmatch.group(1), rmatch.group(2), rmatch.group(3)
            supersedes = ID_TOKEN_RE.findall(sup_raw) if sup_raw else []
            req = {"id": rid, "supersedes": supersedes, "text": rtext.strip()}
            entry.requirements.append(req)
            last_req = req
            if isinstance(section, tuple) and section[0] == "feature":
                pass  # requirements under a feature heading are fine; prefix comes from the ID
        elif REQ_LOOKSLIKE_RE.match(line):
            warnings.append(
                f"{path.name}: looks like a requirement but did not parse "
                f"(check the '**PREFIX-N**: text' shape): {line!r}"
            )
        elif isinstance(section, tuple) and section[0] == "feature":
            entry.features[section[1]]["desc"].append(line)

    return entry


def load_entries(entries_dir, errors, warnings):
    entries = []
    seen_numbers = {}
    if not entries_dir.is_dir():
        errors.append(f"entries directory not found: {entries_dir}")
        return entries
    for path in sorted(entries_dir.iterdir()):
        if not path.is_file():
            continue
        m = ENTRY_FILE_RE.match(path.name)
        if not m:
            if path.suffix == ".md":
                warnings.append(f"{path.name}: ignored (not NNNN-slug.md)")
            continue
        number = int(m.group(1))
        if number in seen_numbers:
            errors.append(
                f"duplicate entry number {number:04d}: {seen_numbers[number]} and {path.name}"
            )
            continue
        seen_numbers[number] = path.name
        entries.append(parse_entry(path, number, warnings))
    entries.sort(key=lambda e: e.number)
    return entries


def replay(entries, errors, warnings):
    """Replay the entries in order. Returns (active, closed, features)."""
    active = {}    # id -> {"text", "born", "last"}
    closed = {}    # id -> {"kind": "superseded"|"retired", "by", "entry", "reason"}
    features = {}  # prefix -> {"title", "desc", "entry"}

    for e in entries:
        fname = e.path.name
        defined_here = set()

        for req in e.requirements:
            rid = req["id"]
            if rid in defined_here:
                errors.append(f"{fname}: {rid} defined twice in the same entry")
                continue
            defined_here.add(rid)

            if rid in closed:
                errors.append(
                    f"{fname}: {rid} was closed in entry "
                    f"{closed[rid]['entry']:04d} and cannot be redefined — mint a new ID"
                )
                continue

            if rid in active:
                active[rid]["text"] = req["text"]
                active[rid]["last"] = e.number
            else:
                active[rid] = {"text": req["text"], "born": e.number, "last": e.number}

            for old in req["supersedes"]:
                if old == rid:
                    errors.append(f"{fname}: {rid} cannot supersede itself")
                elif old in closed:
                    errors.append(
                        f"{fname}: {rid} supersedes {old}, which was already closed "
                        f"in entry {closed[old]['entry']:04d}"
                    )
                elif old not in active:
                    errors.append(f"{fname}: {rid} supersedes unknown requirement {old}")
                else:
                    del active[old]
                    closed[old] = {"kind": "superseded", "by": rid, "entry": e.number, "reason": ""}

        for rid, reason in e.retires:
            if rid in defined_here:
                warnings.append(f"{fname}: {rid} is both defined and retired in the same entry")
            if rid in closed:
                errors.append(
                    f"{fname}: cannot retire {rid}; already closed in entry "
                    f"{closed[rid]['entry']:04d}"
                )
            elif rid not in active:
                errors.append(f"{fname}: cannot retire unknown requirement {rid}")
            else:
                del active[rid]
                closed[rid] = {"kind": "retired", "by": None, "entry": e.number, "reason": reason}

        for prefix, feat in e.features.items():
            features[prefix] = {
                "title": feat["title"],
                "desc": " ".join(feat["desc"]).strip(),
                "entry": e.number,
            }

    return active, closed, features


def id_sort_key(rid):
    prefix, num = ID_RE.match(rid).groups()
    return (prefix, int(num))


def render(entries, active, closed, features):
    last = max(e.number for e in entries)
    lines = [
        "# Specification",
        "",
        "> **Generated — do not edit.** This file is the fold of `specs/entries/`.",
        "> To change the spec, append a new entry and run"
        " `python specs/fold_spec.py fold`.",
        "",
        f"_{len(entries)} spec entries folded (latest: {last:04d}) — "
        f"{len(active)} active requirements, {len(closed)} closed._",
        "",
    ]

    prefixes = sorted({ID_RE.match(rid).group(1) for rid in active})
    for prefix in prefixes:
        feat = features.get(prefix)
        lines.append(f"## {prefix} — {feat['title']}" if feat else f"## {prefix}")
        lines.append("")
        if feat and feat["desc"]:
            lines.append(feat["desc"])
            lines.append("")
        ids = sorted((r for r in active if r.startswith(prefix + "-")), key=id_sort_key)
        for rid in ids:
            req = active[rid]
            prov = f"{req['born']:04d}"
            if req["last"] != req["born"]:
                prov += f" → {req['last']:04d}"
            lines.append(f"- **{rid}** — {req['text']} _[{prov}]_")
        lines.append("")

    if closed:
        lines.append("## Closed requirements")
        lines.append("")
        for rid in sorted(closed, key=id_sort_key):
            t = closed[rid]
            if t["kind"] == "superseded":
                lines.append(f"- **{rid}** — superseded by **{t['by']}** in {t['entry']:04d}")
            else:
                reason = f": {t['reason']}" if t["reason"] else ""
                lines.append(f"- **{rid}** — retired in {t['entry']:04d}{reason}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def resolve_specs_dir(arg):
    if arg:
        return Path(arg)
    script_dir = Path(__file__).resolve().parent
    if (script_dir / "entries").is_dir():
        return script_dir
    return Path("specs")


def report(errors, warnings):
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    for e in errors:
        print(f"error: {e}", file=sys.stderr)


def slugify(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "entry"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", help="specs directory (default: the script's own directory "
                                      "if it contains entries/, else ./specs)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fold", help="validate + regenerate SPEC.md")
    sub.add_parser("check", help="validate + fail if SPEC.md is missing or stale")
    sub.add_parser("validate", help="lint the spec entries")
    p_new = sub.add_parser("new", help="scaffold the next-numbered entry")
    p_new.add_argument("title", nargs="+")
    p_next = sub.add_parser("next-id", help="next free requirement number for a prefix")
    p_next.add_argument("prefix")
    args = parser.parse_args()

    specs_dir = resolve_specs_dir(args.dir)
    entries_dir = specs_dir / "entries"
    spec_path = specs_dir / "SPEC.md"

    if args.command == "new":
        entries_dir.mkdir(parents=True, exist_ok=True)
        numbers = [
            int(ENTRY_FILE_RE.match(p.name).group(1))
            for p in entries_dir.iterdir()
            if p.is_file() and ENTRY_FILE_RE.match(p.name)
        ]
        number = max(numbers) + 1 if numbers else 1
        title = " ".join(args.title)
        path = entries_dir / f"{number:04d}-{slugify(title)}.md"
        path.write_text(
            NEW_TEMPLATE.format(title=title, date=datetime.date.today().isoformat()),
            encoding="utf-8",
        )
        print(path)
        return 0

    errors, warnings = [], []
    entries = load_entries(entries_dir, errors, warnings)
    if not entries and not errors:
        errors.append(f"no spec entries found in {entries_dir}")
    active, closed, features = replay(entries, errors, warnings) if entries else ({}, {}, {})

    if args.command == "next-id":
        prefix = args.prefix.upper()
        nums = [
            int(ID_RE.match(rid).group(2))
            for rid in list(active) + list(closed)
            if ID_RE.match(rid).group(1) == prefix
        ]
        print(f"{prefix}-{max(nums) + 1 if nums else 1}")
        return 0

    report(errors, warnings)
    if errors:
        return 1

    if args.command == "validate":
        print(f"ok: {len(entries)} entries, {len(active)} active requirements, "
              f"{len(closed)} closed" + (f", {len(warnings)} warning(s)" if warnings else ""))
        return 0

    rendered = render(entries, active, closed, features)

    if args.command == "fold":
        spec_path.write_text(rendered, encoding="utf-8")
        print(f"folded {len(entries)} entries -> {spec_path} "
              f"({len(active)} active, {len(closed)} closed)")
        return 0

    if args.command == "check":
        if not spec_path.exists():
            print(f"error: {spec_path} does not exist — run: python {sys.argv[0]} fold",
                  file=sys.stderr)
            return 1
        if spec_path.read_text(encoding="utf-8") != rendered:
            print(f"error: {spec_path} is stale — run: python {sys.argv[0]} fold",
                  file=sys.stderr)
            return 1
        print(f"{spec_path} is up to date")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
