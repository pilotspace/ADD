#!/usr/bin/env python3
"""lightweight-setup (add-lean-loop task 3): setup seeds-and-defers the
foundation — init-seeded PROJECT.md carries living markers, 0-setup.md teaches
first-touch filling, and the lock/red-suite trust floor is unchanged.

Run:
    python3 -m unittest test_lightweight_setup -v
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ADD_PY = HERE / "add.py"
SETUP_GUIDE = HERE.parent / "skill" / "add" / "phases" / "0-setup.md"

LIVING = "living: fill on first touch"


class InitSeedsLivingMarkers(unittest.TestCase):
    def test_project_md_sections_marked(self):  # M2
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, str(ADD_PY), "init", "--name", "lw",
                                "--stage", "mvp"], cwd=tmp, capture_output=True,
                               text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
            proj = (pathlib.Path(tmp) / ".add" / "PROJECT.md").read_text()
            self.assertGreaterEqual(proj.count(LIVING), 3,
                                    "Domain/Spec/UI-UX sections must carry the living marker")


class SetupGuideSeedsAndDefers(unittest.TestCase):
    def setUp(self):
        self.text = SETUP_GUIDE.read_text()

    def test_teaches_seed_not_draft(self):  # M1
        self.assertIn("Seed, don't draft", self.text)
        self.assertIn(LIVING, self.text)

    def test_no_per_role_persona_mandate_at_setup(self):  # M1
        self.assertNotIn("Author one per role", self.text)
        self.assertIn("generic", self.text)

    def test_exit_gate_defers_untouched_sections(self):  # M1
        gate = re.search(r"<exit_gate>(.*?)</exit_gate>", self.text, re.S).group(1)
        self.assertNotIn("Living docs filled", gate)
        self.assertIn("living marker", gate)

    def test_trust_floor_unchanged(self):  # M3
        gate = re.search(r"<exit_gate>(.*?)</exit_gate>", self.text, re.S).group(1)
        self.assertIn("lock", gate)
        self.assertIn("§1–§4", gate)
        self.assertIn("RED", gate)


class SkillTreesStayIdentical(unittest.TestCase):
    def test_setup_guide_parity(self):
        import hashlib
        repo = HERE.parent.parent
        trees = (SETUP_GUIDE,
                 repo / ".claude" / "skills" / "add" / "phases" / "0-setup.md",
                 HERE.parent / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "0-setup.md")
        digests = {hashlib.md5(t.read_bytes()).hexdigest() for t in trees if t.exists()}
        self.assertEqual(1, len(digests), "0-setup.md trees diverged")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class NeverDeferInvariants(unittest.TestCase):
    """never-defer-invariants: entry-contract-class constraints pin at setup."""

    def test_invariants_seed_line_on_init(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, str(ADD_PY), "init", "--name", "ndi",
                                "--stage", "mvp"], cwd=tmp, capture_output=True,
                               text=True, timeout=120)
            self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
            proj = (pathlib.Path(tmp) / ".add" / "PROJECT.md").read_text()
            dom = proj.split("## Domain", 1)[1][:400]
            self.assertIn("invariants:", dom)
            self.assertIn("never deferred", dom)

    def test_setup_guide_pins_invariants(self):
        text = SETUP_GUIDE.read_text()
        self.assertIn("Pin invariants first", text)
        self.assertIn("run/entry contract", text)
        self.assertIn("§0", text.split("Pin invariants first", 1)[1][:400],
                      "guide must say every task §0 re-states the invariants")
