#!/usr/bin/env python3
"""Red/green for help-diet (engine-minimalism, frozen §3 v1).

`add.py --help` (the TOP parser) is trimmed from the ~121-line argparse dump to
the flow map + a COMPACT command-name list + the `add.py <command> -h` pointer —
cutting the re-read cache-weight (17% of an ADD run's engine_output, one early
call) WITHOUT losing discoverability. A subcommand's own `--help` is unchanged.

Run: python3 -m unittest test_help_diet -v
"""
import io
import unittest
from contextlib import redirect_stdout, redirect_stderr

from add import build_parser

_MAP_HEAD = "ADD — spec-and-tests-first"
# a spread of subcommands across the alphabet — all must stay discoverable
_SAMPLE = ["init", "new-task", "advance", "freeze", "gate", "status",
           "milestone-done", "new-milestone", "delta-append", "re-cross"]


class HelpDietTest(unittest.TestCase):
    def _top_help(self) -> str:
        return build_parser().format_help()

    def test_top_help_is_compact(self):
        fh = self._top_help()
        n = fh.count("\n") + 1
        self.assertLessEqual(n, 45, f"top --help must be <=45 lines, got {n}")
        self.assertTrue(fh.lstrip().startswith(_MAP_HEAD), "still leads with the flow map")

    def test_every_command_still_discoverable(self):
        fh = self._top_help()
        for cmd in _SAMPLE:
            self.assertIn(cmd, fh, f"'{cmd}' must stay listed in the compact command list")
        self.assertIn("-h", fh, "the per-command flags pointer (add.py <command> -h) is present")

    def test_no_per_command_help_paragraph(self):
        # the FULL dump carried each command's help sentence; the compact list drops them.
        fh = self._top_help()
        self.assertNotIn("scaffold a new task (PLAN.md", fh,
                         "the per-command help paragraph must be gone (compact names only)")
        self.assertNotIn("record a verify gate outcome", fh)

    def test_subcommand_help_unchanged(self):
        # M3/R1: a subcommand parser (prog != "add.py") is NOT trimmed.
        out, err = io.StringIO(), io.StringIO()
        code = None
        try:
            with redirect_stdout(out), redirect_stderr(err):
                build_parser().parse_args(["new-task", "--help"])
        except SystemExit as e:
            code = e.code
        blob = out.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("--title", blob, "subcommand --help still shows its own flags")
        self.assertIn("--fast", blob)
        self.assertNotIn(_MAP_HEAD, blob, "the flow map must not hijack subcommand help")


if __name__ == "__main__":
    unittest.main()
