"""add_engine.autonomy — autonomy-level read & resolve (engine-modularization 16/N).

Read the declared level off a task header, resolve the effective level (declared else the
project default), and read the project default token. A closed, unpatched cluster
(transitive-closure AST = zero outbound). The cluster-private _AUTONOMY_LINE_RE lives here;
the SHARED _AUTONOMY_LEVELS lives in constants.py. Deps: constants + taskdoc (_task_header)
+ stdlib; no add.
"""
from __future__ import annotations

import re
from pathlib import Path

from add_engine.constants import _AUTONOMY_LEVELS
from add_engine.taskdoc import _task_header

_AUTONOMY_LINE_RE = re.compile(r"(?:^|·)[ \t]*autonomy:[ \t]*([^\s<#|]+)", re.MULTILINE)


def _autonomy_level(hdr: str):
    """The declared autonomy rung from a TASK.md header region (HTML comments
    already stripped by _task_header). Returns a member of _AUTONOMY_LEVELS, or
    None when no `autonomy:` line is present (UNSET — an unfilled `<…>` placeholder,
    whose value the regex declines, counts as unset), or "?" when a REAL token outside
    the set was written (unknown). PURE."""
    m = _AUTONOMY_LINE_RE.search(hdr)
    if not m:
        return None
    tok = m.group(1).strip().lower()
    return tok if tok in _AUTONOMY_LEVELS else "?"

def _effective_autonomy(root: Path, state: dict, slug: str) -> str:
    """The autonomy rung that governs `slug` right now: the task's own declared rung,
    falling back to the project default when the task line is UNSET (None) or an
    unrecognized token ("?") — the same fail-safe chain cmd_new_task seeds from
    (_project_autonomy: absent -> auto, garbled -> conservative). PURE. `state` is unused
    today; it is kept in the signature beside _driver_stop for symmetry."""
    lvl = _autonomy_level(_task_header(root, slug))
    return lvl if lvl in _AUTONOMY_LEVELS else _project_autonomy(root)

def _project_autonomy_token(root: Path):
    """The RAW autonomy declaration in PROJECT.md — a recognized rung, None when no
    declaration line is present, or "?" for a real-but-unrecognized token. Uses the
    anchored _autonomy_level (a title/prose substring is never a declaration) with
    HTML comments stripped. Unreadable foundation -> None. Read-only and PURE."""
    try:
        text = (root / "PROJECT.md").read_text(encoding="utf-8")
    except OSError:
        return None
    return _autonomy_level(re.sub(r"<!--.*?-->", "", text, flags=re.S))

def _project_autonomy(root: Path) -> str:
    """The autonomy rung a new task INHERITS from the project default. Fail-SAFE:
    no declaration -> "auto" (the method default; v7: absent = auto); an unrecognized
    token -> "conservative" (NEVER silently "auto"); an unreadable foundation -> "auto".
    Read-only and PURE — mirrors _project_goal; the seed source for cmd_new_task."""
    tok = _project_autonomy_token(root)
    return "auto" if tok is None else ("conservative" if tok == "?" else tok)
