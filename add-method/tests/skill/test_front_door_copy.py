"""The front door's framing must not tell a non-code reader that ADD is not for them.

`adoption-beyond-code` fixed what was FALSE here. What remained was not false, only narrow: the
problem statement said "AI coding", the prerequisite asked for a "CLI coding agent", and the
package summary described "building software when the AI writes the code". A reconciliation lead
who reached the walkthrough link had already been told three times that this was for people who
write code.

Two deliberate asymmetries in this guard:

1. The retired phrases are PINNED literals. That is correct here and nowhere else in this suite —
   the rule is "do not bring these back", so the literal IS the specification. Contrast every other
   guard added this milestone, which derives from the engine because it asserts what is TRUE rather
   than what is FORBIDDEN.
2. Benchmark sentences KEEP their code framing (A2). The campaign measured a six-milestone software
   project; describing it in domain-neutral terms would generalise real evidence beyond what it
   supports. A guard that swept those up would be enforcing a lie.
"""
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROOT_README = REPO / "README.md"
PKG_README = REPO / "add-method" / "README.md"
READMES = (ROOT_README, PKG_README)

# M1 — retired because each narrows ADD to software at a point where a reader is deciding whether
# it is for them. Paired with the claim that must SURVIVE the widening (R:NEUTERED, E1): a sentence
# deleted to satisfy this list would cost the reader a real fact.
RETIRED = {
    "AI coding doesn't fail on day one": "it rots",
    "An agent already knows how to write code": "one context window",
    "CLI coding agent": "Claude Code",
    "for building software when the AI writes the code": "verify",
    "the code is disposable": "disposable",
}

# M2 — untouched by this task. Guarded here as well as in test_positioning because this task edits
# the same two files and the tagline sits in the same paragraph as a retired phrase.
IDENTITY = (
    "ADD — AI-Driven Development",
    "@pilotspace/add",
    "pilotspace-add",
    "Your AI's first milestone is always great. ADD is for every milestone after that.",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    """Whitespace-normalised, for matching a claim that WRAPS across a line.

    Markdown prose is hard-wrapped, so `one context window` is stored as `one\\ncontext window` and
    a raw substring search reports the claim missing when it is plainly there. This is the third
    wrapped-text false negative in this suite (the evidence ladder needed a paragraph reader; the
    engine-comment guard needed comment markers flattened). Normalising the READER does not change
    what is asserted — the alternative was reflowing the prose to suit a regex.
    """
    return " ".join(_text(path).split())


def _label(path: Path) -> str:
    return str(path.relative_to(REPO))


def test_narrowing_phrases_are_gone():
    """M1 + R:REGRESS — the five named phrases, in either file."""
    found = [f"{_label(p)}: {phrase!r}" for p in READMES for phrase in RETIRED
             if phrase in _flat(p)]
    assert not found, (
        f"framing that narrows ADD to software is still on the front door: {found} — these are the "
        f"sentences a non-code reader meets while deciding whether this is for them")


def test_widened_claims_survived():
    """R:NEUTERED + E1 — prove each retirement widened a sentence instead of deleting one.

    Without this, the guard above is trivially satisfiable by cutting whole paragraphs, which would
    make the README shorter and worse. Each retired phrase names a word its claim cannot lose.
    """
    both = " ".join(_flat(p) for p in READMES)
    lost = [f"{phrase!r} -> {keep!r}" for phrase, keep in RETIRED.items() if keep not in both]
    assert not lost, (
        f"a retired phrase took its claim with it: {lost} — the sentence was supposed to be widened, "
        f"not removed; a reader who lost the fact is worse off than one who read it narrowly")


def test_benchmark_claims_keep_their_code_framing():
    """M3 + A2 — the campaign measured software. Saying otherwise would overstate real evidence."""
    root = _flat(ROOT_README)
    assert re.search(r"six[- ]milestone", root, re.I) or "six evolving milestones" in root, \
        "the benchmark framing lost its scope — what was measured was a six-milestone project"
    assert "spec-kit" in root, "the honest-comparison caveat is gone from the root README"


def test_identity_untouched_by_copy_pass():
    """M2 — this task edits the paragraphs the tagline lives in; prove it did not move it."""
    for phrase in IDENTITY:
        assert any(phrase in _text(p) for p in READMES), \
            f"the identity string {phrase!r} is gone from both READMEs"

    for path in READMES:
        head = subprocess.run(["git", "show", f"HEAD:{_label(path)}"],
                              cwd=REPO, capture_output=True, text=True)
        if head.returncode != 0:
            continue
        for phrase in IDENTITY:
            assert (phrase in head.stdout) == (phrase in _text(path)), (
                f"{_label(path)} changed whether it carries {phrase!r} — the name is settled and "
                f"this task has no mandate to move it")
