#!/usr/bin/env python3
"""Red/green tests for the advisor 3-lens verdict block
(milestone advisor-gated-autonomy, task `advisor-review-step`).

CONTRACT (frozen @ v1) — MEASURE-NOT-BLOCK (no hard gate):
  templates/TASK.md.tmpl §6 gains a `### Advisor 3-lens verdict` block AFTER the
    `### Refute-read verdict` block and BEFORE `### GATE RECORD`.
    The block carries `<…>`-placeholder lines for Advisor, 1-3 lens results,
    Verdict, Residue, Binding.
  _guarantee_lint_notices(root, state) gains key  advisor_verdict_unrecorded: [slug...]
    scope: tasks with phase in {verify, observe, done} whose §6 block is PRESENT-but-unfilled
    (_section_unfilled "### Advisor 3-lens verdict"); ABSENT block -> grandfathered (not listed).
    NO autonomy filter — mirror refute_unrecorded EXACTLY.
  cmd_audit: prints ONE grouped "advisor_verdict_unrecorded — N task(s): <slugs> — ..."; EXIT 0.
  cmd_audit --json: additive guarantee_lints["advisor_verdict_unrecorded"] = [...].
  cmd_gate: UNCHANGED — an unfilled block NEVER blocks a gate (MEASURE-NOT-BLOCK).
  Clean line: "audit: clean (N tasks checked)" only when advisor_verdict_unrecorded is also empty.
One test per scenario. Run: python3 -m unittest test_advisor_review_step -v
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

ADVISOR_HEADER = "### Advisor 3-lens verdict"


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-advisor-")).resolve()
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
        """A fresh task driven to verify — its §6 carries the template's unfilled advisor block."""
        self._silent("new-task", slug, "--title", "Feature")
        self._silent("phase", "verify", slug)
        return self._task_md(slug)

    def _fill_advisor(self, slug, *, security="CLEAR", concurrency="CLEAR",
                      architecture="CLEAR", verdict="PASS", residue="none",
                      binding="advisory — low"):
        """Replace all <…> placeholders in the advisor block with real values."""
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        t = t.replace("Advisor: <agent-id | self>", "Advisor: self")
        t = t.replace("1. Security: <CLEAR | HARD-STOP: finding>",
                      f"1. Security: {security}")
        t = t.replace("2. Concurrency: <CLEAR | RESIDUE: finding>",
                      f"2. Concurrency: {concurrency}")
        t = t.replace("3. Architecture: <CLEAR | RESIDUE: finding>",
                      f"3. Architecture: {architecture}")
        t = t.replace("Verdict: <PASS | HARD-STOP>", f"Verdict: {verdict}")
        t = t.replace("Residue: <none | summary>", f"Residue: {residue}")
        # The Binding placeholder nests angle-brackets; handle it broadly
        t = re.sub(r"Binding: <[^>\n]+(?:<[^>\n]+>)?[^>\n]*>",
                   f"Binding: {binding}", t)
        p.write_text(t, encoding="utf-8")

    def _drop_advisor(self, slug):
        """Remove the entire advisor block (simulates a legacy TASK.md without it)."""
        p = self._task_md(slug)
        t = re.sub(
            r"### Advisor 3-lens verdict.*?(?=\n### GATE RECORD)",
            "",
            p.read_text(encoding="utf-8"),
            flags=re.DOTALL,
        )
        p.write_text(t, encoding="utf-8")

    def _also_fill_refute(self, slug):
        """Fill the refute block so that block doesn't pollute audit output."""
        p = self._task_md(slug)
        t = (p.read_text(encoding="utf-8")
             .replace("Verdict: <EARNED | NOT-EARNED>", "Verdict: EARNED")
             .replace("<self | agent-id>", "self")
             .replace("<what was probed>", "the whole diff"))
        p.write_text(t, encoding="utf-8")

    def _set_header_dims(self, slug, *, risk="low", sensitivity="architecture"):
        """Declare risk + sensitivity on the slug line (clears risk_unset / sensitivity_unset).
        Uses risk: low (NOT high) so unguarded_high_risk_auto never fires."""
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        t = re.sub(r"(?m)^(slug: .*?)$",
                   rf"\1 · risk: {risk} · sensitivity: {sensitivity}", t, count=1)
        p.write_text(t, encoding="utf-8")

    def _fill_deep_checks(self, slug):
        """Fill the §6 Deep checks placeholder (clears the 'shallow' glint)."""
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8").replace(
            "<what read · what confirmed>", "read the diff in full; behaviour matches the contract")
        p.write_text(t, encoding="utf-8")


