"""Reference amb1 app — only the unambiguous surface of amb1/PROMPT.md (create/list/get/cancel,
typed fields, bearer caller). No waitlist: the amb1 edge suite never touches a planted ambiguity.
Used only to prove that suite passes a correct app. Stdlib only; `python -m app` on $PORT."""
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REQUIRED = ("title", "start_time", "end_time", "room_id")
BOOKINGS: dict[str, dict] = {}


def _when(value):
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def invalid(data):
    if not isinstance(data, dict):
        return "body must be a JSON object"
    missing = [f for f in REQUIRED if f not in data]
    if missing:
        return f"missing {missing[0]}"
    if _when(data["start_time"]) is None or _when(data["end_time"]) is None:
        return "times must be ISO-8601"
    p = data.get("priority")
    if p is not None and (isinstance(p, bool) or not isinstance(p, int)):
        return "priority must be an integer"
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

    def _caller(self):
        auth = self.headers.get("Authorization") or ""
        return auth[7:] if auth.startswith("Bearer ") else None

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
        length = int(self.headers.get("Content-Length") or 0)
        try:
            data = json.loads(self.rfile.read(length) or b"null")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self._send(400, {"error": "malformed JSON"})
        err = invalid(data)
        if err:
            return self._send(400, {"error": err})
        booking = {"id": uuid.uuid4().hex, "status": "pending", "created_by": self._caller(),
                   **{k: data[k] for k in REQUIRED}, "priority": data.get("priority")}
        BOOKINGS[booking["id"]] = booking
        return self._send(201, booking)

    def do_DELETE(self):
        booking = BOOKINGS.get(self._id())
        if booking is None:
            return self._send(404, {"error": "not found"})
        if _when(booking["start_time"]) - datetime.now(timezone.utc) < timedelta(hours=24):
            return self._send(422, {"error": "inside the cancellation window"})
        booking["status"] = "cancelled"
        return self._send(200, booking)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("PORT", "8000"))), Handler).serve_forever()
