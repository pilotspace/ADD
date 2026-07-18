#!/usr/bin/env python3
"""Behavioral proof of the route scoreboard (milestone persona-gepa-loop).

M1 persona-core made `gate` append one JSON line per recorded outcome to
`.add/traces/route-outcomes.jsonl` — a write-only stream until now. This suite
pins the READ side: `add.py deltas` rolls the traces up per LANE (n gated ·
outcome mix · heals · median age) and points the PM persona at the GEPA
reflection, whose only mutation channel is `delta-append` + a human folding
ratified rules into the persona file.

Contract:
  - rollup prints under `deltas` when traces exist: one line per lane with
    gated count, PASS/HARD-STOP mix, heal total, median age;
  - silent at zero: no traces dir / empty file -> no scoreboard block;
  - degrade-safe: a malformed JSON line is skipped, never a crash (exit 0);
  - --json carries the same rollup under "routes";
  - the nudge names the GEPA loop and the delta-append channel — the engine
    never edits a persona.
Run: python3 -m unittest test_route_scoreboard -v
"""
import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import add


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


def _trace(**kw):
    base = {"ts": "2026-07-18T00:00:00+00:00", "task": "t", "milestone": "mvp",
            "kind": None, "lane": "full", "routed_by": "ai", "persona": None,
            "outcome": "PASS", "heals": 0, "recross": False, "age_hours": 1.0,
            "target_hit": None, "actor": "Tester"}
    base.update(kw)
    return json.dumps(base)


class RouteScoreboardTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-scoreboard-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.traces = self.tmp / ".add" / "traces"

    def tearDown(self):
        os.chdir(self._cwd)

    def _write_traces(self, lines):
        self.traces.mkdir(parents=True, exist_ok=True)
        (self.traces / "route-outcomes.jsonl").write_text(
            "\n".join(lines) + "\n", encoding="utf-8")

    def test_rollup_per_lane(self):
        self._write_traces([
            _trace(task="a", lane="full", outcome="PASS", heals=1, age_hours=10.0),
            _trace(task="b", lane="full", outcome="HARD-STOP", heals=2, age_hours=20.0),
            _trace(task="c", lane="fast", outcome="PASS", heals=0, age_hours=1.0),
        ])
        code, out, _ = _run(["deltas"])
        self.assertEqual(code, 0)
        self.assertIn("route scoreboard", out)
        self.assertRegex(out, r"full\s*: 2 gated", "per-lane gated count")
        self.assertRegex(out, r"fast\s*: 1 gated")
        self.assertIn("PASS 1", out, "outcome mix per lane (full: 1 PASS)")
        self.assertIn("HARD-STOP 1", out)
        self.assertIn("heals 3", out, "full lane total heals")
        self.assertIn("15.0h", out, "median age of the full lane (10, 20)")

    def test_silent_at_zero(self):
        code, out, _ = _run(["deltas"])
        self.assertEqual(code, 0)
        self.assertNotIn("route scoreboard", out,
                         "no traces -> no scoreboard block (silent at zero)")
        self.assertIn("no open deltas.", out)

    def test_malformed_line_skipped(self):
        self._write_traces([_trace(lane="full"), "{not json", _trace(task="z", lane="fast")])
        code, out, _ = _run(["deltas"])
        self.assertEqual(code, 0, "a malformed trace line must never crash the report")
        self.assertRegex(out, r"full\s*: 1 gated")
        self.assertRegex(out, r"fast\s*: 1 gated")

    def test_json_carries_routes(self):
        self._write_traces([_trace(lane="oneshot", heals=1, age_hours=2.0)])
        code, out, _ = _run(["deltas", "--json"])
        self.assertEqual(code, 0)
        obj = json.loads(out)
        self.assertIn("routes", obj)
        self.assertEqual(obj["routes"]["oneshot"]["gated"], 1)
        self.assertEqual(obj["routes"]["oneshot"]["heals"], 1)
        self.assertEqual(obj["routes"]["oneshot"]["outcomes"], {"PASS": 1})

    def test_json_routes_empty_at_zero(self):
        code, out, _ = _run(["deltas", "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out).get("routes"), {})

    def test_nudge_names_gepa_and_channel(self):
        self._write_traces([_trace()])
        _, out, _ = _run(["deltas"])
        self.assertIn("GEPA", out, "the rollup points the PM persona at the GEPA reflection")
        self.assertIn("add.py delta-append", out, "the only mutation channel is delta-append")
        self.assertIn("personas", out, "the fold target is the persona file — human-owned")

    def test_engine_never_edits_a_persona(self):
        # structural: cmd_deltas stays read-only — no write path into .add/personas/
        self._write_traces([_trace()])
        personas = self.tmp / ".add" / "personas"
        before = sorted(p.name for p in personas.rglob("*")) if personas.exists() else []
        _run(["deltas"])
        after = sorted(p.name for p in personas.rglob("*")) if personas.exists() else []
        self.assertEqual(before, after, "deltas must write NOTHING under .add/personas/")


class ProseAccordTest(unittest.TestCase):
    """loop.md documents the GEPA beat the scoreboard feeds — prose ≡ enforcement."""
    LOOP = Path(__file__).resolve().parent.parent / "skill" / "add" / "loop.md"

    def test_loop_guide_names_gepa_beat(self):
        t = self.LOOP.read_text(encoding="utf-8")
        self.assertIn("GEPA", t, "loop.md must name the GEPA reflection")
        self.assertIn("route scoreboard", t, "loop.md must point at the deltas rollup")
        self.assertIn("delta-append", t, "the only proposal channel is delta-append")
        self.assertIn(".add/personas/", t, "the fold target is the persona file")

    def test_loop_guide_states_mutation_rails(self):
        t = self.LOOP.read_text(encoding="utf-8").lower()
        self.assertIn("human folds", t, "persona mutation is human-owned")
        for guarded in ("frozen contracts", "hard-stop"):
            self.assertIn(guarded, t,
                          f"the rails must name what personas never touch: {guarded}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
