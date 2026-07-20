#!/usr/bin/env python3
"""Doc-grep tests for the security-escalation honesty disclosure
(flow-honesty milestone, task `security-escalation-disclosure`, M1).

CONTRACT (frozen @ v1) — doc-only, no engine change:
  run.md + phases/verify.md must DISCLOSE that the engine cannot detect a MISSED security
  finding: `unescalated_security_note` only catches a MARKED note (NOTE/⚠) that was auto-gated,
  so under `auto` a human SPOT-AUDIT is the only backstop for a finding never marked. The standing
  "a security finding is always HARD-STOP" guarantee stays VERBATIM. add.py byte-identical
  (ENGINE_MD5 unchanged). The disclosure lands byte-identically across the 3 skill trees.

Reject labels: missing_disclosure_verify · missing_disclosure_run · guarantee_weakened · skill_tree_drift
One test per scenario. Run: python3 -m unittest test_security_escalation_disclosure -v
"""
import hashlib
import re
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
PKG_ROOT = TOOLING.parent          # add-method/
REPO_ROOT = PKG_ROOT.parent        # repo root

SKILL_TREES = [
    PKG_ROOT / "skill" / "add",                                       # canonical
    REPO_ROOT / ".claude" / "skills" / "add",                         # installed (dogfood)
    PKG_ROOT / "src" / "add_method" / "_bundled" / "skill" / "add",   # bundled (shipped)
]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


class SecurityEscalationDisclosureTest(unittest.TestCase):
    def _each(self, rel):
        return [(t, _read(t / rel)) for t in SKILL_TREES]

    def test_verify_guide_discloses_missed_finding(self):       # Must + missing_disclosure_verify
        for tree, text in self._each("phases/verify.md"):
            low = text.lower()
            self.assertIn("spot-audit", low,
                          f"missing_disclosure_verify: no spot-audit backstop in {tree}")
            # Anchor the blind-spot assertion on a DISCLOSURE-UNIQUE phrase (pin the line, not a
            # keyword): bare "invisible" also matches the unrelated earned-green line ("invisible to
            # the mechanical tamper tripwire") — "never marked"/"wrote down" appear ONLY in the
            # disclosure, so stripping the blind-spot sentence now fails this assertion too.
            self.assertTrue(re.search(r"never marked|wrote down", low),
                            f"missing_disclosure_verify: no missed-finding blind spot in {tree}")

    def test_run_guide_qualifies_always_escalates(self):        # Must + missing_disclosure_run
        for tree, text in self._each("run.md"):
            low = text.lower()
            self.assertIn("spot-audit", low,
                          f"missing_disclosure_run: no spot-audit backstop in {tree}")
            self.assertTrue(re.search(r"surfaces?|miss(ed|es)|invisible", low),
                            f"missing_disclosure_run: no if-surfaced qualifier in {tree}")

    def test_guarantee_not_weakened(self):                      # guarantee_weakened
        for tree in SKILL_TREES:
            v = _read(tree / "phases/verify.md")
            self.assertIn("always `HARD-STOP`", v,
                          f"guarantee_weakened: 6-verify dropped 'always HARD-STOP' in {tree}")
            r = _read(tree / "run.md")
            self.assertIn("Security still always escalates", r,
                          f"guarantee_weakened: run.md dropped the escalation guarantee in {tree}")

    def test_skill_trees_byte_identical_for_both_guides(self):  # skill_tree_drift
        for rel in ("run.md", "phases/verify.md"):
            md5s = {hashlib.md5(_read(t / rel).encode("utf-8")).hexdigest() for t in SKILL_TREES}
            self.assertEqual(len(md5s), 1,
                             f"skill_tree_drift: {rel} differs across the 3 skill trees")

    def test_engine_untouched(self):                            # doc-only: add.py byte-identical
        import engine_pin
        got = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(got, engine_pin.ENGINE_MD5,
                         "doc-only task must not touch the engine (add.py byte-identical)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
