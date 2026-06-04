#!/usr/bin/env python3
"""Tests for the runnable Quickstart guide (add-method/GETTING-STARTED.md).

The guide is the artifact under test: we assert it exists, documents the real
commands, and that its golden command spine actually drives a project to a PASS.
Run: python3 -m unittest test_quickstart -v
"""
import argparse
import os
import re
import tempfile
import unittest
from pathlib import Path

import add

GUIDE = Path(__file__).resolve().parent.parent / "GETTING-STARTED.md"

REQUIRED_STRINGS = [
    "npx @pilotspace/add init",      # npm install path
    "pip install pilotspace-add",    # PyPI install path — must be documented too
    "pilotspace-add init",           # the console-script the pip package exposes
    "add.py status",
    "add.py new-task",
    "add.py advance",
    "add.py gate PASS",
    "add.py check",
    "add.py guide",
]


class QuickstartGuideTest(unittest.TestCase):
    def _text(self) -> str:
        return GUIDE.read_text(encoding="utf-8")

    def test_guide_exists(self):
        self.assertTrue(GUIDE.exists(), f"missing {GUIDE}")

    def test_guide_contains_required_commands(self):
        text = self._text()
        for s in REQUIRED_STRINGS:
            self.assertIn(s, text, f"guide must document: {s}")

    def test_documented_commands_are_real(self):
        # every `add.py <word>` mentioned must be a real subcommand — derive the valid
        # set from the parser (future-proof: new commands are recognised automatically)
        sub = next(a for a in add.build_parser()._actions
                   if isinstance(a, argparse._SubParsersAction))
        valid = set(sub.choices) | set(add.PHASES)
        tokens = set(re.findall(r"add\.py\s+([a-z\-]+)", self._text()))
        unknown = {t for t in tokens if t not in valid}
        self.assertFalse(unknown, f"guide references unknown commands: {unknown}")

    def test_golden_spine_reaches_pass(self):
        # the command spine the guide teaches must drive a project to done/PASS
        cwd = Path.cwd()
        tmp = tempfile.mkdtemp(prefix="quickstart-")
        try:
            os.chdir(tmp)
            add.main(["init", "--name", "demo", "--stage", "mvp"])
            add.main(["new-task", "transfer", "--title", "Transfer money"])
            for _ in range(5):  # specify -> scenarios -> contract -> tests -> build -> verify
                add.main(["advance"])
            add.main(["gate", "PASS"])
            import json
            state = json.loads((Path(tmp) / ".add" / "state.json").read_text())
            self.assertEqual(state["tasks"]["transfer"]["phase"], "done")
            self.assertEqual(state["tasks"]["transfer"]["gate"], "PASS")
        finally:
            os.chdir(cwd)


if __name__ == "__main__":
    unittest.main(verbosity=2)
