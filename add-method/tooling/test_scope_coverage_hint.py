#!/usr/bin/env python3
"""Red/green tests for the scope coverage hint (task scope-coverage-hint, frozen v1):
the WM1 re-cross repairs came from TOO-NARROW declarations — every token resolved
[ok] but the build touched §3 Touches paths outside them. The freeze echo now notes
each existing Touches path not covered by the resolved scope. Propose-not-impose;
never speculative (nonexistent paths stay silent); fail-open.

Run: python3 -m unittest test_scope_coverage_hint -v
"""
import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

_SEC3 = """### Grounding
Touches (files · symbols): pkg/api/handler.py:handle — covered · lib/util.py:helper — outside · ghost/nowhere.py:phantom — nonexistent
Anchors the contract cites: handle
Ground SHA: hand1234 — hand-grounded

### Contract

```
GET /w -> ok
```

`Least-sure flag surfaced at freeze:`
  ⚠ [contract] the shape is the least-sure part — cost if wrong: a reparse.
Status: DRAFT

### Build-strategy
Scope (may touch): `pkg/api/`
"""


class _Harness(unittest.TestCase):
    """A live board arranged through the real CLI (mirrors test_scope_echo_draft's
    harness — duplicated per this repo's one-harness-per-file norm)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-sch-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)

    def _ok(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        text = out.getvalue() + err.getvalue()
        self.assertEqual(code, 0, f"{argv} exited {code}: {text}")
        return text

    def _frozen_board(self, drop_scope_line: bool = False):
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        self._ok("new-task", "t", "--title", "T")
        self._ok("advance", "--to", "plan")
        (self.tmp / "pkg" / "api").mkdir(parents=True)
        (self.tmp / "pkg" / "api" / "handler.py").write_text("x = 1\n", encoding="utf-8")
        (self.tmp / "lib").mkdir()
        (self.tmp / "lib" / "util.py").write_text("y = 2\n", encoding="utf-8")
        p = self.tmp / ".add" / "tasks" / "t" / "PLAN.md"
        text = p.read_text(encoding="utf-8")
        sec3 = _SEC3
        if drop_scope_line:
            sec3 = "\n".join(ln for ln in sec3.splitlines()
                             if not ln.startswith("Scope (may touch):")) + "\n"
        new = re.sub(r"(?ms)(^### Contract.*?)(?=^---)", sec3 + "\n", text, count=1)
        self.assertNotEqual(new, text, "fixture §3 replacement failed")
        new = re.sub(r"(?m)^Boundary:.*$", "Boundary: none — no external input", new, count=1)
        p.write_text(new, encoding="utf-8")
        return self._ok("freeze", "--by", "Tester")


class CoverageHintTest(_Harness):
    def test_outside_path_noted(self):                             # M1 + Boundary
        out = self._frozen_board()
        self.assertIn("note: §3 Touches cites lib/util.py outside the declared scope", out)
        self.assertNotIn("handler.py outside", out,
                         "a covered Touches path must stay silent")

    def test_nonexistent_silent(self):                             # M2
        out = self._frozen_board()
        self.assertNotIn("ghost/nowhere.py", out,
                         "a nonexistent Touches path must never draw a note (not speculative)")

    def test_undeclared_branch_unchanged(self):                    # M2/R
        out = self._frozen_board(drop_scope_line=True)
        self.assertIn("scope: UNDECLARED (grandfathered)", out)
        self.assertIn("scope (proposed from §3 Touches):", out)
        self.assertNotIn("outside the declared scope", out,
                         "no coverage notes without a declaration to be outside of")

    def test_footer_stays_last(self):                              # R
        out = self._frozen_board()
        last = [ln for ln in out.splitlines() if ln.strip()][-1]
        self.assertTrue(last.startswith("next:"))


if __name__ == "__main__":
    unittest.main()
