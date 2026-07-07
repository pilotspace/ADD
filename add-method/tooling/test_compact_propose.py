#!/usr/bin/env python3
"""Red/green tests for `add.py compact-foundation --propose` (task compact-propose,
milestone delta-drain, contract FROZEN @ v1).

A READ-ONLY preview verb for the compact-foundation.md ritual: per spec (PROJECT.md ·
CONVENTIONS.md) with >=1 live `[folded foundation-version N]` stamp it renders the
would-be settled line with the per-file fv range, then a footer naming the human
ritual. It NEVER writes; bare `compact-foundation` (no --propose) exits 2. The write
stays the human-confirmed ritual — this verb automates only the "propose" step.

Run: python3 -m unittest test_compact_propose -v
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

FOOTER = "read-only preview — the write stays the human-confirmed ritual (compact-foundation.md)"
NOTHING = "nothing to propose — no folded tail above the settled line"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class CompactProposeTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-compact-propose-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._run(["init", "--name", "demo"])
        self._run(["lock", "--force"])

    @staticmethod
    def _run(argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                add.main(argv)
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
        return out.getvalue(), err.getvalue(), code

    def _spec(self, name):
        return Path(self.tmp) / ".add" / name

    def _seed_folded(self, name, fvs):
        p = self._spec(name)
        text = p.read_text(encoding="utf-8")
        lines = "".join(f"- [folded foundation-version {n}] lesson {n} rolled\n" for n in fvs)
        p.write_text(text + "\n" + lines, encoding="utf-8")

    # ── M1 + Accept: per-spec propose line with the fv range + footer ────────────
    def test_propose_renders_range_and_footer(self):
        self._seed_folded("PROJECT.md", (3, 7))
        out, _, code = self._run(["compact-foundation", "--propose"])
        self.assertEqual(code, 0)
        self.assertIn("PROJECT.md : 2 folded line(s) (fv3-fv7) -> propose: "
                      "settled fv3-fv7 — <theme — draft at confirm> (see git)", out)
        self.assertEqual(out.rstrip().splitlines()[-1], FOOTER, "footer must be the last line")

    def test_both_specs_render_when_stamped(self):
        self._seed_folded("PROJECT.md", (2,))
        self._seed_folded("CONVENTIONS.md", (4, 5, 6))
        out, _, _ = self._run(["compact-foundation", "--propose"])
        self.assertIn("PROJECT.md : 1 folded line(s) (fv2-fv2)", out)
        self.assertIn("CONVENTIONS.md : 3 folded line(s) (fv4-fv6)", out)

    # ── M3: the verb NEVER writes ─────────────────────────────────────────────────
    def test_propose_writes_nothing(self):
        self._seed_folded("PROJECT.md", (3, 7))
        before = {n: _md5(self._spec(n)) for n in ("PROJECT.md", "CONVENTIONS.md")}
        self._run(["compact-foundation", "--propose"])
        after = {n: _md5(self._spec(n)) for n in ("PROJECT.md", "CONVENTIONS.md")}
        self.assertEqual(before, after, "compact-foundation --propose must be byte-read-only")

    # ── M4: zero stamps -> nothing to propose (exit 0) ────────────────────────────
    def test_zero_tail_message(self):
        out, _, code = self._run(["compact-foundation", "--propose"])
        self.assertEqual(code, 0)
        self.assertIn(NOTHING, out)
        self.assertNotIn("-> propose:", out)

    # ── R:propose_only — bare verb rejects, still no writes ──────────────────────
    def test_bare_verb_rejects_exit_2(self):
        self._seed_folded("PROJECT.md", (3,))
        before = _md5(self._spec("PROJECT.md"))
        _, err, code = self._run(["compact-foundation"])
        self.assertEqual(code, 2, "compact-foundation without --propose must exit 2")
        self.assertIn("--propose", err)
        self.assertIn("compact-foundation.md", err, "stderr must name the human ritual")
        self.assertEqual(_md5(self._spec("PROJECT.md")), before)

    # ── honest re-pin ─────────────────────────────────────────────────────────────
    def test_engine_repin_honest(self):
        digests = {_md5(p) for p in ADDPY_TRIO}
        self.assertEqual(len(digests), 1, "add.py trio diverged")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "ENGINE_MD5 must equal the BUILT add.py (re-pin honestly)")


if __name__ == "__main__":
    unittest.main()
