#!/usr/bin/env python3
"""egg-info-prune (milestone wm1-lean-to-twelve) — `<name>.egg-info/` build metadata
never reads as out-of-scope writes.

2026-07-23 run-3: 3/3 reps ran `pip install -e .` in-workspace, setuptools wrote
`app.egg-info/` at the project root, and the gate refused scope_violation on it —
the name is PROJECT-DERIVED, so no literal in _SCOPE_EXCLUDE_DIRS can cover it;
the prune is a suffix match in _scope_walk's dirnames filter. Suffix ONLY — a dir
merely containing the substring stays watched.

Run: cd add-method/tooling && python3 -m unittest test_egg_info_prune -v
"""
from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

import add


class EggInfoPrune(unittest.TestCase):
    def _tree(self, *rels):
        tmp = Path(tempfile.mkdtemp(prefix="add-eip-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        for rel in rels:
            f = tmp / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("x\n", encoding="utf-8")
        return tmp

    def test_egg_info_dir_pruned(self):                              # M1
        tmp = self._tree("app.egg-info/PKG-INFO", "app.egg-info/SOURCES.txt", "src/app.py")
        keys = set(add._scope_walk(tmp))
        self.assertEqual(keys, {os.path.join("src", "app.py")},
                         f"*.egg-info dirs are setuptools-owned metadata, never a write-set: {keys}")

    def test_egg_info_substring_kept(self):                          # M2
        tmp = self._tree("egg-info-tools/x.py")
        keys = set(add._scope_walk(tmp))
        self.assertEqual(keys, {os.path.join("egg-info-tools", "x.py")},
                         "suffix match only — a dir merely containing the substring stays watched")


if __name__ == "__main__":
    unittest.main(verbosity=2)
