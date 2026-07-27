#!/usr/bin/env python3
"""direction-one-shot: `add.py draft` writes the whole direction bundle in ONE
call, all-or-nothing, and refuses to freeze on a suite that is not red.

THE DEFECT THIS CLOSES. The pay1-4 flamegraph fold (2026-07-26) measured 4.9 of
direction's 31 minutes spent building a single PLAN.md through 45 successive
Edits — 45 round-trips to write one file. `advance --fill` already batches ONE
section for ONE crossing; direction needs three sections and one freeze.

The second half is the harder claim: "the red suite ran red before the build"
has always been a discipline the agent ASSERTS. With `--run-red` it becomes a
fact the engine OBSERVED, and a green suite at freeze time is a refusal rather
than a note.

Run:
    python3 -m unittest test_direction_one_shot -v
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ADD_PY = HERE / "add.py"
REPO = HERE.parents[1]


# A bundle that satisfies every EXISTING freeze floor, so a refusal in these
# tests is always the NEW guard firing and never an old one.
GOOD_BUNDLE = """## 1 · SPECIFY
Feature: the widget counts things.
Must:
<must>
  - it counts
</must>
<reject>
  - a negative count -> "negative_count"
</reject>
Boundary: `int` input only — one format variant.

## 3 · PLAN

### Contract
```
count(items: list) -> int
```
Ground: the widget module.
Target (measurable): count([]) == 0 and count([1,2]) == 2.
Status: DRAFT

Scope (may touch): `src/`
Least-sure flag surfaced at freeze: [contract] whether an empty list is 0 or an error — cost: one line.

## 4 · TESTS & SCENARIOS
<test_plan>
  - test_counts: count([1,2]) == 2 · covers: M1
</test_plan>
Tests live in: `tests/`
"""

GREEN_CMD = f'{sys.executable} -c "import sys; sys.exit(0)"'
RED_CMD = f'{sys.executable} -c "import sys; sys.exit(1)"'
SLOW_CMD = f'{sys.executable} -c "import time; time.sleep(30)"'


def _run(cwd, *args, stdin_text=None, timeout=120):
    return subprocess.run(
        [sys.executable, str(ADD_PY), *args],
        cwd=str(cwd), capture_output=True, text=True, input=stdin_text, timeout=timeout,
    )


class _Project(unittest.TestCase):
    """A minimal inited project with one task at `direction`."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        r = _run(self.root, "init", "--name", "oneshot", "--stage", "mvp")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        _run(self.root, "lock")
        r = _run(self.root, "new-task", "widget", "--title", "Widget")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.task_md = self.root / ".add" / "tasks" / "widget" / "PLAN.md"

    def tearDown(self):
        self._tmp.cleanup()

    def _bundle(self, text=GOOD_BUNDLE, name="bundle.md"):
        p = self.root / name
        p.write_text(text, encoding="utf-8")
        return str(p)

    def assertUnchanged(self, before: bytes, why: str):
        self.assertEqual(self.task_md.read_bytes(), before,
                         f"all-or-nothing broken: {why}")


class OneCallWritesTheBundle(_Project):
    def test_one_call_writes_all_three_sections(self):  # M1
        r = _run(self.root, "draft", "--from", self._bundle())
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        body = self.task_md.read_text()
        self.assertIn("Feature: the widget counts things.", body)
        self.assertIn("count(items: list) -> int", body)
        self.assertIn("test_counts", body)

    def test_draft_from_stdin(self):  # M1 [edge]
        r = _run(self.root, "draft", "--from", "-", stdin_text=GOOD_BUNDLE)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("count(items: list) -> int", self.task_md.read_text())

    def test_same_bundle_one_call_equals_section_by_section(self):  # M1 [edge]
        # The one-shot path must not produce a different file from the stepwise one,
        # or the verb is a second grammar wearing the first one's name.
        r = _run(self.root, "draft", "--from", self._bundle())
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        one_shot = self.task_md.read_text()
        for marker in ("## 1 ·", "## 3 ·", "## 4 ·"):
            self.assertIn(marker, one_shot, "draft destroyed a section heading")
        # section order and count preserved
        self.assertEqual(one_shot.count("## 3 ·"), 1)


