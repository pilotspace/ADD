#!/usr/bin/env python3
"""Red/green tests for the §5 scope-of-impact declaration (task scope-decl-template,
milestone build-scope-lock).

A prose/template-only task: §5 of TASK.md.tmpl gains the `Scope (may touch):`
allowlist + `Strategy (ordered batches):` plan lines and a grammar comment;
phases/5-build.md teaches the discipline (declare-at-bundle · freeze-at-contract
· honor-or-change-request · the scope-gate-enforce deferral NAMED); one line in
phases/3-contract.md says the freeze covers them. Content anchors prove the
words exist (the folded prose-guides-are-TDD-able convention); add.py is
untouched — a guard asserts it, plus the template's tag census stays frozen
(v16 vocab: no new XML tag). Run:
    python3 -m unittest test_scope_decl_template -v
"""
import hashlib
import io
import os
import re
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
import engine_pin

HERE = Path(__file__).resolve().parent          # add-method/tooling
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"

CANON_TMPL = HERE / "templates" / "TASK.md.tmpl"
DOG_TMPL = REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl"
BUNDLE_TMPL = BUNDLE / "tooling" / "templates" / "TASK.md.tmpl"

# fast-lane template trio (build-strategy-solutions ADD-2)
CANON_FAST = HERE / "templates" / "TASK.fast.md.tmpl"
DOG_FAST = REPO / ".add" / "tooling" / "templates" / "TASK.fast.md.tmpl"
BUNDLE_FAST = BUNDLE / "tooling" / "templates" / "TASK.fast.md.tmpl"

CANON_BUILD = ADD_METHOD / "skill" / "add" / "phases" / "5-build.md"
DOG_BUILD = REPO / ".claude" / "skills" / "add" / "phases" / "5-build.md"
BUNDLE_BUILD = BUNDLE / "skill" / "add" / "phases" / "5-build.md"

CANON_CONTRACT = ADD_METHOD / "skill" / "add" / "phases" / "3-contract.md"
DOG_CONTRACT = REPO / ".claude" / "skills" / "add" / "phases" / "3-contract.md"
BUNDLE_CONTRACT = BUNDLE / "skill" / "add" / "phases" / "3-contract.md"

ADDPY_TRIO = (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
              BUNDLE / "tooling" / "add.py")

