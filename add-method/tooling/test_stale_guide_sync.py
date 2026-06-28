#!/usr/bin/env python3
"""Red/green tests for stale-guide-sync (milestone flow-honesty, task 7/7, M5).

CONTRACT (frozen @ v1) — PROSE-ONLY, engine BYTE-FROZEN:
  - 5-build.md + TASK.md.tmpl: the stale `scope-gate-enforce` deferral is GONE; the gate is
    described as ENFORCED at the verify gate (scope_violation -> self-heal).
  - run.md owns the ONE canonical 8-item auto-PASS precondition list; book ch.08 names the SAME
    items (adds completeness-critic + deep-check + recorded refute-read); 6-verify points to run.md.
  - run.md + 6-verify.md note `add.py audit` surfaces shallow_deep_check + risk_unset + refute_unrecorded.
  - book ch.08 carries the never-marked-security-finding disclosure (book<->skill parity).
  - book ch.03/04 cross-ref the TASK.md §1/§2 they fill.
  - ENGINE_MD5 + ENGINE_PKG_MD5 byte-UNCHANGED; edited files byte-identical across mirror trees.
Run: python3 -m unittest test_stale_guide_sync -v
"""
import hashlib
import re
import unittest
from pathlib import Path

import add

TOOLING = Path(add.__file__).resolve().parent
ADD_METHOD = TOOLING.parent
REPO = ADD_METHOD.parent
SKILL = ADD_METHOD / "skill" / "add"
DOCS = ADD_METHOD / "docs"
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"

BUILD_MD = SKILL / "phases" / "5-build.md"
RUN_MD = SKILL / "run.md"
VERIFY_MD = SKILL / "phases" / "6-verify.md"
TMPL = TOOLING / "templates" / "TASK.md.tmpl"
CH03 = DOCS / "03-step-1-specify.md"
CH04 = DOCS / "04-step-2-scenarios.md"
CH08 = DOCS / "08-step-6-verify.md"
PIN = TOOLING / "engine_pin.py"

STALE_TOKENS = ("scope-gate-enforce", "until it ships", "prose discipline")


def _read(p):
    return p.read_text(encoding="utf-8")


class StaleNoteGoneTest(unittest.TestCase):
    def test_no_stale_scope_gate_deferral(self):
        for p in (BUILD_MD, TMPL):
            text = _read(p)
            for tok in STALE_TOKENS:
                self.assertNotIn(tok, text, f"{p.name}: stale token {tok!r} must be gone")
            self.assertTrue(
                "scope_violation" in text or "enforced at the verify gate" in text,
                f"{p.name}: must describe the scope gate as ENFORCED")


class CanonicalPreconditionsTest(unittest.TestCase):
    CANON = ["test", "coverage", "loops dry", "completeness-critic",
             "deep check", "refute-read", "residue"]

    def test_run_md_canonical_preconditions(self):
        text = _read(RUN_MD).lower()
        for item in [c.lower() for c in self.CANON]:
            self.assertIn(item, text, f"run.md canonical list missing: {item!r}")

    def test_book_ch08_names_same_set(self):
        text = _read(CH08).lower()
        for item in ("completeness-critic", "deep check", "refute-read"):
            self.assertIn(item, text, f"book ch.08 must name the canonical item: {item!r}")

    def test_6verify_points_to_canonical(self):
        # the 6-verify autonomy blockquote must point at run.md as the canonical list
        head = _read(VERIFY_MD).split("## Part one", 1)[0]
        self.assertIn("run.md", head, "6-verify autonomy blockquote must point to run.md")


class AuditAndDisclosureTest(unittest.TestCase):
    def test_audit_surfaces_lints_noted(self):
        for p in (RUN_MD, VERIFY_MD):
            text = _read(p)
            for lint in ("shallow_deep_check", "risk_unset", "refute_unrecorded"):
                self.assertIn(lint, text,
                              f"{p.name} must note add.py audit surfaces {lint}")

    def test_book_missed_finding_disclosure(self):
        text = _read(CH08)
        self.assertIn("unescalated_security_note", text,
                      "book ch.08 must name the unescalated_security_note blind spot")
        self.assertTrue("never marked" in text or "never wrote" in text,
                        "book ch.08 must disclose a never-marked finding is invisible")
        self.assertIn("spot-audit", text)


class BookCrossRefTest(unittest.TestCase):
    def test_book_chapters_crossref_task(self):
        c3 = _read(CH03)
        self.assertIn("TASK.md", c3)
        self.assertIn("§1", c3)
        c4 = _read(CH04)
        self.assertIn("TASK.md", c4)
        self.assertIn("§2", c4)


class EngineFrozenTest(unittest.TestCase):
    def test_engine_byte_unchanged(self):
        pin = _read(PIN)
        declared = re.search(r'ENGINE_MD5 = "([0-9a-f]{32})"', pin).group(1)
        actual = hashlib.md5((TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(actual, declared,
                         "prose-only task: add.py must match ENGINE_MD5 (no engine change)")

    def test_security_guarantee_intact(self):
        self.assertIn("always a HARD-STOP and is never auto-passed", _read(VERIFY_MD))
        self.assertIn("HARD-STOP", _read(CH08))


class ParityTest(unittest.TestCase):
    CASES = [
        (SKILL / "phases" / "5-build.md", REPO / ".claude/skills/add/phases/5-build.md",
         BUNDLE / "skill/add/phases/5-build.md"),
        (RUN_MD, REPO / ".claude/skills/add/run.md", BUNDLE / "skill/add/run.md"),
        (VERIFY_MD, REPO / ".claude/skills/add/phases/6-verify.md",
         BUNDLE / "skill/add/phases/6-verify.md"),
        (CH08, REPO / "08-step-6-verify.md", BUNDLE / "docs/08-step-6-verify.md"),
        (CH03, REPO / "03-step-1-specify.md", BUNDLE / "docs/03-step-1-specify.md"),
        (CH04, REPO / "04-step-2-scenarios.md", BUNDLE / "docs/04-step-2-scenarios.md"),
    ]

    def test_three_tree_parity_holds(self):
        for canon, *mirrors in self.CASES:
            cb = canon.read_bytes()
            for m in mirrors:
                self.assertEqual(cb, m.read_bytes(), f"mirror drift: {m}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
