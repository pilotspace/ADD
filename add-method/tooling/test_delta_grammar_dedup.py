#!/usr/bin/env python3
"""Behavioral proof of the delta-grammar dedup (task: delta-grammar-dedup, v12-1).

CONTRACT (frozen @ v1): the enumerated delta grammar
  (DDD|SDD|UDD|TDD|ADD) · (open|folded|rejected)
is compiled EXACTLY ONCE in add.py (the module-level `_DELTA_RE`), reused by
`_task_prose`, `_collect_open_deltas`, and `_lint_task_deltas`. The canonical
regex stays PERMISSIVE (leading whitespace tolerated) because `_task_prose`
feeds it un-stripped lines. Behaviour of report/`deltas`/lint is unchanged.

RED driver: test_one_canonical_delta_grammar_source (2 copies exist today).
The other two are the behaviour-preserving safety net (green now AND after).
Run: python3 -m unittest test_delta_grammar_dedup -v
"""
import inspect
import os
import re
import tempfile
import shutil
import unittest
from pathlib import Path

import add


# Source-level count of compiled regexes that enumerate the competency alternation.
# _TAG_BROAD_RE uses [^]·]+ (no enumeration) so it is correctly NOT counted.
_ENUM = re.compile(r"\(DDD\|SDD\|UDD\|TDD\|ADD\)")


def _add_source() -> str:
    return Path(inspect.getfile(add)).read_text(encoding="utf-8")


class DeltaGrammarDedupTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-delta-dedup-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    def _write_task_observe(self, slug, *observe_lines):
        """Create task `slug` and replace its §7 OBSERVE delta block with `observe_lines`."""
        if slug not in (add.load_state(add.find_root()).get("tasks") or {}):
            add.main(["new-task", slug, "--title", "Feature"])
        p = Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"
        text = p.read_text(encoding="utf-8")
        marker = "### Competency deltas"
        idx = text.index(marker) + len(marker)
        p.write_text(text[:idx] + "\n" + "\n".join(observe_lines) + "\n", encoding="utf-8")

    # --- RED driver: one canonical source -----------------------------------
    def test_one_canonical_delta_grammar_source(self):
        """Exactly one compiled regex enumerates the competency grammar."""
        src = _add_source()
        # Count only lines that BOTH enumerate the grammar AND are a compiled-regex literal
        # (a pattern string). The canonical lives in a re.compile(...) call.
        hits = [ln for ln in src.splitlines() if _ENUM.search(ln)]
        self.assertEqual(
            len(hits), 1,
            "the enumerated delta grammar must be compiled exactly ONCE "
            f"(found {len(hits)} copies):\n  " + "\n  ".join(hits),
        )

    # --- safety net 1: indented tag line still recognised by the report path -
    def test_task_prose_recognizes_indented_tag_line(self):
        """_task_prose must still parse an INDENTED delta tag line (permissive match)."""
        self._write_task_observe(
            "a",
            "    - [DDD · open] indented learning text (evidence: ev1)",
        )
        _observe, deltas = add._task_prose(add.find_root(), "a")
        self.assertTrue(deltas, "an indented tag line was dropped — canonical not permissive")
        self.assertIn("DDD", deltas[0])
        self.assertIn("open", deltas[0])
        self.assertIn("indented learning text", deltas[0])

    # --- safety net 2: both delta paths agree on the grammar -----------------
    def test_both_delta_paths_agree(self):
        """The report path (_task_prose) and the deltas path (_collect_open_deltas)
        recognise the SAME valid open delta as a delta-start, and a malformed tag is
        a delta-start in NEITHER. (Scoped to grammar recognition — the two paths'
        continuation-termination logic differs by design and is out of this task's scope,
        so the malformed line is blank-separated to isolate grammar from continuation.)"""
        self._write_task_observe(
            "b",
            "- [SDD · open] valid stripped tag (evidence: e1)",
            "",                               # blank: terminates the entry in BOTH paths
            "- [BOGUS] not a delta at all",   # malformed: a delta-start in NEITHER path
        )
        root = add.find_root()
        _observe, prose_deltas = add._task_prose(root, "b")
        by_comp = add._collect_open_deltas(root)
        # report path: exactly one valid open delta; bogus not recognised as its own delta
        self.assertEqual(len(prose_deltas), 1, "report path miscounted valid deltas")
        self.assertIn("valid stripped tag", prose_deltas[0])
        self.assertNotIn("BOGUS", " ".join(prose_deltas))
        # deltas path agrees: one SDD open entry, bogus excluded
        self.assertEqual(sum(len(v) for v in by_comp.values()), 1, "deltas path miscounted")
        self.assertEqual(by_comp["SDD"][0]["text"], "valid stripped tag")


if __name__ == "__main__":
    unittest.main(verbosity=2)
