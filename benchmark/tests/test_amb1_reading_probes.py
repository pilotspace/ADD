"""The reading probes must resolve against apps whose reading is KNOWN.

Six live runs scored `A-priority-vs-fifo` as `neither` — every arm, every rep.
That is not six apps declining to choose; it is a probe that cannot be satisfied.
It required the promoted entry to still be LISTED in the waitlist with
`status == "confirmed"`, and an app that promotes an entry naturally removes it.
Probing rep1/add directly: it promoted `priority: 9` correctly and still scored
`neither`.

`A-position-ordering` had a narrower version of the same disease — it read the
key `position`, and rep0/add reports `waitlist_position`. Same semantics, wrong
spelling, scored `neither` while visibly ordering by priority.

Both are the vacuous-assertion class: a probe whose FALSE branch is unreachable
tells you nothing, and a meter that can only ever say "neither" quietly converts
every run into `guessed_wrong`. The fix is to assert on the OBSERVABLE OUTCOME
(which entry left the queue) rather than on a data-structure residency and a
field name the prompt never fixes.

These reference apps have no ambiguity: each one's reading is chosen by a knob.
A probe that cannot recover a reading it was handed cannot be trusted to report
one it was not.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.workload._oracle_lib import running_app
from benchmark.workload.amb1.ambiguity import AMBIGUITIES

_BY_ID = {a["id"]: a for a in AMBIGUITIES}

# ── reference app ─────────────────────────────────────────────────────────────
# Always resolves the CONTRADICTION as waitlist (otherwise there is no queue to
# observe). Two knobs decide the other two items:
#   ORDERING     — "priority" | "fifo"          -> A-priority-vs-fifo
#   POSITION_KEY — "position" | "waitlist_position" -> A-position-ordering
# Promotion REMOVES the entry from the queue, which is what the old probe could
# not see, and what every live arm actually did.

_APP = '''\
import json, os, uuid
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

ORDERING = "{ordering}"
POSITION_KEY = "{position_key}"
PROMOTE_ALL = {promote_all}

BOOKINGS = {{}}
WAITLIST = {{}}

def _now():
    return datetime.now(timezone.utc)

def _parse(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None

def _conflicts(room, start, end):
    for b in BOOKINGS.values():
        if b["room_id"] != room or b.get("cancelled"):
            continue
        s, e = _parse(b["start_time"]), _parse(b["end_time"])
        if s and e and start < e and s < end:
            return True
    return False

def _order(q):
    if ORDERING == "priority":
        q.sort(key=lambda r: -int(r.get("priority") or 0))
    else:
        q.sort(key=lambda r: r["seq"])
    for i, r in enumerate(q, 1):
        r[POSITION_KEY] = i

class H(BaseHTTPRequestHandler):
    def _send(self, code, payload=None):
        body = json.dumps(payload).encode() if payload is not None else b""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _caller(self):
        return self.headers.get("Authorization", "").replace("Bearer ", "").strip() or "anon"

    def do_GET(self):
        if self.path == "/bookings":
            return self._send(200, [b for b in BOOKINGS.values() if not b.get("cancelled")])
        if self.path.startswith("/rooms/") and self.path.endswith("/waitlist"):
            return self._send(200, WAITLIST.get(self.path.split("/")[2], []))
        if self.path.startswith("/bookings/"):
            b = BOOKINGS.get(self.path.split("/")[-1])
            return self._send(200, b) if b and not b.get("cancelled") else self._send(404, {{}})
        return self._send(404, {{}})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(n) or b"{{}}")
        except Exception:
            return self._send(400, {{}})
        for k in ("title", "start_time", "end_time", "room_id"):
            if k not in data:
                return self._send(400, {{}})
        s, e = _parse(data["start_time"]), _parse(data["end_time"])
        if not s or not e:
            return self._send(400, {{}})
        rec = {{"id": str(uuid.uuid4()), "title": data["title"],
               "start_time": data["start_time"], "end_time": data["end_time"],
               "room_id": data["room_id"], "status": "pending",
               "priority": data.get("priority"), "created_by": self._caller(),
               "seq": len(BOOKINGS) + sum(len(v) for v in WAITLIST.values())}}
        if _conflicts(data["room_id"], s, e):
            q = WAITLIST.setdefault(data["room_id"], [])
            rec["status"] = "waitlisted"
            q.append(rec)
            _order(q)
            return self._send(202, rec)
        BOOKINGS[rec["id"]] = rec
        return self._send(201, rec)

    def do_DELETE(self):
        b = BOOKINGS.get(self.path.split("/")[-1])
        if not b or b.get("cancelled"):
            return self._send(404, {{}})
        start = _parse(b["start_time"])
        if start and start - _now() < timedelta(hours=24):
            return self._send(422, {{}})
        b["cancelled"] = True
        q = WAITLIST.get(b["room_id"]) or []
        if q:
            _order(q)
            n = len(q) if PROMOTE_ALL else 1
            for _ in range(n):
                promoted = q.pop(0)      # LEAVES the queue — the live behaviour
                promoted["status"] = "confirmed"
                BOOKINGS[promoted["id"]] = promoted
            _order(q)
        return self._send(200, b)

    def log_message(self, *a):
        pass

HTTPServer(("127.0.0.1", int(os.environ["PORT"])), H).serve_forever()
'''


def _app(root: pathlib.Path, ordering: str, position_key: str,
         promote_all: bool = False) -> pathlib.Path:
    ws = root / f"{ordering}-{position_key}-{promote_all}"
    pkg = ws / "app"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "__main__.py").write_text(
        _APP.format(ordering=ordering, position_key=position_key,
                    promote_all=promote_all), encoding="utf-8")
    return ws


@pytest.fixture(scope="module")
def apps(tmp_path_factory):
    root = tmp_path_factory.mktemp("amb1probe")
    return {
        "priority": _app(root, "priority", "position"),
        "fifo": _app(root, "fifo", "position"),
        # rep0/add's spelling — same semantics, different key.
        "priority_alias": _app(root, "priority", "waitlist_position"),
        # Promotes the ENTIRE queue on a cancellation: it has expressed no
        # ordering preference, so no reading may be attributed to it.
        "greedy": _app(root, "priority", "position", promote_all=True),
    }


def _readings(item_id: str, ws: pathlib.Path) -> dict[str, bool]:
    """Run every reading of an item against a live app; return {name: bool}.

    A raising probe counts False — the scorer's own rule (`_resolve_shipped`:
    "A raising probe counts as False (fail-closed)"). Demanding exception-free
    probes here would test a contract the scorer does not have.
    """
    item = _BY_ID[item_id]
    out = {}
    with running_app(str(ws)) as base:
        for name, probe in item["readings"].items():
            try:
                out[name] = bool(probe(base, ws))
            except Exception:
                out[name] = False
    return out


def _shipped(item_id: str, ws: pathlib.Path) -> str:
    """Through the scorer's real resolver, not a reimplementation of it."""
    from benchmark.score import _resolve_shipped
    with running_app(str(ws)) as base:
        return _resolve_shipped(_BY_ID[item_id], base, ws)


