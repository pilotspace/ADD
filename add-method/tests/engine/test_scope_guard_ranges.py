"""Red suite for `scope-guard-names-its-range` — a scope guard names the range it guards.

Two guards in this suite claimed a task had not touched a file, and asserted it with a diff
against the WORKING TREE. That guards nothing: it reports red on every branch that touches the
path for any reason, and green the moment you type `git commit`. One of the two was worse — its
path is gitignored AND absent, so `git diff` returned nothing for every possible working tree and
the check reported success while running on nothing at all.

The claim itself ("this task did not touch X") is settled at MERGE. No diff can re-litigate it,
so those guards are retired with a record. What replaces them is the shape check below: every
`git diff` in the suite must name a revision range, or say what it is actually asserting.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO.parent
sys.path.insert(0, str(REPO / "tooling"))

RETIRED = {
    "tests/skill/test_claimed_output_guard.py": "test_no_engine_output_was_added",
    "tests/engine/test_cut_flags.py": "test_gated_node_untouched",
}

# A `git diff` is legitimate when its arguments name a revision RANGE — `main...HEAD`, `A..B` —
# because that names WHICH commits the claim is about. A bare diff, or one against `HEAD`, names
# the uncommitted working tree, which `git commit` empties (E1, A5).
_WORKING_TREE = {"HEAD", "--cached", "--staged"}


# WIDENED (a-head-guard-declares-its-lifetime): this enumerated `git diff` alone, because that is
# the spelling the two retired guards happened to use. Seven more sites resolve a ref through
# `git show HEAD:<path>` and one through `git merge-base`, and every one of them is satisfied by
# `git commit` exactly the same way. A rule enforced over one spelling of a shape is a rule the
# other spellings do not have. `ls-files`, `rev-parse` and `status` are NOT here: they read the
# index, not a revision, so nothing about them expires (A2).
_REF_VERBS = ("diff", "show", "merge-base")


def _enclosing(tree, node):
    """The FunctionDef whose source span contains `node` — the unit that owns a lifetime."""
    best = None
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        if fn.lineno <= node.lineno <= (fn.end_lineno or fn.lineno):
            if best is None or fn.lineno > best.lineno:
                best = fn
    return best


def _git_ref_calls():
    """Every git invocation that resolves a REVISION: (path, line, argv, enclosing FunctionDef)."""
    out = []
    for f in sorted((REPO / "tests").rglob("test_*.py")):
        tree = ast.parse(f.read_text())
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            arg = n.args[0] if n.args else None
            if not isinstance(arg, ast.List):
                continue
            words = [e.value for e in arg.elts if isinstance(e, ast.Constant)
                     and isinstance(e.value, str)]
            if words[:1] != ["git"] or words[1:2] not in ([v] for v in _REF_VERBS):
                continue                      # E3: a string literal saying "git diff" is prose
            # An f-string ref (`f"HEAD:{rel}"`) contributes no Constant, so read the whole call's
            # literals to see which revision it names — the argv list alone would miss it.
            spelled = words + [c.value for c in ast.walk(arg)
                               if isinstance(c, ast.Constant) and isinstance(c.value, str)
                               and c.value not in words]
            out.append((f.relative_to(REPO).as_posix(), n.lineno, words, spelled,
                        _enclosing(tree, n)))
    return out


def _git_diff_calls():
    """The `git diff` subset, unchanged — the two rungs below were written against it."""
    return [(p, ln, w) for p, ln, w, _, _ in _git_ref_calls() if w[1] == "diff"]


def _names_a_range(words):
    return any(".." in w for w in words[2:])


def test_no_scope_guard_is_satisfied_by_a_commit():
    """covers: M1, M3, R:COMMITCLEAN, A5, A6, E1, E3 — the shape, enumerated over the suite."""
    offenders = [
        (path, line, words) for path, line, words in _git_diff_calls()
        if not _names_a_range(words)
    ]
    assert not offenders, (
        "R:COMMITCLEAN — these `git diff` guards name no revision range, so they assert something "
        "about the working tree and `git commit` alone makes them pass:\n"
        + "\n".join(f"  {p}:{ln} — {w}" for p, ln, w in offenders)
        + "\n\nEither name the range the claim is about (`main...HEAD`), or — if the claim is "
          "settled and no range can re-litigate it — assert the PREMISE instead: what must still "
          "be true, so a restored subject turns this red.")


def test_no_guard_diffs_a_path_git_cannot_see():
    """covers: M2, R:BLINDPATH, A4, E2 — a diff against a path git does not track proves nothing."""
    blind = []
    for path, line, words in _git_diff_calls():
        for target in words[words.index("--") + 1:] if "--" in words else []:
            tracked = subprocess.run(["git", "ls-files", "--error-unmatch", target],
                                     cwd=str(REPO), capture_output=True, text=True)
            if tracked.returncode != 0:
                blind.append(f"  {path}:{line} — `{target}` is untracked or absent"
                             f"{' (and the diff names no range either)' if not _names_a_range(words) else ''}")
    assert not blind, (
        "R:BLINDPATH — these guards diff a path git cannot see, so they report success for every "
        "possible working tree:\n" + "\n".join(blind)
        + "\n\nAssert the premise instead — that the subject is absent — so restoring it turns "
          "this red and whoever restores it has to decide what protects it.")


def test_the_retired_guards_left_a_record():
    """covers: M4, A3, E4 — a claim withdrawn in silence is a claim nobody can audit."""
    missing = []
    for rel, name in RETIRED.items():
        text = (REPO / rel).read_text()
        assert f"def {name}(" not in text, (
            f"{rel}::{name} is still defined — it guards the working tree and is satisfied by "
            f"`git commit`; retire it with a record (M4)")
        if name not in text:
            missing.append(f"  {rel} — no record of `{name}` or why its claim is settled")
    assert not missing, (
        "M4 — a retired guard must leave its reason in the module it left, not only in a commit "
        "message nobody greps:\n" + "\n".join(missing))


# Every ref a guard may resolve must exist in a FRESH SHALLOW checkout — which is what
# `actions/checkout@v7` makes by default (depth 1, no remote branches). `HEAD` always does.
# `origin/<branch>` does not, and reading its absence as a failed claim is what took CI red.
_ABSENT_ON_A_SHALLOW_CLONE = ("origin/", "refs/remotes/")

# The label a working-tree-vs-HEAD guard owes its reader. Deliberately a WORD in the function's
# own source rather than a decorator: it is a warning to the next person editing the file, not a
# token that satisfies a checker (A6).
_TRIPWIRE = "TRIPWIRE"


def test_no_guard_reads_a_ref_a_fresh_checkout_lacks():
    """covers: M2, R:ABSENTREF, A2, A4, A5 — a ref CI does not have is not a baseline."""
    calls = _git_ref_calls()
    assert len(calls) >= 8, \
        f"the enumeration found only {len(calls)} git-ref call(s); it is not reading the suite"
    absent = [f"  {p}:{ln} — resolves {w!r}" for p, ln, _, spelled, _ in calls
              for w in spelled if w.startswith(_ABSENT_ON_A_SHALLOW_CLONE)]
    assert not absent, (
        "R:ABSENTREF — these guards resolve a ref that `actions/checkout`'s depth-1 clone does "
        "not have, so on CI they read `cannot establish a baseline` as `the claim is false`:\n"
        + "\n".join(absent)
        + "\n\nPin the content instead (`test_the_messages_are_untouched`), or name a range whose "
          "ends the checkout actually fetches.")


def test_a_worktree_guard_declares_it_is_a_tripwire():
    """covers: M1, M3, R:SILENTTRIPWIRE, A1, A6 — say which of the two it is, in the source.

    A `HEAD`-vs-working-tree guard is not worthless — it fires while the edit is being made,
    which is when it can help. What is worthless is a green CI read as the claim having held,
    because after `git commit` the two sides are the same bytes. So the guard stays and says so.
    """
    unlabelled = []
    for path, line, _, spelled, fn in _git_ref_calls():
        if not any(w.startswith("HEAD:") or w == "HEAD" for w in spelled):
            continue                                   # a named range expires nothing
        if fn is None:
            unlabelled.append(f"  {path}:{line} — at module level, so it owns no lifetime")
            continue
        src = ast.get_source_segment((REPO / path).read_text(), fn) or ""
        if _TRIPWIRE not in src:
            unlabelled.append(f"  {path}:{line} — {fn.name}")
    assert not unlabelled, (
        "R:SILENTTRIPWIRE — these guards compare the working tree to `HEAD`, which `git commit` "
        f"makes identical, and never say so:\n" + "\n".join(unlabelled)
        + f"\n\nWrite {_TRIPWIRE} and a sentence in the function: it fires during the edit and "
          "is inert once committed, so nobody reads a green CI as this claim holding. If the "
          "claim must hold permanently, pin the content instead.")


def test_the_widening_dropped_no_claim():
    """covers: M4, R:CLAIMDROP, A3 — annotating a guard is not softening it."""
    for path, _, _, spelled, fn in _git_ref_calls():
        # `test_*` only. A private helper legitimately RETURNS the baseline for a check to
        # assert on (`_at_head`); demanding an assert inside it would push the read back into
        # every caller, which is the duplication the helper exists to remove.
        if fn is None or not fn.name.startswith("test_") \
                or not any(w.startswith("HEAD") for w in spelled):
            continue
        asserts = [n for n in ast.walk(fn) if isinstance(n, ast.Assert)]
        assert asserts, (
            f"R:CLAIMDROP — {path}::{fn.name} reads git and asserts nothing. This task labels "
            f"guards; it does not empty them.")
