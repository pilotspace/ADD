#!/usr/bin/env python3
"""Red/green tests for persona-subagent-prompt (persona-learning-loop 4/7).

The portable worker PROMPT loads the active `.add/personas/<slug>.md` (Identity->persona,
Critical Rules->constraints, Success Metrics->done-bar) via a {{PERSONA_SLUG}} slot. ONE canonical
runner-token-free body ships as a seedable template the engine renders LOCALLY (no network, no
process launch); thin per-platform adapter stubs cover the 9 onboarded agents — Claude Code
verified, the rest illustrative. The streams.md worker contract documents the injection point.
Run: python3 -m unittest test_persona_subagent_prompt -v
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
# the 9 coding agents ADD already onboards
PLATFORMS = ("Claude Code", "Codex", "opencode", "Cursor", "Windsurf",
             "Copilot", "Cline", "Aider", "Gemini CLI")
# the marker splitting the runner-token-free BODY from the per-runner ADAPTER STUBS section
ADAPTER_MARKER = "## Adapter stubs"
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

    # scenario: the 9 per-platform stubs exist with the honesty labelling
    def test_nine_platform_stubs_present(self):
        body = _tmpl(TOOLING)
        stubs = body.split(ADAPTER_MARKER, 1)[1]
        for plat in PLATFORMS:
            self.assertIn(plat, stubs, f"an adapter stub must exist for {plat}")

    # scenario: only Claude Code is marked verified; every other is labelled illustrative
    def test_only_claude_code_verified(self):
        stubs = _tmpl(TOOLING).split(ADAPTER_MARKER, 1)[1].lower()
        self.assertIn("verified", stubs, "the Claude Code stub must be marked verified")
        self.assertIn("illustrative", stubs, "non-verified stubs must be labelled illustrative")
        # 'verified' appears once (Claude Code); the others are illustrative
        self.assertEqual(stubs.count("verified"), 1,
                         "exactly one stub (Claude Code) may claim verified; the rest illustrative")

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
    def test_subagent_prompt_parity(self):
        tmpls = {_tmpl(t) for t in ENGINE_TREES}
        self.assertEqual(len(tmpls), 1, "the PROMPT template must be byte-identical across engine trees")
        streams = {_streams(t) for t in SKILL_TREES}
        self.assertEqual(len(streams), 1, "streams.md must be byte-identical across skill trees")


if __name__ == "__main__":
    unittest.main(verbosity=2)
