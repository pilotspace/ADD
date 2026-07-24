#!/usr/bin/env python3
"""Red/green tests for the 2.4.0 release readiness.

Minor cut: the strategy-intake milestone closes — a fitting persona becomes ADD's
adaptive PM brain (the new strategy.md DISCUSS→OPTIMIZE→CONVERGE loop filling the
`## Strategy` slot, the add-advisor refute at CONVERGE, the risk-proportional depth
ladder, and intake loading the fitting persona before it sizes) — plus the follow-on
that completes the §2→§4 scenarios fold and adds a shipped-surface CI sweep. All
changes are skill/agent-surface prose; the engine is unchanged (additive/zero).

In-repo readiness only — the live-registry halves (npm/PyPI serving 2.4.0) are
verify-gate EVIDENCE gathered after the human-gated tag push, never unit tests.
The live-version-agreement asserts migrated FORWARD from test_release_2_3_0
(release-gate pattern: exactly ONE suite pins the current version).
Run:
    python3 -m unittest test_release_2_4_0 -v
"""
import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent                       # add-method/

CHANGELOG = PKG / "CHANGELOG.md"

VERSION = "2.4.0"
PRIOR_VERSIONS = ("2.3.0", "2.2.0", "2.1.0", "2.0.0", "1.18.0", "1.17.0", "1.16.1",
                  "1.16.0", "1.15.0", "1.14.0", "1.13.0", "1.12.0", "1.11.0", "1.10.0",
                  "1.9.0", "1.8.0", "1.7.3", "1.7.2", "1.7.1", "1.7.0", "1.6.0", "1.5.0",
                  "1.4.0", "1.3.0", "1.2.0", "1.1.0", "1.0.0")
# the headline changes the 2.4.0 notes must name
FEATURE_ANCHORS = ("strategy loop", "DISCUSS", "CONVERGE", "risk-proportional",
                   "add-advisor", "fitting persona", "shipped-surface")


class ChangelogTest(unittest.TestCase):
    def test_changelog_has_2_4_0_entry(self):
        self.assertTrue(CHANGELOG.is_file(), "CHANGELOG.md missing")
        text = CHANGELOG.read_text(encoding="utf-8")
        self.assertIn(f"## [{VERSION}]", text)
        for prior in PRIOR_VERSIONS:
            self.assertIn(f"## [{prior}]", text,
                          f"the {prior} lineage entry must survive the bump")
        entry = text.split(f"## [{VERSION}]", 1)[1].split("## [", 1)[0]
        for anchor in FEATURE_ANCHORS:
            self.assertIn(anchor, entry, f"2.4.0 entry must name: {anchor}")


class ReleaseShapeTest(unittest.TestCase):
    """The version sources move in lockstep (migrated forward from 2.3.0)."""

    def test_versions_agree_at_2_4_0(self):
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

    def test_skill_frontmatter_version_in_sync(self):
        # the three skill trees carry the version in SKILL.md frontmatter; the CI
        # mirror-gap meta-test fails publish if they drift. Assert all three at VERSION.
        trees = (
            PKG / "skill" / "add" / "SKILL.md",
            PKG / "src" / "add_method" / "_bundled" / "skill" / "add" / "SKILL.md",
            PKG.parent / ".claude" / "skills" / "add" / "SKILL.md",
        )
        for f in trees:
            m = re.search(r'(?m)^\s*version:\s*"([^"]+)"', f.read_text(encoding="utf-8"))
            self.assertIsNotNone(m, f"no version frontmatter in {f}")
            self.assertEqual(m.group(1), VERSION, f"{f} version must be {VERSION}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
