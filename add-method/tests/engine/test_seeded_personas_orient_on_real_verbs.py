"""A seeded lens orients with commands the engine actually has, or it orients on nothing.

Measured 2026-09-02, running what the shipped persona templates instruct:

    $ python3 .add/tooling/add.py status --all
    (exit 0, NO OUTPUT)          <- add.py is a LIBRARY; the entrypoint is cli.py
    $ python3 .add/tooling/cli.py status --brief
    error: unrecognized arguments: --brief
    $ add graph / add milestone-confirm
    (neither is among the 24 verbs)

Three of the four seeded personas open with an ORIENT command that is either silent or an
error. The silent one is the dangerous shape: a planner lens loads, runs `add.py status --all`,
gets an empty string back, reads it as "clean bundle" and drafts from a guess — which is the
exact failure ORIENT exists to prevent.

The guard is a CENSUS over every shipped persona template, so a lens added later cannot skip it.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
import cli as cli_mod  # noqa: E402

TEMPLATES = REPO / "tooling" / "templates" / "personas"
VERBS = set(cli_mod.build_parser()._subparsers._group_actions[0].choices)

# `add <verb>` and `add.py <verb>` / `cli.py <verb>`, wherever they appear in the prose.
INVOCATION = re.compile(r"(?:\badd\b|add\.py|cli\.py)\s+([a-z][a-z0-9-]*)")


def _templates():
    found = sorted(TEMPLATES.glob("*.md.tmpl"))
    assert found, f"no persona templates found under {TEMPLATES} — the census is broken"
    return found


def test_every_command_a_persona_names_is_a_real_verb():
    """covers: M1, R:PHANTOMVERB — enumerated from the shipped templates, never a hand list."""
    bad, seen = [], 0
    for tmpl in _templates():
        for line in tmpl.read_text(encoding="utf-8").splitlines():
            for verb in INVOCATION.findall(line):
                seen += 1
                if verb in ("py", "add") or verb not in VERBS:
                    if verb in ("py", "add"):
                        continue
                    bad.append(f"{tmpl.name}: `{verb}` is not one of the {len(VERBS)} verbs")
    assert not bad, "seeded personas instruct commands the engine does not have:\n  " + \
                    "\n  ".join(sorted(set(bad)))
    # Its sibling above learned this the hard way: `assert not bad` reports success when the
    # loop that fills `bad` never ran. Tie the floor to the roster, not to a magic number.
    assert seen >= len(_templates()), (
        f"only {seen} invocation(s) found across {len(_templates())} lenses — the census is not "
        f"reading the templates")


def test_no_persona_drives_the_library_instead_of_the_entrypoint():
    """covers: M2, R:SILENTORIENT — `add.py` prints nothing, so orienting on it reads clean."""
    bad = [t.name for t in _templates() if "add.py " in t.read_text(encoding="utf-8")]
    assert not bad, (
        "these personas orient by running `add.py`, which is a LIBRARY and prints nothing — "
        f"an empty result reads as a clean bundle: {bad}")


def test_the_library_really_is_silent(tmp_path):
    """covers: A1 — the premise, executed, so this guard cannot rest on a stale claim."""
    add.init(tmp_path, "code", "T")
    proc = subprocess.run([sys.executable, str(REPO / "tooling" / "add.py"), "status", "--all"],
                          capture_output=True, text=True, cwd=tmp_path.parent)
    assert proc.stdout.strip() == "", (
        f"add.py now prints — this guard's premise has changed: {proc.stdout[:200]!r}")


def test_every_orient_command_runs_clean(tmp_path):
    """covers: M3, E1 — not merely a real verb: the flags must parse too."""
    # `add.init` returns a TUPLE, so `init(...) or tmp_path` bound `root` to the repr of the whole
    # graph dict. Every command then ran against a bundle that does not exist — `status` printed
    # nothing and exited 0, so this check passed VACUOUSLY on every command it was given. It only
    # surfaced on CI, where Path.exists() raises ENAMETOOLONG (3.10/3.12) instead of returning
    # False (3.14): a version-dependent crash standing in for a check that was never running.
    add.init(tmp_path, "code", "T")
    root = tmp_path
    failures, ran = [], 0
    for tmpl in _templates():
        for line in tmpl.read_text(encoding="utf-8").splitlines():
            if "ORIENT on load" not in line:
                continue
            for cmd in re.findall(r"`([^`]*(?:add\.py|cli\.py|\badd\b)[^`]*)`", line):
                argv = cmd.replace("python3", "").replace(".add/tooling/add.py", "") \
                          .replace(".add/tooling/cli.py", "").replace("add ", " ", 1).split()
                if not argv or argv[0] not in VERBS:
                    continue
                proc = subprocess.run(
                    [sys.executable, str(REPO / "tooling" / "cli.py"), "--root", str(root), *argv],
                    capture_output=True, text=True)
                ran += 1
                if proc.returncode != 0 or "unrecognized" in proc.stderr:
                    failures.append(f"{tmpl.name}: `{cmd}` -> {proc.stderr.strip()[:120]}")
    assert not failures, "ORIENT commands that do not run:\n  " + "\n  ".join(failures)
    # The check above passed vacuously for its whole life because `root` pointed at nothing and
    # every command exited 0 against an absent bundle. A check that asserts an empty list must
    # also assert it looked at something.
    # Not a magic number: EVERY seeded lens carries an ORIENT line, so the floor is the roster
    # itself. A new template with no ORIENT line, or one whose command the regex cannot see,
    # fails here rather than quietly shrinking what this guard inspects.
    assert ran >= len(_templates()), (
        f"only {ran} ORIENT command(s) ran across {len(_templates())} seeded lenses — a lens "
        f"carries no ORIENT line, or its command is not in a form this check can execute")
