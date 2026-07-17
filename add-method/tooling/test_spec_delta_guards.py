#!/usr/bin/env python3
"""Behavioral proof of the SPEC-delta GUARDS (task: spec-delta-guards, delta-resolution).

CONTRACT (kernel-trim (ADD 2.0 M5): the compact-refusal surface died with `compact`):
  - `status` prints a read-only "spec : N open SPEC delta(s) — stale; drain via add.py deltas"
    line (project-wide; silent at 0) — the staleness wording pin migrated from test_delta_drain.
  - `milestone-done` prints a "note: N open SPEC delta(s) to resolve …" (project-wide; never blocks).
  - `report <ms> --json` carries summary["open_spec"] = project-wide count.
  All surfaces read ONE source: len(_collect_open_spec_deltas(root)). One test per SCENARIO.
Run: python3 -m unittest test_spec_delta_guards -v
"""
from __future__ import annotations

import io
import os
import re
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = None
    with redirect_stdout(out), redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
    return out.getvalue(), err.getvalue(), code


def _meet_exit_criteria(ms):
    root = add.find_root()
    p = root / "milestones" / ms / add.MILESTONE_FILE
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                  lambda m: m.group(0).replace("- [ ]", "- [x]"), text, flags=re.S)
    p.write_text(text, encoding="utf-8")


class SpecDeltaGuardsTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-spec-guards-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.root = Path(self.tmp) / ".add"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- helpers -------------------------------------------------------------
    def _plant_spec(self, slug, text="x"):
        """Inject one grammar-valid OPEN SPEC delta into slug's §7 block."""
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        i = s.index("### Spec delta") + len("### Spec delta")
        p.write_text(s[:i] + f"\n- [SPEC · open] {text} (evidence: e)\n" + s[i:],
                     encoding="utf-8")

    def _state_bytes(self):
        return (self.root / "state.json").read_bytes()

    # --- scenarios -----------------------------------------------------------
    def test_status_nudges_open_spec_silent_when_none(self):  # Must 2 (+ staleness wording, ex delta-drain)
        add.main(["new-task", "a"])
        out, _, _ = _run(["status"])
        self.assertNotRegex(out, r"spec\s*:\s*\d+ open",
                            "status must be silent when no open SPEC delta")
        self.assertNotIn("stale", out.lower())
        self._plant_spec("a", "rate limit")
        out2, _, _ = _run(["status"])
        # Pin the `spec :` prefix AND the staleness AND the drain pointer, so a
        # `stale :`-prefixed or pointer-less impl would FAIL here.
        self.assertRegex(
            out2,
            r"spec\s*:\s*1 open SPEC delta(?:s)? — stale; drain via add\.py deltas",
            "status must keep the `spec :` prefix AND name staleness AND point at the drain surface")
        # status itself never wrote (compare a status run against its own pre-bytes)
        pre = self._state_bytes()
        _run(["status"])
        self.assertEqual(self._state_bytes(), pre, "status must be read-only")

    def test_milestone_done_nudges_open_spec(self):  # Must 3
        add.main(["new-milestone", "mvp", "--goal", "g"])
        add.main(["new-task", "t", "--milestone", "mvp"])
        add.main(["phase", "verify", "t"])
        add.main(["gate", "PASS", "t"])
        self._plant_spec("t", "watch the retry path")
        _meet_exit_criteria("mvp")
        out, err, code = _run(["milestone-done", "mvp"])
        self.assertIsNone(code, f"milestone-done must still succeed: {err}")
        self.assertRegex(out, r"note:.*open SPEC delta", "must nudge open SPEC deltas")

    def test_report_counts_open_spec_projectwide(self):  # Must 4
        add.main(["new-milestone", "v1", "--goal", "g"])
        add.main(["new-task", "t", "--milestone", "v1"])
        add.main(["new-task", "elsewhere"])       # the open delta lives OFF the reported milestone
        self._plant_spec("elsewhere", "stray")
        before = self._state_bytes()
        out, err, code = _run(["report", "v1", "--json"])
        self.assertIsNone(code, f"report failed: {err}")
        data = json.loads(out)
        self.assertEqual(data["summary"]["open_spec"], 1,
                         "report open_spec is the PROJECT-WIDE count")
        self.assertEqual(self._state_bytes(), before, "report must be read-only")


if __name__ == "__main__":
    unittest.main()
