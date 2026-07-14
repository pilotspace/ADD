#!/usr/bin/env python3
"""Red/green tests for derived stamps (task derived-stamps, frozen contract v1):
`freeze` fills a §3 `Ground SHA:` line still carrying its `<...>` placeholder with
the repo's real short HEAD — derived data the agent hand-types today (weight audit
2026-07-13). Grandfather + fail-open, mirroring _stamp_gate_record:

  M1 — placeholder + git repo -> the frozen §3 carries the real short HEAD,
       stamped in the SAME atomic write the Status flip rides (tamper-clean).
  R1 — a hand-filled Ground SHA line is byte-untouched (grandfather).
  R2 — no git repo -> freeze succeeds, the line stays untouched (fail-open).
  M2 — the stamp lives INSIDE the tamper fingerprint: freeze -> advance to
       verify -> gate PASS records clean (no contract_tampered return).

One test per §1 Must/Reject. Run: python3 -m unittest test_derived_stamps -v
"""
import io
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

_DRAFT = (
    "\n### Grounding\n"
    "Touches (files · symbols): src/x.py:handler\n"
    "Anchors the contract cites: handler\n"
    "Ground SHA: <`git rev-parse --short HEAD` at ground time — any line ref reads \"as of\" it>\n"
    "\n### Contract\n"
    "\n```\nGET /widget -> { ok: true }\n```\n\n"
    "`Least-sure flag surfaced at freeze:`\n"
    "  ⚠ [contract] the shape is the least-sure part — cost if wrong: a reparse.\n"
    "Status: DRAFT\n"
    "\n### Build-strategy\n"
    "Scope (may touch): `./src/`\n"
)


class _Harness(unittest.TestCase):
    """A live board arranged through the real CLI (mirrors test_kickoff_truth's
    harness — duplicated per this repo's one-harness-per-file norm)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-ds-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(out), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return out.getvalue() + err.getvalue(), code

    def _ok(self, *argv):
        text, code = self._run(*argv)
        self.assertEqual(code, 0, f"{argv} exited {code}: {text}")
        return text

    def _board(self, git: bool):
        """init + lock + a drafted oneshot task at plan; optionally a real git repo."""
        if git:
            subprocess.run(["git", "init", "-q"], check=True)
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                            "commit", "-q", "--allow-empty", "-m", "seed"], check=True)
        self._ok("init", "--name", "demo", "--stage", "mvp")
        self._ok("lock", "--force")
        self._ok("new-task", "t", "--title", "T", "--oneshot")
        self._ok("advance", "--to", "plan")
        p = self.tmp / ".add" / "tasks" / "t" / "TASK.md"
        text = p.read_text(encoding="utf-8")
        new = re.sub(r"(?ms)(^### Grounding.*?)(?=^---)", _DRAFT.lstrip("\n") + "\n",
                     text, count=1)
        self.assertNotEqual(new, text, "fixture §3 replacement failed")
        # quality-floors: an unfilled §1 Boundary: refuses the freeze — fill it
        new = re.sub(r"(?m)^Boundary:.*$", 'Boundary: none — no external input', new, count=1)
        p.write_text(new, encoding="utf-8")
        return p

    def _sec3(self, p: Path) -> str:
        return add._phase_spans(p.read_text(encoding="utf-8")).get(3, "")

    def _head(self) -> str:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True).stdout.strip()


class StampTest(_Harness):
    def test_freeze_stamps_placeholder_ground_sha(self):          # M1
        p = self._board(git=True)
        self._ok("freeze", "--by", "Tester")
        sec3 = self._sec3(p)
        head = self._head()
        self.assertTrue(head, "fixture git repo must resolve a HEAD")
        self.assertIn(f"Ground SHA: {head} — stamped by freeze", sec3)
        self.assertNotIn("Ground SHA: <", sec3, "the placeholder must be consumed")

    def test_hand_filled_line_untouched(self):                    # R1
        p = self._board(git=True)
        text = p.read_text(encoding="utf-8")
        p.write_text(text.replace(
            "Ground SHA: <`git rev-parse --short HEAD` at ground time — any line ref reads \"as of\" it>",
            "Ground SHA: abc1234 — hand-grounded"), encoding="utf-8")
        self._ok("freeze", "--by", "Tester")
        self.assertIn("Ground SHA: abc1234 — hand-grounded", self._sec3(p),
                      "a resolved line must stay byte-untouched (grandfather)")

    def test_no_git_freeze_succeeds_line_untouched(self):         # R2
        p = self._board(git=False)
        self._ok("freeze", "--by", "Tester")                      # must NOT die
        self.assertIn("Ground SHA: <", self._sec3(p),
                      "without git the placeholder stays — fail-open, never a fake SHA")

    def test_stamp_inside_tamper_fingerprint(self):               # M2
        self._board(git=True)
        self._ok("freeze", "--by", "Tester")
        self._ok("advance")                                       # plan -> tests
        self._ok("advance")                                       # tests -> build
        self._ok("advance")                                       # build -> verify
        out = self._ok("gate", "PASS")
        self.assertIn("gate -> PASS", out)
        self.assertNotIn("contract_tampered", out,
                         "the stamp must be part of the frozen fingerprint, not after it")


if __name__ == "__main__":
    unittest.main()
