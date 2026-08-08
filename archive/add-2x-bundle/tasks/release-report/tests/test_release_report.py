#!/usr/bin/env python3
"""Red→green guard for release-report §3 (FROZEN @ v1).

add.py release-report: a READ-ONLY gather of the release inventory into 5 record-sets
(releasable · changed · waivers · blockers · monitors + summary), text + --json, exit 0
ALWAYS (only no_project non-zero), PURE (no writes). Plus the `→ releasable: N` status cue
and the RELEASES.md attribution-read (a milestone is released iff its slug is on a
`milestones:` line; missing/malformed ledger → fail-open: all closed releasable). The 3
engine homes stay byte-identical.

RED until release-report exists (today argparse rejects the subcommand → non-zero exit).
Run standalone:  python3 -m unittest test_release_report -v
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
# judgment tokens the gather must NEVER emit (gather-not-judge invariant; shared with graduation)
FORBIDDEN = ("readiness", "recommend", "ranking", "verdict", "score")
STATE = Path(".add/state.json")


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


def _close_milestone(slug, goal="ship it", archived=False):
    """Register a CLOSED (milestone-done gate passed) milestone — live-done OR archived."""
    s = _load()
    if archived:
        s.setdefault("archived", []).append({"slug": slug, "title": slug, "tasks": 1})
    else:
        s.setdefault("milestones", {})[slug] = {"status": "done", "title": slug, "goal": goal}
    _save(s)


def _write_releases(text):
    # project root = the directory containing .add/  (find_root() returns the .add dir)
    Path("RELEASES.md").write_text(text, encoding="utf-8")


_LEDGER_M1 = "# Releases\n\n## 1.0.0 — 2026-06-16\nmilestones: m1\nwaivers: none\nevidence: x\n"


class ReleaseReportTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-release-report-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ── Must ──────────────────────────────────────────────────────────────────────────────
    def test_release_data_five_sets(self):
        _close_milestone("m1")
        code, out, _ = _run(["release-report", "--json"])
        self.assertEqual(code, 0)
        d = json.loads(out)
        for k in ("releasable", "changed", "waivers", "blockers", "monitors", "summary"):
            self.assertIn(k, d, f"the {k!r} record-set must be present")

    def test_release_data_pure(self):
        _close_milestone("m1")
        before = STATE.read_bytes()
        _run(["release-report"])
        _run(["release-report", "--json"])
        self.assertEqual(STATE.read_bytes(), before, "release-report must not mutate state (report-not-pure)")
        self.assertFalse(Path("RELEASES.md").exists(), "a read must not write RELEASES.md (report-not-pure)")

    def test_exit_zero_always(self):
        _close_milestone("m1")
        code, _, _ = _run(["release-report"])
        self.assertEqual(code, 0, "a normal gather exits 0")
        empty = tempfile.mkdtemp(prefix="add-release-empty-")
        os.chdir(empty)
        try:
            code2, _, _ = _run(["release-report"])
            self.assertNotEqual(code2, 0, "no_project must exit non-zero")
        finally:
            os.chdir(self.tmp)

    def test_cue_fires_and_clears(self):
        _close_milestone("m1")
        _, out, _ = _run(["status"])
        self.assertIn("releasable", out.lower(), "the cue must fire for a closed-unreleased milestone")
        _write_releases(_LEDGER_M1)
        _, out2, _ = _run(["status"])
        self.assertNotIn("→ releasable", out2, "the cue clears once the milestone is attributed")

    def test_attribution_read(self):
        _close_milestone("m1")
        _close_milestone("m2")
        _write_releases(_LEDGER_M1)
        _, out, _ = _run(["release-report", "--json"])
        slugs = {r["slug"] for r in json.loads(out)["releasable"]}
        self.assertNotIn("m1", slugs, "an attributed milestone is not releasable")
        self.assertIn("m2", slugs, "an unattributed closed milestone stays releasable")

    def test_fail_open_ledger(self):
        _close_milestone("m1")
        _write_releases("garbage ::: not a ledger\n\n###\n")
        code, out, _ = _run(["release-report", "--json"])
        self.assertEqual(code, 0, "a malformed ledger must not crash")
        slugs = {r["slug"] for r in json.loads(out)["releasable"]}
        self.assertIn("m1", slugs, "malformed ledger → fail-open (all closed releasable)")

    def test_not_judging(self):
        _close_milestone("m1")
        _, out, _ = _run(["release-report", "--json"])
        low = out.lower()
        for bad in FORBIDDEN:
            self.assertNotIn(bad, low, f"gather-not-judge: must not emit {bad!r}")

    # ── Reject ────────────────────────────────────────────────────────────────────────────
    def test_engine_3home_parity(self):
        digests = {p: hashlib.md5((Path(_ROOT) / p).read_bytes()).hexdigest() for p in _ENGINES}
        self.assertEqual(len(set(digests.values())), 1, f"engine homes diverged (engine-drift): {digests}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
