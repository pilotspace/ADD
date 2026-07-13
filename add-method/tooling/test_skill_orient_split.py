#!/usr/bin/env python3
"""Red/green tests for the skill orient split (task skill-orient-split, frozen v1):
SKILL.md is read on EVERY task but carried ~4.6KB of on-demand routing prose
("Beyond the bundle" verbose bullets) most tasks never take. That prose moves to
the on-demand guide `beyond.md`; SKILL.md keeps a compact one-line-per-trigger
index. Structural pins (pointer census, phase table, banner cue, Depth-by-stage)
are guarded by their own suites and stay green — this suite pins the SPLIT itself.

Run: python3 -m unittest test_skill_orient_split -v
"""
import unittest
from pathlib import Path

from test_skill_lean import ON_DEMAND_POINTERS

_CANON = Path(__file__).resolve().parent.parent / "skill" / "add"
_SKILL = _CANON / "SKILL.md"
_BEYOND = _CANON / "beyond.md"

# One marker per moved routing bullet — the prose must live on in beyond.md.
_MOVED_MARKERS = [
    "Pipeline ready tasks behind frozen",       # run/streams spawn lane
    "Collapse, never skip",                     # fast lane (frozen-scope wording)
    "design-definition loop",                   # UDD
    "holds it open",                            # milestone loop
    "propose graduation",                       # graduate
    "releasable:",                              # release
    "component pillar",                         # components
    "persona loop",                             # personas
    "Risk-class of a task",                     # sensitivity
]


class OrientSplitTest(unittest.TestCase):
    def test_skill_under_size_ceiling(self):                       # M1
        self.assertTrue(_SKILL.exists())
        size = len(_SKILL.read_bytes())
        self.assertLessEqual(size, 9500,
                             f"SKILL.md is {size}B; the orient core must stay <= 9500B "
                             f"(the split moved the routing prose to beyond.md)")

    def test_beyond_exists_with_moved_markers(self):               # M2
        self.assertTrue(_BEYOND.exists(), "beyond.md (the on-demand routing guide) is missing")
        text = _BEYOND.read_text(encoding="utf-8")
        missing = [m for m in _MOVED_MARKERS if m not in text]
        self.assertEqual(missing, [],
                         f"beyond.md must carry the moved routing prose; missing: {missing}")

    def test_index_names_every_pointer_plus_beyond(self):          # M1 + R1
        text = _SKILL.read_text(encoding="utf-8")
        self.assertIn("`beyond.md`", text,
                      "SKILL.md must route to the on-demand guide it spun off")
        missing = [p for p in ON_DEMAND_POINTERS if f"`{p}`" not in text]
        self.assertEqual(missing, [],
                         f"the compact index must keep every pinned pointer: {missing}")

    def test_moved_prose_left_skill(self):                         # M1 (no duplication)
        text = _SKILL.read_text(encoding="utf-8")
        exempt = ("propose graduation", "persona loop")
        # "propose graduation" also lives in Depth-by-stage's production line (pinned by
        # test_graduate_guard); "persona loop" is pinned INTO SKILL.md by
        # test_persona_method_docs — every OTHER moved bullet appears only in beyond.md.
        still_there = [m for m in _MOVED_MARKERS if m in text and m not in exempt]
        self.assertEqual(still_there, [],
                         f"moved routing prose still duplicated in SKILL.md: {still_there}")

    def test_beyond_synced_across_trees(self):                     # M2 (x3 parity)
        repo = _CANON.parent.parent.parent
        twins = [
            repo / "add-method" / "src" / "add_method" / "_bundled" / "skill" / "add" / "beyond.md",
            repo / ".claude" / "skills" / "add" / "beyond.md",
        ]
        canon = _BEYOND.read_bytes() if _BEYOND.exists() else b""
        for t in twins:
            self.assertTrue(t.exists(), f"beyond.md missing from twin: {t}")
            self.assertEqual(t.read_bytes(), canon, f"twin drifted: {t}")


if __name__ == "__main__":
    unittest.main()
