#!/usr/bin/env python3
"""Red/green tests for the phase-agent roster (agency-agents integration).

ADD ships a registered subagent per phase — a roster of phase-specialists the orchestrator
spawns step by step (`add:add-<phase>` as a plugin · `add-<phase>` as a project agent). Each
agent codifies that phase's ROLE (lifted from the phase guide — single source of truth) wrapped
in ONE shared worker contract: load the fit `.add/personas/<slug>.md` and BECOME it · the hard
boundary (never weaken a test, never edit a frozen contract; SECURITY is always HARD-STOP) ·
the confidence.md self-score · a fixed disclose-progress return. The roster rides in the plugin
(`agents/`, auto-discovered) and is mirrored into `.claude/agents/` so this repo dogfoods it.

Run: python3 -m unittest test_phase_agents -v
"""
import re
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent              # add-method/  (plugin root — `.claude-plugin/plugin.json`)
REPO_ROOT = PKG_ROOT.parent            # AIDD-Book/   (the working repo)

# the 9 phases, one registered subagent each (ground is its own §0 mapper, separate from setup)
PHASES = ("setup", "ground", "specify", "scenarios", "contract",
          "tests", "build", "verify", "observe")

# the agent roster lives in TWO trees, byte-identical:
#   plugin (ships to plugin users, auto-discovered)  +  repo .claude/agents (in-repo dogfooding)
AGENT_TREES = (PKG_ROOT / "agents", REPO_ROOT / ".claude" / "agents")

# every agent body must carry the ONE shared worker contract (markers, lower-cased match)
CONTRACT_MARKERS = (
    ".add/personas",   # load the fit persona and become it
    "hard-stop",       # the security boundary
    "security",        # ... is always HARD-STOP
    "weaken",          # never weaken / skip a test
    "frozen contract", # never edit the frozen contract
    "confidence",      # the confidence.md self-score
    "return",          # the fixed disclose-progress return shape
    ".add/docs",       # method depth defers to the book (single source of truth)
)

_NAME_RE = re.compile(r"^[a-z][a-z-]*$")


def _agent_path(tree: Path, phase: str) -> Path:
    return tree / f"add-{phase}.md"


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
    def test_all_nine_agents_exist_in_both_trees(self):
        for tree in AGENT_TREES:
            for phase in PHASES:
                p = _agent_path(tree, phase)
                self.assertTrue(p.is_file(), f"missing phase-agent: {p}")

    def test_no_stray_agents_in_roster(self):
        # exactly the 9 add-<phase>.md files — no orphan, no typo'd duplicate
        want = {f"add-{p}.md" for p in PHASES}
        for tree in AGENT_TREES:
            got = {p.name for p in tree.glob("add-*.md")}
            self.assertEqual(got, want, f"roster drift in {tree}: {got ^ want}")


class FrontmatterTest(unittest.TestCase):
    def test_required_frontmatter_fields(self):
        for phase in PHASES:
            text = _agent_path(AGENT_TREES[0], phase).read_text(encoding="utf-8")
            fm = _frontmatter(text)
            self.assertEqual(fm.get("name"), f"add-{phase}",
                             f"add-{phase}: name must be 'add-{phase}'")
            self.assertTrue(_NAME_RE.match(fm.get("name", "")),
                            f"add-{phase}: name must be lowercase letters + hyphens")
            self.assertTrue(fm.get("description"),
                            f"add-{phase}: a non-empty description is required")
            # model defaults to inherit; if set it must be a known tier/inherit
            model = fm.get("model")
            if model is not None:
                self.assertIn(model, ("inherit", "sonnet", "opus", "haiku", "fable"),
                              f"add-{phase}: model must be a known tier or inherit")


class SharedContractTest(unittest.TestCase):
    def test_each_agent_carries_the_worker_contract(self):
        for phase in PHASES:
            low = _agent_path(AGENT_TREES[0], phase).read_text(encoding="utf-8").lower()
            for marker in CONTRACT_MARKERS:
                self.assertIn(marker, low,
                              f"add-{phase}: missing shared-contract marker {marker!r}")

    def test_each_agent_names_its_phase(self):
        for phase in PHASES:
            low = _agent_path(AGENT_TREES[0], phase).read_text(encoding="utf-8").lower()
            self.assertIn(phase, low, f"add-{phase}: body must name its own phase")

    def test_generic_persona_degrade_path(self):
        # no fit persona seeded → a generic engineer, never blocks (mirrors the PROMPT template)
        for phase in PHASES:
            low = _agent_path(AGENT_TREES[0], phase).read_text(encoding="utf-8").lower()
            self.assertIn("no persona", low,
                          f"add-{phase}: must document the no-persona degrade path")


class ParityTest(unittest.TestCase):
    def test_roster_byte_identical_across_trees(self):
        for phase in PHASES:
            bodies = {_agent_path(t, phase).read_text(encoding="utf-8") for t in AGENT_TREES}
            self.assertEqual(len(bodies), 1,
                             f"add-{phase}.md must be byte-identical across agent trees")


if __name__ == "__main__":
    unittest.main(verbosity=2)
