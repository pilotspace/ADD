"""AMB1 edge suite — HELD OUT. Only behaviour amb1/PROMPT.md states outright and that holds under
every reading of its planted ambiguities: typed fields (ISO times, "an optional integer
`priority`"), a request missing a field is 400, an unknown booking is 404, and a server that never
answers garbage with a 5xx. Nothing here touches waitlist order, cancel authority, cancelled
visibility, list scope or the conflict response (see ../oracle/test_amb1_clean.py). Scored as its
own dimension (benchmark/quality.py edge_robustness). Never visible to an arm.
"""
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

import pytest

from benchmark.workload._oracle_lib import http_call, running_app

ALICE = {"Authorization": "Bearer test-token-alice"}


def _iso(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _body(**over) -> dict:
    body = {"title": "Standup", "start_time": _iso(72), "end_time": _iso(73), "room_id": "edge-room"}
    body.update(over)
    return body


@pytest.fixture(scope="module")
def base():
    ws = os.environ.get("BENCH_WORKSPACE")
    if not ws:
        pytest.fail("BENCH_WORKSPACE not set")
    with running_app(ws) as url:
        yield url


def _raw(url: str, raw: bytes) -> int:
    req = urllib.request.Request(url, data=raw, method="POST",
                                 headers={"Content-Type": "application/json", **ALICE})
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, ConnectionError, OSError):
        return 599  # the app dropped the connection: counted as a server failure


def _create(base, **over):
    return http_call("POST", f"{base}/bookings", _body(**over), ALICE)


def test_malformed_json_is_400(base):
    assert _raw(f"{base}/bookings", b"{not json") == 400


def test_non_object_body_is_400(base):
    assert _raw(f"{base}/bookings", json.dumps([_body()]).encode()) == 400


@pytest.mark.parametrize("bad", ["high", 1.5, True], ids=["string", "fraction", "bool"])
def test_priority_must_be_an_integer(base, bad):
    assert _create(base, priority=bad, room_id=f"edge-prio-{bad}")[0] == 400


@pytest.mark.parametrize("field", ["start_time", "end_time"])
def test_non_iso_time_is_400(base, field):
    assert _create(base, **{field: "next tuesday", "room_id": f"edge-time-{field}"})[0] == 400


def test_delete_unknown_booking_is_404(base):
    assert http_call("DELETE", f"{base}/bookings/no-such-booking", None, ALICE)[0] == 404


def test_ids_are_distinct(base):
    ids = set()
    for i in range(4):
        status, body = _create(base, room_id=f"edge-distinct-{i}")
        assert status in (200, 201), body
        ids.add(body["id"])
    assert len(ids) == 4


@pytest.mark.parametrize("raw", [b"null", b"123", b"{}", b'{"title": null}', b"\xff\xfe"],
                         ids=["null", "number", "empty", "null-title", "not-utf8"])
def test_garbage_never_5xx(base, raw):
    assert _raw(f"{base}/bookings", raw) < 500
