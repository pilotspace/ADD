#!/usr/bin/env python3
"""Red/green tests for ci-tooling-mirror-gap — repo hygiene, not an engine feature.

`untrack-add-tooling` (commit 16afe85) made `.add/tooling/` a gitignored, untracked
dogfood mirror and gave `.github/workflows/ci.yml`'s `seam-audit` job a materialize
step (mkdir + copy add.py/add_engine/engine_pin.py/templates from add-method/tooling/)
so that job survives a fresh checkout. Two OTHER jobs that run the same tooling test
suite were missed: ci.yml's `test` job and publish.yml's `guard` job. Verified via an
isolated `git clone` + `git checkout` (not the working tree): a fresh checkout with no
`.add/tooling` on disk fails 38 tests + errors on 68 more, because dozens of tests
(the `_3tree`/`_3tree_parity`/`mirrors_and_pin` family) hard-require
`.add/tooling/add_engine/*.py` to exist, with no `.exists()` soft-skip.

Frozen shape (§3 @ v1): copy the exact seam-audit materialize step, byte-identical,
into both the `test` job (before "Run tooling test suite") and the `guard` job
(before "Run tooling test suite (red/green gate)"). No shared composite action
(duplication mirrors this repo's existing style, e.g. the audit invocation is also
duplicated into GETTING-STARTED.md). seam-audit itself receives no edits.

These assertions run against the REAL repo state (ci.yml / publish.yml content) —
no sandbox needed for the wiring checks; the fresh-checkout scenario clones the repo
into a temp dir to prove the fix actually survives a real checkout, not just the
local working tree (which already happens to have .add/tooling present).

Run: cd add-method/tooling && python3 -m unittest test_ci_tooling_mirror_gap -v
"""
from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent          # add-method/tooling
ADD_METHOD = HERE.parent                        # add-method
REPO = ADD_METHOD.parent                        # repo root
CI_YML = REPO / ".github" / "workflows" / "ci.yml"
PUBLISH_YML = REPO / ".github" / "workflows" / "publish.yml"

# every line the materialize step must contain — each checked individually and by
# position, so a partial/incomplete copy (e.g. add_engine/ or engine_pin.py silently
# dropped) fails instead of slipping through a loosely-anchored first...last regex.
# Identical to test_untrack_add_tooling.py's _REQUIRED_MATERIALIZE_LINES (the proven
# seam-audit step this task replicates into 2 more jobs).
_REQUIRED_MATERIALIZE_LINES = [
    "mkdir -p .add/tooling",
    "cp add-method/tooling/add.py .add/tooling/add.py",
    "cp -r add-method/tooling/add_engine .add/tooling/add_engine",
    "cp add-method/tooling/engine_pin.py .add/tooling/engine_pin.py",
    "cp -r add-method/tooling/templates .add/tooling/templates",
]


def _setuptools_available() -> bool:
    return importlib.util.find_spec("setuptools") is not None


def _expected_skip_count() -> int:
    """The nested clone's own full-suite run always self-skips exactly once — its
    own recursion guard (FreshCheckoutSurvivesTestJob, rediscovered inside the
    clone) hits `_ADD_CI_MIRROR_GAP_NESTED == "1"` and calls skipTest — PLUS
    whatever environment-conditional skips the CURRENT interpreter is already
    known to produce elsewhere in the suite: test_packaging.py's 3 PyWheelTest
    checks self-skip per-method when setuptools isn't importable. (kernel-trim
    (ADD 2.0 M5): the 6 component-pillar files with tomllib skips are deleted.)
    Computed instead of a fixed literal, so an unrelated skip still fails loudly
    instead of being silently waved through."""
    n = 1
    if not _setuptools_available():
        n += 3
    return n


def _nested_ok_regex(n: int) -> re.Pattern:
    """A bare `^OK$` can never match a real nested run (see _expected_skip_count),
    so require the EXACT expected count — not `\\(skipped=\\d+\\)` — so an
    unrelated skip still fails loudly instead of being silently waved through."""
    if n <= 0:
        return re.compile(r"(?m)^OK\s*$")
    return re.compile(rf"(?m)^OK \(skipped={n}\)\s*$")


def _job_block(text: str, job_name: str) -> str:
    """Extract a named top-level job's YAML block (2-space-indented key to the
    next 2-space-indented key or EOF) — same extraction shape test_audit_ci.py
    already uses for `seam-audit`."""
    m = re.search(rf"(?ms)^  {re.escape(job_name)}:\n(.*?)(?=^  [A-Za-z]|\Z)", text)
    return m.group(1) if m else ""


