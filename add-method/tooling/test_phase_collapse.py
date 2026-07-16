#!/usr/bin/env python3
"""RED/green suite for thin-engine-loop · phase-collapse-3 (W2 — the universal collapse).

W1 gave the opt-in `--thin` lane a 3-call walk. W2 makes the 3-phase model THE state
machine: every lane's task is born at `direction` (the collapsed specify+plan+tests
span), ONE `freeze --by <name> --cross` crosses the whole front into `build` through
_build_entry's unchanged floor (tamper tripwire + scope snapshot), and `gate` keeps
its compound build→verify cross. Legacy phase values (specify · scenarios · ground ·
plan · contract · tests) normalize to `direction` at READ time — zero task-file
rewrites. Floors are pinned unchanged: contract_not_drafted · unflagged_freeze ·
no gate before the freeze.

RED against the 6-phase engine by design; two tests are green regression PINS
(gate compound cross · freeze floors) so the collapse cannot land by weakening them.

Run: python3 -m unittest test_phase_collapse -v
"""
from __future__ import annotations

import io
import json
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

# a real drafted §3 PLAN body (no template placeholders), with the well-formed flag —
# mirrors test_freeze_command's canonical draft (fenced shape first, then Status:).
_DRAFT_FLAGGED = (
    "\n### Contract\n```\nGET /widget  body: { id }\n  200 -> { ok: true }\n```\n\n"
    "Status: DRAFT\n"
    "Least-sure flag surfaced at freeze:\n"
    "  ⚠ [contract] the id encoding is the least-sure part — cost if wrong: a reparse.\n"
)
_DRAFT_NOFLAG = (
    "\n### Contract\n```\nGET /widget  body: { id }\n  200 -> { ok: true }\n```\n\nStatus: DRAFT\n"
)


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-collapse-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue() + err.getvalue(), code     # merged: _die writes to stderr

    def _state(self):
        return json.loads((self.tmp / ".add" / "state.json").read_text())

    def _task_md(self, slug):
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

    def _draft_s3(self, slug, body=_DRAFT_FLAGGED):
        """Replace the scaffolded §3 body with a real drafted contract, and satisfy the
        §1 Boundary floor (quality-floors: boundary_unfilled) where the lane carries it."""
        md = self._task_md(slug)
        text = md.read_text(encoding="utf-8")
        raw3 = add._phase_spans(text)[3]
        text = text.replace(raw3, body)
        text = re.sub(r"(?m)^Boundary:.*$",
                      'Boundary: none — single internal enum change, no external input shape',
                      text)
        md.write_text(text, encoding="utf-8")

    def _stored_phase(self, slug):
        return self._state()["tasks"][slug]["phase"]


class DirectionIsTheBirthPhase(_Harness):
    def test_default_lane_starts_at_direction(self):                       # M1
        self._silent("new-task", "t", "--title", "Feature")
        self.assertEqual(self._stored_phase("t"), "direction",
                         "every lane must be born at the direction span")
        marker = self._task_md("t").read_text(encoding="utf-8")
        self.assertRegex(marker, r"(?m)^phase:\s*direction\b",
                         "the TASK.md marker must mirror state at scaffold")

    def test_every_lane_prescribes_three_calls(self):                      # M4
        for slug, flags in (("a", []), ("b", ["--fast"]), ("c", ["--oneshot"])):
            out = self._silent("new-task", slug, "--title", "Feature", *flags)
            lane = flags[0] if flags else "default"
            self.assertNotRegex(
                out, r"(?m)^\s+add\.py\s+advance\b",
                f"{lane}: the recipe may prescribe no bookkeeping advance — "
                f"freeze --cross + gate are the only remaining calls")


class OneFreezeCrossesTheFront(_Harness):
    def _new_drafted(self, slug="t"):
        self._silent("new-task", slug, "--title", "Feature")
        self._draft_s3(slug)
        return slug

    def test_freeze_cross_universal_from_direction(self):                  # M2
        slug = self._new_drafted()
        out = self._silent("freeze", "--by", "Tin Dang", "--cross")
        self.assertRegex(
            add._phase_spans(self._task_md(slug).read_text(encoding="utf-8"))[3],
            r"Status:\s*FROZEN @ v1 — approved by Tin Dang")
        self.assertEqual(self._stored_phase(slug), "build",
                         f"one freeze --cross must land build; output was:\n{out}")

    def test_freeze_cross_arms_tamper_floor(self):                         # M2
        slug = self._new_drafted()
        self._silent("freeze", "--by", "Tin Dang", "--cross")
        self.assertIn("tripwire", self._state()["tasks"][slug],
                      "the direction→build cross must arm the tamper tripwire "
                      "(the W1 floor, now universal — never a parallel path)")


