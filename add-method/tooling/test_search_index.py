#!/usr/bin/env python3
"""Red/green tests for search-index (context-search, task 1/2): `add.py search
<keyword...>` — a read-only CLI command + a new pure `add_engine/search.py`
module that keyword/substring-scans the active + archived milestone/task
corpus's title/goal/rationale (milestone) or title/Feature (task) lines —
never full body, never graph traversal, never semantic matching — ranking
hits by descending match count and printing `{slug, kind, status, snippet}`.

One test class per §2 SCENARIOS gherkin block (20 scenarios, frozen contract
@ v1). A trailing `SearchPureFunctionsContractConformance` class adds a few
direct unit tests against the 6 named-in-contract functions (mirrors
test_rule_id_coverage.py's own extra `RuleCoverageGapsPure` class) — these
are ADDITIONAL contract-conformance checks, not a substitute for the 20
scenario tests above them.

Run: cd add-method/tooling && python3 -m unittest test_search_index -v
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import add
import engine_pin

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ADD_PY_COPIES = [
    HERE / "add.py",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
]
SEARCH_PY_COPIES = [
    HERE / "add_engine" / "search.py",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "add_engine" / "search.py",
    REPO / ".add" / "tooling" / "add_engine" / "search.py",
]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class _Board(unittest.TestCase):
    """Shared harness: a fresh temp `.add/` project + raw MILESTONE.md/TASK.md
    fixture writers. Search is stateless (reads only the filesystem corpus, no
    state.json involvement beyond `find_root`), so fixtures are written
    directly — no need to drive the full new-milestone/new-task scaffolding."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-search-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self.root = self.tmp / ".add"

    def _silent(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            try:
                add.main(list(argv))
            except SystemExit as e:
                if e.code:
                    raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        """stdout+stderr merged (mirrors test_rule_id_coverage.py's own _run)."""
        buf = io.StringIO()
        code = 0
        with redirect_stdout(buf), redirect_stderr(buf):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), code

    def _run_split(self, *argv):
        """stdout/stderr kept SEPARATE — needed to prove a usage error prints
        nothing on stdout (no hit list) while argparse's message lands on stderr."""
        out_buf, err_buf = io.StringIO(), io.StringIO()
        code = 0
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
        return out_buf.getvalue(), err_buf.getvalue(), code

    def _write_milestone(self, slug, *, title=None, goal="", rationale="",
                          status="active", extra_body="", archived=False):
        d = (self.root / "archive" / slug) if archived else (self.root / "milestones" / slug)
        d.mkdir(parents=True, exist_ok=True)
        title = slug if title is None else title
        path = d / "MILESTONE.md"
        path.write_text(
            f"# MILESTONE: {title}\n\n"
            f"goal: {goal}\n"
            f"rationale: {rationale}\n"
            f"stage: mvp · status: {status} · created: 2026-01-01T00:00:00+00:00\n\n"
            f"## Scope\n{extra_body}\n",
            encoding="utf-8",
        )
        return path

    def _write_task(self, slug, *, title=None, feature="", phase="ground",
                     extra_body="", archived_under=None):
        d = ((self.root / "archive" / archived_under / "tasks" / slug) if archived_under
             else (self.root / "tasks" / slug))
        d.mkdir(parents=True, exist_ok=True)
        title = slug if title is None else title
        path = d / "TASK.md"
        path.write_text(
            f"# TASK: {title}\n\n"
            f"slug: {slug} · created: 2026-01-01 · stage: mvp\n"
            f"milestone: none\n"
            f"phase: {phase}\n\n"
            f"## 1 · SPECIFY\n\n"
            f"Feature: {feature}\n\n"
            f"{extra_body}\n",
            encoding="utf-8",
        )
        return path


# --- 1: multiple keywords OR-match case-insensitively -----------------------
class OrMatchCaseInsensitive(_Board):
    def test_or_match_case_insensitive(self):                      # M1
        self._write_milestone("has-search", goal="a goal that mentions search only")
        out, code = self._run("search", "INDEX", "search")
        self.assertEqual(code, 0)
        self.assertIn("has-search", out, "the OR-combined keyword 'search' must match")


# --- 2: all 4 corpus roots are scanned --------------------------------------
class AllFourRootsScanned(_Board):
    def test_all_four_roots_scanned(self):                         # M2
        self._write_milestone("live-ms", goal="contains ZKEYWORD here")
        self._write_task("live-task", feature="contains ZKEYWORD here")
        self._write_milestone("arch-ms", goal="contains ZKEYWORD here", archived=True)
        self._write_task("arch-task", feature="contains ZKEYWORD here", archived_under="arch-ms")
        out, code = self._run("search", "ZKEYWORD")
        self.assertEqual(code, 0)
        for slug in ("live-ms", "live-task", "arch-ms", "arch-task"):
            self.assertIn(slug, out, f"{slug} must appear in the hit list")


