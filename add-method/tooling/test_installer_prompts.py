#!/usr/bin/env python3
"""Tests for the interactive installer onramp (installer-experience · installer-prompts).

Behavioral pins for the FROZEN @ v1 contract: a guided installer that is interactive
only in a real terminal and byte-identical to today everywhere else, on both the npm
(clack) and pip (stdlib input) twins.

The subprocess harness pipes stdout/stdin, so a plain run is never a TTY -> the
NON-interactive path runs and the existing installer tests are unaffected. The
interactive branch is reached deterministically via the documented test seam
`ADD_INSTALLER_FORCE_INTERACTIVE` (contract §3):
    "1"    -> force interactive (real clack on npm / input() on pip)
    "fail" -> force interactive but the clack import throws -> clack_unavailable fallback

One honest gap (NOT a silent skip): the npm clack happy-path TUI (M1) needs a real
PTY; it is manual-verified in a terminal. CI here covers its branch reachability
(the fail/1 seams) + the byte-identical plain path. pip's input() flow is line-based,
so M2 IS automated below.

Run: python3 -m unittest test_installer_prompts -v
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import json
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent          # add-method/
REPO_ROOT = PKG_ROOT.parent
CLI_JS = PKG_ROOT / "bin" / "cli.js"
PACKAGE_JSON = PKG_ROOT / "package.json"
SRC_DIR = PKG_ROOT / "src"

NODE = shutil.which("node")

from engine_pin import ENGINE_MD5
ENGINE_PATHS = (
    PKG_ROOT / "tooling" / "add.py",
    REPO_ROOT / ".add" / "tooling" / "add.py",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


def _run_node(args, cwd=None, env_extra=None, stdin=None):
    env = dict(os.environ)
    # Never let a parent CI var leak into a forced-interactive test (CI overrides the seam).
    env.pop("CI", None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [NODE, str(CLI_JS), *args],
        cwd=cwd, capture_output=True, text=True, timeout=120, env=env, input=stdin)


def _run_pip(args, cwd=None, env_extra=None, stdin=None):
    env = dict(os.environ)
    env.pop("CI", None)
    env["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    if env_extra:
        env.update(env_extra)
    code = ("import sys; from add_method._cli import main; "
            "sys.exit(main(sys.argv[1:]))")
    return subprocess.run(
        [sys.executable, "-c", code, *args],
        cwd=cwd, capture_output=True, text=True, timeout=120, env=env, input=stdin)


def _brain_landed(root: Path) -> bool:
    return (
        (root / ".claude" / "skills" / "add" / "SKILL.md").exists()
        and (root / ".add" / "tooling" / "add.py").exists()
        and any((root / ".add" / "docs").glob("*.md"))
        and not (root / ".add" / "state.json").exists()
    )


def _nothing_written(root: Path) -> bool:
    return not (root / ".claude").exists() and not (root / ".add").exists()


# --- M9: dependency declared ------------------------------------------------

class ClackDependencyTest(unittest.TestCase):
    def test_clack_dependency_declared(self):
        pkg = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
        deps = pkg.get("dependencies", {})
        self.assertEqual(deps.get("@clack/prompts"), "^1.5.1",
                         "package.json must declare @clack/prompts pinned to ^1.5.1")
        self.assertEqual(pkg.get("engines", {}).get("node"), ">=18",
                         "engines.node must remain >=18")


# --- M6: clack is lazy-loaded (structural) ----------------------------------

class ClackLazyImportTest(unittest.TestCase):
    def test_clack_lazy_no_toplevel_import(self):
        src = CLI_JS.read_text(encoding="utf-8")
        self.assertNotIn('require("@clack/prompts")', src,
                         "clack must NOT be required at the top level (lazy only)")
        self.assertNotIn("require('@clack/prompts')", src,
                         "clack must NOT be required at the top level (single-quote variant)")
        self.assertNotIn("from \"@clack/prompts\"", src,
                         "clack must NOT be statically imported (lazy only)")
        self.assertNotIn("from '@clack/prompts'", src,
                         "clack must NOT be statically imported (single-quote variant)")
        self.assertIn('import("@clack/prompts")', src,
                      "clack must be loaded via a dynamic import() on the interactive path")


# --- M3: non-interactive is byte-identical ----------------------------------

@unittest.skipUnless(NODE, "node not on PATH — npx-side check skipped (honest skip)")
class NonInteractiveNpmTest(unittest.TestCase):
    def test_noninteractive_byte_identical_npm(self):
        with tempfile.TemporaryDirectory(prefix="ip-npm-") as tmp:
            res = _run_node(["init"], cwd=tmp)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue(_brain_landed(Path(tmp)), "plain npm init must drop the brain")
            self.assertIn("/add", res.stdout, "handoff must name /add")


class NonInteractivePipTest(unittest.TestCase):
    def test_noninteractive_byte_identical_pip(self):
        with tempfile.TemporaryDirectory(prefix="ip-pip-") as tmp:
            res = _run_pip(["init"], cwd=tmp)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue(_brain_landed(Path(tmp)), "plain pip init must drop the brain")
            self.assertIn("/add", res.stdout, "handoff must name /add")


# --- M4, M5: --yes / --non-interactive recognized on both twins -------------

@unittest.skipUnless(NODE, "node not on PATH — honest skip")
class YesFlagNpmTest(unittest.TestCase):
    def test_yes_flag_recognized_npm(self):
        with tempfile.TemporaryDirectory(prefix="ip-npm-") as tmp:
            res = _run_node(["init", "--yes"], cwd=tmp)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue(_brain_landed(Path(tmp)))
            self.assertNotIn("ignoring unknown flag --yes", res.stderr,
                             "--yes must be a recognized flag, not warned as unknown")

    def test_non_interactive_alias_npm(self):
        with tempfile.TemporaryDirectory(prefix="ip-npm-") as tmp:
            res = _run_node(["init", "--non-interactive"], cwd=tmp)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue(_brain_landed(Path(tmp)))
            self.assertNotIn("ignoring unknown flag --non-interactive", res.stderr)

    def test_yes_overrides_force_interactive_seam_npm(self):
        # contract: --yes / --non-interactive override the test seam to non-interactive
        with tempfile.TemporaryDirectory(prefix="ip-npm-") as tmp:
            res = _run_node(["init", "--yes"], cwd=tmp, stdin="",
                            env_extra={"ADD_INSTALLER_FORCE_INTERACTIVE": "1"})
            self.assertEqual(res.returncode, 0,
                             "--yes must beat the force-interactive seam (plain path, exit 0)")
            self.assertTrue(_brain_landed(Path(tmp)))


class YesFlagPipTest(unittest.TestCase):
    def test_yes_flag_recognized_pip(self):
        with tempfile.TemporaryDirectory(prefix="ip-pip-") as tmp:
            res = _run_pip(["init", "--yes"], cwd=tmp)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue(_brain_landed(Path(tmp)))

    def test_non_interactive_alias_pip(self):
        with tempfile.TemporaryDirectory(prefix="ip-pip-") as tmp:
            res = _run_pip(["init", "--non-interactive"], cwd=tmp)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue(_brain_landed(Path(tmp)))

    def test_yes_overrides_force_interactive_seam_pip(self):
        with tempfile.TemporaryDirectory(prefix="ip-pip-") as tmp:
            res = _run_pip(["init", "--yes"], cwd=tmp, stdin="",
                           env_extra={"ADD_INSTALLER_FORCE_INTERACTIVE": "1"})
            self.assertEqual(res.returncode, 0,
                             "--yes must beat the force-interactive seam (no EOF cancel)")
            self.assertTrue(_brain_landed(Path(tmp)))


# --- M7 / clack_unavailable: forced-interactive import failure falls back ---

@unittest.skipUnless(NODE, "node not on PATH — honest skip")
class ClackUnavailableTest(unittest.TestCase):
    def test_clack_unavailable_falls_back_npm(self):
        with tempfile.TemporaryDirectory(prefix="ip-npm-") as tmp:
            res = _run_node(["init"], cwd=tmp,
                            env_extra={"ADD_INSTALLER_FORCE_INTERACTIVE": "fail"})
            self.assertEqual(res.returncode, 0,
                             "a failed clack import must degrade to plain text, not crash")
            self.assertTrue(_brain_landed(Path(tmp)),
                            "the install must still complete after the fallback")
            self.assertRegex(res.stderr.lower(), r"(clack|interactive).*(unavailable|fall)",
                             "the fallback must emit a warn line about clack being unavailable")


# --- M8 / user_cancelled: abort before the write leaves nothing -------------

@unittest.skipUnless(NODE, "node not on PATH — honest skip")
class UserCancelledNpmTest(unittest.TestCase):
    def test_user_cancelled_writes_nothing_npm(self):
        with tempfile.TemporaryDirectory(prefix="ip-npm-") as tmp:
            # forced interactive + closed stdin -> clack cannot read a confirm -> cancel
            res = _run_node(["init"], cwd=tmp, stdin="",
                            env_extra={"ADD_INSTALLER_FORCE_INTERACTIVE": "1"})
            self.assertEqual(res.returncode, 130,
                             "a cancel before the write must exit 130")
            self.assertTrue(_nothing_written(Path(tmp)),
                            "a cancel must write NO files under the target")


class UserCancelledPipTest(unittest.TestCase):
    def test_user_cancelled_writes_nothing_pip(self):
        with tempfile.TemporaryDirectory(prefix="ip-pip-") as tmp:
            # forced interactive + EOF on stdin -> input() raises EOFError -> cancel
            res = _run_pip(["init"], cwd=tmp, stdin="",
                           env_extra={"ADD_INSTALLER_FORCE_INTERACTIVE": "1"})
            self.assertEqual(res.returncode, 130,
                             "a pip cancel (EOF) must exit 130")
            self.assertTrue(_nothing_written(Path(tmp)),
                            "a pip cancel must write NO files under the target")


# --- M2: pip interactive happy path (line-based input is feedable) ----------

class PipInteractiveHappyTest(unittest.TestCase):
    def test_pip_interactive_happy_path(self):
        with tempfile.TemporaryDirectory(prefix="ip-pip-") as tmp:
            res = _run_pip(["init"], cwd=tmp, stdin="\nn\n",   # accept default target, then project-only scope
                           env_extra={"ADD_INSTALLER_FORCE_INTERACTIVE": "1"})
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue(_brain_landed(Path(tmp)),
                            "accepting the prompt must drop the brain")
            combined = (res.stdout + res.stderr).lower()
            self.assertIn("target", combined,
                          "the interactive pip flow must show a target prompt")


# --- engine untouched (parity with test_installer_handoff) ------------------

class EnginePinTest(unittest.TestCase):
    def test_engine_untouched(self):
        for p in ENGINE_PATHS:
            self.assertTrue(p.exists(), f"missing engine copy: {p}")
            digest = hashlib.md5(p.read_bytes()).hexdigest()
            self.assertEqual(digest, ENGINE_MD5,
                             f"{p} changed — the installer onramp never edits the engine")


# --- rule-file mode parity (ccsk projects relocate the CLAUDE.md pointer) ----

def _assert_rule_file_layout(test, root: Path):
    """Both Phase-1 installers, in a ccsk project, must drop the Claude pointer into
    .claude/rules/add-workflows.md + a reference bullet in CLAUDE.md (no inline block)."""
    rules = root / ".claude" / "rules" / "add-workflows.md"
    test.assertTrue(rules.exists(), "rule file must be created in a ccsk project")
    test.assertIn("ADD:BEGIN", rules.read_text(encoding="utf-8"),
                  "rule file must hold the marked ADD pointer")
    claude = (root / "CLAUDE.md").read_text(encoding="utf-8")
    test.assertIn("add-workflows.md", claude, "CLAUDE.md must reference the rule file")
    test.assertNotIn("ADD:BEGIN", claude, "CLAUDE.md must NOT hold the inline block")


@unittest.skipUnless(NODE, "node not on PATH — npx-side check skipped (honest skip)")
class RuleFileModeNpmTest(unittest.TestCase):
    def test_ccsk_relocates_npm(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".ccsk").mkdir()
            res = _run_node(["init"], cwd=tmp, env_extra={"CLAUDECODE": "1"})
            self.assertEqual(res.returncode, 0, res.stderr)
            _assert_rule_file_layout(self, Path(tmp))

    def test_flag_relocates_npm(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = _run_node(["init", "--rule-file"], cwd=tmp, env_extra={"CLAUDECODE": "1"})
            self.assertEqual(res.returncode, 0, res.stderr)
            _assert_rule_file_layout(self, Path(tmp))


class RuleFileModePipTest(unittest.TestCase):
    def test_ccsk_relocates_pip(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".ccsk").mkdir()
            res = _run_pip(["init", tmp], env_extra={"CLAUDECODE": "1"})
            self.assertEqual(res.returncode, 0, res.stderr)
            _assert_rule_file_layout(self, Path(tmp))

    def test_flag_relocates_pip(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = _run_pip(["init", tmp, "--rule-file"], env_extra={"CLAUDECODE": "1"})
            self.assertEqual(res.returncode, 0, res.stderr)
            _assert_rule_file_layout(self, Path(tmp))


if __name__ == "__main__":
    unittest.main(verbosity=2)
