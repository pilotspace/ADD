"""Shared parsers for the apply-compaction dogfood (task: apply-compaction).

ONE record-parser per append-only sequence, used by BOTH the red suite and the
transform script so they agree on what a "record" is. Pure reads — no I/O policy,
no transform logic (the reverse+roll lives in apply_compaction.py, under test).

A "record" is:
  - §Key-Decisions : one table data row  -> {date, line}
  - §Method-learnings / §Spec : one top-level `- `/`* ` bullet BLOCK (incl. its
    wrapped continuation lines) -> {maxfv, block}
"""
import re

_DATE_ROW = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|")
_FV = re.compile(r"foundation-version\s+(\d+)")

# settled-line shapes (the frozen §3 contract)
SETTLED_KD = re.compile(r"^\|\s*settled\s+(\d{4}-\d{2}-\d{2})[–-](\d{4}-\d{2}-\d{2})\s*\|\s*(\d+)\b")
SETTLED_ML = re.compile(r"^-\s*settled conventions\s+fv\d+[–-]fv\d+\s+—\s+(\d+)\b")
SETTLED_SPEC = re.compile(r"^-\s*settled\s+fv\d+[–-]fv\d+\s+—")


def _section_lines(text, head_prefix):
    """Lines strictly inside the `## <head_prefix>…` section (until the next `## `)."""
    lines = text.splitlines()
    out, inside = [], False
    for l in lines:
        if l.startswith("## ") and l.startswith("## " + head_prefix):
            inside = True
            continue
        if inside and l.startswith("## "):
            break
        if inside:
            out.append(l)
    return out


def _maxfv(block_text):
    fv = [int(x) for x in _FV.findall(block_text)]
    return max(fv) if fv else None


def _bullets(lines, lead):
    """Group `lines` into top-level bullet blocks; `lead` matches a block opener."""
    blocks, cur = [], None
    for l in lines:
        if lead.match(l):
            if cur is not None:
                blocks.append(cur)
            cur = [l]
        elif cur is not None:
            cur.append(l)
    if cur is not None:
        blocks.append(cur)
    return ["\n".join(b).rstrip() for b in blocks]


def parse_key_decisions(text):
    """Data rows of §Key Decisions, in file order. Skips header + separator rows."""
    out = []
    for l in _section_lines(text, "Key Decisions"):
        if not l.lstrip().startswith("|"):
            continue
        s = l.strip()
        if SETTLED_KD.match(s):
            out.append({"date": None, "line": l, "settled": True})
            continue
        m = _DATE_ROW.match(s)
        if m:
            out.append({"date": m.group(1), "line": l, "settled": False})
    return out


def parse_method_learnings(text):
    blocks = _bullets(_section_lines(text, "Method learnings"), re.compile(r"^- "))
    return [{"maxfv": _maxfv(b), "block": b, "settled": bool(SETTLED_ML.match(b))} for b in blocks]


def parse_spec_bullets(text):
    blocks = _bullets(_section_lines(text, "Spec"), re.compile(r"^[-*] "))
    return [{"maxfv": _maxfv(b), "block": b, "settled": bool(SETTLED_SPEC.match(b))} for b in blocks]


def sequences(text_project, text_conventions):
    """The 3 append-only sequences as record lists."""
    return {
        "key_decisions": parse_key_decisions(text_project),
        "spec": parse_spec_bullets(text_project),
        "method_learnings": parse_method_learnings(text_conventions),
    }


# --- eligibility (the human-approved v1–v20 boundary, frozen §3) -----------------
# Shared by the red suite AND the transform so they classify identically.
ROLL_DATE_CUTOFF = "2026-06-08"   # §Key-Decisions: rows on/before this roll
ROLL_MAXFV_CUTOFF = 20            # §Method-learnings / §Spec: max foundation-version <= this rolls

def is_rolled(seq_name, rec):
    """True iff this record is in the approved oldest, shipped, zero-residue run."""
    if rec.get("settled"):
        return False
    if seq_name == "key_decisions":
        return rec["date"] is not None and rec["date"] <= ROLL_DATE_CUTOFF
    if seq_name == "method_learnings":
        return rec["maxfv"] is not None and rec["maxfv"] <= ROLL_MAXFV_CUTOFF
    if seq_name == "spec":
        # the v1–v20 prose is un-fv-stamped (maxfv None); every fv21+ bullet carries its stamp
        return rec["maxfv"] is None or rec["maxfv"] <= ROLL_MAXFV_CUTOFF
    raise ValueError(seq_name)

def split(seq_name, records):
    """(rolled, kept) — kept excludes any pre-existing settled line."""
    rolled = [r for r in records if is_rolled(seq_name, r)]
    kept = [r for r in records if not is_rolled(seq_name, r) and not r.get("settled")]
    return rolled, kept