def _materialize_run_block(job_block: str) -> str:
    """The literal `run: |` body of the "Materialize the dogfood tooling mirror" step
    inside a job block — i.e. the ACTUAL lines ci.yml/publish.yml would execute, not a
    hardcoded copy of them. Indentation-stripped so it can be handed to `bash -c`."""
    m = re.search(
        r"(?ms)^\s*-\s*name:\s*Materialize the dogfood tooling mirror.*?\n"
        r"\s*run:\s*\|\n(.*?)(?=^\s*-\s*name:|\Z)",
        job_block,
    )
    if not m:
        return ""
    lines = m.group(1).splitlines()
    indents = [len(l) - len(l.lstrip()) for l in lines if l.strip()]
    cut = min(indents) if indents else 0
    return "\n".join(l[cut:] for l in lines)


class CiTestJobMaterializes(unittest.TestCase):
    def test_ci_test_job_materializes_before_suite(self):          # M1, M3
        block = _job_block(CI_YML.read_text(encoding="utf-8"), "test")
        self.assertTrue(block, "ci.yml must define a top-level `test` job")
        run_pos = block.find("Run tooling test suite")
        self.assertGreaterEqual(run_pos, 0,
                                 "the `test` job must carry the tooling-suite run step")
        for line in _REQUIRED_MATERIALIZE_LINES:
            pos = block.find(line)
            self.assertGreaterEqual(pos, 0,
                                     f"ci.yml `test` job must materialize: {line!r}")
            self.assertLess(pos, run_pos,
                             f"materialize line must run BEFORE the suite: {line!r}")


class PublishGuardJobMaterializes(unittest.TestCase):
    def test_publish_guard_job_materializes_before_suite(self):    # M2, M3
        block = _job_block(PUBLISH_YML.read_text(encoding="utf-8"), "guard")
        self.assertTrue(block, "publish.yml must define a top-level `guard` job")
        run_pos = block.find("Run tooling test suite (red/green gate)")
        self.assertGreaterEqual(run_pos, 0,
                                 "the `guard` job must carry the tooling-suite run step")
        for line in _REQUIRED_MATERIALIZE_LINES:
            pos = block.find(line)
            self.assertGreaterEqual(pos, 0,
                                     f"publish.yml `guard` job must materialize: {line!r}")
            self.assertLess(pos, run_pos,
                             f"materialize line must run BEFORE the suite: {line!r}")


