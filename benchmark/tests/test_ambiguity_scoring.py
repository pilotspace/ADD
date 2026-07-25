"""bench-ambiguity-scoring: wiring the ambiguity scorer into score_record.

bench-ambiguity shipped the track and the scorer; nothing called it. A `--family amb`
run would have spawned real agents, spent real money, written valid records, and
computed no ambiguity_surface_rate at all — full price for zero signal on the one
question the track exists to answer.

The design mirrors compute_coverage_detail deliberately: same shape of problem (load a
workload-local module, ONE hermetic boot, per-row probe, fail-closed, emit a detail
artifact), so a second idiom for the same job would be the real cost.

Two properties this suite exists to defend:

WHICH READING SHIPPED IS DECIDED BY PROBE, NEVER BY PROSE. An agent's transcript is
evidence of what it SAID; only the built app is evidence of what it DID. A scorer that
reads the claim is a scorer an agent can talk its way past.

EDIT_POS IS COUNTED IDENTICALLY FOR EVERY ARM. Surfacing must precede the first
code-writing act. Across 118 archived transcripts every arm writes via Write/Edit, but
Bash heredocs are non-zero and ASYMMETRIC (add 23, spec-kit 1) — so counting only
Write/Edit would push the cut-point later for the arm that heredocs and credit it with
surfacing that came after its real first edit. That is self-flattery in the exact
metric the track measures, which is why test_edit_pos_counts_a_bash_heredoc_write is
here.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.score import (
    BenchError,
    _first_code_write_offset,
    _load_ambiguities,
    compute_ambiguity_detail,
)

# ── fixtures: a synthetic amb workload + a bootable app, so nothing here needs
#    an agent, a network, or money ───────────────────────────────────────────────

_APP = '''\
import json, os
from http.server import BaseHTTPRequestHandler, HTTPServer

READING = os.environ.get("READING", "{reading}")

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({{"reading": READING}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a): pass

HTTPServer(("127.0.0.1", int(os.environ["PORT"])), H).serve_forever()
'''

_AMBIGUITY_MOD = '''\
from benchmark.workload._oracle_lib import http_call

def _reading_is(name):
    def probe(base, ws):
        _, body = http_call("GET", f"{base}/x")
        return isinstance(body, dict) and body.get("reading") == name
    return probe

AMBIGUITIES = [
    {"id": "A-one", "klass": "contradiction",
     "anchors": ("cancellation window", "24 hours"),
     "readings": {"alpha": _reading_is("alpha"), "beta": _reading_is("beta")},
     "defensible": "alpha"},
    {"id": "A-two", "klass": "gap",
     "anchors": ("promotion order",),
     "readings": {"alpha": _reading_is("alpha"), "beta": _reading_is("beta")},
     "defensible": "alpha"},
]
'''


@pytest.fixture
def workload(tmp_path, monkeypatch):
    """A synthetic `workload/amb9/` that _load_ambiguities can resolve."""
    import benchmark.score as score

    root = tmp_path / "repo"
    d = root / "benchmark" / "workload" / "amb9"
    d.mkdir(parents=True)
    (d / "__init__.py").write_text("", encoding="utf-8")
    (d / "ambiguity.py").write_text(_AMBIGUITY_MOD, encoding="utf-8")
    monkeypatch.setattr(score, "REPO_ROOT", root)
    return root


def _workspace(tmp_path: pathlib.Path, reading: str) -> pathlib.Path:
    ws = tmp_path / f"ws-{reading}"
    pkg = ws / "app"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "__main__.py").write_text(_APP.format(reading=reading), encoding="utf-8")
    return ws


def _transcript(tmp_path: pathlib.Path, events: list[dict], name="t.jsonl") -> pathlib.Path:
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
    return p


def _assistant(*blocks) -> dict:
    return {"type": "assistant", "message": {"content": list(blocks)}}


def _text(s: str) -> dict:
    return {"type": "text", "text": s}


def _tool(name: str, **inp) -> dict:
    return {"type": "tool_use", "name": name, "input": inp}


# ── M1 · shape ────────────────────────────────────────────────────────────────

class TestDetailShape:
    def test_detail_has_one_row_per_planted_item(self, tmp_path, workload):
        # M1 — in AMBIGUITIES order, so a rate is always explainable item by item.
        ws = _workspace(tmp_path, "alpha")
        tx = _transcript(tmp_path, [_assistant(_text("building"))])
        detail = compute_ambiguity_detail(ws, tx, 9, "amb")
        assert [d["id"] for d in detail] == ["A-one", "A-two"]
        assert {"id", "klass", "shipped", "verdict", "evidence"} <= set(detail[0])


# ── M2 · probe decides, prose does not ────────────────────────────────────────

class TestShippedIsDecidedByProbe:
    def test_shipped_is_decided_by_probe_not_prose(self, tmp_path, workload):
        # M2 — THE ANTI-TALK-YOUR-WAY-PAST TEST. The transcript claims beta; the
        # built app serves alpha. The app wins, or the metric is defeatable by text.
        ws = _workspace(tmp_path, "alpha")
        tx = _transcript(tmp_path, [_assistant(_text("I implemented the beta reading."))])
        detail = compute_ambiguity_detail(ws, tx, 9, "amb")
        assert all(d["shipped"] == "alpha" for d in detail)


# ── M3 · resolution rules ─────────────────────────────────────────────────────

class TestReadingResolution:
    def test_exactly_one_true_probe_resolves_that_reading(self, tmp_path, workload):
        ws = _workspace(tmp_path, "beta")
        tx = _transcript(tmp_path, [_assistant(_text("x"))])
        assert compute_ambiguity_detail(ws, tx, 9, "amb")[0]["shipped"] == "beta"

    def test_zero_true_probes_resolve_neither(self, tmp_path, workload):
        # An app implementing NEITHER reading is credited with neither.
        ws = _workspace(tmp_path, "gamma")
        tx = _transcript(tmp_path, [_assistant(_text("x"))])
        assert compute_ambiguity_detail(ws, tx, 9, "amb")[0]["shipped"] == "neither"

    def test_many_true_probes_resolve_neither(self, tmp_path, workload, monkeypatch):
        # M3 boundary — an app satisfying BOTH readings has not chosen one, so it
        # cannot be credited with a choice. Guessing right requires having guessed.
        import benchmark.score as score
        mod = score._load_ambiguities(9, "amb")
        for row in mod:
            row["readings"] = {"alpha": lambda *_: True, "beta": lambda *_: True}
        monkeypatch.setattr(score, "_load_ambiguities", lambda *a, **k: mod)
        ws = _workspace(tmp_path, "alpha")
        tx = _transcript(tmp_path, [_assistant(_text("x"))])
        assert compute_ambiguity_detail(ws, tx, 9, "amb")[0]["shipped"] == "neither"


# ── M4 · edit_pos, counted identically for every arm ──────────────────────────

class TestEditPos:
    def test_edit_pos_counts_write_and_edit_tool_use(self, tmp_path):
        for tool in ("Write", "Edit"):
            tx = _transcript(tmp_path, [
                _assistant(_text("thinking about it")),
                _assistant(_tool(tool, file_path="app/__main__.py", content="x")),
            ], name=f"{tool}.jsonl")
            assert _first_code_write_offset(tx) > 0, f"{tool} not counted as a code write"

    def test_edit_pos_counts_a_bash_heredoc_write(self, tmp_path):
        # THE FAIRNESS CASE. Archived runs show arms differ here (add 23 heredocs,
        # spec-kit 1). An arm that writes code through Bash must not get a later
        # cut-point — and therefore free surfacing — for using a different tool.
        tx = _transcript(tmp_path, [
            _assistant(_text("planning")),
            _assistant(_tool("Bash", command="cat > app/__main__.py <<'PY'\nprint(1)\nPY")),
        ])
        assert _first_code_write_offset(tx) > 0, "a Bash heredoc write was not counted"

    def test_edit_pos_ignores_a_bash_command_that_writes_nothing(self, tmp_path):
        # The converse: reading files or running tests is not committing to a
        # reading, so it must not close the surfacing window.
        tx = _transcript(tmp_path, [
            _assistant(_tool("Bash", command="python3 -m pytest -q")),
            _assistant(_tool("Read", file_path="app/__main__.py")),
        ])
        assert _first_code_write_offset(tx) == 0, "a non-writing command closed the window"

    def test_edit_pos_identical_for_equivalent_arm_transcripts(self, tmp_path):
        # M4 — the same acts in two arms' tool shapes must both be counted. The
        # OFFSETS differ (different bytes); what must not differ is whether the
        # write registers at all.
        #
        # Both transcripts open with reasoning, as every real one does. That is not
        # decoration: offset 0 is returned BOTH for "no write found" and for "the
        # write is the very first byte", so a write-only fixture cannot distinguish
        # a counted write from an uncounted one. The two cases are equivalent for
        # scoring — nothing can precede offset 0 either way, so neither can score
        # surfaced — but a test must not rest on that collapse.
        lead = _assistant(_text("considering the two readings before writing anything"))
        a = _transcript(tmp_path, [lead, _assistant(_tool(
            "Write", file_path="app/__main__.py", content="x"))], name="a.jsonl")
        b = _transcript(tmp_path, [lead, _assistant(_tool(
            "Bash", command="cat > app/__main__.py <<'PY'\nx\nPY"))], name="b.jsonl")
        assert _first_code_write_offset(a) > 0 and _first_code_write_offset(b) > 0


# ── R · rejects, all fail-closed ──────────────────────────────────────────────

class TestRejects:
    def test_missing_ambiguity_module_raises(self, tmp_path, monkeypatch):
        import benchmark.score as score
        monkeypatch.setattr(score, "REPO_ROOT", tmp_path)
        with pytest.raises(BenchError, match="missing_ambiguity_module"):
            _load_ambiguities(9, "amb")

    def test_malformed_ambiguities_raises(self, tmp_path, monkeypatch):
        import benchmark.score as score
        d = tmp_path / "benchmark" / "workload" / "amb9"
        d.mkdir(parents=True)
        (d / "ambiguity.py").write_text("AMBIGUITIES = [{'id': 'x'}]\n", encoding="utf-8")
        monkeypatch.setattr(score, "REPO_ROOT", tmp_path)
        with pytest.raises(BenchError, match="invalid_ambiguity_row"):
            _load_ambiguities(9, "amb")

    def test_unbootable_workspace_ships_neither_and_does_not_raise(self, tmp_path, workload):
        # Fail-closed: a broken run scores nothing, never crashes the scorer.
        ws = tmp_path / "empty"
        ws.mkdir()
        tx = _transcript(tmp_path, [_assistant(_text("x"))])
        detail = compute_ambiguity_detail(ws, tx, 9, "amb")
        assert all(d["shipped"] == "neither" for d in detail)

    def test_missing_transcript_yields_edit_pos_zero(self, tmp_path):
        # Fail-closed AGAINST crediting surfacing, pinned DIRECTLY.
        #
        # Found by mutation: making this return 10**9 left all 17 tests green,
        # because the only test covering it went through compute_ambiguity_detail,
        # where a missing transcript also yields empty TEXT — so nothing surfaced
        # for a reason that had nothing to do with edit_pos. The clause was in the
        # contract and pinned by nothing. A missing artifact must never be able to
        # open an unbounded surfacing window.
        assert _first_code_write_offset(tmp_path / "nope.jsonl") == 0

    def test_no_write_in_transcript_yields_edit_pos_zero(self, tmp_path):
        # Same fail-closed rule for a transcript that exists but never writes code:
        # an agent that only talked has no window in which to have surfaced.
        tx = _transcript(tmp_path, [_assistant(_text("I thought about it at length"))])
        assert _first_code_write_offset(tx) == 0

    def test_missing_transcript_scores_zero_surfaced(self, tmp_path, workload):
        # The end-to-end consequence of the two above.
        ws = _workspace(tmp_path, "alpha")
        detail = compute_ambiguity_detail(ws, tmp_path / "nope.jsonl", 9, "amb")
        assert all(d["verdict"] != "surfaced" for d in detail)


# ── M5 / M6 · the record, and the promise that wm is untouched ────────────────

class TestScoreRecordWiring:
    def test_score_record_amb_emits_metric_and_detail(self):
        # M5 — the metric and its per-item breakdown travel together, so a rate is
        # never published without the evidence a human would need to audit it.
        import inspect

        import benchmark.score as score
        src = inspect.getsource(score.score_record)
        assert "ambiguity_surface_rate" in src, "score_record never sets the metric"
        assert "ambiguity_detail" in src, "score_record never emits the detail artifact"

    def test_amb_scoring_is_gated_on_the_family(self):
        # M6 — the ambiguity path must be reachable ONLY for the amb family, so wm
        # and hv records cannot grow a key and cannot pay for a boot they don't use.
        import inspect

        import benchmark.score as score
        src = inspect.getsource(score.score_record)
        idx = src.index("ambiguity_surface_rate")
        window = src[max(0, idx - 500):idx]
        assert 'family == "amb"' in window, \
            "ambiguity scoring is not gated on family == 'amb'"

    def test_required_metrics_unchanged(self):
        # M6 — the frozen metric set is the compatibility contract for every
        # archived record. ambiguity_surface_rate is OPTIONAL or old records break.
        from benchmark.schema.run_record import OPTIONAL_METRICS, REQUIRED_METRICS
        assert "ambiguity_surface_rate" not in REQUIRED_METRICS
        assert "ambiguity_surface_rate" in OPTIONAL_METRICS

    def test_wm_record_still_validates_without_the_new_metric(self):
        # M6 — the concrete promise: a wm record carrying none of this still passes.
        from benchmark.schema.run_record import REQUIRED_METRICS, validate
        rec = validate({
            "arm": "add", "wm": 1, "rep": 0, "status": "done",
            "metrics": {k: 0.0 for k in REQUIRED_METRICS},
            "artifacts": {"workspace": "/w", "transcript": "/t", "oracle_report": "/o"},
        })
        assert "ambiguity_surface_rate" not in rec.metrics
