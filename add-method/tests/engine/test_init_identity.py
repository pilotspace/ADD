"""Red suite for the identity `init` stamps into a fresh bundle.

Two defects, both visible in the very first files `add init` writes — found by initialising a real
bundle for this repo during the 3.0 release prep:

  * `okf_version: "0.2"` — was a stamp of a format nothing read. RE-AIMED by task
    `okf-spec-frontmatter`: the milestone `okf-graph-time` adopts OKF v0.2 for the living specs
    and `doctor` now reads this declaration to report `okf_conformance`, so the stamp is
    deliberate and the guard pins its PRESENCE. The original rule is unchanged — a key nothing
    reads does not belong in a fresh bundle.
  * `name:`/`title:` default to the BUNDLE directory, which is always `.add` in real use (the CLI
    passes `<project>/.add` as root). So every project was called `.add` — in `index.md`, in
    `PROJECT.md`, and in the `add status` header, which renders the Project node's `title:`.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


def _fm(path: Path) -> str:
    return path.read_text(encoding="utf-8").split("---", 2)[1]


def test_a_fresh_bundle_declares_both_formats_it_conforms_to(tmp_path):
    """covers: M1 — a fresh bundle declares ABF-1, and now OKF v0.2 alongside it.

    RE-AIMED, not deleted (task okf-spec-frontmatter, M9). This assertion used to require
    `okf_version` to be ABSENT: it was stripped on 2026-08-08 (baa066ae) because nothing read
    it, and dead metadata that tells a new user their bundle is something it is not is worse
    than no metadata. That reason was sound and the RULE behind it still stands — no key that
    nothing reads. What changed is the premise, not the rule: `doctor` now derives an
    `okf_conformance` finding from this declaration, so the stamp has a reader and the bundle's
    OKF claim is one the engine can be held to.

    The direction is pinned deliberately in both places. A silent re-removal of the stamp fails
    HERE, and a reader silently removed fails at
    `test_spec_okf_frontmatter.py::test_doctor_reports_okf_conformance` — so the stamp and its
    reader cannot drift apart without a red suite.
    """
    add.init(tmp_path, "code", "Demo")
    fm = _fm(tmp_path / "index.md")
    assert "abf_version" in fm, "the bundle must still declare the format it IS"
    assert 'okf_version: "0.2"' in fm, (
        f"init no longer declares OKF conformance — if that is deliberate, `doctor`'s "
        f"okf_conformance reader must go with it:\n{fm}")


def test_the_project_is_named_for_the_project_not_the_bundle_dir(tmp_path):
    """covers: M2 — the default name comes from the project, not from the `.add` dir itself.

    This is how the CLI calls it: root is `<project>/.add`, so reading `root.name` names every
    project on earth `.add`.
    """
    bundle = tmp_path / "my-service" / ".add"
    bundle.mkdir(parents=True)
    add.init(bundle, "code")

    assert "name: my-service" in _fm(bundle / "index.md"), \
        f"index.md is not named for the project:\n{_fm(bundle / 'index.md')}"
    assert "title: my-service" in _fm(bundle / "PROJECT.md"), \
        f"PROJECT.md is not named for the project:\n{_fm(bundle / 'PROJECT.md')}"


def test_an_explicit_title_still_wins(tmp_path):
    """covers: M2 — the derived name is only a DEFAULT; a passed title outranks it everywhere."""
    bundle = tmp_path / "my-service" / ".add"
    bundle.mkdir(parents=True)
    add.init(bundle, "code", "Payments Platform")

    assert "name: Payments Platform" in _fm(bundle / "index.md")
    assert "title: Payments Platform" in _fm(bundle / "PROJECT.md")


def test_status_header_names_the_project(tmp_path):
    """covers: M2 — the user-visible surface: `add status` renders the Project node's title."""
    bundle = tmp_path / "my-service" / ".add"
    bundle.mkdir(parents=True)
    add.init(bundle, "code")

    assert add.status(bundle).splitlines()[0].startswith("my-service"), \
        f"status still heads the report with the bundle dir:\n{add.status(bundle)}"
