#!/usr/bin/env python3
"""Red/green tests for the §7 Decisions (ADR) audit lint + the docs (milestone adr-at-observe, task 3).

`add.py audit` fires `adr_record_missing` when an already-audited task (done/observe or gated) carries
a §7 "### Decisions (ADR)" block STILL holding its bare "<harvested at done…>" placeholder — the
harvest never ran. GRANDFATHER: a §7 with no block is legacy (never flagged). The probe is the
BARE-LINE regex (a substring in harvested prose is not a false positive). PURE read. The observe
guide + book + glossary document the record (byte-identical across their 3 trees).

Run: python3 -m unittest test_adr_audit -v
"""
import contextlib
import hashlib
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
PLACEHOLDER = ("<harvested at done from §1/§3/§5/§6 — do not hand-edit; one actor-tagged line "
               "per decision, refilled only while this placeholder stands>")

# the 3 doc/skill surfaces, each as its (canonical, dogfood, bundle) trio
OBSERVE_GUIDE = (ADD_METHOD / "skill/add/phases/7-observe.md",
                 REPO / ".claude/skills/add/phases/7-observe.md",
                 ADD_METHOD / "src/add_method/_bundled/skill/add/phases/7-observe.md")
BOOK_LOOP = (ADD_METHOD / "docs/09-the-loop.md",
             REPO / ".add/docs/09-the-loop.md",
             ADD_METHOD / "src/add_method/_bundled/docs/09-the-loop.md")
GLOSSARY = (ADD_METHOD / "docs/appendix-c-glossary.md",
            REPO / ".add/docs/appendix-c-glossary.md",
            ADD_METHOD / "src/add_method/_bundled/docs/appendix-c-glossary.md")


def _md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


class AdrAuditTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-adra-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "demo"])
        self._quiet(["lock", "--force"])

    def tearDown(self):
        os.chdir(self._cwd)

    @staticmethod
    def _quiet(argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            add.main(argv)

    def _state(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())

    def _path(self, slug="t"):
        return Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"

    def _gated_task(self, slug="t"):
        """A scaffolded full task, gated PASS (the harvest runs at gate -> §7 harvested)."""
        self._quiet(["new-task", slug])
        self._quiet(["phase", "verify", slug])
        self._quiet(["gate", "PASS", slug])

    def _adr_findings(self, slug=None):
        _checked, findings = add._audit_findings(Path(self.tmp) / ".add", self._state())
        return [x for x in findings
                if x["code"] == "adr_record_missing" and (slug is None or x["task"] == slug)]

    def _reset_adr_to_placeholder(self, slug="t"):
        p = self._path(slug)
        txt = re.sub(r"(### Decisions \(ADR\)\n).*?(\n\n### Spec delta)",
                     r"\1" + PLACEHOLDER + r"\2", p.read_text(), flags=re.S)
        p.write_text(txt, encoding="utf-8")

    # ── the lint fires on a gated task whose §7 block was never harvested ─────────────────
    def test_lint_fires_on_unharvested_block(self):
        self._gated_task()
        self._reset_adr_to_placeholder()              # simulate a record that never harvested
        self.assertTrue(self._adr_findings("t"), "adr_record_missing fires on an unharvested §7 block")

    def test_unharvested_is_a_real_finding_not_a_soft_surface(self):
        # the design call: adr_record_missing rides in findings[] (drives exit 1), NOT in the
        # measure-not-block guarantee_lints[] bucket (exit 0). --json isolates that distinction.
        self._gated_task()
        self._reset_adr_to_placeholder()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.suppress(SystemExit):
            add.main(["audit", "--json"])
        data = json.loads(buf.getvalue())
        self.assertIn("adr_record_missing", [f["code"] for f in data["findings"]],
                      "adr_record_missing is a real finding (drives the exit-1 CI gate)")
        self.assertNotIn("adr_record_missing", json.dumps(data.get("guarantee_lints", {})),
                         "it is NOT a measure-not-block surface")

    # ── a harvested block passes; audit is pure ──────────────────────────────────────────
    def test_harvested_block_passes_and_audit_is_pure(self):
        self._gated_task()
        before = _md5(self._path())
        self.assertEqual(self._adr_findings("t"), [], "a harvested §7 block raises no finding")
        with contextlib.redirect_stdout(io.StringIO()):
            with contextlib.suppress(SystemExit):
                add.main(["audit"])
        self.assertEqual(_md5(self._path()), before, "audit is a pure read — the file is unchanged")

    # ── a legacy task with no §7 ADR block is grandfathered ──────────────────────────────
    def test_legacy_no_block_grandfathered(self):
        self._quiet(["new-task", "u"])
        p = self._path("u")                            # strip the §7 ADR block (pre-feature scaffold)
        txt = re.sub(r"### Decisions \(ADR\)\n.*?\n\n(### Spec delta)", r"\1", p.read_text(), flags=re.S)
        p.write_text(txt, encoding="utf-8")
        self.assertNotIn("### Decisions (ADR)", p.read_text())
        self._quiet(["phase", "verify", "u"])
        self._quiet(["gate", "PASS", "u"])
        self.assertEqual(self._adr_findings("u"), [], "a §7 with no ADR block is legacy — never flagged")

    # ── harvested prose quoting the placeholder is not a false positive ──────────────────
    def test_substring_in_prose_no_false_positive(self):
        self._gated_task()
        p = self._path()                               # add a harvested line that CONTAINS the substring
        txt = p.read_text().replace(
            "### Decisions (ADR)\n",
            "### Decisions (ADR)\n- [AI] build — strategy used: quoted the <harvested at done> token\n", 1)
        p.write_text(txt, encoding="utf-8")
        self.assertIn("<harvested at done", p.read_text())   # substring present...
        self.assertEqual(self._adr_findings("t"), [], "...but no bare placeholder line -> no finding")

    # ── the record is documented + byte-identical across the 3 trees of each surface ─────
    def test_docs_carry_adr_term_and_parity(self):
        for name, trio in (("observe guide", OBSERVE_GUIDE), ("book loop", BOOK_LOOP), ("glossary", GLOSSARY)):
            canon = trio[0].read_text(encoding="utf-8")
            self.assertIn("Decisions (ADR)", canon, f"{name} must document the §7 Decisions (ADR) record")
            self.assertEqual(len({_md5(p) for p in trio}), 1, f"{name}: the 3 trees must be byte-identical")


if __name__ == "__main__":
    unittest.main(verbosity=2)
