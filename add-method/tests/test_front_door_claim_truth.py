"""The front door must not assert an advantage this repository's own evidence refutes.

`promised-capability-guard` bound the README to nouns the engine EXPOSES. It never asked whether a
MEASURED claim survived the measurement, and one did not:

  R:UNBACKEDCLAIM  Highlights told the reader a thin kernel and a short walk "keep ADD the cheap
                   option, not the heavyweight one". The repo's own revised benchmark reports the
                   opposite at equal trust — spec-kit $1.42–1.68 per milestone vs ADD $2.58–2.92,
                   ADD ~1.7–1.8× — and explicitly RETRACTS the earlier cheaper-per-milestone claim.
                   ADD's defensible cost win is against its own 1.x lineage, not against a rival.

Two quieter defects rode along: the shipped skill trees still declared `version: "3.1.0"` two minor
releases after 3.1 (the version-parity gate enumerated five sources and knew nothing of the skill),
and the cookbook line for `doctor` said it "never writes" without naming `--sync`, which does.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
# BOTH front doors, always. The retracted cost claim shipped on each in different words, and a
# guard that reads one of two landing pages leaves the refuted sentence on the page most visitors
# actually reach. `test_promised_capabilities` already enumerates both; so does this.
READMES = (PKG / "README.md", ROOT / "README.md")
README = PKG / "README.md"
BENCH = ROOT / "benchmark" / "results" / "2026-07-add-2.0-remeasure.md"
SKILL_TREES = (PKG / "skill" / "add",
               PKG / "src" / "add_method" / "_bundled" / "skill" / "add",
               ROOT / ".claude" / "skills" / "add")

sys.path.insert(0, str(PKG / "tooling"))
import cli  # noqa: E402


def _readme(path=None) -> str:
    return (path or README).read_text(encoding="utf-8")


def _highlights(path=None) -> str:
    """The Highlights section. The two front doors head it differently (`## Highlights` vs
    `## ✨ Highlights`), so match the HEADING TEXT rather than the literal line — a split on one
    spelling reads the other as having no Highlights at all."""
    lines = _readme(path).splitlines()
    start = next((i for i, l in enumerate(lines)
                  if l.startswith("#") and l.strip().lstrip("#").strip().lstrip("✨ ") == "Highlights"), None)
    assert start is not None, f"{path or README} has no Highlights heading"
    out = []
    for line in lines[start + 1:]:
        if line.startswith("#"):
            break
        out.append(line)
    return "\n".join(out)


def _engine_verb_count() -> int:
    sub = next(a for a in cli.build_parser()._actions
               if getattr(a, "choices", None) and isinstance(a.choices, dict))
    return len(sub.choices)


def _pkg_version() -> str:
    return json.loads((PKG / "package.json").read_text(encoding="utf-8"))["version"]


# --- M1/A1/R:UNBACKEDCLAIM ------------------------------------------------------------------

def test_no_front_door_claim_contradicts_the_benchmark():
    """covers: M1, A1, R:UNBACKEDCLAIM · the cost clause is absent."""
    assert BENCH.is_file(), "the cited benchmark report is missing — the claim cannot be checked"
    assert "retracted" in BENCH.read_text(encoding="utf-8").lower(), \
        "the report no longer carries the retraction this guard is anchored to"
    for path in READMES:
        _assert_no_cost_claim(path)


def _assert_no_cost_claim(path):
    flat = " ".join(_highlights(path).split())
    banned = re.compile(r"the cheap(?:er|est)? option|cheaper than|cheapest|"
                        r"lowest[- ]cost|costs? less than", re.I)
    hit = banned.search(flat)
    assert not hit, (f"{path} asserts a cost advantage the repo's own benchmark retracts: "
                     f"…{flat[max(0, hit.start()-90):hit.end()+90]}…")


def test_the_replacement_claim_is_one_a_test_binds():
    """covers: A2 · the deleted clause is replaced by a guarantee this repo can demonstrate."""
    flat = " ".join(_highlights().split())
    assert re.search(r"receipt|frozen contract|refus", flat, re.I), \
        "the ceremony bullet lost its point — replace the cost claim with a backed guarantee"


def test_the_measured_claim_carries_its_provenance():
    """covers: M5, A2 · sample size and engine version sit with the claim.

    BOTH front doors, like the M1 sibling above. This check read one of the two while that one
    read both, and the root README's copy of the same sentence shipped with no provenance at
    all — a rule that quantifies over a set has to enumerate that set, in every check that
    states it, not just the first one written.
    """
    for path in READMES:
        flat = " ".join(_highlights(path).split())
        m = re.search(r"Measured[^.]*\.", flat)
        assert m, f"{path}: the measured claim is gone — if it was cut, cut this check with it"
        window = flat[m.start():m.start() + 320]
        assert re.search(r"n\s*=\s*\d", window), f"{path}: no sample size beside the claim"
        assert re.search(r"\b\d+\.\d+(\.\d+)?\b", window), \
            f"{path}: no engine version beside the claim"


# --- M2/A3 — the ladder ---------------------------------------------------------------------

def test_the_readme_shows_the_size_ladder():
    """covers: M2, A3 · the ladder rows appear before the install section."""
    text = _readme()
    assert "## Install" in text, "the install section moved — this check's ordering anchor is gone"
    before = text.split("## Install", 1)[0]
    for rung in ("direct", "Task", "Milestone"):
        assert rung in before, f"the ceremony ladder never names the `{rung}` rung before Install"
    assert re.search(r"never (?:create|need) a node|no node|without a node", before, re.I), \
        "the ladder must state that most changes never create a node"
    assert "## Highlights" in before and \
        before.index("## Highlights") < before.rindex("direct"), \
        "the ladder must land AFTER Highlights — the ceremony question comes before install"


# --- M3/E3 — the doctor line ----------------------------------------------------------------

def test_the_doctor_cookbook_line_names_sync():
    """covers: M3, E3 · the line names the flag and what it writes."""
    for tree in SKILL_TREES:
        _assert_doctor_line(tree)


def _assert_doctor_line(tree):
    text = (tree / "SKILL.md").read_text(encoding="utf-8")
    lines = [l for l in text.splitlines() if re.search(r"^add doctor\b", l)]
    assert lines, "SKILL.md's cookbook no longer names `add doctor`"
    joined = " ".join(lines)
    assert "--sync" in joined, "the doctor line never names `--sync`, the flag that DOES write"
    assert re.search(r"recompil|recomputes?|re-?vendor|repairs?|regenerat", joined, re.I), \
        "the line names `--sync` without saying what it writes"


def test_the_skill_line_budget_is_unmoved():
    """covers: E3 · a replacement, not an addition."""
    for tree in SKILL_TREES:
        n = len((tree / "SKILL.md").read_text(encoding="utf-8").splitlines())
        assert n == 176, f"{tree}/SKILL.md is {n} lines — the pin is 176"


# --- M4/E4 — every version declaration ------------------------------------------------------

def test_version_parity_enumerates_every_declaration():
    """covers: M4, E4 · seven sources, all equal, skill trees included."""
    version = _pkg_version()
    declared = {}
    for tree in SKILL_TREES:
        text = (tree / "SKILL.md").read_text(encoding="utf-8")
        m = re.search(r'version:\s*"([^"]+)"', text)
        assert m, f"{tree}/SKILL.md declares no version"
        declared[str(tree)] = m.group(1)
    off = {k: v for k, v in declared.items() if v != version}
    assert not off, f"skill trees declare a stale version (package is {version}): {off}"


def test_the_parity_gate_itself_counts_the_skill_trees():
    """covers: M4 · the guard enumerates them, so a fourth declaration cannot ship unchecked."""
    guard = (PKG / "tests" / "test_version_parity.py").read_text(encoding="utf-8")
    assert "SKILL.md" in guard, \
        "test_version_parity.py still knows only five sources — the skill declarations ride free"


# --- E1 — the verb count is bound -----------------------------------------------------------

def test_the_verb_count_is_read_from_the_parser():
    """covers: E1 · the count is bound, not literal."""
    real = _engine_verb_count()
    for m in re.finditer(r"(\d+)[- ]verbs?\b", _readme()):
        assert int(m.group(1)) == real, \
            f"the README says {m.group(1)} verbs; the parser has {real}"


def test_the_benchmark_report_is_untouched():
    """covers: E2 · the report is honest and not to be edited; only the README's summary changes.

    The cheapest way to make a front-door claim true is to edit the evidence it contradicts. E2
    forbids exactly that, so this reads the report against git: it must be byte-identical to the
    committed version, and it must still carry the retraction the corrected README defers to.
    """
    rel = BENCH.relative_to(ROOT)
    head = subprocess.run(["git", "show", f"HEAD:{rel.as_posix()}"],
                          cwd=str(ROOT), capture_output=True)
    assert head.returncode == 0, f"{rel} is not tracked — the report cannot be held to its committed form"
    assert head.stdout == BENCH.read_bytes(), (
        f"{rel} was edited. The benchmark is the evidence this task defers to; the repair for a "
        f"refuted claim is to change the CLAIM, never the measurement.")
    text = BENCH.read_text(encoding="utf-8")
    assert "retracted" in text.lower() and "spec-kit is cheaper" in text, \
        "the report no longer states the finding the corrected README defers to"
