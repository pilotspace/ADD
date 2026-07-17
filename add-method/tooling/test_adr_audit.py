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

# the 3 git-tracked mirror trees per surface. Skill guide: canonical · .claude dogfood · bundle.
# Book/glossary: canonical · repo-ROOT mirror (test_book_parity) · bundle — NOT .add/docs/, which is
# a gitignored local install artifact absent in CI.
OBSERVE_GUIDE = (ADD_METHOD / "skill/add/phases/verify.md",
                 REPO / ".claude/skills/add/phases/verify.md",
                 ADD_METHOD / "src/add_method/_bundled/skill/add/phases/verify.md")
BOOK_LOOP = (ADD_METHOD / "docs/09-the-loop.md",
             REPO / "09-the-loop.md",
             ADD_METHOD / "src/add_method/_bundled/docs/09-the-loop.md")
GLOSSARY = (ADD_METHOD / "docs/appendix-c-glossary.md",
            REPO / "appendix-c-glossary.md",
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

    # ── the record is documented + byte-identical across the 3 trees of each surface ─────
    def test_docs_carry_adr_term(self):
        for name, trio in (("observe guide", OBSERVE_GUIDE), ("book loop", BOOK_LOOP), ("glossary", GLOSSARY)):
            canon = trio[0].read_text(encoding="utf-8")
            self.assertIn("Decisions (ADR)", canon, f"{name} must document the §7 Decisions (ADR) record")


if __name__ == "__main__":
    unittest.main(verbosity=2)
