#!/usr/bin/env python3
"""Red/green tests for the per-facet ADR harvest (task facet-adr-harvest,
milestone build-strategy-facets, contract FROZEN @ v1).

`add.py gate <outcome>` already harvests §7 Decisions (ADR) from the task's actor-stamps.
This task extends the §5 source: each FILLED strategy facet (Approach (domain strategy) ·
Data strategy · Pattern · Optimization stance) emits its own "- [AI] build — <key>: <value>"
line, ordered, directly BEFORE the existing strategy-used line. An unfilled facet (absent,
or value with a LEADING "<") is silent; zero filled facets collapse to today's exact block
(legacy done tasks re-stamp byte-identical). §7's Watch hint now cites the §5 Optimization
stance as a monitor. Harvest stays try/except-shielded — it can never block a gate.

Run: python3 -m unittest test_facet_adr_harvest -v
"""
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import add
import engine_pin

HERE = Path(__file__).resolve().parent
ADD_METHOD = HERE.parent
REPO = ADD_METHOD.parent
BUNDLE = ADD_METHOD / "src" / "add_method" / "_bundled"

CANON_TMPL = HERE / "templates" / "TASK.md.tmpl"
# fresh-checkout skip-tolerance (ba09498 precedent): gitignored dogfood twins may be absent
# on a clean clone — assert lockstep over the twins that exist (canon + bundle always do)
TMPL_TWINS = tuple(p for p in (CANON_TMPL,
                               REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
                               ADD_METHOD / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
                               BUNDLE / "tooling" / "templates" / "TASK.md.tmpl") if p.exists())
assert len(TMPL_TWINS) >= 2, "twin set collapsed below canon+bundle"
ADDPY_TRIO = (HERE / "add.py", REPO / ".add" / "tooling" / "add.py",
              BUNDLE / "tooling" / "add.py")

# the contract-frozen Watch line (§3 v1) — byte-exact. plan-phase-core relocated
# Optimization stance from §5 BUILD into §3 PLAN's ### Build-strategy, so the cross-cite
# tracks that move (still names the SAME field, just its new section).
WATCH_LINE = ("Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency "
              "— the §3 Build-strategy Optimization stance budget is a monitor here, not just "
              "an intention>")

FACET_FILLS = {  # label -> (real value, expected ADR key)
    "Approach (domain strategy)": ("event-sourced ledger append", "approach"),
    "Data strategy": ("append-only rows keyed by transfer id", "data strategy"),
    "Pattern": ("repository pattern per CONVENTIONS", "pattern"),
    "Optimization stance": ("latency p99 under 50ms", "optimization stance"),
}


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


class FacetAdrHarvestTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-facet-adr-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        self._quiet(["init", "--name", "demo"])
        self._quiet(["lock", "--force"])

    def tearDown(self):
        os.chdir(self._cwd)

    @staticmethod
    def _quiet(argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            add.main(argv)

    def _path(self, slug="t"):
        return Path(self.tmp) / ".add" / "tasks" / slug / "TASK.md"

    def _adr_block(self, slug="t"):
        t = self._path(slug).read_text()
        m = re.search(r"### Decisions \(ADR\).*?(?=\n##\s|\n---|\Z)", t, re.S)
        blk = m.group(0) if m else ""
        return re.sub(r"<!--.*?-->", "", blk, flags=re.S)

    def _task_at_verify(self, slug="t", fill=(), strategy=None, mutate=None):
        """Scaffold a task; fill the named §5 facets with real values; drive to verify."""
        self._quiet(["new-task", slug])
        p = self._path(slug)
        txt = p.read_text()
        for label in fill:
            value, _ = FACET_FILLS[label]
            txt = re.sub(rf"(?m)^{re.escape(label)}:.*$", f"{label}: {value}", txt)
        if strategy is not None:
            txt = re.sub(r"(?m)^Strategy actually used:.*$",
                         f"Strategy actually used: {strategy}", txt)
        if mutate:
            txt = mutate(txt)
        p.write_text(txt, encoding="utf-8")
        self._quiet(["phase", "verify", slug])

    def _build_lines(self, slug="t"):
        return [ln for ln in self._adr_block(slug).splitlines()
                if ln.strip().startswith("- [AI] build —")]

    # ── M1: filled facets each earn an ADR line, ordered, before strategy-used ────────
    def test_filled_facets_each_earn_a_line(self):
        self._task_at_verify(fill=tuple(FACET_FILLS), strategy="as planned")
        self._quiet(["gate", "PASS"])
        lines = self._build_lines()
        self.assertEqual(len(lines), 5, f"4 facet lines + strategy-used expected, got: {lines}")
        for i, (label, (value, key)) in enumerate(FACET_FILLS.items()):
            self.assertIn(f"— {key}: {value}", lines[i], f"facet {key} missing/misordered")
        self.assertIn("strategy used: as planned", lines[4], "strategy-used stays LAST")

    # ── M2: an unfilled facet stays silent ─────────────────────────────────────────────
    def test_unfilled_facet_stays_silent(self):
        self._task_at_verify(fill=("Approach (domain strategy)",))
        self._quiet(["gate", "PASS"])
        lines = self._build_lines()
        self.assertEqual(len(lines), 2, f"approach + strategy-used only, got: {lines}")
        self.assertIn("— approach: event-sourced ledger append", lines[0])
        for key in ("data strategy:", "pattern:", "optimization stance:"):
            self.assertNotIn(key, self._adr_block(), f"placeholder facet leaked: {key}")

    # ── M3: legacy collapse — facet-less §5 renders exactly today's block ─────────────
    def test_legacy_collapse_byte_identical(self):
        def strip_facets(txt):
            for label in FACET_FILLS:
                txt = re.sub(rf"(?m)^{re.escape(label)}:.*\n", "", txt)
            return txt
        self._task_at_verify(slug="legacy", mutate=strip_facets)
        self._quiet(["gate", "PASS"])
        lines = [ln for ln in self._adr_block("legacy").splitlines() if ln.strip().startswith("- ")]
        self.assertEqual(len(lines), 4, f"legacy block must be today's 4 lines, got: {lines}")
        self.assertIn("strategy used: as planned", lines[2], "as-planned default intact")

    def test_placeholders_also_collapse(self):
        self._task_at_verify(slug="ph")            # facets left as template placeholders
        self._quiet(["gate", "PASS"])
        lines = [ln for ln in self._adr_block("ph").splitlines() if ln.strip().startswith("- ")]
        self.assertEqual(len(lines), 4, f"placeholder facets must collapse, got: {lines}")

    # ── M4: the Watch line cites the stance; twins + ceiling hold ──────────────────────
    # byte-ledger migrates forward (method-ergonomics precedent): plan-phase-core folded
    # the old standalone §0 GROUND section into §3 PLAN's ### Grounding sub-block and added
    # ### Build-strategy — a real, already-frozen structural growth, not a drive-by bloat —
    # so this LOCAL fence re-baselines to the new actual size. The canonical ledger lives in
    # test_taskmd_lean.py (a sibling batch's fence, out of this file's scope).
    def test_watch_line_cites_stance(self):
        text = CANON_TMPL.read_text(encoding="utf-8")
        self.assertIn(WATCH_LINE, text, "§7 Watch must carry the contract-exact stance cross-cite")
        self.assertEqual(len({_md5(p) for p in TMPL_TWINS}), 1, "TASK.md.tmpl twins diverged")
        self.assertLessEqual(len(text.encode("utf-8")), 12400, "template size ceiling busted")

    # ── M5: honest re-pin ───────────────────────────────────────────────────────────────
    def test_engine_repin_honest(self):
        digests = {_md5(p) for p in ADDPY_TRIO}
        self.assertEqual(len(digests), 1, "add.py trio diverged")
        self.assertEqual(digests.pop(), engine_pin.ENGINE_MD5,
                         "ENGINE_MD5 must equal the BUILT add.py (re-pin honestly)")

    # ── R:false_placeholder_drop — mid-text "<" is faithful-captured ───────────────────
    def test_faithful_capture_mid_text_bracket(self):
        def fill_with_tag(txt):
            return re.sub(r"(?m)^Pattern:.*$",
                          "Pattern: wrap each field in a <strategy> tag per streams.md", txt)
        self._task_at_verify(slug="tagd", mutate=fill_with_tag)
        self._quiet(["gate", "PASS"])
        self.assertIn("— pattern: wrap each field in a <strategy> tag per streams.md",
                      self._adr_block("tagd"),
                      "a value CONTAINING '<' mid-text must not degrade to unfilled")

    # ── R:gate_blocked — harvest failure never blocks the gate ────────────────────────
    def test_harvest_never_blocks_gate(self):
        self._task_at_verify(slug="boom", fill=tuple(FACET_FILLS))
        with mock.patch.object(add, "_capture_wrapped", side_effect=RuntimeError("boom")):
            self._quiet(["gate", "PASS"])
        state = json.loads((Path(self.tmp) / ".add" / "state.json").read_text())
        self.assertEqual(state["tasks"]["boom"].get("gate"), "PASS",
                         "a harvest exception must never block the gate")

    # ── R:cross_section_bleed — facets harvest from §5 ONLY ───────────────────────────
    def test_no_cross_section_bleed(self):
        def plant_decoys(txt):
            txt = txt.replace("## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md",
                              "## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md\n"
                              "Pattern: DECOY-ZERO must never be harvested")
            return txt.replace("## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md",
                               "## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md\n"
                               "Optimization stance: DECOY-SIX must never be harvested")
        self._task_at_verify(slug="bleed", mutate=plant_decoys)
        self._quiet(["gate", "PASS"])
        block = self._adr_block("bleed")
        self.assertNotIn("DECOY-ZERO", block, "§0 prose bled into the facet harvest")
        self.assertNotIn("DECOY-SIX", block, "§6 prose bled into the facet harvest")


if __name__ == "__main__":
    unittest.main()
