"""Sloppy amb1 app — answers the visible amb1 oracle's shapes but validates no types and crashes
on malformed JSON. Used only to prove the amb1 edge suite catches it."""
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

    def do_GET(self):
        if self.path.rstrip("/") == "/bookings":
            return self._send(200, list(BOOKINGS.values()))
        b = BOOKINGS.get(self.path.rstrip("/").split("/")[-1])
        return self._send(200, b) if b else self._send(404, {"error": "not found"})

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        if not all(k in data for k in ("title", "start_time", "end_time", "room_id")):
            return self._send(400, {"error": "missing field"})
        booking = {"id": uuid.uuid4().hex, "status": "pending", **data}
        BOOKINGS[booking["id"]] = booking
        return self._send(201, booking)

    def do_DELETE(self):
        b = BOOKINGS.get(self.path.rstrip("/").split("/")[-1])
        b["status"] = "cancelled"
        return self._send(200, b)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("PORT", "8000"))), Handler).serve_forever()
