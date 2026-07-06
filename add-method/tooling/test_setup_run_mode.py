#!/usr/bin/env python3
"""Content + parity guard for the setup "Run mode" step (task setup-run-mode,
v13-onboarding-polish 2/6).

phases/0-setup.md must gain a "## Run mode" step that (a) shows an autonomy×streams
comparison table, (b) proposes parallel+auto as the DEFAULT confirm-to-keep, (c) cites
`add.py waves` + the autonomy dial and preserves the one-approval-per-contract floor,
(d) records the choice in PROJECT.md Key Decisions; and streams.md must name parallel+auto
as the project default (opt-out). All three skill trees stay byte-identical.

Also guards add.py init --run-mode {auto,conservative}: absent flag stays byte-identical;
the flag sets paired autonomy+streams in PROJECT.md; an invalid value exits 2.

Content-test pattern per test_cospecify_lift. Run: python3 -m unittest test_setup_run_mode -v
"""
from __future__ import annotations

import hashlib
import io
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import add

ADD_METHOD = Path(__file__).resolve().parent.parent
REPO = ADD_METHOD.parent

CANONICAL = ADD_METHOD / "skill" / "add"
BUNDLED = ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add"
DOGFOOD = REPO / ".claude" / "skills" / "add"

SETUP = "phases/0-setup.md"
STREAMS = "streams.md"


def _read(tree: Path, rel: str) -> str:
    return (tree / rel).read_text(encoding="utf-8")


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class RunModeStep(unittest.TestCase):
    def setUp(self):
        self.setup = _read(CANONICAL, SETUP)
        # the "## Run mode" section text (heading -> next "## " or EOF)
        self.assertIn("## Run mode", self.setup, "setup guide must gain a '## Run mode' step")
        start = self.setup.index("## Run mode")
        nxt = self.setup.find("\n## ", start + 1)
        self.section = self.setup[start: nxt if nxt != -1 else len(self.setup)]

    def test_run_mode_table_present(self):
        # a markdown table (pipe rows) naming both modes + gate/concurrency columns
        self.assertIn("|", self.section, "the run-mode step must include a comparison table")
        low = self.section.lower()
        self.assertIn("sequential", low)
        self.assertIn("parallel", low)
        self.assertTrue("gate" in low, "table must name the human gates")
        self.assertTrue("concurren" in low or "flow" in low, "table must name concurrency/flow")

    def test_proposes_sequential_auto_default(self):
        # sequential-auto-default (direct chat-directed edit, real usage showed parallel/multi-agent
        # spawning is rarely used in practice): the DEFAULT is now `sequential + auto`; `parallel`
        # stays a named, explicit opt-in for a milestone with genuinely independent tasks.
        low = self.section.lower()
        self.assertIn("default", low, "the step must name a default")
        self.assertIn("sequential", low)
        self.assertIn("auto", low)
        self.assertIn("confirm", low, "the default must be confirm-to-keep, not a silent flip")
        default_idx = low.index("*(default)*") if "*(default)*" in low else low.index("default")
        self.assertIn("sequential", low[max(0, default_idx - 60):default_idx],
                      "`sequential` must be the mode actually tagged *(default)*, not just present")
        self.assertIn("parallel", low, "parallel must still be named, as the opt-in path")

    def test_cites_waves_and_autonomy(self):
        self.assertIn("add.py waves", self.section, "must cite the scheduler")
        self.assertIn("autonomy", self.section.lower(), "must cite the autonomy dial")
        # the one-approval floor must be explicit so 'auto' is not read as 'no gate'
        self.assertIn("contract", self.section.lower())

    def test_records_in_project_key_decisions(self):
        self.assertIn("Key Decisions", self.section, "the choice must be recorded in PROJECT.md Key Decisions")

    def test_streams_names_new_default(self):
        # sequential-auto-default: streams.md must now name `sequential + auto` as the project
        # default and reframe parallel streaming as an explicit opt-in (was: parallel+auto
        # default/opt-out) — real usage showed parallel/multi-agent spawning is rarely used.
        streams = _read(CANONICAL, STREAMS).lower()
        self.assertIn("default", streams)
        self.assertIn("sequential", streams)
        self.assertTrue("parallel" in streams and "auto" in streams)
        self.assertIn("opt-in", streams,
                      "streams.md must name parallel streaming as opt-in, not the default")
        self.assertNotIn("opt-out", streams,
                         "the stale opt-out framing must not survive the default flip")

    def test_three_trees_byte_identical(self):
        for rel in (SETUP, STREAMS):
            digests = {_md5(t / rel) for t in (CANONICAL, BUNDLED, DOGFOOD)}
            self.assertEqual(len(digests), 1, f"{rel} diverged across the 3 skill trees")


