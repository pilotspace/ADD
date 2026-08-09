"""Red→green guard for close-section-template §3 (FROZEN @ v1).

The MILESTONE template gains two AI-filled close sections AFTER `## Exit criteria`:
`## Close — ship review` (ship-by-domain {tooling,skill,book} + a cross-task evidence row +
a goal-met map) and `## Release steps` (AI-defined hints; merge is one small step; an export
hint). The frozen seam is a TOKEN SET + 5 structural invariants — engine logic UNCHANGED.

RED drivers (fail until the template gains the two sections, then green):
  test_S1_S2_close_section_renders_three_domains ·
  test_S3_release_steps_merge_and_export_hint ·
  test_S4_release_checkbox_excluded_from_goal_tally ·
  test_S5_template_tree_parity_includes_new_sections
DISCLOSED green-at-red guard (green now, MUST stay green — no scan target until built):
  test_no_engine_outward_act (add.py gains no `gh pr create` / docx shell-out).

unittest (repo convention). Run: python3 -m unittest discover -s tests
"""
import hashlib
import importlib.util
import os
import re
import tempfile
import unittest
from pathlib import Path

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

_CANON_TMPL = os.path.join(_ROOT, "add-method/tooling/templates/MILESTONE.md.tmpl")
_TMPL_COPIES = [
    os.path.join(_ROOT, "add-method/tooling/templates/MILESTONE.md.tmpl"),
    os.path.join(_ROOT, "add-method/src/add_method/_bundled/tooling/templates/MILESTONE.md.tmpl"),
    os.path.join(_ROOT, ".add/tooling/templates/MILESTONE.md.tmpl"),
]
_ENGINE = os.path.join(_ROOT, "add-method/tooling/add.py")

_CLOSE = "## Close — ship review"
_RELEASE = "## Release steps"
_EXIT = "## Exit criteria"


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _tmpl():
    return _read(_CANON_TMPL)


def _section(text, heading):
    """Slice from `heading` to the next '## ' heading or EOF — the engine's own bound."""
    m = re.search(re.escape(heading) + r".*?(?=\n## |\Z)", text, re.S)
    return m.group(0) if m else ""


def _load_engine():
    spec = importlib.util.spec_from_file_location("add_engine_cst", _ENGINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CloseSectionTemplate(unittest.TestCase):

    # S1 order + S2 close content ------------------------------------------
    def test_S1_S2_close_section_renders_three_domains(self):
        t = _tmpl()
        self.assertIn(_CLOSE, t, "template missing the Close — ship review section")
        self.assertIn(_RELEASE, t, "template missing the Release steps section")
        # S1: Exit criteria < Close < Release
        self.assertLess(t.index(_EXIT), t.index(_CLOSE), "Close must come AFTER Exit criteria")
        self.assertLess(t.index(_CLOSE), t.index(_RELEASE), "Release steps must come after Close")
        # S2: the three bounded contexts + a cross-task evidence row + a goal-met map
        close = _section(t, _CLOSE)
        for dom in ("tooling", "skill", "book"):
            self.assertIn(dom, close, f"Close section must name the {dom} domain")
        self.assertRegex(close, r"gate=.*tests=.*residue=",
                         "Close section needs a cross-task evidence row shape")
        self.assertIn("Exit criteria", close,
                      "Close section needs a goal-met map referencing Exit criteria")

    # S3 release-steps content ---------------------------------------------
    def test_S3_release_steps_merge_and_export_hint(self):
        rel = _section(_tmpl(), _RELEASE)
        self.assertIn("- [ ]", rel, "Release steps must be ordered checkbox hints")
        self.assertIn("merge", rel.lower(), "Release steps must name merge as one step")
        self.assertRegex(rel.lower(), r"docx|pandoc|export",
                         "Release steps must carry a portable-doc export hint")

    # S4 tally exclusion (the lowest-confidence invariant) -----------------
    def test_S4_release_checkbox_excluded_from_goal_tally(self):
        eng = _load_engine()
        t = _tmpl()
        with tempfile.TemporaryDirectory() as d:
            mdir = os.path.join(d, "milestones", "demo")
            os.makedirs(mdir)
            with open(os.path.join(mdir, "MILESTONE.md"), "w", encoding="utf-8") as fh:
                fh.write(t)
            _, total = eng._exit_criteria(Path(d), "demo")
            _, ctotal = eng._exit_criteria_cited(Path(d), "demo")
        exit_boxes = len(re.findall(r"- \[[ x]\]", _section(t, _EXIT)))
        new_boxes = (len(re.findall(r"- \[[ x]\]", _section(t, _CLOSE)))
                     + len(re.findall(r"- \[[ x]\]", _section(t, _RELEASE))))
        # the new sections carry their OWN checkboxes (red until they exist)
        self.assertGreaterEqual(new_boxes, 1,
                                "Close/Release must carry checkboxes of their own")
        # ...yet the goal tally counts the Exit-criteria slice ALONE — the new ones are excluded
        self.assertEqual(total, exit_boxes, "goal tally must count Exit criteria alone")
        self.assertEqual(ctotal, exit_boxes, "cited tally must count Exit criteria alone")

    # S5 three-tree parity, including the new content ----------------------
    def test_S5_template_tree_parity_includes_new_sections(self):
        digests = set()
        for p in _TMPL_COPIES:
            self.assertTrue(os.path.exists(p), f"missing template copy: {p}")
            txt = _read(p)
            self.assertIn(_CLOSE, txt, f"{p} missing the Close section")
            self.assertIn(_RELEASE, txt, f"{p} missing the Release steps section")
            digests.add(hashlib.md5(txt.encode("utf-8")).hexdigest())
        self.assertEqual(len(digests), 1, "the three template copies diverged (tree_drift)")

    # DISCLOSED green-at-red guard: engine never performs the outward act ---
    def test_no_engine_outward_act(self):
        src = _read(_ENGINE)
        self.assertNotIn("gh pr create", src, "engine must not perform the PR (engine_performs_outward_act)")
        self.assertNotRegex(src, r"import\s+docx|python-docx",
                            "engine must not render docx (engine_performs_outward_act)")


if __name__ == "__main__":
    unittest.main()
