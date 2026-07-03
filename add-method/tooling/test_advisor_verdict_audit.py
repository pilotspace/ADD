#!/usr/bin/env python3
"""Red/green tests for two new audit lint codes
(milestone advisor-gated-autonomy, task `advisor-verdict-audit`).

  advisor_reviewer_is_author     — advisor and gate actor share the same identity
  advisor_residue_on_mechanical_mis_tier — mechanical tier with non-none residue + PASS verdict

CONTRACT (frozen @ v1) — MEASURE-NOT-BLOCK (no hard gate, exit 0 always):
  _guarantee_lint_notices gains keys:
    advisor_reviewer_is_author[]       — flagged when Advisor name == gate_actor name (case-insensitive)
    advisor_residue_on_mechanical_mis_tier[] — flagged when sensitivity==mechanical AND Residue!='none' AND Verdict startswith 'PASS'
  cmd_audit: prints ONE grouped line per code (mirroring advisor_verdict_unrecorded style)
  cmd_audit --json: keys appear automatically in guarantee_lints
  Clean line: suppressed when either new code fires

Run: python3 -m unittest test_advisor_verdict_audit -v
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


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-advaudit-")).resolve()
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
        """A fresh task driven to verify — §6 carries the template's unfilled advisor block."""
        self._silent("new-task", slug, "--title", "Feature")
        self._silent("phase", "verify", slug)
        return self._task_md(slug)

    def _fill_reported(self, slug):
        """Record both Reported: yes lines (§3 + §6) — report-rendered-trace's new fields."""
        p = self._task_md(slug)
        t = re.sub(r"(?m)^Reported:.*$", "Reported: yes", p.read_text(encoding="utf-8"))
        p.write_text(t, encoding="utf-8")

    def _fill_advisor(self, slug, *, advisor="self", security="CLEAR", concurrency="CLEAR",
                      architecture="CLEAR", verdict="PASS", residue="none",
                      binding="advisory — low"):
        """Replace all <…> placeholders in the advisor block with real values."""
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        t = t.replace("Advisor: <agent-id | self>", f"Advisor: {advisor}")
        t = t.replace("1. Security: <CLEAR | HARD-STOP: finding>",
                      f"1. Security: {security}")
        t = t.replace("2. Concurrency: <CLEAR | RESIDUE: finding>",
                      f"2. Concurrency: {concurrency}")
        t = t.replace("3. Architecture: <CLEAR | RESIDUE: finding>",
                      f"3. Architecture: {architecture}")
        t = t.replace("Verdict: <PASS | HARD-STOP>", f"Verdict: {verdict}")
        t = t.replace("Residue: <none | summary>", f"Residue: {residue}")
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
        """Declare risk + sensitivity on the slug line."""
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8")
        t = re.sub(r"(?m)^(slug: .*?)$",
                   rf"\1 · risk: {risk} · sensitivity: {sensitivity}", t, count=1)
        p.write_text(t, encoding="utf-8")

    def _fill_deep_checks(self, slug):
        """Fill the §6 Deep checks placeholder."""
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8").replace(
            "<what read · what confirmed>", "read the diff in full; behaviour matches the contract")
        p.write_text(t, encoding="utf-8")

    def _gate_task(self, slug, outcome="PASS"):
        """Gate the task (phase → done, gate_actor is written to state).
        NOTE: this causes _audit_findings to audit the task; use _inject_gate_actor
        instead when the test also asserts exit code 0."""
        self._silent("gate", outcome, slug)

    def _get_gate_actor_name(self, slug):
        """Read gate_actor['name'] for slug from state.json."""
        state = json.loads(
            (self.tmp / ".add" / "state.json").read_text(encoding="utf-8")
        )
        return state["tasks"][slug].get("gate_actor", {}).get("name", "")

    def _inject_gate_actor(self, slug, name):
        """Write gate_actor directly into state.json WITHOUT changing phase/gate.
        This allows tests for advisor_reviewer_is_author to control the gate actor
        name without moving the task to 'done' (which triggers unstamped_freeze)."""
        sp = self.tmp / ".add" / "state.json"
        state = json.loads(sp.read_text(encoding="utf-8"))
        state["tasks"][slug]["gate_actor"] = {"name": name, "email": None, "source": "test"}
        sp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    def _set_advisor_name(self, slug, name):
        """Replace the Advisor: line in §6 with a specific name."""
        p = self._task_md(slug)
        t = re.sub(r"(?m)^Advisor:.*$", f"Advisor: {name}", p.read_text(encoding="utf-8"))
        p.write_text(t, encoding="utf-8")

    def _fill_all_noise_except(self, slug, *, keep_advisor_unfilled=False,
                               keep_refute_unfilled=False):
        """Fill all standard glints except those deliberately kept for testing."""
        self._set_header_dims(slug, risk="low", sensitivity="architecture")
        self._fill_deep_checks(slug)
        if not keep_refute_unfilled:
            self._also_fill_refute(slug)
        if not keep_advisor_unfilled:
            self._fill_advisor(slug)


