#!/usr/bin/env python3
"""Red/green tests for the project-extensible sensitivity glossary (task sensitivity-glossary).

CONTRACT (frozen @ v1):
  _project_sensitivity_values(root) -> base _SENSITIVITY_VALUES ∪ domain tokens parsed from
     GLOSSARY.md "## Sensitivity classes" section ("- <token>: …"/"- <token> — …" -> token.lower());
     PURE, deduped, base-first; FAIL-SAFE (no file/section/unreadable -> base only, never empty).
  _task_sensitivity(hdr, valid=None) -> member|None|"?" — membership vs `valid` (default base).
  add.py freeze: a header sensitivity in base ∪ project freezes; only a token in NEITHER -> sensitivity_invalid.
  add.py init: seeds a "## Sensitivity classes" section into GLOSSARY.md (the base four).
  add.py check: a MEASURE-only nudge when a project declares no domain classes (exit 0).

Render-blind: assertions read returned values / printed lines / file surface.
Run: python3 -m unittest test_sensitivity_glossary -v
"""
import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

_DRAFT_FLAGGED = (
    "\n```\nGET /widget  body: { id }\n  200 -> { ok: true }\n```\n\n"
    "Status: DRAFT\n"
    "Least-sure flag surfaced at freeze:\n"
    "  ⚠ [contract] the id encoding is the least-sure part — cost if wrong: a reparse.\n"
)


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-sensglossary-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(io.StringIO()):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue() + err.getvalue(), code

    def _root(self):
        return self.tmp / ".add"

    def _glossary(self):
        return self._root() / "GLOSSARY.md"

    def _add_domain_class(self, token, defn="domain risk class"):
        """Append a domain class line under a '## Sensitivity classes' section (create if absent)."""
        p = self._glossary()
        text = p.read_text(encoding="utf-8")
        if "## Sensitivity classes" not in text:
            text += "\n\n## Sensitivity classes\n"
        text += f"- {token}: {defn}\n"
        p.write_text(text, encoding="utf-8")

    def _task_md(self, slug):
        return self._root() / "tasks" / slug / "PLAN.md"

    def _new_task_at_contract(self, slug="t"):
        self._silent("lock", "--force")
        self._silent("new-milestone", "m", "--goal", "g", "--stage", "mvp")
        self._silent("new-task", slug, "--title", "Feature")
        self._silent("phase", "plan", slug)          # plan-phase-core: "contract" collapsed into "plan"
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        # plan-phase-core: §3 PLAN now holds ### Grounding + ### Contract + ### Build-strategy —
        # replace only the ### Contract sub-block body, leaving Grounding/Build-strategy intact.
        new = re.sub(r"(### Contract[^\n]*\n).*?(\n### Build-strategy)",
                     lambda m: m.group(1) + _DRAFT_FLAGGED + m.group(2), text, count=1, flags=re.S)
        new = re.sub(r"(?m)^Boundary: <[^\n]*$",
                     "Boundary: none — no external input", new, count=1)
        p.write_text(new, encoding="utf-8")

    def _set_sensitivity(self, slug, token):
        p = self._task_md(slug)
        text = p.read_text(encoding="utf-8")
        p.write_text(re.sub(r"(?m)^(slug:.*)$", r"\1 · sensitivity: " + token, text, count=1),
                     encoding="utf-8")

    def _section3(self, slug):
        return add._phase_spans(self._task_md(slug).read_text(encoding="utf-8")).get(3, "")


class ProjectSensitivityValuesTest(_Harness):
    def test_union_includes_domain(self):
        self._add_domain_class("pii")
        self._add_domain_class("payments")
        vals = add._project_sensitivity_values(self._root())
        for base in add._SENSITIVITY_VALUES:
            self.assertIn(base, vals, "base must always be present")
        self.assertIn("pii", vals)
        self.assertIn("payments", vals)

    def test_no_section_falls_back_to_base(self):
        # init seeds the base section but no DOMAIN classes; resolver still yields exactly the base
        vals = add._project_sensitivity_values(self._root())
        self.assertEqual(tuple(vals), tuple(add._SENSITIVITY_VALUES),
                         "no domain classes -> exactly the base four (non-empty, base-only)")

    def test_missing_glossary_is_base(self):
        self._glossary().unlink()
        self.assertEqual(tuple(add._project_sensitivity_values(self._root())),
                         tuple(add._SENSITIVITY_VALUES), "unreadable/absent glossary -> base only")


class TaskSensitivityValidParamTest(_Harness):
    def test_valid_param_admits_domain_value(self):
        self.assertEqual(add._task_sensitivity("slug: t · sensitivity: pii", valid=("pii",)), "pii")

    def test_default_is_base_only(self):
        # without `valid`, a domain token is unknown ("?") — back-compat with the base reader
        self.assertEqual(add._task_sensitivity("slug: t · sensitivity: pii"), "?")


class FreezeUnionTest(_Harness):
    def test_domain_value_freezes(self):
        self._add_domain_class("pii")
        self._new_task_at_contract("t")
        self._set_sensitivity("t", "pii")
        self._silent("freeze", "--by", "Tin Dang")
        self.assertRegex(self._section3("t"), r"Status:\s*FROZEN @ v1")

    def test_unknown_everywhere_refuses(self):
        self._new_task_at_contract("t")
        self._set_sensitivity("t", "spicy")          # not base, not in glossary
        before = self._task_md("t").read_bytes()
        out, code = self._run("freeze")
        self.assertNotEqual(code, 0)
        self.assertIn("sensitivity_invalid", out)
        self.assertFalse(add._contract_frozen(self._section3("t")))
        self.assertEqual(self._task_md("t").read_bytes(), before)


class InitAndNudgeTest(_Harness):
    def test_init_seeds_section(self):
        self.assertIn("## Sensitivity classes", self._glossary().read_text(encoding="utf-8"),
                      "init seeds the sensitivity-classes section into GLOSSARY.md")

    def test_check_nudges_when_no_domain_classes(self):
        # a project with only the base (no domain classes) -> check carries a nudge AND exits 0
        out, code = self._run("check")
        self.assertEqual(code, 0, out)
        self.assertIn("sensitivity", out.lower())
        self.assertRegex(out, r"(?i)sensitivit.*(domain|class|glossary)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
