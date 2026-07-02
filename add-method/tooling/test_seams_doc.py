#!/usr/bin/env python3
"""Red/green tests for seams-doc (milestone `seams`): `.add/SEAMS.md` seeds the project-level
cross-cutting-convention registry (5 milestone-ranked entries) plus a `.add/GLOSSARY.md` delta
(`Seam` term + amended `Survivor layer` line). Asserts SHAPE — heading grammar, the Name/Anchor/
Contract/Citations field order, anchor resolution against the CURRENT tree, and a reproducible
Citations pattern — never the exact prose wording, so a future light copyedit doesn't false-fail.

R:same_milestone_repeat and the "concurrency is ruled out" edge case are, per this task's own
§0 Issues/Risks, named human/AI-judged claims ("no mechanical way to verify >=2 DIFFERENT
milestones... never a grep gate" / a single-writer static doc) — they are documented, not faked
as mechanical asserts; see KnownJudgmentCallsAreDocumentedNotFaked below.

Run: cd add-method/tooling && python3 -m unittest test_seams_doc -v
"""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent          # add-method/tooling -> add-method -> repo root
SEAMS = REPO / ".add" / "SEAMS.md"
GLOSSARY = REPO / ".add" / "GLOSSARY.md"
MILESTONES_DIR = REPO / ".add" / "milestones"

# the milestone's frozen rank order (duplication + error-cost weighted — NOT a citation-count sort)
EXPECTED_ORDER = [
    "engine-md5-repin",
    "three-tree-parity",
    "scope-token-grammar",
    "phase-body-extraction",
    "section-unfilled-truth-table",
]
FIELD_ORDER = ["Name:", "Anchor:", "Contract:", "Citations:"]

HEADING_RE = re.compile(r"^## (.+)$", re.MULTILINE)
ANCHOR_SYM_RE = re.compile(r"`([^`:]+):(\d+)`\s*\(`([^`]+)`\)")
BARE_PATH_RE = re.compile(r"`([^`\s]+\.(?:py|md))`(?!:\d)")
EXAMPLES_RE = re.compile(r"e\.g\.(.*)$", re.DOTALL)
METHOD_CMD_RE = re.compile(r"method:\s*`([^`]+)`")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _entry_blocks(text: str) -> dict[str, str]:
    """Split the body into {heading_id: block_text} — a block runs from one `## ` heading to
    the next (or EOF). No headings -> {}."""
    heads = list(HEADING_RE.finditer(text))
    out: dict[str, str] = {}
    for i, m in enumerate(heads):
        start = m.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out[m.group(1)] = text[start:end]
    return out


def _field(block: str, name: str) -> str:
    """Raw text of one field (e.g. 'Contract:') up to the next known field label or block end —
    tolerant of the field's prose wrapping across multiple physical lines."""
    others = "|".join(re.escape(f) for f in FIELD_ORDER if f != name)
    m = re.search(rf"{re.escape(name)}\s*(.*?)(?=\n(?:{others})|\Z)", block, re.DOTALL)
    return m.group(1).strip() if m else ""


def _anchor_citations(anchor_block: str):
    """Yield (path, line_or_None, symbol_or_None) for every citation in an Anchor field — a
    `path:line` + `(symbol)` pair, or a bare `path` (whole-file, no single-symbol anchor)."""
    consumed = []
    for m in ANCHOR_SYM_RE.finditer(anchor_block):
        yield m.group(1), int(m.group(2)), m.group(3)
        consumed.append((m.start(), m.end()))
    stripped = anchor_block
    for start, end in sorted(consumed, reverse=True):
        stripped = stripped[:start] + stripped[end:]
    for m in BARE_PATH_RE.finditer(stripped):
        yield m.group(1), None, None


class SeamsFileIsTheOnlyOne(unittest.TestCase):
    def test_seams_md_exists(self):                                     # M1
        self.assertTrue(SEAMS.exists(), ".add/SEAMS.md must exist as the one project-level file")

    def test_no_milestone_scoped_seams_file(self):                      # R:milestone_scoped_seams_file
        offenders = list(MILESTONES_DIR.glob("*/SEAMS.md")) if MILESTONES_DIR.exists() else []
        self.assertEqual(offenders, [], f"milestone_scoped_seams_file: {offenders}")


class OpensWithTitleAndEvidenceBar(unittest.TestCase):
    def test_h1_title_and_evidence_bar_blockquote(self):                 # M2
        text = _read(SEAMS)
        self.assertRegex(text, r"^# \S", "file must open with an H1 title")
        self.assertRegex(text, r"(?mi)^>.*\b(?:2|two)\b.*milestone",
                          "intro blockquote must state the >=2-different-milestones evidence bar")
        self.assertIn("Seams consulted:", text, "intro must name the citation grammar")


