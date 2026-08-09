"""The repo runs the method it ships.

Until 3.0 this repo's own `.add/` was a 2.x/OKF bundle — 817 tracked files the shipped engine
could not even open (`add status` answered "no bundle here"). A project that ships ADD while its
own bundle runs a retired engine is the one claim a reader can check for free, so it is now a test
rather than an intention.

The 2.x bundle was not deleted: it is kept, readable, under `archive/add-2x-bundle/` as the record
of how this repo was built. These checks are about what is CURRENT.

Note the asymmetry with `.gitignore`: `.add/tooling/` and `.add/personas-teacher/` are vendored
and deliberately untracked, so a fresh clone has an `.add/` with no engine in it. Every check here
therefore reads the bundle's own files or drives the engine from `add-method/tooling/` — never
from `.add/tooling/`, which may legitimately be absent.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]      # add-method/
ROOT = REPO.parent                              # the repository root
BUNDLE = ROOT / ".add"
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


def test_the_repo_has_its_own_bundle():
    """covers: M1 — `index.md` is the marker `init` writes and nothing else does."""
    assert (BUNDLE / "index.md").is_file(), \
        "the repo has no ADD bundle of its own — it cannot dogfood a method it does not run"


def _project_title() -> str:
    """The project's name as COMMITTED in its own bundle."""
    fm = (BUNDLE / "PROJECT.md").read_text(encoding="utf-8").split("---", 2)[1]
    return next(line.split(":", 1)[1].strip()
                for line in fm.splitlines() if line.startswith("title:"))


def test_the_shipped_engine_can_read_it():
    """covers: M2 — the whole point: the engine in add-method/ opens the repo's own bundle.

    The header is checked against the bundle's OWN committed `title:`, not against the checkout
    directory name: CI clones into `…/ADD/ADD` while the committed title is `AIDD-Book`, and a
    test that conflates the two asserts a fact about the clone path rather than about the bundle.
    """
    report = add.status(BUNDLE)
    assert "no bundle here" not in report, \
        f"the shipped engine cannot read this repo's own bundle:\n{report}"
    assert report.splitlines()[0].startswith(_project_title()), \
        f"status does not name this project ({_project_title()}):\n{report}"


def test_the_bundle_declares_the_shipped_format_and_engine():
    """covers: M3 — the bundle says it is ABF-1, on the version this package ships."""
    fm = (BUNDLE / "index.md").read_text(encoding="utf-8").split("---", 2)[1]
    assert 'abf_version: "1.3"' in fm, f"the bundle does not declare ABF-1:\n{fm}"
    assert f"engine: {add.ENGINE}" in fm, \
        f"the bundle's engine stamp disagrees with the shipped engine {add.ENGINE}:\n{fm}"


def test_no_retired_2x_residue_in_the_current_bundle():
    """covers: R:OKFRESIDUE — the files that defined the retired bundle must not be back.

    `add_engine/` was the OKF engine tree, `SOUL.md` its seeded persona file, and `state.json` its
    mutable state surface — all three retired by 3.0.
    """
    for residue in ("SOUL.md", "state.json", "PROJECT.md.bak", "tooling/add_engine"):
        assert not (BUNDLE / residue).exists(), \
            f"retired 2.x artefact is back in the current bundle: .add/{residue}"


def test_the_2x_bundle_is_kept_as_a_record():
    """covers: M4 — archived, not destroyed. The history of how this repo was built stays readable."""
    archived = ROOT / "archive" / "add-2x-bundle"
    assert archived.is_dir(), "the 2.x bundle should be archived, not deleted"
    assert (archived / "PROJECT.md").is_file(), "the archived bundle is not intact"
