"""Every living surface that enumerates the sweep vocabulary must agree with the engine.

The vocabulary is closed, which means it gets WRITTEN OUT to a reader — in the format spec, the
tutorial, the skill, its phase guide, and two chapters of the docs. Eight copies, all maintained by
hand. Adding a sixth dimension to the engine and missing one of them would reproduce exactly the
drift the milestone before this one spent seven tasks closing.

So the agreement is DERIVED, never pinned: the expected names are read from `add.SWEEP_DIMENSIONS`
at run time, and this file contains no literal copy of the list. That is the difference between a
guard and a ninth copy. The count word is derived the same way — a sentence saying "ask all five"
is just as wrong as a missing name, and greps for names alone never catch it.

Two deliberate exclusions, both named with a reason rather than filtered silently:

1. **Dated announcements keep their release framing.** Each described the release it announced, and
   at 3.0 there genuinely were five. Editing one to match today would falsify a record to flatter
   the present — the same rule that keeps the benchmark sentences code-framed in the front door.
2. **The CHANGELOG is a dated record too**, entry by entry, for the same reason.

`_enumerating_docs` is the part that matters most. A check that only visited a hard-coded list would
pass forever while a NEW doc quietly grew a sixth stale copy — the milestone's own lesson, learned
the expensive way: when a rule quantifies over a set, its check has to enumerate that set, and fail
loudly on a member it has not been taught about.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tooling"))
import add  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
PKG = REPO / "add-method"

# The surfaces that tell a reader, TODAY, what the vocabulary is. Every one must agree.
LIVING = (
    PKG / "FORMAT.md",
    PKG / "GETTING-STARTED.md",
    PKG / "docs" / "03-direction.md",
    PKG / "docs" / "12-bundle-format.md",
    PKG / "skill" / "add" / "SKILL.md",
    PKG / "skill" / "add" / "phases" / "direction.md",
    PKG / "src" / "add_method" / "_bundled" / "skill" / "add" / "SKILL.md",
    PKG / "src" / "add_method" / "_bundled" / "skill" / "add" / "phases" / "direction.md",
    REPO / ".claude" / "skills" / "add" / "SKILL.md",
    REPO / ".claude" / "skills" / "add" / "phases" / "direction.md",
)

# Excluded from must-agree, each with the reason. A dated record is not stale — it is accurate
# about its date.
DATED = {
    PKG / "docs" / "announcements" / "introducing-add-30.md":
        "announced 3.0, where the vocabulary genuinely had five names",
    PKG / "docs" / "announcements" / "2026-08-11-we-tried-to-cheat-our-own-dev-method.md":
        "a dated report of what the benchmark runs met at the time",
    PKG / "CHANGELOG.md":
        "an append-only record; each entry describes the release it shipped in",
}

# Of those, the ones that must not change AT ALL. Classification and immutability are two
# different jobs, and conflating them made the first version of this guard refuse the release
# entry this very change has to write: the CHANGELOG is a dated record that legitimately GROWS,
# newest-first. What must never happen to it is the same thing that must never happen to an
# announcement — an existing entry edited to match the present — and a byte pin cannot express
# that on a file with a moving head.
PINNED = tuple(p for p in DATED if p.parent.name == "announcements")

COUNT_WORDS = {4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}
EXPECTED_COUNT = COUNT_WORDS[len(add.SWEEP_DIMENSIONS)]

# Roots a reader actually reads. Excludes tests (which derive) and personas (which do not enumerate).
SCAN_ROOTS = ("add-method/FORMAT.md", "add-method/GETTING-STARTED.md", "add-method/README.md",
              "add-method/CHANGELOG.md", "add-method/docs", "add-method/skill",
              "add-method/src/add_method/_bundled/skill", ".claude/skills/add", "README.md")


def _label(path: Path) -> str:
    return str(path.relative_to(REPO))


def _names_on(line: str) -> set:
    """Dimension names this line ENUMERATES — two renderings, both real in the corpus.

    `who · which · when · absent · order` is one backticked run split by the separator; the prose
    rendering in `03-direction.md` backticks each name on its own. Matching bare words anywhere
    would sweep in every sentence containing "who" or "when", so each reading is anchored: a
    separator run, or an individually backticked token.

    The run form cannot be read by splitting on the separator and comparing segments exactly —
    the two OUTER names carry the surrounding sentence with them (`closed — \\`who` and
    `order\\` — because an`), so the first and last of five silently went missing. Inside a run,
    a word-boundary search is anchored enough.
    """
    dims = set(add.SWEEP_DIMENSIONS)
    found = set(re.findall(r"`(\w+)`", line)) & dims
    if line.count(" · ") >= 2:
        found |= {d for d in dims if re.search(rf"\b{d}\b", line)}
    return found


def _is_enumeration(line: str) -> bool:
    return len(_names_on(line)) >= 3


def _tracked_docs() -> list:
    out = subprocess.run(["git", "ls-files", "--", *SCAN_ROOTS],
                         cwd=REPO, capture_output=True, text=True).stdout.split()
    return [REPO / p for p in out if p.endswith(".md")]


def _enumerating_docs() -> list:
    found = []
    for path in _tracked_docs():
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(_is_enumeration(line) for line in text.splitlines()):
            found.append(path)
    return found


def test_living_prose_agrees_with_the_engine():
    """covers: M3, E1, R:PINNED — derived from the engine's list, and complete over the corpus."""
    expected = set(add.SWEEP_DIMENSIONS)

    stale = []
    for path in LIVING:
        text = path.read_text(encoding="utf-8")
        carried = set()
        for line in text.splitlines():
            if _is_enumeration(line):
                carried |= _names_on(line)
        missing = expected - carried
        if missing or not carried:
            stale.append(f"{_label(path)}: missing {sorted(missing) or 'any enumeration at all'}")
    assert not stale, (
        f"a living surface tells a reader a different vocabulary than the engine enforces: {stale} "
        f"— the engine's list is {list(add.SWEEP_DIMENSIONS)}")

    # A count word only miscounts when it is counting THE DIMENSIONS, which the corpus does in
    # exactly two phrasings: "<count> dimensions" and the sweep idiom "ask all <count>". Anything
    # looser is wrong in both directions, and both failures were live here:
    #   · `\bfive\b` near "dimension" flagged a MEASURED fact — three live runs "wrote five to
    #     seven real assumptions" — which keeps its number for the reason the front door's
    #     benchmark sentences keep their code framing.
    #   · `(all|the) <count>` flagged "the five specs" in seven files. That is a different five —
    #     the 5-DD living specs — and it did not change.
    # The completeness half of this check is the primary enforcement; this half only reaches prose
    # that states a count without listing the names.
    wrong = "|".join(w for w in COUNT_WORDS.values() if w != EXPECTED_COUNT)
    MISCOUNT = re.compile(rf"\b({wrong})\s+(?:\w+\s+)?dimensions?\b|\bask\s+(?:all|each)\s+({wrong})\b")
    miscounted = [f"{_label(p)}:{n}" for p in LIVING
                  for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
                  if MISCOUNT.search(line)]
    assert not miscounted, (
        f"a living surface still counts the dimensions wrong: {miscounted} — there are now "
        f"{EXPECTED_COUNT}, and 'ask all five' misleads a reader exactly as a missing name would")

    known = {p.resolve() for p in LIVING} | {p.resolve() for p in DATED}
    unclassified = [_label(p) for p in _enumerating_docs() if p.resolve() not in known]
    assert not unclassified, (
        f"these docs enumerate the sweep vocabulary and this guard has never been told about them: "
        f"{unclassified} — add each to LIVING (it must agree) or to DATED (with the reason it is a "
        f"record, not a claim about today). A guard that quantifies over a set must enumerate it.")


