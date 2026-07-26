"""A session workspace cannot be re-scored against an EARLIER milestone.

This trap produced a false alarm during the 2026-07-26 shape audit. Re-scoring
`runs-session/*` and `runs-atomic-session/*` today returned 0.00 for wm1 against
stored figures of 0.92-1.00, which reads exactly like archived-workspace rot. It
is not rot, and the stored figures are fine.

The cause is the milestone sequence itself. wm1's checklist sends NO
Authorization header — grep it: zero occurrences. wm2's `R-auth-401` REQUIRES
that an unauthenticated request return 401. A session run evolves ONE workspace
through wm1..wm6, so the moment it satisfies wm2 every wm1 probe receives 401 and
wm1 scores 0.00 forever. The two contracts are mutually exclusive BY DESIGN;
wm2's requirement is that wm1's client behaviour stops working.

Per-milestone records for a session run were scored when that milestone
completed, against the tree as it then stood. That is the only valid time to
score them. Re-scoring the FINAL tree against an earlier checklist compares an
app to a contract it was deliberately made to outgrow.

The practical rule this pins:
  - per-milestone runs (runs/<campaign>/<arm>/wm<N>/workspace) re-score fine;
    each has its own tree.
  - session runs (one workspace, many milestones) re-score ONLY against their
    LAST milestone. An earlier-milestone re-score is meaningless, not a
    regression, and must never be reported as one.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.score import compute_requirement_coverage

WORKLOAD = pathlib.Path(__file__).resolve().parents[1] / "workload"

# A wm1-shaped app. AUTH is the only knob: with it on, the app satisfies wm2's
# R-auth-401 and therefore refuses every wm1 probe.
_APP = '''\
import json, os, uuid
from http.server import BaseHTTPRequestHandler, HTTPServer

REQUIRE_AUTH = {require_auth}
BOOKINGS = {{}}

class H(BaseHTTPRequestHandler):
    def _send(self, code, payload=None):
        body = json.dumps(payload).encode() if payload is not None else b""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _denied(self):
        if REQUIRE_AUTH and not self.headers.get("Authorization"):
            self._send(401, {{"error": "unauthorized"}})
            return True
        return False

    def do_GET(self):
        if self._denied():
            return
        if self.path == "/bookings":
            return self._send(200, list(BOOKINGS.values()))
        b = BOOKINGS.get(self.path.rsplit("/", 1)[-1])
        return self._send(200, b) if b else self._send(404, {{"error": "not_found"}})

    def do_POST(self):
        if self._denied():
            return
        n = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(n) or b"{{}}")
        except Exception:
            return self._send(400, {{"error": "bad_json"}})
        for k in ("title", "start_time", "duration_minutes"):
            if k not in data:
                return self._send(400, {{"error": "missing_field"}})
        rec = {{"id": str(uuid.uuid4()), "status": "pending", **data}}
        BOOKINGS[rec["id"]] = rec
        return self._send(201, rec)

    def log_message(self, *a):
        pass

HTTPServer(("127.0.0.1", int(os.environ["PORT"])), H).serve_forever()
'''


def _app(root: pathlib.Path, require_auth: bool) -> pathlib.Path:
    ws = root / f"auth-{require_auth}"
    pkg = ws / "app"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "__main__.py").write_text(_APP.format(require_auth=require_auth),
                                     encoding="utf-8")
    return ws


@pytest.fixture(scope="module")
def apps(tmp_path_factory):
    root = tmp_path_factory.mktemp("crossmilestone")
    return {"open": _app(root, False), "authed": _app(root, True)}


class TestWm1AndWm2ContractsAreMutuallyExclusive:
    def test_wm1_checklist_sends_no_authorization_header(self):
        # The premise. If wm1 ever starts sending a token, this whole trap
        # dissolves and the note above stops being true.
        src = (WORKLOAD / "wm1" / "checklist.py").read_text(encoding="utf-8")
        assert "Authorization" not in src

    def test_wm2_requires_unauthenticated_requests_to_be_refused(self):
        src = (WORKLOAD / "wm2" / "checklist.py").read_text(encoding="utf-8")
        assert "R-auth-401" in src

    def test_the_same_app_scores_wm1_at_zero_once_it_enforces_auth(self, apps):
        # The proof, live: ONE app, one knob. Nothing about its wm1 behaviour
        # changes — only whether it satisfies the NEXT milestone's requirement.
        without = compute_requirement_coverage(apps["open"], 1, "wm")
        with_auth = compute_requirement_coverage(apps["authed"], 1, "wm")
        assert without > 0.0, "reference app satisfies no wm1 row; test is vacuous"
        assert with_auth == 0.0, (
            f"expected a total wm1 wipeout from auth alone, got {with_auth}")

    def test_a_zero_here_is_not_evidence_of_a_broken_app(self, apps):
        # Stated as an assertion so it cannot quietly stop being true: the
        # auth-enforcing app is strictly MORE capable, and scores strictly less.
        assert (compute_requirement_coverage(apps["authed"], 1, "wm")
                < compute_requirement_coverage(apps["open"], 1, "wm"))
