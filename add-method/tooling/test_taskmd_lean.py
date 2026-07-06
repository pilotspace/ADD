"""task-md-optimize (method-ergonomics): the TASK.md template stays lean.

CONTRACT — comment-bloat ceiling, machine-parsed markers untouched:
  templates/TASK.md.tmpl total size <= 10600 B and its HTML-comment volume <= 2500 B (UTF-8 bytes);
  the pinned anchors survive verbatim: `risk: high` (test_high_risk_signal) · the §4 grammar
  anchor + forms (test_declare_grammar_doc) · §3 keeps EXACTLY ONE merged comment
  (test_template_form_tags) · every `### ` §6 block heading and machine-read line
  (`Status:` · `Reported:` · `Scope (may touch):` · `Tests live in:`) stays;
  all template trees stay byte-identical.
Run: python3 -m unittest test_taskmd_lean -v
"""
import re
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
ADD_METHOD = TOOLING.parent
REPO = ADD_METHOD.parent
CANON = TOOLING / "templates" / "TASK.md.tmpl"
TREES = (CANON,
         REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
         ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.md.tmpl")

SIZE_CEILING = 10600      # UTF-8 bytes (pre-task: 12442)
COMMENT_CEILING = 2500   # UTF-8 bytes of HTML comments (pre-task: 3418)


class LeanTemplateTest(unittest.TestCase):
    def setUp(self):
        self.text = CANON.read_text(encoding="utf-8")

    def test_size_ceiling(self):
        self.assertLessEqual(len(self.text.encode("utf-8")), SIZE_CEILING,
                             f"TASK.md.tmpl is {len(self.text.encode('utf-8'))}B; frozen ceiling {SIZE_CEILING}B")

    def test_comment_volume_ceiling(self):
        vol = sum(len(c.encode("utf-8")) for c in re.findall(r"<!--.*?-->", self.text, re.S))
        self.assertLessEqual(vol, COMMENT_CEILING,
                             f"comment volume {vol}B exceeds the {COMMENT_CEILING}B ceiling")

    def test_pinned_anchors_survive(self):
        for anchor in ("risk: high", "declare paths as backticked tokens",
                       "Status: DRAFT", "Scope (may touch):", "Tests live in:",
                       "### Build expectations", "### Deep checks", "### Live-verify evidence",
                       "### Refute-read verdict", "### Advisor 3-lens verdict", "### GATE RECORD",
                       "### Decisions (ADR)", "### Spec delta", "### Competency deltas",
                       "Persona (required):"):   # (flag line lives in TASK.fast + agent-added §3, not here)
            self.assertIn(anchor, self.text, f"machine-read anchor lost: {anchor}")

    def test_sec3_single_comment(self):
        sec3 = self.text.split("## 3 · CONTRACT")[1].split("## 4 · TESTS")[0]
        self.assertEqual(1, sec3.count("<!--"), "§3 keeps exactly ONE merged comment")

    def test_trees_byte_identical(self):
        ref = CANON.read_bytes()
        for p in TREES[1:]:
            self.assertEqual(ref, p.read_bytes(), f"template tree drift: {p}")


if __name__ == "__main__":
    unittest.main()
