#!/usr/bin/env python3
"""Behavioral proof of the SPEC-delta resolution VERBS (task: seed-and-drop, delta-resolution).

CONTRACT (frozen @ v1): the first WRITERS that move a SPEC delta off `open`.
  add.py new-task <new> --from-delta <prior>
    -> scaffolds <new>; §1 Feature = "<delta-text> (from <prior> spec-delta)";
       flips prior's FIRST "[SPEC · open] X (evidence:e)" -> "[SPEC · seeded] X (evidence:e) [→ <new>]";
       state["tasks"][<new>]["from_delta"] = "<prior>".
    reject: "no_open_spec_delta" (prior has none) · "already exists" (slug taken — prior NOT flipped).
  add.py drop-delta <task>
    -> flips task's FIRST "[SPEC · open] X" -> "[SPEC · dropped] X" (text+evidence intact).
    reject: "no_open_spec_delta" · "unknown task '<slug>'".
  Both take the FIRST open delta in source order; validate-ALL-then-write (no partial writes).
  Internal _resolve_spec_delta(text, new_status, pointer=None) -> str | None (pure; None when no open).
One test per SCENARIO.
Run: python3 -m unittest test_seed_and_drop -v
"""
import contextlib
import io
import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import add


def _run(argv):
    """Run add.main(argv), capturing (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            add.main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out.getvalue(), err.getvalue()


class SeedAndDropTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-seed-drop-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])  # no "setup" key -> grandfathered-locked

    def tearDown(self):
        os.chdir(self._cwd)

    # --- helpers -------------------------------------------------------------
    def _root(self):
        return self.tmp / ".add"

    def _task_md(self, slug):
        return self._root() / "tasks" / slug / "PLAN.md"

    def _mk(self, slug):
        """Create task `slug` (idempotent); return its PLAN.md path."""
        root = add.find_root()
        if slug not in (add.load_state(root).get("tasks") or {}):
            add.main(["new-task", slug, "--title", "Feature"])
        return self._task_md(slug)

    def _set_spec(self, slug, *open_texts):
        """Rewrite `slug`'s §7 OBSERVE with one "- [SPEC · open] <t> (evidence: ev)"
        line per `open_texts`, in order, followed by an empty Competency block."""
        p = self._mk(slug)
        text = p.read_text(encoding="utf-8")
        idx = text.index("## 7 · OBSERVE")
        head_end = text.index("\n", idx) + 1
        lines = "".join(f"- [SPEC · open] {t} (evidence: ev)\n" for t in open_texts)
        body = f"\n### Spec delta\n{lines}\n### Competency deltas\n"
        p.write_text(text[:head_end] + body, encoding="utf-8")
        return p

    def _state(self):
        return json.loads((self._root() / "state.json").read_text(encoding="utf-8"))

    # --- scenarios -----------------------------------------------------------
    def test_seed_creates_task_and_seeds_source(self):  # Must 1
        self._set_spec("prior", "rate-limit retries")
        code, out, err = _run(["new-task", "followup", "--from-delta", "prior"])
        self.assertEqual(code, 0, f"seed failed: {out}{err}")
        # new task scaffolded with provenance-stamped Feature
        followup = self._task_md("followup")
        self.assertTrue(followup.exists(), "followup task not created")
        ftext = followup.read_text(encoding="utf-8")
        self.assertIn("Feature: rate-limit retries (from prior spec-delta)", ftext)
        # source delta consumed -> seeded with the pointer stamp, evidence preserved
        ptext = self._task_md("prior").read_text(encoding="utf-8")
        self.assertIn(
            "- [SPEC · seeded] rate-limit retries (evidence: ev) [→ followup]", ptext)
        self.assertNotIn("[SPEC · open] rate-limit retries", ptext)
        # lineage recorded in state
        self.assertEqual(self._state()["tasks"]["followup"]["from_delta"], "prior")

    def test_seed_no_open_refuses(self):  # Reject 1 (seed)
        self._mk("prior")  # fresh task — empty "### Spec delta" block, no open delta
        before = self._task_md("prior").read_bytes()
        code, out, err = _run(["new-task", "followup", "--from-delta", "prior"])
        self.assertNotEqual(code, 0)
        self.assertIn("no_open_spec_delta", out + err)
        self.assertFalse((self._root() / "tasks" / "followup").exists())
        self.assertEqual(self._task_md("prior").read_bytes(), before)  # untouched

    def test_seed_taken_slug_no_consume(self):  # Reject 3 (validate-all-then-write)
        self._set_spec("prior", "shared idea")
        self._mk("followup")  # the slug is already taken
        before = self._task_md("prior").read_bytes()
        code, out, err = _run(["new-task", "followup", "--from-delta", "prior"])
        self.assertNotEqual(code, 0)
        self.assertIn("already exists", out + err)
        # the prior delta must remain OPEN — nothing was written
        self.assertEqual(self._task_md("prior").read_bytes(), before)
        self.assertIn("[SPEC · open] shared idea",
                      self._task_md("prior").read_text(encoding="utf-8"))

    def test_resolve_spec_delta_pure_none(self):  # internal contract
        # a §7 body with no OPEN SPEC delta -> the pure transformer returns None (no write)
        text = "## 7 · OBSERVE\n\n### Spec delta\n- [SPEC · dropped] x (evidence: e)\n"
        self.assertIsNone(add._resolve_spec_delta(text, "dropped"))


if __name__ == "__main__":
    unittest.main()
