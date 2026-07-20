#!/usr/bin/env python3
"""Red/green tests for specs-5dd (ADD 2.0 M3).

CONTRACT: the foundation becomes FIVE living 5-DD spec files —
`.add/specs/{domain,system,experience,quality,method}.md` (DDD · SDD · UDD ·
TDD · ADD) — and deltas append IN-FLIGHT via the kernel verb `delta-append`
(one of the ratified 2.0 eight): lessons land in the right spec the moment
they are learned, not batched at milestone close.

- init seeds the 5 spec files (never-clobber, same survivor idiom as
  SETUP_FILES); each carries a `## Deltas (newest first)` section.
- `delta-append <dd> "<text>"`: dd ∈ ddd|sdd|udd|tdd|add routes to its spec
  file; the line is prepended UNDER the Deltas heading (newest first), tagged
  `[open · <date>]`, with `task:<slug>` stamped from the active task (or
  `--task`; absent -> no task tag, never inferred).
- An unknown dd refuses with `delta_dd_unknown` before any write.
- Legacy tolerance: a pre-2.0 project with no .add/specs/ gets the TARGET
  spec file seeded on demand by delta-append — the verb never dies on a
  missing dir.
- The spec template ships as templates/specs/SPEC.md.tmpl (one template,
  rendered five ways — template-unify discipline).

Run: python3 -m unittest test_specs_5dd -v
"""
from __future__ import annotations

import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
from add_engine import constants

TOOLING = Path(__file__).resolve().parent
SPEC_TMPL = TOOLING / "templates" / "specs" / "SPEC.md.tmpl"
DD_FILES = {"ddd": "domain.md", "sdd": "system.md", "udd": "experience.md",
            "tdd": "quality.md", "add": "method.md"}


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-5dd-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue() + err.getvalue(), code

    def _ok(self, *argv):
        text, code = self._run(*argv)
        self.assertEqual(code, 0, f"{argv} exited {code}: {text}")
        return text

    def _spec(self, dd: str) -> str:
        return (self.tmp / ".add" / "specs" / DD_FILES[dd]).read_text(encoding="utf-8")


class SeedingTest(_Harness):
    # Must: init seeds all five living specs
    def test_init_seeds_five_specs(self):
        self._ok("init", "--name", "demo", "--stage", "mvp")
        for dd, fname in DD_FILES.items():
            p = self.tmp / ".add" / "specs" / fname
            self.assertTrue(p.is_file(), f"init must seed .add/specs/{fname} ({dd})")
            self.assertIn("## Deltas", p.read_text(encoding="utf-8"),
                          f"{fname} must carry the Deltas section")

    # Must: never-clobber — a customized spec survives re-init --force
    def test_reinit_never_clobbers(self):
        self._ok("init", "--name", "demo", "--stage", "mvp")
        p = self.tmp / ".add" / "specs" / "domain.md"
        p.write_text("# my custom domain spec\n\n## Deltas (newest first)\n", encoding="utf-8")
        self._ok("init", "--name", "demo", "--stage", "mvp", "--force")
        self.assertIn("my custom domain spec", p.read_text(encoding="utf-8"),
                      "re-init must never clobber a living spec")

    # Must: one shipped template serves all five (template-unify)
    def test_one_spec_template_ships(self):
        self.assertTrue(SPEC_TMPL.is_file(),
                        "templates/specs/SPEC.md.tmpl must ship (ONE template, five renders)")
        text = SPEC_TMPL.read_text(encoding="utf-8")
        self.assertIn("## Deltas", text)

    # Must: the DD map is a closed engine constant
    def test_dd_map_exported(self):
        self.assertIn("SPEC_DDS", constants.__all__)
        self.assertEqual(set(constants.SPEC_DDS), set(DD_FILES),
                         "SPEC_DDS must map exactly the five DDs")


class DeltaAppendTest(_Harness):
    # Must: a delta lands under the right spec's Deltas heading, [open]-tagged
    def test_append_routes_to_spec(self):
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("delta-append", "tdd", "mutation-probe every earned green")
        text = self._spec("tdd")
        self.assertIn("mutation-probe every earned green", text)
        self.assertIn("[open", text.split("## Deltas", 1)[1],
                      "the delta must be [open]-tagged under the Deltas heading")
        for other in ("ddd", "sdd", "udd", "add"):
            self.assertNotIn("mutation-probe", self._spec(other),
                             f"the delta must not leak into the {other} spec")

    # Must: newest first — the second delta appears ABOVE the first
    def test_newest_first(self):
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("delta-append", "add", "first lesson")
        self._ok("delta-append", "add", "second lesson")
        tail = self._spec("add").split("## Deltas", 1)[1]
        self.assertLess(tail.index("second lesson"), tail.index("first lesson"),
                        "deltas prepend newest-first under the heading")

    # Must: the active task is stamped; --task overrides; no task -> no tag
    def test_task_stamping(self):
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("delta-append", "sdd", "taskless lesson")
        self.assertNotIn("task:", self._spec("sdd").split("## Deltas", 1)[1])
        self._ok("lock", "--force")
        self._ok("new-task", "t", "--title", "T")
        self._ok("delta-append", "sdd", "in-flight lesson")
        self.assertIn("task:t", self._spec("sdd"))
        self._ok("delta-append", "sdd", "other-task lesson", "--task", "zz")
        self.assertIn("task:zz", self._spec("sdd"))

    # Reject delta_dd_unknown: refuse BEFORE any write
    def test_unknown_dd_refused(self):
        self._ok("init", "--name", "demo", "--stage", "mvp")
        out, code = self._run("delta-append", "xdd", "nope")
        self.assertNotEqual(code, 0)
        self.assertIn("delta_dd_unknown", out)

    # Boundary: a legacy project (no specs/) gets the target file seeded on demand
    def test_legacy_seeds_on_demand(self):
        self._ok("init", "--name", "demo", "--stage", "mvp")
        shutil.rmtree(self.tmp / ".add" / "specs")
        self._ok("delta-append", "udd", "late lesson")
        self.assertIn("late lesson", self._spec("udd"),
                      "delta-append must seed the missing spec file, never die")


if __name__ == "__main__":
    unittest.main()
