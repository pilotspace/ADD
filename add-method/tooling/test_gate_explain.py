"""gate-explain (method-ergonomics): the composed gate-decision answer, engine-printed.

CONTRACT — READ-ONLY, additive:
  `add.py gate --explain [slug]` prints the composed auto-pass/escalation path for the task,
  composed from the SAME predicates cmd_gate enforces (autonomy header · risk: high guard ·
  sensitivity · advisor 3-lens verdict · advisor-gate-relax), then exits 0 writing NOTHING.
  Output contract (machine-greppable):
    line 1: `gate-explain <slug>`; a `path: <AUTO|HUMAN|RELAX|REFUSED>` line; the security
    floor named on every path (`security` + `HARD-STOP`).
  Path table: lowered autonomy -> HUMAN · risk:high unguarded & unrelaxed -> REFUSED
  (names unguarded_high_risk_auto) · mechanical + advisor PASS/none -> RELAX · else AUTO.
  Plain `add.py gate` without an outcome still refuses exactly as before.
Run: python3 -m unittest test_gate_explain -v
"""
import contextlib
import io
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import add


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-gex-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("lock", "--force")
        self._silent("new-task", "t", "--title", "F")
        self.md = self.tmp / ".add" / "tasks" / "t" / "PLAN.md"

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

    def _set_header(self, **kv):
        t = self.md.read_text(encoding="utf-8")
        if kv.get("autonomy"):
            t = t.replace("autonomy: auto", f"autonomy: {kv['autonomy']}")
        if kv.get("risk_high"):
            t = t.replace("slug: t ·", "slug: t · risk: high ·")
        if kv.get("sensitivity"):
            t = t.replace("phase: direction", f"sensitivity: {kv['sensitivity']}\nphase: direction", 1)
        self.md.write_text(t, encoding="utf-8")

    def _fill_advisor_pass(self):
        t = (self.md.read_text(encoding="utf-8")
             .replace("Advisor: <agent-id | self>", "Advisor: self")
             .replace("1. Security: <CLEAR | HARD-STOP: finding>", "1. Security: CLEAR")
             .replace("2. Concurrency: <CLEAR | RESIDUE: finding>", "2. Concurrency: CLEAR")
             .replace("3. Architecture: <CLEAR | RESIDUE: finding>", "3. Architecture: CLEAR")
             .replace("Verdict: <PASS | HARD-STOP>", "Verdict: PASS")
             .replace("Residue: <none | summary>", "Residue: none")
             .replace("Binding: <yes — mechanical | advisory — <sensitivity>>", "Binding: yes — mechanical"))
        self.md.write_text(t, encoding="utf-8")


class ExplainPathsTest(_Harness):
    def test_auto_path(self):                                    # scenario 1
        out = self._silent("gate", "--explain", "t")
        self.assertIn("gate-explain t", out)
        self.assertIn("path: AUTO", out)

    def test_human_path_on_lowered(self):                        # scenario 2
        self._set_header(autonomy="conservative")
        out = self._silent("gate", "--explain", "t")
        self.assertIn("path: HUMAN", out)

    def test_refused_path_on_unguarded_high_risk(self):          # scenario 3
        self._set_header(risk_high=True)
        out = self._silent("gate", "--explain", "t")
        self.assertIn("path: REFUSED", out)
        self.assertIn("unguarded_high_risk_auto", out)

    def test_relax_path_mechanical_clean_advisor(self):          # scenario 4
        self._set_header(risk_high=True, sensitivity="mechanical")
        self._fill_advisor_pass()
        out = self._silent("gate", "--explain", "t")
        self.assertIn("path: RELAX", out)

    def test_security_floor_named_on_every_path(self):           # scenario 5
        for setup in (dict(), dict(autonomy="conservative")):
            h = _Harness()  # fresh project per variant
            h.setUp()
            try:
                if setup:
                    h._set_header(**setup)
                out = h._silent("gate", "--explain", "t")
                self.assertIn("security", out.lower())
                self.assertIn("HARD-STOP", out)
            finally:
                h.tearDown()
                h.doCleanups()


class ExplainSafetyTest(_Harness):
    def test_read_only(self):                                    # scenario 6
        state = self.tmp / ".add" / "state.json"
        before = state.read_bytes()
        self._silent("gate", "--explain", "t")
        self.assertEqual(before, state.read_bytes(), "--explain writes NOTHING")

    def test_plain_gate_still_requires_outcome(self):            # scenario 7
        code, out = self._run("gate")
        self.assertNotEqual(code, 0)
        self.assertIn("outcome must be one of", out)


if __name__ == "__main__":
    unittest.main()
