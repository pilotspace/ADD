#!/usr/bin/env python3
"""wave-status-hint — `add.py status` surfaces a live WAVE.md as the wave resume hint.

The wave-ledger convention (streams.md "Wave ledger") made WAVE.md the wave's resume
point, but `status` — the mandated first-orientation command — did not surface it, so
resuming still leaned on the orchestrator remembering to look in the milestone dir
(the disclosed [ADD] residue at the wave-ledger gate). This suite drives the hint:
existence-only detection (no open/read/parse — no new IO failure path), human surface
only, the frozen machine-state-json (`status --json`) byte-shape untouched.

Run: python3 -m unittest test_wave_status_hint -v
"""
import contextlib
import io
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class WaveStatusHintTest(unittest.TestCase):
    """status prints one 'wave    :' hint line per live ledger; silent otherwise."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-wave-hint-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        add.main(["new-milestone", "mvp", "--goal", "g", "--stage", "mvp"])
        self.ms_dir = Path(self.tmp) / ".add" / "milestones" / "mvp"

    def tearDown(self):
        os.chdir(self._cwd)

    def _wave_lines(self, out):
        return [l for l in out.splitlines() if l.startswith("wave    :")]

    def test_status_hints_live_wave(self):
        (self.ms_dir / "WAVE.md").write_text("wave: 1 · status: live\n", encoding="utf-8")
        code, out, _ = _run(["status"])
        self.assertEqual(code, 0)
        lines = self._wave_lines(out)
        self.assertEqual(len(lines), 1, "exactly one hint for one live ledger")
        self.assertIn(".add/milestones/mvp/WAVE.md", lines[0])
        self.assertIn("LIVE", lines[0])
        self.assertIn("re-orient", lines[0],
                      "the hint must carry the resume instruction, not just the path")
        ctx = next(i for i, l in enumerate(out.splitlines()) if l.startswith("context :"))
        pos = next(i for i, l in enumerate(out.splitlines()) if l.startswith("wave    :"))
        self.assertGreater(pos, ctx, "the wave hint renders after the foundation pointer")

    def test_status_silent_without_wave(self):
        code, out, _ = _run(["status"])
        self.assertEqual(code, 0)
        self.assertEqual(self._wave_lines(out), [],
                         "phantom_wave_hint: no ledger -> no hint line")

    def test_dir_at_wave_path_no_hint_no_crash(self):
        (self.ms_dir / "WAVE.md").mkdir()
        code, out, err = _run(["status"])
        self.assertEqual(code, 0, "not_a_file_no_hint: a directory must not crash status")
        self.assertEqual(self._wave_lines(out), [],
                         "not_a_file_no_hint: a directory at the path is not a live ledger")
        self.assertNotIn("Traceback", err)

    def test_one_line_per_live_ledger(self):
        (self.ms_dir / "WAVE.md").write_text("wave: 1\n", encoding="utf-8")
        add.main(["new-milestone", "mvp-2", "--goal", "g2", "--stage", "mvp"])
        ms2 = Path(self.tmp) / ".add" / "milestones" / "mvp-2"
        (ms2 / "WAVE.md").write_text("wave: 1\n", encoding="utf-8")
        code, out, _ = _run(["status"])
        self.assertEqual(code, 0)
        self.assertEqual(len(self._wave_lines(out)), 2,
                         "fail-loud: the one-live-wave anomaly is shown, never hidden")

    def test_json_surface_frozen(self):
        (self.ms_dir / "WAVE.md").write_text("wave: 1\n", encoding="utf-8")
        code, out, _ = _run(["status", "--json"])
        self.assertEqual(code, 0)
        obj = json.loads(out)
        # v4-1 machine-state-json froze these base keys. v22 (human-ratified change-request,
        # 2026-06-08) re-interprets the surface as ADDITIVE: the base keys stay immutable
        # (present, never moved/removed) and ONLY sanctioned keys may extend it — so existing
        # consumers keep working (additive = backward-safe, cf. v8-1 check --json). Ratified
        # additive keys: the v22 stage-graduation pair, plus the state-model-reshape multi-active
        # pair (parallel-status-view, 2026-06-22) exposing the active SET + per-milestone task map,
        # plus the user-identity actor object (identity-in-status, 2026-06-22) = _whoami(state),
        # plus the milestones_total/tasks_total pair (status-pagination, 2026-07-02) — the true
        # corpus size, present so a consumer can detect the new default top-10 cap on
        # milestones[]/tasks[] (lifted with --all).
        base = {"project", "stage", "active_task", "milestones", "tasks"}
        sanctioned = {"graduation_ready", "stage_criteria", "active_milestones", "active_tasks",
                      "actor", "milestones_total", "tasks_total"}
        keys = set(obj.keys())
        self.assertTrue(base <= keys,
                        "frozen_json_surface_touched: a base machine-state key was moved/removed")
        self.assertEqual(keys - base, sanctioned,
                         "json_surface_unsanctioned_key: only the ratified additive keys "
                         "may extend status --json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
