#!/usr/bin/env python3
"""RED/green target for milestone thin-engine-loop, W1 (phase-collapse-6-to-3).

The enhancement's PROOF is implementation speed, made measurable: a thin-lane task
must reach `done` in <=3 engine calls (new-task + the prescribed remaining calls),
down from the 5 every current lane prescribes (new-task · advance --to plan · freeze ·
advance · gate). The two `advance` calls are pure Direction-span bookkeeping — a
Direction-span freeze (specify+plan+tests -> build) + the compound gate collapse them.

This test is RED against the 6-phase engine on purpose: it locks the 3-call target so
W1's green is a bar, not a claim. It counts the engine's OWN prescribed calls (its
`recipe` surface) — it does not weaken any floor; freeze/gate/tamper stay mechanical.

Run: python3 -m unittest test_thin_engine_call_floor -v
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
ADD = _TOOLING.parent.parent / ".add" / "tooling" / "add.py"
if not ADD.exists():                       # fresh-checkout tolerance: gitignored mirror absent
    ADD = _TOOLING / "add.py"


def _run(args, cwd):
    return subprocess.run([sys.executable, str(ADD), *args],
                          cwd=cwd, capture_output=True, text=True)


def _prescribed_calls(new_task_out):
    """Count the phase-driving engine calls the engine prescribes to take the thin task
    from creation to `done`: the `recipe` block new-task prints (advance/freeze/gate lines)
    plus the already-spent new-task itself. Deduplicates the compact and listed recipe
    forms by taking the max verb-run in the output."""
    # count only the indented recipe block lines (`  add.py <verb> ...`), not the
    # compact one-line restatement the engine also prints — avoids double-counting.
    verbs = re.findall(r"(?m)^\s+add\.py\s+(advance|freeze|gate)\b", new_task_out)
    return 1 + len(verbs)   # new-task already ran + its prescribed remaining calls


class ThinLaneReachesDoneInThreeCalls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="thin-floor-")
        _run(["init", "--name", "demo", "--stage", "mvp"], self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_thin_task_prescribes_at_most_three_engine_calls(self):
        r = _run(["new-task", "tweak", "--title", "trivial doc tweak", "--thin"], self.tmp)
        self.assertEqual(r.returncode, 0, f"new-task failed: {r.stderr}")
        n = _prescribed_calls(r.stdout + r.stderr)
        self.assertLessEqual(
            n, 3,
            f"thin lane must reach done in <=3 engine calls; engine prescribes {n} "
            f"(the two `advance` bookkeeping calls must collapse into the "
            f"Direction-span freeze + compound gate)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
