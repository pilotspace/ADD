#!/usr/bin/env python3
"""engine-batch-ops (add-lean-loop task 1): `advance --fill` writes the current
phase's TASK.md section AND advances in one call — all-or-nothing (a guard
refusal restores TASK.md byte-identical) — and `status --brief` prints only
the resume essentials.

Run:
    python3 -m unittest test_engine_batch_ops -v
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ADD_PY = HERE / "add.py"


def _run(cwd, *args, stdin_text=None):
    return subprocess.run(
        [sys.executable, str(ADD_PY), *args],
        cwd=str(cwd), capture_output=True, text=True, input=stdin_text, timeout=120,
    )


class _Project(unittest.TestCase):
    """A minimal inited project with one task at `specify`."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        r = _run(self.root, "init", "--name", "batchops", "--stage", "mvp")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        _run(self.root, "lock")
        r = _run(self.root, "new-task", "widget", "--title", "Widget")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        # phase-collapse-3: new-task now seeds phase=direction directly (specify · plan ·
        # tests are ONE span), so the task is already at direction here.
        self.task_md = self.root / ".add" / "tasks" / "widget" / "TASK.md"

    def tearDown(self):
        self._tmp.cleanup()

    def _freeze(self):
        """Stamp §3 FROZEN + a well-formed flag so the direction->build crossing (the
        ONE freeze gate) passes. freeze-gate-universal sweep."""
        self.task_md.write_text(self.task_md.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")


class FillAndAdvance(_Project):
    def test_fill_writes_section_and_advances(self):  # M1
        # phase-collapse-3: --fill drafts the CURRENT phase's primary section (§1 for
        # direction) and then runs the unchanged advance guard stack — direction's only
        # crossing (into build) still needs §3 FROZEN, independent of what --fill wrote.
        self._freeze()
        draft = self.root / "draft.md"
        draft.write_text("Feature: widget rules\nMust:\n  - the one rule\n")
        r = _run(self.root, "advance", "--fill", str(draft))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        body = self.task_md.read_text()
        self.assertIn("Feature: widget rules", body)
        self.assertIn("phase: build", body)

    def test_fill_from_stdin(self):  # M1 (stdin form)
        self._freeze()
        r = _run(self.root, "advance", "--fill", "-", stdin_text="Feature: stdin rules\n")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("Feature: stdin rules", self.task_md.read_text())

    def test_guard_refusal_rolls_back_byte_identical(self):  # M2
        # phase-collapse-3: the front is ONE phase (direction) — no separate "plan" phase
        # to walk to first. --fill on a still-unfrozen §3 refuses right at the single
        # direction->build crossing (contract_not_frozen), same all-or-nothing rollback.
        before = self.task_md.read_bytes()
        draft = self.root / "d4.md"
        draft.write_text("Plan: test_widget — red first\n")
        r = _run(self.root, "advance", "--fill", str(draft))
        self.assertNotEqual(r.returncode, 0, "unfrozen §3 must refuse the crossing")
        self.assertEqual(self.task_md.read_bytes(), before,
                         "guard refusal must restore TASK.md byte-identical")
        self.assertIn("phase: direction", self.task_md.read_text())

    def test_fill_with_to_rejected(self):  # R1
        draft = self.root / "d.md"
        draft.write_text("x\n")
        before = self.task_md.read_bytes()
        r = _run(self.root, "advance", "--fill", str(draft), "--to", "tests")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("fill_with_to_unsupported", r.stderr + r.stdout)
        self.assertEqual(self.task_md.read_bytes(), before)

    def test_fill_unreadable_rejected(self):  # R2
        before = self.task_md.read_bytes()
        r = _run(self.root, "advance", "--fill", str(self.root / "nope.md"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("fill_unreadable", r.stderr + r.stdout)
        self.assertEqual(self.task_md.read_bytes(), before)

    def test_fill_unparseable_body_rejected(self):  # R3
        before = self.task_md.read_bytes()
        for payload in ("## sneaky heading\n", "above\n---\nbelow\n"):
            draft = self.root / "bad.md"
            draft.write_text(payload)
            r = _run(self.root, "advance", "--fill", str(draft))
            self.assertNotEqual(r.returncode, 0, payload)
            self.assertIn("fill_body_unparseable", r.stderr + r.stdout)
            self.assertEqual(self.task_md.read_bytes(), before)

    def test_fill_section_missing_rejected(self):  # R4
        body = self.task_md.read_text()
        self.task_md.write_text(body.replace("## 1 · SPECIFY", "## X · SPECIFY"))
        before = self.task_md.read_bytes()
        draft = self.root / "d.md"
        draft.write_text("x\n")
        r = _run(self.root, "advance", "--fill", str(draft))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("fill_section_missing", r.stderr + r.stdout)
        self.assertEqual(self.task_md.read_bytes(), before)


class BriefStatus(_Project):
    def test_brief_is_slug_phase_and_next_only(self):  # M3
        r = _run(self.root, "status", "--brief")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        out = [ln for ln in r.stdout.splitlines() if ln.strip()]
        self.assertLessEqual(len(out), 6, r.stdout)
        joined = "\n".join(out)
        self.assertIn("widget", joined)
        self.assertIn("direction", joined)
        self.assertIn("next:", joined)

    def test_plain_status_unchanged_shape(self):
        r = _run(self.root, "status")
        self.assertEqual(r.returncode, 0)
        self.assertGreater(len(r.stdout.splitlines()), 6,
                           "plain status keeps the full orient dump")


class TreesStayIdentical(unittest.TestCase):
    def test_three_trees_byte_identical(self):
        import hashlib
        repo = HERE.parent.parent
        trees = (HERE / "add.py",
                 repo / ".add" / "tooling" / "add.py",
                 HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "add.py")
        digests = {hashlib.md5(t.read_bytes()).hexdigest() for t in trees}
        self.assertEqual(1, len(digests), "engine trees diverged")


if __name__ == "__main__":
    unittest.main(verbosity=2)