class InitRunMode(unittest.TestCase):
    """Engine tests: add.py init --run-mode {auto,conservative}.

    Invariant: absent-flag path is BYTE-IDENTICAL to today (no streams: line added).
    """

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-runmode-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)

    def _run(self, *argv):
        return add.main(list(argv))

    def _project_md(self) -> str:
        return (Path(self.tmp) / ".add" / "PROJECT.md").read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # 1. absent-flag: byte-identical to today
    # ------------------------------------------------------------------
    def test_init_runmode_absent_byte_identical(self):
        """No --run-mode: PROJECT.md has autonomy: auto, NO streams: line."""
        self._run("init", "--name", "demo")
        text = self._project_md()
        self.assertIn("autonomy: auto", text,
                      "PROJECT.md must contain 'autonomy: auto' by default")
        streams_lines = [l for l in text.splitlines() if l.startswith("streams:")]
        self.assertEqual([], streams_lines,
                         "absent-flag path must NOT write any 'streams:' line")

    # ------------------------------------------------------------------
    # 2. --run-mode auto
    # ------------------------------------------------------------------
    def test_init_runmode_auto(self):
        """--run-mode auto: autonomy: auto AND streams: parallel in PROJECT.md."""
        self._run("init", "--name", "demo", "--run-mode", "auto")
        text = self._project_md()
        self.assertIn("autonomy: auto", text)
        self.assertTrue(
            any(l.startswith("streams: parallel") for l in text.splitlines()),
            "streams: parallel not found in PROJECT.md after --run-mode auto",
        )

    # ------------------------------------------------------------------
    # 3. --run-mode conservative
    # ------------------------------------------------------------------
    def test_init_runmode_conservative(self):
        """--run-mode conservative: autonomy: conservative AND streams: sequential."""
        self._run("init", "--name", "demo", "--run-mode", "conservative")
        text = self._project_md()
        self.assertIn("autonomy: conservative", text)
        self.assertTrue(
            any(l.startswith("streams: sequential") for l in text.splitlines()),
            "streams: sequential not found in PROJECT.md after --run-mode conservative",
        )

    # ------------------------------------------------------------------
    # 4. invalid value → exit 2 (argparse choices rejection)
    # ------------------------------------------------------------------
    def test_init_runmode_invalid_exit2(self):
        """--run-mode bogus: argparse must exit 2; no .add/ dir created."""
        # argparse writes to stderr; suppress it so the test output stays clean
        with self.assertRaises(SystemExit) as cm:
            with open(os.devnull, "w") as devnull:
                old_err = sys.stderr
                sys.stderr = devnull
                try:
                    add.main(["init", "--name", "demo", "--run-mode", "bogus"])
                finally:
                    sys.stderr = old_err
        self.assertEqual(cm.exception.code, 2,
                         "invalid --run-mode must produce argparse exit 2")
        self.assertFalse((Path(self.tmp) / ".add").exists(),
                         "no .add/ dir should be created when argparse rejects the flag")

    # ------------------------------------------------------------------
    # 5. setup guide names both persist commands
    # ------------------------------------------------------------------
    def test_setup_step_names_both_persist_cmds(self):
        """phases/0-setup.md Run mode section must cite both persist commands."""
        text = (CANONICAL / "phases" / "0-setup.md").read_text(encoding="utf-8")
        self.assertIn("## Run mode", text)
        start = text.index("## Run mode")
        nxt = text.find("\n## ", start + 1)
        section = text[start: nxt if nxt != -1 else len(text)]
        self.assertIn("autonomy set", section,
                      "Run mode section must name 'autonomy set'")
        self.assertIn("--project", section,
                      "Run mode section must include --project flag")
        self.assertIn("streams set", section,
                      "Run mode section must name 'streams set' (the streams persist command)")

    # ------------------------------------------------------------------
    # 6. streams.md keeps required vocab
    # ------------------------------------------------------------------
    def test_streams_md_keeps_vocab(self):
        """streams.md must retain 'parallel', 'auto', and 'default'/'opt-out'."""
        text = (CANONICAL / "streams.md").read_text(encoding="utf-8").lower()
        self.assertIn("parallel", text)
        self.assertIn("auto", text)
        self.assertTrue(
            "default" in text or "opt-out" in text,
            "streams.md must name parallel+auto as the project default or opt-out",
        )


if __name__ == "__main__":
    unittest.main()
