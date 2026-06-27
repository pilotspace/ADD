#!/usr/bin/env python3
"""Red/green tests for the open-SPEC-delta RELEASE floor + the carry/reopen delta lifecycle
(milestone flow-honesty, task `delta-drain`).

CONTRACT (frozen @ v1) — backpressure so SPEC deltas resolve instead of accumulating:
  add.py release <v> [--force]
    FLOOR (after release_undisclosed_waiver): open SPEC deltas > 0 and not --force
      -> "release_open_spec_deltas" (forceable; release_security_open stays un-forceable).
      validate-before-write: CHANGELOG/RELEASES/state byte-unchanged on reject.
  release_data[...]["open_spec_deltas"] = {count, items}   (PURE; wraps _collect_open_spec_deltas)
  add.py carry-delta <slug> [--match S | --all] --reason "<t>"
    -> [SPEC · open] -> [SPEC · carried] + " [carried: <t>]"  (text + (evidence:) byte-preserved)
    reject: carry_reason_required · no_open_spec_delta · ambiguous_spec_delta
  add.py reopen-delta <slug> [--match S]   -> [SPEC · carried] -> [SPEC · open]
    reject: no_carried_spec_delta
  add.py deltas [--carried | --all]   -> carried section (retrieval); bare = open only (unchanged)
  add.py status   -> PRESENT-ONLY "stale : N open SPEC delta(s)" when N>0 (byte-identical at 0)
  Lifecycle: open <-> carried -> {seeded | dropped}.  carried JOINS _SPEC_DELTA_RE / _SPEC_STATUSES.
One test per scenario.
Run: python3 -m unittest test_delta_drain -v
"""
import contextlib
import io
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-drain-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("lock", "--force")

    def tearDown(self):
        os.chdir(self._cwd)

    # --- harness -------------------------------------------------------------
    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return code, out.getvalue() + err.getvalue()

    def _root(self):
        return self.tmp / ".add"

    def _task_md(self, slug):
        return self._root() / "tasks" / slug / "TASK.md"

    def _state(self):
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _mk(self, slug):
        if slug not in (self._state().get("tasks") or {}):
            self._silent("new-task", slug, "--title", "Feature")
        return self._task_md(slug)

    def _set_spec(self, slug, *open_texts):
        """Give `slug` one '- [SPEC · open] <t> (evidence: ev)' line per open_texts."""
        p = self._mk(slug)
        text = p.read_text(encoding="utf-8")
        idx = text.index("## 7 · OBSERVE")
        head_end = text.index("\n", idx) + 1
        lines = "".join(f"- [SPEC · open] {t} (evidence: ev)\n" for t in open_texts)
        body = f"\n### Spec delta\n{lines}\n### Competency deltas\n"
        p.write_text(text[:head_end] + body, encoding="utf-8")
        return p

    def _loose_done(self, slug="loose1"):
        """A milestone-free task carried to PASS — makes the project releasable.
        `phase verify` jumps past build, so the universal freeze gate is not crossed."""
        self._silent("new-task", slug, "--title", "Standalone")
        self._silent("phase", "verify", slug)
        self._silent("gate", "PASS", slug)

    def _hardstop(self, slug="sec"):
        self._silent("new-task", slug, "--title", "Security")
        self._silent("phase", "verify", slug)
        self._silent("gate", "HARD-STOP", slug)

    def _changelog(self):
        p = self.tmp / "CHANGELOG.md"
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def _releases(self):
        p = self.tmp / "RELEASES.md"
        return p.read_text(encoding="utf-8") if p.exists() else ""


class ReleaseFloorTest(_Harness):
    def test_floor_refuses_open_delta_release(self):           # Reject 1 + Must (floor)
        self._loose_done("loose1")                              # something to bundle
        self._set_spec("d", "rate-limit the retries")           # 1 open SPEC delta
        cl_before, rel_before = self._changelog(), self._releases()
        code, out = self._run("release", "0.1.0")               # no --force
        self.assertNotEqual(code, 0)
        self.assertIn("release_open_spec_deltas", out)
        self.assertIn("1", out, "the reject names the count")
        self.assertEqual(self._changelog(), cl_before, "CHANGELOG byte-unchanged on reject")
        self.assertEqual(self._releases(), rel_before, "RELEASES byte-unchanged on reject")

    def test_force_cuts_past_floor(self):                       # After (--force, loud)
        self._loose_done("loose1")
        self._set_spec("d", "rate-limit the retries")
        code, out = self._run("release", "0.1.0", "--force")
        self.assertEqual(code, 0, f"--force should record: {out}")
        self.assertIn("loose1", self._releases(), "the cut row is written under --force")

    def test_security_still_unforceable_with_deltas_clear(self):  # Reject (security wins)
        self._loose_done("loose1")
        self._hardstop("sec")                                  # open HARD-STOP, 0 open deltas
        code, out = self._run("release", "0.1.0", "--force")
        self.assertNotEqual(code, 0)
        self.assertIn("release_security_open", out, "security is never bypassable, deltas or not")

    def test_release_data_counts_open(self):                   # Must (one source, pure)
        self._set_spec("d", "alpha", "beta")
        root = add.find_root()
        d = add.release_data(root, add.load_state(root))
        self.assertEqual(d["open_spec_deltas"]["count"], 2)
        self.assertEqual(len(d["open_spec_deltas"]["items"]), 2)


