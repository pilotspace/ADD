#!/usr/bin/env python3
"""Red/green tests for compound ticks (task compound-ticks, frozen v1): the oneshot
lane's 8-9 calls include two PURE ticks with no work between them (freeze->tests ·
build->verify->gate). Two OPT-IN compressions remove them: `freeze --cross` lands a
plan-phase freeze in tests, and a completing gate at the BUILD phase auto-crosses
build->verify before recording. Defaults stay byte-identical; refusals verbatim.

Run: python3 -m unittest test_compound_ticks -v
"""
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

_SEC3 = """### Grounding
Touches (files · symbols): pkg/api/handler.py:handle — the endpoint
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
    """A live board arranged through the real CLI (mirrors test_scope_coverage_hint's
    harness — duplicated per this repo's one-harness-per-file norm)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-cti-")).resolve()
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

    def _phase(self, slug="t"):
        state = json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))
        return state["tasks"][slug]["phase"]

    def _planned_board(self):
        """A oneshot task at the plan phase with a freezeable §3."""
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        self._ok("new-task", "t", "--title", "T", "--oneshot")
        self._ok("advance", "--to", "plan")
        p = self.tmp / ".add" / "tasks" / "t" / "TASK.md"
        text = p.read_text(encoding="utf-8")
        new = re.sub(r"(?ms)(^### Grounding.*?)(?=^---)", _SEC3 + "\n", text, count=1)
        self.assertNotEqual(new, text, "fixture §3 replacement failed")
        new = re.sub(r"(?m)^Boundary:.*$", "Boundary: none — no external input", new, count=1)
        p.write_text(new, encoding="utf-8")
        return p


class FreezeCrossTest(_Harness):
    def test_cross_lands_in_build(self):                           # M1 + Accept
        self._planned_board()
        out = self._ok("freeze", "--by", "Tester", "--cross")
        self.assertIn("froze §3 of t @ v1", out)
        self.assertIn("crossed into build", out)
        self.assertEqual(self._phase(), "build",
                         "--cross must land a direction-phase freeze in build")

    def test_bare_freeze_unchanged(self):                          # M1 (default)
        self._planned_board()
        out = self._ok("freeze", "--by", "Tester")
        self.assertNotIn("crossed", out, "the bare freeze must not cross")
        self.assertNotIn("--cross", out.replace("freeze --by", ""),
                         "the bare freeze output must not advertise the flag")
        self.assertEqual(self._phase(), "direction", "the bare freeze stays at direction")

    def test_cross_on_refused_freeze_no_crossing(self):            # R1
        self._planned_board()
        self._ok("freeze", "--by", "Tester")
        out = self._ok("freeze", "--by", "Tester", "--cross")      # benign no-op path
        self.assertIn("already frozen", out)
        self.assertNotIn("crossed", out,
                         "a freeze that did not stamp must never cross")
        self.assertEqual(self._phase(), "direction")

    def test_cross_nonbuild_note(self):                            # R2 + Boundary
        p = self._planned_board()
        self._ok("freeze", "--by", "Tester", "--cross")            # now at build
        text = p.read_text(encoding="utf-8")
        new = re.sub(r"(?m)^Status: FROZEN @ v1.*$", "Status: DRAFT", text, count=1)
        self.assertNotEqual(new, text, "change-request DRAFT flip failed")
        p.write_text(new, encoding="utf-8")
        out = self._ok("freeze", "--by", "Tester", "--cross")      # v2, phase != direction
        self.assertIn("froze §3 of t @ v2", out)
        self.assertIn("only a direction-phase freeze crosses", out)
        self.assertEqual(self._phase(), "build", "a non-direction --cross must not move the phase")


class GateFromBuildTest(_Harness):
    def test_gate_pass_from_build(self):                           # M2 + Accept
        self._planned_board()
        self._ok("freeze", "--by", "Tester")
        self._ok("phase", "build", "t")                            # the logged override
        out = self._ok("gate", "PASS", "t")
        self.assertIn("crossed build -> verify", out)
        self.assertEqual(self._phase(), "done",
                         "gate PASS from build must cross and record in one call")

    def test_gate_refused_before_build(self):                      # R3 (verbatim refusal)
        self._planned_board()
        self._ok("freeze", "--by", "Tester")                       # bare freeze — stays at direction
        out, code = self._run("gate", "PASS", "t")
        self.assertNotEqual(code, 0, "gate PASS before build must still refuse")
        self.assertIn("gate_pass_before_verify", out)
        self.assertNotIn("crossed", out)
        self.assertEqual(self._phase(), "direction")


class RecipeCrossTest(_Harness):
    def test_recipe_advertises_compressed_lane(self):              # M3
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        out = self._ok("new-task", "t", "--title", "T", "--oneshot")
        tail = out[out.lower().index("recipe"):]
        self.assertIn("--cross", tail, "the recipe must advertise freeze --cross")
        self.assertIn("gate PASS", tail)
        self.assertIn("from build", tail,
                       "the recipe must say the gate records from build")


if __name__ == "__main__":
    unittest.main()
