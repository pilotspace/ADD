"""Red→green guard for release-guide §3 (FROZEN @ v1).

release.md (the 7-step RELEASE scope-level guide) byte-identical across the 3 skill homes, plus a
SKILL.md "Beyond the bundle" cross-ref. Engine UNCHANGED (convention-guided seam — the cut's
behaviour is the sibling release-report / release-command tasks').

unittest (repo convention). RED before build: release.md does not exist in the homes; the SKILL
cross-ref is absent; the wording-lint surface count is still 27.
"""
import hashlib
import os
import re
import sys
import unittest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
_TOOLING = os.path.join(_ROOT, "add-method", "tooling")
if _TOOLING not in sys.path:
    sys.path.insert(0, _TOOLING)

_GUIDE_HOMES = [
    "add-method/skill/add/release.md",
    "add-method/src/add_method/_bundled/skill/add/release.md",
    ".claude/skills/add/release.md",
]
_SKILL_HOMES = [
    "add-method/skill/add/SKILL.md",
    "add-method/src/add_method/_bundled/skill/add/SKILL.md",
    ".claude/skills/add/SKILL.md",
]
_ENGINES = [
    "add-method/tooling/add.py",
    ".add/tooling/add.py",
    "add-method/src/add_method/_bundled/tooling/add.py",
]
_FLOOR_CODES = ["release_security_open", "release_tests_red",
                "release_no_closed_milestone", "release_undisclosed_waiver"]
_FLOW_ARC = "cue → gather → draft notes → readiness floor → human confirms → cut → watch"
_EXPECTED_SURFACE_COUNT = 28   # 27 today + release.md (the inventory bump this task registers)


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def _exists(rel):
    return os.path.exists(os.path.join(_ROOT, rel))


def _norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


class ReleaseGuideTest(unittest.TestCase):
    def _guide(self):
        if not _exists(_GUIDE_HOMES[0]):
            self.fail("release.md missing — build has not run (expected RED pre-build)")
        return _norm(_read(_GUIDE_HOMES[0]))

    # ── deliverable + parity ──────────────────────────────────────────────────────────────────
    def test_guide_exists_3_homes(self):
        for home in _GUIDE_HOMES:
            self.assertTrue(_exists(home), f"release.md missing at {home}")

    def test_guide_mirror_parity(self):
        if not all(_exists(h) for h in _GUIDE_HOMES):
            self.fail("release.md missing in a home (expected RED pre-build)")
        d = {h: hashlib.md5(_read(h).encode("utf-8")).hexdigest() for h in _GUIDE_HOMES}
        self.assertEqual(len(set(d.values())), 1, f"release.md homes diverged (mirror-drift): {d}")

    # ── the flow + the cue ────────────────────────────────────────────────────────────────────
    def test_flow_7_steps(self):
        t = self._guide()
        self.assertIn(_FLOW_ARC.lower(), t, "the 7-step flow arc is missing or out of order")

    def test_cue_named(self):
        t = self._guide()
        self.assertIn("releasable", t, "the `→ releasable` cue is not named")
        self.assertIn("tally", t, "the cue must be described as a tally (never a judgment)")

    # ── the floor ─────────────────────────────────────────────────────────────────────────────
    def test_floor_4_codes_security_unforceable(self):
        t = self._guide()
        for code in _FLOOR_CODES:
            self.assertIn(code, t, f"floor reject code missing: {code}")
        self.assertIn("does not override", t,
                      "security must be the un-forceable reject (--force does not override release_security_open)")

    # ── the invariants (decision-set) ─────────────────────────────────────────────────────────
    def test_engine_records_human_ships(self):
        t = self._guide()
        self.assertIn("never tags, publishes, or deploys", t,
                      "the guide must state the engine never tags/publishes/deploys")
        for rec in ("changelog", "releases.md", "attribution"):
            self.assertIn(rec, t, f"the engine-records claim must name: {rec}")

    def test_after_fold_bundles(self):
        t = self._guide()
        self.assertIn("fold.md", t, "the after-fold order must reference fold.md")
        self.assertIn("milestone-done → fold → compact → archive", t, "the lifecycle order is missing")
        self.assertIn("orthogonal", t, "release must be stated orthogonal to stage")
        self.assertTrue(re.search(r"bundle", t), "release must be stated to bundle ≥1 milestone")

    # ── the SKILL cross-ref ───────────────────────────────────────────────────────────────────
    def test_skill_cross_ref_3_homes(self):
        for home in _SKILL_HOMES:
            t = _norm(_read(home))
            self.assertIn("release.md", t, f"{home}: no Beyond-the-bundle cross-ref to release.md")
            self.assertIn("graduate.md", t, f"{home}: the graduation cross-ref should remain (release follows graduation)")
        digests = {h: hashlib.md5(_read(h).encode("utf-8")).hexdigest() for h in _SKILL_HOMES}
        self.assertEqual(len(set(digests.values())), 1, f"SKILL.md homes diverged (mirror-drift): {digests}")

    # ── the inventory bump ────────────────────────────────────────────────────────────────────
    def test_surface_count_28(self):
        import wording_lint as wl
        self.assertEqual(len(wl.surface_files()), _EXPECTED_SURFACE_COUNT,
                         "release.md must be registered on the wording-lint surface (27 → 28)")

    # ── wording-clean ─────────────────────────────────────────────────────────────────────────
    def test_wording_clean(self):
        if not _exists(_GUIDE_HOMES[0]):
            self.fail("release.md missing (expected RED pre-build)")
        import wording_lint as wl
        findings = wl.lint_text(_read(_GUIDE_HOMES[0]), wl.load_rubric(), source=_GUIDE_HOMES[0])
        self.assertEqual(findings, [], f"release.md prose has banned idioms (wording-regression): {findings}")

    # ── convention-guided seam ────────────────────────────────────────────────────────────────
    def test_no_engine_creep(self):
        # the engine never references the guide FILE (release.md) — guides are agent-facing, not
        # engine-parsed. (The `release` command itself is a sibling task and may land later; it
        # never references the guide file, so this guard survives that.)
        for eng in _ENGINES:
            if not _exists(eng):
                continue
            self.assertNotIn("release.md", _read(eng),
                             f"{eng}: engine references the guide file — convention-guided seam broken (engine-creep)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
