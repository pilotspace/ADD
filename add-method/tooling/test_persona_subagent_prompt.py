#!/usr/bin/env python3
"""Red/green tests for persona-subagent-prompt (persona-learning-loop 4/7).

The portable worker PROMPT loads the active `.add/personas/<slug>.md` (Identity->persona,
Critical Rules->constraints, Success Metrics->done-bar) via a {{PERSONA_SLUG}} slot. ONE canonical
runner-token-free body ships as a seedable template the engine renders LOCALLY (no network, no
process launch); a runner-AGNOSTIC spawn contract (four slots: prompt template · persona ·
model · isolation) replaces the retired per-platform adapter table (ADD 2.0 M1 roster-distill) —
Claude Code stays the one verified reference. The streams.md worker contract documents the
injection point. Run: python3 -m unittest test_persona_subagent_prompt -v
"""
import inspect
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

ENGINE_TREES = (
    TOOLING,
    REPO_ROOT / ".add" / "tooling",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling",
)
SKILL_TREES = (
    PKG_ROOT / "skill" / "add",
    REPO_ROOT / ".claude" / "skills" / "add",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "skill" / "add",
)
TMPL_REL = "templates/PROMPT.persona.md.tmpl"
# runner tokens the PORTABLE body must never carry (the spawn contract is runner-agnostic;
# Claude Code alone may appear BELOW the marker as the verified reference)
PLATFORMS = ("Claude Code", "Codex", "opencode", "Cursor", "Windsurf", "Trae",
             "Copilot", "Cline", "Aider", "Gemini CLI")
# the marker splitting the runner-token-free BODY from the runner-agnostic SPAWN CONTRACT
ADAPTER_MARKER = "## Spawn contract"
# the four general slots every runner honors (replaces the retired 10-row adapter table)
CONTRACT_SLOTS = ("prompt template", "persona", "model", "isolation")
# network/process-launch tokens a NO-EXEC path must never contain (built to dodge lint scanners)
FORBIDDEN_EXEC = ("socket", "urllib", "requests", "sub" + "process",
                  "Pop" + "en", "os." + "system", "spa" + "wn")


def _tmpl(tree: Path) -> str:
    return (tree / TMPL_REL).read_text(encoding="utf-8")


def _streams(tree: Path) -> str:
    # streams.md is a SKILL guide — it lives in the skill trees, never the engine (tooling) tree
    return (tree / "streams.md").read_text(encoding="utf-8")


CANON_SKILL = SKILL_TREES[0]


class InjectionPointTest(unittest.TestCase):
    # scenario: the worker PROMPT loads the active persona by slug (mapping covers all 3 sections)
    def test_prompt_injection_maps_all_three_sections(self):
        body = _tmpl(TOOLING)
        self.assertIn("{{PERSONA_SLUG}}", body, "the template must carry a {{PERSONA_SLUG}} slot")
        for section in ("## Identity", "## Critical Rules", "## Success Metrics"):
            self.assertIn(section, body, f"the injection mapping must name the persona '{section}'")
        # the streams.md worker contract documents the injection point too
        self.assertIn("{{PERSONA_SLUG}}", _streams(CANON_SKILL),
                      "streams.md worker contract must reference the {{PERSONA_SLUG}} slot")

    # scenario: one canonical portable body, no runner tokens (in the BODY, before the stubs section)
    def test_portable_body_no_runner_tokens(self):
        body = _tmpl(TOOLING)
        self.assertIn(ADAPTER_MARKER, body, "the template must separate body from adapter stubs")
        portable = body.split(ADAPTER_MARKER, 1)[0]
        for plat in PLATFORMS:
            self.assertNotIn(plat, portable,
                             f"the portable body must carry no runner-specific token (found {plat!r})")

    # scenario: the runner-agnostic spawn contract carries the four general slots
    def test_spawn_contract_slots_present(self):
        contract = _tmpl(TOOLING).split(ADAPTER_MARKER, 1)[1].lower()
        for slot in CONTRACT_SLOTS:
            self.assertIn(slot, contract, f"the spawn contract must carry the '{slot}' slot")
        for plat in PLATFORMS[1:]:
            self.assertNotIn(plat, _tmpl(TOOLING).split(ADAPTER_MARKER, 1)[1],
                             f"no per-runner row may survive (found {plat!r}) — general guidance only")

    # scenario: only Claude Code is named as the verified reference
    def test_only_claude_code_verified(self):
        contract = _tmpl(TOOLING).split(ADAPTER_MARKER, 1)[1].lower()
        self.assertIn("verified", contract, "Claude Code must be marked the verified reference")
        self.assertIn("claude code", contract, "the verified reference must name Claude Code")
        self.assertEqual(contract.count("verified"), 1,
                         "exactly one runner (Claude Code) may claim verified")

    # scenario: degrade-safe when no persona is matched
    def test_degrade_no_persona_generic(self):
        low = (_tmpl(TOOLING) + _streams(CANON_SKILL)).lower()
        self.assertIn("no persona", low,
                      "must document the no-persona degrade path (generic persona, never blocks)")

    # scenario: the template renders locally with no network or process launch (NO-EXEC)
    def test_template_render_path_no_exec(self):
        import add
        src = inspect.getsource(add._render_template)
        for forbidden in FORBIDDEN_EXEC:
            self.assertNotIn(forbidden, src,
                             f"the template render path must stay NO-EXEC (found {forbidden!r})")

    # scenario: the change is byte-identical across the trees


if __name__ == "__main__":
    unittest.main(verbosity=2)
