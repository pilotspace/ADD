"""Shared oracle helper: drive an arm's workspace over HTTP per the fixed
entry contract (`python -m app` on `$PORT`). Stdlib only.

NOT an oracle test file itself (no `test_*` name) — but it is still harness
code that must never be copied into an arm's workspace; keep it under
benchmark/workload/, outside every wm<N>/oracle/ directory so a
path/content-hash isolation check never has to special-case it.
"""
from __future__ import annotations

import contextlib
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

STARTUP_TIMEOUT_S = 10.0
POLL_INTERVAL_S = 0.2

# Dirs never needed to boot `python -m app` (stdlib entry contract) — excluded
# from the isolation copy so it stays fast (a per-arm .venv is large/slow).
_ISOLATION_EXCLUDE = ("__pycache__", ".venv", ".git", "node_modules", ".add")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextlib.contextmanager
def isolated_workspace(workspace):
    """Yield a fresh temp copy of `workspace` with the app's persistent store
    RESET, so scoring is reproducible on archived builds and never mutates the
    source (hermetic-scoring §3 CONTRACT @ v1).

    The copy excludes the heavy dirs the stdlib `python -m app` entry contract
    never needs (`.venv`/`.git`/`__pycache__`/`node_modules`/`.add`), and every
    root-level `*.json` in the copy — the booking store, whatever its name
    (`bookings.json`, `bookings_data.json`, ...) — is removed so the app boots
    empty. The temp dir is always removed on exit; the SOURCE is never written.

    Fail-closed: a missing/uncopyable source yields an empty temp dir the app
    cannot boot from (callers see the ordinary unreachable-app red), never a raise.
    """
    src = pathlib.Path(workspace)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="bench-iso-"))
    copy = tmp / "workspace"
    try:
        try:
            shutil.copytree(src, copy, ignore=shutil.ignore_patterns(*_ISOLATION_EXCLUDE))
        except Exception:
            copy.mkdir(parents=True, exist_ok=True)  # fail-closed: empty, unbootable
        for store in copy.glob("*.json"):  # root-level store, name-agnostic
            with contextlib.suppress(Exception):
                store.unlink()
        yield copy
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@contextlib.contextmanager
def running_app(workspace: str):
    """Start `python -m app` in `workspace` on a free $PORT; yield base_url.

    On an empty/incomplete workspace the subprocess exits immediately or
    never opens the port — in that case yields a base_url that simply will
    not answer, so callers see ordinary connection failures (a clean
    oracle-red on an empty workspace), not a harness crash.
    """
    port = _free_port()
    env = {**os.environ, "PORT": str(port)}
    proc = subprocess.Popen(
        [sys.executable, "-m", "app"],
        cwd=workspace,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + STARTUP_TIMEOUT_S
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                break  # process died — never came up, let callers fail naturally
            try:
                urllib.request.urlopen(f"{base_url}/bookings", timeout=0.5)
                break
            except urllib.error.HTTPError:
                break  # server answered (even with an error status) — it's up
            except (urllib.error.URLError, ConnectionError, OSError):
                time.sleep(POLL_INTERVAL_S)
        yield base_url
    finally:
        if proc.poll() is None:
            proc.terminate()
            with contextlib.suppress(Exception):
                proc.wait(timeout=3)


def http_call(method: str, url: str, payload: dict | None = None, headers: dict | None = None):
    """Return (status_code, parsed_json_or_None). Never raises for HTTP error
    statuses — those are meaningful oracle assertions, not harness bugs."""
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            body = resp.read()
            parsed = json.loads(body) if body else None
            return resp.status, parsed
    except urllib.error.HTTPError as exc:
        body = exc.read()
        try:
            parsed = json.loads(body) if body else None
        except json.JSONDecodeError:
            parsed = None
        return exc.code, parsed
    except (urllib.error.URLError, ConnectionError, OSError) as exc:
        raise AssertionError(f"app did not respond at {url}: {exc}") from exc
