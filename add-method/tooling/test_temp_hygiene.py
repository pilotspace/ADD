#!/usr/bin/env python3
"""Leak guard (audit F14) — no test in this tree leaves a tempfile.mkdtemp dir behind.

Every `test_*.py` that creates a temp dir (`tempfile.mkdtemp(...)`) MUST also clean it
up — reference a cleanup seam (`shutil.rmtree` or `self.addCleanup`). A test that mkdtemps
without cleaning leaks a directory into the OS temp on every run; over a full suite that is
~100 stray dirs. This is a forward FENCE: a newly-added leaking test goes red here.

Static check (reads the file text — fast, no suite run). Run:
    python3 -m unittest test_temp_hygiene -v
"""
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _leakers():
    """test_*.py files that mkdtemp without any cleanup seam (self excluded)."""
    out = []
    for f in sorted(HERE.glob("test_*.py")):
        if f.name == "test_temp_hygiene.py":
            continue
        t = f.read_text(encoding="utf-8")
        if ".mkdtemp(" in t and not ("rmtree" in t or "addCleanup" in t):
            out.append(f.name)
    return out


class TempHygieneTest(unittest.TestCase):
    def test_no_test_file_leaks_tempdir(self):
        leakers = _leakers()
        self.assertEqual(
            leakers, [],
            f"temp_leak: {len(leakers)} test file(s) call tempfile.mkdtemp but never "
            f"rmtree/addCleanup — add `shutil.rmtree(self.tmp, ignore_errors=True)` to "
            f"their tearDown:\n  " + "\n  ".join(leakers),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
