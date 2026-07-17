#!/usr/bin/env python3
"""skill-loop-fold red suite (task skill-loop-fold, thin-engine-loop W4).

SKILL.md narrates the whole 3-beat loop INLINE; phases/ collapses 7 → 3
on-demand reference files (direction.md · build.md · verify.md — setup/specify/
plan/tests fold into direction, fast-lane absorbed into SKILL.md routing);
an ordinary task reads ZERO guide files. Budgets: SKILL.md ≤ 9500 B, the
phases/ pool measurably below its 33,496 B pre-task total.

Red-for-the-right-reason today: 7 legacy files exist, the 3 new names don't,
SKILL.md still mandates a per-phase guide load. Floor pins (green today AND
after): SKILL.md byte ceiling; the security-HARD-STOP teaching survives.

Run: python3 -m unittest test_skill_loop_fold -v
"""
import hashlib
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

# the 3 git-tracked skill trees (a missing tree is skipped, never failed)
SKILL_TREES = (
    REPO / "add-method" / "skill" / "add",
    REPO / ".claude" / "skills" / "add",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "skill" / "add",
)
NEW_FILES = ("direction.md", "build.md", "verify.md")
LEGACY = ("0-setup.md", "1-specify.md", "2-scenarios.md", "3-plan.md",
          "4-tests.md", "5-build.md", "6-verify.md", "7-observe.md", "fast-lane.md")

PRE_TASK_POOL = 33496          # bytes over 7 files, recorded 2026-07-17
SKILL_CEILING = 9500

# teaching anchors that must survive the fold, mapped to their new home
# (one representative per folded source; the migrated original suites keep
# their own full pins after their path re-aim)
ANCHORS = {
    "direction.md": ("## Declaring where tests live",        # 4-tests.md grammar section
                     "declare paths as backticked tokens",   # its comment anchor
                     "SETUP-REVIEW",                         # 0-setup baseline artifact
                     "lowest-confidence"),                   # 1-specify ranked-flag rule
    "build.md": ("Approach (domain strategy",                # 5-build facet teaching
                 "Optimization stance",
                 "scope_violation"),                         # scope-lock discipline
    "verify.md": ("do not skim",                             # 6-verify deep-check rubric
                  "adversarial refute-read",
                  "HARD-STOP"),                              # security floor teaching
}


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _trees():
    return [t for t in SKILL_TREES if (t / "SKILL.md").exists()]


class PhasesCensusTest(unittest.TestCase):
    def test_phases_census_exactly_three(self):
        for tree in _trees():
            names = sorted(p.name for p in (tree / "phases").glob("*.md"))
            self.assertEqual(names, sorted(NEW_FILES),
                             f"{tree}/phases must hold exactly the 3 beat references")

    def test_no_legacy_guide_survives(self):
        for tree in _trees():
            for name in LEGACY:
                self.assertFalse((tree / "phases" / name).exists(),
                                 f"legacy guide must not survive the fold: {tree}/phases/{name}")


class SkillNarratesLoopTest(unittest.TestCase):
    def setUp(self):
        self.skill = (SKILL_TREES[0] / "SKILL.md").read_text(encoding="utf-8")

    def test_three_beat_recipe_inline(self):
        for anchor in ("freeze --by", "--cross", "gate PASS", "direction"):
            self.assertIn(anchor, self.skill,
                          f"SKILL.md must narrate the 3-beat recipe inline ({anchor!r})")

    def test_no_mandatory_per_phase_load(self):
        self.assertNotIn("load the\n  matching `phases/<n>-<phase>.md`", self.skill)
        self.assertNotRegex(
            self.skill, r"(?i)load the phase guide \*\*only for the phase you are in\*\*",
            "phase references must be on-demand, never a mandated per-phase load")
        for name in NEW_FILES:
            self.assertIn(f"phases/{name}", self.skill,
                          "SKILL.md must still NAME the on-demand references")


class AnchorsSurviveTest(unittest.TestCase):
    def test_pinned_anchors_survive_fold(self):
        base = SKILL_TREES[0] / "phases"
        for fname, anchors in ANCHORS.items():
            f = base / fname
            self.assertTrue(f.exists(), f"missing reference file {f}")
            body = f.read_text(encoding="utf-8")
            for a in anchors:
                self.assertIn(a, body, f"anchor_dropped: {a!r} must live in {fname}")


class ByteBudgetsTest(unittest.TestCase):
    def test_skill_byte_ceiling(self):
        # floor pin — green today (exactly 9500) and must stay green
        for tree in _trees():
            self.assertLessEqual((tree / "SKILL.md").stat().st_size, SKILL_CEILING,
                                 f"{tree}/SKILL.md over the {SKILL_CEILING}B ceiling")

    def test_phases_pool_measurably_smaller(self):
        pool = sum(p.stat().st_size for p in (SKILL_TREES[0] / "phases").glob("*.md"))
        self.assertLess(pool, PRE_TASK_POOL,
                        f"phases/ pool must shrink below its pre-task {PRE_TASK_POOL}B (now {pool}B)")


class TreeLockstepTest(unittest.TestCase):
    def test_three_tree_lockstep(self):
        for name in NEW_FILES:
            digests = {_md5(t / "phases" / name) for t in _trees()
                       if (t / "phases" / name).exists()}
            self.assertEqual(len(digests), 1,
                             f"phases/{name} must be byte-identical across the skill trees")


if __name__ == "__main__":
    unittest.main(verbosity=2)
