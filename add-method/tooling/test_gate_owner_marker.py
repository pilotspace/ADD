#!/usr/bin/env python3
"""Red/green tests for the driver marker on the footer + the guide (task gate-owner-marker).

CONTRACT (frozen @ v1, next-step-seams 2/3):
  Every engine footer AND the `guide` TEXT next-step line end with exactly ONE driver marker
  filling the slot next-footer-engine reserved — ` [you drive]` (the AI proceeds) or
  ` [human gate]` (a human owns it). One resolver:

      _driver_stop(root, state, slug, phase) -> bool
          phase == "verify"  -> _effective_autonomy(root, state, slug) != "auto"   # the ONE dial seam
          else               -> _phase_owner(phase) != "ai"                        # structural, dial-blind
      _driver_marker(stop) -> " [human gate]" if stop else " [you drive]"

  The phase × autonomy table (only the verify row moves with the dial):
      ground/tests/build/observe -> [you drive] (always)
      specify/scenarios/contract/done -> [human gate] (always; contract freeze stays human, run.md:21)
      verify -> [you drive] under auto, [human gate] under conservative/manual   <- exit criterion

  Option F: the FROZEN machine-state-json JSON (`owner`/`stop`) is NOT touched — the marker rides
  the footer + guide TEXT only. Fail-soft (no milestone / error) keeps NO marker.

Render-blind: every assertion reads the printed footer/guide line or the public resolver, never a
private state key. Run: python3 -m unittest test_gate_owner_marker -v
"""
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent           # add-method/tooling


