#!/usr/bin/env python3
"""Tests for the GETTING-STARTED conversational spine (v15 getting-started-rewrite).

The doc is the artifact under test: the spine (everything before the
escape-hatch heading) asks the reader to type ONLY the install command; the
by-hand seven-phase walk lives in a self-contained escape-hatch appendix.
These tests pin the v15 restructure; the shipped guards (test_quickstart,
test_v8_docs, test_onboarding_align, test_release_1_4_0) pin what must
survive it — together they are the union the rewrite designs to.
Run: python3 -m unittest test_getting_started_spine -v
"""
import hashlib
import re
import unittest
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent          # add-method/
REPO_ROOT = PKG_ROOT.parent
GUIDE = PKG_ROOT / "GETTING-STARTED.md"

ENGINE_PATHS = (
    PKG_ROOT / "tooling" / "add.py",
    REPO_ROOT / ".add" / "tooling" / "add.py",
    PKG_ROOT / "src" / "add_method" / "_bundled" / "tooling" / "add.py",
)

# The four phase-walk commands the spine must never ask the reader to type.
# (status · guide · check · audit remain spine-legal: override/CI surfaces.)
PHASE_WALK = ("add.py new-task", "add.py advance", "add.py gate", "add.py stage")

# A markdown HEADING (not an incidental phrase) opens the escape hatch — same
# rule the shipped onboarding-align guard uses.
ESCAPE_HEADING = re.compile(r"^#{2,3} .*(under the hood|escape hatch)", re.I | re.M)


def _text() -> str:
    return GUIDE.read_text(encoding="utf-8")


def _split_at_escape(text: str):
    """(spine, appendix) — split at the escape-hatch heading line."""
    m = ESCAPE_HEADING.search(text)
    if m is None:
        raise AssertionError(
            "no escape-hatch heading found — a shipped guard requires one")
    return text[: m.start()], text[m.start():]


def _section(text: str, heading_substr: str):
    """Body of the first ## section whose heading contains the substring
    (case-insensitive), up to the next ## heading. None if absent."""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("## ") and heading_substr in ln.lower():
            start = i
            break
    if start is None:
        return None
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            return "\n".join(lines[start:j])
    return "\n".join(lines[start:])


class SpineTest(unittest.TestCase):
    def test_spine_free_of_phase_walk_commands(self):
        spine, _ = _split_at_escape(_text())
        for cmd in PHASE_WALK:
            self.assertNotIn(
                cmd, spine,
                f"the spine asks the reader to type `{cmd}` — phase-walk "
                f"commands belong in the escape-hatch appendix only")

    def test_install_section_flagless_first_with_handoff(self):
        sec = _section(_text(), "install")
        self.assertIsNotNone(sec, "no Install section heading found")
        self.assertRegex(
            sec, re.compile(r"^npx @pilotspace/add init\s*$", re.M),
            "the npx install example must lead with the FLAGLESS form "
            "(its own line, no --name/--stage)")
        self.assertRegex(
            sec, re.compile(r"^pilotspace-add init\s*$", re.M),
            "the pip install example must lead with the FLAGLESS form")
        low = sec.lower()
        self.assertIn("open claude code", low,
                      "install must hand off to the conversation")
        self.assertIn("/add", sec,
                      "the handoff names the /add entry point")

    def test_first_feature_section_merged(self):
        sec = _section(_text(), "your first feature")
        self.assertIsNotNone(
            sec, "no 'Your first feature' section — the fast path and the "
                 "old spine §3 merge into one conversational section")
        low = sec.lower()
        self.assertIn("/add", sec, "the /add prompt fence must lead the section")
        self.assertIn("transfer money", low, "the worked example survives")
        for term in ("intake", "milestone", "specification bundle"):
            self.assertIn(term, low,
                          f"the on-ramp steps must name {term!r} in this section")
        self.assertIn("onboarding", low, "the On-ramp callout survives")

    def test_what_just_happened_overrides(self):
        sec = _section(_text(), "what just happened")
        self.assertIsNotNone(
            sec, "no 'What just happened' section — status/guide need a home "
                 "framed as the reader's override, not a step")
        self.assertIn("add.py status", sec,
                      "the override section names the resume command")
        low = sec.lower()
        self.assertTrue(
            any(w in low for w in ("override", "yourself", "resume", "if you ever")),
            "status/guide must be framed as the reader's OWN surface "
            "(override/resume), not an instructed step")
        for cmd in PHASE_WALK:
            self.assertNotIn(cmd, sec, f"phase-walk command `{cmd}` in the override section")

    def test_escape_hatch_self_contained(self):
        _, appendix = _split_at_escape(_text())
        for cmd in ("add.py new-task", "add.py advance", "add.py gate PASS",
                    "add.py stage"):
            self.assertIn(
                cmd, appendix,
                f"the escape hatch must be self-contained — `{cmd}` belongs "
                f"in the appendix so the by-hand walk works without the spine")


if __name__ == "__main__":
    unittest.main(verbosity=2)
