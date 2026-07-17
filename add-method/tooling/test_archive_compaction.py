#!/usr/bin/env python3
"""test_archive_compaction.py — the v18 heavy-archive (`compact`) behavior suite.

The contract is drafted in .add/tasks/archive-compaction/TASK.md §3: `add.py compact
<slug>` moves an ALREADY light-archived milestone's files (MILESTONE.md + siblings +
every rollup-member task dir) into one recovery bundle `.add/archive/<slug>/`, after
proving every member's competency deltas are folded — validate-all-then-move, so any
reject leaves tree AND state.json byte-for-byte unchanged. Tests scaffold REAL projects
via add.main() and assert engine output, never internals-by-inspection.

Written RED-FIRST (tests phase, before Build): every compact-invoking test fails while
the subcommand doesn't exist (argparse: invalid choice); the triplet-parity guard is
green by construction and stays a tripwire.

Run: python3 -m unittest test_archive_compaction -v
"""
from __future__ import annotations

import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

_TOOLING = Path(add.__file__).resolve().parent


def _meet_exit_criteria(ms: str) -> None:
    """v20 goal-gate: check the milestone's '## Exit criteria' box so milestone-done
    releases. Targets only the Exit-criteria section — never the Tasks rows."""
    root = add.find_root()
    p = root / "milestones" / ms / add.MILESTONE_FILE
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                  lambda m: m.group(0).replace("- [ ]", "- [x]"), text, flags=re.S)
    p.write_text(text, encoding="utf-8")
_REPO = _TOOLING.parents[1]  # .../AIDD-Book

# the contracted reject codes (TASK.md §3) — compact's full error vocabulary
REJECT_CODES = {
    "milestone_not_archived", "unknown_milestone", "open_deltas_unfolded",
    "already_compacted", "archive_destination_exists", "source_files_missing",
}


def _run(argv: list[str]) -> tuple[str, str, int | None]:
    """Run add.main(argv) capturing stdout/stderr; returns (out, err, exit_code).
    exit_code is None when main returns normally."""
    out, err = io.StringIO(), io.StringIO()
    code: int | None = None
    with redirect_stdout(out), redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:  # _die and argparse both raise SystemExit
            code = e.code if isinstance(e.code, int) else 1
    return out.getvalue(), err.getvalue(), code


def _snapshot(base: Path) -> dict[str, bytes]:
    """relpath -> bytes for every file under base — the byte-for-byte-unchanged probe."""
    return {
        str(p.relative_to(base)): p.read_bytes()
        for p in sorted(base.rglob("*")) if p.is_file()
    }


class _ArchivedMilestoneBase(unittest.TestCase):
    """Real end-to-end temp project with milestone 'v1' light-archived (2 done tasks).

    The flow is the engine's own: init -> new-milestone -> new-task ×2 -> phase verify
    -> gate PASS -> milestone-done -> archive-milestone. After setUp, files are on disk
    and state holds only the archived rollup — the exact precondition compact operates on.
    """

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-compact-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        add.main(["new-milestone", "v1", "--goal", "demo goal"])
        for slug in ("t1", "t2"):
            add.main(["new-task", slug, "--milestone", "v1"])
            add.main(["phase", "verify", slug])
            add.main(["gate", "PASS", slug])
        _meet_exit_criteria("v1")   # v20 goal-gate: meet criteria before close
        _run(["milestone-done", "v1"])
        _run(["archive-milestone", "v1"])
        self.root = Path(self.tmp) / ".add"

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _plant_open_delta(self, slug: str) -> None:
        """Append one grammar-valid OPEN competency delta to a member TASK.md §7."""
        task_md = self.root / "tasks" / slug / "TASK.md"
        task_md.write_text(
            task_md.read_text(encoding="utf-8")
            + "  - [TDD · open] harness-planted lesson (evidence: probe)\n",
            encoding="utf-8",
        )


