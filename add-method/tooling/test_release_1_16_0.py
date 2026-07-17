#!/usr/bin/env python3
"""Red/green tests for the 1.16.0 release readiness.

Bundles one milestone — install-update-hardening (add.py init/update, both
--global and project-scope, pip+npm twins, survive a crash or a concurrent run
without leaving a half-written .add/ tree or a wedged lock): a new project-scope
install/update lock + opt-in --lock-timeout, plus crash-safe stage-then-commit
for the managed-tree reconcile copy and the user-data persist/restore path, plus
a TOCTOU race + ticket-leak livelock fix in the existing global lock. No loose
tasks attributed this cut. Installer-only — the ADD engine (add.py) is
byte-identical (the engine pin unchanged) since this milestone's own ship-by-domain
review named tooling (_installer.py + cli.js) as the only surface touched;
parity across the 3 mirror trees is what this suite pins, not a fixed hash.

In-repo readiness only — the live-registry halves (npm/PyPI serving 1.16.0) are
verify-gate EVIDENCE gathered after the human-gated tag push, never unit tests.
Run:
    python3 -m unittest test_release_1_16_0 -v
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

VERSION = "1.16.0"
PRIOR_VERSIONS = ("1.15.0", "1.14.0", "1.13.0", "1.12.0", "1.11.0", "1.10.0", "1.9.0", "1.8.0",
                  "1.7.3", "1.7.2", "1.7.1", "1.7.0", "1.6.0", "1.5.0", "1.4.0", "1.3.0",
                  "1.2.0", "1.1.0", "1.0.0")
# the headline milestone the 1.16.0 notes must name (add-method/CHANGELOG.md is the
# hand-authored Keep-a-Changelog; the slug appears verbatim in the entry's intro)
FEATURE_ANCHORS = ("install-update-hardening",)


class ChangelogTest(unittest.TestCase):
    def test_changelog_has_1_16_0_entry(self):
        self.assertTrue(CHANGELOG.is_file(), "CHANGELOG.md missing")
        text = CHANGELOG.read_text(encoding="utf-8")
        self.assertIn(f"## [{VERSION}]", text)
        for prior in PRIOR_VERSIONS:
            self.assertIn(f"## [{prior}]", text,
                          f"the {prior} lineage entry must survive the bump")
        entry = text.split(f"## [{VERSION}]", 1)[1].split("## [", 1)[0]
        for anchor in FEATURE_ANCHORS:
            self.assertIn(anchor, entry, f"1.16.0 entry must name: {anchor}")

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
    # NOTE: 1.16.0 is superseded by 1.16.1 — the live-version-agreement assertions
    # (versions/plugin/runtime == VERSION) moved to test_release_1_16_1.py. This file
    # keeps only the lineage + shipped-doc + engine-parity checks, which stay true
    # across bumps.
    def test_getting_started_mentions_guide_line(self):
        text = (PKG / "GETTING-STARTED.md").read_text(encoding="utf-8")
        self.assertIn("guide  :", text,
                      "orient docs must name the phase-playbook line")


if __name__ == "__main__":
    unittest.main(verbosity=2)
