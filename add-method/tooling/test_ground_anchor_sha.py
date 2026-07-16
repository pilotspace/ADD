#!/usr/bin/env python3
"""Red/green tests for ground-anchor-sha (drift-guard M3/1) — the §0 Ground SHA anchor.

§0 reference rot (PR40 audit): line numbers drift during BUILD while symbols survive. The fix —
the engine SEEDS a `Ground SHA:` field in §0 (the AI fills it with `git rev-parse --short HEAD`,
honoring NO-EXEC) and `add.py check` WARNs (exit 0) when a §0 cites bare line numbers (`l.NNN`)
without one, so drift is detectable instead of silent. Frozen shape (§3 @ v1):
  - TASK.md.tmpl §0 gains a literal `Ground SHA:` field (FULL template only; fast lane omits it);
  - `_read_ground_sha(text)` reads it (None if absent or a `<placeholder>`); `_ground_cites_line_ref`
    probes the §0 block for the `l.\\d+` idiom; cmd_check WARNs when it cites + has no SHA;
  - INVARIANTS: add.py ×3 == re-pinned ENGINE_MD5; TASK.md.tmpl ×3 byte-identical; phases pool ≤ target.

Run: cd add-method/tooling && python3 -m unittest test_ground_anchor_sha -v
"""
from __future__ import annotations

import hashlib
import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import add
import engine_pin

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

TASK_TMPL_COPIES = [
    HERE / "templates" / "TASK.md.tmpl",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.md.tmpl",
    REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
]
ADD_PY_COPIES = [
    HERE / "add.py",
    HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
]
_CANON_SKILL = HERE.parent / "skill" / "add"
PHASES_POOL = [
    "phases/0-setup.md", "phases/1-specify.md",
    "phases/3-plan.md", "phases/4-tests.md",
    "phases/5-build.md", "phases/6-verify.md",
]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class _Board(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-gsa-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self._silent("lock", "--force")

    def _silent(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            try:
                add.main(list(argv))
            except SystemExit as e:
                if e.code:
                    raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        buf = io.StringIO()
        code = 0
        with redirect_stdout(buf), redirect_stderr(buf):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), code

    def _task_md(self, slug: str) -> Path:
        return self.tmp / ".add" / "tasks" / slug / "TASK.md"

    def _patch_ground(self, slug: str, *, line_ref: bool, sha: str | None):
        """Rewrite the task's §0 Touches line to (optionally) cite l.NNN, and set/clear the SHA."""
        p = self._task_md(slug)
        txt = p.read_text(encoding="utf-8")
        cite = " add.py:cmd_release (l.6286) —" if line_ref else " add.py:cmd_release —"
        txt = re.sub(r"(?m)^(Touches[^\n]*):.*$", r"\1:" + cite + " grounded", txt, count=1)
        if sha is not None:
            if re.search(r"(?m)^Ground SHA:", txt):
                txt = re.sub(r"(?m)^Ground SHA:.*$", f"Ground SHA: {sha}", txt, count=1)
            else:  # field not present yet (pre-build) — append into §0 so the test is meaningful
                txt = re.sub(r"(?m)^(Related intent:[^\n]*)$", r"\1\nGround SHA: " + sha, txt, count=1)
        p.write_text(txt, encoding="utf-8")


class GroundShaField(_Board):
    def test_new_task_has_ground_sha_field(self):                 # M1
        # plan-phase-core: grounding (and its `Ground SHA:` field) moved from a
        # standalone §0 BEFORE §1 SPECIFY into the §3 PLAN `### Grounding` sub-block,
        # which now renders AFTER §1/§2 — splitting on "## 1 " no longer isolates the
        # grounding block (it isolates only the header, since §1 comes first now).
        # Re-pointed via add._ground_section, the engine's own grounding extractor.
        self._silent("new-task", "t1", "--title", "T")
        g = self._task_md("t1").read_text(encoding="utf-8")
        grounding = add._ground_section(g)
        self.assertIn("Ground SHA:", grounding,
                      "a new task's §3 PLAN Grounding sub-block must carry a `Ground SHA:` field")


class CheckWarnsOnDrift(_Board):
    def test_check_warns_on_line_ref_without_sha(self):           # M3
        self._silent("new-task", "t1", "--title", "T")
        self._patch_ground("t1", line_ref=True, sha=None)
        out, code = self._run("check")
        self.assertEqual(code, 0, "the drift finding must be a WARN, not a blocking check")
        self.assertRegex(out, r"(?i)t1.*Ground SHA",
                         "check must WARN that t1's §0 cites line numbers without a Ground SHA")

    def test_ground_sha_silences_warning(self):                  # M3
        self._silent("new-task", "t1", "--title", "T")
        self._patch_ground("t1", line_ref=True, sha="abc1234")
        out, code = self._run("check")
        self.assertEqual(code, 0)
        self.assertNotRegex(out, r"(?i)t1[^\n]*Ground SHA",
                            "a present Ground SHA must silence the line-ref warning for t1")

    def test_line_ref_outside_ground_not_flagged(self):          # R:line_ref_false_positive
        self._silent("new-task", "t1", "--title", "T")
        self._patch_ground("t1", line_ref=False, sha=None)       # no l.NNN in §0
        # a line number elsewhere (a §4 path/figure) must never trip the §0-scoped probe
        p = self._task_md("t1")
        p.write_text(p.read_text(encoding="utf-8") + "\n<!-- see ./tests/x.py and l.999 below §0 -->\n",
                     encoding="utf-8")
        out, code = self._run("check")
        self.assertEqual(code, 0)
        self.assertNotRegex(out, r"(?i)t1[^\n]*Ground SHA",
                            "a line number outside §0 must not raise the Ground-SHA warning")


class EnginePinnedAndTemplateParity(unittest.TestCase):
    def test_template_has_ground_sha_and_parity(self):           # M1, M4
        # plan-phase-core: same re-point as test_new_task_has_ground_sha_field above —
        # the Grounding sub-block (and its Ground SHA field) now lives in §3 PLAN,
        # AFTER §1/§2, so a "## 1 " split no longer isolates it.
        present = [p for p in TASK_TMPL_COPIES if p.exists()]
        self.assertEqual(len(present), 3, "all 3 TASK.md.tmpl copies must exist")
        for p in present:
            grounding = add._ground_section(p.read_text(encoding="utf-8"))
            self.assertIn("Ground SHA:", grounding,
                          "TASK.md.tmpl §3 PLAN Grounding must carry a `Ground SHA:` field")
        self.assertEqual(len({_md5(p) for p in present}), 1,
                         "the 3 TASK.md.tmpl copies must be byte-identical")

    def test_engine_byte_identical_to_pin(self):                 # M4, R:engine_pin_drift
        present = [p for p in ADD_PY_COPIES if p.exists()]
        digests = {_md5(p) for p in present}
        self.assertEqual(len(digests), 1, "all add.py copies must be byte-identical")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "add.py must match the re-pinned engine_pin.ENGINE_MD5")

if __name__ == "__main__":
    unittest.main(verbosity=2)
