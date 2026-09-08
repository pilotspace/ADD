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


def _git_diff_calls():
    """Every `git diff` invocation in the suite: (path, line, argv-as-written)."""
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
            if words[:2] != ["git", "diff"]:
                continue                      # E3: a string literal saying "git diff" is prose
            out.append((f.relative_to(REPO).as_posix(), n.lineno, words))
    return out


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
