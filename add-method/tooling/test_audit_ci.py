#!/usr/bin/env python3
"""Red/green tests for the audit-ci wiring (task audit-ci, milestone v14).

The gate-audit engine is FROZEN (gate-audit @ v1) — this task only WIRES it:
a distinct `seam-audit` job in .github/workflows/ci.yml and a copy-paste
consumer workflow in GETTING-STARTED.md. The wiring is tested behaviorally:
the literal `run:` command is EXTRACTED from ci.yml and executed via
subprocess in an installed-layout fixture (.add/tooling/add.py — the path the
npm/PyPI installer creates), so the exact string CI runs is proven to fail on
a malformed seam record and pass on a clean board. Requires `python3` on PATH
(true on dev machines and ubuntu-latest). Run:
    python3 -m unittest test_audit_ci -v
"""
import io
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add
import md_section
import test_gate_audit as tga   # the frozen record shapes live in ONE place

HERE = Path(__file__).resolve().parent                  # add-method/tooling
REPO = HERE.parent.parent                                # repo root
CI_YML = REPO / ".github" / "workflows" / "ci.yml"
GETTING_STARTED = HERE.parent / "GETTING-STARTED.md"
BUNDLED_ADD = HERE.parent / "src" / "add_method" / "_bundled" / "tooling" / "add.py"

# the one canonical invocation — identical in this repo and in consumer repos,
# because the installer places add.py at the same path (bin/cli.js: tooling -> .add/tooling)
CANONICAL = "python3 .add/tooling/add.py audit"


def _jobs_keys() -> list[str]:
    """Job names: 2-space-indented keys inside the jobs: section of ci.yml."""
    text = CI_YML.read_text(encoding="utf-8")
    parts = text.split("\njobs:\n", 1)
    if len(parts) < 2:
        return []
    return re.findall(r"^  ([A-Za-z][\w-]*):", parts[1], re.M)


def _seam_audit_run_line() -> str | None:
    """The literal run: command under the seam-audit job (None if absent)."""
    text = CI_YML.read_text(encoding="utf-8")
    block = re.search(r"(?ms)^  seam-audit:\n(.*?)(?=^  [A-Za-z]|\Z)", text)
    if not block:
        return None
    run = re.search(r"^\s*run:\s*(.+?)\s*$", block.group(1), re.M)
    return run.group(1) if run else None


class WiringShapeTest(unittest.TestCase):
    """The enforcement is a job distinct from the agent (exit criterion 2)."""

    def test_ci_defines_distinct_seam_audit_job(self):
        keys = _jobs_keys()
        self.assertIn("test", keys, "the existing test job must stay")
        self.assertIn("seam-audit", keys,
                      f"seam-audit must be its OWN job, not a buried step; jobs={keys}")
        self.assertIsNotNone(_seam_audit_run_line(),
                             "the seam-audit job must carry a run: command")

    def test_ci_audit_command_is_canonical(self):
        self.assertEqual(_seam_audit_run_line(), CANONICAL,
                         "one canonical invocation works in dogfood AND consumer repos")


class WiringBehaviorTest(unittest.TestCase):
    """The EXACT command string in ci.yml, executed against an installed layout."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-audit-ci-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(["init", "--name", "demo"])
            add.main(["new-milestone", "v1", "--title", "T", "--goal", "g"])
            add.main(["new-task", "alpha", "--title", "alpha"])
            add.main(["phase", "verify"])
            add.main(["gate", "PASS", "alpha"])
        # a well-formed record, byte-shaped by gate-audit's frozen constants
        self._task_md = self.tmp / ".add" / "tasks" / "alpha" / "TASK.md"
        self._task_md.write_text("\n".join([
            "# TASK: alpha", "",
            # a well-formed done task declares its risk + sensitivity level — keeps the board clean
            # of the presence-only `risk_unset`/`sensitivity_unset` notices (guarantee-audit-lints,
            # flow-honesty M3 + risk-sensitivity-taxonomy).
            "slug: alpha · risk: normal · sensitivity: mechanical", "",
            "## 1 · SPECIFY", "Feature: f", "",
            "## 2 · SCENARIOS", "(none)", "",
            "## 3 · CONTRACT", "```\nshape\n```", "", tga.GOOD3, "",
            "## 4 · TESTS", "plan", "",
            "## 5 · BUILD", "code", "",
            "## 6 · VERIFY", tga._sec6(), "",
            "## 7 · OBSERVE", "watch", "",
        ]), encoding="utf-8")
        # installed layout: the npm/PyPI installer puts add.py at .add/tooling/add.py
        tooling = self.tmp / ".add" / "tooling"
        tooling.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / "add.py", tooling / "add.py")
        # the engine is a package now: add.py imports add_engine.constants — copy it too
        shutil.copytree(HERE / "add_engine", tooling / "add_engine",
                        ignore=shutil.ignore_patterns("__pycache__"))

    def tearDown(self):
        os.chdir(self._cwd)

    def _run_ci_command(self):
        line = _seam_audit_run_line()
        self.assertIsNotNone(line, "ci.yml must define the seam-audit run line")
        # safety precondition: NEVER execute a drifted line — if ci.yml's command
        # changes, fail here without running it (the equality test reports the
        # drift; this guard ensures the suite never executes an unpinned string)
        self.assertEqual(line, CANONICAL,
                         "refusing to execute a non-canonical command from ci.yml")
        return subprocess.run(shlex.split(line), cwd=self.tmp,
                              capture_output=True, text=True, timeout=60)

    def _snapshot(self):
        # ignore Python bytecode: importing the add_engine package writes
        # __pycache__/*.pyc, which is not a meaningful "write" by the CI command
        return sorted(str(p) for p in self.tmp.rglob("*")
                      if p.is_file() and "__pycache__" not in p.parts)

    def test_ci_command_passes_clean_board(self):
        files = self._snapshot()
        proc = self._run_ci_command()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("audit: clean", proc.stdout)
        self.assertEqual(self._snapshot(), files, "the CI command must not write")

    def test_ci_command_fails_on_malformed_seam(self):
        # a commit strips the freeze stamp -> the machine the agent does not
        # control goes red and names the task
        body = self._task_md.read_text(encoding="utf-8")
        self._task_md.write_text(body.replace(tga.GOOD3, "Status: FROZEN"),
                                 encoding="utf-8")
        files = self._snapshot()
        proc = self._run_ci_command()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("unstamped_freeze", proc.stdout)
        self.assertIn("alpha", proc.stdout)
        self.assertEqual(self._snapshot(), files, "the CI command must not write")


class ConsumerShipTest(unittest.TestCase):
    """Consumers get the identical enforcement as a copy-paste workflow."""

    def test_getting_started_ships_consumer_workflow(self):
        text = GETTING_STARTED.read_text(encoding="utf-8")
        self.assertIn("## Enforce the decision points in CI", text)
        section = md_section.section(text, "## Enforce the decision points in CI")
        self.assertIn(CANONICAL, section,
                      "the snippet must use the same canonical command as this repo")
        self.assertIn("seam-audit", section)
        self.assertIn("actions/checkout", section)
        self.assertIn("actions/setup-python", section)

    def test_bundle_ships_audit_engine(self):
        # "shipped in the package" stays true by test, not by memory (×3 parity
        # elsewhere pins byte-equality; this pins the audit surface specifically)
        self.assertIn('add_parser("audit"',
                      BUNDLED_ADD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
