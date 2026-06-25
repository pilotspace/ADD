#!/usr/bin/env python3
"""add_engine.accessors — pure active-task / active-milestone state-dict accessors.

In-memory readers/mutators over the state dict (no file IO, no imports beyond
__future__). Extracted from add.py (engine-modularization 4/N); add.py re-exports
them as module globals so `add._active_task` etc. resolve unchanged.
"""
from __future__ import annotations


def _active_milestone(state: dict) -> str | None:
    """The primary active milestone — the N<=1 scalar mirror (== active_milestones[0])."""
    return state.get("active_milestone")

def _active_task(state: dict, milestone: str | None = None) -> str | None:
    """The active task: per-milestone when `milestone` is given (partial-state -> None),
    else the global/primary scalar active task. Total — never raises."""
    if milestone is None:
        return state.get("active_task")
    return (state.get("active_tasks") or {}).get(milestone)

def _set_active_milestone(state: dict, slug: str | None) -> None:
    """Set the primary active milestone, keeping `active_milestones` consistent (N<=1 sync)."""
    state["active_milestone"] = slug
    state["active_milestones"] = [] if slug is None else [slug]

def _set_active_task(state: dict, slug: str | None, milestone: str | None = None) -> None:
    """Set the active task, keeping the scalar mirror AND the per-milestone map in sync.
    With no owning active milestone the active task is scalar-only (the migration's orphan
    rule); clearing (slug is None) pops the milestone's entry."""
    state["active_task"] = slug
    ms = milestone if milestone is not None else _active_milestone(state)
    tasks_map = state.setdefault("active_tasks", {})
    if ms is None:
        return
    if slug is None:
        tasks_map.pop(ms, None)
    else:
        tasks_map[ms] = slug

def _activate_milestone(state: dict, slug: str) -> None:
    """Add a milestone to the active SET (idempotent) and make it the primary focus,
    syncing the scalar active_task to that milestone's entry. Does NOT remove other members
    (this is how a user reaches N>=2 active milestones)."""
    ms_list = state.setdefault("active_milestones", [])
    if slug not in ms_list:
        ms_list.append(slug)
    state["active_milestone"] = slug
    state["active_task"] = (state.get("active_tasks") or {}).get(slug)

def _deactivate_milestone(state: dict, slug: str) -> None:
    """Remove a milestone from the active SET, pop its active-task entry, and (if it was the
    primary) repoint the primary to the most-recent remaining member (or None when empty)."""
    ms_list = state.setdefault("active_milestones", [])
    if slug in ms_list:
        ms_list.remove(slug)
    (state.setdefault("active_tasks", {})).pop(slug, None)
    if state.get("active_milestone") == slug:
        new = ms_list[-1] if ms_list else None
        state["active_milestone"] = new
        state["active_task"] = (state.get("active_tasks") or {}).get(new) if new else None
