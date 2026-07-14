#!/usr/bin/env python3
"""Red/green tests for template-touches-scope-dedup (call-residuals, frozen §3 v1):
the two TASK templates invited the SAME file list twice — §3 `Touches (files · symbols)`
and §5 `Scope (may touch)` — so agents authored the write-set twice (the duplication
scope-first-draft's own Grounding had to hand-fix this session). The dedup rewords the
placeholder VALUES so §3 Touches names symbols and points to §5 Scope as the write-set
owner, and §5 Scope declares itself the single source of truth. LABELS stay byte-frozen
(test_seams_template_wiring pins them); canonical==bundle stays byte-identical
(test_bundle_parity). This asserts the guidance text across BOTH tracked template trees.

Run: python3 -m unittest test_template_touches_scope_dedup -v
"""
import re
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent                       # add-method/tooling
_TREES = [
    _HERE / "templates",                                      # canonical
    _HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "templates",  # bundle
]
_FILES = ["TASK.md.tmpl", "TASK.fast.md.tmpl"]


def _line(text: str, label: str) -> str:
    for ln in text.splitlines():
        if ln.lstrip().startswith(label):
            return ln
    return ""


class TemplateDedupTest(unittest.TestCase):
    def _templates(self):
        for tree in _TREES:
            for name in _FILES:
                p = tree / name
                self.assertTrue(p.exists(), f"missing template: {p}")
                yield p, p.read_text(encoding="utf-8")

    def test_touches_points_to_scope_as_write_set_owner(self):
        # §3 Touches placeholder must tell the agent NOT to re-list files, → §5 Scope owns it.
        for p, text in self._templates():
            touches = _line(text, "Touches (files")
            self.assertIn("not the full file list", touches,
                          f"{p}: §3 Touches must say 'not the full file list'")
            self.assertRegex(touches, r"§5 Scope",
                             f"{p}: §3 Touches must point to §5 Scope as the write-set owner")

    def test_scope_declares_single_source_of_truth(self):
        # §5 Scope placeholder must declare itself the one owner of the file write-set.
        for p, text in self._templates():
            scope = _line(text, "Scope (may touch):")
            self.assertIn("single source of truth", scope,
                          f"{p}: §5 Scope must declare 'single source of truth' for the write-set")

    def test_labels_and_src_token_byte_unchanged(self):
        # the dedup rewords ONLY the <…> value — labels + the ./src/ default stay frozen.
        for p, text in self._templates():
            touches = _line(text, "Touches (files")
            self.assertRegex(touches, r"^Touches \(files · symbols(?: · signatures)?\): ",
                             f"{p}: Touches LABEL must be byte-unchanged")
            scope = _line(text, "Scope (may touch):")
            self.assertIn("`./src/`", scope, f"{p}: §5 Scope must keep the ./src/ default token")

    def test_canonical_and_bundle_byte_identical(self):
        for name in _FILES:
            canon = (_TREES[0] / name).read_text(encoding="utf-8")
            bundle = (_TREES[1] / name).read_text(encoding="utf-8")
            self.assertEqual(canon, bundle, f"{name}: canonical and bundle template must be byte-identical")


if __name__ == "__main__":
    unittest.main()