SCOPE_LABEL = "Scope (may touch):"
STRATEGY_LABEL = "Strategy (ordered batches):"
KNOWN_FIX_LABEL = "Known-problem fixes:"             # ADD-1 (full §5)
FAST_STRATEGY_LABEL = "Strategy & known-problem fixes:"  # ADD-2 (fast §5)
SAFETY_LINE = "Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>"
SECTION_HEADING = "## Declaring the scope of impact"
# the three pre-existing §5 lines that MUST stay byte-identical (additive change)
EXISTING_LINES = (
    "Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>",
    "Code lives in: `./src/`",
    "Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.",
)
# the v16/v18 frozen tag census of TASK.md.tmpl — a NEW tag is an amendment, never a drive-by
FROZEN_TAGS = ['action', 'after', 'alternative', 'assumptions', 'chosen', 'code',
               'cost', 'date', 'error_code', 'fields', 'link', 'must', 'name',
               'path', 'reject', 'scenario', 'scenarios', 'test_plan',
               'unchanged', 'why']


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class ScopeDeclTemplateTest(unittest.TestCase):
    # ---- scenario: a fresh scaffold carries the scope-of-impact placeholders
    def test_scaffold_carries_scope_of_impact_lines(self):
        cwd = Path.cwd()
        tmp = Path(tempfile.mkdtemp(prefix="add-scope-decl-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        try:
            os.chdir(tmp)
            buf, err = io.StringIO(), io.StringIO()
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["init", "--name", "demo"])
                add.main(["lock", "--force"])
                add.main(["new-task", "alpha", "--title", "alpha"])
            text = (tmp / ".add" / "tasks" / "alpha" / "TASK.md").read_text(
                encoding="utf-8")
            self.assertIn(SCOPE_LABEL, text)
            self.assertIn(STRATEGY_LABEL, text)
            self.assertLess(text.index(SCOPE_LABEL),
                            text.index(STRATEGY_LABEL),
                            "Scope line must sit ABOVE the Strategy line")
            self.assertLess(text.index(STRATEGY_LABEL),
                            text.index("Safety rule (feature-specific):"),
                            "both new lines must sit ABOVE the existing lines")
            for line in EXISTING_LINES:
                self.assertIn(line, text,
                              "pre-existing line changed - the add is additive")
        finally:
            os.chdir(cwd)

    # ---- scenario: the grammar comment states the rules + named divergence --
    def test_template_grammar_comment(self):
        text = CANON_TMPL.read_text(encoding="utf-8")
        self.assertIn(SCOPE_LABEL, text)
        self.assertIn(STRATEGY_LABEL, text)
        for form in ("this task dir", "project root", "sibling of the previous",
                     "whole subtree", "fail-closed", "scope-gate-enforce"):
            self.assertIn(form, text, f"template misses grammar form: {form}")

    # ---- scenario: the build guide teaches the discipline, deferral said ----
    def test_build_guide_scope_of_impact_section(self):
        text = CANON_BUILD.read_text(encoding="utf-8")
        self.assertIn(SECTION_HEADING, text)
        for token in ("frozen", "change request", "scope-gate-enforce"):
            self.assertIn(token, text, f"build guide misses: {token}")
        # placed between small-batches and the cardinal rule
        self.assertLess(text.index("## Work in small batches"),
                        text.index(SECTION_HEADING))
        self.assertLess(text.index(SECTION_HEADING),
                        text.index("## The cardinal rule"))
        # exit gate carries the no-undeclared-touch line
        gate = text[text.index("<exit_gate>"):text.index("</exit_gate>")]
        self.assertIn("outside the declared", gate)

    # ---- scenario: the contract guide names the freeze coverage -------------
    def test_contract_guide_freeze_line(self):
        text = CANON_CONTRACT.read_text(encoding="utf-8")
        self.assertIn("Scope (may touch)", text)
        self.assertIn("Strategy", text)

    # ---- scenario: pre-existing tasks are grandfathered (regression) --------
    def test_grandfather_is_prose_not_retro_red(self):
        text = CANON_TMPL.read_text(encoding="utf-8")
        for token in ("UNDECLARED", "grandfathered", "never retro-red"):
            self.assertIn(token, text, f"grandfather meaning missing: {token}")

    # ---- scenario: mirrors hold and the engine is untouched -----------------
    def test_mirrors_and_engine_untouched(self):
        self.assertEqual(_md5(CANON_TMPL), _md5(DOG_TMPL), "template: dogfood diverged")
        self.assertEqual(_md5(CANON_TMPL), _md5(BUNDLE_TMPL), "template: bundle diverged")
        self.assertEqual(_md5(CANON_BUILD), _md5(DOG_BUILD), "5-build: dogfood diverged")
        self.assertEqual(_md5(CANON_BUILD), _md5(BUNDLE_BUILD), "5-build: bundle diverged")
        self.assertEqual(_md5(CANON_CONTRACT), _md5(DOG_CONTRACT),
                         "3-contract: dogfood diverged")
        self.assertEqual(_md5(CANON_CONTRACT), _md5(BUNDLE_CONTRACT),
                         "3-contract: bundle diverged")
        digests = {_md5(p) for p in ADDPY_TRIO}
        self.assertEqual(len(digests), 1, "add.py trio diverged")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "add.py changed - this is a prose/template-only task")
        tags = sorted(set(re.findall(r"</?([a-z_]+)>",
                                     CANON_TMPL.read_text(encoding="utf-8"))))
        self.assertEqual(tags, FROZEN_TAGS,
                         "template tag census changed - the v16 vocab is frozen")

    # ---- build-strategy-solutions ADD-1: full §5 gains a Known-problem fixes line --
    def test_full_template_known_problem_fixes_line(self):
        text = CANON_TMPL.read_text(encoding="utf-8")
        self.assertIn(KNOWN_FIX_LABEL, text, "full §5 missing the Known-problem fixes line")
        # additive placement: Strategy < Known-problem fixes < Safety rule
        self.assertLess(text.index(STRATEGY_LABEL), text.index(KNOWN_FIX_LABEL),
                        "Known-problem fixes must sit BELOW Strategy")
        self.assertLess(text.index(KNOWN_FIX_LABEL),
                        text.index("Safety rule (feature-specific):"),
                        "Known-problem fixes must sit ABOVE the Safety rule line")
        for line in EXISTING_LINES:
            self.assertIn(line, text, "pre-existing §5 line changed - the add is additive")

    # ---- ADD-2: fast §5 gains a single strategy & known-problem fixes line --------
    def test_fast_template_strategy_line(self):
        text = CANON_FAST.read_text(encoding="utf-8")
        self.assertIn(FAST_STRATEGY_LABEL, text, "fast §5 missing the strategy line")
        self.assertLess(text.index(SCOPE_LABEL), text.index(FAST_STRATEGY_LABEL),
                        "the fast strategy line must sit BELOW Scope")

    def test_fast_template_mirrors(self):
        self.assertEqual(_md5(CANON_FAST), _md5(DOG_FAST), "fast template: dogfood diverged")
        self.assertEqual(_md5(CANON_FAST), _md5(BUNDLE_FAST), "fast template: bundle diverged")

    # ---- ADD-1/2: a fresh scaffold carries the new lines (full + fast) ------------
    def test_scaffold_carries_strategy_solutions(self):
        cwd = Path.cwd()
        tmp = Path(tempfile.mkdtemp(prefix="add-strat-sol-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
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
            self.assertIn(KNOWN_FIX_LABEL, full, "full scaffold missing Known-problem fixes")
            self.assertIn(FAST_STRATEGY_LABEL, fast, "fast scaffold missing the strategy line")
        finally:
            os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
