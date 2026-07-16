#!/usr/bin/env python3
"""Red/green tests for the `sensitivity:` task-header dimension (task risk-sensitivity-taxonomy).

CONTRACT (frozen @ v1):
  _SENSITIVITY_VALUES = ("security", "data", "architecture", "mechanical")   # closed enum
  _task_sensitivity(hdr) -> member | None (absent) | "?" (real-but-unknown token)  # PURE, anchored
  add.py freeze: a present-but-unknown sensitivity ("?") -> "sensitivity_invalid" (no write);
                 absent (None) or a valid member -> freeze proceeds (absent grandfathered).
  add.py status: surfaces the active task's "sensitivity: <member>".

Render-blind: assertions read the returned value / printed lines / file surface.
Run: python3 -m unittest test_sensitivity_taxonomy -v
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

import add

# a real drafted + well-flagged §3 body (no template placeholders) — freezable
_DRAFT_FLAGGED = (
    "\n```\nGET /widget  body: { id }\n  200 -> { ok: true }\n```\n\n"
    "Status: DRAFT\n"
    "Least-sure flag surfaced at freeze:\n"
    "  ⚠ [contract] the id encoding is the least-sure part — cost if wrong: a reparse.\n"
)


# ── the reader: anchored, PURE ────────────────────────────────────────────────
class TaskSensitivityReaderTest(unittest.TestCase):
    def test_reads_valid_member(self):
        self.assertEqual(add._task_sensitivity("slug: t · stage: mvp · sensitivity: mechanical\n"),
                         "mechanical")

    def test_absent_reads_none(self):
        self.assertIsNone(add._task_sensitivity("slug: t · stage: mvp\nphase: ground\n"))

    def test_unknown_token_reads_question(self):
        self.assertEqual(add._task_sensitivity("slug: t · sensitivity: spicy\n"), "?")

    def test_prose_substring_not_a_declaration(self):
        # mid-line / title substring (not line-start, not after ·) is never a declaration
        hdr = "# a task about sensitivity: data in general\nslug: t · stage: mvp\n"
        self.assertIsNone(add._task_sensitivity(hdr))


# ── freeze validation + status surfacing ──────────────────────────────────────
class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-sensitivity-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(io.StringIO()):
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
        return out.getvalue() + err.getvalue(), code

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text())

    def _task_md(self, slug):
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

    def _new_task_at_contract(self, slug="t", drafted=_DRAFT_FLAGGED):
        self._silent("lock", "--force")
        if "m" not in self._state().get("milestones", {}):
            self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", slug, "--title", "Feature")
        self._silent("phase", "plan", slug)         # plan-phase-core: "contract" collapsed into "plan"
        if drafted is not None:
            p = self._task_md(slug)
            text = p.read_text(encoding="utf-8")
            # plan-phase-core: §3 PLAN now holds ### Grounding + ### Contract + ### Build-strategy —
            # replace only the ### Contract sub-block body, leaving Grounding/Build-strategy intact.
            new = re.sub(r"(### Contract[^\n]*\n).*?(\n### Build-strategy)",
                         lambda m: m.group(1) + drafted + m.group(2), text, count=1, flags=re.S)
            new = re.sub(r"(?m)^Boundary: <[^\n]*$",
                         "Boundary: none — no external input", new, count=1)
            p.write_text(new, encoding="utf-8")

    def _set_sensitivity(self, slug, token):
        """Append `· sensitivity: <token>` to the header slug: line (a real declaration)."""
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        new = re.sub(r"(?m)^(slug:.*)$", r"\1 · sensitivity: " + token, text, count=1)
        p.write_text(new, encoding="utf-8")

    def _section3(self, slug):
        return add._phase_spans(self._task_md(slug).read_text(encoding="utf-8")).get(3, "")


class FreezeSensitivityTest(_Harness):
    def test_freeze_refuses_invalid_sensitivity(self):
        self._new_task_at_contract("t")
        self._set_sensitivity("t", "spicy")
        before = self._task_md("t").read_bytes()
        out, code = self._run("freeze")
        self.assertNotEqual(code, 0)
        self.assertIn("sensitivity_invalid", out)
        self.assertFalse(add._contract_frozen(self._section3("t")), "§3 must stay DRAFT")
        self.assertEqual(self._task_md("t").read_bytes(), before, "rejected freeze writes nothing")
        self.assertNotIn("freeze", self._state()["tasks"]["t"])

    def test_freeze_proceeds_valid_sensitivity(self):
        self._new_task_at_contract("t")
        self._set_sensitivity("t", "security")
        self._silent("freeze", "--by", "Tin Dang")
        self.assertRegex(self._section3("t"), r"Status:\s*FROZEN @ v1")

    def test_freeze_proceeds_absent_sensitivity(self):
        self._new_task_at_contract("t")          # no sensitivity: line on the header
        self._silent("freeze", "--by", "Tin Dang")
        self.assertRegex(self._section3("t"), r"Status:\s*FROZEN @ v1",
                         "absent sensitivity is grandfathered and never blocks the freeze")


class StatusSensitivityTest(_Harness):
    def test_status_shows_sensitivity(self):
        self._new_task_at_contract("t")          # t is the active task
        self._set_sensitivity("t", "architecture")
        out = self._silent("status")
        self.assertIn("sensitivity: architecture", out,
                      "status surfaces the active task's declared sensitivity")


if __name__ == "__main__":
    unittest.main(verbosity=2)
