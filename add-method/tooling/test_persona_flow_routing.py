"""persona-flow-routing (dynamic-personas): the flow: schema field gets writers AND readers.

CONTRACT (frozen @ v1):
  The 1.16.1 persona schema (`flow:` frontmatter · `## Abilities` · `source:` provenance)
  landed with zero consumers. This task wires it live: add-persona drafts to the CURRENT
  schema (teacher-distilled) and returns `flow` in its verdict; the 4 other roster agents
  select flow:-first (design→design · build→build · verify/advisor→advisor); design.md's
  persona evidence checklist and advisor.md's <persona> block route by flow:; the 6 dogfood
  personas carry flow:. Invariants held: a persona never lowers a gate (the generic
  no-match fallback never blocks); the orchestration pool stays under its frozen ceiling;
  agent trees ×2 and skill trees ×3 stay byte-identical; </persona> precedes <strategy>.
Run: python3 -m unittest test_persona_flow_routing -v
"""
import hashlib
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent

AGENT_TREES = (ADD_METHOD / "agents", REPO / ".claude" / "agents")
SKILL_TREES = (ADD_METHOD / "skill" / "add",
               REPO / ".claude" / "skills" / "add",
               ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add")
PERSONAS = REPO / ".add" / "personas"

# roster agent → the flow: value its "Become the persona" stanza must select first
FLOW_OF = {"add-design": "design", "add-build": "build",
           "add-verify": "advisor", "add-advisor": "advisor"}
KNOWN_FLOWS = {"design", "build", "advisor"}


def _agent(name: str) -> str:
    return (AGENT_TREES[0] / f"{name}.md").read_text(encoding="utf-8")


def _skill(name: str) -> str:
    return (SKILL_TREES[0] / name).read_text(encoding="utf-8")


class AddPersonaDraftsCurrentSchema(unittest.TestCase):
    def test_drafting_bullet_names_flow_abilities_source(self):    # M1
        text = _agent("add-persona")
        self.assertIn("`flow:`", text,
                      "add-persona must draft the flow: routing frontmatter")
        self.assertIn("`source:`", text,
                      "add-persona must record teacher provenance via source:")
        self.assertIn("## Abilities", text,
                      "add-persona must draft the ## Abilities section")

    def test_return_verdict_carries_flow(self):                    # M1
        text = _agent("add-persona")
        stanza = text.split("## Return (disclose progress)", 1)[1]
        self.assertRegex(stanza, r"\bflow\b",
                         "the Return verdict must carry the persona's flow")


class RosterAgentsSelectFlowFirst(unittest.TestCase):
    def test_each_agent_names_its_flow(self):                      # M2
        for name, flow in FLOW_OF.items():
            text = _agent(name)
            stanza = text.split("## Become the persona", 1)[1].split("\n\n", 1)[0]
            self.assertIn(f"`flow: {flow}`", stanza,
                          f"{name} must select `flow: {flow}` personas first")


class DesignChecklistRoutesByFlow(unittest.TestCase):
    def test_checklist_keys_on_flow_design(self):                  # M3
        text = _skill("design.md")
        self.assertIn("`flow: design`", text,
                      "design.md's persona evidence checklist must key on flow: design")


class AdvisorPersonaBlockPrefersFlow(unittest.TestCase):
    def test_persona_block_names_flow(self):                       # M4
        text = _skill("advisor.md")
        block = text.split("<persona>", 1)[1].split("</persona>", 1)[0]
        self.assertIn("flow", block,
                      "advisor.md's <persona> block must prefer a flow-matched persona")

    def test_persona_still_precedes_strategy(self):                # M4 (ordering pin)
        # line-start tags only — advisor.md line ~28 MENTIONS `<strategy>` in prose
        text = _skill("advisor.md")
        self.assertLess(text.index("\n</persona>"), text.index("\n<strategy>"))


class DogfoodPersonasCarryFlow(unittest.TestCase):
    def test_all_seeded_personas_have_flow(self):                  # M5
        files = sorted(PERSONAS.glob("*.md"))
        self.assertGreaterEqual(len(files), 6, "the seeded dogfood roster shrank")
        for f in files:
            fm = f.read_text(encoding="utf-8").split("---", 2)[1]
            m = re.search(r"^flow:\s*(.+)$", fm, re.MULTILINE)
            self.assertIsNotNone(m, f"{f.name} misses the flow: frontmatter line")
            vals = {v.strip() for v in m.group(1).split(",")}
            self.assertTrue(vals <= KNOWN_FLOWS,
                            f"{f.name} flow values {vals} outside {KNOWN_FLOWS}")


class NoGateCreep(unittest.TestCase):
    def test_generic_fallback_never_blocks(self):                  # R1
        for name in FLOW_OF:
            self.assertIn("never block", _agent(name),
                          f"{name} must keep its generic never-blocks fallback")
        self.assertIn("never blocks", _skill("advisor.md"),
                      "advisor.md's no-match fallback must never block")
        self.assertIn("never lowers a gate", _skill("design.md"),
                      "design.md must keep: a persona never lowers a gate")


class BudgetsAndParityHold(unittest.TestCase):
    def test_orchestration_pool_absorbed(self):                    # R2
        import test_skill_lean as tsl
        pool = next(p for p in tsl.POOLS if p["name"] == "orchestration")
        target = int(pool["baseline"] * pool["ratio"])
        nbytes = sum(len((tsl._CANON / g).read_bytes())
                     for g in pool["guides"] if (tsl._CANON / g).exists())
        self.assertLessEqual(nbytes, target,
                             f"orchestration pool {nbytes} B must stay <= {target} B "
                             "(absorb, never budget-bump)")

    def test_trees_stay_in_parity(self):                           # R3
        for name in list(FLOW_OF) + ["add-persona"]:
            digests = {hashlib.md5((tree / f"{name}.md").read_bytes()).hexdigest()
                       for tree in AGENT_TREES}
            self.assertEqual(len(digests), 1, f"{name}.md drifted between agent trees")
        for guide in ("design.md", "advisor.md"):
            digests = {hashlib.md5((tree / guide).read_bytes()).hexdigest()
                       for tree in SKILL_TREES}
            self.assertEqual(len(digests), 1, f"{guide} drifted across skill trees")


if __name__ == "__main__":
    unittest.main()
