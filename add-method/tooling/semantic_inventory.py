"""semantic_inventory.py — the v17 prompt-clarity preservation GATE (the meaning-side twin of wording_lint.py).

Reads its units FROM SEMANTIC_INVENTORY.md (single source — no hardcoded duplicate) and diffs them
against the agent-facing surface (skill/add, 18 files). DETERMINISTIC.
It proves preservation is NECESSARY, not SUFFICIENT — three checks, each failing only on a real regression:

  S1  every frozen token still present IN ITS FILE          (unit_dropped / unit_relocated)
  S2  every invariant's anchors still co-occur in its window (invariant_broken)
  S3  no invariant's negative-anchor sits in its window      (exception_introduced)

plus two FREEZE-TIME self-checks (full mode): every task-1 negative_keep_list item maps to ≥1 invariant
(invariant_uncovered), and the doc names its cede-list (overclaim_sufficient).

Window: S1 = per-file. S2/S3 = ANCHOR-LOCAL — a markdown list-item is its own unit, else the blank-line
paragraph (tighter than a paragraph by necessity: run.md's contiguous auto-gate bullets put RISK-ACCEPTED
next to the security rule; a paragraph window would false-positive at freeze).

A VERBATIM-text diff (verbatim_diff) and a MODEL-judged "same meaning?" check (model_judged_gate) are
refused by design — each mis-gates a good reword. That refusal is structural: CHECK_KINDS carries only "diff".
The INVERSION class (an added exception around surviving anchors) is CEDED, by name, to human review +
the indicative behavioral eval — see SEMANTIC_INVENTORY.md `## cede_list`.

Design for failure: a missing/malformed inventory or an unreadable surface file exits 2 with a named
error — never a silent green.

Run:  python3 semantic_inventory.py                 # full surface + freeze-time checks
      python3 semantic_inventory.py --surface a.md  # spot-check specific files (S1+S2+S3 only)
      python3 semantic_inventory.py --extract       # re-derive the token layer from the surface (drift aid)
Test: python3 -m unittest test_semantic_inventory -v
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import wording_lint as wl  # reuse the canonical 19-file surface + the frozen negative_keep_list

DEFAULT_INVENTORY = Path(__file__).resolve().parent / "SEMANTIC_INVENTORY.md"

GATE_OUTCOMES = ("PASS", "RISK-ACCEPTED", "HARD-STOP", "ESCALATE", "auto-resolved")

# Every check is a deterministic DIFF (token / anchor co-occurrence). No "verbatim" or "model" kind exists —
# a verbatim-text or model-judged check is refused by design because either mis-gates a good reword.
CHECK_KINDS = ("diff", "diff", "diff", "diff", "diff")  # S1 · S2 · S3 · coverage · cede

_REQUIRED_SECTIONS = ("token_layer", "invariants", "coverage", "cede_list")
_NAMED_CODE_RE = re.compile(r"`([a-z][a-z0-9]*_[a-z0-9_]+)`")
_INVARIANT_RE = re.compile(
    r"^(?P<id>[\w-]+)\s*@\s*(?P<file>\S+)\s*\|\s*anchors:\s*(?P<anchors>.*?)"
    r"(?:\s*\|\s*neg:\s*(?P<neg>.*?))?\s*$")


class InventoryError(Exception):
    """The inventory is missing or malformed — fail loud, never a silent green."""


@dataclass
class Finding:
    file: str
    code: str
    unit: str


@dataclass
class Invariant:
    id: str
    file: str
    anchors: list[str] = field(default_factory=list)
    neg_anchors: list[str] = field(default_factory=list)


@dataclass
class Inventory:
    token_layer: list[tuple[str, str]] = field(default_factory=list)   # (token, filespec)
    invariants: list[Invariant] = field(default_factory=list)
    coverage: list[tuple[str, str]] = field(default_factory=list)      # (negative-substring, invariant-id)
    cede_present: bool = False
    source: str | None = None


# ── matching ────────────────────────────────────────────────────────────────────────────────
def _token_present(token: str, text: str) -> bool:
    """A stable identifier: boundary-guarded, CASE-SENSITIVE (PASS, not pass; the snake_case code exactly)."""
    return re.search(r"(?<![\w-])" + re.escape(token) + r"(?![\w-])", text) is not None


def _anchor_present(anchor: str, window: str) -> bool:
    """A semantic anchor: case-insensitive SUBSTRING (lenient — tolerant of inflection/emphasis like
    'auto-passed' or '**security**'; favours a green over a false-red on a good reword)."""
    return anchor.lower() in window.lower()


def _neg_present(neg: str, window: str) -> bool:
    """A forbidden exception word: boundary-guarded (so 'except' never matches 'exception'/'exceptions'),
    case-insensitive. Strict here so S3 fires only on a real added exception, never on reinforcing prose."""
    return re.search(r"(?<![\w-])" + re.escape(neg) + r"(?![\w-])", window, re.IGNORECASE) is not None


def units(text: str) -> list[str]:
    """Smallest natural text units: a markdown list-item is its own unit; otherwise a blank-line
    paragraph. The tightest window that holds run.md's contiguous auto-gate bullets apart."""
    out: list[str] = []
    cur: list[str] = []
    for line in text.splitlines():
        is_item = re.match(r"^\s*([-*]|\d+\.)\s", line)
        if not line.strip():
            if cur:
                out.append("\n".join(cur))
                cur = []
        elif is_item:
            if cur:
                out.append("\n".join(cur))
            cur = [line]
        else:
            cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return out


