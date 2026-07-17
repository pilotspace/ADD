#!/usr/bin/env python3
"""Red/green tests for compact-force-override (delta-resolution-polish 3/3): a `--force`
flag on `add.py compact` overrides the `open_spec_deltas_unresolved` block ONLY — the
escape hatch for a settled milestone blocked by an unrelated open SPEC delta elsewhere.
CONTRACT frozen @ v1. --force absent → byte-identical block. --force bypasses + WARNS +
records `force_bypassed_spec_deltas` on the archived entry. It NEVER overrides a
structural guard (milestone_not_archived, unknown_milestone, …). Run:
  python3 -m unittest test_compact_force_override -v
"""
from __future__ import annotations

import hashlib
import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    try:
        with redirect_stdout(out), redirect_stderr(err):
            add.main(list(argv))
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
    return code, out.getvalue(), err.getvalue()


def _meet_exit_criteria(root: Path, ms: str) -> None:
    p = root / "milestones" / ms / add.MILESTONE_FILE
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                  lambda m: m.group(0).replace("- [ ]", "- [x]"), text, flags=re.S)
    p.write_text(text, encoding="utf-8")


def _snapshot(base: Path) -> dict:
    return {str(p.relative_to(base)): p.read_bytes()
            for p in sorted(base.rglob("*")) if p.is_file()}


class _ArchivedBase(unittest.TestCase):
    """Temp project with milestone 'v1' light-archived (2 done tasks) — the precondition
    compact operates on — plus a standalone task 'other' to carry an unrelated SPEC delta."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-cfo-")).resolve()
        os.chdir(self.tmp)
        _run(["init", "--name", "demo"])
        _run(["new-milestone", "v1", "--goal", "demo goal"])
        for slug in ("t1", "t2"):
            _run(["new-task", slug, "--milestone", "v1"])
            _run(["phase", "verify", slug])
            _run(["gate", "PASS", slug])
        self.root = self.tmp / ".add"
        _meet_exit_criteria(self.root, "v1")
        _run(["milestone-done", "v1"])
        _run(["archive-milestone", "v1"])

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _plant_open_spec(self, slug: str, text: str = "unrelated forward hand-off") -> None:
        """Create a standalone task and plant one open SPEC delta in its §7 OBSERVE."""
        _run(["new-task", slug, "--title", "Carrier"])
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        idx = s.index("## 7 · OBSERVE")
        he = s.index("\n", idx) + 1
        body = f"\n### Spec delta\n- [SPEC · open] {text} (evidence: ev)\n\n### Competency deltas\n"
        p.write_text(s[:he] + body, encoding="utf-8")

    def _archived_entry(self):
        state = add.load_state(self.root)
        return next(e for e in state.get("archived", []) if e.get("slug") == "v1")


class ForceOverrideTest(_ArchivedBase):
    def test_open_spec_blocks_without_force(self):
        self._plant_open_spec("other")
        pre = _snapshot(self.root)
        code, out, err = _run(["compact", "v1"])
        self.assertNotEqual(code, 0)
        self.assertIn("open_spec_deltas_unresolved", err)
        self.assertIn("--force", err)                       # the block names the escape hatch
        self.assertIn("other", err)                         # names the offender
        self.assertFalse((self.root / "archive" / "v1").exists())
        self.assertEqual(pre, _snapshot(self.root))         # byte-for-byte unchanged

    def test_force_bypasses_and_records(self):
        self._plant_open_spec("other")
        code, out, err = _run(["compact", "v1", "--force"])
        self.assertEqual(code, 0, err)
        self.assertTrue((self.root / "archive" / "v1" / "MILESTONE.md").is_file())
        # WARN is loud on stdout, names the construct AND the bypassed offender (not silent)
        self.assertIn("force_bypassed_spec_deltas", out)
        self.assertRegex(out, r"--force bypassed open SPEC delta.*other")
        entry = self._archived_entry()
        self.assertIn("other", entry.get("force_bypassed_spec_deltas", []))

    def test_force_clean_noop(self):
        # archive-ready, NO open SPEC delta anywhere → --force changes nothing but compacts
        code, out, err = _run(["compact", "v1", "--force"])
        self.assertEqual(code, 0, err)
        self.assertTrue((self.root / "archive" / "v1" / "MILESTONE.md").is_file())
        entry = self._archived_entry()
        self.assertNotIn("force_bypassed_spec_deltas", entry)   # no bypass key when nothing bypassed

    def test_force_does_not_override_structural(self):
        # an ACTIVE milestone — --force must NOT push it past the structural guard
        _run(["new-milestone", "v2", "--goal", "live"])
        _run(["new-task", "t3", "--milestone", "v2"])
        pre = _snapshot(self.root)
        code, out, err = _run(["compact", "v2", "--force"])
        self.assertNotEqual(code, 0)
        self.assertIn("milestone_not_archived", err)
        self.assertFalse((self.root / "archive" / "v2").exists())
        self.assertEqual(pre, _snapshot(self.root))

    def test_force_does_not_override_member_competency_delta(self):
        # --force is scoped to the SPEC guard ONLY — a member's open competency delta still blocks
        task_md = self.root / "tasks" / "t1" / "TASK.md"
        task_md.write_text(task_md.read_text(encoding="utf-8")
                           + "  - [TDD · open] planted lesson (evidence: probe)\n", encoding="utf-8")
        pre = _snapshot(self.root)
        code, out, err = _run(["compact", "v1", "--force"])
        self.assertNotEqual(code, 0)
        self.assertIn("open_deltas_unfolded", err)
        self.assertEqual(pre, _snapshot(self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
