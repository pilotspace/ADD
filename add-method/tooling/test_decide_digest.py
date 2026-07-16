#!/usr/bin/env python3
"""Red/green tests for `add.py report --decide` — the decision-seam digest — and the
rollup's DECIDE NEXT footer (task decide-digest, milestone v13).

The digest detects a task's seam FROM STATE ONLY (recorded / front / gate), extracts
decision markers (`⚠` / `- [~]` / `- [ ]` + deeper-indented continuations) BYTE-VERBATIM
from TASK.md §bodies, and renders decisive-facts-first: NEEDS YOUR JUDGMENT → ENGINE
FACTS → UNLOCKS → DECIDE. Every --decide path is PURE (no writes). The milestone rollup
always ends with one DECIDE NEXT line (HARD-STOP → fold+archive → seam-blocked task →
run-in-progress). Asserts behavior via stdout/exit/state — never internals. Run:
    python3 -m unittest test_decide_digest -v
"""
import hashlib
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add


def _meet_exit_criteria(ms: str) -> None:
    """v20 goal-gate: check the milestone's '## Exit criteria' box so milestone-done
    releases. Targets only the Exit-criteria section — never the Tasks rows."""
    root = add.find_root()
    p = root / "milestones" / ms / add.MILESTONE_FILE
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"## Exit criteria.*?(?=\n## |\Z)",
                  lambda m: m.group(0).replace("- [ ]", "- [x]"), text, flags=re.S)
    p.write_text(text, encoding="utf-8")

# §6 marker (line + deeper-indented continuation) used by the byte-verbatim assertions.
SEC6_MARKER = ("  - [~] disclosed deviation — touched a meta-test\n"
               "      registry line only; weakens no assertion")
SEC1_FLAG = "  ⚠ risky assumption — least sure because prose drifts; if wrong: re-cut"


def _task_md_text(sec1="", sec3="", sec6=""):
    """A minimal TASK.md with the seven numbered headings and controlled §bodies."""
    return "\n".join([
        "# TASK: t", "",
        "## 1 · SPECIFY", sec1 or "Feature: f", "",
        "## 2 · SCENARIOS", "(none)", "",
        "## 3 · CONTRACT", sec3 or "shape", "",
        "## 4 · TESTS", "plan", "",
        "## 5 · BUILD", "code", "",
        "## 6 · VERIFY", sec6 or "  - [x] all tests pass", "",
        "## 7 · OBSERVE", "watch", "",
    ])


class DecideDigestTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-decide-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])
        add.main(["new-milestone", "v13", "--title", "Decide", "--goal", "decide fast"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _state_file(self) -> Path:
        return self._root() / "state.json"

    def _hash_state(self) -> str:
        return hashlib.sha256(self._state_file().read_bytes()).hexdigest()

    def _file_set(self):
        return sorted(str(p) for p in self._root().rglob("*") if p.is_file())

    def _run(self, *args):
        """Run `report` capturing stdout/stderr; return (out, err, code)."""
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
        tests->build. freeze-gate-universal sweep.
        _task_md_text does not include 'Status: DRAFT', so append before ## 4 · TESTS."""
        p = self._root() / "tasks" / slug / "TASK.md"
        txt = p.read_text(encoding="utf-8")
        if "Status: DRAFT" in txt:
            txt = txt.replace(
                "Status: DRAFT",
                "Status: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
                "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none",
            )
        else:
            txt = txt.replace(
                "\n## 4 · TESTS\n",
                "\nStatus: FROZEN @ v1 — approved by Tester 2026-06-27.\n"
                "Least-sure flag surfaced at freeze: [contract] fixture stub — cost: none\n"
                "\n## 4 · TESTS\n",
            )
        p.write_text(txt, encoding="utf-8")

    def _mk_task(self, slug, phase=None, sec1="", sec3="", sec6="", deps=None):
        argv = ["new-task", slug, "--title", slug]
        if deps:
            argv += ["--depends-on", deps]
        add.main(argv)
        (self._root() / "tasks" / slug / "TASK.md").write_text(
            _task_md_text(sec1, sec3, sec6), encoding="utf-8")
        if phase:
            add.main(["phase", phase, slug])

    # ---- task-level --decide ----------------------------------------------
    def test_gate_seam_digest_leads_with_judgment(self):
        add.main(["new-task", "dep-a", "--title", "dep"])
        add.main(["phase", "verify", "dep-a"])
        add.main(["gate", "PASS", "dep-a"])
        self._mk_task("alpha", phase="verify",
                      sec1=SEC1_FLAG, sec6=SEC6_MARKER, deps="dep-a")
        out, _, code = self._run("v13", "alpha", "--decide")
        self.assertEqual(code, 0)
        self.assertIn("NEEDS YOUR JUDGMENT (2)", out)
        # §6 marker renders BEFORE the §1 flag, both verbatim (line content intact)
        self.assertIn("disclosed deviation — touched a meta-test", out)
        self.assertIn("registry line only; weakens no assertion", out)
        self.assertIn("risky assumption", out)
        self.assertLess(out.index("disclosed deviation"), out.index("risky assumption"))
        self.assertIn("ENGINE FACTS", out)
        self.assertIn("verify", out)
        self.assertIn("dep-a", out)                  # deps with their gates
        self.assertIn("PASS | RISK-ACCEPTED | HARD-STOP", out)

    def test_front_seam_renders_bundle_for_approval(self):
        sec1 = SEC1_FLAG + "\n  ⚠ second flag — least sure because new; if wrong: redo"
        sec3 = "the-frozen-shape-text\n\nStatus: DRAFT"
        self._mk_task("alpha", phase="plan", sec1=sec1, sec3=sec3)
        out, _, code = self._run("v13", "alpha", "--decide")
        self.assertEqual(code, 0)
        self.assertIn("risky assumption", out)
        self.assertIn("second flag", out)
        self.assertIn("the-frozen-shape-text", out)  # §3 block verbatim
        self.assertIn("STATUS DRAFT", out)
        # flags render before the contract block
        self.assertLess(out.index("risky assumption"), out.index("the-frozen-shape-text"))
        self.assertIn("freeze", out)                 # DECIDE: approve -> freeze §3 -> run

    def test_frozen_front_no_pending_decision(self):
        self._mk_task("alpha", phase="tests",
                      sec3="shape\n\nStatus: FROZEN @ v1")
        out, _, code = self._run("v13", "alpha", "--decide")
        self.assertEqual(code, 0)
        self.assertIn("no decision pending", out)
        self.assertIn("verify", out)                 # names the next seam

    def test_zero_markers_prints_count_zero(self):
        self._mk_task("alpha", phase="verify")       # bodies carry no marker lines
        out, _, code = self._run("v13", "alpha", "--decide")
        self.assertEqual(code, 0)
        self.assertIn("NEEDS YOUR JUDGMENT (0)", out)
        self.assertIn("ENGINE FACTS", out)

    def test_bare_decide_uses_active_task(self):
        self._mk_task("alpha", phase="verify", sec6=SEC6_MARKER)  # new-task sets active
        out, _, code = self._run("--decide")
        self.assertEqual(code, 0)
        self.assertIn("alpha", out)
        self.assertIn("NEEDS YOUR JUDGMENT", out)

    def test_bare_decide_no_active_task_refused(self):
        before = self._hash_state()
        out, err, code = self._run("--decide")       # no tasks exist at all
        self.assertEqual(code, 1)
        self.assertIn("no_active_task", err)
        self.assertEqual(self._hash_state(), before)

    def test_recorded_seam_shows_gate_from_state(self):
        self._mk_task("alpha", phase="verify", sec6=SEC6_MARKER)
        add.main(["gate", "PASS", "alpha"])          # -> phase done, gate PASS
        out, _, code = self._run("v13", "alpha", "--decide")
        self.assertEqual(code, 0)
        self.assertIn("no decision pending", out)
        self.assertIn("PASS", out)

    def test_decide_json_one_dict_frozen_keys(self):
        self._mk_task("alpha", phase="verify", sec6=SEC6_MARKER)
        out, _, code = self._run("v13", "alpha", "--decide", "--json")
        self.assertEqual(code, 0)
        d = json.loads(out)
        self.assertIsInstance(d, dict)
        self.assertEqual(set(d.keys()),
                         {"seam", "milestone", "task", "phase", "gate",
                          "judgment", "facts", "unlocks", "decide", "plan"})
        self.assertEqual(d["seam"], "gate")
        self.assertEqual(d["task"], "alpha")
        self.assertEqual(d["judgment"][0]["marker"], "[~]")
        self.assertEqual(d["judgment"][0]["section"], 6)
        self.assertEqual(d["judgment"][0]["text"], SEC6_MARKER)   # byte-identical
        self.assertEqual(set(d["facts"].keys()), {"phase", "gate", "deps", "tests"})

    def test_unconfirmed_item_marker_extracted(self):
        # third prefix of the frozen grammar: `- [ ]` (unconfirmed item); `- [x]` never matches
        sec6 = "  - [x] all tests pass\n  - [ ] a person reviewed and approved the change"
        self._mk_task("alpha", phase="verify", sec6=sec6)
        out, _, code = self._run("v13", "alpha", "--decide", "--json")
        self.assertEqual(code, 0)
        d = json.loads(out)
        self.assertEqual(len(d["judgment"]), 1)
        self.assertEqual(d["judgment"][0]["marker"], "[ ]")
        self.assertIn("a person reviewed", d["judgment"][0]["text"])

    def test_decide_json_on_milestone_keys_stable(self):
        # milestone altitude keeps the SAME frozen key set, task null
        self._mk_task("alpha", phase="verify")
        out, _, code = self._run("v13", "--decide", "--json")
        self.assertEqual(code, 0)
        d = json.loads(out)
        self.assertEqual(set(d.keys()),
                         {"seam", "milestone", "task", "phase", "gate",
                          "judgment", "facts", "unlocks", "decide", "plan"})
        self.assertIsNone(d["task"])
        self.assertEqual(d["plan"], [])              # milestone altitude carries an empty plan
        self.assertIn("alpha", d["decide"])

    # ---- BUILD PLAN block (plan-in-report): the §3 build-strategy plan-of-action ----
    # A filled §3 Build-strategy sub-block: the plan-of-action fields the freeze surfaces.
    _BS_FILLED = ("the-frozen-shape-text\n\n"
                  "Scope (may touch): add.py gate-udd.md\n"
                  "Strategy (ordered batches): 1. red 2. green 3. sync\n"
                  "Persona (required): generic\n"
                  "Spawn isolation (default): inline\n\n"
                  "Status: DRAFT")

    def test_build_plan_block_renders_at_freeze(self):
        """M1: front seam + a filled §3 Build-strategy -> a BUILD PLAN block with the fields."""
        self._mk_task("alpha", phase="plan", sec3=self._BS_FILLED)
        out, _, code = self._run("v13", "alpha", "--decide", "--plain")
        self.assertEqual(code, 0)
        self.assertIn("BUILD PLAN", out)
        region = out[out.index("BUILD PLAN"):]
        for frag in ("Scope", "add.py gate-udd.md",
                     "Strategy", "1. red 2. green 3. sync",
                     "Persona", "generic", "Spawn isolation", "inline"):
            self.assertIn(frag, region)
        # additive — the §3 verbatim dump still renders (before the block)
        self.assertIn("CONTRACT (§3 verbatim)", out)
        self.assertLess(out.index("CONTRACT (§3 verbatim)"), out.index("BUILD PLAN"))

    def test_build_plan_json_key_holds_filled_fields(self):
        """M2: the JSON `plan` key is a list of {label, value} for each FILLED field."""
        self._mk_task("alpha", phase="plan", sec3=self._BS_FILLED)
        out, _, code = self._run("v13", "alpha", "--decide", "--json")
        self.assertEqual(code, 0)
        plan = json.loads(out)["plan"]
        self.assertTrue(all(set(e) == {"label", "value"} for e in plan))
        labels = [e["label"] for e in plan]
        self.assertEqual(labels, ["Scope (may touch)", "Strategy (ordered batches)",
                                  "Persona (required)", "Spawn isolation (default)"])
        self.assertEqual(plan[0]["value"], "add.py gate-udd.md")

    def test_build_plan_no_field_bleed(self):
        """A field value must NOT swallow the next field's label/text — even when that
        next label isn't a `Word (paren):` form (Approach→Data strategy, Spawn→Known-problem
        fixes). Reproduces the real §3 sub-block the dogfood surfaced."""
        sec3 = ("shape\n\n"
                "Scope (may touch): add.py\n"
                "Strategy (ordered batches): 1. a 2. b\n"
                "Approach (domain strategy): reuse the extractor\n"
                "Data strategy: two list keys\n"
                "Pattern: additive extension\n"
                "Optimization stance: legibility-first\n"
                "Persona (required): generic\n"
                "Spawn isolation (default): inline\n"
                "Known-problem fixes: re-pin both asserts\n\n"
                "Status: DRAFT")
        self._mk_task("alpha", phase="plan", sec3=sec3)
        out, _, code = self._run("v13", "alpha", "--decide", "--json")
        self.assertEqual(code, 0)
        plan = {e["label"]: e["value"] for e in json.loads(out)["plan"]}
        self.assertEqual(plan["Approach (domain strategy)"], "reuse the extractor")
        self.assertEqual(plan["Spawn isolation (default)"], "inline")
        self.assertEqual(plan["Known-problem fixes"], "re-pin both asserts")
        # the ADR facets (Data strategy · Pattern · Optimization stance) are NOT plan fields
        for adr in ("Data strategy", "Pattern", "Optimization stance"):
            self.assertNotIn(adr, plan)

    def test_build_plan_skips_placeholder_fields(self):
        """M3: an unfilled placeholder (`<…>`) or the bare `./src/` Scope default is skipped."""
        sec3 = ("shape\n\n"
                "Scope (may touch): ./src/\n"
                "Persona (required): <name the persona>\n"
                "Spawn isolation (default): inline\n\n"
                "Status: DRAFT")
        self._mk_task("alpha", phase="plan", sec3=sec3)
        out, _, code = self._run("v13", "alpha", "--decide", "--json")
        self.assertEqual(code, 0)
        labels = [e["label"] for e in json.loads(out)["plan"]]
        self.assertEqual(labels, ["Spawn isolation (default)"])   # only the real field survives

    def test_build_plan_strips_trailing_template_hint(self):
        """M1/M3: a trailing `   <hint>` on a filled field is stripped from the surfaced value."""
        sec3 = ("shape\n\n"
                "Scope (may touch): add.py   <the scope hint text>\n\n"
                "Status: DRAFT")
        self._mk_task("alpha", phase="plan", sec3=sec3)
        out, _, code = self._run("v13", "alpha", "--decide", "--json")
        self.assertEqual(code, 0)
        plan = json.loads(out)["plan"]
        self.assertEqual(plan, [{"label": "Scope (may touch)", "value": "add.py"}])

    def test_build_plan_empty_omits_block(self):
        """R1: no filled Build-strategy field -> plan == [] and no BUILD PLAN header, exit 0."""
        self._mk_task("alpha", phase="plan", sec3="just-a-shape\n\nStatus: DRAFT")
        out, _, code = self._run("v13", "alpha", "--decide", "--plain")
        self.assertEqual(code, 0)
        self.assertNotIn("BUILD PLAN", out)
        jout, _, _ = self._run("v13", "alpha", "--decide", "--json")
        self.assertEqual(json.loads(jout)["plan"], [])

    def test_build_plan_absent_at_gate_seam(self):
        """M4/R2: a filled Build-strategy at the verify (gate) seam -> no block, plan == []."""
        self._mk_task("alpha", phase="verify", sec3=self._BS_FILLED)
        out, _, code = self._run("v13", "alpha", "--decide", "--plain")
        self.assertEqual(code, 0)
        self.assertNotIn("BUILD PLAN", out)
        jout, _, _ = self._run("v13", "alpha", "--decide", "--json")
        self.assertEqual(json.loads(jout)["plan"], [])

    def test_build_plan_render_writes_nothing(self):
        """R3: the plan-bearing digest is PURE — no writes on the front-seam path."""
        self._mk_task("alpha", phase="plan", sec3=self._BS_FILLED)
        before_state, before_files = self._hash_state(), self._file_set()
        for argv in (("v13", "alpha", "--decide"), ("v13", "alpha", "--decide", "--json")):
            _, _, code = self._run(*argv)
            self.assertEqual(code, 0)
        self.assertEqual(self._hash_state(), before_state)
        self.assertEqual(self._file_set(), before_files)

    def test_decide_plain_ascii_no_ansi(self):
        self._mk_task("alpha", phase="verify", sec6=SEC6_MARKER)
        out, _, code = self._run("v13", "alpha", "--decide", "--plain")
        self.assertEqual(code, 0)
        self.assertNotIn("\x1b[", out)

    # ---- rollup DECIDE NEXT footer -----------------------------------------
    def test_footer_done_milestone_fold_archive(self):
        self._mk_task("alpha", phase="verify")
        add.main(["gate", "PASS", "alpha"])
        _meet_exit_criteria("v13")   # v20 goal-gate: criteria met so footer shows archive path
        out, _, code = self._run("v13")
        self.assertEqual(code, 0)
        self.assertIn("DECIDE NEXT", out)
        self.assertIn("consolidate", out)
        self.assertIn("archive-milestone", out)

    def test_footer_names_seam_blocked_task(self):
        self._mk_task("alpha", phase="verify")
        out, _, code = self._run("v13")
        self.assertEqual(code, 0)
        footer = out[out.index("DECIDE NEXT"):]
        self.assertIn("alpha", footer)
        self.assertIn("gate", footer)

    def test_footer_hard_stop_wins(self):
        self._mk_task("alpha", phase="verify")
        add.main(["gate", "HARD-STOP", "alpha"])
        self._mk_task("beta", phase="plan")           # also awaiting an approval
        out, _, code = self._run("v13")
        self.assertEqual(code, 0)
        footer = out[out.index("DECIDE NEXT"):]
        self.assertIn("alpha", footer)
        self.assertIn("HARD-STOP", footer)

    def test_footer_run_in_progress(self):
        self._mk_task("alpha")                   # create at ground (no phase jump yet)
        self._freeze("alpha")                    # freeze-gate-universal sweep
        add.main(["phase", "build", "alpha"])    # now allowed by frozen §3
        out, _, code = self._run("v13")
        self.assertEqual(code, 0)
        footer = out[out.index("DECIDE NEXT"):]
        self.assertIn("run in progress", footer)
        self.assertIn("alpha", footer)

    def test_decide_on_milestone_renders_footer_block_only(self):
        self._mk_task("alpha", phase="verify")
        out, _, code = self._run("v13", "--decide")
        self.assertEqual(code, 0)
        self.assertIn("DECIDE NEXT", out)
        self.assertNotIn("EXIT CRITERIA", out)       # no rollup table around it

    # ---- purity + stability -------------------------------------------------
    def test_decide_writes_nothing(self):
        self._mk_task("alpha", phase="verify", sec6=SEC6_MARKER)
        before_state, before_files = self._hash_state(), self._file_set()
        for argv in (("v13", "alpha", "--decide"),
                     ("v13", "--decide"),
                     ("v13", "alpha", "--decide", "--json")):
            _, _, code = self._run(*argv)
            self.assertEqual(code, 0)   # purity must hold on SUCCESSFUL paths
        self.assertEqual(self._hash_state(), before_state)
        self.assertEqual(self._file_set(), before_files)

    def test_existing_outputs_stable(self):
        self._mk_task("alpha", phase="verify")
        drill, _, code = self._run("v13", "alpha")   # plain drill: NO footer, no digest
        self.assertEqual(code, 0)
        self.assertNotIn("DECIDE NEXT", drill)
        rollup, _, code = self._run("v13")
        self.assertEqual(code, 0)
        # v9 landmarks intact; the footer is APPENDED (after the LEARNINGS block)
        for landmark in ("VERDICT", "EXIT CRITERIA", "LEARNINGS"):
            self.assertIn(landmark, rollup)
        self.assertLess(rollup.index("LEARNINGS"), rollup.index("DECIDE NEXT"))


class ReportTemplateSurfaceTest(unittest.TestCase):
    """M5: the ONE human-gate report shape (gate-udd.md) names the BUILD PLAN block."""

    def test_report_template_documents_build_plan(self):
        skill = Path(add.__file__).resolve().parent.parent / "skill" / "add"
        tmpl = skill / "gate-udd.md"
        self.assertTrue(tmpl.is_file(), f"missing {tmpl}")
        self.assertIn("BUILD PLAN", tmpl.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
