#!/usr/bin/env python3
"""extract-state (engine-modularization 3/N) — the pure root/state-parse/error
helpers (`find_root`, `_require_root`, `_migrate_state`, `_state_text_or_die`,
`_die`, + the `_CONFLICT_MARKER_RE` regex) moved from add.py into
add_engine/io_state.py (extending the IO primitives from task 2), re-exported as
add.py module globals.

CONTRACT v2: `save_state`/`load_state` are deliberately KEPT in add.py — they are
NOT pure leaves. Their write-failure surface is pinned by `mock.patch("add._atomic_write")`
in test_state_hardening (a mutating command ends in save_state); moving them would
require repointing those patches. Keeping them in add.py preserves the milestone's
zero-test-churn property — they call the re-imported `_now`/`_atomic_write`/`_die`/
`_state_text_or_die`/`_migrate_state` as add module globals, so both the real path
and the `add._atomic_write` injection keep working. (They get their own later task.)

Run: python3 -m unittest test_engine_extract_state -v
"""
import hashlib
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

TREES = (
    TOOLING,
    REPO_ROOT / ".add" / "tooling",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling",
)

MOVED = ("find_root", "_require_root", "_migrate_state", "_state_text_or_die",
         "_die", "_CONFLICT_MARKER_RE")
KEPT_IN_ADD = ("save_state", "load_state")


class ReexportTest(unittest.TestCase):
    def test_helpers_live_in_io_state(self):
        from add_engine import io_state
        for name in MOVED:
            self.assertTrue(hasattr(io_state, name),
                            f"io_state must define {name} after the extraction")

    def test_helpers_reexported_same_object(self):
        import add
        from add_engine import io_state
        for name in MOVED:
            self.assertTrue(hasattr(add, name),
                            f"state_helper_drift: add.{name} missing after the split")
            self.assertIs(getattr(add, name), getattr(io_state, name),
                          f"state_helper_drift: add.{name} is not the io_state object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            token = f"\n{name} = " if name.isupper() else f"\ndef {name}("
            self.assertNotIn(token, src,
                             f"dead-code: add.py still defines {name} (duplicate of io_state)")

    def test_save_load_kept_in_add(self):
        """Contract v2: save_state/load_state stay in add.py (write-path-sensitive)."""
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in KEPT_IN_ADD:
            self.assertIn(f"\ndef {name}(", src,
                          f"{name} must remain defined in add.py (its add._atomic_write "
                          "failure-injection tests rely on it)")


class StateRoundTripTest(unittest.TestCase):
    def test_state_loads_through_moved_helpers(self):
        """load_state (kept in add.py) reads state back through the MOVED
        _state_text_or_die + _migrate_state + find_root — the move serves the real path."""
        import add
        cwd = os.getcwd()
        tmp = Path(tempfile.mkdtemp(prefix="add-state-")).resolve()
        try:
            os.chdir(tmp)
            buf, err = io.StringIO(), io.StringIO()
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["init", "--name", "demo"])
            root = add.find_root(tmp)                       # MOVED helper
            self.assertIsNotNone(root, "find_root must locate the project it just created")
            state = add.load_state(root)                    # routes through MOVED _state_text_or_die
            self.assertIsInstance(state, dict)
            self.assertIn("stage", state, "load_state must read back a well-formed state")
        finally:
            os.chdir(cwd)
            shutil.rmtree(tmp, ignore_errors=True)


class PinTest(unittest.TestCase):
    def test_engine_md5_still_pins_add_py(self):
        import engine_pin
        got = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(got, engine_pin.ENGINE_MD5,
                         "ENGINE_MD5 must stay md5(add.py), re-aimed after the shrink")

    def test_pkg_digest_3tree(self):
        import engine_pin
        import engine_manifest
        for tree in TREES:
            self.assertEqual(engine_manifest.package_digest(tree), engine_pin.ENGINE_PKG_MD5,
                             f"mirror_incomplete: {tree} package digest != ENGINE_PKG_MD5")

    def test_pins_are_literals(self):
        src = (TOOLING / "engine_pin.py").read_text(encoding="utf-8")
        for forbidden in ("hashlib", "read_bytes", "read_text", "open("):
            self.assertNotIn(forbidden, src,
                             f"vacuous_pin: engine_pin.py must not {forbidden!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
