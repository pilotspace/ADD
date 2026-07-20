#!/usr/bin/env python3
"""Plugin-manifest guard: the Claude Code marketplace + plugin manifests must stay
valid, in sync with the npm package, and honour the contract the `add` skill's
engine/book resolution rule promises.

ADD ships two ways now:
  - npm/pip  -> the CLI drops .add/tooling/add.py + .add/docs/ into the project.
  - plugin   -> `/plugin install add@add-method`. Nothing is dropped; the skill
                reaches the engine and the book at ${CLAUDE_PLUGIN_ROOT}/... .

For the plugin path to work, three things must hold and never drift:
  1. .claude-plugin/marketplace.json (repo root) lists the `add` plugin and points
     at ./add-method, where a plugin.json actually lives.
  2. add-method/.claude-plugin/plugin.json is well-formed, names skills ./skill/,
     and carries the SAME version as package.json (one source of truth).
  3. The files the SKILL.md resolution rule promises under ${CLAUDE_PLUGIN_ROOT}
     — tooling/add.py, tooling/templates/, docs/, skill/add/SKILL.md — exist, and
     the rule itself is present in the skill (so it cannot be silently removed).

Run: python3 -m unittest test_plugin_manifest -v
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent              # add-method/  (== the plugin root)
_REPO_ROOT = _ADD_METHOD.parent            # repo root    (== the marketplace root)

_MARKETPLACE = _REPO_ROOT / ".claude-plugin" / "marketplace.json"
_PLUGIN = _ADD_METHOD / ".claude-plugin" / "plugin.json"
_PACKAGE_JSON = _ADD_METHOD / "package.json"


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


class MarketplaceManifest(unittest.TestCase):
    def test_exists_and_is_valid_json(self) -> None:
        self.assertTrue(_MARKETPLACE.is_file(), f"missing {_MARKETPLACE}")
        data = _load(_MARKETPLACE)
        self.assertIsInstance(data, dict)

    def test_required_fields(self) -> None:
        data = _load(_MARKETPLACE)
        self.assertTrue(data.get("name"), "marketplace needs a name")
        self.assertNotIn(" ", data["name"], "marketplace name is the @<name> handle — no spaces")
        self.assertIsInstance(data.get("owner"), dict)
        self.assertTrue(data["owner"].get("name"), "owner needs a name")
        self.assertIsInstance(data.get("plugins"), list)
        self.assertTrue(data["plugins"], "marketplace lists no plugins")

    def test_add_plugin_source_resolves_to_a_plugin_dir(self) -> None:
        data = _load(_MARKETPLACE)
        entry = next((p for p in data["plugins"] if p.get("name") == "add"), None)
        self.assertIsNotNone(entry, "marketplace must list the `add` plugin")
        src = entry["source"]
        self.assertIsInstance(src, str, "source is the same-repo relative path form")
        self.assertTrue(src.startswith("./"), "relative source must start with ./")
        plugin_dir = (_REPO_ROOT / src).resolve()
        self.assertEqual(plugin_dir, _ADD_METHOD, "the add plugin lives in ./add-method")
        self.assertTrue((plugin_dir / ".claude-plugin" / "plugin.json").is_file(),
                        "source dir must contain .claude-plugin/plugin.json")


class PluginManifest(unittest.TestCase):
    def test_exists_and_is_valid_json(self) -> None:
        self.assertTrue(_PLUGIN.is_file(), f"missing {_PLUGIN}")
        self.assertIsInstance(_load(_PLUGIN), dict)

    def test_name_and_skills_path(self) -> None:
        data = _load(_PLUGIN)
        self.assertEqual(data.get("name"), "add", "plugin name drives /add:<skill>")
        self.assertEqual(data.get("skills"), "./skill/", "skills dir holds add/SKILL.md")
        skill_md = (_ADD_METHOD / "skill" / "add" / "SKILL.md")
        self.assertTrue(skill_md.is_file(), "skills path must resolve to add/SKILL.md")

    def test_version_tracks_the_npm_package(self) -> None:
        # one source of truth — a bumped package.json must bump the plugin too.
        self.assertEqual(_load(_PLUGIN).get("version"),
                         _load(_PACKAGE_JSON).get("version"),
                         "plugin.json version must match package.json version")


class PluginRootContract(unittest.TestCase):
    """A plugin install must be able to materialize the engine + book into the project."""

    def test_bootstrapper_and_payload_present(self) -> None:
        # the skill bootstraps via `node ${CLAUDE_PLUGIN_ROOT}/bin/cli.js init --no-skill`,
        # which copies these into the project — so all three must ride in the plugin.
        self.assertTrue((_ADD_METHOD / "bin" / "cli.js").is_file(),
                        "${CLAUDE_PLUGIN_ROOT}/bin/cli.js (the bootstrapper) must exist")
        self.assertTrue((_ADD_METHOD / "tooling" / "add.py").is_file(),
                        "the engine the bootstrap drops must exist")
        self.assertTrue((_ADD_METHOD / "tooling" / "templates").is_dir(),
                        "the engine needs its co-located templates/ dir")

    def test_book_present(self) -> None:
        docs = _ADD_METHOD / "docs"
        self.assertTrue(docs.is_dir(), "the book the bootstrap drops must exist")
        self.assertTrue(list(docs.glob("0*-*.md")), "the book must ship its chapters")

    def test_skill_carries_the_bootstrap(self) -> None:
        # the bootstrap line is the ONLY thing that makes a plugin install reach the
        # engine — it must never be dropped from the skill.
        text = (_ADD_METHOD / "skill" / "add" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/bin/cli.js", text)
        self.assertIn("--no-skill", text)


class BootstrapDropsEngineOnly(unittest.TestCase):
    """`cli.js init --no-skill` is what a plugin runs on first use: it must drop the
    engine into the project but NOT a duplicate skill (the plugin owns the skill) and
    NOT a book tree (book-stops-shipping, 2.0 M6b)."""

    def test_no_skill_drops_engine_but_not_skill_or_book(self) -> None:
        import shutil
        import subprocess
        import tempfile

        if shutil.which("node") is None:
            self.skipTest("node is not available")
        cli = _ADD_METHOD / "bin" / "cli.js"
        with tempfile.TemporaryDirectory() as d:
            proc = subprocess.run(["node", str(cli), "init", "--no-skill", d],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            target = Path(d)
            self.assertTrue((target / ".add" / "tooling" / "add.py").is_file(),
                            "engine must land in .add/tooling/")
            self.assertFalse((target / ".add" / "docs").exists(),
                             "book-stops-shipping: no .add/docs may land")
            self.assertFalse((target / ".claude" / "skills" / "add").exists(),
                             "--no-skill must NOT drop a duplicate skill (plugin owns it)")
            # runtime-only: no test files leak into the project copy
            self.assertEqual(list((target / ".add" / "tooling").glob("test_*.py")), [])


if __name__ == "__main__":
    unittest.main()
