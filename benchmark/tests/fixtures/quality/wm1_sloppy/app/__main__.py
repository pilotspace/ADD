"""Sloppy wm1 app — passes the visible wm1 oracle (CRUD, 404, 400 on a missing field) but checks
no types and crashes on malformed JSON. Used only to prove the wm1 edge suite catches it."""
import json
import os
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BOOKINGS: dict[str, dict] = {}


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
        return json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")

    def _id(self):
        return self.path.rstrip("/").split("/")[-1]

    def do_GET(self):
        if self.path.rstrip("/") == "/bookings":
            return self._send(200, list(BOOKINGS.values()))
        b = BOOKINGS.get(self._id())
        return self._send(200, b) if b else self._send(404, {"error": "not found"})

    def do_POST(self):
        data = self._body()
        if not all(k in data for k in ("title", "start_time", "duration_minutes")):
            return self._send(400, {"error": "missing field"})
        booking = {"id": uuid.uuid4().hex, "status": "pending", **data}
        BOOKINGS[booking["id"]] = booking
        return self._send(201, booking)

    def do_PATCH(self):
        b = BOOKINGS.get(self._id())
        if not b:
            return self._send(404, {"error": "not found"})
        b.update(self._body())
        return self._send(200, b)

    def do_DELETE(self):
        if BOOKINGS.pop(self._id(), None) is None:
            return self._send(404, {"error": "not found"})
        return self._send(204)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("PORT", "8000"))), Handler).serve_forever()
