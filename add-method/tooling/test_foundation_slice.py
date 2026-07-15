#!/usr/bin/env python3
"""foundation-slice (engine-output-trim, context/turn lever) — progressive disclosure.
PROJECT.md is a cross-milestone foundation read at orient and re-read every turn. `status
--foundation` discloses the SKELETON — preamble (incl. invariants) + Domain + Spec IN FULL,
every OTHER section COLLAPSED to its heading + an on-demand `--foundation "<section>"` pull;
the newest Key Decisions kept, the stale tail pulled. Invariants (run/entry contracts that
bind EVERY task) are NEVER collapsed. A named `--foundation "<section>"` fleshes out one
section on demand; `--all` restores the whole foundation.

Run: python3 -m unittest test_foundation_slice -v
"""
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

_FIXTURE = """# PROJECT — foundation
invariants: the artifact runs as `python -m app` on $PORT

## Domain (DDD) — the language and the boundaries
DOMAIN_BODY_MARKER — the ubiquitous language lives here.

## Spec / Living Document (SDD) — what we are building, now
SPEC_BODY_MARKER — the current spec, holistic across milestones.

## Users (UDD) — UI/UX: design before code
UDD_BODY_MARKER — wireframes, color tokens, screen flows a backend task ignores.
more UI detail line one
more UI detail line two

## Key Decisions (append-only — newest-first)
- NEWEST_DECISION_MARKER 2026-07-15 keep me
- decision b
- decision c
- decision d
- decision e
- decision f
- decision g
- decision h
- decision i
- decision j
- decision k
- decision l
- decision m
- decision n
- decision o
- decision p
- decision q
- decision r
- decision s
- decision t
- decision u
- OLD_DECISION_MARKER 2026-01-01 elide me (stale tail)
"""


class _Harness(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-fslice-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo", "--stage", "mvp")
        (self.tmp / ".add" / "PROJECT.md").write_text(_FIXTURE, encoding="utf-8")

    def _silent(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit:
            pass

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue(), err.getvalue(), code


class FoundationMapTest(_Harness):
    def test_map_keeps_invariants_domain_spec(self):
        out, _, _ = self._run("status", "--foundation")
        self.assertIn("invariants:", out, "invariants (bind every task) must never be collapsed")
        self.assertIn("DOMAIN_BODY_MARKER", out, "Domain must be full in the map")
        self.assertIn("SPEC_BODY_MARKER", out, "Spec must be full in the map")
        self.assertIn("NEWEST_DECISION_MARKER", out, "the newest decisions must survive")

    def test_map_collapses_udd_body_to_a_pull_hint(self):
        out, _, _ = self._run("status", "--foundation")
        self.assertNotIn("UDD_BODY_MARKER", out, "the UI/UX (UDD) body must be collapsed in the map")
        self.assertIn("## Users", out, "the UDD heading stays as a signpost")
        self.assertIn('--foundation "Users"', out, "a collapsed section must leave an on-demand pull hint")

    def test_map_collapses_stale_decision_tail(self):
        out, _, _ = self._run("status", "--foundation")
        self.assertNotIn("OLD_DECISION_MARKER", out, "the stale decision tail must be collapsed")
        self.assertIn('--foundation "Key Decisions"', out, "the decision tail must leave a pull hint")

    def test_all_restores_the_full_foundation(self):
        full, _, _ = self._run("status", "--foundation", "--all")
        self.assertIn("UDD_BODY_MARKER", full, "--all restores the UDD body")
        self.assertIn("OLD_DECISION_MARKER", full, "--all restores every decision")

    def test_map_is_materially_shorter_than_full(self):
        sliced, _, _ = self._run("status", "--foundation")
        full, _, _ = self._run("status", "--foundation", "--all")
        self.assertLess(len(sliced), len(full), "the map must be shorter than the full foundation")


class FoundationPullTest(_Harness):
    def test_pull_returns_only_the_named_section_body(self):
        out, _, code = self._run("status", "--foundation", "Users")
        self.assertEqual(code, 0)
        self.assertIn("UDD_BODY_MARKER", out, "pulling `Users` must flesh out that section body")
        self.assertIn("more UI detail line two", out, "the WHOLE section body, not a summary")
        self.assertNotIn("DOMAIN_BODY_MARKER", out, "a pull is ONE section, not the whole foundation")

    def test_pull_matches_a_multiword_selector(self):
        out, _, code = self._run("status", "--foundation", "Key Decisions")
        self.assertEqual(code, 0)
        self.assertIn("OLD_DECISION_MARKER", out, "pulling `Key Decisions` fleshes out the full tail")

    def test_pull_unknown_section_fails_closed(self):
        out, err, code = self._run("status", "--foundation", "Nonexistent")
        self.assertNotEqual(code, 0, "an unknown section must fail, never a silent empty read")
        self.assertIn("foundation_section_unknown", err)


if __name__ == "__main__":
    unittest.main()
