"""Red→green guard for compact-guide §3 (FROZEN @ v1).

compact-foundation.md (the convention-guided ritual, one section per spec) realizing the frozen
compaction-contract, byte-identical across the 3 skill homes, plus a SKILL.md milestone-close cue.
Engine untouched (convention-guided seam).

unittest (repo convention). RED before build: the guide + the SKILL cue do not exist yet.
"""
import hashlib
import os
import re
import unittest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

_GUIDE = "{}/add/compact-foundation.md"
_GUIDE_HOMES = [
    "add-method/skill/add/compact-foundation.md",
    "add-method/src/add_method/_bundled/skill/add/compact-foundation.md",
    ".claude/skills/add/compact-foundation.md",
]
_SKILL_HOMES = [
    "add-method/skill/add/SKILL.md",
    "add-method/src/add_method/_bundled/skill/add/SKILL.md",
    ".claude/skills/add/SKILL.md",
]
_ENGINES = ["add-method/tooling/add.py", ".add/tooling/add.py"]
_REJECTS = ["open-residue-version", "trail-loss", "wrong-order"]
_SPEC_SECTIONS = ["project.md §spec", "project.md §key-decisions", "conventions.md", "glossary.md", "model_registry.md"]


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def _exists(rel):
    return os.path.exists(os.path.join(_ROOT, rel))


def _norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


class CompactGuideTest(unittest.TestCase):
    def _guide(self):
        if not _exists(_GUIDE_HOMES[0]):
            self.fail("compact-foundation.md missing — build has not run (expected RED pre-build)")
        return _norm(_read(_GUIDE_HOMES[0]))

    def test_guide_exists_3_homes(self):
        for home in _GUIDE_HOMES:
            self.assertTrue(_exists(home), f"compact-foundation.md missing at {home}")

    def test_guide_mirror_parity(self):
        if not all(_exists(h) for h in _GUIDE_HOMES):
            self.fail("compact-foundation.md missing in a home (expected RED pre-build)")
        d = {h: hashlib.md5(_read(h).encode("utf-8")).hexdigest() for h in _GUIDE_HOMES}
        self.assertEqual(len(set(d.values())), 1, f"compact-foundation.md homes diverged (mirror-drift): {d}")

    def test_per_spec_sections(self):
        t = self._guide()
        for spec in _SPEC_SECTIONS:
            self.assertIn(spec, t, f"no rolled-line section for {spec}")

    def test_ritual_realizes_contract(self):
        t = self._guide()
        self.assertIn("shipped", t, "eligibility (shipped) missing")
        self.assertTrue(re.search(r"zero open residues|no open residue", t), "eligibility (zero open residues) missing")
        self.assertIn("newest-first", t, "newest-first ordering missing")
        self.assertTrue("tail" in t or "bottom" in t, "settled line at the tail/bottom missing")
        self.assertIn("never delete", t, "preservation (never delete) missing")
        self.assertIn("git", t, "preservation (git pointer) missing")
        for code in _REJECTS:
            self.assertIn(code, t, f"reject code missing: {code}")

    def test_skill_cue_3_homes(self):
        for home in _SKILL_HOMES:
            t = _norm(_read(home))
            self.assertIn("compact-foundation.md", t, f"{home}: no milestone-close cue to compact-foundation.md")
            self.assertIn("fold.md", t, f"{home}: the fold cue should remain (compaction follows fold)")
        digests = {h: hashlib.md5(_read(h).encode("utf-8")).hexdigest() for h in _SKILL_HOMES}
        self.assertEqual(len(set(digests.values())), 1, f"SKILL.md homes diverged (mirror-drift): {digests}")

    def test_no_engine_creep(self):
        for eng in _ENGINES:
            src = _read(eng)
            for code in _REJECTS:
                self.assertNotIn(code, src, f"{eng}: engine enforces '{code}' — violates the convention-guided seam")
            self.assertNotIn("compact-foundation", src, f"{eng}: engine references the guide — convention-guided seam broken")


if __name__ == "__main__":
    unittest.main()
