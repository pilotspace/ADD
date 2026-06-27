#!/usr/bin/env python3
"""Red/green tests for the guarantee-audit-lints notices
(milestone flow-honesty, task `guarantee-audit-lints`, M3).

CONTRACT (frozen @ v1) — two PRESENCE-ONLY, MEASURE-NOT-BLOCK notices on read-only `add.py audit`:
  _guarantee_lint_notices(root, state) -> {"shallow": [slug...], "risk_unset": [slug...]}
    scope: tasks with phase in {verify, observe, done}
    shallow    = _section_unfilled(<§6 body>, "### Deep checks")  (ABSENT block -> grandfathered)
    risk_unset = header has NO risk: token (_RISK_ANY_RE)
  cmd_audit: prints "shallow_deep_check <slug>" per-task + ONE grouped "risk_unset — N task(s): ..."
             line, AFTER findings + freeze_skips; the EXIT CODE is unchanged (notices never raise it).
  cmd_audit --json: additive "guarantee_lints": {"shallow": [...], "risk_unset": [...]}.
One test per scenario. Run: python3 -m unittest test_guarantee_lints -v
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


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-glint-")).resolve()
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

    # --- task builders -------------------------------------------------------
    def _verify_task(self, slug):
        """A fresh task driven to verify: §6 Deep-checks UNFILLED + header has no risk: token."""
        self._silent("new-task", slug, "--title", "Feature")
        self._silent("phase", "verify", slug)
        return self._task_md(slug)

    def _fill_deepcheck(self, slug):
        p = self._task_md(slug)
        p.write_text(p.read_text(encoding="utf-8").replace(
            "<what read · what confirmed>", "read both guides in full; confirmed the disclosure"),
            encoding="utf-8")

    def _drop_deepcheck(self, slug):
        p = self._task_md(slug)
        t = re.sub(r"### Deep checks.*?(?=\n### GATE RECORD)", "", p.read_text(encoding="utf-8"),
                   flags=re.DOTALL)
        p.write_text(t, encoding="utf-8")

    def _declare_risk(self, slug):
        p = self._task_md(slug)
        t = p.read_text(encoding="utf-8").replace("· stage: mvp", "· stage: mvp · risk: high", 1)
        p.write_text(t, encoding="utf-8")


class ShallowDeepCheckTest(_Harness):
    def test_shallow_surfaces_unfilled_block(self):          # Must (scenario 1)
        self._verify_task("t")
        code, out = self._run("audit")
        self.assertIn("shallow_deep_check t", out)
        self.assertEqual(code, 0, "a notice, not a finding")

    def test_filled_block_not_flagged(self):                 # filled -> silent
        self._verify_task("t")
        self._fill_deepcheck("t")
        _, out = self._run("audit")
        self.assertNotIn("shallow_deep_check t", out)

    def test_absent_block_grandfathered(self):               # Reject (grandfather)
        self._verify_task("t")
        self._drop_deepcheck("t")
        code, out = self._run("audit")
        self.assertNotIn("shallow_deep_check t", out)
        self.assertEqual(code, 0)

    def test_not_at_verify_is_silent(self):                  # Reject (phase < verify)
        self._silent("new-task", "g", "--title", "X")        # stays at ground
        _, out = self._run("audit")
        self.assertNotIn("shallow_deep_check g", out)
        self.assertNotIn("risk_unset", out, "a ground task triggers no risk_unset either")


class RiskUnsetTest(_Harness):
    def test_risk_unset_is_one_grouped_notice(self):         # Must (scenario 2)
        for s in ("a", "b", "c"):
            self._verify_task(s)
        code, out = self._run("audit")
        m = re.search(r"risk_unset — (\d+) task\(s\)[^\n]*", out)
        self.assertIsNotNone(m, f"one grouped risk_unset line expected:\n{out}")
        self.assertEqual(int(m.group(1)), 3)
        self.assertEqual(out.count("risk_unset"), 1, "exactly ONE grouped line, not per-task")
        for s in ("a", "b", "c"):
            self.assertIn(s, m.group(0))
        self.assertEqual(code, 0)

    def test_declared_risk_excluded(self):                   # Reject (risk declared)
        self._verify_task("hi")
        self._declare_risk("hi")
        self._verify_task("lo")
        code, out = self._run("audit")
        m = re.search(r"risk_unset — \d+ task\(s\)[^\n]*", out)
        self.assertIsNotNone(m)
        self.assertIn("lo", m.group(0))
        self.assertNotIn("hi", m.group(0), "a risk:-declared task is excluded")


class ExitCodeAndJsonTest(_Harness):
    def test_notices_keep_exit_zero(self):                   # Must (exit unchanged)
        self._verify_task("t")
        code, out = self._run("audit")
        self.assertEqual(code, 0)
        self.assertTrue("shallow_deep_check" in out or "risk_unset" in out)

    def test_findings_still_exit_one(self):                  # notices don't MASK findings
        self._silent("new-task", "t", "--title", "X")
        self._silent("phase", "verify", "t")
        self._silent("gate", "PASS", "t")                    # done, auto-gate reviewer
        self._declare_risk("t")                              # risk: high w/ unlowered autonomy
        code, out = self._run("audit")
        self.assertIn("unguarded_high_risk_auto", out)
        self.assertEqual(code, 1, "a real finding still exits 1, notices notwithstanding")

    def test_json_carries_guarantee_lints(self):             # Must (--json)
        self._verify_task("t")
        _, out = self._run("audit", "--json")
        data = json.loads(out)
        self.assertIn("guarantee_lints", data)
        self.assertIn("t", data["guarantee_lints"]["shallow"])
        self.assertIn("t", data["guarantee_lints"]["risk_unset"])
        self.assertIn("findings", data)
        self.assertIn("freeze_skips", data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
