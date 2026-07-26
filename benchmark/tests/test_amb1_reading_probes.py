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
CANCEL_AUTH = "{cancel_auth}"          # "owner" | "anyone"
CANCELLED_VISIBLE = "{cancelled_visible}"   # "listed" | "hidden"
ADJACENCY = "{adjacency}"              # "half_open" | "closed"
LIST_SCOPE = "{list_scope}"            # "all" | "own"
ENVELOPE = {envelope}                   # wrap GET /bookings as {{"bookings": [...]}}

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
        if not s or not e:
            continue
        if ADJACENCY == "closed":
            if start <= e and s <= end:   # touching intervals collide
                return True
        elif start < e and s < end:       # half-open: back-to-back is fine
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
            out = list(BOOKINGS.values())
            if CANCELLED_VISIBLE == "hidden":
                out = [b for b in out if not b.get("cancelled")]
            if LIST_SCOPE == "own":
                out = [b for b in out if b.get("created_by") == self._caller()]
            return self._send(200, {{"bookings": out}} if ENVELOPE else out)
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
        if CANCEL_AUTH == "owner" and b.get("created_by") != self._caller():
            return self._send(403, {{}})
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


_DEFAULTS = {"ordering": "priority", "position_key": "position",
             "promote_all": False, "cancel_auth": "owner",
             "cancelled_visible": "listed", "adjacency": "half_open",
             "list_scope": "all", "envelope": False}


def _app(root: pathlib.Path, name: str, **knobs) -> pathlib.Path:
    settings = {**_DEFAULTS, **knobs}
    ws = root / name
    pkg = ws / "app"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "__main__.py").write_text(_APP.format(**settings), encoding="utf-8")
    return ws


