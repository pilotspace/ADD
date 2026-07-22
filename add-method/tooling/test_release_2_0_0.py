#!/usr/bin/env python3
"""Red/green tests for the 2.0.0 release readiness (ADD 2.0 — skill-led, thin kernel).

Major cut: engine-kernel-trim (54 → 31 verbs; platform pillars → seed-persona
playbooks) · PLAN.md rename + the one-shot `add.py migrate` board conversion ·
5-DD living specs with `delta-append` · book-stops-shipping (site-only,
BOOK_URL deep links) · phase-collapse-3 · persona routes + the route
scoreboard (GEPA).

In-repo readiness only — the live-registry halves (npm/PyPI serving 2.0.0) are
verify-gate EVIDENCE gathered after the human-gated tag push, never unit tests.
The live-version-agreement asserts migrated FORWARD from test_release_1_18_0
(release-gate pattern: exactly ONE suite pins the current version).
Run:
    python3 -m unittest test_release_2_0_0 -v
"""
import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent                       # add-method/

CHANGELOG = PKG / "CHANGELOG.md"

VERSION = "2.0.0"
PRIOR_VERSIONS = ("1.18.0", "1.17.0", "1.16.1", "1.16.0", "1.15.0", "1.14.0", "1.13.0",
                  "1.12.0", "1.11.0", "1.10.0", "1.9.0", "1.8.0", "1.7.3", "1.7.2",
                  "1.7.1", "1.7.0", "1.6.0", "1.5.0", "1.4.0", "1.3.0", "1.2.0",
                  "1.1.0", "1.0.0")
# the headline changes the 2.0.0 notes must name
FEATURE_ANCHORS = ("kernel", "PLAN.md", "`add.py migrate`", "delta-append",
                   "book-stops-shipping", "route scoreboard", "GEPA")


class ChangelogTest(unittest.TestCase):
    def test_changelog_has_2_0_0_entry(self):
        self.assertTrue(CHANGELOG.is_file(), "CHANGELOG.md missing")
        text = CHANGELOG.read_text(encoding="utf-8")
        self.assertIn(f"## [{VERSION}]", text)
        for prior in PRIOR_VERSIONS:
            self.assertIn(f"## [{prior}]", text,
                          f"the {prior} lineage entry must survive the bump")
        entry = text.split(f"## [{VERSION}]", 1)[1].split("## [", 1)[0]
        for anchor in FEATURE_ANCHORS:
            self.assertIn(anchor, entry, f"2.0.0 entry must name: {anchor}")

    def test_major_names_breaking_changes(self):
        # semver: a major that breaks silently is a trap — the entry must carry
        # an explicit Breaking block naming the 2.0 line.
        entry = CHANGELOG.read_text(encoding="utf-8").split(
            f"## [{VERSION}]", 1)[1].split("## [", 1)[0]
        self.assertIn("Breaking", entry, "a MAJOR entry must name its breaking changes")
        for brk in ("PLAN.md", "migrate", ".add/docs"):
            self.assertIn(brk, entry, f"the Breaking block must cover: {brk}")


class ReleaseShapeTest(unittest.TestCase):
    # NOTE: 2.0.0 is superseded by 2.1.0 — the live-version-agreement assertions
    # migrated FORWARD into test_release_2_1_0 (release-gate pattern: exactly ONE
    # suite pins the current version).

    def test_major_entry_keeps_its_migrate_pointer(self):
        # the 2.0 upgrade door must stay documented for as long as 1.x boards exist
        entry = CHANGELOG.read_text(encoding="utf-8").split(
            f"## [{VERSION}]", 1)[1].split("## [", 1)[0]
        self.assertIn("`add.py migrate`", entry,
                      "the 2.0.0 entry must keep naming the one-shot board conversion")


if __name__ == "__main__":
    unittest.main(verbosity=2)
