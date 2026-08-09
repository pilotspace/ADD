"""Red→green guard for gate-wiring §3 (FROZEN @ v1).

Each of the 8 human-gate guides points at report-template.md's "guided choice" convention beside its
existing ARC cue. Presentation-only — report-template.md (the frozen convention) is UNTOUCHED, and the
engine is byte-identical. Each guide stays byte-identical across the 3 skill homes.

RED before build: the 8 guides carry no "guided choice" cue, and MILESTONE.md EC2 still names a phantom
"human-gated-advance" guide. Maps to TASK.md M1–M5 + the 3 reject codes.
"""
import hashlib
import os
import re
import unittest

# tests → gate-wiring → tasks → .add → repo root
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

_HOME_DIRS = [
    "add-method/skill/add",
    "add-method/src/add_method/_bundled/skill/add",
    ".claude/skills/add",
]
_CANONICAL = _HOME_DIRS[0]

# The 8 human-gate guides (the frozen coverage set), relative to a skill home.
_GUIDES = [
    "phases/0-setup.md", "phases/3-contract.md", "phases/6-verify.md",
    "intake.md", "scope.md", "loop.md", "graduate.md", "release.md",
]

# The full closed v16 vocab — these 8 guides mix phase guides ({prompt, output_format, exit_gate})
# with on-demand guides that also carry the engine-doc tags ({constraints, reject_codes}).
_CLOSED_TAGS = {"prompt", "exit_gate", "constraints", "reject_codes", "output_format"}
_CUE = "guided choice"
_MILESTONE = ".add/milestones/decision-suggestions/MILESTONE.md"


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


class GateWiring(unittest.TestCase):
    # ── M1 / C1+C2: every gate guide carries the cue pointing at report-template.md (RED) ────────
    def test_each_guide_cued(self):
        missing = []
        for g in _GUIDES:
            text = _read(os.path.join(_CANONICAL, g))
            if _CUE not in text or "report-template" not in text:
                missing.append(g)
        self.assertEqual(missing, [], f"guide_uncued — guides without a '{_CUE}' cue: {missing}")

    # ── M4 / I2: no XML tag outside the closed phase-guide vocab ─────────────────────────────────
    # Match CLOSING tags only — real block tags are paired (`<prompt>…</prompt>`), while prose
    # placeholders (`<name>`, `<slug>`) are never closed, so this ignores the placeholder hazard.
    def test_no_new_tag(self):
        for g in _GUIDES:
            tags = set(re.findall(r"</([a-z_]+)>", _read(os.path.join(_CANONICAL, g))))
            offenders = tags - _CLOSED_TAGS
            self.assertEqual(offenders, set(), f"{g}: out-of-vocab tag(s) {sorted(offenders)}")

    # ── home_drift / I3: each guide byte-identical across the 3 homes ────────────────────────────
    def test_each_guide_homes_identical(self):
        for g in _GUIDES:
            digests = {d: hashlib.md5(_read(os.path.join(d, g)).encode("utf-8")).hexdigest()
                       for d in _HOME_DIRS}
            self.assertEqual(len(set(digests.values())), 1, f"home_drift — {g}: {digests}")

    # ── convention_touched / I1: report-template.md's frozen guided-choice section is unchanged ──
    def test_convention_untouched(self):
        text = _read(os.path.join(_CANONICAL, "report-template.md"))
        for tok in ("▶", "recommended pick", "guided choice"):
            self.assertIn(tok, text, f"frozen convention token missing/changed: {tok!r}")

    # ── M5 / I4: MILESTONE.md EC2 reconciled to the 8-guide set (no phantom advance guide) ───────
    def test_milestone_ec2_reconciled(self):
        text = _read(_MILESTONE)
        self.assertNotIn("human-gated-advance", text,
                         "EC2 still claims a phantom 'human-gated-advance' guide")


if __name__ == "__main__":
    unittest.main()
