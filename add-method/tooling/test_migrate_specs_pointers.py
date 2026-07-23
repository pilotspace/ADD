#!/usr/bin/env python3
"""migrate-specs-pointers: `add.py init`/`migrate` wire PROJECT.md to point at each
of the five living 5-DD specs — a managed, SPEC_DDS-driven ADD:SPECS block, injected
idempotently. PROJECT.md stays the thin read-first index; the block routes to the
detail in `.add/specs/`. A migrating (pre-pointer) project gets the block wired in;
`init` scaffolds it from the start; a second run is a stable no-op.

Run: cd add-method/tooling && python3 -m unittest test_migrate_specs_pointers -v
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADD_PY = HERE / "add.py"
sys.path.insert(0, str(HERE))
from add_engine.constants import SPEC_DDS, _SPECS_BEGIN, _SPECS_END  # noqa: E402


def _run(cwd, *args):
    return subprocess.run([sys.executable, str(ADD_PY), *args], cwd=cwd,
                          capture_output=True, text=True, timeout=120)


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        r = _run(self.root, "init", "--name", "sp", "--stage", "mvp")
        assert r.returncode == 0, r.stderr + r.stdout
        self.pmd = Path(self.root) / ".add" / "PROJECT.md"

    def tearDown(self):
        self._tmp.cleanup()

    def _strip_block(self):
        t = self.pmd.read_text()
        b, e = t.find(_SPECS_BEGIN), t.find(_SPECS_END)
        if b != -1 and e != -1:
            self.pmd.write_text(t[:b] + t[e + len(_SPECS_END):])


class InitWiresSpecs(_Base):
    def test_init_scaffolds_the_specs_block(self):
        # S1: a freshly init'd PROJECT.md already points at each of the five specs
        t = self.pmd.read_text()
        self.assertIn(_SPECS_BEGIN, t, "init must scaffold the ADD:SPECS block")
        self.assertIn(_SPECS_END, t)
        for fname, *_ in SPEC_DDS.values():
            self.assertIn(f".add/specs/{fname}", t, f"PROJECT.md must point at {fname}")


class MigrateWiresSpecs(_Base):
    def test_migrate_injects_when_absent(self):
        # S2: a pre-pointer PROJECT.md (block stripped) gets it wired by migrate
        self._strip_block()
        self.assertNotIn(_SPECS_BEGIN, self.pmd.read_text())
        r = _run(self.root, "migrate")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        t = self.pmd.read_text()
        self.assertIn(_SPECS_BEGIN, t, "migrate must inject the ADD:SPECS block")
        for fname, *_ in SPEC_DDS.values():
            self.assertIn(f".add/specs/{fname}", t)

    def test_block_lists_exactly_the_five_specs(self):
        # S3: driven by SPEC_DDS — no more, no fewer than the five spec files
        t = self.pmd.read_text()
        block = t[t.find(_SPECS_BEGIN):t.find(_SPECS_END)]
        refs = set(re.findall(r"\.add/specs/(\S+\.md)", block))
        self.assertEqual(refs, {v[0] for v in SPEC_DDS.values()},
                         "the block must reference exactly the SPEC_DDS files")

    def test_migrate_is_idempotent(self):
        # S4: strip → migrate → migrate again is a stable no-op, one block only
        self._strip_block()
        _run(self.root, "migrate")
        first = self.pmd.read_text()
        _run(self.root, "migrate")
        self.assertEqual(self.pmd.read_text(), first, "a second migrate must be a stable no-op")
        self.assertEqual(first.count(_SPECS_BEGIN), 1, "exactly one specs block, never duplicated")


if __name__ == "__main__":
    unittest.main(verbosity=2)
