#!/usr/bin/env python3
"""Red/green tests for `add.py freeze` — the engine write-seam for the §3 contract
freeze (task freeze-actor-stamp). It is the 5th engine-WRITTEN human seam: it flips
§3 `DRAFT -> FROZEN @ vN — approved by <name>` AND records a structured `{name,email,
source}` actor on the task's state record, joining lock · gate · milestone-done · release.
Run: python3 -m unittest test_freeze_command -v
"""
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import add
from add_engine import identity

KNOWN = {"name": "Ada", "email": "ada@x.io", "source": "git"}

# a real drafted §3 body (no template placeholders) — optionally with the well-formed flag
_DRAFT_FLAGGED = (
    "\n```\nGET /widget  body: { id }\n  200 -> { ok: true }\n```\n\n"
    "Status: DRAFT\n"
    "Least-sure flag surfaced at freeze:\n"
    "  ⚠ [contract] the id encoding is the least-sure part — cost if wrong: a reparse.\n"
)
_DRAFT_NOFLAG = (
    "\n```\nGET /widget  body: { id }\n  200 -> { ok: true }\n```\n\nStatus: DRAFT\n"
)


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-freeze-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue() + err.getvalue(), code     # merged: _die writes to stderr

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text())

    def _task_md(self, slug):
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

    def _new_task_at_contract(self, slug="t", drafted=_DRAFT_FLAGGED):
        """Lock, a milestone + task, jump to `contract`, and replace §3 with `drafted`."""
        self._silent("lock", "--force")
        if "m" not in self._state().get("milestones", {}):
            self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", slug, "--title", "Feature")
        self._silent("phase", "contract", slug)
        if drafted is not None:
            self._set_section3(slug, drafted)

    def _set_section3(self, slug, body):
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        new = re.sub(r"(## 3 · CONTRACT[^\n]*\n).*?(\n---)",
                     lambda m: m.group(1) + body + m.group(2), text, count=1, flags=re.S)
        p.write_text(new, encoding="utf-8")

    def _section3(self, slug):
        return add._phase_spans(self._task_md(slug).read_text(encoding="utf-8")).get(3, "")


class FreezeHappyPathTest(_Harness):
    def test_freeze_active_stamps_section3_and_actor(self):
        self._new_task_at_contract("t")
        with mock.patch.object(identity, "_whoami", return_value=dict(KNOWN)):
            self._silent("freeze")
        raw3 = self._section3("t")
        self.assertRegex(raw3, r"Status:\s*FROZEN @ v1 — approved by Ada")
        self.assertTrue(add._AUDIT_STAMP_RE.search(raw3))
        rec = self._state()["tasks"]["t"]["freeze"]
        self.assertEqual(rec["version"], "v1")
        self.assertEqual(rec["approved_by"], "Ada")
        self.assertEqual(rec["actor"], KNOWN)
        self.assertIn("frozen_at", rec)

    def test_freeze_named_task_leaves_focus_unchanged(self):
        self._new_task_at_contract("first")
        # a second task becomes active; freeze `first` by slug
        self._silent("new-task", "second", "--title", "Other")
        self._silent("use", "second")
        self._silent("freeze", "first")
        self.assertRegex(self._section3("first"), r"Status:\s*FROZEN @ v1")
        self.assertEqual(add._active_task(self._state()), "second")  # focus unchanged

    def test_by_overrides_approver_name(self):
        self._new_task_at_contract("t")
        self._silent("freeze", "--by", "Tin Dang")
        self.assertRegex(self._section3("t"), r"Status:\s*FROZEN @ v1 — approved by Tin Dang")
        self.assertEqual(self._state()["tasks"]["t"]["freeze"]["approved_by"], "Tin Dang")

    def test_freeze_targets_section3_not_a_decoy_draft_line(self):
        # regression: a bare `Status: DRAFT` in §1 prose must NOT be the line that freezes
        self._new_task_at_contract("t")
        p = self._task_md("t")
        text = p.read_text(encoding="utf-8")
        text = text.replace("## 1 · SPECIFY", "## 1 · SPECIFY\nStatus: DRAFT\n", 1)
        p.write_text(text, encoding="utf-8")
        self._silent("freeze")
        self.assertRegex(self._section3("t"), r"Status:\s*FROZEN @ v1")          # §3 froze
        sec1 = add._phase_spans(p.read_text(encoding="utf-8")).get(1, "")
        self.assertIn("Status: DRAFT", sec1)                                     # §1 decoy untouched
        self.assertNotRegex(sec1, r"Status:\s*FROZEN")

    def test_refreeze_after_change_request_increments_version(self):
        self._new_task_at_contract("t")
        self._silent("freeze")
        # change-request: revert §3 to a flagged DRAFT, then re-freeze
        self._set_section3("t", _DRAFT_FLAGGED)
        self._silent("freeze")
        self.assertRegex(self._section3("t"), r"Status:\s*FROZEN @ v2")
        self.assertEqual(self._state()["tasks"]["t"]["freeze"]["version"], "v2")


class FreezeRejectTest(_Harness):
    def test_refuse_no_active_task(self):
        before = self._state()
        out, code = self._run("freeze")
        self.assertNotEqual(code, 0)
        self.assertIn("no_active_task", out)
        self.assertEqual(self._state(), before)        # nothing written

    def test_refuse_already_frozen(self):
        self._new_task_at_contract("t")
        self._silent("freeze")
        frozen3 = self._section3("t")
        rec = self._state()["tasks"]["t"]["freeze"]
        out, code = self._run("freeze")
        self.assertNotEqual(code, 0)
        self.assertIn("already_frozen", out)
        self.assertEqual(self._section3("t"), frozen3)             # §3 unchanged
        self.assertEqual(self._state()["tasks"]["t"]["freeze"], rec)  # stamp unchanged

    def test_refuse_contract_not_drafted_template(self):
        # at `contract` but §3 still the unfilled template (has <METHOD> placeholder)
        self._new_task_at_contract("t", drafted=None)
        out, code = self._run("freeze")
        self.assertNotEqual(code, 0)
        self.assertIn("contract_not_drafted", out)
        self.assertFalse(add._contract_frozen(self._section3("t")))   # §3 Status line not frozen
        self.assertNotIn("freeze", self._state()["tasks"]["t"])

    def test_refuse_unflagged_freeze(self):
        self._new_task_at_contract("t", drafted=_DRAFT_NOFLAG)
        out, code = self._run("freeze")
        self.assertNotEqual(code, 0)
        self.assertIn("unflagged_freeze", out)
        self.assertFalse(add._contract_frozen(self._section3("t")))   # §3 Status line not frozen
        self.assertNotIn("freeze", self._state()["tasks"]["t"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
