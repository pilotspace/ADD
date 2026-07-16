"""fastlane-ground-lite (method-ergonomics): the fast lane's §0 carries the drift anchor.

CONTRACT — supersedes ground-anchor-sha's "fast lane omits it" scope note (recorded change).
template-unify migration: the fast lane is now a derived render of the ONE TASK.md.tmpl,
so the field pins point at that template + the shared _FALLBACK_TASK:
  templates/TASK.md.tmpl §3 Grounding carries the `Ground SHA:` line (all template trees);
  _FALLBACK_TASK carries the same field (circuit-breaker parity of the FIELD, not bytes);
  a scaffolded `new-task --fast` TASK.md contains it;
  behavior unchanged: check WARNs on a §0 citing l.NNN with a placeholder SHA, silent when filled
  (the field exists so a fast task can actually clear the WARN without hand-adding the line).
Run: python3 -m unittest test_fastlane_ground_lite -v
"""
import contextlib
import io
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import add
from add_engine.constants import _FALLBACK_TASK

TOOLING = Path(add.__file__).resolve().parent
ADD_METHOD = TOOLING.parent
REPO = ADD_METHOD.parent
FAST_TREES = (
    TOOLING / "templates" / "TASK.md.tmpl",
    REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
    ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.md.tmpl",
)


def _ground_block(text: str) -> str:
    return add._ground_section(text)


class TemplateFieldTest(unittest.TestCase):
    def test_fast_template_has_ground_sha_3trees(self):          # scenario 1
        for p in FAST_TREES:
            self.assertIn("Ground SHA:", _ground_block(p.read_text(encoding="utf-8")),
                          f"{p} §3 Grounding must carry the Ground SHA drift anchor")

    def test_fallback_has_ground_sha(self):                      # scenario 2
        self.assertIn("Ground SHA:", _ground_block(_FALLBACK_TASK),
                      "_FALLBACK_TASK §3 must carry the field (circuit-breaker parity)")


class ScaffoldAndBehaviorTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-fgl-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("lock", "--force")
        self._silent("new-task", "t", "--fast", "--title", "F")
        self.md = self.tmp / ".add" / "tasks" / "t" / "TASK.md"   # fast renders into TASK.md

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

    def _check_out(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            try:
                add.main(["check"])
            except SystemExit:
                pass
        return buf.getvalue()

    def test_scaffold_contains_field(self):                      # scenario 3
        self.assertIn("Ground SHA:", _ground_block(self.md.read_text(encoding="utf-8")))

    # template-touches-scope-dedup: match the Touches line by label + any <…> placeholder
    # (the dedup reworded the placeholder value), so these stay green across future rewords.
    _TOUCHES_PLACEHOLDER = re.compile(r"Touches \(files · symbols[^)]*\): <[^\n]*>")
    _TOUCHES_LINEREF = "Touches (files · symbols): add.py l.42 — the audit printer"

    def test_warn_fires_on_lineref_placeholder_sha(self):        # scenario 4
        t = self._TOUCHES_PLACEHOLDER.sub(
            self._TOUCHES_LINEREF, self.md.read_text(encoding="utf-8"))
        self.md.write_text(t, encoding="utf-8")
        self.assertIn("cites line numbers", self._check_out())

    def test_warn_clears_when_sha_filled(self):                  # scenario 5
        t = self._TOUCHES_PLACEHOLDER.sub(
            self._TOUCHES_LINEREF, self.md.read_text(encoding="utf-8"))
        t = re.sub(r"Ground SHA: <[^>\n]*>", "Ground SHA: abc1234", t)
        self.md.write_text(t, encoding="utf-8")
        self.assertNotIn("cites line numbers", self._check_out())


if __name__ == "__main__":
    unittest.main()
