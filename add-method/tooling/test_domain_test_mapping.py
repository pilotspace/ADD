"""domain-test-mapping (method-ergonomics): 4-tests.md widens "test" beyond xUnit code.

CONTRACT:
  phases/4-tests.md states "a test is any machine-checkable assertion" and names the
  per-domain forms — metric threshold · reconciliation query · plan-diff — with red-first
  explicitly holding for each (the assertion must FAIL before the change exists).
  Net ≤0B on the frozen phases pool (lean-over-budget-bump: absorbed by compressing the
  same guide's prose, pinned tokens untouched); 3 guide trees stay byte-identical.
Run: python3 -m unittest test_domain_test_mapping -v
"""
import hashlib
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
TREES = (
    ADD_METHOD / "skill" / "add" / "phases" / "4-tests.md",
    REPO / ".claude" / "skills" / "add" / "phases" / "4-tests.md",
    ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "4-tests.md",
)
# the frozen phases pool ceiling (test_skill_lean: baseline 41190 × ratio 0.80) — this task
# must fit UNDER it with no rebaseline; duplicated here so a pool bust names this task too
POOL_GUIDES = ["0-ground.md", "0-setup.md", "1-specify.md", "2-scenarios.md", "3-contract.md",
               "4-tests.md", "5-build.md", "6-verify.md", "7-observe.md"]
POOL_CEILING = int(41190 * 0.80)


class DomainTestMappingTest(unittest.TestCase):
    def test_guide_states_machine_checkable(self):             # scenario 1
        text = TREES[0].read_text(encoding="utf-8")
        self.assertIn("machine-checkable assertion", text)

    def test_guide_names_domain_forms(self):                   # scenario 2
        text = TREES[0].read_text(encoding="utf-8")
        for form in ("metric threshold", "reconciliation query", "plan-diff"):
            self.assertIn(form, text, f"4-tests.md misses the domain form: {form}")

    def test_red_first_holds_for_each_form(self):              # scenario 3
        text = TREES[0].read_text(encoding="utf-8")
        tail = text.split("machine-checkable assertion", 1)[1][:400]
        self.assertIn("FAIL before", tail,
                      "red-first must be restated where the wider forms are introduced")

    def test_three_trees_byte_identical(self):                 # scenario 4
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in TREES}
        self.assertEqual(len(digests), 1, "4-tests.md guide trees diverged")

    def test_phases_pool_absorbed(self):                       # scenario 5 — net ≤0B
        total = sum((ADD_METHOD / "skill" / "add" / "phases" / g).stat().st_size
                    for g in POOL_GUIDES)
        self.assertLessEqual(total, POOL_CEILING,
                             "the domain-form addition must be absorbed, not budget-bumped")


if __name__ == "__main__":
    unittest.main()
