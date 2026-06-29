#!/usr/bin/env python3
"""docs-align (advisor-gated-autonomy) — the prose touch-point guard.

The milestone's engine tasks (advisor-review-step / advisor-verdict-audit / advisor-gate-relax)
shipped the BEHAVIOR; docs-align aligns the human-facing PROSE with it. This module is the
red→green artifact for docs-align's content scenarios (§2): each of the 7 touch-points must
state its required content. Parity (3-tree byte-identity), the lean budget, and wording-lint
are guarded by their own modules (test_skill_parity / test_bundle_parity · test_skill_lean ·
test_ubiquitous_language); this module asserts the CONTENT is present.

Run: python3 -m unittest test_docs_align -v
"""
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent

# The three skill trees that must each carry the prose (parity guards byte-identity separately).
_SKILL_TREES = [
    _ADD_METHOD / "skill" / "add",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add",
    _REPO / ".claude" / "skills" / "add",
]
# The two GLOSSARY surfaces (live dogfood file + seeded template).
_GLOSSARY_FILES = [
    _REPO / ".add" / "GLOSSARY.md",
    _ADD_METHOD / "tooling" / "templates" / "GLOSSARY.md.tmpl",
]
# The three template trees (the §6 Advisor 3-lens block ships in each).
_TMPL_FILES = [
    _ADD_METHOD / "tooling" / "templates" / "TASK.md.tmpl",
    _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.md.tmpl",
    _REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


class DocsAlignTouchPoints(unittest.TestCase):
    """One test per §2 content scenario; each asserts the required content in every tree."""

    # 1 — 6-verify.md: the §6 Advisor 3-lens recording instruction.
    def test_6verify_advisor_recording(self):
        for tree in _SKILL_TREES:
            t = _read(tree / "phases" / "6-verify.md")
            self.assertIn("### Advisor 3-lens verdict", t, f"6-verify missing §6 block ref in {tree}")
            self.assertIn("advisor_verdict_unrecorded", t, f"6-verify missing companion lint in {tree}")
            self.assertIn("Binding", t, f"6-verify missing Binding distinction in {tree}")
            self.assertIn("Run the three lenses in order", t, f"6-verify missing sequential order in {tree}")

    # 2 — advisor.md: the 3-lens sequential checklist section.
    def test_advisor_3lens_section(self):
        for tree in _SKILL_TREES:
            t = _read(tree / "advisor.md")
            self.assertIn("The 3-lens sequential checklist at verify", t, f"advisor.md missing section in {tree}")
            self.assertIn("CLEAR", t, f"advisor.md missing CLEAR verdict in {tree}")
            self.assertIn("RESIDUE", t, f"advisor.md missing RESIDUE verdict in {tree}")
            self.assertIn("Verdict", t, f"advisor.md missing record fields in {tree}")
            self.assertIn("Binding", t, f"advisor.md missing Binding field in {tree}")

    # 3 — run.md: the advisor-gate-relax pathway + companion lint.
    def test_runmd_gate_relax_pathway(self):
        for tree in _SKILL_TREES:
            t = _read(tree / "run.md")
            self.assertIn("advisor-gate-relax", t, f"run.md missing pathway name in {tree}")
            self.assertIn("advisor_verdict_unrecorded", t, f"run.md missing companion lint in {tree}")
            # the relax is mechanical-only and never relaxes security / non-mechanical
            self.assertIn("never relaxed", t, f"run.md missing the never-relaxed safety clause in {tree}")

    # 4 — sensitivity.md: the three §6 record fields on the mechanical class.
    def test_sensitivity_three_fields(self):
        for tree in _SKILL_TREES:
            t = _read(tree / "sensitivity.md")
            self.assertIn("Verdict · Residue · Binding", t, f"sensitivity.md missing the 3 fields in {tree}")

    # 5 — SKILL.md: the advisor-gate-relax pointer.
    def test_skill_pointer(self):
        for tree in _SKILL_TREES:
            t = _read(tree / "SKILL.md")
            self.assertIn("advisor-gate-relax", t, f"SKILL.md missing the pointer in {tree}")

    # 6 — TASK.md.tmpl: the §6 Advisor 3-lens verdict block ships in each template tree.
    def test_template_advisor_block(self):
        for p in _TMPL_FILES:
            t = _read(p)
            self.assertIn("### Advisor 3-lens verdict", t, f"template missing the §6 block in {p}")

    # 7 — both GLOSSARY surfaces define all four terms (wording-lint conformant: "level", not "dial").
    def test_glossary_four_terms(self):
        terms = ["advisor-gate-relax", "advisor 3-lens verdict", "binding verdict", "advisory verdict"]
        for p in _GLOSSARY_FILES:
            t = _read(p)
            for term in terms:
                self.assertIn(term, t, f"GLOSSARY {p} missing term: {term!r}")

    # the wording-lint conformance the build chose over the frozen §3 "dial" wording (§6 delta).
    # NOTE: the bridge entry `autonomy level: … (formerly "autonomy dial")` is the sanctioned
    # legacy pointer and stays; only the advisor-gate-relax DEFINITION's usage must say "level".
    def test_glossary_relax_def_uses_level_not_dial(self):
        for p in _GLOSSARY_FILES:
            t = _read(p)
            self.assertIn("lowered autonomy level", t, f"GLOSSARY {p} relax def must use 'lowered autonomy level'")
            self.assertNotIn("lowered autonomy dial", t, f"GLOSSARY {p} reintroduced banned 'lowered autonomy dial'")


if __name__ == "__main__":
    unittest.main()
