"""Every capability the front door promises must name the shipped thing that makes it true.

`adoption-beyond-code` found seven false front-door claims and built a guard for each. This one
still got through all of them: both READMEs promised "a wireframe and a zero-dependency HTML mock,
approved before any build" while the skill tree contained no mention of either. It was a 1.7-era UI
step that 3.0 removed, and nothing noticed for two minor versions.

The reason is worth stating plainly, because it defines what THIS file does differently. Those
guards check nouns the engine EXPOSES — bundle files, verb counts, profiles, runnable commands. A
noun can be looked up. A capability cannot: "see the UI before a line of code" names no symbol, so
no amount of checking the engine's exports would ever have reached it.

So the binding is inverted. Each bullet declares the artifact that makes it true, by kind:

    verb:<name>     a verb `cli.py` registers — the capability is a command you can run
    engine:<expr>   a value in the engine that IS the behaviour (a floor, a mapping, a list)
    skill:<path>    a file in the skill tree that carries the instruction

and the guard resolves it against the real tree. What it can prove is narrow and worth being honest
about: that SOMETHING ships under that name. It cannot read the bullet and judge whether the thing
is what the bullet describes — that is the author's job at registration time. What it makes
impossible is the specific failure that happened here: a promise outliving the feature, with no
edit anywhere near the README to prompt anyone to look.

Two rules keep it from decaying into a ritual. An anchor may never be the bullet's own words found
somewhere in the corpus (R:LOOSE — the promise proving itself is the failure being closed). And an
unregistered bullet fails BY NAME, saying what the anchor kinds are and that retiring an unbackable
promise is the intended outcome, not a workaround — because the next person to meet this check will
be editing the front door months from now knowing nothing about this task, and a check that reads
as an obstacle gets satisfied with a vague anchor, which is worse than no check at all.
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
ROOT_README = REPO / "README.md"
PKG_README = PKG / "README.md"

BULLET = re.compile(r"^\s*[-*]\s")

# M1 — retired, each with the claim that must SURVIVE the retirement (R:CULL). A guard that only
# forbade phrases would be satisfiable by cutting whole bullets, which is the cheap wrong answer.
RETIRED = {
    "wireframe": "See the UI",
    "HTML mock": "before a line of code",
    "kill-test": "reasons before it drafts",
}

IDENTITY = ("ADD — AI-Driven Development", "@pilotspace/add", "pilotspace-add")

# S3 — the registry. Keyed per file (E1): the package README is shorter by design, so a shared
# key would silently accept a bullet present in one list and absent from the other.
# The key is a distinctive fragment of the bullet; the value is its anchor.
ANCHORS = {
    "README.md": {
        "stops re-breaking last month's work": "skill:loop.md",
        "Stop babysitting the build": "verb:freeze",
        "Know it's correct without reading every line": "verb:gate",
        "Pay ceremony only where it buys something": "verb:gate",
        "Never ship a security hole on autopilot": "engine:SENSITIVITY_FLOOR",
        "The method adapts to *your* codebase": "verb:learn",
        "The agent reasons before it drafts": "verb:advise",
        "has to live with this": "engine:SWEEP_DIMENSIONS",
        "Everything about a feature in one place": "verb:new",
        "Grows with your team": "verb:wave",
        "Keep the agent you already use": "verb:init",
    },
    "add-method/README.md": {
        "stops re-breaking last month's work": "skill:loop.md",
        "Stop babysitting the build": "verb:freeze",
        "Know it's correct without reading every line": "verb:gate",
        "Pay ceremony only where it buys something": "verb:gate",
        "Never ship a security hole on autopilot": "engine:SENSITIVITY_FLOOR",
        "The method adapts to *your* codebase": "verb:learn",
        "has to live with this": "engine:SWEEP_DIMENSIONS",
        "Grows with your team": "verb:wave",
        "Keep the agent you already use": "verb:init",
    },
}

ANCHOR_KINDS = "verb:<name> · engine:<value> · skill:<file in the skill tree>"


def _label(path: Path) -> str:
    return str(path.relative_to(REPO))


def _verbs() -> set:
    src = (PKG / "tooling" / "cli.py").read_text(encoding="utf-8")
    return set(re.findall(r"add_parser\(\s*[\"']([a-z-]+)", src))


def _highlights(path: Path) -> list:
    """The bullets under the Highlights heading — the fixed list of capability claims.

    A2: only this list. The tagline, the comparison table and the benchmark prose are argument,
    not claims about what ships, and demanding an anchor for an argument would be a category error.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip().lstrip("# ").strip()
                 in ("Highlights", "✨ Highlights"))
    out = []
    for line in lines[start + 1:]:
        if line.startswith("#"):
            break
        if BULLET.match(line):
            out.append(line.strip())
    return out


