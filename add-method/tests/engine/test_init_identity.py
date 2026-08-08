"""Red suite for the identity `init` stamps into a fresh bundle.

Two defects, both visible in the very first files `add init` writes — found by initialising a real
bundle for this repo during the 3.0 release prep:

  * `okf_version: "0.2"` — a stamp of the retired OKF format, written by the release that retires
    it. Nothing in the engine, the validator, or the skill ever READS it; it is dead metadata that
    tells a new user their 3.0 bundle is an OKF one.
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


def test_a_fresh_bundle_carries_no_retired_okf_stamp(tmp_path):
    """covers: M1 — 3.0 is ABF-1; a fresh bundle must not stamp the retired format's version."""
    add.init(tmp_path, "code", "Demo")
    fm = _fm(tmp_path / "index.md")
    assert "okf_version" not in fm, f"init still stamps the retired OKF version:\n{fm}"
    assert "abf_version" in fm, "the bundle must still declare the format it IS"


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
