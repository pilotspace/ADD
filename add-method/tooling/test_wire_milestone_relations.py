#!/usr/bin/env python3
"""Red/green for wire-milestone-relations (engine-hygiene, frozen §3 v1).

Finish-wires the parsed-but-unused `_milestone_relations` into a command surface:
a new `_milestone_relations_health(root, state)` validates every milestone's
relation edges (dangling target / self edge), surfaced ADVISORY (never red) in
cmd_check (per-finding warnings) and cmd_status (a one-line count) — mirroring the
task-level `_relations_health`.

Run: python3 -m unittest test_wire_milestone_relations -v
"""
import hashlib
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
import engine_pin

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"
ADDPY_TRIO = (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
              BUNDLE / "tooling" / "add.py")


class _Board(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-msrel-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")

    def tearDown(self):
        os.chdir(self._cwd)

    def _silent(self, *argv):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            try:
                add.main(list(argv))
            except SystemExit:
                pass

    def _run(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _root(self):
        return self.tmp / ".add"

    def _add_ms(self, slug, *header_rel_lines):
        """Create milestone `slug`, then inject relation line(s) into its MILESTONE.md header."""
        self._silent("new-milestone", slug, "--title", slug.upper(), "--goal", "g")
        if header_rel_lines:
            p = self._root() / "milestones" / slug / "MILESTONE.md"
            txt = p.read_text(encoding="utf-8")
            # insert the relation lines right after the H1 title (still in the header, before any `## `)
            lines = txt.splitlines()
            lines.insert(1, "\n".join(header_rel_lines))
            p.write_text("\n".join(lines), encoding="utf-8")


class MilestoneRelationsHealthTest(_Board):
    def test_health_flags_dangling_and_self(self):
        self._add_ms("a", "relates-to: ghost")   # ghost is no milestone -> dangling
        self._add_ms("b", "depends-on: b")        # names itself -> self
        findings = add._milestone_relations_health(self._root(), add.load_state(self._root()))
        kinds = sorted((f["mslug"], f["kind"]) for f in findings)
        self.assertIn(("a", "dangling"), kinds, f"A→ghost must be dangling: {findings}")
        self.assertIn(("b", "self_relation"), kinds, f"B→B must be self_relation: {findings}")
        self.assertEqual(len(findings), 2, f"exactly the 2 findings, no more: {findings}")

    def test_clean_project_no_findings(self):
        self._add_ms("a")
        self._add_ms("b", "depends-on: a")        # resolves to a known milestone -> silent
        self.assertEqual(add._milestone_relations_health(self._root(), add.load_state(self._root())), [],
                         "resolvable + relation-less milestones yield no findings")


class SurfaceTest(_Board):
    def test_check_warns_but_does_not_fail(self):
        self._add_ms("a", "relates-to: ghost")
        self._add_ms("b", "depends-on: b")
        out, err, code = self._run("check")
        blob = out + err
        self.assertIn("ghost", blob, "check surfaces the dangling milestone edge")
        self.assertIn("self_relation", blob.replace("self relation", "self_relation") + blob,
                      "check surfaces the self edge")
        self.assertNotIn("check: FAIL", blob)
        # advisory: dangling/self relations must never turn the check red (exit non-2 for content-fail)
        # a clean-but-warned check still exits 0
        self.assertEqual(code, 0, f"a dangling/self milestone relation must NOT fail the check: {blob}")

    def test_status_prints_advisory_oneliner(self):
        self._add_ms("a", "relates-to: ghost")
        self._add_ms("b", "depends-on: b")
        out, _, _ = self._run("status")
        self.assertIn("milestone-relations:", out, f"status prints the advisory one-liner: {out}")
        self.assertIn("1 dangling", out)
        self.assertIn("1 self", out)

    def test_status_silent_when_clean(self):
        self._add_ms("a")
        out, _, _ = self._run("status")
        self.assertNotIn("milestone-relations:", out,
                         "a clean project prints no milestone-relations line")


if __name__ == "__main__":
    unittest.main(verbosity=2)
