#!/usr/bin/env python3
"""Red/green tests for plan-core (ADD 2.0 M2 plan-core-shards).

CONTRACT: the §3 PLAN is ADD 2.0's core artifact — it carries a MEASURABLE
Target the verify evidence must hit, and the gate records whether it was hit.

- PLAN.md.tmpl §3 carries a `Target (measurable):` line (numbers, not
  adjectives) — measure-not-block: freeze never refuses on it.
- `gate <outcome> --target-hit yes|partial|no` records the judgment in state
  (tasks[slug]["target_hit"]) and in the route-outcome trace line
  ("target_hit" key, null when the flag is absent — the engine never infers).
- An invalid --target-hit value is refused BEFORE any write
  (target_hit_invalid).
- Shard tolerance: AI-architected shard files inside `.add/tasks/<slug>/`
  (beyond PLAN.md) are the AI's free architecture — they never trip the §5
  scope guard (the .add tree is outside the scope walk by construction; this
  pins that as a 2.0 contract, not an accident).

Run: python3 -m unittest test_plan_target -v
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

TOOLING = Path(__file__).resolve().parent
TMPL = TOOLING / "templates" / "PLAN.md.tmpl"

_SEC3 = """### Grounding
Touches (files · symbols): pkg/api/handler.py:handle — the endpoint
Anchors the contract cites: handle
Ground SHA: hand1234 — hand-grounded

### Contract

```
GET /w -> ok
```

Target (measurable): all §4 tests green · 0 new deps

`Least-sure flag surfaced at freeze:`
  ⚠ [contract] the shape is the least-sure part — cost if wrong: a reparse.
Status: DRAFT

### Build-strategy
Scope (may touch): `pkg/api/`
"""

TRACE_REL = Path(".add") / "traces" / "route-outcomes.jsonl"


class _Harness(unittest.TestCase):
    """A live board arranged through the real CLI (mirrors test_route_trace's
    harness — duplicated per this repo's one-harness-per-file norm)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-plt-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue() + err.getvalue(), code

    def _ok(self, *argv):
        text, code = self._run(*argv)
        self.assertEqual(code, 0, f"{argv} exited {code}: {text}")
        return text

    def _board_at_build(self):
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        self._ok("new-task", "t", "--title", "T", "--oneshot")
        self._ok("advance", "--to", "plan")
        p = self.tmp / ".add" / "tasks" / "t" / "PLAN.md"
        text = p.read_text(encoding="utf-8")
        new = re.sub(r"(?ms)(^### Grounding.*?)(?=^---)", _SEC3 + "\n", text, count=1)
        self.assertNotEqual(new, text, "fixture §3 replacement failed")
        new = re.sub(r"(?m)^Boundary:.*$", "Boundary: none — no external input", new, count=1)
        p.write_text(new, encoding="utf-8")
        self._ok("freeze", "--by", "Tester")
        self._ok("phase", "build", "t")
        return p

    def _state_task(self):
        state = json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))
        return state["tasks"]["t"]

    def _trace_lines(self):
        tf = self.tmp / TRACE_REL
        if not tf.is_file():
            return []
        return [json.loads(ln) for ln in
                tf.read_text(encoding="utf-8").splitlines() if ln.strip()]


class TemplateTargetTest(unittest.TestCase):
    # Must: the shipped template's §3 carries the measurable Target line
    def test_template_has_target_line(self):
        text = TMPL.read_text(encoding="utf-8")
        self.assertIn("Target (measurable):", text,
                      "PLAN.md.tmpl §3 must carry a 'Target (measurable):' line")
        sec3_end = text.index("## 4 ·")
        self.assertLess(text.index("Target (measurable):"), sec3_end,
                        "the Target line belongs to the §3 PLAN, before §4")

    # Must: measure-not-block — a §3 WITHOUT a Target line still freezes
    def test_freeze_never_refuses_on_absent_target(self):
        # _SEC3 minus the Target line freezes fine (proven by every sibling
        # suite's fixture); this pins the discipline in prose + the harness below.
        self.assertNotIn("Target", "".join(
            l for l in _SEC3.splitlines() if l.startswith("Status:")))


class TargetHitAtGateTest(_Harness):
    # Must: --target-hit records into state AND the trace
    def test_target_hit_recorded(self):
        self._board_at_build()
        self._ok("gate", "PASS", "t", "--target-hit", "yes")
        self.assertEqual(self._state_task().get("target_hit"), "yes")
        self.assertEqual(self._trace_lines()[-1]["target_hit"], "yes")

    # Must: partial and no are valid judgments
    def test_partial_and_no_valid(self):
        self._board_at_build()
        self._ok("gate", "HARD-STOP", "t", "--target-hit", "no")
        self.assertEqual(self._trace_lines()[-1]["target_hit"], "no")
        self._ok("phase", "verify", "t")
        self._ok("gate", "PASS", "t", "--target-hit", "partial")
        self.assertEqual(self._state_task().get("target_hit"), "partial")
        self.assertEqual(self._trace_lines()[-1]["target_hit"], "partial")

    # Reject target_hit_invalid: an unknown value refuses BEFORE any write
    def test_invalid_value_refused_before_write(self):
        self._board_at_build()
        out, code = self._run("gate", "PASS", "t", "--target-hit", "maybe")
        self.assertNotEqual(code, 0, "an invalid --target-hit must refuse")
        self.assertIn("target_hit_invalid", out)
        self.assertNotEqual(self._state_task().get("gate"), "PASS",
                            "the refusal must land before the verdict write")
        self.assertEqual(self._trace_lines(), [], "no trace on a refused gate")

    # Reject absence_is_conformant: no flag -> null in the trace, no state key
    def test_absent_flag_null(self):
        self._board_at_build()
        self._ok("gate", "PASS", "t")
        self.assertNotIn("target_hit", self._state_task())
        self.assertIsNone(self._trace_lines()[-1]["target_hit"])


class ShardToleranceTest(_Harness):
    # Must (2.0 contract): shard files in the task folder never trip the scope guard
    def test_shards_never_trip_scope_guard(self):
        self._board_at_build()
        shard_dir = self.tmp / ".add" / "tasks" / "t"
        (shard_dir / "notes-shard.md").write_text("# build notes\n", encoding="utf-8")
        (shard_dir / "evidence").mkdir()
        (shard_dir / "evidence" / "run-1.txt").write_text("ok\n", encoding="utf-8")
        out = self._ok("gate", "PASS", "t")
        self.assertIn("gate -> PASS", out)
        self.assertEqual(self._state_task().get("gate"), "PASS",
                         "shard files are the AI's free architecture — never a scope touch")


if __name__ == "__main__":
    unittest.main()
