#!/usr/bin/env python3
"""Guard: regenerated test-cache artifacts are excluded from the §5 scope walk.

Trigger: bench-pilot-report heal_exhausted HARD-STOP — the verify gate's own
proof-suite run regenerates benchmark/.pytest_cache + .coverage, which the
scope walk then counted as out-of-scope touches. The exclusion constant's own
comment documents additive widening as the sanctioned change-request path.
Run:
    python3 -m unittest test_scope_exclude_test_caches -v
"""
import hashlib
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
TREES = (
    HERE / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"addpy_{path.parts[-3]}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ScopeExcludeTestCachesTest(unittest.TestCase):
    def test_pytest_cache_dir_excluded_in_all_trees(self):
        for tree in TREES:
            mod = _load(tree)
            self.assertIn(".pytest_cache", mod._SCOPE_EXCLUDE_DIRS,
                          f"{tree}: .pytest_cache missing from _SCOPE_EXCLUDE_DIRS")

    def test_coverage_file_excluded_in_all_trees(self):
        for tree in TREES:
            mod = _load(tree)
            self.assertIn(".coverage", mod._SCOPE_EXCLUDE_FILES,
                          f"{tree}: .coverage missing from _SCOPE_EXCLUDE_FILES")

    def test_trees_stay_byte_identical(self):
        digests = {hashlib.md5(t.read_bytes()).hexdigest() for t in TREES}
        self.assertEqual(1, len(digests), "engine trees diverged")


if __name__ == "__main__":
    unittest.main(verbosity=2)
