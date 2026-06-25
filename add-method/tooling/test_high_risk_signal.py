#!/usr/bin/env python3
"""Red/green tests for the mechanized high-risk guard (task high-risk-signal, v14).

run.md's guard becomes engine-enforced for the DECLARED case: a TASK.md header
carrying `risk: high` without `autonomy: conservative` is a pure token
contradiction — `gate` refuses to complete it (state untouched) and `audit`
flags `unguarded_high_risk_auto` on records. Judgment of WHAT is high-risk
stays human (the declaration, reviewed at the freeze); the engine never
classifies scope. HARD-STOP is never blocked. Run:
    python3 -m unittest test_high_risk_signal -v
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
import test_gate_audit as tga   # frozen record shapes — one source of truth

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BUNDLE = HERE.parent / "src" / "add_method" / "_bundled"

# prose-accord anchors (the guide must state what the engine now does)
RUN_MD_ANCHOR = "the engine refuses the declared combination"
TMPL_ANCHOR = "risk: high"

WAIVER = ["--owner", "Tin", "--ticket", "T-1", "--expires", "2026-07-01"]


class _Board(unittest.TestCase):
    """A live board arranged through the real CLI (engine input contracts)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-hrs-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["init", "--name", "demo"])
            add.main(["new-milestone", "v1", "--title", "T", "--goal", "g"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ---- helpers ----------------------------------------------------------
    def _root(self) -> Path:
        return self.tmp / ".add"

    def _task_md(self, slug: str) -> Path:
        return self._root() / "tasks" / slug / "TASK.md"

    def _mk_verify_task(self, slug: str, header_extra: str = ""):
        """A task advanced to verify, with optional tokens appended to its
        slug header line (e.g. ' · risk: high · autonomy: conservative')."""
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["new-task", slug, "--title", slug])
            add.main(["phase", "verify", slug])
        if header_extra:
            p = self._task_md(slug)
            text = p.read_text(encoding="utf-8")
            text = re.sub(rf"^(slug: {slug}.*)$", rf"\1{header_extra}",
                          text, count=1, flags=re.M)
            p.write_text(text, encoding="utf-8")

    def _gate(self, *args):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["gate", *args])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _audit_json(self):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(["audit", "--json"])
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return json.loads(buf.getvalue()), code

    def _state_snapshot(self):
        return hashlib.sha256(
            (self._root() / "state.json").read_bytes()).hexdigest()

    def _assert_refused(self, out, err, code, slug):
        self.assertNotEqual(code, 0, "an unguarded high-risk gate must refuse")
        self.assertIn("unguarded_high_risk_auto", out + err)
        st = json.loads((self._root() / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(st["tasks"][slug]["phase"], "verify",
                         "refusal must leave the phase untouched")
        self.assertEqual(st["tasks"][slug]["gate"], "none",
                         "refusal must record no gate")


class GateRefusalTest(_Board):
    def test_gate_refuses_default_auto(self):
        # absent autonomy token = auto (v7 default) -> unguarded by design
        self._mk_verify_task("alpha", " · risk: high")
        before = self._state_snapshot()
        out, err, code = self._gate("PASS", "alpha")
        self._assert_refused(out, err, code, "alpha")
        self.assertEqual(self._state_snapshot(), before,
                         "refusal must be a pure no-op on state.json")

    def test_gate_refuses_explicit_auto(self):
        self._mk_verify_task("alpha", " · risk: high · autonomy: auto")
        out, err, code = self._gate("PASS", "alpha")
        self._assert_refused(out, err, code, "alpha")

    def test_gate_refuses_risk_accepted_bypass(self):
        # a fully-signed waiver still cannot complete an unguarded high-risk task
        self._mk_verify_task("alpha", " · risk: high")
        out, err, code = self._gate("RISK-ACCEPTED", "alpha", *WAIVER)
        self._assert_refused(out, err, code, "alpha")

    def test_gate_hard_stop_always_allowed(self):
        # never block the stop path
        self._mk_verify_task("alpha", " · risk: high")
        out, err, code = self._gate("HARD-STOP", "alpha")
        self.assertEqual(code, 0, out + err)
        st = json.loads((self._root() / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(st["tasks"]["alpha"]["gate"], "HARD-STOP")

    def test_gate_allows_guarded(self):
        self._mk_verify_task("alpha", " · risk: high · autonomy: conservative")
        out, err, code = self._gate("PASS", "alpha")
        self.assertEqual(code, 0, out + err)
        st = json.loads((self._root() / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(st["tasks"]["alpha"]["phase"], "done")
        self.assertEqual(st["tasks"]["alpha"]["gate"], "PASS")

    def test_gate_ordinary_unaffected(self):
        # no risk token -> exactly today's behavior (regression guard)
        self._mk_verify_task("alpha")
        out, err, code = self._gate("PASS", "alpha")
        self.assertEqual(code, 0, out + err)
        st = json.loads((self._root() / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(st["tasks"]["alpha"]["phase"], "done")


class AuditFindingTest(_Board):
    """F7: the record-shape side, enforced in CI by audit-ci."""

    def _done_high_risk(self, slug, record):
        """A guarded high-risk task gated PASS, with §3/§6 we control."""
        self._mk_verify_task(slug, " · risk: high · autonomy: conservative")
        out, err, code = self._gate("PASS", slug)
        self.assertEqual(code, 0, out + err)
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        header_line = next(l for l in text.splitlines() if l.startswith("slug:"))
        p.write_text("\n".join([
            f"# TASK: {slug}", header_line, "",
            "## 1 · SPECIFY", "Feature: f", "",
            "## 2 · SCENARIOS", "(none)", "",
            "## 3 · CONTRACT", "```\nshape\n```", "", tga.GOOD3, "",
            "## 4 · TESTS", "plan", "",
            "## 5 · BUILD", "code", "",
            "## 6 · VERIFY", tga._sec6(record=record), "",
            "## 7 · OBSERVE", "watch", "",
        ]), encoding="utf-8")

    def _codes(self, d):
        return [x["code"] for x in d["findings"]]

    def test_audit_flags_tampered_header(self):
        # gate passed GUARDED, then the header's dial was stripped post-gate
        self._done_high_risk("alpha", tga.REC_HUMAN)
        p = self._task_md("alpha")
        p.write_text(p.read_text(encoding="utf-8")
                     .replace(" · autonomy: conservative", ""), encoding="utf-8")
        d, code = self._audit_json()
        self.assertEqual(code, 1)
        self.assertIn("unguarded_high_risk_auto", self._codes(d))

    def test_audit_flags_auto_reviewed_record(self):
        # declared conservative, but the GATE RECORD names the auto-gate
        self._done_high_risk("alpha", tga.REC_AUTO)
        d, code = self._audit_json()
        self.assertEqual(code, 1)
        self.assertIn("unguarded_high_risk_auto", self._codes(d))

    def test_audit_silent_guarded_human(self):
        self._done_high_risk("alpha", tga.REC_HUMAN)
        d, code = self._audit_json()
        self.assertNotIn("unguarded_high_risk_auto", self._codes(d))
        self.assertEqual(code, 0, d)

    def test_audit_silent_ordinary_auto(self):
        # the live-board shape: ordinary tasks auto-resolve freely (45 stay clean)
        self._mk_verify_task("alpha")
        out, err, code = self._gate("PASS", "alpha")
        self.assertEqual(code, 0, out + err)
        p = self._task_md("alpha")
        p.write_text("\n".join([
            "# TASK: alpha", "",
            "## 1 · SPECIFY", "Feature: f", "",
            "## 2 · SCENARIOS", "(none)", "",
            "## 3 · CONTRACT", "```\nshape\n```", "", tga.GOOD3, "",
            "## 4 · TESTS", "plan", "",
            "## 5 · BUILD", "code", "",
            "## 6 · VERIFY", tga._sec6(record=tga.REC_AUTO), "",
            "## 7 · OBSERVE", "watch", "",
        ]), encoding="utf-8")
        d, code = self._audit_json()
        self.assertNotIn("unguarded_high_risk_auto", self._codes(d))
        self.assertEqual(code, 0, d)


class ProseAccordTest(unittest.TestCase):
    """The guides must state what the engine now does — synced ×3."""

    def _assert_triplet(self, rel: tuple[str, ...], anchor: str):
        canon = HERE.parent.joinpath(*rel)
        self.assertIn(anchor, canon.read_text(encoding="utf-8"), canon)
        if rel[:2] == ("skill", "add"):   # skill files dogfood under .claude/skills
            dogfood = REPO / ".claude" / "skills" / "add" / Path(*rel[2:])
        else:                              # tooling files dogfood under .add
            dogfood = REPO / ".add" / Path(*rel)
        for twin in (dogfood, BUNDLE.joinpath(*rel)):
            self.assertEqual(canon.read_bytes(), twin.read_bytes(),
                             f"divergence: {twin}")

    def test_run_md_states_mechanized_guard(self):
        self._assert_triplet(("skill", "add", "run.md"), RUN_MD_ANCHOR)

    def test_template_documents_risk_token(self):
        self._assert_triplet(("tooling", "templates", "TASK.md.tmpl"), TMPL_ANCHOR)


if __name__ == "__main__":
    unittest.main(verbosity=2)
