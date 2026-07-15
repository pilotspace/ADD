"""Hermetic scoring (hermetic-scoring §3 CONTRACT @ v1): scoring boots the app
in an ISOLATED copy of the workspace with the persistent store RESET, so the
source workspace is never mutated and coverage/oracle are reproducible on
archived builds.

`isolated_workspace` is imported LAZILY inside each test so the suite runs RED
test-by-test on the missing implementation, not dying at collection.
"""
from __future__ import annotations

import importlib
import pathlib
import textwrap

from benchmark.score import compute_requirement_coverage


def _oracle_lib():
    return importlib.import_module("benchmark.workload._oracle_lib")


# A minimal `python -m app` booking app that PERSISTS to bookings.json in cwd —
# enough to exercise the store-write path (the wm1 checklist probes POST to it).
_STORE_APP = '''
import json, os
from http.server import BaseHTTPRequestHandler, HTTPServer

STORE = "bookings.json"


def _load():
    try:
        with open(STORE) as f:
            return json.load(f)
    except Exception:
        return {}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        data = _load()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(list(data.values())).encode())

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(n) or b"{}")
        data = _load()
        bid = str(len(data) + 1)
        body["id"] = bid
        data[bid] = body
        with open(STORE, "w") as f:   # PERSIST to cwd — the contamination source
            json.dump(data, f)
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())


def main():
    HTTPServer(("127.0.0.1", int(os.environ.get("PORT", "8000"))), H).serve_forever()


if __name__ == "__main__":
    main()
'''


def _write_store_app(ws: pathlib.Path) -> None:
    ws.mkdir(parents=True, exist_ok=True)
    (ws / "app.py").write_text(textwrap.dedent(_STORE_APP))


# --------------------------------------------------------------------------
# isolated_workspace — the core new symbol (Contract)
# --------------------------------------------------------------------------


def test_isolated_workspace_resets_store_and_excludes_heavy(tmp_path):
    ws = tmp_path / "ws"
    _write_store_app(ws)
    (ws / "bookings.json").write_text('{"seed": {"id": "seed"}}')
    (ws / "bookings_data.json").write_text("{}")  # a differently-named store
    (ws / ".venv").mkdir()
    (ws / ".venv" / "big").write_text("x" * 1000)
    (ws / "__pycache__").mkdir()
    (ws / "__pycache__" / "junk.pyc").write_text("x")

    isolated_workspace = _oracle_lib().isolated_workspace
    with isolated_workspace(ws) as copy:
        copy = pathlib.Path(copy)
        assert (copy / "app.py").is_file()          # code copied
        assert not (copy / ".venv").exists()         # heavy dir excluded
        assert not (copy / "__pycache__").exists()
        assert not (copy / "bookings.json").exists()      # root *.json store reset
        assert not (copy / "bookings_data.json").exists()  # name-agnostic reset
        held = copy

    assert not held.exists()  # temp removed on exit


def test_isolated_workspace_never_writes_source(tmp_path):
    ws = tmp_path / "ws"
    _write_store_app(ws)
    (ws / "bookings.json").write_text('{"seed": 1}')
    before = (ws / "bookings.json").read_bytes()

    isolated_workspace = _oracle_lib().isolated_workspace
    with isolated_workspace(ws) as copy:
        copy = pathlib.Path(copy)
        (copy / "bookings.json").write_text('{"mutated": true}')  # write into the COPY

    assert (ws / "bookings.json").read_bytes() == before  # source byte-unchanged
    assert (ws / ".venv" if (ws / ".venv").exists() else ws).exists()


# --------------------------------------------------------------------------
# scoring is hermetic (M1/M2) — the source store is never mutated by scoring
# --------------------------------------------------------------------------


def test_coverage_does_not_mutate_source_store(tmp_path):
    ws = tmp_path / "ws"
    _write_store_app(ws)
    (ws / "bookings.json").write_text('{"seed": {"id": "seed"}}')
    before = (ws / "bookings.json").read_bytes()

    # the wm1 probes POST to the app; without isolation those bookings would be
    # persisted into THIS workspace's store — with isolation they land in a copy.
    compute_requirement_coverage(ws, 1)

    assert (ws / "bookings.json").read_bytes() == before


def test_coverage_reproducible_across_repeated_scorings(tmp_path):
    ws = tmp_path / "ws"
    _write_store_app(ws)
    # no pre-seeded store: each scoring must start from the SAME reset state,
    # so repeated calls yield the identical value despite probe writes.
    first = compute_requirement_coverage(ws, 1)
    second = compute_requirement_coverage(ws, 1)
    third = compute_requirement_coverage(ws, 1)
    assert first == second == third
