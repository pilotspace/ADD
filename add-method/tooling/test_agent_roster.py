#!/usr/bin/env python3
"""Red/green tests for phase-agents-lean — a LEAN 4-agent roster (add-design, add-build,
add-verify, add-persona), NOT a mirror of the foreign, unmerged `feat/persona-distillation-depth`
branch's 9-agent one-per-phase roster. Each of add-design/add-build/add-verify spans MULTIPLE ADD
phases (grouped 3-way: design = setup..contract, build = tests+build, verify = verify+observe);
add-persona is a 4th, cross-cutting SERVICE agent that owns no ADD phase — it selects or drafts
the best-fit `.add/personas/<slug>.md` for the other 3 agents (or the orchestrator) on request.

All 4 ship in the plugin (`add-method/agents/`, auto-discovered — no `plugin.json` edit) and are
mirrored byte-identical into `.claude/agents/` for this repo's own dogfooding.

Run: cd add-method/tooling && python3 -m unittest test_agent_roster -v
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent              # add-method/  (plugin root — `.claude-plugin/plugin.json`)
REPO_ROOT = PKG_ROOT.parent            # AIDD-Book/   (the working repo)

AGENTS = ("design", "build", "verify", "persona")

# ADD phases each agent names in its own body. add-persona owns no ADD phase (cross-cutting
# service) — its empty tuple exempts it from SharedContractTest.test_each_agent_names_its_phases.
AGENT_PHASES = {
    "design": ("setup", "ground", "specify", "scenarios", "contract"),
    "build": ("tests", "build"),
    "verify": ("verify", "observe"),
    "persona": (),
}

# the roster lives in TWO trees, byte-identical:
#   plugin (ships to plugin users, auto-discovered)  +  repo .claude/agents (in-repo dogfooding)
AGENT_TREES = (PKG_ROOT / "agents", REPO_ROOT / ".claude" / "agents")

# every agent body must carry the ONE shared worker contract (markers, lower-cased match) —
# adapted from the foreign branch's own CONTRACT_MARKERS (test_phase_agents.py), same 8 markers.
CONTRACT_MARKERS = (
    ".add/personas",   # load the fit persona and become it (or, for add-persona: the schema itself)
    "hard-stop",        # the security boundary
    "security",         # ... is always HARD-STOP
    "weaken",           # never weaken / skip a test
    "frozen contract",  # never edit the frozen contract
    "confidence",       # the confidence.md self-score
    "return",           # the fixed disclose-progress return shape
    ".add/docs",        # method depth defers to the book (single source of truth)
)

_NAME_RE = re.compile(r"^[a-z][a-z-]*$")


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


class RosterPresenceTest(unittest.TestCase):
    def test_all_four_agents_exist_in_both_trees(self):            # M1-M4
        for tree in AGENT_TREES:
            for agent in AGENTS:
                p = _agent_path(tree, agent)
                self.assertTrue(p.is_file(), f"missing agent: {p}")

    def test_no_stray_agents_in_roster(self):                       # R: agent_roster_stray
        want = {f"add-{a}.md" for a in AGENTS}
        for tree in AGENT_TREES:
            got = {p.name for p in tree.glob("add-*.md")}
            self.assertEqual(got, want, f"agent_roster_stray in {tree}: {got ^ want}")


class FrontmatterTest(unittest.TestCase):
    def test_required_frontmatter_fields(self):                     # M7, R: agent_name_mismatch
        for agent in AGENTS:
            text = _agent_path(AGENT_TREES[0], agent).read_text(encoding="utf-8")
            fm = _frontmatter(text)
            self.assertEqual(fm.get("name"), f"add-{agent}",
                              f"agent_name_mismatch: add-{agent} name must be 'add-{agent}'")
            self.assertTrue(_NAME_RE.match(fm.get("name", "")),
                             f"add-{agent}: name must be lowercase letters + hyphens")
            self.assertTrue(fm.get("description"),
                            f"add-{agent}: a non-empty description is required")
            model = fm.get("model")
            if model is not None:
                self.assertIn(model, ("inherit", "sonnet", "opus", "haiku", "fable"),
                              f"add-{agent}: model must be a known tier or inherit")


class SharedContractTest(unittest.TestCase):
    def test_each_agent_carries_the_worker_contract(self):          # M6
        for agent in AGENTS:
            low = _agent_path(AGENT_TREES[0], agent).read_text(encoding="utf-8").lower()
            for marker in CONTRACT_MARKERS:
                self.assertIn(marker, low,
                              f"add-{agent}: missing shared-contract marker {marker!r}")

    def test_each_agent_names_its_phases(self):                     # M1-M3
        for agent, phases in AGENT_PHASES.items():
            if not phases:
                continue  # add-persona: cross-cutting service, owns no ADD phase — exempt by design
            low = _agent_path(AGENT_TREES[0], agent).read_text(encoding="utf-8").lower()
            for phase in phases:
                self.assertIn(phase, low, f"add-{agent}: body must name phase {phase!r}")


class BoundaryTest(unittest.TestCase):
    def test_add_design_never_self_approves_freeze(self):           # R: agent_self_approves_freeze
        low = _agent_path(AGENT_TREES[0], "design").read_text(encoding="utf-8").lower()
        self.assertRegex(
            low, r"never\s+(?:itself\s+)?marks?\s+.*frozen",
            "agent_self_approves_freeze: add-design must state it never marks the contract's "
            "Status as FROZEN itself — that is always the human's decision")

    def test_add_persona_never_clobbers(self):                      # R: persona_agent_clobbers
        low = _agent_path(AGENT_TREES[0], "persona").read_text(encoding="utf-8").lower()
        self.assertRegex(
            low, r"never\s+overwrit\w*\s+an?\s+existing",
            "persona_agent_clobbers: add-persona must state it never overwrites an existing "
            "persona file")


class ParityTest(unittest.TestCase):
    def test_roster_byte_identical_across_trees(self):               # M5, R: agent_roster_drift
        for agent in AGENTS:
            bodies = {_agent_path(t, agent).read_text(encoding="utf-8") for t in AGENT_TREES}
            self.assertEqual(len(bodies), 1,
                             f"agent_roster_drift: add-{agent}.md must be byte-identical "
                             f"across {AGENT_TREES[0]} and {AGENT_TREES[1]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
