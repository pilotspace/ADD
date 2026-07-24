#!/usr/bin/env python3
"""lock-reclaim-hardening: the stale-reclaim unlink must re-verify STALENESS, not just inode.

Root cause of the publish-gate flake (test_concurrent_stale_reclaim, peak=2 on Linux CI):
`_update_lock`'s reclaim re-stat-before-unlink guard trusted inode-NUMBER identity
(`current_ino == st.st_ino`). Linux ext4/tmpfs REUSE freed inode numbers, so a live
holder's fresh replacement lock can reuse the crashed file's inode — a delayed racer then
passes the inode check and unlinks the LIVE lock, and both hold (peak=2). macOS APFS does
not reuse inodes short-term, which is why it never reproduced locally.

The fix adds `_still_stale_generation(path, observed_ino, stale_after)`: reclaim only if the
current file is BOTH the observed inode AND still stale (mtime age > stale_after). A fresh
reused-inode holder (age ~0) is spared. These deterministic unit tests prove that invariant
(the concurrency integration test can't reproduce inode reuse on APFS — 0/80 under load).
"""

import os
import time
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from add_method import _installer            # noqa: E402


class StillStaleGeneration(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp(prefix="reclaim-harden-")
        self.path = Path(self.tmp) / ".update.lock"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _make(self, age_seconds):
        self.path.write_text("x")
        st = self.path.stat()
        past = time.time() - age_seconds
        os.utime(self.path, (past, past))
        return self.path.stat().st_ino

    def test_reused_inode_live_file_not_reclaimable(self):              # M2, R:weakened_mutual_exclusion
        # Observe a stale generation's inode, then the file becomes FRESH at the SAME inode
        # (exactly what inode reuse produces: a live holder's new lock reusing the freed inode).
        observed_ino = self._make(age_seconds=100)
        os.utime(self.path, None)   # refresh mtime -> now fresh, inode UNCHANGED (same file)
        self.assertFalse(
            _installer._still_stale_generation(self.path, observed_ino, stale_after=90),
            "a same-inode file that is now FRESH must NOT be reclaimed — it is a live holder "
            "whose lock reused the crashed generation's inode number (the peak=2 double-hold)")

    def test_genuinely_stale_same_inode_is_reclaimable(self):          # M4
        observed_ino = self._make(age_seconds=100)
        self.assertTrue(
            _installer._still_stale_generation(self.path, observed_ino, stale_after=90),
            "a genuinely crashed stale lock (aged mtime, same inode) must still be reclaimable")

    def test_vanished_file_not_reclaimable(self):                      # M4
        observed_ino = self._make(age_seconds=100)
        os.unlink(self.path)
        self.assertFalse(
            _installer._still_stale_generation(self.path, observed_ino, stale_after=90),
            "a vanished path is not a reclaim target (OSError -> False)")

    def test_different_inode_not_reclaimable(self):                    # M2 (reinforce)
        observed_ino = self._make(age_seconds=100)
        os.unlink(self.path)
        self.path.write_text("y")          # recreate — a DIFFERENT generation
        past = time.time() - 100
        os.utime(self.path, (past, past))  # even if it is ALSO stale...
        new_ino = self.path.stat().st_ino
        if new_ino == observed_ino:
            self.skipTest("filesystem reused the inode number; identity-by-mtime still covers it")
        self.assertFalse(
            _installer._still_stale_generation(self.path, observed_ino, stale_after=90),
            "a different-inode file is a different generation — not the one we observed")


class JsStillStaleGeneration(unittest.TestCase):
    """The JS/npm twin (`bin/cli.js`) carried the IDENTICAL inode-identity reclaim guard at four
    sites (ticket + main lock in each of acquireUpdateLock/acquireProjectLock), so the same
    reused-inode double-hold shipped on the npm install path. cli.js already has a
    `require.main === module` guard + `module.exports`, so the helper is driven directly.
    """

    @classmethod
    def setUpClass(cls):
        import shutil
        if shutil.which("node") is None:
            raise unittest.SkipTest("node not available")
        cls.cli = Path(__file__).resolve().parent.parent / "bin" / "cli.js"

    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp(prefix="js-reclaim-harden-")
        self.path = Path(self.tmp) / ".update.lock"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _node_probe(self, body):
        """Run `body` in a node subprocess with `cli` (the required module) and `p` (the lock
        path) in scope; the script must print exactly `true` or `false`."""
        import json
        import subprocess
        script = (
            "const cli = require(%s);\n"
            "const p = %s;\n"
            "%s\n" % (json.dumps(str(self.cli)), json.dumps(str(self.path)), body)
        )
        out = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0,
                         "node helper harness failed (RED for the right reason means a MISSING "
                         "export, surfaced here verbatim):\n%s\n%s" % (out.stdout, out.stderr))
        return out.stdout.strip().splitlines()[-1]

    def _make(self, age_seconds):
        self.path.write_text("x")
        past = time.time() - age_seconds
        os.utime(self.path, (past, past))
        return self.path.stat().st_ino

    def test_js_reused_inode_live_file_not_reclaimable(self):        # M2, R:weakened_mutual_exclusion
        observed_ino = self._make(age_seconds=100)
        os.utime(self.path, None)   # same inode, now FRESH — the live reused-inode holder
        self.assertEqual(
            self._node_probe("console.log(cli.stillStaleGeneration(p, %d, 90));" % observed_ino),
            "false",
            "JS twin: a same-inode file that is now FRESH must NOT be reclaimed — that is the "
            "npm-path mirror of the peak=2 double-hold")

    def test_js_genuinely_stale_same_inode_is_reclaimable(self):     # M4
        observed_ino = self._make(age_seconds=100)
        self.assertEqual(
            self._node_probe("console.log(cli.stillStaleGeneration(p, %d, 90));" % observed_ino),
            "true",
            "JS twin: a genuinely crashed stale lock must still self-heal")
        os.unlink(self.path)
        self.assertEqual(
            self._node_probe("console.log(cli.stillStaleGeneration(p, %d, 90));" % observed_ino),
            "false",
            "JS twin: a vanished path is not a reclaim target")


if __name__ == "__main__":
    unittest.main()
