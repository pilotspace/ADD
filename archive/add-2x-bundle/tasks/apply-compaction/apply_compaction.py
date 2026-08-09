"""apply-compaction transform (build deliverable, realizes §3 FROZEN @ v1).

Dogfoods foundation compaction on the LIVE specs: per sequence, REVERSE the records
newest-first then ROLL the approved v1–v20 tail into ONE settled line at the bottom.
Segment-based splice — each record keeps its own lines verbatim (continuations + blanks
ride along), only the order changes and the rolled run is summarized. Multiset-preserving
on the kept run (asserted). Rolled records survive in git history (the "see git" pointer).

Run once from the task dir:  python3 apply_compaction.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compaction_lib as cl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PROJECT = os.path.join(ROOT, ".add", "PROJECT.md")
CONVENTIONS = os.path.join(ROOT, ".add", "CONVENTIONS.md")

SETTLED = {
    "spec": "- settled fv1–fv20 — ADD bootstrapping → production-ready: SDD foundation · self-driving run · one-approval auto · awareness surface · decision-point reports · zero-command on-ramp · prompt & file hygiene · dynamic loop (see git)",
    "key_decisions": "| settled 2026-05-28–2026-06-08 | 48 foundational decisions rolled (v1.0 npm scope → v20 dynamic loop) | bootstrapping through production-ready ADD | see git |",
    "method_learnings": "- settled conventions fv2–fv20 — 67 method learnings rolled (early ADD/TDD/SDD discipline) (see git)",
}


def _section_bounds(lines, head_prefix):
    start = next(i for i, l in enumerate(lines) if l.startswith("## " + head_prefix))
    end = next((i for i, l in enumerate(lines) if i > start and l.startswith("## ")), len(lines))
    return start, end


def _segments(lines, lo, hi, is_start):
    """Partition lines[lo:hi] into record segments (a start line + its trailing lines).
    Returns (first_idx, last_content_idx, [segment_line_lists]). Leading non-record lines
    (table header/separator, the blank after a heading) are excluded from segmentation."""
    first = next(i for i in range(lo, hi) if is_start(lines[i]))
    last_content = max(i for i in range(first, hi) if lines[i].strip())
    starts = [i for i in range(first, last_content + 1) if is_start(lines[i])]
    segs = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else last_content + 1
        segs.append(lines[s:e])
    return first, last_content, segs


def _maxfv(text):
    fv = [int(x) for x in cl._FV.findall(text)]
    return max(fv) if fv else None


def _transform_block_seq(lines, head_prefix, name, is_start):
    start, end = _section_bounds(lines, head_prefix)
    first, last_content, segs = _segments(lines, start + 1, end, is_start)
    recs = [{"block": "\n".join(s), "maxfv": _maxfv("\n".join(s)), "settled": False} for s in segs]
    rolled, kept = cl.split(name, recs)
    _assert_preserved(name, recs, rolled, kept)
    kept_segs = [segs[i] for i, r in enumerate(recs) if r in kept]
    new_region = [ln for seg in reversed(kept_segs) for ln in seg] + [SETTLED[name]]
    return lines[:first] + new_region + lines[last_content + 1:], len(rolled)


def _transform_key_decisions(lines):
    start, end = _section_bounds(lines, "Key Decisions")
    is_row = lambda l: bool(cl._DATE_ROW.match(l.strip()))
    first = next(i for i in range(start, end) if is_row(lines[i]))
    last = max(i for i in range(first, end) if is_row(lines[i]))
    rows = lines[first:last + 1]
    recs = [{"line": r, "date": cl._DATE_ROW.match(r.strip()).group(1), "settled": False} for r in rows]
    rolled, kept = cl.split("key_decisions", recs)
    _assert_preserved("key_decisions", recs, rolled, kept)
    kept_rows = [r["line"] for r in reversed(kept)]
    new_region = kept_rows + [SETTLED["key_decisions"]]
    return lines[:first] + new_region + lines[last + 1:], len(rolled)


def _assert_preserved(name, recs, rolled, kept):
    ident = (lambda r: r["line"].strip()) if name == "key_decisions" else (lambda r: r["block"].strip())
    orig = [ident(r) for r in recs]
    got = [ident(r) for r in rolled] + [ident(r) for r in kept]
    assert sorted(orig) == sorted(got), f"{name}: reverse/roll partition is not multiset-preserving"
    assert len(rolled) + len(kept) == len(recs), f"{name}: record count drift"


def main():
    proj = open(PROJECT, encoding="utf-8").read().split("\n")
    proj, n_spec = _transform_block_seq(proj, "Spec", "spec", lambda l: bool(re.match(r"[-*] ", l)))
    proj, n_kd = _transform_key_decisions(proj)
    open(PROJECT, "w", encoding="utf-8").write("\n".join(proj))

    conv = open(CONVENTIONS, encoding="utf-8").read().split("\n")
    conv, n_ml = _transform_block_seq(conv, "Method learnings", "method_learnings", lambda l: l.startswith("- "))
    open(CONVENTIONS, "w", encoding="utf-8").write("\n".join(conv))

    print(f"rolled — §Spec:{n_spec}  §Key-Decisions:{n_kd}  §Method-learnings:{n_ml}")


if __name__ == "__main__":
    main()
