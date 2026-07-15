"""Red/green for coverage-scorer (honest-fidelity-meter, frozen §3 v1).

Deterministic `requirement_coverage` replaces the artifact-blind LLM `spec_fidelity`:
a frozen per-WM requirement checklist (1 requirement -> >=1 probe) is run against
the built app; coverage = covered/total, in [0,1], with NO LLM in the metric path.

One test per §2 scenario. App-dependent probes use a minimal WM1 booking-app
fixture served via the entry contract `python -m app`.

Run: python3 -m pytest tests/test_requirement_coverage.py -q
"""
from __future__ import annotations

import json
import pathlib

import pytest

from benchmark import score as score_mod
from benchmark.schema.run_record import (
    OPTIONAL_METRICS,
    REQUIRED_METRICS,
    BenchError,
    validate,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# fixtures — a minimal WM1 booking app (entry contract: python -m app on $PORT)
# --------------------------------------------------------------------------

_WM1_APP = '''
import json, os, re
from http.server import BaseHTTPRequestHandler, HTTPServer

BOOKINGS = {}
NEXT_ID = [1]
STATUSES = {"pending", "confirmed", "cancelled"}


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body):
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_POST(self):
        if self.path != "/bookings":
            return self._send(404, {"error": "not_found"})
        b = self._read_json()
        if not b.get("title") or not b.get("start_time"):
            return self._send(400, {"error": "missing_required_field"})
        dur = b.get("duration_minutes")
        if not isinstance(dur, int) or isinstance(dur, bool) or dur <= 0:
            return self._send(400, {"error": "bad_duration"})
        if b.get("status", "pending") not in STATUSES:
            return self._send(400, {"error": "bad_status"})
        bid = str(NEXT_ID[0]); NEXT_ID[0] += 1
        rec = {"id": bid, "title": b["title"], "start_time": b["start_time"],
               "duration_minutes": dur, "status": b.get("status", "pending")}
        BOOKINGS[bid] = rec
        return self._send(201, rec)

    def do_GET(self):
        if self.path == "/bookings":
            return self._send(200, list(BOOKINGS.values()))
        m = re.fullmatch(r"/bookings/([^/]+)", self.path)
        if m:
            rec = BOOKINGS.get(m.group(1))
            return self._send(200, rec) if rec else self._send(404, {"error": "not_found"})
        return self._send(404, {"error": "not_found"})

    def do_PATCH(self):
        m = re.fullmatch(r"/bookings/([^/]+)", self.path)
        if not m:
            return self._send(404, {"error": "not_found"})
        rec = BOOKINGS.get(m.group(1))
        if not rec:
            return self._send(404, {"error": "not_found"})
        b = self._read_json()
        if "status" in b and b["status"] not in STATUSES:
            return self._send(400, {"error": "bad_status"})
        rec.update({k: v for k, v in b.items() if k in ("title", "start_time", "duration_minutes", "status")})
        return self._send(200, rec)

    def do_DELETE(self):
        m = re.fullmatch(r"/bookings/([^/]+)", self.path)
        if not m:
            return self._send(404, {"error": "not_found"})
        return self._send(200, {}) if BOOKINGS.pop(m.group(1), None) is not None \\
            else self._send(404, {"error": "not_found"})

    def log_message(self, *a):
        pass


def main():
    HTTPServer(("127.0.0.1", int(os.environ["PORT"])), Handler).serve_forever()


if __name__ == "__main__":
    main()
'''

# a CLI so the WM1 "CLI parity" requirement can be probed
_WM1_CLI = '''
import sys, json, urllib.request, os

def main(argv):
    base = os.environ.get("APP_BASE", "http://127.0.0.1:" + os.environ.get("PORT", "0"))
    cmd = argv[0] if argv else ""
    if cmd == "list":
        with urllib.request.urlopen(base + "/bookings") as r:
            print(r.read().decode()); return 0
    return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''


def _write_wm1_app(ws: pathlib.Path, *, with_delete: bool = True, with_cli: bool = True) -> None:
    ws.mkdir(parents=True, exist_ok=True)
    app = _WM1_APP if with_delete else _WM1_APP.replace("def do_DELETE", "def _disabled_DELETE")
    (ws / "app.py").write_text(app)
    if with_cli:
        (ws / "cli.py").write_text(_WM1_CLI)


def _write_record(runs_root: pathlib.Path, arm: str, wm: int, metrics: dict) -> pathlib.Path:
    wm_dir = runs_root / arm / f"wm{wm}"
    ws = wm_dir / "workspace"
    ws.mkdir(parents=True, exist_ok=True)
    rec = {
        "arm": arm, "wm": wm, "rep": 0, "status": "done",
        "metrics": metrics,
        "artifacts": {"workspace": str(ws), "transcript": str(wm_dir / "t.jsonl"),
                      "oracle_report": str(wm_dir / "oracle_report.json")},
    }
    (wm_dir / "record.json").write_text(json.dumps(rec))
    (wm_dir / "t.jsonl").write_text("")
    (wm_dir / "oracle_report.json").write_text(json.dumps(
        {"app_check": {"app_reachable": True, "status": 200}, "isolation_clean": True, "leaks": []}))
    return wm_dir / "record.json"


# --------------------------------------------------------------------------
# Scenario: deterministic coverage from a WM1 checklist   (M2, M5)
# --------------------------------------------------------------------------

def test_deterministic_coverage_from_wm1_checklist(tmp_path):
    ws = tmp_path / "workspace"
    _write_wm1_app(ws)
    first = score_mod.compute_requirement_coverage(ws, 1)
    second = score_mod.compute_requirement_coverage(ws, 1)
    assert 0.0 <= first <= 1.0, first
    assert first == second, f"non-deterministic: {first} != {second}"
    # a correct WM1 app covers every requirement
    assert first == 1.0, f"complete WM1 app should score 1.0, got {first}"


# --------------------------------------------------------------------------
# Scenario: a failing probe lowers coverage, never crashes   (M3)
# --------------------------------------------------------------------------

def test_failing_probe_lowers_coverage_no_crash(tmp_path):
    ws = tmp_path / "workspace"
    _write_wm1_app(ws, with_delete=False)  # DELETE endpoint missing
    cov = score_mod.compute_requirement_coverage(ws, 1)  # must NOT raise
    assert 0.0 <= cov < 1.0, f"a missing DELETE must lower coverage below 1.0, got {cov}"


# --------------------------------------------------------------------------
# Scenario: metric set swapped — old key rejected   (M1, R1)
# --------------------------------------------------------------------------

def test_metric_set_swapped():
    assert "requirement_coverage" in REQUIRED_METRICS
    assert "oracle_pass_rate" in REQUIRED_METRICS
    assert "spec_fidelity" not in REQUIRED_METRICS
    assert "spec_fidelity" not in OPTIONAL_METRICS


def _base_metrics(**over):
    m = {"regression_rate": 0.0, "requirement_coverage": 0.9, "tokens_total": 1.0,
         "cost_usd": 0.1, "context_rot_slope": 0.0, "time_to_first_edit": 1.0,
         "oracle_pass_rate": 1.0}
    m.update(over)
    return m


def test_spec_fidelity_only_record_rejected():
    bad = {"arm": "add", "wm": 1, "rep": 0, "status": "done",
           "metrics": _base_metrics(spec_fidelity=0.9, requirement_coverage=None),
           "artifacts": {"workspace": "w", "transcript": "t", "oracle_report": "o"}}
    del bad["metrics"]["requirement_coverage"]
    bad["metrics"]["spec_fidelity"] = 0.9
    with pytest.raises(BenchError, match="invalid_run_record"):
        validate(bad)


def test_new_metric_record_validates_clean():
    good = {"arm": "add", "wm": 1, "rep": 0, "status": "done",
            "metrics": _base_metrics(),
            "artifacts": {"workspace": "w", "transcript": "t", "oracle_report": "o"}}
    validate(good)  # must not raise


# --------------------------------------------------------------------------
# Scenario: slope over coverage with an archived-record shim   (M4)
# --------------------------------------------------------------------------

def test_slope_shim_reads_archived_spec_fidelity(tmp_path):
    # M4: the WM3+ slope prior-read must read a LEGACY record (spec_fidelity only,
    # no requirement_coverage) leniently — never through the v3-strict validate() —
    # and fall back to spec_fidelity, so a mixed old/new trajectory never KeyErrors.
    runs_root = tmp_path / "runs"
    # WM1 archived: only spec_fidelity (would be REJECTED by validate())
    m1 = {"regression_rate": 0.0, "spec_fidelity": 0.8, "tokens_total": 1.0,
          "cost_usd": 0.1, "context_rot_slope": 0.0, "time_to_first_edit": 1.0}
    _write_record(runs_root, "add", 1, m1)
    _write_record(runs_root, "add", 2, _base_metrics(requirement_coverage=0.9))

    m1_read = score_mod._read_prior_metrics_lenient(runs_root, "add", 1)
    m2_read = score_mod._read_prior_metrics_lenient(runs_root, "add", 2)
    assert score_mod._prior_fidelity_value(m1_read) == 0.8, "legacy spec_fidelity read via shim"
    assert score_mod._prior_fidelity_value(m2_read) == 0.9, "new requirement_coverage read directly"

    # the full trajectory (legacy 0.8, new 0.9, this-WM 0.95) computes a float, no KeyError
    slope = score_mod.compute_context_rot_slope([0.8, 0.9, 0.95])
    assert isinstance(slope, float)


# --------------------------------------------------------------------------
# Scenario: no LLM in the metric path   (After)
# --------------------------------------------------------------------------

def test_no_llm_in_metric_path(tmp_path, monkeypatch):
    runs_root = tmp_path / "runs"
    ws = runs_root / "add" / "wm1" / "workspace"
    _write_wm1_app(ws)
    _write_record(runs_root, "add", 1, _base_metrics())

    def _boom(*a, **k):
        raise AssertionError("judge must not be on the metric path")

    monkeypatch.setattr(score_mod.judge, "judge_fidelity_median", _boom, raising=False)
    rec = score_mod.score_record("add", 1, runs_root=runs_root)
    assert "requirement_coverage" in rec.metrics
    assert "spec_fidelity" not in rec.metrics


# --------------------------------------------------------------------------
# Scenario: malformed checklist rejected   (R2)
# --------------------------------------------------------------------------

def test_malformed_checklist_rejected():
    with pytest.raises(BenchError, match="invalid_checklist"):
        score_mod.validate_checklist([{"id": "x", "description": "no probe"}])


# --------------------------------------------------------------------------
# Scenario: report shows the new column   (M6)
# --------------------------------------------------------------------------

def test_report_shows_requirement_coverage_column():
    from benchmark.report import METRIC_COLUMNS
    assert "requirement_coverage" in METRIC_COLUMNS
    assert "spec_fidelity" not in METRIC_COLUMNS
