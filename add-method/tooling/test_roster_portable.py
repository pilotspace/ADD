#!/usr/bin/env python3
"""Red/green tests for the PORTABLE phase-roster in the ADD guideline block
(milestone `portable-roster`, task `roster-portable-shape`, §3 FROZEN @ v1).

The guideline block that `sync-guidelines`/`init` writes into every tool's AGENTS.md
(and Claude's CLAUDE.md) must carry a COMPACT, tool-agnostic roster section — the 5
role-stances mapped to their phase span + recommended tier, plus persona/advisor marked
as cross-cutting services that own no phase — DERIVED from add-method/agents/*.md, and
POINTING to the per-phase guides + the floor already in the block (never restating them).

The roster is a hand-written compact form that this suite parity-CHECKS against the
canonical agents/*.md (CHECK-not-generate): every role name, its phase span, its tier
word, and both service names must be present, and the block↔AGENTS role set is bound
BIDIRECTIONALLY (added / removed / re-tiered => drift). Reject codes are the assertion
messages, matching the sibling test_agent_roster convention. Uses Python string search
only — never shells out to grep (ugrep/BSD-grep gotcha).

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

# Roster data (inlined — formerly shared from the retired test_agent_roster prose guard).
_PKG_ROOT = Path(__file__).resolve().parent.parent      # add-method/
_REPO_ROOT = _PKG_ROOT.parent                            # AIDD-Book/
AGENTS = ("design", "build", "verify", "persona", "advisor")
AGENT_PHASES = {
    "design": ("setup", "ground", "specify", "scenarios", "contract"),
    "build": ("tests", "build"),
    "verify": ("verify", "observe"),
    "persona": (),
    "advisor": (),
}
AGENT_TREES = (_PKG_ROOT / "agents", _REPO_ROOT / ".claude" / "agents")


def _agent_path(tree: Path, agent: str) -> Path:
    return tree / f"add-{agent}.md"


def _frontmatter(text: str) -> dict:
    """Parse the leading YAML-ish frontmatter (key: value) between the first two '---' fences."""
    if not text.startswith("---"):
        return {}
    _, fm, _body = text.split("---", 2)
    out = {}
    for line in fm.strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out

# the tier the roster must show per role — DERIVED from each agent's own description
# ("Recommended tier — <tier>"), never hard-coded here (re-tiering the source moves this).
TIER_RE = re.compile(r"recommended tier\s*[—-]\s*(top|mid)", re.I)
_BULLET_RE = re.compile(r"^\s*[-*]\s*([a-z][a-z-]*)")


def _agent_tier(agent: str) -> str:
    fm = _frontmatter(_agent_path(AGENT_TREES[0], agent).read_text(encoding="utf-8"))
    m = TIER_RE.search(fm.get("description", ""))
    return m.group(1).lower() if m else ""


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


def _role_line(roster: str, role: str) -> str:
    for l in roster.splitlines():
        if role in l.lower():
            return l
    return ""


def _roster_roles(roster: str) -> set:
    """The role short-names the roster lists as bullets (for a bidirectional set check)."""
    return {m.group(1) for l in roster.splitlines() if (m := _BULLET_RE.match(l))}


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
    def test_roster_names_5_roles_and_spans(self):                      # M1
        roster = _roster(self.agents_block())
        self.assertTrue(roster, "block carries no roster section")
        self.assertEqual(_roster_roles(roster), set(AGENTS),
                         f"roster must list exactly {set(AGENTS)}, got {_roster_roles(roster)}")
        for agent in ("design", "build", "verify"):
            line = _role_line(roster, agent).lower()
            first, last = AGENT_PHASES[agent][0], AGENT_PHASES[agent][-1]
            self.assertIn(first, line, f"{agent} line missing first phase {first!r}")
            self.assertIn(last, line, f"{agent} line missing last phase {last!r}")
        for svc in ("persona", "advisor"):
            line = _role_line(roster, svc).lower()
            self.assertRegex(line, r"(service|any phase|cross-cut)",
                             f"{svc} must be marked a cross-cutting service (owns no phase)")

    def test_each_role_shows_tier(self):                                # M2
        roster = _roster(self.agents_block())
        self.assertTrue(roster, "block carries no roster section")
        for agent in AGENTS:
            tier = _agent_tier(agent)
            self.assertIn(tier, ("top", "mid"), f"could not derive tier for {agent}")
            self.assertIn(tier, _role_line(roster, agent).lower(),
                          f"{agent} line must show its recommended tier {tier!r}")

    def test_roster_points_not_restates(self):                          # M3
        block = self.agents_block()
        roster = _roster(block).lower()
        self.assertTrue(roster, "block carries no roster section")
        self.assertIn("guide", roster, "roster must point at the per-phase guides")
        self.assertEqual(block.count("Never weaken a test or edit a frozen contract"), 1,
                         "roster must NOT duplicate the floor sentence (point, don't restate)")

    def test_roster_derived_from_agents(self):                          # M4
        roster = _roster(self.agents_block())
        self.assertTrue(roster, "block carries no roster section")
        for agent in AGENTS:
            line = _role_line(roster, agent).lower()
            self.assertIn(agent, roster.lower(), f"roster missing role {agent}")
            self.assertIn(_agent_tier(agent), line, f"{agent} tier not derived onto its line")
            for phase in (AGENT_PHASES[agent][:1] + AGENT_PHASES[agent][-1:]):
                self.assertIn(phase, line, f"{agent} line missing derived phase {phase!r}")


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
    def test_drift_bidirectional(self):                                 # R1: roster_portable_drift
        roster = _roster(self.agents_block())
        self.assertEqual(
            _roster_roles(roster), set(AGENTS),
            f"roster_portable_drift: block roster roles {_roster_roles(roster)} must EQUAL the "
            f"canonical roster {set(AGENTS)} — added / removed / renamed agent")

    def test_claude_leak_rejected(self):                                # R2: roster_claude_only_leak
        roster = _roster(self.agents_block())
        self.assertTrue(roster, "roster_claude_only_leak: no roster section to check")
        for tok in ("task(subagent_type", "plugin auto-discovery", ".claude/agents"):
            self.assertNotIn(tok, roster.lower(),
                             f"roster_claude_only_leak: portable roster must not carry {tok!r}")

    def test_phase_mismatch_rejected(self):                             # R3: roster_phase_mismatch
        roster = _roster(self.agents_block())
        bline = _role_line(roster, "build").lower()
        self.assertTrue(bline, "roster_phase_mismatch: no build role line")
        self.assertIn("tests", bline, "roster_phase_mismatch: build must map to its own phases")
        for foreign in ("verify", "observe", "specify"):
            self.assertNotIn(foreign, bline,
                             f"roster_phase_mismatch: build line must not name {foreign!r} "
                             f"(a phase build does not own)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
