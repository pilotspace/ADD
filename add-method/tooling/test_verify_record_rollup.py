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
  Guides: phases/direction.md (BOTH skill twins) instructs pre-declaring the §6 Build-expectations
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
SKILL_TESTS_MD = ADD_METHOD / "skill" / "add" / "phases" / "direction.md"
DOGFOOD_TESTS_MD = REPO / ".claude" / "skills" / "add" / "phases" / "direction.md"

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
            "<what read · what confirmed>", "read the diff in full · confirmed").replace(
            "(spec-dialect floor): <what confirmed>",
            "(spec-dialect floor): tests speak the spec's Z-timestamp example"),
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
