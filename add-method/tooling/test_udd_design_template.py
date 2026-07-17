"""Red suite for udd-design-template (udd-design-foundation 3/4).

Frozen contract §3 @ v1: a DESIGN.md template wired into 0-setup.
  - ENGINE: SETUP_FILES gains "DESIGN.md" (appended) so `add.py init` renders
    templates/DESIGN.md.tmpl → .add/DESIGN.md via the generic render+write loop.
  - TEMPLATE: a STRUCTURED BINDING doc — SIX required sections (header · Identity ·
    Principles · Screens · Foundation · Render), {{project}}/{{stage}}/{{date}}
    substituted, rendering NON-BLANK. Identity PROMPTS (HTML-comment), never
    pre-fills a concrete value. Foundation points to the named-set SAMPLES; Screens
    indexes prototypes/<name>.json (seeded with prototype.sample.json); Render points
    to udd-catalog.md's recipe.
  - PROSE: phases/direction.md names DESIGN.md as a living doc to draft.
  - PARITY: DESIGN.md.tmpl canonical↔bundle (+ dogfood copy); 0-setup.md ×3.

Five named reds (the DESIGN.md guards; udd-check-lint does NOT lint this prose):
    design_not_wired · design_template_blank · identity_prefilled ·
    design_section_missing · mirror_drift

These run RED before build: _render_template("DESIGN.md", …) returns "" (the
template is not shipped yet), "DESIGN.md" ∉ SETUP_FILES, 0-setup.md lacks the line,
the DESIGN.md.tmpl mirrors are missing, and the pin is not yet re-aimed.
"""
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import add

_TOOLING = Path(__file__).resolve().parent
_ADD_METHOD = _TOOLING.parent
_REPO = _ADD_METHOD.parent
_BUNDLE_TOOLING = _ADD_METHOD / "src" / "add_method" / "_bundled" / "tooling"
_DOGFOOD_TOOLING = _REPO / ".add" / "tooling"

_CANON_SKILL = _ADD_METHOD / "skill" / "add"
_BUNDLE_SKILL = _ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add"
_DOGFOOD_SKILL = _REPO / ".claude" / "skills" / "add"

# the H2 anchors the contract pins (header is detected separately via the self-note)
_H2_ANCHORS = ("## Identity", "## Principles", "## Screens", "## Foundation", "## Render")


def _render():
    """Render the (not-yet-shipped) canonical DESIGN.md template — "" until build."""
    return add._render_template("DESIGN.md", date="2026-01-01", project="Demo", stage="mvp")


def _section(doc, heading):
    """The '## <heading>…' block up to the next '## ' (or EOF). '' if absent."""
    out, capturing = [], False
    for ln in doc.splitlines():
        if ln.startswith("## "):
            if capturing:
                break
            capturing = ln[3:].strip().lower().startswith(heading.lower())
            if capturing:
                out.append(ln)
                continue
        elif capturing:
            out.append(ln)
    return "\n".join(out)


class DesignTemplateSectionTest(unittest.TestCase):
    # --- the template renders, non-blank, with substitutions resolved ----
    def test_template_renders_nonblank_substituted(self):
        """design_template_blank: the template must render non-blank, no raw {{tokens}}."""
        doc = _render()
        self.assertTrue(doc.strip(), "DESIGN.md.tmpl must render non-blank")
        self.assertNotIn("{{", doc, "every {{token}} must be substituted")
        for sub in ("Demo", "mvp", "2026-01-01"):
            self.assertIn(sub, doc, f"the header must carry the substituted {sub!r}")

    def test_all_required_sections_present(self):
        """design_section_missing: header self-note + the five H2 anchors, IN ORDER."""
        doc = _render()
        # the header self-note — and it must be VISIBLE prose, not buried in a comment
        self.assertRegex(doc, r"[Nn]o UI", "the header self-note ('no UI? optional — delete it')")
        visible = re.sub(r"<!--.*?-->", "", doc, flags=re.DOTALL)
        self.assertRegex(visible, r"[Nn]o UI", "the self-note must be visible prose, not inside a comment")
        # presence of the five H2 anchors
        for anchor in _H2_ANCHORS:
            self.assertIn(anchor, doc, f"missing required section: {anchor}")
        # contracted ORDER — header (self-note) precedes ## Identity, then anchors monotone
        positions = [doc.index(a) for a in _H2_ANCHORS]
        self.assertEqual(positions, sorted(positions),
                         "sections must appear in the contracted order: "
                         "Identity · Principles · Screens · Foundation · Render")
        self.assertLess(re.search(r"[Nn]o UI", doc).start(), positions[0],
                        "the header (carrying the self-note) must precede ## Identity")

    def test_identity_section_prompts_not_prefilled(self):
        """identity_prefilled — the contract's OR: NEITHER a #RRGGBB hex NOR a
        non-comment brand/type literal; every identity field is an HTML-comment prompt."""
        block = _section(_render(), "Identity")
        self.assertIn("<!--", block, "identity fields must be HTML-comment prompts")
        no_comments = re.sub(r"<!--.*?-->", "", block, flags=re.DOTALL)
        # half 1: no concrete brand hex outside a prompt
        self.assertNotRegex(no_comments, r"#[0-9A-Fa-f]{6}",
                            "a concrete brand hex outside a prompt = identity_prefilled")
        # half 2: every '- **field** — <value>' bullet's value must be a PROMPT (empty once
        # comments stripped) — a non-comment literal (e.g. a typeface name) is prefilled too
        for ln in no_comments.splitlines():
            self.assertNotRegex(
                ln, r"^-\s+\*\*.+?\*\*\s*[—:-]\s*\S",
                f"identity field carries a pre-filled literal, not a prompt: {ln!r}")

    def test_screens_section_indexes_prototypes(self):
        """The Screens section is a TABLE indexing prototypes by name, seeded with the sample row."""
        block = _section(_render(), "Screens")
        self.assertIn("prototypes/", block, "screens must point at prototypes/")
        # an actual table (a Prototype column) with the sample as a worked ROW — not a prose mention
        self.assertRegex(block, r"\|[^\n]*[Pp]rototype[^\n]*\|",
                         "screens must be a table with a Prototype column")
        self.assertRegex(block, r"\|[^\n]*prototype\.sample\.json[^\n]*\|",
                         "the shipped sample must seed a worked table row")

    def test_foundation_points_to_named_set_samples(self):
        """The Foundation section binds the named set + its docs + its shipped samples."""
        block = _section(_render(), "Foundation")
        for token in ("tokens.json", "catalog.json", "prototypes/",
                      "tokens.sample.json", "catalog.sample.json", "prototype.sample.json",
                      "udd-tokens.md", "udd-catalog.md"):
            self.assertIn(token, block, f"foundation must point to {token}")

    def test_render_section_points_to_recipe(self):
        """The Render section points to the udd-catalog.md render recipe."""
        block = _section(_render(), "Render")
        self.assertIn("udd-catalog.md", block, "render must point at the recipe doc")
        self.assertIn("Render recipe", block, "render must name the '## Render recipe' section")


