#!/usr/bin/env python3
"""seed-method-personas: `add.py init`/`migrate` seed the three METHOD-LENS planner
personas (task-planner · milestone-planner · release-planner) into `.add/personas/`.

Why these three and not a roster of presets: 12 preset personas shipped for months
with no consumer and were retired. The line that keeps this from repeating is written
into persona-author/references/contract.md — ship a persona ONLY if it reasons about
ADD's own artifacts (PLAN.md sections, the frozen contract, the milestone DAG, the
release cut), never about a project domain (security, data, UX).

The load proof (S3) is the point of the whole task: a seeded persona must be READ by a
surface, not merely present on disk. A presence-only assertion is exactly what let the
retired presets pass a green suite while being dead.

Run: cd add-method/tooling && python3 -m unittest test_seed_method_personas -v
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADD_PY = HERE / "add.py"
sys.path.insert(0, str(HERE))
from add_engine.constants import METHOD_PERSONAS  # noqa: E402

# the three skill trees that must all carry the shipping criterion
REPO = HERE.parent.parent
CONTRACT_TREES = (
    REPO / "add-method/skill/add/persona-author/references/contract.md",
    REPO / ".claude/skills/add/persona-author/references/contract.md",
    REPO / "add-method/src/add_method/_bundled/skill/add/persona-author/references/contract.md",
)


def _run(cwd, *args):
    return subprocess.run([sys.executable, str(ADD_PY), *args], cwd=cwd,
                          capture_output=True, text=True, timeout=120)


class _Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        r = _run(self.root, "init", "--name", "smp", "--stage", "mvp")
        assert r.returncode == 0, r.stderr + r.stdout
        self.personas = Path(self.root) / ".add" / "personas"

    def tearDown(self):
        self._tmp.cleanup()


class InitSeeds(_Base):
    def test_init_seeds_the_three_method_personas(self):
        # M1: a fresh init lands exactly the three method lenses, each non-empty
        got = sorted(p.stem for p in self.personas.glob("*.md"))
        self.assertEqual(got, sorted(METHOD_PERSONAS),
                         f"init must seed exactly the method personas, got {got}")
        for slug in METHOD_PERSONAS:
            body = (self.personas / f"{slug}.md").read_text()
            self.assertTrue(body.strip(), f"{slug} seeded blank")
            # presence-based schema: the required sections the engine validates
            for section in ("## Identity", "## Critical Rules",
                            "## Default Requirement", "## Success Metrics"):
                self.assertIn(section, body, f"{slug} missing {section}")

    def test_seeded_personas_are_schema_clean(self):
        # M1 (cont): `check` must report no failure and no persona-quality WARN
        r = _run(self.root, "check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for slug in METHOD_PERSONAS:
            for line in (r.stdout + r.stderr).splitlines():
                if line.startswith("WARN") and slug in line:
                    self.fail(f"seeded persona raised a quality WARN: {line}")


class RosterLoadsThem(_Base):
    def test_seeded_personas_appear_in_the_status_roster(self):
        # M3 — THE LOAD PROOF. Not "the file exists" but "a surface reads it".
        # `status --all` prints `slug[flow] — vibe` per persona; a seed that never
        # reaches this line is dead weight, which is how the 12 presets survived.
        r = _run(self.root, "status", "--all")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout
        for slug in METHOD_PERSONAS:
            self.assertIn(slug, out, f"{slug} absent from the status --all roster")
            # the roster prints slug[flow] — a bare mention elsewhere is not proof
            self.assertRegex(out, rf"{slug} \[[a-z, ]+\] — \S",
                             f"{slug} present but not rendered as a roster entry")

    def test_unseeded_nudge_is_gone(self):
        # M3 (cont): the "personas: unseeded" nudge must not fire on a seeded project
        r = _run(self.root, "status", "--all")
        self.assertNotIn("unseeded", r.stdout,
                         "a seeded project must not still report an unseeded roster")


class NeverClobbers(_Base):
    SENTINEL = "## Identity\nUSER EDITED — do not overwrite.\n"

    def test_seeding_never_clobbers_an_edited_persona(self):
        # M4: the _seed_spec_file survivor idiom — an existing file is returned as-is
        target = self.personas / f"{METHOD_PERSONAS[0]}.md"
        target.write_text(self.SENTINEL)
        before = target.read_bytes()

        r = _run(self.root, "init", "--name", "smp", "--stage", "mvp", "--force")
        self.assertEqual(r.returncode, 0, r.stderr)   # --force must SUCCEED, or this case proves nothing
        self.assertEqual(target.read_bytes(), before,
                         "re-init clobbered a user-edited persona")

        r = _run(self.root, "migrate")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(target.read_bytes(), before,
                         "migrate clobbered a user-edited persona")

    def test_deleted_persona_is_restored_but_survivors_are_not_touched(self):
        # M4 (cont): seeding is additive — it fills gaps, it does not rewrite
        keep = self.personas / f"{METHOD_PERSONAS[1]}.md"
        keep.write_text(self.SENTINEL)
        keep_bytes = keep.read_bytes()
        (self.personas / f"{METHOD_PERSONAS[0]}.md").unlink()

        r = _run(self.root, "migrate")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertTrue((self.personas / f"{METHOD_PERSONAS[0]}.md").exists(),
                        "migrate did not restore the missing method persona")
        self.assertEqual(keep.read_bytes(), keep_bytes,
                         "migrate rewrote a persona that was already present")


class MigrateRetrofits(_Base):
    def test_migrate_retrofits_method_personas(self):
        # M2: an existing (pre-seeding) project gets the three on migrate — the
        # same twin-call precedent _seed_spec_file already sets for the 5-DD specs
        for p in self.personas.glob("*.md"):
            p.unlink()
        self.assertEqual(list(self.personas.glob("*.md")), [])

        r = _run(self.root, "migrate")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        got = sorted(p.stem for p in self.personas.glob("*.md"))
        self.assertEqual(got, sorted(METHOD_PERSONAS),
                         f"migrate must retrofit the method personas, got {got}")


class BlankTemplateIsSkipped(_Base):
    def test_blank_template_is_skipped_not_seeded_empty(self):
        # R:seed_skipped_blank — the _seed_spec_file circuit breaker. A stale or
        # blank template must never produce a 0-content survivor that then reads as
        # an authoritative-but-empty persona.
        tmpl_dir = HERE / "templates" / "personas"
        slug = METHOD_PERSONAS[0]
        src = tmpl_dir / f"{slug}.md.tmpl"
        original = src.read_text()
        (self.personas / f"{slug}.md").unlink()
        try:
            src.write_text("   \n")
            r = _run(self.root, "migrate")
            dest = self.personas / f"{slug}.md"
            self.assertFalse(dest.exists() and not dest.read_text().strip(),
                             "a blank template produced a 0-content persona survivor")
            self.assertIn("missing/blank", r.stderr + r.stdout,
                          "a skipped blank seed must warn, not fail silently")
        finally:
            src.write_text(original)


class ShippingCriterionIsDocumented(unittest.TestCase):
    def test_shipping_criterion_documented(self):
        # R:not_a_method_lens — the rule that stops this becoming preset-shipping
        # again must exist in every skill tree, or the boundary is folklore.
        for tree in CONTRACT_TREES:
            self.assertTrue(tree.exists(), f"missing contract tree: {tree}")
            body = tree.read_text()
            self.assertIn("method lens", body.lower(),
                          f"{tree} does not document the method-lens criterion")
            self.assertIn("domain", body.lower(),
                          f"{tree} does not name the domain-lens exclusion")


if __name__ == "__main__":
    unittest.main()
