#!/usr/bin/env python3
"""npm cli.js seeds .add/SOUL.md if missing — parity with the pip _seed_soul_md twin
(task: soul-seed-npm-parity).

The pip installer (_installer.py._seed_soul_md) already re-seeds a missing SOUL.md on
both install and update; the npm launcher (bin/cli.js) did not. cli.js carries no node
test harness, so — exactly like test_update.py — this is a TEXT-INVARIANT proof on the
cli.js source: the seed function exists, references the bundled template, guards
skip-if-exists, and is called in BOTH the install (dropFiles) and update (cmdUpdate)
regions. The behavioral coverage lives on the pip twin (test_installer_soul_seed.py).

Run: python3 -m unittest test_soul_seed_npm_parity -v
"""
import re
import unittest
from pathlib import Path

_ADD_METHOD = Path(__file__).resolve().parent.parent
CLI_JS = _ADD_METHOD / "bin" / "cli.js"


class SoulSeedNpmParity(unittest.TestCase):
    def _src(self) -> str:
        return CLI_JS.read_text(encoding="utf-8")

    def test_seed_function_defined(self):
        src = self._src()
        self.assertRegex(src, r"function\s+seedSoulMd\s*\(",
                         "cli.js must define a seedSoulMd function (pip _seed_soul_md twin)")
        self.assertIn("SOUL.md.tmpl", src,
                      "seedSoulMd must seed from the bundled tooling/templates/SOUL.md.tmpl")

    def test_skip_if_exists_guard(self):
        # never clobber a user-owned SOUL.md
        src = self._src()
        self.assertRegex(src, r"seedSoulMd[\s\S]*?existsSync\([^\)]*dest[^\)]*\)\s*\)\s*return",
                         "seedSoulMd must skip-if-exists (never clobber an existing SOUL.md)")

    def test_called_in_both_install_and_update(self):
        src = self._src()
        # locate the two host functions and assert each calls seedSoulMd
        for fn in ("dropFiles", "cmdUpdate"):
            m = re.search(rf"function\s+{fn}\s*\([\s\S]*?\n\}}", src)
            self.assertIsNotNone(m, f"could not locate {fn} in cli.js")
            self.assertIn("seedSoulMd(", m.group(0),
                          f"{fn} must call seedSoulMd( after reconcile (npm<->pip parity)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
