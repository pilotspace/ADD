#!/usr/bin/env python3
"""Doc-truth tests for persona-required-domain-hint. CONTRACT frozen @ v1.

TASK.md.tmpl's §5 Persona field flips from optional ("absent = generic") to required (the field
must be filled — `generic` is the accepted explicit fallback, not a silent absence). Both
TASK.md.tmpl and TASK.fast.md.tmpl gain a domain-strategy hint in their Strategy line: let the
persona's domain stance shape the chosen implementation approach, not just architecture/pattern
choice. Prose-only — no engine change, no new gate, no new XML tag. Run:
python3 -m unittest test_persona_required_domain_hint -v
"""
import hashlib
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent
REPO_ROOT = PKG_ROOT.parent

TEMPLATE_TREES = (
    PKG_ROOT / "tooling" / "templates" / "TASK.md.tmpl",
    REPO_ROOT / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.md.tmpl",
)
FAST_TREES = (
    PKG_ROOT / "tooling" / "templates" / "TASK.fast.md.tmpl",
    REPO_ROOT / ".add" / "tooling" / "templates" / "TASK.fast.md.tmpl",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.fast.md.tmpl",
)
CANON_TMPL = TEMPLATE_TREES[0]
CANON_FAST = FAST_TREES[0]

STRATEGY_LABEL = "Strategy (ordered batches):"
FAST_STRATEGY_LABEL = "Strategy & known-problem fixes:"

# the v16/v18 frozen tag census of TASK.md.tmpl (mirrors test_scope_decl_template.FROZEN_TAGS —
# duplicated here, not imported, so this test independently proves no new tag was introduced)
FROZEN_TAGS = ['action', 'after', 'alternative', 'assumptions', 'chosen', 'code',
               'cost', 'date', 'error_code', 'fields', 'link', 'must', 'name',
               'path', 'reject', 'scenario', 'scenarios', 'sensitivity',
               'test_plan', 'unchanged', 'why']


def _section(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class PersonaRequiredTest(unittest.TestCase):
    # plan-phase-core relocated Persona/Strategy from §5 BUILD into §3 PLAN's own
    # ### Build-strategy sub-block — re-point the extraction there, same field, new home.
    def setUp(self):
        self.text = CANON_TMPL.read_text(encoding="utf-8")
        self.section5 = _section(self.text, "### Build-strategy", "## 4 ·")

    def test_persona_line_is_required(self):
        self.assertIn("Persona (required):", self.section5,
                      "TASK.md.tmpl §5 Persona line must read '(required)'")
        self.assertNotIn("Persona (optional):", self.section5,
                         "the old '(optional)' wording must not survive")
        self.assertNotIn("absent = generic", self.section5,
                         "the silent 'absent = generic' escape hatch must be removed")

    def test_persona_generic_fallback_named(self):
        self.assertIn("generic", self.section5.lower(),
                      "the Persona line must still name 'generic' as the explicit fallback")

    def test_full_strategy_line_gains_domain_hint(self):
        self.assertIn(STRATEGY_LABEL, self.section5, "Strategy label must be unchanged")
        strategy_line = self.section5[self.section5.index(STRATEGY_LABEL):]
        strategy_line = strategy_line.split(">", 1)[0]
        self.assertIn("Persona", strategy_line,
                      "the Strategy placeholder must reference the named Persona")
        self.assertIn("domain stance", strategy_line.lower(),
                      "the Strategy placeholder must mention the domain stance shaping the approach")


class FastStrategyDomainHintTest(unittest.TestCase):
    def setUp(self):
        self.text = CANON_FAST.read_text(encoding="utf-8")

    def test_fast_strategy_line_gains_domain_hint(self):
        self.assertIn(FAST_STRATEGY_LABEL, self.text, "fast Strategy label must be unchanged")
        strategy_line = self.text[self.text.index(FAST_STRATEGY_LABEL):]
        strategy_line = strategy_line.split(">", 1)[0]
        self.assertIn("persona", strategy_line.lower(),
                      "the fast Strategy placeholder must reference the active persona")
        self.assertIn("domain stance", strategy_line.lower(),
                      "the fast Strategy placeholder must mention the domain stance shaping the approach")


class NoNewFrozenTagTest(unittest.TestCase):
    def test_no_new_frozen_tag(self):
        import re
        tags = sorted(set(re.findall(r"</?([a-z_]+)>", CANON_TMPL.read_text(encoding="utf-8"))))
        self.assertEqual(tags, FROZEN_TAGS,
                         "the v16 XML tag census changed - no new bare <word> tag is allowed")


class MirrorsAndEnginePinTest(unittest.TestCase):
    def test_full_template_mirrors(self):
        digests = {_md5(p) for p in TEMPLATE_TREES}
        self.assertEqual(len(digests), 1, "TASK.md.tmpl diverged across the 3 engine trees")

    def test_fast_template_mirrors(self):
        digests = {_md5(p) for p in FAST_TREES}
        self.assertEqual(len(digests), 1, "TASK.fast.md.tmpl diverged across the 3 engine trees")

    def test_engine_pin_unchanged(self):
        import engine_pin
        live = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(live, engine_pin.ENGINE_MD5,
                         "this task touches no engine code — ENGINE_MD5 must equal the pin")


if __name__ == "__main__":
    unittest.main(verbosity=2)