class TestPriorityGapProbeResolves:
    """R:vacuous_probe — `neither` in 6/6 live runs was the meter, not the apps."""

    def test_priority_ordering_app_reads_as_priority_first(self, apps):
        r = _readings("A-priority-vs-fifo", apps["priority"])
        assert r == {"priority_first": True, "fifo_first": False}, r

    def test_fifo_ordering_app_reads_as_fifo_first(self, apps):
        # The converse. Without it, a probe hard-wired to True would pass above.
        r = _readings("A-priority-vs-fifo", apps["fifo"])
        assert r == {"priority_first": False, "fifo_first": True}, r

    def test_promoted_entry_leaving_the_queue_is_still_observed(self, apps):
        # The exact defect: both reference apps REMOVE the promoted entry, which
        # is what every live arm did and what the old probe could not see.
        for key in ("priority", "fifo"):
            assert any(_readings("A-priority-vs-fifo", apps[key]).values()), \
                f"{key}: promotion is unobservable to the probe"


class TestPositionProbeResolves:
    def test_position_app_reads_as_by_priority(self, apps):
        r = _readings("A-position-ordering", apps["priority"])
        assert r == {"by_priority": True, "by_arrival": False}, r

    def test_arrival_app_reads_as_by_arrival(self, apps):
        r = _readings("A-position-ordering", apps["fifo"])
        assert r == {"by_priority": False, "by_arrival": True}, r

    def test_field_name_does_not_change_the_reading(self, apps):
        # R:field_name_coupling — rep0/add reported `waitlist_position` and was
        # scored `neither` while visibly ordering by priority. The prompt fixes
        # the SEMANTICS of position, never its spelling.
        assert (_readings("A-position-ordering", apps["priority_alias"])
                == _readings("A-position-ordering", apps["priority"]))


class TestStillNonVacuousDownward:
    def test_unreachable_app_resolves_to_no_reading(self, tmp_path):
        # The other direction: a probe that reports a reading for an app that
        # does not exist would make every score meaningless.
        ws = tmp_path / "empty"
        ws.mkdir()
        for item_id in ("A-priority-vs-fifo", "A-position-ordering"):
            assert _shipped(item_id, ws) == "neither", item_id

    def test_scorer_recovers_the_known_reading_end_to_end(self, apps):
        # The probes are only worth fixing if `shipped` changes with them — the
        # unit could resolve while the seam still reported "neither".
        assert _shipped("A-priority-vs-fifo", apps["priority"]) == "priority_first"
        assert _shipped("A-priority-vs-fifo", apps["fifo"]) == "fifo_first"
        assert _shipped("A-position-ordering", apps["priority_alias"]) == "by_priority"

    def test_app_that_promotes_everything_expresses_no_reading(self, apps):
        # R:false_reading — with the exactly-one-promoted guard removed, this app
        # hands back whichever entry happened to be first and that arbitrary
        # priority is published as the arm's decision. Guessing right requires
        # having guessed; draining the queue is not a guess.
        assert _shipped("A-priority-vs-fifo", apps["greedy"]) == "neither"

    def test_no_reading_pair_is_ever_simultaneously_true(self, apps):
        # `shipped` resolves to a single reading; two true readings collapse to
        # "neither" and silently re-creates the bug being fixed here.
        for item_id in ("A-priority-vs-fifo", "A-position-ordering"):
            for key in ("priority", "fifo"):
                r = _readings(item_id, apps[key])
                assert sum(r.values()) <= 1, (item_id, key, r)