class InitDraftsDesignTest(unittest.TestCase):
    def setUp(self):
        self._cwd = Path.cwd()
        self.tmp = tempfile.mkdtemp(prefix="add-design-")
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self._cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_design_is_a_setup_file(self):
        """design_not_wired: "DESIGN.md" must be registered in SETUP_FILES."""
        self.assertIn("DESIGN.md", add.SETUP_FILES)

    def test_init_drafts_nonblank_design(self):
        """The exit criterion: a fresh init drafts a non-blank .add/DESIGN.md."""
        add.main(["init", "--name", "Demo", "--stage", "mvp"])
        doc = Path(self.tmp) / ".add" / "DESIGN.md"
        self.assertTrue(doc.exists(), "init must draft .add/DESIGN.md")
        text = doc.read_text(encoding="utf-8")
        self.assertTrue(text.strip(), "the drafted DESIGN.md must be non-blank")
        self.assertNotIn("{{", text, "substitutions must be resolved on disk")
        self.assertIn("Demo", text)

    def test_other_setup_files_still_drafted(self):
        """Wiring DESIGN.md must not disturb the other survivor-layer files."""
        add.main(["init", "--name", "Demo", "--stage", "mvp"])
        root = Path(self.tmp) / ".add"
        for f in ("PROJECT.md", "CONVENTIONS.md", "GLOSSARY.md", "MODEL_REGISTRY.md"):
            self.assertTrue((root / f).exists(), f"{f} must still be drafted")


class SetupProseTest(unittest.TestCase):
    def test_0setup_names_design_md(self):
        """phases/direction.md names DESIGN.md as a living doc setup drafts."""
        text = (_CANON_SKILL / "phases" / "direction.md").read_text(encoding="utf-8")
        self.assertIn("DESIGN.md", text, "0-setup must name DESIGN.md as a doc to draft")


class DesignArtifactParityTest(unittest.TestCase):
    def test_design_template_mirrored(self):
        """mirror_drift: DESIGN.md.tmpl byte-identical canonical↔bundle (+ dogfood)."""
        rel = "templates/DESIGN.md.tmpl"
        canon = (_TOOLING / rel).read_bytes()
        self.assertEqual(canon, (_BUNDLE_TOOLING / rel).read_bytes(), f"{rel}: canonical ≠ bundled")
        self.assertEqual(canon, (_DOGFOOD_TOOLING / rel).read_bytes(), f"{rel}: canonical ≠ dogfood")

    def test_0setup_mirrored(self):
        """mirror_drift: phases/direction.md byte-identical across the ×3 skill mirrors."""
        rel = "phases/direction.md"
        canon = (_CANON_SKILL / rel).read_bytes()
        self.assertEqual(canon, (_BUNDLE_SKILL / rel).read_bytes(), f"{rel}: canonical ≠ bundled")
        self.assertEqual(canon, (_DOGFOOD_SKILL / rel).read_bytes(), f"{rel}: canonical ≠ dogfood")


if __name__ == "__main__":
    unittest.main()