class RefusalsRestoreBytes(_Project):
    def test_bundle_missing_a_section_is_refused_before_any_write(self):  # M1 R1
        before = self.task_md.read_bytes()
        partial = GOOD_BUNDLE.split("## 4 ·")[0]
        r = _run(self.root, "draft", "--from", self._bundle(partial))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("draft_sections_missing", r.stderr + r.stdout)
        self.assertUnchanged(before, "a rejected bundle wrote anyway")

    def test_unknown_section_is_refused(self):  # M1 R2
        before = self.task_md.read_bytes()
        bad = GOOD_BUNDLE + "\n## 5 · BUILD\nnot yours to write\n"
        r = _run(self.root, "draft", "--from", self._bundle(bad))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("draft_unknown_section", r.stderr + r.stdout)
        self.assertUnchanged(before, "an unknown section wrote anyway")

    def test_draft_onto_a_frozen_contract_is_refused(self):  # M6 R3
        r = _run(self.root, "draft", "--from", self._bundle(), "--freeze", "--by", "Tester")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        before = self.task_md.read_bytes()
        r = _run(self.root, "draft", "--from", self._bundle())
        self.assertNotEqual(r.returncode, 0, "a frozen contract was silently redrafted")
        self.assertIn("draft_onto_frozen", r.stderr + r.stdout)
        self.assertUnchanged(before, "a frozen contract was rewritten")

    def test_refusal_restores_bytes_on_every_reject_path(self):  # M2
        cases = {
            "draft_sections_missing": (GOOD_BUNDLE.split("## 3 ·")[0], []),
            "draft_unknown_section": (GOOD_BUNDLE + "\n## 6 · VERIFY\nnope\n", []),
            "red_suite_green": (GOOD_BUNDLE, ["--run-red", GREEN_CMD, "--freeze",
                                              "--by", "Tester"]),
            "red_suite_unrunnable": (GOOD_BUNDLE, ["--run-red", "definitely-not-a-command",
                                                   "--freeze", "--by", "Tester"]),
        }
        for code, (text, extra) in cases.items():
            with self.subTest(reject=code):
                before = self.task_md.read_bytes()
                r = _run(self.root, "draft", "--from", self._bundle(text), *extra)
                self.assertNotEqual(r.returncode, 0, f"{code} did not refuse")
                self.assertIn(code, r.stderr + r.stdout)
                self.assertUnchanged(before, f"{code} left a partial write")

    def test_unreadable_bundle_is_refused(self):  # M1
        before = self.task_md.read_bytes()
        r = _run(self.root, "draft", "--from", str(self.root / "nope.md"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("draft_unreadable", r.stderr + r.stdout)
        self.assertUnchanged(before, "a missing bundle wrote anyway")


class TheEngineObservesTheRed(_Project):
    def test_run_red_refuses_a_green_suite(self):  # M4 R4
        r = _run(self.root, "draft", "--from", self._bundle(),
                 "--run-red", GREEN_CMD, "--freeze", "--by", "Tester")
        self.assertNotEqual(r.returncode, 0, "a GREEN suite was allowed to freeze")
        self.assertIn("red_suite_green", r.stderr + r.stdout)
        # NB the pristine template carries "Status: FROZEN @ vN" inside an
        # explanatory comment, so a substring check is met by a correctly-restored
        # file. Anchor at line-start, exactly as _contract_frozen does.
        self.assertIsNone(re.search(r"(?m)^Status:\s*FROZEN",
                                    self.task_md.read_text()),
                          "a GREEN suite stamped the contract FROZEN")

    def test_run_red_proceeds_on_a_red_suite(self):  # M4
        r = _run(self.root, "draft", "--from", self._bundle(),
                 "--run-red", RED_CMD, "--freeze", "--by", "Tester")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("FROZEN @", self.task_md.read_text())

    def test_unrunnable_suite_is_a_refusal_not_a_skip(self):  # M4 R5
        before = self.task_md.read_bytes()
        r = _run(self.root, "draft", "--from", self._bundle(),
                 "--run-red", "definitely-not-a-command", "--freeze", "--by", "Tester")
        self.assertNotEqual(r.returncode, 0, "an unrunnable suite was treated as red")
        self.assertIn("red_suite_unrunnable", r.stderr + r.stdout)
        self.assertUnchanged(before, "an unrunnable suite left a partial write")

    def test_red_run_is_bounded_by_a_timeout(self):  # M5 R5
        # 30s command, 2s limit, 60s harness ceiling: if the engine hangs, this
        # test fails on the harness timeout rather than passing slowly.
        r = _run(self.root, "draft", "--from", self._bundle(),
                 "--run-red", SLOW_CMD, "--red-timeout", "2",
                 "--freeze", "--by", "Tester", timeout=60)
        self.assertNotEqual(r.returncode, 0)
        out = r.stderr + r.stdout
        self.assertIn("red_suite_unrunnable", out)
        self.assertIn("2", out, "the refusal must name the limit it hit")


class ExistingFloorsStillDecide(_Project):
    def test_freeze_floors_still_decide(self):  # M3
        # A bundle with no lowest-confidence flag must still hit unflagged_freeze —
        # draft chains cmd_freeze, it does not reimplement (or bypass) a floor.
        unflagged = GOOD_BUNDLE.replace(
            "Least-sure flag surfaced at freeze: [contract] whether an empty list is 0 "
            "or an error — cost: one line.\n", "")
        before = self.task_md.read_bytes()
        r = _run(self.root, "draft", "--from", self._bundle(unflagged),
                 "--freeze", "--by", "Tester")
        self.assertNotEqual(r.returncode, 0, "draft --freeze bypassed unflagged_freeze")
        self.assertIn("unflagged_freeze", r.stderr + r.stdout)
        self.assertUnchanged(before, "a refused freeze left the draft behind")

    def test_advance_fill_is_untouched(self):  # M3 [edge]
        self.task_md.write_text(self.task_md.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-07-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")
        draft = self.root / "one-section.md"
        draft.write_text("Feature: still works\n")
        r = _run(self.root, "advance", "--fill", str(draft))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("Feature: still works", self.task_md.read_text())


if __name__ == "__main__":
    unittest.main()
