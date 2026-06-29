#!/usr/bin/env python3
"""Red/green for mirror-resync: the two stale mirror files must byte-match canonical
(fallout of commit 123258c — canonical + _bundled enriched, these mirrors left behind)."""
import hashlib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
PAIRS = [
    (REPO / "add-method/skill/add/phases/5-build.md",
     REPO / ".claude/skills/add/phases/5-build.md"),
    (REPO / "add-method/tooling/templates/TASK.md.tmpl",
     REPO / ".add/tooling/templates/TASK.md.tmpl"),
]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class MirrorParity(unittest.TestCase):
    def test_mirrors_match_canonical(self):
        for canon, mirror in PAIRS:
            self.assertTrue(canon.exists(), f"canonical missing: {canon}")
            self.assertTrue(mirror.exists(), f"mirror missing: {mirror}")
            self.assertEqual(_md5(canon), _md5(mirror),
                             f"mirror drifted from canonical: {mirror}")


if __name__ == "__main__":
    unittest.main()