class HeadingsAreBareKebabCaseInFrozenOrder(unittest.TestCase):
    def test_exactly_five_headings_bare_kebab_case_frozen_order(self):   # M3, M7, R:unstable_anchor_slug
        text = _read(SEAMS)
        ids = HEADING_RE.findall(text)
        self.assertEqual(len(ids), 5, f"expected exactly 5 '## ' entries, found {len(ids)}: {ids}")
        for hid in ids:
            self.assertRegex(hid, r"^[a-z0-9-]+$", f"unstable_anchor_slug: {hid!r}")
        self.assertEqual(ids, EXPECTED_ORDER,
                          "entries must ship in the milestone's ranked order, not sorted by citation count")

    def test_grep_c_heading_count_is_five(self):                        # edge case
        out = subprocess.run(["grep", "-c", "^## ", str(SEAMS)], capture_output=True, text=True)
        self.assertEqual(out.stdout.strip(), "5")


class FieldOrderIsNameAnchorContractCitations(unittest.TestCase):
    def test_every_entry_has_fields_in_order(self):
        text = _read(SEAMS)
        blocks = _entry_blocks(text)
        self.assertEqual(len(blocks), 5)
        for hid, block in blocks.items():
            positions = [block.find(f) for f in FIELD_ORDER]
            self.assertTrue(all(p != -1 for p in positions), f"{hid}: missing a required field")
            self.assertEqual(positions, sorted(positions),
                              f"{hid}: fields must appear in Name/Anchor/Contract/Citations order")


class AnchorsResolveInCurrentTree(unittest.TestCase):
    def test_every_anchor_resolves(self):                               # M4, R:unverifiable_anchor
        text = _read(SEAMS)
        blocks = _entry_blocks(text)
        for hid, block in blocks.items():
            anchor_block = _field(block, "Anchor:")
            citations = list(_anchor_citations(anchor_block))
            self.assertTrue(citations, f"{hid}: Anchor field cites nothing")
            has_line_cite = False
            for path, line, symbol in citations:
                target = REPO / path
                self.assertTrue(target.exists(), f"{hid}: unverifiable_anchor - {path} missing")
                if line is not None:
                    has_line_cite = True
                    lines = target.read_text(encoding="utf-8").splitlines()
                    self.assertGreaterEqual(len(lines), line,
                                             f"{hid}: unverifiable_anchor - {path} has <{line} lines")
                    self.assertIn(symbol, lines[line - 1],
                                  f"{hid}: unverifiable_anchor - {symbol!r} not found at {path}:{line}")
            self.assertTrue(has_line_cite, f"{hid}: needs >=1 real path:line anchor")

    def test_no_two_entries_share_an_identical_anchor(self):            # edge case
        text = _read(SEAMS)
        blocks = _entry_blocks(text)
        seen: dict[tuple[str, int], str] = {}
        for hid, block in blocks.items():
            for path, line, _sym in _anchor_citations(_field(block, "Anchor:")):
                if line is None:
                    continue
                key = (path, line)
                self.assertNotIn(key, seen, f"{hid} and {seen.get(key)} collide on anchor {key}")
                seen[key] = hid


class ContractFieldIsOneParagraph(unittest.TestCase):
    def test_contract_is_single_paragraph_no_bullets(self):             # M5
        text = _read(SEAMS)
        blocks = _entry_blocks(text)
        for hid, block in blocks.items():
            contract = _field(block, "Contract:")
            self.assertTrue(contract, f"{hid}: missing Contract field")
            self.assertNotRegex(contract, r"(?m)^\s*[-*]\s", f"{hid}: Contract must not be a bullet list")
            self.assertNotRegex(contract, r"(?m)^#{1,6}\s", f"{hid}: Contract must not contain a sub-heading")
            self.assertNotIn("\n\n", contract, f"{hid}: Contract must be ONE paragraph, no blank-line break")


