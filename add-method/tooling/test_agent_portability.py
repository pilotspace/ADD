#!/usr/bin/env python3
"""Red/green tests for agent-portability (milestone v14, exit criterion 4).

Any agent — Cursor, Copilot, Codex, Claude — must locate and follow the correct
phase guide STARTING FROM AGENTS.md ALONE, through the CLI: `guide` names the
phase playbook file (.claude/skills/add/phases/<n>-<phase>.md) when it exists,
never a dead pointer; the sync-guidelines block states the agent-agnostic loop.
The exit criterion is executed literally by the protocol-walk test. Run:
    python3 -m unittest test_agent_portability -v
"""
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

PHASE_FILES = {
    "specify": "1-specify.md", "scenarios": "2-scenarios.md",
    "contract": "3-contract.md", "tests": "4-tests.md",
    "build": "5-build.md", "verify": "6-verify.md", "observe": "7-observe.md",
}


def _run(argv):
    buf, err = io.StringIO(), io.StringIO()
    code = 0
    try:
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(argv)
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
    return buf.getvalue(), err.getvalue(), code


class _Project(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-portability-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        _run(["init", "--name", "demo"])
        _run(["new-milestone", "v1", "--title", "T", "--goal", "g"])
        _run(["new-task", "t", "--title", "Feature"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _install_skill_tree(self):
        """The layout BOTH installers create: .claude/skills/add/phases/*.md."""
        phases = self.tmp / ".claude" / "skills" / "add" / "phases"
        phases.mkdir(parents=True, exist_ok=True)
        for phase, fname in PHASE_FILES.items():
            (phases / fname).write_text(
                f"# Phase guide — {phase.capitalize()}\n", encoding="utf-8")

    def _to_phase(self, phase):
        _run(["phase", phase, "t"])


class GuideLineTest(_Project):
    def test_guide_names_playbook_per_phase(self):
        self._install_skill_tree()
        for phase, fname in PHASE_FILES.items():
            self._to_phase(phase)
            out, err, code = _run(["guide"])
            self.assertEqual(code, 0, err)
            expect = f".claude/skills/add/phases/{fname}"
            m = re.search(r"^guide  : (.+)$", out, re.M)
            self.assertIsNotNone(m, f"no guide line at phase {phase}:\n{out}")
            self.assertEqual(m.group(1).strip(), expect, f"wrong file at {phase}")
            self.assertTrue((self.tmp / expect).exists())

    def test_no_dead_pointer_without_tree(self):
        # no .claude/skills tree -> hint, never a path to a nonexistent file
        self._to_phase("specify")
        out, _, code = _run(["guide"])
        self.assertEqual(code, 0)
        self.assertIn("phase guides not installed", out)
        for line in out.splitlines():
            if line.startswith("guide"):
                self.assertNotIn(".claude/skills", line,
                                 "must not print a dead path")

    def test_json_guide_key_additive(self):
        self._install_skill_tree()
        self._to_phase("tests")
        out, _, code = _run(["guide", "--json"])
        self.assertEqual(code, 0)
        d = json.loads(out)
        self.assertEqual(d["guide"], ".claude/skills/add/phases/4-tests.md")
        for k in ("task", "phase", "owner", "stop", "next_step", "chapter", "gate"):
            self.assertIn(k, d, "frozen v1 keys must remain")
        # tree absent -> null, never a dead path
        (self.tmp / ".claude" / "skills" / "add" / "phases" / "4-tests.md").unlink()
        out, _, _ = _run(["guide", "--json"])
        self.assertIsNone(json.loads(out)["guide"])

    def test_done_phase_no_pointer(self):
        self._install_skill_tree()
        self._to_phase("verify")
        _run(["gate", "PASS", "t"])
        out, _, code = _run(["guide"])
        self.assertEqual(code, 0)
        self.assertNotRegex(out, r"^guide  :", "done has no playbook pointer")
        out, _, _ = _run(["guide", "--json"])
        self.assertIsNone(json.loads(out)["guide"])

    def test_guide_stays_read_only(self):
        self._install_skill_tree()
        self._to_phase("build")
        state = self.tmp / ".add" / "state.json"
        before = state.read_bytes()
        _run(["guide"])
        _run(["guide", "--json"])
        self.assertEqual(state.read_bytes(), before)


class BlockTest(_Project):
    def _block(self, name):
        text = (self.tmp / name).read_text(encoding="utf-8")
        self.assertIn(add._GUIDE_BEGIN, text)
        return text.split(add._GUIDE_BEGIN, 1)[1].split(add._GUIDE_END, 1)[0]

    def test_block_routes_any_agent(self):
        _run(["sync-guidelines"])
        for name in ("AGENTS.md", "CLAUDE.md"):
            block = self._block(name)
            # the agent-agnostic loop, by command
            self.assertIn("add.py status", block, name)
            self.assertIn("add.py guide", block, name)
            self.assertIn("any agent", block, name)
            # the three non-negotiables
            self.assertIn("Never weaken a test or edit a frozen contract", block, name)
            self.assertIn("ONE human approval", block, name)
            self.assertIn("security", block, name)
            # pinned anchors survive (test_guidelines compatibility)
            self.assertIn("## ADD — how to work in this repo", block, name)
            self.assertIn("PROJECT.md", block, name)


class ProtocolWalkTest(_Project):
    """The exit criterion, executed literally: starting from AGENTS.md alone,
    a non-Claude agent reaches the exact phase guide for the active task."""

    def test_protocol_walk_from_agents_md(self):
        self._install_skill_tree()
        self._to_phase("specify")
        _run(["sync-guidelines"])
        agents = (self.tmp / "AGENTS.md").read_text(encoding="utf-8")

        # step 1 — AGENTS.md names the commands; extract them AS WRITTEN
        cmds = re.findall(r"`python3 (\.add/tooling/add\.py [a-z-]+)`", agents)
        self.assertTrue(any(c.endswith(" status") for c in cmds),
                        f"AGENTS.md must name the status command: {cmds}")
        guide_cmds = [c for c in cmds if c.endswith(" guide")]
        self.assertTrue(guide_cmds, f"AGENTS.md must name the guide command: {cmds}")

        # step 2 — run the guide command exactly as the block names it
        out, err, code = _run(guide_cmds[0].split()[1:])
        self.assertEqual(code, 0, err)

        # step 3 — open the file the guide line names; it IS the phase playbook
        m = re.search(r"^guide  : (\S+)$", out, re.M)
        self.assertIsNotNone(m, f"guide must name the playbook:\n{out}")
        playbook = (self.tmp / m.group(1)).read_text(encoding="utf-8")
        self.assertIn("Specify", playbook,
                      "the walk must land on the Specify phase guide")


if __name__ == "__main__":
    unittest.main(verbosity=2)
