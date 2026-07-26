"""Interrupt-resume mechanics: sample a kill point, kill there, resume clean.

The track this serves asks whether a method survives losing its context
mid-milestone. ADD's claim is that its on-disk state (PLAN.md, the frozen
contract, the engine's phase marker) makes a resume cheap; a method that lives
only in the conversation should have to rediscover what it was doing. Neither
half of that is measured anywhere today.

THE SAMPLING DECISION, stated because it is a choice and not a neutral fact.

Every kill rule encodes a theory of "the same point in the work", and there is
no neutral option:

  wall-clock fraction   advantages methods that write code early, because a
                        planning-first method is caught before it has built
                        much — the metric would measure PACE, not recovery.

  K-th code write       advantages methods that plan before writing, because
  (chosen)              they reach the K-th write later and have done more
                        thinking by then.

We choose progress-sampling because the track's question is "given the same
amount of code written, who recovers better?", and because wall-clock sampling
would let raw arm SPEED leak into a recovery metric. K is sampled per
(wm, rep) and NEVER per arm — every arm is interrupted at the same progress
point, not merely from the same distribution. An arm-dependent K would compare
arms at different places and call it a controlled experiment.

The edge case the choice creates is handled rather than ignored: a method that
writes no code never reaches the K-th write, so `backstop_s` bounds it. Without
that, not building would buy immunity from interruption — and a planning-heavy
method could score perfect recovery by never having started.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import signal
import subprocess
import time
from typing import Any

__all__ = ["DEFAULT_SEED", "sample_kill_point", "count_code_writes", "watch_and_kill"]

DEFAULT_SEED = "add-bench-2/interrupt/v1"

# The SAME code-writing vocabulary benchmark.score uses for its edit_pos
# cut-point. Imported rather than restated: if the trigger and the cut-point
# ever drifted, a run could be killed at a moment the scorer does not believe
# was a write, and test_code_write_counting_matches_the_scorer would be the only
# thing standing between that and a silently wrong measurement.
from benchmark.score import _BASH_WRITE, _WRITE_TOOLS  # noqa: E402


def sample_kill_point(wm: int, rep: int, *, seed: str = DEFAULT_SEED,
                      lo: int = 2, hi: int = 8) -> int:
    """The k-th code write at which to interrupt — deterministic, arm-independent.

    Takes NO arm parameter, deliberately and structurally: an arm-dependent kill
    point would interrupt different methods at different amounts of completed
    work, which is not a controlled comparison however carefully the
    distribution is matched. Determinism makes a campaign reproducible and lets
    a reader recompute any published kill point from the record.
    """
    if lo < 1 or hi < lo:
        raise ValueError(f"invalid kill-point range: [{lo}, {hi}]")
    digest = hashlib.sha256(f"{seed}|{wm}|{rep}".encode()).digest()
    return lo + (int.from_bytes(digest[:8], "big") % (hi - lo + 1))


def count_code_writes(transcript_text: str) -> int:
    """How many code-writing acts the transcript shows so far.

    Tolerant of a PARTIAL final line: the transcript is being streamed while we
    read it, so the last line is routinely half-written. A crash here would kill
    the watcher and silently disable interruption for that run.
    """
    seen = 0
    for line in transcript_text.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue                      # partial or non-JSON line
        message = event.get("message") if isinstance(event, dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        for block in content or []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            name = block.get("name")
            if name in _WRITE_TOOLS:
                seen += 1
            elif name == "Bash" and _BASH_WRITE.search(
                    str((block.get("input") or {}).get("command", ""))):
                seen += 1
    return seen


def _kill_group(proc: subprocess.Popen) -> None:
    """Kill the whole process group, so an agent's children die with it.

    An agent spawns test runners and servers. Killing only the parent leaves
    those alive, holding ports and writing files — the resumed run would then
    be racing the corpse of the one we interrupted."""
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.kill()
        except Exception:
            pass


def watch_and_kill(proc: subprocess.Popen, transcript_path, *, k: int,
                   backstop_s: float, poll_s: float = 0.5) -> dict[str, Any]:
    """Poll the streaming transcript; kill the process group at the k-th write.

    Returns what actually happened, which goes straight onto the record:

        fired: "kth_write" | "backstop" | "none"
        writes_seen / elapsed_s at the moment of the decision

    "none" means the run finished on its own before either trigger — a real
    outcome that must be recorded rather than retried, because silently
    re-running until an interrupt lands would bias the sample toward slow runs.
    """
    if backstop_s <= 0:
        raise ValueError(f"backstop_s must be positive, got {backstop_s!r}")
    started = time.monotonic()
    writes = 0
    # An absolute ceiling ABOVE the backstop. The backstop is the intended exit;
    # this is the circuit breaker for the case where it does not fire at all.
    # Found by mutation: deleting the backstop turned this loop into an infinite
    # one, so the suite HUNG instead of failing — in CI that is a multi-hour
    # timeout rather than a red X, and a hang is the one failure nobody reads.
    ceiling = started + backstop_s * 2 + 30
    while time.monotonic() < ceiling:
        if proc.poll() is not None:                      # finished on its own
            return {"fired": "none", "writes_seen": writes,
                    "elapsed_s": round(time.monotonic() - started, 3)}
        try:
            text = transcript_path.read_text(errors="replace")
        except (OSError, FileNotFoundError):
            text = ""                                    # not created yet
        writes = count_code_writes(text)
        elapsed = time.monotonic() - started
        if writes >= k:
            _kill_group(proc)
            return {"fired": "kth_write", "writes_seen": writes,
                    "elapsed_s": round(elapsed, 3)}
        if elapsed >= backstop_s:
            # M3: a run that never writes must still be interrupted, or not
            # building would buy immunity from the whole track.
            _kill_group(proc)
            return {"fired": "backstop", "writes_seen": writes,
                    "elapsed_s": round(elapsed, 3)}
        time.sleep(poll_s)
    # Ceiling reached: kill anyway and say so. Reporting "ceiling" rather than
    # "backstop" keeps the record honest — this run was cut by a safety net, not
    # by the sampling rule, and it should not be pooled with properly sampled
    # interrupts when the numbers are read.
    _kill_group(proc)
    return {"fired": "ceiling", "writes_seen": writes,
            "elapsed_s": round(time.monotonic() - started, 3)}
