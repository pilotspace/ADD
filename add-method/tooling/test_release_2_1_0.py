#!/usr/bin/env python3
"""Red/green tests for the 2.1.0 release readiness.

Minor cut: two-agent roster (add-worker + add-advisor, every-beat advising +
mid-flight support fan-out) · persona-author skill v11 (numbers-you'd-defend ·
per-flow stance · seeding) · flexible TDD (§4 acceptance checks for non-coding
kinds) · round-visible runs (uncapped observational verify→build rounds) ·
foundation-split (the dogfood 1.x→2.0 foundation migration worked example).

In-repo readiness only — the live-registry halves (npm/PyPI serving 2.1.0) are
verify-gate EVIDENCE gathered after the human-gated tag push, never unit tests.
The live-version-agreement asserts migrated FORWARD from test_release_2_0_0
(release-gate pattern: exactly ONE suite pins the current version).
Run:
    python3 -m unittest test_release_2_1_0 -v
"""
import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent                       # add-method/

CHANGELOG = PKG / "CHANGELOG.md"

VERSION = "2.1.0"
PRIOR_VERSIONS = ("2.0.0", "1.18.0", "1.17.0", "1.16.1", "1.16.0", "1.15.0", "1.14.0",
                  "1.13.0", "1.12.0", "1.11.0", "1.10.0", "1.9.0", "1.8.0", "1.7.3",
                  "1.7.2", "1.7.1", "1.7.0", "1.6.0", "1.5.0", "1.4.0", "1.3.0",
                  "1.2.0", "1.1.0", "1.0.0")
# the headline changes the 2.1.0 notes must name
FEATURE_ANCHORS = ("add-worker", "add-advisor", "persona-author", "flexible TDD",
                   "acceptance checks", "round", "foundation-split")


class ChangelogTest(unittest.TestCase):
    def test_changelog_has_2_1_0_entry(self):
        self.assertTrue(CHANGELOG.is_file(), "CHANGELOG.md missing")
        text = CHANGELOG.read_text(encoding="utf-8")
        self.assertIn(f"## [{VERSION}]", text)
        for prior in PRIOR_VERSIONS:
            self.assertIn(f"## [{prior}]", text,
                          f"the {prior} lineage entry must survive the bump")
        entry = text.split(f"## [{VERSION}]", 1)[1].split("## [", 1)[0]
        for anchor in FEATURE_ANCHORS:
            self.assertIn(anchor, entry, f"2.1.0 entry must name: {anchor}")

    def test_minor_names_its_retirements(self):
        # two `!`-marked commits ride this minor (the `add` agent · the static
        # persona template); the entry must carry an explicit Retired block so
        # the supersessions are named, not silent.
        entry = CHANGELOG.read_text(encoding="utf-8").split(
            f"## [{VERSION}]", 1)[1].split("## [", 1)[0]
        self.assertIn("Retired", entry, "the retirements must be named")
        for ret in ("`add` roster agent", "persona template"):
            self.assertIn(ret, entry, f"the Retired block must cover: {ret}")


class ReleaseShapeTest(unittest.TestCase):
    """The version sources move in lockstep (migrated forward from 2.0.0)."""

    def test_versions_agree_at_2_1_0(self):
        pkg = json.loads((PKG / "package.json").read_text(encoding="utf-8"))["version"]
        py = re.search(r'(?m)^version\s*=\s*"([^"]+)"',
                       (PKG / "pyproject.toml").read_text(encoding="utf-8")).group(1)
        self.assertEqual((pkg, py), (VERSION, VERSION),
                         "publish.yml's guard would fail this release closed")

    def test_runtime_version_agrees(self):
        init = (PKG / "src" / "add_method" / "__init__.py").read_text(encoding="utf-8")
        runtime = re.search(r'(?m)^__version__\s*=\s*"([^"]+)"', init).group(1)
        self.assertEqual(runtime, VERSION,
                         "add_method.__version__ must match the shipped version")

    def test_plugin_version_matches(self):
        plugin = json.loads(
            (PKG / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )["version"]
        self.assertEqual(plugin, VERSION,
                         "the Claude Code plugin manifest must match the shipped version")

    def test_package_lock_self_version(self):
        # npm refuses a mismatched lock in CI; the lock self-version appears twice
        # (top-level + the "" package entry) — both must carry the release.
        lock = json.loads((PKG / "package-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["version"], VERSION)
        self.assertEqual(lock["packages"][""]["version"], VERSION)


if __name__ == "__main__":
    unittest.main(verbosity=2)
