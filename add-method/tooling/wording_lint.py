"""wording_lint.py — the v17 prompt-clarity regression FENCE.

Reads its lists FROM WORDING_RUBRIC.md (single source — no hardcoded duplicate) and checks the
agent-facing surface (skill/add, 19 files). Four collision-free
fences, each able to fail ONLY on a literal regression — never on a good rewrite:

  F1  no ENFORCED banned phrase present     (case-INSENSITIVE, word-boundary, inflection-tolerant)
  F2  no banned emphasis token present       (case-SENSITIVE — the ALL-CAPS shout, not ordinary prose)
  F3  every keep-list term still present     (guards a global rename; over the FULL surface only)
  F4  the rubric is self-consistent          (freeze-time, on WORDING_RUBRIC.md itself)

A count / density / threshold check is refused by design (`metric_gate`): it would false-positive
on a good rewrite — the same failure mode that disqualified v17's behavioral eval as a gate.
That refusal is structural: CHECK_KINDS carries only "fence".

Design for failure: a missing/malformed rubric or an unreadable surface file exits 2 with a named
error — never a silent green pass.

Run:  python3 wording_lint.py                 # full surface
      python3 wording_lint.py --surface a.md  # spot-check specific files (F1+F2 only)
Test: python3 -m unittest test_wording_lint -v
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_TOOLING = Path(__file__).resolve().parent
_SKILL = _TOOLING.parent / "skill" / "add"
_DOCS = _TOOLING.parent / "docs"
DEFAULT_RUBRIC = _TOOLING / "WORDING_RUBRIC.md"

# Every lint check is a FENCE (fails only on a literal regression). No 'metric' kind exists —
# a count/density/threshold is refused as `metric_gate` because it false-positives on good rewrites.
FENCES = ("F1_enforced_banned_absent", "F2_emphasis_token_absent",
          "F3_keep_term_present", "F4_rubric_self_consistent")
CHECK_KINDS = tuple("fence" for _ in FENCES)

_REQUIRED_SECTIONS = ("idiom_map", "enforced_banned", "keep_list",
                      "negative_keep_list", "emphasis_tokens")


class RubricError(Exception):
    """The rubric is missing or malformed — fail loud, never a silent green."""


@dataclass
class Finding:
    file: str
    code: str
    phrase: str


@dataclass
class Rubric:
    enforced_banned: list[str] = field(default_factory=list)
    keep_terms: list[str] = field(default_factory=list)
    emphasis_tokens: list[str] = field(default_factory=list)
    mapped_idioms: list[tuple[str, str]] = field(default_factory=list)
    negative_keep: list[tuple[str, str]] = field(default_factory=list)
    source: str | None = None

    @property
    def banned_phrases(self) -> list[str]:
        """Every phrase the rubric treats as banned: enforced + the (not-yet-enforced) mapped idioms.
        F4 validates the whole set so a self-collision is caught before an idiom is ever promoted."""
        return list(self.enforced_banned) + [idiom for idiom, _ in self.mapped_idioms]


# ── matching ────────────────────────────────────────────────────────────────────────────────
# Boundary = not preceded/followed by a word char OR a hyphen, so a phrase never matches as a
# substring of a larger token ("fold" inside "unfolded", "wall of" inside "firewall office").
def _phrase_re(phrase: str, *, ignorecase: bool) -> re.Pattern[str]:
    """A banned idiom: boundary-guarded, inflection-tolerant (stamp/stamped/stamping), case-insensitive."""
    flags = re.IGNORECASE if ignorecase else 0
    return re.compile(r"(?<![\w-])" + re.escape(phrase) + r"(?:ing|ed|es|s|d)?(?![\w-])", flags)


def _token_re(token: str) -> re.Pattern[str]:
    """An emphasis shout: boundary-guarded, CASE-SENSITIVE, no inflection. Matches the ALL-CAPS
    form only — so the legitimate '## Non-negotiable rules' header and ordinary 'critical' prose
    never trip the fence (case-insensitive here would block a good rewrite)."""
    return re.compile(r"(?<![\w-])" + re.escape(token) + r"(?![\w-])")


# ── parsing (single source of truth) ─────────────────────────────────────────────────────────
def _sections(text: str) -> dict[str, list[str]]:
    """Split a rubric doc into `## <name>` -> [item, ...] for each `- item` bullet. `(none...)`
    bullets resolve to an empty section."""
    out: dict[str, list[str]] = {}
    cur: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            out.setdefault(cur, [])
            continue
        if cur is not None and line.lstrip().startswith("- "):
            item = line.lstrip()[2:].strip()
            if item.lower().startswith("(none"):
                continue
            out[cur].append(item)
    return out


_MAP_RE = re.compile(r"^(?P<idiom>.*?)\s*->\s*(?P<direct>.*?)\s*\[(?P<status>mapped|enforced)\]\s*$")


def load_rubric(path: str | Path | None = None) -> Rubric:
    """Parse WORDING_RUBRIC.md into a Rubric. Raise RubricError on a missing or malformed file."""
    p = Path(path) if path is not None else DEFAULT_RUBRIC
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as e:
        raise RubricError(f"cannot read rubric {p}: {e}") from e

    sec = _sections(text)
    missing = [s for s in _REQUIRED_SECTIONS if s not in sec]
    if missing:
        raise RubricError(f"rubric {p} is missing section(s): {', '.join(missing)}")

    mapped: list[tuple[str, str]] = []
    enforced: list[str] = list(sec["enforced_banned"])
    for item in sec["idiom_map"]:
        m = _MAP_RE.match(item)
        if not m:
            raise RubricError(f"rubric {p}: malformed idiom_map entry: {item!r}")
        if m["status"] == "enforced":
            enforced.append(m["idiom"])
        else:
            mapped.append((m["idiom"], m["direct"]))

    negatives: list[tuple[str, str]] = []
    for item in sec["negative_keep_list"]:
        neg, _, why = item.partition("# why:")
        negatives.append((neg.strip(), why.strip()))

    return Rubric(
        enforced_banned=enforced,
        keep_terms=list(sec["keep_list"]),
        emphasis_tokens=list(sec["emphasis_tokens"]),
        mapped_idioms=mapped,
        negative_keep=negatives,
        source=str(p),
    )


# ── fences ───────────────────────────────────────────────────────────────────────────────────
def lint_text(text: str, rubric: Rubric, source: str) -> list[Finding]:
    """F1 + F2 over one text: an enforced idiom present, or an emphasis shout present."""
    out: list[Finding] = []
    for phrase in rubric.enforced_banned:
        if _phrase_re(phrase, ignorecase=True).search(text):
            out.append(Finding(source, "banned_idiom_present", phrase))
    for tok in rubric.emphasis_tokens:
        if _token_re(tok).search(text):
            out.append(Finding(source, "banned_emphasis_token", tok))
    return out


def keep_term_findings(rubric: Rubric, files: list[Path]) -> list[Finding]:
    """F3: every keep-list term must still appear SOMEWHERE on the surface (a lenient presence
    check — it can only fail when a term has been globally renamed away)."""
    aggregate = "\n".join(_read(f) for f in files).lower()
    return [Finding("<surface>", "keep_term_missing", term)
            for term in rubric.keep_terms if term.lower() not in aggregate]


def validate_rubric(rubric: Rubric) -> list[Finding]:
    """F4 (freeze-time): the rubric is self-consistent.
    - ambiguous_ban: a banned entry that is a bare single word, or a substring of a keep term
      (either would false-positive — exactly what the fence must never do).
    - rubric_self_collision: a direct-form (replacement) that reintroduces a banned phrase."""
    out: list[Finding] = []
    for phrase in rubric.banned_phrases:
        if re.fullmatch(r"[A-Za-z]+", phrase):
            out.append(Finding("<rubric>", "ambiguous_ban", f"{phrase} (single bare word)"))
            continue
        for term in rubric.keep_terms:
            if _phrase_re(phrase, ignorecase=True).search(term):
                out.append(Finding("<rubric>", "ambiguous_ban", f"{phrase} ⊂ keep term {term!r}"))
                break
    for _idiom, direct in rubric.mapped_idioms:
        for phrase in rubric.banned_phrases:
            if _phrase_re(phrase, ignorecase=True).search(direct):
                out.append(Finding("<rubric>", "rubric_self_collision",
                                   f"direct {direct!r} reintroduces banned {phrase!r}"))
    return out


def lint_surface(rubric: Rubric, files: list[Path]) -> list[Finding]:
    """Full surface sweep: F1+F2 per file + F3 presence over the aggregate."""
    out: list[Finding] = []
    for f in files:
        out += lint_text(_read(f), rubric, source=str(f))
    out += keep_term_findings(rubric, files)
    return out


# ── surface + IO ───────────────────────────────────────────────────────────────────────────
def surface_files() -> list[Path]:
    """The canonical agent-facing surface: skill/add (19 files).
    The _bundled & .claude mirrors are byte-identical (test_bundle_parity/test_tree_parity),
    so checking the canonical tree suffices. The book's prompt-library appendix was part of this
    surface until 3.0 cut it — the skill carries the prompting now, so the book is not agent-facing."""
    return sorted(_SKILL.glob("*.md")) + sorted((_SKILL / "phases").glob("*.md"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── CLI ───────────────────────────────────────────────────────────────────────────────────────
def run(argv: list[str] | None = None) -> tuple[int, str]:
    """Returns (exit_code, output). 0 = clean · 1 = findings · 2 = broken rubric / unreadable surface."""
    parser = argparse.ArgumentParser(prog="wording-lint", add_help=False)
    parser.add_argument("--rubric", default=None)
    parser.add_argument("--surface", nargs="+", default=None)
    args = parser.parse_args(argv)

    try:
        rubric = load_rubric(args.rubric)
    except RubricError as e:
        return 2, f"wording-lint: ERROR {e}"

    out = [f"wording-lint: rubric = {rubric.source}"]
    findings = list(validate_rubric(rubric))  # F4 always

    if args.surface is not None:                # spot-check mode: F1+F2 on the named files only
        targets = [Path(s) for s in args.surface]
        include_f3 = False
    else:                                        # full mode: the canonical surface + F3
        targets = surface_files()
        include_f3 = True

    try:
        for f in targets:
            findings += lint_text(_read(f), rubric, source=str(f))
        if include_f3:
            findings += keep_term_findings(rubric, targets)
    except OSError as e:
        return 2, f"wording-lint: ERROR unreadable surface: {e}"

    for fd in findings:
        out.append(f"  {fd.file}: {fd.code}: {fd.phrase}")
    rc = 1 if findings else 0
    out.append(f"wording-lint: {len(findings)} finding(s) — {'FAIL' if rc else 'OK'}")
    return rc, "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    rc, out = run(argv)
    print(out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
