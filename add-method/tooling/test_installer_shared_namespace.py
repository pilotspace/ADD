#!/usr/bin/env python3
"""Red/green tests for installer-shared-namespace-guard (fast lane, frozen v1):
`.claude/agents` is a SHARED namespace — the user's own Claude Code subagents
live there. ADD's install/update may own only its shipped roster files (per-file
atomic landings + an explicit tombstone list, empty today), never the directory.
The reported bug: the whole-dir clean-replace swept every non-ADD agent as an
orphan. Every other managed tree keeps whole-dir clean-replace unchanged.

Run: python3 -m unittest test_installer_shared_namespace -v
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent          # add-method/
CLI_JS = PKG_ROOT / "bin" / "cli.js"
SRC_DIR = PKG_ROOT / "src"
AGENTS_SRC = PKG_ROOT / "agents"
NODE = shutil.which("node")

FOREIGN = "my-custom-agent.md"
FOREIGN_BODY = "# my agent\nuser-owned; ADD must never touch this file.\n"
PREFIXED_FOREIGN = "add-custom-of-mine.md"                  # tests the no-prefix-heuristic rule


def _baseline_env():
    env = dict(os.environ)
    for k in list(env):
        if k in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT") or k.startswith(("CODEX_", "OPENCODE")):
            env.pop(k, None)
    return env


def _run_node(args, cwd):
    return subprocess.run([NODE, str(CLI_JS), *args], cwd=cwd, capture_output=True,
                          text=True, timeout=120, env=_baseline_env())


def _run_pip(args, cwd):
    env = _baseline_env()
    env["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    code = ("import sys; from add_method._cli import main; "
            "sys.exit(main(sys.argv[1:]))")
    return subprocess.run([sys.executable, "-c", code, *args], cwd=cwd,
                          capture_output=True, text=True, timeout=120, env=env)


class _Harness(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="add-isn-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _seed_foreign(self):
        agents = self.tmp / ".claude" / "agents"
        agents.mkdir(parents=True, exist_ok=True)
        (agents / FOREIGN).write_text(FOREIGN_BODY, encoding="utf-8")
        (agents / PREFIXED_FOREIGN).write_text(FOREIGN_BODY, encoding="utf-8")
        return agents

    def _assert_shared_semantics(self, agents: Path, out: str):
        self.assertEqual((agents / FOREIGN).read_text(encoding="utf-8"), FOREIGN_BODY,
                         f"user agent must survive byte-identical: {out}")
        self.assertEqual((agents / PREFIXED_FOREIGN).read_text(encoding="utf-8"),
                         FOREIGN_BODY,
                         "an add- prefixed USER file survives too — removal is "
                         "tombstone-only, never a name heuristic")
        for f in sorted(AGENTS_SRC.glob("*.md")):
            self.assertEqual((agents / f.name).read_bytes(), f.read_bytes(),
                             f"shipped roster file must land/refresh: {f.name}")


@unittest.skipUnless(NODE, "node not on PATH — npm-side check skipped (honest skip)")
class NodeInstallerSharedNamespaceTest(_Harness):
    def test_init_preserves_foreign_agents(self):              # M1 + M2 + Accept
        agents = self._seed_foreign()
        r = _run_node(["init"], cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self._assert_shared_semantics(agents, r.stdout + r.stderr)

    def test_update_preserves_foreign_and_refreshes_roster(self):   # M1 + M2 + Accept
        agents = self._seed_foreign()
        r = _run_node(["init"], cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (agents / "add-verify.md").write_text("stale local edit", encoding="utf-8")
        r2 = _run_node(["update"], cwd=self.tmp)
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        self._assert_shared_semantics(agents, r2.stdout + r2.stderr)

    def test_fresh_dir_created_with_roster(self):              # Boundary (fresh)
        r = _run_node(["init"], cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        agents = self.tmp / ".claude" / "agents"
        for f in sorted(AGENTS_SRC.glob("*.md")):
            self.assertTrue((agents / f.name).exists(), f"roster missing: {f.name}")

    def test_non_shared_tree_still_sweeps_orphans(self):       # M4 (tooling keeps clean-replace)
        r = _run_node(["init"], cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        orphan = self.tmp / ".add" / "tooling" / "zz-orphan.md"
        orphan.write_text("upstream-removed leftover", encoding="utf-8")
        r2 = _run_node(["update"], cwd=self.tmp)
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        self.assertFalse(orphan.exists(),
                         "non-shared managed trees must keep whole-dir clean-replace")


class PipInstallerSharedNamespaceTest(_Harness):
    def test_init_preserves_foreign_agents(self):              # M1 + M2 + Accept
        agents = self._seed_foreign()
        r = _run_pip(["init"], cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self._assert_shared_semantics(agents, r.stdout + r.stderr)

    def test_update_preserves_foreign_and_refreshes_roster(self):   # M1 + M2 + Accept
        agents = self._seed_foreign()
        r = _run_pip(["init"], cwd=self.tmp)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (agents / "add-verify.md").write_text("stale local edit", encoding="utf-8")
        r2 = _run_pip(["update"], cwd=self.tmp)
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        self._assert_shared_semantics(agents, r2.stdout + r2.stderr)

    def test_tombstoned_name_is_removed(self):                 # M3 (explicit list, unit seam)
        sys.path.insert(0, str(SRC_DIR))
        try:
            from add_method import _installer
        finally:
            sys.path.pop(0)
        # roster-distill (ADD 2.0 M1): the 5-agent roster is tombstoned — update removes
        # exactly these names from the shared namespace, never a sweep or heuristic.
        self.assertEqual(getattr(_installer, "_RETIRED_AGENTS", None),
                         ("add-design.md", "add-build.md", "add-verify.md",
                          "add-persona.md", "add-advisor.md"),
                         "_RETIRED_AGENTS must name exactly the retired 5-agent roster")
        agents = self._seed_foreign()
        (agents / "add-observe.md").write_text("retired roster leftover", encoding="utf-8")
        original = _installer._RETIRED_AGENTS
        _installer._RETIRED_AGENTS = ("add-observe.md",)
        try:
            _installer._shared_file_replace(AGENTS_SRC, agents)
        finally:
            _installer._RETIRED_AGENTS = original
        self.assertFalse((agents / "add-observe.md").exists(),
                         "a tombstoned name must be removed")
        self.assertEqual((agents / FOREIGN).read_text(encoding="utf-8"), FOREIGN_BODY,
                         "tombstone removal must not touch foreign files")

    def test_shared_lander_reports_rollup_shape(self):         # contract: {restored, refreshed}
        sys.path.insert(0, str(SRC_DIR))
        try:
            from add_method import _installer
        finally:
            sys.path.pop(0)
        agents = self.tmp / ".claude" / "agents"        # fresh: all restored
        roll = _installer._shared_file_replace(AGENTS_SRC, agents)
        n = len(list(AGENTS_SRC.glob("*.md")))
        self.assertEqual(roll, {"restored": n, "refreshed": 0})
        roll2 = _installer._shared_file_replace(AGENTS_SRC, agents)
        self.assertEqual(roll2, {"restored": 0, "refreshed": n})


if __name__ == "__main__":
    unittest.main()
