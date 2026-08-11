"""Red suite for `campaign.py` (beta-2, W6) — repetition sets get a first-class record.

The amb1 campaign was aggregated by hand: five run trees, five `record.json`s, and every
mean in FINDINGS-2026-08-10.md computed in a scratch shell. That works exactly once. The
docket item ("the benchmark grows from single probes to full repetition sets; campaign
records stay committed") needs the aggregation to be a program, so the committed record is
reproducible from the run trees by anyone:

  * collect every `record.json` under any number of run roots (rep dirs nest freely);
  * group by arm; per-item verdict tallies across reps; mean/min/max of the headline
    metrics; safe rate = (surfaced + guessed_right) / items;
  * only `status: done` records count — a half-run is not a data point, and skipping it
    silently would be the meter lying, so skipped records are REPORTED in the output;
  * deterministic output (sorted arms, sorted item ids) — a campaign record that diffs
    against itself on re-run is not a record.
"""

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.campaign import aggregate, render_markdown  # noqa: E402


def _record(rep: int, verdicts: dict, *, arm="add", status="done",
            surface_rate=None, cost=1.0) -> dict:
    detail = [{"id": i, "klass": "silent-gap", "shipped": "x", "verdict": v,
               "evidence": "…"} for i, v in sorted(verdicts.items())]
    surfaced = sum(1 for v in verdicts.values() if v == "surfaced")
    return {
        "arm": arm, "wm": 1, "rep": rep, "status": status,
        "metrics": {"ambiguity_surface_rate": (surfaced / len(verdicts))
                    if surface_rate is None else surface_rate,
                    "cost_usd": cost},
        "artifacts": {"ambiguity_detail": json.dumps(detail)},
    }


def _write(root: pathlib.Path, rel: str, record: dict):
    path = root / rel / "record.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record))


@pytest.fixture
def runs(tmp_path):
    """Two reps of `add`, one rep of `vanilla`, one half-run to be reported-not-counted."""
    _write(tmp_path, "rep0/add/amb1",
           _record(0, {"A-who": "surfaced", "A-order": "guessed_wrong"}, cost=2.0))
    _write(tmp_path, "rep1/add/amb1",
           _record(1, {"A-who": "surfaced", "A-order": "guessed_right"}, cost=4.0))
    _write(tmp_path, "rep2/add/amb1",
           _record(2, {"A-who": "surfaced", "A-order": "surfaced"}, status="running"))
    _write(tmp_path, "rep0/vanilla/amb1",
           _record(0, {"A-who": "guessed_wrong", "A-order": "guessed_wrong"},
                   arm="vanilla", cost=0.5))
    return tmp_path


def test_aggregate_groups_by_arm_and_counts_reps(runs):
    """covers: M1 — the campaign is arms × reps, discovered, not configured."""
    campaign = aggregate([runs])
    assert sorted(campaign["arms"]) == ["add", "vanilla"]
    assert campaign["arms"]["add"]["reps"] == 2
    assert campaign["arms"]["vanilla"]["reps"] == 1


def test_per_item_verdicts_tally_across_reps(runs):
    """covers: M2 — the per-item view is the campaign's whole point: which silence
    is surfaced RELIABLY vs once, which reading is wrong EVERY time."""
    items = aggregate([runs])["arms"]["add"]["items"]
    assert items["A-who"] == {"surfaced": 2}
    assert items["A-order"] == {"guessed_wrong": 1, "guessed_right": 1}


def test_metrics_carry_mean_min_max(runs):
    """covers: M3 — a mean without its spread over three reps is a guess with digits."""
    m = aggregate([runs])["arms"]["add"]["metrics"]["ambiguity_surface_rate"]
    assert m["n"] == 2 and m["min"] == 0.5 and m["max"] == 0.5 and m["mean"] == 0.5
    cost = aggregate([runs])["arms"]["add"]["metrics"]["cost_usd"]
    assert cost == {"n": 2, "mean": 3.0, "min": 2.0, "max": 4.0}


def test_safe_rate_counts_surfaced_and_guessed_right(runs):
    """covers: M3 — the blog's own headline stat, computed the same way, by code."""
    assert aggregate([runs])["arms"]["add"]["safe_rate"]["mean"] == 0.75
    assert aggregate([runs])["arms"]["vanilla"]["safe_rate"]["mean"] == 0.0


def test_non_done_records_are_reported_not_counted(runs):
    """covers: M4, R:SILENTSKIP — a half-run is not a data point, and hiding the skip
    would be the meter lying about its own coverage."""
    campaign = aggregate([runs])
    assert campaign["arms"]["add"]["reps"] == 2, "the running rep leaked into the stats"
    assert any("rep2" in s for s in campaign["skipped"]), campaign["skipped"]


def test_markdown_is_deterministic_and_names_the_skips(runs):
    """covers: M5 — a record that diffs against itself on re-run is not a record."""
    one = render_markdown(aggregate([runs]))
    two = render_markdown(aggregate([runs]))
    assert one == two
    assert "A-order" in one and "add" in one and "skipped" in one.lower()


def test_a_note_rides_the_record(runs):
    """covers: M5 — a pooled record over heterogeneous reps NEEDS its caveat in-band;
    a caveat living only in a commit message is a caveat nobody reads."""
    text = render_markdown(aggregate([runs]), note="reps span five engine versions")
    assert "reps span five engine versions" in text


def test_an_empty_tree_is_an_error_not_a_zero(tmp_path):
    """covers: E1 — zero records aggregated to a clean report would be a green lie."""
    with pytest.raises(ValueError):
        aggregate([tmp_path])
