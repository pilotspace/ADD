#!/usr/bin/env python3
"""Behavioral proof of `add.py fold`'s Glossary-delta extension (task: fold-glossary-deltas).
CONTRACT frozen @ v1.

Extends `cmd_fold` with a 6th pseudo-competency `GLOSSARY`: a DONE task's clean, unfolded
`Glossary deltas: <term>: <definition>` line consolidates into `.add/GLOSSARY.md` (unstamped,
matching that file's own existing convention) while the task's OWN line gets
` [folded foundation-version N]` appended — sharing the SAME atomic multi-file write + ONE
version bump as any competency deltas folded in the same run. A line that doesn't cleanly
parse as `<term>: <definition>` is silently skipped (never guessed at), but the skip is
COUNTED and reported in `fold`'s own printed summary.

Run: python3 -m unittest test_fold_glossary -v
"""
from __future__ import annotations

import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = None
    with redirect_stdout(out), redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
    return out.getvalue(), err.getvalue(), code


def _snapshot(base):
    return {str(p.relative_to(base)): p.read_bytes()
            for p in sorted(base.rglob("*")) if p.is_file()}


class FoldGlossaryTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-fold-glossary-")
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        self.root = Path(self.tmp) / ".add"
        self.project = self.root / "PROJECT.md"
        self.conventions = self.root / "CONVENTIONS.md"
        self.glossary = self.root / "GLOSSARY.md"
        if not self.glossary.exists():
            self.glossary.write_text("# GLOSSARY\n\nState: the resume point.\n", encoding="utf-8")

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- helpers -------------------------------------------------------------
    def _new_task(self, slug):
        add.main(["new-task", slug])

    def _mark_done(self, slug):
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        s = re.sub(r"(?m)^phase:.*$", "phase: done", s, count=1)
        p.write_text(s, encoding="utf-8")

    def _plant_glossary(self, slug, text):
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        s = re.sub(r"(?m)^Glossary deltas:.*$", f"Glossary deltas: {text}", s, count=1)
        p.write_text(s, encoding="utf-8")

    def _plant_glossary_with_flag(self, slug, glossary_text, flag_text):
        """Plant a Glossary-deltas line immediately followed by a `Least-sure flag surfaced at
        freeze:` line — the REAL shape every frozen task carries (freeze inserts that hyphenated
        label right after `Glossary deltas:`, before `Status: FROZEN...`), unlike `_plant_glossary`
        alone which leaves the fresh-task template's `Status: DRAFT` immediately after instead."""
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        s = re.sub(r"(?m)^Glossary deltas:.*$",
                    f"Glossary deltas: {glossary_text}\nLeast-sure flag surfaced at freeze: {flag_text}",
                    s, count=1)
        p.write_text(s, encoding="utf-8")

    def _plant_comp(self, slug, tag, text, ev="e"):
        p = self.root / "tasks" / slug / "TASK.md"
        s = p.read_text(encoding="utf-8")
        i = s.index("### Competency deltas") + len("### Competency deltas")
        p.write_text(s[:i] + f"\n- [{tag} · open] {text} (evidence: {ev})\n" + s[i:],
                     encoding="utf-8")

    def _set_fv(self, n):
        s = self.project.read_text(encoding="utf-8")
        if re.search(r"foundation-version:\s*\d+", s):
            s = re.sub(r"foundation-version:\s*\d+", f"foundation-version: {n}", s)
        else:
            s = re.sub(r"(?m)^(slug:.*)$", rf"\1 · foundation-version: {n}", s, count=1)
        self.project.write_text(s, encoding="utf-8")

    def _fv(self):
        m = re.search(r"foundation-version:\s*(\d+)", self.project.read_text(encoding="utf-8"))
        return int(m.group(1)) if m else None

    def _task_md(self, slug):
        return (self.root / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")

    # --- scenarios -------------------------------------------------------------
    def test_glossary_delta_consolidated(self):  # M1
        self._new_task("alpha")
        self._plant_glossary("alpha", "widget: a small reusable gizmo used across the pipeline")
        self._mark_done("alpha")
        self._set_fv(9)
        out, err, code = _run(["fold", "--comp", "GLOSSARY"])
        self.assertIsNone(code, f"fold should succeed: {out}{err}")
        glossary = self.glossary.read_text(encoding="utf-8")
        self.assertIn("widget: a small reusable gizmo used across the pipeline", glossary)
        self.assertIn("[folded foundation-version 10]", self._task_md("alpha"))
        self.assertEqual(self._fv(), 10)

    def test_duplicate_term_skipped(self):  # M2
        self.glossary.write_text(
            self.glossary.read_text(encoding="utf-8") + "Widget: an EXISTING, different definition.\n",
            encoding="utf-8")
        before_glossary = self.glossary.read_bytes()
        self._new_task("beta")
        self._plant_glossary("beta", "widget: a NEW definition that must not be added")
        self._mark_done("beta")
        self._set_fv(4)
        out, err, code = _run(["fold", "--comp", "GLOSSARY"])
        self.assertIsNone(code, f"fold should succeed: {out}{err}")
        self.assertEqual(self.glossary.read_bytes(), before_glossary,
                          "a case-insensitive existing term is never duplicated")
        self.assertIn("[folded foundation-version 5]", self._task_md("beta"),
                       "the task's own line is still stamped even when the term is a duplicate")

    def test_unparseable_line_skipped_and_counted(self):  # R1
        self._new_task("clean")
        self._plant_glossary("clean", "gadget: a clean, parseable definition")
        self._mark_done("clean")
        self._new_task("messy")
        self._plant_glossary("messy", "holder-side heartbeat — a background daemon thread with no colon at all")
        self._mark_done("messy")
        self._set_fv(1)
        before_messy = self._task_md("messy")
        out, err, code = _run(["fold", "--comp", "GLOSSARY"])
        self.assertIsNone(code, f"fold should succeed: {out}{err}")
        glossary = self.glossary.read_text(encoding="utf-8")
        self.assertIn("gadget: a clean, parseable definition", glossary)
        self.assertNotIn("holder-side heartbeat", glossary)
        self.assertEqual(self._task_md("messy"), before_messy, "an unparseable line is byte-unchanged")
        self.assertIn("unparseable", (out + err).lower(), "the skip is measured/reported, not silent to the human")

    def test_already_folded_line_not_reselected(self):  # M3 idempotency
        self._new_task("gamma")
        self._plant_glossary("gamma", "sprocket: a toothed part [folded foundation-version 3]")
        self._mark_done("gamma")
        self._set_fv(3)
        before_glossary = self.glossary.read_bytes()
        before_task = self._task_md("gamma")
        out, err, code = _run(["fold", "--comp", "GLOSSARY"])
        self.assertIsNotNone(code, "nothing open to fold -> refuses, not a silent no-op success")
        self.assertIn("no_open_deltas", out + err)
        self.assertEqual(self.glossary.read_bytes(), before_glossary)
        self.assertEqual(self._task_md("gamma"), before_task)

    def test_glossary_and_competency_share_one_bump(self):  # M4
        self._new_task("comp_task")
        self._plant_comp("comp_task", "SDD", "wording-lint rejects slang")
        self._new_task("gloss_task")
        self._plant_glossary("gloss_task", "cog: a small gear")
        self._mark_done("gloss_task")
        self._set_fv(20)
        out, err, code = _run(["fold"])
        self.assertIsNone(code, f"fold should succeed: {out}{err}")
        self.assertEqual(self._fv(), 21, "exactly one bump covers both classes")
        self.assertIn("[folded foundation-version 21]", self._task_md("gloss_task"))
        self.assertIn("[SDD · folded]", self._task_md("comp_task"))
        self.assertIn("[folded foundation-version 21]", self._task_md("comp_task"))
        self.assertIn("cog: a small gear", self.glossary.read_text(encoding="utf-8"))

    def test_not_done_task_excluded(self):  # Reject: not-done
        self._new_task("undone")
        self._plant_glossary("undone", "thingamajig: should never fold while not done")
        # deliberately do NOT _mark_done
        self._set_fv(2)
        before_glossary = self.glossary.read_bytes()
        out, err, code = _run(["fold", "--comp", "GLOSSARY"])
        self.assertIsNotNone(code)
        self.assertIn("no_open_deltas", out + err)
        self.assertEqual(self.glossary.read_bytes(), before_glossary)

    def test_comp_glossary_narrows_to_glossary_only(self):  # contract narrowing
        self._new_task("comp_only")
        self._plant_comp("comp_only", "SDD", "an untouched competency lesson")
        self._new_task("gloss_only")
        self._plant_glossary("gloss_only", "doohickey: a small mechanism")
        self._mark_done("gloss_only")
        self._set_fv(6)
        out, err, code = _run(["fold", "--comp", "GLOSSARY"])
        self.assertIsNone(code, f"fold should succeed: {out}{err}")
        self.assertIn("[SDD · open]", self._task_md("comp_only"), "competency lesson untouched by --comp GLOSSARY")
        self.assertIn("doohickey: a small mechanism", self.glossary.read_text(encoding="utf-8"))

    def test_least_sure_flag_continuation_no_contamination_no_false_candidate(self):
        # regression: every REAL frozen task inserts "Least-sure flag surfaced at freeze:" directly
        # after "Glossary deltas:" (before "Status: FROZEN...") — a continuation-stop check whose
        # character class is too narrow to recognize that hyphenated label (real corpus label, e.g.
        # "Least-sure flag surfaced at freeze:", "BIND-DON'T-BREAK:") wrongly treats it as more
        # wrapped glossary prose: it corrupts a clean definition with the flag's own unrelated text
        # (the rule-id-coverage shape) AND can turn a genuinely no-colon, unparseable line into a
        # false-positive candidate that borrows the flag line's OWN colon (the seams-doc shape).
        self._new_task("clean_flagged")
        self._plant_glossary_with_flag(
            "clean_flagged", "gizmo: a clean definition that must stay clean",
            flag_text="[spec] something entirely unrelated that must never appear in GLOSSARY.md")
        self._mark_done("clean_flagged")
        self._new_task("noclon_flagged")
        self._plant_glossary_with_flag(
            "noclon_flagged", "`Term A` (new) + `Term B` (amended) — both listed above.",
            flag_text="[contract] unrelated freeze-time prose with its own colon: like this")
        self._mark_done("noclon_flagged")
        self._set_fv(7)
        out, err, code = _run(["fold", "--comp", "GLOSSARY"])
        self.assertIsNone(code, f"fold should succeed: {out}{err}")
        glossary = self.glossary.read_text(encoding="utf-8")
        self.assertIn("gizmo: a clean definition that must stay clean", glossary)
        self.assertNotIn("something entirely unrelated", glossary,
                          "the Least-sure-flag continuation must never bleed into a glossary definition")
        self.assertNotIn("Term A", glossary,
                          "a no-colon line stays unparseable, never a false candidate borrowing the flag's colon")
        self.assertIn("unparseable", (out + err).lower(),
                       "the no-colon line is measured/reported, not silently admitted")

    # --- pure unit proofs --------------------------------------------------
    def test_parse_glossary_delta_pure(self):
        self.assertEqual(add._parse_glossary_delta("widget: a small gizmo"),
                          ("widget", "a small gizmo"))
        self.assertEqual(add._parse_glossary_delta("`Widget`: a backtick-wrapped term"),
                          ("Widget", "a backtick-wrapped term"))
        self.assertIsNone(add._parse_glossary_delta("none"), "none -> not a candidate")
        self.assertIsNone(add._parse_glossary_delta("none — deliberately empty"))
        self.assertIsNone(add._parse_glossary_delta(
            "holder-side heartbeat — a background thread with no colon"), "no top-level colon -> reject")
        self.assertIsNone(add._parse_glossary_delta(
            "`portable roster: the compact thing` (reaffirms the milestone glossary delta)"),
            "an unmatched opening backtick before the split colon -> reject")
        self.assertIsNone(add._parse_glossary_delta(
            "`search corpus`: the active set. `indexed line(s)`: a second embedded term"),
            "a second embedded `term`: span in the definition -> multi-term, reject")
        self.assertIsNone(add._parse_glossary_delta(
            "widget: already folded [folded foundation-version 7]"),
            "already-stamped -> not a candidate")

    def test_fold_glossary_delta_pure(self):
        line = "Glossary deltas: widget: a small gizmo\n"
        out = add._fold_glossary_delta(line, 12)
        self.assertIsNotNone(out)
        self.assertIn("widget: a small gizmo [folded foundation-version 12]", out)
        self.assertIsNone(add._fold_glossary_delta("Glossary deltas: none\n", 12))


if __name__ == "__main__":
    unittest.main()
