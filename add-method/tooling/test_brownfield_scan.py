#!/usr/bin/env python3
"""Behavioral proof of brownfield detection in cmd_init (task: brownfield-scan, v12).

CONTRACT (frozen @ v1):
  - `_is_brownfield(base)` is True iff base holds a child whose name is NOT in
    _INIT_EXCLUDE = {.add, AGENTS.md, CLAUDE.md, .git} (False on empty/missing base).
  - cmd_init, after scaffolding, prints a STABLE "brownfield:"-prefixed signal on a brownfield
    base and the existing greenfield closing (byte-for-byte) otherwise. init never refuses.
  - The engine only DETECTS + SIGNALS; reading code / filling survivors is the AI's job (adopt.md).

The adopt.md guide is prose: its byte-parity is asserted by test_tree_parity + test_bundle_parity,
not here (TDD binds where there is code). One test per code scenario.
Run: python3 -m unittest test_brownfield_scan -v
"""
import contextlib
import io
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add

_GREENFIELD_MARK = "say what you want to build"   # unique to the greenfield closing
_BROWNFIELD_MARK = "brownfield:"                   # first token of the brownfield signal


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class BrownfieldScanTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-brownfield-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self._cwd)

    # --- the predicate -------------------------------------------------------
    def test_is_brownfield_predicate(self):
        base = Path(self.tmp)
        self.assertFalse(add._is_brownfield(base), "empty base is greenfield")
        (base / ".add").mkdir()
        (base / "AGENTS.md").write_text("x", encoding="utf-8")
        (base / "CLAUDE.md").write_text("x", encoding="utf-8")
        self.assertFalse(add._is_brownfield(base), "only the tool's own files -> greenfield")
        (base / "main.py").write_text("print('hi')\n", encoding="utf-8")
        self.assertTrue(add._is_brownfield(base), "prior source content -> brownfield")

    # --- scenarios -----------------------------------------------------------
    def test_brownfield_dir_emits_signal(self):
        Path(self.tmp, "main.py").write_text("print('hi')\n", encoding="utf-8")
        code, out, _ = _run(["init", "--name", "demo"])
        self.assertEqual(code, 0)
        self.assertIn(_BROWNFIELD_MARK, out)
        self.assertNotIn(_GREENFIELD_MARK, out, "brownfield must replace the greenfield closing")

    def test_greenfield_dir_unchanged(self):
        code, out, _ = _run(["init", "--name", "demo"])
        self.assertEqual(code, 0)
        self.assertNotIn(_BROWNFIELD_MARK, out)
        self.assertIn(_GREENFIELD_MARK, out, "empty base keeps the greenfield closing")

    def test_excluded_only_not_brownfield(self):
        _run(["init", "--name", "demo"])                 # scaffolds .add/, AGENTS.md, CLAUDE.md
        code, out, _ = _run(["init", "--name", "demo", "--force"])   # only excluded files remain
        self.assertEqual(code, 0)
        self.assertNotIn(_BROWNFIELD_MARK, out, "re-init of the tool's own files is not brownfield")

    def test_survivor_never_clobbered_on_reinit(self):
        _run(["init", "--name", "demo"])
        pj = Path(self.tmp, ".add", "PROJECT.md")
        pj.write_text("SENTINEL — hand edited\n", encoding="utf-8")
        _run(["init", "--name", "demo", "--force"])      # --force resets state, must NOT touch survivors
        self.assertEqual(pj.read_text(encoding="utf-8"), "SENTINEL — hand edited\n")

    # --- integration: the entry adopt.md prescribes -------------------------
    def test_brownfield_await_lock_arms_gate_then_lock_succeeds(self):
        """adopt.md tells brownfield onboarding to enter with `init --await-lock`:
        it must BOTH emit the brownfield signal AND seed an unlocked setup, so the
        closing `lock` succeeds (a plain init would be grandfathered-locked -> already_locked)."""
        Path(self.tmp, "main.py").write_text("print('hi')\n", encoding="utf-8")
        code, out, _ = _run(["init", "--name", "demo", "--await-lock"])
        self.assertEqual(code, 0)
        self.assertIn(_BROWNFIELD_MARK, out, "init --await-lock still emits the brownfield signal")
        state = json.loads(Path(self.tmp, ".add", "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["setup"]["locked"], False, "--await-lock seeds an unlocked setup (gate armed)")
        # the guide's closing command must succeed on this seeded setup
        lock_code, _, lock_err = _run(["lock", "--by", "Tester"])
        self.assertEqual(lock_code, 0, f"lock must succeed on an --await-lock setup, got: {lock_err}")
        relocked = json.loads(Path(self.tmp, ".add", "state.json").read_text(encoding="utf-8"))
        self.assertEqual(relocked["setup"]["locked"], True, "lock flips the seeded setup to locked")

    # --- _INIT_EXCLUDE boundary (change-request v2): boilerplate is not code ---
    def test_boilerplate_only_is_greenfield(self):
        """A repo holding ONLY license + VCS/CI/editor scaffolding carries no domain
        signal -> it must read greenfield (no false brownfield positive)."""
        for name in ("LICENSE", ".gitignore", ".gitattributes", ".editorconfig"):
            Path(self.tmp, name).write_text("boilerplate\n", encoding="utf-8")
        Path(self.tmp, ".github").mkdir()
        code, out, _ = _run(["init", "--name", "demo"])
        self.assertEqual(code, 0)
        self.assertNotIn(_BROWNFIELD_MARK, out, "license + CI/editor scaffolding alone is not brownfield")
        self.assertIn(_GREENFIELD_MARK, out, "boilerplate-only base keeps the greenfield closing")

    def test_readme_still_triggers_brownfield(self):
        """A README carries domain content (adopt.md reads it for PROJECT.md) ->
        it MUST keep triggering brownfield even alongside excluded boilerplate."""
        Path(self.tmp, "LICENSE").write_text("MIT\n", encoding="utf-8")
        Path(self.tmp, "README.md").write_text("# Acme — orders & invoices\n", encoding="utf-8")
        code, out, _ = _run(["init", "--name", "demo"])
        self.assertEqual(code, 0)
        self.assertIn(_BROWNFIELD_MARK, out, "a README is domain content -> brownfield")


if __name__ == "__main__":
    unittest.main()
