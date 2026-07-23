#!/usr/bin/env python3
"""gate-experience-udd (milestone strategy-intake) — acceptance suite for the frozen §3
contract: the persona-owned gate report, physically folded into the UDD doc family.

report-template.md was RENAMED to gate-udd.md across all three skill trees (a git-tracked
rename, byte-identical across trees), reframed to open as the TEXT-MODE UDD GATE SURFACE
cross-linking design.md, with the four floors preserved; design.md's UDD loop gained a
lightweight text-mode gate variant; and every live report-template.md pointer was repointed.

The migration already landed on the tree; this suite is the contract-conformance check —
it pins the ACHIEVED, drift-stable invariants (M1·M2·M3·M4·M5, R1·R3), deliberately NOT the
frozen contract's since-superseded literal anchors (the removed test_skill_lean.py, the 9500 B
ceiling now at 9876, the 9514 byte pin, the absolute ENGINE_MD5 4e65596 — all re-resolved
against the live tree at verify, per docs/08-step-6-verify.md).

Run: cd add-method/tooling && python3 -m unittest test_gate_experience_udd -v
"""
from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_PKG = _TOOLING.parent                       # add-method/
_REPO = _PKG.parent                          # AIDD-Book/

# the three git-tracked skill trees (canonical · bundled · Claude)
SKILL_TREES = (
    _PKG / "skill" / "add",
    _PKG / "src" / "add_method" / "_bundled" / "skill" / "add",
    _REPO / ".claude" / "skills" / "add",
)
# the two book docs M4 repoints, across the three tracked book trees
BOOK_DOCS = [
    t / n
    for t in (_PKG / "docs", _PKG / "src" / "add_method" / "_bundled" / "docs", _REPO)
    for n in ("02-the-flow.md", "appendix-c-glossary.md")
]
_OLD = "report-template" + ".md"             # the retired filename pointer (split so this file never self-matches)
_NEW = "gate-udd.md"


class RenameHappened(unittest.TestCase):
    def test_report_template_gone_gate_udd_present(self):                 # M1, R1
        for tree in SKILL_TREES:
            self.assertFalse((tree / _OLD).exists(), f"{_OLD} must not exist in {tree}")
            self.assertTrue((tree / _NEW).exists(), f"{_NEW} must exist in {tree}")

    def test_gate_udd_byte_identical_across_trees(self):                  # M1
        digests = {hashlib.md5((t / _NEW).read_bytes()).hexdigest() for t in SKILL_TREES}
        self.assertEqual(len(digests), 1, f"{_NEW} must be byte-identical across the 3 trees, got {digests}")


class GateUddIsUddSurface(unittest.TestCase):
    def test_opens_as_text_mode_udd_gate_surface_linking_design(self):    # M2
        text = (SKILL_TREES[0] / _NEW).read_text(encoding="utf-8")
        head = text[:600].lower()
        self.assertIn("text-mode udd gate surface", head, "gate-udd.md must open as the text-mode UDD gate surface")
        self.assertIn("design.md", text[:600], "gate-udd.md must cross-link design.md as its design home")

    def test_four_floors_preserved(self):                                 # M2, R3
        text = (SKILL_TREES[0] / _NEW).read_text(encoding="utf-8").lower()
        for floor in ("show-before-ask", "one-approval", "never-pre-stamp"):
            self.assertIn(floor, text, f"gate-udd.md dropped the {floor!r} floor")
        self.assertTrue(
            "security = hard-stop" in text or "security = **hard-stop**" in text
            or ("security" in text and "hard-stop" in text),
            "gate-udd.md must keep the security = HARD-STOP floor",
        )


class DesignGateVariant(unittest.TestCase):
    def test_design_carries_text_mode_gate_variant(self):                 # M3
        for tree in SKILL_TREES:
            text = (tree / "design.md").read_text(encoding="utf-8")
            self.assertIn("Text-mode gate variant", text, f"design.md in {tree} lost the text-mode gate variant")
            block = text.split("Text-mode gate variant", 1)[1][:400]
            self.assertIn("INTERACTION", block, "the gate variant must intake the INTERACTION axis")
            self.assertIn(_NEW, block, "the gate variant must name gate-udd.md as its report reference")
            self.assertRegex(block.lower(), r"no\s+capture\s+beat", "the gate variant must skip the capture beat")


class NoDanglingReference(unittest.TestCase):
    def _live_surfaces(self):
        for tree in SKILL_TREES:
            yield from tree.glob("*.md")
            yield from tree.glob("phases/*.md")
        yield from BOOK_DOCS
        for p in _TOOLING.glob("test_*.py"):
            if p.name != Path(__file__).name:                 # never self-match the split token above
                yield p

    def test_no_live_report_template_pointer(self):                       # M4, R1
        offenders = [str(p) for p in self._live_surfaces()
                     if p.exists() and _OLD in p.read_text(encoding="utf-8")]
        self.assertEqual(offenders, [], f"dangling_gate_ref: live pointer to {_OLD} survives in {offenders}")


class EngineUntouched(unittest.TestCase):
    def test_migration_never_touched_the_engine(self):                    # M5 (drift-stable form)
        add_py = (_TOOLING / "add.py").read_text(encoding="utf-8")
        self.assertNotIn(_OLD, add_py, "engine must not reference the retired gate-report path")
        self.assertNotIn(_NEW, add_py, "the migration is docs/tests only — the engine never keyed the gate-report file")


if __name__ == "__main__":
    unittest.main(verbosity=2)
