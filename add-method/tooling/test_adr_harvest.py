#!/usr/bin/env python3
"""Red/green tests for the §7 Decisions (ADR) harvest (milestone adr-at-observe, task 2).

`add.py gate <outcome>` harvests a §7 "### Decisions (ADR)" block from the actor-stamps already
in the task — §1 framing (AI) · §3 freeze (human) · §5 strategy-actually-used (AI) · §6 gate
(human|AI). It mirrors gate-record-writeback: a write-back called AFTER _stamp_gate_record,
grandfathering a resolved or absent block (byte-identical no-op), never raising.

Run: python3 -m unittest test_adr_harvest -v
"""
import contextlib
import hashlib
import io
import json
import os
import re
import tempfile
import shutil
import unittest
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
CANON_TMPL = HERE / "templates" / "PLAN.md.tmpl"
DOG_TMPL = ADD_METHOD.parent / ".add" / "tooling" / "templates" / "PLAN.md.tmpl"
BUNDLE_TMPL = ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "PLAN.md.tmpl"

ADR_HEADER = "### Decisions (ADR)"


def _md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


class AdrHarvestTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-adr-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "demo"])
        self._quiet(["lock", "--force"])

    def tearDown(self):
        os.chdir(self._cwd)

    # ── helpers ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _quiet(argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            add.main(argv)

    def _state(self):
        return json.loads((Path(self.tmp) / ".add" / "state.json").read_text())

    def _task(self, slug="t"):
        return self._state()["tasks"][slug]

    def _path(self, slug="t"):
        return Path(self.tmp) / ".add" / "tasks" / slug / "PLAN.md"

    def _adr_block(self, slug="t"):
        t = self._path(slug).read_text()
        m = re.search(r"### Decisions \(ADR\).*?(?=\n##\s|\n---|\Z)", t, re.S)
        blk = m.group(0) if m else ""
        # strip-scaffold-at-done: a completing gate now removes the §7 `<!-- e.g. … -->` example
        # comment (orthogonal to the harvest) — normalize it out so this still tests the harvested
        # decision lines, not the template's instruction scaffolding.
        return re.sub(r"<!--.*?-->", "", blk, flags=re.S)

    def _task_at_verify(self, slug="t"):
        """Scaffold a task and give the harvest real §1 framing + §5 strategy stamps."""
        self._quiet(["new-task", slug])
        p = self._path(slug)
        txt = p.read_text()
        txt = txt.replace(
            "Framings weighed: <chosen> (chosen — why) · <alternative>",
            "Framings weighed: AlphaApproach (chosen) · BetaApproach · GammaApproach")
        txt = re.sub(r"(?m)^Strategy actually used:.*$",
                     "Strategy actually used: batched the edits then re-ran the suite", txt)
        p.write_text(txt, encoding="utf-8")
        self._quiet(["phase", "verify", slug])

    # ── gate PASS harvests an actor-tagged block ─────────────────────────────────────────
    def test_gate_harvests_actor_tagged_block(self):
        self._task_at_verify()
        self._quiet(["gate", "PASS"])
        block = self._adr_block()
        self.assertTrue(block, "§7 Decisions (ADR) block present after gate")
        self.assertNotIn("harvested at done", block, "the placeholder line was replaced")
        # the four sources, each on an actor-tagged line
        self.assertRegex(block, r"\[AI\][^\n]*specify[^\n]*AlphaApproach", "§1 framing chosen, [AI]")
        self.assertIn("BetaApproach", block, "§1 rejected alternatives carried")
        self.assertRegex(block, r"\[human\][^\n]*freeze", "§3 freeze, [human]")
        self.assertRegex(block, r"\[AI\][^\n]*strategy used: batched the edits", "§5 strategy, [AI]")
        self.assertRegex(block, r"\[(human|AI)\][^\n]*gate PASS", "§6 gate")
        # every list line is actor-tagged (untagged_decision guard)
        for ln in block.splitlines():
            if ln.strip().startswith("- "):
                self.assertRegex(ln, r"\[(human|AI)\]", f"untagged decision line: {ln}")
        self.assertEqual(self._task().get("gate"), "PASS")

    def test_harvest_not_authored(self):
        # every rendered decision line is backed by a stamp actually present in the task
        self._task_at_verify()
        self._quiet(["gate", "PASS"])
        block = self._adr_block()
        for token in ("AlphaApproach", "batched the edits", "freeze", "gate PASS"):
            self.assertIn(token, block, f"{token} must be harvested from a real stamp")

    # ── REGRESSION: the harvest targets ONLY the §7 OBSERVE placeholder ───────────────────
    def test_harvest_targets_only_section_7(self):
        # A "<harvested at done …>" line OUTSIDE §7 (e.g. a §3 contract that ILLUSTRATES this very
        # feature) must NOT be matched — only the §7 OBSERVE placeholder is filled. Dogfooding
        # adr-harvest corrupted its OWN frozen §3 illustration because the engine matched the first
        # file-wide line; this pins the §7-OBSERVE scope.
        self._task_at_verify()
        p = self._path()
        decoy = "<harvested at done — DECOY inside §3, must stay byte-untouched>"
        txt = p.read_text()
        i = txt.index("## 3 · PLAN")        # insert the decoy as its OWN line (ends in '>') after the §3 header
        j = txt.index("\n", i)
        txt = txt[:j + 1] + "\n" + decoy + "\n" + txt[j + 1:]
        self.assertLess(txt.index(decoy), txt.index("## 7 · OBSERVE"), "decoy precedes §7")
        p.write_text(txt, encoding="utf-8")
        self._quiet(["gate", "PASS"])
        after = p.read_text()
        self.assertIn(decoy, after, "a <harvested at done> line outside §7 must be untouched")
        self.assertRegex(self._adr_block(), r"\[AI\][^\n]*specify[^\n]*AlphaApproach",
                         "the §7 OBSERVE block is the harvest target, not the first file-wide match")

    # ── faithful capture: §1 "(chosen — rationale)" parses the chosen framing ─────────────
    def test_framing_parses_chosen_with_rationale(self):
        self._quiet(["new-task", "f"])
        p = self._path("f")
        txt = p.read_text().replace(
            "Framings weighed: <chosen> (chosen — why) · <alternative>",
            "Framings weighed: WriteBack (chosen — reuses the proven mechanics) · CommandX · StateOnly")
        p.write_text(txt, encoding="utf-8")
        self._quiet(["phase", "verify", "f"])
        self._quiet(["gate", "PASS", "f"])
        block = self._adr_block("f")
        self.assertRegex(block, r"\[AI\][^\n]*chose WriteBack",
                         "chosen framing parsed from '(chosen — rationale)', not lost to <unrecorded>")
        self.assertNotIn("chose <unrecorded>", block, "the chosen must not degrade when a rationale is present")

    # ── faithful capture: a filled §5 containing '<' is not mistaken for unfilled ─────────
    def test_strategy_value_with_angle_bracket_kept(self):
        self._quiet(["new-task", "g"])
        p = self._path("g")
        txt = re.sub(r"(?m)^Strategy actually used:.*$",
                     "Strategy actually used: rewrote the `<harvested>` parser and fixed x < y", p.read_text())
        p.write_text(txt, encoding="utf-8")
        self._quiet(["phase", "verify", "g"])
        self._quiet(["gate", "PASS", "g"])
        block = self._adr_block("g")
        self.assertIn("rewrote the `<harvested>` parser", block, "a filled §5 with '<' is not 'unfilled'")
        self.assertNotIn("strategy used: as planned", block, "the real strategy must not degrade to the default")

    # ── wrapped fields: a multi-line "Framings weighed:" is captured in full ─────────────
    def test_framing_captures_wrapped_field(self):
        self._quiet(["new-task", "h"])
        p = self._path("h")
        txt = p.read_text().replace(
            "Framings weighed: <chosen> (chosen — why) · <alternative>",
            "Framings weighed: WriteBack (chosen — reuses the proven\n"
            "  mechanics) · CommandX · StateOnly")
        p.write_text(txt, encoding="utf-8")
        self._quiet(["phase", "verify", "h"])
        self._quiet(["gate", "PASS", "h"])
        block = self._adr_block("h")
        self.assertRegex(block, r"\[AI\][^\n]*chose WriteBack",
                          "a wrapped Framings weighed value must still harvest the chosen framing")
        self.assertNotIn("chose <unrecorded>", block, "a wrapped field must not degrade to <unrecorded>")

    def test_strategy_captures_wrapped_field(self):
        self._quiet(["new-task", "i"])
        p = self._path("i")
        txt = re.sub(r"(?m)^Strategy actually used:.*$",
                      "Strategy actually used: rewrote the parser across\n"
                      "  two batches and re-ran the suite", p.read_text())
        p.write_text(txt, encoding="utf-8")
        self._quiet(["phase", "verify", "i"])
        self._quiet(["gate", "PASS", "i"])
        block = self._adr_block("i")
        self.assertIn("rewrote the parser across two batches and re-ran the suite", block,
                      "a wrapped Strategy actually used value must be captured in full")

    def test_wrapped_field_stops_at_next_label(self):
        self._quiet(["new-task", "j"])
        p = self._path("j")
        txt = p.read_text().replace(
            "Framings weighed: <chosen> (chosen — why) · <alternative>\nMust:",
            "Framings weighed: WriteBack (chosen — a two-line\n  value)\nMust:")
        p.write_text(txt, encoding="utf-8")
        self._quiet(["phase", "verify", "j"])
        self._quiet(["gate", "PASS", "j"])
        block = self._adr_block("j")
        self.assertRegex(block, r"\[AI\][^\n]*chose WriteBack")
        self.assertNotIn("Must", block, "the capture must stop before the next label, never absorb it")

    def test_wrapped_field_stops_at_blank_line(self):
        self._quiet(["new-task", "k"])
        p = self._path("k")
        txt = p.read_text().replace(
            "Framings weighed: <chosen> (chosen — why) · <alternative>\nMust:",
            "Framings weighed: WriteBack (chosen — a two-line\n  value)\n\nMust:")
        p.write_text(txt, encoding="utf-8")
        self._quiet(["phase", "verify", "k"])
        self._quiet(["gate", "PASS", "k"])
        block = self._adr_block("k")
        self.assertRegex(block, r"\[AI\][^\n]*chose WriteBack")
        self.assertNotIn("Must", block, "the capture must stop at the blank line, never absorb past it")

    def test_single_line_fields_unchanged(self):
        self._quiet(["new-task", "l"])
        p = self._path("l")
        txt = p.read_text().replace(
            "Framings weighed: <chosen> (chosen — why) · <alternative>",
            "Framings weighed: WriteBack (chosen) · CommandX · StateOnly")
        txt = re.sub(r"(?m)^Strategy actually used:.*$",
                      "Strategy actually used: rewrote the parser in one pass", txt)
        p.write_text(txt, encoding="utf-8")
        self._quiet(["phase", "verify", "l"])
        self._quiet(["gate", "PASS", "l"])
        block = self._adr_block("l")
        self.assertRegex(block, r"\[AI\][^\n]*chose WriteBack",
                          "a single-line Framings weighed value must harvest exactly as before")
        self.assertIn("rewrote the parser in one pass", block,
                      "a single-line Strategy actually used value must harvest exactly as before")

    def test_wrapped_field_stops_at_parenthetical_label(self):
        # the REAL template places "Safety rule (feature-specific):" immediately after
        # "Strategy actually used:" with no blank line — a boundary blind to "(...)" labels
        # would silently swallow it into the harvested strategy text.
        self._quiet(["new-task", "m"])
        p = self._path("m")
        txt = re.sub(r"(?m)^Strategy actually used:.*$",
                      "Strategy actually used: rewrote the parser across\n"
                      "  two batches and re-ran the suite", p.read_text())
        p.write_text(txt, encoding="utf-8")
        self._quiet(["phase", "verify", "m"])
        self._quiet(["gate", "PASS", "m"])
        block = self._adr_block("m")
        self.assertIn("rewrote the parser across two batches and re-ran the suite", block)
        self.assertNotIn("Safety rule", block,
                         "a parenthetical-suffixed label must still stop the capture")

    # ── grandfather: a resolved (hand-edited) block is byte-untouched ─────────────────────
    def test_grandfather_resolved_block_untouched(self):
        self._task_at_verify()
        p = self._path()
        txt = re.sub(r"(?m)^<harvested at done[^\n]*>$",
                     "- [human] freeze — hand-written, keep me", p.read_text())
        p.write_text(txt, encoding="utf-8")
        block_before = self._adr_block()
        self._quiet(["gate", "PASS"])
        self.assertEqual(self._adr_block(), block_before, "a resolved ADR block is byte-untouched")
        self.assertNotIn("AlphaApproach", self._adr_block(), "no harvest over a resolved block")
        self.assertEqual(self._task().get("gate"), "PASS")

    # ── absent block -> no ADR fabricated (legacy / fast tasks) ──────────────────────────
    def test_absent_block_is_noop(self):
        # NOTE: gate-record-writeback legitimately stamps §6, so the file is NOT byte-identical;
        # the ADR invariant is that NO Decisions (ADR) block is fabricated where none existed.
        self._task_at_verify()
        p = self._path()
        stripped = re.sub(r"### Decisions \(ADR\).*?(?=\n##\s|\n---|\Z)", "", p.read_text(), flags=re.S)
        p.write_text(stripped, encoding="utf-8")
        self.assertNotIn(ADR_HEADER, p.read_text())
        self._quiet(["gate", "PASS"])  # must not raise
        self.assertNotIn(ADR_HEADER, p.read_text(), "no ADR block was fabricated where none existed")
        self.assertEqual(self._task().get("gate"), "PASS")

    # ── never blocks the gate even with malformed sources ────────────────────────────────
    def test_never_blocks_on_malformed_sources(self):
        self._quiet(["new-task", "u"])
        p = self._path("u")
        # wipe §1 framing + §5 to placeholders / empties, then jump to verify
        txt = re.sub(r"(?m)^Framings weighed:.*$", "Framings weighed:", p.read_text())
        txt = re.sub(r"(?m)^Strategy actually used:.*$", "Strategy actually used:", txt)
        p.write_text(txt, encoding="utf-8")
        self._quiet(["phase", "verify", "u"])
        self._quiet(["gate", "PASS", "u"])  # must not raise
        self.assertEqual(self._task("u").get("gate"), "PASS", "gate records despite malformed sources")

    # ── the full template carries the §7 block + placeholder, 3-tree parity ──────────────
    def test_template_carries_adr_block(self):
        text = CANON_TMPL.read_text(encoding="utf-8")
        self.assertIn(ADR_HEADER, text, "PLAN.md.tmpl §7 missing the Decisions (ADR) block")
        # placed after "Watch", before "### Spec delta"
        self.assertLess(text.index(ADR_HEADER), text.index("### Spec delta"))

    def test_template_mirrors(self):
        self.assertEqual(_md5(CANON_TMPL), _md5(DOG_TMPL), "full template: dogfood diverged")
        self.assertEqual(_md5(CANON_TMPL), _md5(BUNDLE_TMPL), "full template: bundle diverged")

    # ── only add.py + templates change: the package pin holds ────────────────────────────


if __name__ == "__main__":
    unittest.main(verbosity=2)
