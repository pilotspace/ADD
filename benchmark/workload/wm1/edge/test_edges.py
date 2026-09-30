"""WM1 edge suite — HELD OUT. Behaviour wm1/PROMPT.md implies ("`duration_minutes` (positive
integer, required)", "`status` (one of …)", "`start_time` (ISO-8601 string)", 400 on a bad payload,
404 on an unknown id) but the visible oracle never checks. Scored as its own dimension
(benchmark/quality.py edge_robustness), never folded into oracle_pass_rate. Never visible to an arm.
"""
import json
import os
import urllib.error
import urllib.request

import pytest

from benchmark.workload._oracle_lib import http_call, running_app

GOOD = {"title": "Standup", "start_time": "2026-08-01T09:00:00Z", "duration_minutes": 30}


@pytest.fixture(scope="module")
def base():
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    with running_app(ws) as url:
        yield url


def _raw(method: str, url: str, raw: bytes) -> int:
    req = urllib.request.Request(url, data=raw, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, ConnectionError, OSError):
        return 599  # the app dropped the connection: counted as a server failure


def _create(base, **over):
    status, body = http_call("POST", f"{base}/bookings", {**GOOD, **over})
    return status, body


def test_malformed_json_is_400(base):
    assert _raw("POST", f"{base}/bookings", b"{not json") == 400


def test_non_object_body_is_400(base):
    assert _raw("POST", f"{base}/bookings", json.dumps([GOOD]).encode()) == 400


@pytest.mark.parametrize("bad", [0, -5, "30", 30.5, True], ids=["zero", "negative", "string", "fraction", "bool"])
def test_duration_must_be_a_positive_integer(base, bad):
    assert _create(base, duration_minutes=bad)[0] == 400


def test_unknown_status_is_400_on_create(base):
    assert _create(base, status="done")[0] == 400


def test_non_iso_start_time_is_400(base):
    assert _create(base, start_time="tomorrow at nine")[0] == 400


def test_non_string_title_is_400(base):
    assert _create(base, title=123)[0] == 400


def test_invalid_patch_is_400_and_changes_nothing(base):
    status, body = _create(base)
    assert status in (200, 201)
    bid = body["id"]
    assert http_call("PATCH", f"{base}/bookings/{bid}", {"duration_minutes": -1})[0] == 400
    assert http_call("PATCH", f"{base}/bookings/{bid}", {"status": "done"})[0] == 400
    status, fetched = http_call("GET", f"{base}/bookings/{bid}")
    assert status == 200 and fetched["duration_minutes"] == 30 and fetched["status"] == "pending"


def test_deleted_booking_is_gone(base):
    bid = _create(base)[1]["id"]
    assert http_call("DELETE", f"{base}/bookings/{bid}")[0] in (200, 202, 204)
    assert http_call("GET", f"{base}/bookings/{bid}")[0] == 404
    assert http_call("DELETE", f"{base}/bookings/{bid}")[0] == 404


def test_ids_are_distinct(base):
    ids = {_create(base, title=f"t{i}")[1]["id"] for i in range(5)}
    assert len(ids) == 5


@pytest.mark.parametrize("raw", [b"null", b"123", b'"text"', b"{}", b'{"title": null}', b"\xff\xfe"],
                         ids=["null", "number", "string", "empty", "null-title", "not-utf8"])
def test_garbage_never_5xx(base, raw):
    assert _raw("POST", f"{base}/bookings", raw) < 500
