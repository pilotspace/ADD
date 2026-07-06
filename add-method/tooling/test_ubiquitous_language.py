"""ubiquitous-language red suite — the rename's behavioral fence (TASK: ubiquitous-language).

Guards the 17-row slang→domain map frozen in the task's §3 CONTRACT:
  - the rubric revs to v2 and carries the map (idiom rows in, renamed terms out of keep_list),
  - the slang is gone — BOTH written forms — from the EXTENDED surface (skill + templates +
    docs + diagrams/*.md + README + GETTING-STARTED), which the 19-file wording-lint never reaches,
  - the v17 enforced escapees (first feeder et al.) are swept from those newly covered surfaces,
  - every renamed concept keeps a glossary bridge to its former name + machine token,
  - add.py's emitted prose (sync-guidelines block, help text, hints) speaks domain terms,
  - machine tokens (CLI verbs · reject codes · skill file names) are byte-unchanged.

Bridge exemption: glossary lines carrying `formerly "` may mention a legacy term — they ARE the
bridge. A build that smuggles slang behind that marker is caught by the human verify read, not here.

RED before build by design; a permanent regression guard after.
Run: python3 -m unittest test_ubiquitous_language -v
"""

import ast
import re
import unittest
from pathlib import Path

TOOLING = Path(__file__).resolve().parent          # add-method/tooling
PKG = TOOLING.parent                               # add-method
RUBRIC = TOOLING / "WORDING_RUBRIC.md"
ADD_PY = TOOLING / "add.py"

# The frozen §3 map — slug · ban regex (both written forms) · v1 keep_list entry to retire (or None)
# · idiom_map row key · replacement that must enter keep_list (None = off-lint-surface, this test
# is its only fence) · required glossary-bridge machine token (or None).
TERMS = [
    dict(slug="one-approval-front", ban=r"\b(one[- ]approval|approval|the|whole|task's) front\b",
         old_keep="one-approval front", idiom="one-approval front", keep="specification bundle", token=None),
    # (?!-audit): `seam-audit` is a Group C machine token — CI job/workflow name,
    # pinned by test_audit_ci + test_release_1_4_0 (contract machine-layer rule).
    # (?!\.md\b): "SEAMS.md" is the shipped cross-cutting-convention-citation file
    # (unrelated new concept, task seams-doc/milestone seams). (?!\s+consulted\b):
    # "Seams consulted:" is that file's citation field label (TASK.md.tmpl, task
    # seams-template-wiring). Neither is the retired "seam = decision point" idiom.
    dict(slug="seam", ban=r"\bseams?\b(?!-audit)(?!\.md\b)(?!\s+consulted\b)",
         old_keep="seam", idiom="seam", keep="decision point", token=None),
    dict(slug="fold", ban=r"\bfold(s|ed|ing)?\b",
         old_keep="fold", idiom="fold", keep="retrospective consolidation", token="add.py deltas"),
    dict(slug="competency-delta", ban=r"\bcompetency deltas?\b",
         old_keep="competency delta", idiom="competency delta", keep="lesson learned", token=None),
    dict(slug="least-sure", ban=r"\bleast[- ]sure\b",
         old_keep="least-sure", idiom="least-sure", keep="lowest-confidence", token=None),
    dict(slug="touch-boundary", ban=r"\btouch[- ]boundar(y|ies)\b",
         old_keep="touch-boundary", idiom="touch-boundary", keep="change scope", token=None),
    dict(slug="survivor", ban=r"\bsurvivors?\b",
         old_keep="survivor", idiom="survivor", keep="living documentation", token=None),
    dict(slug="altitude", ban=r"\baltitudes?\b",
         old_keep="intake altitude", idiom="altitude", keep="scope level", token=None),
    dict(slug="lock-down", ban=r"\block[- ]downs?\b",
         old_keep=None, idiom="lock-down", keep="baseline approval", token="add.py lock"),
    dict(slug="blind-spot", ban=r"\bblind[- ]?spots?\b",
         old_keep=None, idiom="blind-spot", keep="non-functional review", token=None),
    dict(slug="safety-net", ban=r"\bsafety[- ]nets?\b",
         old_keep=None, idiom="safety net", keep="failing-first suite", token=None),
    dict(slug="evidence-auto-gate", ban=r"\bevidence auto[- ]gate\b",
         old_keep="evidence auto-gate", idiom="evidence auto-gate", keep="automated quality gate", token=None),
    dict(slug="autonomy-dial", ban=r"\bdial(s|ed|ing)?\b",
         old_keep="autonomy dial", idiom="autonomy dial", keep="autonomy level", token=None),
    dict(slug="trust-layer", ban=r"\btrust layer\b",
         old_keep="trust layer", idiom="trust layer", keep="method rationale", token=None),
    dict(slug="spine", ban=r"\bspines?\b",
         old_keep=None, idiom="forward spine", keep=None, token=None),   # "primary flow" lives off the lint surface
    dict(slug="on-ramp", ban=r"\bon[- ]?ramps?\b",
         old_keep=None, idiom="on-ramp", keep="onboarding", token=None),
    dict(slug="surfaces", ban=r"\b(state|story) surface\b",
         old_keep=None, idiom="state surface", keep=None, token=None),   # "working state"/"audit trail" off the lint surface
]

