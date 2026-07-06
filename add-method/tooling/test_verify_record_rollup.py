"""verify-record-rollup (method-ergonomics): ONE derived summary glint for the §6 verify record.

CONTRACT — ADDITIVE, MEASURE-NOT-BLOCK, append-frozen lint vocabulary:
  _guarantee_lint_notices gains a DERIVED key  verify_record_incomplete: [slug...]
    = sorted, per-slug-deduped union of the four §6 record lists
      (shallow ∪ refute_unrecorded ∪ advisor_verdict_unrecorded ∪ verify_report_unrecorded).
    Same scope as its members: tasks with phase in {verify, observe, done} only.
  cmd_audit: prints exactly ONE grouped "verify_record_incomplete — N task(s): <slugs> — ..."
    line AFTER the existing per-code lines, ONLY when the union is non-empty. The line must NOT
    contain any of the four member code tokens (their own "exactly one grouped line" pins hold).
  cmd_audit --json: additive guarantee_lints["verify_record_incomplete"].
  Exit code unchanged (a notice, never a finding). Clean-line conjunction unchanged (derived key
  is empty exactly when its members are).
  Guides: phases/4-tests.md (BOTH skill twins) instructs pre-declaring the §6 Build-expectations
  block at TESTS time, before build.
One test per scenario. Run: python3 -m unittest test_verify_record_rollup -v
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
SKILL_TESTS_MD = ADD_METHOD / "skill" / "add" / "phases" / "4-tests.md"
DOGFOOD_TESTS_MD = REPO / ".claude" / "skills" / "add" / "phases" / "4-tests.md"

ROLLUP = "verify_record_incomplete"
MEMBER_CODES = ("shallow_deep_check", "refute_unrecorded",
                "advisor_verdict_unrecorded", "verify_report_unrecorded")


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-rollup-")).resolve()
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
        self._silent("new-task", slug, "--title", "Feature")
        self._silent("phase", "verify", slug)
        return self._task_md(slug)

    # -- §6 record fills (mirror the sibling suites' replacement style) --------

    def _fill_deep(self, slug):
        p = self._task_md(slug)
        p.write_text(p.read_text(encoding="utf-8").replace(
            "<what read · what confirmed>", "read the diff in full · confirmed"),
            encoding="utf-8")

    def _fill_refute(self, slug):
        p = self._task_md(slug)
        t = (p.read_text(encoding="utf-8")
             .replace("Verdict: <EARNED | NOT-EARNED>", "Verdict: EARNED")
             .replace("<self | agent-id>", "self")
             .replace("<what was probed>", "the whole diff, adversarially"))
        p.write_text(t, encoding="utf-8")

    def _fill_advisor(self, slug):
        p = self._task_md(slug)
        t = (p.read_text(encoding="utf-8")
             .replace("Advisor: <agent-id | self>", "Advisor: self")
             .replace("1. Security: <CLEAR | HARD-STOP: finding>", "1. Security: CLEAR")
             .replace("2. Concurrency: <CLEAR | RESIDUE: finding>", "2. Concurrency: CLEAR")
             .replace("3. Architecture: <CLEAR | RESIDUE: finding>", "3. Architecture: CLEAR")
             .replace("Verdict: <PASS | HARD-STOP>", "Verdict: PASS")
             .replace("Residue: <none | summary>", "Residue: none")
             .replace("Binding: <yes — mechanical | advisory — <sensitivity>>",
                      "Binding: advisory — architecture"))
        p.write_text(t, encoding="utf-8")

    def _fill_verify_reported(self, slug):
        p = self._task_md(slug)
        t = re.sub(
            r"Reported: <yes — the gate report[^\n]*>",
            "Reported: yes — rendered before the outcome",
            p.read_text(encoding="utf-8"))
        p.write_text(t, encoding="utf-8")

    def _fill_all(self, slug):
        self._fill_deep(slug)
        self._fill_refute(slug)
        self._fill_advisor(slug)
        self._fill_verify_reported(slug)

    def _rollup_line(self, out):
        m = re.search(rf"{ROLLUP}[^\n]*", out)
        return m.group(0) if m else None


class RollupNoticeTest(_Harness):
    def test_rollup_fires_on_unfilled(self):                    # scenario 1
        self._verify_task("t")
        code, out = self._run("audit")
        self.assertIn(ROLLUP, out)
        line = self._rollup_line(out)
        self.assertIn("t", line)
        self.assertEqual(code, 0, "a notice, not a finding")

    def test_rollup_cleared_when_filled(self):                  # scenario 2
        self._verify_task("t")
        self._fill_all("t")
        _, out = self._run("audit")
        line = self._rollup_line(out)
        self.assertTrue(line is None or "t" not in line,
                        f"a fully-recorded §6 must clear the rollup:\n{out}")

    def test_slug_once_despite_multiple_unfilled(self):         # scenario 3 (dedupe)
        self._verify_task("zzq")                                # all four blocks unfilled
        _, out = self._run("audit")
        line = self._rollup_line(out)
        self.assertIsNotNone(line)
        self.assertEqual(line.count("zzq"), 1,
                         f"slug listed once in the rollup line despite 4 unfilled blocks:\n{line}")

    def test_one_grouped_line(self):                            # scenario 4
        for s in ("a", "b", "c"):
            self._verify_task(s)
        _, out = self._run("audit")
        self.assertEqual(out.count(ROLLUP), 1, "exactly ONE grouped rollup line")
        m = re.search(rf"{ROLLUP} — (\d+) task\(s\)[^\n]*", out)
        self.assertIsNotNone(m, f"a grouped 'N task(s)' line expected:\n{out}")
        self.assertEqual(int(m.group(1)), 3)

    def test_ground_task_not_listed(self):                      # scenario 5 (scope)
        self._silent("new-task", "g", "--title", "X")           # stays at ground
        _, out = self._run("audit")
        self.assertNotIn(ROLLUP, out)

    def test_member_codes_not_in_rollup_line(self):             # scenario 6 (pin safety)
        self._verify_task("t")
        _, out = self._run("audit")
        line = self._rollup_line(out)
        for code in MEMBER_CODES:
            self.assertNotIn(code, line,
                             f"rollup line must not repeat member token {code}:\n{line}")

    def test_rollup_after_per_code_lines(self):                 # scenario 7 (position)
        self._verify_task("t")
        _, out = self._run("audit")
        self.assertGreater(out.index(ROLLUP), out.index("refute_unrecorded"),
                           "rollup renders AFTER the per-code detail lines")


class JsonAndFindingTest(_Harness):
    def test_json_additive_key(self):                           # scenario 8
        self._verify_task("t")
        _, out = self._run("audit", "--json")
        data = json.loads(out)
        self.assertIn(ROLLUP, data["guarantee_lints"])
        self.assertIn("t", data["guarantee_lints"][ROLLUP])

    def test_never_a_finding(self):                             # scenario 9
        self._verify_task("t")
        code, out = self._run("audit", "--json")
        data = json.loads(out)
        finding_codes = [f["code"] for f in data.get("findings", [])]
        self.assertNotIn(ROLLUP, finding_codes, "the rollup is a glint, never a finding")
        self.assertEqual(code, 0)

    def test_existing_member_lists_unchanged(self):             # scenario 10 (additive)
        self._verify_task("t")
        _, out = self._run("audit", "--json")
        data = json.loads(out)
        for key in ("shallow", "refute_unrecorded",
                    "advisor_verdict_unrecorded", "verify_report_unrecorded"):
            self.assertIn(key, data["guarantee_lints"], "member keys stay")
            self.assertIn("t", data["guarantee_lints"][key])
        union = sorted(set(data["guarantee_lints"]["shallow"])
                       | set(data["guarantee_lints"]["refute_unrecorded"])
                       | set(data["guarantee_lints"]["advisor_verdict_unrecorded"])
                       | set(data["guarantee_lints"]["verify_report_unrecorded"]))
        self.assertEqual(data["guarantee_lints"][ROLLUP], union,
                         "rollup is exactly the members' union")


class GuideDisclosureTest(unittest.TestCase):
    def test_tests_guide_declares_expectations(self):           # scenario 11
        for p in (SKILL_TESTS_MD, DOGFOOD_TESTS_MD):
            text = p.read_text(encoding="utf-8")
            self.assertIn("Build expectations", text,
                          f"{p} must tell the tests phase to pre-declare §6 Build expectations")
            self.assertIn("before", text.split("Build expectations", 1)[1][:200].lower(),
                          f"{p} must say the block is filled BEFORE build")


if __name__ == "__main__":
    unittest.main()
