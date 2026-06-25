#!/usr/bin/env python3
"""Tests for the gemini profile + .gemini/settings.json merge (multi-agent-installer · gemini-settings-config).

The installer detects Gemini CLI, writes the AGENTS.md pointer (existing path), AND merges
<target>/.gemini/settings.json so context.fileName includes "AGENTS.md" — fail-soft, idempotent,
preserving every other key. Both twins (pip _installer.py + npm bin/cli.js) decide identically.

Run: python3 -m unittest test_gemini_settings -v
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_SRC = _ADD_METHOD / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from add_method import _installer            # noqa: E402

CLI_JS = _ADD_METHOD / "bin" / "cli.js"
NODE = shutil.which("node")
GEMINI_ENV = {"GEMINI_CLI": "1"}


def _make_bundled(root: Path) -> Path:
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py\n")
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "00-introduction.md").write_text("intro\n")
    return root


def _settings(target: Path) -> dict:
    return json.loads((target / ".gemini" / "settings.json").read_text(encoding="utf-8"))


def _seed(target: Path, data: dict) -> None:
    (target / ".gemini").mkdir(parents=True, exist_ok=True)
    (target / ".gemini" / "settings.json").write_text(json.dumps(data), encoding="utf-8")


class DetectTest(unittest.TestCase):
    def test_detect_gemini(self):
        p = _installer._detect_agent(GEMINI_ENV)
        self.assertEqual(p["id"], "gemini")
        self.assertEqual(p["integration_file"], "AGENTS.md")


class MergeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gemini-merge-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_fresh_creates_settings(self):
        action = _installer._write_gemini_settings(self.tmp)
        self.assertEqual(action, "created")
        self.assertEqual(_settings(self.tmp)["context"]["fileName"], ["AGENTS.md"])

    def test_string_fileName_becomes_list(self):
        _seed(self.tmp, {"context": {"fileName": "GEMINI.md"}})
        _installer._write_gemini_settings(self.tmp)
        self.assertEqual(_settings(self.tmp)["context"]["fileName"], ["GEMINI.md", "AGENTS.md"])

    def test_list_appends_agents_md(self):
        _seed(self.tmp, {"context": {"fileName": ["GEMINI.md"]}})
        _installer._write_gemini_settings(self.tmp)
        names = _settings(self.tmp)["context"]["fileName"]
        self.assertIn("GEMINI.md", names)
        self.assertIn("AGENTS.md", names)

    def test_other_keys_preserved(self):
        _seed(self.tmp, {"theme": "dark", "context": {"fileName": ["GEMINI.md"]}})
        _installer._write_gemini_settings(self.tmp)
        self.assertEqual(_settings(self.tmp)["theme"], "dark")

    def test_idempotent(self):
        _installer._write_gemini_settings(self.tmp)
        raw = (self.tmp / ".gemini" / "settings.json").read_bytes()
        action = _installer._write_gemini_settings(self.tmp)
        self.assertEqual(action, "unchanged")
        self.assertEqual((self.tmp / ".gemini" / "settings.json").read_bytes(), raw)

    def test_malformed_skipped(self):
        (self.tmp / ".gemini").mkdir()
        (self.tmp / ".gemini" / "settings.json").write_text("{not json", encoding="utf-8")
        action = _installer._write_gemini_settings(self.tmp)
        self.assertEqual(action, "skipped")
        self.assertEqual((self.tmp / ".gemini" / "settings.json").read_text(encoding="utf-8"), "{not json")


class InstallFlowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gemini-inst-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.proj = self.tmp / "proj"
        self.proj.mkdir()

    def _install(self, env):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = _installer.install(target=str(self.proj), bundled=str(self.bundled),
                                      non_interactive=True, env=env)
        return code

    def test_install_flow_writes_pointer_and_settings(self):
        self.assertEqual(self._install(GEMINI_ENV), 0)
        self.assertTrue((self.proj / "AGENTS.md").exists(), "gemini install writes the AGENTS.md pointer")
        self.assertIn("AGENTS.md", _settings(self.proj)["context"]["fileName"])

    def test_unwritable_does_not_abort(self):
        (self.proj / ".gemini").mkdir()
        (self.proj / ".gemini" / "settings.json").mkdir()   # a dir where the file is expected
        self.assertEqual(self._install(GEMINI_ENV), 0, "an unwritable settings.json must not abort the drop")
        self.assertTrue((self.proj / ".claude" / "skills" / "add" / "SKILL.md").exists())

    def test_no_gemini_dir_for_other_agent(self):
        self._install({"CURSOR_AGENT": "1"})
        self.assertFalse((self.proj / ".gemini").exists(), "no .gemini for a non-gemini agent")


class ParityTest(unittest.TestCase):
    def test_parity_gemini_symbol(self):
        js = CLI_JS.read_text(encoding="utf-8")
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        self.assertIn("gemini", js)
        self.assertIn("gemini", py)
        self.assertIn("writeGeminiSettings", js)
        self.assertIn("_write_gemini_settings", py)


@unittest.skipUnless(NODE, "node not on PATH — npm gemini-settings check skipped (honest skip)")
class NpmTest(unittest.TestCase):
    def test_npm_gemini_writes_settings(self):
        with tempfile.TemporaryDirectory(prefix="gemini-npm-") as tmp:
            env = dict(os.environ)
            for k in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CI"):
                env.pop(k, None)
            env.update(GEMINI_ENV)
            res = subprocess.run([NODE, str(CLI_JS), "init", "--yes"], cwd=tmp,
                                 capture_output=True, text=True, timeout=120, env=env)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue((Path(tmp) / "AGENTS.md").exists())
            data = json.loads((Path(tmp) / ".gemini" / "settings.json").read_text(encoding="utf-8"))
            self.assertIn("AGENTS.md", data["context"]["fileName"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
