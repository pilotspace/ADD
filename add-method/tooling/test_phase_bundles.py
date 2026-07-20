#!/usr/bin/env python3
"""Red/green suite for phase-bundles (task: phase-bundles, milestone: three-phase-flow).

CONTRACT (frozen, as briefed at BUILD; re-pointed for phase-collapse-3 — the whole front
span (specify+scenarios+plan+tests) collapsed into ONE `direction` phase, PHASES now has
3 work phases + terminal "done"): the 3 work phases (PHASES minus "done") group into 3
agent-owned bundles surfaced at `status`/`guide`:

  PHASE_GROUPS = {
      "DIRECTION": ("direction",),
      "BUILD":     ("build",),
      "VERIFY":    ("verify",),
  }
  PHASE_AGENT (per-PHASE, 3 keys) = {
      "direction": "add-design",
      "build": "add-build",
      "verify": "add-verify",
  }

`_phase_bundle(phase)` resolves a phase to its bundle name; None for the terminal
"done" phase (documented, non-crashing); `_die("unmapped_phase_bundle")` for any other
unmapped token (fail-closed, mirrors `_phase_owner`).

`status`/`guide` (plain + --json) grow ONE additive, present-only `bundle` line/field —
silent/null at "done" or with no active task; every existing key/line is untouched.

One test per §2 scenario. Run: python3 -m unittest test_phase_bundles -v
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import add
from add_engine import constants as engine_constants
from add_engine import predicates as engine_predicates
from add_engine.constants import PHASES

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parent
REPO_ROOT = PKG_ROOT.parent

TREES = (
    HERE,
    REPO_ROOT / ".add" / "tooling",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling",
)


def _run(argv):
    """Run add.main(argv) in-process, capturing (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class PhaseGroupsConstantTest(unittest.TestCase):
    """M1 — PHASE_GROUPS is a complete, disjoint 3-way partition of the 8 work phases."""

    def test_exact_keys(self):
        self.assertEqual(set(engine_constants.PHASE_GROUPS.keys()),
                         {"DIRECTION", "BUILD", "VERIFY"})

    def test_tuples_match_frozen_shape(self):
        # phase-collapse-3: the whole front span collapsed into ONE `direction` phase;
        # DIRECTION now names just (direction,), 1 phase (was 3).
        self.assertEqual(engine_constants.PHASE_GROUPS["DIRECTION"],
                         ("direction",))
        self.assertEqual(engine_constants.PHASE_GROUPS["BUILD"], ("build",))
        self.assertEqual(engine_constants.PHASE_GROUPS["VERIFY"], ("verify",))

    def test_union_and_pairwise_disjoint(self):
        groups = engine_constants.PHASE_GROUPS
        union = set().union(*groups.values())
        self.assertEqual(union, set(PHASES) - {"done"})
        vals = list(groups.values())
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                self.assertEqual(set(vals[i]) & set(vals[j]), set(),
                                 f"{list(groups.keys())[i]} and {list(groups.keys())[j]} overlap")

    def test_importable_via_star_import(self):
        self.assertIn("PHASE_GROUPS", engine_constants.__all__)
        self.assertTrue(hasattr(add, "PHASE_GROUPS"),
                        "add.py must re-export PHASE_GROUPS via `from add_engine.constants import *`")
        self.assertEqual(add.PHASE_GROUPS, engine_constants.PHASE_GROUPS)


class PhaseAgentConstantTest(unittest.TestCase):
    """M2 — PHASE_AGENT names the preferred roster agent per PHASE (8 keys)."""

    def test_keys_cover_every_non_done_phase(self):
        self.assertEqual(set(engine_constants.PHASE_AGENT.keys()), set(PHASES) - {"done"})

    def test_values_match_shipped_roster_ownership(self):
        # roster-distill (ADD 2.0 M1): ONE `add` agent serves every phase — the spawn
        # names the mode, the agent loads the beat's guide + persona.
        pa = engine_constants.PHASE_AGENT
        self.assertEqual(pa["direction"], "add")
        self.assertEqual(pa["build"], "add")
        self.assertEqual(pa["verify"], "add")

    def test_values_are_roster_slugs_only(self):
        self.assertTrue(set(engine_constants.PHASE_AGENT.values()) <= {"add"})

    def test_importable_via_star_import(self):
        self.assertIn("PHASE_AGENT", engine_constants.__all__)
        self.assertTrue(hasattr(add, "PHASE_AGENT"),
                        "add.py must re-export PHASE_AGENT via `from add_engine.constants import *`")
        self.assertEqual(add.PHASE_AGENT, engine_constants.PHASE_AGENT)


class PhaseBundleResolverTest(unittest.TestCase):
    """M3 — _phase_bundle: normal resolve / terminal None / fail-closed unmapped."""

    def test_resolves_direction_phases(self):
        for phase in ("direction",):
            self.assertEqual(engine_predicates._phase_bundle(phase), "DIRECTION", phase)

    def test_resolves_build_phase(self):
        self.assertEqual(engine_predicates._phase_bundle("build"), "BUILD")

    def test_resolves_verify_phases(self):
        self.assertEqual(engine_predicates._phase_bundle("verify"), "VERIFY")

    def test_done_returns_none_no_exception(self):
        self.assertIsNone(engine_predicates._phase_bundle("done"))

    def test_unmapped_phase_dies_fail_closed(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit):
                engine_predicates._phase_bundle("bogus")
        self.assertIn("unmapped_phase_bundle", err.getvalue())

    def test_exposed_on_add_module(self):
        self.assertTrue(hasattr(add, "_phase_bundle"))
        self.assertEqual(add._phase_bundle("direction"), "DIRECTION")


class CliFixture(unittest.TestCase):
    """Shared tmp-project fixture for the status/guide CLI-surface scenarios."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-phase-bundles-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        code, _, err = _run(["init", "--name", "pb", "--stage", "mvp"])
        assert code == 0, err
        code, _, err = _run(["new-task", "feat", "--title", "Feature"])
        assert code == 0, err

    def _set_phase(self, phase):
        argv = ["phase", phase, "feat"]
        if phase == "build":
            argv.append("--skip-freeze")   # test task's §3 is a stub, never frozen
        code, _, err = _run(argv)
        assert code == 0, err


class StatusPlainBundleLineTest(CliFixture):
    """M4 — status prints the active bundle + preferred agent; silent at done/no-task."""

    def test_status_prints_bundle_for_non_done_task(self):
        # roster-distill (ADD 2.0 M1): every phase prefers the ONE `add` agent.
        _, out, _ = _run(["status"])
        self.assertIn("DIRECTION", out)
        bundle_lines = [ln for ln in out.splitlines() if ln.strip().startswith("bundle")]
        self.assertEqual(len(bundle_lines), 1, out)
        self.assertIn("prefer: add agent", bundle_lines[0])

    def test_status_silent_at_done(self):
        self._set_phase("build")
        self._set_phase("verify")
        self._set_phase("done")
        _, out, _ = _run(["status"])
        self.assertFalse(any(ln.strip().startswith("bundle") for ln in out.splitlines()), out)

    def test_status_silent_with_no_active_task(self):
        # simulate "no active task" with a fresh, task-less project (simplest reliable state)
        shutil.rmtree(self.tmp)
        self.tmp = tempfile.mkdtemp(prefix="add-phase-bundles-empty-")
        os.chdir(self.tmp)
        code, _, err = _run(["init", "--name", "pb2", "--stage", "mvp"])
        assert code == 0, err
        _, out, _ = _run(["status"])
        self.assertFalse(any(ln.strip().startswith("bundle") for ln in out.splitlines()), out)


class GuidePlainBundleLineTest(CliFixture):
    """M5 — guide prints the active bundle + preferred agent; silent at done."""

    def test_guide_prints_bundle_for_non_done_task(self):
        self._set_phase("build")
        _, out, _ = _run(["guide"])
        lines = out.splitlines()
        guide_idx = next(i for i, ln in enumerate(lines) if ln.startswith("guide") or ln.startswith("next"))
        bundle_idx = next((i for i, ln in enumerate(lines) if ln.strip().startswith("bundle")), None)
        self.assertIsNotNone(bundle_idx, out)
        self.assertGreater(bundle_idx, guide_idx, out)
        self.assertIn("BUILD", lines[bundle_idx])
        self.assertIn("agent-call-preferred: add", lines[bundle_idx])

    def test_guide_silent_at_done(self):
        self._set_phase("build")
        self._set_phase("verify")
        self._set_phase("done")
        _, out, _ = _run(["guide"])
        self.assertFalse(any(ln.strip().startswith("bundle") for ln in out.splitlines()), out)
        # existing done-phase resume guidance is unchanged (still present)
        self.assertIn("active :", out)


class StatusJsonBundleFieldTest(CliFixture):
    """M6 — status --json carries an additive 'bundle' field, additive-only."""

    def test_tasks_list_bundle_field(self):
        self._set_phase("specify")
        _, out, _ = _run(["status", "--json"])
        data = json.loads(out)
        task_obj = next(t for t in data["tasks"] if t["slug"] == "feat")
        self.assertEqual(task_obj["bundle"], "DIRECTION")
        for key in ("phase", "gate", "milestone", "owner", "assignee"):
            self.assertIn(key, task_obj)

    def test_single_task_object_bundle_field(self):
        self._set_phase("specify")
        _, out, _ = _run(["status", "--json", "--task", "feat"])
        data = json.loads(out)
        self.assertEqual(data["bundle"], "DIRECTION")
        for key in ("slug", "phase", "gate", "milestone", "owner", "assignee"):
            self.assertIn(key, data)

    def test_bundle_null_at_done(self):
        self._set_phase("build")
        self._set_phase("verify")
        self._set_phase("done")
        _, out, _ = _run(["status", "--json", "--task", "feat"])
        data = json.loads(out)
        self.assertIsNone(data["bundle"])


class GuideJsonBundleFieldTest(CliFixture):
    """M6 — guide --json carries an additive 'bundle' field, null at done."""

    def test_bundle_field_non_done(self):
        self._set_phase("build")
        _, out, _ = _run(["guide", "--json"])
        data = json.loads(out)
        self.assertEqual(data["bundle"], "BUILD")
        for key in ("task", "phase", "owner", "stop", "next_step", "chapter", "gate", "guide"):
            self.assertIn(key, data)

    def test_bundle_null_at_done(self):
        self._set_phase("build")
        self._set_phase("verify")
        self._set_phase("done")
        _, out, _ = _run(["guide", "--json"])
        data = json.loads(out)
        self.assertIsNone(data["bundle"])


class SkillDocBundleColumnTest(unittest.TestCase):
    """M7 — SKILL.md phase table gains a Bundle column; roster states agent-call-preferred
    as the DEFAULT execution mode."""

    SKILL = HERE.parent / "skill" / "add" / "SKILL.md"

    def test_phase_table_has_bundle_column_populated(self):
        # skill-loop-fold: the phase table is retired — SKILL.md narrates the three
        # bundles INLINE. Same intent: every old phase is owned by a named bundle.
        text = self.SKILL.read_text(encoding="utf-8")
        for beat in ("**DIRECTION**", "**BUILD**", "**VERIFY**"):
            self.assertIn(beat, text, f"SKILL.md must narrate the {beat} bundle inline")
        direction = text.split("**DIRECTION**", 1)[1].split("**BUILD**", 1)[0]
        for span in ("§1", "§2", "§3", "§4"):
            self.assertIn(span, direction,
                          f"the DIRECTION bundle must own the {span} span of the old phases")

    def test_agent_call_preferred_documented_as_default(self):
        text = self.SKILL.read_text(encoding="utf-8")
        self.assertIn("agent-call-preferred", text)
        self.assertRegex(text, re.compile(r"default execution mode", re.IGNORECASE))


if __name__ == "__main__":
    unittest.main(verbosity=2)
