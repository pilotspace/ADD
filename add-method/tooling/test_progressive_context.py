#!/usr/bin/env python3
"""progressive-task-context (add-lean-loop task 2): `status --section` prints
ONE raw §body of the active task; the SKILL.md quick-ref teaches the batched
loop under the frozen lean pool fence.

Run:
    python3 -m unittest test_progressive_context -v
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ADD_PY = HERE / "add.py"
SKILL_MD = HERE.parent / "skill" / "add" / "SKILL.md"


def _run(cwd, *args, stdin_text=None):
    return subprocess.run(
        [sys.executable, str(ADD_PY), *args],
        cwd=str(cwd), capture_output=True, text=True, input=stdin_text, timeout=120,
    )


class _Project(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.assertEqual(_run(self.root, "init", "--name", "ptc", "--stage", "mvp").returncode, 0)
        _run(self.root, "lock")
        self.assertEqual(_run(self.root, "new-task", "widget", "--title", "Widget").returncode, 0)
        # phase-collapse-3: the front is ONE phase (direction) whose only crossing (into
        # build) needs §3 FROZEN, so `advance --fill` can no longer draft-and-cross out of
        # direction with just a §1 fill (it would refuse contract_not_frozen). §1 is
        # written directly instead — this fixture only needs the body present, not a
        # completed crossing.
        task_md = self.root / ".add" / "tasks" / "widget" / "PLAN.md"
        task_md.write_text(
            task_md.read_text().replace(
                "Feature: <name — one-line description of the behavior this task ships>",
                "Feature: widget rules\nMust:\n  - the one rule",
            ), encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()


class SectionRead(_Project):
    def test_reads_one_section_raw(self):  # M1
        r = _run(self.root, "status", "--section", "1")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("Feature: widget rules", r.stdout)
        self.assertNotIn("next:", r.stdout, "no footer — raw body only")
        self.assertNotIn("## 2", r.stdout, "one section only")

    def test_phase_name_alias(self):  # M2
        # phase-collapse-3: specify/plan/tests all fold into `direction`, whose PRIMARY
        # §-number is 1 — so the phase-name alias is `direction` now, not `specify`.
        by_num = _run(self.root, "status", "--section", "1").stdout
        by_name = _run(self.root, "status", "--section", "direction").stdout
        self.assertEqual(by_num, by_name)

    def test_unknown_section_rejected(self):  # R1
        for bad in ("9", "bogus"):
            r = _run(self.root, "status", "--section", bad)
            self.assertNotEqual(r.returncode, 0, bad)
            self.assertIn("section_unknown", r.stderr + r.stdout)

    def test_missing_section_rejected(self):  # R3
        task_md = self.root / ".add" / "tasks" / "widget" / "PLAN.md"
        task_md.write_text(task_md.read_text().replace("## 2 · SCENARIOS", "## X · SCENARIOS"))
        r = _run(self.root, "status", "--section", "2")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("section_missing", r.stderr + r.stdout)


class SkillQuickRef(unittest.TestCase):
    def test_quick_ref_teaches_batched_loop(self):  # M3
        text = SKILL_MD.read_text()
        for token in ("status --brief", "advance --fill", "status --section"):
            self.assertIn(token, text, f"SKILL.md quick-ref must teach `{token}`")


if __name__ == "__main__":
    unittest.main(verbosity=2)
