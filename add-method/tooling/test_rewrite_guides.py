"""rewrite-guides §4 suite — both-forms idiom retirement + gate-blind safety-line guards.

Two RED targets (the build drives these green):
  - test_no_idiom_any_form_on_surface : zero hyphen- OR space-form occurrences of any of the
    5 idiom_map idioms anywhere on the lint surface. This is STRONGER than F1, which is
    form-strict — the live escape it closes: `blast-radius` survived in phases/7-observe.md
    while `blast radius` was [enforced] and the lint stayed green.
  - test_idiom_map_fully_enforced     : every idiom_map entry is [enforced] (the promotion
    protocol ran to completion — clarity-greenstate's exit asserts the same).

Three GREEN guards (green at write-time, disclosed in §4 — they pin what NO gate covers):
  - test_protected_safety_lines_pinned : the gate-blind safety negatives stay byte-present
    (5-build.md and 4-tests.md have ZERO inventory entries; 6-verify.md is token-only).
  - test_appendix_b_copies_identical   : the 3 tracked appendix-b copies stay byte-identical
    (no parity test covers them — bundle/tree parity guard skill/add only).
  - test_never_fields_survive          : every `Never:` prompt-field survives the rewrite
    (the negative_keep_list's protected prompt-grammar slot).
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
sys.path.insert(0, str(_TOOLING))

from wording_lint import load_rubric, surface_files  # noqa: E402

_REPO = _TOOLING.parent.parent           # add-method/tooling -> repo root
_SKILL = _TOOLING.parent / "skill" / "add"
_DOCS = _TOOLING.parent / "docs"

# Both written forms (hyphen and space) of every idiom_map idiom, inflection-tolerant,
# bounded like the lint's matcher so substrings ("firewall of") never fire.
_IDIOM_ANY_FORM = [
    ("rubber-stamp", r"(?<![\w-])rubber[-\s]+stamp\w*(?![\w-])"),
    ("wall of", r"(?<![\w-])wall[-\s]+of(?![\w-])"),
    ("collapses to", r"(?<![\w-])collaps\w*[-\s]+to(?![\w-])"),
    ("first feeder", r"(?<![\w-])first[-\s]+feeder\w*(?![\w-])"),
    ("blast radius", r"(?<![\w-])blast[-\s]+radius(?![\w-])"),
]

# The gate-blind safety lines this task must leave byte-present (see module docstring).
_PINNED_SAFETY = {
    _SKILL / "phases" / "5-build.md": (
        "Never weaken or delete a test to make it pass",
        "never edit the frozen",
    ),
    _SKILL / "phases" / "6-verify.md": (
        "always a HARD-STOP and is never auto-passed",
        "A security finding is always `HARD-STOP`, never a waiver.",
    ),
    _SKILL / "phases" / "4-tests.md": (
        "symlink escapes are never read",
    ),
}

# Files carrying a `Never:` prompt-field today — each must still carry one after the rewrite.
_NEVER_FIELD_FILES = (
    _SKILL / "phases" / "1-specify.md",
    _SKILL / "phases" / "2-scenarios.md",
    _SKILL / "phases" / "3-plan.md",
    _SKILL / "phases" / "4-tests.md",
    _SKILL / "phases" / "5-build.md",
    _SKILL / "phases" / "7-observe.md",
    _DOCS / "appendix-b-prompts.md",
)

_APPENDIX_COPIES = (
    _DOCS / "appendix-b-prompts.md",                                        # canonical
    _TOOLING.parent / "src" / "add_method" / "_bundled" / "docs" / "appendix-b-prompts.md",
    _REPO / "appendix-b-prompts.md",                                        # repo root
)


class TestIdiomRetirement(unittest.TestCase):
    """The two RED targets."""

    def test_no_idiom_any_form_on_surface(self) -> None:
        hits: list[str] = []
        for f in surface_files():
            text = f.read_text(encoding="utf-8")
            for name, pattern in _IDIOM_ANY_FORM:
                for i, line in enumerate(text.splitlines(), 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        hits.append(f"{f.name}:{i} [{name}] {line.strip()[:80]}")
        self.assertEqual(hits, [],
                         "idiom occurrences (either written form) survive on the surface:\n  "
                         + "\n  ".join(hits))

    # The five v17 idioms — this core set may never shrink or swap (clarity-greenstate, 2026-06-07).
    V17_IDIOMS = {"blast radius", "collapses to", "first feeder", "rubber-stamp", "wall of"}
    # ubiquitous-language wave (CR-3, ratified by Tin Dang 2026-06-07 at the build decision point):
    # grows ONLY with that task's frozen §3 map — one enumerated addition per landed term commit.
    UBIQUITOUS_IDIOMS = {"on-ramp", "forward spine", "the spine", "state surface", "story surface", "trust layer", "safety net", "blind-spot", "blind spot", "touch-boundary", "touch boundary", "evidence auto-gate", "autonomy dial", "the dial", "lower the dial", "survivor layer", "the survivors", "survivor file", "intake altitude", "milestone altitude", "setup-altitude", "setup altitude", "foundation altitude", "every altitude", "lock-down", "lock down", "competency delta", "least-sure", "least sure", "the seam", "a seam", "decision seam", "freeze seam", "human seam", "seam template", "the fold", "fold ritual", "self-fold", "one-approval front", "the front", "whole front"}

    # autonomy-command wave (ratified by Tin Dang 2026-06-15 at the §3 freeze decision point): the
    # command-shaped "set autonomy:" idiom is retired in favour of the add.py autonomy set verb.
    AUTONOMY_COMMAND_IDIOMS = {"set autonomy:"}

    def test_idiom_map_fully_enforced(self) -> None:
        rubric = load_rubric()
        self.assertEqual(rubric.mapped_idioms, [],
                         f"idiom_map entries still [mapped]: {[i for i, _ in rubric.mapped_idioms]}")
        # named-set equality (additive tightening, clarity-greenstate frozen contract 2026-06-07):
        # count alone passes a delete-one-add-another swap in the map; identity does not.
        expected = self.V17_IDIOMS | self.UBIQUITOUS_IDIOMS | self.AUTONOMY_COMMAND_IDIOMS
        self.assertEqual(set(rubric.enforced_banned), expected,
                         f"enforced_banned must be EXACTLY the ratified idiom set "
                         f"({len(expected)} names), got {sorted(rubric.enforced_banned)}")


class TestGateBlindGuards(unittest.TestCase):
    """The three GREEN guards — green now, pinned so the build cannot drift them."""

    def test_protected_safety_lines_pinned(self) -> None:
        for path, needles in _PINNED_SAFETY.items():
            text = path.read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text,
                              f"{path.name}: protected safety line lost: {needle!r}")

    def test_appendix_b_copies_identical(self) -> None:
        blobs = [(p, p.read_bytes()) for p in _APPENDIX_COPIES]
        canonical_path, canonical = blobs[0]
        for p, blob in blobs[1:]:
            self.assertEqual(blob, canonical,
                             f"appendix-b copy drifted: {p} != {canonical_path}")

    def test_never_fields_survive(self) -> None:
        for path in _NEVER_FIELD_FILES:
            text = path.read_text(encoding="utf-8")
            self.assertIn("Never:", text, f"{path.name}: `Never:` prompt-field lost")
        appendix = (_DOCS / "appendix-b-prompts.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(appendix.count("Never:"), 7,
                                "appendix-b lost `Never:` prompt-fields (had 7 at freeze)")


if __name__ == "__main__":
    unittest.main()
