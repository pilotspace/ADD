"""Long-horizon survivors (wm3/wm4/wm5) — the wm4–6 scoring prerequisite.

compute_regression_rate_v2 refuses to score wm{k} unless EVERY earlier WM has
workload/wm{j}/oracle/survivors.py (checked before any spawn). The v2 meter
shipped survivors for wm1/wm2 only — extending a campaign to wm4–6 dies with
`regression_run_failed: missing survivors file(s)` at the first wm4 scoring
(live, 2026-07-18, both session modes). These tests pin the wm3/wm4/wm5
survivor files and their two safety rules (wv1 meter lessons):

  - fallback ONLY on 400 (meter defect #5: retrying on a business 409 turned
    a correct rejection into a false regression);
  - room-adaptivity: WM5 makes room_id required and re-scopes overlap
    per-room, so earlier-WM probes must add the SAME room on shape rejection
    for their conflict expectations to survive.

Run: python3 -m pytest benchmark/tests/test_longhorizon_survivors.py
"""
from __future__ import annotations

import importlib.util
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKLOAD = REPO_ROOT / "benchmark" / "workload"


def _load(wm: int):
    path = WORKLOAD / f"wm{wm}" / "oracle" / "survivors.py"
    spec = importlib.util.spec_from_file_location(f"survivors_lh_wm{wm}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_survivors_exist_for_every_wm_below_wm6():
    # wm6 scoring re-runs survivors of wm1..wm5 — all five must exist
    for wm in (1, 2, 3, 4, 5):
        path = WORKLOAD / f"wm{wm}" / "oracle" / "survivors.py"
        assert path.exists(), f"wm{wm} survivors.py missing — wm{wm + 1}+ cannot be scored"
        body = path.read_text()
        assert "test-token-alice" in body, f"wm{wm} survivors must carry the pinned token"
        assert "def test_" in body


def test_longhorizon_survivors_importable_and_sized():
    for wm, floor in ((3, 3), (4, 3), (5, 4)):
        mod = _load(wm)
        count = sum(1 for name in dir(mod) if name.startswith("test_"))
        assert count >= floor, f"wm{wm} survivors expose {count} probes, need >= {floor}"


def test_wm2_create_is_room_adaptive():
    """At WM5+ every create needs room_id; wm2's shape chain (end_time ->
    duration_minutes) dead-ends at 400/400 and false-fails 3 of its 4 probes
    (live: fresh add wm5 scored reg 3/13 on a correct app, 2026-07-18). The
    chain must end with an end_time+room attempt; business statuses still
    return untouched at every step."""
    mod = _load(2)

    calls: list = []

    def fake_room_only(method, url, payload=None, headers=None):
        calls.append(payload)
        return (201, {"id": "1"}) if "room_id" in payload else (400, {"error": "room_id required"})

    mod.http_call = fake_room_only
    status, _ = mod._create("http://x", "test-token-alice", "t",
                            "2028-03-06T09:00:00Z", "2028-03-06T09:30:00Z", 30)
    assert status == 201, "the chain must reach an end_time+room attempt"
    assert "room_id" in calls[-1]

    calls.clear()

    def fake_409(method, url, payload=None, headers=None):
        calls.append(payload)
        return 409, {"error": "overlap"}

    mod.http_call = fake_409
    status, _ = mod._create("http://x", "test-token-alice", "t",
                            "2028-03-06T09:00:00Z", "2028-03-06T09:30:00Z", 30)
    assert status == 409 and len(calls) == 1, "409 still returns untouched, no retries"


def test_wm3_room_fallback_only_on_shape_rejection():
    """The room-adaptive create may retry ONLY on 400; a business-rule status
    (401/403/409) must be returned untouched (meter defect #5 recurrence guard)."""
    mod = _load(3)

    calls: list = []

    def fake_409(method, url, payload=None, headers=None):
        calls.append(payload)
        return 409, {"error": "overlap"}

    mod.http_call = fake_409
    status, _ = mod._create("http://x", "test-token-alice", "t",
                            "2028-06-05T10:00:00Z", "2028-06-05T11:00:00Z", "r1")
    assert status == 409, "a 409 must reach the caller, never trigger a retry"
    assert len(calls) == 1, f"fallback fired on 409: {calls}"

    calls.clear()

    def fake_400_then_created(method, url, payload=None, headers=None):
        calls.append(payload)
        return (400, {"error": "room_id required"}) if len(calls) == 1 else (201, {"id": "1"})

    mod.http_call = fake_400_then_created
    status, _ = mod._create("http://x", "test-token-alice", "t",
                            "2028-06-05T10:00:00Z", "2028-06-05T11:00:00Z", "r1")
    assert status == 201 and len(calls) == 2, "400 must trigger the room fallback"
    assert calls[1].get("room_id") == "r1", "the fallback must add the caller's room"
