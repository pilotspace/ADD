#!/usr/bin/env python3
"""Red/green tests for persona-presets (six-phase-loop 5/6, frozen v1): each
roster bundle agent's no-persona fallback upgrades from one thin generic line
to a named teacher-grade expert stance PER OWNED PHASE (`Preset (<phase>):`).
The project-persona routing stays first; a preset never blocks, never lowers
a gate.

Run: python3 -m unittest test_persona_presets -v
"""
import hashlib
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parent
REPO_ROOT = PKG_ROOT.parent
_AGENTS = PKG_ROOT / "agents"
_BUNDLED = PKG_ROOT / "src" / "add_method" / "_bundled" / "agents"

# agent -> the per-phase preset markers its persona section must carry (M1-M3)
_PRESETS = {
    "add-design.md": ["Preset (specify):", "Preset (plan):"],
    "add-build.md": ["Preset (tests):", "Preset (build):"],
    "add-verify.md": ["Preset (verify):"],
}
# the routing-first sentence that must SURVIVE the fallback replacement (M4)
_ROUTING_MARKER = "Load the fit `.add/personas/<slug>.md` and BECOME it"


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class PresetCensusTest(unittest.TestCase):
    def test_each_agent_carries_a_preset_per_owned_phase(self):    # M1-M3 + Accept
        for name, markers in _PRESETS.items():
            text = (_AGENTS / name).read_text(encoding="utf-8")
            missing = [m for m in markers if m not in text]
            self.assertEqual(missing, [],
                             f"{name} must carry a named preset per owned phase; "
                             f"missing: {missing}")

    def test_no_bare_generic_fallback_left(self):                  # M1-M3 (upgrade, not add)
        for name in _PRESETS:
            text = (_AGENTS / name).read_text(encoding="utf-8")
            self.assertNotIn("Use a generic", text,
                             f"{name}: the thin generic fallback must be replaced "
                             f"by the per-phase presets, not kept beside them")

    def test_routing_first_sentence_survives(self):                # M4 + R1
        for name in _PRESETS:
            text = (_AGENTS / name).read_text(encoding="utf-8")
            self.assertIn(_ROUTING_MARKER, text,
                          f"{name}: project-persona routing must stay first — "
                          f"presets are the fallback tier only")
            self.assertIn("never lowers a gate", text,
                          f"{name}: the preset tier must state it never lowers a gate")


class ParityTest(unittest.TestCase):
    def test_presets_synced_x2(self):                              # M5
        installed = REPO_ROOT / ".claude" / "agents"
        for name in _PRESETS:
            canon = _md5(_AGENTS / name)
            self.assertEqual(_md5(_BUNDLED / name), canon, f"bundled drifted: {name}")
            self.assertEqual(_md5(installed / name), canon, f"installed stale: {name}")


if __name__ == "__main__":
    unittest.main()
