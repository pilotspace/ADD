#!/usr/bin/env python3
"""Red→green guard for release-command §3 (FROZEN @ v1).

add.py release <version>: a GUARDED, record-only cut. It enforces the 4-code readiness floor
(release_security_open [UN-FORCEABLE] · release_tests_red · release_no_closed_milestone ·
release_undisclosed_waiver), then RECORDS by prepending CHANGELOG.md + an append-only
RELEASES.md row that attributes the bundled milestones. The engine records; it NEVER tags /
publishes / deploys / bumps a version source / writes state.json. Validate-before-write: a reject
leaves both files + state.json byte-for-byte unchanged. A failed second write rolls back the first.

RED until `release` exists (today argparse rejects the subcommand → non-zero exit).
Run standalone:  python3 -m unittest test_release_command -v
"""
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
_TOOLING = os.path.join(_ROOT, "add-method", "tooling")
if _TOOLING not in sys.path:
    sys.path.insert(0, _TOOLING)
import add  # noqa: E402  (canonical engine; the 3 homes are byte-identical, asserted below)

_ENGINES = [
    "add-method/tooling/add.py",
    ".add/tooling/add.py",
    "add-method/src/add_method/_bundled/tooling/add.py",
]
STATE = Path(".add/state.json")
CHANGELOG = Path("CHANGELOG.md")   # project root = the dir containing .add/
RELEASES = Path("RELEASES.md")


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


def _load():
    return json.loads(STATE.read_text(encoding="utf-8"))


def _save(s):
    STATE.write_text(json.dumps(s, indent=2), encoding="utf-8")


def _close_milestone(slug, goal="ship it"):
    """A CLOSED (milestone-done) live milestone — the releasable bundle."""
    s = _load()
    s.setdefault("milestones", {})[slug] = {"status": "done", "title": slug, "goal": goal}
    _save(s)


def _seed_task(slug, *, phase="done", gate="PASS", milestone="m1", waiver=None):
    """Seed a task record to drive a floor condition (HARD-STOP blocker, in-flight build, waiver)."""
    s = _load()
    rec = {"milestone": milestone, "phase": phase, "gate": gate}
    if waiver is not None:
        rec["waiver"] = waiver
    s.setdefault("tasks", {})[slug] = rec
    _save(s)


class ReleaseCommandTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-release-command-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ── Must / happy path ───────────────────────────────────────────────────────────────────
    def test_green_cut_writes_two_files_and_clears_cue(self):
        _close_milestone("m1")
        code, _, _ = _run(["release", "1.0.0"])
        self.assertEqual(code, 0, "a clean cut exits 0")
        cl = CHANGELOG.read_text(encoding="utf-8")
        rel = RELEASES.read_text(encoding="utf-8")
        self.assertIn("## 1.0.0", cl, "CHANGELOG gains the version block")
        self.assertIn("## 1.0.0", rel, "RELEASES gains the version row")
        self.assertRegex(rel, r"milestones:.*\bm1\b", "the row attributes the bundled milestone")
        _, rep, _ = _run(["release-report", "--json"])
        slugs = {r["slug"] for r in json.loads(rep)["releasable"]}
        self.assertNotIn("m1", slugs, "the attributed milestone is no longer releasable")

    def test_green_cut_does_not_touch_state(self):
        _close_milestone("m1")
        before = STATE.read_bytes()
        _run(["release", "1.0.0"])
        self.assertEqual(STATE.read_bytes(), before, "release records via the ledger, NEVER state.json")

    def test_ledger_append_only_newest_first(self):
        _close_milestone("m1")
        _run(["release", "1.0.0"])
        first = RELEASES.read_text(encoding="utf-8")
        _close_milestone("m2")
        _run(["release", "2.0.0"])
        rel = RELEASES.read_text(encoding="utf-8")
        self.assertLess(rel.index("## 2.0.0"), rel.index("## 1.0.0"), "newest row is on top")
        self.assertIn("milestones: m1", first.replace(",", ""))  # the 1.0.0 row existed
        self.assertIn("## 1.0.0", rel, "the prior row is preserved (append-only)")

    def test_with_waivers_discloses_and_cuts(self):
        _close_milestone("m1")
        _seed_task("waived-task", gate="RISK-ACCEPTED",
                   waiver={"owner": "tin", "ticket": "JIRA-1", "expires": "2099-01-01"})
        code, _, _ = _run(["release", "1.0.0", "--with-waivers"])
        self.assertEqual(code, 0, "disclosing the waiver lets the cut proceed")
        self.assertRegex(RELEASES.read_text(encoding="utf-8"),
                         r"waivers:.*waived-task", "the row records the disclosed waiver slug")

    def test_force_overrides_red_build(self):
        _close_milestone("m1")
        _seed_task("wip", phase="build", gate="none")    # in-flight build → release_tests_red
        code, _, _ = _run(["release", "1.0.0", "--force"])
        self.assertEqual(code, 0, "--force overrides a forceable reject (release_tests_red)")
        self.assertTrue(RELEASES.exists(), "the forced cut was recorded")

    # ── Reject ──────────────────────────────────────────────────────────────────────────────
    def test_security_hardstop_unforceable(self):
        _close_milestone("m1")
        _seed_task("sec", gate="HARD-STOP")
        before_state = STATE.read_bytes()
        code, _, err = _run(["release", "1.0.0", "--force"])   # even with --force
        self.assertNotEqual(code, 0, "an open HARD-STOP refuses the cut")
        self.assertIn("release_security_open", err)
        self.assertFalse(CHANGELOG.exists() or RELEASES.exists(), "a reject writes nothing")
        self.assertEqual(STATE.read_bytes(), before_state, "state.json untouched on reject")

    def test_inflight_build_blocks(self):
        _close_milestone("m1")
        _seed_task("wip", phase="build", gate="none")
        code, _, err = _run(["release", "1.0.0"])
        self.assertNotEqual(code, 0)
        self.assertIn("release_tests_red", err)
        self.assertFalse(RELEASES.exists(), "a reject writes nothing")

    def test_no_closed_milestone_refused(self):
        # nothing closed at all → nothing releasable
        code, _, err = _run(["release", "1.0.1"])
        self.assertNotEqual(code, 0)
        self.assertIn("release_no_closed_milestone", err)
        self.assertFalse(CHANGELOG.exists() or RELEASES.exists())

    def test_undisclosed_waiver_blocks(self):
        _close_milestone("m1")
        _seed_task("waived-task", gate="RISK-ACCEPTED",
                   waiver={"owner": "tin", "ticket": "JIRA-1", "expires": "2099-01-01"})
        code, _, err = _run(["release", "1.0.0"])           # no --with-waivers
        self.assertNotEqual(code, 0)
        self.assertIn("release_undisclosed_waiver", err)
        self.assertFalse(RELEASES.exists())

    def test_failed_second_write_rolls_back_first(self):
        _close_milestone("m1")
        before_state = STATE.read_bytes()
        orig = add._atomic_write

        def boom(path, text):
            if str(path).endswith("RELEASES.md"):
                raise OSError("simulated disk failure on the ledger write")
            return orig(path, text)

        add._atomic_write = boom
        try:
            code, _, err = _run(["release", "1.0.0"])
        finally:
            add._atomic_write = orig
        self.assertNotEqual(code, 0)
        self.assertIn("release_write_failed", err)
        self.assertFalse(CHANGELOG.exists(), "CHANGELOG rolled back (it did not exist before)")
        self.assertFalse(RELEASES.exists())
        self.assertEqual(STATE.read_bytes(), before_state, "state.json untouched")

    def test_no_project(self):
        empty = tempfile.mkdtemp(prefix="add-release-cmd-empty-")
        os.chdir(empty)
        try:
            code, _, err = _run(["release", "1.0.0"])
            self.assertNotEqual(code, 0)
            self.assertIn("no_project", err)
        finally:
            os.chdir(self.tmp)

    def test_engine_3home_parity(self):
        digests = {p: hashlib.md5((Path(_ROOT) / p).read_bytes()).hexdigest() for p in _ENGINES}
        self.assertEqual(len(set(digests.values())), 1, f"engine homes diverged (engine-drift): {digests}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
