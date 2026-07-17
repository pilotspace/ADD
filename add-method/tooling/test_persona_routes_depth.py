#!/usr/bin/env python3
"""persona-routes-depth red suite (thin-engine-loop W5).

The fitting persona proposes the ceremony lane in the TASK header —
`route: <full|fast|oneshot> · routed-by: <persona:<slug> | human> — <why>` —
the freeze (direction→build cross) ratifies it by recording
state.tasks[slug].route = {lane, by}; a missing/malformed line records
lane "unrouted" and NEVER refuses (measure-not-block). `add.py audit` gains
route_unrecorded + route_lane_mismatch, grandfathered by key absence.
SKILL.md's flag mode teaches propose-then-ratify, ≤9500 B, ×3 trees.

Red-for-the-right-reason today: the freeze writes no route key, the audit
codes don't exist, SKILL.md still calls the flags human-owned. Floor pins
(green today AND after): an unrouted freeze still crosses; old records are
never retro-redded; no route refusal exists at the freeze.

Run: python3 -m unittest test_persona_routes_depth -v
"""
import hashlib
import re
import unittest
from pathlib import Path

import add
from test_freeze_command import _Harness, _DRAFT_FLAGGED

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

SKILL_TREES = (
    HERE.parent / "skill" / "add" / "SKILL.md",
    REPO / ".claude" / "skills" / "add" / "SKILL.md",
    HERE.parent / "src" / "add_method" / "_bundled" / "skill" / "add" / "SKILL.md",
)

ROUTE_LINE = "route: full · routed-by: persona:methodology-engine-dev — engine change"


class _RouteHarness(_Harness):
    def _add_route_line(self, slug, line):
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        text = re.sub(r"(?m)^(phase:[^\n]*)$",
                      lambda m: m.group(1) + "\n" + line, text, count=1)
        p.write_text(text, encoding="utf-8")

    def _freeze_cross(self, slug="t"):
        self._silent("freeze", slug, "--by", "Ada", "--cross")

    def _route_rec(self, slug="t"):
        return self._state()["tasks"][slug].get("route")


class FreezeRecordsRouteTest(_RouteHarness):
    def test_routed_freeze_records_lane(self):
        self._new_task_at_plan("t")
        self._add_route_line("t", ROUTE_LINE)
        self._freeze_cross("t")
        rec = self._route_rec("t")
        self.assertIsNotNone(rec, "the freeze must record the route in state.json")
        self.assertEqual(rec.get("lane"), "full")
        self.assertIn("persona:methodology-engine-dev", rec.get("by") or "")
        # the ratify is a side record — the existing stamps behave exactly as before
        self.assertTrue(self._state()["tasks"]["t"].get("flag_verified"))

    def test_recross_rerecords_route(self):
        self._new_task_at_plan("t")
        self._add_route_line("t", "route: fast · routed-by: human — tiny sweep")
        self._freeze_cross("t")
        p = self._task_md("t")
        p.write_text(p.read_text(encoding="utf-8").replace(
            "route: fast · routed-by: human — tiny sweep",
            "route: full · routed-by: human — grew mid-flight"), encoding="utf-8")
        self._silent("re-cross", "t", "--by", "Ada")
        rec = self._route_rec("t")
        self.assertEqual((rec or {}).get("lane"), "full",
                         "a re-cross must re-record the ratified route")

    def test_unrouted_freeze_crosses(self):
        # FLOOR half: the cross itself must succeed with no route line (measure-not-block)
        self._new_task_at_plan("t")
        self._freeze_cross("t")
        self.assertEqual(self._state()["tasks"]["t"].get("phase"), "build",
                         "an unrouted freeze must still cross (measure-not-block floor)")
        rec = self._route_rec("t")
        self.assertEqual((rec or {}).get("lane"), "unrouted",
                         "an absent route line records lane 'unrouted'")

    def test_unknown_lane_records_unrouted(self):
        self._new_task_at_plan("t")
        self._add_route_line("t", "route: turbo · routed-by: human — hunch")
        self._freeze_cross("t")
        rec = self._route_rec("t")
        self.assertEqual((rec or {}).get("lane"), "unrouted",
                         "an unknown lane token records 'unrouted', never a refusal")
class DoctrineTest(unittest.TestCase):
    def test_skill_doctrine_propose_ratify(self):
        text = SKILL_TREES[0].read_text(encoding="utf-8")
        self.assertIn("route:", text, "SKILL.md must name the route header line")
        self.assertIn("routed-by", text, "SKILL.md must name the routed-by attribution")
        self.assertRegex(text, r"(?i)propos", "flag mode must teach the persona PROPOSES the route")
        self.assertRegex(text, r"(?i)ratif", "flag mode must teach the human/freeze RATIFIES it")


    def test_no_new_freeze_refusal(self):
        # FLOOR: measure-not-block — the freeze path must never gain a route refusal
        src = (HERE / "add.py").read_text(encoding="utf-8")
        self.assertNotRegex(src, r'_die\("route',
                            "no route_* refusal may exist — audit measures, the freeze never blocks")


if __name__ == "__main__":
    unittest.main(verbosity=2)