@pytest.fixture(scope="module")
def apps(tmp_path_factory):
    root = tmp_path_factory.mktemp("amb1probe")
    return {
        "priority": _app(root, "priority", ordering="priority"),
        "fifo": _app(root, "fifo", ordering="fifo"),
        # rep0/add's spelling — same semantics, different key.
        "priority_alias": _app(root, "alias", position_key="waitlist_position"),
        # Promotes the ENTIRE queue on a cancellation: it has expressed no
        # ordering preference, so no reading may be attributed to it.
        "greedy": _app(root, "greedy", promote_all=True),
        # The four NEW plants, both ways round. Every knob flipped together, so
        # one app can prove all four probes read what they were handed.
        "strict": _app(root, "strict", cancel_auth="owner", cancelled_visible="hidden",
                       adjacency="closed", list_scope="own"),
        "loose": _app(root, "loose", cancel_auth="anyone", cancelled_visible="listed",
                      adjacency="half_open", list_scope="all"),
        # A live spec-kit build answers {"bookings": [...]}. The prompt says
        # "lists bookings" and never fixes the shape.
        "enveloped": _app(root, "enveloped", cancel_auth="anyone",
                          cancelled_visible="listed", list_scope="all", envelope=True),
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


# ── the four ADDED plants ─────────────────────────────────────────────────────
# Rationale for widening: with three items, two of which every arm resolved the
# same way, the track measured ONE binary per run. n=3 could not separate
# anything. These four are also chosen to fix a design flaw in the original two —
# `A-priority-vs-fifo` and `A-position-ordering` can only resolve under the
# WAITLIST reading of the contradiction, so an arm that reads §2 as authoritative
# gets `neither` for free on both. Each item below resolves under EITHER reading,
# because none of them touches the queue.
#
# None required a PROMPT edit: a gap is by definition something the prompt does
# not say, and the trap is a reading the prompt already invites. The workload the
# archived runs were given is unchanged, so they re-score for free.

NEW_ITEMS = ("A-cancel-authority", "A-cancelled-visibility",
             "A-adjacent-boundary", "A-list-scope")

_STRICT_READINGS = {"A-cancel-authority": "owner_only",
                    "A-cancelled-visibility": "hidden",
                    "A-adjacent-boundary": "closed",
                    "A-list-scope": "own_only"}
_LOOSE_READINGS = {"A-cancel-authority": "anyone",
                   "A-cancelled-visibility": "listed",
                   "A-adjacent-boundary": "half_open",
                   "A-list-scope": "all"}


class TestAddedPlantsExist:
    def test_all_four_are_declared_and_valid(self):
        from benchmark.ambiguity import validate_ambiguities
        validate_ambiguities(AMBIGUITIES)
        for item_id in NEW_ITEMS:
            assert item_id in _BY_ID, item_id

    def test_no_added_anchor_is_a_marker(self):
        # validate_ambiguities enforces this, but the failure it prevents is
        # subtle enough to name: an anchor inside the marker vocabulary marks
        # itself, so a silent run reads as a surfaced one.
        from benchmark.ambiguity import MARKERS
        for item_id in NEW_ITEMS:
            for anchor in _BY_ID[item_id]["anchors"]:
                assert not any(m in anchor.lower() for m in MARKERS), (item_id, anchor)


class TestAddedPlantsResolveBothWays:
    @pytest.mark.parametrize("item_id", NEW_ITEMS)
    def test_strict_app_reads_strict(self, apps, item_id):
        assert _shipped(item_id, apps["strict"]) == _STRICT_READINGS[item_id]

    @pytest.mark.parametrize("item_id", NEW_ITEMS)
    def test_loose_app_reads_loose(self, apps, item_id):
        # The converse of the above. Without both, a probe hard-wired to one
        # reading passes half the suite and reports that reading forever.
        assert _shipped(item_id, apps["loose"]) == _LOOSE_READINGS[item_id]

    @pytest.mark.parametrize("item_id", NEW_ITEMS)
    def test_unreachable_app_resolves_to_neither(self, tmp_path, item_id):
        ws = tmp_path / f"empty-{item_id}"
        ws.mkdir()
        assert _shipped(item_id, ws) == "neither"


@pytest.fixture(scope="module")
def rejecting_app(tmp_path_factory):
    """An app that NEVER waitlists: conflicts are rejected with 409, so no queue
    ever exists. Any item that needs a queue to resolve is invisible here."""
    root = tmp_path_factory.mktemp("amb1reject")
    ws = root / "reject"
    pkg = ws / "app"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    src = _APP.format(**{**_DEFAULTS, "cancel_auth": "anyone",
                         "cancelled_visible": "listed", "list_scope": "all"})
    src = src.replace(
        '''        if _conflicts(data["room_id"], s, e):
            q = WAITLIST.setdefault(data["room_id"], [])
            rec["status"] = "waitlisted"
            q.append(rec)
            _order(q)
            return self._send(202, rec)''',
        '''        if _conflicts(data["room_id"], s, e):
            return self._send(409, {"error": "conflict"})''')
    (pkg / "__main__.py").write_text(src, encoding="utf-8")
    return ws


class TestAddedPlantsAreWaitlistIndependent:
    """The flaw the widening is meant to fix, pinned mechanically.

    An item that only resolves when the app built a waitlist hands `neither` to
    any arm that read §2 (reject with 409) as authoritative — scoring the arm for
    a reading the prompt itself offered."""

    @pytest.mark.parametrize("item_id", NEW_ITEMS)
    def test_added_item_still_resolves_without_a_waitlist(self, rejecting_app, item_id):
        assert _shipped(item_id, rejecting_app) != "neither", (
            f"{item_id} needs a waitlist to resolve — it hands `neither` to every "
            "arm that reads the contradiction as reject-409")

    @pytest.mark.parametrize("item_id", ("A-priority-vs-fifo", "A-position-ordering"))
    def test_original_two_are_the_ones_that_cannot(self, rejecting_app, item_id):
        # Not a bug to fix — a documented limit of those two items, recorded here
        # so the asymmetry is visible rather than folded into an average.
        assert _shipped(item_id, rejecting_app) == "neither"


class TestListingShapeIsNotAReading:
    """R:over_specified_probe, third occurrence in this file.

    rep1 and rep2 of spec-kit answer `GET /bookings` as {"bookings": [...]}. A
    probe requiring a bare JSON array scored BOTH listing items `neither` for
    those runs — reporting "expressed no preference" about an app that expressed
    one plainly. The prompt fixes the semantics of the listing, never its
    serialization, so the envelope must not change any reading.
    """

    @pytest.mark.parametrize("item_id", ("A-cancelled-visibility", "A-list-scope"))
    def test_envelope_does_not_change_the_reading(self, apps, item_id):
        assert _shipped(item_id, apps["enveloped"]) == _shipped(item_id, apps["loose"])

    @pytest.mark.parametrize("item_id", ("A-cancelled-visibility", "A-list-scope"))
    def test_enveloped_app_still_resolves(self, apps, item_id):
        # Equality alone would also hold if BOTH were "neither".
        assert _shipped(item_id, apps["enveloped"]) != "neither"


class TestEnvelopeDoesNotCostCoverage:
    """The clean checklist must not charge an arm for wrapping its list.

    This is the amb1 end-to-end for the 2026-07-26 shape audit: two apps whose
    ONLY difference is `[...]` versus `{"bookings": [...]}` — a serialization the
    PROMPT never fixes — must score identical requirement_coverage.
    """

    def test_enveloped_app_scores_the_same_coverage(self, apps):
        from benchmark.score import compute_requirement_coverage
        bare = compute_requirement_coverage(apps["loose"], 1, "amb")
        wrapped = compute_requirement_coverage(apps["enveloped"], 1, "amb")
        assert bare == wrapped, f"envelope costs coverage: bare={bare} enveloped={wrapped}"
        # Equality alone would hold if both were 0.0 for an unrelated reason.
        assert bare == 1.0, bare
