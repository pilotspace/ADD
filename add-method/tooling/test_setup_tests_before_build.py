#!/usr/bin/env python3
"""Content + 3-tree parity guard for routing setup through the tests phase (task
setup-tests-before-build, milestone audit-hardening — deep-audit finding F6).

phases/0-setup.md drafted only §1–§3 then handed the first task straight to
phases/5-build.md, so the FIRST feature reached build with NO red test — violating
the non-negotiable rule "never start Build until §1–§4 exist and tests are red".
The fix routes setup THROUGH phases/4-tests.md: the full §1–§4 bundle (the red suite
included) is drafted and FAILING before the lock opens build.

Assertions are region-anchored (step 3 "## 3"; the Exit gate) so the suite is
genuinely red before build — a stray "tests" elsewhere must not satisfy them.

Run: python3 -m unittest test_setup_tests_before_build -v
"""
from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

ADD_METHOD = Path(__file__).resolve().parent.parent
REPO = ADD_METHOD.parent
CANONICAL = ADD_METHOD / "skill" / "add"
BUNDLED = ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add"
DOGFOOD = REPO / ".claude" / "skills" / "add"
SETUP = "phases/0-setup.md"


def _read(tree: Path, rel: str) -> str:
    return (tree / rel).read_text(encoding="utf-8")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class SetupTestsBeforeBuild(unittest.TestCase):
    def setUp(self):
        self.setup = _read(CANONICAL, SETUP)
        self.low = self.setup.lower()

    def _region(self, start: str, end: str) -> str:
        i = self.setup.index(start)
        j = self.setup.index(end, i)
        return self.setup[i:j].lower()

    def test_setup_routes_through_4_tests(self):
        # step 3 ("## 3") must draft the FULL bundle and route through the tests guide
        region = self._region("## 3", "## Run mode")
        self.assertIn("4-tests.md", region,
                      "step 3 must route the first task through phases/4-tests.md")
        self.assertTrue("§1–§4" in region or "§4" in region,
                        "step 3 must draft the full §1–§4 bundle (the red suite is part of it)")

    def test_tests_red_before_build_in_sequence(self):
        region = self._region("## 3", "## Run mode")
        self.assertIn("tests red", region,
                      "step 3's sequence must name the red tests (e.g. 'bundle (§1–§4, tests RED) -> lock -> build')")
        self.assertIn("before build", region,
                      "step 3 must state the red suite must exist/fail BEFORE build opens")

    def test_exit_gate_requires_red_suite_before_build(self):
        region = self._region("## Exit gate", "## Next")
        self.assertIn("4-tests.md", region,
                      "the Exit gate must reference the tests guide")
        self.assertIn("red", region,
                      "the Exit gate must require the first task's RED suite before build")
        self.assertIn("§1–§4", region,
                      "the Exit gate must record the full §1–§4 bundle was drafted")

    def test_three_trees_byte_identical(self):
        digests = {_md5(t / SETUP) for t in (CANONICAL, BUNDLED, DOGFOOD)}
        self.assertEqual(len(digests), 1, "0-setup.md diverged across the 3 skill trees")

    def test_no_existing_section_dropped(self):
        for anchor in ("## 2a", "## 2b", "## 2c", "## 3 · Draft to the lock",
                       "## Run mode", "## 4 · The one human gate", "## Exit gate", "## Next"):
            self.assertIn(anchor, self.setup,
                          f"the edit must not drop the existing '{anchor}' section")


if __name__ == "__main__":
    unittest.main()
