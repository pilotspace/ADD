#!/usr/bin/env python3
"""Behavioral proof of the SKILL.md "Flag mode" quick-ref (task: flag-mode-quickref).

The always-loaded orient region of SKILL.md must carry ONE labelled "Flag mode" entry
that names BOTH human-owned dials — `--fast` (the task lane) and `auto` (the autonomy
mode) — so a reader can discover them without spelunking the phase guides. Propagated
byte-identical across all three skill trees.

Run: python3 -m unittest test_flag_mode_quickref -v
"""
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

SKILL_TREES = (
    _ADD_METHOD / "skill" / "add" / "SKILL.md",
    _REPO / ".claude" / "skills" / "add" / "SKILL.md",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "SKILL.md",
)


class FlagModeQuickRef(unittest.TestCase):
    def _canon(self) -> str:
        return SKILL_TREES[0].read_text(encoding="utf-8")

    def test_flag_mode_label_present(self):
        self.assertIn("**Flag mode**", self._canon(),
                      "SKILL.md must carry a labelled 'Flag mode' quick-ref")

    def test_names_both_dials(self):
        # the block must name BOTH the fast task lane and the auto autonomy mode
        block = self._canon()
        # isolate the Flag mode block (from its label to the next blank-line-then-## or **)
        m = re.search(r"\*\*Flag mode\*\*.*?(?=\n##|\n\n##|\Z)", block, re.DOTALL)
        self.assertIsNotNone(m, "could not locate the Flag mode block")
        seg = m.group(0)
        self.assertIn("--fast", seg, "Flag mode must name the `--fast` task lane")
        self.assertRegex(seg, r"\bauto\b", "Flag mode must name the `auto` autonomy mode")
        self.assertIn("autonomy", seg, "Flag mode must name the autonomy dial")

    def test_all_three_trees_carry_it(self):
        for p in SKILL_TREES:
            self.assertTrue(p.exists(), f"missing skill tree: {p}")
            self.assertIn("**Flag mode**", p.read_text(encoding="utf-8"),
                          f"the Flag mode block must be present in {p}")


if __name__ == "__main__":
    unittest.main()
