#!/usr/bin/env python3
"""Red/green tests for persona-schema-hardening (fast task, self-improving-loop).

CONTRACT (§3 FROZEN v1): a new PURE/NO-EXEC predicate `_persona_quality_warnings(md_text)`
mechanically measures the two template disciplines the presence-based schema check can't
see — (A) a `flow:` value outside design|build|advisor (a typo'd flow is loaded by no
surface), (B) a bare `<…>` placeholder outside backtick spans and HTML comments (a
half-filled template copy). `add.py check` surfaces each finding as a WARN
`persona_quality: …` on REAL (non-`_`-prefixed) personas — never a failure
(measure-not-block). Flow values single-sourced as constants.PERSONA_FLOW_VALUES.
One test per §1 Must/Reject + the Accept line. Run:
python3 -m unittest test_persona_schema_hardening -v
"""
from __future__ import annotations

import inspect
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import add

TOOLING = Path(__file__).resolve().parent
REPO_ROOT = TOOLING.parent.parent
DOGFOOD_PERSONAS = REPO_ROOT / ".add" / "personas"
# network/spawn/file-IO tokens a PURE NO-EXEC predicate must never contain
FORBIDDEN_EXEC = ("socket", "urllib", "requests", "subprocess", "Popen",
                  "os." + "system", "spawn", "open(")


def _persona(flow=None, body_extra=""):
    fm = "---\nname: X\nvibe: y\n"
    if flow is not None:
        fm += f"flow: {flow}\n"
    fm += "---\n"
    return (fm + "## Identity\nA specialist.\n\n## Critical Rules\n- rule\n\n"
            "## Default Requirement\nreq.\n\n## Success Metrics\n- metric\n" + body_extra)


class QualityPredicateTest(unittest.TestCase):
    # §1 Must: clean persona -> []
    def test_clean_persona_no_findings(self):
        self.assertEqual(add._persona_quality_warnings(_persona(flow="build")), [])

    # §1 Accept (Finding A): a typo'd flow value is named
    def test_flow_typo_warns(self):
        findings = add._persona_quality_warnings(_persona(flow="builder"))
        self.assertTrue(any("builder" in f for f in findings),
                        f"a bad flow value must be named in the finding: {findings}")

    # §1 Must: comma-separated valid values stay clean
    def test_multi_flow_valid_clean(self):
        self.assertEqual(add._persona_quality_warnings(_persona(flow="design, advisor")), [])

    # §1 Reject absence_is_conformant: no flow: line -> no Finding A
    def test_absent_flow_is_clean(self):
        self.assertEqual(add._persona_quality_warnings(_persona(flow=None)), [])

    # §1 Accept (Finding B): a bare <…> placeholder is flagged
    def test_bare_placeholder_warns(self):
        findings = add._persona_quality_warnings(
            _persona(flow="build", body_extra="- <another concrete capability>\n"))
        self.assertTrue(any("placeholder" in f for f in findings),
                        f"a bare <…> placeholder must be flagged: {findings}")

    # §1 Must (Finding B strip rules): backticked and commented <…> are content, not placeholders
    def test_backticked_and_commented_are_clean(self):
        extra = ("- documented tag `<persona>` and path `.add/personas/<slug>.md`\n"
                 "<!-- a comment mentioning <slug> placeholders is fine -->\n")
        self.assertEqual(
            add._persona_quality_warnings(_persona(flow="build", body_extra=extra)), [])

    # §1 Reject no_exec_violation: PURE predicate — no IO/network/spawn tokens in its source
    def test_predicate_pure_no_exec(self):
        src = inspect.getsource(add._persona_quality_warnings)
        for tok in FORBIDDEN_EXEC:
            self.assertNotIn(tok, src, f"PURE predicate must not contain '{tok}'")

    # §1 Must: flow values single-sourced from constants.PERSONA_FLOW_VALUES
    def test_flow_values_single_source(self):
        from add_engine import constants
        self.assertEqual(constants.PERSONA_FLOW_VALUES, ("design", "build", "advisor"))
        self.assertIn("PERSONA_FLOW_VALUES", constants.__all__)
        src = inspect.getsource(add._persona_quality_warnings)
        self.assertIn("PERSONA_FLOW_VALUES", src,
                      "the predicate must read the constant, not a duplicate literal")


class CheckWiringTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-persona-quality-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        add.main(["init", "--name", "demo"])

    def _run_check(self):
        buf = io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf):
                add.main(["check"])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return buf.getvalue(), code

    # §1 Accept end-to-end + §1 Reject measure_not_block: WARN surfaces, check still exits 0
    def test_check_emits_warn_not_fail(self):
        (Path(self.tmp) / ".add" / "personas" / "sloppy.md").write_text(
            _persona(flow="builder", body_extra="- <another concrete capability>\n"),
            encoding="utf-8")
        out, code = self._run_check()
        self.assertIn("persona_quality", out, "check must surface the quality findings")
        self.assertIn("sloppy", out, "check must name the offending persona slug")
        self.assertIn("builder", out, "the flow finding must name the bad value")
        self.assertEqual(code, 0, "a quality finding must NOT block check (measure-not-block)")

    # the seeded `_template.md` (all placeholders by design) must NOT be quality-warned
    def test_seeded_template_not_warned(self):
        out, _ = self._run_check()
        self.assertNotIn("persona_quality", out,
                         "a fresh project (template only) must emit no quality WARNs")


class DogfoodCleanTest(unittest.TestCase):
    # §1 Accept: the 6 real dogfood personas produce zero quality findings
    def test_dogfood_personas_zero_quality_warns(self):
        files = [p for p in sorted(DOGFOOD_PERSONAS.glob("*.md"))
                 if not p.stem.startswith("_")]
        self.assertGreaterEqual(len(files), 6, "expected the dogfood persona roster")
        for p in files:
            findings = add._persona_quality_warnings(p.read_text(encoding="utf-8"))
            self.assertEqual(findings, [], f"{p.name} must be quality-clean: {findings}")


if __name__ == "__main__":
    unittest.main()
