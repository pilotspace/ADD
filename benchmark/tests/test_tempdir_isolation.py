"""Per-boot tempdir isolation (hermetic-scoring amendment, 2026-07-18).

Live defect: a spec-kit-arm app persisted bookings at
`tempfile.gettempdir()/app_bookings.json` — outside the workspace, so
isolated_workspace's root-store reset never touched it and ONE global temp
file accumulated state across every probe, suite, run, and campaign that
booted the app (fresh spec-kit wm4: cov .50 in-campaign vs .17 on a
same-frozen-workspace rescore, drift with no code change). running_app now
hands every boot a FRESH private TMPDIR/TEMP/TMP and removes it afterwards,
so a tempdir-persisting app boots empty exactly like a workspace-rooted one.

Run: python3 -m pytest benchmark/tests/test_tempdir_isolation.py
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import urllib.request

BENCH = pathlib.Path(__file__).resolve().parents[1]
REPO = BENCH.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from benchmark.workload._oracle_lib import running_app  # noqa: E402

# an app that answers GET / with its tempfile.gettempdir()
_APP = """\
import http.server, json, os, tempfile

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"tmp": tempfile.gettempdir()}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass

http.server.HTTPServer(("127.0.0.1", int(os.environ["PORT"])), H).serve_forever()
"""


def _boot_and_read_tmp(workspace: pathlib.Path) -> str:
    with running_app(str(workspace)) as base:
        with urllib.request.urlopen(f"{base}/", timeout=2) as resp:
            import json
            return json.loads(resp.read())["tmp"]


def test_empty_workspace_never_imports_a_foreign_app(tmp_path, monkeypatch):
    """Bare-runtime boot (-E -s -S). Live defect 2026-07-18: a campaign agent
    editable-installed its app into the GLOBAL site-packages; empty-workspace
    boots then imported that foreign app and probes scored someone else's
    build (wm2/wm3 red-oracle meta-tests saw a wm5-era app answer). PYTHONPATH
    stands in for the site-packages vector here — without -E it would resolve."""
    foreign = tmp_path / "foreign"
    (foreign / "app").mkdir(parents=True)
    (foreign / "app" / "__init__.py").write_text("")
    (foreign / "app" / "__main__.py").write_text(_APP)
    monkeypatch.setenv("PYTHONPATH", str(foreign))

    empty_ws = tmp_path / "empty-ws"
    empty_ws.mkdir()
    with running_app(str(empty_ws)) as base:
        try:
            with urllib.request.urlopen(f"{base}/", timeout=2):
                answered = True
        except Exception:
            answered = False
    assert not answered, "an empty workspace must yield a dead URL, never a foreign app"


def test_each_boot_gets_a_fresh_private_tempdir(tmp_path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "__init__.py").write_text("")
    (app_dir / "__main__.py").write_text(_APP)

    first = _boot_and_read_tmp(tmp_path)
    second = _boot_and_read_tmp(tmp_path)

    host_tmp = tempfile.gettempdir()
    assert first != host_tmp, "the app must not see the operator's shared tempdir"
    assert second != host_tmp
    assert first != second, "every boot must get its OWN tempdir — no cross-boot state"
    assert not pathlib.Path(first).exists(), "the private tempdir is removed after the boot"
