#!/usr/bin/env python3
"""Structural proof of the foundation-update ritual (task: foundation-update-loop, v5).

foundation-update-loop CLOSES the self-improving loop: competency-deltas lets a task EMIT learnings;
this ritual FOLDS the confirmed ones into a versioned foundation. It is JUDGMENT (gather → propose →
human confirm → append-only write), so the deliverable is a rubric (skill/add/fold.md) + a
`foundation-version:` marker in PROJECT.md — NOT engine logic. The red/green guard asserts STRUCTURE:
the rubric exists in both skill trees (md5 parity), documents the ritual, the fold routing for all
five competencies (DDD/SDD/UDD→PROJECT.md sections, TDD/ADD→CONVENTIONS.md, all→§Key Decisions), the
status transitions, append-only+version-bump, the trigger convention, and the three reject codes;
add.py gains NO fold command; PROJECT.md carries the version marker; the worked example cites real
history; and the "Foundation version" glossary entry is present across the three doc trees. Exactly
12 tests — frozen @ v2 (test 12 added by change-request 2026-06-03, closing the v5 disclosed gap:
the glossary entry was built but unguarded). (The mechanical delta counter is convergence-signal.)

Run: python3 -m unittest test_foundation_update_loop -v
"""
import hashlib
import re
import unittest
from pathlib import Path

# Resolve repo paths from THIS file, not cwd: tooling/ -> add-method/ -> repo root.
_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CANONICAL_FOLD = _ADD_METHOD / "skill" / "add" / "fold.md"
DOGFOOD_FOLD = _REPO / ".claude" / "skills" / "add" / "fold.md"
CANONICAL_SKILL = _ADD_METHOD / "skill" / "add" / "SKILL.md"
DOGFOOD_SKILL = _REPO / ".claude" / "skills" / "add" / "SKILL.md"
ADD_PY = _ADD_METHOD / "tooling" / "add.py"
PROJECT_MD = _REPO / ".add" / "PROJECT.md"

# The three shipped doc trees the contract names — canonical, bundled (published package), dogfood.
# (Byte-parity across trees is test_bundle_parity.py's job; here we guard the ENTRY's presence.)
GLOSSARY_TREES = (
    _ADD_METHOD / "docs" / "appendix-c-glossary.md",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "docs" / "appendix-c-glossary.md",
    _REPO / ".add" / "docs" / "appendix-c-glossary.md",
)

COMPETENCIES = {"DDD", "SDD", "UDD", "TDD", "ADD"}
REJECT_CODES = {"no_open_deltas", "unconfirmed_fold", "unroutable_delta"}


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _fold_text() -> str:
    return CANONICAL_FOLD.read_text(encoding="utf-8")


def _worked_example_section(text: str) -> str:
    m = re.search(r"^#+\s*worked example.*$", text, flags=re.IGNORECASE | re.MULTILINE)
    return text[m.start():] if m else ""