# --- 3: an archived task nested under its milestone bundle is found --------
class ArchivedTaskNestedLayoutFound(_Board):
    def test_archived_task_found_when_nested_under_milestone_bundle(self):
        # M2, R:archived_task_layout_missed
        self._write_task("nested-task", feature="contains UNIQUEARCHKW",
                          archived_under="owning-ms")
        # deliberately NO flat .add/archive/nested-task/TASK.md exists
        self.assertFalse((self.root / "archive" / "nested-task").exists())
        out, code = self._run("search", "UNIQUEARCHKW", "--json")
        self.assertEqual(code, 0)
        hits = json.loads(out)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["slug"], "nested-task")
        self.assertEqual(hits[0]["kind"], "task")
        self.assertEqual(hits[0]["status"], "archived")


# --- 4: match scope excludes a milestone's full body ------------------------
class ExcludesMilestoneFullBody(_Board):
    def test_milestone_full_body_excluded(self):                   # M3, R:full_body_scanned
        self._write_milestone("body-ms", goal="ordinary goal", rationale="ordinary rationale",
                               extra_body="zzzOnlyInBodyzzz lives in Shared decisions only")
        out, code = self._run("search", "zzzOnlyInBodyzzz")
        self.assertEqual(code, 0)
        self.assertNotIn("body-ms", out)
        self.assertIn("no matches for:", out)


# --- 5: match scope excludes a task's full body -----------------------------
class ExcludesTaskFullBody(_Board):
    def test_task_full_body_excluded(self):                        # M3
        self._write_task("body-task", feature="ordinary feature line",
                          extra_body="## 5 · BUILD\nzzzOnlyInStrategyzzz lives in Strategy")
        out, code = self._run("search", "zzzOnlyInStrategyzzz")
        self.assertEqual(code, 0)
        self.assertNotIn("body-task", out)


# --- 6: an unfilled Feature placeholder is not searchable content ----------
class PlaceholderNotSearchable(_Board):
    def test_unfilled_feature_placeholder_not_matched(self):
        # M3, R:placeholder_treated_as_content
        self._write_task("fresh-task", feature="<name>")
        out, code = self._run("search", "name")
        self.assertEqual(code, 0)
        self.assertNotIn("fresh-task", out)


# --- 7: ranking is by descending match count --------------------------------
class RankingDescending(_Board):
    def test_ranking_by_descending_count(self):                    # M4, R:unranked_output
        self._write_milestone("three-hits", goal="search search search")
        self._write_milestone("one-hit", goal="search only once")
        out, code = self._run("search", "search")
        self.assertEqual(code, 0)
        self.assertLess(out.index("three-hits"), out.index("one-hit"),
                         "the 3-occurrence milestone must print before the 1-occurrence one")


# --- 8: a tie in match count is broken alphabetically by slug --------------
class TieBreakAlphabetical(_Board):
    def test_tie_broken_alphabetically_by_slug(self):              # M4
        self._write_task("beta-task", feature="contains tiekeyword once")
        self._write_task("alpha-task", feature="contains tiekeyword once")
        out, code = self._run("search", "tiekeyword")
        self.assertEqual(code, 0)
        self.assertLess(out.index("alpha-task"), out.index("beta-task"))


# --- 9: each hit prints exactly the 4 frozen fields, snippet truncated -----
class HitPrintsExactFieldsSnippetTruncated(_Board):
    def test_text_row_exact_fields_snippet_truncated(self):
        # M5, R:output_field_mismatch
        from add_engine.search import MAX_SNIPPET_LEN
        long_goal = "keywordhit " + ("x" * 200)
        self._write_milestone("long-ms", goal=long_goal)
        out, code = self._run("search", "keywordhit")
        self.assertEqual(code, 0)
        row = re.search(r"^long-ms  \[milestone, active\]  \(1 match\(es\)\)$", out, re.M)
        self.assertIsNotNone(row, f"row format mismatch (no unexpected 5th field):\n{out}")
        snippet_line = re.search(r"^ {4}(.+)$", out, re.M)
        self.assertIsNotNone(snippet_line)
        snippet = snippet_line.group(1)
        self.assertTrue(snippet.endswith("..."), "a truncated snippet must end in an ellipsis")
        self.assertEqual(len(snippet), MAX_SNIPPET_LEN + 3,
                          "snippet must be the first 120 chars + a 3-char ellipsis")


