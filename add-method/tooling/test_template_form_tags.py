#!/usr/bin/env python3
"""test_template_form_tags.py — the v18 FORM-TAG amendment's parse-seam suite.

The amendment is drafted in .add/tasks/xml-prompt-structure/TASK.md §3: TASK.md.tmpl's
six fill regions gain a CLOSED form-tag class (must · reject · after · assumptions ·
scenarios · test_plan) — a class DISJOINT from the v16 instruction tags, templates-only.
This suite proves the ENGINE READS NEW SCAFFOLDS UNCHANGED (the seam invariant) and that
the guards catch each contracted reject code. Tests scaffold REAL projects via add.main()
and assert engine output, never internals-by-inspection.

Written RED-FIRST (tests phase, before Build): the behavior tests fail until the
templates carry the tags; the reject-fixture tests prove the guards' sensitivity.

Run: python3 -m unittest test_template_form_tags -v
"""
from __future__ import annotations

import os
import re
import tempfile
import shutil
import unittest
from pathlib import Path

import add

# ── the contracted vocabulary (TASK.md §3, v18 amendment) ────────────────────────────
FORM_TAGS = {"must", "reject", "after", "assumptions", "scenarios", "test_plan"}
INSTRUCTION_TAGS = {"prompt", "exit_gate", "constraints", "reject_codes", "output_format"}

# labels that must SURVIVE next to their tags (reject label_dropped)
LABELS = (
    "Must:",
    "Reject:",
    "After:",
    "Assumptions — lowest-confidence first:",
    "Framings weighed:",
)

# engine-parsed seams that must survive in a scaffold (reject parsed_seam_touched)
SEAM_PATTERNS = {
    "phase_marker": re.compile(r"^phase: ground", re.M),
    "title": re.compile(r"^# TASK: ", re.M),
    "status_draft": re.compile(r"^Status: DRAFT", re.M),
    "outcome": re.compile(r"^Outcome: <PASS \| RISK-ACCEPTED \| HARD-STOP>", re.M),
    "tests_live_in": re.compile(r"^Tests live in: `", re.M),
    "security_checklist": re.compile(r"^\s*- \[ \] no exposed secrets", re.M),
    "gate_record": re.compile(r"^### GATE RECORD", re.M),
}

_OPEN = re.compile(r"<([a-z][a-z0-9_-]*)>")
_CLOSE = re.compile(r"</([a-z][a-z0-9_-]*)>")
_TOOLING = Path(add.__file__).resolve().parent
_REPO = _TOOLING.parents[1]  # .../AIDD-Book


def _paired_tags(text: str) -> set[str]:
    """Paired <x>…</x> names — the convention's tag test; unpaired <x> is a prose
    placeholder and never counts (v16 disambiguation rule)."""
    return set(_OPEN.findall(text)) & set(_CLOSE.findall(text))


def _dogfood_task(slug: str) -> Path | None:
    """Resolve a dogfood TASK.md: the active tree first, else a compacted recovery
    bundle (`compact` moves an archived milestone's files to .add/archive/<m>/tasks/,
    it never deletes). None only on a fresh package without dogfood history —
    re-aimed at the v18 close when compaction moved both pinned artifacts
    (human-approved change-request; stale-guard-sweep convention)."""
    active = _REPO / ".add" / "tasks" / slug / "TASK.md"
    if active.exists():
        return active
    for cand in sorted(_REPO.glob(f".add/archive/*/tasks/{slug}/TASK.md")):
        return cand
    return None


