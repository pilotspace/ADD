#!/usr/bin/env python3
"""scope-walk-prune (milestone wm1-lean-to-twelve) — virtualenv/tooling dirs never read
as out-of-scope writes, and the untouched-Scope-default warning explains how it clears.

The 2026-07-23 re-measure #2 lost 3-5 calls in 3/3 reps to ONE deterministic trap: the
build made an in-workspace `.venv/`, `_scope_walk` snapshotted it (node_modules is pruned,
.venv was not), and the gate refused scope_violation on `.venv/bin/app-cli` — grep-the-
engine -> re-cross -> re-gate. The prune set gains the conventionally tool-owned names
only; `dist`/`build` stay WATCHED because they can be a project's real write-set. rep1
additionally re-crossed 3x trying to clear the untouched-default warning — the message
now says it is a note that clears only by editing the Scope line.

Run: cd add-method/tooling && python3 -m unittest test_scope_walk_prune -v
"""
from __future__ import annotations

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
Touches (files · symbols): src/app.py:main — the entrypoint
Anchors the contract cites: main
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
    """A live board arranged through the real CLI (mirrors test_scope_first_freeze's
    harness — duplicated per this repo's one-harness-per-file norm)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-swp-")).resolve()
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
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        self._ok("new-task", "t", "--title", "T")
        (self.tmp / "src").mkdir(exist_ok=True)
        (self.tmp / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
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

    def _make_venv_junk(self):
        for rel in (".venv/bin/app-cli", ".venv/lib/python3.12/site-packages/x.py"):
            f = self.tmp / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("junk\n", encoding="utf-8")


class WalkPrune(unittest.TestCase):
    def test_walk_prunes_venv_tree(self):                            # M1, M2
        tmp = Path(tempfile.mkdtemp(prefix="add-swp-walk-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        for rel in (".venv/bin/x", "venv/y", ".tox/z", ".mypy_cache/m",
                    ".ruff_cache/r", ".eggs/e", "src/app.py"):
            f = tmp / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("x\n", encoding="utf-8")
        keys = set(add._scope_walk(tmp))
        self.assertEqual(keys, {os.path.join("src", "app.py")},
                         f"tool-owned dirs must be pruned from the walk, got {keys}")

    def test_dist_build_not_pruned(self):                            # M5
        tmp = Path(tempfile.mkdtemp(prefix="add-swp-dist-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        for rel in ("dist/artifact.txt", "build/out.txt"):
            f = tmp / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("x\n", encoding="utf-8")
        keys = set(add._scope_walk(tmp))
        self.assertEqual(keys, {os.path.join("dist", "artifact.txt"),
                                os.path.join("build", "out.txt")},
                         "dist/build can be a REAL write-set — the gate must keep watching them")


class GateWithVenv(_Harness):
    def test_gate_clean_with_venv(self):                             # M3
        self._board("`src/`")
        self._ok("freeze", "--by", "Tester", "--cross")
        (self.tmp / "src" / "app.py").write_text("x = 2\n", encoding="utf-8")
        self._make_venv_junk()                                       # the 3/3-reps trap
        out = self._ok("gate", "PASS")
        self.assertNotIn("scope_violation", out,
                         "an in-workspace virtualenv must never trip the scope gate")

    def test_real_violation_still_caught(self):                      # M5, R:scope_violation
        self._board("`src/`")
        self._ok("freeze", "--by", "Tester", "--cross")
        (self.tmp / "src" / "app.py").write_text("x = 2\n", encoding="utf-8")
        self._make_venv_junk()
        (self.tmp / "rogue.py").write_text("bad\n", encoding="utf-8")
        out, code = self._run("gate", "PASS")
        self.assertNotEqual(code, 0, "a REAL out-of-cover write must still fail the gate")
        self.assertIn("scope_violation", out)
        self.assertIn("rogue.py", out)
        self.assertNotIn(".venv", out, "the refusal must name real writes, never pruned junk")


class WarnSelfExplains(_Harness):
    def test_warn_self_explains(self):                               # M4
        self._board(None, keep_template_scope=True)
        out = self._ok("freeze", "--by", "Tester", "--cross")
        self.assertIn("still the template default", out)
        self.assertIn("not a blocker", out,
                      "the warn must say it is a note, not a gate")
        self.assertIn("re-cross does not clear it", out,
                      "rep1 re-crossed 3x trying to clear the warn — the message must forbid that path")


if __name__ == "__main__":
    unittest.main(verbosity=2)
