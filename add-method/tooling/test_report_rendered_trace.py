#!/usr/bin/env python3
"""Red/green tests for the mechanical report-rendered trace (direct chat-directed task
`report-rendered-trace`, motivated by a forensic transcript audit of a separate ADD project
where gate-udd.md was cited-but-never-rendered at every human gate).

CONTRACT — design mirrors refute_unrecorded/advisor_verdict_unrecorded EXACTLY, MEASURE-NOT-BLOCK:
  templates/TASK.md.tmpl §3 gains a `Reported: <…>` line right after `Status: DRAFT`.
  templates/TASK.md.tmpl §6 gains a `Reported: <…>` line as the first line of `### GATE RECORD`,
    before `Outcome:`.
  _guarantee_lint_notices(root, state) gains two keys:
    contract_report_unrecorded[] = §3 body's `Reported:` line PRESENT-but-unfilled
      (_reported_unrecorded); ABSENT line -> grandfathered (not listed).
    verify_report_unrecorded[]   = §6 body's `Reported:` line PRESENT-but-unfilled; same
      grandfather rule. Both scoped like every other §6 guarantee: tasks with phase in
      {verify, observe, done} only.
  cmd_audit: prints ONE grouped line per code, mirroring refute_unrecorded's exact phrasing shape.
  cmd_audit --json: additive guarantee_lints["contract_report_unrecorded"] / ["verify_report_unrecorded"].
  cmd_gate: UNCHANGED — neither key ever blocks a gate (measure-not-block).
  Disclosure: run.md names both codes; 3-plan.md/6-verify.md each instruct recording
    `Reported: yes` at their respective gate.
One test per scenario. Run: python3 -m unittest test_report_rendered_trace -v
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
CONTRACT_MD = ADD_METHOD / "skill" / "add" / "phases" / "direction.md"
VERIFY_MD = ADD_METHOD / "skill" / "add" / "phases" / "verify.md"


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-reported-")).resolve()
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
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

    def _verify_task(self, slug):
        """A fresh task driven to verify — §3/§6 both carry the template's unfilled Reported: line."""
        self._silent("new-task", slug, "--title", "Feature")
        self._silent("phase", "verify", slug)
        return self._task_md(slug)

    def _fill_contract_reported(self, slug):
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        t = re.sub(r"(?m)^Reported:.*$", "Reported: yes", t, count=1)
        p.write_text(t, encoding="utf-8")

    def _fill_verify_reported(self, slug):
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        # the SECOND "Reported:" line in the file belongs to §6 GATE RECORD
        parts = t.split("Reported:", 2)
        self.assertEqual(len(parts), 3, "expected two Reported: lines (§3 then §6)")
        t = parts[0] + "Reported:" + parts[1] + "Reported: yes" + re.sub(r"^[^\n]*", "", parts[2], count=1)
        p.write_text(t, encoding="utf-8")

    def _drop_contract_reported(self, slug):
        p = self._task_md(slug)
        t = re.sub(r"(?m)^Reported:.*\n", "", p.read_text(encoding="utf-8"), count=1)
        p.write_text(t, encoding="utf-8")

    def _drop_verify_reported(self, slug):
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        parts = t.split("Reported:", 2)
        self.assertEqual(len(parts), 3)
        t = parts[0] + "Reported:" + parts[1] + re.sub(r"^[^\n]*\n", "", parts[2], count=1)
        p.write_text(t, encoding="utf-8")