# ── the guards (the amendment's reject codes as callable checks) ─────────────────────
def form_tag_offenses(template_text: str) -> list[str]:
    """All v18 reject codes detectable from one template text, by name."""
    offenses: list[str] = []
    paired = _paired_tags(template_text)
    if paired & INSTRUCTION_TAGS:
        offenses.append("class_mixed")
    if paired - INSTRUCTION_TAGS - FORM_TAGS:
        offenses.append("form_vocab_offmidiom")
    for tag in sorted(paired & FORM_TAGS):
        if re.search(rf"^\s*<{tag}>.+</{tag}>\s*$", template_text, re.M):
            offenses.append("inline_fill")
            break
    if paired & {"must", "reject", "after", "assumptions"}:
        for label, tag in (("Must:", "must"), ("Reject:", "reject"), ("After:", "after"),
                           ("Assumptions — lowest-confidence first:", "assumptions")):
            if tag in paired and label not in template_text:
                offenses.append("label_dropped")
                break
    for name, pat in SEAM_PATTERNS.items():
        if not pat.search(template_text):
            offenses.append("parsed_seam_touched")
            break
    return offenses


def tree_parity_offenses() -> list[str]:
    """template_drift if any of the 7 .tmpl files differs across the two tooling trees."""
    canon = _REPO / "add-method" / "tooling" / "templates"
    dogfood = _REPO / ".add" / "tooling" / "templates"
    if not dogfood.exists():
        return []  # fresh package without the dogfood mirror — parity is vacuous
    names = {p.name for p in canon.glob("*.tmpl")} | {p.name for p in dogfood.glob("*.tmpl")}
    return ["template_drift"] if any(
        not (canon / n).exists() or not (dogfood / n).exists()
        or (canon / n).read_bytes() != (dogfood / n).read_bytes()
        for n in sorted(names)
    ) else []


class _ScaffoldBase(unittest.TestCase):
    """Real end-to-end scaffold in a temp project (the test_cospecify_scaffold pattern)."""

    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-formtags-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.tmp)
        add.main(["init"])
        add.main(["new-task", "demo", "--title", "Demo feature"])
        self.root = Path(self.tmp) / ".add"
        self.task_md = self.root / "tasks" / "demo" / "TASK.md"

    def tearDown(self):
        os.chdir(self._cwd)


# ── behavior: the scaffold carries the amendment (RED until Build) ───────────────────
class ScaffoldCarriesFormTags(_ScaffoldBase):
    def test_scaffold_carries_form_tags(self):
        text = self.task_md.read_text(encoding="utf-8")
        paired = _paired_tags(text)
        self.assertEqual(
            FORM_TAGS, paired & FORM_TAGS,
            f"scaffold must carry all six form tags; missing: {FORM_TAGS - paired}",
        )
        for tag in sorted(FORM_TAGS):  # own-line open AND close (block boundaries)
            self.assertRegex(text, rf"(?m)^\s*<{tag}>\s*$", f"<{tag}> must open on its own line")
            self.assertRegex(text, rf"(?m)^\s*</{tag}>\s*$", f"</{tag}> must close on its own line")
        for label in LABELS:  # labels are never replaced by tags
            self.assertIn(label, text, f"label survives beside its tag: {label!r}")
        self.assertEqual([], form_tag_offenses(text), "a clean scaffold has zero offenses")

    def test_filled_region_reads_nonempty(self):
        text = self.task_md.read_text(encoding="utf-8")
        self.assertIn("<must>", text, "needs the <must> region to fill (RED until Build)")
        filled = text.replace("<must>", "<must>\n  - debit and credit post atomically", 1)
        self.task_md.write_text(filled, encoding="utf-8")
        bodies = {p["n"]: p["body"] for p in add.task_phases(self.root, "demo")}
        self.assertNotEqual("(empty)", bodies[1], "a filled tagged region must count as content")
        self.assertIn("debit and credit post atomically", bodies[1])

    def test_lean_pass_single_freeze_comment(self):
        tmpl = (_TOOLING / "templates" / "TASK.md.tmpl").read_text(encoding="utf-8")
        sec3 = tmpl.split("## 3 · CONTRACT")[1].split("## 4 · TESTS")[0]
        self.assertEqual(
            1, sec3.count("<!--"),
            "lean pass: §3 carries ONE merged instruction comment (today: three)",
        )
        # the pre-lean template carried 12 comment opens; the §4 grammar comment and the
        # header risk comment are PINNED by test_declare_grammar_doc / test_high_risk_signal
        # and must not move — "shrank" is the contracted assertion (TASK.md §4 plan).
        self.assertLess(
            tmpl.count("<!--"), 12,
            "lean pass: total comment volume must shrink below the pre-lean 12",
        )


