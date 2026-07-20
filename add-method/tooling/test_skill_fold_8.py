#!/usr/bin/env python3
"""Red/green tests for skill-fold-8 (ADD 2.0 M4 skill-unify, commit B).

CONTRACT: the eight zero-engine-mention guides fold into their beat homes and
the files are DELETED from all three skill trees — the on-demand pool shrinks
from 25 to 17 files with no teaching lost:

  scope.md · confidence.md        -> phases/direction.md
  advisor.md · sensitivity.md     -> phases/verify.md
  self-improve.md                 -> phases/build.md
  soul.md                         -> deltas.md
  setup-review.md                 -> adopt.md
  components.md                   -> deleted (beyond.md re-aims to the book
                                     chapter + the platform personas)

- Every fold keeps its externally-pinned teaching (the migrated original
  suites keep their full pins after their path re-aim; this suite pins one
  representative anchor per fold so a lost teaching fails HERE too).
- No stale pointers: no *.md in any skill tree cites a deleted name.
- The byte fences hold: phases/ pool stays under its 33,496B ceiling
  (test_skill_loop_fold) and the orchestration pool — advisor.md leaves it —
  re-pins at 41300 minus advisor's bytes (never a weakened floor).

Run: python3 -m unittest test_skill_fold_8 -v
"""
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SKILL_TREES = (
    REPO / "add-method" / "skill" / "add",
    REPO / ".claude" / "skills" / "add",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "skill" / "add",
)
DELETED = ("scope.md", "confidence.md", "advisor.md", "sensitivity.md",
           "self-improve.md", "soul.md", "setup-review.md", "components.md",
           # kernel-trim (ADD 2.0 M5): the platform guides died with their verbs —
           # the playbooks live in the seed personas now
           "streams.md", "release.md", "graduate.md", "fold.md", "compact-foundation.md")

# one representative teaching per fold, pinned in its NEW home
ANCHORS = {
    "phases/direction.md": (
        "## Ground",                          # scope.md: the milestone Ground section
        "Confirm before create is the convention",
        "advisory, never a gate",             # confidence.md: the hard rule
        "< 0.9",                              # confidence.md: the refine threshold
    ),
    "phases/verify.md": (
        "Code-Reviewer",                      # advisor.md: refute-read persona map
        "never lowers a gate",                # advisor.md: the floor
        "<strategy>",                         # advisor.md: the worker-contract block
        "value formats are the risk surface", # sensitivity.md: the datetime/money rule
        "sensitivity_invalid",                # sensitivity.md: the reject code
    ),
    "phases/build.md": (
        "nothing self-approves",              # self-improve.md: the one map's floor
    ),
    "deltas.md": (
        "[VOICE",                             # soul.md: the voice-delta grammar
        "unconfirmed_voice_rewrite",          # soul.md: the reject floor
    ),
    "adopt.md": (
        "SETUP-REVIEW.md",                    # setup-review.md: the artifact
        "confirm in chat",                    # setup-review.md: the sign row
        "lowest-confidence-first",            # setup-review.md: the ordering rule
    ),
    "beyond.md": (
        "stream-orchestrator persona",        # streams.md: the playbook's new owner
        "release-manager persona",            # release.md: the cut playbook's owner
        "platform-engineer seed persona",     # components: the monorepo playbook's owner
    ),
}


def _trees():
    return [t for t in SKILL_TREES if (t / "SKILL.md").exists()]


class FoldedFilesGone(unittest.TestCase):
    # Must: the eight sources are deleted from every tree
    def test_deleted_everywhere(self):
        for tree in _trees():
            for name in DELETED:
                self.assertFalse((tree / name).exists(),
                                 f"folded guide must not survive: {tree / name}")


class TeachingsSurvive(unittest.TestCase):
    # Must: one representative anchor per fold lives in its new home
    def test_anchors_in_new_homes(self):
        base = SKILL_TREES[0]
        for fname, anchors in ANCHORS.items():
            body = (base / fname).read_text(encoding="utf-8")
            for a in anchors:
                self.assertIn(a, body, f"anchor_dropped: {a!r} must live in {fname}")


class NoStalePointers(unittest.TestCase):
    # Reject: no surviving guide cites a deleted filename. Word-boundary match —
    # `docs/17-components.md` (the book chapter) is NOT a citation of the deleted
    # skill guide `components.md`.
    def test_no_references_to_deleted(self):
        for tree in _trees():
            for p in tree.rglob("*.md"):
                body = p.read_text(encoding="utf-8")
                for name in DELETED:
                    pat = r"(?<![\w/-])" + re.escape(name)
                    hit = re.search(pat, body)
                    self.assertIsNone(hit,
                                      f"stale pointer: {p} still cites {name}")


class ByteFences(unittest.TestCase):
    # Floor: the phases/ pool ceiling holds after the folds land
    def test_phases_pool_under_ceiling(self):
        pool = sum(p.stat().st_size for p in (SKILL_TREES[0] / "phases").glob("*.md"))
        self.assertLess(pool, 33496, f"phases/ pool must stay under 33496B (now {pool}B)")


if __name__ == "__main__":
    unittest.main()