class CarryReopenTest(_Harness):
    def test_carry_defers_without_loss(self):                  # Must (carry) + retrieval
        self._set_spec("t", "fold the run/streams overlap")
        code, out = self._run("carry-delta", "t", "--reason", "post-1.13 backlog")
        self.assertEqual(code, 0, f"carry failed: {out}")
        body = self._task_md("t").read_text(encoding="utf-8")
        self.assertIn("[SPEC · carried] fold the run/streams overlap", body)
        self.assertIn("[carried: post-1.13 backlog]", body)
        self.assertIn("(evidence: ev)", body, "the evidence tail is byte-preserved")
        # cleared from the open view, retrievable in the carried view
        _, open_out = self._run("deltas")
        self.assertNotIn("fold the run/streams overlap", open_out)
        _, carried_out = self._run("deltas", "--carried")
        self.assertIn("fold the run/streams overlap", carried_out)

    def test_carry_requires_reason(self):                      # Reject (carry_reason_required)
        self._set_spec("t", "some idea")
        before = self._task_md("t").read_bytes()
        code, out = self._run("carry-delta", "t")
        self.assertNotEqual(code, 0)
        self.assertIn("carry_reason_required", out)
        self.assertEqual(self._task_md("t").read_bytes(), before, "no write on reject")

    def test_carry_no_open_refuses(self):                      # Reject (no_open_spec_delta)
        self._mk("t")                                          # fresh task, no open delta
        before = self._task_md("t").read_bytes()
        code, out = self._run("carry-delta", "t", "--reason", "x")
        self.assertNotEqual(code, 0)
        self.assertIn("no_open_spec_delta", out)
        self.assertEqual(self._task_md("t").read_bytes(), before)

    def test_carry_match_ambiguous(self):                      # Reject (ambiguous_spec_delta)
        self._set_spec("t", "tune the cache", "tune the queue")
        code, out = self._run("carry-delta", "t", "--match", "tune", "--reason", "later")
        self.assertNotEqual(code, 0)
        self.assertIn("ambiguous_spec_delta", out)

    def test_carry_all_carries_every_open(self):               # Must (--all)
        self._set_spec("t", "first", "second")
        code, out = self._run("carry-delta", "t", "--all", "--reason", "batch")
        self.assertEqual(code, 0, f"--all failed: {out}")
        body = self._task_md("t").read_text(encoding="utf-8")
        self.assertNotIn("[SPEC · open]", body, "every open delta is carried")
        self.assertEqual(body.count("[SPEC · carried]"), 2)

    def test_reopen_reactivates(self):                         # Must (reopen) + Reject
        self._set_spec("t", "defer me")
        self._silent("carry-delta", "t", "--reason", "later")
        code, out = self._run("reopen-delta", "t")
        self.assertEqual(code, 0, f"reopen failed: {out}")
        body = self._task_md("t").read_text(encoding="utf-8")
        self.assertIn("[SPEC · open] defer me", body)
        self.assertNotIn("[SPEC · carried] defer me", body)
        # reopen with nothing carried refuses
        code2, out2 = self._run("reopen-delta", "t")
        self.assertNotEqual(code2, 0)
        self.assertIn("no_carried_spec_delta", out2)


class StatusStalenessTest(_Harness):
    def test_status_shows_staleness_only_when_open(self):      # Must (status line, v2 contract)
        # 0 open deltas -> the spec/staleness cue is ABSENT (byte-identical to today)
        _, clean = self._run("status")
        self.assertNotRegex(clean, r"spec\s*:\s*\d+ open", "no spec-delta cue when 0 open")
        self.assertNotIn("stale", clean.lower())
        # N>0 -> the SHIPPED `spec :` cue (the prefix spec-delta-guards pins) REFRAMED to name
        # staleness + the drain surface. Pin the prefix AND the staleness AND the drain pointer,
        # so a `stale :`-prefixed or pointer-less impl would FAIL here (closes the v1 under-spec).
        self._set_spec("d", "one", "two")
        _, stale = self._run("status")
        self.assertRegex(
            stale,
            r"spec\s*:\s*2 open SPEC delta(?:s)? — stale; drain via add\.py deltas",
            "status must keep the `spec :` prefix AND name staleness AND point at the drain surface")


if __name__ == "__main__":
    unittest.main()
