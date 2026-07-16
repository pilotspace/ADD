#!/usr/bin/env python3
"""Marker guard for persona-owned gates (task: persona-owns-gates, milestone strategy-intake).

report-template.md is retired from a FIXED, mandated ordered section list into
persona-owned PRINCIPLES: a gate report must CONVEY a required content set, but the
fitting persona owns structure, order, emphasis, length and cadence — adapted per
project. A sensible DEFAULT layout may remain (the persona's baseline); what is
retired is the MANDATE that every gate render those blocks in that order.

The four trust floors survive as persona-contract OBLIGATIONS, not layout:
show-before-ask · one-approval-at-the-freeze · never-pre-stamp. security = HARD-STOP
is the ONE hard, un-persona-negotiable floor (the strikeable carve-out per the
milestone's Shared decisions). The engine is untouched — the `Reported:` trace +
contract/verify_report_unrecorded audit codes stay verbatim; no ENGINE_MD5 repin.

Red before the build rewrite, green after. Run: python3 -m unittest test_persona_owned_gates -v
"""
import hashlib
import importlib.util
import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_REPO = _TOOLING.parent.parent
CANON = _TOOLING.parent / "skill" / "add"
BUNDLED = _TOOLING.parent / "src" / "add_method" / "_bundled" / "skill" / "add"
DOGFOOD = _REPO / ".claude" / "skills" / "add"
TEMPLATE = CANON / "report-template.md"
SKILL = CANON / "SKILL.md"


class PersonaOwnsStructureTest(unittest.TestCase):
    """M1 / R1 — the persona owns the form; no fixed ordered list is MANDATED."""

    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")
        self.low = self.text.lower()

    def test_declares_persona_owns_structure(self):
        self.assertTrue(
            "persona owns" in self.low
            or "persona-owned" in self.low
            or "you own the form" in self.low,
            "report-template.md must hand report structure/order/cadence to the persona",
        )

    def test_no_fixed_ordered_section_list_is_mandated(self):
        # the retired MANDATE language — a persona-owned default may remain, a mandate may not
        self.assertNotIn(
            "The report blocks, in order",
            self.text,
            "the fixed 'report blocks, in order' MANDATE heading must be retired",
        )
        self.assertNotIn(
            "Render every block",
            self.text,
            "the 'Render every block' fixed-layout mandate must be retired",
        )

    def test_names_the_required_content_a_gate_conveys(self):
        self.assertIn(
            "convey",
            self.low,
            "report-template.md must frame the report blocks as content to CONVEY",
        )
        for token in ("arc", "flags", "evidence"):
            self.assertIn(
                token, self.low, f"the required-content set must still name {token!r}"
            )


class FourFloorsSurviveTest(unittest.TestCase):
    """M2 / M3 / R2 — the four floors survive as obligations; security is the one hard floor."""

    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")
        self.low = self.text.lower()

    def test_three_soft_floors_present(self):
        self.assertTrue(
            "show-before-ask" in self.low or "show before ask" in self.low,
            "floor: show-before-ask must be present",
        )
        self.assertTrue(
            "one-approval" in self.low
            or "one approval" in self.low
            or "one freeze" in self.low
            or "one gate" in self.low,
            "floor: one-approval-at-the-freeze must be present",
        )
        self.assertTrue(
            "pre-stamp" in self.low or "pre stamp" in self.low,
            "floor: never-pre-stamp must be present",
        )

    def test_security_hard_stop_is_the_one_hard_floor(self):
        self.assertIn(
            "HARD-STOP",
            self.text,
            "floor: security = HARD-STOP must be present",
        )
        self.assertTrue(
            "un-persona-negotiable" in self.low
            or re.search(
                r"(one|only)\b[^.\n]{0,60}(hard|un-negotiable|non-negotiable)[^.\n]{0,40}floor",
                self.low,
            )
            is not None,
            "security must be marked the ONE hard, un-persona-negotiable floor",
        )


class EngineUntouchedGuardTest(unittest.TestCase):
    """M5 — this task edits no engine (a green regression guard, red only if the engine is touched)."""

    def test_engine_md5_pin_unchanged(self):
        pin_path = _TOOLING / "engine_pin.py"
        spec = importlib.util.spec_from_file_location("engine_pin_pog", pin_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        add_py = (_TOOLING / "add.py").read_bytes()
        self.assertEqual(
            hashlib.md5(add_py).hexdigest(),
            mod.ENGINE_MD5,
            "persona-owns-gates must not touch the engine (ENGINE_MD5 must still match add.py)",
        )

    def test_report_trace_audit_codes_intact(self):
        add_py = (_TOOLING / "add.py").read_text(encoding="utf-8")
        for code in (
            "contract_report_unrecorded",
            "verify_report_unrecorded",
            "_REPORTED_LINE_RE",
        ):
            self.assertIn(
                code, add_py, f"the engine report-trace symbol {code!r} must stay intact"
            )


class SkillNamesPrinciplesTest(unittest.TestCase):
    """M4 — SKILL.md names the principles, stays under the ceiling, 3 trees byte-identical."""

    def test_skill_report_line_names_principles_not_fixed_sequence(self):
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("report-template", skill, "SKILL.md must point at report-template.md")
        self.assertNotIn(
            "FLAGS → DECIDED → EVIDENCE → APPROVE → NEXT",
            skill,
            "SKILL.md must not restate the fixed banner→…→NEXT sequence as the mandate",
        )

    def test_skill_under_ceiling(self):
        self.assertLess(
            SKILL.stat().st_size, 9500, "SKILL.md must stay under the 9500 B ceiling"
        )

    def test_three_skill_trees_byte_identical(self):
        for rel in ("report-template.md", "SKILL.md"):
            a = hashlib.md5((CANON / rel).read_bytes()).hexdigest()
            b = hashlib.md5((BUNDLED / rel).read_bytes()).hexdigest()
            c = hashlib.md5((DOGFOOD / rel).read_bytes()).hexdigest()
            self.assertEqual(a, b, f"{rel}: canonical vs _bundled must be byte-identical")
            self.assertEqual(a, c, f"{rel}: canonical vs dogfood must be byte-identical")


if __name__ == "__main__":
    unittest.main(verbosity=2)
