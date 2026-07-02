"""add_engine.search — keyword/substring search over the milestone/task corpus
(context-search, search-index task). A flat, keyword-only index over document
prose — title/goal/rationale (MILESTONE.md) or title/Feature (TASK.md) lines,
never full body, never graph/backlink traversal, never a persisted cache:
rebuilt fresh on every call (the milestone's own "rebuild-on-demand is enough"
scope decision). Deliberately distinct from a graph-query command over the
artifact backlink edges (rejected elsewhere) — this is plain substring
retrieval over document prose. PURE except the file reads `_search_corpus`
performs; NO-EXEC — no network, no subprocess, no persona/teacher read.
"""
from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

from add_engine.constants import MILESTONE_FILE

MAX_SNIPPET_LEN = 120

_PLACEHOLDER_RE = re.compile(r"^<[^>\n]+>$")


def _fold_continuation(raw: str) -> str:
    """Join a field's first-line value with any indented wrap-continuation
    lines that follow it into one flat, single-line string (mirrors
    taskdoc._task_prose's continuation join). `raw` is the value's own first
    line followed by the REST of the document — folding stops at the first
    blank line or the first line that is NOT indented (a sibling `key:` line
    never bleeds in). PURE."""
    lines = raw.splitlines()
    if not lines:
        return ""
    parts = [lines[0].strip()]
    for ln in lines[1:]:
        if not ln or not ln[:1].isspace():
            break
        stripped = ln.strip()
        if not stripped:
            break
        parts.append(stripped)
    return " ".join(p for p in parts if p).strip()


def _line_field(text: str, prefix: str) -> str:
    """The first `prefix`-led line's value (continuation-folded via
    `_fold_continuation`); '' if no line starts with `prefix`. Shared helper
    behind `_milestone_fields`/`_task_fields` — not part of the frozen 6, but
    a private implementation detail (mirrors milestones.py's own private
    _VERIFY_CITE_RE convention)."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith(prefix):
            first = ln[len(prefix):].strip()
            return _fold_continuation("\n".join([first, *lines[i + 1:]]))
    return ""


def _milestone_fields(text: str) -> dict[str, str]:
    """{'title', 'goal', 'rationale'} from raw MILESTONE.md text, continuation-
    folded. Missing field -> ''. Extends milestones._milestone_doc's
    (title, goal) shape with 'rationale'. Dict INSERTION ORDER (title, goal,
    rationale) is the snippet priority `_keyword_hit` reads. PURE; NO-EXEC."""
    return {
        "title": _line_field(text, "# MILESTONE:"),
        "goal": _line_field(text, "goal:"),
        "rationale": _line_field(text, "rationale:"),
    }


def _task_fields(text: str) -> dict[str, str]:
    """{'title', 'feature'} from raw TASK.md text — H1 title + §1 `Feature:`
    line, continuation-folded; an unfilled `<name>`-style placeholder value
    -> '' (never treated as matchable content). Dict INSERTION ORDER (title,
    feature) is the snippet priority `_keyword_hit` reads. PURE; NO-EXEC."""
    feature = _line_field(text, "Feature:")
    if _PLACEHOLDER_RE.match(feature.strip()):
        feature = ""
    return {
        "title": _line_field(text, "# TASK:"),
        "feature": feature,
    }


def _keyword_hit(fields: dict[str, str], keywords: list[str]) -> tuple[int, str] | None:
    """(match_count, snippet) for one artifact's indexed fields against
    `keywords`: case-insensitive substring, OR-combined. count sums ALL
    keyword occurrences across ALL fields; snippet is the first field (dict
    order) containing ANY keyword match, truncated to MAX_SNIPPET_LEN with an
    ellipsis. None -> no keyword matched anywhere. PURE; NO-EXEC."""
    needles = [k.lower() for k in keywords]
    count = 0
    snippet: str | None = None
    for value in fields.values():
        if not value:
            continue
        hay = value.lower()
        field_count = sum(hay.count(n) for n in needles if n)
        count += field_count
        if snippet is None and field_count > 0:
            snippet = (value[:MAX_SNIPPET_LEN] + "...") if len(value) > MAX_SNIPPET_LEN else value
    if count == 0:
        return None
    return count, snippet


def _iter_corpus(root: Path) -> Iterator[tuple[Path, str, bool]]:
    """Yield (path, kind, archived) over the 4 frozen corpus roots, in fixed
    order: active milestones, active tasks, archived milestones, archived
    tasks (nested under the owning milestone's compact bundle — never a flat
    `archive/*/TASK.md`). A missing root dir yields nothing — `Path.glob` on
    an absent directory is empty, never an OSError."""
    for pattern, kind, archived in (
        (f"milestones/*/{MILESTONE_FILE}", "milestone", False),
        ("tasks/*/TASK.md", "task", False),
        (f"archive/*/{MILESTONE_FILE}", "milestone", True),
        ("archive/*/tasks/*/TASK.md", "task", True),
    ):
        for p in sorted(root.glob(pattern)):
            yield p, kind, archived


def _own_status(text: str, kind: str) -> str:
    """The doc's own status — milestone: the `status:` token off the
    `stage: ... · status: ... · created: ...` header line; task: the
    `phase:` header line's value. '(unknown)' if absent. Never consulted for
    an archive-root hit — `_search_corpus` overrides to "archived" first.
    Private implementation detail behind `_search_corpus`. PURE."""
    if kind == "milestone":
        m = re.search(r"(?m)^stage:.*?\bstatus:\s*(\S+)", text)
    else:
        m = re.search(r"(?m)^phase:\s*(\S+)", text)
    return m.group(1) if m else "(unknown)"


def _search_corpus(root: Path, keywords: list[str]) -> list[dict]:
    """Assemble {slug, kind, status, snippet, count} per hit across the full
    corpus (`_iter_corpus`): status is the literal "archived" for any
    archive/-root hit (overrides a stale in-doc status:/phase: value), else
    the doc's own status:/phase: line (`_own_status`), or "(unknown)" if
    absent. Sorted by (-count, slug) — strictly descending count, ties broken
    alphabetically by slug. An unreadable doc is skipped, never raises
    (mirrors _collect_open_deltas' degrade-safe try/except OSError). PURE
    except the file reads it performs."""
    hits: list[dict] = []
    for path, kind, archived in _iter_corpus(root):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        fields = _milestone_fields(text) if kind == "milestone" else _task_fields(text)
        hit = _keyword_hit(fields, keywords)
        if hit is None:
            continue
        count, snippet = hit
        status = "archived" if archived else _own_status(text, kind)
        hits.append({
            "slug": path.parent.name,
            "kind": kind,
            "status": status,
            "snippet": snippet,
            "count": count,
        })
    hits.sort(key=lambda h: (-h["count"], h["slug"]))
    return hits