# --- 10: status is "archived" overriding a stale in-doc value --------------
class StatusArchivedOverridesStale(_Board):
    def test_archived_status_overrides_stale_indoc_value(self):    # M6
        self._write_milestone("stale-ms", goal="contains STALEKW here",
                               status="active", archived=True)
        out, code = self._run("search", "STALEKW", "--json")
        self.assertEqual(code, 0)
        hits = json.loads(out)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["status"], "archived",
                          "an archive-root hit's status must be 'archived' even though "
                          "the doc's own status: line still literally reads 'active'")


# --- 11: a live task's status is its phase line -----------------------------
class LiveTaskStatusIsPhase(_Board):
    def test_live_task_status_reads_phase_line(self):              # M6
        self._write_task("phase-task", feature="contains PHASEKW here", phase="build")
        out, code = self._run("search", "PHASEKW", "--json")
        self.assertEqual(code, 0)
        hits = json.loads(out)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["status"], "build")


# --- 12: zero keywords is an argparse usage error ---------------------------
class ZeroKeywordsIsUsageError(_Board):
    def test_zero_keywords_is_argparse_usage_error(self):
        # R:search_accepts_zero_keywords
        self._write_milestone("some-ms", goal="anything at all")
        out, err, code = self._run_split("search")
        self.assertEqual(code, 2)
        self.assertEqual(out, "", "no hit list may print on a usage error")
        self.assertNotIn("some-ms", out, "no artifact may be treated as matched-by-default")


# --- 13: zero matches is a clean, non-error result --------------------------
class ZeroMatchesIsClean(_Board):
    def test_zero_matches_prints_clean_message_exit_zero(self):    # M7
        self._write_milestone("some-ms", goal="ordinary goal")
        out, code = self._run("search", "zzzNoSuchKeywordzzz")
        self.assertEqual(code, 0)
        self.assertEqual(out, "no matches for: zzzNoSuchKeywordzzz\n")


# --- 14: an empty corpus returns cleanly ------------------------------------
class EmptyCorpusReturnsCleanly(_Board):
    def test_empty_corpus_no_exception(self):                      # edge case
        out, code = self._run("search", "anything")
        self.assertEqual(code, 0)
        self.assertEqual(out, "no matches for: anything\n")


# --- 15: --json prints the frozen 4-field array, no count -------------------
class JsonPrintsFrozenFieldsNoCount(_Board):
    def test_json_hit_has_exactly_four_fields_no_count(self):      # M8
        self._write_milestone("json-ms", goal="contains JSONKW here")
        out, code = self._run("search", "JSONKW", "--json")
        self.assertEqual(code, 0)
        hits = json.loads(out)
        self.assertEqual(len(hits), 1)
        self.assertEqual(set(hits[0].keys()), {"slug", "kind", "status", "snippet"})


# --- 16: --json with zero matches prints an empty array ---------------------
class JsonZeroMatchesEmptyArray(_Board):
    def test_json_zero_matches_prints_empty_array(self):           # M8
        out, code = self._run("search", "zzzNoSuchKeywordzzz", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "[]")


# --- 17: a malformed/unreadable doc is skipped, not fatal ------------------
class MalformedDocSkippedNotFatal(_Board):
    def test_unreadable_doc_is_skipped_not_fatal(self):
        # M9, R:search_crashes_on_malformed_doc
        self._write_task("good-task", feature="contains SURVIVEKW here")
        broken_dir = self.root / "tasks" / "broken-task"
        broken_dir.mkdir(parents=True, exist_ok=True)
        # a DIRECTORY where a file is expected -> .read_text() raises
        # IsADirectoryError (an OSError subclass) portably, no chmod/root gotchas
        (broken_dir / "TASK.md").mkdir()
        out, code = self._run("search", "SURVIVEKW")
        self.assertEqual(code, 0, f"must not raise on a malformed doc:\n{out}")
        self.assertIn("good-task", out, "every OTHER readable artifact must still be reported")


# --- 18: no graph/backlink traversal ----------------------------------------
class NoBacklinkTraversal(_Board):
    def test_textual_reference_does_not_pull_in_the_referencing_milestone(self):
        # R:not_a_backlink_query
        self._write_milestone("milestone-b", title="milestone B has uniquewordB inside",
                               goal="ordinary goal for B")
        self._write_milestone("milestone-a", title="milestone A",
                               rationale="kindred spirit to the milestone-b roadmap")
        out, code = self._run("search", "uniquewordB")
        self.assertEqual(code, 0)
        self.assertIn("milestone-b", out)
        self.assertNotIn("milestone-a", out,
                          "A must NOT be returned merely because its rationale names B")


