#!/usr/bin/env python3
"""scope-first-freeze (milestone wm1-lean-to-twelve) — fail-closed freeze on a zero-cover
Scope declaration + the root-relative template default + the task-dir teach note.

The 2026-07-23 WM1 re-measure lost 2-3 calls/rep to the scope-grammar death spiral: a
garbage/misresolved §3 Scope froze fine (echo warned, propose-not-impose), the build wrote
outside the phantom cover, scope_violation fired at the gate, and the agent paid re-cross +
gate again. The Scope line lives INSIDE frozen §3, so the ONLY cheap fix point is the freeze
itself: a declaration resolving to the EMPTY allowlist now refuses `scope_unresolved`
(validate-then-write — nothing persisted); UNDECLARED stays grandfathered; greenfield
[MISSING] tokens still freeze. The template default flips `./src/` -> `src/` (agents copy the
token shape they see — rep1/2 evidence) and a [MISSING] token under `.add/tasks/` gets a
teach note naming the `./…`=task-dir rule.

Run: cd add-method/tooling && python3 -m unittest test_scope_first_freeze -v
"""
from __future__ import annotations

import hashlib
import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

_TOOLING = Path(__file__).resolve().parent
_PKG = _TOOLING.parent
_REPO = _PKG.parent
TMPL_TWINS = (
    _PKG / "tooling" / "templates" / "PLAN.md.tmpl",
    _PKG / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "PLAN.md.tmpl",
    _REPO / ".add" / "tooling" / "templates" / "PLAN.md.tmpl",
    _PKG / ".add" / "tooling" / "templates" / "PLAN.md.tmpl",
)

_SEC3 = """### Grounding
Touches (files · symbols): pkg/api/handler.py:handle — the entrypoint
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
    """A live board arranged through the real CLI (mirrors test_scope_echo_draft's
    harness — duplicated per this repo's one-harness-per-file norm)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-sff-")).resolve()
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

    def _board(self, scope_line: str | None, keep_template_scope: bool = False):
        """init + a drafted task with the given Scope declaration (None = drop the line;
        keep_template_scope = leave the scaffolded template Scope line untouched)."""
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        self._ok("new-task", "t", "--title", "T")
        (self.tmp / "pkg" / "api").mkdir(parents=True)
        (self.tmp / "pkg" / "api" / "handler.py").write_text("x = 1\n", encoding="utf-8")
        p = self.tmp / ".add" / "tasks" / "t" / "PLAN.md"
        text = p.read_text(encoding="utf-8")
        sec3 = _SEC3
        if keep_template_scope:
            tmpl_scope = next(ln for ln in text.splitlines()
                              if ln.startswith("Scope (may touch):"))
            sec3 = sec3.replace("Scope (may touch): {scope}", tmpl_scope)
        elif scope_line is None:
            sec3 = "\n".join(ln for ln in sec3.splitlines()
                             if not ln.startswith("Scope (may touch):")) + "\n"
        else:
            sec3 = sec3.replace("{scope}", scope_line)
        new = re.sub(r"(?ms)(^### Contract.*?)(?=^---)", sec3 + "\n", text, count=1)
        self.assertNotEqual(new, text, "fixture §3 replacement failed")
        new = re.sub(r"(?m)^Boundary:.*$", "Boundary: none — no external input", new, count=1)
        p.write_text(new, encoding="utf-8")
        return p


class RefusalTest(_Harness):
    def test_garbage_scope_refused(self):                            # M1, R:refusal_wrote_state
        p = self._board("app/, tests/, pyproject.toml")              # UNBACKTICKED — the rep0 form
        out, code = self._run("freeze", "--by", "Tester")
        self.assertNotEqual(code, 0, "a zero-cover declaration must refuse the freeze")
        self.assertIn("scope_unresolved", out)
        self.assertIn("project root", out, "the refusal must teach the token grammar")
        self.assertFalse((self.tmp / ".add" / "tasks" / "t" / "scope-snapshot.json").exists(),
                         "validate-then-write: no sidecar on the refusal path")
        self.assertNotIn("FROZEN", p.read_text(encoding="utf-8"),
                         "validate-then-write: §3 must NOT freeze on the refusal path")

    def test_outside_root_refused(self):                             # M1
        self._board("`../outside/`")
        out, code = self._run("freeze", "--by", "Tester")
        self.assertNotEqual(code, 0, "outside-root-only tokens resolve to zero cover -> refuse")
        self.assertIn("scope_unresolved", out)


class GrandfatherTest(_Harness):
    def test_undeclared_grandfathered(self):                         # M2, R:grandfather_broken
        self._board(None)
        out = self._ok("freeze", "--by", "Tester")
        self.assertIn("scope: UNDECLARED (grandfathered)", out)

    def test_greenfield_missing_freezes(self):                       # M3, R:greenfield_refused
        self._board("`pkg/nope/`")
        out = self._ok("freeze", "--by", "Tester")
        self.assertRegex(out, r"(?m)^scope: pkg/nope/ \[MISSING\]$")

    def test_taskdir_missing_teach_note(self):                       # M4
        self._board("`./nope/`")
        out = self._ok("freeze", "--by", "Tester")
        self.assertIn("THIS TASK's dir", out,
                      "a [MISSING] token under .add/tasks/ must carry the task-dir teach note")
        self.assertIn("root-relative", out)


class TemplateDefault(unittest.TestCase):
    def test_template_default_root_relative(self):                   # M5
        text = TMPL_TWINS[0].read_text(encoding="utf-8")
        line = next(ln for ln in text.splitlines() if ln.startswith("Scope (may touch):"))
        self.assertIn("`src/`", line, "the Scope default must be the root-relative `src/`")
        self.assertNotIn("`./src/`", line, "the task-dir default shape taught the measured trap")
        self.assertIn("project root", line, "the hint must carry the grammar cue")
        present = [t for t in TMPL_TWINS if t.exists()]
        digests = {hashlib.md5(t.read_bytes()).hexdigest() for t in present}
        self.assertEqual(len(digests), 1, f"PLAN.md.tmpl twins must be byte-identical, got {digests}")


class DefaultWarn(_Harness):
    def test_untouched_default_warns(self):                          # M6
        self._board(None, keep_template_scope=True)
        out = self._ok("freeze", "--by", "Tester", "--cross")        # the warning lives at the tests->build crossing
        self.assertIn("still the template default", out,
                      "an untouched Scope default must warn at the crossing (repaired detection)")
        self.assertNotIn("scope: name/", out,
                         "the hint's grammar examples must NOT parse as phantom scope tokens")


class BuildPlanSkip(unittest.TestCase):
    def test_build_plan_skips_new_default(self):                     # M7
        raw3 = "### Build-strategy\nScope (may touch): `src/`   <HARD — fill before the freeze; x>\n"
        self.assertEqual(add._build_plan(raw3), [],
                         "the bare untouched `src/` default is a placeholder, not a plan")
        legacy = "### Build-strategy\nScope (may touch): `./src/`\n"
        self.assertEqual(add._build_plan(legacy), [], "the legacy `./src/` default stays skipped")
        real = "### Build-strategy\nScope (may touch): `src/` `tests/`\n"
        self.assertEqual(len(add._build_plan(real)), 1,
                         "a REAL multi-token declaration starting with src/ must surface")


if __name__ == "__main__":
    unittest.main(verbosity=2)
