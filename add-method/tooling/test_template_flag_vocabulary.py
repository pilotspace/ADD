#!/usr/bin/env python3
"""fold-residue-templates: the scaffold templates may not teach retired instructions.

The scenarios-into-tests fold retired §2 and the atomic-node work retired the lane
flags and the per-step phases. Each sweep fixed the instances it could see by hand,
with nothing left behind to object — so a dead `--fast` citation and a dead
"phase-0 ... before specify" definition kept shipping into every scaffolded project.

These checks close the CLASS: a template may not advertise a flag argparse rejects,
name a retired phase as a live step, or drift from the engine's own wording. They
read the SHIPPED template text and the REAL argparse, so a future retirement that
forgets a template fails here instead of reaching a user.
"""

import re
import sys
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent
REPO = TOOLING.parent.parent
ADD_PY = TOOLING / "add.py"

TEMPLATE_TREES = [
    REPO / "add-method" / "tooling" / "templates",
    REPO / ".add" / "tooling" / "templates",
    REPO / "add-method" / ".add" / "tooling" / "templates",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "templates",
]
SOURCE_TREE = TEMPLATE_TREES[0]

# Prose templates only. The UDD *.css/*.json/*.html samples are design artifacts whose
# `--foo` tokens are CSS custom properties, never CLI flags.
PROSE_SUFFIXES = {".tmpl", ".md"}
# Defense in depth: even inside prose, a design token may be quoted inline.
CSS_PROP = re.compile(r"^--(?:primitive|semantic)-")

LONG_FLAG = re.compile(r"(?<![\w-])(--[a-z][a-z-]*)")


def _prose_files(tree):
    return [p for p in sorted(tree.rglob("*")) if p.is_file() and p.suffix in PROSE_SUFFIXES]


def _parser():
    """add.py's real argparse parser.

    Scraping `--help` does NOT work: add.py prints a hand-written help with no verb
    list, and intercepts unknown verbs with its own message, so argparse's usage line
    surfaces only from a real-verb-plus-bad-flag error. Importing build_parser() reads
    the actual option objects — authoritative, and it can't drift from the CLI.
    """
    if str(TOOLING) not in sys.path:
        sys.path.insert(0, str(TOOLING))
    import add                                        # noqa: E402  (path set above)
    return add.build_parser()


def _accepted_flags():
    """Every long option add.py accepts — top level plus every subparser."""
    import argparse

    root = _parser()
    parsers = [root]
    for action in root._actions:
        if isinstance(action, argparse._SubParsersAction):
            parsers.extend(action.choices.values())

    flags = set()
    for p in parsers:
        for action in p._actions:
            flags.update(opt for opt in action.option_strings if opt.startswith("--"))
    return flags


class TemplateFlagVocabulary(unittest.TestCase):
    def test_no_dead_cli_flag(self):                                   # M1
        accepted = _accepted_flags()
        self.assertIn("--tiny", accepted, "sanity: the real flag must be discoverable")

        dead = []
        for f in _prose_files(SOURCE_TREE):
            for line_no, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                for flag in LONG_FLAG.findall(line):
                    if CSS_PROP.match(flag) or flag in accepted:
                        continue
                    dead.append(f"{f.relative_to(SOURCE_TREE)}:{line_no} cites {flag}")
        self.assertEqual(dead, [], "templates advertise flags the engine rejects: " + "; ".join(dead))


class TemplatePhaseVocabulary(unittest.TestCase):
    def test_no_retired_phase_vocabulary(self):                        # M2
        sys.path.insert(0, str(TOOLING))
        from add_engine.constants import PHASES

        # Phrases that assert a retired step is a LIVE part of the flow. Bare mentions of
        # a legacy name (a glossary "formerly ..." note) stay legal on purpose.
        retired = re.compile(r"phase-0|phase 0 |before specify|the specify phase|"
                             r"the scenarios phase|the contract phase|the tests phase",
                             re.IGNORECASE)
        self.assertNotIn("specify", PHASES, "sanity: specify really is retired")

        hits = []
        for f in _prose_files(SOURCE_TREE):
            for line_no, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if retired.search(line):
                    hits.append(f"{f.relative_to(SOURCE_TREE)}:{line_no}")
        self.assertEqual(hits, [], "templates describe a retired phase as live: " + "; ".join(hits))


class TemplateEngineParity(unittest.TestCase):
    def test_bundle_enumeration_matches_engine(self):                  # M3
        engine = ADD_PY.read_text(encoding="utf-8")
        self.assertIn("§1–§4 (rules · change plan · red suite)", engine,
                      "sanity: the engine's own bundle enumeration moved — re-aim this check")

        plan = (SOURCE_TREE / "PLAN.md.tmpl").read_text(encoding="utf-8")
        self.assertNotIn("rules · scenarios · change plan · red suite", plan,
                         "PLAN.md.tmpl still enumerates a separate `scenarios` bundle item; "
                         "the engine (add.py) lists three: rules · change plan · red suite")


class TemplateTreeParity(unittest.TestCase):
    def test_template_trees_identical(self):                           # M4
        base = {p.relative_to(SOURCE_TREE): p.read_bytes()
                for p in SOURCE_TREE.rglob("*") if p.is_file()}
        for tree in TEMPLATE_TREES[1:]:
            if not tree.is_dir():
                continue                    # a tree absent from this checkout is not drift
            other = {p.relative_to(tree): p.read_bytes()
                     for p in tree.rglob("*") if p.is_file()}
            self.assertEqual(sorted(base), sorted(other), f"file set differs: {tree}")
            for rel, blob in base.items():
                self.assertEqual(blob, other[rel], f"twin drift: {tree}/{rel}")


if __name__ == "__main__":
    unittest.main()
