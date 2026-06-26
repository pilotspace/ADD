#!/usr/bin/env python3
"""extract-guidelines (engine-modularization 8/N) — the guidelines/CLAUDE.md-injection
subsystem (8 fns + the cluster-private `_INIT_EXCLUDE`) moved from add.py into a NEW
add_engine/guidelines.py, re-exported as add.py module globals.

Transitive-closure AST scan proved the cluster is self-contained (ZERO outbound calls
to non-cluster add fns) and none are monkeypatched → a plain re-export, no qualification.
Deps: constants (6) + _atomic_write (io_state) + os/re/sys/Path (stdlib).

Run: python3 -m unittest test_engine_extract_guidelines -v
"""
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

TREES = (
    TOOLING,
    REPO_ROOT / ".add" / "tooling",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling",
)

MOVED = ("_guideline_block", "_inject_block", "_rule_file_mode", "_strip_inline_block",
         "_insert_rule_reference", "_ensure_claude_reference", "_inject_guidelines",
         "_is_brownfield")


class ReexportTest(unittest.TestCase):
    def test_guidelines_live_in_module(self):
        from add_engine import guidelines
        for name in MOVED:
            self.assertTrue(hasattr(guidelines, name),
                            f"guidelines.py must define {name} after the extraction")
        self.assertTrue(hasattr(guidelines, "_INIT_EXCLUDE"),
                        "the cluster-private _INIT_EXCLUDE must travel with _is_brownfield")

    def test_guidelines_reexported_same_object(self):
        import add
        from add_engine import guidelines
        for name in MOVED:
            self.assertTrue(hasattr(add, name),
                            f"guideline_drift: add.{name} missing after the split")
            self.assertIs(getattr(add, name), getattr(guidelines, name),
                          f"guideline_drift: add.{name} is not the guidelines object")

    def test_add_py_no_longer_defines_them(self):
        src = (TOOLING / "add.py").read_text(encoding="utf-8")
        for name in MOVED:
            self.assertNotIn(f"\ndef {name}(", src,
                             f"dead-code: add.py still defines {name}")
        self.assertNotIn("\n_INIT_EXCLUDE = {", src,
                         "dead-code: add.py still defines _INIT_EXCLUDE")


class BlockInjectionTest(unittest.TestCase):
    def test_init_writes_canonical_add_block(self):
        import add
        from add_engine import guidelines
        cwd = os.getcwd()
        tmp = Path(tempfile.mkdtemp(prefix="add-guide-")).resolve()
        try:
            os.chdir(tmp)
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(buf):
                add.main(["init", "--name", "demo"])
            claude = (tmp / "CLAUDE.md").read_text(encoding="utf-8")
            # the canonical block body (from the moved _guideline_block) must be present verbatim
            block = guidelines._guideline_block()
            self.assertIn(block, claude,
                          "the marker-delimited ADD block must be injected byte-identically")
        finally:
            os.chdir(cwd)
            shutil.rmtree(tmp, ignore_errors=True)


class NoCycleTest(unittest.TestCase):
    def test_guidelines_imports_without_add(self):
        code = ("import add_engine.guidelines as g; "
                "assert all(hasattr(g, n) for n in "
                "['_inject_guidelines','_is_brownfield','_guideline_block'])")
        r = subprocess.run([sys.executable, "-c", code], cwd=str(TOOLING),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"cycle/import error: {r.stderr.strip()}")


class PinTest(unittest.TestCase):
    def test_engine_md5_still_pins_add_py(self):
        import engine_pin
        got = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(got, engine_pin.ENGINE_MD5,
                         "ENGINE_MD5 must stay md5(add.py), re-aimed after the shrink")

    def test_pkg_digest_includes_guidelines_3tree(self):
        import engine_pin
        import engine_manifest
        names = [f.name for f in engine_manifest.package_files(TOOLING)]
        self.assertIn("guidelines.py", names, "guidelines.py must join the package manifest")
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