class FoundationUpdateLoopTest(unittest.TestCase):
    def test_fold_exists_in_both_trees_with_md5_parity(self):
        self.assertTrue(CANONICAL_FOLD.exists(), f"missing {CANONICAL_FOLD}")
        self.assertTrue(DOGFOOD_FOLD.exists(), f"missing {DOGFOOD_FOLD}")
        self.assertEqual(_md5(CANONICAL_FOLD), _md5(DOGFOOD_FOLD),
                         "fold.md differs between the canonical and dogfood skill trees")

    def test_documents_the_ritual_sequence(self):
        low = _fold_text().lower()
        for step in ("gather", "propose", "confirm"):
            self.assertIn(step, low, f"fold.md does not document the '{step}' step")
        self.assertTrue(re.search(r"fold|write|append", low),
                        "fold.md does not document the write/fold step")

    def test_documents_fold_routing_all_five_plus_key_decisions(self):
        text = _fold_text()
        for c in COMPETENCIES:
            self.assertIn(c, text, f"fold.md routing omits the '{c}' competency")
        self.assertIn("CONVENTIONS.md", text, "fold.md must route TDD/ADD to CONVENTIONS.md")
        self.assertIn("PROJECT.md", text, "fold.md must route DDD/SDD/UDD to PROJECT.md")
        self.assertIsNotNone(re.search(r"key decisions", text, re.IGNORECASE),
                             "fold.md must state the §Key Decisions universal audit row")

    def test_documents_status_transitions(self):
        text = _fold_text()
        low = text.lower()
        self.assertIn("folded", low, "fold.md must document the 'folded' transition")
        self.assertIn("rejected", low, "fold.md must document the 'rejected' transition")
        self.assertIsNotNone(
            re.search(r"reject\w*.{0,80}(left in place|not delet|in place)|"
                      r"(left in place|not delet|in place).{0,80}reject", low, re.DOTALL),
            "fold.md must state a rejected delta is left in place (auditable)")

    def test_states_append_only_and_version_bump(self):
        low = _fold_text().lower()
        self.assertIn("append", low, "fold.md must state folds are append-only")
        self.assertIn("foundation-version", low, "fold.md must reference foundation-version")
        self.assertTrue(re.search(r"bump|increment|advance", low),
                        "fold.md must state the version bumps on a fold")

    def test_states_trigger_convention(self):
        low = _fold_text().lower()
        self.assertTrue(re.search(r"milestone clos|on demand|on-demand", low),
                        "fold.md must state the trigger (milestone close / on demand)")

    def test_add_py_exposes_no_fold_command(self):
        src = ADD_PY.read_text(encoding="utf-8")
        m = re.search(r'add_parser\(\s*["\'](fold|foundation)["\']', src)
        self.assertIsNone(
            m, "add.py must NOT gain a fold/foundation subcommand (engine stays judgment-free)")

    def test_documents_all_three_reject_codes(self):
        text = _fold_text()
        for code in REJECT_CODES:
            self.assertIn(code, text, f"fold.md does not document the '{code}' reject code")

    def test_project_md_carries_foundation_version_marker(self):
        text = PROJECT_MD.read_text(encoding="utf-8")
        self.assertIsNotNone(
            re.search(r"foundation-version:\s*\d+", text),
            ".add/PROJECT.md must carry a 'foundation-version: <int>' marker")

    def test_skill_md_links_fold_and_both_trees_identical(self):
        for skill in (CANONICAL_SKILL, DOGFOOD_SKILL):
            self.assertIn("fold.md", skill.read_text(encoding="utf-8"),
                          f"{skill} does not point to fold.md")
        self.assertEqual(_md5(CANONICAL_SKILL), _md5(DOGFOOD_SKILL),
                         "the two SKILL.md copies are not byte-identical")

    def test_worked_example_references_real_history(self):
        section = _worked_example_section(_fold_text())
        self.assertTrue(section, "fold.md has no 'worked example' section")
        self.assertIn("competency-deltas", section,
                      "fold.md's worked example should cite the real competency-deltas task")

    def test_glossary_defines_foundation_version_in_all_three_trees(self):
        # Change-request test 12 (frozen @ v2): the contract ships a "Foundation version" glossary
        # entry across three doc trees; v5 built it but left it unguarded. Guard its PRESENCE here
        # (byte-parity stays test_bundle_parity.py's job — no redundant md5 check).
        #
        # The third tree (.add/docs) is the dogfood install, which is gitignored and
        # regenerated on `add.py init` — so it is ABSENT on a clean checkout / CI. Guard
        # the PRESENT trees and require the two tracked sources (canonical + bundle),
        # mirroring test_flow_diagram's present-trees pattern. Asserting all three exist
        # would fail in CI on a directory that is never a committed source.
        present = [t for t in GLOSSARY_TREES if t.exists()]
        self.assertGreaterEqual(
            len(present), 2,
            "expected at least the canonical + bundled glossary trees to be present")
        for tree in present:
            self.assertIsNotNone(
                re.search(r"\*\*Foundation version\*\*", tree.read_text(encoding="utf-8"),
                          re.IGNORECASE),
                f"{tree} has no 'Foundation version' entry")


if __name__ == "__main__":
    unittest.main(verbosity=2)
