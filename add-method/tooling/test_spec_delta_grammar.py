#!/usr/bin/env python3
"""Behavioral proof of the SPEC-delta resolution grammar (task: spec-delta-grammar, delta-resolution).

CONTRACT (frozen @ v1): §7 gains a SEPARATE "### Spec delta" track, disjoint from
"### Competency deltas". Entries are "- [SPEC · <status>] <text>" with status ∈
{open,seeded,dropped} (tag-scoped — disjoint from competency {open,folded,rejected}).
_collect_open_spec_deltas(root) -> [{task,text,evidence}] (open only). _task_prose's
observe = first-open-SPEC -> legacy "Spec delta for the next loop:" -> "(unknown)".
_lint_task_deltas lints BOTH blocks tag-scoped; reasons unknown_status|malformed_delta|
unknown_competency|no_evidence (evidence REQUIRED on open SPEC too). `add.py deltas`
shows a separate spec section + a separate --json key. new-task scaffolds a "### Spec
delta" block (tmpl ≡ fallback). One test per SCENARIO.
Run: python3 -m unittest test_spec_delta_grammar -v
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


class SpecDeltaGrammarTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-spec-delta-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    # --- helpers -------------------------------------------------------------
    def _task(self, slug):
        """Create task `slug` (if new); return its PLAN.md path."""
        root = add.find_root()
        if slug not in (add.load_state(root).get("tasks") or {}):
            add.main(["new-task", slug, "--title", "Feature"])
        return Path(self.tmp) / ".add" / "tasks" / slug / "PLAN.md"

    def _write_observe(self, slug, body):
        """Replace everything after the '## 7 · OBSERVE' heading line with `body`.

        §7 is the last section, so this gives each test full control of the OBSERVE
        content (blocks + legacy line) independent of the template's current shape."""
        p = self._task(slug)
        text = p.read_text(encoding="utf-8")
        idx = text.index("## 7 · OBSERVE")
        head_end = text.index("\n", idx) + 1
        p.write_text(text[:head_end] + body, encoding="utf-8")
        return p

    def _state_bytes(self):
        return (Path(self.tmp) / ".add" / "state.json").read_bytes()

    # --- scenarios -----------------------------------------------------------
    def test_spec_block_lists_only_open_collects(self):  # Must 1, 4
        self._write_observe(
            "a",
            "### Spec delta\n"
            "- [SPEC · open] keep this one (evidence: prod spike)\n"
            "- [SPEC · seeded] already consumed (evidence: e) [→ next-task]\n"
            "- [SPEC · dropped] decided against (evidence: e)\n",
        )
        root = add.find_root()
        spec = add._collect_open_spec_deltas(root)
        texts = [d["text"] for d in spec if d["task"] == "a"]
        self.assertEqual(texts, ["keep this one"], "only the OPEN SPEC entry collects")
        comp = add._collect_open_deltas(root)
        self.assertEqual(
            sum(len(v) for v in comp.values()), 0,
            "a SPEC entry must never be bucketed as a competency delta",
        )

    def test_spec_status_lints_clean_arrow_tolerated(self):  # Must 2, 6
        self._write_observe(
            "a",
            "### Spec delta\n"
            "- [SPEC · seeded] rate-limit retry (evidence: herd) [→ fix-herd]\n",
        )
        code, out, _ = _run(["check"])
        self.assertIn("deltas well-formed", out, "the delta-lint check did not run")
        self.assertNotIn("unknown_status", out)
        self.assertNotIn("malformed_delta", out, "[→ fix-herd] pointer must not trip the lint")
        self.assertEqual(code, 0)

    def test_spec_cross_set_status_rejected(self):  # Reject 1
        self._write_observe("a", "### Spec delta\n- [SPEC · folded] wrong set (evidence: e)\n")
        code, out, _ = _run(["check"])
        self.assertEqual(code, 1)
        self.assertIn("unknown_status", out)
        self.assertIn("[SPEC · folded]", out, "the reason must name the offending line")

    def test_competency_cross_set_status_rejected(self):  # Reject 2
        self._write_observe("a", "### Competency deltas\n- [SDD · seeded] wrong set (evidence: e)\n")
        code, out, _ = _run(["check"])
        self.assertEqual(code, 1)
        self.assertIn("unknown_status", out)
        self.assertIn("[SDD · seeded]", out)

    def test_spec_empty_text_malformed(self):  # Reject 3
        self._write_observe("a", "### Spec delta\n- [SPEC · open]\n")
        code, out, _ = _run(["check"])
        self.assertEqual(code, 1)
        self.assertIn("malformed_delta", out)

    def test_spec_evidence_required(self):  # Must 7, Reject 4
        self._write_observe("a", "### Spec delta\n- [SPEC · open] surface 429s in the UI\n")
        code, out, _ = _run(["check"])
        self.assertEqual(code, 1, "an open SPEC entry with no evidence must fail")
        self.assertIn("no_evidence", out)
        # the SAME task, now WITH evidence, lints clean (overwrite a — no stray bad task
        # left in the project, so the whole-project check reflects only the fixed entry)
        self._write_observe("a", "### Spec delta\n- [SPEC · open] surface 429s (evidence: prod 429s)\n")
        code2, out2, _ = _run(["check"])
        self.assertEqual(code2, 0, "an open SPEC entry WITH evidence must pass")

    def test_observe_from_spec_block(self):  # Must 3
        self._write_observe("a", "### Spec delta\n- [SPEC · open] rate-limit retry (evidence: herd)\n")
        root = add.find_root()
        observe, _deltas = add._task_prose(root, "a")
        self.assertEqual(observe, "rate-limit retry")

    def test_observe_legacy_fallback(self):  # Must 3 (back-compat)
        self._write_observe("a", "Spec delta for the next loop: legacy value here\n")
        root = add.find_root()
        observe, _deltas = add._task_prose(root, "a")
        self.assertEqual(observe, "legacy value here")
        self.assertEqual(
            [d for d in add._collect_open_spec_deltas(root) if d["task"] == "a"], [],
            "a legacy-only task has no SPEC delta to collect",
        )

    def test_deltas_lists_spec_section(self):  # Must 5
        self._write_observe(
            "a",
            "### Spec delta\n"
            "- [SPEC · open] surface 429s in the UI (evidence: prod)\n"
            "\n"
            "### Competency deltas\n"
            "- [TDD · open] missing a scenario (evidence: review)\n",
        )
        before = self._state_bytes()
        code, out, _ = _run(["deltas"])
        self.assertEqual(code, 0, "deltas must exit 0")
        self.assertIn("TDD (1)", out, "competency section still renders")
        self.assertIn("spec", out.lower(), "a distinct SPEC section must render")
        self.assertIn("surface 429s in the UI", out)
        self.assertEqual(self._state_bytes(), before, "deltas must be read-only")
        # --json carries the two under separate keys
        code_j, out_j, _ = _run(["deltas", "--json"])
        payload = json.loads(out_j)
        self.assertIn("by_competency", payload)
        self.assertIn("spec", payload, "--json must carry a separate 'spec' key")
        self.assertEqual(len(payload["spec"]), 1)
        self.assertEqual(payload["spec"][0]["text"], "surface 429s in the UI")

    def test_new_task_scaffolds_spec_block(self):  # Must (template)
        p = self._task("fresh")
        text = p.read_text(encoding="utf-8")
        self.assertIn("### Spec delta", text, "a fresh task must scaffold a '### Spec delta' block")
        self.assertNotIn(
            "Spec delta for the next loop:", text,
            "the legacy free-text field must be gone from the template",
        )

    def test_template_canonical_and_fallback_agree(self):  # Must (template parity)
        # The canonical PLAN.md.tmpl and the embedded _FALLBACK_TASK must both carry
        # the new block (so the tool behaves identically when templates/ is missing).
        tmpl = (Path(add.__file__).parent / "templates" / "PLAN.md.tmpl").read_text(encoding="utf-8")
        self.assertIn("### Spec delta", tmpl)
        self.assertNotIn("Spec delta for the next loop:", tmpl)
        self.assertIn("### Spec delta", add._FALLBACK_TASK)
        self.assertNotIn("Spec delta for the next loop:", add._FALLBACK_TASK)


if __name__ == "__main__":
    unittest.main()
