"""The front door must offer every way in that the package actually ships.

`BEYOND-CODE.md` shipped complete, executed and reachable from nowhere — zero references from
either README. That is the defect `test_no_orphan_refs` was written for one milestone ago, now for
a shipped document instead of a skill ref: correct, verified, and useless, because the reader who
needed it never learns it exists.

R:IDENTITYCREEP is the load-bearing NEGATIVE rule here. Naming the project, its tagline and its
packages is a human-owned decision that is currently unanswered, so this task must be provably
unable to have drifted it while editing the same two files.
"""
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PACKAGE = REPO / "add-method"
ROOT_README = REPO / "README.md"
PKG_README = PACKAGE / "README.md"
READMES = (ROOT_README, PKG_README)

# A2: a reader-facing walkthrough is a PATH IN — it teaches a reader how to start. Everything here
# is a top-level doc that is something else, with the reason it is not a way in:
#   README        an index, not a path
#   CHANGELOG · RELEASES   records of what happened
#   MIGRATION     a procedure for someone who already adopted
#   FORMAT        the bundle-format specification, referenced by the skill on demand
#   SECURITY      a disclosure policy
#   THIRD_PARTY_NOTICES · LICENSE   legal text
# Anything NOT listed here is treated as a walkthrough and must be reachable — so a new top-level
# doc fails this loudly rather than being silently dropped from coverage.
NOT_A_WALKTHROUGH = {"README.md", "CHANGELOG.md", "RELEASES.md", "MIGRATION.md", "LICENSE.md",
                     "FORMAT.md", "SECURITY.md", "THIRD_PARTY_NOTICES.md"}

# R:IDENTITYCREEP — the strings this task is forbidden to touch. Pinned deliberately: these are the
# one place a literal is CORRECT, because the rule is "do not change", and the decision to change
# them belongs to a human who has not made it.
IDENTITY = (
    "ADD — AI-Driven Development",
    "@pilotspace/add",
    "pilotspace-add",
    "Your AI's first milestone is always great. ADD is for every milestone after that.",
)

MD_LINK = re.compile(r"\[[^\]]*\]\((\.{1,2}/[^)#\s]+)")
# A bullet is `- ` or `* ` — the SPACE is what makes it a list. Without it, `**New here?**` reads as
# a bullet and a bold paragraph gets judged as if it were a list entry.
BULLET = re.compile(r"^\s*[-*]\s")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _label(path: Path) -> str:
    return str(path.relative_to(REPO))


def shipped_walkthroughs():
    """Derived from the package tree (M4), never listed — a new walkthrough is covered on arrival."""
    found = [p for p in sorted(PACKAGE.glob("*.md")) if p.name not in NOT_A_WALKTHROUGH]
    assert found, f"no reader-facing walkthrough found under {PACKAGE} — the extractor has drifted"
    return found


def test_every_shipped_walkthrough_is_reachable():
    """M1 + M4 — a walkthrough no README links cannot do its job, however correct it is."""
    both = "\n".join(_text(p) for p in READMES)
    orphans = [p.name for p in shipped_walkthroughs() if p.name not in both]
    assert not orphans, (
        f"walkthroughs the front door never reaches: {orphans} — correct, executed and invisible "
        f"to the reader who needed them")


def test_walkthroughs_are_offered_as_peers():
    """M2 — presence is not enough; a path offered one level down is offered to nobody.

    The comparison is by list nesting: in any bullet list that names the code walkthrough, the
    non-code one must appear as a sibling at the same indent, not tucked inside a sub-bullet or a
    trailing aside.
    """
    misplaced = []
    for path in READMES:
        lines = _text(path).splitlines()
        code_at = [(i, len(ln) - len(ln.lstrip()))
                   for i, ln in enumerate(lines)
                   if "GETTING-STARTED.md" in ln and BULLET.match(ln)]
        if not code_at:
            continue
        for i, indent in code_at:
            peers = [j for j, ln in enumerate(lines)
                     if "BEYOND-CODE.md" in ln and BULLET.match(ln)
                     and (len(ln) - len(ln.lstrip())) == indent
                     and abs(j - i) <= 6]
            if not peers:
                misplaced.append(f"{_label(path)}:{i + 1}: {lines[i].strip()[:70]}")
    assert not misplaced, (
        f"the code walkthrough is listed without the non-code one beside it: {misplaced} — a list "
        f"that names only one way in tells the other reader, by omission, that there is no other")


def test_readme_relative_links_resolve():
    """M3 + E1 — each link resolves against ITS OWN file's directory, not the repo root.

    `./GETTING-STARTED.md` means two different paths depending on which README carries it. A guard
    that resolved everything from the repo root would pass the broken one and fail the correct one.
    """
    dead = []
    for path in READMES:
        for target in MD_LINK.findall(_text(path)):
            if not (path.parent / target).exists():
                dead.append(f"{_label(path)} -> {target}")
    assert not dead, f"relative links that resolve to nothing: {dead}"


def test_identity_is_unchanged():
    """R:IDENTITYCREEP — this task edits the two files where the name lives; prove it did not move it.

    Checked against git rather than only against the working tree, so the guard compares what this
    task INHERITED, not what it happens to have written.
    """
    for phrase in IDENTITY:
        present = [p for p in READMES if phrase in _text(p)]
        assert present, f"the identity string {phrase!r} is gone from both READMEs"

    for path in READMES:
        head = subprocess.run(["git", "show", f"HEAD:{_label(path)}"],
                              cwd=REPO, capture_output=True, text=True)
        if head.returncode != 0:
            continue                     # not yet committed on this branch; the working tree stands
        for phrase in IDENTITY:
            assert (phrase in head.stdout) == (phrase in _text(path)), (
                f"{_label(path)} changed whether it carries {phrase!r} — the project's identity is "
                f"a human's decision and this task has no mandate to move it")
