#!/usr/bin/env python3
"""trim-build-strategy-labels (milestone build-strategy-trim) — conformance suite for the
§3 Build-strategy relabel: `Scope (may touch)` is the HARD, tamper-guarded scope-lock; the
rest (Strategy · Approach · Regression floor · Persona) is SOFT/optional.

This is a static-surface conformance suite. It pins the ACHIEVED labels across the 4 PLAN.md.tmpl
twins + the engine's `_PLAN_FIELDS` recognizer, and the backward-compat fallback in `_build_plan`
that keeps already-frozen tasks (authored `Persona (required):`) surfacing their Persona.

Run: cd add-method/tooling && python3 -m unittest test_build_strategy_labels -v
"""
from __future__ import annotations

import hashlib
import importlib.util
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_PKG = _TOOLING.parent                        # add-method/
_REPO = _PKG.parent                           # AIDD-Book/

# the 4 PLAN.md.tmpl twins (canon · bundled git-tracked · two gitignored working twins)
TMPL_TWINS = (
    _PKG / "tooling" / "templates" / "PLAN.md.tmpl",
    _PKG / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "PLAN.md.tmpl",
    _REPO / ".add" / "tooling" / "templates" / "PLAN.md.tmpl",
    _PKG / ".add" / "tooling" / "templates" / "PLAN.md.tmpl",
)
CANON = TMPL_TWINS[0]
_REQUIRED = "Persona (" + "required)"          # split so this file never self-trips a grep


def _load_add():
    spec = importlib.util.spec_from_file_location("add_under_test", _TOOLING / "add.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TemplateLabels(unittest.TestCase):
    def test_persona_label_is_optional(self):                             # M2
        text = CANON.read_text(encoding="utf-8")
        self.assertIn("Persona (optional):", text, "§3 Persona label must read 'Persona (optional):'")
        self.assertNotIn(_REQUIRED + ":", text, "§3 must not keep the old 'Persona (required):' label")

    def test_scope_and_regression_prefixes_preserved(self):               # M3, R:scope_lock_prefix_lost
        text = CANON.read_text(encoding="utf-8")
        self.assertIn("Scope (may touch):", text, "the machine-read scope-lock prefix must survive verbatim")
        self.assertIn("Regression floor:", text, "the inherited-floors census prefix must survive verbatim")

    def test_header_marks_scope_hard(self):                               # M1
        header = next(ln for ln in CANON.read_text(encoding="utf-8").splitlines()
                      if ln.startswith("### Build-strategy"))
        low = header.lower()
        self.assertIn("scope (may touch)", low, "the §3 header must name Scope (may touch)")
        self.assertIn("hard", low, "the §3 header must mark Scope (may touch) as HARD scope-lock")

    def test_template_twins_byte_identical(self):                         # M5, R:twin_drift
        present = [t for t in TMPL_TWINS if t.exists()]
        digests = {hashlib.md5(t.read_bytes()).hexdigest() for t in present}
        self.assertEqual(len(digests), 1, f"PLAN.md.tmpl twins must be byte-identical, got {digests}")


class EngineRecognizer(unittest.TestCase):
    def test_engine_recognizes_optional(self):                           # M4
        add = _load_add()
        self.assertIn("Persona (optional)", add._PLAN_FIELDS,
                      "_PLAN_FIELDS must recognize the new 'Persona (optional)' label")

    def test_legacy_persona_still_surfaces(self):                        # M4 (backward-compat)
        add = _load_add()
        raw3 = ("### Build-strategy\n"
                "Scope (may touch): `add-method/tooling`\n"
                "Persona (" + "required): generic\n")   # a frozen legacy task's shape
        rows = add._build_plan(raw3)
        self.assertTrue(any("generic" == r["value"] for r in rows),
                        f"_build_plan must still surface a legacy 'Persona (required):' line, got {rows}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
