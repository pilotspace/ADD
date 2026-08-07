"""`add status` distinguishes "no bundle here" from "an empty bundle" (field-report finding #2).

The skill tells an agent to run `status` first, every session. On a directory that has no bundle yet,
the honest answer is "no bundle — run `add init`", not the normal empty-orientation `next: add new
milestone` — which sends a cold agent building scope before a bundle exists. `index.md` is the marker.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def test_status_on_no_bundle_points_to_init(tmp_path):
    """covers: M1 — a dir with no index.md is told to run add init."""
    out = add.status(tmp_path / "nowhere")  # never initialised
    assert "init" in out.lower(), f"a bundle-less dir must be pointed at `add init`, got:\n{out}"


def test_status_on_no_bundle_is_not_false_empty(tmp_path):
    """covers: R:FALSEEMPTY — it must not emit the normal empty-bundle orientation."""
    out = add.status(tmp_path / "nowhere")
    assert "new milestone" not in out, "no bundle must not read as an empty, ready bundle"


def test_status_on_a_real_bundle_is_unchanged(tmp_path):
    """A real (initialised) bundle still orients normally — the guard only fires when absent."""
    add.init(tmp_path, "code", "T")
    out = add.status(tmp_path)
    assert "nodes" in out and out.strip().splitlines()[-1].lower().startswith("next:")
