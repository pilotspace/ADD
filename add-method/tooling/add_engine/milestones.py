"""add_engine.milestones — MILESTONE.md / state milestone readers (engine-modularization 10/N).

Goal, exit-criteria (and how many cite verify-evidence), stage-criteria, all-milestones-done,
and the production-roadmap check. A closed, unpatched cluster (transitive-closure AST = zero
outbound). The cluster-private _VERIFY_CITE_RE lives here. Deps: constants + stdlib (no add).
"""
from __future__ import annotations

import re
from pathlib import Path

from add_engine.constants import GOAL_UNSET, MILESTONE_FILE

_VERIFY_CITE_RE = re.compile(r"\(verify:\s*\S.*?\)", re.I)


def _has_production_roadmap(state: dict) -> bool:
    """True iff ≥1 milestone in state has stage == "production" (STATUS-AGNOSTIC).
    The single source of the stage-graduation floor (v22 graduate-guide): the guard counts
    that a production-roadmap RECORD exists — it never judges whether those milestones are
    done/good/sufficient (gather-not-judge). An archived-out-of-state roadmap falls to --force."""
    return any(m.get("stage") == "production"
               for m in state.get("milestones", {}).values())

def _project_goal(root: Path) -> str:
    """The project GOAL — the value of the first `goal:` line in PROJECT.md, else
    GOAL_UNSET. Read-only and fail-closed: a missing/unreadable foundation or a
    blank value degrades to the sentinel (orientation never raises). Mirrors how
    _milestone_doc reads the milestone goal — the foundation is the single source."""
    f = root / "PROJECT.md"
    try:
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("goal:"):
                return line.split(":", 1)[1].strip() or GOAL_UNSET
    except OSError:
        pass
    return GOAL_UNSET

def _milestone_doc(root: Path, mslug: str) -> tuple[str, str]:
    """(title, goal) from MILESTONE.md; ('(unknown)','(unknown)') if the doc is gone."""
    f = root / "milestones" / mslug / MILESTONE_FILE
    if not f.exists():
        return "(unknown)", "(unknown)"
    title, goal = "(unknown)", "(unknown)"
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.startswith("# MILESTONE:"):
            title = line.split(":", 1)[1].strip() or "(unknown)"
        elif line.startswith("goal:"):
            goal = line.split(":", 1)[1].strip() or "(unknown)"
            break
    return title, goal

def _exit_criteria(root: Path, mslug: str) -> tuple[int, int]:
    """(met, total) checkbox tally inside MILESTONE.md's 'Exit criteria' section."""
    f = root / "milestones" / mslug / MILESTONE_FILE
    if not f.exists():
        return 0, 0
    m = re.search(r"## Exit criteria.*?(?=\n## |\Z)", f.read_text(encoding="utf-8"), re.S)
    if not m:
        return 0, 0
    sec = m.group(0)
    met = len(re.findall(r"- \[x\]", sec))
    total = met + len(re.findall(r"- \[ \]", sec))
    return met, total

def _exit_criteria_cited(root: Path, mslug: str) -> tuple[int, int]:
    """(cited, total) over MILESTONE.md's 'Exit criteria' section. total = every
    `- [ ]`/`- [x]` criterion line; cited = those carrying a NON-EMPTY
    `(verify: <citation>)`. Read-only and PURE; missing file/section -> (0, 0).
    Mirrors _exit_criteria (the checkbox tally) — an ADDITIVE classification beside
    it; it never touches `milestone_goal_unmet`."""
    f = root / "milestones" / mslug / MILESTONE_FILE
    if not f.exists():
        return 0, 0
    m = re.search(r"## Exit criteria.*?(?=\n## |\Z)", f.read_text(encoding="utf-8"), re.S)
    if not m:
        return 0, 0
    cited = total = 0
    for ln in m.group(0).splitlines():
        if re.match(r"\s*- \[[ x]\]", ln):
            total += 1
            if _VERIFY_CITE_RE.search(ln):
                cited += 1
    return cited, total

def _stage_criteria(root: Path) -> tuple[int, int]:
    """(met, total) checkbox tally inside PROJECT.md's 'Stage goal criteria' section — the
    PROJECT.md analog of _exit_criteria (v22): the human's stage-covered affirmation. Read-only
    and fail-closed to (0, 0): a missing file, a missing section, or any read error never raises
    and never fabricates a cue (so an unreadable foundation withholds graduation, design-for-failure)."""
    try:
        text = (root / "PROJECT.md").read_text(encoding="utf-8")
    except OSError:
        return 0, 0
    m = re.search(r"## Stage goal criteria.*?(?=\n## |\Z)", text, re.S)
    if not m:
        return 0, 0
    sec = m.group(0)
    met = len(re.findall(r"- \[x\]", sec))
    total = met + len(re.findall(r"- \[ \]", sec))
    return met, total

def _all_milestones_done(state: dict) -> bool:
    """True when the project HAS milestones and EVERY one is status=done (v22). Archived
    milestones are absent from state['milestones'] (removed by the archive lifecycle), so they
    do not count; a project with zero milestones is not 'covered' and returns False."""
    ms = state.get("milestones") or {}
    return bool(ms) and all(m.get("status") == "done" for m in ms.values())
