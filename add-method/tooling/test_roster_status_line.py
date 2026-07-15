#!/usr/bin/env python3
"""Red/green tests for the engine-rendered persona roster (task roster-status-line,
milestone delta-drain, contract FROZEN @ v1).

With >=1 REAL persona seeded, `add.py status` renders a `personas:` header plus one
line per persona — `  - <slug> [<flow|?>] — <vibe, truncated to 70 chars>` — a pure
frontmatter read so agents stop whole-roster body reads. `add.py check` renders ONE
INFO row: `roster: <slug>[<flow>] · …` (vibe elided — check is a linter). Zero real
personas -> both outputs byte-identical to today. Fail-soft: a frontmatter-less file
degrades to `[?]`, never raises. Advisory — never a WARN, never a gate.

Run: python3 -m unittest test_roster_status_line -v
"""
import contextlib
import hashlib
import io
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import add
import engine_pin

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"
ADDPY_TRIO = (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
              BUNDLE / "tooling" / "add.py")

PERSONA = """---
name: AA Test
vibe: {vibe}
flow: {flow}
use-when: testing
not-when: production
---

## Identity
x
"""


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class RosterStatusLineTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-roster-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._run(["init", "--name", "demo"])
        self._run(["lock", "--force"])
        self.pdir = Path(self.tmp) / ".add" / "personas"
        self.pdir.mkdir(exist_ok=True)

    @staticmethod
    def _run(argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                add.main(argv)
            except SystemExit:
                pass
        return out.getvalue()

    def _seed(self, slug="aa-test", vibe="Trust evidence, not inspection.", flow="verify, advisor"):
        (self.pdir / f"{slug}.md").write_text(PERSONA.format(vibe=vibe, flow=flow),
                                              encoding="utf-8")

    # ── M1 + Accept: status renders slug · flow · vibe ────────────────────────────
    def test_status_renders_roster(self):
        self._seed()
        out = self._run(["status", "--all"])   # roster body gates behind --all (status-lean-default)
        self.assertIn("personas:", out)
        self.assertIn("- aa-test [verify, advisor] — Trust evidence, not inspection.", out)

    def test_roster_sorted_by_slug(self):
        self._seed("zz-late", flow="build")
        self._seed("aa-early", flow="design")
        out = self._run(["status", "--all"])   # roster body: --all
        self.assertLess(out.index("aa-early"), out.index("zz-late"), "roster must sort by slug")

    # ── M2: check renders one INFO roster row ─────────────────────────────────────
    def test_check_renders_roster_row(self):
        self._seed()
        out = self._run(["check"])
        self.assertIn("roster: aa-test[verify, advisor]", out)

    # ── M3: zero real personas -> byte-identical output ───────────────────────────
    def test_no_persona_no_roster(self):
        out = self._run(["status"])
        self.assertNotIn("personas:", out, "a persona-less project must render no roster")
        self.assertNotIn("roster:", self._run(["check"]))

    # ── M4: fail-soft — frontmatter-less file degrades to [?] ─────────────────────
    def test_frontmatterless_degrades(self):
        (self.pdir / "bare.md").write_text("just prose, no frontmatter\n", encoding="utf-8")
        out = self._run(["status", "--all"])   # roster body: --all
        self.assertIn("- bare [?] —", out, "a parse miss must degrade to '?', not raise")

    # ── M5: vibe truncation at 70 ─────────────────────────────────────────────────
    def test_vibe_truncated_to_70(self):
        self._seed(vibe="v" * 100, flow="build")
        line = next(ln for ln in self._run(["status", "--all"]).splitlines() if "- aa-test" in ln)   # roster body: --all
        self.assertIn("v" * 70 + "…", line)
        self.assertNotIn("v" * 71, line)

    # ── honest re-pin ─────────────────────────────────────────────────────────────
    def test_engine_repin_honest(self):
        digests = {_md5(p) for p in ADDPY_TRIO}
        self.assertEqual(len(digests), 1, "add.py trio diverged")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "ENGINE_MD5 must equal the BUILT add.py (re-pin honestly)")


if __name__ == "__main__":
    unittest.main()
