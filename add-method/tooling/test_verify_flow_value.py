#!/usr/bin/env python3
"""Red/green tests for the dedicated `verify` persona flow value (task verify-flow-value,
milestone delta-drain, contract FROZEN @ v1).

PERSONA_FLOW_VALUES grows to ("design", "build", "advisor", "verify") — verify is the
evidence-judging surface (the earned-green refute-read + the gate-record lens), added
BESIDE advisor (whose delegation meaning is unchanged). Every enumerating surface renders
the same 4-value set: the engine constant/validator, the persona template's flow hint
("four apply-surfaces"), docs/18-personas.md ("Apply — four surfaces"), the add-verify
agent routing (verify first -> advisor fallback), the 6-verify guide bullet, and this
project's tdd-verifier persona (`flow: verify, advisor` — writer+reader in one task).

Run: python3 -m unittest test_verify_flow_value -v
"""
import hashlib
import unittest
from pathlib import Path

import engine_pin
import test_skill_lean
from add_engine.constants import PERSONA_FLOW_VALUES
from add_engine.predicates import _persona_quality_warnings

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"


def _existing(*paths):
    present = tuple(p for p in paths if p.exists())
    assert len(present) >= 2, f"twin set collapsed below canon+bundle: {paths}"
    return present

CONSTANTS_TWINS = _existing(HERE / "add_engine" / "constants.py",
                            REPO / ".add" / "tooling" / "add_engine" / "constants.py",
                            BUNDLE / "tooling" / "add_engine" / "constants.py")
TEMPLATE_TWINS = _existing(HERE / "templates" / "personas" / "_template.md.tmpl",
                           REPO / ".add" / "tooling" / "templates" / "personas" / "_template.md.tmpl",
                           ADD_METHOD / ".add" / "tooling" / "templates" / "personas" / "_template.md.tmpl",
                           BUNDLE / "tooling" / "templates" / "personas" / "_template.md.tmpl")
DOCS_TWINS = (ADD_METHOD / "docs" / "18-personas.md",
              REPO / "18-personas.md",
              BUNDLE / "docs" / "18-personas.md")
AGENT_TWINS = (ADD_METHOD / "agents" / "add-verify.md",
               REPO / ".claude" / "agents" / "add-verify.md",
               BUNDLE / "agents" / "add-verify.md")
GUIDE_TWINS = (ADD_METHOD / "skill" / "add" / "phases" / "6-verify.md",
               REPO / ".claude" / "skills" / "add" / "phases" / "6-verify.md",
               BUNDLE / "skill" / "add" / "phases" / "6-verify.md")
TDD_VERIFIER = REPO / ".add" / "personas" / "tdd-verifier.md"
ADDPY_TRIO = (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
              BUNDLE / "tooling" / "add.py")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _fm(flow_line: str) -> str:
    return f"---\nname: X\nvibe: Y\n{flow_line}\n---\nbody\n"


class VerifyFlowValueTest(unittest.TestCase):
    # ── M1: the frozen 4-value constant, twins lockstep ───────────────────────────
    def test_constant_is_the_frozen_4_tuple(self):
        self.assertEqual(PERSONA_FLOW_VALUES, ("design", "build", "advisor", "verify"))

    def test_constants_twins_lockstep(self):
        self.assertEqual(len({_md5(p) for p in CONSTANTS_TWINS}), 1, "constants.py twins diverged")

    # ── Accept: flow: verify earns no quality warning ─────────────────────────────
    def test_flow_verify_is_warning_free(self):
        findings = [f for f in _persona_quality_warnings(_fm("flow: verify, advisor"))
                    if f.startswith("flow value")]
        self.assertEqual(findings, [], "flow: verify must be a valid routed value")

    # ── R: unknown value still warns, naming the 4-value set ─────────────────────
    def test_unknown_flow_still_warns_naming_verify(self):
        findings = [f for f in _persona_quality_warnings(_fm("flow: zzz"))
                    if f.startswith("flow value")]
        self.assertEqual(len(findings), 1)
        self.assertIn("design|build|advisor|verify", findings[0])

    # ── M2: the template flow hint teaches verify + four surfaces ─────────────────
    def test_template_hint_names_verify(self):
        text = TEMPLATE_TWINS[0].read_text(encoding="utf-8")
        self.assertIn("four apply-surfaces", text, "template must count FOUR apply-surfaces")
        self.assertIn("verify", text.split("use-when:")[0], "flow hint must name verify")
        self.assertEqual(len({_md5(p) for p in TEMPLATE_TWINS}), 1, "template twins diverged")

    # ── M3: the book chapter gains the fourth surface ─────────────────────────────
    def test_docs_four_surfaces(self):
        digests = set()
        for p in DOCS_TWINS:
            text = p.read_text(encoding="utf-8")
            self.assertIn("## Apply — four surfaces", text, f"{p} still counts three surfaces")
            self.assertIn("**verify", text, f"{p} missing the verify surface bullet")
            digests.add(_md5(p))
        self.assertEqual(len(digests), 1, "18-personas.md twins diverged")

    # ── M4: add-verify routes flow: verify first ──────────────────────────────────
    def test_add_verify_routes_verify_first(self):
        digests = set()
        for p in AGENT_TWINS:
            text = p.read_text(encoding="utf-8")
            self.assertIn("`flow: verify` persona first", text,
                          f"{p} must select flow: verify first")
            self.assertIn("flow: advisor", text, f"{p} must keep the advisor fallback")
            digests.add(_md5(p))
        self.assertEqual(len(digests), 1, "add-verify.md twins diverged")

    # ── M5: the verify guide names the flow; phases pool fence held ──────────────
    def test_verify_guide_names_flow(self):
        digests = set()
        for p in GUIDE_TWINS:
            self.assertIn("flow: verify", p.read_text(encoding="utf-8"),
                          f"{p} persona bullet must name flow: verify")
            digests.add(_md5(p))
        self.assertEqual(len(digests), 1, "6-verify.md trees diverged")

    def test_phases_pool_fence_held(self):
        pool = next(p for p in test_skill_lean.POOLS if p["name"] == "phases")
        self.assertLessEqual(test_skill_lean._pool_bytes(pool),
                             int(pool["baseline"] * pool["ratio"]),
                             "phases pool over its fence — compress 6-verify.md in-file")

    # ── M6: the reader exists — tdd-verifier declares the value ───────────────────
    def test_tdd_verifier_declares_verify(self):
        if not TDD_VERIFIER.exists():          # fresh-checkout tolerance (.add/personas is local)
            self.skipTest("dogfood persona absent on a fresh checkout")
        text = TDD_VERIFIER.read_text(encoding="utf-8")
        self.assertIn("flow: verify, advisor", text,
                      "tdd-verifier must adopt the new value (no dead wiring)")

    # ── pin honesty: add.py untouched by this task ────────────────────────────────
    def test_engine_addpy_untouched(self):
        digests = {_md5(p) for p in ADDPY_TRIO}
        self.assertEqual(len(digests), 1, "add.py trio diverged")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "add.py must not move in this task (constants-only engine change)")


if __name__ == "__main__":
    unittest.main()
