"""Red suite for `scope-flag-append` — a CLI argument is never silently dropped.

Scratch-build finding (slugline, on the published 3.0.0b2 wheel): `add new Task x
--scope a.py --scope b.py` kept only `b.py` — argparse's plain store means last-wins, and
the first flag vanished without a word. The node shipped with half its freshness set. Both
forms must work and compose: repetition appends in command-line order, and the documented
comma form splits in place.

Driven as dogfood task `.add/tasks/scope-flag-append.md` (v3.0.0 hardening tally #7).
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

CLI = REPO / "tooling" / "cli.py"


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path / ".add", "code", "T")
    return tmp_path / ".add"


def _new_scope(bundle, slug, *scope_args):
    subprocess.run([sys.executable, str(CLI), "--root", str(bundle),
                    "new", "Task", slug, *scope_args], check=True, capture_output=True)
    fm = (bundle / "tasks" / f"{slug}.md").read_text(encoding="utf-8")
    return re.findall(r"^  - (.+)$", fm.split("gives:")[0], re.M)


def test_repeated_scope_flags_append(bundle):
    """covers: M1, R:LASTWINS — two flags, two entries, in order."""
    scope = _new_scope(bundle, "twoflags", "--scope", "a.py", "--scope", "b.py")
    assert scope == ["a.py", "b.py"], \
        f"a repeated --scope silently dropped values: {scope}"


def test_comma_form_still_splits(bundle):
    """covers: M2 — the documented form is untouched."""
    assert _new_scope(bundle, "commas", "--scope", "a.py,b.py") == ["a.py", "b.py"]


def test_mixed_flags_and_commas_compose(bundle):
    """covers: M2, E1 — repetition and commas expand in place."""
    scope = _new_scope(bundle, "mixed", "--scope", "a.py", "--scope", "b.py,c.py")
    assert scope == ["a.py", "b.py", "c.py"], scope


def test_scope_is_the_only_plural_flag(bundle):
    """covers: A1 (probe) — no other `new` flag advertises plural values, so the
    append treatment stays a one-flag decision until a help text says otherwise."""
    out = subprocess.run([sys.executable, str(CLI), "new", "--help"],
                         capture_output=True, text=True).stdout
    plural = [l for l in out.splitlines()
              if re.search(r"comma|paths|multiple", l) and "--scope" not in l]
    assert not plural, f"another plural flag exists — revisit A1: {plural}"
