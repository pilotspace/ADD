#!/usr/bin/env python3
"""template-unify red suite (task template-unify, thin-engine-loop W3).

ONE PLAN.md.tmpl serves every lane: PLAN.fast.md.tmpl is deleted from all
template trees; `--fast` renders the full template minus exactly the
`_FAST_SECTIONS` heading blocks (subset by construction) plus a spliced
`fast: true` header; `--oneshot` adds its two headers + the spliced §3
"### AI-verify record" block. The whole template family gets a lean-pass —
measurably smaller, machine-read lines intact (byte ledger pinned here).

Red-for-the-right-reason today (pre-build):
  - fast renders from a DIFFERENT template file -> subset/drop-set red
  - PLAN.fast.md.tmpl + _FALLBACK_TASK_FAST still exist -> file-gone red
  - the full template's marker is `phase: specify` -> native-marker red
  - the full template has no §1 Boundary: line -> boundary-both-lanes red
  - family templates are exactly the pre-task sizes -> byte-ledger red
Floor pins (green today, must STAY green through the rebuild):
  - oneshot headers + AI-verify checklist refusal (ai_freeze_checklist_incomplete)
  - boundary_unfilled refusal is lane-agnostic at cmd_freeze
  - the default full scaffold keeps every §1–§7 heading

Run: python3 -m unittest test_template_unify -v
"""
import io
import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import add

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
TEMPLATES = HERE / "templates"

# the 4 template trees (canonical · bundle · both dogfood twins); a tree absent
# in a fresh checkout is skipped, never failed (fresh-checkout skip-tolerance)
TEMPLATE_TREES = (
    REPO / "add-method" / "tooling" / "templates",
    REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "templates",
    REPO / ".add" / "tooling" / "templates",
    REPO / "add-method" / ".add" / "tooling" / "templates",
)

PLACEHOLDER_BOUNDARY = ("Boundary: <one format-variant per external input shape "
                        "the tests must speak — e.g. aware vs naive timestamp "
                        '· or "none — no external input">')
REAL_BOUNDARY = "Boundary: aware (Z-suffixed) vs naive timestamp on request.created_at"


def _headings(text: str) -> list[str]:
    return re.findall(r"(?m)^#{2,3} .*$", text)