class ContractReportUnrecordedTest(_Harness):
    def test_audit_surfaces_unrecorded(self):                     # scenario 1
        self._verify_task("t")
        code, out = self._run("audit")
        self.assertIn("contract_report_unrecorded", out)
        self.assertIn("t", out)
        self.assertEqual(code, 0, "a notice, not a finding")

    def test_recorded_clears_notice(self):                        # scenario 2
        self._verify_task("t")
        self._fill_contract_reported("t")
        _, out = self._run("audit")
        m = re.search(r"contract_report_unrecorded[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        f"a recorded §3 report must clear the notice:\n{out}")

    def test_absent_line_grandfathers(self):                      # scenario 3
        self._verify_task("t")
        self._drop_contract_reported("t")
        code, out = self._run("audit")
        m = re.search(r"contract_report_unrecorded[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0), "absent line is never retro-flagged")
        self.assertEqual(code, 0)


class VerifyReportUnrecordedTest(_Harness):
    def test_audit_surfaces_unrecorded(self):                     # scenario 1 (verify twin)
        self._verify_task("t")
        code, out = self._run("audit")
        self.assertIn("verify_report_unrecorded", out)
        self.assertIn("t", out)
        self.assertEqual(code, 0, "a notice, not a finding")

    def test_recorded_clears_notice(self):                        # scenario 2 (verify twin)
        self._verify_task("t")
        self._fill_verify_reported("t")
        _, out = self._run("audit")
        m = re.search(r"verify_report_unrecorded[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        f"a recorded §6 report must clear the notice:\n{out}")

    def test_absent_line_grandfathers(self):                      # scenario 3 (verify twin)
        self._verify_task("t")
        self._drop_verify_reported("t")
        code, out = self._run("audit")
        m = re.search(r"verify_report_unrecorded[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0), "absent line is never retro-flagged")
        self.assertEqual(code, 0)

    def test_independent_of_contract_notice(self):                # both fire independently
        self._verify_task("t")
        self._fill_contract_reported("t")                          # clear §3 only
        _, out = self._run("audit")
        self.assertNotIn("contract_report_unrecorded", out)
        self.assertIn("verify_report_unrecorded", out)              # §6 still unfilled


class GroupedAndScopeTest(_Harness):
    def test_one_grouped_line_each(self):                          # grouped, like refute_unrecorded
        for s in ("a", "b", "c"):
            self._verify_task(s)
        _, out = self._run("audit")
        for code in ("contract_report_unrecorded", "verify_report_unrecorded"):
            self.assertEqual(out.count(code), 1, f"exactly ONE grouped line for {code}")
            m = re.search(rf"{code} — (\d+) task\(s\)[^\n]*", out)
            self.assertIsNotNone(m, f"a grouped 'N task(s)' line expected for {code}:\n{out}")
            self.assertEqual(int(m.group(1)), 3)

    def test_not_at_verify_is_silent(self):                        # phase < verify -> grandfather
        self._silent("new-task", "g", "--title", "X")               # stays at ground
        _, out = self._run("audit")
        self.assertNotIn("contract_report_unrecorded", out)
        self.assertNotIn("verify_report_unrecorded", out)


class MeasureNotBlockTest(_Harness):
    def test_gate_never_blocked_by_unrecorded(self):               # the core guarantee
        self._verify_task("t")
        code, out = self._run("gate", "PASS", "t")
        self.assertEqual(code, 0, f"an unrecorded report must NOT block a gate:\n{out}")
        state = json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["t"]["phase"], "done")
        self.assertEqual(state["tasks"]["t"]["gate"], "PASS")

    def test_no_new_reject_code_in_engine(self):                   # no hard gate shipped
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for bad in ("report_unrecorded_missing", "contract_report_missing", "verify_report_missing"):
            self.assertNotIn(bad, src, "measure-not-block: no hard-gate reject code may ship")


class TemplateAndWritebackTest(_Harness):
    def test_template_carries_contract_reported(self):             # scenario: template shape
        p = self._verify_task("t")
        body = p.read_text(encoding="utf-8")
        self.assertRegex(body, r"Status: DRAFT\nReported:\s*<[^>\n]+>",
                         "§3 Reported: must sit right after Status: DRAFT")

    def test_template_carries_verify_reported(self):
        p = self._verify_task("t")
        body = p.read_text(encoding="utf-8")
        self.assertRegex(body, r"### GATE RECORD\nReported:\s*<[^>\n]+>\nOutcome:",
                         "§6 Reported: must be the first line of GATE RECORD, before Outcome")

    def test_writebacks_inert_to_new_fields(self):                 # scenario: gate stamp doesn't mangle it
        self._verify_task("t")
        self._fill_contract_reported("t")
        self._fill_verify_reported("t")
        self._silent("gate", "PASS", "t")
        body = self._task_md("t").read_text(encoding="utf-8")
        self.assertEqual(body.count("Reported:"), 2, "gate stamp must not consume or duplicate either line")
        gate_region = body.split("### GATE RECORD", 1)[1]
        self.assertIn("PASS", gate_region, "_stamp_gate_record still stamped Outcome")


class JsonAndDisclosureTest(_Harness):
    def test_audit_json_has_both_keys(self):
        self._verify_task("t")
        _, out = self._run("audit", "--json")
        data = json.loads(out)
        for code in ("contract_report_unrecorded", "verify_report_unrecorded"):
            self.assertIn(code, data["guarantee_lints"])
            self.assertIn("t", data["guarantee_lints"][code])

    def test_disclosure_in_run_md(self):
        text = RUN_MD.read_text(encoding="utf-8")
        for code in ("contract_report_unrecorded", "verify_report_unrecorded"):
            self.assertIn(code, text, f"run.md must disclose {code}")

    def test_disclosure_in_contract_and_verify_guides(self):
        self.assertIn("Reported: yes", CONTRACT_MD.read_text(encoding="utf-8"),
                      "3-plan.md must instruct recording Reported: yes at the freeze")
        self.assertIn("Reported: yes", VERIFY_MD.read_text(encoding="utf-8"),
                      "6-verify.md must instruct recording Reported: yes at the gate")


if __name__ == "__main__":
    unittest.main(verbosity=2)
