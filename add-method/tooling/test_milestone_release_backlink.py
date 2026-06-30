#!/usr/bin/env python3
"""Red/green tests for milestone-release-backlink — the engine-stamped MILESTONE.md `release:`.

The milestone↔release link becomes a self-describing header backlink the engine SEEDS
(`release: pending` at new-milestone) and STAMPS (`release: <version>` at the cut), mirroring
task-milestone-backlink one scope-level up. Frozen shape (§3 @ v1):
  - MILESTONE.md.tmpl gains a literal `release: pending` header line (after `stage: … created:`);
  - `add.py release <v>` rewrites/inserts each BUNDLED milestone's `release:` line to <v>, and the
    stamp writes RIDE cmd_release's existing all-or-nothing _atomic_write_many batch (rollback-safe);
  - INVARIANTS: every add.py == engine_pin.ENGINE_MD5 (re-pinned); MILESTONE.md.tmpl ×3 byte-identical;
    the phases lean pool stays within budget (no phase-guide prose).

Run: cd add-method/tooling && python3 -m unittest test_milestone_release_backlink -v
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
from unittest import mock

import add
import engine_pin

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

MILE_TMPL_COPIES = [
    HERE / "templates" / "MILESTONE.md.tmpl",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "MILESTONE.md.tmpl",
    REPO / ".add" / "tooling" / "templates" / "MILESTONE.md.tmpl",
]
ADD_PY_COPIES = [
    HERE / "add.py",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
]
_CANON_SKILL = HERE.parent / "skill" / "add"
PHASES_POOL = [
    "phases/0-ground.md", "phases/0-setup.md", "phases/1-specify.md",
    "phases/2-scenarios.md", "phases/3-contract.md", "phases/4-tests.md",
    "phases/5-build.md", "phases/6-verify.md", "phases/7-observe.md",
]
_REL_LINE = re.compile(r"(?m)^release:\s*(.+?)\s*$")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class _Board(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-mrbl-")).resolve()
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

    def _mile_md(self, slug: str) -> Path:
        return self.tmp / ".add" / "milestones" / slug / "MILESTONE.md"

    def _release_line(self, slug: str):
        m = _REL_LINE.search(self._mile_md(slug).read_text(encoding="utf-8"))
        return m.group(1) if m else None

    def _closed_milestone(self, slug="v1"):
        """A closed-and-unreleased milestone. Created via the CLI (so its MILESTONE.md exists),
        then marked done directly in state.json — the release bundle reads `status == done`, and
        driving a full task→gate→goal-gate close is out of scope for this fixture."""
        self._silent("new-milestone", slug, "--goal", "g", "--stage", "mvp")
        sp = self.tmp / ".add" / "state.json"
        st = json.loads(sp.read_text(encoding="utf-8"))
        st["milestones"][slug]["status"] = "done"
        sp.write_text(json.dumps(st, indent=2), encoding="utf-8")


class NewMilestoneSeedsPending(_Board):
    def test_new_milestone_has_release_pending(self):            # M1
        self._silent("new-milestone", "v1", "--goal", "g", "--stage", "mvp")
        self.assertEqual(self._release_line("v1"), "pending",
                         "a new milestone must seed `release: pending`")


class ReleaseStampsBundle(_Board):
    def test_release_stamps_bundled_milestone(self):             # M2
        self._closed_milestone("v1")
        self.assertEqual(self._release_line("v1"), "pending")
        self._silent("release", "1.0.0")
        self.assertEqual(self._release_line("v1"), "1.0.0",
                         "release must stamp the bundled milestone's `release:` line")
        rel = (self.tmp / "RELEASES.md").read_text(encoding="utf-8")
        self.assertIn("v1", rel)

    def test_grandfathered_milestone_inserted(self):            # M3, R:release_insert_crash
        self._closed_milestone("v1")
        p = self._mile_md("v1")
        p.write_text(_REL_LINE.sub("", p.read_text(encoding="utf-8"), count=1), encoding="utf-8")
        self.assertIsNone(self._release_line("v1"), "precondition: the release line is stripped")
        _, code = self._run("release", "1.0.0")
        self.assertEqual(code, 0, "release must INSERT the line, not crash, for a grandfathered file")
        self.assertEqual(self._release_line("v1"), "1.0.0")


class StampRidesAtomicBatch(_Board):
    def test_failed_cut_rolls_back_stamp_and_ledgers(self):     # M3, R:stamp_breaks_atomicity
        self._closed_milestone("v1")
        changelog = self.tmp / "CHANGELOG.md"
        with mock.patch.object(add, "_atomic_write_many", side_effect=OSError("boom")):
            _, code = self._run("release", "1.0.0")
        self.assertNotEqual(code, 0, "a failed batch write must fail the cut")
        # the stamp must NOT have landed (it rode the same batch) and no ledger was created
        self.assertEqual(self._release_line("v1"), "pending",
                         "the stamp must roll back with the ledger (one atomic batch)")
        self.assertFalse(changelog.exists(), "CHANGELOG must not be half-written")


class EnginePinnedAndTemplateParity(unittest.TestCase):
    def test_template_has_release_field_and_is_parity(self):    # M1, M4
        present = [p for p in MILE_TMPL_COPIES if p.exists()]
        self.assertEqual(len(present), 3, "all 3 MILESTONE.md.tmpl copies must exist")
        for p in present:
            self.assertIn("release:", p.read_text(encoding="utf-8"),
                          "MILESTONE.md.tmpl must carry a `release:` header field")
        self.assertEqual(len({_md5(p) for p in present}), 1,
                         "the 3 MILESTONE.md.tmpl copies must be byte-identical")

    def test_engine_byte_identical_to_pin(self):                # M4, R:engine_pin_drift
        present = [p for p in ADD_PY_COPIES if p.exists()]
        digests = {_md5(p) for p in present}
        self.assertEqual(len(digests), 1, "all add.py copies must be byte-identical")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "add.py must match the re-pinned engine_pin.ENGINE_MD5")

    def test_phases_pool_untouched_within_budget(self):         # M4
        from test_skill_lean import POOLS
        phases = next(p for p in POOLS if p["name"] == "phases")
        target = int(phases["baseline"] * phases["ratio"])
        nbytes = sum(len((_CANON_SKILL / g).read_bytes())
                     for g in PHASES_POOL if (_CANON_SKILL / g).exists())
        self.assertLessEqual(nbytes, target,
                             f"phases pool {nbytes} B must stay ≤ {target} (no phase-guide prose)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
