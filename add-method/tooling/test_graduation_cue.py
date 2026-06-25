#!/usr/bin/env python3
"""Behavioral proof of the stage-goal-criteria graduation cue (task: stage-goal-criteria, v22).

CONTRACT (frozen @ v1): `add.py status` gains a READ-ONLY, ADDITIVE graduation cue.
  graduation_ready := all-milestones-done AND stage-criteria total>0 AND met==total.
  - text:   when ready, append ONE line containing "MVP covered -> propose graduation";
            when not ready, the text is byte-identical to today (no cue line).
  - --json: add EXACTLY two keys — graduation_ready: bool, stage_criteria: {met,total};
            every pre-existing key + value unchanged.
  - reject (fail-closed; no cue; status unchanged): milestones_incomplete · no_stage_criteria ·
    criteria_unmet · project_unreadable.

RED drivers (fail today — graduation_ready/cue do not exist): cue_fires · json_graduation_ready ·
json_keys_present · cue_self_contained · criteria_unmet_json. Safety nets guard read-only /
byte-unchanged / fail-closed. Run from repo root:
  PYTHONPATH=add-method/tooling python3 -m unittest test_graduation_cue -v
"""
import contextlib
import hashlib
import io
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add

CUE = "MVP covered → propose graduation"   # the action line; arrow = U+2192
STATE = Path(".add/state.json")
PROJECT = Path(".add/PROJECT.md")


def _run(argv):
    """Run add.main(argv) in the temp project, capturing (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _mark_milestone_done(slug: str) -> None:
    """Precondition (not an internal): set a milestone status=done in state.json. Leaves it the
    active milestone — the real post-`milestone-done`, pre-archive state."""
    state = json.loads(STATE.read_text(encoding="utf-8"))
    state["milestones"][slug]["status"] = "done"
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _add_criteria_block(checks) -> None:
    """Append a `## Stage goal criteria` block to PROJECT.md with the given box states."""
    body = ["", "## Stage goal criteria", ""]
    body += [f"- [{'x' if c else ' '}] criterion {i}" for i, c in enumerate(checks)]
    with PROJECT.open("a", encoding="utf-8") as f:
        f.write("\n".join(body) + "\n")


class GraduationCueTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-graduation-cue-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])                       # grandfathered-locked
        add.main(["new-milestone", "v1", "--goal", "ship the core loop"])

    def tearDown(self):
        os.chdir(self._cwd)

    # --- RED drivers: graduation_ready / cue do not exist yet ----------------
    def test_cue_fires_when_ready(self):
        _mark_milestone_done("v1")
        _add_criteria_block([True, True])
        code, out, _ = _run(["status"])
        self.assertEqual(code, 0)
        self.assertIn(CUE, out, "all milestones done + all criteria checked must show the cue")

    def test_json_graduation_ready_true(self):
        _mark_milestone_done("v1")
        _add_criteria_block([True, True])
        code, out, _ = _run(["status", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertTrue(data["graduation_ready"])
        self.assertEqual(data["stage_criteria"], {"met": 2, "total": 2})

    def test_json_keys_present_when_not_ready(self):
        # active (not-done) milestone -> not ready, but the two keys exist (additive, always).
        _add_criteria_block([True, True])
        code, out, _ = _run(["status", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertFalse(data["graduation_ready"])
        self.assertIn("stage_criteria", data)

    def test_cue_self_contained_no_file_ref(self):
        _mark_milestone_done("v1")
        _add_criteria_block([True])
        _, out, _ = _run(["status"])
        cue_line = next((ln for ln in out.splitlines() if CUE in ln), "")
        self.assertTrue(cue_line, "cue must render when ready")
        self.assertNotIn(".md", cue_line)                          # names the action, not a guide file
        self.assertNotIn("graduate.md", cue_line)

    def test_criteria_unmet_json_false(self):
        _mark_milestone_done("v1")
        _add_criteria_block([True, False])                         # met=1 total=2
        code, out, _ = _run(["status", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertFalse(data["graduation_ready"])
        self.assertEqual(data["stage_criteria"], {"met": 1, "total": 2})

    # --- safety nets: read-only / byte-unchanged / fail-closed ---------------
    def test_cue_is_read_only(self):
        _mark_milestone_done("v1")
        _add_criteria_block([True])
        before_s, before_p = _md5(STATE), _md5(PROJECT)
        stage_before = json.loads(STATE.read_text(encoding="utf-8"))["stage"]
        _run(["status"])
        self.assertEqual(_md5(STATE), before_s, "status must not mutate state.json")
        self.assertEqual(_md5(PROJECT), before_p, "status must not mutate PROJECT.md")
        self.assertEqual(json.loads(STATE.read_text(encoding="utf-8"))["stage"], stage_before,
                         "status must not flip the stage")

    def test_withheld_while_milestone_active(self):
        _add_criteria_block([True, True])                          # checked, but v1 not done
        _, out, _ = _run(["status"])
        self.assertNotIn(CUE, out, "cue withheld while any milestone is not done")

    def test_grandfather_no_block(self):
        _mark_milestone_done("v1")                                 # all done, but no criteria block
        _, out, _ = _run(["status"])
        self.assertNotIn(CUE, out, "no criteria block (total==0) -> no cue")

    def test_block_presence_no_effect_while_incomplete(self):
        # byte-identical invariant: while a milestone is active, the block perturbs nothing.
        _, out_without, _ = _run(["status"])
        _add_criteria_block([True, True])
        _, out_with, _ = _run(["status"])
        self.assertEqual(out_without, out_with,
                         "the criteria block must not change status text while incomplete")

    def test_fail_closed_on_unparseable_section(self):
        _mark_milestone_done("v1")
        with PROJECT.open("a", encoding="utf-8") as f:             # header, but no parseable boxes
            f.write("\n## Stage goal criteria\n\n(notes, no checkboxes)\n")
        code, out, _ = _run(["status"])
        self.assertEqual(code, 0, "status must still render")
        self.assertNotIn(CUE, out, "a section with no boxes (total==0) -> no cue (fail-closed)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
