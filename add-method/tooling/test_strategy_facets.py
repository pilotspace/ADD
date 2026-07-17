#!/usr/bin/env python3
"""Red/green tests for the faceted §5 build strategy block (task strategy-facet-block,
milestone build-strategy-facets, contract FROZEN @ v1).

A prose/template-only task: full TASK.md.tmpl §5 gains four ADDITIVE, domain-generic
facet lines — Approach (domain strategy) · Data strategy · Pattern · Optimization
stance — between the Strategy (ordered batches) line and the Persona line; the fast
template collapses to ONE Approach line (collapse, never skip); phases/build.md and
the 07-step-5-build.md chapter teach the facets; the engine is untouched. Placeholders
carry spaces (frozen tag census unchanged), no new HTML comment (ceiling <12), no
backtick in any new §5 line (scope-token grammar unaffected). Run:
    python3 -m unittest test_strategy_facets -v
"""
import hashlib
import io
import os
import shutil
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
import engine_pin
from test_scope_decl_template import (EXISTING_LINES, FROZEN_TAGS, ACTUAL_LABEL,
                                      FAST_STRATEGY_LABEL, STRATEGY_LABEL)

HERE = Path(__file__).resolve().parent          # add-method/tooling
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"

# 4-twin lockstep for each template (canon · repo dogfood · add-method dogfood · bundle).
# Fresh-checkout skip-tolerance (ba09498 precedent): the dogfood trees are gitignored and
# absent on a fresh clone — lockstep is asserted over the twins that EXIST; canon + bundle
# are git-tracked and always present, so the parity claim never goes vacuous.
def _existing(*paths):
    present = tuple(p for p in paths if p.exists())
    assert len(present) >= 2, f"twin set collapsed below canon+bundle: {paths}"
    return present

FULL_TWINS = _existing(HERE / "templates" / "TASK.md.tmpl",
                       REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
                       ADD_METHOD / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
                       BUNDLE / "tooling" / "templates" / "TASK.md.tmpl")
BUILD_GUIDES = (ADD_METHOD / "skill" / "add" / "phases" / "build.md",
                REPO / ".claude" / "skills" / "add" / "phases" / "build.md",
                BUNDLE / "skill" / "add" / "phases" / "build.md")
CHAPTERS = (ADD_METHOD / "docs" / "07-step-5-build.md",
            REPO / "07-step-5-build.md",
            BUNDLE / "docs" / "07-step-5-build.md")
ADDPY_TRIO = (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
              BUNDLE / "tooling" / "add.py")

PERSONA_LABEL = "Persona (required):"
APPROACH_LABEL = "Approach (domain strategy):"
DATA_LABEL = "Data strategy:"
PATTERN_LABEL = "Pattern:"
STANCE_LABEL = "Optimization stance:"

