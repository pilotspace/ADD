#!/usr/bin/env python3
"""Red/green tests for honest-reject-naming (milestone flow-honesty).

CONTRACT (frozen @ v1) — honest LABELING; gate CONDITIONS byte-unchanged, only reject-code
STRINGS move (+ one behavior refinement: carry's --match-miss gains a distinct code):
  release FLOOR  (add_engine/release.py:_build_in_flight, condition UNCHANGED; --force-able)
    add.py release <v>   a task in build/verify, gate=none  ->  "release_build_in_flight"  (was release_tests_red)
  SPEC-delta vocab reconciled to the seed/drop set:
    carry-delta  --match S hits >1 OPEN     -> "ambiguous_spec_match"   (was ambiguous_spec_delta)
    carry-delta  --match S hits 0, OPEN>0   -> "no_matching_spec_delta"  (was lumped -> no_open_spec_delta)
    carry-delta  no OPEN delta at all       -> "no_open_spec_delta"      (UNCHANGED)
    reopen-delta --match S hits >1 CARRIED  -> "ambiguous_spec_match"   (was ambiguous_spec_delta)
  PROSE (read-only docs, code string "goal_not_auto_ready" UNCHANGED):
    11-governance.md goal-clarity over-claim "earns trust" -> "measures citation presence"
    scope.md "Confirm before create is the invariant" -> the convention, enforced only by the opt-in --await-confirm gate
  HYGIENE: the old code strings (release_tests_red / ambiguous_spec_delta) are GONE from live
    engine emit sites + guide + book trees (historical records — CHANGELOG, .add/tasks/*, engine_pin
    genealogy — are honest history, NOT rewritten).
One test per scenario.
Run: python3 -m unittest test_reject_names -v
"""
import contextlib
import io
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add

# --- repo geometry (add.py == <repo>/add-method/tooling/add.py) -----------------
TOOLING = Path(add.__file__).resolve().parent          # add-method/tooling
ADD_METHOD = TOOLING.parent                            # add-method
REPO = ADD_METHOD.parent                               # repo root
ENGINE_DIR = TOOLING / "add_engine"
SKILL_TREES = [
    ADD_METHOD / "skill" / "add",
    REPO / ".claude" / "skills" / "add",
    ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add",
]
BOOK_TREES = [
    ADD_METHOD / "docs",
    ADD_METHOD / "src" / "add_method" / "_bundled" / "docs",
    REPO,                                              # the repo-root book mirror
]
BOOK_FILES = ["16-releasing.md", "11-governance.md", "appendix-c-glossary.md"]
OLD_CODES = ("release_tests_red", "ambiguous_spec_delta")


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-reject-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("lock", "--force")

    def tearDown(self):
        os.chdir(self._cwd)

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return code, out.getvalue() + err.getvalue()

    def _root(self):
        return self.tmp / ".add"

    def _task_md(self, slug):
        return self._root() / "tasks" / slug / "PLAN.md"

    def _state(self):
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _mk(self, slug):
        if slug not in (self._state().get("tasks") or {}):
            self._silent("new-task", slug, "--title", "Feature")
        return self._task_md(slug)

    def _set_spec(self, slug, *open_texts):
        """Give `slug` one '- [SPEC · open] <t> (evidence: ev)' line per open_texts."""
        p = self._mk(slug)
        text = p.read_text(encoding="utf-8")
        idx = text.index("## 7 · OBSERVE")
        head_end = text.index("\n", idx) + 1
        lines = "".join(f"- [SPEC · open] {t} (evidence: ev)\n" for t in open_texts)
        body = f"\n### Spec delta\n{lines}\n### Competency deltas\n"
        p.write_text(text[:head_end] + body, encoding="utf-8")
        return p

    def _loose_done(self, slug="loose1"):
        """A milestone-free task carried to PASS -> the project is releasable."""
        self._silent("new-task", slug, "--title", "Standalone")
        self._silent("phase", "verify", slug)
        self._silent("gate", "PASS", slug)

    def _build_in_flight(self, slug="bif"):
        """A task parked at verify with no gate -> _build_in_flight(state) is True
        (phase verify jumps past build, so the universal freeze gate is not crossed)."""
        self._silent("new-task", slug, "--title", "WIP")
        self._silent("phase", "verify", slug)

    def _changelog(self):
        p = self.tmp / "CHANGELOG.md"
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def _releases(self):
        p = self.tmp / "RELEASES.md"
        return p.read_text(encoding="utf-8") if p.exists() else ""
class RepoHygieneTest(unittest.TestCase):
    """Grep the LIVE trees — engine emit sites + guide + book — for the retired codes.
    Historical records (CHANGELOG, .add/tasks/*, .add/archive/*, engine_pin genealogy) are
    honest history and intentionally NOT scanned."""

    def _engine_sources(self):
        return [TOOLING / "add.py", *sorted(ENGINE_DIR.glob("*.py"))]

    def test_old_codes_absent_from_engine(self):               # Must (gone from emit sites)
        for f in self._engine_sources():
            body = f.read_text(encoding="utf-8")
            for code in OLD_CODES:
                self.assertNotIn(code, body, f"{code} still in {f.name}")

    def test_old_codes_absent_from_guides(self):               # Must (gone from skill guides)
        for tree in SKILL_TREES:
            for md in sorted(tree.rglob("*.md")):
                body = md.read_text(encoding="utf-8")
                for code in OLD_CODES:
                    self.assertNotIn(code, body, f"{code} still in {md}")

    def test_old_codes_absent_from_book(self):                 # Must (gone from book floor list)
        for tree in BOOK_TREES:
            for name in BOOK_FILES:
                body = (tree / name).read_text(encoding="utf-8")
                for code in OLD_CODES:
                    self.assertNotIn(code, body, f"{code} still in {tree / name}")

    def test_new_release_code_present_in_book(self):           # Must (the rename landed in prose)
        for tree in BOOK_TREES:
            body = (tree / "16-releasing.md").read_text(encoding="utf-8")
            self.assertIn("release_build_in_flight", body, f"new code missing in {tree}")


class ProseFramingTest(unittest.TestCase):
    def _canonical(self, *parts):
        return (ADD_METHOD / "docs").joinpath(*parts).read_text(encoding="utf-8")

    def test_goal_prose_measures_not_earns(self):              # Must (goal_not_auto_ready reframe)
        gov = self._canonical("11-governance.md")
        self.assertNotIn("earns trust", gov.replace("*", ""),
                         "the goal-clarity over-claim 'earns trust' is reframed")
        self.assertIn("measures citation presence", gov)
        self.assertIn("goal_not_auto_ready", gov, "the code string itself is UNCHANGED")

    def test_scope_md_opt_in_not_invariant(self):              # Must (scope.md relabel)
        scope = (ADD_METHOD / "skill" / "add" / "phases" / "direction.md").read_text(encoding="utf-8")
        self.assertNotIn("Confirm before create is the invariant", scope)
        self.assertIn("Confirm before create is the convention", scope)
        self.assertIn("--await-confirm", scope)


if __name__ == "__main__":
    unittest.main()