def _resolves(anchor: str) -> bool:
    """Does the artifact this bullet points at actually ship?

    R:LOOSE: every kind resolves against a STRUCTURE — the verb table, an engine attribute, a
    file in the tree. None of them searches for the bullet's own words, because a promise that
    can cite itself is exactly the thing this file exists to stop.
    """
    kind, _, ref = anchor.partition(":")
    if kind == "verb":
        return ref in _verbs()
    if kind == "engine":
        return hasattr(add, ref)
    if kind == "skill":
        return (PKG / "skill" / "add" / ref).exists()
    return False


def test_every_highlight_names_a_shipped_artifact():
    """covers: M2, M3, E1, R:LOOSE — the anchor resolves, for every bullet in both lists."""
    broken = []
    for rel, registry in ANCHORS.items():
        for key, anchor in registry.items():
            if not _resolves(anchor):
                broken.append(f"{rel}: {key!r} -> {anchor}")
    assert not broken, (
        f"a front-door promise points at something that does not ship: {broken} — either the "
        f"capability was removed and the bullet must go with it, or the anchor names the wrong "
        f"artifact. This is the check the wireframe promise needed and did not have.")


def test_unregistered_bullet_fails_by_name():
    """covers: M3, A6 — a new promise cannot join the list silently.

    The message is the deliverable here as much as the assertion. Whoever meets this check will be
    editing the front door with no knowledge of this task, so it has to say what to do and that
    retiring the bullet is a legitimate answer — otherwise it gets satisfied with a vague anchor
    and the list reads as verified while meaning less than before.
    """
    for path, rel in ((ROOT_README, "README.md"), (PKG_README, "add-method/README.md")):
        registry = ANCHORS[rel]
        unregistered = [b for b in _highlights(path)
                        if not any(key in b for key in registry)]
        assert not unregistered, (
            f"{_label(path)} promises something this guard has never been told about:\n  "
            + "\n  ".join(unregistered)
            + f"\n\nRegister each in ANCHORS['{rel}'] with the shipped artifact that makes it "
              f"true ({ANCHOR_KINDS}) — or, if nothing ships that keeps the promise, RETIRE the "
              f"bullet. Retiring is the intended outcome, not a workaround: the wireframe promise "
              f"outlived its feature by two minor versions because nothing here could see it.")

        orphaned = [key for key in registry
                    if not any(key in b for b in _highlights(path))]
        assert not orphaned, (
            f"{_label(path)}: these registry entries match no bullet: {orphaned} — a stale entry "
            f"makes the count look complete while a real promise goes unchecked")


def test_retired_promises_are_gone():
    """covers: M1 — the capabilities the shipped surface does not carry."""
    found = [f"{_label(p)}: {phrase!r}"
             for p in (ROOT_README, PKG_README)
             for phrase in RETIRED
             if phrase in p.read_text(encoding="utf-8")]
    assert not found, (
        f"the front door still promises a capability nothing ships: {found} — the skill tree has "
        f"no wireframe step and no HTML mock; that was a 1.7-era UI beat 3.0 removed")


def test_retirement_did_not_cull_a_true_claim():
    """covers: M4, R:CULL — GREEN by design, armed through the build against the cheap answer."""
    both = " ".join(p.read_text(encoding="utf-8") for p in (ROOT_README, PKG_README))
    for phrase in IDENTITY:
        assert phrase in both, f"the identity string {phrase!r} is gone from both READMEs"
    assert "spec-kit" in ROOT_README.read_text(encoding="utf-8"), \
        "the honest-comparison caveat is gone from the root README"

    for path, rel in ((ROOT_README, "README.md"), (PKG_README, "add-method/README.md")):
        head = subprocess.run(["git", "show", f"HEAD:{rel}"],
                              cwd=REPO, capture_output=True, text=True)
        if head.returncode != 0:
            continue
        before = len([l for l in head.stdout.splitlines() if BULLET.match(l)])
        after = len([l for l in path.read_text(encoding="utf-8").splitlines()
                     if BULLET.match(l)])
        assert before - after <= 2, (
            f"{rel} lost {before - after} bullets — this task retires the wireframe promise and "
            f"narrows one other. Reaching green by deleting bullets whose promises the product "
            f"actually keeps is what R:CULL forbids; the reader is worse off, not better informed.")
