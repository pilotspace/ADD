"""fold-persona-sections (self-improving-loop): fold grows the CURRENT persona schema.

CONTRACT (frozen @ v1):
  `_PERSONA_FOLD_SECTIONS` gains `anti-pattern` -> `## Anti-patterns` and `ability` ->
  `## Abilities` — the 1.16.1 schema sections the persona learning loop could not grow
  (the same dead-wiring class flow: was). The fail-closed machinery is unchanged: an
  unknown hint or a persona missing the target section still dies
  `persona_section_unroutable` with nothing written; never-clobber holds. Every prose
  surface documenting the hint list names all four; add-verify/add-persona recommend
  persona-targeting a behavioral lesson. Engine x3 / skill x3 / book x4 / agent x3 parity.
Run: python3 -m unittest test_fold_persona_sections -v
"""
import contextlib
import hashlib
import io
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent

PERSONA = """---
name: Probe
vibe: probes the fold routing.
flow: advisor
---

## Identity
A probe persona.

## Abilities
- existing ability line.

## Critical Rules
- existing rule.

## Anti-patterns
- existing anti-pattern.

## Default Requirement
Probe everything.

## Success Metrics
- existing metric.
"""


class _FoldBase(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-fps-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._run("init", "--name", "demo", "--stage", "mvp")
        self._run("lock", "--force")
        self._run("new-task", "t", "--title", "T")
        (self.tmp / ".add" / "personas").mkdir(exist_ok=True)
        (self.tmp / ".add" / "personas" / "probe.md").write_text(PERSONA, encoding="utf-8")
        proj = self.tmp / ".add" / "PROJECT.md"
        s = proj.read_text(encoding="utf-8")
        if "foundation-version:" not in s:
            s = re.sub(r"(?m)^(slug:.*)$", r"\1 · foundation-version: 4", s, count=1)
            proj.write_text(s, encoding="utf-8")

    def _run(self, *argv, expect_die=False):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code or 0
        if expect_die:
            self.assertNotEqual(code, 0, f"{argv} unexpectedly succeeded: {buf.getvalue()}")
        else:
            self.assertEqual(code, 0, f"{argv} exited {code}: {err.getvalue()}")
        return buf.getvalue() + err.getvalue()

    def _plant(self, line):
        md = self.tmp / ".add" / "tasks" / "t" / "PLAN.md"
        t = md.read_text(encoding="utf-8")
        marker = "### Competency deltas\n"
        i = t.index(marker) + len(marker)
        j = t.index("\n", i) + 1                       # skip the grammar line
        md.write_text(t[:j] + line + "\n" + t[j:], encoding="utf-8")

    def _persona(self):
        return (self.tmp / ".add" / "personas" / "probe.md").read_text(encoding="utf-8")
class ProseNamesAllFour(unittest.TestCase):
    def test_guides_and_book(self):                                # M3
        # kernel-trim (ADD 2.0 M5): fold.md died — deltas.md is the grammar's one home
        deltas = (ADD_METHOD / "skill" / "add" / "deltas.md").read_text(encoding="utf-8")
        observe = (ADD_METHOD / "skill" / "add" / "phases" / "verify.md").read_text(encoding="utf-8")
        book = (ADD_METHOD / "docs" / "18-personas.md").read_text(encoding="utf-8")
        for hint in ("critical-rule", "success-metric", "anti-pattern", "ability"):
            self.assertIn(hint, deltas, f"deltas.md grammar misses {hint}")
        self.assertIn("anti-pattern", observe, "6-verify.md persona footnote misses the new hints (guide-recut moved it)")
        self.assertIn("Anti-patterns", book, "18-personas.md must name the grown sections")
        self.assertIn("Abilities", book)

    def test_agents_recommend_persona_tag(self):                   # M4
        # roster-distill (ADD 2.0 M1): the ONE `add` agent carries the recommendation
        text = (ADD_METHOD / "agents" / "add.md").read_text(encoding="utf-8")
        self.assertIn("persona:", text,
                      "the add agent must recommend persona-targeting behavioral lessons")


if __name__ == "__main__":
    unittest.main()
