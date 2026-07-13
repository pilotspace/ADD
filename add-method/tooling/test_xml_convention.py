"""test_xml_convention.py — enforce the v16 XML prompt convention on the pilot.

The convention is frozen in .add/tasks/xml-convention/TASK.md §3. This guard asserts it on
the worked-reference pilot (phases/1-specify.md, FULLY converted) and grows file-by-file as
later v16 tasks land: the 7 phase guides (task phase-guides-xml) and the 10 engine docs
(task engine-docs-xml — the first use of <constraints>/<reject_codes>).

Scope (task xml-convention): the pilot only. The 3-mirror parity is enforced by
test_bundle_parity + test_tree_parity (not re-authored here — checking the canonical tree suffices,
since parity guarantees _bundled/ and .claude/skills/add/ match it byte-for-byte).

Run: python3 -m unittest test_xml_convention -v
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_SKILL = _TOOLING.parent / "skill" / "add"
PILOT = _SKILL / "phases" / "1-specify.md"

# The frozen CLOSED vocabulary (TASK.md §3 CONTRACT). A tag outside this set = reject `vocab_offmidiom`.
# Lean BLOCK-LEVEL core: 5 tags, all-underscore. Tags mark block BOUNDARIES only — NO field children,
# NO nesting. Inside <prompt> the appendix-b skeleton labels (Role:/Read first:/Steps:/Never:) stay
# plain text. A stray field tag like <role> is auto-rejected here (it's not in the 5-tag set).
VOCAB = {
    "prompt", "exit_gate", "constraints", "reject_codes", "output_format",
}

# Sections of the pilot that are genuine narrative — they MUST stay prose (reject `narrative_tagged`).
NARRATIVE_HEADERS = ("## Co-specify in three moves", "## The lowest-confidence flag is bundle-wide")

_OPEN = re.compile(r"<([a-z][a-z0-9_-]*)>")
_CLOSE = re.compile(r"</([a-z][a-z0-9_-]*)>")


def _paired_tags(text: str) -> set[str]:
    """Convention tags are PAIRED. A name with both <x> and </x> is a convention tag;
    a single unpaired <x> is a prose placeholder (<name>, <why>, <cost>) and is ignored."""
    return set(_OPEN.findall(text)) & set(_CLOSE.findall(text))


def _section(text: str, header: str) -> str:
    """Return the body of a '## <header>' section, up to the next '## ' or EOF."""
    out: list[str] = []
    grabbing = False
    for line in text.splitlines():
        if line.strip() == header:
            grabbing = True
            continue
        if grabbing and line.startswith("## "):
            break
        if grabbing:
            out.append(line)
    return "\n".join(out)


_FENCE = re.compile(r"```.*?```", re.DOTALL)


def _strip_code_fences(text: str) -> str:
    """Drop ```…``` fenced blocks so paired tags INSIDE a fence don't count as convention tags
    (the convention leaves code fences as markdown — they are self-marking). Tags OUTSIDE a fence
    survive. This is what makes streams.md's worker-contract ```xml block exempt from the vocab
    check while a `<constraints>` wrap placed OUTSIDE a fence is still seen."""
    return _FENCE.sub("", text)


# ─── task phase-guides-xml: the 7 remaining phase guides (0,2-7) ──────────────────────────────
# Each guide applies the SAME three tags the pilot uses — prompt · output_format · exit_gate —
# and introduces NO new vocabulary (constraints/reject_codes are reserved for the engine docs, task 3).
# The narrative list per file is ENUMERATED so the over-tagging guard is real, not hollow: a tag on any
# listed narrative section fails test_phase_narrative_untagged.
PHASE_SUBSET = {"prompt", "output_format", "exit_gate"}
PHASE_FILES = {
    "0-setup.md": {
        "prompt": False, "output_format": False,
        "narrative": (
            "## 1 · Zero-touch entry — you run init yourself",
            "## 2a · Brownfield — map it silently",
            "## 2b · Greenfield — the 4-lens interview (kept): co-specify at foundation level",
            "## 3 · Draft to the lock (both paths)",
            "## 4 · The one human gate — the baseline approval",
            "## 5 · After the lock",
            "## Next",
        )},
    "2-scenarios.md": {
        "prompt": True, "output_format": True,
        "narrative": ("## Next",)},
    "3-plan.md": {
        "prompt": True, "output_format": True,
        "narrative": ("## The freeze review checklist", "## Next")},
    "4-tests.md": {
        "prompt": True, "output_format": True,
        "narrative": ("## The must-fail principle", "## Declaring where tests live", "## Next")},
    "5-build.md": {
        "prompt": True, "output_format": False,
        "narrative": ("## Work in small batches", "## The cardinal rule", "## Next")},
    "6-verify.md": {
        "prompt": False, "output_format": False,
        "narrative": (
            "## Part one — confirm the evidence",
            "## Part two — check what tests miss",
            "## Part four — was the green earned?",
            "## Record exactly one outcome (no silent pass)",
        )},
    "7-observe.md": {
        "prompt": True, "output_format": False,
        "narrative": ("## Do", "## Next")},
}


def _produce_section(text: str) -> str:
    """Body of the '## Produce…' section (header varies: '## Produce', '## Produce (in TASK.md §2)')."""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("## Produce"):
            return _section(text, s)
    return ""


class TestXmlConventionPhaseGuides(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.texts = {}
        for name in PHASE_FILES:
            p = _SKILL / "phases" / name
            assert p.exists(), f"phase guide missing: {p}"
            cls.texts[name] = p.read_text(encoding="utf-8")

    def test_phase_prompts_converted(self) -> None:
        """Must: every guide that HAS a '## AI prompt' carries a block-level <prompt> (plain-text Role:, no field tags), header preserved."""
        for name, spec in PHASE_FILES.items():
            if not spec["prompt"]:
                continue
            text = self.texts[name]
            self.assertIn("## AI prompt", text, f"{name}: '## AI prompt' header dropped")
            block = re.search(r"<prompt>(.*?)</prompt>", text, re.DOTALL)
            self.assertIsNotNone(block, f"{name}: no <prompt>…</prompt> block")
            body = block.group(1)
            self.assertIn("Role:", body, f"{name}: plain-text 'Role:' label missing inside <prompt>")
            self.assertEqual(_paired_tags(body), set(),
                             f"{name}: field-level tags inside <prompt> — use plain-text labels")

    def test_phase_output_format(self) -> None:
        """Must: every guide that HAS a '## Produce' wraps its body in <output_format>."""
        for name, spec in PHASE_FILES.items():
            if not spec["output_format"]:
                continue
            text = self.texts[name]
            self.assertIn("<output_format>", text, f"{name}: no <output_format> block")
            self.assertIn("<output_format>", _produce_section(text),
                          f"{name}: <output_format> is not inside the '## Produce' section")

    def test_phase_exit_gate(self) -> None:
        """Must: all 7 guides carry an <exit_gate> block."""
        for name in PHASE_FILES:
            self.assertIn("<exit_gate>", self.texts[name], f"{name}: no <exit_gate> block")

    def test_phase_vocab_subset(self) -> None:
        """Reject vocab_offmidiom: every paired tag in the 7 guides ∈ {prompt, output_format, exit_gate}."""
        for name in PHASE_FILES:
            tags = _paired_tags(self.texts[name])
            self.assertTrue(tags, f"{name}: no paired convention tags found (not converted)")
            offenders = tags - PHASE_SUBSET
            self.assertFalse(offenders, f"{name}: out-of-subset tags {sorted(offenders)} (constraints/reject_codes belong to task 3)")

    def test_phase_narrative_untagged(self) -> None:
        """Reject narrative_tagged: each file's enumerated narrative sections carry NO paired tags."""
        for name, spec in PHASE_FILES.items():
            text = self.texts[name]
            for header in spec["narrative"]:
                body = _section(text, header)
                self.assertEqual(_paired_tags(body), set(),
                                 f"{name}: narrative section {header!r} carries convention tags — must stay prose")


