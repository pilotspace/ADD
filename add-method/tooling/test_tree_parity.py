#!/usr/bin/env python3
"""Canonical tree-parity + engine-pin sweep — ADD 3.0 (ABF-1), flat-engine edition.

This ONE suite owns the package's static-tree integrity invariants so a diverged or
orphaned file reds exactly here. Adapted from the 2.5 sweep for the flat two-file
engine (add.py + cli.py; no add_engine/ package).

Surfaces swept:
  skill    add-method/skill/add  ==  _bundled/skill/add  (git-tracked: ALWAYS compared)
                                 ==  .claude/skills/add   (dogfood twin: exists-skip)
  tooling  add.py · cli.py · templates/**  ==  _bundled/tooling/**   (ALWAYS)
  corpus   add-method/personas-teacher  ==  _bundled/personas-teacher (ALWAYS)
  pins     md5(add.py) == ENGINE_MD5 · md5(cli.py) == ENGINE_PKG_MD5

Skip policy — never vacuous: the canonical and _bundled trees are git-tracked and are
ALWAYS compared (their absence is a hard failure); only the gitignored/channel-installed
dogfood twin (.claude/skills/add on a fresh package) exists-skips.

Run: python3 -m pytest add-method/tooling/test_tree_parity.py -v
"""
from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine_manifest  # noqa: E402
import engine_pin  # noqa: E402

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent
_BUNDLE = _ADD_METHOD / "src" / "add_method" / "_bundled"

CANON_SKILL = _ADD_METHOD / "skill" / "add"
BUNDLE_SKILL = _BUNDLE / "skill" / "add"
DOGFOOD_SKILL = _REPO / ".claude" / "skills" / "add"

CANON_TOOLING = _TOOLING
BUNDLE_TOOLING = _BUNDLE / "tooling"

CANON_CORPUS = _ADD_METHOD / "personas-teacher"
BUNDLE_CORPUS = _BUNDLE / "personas-teacher"

# Files that live in the canonical tooling dir but are dev-only (never shipped to _bundled).
_DEV_ONLY = {"engine_pin.py", "engine_manifest.py", "gate_fixtures.py", "md_section.py",
             "pty_clack.py", "semantic_inventory.py", "wording_lint.py", "t",
             "SEMANTIC_INVENTORY.md", "WORDING_RUBRIC.md"}


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _tree_map(root: Path, *, skip_names=frozenset()) -> dict:
    """{relative-posix-path: md5} for every file under root, excluding junk + skip_names."""
    out = {}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts or p.suffix in (".pyc", ".pyo") or p.name == ".DS_Store":
            continue
        rel = p.relative_to(root)
        if rel.parts and rel.parts[0] in skip_names:
            continue
        out[rel.as_posix()] = _md5(p)
    return out


class EnginePinParity(unittest.TestCase):
    def test_add_py_matches_ENGINE_MD5(self):
        self.assertEqual(engine_manifest.engine_digest(_TOOLING), engine_pin.ENGINE_MD5,
                         "md5(tooling/add.py) drifted from ENGINE_MD5 — re-aim engine_pin.py")

    def test_cli_py_matches_ENGINE_PKG_MD5(self):
        self.assertEqual(engine_manifest.package_digest(_TOOLING), engine_pin.ENGINE_PKG_MD5,
                         "md5(tooling/cli.py) drifted from ENGINE_PKG_MD5 — re-aim engine_pin.py")


class BundleParity(unittest.TestCase):
    def test_skill_bundle_matches_canonical(self):
        self.assertTrue(CANON_SKILL.is_dir() and BUNDLE_SKILL.is_dir(),
                        "canonical + bundled skill trees must both exist (git-tracked)")
        self.assertEqual(_tree_map(CANON_SKILL), _tree_map(BUNDLE_SKILL),
                         "skill/add drifted from _bundled/skill/add — run scripts/prepare_bundle.py")

    def test_engine_bundle_matches_canonical(self):
        for name in ("add.py", "cli.py"):
            self.assertEqual(_md5(CANON_TOOLING / name), _md5(BUNDLE_TOOLING / name),
                             f"tooling/{name} drifted from _bundled — run prepare_bundle.py")

    def test_templates_bundle_matches_canonical(self):
        self.assertEqual(_tree_map(CANON_TOOLING / "templates"),
                         _tree_map(BUNDLE_TOOLING / "templates"),
                         "tooling/templates drifted from _bundled — run prepare_bundle.py")

    def test_bundle_ships_no_add_engine_or_dev_only(self):
        self.assertFalse((BUNDLE_TOOLING / "add_engine").exists(),
                         "the flat engine ships no add_engine/ package")
        shipped = {p.name for p in BUNDLE_TOOLING.iterdir() if p.is_file()}
        leaked = shipped & _DEV_ONLY
        self.assertFalse(leaked, f"dev-only files leaked into the bundle: {leaked}")

    def test_corpus_bundle_matches_canonical(self):
        self.assertTrue(CANON_CORPUS.is_dir() and BUNDLE_CORPUS.is_dir(),
                        "canonical + bundled personas-teacher must both exist")
        self.assertEqual(_tree_map(CANON_CORPUS), _tree_map(BUNDLE_CORPUS),
                         "personas-teacher drifted from _bundled — run prepare_bundle.py")


class DogfoodMirror(unittest.TestCase):
    def test_dogfood_skill_matches_canonical_when_present(self):
        if not DOGFOOD_SKILL.is_dir():
            self.skipTest("dogfood .claude/skills/add absent (fresh package) — exists-skip")
        self.assertEqual(_tree_map(CANON_SKILL), _tree_map(DOGFOOD_SKILL),
                         ".claude/skills/add drifted from add-method/skill/add — resync the mirror")


if __name__ == "__main__":
    unittest.main()