class CitationsFieldIsReproducible(unittest.TestCase):
    def test_citations_pattern_count_method_sha_examples(self):         # M6, R:uncited_count
        text = _read(SEAMS)
        blocks = _entry_blocks(text)
        for hid, block in blocks.items():
            citations = _field(block, "Citations:")
            self.assertRegex(citations, r"\d", f"{hid}: uncited_count - no digit count")
            # "method:" (a literal grep/query command) is the default reproduction path; a
            # low-count/qualitative entry may instead name a "source:" (e.g. a task's own §7
            # spec-delta) when grep is a documented weak proxy (see scope-token-grammar) — either
            # way it must be backticked and reproducible/spot-checkable, never a bare claim.
            self.assertRegex(citations, r"(?:method|source):\s*`[^`]+`",
                              f"{hid}: uncited_count - no backticked method/source")
            self.assertRegex(citations, r"as of\s*`[0-9a-f]{6,40}`", f"{hid}: uncited_count - no as-of SHA")
            # named examples are usually backtick-fenced after "e.g." (`slug`, `slug`), but a
            # low-count/qualitative entry may instead name them in plain prose within its
            # "source:" sentence (scope-token-grammar names 2 of its 3 that way, no "e.g." at
            # all) — so scan broadly for >=2 DISTINCT task-slug-shaped identifiers (kebab-case,
            # >=1 hyphen) anywhere in the field, after removing the method/source command and
            # the as-of SHA so those never get mistaken for a named example.
            method_or_source_m = re.search(r"(?:method|source):\s*`([^`]+)`", citations)
            as_of_m = re.search(r"as of\s*`([0-9a-f]{6,40})`", citations)
            residual = citations
            for grp in (method_or_source_m, as_of_m):
                if grp:
                    residual = residual.replace(f"`{grp.group(1)}`", "")
            slug_like = set(re.findall(r"\b[a-z][a-z0-9]*(?:-[a-z0-9]+)+\b", residual))
            self.assertGreaterEqual(len(slug_like), 2,
                                     f"{hid}: uncited_count - needs >=2 named example slugs, found {slug_like}")

    def test_engine_md5_repin_citations_command_is_reproducible(self):  # M6 scenario: re-run the grep
        text = _read(SEAMS)
        block = _entry_blocks(text)["engine-md5-repin"]
        citations = _field(block, "Citations:")
        cmd = METHOD_CMD_RE.search(citations).group(1)
        out = subprocess.run(["bash", "-c", cmd], cwd=REPO, capture_output=True, text=True)
        matched = [ln for ln in out.stdout.splitlines() if ln.strip()]
        self.assertTrue(matched, "the stated grep method must actually match files in the current tree")
        examples = re.findall(r"`([^`]+)`", EXAMPLES_RE.search(citations).group(1))
        for slug in examples:
            self.assertTrue(any(f"/{slug}/" in p or p.endswith(f"/{slug}") for p in matched),
                             f"named example {slug!r} must be spot-checkable via the stated method")

    def test_stale_estimate_divergence_is_disclosed_not_silent(self):   # edge case
        text = _read(SEAMS)
        citations = _field(_entry_blocks(text)["engine-md5-repin"], "Citations:")
        self.assertRegex(citations, r"(?i)revis",
                          "a divergence from the milestone's seed estimate must be named inline, not silent")


class GraphNodeRenderingIsRejected(unittest.TestCase):
    def test_no_entry_rendered_as_json_or_yaml_node(self):              # R:graph_node_seam
        text = _read(SEAMS)
        self.assertNotIn("```", text, "graph_node_seam: entries must ship as prose, not a fenced code block")
        for line in text.splitlines():
            self.assertNotRegex(line.strip(), r"^\{.*\}$", "graph_node_seam: no JSON node")


class GlossaryGainsSeamAndAmendsSurvivorLayer(unittest.TestCase):
    def test_seam_defined_and_survivor_layer_lists_seams(self):         # M8
        text = _read(GLOSSARY)
        self.assertRegex(text, r"(?m)^Seam:\s+\S", "GLOSSARY must define 'Seam:'")
        m = re.search(r"(?m)^Survivor layer:.*$", text)
        self.assertTrue(m, "GLOSSARY must still carry a 'Survivor layer:' line")
        self.assertIn("SEAMS", m.group(0), "Survivor layer line must now list SEAMS")


class KnownJudgmentCallsAreDocumentedNotFaked(unittest.TestCase):
    """R:same_milestone_repeat and the concurrency-ruled-out edge case are, per this task's own
    §0 Issues/Risks, named human/AI-judged claims — 'no mechanical way to verify >=2 DIFFERENT
    milestones... never a grep gate.' The closest honest mechanical guard: the shipped entry set
    is EXACTLY the milestone's human-vetted 5 (also asserted by test_exactly_five_headings_...);
    any addition beyond it needs the same deliberate vetting, never a silent grep promotion."""
    def test_entry_set_is_closed_to_the_vetted_five(self):
        text = _read(SEAMS)
        self.assertEqual(set(HEADING_RE.findall(text)), set(EXPECTED_ORDER))


if __name__ == "__main__":
    unittest.main(verbosity=2)