# v17 idioms already [enforced] on the 19-file lint surface but never checked beyond it.
ESCAPEES = {
    "first feeder": r"\bfirst feeder\b",
    "rubber-stamp": r"\brubber[- ]stamp(s|ed|ing)?\b",
    "blast radius": r"\bblast[- ]radius\b",
    "wall of": r"\bwall of\b",
    "collapses to": r"\bcollapses? to\b",
}

BRIDGE_MARKER = 'formerly "'
BRIDGE_FILES = [PKG / "docs" / "appendix-c-glossary.md",
                PKG / "tooling" / "templates" / "GLOSSARY.md.tmpl"]


def extended_surface():
    """Every prose file the §3 CHANGE SCOPE covers (canonical only — parity guards the mirrors)."""
    files = sorted((PKG / "skill" / "add").rglob("*.md"))
    files += sorted((PKG / "tooling" / "templates").glob("*.tmpl"))
    files += sorted((PKG / "docs").glob("*.md"))
    files += sorted((PKG / "diagrams").glob("*.md"))
    files += [PKG / "README.md", PKG / "GETTING-STARTED.md"]
    return [f for f in files if f.exists()]


MACHINE_HEADINGS = ("### Competency deltas",)  # engine-parsed TASK.md format keys (add.py _DELTA block
# locator + 46 historical task files) — Group C machine tokens per the frozen §3 contract; prose-only ban.


def scan(regex, files):
    """All (file, lineno, line) PROSE hits for regex. Machine-layer text is exempt per the frozen
    contract's Group C rule: glossary bridge lines, machine-format headings, fenced code blocks
    (state diagrams, yml workflows, delta grammar) and inline code spans (`folded`, `fold.md`,
    `seam`, …) keep their names — the ban polices prose only. The human verify read is the
    backstop against slang smuggled into a code span/fence (disclosed in §3)."""
    pat = re.compile(regex, re.IGNORECASE)
    hits = []
    for f in files:
        in_fence = False
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence or BRIDGE_MARKER in line or line.strip() in MACHINE_HEADINGS:
                continue
            if pat.search(re.sub(r"`[^`]+`", "", line)):
                hits.append(f"{f.relative_to(PKG.parent)}:{n}: {line.strip()[:100]}")
    return hits


