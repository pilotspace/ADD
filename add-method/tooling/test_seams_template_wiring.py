#!/usr/bin/env python3
"""Red/green tests for seams-template-wiring (milestone `seams`): wire the already-shipped
`.add/SEAMS.md` citation grammar (frozen by `seams-doc`) into `TASK.md.tmpl`'s §0 GROUND as one
new OPTIONAL line, `Seams consulted:`, placed between `Honors (patterns / conventions):` and
`Anchors the contract cites:`, byte-identical across the 3 FULL-template trees. Frozen shape
(§3 @ v1):
  - exactly one new line, exact label `Seams consulted:` (no "(optional)" before the colon),
    bracket content never a bare `[a-z_]+`-only token, zero `<!--`/`-->` sequences;
  - the line is optional — absence/unfilled never gates/warns; add.py stays byte-identical to
    engine_pin.ENGINE_MD5 (no engine edit this task);
  - TASK.fast.md.tmpl and every guide file are UNCHANGED (out of scope).

Behavior pinned, not prose phrasing. Run: cd add-method/tooling && python3 -m unittest
test_seams_template_wiring -v
"""
from __future__ import annotations

import hashlib
import io
import os
import re
import shutil
import subprocess
import tempfile
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
TMPL_COPIES = [CANON_TMPL, DOG_TMPL, BUNDLE_TMPL]

CANON_FAST = HERE / "templates" / "TASK.fast.md.tmpl"
DOG_FAST = REPO / ".add" / "tooling" / "templates" / "TASK.fast.md.tmpl"
BUNDLE_FAST = BUNDLE / "tooling" / "templates" / "TASK.fast.md.tmpl"
FAST_COPIES = [CANON_FAST, DOG_FAST, BUNDLE_FAST]

ADDPY_TRIO = [
    ADD_METHOD / "tooling" / "add.py",
    BUNDLE / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
]

GUIDE_COPIES = [
    ADD_METHOD / "skill" / "add" / "phases" / "0-ground.md",
    REPO / ".claude" / "skills" / "add" / "phases" / "0-ground.md",
    ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "0-ground.md",
]

LABEL = "Seams consulted:"
HONORS = "Honors (patterns / conventions):"
ANCHORS = "Anchors the contract cites:"

# FROZEN_TAGS census regex, same as test_scope_decl_template.py's own scan — imported directly
# below so a drift in one file cannot silently diverge from the other's definition.
from test_scope_decl_template import FROZEN_TAGS  # noqa: E402


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _parse_grep_cl_matches(raw_lines):
    """Grep-flavor-agnostic parse of `grep -cl` stdout lines into the set of matched paths.

    GNU grep's -cl prints one bare matching filename per line. BSD grep's -cl instead prints
    a "path:N" count line for every input file (N == 0 for a non-match) PLUS a separate bare
    "path" line for each actual match. A trailing ":<digits>" is only a BSD count line when
    it parses as an int; treat it as a match only when that count is > 0, so a BSD "path:0"
    line for a genuine non-match is excluded rather than misread as a match.
    """
    matched = set()
    for line in raw_lines:
        head, sep, tail = line.rpartition(":")
        if sep and tail.isdigit():
            if int(tail) > 0:
                matched.add(head)
        else:
            matched.add(line)
    return matched


def _section0(text: str) -> str:
    """The grounding sub-block. plan-phase-core collapsed §0 GROUND into §3 PLAN's
    `### Grounding` sub-block (no more standalone `## 0 ·` heading); extract that
    sub-block instead, ending right before the `### Contract` sub-block starts."""
    m = re.search(r"### Grounding.*?(?=\n### Contract)", text, flags=re.S)
    return m.group(0) if m else ""


def _run_cli(args: list[str]) -> tuple[str, str]:
    buf, err = io.StringIO(), io.StringIO()
    with redirect_stdout(buf), redirect_stderr(err):
        add.main(args)
    return buf.getvalue(), err.getvalue()


