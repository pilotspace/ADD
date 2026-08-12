"""Package-root conftest — a partial run says so.

`pytest.ini` already makes a bare `pytest` from this directory collect the whole suite, and its
comment already explains why `tooling/` must stay collectable. None of that helps when someone
runs `pytest add-method/tests/` and reads the green summary as a verdict on everything. That
happened here for a full session: `tests/` was green every time while `tooling/` — 8 checks,
including the ENGINE_MD5 pins CI also runs — was red, and a red branch reached the point of merge
on the strength of it.

Nothing here tries to stop a narrow run. Running one directory while iterating is the right thing
to do most of the time, and an error would only teach people to reach for a suppression flag —
which is precisely what this must not have. It just removes the ambiguity: when the run covered
part of the suite, the last line on screen says which part it didn't.
"""
from __future__ import annotations

from pathlib import Path

PKG = Path(__file__).resolve().parent

# Discovered, never listed. A hand-maintained list of test directories would have omitted
# `tooling/` for the same reason a person does: it does not look like a test directory, it looks
# like the engine's home. Whatever `norecursedirs` excludes (the `eval/` sample project, `.add/`
# bundles left by a dogfood run) is excluded here too, by asking the same config.
_SKIP = {".git", ".add", "node_modules", "build", "dist", "__pycache__", "eval"}

# `eval/fixture/` is a nested sample project the eval driver (`tests/eval/`) copies and runs; its
# tests import `src.calc` relative to their own root and must not be collected here. Anchored to
# THIS directory on purpose: `norecursedirs = eval` matched the basename and swallowed
# `tests/eval` too, and `--ignore=eval` resolves against rootdir, so it stopped applying the
# moment pytest was invoked from the repo root. An absolute path holds from either.
collect_ignore = [str(PKG / "eval")]


def test_roots(pkg: Path = PKG) -> list:
    """Every directory under `pkg` holding a `test_*.py`, sorted for a stable notice."""
    found = set()
    for path in pkg.rglob("test_*.py"):
        rel = path.relative_to(pkg)
        if rel.parts[0] in _SKIP or any(p.startswith(".") for p in rel.parts[:-1]):
            continue
        found.add(path.parent)
    return sorted(found)


def rel(path: Path, pkg: Path = PKG) -> str:
    return path.relative_to(pkg).as_posix()


def _top(path: Path, pkg: Path = PKG) -> str:
    """The top-level root a directory belongs to — `tests/skill` reports under `tests`.

    The notice is about which SUITE went unrun, not which leaf directory. Naming
    `tests/book`, `tests/engine`, `tests/eval` and `tests/skill` separately when someone ran
    `pytest tooling/` would bury the one word they need.
    """
    return path.relative_to(pkg).parts[0]


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Name the suites this run did not reach — after the summary line it qualifies.

    Deliberately not `pytest_sessionfinish`: this hook writes through the terminal reporter, so
    the notice lands with the rest of the report instead of after it.
    """
    collected = getattr(terminalreporter, "_session", None)
    items = getattr(collected, "items", None) if collected else None
    if not items:
        return                      # A4 — a run that collected nothing has a louder problem

    ran = {_top(Path(str(item.fspath)).parent) for item in items}
    known = {_top(root) for root in test_roots()}
    missed = sorted(known - ran)
    if not missed:
        return                      # M4 — silence on a complete run, or nobody reads it

    terminalreporter.write_sep("=", "PARTIAL RUN", yellow=True)
    terminalreporter.write_line(
        f"not collected: {' · '.join(missed)} — this run says nothing about "
        f"{'them' if len(missed) > 1 else 'it'}.")
    terminalreporter.write_line(
        f"full suite:    python3 -m pytest -q      (from {PKG.name}/, what CI runs)")
