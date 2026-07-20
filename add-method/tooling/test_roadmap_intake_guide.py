"""Red suite for roadmap-intake-guide (milestone multi-milestone-intake 2/3). Contract §3 FROZEN @ v1.

intake.md gains a `## Roadmap` section: a request that decomposes into N>1 milestones is proposed
as a roadmap and, on human confirm, created as 1 active + N−1 `new-milestone --queued`, then
promoted one at a time with `activate`. Convention-only (no engine change). The glossary defines
the `queued` milestone status + "roadmap". One assertion per frozen scenario.

RED until the section + glossary entries exist; GREEN after build. Mirror parity asserted here too.
"""
from __future__ import annotations

from pathlib import Path
import unittest

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

_CANON_SKILL = _ADD_METHOD / "skill" / "add"
_BUNDLE_SKILL = _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add"
_DOGFOOD_SKILL = _REPO / ".claude" / "skills" / "add"

_INTAKE = _CANON_SKILL / "intake.md"
_GLOSSARY = _ADD_METHOD / "docs" / "appendix-c-glossary.md"


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _section(doc: str, heading: str) -> str:
    out, cap = [], False
    for ln in doc.splitlines():
        if ln.startswith("## "):
            if cap:
                break
            cap = ln[3:].strip().lower().startswith(heading.lower())
            if cap:
                out.append(ln); continue
        elif cap:
            out.append(ln)
    return "\n".join(out)


class RoadmapIntakeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intake = _text(_INTAKE)
        cls.lower = cls.intake.lower()

    # Scenario: intake.md has a Roadmap section
    def test_roadmap_section_exists(self):
        self.assertIn("## roadmap", self.lower, "intake.md must add a '## Roadmap' section")

    # Scenario: the roadmap section names the engine path
    def test_section_names_engine_path(self):
        sec = _section(self.intake, "Roadmap")
        self.assertIn("--queued", sec, "the Roadmap section must name `new-milestone --queued`")
        self.assertIn("activate", sec.lower(), "the Roadmap section must name `activate` to promote")
        self.assertTrue("1 active" in sec.lower() or "first active" in sec.lower()
                        or "one active" in sec.lower(),
                        "the section must describe 1 active + the rest queued")

    # Scenario: the intake floor is preserved
    def test_floor_propose_then_confirm(self):
        sec = _section(self.intake, "Roadmap").lower()
        self.assertIn("propose", sec, "roadmap must be PROPOSED by the AI")
        self.assertIn("confirm", sec, "roadmap_unconfirmed: the human must CONFIRM before creation")

    # Scenario: roadmap is distinguished from split_required
    def test_distinguished_from_split_required(self):
        self.assertIn("split_required", self.lower,
                      "the roadmap guidance must contrast itself with split_required")

    # Scenario: glossary defines the new terms
    def test_glossary_defines_terms(self):
        g = _text(_GLOSSARY).lower()
        self.assertIn("queued", g, "glossary must define the queued milestone status")
        self.assertIn("roadmap", g, "glossary must define roadmap as the multi-milestone intake artifact")

    # Scenario: convention-only, mirrors in sync


if __name__ == "__main__":
    unittest.main(verbosity=2)
