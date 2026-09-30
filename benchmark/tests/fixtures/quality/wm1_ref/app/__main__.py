"""Reference wm1 app — a correct reading of wm1/PROMPT.md, used only to prove the wm1 edge suite
passes a correct app. Stdlib only; runs as `python -m app` on $PORT."""
import json
import os
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STATUSES = {"pending", "confirmed", "cancelled"}
REQUIRED = ("title", "start_time", "duration_minutes")
BOOKINGS: dict[str, dict] = {}


def _is_iso(value) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def invalid(data, partial: bool):
    if not isinstance(data, dict):
        return "body must be a JSON object"
    if not partial:
        missing = [f for f in REQUIRED if f not in data]
        if missing:
            return f"missing {missing[0]}"
    if "title" in data and not isinstance(data["title"], str):
        return "title must be a string"
    if "start_time" in data and not _is_iso(data["start_time"]):
        return "start_time must be ISO-8601"
    if "duration_minutes" in data:
        d = data["duration_minutes"]
        if isinstance(d, bool) or not isinstance(d, int) or d <= 0:
            return "duration_minutes must be a positive integer"
    if "status" in data and data["status"] not in STATUSES:
        return "unknown status"
    return None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body=None):
        raw = json.dumps(body).encode() if body is not None else b""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        try:
            return True, json.loads(self.rfile.read(length) or b"null")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False, None

    def _id(self):
        parts = self.path.rstrip("/").split("/")
        return parts[2] if len(parts) == 3 and parts[1] == "bookings" else None

    def do_GET(self):
        if self.path.rstrip("/") == "/bookings":
            return self._send(200, list(BOOKINGS.values()))
        bid = self._id()
        if bid in BOOKINGS:
            return self._send(200, BOOKINGS[bid])
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path.rstrip("/") != "/bookings":
            return self._send(404, {"error": "not found"})
        ok, data = self._body()
        err = "malformed JSON" if not ok else invalid(data, partial=False)
        if err:
            return self._send(400, {"error": err})
        booking = {"id": uuid.uuid4().hex, "title": data["title"], "start_time": data["start_time"],
                   "duration_minutes": data["duration_minutes"], "status": data.get("status", "pending")}
        BOOKINGS[booking["id"]] = booking
        return self._send(201, booking)

    def do_PATCH(self):
        bid = self._id()
        if bid not in BOOKINGS:
            return self._send(404, {"error": "not found"})
        ok, data = self._body()
        err = "malformed JSON" if not ok else invalid(data, partial=True)
        if err:
            return self._send(400, {"error": err})
        for key in ("title", "start_time", "duration_minutes", "status"):
            if key in data:
                BOOKINGS[bid][key] = data[key]
        return self._send(200, BOOKINGS[bid])

    def do_DELETE(self):
        bid = self._id()
        if BOOKINGS.pop(bid, None) is None:
            return self._send(404, {"error": "not found"})
        return self._send(204)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("PORT", "8000"))), Handler).serve_forever()