class FreshCheckoutSurvivesTestJob(unittest.TestCase):
    """Proves the fix against a REAL checkout, not the local working tree (which
    already happens to carry .add/tooling on disk, just untracked)."""

    def test_fresh_checkout_survives_test_job_sequence(self):      # M5
        # recursion guard: once this file is committed, a nested clone's own
        # `unittest discover` would rediscover this very test and clone-of-clone
        # forever. The env var is set on the subprocess below, never on this process.
        if os.environ.get("_ADD_CI_MIRROR_GAP_NESTED") == "1":
            self.skipTest("nested invocation — recursion guard")
        if not shutil.which("git"):
            self.skipTest("git not available")
        tmp = Path(tempfile.mkdtemp(prefix="ci-fresh-checkout-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        clone = tmp / "clone"
        r = subprocess.run(["git", "clone", "--no-hardlinks", "-q", str(REPO), str(clone)],
                            capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, f"clone failed: {r.stdout}{r.stderr}")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                               capture_output=True, text=True, check=True).stdout.strip()
        r = subprocess.run(["git", "checkout", "-q", head], cwd=clone,
                            capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, f"checkout failed: {r.stdout}{r.stderr}")
        self.assertFalse((clone / ".add" / "tooling").exists(),
                          "precondition: a fresh checkout must NOT carry .add/tooling "
                          "(it is gitignored/untracked) — otherwise this test proves nothing")

        # run the ACTUAL test-job materialize lines, extracted from ci.yml's own text
        # (not the hardcoded _REQUIRED_MATERIALIZE_LINES constant) — proves the exact
        # bytes CI would execute, not merely that some known-good lines exist somewhere.
        test_block = _job_block(CI_YML.read_text(encoding="utf-8"), "test")
        materialize_script = _materialize_run_block(test_block)
        self.assertTrue(materialize_script, "could not extract the materialize run: block "
                        "from ci.yml's `test` job")
        r = subprocess.run(["bash", "-c", materialize_script], cwd=clone,
                            capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, f"materialize failed: {r.stdout}{r.stderr}")
        self.assertTrue((clone / ".add" / "tooling" / "add_engine").is_dir(),
                         "materialize step must produce .add/tooling/add_engine")

        # match ci.yml's `test` job fidelity: it runs `npm ci` (setup-node + npm ci steps)
        # before the suite, so @clack/prompts is importable for the interactive-path pty
        # tests — skipping this step is not a lighter-weight equivalent, it changes which
        # code path those tests exercise (plain-text fallback vs. the real clack UI) and
        # was the actual cause of an early, unrelated-looking pty-timeout failure here.
        if shutil.which("npm"):
            r = subprocess.run(["npm", "ci"], cwd=clone / "add-method",
                                capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, f"npm ci failed: {r.stdout}{r.stderr}")
        else:
            self.skipTest("npm not available — cannot faithfully reproduce the test job")

        env = {**os.environ, "_ADD_CI_MIRROR_GAP_NESTED": "1"}
        r = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tooling", "-p", "test_*.py"],
            cwd=clone / "add-method", capture_output=True, text=True, timeout=600, env=env,
        )
        combined = r.stdout + r.stderr
        tail = "\n".join(combined.splitlines()[-15:])
        self.assertEqual(r.returncode, 0,
                          f"fresh-checkout suite must be fully green after materialize:\n{tail}")
        # exact zero-failures/errors, not a loose substring check — "OK" alone would
        # also appear inside an "OK (skipped=N)" or a stray log line, and a run with
        # e.g. "FAILED (failures=1)" still contains "OK" earlier in some subprocess's
        # own stdout noise, so pin the unittest summary line itself. Tolerates exactly
        # this interpreter's computed expected skip count (see _expected_skip_count) —
        # any other skip count, failure, or error still fails this assertion.
        expected_skips = _expected_skip_count()
        self.assertRegex(combined, _nested_ok_regex(expected_skips),
                          f"fresh-checkout suite must report a bare 'OK' summary line "
                          f"matching this interpreter's expected skip count "
                          f"({expected_skips}):\n{tail}")
        ran_match = re.search(r"Ran (\d+) tests? in", combined)
        self.assertIsNotNone(ran_match, f"no 'Ran N tests' summary found:\n{tail}")
        # sanity floor, not an exact match to a sibling suite run (which would itself
        # require a second, unguarded full-discovery subprocess and reintroduce the
        # exact recursion risk this test's own guard exists to prevent) — catches a
        # gross discovery failure (e.g. a cwd bug finding 3 tests instead of ~2500+).
        self.assertGreater(int(ran_match.group(1)), 2000,
                            f"fresh-checkout suite discovered suspiciously few tests:\n{tail}")


class OkSummaryRegexTest(unittest.TestCase):
    """Fast, pure-logic coverage for the nested-suite summary tolerance (tasks
    fresh-checkout-skip-tolerance / nested-suite-skip-count-tolerance) — decoupled
    from the expensive git-clone + npm-ci + full-suite integration test above,
    which exercises the SAME pattern for real. The nested run's own recursion
    guard (this file's FreshCheckoutSurvivesTestJob, rediscovered inside the
    clone) always self-skips exactly once, PLUS whatever environment-conditional
    skips the CURRENT interpreter already produces elsewhere in the suite
    (test_packaging's wheel checks skip per-method when setuptools isn't
    importable) — compute the exact expected count instead of a fixed literal,
    so an unrelated skip still fails loudly."""

    def test_both_deps_present_computes_one(self):
        with mock.patch("test_ci_tooling_mirror_gap._setuptools_available", return_value=True):
            self.assertEqual(_expected_skip_count(), 1)

    def test_setuptools_missing_adds_three(self):
        with mock.patch("test_ci_tooling_mirror_gap._setuptools_available", return_value=False):
            self.assertEqual(_expected_skip_count(), 4)

    def test_regex_matches_its_own_exact_count(self):
        rx = _nested_ok_regex(7)
        self.assertRegex("OK (skipped=7)\n", rx)
        self.assertNotRegex("OK (skipped=6)\n", rx)
        self.assertNotRegex("OK (skipped=8)\n", rx)

    def test_regex_zero_accepts_bare_ok(self):
        self.assertRegex("OK\n", _nested_ok_regex(0))

    def test_rejects_a_failure_summary(self):
        self.assertNotRegex("FAILED (failures=1)\n", _nested_ok_regex(1))

    def test_unexpected_extra_skip_still_fails(self):
        self.assertNotRegex("OK (skipped=8)\n", _nested_ok_regex(7))


if __name__ == "__main__":
    unittest.main(verbosity=2)
