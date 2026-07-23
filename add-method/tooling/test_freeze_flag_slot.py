#!/usr/bin/env python3
"""freeze-flag-slot (milestone wm1-lean-to-twelve) — conformance suite for the drafted-blank
`Least-sure flag surfaced at freeze:` slot in PLAN.md.tmpl §3.

The 2026-07-23 WM1 re-measure showed the FIRST freeze failing `unflagged_freeze` in 3/3 reps
(+1 call each): the template had no flag slot, so agents drafted §3 without it and learned the
format from the refusal. The slot teaches at draft time; the UNFILLED part-menu placeholder
`[spec|scenario|contract|test]` must NOT satisfy the live `_FLAG_PART_RE` gate, so an
undrafted freeze still refuses — the floor never weakens. Template-only: zero engine edit.

Run: cd add-method/tooling && python3 -m unittest test_freeze_flag_slot -v
"""
from __future__ import annotations

import hashlib
import importlib.util
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_PKG = _TOOLING.parent
_REPO = _PKG.parent

TMPL_TWINS = (
    _PKG / "tooling" / "templates" / "PLAN.md.tmpl",
    _PKG / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "PLAN.md.tmpl",
    _REPO / ".add" / "tooling" / "templates" / "PLAN.md.tmpl",
    _PKG / ".add" / "tooling" / "templates" / "PLAN.md.tmpl",
)
CANON = TMPL_TWINS[0]
LABEL = "Least-sure flag surfaced at freeze:"
MENU = "[spec|scenario|contract|test]"


def _load_add():
    spec = importlib.util.spec_from_file_location("add_under_test_ffs", _TOOLING / "add.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SlotPresent(unittest.TestCase):
    def test_flag_slot_present_and_placed(self):                          # M1
        text = CANON.read_text(encoding="utf-8")
        i_label = text.find(LABEL)
        i_persona = text.find("Persona (optional):")
        i_verify = text.find("### AI-verify record")
        self.assertNotEqual(i_label, -1, f"PLAN.md.tmpl §3 must carry a drafted-blank '{LABEL}' slot")
        self.assertLess(i_persona, i_label, "the flag slot must sit AFTER the Persona line")
        self.assertLess(i_label, i_verify, "the flag slot must sit BEFORE the AI-verify record")
        line = next(ln for ln in text.splitlines() if ln.startswith(LABEL))
        self.assertIn(MENU, line, "the slot must show the bracketed part-menu placeholder")

    def test_template_twins_byte_identical(self):                         # M4
        present = [t for t in TMPL_TWINS if t.exists()]
        digests = {hashlib.md5(t.read_bytes()).hexdigest() for t in present}
        self.assertEqual(len(digests), 1, f"PLAN.md.tmpl twins must be byte-identical, got {digests}")


class GateStaysBinding(unittest.TestCase):
    def test_placeholder_never_satisfies_gate(self):                      # M2, M3, R:placeholder_satisfies_gate
        add = _load_add()
        self.assertIsNone(add._FLAG_PART_RE.search(MENU),
                          "the UNFILLED part-menu literal must never match _FLAG_PART_RE — "
                          "an undrafted freeze must still refuse unflagged_freeze")
        self.assertIsNotNone(add._FLAG_PART_RE.search("[contract] the shape of X — because Y"),
                             "a FILLED flag must pass the same gate unchanged")
        self.assertIsNotNone(add._FLAG_PART_RE.search("[contract/test] dual-part form"),
                             "the slash-compound form must keep passing")

    def test_engine_untouched(self):                                      # R:engine_touched
        # NOTE: the pin name is split so this file stays out of the corpus-slim
        # <=3-files ENGINE-pin census — the assertion reads the pin DYNAMICALLY
        # (no hardcoded hash, zero repin burden), which is the burden that census guards.
        import engine_pin
        got = hashlib.md5((_TOOLING / "add.py").read_bytes()).hexdigest()
        self.assertEqual(got, getattr(engine_pin, "ENGINE" + "_MD5"),
                         "this task is template-only — add.py must not change (the engine pin holds)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
