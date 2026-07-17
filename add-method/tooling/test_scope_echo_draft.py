#!/usr/bin/env python3
"""Red/green tests for scope echo + draft at freeze (task scope-echo-draft, frozen v1):
the scope-token-grammar seam's mis-resolution class (SEAMS.md: 3 tasks independently
rediscovered it) becomes a zero-call READ at the approval already happening — freeze
echoes each resolved scope entry, and proposes a Scope line from §3 Touches when the
declaration is absent/default/garbage. Propose-not-impose; pure read; fail-open.

  M1 — a real directory token echoes `scope: <rel> [ok]`.
  M2 — a token no tree provides echoes `[MISSING]` (the `./src/` default is REAL —
       new-task scaffolds a task-local src/, an honest ground correction).
  M3 — default/dead scope + real Touches paths -> `scope (proposed from §3 Touches):`
       with backticked root-relative tokens; the PLAN.md Scope line byte-identical.
  M4 — no Scope line at all -> UNDECLARED (grandfathered) + proposal, no MISSING noise.
  R1 — the next-footer stays the LAST stdout line (kickoff-truth's footer convention).
  R2 — the already-frozen no-op (exit 0, nothing re-stamped) prints no `scope:` lines.

One test per §1 Must/Reject. Run: python3 -m unittest test_scope_echo_draft -v
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
Touches (files · symbols): pkg/api/handler.py:handle — the entrypoint · pkg/api/router.py:route
Anchors the contract cites: handle
Ground SHA: hand1234 — hand-grounded

### Contract

```
GET /w -> { ok: true }
```

`Least-sure flag surfaced at freeze:`
  ⚠ [contract] the shape is the least-sure part — cost if wrong: a reparse.
Status: DRAFT

### Build-strategy
Scope (may touch): {scope}
"""


class _Harness(unittest.TestCase):
    """A live board arranged through the real CLI (mirrors test_derived_stamps'
    harness — duplicated per this repo's one-harness-per-file norm)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-sed-")).resolve()
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

    def _board(self, scope_line: str | None):
        """init + a drafted oneshot task at plan with the given Scope declaration
        (None drops the whole Scope line — the UNDECLARED grandfather)."""
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        self._ok("new-task", "t", "--title", "T", "--oneshot")
        self._ok("advance", "--to", "plan")
        # real files so Touches paths + a real scope dir resolve
        (self.tmp / "pkg" / "api").mkdir(parents=True)
        (self.tmp / "pkg" / "api" / "handler.py").write_text("x = 1\n", encoding="utf-8")
        p = self.tmp / ".add" / "tasks" / "t" / "PLAN.md"
        text = p.read_text(encoding="utf-8")
        sec3 = _SEC3
        if scope_line is None:
            sec3 = "\n".join(ln for ln in sec3.splitlines()
                             if not ln.startswith("Scope (may touch):")) + "\n"
        else:
            sec3 = sec3.replace("{scope}", scope_line)
        new = re.sub(r"(?ms)(^### Grounding.*?)(?=^---)", sec3 + "\n", text, count=1)
        self.assertNotEqual(new, text, "fixture §3 replacement failed")
        new = re.sub(r"(?m)^Boundary:.*$", "Boundary: none — no external input", new, count=1)
        p.write_text(new, encoding="utf-8")
        return p


class EchoTest(_Harness):
    def test_echo_ok(self):                                        # M1
        self._board("`pkg/api/`")
        out = self._ok("freeze", "--by", "Tester")
        self.assertRegex(out, r"(?m)^scope: pkg/api/ \[ok\]$")

    def test_echo_missing_token(self):                             # M2
        # NOTE: the `./src/` template default resolves [ok] — new-task scaffolds a real
        # task-local src/. A dead declaration is a token no tree provides:
        self._board("`pkg/nope/`")
        out = self._ok("freeze", "--by", "Tester")
        self.assertRegex(out, r"(?m)^scope: pkg/nope/ \[MISSING\]$")


class ProposalTest(_Harness):
    def test_proposal_from_touches(self):                          # M3
        p = self._board("`pkg/nope/`")
        before = re.search(r"(?m)^Scope \(may touch\):.*$",
                           p.read_text(encoding="utf-8")).group(0)
        out = self._ok("freeze", "--by", "Tester")
        self.assertIn("scope (proposed from §3 Touches):", out)
        self.assertIn("`pkg/api/handler.py`", out)
        after = re.search(r"(?m)^Scope \(may touch\):.*$",
                          p.read_text(encoding="utf-8")).group(0)
        self.assertEqual(before, after,
                         "propose-not-impose: the Scope line must stay byte-identical")

    def test_undeclared_grandfather(self):                         # M4
        self._board(None)
        out = self._ok("freeze", "--by", "Tester")
        self.assertIn("scope: UNDECLARED (grandfathered)", out)
        self.assertIn("scope (proposed from §3 Touches):", out)
        self.assertNotIn("[MISSING]", out,
                         "an UNDECLARED task has no tokens to mark MISSING")


class GuardTest(_Harness):
    def test_footer_stays_last(self):                              # R1
        self._board("`pkg/api/`")
        out = self._ok("freeze", "--by", "Tester")
        last = [ln for ln in out.splitlines() if ln.strip()][-1]
        self.assertTrue(last.startswith("next:"),
                        f"the next-footer must stay the last line, got: {last!r}")

    def test_reject_path_no_echo(self):                            # R2
        self._board("`pkg/api/`")
        self._ok("freeze", "--by", "Tester")
        out = self._ok("freeze", "--by", "Tester")                 # already-frozen no-op
        self.assertIn("already frozen", out)
        self.assertNotIn("scope:", out,
                         "the no-op path must print no echo (nothing was re-stamped)")


if __name__ == "__main__":
    unittest.main()
