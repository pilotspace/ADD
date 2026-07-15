"""Red/green for anatomy-core (token-anatomy milestone, frozen §3 v1).

`token_anatomy(transcript)` attributes a run's cache-read cost to categories
(method-doc · engine-output · build-work · conversation) by residency-weighting
each message (size x #later turns it stays resident). Synthetic fixtures with
known sizes make the attribution exactly checkable; one sanity pass runs on the
real ADD transcript.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from benchmark.anatomy import token_anatomy
from benchmark.schema.run_record import BenchError

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


# --- fixture builders (match the real transcript JSONL shape) ------------------

def _assistant(cache_read: int, *, tool=None, thinking=""):
    content = []
    if thinking:
        content.append({"type": "thinking", "thinking": thinking})
    if tool:
        content.append({"type": "tool_use", "id": tool["id"], "name": tool["name"], "input": tool["input"]})
    return {"type": "assistant", "message": {"content": content,
                                             "usage": {"cache_read_input_tokens": cache_read,
                                                       "cache_creation_input_tokens": 0,
                                                       "input_tokens": 0, "output_tokens": 0}}}


def _tool_result(tool_use_id: str, content: str):
    return {"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": tool_use_id, "content": content}]}}


def _write(tmp_path, *messages) -> pathlib.Path:
    p = tmp_path / "transcript.jsonl"
    p.write_text("\n".join(json.dumps(m) for m in messages) + "\n")
    return p


# --- M4: tool-aware categorization --------------------------------------------

def test_method_doc_read_lands_in_method_doc(tmp_path):
    t = _write(
        tmp_path,
        _assistant(0, tool={"id": "tu1", "name": "Read", "input": {"file_path": ".add/PROJECT.md"}}),
        _tool_result("tu1", "P" * 4000),   # big method-doc read
        _assistant(500),                    # a later turn -> the read is resident
    )
    a = token_anatomy(t)
    assert a["categories"]["method_doc"] > 0
    assert a["categories"]["method_doc"] == max(a["categories"].values())
    assert a["categories"]["engine_output"] == 0
    assert a["categories"]["build_work"] == 0


def test_add_py_bash_lands_in_engine_output(tmp_path):
    t = _write(
        tmp_path,
        _assistant(0, tool={"id": "tu1", "name": "Bash", "input": {"command": "python3 .add/tooling/add.py status"}}),
        _tool_result("tu1", "E" * 4000),
        _assistant(500),
    )
    a = token_anatomy(t)
    assert a["categories"]["engine_output"] > 0
    assert a["categories"]["engine_output"] == max(a["categories"].values())
    assert a["categories"]["method_doc"] == 0


def test_source_io_lands_in_build_work(tmp_path):
    t = _write(
        tmp_path,
        _assistant(0, tool={"id": "tu1", "name": "Bash", "input": {"command": "python3 -m pytest benchmark/tests"}}),
        _tool_result("tu1", "B" * 4000),
        _assistant(500),
    )
    a = token_anatomy(t)
    assert a["categories"]["build_work"] > 0
    assert a["categories"]["method_doc"] == 0
    assert a["categories"]["engine_output"] == 0


# --- M2: residency weighting (earlier read costs more) -------------------------

def test_earlier_read_outweighs_later_same_size(tmp_path):
    t = _write(
        tmp_path,
        _assistant(0, tool={"id": "tu1", "name": "Read", "input": {"file_path": ".add/PROJECT.md"}}),
        _tool_result("tu1", "M" * 4000),   # method: resident for 2 later turns
        _assistant(100, tool={"id": "tu2", "name": "Edit", "input": {"file_path": "benchmark/score.py"}}),
        _tool_result("tu2", "B" * 4000),   # build: same size, resident for 1 later turn
        _assistant(200),
    )
    a = token_anatomy(t)
    # identical size, earlier residency -> method_doc weight > build_work
    assert a["categories"]["method_doc"] > a["categories"]["build_work"] > 0


# --- M1: attribution sums to the actual cache_read -----------------------------

def test_categories_sum_to_total_cache_read(tmp_path):
    t = _write(
        tmp_path,
        _assistant(0, tool={"id": "tu1", "name": "Read", "input": {"file_path": ".add/PROJECT.md"}}),
        _tool_result("tu1", "M" * 4000),
        _assistant(300, tool={"id": "tu2", "name": "Bash", "input": {"command": "add.py advance"}}),
        _tool_result("tu2", "E" * 4000),
        _assistant(700),
    )
    a = token_anatomy(t)
    assert a["total_cache_read"] == 1000
    assert abs(sum(a["categories"].values()) - a["total_cache_read"]) <= 2  # rounding only
    assert a["attributed_pct"] >= 0.95


# --- M3: deterministic + fault-tolerant ---------------------------------------

def test_deterministic(tmp_path):
    t = _write(
        tmp_path,
        _assistant(0, tool={"id": "tu1", "name": "Read", "input": {"file_path": ".add/PROJECT.md"}}),
        _tool_result("tu1", "M" * 4000),
        _assistant(500),
    )
    assert token_anatomy(t) == token_anatomy(t)


def test_no_usage_transcript_all_zeros(tmp_path):
    p = tmp_path / "transcript.jsonl"
    p.write_text('\n{"type":"system"}\nnot json\n{"type":"user","message":{"content":[]}}\n')
    a = token_anatomy(p)  # must NOT raise
    assert a["total_cache_read"] == 0
    assert a["turns"] == 0
    assert all(v == 0 for v in a["categories"].values())


# --- R1: missing transcript fails loud ----------------------------------------

def test_missing_transcript_raises(tmp_path):
    with pytest.raises(BenchError, match="anatomy_no_transcript"):
        token_anatomy(tmp_path / "nope.jsonl")


# --- sanity: the REAL ADD transcript attributes cleanly ------------------------

def test_real_add_transcript_attributes_ceremony(tmp_path):
    real = REPO_ROOT / "benchmark" / "runs" / "add-v2meter-r0" / "wm1" / "transcript.jsonl"
    if not real.exists():
        pytest.skip("archived transcript not present")
    a = token_anatomy(real)
    assert a["turns"] > 50
    assert a["total_cache_read"] > 1_000_000
    assert a["attributed_pct"] >= 0.95
    # ADD's ceremony surfaces are actually present in the attribution
    assert a["categories"]["method_doc"] > 0
    assert a["categories"]["engine_output"] > 0
