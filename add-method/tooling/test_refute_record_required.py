#!/usr/bin/env python3
"""Red/green tests for the recorded earned-green refute-read verdict
(milestone flow-honesty, task `self-grading-refute-record`, M4).

CONTRACT (frozen @ v1) — design C, MEASURE-NOT-BLOCK (no hard gate):
  templates/PLAN.md.tmpl §6 gains a `### Refute-read verdict` block (after Deep checks, before
    GATE RECORD) with `<…>`-placeholder `Verdict:` + `By:` lines.
  _guarantee_lint_notices(root, state) gains key  refute_unrecorded: [slug...]
    scope: tasks with phase in {verify, observe, done} whose §6 block is PRESENT-but-unfilled
    (_section_unfilled "### Refute-read verdict"); ABSENT block -> grandfathered (not listed).
  cmd_audit: prints ONE grouped "refute_unrecorded — N task(s): <slugs>"; EXIT CODE unchanged (0).
  cmd_audit --json: additive guarantee_lints["refute_unrecorded"] = [...].
  cmd_gate: UNCHANGED — an unfilled block NEVER blocks a gate; NO `refute_record_missing` reject.
  Disclosure: run.md + phases/verify.md + book 08-step-6-verify.md name the auto mandate +
    `refute_unrecorded` + the human spot-audit backstop.
One test per scenario. Run: python3 -m unittest test_refute_record_required -v
"""
import contextlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import add

TOOLING = Path(add.__file__).resolve().parent
ADD_METHOD = TOOLING.parent
REPO = ADD_METHOD.parent
RUN_MD = ADD_METHOD / "skill" / "add" / "run.md"
VERIFY_MD = ADD_METHOD / "skill" / "add" / "phases" / "verify.md"
BOOK_CH8 = ADD_METHOD / "docs" / "08-step-6-verify.md"
MILESTONE = REPO / ".add" / "milestones" / "flow-honesty" / "MILESTONE.md"

REFUTE_HEADER = "### Refute-read verdict"


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-refute-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("lock", "--force")

    def tearDown(self):
        os.chdir(self._cwd)

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        out = io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return code, out.getvalue()

    def _task_md(self, slug):
        return self.tmp / ".add" / "tasks" / slug / "PLAN.md"

    def _verify_task(self, slug):
        """A fresh task driven to verify — its §6 carries the template's unfilled refute block."""
        self._silent("new-task", slug, "--title", "Feature")
        self._silent("phase", "verify", slug)
        return self._task_md(slug)

    def _fill_refute(self, slug):
        p = self._task_md(slug)
        t = (p.read_text(encoding="utf-8")
             .replace("Verdict: <EARNED | NOT-EARNED>", "Verdict: EARNED")
             .replace("<self | agent-id>", "self")
             .replace("<what was probed>", "the whole diff, adversarially"))
        p.write_text(t, encoding="utf-8")

    def _drop_refute(self, slug):
        p = self._task_md(slug)
        t = re.sub(r"### Refute-read verdict.*?(?=\n### GATE RECORD)", "",
                   p.read_text(encoding="utf-8"), flags=re.DOTALL)
        p.write_text(t, encoding="utf-8")
class MeasureNotBlockTest(_Harness):
    def test_gate_never_blocked_by_unrecorded(self):         # scenario 4 — the core guarantee
        self._verify_task("t")                               # auto task, refute block unfilled
        code, out = self._run("gate", "PASS", "t")
        self.assertEqual(code, 0, f"an unrecorded verdict must NOT block a gate:\n{out}")
        import json as _j
        state = _j.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["t"]["phase"], "done")
        self.assertEqual(state["tasks"]["t"]["gate"], "PASS")

    def test_no_new_reject_code_in_engine(self):             # no hard gate shipped
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        self.assertNotIn("refute_record_missing", src,
                         "design C is measure-not-block: no hard-gate reject code may ship")
class TemplateAndWritebackTest(_Harness):
    def test_template_carries_verdict_block(self):           # scenario 5
        p = self._verify_task("t")
        body = p.read_text(encoding="utf-8")
        self.assertIn(REFUTE_HEADER, body)
        self.assertRegex(body, r"Verdict:\s*<[^>\n]+>", "ships an unfilled placeholder")
        i_chk = body.find("- [ ] all tests pass")
        i_ref = body.find(REFUTE_HEADER)
        i_gate = body.find("### GATE RECORD")
        self.assertTrue(-1 < i_chk < i_ref < i_gate,
                        "refute block sits AFTER the §6 checklist and BEFORE GATE RECORD "
                        "(atomic-node: Deep checks + Build expectations left the template)")

    def test_writebacks_inert_to_new_block(self):            # scenario 6
        self._verify_task("t")
        self._fill_refute("t")                               # so the gate isn't about the notice
        self._silent("gate", "PASS", "t")
        body = self._task_md("t").read_text(encoding="utf-8")
        gate_region = body.split("### GATE RECORD", 1)[1]
        self.assertIn("PASS", gate_region, "_stamp_gate_record stamped the GATE RECORD")
        self.assertEqual(body.count(REFUTE_HEADER), 1,
                         "the write-backs must not consume or duplicate the refute block")
        self.assertIn("### Decisions (ADR)", body, "§7 ADR block intact for _stamp_adr_record")


class JsonAndDisclosureTest(_Harness):

    def test_exit_criterion_reworded(self):                  # milestone-doc reword
        if not MILESTONE.exists():
            self.skipTest("flow-honesty milestone archived")
        text = MILESTONE.read_text(encoding="utf-8")
        line = next((ln for ln in text.splitlines()
                     if "self-grading-refute-record" in ln and "verify:" in ln), "")
        self.assertIn("refute_unrecorded", line,
                      "the exit criterion must name the measure, not the dropped hard gate")
        self.assertNotIn("auto-PASS is invalid", line)


if __name__ == "__main__":
    unittest.main(verbosity=2)
