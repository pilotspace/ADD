#!/usr/bin/env python3
"""Red/green tests for build-entry-spec-echo (six-phase-loop 6/6, frozen v1): the
tick INTO build re-renders WHAT to build — §1 Must/Reject bullet first-lines +
the frozen §3 contract-fence head — via a NEW pure-read `_spec_echo` helper
called fail-open at the TAIL of `_build_entry`, so BOTH entries (`advance`
tests->build AND the `phase build` override) echo, a refused entry never does,
and an echo failure never blocks the tick.

Run: python3 -m unittest test_build_entry_spec_echo -v
"""
import hashlib
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

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parent
REPO_ROOT = PKG_ROOT.parent

_SEC1 = """Feature: fixture feature
Must:
  - first must behavior
    continuation detail that must NOT echo as its own line
  - second must behavior
Reject:
  - bad input shape -> "err_bad_shape"
Accept: Given x When y Then z
"""

_SEC3 = """### Contract

```
do_thing(x) -> Result   FIXTURE-CONTRACT-HEAD
fields: a - b
```

Status: DRAFT
"""


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-bese-")).resolve()
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

    def _board(self):
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        self._ok("new-task", "t", "--title", "T", "--oneshot")

    def _task_md(self, slug="t"):
        return self.tmp / ".add" / "tasks" / slug / "PLAN.md"

    def _fill_spec(self, slug="t", sec1=_SEC1, sec3=_SEC3):
        """Replace §1 and §3 bodies wholesale with known fixture content."""
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        text = re.sub(r"(?s)(^## 1 ·[^\n]*\n).*?(?=^## )",
                      lambda m: m.group(1) + sec1 + "\n", text, count=1, flags=re.M)
        text = re.sub(r"(?s)(^## 3 ·[^\n]*\n).*?(?=^## )",
                      lambda m: m.group(1) + sec3 + "\n", text, count=1, flags=re.M)
        p.write_text(text, encoding="utf-8")

    def _freeze(self, slug="t"):
        p = self._task_md(slug)
        p.write_text(p.read_text(encoding="utf-8").replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-07-14.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _phase(self, slug="t"):
        state = json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))
        return state["tasks"][slug]["phase"]

    def _at_direction_frozen(self):
        """Fill + freeze t's fixture §3 — a fresh task is BORN at `direction`
        (phase-collapse-3), primed for the ONE direction->build crossing."""
        self._fill_spec()
        self._freeze()


class EchoAtAdvanceTest(_Harness):
    def test_advance_into_build_echoes_spec(self):                 # M1 + M2 + Accept
        self._board()
        self._at_direction_frozen()
        out = self._ok("advance", "t")                             # direction -> build: the tick
        self.assertEqual(self._phase(), "build")
        self.assertIn("build to (frozen plan):", out)
        self.assertIn("must: first must behavior", out)
        self.assertIn("must: second must behavior", out)
        self.assertIn('reject: bad input shape -> "err_bad_shape"', out)
        self.assertIn("contract: do_thing(x) -> Result   FIXTURE-CONTRACT-HEAD", out)
        self.assertNotIn("continuation detail", out,
                         "only a bullet's FIRST line echoes")

    def test_echo_lines_render_in_order(self):                     # M1 (shape: header, must, reject, contract)
        self._board()
        self._at_direction_frozen()
        out = self._ok("advance", "t")
        idx = [out.index("build to (frozen plan):"),
               out.index("must: first must behavior"),
               out.index('reject: bad input shape'),
               out.index("contract: do_thing")]
        self.assertEqual(idx, sorted(idx),
                         "echo must render header -> must -> reject -> contract, in order")


class EchoAtPhaseOverrideTest(_Harness):
    def test_phase_build_override_echoes_too(self):                # M2 (both entries funnel through _build_entry)
        self._board()
        self._fill_spec()
        self._freeze()
        out = self._ok("phase", "build", "t")
        self.assertEqual(self._phase(), "build")
        self.assertIn("build to (frozen plan):", out)
        self.assertIn("must: first must behavior", out)
        self.assertIn("contract: do_thing(x) -> Result   FIXTURE-CONTRACT-HEAD", out)