# ─── task engine-docs-xml: the 10 engine docs ─────────────────────────────────────────────────
# Engine docs carry ONLY <constraints> + <reject_codes> — the two tags the frozen TAG→FIRST-USE map
# reserved for the engine layer (this is their first use). <output_format> is intentionally ABSENT:
# every engine-doc output-shape is a CODE FENCE (deltas' grammar, report-template's five-block digest,
# setup-review's template), left as markdown per the convention's fence-exemption — <output_format>
# already earns its use in task 2's phase-guide "## Produce" prose. streams.md's worker-contract ```xml
# fence is UNTOUCHED (pre-existing worker scaffolding inside a fence): the vocab check strips code
# fences first, and a positive guard asserts the worker contract SURVIVES. The narrative list per file
# is ENUMERATED so the over-tagging guard is real, not hollow.
ENGINE_SUBSET = {"constraints", "reject_codes"}  # STRICT — excludes output_format on purpose
WORKER_CONTRACT_TAGS = {
    "objective", "persona", "strategy", "touch_boundary", "context_files", "expertise", "tools", "return",
}
ENGINE_FILES = {
    "confidence.md": {
        "tags": {"constraints"},
        "narrative": (
            "## The six dimensions",
            "## Where it plugs in",
        )},
    "advisor.md": {
        "tags": {"constraints"},
        "narrative": (
            "## When to spawn — and when not",
            "## The plan-following prompt template",   # holds the ```xml template fence
            "## Choosing the model — vendor-neutral tiers",
        )},
    "design.md": {                                     # UDD design-definition loop (udd-design-loop)
        "tags": {"constraints"},
        "narrative": (
            "## The loop — four beats",
            "## Tool-agnostic capture",
        )},
    "SKILL.md": {
        "tags": {"constraints"},
        "narrative": (
            "## The flow and which file to load",
            "## Depth by stage",
            "## The method rationale",
        )},
    "intake.md": {
        "tags": {"reject_codes"},
        "narrative": (
            "## The four buckets",
            "## Worked examples (from this project's own history)",
        )},
    "scope.md": {
        "tags": {"reject_codes"},
        "narrative": (
            "## What to do per intake outcome",
            "## Worked example (from this repo's own history)",
        )},
    "run.md": {
        "tags": {"constraints"},
        "narrative": (
            "## The specification bundle (v7)",
        )},
    "streams.md": {
        "tags": {"constraints"},
        "narrative": (
            "## The two queues",
            "## Design for failure (required)",
            "## The worker contract — portable across coding agents",  # holds the ```xml fence
        )},
    "deltas.md": {
        "tags": {"reject_codes"},
        "narrative": (
            "## The grammar (frozen)",                                  # holds a ``` fence
            "## The five competencies (pick exactly one per delta)",
            "## Worked example",
        )},
    "fold.md": {
        "tags": {"reject_codes"},
        "narrative": (
            "## The ritual",
            "## Fold routing (every competency has a home)",
            "## Worked example (from this repo's own history)",
        )},
    "adopt.md": {
        "tags": {"constraints"},  # "Two rules that never bend" lives INSIDE "## The silent mapping"
        "narrative": (
            "## The signal — and arming the gate",
            "## Where it ends — the baseline approval",
        )},
    "report-template.md": {
        "tags": {"constraints"},
        "narrative": (
            "## The report blocks, in order",                          # holds the digest ``` fence
        )},
    "setup-review.md": {
        "tags": {"constraints"},
        "narrative": (
            "## Where it lives",
            "## The template",                                         # holds the ```markdown fence
            "## Where it ends",
        )},
}


