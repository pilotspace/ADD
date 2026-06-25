#!/usr/bin/env python3
"""Tests for agent detection (installer-experience · agent-detect).

FROZEN @ v1: the installer detects the active agent from env (an ordered profile registry,
generic last), writes THAT agent's integration file as a marker-delimited ADD pointer
(mirroring add.py:_inject_block — the SAME _GUIDE_BEGIN/_GUIDE_END so init's sync-guidelines
supersedes it in place), and prints THAT agent's next step. Unknown → generic AGENTS.md.
Both twins, identical detection result for the same env.

pip is hermetic: _detect_agent(env) takes an explicit env dict; install(bundled=, env=) injects
both. npm uses the real packaged sources via subprocess with an injected env (skips without node).

Run: python3 -m unittest test_agent_detect -v
"""
import contextlib
import importlib.util
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

# load the real engine to prove init's sync-guidelines supersedes the drop-time pointer
_spec = importlib.util.spec_from_file_location("add_engine_for_agent_detect", _TOOLING / "add.py")
add_engine = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(add_engine)


def _make_bundled(root: Path) -> Path:
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py\n")
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "00-introduction.md").write_text("intro\n")
    return root


# --- detection: pure, env-driven, deterministic ----------------------------

class DetectTest(unittest.TestCase):
    def test_detect_claude_from_env_pip(self):                    # D1, D2
        p = _installer._detect_agent({"CLAUDECODE": "1"})
        self.assertEqual(p["id"], "claude")
        self.assertEqual(p["integration_file"], "CLAUDE.md")
        self.assertIn("/add", p["next_step"])

    def test_detect_codex_from_env_pip(self):                     # D1, D3
        p = _installer._detect_agent({"CODEX_HOME": "/x"})
        self.assertEqual(p["id"], "codex")
        self.assertEqual(p["integration_file"], "AGENTS.md")
        self.assertIn("AGENTS.md", p["next_step"])

    def test_unknown_falls_back_to_generic_pip(self):             # D1, D4
        p = _installer._detect_agent({})
        self.assertEqual(p["id"], "generic")
        self.assertEqual(p["integration_file"], "AGENTS.md")
        # the generic next-step preserves today's onramp wording
        self.assertIn("/add", p["next_step"])
        self.assertIn("say what you want to build", p["next_step"])

    def test_detect_is_deterministic_and_total(self):             # D1
        env = {"CLAUDECODE": "1", "CODEX_HOME": "/x"}             # both present -> order decides
        self.assertEqual(_installer._detect_agent(env), _installer._detect_agent(dict(env)))
        # never throws on odd input
        self.assertEqual(_installer._detect_agent({"CLAUDECODE": ""})["id"], "generic")


# --- pointer write: mirrors _inject_block, same markers --------------------

class PointerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="agent-ptr-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.claude = _installer._detect_agent({"CLAUDECODE": "1"})
        self.generic = _installer._detect_agent({})

    def test_pointer_created_with_shared_markers(self):           # D6, D7
        action = _installer._write_agent_pointer(self.tmp, self.claude)
        self.assertEqual(action, "created")
        text = (self.tmp / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(text.count(add_engine._GUIDE_BEGIN), 1,
                         "pointer must carry exactly one ADD:BEGIN")
        self.assertIn(add_engine._GUIDE_END, text)

    def test_pointer_idempotent_and_preserves_user_content(self):  # D6, D7
        agents = self.tmp / "AGENTS.md"
        agents.write_text("# My Project\n\nuser prose\n", encoding="utf-8")
        # appending a block to an EXISTING file is an update (created is absent-only, per D6)
        first = _installer._write_agent_pointer(self.tmp, self.generic)
        self.assertEqual(first, "updated")
        self.assertTrue((self.tmp / "AGENTS.md.bak").exists(), "a real change backs up .bak first")
        (self.tmp / "AGENTS.md.bak").unlink()                      # clear, so a NEW .bak is detectable
        again = _installer._write_agent_pointer(self.tmp, self.generic)
        self.assertEqual(again, "unchanged", "a second identical write must be a no-op")
        self.assertFalse((self.tmp / "AGENTS.md.bak").exists(),
                         "an unchanged write must not leave a .bak")
        self.assertIn("user prose", agents.read_text(encoding="utf-8"),
                      "content outside the markers must survive")

    def test_init_supersedes_pointer_pip(self):                   # D7
        _installer._write_agent_pointer(self.tmp, self.claude)
        # the real engine's per-file injector replaces the marked region with the full block
        add_engine._inject_block(self.tmp / "CLAUDE.md")
        text = (self.tmp / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(text.count(add_engine._GUIDE_BEGIN), 1,
                         "sync-guidelines must replace the pointer in place — no duplicate block")
        self.assertIn("## ADD — how to work in this repo", text,
                      "the full guideline block must supersede the minimal pointer")

    def test_undecodable_integration_left_untouched(self):        # Reject integration_unreadable
        raw = "ADD:BEGIN".encode("utf-16")                        # not valid UTF-8
        (self.tmp / "CLAUDE.md").write_bytes(raw)
        action = _installer._write_agent_pointer(self.tmp, self.claude)
        self.assertEqual(action, "skipped")
        self.assertEqual((self.tmp / "CLAUDE.md").read_bytes(), raw,
                         "an undecodable target must be left byte-identical")

    def test_unwritable_integration_skips(self):                  # Reject integration_unwritable
        (self.tmp / "CLAUDE.md").mkdir()                          # a dir where a file is expected -> OSError
        action = _installer._write_agent_pointer(self.tmp, self.claude)
        self.assertEqual(action, "skipped", "an unwritable target must warn+skip, not raise")


# --- install flow: detect -> reconcile -> pointer -> agent next-step --------

class InstallFlowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="agent-inst-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bundled = _make_bundled(self.tmp / "pkg")
        self.proj = self.tmp / "proj"
        self.proj.mkdir()

    def _install(self, env, **kw):
        return _installer.install(target=str(self.proj), bundled=str(self.bundled),
                                  non_interactive=True, env=env, **kw)

    def test_closing_next_step_is_agent_specific_pip(self):       # D5
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = self._install({"CLAUDECODE": "1"})
        self.assertEqual(code, 0)
        self.assertIn("/add", buf.getvalue(), "the closing next-step must name the claude entry")

    def test_drop_writes_pointer_pip(self):                       # D6
        self._install({"CLAUDECODE": "1"})
        claude_md = self.proj / "CLAUDE.md"
        self.assertTrue(claude_md.exists(), "the detected agent's integration file must be written")
        self.assertEqual(claude_md.read_text(encoding="utf-8").count(add_engine._GUIDE_BEGIN), 1)

    def test_no_init_no_state_pip(self):                          # D9
        self._install({"CLAUDECODE": "1"})
        self.assertFalse((self.proj / ".add" / "state.json").exists(),
                         "the installer must create NO state.json")
        self.assertNotIn("spawnSync", CLI_JS.read_text(encoding="utf-8"),
                         "cli.js must not spawn a subprocess")

    def test_unwritable_pointer_does_not_abort_drop_pip(self):    # Reject integration_unwritable
        (self.proj / "CLAUDE.md").mkdir()                         # pointer write will hit OSError
        code = self._install({"CLAUDECODE": "1"})
        self.assertEqual(code, 0, "a failed pointer write must not abort a successful drop")
        self.assertTrue((self.proj / ".claude" / "skills" / "add" / "SKILL.md").exists(),
                        "the managed-layer drop must be intact")


# --- multi-agent-installer: the six new profiles ----------------------------
# Each agent's representative env signal -> expected (id, integration_file).
NEW_AGENTS = {
    "cursor":   ({"CURSOR_AGENT": "1"},  "AGENTS.md"),
    "windsurf": ({"WINDSURF": "1"},      "AGENTS.md"),
    "trae":     ({"TRAE_AI_IDE": "1"},   "AGENTS.md"),
    "copilot":  ({"COPILOT_AGENT": "1"}, "AGENTS.md"),
    "cline":    ({"CLINE_ACTIVE": "1"},  ".clinerules"),
    "aider":    ({"AIDER_MODEL": "1"},   "AGENTS.md"),   # detected via the AIDER_ prefix
}


class NewAgentProfilesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="new-agent-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_detect_each_new_agent_from_env(self):                # one Must
        for agent_id, (env, _file) in NEW_AGENTS.items():
            with self.subTest(agent=agent_id):
                self.assertEqual(_installer._detect_agent(env)["id"], agent_id)

    def test_integration_file_mapping(self):                      # one Must
        for agent_id, (env, expected_file) in NEW_AGENTS.items():
            with self.subTest(agent=agent_id):
                self.assertEqual(_installer._detect_agent(env)["integration_file"], expected_file)

    def test_unknown_and_empty_still_generic(self):               # detection invariants preserved
        self.assertEqual(_installer._detect_agent({})["id"], "generic")
        self.assertEqual(_installer._detect_agent({"CURSOR_AGENT": ""})["id"], "generic")

    def test_next_step_names_the_agent(self):                     # one Must
        for agent_id, (env, _file) in NEW_AGENTS.items():
            with self.subTest(agent=agent_id):
                self.assertTrue(_installer._detect_agent(env)["next_step"].strip(),
                                "every new profile carries a next_step")
        aider = _installer._detect_agent(NEW_AGENTS["aider"][0])
        self.assertIn("aider.conf", aider["next_step"].lower().replace(" ", ""),
                      "aider's next_step must name the config step it needs")

    def test_enriched_cli_probe_picks_new_agent(self):            # one Must (machine signal)
        prof = _installer._detect_agent_enriched({}, target=None, which=lambda c: c == "cursor")
        self.assertEqual(prof["id"], "cursor")
        # env signal still wins over the CLI probe
        prof2 = _installer._detect_agent_enriched({"WINDSURF": "1"}, target=None,
                                                  which=lambda c: c == "cursor")
        self.assertEqual(prof2["id"], "windsurf")

    def test_pointer_written_for_new_agent(self):                 # After
        cursor = _installer._detect_agent(NEW_AGENTS["cursor"][0])
        action = _installer._write_agent_pointer(self.tmp, cursor)
        self.assertEqual(action, "created")
        text = (self.tmp / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(text.count(add_engine._GUIDE_BEGIN), 1)

    def test_cline_writes_clinerules(self):                       # integration_file mapping
        cline = _installer._detect_agent(NEW_AGENTS["cline"][0])
        _installer._write_agent_pointer(self.tmp, cline)
        self.assertTrue((self.tmp / ".clinerules").exists(),
                        "cline's pointer goes to .clinerules")

    def test_unwritable_target_does_not_abort_drop(self):         # Reject integration_unwritable
        bundled = _make_bundled(self.tmp / "pkg")
        proj = self.tmp / "proj"
        proj.mkdir()
        (proj / "AGENTS.md").mkdir()                              # a dir where a file is expected
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = _installer.install(target=str(proj), bundled=str(bundled),
                                      non_interactive=True, env=NEW_AGENTS["cursor"][0])
        self.assertEqual(code, 0, "a failed pointer write must not abort the drop")
        self.assertTrue((proj / ".claude" / "skills" / "add" / "SKILL.md").exists())


# --- npm: real packaged sources via subprocess ------------------------------

@unittest.skipUnless(NODE, "node not on PATH — npx-side agent-detect checks skipped (honest skip)")
class NpmAgentTest(unittest.TestCase):
    def _init(self, cwd, env_extra):
        env = dict(os.environ)
        env.pop("CI", None)
        env.update(env_extra)
        return subprocess.run([NODE, str(CLI_JS), "init", "--yes"], cwd=cwd,
                              capture_output=True, text=True, timeout=120, env=env)

    def test_detect_claude_from_env_npm(self):                    # D2, D5, D10
        with tempfile.TemporaryDirectory(prefix="agent-npm-") as tmp:
            res = self._init(tmp, {"CLAUDECODE": "1"})
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue((Path(tmp) / "CLAUDE.md").exists(),
                            "a Claude install must write CLAUDE.md")
            self.assertIn("/add", res.stdout)

    def test_detect_each_new_agent_npm(self):                     # multi-agent-installer (twin parity, live cli.js)
        for agent_id, (env_extra, expected_file) in NEW_AGENTS.items():
            with self.subTest(agent=agent_id), tempfile.TemporaryDirectory(prefix="new-agent-npm-") as tmp:
                env = dict(os.environ)
                for k in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CI"):
                    env.pop(k, None)               # claude/CI must not pre-empt the agent signal
                env.update(env_extra)
                res = subprocess.run([NODE, str(CLI_JS), "init", "--yes"], cwd=tmp,
                                     capture_output=True, text=True, timeout=120, env=env)
                self.assertEqual(res.returncode, 0, res.stderr)
                self.assertTrue((Path(tmp) / expected_file).exists(),
                                f"{agent_id} install must write {expected_file}")

    def test_unknown_generic_npm(self):                           # D4, D10
        with tempfile.TemporaryDirectory(prefix="agent-npm-") as tmp:
            env = dict(os.environ)
            for k in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT"):
                env.pop(k, None)
            env.pop("CI", None)
            res = subprocess.run([NODE, str(CLI_JS), "init", "--yes"], cwd=tmp,
                                 capture_output=True, text=True, timeout=120, env=env)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue((Path(tmp) / "AGENTS.md").exists(),
                            "an unknown agent must get the generic AGENTS.md")


# --- parity: same registry in both twins ------------------------------------

class ParityTest(unittest.TestCase):
    def test_parity_profiles(self):                               # D10 structural
        js = CLI_JS.read_text(encoding="utf-8")
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        for token in ("claude", "codex", "opencode", "generic", "CLAUDECODE", "AGENTS.md", "CLAUDE.md"):
            self.assertIn(token, js, f"cli.js profile registry must mention '{token}'")
            self.assertIn(token, py, f"_installer.py profile registry must mention '{token}'")

    def test_parity_six_new_profiles(self):                       # multi-agent-installer
        js = CLI_JS.read_text(encoding="utf-8")
        py = (_SRC / "add_method" / "_installer.py").read_text(encoding="utf-8")
        for token in ("cursor", "windsurf", "trae", "copilot", "cline", "aider", ".clinerules"):
            self.assertIn(token, js, f"cli.js must enumerate the new profile token '{token}'")
            self.assertIn(token, py, f"_installer.py must enumerate the new profile token '{token}'")


if __name__ == "__main__":
    unittest.main(verbosity=2)
