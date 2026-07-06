"""persona-load-performance (dynamic-personas): what an agent ingests at persona load is
current-schema, invariant-true, and cheap to select.

CONTRACT (frozen @ v1):
  The 6 dogfood personas carry `## Abilities` (>=2 bullets, command-anchored) and
  `## Anti-patterns` (default-suspect instincts) and no rotted suite-count snapshot
  (metrics are invariants — template distillation discipline #4). Selection is
  frontmatter-first: the 4 flow-routed roster agents and advisor.md instruct choosing
  from frontmatter (name · vibe · flow) and reading only the chosen body. add-persona
  routes into the teacher library by division directory name, never the catalog README.
  The template names the orient-commands convention. Floor unchanged: never-blocks /
  HARD-STOP wording survives; orchestration pool <= ceiling; twin trees byte-identical.
Run: python3 -m unittest test_persona_load_performance -v
"""
import hashlib
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent

AGENT_TREES = (ADD_METHOD / "agents",
               REPO / ".claude" / "agents",
               ADD_METHOD / "src" / "add_method" / "_bundled" / "agents")
SKILL_TREES = (ADD_METHOD / "skill" / "add",
               REPO / ".claude" / "skills" / "add",
               ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add")
PERSONAS = REPO / ".add" / "personas"
TEMPLATE = ADD_METHOD / "tooling" / "templates" / "personas" / "_template.md.tmpl"
ROSTER = ("add-design", "add-build", "add-verify", "add-advisor")


def _agent(name: str) -> str:
    return (AGENT_TREES[0] / f"{name}.md").read_text(encoding="utf-8")


def _sections(text: str) -> list:
    """Top-level ## headers, fence-aware (skeletons inside ``` blocks don't count)."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith("## "):
            out.append(line[3:].strip())
    return out


class PersonasCarryCurrentSchema(unittest.TestCase):
    def test_abilities_and_antipatterns_present(self):             # M1
        files = sorted(PERSONAS.glob("*.md"))
        self.assertGreaterEqual(len(files), 6, "the seeded dogfood roster shrank")
        for f in files:
            secs = _sections(f.read_text(encoding="utf-8"))
            self.assertIn("Abilities", secs, f"{f.name} misses ## Abilities")
            self.assertIn("Anti-patterns", secs, f"{f.name} misses ## Anti-patterns")

    def test_abilities_are_command_anchored(self):                 # M1
        for f in sorted(PERSONAS.glob("*.md")):
            text = f.read_text(encoding="utf-8")
            body = text.split("## Abilities", 1)[1].split("\n## ", 1)[0]
            bullets = [ln for ln in body.splitlines() if ln.lstrip().startswith("- ")]
            self.assertGreaterEqual(len(bullets), 2,
                                    f"{f.name} Abilities needs >=2 bullets")
            self.assertIn("`", body,
                          f"{f.name} Abilities must anchor to a real backticked command/file")


class MetricsAreInvariants(unittest.TestCase):
    def test_no_rotted_suite_count_literals(self):                 # M2
        for f in sorted(PERSONAS.glob("*.md")):
            text = f.read_text(encoding="utf-8")
            m = re.search(r"\b2[0-9]{3}/0\b", text)
            self.assertIsNone(m, f"{f.name} carries a volatile suite-count snapshot "
                                 f"({m.group(0) if m else ''}) — restate as an invariant")


class SelectionIsFrontmatterFirst(unittest.TestCase):
    def test_roster_agents_instruct_frontmatter_first(self):       # M3
        # "frontmatter" alone is already present (the flow: routing phrase) — require the
        # cost instruction itself: pick from frontmatter, read only the chosen BODY
        for name in ROSTER:
            stanza = _agent(name).split("## Become the persona", 1)[1].split("\n\n", 1)[0]
            self.assertIn("body of the one", stanza,
                          f"{name} must instruct: read only the body of the one you become")

    def test_advisor_block_instructs_frontmatter_first(self):      # M3
        text = (SKILL_TREES[0] / "advisor.md").read_text(encoding="utf-8")
        block = text.split("<persona>", 1)[1].split("</persona>", 1)[0]
        self.assertIn("frontmatter", block,
                      "advisor.md <persona> block must instruct frontmatter-first selection")


class DynamicDraftRoutesIntoTeacher(unittest.TestCase):
    def test_add_persona_routes_by_division_dir(self):             # M4
        text = _agent("add-persona")
        self.assertIn("division", text,
                      "add-persona must route the teacher library by division directory")
        self.assertIn("README", text,
                      "add-persona must be told to skip the teacher catalog README")


class TemplateNamesOrientConvention(unittest.TestCase):
    def test_orient_commands_convention(self):                     # M5
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("orient", text.lower(),
                      "the template's Abilities guidance must name the orient-commands convention")


class FloorAndBudgetsUnchanged(unittest.TestCase):
    def test_never_blocks_and_hard_stop_preserved(self):           # R1
        for name in ROSTER:
            self.assertIn("never block", _agent(name))
            self.assertIn("HARD-STOP", _agent(name))
        gk = (PERSONAS / "security-gatekeeper.md").read_text(encoding="utf-8")
        self.assertIn("HARD-STOP, full stop", gk,
                      "security-gatekeeper's un-forceable wording is untouchable")

    def test_pool_ceiling_held(self):                              # R2
        import test_skill_lean as tsl
        pool = next(p for p in tsl.POOLS if p["name"] == "orchestration")
        target = int(pool["baseline"] * pool["ratio"])
        nbytes = sum(len((tsl._CANON / g).read_bytes())
                     for g in pool["guides"] if (tsl._CANON / g).exists())
        self.assertLessEqual(nbytes, target)

    def test_tree_parity(self):                                    # R3
        for name in ROSTER + ("add-persona",):
            digests = {hashlib.md5((tree / f"{name}.md").read_bytes()).hexdigest()
                       for tree in AGENT_TREES}
            self.assertEqual(len(digests), 1, f"{name}.md drifted across agent trees")
        digests = {hashlib.md5((tree / "advisor.md").read_bytes()).hexdigest()
                   for tree in SKILL_TREES}
        self.assertEqual(len(digests), 1, "advisor.md drifted across skill trees")


if __name__ == "__main__":
    unittest.main()
