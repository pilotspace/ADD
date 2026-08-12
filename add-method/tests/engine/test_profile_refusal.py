"""`init` must refuse a profile it cannot honour, instead of quietly writing `code` lenses.

`PROFILES.get(profile) or PROFILES["code"]` meant every unrecognised name resolved to the code
lens set. A finance lead who guesses `--profile finance` gets a bundle asking how the product is
built and what that forecloses, concludes ADD understood the domain, and discovers otherwise only
after writing into it.

Every expectation here is derived from `add.PROFILES` and `add.SENSITIVITY_FLOOR` rather than
listed, so adding a profile later moves the checks with it — a profile is DATA, and a guard that
pinned today's two would have to be edited to ship a third.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOLING = REPO / "tooling"
CLI = TOOLING / "cli.py"
ENGINE = TOOLING / "add.py"
BUNDLED = REPO / "src" / "add_method" / "_bundled" / "tooling"
sys.path.insert(0, str(TOOLING))

import add  # noqa: E402

# R:NEWFLOOR exists because a "domain profile" is the exact shape of change that tempts someone to
# invent a `finance` floor — additivity means lenses only.
#
# The invariant is about which sensitivities RAISE the floor, not about how many keys the map has.
# A first draft asserted `set(SENSITIVITY_FLOOR) == {security, data, architecture}` and failed on
# `mechanical`, which is a legitimate fourth sensitivity mapping to `process` — it raises nothing.
# That draft conflated two vocabularies: sensitivity NAMES (the map's keys) and authority VALUES
# (`AUTHORITY_ORDER`). Both are derived below instead of listed.
RAISING = {"security", "data", "architecture"}


def _init(tmp_path, *flags):
    return subprocess.run([sys.executable, str(CLI), "init", *flags, "Probe"],
                          capture_output=True, text=True, cwd=tmp_path)


def test_unknown_profile_refuses(tmp_path):
    """M1 + R:SILENTFALLBACK — refuse, and say what IS on offer."""
    out = _init(tmp_path, "--profile", "finance")
    said = out.stdout + out.stderr
    assert out.returncode != 0, \
        f"`init --profile finance` succeeded — it silently wrote lenses for a profile it never had:\n{said}"
    for shipped in add.PROFILES:
        assert shipped in said, (
            f"the refusal never names the `{shipped}` profile — refusing without saying what is "
            f"available trades a wrong answer for an unhelpful one. It said:\n{said}")


def test_refused_init_leaves_nothing_behind(tmp_path):
    """M2 — a refusal that half-creates a bundle is worse than the fallback it replaces."""
    _init(tmp_path, "--profile", "finance")
    leftovers = sorted(p.name for p in tmp_path.iterdir())
    assert not leftovers, f"a refused `init` left files behind: {leftovers}"


def test_shipped_profiles_still_initialise(tmp_path):
    """M3 — driven from `add.PROFILES`, so a third profile is covered the day it lands."""
    assert add.PROFILES, "the engine ships no profiles at all — the premise changed"
    for name, lenses in add.PROFILES.items():
        target = tmp_path / name
        target.mkdir()
        out = _init(target, "--profile", name)
        assert out.returncode == 0, f"`--profile {name}` is shipped but refused:\n{out.stdout}{out.stderr}"
        specs = {p.stem for p in (target / ".add" / "specs").glob("*.md")}
        assert set(lenses) <= specs, (
            f"`--profile {name}` did not write its own lenses: expected {sorted(lenses)}, "
            f"found {sorted(specs)}")


def test_omitted_profile_still_defaults_to_code(tmp_path):
    """M3 + E2 — the rule binds a WRONG name, never a missing one.

    Without this, the obvious implementation (require `--profile`) would break every scripted
    `init` in existence — a breaking change nobody asked for, hiding inside a bug fix.
    """
    out = _init(tmp_path)
    assert out.returncode == 0, f"a bare `init` was refused:\n{out.stdout}{out.stderr}"
    specs = {p.stem for p in (tmp_path / ".add" / "specs").glob("*.md")}
    assert set(add.PROFILES["code"]) <= specs, \
        f"a bare `init` did not produce the code lens set: found {sorted(specs)}"


def test_engine_promises_no_unshipped_profile():
    """M4 — the source itself advertised three profiles that ship nowhere.

    `add.py` carried "the remaining three ship as template files (amendment A1)". No such template
    exists in the tree. A comment is documentation too, and this one told the next reader to go
    looking for something that was never built.

    The claim WRAPS across two comment lines, so a plain substring search over the raw source finds
    nothing and the check reads green while the claim is still there — the same one-line-read bug
    the evidence-ladder guard hit. Comment markers and newlines are flattened before matching.
    """
    src = " ".join(ENGINE.read_text(encoding="utf-8").replace("#", " ").split())
    assert "remaining three ship as template files" not in src, (
        "the engine still promises three profiles that ship as template files — no such template "
        "exists anywhere in the tree; delete the claim rather than leave it as an aspiration")


def test_engine_twins_are_identical():
    """M5 — the package bundle must not drift from the canonical engine."""
    for name in ("add.py", "cli.py"):
        a = hashlib.sha256((TOOLING / name).read_bytes()).hexdigest()
        b = hashlib.sha256((BUNDLED / name).read_bytes()).hexdigest()
        assert a == b, f"`{name}` differs between tooling/ and src/add_method/_bundled/tooling/"


def test_refusal_adds_no_floor_or_evidence_kind():
    """R:NEWFLOOR — additivity under test: a profile selects lenses, never what a gate demands."""
    raising = {s for s, a in add.SENSITIVITY_FLOOR.items() if a != "process"}
    assert raising == RAISING, (
        f"the sensitivities that raise the authority floor changed to {sorted(raising)} — a profile "
        f"selects lenses and must never introduce a floor")
    stray = set(add.SENSITIVITY_FLOOR.values()) - set(add.AUTHORITY_ORDER)
    assert not stray, f"sensitivities map to authority values outside AUTHORITY_ORDER: {sorted(stray)}"
    assert add.SENSITIVITY_FLOOR["security"] == "human", \
        "the security floor is no longer human — that floor cannot be traded for any domain"


def test_no_scope_path_is_gitignored():
    """E1 — a gitignored `scope:` entry has no git blob, so its freshness cannot be attested.

    This task edits the engine, and the copy it is DRIVEN by (`.add/tooling/`) is gitignored. Had
    that path been declared in scope, the gate would have been digesting a file git cannot address.
    The rule generalises past this task: scope is the attested surface, so anything in it must be
    something git can address.
    """
    task = REPO.parent / ".add" / "tasks" / "profile-refusal.md"
    lines = task.read_text(encoding="utf-8").splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("scope:"))
    declared = []
    for ln in lines[start + 1:]:
        if not ln.startswith("  - "):
            break
        declared.append(ln[4:].strip())
    assert declared, "the task declares no scope — nothing to check, which is not a pass"

    ignored = [p for p in declared
               if subprocess.run(["git", "check-ignore", "-q", p],
                                 cwd=REPO.parent, capture_output=True).returncode == 0]
    assert not ignored, (
        f"scope declares gitignored paths: {ignored} — freshness digests a git blob, so an ignored "
        f"entry cannot be attested and the gate would be trusting a file git cannot address")