class SeamsLineAddedTest(unittest.TestCase):
    """M1 / Scenario: Seams consulted line lands between Honors and Anchors."""

    def test_line_present_in_all_3_trees(self):
        for p in TMPL_COPIES:
            text = p.read_text(encoding="utf-8")
            self.assertIn(LABEL, text, f"{p}: missing {LABEL!r}")

    def test_line_lands_between_honors_and_anchors(self):
        for p in TMPL_COPIES:
            sec0 = _section0(p.read_text(encoding="utf-8"))
            self.assertTrue(sec0, f"{p}: no §3 PLAN ### Grounding sub-block found")
            self.assertIn(HONORS, sec0, f"{p}: missing Honors line")
            self.assertIn(ANCHORS, sec0, f"{p}: missing Anchors line")
            self.assertIn(LABEL, sec0, f"{p}: missing {LABEL!r} in §0")
            i_honors = sec0.index(HONORS)
            i_seams = sec0.index(LABEL)
            i_anchors = sec0.index(ANCHORS)
            self.assertLess(i_honors, i_seams,
                             f"{p}: {LABEL!r} must come AFTER Honors")
            self.assertLess(i_seams, i_anchors,
                             f"{p}: {LABEL!r} must come BEFORE Anchors")

    def test_label_is_exact_no_optional_prefix(self):
        # the milestone's own exit-criterion grep matches this literal substring verbatim
        for p in TMPL_COPIES:
            text = p.read_text(encoding="utf-8")
            self.assertIn(LABEL, text)
            # no "(optional)" (or similar) inserted BEFORE the colon
            m = re.search(r"Seams consulted\s*(\([^)]*\))?\s*:", text)
            self.assertIsNotNone(m, f"{p}: label pattern not found")
            self.assertIsNone(m.group(1),
                               f"{p}: label must not carry a parenthetical before the colon")

    def test_every_other_section0_line_byte_unchanged_same_order(self):
        # the pre-existing §0 field labels must all still be present, in original relative order
        pre_existing = [
            "Touches (files · symbols · signatures):",
            "Context (working folder):",
            HONORS,
            ANCHORS,
            "Issues/Risks:",   # plan-phase-core: label lost its "(→ feed §1)" suffix
            "Related intent:",
            "Ground SHA:",
        ]
        for p in TMPL_COPIES:
            sec0 = _section0(p.read_text(encoding="utf-8"))
            positions = [sec0.index(line) for line in pre_existing]
            self.assertEqual(positions, sorted(positions),
                              f"{p}: pre-existing §0 lines reordered")


