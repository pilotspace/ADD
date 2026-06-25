#!/usr/bin/env python3
"""Red/green tests for per-stream-owner (multi-active-UX 2/3): the `status` `streams:` block
names each active stream's milestone owner (present-only), and `status --json` milestone entries
carry owner/assignee — additive, byte-identical when unset. Run:
  python3 -m unittest test_per_stream_owner -v
"""
import hashlib
import io
import json
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import add
from engine_pin import ENGINE_MD5

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_COPIES = (
    REPO / "add-method" / "tooling" / "add.py",
    REPO / ".add" / "tooling" / "add.py",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-streamowner-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        self.state = self.tmp / ".add" / "state.json"

    def tearDown(self):
        os.chdir(self._cwd)

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return code, out.getvalue(), err.getvalue()

    def _poke(self, mutate):
        st = json.loads(self.state.read_text(encoding="utf-8"))
        mutate(st)
        self.state.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")

    def _milestone(self, slug, *, owner=None):
        self._silent("new-milestone", slug, "--goal", "g", "--stage", "mvp")
        if owner is not None:
            self._silent("assign", slug, "--owner", owner)   # slug is a milestone (no same-name task)

    def _activate(self, *slugs):
        self._poke(lambda st: st.__setitem__("active_milestones", list(slugs)))

    def _stream_lines(self, out):
        """The lines under the human `streams:` header (each begins with a 2-space indent + mark)."""
        lines = out.splitlines()
        try:
            start = next(i for i, l in enumerate(lines) if l.startswith("streams :"))
        except StopIteration:
            return []
        block = []
        for l in lines[start + 1:]:
            if l.startswith("  ") and "task=" in l:
                block.append(l)
            elif not l.startswith("  "):
                break
        return block


class StreamOwnerTest(_Harness):
    def test_owned_stream_shows_owner(self):
        self._milestone("m1", owner="Ada <ada@x.io>")
        self._milestone("m2")
        self._activate("m1", "m2")
        before = self.state.read_text(encoding="utf-8")
        code, out, err = self._run("status")
        self.assertEqual(code, 0, err)
        m1_line = next((l for l in self._stream_lines(out) if "m1" in l), "")
        self.assertIn("owner:", m1_line)
        self.assertIn("Ada", m1_line)
        self.assertEqual(self.state.read_text(encoding="utf-8"), before)  # read-only

    def test_no_owner_stream_has_no_owner_fragment(self):
        self._milestone("m1")
        self._milestone("m2")
        self._activate("m1", "m2")
        code, out, err = self._run("status")
        self.assertEqual(code, 0, err)
        block = self._stream_lines(out)
        self.assertTrue(block, "streams block should render with 2 active milestones")
        for line in block:
            self.assertNotIn("owner:", line)               # no fragment when no owner
            self.assertNotIn(" · ", line)                  # not even an empty separator fragment

    def test_blank_name_owner_renders_no_fragment(self):
        # contract: a hand-edited blank-name owner (name "" but an email present) emits NO
        # owner fragment — _fmt_actor would return " <email>" (truthy), so the name-guard matters.
        self._milestone("m1")
        self._milestone("m2")
        self._poke(lambda st: st["milestones"]["m1"].__setitem__(
            "owner", {"name": "", "email": "ghost@x.io", "source": "git"}))
        self._activate("m1", "m2")
        code, out, err = self._run("status")
        self.assertEqual(code, 0, err)
        for line in self._stream_lines(out):
            self.assertNotIn("owner:", line)
            self.assertNotIn("ghost@x.io", line)


class StreamJsonTest(_Harness):
    def test_json_milestone_owner_assignee(self):
        self._milestone("m1", owner="Ada <ada@x.io>")
        self._milestone("m2")
        self._activate("m1", "m2")
        code, out, err = self._run("status", "--json")
        self.assertEqual(code, 0, err)
        obj = json.loads(out)
        m1 = next(m for m in obj["milestones"] if m["slug"] == "m1")
        self.assertEqual(m1["owner"]["name"], "Ada")
        self.assertIn("assignee", m1)
        self.assertIsNone(m1["assignee"])                  # present-only value, None when unset
        # frozen-surface guard: top-level key set unchanged (only sanctioned additive keys)
        base = {"project", "stage", "active_task", "milestones", "tasks"}
        sanctioned = {"graduation_ready", "stage_criteria", "active_milestones",
                      "active_tasks", "actor"}
        self.assertEqual(set(obj) - base, sanctioned)


class StreamSingleTest(_Harness):
    def test_single_milestone_unaffected(self):
        self._milestone("m1", owner="Ada <ada@x.io>")
        self._activate("m1")                               # only ONE active -> no streams block
        code, out, err = self._run("status")
        self.assertEqual(code, 0, err)
        self.assertNotIn("streams :", out)                 # additive-cue: N<=1 untouched
        self.assertEqual(self._stream_lines(out), [])


class EnginePinTest(unittest.TestCase):
    def test_three_trees_byte_identical_and_pinned(self):
        digests = {hashlib.md5(p.read_bytes()).hexdigest() for p in ENGINE_COPIES}
        self.assertEqual(len(digests), 1)
        self.assertEqual(digests.pop(), ENGINE_MD5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
