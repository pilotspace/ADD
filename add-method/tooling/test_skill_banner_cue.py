#!/usr/bin/env python3
"""Red/green tests for skill-banner-cue (frozen @ v1, milestone loop-readability).

PROSE-ONLY task — no engine logic change. §3 CONTRACT: SKILL.md's always-loaded compact
pipeline sentence (already citing SHAPE) gains a minimal citation of gate-udd.md's
decision banner ("rendered first, above everything") — the element that renders even
before the ARC. intake.md and gate-udd.md are explicitly OUT of scope (0 B delta).

Mirrors §2 SCENARIOS M1/M2/M3/R2 (mechanically-checkable; R1 is covered by the existing
targeted regression batch, not a dedicated test here).

Run: python3 -m unittest test_skill_banner_cue -v
"""
import hashlib
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent
_BUNDLE = _ADD_METHOD / "src" / "add_method" / "_bundled"

CANON_SKILL_MD = _ADD_METHOD / "skill" / "add" / "SKILL.md"
DOG_SKILL_MD = _REPO / ".claude" / "skills" / "add" / "SKILL.md"
BUNDLE_SKILL_MD = _BUNDLE / "skill" / "add" / "SKILL.md"
SKILL_TRIO = (CANON_SKILL_MD, DOG_SKILL_MD, BUNDLE_SKILL_MD)

INTAKE_MD = _ADD_METHOD / "skill" / "add" / "intake.md"

# M1 needle migrated @ gate-experience-udd: persona-owns-gates retired the fixed report SEQUENCE
# (the old "PLAN/SHAPE → SUMMARY → …" mandate) for persona-owned PRINCIPLES, so the cue now checks
# only that SKILL.md's report line names the BANNER ahead of the ARC — the M1 intent — not a sequence.
_BEFORE = "open with the ARC (goal · done · plan, engine-sourced), then PLAN/SHAPE → SUMMARY →"
_AFTER = "the gate report (banner then the ARC)"

_INTAKE_BYTES_BEFORE_TASK = len(INTAKE_MD.read_bytes())


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class SkillMdNamesBanner(unittest.TestCase):
    """M1: SKILL.md's compact pipeline sentence cites the banner ahead of the ARC."""

    def test_skill_names_banner(self):
        text = CANON_SKILL_MD.read_text(encoding="utf-8")
        self.assertIn(_AFTER, text, "SKILL.md must cite the banner ahead of the ARC")
        self.assertNotIn(_BEFORE, text, "the pre-fix wording (no banner) must not survive")


class MirrorsByteIdentical(unittest.TestCase):
    """M2: all 3 SKILL.md copies stay byte-identical after the edit."""

    def test_mirrors_byte_identical(self):
        digests = {_md5(p) for p in SKILL_TRIO}
        self.assertEqual(len(digests), 1, "SKILL.md's 3 mirrors must be byte-identical")

    def test_no_longer_matches_pre_edit_digest(self):
        pre_edit_digest = "54eade6b583e1487d5c22c7505a92fe2"
        self.assertNotEqual(_md5(CANON_SKILL_MD), pre_edit_digest,
                            "the edit must actually land, not a no-op")


class CorePoolUnderBudget(unittest.TestCase):
    """M3: the 'core' pool measures within budget after the edit."""

    def test_core_pool_under_budget(self):
        import test_skill_lean as tsl
        pool = next(p for p in tsl.POOLS if p["name"] == "core")
        target = int(pool["baseline"] * pool["ratio"])
        nbytes = sum(len((tsl._CANON / g).read_bytes())
                    for g in pool["guides"] if (tsl._CANON / g).exists())
        self.assertLessEqual(nbytes, target,
                             f"core pool {nbytes} B must stay <= {target} B")


class IntakeUntouched(unittest.TestCase):
    """R2: intake.md is explicitly out of scope — byte count must not move."""

    def test_intake_untouched(self):
        self.assertEqual(len(INTAKE_MD.read_bytes()), _INTAKE_BYTES_BEFORE_TASK,
                         "intake.md must be untouched by this task (0 B delta)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
