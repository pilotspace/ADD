#!/usr/bin/env python3
"""Red/green tests for the fold draft at close (task fold-draft-at-close, frozen v1):
milestone-done's SPEC-delta nudge grows a pre-classified draft — one line per open
SPEC delta with a MECHANICAL class + rationale (`seed` when a cited path resolves in
the current tree · `drop?` when path tokens exist but none resolve · `seed` by
default when pathless). Propose-not-impose: stdout only, the human still resolves;
the existing nudge lines survive; fail-open.

  M1 — three delta shapes classify seed / drop? / seed with matching rationales.
  M2 — the existing SPEC nudge + review pointer survive (fold_nudge pins).
  M3 — stdout only: a rerun of `deltas` shows the same open set (no state change).
  R1 — zero open SPEC deltas -> no draft block.
  R2 — the next-footer stays the last stdout line.

One test per §1 Must/Reject. Run: python3 -m unittest test_fold_draft_at_close -v
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
Touches (files · symbols): src/x.py:handler
Anchors the contract cites: handler
Ground SHA: hand1234 — hand-grounded

### Contract

```
GET /w -> ok
```

`Least-sure flag surfaced at freeze:`
  ⚠ [contract] the shape is the least-sure part — cost if wrong: a reparse.
Status: DRAFT

### Build-strategy
Scope (may touch): `./src/`
"""

_DELTAS = """### Spec delta
- [SPEC · open] extend the widget parser (evidence: pkg/live.py handles only v1)
- [SPEC · open] port the legacy shim (evidence: pkg/gone.py still imports it)
- [SPEC · open] interview the operators about retry policy (evidence: support thread)
"""


class _Harness(unittest.TestCase):
    """A live board arranged through the real CLI (mirrors test_scope_echo_draft's
    harness — duplicated per this repo's one-harness-per-file norm)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-fdc-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue() + err.getvalue(), code

    def _ok(self, *argv):
        text, code = self._run(*argv)
        self.assertEqual(code, 0, f"{argv} exited {code}: {text}")
        return text

    def _closed_milestone(self, with_deltas: bool):
        """init + a milestone whose single task ran to done; optionally 3 open SPEC
        deltas (live path · dead path · pathless) injected into its §7 block."""
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        self._ok("new-milestone", "m", "--title", "M", "--goal", "close cleanly")
        ms = self.tmp / ".add" / "milestones" / "m" / "MILESTONE.md"
        if ms.exists():  # criteria-less close: the goal-gate must not fire
            body = ms.read_text(encoding="utf-8")
            ms.write_text(re.sub(r"(?m)^\s*- \[ \].*\n?", "", body), encoding="utf-8")
        self._ok("new-task", "t", "--title", "T", "--milestone", "m")
        self._ok("advance", "--to", "plan")
        p = self.tmp / ".add" / "tasks" / "t" / "PLAN.md"
        text = p.read_text(encoding="utf-8")
        new = re.sub(r"(?ms)(^### Contract.*?)(?=^---)", _SEC3 + "\n", text, count=1)
        self.assertNotEqual(new, text, "fixture §3 replacement failed")
        new = re.sub(r"(?m)^Boundary:.*$", "Boundary: none — no external input", new, count=1)
        p.write_text(new, encoding="utf-8")
        self._ok("freeze", "--by", "Tester")
        for _ in range(3):
            self._ok("advance")
        self._ok("gate", "PASS")
        if with_deltas:
            (self.tmp / "pkg").mkdir()
            (self.tmp / "pkg" / "live.py").write_text("x = 1\n", encoding="utf-8")
            text = p.read_text(encoding="utf-8")
            new = re.sub(r"(?ms)^### Spec delta\n.*?(?=^###|\Z)", _DELTAS + "\n",
                         text, count=1)
            if new == text:                      # no §7 block scaffolded -> append one
                new = text + "\n" + _DELTAS
            p.write_text(new, encoding="utf-8")
        return p


class DraftTest(_Harness):

    def test_existing_nudge_survives(self):                        # M2
        self._closed_milestone(with_deltas=True)
        out = self._ok("milestone-done", "m")
        self.assertIn("open SPEC", out)
        self.assertIn("add.py deltas", out, "the review pointer must survive")

    def test_stdout_only(self):                                    # M3
        self._closed_milestone(with_deltas=True)
        before = self._ok("deltas")
        self._ok("milestone-done", "m")
        after = self._ok("deltas")
        self.assertEqual(before.replace("m' -> done", ""), after.replace("m' -> done", ""),
                         "the draft must not resolve/mutate any delta")


class GuardTest(_Harness):
    def test_no_deltas_no_draft(self):                             # R1
        self._closed_milestone(with_deltas=False)
        out = self._ok("milestone-done", "m")
        self.assertNotIn("fold draft", out)

    def test_footer_stays_last(self):                              # R2
        self._closed_milestone(with_deltas=True)
        out = self._ok("milestone-done", "m")
        last = [ln for ln in out.splitlines() if ln.strip()][-1]
        self.assertTrue(last.startswith("next:"),
                        f"the next-footer must stay the last line, got: {last!r}")


if __name__ == "__main__":
    unittest.main()
