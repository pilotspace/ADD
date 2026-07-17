#!/usr/bin/env python3
"""Red/green tests for the earned-green rubric (task earned-green-rubric, verify-integrity).

Task 1 (tamper-tripwire) is the MECHANICAL floor: it catches the cheats it can SEE
(an edited test or frozen contract). This task adds the JUDGMENT layer for the cheats
it CANNOT see — the build that makes the UNCHANGED red suite pass without EARNING it:
  - src OVERFIT to the test fixtures (special-cased to the literal inputs)
  - VACUOUS / tautological asserts (green even against an empty implementation)
  - real logic STUBBED away (the function returns a constant the tests accept)
Scored by an INDEPENDENT adversarial refute-read — a reviewer (a subagent under
autonomy:auto is recommended; the engine never spawns one) prompted to argue
"the green was NOT earned". A confirmed earned-green failure is HARD-STOP-class.

This is PROSE + TEMPLATE only (the verify-deepen precedent): add.py is byte-unchanged
(the engine stays judgment-free; the resolver, not the engine, judges earned-vs-gamed).
The rubric is stated IDENTICALLY in the guide (phases/verify.md) and the book
(docs/08-step-6-verify.md), carried as one additive §6 template line, and the two new
terms are defined in the living glossary. ENFORCEMENT (the auto-gate wiring + the
<=3-attempt self-heal loop) is task 3 (heal-then-escalate) — NOT here.

ASCII-safe anchors (house rule): each anchor is a contiguous ASCII substring of the
frozen canonical wording, so drift between surfaces shows up as a missing anchor.

Run: python3 -m unittest test_earned_green_rubric -v
"""
from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

import engine_pin

_TOOLING = Path(__file__).resolve().parent              # add-method/tooling
_ADD_METHOD = _TOOLING.parent                           # add-method
_REPO = _ADD_METHOD.parent                              # repo root

# ── the surfaces (canonical copies) ───────────────────────────────────────────
GUIDE = _ADD_METHOD / "skill" / "add" / "phases" / "verify.md"
BOOK = _ADD_METHOD / "docs" / "08-step-6-verify.md"
RUN_MD = _ADD_METHOD / "skill" / "add" / "run.md"
TASK_TMPL = _ADD_METHOD / "tooling" / "templates" / "PLAN.md.tmpl"
GLOSSARY_TMPL = _ADD_METHOD / "tooling" / "templates" / "GLOSSARY.md.tmpl"
LIVING_GLOSSARY = _REPO / ".add" / "GLOSSARY.md"
ADD_PY = _ADD_METHOD / "tooling" / "add.py"

# ── the mirror trees (every copy — drift in any is a finding) ─────────────────
GUIDE_TREES = [
    GUIDE,                                                                       # canonical
    _REPO / ".claude" / "skills" / "add" / "phases" / "verify.md",            # dogfood
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "verify.md",  # bundle
]
ROOT_BOOK = _REPO / "08-step-6-verify.md"
BOOK_TREES = [
    ROOT_BOOK,                                                                   # root
    BOOK,                                                                        # canonical
]   # book-stops-shipping (2.0 M6b): no bundled/dogfood copies
TMPL_TREES = [
    TASK_TMPL,                                                                   # canonical
    _REPO / ".add" / "tooling" / "templates" / "PLAN.md.tmpl",                  # dogfood
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "PLAN.md.tmpl",  # bundle
]

# Contiguous ASCII substrings of the frozen canonical wording. Each must appear
# VERBATIM (whitespace-collapsed) in BOTH the guide and the book; a missing anchor
# in either is rubric_drift.
EARNED_ANCHORS = [
    "overfit to the test fixtures",
    "vacuous",
    "stubbed away",
    "adversarial refute-read",
    "the green was NOT earned",
    "the engine never spawns one",
    "never auto-passed, never RISK-ACCEPTED",
]

# The three judgment cheats must be NAMED (per-surface keyword presence).
CHEAT_KEYWORDS = ["overfit", "vacuous", "stub"]

