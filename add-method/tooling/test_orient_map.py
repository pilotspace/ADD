#!/usr/bin/env python3
"""Red/green for orient-map (orientation-honesty, frozen §3 v1).

Bare `add.py` and `add.py --help` LEAD with a concise flow-ordered command map
instead of the ~50-choice argparse dump — killing the stubborn 1/rep initial
`--help` orientation probe. A subcommand's own `--help` and the help-habit-kill
unknown-command interception stay unchanged.

Run: python3 -m unittest test_orient_map -v
"""
import contextlib
import io
import unittest

from add import build_parser

_MAP_HEAD = "ADD — spec-and-tests-first"


def _parse(argv):
    """Return (exit_code, stdout, stderr) for build_parser().parse_args(argv)."""
    out, err = io.StringIO(), io.StringIO()
    code = None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            build_parser().parse_args(argv)
    except SystemExit as e:
        code = e.code
    return code, out.getvalue(), err.getvalue()


class OrientMapTest(unittest.TestCase):
    def test_top_help_leads_with_map_then_compact_list(self):
        # help-diet (engine-minimalism) superseded the "FULL argparse list follows" behavior:
        # the map still LEADS, every command NAME stays discoverable, but the list is now COMPACT
        # (no per-command help paragraph, <=45 lines) to cut re-read cache-weight.
        fh = build_parser().format_help()
        self.assertTrue(fh.lstrip().startswith(_MAP_HEAD), "top --help must LEAD with the flow map")
        self.assertIn("add.py status", fh, "the map names status as the start")
        self.assertIn("freeze --by", fh, "the map hands freeze with its flag")
        self.assertIn("new-milestone", fh, "every command NAME still appears (discoverability held)")
        self.assertLessEqual(fh.count("\n") + 1, 45, "the command list is now compact (<=45 lines)")
        self.assertNotIn("scaffold a milestone (SDD", fh, "no per-command help paragraph (compact names)")

    def test_bare_addpy_prints_map_to_stderr(self):
        code, out, err = _parse([])
        self.assertEqual(code, 2, "bare add.py still exits 2")
        self.assertIn(_MAP_HEAD, err, "bare add.py prints the flow map to stderr")
        self.assertIn("add.py status", err, "and points at status")
        self.assertNotIn("{init,lock,freeze", out + err, "not the raw 50-choice usage dump")

    def test_subcommand_help_unchanged(self):
        code, out, err = _parse(["init", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("--stage", out, "a subcommand's own --help still shows its flags")
        self.assertNotIn(_MAP_HEAD, out, "the flow map must NOT hijack subcommand help")

    def test_unknown_command_interception_unchanged(self):
        code, out, err = _parse(["statuss"])
        self.assertEqual(code, 2)
        self.assertIn("unknown command 'statuss'", out + err, "help-habit-kill stays intact")
        self.assertNotIn(_MAP_HEAD, out + err, "an unknown command is not the orientation path")


if __name__ == "__main__":
    unittest.main()
