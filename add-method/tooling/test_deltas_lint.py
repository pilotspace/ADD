#!/usr/bin/env python3
"""Behavioral proof of `add.py check` delta-grammar/routing guard (task: deltas-lint, v10).

CONTRACT (frozen @ v1): `check` scans every task's "### Competency deltas" block; each
non-comment line beginning "- [" MUST fully parse `- [<COMP> · <status>] <text> (evidence: …)`
with COMP ∈ {DDD,SDD,UDD,TDD,ADD}, status ∈ {open,folded,rejected}, evidence required. It emits
one "task '<slug>' deltas well-formed" check per task with a delta block; a malformed/unroutable
line FAILS it (check exits 1) with a code (unknown_competency|unknown_status|no_evidence|
malformed_delta). Comment lines are skipped. Fail-closed, read-only. One test per SCENARIO.
Run: python3 -m unittest test_deltas_lint -v
"""
import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

import add


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class DeltasLintTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-deltas-lint-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _add_deltas(self, slug, *lines):
        root = add.find_root()
        if slug not in (add.load_state(root).get("tasks") or {}):
            add.main(["new-task", slug, "--title", "Feature"])
        p = Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"
        text = p.read_text(encoding="utf-8")
        marker = "### Competency deltas"
        idx = text.index(marker) + len(marker)
        p.write_text(text[:idx] + "\n" + "\n".join(lines) + "\n" + text[idx:],
                     encoding="utf-8")

    # --- scenarios -----------------------------------------------------------
    def test_well_formed_deltas_pass(self):
        self._add_deltas("a",
                         "- [TDD · open] valid one (evidence: e)",
                         "- [DDD · folded] valid two (evidence: e)")
        code, out, _ = _run(["check"])
        self.assertIn("deltas well-formed", out, "the delta-lint check did not run")
        self.assertNotIn("unknown_competency", out)
        self.assertNotIn("malformed_delta", out)
        self.assertEqual(code, 0, "well-formed deltas must not fail check")

    def test_unknown_competency_fails(self):
        self._add_deltas("a", "- [XYZ · open] bad competency (evidence: e)")
        code, out, _ = _run(["check"])
        self.assertEqual(code, 1)
        self.assertIn("unknown_competency", out)

    def test_unknown_status_fails(self):
        self._add_deltas("a", "- [TDD · pending] bad status (evidence: e)")
        code, out, _ = _run(["check"])
        self.assertEqual(code, 1)
        self.assertIn("unknown_status", out)

    def test_missing_evidence_fails(self):
        self._add_deltas("a", "- [TDD · open] a learning with no evidence pointer")
        code, out, _ = _run(["check"])
        self.assertEqual(code, 1)
        self.assertIn("no_evidence", out)

    def test_comment_malformed_ignored(self):
        self._add_deltas("a",
                         "- [TDD · open] real valid (evidence: e)",
                         "<!-- e.g. - [XYZ · bogus] commented malformed line -->")
        code, out, _ = _run(["check"])
        self.assertIn("deltas well-formed", out, "the delta-lint check did not run")
        self.assertEqual(code, 0, "a malformed line inside an HTML comment must be skipped")
        self.assertNotIn("unknown_competency", out)

    def test_multiline_open_evidence_on_continuation_passes(self):
        # a real-world shape: the tag line wraps; (evidence: …) lands on the next line
        self._add_deltas("a",
                         "- [ADD · open] a learning whose sentence wraps across lines and keeps",
                         "  going here (evidence: this build) with more trailing prose")
        code, out, _ = _run(["check"])
        self.assertIn("deltas well-formed", out, "the delta-lint check did not run")
        self.assertEqual(code, 0, "evidence on a continuation line must satisfy the guard")

    def test_folded_multiline_without_evidence_skipped(self):
        # historical folded entries are NOT retrofitted, even if they lack inline evidence
        self._add_deltas("a",
                         "- [TDD · folded] a historical learning that wraps and never",
                         "  carries an inline evidence pointer at all")
        code, out, _ = _run(["check"])
        self.assertIn("deltas well-formed", out, "the delta-lint check did not run")
        self.assertEqual(code, 0, "folded history must be skipped, not re-validated")
        self.assertNotIn("no_evidence", out)

    def test_unreadable_task_emits_no_check(self):
        # design-for-failure: an existing-but-unreadable TASK.md yields no lint check
        # (None), never a crash/traceback.
        from unittest import mock
        self._add_deltas("a", "- [TDD · open] one (evidence: e)")
        root = add.find_root()
        with mock.patch.object(Path, "read_text", side_effect=OSError("boom")):
            result = add._lint_task_deltas(root, "a")
        self.assertIsNone(result, "unreadable TASK.md must yield no check (None), not a crash")


if __name__ == "__main__":
    unittest.main(verbosity=2)
