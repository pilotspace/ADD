#!/usr/bin/env python3
"""Red/green tests for route-outcome traces (ADD 2.0 M1 persona-core).

CONTRACT: every recorded gate outcome appends ONE JSON line to
`.add/traces/route-outcomes.jsonl` — the evidence stream the persona
performance scoreboard (and the GEPA fold) reads. Engine-derivable fields
only; the append is degrade-safe (an unwritable trace path NEVER blocks the
verdict — state is the source of truth, the trace is telemetry).

Line schema (keys always present, null when unknown):
  ts · task · milestone · kind · lane · routed_by · persona · outcome ·
  heals · recross · age_hours · actor

- lane/routed_by come from the state route record (stamped at freeze).
- persona is parsed from a `persona:<slug>` routed-by prefix; human-routed
  or unrouted -> null.
- kind is read LIVE from the TASK.md header `kind:` line at gate time.
- HARD-STOP traces too — every outcome is a data point, not only PASS.

Run: python3 -m unittest test_route_trace -v
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

_SEC3 = """### Grounding
Touches (files · symbols): pkg/api/handler.py:handle — the endpoint
Anchors the contract cites: handle
Ground SHA: hand1234 — hand-grounded

### Contract

```
GET /w -> ok
```

`Least-sure flag surfaced at freeze:`
  ⚠ [contract] the shape is the least-sure part — cost if wrong: a reparse.
Status: DRAFT

### Build-strategy
Scope (may touch): `pkg/api/`
"""

TRACE_REL = Path(".add") / "traces" / "route-outcomes.jsonl"
REQUIRED_KEYS = {"ts", "task", "milestone", "kind", "lane", "routed_by",
                 "persona", "outcome", "heals", "recross", "age_hours", "actor"}


class _Harness(unittest.TestCase):
    """A live board arranged through the real CLI (mirrors test_compound_ticks'
    harness — duplicated per this repo's one-harness-per-file norm)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-rtr-")).resolve()
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

    def _board_at_build(self, header_extra: str = ""):
        """A frozen oneshot task moved to build, ready for a completing gate."""
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        self._ok("new-task", "t", "--title", "T", "--oneshot")
        self._ok("advance", "--to", "plan")
        p = self.tmp / ".add" / "tasks" / "t" / "TASK.md"
        text = p.read_text(encoding="utf-8")
        new = re.sub(r"(?ms)(^### Grounding.*?)(?=^---)", _SEC3 + "\n", text, count=1)
        self.assertNotEqual(new, text, "fixture §3 replacement failed")
        new = re.sub(r"(?m)^Boundary:.*$", "Boundary: none — no external input", new, count=1)
        if header_extra:
            new = new.replace("phase: direction", header_extra + "\nphase: direction", 1)
        p.write_text(new, encoding="utf-8")
        self._ok("freeze", "--by", "Tester")
        self._ok("phase", "build", "t")
        return p

    def _trace_lines(self):
        tf = self.tmp / TRACE_REL
        if not tf.is_file():
            return []
        return [json.loads(ln) for ln in
                tf.read_text(encoding="utf-8").splitlines() if ln.strip()]


class TraceOnGateTest(_Harness):
    # Must: a completing gate appends exactly one line with the full schema
    def test_pass_appends_one_line(self):
        self._board_at_build()
        self._ok("gate", "PASS", "t")
        lines = self._trace_lines()
        self.assertEqual(len(lines), 1, "one gate -> one trace line")
        line = lines[0]
        self.assertEqual(REQUIRED_KEYS, set(line) & REQUIRED_KEYS,
                         f"missing keys: {REQUIRED_KEYS - set(line)}")
        self.assertEqual(line["task"], "t")
        self.assertEqual(line["outcome"], "PASS")
        self.assertEqual(line["lane"], "oneshot")
        self.assertEqual(line["heals"], 0)
        self.assertIsInstance(line["age_hours"], (int, float))

    # Must: a persona-routed task records the persona slug (route ratified at freeze)
    def test_persona_parsed_from_route(self):
        self._board_at_build(
            header_extra="route: oneshot · routed-by: persona:tdd-verifier — lean change")
        self._ok("gate", "PASS", "t")
        line = self._trace_lines()[-1]
        self.assertEqual(line["persona"], "tdd-verifier")
        self.assertEqual(line["lane"], "oneshot")

    # Reject no_guess: unrouted / human-routed -> persona null, never inferred
    def test_unrouted_persona_null(self):
        self._board_at_build()
        self._ok("gate", "PASS", "t")
        line = self._trace_lines()[0]
        self.assertIsNone(line["persona"])

    # Must: the declared header kind lands in the trace
    def test_kind_from_header(self):
        self._board_at_build(header_extra="kind: security")
        self._ok("gate", "PASS", "t")
        self.assertEqual(self._trace_lines()[0]["kind"], "security")

    # Reject absence_is_conformant: no kind: line -> null
    def test_absent_kind_null(self):
        self._board_at_build()
        self._ok("gate", "PASS", "t")
        self.assertIsNone(self._trace_lines()[0]["kind"])

    # Must: HARD-STOP is a data point too (recordable from any phase)
    def test_hard_stop_traced(self):
        self._board_at_build()
        self._ok("gate", "HARD-STOP", "t")
        lines = self._trace_lines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["outcome"], "HARD-STOP")

    # Must: consecutive gates accumulate (append, never truncate)
    def test_appends_accumulate(self):
        self._board_at_build()
        self._ok("gate", "HARD-STOP", "t")
        self._ok("phase", "verify", "t")
        self._ok("gate", "PASS", "t")
        outcomes = [l["outcome"] for l in self._trace_lines()]
        self.assertEqual(outcomes, ["HARD-STOP", "PASS"])


class TraceDegradeSafeTest(_Harness):
    # Reject telemetry_blocks_verdict: an unwritable trace path never fails the gate
    def test_unwritable_trace_never_blocks(self):
        self._board_at_build()
        # occupy the traces path with a FILE so mkdir fails with an OSError
        (self.tmp / ".add" / "traces").write_text("squatter", encoding="utf-8")
        out = self._ok("gate", "PASS", "t")
        self.assertIn("gate -> PASS", out)
        state = json.loads((self.tmp / ".add" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["tasks"]["t"]["gate"], "PASS",
                         "the verdict is durable even when the trace write fails")


if __name__ == "__main__":
    unittest.main()
