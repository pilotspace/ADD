"""amb1's meters must be BLIND to how an arm resolved the planted ambiguities.

A checklist row or oracle test that depends on the resolution of a planted
ambiguity declares one reading correct. That does two bad things at once: it
converts the ambiguity track into a right-answer track, and it hands a higher
score to whichever arm happens to share the checklist author's reading — for no
engineering reason at all.

The docstring in checklist.py asserts its clean subset is clean. An assertion is
not evidence. This suite makes it refutable: two reference apps, identical in
every unambiguous behaviour, differing ONLY in how they resolve all three planted
ambiguities. If any probe is reading-dependent, the two apps score differently
and test_both_ambiguity_resolutions_score_identical_* fails.

That is the whole design: a claim about fairness that a machine can refute.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.score import (
    _load_checklist,
    compute_oracle_pass_rate,
    compute_requirement_coverage,
)

AMB1 = pathlib.Path(__file__).resolve().parents[1] / "workload" / "amb1"

# ── the reference app ─────────────────────────────────────────────────────────
# Stdlib only, exactly as the PROMPT requires. RESOLUTION is the single knob: it
# decides all three planted ambiguities together, and nothing else.

_REFERENCE_APP = '''\
import json, os, uuid
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

RESOLUTION = "{resolution}"          # "waitlist" | "reject"
# The four ADDED plants (2026-07-26). Each knob is a reading the prompt leaves
# open; the clean checklist must not be able to tell which one was chosen.
CANCEL_AUTH = "{cancel_auth}"             # "owner" | "anyone"
CANCELLED_VISIBLE = "{cancelled_visible}"  # "listed" | "hidden"
ADJACENCY = "{adjacency}"                 # "half_open" | "closed"
LIST_SCOPE = "{list_scope}"               # "all" | "own"

BOOKINGS = {{}}
WAITLIST = {{}}

def _now():
    return datetime.now(timezone.utc)

def _parse(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None

def _conflicts(room, start, end, ignore=None):
    for b in BOOKINGS.values():
        if b["id"] == ignore or b["room_id"] != room or b.get("cancelled"):
            continue
        s, e = _parse(b["start_time"]), _parse(b["end_time"])
        if not s or not e:
            continue
        if ADJACENCY == "closed":
            if start <= e and s <= end:
                return True
        elif start < e and s < end:
            return True
    return False

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
        auth = self.headers.get("Authorization", "")
        return auth.replace("Bearer ", "").strip() or "anonymous"

    def do_GET(self):
        if self.path == "/bookings":
            out = list(BOOKINGS.values())
            if CANCELLED_VISIBLE == "hidden":
                out = [b for b in out if not b.get("cancelled")]
            if LIST_SCOPE == "own":
                out = [b for b in out if b.get("created_by") == self._caller()]
            return self._send(200, out)
        if self.path.startswith("/bookings/"):
            b = BOOKINGS.get(self.path.split("/")[-1])
            return self._send(200, b) if b and not b.get("cancelled") else self._send(404, {{"error": "not_found"}})
        if self.path.startswith("/rooms/") and self.path.endswith("/waitlist"):
            room = self.path.split("/")[2]
            return self._send(200, WAITLIST.get(room, []))
        return self._send(404, {{"error": "not_found"}})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(n) or b"{{}}")
        except Exception:
            return self._send(400, {{"error": "bad_json"}})
        for k in ("title", "start_time", "end_time", "room_id"):
            if k not in data:
                return self._send(400, {{"error": "missing_field"}})
        s, e = _parse(data["start_time"]), _parse(data["end_time"])
        if not s or not e:
            return self._send(400, {{"error": "bad_time"}})
        rec = {{"id": str(uuid.uuid4()), "title": data["title"],
               "start_time": data["start_time"], "end_time": data["end_time"],
               "room_id": data["room_id"], "status": "pending",
               "created_by": self._caller()}}
        if "priority" in data:
            rec["priority"] = data["priority"]
        if _conflicts(data["room_id"], s, e):
            # THE ONLY BRANCH THAT DIFFERS BETWEEN THE TWO REFERENCE APPS.
            if RESOLUTION == "waitlist":
                q = WAITLIST.setdefault(data["room_id"], [])
                rec["status"] = "waitlisted"
                q.append(rec)
                q.sort(key=lambda r: -int(r.get("priority", 0)))
                for i, r in enumerate(q, 1):
                    r["position"] = i
                return self._send(202, rec)
            return self._send(409, {{"error": "conflict"}})
        BOOKINGS[rec["id"]] = rec
        return self._send(201, rec)

    def do_DELETE(self):
        b = BOOKINGS.get(self.path.split("/")[-1])
        if not b or b.get("cancelled"):
            return self._send(404, {{"error": "not_found"}})
        if CANCEL_AUTH == "owner" and b.get("created_by") != self._caller():
            return self._send(403, {{"error": "forbidden"}})
        start = _parse(b["start_time"])
        if start and start - _now() < timedelta(hours=24):
            return self._send(422, {{"error": "inside_cancellation_window"}})
        b["cancelled"] = True
        q = WAITLIST.get(b["room_id"]) or []
        if q:
            promoted = q.pop(0)
            promoted["status"] = "confirmed"
            BOOKINGS[promoted["id"]] = promoted
            for i, r in enumerate(q, 1):
                r["position"] = i
        return self._send(204)

    def log_message(self, *a):
        pass

HTTPServer(("127.0.0.1", int(os.environ["PORT"])), H).serve_forever()
'''


_READING_DEFAULTS = {"cancel_auth": "owner", "cancelled_visible": "listed",
                     "adjacency": "half_open", "list_scope": "all"}

# Every added plant flipped to its OTHER reading, all at once.
_FLIPPED = {"cancel_auth": "anyone", "cancelled_visible": "hidden",
            "adjacency": "closed", "list_scope": "own"}


def _reference(tmp_path: pathlib.Path, resolution: str, name: str = "",
               **readings) -> pathlib.Path:
    ws = tmp_path / f"ref-{name or resolution}"
    pkg = ws / "app"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "__main__.py").write_text(
        _REFERENCE_APP.format(resolution=resolution,
                              **{**_READING_DEFAULTS, **readings}), encoding="utf-8")
    return ws


@pytest.fixture(scope="module")
def refs(tmp_path_factory):
    root = tmp_path_factory.mktemp("amb1refs")
    refs = {r: _reference(root, r) for r in ("waitlist", "reject")}
    # Same conflict reading, every ADDED plant resolved the other way.
    refs["flipped"] = _reference(root, "waitlist", name="flipped", **_FLIPPED)
    return refs


# ── M1 / M2 · the meters exist at all ─────────────────────────────────────────

class TestMetersExist:
    def test_amb1_checklist_loads_and_validates(self):
        # M1 — score_record raised missing_checklist before this row existed.
        rows = _load_checklist(1, "amb")
        assert len(rows) >= 8
        assert all(callable(r["probe"]) for r in rows)

    def test_amb1_oracle_suite_collects(self):
        # M2 — compute_oracle_pass_rate raised unknown_workload_family without it.
        oracle = AMB1 / "oracle"
        assert oracle.is_dir()
        assert list(oracle.glob("test_*.py")), "no oracle tests to collect"


# ── M3 · nothing may depend on a planted ambiguity ────────────────────────────

class TestNoContamination:
    """Mechanical, not editorial. A reviewer reading for contamination is exactly
    the check that already failed once this session."""

    def _sources(self) -> dict[str, str]:
        src = {"checklist.py": (AMB1 / "checklist.py").read_text(encoding="utf-8")}
        for t in (AMB1 / "oracle").glob("test_*.py"):
            src[t.name] = t.read_text(encoding="utf-8")
        return src

    def _code_only(self, text: str) -> str:
        """Strip comments and docstrings — the contamination map DESCRIBES the
        forbidden endpoints in prose, and prose is not a probe."""
        import ast
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)):
                node.value.value = ""
        return ast.unparse(tree)

    def test_no_probe_touches_waitlist_or_promotion_endpoints(self):
        # R:contaminated_probe — /waitlist is unreachable under the `reject`
        # reading, so any probe calling it scores that arm 0 for its reading.
        for name, text in self._sources().items():
            code = self._code_only(text)
            assert "/waitlist" not in code, f"{name} probes the waitlist endpoint"
            assert "position" not in code, f"{name} asserts position semantics"
            assert "confirmed" not in code, f"{name} asserts promotion status"

    def test_no_probe_asserts_a_conflict_status_code(self):
        # R:contaminated_probe — 202 vs 409 IS the planted contradiction.
        for name, text in self._sources().items():
            code = self._code_only(text)
            assert "202" not in code, f"{name} asserts the waitlist reading"
            assert "409" not in code, f"{name} asserts the reject reading"


# ── M4 · non-vacuous in both directions ───────────────────────────────────────

class TestNonVacuous:
    def test_empty_workspace_scores_zero_coverage(self, tmp_path):
        # R:vacuous_meter — the failure mode this whole session kept finding.
        ws = tmp_path / "empty"
        ws.mkdir()
        assert compute_requirement_coverage(ws, 1, "amb") == 0.0

    def test_empty_workspace_scores_zero_oracle(self, tmp_path):
        ws = tmp_path / "empty2"
        ws.mkdir()
        assert compute_oracle_pass_rate(ws, 1, "amb") == 0.0

    def test_reference_app_scores_full_coverage(self, refs):
        # The converse of vacuity: the clean subset must be SATISFIABLE, or a 0.0
        # would mean "impossible" rather than "not built".
        assert compute_requirement_coverage(refs["waitlist"], 1, "amb") == 1.0

    def test_reference_app_passes_the_oracle(self, refs):
        assert compute_oracle_pass_rate(refs["waitlist"], 1, "amb") == 1.0


# ── M5 · THE FAIRNESS PROOF ───────────────────────────────────────────────────

class TestResolutionBlindness:
    """Two apps identical in every unambiguous behaviour, differing ONLY in how
    they resolve all three planted ambiguities. The meters must not notice."""

    def test_both_ambiguity_resolutions_score_identical_coverage(self, refs):
        a = compute_requirement_coverage(refs["waitlist"], 1, "amb")
        b = compute_requirement_coverage(refs["reject"], 1, "amb")
        assert a == b, (
            f"coverage sees the reading: waitlist={a} reject={b} — a probe is "
            "reading-dependent, so the meter rewards one interpretation")

    def test_both_ambiguity_resolutions_score_identical_oracle(self, refs):
        a = compute_oracle_pass_rate(refs["waitlist"], 1, "amb")
        b = compute_oracle_pass_rate(refs["reject"], 1, "amb")
        assert a == b, (
            f"oracle sees the reading: waitlist={a} reject={b}")

    def test_added_plants_do_not_move_coverage(self, refs):
        # The widening (2026-07-26) added four plants. If the clean checklist can
        # tell how any of them was resolved, the track has quietly become a
        # right-answer track for that item — the exact thing this suite exists to
        # refute, now covering seven items rather than three.
        a = compute_requirement_coverage(refs["waitlist"], 1, "amb")
        b = compute_requirement_coverage(refs["flipped"], 1, "amb")
        assert a == b, (
            f"coverage sees an added reading: default={a} flipped={b} — a row "
            "depends on cancel authority, cancelled visibility, adjacency, or "
            "list scope")

    def test_added_plants_do_not_move_the_oracle(self, refs):
        a = compute_oracle_pass_rate(refs["waitlist"], 1, "amb")
        b = compute_oracle_pass_rate(refs["flipped"], 1, "amb")
        assert a == b, f"oracle sees an added reading: default={a} flipped={b}"

    def test_the_two_references_really_do_differ(self, refs):
        # Guards the guard: if both apps behaved identically, the fairness proof
        # above would be trivially true and prove nothing at all.
        from benchmark.workload._oracle_lib import http_call, running_app

        seen = {}
        for name, ws in refs.items():
            with running_app(str(ws)) as base:
                body = {"title": "T", "start_time": "2027-01-01T10:00:00+00:00",
                        "end_time": "2027-01-01T11:00:00+00:00", "room_id": "dup"}
                http_call("POST", f"{base}/bookings", dict(body))
                status, _ = http_call("POST", f"{base}/bookings", dict(body))
                seen[name] = status
        assert seen["waitlist"] != seen["reject"], (
            f"the two reference apps resolve the contradiction identically: {seen}")


# ── M6 · every REQUIRED metric is computable for the amb family ───────────────

class TestRecordCompleteness:
    def test_every_required_metric_is_computable_for_amb(self, refs):
        # M6 — the blocker this task exists to clear. Before it, score_record
        # raised missing_checklist / unknown_workload_family, so a live run would
        # have spent real money and then crashed instead of writing a record.
        import benchmark.score as score
        from benchmark.schema.run_record import REQUIRED_METRICS

        ws = refs["waitlist"]
        computed = {
            "requirement_coverage": score.compute_requirement_coverage(ws, 1, "amb"),
            "oracle_pass_rate": score.compute_oracle_pass_rate(ws, 1, "amb"),
            "regression_rate": score.compute_regression_rate_v2(ws, 1, "amb"),
        }
        for name, value in computed.items():
            assert isinstance(value, float), f"{name} is not a float"
        missing = {m for m in REQUIRED_METRICS
                   if m not in computed} - {"tokens_total", "cost_usd",
                                            "context_rot_slope", "time_to_first_edit"}
        assert not missing, f"REQUIRED metrics with no computation path: {missing}"

    def test_ambiguity_rate_is_computable_for_amb1(self, refs, tmp_path):
        # The track's own metric, end to end on a real workspace: the reference app
        # never surfaces anything (it has no transcript), so the honest score is 0.0
        # — surfacing is not something an app can demonstrate, only an agent.
        import benchmark.score as score
        detail = score.compute_ambiguity_detail(
            refs["waitlist"], tmp_path / "absent.jsonl", 1, "amb")
        # 3 at first freeze; 7 after the 2026-07-26 widening. Pinned as a literal
        # rather than len(AMBIGUITIES) so a silently DROPPED item still fails —
        # comparing the meter against itself would notice nothing.
        assert len(detail) == 7
        assert all(d["verdict"] != "surfaced" for d in detail)
        assert {d["klass"] for d in detail} == {"contradiction", "gap", "trap"}
