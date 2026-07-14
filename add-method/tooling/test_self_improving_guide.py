"""self-improving-guide (self-improving-loop): one map of how ADD improves itself.

CONTRACT (frozen @ v1):
  `skill/add/self-improve.md` (NEW, unpooled — tree census only) maps the four
  self-improving artifacts (foundation · personas · SOUL.md · next scope) with each one's
  emit grammar and consolidator, routes all 5 domains, names how the 8 steps feed observe,
  and POINTS at the mechanics guides without duplicating their rules. 6-verify.md points
  at it. Whole-tree + phases budgets hold; 3 skill trees stay byte-identical.
Run: python3 -m unittest test_self_improving_guide -v
"""
import hashlib
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
TREES = (ADD_METHOD / "skill" / "add",
         REPO / ".claude" / "skills" / "add",
         ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add")


def _map_text() -> str:
    return (TREES[0] / "self-improve.md").read_text(encoding="utf-8")


class MapNamesFourArtifacts(unittest.TestCase):
    def test_artifacts_with_consolidators(self):                   # M1
        t = _map_text()
        for token in ("PROJECT.md", "personas", "SOUL.md", "SPEC"):
            self.assertIn(token, t, f"the map misses the artifact: {token}")
        self.assertIn("fold", t, "the map must name the consolidator command")
        self.assertIn("(evidence:", t, "the map must show the evidence-closed grammar")


class MapCoversDomainsAndSteps(unittest.TestCase):
    def test_five_domains(self):                                   # M2
        t = _map_text()
        for tag in ("DDD", "SDD", "UDD", "TDD", "ADD"):
            self.assertIn(tag, t, f"the map misses the domain: {tag}")

    def test_eight_steps_feed_observe(self):                       # M2
        t = _map_text().lower()
        for feed in ("ground", "freeze", "red", "build", "verify", "observe"):
            self.assertIn(feed, t, f"the map misses the step feed: {feed}")


class MapPointsNeverDuplicates(unittest.TestCase):
    def test_points_at_mechanics(self):                            # M3
        t = _map_text()
        for guide in ("deltas.md", "fold.md", "compact-foundation.md", "soul.md",
                      "confidence.md"):
            self.assertIn(guide, t, f"the map must point at {guide}")
        self.assertIn("carried:", t, "the map must name the status accumulation cues")
        self.assertIn("compaction:", t)

    def test_no_duplicated_reject_codes(self):                     # M3
        t = _map_text()
        for code in ("no_open_deltas", "missing_route_section", "persona_clobber_forbidden"):
            self.assertNotIn(code, t, "the map must POINT at fold.md, not copy its rejects")


class ObservePointsAtMap(unittest.TestCase):
    def test_observe_next_points_here(self):                       # M4
        # guide-recut: the Observe duties live in 6-verify.md's post-gate block now
        t = (TREES[0] / "phases" / "6-verify.md").read_text(encoding="utf-8")
        self.assertIn("self-improve.md", t, "6-verify.md must point at the map")


class BudgetsAndParity(unittest.TestCase):
    def test_tree_and_phases_budgets_hold(self):                   # R1+R2
        import test_skill_lean as tsl
        nbytes = sum(len(p.read_bytes()) for p in tsl._CANON.rglob("*.md"))
        self.assertLessEqual(nbytes, tsl.TREE_TARGET_BYTES, "whole-tree census bust")
        pool = next(p for p in tsl.POOLS if p["name"] == "phases")
        n = sum(len((tsl._CANON / g).read_bytes())
                for g in pool["guides"] if (tsl._CANON / g).exists())
        self.assertLessEqual(n, int(pool["baseline"] * pool["ratio"]), "phases pool bust")

    def test_three_tree_parity(self):                              # R3
        for name in ("self-improve.md", "phases/6-verify.md"):
            digests = {hashlib.md5((tree / name).read_bytes()).hexdigest()
                       for tree in TREES}
            self.assertEqual(len(digests), 1, f"{name} drifted across skill trees")


if __name__ == "__main__":
    unittest.main()
