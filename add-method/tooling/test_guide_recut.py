#!/usr/bin/env python3
"""Red/green tests for guide-recut (six-phase-loop 3/6, frozen v1): the phase-guide
tree re-cuts to the merged 6-phase loop — 1-specify absorbs 2-scenarios' duties,
6-verify absorbs 7-observe's, the two absorbed files are DELETED from all three
guide trees, and SKILL.md's phase table shows the 6-row loop with no dead pointer.

Run: python3 -m unittest test_guide_recut -v
"""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parent
REPO_ROOT = PKG_ROOT.parent

GUIDE_TREES = (
    PKG_ROOT / "skill" / "add",                                      # canonical
    PKG_ROOT / "src" / "add_method" / "_bundled" / "skill" / "add",  # bundled twin
    REPO_ROOT / ".claude" / "skills" / "add",                        # live-skill twin
)
_CANON = GUIDE_TREES[0]
_DELETED = ("phases/2-scenarios.md", "phases/7-observe.md")

# One marker per load-bearing duty the merge must carry (§1 Must list).
_SPECIFY_DUTY_MARKERS = [
    "Given <starting situation>",          # the gherkin output format survives
    "And <what must remain unchanged>",    # the And-unchanged clause per rejection
    "one scenario per Must",               # per-Must AND per-Reject coverage duty
    "partial failure",                     # the edge-case sweep vocabulary
]
_VERIFY_DUTY_MARKERS = [
    "scope-of-impact",                     # release behind a flag/rollout
    "monitors",                            # scenarios-as-monitors
    "spec delta",                          # the next loop's entry
    "voice delta",                         # the SOUL.md route
]


class DeletionTest(unittest.TestCase):
    def test_absorbed_files_deleted_x3(self):                       # M3
        leftovers = [str(tree / rel) for tree in GUIDE_TREES for rel in _DELETED
                     if (tree / rel).exists()]
        self.assertEqual(leftovers, [],
                         f"absorbed guides must be deleted from every tree: {leftovers}")

    def test_absorbing_guides_synced_x3(self):                      # M1 + M2 (parity)
        for rel in ("phases/1-specify.md", "phases/6-verify.md"):
            canon = (_CANON / rel).read_bytes()
            for tree in GUIDE_TREES[1:]:
                self.assertEqual((tree / rel).read_bytes(), canon,
                                 f"twin drifted: {tree / rel}")


class AbsorbedDutiesTest(unittest.TestCase):
    def test_specify_guide_carries_scenario_duties(self):           # M1 + R2
        text = (_CANON / "phases" / "1-specify.md").read_text(encoding="utf-8")
        missing = [m for m in _SPECIFY_DUTY_MARKERS if m not in text]
        self.assertEqual(missing, [],
                         f"1-specify.md must carry 2-scenarios' duties; missing: {missing}")

    def test_verify_guide_carries_observe_duties(self):             # M2 + R2
        text = (_CANON / "phases" / "6-verify.md").read_text(encoding="utf-8")
        missing = [m for m in _VERIFY_DUTY_MARKERS if m not in text]
        self.assertEqual(missing, [],
                         f"6-verify.md must carry 7-observe's duties; missing: {missing}")


class RoutingTest(unittest.TestCase):
    def test_no_live_guide_names_a_deleted_file(self):              # R1 + M5
        offenders = []
        for tree in GUIDE_TREES:
            for f in sorted(tree.rglob("*.md")):
                body = f.read_text(encoding="utf-8", errors="replace")
                for rel in ("2-scenarios.md", "7-observe.md"):
                    if rel in body:
                        offenders.append(f"{f}:{rel}")
        self.assertEqual(offenders, [],
                         f"live skill prose still routes to a deleted guide: {offenders}")

    def test_specify_next_routes_to_plan(self):                     # M1 (Accept)
        text = (_CANON / "phases" / "1-specify.md").read_text(encoding="utf-8")
        self.assertIn("phases/3-plan.md", text,
                      "specify's Next pointer must route straight to plan")

    def test_skill_table_shows_the_six_phase_loop(self):            # M4 (Accept)
        text = (_CANON / "SKILL.md").read_text(encoding="utf-8")
        rows = [ln for ln in text.splitlines()
                if ln.startswith("|") and "`phases/" in ln]
        self.assertEqual(len(rows), 6,
                         f"the phase table must hold exactly 6 guide rows: {rows}")
        joined = "\n".join(rows)
        for gone in ("2-scenarios", "7-observe"):
            self.assertNotIn(gone, joined, f"dead row survives: {gone}")
        spec_row = next(r for r in rows if "1-specify" in r)
        self.assertIn("§2", spec_row, "the specify row must own §2 too")
        ver_row = next(r for r in rows if "6-verify" in r)
        self.assertIn("§7", ver_row, "the verify row must own §7 too")

    def test_skill_size_ceiling_held(self):                         # ceiling honors
        size = len((_CANON / "SKILL.md").read_bytes())
        self.assertLessEqual(size, 9500,
                             f"SKILL.md is {size}B; the orient-split ceiling binds this edit")


if __name__ == "__main__":
    unittest.main()
