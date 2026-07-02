#!/usr/bin/env python3
"""Red/green test — the skill's OWN drafting guides adapt to the new MILESTONE.md.tmpl
UI/UX hint (test_milestone_uiux_hint.py), not just carry it passively.

A template hint alone is not enough — proven live in this project's own history: the
first draft of a real UI/UX-flavored milestone (loop-readability) named its Scope in
generic ADD prose, missing the hint entirely, until a human caught it. So the DRAFTING
GUIDES that actively walk the AI through filling MILESTONE.md/TASK.md must teach
"apply the hint's vocabulary here" explicitly:
  - scope.md (milestone-level Scope drafting) gains a one-line pointer on its
    "Scope In/Out" bullet.
  - phases/1-specify.md (task-level Feature/Must drafting) gains a one-line pointer to
    the SAME vocabulary, via the parent MILESTONE.md's hint (TASK.md.tmpl itself has
    zero `<!--` comment headroom — see test_template_form_tags.py — so the task-level
    guide points at the milestone's hint rather than duplicating the vocabulary).

Both guides sit in the byte-budget-pinned "reference"/"phases" pools
(test_skill_lean.py POOLS) with near-zero headroom (38 B / 46 B measured at the time of
this task) — too little for a meaningful addition, so this is a small, disclosed,
human-directed rebaseline of both pool baselines, mirroring the established
"rebaseline for human-approved new surface" precedent (see the reference pool's own
phase-search-wiring comment in test_skill_lean.py for the identical prior case: a
one-line addition to this SAME file, scope.md).

Run: python3 -m unittest test_skill_uiux_hint_adoption -v
"""
import hashlib
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

CANONICAL_SCOPE = _ADD_METHOD / "skill" / "add" / "scope.md"
DOGFOOD_SCOPE = _REPO / ".claude" / "skills" / "add" / "scope.md"
BUNDLE_SCOPE = _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "scope.md"

CANONICAL_SPECIFY = _ADD_METHOD / "skill" / "add" / "phases" / "1-specify.md"
DOGFOOD_SPECIFY = _REPO / ".claude" / "skills" / "add" / "phases" / "1-specify.md"
BUNDLE_SPECIFY = (_ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add"
                  / "phases" / "1-specify.md")

# the hint the templates carry — scope.md must point drafting AT this, not restate it
HINT_ANCHOR = "Scope hint"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class ScopeMdAdoptsHint(unittest.TestCase):
    def test_scope_in_out_bullet_points_at_the_template_hint(self):
        text = CANONICAL_SCOPE.read_text(encoding="utf-8")
        self.assertIn("Scope In/Out", text)
        bullet_block = text.split("**Scope In/Out**", 1)[1].split("\n- **", 1)[0]
        self.assertIn("UI/UX", bullet_block,
                      "the Scope In/Out drafting bullet must name UI/UX explicitly")
        self.assertIn(HINT_ANCHOR, bullet_block,
                      "must point at the template's OWN hint, not restate the vocabulary")
        self.assertIn("generic", bullet_block,
                      "must warn against generic prose, echoing the hint's own framing")

    def test_mirrors_byte_identical(self):
        digests = {_md5(p) for p in (CANONICAL_SCOPE, DOGFOOD_SCOPE, BUNDLE_SCOPE)}
        self.assertEqual(len(digests), 1, "the 3 scope.md copies must be byte-identical")


class SpecifyMdAdoptsHint(unittest.TestCase):
    def test_specify_points_at_the_milestone_hint(self):
        text = CANONICAL_SPECIFY.read_text(encoding="utf-8")
        # "UI feature" (not "UI/UX") matches this guide's OWN pre-existing phrasing
        # (its design.md trigger a few lines above already says "a UI feature with a screen")
        self.assertIn("UI feature", text,
                      "1-specify.md must name a UI feature explicitly, not stay silent on it")
        self.assertIn("MILESTONE.md", text,
                      "task-level drafting must point at the parent MILESTONE.md's hint "
                      "(TASK.md.tmpl itself has zero comment-budget headroom to carry one)")

    def test_mirrors_byte_identical(self):
        digests = {_md5(p) for p in (CANONICAL_SPECIFY, DOGFOOD_SPECIFY, BUNDLE_SPECIFY)}
        self.assertEqual(len(digests), 1, "the 3 1-specify.md copies must be byte-identical")


if __name__ == "__main__":
    unittest.main(verbosity=2)
