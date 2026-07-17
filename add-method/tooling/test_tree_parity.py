#!/usr/bin/env python3
"""Tree-parity guard: the `add` skill ships in two trees that MUST stay byte-identical —
the canonical `add-method/skill/add/` (packaged + installed by cli.js) and the dogfood
`.claude/skills/add/` (what this repo runs on itself).

Parity was previously asserted file-by-file, ad hoc (glossary, run.md, SKILL.md), which let
`phases/direction.md` drift silently — no test named it. This walks the WHOLE tree and asserts
every file has a byte-identical twin in BOTH directions (no divergence, no orphan either side),
so no skill file can drift unguarded again.

Run: python3 -m unittest test_tree_parity -v
"""
import hashlib
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CANON_SKILL = _ADD_METHOD / "skill" / "add"
DOGFOOD_SKILL = _REPO / ".claude" / "skills" / "add"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _rel_files(root: Path):
    return {p.relative_to(root) for p in root.rglob("*") if p.is_file()}


class TreeParityTest(unittest.TestCase):
    def test_skill_trees_byte_identical(self):
        if not (CANON_SKILL.exists() and DOGFOOD_SKILL.exists()):
            self.skipTest("a skill tree is absent (e.g. fresh package without the dogfood mirror)")
        canon = _rel_files(CANON_SKILL)
        dog = _rel_files(DOGFOOD_SKILL)
        # same file set both ways — catch added/removed files, not just edited ones
        self.assertEqual(
            sorted(map(str, canon)), sorted(map(str, dog)),
            "skill trees have different file sets (orphan files):\n"
            f"  only in canonical: {sorted(map(str, canon - dog))}\n"
            f"  only in dogfood:   {sorted(map(str, dog - canon))}",
        )
        # every shared file byte-identical
        mismatched = [
            str(rel) for rel in sorted(canon, key=str)
            if _md5(CANON_SKILL / rel) != _md5(DOGFOOD_SKILL / rel)
        ]
        self.assertEqual(
            mismatched, [],
            "skill file(s) diverged between canonical and dogfood trees "
            "(propagate with cp):\n  " + "\n  ".join(mismatched),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
