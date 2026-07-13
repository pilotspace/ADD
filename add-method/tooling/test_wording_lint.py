"""test_wording_lint.py — the v17 wording-rubric red→green suite.

Pins the frozen contract in .add/tasks/wording-rubric/TASK.md §3: `wording-lint` is a
DETERMINISTIC regression FENCE, never a metric. It may fail only on a literal regression
(an enforced banned phrase / a banned emphasis token reappears, or a keep-list term
vanishes) — never on a good rewrite. A count/density/threshold check is refused by design
(`metric_gate`) because it would false-positive on a good rewrite — the same failure mode
that disqualified v17's behavioral eval as a gate.

One test per §2 scenario. Fixtures are temp files; surface tests read the canonical
add-method/skill/add tree (the _bundled & .claude mirrors are byte-identical via
test_bundle_parity/test_tree_parity, so checking canonical suffices).

Run: python3 -m unittest test_wording_lint -v
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import wording_lint as wl

_TOOLING = Path(__file__).resolve().parent


def _write(dir_path: Path, name: str, body: str) -> Path:
    p = dir_path / name
    p.write_text(body, encoding="utf-8")
    return p


# A minimal, self-consistent rubric used by machinery tests (kept off the real surface).
_MINI_RUBRIC = """# WORDING_RUBRIC — fixture

## idiom_map
- rubber-stamp -> approve without reading [mapped]
- wall of -> flat list of [mapped]

## enforced_banned
- (none)

## keep_list
- one-approval front
- fold
- HARD-STOP

## negative_keep_list
- never auto-pass a security finding # why: safety boundary

