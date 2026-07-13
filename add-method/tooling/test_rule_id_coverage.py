#!/usr/bin/env python3
"""Red/green tests for rule-id-coverage (traceability-ids, task 1/2 — the milestone's flagship
goal): a §1 Must/Reject with no §2 scenario tag and no §4 `covers:` reference is a coverage gap,
surfaced by `add.py check` as a never-blocking WARN — but ONLY for a task that already uses the
M#/R:code tagging convention at all (opt-in by tag presence); a task with zero tags anywhere in
§2/§4 is grandfathered and stays completely silent, so 50+ pre-existing tasks are never retro-flagged.

Run: cd add-method/tooling && python3 -m unittest test_rule_id_coverage -v
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
from add_engine.predicates import _rule_coverage_gaps

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ADD_PY_COPIES = [
    HERE / "add.py",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
]
_CANON_SKILL = HERE.parent / "skill" / "add"
PHASES_POOL = [
    "phases/0-setup.md", "phases/1-specify.md",
    "phases/2-scenarios.md", "phases/3-plan.md", "phases/4-tests.md",
    "phases/5-build.md", "phases/6-verify.md", "phases/7-observe.md",
]
TEMPLATE_COPIES = [
    HERE / "templates" / "TASK.md.tmpl",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.md.tmpl",
    REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
]

_SEC1 = (
    "Must:\n<must>\n"
    "  - M1: tagged must\n"
    "  - M2: untagged must\n"
    "</must>\n"
    "Reject:\n<reject>\n"
    "  - bad input -> \"bad_code\"\n"
    "</reject>\n"
)


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class _Board(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-ridc-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("lock", "--force")

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
        buf = io.StringIO()
        code = 0
        with redirect_stdout(buf), redirect_stderr(buf):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), code

    def _task_md(self, slug: str) -> Path:
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

    def _set_section(self, slug: str, n: int, body: str):
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        pattern = re.compile(rf"(?ms)(^##\s*{n}\s*·[^\n]*\n)(.*?)(?=^##\s*\d+\s*·|\Z)")
        new_text, count = pattern.subn(lambda m: m.group(1) + body + "\n", text, count=1)
        assert count == 1, f"section {n} heading not found in {slug}'s TASK.md"
        p.write_text(new_text, encoding="utf-8")

    def _make_task(self, slug: str, sec1: str, sec2: str, sec4: str = ""):
        self._silent("new-task", slug, "--title", slug)
        self._set_section(slug, 1, sec1)
        self._set_section(slug, 2, sec2)
        if sec4:
            self._set_section(slug, 4, sec4)

    def _force_phase(self, slug: str, phase: str):
        sp = self.tmp / ".add" / "state.json"
        st = json.loads(sp.read_text(encoding="utf-8"))
        st["tasks"][slug]["phase"] = phase
        sp.write_text(json.dumps(st, indent=2), encoding="utf-8")
        p = self._task_md(slug)
        text = re.sub(r"(?m)^phase:\s*\S+", f"phase: {phase}", p.read_text(encoding="utf-8"), count=1)
        p.write_text(text, encoding="utf-8")


class UngrandfatheredTaskIsSilent(_Board):
    def test_zero_tags_grandfathers_the_task(self):               # M2, R:coverage_check_ungrandfathered
        self._make_task("legacy", _SEC1, "<scenarios>\nno tags here\n</scenarios>\n")
        out, code = self._run("check")
        self.assertNotIn("coverage gap", out, "a task with zero §2/§4 tags must never warn")
        self.assertEqual(code, 0)


class OneTagOptsIn(_Board):
    def test_one_tag_opts_the_task_in(self):                      # M2
        sec2 = "<scenarios>\nScenario: x   # M1\n  Given a\n  When b\n  Then c\n</scenarios>\n"
        self._make_task("opted", _SEC1, sec2)
        out, code = self._run("check")
        self.assertIn("M2", out, "once opted in, the untagged M2 must be flagged")
        self.assertIn("coverage gap", out)
        self.assertEqual(code, 0)


class CoversLineSatisfiesCoverage(_Board):
    def test_covers_line_alone_covers_a_must(self):               # M3
        sec2 = "<scenarios>\nScenario: x   # M1\n  Given a\n  When b\n  Then c\n</scenarios>\n"
        sec4 = "<test_plan>\n  - test_x: arrange a / act b / assert c · covers: M2\n</test_plan>\n"
        self._make_task("covered", _SEC1, sec2, sec4)
        out, code = self._run("check")
        self.assertNotIn("'M2'", out, "a §4 covers: line alone must satisfy coverage for M2")
        self.assertEqual(code, 0)


class UncoveredIdIsAGap(_Board):
    def test_uncovered_must_is_flagged_tagged_must_is_not(self):  # M3, R:false_coverage_gap
        sec2 = "<scenarios>\nScenario: x   # M1\n  Given a\n  When b\n  Then c\n</scenarios>\n"
        self._make_task("gap", _SEC1, sec2)
        out, code = self._run("check")
        self.assertIn("M2", out)
        self.assertNotIn("'M1'", out, "M1 IS tagged in §2 — must not be flagged")
        self.assertEqual(code, 0)


class WarnNeverBlocks(_Board):
    def test_gap_prints_as_warn_and_exits_zero(self):             # M4, R:coverage_warn_blocks
        sec2 = "<scenarios>\nScenario: x   # M1\n  Given a\n  When b\n  Then c\n</scenarios>\n"
        self._make_task("warned", _SEC1, sec2)
        out, code = self._run("check")
        self.assertIn("WARN", out)
        self.assertIn("Must", out)
        self.assertEqual(code, 0)


class TemplateGainsCoversAcrossTrees(unittest.TestCase):
    def test_covers_field_present_and_trees_match(self):          # M5
        present = [p for p in TEMPLATE_COPIES if p.exists()]
        self.assertTrue(present, "at least the canonical template must exist")
        texts = {p.read_text(encoding="utf-8") for p in present}
        self.assertEqual(len(texts), 1, "all template trees must be byte-identical")
        self.assertIn("covers:", texts.pop(), "§4's test_plan bullet must gain a covers: field")


class GapSurvivesDone(_Board):
    def test_gap_still_warns_once_task_is_done(self):             # M6, R:gap_skipped_on_done
        sec2 = "<scenarios>\nScenario: x   # M1\n  Given a\n  When b\n  Then c\n</scenarios>\n"
        self._make_task("shipped", _SEC1, sec2)
        self._force_phase("shipped", "done")
        out, code = self._run("check")
        self.assertIn("M2", out, "a coverage gap in a DONE task must still surface")
        self.assertEqual(code, 0)


class MalformedTaskDegradesSafely(_Board):
    def test_check_does_not_crash_on_malformed_task(self):        # R:check_crashes_on_malformed_task
        task_dir = self._task_md("broken").parent
        task_dir.mkdir(parents=True, exist_ok=True)
        self._task_md("broken").write_text("not a real TASK.md at all", encoding="utf-8")
        sp = self.tmp / ".add" / "state.json"
        st = json.loads(sp.read_text(encoding="utf-8"))
        st["tasks"]["broken"] = {"phase": "ground"}
        sp.write_text(json.dumps(st, indent=2), encoding="utf-8")
        out, code = self._run("check")     # must not raise
        self.assertIsInstance(out, str)


class DuplicateIdDoesNotCrash(unittest.TestCase):
    def test_duplicate_id_deduped_not_double_warned(self):        # edge case
        sec1 = "  - M1: first\n  - M1: duplicate of first\n"
        sec2 = "Scenario: x   # M9\n"       # M1 tagged nowhere -> both occurrences share one gap
        gaps = _rule_coverage_gaps(sec1, sec2, "")
        self.assertEqual(gaps.count(("M1", "Must")), 1,
                          "a duplicate ID must be reported once, not twice")


class RuleCoverageGapsPure(unittest.TestCase):
    def test_id_grammar_recognized(self):                          # M1
        sec1 = '  - M3: some behavior\n  - bad input -> "code_x"\n'
        sec2 = "Scenario: x   # M3, R:code_x\n"
        self.assertEqual(_rule_coverage_gaps(sec1, sec2, ""), [], "both tagged IDs are covered")

    def test_real_shipped_tag_grammar(self):                       # regex fidelity vs real usage
        # the ACTUAL form used by delta-task-backlink's §2 — comma-separated mixed Must/Reject
        sec2 = ("Scenario: x   # M2, R:backlink_clobbers_authored\n"
                "Scenario: y   # R:false_dangling_warn\n")
        sec1 = (
            "  - M2: a thing\n"
            '  - a clobber -> "backlink_clobbers_authored"\n'
            '  - a false warn -> "false_dangling_warn"\n'
        )
        self.assertEqual(_rule_coverage_gaps(sec1, sec2, ""), [])


class EnginePinnedAndPoolUntouched(unittest.TestCase):
    def test_engine_byte_identical_to_pin(self):                   # M7, R:engine_pin_drift
        present = [p for p in ADD_PY_COPIES if p.exists()]
        digests = {_md5(p) for p in present}
        self.assertEqual(len(digests), 1, "all add.py copies must be byte-identical")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                          "add.py must match the re-pinned engine_pin.ENGINE_MD5")

    def test_phases_pool_untouched(self):                          # M7
        from test_skill_lean import POOLS
        phases = next(p for p in POOLS if p["name"] == "phases")
        target = int(phases["baseline"] * phases["ratio"])
        nbytes = sum(len((_CANON_SKILL / g).read_bytes())
                     for g in PHASES_POOL if (_CANON_SKILL / g).exists())
        self.assertLessEqual(nbytes, target, f"phases pool {nbytes} B must stay <= {target}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
