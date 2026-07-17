#!/usr/bin/env python3
"""THE canonical tree-parity + engine-pin sweep (task test-corpus-slim).

Parity was previously asserted ad hoc — ~110 per-task copies of "these trees
agree" and "the engine is untouched" scattered across the corpus, so every
guide fold or repin rippled into dozens of duplicated reds. This ONE suite now
owns every static-tree invariant; per-task suites keep only content pins.

Surfaces swept (a diverged or orphan file reds exactly this suite):
  skill    add-method/skill/add ↔ _bundled/skill/add ↔ .claude/skills/add
  agents   add-method/agents/add-*.md ↔ _bundled/agents ↔ .claude/agents
  tooling  add.py · engine_pin.py · add_engine/*.py · templates/** — 4-way
           (canonical · _bundled · REPO/.add · add-method/.add)
  docs     add-method/docs/*.md ↔ _bundled/docs ↔ repo-root chapter mirrors
  pins     md5(add.py) == ENGINE_MD5 · package_digest == ENGINE_PKG_MD5 (ONCE)

Skip policy — never vacuous: the canonical and _bundled trees are git-tracked
and are ALWAYS compared (their absence is a hard failure, never a skip); only
the gitignored dogfood twins (.claude mirrors on a fresh package, the two
.add/tooling trees on a fresh clone) exists-skip, with ≥2 trees always live
(ba09498 precedent).

Run: python3 -m unittest test_tree_parity -v
"""
import hashlib
import re
import unittest
from pathlib import Path

import engine_manifest
import engine_pin

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent
_BUNDLE = _ADD_METHOD / "src" / "add_method" / "_bundled"

# git-tracked trees: ALWAYS present, ALWAYS compared (a missing one is a failure)
CANON_SKILL = _ADD_METHOD / "skill" / "add"
BUNDLE_SKILL = _BUNDLE / "skill" / "add"
# gitignored / channel-installed twins: exists-skip
DOGFOOD_SKILL = _REPO / ".claude" / "skills" / "add"

AGENT_TREES = (_ADD_METHOD / "agents", _BUNDLE / "agents", _REPO / ".claude" / "agents")

TOOLING_TREES = (_TOOLING, _BUNDLE / "tooling",
                 _REPO / ".add" / "tooling", _ADD_METHOD / ".add" / "tooling")

DOCS_CANON = _ADD_METHOD / "docs"
DOCS_BUNDLE = _BUNDLE / "docs"
DOCS_DOGFOOD = _REPO / ".add" / "docs"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _rel_files(root: Path):
    return {p.relative_to(root) for p in root.rglob("*") if p.is_file()}


class SkillTreeParityTest(unittest.TestCase):
    def test_skill_trees_byte_identical(self):
        # canonical + bundled are git-tracked: never skipped, never vacuous
        for tracked in (CANON_SKILL, BUNDLE_SKILL):
            self.assertTrue(tracked.is_dir(), f"git-tracked skill tree missing: {tracked}")
        trees = [CANON_SKILL, BUNDLE_SKILL] + (
            [DOGFOOD_SKILL] if DOGFOOD_SKILL.is_dir() else [])
        canon = _rel_files(CANON_SKILL)
        for twin in trees[1:]:
            other = _rel_files(twin)
            self.assertEqual(
                sorted(map(str, canon)), sorted(map(str, other)),
                f"skill file sets differ (orphans) between {CANON_SKILL} and {twin}:\n"
                f"  only in canonical: {sorted(map(str, canon - other))}\n"
                f"  only in twin:      {sorted(map(str, other - canon))}")
            mismatched = [str(rel) for rel in sorted(canon, key=str)
                          if _md5(CANON_SKILL / rel) != _md5(twin / rel)]
            self.assertEqual(mismatched, [],
                             f"skill file(s) diverged vs {twin} (propagate with cp):\n  "
                             + "\n  ".join(mismatched))