class GateKeepsTheCompoundCross(_Harness):
    def test_gate_compound_cross_regression(self):                         # M3 (green pin)
        # today's thin lane already reaches build in one cross; the pin holds it
        self._silent("new-task", "t", "--title", "Feature", "--thin")
        self._draft_s3("t")
        self._silent("freeze", "--by", "Tin Dang", "--cross")
        self.assertEqual(self._stored_phase("t"), "build")
        self._silent("gate", "PASS")
        t = self._state()["tasks"]["t"]
        self.assertEqual(t.get("gate"), "PASS",
                         "gate from build must record the outcome in the same call")


class LegacyRecordsReadAsDirection(_Harness):
    def test_legacy_phase_values_read_as_direction(self):                  # M5
        self._silent("new-task", "t", "--title", "Feature")
        # simulate a pre-collapse record: stored phase value written by the old engine
        st_path = self.tmp / ".add" / "state.json"
        st = json.loads(st_path.read_text())
        st["tasks"]["t"]["phase"] = "plan"
        st_path.write_text(json.dumps(st, indent=2))
        before = self._task_md("t").read_text(encoding="utf-8")
        out = self._silent("status")
        self.assertIn("direction", out,
                      "status must render a legacy 'plan' record at direction")
        self.assertEqual(before, self._task_md("t").read_text(encoding="utf-8"),
                         "read-side normalization must rewrite no task file")
        # and the crossing accepts the legacy record exactly like a direction one
        self._draft_s3("t")
        self._silent("freeze", "--by", "Tin Dang", "--cross")
        self.assertEqual(self._stored_phase("t"), "build")

    def test_phase_cmd_maps_legacy_name(self):                             # M6
        self._silent("new-task", "t", "--title", "Feature")
        out = self._silent("phase", "plan", "t")
        self.assertEqual(self._stored_phase("t"), "direction",
                         "a legacy phase name must map to its 3-phase home")
        self.assertIn("direction", out, "the mapping must be noted in the output")

    def test_phase_cmd_accepts_direction(self):                            # M6
        self._silent("new-task", "t", "--title", "Feature")
        self._silent("phase", "build", "t", "--skip-freeze")
        self._silent("phase", "direction", "t")
        self.assertEqual(self._stored_phase("t"), "direction")

    def test_phase_cmd_rejects_unknown(self):                              # R1
        self._silent("new-task", "t", "--title", "Feature")
        before = self._stored_phase("t")
        _, code = self._run("phase", "shipping", "t")
        self.assertNotEqual(code, 0, "an unknown phase token must be refused")
        self.assertEqual(self._stored_phase("t"), before,
                         "a refused phase call must leave state unchanged")


class TheFloorsAreUnchanged(_Harness):
    def test_freeze_floors_unchanged(self):                                # R2 · R3 (red: the flag floor is reachable from direction only post-collapse)
        self._silent("new-task", "t", "--title", "Feature")
        out, code = self._run("freeze", "--by", "Tin Dang", "--cross")     # §3 still template
        self.assertNotEqual(code, 0)
        self.assertIn("contract_not_drafted", out)
        self.assertNotEqual(self._stored_phase("t"), "build")
        self._draft_s3("t", _DRAFT_NOFLAG)                                 # drafted, no ⚠ flag
        out, code = self._run("freeze", "--by", "Tin Dang", "--cross")
        self.assertNotEqual(code, 0)
        self.assertIn("unflagged_freeze", out)
        self.assertNotEqual(self._stored_phase("t"), "build")

    def test_no_gate_before_freeze(self):                                  # R4 (green pin)
        self._silent("new-task", "t", "--title", "Feature")
        out, code = self._run("gate", "PASS")
        self.assertNotEqual(code, 0, "gate at the direction span must be refused")
        self.assertEqual(self._state()["tasks"]["t"].get("gate"), "none",
                         "a refused gate must record no outcome")


if __name__ == "__main__":
    unittest.main(verbosity=2)