# --- 19: no persisted index or cache file -----------------------------------
class NoPersistedCache(_Board):
    def test_second_call_reflects_current_file_content(self):
        # R:incremental_index_introduced
        task_path = self._write_task("live-edit-task", feature="no fresh word yet")
        out1, code1 = self._run("search", "freshword")
        self.assertEqual(code1, 0)
        self.assertNotIn("live-edit-task", out1)
        task_path.write_text(
            task_path.read_text(encoding="utf-8").replace(
                "no fresh word yet", "contains freshword now"),
            encoding="utf-8",
        )
        out2, code2 = self._run("search", "freshword")
        self.assertEqual(code2, 0)
        self.assertIn("live-edit-task", out2,
                       "the second call must reflect the EDITED file, proving no stale cache")


# --- 20: a keyword matching both a milestone and a task returns both -------
class MatchesBothKindsReturnsBoth(_Board):
    def test_keyword_matching_both_kinds_returns_both(self):       # edge case
        self._write_milestone("ctx-ms", title="the context milestone")
        self._write_task("ctx-task", title="the context task", feature="unrelated feature line")
        out, code = self._run("search", "context", "--json")
        self.assertEqual(code, 0)
        hits = json.loads(out)
        kinds = {h["kind"] for h in hits}
        self.assertEqual(kinds, {"milestone", "task"})


# --- contract-conformance: the 6 named-in-contract search.py functions -----
class SearchPureFunctionsContractConformance(unittest.TestCase):
    """Direct unit tests against the exact functions §3 CONTRACT names —
    ADDITIONAL to the 20 CLI-level scenario tests above (mirrors
    test_rule_id_coverage.py's own extra RuleCoverageGapsPure class)."""

    def test_fold_continuation_joins_indented_lines_stops_at_unindented(self):
        from add_engine.search import _fold_continuation
        raw = "first line\n  continued once\n  continued twice\nSTOP: not indented"
        self.assertEqual(_fold_continuation(raw), "first line continued once continued twice")

    def test_fold_continuation_stops_at_blank_line(self):
        from add_engine.search import _fold_continuation
        raw = "first line\n\nnot folded"
        self.assertEqual(_fold_continuation(raw), "first line")

    def test_milestone_fields_missing_field_is_empty_string(self):
        from add_engine.search import _milestone_fields
        fields = _milestone_fields("# MILESTONE: only a title\n")
        self.assertEqual(fields, {"title": "only a title", "goal": "", "rationale": ""})

    def test_task_fields_placeholder_feature_is_empty_string(self):
        from add_engine.search import _task_fields
        fields = _task_fields("# TASK: a title\n\nFeature: <name>\n")
        self.assertEqual(fields["feature"], "")

    def test_keyword_hit_none_when_nothing_matches(self):
        from add_engine.search import _keyword_hit
        self.assertIsNone(_keyword_hit({"title": "abc", "goal": "def"}, ["zzz"]))

    def test_keyword_hit_sums_across_all_fields(self):
        from add_engine.search import _keyword_hit
        hit = _keyword_hit({"title": "cat cat", "goal": "cat"}, ["cat"])
        self.assertEqual(hit[0], 3)
        self.assertEqual(hit[1], "cat cat")   # first field (dict order) containing a match

    def test_iter_corpus_missing_root_yields_nothing(self):
        from add_engine.search import _iter_corpus
        self.assertEqual(list(_iter_corpus(Path("/definitely/does/not/exist"))), [])


# --- engine-parity: this task's own regression guard (mirrors precedent) ---
class EngineSearchPinned(unittest.TestCase):
    def test_add_py_byte_identical_and_pinned(self):                # M... (invariants)
        present = [p for p in ADD_PY_COPIES if p.exists()]
        self.assertTrue(present, "at least the canonical add.py must exist")
        digests = {_md5(p) for p in present}
        self.assertEqual(len(digests), 1, "all add.py copies must be byte-identical")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                          "add.py must match the re-pinned engine_pin.ENGINE_MD5")

    def test_search_py_exists_and_byte_identical_across_trees(self):
        present = [p for p in SEARCH_PY_COPIES if p.exists()]
        self.assertEqual(len(present), 3, "add_engine/search.py must exist in all 3 engine trees")
        digests = {_md5(p) for p in present}
        self.assertEqual(len(digests), 1, "all add_engine/search.py copies must be byte-identical")

    def test_package_digest_matches_pinned_engine_pkg_md5(self):
        import engine_manifest
        for tree in (HERE, HERE.parent / "src" / "add_method" / "_bundled" / "tooling",
                     REPO / ".add" / "tooling"):
            self.assertEqual(engine_manifest.package_digest(tree), engine_pin.ENGINE_PKG_MD5,
                              f"mirror_incomplete: {tree} package digest != ENGINE_PKG_MD5")


if __name__ == "__main__":
    unittest.main(verbosity=2)