def window_for(text: str, anchors: list[str]) -> str | None:
    """The unit holding the PRIMARY anchor (anchors[0]) where the MOST anchors co-occur."""
    if not anchors:
        return None
    primary = anchors[0]
    cands = [u for u in units(text) if _anchor_present(primary, u)]
    if not cands:
        return None
    return max(cands, key=lambda u: sum(_anchor_present(a, u) for a in anchors))


# ── parsing (single source of truth) ─────────────────────────────────────────────────────────
def _sections(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    cur: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            out.setdefault(cur, [])
            continue
        if cur is not None and line.lstrip().startswith("- "):
            out[cur].append(line.lstrip()[2:].strip())
    return out


def load_inventory(path: str | Path | None = None) -> Inventory:
    """Parse SEMANTIC_INVENTORY.md into an Inventory. Raise InventoryError on a missing/malformed file."""
    p = Path(path) if path is not None else DEFAULT_INVENTORY
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as e:
        raise InventoryError(f"cannot read inventory {p}: {e}") from e

    sec = _sections(text)
    missing = [s for s in _REQUIRED_SECTIONS if s not in sec]
    if missing:
        raise InventoryError(f"inventory {p} is missing section(s): {', '.join(missing)}")

    token_layer: list[tuple[str, str]] = []
    for item in sec["token_layer"]:
        filespec, _, toks = item.partition(":")
        if not toks.strip():
            raise InventoryError(f"inventory {p}: malformed token_layer entry: {item!r}")
        for tok in (t.strip() for t in toks.split(",")):
            if tok:
                token_layer.append((tok, filespec.strip()))

    invariants: list[Invariant] = []
    for item in sec["invariants"]:
        m = _INVARIANT_RE.match(item)
        if not m:
            raise InventoryError(f"inventory {p}: malformed invariant entry: {item!r}")
        anchors = [a.strip() for a in m["anchors"].split(",") if a.strip()]
        negs = [n.strip() for n in (m["neg"] or "").split(",") if n.strip()]
        invariants.append(Invariant(m["id"], m["file"], anchors, negs))

    coverage: list[tuple[str, str]] = []
    for item in sec["coverage"]:
        key, _, inv_id = item.partition("->")
        if inv_id.strip():
            coverage.append((key.strip(), inv_id.strip()))

    return Inventory(
        token_layer=token_layer,
        invariants=invariants,
        coverage=coverage,
        cede_present=bool(sec.get("cede_list")),
        source=str(p),
    )


def negative_keep_list() -> list[tuple[str, str]]:
    """The 5 frozen task-1 safety negatives (read from WORDING_RUBRIC.md — the single source coupling
    task 2's coverage check to task 1's frozen artifact)."""
    return wl.load_rubric().negative_keep


# ── surface + IO ───────────────────────────────────────────────────────────────────────────
def surface_files() -> list[Path]:
    """The same canonical 19-file surface wording_lint checks (single source of the file list)."""
    return wl.surface_files()


def _resolve(filespec: str, files: list[Path]) -> Path | None:
    fs = filespec.replace("\\", "/")
    for f in files:
        s = str(f).replace("\\", "/")
        if f.name == fs or s.endswith("/" + fs):
            return f
    return None


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _scope_to(inv: Inventory, files: list[Path]) -> Inventory:
    """Spot-check helper: keep only the units whose declared file is among `files`, so checking a
    SUBSET (e.g. `--surface run.md`) never flags another file's tokens as dropped. Full mode passes
    the whole 19-file surface, so nothing is dropped there."""
    return Inventory(
        token_layer=[(t, fs) for t, fs in inv.token_layer if _resolve(fs, files)],
        invariants=[iv for iv in inv.invariants if _resolve(iv.file, files)],
        coverage=inv.coverage,
        cede_present=inv.cede_present,
        source=inv.source,
    )


# ── checks ───────────────────────────────────────────────────────────────────────────────────
def check_tokens(inv: Inventory, files: list[Path]) -> list[Finding]:
    """S1: every frozen token present IN ITS FILE — else unit_relocated (it moved) or unit_dropped (it's gone)."""
    texts = {f: _read(f) for f in files}
    out: list[Finding] = []
    for token, filespec in inv.token_layer:
        target = _resolve(filespec, files)
        if target is not None and _token_present(token, texts[target]):
            continue
        elsewhere = any(_token_present(token, t) for f, t in texts.items() if f is not target)
        out.append(Finding(filespec, "unit_relocated" if elsewhere else "unit_dropped", token))
    return out


def check_invariants(inv: Inventory, files: list[Path]) -> list[Finding]:
    """S2 + S3: anchors co-occur in the window (else invariant_broken); no neg-anchor in it (else exception_introduced)."""
    out: list[Finding] = []
    for iv in inv.invariants:
        target = _resolve(iv.file, files)
        if target is None:
            out.append(Finding(iv.file, "invariant_broken", f"{iv.id} (file gone)"))
            continue
        text = _read(target)
        win = window_for(text, iv.anchors)
        missing = iv.anchors if win is None else [a for a in iv.anchors if not _anchor_present(a, win)]
        if missing:
            out.append(Finding(iv.file, "invariant_broken", f"{iv.id} missing anchors {missing}"))
            continue
        hit = [n for n in iv.neg_anchors if _neg_present(n, win)]
        if hit:
            out.append(Finding(iv.file, "exception_introduced", f"{iv.id} exception {hit}"))
    return out


def check_coverage(inv: Inventory, negatives: list[tuple[str, str]]) -> list[Finding]:
    """Freeze-time: every safety negative maps (via a coverage key) to ≥1 existing invariant — else invariant_uncovered."""
    ids = {iv.id for iv in inv.invariants}
    out: list[Finding] = []
    for neg, _why in negatives:
        covered = any(key.lower() in neg.lower() and inv_id in ids for key, inv_id in inv.coverage)
        if not covered:
            out.append(Finding("<inventory>", "invariant_uncovered", neg))
    return out


def check_cede(inv: Inventory) -> list[Finding]:
    """Freeze-time: the doc must NAME its cede-list — an inventory that claims preservation without naming
    what it cedes is the overclaim this gate forbids."""
    return [] if inv.cede_present else [Finding("<inventory>", "overclaim_sufficient", "cede_list missing/empty")]


def lint_surface(inv: Inventory, files: list[Path], negatives: list[tuple[str, str]]) -> list[Finding]:
    """Full check: S1 + S2/S3 over the surface + the two freeze-time self-checks."""
    return (check_tokens(inv, files) + check_invariants(inv, files)
            + check_coverage(inv, negatives) + check_cede(inv))


def extract_tokens(files: list[Path]) -> dict[str, list[str]]:
    """Re-derive the token layer from the surface (drift aid): gate_outcomes present + backticked snake_case codes."""
    out: dict[str, list[str]] = {}
    for f in files:
        text = _read(f)
        found = {o for o in GATE_OUTCOMES if _token_present(o, text)}
        found |= set(_NAMED_CODE_RE.findall(text))
        if found:
            out[str(f)] = sorted(found)
    return out


# ── CLI ───────────────────────────────────────────────────────────────────────────────────────
def run(argv: list[str] | None = None) -> tuple[int, str]:
    """Returns (exit_code, output). 0 = clean · 1 = findings · 2 = broken inventory / unreadable surface."""
    parser = argparse.ArgumentParser(prog="semantic-inventory", add_help=False)
    parser.add_argument("--inventory", default=None)
    parser.add_argument("--surface", nargs="+", default=None)
    parser.add_argument("--extract", action="store_true")
    args = parser.parse_args(argv)

    try:
        inv = load_inventory(args.inventory)
    except InventoryError as e:
        return 2, f"semantic-inventory: ERROR {e}"

    out = [f"semantic-inventory: inventory = {inv.source}"]

    try:
        if args.extract:
            for path, toks in extract_tokens(surface_files()).items():
                out.append(f"  {Path(path).name}: {', '.join(toks)}")
            out.append("semantic-inventory: extract (drift aid — not auto-frozen)")
            return 0, "\n".join(out)

        if args.surface is not None:                      # spot-check: S1+S2+S3 on the named files only
            targets = [Path(s) for s in args.surface]
            scoped = _scope_to(inv, targets)              # only judge units that live in the named files
            findings = check_tokens(scoped, targets) + check_invariants(scoped, targets)
        else:                                             # full: the canonical surface + freeze-time checks
            findings = lint_surface(inv, surface_files(), negative_keep_list())
    except OSError as e:
        return 2, f"semantic-inventory: ERROR unreadable surface: {e}"

    for fd in findings:
        out.append(f"  {fd.file}: {fd.code}: {fd.unit}")
    rc = 1 if findings else 0
    out.append(f"semantic-inventory: {len(findings)} finding(s) — {'FAIL' if rc else 'OK'}")
    return rc, "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    rc, output = run(argv)
    print(output)
    return rc


if __name__ == "__main__":
    sys.exit(main())
