#!/usr/bin/env python3
"""strategy-section (milestone strategy-intake) — conformance suite for the drafted-blank
`## Strategy` slot in MILESTONE.md.tmpl.

The milestone template gains ONE section, `## Strategy`, inserted BETWEEN `## Exit criteria`
and `## Close — ship review`. It is drafted-blank (placeholder `<...>` slots like `## Close` /
`## Release steps`), SOFT/advisory, and NEVER parsed or gated by the engine. Placement after
`## Exit criteria` keeps it out of the `## Tasks` DAG-parse span (R2), so the task graph is
byte-behaviour-unchanged. All template twins stay byte-identical (M4).

Run: cd add-method/tooling && python3 -m unittest test_strategy_section -v
"""
from __future__ import annotations

import hashlib
import importlib.util
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_PKG = _TOOLING.parent                        # add-method/
_REPO = _PKG.parent                           # AIDD-Book/

TMPL_TWINS = tuple(t for t in (
    _PKG / "tooling" / "templates" / "MILESTONE.md.tmpl",
    _PKG / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "MILESTONE.md.tmpl",
    _REPO / ".add" / "tooling" / "templates" / "MILESTONE.md.tmpl",
    _PKG / ".add" / "tooling" / "templates" / "MILESTONE.md.tmpl",
) if True)
CANON = TMPL_TWINS[0]


def _load_add():
    spec = importlib.util.spec_from_file_location("add_under_test_ss", _TOOLING / "add.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TemplateSlot(unittest.TestCase):
    def test_strategy_slot_present_and_placed(self):                      # M1, M2 (renders verbatim)
        text = CANON.read_text(encoding="utf-8")
        i_strat = text.find("## Strategy")
        i_exit = text.find("## Exit criteria")
        i_close = text.find("## Close")
        self.assertNotEqual(i_strat, -1, "MILESTONE.md.tmpl must carry a `## Strategy` section")
        self.assertNotEqual(i_exit, -1, "template must still have `## Exit criteria`")
        self.assertNotEqual(i_close, -1, "template must still have `## Close`")
        self.assertLess(i_exit, i_strat, "`## Strategy` must be placed AFTER `## Exit criteria`")
        self.assertLess(i_strat, i_close, "`## Strategy` must be placed BEFORE `## Close`")

    def test_strategy_is_drafted_blank(self):                             # R1 (soft, not required)
        text = CANON.read_text(encoding="utf-8")
        block = text[text.find("## Strategy"):text.find("## Close")]
        self.assertIn("<", block, "the `## Strategy` slot must be drafted-blank (placeholder `<...>` slots)")

    def test_twins_byte_identical(self):                                  # M4
        present = [t for t in TMPL_TWINS if t.exists()]
        digests = {hashlib.md5(t.read_bytes()).hexdigest() for t in present}
        self.assertEqual(len(digests), 1, f"MILESTONE.md.tmpl twins must be byte-identical, got {digests}")


class TasksParseUnchanged(unittest.TestCase):
    def test_tasks_dag_ignores_strategy(self):                            # M3, R2
        add = _load_add()
        md = (
            "## Tasks (breadth-first)\n"
            "- [ ] alpha   depends-on: none   — the first slice\n"
            "- [ ] beta   depends-on: alpha   — builds on alpha\n"
            "\n## Exit criteria (observable)\n"
            "- [ ] User can X   (← alpha)\n"
            "\n## Strategy   (AI-drafted WITH the human)\n"
            "- Approach (sequencing): <risk-first — and WHY>\n"
            "- Waves (parallel): <slugs — or sequential>\n"
            "\n## Close — ship review\n"
        )
        graph = add._compile_task_graph(md)
        self.assertEqual(set(graph), {"alpha", "beta"},
                         f"the `## Tasks` DAG must read exactly the 2 task rows, not a Strategy line; got {graph}")
        self.assertEqual(graph["beta"], ["alpha"], "the depends-on edge must survive the Strategy insertion")

    def test_engine_never_parses_strategy(self):                          # R1 (stays soft — no engine consumer)
        add_py = (_TOOLING / "add.py").read_text(encoding="utf-8")
        self.assertNotIn('"## Strategy"', add_py,
                         "the engine must not key on a `## Strategy` literal — the section renders verbatim, never gated")
        self.assertNotIn("strategy_must_stay_soft", add_py,
                         "no reject code should exist — a drafted-blank Strategy is simply valid, never held")


if __name__ == "__main__":
    unittest.main(verbosity=2)