# ── behavior: the engine reads new scaffolds unchanged (the seam invariant) ──────────
class EngineSeamsUnchanged(_ScaffoldBase):
    def test_unfilled_scaffold_semantics_unchanged(self):
        # today an unfilled scaffold's 7 bodies show their labels (Feature:/Must:/…) —
        # adding tags must not flip any section's emptiness class in either direction.
        bodies = [p["body"] for p in add.task_phases(self.root, "demo")]
        self.assertNotIn("(empty)", bodies,
                         "all 7 bodies keep their labels, exactly as on the old template")
        # …and a tag-only block is placeholder-class: tags alone never fabricate content
        self.assertEqual("(empty)", add._clean_phase_body("<must>\n</must>"))

    def test_phase_marker_roundtrip_and_seams(self):
        text = self.task_md.read_text(encoding="utf-8")
        for name, pat in SEAM_PATTERNS.items():
            self.assertTrue(pat.search(text), f"parsed seam survives in scaffold: {name}")
        add.main(["advance"])  # ground -> specify, syncs the marker into TASK.md
        self.assertRegex(self.task_md.read_text(encoding="utf-8"), r"(?m)^phase: specify",
                         "the phase: marker sync must keep working on the new template")

    def test_freeze_gate_and_declared_count_seams(self):
        text = self.task_md.read_text(encoding="utf-8")
        self.assertFalse(any(re.match(r"\s*Status:\s*FROZEN", ln) for ln in text.splitlines()),
                         "a fresh scaffold is DRAFT")
        stamped = text.replace("Status: DRAFT", "Status: FROZEN @ v1 — approved by tester", 1)
        self.task_md.write_text(stamped, encoding="utf-8")
        sec3 = stamped.split("## 3 · CONTRACT")[1].split("## 4 ·")[0]
        self.assertTrue(any(re.match(r"\s*Status:\s*FROZEN", ln) for ln in sec3.splitlines()),
                        "the freeze stamp parses exactly as before")
        tests_dir = self.root / "tasks" / "demo" / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "test_demo.py").write_text("def test_x():\n    assert True\n")
        self.assertEqual(1, add._declared_tests_count(self.root, "demo"),
                         "`Tests live in:` token counting is byte-compatible")


