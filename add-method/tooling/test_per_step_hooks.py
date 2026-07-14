"""test_per_step_hooks — guards the Advisor+Confidence hook woven into every phase guide.

Each of the 8 phase guides (0-ground … 7-observe) must carry ONE thin, phase-appropriate
blockquote hook — marked `Advisor · Confidence` — that names BOTH advisor.md and confidence.md,
so an agent self-scores and knows when to delegate in the idiom of the phase it is in. SKILL.md
must cross-ref both docs so they are discoverable. The hooks must be mutually distinct (not
boilerplate) and add no banned idiom / XML tag (those invariants are owned by test_wording_lint /
test_xml_convention; here we pin the surface count is unchanged).

Owning task: per-step-hooks (milestone advisor-context). RED until the hooks exist; GREEN after.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_PHASES = _TOOLING.parent / "skill" / "add" / "phases"
_SKILL = _TOOLING.parent / "skill" / "add" / "SKILL.md"

_PHASE_FILES = (
    "1-specify.md", "2-scenarios.md", "3-plan.md",
    "4-tests.md", "5-build.md", "6-verify.md", "7-observe.md",
)
_MARKER = "Advisor · Confidence"

# wording_lint uses dataclasses (breaks under a synthetic importlib module name), so import it
# by putting tooling/ on the path — the same way test_wording_lint.py does.
sys.path.insert(0, str(_TOOLING))
import wording_lint as _wl  # noqa: E402


def _hook_line(text: str) -> str | None:
    for line in text.splitlines():
        if _MARKER in line:
            return line.strip()
    return None


class TestPerStepHooks(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hooks: dict[str, str] = {}
        for name in _PHASE_FILES:
            p = _PHASES / name
            assert p.exists(), f"phase guide missing: {p}"
            cls.hooks[name] = _hook_line(p.read_text(encoding="utf-8")) or ""
        cls.skill = _SKILL.read_text(encoding="utf-8")

    def test_every_guide_hooked(self) -> None:
        for name in _PHASE_FILES:
            line = self.hooks[name]
            self.assertTrue(line, f"guide_unhooked: {name} has no '{_MARKER}' hook")
            self.assertIn("advisor.md", line, f"{name}: hook must name advisor.md")
            self.assertIn("confidence.md", line, f"{name}: hook must name confidence.md")

    def test_hooks_distinct(self) -> None:
        lines = [self.hooks[n] for n in _PHASE_FILES]
        self.assertEqual(len(set(lines)), len(lines),
                         "hooks must be phase-appropriate, not byte-identical boilerplate")

    def test_hook_is_pure_prose(self) -> None:
        # a blockquote hook carries no paired XML convention tag (keeps the phase-guide vocab clean)
        for name in _PHASE_FILES:
            self.assertNotIn("<prompt>", self.hooks[name])
            self.assertNotIn("<constraints>", self.hooks[name])

    def test_skill_cross_ref(self) -> None:
        self.assertIn("advisor.md", self.skill, "SKILL.md must cross-ref advisor.md")
        self.assertIn("confidence.md", self.skill, "SKILL.md must cross-ref confidence.md")

    def test_wording_surface_count_unchanged(self) -> None:
        self.assertEqual(len(_wl.surface_files()), 32,
                         "editing guides must not change the wording-lint surface count "
                         "(32: +beyond.md @ skill-orient-split; "
                         "0-ground.md + 3-contract.md merged into 3-plan.md @ guides-and-skill, net -1; "
                         "+fast-lane.md @ fast-lane, +components.md @ component-method-docs, "
                         "+sensitivity.md @ sensitivity-glossary, +self-improve.md @ self-improving-guide)")


if __name__ == "__main__":
    unittest.main()