# ---------------------------------------------------------------------------
# advisor_reviewer_is_author
# ---------------------------------------------------------------------------

class AdvisorReviewerIsAuthorTest(_Harness):
    def test_reviewer_same_as_gate_actor_is_flagged(self):      # scenario (a)
        """Advisor name == gate_actor name → flagged."""
        self._verify_task("t")
        # Use _inject_gate_actor to set gate_actor without moving task to 'done'
        # (which would trigger unstamped_freeze and exit 1, masking our glint test).
        self._inject_gate_actor("t", "Alice Reviewer")
        self._fill_advisor("t", advisor="Alice Reviewer")
        code, out = self._run("audit")
        self.assertEqual(code, 0, "MEASURE-NOT-BLOCK: must exit 0")
        self.assertIn("advisor_reviewer_is_author", out,
                      f"same identity must fire the lint:\n{out}")
        self.assertIn("t", out)

    def test_reviewer_different_from_gate_actor_not_flagged(self):  # scenario (b)
        """Advisor name ≠ gate_actor name → NOT flagged."""
        self._verify_task("t")
        self._fill_advisor("t", advisor="someone-else-entirely")
        self._gate_task("t")
        _, out = self._run("audit")
        m = re.search(r"advisor_reviewer_is_author[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        f"different identity must NOT fire the lint:\n{out}")

    def test_advisor_block_absent_not_flagged(self):             # scenario (c) part 1
        """Absent advisor block → advisor_reviewer_is_author NOT flagged."""
        self._verify_task("t")
        self._drop_advisor("t")
        self._gate_task("t")
        _, out = self._run("audit")
        m = re.search(r"advisor_reviewer_is_author[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        "absent advisor block must not fire advisor_reviewer_is_author")

    def test_unfilled_advisor_block_not_flagged(self):
        """Present-but-unfilled advisor block → advisor_reviewer_is_author NOT flagged
        (the filled check prevents double-counting with advisor_verdict_unrecorded)."""
        self._verify_task("t")
        # Do NOT fill advisor — it stays as template placeholders
        self._gate_task("t")
        _, out = self._run("audit")
        m = re.search(r"advisor_reviewer_is_author[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        "unfilled block must not fire advisor_reviewer_is_author")

    def test_no_gate_actor_not_flagged(self):
        """Task at verify with no gate_actor yet → NOT flagged (gate_actor name empty)."""
        self._verify_task("t")
        self._fill_advisor("t", advisor="some-name")
        # Do NOT gate → gate_actor is not set
        _, out = self._run("audit")
        m = re.search(r"advisor_reviewer_is_author[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        "no gate_actor → must not fire advisor_reviewer_is_author")

    def test_exit_zero_when_flagged(self):                       # exit 0 invariant
        """MEASURE-NOT-BLOCK: audit exits 0 even when advisor_reviewer_is_author fires."""
        self._verify_task("t")
        self._inject_gate_actor("t", "Bob Author")
        self._fill_advisor("t", advisor="Bob Author")
        code, _ = self._run("audit")
        self.assertEqual(code, 0)

    def test_grouped_one_line(self):
        """Multiple flagged tasks → single grouped N task(s) line."""
        for slug in ("a", "b"):
            self._verify_task(slug)
            self._fill_advisor(slug)
            self._gate_task(slug)
            actor_name = self._get_gate_actor_name(slug)
            self._set_advisor_name(slug, actor_name)
        _, out = self._run("audit")
        self.assertEqual(out.count("advisor_reviewer_is_author"), 1,
                         "exactly ONE grouped line expected")
        m = re.search(r"advisor_reviewer_is_author — (\d+) task\(s\)[^\n]*", out)
        self.assertIsNotNone(m, f"grouped 'N task(s)' line expected:\n{out}")
        self.assertEqual(int(m.group(1)), 2)


# ---------------------------------------------------------------------------
# advisor_residue_on_mechanical_mis_tier
# ---------------------------------------------------------------------------

class AdvisorResidueOnMechanicalMisTierTest(_Harness):
    def test_mechanical_residue_non_none_pass_verdict_flagged(self):  # scenario (d)
        """mechanical sensitivity + Residue non-none + Verdict PASS → flagged."""
        self._verify_task("t")
        self._set_header_dims("t", risk="low", sensitivity="mechanical")
        self._fill_advisor("t", residue="leftover concern", verdict="PASS")
        _, out = self._run("audit")
        self.assertIn("advisor_residue_on_mechanical_mis_tier", out,
                      f"mechanical+residue+PASS must fire the lint:\n{out}")
        self.assertIn("t", out)

    def test_mechanical_residue_none_not_flagged(self):           # scenario (e)
        """mechanical sensitivity + Residue=none → NOT flagged."""
        self._verify_task("t")
        self._set_header_dims("t", risk="low", sensitivity="mechanical")
        self._fill_advisor("t", residue="none", verdict="PASS")
        _, out = self._run("audit")
        m = re.search(r"advisor_residue_on_mechanical_mis_tier[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        f"residue=none must NOT fire the lint:\n{out}")

    def test_non_mechanical_sensitivity_with_residue_not_flagged(self):  # scenario (f)
        """non-mechanical sensitivity + Residue non-none → NOT flagged."""
        self._verify_task("t")
        self._set_header_dims("t", risk="low", sensitivity="architecture")
        self._fill_advisor("t", residue="some concern", verdict="PASS")
        _, out = self._run("audit")
        m = re.search(r"advisor_residue_on_mechanical_mis_tier[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        f"non-mechanical sensitivity must NOT fire the lint:\n{out}")

    def test_mechanical_hard_stop_verdict_not_flagged(self):
        """mechanical + Residue non-none + Verdict HARD-STOP → NOT flagged (Verdict not PASS)."""
        self._verify_task("t")
        self._set_header_dims("t", risk="low", sensitivity="mechanical")
        self._fill_advisor("t", residue="critical defect", verdict="HARD-STOP")
        _, out = self._run("audit")
        m = re.search(r"advisor_residue_on_mechanical_mis_tier[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        f"HARD-STOP verdict must NOT fire the lint:\n{out}")

    def test_advisor_block_absent_not_flagged(self):             # scenario (c) part 2
        """Absent advisor block → advisor_residue_on_mechanical_mis_tier NOT flagged."""
        self._verify_task("t")
        self._set_header_dims("t", risk="low", sensitivity="mechanical")
        self._drop_advisor("t")
        _, out = self._run("audit")
        m = re.search(r"advisor_residue_on_mechanical_mis_tier[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        "absent advisor block must not fire advisor_residue_on_mechanical_mis_tier")

    def test_exit_zero_when_flagged(self):                       # exit 0 invariant
        """MEASURE-NOT-BLOCK: audit exits 0 even when advisor_residue_on_mechanical_mis_tier fires."""
        self._verify_task("t")
        self._set_header_dims("t", risk="low", sensitivity="mechanical")
        self._fill_advisor("t", residue="leftover concern", verdict="PASS")
        code, _ = self._run("audit")
        self.assertEqual(code, 0)

    def test_grouped_one_line(self):
        """Multiple flagged tasks → single grouped N task(s) line."""
        for slug in ("a", "b"):
            self._verify_task(slug)
            self._set_header_dims(slug, risk="low", sensitivity="mechanical")
            self._fill_advisor(slug, residue="some concern", verdict="PASS")
        _, out = self._run("audit")
        self.assertEqual(out.count("advisor_residue_on_mechanical_mis_tier"), 1,
                         "exactly ONE grouped line expected")
        m = re.search(r"advisor_residue_on_mechanical_mis_tier — (\d+) task\(s\)[^\n]*", out)
        self.assertIsNotNone(m, f"grouped 'N task(s)' line expected:\n{out}")
        self.assertEqual(int(m.group(1)), 2)

    def test_case_insensitive_residue_none(self):
        """Residue: None (capitalised) should still suppress the lint."""
        self._verify_task("t")
        self._set_header_dims("t", risk="low", sensitivity="mechanical")
        self._fill_advisor("t", residue="None", verdict="PASS")
        _, out = self._run("audit")
        m = re.search(r"advisor_residue_on_mechanical_mis_tier[^\n]*", out)
        self.assertTrue(m is None or "t" not in m.group(0),
                        "residue=None (capitalised) must suppress the lint")


# ---------------------------------------------------------------------------
# JSON output — scenario (g): new codes never in findings, appear in guarantee_lints
# ---------------------------------------------------------------------------

class JsonOutputTest(_Harness):
    def test_reviewer_is_author_in_json_guarantee_lints(self):
        """advisor_reviewer_is_author appears in guarantee_lints when fired."""
        self._verify_task("t")
        self._fill_advisor("t")
        self._gate_task("t")
        actor_name = self._get_gate_actor_name("t")
        self._set_advisor_name("t", actor_name)
        _, out = self._run("audit", "--json")
        data = json.loads(out)
        self.assertIn("advisor_reviewer_is_author", data["guarantee_lints"],
                      "key must appear in guarantee_lints")
        self.assertIn("t", data["guarantee_lints"]["advisor_reviewer_is_author"])

    def test_mis_tier_in_json_guarantee_lints(self):
        """advisor_residue_on_mechanical_mis_tier appears in guarantee_lints when fired."""
        self._verify_task("t")
        self._set_header_dims("t", risk="low", sensitivity="mechanical")
        self._fill_advisor("t", residue="concern", verdict="PASS")
        _, out = self._run("audit", "--json")
        data = json.loads(out)
        self.assertIn("advisor_residue_on_mechanical_mis_tier", data["guarantee_lints"])
        self.assertIn("t", data["guarantee_lints"]["advisor_residue_on_mechanical_mis_tier"])

    def test_new_codes_not_in_findings(self):                    # scenario (g)
        """Both new codes must NEVER appear in findings (MEASURE-NOT-BLOCK)."""
        self._verify_task("t")
        self._fill_advisor("t")
        self._gate_task("t")
        actor_name = self._get_gate_actor_name("t")
        self._set_advisor_name("t", actor_name)
        _, out = self._run("audit", "--json")
        data = json.loads(out)
        finding_codes = [f["code"] for f in data.get("findings", [])]
        self.assertNotIn("advisor_reviewer_is_author", finding_codes)
        self.assertNotIn("advisor_residue_on_mechanical_mis_tier", finding_codes)

    def test_json_keys_present_even_when_not_fired(self):
        """guarantee_lints always carries both keys (empty lists when not fired)."""
        _, out = self._run("audit", "--json")
        data = json.loads(out)
        self.assertIn("advisor_reviewer_is_author", data["guarantee_lints"])
        self.assertIn("advisor_residue_on_mechanical_mis_tier", data["guarantee_lints"])


# ---------------------------------------------------------------------------
# Clean-line guard — scenario (h): suppressed when either new code fires
# ---------------------------------------------------------------------------

class CleanLineGuardTest(_Harness):
    def test_clean_suppressed_when_reviewer_is_author(self):     # scenario (h) part 1
        """Clean line must NOT print when advisor_reviewer_is_author fires."""
        self._verify_task("t")
        self._set_header_dims("t", risk="low", sensitivity="architecture")
        self._fill_deep_checks("t")
        self._also_fill_refute("t")
        self._fill_advisor("t")
        self._gate_task("t")
        actor_name = self._get_gate_actor_name("t")
        self._set_advisor_name("t", actor_name)
        _, out = self._run("audit")
        self.assertNotIn("audit: clean", out,
                         "clean must be suppressed when advisor_reviewer_is_author fires")
        self.assertIn("advisor_reviewer_is_author", out)

    def test_clean_suppressed_when_mis_tier_fires(self):         # scenario (h) part 2
        """Clean line must NOT print when advisor_residue_on_mechanical_mis_tier fires."""
        self._verify_task("t")
        self._set_header_dims("t", risk="low", sensitivity="mechanical")
        self._fill_deep_checks("t")
        self._also_fill_refute("t")
        self._fill_advisor("t", residue="some residue", verdict="PASS")
        _, out = self._run("audit")
        self.assertNotIn("audit: clean", out,
                         "clean must be suppressed when advisor_residue_on_mechanical_mis_tier fires")
        self.assertIn("advisor_residue_on_mechanical_mis_tier", out)

    def test_clean_appears_when_both_new_codes_clear(self):
        """audit: clean appears when all glints (including both new codes) are empty.
        Task stays at verify (no gate_actor) so _audit_findings skips it.
        advisor_reviewer_is_author requires BOTH names non-empty — no gate_actor → not fired.
        advisor_residue_on_mechanical_mis_tier requires sensitivity==mechanical — not fired."""
        self._verify_task("t")
        self._set_header_dims("t", risk="low", sensitivity="architecture")
        self._fill_deep_checks("t")
        self._also_fill_refute("t")
        # Fill advisor with a real name; no gate_actor → reviewer_is_author won't fire.
        self._fill_advisor("t", advisor="alice")
        self._fill_reported("t")
        # No _gate_task → task remains verify/gate=none → _audit_findings skips → exit 0.
        code, out = self._run("audit")
        self.assertEqual(code, 0)
        self.assertIn("audit: clean", out,
                      f"fully clean task must print the clean line:\n{out}")
        self.assertNotIn("advisor_reviewer_is_author", out)
        self.assertNotIn("advisor_residue_on_mechanical_mis_tier", out)


if __name__ == "__main__":
    unittest.main()