# ── behavior: scope edges (milestone/project untagged · class separation · parity) ───
class ScopeEdges(unittest.TestCase):
    def test_milestone_project_templates_untagged(self):
        for name in ("MILESTONE.md", "PROJECT.md"):
            text = add._render_template(name, title="T", goal="G", stage="mvp",
                                        date="2026-01-01", project="p")
            self.assertEqual(set(), _paired_tags(text) & (FORM_TAGS | INSTRUCTION_TAGS),
                             f"{name}.tmpl carries NO tags in v18 (clarity edits only)")
        mtext = add._render_template("MILESTONE.md", title="T", goal="G", stage="mvp",
                                     date="2026-01-01")
        self.assertIn("## Exit criteria", mtext)
        self.assertRegex(mtext, r"(?m)^- \[ \] ")

    def test_class_separation_templates_vs_guides(self):
        for tmpl in (_TOOLING / "templates").glob("*.tmpl"):
            paired = _paired_tags(tmpl.read_text(encoding="utf-8"))
            self.assertEqual(set(), paired & INSTRUCTION_TAGS,
                             f"instruction tags never in templates: {tmpl.name}")
            self.assertEqual(set(), paired - FORM_TAGS,
                             f"template tags stay inside the closed form set: {tmpl.name}")
        skill = _TOOLING.parent / "skill" / "add"
        for guide in skill.rglob("*.md"):
            paired = _paired_tags(guide.read_text(encoding="utf-8"))
            self.assertEqual(set(), paired & FORM_TAGS,
                             f"form tags never in skill guides: {guide.relative_to(skill)}")

    def test_template_tree_parity_all_seven(self):
        dogfood = _REPO / ".add" / "tooling" / "templates"
        if not dogfood.exists():
            self.skipTest("dogfood mirror absent (fresh package)")
        self.assertEqual([], tree_parity_offenses(),
                         "all 7 .tmpl files byte-identical across both tooling trees")

    def test_amendment_is_a_frozen_artifact(self):
        task = _dogfood_task("xml-prompt-structure")
        v16 = _dogfood_task("xml-convention")  # resolved up front: BOTH pins or skip,
        if task is None or v16 is None:        # so the v16 read can never crash bare
            self.skipTest("amendment task absent (fresh package without dogfood history)")
        text = task.read_text(encoding="utf-8")
        sec3 = text.split("## 3 · CONTRACT")[1].split("## 4 ·")[0]
        for tag in sorted(FORM_TAGS):
            self.assertIn(f"<{tag}>", sec3, f"amendment names the closed set member <{tag}>")
        self.assertTrue(any(re.match(r"\s*Status:\s*FROZEN @ v18", ln)
                            for ln in sec3.splitlines()),
                        "the amendment is FROZEN @ v18 (one human approval) — RED until then")
        v16_sec3 = v16.read_text(encoding="utf-8").split("## 3 · CONTRACT")[1]
        for tag in sorted(INSTRUCTION_TAGS):
            self.assertIn(f"<{tag}>", v16_sec3, "the v16 five remain unchanged")


# ── guard sensitivity: each contracted reject code fires on its fixture ──────────────
class RejectGuards(unittest.TestCase):
    CLEAN = (
        "# TASK: t\n\nphase: ground\n\nMust:\n<must>\n  - <required behavior>\n</must>\n"
        "Reject:\n<reject>\n  - <bad> -> \"<code>\"\n</reject>\n"
        "After:\n<after>\n  - <state>\n</after>\n"
        "Assumptions — lowest-confidence first:\n<assumptions>\n  ⚠ <a>\n</assumptions>\n"
        "Framings weighed: <x>\nStatus: DRAFT\n"
        "Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>\n### GATE RECORD\n"
        "Tests live in: `./tests/`\n  - [ ] no exposed secrets, injection openings\n"
    )

    def test_clean_fixture_has_no_offenses(self):
        self.assertEqual([], form_tag_offenses(self.CLEAN))

    def test_reject_inline_fill(self):
        bad = self.CLEAN.replace("<must>\n  - <required behavior>\n</must>",
                                 "<must>debit+credit atomic</must>")
        self.assertIn("inline_fill", form_tag_offenses(bad))

    def test_inline_fill_hazard_is_real(self):
        # the WHY behind the rule, pinned to engine behavior: a filled one-line element
        # is placeholder-shaped, so the section reads (empty) — a silent spec loss.
        self.assertEqual("(empty)", add._clean_phase_body("<must>debit+credit atomic</must>"))

    def test_reject_class_mixed(self):
        bad = self.CLEAN + "<constraints>\nnever do X\n</constraints>\n"
        self.assertIn("class_mixed", form_tag_offenses(bad))

    def test_reject_form_vocab_offmidiom(self):
        bad = self.CLEAN + "<notes>\nfree text\n</notes>\n"
        self.assertIn("form_vocab_offmidiom", form_tag_offenses(bad))

    def test_reject_label_dropped(self):
        bad = self.CLEAN.replace("Must:\n<must>", "<must>")
        self.assertIn("label_dropped", form_tag_offenses(bad))

    def test_reject_parsed_seam_touched(self):
        bad = self.CLEAN.replace("- [ ] no exposed secrets, injection openings",
                                 "- [ ] security looks fine")
        self.assertIn("parsed_seam_touched", form_tag_offenses(bad))

    def test_reject_template_drift(self):
        canon = _REPO / "add-method" / "tooling" / "templates" / "TASK.md.tmpl"
        dogfood = _REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl"
        if not dogfood.exists():
            self.skipTest("dogfood mirror absent")
        original = dogfood.read_bytes()
        try:
            dogfood.write_bytes(original + b"\n<!-- drift -->\n")
            self.assertEqual(["template_drift"], tree_parity_offenses(),
                             "a single diverged byte must fail parity")
        finally:
            dogfood.write_bytes(original)
        self.assertEqual(canon.read_bytes(), dogfood.read_bytes())