def rubric_section(name):
    text = RUBRIC.read_text(encoding="utf-8")
    m = re.search(rf"^## {re.escape(name)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


class RubricV2Test(unittest.TestCase):
    """CR-R landed: the map is in idiom_map, the renamed terms left keep_list, replacements entered."""

    def test_rubric_v2_carries_the_map(self):
        idioms = rubric_section("idiom_map")
        keeps = rubric_section("keep_list")
        for t in TERMS:
            with self.subTest(term=t["slug"]):
                self.assertIn(t["idiom"], idioms,
                              f"idiom_map is missing the '{t['idiom']}' retirement row (CR-R not landed)")
                if t["old_keep"]:
                    self.assertNotIn(f"\n- {t['old_keep']}\n", keeps + "\n",
                                     f"keep_list still guards the retired term '{t['old_keep']}'")
                if t["keep"]:
                    self.assertIn(t["keep"], keeps,
                                  f"keep_list does not yet guard the replacement '{t['keep']}'")


class ExtendedSurfaceTest(unittest.TestCase):
    """The rename is real: zero slang hits — both written forms — beyond the lint's 19 files too."""

    def test_slang_absent_extended_surface(self):
        files = extended_surface()
        for t in TERMS:
            with self.subTest(term=t["slug"]):
                hits = scan(t["ban"], files)
                self.assertEqual([], hits,
                                 f"'{t['slug']}' still on the surface ({len(hits)} hits):\n  "
                                 + "\n  ".join(hits[:8]))

    def test_enforced_escapees_swept(self):
        files = extended_surface()
        for name, ban in ESCAPEES.items():
            with self.subTest(idiom=name):
                hits = scan(ban, files)
                self.assertEqual([], hits,
                                 f"v17-enforced idiom '{name}' survives off the lint surface:\n  "
                                 + "\n  ".join(hits[:8]))


class GlossaryBridgeTest(unittest.TestCase):
    """Every renamed concept stays findable from its old name and its machine token."""

    def test_glossary_bridge_complete(self):
        for bf in BRIDGE_FILES:
            self.assertTrue(bf.exists(), f"bridge file missing: {bf}")
        text = "\n".join(bf.read_text(encoding="utf-8") for bf in BRIDGE_FILES)
        for t in TERMS:
            with self.subTest(term=t["slug"]):
                new_name = (t["keep"] or t["slug"].replace("-", " "))
                self.assertIn(BRIDGE_MARKER, text, "no bridge entries exist yet")
                self.assertTrue(re.search(re.escape(new_name), text, re.I),
                                f"bridge lacks the new term '{new_name}'")
                if t["token"]:
                    self.assertIn(t["token"], text,
                                  f"bridge for '{new_name}' lacks its machine token '{t['token']}'")


class AddPyProseTest(unittest.TestCase):
    """CR-2 landed: the prose add.py emits (guideline block · help · hints) speaks domain terms."""

    # Group C machine literals (frozen §3 machine-layer rule — state keys / enum values /
    # grammar patterns keep their names, bridged in the glossary):
    MACHINE_CONSTANTS = {"seam", "folded", "fold"}   # --json owner enum + decide key · delta status · `add.py fold` subcommand (v3)
    MACHINE_SPANS = (                           # machine-token fragments inside longer strings
        "###\\s*Competency deltas",             # the _DELTA block locator pattern (x2)
        "### Competency deltas",                # docstrings quoting the machine heading
        "(human|seam|ai)",                      # the owner-enum listing in cmd docs
        "(open|folded|rejected)",               # the delta-status grammar in _DELTA_RE
        "folded/rejected",                      # docstring reference to the status pair
        "Least-sure flag surfaced at freeze",   # the §3 lowest-confidence-flag label (_FLAG_LABEL_RE)
        "[folded foundation-version",           # the fold stamp grammar (_foundation_tail counts it)
    )

    def test_sync_guidelines_domain_clean(self):
        tree = ast.parse(ADD_PY.read_text(encoding="utf-8"))
        strings = [n.value for n in ast.walk(tree)
                   if isinstance(n, ast.Constant) and isinstance(n.value, str)
                   and n.value not in self.MACHINE_CONSTANTS]
        prose = "\n".join(strings)
        for span in self.MACHINE_SPANS:
            prose = prose.replace(span, " ")
        bans = {t["slug"]: t["ban"] for t in TERMS} | ESCAPEES
        offending = {slug: re.findall(ban, prose, re.IGNORECASE)[:3]
                     for slug, ban in bans.items() if re.search(ban, prose, re.IGNORECASE)}
        self.assertEqual({}, offending,
                         f"add.py string literals still carry slang: {offending}")


class MachineTokensTest(unittest.TestCase):
    """GREEN-now standing guard: the machine layer never renames (the glossary bridges instead)."""

    def test_machine_tokens_unchanged(self):
        src = ADD_PY.read_text(encoding="utf-8")
        for verb in ("init", "lock", "new-task", "new-milestone", "advance", "gate",
                     "status", "guide", "deltas", "audit", "sync-guidelines"):
            self.assertRegex(src, rf"add_parser\(\s*['\"]{re.escape(verb)}['\"]",
                             f"CLI verb '{verb}' renamed or removed — machine_token_renamed")
        skill = PKG / "skill" / "add"
        for fname in ("SKILL.md", "intake.md", "run.md", "scope.md", "fold.md", "deltas.md",
                      "streams.md", "adopt.md", "setup-review.md", "report-template.md"):
            self.assertTrue((skill / fname).exists(),
                            f"skill file '{fname}' renamed/removed — machine_token_renamed")
        for fname, code in (("intake.md", "ask_human"), ("fold.md", "unconfirmed_fold"),
                            ("run.md", "unguarded_high_risk_auto")):
            self.assertIn(code, (skill / fname).read_text(encoding="utf-8"),
                          f"reject code '{code}' missing from {fname} — machine_token_renamed")


if __name__ == "__main__":
    unittest.main()
