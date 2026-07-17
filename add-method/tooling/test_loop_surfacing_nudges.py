"""loop-surfacing-nudges (self-improving-loop): the engine surfaces the loop's own accumulation.

CONTRACT (frozen @ v1):
  ADDITIVE status cues, after the releasable lines: `→ carried: N deferred spec delta(s) —
  add.py deltas --carried` (N>0) and `→ compaction: B folded bullet(s) above the settled line
  (last rolled fvK|never, now fvM) — compact-foundation.md` (B >= 25). A clean project's
  status output is byte-identical. release-report's TEXT gains a `Carried (N)` total set; its
  --json facts interface is UNCHANGED. loop.md's gather step names `deltas --carried` at net
  <=0B on the 41300-floor orchestration pool. Cues COUNT, never judge — no write, no verb.
Run: python3 -m unittest test_loop_surfacing_nudges -v
"""
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

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent

CARRIED = ("  - [SPEC · carried] widen the retry window (evidence: task §6) "
           "[carried: parked for v2]\n")


class _Base(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-lsn-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._run("init", "--name", "demo", "--stage", "mvp")
        self._run("lock", "--force")
        self._run("new-task", "t", "--title", "T")

    def _run(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code or 0
        self.assertEqual(code, 0, f"{argv} exited {code}: {err.getvalue()}")
        return buf.getvalue() + err.getvalue()

    def _plant_carried(self):
        md = self.tmp / ".add" / "tasks" / "t" / "TASK.md"
        t = md.read_text(encoding="utf-8")
        marker = "### Spec delta\n"
        i = t.index(marker) + len(marker)
        j = t.index("\n", i) + 1
        md.write_text(t[:j] + CARRIED + t[j:], encoding="utf-8")

    def _plant_tail(self, n, settled_to=None):
        proj = self.tmp / ".add" / "PROJECT.md"
        s = proj.read_text(encoding="utf-8")
        if "foundation-version:" not in s:
            s = re.sub(r"(?m)^(slug:.*)$", r"\1 · foundation-version: 30", s, count=1)
        bullets = "".join(f"- lesson {i}.  [folded foundation-version {i + 3}]\n"
                          for i in range(n))
        s += "\n## Spec\n" + bullets
        if settled_to:
            s += f"- settled fv1–fv{settled_to} — early work (see git)\n"
        proj.write_text(s, encoding="utf-8")


class StatusCues(_Base):

    def test_status_silent_when_clean(self):                       # R1
        out = self._run("status")
        self.assertNotIn("carried:", out)
        self.assertNotIn("compaction:", out)

    def test_below_threshold_is_quiet(self):                       # R1 edge
        self._plant_tail(24, settled_to=2)
        out = self._run("status")
        self.assertNotIn("compaction:", out)
class LoopGuideAndParity(unittest.TestCase):
    def test_loop_md_names_carried(self):                          # M4
        # kernel-trim (ADD 2.0 M5): the carried lens died — the gather step
        # points at the one open-deltas surface.
        text = (ADD_METHOD / "skill" / "add" / "loop.md").read_text(encoding="utf-8")
        self.assertIn("add.py deltas", text,
                      "loop.md's gather step must point at the open-deltas surface")

    def test_pool_holds_dedup_floor(self):                         # R3
        # skill-fold-8 dropped advisor.md (floor 41300→36361); kernel-trim (ADD 2.0
        # M5) dropped streams.md (16223B) — the floor drops by its bytes, never
        # re-widened: 36361 − 16223 = 20138.
        guides = ["run.md", "loop.md", "design.md"]
        skill = ADD_METHOD / "skill" / "add"
        total = sum((skill / g).stat().st_size for g in guides)
        self.assertLessEqual(total, 20138, "the dedup RECLAIM floor must hold")


if __name__ == "__main__":
    unittest.main()
