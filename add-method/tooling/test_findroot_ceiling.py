#!/usr/bin/env python3
"""Red/green tests for harness-workspace-isolation (orientation-honesty, frozen §3 v1).

`find_root` gains an OPT-IN env ceiling `ADD_ROOT_CEILING`: the upward walk stops at
that dir (inclusive), so a workspace nested under an ancestor `.add/` resolves its OWN
project — never the parent. Env unset MUST be byte-identical to the legacy walk.

Env is scoped with patch.dict so it never leaks into sibling add_engine tests.

Run: python3 -m unittest test_findroot_ceiling -v
"""
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from add_engine import io_state
from add_engine.constants import ROOT_DIRNAME, STATE_FILE


class _Nested(unittest.TestCase):
    def setUp(self):
        # A/ is a real project (A/.add/state.json); W = A/work is a fresh nested
        # workspace with no .add/ of its own; sub is a subdir of W.
        self.A = Path(tempfile.mkdtemp(prefix="add-fr-")).resolve()
        self.addCleanup(shutil.rmtree, self.A, ignore_errors=True)
        (self.A / ROOT_DIRNAME).mkdir()
        (self.A / ROOT_DIRNAME / STATE_FILE).write_text(json.dumps({"schema": 1}))
        self.W = self.A / "work"
        self.sub = self.W / "sub"
        self.sub.mkdir(parents=True)

    def _seed_workspace_project(self):
        (self.W / ROOT_DIRNAME).mkdir()
        (self.W / ROOT_DIRNAME / STATE_FILE).write_text(json.dumps({"schema": 1}))


class CeilingTest(_Nested):
    def test_ancestor_above_ceiling_not_resolved(self):
        # env=W, W has no .add/ yet -> the ancestor A/.add above the ceiling is NOT resolved.
        with mock.patch.dict(os.environ, {"ADD_ROOT_CEILING": str(self.W)}):
            self.assertIsNone(io_state.find_root(self.W),
                              "a project ABOVE the ceiling must not be resolved")
        # and A/.add/state.json is untouched
        self.assertTrue((self.A / ROOT_DIRNAME / STATE_FILE).exists())

    def test_env_unset_preserves_legacy_walk(self):
        env = {k: v for k, v in os.environ.items() if k != "ADD_ROOT_CEILING"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(io_state.find_root(self.W), self.A / ROOT_DIRNAME,
                             "env unset must walk to the ancestor exactly as today")

    def test_workspace_own_project_resolves_under_ceiling(self):
        self._seed_workspace_project()
        with mock.patch.dict(os.environ, {"ADD_ROOT_CEILING": str(self.W)}):
            self.assertEqual(io_state.find_root(self.W), self.W / ROOT_DIRNAME,
                             "the ceiling bounds the TOP, never the workspace's own root")
            self.assertEqual(io_state.find_root(self.sub), self.W / ROOT_DIRNAME,
                             "a subdir under the ceiling still resolves the workspace root")

    def test_ceiling_off_the_chain_falls_open(self):
        # ceiling that isn't an ancestor of cwd -> break never fires -> legacy walk.
        off = Path(tempfile.mkdtemp(prefix="add-off-")).resolve()
        self.addCleanup(shutil.rmtree, off, ignore_errors=True)
        with mock.patch.dict(os.environ, {"ADD_ROOT_CEILING": str(off)}):
            self.assertEqual(io_state.find_root(self.W), self.A / ROOT_DIRNAME,
                             "an off-chain ceiling must not redirect; walk proceeds")


if __name__ == "__main__":
    unittest.main()
