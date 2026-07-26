"""AMB1 FROZEN requirement checklist — the CLEAN SUBSET only.

One row per requirement amb1/PROMPT.md states UNAMBIGUOUSLY. This checklist is
deliberately smaller than the prompt, and the omissions are the point.

WHY MOST OF THE MILESTONE IS NOT SCORED HERE
--------------------------------------------
amb1 plants seven ambiguities on purpose (see ambiguity.py). A checklist row that
depends on how an arm RESOLVED one of them would declare one reading correct —
quietly converting the ambiguity track into a right-answer track and destroying
the thing it measures. Worse, it would do so asymmetrically: the arm sharing the
checklist author's reading scores higher for no engineering reason.

Contamination map — what is excluded, and which planted item excludes it:

  A-conflict-response (§1 waitlists a conflict with 202 · §2 rejects it with 409)
      Poisons EVERY probe that needs an entry to reach a waitlist: under the
      `reject` reading no waitlist ever populates, so such a probe scores an arm
      0 for taking a reading the prompt itself offered.
      -> excludes waitlist membership, promotion, and position entirely.

  A-priority-vs-fifo   -> excludes promotion ORDER (§4 §5)
  A-position-ordering  -> excludes position semantics (§6)

  Added 2026-07-26, when the track was widened from three items to seven. Each
  one is a reading the prompt leaves open, so no row may depend on it:

  A-cancel-authority     -> excludes cancelling ANOTHER caller's booking.
      R-delete-cancels deliberately has ALICE cancel her own.
  A-cancelled-visibility -> excludes whether a cancelled booking remains in
      GET /bookings. R-get-list asserts only that the response is a JSON array.
  A-adjacent-boundary    -> excludes back-to-back bookings. Every row here already
      uses a distinct room_id, so no row can reach the conflict path at all.
  A-list-scope           -> excludes WHOSE bookings GET /bookings returns.
      R-auth-identifies-caller inspects the two create RESPONSES, never a listing.

  These four are, unlike the original two, resolvable under EITHER reading of
  A-conflict-response — none of them touches the waitlist. That was the point of
  choosing them: an item that needs a queue hands `neither` to any arm that read
  §2 (reject with 409) as authoritative.

  GET /rooms/{id}/waitlist answering on an empty room is EXCLUDED as borderline:
  §6 states the endpoint unconditionally, but an arm that read §2 as
  authoritative may reasonably build no waitlist feature at all. Punishing that
  is punishing the reading, not the omission.

What remains is provable under BOTH readings of every planted item — which is
exactly what `test_both_ambiguity_resolutions_score_identical_coverage` proves
mechanically, so this docstring's claim is refutable rather than asserted.

FROZEN: adding/removing a row moves every arm's coverage denominator. Each `id`
is stable — reports key off it.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from benchmark.workload._oracle_lib import http_call, running_app  # noqa: F401

_ALICE = {"Authorization": "Bearer test-token-alice"}
_BOB = {"Authorization": "Bearer test-token-bob"}


def _iso(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _body(**over) -> dict:
    """A booking far enough out that the 24h cancellation window never applies.

    Every base-behaviour row uses a distinct room_id so no row can ever collide
    with another and trip the conflict path — the one path this checklist must
    never touch."""
    body = {"title": "Standup", "start_time": _iso(72), "end_time": _iso(73),
            "room_id": "clean-default"}
    body.update(over)
    return body


def _create(base: str, **over):
    return http_call("POST", f"{base}/bookings", _body(**over), headers=_ALICE)


# ── base behaviour ────────────────────────────────────────────────────────────

def _p_post_create(base, ws):
    status, body = _create(base, room_id="c-create")
    return status in (200, 201) and isinstance(body, dict) and bool(body.get("id"))


def _p_get_list(base, ws):
    status, body = http_call("GET", f"{base}/bookings", None, headers=_ALICE)
    return status == 200 and isinstance(body, list)


def _p_get_one(base, ws):
    _, created = _create(base, room_id="c-get-one")
    bid = created.get("id") if isinstance(created, dict) else None
    status, body = http_call("GET", f"{base}/bookings/{bid}", None, headers=_ALICE)
    return status == 200 and isinstance(body, dict) and body.get("id") == bid


def _p_unknown_404(base, ws):
    status, _ = http_call("GET", f"{base}/bookings/does-not-exist", None, headers=_ALICE)
    return status == 404


def _p_missing_field_400(base, ws):
    status, _ = http_call("POST", f"{base}/bookings", {"title": "no times"}, headers=_ALICE)
    return status == 400


def _p_status_default_pending(base, ws):
    _, created = _create(base, room_id="c-pending")
    return isinstance(created, dict) and created.get("status") == "pending"


def _p_priority_accepted(base, ws):
    """The prompt makes `priority` an optional integer field. WHAT priority MEANS
    for promotion order is ambiguous (A-priority-vs-fifo) and is NOT probed — only
    that the field is accepted on create."""
    status, body = _create(base, room_id="c-priority", priority=5)
    return status in (200, 201) and isinstance(body, dict) and bool(body.get("id"))


def _p_auth_identifies_caller(base, ws):
    """A booking records who created it. Two callers, two bookings, and each is
    fetchable — the identity is recorded somewhere the app can distinguish."""
    _, a = http_call("POST", f"{base}/bookings", _body(room_id="c-auth-a"), headers=_ALICE)
    _, b = http_call("POST", f"{base}/bookings", _body(room_id="c-auth-b"), headers=_BOB)
    if not (isinstance(a, dict) and isinstance(b, dict)):
        return False
    if not (a.get("id") and b.get("id")) or a["id"] == b["id"]:
        return False
    blob = f"{a}{b}".lower()
    return "alice" in blob or "bob" in blob or "user" in blob or "created_by" in blob


# ── §3 cancellation window — independent of all three planted items ───────────

def _p_delete_cancels(base, ws):
    """A booking comfortably OUTSIDE the 24h window can be cancelled."""
    _, created = _create(base, room_id="c-delete")
    bid = created.get("id") if isinstance(created, dict) else None
    status, _ = http_call("DELETE", f"{base}/bookings/{bid}", None, headers=_ALICE)
    return status in (200, 204)


def _p_cancel_window_422(base, ws):
    """INSIDE the 24h window, DELETE returns 422. §3 states this outright and no
    planted ambiguity touches it."""
    _, created = _create(base, room_id="c-window",
                         start_time=_iso(2), end_time=_iso(3))
    bid = created.get("id") if isinstance(created, dict) else None
    if not bid:
        return False
    status, _ = http_call("DELETE", f"{base}/bookings/{bid}", None, headers=_ALICE)
    return status == 422


def _p_entry_contract(base, ws):
    """`python -m app` serves HTTP on $PORT — if any GET answers, it held."""
    status, _ = http_call("GET", f"{base}/bookings", None, headers=_ALICE)
    return status == 200


REQUIREMENTS = [
    {"id": "R-post-create", "description": "POST /bookings creates a booking with a server id", "probe": _p_post_create},
    {"id": "R-get-list", "description": "GET /bookings lists bookings as a JSON array", "probe": _p_get_list},
    {"id": "R-get-one", "description": "GET /bookings/{id} fetches one booking", "probe": _p_get_one},
    {"id": "R-unknown-404", "description": "an unknown booking id returns 404", "probe": _p_unknown_404},
    {"id": "R-missing-field-400", "description": "create with a missing required field returns 400", "probe": _p_missing_field_400},
    {"id": "R-status-default-pending", "description": "a new booking's status defaults to pending", "probe": _p_status_default_pending},
    {"id": "R-priority-accepted", "description": "an optional integer priority is accepted on create", "probe": _p_priority_accepted},
    {"id": "R-auth-identifies-caller", "description": "the Authorization bearer identifies the caller and the booking records it", "probe": _p_auth_identifies_caller},
    {"id": "R-delete-cancels", "description": "a booking outside the 24h window can be cancelled", "probe": _p_delete_cancels},
    {"id": "R-cancel-window-422", "description": "cancelling inside the 24h window returns 422", "probe": _p_cancel_window_422},
    {"id": "R-entry-contract", "description": "the app runs as `python -m app` serving HTTP on $PORT", "probe": _p_entry_contract},
]
