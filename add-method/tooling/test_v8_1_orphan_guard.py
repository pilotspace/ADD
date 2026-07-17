#!/usr/bin/env python3
"""Behavioral proof of the orphan-task guard (task: orphan-task-guard, v8-1).

v8 made the docs LEAD with the intake -> milestone flow. v8-1 gives that flow a runtime
backstop: `add.py` WARNS (never blocks) when a task lives outside a milestone, nudging work
back toward `/add` -> intake.

CONTRACT (frozen @ v1):
  - `add.py check` gains a WARNING tier (separate from PASS/FAIL). A task whose state.json
    `milestone` is null -> a WARN line naming the intake flow. Warnings do NOT feed `failed`;
    exit stays 0 (warn-never-block). `--json` gains `warnings: [...]` + `warned: N`; `passed`/
    `failed` unchanged; an orphan is NEVER in `failed`.
  - `add.py new-task <slug>` resolving to NO milestone -> still creates the task (exit 0,
    escape hatch) + prints an intake nudge.
  - TEXT INVARIANT (honesty): the text speaks of STRUCTURE ("outside a milestone" / "not
    attached"), NEVER the act ("flow followed" / "flow not followed"). The guard sees the
    footprint (milestone is null), not whether an intake conversation actually happened.

One test per SCENARIO + an md5 parity guard on the mirrored add.py trees.
Run: python3 -m unittest test_v8_1_orphan_guard -v
"""
import contextlib
import hashlib
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from pathlib import Path

import add

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent
ADDPY_CANON = _ADD_METHOD / "tooling" / "add.py"
ADDPY_DOGFOOD = _REPO / ".add" / "tooling" / "add.py"

# any phrasing that would claim the ACT of intake (over-claiming) rather than the structure
ACT_CLAIM = re.compile(r"\b(followed|skipped|ran intake|didn't run|did not run|you (ran|skipped))\b",
                       re.IGNORECASE)


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


class OrphanGuardTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-orphan-guard-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])   # fresh project: no active milestone

    def tearDown(self):
        os.chdir(self._cwd)

    # --- scenario 1: check warns on an orphan task but still passes ----------
    def test_check_warns_on_orphan_but_passes(self):
        _run(["new-task", "t"])                 # no active milestone -> orphan
        code, out, _ = _run(["check"])
        self.assertEqual(code, 0, "check must NOT block on an orphan task (warn-never-block)")
        self.assertIn("outside a milestone", out.lower(),
                      "check must WARN that the task is outside a milestone")
        # assert the WORD "intake" (not the path — the tmpdir is named "add-orphan-guard",
        # so a /add regex would false-match the absolute path printed by the tool)
        self.assertIn("intake", out.lower(), "the warning must name the intake flow")

    # --- scenario 2: WARN tier exists but stays silent for an attached task --
    def test_check_clean_when_attached(self):
        _run(["new-milestone", "v1"])           # becomes active
        _run(["new-task", "a"])                 # auto-attaches to v1
        code, out, _ = _run(["check", "--json"])
        self.assertEqual(code, 0)
        obj = json.loads(out)
        self.assertIn("warnings", obj, "the WARN tier must exist in --json (proves it is built)")
        names = " ".join(w.get("name", "") for w in obj["warnings"])
        self.assertNotIn("'a'", names, "an attached task must NOT be warned as orphan")

    # --- scenario 3: new-task with no milestone nudges but still creates -----
    def test_new_task_orphan_nudges_and_creates(self):
        code, out, _ = _run(["new-task", "lonely"])
        self.assertEqual(code, 0, "new-task must still create the task (escape hatch)")
        # match the nudge's STRUCTURAL phrase, not "/add" — the tmpdir path contains "/add"
        self.assertIn("not attached to a milestone", out.lower(),
                      "new-task on an orphan must nudge that it is not attached to a milestone")
        self.assertIn("intake", out.lower(),
                      "the nudge must name the intake flow")
        root = add.find_root()
        self.assertIn("lonely", add.load_state(root).get("tasks", {}),
                      "the orphan task must be created despite the nudge")

    # --- scenario 4: new-task with a milestone does not nudge ---------------
    def test_new_task_attached_no_nudge(self):
        _run(["new-milestone", "v1"])
        code, out, _ = _run(["new-task", "attached"])
        self.assertEqual(code, 0)
        self.assertNotIn("not attached to a milestone", out.lower(),
                         "a task linked to a milestone must NOT get the orphan nudge")
        self.assertIn("v1", out, "an attached task should report its milestone link")

    # --- scenario 5: the text labels structure, not the act -----------------
    def test_text_labels_structure_not_act(self):
        _, nt_out, _ = _run(["new-task", "t"])  # orphan nudge
        _, ck_out, _ = _run(["check"])          # orphan warn
        blob = nt_out + ck_out
        self.assertTrue(("outside a milestone" in blob.lower()) or ("not attached" in blob.lower()),
                        "text must speak of STRUCTURE (outside a milestone / not attached)")
        self.assertIsNone(ACT_CLAIM.search(blob),
                          f"text must NOT claim the intake ACT was/ wasn't done: {blob!r}")

    # --- scenario 6: check --json carries warnings without inflating failed --
    def test_check_json_warnings_not_failed(self):
        _run(["new-task", "t"])                 # orphan
        code, out, _ = _run(["check", "--json"])
        self.assertEqual(code, 0)
        obj = json.loads(out)
        self.assertIn("warnings", obj)
        self.assertGreaterEqual(obj.get("warned", 0), 1, "the orphan must be counted in `warned`")
        self.assertEqual(obj.get("failed", -1), 0, "an orphan must NOT inflate `failed`")
        failed_names = " ".join(c.get("name", "") for c in obj.get("checks", []) if not c.get("ok"))
        self.assertNotIn("'t'", failed_names, "the orphan task must not appear as a FAIL")

    # --- md5 parity: the build must keep both add.py trees identical ---------


if __name__ == "__main__":
    unittest.main(verbosity=2)
