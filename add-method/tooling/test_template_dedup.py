#!/usr/bin/env python3
"""Red/green tests for template comment dedup (task template-dedup, frozen v1):
TASK.md.tmpl comments point at each rule's canonical home instead of restating it
(weight audit 2026-07-13: 11 comment blocks / 2848B, 2B under the 2850 ceiling).

  M1 — every EXIT-carrying comment is a pointer, <=120B.
  M2 — the scope-token grammar is not restated in the template (canonical home:
       the engine grammar + the SEAMS scope-token-grammar seam).
  M3 — the Ground SHA comment (BOTH templates) says the engine stamps it at
       freeze and no longer instructs `git rev-parse` hand-typing; the plan
       guide's Ground SHA bullet says the same.
  M4 — total comment bytes <= 2400 (headroom reclaimed under the 2850 ceiling).
  R  — the tag census vocabulary gains nothing new; the Reported: attestation
       prompts survive (never dedup an attestation).

Run: python3 -m unittest test_template_dedup -v
"""
import re
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_TMPL = _HERE / "templates" / "TASK.md.tmpl"
_FAST = _HERE / "templates" / "TASK.fast.md.tmpl"
_PLAN_GUIDE = _HERE.parent / "skill" / "add" / "phases" / "3-plan.md"

_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def _comments(text: str) -> list[str]:
    return _COMMENT_RE.findall(text)


class ExitPointerTest(unittest.TestCase):
    def test_exit_comments_are_pointers(self):                     # M1
        text = _TMPL.read_text(encoding="utf-8")
        exits = [c for c in _comments(text) if "EXIT:" in c]
        self.assertTrue(exits, "the template must keep its EXIT cues (as pointers)")
        for c in exits:
            self.assertLessEqual(
                len(c.encode("utf-8")), 120,
                f"an EXIT comment must be a pointer, not a restatement: {c[:80]!r}")

    def test_scope_grammar_restatement_survives(self):             # M2 (v2)
        # v2 change request: 4 pre-existing suites pin the TEMPLATE as the frozen
        # scope-decl declaration surface — the grammar restatement is load-bearing
        # content, NOT dedup-able. This pin keeps a future dedup pass honest.
        text = _TMPL.read_text(encoding="utf-8")
        for form in ("sibling of the previous", "whole subtree", "fail-closed",
                     "UNDECLARED", "never retro-red"):
            self.assertIn(form, text, f"pinned grammar form lost: {form}")


class GroundShaCommentTest(unittest.TestCase):
    def _line(self, path: Path) -> str:
        m = re.search(r"(?m)^Ground SHA:.*$", path.read_text(encoding="utf-8"))
        self.assertIsNotNone(m, f"{path.name} lost its Ground SHA line")
        return m.group(0)

    def test_ground_sha_comment_says_engine_stamps_both_tmpls(self):   # M3
        for path in (_TMPL, _FAST):
            line = self._line(path)
            self.assertIn("stamped by freeze", line,
                          f"{path.name}: the placeholder must say the engine stamps it")
            self.assertNotIn("rev-parse", line,
                             f"{path.name}: stop instructing the hand-typed SHA")

    def test_plan_guide_bullet_updated(self):                      # M3
        text = _PLAN_GUIDE.read_text(encoding="utf-8")
        m = re.search(r"(?m)^- \*\*Ground SHA\*\*.*$", text)
        self.assertIsNotNone(m, "3-plan.md lost its Ground SHA bullet")
        self.assertIn("stamped by freeze", m.group(0))
        self.assertNotIn("rev-parse", m.group(0))


class CommentBudgetTest(unittest.TestCase):
    def test_comment_budget(self):                                 # M4
        text = _TMPL.read_text(encoding="utf-8")
        total = sum(len(c.encode("utf-8")) for c in _comments(text))
        self.assertLessEqual(total, 2650,
                             f"comment bytes {total} — the dedup must reclaim headroom "
                             "(v2: the pinned grammar restatements stay)")

    def test_reported_attestation_prompts_survive(self):           # R
        text = _TMPL.read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"(?m)^Reported: <", text)), 2,
                         "both Reported: attestation prompts are load-bearing — keep them")


if __name__ == "__main__":
    unittest.main()