# Pre-existing section-6 template lines the additive change must NOT remove
# (a subset re-checked here so this guard fails loudly on a seam break).
SIX_EXISTING = [
    "all tests pass",
    "no test or contract was altered during build",
    "### Deep checks",
    "### GATE RECORD",
]

# heal-then-escalate (task 3) LANDED the bounded self-heal loop. Its home is run.md (the
# build->verify run guide); the verify guide POINTS to it. The earlier "these tokens must NOT
# leak into the task-2 rubric" absence-list is superseded by the presence guard below — once
# task 3 exists, the loop is documented reality, not a future-task token to keep out.
LOOP_ANCHORS_RUN_MD = ["self-heal", "escalat"]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _norm(text: str) -> str:
    """Collapse all whitespace (incl. markdown hard-wraps) to single spaces.

    "Stated identically" means the same WORDING, not the same line breaks — each
    surface wraps the canonical sentence at its own column.
    """
    return " ".join(text.split())


def _paired_tags(text: str) -> set[str]:
    """The set of paired <tag>…</tag> names in a markdown file (code fences stripped)."""
    no_fence = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    opens = set(re.findall(r"<([a-z_]+)>", no_fence))
    closes = set(re.findall(r"</([a-z_]+)>", no_fence))
    return opens & closes


class EarnedGreenRubricTest(unittest.TestCase):

    # ── per-surface content ───────────────────────────────────────────────────
    def test_guide_names_three_cheats(self):
        text = GUIDE.read_text(encoding="utf-8")
        for kw in CHEAT_KEYWORDS:
            self.assertIn(kw, text, f"the guide must name the '{kw}' cheat")

    def test_guide_requires_refute_read(self):
        # _norm collapses markdown hard-wraps: the anchor is a word-sequence, not a
        # literal-with-newlines (the same invariant test_verify_deepen documents).
        text = _norm(GUIDE.read_text(encoding="utf-8"))
        self.assertIn("adversarial refute-read", text)
        self.assertIn("the green was NOT earned", text)
        self.assertIn("the engine never spawns one", text,
                      "the refute-read is a recommendation; the engine never spawns it")

    def test_book_has_rubric(self):
        text = _norm(BOOK.read_text(encoding="utf-8"))
        for kw in CHEAT_KEYWORDS:
            self.assertIn(kw, text, f"the book must name the '{kw}' cheat")
        self.assertIn("adversarial refute-read", text)

    # ── stated identically across guide + book (rubric_drift) ─────────────────
    def test_rubric_stated_identically(self):
        surfaces = {
            "guide": _norm(GUIDE.read_text(encoding="utf-8")),
            "book": _norm(BOOK.read_text(encoding="utf-8")),
        }
        for anchor in EARNED_ANCHORS:
            a = _norm(anchor)
            for name, text in surfaces.items():
                self.assertIn(a, text,
                              f"rubric_drift: earned-green anchor missing from {name}: {anchor!r}")

    # ── the §6 template line (additive) ───────────────────────────────────────
    def test_template_earned_green_additive(self):
        text = TASK_TMPL.read_text(encoding="utf-8")
        six = text.split("## 6 ")[1].split("## 7 ")[0]
        self.assertIn("earned", six.lower(), "the §6 template must carry an earned-green check line")
        # the new line sits inside section 6, before the gate record
        self.assertLess(six.lower().index("earned"), six.index("### GATE RECORD"),
                        "the earned-green line must precede the GATE RECORD")
        for line in SIX_EXISTING:
            self.assertIn(line, text, f"seam_broken: existing section-6 line vanished: {line!r}")

    # ── the glossary terms + the single-source pointer ────────────────────────
    def test_glossary_defines_terms_and_points_runmd(self):
        checked = 0
        for path in (GLOSSARY_TMPL, LIVING_GLOSSARY):
            if not path.exists():
                continue
            checked += 1
            low = path.read_text(encoding="utf-8").lower()
            self.assertIn("earned green", low, f"{path.name} must define 'earned green'")
            self.assertIn("adversarial refute-read", low,
                          f"{path.name} must define 'adversarial refute-read'")
            self.assertIn("adversarial verify", low,
                          f"{path.name}: the refute-read must POINT to run.md's adversarial verify")
        self.assertGreater(checked, 0, "no glossary present to check")

    # ── the loop is homed in run.md; the verify guide points (separation guard) ──
    def test_loop_homed_in_run_md_verify_guide_points(self):
        """heal-then-escalate LANDED the bounded self-heal loop — this supersedes the task-2
        forward-reference absence-check (whose premise, 'task 2 must not pre-empt task 3', is
        now FULFILLED). Separation guard: the loop's machinery lives in run.md (its home, the
        build->verify run); the verify guide STATES the HARD-STOP principle and POINTS to
        run.md. Coverage goes UP — this now guards run.md's loop presence, which the
        absence-check never did."""
        run_low = _norm(RUN_MD.read_text(encoding="utf-8")).lower()
        for anchor in LOOP_ANCHORS_RUN_MD:
            self.assertIn(anchor, run_low,
                          f"the bounded self-heal loop must be documented in run.md: {anchor!r}")
        guide = GUIDE.read_text(encoding="utf-8")
        self.assertIn("HARD-STOP", guide, "the verify guide still states the HARD-STOP principle")
        self.assertIn("run.md", guide, "the verify guide POINTS to run.md for the loop")

    # ── the rubric stays out of the engine (the engine names the channel, not the cheats) ──

    # ── the guide adds no off-vocabulary XML tag (vocab_offmidiom) ────────────
    def test_guide_vocab_subset(self):
        tags = _paired_tags(GUIDE.read_text(encoding="utf-8"))
        offenders = tags - {"prompt", "output_format", "exit_gate"}
        self.assertFalse(offenders, f"6-verify.md introduced off-subset tags {sorted(offenders)}")

    # ── every mirror carries the rubric; no stale root (mirror_drift) ─────────
    def test_all_skill_trees_carry_anchors(self):
        present = [p for p in GUIDE_TREES if p.exists()]
        self.assertGreaterEqual(len(present), 2, "fewer than two skill trees present")
        for p in present:
            text = _norm(p.read_text(encoding="utf-8"))
            self.assertIn("adversarial refute-read", text, f"guide mirror missing rubric: {p}")
            self.assertIn("overfit", text, f"guide mirror missing cheats: {p}")

    def test_all_book_trees_carry_anchors(self):
        present = [p for p in BOOK_TREES if p.exists()]
        self.assertGreaterEqual(len(present), 2, "fewer than two book trees present")
        for p in present:
            text = _norm(p.read_text(encoding="utf-8"))
            self.assertIn("adversarial refute-read", text, f"book mirror missing rubric: {p}")
            self.assertIn("overfit", text, f"book mirror missing cheats: {p}")

    def test_root_book_matches_canonical(self):
        if not (ROOT_BOOK.exists() and BOOK.exists()):
            self.skipTest("root or canonical book copy absent")
        self.assertEqual(_md5(ROOT_BOOK), _md5(BOOK),
                         "mirror_drift: root ./08-step-6-verify.md diverged from canonical "
                         "(08 is not a woven chapter — this task adds the root<->canonical guard)")

    def test_rubric_stays_out_of_engine(self):
        # the JUDGMENT RUBRIC — the specific cheats and how to spot them — never
        # lives in the engine; it lives in the verify guide. The heal channel may
        # carry its source LABEL ("refute-read"), but the engine never re-teaches
        # the cheats. (Tree parity + the engine pin live in test_tree_parity.)
        src = ADD_PY.read_text(encoding="utf-8")
        for cheat in ("overfit", "vacuous", "stubbed-away"):
            self.assertNotIn(cheat, src,
                             f"the earned-green rubric vocab must stay out of the engine: {cheat!r}")
        self.assertNotIn("the green was NOT earned", src,
                         "the refute-read PROMPT is a guide artifact, never the engine")


if __name__ == "__main__":
    unittest.main(verbosity=2)
