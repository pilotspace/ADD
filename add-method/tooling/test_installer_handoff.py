#!/usr/bin/env python3
"""Tests for the flagless installer handoff (v15 installer-handoff).

Behavioral pins for what v12 shipped as words (a flagless install that lands
the brain and hands off to /add). The handoff is CONVERSATIONAL-ONLY: 9d020e0
("update CLI instructions for user clarity") reworded it to the tool-agnostic
"open your AI Agent CLI (like Claude Code, Codex, etc.)" and REMOVED the manual
`init --await-lock` CLI-escape hint — so the closing output points only at /add
(the `--await-lock` flag itself still exists; /add runs it internally to arm the
v12 lock-down — only the user-facing fallback hint was dropped).
The npx-side tests skip honestly when `node` is absent (the npm-gated
precedent in test_packaging).
Run: python3 -m unittest test_installer_handoff -v
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent          # add-method/
REPO_ROOT = PKG_ROOT.parent
CLI_JS = PKG_ROOT / "bin" / "cli.js"
README = PKG_ROOT / "README.md"
SRC_DIR = PKG_ROOT / "src"

NODE = shutil.which("node")

ENGINE_PATHS = (
    PKG_ROOT / "tooling" / "add.py",
    REPO_ROOT / ".add" / "tooling" / "add.py",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)


def _baseline_env():
    """A scrubbed env so the flagless install tests the GENERIC (no-agent-detected)
    handoff deterministically — wherever the suite runs. agent-detect tailors the
    handoff when a coding-agent signal is present (CLAUDECODE/CODEX_*/OPENCODE*); the
    agent-specific paths are covered in test_agent_detect. Here we pin the baseline."""
    env = dict(os.environ)
    for k in list(env):
        if k in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT") or k.startswith(("CODEX_", "OPENCODE")):
            env.pop(k, None)
    return env


def _run_node_init(extra=(), cwd=None):
    return subprocess.run(
        [NODE, str(CLI_JS), "init", *extra],
        cwd=cwd, capture_output=True, text=True, timeout=120, env=_baseline_env())


def _run_pip_init(extra=(), cwd=None):
    env = _baseline_env()
    env["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    code = ("import sys; from add_method._cli import main; "
            "sys.exit(main(sys.argv[1:]))")
    return subprocess.run(
        [sys.executable, "-c", code, "init", *extra],
        cwd=cwd, capture_output=True, text=True, timeout=120, env=env)


def _assert_brain_landed(tc, root: Path, out: str):
    tc.assertTrue((root / ".claude" / "skills" / "add" / "SKILL.md").exists(),
                  "skill tree missing after flagless install")
    tc.assertTrue((root / ".add" / "tooling" / "add.py").exists(),
                  "tooling missing after flagless install")
    tc.assertFalse((root / ".add" / "docs").exists(),
                   "book-stops-shipping (2.0 M6b): the installer must not drop .add/docs")
    tc.assertFalse((root / ".add" / "state.json").exists(),
                   "installer must NEVER run init — no state.json")
    low = out.lower()
    tc.assertIn("open your ai agent cli", low,
                "the final output hands off to the conversational, tool-agnostic entry")
    tc.assertIn("/add", out, "the handoff names /add")
    tc.assertNotIn("--await-lock", out,
                   "the handoff is conversational-only — the manual `init --await-lock` "
                   "CLI-escape hint was removed for clarity (9d020e0); never re-advertise it")


@unittest.skipUnless(NODE, "node not on PATH — npx-side install check skipped (honest skip)")
class NpxFlaglessTest(unittest.TestCase):
    def test_npx_flagless_install_behavioral(self):
        with tempfile.TemporaryDirectory(prefix="add-npx-") as tmp:
            res = _run_node_init(cwd=tmp)
            self.assertEqual(res.returncode, 0,
                             f"flagless npx init failed:\n{res.stderr}")
            _assert_brain_landed(self, Path(tmp), res.stdout)

    def test_missing_flag_value_fails(self):
        # in-build STRENGTHENING amendment (disclosed at the gate): a trailing
        # `--stage` with no value must fail loudly, matching the pip twin's
        # argparse error — never silently drop the flag the user tried to pass
        with tempfile.TemporaryDirectory(prefix="add-npx-") as tmp:
            res = _run_node_init(("--stage",), cwd=tmp)
            self.assertNotEqual(res.returncode, 0,
                                "npx init --stage (no value) must fail, not "
                                "silently ignore the flag")


class PipFlaglessTest(unittest.TestCase):
    def test_pip_flagless_install_behavioral(self):
        with tempfile.TemporaryDirectory(prefix="add-pip-") as tmp:
            res = _run_pip_init(cwd=tmp)
            self.assertEqual(res.returncode, 0,
                             f"flagless pip init failed:\n{res.stderr}")
            _assert_brain_landed(self, Path(tmp), res.stdout)

    def test_missing_flag_value_fails(self):
        # twin of the npx-side strengthening amendment: argparse already
        # enforces this — the test pins the parity so neither side regresses
        with tempfile.TemporaryDirectory(prefix="add-pip-") as tmp:
            res = _run_pip_init(("--stage",), cwd=tmp)
            self.assertNotEqual(res.returncode, 0,
                                "pip init --stage (no value) must fail")


class ReadmeFlaglessTest(unittest.TestCase):
    def test_readme_install_examples_flagless_first(self):
        text = README.read_text(encoding="utf-8")
        # the flagless pin allows the marketing copy's trailing "# ecosystem" comment and the
        # pip one-liner prefix — any flag between `init` and EOL/comment still fails the pin.
        self.assertRegex(
            text, re.compile(r"^npx @pilotspace/add init\s*(#.*)?$", re.M),
            "README's npx install example must lead with the flagless form")
        self.assertRegex(
            text, re.compile(r"^(pip install pilotspace-add && )?pilotspace-add init\s*(#.*)?$", re.M),
            "README's pip install example must lead with the flagless form")


if __name__ == "__main__":
    unittest.main(verbosity=2)