class _Board(unittest.TestCase):
    """A live board through the real CLI — the test_fast_boundary_line idiom,
    duplicated per this repo's one-harness-per-file norm."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="add-template-unify-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self.tmp)
        self._silent("init", "--name", "demo")
        self._silent("new-milestone", "v1", "--title", "T", "--goal", "g")

    def _silent(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            add.main(list(argv))
        return buf.getvalue(), err.getvalue()

    def _run(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        code = 0
        try:
            with redirect_stdout(buf), redirect_stderr(err):
                add.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
        return buf.getvalue(), err.getvalue(), code

    def _task_md(self, slug: str) -> Path:
        return self.tmp / ".add" / "tasks" / slug / "PLAN.md"

    def _scaffold(self, slug: str, *flags) -> str:
        self._silent("new-task", slug, "--title", "probe", *flags)
        return self._task_md(slug).read_text(encoding="utf-8")

    def _write_task(self, slug: str, boundary_line: str, *, fast=False,
                    oneshot=False, ai_boxes_ticked=True):
        """A minimal freeze-ready board fixture; boxes toggle the AI-verify floor."""
        spec1 = ["Feature: f", "Must:", "  - m",
                 "Accept: Given g, When w, Then t", boundary_line]
        header = [f"# PLAN: {slug}",
                  f"slug: {slug} · created: 2026-07-16 · stage: mvp"]
        if fast or oneshot:
            header.append("fast: true")
        if oneshot:
            header += ["oneshot: true", "gate_mode: ai-plan-verify"]
        sec3 = ["### Grounding",
                "Anchors the contract cites: cmd_advance",
                "### Contract",
                "```", "shape: f(x) -> ok · bad -> err", "```",
                "Least-sure flag surfaced at freeze: [contract] narrow "
                "shape — cost: one re-freeze.",
                "Status: DRAFT",
                "### Build-strategy",
                "Scope (may touch): `src/`"]
        if oneshot:
            box = "x" if ai_boxes_ticked else " "
            sec3 += ["", "### AI-verify record (required when gate_mode: ai-plan-verify)",
                     f"- [{box}] §3 PLAN grounding anchors resolve in the current tree",
                     f"- [{box}] §1 every Must + every Reject present, each Reject paired with an error code",
                     f"- [{box}] §3 Contract shape is concrete (no template placeholder text remains)",
                     f"- [{box}] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)",
                     "Verified by: test-agent · at: 2026-07-16T00:00:00Z"]
        sec = lambda n, name, *body: [f"## {n} · {name}", *body, ""]
        lines = [*header, "phase: direction", "",
                 *sec(1, "SPECIFY", *spec1),
                 *sec(2, "SCENARIOS", "(none)"),
                 *sec(3, "PLAN", *sec3),
                 *sec(4, "TESTS", "Tests live in: `./tests/`"),
                 *sec(5, "BUILD", "Code lives in: `./src/`"),
                 *sec(6, "VERIFY", "checks"),
                 *sec(7, "OBSERVE", "watch")]
        self._silent("new-task", slug, "--title", slug)
        self._task_md(slug).write_text("\n".join(lines), encoding="utf-8")


# ── M1: the fast template file (and its fallback) cease to exist ─────────────
class FastTemplateGoneTest(unittest.TestCase):
    def test_fast_template_file_gone_from_every_tree(self):
        for tree in TEMPLATE_TREES:
            if not tree.is_dir():
                continue  # fresh-checkout tolerance — a missing twin is not a failure
            self.assertFalse((tree / "PLAN.fast.md.tmpl").exists(),
                             f"PLAN.fast.md.tmpl must be deleted from {tree}")

    def test_fast_fallback_literal_gone_from_engine(self):
        src = (HERE / "add.py").read_text(encoding="utf-8")
        self.assertNotIn("_FALLBACK_TASK_FAST", src,
                         "the fast fallback template must be deleted with its file")


# ── M5 + M6: the one template is natively 3-phase and carries the Boundary ──
class TemplateShapeTest(unittest.TestCase):
    def setUp(self):
        self.tmpl = (TEMPLATES / "PLAN.md.tmpl").read_text(encoding="utf-8")

    def test_native_direction_marker(self):
        self.assertRegex(self.tmpl, r"(?m)^phase: direction\b",
                         "the template must natively carry the 3-phase marker")
        self.assertNotRegex(self.tmpl, r"(?m)^phase: specify\b",
                            "no legacy phase name on the marker line")

    def test_full_template_carries_boundary_line(self):
        self.assertIn("\nBoundary: <", self.tmpl,
                      "§1 must scaffold a Boundary: line on the full lane too (M6)")
        acc = self.tmpl.find("\nBoundary: ")
        must = self.tmpl.find("<must>")
        self.assertGreater(acc, -1)
        self.assertLess(acc, self.tmpl.find("## 2 ·"),
                        "the Boundary: line lives in §1")
        self.assertGreater(acc, must, "Boundary rides inside §1 after the rules")


# ── M2: fast render = full render minus exactly _FAST_SECTIONS ───────────────
class RenderSubsetTest(_Board):
    def _pair(self):
        full = self._scaffold("full-t").replace("full-t", "SLUG")
        fast = self._scaffold("fast-t", "--fast").replace("fast-t", "SLUG")
        return full, fast

    def test_fast_is_strict_subset(self):
        full, fast = self._pair()
        extras = set(fast.splitlines()) - set(full.splitlines())
        self.assertLessEqual(
            extras, {"fast: true"},
            f"every fast line must exist in the full render (splice-only extras); "
            f"foreign lines: {sorted(extras)[:8]}")

    def test_fast_drops_exactly_fast_sections(self):
        from add_engine.constants import _FAST_SECTIONS  # red until the build lands it
        full, fast = self._pair()
        for key in _FAST_SECTIONS:
            self.assertFalse(any(l.startswith(key) for l in fast.splitlines()),
                             f"fast must drop the {key!r} block")
        # the frozen §3 strip rule: a key's block runs to the next heading of the
        # SAME-OR-HIGHER level — a dropped ## block absorbs its nested ### headings
        # (§7's sub-blocks go with "## 7 · OBSERVE"); those count as dropped too.
        level = lambda h: 2 if h.startswith("## ") else 3
        dropped_lvl = None
        for h in _headings(full):
            if dropped_lvl is not None and level(h) > dropped_lvl:
                continue                       # nested inside a dropped block
            if any(h.startswith(k) for k in _FAST_SECTIONS):
                dropped_lvl = level(h)
                continue
            dropped_lvl = None
            self.assertIn(h, fast,
                          f"fast may drop ONLY _FAST_SECTIONS blocks; missing: {h!r}")

    def test_default_lane_keeps_every_section(self):
        # floor pin: the full scaffold still carries all seven step sections
        full = self._scaffold("plain-t")
        for n in range(1, 8):
            self.assertRegex(full, rf"(?m)^## {n} ·",
                             f"the full lane must keep §{n}")


# ── M3: oneshot keeps its headers and the AI-verify freeze floor ─────────────
class OneshotFloorTest(_Board):
    def test_oneshot_scaffold_carries_headers_and_record(self):
        text = self._scaffold("o-t", "--oneshot")
        self.assertIn("fast: true", text)
        self.assertIn("oneshot: true", text)
        self.assertIn("gate_mode: ai-plan-verify", text)
        self.assertIn("### AI-verify record", text,
                      "the spliced §3 AI-verify block must survive the one-template rebuild")

    def test_unticked_checklist_refuses_ai_freeze(self):
        self._write_task("t", REAL_BOUNDARY, oneshot=True, ai_boxes_ticked=False)
        out, err, code = self._run("freeze", "t", "--ai-plan-verify", "--by", "test-agent")
        self.assertNotEqual(code, 0)
        self.assertIn("ai_freeze_checklist_incomplete", out + err,
                      f"the AI-verify floor must hold: {out + err}")


# ── M6: the boundary floor fires on BOTH lanes ────────────────────────────────
class BoundaryBothLanesTest(_Board):
    def test_fast_lane_placeholder_refused(self):
        self._write_task("t", PLACEHOLDER_BOUNDARY, fast=True)
        out, err, code = self._run("freeze", "t", "--by", "Tester")
        self.assertNotEqual(code, 0)
        self.assertIn("boundary_unfilled", out + err)

    def test_full_lane_placeholder_refused(self):
        # lane-agnostic at cmd_freeze (green pin); M6's red half is
        # TemplateShapeTest.test_full_template_carries_boundary_line
        self._write_task("t", PLACEHOLDER_BOUNDARY, fast=False)
        out, err, code = self._run("freeze", "t", "--by", "Tester")
        self.assertNotEqual(code, 0)
        self.assertIn("boundary_unfilled", out + err)


# ── M4: the family lean-pass — smaller files, machine-read lines intact ──────
class FamilyByteLedgerTest(unittest.TestCase):
    # pre-task sizes recorded 2026-07-16 (the lean-pass must strictly shrink each,
    # even though PLAN.md.tmpl GAINS the Boundary: line)
    LEDGER = {
        "PLAN.md.tmpl": 12209,
        "MILESTONE.md.tmpl": 4211,
        "PROMPT.persona.md.tmpl": 3225,
        "personas/_template.md.tmpl": 6922,
    }
    ANCHORS = {
        "PLAN.md.tmpl": ("<must>", "<reject>", "<scenarios>", "<test_plan>",
                         "Status: DRAFT", "### GATE RECORD",
                         "Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>",
                         "Scope (may touch):"),
        "MILESTONE.md.tmpl": ("## Tasks", "## Exit criteria", "## Scope",
                              "### Goal met?"),
        "PROMPT.persona.md.tmpl": ("## Adapter stubs",),
        "personas/_template.md.tmpl": ("## Identity", "## Abilities",
                                       "## Critical Rules", "## Playbook"),
    }

    def test_every_family_file_measurably_leaner(self):
        for rel, ceiling in self.LEDGER.items():
            size = (TEMPLATES / rel).stat().st_size
            self.assertLess(size, ceiling,
                            f"{rel} must shrink below its pre-task {ceiling}B (now {size}B)")

    def test_machine_read_lines_survive_the_cut(self):
        for rel, anchors in self.ANCHORS.items():
            body = (TEMPLATES / rel).read_text(encoding="utf-8")
            for a in anchors:
                self.assertIn(a, body, f"{rel} lean-pass must keep {a!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