class TestXmlConventionEngineDocs(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.texts = {}
        for name in ENGINE_FILES:
            p = _SKILL / name
            assert p.exists(), f"engine doc missing: {p}"
            cls.texts[name] = p.read_text(encoding="utf-8")

    def test_engine_tags_present(self) -> None:
        """Must: each engine doc carries each of the paired convention tag(s) the map assigns it."""
        for name, spec in ENGINE_FILES.items():
            text = self.texts[name]
            for tag in spec["tags"]:
                self.assertIsNotNone(re.search(rf"<{tag}>.*?</{tag}>", text, re.DOTALL),
                                     f"{name}: no <{tag}>…</{tag}> block (not converted)")

    def test_engine_vocab_subset(self) -> None:
        """Reject vocab_offmidiom / fenced_shape_tagged: every paired tag (code fences stripped)
        in each engine doc ∈ {constraints, reject_codes}. STRICT — output_format here would fail."""
        for name in ENGINE_FILES:
            tags = _paired_tags(_strip_code_fences(self.texts[name]))
            self.assertTrue(tags, f"{name}: no paired convention tags found (not converted)")
            offenders = tags - ENGINE_SUBSET
            self.assertFalse(offenders,
                             f"{name}: out-of-subset tags {sorted(offenders)} "
                             f"(engine docs use ONLY constraints/reject_codes — no output_format)")
            self.assertNotIn("output_format", tags,
                             f"{name}: <output_format> in an engine doc — fenced shapes stay markdown")

    def test_engine_worker_contract_preserved(self) -> None:
        """Reject worker_contract_touched: streams.md's worker-contract ```xml fence is UNTOUCHED —
        its tags are present in raw text AND gone after fence-strip (fenced ⇒ exempt, never trips vocab)."""
        raw = self.texts["streams.md"]
        raw_tags = _paired_tags(raw)
        missing = WORKER_CONTRACT_TAGS - raw_tags
        self.assertFalse(missing, f"streams.md worker-contract tags missing/altered: {sorted(missing)}")
        stripped_tags = _paired_tags(_strip_code_fences(raw))
        leaked = WORKER_CONTRACT_TAGS & stripped_tags
        self.assertEqual(leaked, set(),
                         f"worker-contract tags {sorted(leaked)} leaked outside the code fence — must stay fenced/exempt")

    def test_engine_narrative_untagged(self) -> None:
        """Reject narrative_tagged: each doc's enumerated narrative sections (fences stripped) carry NO paired tags."""
        for name, spec in ENGINE_FILES.items():
            text = self.texts[name]
            for header in spec["narrative"]:
                body = _strip_code_fences(_section(text, header))
                self.assertEqual(_paired_tags(body), set(),
                                 f"{name}: narrative section {header!r} carries convention tags — must stay prose")


# ─── task appendix-templates-xml: the prompt catalog (docs/appendix-b-prompts.md) ─────────────
# appendix-b reproduces the playbook/ prompts VERBATIM as a published, copy-able book page. Unlike the
# skill/ files (which the agent CONSUMES as text), appendix-b is RENDERED — so each prompt's code fence
# MUST stay a fence: strip it and markdown swallows the <name>/<action> placeholders and re-parses the
# indented `# why:` / step continuations as nested code, silently breaking the page. The convention is
# therefore applied by WRAPPING each intact fence in a block-level <prompt> pair, with a blank line
# after <prompt> and before </prompt> so CommonMark still parses the fence as a code block (the wrap
# tags render as invisible HTML). Fence-strip then leaves the <prompt> pair, so the vocab check sees it.
# Vocab here is exactly {prompt}: a self-contained playbook prompt keeps its Read first:/Task:/Exit:/
# Never: labels as PLAIN TEXT inside <prompt> (the frozen convention's stated rule for appendix-b
# labels) — no output_format / exit_gate / constraints / reject_codes. templates/*.tmpl are pure
# fill-in FORMS with no executable structure: assessed, nothing to tag (recorded at the milestone gate).
_DOCS = _TOOLING.parent / "docs"
APPENDIX_B = _DOCS / "appendix-b-prompts.md"
APPENDIX_SUBSET = {"prompt"}  # STRICT — appendix-b is a {prompt} catalog, nothing else
APPENDIX_INTRO_UNTIL = "### `playbook/1_specify.md`"  # everything before the first prompt is narrative


class TestXmlConventionAppendixB(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        assert APPENDIX_B.exists(), f"appendix-b missing: {APPENDIX_B}"
        cls.text = APPENDIX_B.read_text(encoding="utf-8")

    def test_appendix_prompts_wrapped(self) -> None:
        """Must: every playbook prompt is a block-level <prompt> that STILL CONTAINS its code fence.
        Removing the fence (rendering the body as live markdown) would swallow the <name>/<action>
        placeholders and mangle the indented `# why:` lines — vocab-clean but a broken page."""
        blocks = re.findall(r"<prompt>(.*?)</prompt>", self.text, re.DOTALL)
        fences = _FENCE.findall(self.text)
        self.assertTrue(blocks, "no <prompt> blocks (appendix-b not converted)")
        self.assertEqual(len(blocks), len(fences),
                         f"{len(blocks)} <prompt> blocks vs {len(fences)} code fences — "
                         "each prompt must wrap exactly one intact fence")
        for i, body in enumerate(blocks):
            self.assertIn("```", body,
                          f"<prompt> block #{i + 1} lost its code fence — a removed fence renders the "
                          "prompt as live markdown and mangles its <…> placeholders / indented lines")

    def test_appendix_vocab_subset(self) -> None:
        """Reject vocab_offmidiom: every paired tag (code fences stripped) ∈ {prompt}. No engine/phase tags."""
        tags = _paired_tags(_strip_code_fences(self.text))
        self.assertTrue(tags, "no paired convention tags found (appendix-b not converted)")
        offenders = tags - APPENDIX_SUBSET
        self.assertFalse(offenders,
                         f"out-of-subset tags {sorted(offenders)} — appendix-b is a {{prompt}} catalog only")

    def test_appendix_render_safe(self) -> None:
        """Reject page_mangled: with code fences stripped, NO bare <lowercase> placeholder and NO
        ≥4-space-indented prose line may remain OUTSIDE a fence — both render-break the published page.
        This is the guard a vocab-only check cannot make: it proves the fences were WRAPPED, not removed."""
        stripped = _strip_code_fences(self.text)
        leaked = set(_OPEN.findall(stripped)) - APPENDIX_SUBSET
        self.assertFalse(leaked,
                         f"angle-bracket tokens {sorted(leaked)} leaked outside a fence — "
                         "a removed fence exposed prompt-body placeholders to the renderer")
        indented = [ln for ln in stripped.splitlines() if ln[:4] == "    " and ln.strip()]
        self.assertEqual(indented, [],
                         f"{len(indented)} prose line(s) indented ≥4 spaces outside a fence "
                         f"(markdown renders them as code): {indented[:3]}")

    def test_appendix_intro_untagged(self) -> None:
        """Reject narrative_tagged: the intro paragraph (before the first prompt) stays prose."""
        intro = self.text.split(APPENDIX_INTRO_UNTIL)[0]
        self.assertEqual(_paired_tags(_strip_code_fences(intro)), set(),
                         "appendix-b intro carries convention tags — narrative must stay prose")


class TestXmlConventionPilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        assert PILOT.exists(), f"pilot missing: {PILOT}"
        cls.text = PILOT.read_text(encoding="utf-8")

    def test_pilot_fully_converted(self) -> None:
        """Must: 1-specify.md is the COMPLETE worked reference — block-level <prompt>, <output_format>, <exit_gate>."""
        block = re.search(r"<prompt>(.*?)</prompt>", self.text, re.DOTALL)
        self.assertIsNotNone(block, "no <prompt>…</prompt> block (## AI prompt not converted)")
        body = block.group(1)
        # block-level: skeleton labels are PLAIN TEXT inside <prompt> (not tagged)
        for label in ("Role:", "Never:"):
            self.assertIn(label, body, f"plain-text skeleton label '{label}' missing inside <prompt>")
        self.assertEqual(_paired_tags(body), set(),
                         "field-level tags found inside <prompt> — block-level uses plain-text labels")
        for tag in ("output_format", "exit_gate"):
            self.assertIn(f"<{tag}>", self.text, f"<{tag}> missing — pilot is not a full reference")

    def test_ai_prompt_header_preserved(self) -> None:
        """Reject header_dropped: the '## AI prompt' header survives (test_declare_grammar_doc relies on it)."""
        self.assertIn("## AI prompt", self.text, "the '## AI prompt' header was dropped")

    def test_vocab_in_set(self) -> None:
        """Reject vocab_offmidiom: every PAIRED convention tag is in the frozen vocabulary."""
        tags = _paired_tags(self.text)
        self.assertTrue(tags, "no paired convention tags found (pilot not yet converted)")
        offenders = tags - VOCAB
        self.assertFalse(offenders, f"out-of-vocabulary tags: {sorted(offenders)}")

    def test_narrative_untagged(self) -> None:
        """Reject narrative_tagged: genuine narrative sections carry NO paired convention tags."""
        for header in NARRATIVE_HEADERS:
            body = _section(self.text, header)
            self.assertEqual(_paired_tags(body), set(),
                             f"{header} carries convention tags — narrative must stay prose")


if __name__ == "__main__":
    unittest.main()
