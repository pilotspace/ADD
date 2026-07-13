#!/usr/bin/env python3
"""Red/green tests for bundle-disclosure (six-phase-loop 4/6, frozen v1): phase
guides disclose INTO the roster bundle agents — each agent's own file names the
bundle guide(s) it loads at spawn, the orchestrator reads only SKILL.md when
delegating, and no agent names a deleted guide or a retired step name. The
inline lane stays first-class (load the one phase guide yourself, unchanged).

Run: python3 -m unittest test_bundle_disclosure -v
"""
import hashlib
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parent
REPO_ROOT = PKG_ROOT.parent

_AGENTS = PKG_ROOT / "agents"
_BUNDLED_AGENTS = PKG_ROOT / "src" / "add_method" / "_bundled" / "agents"
_SKILL = PKG_ROOT / "skill" / "add" / "SKILL.md"

# agent -> the exact bundle guides its file must instruct loading (M1-M3)
_BUNDLE_GUIDES = {
    "add-design.md": ["phases/0-setup.md", "phases/1-specify.md", "phases/3-plan.md"],
    "add-build.md": ["phases/4-tests.md", "phases/5-build.md"],
    "add-verify.md": ["phases/6-verify.md"],
}
# step names retired by the six-phase merges — none may survive as a SPAWN STEP
# in a description line (capability prose may still use the lowercase words).
_RETIRED_STEPS = ("GROUND", "SCENARIOS", "CONTRACT", "OBSERVE")
# path-qualified: the DOCS chapters (docs/04-step-2-scenarios.md …) live on; only
# the skill-tree guides were deleted.
_DELETED_GUIDES = ("phases/2-scenarios.md", "phases/7-observe.md")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class BundleGuidesTest(unittest.TestCase):
    def test_each_agent_names_its_bundle_guides(self):             # M1 + M2 + M3 + Accept
        for name, guides in _BUNDLE_GUIDES.items():
            text = (_AGENTS / name).read_text(encoding="utf-8")
            missing = [g for g in guides if g not in text]
            self.assertEqual(missing, [],
                             f"{name} must name the bundle guide(s) it loads at spawn; "
                             f"missing: {missing}")

    def test_no_agent_names_a_deleted_guide_or_retired_step(self):  # R1
        for f in sorted(_AGENTS.glob("*.md")):
            text = f.read_text(encoding="utf-8")
            for g in _DELETED_GUIDES:
                self.assertNotIn(g, text, f"{f.name} names the deleted guide {g}")
            desc = next((ln for ln in text.splitlines()
                         if ln.startswith("description:")), "")
            step_m = re.search(r"Spawn at the ([^.]*)\bstep", desc)
            if step_m:
                for retired in _RETIRED_STEPS:
                    self.assertNotIn(retired, step_m.group(1),
                                     f"{f.name} still names retired step {retired} "
                                     f"in its spawn line: {step_m.group(0)}")


class DisclosureSplitTest(unittest.TestCase):
    def test_skill_states_the_disclosure_split(self):              # M4 + R2
        text = _SKILL.read_text(encoding="utf-8")
        self.assertIn("loads its own bundle guides", text,
                      "SKILL.md must state that a delegated roster agent loads "
                      "its own bundle guides (the orchestrator reads SKILL.md only)")

    def test_skill_ceiling_held(self):                             # M4 (ceiling honors)
        size = len(_SKILL.read_bytes())
        self.assertLessEqual(size, 9500,
                             f"SKILL.md is {size}B; the orient-split ceiling binds")


class ParityTest(unittest.TestCase):
    def test_agents_bundled_parity_after_recut(self):              # M5
        for f in sorted(_AGENTS.glob("*.md")):
            twin = _BUNDLED_AGENTS / f.name
            self.assertTrue(twin.exists(), f"bundled twin missing: {twin}")
            self.assertEqual(_md5(twin), _md5(f), f"bundled twin drifted: {f.name}")

    def test_installed_agents_refreshed(self):                     # M5 (.claude copies)
        installed = REPO_ROOT / ".claude" / "agents"
        for name in _BUNDLE_GUIDES:
            f = installed / name
            self.assertTrue(f.exists(), f"installed agent missing: {f}")
            self.assertEqual(_md5(f), _md5(_AGENTS / name),
                             f"installed agent stale: {name}")


if __name__ == "__main__":
    unittest.main()
