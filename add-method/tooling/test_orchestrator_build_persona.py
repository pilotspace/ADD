#!/usr/bin/env python3
"""Doc-truth tests for orchestrator-build-persona (persona-learning-loop 7/7). CONTRACT frozen @ v1.

While building, the orchestrating agent may adopt a project persona as a DOMAIN identity overlay
LAYERED on SOUL.md — phases/build.md documents loading the active `.add/personas/<slug>.md`
(SOUL = voice/trust · persona = domain stance), and the TASK template's §5 Strategy carries an
OPTIONAL persona hook naming the persona the build embodies. SOUL.md stays human-owned (the overlay
never rewrites it) and the persona is advisory (never lowers a gate). The engine never reads the
persona on the build path, so this is doc/template-truth only (no engine change). Run:
python3 -m unittest test_orchestrator_build_persona -v
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
TEMPLATE_TREES = (
    PKG_ROOT / "tooling" / "templates" / "TASK.md.tmpl",
    REPO_ROOT / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.md.tmpl",
)
CANON = SKILL_TREES[0]


def _build_guide(tree: Path) -> str:
    return (tree / "phases" / "build.md").read_text(encoding="utf-8")


class OrchestratorBuildPersonaTest(unittest.TestCase):
    def setUp(self):
        self.text = _build_guide(CANON)
        self.low = self.text.lower()

    def test_build_guide_documents_overlay(self):
        self.assertIn(".add/personas/", self.text,
                      "5-build.md must tell the orchestrator to load the active .add/personas/<slug>.md")
        self.assertIn("overlay", self.low, "5-build.md must frame the persona as a domain identity overlay")
        self.assertIn("soul.md", self.low, "the overlay must be layered on SOUL.md")
        self.assertIn("stance", self.low, "5-build.md must distinguish SOUL voice from the persona's domain stance")

    def test_task_template_has_persona_hook(self):
        # plan-phase-core relocated the Persona hook from §5 BUILD into §3 PLAN's own
        # ### Build-strategy sub-block — re-point, same field, new home.
        body = TEMPLATE_TREES[0].read_text(encoding="utf-8")
        section = body.split("### Build-strategy", 1)[1].split("## 4 ·", 1)[0]
        self.assertIn(".add/personas/", section,
                      "TASK.md.tmpl §3 Build-strategy must name a .add/personas/<slug>.md persona hook")
        self.assertIn("persona", section.lower(), "§3 Build-strategy must mention the persona hook")

    def test_overlay_never_rewrites_soul(self):
        self.assertIn("human-owned", self.low.replace("human owned", "human-owned"),
                      "5-build.md must state SOUL.md is human-owned")
        self.assertIn("never rewrite", self.low.replace("never rewrites", "never rewrite"),
                      "5-build.md must state the overlay never rewrites SOUL.md")
        # The shipped SOUL seed carries none of this task's overlay additions (stays untouched
        # by the overlay). A per-project SOUL.md is generated from this committed template; the
        # template is the byte-stable artifact CI can read (the live skill SOUL.md is not shipped).
        soul = (PKG_ROOT / "tooling" / "templates" / "SOUL.md.tmpl").read_text(encoding="utf-8")
        self.assertNotIn(".add/personas/", soul,
                         "the SOUL seed must not be rewritten with the persona overlay (human-owned)")

    def test_persona_never_lowers_gate(self):
        self.assertIn("never lower", self.low.replace("never lowers", "never lower"),
                      "5-build.md must state the persona never lowers a gate")
        self.assertIn("hard-stop", self.low, "a security finding must still HARD-STOP")


if __name__ == "__main__":
    unittest.main(verbosity=2)
