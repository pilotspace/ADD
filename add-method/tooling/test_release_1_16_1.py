#!/usr/bin/env python3
"""Red/green tests for the 1.16.1 release readiness (persona-loop hotfix).

Patch cut, no milestone — two loose, additive persona-loop improvements found
while dogfooding ADD in a real consumer project: the seed nudge is now
project-scoped (touches add.py/constants.py/io_state.py, the engine pin re-aimed),
and the persona schema template recommends a `flow:` field + `## Abilities`
section (templates-only, no engine change). Neither weakens an existing
engine check; PERSONA_FRONTMATTER_KEYS / PERSONA_REQUIRED_SECTIONS untouched.

In-repo readiness only — the live-registry halves (npm/PyPI serving 1.16.1) are
verify-gate EVIDENCE gathered after the human-gated tag push, never unit tests.
Run:
    python3 -m unittest test_release_1_16_1 -v
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

VERSION = "1.16.1"
PRIOR_VERSIONS = ("1.16.0", "1.15.0", "1.14.0", "1.13.0", "1.12.0", "1.11.0", "1.10.0", "1.9.0",
                  "1.8.0", "1.7.3", "1.7.2", "1.7.1", "1.7.0", "1.6.0", "1.5.0", "1.4.0", "1.3.0",
                  "1.2.0", "1.1.0", "1.0.0")
CANONICAL_AUDIT = "run: python3 .add/tooling/add.py audit"
# the headline changes the 1.16.1 notes must name
FEATURE_ANCHORS = ("project-scoped", "flow:", "## Abilities")


class ChangelogTest(unittest.TestCase):
    def test_changelog_has_1_16_1_entry(self):
        self.assertTrue(CHANGELOG.is_file(), "CHANGELOG.md missing")
        text = CHANGELOG.read_text(encoding="utf-8")
        self.assertIn(f"## [{VERSION}]", text)
        for prior in PRIOR_VERSIONS:
            self.assertIn(f"## [{prior}]", text,
                          f"the {prior} lineage entry must survive the bump")
        entry = text.split(f"## [{VERSION}]", 1)[1].split("## [", 1)[0]
        for anchor in FEATURE_ANCHORS:
            self.assertIn(anchor, entry, f"1.16.1 entry must name: {anchor}")

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

    def test_audit_line_survives_bumps(self):
        self.assertIn(CANONICAL_AUDIT, CI_YML.read_text(encoding="utf-8"),
                      "the seam-audit command must stay byte-identical")


class ReleaseShapeTest(unittest.TestCase):
    def test_getting_started_mentions_guide_line(self):
        text = (PKG / "GETTING-STARTED.md").read_text(encoding="utf-8")
        self.assertIn("guide  :", text,
                      "orient docs must name the phase-playbook line")


if __name__ == "__main__":
    unittest.main(verbosity=2)