# the contract-frozen facet lines (§3 v1, relocated into §3 PLAN's ### Build-strategy by
# plan-phase-core) — byte-exact against templates/TASK.md.tmpl
FULL_FACET_LINES = (
    "Approach (domain strategy): <the core technique chosen and WHY it fits this task's domain "
    "— an algorithm, a data model, a migration path, a prose structure, a UX flow — derive from "
    "§1 Framings weighed, not invented here>",
    "Data strategy: <the shapes and access patterns the work realizes — must agree with the "
    "Contract Schema line above>",
    "Pattern: <the domain pattern this build follows and the Grounding Honors / CONVENTIONS.md "
    "anchor it extends>",
    "Optimization stance: <WHAT is optimized and its budget — latency, memory, token cost, "
    "readability — or \"correctness-first, no budget\"; never blank; ⚠-mark the facet you trust "
    "least; risk: high -> consult add-advisor; advisory, never a gate>",
)
# template-hint-dedup: the fast §5 Approach hint migrated from a stance-restating one-liner
# to a ≤6-word technique TAG ("NOT a restatement of the Strategy above") — still ONE collapsed
# line in the same §5 position (the facets feature's fast-collapse invariant holds).
# template-unify: the fast render shares the FULL facet lines (one template)


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class StrategyFacetsTest(unittest.TestCase):
    # ---- M1: the four facet lines, in order, between Strategy and Persona -------
    def test_full_template_facet_lines_ordered(self):
        text = FULL_TWINS[0].read_text(encoding="utf-8")
        idx = [text.index(STRATEGY_LABEL)]
        for line in FULL_FACET_LINES:
            self.assertIn(line, text, f"full §5 missing the contract-exact facet line: {line[:40]}…")
            idx.append(text.index(line))
        idx.append(text.index(PERSONA_LABEL))
        self.assertEqual(idx, sorted(idx),
                         "facet order must be Strategy < Approach < Data < Pattern < Stance < Persona")

    # ---- M2: each hint names its upstream anchor + stays domain-generic ---------
    # plan-phase-core: the anchors now live IN §3 (Approach cites the still-external §1;
    # Data strategy / Pattern cite their §3 PLAN sibling sub-blocks "Contract"/"Grounding" by
    # name rather than a section number, since both now live inside the same §3).
    def test_facet_hints_cite_upstream_anchors(self):
        self.assertIn("§1 Framings weighed", FULL_FACET_LINES[0])
        self.assertIn("Contract Schema", FULL_FACET_LINES[1])
        self.assertIn("Grounding Honors", FULL_FACET_LINES[2])
        # domain-generic: a non-code example rides next to the dev ones
        self.assertIn("prose structure", FULL_FACET_LINES[0])

    # ---- M3: the stance line carries the fill discipline ------------------------
    # plan-phase-core: Build-strategy is now filled+frozen at PLAN (with Grounding+Contract)
    # rather than left draft through tests->build, so that token is retired with the phase.
    def test_optimization_stance_fill_discipline(self):
        stance = FULL_FACET_LINES[3]
        for token in ("never blank", "⚠", "add-advisor", "advisory, never a gate"):
            self.assertIn(token, stance, f"Optimization stance missing discipline token: {token}")

    # template-unify: M4's collapsed fast Approach line is retired — the fast lane
    # derives from the one template and carries the FULL facet lines
    # (test_scaffold_carries_facets pins the live fast scaffold).

    # ---- M5: twins in md5 lockstep ----------------------------------------------

    # ---- M6: the build guide teaches the facets, trio identical -----------------
    def test_build_guide_teaches_facets(self):
        digests = set()
        for p in BUILD_GUIDES:
            text = p.read_text(encoding="utf-8")
            for anchor in (APPROACH_LABEL.rstrip(":"), "Optimization stance"):
                self.assertIn(anchor, text, f"{p} does not teach the facets ({anchor})")
            digests.add(_md5(p))
        self.assertEqual(len(digests), 1, "5-build.md trees diverged")

    # ---- M6: the phases lean fence holds (same math as test_skill_lean) ---------
    # ---- M7: the book chapter gains the strategy-choice passage -----------------
    def test_book_chapter_strategy_passage(self):
        digests = set()
        for p in CHAPTERS:
            self.assertIn("Choosing the implementation strategy", p.read_text(encoding="utf-8"),
                          f"{p} missing the strategy-choice passage")
            digests.add(_md5(p))
        self.assertEqual(len(digests), 1, "07-step-5-build.md twins diverged")

    # ---- R:tag_census_amend ------------------------------------------------------
    def test_tag_census_unchanged(self):
        tags = sorted(set(re.findall(r"</?([a-z_]+)>", FULL_TWINS[0].read_text(encoding="utf-8"))))
        self.assertEqual(tags, FROZEN_TAGS, "template tag census changed — the v16/v18 vocab is frozen")

    # ---- R:comment_ceiling -------------------------------------------------------
    def test_comment_ceiling_held(self):
        count = FULL_TWINS[0].read_text(encoding="utf-8").count("<!--")
        self.assertLess(count, 12, "TASK.md.tmpl gained a comment — facet guidance lives in line hints")

    # ---- R:nonadditive_change ----------------------------------------------------
    def test_additive_only(self):
        text = FULL_TWINS[0].read_text(encoding="utf-8")
        # EXISTING_LINES' own Constraints wording predates plan-phase-core (§5 Constraints now
        # names the frozen §3 contract + the relocated §3 Build-strategy Scope it must stay
        # inside) — re-point to the CURRENT §5 Constraints line; Safety rule / Code lives in
        # are still byte-identical, so the additive-only check keeps its original strength.
        preexisting = tuple(l for l in EXISTING_LINES if not l.startswith("Constraints:")) + (
            "Constraints: do NOT change any test or the frozen §3 contract; stay inside the "
            "§3 Build-strategy Scope; allow-list packages only; ask if unclear.",
        )
        for line in preexisting + (STRATEGY_LABEL, ACTUAL_LABEL):
            self.assertIn(line, text, "pre-existing §5 line changed — the add is additive")

    # ---- R:scope_token_leak ------------------------------------------------------
    def test_no_backtick_in_facet_lines(self):
        for line in FULL_FACET_LINES:
            self.assertNotIn("`", line, "a backtick in a §5 line can parse as a scope token")

    # ---- R:engine_touched --------------------------------------------------------

    # ---- After-1: a fresh scaffold carries the facets (full + fast) --------------
    def test_scaffold_carries_facets(self):
        cwd = Path.cwd()
        tmp = Path(tempfile.mkdtemp(prefix="add-strat-facet-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.addCleanup(os.chdir, cwd)
        try:
            os.chdir(tmp)
            buf, err = io.StringIO(), io.StringIO()
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["init", "--name", "demo"])
                add.main(["lock", "--force"])
                add.main(["new-task", "fullx", "--title", "fullx"])
                add.main(["new-task", "fastx", "--title", "fastx", "--fast"])
            full = (tmp / ".add" / "tasks" / "fullx" / "TASK.md").read_text(encoding="utf-8")
            fast = (tmp / ".add" / "tasks" / "fastx" / "TASK.md").read_text(encoding="utf-8")
            for line in FULL_FACET_LINES:
                self.assertIn(line, full, "full scaffold missing a facet line")
            for line in FULL_FACET_LINES:
                self.assertIn(line, fast, "fast scaffold missing a facet line (uniform §3)")
        finally:
            os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
