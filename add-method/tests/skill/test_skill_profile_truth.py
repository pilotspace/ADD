"""The shipped skill must describe the profile behaviour the engine actually has.

`profile-refusal` made `init` refuse a profile it does not ship. Two skill files still described
the fallback it replaced — `SKILL.md` ("writes the `code` lenses under any other name without
refusing") and `domains.md` ("accepts any string and then silently writes the `code` lenses"), in
all three shipped trees.

The cost is not cosmetic. `domains.md` used that claim as the REASON for a rule: do not invent a
profile, *because* it fails silently. The rule is still right; its reason is now false, and a
reader who tests the reason and finds it wrong has no cause to keep the rule (R:RULEWITHOUTREASON).

Everything the guard knows about profiles it reads from `add.PROFILES`, so a third profile moves
the expectation instead of breaking a pinned list.
"""
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402 — the engine is the authority on which profiles exist

# A3: a claim is shipped the moment ANY tree carries it, and `_bundled` is what pip installs.
TREES = (
    REPO / "skill" / "add",
    REPO / "src" / "add_method" / "_bundled" / "skill" / "add",
    REPO.parent / ".claude" / "skills" / "add",
)
TOUCHED = ("SKILL.md", "domains.md")

# The fallback, in the shapes the skill actually used to phrase it.
FALLBACK = re.compile(
    r"(accepts any string"
    r"|without refusing"
    r"|silently writes the `?code`? lenses"
    r"|writes the `?code`? lenses under (?:any|another) )",
    re.I)
# A2: describing what CHANGED is not promising it. A sentence marked as former is honest history.
FORMER = re.compile(r"\b(used to|formerly|before 3\.2|no longer|until now|previously)\b", re.I)

PROFILE_MENTION = re.compile(r"--profile\s+(?:<([^>]+)>|`?([a-z]+)`?)")


def _shipped_files():
    files = [(t / name) for t in TREES for name in TOUCHED if (t / name).is_file()]
    assert files, f"no shipped skill files found under {[str(t) for t in TREES]}"
    return files


def _label(path: Path) -> str:
    """Three trees, and two of them end in a directory called `skill`/`skills` — a short suffix
    makes two distinct files read as one. The path from the repo root is the only unambiguous name."""
    return str(path.relative_to(REPO.parent))


def _profiles_named(text: str) -> set:
    named = set()
    for m in PROFILE_MENTION.finditer(text):
        if m.group(2):
            named.add(m.group(2))
        else:
            named |= {p.strip(" `") for p in m.group(1).split("|")}
    return named


def test_skill_claims_no_silent_profile_fallback():
    """M1 + R:RULEWITHOUTREASON — the fallback is gone; nothing may still promise it."""
    stale = []
    for path in _shipped_files():
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if FALLBACK.search(line) and not FORMER.search(line):
                stale.append(f"{_label(path)}:{n}: {line.strip()[:70]}")
    assert not stale, (
        f"shipped skill surface still promises the silent `code` fallback the engine removed: "
        f"{stale} — `init` refuses now, and a rule resting on a reason the engine no longer "
        f"supports is a rule a reader has cause to discard")


def test_skill_names_only_shipped_profiles():
    """M2 + M4 — both directions against the engine, never a literal list."""
    shipped = set(add.PROFILES)
    named = set()
    for path in _shipped_files():
        named |= _profiles_named(path.read_text(encoding="utf-8"))
    assert named, "the skill names no profile at all — an agent cannot pick one it never sees"
    assert not (named - shipped), \
        f"the skill names profiles the engine does not ship: {sorted(named - shipped)}"
    assert not (shipped - named), (
        f"the engine ships profiles the skill never names: {sorted(shipped - named)} — an agent "
        f"orienting from SKILL.md cannot offer an option nobody told it exists")


def test_profile_extractor_is_derived_not_pinned():
    """R:PINNED — a fabricated mention must come back, proving nothing is hard-coded."""
    assert _profiles_named("run `add init --profile invented`") == {"invented"}, \
        "the profile extractor is pinning literals and will rot the way the prose did"
    assert set(add.PROFILES), "the engine exposes no PROFILES mapping — the premise changed"


def test_all_three_skill_trees_agree():
    """M3 + A3 — a fix that lands in one tree and not the others is not shipped."""
    for name in TOUCHED:
        digests = {}
        for tree in TREES:
            path = tree / name
            if path.is_file():
                digests[str(tree)] = hashlib.sha256(path.read_bytes()).hexdigest()
        assert len(digests) == len(TREES), f"`{name}` is missing from a shipped tree: {digests}"
        assert len(set(digests.values())) == 1, f"`{name}` differs across the skill trees"


# RETIRED: test_skill_surface_within_budget_after_edit (M3, E1)
#
# Its own docstring said it: "a second opinion about a pinned number is not a check, it is a
# contradiction." It then took one anyway — scraping `n <= (\d+)` out of test_surface.py's SOURCE
# TEXT to re-assert a budget that file already asserts. The scrape was itself pinned by a third
# module, so one number was held by a web of source-text pins across four files.
#
# The budgets live in tests/skill/skill_budget.py now, asserted once each. That a rewrite must FIT
# is still the rule; it is checked where the number is. Retired by `one-budget-one-guard`.
