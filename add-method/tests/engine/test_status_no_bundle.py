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


def _legacy_bundle(tmp_path):
    """A 2.5-shaped bundle: `state.json` + `tasks/<slug>/PLAN.md`, neither of which 3.0 writes."""
    legacy = tmp_path / "legacy"
    (legacy / "tasks" / "checkout").mkdir(parents=True)
    (legacy / "state.json").write_text('{"stage": "mvp"}', encoding="utf-8")
    (legacy / "tasks" / "checkout" / "PLAN.md").write_text("# Checkout\n", encoding="utf-8")
    return legacy


def test_status_names_a_2x_bundle_rather_than_denying_it(tmp_path):
    """covers: M2, E1 — a 2.x bundle is not "no bundle"; saying so reads as data loss.

    2.x wrote `state.json` and `tasks/<slug>/PLAN.md`; 3.0 reads `index.md` + `graph.json` and
    retired the `migrate` verb, so the upgrade is a deliberate clean break. The engine has to SAY
    that. Upgrading 2.5 → 3.0 and being told "no bundle here — run `add init`" while your own
    state.json sits in the same directory reads as "the upgrade ate my project".
    """
    out = add.status(_legacy_bundle(tmp_path))
    low = out.lower()
    assert "2.x" in low, f"a 2.x bundle must be named as one:\n{out}"
    assert "no bundle here" not in low, f"their work is right there — do not deny it:\n{out}"
    assert "untouched" in low or "deleted" in low, \
        f"say the 2.x files are safe, or the message reads as data loss:\n{out}"
    assert out.strip().splitlines()[-1].lower().startswith("next:"), \
        f"every orientation ends in a runnable next: line:\n{out}"


def test_a_truly_empty_dir_is_still_plain_no_bundle(tmp_path):
    """covers: E2 — the 2.x branch must not swallow the ordinary bundle-less case."""
    out = add.status(tmp_path / "nowhere")
    assert "2.x" not in out.lower(), f"an empty dir is not a 2.x bundle:\n{out}"


def test_status_on_a_real_bundle_is_unchanged(tmp_path):
    """A real (initialised) bundle still orients normally — the guard only fires when absent."""
    add.init(tmp_path, "code", "T")
    out = add.status(tmp_path)
    assert "nodes" in out and out.strip().splitlines()[-1].lower().startswith("next:")
