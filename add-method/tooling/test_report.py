#!/usr/bin/env python3
"""Red/green tests for `add.py report` — the read-only what-happened DASHBOARD.

report renders a milestone digest (banner header · per-task phase track · rollup) to
stdout, sourcing phase/gate/waiver from state.json and prose (observe delta, competency
deltas) from each TASK.md. It is STRICTLY read-only: writes nothing, never mutates
state.json. The same render_report() string is what v9's retro-artifact persists to
RETRO.md, so it must be pure + deterministic. Run:
    python3 -m unittest test_report -v
"""
import hashlib
import io
import os
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


class ReportTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-report-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _state_file(self) -> Path:
        return self._root() / "state.json"

    def _hash_state(self) -> str:
        return hashlib.sha256(self._state_file().read_bytes()).hexdigest()

    def _report(self, *args):
        """Run `report` capturing stdout/stderr; return (out, err, code). report's
        rejects go through _die -> SystemExit; success returns normally (code 0)."""
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["report", *args])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _freeze(self, slug: str) -> None:
        """Stamp §3 FROZEN + a well-formed flag so the universal freeze gate passes at
        tests->build. freeze-gate-universal sweep."""
        p = self._task_md(slug)
        p.write_text(p.read_text().replace(
            "Status: DRAFT",
            "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
            "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
        ), encoding="utf-8")

    def _done_pass(self, slug):
        add.main(["phase", "verify", slug])
        add.main(["gate", "PASS", slug])

    def _task_md(self, slug) -> Path:
        return self._root() / "tasks" / slug / "TASK.md"

    def _set_observe(self, slug, text):
        # observe now derives from the §7 "### Spec delta" block (first open entry).
        p = self._task_md(slug)
        s = p.read_text()
        marker = "### Spec delta"
        idx = s.index(marker) + len(marker)
        s = s[:idx] + f"\n- [SPEC · open] {text} (evidence: scn)\n" + s[idx:]
        p.write_text(s)

    def _add_delta(self, slug, line):
        p = self._task_md(slug)
        p.write_text(p.read_text().rstrip() + "\n" + line + "\n")

    def _add_test_files(self, slug, n):
        d = self._root() / "tasks" / slug / "tests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "test_gen.py").write_text(
            "\n".join(f"def test_case_{i}():\n    assert True\n" for i in range(n)))

    def _rm_tests_dir(self, slug):
        d = self._root() / "tasks" / slug / "tests"
        for f in d.glob("*"):
            f.unlink()
        d.rmdir()

    # ---- scenarios --------------------------------------------------------
    def test_active_mid_flight(self):
        add.main(["new-milestone", "v9", "--title", "Awareness", "--goal", "see what happened"])
        add.main(["new-task", "alpha", "--title", "Alpha"])
        self._done_pass("alpha")
        self._add_test_files("alpha", 3)
        add.main(["new-task", "beta", "--title", "Beta"])  # stays at specify
        before = self._hash_state()
        out, _, code = self._report()  # no arg -> active milestone v9
        self.assertEqual(code, 0)
        self.assertIn("v9", out)
        self.assertIn("1/2 done", out)    # header label grid (v4): TASKS  1/2 done
        self.assertIn("alpha", out)
        self.assertIn("beta", out)
        self.assertEqual(self._hash_state(), before)  # read-only

    def test_named_milestone(self):
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        before = self._hash_state()
        out, _, code = self._report("v9")
        self.assertEqual(code, 0)
        self.assertIn("v9", out)
        self.assertEqual(self._hash_state(), before)

    def test_waiver_surfaced(self):
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        add.main(["phase", "verify", "alpha"])
        add.main(["gate", "RISK-ACCEPTED", "alpha",
                  "--owner", "tin", "--ticket", "JIRA-1", "--expires", "2026-12-31"])
        out, _, code = self._report("v9")
        self.assertEqual(code, 0)
        self.assertIn("WAIVERS", out)
        self.assertIn("RISK", out)        # gate shortened to RISK in the column (v3)
        self.assertIn("tin", out)
        self.assertIn("JIRA-1", out)
        self.assertIn("2026-12-31", out)

    def test_failclosed_unknown(self):
        # observe is fail-closed in the raw data; the v3 compact table shows the
        # tests column (0), observe detail lives in --json.
        import json as _json
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])           # observe = placeholder, no tests/ files
        self._rm_tests_dir("alpha")
        out, _, code = self._report("v9")
        self.assertEqual(code, 0)
        self.assertRegex(out, r"alpha\s+specify\s+—\s+0\s")  # row renders, tests=0, no crash
        jout, _, _ = self._report("v9", "--json")
        self.assertEqual(_json.loads(jout)["tasks"][0]["observe"], "(unknown)")

    def test_deltas_with_status(self):
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        self._add_delta("alpha", "- [DDD · open] org/workspace conflated (evidence: scn_x failed)")
        self._add_delta("alpha", "- [TDD · folded] missing race scenario (evidence: review note)")
        out, _, code = self._report("v9")
        self.assertEqual(code, 0)
        self.assertIn("DDD", out)
        self.assertIn("open", out)
        self.assertIn("TDD", out)
        self.assertIn("folded", out)  # NOT open-only — folded delta still shows

    def test_zero_task_milestone(self):
        add.main(["new-milestone", "v9", "--goal", "g"])  # zero member tasks
        out, _, code = self._report("v9")
        self.assertEqual(code, 0)        # no ZeroDivisionError
        self.assertIn("0/0 done", out)   # header grid: TASKS  0/0 done (no ZeroDivisionError)
        self.assertIn("(no tasks yet)", out)
        self.assertIn("met", out)        # exit-criteria line still renders (0/N from the template)

    def test_missing_milestone_doc(self):
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        (self._root() / "milestones" / "v9" / "MILESTONE.md").unlink()
        out, _, code = self._report("v9")
        self.assertEqual(code, 0)        # milestone exists in state -> still prints
        self.assertIn("(unknown)", out)  # title/goal unknown
        self.assertIn("0/0 met", out)    # no doc -> no exit criteria

    def test_unknown_milestone(self):
        add.main(["new-milestone", "v9", "--goal", "g"])
        before = self._hash_state()
        out, err, code = self._report("v99")
        self.assertNotEqual(code, 0)
        self.assertIn("unknown_milestone", out + err)
        self.assertEqual(self._hash_state(), before)

    def test_no_active_milestone(self):
        # fresh init has no active_milestone and no arg given
        _, err, code = self._report()
        self.assertNotEqual(code, 0)
        out_err = err
        self.assertIn("no_active_milestone", out_err)

    def test_render_is_pure(self):
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        root, state = add.find_root(), None
        state = add.load_state(root)
        before = self._hash_state()
        a = add.render_report(root, state, "v9")
        b = add.render_report(root, state, "v9")
        self.assertIsInstance(a, str)
        self.assertEqual(a, b)                       # deterministic
        self.assertEqual(self._hash_state(), before)  # zero writes

    def test_phase_track_compact(self):
        # v3: compact 8-cell track (no per-cell labels). Asserted on the canonical
        # Unicode render (what RETRO.md gets); cmd_report downshifts to ASCII when
        # stdout can't do Unicode (e.g. a pipe), which is tested separately.
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        add.main(["phase", "tests", "alpha"])  # index 3 -> ◉ at cell 4
        add.main(["new-task", "beta"])
        self._done_pass("beta")
        root = add.find_root()
        out = add.render_report(root, add.load_state(root), "v9")  # ascii=False (canonical)
        self.assertIn("●●◉○○○", out)      # alpha at 'tests': 2 reached, current, 3 pending
        self.assertIn("●●●●●●", out)      # beta done -> whole track reached (6 phases)
        self.assertIn("PASS", out)         # gate word (no glyph badge in column)
        self.assertIn("legend", out)       # one legend, not per-row labels

    def test_progress_bar_glyphs(self):
        # v3: the EXIT CRITERIA bar uses the reached/pending glyphs, no divide-by-zero
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        self._done_pass("alpha")
        add.main(["new-task", "beta"])
        root = add.find_root()
        out = add.render_report(root, add.load_state(root), "v9")  # canonical Unicode
        self.assertIn("1/2 done", out)                      # header grid: TASKS  1/2 done
        self.assertRegex(out, r"EXIT CRITERIA\s+[●○]{10}")  # 10-cell bar

    def test_observe_scoped_to_section(self):
        # Regression: a decoy 'Spec delta for the next loop:' OUTSIDE §7 must NOT win.
        # observe lives in --json (not the compact v3 table), so assert there.
        import json as _json
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        p = self._task_md("alpha")
        s = p.read_text().replace(
            "## 1 · SPECIFY",
            'mentions "Spec delta for the next loop: DECOY" in prose\n\n## 1 · SPECIFY', 1)
        p.write_text(s)
        self._set_observe("alpha", "real delta from section 7")
        jout, _, _ = self._report("v9", "--json")
        observe = _json.loads(jout)["tasks"][0]["observe"]
        self.assertEqual(observe, "real delta from section 7")
        self.assertNotIn("DECOY", observe)

    def test_goal_wraps_label_once(self):
        long_goal = "a person sees what happened " * 8  # forces multi-line wrap
        add.main(["new-milestone", "v9", "--goal", long_goal.strip()])
        out, _, code = self._report("v9")
        self.assertEqual(code, 0)
        goal_lines = [ln for ln in out.splitlines() if ln.strip().startswith("goal")]
        self.assertEqual(len(goal_lines), 1)  # label appears once, not on every wrapped line

    def test_json_raw_capture(self):
        # The tool captures RAW DATA the agent formats from a template. --json must be
        # valid JSON with the report's facts, and stay strictly read-only.
        import json as _json
        add.main(["new-milestone", "v9", "--title", "Awareness", "--goal", "see it"])
        add.main(["new-task", "alpha"])
        self._done_pass("alpha")
        self._add_delta("alpha", "- [ADD · open] learned a thing (evidence: scn)")
        before = self._hash_state()
        out, _, code = self._report("v9", "--json")
        self.assertEqual(code, 0)
        data = _json.loads(out)  # must parse
        self.assertEqual(data["milestone"]["slug"], "v9")
        self.assertEqual(data["milestone"]["title"], "Awareness")
        self.assertEqual(data["summary"]["tasks_total"], 1)
        self.assertEqual(data["summary"]["tasks_done"], 1)
        self.assertEqual(data["summary"]["gates"]["PASS"], 1)
        self.assertEqual(data["tasks"][0]["slug"], "alpha")
        self.assertIn("phase_index", data["tasks"][0])
        self.assertTrue(any("ADD" in d for d in data["deltas"]))
        self.assertEqual(self._hash_state(), before)  # read-only

    def test_multiline_fidelity(self):
        # Real §7 fields wrap across physical lines; raw capture must JOIN them, not
        # truncate at the first newline.
        import json as _json
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        p = self._task_md("alpha")
        s = p.read_text()
        marker = "### Spec delta"
        idx = s.index(marker) + len(marker)
        s = s[:idx] + (
            "\n- [SPEC · open] first line of the delta\n"
            "  second physical line continues it\n"
            "  third line ends it (evidence: scn_x)\n") + s[idx:]
        s = s.rstrip() + (
            "\n- [ADD · open] a learning that wraps across\n"
            "  an indented continuation line (evidence: scn_y)\n")
        p.write_text(s)
        out, _, code = self._report("v9", "--json")
        self.assertEqual(code, 0)
        data = _json.loads(out)
        obs = data["tasks"][0]["observe"]
        self.assertIn("first line of the delta", obs)
        self.assertIn("third line ends it", obs)          # continuation joined, not lost
        self.assertTrue(any("indented continuation line" in d for d in data["deltas"]))

    def test_json_and_text_agree(self):
        # one source of facts: --json counts must match the text dashboard's
        import json as _json
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        self._done_pass("alpha")
        add.main(["new-task", "beta"])
        jout, _, _ = self._report("v9", "--json")
        tout, _, _ = self._report("v9")
        data = _json.loads(jout)
        self.assertIn(f"{data['summary']['tasks_done']}/{data['summary']['tasks_total']} done", tout)

    # ---- v3 terminal-correctness tier ------------------------------------
    def test_verdict_states(self):
        # verdict-first header: DONE / ACTIVE / BLOCKED
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        out, _, _ = self._report("v9")
        self.assertIn("ACTIVE", out)                      # in flight
        self._done_pass("alpha")
        out, _, _ = self._report("v9")
        self.assertIn("DONE", out)                        # all tasks done
        add.main(["new-task", "beta"])
        self._freeze("beta")                     # freeze-gate-universal sweep
        add.main(["phase", "build", "beta"])
        add.main(["gate", "HARD-STOP", "beta"])
        out, _, _ = self._report("v9")
        self.assertIn("BLOCKED", out)                     # a HARD-STOP blocks

    def test_ascii_tier(self):
        # render_report(ascii=True) must avoid Unicode box/glyphs for dumb terminals
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        self._done_pass("alpha")            # done -> track is all reached '#'
        root = add.find_root()
        out = add.render_report(root, add.load_state(root), "v9", ascii=True)
        self.assertIn("=" * 10, out)        # ASCII banner
        self.assertIn("#", out)             # ASCII reached glyph
        self.assertNotIn("●", out)          # no Unicode dots
        self.assertNotIn("═", out)          # no Unicode banner

    def test_no_ansi_when_not_tty(self):
        # captured (non-tty) stdout must carry NO ANSI escapes — keeps pipes/RETRO clean
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        out, _, code = self._report("v9")
        self.assertEqual(code, 0)
        self.assertNotIn("\x1b[", out)      # no color codes when piped

    def test_plain_flag_is_ascii_no_color(self):
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        out, _, code = self._report("v9", "--plain")
        self.assertEqual(code, 0)
        self.assertNotIn("\x1b[", out)      # never colored
        self.assertNotIn("●", out)          # ASCII tier
        self.assertIn("=" * 10, out)

    def test_columns_aligned_no_len_rightpad(self):
        # the v3 table is left-aligned columns (the header names them); no 'gate:' tail
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        out, _, _ = self._report("v9")
        self.assertRegex(out, r"TASK\s+PHASE\s+GATE\s+TESTS\s+PROGRESS")
        self.assertNotIn("gate:", out)      # old right-aligned badge format is gone

    # ---- v4 layout (human-review enhancement) ----------------------------
    def test_header_is_label_grid(self):
        # v4: the crammed '·'-joined header became a scannable 2-col label grid
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        self._done_pass("alpha")
        out, _, _ = self._report("v9")
        self.assertRegex(out, r"VERDICT\s+DONE")              # verdict leads, own line
        self.assertRegex(out, r"TASKS\s+1/1 done\s+CRITERIA\s+\d+/\d+ met")
        self.assertRegex(out, r"GATES\s+1 PASS\s+WAIVERS\s+none")
        self.assertNotIn("· 1/1 tasks ·", out)                # old crammed line is gone

    def test_learnings_wrapped_not_clipped(self):
        # v4: learnings are word-wrapped to FULL text (no mid-word '…' truncation),
        # each led by a bullet — the retro's payload must be readable.
        add.main(["new-milestone", "v9", "--goal", "g"])
        add.main(["new-task", "alpha"])
        long_tail = "the quick brown fox jumps over the lazy dog repeatedly " * 4
        self._add_delta("alpha", f"- [ADD · open] {long_tail.strip()} (evidence: scn_z)")
        out = add.render_report(add.find_root(), add.load_state(add.find_root()), "v9")
        self.assertIn("LEARNINGS (1 carried)", out)
        self.assertIn("• ADD · open ·", out)                  # bulleted
        self.assertIn("(evidence: scn_z)", out)               # tail survives -> not clipped
        self.assertNotRegex(out, r"…\s*\n.*ADD · open")       # no ellipsis on the learning
        learn_lines = [ln for ln in out.splitlines() if "evidence: scn_z" in ln
                       or "quick brown fox" in ln]
        self.assertGreater(len(learn_lines), 1)               # wrapped across >1 line


if __name__ == "__main__":
    unittest.main()