# ---------------------------------------------------------------------------
# Scenario (b) — present-but-unfilled → flagged, exit 0
# ---------------------------------------------------------------------------

class AdvisorVerdictUnrecordedNoticeTest(_Harness):
    def test_audit_surfaces_unrecorded(self):                  # scenario b
        self._verify_task("t")
        code, out = self._run("audit")
        self.assertIn("advisor_verdict_unrecorded", out)
        self.assertIn("t", out)
        self.assertEqual(code, 0, "a notice, not a finding")

    def test_recorded_verdict_clears_notice(self):             # scenario a — filled → not flagged
        self._verify_task("t")
        self._fill_advisor("t")
        _, out = self._run("audit")
        m = re.search(r"advisor_verdict_unrecorded[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        f"a recorded verdict must clear the notice:\n{out}")

    def test_absent_block_grandfathers(self):                  # scenario f — legacy task
        self._verify_task("t")
        self._drop_advisor("t")
        code, out = self._run("audit")
        m = re.search(r"advisor_verdict_unrecorded[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        "absent block is never retro-flagged")
        self.assertEqual(code, 0)

    def test_one_grouped_line(self):                           # grouped like refute_unrecorded
        for s in ("a", "b", "c"):
            self._verify_task(s)
        _, out = self._run("audit")
        self.assertEqual(out.count("advisor_verdict_unrecorded"), 1,
                         "exactly ONE grouped line")
        m = re.search(r"advisor_verdict_unrecorded — (\d+) task\(s\)[^\n]*", out)
        self.assertIsNotNone(m, f"a grouped 'N task(s)' line expected:\n{out}")
        self.assertEqual(int(m.group(1)), 3)

    def test_not_at_verify_is_silent(self):                    # pre-verify → not flagged
        self._silent("new-task", "g", "--title", "X")         # stays at ground
        _, out = self._run("audit")
        self.assertNotIn("advisor_verdict_unrecorded", out)


# ---------------------------------------------------------------------------
# Scenario (c) — Security HARD-STOP shape → counts as filled (not flagged)
# ---------------------------------------------------------------------------

class HardStopVerdictTest(_Harness):
    def test_security_hard_stop_not_flagged(self):             # scenario c
        self._verify_task("t")
        self._fill_advisor(
            "t",
            security="HARD-STOP: SQL injection in query builder",
            concurrency="",            # left blank per HARD-STOP rule
            architecture="",
            verdict="HARD-STOP",
            residue="SQL injection risk in query builder",
            binding="advisory — low",
        )
        _, out = self._run("audit")
        m = re.search(r"advisor_verdict_unrecorded[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        f"a HARD-STOP shape is filled — must not be flagged:\n{out}")


# ---------------------------------------------------------------------------
# Scenario (d) — Binding "yes — mechanical" → filled, not flagged
# ---------------------------------------------------------------------------

class MechanicalBindingTest(_Harness):
    def test_mechanical_binding_not_flagged(self):             # scenario d
        self._verify_task("t")
        self._fill_advisor("t", binding="yes — mechanical", verdict="PASS")
        _, out = self._run("audit")
        m = re.search(r"advisor_verdict_unrecorded[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        f"mechanical binding is filled — must not be flagged:\n{out}")


# ---------------------------------------------------------------------------
# Scenario (e) — Binding "advisory — architecture" → filled, not flagged
# ---------------------------------------------------------------------------

class AdvisoryBindingTest(_Harness):
    def test_advisory_binding_not_flagged(self):               # scenario e
        self._verify_task("t")
        self._fill_advisor("t", binding="advisory — architecture", verdict="PASS")
        _, out = self._run("audit")
        m = re.search(r"advisor_verdict_unrecorded[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        f"advisory binding is filled — must not be flagged:\n{out}")


# ---------------------------------------------------------------------------
# MEASURE-NOT-BLOCK — gate is never blocked, exit code stays 0
# ---------------------------------------------------------------------------

class MeasureNotBlockTest(_Harness):
    def test_gate_never_blocked_by_unrecorded(self):           # gate unaffected
        self._verify_task("t")
        code, out = self._run("gate", "PASS", "t")
        self.assertEqual(code, 0,
                         f"an unfilled advisor block must NOT block a gate:\n{out}")
        state = json.loads(
            (self.tmp / ".add" / "state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(state["tasks"]["t"]["phase"], "done")
        self.assertEqual(state["tasks"]["t"]["gate"], "PASS")

    def test_no_new_reject_code_in_engine(self):               # no hard gate
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        self.assertNotIn("advisor_verdict_missing", src,
                         "design is measure-not-block: no hard-gate reject code may ship")

    def test_audit_exit_zero_with_notice(self):                # notice never raises exit
        self._verify_task("t")
        code, _ = self._run("audit")
        self.assertEqual(code, 0)


# ---------------------------------------------------------------------------
# Template placement — must appear after Refute-read and before GATE RECORD
# ---------------------------------------------------------------------------

class TemplatePlacementTest(_Harness):
    def test_template_carries_advisor_block(self):             # block exists with placeholders
        p = self._verify_task("t")
        body = p.read_text(encoding="utf-8")
        self.assertIn(ADVISOR_HEADER, body)
        self.assertRegex(body, r"Advisor:\s*<[^>\n]+>", "ships an unfilled Advisor placeholder")
        self.assertRegex(body, r"Verdict:\s*<[^>\n]+>")
        self.assertRegex(body, r"Binding:\s*<[^>\n]+")

    def test_block_position_after_refute_before_gate(self):    # ordering invariant
        p = self._verify_task("t")
        body = p.read_text(encoding="utf-8")
        i_refute = body.find("### Refute-read verdict")
        i_advisor = body.find(ADVISOR_HEADER)
        i_gate = body.find("### GATE RECORD")
        self.assertGreater(i_refute, -1, "Refute-read verdict block must still exist")
        self.assertGreater(i_advisor, -1, "Advisor block must exist")
        self.assertGreater(i_gate, -1, "GATE RECORD must exist")
        self.assertLess(i_refute, i_advisor,
                        "Advisor block must sit AFTER Refute-read verdict")
        self.assertLess(i_advisor, i_gate,
                        "Advisor block must sit BEFORE GATE RECORD")


# ---------------------------------------------------------------------------
# Scenario (g) — clean line only when advisor_verdict_unrecorded is ALSO empty
# ---------------------------------------------------------------------------

class CleanLineGuardTest(_Harness):
    def test_clean_line_suppressed_when_advisor_unrecorded(self): # scenario g
        self._verify_task("t")
        # also fill other notices so only advisor_verdict_unrecorded fires
        self._also_fill_refute("t")
        _, out = self._run("audit")
        self.assertNotIn("audit: clean", out,
                         "clean line must NOT print when advisor_verdict_unrecorded fires")
        self.assertIn("advisor_verdict_unrecorded", out)

    def test_clean_line_appears_when_advisor_also_empty(self):    # clean when all clear
        # Provision a FULLY clean task: header dims set, deep-checks + refute + advisor
        # all filled, so every glint list is empty and "audit: clean" must print with
        # the new advisor_verdict_unrecorded guard in the conjunction.
        self._verify_task("t")
        self._set_header_dims("t", risk="low", sensitivity="architecture")
        self._fill_deep_checks("t")
        self._also_fill_refute("t")
        self._fill_advisor("t")
        code, out = self._run("audit")
        self.assertEqual(code, 0)
        self.assertIn("audit: clean", out,
                      f"a fully-clean task must print the clean line (new guard included):\n{out}")
        self.assertNotIn("advisor_verdict_unrecorded", out,
                         "no advisor notice on a filled block")


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

class JsonOutputTest(_Harness):
    def test_audit_json_has_advisor_key(self):                 # json shape
        self._verify_task("t")
        _, out = self._run("audit", "--json")
        data = json.loads(out)
        self.assertIn("advisor_verdict_unrecorded", data["guarantee_lints"])
        self.assertIn("t", data["guarantee_lints"]["advisor_verdict_unrecorded"])

    def test_advisor_key_not_in_findings(self):                # NEVER a finding
        self._verify_task("t")
        _, out = self._run("audit", "--json")
        data = json.loads(out)
        finding_codes = [f["code"] for f in data.get("findings", [])]
        self.assertNotIn("advisor_verdict_unrecorded", finding_codes,
                         "advisor_verdict_unrecorded is a glint, never a finding")


if __name__ == "__main__":
    unittest.main(verbosity=2)
