"""skill-dedup (method-ergonomics): run.md's bundle section becomes a pointer, not a copy.

CONTRACT:
  run.md's "## The specification bundle (v7)" section stops duplicating the freeze
  presentation that phases/3-plan.md owns (the ⚠ flag grammar · the freeze-review
  walkthrough): it keeps the one-approval fact, the "seven lines" checklist reference and
  the lowest-confidence-first cue, and POINTS at `phases/3-plan.md` for the rest.
  The flag grammar `[spec|scenario|contract|test]` keeps exactly ONE guide home
  (3-plan.md); the section shrinks under 700B; 3 run.md trees stay byte-identical;
  the orchestration pool only shrinks (ceiling reconciled, never rebaselined).
Run: python3 -m unittest test_skill_dedup -v
"""
import hashlib
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
SKILL = ADD_METHOD / "skill" / "add"
TREES = (SKILL / "run.md",
         REPO / ".claude" / "skills" / "add" / "run.md",
         ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "run.md")
HEADING = "## The specification bundle (v7)"
FLAG_GRAMMAR = "[spec|scenario|contract|test]"


def _section(text: str) -> str:
    body = text.split(HEADING, 1)[1]
    return body.split("\n## ", 1)[0]


class SkillDedupTest(unittest.TestCase):
    def setUp(self):
        self.text = TREES[0].read_text(encoding="utf-8")
        self.sec = _section(self.text)

    def test_section_points_at_contract_guide(self):          # scenario 1
        self.assertIn("phases/3-plan.md", self.sec,
                      "the bundle section must point at its owning guide")

    def test_kept_tokens(self):                                # scenario 2
        for token in ("one approval", "seven lines", "lowest-confidence first"):
            self.assertIn(token, self.sec, f"the pointer must keep '{token}'")

    def test_flag_grammar_single_home(self):                   # scenario 3
        self.assertNotIn(FLAG_GRAMMAR, self.text,
                         "run.md must not duplicate the flag grammar (3-plan.md owns it)")
        contract = (SKILL / "phases" / "3-plan.md").read_text(encoding="utf-8")
        self.assertIn(FLAG_GRAMMAR, contract, "3-plan.md must keep the grammar's one home")

    def test_section_compressed(self):                         # scenario 4
        self.assertLessEqual(len(self.sec.encode("utf-8")), 700,
                             "the bundle section must be a pointer, not a copy")

    def test_tree_parity(self):                                # scenario 5
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in TREES}
        self.assertEqual(len(digests), 1, "run.md trees diverged")

    def test_orchestration_pool_shrinks(self):                 # scenario 6 — reconcile, no rebaseline
        guides = ["run.md", "streams.md", "advisor.md", "loop.md", "design.md"]
        total = sum((SKILL / g).stat().st_size for g in guides)
        self.assertLessEqual(total, 41300,
                             "dedup must RECLAIM ground (pool well under the frozen ceiling)")


if __name__ == "__main__":
    unittest.main()
