#!/usr/bin/env python3
"""Red/green for the expectations-first flow (plan-phase-core · milestone expectations-first).

Pins the collapsed `plan` phase: ground+contract fold into ONE `plan` phase (the change
plan = grounding + frozen contract + build-strategy), the order becomes
specify -> plan -> tests -> build -> verify -> observe, the single human
freeze moves to `plan`, the §3 PLAN template carries the sub-blocks, the grounding floor
reads §3, and legacy `ground`/`contract` states still load. The cross-component contract
system is UNTOUCHED.

Behavior pinned, not prose phrasing. Run: python3 -m unittest test_plan_phase_flow -v
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
import engine_pin
from add_engine import constants as C

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

ADD_PY_COPIES = [
    _ADD_METHOD / "tooling" / "add.py",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    _REPO / ".add" / "tooling" / "add.py",
]
TMPL_COPIES = [
    _ADD_METHOD / "tooling" / "templates" / "TASK.md.tmpl",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.md.tmpl",
    _REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class ConstantsShape(unittest.TestCase):
    """M1, M2 — the phase tuple + bundles name `direction`, never the pre-collapse
    sub-phase names (phase-collapse-3: specify/plan/tests/ground/contract/scenarios/
    observe all folded away)."""

    def test_phases_expectations_first(self):  # M1
        self.assertEqual(
            C.PHASES,
            ("direction", "build", "verify", "done"),
        )
        for retired in ("ground", "contract", "specify", "plan", "scenarios", "tests", "observe"):
            self.assertNotIn(retired, C.PHASES)

    def test_direction_bundle_names_direction(self):  # M2
        self.assertEqual(C.PHASE_GROUPS["DIRECTION"], ("direction",))
        for name, d in (("PHASE_OWNER", C.PHASE_OWNER),
                        ("PHASE_AGENT", C.PHASE_AGENT),
                        ("PHASE_GUIDE", C.PHASE_GUIDE)):
            self.assertIn("direction", d, f"{name} must carry a `direction` key")
            for retired in ("ground", "contract", "specify", "plan", "scenarios", "tests"):
                self.assertNotIn(retired, d, f"{name} must drop `{retired}`")

    def test_direction_is_the_freeze_seam_owner(self):  # M4
        self.assertEqual(C.PHASE_OWNER["direction"], "seam")

    def test_front_phases_names_direction(self):  # M9
        self.assertIn("direction", add._FRONT_PHASES)
        self.assertNotIn("contract", add._FRONT_PHASES)
        self.assertEqual(len(add._FRONT_PHASES), 1,
                         "the whole front collapsed into ONE phase")


class GroundingFloorReadsPlan(unittest.TestCase):
    """M6 — the grounding measure reads the §3 PLAN grounding sub-block, not §0."""

    def test_grounded_state_true_from_section3(self):
        raw = {3: ("### Grounding\nAnchors the contract cites: `PHASES` · `_FRONT_PHASES`\n"
                   "### Contract\n```\nSHAPE\n```\n### Build-strategy\nx\n")}
        self.assertTrue(add._grounded_state(raw))

    def test_grounded_state_false_on_placeholder(self):
        raw = {3: "### Grounding\nAnchors the contract cites: <the symbols §3 names>\n### Contract\n"}
        self.assertFalse(add._grounded_state(raw))

    def test_grounded_state_none_without_plan(self):
        self.assertIsNone(add._grounded_state({1: "no plan section here"}))


class ContractHardStrategySoft(unittest.TestCase):
    """M7 — the tamper fingerprint keys on the FIRST fenced block in §3 (the contract);
    grounding/build-strategy prose around it is not frozen."""

    _S3 = ("### Grounding\nAnchors the contract cites: `PHASES`\n"
           "### Contract\n```\nCONTRACT SHAPE v1\n```\n"
           "### Build-strategy\nStrategy: do the thing\n")

    def test_prose_change_does_not_tamper(self):
        h = add._contract_body_hash(self._S3)
        prose = self._S3.replace("do the thing", "do the thing DIFFERENTLY")
        self.assertEqual(add._contract_body_hash(prose), h)

    def test_fenced_contract_change_tampers(self):
        h = add._contract_body_hash(self._S3)
        shape = self._S3.replace("CONTRACT SHAPE v1", "CONTRACT SHAPE v2")
        self.assertNotEqual(add._contract_body_hash(shape), h)


class _CLI(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-planflow-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._run("init", "--name", "demo")
        self._run("new-milestone", "v1", "--title", "T", "--goal", "g")
        self._run("milestone-confirm", "v1")
        self._run("new-task", "t", "--title", "Feature")

    def _run(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit:
            pass
        return buf.getvalue() + err.getvalue()

    def _root(self):
        return self.tmp / ".add"

    def _state(self):
        return json.loads((self._root() / "state.json").read_text())

    def _task_md(self):
        return (self._root() / "tasks" / "t" / "TASK.md")

    # M3 — a fresh task opens at direction
    def test_new_task_seeds_direction(self):
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "direction")
        marker = [l for l in self._task_md().read_text().splitlines() if l.startswith("phase:")][0]
        # assert the phase VALUE (left of the descriptive comment), not the whole line —
        # the comment legitimately says "grounding", so a bare substring check is wrong.
        self.assertEqual(marker.split("<!--", 1)[0].strip(), "phase: direction")

    # M5 — the rendered template carries the §3 PLAN sub-blocks; no §0 GROUND
    def test_template_renders_plan_subblocks(self):
        md = self._task_md().read_text()
        self.assertNotIn("## 0 · GROUND", md)
        self.assertIn("## 3 · PLAN", md)
        for sub in ("### Grounding", "### Contract", "### Build-strategy"):
            self.assertIn(sub, md, f"§3 PLAN must contain {sub}")

    # M9 — an unfrozen `plan` is the PLAN approval seam
    def test_plan_phase_is_approval_seam(self):
        st = self._state()
        st["tasks"]["t"]["phase"] = "plan"
        (self._root() / "state.json").write_text(json.dumps(st))
        state = add.load_state(self._root())
        d = add.decide_data(self._root(), state, "v1", "t")
        self.assertEqual(d["seam"], "front")
        txt = add.render_decide(self._root(), state, "v1", "t")
        self.assertIn("PLAN", txt)
        self.assertNotIn("CONTRACT APPROVAL", txt)
        self.assertNotIn("GROUND", txt)

    # M10, R2 — legacy ground/contract phase records still load + migrate, idempotently
    # (phase-collapse-3: BOTH legacy tokens now map to the SAME collapsed home, "direction" —
    # there is no longer a "ground"->specify vs "contract"->plan distinction to preserve.)
    def test_legacy_ground_contract_states_load(self):
        st = self._state()
        st["tasks"]["t"]["phase"] = "ground"
        st["tasks"].setdefault("u", dict(st["tasks"]["t"]))
        st["tasks"]["u"]["phase"] = "contract"
        (self._root() / "state.json").write_text(json.dumps(st))
        # load must not crash and must migrate the two legacy tokens
        state = add.load_state(self._root())
        self.assertEqual(state["tasks"]["t"]["phase"], "direction")
        self.assertEqual(state["tasks"]["u"]["phase"], "direction")
        # idempotent: a second load changes nothing further
        again = add.load_state(self._root())
        self.assertEqual(again["tasks"]["t"]["phase"], "direction")
        self.assertEqual(again["tasks"]["u"]["phase"], "direction")

    # M4, R3 — crossing direction->build needs a frozen §3 (phase-collapse-3: there is no
    # longer a separate "plan" phase to advance into first — a fresh task is already at
    # direction, and `advance` itself now attempts the direction->build crossing).
    def test_direction_to_build_needs_frozen(self):
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "direction")
        p = self._task_md()
        md = p.read_text()
        # replace the §3 contract fence placeholder with a real drafted shape
        md = md.replace("<METHOD> <path>", "GET /x").replace(
            "Status: DRAFT",
            "Status: DRAFT\nLeast-sure flag surfaced at freeze: [contract] fixture — cost: none")
        p.write_text(md)
        # DRAFT: crossing into build without --skip-freeze is refused
        out = self._run("advance")
        self.assertIn("contract_not_frozen", out)
        self.assertEqual(self._state()["tasks"]["t"]["phase"], "direction")


if __name__ == "__main__":
    unittest.main(verbosity=2)
