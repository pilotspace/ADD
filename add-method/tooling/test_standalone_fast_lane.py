#!/usr/bin/env python3
"""Behavioral proof of the blessed milestone-free fast lane (task: standalone-fast-task).

A `--fast` task created with NO owning milestone is a DELIBERATE low-ceremony lane, not an
orphan to nag. This is distinct from the v8-1 orphan guard, which still nudges/​warns a
*non-fast* milestone-less task.

CONTRACT (frozen @ v1 — soft-info):
  - `new-task <slug> --fast` resolving to NO milestone -> stdout AFFIRMS a standalone fast
    lane (milestone-free by design); it does NOT print the intake nudge.
  - `add.py check` gains an additive INFO tier: a milestone-less task carrying the `fast`
    marker -> a soft INFO line (NOT a WARN). `--json` gains `infos: [...]` + `informed: N`;
    `passed`/`failed`/`warned`/`warnings` are UNCHANGED; a fast standalone is NEVER in
    `warnings` and NEVER inflates `warned`.
  - The NON-fast milestone-less path is UNCHANGED — still nudges on create, still WARNs in
    check (keeps test_v8_1_orphan_guard green).

Run: python3 -m unittest test_standalone_fast_lane -v
"""
import contextlib
import io
import json
import os
import tempfile
import shutil
import unittest

import add


def _run(argv):
    """Run add.main(argv) in-process, capturing (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class BlessedStandaloneFastLane(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self.tmp = tempfile.mkdtemp(prefix="add-standalone-fast-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])   # fresh project: no active milestone

    def tearDown(self):
        os.chdir(self._cwd)

    # --- scenario (a): a fast standalone create AFFIRMS the lane, no intake nudge ----
    def test_fast_standalone_create_affirms_lane(self):
        code, out, _ = _run(["new-task", "t", "--fast"])
        self.assertEqual(code, 0, "new-task --fast must create the task")
        low = out.lower()
        self.assertTrue(
            ("standalone fast" in low) or ("milestone-free" in low),
            f"a fast standalone create must AFFIRM the lane, got: {out!r}")
        self.assertNotIn(
            "size it via", low,
            "a blessed fast standalone must NOT print the intake nudge")
        self.assertIn("t", add.load_state(add.find_root()).get("tasks", {}),
                      "the fast standalone task must be created")

    # --- scenario (b): check emits a soft INFO (not a WARN) for the fast standalone --
    def test_check_infos_fast_standalone_not_warned(self):
        _run(["new-task", "t", "--fast"])
        code, out, _ = _run(["check", "--json"])
        self.assertEqual(code, 0, "check must not block on a fast standalone (warn/info-never-block)")
        obj = json.loads(out)
        # additive INFO tier exists and carries the fast standalone
        self.assertIn("infos", obj, "check --json must gain an additive `infos` tier")
        self.assertGreaterEqual(obj.get("informed", 0), 1, "the fast standalone must be counted in `informed`")
        info_names = " ".join(i.get("name", "") for i in obj["infos"])
        self.assertIn("'t'", info_names, "the fast standalone 't' must appear as an INFO")
        # and it must NOT be a warning / must not inflate warned
        warn_names = " ".join(w.get("name", "") for w in obj.get("warnings", []))
        self.assertNotIn("'t'", warn_names, "a fast standalone must NOT be a WARN")
        # legacy keys untouched
        self.assertEqual(obj.get("failed", -1), 0, "a fast standalone must not inflate `failed`")

    # --- scenario (c): the NON-fast orphan path is UNCHANGED (regression) -----------
    def test_non_fast_orphan_still_nudges_and_warns(self):
        code, out, _ = _run(["new-task", "u"])          # no --fast -> orphan
        self.assertEqual(code, 0)
        self.assertIn("not attached to a milestone", out.lower(),
                      "a NON-fast orphan must still get the intake nudge (v8.1 guard)")
        code, cout, _ = _run(["check", "--json"])
        obj = json.loads(cout)
        warn_names = " ".join(w.get("name", "") for w in obj.get("warnings", []))
        self.assertIn("'u'", warn_names, "a NON-fast orphan must still be WARNed in check")


if __name__ == "__main__":
    unittest.main()
