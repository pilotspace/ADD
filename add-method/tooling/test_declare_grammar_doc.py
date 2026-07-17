#!/usr/bin/env python3
"""Red/green tests for stating the `Tests live in:` declaration grammar in the §4
template + phase guide (task declare-grammar-doc, milestone v13-1).

A prose-only task: content anchors prove the words exist (the folded
"prose-guides-are-TDD-able" convention); engine behavior stays pinned by
test_declared_fallback.py. add.py is untouched — a guard asserts it. Run:
    python3 -m unittest test_declare_grammar_doc -v
"""
import hashlib
import io
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent          # add-method/tooling
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"

CANON_TMPL = HERE / "templates" / "TASK.md.tmpl"
DOG_TMPL = REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl"
BUNDLE_TMPL = BUNDLE / "tooling" / "templates" / "TASK.md.tmpl"

CANON_GUIDE = ADD_METHOD / "skill" / "add" / "phases" / "direction.md"
DOG_GUIDE = REPO / ".claude" / "skills" / "add" / "phases" / "direction.md"
BUNDLE_GUIDE = BUNDLE / "skill" / "add" / "phases" / "direction.md"

ADDPY_TRIO = (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
              BUNDLE / "tooling" / "add.py")

# message-specific anchor only the real grammar comment emits (folded convention:
# never assert an ambient token)
COMMENT_ANCHOR = "declare paths as backticked tokens"
SECTION_HEADING = "## Declaring where tests live"
VISIBLE_DEFAULT = "Tests live in: `./tests/` · MUST run red (missing implementation) before Build."


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class DeclareGrammarDocTest(unittest.TestCase):
    # ---- scenario: template states the grammar -----------------------------
    def test_template_states_grammar(self):
        text = CANON_TMPL.read_text(encoding="utf-8")
        self.assertIn(VISIBLE_DEFAULT, text)                 # default line unchanged
        self.assertIn(COMMENT_ANCHOR, text)
        for form in ("this task dir", "project root", "sibling of the previous",
                     "non-recursive", "†"):
            self.assertIn(form, text, f"template misses grammar form: {form}")

    # ---- scenario: scaffolds carry the grammar (behavioral) ----------------
    def test_scaffold_carries_grammar(self):
        cwd = Path.cwd()
        tmp = Path(tempfile.mkdtemp(prefix="add-grammar-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        try:
            os.chdir(tmp)
            buf, err = io.StringIO(), io.StringIO()
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["init", "--name", "demo"])
                add.main(["new-milestone", "v1", "--title", "T", "--goal", "g"])
                add.main(["new-task", "alpha", "--title", "alpha"])
            generated = (tmp / ".add" / "tasks" / "alpha" / "TASK.md").read_text(
                encoding="utf-8")
            self.assertIn(COMMENT_ANCHOR, generated)         # comment is copied through
        finally:
            os.chdir(cwd)

    # ---- scenario: guide section exists ------------------------------------
    def test_guide_section_present(self):
        text = CANON_GUIDE.read_text(encoding="utf-8")
        self.assertIn(SECTION_HEADING, text)
        for rule in ("FIRST", "backticked", "task dir", "project root",
                     "sibling", "non-recursive", "dedup", "†"):
            self.assertIn(rule, text, f"guide misses resolution rule: {rule}")
        # skill-loop-fold: the old ## Produce / ## AI prompt frame folded into
        # direction.md's Tests span — the grammar section now closes that span.
        self.assertLess(text.index("## Tests"), text.index(SECTION_HEADING))

    # ---- scenario: three trees agree ----------------------------------------
    def test_grammar_doc_tree_parity(self):
        self.assertEqual(_md5(CANON_TMPL), _md5(DOG_TMPL), "template: dogfood diverged")
        self.assertEqual(_md5(CANON_TMPL), _md5(BUNDLE_TMPL), "template: bundle diverged")
        self.assertEqual(_md5(CANON_GUIDE), _md5(DOG_GUIDE), "guide: dogfood diverged")
        self.assertEqual(_md5(CANON_GUIDE), _md5(BUNDLE_GUIDE), "guide: bundle diverged")

    # ---- scenario: engine untouched (green-by-design regression guard) -----
    def test_engine_untouched(self):
        a, b, c = (_md5(p) for p in ADDPY_TRIO)
        self.assertEqual(a, b, "add.py: dogfood diverged from canonical")
        self.assertEqual(a, c, "add.py: bundle diverged from canonical")


if __name__ == "__main__":
    unittest.main()
