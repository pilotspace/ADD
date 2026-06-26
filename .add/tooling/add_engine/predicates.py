#!/usr/bin/env python3
"""add_engine.predicates — pure state/markdown predicates for the ADD engine.

Phase ownership, setup/milestone gating checks, and section-filled detection.
Extracted from add.py (engine-modularization 5/N); add.py re-exports them as module
globals so `add._phase_owner` etc. resolve unchanged.
"""
from __future__ import annotations

import re

from add_engine.constants import PHASE_OWNER
from add_engine.io_state import _die


def _phase_owner(phase: str) -> str:
    """Map a phase to its owner (human|seam|ai); `unmapped_phase` if absent (fail closed)."""
    owner = PHASE_OWNER.get(phase)
    if owner is None:
        _die("unmapped_phase")
    return owner

def _setup_locked(state: dict) -> bool:
    """True when the project's setup is locked — i.e. the build-boundary gate is OPEN.

    A state with NO "setup" key is GRANDFATHERED-locked: plain `init` and every legacy
    project are never gated (the lock is opt-in via `init --await-lock`). The gate is
    therefore active in exactly one case: "setup" present AND locked is False."""
    return ("setup" not in state) or (state["setup"].get("locked") is True)

def _milestone_confirmed(state: dict, mslug: str) -> bool:
    """True when milestone `mslug` is confirmed — i.e. the new-task gate is OPEN.

    Mirrors `_setup_locked` one level down. A milestone record with NO "confirmed" key is
    GRANDFATHERED-confirmed: every milestone created WITHOUT `--await-confirm` (and every
    pre-existing one) is never gated. Opt-in: `new-milestone --await-confirm` seeds confirmed:false,
    so the gate is active in exactly one case: the record is present AND confirmed is False. An
    unknown milestone is treated as confirmed here (existence is cmd_new_task's separate check)."""
    m = (state.get("milestones") or {}).get(mslug)
    if not isinstance(m, dict) or "confirmed" not in m:
        return True
    return m["confirmed"] is True

def _section_unfilled(md_text: str, header: str) -> bool:
    """True iff the `header` section is PRESENT but UNFILLED — empty (no real bullet) or
    still a `<…>` template placeholder. ABSENT section -> False (grandfathered legacy);
    a filled section (>=1 real bullet, no `<…>`) -> False. Pure predicate — the shared
    placeholder test the fill gates use (contract-fill at confirm; build-expectations at build)."""
    body, in_sec, present = [], False, False
    for ln in md_text.splitlines():
        if ln.startswith(header):
            in_sec, present = True, True
            continue
        if in_sec:
            if ln.startswith("#"):          # ANY next header (## or ###) ends our section
                break
            if ln.lstrip().startswith(">"):  # skip blockquote GUIDANCE — it is not content
                continue
            body.append(ln)
    if not present:
        return False                        # absent -> grandfather
    text = "\n".join(body).strip()
    if not text:
        return True                         # present but empty
    return bool(re.search(r"<[^>\n]+>", text))   # a <…> placeholder remains


def _task_done(t: dict) -> bool:
    # Matrix 3: a task is done when Verify reads PASS *or a signed RISK-ACCEPTED*.
    # Both completing gates advance phase to "done" (cmd_gate), and a waiver is
    # signed at gate time — so a verdict gate is enough here; we need not re-read
    # the waiver. HARD-STOP never reaches "done". A bare `phase done` (escape
    # hatch, gate still "none") deliberately does NOT count: completion needs a
    # recorded verdict, not just a phase marker.
    return t.get("phase") == "done" and t.get("gate") in ("PASS", "RISK-ACCEPTED")
