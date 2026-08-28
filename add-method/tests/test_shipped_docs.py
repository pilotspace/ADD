"""Shipped docs must not advertise verbs the engine does not have.

`README.md` and `GETTING-STARTED.md` ship in BOTH artifacts — the npm `files` whitelist and the
wheel — and the README is the landing copy on both registry pages. After the 3.0 graft the README
still told people to run `add.py migrate` (a verb 3.0 deliberately retired) and `add.py check`,
and GETTING-STARTED still taught the entire 2.x flow: `advance`, `guide`, `new-task`, `stage`.

The book's appendices got a phantom-verb gate in `tests/book/test_appendices.py`; the package's
own docs — the ones a paying consumer actually reads first — never did, so nothing caught it.

The verb list is read from `cli.build_parser()`, the engine's own parser, so this gate cannot
drift from the CLI the way a hand-maintained list would.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / "tooling"))
import cli  # noqa: E402

# `pilotspace-add update` is the INSTALLER's surface, not the engine's — a different CLI with a
# different verb set. It is real; it just is not in build_parser().
INSTALLER_VERBS = {"update"}

# CHANGELOG.md ships too, but naming a retired verb is its entire job ("retired: guide, migrate,
# sync-guidelines"). Gating it would forbid the release notes from describing the release.
SHIPPED_DOCS = ("README.md", "GETTING-STARTED.md")


def _shipped_skill_docs() -> list[str]:
    """Every markdown file under skill/ — the agent-facing instruction surface.

    The doc gate above stopped at the human-facing docs, and the identical defect rode a
    SKILL: persona-author told the agent `add.py check` in five places — a phantom verb on
    a silent-no-op entry point, in an instruction file whose whole purpose is to be
    followed literally. Glob rather than list, so a new skill file is gated the day it
    ships instead of the day someone remembers this test.
    """
    return sorted(str(p.relative_to(PKG)) for p in (PKG / "skill").rglob("*.md"))

# `add.py <verb>` (any path prefix) or a bare `add <verb>` not glued to a package name — so
# `pilotspace-add update`, `@pilotspace/add@latest`, and `marketplace add pilotspace/ADD` do not
# read as engine calls.
VERB_RE = re.compile(r"(?:add\.py|(?<![\w/@-])add)\s+([a-z][a-z-]+)(?![\w/@-])")

# `add.py` followed by anything that reads as a verb. A bare path with no verb after it is
# prose ABOUT the module, not a call, so the architecture table may still name the file.
ADD_PY_CALL_RE = re.compile(r"add\.py\s+[a-z][a-z-]+")


def _engine_verbs() -> set[str]:
    sub = next(a for a in cli.build_parser()._actions if getattr(a, "choices", None)
               and isinstance(a.choices, dict))
    return set(sub.choices)


def _phantoms(rel: str) -> dict[str, list[int]]:
    known = _engine_verbs() | INSTALLER_VERBS
    found: dict[str, list[int]] = {}
    for n, line in enumerate((PKG / rel).read_text(encoding="utf-8").splitlines(), 1):
        for verb in VERB_RE.findall(line):
            if verb not in known:
                found.setdefault(verb, []).append(n)
    return found


def test_the_verb_oracle_is_the_engine_itself():
    """covers: M1 — if this list ever came back empty the gate below would pass vacuously."""
    verbs = _engine_verbs()
    assert {"init", "status", "gate", "freeze"} <= verbs, f"parser introspection broke: {verbs}"
    assert "migrate" not in verbs and "advance" not in verbs, \
        "2.x verbs are back in the parser — this gate assumes 3.0 retired them"


def test_readme_advertises_no_phantom_verbs():
    """covers: M2, E1 — the landing copy on npmjs.com and PyPI."""
    phantoms = _phantoms("README.md")
    assert not phantoms, f"README.md advertises verbs the engine lacks: {phantoms}"


def test_getting_started_advertises_no_phantom_verbs():
    """covers: M2, E2 — the 10-minute quickstart the README links to."""
    phantoms = _phantoms("GETTING-STARTED.md")
    assert not phantoms, f"GETTING-STARTED.md advertises verbs the engine lacks: {phantoms}"


def test_add_py_is_not_an_entry_point():
    """covers: M3 — the premise the gate below rests on, asserted rather than assumed.

    3.0 moved the CLI to `cli.py` and left `add.py` a library module with no `__main__`.
    So `python3 .add/tooling/add.py status` does not error — it exits 0 having printed
    nothing, which is the worst possible shape: a reader cannot tell it from a real run
    that found nothing to say. If add.py ever regains a `__main__`, this fails and the
    gate below should be retired rather than left standing on a stale premise.
    """
    proc = subprocess.run([sys.executable, str(PKG / "tooling" / "add.py"), "status"],
                          capture_output=True, text=True, cwd=PKG)
    assert proc.stdout == "" and proc.returncode == 0, (
        "add.py now dispatches verbs — retire test_shipped_docs_never_invoke_add_py "
        f"(rc={proc.returncode}, stdout={proc.stdout!r})")


def test_shipped_docs_never_invoke_add_py():
    """covers: M3, R:SILENT_NOOP — every runnable line must name the real entry point.

    The phantom gate above cannot catch this class: it checks verb NAMES, and `add.py status`
    names a perfectly real verb. What is wrong is the interpreter target, so it needs its
    own oracle.
    """
    offenders: dict[str, list[int]] = {}
    for rel in SHIPPED_DOCS:
        for n, line in enumerate((PKG / rel).read_text(encoding="utf-8").splitlines(), 1):
            if ADD_PY_CALL_RE.search(line):
                offenders.setdefault(rel, []).append(n)
    assert not offenders, (
        "shipped docs invoke `add.py <verb>`, which exits 0 and prints nothing; "
        f"use `.add/tooling/cli.py` instead: {offenders}")


# Skill prose uses `add` as an ordinary English verb constantly ("you add those yourself",
# "add or sharpen a rule"), so the bare-`add` form only counts INSIDE code — a backtick span
# or a fenced block, the only places a skill states a runnable line. `add.py <verb>` still
# counts anywhere: that spelling is never English.
_CODE_SPANS = re.compile(r"`[^`\n]+`")


def _skill_phantoms(rel: str) -> dict[str, list[int]]:
    known = _engine_verbs() | INSTALLER_VERBS
    found: dict[str, list[int]] = {}
    fenced = False
    for n, line in enumerate((PKG / rel).read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        code = line if fenced else " ".join(_CODE_SPANS.findall(line))
        candidates = VERB_RE.findall(code) + [v for v in VERB_RE.findall(line)
                                              if "add.py" in line]
        for verb in candidates:
            if verb not in known:
                found.setdefault(verb, []).append(n)
    return found


def test_shipped_skills_advertise_no_phantom_verbs():
    """covers: M2, E3 — the instruction files an AGENT follows literally.

    A phantom verb in a skill is worse than one in a README: no human skims it with
    judgment; the agent runs the line as written, gets exit 0 and no output, and reports
    the step done.
    """
    offenders = {rel: ph for rel in _shipped_skill_docs() if (ph := _skill_phantoms(rel))}
    assert not offenders, f"shipped skills advertise verbs the engine lacks: {offenders}"


def test_the_skill_detector_ignores_english_but_catches_code(tmp_path):
    """covers: R:GREENLIE — prose `add those yourself` must not fire; a fenced or
    backticked phantom must."""
    planted = PKG / "skill" / "_gate_probe.md"
    planted.write_text("you add those yourself, then add or sharpen a rule\n"
                       "run `add sharpen` until green\n"
                       "```bash\nadd migrate --all\n```\n", encoding="utf-8")
    try:
        rel = str(planted.relative_to(PKG))
        assert _skill_phantoms(rel) == {"sharpen": [2], "migrate": [4]}
    finally:
        planted.unlink()


def test_shipped_skills_never_invoke_add_py():
    """covers: M3, R:SILENT_NOOP — same oracle as the docs gate, over the skill tree."""
    offenders: dict[str, list[int]] = {}
    for rel in _shipped_skill_docs():
        for n, line in enumerate((PKG / rel).read_text(encoding="utf-8").splitlines(), 1):
            if ADD_PY_CALL_RE.search(line):
                offenders.setdefault(rel, []).append(n)
    assert not offenders, (
        "shipped skills invoke `add.py <verb>`, which exits 0 and prints nothing; "
        f"use `.add/tooling/cli.py` instead: {offenders}")


def test_the_entry_point_detector_finds_a_planted_call(tmp_path):
    """covers: R:GREENLIE — and does not fire on prose that merely names the file."""
    assert ADD_PY_CALL_RE.search("python3 .add/tooling/add.py status")
    assert ADD_PY_CALL_RE.search("resume any session with `add.py status`")
    # A path with no verb after it is describing the file, not calling it — allowed, so that
    # the architecture table can keep listing `.add/tooling/add.py` as the engine module.
    assert not ADD_PY_CALL_RE.search("| `.add/tooling/add.py` | the notary engine |")
    assert not ADD_PY_CALL_RE.search("python3 .add/tooling/cli.py status")


def test_the_detector_finds_a_planted_phantom(tmp_path):
    """covers: R:GREENLIE — a detector that cannot fail is not a gate.

    Mutation check: the regex has to survive the shapes that surround real usage, so prove it
    catches a retired verb while ignoring the installer and plugin lines that merely look alike.
    """
    planted = tmp_path / "README.md"
    planted.write_text(
        "run `python3 .add/tooling/add.py migrate` to convert\n"
        "npx @pilotspace/add@latest update\n"
        "pipx run pilotspace-add update\n"
        "/plugin marketplace add pilotspace/ADD\n"
        "then `add status` to resume\n", encoding="utf-8")

    known = _engine_verbs() | INSTALLER_VERBS
    hits = {v for line in planted.read_text(encoding="utf-8").splitlines()
            for v in VERB_RE.findall(line) if v not in known}
    assert hits == {"migrate"}, \
        f"expected exactly the planted phantom; got {hits} (false positives break the gate)"