# ── behavior: §6 gains the AI-filled Build-expectations block (verify-build-expectations v1) ──
class BuildExpectationsBlock(unittest.TestCase):
    TASK_TMPL = (
        _REPO / "add-method" / "tooling" / "templates" / "TASK.md.tmpl",
        _REPO / ".add" / "tooling" / "templates" / "TASK.md.tmpl",
        _REPO / "add-method" / "src" / "add_method" / "_bundled" / "tooling" / "templates" / "TASK.md.tmpl",
    )
    VERIFY_GUIDE = (
        _REPO / "add-method" / "skill" / "add" / "phases" / "6-verify.md",
        _REPO / ".claude" / "skills" / "add" / "phases" / "6-verify.md",
        _REPO / "add-method" / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "6-verify.md",
    )

    def _section6(self) -> str:
        tmpl = self.TASK_TMPL[0].read_text(encoding="utf-8")
        return tmpl.split("## 6 · VERIFY")[1].split("## 7 · OBSERVE")[0]

    def test_build_expectations_block_present_in_section6(self):
        sec6 = self._section6()
        self.assertIn("### Build expectations", sec6,
                      "§6 must carry a '### Build expectations' block")
        # the existing §6 parts must survive (the block is additive)
        self.assertIn("### Deep checks", sec6, "Deep checks subsection retained")
        self.assertIn("### GATE RECORD", sec6, "GATE RECORD retained")
        self.assertIn("- [ ] all tests pass", sec6, "the §6 checklist retained")

    def test_block_cue_is_observable_and_derived(self):
        sec6 = self._section6()
        block = sec6.split("### Build expectations")[1].split("### ")[0].lower()
        self.assertIn("confirmed by", block,
                      "each expectation row carries a 'confirmed by'")
        self.assertIn("before build", block,
                      "the block is filled before build")
        self.assertTrue("scenario" in block and "contract" in block,
                        "the cue must name the §2 scenarios + §3 contract derivation")

    def test_engine_seams_untouched_by_the_block(self):
        # the amended template still passes every parsed-seam guard (no parsed_seam_touched).
        tmpl = self.TASK_TMPL[0].read_text(encoding="utf-8")
        self.assertEqual([], form_tag_offenses(tmpl),
                         "the new block must leave the amended template offense-free")

    def test_verify_guide_cues_fill_and_confirm(self):
        guide = self.VERIFY_GUIDE[0].read_text(encoding="utf-8").lower()
        self.assertIn("build expectations", guide,
                      "6-verify.md must reference the build-expectations block")
        self.assertTrue("before build" in guide or "fill" in guide,
                        "the guide cues filling the expectations before build")
        self.assertIn("confirm", guide,
                      "the guide cues confirming each expectation at the gate")

    def test_template_and_guide_parity_three_trees(self):
        for group, label in ((self.TASK_TMPL, "TASK.md.tmpl"), (self.VERIFY_GUIDE, "6-verify.md")):
            present = [p for p in group if p.exists()]
            if len(present) < 2:
                self.skipTest(f"{label}: fewer than 2 trees present (fresh package)")
            blobs = {p.read_bytes() for p in present}
            self.assertEqual(1, len(blobs), f"{label} diverged across its parity trees")


if __name__ == "__main__":
    unittest.main()