## emphasis_tokens
- CRITICAL
- NON-NEGOTIABLE
"""


class TestRubricLoad(unittest.TestCase):
    def test_lint_loads_from_rubric_single_source(self) -> None:
        """§2: the lint reads its lists FROM the rubric doc (no hardcoded duplicate)."""
        with tempfile.TemporaryDirectory() as d:
            rp = _write(Path(d), "WORDING_RUBRIC.md",
                        _MINI_RUBRIC.replace("- one-approval front", "- sentinel-term-xyz"))
            rubric = wl.load_rubric(rp)
            # the parsed keep-list reflects THIS file's content, not a baked-in constant
            self.assertIn("sentinel-term-xyz", rubric.keep_terms)
            self.assertNotIn("one-approval front", rubric.keep_terms)
            self.assertEqual(set(rubric.emphasis_tokens), {"CRITICAL", "NON-NEGOTIABLE"})

    def test_main_prints_rubric_path(self) -> None:
        """§2: the lint reports the rubric path it read."""
        with tempfile.TemporaryDirectory() as d:
            rp = _write(Path(d), "WORDING_RUBRIC.md", _MINI_RUBRIC)
            clean = _write(Path(d), "clean.md", "a plain sentence with no idiom.\n")
            rc, out = wl.run(["--rubric", str(rp), "--surface", str(clean)])
            self.assertEqual(rc, 0)
            self.assertIn(str(rp), out)


class TestFences(unittest.TestCase):
    def test_lint_flags_enforced_idiom_fixture(self) -> None:
        """§2: an enforced banned phrase in a fixture -> banned_idiom_present, exit 1."""
        rubric = wl.Rubric(enforced_banned=["rubber-stamp"], keep_terms=[], emphasis_tokens=[])
        found = wl.lint_text("we rubber-stamp the batch.", rubric, source="x.md")
        self.assertEqual([f.code for f in found], ["banned_idiom_present"])
        self.assertIn("rubber-stamp", found[0].phrase)

    def test_enforced_idiom_catches_inflection(self) -> None:
        """A retired idiom must not creep back inflected ('rubber-stamped')."""
        rubric = wl.Rubric(enforced_banned=["rubber-stamp"], keep_terms=[], emphasis_tokens=[])
        found = wl.lint_text("that gets rubber-stamped fast.", rubric, source="x.md")
        self.assertEqual([f.code for f in found], ["banned_idiom_present"])

    def test_lint_no_falsepositive_substring_and_rewrite(self) -> None:
        """§2: substrings ('firewall office' ⊃ 'wall of') and clean rewrites never fire."""
        rubric = wl.Rubric(enforced_banned=["wall of"], keep_terms=["fold"], emphasis_tokens=[])
        clean = "the firewall office unfolded within; approve without reading."
        self.assertEqual(wl.lint_text(clean, rubric, source="x.md"), [])
        hit = wl.lint_text("a wall of text", rubric, source="x.md")
        self.assertEqual([f.code for f in hit], ["banned_idiom_present"])

    def test_emphasis_token_fence(self) -> None:
        """§2: a banned emphasis token fires; the live surface is clean (green now)."""
        rubric = wl.Rubric(enforced_banned=[], keep_terms=[], emphasis_tokens=["CRITICAL", "NON-NEGOTIABLE"])
        hit = wl.lint_text("this is CRITICAL: do it.", rubric, source="x.md")
        self.assertEqual([f.code for f in hit], ["banned_emphasis_token"])
        live = wl.lint_surface(wl.load_rubric(), wl.surface_files())
        self.assertEqual([f for f in live if f.code == "banned_emphasis_token"], [])

    def test_keep_term_presence(self) -> None:
        """§2: a keep term present on the live surface passes; missing one -> keep_term_missing."""
        live = wl.lint_surface(wl.load_rubric(), wl.surface_files())
        self.assertEqual([f for f in live if f.code == "keep_term_missing"], [])
        rubric = wl.Rubric(enforced_banned=[], keep_terms=["totally-absent-term-qq"], emphasis_tokens=[])
        with tempfile.TemporaryDirectory() as d:
            f = _write(Path(d), "a.md", "nothing relevant here.\n")
            miss = wl.lint_surface(rubric, [f])
            self.assertEqual([x.code for x in miss], ["keep_term_missing"])


class TestRubricValidation(unittest.TestCase):
    def test_self_collision_none_on_frozen_rubric(self) -> None:
        """§2: the REAL frozen rubric is self-consistent (no collision, no ambiguous ban)."""
        findings = wl.validate_rubric(wl.load_rubric())
        bad = [f for f in findings if f.code in ("rubric_self_collision", "ambiguous_ban")]
        self.assertEqual(bad, [], f"frozen rubric is not self-consistent: {bad}")

    def test_ambiguous_ban_refused(self) -> None:
        """§2: a single-word or substring-of-keep enforced entry -> ambiguous_ban."""
        single = wl.Rubric(enforced_banned=["thin"], keep_terms=[], emphasis_tokens=[])
        self.assertIn("ambiguous_ban", [f.code for f in wl.validate_rubric(single)])
        sub = wl.Rubric(enforced_banned=["one-approval"], keep_terms=["one-approval front"], emphasis_tokens=[])
        self.assertIn("ambiguous_ban", [f.code for f in wl.validate_rubric(sub)])

    def test_metric_check_refused(self) -> None:
        """§2: every lint check kind is a fence; 'metric' is refused by design."""
        self.assertTrue(wl.CHECK_KINDS, "the lint must expose its check kinds")
        self.assertTrue(all(k == "fence" for k in wl.CHECK_KINDS),
                        f"a non-fence check leaked in: {wl.CHECK_KINDS}")
        self.assertNotIn("metric", wl.CHECK_KINDS)


class TestDesignForFailure(unittest.TestCase):
    def test_load_missing_rubric_raises(self) -> None:
        """§2: a missing rubric fails LOUD (RubricError), never a silent green."""
        with self.assertRaises(wl.RubricError):
            wl.load_rubric(_TOOLING / "no_such_rubric_zzz.md")

    def test_main_broken_rubric_exits_2(self) -> None:
        """§2: the CLI exits 2 (not 0) on a missing/malformed rubric — no false green."""
        rc, out = wl.run(["--rubric", str(_TOOLING / "no_such_rubric_zzz.md")])
        self.assertEqual(rc, 2)
        with tempfile.TemporaryDirectory() as d:
            empty = _write(Path(d), "WORDING_RUBRIC.md", "# empty, no sections\n")
            rc2, _ = wl.run(["--rubric", str(empty), "--surface", str(empty)])
            self.assertEqual(rc2, 2)


class TestLiveSurfaceGreen(unittest.TestCase):
    def test_enforced_banned_green_over_live_surface(self) -> None:
        """§2: the enforced seed (already-absent) -> zero banned_idiom_present over the live surface.

        The FULL idiom-map green (every mapped idiom retired) is owned by clarity-greenstate,
        not here — this is only the already-absent enforced floor.
        """
        live = wl.lint_surface(wl.load_rubric(), wl.surface_files())
        self.assertEqual([f for f in live if f.code == "banned_idiom_present"], [])

    def test_surface_files_cover_the_contract(self) -> None:
        """The surface is skill/add (29 files: +loop.md @ v20, +graduate.md @ v22, +confidence.md +advisor.md @ advisor-context, +compact-foundation.md @ foundation-compaction, +soul.md @ soul-self-improve, +design.md @ udd-design-loop, +release.md @ release-altitude, +phases/fast-lane.md @ fast-lane, +components.md @ component-method-docs) + docs/appendix-b-prompts.md, per §3."""
        files = wl.surface_files()
        names = {p.name for p in files}
        self.assertIn("SKILL.md", names)
        self.assertIn("loop.md", names)
        self.assertIn("graduate.md", names)
        self.assertIn("confidence.md", names)
        self.assertIn("advisor.md", names)
        self.assertIn("compact-foundation.md", names)
        self.assertIn("soul.md", names)
        self.assertIn("design.md", names)
        self.assertIn("release.md", names)
        self.assertIn("fast-lane.md", names)
        self.assertIn("components.md", names)
        self.assertIn("sensitivity.md", names)
        self.assertIn("appendix-b-prompts.md", names)
        self.assertIn("self-improve.md", names)
        self.assertEqual(len(files), 31, f"expected 30 skill files + appendix-b, got {len(files)} "
                         "(guides-and-skill merged 0-ground.md + 3-contract.md into 3-plan.md, net -1)")


if __name__ == "__main__":
    unittest.main()
