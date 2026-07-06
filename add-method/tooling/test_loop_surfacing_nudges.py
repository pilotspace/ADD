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
    def test_status_shows_carried(self):                           # M1
        self._plant_carried()
        out = self._run("status")
        self.assertIn("carried: 1 deferred spec delta", out)
        self.assertIn("deltas --carried", out)

    def test_status_shows_compaction_tail(self):                   # M2
        self._plant_tail(25, settled_to=2)
        out = self._run("status")
        self.assertIn("compaction: 25 consolidated lesson", out)
        self.assertIn("last rolled fv2", out)
        self.assertIn("now fv30", out)
        self.assertIn("compact-foundation.md", out)

    def test_never_rolled_reads_never(self):                       # M2 edge
        self._plant_tail(25)
        out = self._run("status")
        self.assertIn("last rolled never", out)

    def test_status_silent_when_clean(self):                       # R1
        out = self._run("status")
        self.assertNotIn("carried:", out)
        self.assertNotIn("compaction:", out)

    def test_below_threshold_is_quiet(self):                       # R1 edge
        self._plant_tail(24, settled_to=2)
        out = self._run("status")
        self.assertNotIn("compaction:", out)


class ReleaseReportCarried(_Base):
    def test_release_report_carried_total(self):                   # M3
        self._plant_carried()
        out = self._run("release-report")
        self.assertIn("Carried (1)", out)

    def test_release_json_keys_unchanged(self):                    # R2
        self._plant_carried()
        out = self._run("release-report", "--json")
        d = json.loads(out)
        self.assertNotIn("carried", d,
                         "the frozen release_data facts interface must not gain keys")


class LoopGuideAndParity(unittest.TestCase):
    def test_loop_md_names_carried(self):                          # M4
        text = (ADD_METHOD / "skill" / "add" / "loop.md").read_text(encoding="utf-8")
        self.assertIn("deltas --carried", text,
                      "loop.md's gather step must include the carried backlog")

    def test_pool_holds_dedup_floor(self):                         # R3
        guides = ["run.md", "streams.md", "advisor.md", "loop.md", "design.md"]
        skill = ADD_METHOD / "skill" / "add"
        total = sum((skill / g).stat().st_size for g in guides)
        self.assertLessEqual(total, 41300, "the dedup RECLAIM floor must hold")

    def test_engine_and_loop_parity(self):                         # R3
        for group in (
            [ADD_METHOD / "tooling" / "add.py", REPO / ".add" / "tooling" / "add.py",
             ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "add.py"],
            [ADD_METHOD / "skill" / "add" / "loop.md",
             REPO / ".claude" / "skills" / "add" / "loop.md",
             ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add" / "loop.md"],
        ):
            digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in group}
            self.assertEqual(len(digests), 1, f"twin drift: {group[0].name}")


if __name__ == "__main__":
    unittest.main()