def test_dated_announcements_keep_their_release_framing():
    """covers: R:REWRITE — GREEN at freeze, armed through the build against a too-wide edit."""
    for path in PINNED:
        reason = DATED[path]
        head = subprocess.run(["git", "show", f"HEAD:{_label(path)}"],
                              cwd=REPO, capture_output=True, text=True)
        if head.returncode != 0:
            continue
        assert head.stdout == path.read_text(encoding="utf-8"), (
            f"{_label(path)} was edited — {reason}. Bringing a dated record into line with the "
            f"present falsifies it; the vocabulary changed, what that document said did not.")

    # The CHANGELOG gets the same protection in the form its shape allows: it may GROW, but no
    # line that was already in it may vanish. That is what "do not rewrite a dated entry" means
    # on a file with a moving head, and a byte pin could not say it.
    growing = [p for p in DATED if p not in PINNED]
    for path in growing:
        head = subprocess.run(["git", "show", f"HEAD:{_label(path)}"],
                              cwd=REPO, capture_output=True, text=True)
        if head.returncode != 0:
            continue
        now = set(path.read_text(encoding="utf-8").splitlines())
        lost = [l for l in head.stdout.splitlines() if l.strip() and l not in now]
        assert not lost, (
            f"{_label(path)} lost {len(lost)} line(s) that were already recorded — {DATED[path]}. "
            f"It may gain entries; it may not lose or reword one. First: {lost[0]!r}")