class FailOpenTest(_Harness):
    def test_helper_raise_never_blocks_the_tick(self):             # M3 + R1 (least-sure flag's behavioral form)
        self._board()
        self._at_direction_frozen()
        real = add._spec_echo

        def _boom(*a, **k):
            raise RuntimeError("forced echo failure")

        add._spec_echo = _boom
        self.addCleanup(setattr, add, "_spec_echo", real)
        out, code = self._run("advance", "t")
        self.assertEqual(code, 0,
                         f"a raising echo must never block the build entry: {out}")
        self.assertEqual(self._phase(), "build")
        state = json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))
        self.assertIn("tripwire", state["tasks"]["t"],
                      "the gate stack's own writes must land exactly as before")
        self.assertNotIn("Traceback", out)

    def test_malformed_sections_partial_echo_no_crash(self):       # Boundary (missing Must/Reject + no fence)
        self._board()
        self._fill_spec(sec1="Feature: bare fixture, no rule blocks\n",
                        sec3="### Contract\n\nno fence here at all\n\nStatus: DRAFT\n")
        self._freeze()
        out = self._ok("phase", "build", "t")                      # tick completes
        self.assertEqual(self._phase(), "build")
        self.assertNotIn("must:", out)
        self.assertNotIn("contract: ", out)
        self.assertNotIn("Traceback", out)


class GuardsPrecedeEchoTest(_Harness):
    def test_refused_crossing_never_echoes(self):                  # R2 (validate-then-write)
        self._board()
        self._fill_spec()                                          # §3 stays DRAFT
        out, code = self._run("phase", "build", "t")
        self.assertNotEqual(code, 0)
        self.assertIn("contract_not_frozen", out)
        self.assertNotIn("build to (frozen plan):", out,
                         "a refused entry must not echo")

    def test_skip_freeze_draft_crossing_still_echoes(self):        # Boundary (--skip-freeze DRAFT §3)
        self._board()
        self._fill_spec()                                          # §3 stays DRAFT
        out = self._ok("phase", "build", "t", "--skip-freeze")
        self.assertEqual(self._phase(), "build")
        self.assertIn("must: first must behavior", out,
                      "the echo renders whatever exists, even on a recorded-skip crossing")


class PurityAndParityTest(_Harness):
    def test_spec_echo_is_a_pure_read(self):                       # M3 (never writes)
        self._board()
        self._fill_spec()
        self._freeze()
        before_md = self._task_md().read_bytes()
        before_state = (self.tmp / ".add" / "state.json").read_bytes()
        out, err = io.StringIO(), io.StringIO()
        root = self.tmp / ".add"
        with redirect_stdout(out), redirect_stderr(err):
            add._spec_echo(root, "t")
        self.assertEqual(self._task_md().read_bytes(), before_md)
        self.assertEqual((self.tmp / ".add" / "state.json").read_bytes(), before_state)
        self.assertIn("must: first must behavior", out.getvalue())

    def test_engine_twins_carry_the_echo(self):                    # sync x3 (twin parity on add.py)
        canon = hashlib.md5((PKG_ROOT / "tooling" / "add.py").read_bytes()).hexdigest()
        # the git-TRACKED twin binds unconditionally; the two dogfood twins are
        # gitignored and absent on a fresh checkout — exists()-skip tolerance
        # (fresh-checkout precedent ba09498; gitignored-twins lesson, facets milestone)
        bundled = PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "add.py"
        self.assertEqual(hashlib.md5(bundled.read_bytes()).hexdigest(), canon,
                         f"engine twin drifted: {bundled}")
        for twin in (REPO_ROOT / ".add" / "tooling" / "add.py",
                     PKG_ROOT / ".add" / "tooling" / "add.py"):
            if not twin.exists():
                continue
            self.assertEqual(hashlib.md5(twin.read_bytes()).hexdigest(), canon,
                             f"engine twin drifted: {twin}")


if __name__ == "__main__":
    unittest.main()
