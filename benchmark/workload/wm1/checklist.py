"""WM1 FROZEN requirement checklist — the deterministic fidelity of record.

One row per enumerated requirement in wm1/PROMPT.md. `compute_requirement_coverage`
(benchmark/score.py) boots the built app once and runs each row's `probe(base, workspace)`;
coverage = covered / total. A probe returns True iff the built app satisfies that
requirement. NO LLM anywhere — identical workspace yields the identical score.

This checklist deliberately probes requirements the ad-hoc oracle suite left blind
(CLI parity, duration_minutes positive-int, status enum), so an app that boots but
skips them scores below 1.0 — the whole point of coverage over oracle_pass_rate.

FROZEN: adding/removing a row is a deliberate versioned change (it moves every arm's
coverage denominator). Each `id` is stable — reports key off it.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

from benchmark.workload._oracle_lib import http_call, records

_GOOD = {"title": "Standup", "start_time": "2026-08-01T09:00:00Z", "duration_minutes": 30}


def _create(base: str) -> tuple[int, dict]:
    return http_call("POST", f"{base}/bookings", dict(_GOOD))


def _p_post_create(base, ws):
    status, body = _create(base)
    return status in (200, 201) and isinstance(body, dict) and bool(body.get("id"))


def _p_get_list(base, ws):
    status, body = http_call("GET", f"{base}/bookings")
    return status == 200 and records(body) is not None


def _p_get_one(base, ws):
    _, created = _create(base)
    bid = created.get("id")
    status, body = http_call("GET", f"{base}/bookings/{bid}")
    return status == 200 and body.get("id") == bid


def _p_patch_update(base, ws):
    _, created = _create(base)
    bid = created.get("id")
    status, body = http_call("PATCH", f"{base}/bookings/{bid}", {"status": "confirmed"})
    return status == 200 and body.get("status") == "confirmed"


def _p_delete(base, ws):
    _, created = _create(base)
    bid = created.get("id")
    status, _ = http_call("DELETE", f"{base}/bookings/{bid}")
    if status not in (200, 204):
        return False
    gone, _ = http_call("GET", f"{base}/bookings/{bid}")
    return gone == 404


def _p_status_default_pending(base, ws):
    _, created = _create(base)
    return created.get("status") == "pending"


def _p_missing_field_400(base, ws):
    status, _ = http_call("POST", f"{base}/bookings", {"title": "no start time"})
    return status == 400


def _p_unknown_404(base, ws):
    status, _ = http_call("GET", f"{base}/bookings/does-not-exist")
    return status == 404


def _p_duration_positive(base, ws):
    bad = dict(_GOOD, duration_minutes=0)
    status, _ = http_call("POST", f"{base}/bookings", bad)
    return status == 400


def _p_status_enum(base, ws):
    bad = dict(_GOOD, status="banana")
    status, _ = http_call("POST", f"{base}/bookings", bad)
    return status == 400


# The BARE declared runtime, identical to `running_app`'s app boot: -E ignores
# PYTHONPATH, -s the user site, -S site-packages. cwd (the workspace) stays
# importable — the only place an app may legitimately come from.
#
# `running_app` grew these flags on 2026-07-18 after a campaign agent
# `pip install -e`'d its app into the GLOBAL site-packages and empty-workspace
# boots silently imported someone else's build. This probe spawns its OWN
# subprocess and was never given the same treatment, so it stayed the one path
# that bypassed that fix — and it duly scored covered=True on an empty workspace
# for every run on a contaminated machine. Same defect, same cure, one place it
# was missed.
_BARE = ("-E", "-s", "-S")


def _entry_exists(ws: pathlib.Path, module: str) -> bool:
    """True iff `module`'s source lives in the WORKSPACE UNDER TEST.

    Belt to `_BARE`'s braces: the flags stop a FOREIGN module from being imported,
    this stops us from spawning at all when the workspace never shipped the entry
    point. Cheap, and it keeps the probe honest if the flags are ever loosened.
    """
    rel = pathlib.Path(*module.split("."))
    return (ws / rel.with_suffix(".py")).is_file() or (ws / rel / "__init__.py").is_file()


def _p_cli_parity(base, ws):
    """The PROMPT requires a CLI that lists via the same logic. Try the common
    entry points under the BARE runtime; success = one WHOSE CODE LIVES IN `ws`
    exits 0 for `list`."""
    ws = pathlib.Path(ws)
    port = base.rsplit(":", 1)[-1]
    env = {**os.environ, "APP_BASE": base, "PORT": port}
    # (argv, the module whose source must exist in `ws` for this run to be OURS)
    invocations = (
        ([sys.executable, *_BARE, "-m", "app.cli", "list"], "app.cli"),
        ([sys.executable, *_BARE, "-m", "cli", "list"], "cli"),
        ([sys.executable, *_BARE, "cli.py", "list"], "cli"),
        ([sys.executable, *_BARE, "-m", "app", "list"], "app.__main__"),
    )
    for argv, module in invocations:
        if not _entry_exists(ws, module):
            continue          # not this workspace's code — a pass would be borrowed
        try:
            proc = subprocess.run(argv, cwd=str(ws), env=env, capture_output=True,
                                  text=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            continue
        if proc.returncode == 0:
            return True
    return False


def _p_entry_contract(base, ws):
    """`python -m app` serves HTTP on $PORT — if any GET answers, it held."""
    status, _ = http_call("GET", f"{base}/bookings")
    return status == 200


REQUIREMENTS = [
    {"id": "R-post-create", "description": "POST /bookings creates a booking with a server id", "probe": _p_post_create},
    {"id": "R-get-list", "description": "GET /bookings answers with a collection of bookings", "probe": _p_get_list},
    {"id": "R-get-one", "description": "GET /bookings/{id} fetches one booking", "probe": _p_get_one},
    {"id": "R-patch-update", "description": "PATCH /bookings/{id} updates fields", "probe": _p_patch_update},
    {"id": "R-delete", "description": "DELETE /bookings/{id} removes a booking", "probe": _p_delete},
    {"id": "R-status-default-pending", "description": "a new booking's status defaults to pending", "probe": _p_status_default_pending},
    {"id": "R-missing-field-400", "description": "create with a missing required field returns 400", "probe": _p_missing_field_400},
    {"id": "R-unknown-404", "description": "an unknown booking id returns 404", "probe": _p_unknown_404},
    {"id": "R-duration-positive", "description": "duration_minutes must be a positive integer", "probe": _p_duration_positive},
    {"id": "R-status-enum", "description": "status must be one of pending/confirmed/cancelled", "probe": _p_status_enum},
    {"id": "R-cli-parity", "description": "a CLI lists bookings via the same underlying logic", "probe": _p_cli_parity},
    {"id": "R-entry-contract", "description": "the app runs as `python -m app` serving HTTP on $PORT", "probe": _p_entry_contract},
]
