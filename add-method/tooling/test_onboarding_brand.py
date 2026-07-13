#!/usr/bin/env python3
"""Red-first tests for onboarding-brand (installer-smarts task 1).

Contract FROZEN @ v1: an ADD logo banner + a feature showcase (a value line + the
7-step Specify->Observe loop) render on the INTERACTIVE installer path only, fail-soft
(any render error falls through to the prompts, never aborts), while the NON-interactive
path stays byte-identical to today. Both twins (npm cli.js / pip _installer.py) render
the same DECISIONS; pip is condensed (stdlib), npm fuller (clack).

Harness conventions are shared with test_installer_prompts: subprocess twins, the
ADD_INSTALLER_FORCE_INTERACTIVE seam ("1"=force, "fail"=force+import-throws). The npm
clack TUI needs a real PTY, so npm is covered structurally + by branch-reachability;
pip's input() flow is line-based and fully automated here.

Run: python3 -m unittest test_onboarding_brand -v
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

from test_installer_prompts import (
    _run_node, _run_pip, _brain_landed, NODE, CLI_JS, PKG_ROOT, REPO_ROOT,
)

INSTALLER_PY = PKG_ROOT / "src" / "add_method" / "_installer.py"

# The 6 ADD phases the showcase loop must name (grounded in the method, never invented;
# grounding itself is folded into Plan, not a separate step). Build/Tests are excluded
# from the OUTPUT markers below because the plain installer prose already says "build" —
# these five are showcase-only words that never appear in normal installer output, so
# they cleanly separate the two paths.
LOOP_STEPS = ("Specify", "Plan", "Tests", "Build", "Verify", "Observe")
SHOWCASE_MARKERS = ("Specify", "Plan", "Verify", "Observe")


def _markers_present(text):
    return sum(1 for s in SHOWCASE_MARKERS if s in text)


def _load_engine():
    spec = importlib.util.spec_from_file_location("add_eng", PKG_ROOT / "tooling" / "add.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- faithful: the loop labels are the real ADD phases, not invented marketing ----

class FaithfulShowcaseTest(unittest.TestCase):
    def test_loop_steps_are_the_real_pre_done_phases(self):
        add = _load_engine()
        phases = [p.lower() for p in add.PHASES]
        for s in LOOP_STEPS:
            self.assertIn(s.lower(), phases,
                          f"showcase step {s!r} must be a real ADD phase (grounded, not invented)")
        # exactly the 6 steps before the terminal "done", in order (no separate ground
        # or scenarios phase — grounding folded into Plan, scenarios into Specify)
        self.assertEqual([s.lower() for s in LOOP_STEPS], phases[0:6],
                         "the showcase must be the 6 pre-done phases in order")


# --- the banner is actually wired into BOTH twins (decision-equivalent) -----------

class ShowcaseWiredInSourceTest(unittest.TestCase):
    def test_npm_source_names_the_whole_loop(self):
        src = CLI_JS.read_text(encoding="utf-8")
        missing = [s for s in LOOP_STEPS if s not in src]
        self.assertEqual(missing, [],
                         f"cli.js must render the 7-step loop; missing labels: {missing}")

    def test_pip_source_names_the_whole_loop(self):
        src = INSTALLER_PY.read_text(encoding="utf-8")
        missing = [s for s in LOOP_STEPS if s not in src]
        self.assertEqual(missing, [],
                         f"_installer.py must render the 7-step loop; missing labels: {missing}")


# --- pip interactive renders the brand + showcase (line-based, no PTY needed) ------

class PipInteractiveBrandTest(unittest.TestCase):
    def test_pip_interactive_renders_brand_and_showcase(self):
        with tempfile.TemporaryDirectory(prefix="ob-pip-") as tmp:
            res = _run_pip(["init"], cwd=tmp, stdin="\nn\n",   # target Enter, then project-only scope
                           env_extra={"ADD_INSTALLER_FORCE_INTERACTIVE": "1"})
            self.assertEqual(res.returncode, 0, res.stderr)
            out = res.stdout + res.stderr
            self.assertGreaterEqual(
                _markers_present(out), 4,
                "the pip interactive banner must show the 7-step loop (>=4 showcase markers)")
            self.assertTrue(_brain_landed(Path(tmp)),
                            "the install must still complete after the banner")


# --- degraded terminal still shows the brand, in plain ASCII (no ANSI color) -------

class DegradedTerminalTest(unittest.TestCase):
    def test_pip_no_color_narrow_still_shows_plain_brand(self):
        with tempfile.TemporaryDirectory(prefix="ob-pip-") as tmp:
            res = _run_pip(["init"], cwd=tmp, stdin="\nn\n",   # target Enter, then project-only scope
                           env_extra={"ADD_INSTALLER_FORCE_INTERACTIVE": "1",
                                      "NO_COLOR": "1", "COLUMNS": "30"})
            self.assertEqual(res.returncode, 0, res.stderr)
            out = res.stdout + res.stderr
            self.assertGreaterEqual(
                _markers_present(out), 4,
                "even degraded (NO_COLOR, narrow) the showcase content must still appear")
            self.assertNotIn("\x1b[", res.stdout,
                             "a NO_COLOR render must emit no ANSI color escape sequences")


# --- the non-interactive boundary: NO showcase leaks onto the plain path -----------

class NonInteractiveBoundaryTest(unittest.TestCase):
    def test_pip_noninteractive_has_no_showcase(self):
        with tempfile.TemporaryDirectory(prefix="ob-pip-") as tmp:
            res = _run_pip(["init"], cwd=tmp)
            self.assertEqual(res.returncode, 0, res.stderr)
            out = res.stdout + res.stderr
            self.assertEqual(_markers_present(out), 0,
                             "the non-interactive path must show NO showcase (byte-identical boundary)")
            self.assertTrue(_brain_landed(Path(tmp)))

    @unittest.skipUnless(NODE, "node not on PATH — honest skip")
    def test_npm_noninteractive_has_no_showcase(self):
        with tempfile.TemporaryDirectory(prefix="ob-npm-") as tmp:
            res = _run_node(["init"], cwd=tmp)
            self.assertEqual(res.returncode, 0, res.stderr)
            out = res.stdout + res.stderr
            self.assertEqual(_markers_present(out), 0,
                             "the non-interactive npm path must show NO showcase (byte-identical boundary)")
            self.assertTrue(_brain_landed(Path(tmp)))


# --- fail-soft: a forced clack failure on npm still completes, no banner -----------

@unittest.skipUnless(NODE, "node not on PATH — honest skip")
class NpmFailSoftTest(unittest.TestCase):
    def test_npm_clack_unavailable_still_completes_without_banner(self):
        with tempfile.TemporaryDirectory(prefix="ob-npm-") as tmp:
            res = _run_node(["init"], cwd=tmp,
                            env_extra={"ADD_INSTALLER_FORCE_INTERACTIVE": "fail"})
            self.assertEqual(res.returncode, 0,
                             "a failed clack import must degrade to plain text, not crash the install")
            self.assertTrue(_brain_landed(Path(tmp)),
                            "the install must still complete after the fallback")
            out = res.stdout + res.stderr
            self.assertEqual(_markers_present(out), 0,
                             "the clack-unavailable fallback shows the plain path — no showcase")


# --- seams held: clack stays lazy, the engine is never edited by the render --------

class BrandSeamsHeldTest(unittest.TestCase):
    def test_clack_stays_lazy_after_the_banner(self):
        src = CLI_JS.read_text(encoding="utf-8")
        self.assertNotIn('require("@clack/prompts")', src)
        self.assertNotIn("require('@clack/prompts')", src)
        self.assertIn('import("@clack/prompts")', src,
                      "clack must still be loaded via a dynamic import() (lazy)")

    def test_engine_untouched_by_the_render(self):
        import hashlib
        from engine_pin import ENGINE_MD5
        for p in (PKG_ROOT / "tooling" / "add.py",
                  REPO_ROOT / ".add" / "tooling" / "add.py",
                  PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "add.py"):
            self.assertEqual(hashlib.md5(p.read_bytes()).hexdigest(), ENGINE_MD5,
                             f"{p} changed — the brand render never edits the engine")


if __name__ == "__main__":
    unittest.main(verbosity=2)
