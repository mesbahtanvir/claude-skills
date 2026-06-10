"""Conformance tests for the spec-driven system, citing the requirement IDs
they verify (see specs/SPEC.md). Run: python -m unittest discover -s tests
"""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "specs" / "fold_spec.py"

SKIP_DIRS = {".git", ".github", "specs", "tests"}


def entry(title, body):
    return f"---\ntitle: {title}\ndate: 2026-06-10\n---\n\n{body}\n"


class EntriesCase(unittest.TestCase):
    """Base: a throwaway specs dir and a CLI helper."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.specs = Path(tmp.name) / "specs"
        (self.specs / "entries").mkdir(parents=True)

    def write(self, name, text):
        (self.specs / "entries" / name).write_text(text, encoding="utf-8")

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--dir", str(self.specs), *args],
            capture_output=True, text=True,
        )

    def spec_text(self):
        return (self.specs / "SPEC.md").read_text(encoding="utf-8")


class TestFoldSemantics(EntriesCase):
    def test_redefinition_newest_text_wins(self):
        """[SPEC-4] Re-declaring an active ID redefines it; newest wins."""
        self.write("0001-a.md", entry("A", "- **API-1**: Pages MUST be capped at 50 items."))
        self.write("0002-b.md", entry("B", "- **API-1**: Pages MUST be capped at 25 items."))
        result = self.cli("fold")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("capped at 25", self.spec_text())
        self.assertNotIn("capped at 50", self.spec_text())

    def test_entries_replayed_in_numeric_order(self):
        """[SPEC-1] Numeric order, not lexical order, decides the replay."""
        self.write("9-old.md", entry("Old", "- **API-1**: Value MUST be old."))
        self.write("0010-new.md", entry("New", "- **API-1**: Value MUST be new."))
        self.assertEqual(self.cli("fold").returncode, 0)
        self.assertIn("MUST be new", self.spec_text())

    def test_continuation_lines_join_statement(self):
        """[SPEC-3] Two-space continuations are part of the requirement."""
        self.write("0001-a.md", entry(
            "A", "- **API-1**: The statement MUST wrap across\n  two source lines."))
        self.assertEqual(self.cli("fold").returncode, 0)
        self.assertIn("MUST wrap across two source lines", self.spec_text())

    def test_supersede_and_retire_close_ids(self):
        """[SPEC-5][SPEC-6][FOLD-3] Closed IDs are listed with cause."""
        self.write("0001-a.md", entry("A", (
            "- **API-1**: Old auth error MUST be a string.\n"
            "- **API-2**: CSV export MUST exist.\n"
            "- **API-3**: Pages MUST be capped."
        )))
        self.write("0002-b.md", entry("B", (
            "- **API-4** (supersedes API-1): Auth errors MUST be JSON.\n"
            "\n"
            "## Retires\n"
            "\n"
            "- **API-2**: Export feature removed."
        )))
        self.assertEqual(self.cli("fold").returncode, 0)
        spec = self.spec_text()
        self.assertIn("## Closed requirements", spec)
        self.assertIn("superseded by **API-4** in 0002", spec)
        self.assertIn("retired in 0002: Export feature removed.", spec)
        active_section = spec.split("## Closed requirements")[0]
        self.assertNotIn("API-1**", active_section)
        self.assertNotIn("API-2**", active_section)

    def test_feature_block_newest_wins(self):
        """[SPEC-8] The newest Feature block per prefix sets the section."""
        self.write("0001-a.md", entry("A", (
            "## Feature: API — Alpha title\n\nAlpha description.\n\n"
            "- **API-1**: Something MUST hold."
        )))
        self.write("0002-b.md", entry("B", "## Feature: API — Beta title\n\nBeta description."))
        self.assertEqual(self.cli("fold").returncode, 0)
        self.assertIn("## API — Beta title", self.spec_text())
        self.assertIn("Beta description.", self.spec_text())
        self.assertNotIn("Alpha", self.spec_text())


class TestFoldOutput(EntriesCase):
    def test_fold_is_deterministic(self):
        """[FOLD-1] Folding the same entries twice yields identical bytes."""
        self.write("0001-a.md", entry("A", "- **API-1**: X MUST hold."))
        self.assertEqual(self.cli("fold").returncode, 0)
        first = self.spec_text()
        self.assertEqual(self.cli("fold").returncode, 0)
        self.assertEqual(first, self.spec_text())

    def test_provenance_markers(self):
        """[FOLD-2] Requirements carry born and last-modified entry numbers."""
        self.write("0001-a.md", entry("A", (
            "- **API-1**: Stable MUST hold.\n"
            "- **API-2**: Original MUST hold."
        )))
        self.write("0002-b.md", entry("B", "- **API-2**: Changed MUST hold."))
        self.assertEqual(self.cli("fold").returncode, 0)
        spec = self.spec_text()
        self.assertIn("_[0001]_", spec)
        self.assertIn("_[0001 → 0002]_", spec)


class TestGuardrails(EntriesCase):
    def test_check_fails_when_stale_or_missing(self):
        """[FOLD-4] check exits nonzero on a missing or stale SPEC.md."""
        self.write("0001-a.md", entry("A", "- **API-1**: X MUST hold."))
        self.assertEqual(self.cli("check").returncode, 1)  # missing
        self.assertEqual(self.cli("fold").returncode, 0)
        self.assertEqual(self.cli("check").returncode, 0)  # current
        spec_path = self.specs / "SPEC.md"
        spec_path.write_text(self.spec_text() + "tampered\n", encoding="utf-8")
        self.assertEqual(self.cli("check").returncode, 1)  # stale

    def test_validate_rejects_revival(self):
        """[SPEC-7][FOLD-5] A closed ID cannot be redefined."""
        self.write("0001-a.md", entry("A", "- **API-1**: X MUST hold.\n- **API-2**: Y MUST hold."))
        self.write("0002-b.md", entry("B", "## Retires\n\n- **API-1**: Removed."))
        self.write("0003-c.md", entry("C", "- **API-1**: Back from the dead."))
        result = self.cli("validate")
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot be redefined", result.stderr)

    def test_validate_rejects_unknown_and_duplicate(self):
        """[FOLD-5] Unknown supersede targets and same-entry duplicates fail."""
        self.write("0001-a.md", entry("A", (
            "- **API-1** (supersedes API-99): X MUST hold.\n"
            "- **API-2**: Y MUST hold.\n"
            "- **API-2**: Y duplicated."
        )))
        result = self.cli("validate")
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown requirement API-99", result.stderr)
        self.assertIn("defined twice", result.stderr)

    def test_validate_rejects_duplicate_entry_numbers(self):
        """[FOLD-5] Two files with the same entry number fail validation."""
        self.write("0001-a.md", entry("A", "- **API-1**: X MUST hold."))
        self.write("0001-b.md", entry("B", "- **API-2**: Y MUST hold."))
        result = self.cli("validate")
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate entry number", result.stderr)


class TestAuthoringHelpers(EntriesCase):
    def test_new_scaffolds_next_number(self):
        """[FOLD-6] new creates the next-numbered entry and prints its path."""
        self.write("0007-existing.md", entry("Existing", "- **API-1**: X MUST hold."))
        result = self.cli("new", "Add", "tag", "support")
        self.assertEqual(result.returncode, 0, result.stderr)
        path = Path(result.stdout.strip())
        self.assertEqual(path.name, "0008-add-tag-support.md")
        self.assertTrue(path.exists())
        self.assertIn("title: Add tag support", path.read_text(encoding="utf-8"))

    def test_next_id_never_reuses_closed_numbers(self):
        """[FOLD-7] next-id counts closed IDs too, so numbers never repeat."""
        self.write("0001-a.md", entry("A", "- **API-1**: X MUST hold.\n- **API-2**: Y MUST hold."))
        self.write("0002-b.md", entry("B", "## Retires\n\n- **API-2**: Removed."))
        result = self.cli("next-id", "API")
        self.assertEqual(result.stdout.strip(), "API-3")
        self.assertEqual(self.cli("next-id", "NEW").stdout.strip(), "NEW-1")


class TestRepoConformance(unittest.TestCase):
    def test_fold_script_is_stdlib_only(self):
        """[FOLD-8] fold_spec.py imports nothing outside the stdlib."""
        allowed = {"argparse", "datetime", "re", "sys", "pathlib"}
        source = SCRIPT.read_text(encoding="utf-8")
        imports = set(re.findall(r"^(?:import|from)\s+(\w+)", source, re.MULTILINE))
        self.assertTrue(imports <= allowed, f"unexpected imports: {imports - allowed}")

    def test_skills_declare_matching_names(self):
        """[REPO-1][REPO-2] Each skill dir has SKILL.md with name == dirname."""
        skill_dirs = [
            d for d in REPO.iterdir()
            if d.is_dir() and d.name not in SKIP_DIRS and not d.name.startswith(".")
        ]
        self.assertTrue(skill_dirs, "no skill directories found")
        for d in skill_dirs:
            skill_md = d / "SKILL.md"
            self.assertTrue(skill_md.exists(), f"{d.name}/SKILL.md missing")
            text = skill_md.read_text(encoding="utf-8")
            match = re.search(r"^name:\s*(\S+)\s*$", text, re.MULTILINE)
            self.assertIsNotNone(match, f"{d.name}/SKILL.md has no name field")
            self.assertEqual(match.group(1), d.name)
            self.assertIn("description:", text, f"{d.name}/SKILL.md has no description")

    def test_repo_fold_script_matches_skill_copy(self):
        """[REPO-5] specs/fold_spec.py is byte-identical to the skill's copy."""
        repo_copy = SCRIPT.read_bytes()
        skill_copy = (REPO / "spec-driven" / "scripts" / "fold_spec.py").read_bytes()
        self.assertEqual(repo_copy, skill_copy)

    def test_repo_spec_is_current(self):
        """[REPO-4][FOLD-4] This repository's own SPEC.md matches its entries."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "check"],
            capture_output=True, text=True, cwd=REPO,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