class SeamsLineIsOptionalTest(unittest.TestCase):
    """M2 / Scenario: a task without a cited seam stays fully valid."""

    def test_fresh_scaffold_carries_unfilled_placeholder(self):
        cwd = os.getcwd()
        tmp = Path(tempfile.mkdtemp(prefix="add-seams-tmpl-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.addCleanup(os.chdir, cwd)
        os.chdir(tmp)
        _run_cli(["init", "--name", "demo"])
        _run_cli(["lock", "--force"])
        _run_cli(["new-task", "alpha", "--title", "alpha"])
        text = (tmp / ".add" / "tasks" / "alpha" / "TASK.md").read_text(encoding="utf-8")
        self.assertIn(LABEL, text, "fresh scaffold must carry the Seams consulted line")

    def test_check_and_status_raise_nothing_about_unfilled_seam(self):
        cwd = os.getcwd()
        tmp = Path(tempfile.mkdtemp(prefix="add-seams-tmpl-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.addCleanup(os.chdir, cwd)
        os.chdir(tmp)
        _run_cli(["init", "--name", "demo"])
        _run_cli(["lock", "--force"])
        _run_cli(["new-task", "alpha", "--title", "alpha"])
        check_out, check_err = _run_cli(["check"])
        status_out, status_err = _run_cli(["status"])
        for stream in (check_out, check_err, status_out, status_err):
            self.assertNotIn("Seams consulted", stream,
                              "no check/status output may mention the unfilled seam citation")
            self.assertNotIn("seam", stream.lower(),
                              "no check/status output may warn/gate on the missing seam citation")

    def test_addpy_byte_identical_to_engine_pin(self):
        digests = {_md5(p) for p in ADDPY_TRIO}
        self.assertEqual(len(digests), 1, "add.py trio diverged")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                          "add.py changed — this is a template-only task, no engine edit")


class TagCensusUnchangedTest(unittest.TestCase):
    """M3 / Scenario: the placeholder never mutates the frozen tag census."""

    def test_tag_census_unchanged_21_entries(self):
        tags = sorted(set(re.findall(r"</?([a-z_]+)>",
                                      CANON_TMPL.read_text(encoding="utf-8"))))
        self.assertEqual(tags, FROZEN_TAGS,
                          "template tag census changed — the v16 vocab is frozen")

    def test_seams_bracket_is_not_a_bare_lowercase_token(self):
        text = CANON_TMPL.read_text(encoding="utf-8")
        m = re.search(re.escape(LABEL) + r"\s*<([^>]*)>", text)
        self.assertIsNotNone(m, "Seams consulted placeholder bracket not found")
        bracket = m.group(1)
        self.assertFalse(re.fullmatch(r"[a-z_]+", bracket),
                          f"bracket content {bracket!r} is a bare [a-z_]+ token — "
                          "would collide with FROZEN_TAGS census")


class NoNewHtmlCommentTest(unittest.TestCase):
    """M4 / Scenario: the placeholder introduces no HTML comment."""

    def test_comment_count_unchanged_11(self):
        for p in TMPL_COPIES:
            text = p.read_text(encoding="utf-8")
            self.assertEqual(text.count("<!--"), 11,
                              f"{p}: <!-- count drifted from the frozen 11")

    def test_seams_line_itself_carries_no_comment_markers(self):
        text = CANON_TMPL.read_text(encoding="utf-8")
        m = re.search(r"^" + re.escape(LABEL) + r".*$", text, re.MULTILINE)
        self.assertIsNotNone(m, "Seams consulted line not found")
        line = m.group(0)
        self.assertNotIn("<!--", line)
        self.assertNotIn("-->", line)

    def test_html_comment_re_finds_no_new_unmatched_span(self):
        # mirror add.py:274's own _HTML_COMMENT_RE and confirm it still resolves to exactly
        # the pre-existing 11 comment spans, i.e. no merge across the new line.
        pattern = re.compile(r"<!--.*?-->", re.DOTALL)
        text = CANON_TMPL.read_text(encoding="utf-8")
        spans = pattern.findall(text)
        self.assertEqual(len(spans), 11)


class ThreeTreeParityTest(unittest.TestCase):
    """M5 / Scenario: the edit is byte-identical across the 3 full-template trees."""

    def test_three_trees_byte_identical(self):
        digests = {_md5(p) for p in TMPL_COPIES}
        self.assertEqual(len(digests), 1,
                          f"template_drift: {[(str(p), _md5(p)) for p in TMPL_COPIES]}")

    def test_milestone_exit_grep_lists_all_3(self):
        # exact invocation the milestone's own exit criterion names (one grep -cl call, all
        # 3 paths as args). GNU grep (Linux CI) prints one bare matching filename per line for
        # -cl; BSD grep (macOS's default /usr/bin/grep) instead prints BOTH a "path:N" count
        # line (N == 0 for a non-match) AND a separate bare "path" line per actual match — an
        # implementation quirk, not a matching failure (confirmed directly against
        # /usr/bin/grep, not a shell alias/wrapper). _parse_grep_cl_matches only counts a
        # ":N" line as a match when N > 0, so this asserts the real invariant (all 3 tree
        # paths matched) regardless of which grep flavor runs it — see
        # test_parse_grep_cl_matches_excludes_bsd_zero_count for the regression this guards.
        out = subprocess.run(
            ["grep", "-cl", LABEL, *[str(p) for p in TMPL_COPIES]],
            capture_output=True, text=True)
        raw_lines = out.stdout.strip().splitlines()
        matched = _parse_grep_cl_matches(raw_lines)
        self.assertEqual(matched, {str(p) for p in TMPL_COPIES},
                          f"grep -cl must list all 3 tree paths as matches (raw output: {raw_lines!r})")


class GrepClParsingTest(unittest.TestCase):
    """Unit-level coverage for _parse_grep_cl_matches, independent of the real grep binary."""

    def test_gnu_bare_filenames_all_match(self):
        raw = ["a.txt", "b.txt", "c.txt"]
        self.assertEqual(_parse_grep_cl_matches(raw), {"a.txt", "b.txt", "c.txt"})

    def test_bsd_count_and_bare_lines_all_match(self):
        raw = ["a.txt:1", "a.txt", "b.txt:1", "b.txt"]
        self.assertEqual(_parse_grep_cl_matches(raw), {"a.txt", "b.txt"})

    def test_parse_grep_cl_matches_excludes_bsd_zero_count(self):
        # the regression the earlier `re.sub(r":\d+$", "", line)` fix (commit 5d0ce30) missed:
        # BSD grep -cl prints "path:0" for a genuine non-match, which a bare suffix-strip
        # cannot distinguish from a real match line — this must NOT be counted as matched.
        raw = ["a.txt:1", "a.txt", "nomatch.txt:0", "b.txt:1", "b.txt"]
        self.assertEqual(_parse_grep_cl_matches(raw), {"a.txt", "b.txt"})
        self.assertNotIn("nomatch.txt", _parse_grep_cl_matches(raw))


class FastTemplateUntouchedTest(unittest.TestCase):
    """M6 / Scenario: the fast-lane template and guides are untouched."""

    def test_fast_lane_trees_byte_identical_to_each_other(self):
        digests = {_md5(p) for p in FAST_COPIES}
        self.assertEqual(len(digests), 1, "TASK.fast.md.tmpl trio diverged")

    def test_fast_lane_has_no_seams_consulted_line(self):
        for p in FAST_COPIES:
            text = p.read_text(encoding="utf-8")
            self.assertNotIn(LABEL, text,
                              f"fast_lane_scope_creep: {LABEL!r} leaked into {p}")

    def test_guides_have_no_seams_consulted_line(self):
        # this task's scope is the FULL template only — guides are untouched
        for p in GUIDE_COPIES:
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8")
            self.assertNotIn(LABEL, text,
                              f"guide out of scope for this task, must not carry {LABEL!r}: {p}")


class RejectionContractsTest(unittest.TestCase):
    """One test per §2 Reject scenario — behavior asserted against the REAL shipped artifacts,
    proving the rejected shapes never landed, rather than fabricating a mock reviewer."""

    def test_reject_html_comment_placeholder(self):                    # R:unmatched_comment_merge
        # a placeholder written as an HTML comment would show up as `<!--` immediately after
        # the label; assert the real line carries none, and the total count stays 11.
        text = CANON_TMPL.read_text(encoding="utf-8")
        m = re.search(r"^" + re.escape(LABEL) + r".*$", text, re.MULTILINE)
        self.assertIsNotNone(m)
        self.assertNotIn("<!--", m.group(0))
        self.assertEqual(text.count("<!--"), 11)

    def test_reject_bare_single_word_tag(self):                        # R:frozen_tag_census
        text = CANON_TMPL.read_text(encoding="utf-8")
        m = re.search(re.escape(LABEL) + r"\s*<([^>]*)>", text)
        self.assertIsNotNone(m)
        self.assertFalse(re.fullmatch(r"[a-z_]+", m.group(1)))
        tags = sorted(set(re.findall(r"</?([a-z_]+)>", text)))
        self.assertEqual(tags, FROZEN_TAGS)

    def test_reject_engine_gate_on_optional_line(self):                # R:seam_citation_required
        addpy_src = (ADD_METHOD / "tooling" / "add.py").read_text(encoding="utf-8")
        self.assertNotIn("Seams consulted", addpy_src,
                          "seam_citation_required: add.py must not reference the optional line")
        digests = {_md5(p) for p in ADDPY_TRIO}
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5)

    def test_reject_drifted_tree_copy(self):                           # R:template_drift
        digests = [_md5(p) for p in TMPL_COPIES]
        self.assertEqual(len(set(digests)), 1, f"template_drift: {digests}")

    def test_reject_fast_lane_scope_creep(self):                       # R:fast_lane_scope_creep
        for p in FAST_COPIES:
            self.assertNotIn(LABEL, p.read_text(encoding="utf-8"))


class EdgeCasesTest(unittest.TestCase):
    """edge: pre_existing_task_grandfathered / anchor_resolution_out_of_scope."""

    def test_pre_existing_task_with_no_seams_line_is_grandfathered(self):
        cwd = os.getcwd()
        tmp = Path(tempfile.mkdtemp(prefix="add-seams-tmpl-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        self.addCleanup(os.chdir, cwd)
        os.chdir(tmp)
        _run_cli(["init", "--name", "demo"])
        _run_cli(["lock", "--force"])
        _run_cli(["new-task", "alpha", "--title", "alpha"])
        task_path = tmp / ".add" / "tasks" / "alpha" / "TASK.md"
        text = task_path.read_text(encoding="utf-8")
        # simulate a task scaffolded BEFORE this milestone: strip the Seams consulted line
        stripped = "\n".join(
            line for line in text.splitlines() if not line.startswith(LABEL)
        )
        task_path.write_text(stripped, encoding="utf-8")
        check_out, check_err = _run_cli(["check"])
        self.assertNotIn("Seams consulted", check_out + check_err)
        # exit clean: main() returns 0 and raises nothing for a task missing the (optional) line
        rc = add.main(["check"])
        self.assertEqual(rc, 0,
                          "add.py check must exit clean for a pre-existing task missing the line")

    def test_anchor_resolution_is_not_mechanically_enforced(self):
        # no engine change ships this task — a malformed/nonexistent SEAMS.md#<id> citation
        # is never validated by add.py; confirm no such resolution logic exists.
        addpy_src = (ADD_METHOD / "tooling" / "add.py").read_text(encoding="utf-8")
        self.assertNotIn("SEAMS.md#", addpy_src,
                          "add.py must not mechanically resolve/validate SEAMS.md anchors")


if __name__ == "__main__":
    unittest.main(verbosity=2)