class AgentsParityTest(unittest.TestCase):
    def test_roster_agents_byte_identical(self):
        # roster-distill (ADD 2.0 M1): the ONE `add` agent ships in three trees;
        # .claude/agents also holds user agents, so parity binds the add*.md subset only
        canon, bundle, dogfood = AGENT_TREES
        for tracked in (canon, bundle):
            self.assertTrue(tracked.is_dir(), f"git-tracked agents tree missing: {tracked}")
        names = sorted(p.name for p in canon.glob("add*.md"))
        self.assertTrue(names, "canonical roster is empty — the sweep would be vacuous")
        self.assertEqual(names, sorted(p.name for p in bundle.glob("add*.md")),
                         "bundled roster file set diverged")
        for name in names:
            self.assertEqual(_md5(canon / name), _md5(bundle / name),
                             f"roster agent diverged: {bundle / name}")
            if dogfood.is_dir() and (dogfood / name).exists():
                self.assertEqual(_md5(canon / name), _md5(dogfood / name),
                                 f"roster agent diverged: {dogfood / name}")


class ToolingParityTest(unittest.TestCase):
    """4-way engine parity: canonical · bundle (git-tracked) · two dogfood
    twins (gitignored, exists-skip — ≥2 trees always live)."""

    def _present(self):
        present = [t for t in TOOLING_TREES if (t / "add.py").exists()]
        self.assertGreaterEqual(len(present), 2,
                                "tooling twin set collapsed below canonical+bundle")
        for tracked in TOOLING_TREES[:2]:
            self.assertIn(tracked, present, f"git-tracked tooling tree missing: {tracked}")
        return present

    def test_engine_files_byte_identical(self):
        present = self._present()
        rels = ["add.py", "engine_pin.py"]
        rels += [f"add_engine/{p.name}" for p in sorted((_TOOLING / "add_engine").glob("*.py"))]
        rels += [str(p.relative_to(_TOOLING))
                 for p in sorted((_TOOLING / "templates").rglob("*.tmpl"))]
        for rel in sorted(set(rels)):
            digests = {_md5(t / rel) for t in present if (t / rel).exists()}
            self.assertEqual(len(digests), 1, f"tooling twin diverged: {rel}")

    def test_engine_pin_holds(self):
        # THE one engine-pin assert (test-corpus-slim: per-task copies deleted)
        self.assertEqual(_md5(_TOOLING / "add.py"), engine_pin.ENGINE_MD5,
                         "add.py != ENGINE_MD5 — an engine edit must repin engine_pin.py")
        self.assertEqual(engine_manifest.package_digest(_TOOLING), engine_pin.ENGINE_PKG_MD5,
                         "add_engine package digest != ENGINE_PKG_MD5 — repin needed")


class DocsParityTest(unittest.TestCase):
    def test_book_trees_byte_identical(self):
        for tracked in (DOCS_CANON, DOCS_BUNDLE):
            self.assertTrue(tracked.is_dir(), f"git-tracked docs tree missing: {tracked}")
        canon = {p.name for p in DOCS_CANON.glob("*.md")}
        bundle = {p.name for p in DOCS_BUNDLE.glob("*.md")}
        self.assertEqual(sorted(canon), sorted(bundle), "book chapter sets diverged")
        for name in sorted(canon):
            digests = {_md5(DOCS_CANON / name), _md5(DOCS_BUNDLE / name)}
            # repo-root mirrors exist only for chapter-shaped names (NN-… /
            # appendix-…) — a generic name like README.md at root is the
            # PROJECT's own file, never a mirror; dogfood docs exists-skip
            extras = [DOCS_DOGFOOD / name]
            if re.match(r"\d{2}-|appendix-", name):
                extras.append(_REPO / name)
            for extra in extras:
                if extra.exists():
                    digests.add(_md5(extra))
            self.assertEqual(len(digests), 1, f"book chapter diverged across trees: {name}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
