"""A 25th verb ships with every count of it, or the front door lies.

`test_every_registry_learned_the_new_verb` (tests/engine/test_check_verb.py) hard-codes `check`
for the command-reference row, so it goes green while every `search` registry is missed. This is
that verb's own guard. The verb SET is derived from the CLI source — a hand list is how the
seventh writer gets missed (/specs/method.md#M29) — but the set of enumerating SURFACES is a
hand list, and that is a real limit (A5/A10), so every surface here carries a floor that reds
when the page stops stating what it is being asked about, rather than passing vacuously.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO.parent
sys.path.insert(0, str(REPO / "tooling"))

SKILL_TREES = (REPO / "skill" / "add",
               REPO / "src" / "add_method" / "_bundled" / "skill" / "add",
               ROOT / ".claude" / "skills" / "add")

LINE_PIN = 176
BYTE_PIN = 13258


def _verbs():
    source = (REPO / "tooling" / "cli.py").read_text(encoding="utf-8")
    return set(re.findall(r'sub\.add_parser\("([a-z-]+)"', source))


def test_every_registry_learned_the_search_verb():
    """covers: M8, R:STALE_REGISTRY, A5, A10 — the verb set is derived; every surface has a floor."""
    verbs = _verbs()
    assert "search" in verbs, "cli.py: `search` is not a registered subcommand"
    n = len(verbs)
    # A VALUE, not a ceiling. `search` landed the 25th verb; `show` (task show-verb) landed the
    # 26th, which moves this number without weakening what the guard checks — that every
    # registry below is derived from the CLI rather than hand-maintained.
    assert n == 26, f"the CLI ships {n} verbs; the pin was last re-aimed at `show` — {sorted(verbs)}"

    wired = (REPO / "tests" / "engine" / "test_cli.py").read_text(encoding="utf-8")
    block = wired[wired.find("WIRED = {"):wired.find("}", wired.find("WIRED = {"))]
    assert block, "test_cli.py no longer declares a WIRED set — this guard would pass vacuously"
    declared = set(re.findall(r'"([a-z-]+)"', block))
    assert declared == verbs, f"test_cli.py WIRED drifted from the CLI: {declared ^ verbs}"

    claims = 0
    for rel in ("README.md", "add-method/README.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        found = re.findall(r"(\d+)-verb kernel", text) + re.findall(r"CLI — (\d+) verbs", text)
        assert found, (
            f"{rel}: no verb-count claim matched — a filter on a pattern the page no longer "
            "emits asserts nothing (R:STALE_REGISTRY)")
        for claim in found:
            claims += 1
            assert int(claim) == n, f"{rel}: claims {claim} verbs, the CLI ships {n} (R:STALE_REGISTRY)"
    assert claims >= 3, f"only {claims} verb-count claims were checked; three were measured here"

    # The command reference makes a COMPLETENESS claim on its own page; bind it in both
    # directions rather than only asserting one row exists.
    ref = (REPO / "docs" / "13-command-reference.md").read_text(encoding="utf-8")
    assert "complete, shipped verb set" in ref, \
        "13-command-reference.md no longer claims completeness — this check binds that claim"
    rows = set(re.findall(r"^\|\s*`([a-z-]+)`\s*\|", ref, re.M))
    assert rows, "13-command-reference.md: no verb rows parsed — the guard would pass vacuously"
    assert rows == verbs, f"13-command-reference.md is not the complete verb set: {rows ^ verbs}"
    search_row = next(ln for ln in ref.splitlines() if ln.startswith("| `search` |"))
    assert "--as-of" in search_row, "13-command-reference.md: the `search` row does not name its flag"

    # And the orphan direction: a verb no skill doc names is invisible to the only thing an
    # agent reads. Derived the same way `test_every_wired_verb_is_documented` derives it.
    documented = set()
    for path in (REPO / "skill" / "add").rglob("*.md"):
        if "persona-author" in path.relative_to(REPO / "skill" / "add").parts:
            continue
        documented |= {m.group(1) for m in
                       re.finditer(r"`?add\s+([a-z][a-z-]{1,22})\b", path.read_text(encoding="utf-8"))}
    assert "search" in documented, "no skill doc names `add search` — the verb ships an orphan"


def test_skill_names_search_within_both_budget_pins():
    """covers: R:BUDGET_BUMP, A2 — a new line is funded by compression, never by a re-pin."""
    canonical = SKILL_TREES[0] / "SKILL.md"
    assert canonical.is_file(), \
        f"the skill router is the subject of this check, and it is missing: {canonical}"

    seen = {}
    for tree in SKILL_TREES:
        skill = tree / "SKILL.md"
        assert skill.exists(), f"skill tree missing (not a skip): {skill}"
        text = skill.read_text(encoding="utf-8")
        seen[str(skill)] = text
        line = next((ln for ln in text.splitlines() if "reopen" in ln and "deltas" in ln), None)
        assert line, f"{skill}: no sentence listing the wired loop surface"
        assert "search" in line, \
            f"{skill}: the wired-surface sentence does not name `search` — {line!r}"
    assert len(set(seen.values())) == 1, \
        f"the three skill trees diverged: {sorted(seen)}"

    nlines = len(canonical.read_text(encoding="utf-8").splitlines())
    nbytes = len(canonical.read_bytes())
    assert nlines <= LINE_PIN, f"SKILL.md is {nlines} lines — over the {LINE_PIN} pin (R:BUDGET_BUMP)"
    assert nbytes <= BYTE_PIN, f"SKILL.md is {nbytes} bytes — over the {BYTE_PIN} pin (R:BUDGET_BUMP)"

    # The pins themselves must still be the SAME numbers, in the same file, unedited: raising a
    # pin to make room is the move this reject exists to stop, and it is invisible in a diff of
    # SKILL.md alone.
    surface = (REPO / "tests" / "skill" / "test_surface.py").read_text(encoding="utf-8")
    assert f"n <= {LINE_PIN}" in surface, \
        f"the {LINE_PIN}-line human call was edited or removed (R:BUDGET_BUMP)"
    assert f"BYTE_BUDGET = {BYTE_PIN}" in surface, \
        f"the {BYTE_PIN}-byte pin was raised or removed (R:BUDGET_BUMP)"
