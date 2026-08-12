"""A test run that covered part of the suite must not look like one that covered all of it.

Across a whole session I reported "suite green" from `pytest add-method/tests/` while
`add-method/tooling/` — 8 checks, including the `ENGINE_MD5` pins that CI also runs — was RED.
Every green was true of the suite I ran and silent about the one I did not, and a red branch
reached the point of merge on that basis.

The repo was not at fault. `pytest.ini` already makes a bare `pytest` from the package root
collect all of it, and its comment already explains why `tooling/` must stay collectable. Nothing
here can stop someone typing a narrower command, and nothing should: running one directory while
iterating is the correct thing to do most of the time. What can be fixed is the *ambiguity* — a
partial run now names what it missed, right underneath the summary line that would otherwise be
read as a verdict on the whole suite.

Two design choices worth defending:

1. **The notice never fails the run** (M2). An error would teach people to reach for a suppression
   flag, and a suppression flag is the one thing this must not have (R:GAGGED) — the failure mode
   is somebody finding it inconvenient.
2. **Roots are discovered, never listed** (R:PINNED). A hand-maintained list of test directories
   would have omitted `tooling/` for exactly the reason I did: it does not look like a test
   directory, it looks like the engine's home.

E1 is the subtle one. This guard runs inside the suite it measures, so asking "did this session
collect everything?" would pass trivially whenever the full suite is what ran it. Reachability is
therefore established by asking a fresh collector what a BARE run would collect — a separate
process, with no knowledge of how the current one was invoked.
"""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[2]
CONFTEST = PKG / "conftest.py"


def _root_conftest():
    """Load the package-root conftest BY PATH, under a name that cannot collide.

    A plain `import conftest` works when this file is run alone and silently resolves to
    `tests/engine/conftest.py` on a full run — pytest has already put that one in `sys.modules`
    under the bare name `conftest`. The symptom was an AttributeError 700 tests in, on a check
    that passed in isolation. Which is, with some irony, the same class of mistake this whole
    task is about: a narrow run agreeing with you and a full run not.
    """
    spec = importlib.util.spec_from_file_location("add_root_conftest", CONFTEST)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _bare_collect() -> str:
    """What a bare `pytest` from the package root collects — a fresh process, not this session."""
    return subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q"],
                          cwd=PKG, capture_output=True, text=True).stdout


def test_every_test_root_is_reachable_from_a_bare_run():
    """covers: M3, E1, R:PINNED — discovered from the tree, verified against a fresh collector."""
    conftest = _root_conftest()

    roots = conftest.test_roots(PKG)
    assert roots, "root discovery found no test directories at all — it is not looking where it should"
    assert any(r.name == "tooling" for r in roots), (
        "discovery missed `tooling/` — the directory whose invisibility this task exists to fix. "
        "It holds test_tree_parity.py and does not look like a test directory, which is the point")

    collected = _bare_collect()
    unreachable = [conftest.rel(r, PKG) for r in roots
                   if f"{conftest.rel(r, PKG)}/" not in collected]
    assert not unreachable, (
        f"these test roots exist but a bare `pytest` from {PKG.name}/ does not collect them: "
        f"{unreachable} — a suite nothing runs is a suite nothing proves. Either it belongs in the "
        f"run, or it belongs in `norecursedirs` with the reason written down, as `eval/` is.")


def test_partial_run_names_what_it_missed():
    """covers: M1, A6 — the reader believes they just ran everything; tell them what they didn't."""
    out = subprocess.run([sys.executable, "-m", "pytest", "tests/skill", "-q",
                          "--collect-only"],
                         cwd=PKG, capture_output=True, text=True).stdout

    assert "PARTIAL RUN" in out, (
        f"a run restricted to tests/skill printed no notice — this is the exact shape of the run "
        f"that reported green all session while tooling/ was red. Output tail:\n{out[-600:]}")
    assert "tooling" in out.split("PARTIAL RUN", 1)[1], (
        "the notice fired but did not name `tooling/` — a count tells the reader less than a name, "
        "and the whole point is that they can act on it")
    assert re.search(r"pytest\b", out.split("PARTIAL RUN", 1)[1]), (
        "the notice names what was missed but not the command that would cover it — 'you missed "
        "something' without 'run this' is a message that gets learned and then skipped")


def test_full_run_prints_no_notice():
    """covers: M4 — a notice that appears every time is one nobody reads."""
    out = subprocess.run([sys.executable, "-m", "pytest", "-q", "--collect-only"],
                         cwd=PKG, capture_output=True, text=True).stdout
    assert "PARTIAL RUN" not in out, (
        "the complete run still printed the partial-run notice — it would be noise within a day, "
        f"and noise is how a real warning gets ignored. Output tail:\n{out[-600:]}")


def test_notice_has_no_off_switch():
    """covers: R:GAGGED, M2 — the one thing it must survive is being found inconvenient."""
    src = CONFTEST.read_text(encoding="utf-8")

    gated = [m for m in re.findall(r"os\.environ[^\n]*|getenv\([^\n]*|addoption\([^\n]*", src)
             if "PARTIAL" in src[max(0, src.find(m) - 400):src.find(m) + 400].upper()]
    assert not gated, (
        f"the notice is gated on something that can be switched off: {gated} — a warning with an "
        f"off switch is a warning that will be off")

    # M2: emission must not change the outcome. A partial collect-only run still exits clean.
    proc = subprocess.run([sys.executable, "-m", "pytest", "tests/skill", "-q", "--collect-only"],
                          cwd=PKG, capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    assert proc.returncode == 0, (
        f"a partial run exited {proc.returncode} — the notice is meant to inform, never to fail. "
        f"Making it an error is what teaches people to silence it.")
