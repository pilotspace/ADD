#!/usr/bin/env python3
"""Red/green tests for the 1.9.0 release readiness (lean-pass major bundle).

Bundles four closed milestones — skill-effectiveness (M1), flow-simplification (M3),
flow-enforcement (M4), and the fast-lane sub-milestone.

In-repo readiness only — the live-registry halves (npm/PyPI serving 1.9.0) are
verify-gate EVIDENCE gathered after the human-gated tag push, never unit tests.
Run:
    python3 -m unittest test_release_1_9_0 -v
"""
import hashlib
import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent                       # add-method/
REPO = PKG.parent
BUNDLE = PKG / "src" / "add_method" / "_bundled"

CHANGELOG = PKG / "CHANGELOG.md"
CI_YML = REPO / ".github" / "workflows" / "ci.yml"
PUBLISH_YML = REPO / ".github" / "workflows" / "publish.yml"

VERSION = "1.9.0"
PRIOR_VERSIONS = ("1.8.0", "1.7.3", "1.7.2", "1.7.1", "1.7.0", "1.6.0", "1.5.0",
                  "1.4.0", "1.3.0", "1.2.0", "1.1.0", "1.0.0")   # the changelog must keep its lineage
# the headline capabilities the release notes must name (the lean-pass bundle:
# fast lane + the three engine-enforced fill-seams + the lighter skill tree)
FEATURE_ANCHORS = ("fast-lane", "Freeze-before-build", "flow-enforcement",
                   "Gate-record write-back", "Skill tree 25% lighter", "Confirm-parent")


class ChangelogTest(unittest.TestCase):
    def test_changelog_has_1_9_0_entry(self):
        self.assertTrue(CHANGELOG.is_file(), "CHANGELOG.md missing")
        text = CHANGELOG.read_text(encoding="utf-8")
        self.assertIn(f"## [{VERSION}]", text)
        for prior in PRIOR_VERSIONS:
            self.assertIn(f"## [{prior}]", text,
                          f"the {prior} lineage entry must survive the bump")
        entry = text.split(f"## [{VERSION}]", 1)[1].split("## [", 1)[0]
        for anchor in FEATURE_ANCHORS:
            self.assertIn(anchor, entry, f"1.9.0 entry must name: {anchor}")

    def test_changelog_ships_in_both_channels(self):
        files = json.loads((PKG / "package.json").read_text(encoding="utf-8"))["files"]
        self.assertIn("CHANGELOG.md", files, "npm tarball must ship the changelog")
        self.assertIn("include CHANGELOG.md",
                      (PKG / "MANIFEST.in").read_text(encoding="utf-8"),
                      "sdist/wheel must ship the changelog")


class SecurityPolicyShipsTest(unittest.TestCase):
    """SECURITY.md must keep travelling with both published distributions."""

    def test_security_md_present(self):
        self.assertTrue((PKG / "SECURITY.md").is_file(),
                        "add-method/SECURITY.md must exist")

    def test_security_md_ships_in_both_channels(self):
        files = json.loads((PKG / "package.json").read_text(encoding="utf-8"))["files"]
        self.assertIn("SECURITY.md", files, "npm tarball must ship SECURITY.md")
        self.assertIn("include SECURITY.md",
                      (PKG / "MANIFEST.in").read_text(encoding="utf-8"),
                      "sdist/wheel must ship SECURITY.md")


class WorkflowHygieneTest(unittest.TestCase):
    def test_no_deprecated_actions(self):
        for wf in (CI_YML, PUBLISH_YML):
            text = wf.read_text(encoding="utf-8")
            self.assertNotIn("actions/checkout@v4", text, wf.name)
            self.assertNotIn("actions/setup-python@v5", text, wf.name)
            self.assertNotIn("actions/setup-node@v4", text, wf.name)
class ReleaseShapeTest(unittest.TestCase):
    # The live version-equality asserts (package.json / pyproject / plugin / __init__ all == the
    # shipped version) MOVED FORWARD to test_release_1_10_0.py — only the current cut owns them, so
    # the lineage tests below stay green after the bump. This file keeps the version-AGNOSTIC checks.

    def test_getting_started_mentions_guide_line(self):
        text = (PKG / "GETTING-STARTED.md").read_text(encoding="utf-8")
        self.assertIn("guide  :", text,
                      "orient docs must name the phase-playbook line")


if __name__ == "__main__":
    unittest.main(verbosity=2)