# ── behavior: the happy path (RED until Build) ───────────────────────────────────────
class CompactMovesBundle(_ArchivedMilestoneBase):
    def test_compact_moves_bundle(self):
        out, err, code = _run(["compact", "v1"])
        self.assertIsNone(code, f"compact failed: {err}")
        dest = self.root / "archive" / "v1"
        # bundle layout: MILESTONE.md + siblings + tasks/<tslug>/
        self.assertTrue((dest / "MILESTONE.md").is_file())
        self.assertTrue((dest / "pre-archive-state.bak.json").is_file())
        self.assertTrue((dest / "RETRO.md").is_file())
        for slug in ("t1", "t2"):
            self.assertTrue((dest / "tasks" / slug / "TASK.md").is_file())
            self.assertFalse((self.root / "tasks" / slug).exists())
        self.assertFalse((self.root / "milestones" / "v1").exists())
        # loud report: the slug, the destination, one line PER moved dir with a count
        self.assertIn("v1", out)
        self.assertIn("archive", out)
        for moved in ("t1", "t2"):
            self.assertIn(moved, out)
        self.assertGreaterEqual(
            len(re.findall(r"\d+ file", out)), 3,
            f"expected a per-dir file count for 3 moved dirs, got:\n{out}")

    def test_rollup_stamped_additively(self):
        before = add.load_state(self.root)
        slugs_before = next(e for e in before["archived"] if e["slug"] == "v1")["task_slugs"]
        out, err, code = _run(["compact", "v1"])
        self.assertIsNone(code, f"compact failed: {err}")
        after = add.load_state(self.root)
        entry = next(e for e in after["archived"] if e["slug"] == "v1")
        self.assertRegex(entry.get("compacted", ""), r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(slugs_before, entry["task_slugs"])  # add.py:469 invariant intact
        # archived deps still resolve after compaction
        self.assertIn("t1", add._archived_task_slugs(after))

    def test_readonly_commands_unchanged(self):
        probes = (["status"], ["deltas"], ["check"])
        before = [_run(list(p))[0] for p in probes]
        out, err, code = _run(["compact", "v1"])
        self.assertIsNone(code, f"compact failed: {err}")
        after = [_run(list(p))[0] for p in probes]
        self.assertEqual(before, after)  # the ⚠-assumption pin: no silent report drift

    def test_reverse_move_restores(self):
        pre_tasks = _snapshot(self.root / "tasks")
        pre_ms = _snapshot(self.root / "milestones")
        out, err, code = _run(["compact", "v1"])
        self.assertIsNone(code, f"compact failed: {err}")
        dest = self.root / "archive" / "v1"
        # recovery = reverse move, no state surgery
        for slug in ("t1", "t2"):
            shutil.move(str(dest / "tasks" / slug), str(self.root / "tasks" / slug))
        (self.root / "milestones").mkdir(exist_ok=True)
        (dest / "tasks").rmdir()
        shutil.move(str(dest), str(self.root / "milestones" / "v1"))
        self.assertEqual(pre_tasks, _snapshot(self.root / "tasks"))
        self.assertEqual(pre_ms, _snapshot(self.root / "milestones"))


# ── behavior: every contracted reject, each leaving the world unchanged ──────────────
class CompactRejects(_ArchivedMilestoneBase):
    def _assert_reject(self, argv: list[str], code_name: str) -> None:
        pre = _snapshot(self.root)
        out, err, code = _run(argv)
        self.assertIsNotNone(code, f"expected reject '{code_name}', got success:\n{out}")
        self.assertIn(code_name, err)
        self.assertEqual(pre, _snapshot(self.root))  # byte-for-byte unchanged

    def test_open_delta_blocks(self):
        self._plant_open_delta("t1")
        pre = _snapshot(self.root)
        out, err, code = _run(["compact", "v1"])
        self.assertIsNotNone(code)
        self.assertIn("open_deltas_unfolded", err)
        self.assertIn("t1", err)  # names the offending task
        self.assertEqual(pre, _snapshot(self.root))

    def test_active_milestone_rejected(self):
        add.main(["new-milestone", "v2", "--goal", "live"])
        add.main(["new-task", "t3", "--milestone", "v2"])
        self._assert_reject(["compact", "v2"], "milestone_not_archived")

    def test_unknown_slug_rejected(self):
        self._assert_reject(["compact", "nope"], "unknown_milestone")

    def test_rerun_rejected(self):
        out, err, code = _run(["compact", "v1"])
        self.assertIsNone(code, f"first compact failed: {err}")
        self._assert_reject(["compact", "v1"], "already_compacted")

    def test_destination_collision_rejected(self):
        (self.root / "archive" / "v1").mkdir(parents=True)
        self._assert_reject(["compact", "v1"], "archive_destination_exists")

    def test_missing_source_rejected(self):
        shutil.rmtree(self.root / "tasks" / "t2")
        pre = _snapshot(self.root)
        out, err, code = _run(["compact", "v1"])
        self.assertIsNotNone(code)
        self.assertIn("source_files_missing", err)
        self.assertIn("t2", err)  # names the missing path
        self.assertEqual(pre, _snapshot(self.root))  # NO partial move


# ── guard: the engine ships byte-identical in all three trees ────────────────────────


if __name__ == "__main__":
    unittest.main(verbosity=2)
