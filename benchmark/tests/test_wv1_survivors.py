"""WV1 meter-defect fixes (v2-wv1-longitudinal TASK.md §3 CONTRACT @ v3; M6, M7)
— found live in rep0 2026-07-10:

Defect 1 (token coupling): wm2's prompt said "a fixed set of valid tokens"
without naming them; the oracle asserts test-token-alice/bob; a compliant app
choosing token-alice scored pass_rate 0.2. Fix: the prompt pins the tokens.

Defect 2 (regression inversion): wholesale re-runs of earlier oracle suites
scored a CORRECT wm2 auth implementation regression=1.0 (wm1's unauthenticated
probes now rightly get 401). Fix: regression re-runs only survivors.py —
auth-carrying, shape-tolerant must-survive invariants per earlier WM.
"""
from __future__ import annotations

import pathlib
import types

import pytest

from benchmark import score as score_mod
from benchmark.schema.run_record import BenchError

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKLOAD = REPO_ROOT / "benchmark" / "workload"

REP0_WM1_WORKSPACE = pathlib.Path.home() / (
    "add-benchmark-archives/2026-07-wv1-campaign/rep0-root/add/wm1/workspace"
)


def _patch_run(monkeypatch, stdout: str, returncode: int, calls: list):
    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        return types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr="")

    monkeypatch.setattr(score_mod.subprocess, "run", fake_run)


def test_regression_v2_runs_survivors_only(monkeypatch):
    calls: list = []
    _patch_run(monkeypatch, "5 passed in 1.0s", 0, calls)
    rate = score_mod.compute_regression_rate_v2(pathlib.Path("/tmp/ws"), 3)
    assert rate == 0.0
    targets = [part for part in calls[0] if "workload" in str(part)]
    assert targets, "no workload paths in the pytest argv"
    for part in targets:
        assert str(part).endswith("survivors.py"), f"non-survivor target: {part}"
    joined = " ".join(str(p) for p in calls[0])
    assert "wm1" in joined and "wm2" in joined and "wm3" not in joined


def test_regression_v2_missing_survivors_raises(monkeypatch):
    calls: list = []
    _patch_run(monkeypatch, "1 passed in 0.1s", 0, calls)
    # wm1..wm5 all carry survivors now (long-horizon extension) — synthesize
    # the gap via a nonexistent family: the meter must fail LOUD before
    # spawning anything, never silently score
    with pytest.raises(BenchError, match="^regression_run_failed"):
        score_mod.compute_regression_rate_v2(pathlib.Path("/tmp/ws"), 5, family="nosuchwm")
    assert not calls, "pytest was spawned despite a missing survivors file"


def test_wm2_prompt_pins_tokens():
    text = (WORKLOAD / "wm2" / "PROMPT.md").read_text()
    assert "test-token-alice" in text, "wm2 prompt must pin the exact token the oracle asserts"
    assert "test-token-bob" in text
    # the wm1/wm3 frozen substring anchors stay intact (test_wm123_untouched's contract)
    assert "duration_minutes" in (WORKLOAD / "wm1" / "PROMPT.md").read_text()
    assert "end_time" in (WORKLOAD / "wm3" / "PROMPT.md").read_text()


def test_survivors_exist_and_send_pinned_token():
    for wm in (1, 2):
        path = WORKLOAD / f"wm{wm}" / "oracle" / "survivors.py"
        assert path.exists(), f"wm{wm} survivors.py missing"
        body = path.read_text()
        assert "test-token-alice" in body, f"wm{wm} survivors must carry the pinned token"
        assert "def test_" in body


def test_survivors_pass_against_own_wm_fixture_shapes():
    # survivors are INVARIANTS: collected by pytest and runnable against any
    # BENCH_WORKSPACE — sanity: both files import + expose >= 3 test fns total
    import importlib.util

    total = 0
    for wm in (1, 2):
        path = WORKLOAD / f"wm{wm}" / "oracle" / "survivors.py"
        spec = importlib.util.spec_from_file_location(f"survivors_wm{wm}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        total += sum(1 for name in dir(mod) if name.startswith("test_"))
    assert total >= 5


def test_survivors_create_fallback_only_on_shape_rejection():
    """Live defect 2026-07-10 (meter defect #5): _create's shape-adaptive
    fallback fired on ANY non-2xx — so an app's CORRECT 409 overlap rejection
    triggered a duration_minutes retry, the wm3 app answered 400 (unknown
    field), and the survivor asserted 400 == 409: every arm scored a false
    regression on a behavior it implemented correctly. The fallback may fire
    ONLY on 400 (shape rejection); business-rule statuses (401/403/409) must
    pass through untouched."""
    import importlib.util

    path = WORKLOAD / "wm2" / "oracle" / "survivors.py"
    spec = importlib.util.spec_from_file_location("survivors_wm2_fallback", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    calls: list = []

    def fake_http_call(method, url, payload=None, headers=None):
        calls.append(payload)
        return 409, {"error": "overlap"}

    mod.http_call = fake_http_call
    status, body = mod._create("http://x", "test-token-alice", "t", "s", "e", 30)
    assert status == 409, "a 409 must be returned to the caller, not retried"
    assert len(calls) == 1, f"fallback fired on 409: {calls}"
    # a real shape rejection (400) still falls back
    calls.clear()

    def fake_http_call_400(method, url, payload=None, headers=None):
        calls.append(payload)
        return (400, {"error": "unknown field"}) if len(calls) == 1 else (201, {"id": "1"})

    mod.http_call = fake_http_call_400
    status, _ = mod._create("http://x", "test-token-alice", "t", "s", "e", 30)
    assert status == 201 and len(calls) == 2, "400 must still trigger the shape fallback"


@pytest.mark.skipif(not REP0_WM1_WORKSPACE.exists(), reason="rep0 archive not on this machine")
def test_live_guard_survivors_green_on_a_real_pre_auth_workspace():
    """Survivors must not false-positive on a NO-AUTH app: the rep0 add wm1
    workspace (pass_rate 1.0, built before auth exists) must score 0.0 on
    wm1 survivors — the auth header is carried but ignored. (The rep0 wm2
    workspace can't serve as the guard: it chose token strings the fixed
    meter now legitimately pins differently — its auth side is proven by the
    pinned-token fixture app in test_score instead.)"""
    rate = score_mod.compute_regression_rate_v2(REP0_WM1_WORKSPACE, 2)
    assert rate == 0.0
