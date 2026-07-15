"""Red/green for anatomy-report (token-anatomy milestone, frozen §3 v1).

`render_anatomy(path)` -> a markdown block (per-category tokens + %) and
`compare_arms({label: path})` -> a cross-arm markdown table with a `ceremony%`
column isolating ADD's removable overhead (method_doc + engine_output), plus a
`python -m benchmark.anatomy` CLI (`main(argv)`). Synthetic fixtures with known
sizes make the numbers exactly checkable; one live pass runs the real arms.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from benchmark.anatomy import compare_arms, main, render_anatomy
from benchmark.schema.run_record import BenchError

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


# --- fixture builders (match the real transcript JSONL shape) ------------------

def _assistant(cache_read: int, *, tool=None):
    content = []
    if tool:
        content.append({"type": "tool_use", "id": tool["id"], "name": tool["name"], "input": tool["input"]})
    return {"type": "assistant", "message": {"content": content,
                                             "usage": {"cache_read_input_tokens": cache_read}}}


def _tool_result(tool_use_id: str, content: str):
    return {"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": tool_use_id, "content": content}]}}


def _write_dir(base: pathlib.Path, label: str, *messages) -> pathlib.Path:
    """Write runs/<label>/transcript.jsonl and return the DIRECTORY (CLI arg shape)."""
    d = base / label
    d.mkdir(parents=True, exist_ok=True)
    (d / "transcript.jsonl").write_text("\n".join(json.dumps(m) for m in messages) + "\n")
    return d


def _add_like(base):  # a method-doc read + an add.py bash -> ceremony > 0
    return _write_dir(
        base, "add-v2meter-r0/wm1",
        _assistant(0, tool={"id": "t1", "name": "Read", "input": {"file_path": ".add/PROJECT.md"}}),
        _tool_result("t1", "P" * 4000),
        _assistant(300, tool={"id": "t2", "name": "Bash", "input": {"command": "python3 .add/tooling/add.py status"}}),
        _tool_result("t2", "E" * 4000),
        _assistant(700),
    )


def _speckit_like(base):  # only source IO -> ceremony == 0
    return _write_dir(
        base, "spec-kit-v2meter-r0/wm1",
        _assistant(0, tool={"id": "t1", "name": "Bash", "input": {"command": "python3 -m pytest app"}}),
        _tool_result("t1", "B" * 4000),
        _assistant(500),
    )


# --- M1: render_anatomy is a per-category markdown block -----------------------

def test_render_anatomy_lists_every_category_with_tokens_and_pct(tmp_path):
    d = _add_like(tmp_path)
    md = render_anatomy(d / "transcript.jsonl")
    for cat in ("method_doc", "engine_output", "build_work", "conversation"):
        assert cat in md
    assert "%" in md
    assert "turns" in md
    assert "1,000" in md  # total_cache_read = 300 + 700 (comma-formatted)


# --- M2: compare_arms — a ceremony% table, add>0 & spec-kit==0, input order ----

def test_compare_arms_isolates_ceremony_delta(tmp_path):
    add_d, sk_d = _add_like(tmp_path), _speckit_like(tmp_path)
    table = compare_arms({"add-v2meter-r0/wm1": add_d / "transcript.jsonl",
                          "spec-kit-v2meter-r0/wm1": sk_d / "transcript.jsonl"})
    assert "ceremony%" in table
    assert "add-v2meter-r0/wm1" in table and "spec-kit-v2meter-r0/wm1" in table
    # input order preserved: add row precedes spec-kit row
    assert table.index("add-v2meter-r0/wm1") < table.index("spec-kit-v2meter-r0/wm1")
    # the add row carries a non-zero ceremony%, the spec-kit row a 0.0
    add_row = [ln for ln in table.splitlines() if "add-v2meter-r0/wm1" in ln][0]
    sk_row = [ln for ln in table.splitlines() if "spec-kit-v2meter-r0/wm1" in ln][0]
    # add ceremony = (method_doc+engine_output) is a strict majority here -> > 0
    assert "0.0" not in add_row.split("|")[4]  # ceremony% cell is not 0.0
    assert "0.0" in sk_row


def test_compare_arms_fail_open_on_missing(tmp_path):
    add_d = _add_like(tmp_path)
    table = compare_arms({"add-v2meter-r0/wm1": add_d / "transcript.jsonl",
                          "gone/wm9": tmp_path / "nope" / "transcript.jsonl"})  # missing -> em-dash row
    assert "gone/wm9" in table
    gone_row = [ln for ln in table.splitlines() if "gone/wm9" in ln][0]
    assert "—" in gone_row  # em-dash, never a raise


# --- M3 / R1: the CLI dispatches on argument count ----------------------------

def test_cli_no_args_returns_2(tmp_path, capsys):
    assert main([]) == 2
    err = capsys.readouterr().err
    assert "usage" in err.lower()


def test_cli_one_dir_renders(tmp_path, capsys):
    d = _add_like(tmp_path)
    rc = main([str(d)])  # a DIRECTORY arg -> resolves to <dir>/transcript.jsonl
    out = capsys.readouterr().out
    assert rc == 0
    assert "method_doc" in out and "%" in out


def test_cli_two_dirs_compare(tmp_path, capsys):
    add_d, sk_d = _add_like(tmp_path), _speckit_like(tmp_path)
    rc = main([str(add_d), str(sk_d)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "ceremony%" in out
    assert "add-v2meter-r0/wm1" in out and "spec-kit-v2meter-r0/wm1" in out


def test_cli_single_missing_path_raises(tmp_path):
    with pytest.raises(BenchError, match="anatomy_no_transcript"):
        main([str(tmp_path / "does-not-exist")])


# --- sanity: the REAL arms show ADD's ceremony overhead vs spec-kit ------------

def test_real_arms_quantify_ceremony_overhead(tmp_path):
    add_d = REPO_ROOT / "benchmark" / "runs" / "add-v2meter-r0" / "wm1"
    sk_d = REPO_ROOT / "benchmark" / "runs" / "spec-kit-v2meter-r0" / "wm1"
    if not (add_d / "transcript.jsonl").exists() or not (sk_d / "transcript.jsonl").exists():
        pytest.skip("archived transcripts not present")
    table = compare_arms({"add-v2meter-r0/wm1": add_d / "transcript.jsonl",
                          "spec-kit-v2meter-r0/wm1": sk_d / "transcript.jsonl"})
    add_row = [ln for ln in table.splitlines() if "add-v2meter-r0/wm1" in ln][0]
    sk_row = [ln for ln in table.splitlines() if "spec-kit-v2meter-r0/wm1" in ln][0]
    # ADD's ceremony (method_doc + engine_output) is a large removable share; spec-kit has none
    assert "44." in add_row  # ~44.7% ceremony
    assert "0.0" in sk_row.split("|")[4]  # spec-kit ceremony% == 0.0
