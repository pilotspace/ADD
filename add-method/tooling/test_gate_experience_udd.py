#!/usr/bin/env python3
"""Red suite for gate-experience-udd (milestone strategy-intake). Contract §3 FROZEN @ v1.

The PHYSICAL fold of the persona-owned gate report into the UDD doc family: report-template.md
is RENAMED to gate-udd.md across all 3 skill trees (byte-identical), reframed as the text-mode
UDD gate surface that cross-links design.md; design.md's UDD loop gains a lightweight text-mode
gate variant (intake INTERACTION → design report → confirm, no wireframe/capture beat); and every
former report-template.md reference (9 guides ×3 trees · 2 book docs · 16 tests) is repointed to
gate-udd.md — with no dangling pointer and the historical task-name `report-template-recorded-loop`
left intact. The four floors (show-before-ask · one-approval · never-pre-stamp · security-HARD-STOP)
are preserved in substance — the fold relocates, never weakens. No add.py edit; SKILL.md < 9500 B.

Red before the build, green after. Run: python3 -m unittest test_gate_experience_udd -v
"""
import hashlib
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_REPO = _TOOLING.parent.parent
_TREES = [
    _TOOLING.parent / "skill" / "add",                                   # canonical
    _TOOLING.parent / "src" / "add_method" / "_bundled" / "skill" / "add",  # bundled
    _REPO / ".claude" / "skills" / "add",                                # dogfood
]
CANON = _TREES[0]
DOCS = _TOOLING.parent / "docs"

# built from parts so this test file never self-matches a whole-tree grep for the token
_OLD = "report-template" + ".md"
_OLD_BARE = "report-template"
_NEW = "gate-udd.md"
_KEEP_TASKNAME = "report-template" + "-recorded-loop"   # must survive the migration


class RenameHappenedTest(unittest.TestCase):
    """M1 — report-template.md is gone; gate-udd.md is its byte-identical home in all 3 trees."""

    def test_old_file_absent_in_all_trees(self):
        for t in _TREES:
            self.assertFalse((t / _OLD).exists(), f"{t}/{_OLD} must be renamed away")

    def test_new_file_present_in_all_trees(self):
        for t in _TREES:
            self.assertTrue((t / _NEW).exists(), f"{t}/{_NEW} must exist (the rename target)")

    def test_new_file_byte_identical_across_trees(self):
        digests = {hashlib.md5((t / _NEW).read_bytes()).hexdigest() for t in _TREES if (t / _NEW).exists()}
        self.assertEqual(len(digests), 1, f"{_NEW} must be byte-identical across the 3 trees")


class GateUddIsUddSurfaceTest(unittest.TestCase):
    """M2 / R3 — gate-udd.md is framed as the text-mode UDD gate surface; the four floors survive."""

    def setUp(self):
        p = CANON / _NEW
        if not p.exists():
            self.skipTest(f"{_NEW} not created yet")
        self.low = p.read_text(encoding="utf-8").lower()

    def test_declares_text_mode_udd_gate_surface(self):
        self.assertIn("udd", self.low, "gate-udd.md must frame itself within UDD")
        self.assertIn("text-mode", self.low, "gate-udd.md must name itself the TEXT-MODE gate surface")

    def test_cross_links_design_home(self):
        self.assertIn("design.md", self.low, "gate-udd.md must cross-link design.md as its design home")

    def test_four_floors_present(self):
        for floor in ("show-before-ask", "one-approval", "never-pre-stamp", "hard-stop"):
            self.assertIn(floor, self.low, f"floors_lost: the '{floor}' floor must survive the fold")

    def test_security_stays_un_persona_negotiable(self):
        self.assertIn("un-persona-negotiable", self.low,
                      "floors_lost: security must stay the un-persona-negotiable HARD-STOP floor")


class DesignGateVariantTest(unittest.TestCase):
    """M3 — design.md's UDD loop carries the lightweight text-mode gate variant."""

    def setUp(self):
        self.low = (CANON / "design.md").read_text(encoding="utf-8").lower()

    def test_names_a_text_mode_gate_variant(self):
        self.assertIn("text-mode gate", self.low,
                      "design.md must define a text-mode gate variant of the UDD loop")

    def test_gate_variant_is_lightweight_no_capture(self):
        i = self.low.find("text-mode gate")
        self.assertNotEqual(i, -1)
        window = self.low[i : i + 400]
        self.assertIn("interaction", window, "the gate variant must intake the INTERACTION axis")
        self.assertIn("confirm", window, "the gate variant must end at a confirm")

    def test_names_gate_udd_as_reference(self):
        self.assertIn("gate-udd", self.low, "design.md must name gate-udd.md as the gate's design reference")


class NoDanglingReferenceTest(unittest.TestCase):
    """M4 / R1 — no live file references report-template.md after the migration."""

    def _targets(self):
        for t in _TREES:
            yield from t.rglob("*.md")
        yield from DOCS.glob("*.md")
        yield from _TOOLING.glob("*.py")

    def test_no_dangling_report_template_reference(self):
        offenders = []
        for f in self._targets():
            if f.resolve() == Path(__file__).resolve():
                continue  # this suite names the old token in its own logic
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if _OLD in text:
                offenders.append(str(f.relative_to(_REPO)))
        self.assertEqual(offenders, [], f"dangling_gate_ref: {_OLD} still referenced in:\n  " + "\n  ".join(offenders))

    def test_skill_pointer_names_gate_udd(self):
        skill = (CANON / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("gate-udd", skill, "SKILL.md must point at gate-udd.md")
        self.assertNotIn(_OLD_BARE, skill, "SKILL.md must not keep a report-template pointer")


class TaskNamesPreservedTest(unittest.TestCase):
    """R2 — the historical task-name substring survives (not corrupted to gate-udd-*)."""

    def test_recorded_loop_taskname_intact(self):
        hits = 0
        for f in _TOOLING.glob("*.py"):
            if f.resolve() == Path(__file__).resolve():
                continue
            if _KEEP_TASKNAME in f.read_text(encoding="utf-8"):
                hits += 1
        self.assertGreater(hits, 0,
                           f"taskname_corrupted: the historical '{_KEEP_TASKNAME}' must survive the migration")


class EngineUntouchedTest(unittest.TestCase):
    """M5 — add.py is not the target; SKILL.md stays under the ceiling."""

    def test_skill_under_ceiling(self):
        self.assertLess((CANON / "SKILL.md").stat().st_size, 9500, "SKILL.md must stay < 9500 B")

    def test_addpy_has_no_filename_reference(self):
        addpy = (_TOOLING / "add.py").read_text(encoding="utf-8")
        # the engine is filename-agnostic — it must reference NEITHER name (no repin either way)
        self.assertNotIn(_OLD, addpy, "add.py must not reference the gate report by filename")


if __name__ == "__main__":
    unittest.main(verbosity=2)
