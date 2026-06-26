"""add_engine.taskdoc — TASK.md structural readers (engine-modularization 15/N).

Header, prose, test-count, phase-span, raw phase bodies, and the §7 spec-delta entries —
the pure parsers that read a task document's shape. A closed, unpatched cluster
(transitive-closure AST = zero outbound). The 3 delta-parsing regexes are SHARED with the
deltas-web lint, so they live in constants.py (single source). Deps: constants + components
(_confined) + stdlib; no add.
"""
from __future__ import annotations

import re
from pathlib import Path

from add_engine.constants import _DELTA_RE, _EVIDENCE_RE, _SPEC_DELTA_RE
from add_engine.components import _confined


def _task_header(root: Path, slug: str) -> str:
    """The TASK.md header region — where declared tokens (risk · autonomy)
    live — with HTML comments stripped. Missing file -> '' (no tokens)."""
    try:
        text = (root / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")
    except OSError:
        return ""
    return re.sub(r"<!--.*?-->", "", text.split("\n## ", 1)[0], flags=re.S)

def _count_test_defs(f: Path) -> int:
    """`def test_` occurrences in one file — the ONE counting regex (primary and
    §4-declared fallback share it by construction). OSError -> 0, fail-closed."""
    try:
        return len(re.findall(r"^\s*def test_", f.read_text(encoding="utf-8"), re.M))
    except OSError:
        return 0

def _primary_test_files(root: Path, slug: str) -> list[Path]:
    """The PRIMARY test set — *.py directly in the task's tests/ dir (the stable
    path). A list so the tamper tripwire can hash exactly what the engine counts."""
    d = root / "tasks" / slug / "tests"
    if not d.is_dir():
        return []
    return sorted(d.glob("*.py"))

def _tests_count(root: Path, slug: str) -> int:
    return sum(_count_test_defs(f) for f in _primary_test_files(root, slug))

def _declared_test_files(root: Path, slug: str) -> list[Path]:
    """Resolve the §4 'Tests live in:' declared path(s) to a deduped file list. PURE.
    Tokens are the backticked spans on the FIRST declaring line of the raw §4 body.
    Resolution: './…' -> task dir · contains '/' -> project root (parent of .add) ·
    bare name -> sibling of the previous resolved token (else task dir). A directory
    token yields the *.py files directly inside it; resolved files are deduped.
    v2 confinement: every path must resolve inside the project root — '..' traversal,
    absolute tokens, and symlink escapes are all dropped, fail-closed."""
    body = _raw_phase_bodies(root, slug).get(4, "")
    m = re.search(r"^\s*Tests live in:.*$", body, re.M)
    if not m:
        return []
    tdir = root / "tasks" / slug
    rootp = root.parent.resolve()
    files: list[Path] = []
    prev_dir = None
    for tok in re.findall(r"`([^`]+)`", m.group(0)):
        tok = tok.strip()
        if tok.startswith("./"):
            p = tdir / tok[2:]
        elif "/" in tok:
            p = root.parent / tok
        else:
            p = (prev_dir or tdir) / tok
        try:
            if not _confined(p, rootp):
                continue
            if p.is_dir():
                cand, prev_dir = sorted(f for f in p.glob("*.py")
                                        if _confined(f, rootp)), p
            elif p.is_file() and p.suffix == ".py":
                cand, prev_dir = [p], p.parent
            else:
                continue
        except OSError:
            continue
        files.extend(f for f in cand if f not in files)
    return files

def _declared_tests_count(root: Path, slug: str) -> int:
    """Count tests at the §4 'Tests live in:' declared path(s). PURE, fail-closed 0."""
    return sum(_count_test_defs(f) for f in _declared_test_files(root, slug))

def _tests_info(root: Path, slug: str) -> tuple[int, bool]:
    """(count, declared). The tests/ dir count ALWAYS wins when > 0; otherwise the
    §4-declared fallback — flagged True only when it supplied a non-zero count, so
    a true zero stays a bare, honest 0."""
    primary = _tests_count(root, slug)
    if primary > 0:
        return primary, False
    declared = _declared_tests_count(root, slug)
    return (declared, True) if declared > 0 else (0, False)

def _task_prose(root: Path, slug: str) -> tuple[str, list[str]]:
    """(observe_delta, [delta lines]) from the task's TASK.md §7 — captured at FULL
    fidelity: both fields wrap across physical lines in real files, so continuation
    lines are JOINED. Scoped to the OBSERVE section so we read the FIELD, not §1 prose
    that names it. Fail-closed to '(unknown)' on a missing file / `<...>` placeholder."""
    f = root / "tasks" / slug / "TASK.md"
    if not f.exists():
        return "(unknown)", []
    text = f.read_text(encoding="utf-8")
    m7 = re.search(r"##\s*7\s*·\s*OBSERVE.*\Z", text, re.S)
    section = m7.group(0) if m7 else text
    lines = section.splitlines()
    # observe: prefer the first OPEN SPEC delta from the "### Spec delta" block; fall
    # back to the legacy "Spec delta for the next loop:" free-text field (archived
    # tasks predate the block); else "(unknown)".
    observe = "(unknown)"
    for unit in _spec_delta_entries(section):
        m = _SPEC_DELTA_RE.match(unit[0])
        if m.group(2) != "open":
            continue
        tail = " ".join([m.group(3).strip(), *unit[1:]]).strip()
        em = _EVIDENCE_RE.match(tail)
        first = (em.group(1).strip() if em else tail)
        if first and not first.startswith("<"):
            observe = first
            break
    if observe == "(unknown)":
        for i, ln in enumerate(lines):
            m = re.match(r"\s*Spec delta for the next loop:\s*(.*)", ln)
            if not m:
                continue
            parts = [m.group(1).strip()]
            for nxt in lines[i + 1:]:
                t = nxt.strip()
                if not t or t.startswith("#") or t.startswith("- ") or t.startswith("Watch"):
                    break
                parts.append(t)
            joined = " ".join(p for p in parts if p).strip()
            if joined and not joined.startswith("<"):
                observe = joined
            break

    # deltas: each "- [COMP · status] ..." plus its indented continuation lines
    deltas, i = [], 0
    while i < len(lines):
        m = _DELTA_RE.match(lines[i])
        if not m:
            i += 1
            continue
        parts, j = [m.group(3).strip()], i + 1
        while j < len(lines):
            t = lines[j].strip()
            if not t or t.startswith("#") or _DELTA_RE.match(lines[j]):
                break
            parts.append(t)
            j += 1
        deltas.append(f"{m.group(1)} · {m.group(2)} · {' '.join(parts).strip()}")
        i = j
    return observe, deltas

def _phase_spans(text: str) -> dict[int, str]:
    """Split a TASK.md into RAW §1–§7 bodies keyed by section number — the ONE
    canonical heading scan (`^##\\s*<n>\\s*·`, case/locale-proof); a body runs from
    its heading to the next `## `/`---`/EOF. RAW = byte-faithful lines, no cleaning:
    the decision-marker extractor (decide-digest) depends on byte-verbatim text.
    KNOWN LIMIT: a §body containing a line-start `## ` or bare `---` truncates early —
    today's TASK.md bodies don't (box-chars ─═, `### ` sub-heads)."""
    lines = text.splitlines()
    head = re.compile(r"^##\s*(\d+)\s*·")
    starts: dict[int, int] = {}
    for idx, ln in enumerate(lines):
        m = head.match(ln)
        if m:
            n = int(m.group(1))
            if 0 <= n <= 7 and n not in starts:
                starts[n] = idx
    out: dict[int, str] = {}
    for n, idx in starts.items():
        body_lines = []
        for ln in lines[idx + 1:]:
            if re.match(r"^##\s", ln) or re.match(r"^---\s*$", ln):
                break
            body_lines.append(ln)
        out[n] = "\n".join(body_lines)
    return out

def _raw_phase_bodies(root: Path, slug: str) -> dict[int, str]:
    """RAW §bodies for one task (byte-faithful, for marker extraction). PURE.
    Missing/unreadable TASK.md -> {} (fail-closed, like task_phases)."""
    f = root / "tasks" / slug / "TASK.md"
    try:
        return _phase_spans(f.read_text(encoding="utf-8"))
    except OSError:
        return {}

def _spec_delta_entries(text: str) -> list[list[str]]:
    """Group a "### Spec delta" block into entries (tag line + continuation lines).

    Same grouping discipline as _collect_open_deltas' competency pass, keyed on
    _SPEC_DELTA_RE: a tag line starts an entry; a non-"- " line continues it; a
    blank/comment or a new "- " item ends it. Returns [] when the block is absent."""
    bm = re.search(r"###\s*Spec delta\s*\n(.*?)(?=\n##|\Z)", text, re.S)
    if not bm:
        return []
    entries: list[list[str]] = []
    current: list[str] | None = None
    for line in bm.group(1).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--"):
            current = None
            continue
        if _SPEC_DELTA_RE.match(stripped):
            current = [stripped]
            entries.append(current)
        elif current is not None and not stripped.startswith("-"):
            current.append(stripped)         # genuine wrap of the current entry
        else:
            current = None                   # a new / malformed list item ends the run
    return entries
