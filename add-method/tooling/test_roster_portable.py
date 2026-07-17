#!/usr/bin/env python3
"""Red/green tests for the PORTABLE roster in the ADD guideline block.

ADD 2.0 M1 roster-distill: the roster is ONE `add` agent — the spawn names the
mode (direction · build · verify · advise · persona); the agent loads that
beat's phase guide plus the best-fit persona. The guideline block that
`sync-guidelines`/`init` writes into every tool's AGENTS.md (and Claude's
CLAUDE.md) must carry a COMPACT, tool-agnostic roster section DERIVED from
`add-method/agents/add.md`: the one agent, all five modes, and the
persona-carries-the-expertise routing — POINTING at the per-phase guides +
the floor already in the block (never restating them).

The mode set is bound BIDIRECTIONALLY: the block's modes must EQUAL the mode
bullets `agents/add.md` declares (a mode added/removed in the agent file with
no block regen => drift). Python string search only — never shells out to grep.

Run: cd add-method/tooling && python3 -m unittest test_roster_portable -v
"""
from __future__ import annotations

import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

_PKG_ROOT = Path(__file__).resolve().parent.parent      # add-method/
_REPO_ROOT = _PKG_ROOT.parent                            # AIDD-Book/
MODES = ("direction", "build", "verify", "advise", "persona")
AGENT_TREES = (_PKG_ROOT / "agents", _REPO_ROOT / ".claude" / "agents")
AGENT_FILE = "add.md"
# a mode bullet in the agent file's mode-resolution section: `- **direction** — …`
_MODE_BULLET_RE = re.compile(r"(?m)^-\s*\*\*([a-z]+)\*\*")


def _agent_modes(tree: Path) -> set:
    text = (tree / AGENT_FILE).read_text(encoding="utf-8")
    return set(_MODE_BULLET_RE.findall(text))


def _block(text: str) -> str:
    """The block body between the ADD markers (as it ships in a guideline file)."""
    if add._GUIDE_BEGIN not in text or add._GUIDE_END not in text:
        return ""
    return text.split(add._GUIDE_BEGIN, 1)[1].split(add._GUIDE_END, 1)[0]


def _roster(block: str) -> str:
    """The contiguous roster section: from the first 'roster' line to the next blank
    line (or block end). Returns '' when absent, so callers fail cleanly (red), not error."""
    lines = block.splitlines()
    start = next((i for i, l in enumerate(lines) if "roster" in l.lower()), None)
    if start is None:
        return ""
    out: list[str] = []
    for l in lines[start:]:
        if out and not l.strip():
            break
        out.append(l)
    return "\n".join(out)


class _Synced(unittest.TestCase):
    """A temp project after `init` auto-syncs AGENTS.md + CLAUDE.md with the block."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-roster-portable-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            add.main(["init", "--name", "demo"])

    def agents_block(self) -> str:
        return _block((self.tmp / "AGENTS.md").read_text(encoding="utf-8"))

    def claude_block(self) -> str:
        return _block((self.tmp / "CLAUDE.md").read_text(encoding="utf-8"))


class RosterContentTest(_Synced):
    def test_roster_names_one_agent_and_all_modes(self):                # M1
        roster = _roster(self.agents_block()).lower()
        self.assertTrue(roster, "block carries no roster section")
        self.assertIn("`add` agent", roster, "roster must name the ONE `add` agent")
        for mode in MODES:
            self.assertIn(mode, roster, f"roster missing mode {mode!r}")

    def test_roster_derived_from_agent_file(self):                      # M4 (bidirectional)
        roster = _roster(self.agents_block()).lower()
        self.assertTrue(roster, "block carries no roster section")
        self.assertIn(AGENT_FILE, roster, "roster must cite its source agents/add.md")
        declared = _agent_modes(AGENT_TREES[0])
        listed = {m for m in MODES if m in roster} | {m for m in declared if m in roster}
        self.assertEqual(declared, listed,
                         f"roster_portable_drift: block modes {listed} must EQUAL the agent "
                         f"file's declared mode bullets {declared} — regen sync-guidelines")

    def test_roster_routes_personas(self):                              # M2 (2.0: personas core)
        roster = _roster(self.agents_block()).lower()
        self.assertIn("persona", roster, "roster must route the persona loading")
        self.assertIn("expertise", roster,
                      "roster must say personas carry the expertise (the 2.0 core value)")

    def test_roster_points_not_restates(self):                          # M3
        block = self.agents_block()
        roster = _roster(block).lower()
        self.assertTrue(roster, "block carries no roster section")
        self.assertIn("guide", roster, "roster must point at the per-phase guides")
        self.assertEqual(block.count("Never weaken a test or edit a frozen contract"), 1,
                         "roster must NOT duplicate the floor sentence (point, don't restate)")

    def test_block_stays_lean(self):                                    # M7
        block = self.agents_block()
        roster = _roster(block)
        self.assertTrue(roster, "block carries no roster section")
        lines = [l for l in roster.splitlines() if l.strip()]
        self.assertLessEqual(len(lines), 12, f"roster must stay compact, got {len(lines)} lines")
        for anchor in ("## ADD — how to work in this repo", "add.py status", "PROJECT.md"):
            self.assertIn(anchor, block, f"block lost a pinned anchor: {anchor!r}")

    def test_roster_text_identical_across_tools(self):                  # M6
        ra, rc = _roster(self.agents_block()), _roster(self.claude_block())
        self.assertTrue(ra, "AGENTS.md carries no roster section")
        self.assertEqual(ra, rc, "roster text must be byte-identical across tools")


class RosterAgnosticTest(_Synced):
    def test_no_claude_only_mechanism(self):                            # M5
        block = self.agents_block()
        for tok in ("Task(subagent_type", "plugin auto-discovery", ".claude/agents"):
            self.assertNotIn(tok, block, f"block must carry no Claude-only mechanism: {tok!r}")
        self.assertIn("any agent", block, "block must still route any agent")


class RosterRejectTest(_Synced):
    def test_retired_roster_names_gone(self):                           # R1: no zombie roster
        block = self.agents_block()
        for retired in ("add-design", "add-build", "add-verify", "add-persona", "add-advisor"):
            self.assertNotIn(retired, block,
                             f"retired 5-agent roster name must not survive in the block: {retired!r}")

    def test_agent_file_shipped_in_both_trees(self):                    # R2: roster_uninstalled
        for tree in AGENT_TREES:
            self.assertTrue((tree / AGENT_FILE).exists(),
                            f"the ONE `add` agent must ship in {tree}")
            for retired in ("add-design.md", "add-build.md", "add-verify.md",
                            "add-persona.md", "add-advisor.md"):
                self.assertFalse((tree / retired).exists(),
                                 f"retired agent file must be deleted: {tree / retired}")


if __name__ == "__main__":
    unittest.main()