# the table the frozen §3 contract encodes — only verify moves with the dial
_TABLE = {
    "auto": {
        "ground": " [you drive]", "specify": " [human gate]", "scenarios": " [human gate]",
        "contract": " [human gate]", "tests": " [you drive]", "build": " [you drive]",
        "verify": " [you drive]", "observe": " [you drive]", "done": " [human gate]",
    },
    "conservative": {
        "ground": " [you drive]", "specify": " [human gate]", "scenarios": " [human gate]",
        "contract": " [human gate]", "tests": " [you drive]", "build": " [you drive]",
        "verify": " [human gate]", "observe": " [you drive]", "done": " [human gate]",
    },
}


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (the next-footer-engine idiom)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-driver-marker-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")               # plain init -> grandfathered-locked
        self._silent("new-milestone", "v1", "--title", "T", "--goal", "g")

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- CLI helpers ------------------------------------------------------
    def _silent(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(list(argv))
        return buf.getvalue(), err.getvalue()

    def _run(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _root(self) -> Path:
        return self.tmp / ".add"

    def _task_md(self, slug: str) -> Path:
        return self._root() / "tasks" / slug / "TASK.md"

    def _state(self) -> dict:
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    def _set_state(self, st: dict):
        (self._root() / "state.json").write_text(json.dumps(st), encoding="utf-8")

    # ---- footer parsing (render-blind) ------------------------------------
    @staticmethod
    def _next_lines(out: str) -> list[str]:
        return [ln.strip() for ln in out.splitlines() if ln.strip().startswith("next:")]

    def _footer(self, out: str) -> str:
        lines = self._next_lines(out)
        self.assertTrue(lines, f"expected a `next:` footer line, got:\n{out}")
        return lines[-1]

    # ---- autonomy arrangement ---------------------------------------------
    def _task(self, slug="t", autonomy="auto"):
        """A real seeded task (keeps its TASK.md header), with the autonomy rung set."""
        self._silent("new-task", slug, "--title", slug)
        self._set_autonomy(slug, autonomy)

    def _set_autonomy(self, slug, level):
        p = self._task_md(slug)
        txt = p.read_text(encoding="utf-8")
        new = re.sub(r"(?m)^autonomy:.*$", f"autonomy: {level}", txt, count=1)
        if new == txt and not re.search(r"(?m)^autonomy:", txt):
            new = re.sub(r"(?m)^(slug:.*)$", r"\1\nautonomy: " + level, txt, count=1)
        p.write_text(new, encoding="utf-8")

    def _strip_autonomy(self, slug):
        p = self._task_md(slug)
        p.write_text(re.sub(r"(?m)^autonomy:.*\n", "", p.read_text(encoding="utf-8")),
                     encoding="utf-8")

    def _set_project_autonomy(self, level):
        p = self._root() / "PROJECT.md"
        txt = re.sub(r"(?m)^autonomy:.*\n", "", p.read_text(encoding="utf-8"))
        p.write_text(f"# project\nautonomy: {level}\n\n{txt}", encoding="utf-8")

    # ---- Arm B arrangement (a frozen §3 + red test so tests->build snapshots) ----
    @staticmethod
    def _section(n, name, *body):
        return [f"## {n} · {name}", *body, ""]

    def _write_task(self, slug):
        lines = [
            f"# TASK: {slug}", f"slug: {slug} · created: 2026-06-12 · stage: mvp",
            "phase: ground", "",
            *self._section(0, "GROUND", "Anchors the contract cites: cmd_gate"),
            *self._section(1, "SPECIFY", "Feature: f"),
            *self._section(2, "SCENARIOS", "(none)"),
            *self._section(3, "CONTRACT", "```", "shape: x { a }", "```",
                           "Status: FROZEN @ v1 — approved by Tester 2026-06-12.",
                           "Least-sure flag surfaced at freeze: [contract] none material."),
            *self._section(4, "TESTS", "Coverage target: behavior", "Tests live in: `./tests/`"),
            *self._section(5, "BUILD", "Strategy (ordered batches): 1. build",
                           "Safety rule (feature-specific): none", "Code lives in: `./src/`"),
            *self._section(6, "VERIFY", "checks"),
            *self._section(7, "OBSERVE", "watch"),
        ]
        self._task_md(slug).write_text("\n".join(lines), encoding="utf-8")

    def _write_test_file(self, slug):
        d = self._root() / "tasks" / slug / "tests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_demo.py").write_text("def test_one():\n    assert 2 + 2 == 4\n", encoding="utf-8")

    def _arm(self, slug):
        """Create the task and CROSS tests->build so a later gate completes cleanly."""
        self._silent("new-task", slug, "--title", slug)
        self._write_task(slug)
        self._write_test_file(slug)
        self._silent("phase", "tests", slug)
        self._silent("advance", slug)            # tests -> build

    def _gate(self, slug, outcome="PASS"):
        self._silent("advance", slug)            # build -> verify
        return self._run("gate", outcome, slug)


# ── Arm A: the in-flight task names its driver, from autonomy × phase ────────
class DriverMarkerArmATest(_Board):

    def test_verify_auto_names_ai(self):
        self._task("t", "auto")
        out, _, code = self._run("phase", "verify", "t")
        self.assertEqual(code, 0)
        self.assertTrue(self._footer(out).endswith(" [you drive]"), self._footer(out))

    def test_verify_conservative_names_human(self):
        self._task("t", "conservative")
        out, _, _ = self._run("phase", "verify", "t")
        self.assertTrue(self._footer(out).endswith(" [human gate]"), self._footer(out))

    def test_verify_manual_names_human(self):
        self._task("t", "manual")
        out, _, _ = self._run("phase", "verify", "t")
        self.assertTrue(self._footer(out).endswith(" [human gate]"), self._footer(out))

    def test_contract_freeze_stays_human_under_auto(self):
        self._task("t", "auto")
        out, _, _ = self._run("phase", "contract", "t")
        self.assertTrue(self._footer(out).endswith(" [human gate]"),
                        f"the freeze is dial-blind human, got: {self._footer(out)!r}")

    def test_ai_owned_phase_names_ai(self):
        self._task("t", "conservative")          # even lowered, an ai-owned phase is the AI's
        out, _, _ = self._run("phase", "build", "t")
        self.assertTrue(self._footer(out).endswith(" [you drive]"), self._footer(out))

    def test_unset_autonomy_falls_back_to_project_default(self):
        self._set_project_autonomy("conservative")
        self._task("t", "auto")
        self._strip_autonomy("t")                # no task rung -> fall back to project conservative
        out, _, _ = self._run("phase", "verify", "t")
        self.assertTrue(self._footer(out).endswith(" [human gate]"), self._footer(out))


# ── the guide names the driver too (TEXT only — JSON stays frozen, Option F) ──
class DriverMarkerGuideTest(_Board):

    def test_guide_text_names_driver(self):
        self._task("t", "conservative")
        self._silent("phase", "verify", "t")
        before = (self._root() / "state.json").read_bytes()
        out, _, code = self._run("guide", "t")
        self.assertEqual(code, 0)
        self.assertIn(" [human gate]", out)
        self.assertEqual((self._root() / "state.json").read_bytes(), before, "guide writes nothing")

    def test_guide_json_stop_untouched(self):
        self._task("t", "auto")
        self._silent("phase", "verify", "t")
        out, _, _ = self._run("guide", "--json")
        d = json.loads(out)
        self.assertTrue(d["stop"], "the frozen machine-state-json `stop` (owner != ai) is unchanged")
        tout, _, _ = self._run("guide", "t")    # the autonomy-aware driver lives on the TEXT line
        self.assertIn(" [you drive]", tout)


# ── the public resolver matches the frozen table exactly ─────────────────────
class DriverTableTest(_Board):

    def test_driver_table_matches_contract(self):
        root = add.find_root()
        for level, row in _TABLE.items():
            slug = f"t_{level}"                   # a distinct task per rung — no phase-jump coupling
            self._task(slug, level)
            st = self._state()
            for phase, want in row.items():       # _driver_stop reads the passed phase, not the task's
                got = add._driver_marker(add._driver_stop(root, st, slug, phase))
                self.assertEqual(got, want, f"{level}/{phase}: want {want!r} got {got!r}")


# ── Arm B: the milestone rollup names the driver ─────────────────────────────
class DriverMarkerArmBTest(_Board):

    def test_arm_b_decompose_names_human(self):
        out, _, _ = self._run("new-milestone", "bar", "--title", "B", "--goal", "g")
        f = self._footer(out)
        self.assertIn("decompose into tasks", f)
        self.assertTrue(f.endswith(" [human gate]"), f)

    def test_arm_b_hardstop_names_human(self):
        self._arm("alpha")
        out, _, _ = self._gate("alpha", "HARD-STOP")
        f = self._footer(out)
        self.assertIn("resolve HARD-STOP on alpha", f)
        self.assertTrue(f.endswith(" [human gate]"), f)

    def test_arm_b_run_in_progress_names_ai(self):
        self._arm("alpha")
        self._arm("beta")                        # beta left mid-run (at build)
        self._silent("use", "alpha")
        self._gate("alpha", "PASS")              # alpha done; active=alpha (phase done -> Arm B)
        out, _, _ = self._run("use", "alpha")
        f = self._footer(out)
        self.assertIn("run in progress", f)
        self.assertTrue(f.endswith(" [you drive]"), f)


# ── fail-soft + the unmapped-phase reject: the marker invents no default ─────
class DriverMarkerEdgeTest(_Board):

    def test_fail_soft_no_marker(self):
        self._arm("alpha")
        self._gate("alpha", "PASS")
        st = self._state()
        st["active_milestone"] = None            # the report path would _die on this
        st["tasks"]["alpha"]["milestone"] = None # milestone-less -> milestone-aware use stays scalar-only (no re-activation)
        self._set_state(st)
        out, _, code = self._run("use", "alpha")
        self.assertEqual(code, 0, "a footer never crashes a saved mutation")
        self.assertEqual(self._footer(out), "next: add.py status — re-orient")
        self.assertNotIn("[you drive]", out)
        self.assertNotIn("[human gate]", out)

    def test_unmapped_phase_invents_no_default(self):
        self._arm("alpha")
        st = self._state()
        st["tasks"]["alpha"]["phase"] = "bogus"  # not in PHASE_OWNER
        self._set_state(st)
        out, _, code = self._run("guide", "alpha")
        self.assertNotEqual(code, 0, "an unmapped phase is rejected, not defaulted")
        self.assertNotIn("[you drive]", out)
        self.assertNotIn("[human gate]", out)


# ── the engine-pin idiom: this task's deliberate re-aim is self-tested ───────
# Part of the pin idiom, not optional — every marker task that re-aims the engine
# pins its own `re-aimed @ <slug>` annotation (the sibling next-footer-engine
# suite carries the same guard for its slug). The §3 contract re-aimed the engine,
# so engine_pin.py MUST name this task; the supersession chain keeps the prior
# task's marker present so the lineage is never silently dropped.
class EnginePinTest(unittest.TestCase):

    def test_pin_annotation_names_this_task(self):
        src = (HERE / "engine_pin.py").read_text(encoding="utf-8")
        self.assertIn("re-aimed @ gate-owner-marker", src,
                      "the engine pin must record THIS task's deliberate re-aim")
        self.assertIn("re-aimed @ next-footer-engine", src,
                      "the pin carries the prior task's re-aim (the supersession chain)")


if __name__ == "__main__":
    unittest.main()
