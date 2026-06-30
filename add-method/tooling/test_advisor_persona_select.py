#!/usr/bin/env python3
"""Doc-truth tests for advisor-persona-select (persona-learning-loop 6/7). CONTRACT frozen @ v1.

The advisor spawn template SELECTS the best-fit project persona for a delegated piece — its
`<persona>` block loads `.add/personas/<slug>.md` (Identity/Critical Rules/Success Metrics),
reusing streams.md's worker contract — and the `<return>` verdict RECORDS which persona was used.
The refute-read piece selects a Code-Reviewer persona whose findings carry severity markers
(🔴/🟡/💭). A persona is advisory: it never lowers a gate, and no-match degrades to generic. The
engine never spawns, so this is doc-truth only (no engine change). Run:
python3 -m unittest test_advisor_persona_select -v
"""
import hashlib
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

SKILL_TREES = (
    PKG_ROOT / "skill" / "add",
    REPO_ROOT / ".claude" / "skills" / "add",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "skill" / "add",
)
CANON = SKILL_TREES[0]


def _advisor(tree: Path) -> str:
    return (tree / "advisor.md").read_text(encoding="utf-8")


class AdvisorPersonaSelectTest(unittest.TestCase):
    def setUp(self):
        self.text = _advisor(CANON)

    def test_persona_block_selects_and_loads(self):
        self.assertIn(".add/personas/", self.text,
                      "advisor.md <persona> must load the selected .add/personas/<slug>.md")
        for sect in ("Identity", "Critical Rules", "Success Metrics"):
            self.assertIn(sect, self.text, f"the persona mapping must name '{sect}'")

    def test_return_records_persona(self):
        # the <return> verdict shape must carry a persona field
        block = self.text.split("<return>", 1)[1].split("</return>", 1)[0]
        self.assertIn("persona", block,
                      "the <return> verdict shape must record which persona was used")

    def test_refute_read_codereviewer(self):
        low = self.text.lower()
        self.assertIn("code-reviewer", low,
                      "advisor.md must map the refute-read piece to a Code-Reviewer persona")
        for marker in ("🔴", "🟡", "💭"):
            self.assertIn(marker, self.text, f"the Code-Reviewer findings must use the {marker} marker")

    def test_persona_never_lowers_gate(self):
        low = self.text.lower()
        self.assertIn("never lower", low.replace("never lowers", "never lower"),
                      "advisor.md must state a persona never lowers a gate")
        self.assertIn("hard-stop", low, "a security finding must still HARD-STOP")

    def test_degrade_no_persona_generic(self):
        low = self.text.lower()
        self.assertIn("no match", low.replace("no-match", "no match"),
                      "advisor.md must document the no-match degrade")
        self.assertIn("{{domain}}", low, "the generic fallback must remain a {{DOMAIN}} engineer")

    def test_advisor_parity(self):
        variants = {_advisor(t) for t in SKILL_TREES}
        self.assertEqual(len(variants), 1, "advisor.md must be byte-identical across the 3 skill trees")

    def test_engine_unchanged(self):
        import engine_pin
        live = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(live, engine_pin.ENGINE_MD5,
                         "this task touches no engine code — ENGINE_MD5 must equal the pin")


if __name__ == "__main__":
    unittest.main(verbosity=2)
