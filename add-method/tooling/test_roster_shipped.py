#!/usr/bin/env python3
"""Red/green tests for roster-install-drift (direct chat-directed task `roster-install-drift`,
Fix B of the apple-container transcript audit): the CLAUDE.md/AGENTS.md/.clinerules guideline
block unconditionally cites the agent roster ("Roster (from `add-method/agents/*.md`..."), but
neither npm's `files` allowlist nor the Python wheel's `_bundled/` ever shipped an `agents/`
directory at all — a pip/npm-only consumer project (no Claude Code plugin) gets a roster
citation that can NEVER resolve; there was also no mechanical signal anywhere that this is
the case. `add-method/agents/` + `.claude/agents/` (the dev-repo's own 2-tree parity, covered
by test_agent_roster.py) are UNAFFECTED — this closes the gap for shipped consumer packages.

CONTRACT (direct chat-directed, no formal frozen §3) — MEASURE-NOT-BLOCK for the new check:
  packaging: npm `files` ships `agents/`; the Python wheel ships `_bundled/agents/*.md`
    (byte-identical to `add-method/agents/`, extending test_agent_roster.py's own parity).
  materialization: _installer.py's MANAGED gains ("agents", ".claude/agents", False), OPTIONAL
    gains "agents" (soft-skip, mirrors personas-teacher — an enhancement, not core runtime);
    bin/cli.js's MANAGED gains the matching ["agents", [".claude", "agents"], false] entry.
  prose: add_engine.guidelines._guideline_block() is UNCHANGED — still cites
    `add-method/agents/*.md` (attribution/provenance, not a claim that the path resolves on
    disk). An earlier attempt in this same task to reword it to `.claude/agents/*.md` broke
    the FROZEN test_roster_portable.py contract (portable-roster, §3 FROZEN @ v1): that block
    is shared verbatim into AGENTS.md/.clinerules too, and `.claude/agents` is a Claude-only
    mechanism a Cursor/Copilot/Codex reader has no use for. Reverted; see GuidelineBlockStaysPortable
    below. The resolution guarantee for Claude Code users comes from packaging + the installer
    materializing to `.claude/agents/`, not from what the prose string says.
  check: `add.py check` gains `roster_uninstalled` — WARN (never red) when a guideline file
    cites the roster but `.claude/agents/add-*.md` is missing from the project; silent when
    the roster resolves, and silent when no guideline file cites a roster at all (an older
    block, or a project that never ran sync-guidelines — never retro-flagged). Detection keys
    off the generic `agents/*.md` tail so it fires the same regardless of citation prefix.

Scoped OUT (disclosed, not silently dropped): the GLOBAL_TREES / _GLOBAL_TREES `--global`
install mirror — a less common, opt-in path; the per-project MANAGED fix above already closes
the gap for the overwhelming majority of installs.

Run: python3 -m unittest test_roster_shipped -v
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent
_SRC = _ADD_METHOD / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import add                                    # noqa: E402
from add_method import _installer             # noqa: E402
from add_engine.guidelines import _guideline_block   # noqa: E402

CLI_JS = _ADD_METHOD / "bin" / "cli.js"
PACKAGE_JSON = _ADD_METHOD / "package.json"
CANON_AGENTS = _ADD_METHOD / "agents"
BUNDLED_AGENTS = _ADD_METHOD / "src" / "add_method" / "_bundled" / "agents"
AGENT_NAMES = ("add-worker.md", "add-advisor.md")   # advisor-split: worker + advisor


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class PackagingShipsAgents(unittest.TestCase):
    def test_npm_files_array_ships_agents(self):
        pkg = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
        self.assertIn("agents/", pkg.get("files", []),
                     "package.json's files allowlist must ship agents/")


class PythonInstallerManifest(unittest.TestCase):
    def test_managed_has_agents_entry(self):
        self.assertIn(("agents", ".claude/agents", False), _installer.MANAGED,
                     "_installer.MANAGED must materialize agents/ -> .claude/agents")

    def test_agents_is_optional(self):
        self.assertIn("agents", _installer.OPTIONAL,
                     "agents must soft-skip like personas-teacher (enhancement, not core runtime)")


def _make_bundled_with_agents(root: Path) -> Path:
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill v-new\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py v-new\n")
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "00-introduction.md").write_text("intro v-new\n")
    (root / "agents").mkdir(parents=True)
    # advisor-split: the roster is add-worker + add-advisor (add.md is a tombstone now)
    (root / "agents" / "add-worker.md").write_text("---\nname: add-worker\n---\nworker agent v-new\n")
    (root / "agents" / "add-advisor.md").write_text("---\nname: add-advisor\n---\nadvisor agent v-new\n")
    return root


def _make_bundled_without_agents(root: Path) -> Path:
    """A bundled source predating this fix — agents/ absent entirely (soft-skip proof)."""
    (root / "skill" / "add").mkdir(parents=True)
    (root / "skill" / "add" / "SKILL.md").write_text("skill v-old-shape\n")
    (root / "tooling").mkdir(parents=True)
    (root / "tooling" / "add.py").write_text("# add.py v-old-shape\n")
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "00-introduction.md").write_text("intro v-old-shape\n")
    return root


class PythonInstallerBehavior(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="add-roster-install-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_install_materializes_agents_into_dot_claude(self):
        bundled = _make_bundled_with_agents(self.tmp / "pkg")
        proj = self.tmp / "proj"
        proj.mkdir()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = _installer.install(target=str(proj), bundled=str(bundled),
                                      yes=True, non_interactive=True)
        self.assertEqual(code, 0, buf.getvalue())
        installed = proj / ".claude" / "agents" / "add-worker.md"
        self.assertTrue(installed.is_file(), "install() must materialize agents/ -> .claude/agents")
        self.assertEqual(installed.read_text(), "---\nname: add-worker\n---\nworker agent v-new\n")
        self.assertTrue((proj / ".claude" / "agents" / "add-advisor.md").is_file(),
                        "install() must materialize the whole roster, advisor included")

    def test_update_preserves_undeclared_agents(self):
        # SUPERSEDED PIN (installer-shared-namespace-guard, frozen v1): .claude/agents is a
        # SHARED namespace — the user's own subagents live there, so update lands the shipped
        # files per-file and removes ONLY explicit _RETIRED_AGENTS tombstones. The old pin
        # ("update must clean-replace agents/, sweep orphans") demanded the data-loss bug:
        # any undeclared file — the user's included — was deleted. Strengthened, not weakened:
        # survival is asserted for BOTH an add- prefixed undeclared file (no name heuristic)
        # and the shipped files' refresh, and the tombstone path is pinned separately in
        # test_installer_shared_namespace.py.
        bundled = _make_bundled_with_agents(self.tmp / "pkg")
        proj = self.tmp / "proj"
        proj.mkdir()
        with contextlib.redirect_stdout(io.StringIO()):
            _installer.install(target=str(proj), bundled=str(bundled), yes=True, non_interactive=True)
        stale = proj / ".claude" / "agents" / "add-stale.md"
        stale.write_text("# undeclared — must SURVIVE (tombstone-only removal)\n")
        with contextlib.redirect_stdout(io.StringIO()):
            code = _installer.update(target=str(proj), bundled=str(bundled), version="2.0.0")
        self.assertEqual(code, 0)
        self.assertTrue(stale.exists(),
                        "an undeclared file in the shared namespace survives update — "
                        "removal is tombstone-only, never a sweep or a name heuristic")
        self.assertEqual((proj / ".claude" / "agents" / "add-worker.md").read_text(),
                         "---\nname: add-worker\n---\nworker agent v-new\n",
                         "shipped roster files still refresh")

    def test_missing_agents_in_bundled_soft_skips(self):
        """A bundled source predating this fix (no agents/ at all) must NOT abort install —
        soft-skip, exactly like an older package missing personas-teacher/."""
        bundled = _make_bundled_without_agents(self.tmp / "pkg")
        proj = self.tmp / "proj"
        proj.mkdir()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = _installer.install(target=str(proj), bundled=str(bundled),
                                      yes=True, non_interactive=True)
        self.assertEqual(code, 0, f"a package missing agents/ must still install cleanly:\n{buf.getvalue()}")
        self.assertFalse((proj / ".claude" / "agents").exists())
        # the core managed trees still landed
        self.assertTrue((proj / ".add" / "tooling" / "add.py").is_file())


class CliJsManifestParity(unittest.TestCase):
    """bin/cli.js must expose the SAME agents entry (npm <-> pip parity, static per house style —
    see test_update.py's TwinParityTest for the same text-assertion convention)."""

    def test_managed_array_has_agents_entry(self):
        src = CLI_JS.read_text(encoding="utf-8")
        self.assertIn('["agents", [".claude", "agents"], false]', src,
                     "cli.js's MANAGED array must carry the matching agents entry")

    def test_agents_added_to_optional_set(self):
        src = CLI_JS.read_text(encoding="utf-8")
        self.assertRegex(src, r'OPTIONAL\s*=\s*new Set\(\[[^\]]*"agents"[^\]]*\]\)',
                         "cli.js's OPTIONAL set must include \"agents\" (soft-skip, mirrors personas-teacher)")


class GuidelineBlockStaysPortable(unittest.TestCase):
    """roster-install-drift must NOT regress portable-roster (§3 FROZEN @ v1). The shared block
    is injected into AGENTS.md/.clinerules verbatim, so it may not carry a Claude-only mechanism —
    mirrors test_roster_portable.py's own frozen assertion as a same-task tripwire."""

    def test_no_claude_only_leak(self):
        block = _guideline_block()
        self.assertNotIn(".claude/agents", block,
                         "roster_claude_only_leak: the shared block must stay tool-agnostic — "
                         "cite add-method/agents/*.md (attribution), never a Claude-only path")

    def test_still_cites_roster_for_attribution(self):
        block = _guideline_block()
        self.assertIn("agents/*.md", block,
                     "the roster line must still name its source (add-worker + add-advisor) — "
                     "roster_uninstalled below detects drift from the real .claude/agents/ "
                     "tree, independent of this prose")


class RosterUninstalledCheckLint(unittest.TestCase):
    """add.py check's new project-level, presence-gated, measure-not-block WARN."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="add-roster-check-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self._cwd = Path.cwd()
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)

    def _silent(self, *argv):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                add.main(list(argv))
        except SystemExit as e:
            if e.code:
                raise AssertionError(f"{argv} exited {e.code}: {buf.getvalue()}")
        return buf.getvalue()

    def _run(self, *argv):
        out = io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                add.main(list(argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return code, out.getvalue()

    def test_fires_when_roster_cited_but_not_installed(self):
        self._silent("init", "--name", "demo", "--stage", "mvp")
        # sync-guidelines already wrote CLAUDE.md carrying the (now .claude/agents) roster line;
        # no .claude/agents/add-*.md exists in this fresh init -> the drift is real
        code, out = self._run("check")
        self.assertIn("roster_uninstalled", out)
        self.assertEqual(code, 0, "measure-not-block: a WARN must never fail check")

    def test_clears_when_roster_installed(self):
        self._silent("init", "--name", "demo", "--stage", "mvp")
        agents_dir = self.tmp / ".claude" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "add-worker.md").write_text("---\nname: add-worker\n---\n")
        _, out = self._run("check")
        self.assertNotIn("roster_uninstalled", out)

    def test_json_never_fails_on_the_warn(self):
        self._silent("init", "--name", "demo", "--stage", "mvp")
        code, out = self._run("check", "--json")
        data = json.loads(out)
        self.assertEqual(code, 0)
        self.assertTrue(any(w["name"] == "roster_uninstalled" for w in data["warnings"]),
                        f"--json must carry the same warning: {data['warnings']}")

    def test_no_new_hard_reject_code(self):
        src = (_TOOLING / "add.py").read_text(encoding="utf-8")
        self.assertNotIn("roster_uninstalled_missing", src,
                         "measure-not-block: no hard-gate reject code may ship for this lint")


if __name__ == "__main__":
    unittest.main(verbosity=2)
