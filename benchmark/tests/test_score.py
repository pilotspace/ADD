"""Scenarios: score computes the 5 frozen metrics from artifacts alone
(M1-M10, R1-R7) — hermetic via a fake judge script + fixture records; the
regression-rate real subprocess path (M4) uses a real minimal fixture HTTP
app so `pytest -m regression` genuinely runs against it; R7 monkeypatches
subprocess.run to simulate a collection error (a real one can't be produced
without touching the frozen oracle files)."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import textwrap

import pytest

from benchmark import score as score_mod
from benchmark.schema.run_record import REQUIRED_METRICS, validate

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# fixtures / helpers
# --------------------------------------------------------------------------


def _write_script(tmp_path: pathlib.Path, name: str, body: str) -> pathlib.Path:
    script = tmp_path / name
    script.write_text(textwrap.dedent(body))
    script.chmod(0o755)
    return script


def _fake_judge(tmp_path: pathlib.Path, value: str, name: str = "fake_judge.py") -> list[str]:
    script = _write_script(
        tmp_path,
        name,
        f"""
        #!/usr/bin/env python3
        import sys
        print({value!r})
        """,
    )
    return [sys.executable, str(script)]


def _make_record(
    tmp_path: pathlib.Path,
    runs_root: pathlib.Path,
    arm: str,
    wm: int,
    *,
    status: str = "done",
    tokens_total: float = 4200.0,
    cost_usd: float = 0.31,
    time_to_first_edit: float = 12.5,
    spec_fidelity: float = 0.0,
    regression_rate: float = 0.0,
    context_rot_slope: float = 0.0,
    token_source: str | None = None,
) -> pathlib.Path:
    wm_dir = runs_root / arm / f"wm{wm}"
    workspace_dir = wm_dir / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = wm_dir / "transcript.jsonl"
    transcript_path.write_text("")
    oracle_report_path = wm_dir / "oracle_report.json"
    oracle_report_path.write_text(json.dumps({"app_check": {"app_reachable": True}, "isolation_clean": True, "leaks": []}))

    artifacts = {
        "workspace": str(workspace_dir),
        "transcript": str(transcript_path),
        "oracle_report": str(oracle_report_path),
    }
    if token_source is not None:
        artifacts["token_source"] = token_source

    record = validate(
        {
            "arm": arm,
            "wm": wm,
            "rep": 0,
            "status": status,
            "metrics": {
                "regression_rate": regression_rate,
                "spec_fidelity": spec_fidelity,
                "tokens_total": tokens_total,
                "cost_usd": cost_usd,
                "context_rot_slope": context_rot_slope,
                "time_to_first_edit": time_to_first_edit,
            },
            "artifacts": artifacts,
        }
    )
    record_path = wm_dir / "record.json"
    record_path.write_text(record.to_json())
    return record_path


_APP_PY = '''
import json, os, re
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

BOOKINGS = {}
NEXT_ID = [1]
TOKEN_OWNERS = {"test-token-alice": "alice", "test-token-bob": "bob"}


def _parse_dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _owner_from_auth(headers):
    auth = headers.get("Authorization")
    if not auth:
        return None, False
    token = auth.split(" ", 1)[-1]
    return TOKEN_OWNERS.get(token, token), True


def _public(b):
    return {k: v for k, v in b.items() if not k.startswith("_")}


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
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def do_POST(self):
        if self.path != "/bookings":
            return self._send(404, {"error": "not_found"})
        body = self._read_json()
        title = body.get("title")
        start_time = body.get("start_time")
        if not title or not start_time:
            return self._send(400, {"error": "missing_required_field"})
        owner, _ = _owner_from_auth(self.headers)
        owner = owner or "anonymous"
        start = _parse_dt(start_time)
        if "end_time" in body:
            end = _parse_dt(body["end_time"])
        else:
            duration = body.get("duration_minutes", 0)
            end = start.fromtimestamp(start.timestamp() + duration * 60, tz=timezone.utc)
        for b in BOOKINGS.values():
            if b["owner_id"] == owner and b["status"] != "cancelled":
                if start < b["_end"] and b["_start"] < end:
                    return self._send(409, {"error": "conflict", "conflict_booking_id": b["id"]})
        booking_id = str(NEXT_ID[0])
        NEXT_ID[0] += 1
        record = {
            "id": booking_id, "title": title, "start_time": start_time,
            "end_time": end.isoformat(), "owner_id": owner, "status": "pending",
            "_start": start, "_end": end,
        }
        BOOKINGS[booking_id] = record
        return self._send(201, _public(record))

    def do_GET(self):
        if self.path == "/bookings":
            owner, present = _owner_from_auth(self.headers)
            if not present:
                return self._send(401, {"error": "unauthenticated"})
            result = [_public(b) for b in BOOKINGS.values() if b["owner_id"] == owner]
            return self._send(200, result)
        m = re.fullmatch(r"/bookings/([^/]+)", self.path)
        if m:
            booking = BOOKINGS.get(m.group(1))
            if not booking:
                return self._send(404, {"error": "not_found"})
            return self._send(200, _public(booking))
        return self._send(404, {"error": "not_found"})

    def do_PATCH(self):
        m = re.fullmatch(r"/bookings/([^/]+)", self.path)
        if not m:
            return self._send(404, {"error": "not_found"})
        owner, present = _owner_from_auth(self.headers)
        if not present:
            return self._send(401, {"error": "unauthenticated"})
        booking = BOOKINGS.get(m.group(1))
        if not booking:
            return self._send(404, {"error": "not_found"})
        if booking["owner_id"] != owner:
            return self._send(403, {"error": "forbidden"})
        body = self._read_json()
        new_status = body.get("status")
        if new_status == "cancelled":
            now = datetime.now(timezone.utc)
            if booking["_start"] <= now:
                return self._send(422, {"error": "cancellation_window"})
        booking["status"] = new_status
        return self._send(200, _public(booking))

    def do_DELETE(self):
        m = re.fullmatch(r"/bookings/([^/]+)", self.path)
        if not m:
            return self._send(404, {"error": "not_found"})
        if BOOKINGS.pop(m.group(1), None) is None:
            return self._send(404, {"error": "not_found"})
        return self._send(200, {})

    def log_message(self, format, *args):
        pass


def main():
    port = int(os.environ["PORT"])
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
'''


def _write_fixture_app(workspace_dir: pathlib.Path) -> None:
    (workspace_dir / "app.py").write_text(_APP_PY)


# --------------------------------------------------------------------------
# M1 / R2 - refuses a not-done record
# --------------------------------------------------------------------------


def test_refuses_not_done_record(tmp_path):
    runs_root = tmp_path / "runs"
    record_path = _make_record(tmp_path, runs_root, "add", 1, status="timeout")
    before = record_path.read_bytes()

    with pytest.raises(score_mod.BenchError, match="record_not_done"):
        score_mod.score_record("add", 1, runs_root=runs_root)

    assert record_path.read_bytes() == before


# --------------------------------------------------------------------------
# M2 - token/cost/first-edit validated, not recomputed
# --------------------------------------------------------------------------


def test_validates_tokens_cost_first_edit_unchanged(tmp_path):
    runs_root = tmp_path / "runs"
    record_path = _make_record(
        tmp_path, runs_root, "add", 1, tokens_total=4200.0, cost_usd=0.31, time_to_first_edit=12.5
    )
    judge_cmd = _fake_judge(tmp_path, "0.5")

    score_mod.score_record("add", 1, judge_cmd=judge_cmd, runs_root=runs_root)

    written = json.loads(record_path.read_text())
    assert written["metrics"]["tokens_total"] == 4200.0
    assert written["metrics"]["cost_usd"] == 0.31
    assert written["metrics"]["time_to_first_edit"] == 12.5


def test_unparseable_token_source_surfaced_not_masked(tmp_path):
    runs_root = tmp_path / "runs"
    record_path = _make_record(
        tmp_path, runs_root, "add", 1, tokens_total=0.0, token_source="unparseable"
    )
    judge_cmd = _fake_judge(tmp_path, "0.5")

    score_mod.score_record("add", 1, judge_cmd=judge_cmd, runs_root=runs_root)

    written = json.loads(record_path.read_text())
    assert written["metrics"]["tokens_total"] == 0.0
    assert written["artifacts"]["token_source"] == "unparseable"
    assert "tokens_total" in written["artifacts"].get("metrics_warnings", "")


# --------------------------------------------------------------------------
# M3 - spec_fidelity via injected fake judge
# --------------------------------------------------------------------------


def test_spec_fidelity_via_fake_judge(tmp_path, monkeypatch):
    runs_root = tmp_path / "runs"
    record_path = _make_record(tmp_path, runs_root, "add", 1)
    judge_cmd = _fake_judge(tmp_path, "0.82")

    calls = []
    real_run = subprocess.run

    def _spy_run(argv, **kwargs):
        calls.append(argv)
        return real_run(argv, **kwargs)

    monkeypatch.setattr(score_mod.judge.subprocess, "run", _spy_run)

    score_mod.score_record("add", 1, judge_cmd=judge_cmd, runs_root=runs_root)

    written = json.loads(record_path.read_text())
    assert written["metrics"]["spec_fidelity"] == 0.82
    assert calls, "judge subprocess.run was never invoked"
    for argv in calls:
        assert "claude" not in argv


# --------------------------------------------------------------------------
# M4 - regression_rate computed at WM3 from the marked oracle re-exports
# --------------------------------------------------------------------------


def test_regression_rate_computed_at_wm3(tmp_path):
    runs_root = tmp_path / "runs"
    _make_record(tmp_path, runs_root, "add", 1, status="done", spec_fidelity=0.9)
    _make_record(tmp_path, runs_root, "add", 2, status="done", spec_fidelity=0.75)
    record_path = _make_record(tmp_path, runs_root, "add", 3, spec_fidelity=0.0)

    workspace_dir = runs_root / "add" / "wm3" / "workspace"
    _write_fixture_app(workspace_dir)
    judge_cmd = _fake_judge(tmp_path, "0.6")

    score_mod.score_record("add", 3, judge_cmd=judge_cmd, runs_root=runs_root)

    written = json.loads(record_path.read_text())
    # bench-regression-split: `-m regression` now selects only the 3 shape-
    # independent must-survive tests; the fixture app honors all three.
    assert written["metrics"]["regression_rate"] == pytest.approx(0.0)


def test_regression_rate_counts_must_survive_failures(tmp_path):
    runs_root = tmp_path / "runs"
    _make_record(tmp_path, runs_root, "add", 1, status="done", spec_fidelity=0.9)
    _make_record(tmp_path, runs_root, "add", 2, status="done", spec_fidelity=0.75)
    record_path = _make_record(tmp_path, runs_root, "add", 3, spec_fidelity=0.0)

    workspace_dir = runs_root / "add" / "wm3" / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    # break exactly one must-survive behavior: unauthenticated GET now 200s
    (workspace_dir / "app.py").write_text(
        _APP_PY.replace('self._send(401, {"error": "unauthenticated"})',
                        'self._send(200, [])', 1)
    )
    judge_cmd = _fake_judge(tmp_path, "0.6")

    score_mod.score_record("add", 3, judge_cmd=judge_cmd, runs_root=runs_root)

    written = json.loads(record_path.read_text())
    assert written["metrics"]["regression_rate"] == pytest.approx(1 / 3)


# --------------------------------------------------------------------------
# M5 - regression_rate is 0.0 by definition before WM3
# --------------------------------------------------------------------------


def test_regression_rate_zero_before_wm3(tmp_path, monkeypatch):
    runs_root = tmp_path / "runs"
    record_path = _make_record(tmp_path, runs_root, "add", 1)
    judge_cmd = _fake_judge(tmp_path, "0.5")

    def _boom(*args, **kwargs):
        raise AssertionError("compute_regression_rate must not be invoked for wm1/wm2")

    monkeypatch.setattr(score_mod, "compute_regression_rate", _boom)

    score_mod.score_record("add", 1, judge_cmd=judge_cmd, runs_root=runs_root)

    written = json.loads(record_path.read_text())
    assert written["metrics"]["regression_rate"] == 0.0


# --------------------------------------------------------------------------
# M6 - context_rot_slope computed at WM3 from the 3-point fidelity trend
# --------------------------------------------------------------------------


def test_context_rot_slope_computed_at_wm3(tmp_path):
    runs_root = tmp_path / "runs"
    _make_record(tmp_path, runs_root, "add", 1, status="done", spec_fidelity=0.9)
    _make_record(tmp_path, runs_root, "add", 2, status="done", spec_fidelity=0.75)
    record_path = _make_record(tmp_path, runs_root, "add", 3, spec_fidelity=0.0)

    workspace_dir = runs_root / "add" / "wm3" / "workspace"
    _write_fixture_app(workspace_dir)
    judge_cmd = _fake_judge(tmp_path, "0.6")

    score_mod.score_record("add", 3, judge_cmd=judge_cmd, runs_root=runs_root)

    written = json.loads(record_path.read_text())
    assert written["metrics"]["context_rot_slope"] == pytest.approx(-0.15)


def test_compute_context_rot_slope_pure():
    assert score_mod.compute_context_rot_slope([0.9, 0.75, 0.6]) == pytest.approx(-0.15)


# --------------------------------------------------------------------------
# M7 - context_rot_slope is 0.0 by definition before WM3
# --------------------------------------------------------------------------


def test_context_rot_slope_zero_before_wm3(tmp_path):
    runs_root = tmp_path / "runs"
    record_path = _make_record(tmp_path, runs_root, "add", 2)
    judge_cmd = _fake_judge(tmp_path, "0.5")

    score_mod.score_record("add", 2, judge_cmd=judge_cmd, runs_root=runs_root)

    written = json.loads(record_path.read_text())
    assert written["metrics"]["context_rot_slope"] == 0.0


# --------------------------------------------------------------------------
# M8 - scored write-back preserves the frozen shape
# --------------------------------------------------------------------------


def test_scored_record_still_validates(tmp_path):
    runs_root = tmp_path / "runs"
    record_path = _make_record(tmp_path, runs_root, "add", 1)
    judge_cmd = _fake_judge(tmp_path, "0.5")

    score_mod.score_record("add", 1, judge_cmd=judge_cmd, runs_root=runs_root)

    reloaded = validate(json.loads(record_path.read_text()))
    assert set(reloaded.metrics.keys()) == set(REQUIRED_METRICS)


# --------------------------------------------------------------------------
# M9 - score is idempotent on unchanged artifacts
# --------------------------------------------------------------------------


def test_score_is_idempotent(tmp_path):
    runs_root = tmp_path / "runs"
    record_path = _make_record(tmp_path, runs_root, "add", 1)
    judge_cmd = _fake_judge(tmp_path, "0.5")

    score_mod.score_record("add", 1, judge_cmd=judge_cmd, runs_root=runs_root)
    first = json.loads(record_path.read_text())["metrics"]

    score_mod.score_record("add", 1, judge_cmd=judge_cmd, runs_root=runs_root)
    second = json.loads(record_path.read_text())["metrics"]

    assert first == second


# --------------------------------------------------------------------------
# M10 - WM3 prompt bait assertion is exact (absorbed test, tightened in
# test_workload_prompts.py itself; this test proves the tightening bites).
# --------------------------------------------------------------------------


def test_wm3_bait_assertion_is_exact(tmp_path):
    stripped = REPO_ROOT.joinpath("benchmark", "workload", "wm3", "PROMPT.md").read_text()
    stripped = stripped.replace("duration_minutes", "").replace("end_time", "")
    fixture_dir = tmp_path / "workload" / "wm3"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "PROMPT.md").write_text(stripped)

    lowered = stripped.lower()
    assert "duration_minutes" not in lowered
    assert "end_time" not in lowered
    with pytest.raises(AssertionError):
        assert "duration_minutes" in lowered
        assert "end_time" in lowered


# --------------------------------------------------------------------------
# R1 - unknown record.json path
# --------------------------------------------------------------------------


def test_record_not_found(tmp_path):
    runs_root = tmp_path / "runs"
    with pytest.raises(score_mod.BenchError, match="record_not_found"):
        score_mod.score_record("add", 2, runs_root=runs_root)
    assert not (runs_root / "add").exists()


# --------------------------------------------------------------------------
# R3 - WM3 scored before WM1/WM2 are done
# --------------------------------------------------------------------------


def test_missing_prior_wm_record(tmp_path):
    runs_root = tmp_path / "runs"
    record_path = _make_record(tmp_path, runs_root, "add", 3)
    before = record_path.read_bytes()

    with pytest.raises(score_mod.BenchError, match="missing_prior_wm_record"):
        score_mod.score_record("add", 3, runs_root=runs_root)

    assert record_path.read_bytes() == before


# --------------------------------------------------------------------------
# R4 - invalid WM index
# --------------------------------------------------------------------------


def test_invalid_wm(tmp_path):
    runs_root = tmp_path / "runs"
    with pytest.raises(score_mod.BenchError, match="invalid_wm"):
        score_mod.score_record("add", 4, runs_root=runs_root)
    assert not runs_root.exists()


# --------------------------------------------------------------------------
# R5 - unknown arm
# --------------------------------------------------------------------------


def test_unknown_arm(tmp_path):
    runs_root = tmp_path / "runs"
    with pytest.raises(score_mod.BenchError, match="unknown_arm"):
        score_mod.score_record("ghost", 1, runs_root=runs_root)
    assert not runs_root.exists()


# --------------------------------------------------------------------------
# R6 - judge output is not a parseable float
# --------------------------------------------------------------------------


def test_unparseable_judge_output(tmp_path):
    runs_root = tmp_path / "runs"
    record_path = _make_record(tmp_path, runs_root, "add", 1)
    before = record_path.read_bytes()
    judge_cmd = _fake_judge(tmp_path, "not-a-number")

    with pytest.raises(score_mod.BenchError, match="unparseable_judge_output"):
        score_mod.score_record("add", 1, judge_cmd=judge_cmd, runs_root=runs_root)

    assert record_path.read_bytes() == before


# --------------------------------------------------------------------------
# R7 - regression subprocess itself errors (collection error)
# --------------------------------------------------------------------------


def test_regression_run_failed(tmp_path, monkeypatch):
    runs_root = tmp_path / "runs"
    _make_record(tmp_path, runs_root, "add", 1, status="done", spec_fidelity=0.9)
    _make_record(tmp_path, runs_root, "add", 2, status="done", spec_fidelity=0.75)
    record_path = _make_record(tmp_path, runs_root, "add", 3)
    before = record_path.read_bytes()

    judge_cmd = _fake_judge(tmp_path, "0.6")

    real_run = subprocess.run

    def _fake_run(argv, **kwargs):
        if "pytest" in argv:
            return subprocess.CompletedProcess(argv, returncode=2, stdout="", stderr="ERROR collecting")
        return real_run(argv, **kwargs)

    monkeypatch.setattr(score_mod.subprocess, "run", _fake_run)

    with pytest.raises(score_mod.BenchError, match="regression_run_failed"):
        score_mod.score_record("add", 3, judge_cmd=judge_cmd, runs_root=runs_root)

    assert record_path.read_bytes() == before
