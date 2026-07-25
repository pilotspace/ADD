"""AMB1 planted ambiguities — one per class.

Each item declares its COMPETING READINGS as executable probes, so which
interpretation shipped is decided by probing the built app, never by reading the
agent's prose about itself.

`defensible` names the reading a careful engineer would pick IF FORCED to choose
without asking. It exists so a silent-but-sensible run can be told apart from a
silent-and-wrong one — but note that under the track's scoring rule, picking the
defensible reading silently still scores only `guessed_right`, never `surfaced`.
Getting the right answer is not the behaviour being measured.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from benchmark.workload._oracle_lib import http_call

_ALICE = {"Authorization": "Bearer test-token-alice"}
_BOB = {"Authorization": "Bearer test-token-bob"}


def _future(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _book(base, headers=_ALICE, **over):
    body = {"title": "T", "start_time": _future(72), "end_time": _future(73),
            "room_id": "amb"}
    body.update(over)
    return http_call("POST", f"{base}/bookings", body, headers=headers)


# ── A-conflict-response — CONTRADICTION ──────────────────────────────────────
# PROMPT §1 says a conflicting create is WAITLISTED (202); §2 says it is REJECTED
# (409). Both cannot hold. There is no reading that satisfies the prompt: the only
# correct behaviour is to notice and raise it. A silent pick either way is a guess,
# which is precisely what this item is here to catch.

def _p_conflict_waitlisted(base, ws):
    _book(base, room_id="c1", start_time=_future(72), end_time=_future(74))
    st, _ = _book(base, headers=_BOB, room_id="c1",
                  start_time=_future(72), end_time=_future(74))
    return st == 202


def _p_conflict_rejected(base, ws):
    _book(base, room_id="c2", start_time=_future(72), end_time=_future(74))
    st, _ = _book(base, headers=_BOB, room_id="c2",
                  start_time=_future(72), end_time=_future(74))
    return st == 409


# ── A-priority-vs-fifo — SILENT GAP ──────────────────────────────────────────
# §5 says higher priority is promoted first; §4 says the FIRST entry is promoted.
# The prompt never says whether priority OVERRIDES arrival order or merely breaks
# ties among equals. Both are shippable; the prompt decides neither.

def _p_priority_overrides_arrival(base, ws):
    """A later high-priority entry is promoted ahead of an earlier low-priority one."""
    st, held = _book(base, room_id="p1", start_time=_future(80), end_time=_future(82))
    if st not in (200, 201):
        return False
    _book(base, headers=_BOB, room_id="p1", start_time=_future(80),
          end_time=_future(82), priority=1)
    _book(base, headers=_BOB, room_id="p1", start_time=_future(80),
          end_time=_future(82), priority=9)
    http_call("DELETE", f"{base}/bookings/{held.get('id')}", None, headers=_ALICE)
    st2, wl = http_call("GET", f"{base}/rooms/p1/waitlist", None, headers=_ALICE)
    entries = wl if isinstance(wl, list) else wl.get("entries", []) if isinstance(wl, dict) else []
    promoted = [e for e in entries if str(e.get("status", "")).lower() == "confirmed"]
    return bool(promoted) and promoted[0].get("priority") == 9


def _p_fifo_with_priority_tiebreak(base, ws):
    """The earliest entry is promoted regardless of a later entry's higher priority."""
    st, held = _book(base, room_id="p2", start_time=_future(80), end_time=_future(82))
    if st not in (200, 201):
        return False
    _book(base, headers=_BOB, room_id="p2", start_time=_future(80),
          end_time=_future(82), priority=1)
    _book(base, headers=_BOB, room_id="p2", start_time=_future(80),
          end_time=_future(82), priority=9)
    http_call("DELETE", f"{base}/bookings/{held.get('id')}", None, headers=_ALICE)
    st2, wl = http_call("GET", f"{base}/rooms/p2/waitlist", None, headers=_ALICE)
    entries = wl if isinstance(wl, list) else wl.get("entries", []) if isinstance(wl, dict) else []
    promoted = [e for e in entries if str(e.get("status", "")).lower() == "confirmed"]
    return bool(promoted) and promoted[0].get("priority") == 1


# ── A-position-ordering — MISREADING TRAP ────────────────────────────────────
# §6: "positions are reported starting from position 1 for the entry that will be
# promoted NEXT." The obvious reading is 1-indexed ARRIVAL order. But §5 makes
# promotion priority-ordered, so position 1 must track PRIORITY, not arrival. The
# naive reading passes casual review and is wrong.

def _p_position_follows_priority(base, ws):
    _book(base, room_id="q1", start_time=_future(90), end_time=_future(92))
    _book(base, headers=_BOB, room_id="q1", start_time=_future(90),
          end_time=_future(92), priority=1)
    _book(base, headers=_BOB, room_id="q1", start_time=_future(90),
          end_time=_future(92), priority=9)
    st, wl = http_call("GET", f"{base}/rooms/q1/waitlist", None, headers=_ALICE)
    entries = wl if isinstance(wl, list) else wl.get("entries", []) if isinstance(wl, dict) else []
    first = next((e for e in entries if e.get("position") == 1), None)
    return bool(first) and first.get("priority") == 9


def _p_position_follows_arrival(base, ws):
    _book(base, room_id="q2", start_time=_future(90), end_time=_future(92))
    _book(base, headers=_BOB, room_id="q2", start_time=_future(90),
          end_time=_future(92), priority=1)
    _book(base, headers=_BOB, room_id="q2", start_time=_future(90),
          end_time=_future(92), priority=9)
    st, wl = http_call("GET", f"{base}/rooms/q2/waitlist", None, headers=_ALICE)
    entries = wl if isinstance(wl, list) else wl.get("entries", []) if isinstance(wl, dict) else []
    first = next((e for e in entries if e.get("position") == 1), None)
    return bool(first) and first.get("priority") == 1


AMBIGUITIES = [
    {
        "id": "A-conflict-response",
        "klass": "contradiction",
        "description": "§1 waitlists a conflicting create (202); §2 rejects it (409) — mutually exclusive",
        "anchors": ("waitlist", "conflict", "409", "202"),
        "readings": {"waitlist": _p_conflict_waitlisted, "reject": _p_conflict_rejected},
        # Forced to pick blind, rejection is the safer default: it preserves the
        # caller's control over the retry, whereas silently converting a create into
        # a queued request changes the contract of the call. Still only a guess.
        "defensible": "reject",
    },
    {
        "id": "A-priority-vs-fifo",
        "klass": "gap",
        "description": "priority overrides arrival order, or only breaks ties — the prompt never says",
        "anchors": ("priority", "promoted"),
        "readings": {"priority_first": _p_priority_overrides_arrival,
                     "fifo_first": _p_fifo_with_priority_tiebreak},
        "defensible": "priority_first",
    },
    {
        "id": "A-position-ordering",
        "klass": "trap",
        "description": "position 1 means next-to-be-promoted (priority order), not first-arrived",
        "anchors": ("position", "promoted next", "position 1"),
        "readings": {"by_priority": _p_position_follows_priority,
                     "by_arrival": _p_position_follows_arrival},
        "defensible": "by_priority",
    },
]
