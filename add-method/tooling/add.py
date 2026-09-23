#!/usr/bin/env python3
"""add — the ADD engine for ABF-1 bundles. Python stdlib only, one file.

e1 slice: node I/O. Everything else in the engine calls through here.

Two rules shape this module, and both come from the format:

* **Reads are tiered** (FORMAT law 2). `read(path, tier)` returns exactly its tier and
  no more: T0 is frontmatter, T1 adds `## CARD`, T2 adds the whole body. A tier that
  leaks is a context cost the format exists to remove.
* **Writes are surgical, never regenerative** (task `port-okf-parse`, R:REGEN). A node
  is held as BOTH a parsed dict (to read) and its original raw frontmatter text (to
  write). Changing a key rewrites one line region and leaves every other byte — comments,
  key order, blank lines, block scalars — exactly as the human left it. Serialising a
  parsed dict back to YAML would silently strip the rationale comments this bundle
  carries, which is why no such function exists here.

The parser covers the ABF-1 subset and nothing more: top-level scalars, block lists,
inline lists, inline flow maps, block scalars, nested maps, and lists of flow maps.
Anything outside it survives in `raw` and is simply absent from the dict — never
half-parsed into a plausible wrong value.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path, PurePosixPath

FENCE = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)
BLOCK_SCALARS = {">", ">-", ">+", "|", "|-", "|+"}


# --------------------------------------------------------------------- scanning


def _strip_comment(line: str) -> str:
    """Drop a trailing `#` comment, honouring quotes. A `#` inside a value is data."""
    if "#" not in line:            # the overwhelmingly common line, at C speed
        return line
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1].isspace()):
            return line[:i]
    return line


def _scalar(value: str):
    value = value.strip()
    if value in ("[]", "{}"):
        return [] if value == "[]" else {}
    if value.startswith("[") and value.endswith("]"):
        return [_scalar(v) for v in _split_commas(value[1:-1]) if v.strip()]
    if value.startswith("{") and value.endswith("}"):
        return _flow_map(value)
    if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


_SPECIALS = re.compile(r'["\'{}\[\],]')


def _split_commas(text: str) -> list[str]:
    """Split on commas that sit outside quotes and outside nested braces.

    Jumps between the characters that can change state (one compiled search per special)
    instead of visiting every character in Python — a receipt's `{ path, blob }` line has
    ~4 specials in ~60 characters, and this function runs once per frontmatter list item."""
    out, depth, quote, start, i = [], 0, None, 0, 0
    while True:
        m = _SPECIALS.search(text, i)
        if not m:
            break
        ch, i = m.group(), m.end()
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
        elif ch == "," and depth == 0:
            out.append(text[start:i - 1])
            start = i
    out.append(text[start:])
    return out


def _flow_map(text: str) -> dict:
    """`{ by: x, at: 2026-07-29T08:00Z }` — split pairs on the FIRST colon only, so a
    timestamp or a `human:actor` value keeps its own colons."""
    data = {}
    for pair in _split_commas(text.strip().lstrip("{").rstrip("}")):
        key, sep, value = pair.partition(":")
        if sep:
            data[key.strip()] = _scalar(value)
    return data


def _open_quote(text: str) -> bool:
    """True when `text` ends inside an unterminated quoted string.

    Scanned, never counted. An apostrophe in `the node's own body` makes the single-quote count
    odd while opening nothing, because the value is already inside double quotes. Counting
    instead of tracking state made a continuation run to the end of the frontmatter and swallow
    `budget`, `generated` and `verified` across 25 nodes of this bundle — with the full suite
    green and the M0 validator reporting CONFORMS.

    A quote OPENS only at a token boundary (start of text, or after a space / `{` / `,` / `[`).
    That is YAML's own rule, and its absence was this bug's second incarnation: state-tracking
    fixed the count, then opened on the mid-word apostrophe in `the caller's own transfer
    history` — an UNQUOTED item — and the continuation swallowed every key below it, including
    the `verified:` stamps, so `sealed_direction` returned None and the freeze seal silently
    stopped verifying. Same green suite, same CONFORMS. A mid-word quote is plain content.

    Jumps from quote to quote with `str.find` (C speed between the state changes) — this runs
    once per frontmatter list item, and a quote-sparse line costs two finds instead of a
    per-character Python loop.
    """
    quote, i = None, 0
    while True:
        if quote:
            j = text.find(quote, i)
            if j == -1:
                return True
            quote, i = None, j + 1
        else:
            jd, js = text.find('"', i), text.find("'", i)
            j = (min(jd, js) if jd != -1 and js != -1 else (jd if js == -1 else js))
            if j == -1:
                return False
            if j == 0 or text[j - 1] in " \t{,[":
                quote = text[j]
            i = j + 1


def _tokens(raw: str) -> list[tuple[int, str]]:
    lines = []
    for line in raw.splitlines():
        stripped = _strip_comment(line)
        if stripped.strip():
            lines.append((len(stripped) - len(stripped.lstrip()), stripped.strip()))
    return lines


def _block(toks: list[tuple[int, str]], i: int, indent: int):
    """Parse one block at `indent`; return (value, index after it)."""
    if toks[i][1].startswith("- "):
        items = []
        while i < len(toks) and toks[i][0] >= indent and toks[i][1].startswith("- "):
            text, i = toks[i][1][2:], i + 1
            # A list item may wrap: an unclosed flow map, or an unclosed quote. Both are
            # continued until they balance. Without the quote arm a wrapped `"…"` was cut at
            # the first newline and KEPT its opening quote, so the value parsed to something
            # plausible and wrong — found by e5 rendering a `gives:` into a brief, after this
            # had survived 132 checks, the M0 validator and five human gates.
            while i < len(toks) and (text.count("{") > text.count("}") or _open_quote(text)):
                text, i = text + " " + toks[i][1], i + 1
            items.append(_scalar(text))
        return items, i

    data = {}
    while i < len(toks) and toks[i][0] >= indent:
        if toks[i][0] > indent:  # deeper than this block: not ours to claim
            i += 1
            continue
        key, sep, value = toks[i][1].partition(":")
        if not sep:
            i += 1
            continue
        key, value, i = key.strip(), value.strip(), i + 1
        if value in BLOCK_SCALARS:
            folded = []
            while i < len(toks) and toks[i][0] > indent:
                folded.append(toks[i][1])
                i += 1
            data[key] = " ".join(folded) if value.startswith(">") else "\n".join(folded)
        elif value == "" and i < len(toks) and toks[i][0] > indent:
            data[key], i = _block(toks, i, toks[i][0])
        elif value == "":
            data[key] = []
        else:
            data[key] = _scalar(value)
    return data, i


# ------------------------------------------------------------------ public read


def split(text: str):
    """(raw_frontmatter, body). `(None, text)` when there is no parseable fence.

    Find-based, exactly FENCE's lazy semantics (the closing fence is the FIRST `\\n---` after
    the opening one, optional trailing newline) — the regex walked megabyte documents one
    lazy-dot step at a time, which priced every `read` of a large receipt before a single
    line was parsed. FENCE stays defined as the semantic reference this must keep matching."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    rest = text[end + 4:]
    return text[4:end], (rest[1:] if rest.startswith("\n") else rest)


def parse(text: str):
    """(frontmatter_dict, body). Never raises — a malformed node is the caller's finding
    to record, not this function's exception to throw (FORMAT law 3)."""
    raw, body = split(text)
    if raw is None:
        return None, body
    try:
        toks = _tokens(raw)
        return (_block(toks, 0, 0)[0] if toks else {}), body
    except Exception:  # a notary reports; it does not crash the caller
        return None, text


def card_of(body: str) -> str:
    """The `## CARD` section only — T1 stops where the next `## ` heading starts."""
    out, inside = [], False
    for line in body.splitlines(keepends=True):
        if line.startswith("## "):
            if inside:
                break
            inside = line.strip() == "## CARD"
            continue
        if inside:
            out.append(line)
    return "".join(out).strip()


def read(path: Path, tier: str = "T0") -> dict:
    """Read one node at exactly `tier` (FORMAT §4). Nothing past the tier is returned."""
    if tier not in ("T0", "T1", "T2"):
        raise ValueError(f"unknown tier {tier!r} — expected T0, T1 or T2")
    text = Path(path).read_text(encoding="utf-8")
    raw, body = split(text)
    fm, _ = parse(text)
    return {
        "path": Path(path),
        "fm": fm,
        "raw": raw,
        "card": card_of(body) if tier in ("T1", "T2") else "",
        "body": body if tier == "T2" else "",
    }


# ---------------------------------------------------------------- public write


def _key_line(raw: str, key: str) -> int:
    for n, line in enumerate(raw.splitlines()):
        if line.startswith(f"{key}:"):
            return n
    return -1


def set_key(raw: str, key: str, value: str) -> str:
    """Replace one top-level key's scalar value. Every other byte survives, including a
    trailing comment on the same line."""
    lines = raw.splitlines()
    n = _key_line(raw, key)
    if n < 0:
        return raw + f"\n{key}: {value}"
    stripped = _strip_comment(lines[n])
    comment = lines[n][len(stripped):]
    lines[n] = f"{key}: {value}" + comment
    return "\n".join(lines)


def append_item(raw: str, key: str, item: str) -> str:
    """Append one item to a top-level block list, matching the block's own indentation."""
    lines = raw.splitlines()
    n = _key_line(raw, key)
    if n < 0:
        return raw + f"\n{key}:\n  - {item}"
    # An inline empty list (`verified: []`) becomes a block list on first append. Without
    # this the item lands under a surviving `[]` and parses back as empty — found by e4,
    # because e1's suite only ever appended to a list that already had items.
    head = _strip_comment(lines[n])
    if head.partition(":")[2].strip() == "[]":
        lines[n] = f"{key}:" + lines[n][len(head):]
    last, indent = n, "  "
    for i in range(n + 1, len(lines)):
        body = _strip_comment(lines[i])
        if body.strip().startswith("- "):
            last, indent = i, body[: len(body) - len(body.lstrip())]
        elif body.strip():
            break
    lines.insert(last + 1, f"{indent}- {item}")
    return "\n".join(lines)


def write(path: Path, text: str) -> None:
    """Atomic single-file replace. The temp file shares the target's directory, because
    `os.replace` is only atomic within one filesystem. On failure the original is
    untouched and no debris is left behind."""
    path = Path(path)
    tmp = path.with_name(f".{path.name}.tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


# ===================================================================== the graph (e2)
#
# One compiled graph, built from T0 reads. Every other verb reads this instead of walking
# the tree itself. Three rules from the format shape it:
#
# * **Edges come from an allowlist, never a heuristic** (§3.3). `scope:` holds repo paths and
#   `persona_corpus:` a config path; a scanner that guessed would read `templates/task.md.tmpl`
#   as a link to `/task.md` — observed 2026-07-29.
# * **Fragments resolve in a fixed order** (§3.3): frontmatter key first, heading slug second,
#   `edge_unresolved` third. Ordered, so one reference can never resolve two ways.
# * **Activity is derived, never stored** (§3.4). There is no pointer to corrupt.

EDGE_KEYS = ("depends_on", "needs", "tasks", "milestone", "relates_to", "task", "supersedes")

# A milestone whose history is PUBLISHED: its goal-gate answered, its exit boxes checked. Named
# once, so `reopen` and any later reader ask one list ("shipped" is a release word, not a close).
CLOSED_MILESTONE_STATES = ("done", "archived")

# The SECOND edge family (FORMAT §3.2). `relations:` carries typed edges between CONCEPTS —
# `<source delta id> <rel> <target ref>` — where `EDGE_KEYS` carries untyped edges between NODES.
#
# Two decisions are load-bearing and were both measured, not assumed:
#
# * **`relations` is NOT in `EDGE_KEYS`.** `edges()` yields `(src, key, ref, target)`; a relation
#   folded into that shape loses BOTH the source id and the rel, and `_norm` on the unsplit entry
#   is a containment hole: `_norm("/specs/method.md", "refines /specs/../../outside.md")` returns
#   `/specs/outside.md`, which is INSIDE the bundle — so `edge_out_of_bundle`, one of the three
#   FATAL codes, downgrades to `info`. The head is stripped BEFORE the target is normalised.
# * **The entry is a block-list PLAIN STRING, never a flow map.** `- { rel: refines, target: x }`
#   parses to a dict here and to the raw brace string in `scripts/validate_bundle.py`: one file,
#   two values, no error anywhere. Three whitespace-separated fields parse identically in both.
#
# Closed, and closed SMALL — ONE term, because one term is what the corpus earns. `contradicts`,
# `evidenced_by` and `derived_from` were cut before drafting for having zero instances
# (`evidenced_by` doubly: every delta line already carries an in-band `(evidence: ...)` that
# `DELTA_EVIDENCE` enforces). `supersedes` got further — it was drafted, given a migration
# instance, and cut at VERIFY when that instance was refuted on measurement: its candidate was
# `M28 supersedes M19`, and the phantom-verb fixture M19 enumerates still exists, so M28 does not
# replace M19 — they are overlapping siblings, and M19 is still `open`.
#
# Three of the seven keys in `EDGE_KEYS` (`tasks`, `relates_to`, `supersedes`) have ZERO live uses.
# That is the measured base rate a term with no instance joins, so the bar is a live instance in
# the same change, not a plausible use. Widening this tuple is an engine change held to that bar.
RELATION_VOCAB = ("refines",)
ACTIVE_STATES = ("direction", "build", "verify")
CACHE_NAME = "graph.json"


# ------------------------------------------------- the scan-path read (evidence deferred)
#
# A Run receipt's frontmatter is mostly EVIDENCE: `scope_digest` is one `{path, blob}` entry
# per file in the task's scope, and `passed`/`failed` are the reported test ids. Measured on
# this bundle before this task: 97 receipts held 7979 digest entries and 953 id lines, and
# were 68% of ALL T0 parse time — a cost every command paid, including `status`, the first
# command of every session. Both terms grow monotonically and nothing prunes them: the digest
# grows with the repo (66 -> 103 entries per receipt in three weeks) and receipts are
# append-only, so the scan was O(every receipt ever recorded).
#
# Nothing in the GRAPH ever read it. The payload's only consumers — `fresh()` and the gate's
# coverage map — are both fed by `latest_receipt()`, which does its own direct single-node
# `read()`. So the graph paid for a payload it never looked at.
#
# `raw` is taken from the ORIGINAL text, never from the stripped copy (M2, R:LOSSYRAW). The
# one write path does its own `read()` today, but a lean `raw` would be a loaded gun for the
# next writer that does not — it would drop every digest line on save, silently.
_EVIDENCE_BLOCK = re.compile(r"^  (?:scope_digest|passed|failed):[ \t]*\n(?:[ \t]+- .*\n)*", re.M)


def _read_for_graph(path: Path) -> dict:
    """`read(path, "T0")`, minus a Run receipt's evidence payload (FORMAT §4).

    Anchored to the two-space indent the receipt block is written at, so a TOP-LEVEL key that
    happens to be called `passed:` on some other node is untouched (E2).
    """
    text = Path(path).read_text(encoding="utf-8")
    raw, _ = split(text)
    if "  scope_digest:" in text or "  passed:" in text or "  failed:" in text:
        fm, _ = parse(_EVIDENCE_BLOCK.sub("", text))
    else:
        fm, _ = parse(text)
    return {"path": Path(path), "fm": fm, "raw": raw, "card": "", "body": ""}


def cid_of(root: Path, path: Path) -> str:
    """A bundle-absolute concept ID (OKF §2): `/tasks/x.md`, never a filesystem path."""
    return "/" + Path(path).relative_to(root).as_posix()


def scan(root, strays: list = None) -> dict:
    """Every node in the bundle at T0. Bodies are not read here (law 2).

    `strays`, if given, is a caller-owned list that collects the relative path of every `.md`
    carrying no frontmatter. Contract EXTENDED after this task's gate at human authority (see
    `/tasks/compile-graph.md` `## PLAN`): a graph is right to drop non-nodes, but `doctor` then
    inherits blindness to `missing_frontmatter` — the M0 oracle's most consequential error, and
    the one F6 proved real when a command wrote `.pytest_cache/README.md` into this bundle.
    Strays are NOT nodes and never become keys: every consumer iterates `graph.items()` expecting
    cid -> node, so a foreign key would be F4's silent-wrong-value class, deliberately rebuilt.
    """
    root = Path(root)
    graph = {}
    for path in sorted(root.rglob("*.md")):
        if path.relative_to(root).parts[0] in ("tooling", "personas-teacher", "personas-index"):
            continue  # vendored engine material, the seed corpus, and its generated routing index —
            # never project graph, never a stray. Kept in lockstep with validate_bundle.load()'s twin list:
            # a vendored file this oracle skips but the other reads reds as `missing_frontmatter`.
        node = _read_for_graph(path)
        if node["fm"] is None:
            if strays is not None:
                strays.append(path.relative_to(root).as_posix())
            continue  # not a node — log.md and prose files are data, not graph
        node["cid"] = cid_of(root, path)
        node["root"] = root
        graph[node["cid"]] = node
    return graph


def _norm(src_cid: str, ref: str) -> str:
    """Resolve a reference to a cid. Bundle-absolute wins; relative resolves against `src`."""
    target = ref.partition("#")[0].strip()
    if not target:
        return src_cid
    if target.startswith("/"):
        return target
    base = PurePosixPath(src_cid).parent
    return "/" + str(PurePosixPath(os.path.normpath(str(base / target)))).lstrip("/")


# `milestone:` is the ONE edge key whose value may be a bare slug (§3.2). The reason is a
# property of the key, not a convenience: membership implies exactly one directory, so the slug
# names a cid without guessing. Every other key may point at more than one node type —
# `depends_on:` may name a Task or a Milestone — so no directory is implied there and a bare
# value stays unresolved, which is what keeps `edge_unresolved` meaningful.
#
# Measured before this arm existed: `milestone:` was declared on 45 of 220 nodes and produced
# ZERO edges, because both oracles skip any ref without `.md`. A key in the allowlist that can
# never yield an edge reads as wired and traverses nothing.
MEMBERSHIP_KEY = "milestone"
MEMBERSHIP_DIR = "milestones"
_SLUG = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._-]*\Z")


def _membership_ref(key: str, ref: str) -> str:
    """A bare-slug `milestone:` value -> the cid it names; `""` when the value is not one.

    Containment needs no special case: a value carrying `/` or `..` fails `_SLUG`, so it never
    reaches this mapping and is judged on the `.md` path like every other ref. The mapping can
    only ever produce a path under `MEMBERSHIP_DIR`, which is inside the root by construction.

    The RESERVED names are excluded (§3.1): `index.md` and `log.md` are COMPILED from the nodes,
    so a membership edge into one would point at a derived artifact rather than a milestone. No
    live instance exists — but a mapping that CAN name a reserved file eventually will.
    """
    if key != MEMBERSHIP_KEY or ".md" in ref or not _SLUG.match(ref):
        return ""
    return "" if f"{ref}.md" in NOT_A_NODE else f"/{MEMBERSHIP_DIR}/{ref}.md"


def edges(graph: dict) -> list:
    """`[(src_cid, key, ref, target_cid|None)]` — typed, and only from EDGE_KEYS.

    `ref` is always the value as WRITTEN, never the mapped form: a membership slug and the
    explicit `.md` ref for the same milestone resolve to one target but stay distinguishable to
    a reader of the tuple, so a report can quote what the author typed.
    """
    out = []
    for cid, node in graph.items():
        for key in EDGE_KEYS:
            value = (node["fm"] or {}).get(key)
            if value is None:
                continue
            for ref in value if isinstance(value, list) else [value]:
                ref = str(ref).strip()
                if ".md" not in ref:
                    if not (mapped := _membership_ref(key, ref)):
                        continue
                    out.append((cid, key, ref, mapped if mapped in graph else None))
                    continue
                target = _norm(cid, ref)
                out.append((cid, key, ref, target if target in graph else None))
    return out


def parse_relation(entry) -> tuple:
    """One `relations:` entry as `(src_id, rel, ref)`; `(None, None, raw)` when it is malformed.

    Exactly three whitespace-separated fields — `split()`, never `split(None, 2)`. Capping the
    split would silently accept a fourth field by folding it into the target, which is the
    "unknown reads as clean" shape this bundle has a delta about. A value that is not three
    fields carries no resolvable target and therefore makes NO containment claim: it is reported
    `relation_malformed` and yields no edge. That residual is stated in FORMAT §3.2 rather than
    left implicit, because a containment check that did not run must never look like one that
    passed.
    """
    text = str(entry).strip()
    fields = text.split()
    return tuple(fields) if len(fields) == 3 else (None, None, text)


def relations(graph: dict) -> list:
    """`[(src_cid, src_id, rel, ref, target_cid|None)]` — one tuple per entry, malformed included.

    A malformed entry yields `(cid, None, None, raw, None)` rather than being dropped: a reader
    that silently skips what it cannot parse is one whose empty report cannot be trusted.
    """
    out = []
    for cid, node in graph.items():
        value = (node["fm"] or {}).get("relations")
        if not value:
            continue          # absent, `[]`, `{}` or empty — no relations (A8). `not value`, never
            # `is None`: a bare `- ` list item parses to `{}` here and to an empty LIST in the M0
            # oracle, so `is None` reported one `relation_malformed` against the validator's
            # silence. An empty value is an empty value in both.
        for entry in (value if isinstance(value, list) else [value]):
            src_id, rel, ref = parse_relation(entry)
            if rel is None:
                out.append((cid, None, None, ref, None))
                continue
            target = _norm(cid, ref)
            out.append((cid, src_id, rel, ref, target if target in graph else None))
    return out


# ------------------------------------------------------- the neighbourhood walk (okf-graph-lookup)
#
# `edges()` and `relations()` are flat lists and `cycles()` walks ONE direction of ONE family.
# This is the walk a reader gets: bounded, cycle-safe, and totally ordered so two calls over an
# unchanged bundle are byte-identical.
#
# The unit is the EDGE, not the visit. One edge is emitted once — at the shallowest depth the
# walk reaches it, from whichever end it arrived — because the same link seen outbound from one
# node and inbound at the other is one fact, and emitting it twice doubles every diamond.
NEIGHBORHOOD_MAX = 5         # the ceiling a caller may ask for; the verb refuses above it
NEIGHBORHOOD_DEFAULT = 3     # the walk a caller gets when it names no depth


def neighborhood(graph: dict, cid: str, expand: int = NEIGHBORHOOD_DEFAULT) -> tuple:
    """`(rows, note)` — every edge within `expand` levels of `cid`, both families, both directions.

    A row is `(depth, direction, family, label, origin, src, ref, target)`. `origin` is the
    address of the concept that DECLARED the edge — a lesson address like `/specs/method.md#M8`
    for a relation, and the node's own cid for a node edge, which is declared by the node itself.
    It is an ADDED field, not a redefined `src`, so a consumer that joined on `src` keeps working.
    Without it two lessons refining one target collapsed into a single row, because the delta id
    is the ONLY thing that tells them apart (R:COLLAPSE). `direction` is `"out"` when
    the walk followed the edge from its source and `"in"` when it arrived at its target, `family`
    is `"edge"` (an `EDGE_KEYS` node edge) or `"relation"` (a typed `relations:` concept edge),
    and `label` is the edge key or the rel word. `src`/`target` always describe the edge AS
    WRITTEN, so a row reads the same whichever end the walk came from.

    `rows is None` marks a REFUSAL and only a refusal — `cid` names no node. An empty list is a
    recorded answer: this node exists and has no edges within `expand`. Collapsing the two would
    make "no neighbours" and "no such node" one value (R:EMPTYISUNKNOWN).

    Law 1 holds: the walk reads the graph it is handed, never `graph.json`.
    """
    # A concept address is a legitimate start (§3.3): a lesson is a thing this bundle addresses
    # but does not store as a file, and a reader standing on one wants what refines it. It is
    # admitted only when the lesson EXISTS, so an unknown address refuses in the grammar an
    # unknown cid gets rather than walking an empty graph and reporting "no edges" (M2 · A8).
    if cid not in graph and _concept_of(graph, *cid.partition("#")[::2]) is None:
        return None, (f'`{cid}` names no node in this bundle -> "R:NOSUCHNODE"'
                      "\nnext: add status   # the nodes this bundle actually holds")

    # Both adjacencies built ONCE. A malformed `relations:` entry yields no edge (§3.2) and so
    # joins neither: it carries no resolvable target and therefore makes no claim to walk.
    fwd, rev = {}, {}
    for src, key, ref, target in edges(graph):
        # A node edge is declared by the node itself, so there is no finer identity to carry.
        fwd.setdefault(src, []).append(("edge", key, src, ref, target))
        if target is not None:
            rev.setdefault(target, []).append(("edge", key, src, ref, src))
    # A relation's two ends are CONCEPTS, and the walk joins them as such. `_norm` strips the
    # fragment BY DESIGN — a node edge like `needs: /specs/x.md#gives` must resolve to the FILE,
    # and `resolve`, `brief` and the containment codes all depend on that — so the address is
    # rebuilt HERE, for this family alone (R:NODEEDGEDRIFT). Before this, both ends were the
    # file: `M8 refines /specs/method.md#M4` emitted a row reading `refines /specs/method.md`,
    # and a reader standing on M4 found nothing at all (R:FILEASCONCEPT).
    hosts = {}          # file cid -> the concept addresses that file hosts
    for src, src_id, rel, ref, target in relations(graph):
        if rel is None:
            continue
        # The declaring LESSON, at the address `search` and `deltas` already cite it by. An
        # id-less legacy head degrades to the file, exactly as `delta_address` degrades.
        origin = delta_address(src.rsplit("/", 1)[-1][:-3], src_id)
        dest = _concept_of(graph, target, ref.partition("#")[2].strip()) if target else None
        if dest is None and target is not None and "#" not in ref:
            dest = target                     # E1 — a fragment-less relation still names the file
        fwd.setdefault(origin, []).append(("relation", rel, origin, ref, dest))
        if dest is not None:
            rev.setdefault(dest, []).append(("relation", rel, origin, ref, origin))
        # Containment, not a hop: a file's concepts are walked AT THE FILE'S OWN DEPTH, so
        # `show <spec> --expand 1` still costs one level and still shows what the spec declares
        # (M4 · A5). The descent is one-way — from a concept the walk does NOT climb back into
        # its file, or standing on one lesson would drag in every relation its neighbours wrote.
        for address in (origin, dest):
            if address and "#" in address:
                hosts.setdefault(address.partition("#")[0], set()).add(address)

    # `best` keys the EDGE — including WHO DECLARED IT, so two lessons refining one target stay
    # two edges. The shallowest sighting wins and a second one neither duplicates the row nor
    # re-expands the node behind it.
    best, seen, frontier = {}, {cid}, [cid]
    for depth in range(1, max(0, int(expand)) + 1):
        nxt = set()
        for node in frontier:
            for probe in [node] + sorted(hosts.get(node, ())):
                for family, label, origin, ref, other in fwd.get(probe, []):
                    best.setdefault((family, label, origin, probe, ref, other), (depth, "out"))
                    if other is not None and other not in seen:
                        nxt.add(other)
                for family, label, origin, ref, other in rev.get(probe, []):
                    best.setdefault((family, label, origin, other, ref, probe), (depth, "in"))
                    if other not in seen:
                        nxt.add(other)
        seen |= nxt
        frontier = sorted(nxt)
        if not frontier:
            break

    rows = [(d, direction, family, label, origin, src, ref, target)
            for (family, label, origin, src, ref, target), (d, direction) in best.items()]
    # Every field participates, so no tie reaches dict or set order (R:SILENTORDER). `target` is
    # `None` for an unresolved edge, which no comparison with a string may touch.
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7] or ""))
    if not rows:
        return [], (f"`{cid}` has no edges within {expand} level(s)"
                    "\nnext: add status")
    return rows, (f"{len(rows)} edge(s) within {expand} level(s) of `{cid}`"
                  "\nnext: cite one as a depends_on: or relations: target")


RESOLVE_CANDIDATES = 8       # candidates an ambiguity refusal lists before it starts counting


def resolve_ref(root, ref: str) -> tuple:
    """A bare slug, a filename or a cid -> EXACTLY one cid. `(cid, note)`; `None` marks a refusal.

    It never best-guesses. `cli._resolve` returns `/tasks/<ref>.md` for anything it cannot find,
    which hands the engine a cid that does not exist and lets the refusal come from somewhere
    that cannot name the real problem. Zero matches refuse; several refuse and LIST the
    candidates, because a reader who typed an ambiguous name needs to see what they collided
    with, not to be given one of them.
    """
    graph = scan(Path(root))
    text = str(ref or "").strip()
    nowhere = ("\nnext: add status   # the nodes this bundle actually holds")
    if not text:
        return None, 'an empty ref names no node -> "R:NOREF"' + nowhere
    # A CONCEPT address. `deltas` and `search` both print `/specs/<lens>.md#<id>` and both tell
    # the reader to cite it; until this branch nothing could read it back, so the only way to see
    # one lesson was to read the file holding thirty of them (R:WHOLESPEC).
    if "#" in text:
        file_part, _, frag = text.partition("#")
        file_cid = "/" + file_part.lstrip("/")
        # The FILE first: an unreadable path is a path error, and reporting it as a missing
        # lesson would name the wrong half of the address (A4).
        if file_cid in graph and file_cid.startswith("/specs/") and frag:
            lens = file_cid.rsplit("/", 1)[-1][:-3]
            named = [i for s in DELTA_STATUSES for i in deltas(root, status=s)[0]
                     if i[0] == lens and i.id == frag]
            if len(named) == 1:
                return f"{file_cid}#{frag}", f"`{file_cid}#{frag}`"
            if not named:
                return None, (f'`{frag}` names no lesson in `{file_cid}` -> "R:NOSUCHNODE"'
                              f"\nnext: add deltas --lens {lens}   # the lessons it does hold")
            return None, (f'`{frag}` names {len(named)} lessons in `{file_cid}`, and a read '
                          f'must not choose one of them -> "R:IDCOLLIDE"'
                          f"\nnext: add deltas --lens {lens}   # disambiguate by hand")
    if "/" in text or text.endswith(".md"):
        cid = "/" + text.lstrip("/")
        if cid in graph:
            return cid, f"`{cid}`"
        # A ref carrying `/` was meant literally and stops here — second-guessing a path would
        # reopen the guessing this verb refuses (A2). A bare FILENAME falls through: it named a
        # node that exists, and refusing it asserted something false about the bundle, which is
        # the failure this function was written to end (R:FALSEREFUSAL).
        if "/" in text:
            return None, f'`{text}` names no node in this bundle -> "R:NOSUCHNODE"' + nowhere
        text = text[:-3]
    matches = sorted(c for c in graph if c.rsplit("/", 1)[-1] == f"{text}.md")
    if len(matches) == 1:
        return matches[0], f"`{matches[0]}`"
    if not matches:
        return None, f'`{text}` names no node in this bundle -> "R:NOSUCHNODE"' + nowhere
    # Bounded, for the reason the depth cap is bounded: one read must not cost unbounded
    # context. `add show 1` listed 78 candidates on a live bundle and grew with the task count.
    # The shown set is the deterministic PREFIX of the sorted order, so the refusal reproduces.
    shown = matches[:RESOLVE_CANDIDATES]
    listed = "\n".join(f"  \u00b7 {m}" for m in shown)
    withheld = len(matches) - len(shown)
    more = f"\n  \u00b7 … and {withheld} more" if withheld else ""
    return None, (f'`{text}` names {len(matches)} nodes, and a read must not choose one of them '
                  f'-> "R:GUESS"\n{listed}{more}'
                  f"\nnext: add show {matches[0]}   # name one of the cids above")


def _show_lesson(root, graph: dict, address: str, expand: int) -> tuple:
    """One LESSON read whole. `(view, note)` — the same shape `show` returns for a node.

    A lesson is a concept the bundle addresses (§3.3) but does not store as a file, so the view
    carries its parsed head as `fm` and its text as `body`. Its `rows` are the typed relations
    declared BY it, ordered by `neighborhood` so two reads are byte-identical.
    """
    file_cid, _, frag = address.partition("#")
    lens = file_cid.rsplit("/", 1)[-1][:-3]
    item = next(i for s in DELTA_STATUSES for i in deltas(root, status=s)[0]
                if i[0] == lens and i.id == frag)
    status = next(s for s in DELTA_STATUSES
                  if any(j.id == frag and j[0] == lens for j in deltas(root, status=s)[0]))
    fm = {"type": "Lesson", "lens": lens, "status": status, "competency": item[1]}
    if item.valid_from:
        fm["valid_from"] = item.valid_from
    if item.valid_to:
        fm["valid_to"] = item.valid_to
    # The walk starts AT the concept now, not at its file: standing on a lesson, what you want
    # first is what refines it, and filtering the file's walk down to rows this lesson declared
    # could only ever show the outbound half. `related:` was structurally empty for every lesson
    # that was refined rather than refining.
    rows = [r for r in (neighborhood(graph, address, expand)[0] or []) if r[2] == "relation"]

    dash, dot, down = "\u2014", "\u00b7", "\u2193"
    head = f" {dot} ".join(str(fm[k]) for k in ("type", "lens", "competency") if fm.get(k))
    span = f"  {fm.get('valid_from', dash)}" + (f" \u2192 {fm['valid_to']}" if fm.get("valid_to") else "")
    lines = [f"{address}  [{status}]  {head}{span}".rstrip(), "", item[2], ""]
    if rows:
        up = "\u2191"
        lines.append(f"related (depth {expand} \u00b7 {down} refines \u00b7 {up} refined by):")
        lines += [f"  {r[0]} {down if r[1] == 'out' else up} {r[3]}  "
                  f"{(r[7] if r[1] == 'out' else r[5]) or (dash + ' unresolved')}" for r in rows]
    else:
        lines.append(f"related: none within {expand} level(s)")
    lines.append(f"next: add deltas --lens {lens}   # the rest of this lens")
    view = {"cid": address, "fm": fm, "body": item[2], "rows": rows}
    return view, "\n".join(lines)


def show(root, ref: str, expand: int = NEIGHBORHOOD_DEFAULT) -> tuple:
    """One node read WHOLE, with its neighbourhood. `(view, note)`. Read-only, never writes.

    `view is None` marks a REFUSAL and only a refusal. The view carries `cid`, `fm`, `body` and
    `rows` — the node's own content plus `neighborhood()`'s rows — so a caller renders it without
    re-reading the file.

    The depth is validated FIRST, before the ref is resolved, so an over-cap request is refused
    by the flag the operator actually typed rather than by whatever the walk did with it. The
    cap REFUSES; it never clamps. A clamp reports success for a question nobody asked, which is
    the failure shape this whole milestone is built to avoid.
    """
    if expand > NEIGHBORHOOD_MAX:
        return None, (f'--expand {expand} is past the ceiling of {NEIGHBORHOOD_MAX} — a walk is '
                      f'capped so one read cannot cost unbounded context -> "R:DEPTHCAP"'
                      f"\nnext: add show {ref} --expand {NEIGHBORHOOD_MAX}")
    if expand < 0:
        return None, (f'--expand {expand} is not a depth -> "R:DEPTHCAP"'
                      f"\nnext: add show {ref} --expand {NEIGHBORHOOD_DEFAULT}")

    cid, note = resolve_ref(root, ref)
    if cid is None:
        return None, note

    graph = scan(Path(root))
    if "#" in cid:
        return _show_lesson(root, graph, cid, expand)
    node = read(graph[cid]["path"], "T2")
    rows, _walk = neighborhood(graph, cid, expand)
    view = {"cid": cid, "fm": node["fm"] or {}, "body": node["body"] or "", "rows": rows or []}

    fm = view["fm"]
    dash, dot, down, up = "\u2014", "\u00b7", "\u2193", "\u2191"
    head = f" {dot} ".join(str(fm[k]) for k in ("type", "depth", "sensitivity") if fm.get(k))
    status = fm.get("status") or dash
    # The title rides the header: `show` named the cid, the beat and the type, and the one thing
    # a reader actually wants — what this node is FOR — was only in the CARD, or missing when the
    # CARD was still scaffold.
    titled = _title_of(fm)
    lines = [f"{cid}  [{status}]  {head}{('  ·  ' + titled) if titled else ''}".rstrip()]
    # A released milestone answers "which tree shipped, proven by which receipts" in its header
    # (release-stamp, M5): one line per `act: release` stamp, oldest first, never the body's.
    for st in fm.get("verified") or []:
        if isinstance(st, dict) and st.get("act") == "release":
            lines.append(f"act: release {dot} {st.get('tag')} {dash} tree {str(st.get('tree'))[:12]} "
                         f"{dot} receipts {st.get('receipts') or dash} {dot} by {st.get('by')} at {st.get('at')}")
    lines.append("")
    lines.append(view["body"].rstrip())
    if view["rows"]:
        lines += ["", f"related (depth {expand} {dot} {down} declared here {dot} "
                      f"{up} declared elsewhere):"]
        width = max(len(r[3]) for r in view["rows"])
        for depth, direction, family, label, origin, src, _ref, target in view["rows"]:
            arrow = down if direction == "out" else up
            other = target if direction == "out" else src
            # The declaring lesson's ID, not its whole address: the row already prints the other
            # end, so repeating the file would spend width twice on one fact. Without it two
            # lessons refining one target render as two identical-looking lines (A9).
            mark = "" if family == "edge" else f"  (relation {origin.split('#')[-1]})"
            state = (graph.get(other or "", {}).get("fm") or {}).get("status")
            shown = other or f"{dash} unresolved"
            tag = f"  [{state}]" if state else ""
            lines.append(f"  {depth} {arrow} {label:<{width}}  {shown}{tag}{mark}")
        lines.append(f"{dash} {len(view['rows'])} edge(s) within {expand} level(s)")
    else:
        lines += ["", f"related: none within {expand} level(s)"]
    lines.append(f"next: add show {cid} --expand 1   # the immediate neighbours only")
    return view, "\n".join(lines)


def _concept_of(graph: dict, file_cid: str, frag: str) -> str:
    """`/specs/x.md#M4` when `frag` names a lesson that file really holds, else None.

    The ONE place a concept address is minted for the walk. It reads the target's own body
    through `_delta_ids`, so a fragment the delta grammar rejects mints nothing: an address the
    bundle cannot dereference must never appear as an edge's target (R:PHANTOMTARGET).
    """
    if not frag or file_cid not in graph:
        return None
    if frag not in _delta_ids(read(graph[file_cid]["path"], "T2")["body"]):
        return None
    return file_cid + "#" + frag


def _delta_ids(body: str) -> dict:
    """`{delta id: the whole line}` — §3.3's THIRD fragment form, read from a node's own body.

    Read through `parse_delta_head`, never through a looser regex of its own: a laxer reader here
    would resolve a fragment the engine's own delta grammar rejects, and the two would disagree
    about what a concept address means. First occurrence wins — ids are unique per file
    (R:REUSEDID) and a duplicate must resolve deterministically rather than by scan order.
    """
    out = {}
    for line in live_lines(body):
        match = DELTA_LINE.match(line.strip())
        if not match:
            continue
        head = parse_delta_head(match.group(1))
        if head["code"] is None and head["id"]:
            out.setdefault(head["id"], line.strip())
    return out


def authored_section(body, heading: str) -> str:
    """The `## <heading>` section as the AUTHORING walker sees it — fences blanked, the heading
    canonicalised, and only the seven sections a human writes in.

    `_section_of` on a raw body is a FIFTH reader of "where a section is": it matches `## RULES`
    spelled exactly that way, at column zero, wherever it appears — so `## RULES (frozen)`, `##
    RULES:` and an indented heading all read as NO section, and a ```` ```markdown ```` example of
    the grammar reads as THE section. `rules_of` was routed through `_authored_rules` for exactly
    this reason (E30); the SEAL and the INTERVIEW were not, and the twenty-eighth T2 refute walked
    through the gap: on such a node `confirm` wrote a Must's `(from: …)` tail and `direction_digest`
    did not move — a sourced and an unsourced Must sealed alike (R:DIGESTDRIFT) — because the whole
    Must/Reject payload was outside the seal, which also let a frozen Must be replaced under a
    build with no drift refusal at all. Same fact, one reader.
    """
    return _section_of(_authored_rules(str(body or "")), heading)

def _section(body: str, slug: str) -> str:
    """The body section under the heading whose kebab-cased text is `slug`.

    Read through the ONE heading walker (`_headings`): this slicer deciding for itself what a
    heading is made it a SECOND reader of the rule — fence-blind, so a heading spelled only inside
    a fenced example opened a section, and `_prevention_resolves` consults `resolve` FIRST, so a
    quoted `## my example` addressed a section a prevention bound to while the `- E9` beside it
    was correctly refused (twenty-second T2 refute, E36).
    """
    out, inside = [], False
    for line, level, name in _headings(body):
        # Level TWO only: M2 freezes "a deeper `###` opens none", and the authoring walk reads a
        # `#` title and a `###` sub-heading as CONTENT of the section they sit in. This slicer
        # opened a section for each, so a prevention naming one folded (E37).
        if level == 2:
            if inside:
                break
            inside = "-".join(re.findall(r"[a-z0-9]+", (name or "").lower())) == slug
            continue
        if inside:
            out.append(line)
    return "\n".join(out).strip()


def _is_template(value) -> bool:
    """True when a frontmatter value is still scaffold — `<…>` placeholder text.

    An unauthored value must not SHADOW a real one. Scaffolding `gives:` (so it stops
    being a phantom instruction) gave every Task the frontmatter key, and §3.3 resolves
    a frontmatter key before a heading slug — which silently redirected every `#gives`
    ref away from an authored `## GIVES` section to the placeholder above it. A slot
    nobody has filled is not an answer, so resolution falls through to the heading.
    """
    items = [i for i in (value if isinstance(value, list) else [value])
             if i is not None and str(i).strip() != ""]
    # EMPTY is unauthored too: `scope:` seeds empty and `verified:` starts `[]`, and both resolved
    # — a prevention named a key nobody had filled and the escape folded (E37). Same law as the
    # placeholder: a slot nobody has filled is not an answer.
    return not items or all("<" in str(i) and ">" in str(i) for i in items)


def resolve(graph: dict, ref: str, src: str = "") -> tuple:
    """`(cid, value, why)` under §3.3's ordered grammar.

    `why` is one of `node` · `frontmatter` · `heading` · `edge_unresolved`. Frontmatter wins
    even when a same-named heading exists, so a reference can never resolve two ways.
    """
    cid = _norm(src or ref, ref)
    fragment = ref.partition("#")[2].strip()
    node = graph.get(cid)
    if node is None:
        return cid, None, "edge_unresolved"
    if not fragment:
        return cid, node, "node"
    fm = node["fm"] or {}
    for key in (fragment, fragment.replace("-", "_")):
        if key in fm and not _is_template(fm[key]):
            return cid, fm[key], "frontmatter"
    # Only now is a body read, and only this one (law 2 — never a bulk scan). ONE read, three
    # forms: the heading slug, then the delta id, then unresolved.
    body = read(node["path"], "T2")["body"]
    section = _section(body, fragment)
    if section:
        return cid, section, "heading"
    # §3.3's third form (`typed-relations`). LAST before unresolved, deliberately: a fragment that
    # resolves today must keep resolving the same way, and a delta id carries an upper-case letter
    # while a heading slug is lower-cased, so the two sets cannot collide and a reference still
    # cannot resolve two ways.
    delta = _delta_ids(body).get(fragment)
    return (cid, delta, "delta") if delta else (cid, None, "edge_unresolved")


def active(graph: dict) -> list:
    """Active iff `status` is direction|build|verify (§3.4). Nothing is stored."""
    return sorted(c for c, n in graph.items()
                  if (n["fm"] or {}).get("status") in ACTIVE_STATES)


def ready(graph: dict) -> list:
    """Active tasks whose every `depends_on` target is `done` — the frontier."""
    out = []
    for cid in active(graph):
        node = graph[cid]
        if (node["fm"] or {}).get("type") != "Task":
            continue
        deps = (node["fm"] or {}).get("depends_on") or []
        if all((graph.get(_norm(cid, d), {}).get("fm") or {}).get("status") == "done"
               for d in (deps if isinstance(deps, list) else [deps])):
            out.append(cid)
    return out


def cycles(graph: dict) -> list:
    """Every dependency cycle, as lists of cids. Iterative, so a bad bundle reports (law 3).

    Tarjan's SCC with an explicit stack — a recursive walk would raise RecursionError on a
    deep or cyclic graph, which is the crash R:CYCLECRASH forbids.
    """
    adj = {c: [] for c in graph}
    for src, key, ref, target in edges(graph):
        if target and key in ("depends_on", "needs", "supersedes"):
            adj[src].append(target)

    index, low, on, stack, counter, found = {}, {}, set(), [], [0], []
    for start in graph:
        if start in index:
            continue
        work = [(start, iter(adj[start]))]
        index[start] = low[start] = counter[0]; counter[0] += 1
        stack.append(start); on.add(start)
        while work:
            node, children = work[-1]
            nxt = next(children, None)
            if nxt is None:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[node])
                if low[node] == index[node]:
                    comp = []
                    while True:
                        w = stack.pop(); on.discard(w); comp.append(w)
                        if w == node:
                            break
                    if len(comp) > 1 or node in adj[node]:
                        found.append(sorted(comp))
            elif nxt not in index:
                index[nxt] = low[nxt] = counter[0]; counter[0] += 1
                stack.append(nxt); on.add(nxt)
                work.append((nxt, iter(adj[nxt])))
            elif nxt in on:
                low[node] = min(low[node], index[nxt])
    return found


def _wave_slug(ref) -> str:
    """A cid, a `.md` ref, or a bare slug -> the bare slug (`/tasks/a.md` -> `a`)."""
    return str(ref).rsplit("/", 1)[-1].removesuffix(".md") if ref else ""


def wave(root, milestone_ref, streams=None):
    """Plan a parallel wave from the task DAG (M1–M5).

    A wave is safe to run concurrently only when its streams are BOTH mutually independent (an
    antichain in the `depends_on`/`needs` DAG) AND write-disjoint (no shared `scope:`). This proves
    both from the graph; it never assumes them. The engine stays NO-EXEC — it plans and records; the
    skill creates the worktrees and spawns the builders.

    `streams=None` -> derive the maximal-parallel schedule: topological LEVELS, each a maximal
    antichain (returns `(levels, note)`, levels = list of slug-lists). `streams=[…]` -> validate that
    explicit set is an antichain and scope-disjoint, then record it as the milestone's `active_wave:`
    (returns `(picks, note)`). Any refusal returns `(None, "R:…")`.
    """
    root = Path(root)
    graph = scan(root)
    mslug = _wave_slug(milestone_ref)
    members = {cid: n for cid, n in graph.items()
               if (n["fm"] or {}).get("type") == "Task"
               and _wave_slug((n["fm"] or {}).get("milestone")) == mslug}
    if not members:
        return None, (f"no tasks under milestone `{mslug}` — nothing to plan\n"
                      f"next: add new task <slug> --milestone {mslug}")

    # A cycle among members has no defined parallel plan (M5). Reuse the graph-wide detector, then
    # keep only components that actually touch this milestone.
    for comp in cycles(graph):
        if len(comp) > 1 and any(c in members for c in comp):
            names = ", ".join(sorted(_wave_slug(c) for c in comp if c in members))
            return None, f'R:CYCLE dependency cycle among {names} — no parallel plan on a cyclic graph -> "R:CYCLE"'

    # Member-restricted dependency adjacency: src waits on target (both in this milestone).
    dep = {cid: set() for cid in members}
    for src, key, ref, target in edges(graph):
        if key in ("depends_on", "needs") and src in members and target in members:
            dep[src].add(target)

    def _reaches(a, b) -> bool:
        """Does `a` depend (transitively) on `b`?"""
        seen, stack = set(), [a]
        while stack:
            for y in dep.get(stack.pop(), ()):
                if y == b:
                    return True
                if y not in seen:
                    seen.add(y); stack.append(y)
        return False

    if streams is None:
        placed, levels, remaining = set(), [], dict(dep)
        while remaining:
            layer = sorted(cid for cid, ds in remaining.items() if ds <= placed)
            if not layer:  # defensive — the cycle guard above should already have refused
                return None, 'R:CYCLE unresolvable dependency among members -> "R:CYCLE"'
            levels.append([_wave_slug(c) for c in layer])
            placed |= set(layer)
            for c in layer:
                remaining.pop(c)
        plan = "\n".join(f"  L{i}: {' · '.join(lvl)}" for i, lvl in enumerate(levels))
        return levels, (f"wave plan for `{mslug}` — {len(levels)} level(s), each a parallel antichain:\n{plan}\n"
                        f"next: add wave {mslug} --streams {','.join(levels[0])}")

    # An explicit stream set: it must be a valid antichain, scope-disjoint, all real members.
    # A stream may carry a lens: `slug:persona`. Split it; `picks` stays bare slugs for the
    # antichain/scope proofs, `lens` maps the streams that named a persona.
    picks, lens = [], {}
    for s in streams:
        slug, _, persona = str(s).partition(":")
        slug = _wave_slug(slug)
        picks.append(slug)
        if persona:
            lens[slug] = persona
    by_slug = {_wave_slug(c): c for c in members}
    missing = [s for s in picks if s not in by_slug]
    if missing:
        return None, f'R:NOSTREAM not a task under `{mslug}`: {", ".join(missing)} -> "R:NOSTREAM"'
    # A lens must resolve to a Persona node — record only a real, seeded lens (R:BADPERSONA).
    persona_slugs = {_wave_slug(cid) for cid, n in graph.items() if (n["fm"] or {}).get("type") == "Persona"}
    for slug, persona in lens.items():
        if persona not in persona_slugs:
            return None, (f'R:BADPERSONA `{persona}` is not a Persona node in the bundle — '
                          f'seed it first (`add new Persona {persona}`) -> "R:BADPERSONA"')
    # The sensitivity floor carries into the wave: a stream whose task needs more than `process`
    # authority (data · architecture · security) must carry a lens, or refuse — before any write.
    for slug in picks:
        sens = (members[by_slug[slug]]["fm"] or {}).get("sensitivity")
        if SENSITIVITY_FLOOR.get(sens, "process") != "process" and slug not in lens:
            return None, (f'R:NOLENS stream `{slug}` is `{sens}` (floor above process) but carries no '
                          f'lens — assign one (`{slug}:<persona>`) so the standard has an owner -> "R:NOLENS"')
    for i in range(len(picks)):
        for j in range(i + 1, len(picks)):
            a, b = by_slug[picks[i]], by_slug[picks[j]]
            if _reaches(a, b) or _reaches(b, a):
                return None, (f'R:INTRADEP {picks[i]} and {picks[j]} have a dependency path — '
                              f'sequence them across waves, not within one -> "R:INTRADEP"')
    scopes = {s: {str(x) for x in _scope_list(members[by_slug[s]]["fm"])} for s in picks}
    for i in range(len(picks)):
        for j in range(i + 1, len(picks)):
            common = scopes[picks[i]] & scopes[picks[j]]
            if common:
                return None, (f'R:OVERLAP {picks[i]} and {picks[j]} both write {sorted(common)[0]} — '
                              f'disjoint scope is the write-safety invariant -> "R:OVERLAP"')
    # Stamp the lens on each stream node (NO-EXEC: a record of the AI's choice, never an execution).
    for slug, persona in lens.items():
        npath = root / by_slug[slug].lstrip("/")   # by_slug[slug] is the cid, e.g. "/tasks/a.md"
        tn = read(npath, "T2")
        write(npath, f"---\n{set_key(tn['raw'], 'persona', persona)}\n---\n{tn['body']}")
    tokens = [f"{s}:{lens[s]}" if s in lens else s for s in picks]
    mpath = root / "milestones" / f"{mslug}.md"
    n = read(mpath, "T2")
    write(mpath, f"---\n{set_key(n['raw'], 'active_wave', '[' + ', '.join(tokens) + ']')}\n---\n{n['body']}")
    lensed = " · ".join(f"{s}→{lens[s]}" if s in lens else s for s in picks)
    return picks, (f"wave recorded on `{mslug}`: {lensed} build in parallel (disjoint scope, no intra-dep)\n"
                   f"next: build each stream in its worktree, then add join")


def advise(root, cid: str, persona: str) -> tuple:
    """Record a persona lens on a SEQUENTIAL beat: stamp `advised_by: <persona>`. NO-EXEC.

    The parallel path records this via `wave`→`join`; this is the sequential twin — a first-class,
    validated record of who advised a beat, and exactly what A2's security floor (R:NOCOVERAGE)
    consumes. The engine RECORDS the AI's chosen lens; it never runs, spawns, or judges the persona,
    and a lens never lowers a gate. Re-advising re-routes (the value is replaced, never appended).
    """
    root = Path(root)
    graph = scan(root)
    if cid not in graph:
        return None, f"no such node: {cid}\nnext: add status"
    node_type = (graph[cid]["fm"] or {}).get("type")
    if node_type not in LIFECYCLE_TYPES:
        return None, (f'R:NOTATASK only a lifecycle node (Task/Milestone) carries a lens — '
                      f'`{cid}` is a {node_type} -> "R:NOTATASK"')
    # Same roster resolution `wave` uses: the lens must name a real, seeded Persona node.
    persona_slugs = {_wave_slug(c) for c, n in graph.items() if (n["fm"] or {}).get("type") == "Persona"}
    if persona not in persona_slugs:
        return None, (f'R:BADPERSONA `{persona}` is not a Persona node in the bundle — '
                      f'seed it first (`add new Persona {persona}`) -> "R:BADPERSONA"')
    n = read(graph[cid]["path"], "T2")
    write(graph[cid]["path"], f"---\n{set_key(n['raw'], 'advised_by', persona)}\n---\n{n['body']}")
    slug = cid.rsplit("/", 1)[-1][:-3]
    return persona, (f"`{slug}` advised by `{persona}` — recorded (NO-EXEC: the lens advises; it never "
                     f"freezes or gates)\nnext: add brief {slug}")


def _last_gate_outcome(fm: dict):
    """The `outcome` of the last `act: gate` stamp in `verified[]`, or None if never gated."""
    outcome = None
    for s in (fm or {}).get("verified") or []:
        if isinstance(s, dict) and s.get("act") == "gate":
            outcome = s.get("outcome")
    return outcome


def _effective_gate_stamp(fm: dict):
    """Latest readable gate after reopen; a verdictless legacy gate cannot clear a known stop."""
    stamps = [s for s in (fm or {}).get("verified") or [] if isinstance(s, dict)]
    last_reopen = max((i for i, s in enumerate(stamps) if s.get("act") == "reopen"),
                      default=-1)
    gates = [s for s in stamps[last_reopen + 1:] if s.get("act") == "gate"]
    readable = ("PASS", "RISK-ACCEPTED", "HARD-STOP")
    return next((s for s in reversed(gates) if str(s.get("outcome")) in readable),
                gates[-1] if gates else None)


def _delta_lines(body: str) -> list:
    """Every delta in a spec body as ONE item — its head line plus the continuation lines the
    grammar joins into it (`joined_deltas`), text unchanged.

    Harvesting head lines alone dropped a wrapped escape's whole tail on the way into main, so a
    delta the stream's own `fold` refused R:UNPREVENTED folded there at exit 0: the readers joined
    the unit and the writers severed it (tenth T2 refute, E22).
    """
    # Membership comes from the ONE reader of it (`delta_spans`, over the live view, E47); the TEXT
    # is harvested raw, because a delta main merely QUOTES in a fence is not one main holds and
    # reading it as held dropped the stream's refused escape at the merge (E38). A walk of its own
    # here was a second reader of which lines a delta holds.
    lines = body.splitlines(keepends=True)
    return ["".join(lines[i] for i in idx) for idx in delta_spans(lines).values()]


def _delta_insert_at(lines: list, i: int) -> int:
    """Where a new delta goes under the `## Deltas` heading at `lines[i]` — newest-first, but never
    BETWEEN a delta's head and its continuation lines.

    An unconditional `i + 2` spliced a new head into a wrapped delta, grafting one lesson's tail
    onto another: the escape folded and the innocent lesson refused R:UNPREVENTED (E22).
    """
    marks = list(_headings(lines))
    at = i + 1
    while at < len(marks):
        line, level, _ = marks[at]
        # A fenced example is neither a delta nor the next section — the scan walks past it and the
        # new line lands where every reader looks (E38). The next `## ` still ends the section.
        if level == 2 or (level == 0 and DELTA_LINE.match(str(line).strip())):
            return at
        at += 1
    return at


def _delta_identity(line: str) -> str:
    """The LESSON of a delta line — what two streams could disagree on the disposition of.

    Grammar `- [<COMP> · <status>] <learning> (evidence: <ptr>)`: identity is `<learning>`, so the
    same lesson filed `open` by one stream and `rejected` by another shares an identity and is a
    conflict, while two genuinely different lessons never collide.
    """
    s = line.strip()
    after = s.split("]", 1)[1] if "]" in s else s
    # The LAST marker, as every other reader of this line reads it (E10, E18): splitting at the
    # first one truncated two different lessons to one identity, and the merge dropped both (E40).
    return after.rsplit("(evidence:", 1)[0].strip() if "(evidence:" in after else after.strip()


# ONE address, read the way `resolve` reads it — whitespace on either side of the `#` and all.
# A third reader with a stricter pattern let a re-mint skip every spelling E26 blesses, and the
# escape its stream refused folded in main (twentieth T2 refute, E34). A hit is re-emitted
# canonical, so the merged line carries the address every reader agrees on.
DELTA_ADDR = re.compile(r"/specs/([^/#\s]+)\.md\s*#\s*([A-Za-z0-9:_]+)")


def _merge_deltas(root: Path, per_spec: dict) -> set:
    """Union each stream's delta lines into main's specs. Returns the spec filenames it changed.

    `join` is the SECOND writer of delta lines, and the one that can mint a duplicate address.
    Streams branch from one base, so two of them mint the same next id for two different lessons;
    this union carries both while writing back MAIN's frontmatter, discarding the streams' counters.
    An incoming line whose id is already taken here is re-minted above the high-water. A line
    already in place never moves — ids retire in place, and a renumber would silently re-point
    every relation aimed at them (R:RENUMBER).

    Two passes, because a re-mint moves an address that lines in OTHER specs may name: mint every
    spec first, collecting one remap PER STREAM, then re-point that stream's own lines with its own
    remap. Scoping the remap to the spec being written left a cross-lens prevention naming the id
    it used to have; applying it to every fresh line re-pointed a second stream's tail whose own id
    never moved (nineteenth T2 refute, E33).
    """
    minted, remaps, touched = {}, {}, set()
    for name, entries in per_spec.items():
        path = root / "specs" / name
        node = read(path, "T2")
        lines = node["body"].splitlines(keepends=True)
        present = set(_delta_lines(node["body"]))
        seen, fresh = set(), []
        for ix, line in entries:                       # dedupe incoming, drop what main already holds
            if line not in present and line not in seen:
                seen.add(line)
                fresh.append((ix, line))
        if not fresh:
            continue
        taken = set(_delta_ids_in(lines))
        seq = _delta_high_water(node["raw"], lines)
        letter, out = _delta_letter(path.stem), []
        for ix, line in fresh:
            m = DELTA_LINE.match(line.strip())
            did = parse_delta_head(m.group(1))["id"] if m else None
            if did and did in taken:
                seq += 1
                fresh_id = f"{letter}{seq}"
                line = line.replace(f"· {did} ·", f"· {fresh_id} ·", 1)
                remaps.setdefault(ix, {})[f"/specs/{path.stem}.md#{did}"] = f"/specs/{path.stem}.md#{fresh_id}"
                did = fresh_id
            if did:
                taken.add(did)
                tail = re.search(r"(\d+)\Z", did)
                if tail:
                    seq = max(seq, int(tail.group(1)))
            out.append((ix, line))
        minted[name] = (out, seq)

    for name, (entries, seq) in minted.items():
        path = root / "specs" / name
        node = read(path, "T2")
        lines = node["body"].splitlines(keepends=True)
        # Substituted in ONE pass over the whole address, so a chain of re-mints cannot re-point a
        # line twice and a stream only ever follows its OWN moves.
        fresh = [DELTA_ADDR.sub(
            lambda m, r=remaps.get(ix, {}): r.get(f"/specs/{m.group(1)}.md#{m.group(2)}", m.group(0)), line)
            for ix, line in entries]
        i = heading_index(lines, "deltas")
        if i >= 0:
            at = _delta_insert_at(lines, i)
            lines[at:at] = fresh
        else:
            lines += ["\n## Deltas\n\n"] + fresh
        merged = "".join(lines)
        # Every other delta writer recomputes the counter from the body it wrote; the merge did
        # not, so `status` reported one open delta where `deltas` listed two (E41).
        raw = set_key(set_key(node["raw"], "delta_seq", str(seq)), "open_deltas", str(open_delta_count(merged)))
        write(path, f"---\n{raw}\n---\n{merged}")
        touched.add(name)
    return touched


def _admits(fm: dict) -> bool:
    """Does this stream node contribute to a join? Gated, and not HARD-STOP.

    ONE reader: the pre-flight asked only whether a node was GATED while the merge asks this, and
    they disagreed on exactly one input — a HARD-STOPped stream, the security case, refused a whole
    wave's join over a spec it would never touch (thirty-first T2 refute, E45).
    """
    gated = any(isinstance(st, dict) and st.get("act") == "gate" for st in ((fm or {}).get("verified") or []))
    return gated and _last_gate_outcome(fm or {}) != "HARD-STOP"


def join(root, stream_dirs) -> tuple:
    """Fold N worktree stream bundles back into the main bundle (M1–M4).

    The engine stays NO-EXEC — the skill created the worktrees and spawned the builders; this only
    reconciles their bundles. wave() guaranteed disjoint scope, so streams touched different task
    nodes and the build never raced. Here at the join: node files copy byte-for-byte (disjoint),
    spec deltas union-merge (append-only), graph.json regenerates (rebuildable cache). A HARD-STOP
    stream is never admitted (R:MERGEHARDSTOP); a PASS stream is never dropped (R:DROPPASS).
    """
    root = Path(root)
    # Read every stream path BEFORE merging any of them. `(d / "tasks").glob("*.md")` on a
    # directory that does not exist yields nothing, quietly — so an unread path was
    # indistinguishable from a wave that legitimately merged nothing, and `add join /typo`
    # exited 0 saying "joined 0 stream(s)". Same class as the receipt `run` used to fabricate
    # for a typo'd slug: success reported over input the verb never found.
    #
    # All-or-nothing, and checked first: a partial merge leaves the bundle holding some of a
    # wave's nodes with nothing on record saying which -> "R:PHANTOMSTREAM".
    for d in stream_dirs:
        if not _is_bundle_index(Path(d) / "index.md"):
            return None, (f"unreadable stream: {d} — a stream bundle declares `abf_version:` in "
                          f'its index, and this path does not -> "R:PHANTOMSTREAM"'
                          f"\nnext: check the path, then add join <stream>/.add")

    # A writer must be able to LAND before anything is copied: main's spec must be readable, or a
    # carried lesson lands where no reader looks and the join reports success (E43). Checked here,
    # with the other all-or-nothing checks, because a refusal after the copy is the partial merge.
    for d in stream_dirs:
        # …only for a stream that can CONTRIBUTE: one with no ADMITTED node writes nothing, and
        # refusing over a spec the join would never touch is a refusal nobody can act on (E44).
        # The same predicate the merge applies — asking "is it gated" while the merge asks "gated
        # and not HARD-STOP" made one rejected stream, the security case, block a whole wave (E45).
        if not any(_admits(read(tp, "T2")["fm"] or {})
                   for tp in sorted((Path(d) / "tasks").glob("*.md"))):
            continue
        for sp in sorted((Path(d) / "specs").glob("*.md")):
            # The STREAM's spec first: that is where the escape lives, and a fence there makes
            # `_delta_lines` yield [] — indistinguishable from a stream that filed nothing, so the
            # merge reported success and the refused escape was gone (thirty-first refute, E45).
            for side, node in (("the stream's ", read(sp, "T2")),
                               ("", read(root / "specs" / sp.name, "T2")
                                if (root / "specs" / sp.name).is_file() else None)):
                if node is None or (side == "" and not _delta_lines(read(sp, "T2")["body"])):
                    continue
                why = unreadable_spec(node)
                if why:
                    return None, (f"cannot join — {side}specs/{sp.name} would not be readable at the line: "
                                  f'{why}, so a carried lesson would be lost -> "R:UNREADABLE"'
                                  f"\nnext: add doctor   (it names the file), then add join {d}")
                # `_delta_lines` rebuilds only the lines `delta_spans` HOLDS, so a severed tail is
                # dropped at the merge and main folds a laundered, marker-less delta at exit 0 —
                # the escape its own stream refused (thirty-fourth T2 refute, E48). The merge asks
                # what `fold` asks, on both sides, before it copies anything.
                stray = orphan_tail(node["body"])
                if stray:
                    return None, (f"cannot join — {side}specs/{sp.name} carries `{stray[:60]}`, an escape's "
                                  f'tail that belongs to no delta, and the merge would drop it -> "R:UNPREVENTED"'
                                  f"\nnext: join the tail back onto its delta with a space or a tab, "
                                  f"then add join {d}")

    merged, skipped, specs_touched, conflicts = [], [], set(), []
    incoming = {}  # spec filename -> delta lines contributed by admitted streams (gathered, then partitioned)

    for stream_ix, d in enumerate(stream_dirs):
        d = Path(d)
        admitted = False
        for tp in sorted((d / "tasks").glob("*.md")):
            slug = tp.name[:-3]
            node = read(tp, "T2")
            fm = node["fm"] or {}
            gated = any(isinstance(s, dict) and s.get("act") == "gate"
                        for s in (fm.get("verified") or []))
            if not gated:
                continue  # this stream did not work this node — a stale sibling copy, never a contribution
            outcome = _last_gate_outcome(fm)
            if outcome == "HARD-STOP":
                skipped.append({"slug": slug, "reason": "HARD-STOP"})
                continue  # R:MERGEHARDSTOP — a rejected stream's node never enters main
            # PASS / RISK-ACCEPTED: copy the node + its receipts byte-for-byte (lossless, no shutil).
            # `add init` writes no `tasks/`, so a first join raised FileNotFoundError with no `R:`
            # code — every exit is a refusal or a record (E24), and this one is a record (E39).
            (root / "tasks").mkdir(parents=True, exist_ok=True)
            (root / "tasks" / tp.name).write_bytes(tp.read_bytes())
            # Provenance: a stream built under a lens (`persona:`, stamped by wave) records
            # `advised_by:` on the DELIVERED node — audit-grade, derived from the stream, never
            # fabricated. An unlensed node is left exactly as copied (no `advised_by:`).
            if fm.get("persona"):
                mnode = read(root / "tasks" / tp.name, "T2")
                write(root / "tasks" / tp.name,
                      f"---\n{set_key(mnode['raw'], 'advised_by', fm['persona'])}\n---\n{mnode['body']}")
            sd = d / "tasks" / f"{slug}.d"
            if sd.is_dir():
                for src in sorted(p for p in sd.rglob("*") if p.is_file()):
                    dst = root / "tasks" / f"{slug}.d" / src.relative_to(sd)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(src.read_bytes())
            merged.append(slug)
            admitted = True
        if admitted:  # only an admitted stream's lessons fold in (a HARD-STOP/dropped stream's do not)
            for sp in sorted((d / "specs").glob("*.md")):
                if (root / "specs" / sp.name).is_file():
                    incoming.setdefault(sp.name, []).extend(
                        (stream_ix, ln) for ln in _delta_lines(read(sp, "T2")["body"]))

    # Partition the gathered deltas per spec: a lesson filed with two different dispositions across
    # streams is a CONFLICT (flag it, insert neither variant); everything else unions as before.
    clean_per_spec = {}
    for name, entries in incoming.items():
        groups = {}
        for ix, ln in entries:
            groups.setdefault(_delta_identity(ln), []).append((ix, ln))
        clean = []
        for ident, variants in groups.items():
            distinct = list(dict.fromkeys(ln for _, ln in variants))
            if len(distinct) > 1:
                conflicts.append({"spec": name, "identity": ident, "variants": distinct})
            else:
                clean.append(variants[0])
        clean_per_spec[name] = clean
    specs_touched |= _merge_deltas(root, clean_per_spec)

    load(root)  # M4: regenerate graph.json from the merged files — never copied from a stream
    result = {"merged": merged, "skipped": skipped, "specs": sorted(specs_touched), "conflicts": conflicts}
    note = [f"joined {len(merged)} stream(s): {' · '.join(merged) or '—'}"]
    if skipped:
        note.append("skipped (not merged): " + " · ".join(f"{s['slug']} ({s['reason']})" for s in skipped))
    if specs_touched:
        note.append("specs union-merged: " + ", ".join(sorted(specs_touched)))
    if conflicts:
        note.append("CONFLICTS — a human must reconcile (not auto-merged): "
                    + " · ".join(f"{c['spec']}:{c['identity']}" for c in conflicts))
    note.append("next: add status")
    return result, "\n".join(note)


def load(root, cache: bool = True) -> dict:
    """The graph, always from the files.

    `graph.json` is an **export**, not an optimisation: FORMAT §4 lets a consumer read the
    graph at T0 without this engine. It is written, never read back, which is what makes
    R:CACHEAUTH structurally impossible rather than merely tested — a cache that is never
    consulted cannot outrank the files.
    """
    graph = scan(root)
    if cache:
        try:
            payload = {
                "nodes": {c: (n["fm"] or {}) for c, n in graph.items()},
                "edges": [[s, k, r, t] for s, k, r, t in edges(graph)],
            }
            write(Path(root) / CACHE_NAME, json.dumps(payload, indent=1, sort_keys=True) + "\n")
        except OSError:
            pass  # a read-only bundle is legal; the export is a convenience, never a dependency
    return graph


# ======================================================================= init (e3)
#
# A profile selects which SPEC LENSES a bundle gets — never which rules apply. It is a
# dict, so adding one is data, not an engine branch (goal 2's closed-lens claim, tested by
# adding a profile at runtime). `code` and `doc` are what ships, and this dict is the whole set.
# An earlier note here pointed at further profiles arriving as template files; none was ever built,
# so it sent every reader of this file looking for something that did not exist. `init` now
# REFUSES a name that is not a key here, rather than quietly resolving it to `code`.

PROFILES = {
    "code": {
        "domain": "what the product must be true about",
        "system": "how it is built, and what that forecloses",
        "experience": "who uses it and what they feel",
        "quality": "what counts as proof",
        "method": "how work proceeds, and what a gate costs",
    },
    "doc": {
        "domain": "what the document must get right",
        "experience": "who reads it and what they need",
        "quality": "what counts as proof, when there is no test runner",
        "method": "how drafts proceed to a gate",
    },
}


# The engine version — one source of truth. `_stamp`, `init`'s `engine:`/`tooling_engine:` stamps,
# and the drift-warn all read this, so a version bump is a single edit (M4).
ENGINE = "add/3.6.0"
# Where `init` vendors from: the engine lives beside this file; the seed corpus sits at the bundle
# root as its own managed tree (`.add/personas-teacher/` installed; `add-method/personas-teacher/`
# in the package). `parents[1]` resolves both. Module-level so a test can repoint them to simulate a
# missing source (R:MISSINGSRC).
TOOLING_SRC = Path(__file__).resolve().parent
CORPUS_SRC = Path(__file__).resolve().parents[1] / "personas-teacher"
# The routing index is a SIBLING TREE of the corpus, never a file inside it: `personas-teacher/`
# is a byte-verbatim third-party snapshot that `scripts/update_teacher.py` replaces wholesale, so
# anything written in there is erased on the next refresh. A tree (not a loose file) because the
# installer materializes payload directory-by-directory. Generated by build_persona_index.py.
INDEX_SRC = Path(__file__).resolve().parents[1] / "personas-index"
_ENGINE_FILES = ("add.py", "cli.py")


def _stamp(by: str = ENGINE) -> str:
    return f"generated: {{ by: {by}, at: {_today()} }}"


def _vendor_tooling(root, overwrite: bool = False) -> tuple:
    """Copy the engine + seed corpus into `<root>/tooling/`. Returns `(written, could_not)`.

    Shared by `init` (`overwrite=False` → idempotent, never clobbers a human edit, R:CLOBBER) and
    `doctor_sync` (`overwrite=True` → refresh a stale vendored engine). A missing source degrades to
    an entry in `could_not`, never an exception (R:MISSINGSRC).
    """
    root = Path(root)
    written, could_not = [], []

    def copy(rel: str, src: Path):
        try:
            data = src.read_text(encoding="utf-8")
        except OSError:
            could_not.append(rel)
            return
        dst = root / rel
        if dst.is_file() and not overwrite:
            return  # idempotent: a human's vendored edit outranks a re-copy unless asked to overwrite
        dst.parent.mkdir(parents=True, exist_ok=True)
        write(dst, data)
        written.append("/" + rel)

    for name in _ENGINE_FILES:
        copy(f"tooling/{name}", TOOLING_SRC / name)
    try:
        corpus = sorted(CORPUS_SRC.rglob("*.md"))   # the corpus is nested by division — recurse
    except OSError:
        corpus = []
    if not corpus:
        could_not.append("personas-teacher/*")
    for src in corpus:
        copy(f"personas-teacher/{src.relative_to(CORPUS_SRC).as_posix()}", src)
    # The corpus says what each lens IS; the index says when to reach for it. A bundle with the
    # first and not the second can read personas but cannot route to one.
    try:
        index = sorted(INDEX_SRC.glob("*.md"))
    except OSError:
        index = []
    for src in index:
        copy(f"personas-index/{src.name}", src)
    return written, could_not


def _today() -> str:
    import datetime
    return datetime.date.today().isoformat()


def ancestor_bundle(root):
    """The nearest bundle ABOVE `root`, or None. Read-only; never raises.

    An `index.md` DECLARING `abf_version:` is the marker `init` always writes and nothing else
    does (A2) — the bare filename is not enough, see `_is_bundle_index`. The walk starts at the
    candidate bundle's grandparent — `root` is `<project>/.add`, so `root.parent` is the
    project itself and is never its own ancestor — and stops at the filesystem root or at a
    directory it cannot read (A3, M5). It cannot follow a symlink out of the tree it started
    in because `resolve()` canonicalises first, so every `parents` entry is a real directory;
    that is the whole of M5's symlink clause, and there is no other ceiling — a bundle far
    above you IS an ancestor and is reported as one.

    Why this exists: `status` in a subdirectory used to print `next: add init`, and following
    the engine's own instruction created a second bundle beside the real one. A resume verb
    that tells a lost reader to build a rival to the thing they are lost inside is worse than
    one that says nothing (R:MISDIRECT).
    """
    try:
        start = Path(root).resolve()
    except (OSError, RuntimeError):
        return None
    here = start.parent          # the project dir
    for parent in here.parents:  # nearest first, terminating at the filesystem root
        try:
            candidate = parent / ".add" / "index.md"
            if _is_bundle_index(candidate):
                return parent / ".add"
            # A bundle root passed directly (not a `<project>/.add` shape) still counts.
            # INVARIANT both branches keep: the return is always a BUNDLE ROOT, whose `.parent`
            # is the project — here `parent` holds the marker itself, so `parent` IS the bundle
            # root. Both callers report `Path(above).parent`, and that only reads correctly
            # while this holds.
            if parent != start and _is_bundle_index(parent / "index.md"):
                return parent
        except OSError:
            return None          # unreadable parent — answer None, never raise (E3)
    return None


def _is_bundle_index(path) -> bool:
    """Is this `index.md` a BUNDLE index — not just a file that shares its name?

    The name alone is not the marker. `index.md` is the single most common filename in
    documentation tooling — MkDocs, Docusaurus and Hugo all put one at a section root — so
    keying on the name made every docs tree read as an ADD bundle: `init` refused a legitimate
    project with `R:RIVALBUNDLE` and `status` told the reader they were inside an ADD project
    that does not exist. `abf_version:` is written by `init` into every bundle index and by
    nothing else, so it separates the two at the cost of one small read. Head-only: a bundle
    index declares it in frontmatter, and a huge unrelated file is never fully loaded.
    """
    try:
        if not Path(path).is_file():
            return False
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return "abf_version:" in fh.read(400)
    except OSError:
        return False


def init(root, profile: str = "code", title: str = None, nested: bool = False,
         goal: str = None) -> tuple:
    """Create a conforming bundle. Never overwrites; an existing file is left alone.

    Returns `(graph, created_cids, note)`, or `(None, [], refusal)` when the profile is one this
    engine cannot honour. The note ends in a `next:` line, because a verb that does not say what
    comes next teaches nothing (law 4).
    """
    root, created = Path(root), []
    # Validated BEFORE anything touches the filesystem (M2, A3): an argument the engine cannot
    # honour is wrong independently of what is already on disk, and a refusal that half-created a
    # bundle would be worse than the fallback it replaces.
    #
    # This used to read `PROFILES.get(profile) or PROFILES["code"]`, so `--profile finance` wrote
    # the CODE lenses under a name the engine never understood. The reader learns their domain was
    # never modelled at the first spec they open — after they have written into it. Refusing costs
    # them one command; the silent fallback cost them the bundle (R:SILENTFALLBACK).
    if profile is not None and profile not in PROFILES:
        return None, [], (
            f'`{profile}` is not a profile this engine ships — it would have written the `code` '
            f'lenses under a name nothing understands. Available: {" · ".join(sorted(PROFILES))} '
            f'-> "R:BADPROFILE"\n'
            f'next: add init --profile {sorted(PROFILES)[0]} "<name>" '
            f'(a profile selects spec LENSES, never what a gate demands)')
    # Also BEFORE anything touches the filesystem, and for the same reason: creating a bundle
    # nested under another is wrong independently of what is already here. Two bundles in one
    # repo destroy the "state on disk is the source of truth" claim the method leads with, and
    # the engine used to be what instructed the user to build the second one (R:RIVALBUNDLE).
    # `--nested` is the whole distinction between a monorepo maintainer and a lost newcomer:
    # the engine cannot tell them apart, so the flag is what tells it (A1).
    above = None if nested else ancestor_bundle(root)
    if above is not None:
        return None, [], (
            f'an ADD bundle already exists above this directory, at `{Path(above).parent}` — '
            f'creating one here would leave two bundles in one project, and orientation would '
            f'read whichever you happened to be standing in -> "R:RIVALBUNDLE"\n'
            f'next: cd {Path(above).parent} && add status  '
            f'(or `add init --nested` if a separate bundle here is deliberate)')
    lenses = PROFILES[profile] if profile else PROFILES["code"]
    # The bundle root is `<project>/.add` in every real call (the CLI passes it), so naming the
    # project after the bundle DIRECTORY called every project `.add`. The project is the parent.
    resolved = root.resolve()
    title = title or (resolved.parent.name if resolved.name == ".add" else resolved.name)

    def put(rel: str, text: str):
        path = root / rel
        if path.exists():
            return  # M2 — a human's file always outranks a template
        path.parent.mkdir(parents=True, exist_ok=True)
        write(path, text)
        created.append("/" + rel)

    # `okf_version` sits beside `abf_version` because the two format declarations are read
    # together, and it is written HERE and nowhere else: OKF v0.2 declares the version on the
    # bundle-root index only, so a Spec/Task/Persona carrying one would be N claims that can
    # disagree (R:OKFSPRAWL). Quoted, so a consumer reads the string "0.2" and never a float
    # that round-trips as 0.20. A bundle without it is PRE-OKF, never defective — no verb
    # refuses on its absence and `doctor` gains no finding code for it (law 3).
    put("index.md", f'---\nabf_version: "1.3"\nokf_version: "0.2"\nname: {title}\n'
                    f"profile: {profile}\nengine: {ENGINE}\ntooling_engine: {ENGINE}\ncreated: {_today()}\n"
                    f"sensitive_paths: []\n{_stamp()}\n---\n\n"
                    "<!-- COMPILED BODY (A11) — regenerated by the engine; do not hand-maintain. -->\n")
    put("log.md", "# log\n\n<!-- COMPILED BODY (A20) — rendered from node `verified[]` stamps.\n"
                  "     Humans write in `## Notes` only. -->\n\n## Notes\n")
    # A23 (FORMAT §1.1) — the compiled reserved files declare themselves to git so a merge
    # resolves without a hand-edit. `merge=ours` is a built-in driver (no install step), and
    # both files are views: whichever side survives is restored by `doctor --sync`.
    put(".gitattributes", "index.md merge=ours linguist-generated=true\n"
                          "log.md   merge=ours linguist-generated=true\n")
    # `invariants:` is the key every task is bound to by the method's own prose — and until
    # now it was written by nothing and read by nothing, so the binding named a slot that did
    # not exist. Seeded EMPTY (A2): the engine has nothing true to put there, and content it
    # invented would ship as constraints nobody chose. `doctor` is its reader (R:DEADKEY).
    put("PROJECT.md", f"---\ntype: Project\ntitle: {title}\n"
                      f"goal: {goal or '<one sentence — what is true when this ships>'}\n"
                      f"invariants: []\n"
                      f"stage: mvp\nprofile: {profile}\n{_stamp()}\n---\n"
                      f"## CARD\ngoal: <the one line a cold reader needs>\nstate: initialised\n"
                      f"next: add new milestone <slug>\n")
    for slug, goal in lenses.items():
        put(f"specs/{slug}.md",
            # OKF v0.2's recommended `description:`/`tags:` plus the provenance family
            # `sources:`. `description` is seeded from the SAME `goal` that opens `## Now`, so
            # the two are identical at birth — but they are not two homes for one sentence:
            # `description` is what the LENS IS FOR (stable, machine-read — `_render_index`
            # renders the catalogue row from it), while `## Now` is what is CURRENTLY TRUE in
            # this project's lens and SHOULD drift as the project moves. `tags`/`sources` are
            # slots a human fills, read by nothing in this engine and validated by nothing
            # (NO-EXEC); they scaffold as real empty lists, never placeholder strings, so the
            # first consumer reads `[]` and not a one-item list of angle-bracket text.
            # OKF's doc-status `status:` and `stale_after:` stay OUT: `status:` is ADD's
            # task-lifecycle key, and a spec whose every delta carries a validity interval has
            # no file-level staleness left to declare.
            #
            # `open_deltas: 0` is seeded HERE, not left for the first `learn`. Absence has to
            # mean one thing only — "this bundle predates the counter" — or every fresh bundle
            # would report UNKNOWN until it happened to learn something, and the signal that is
            # supposed to distinguish an unmigrated bundle from a drained one would say the
            # same word for both.
            f"---\ntype: Spec\ntitle: {slug.title()}\nlens: {slug}\nproject: {title}\n"
            f"description: {goal}\ntags: []\nsources: []\nopen_deltas: 0\n{_stamp()}\n---\n"
            f"## Now\n{goal}\n\n## Decisions that bind\n- <the first decision that constrains the rest>\n\n"
            f"## Deltas\n- <what changed, and the evidence that changed it>\n")

    # Seed the starting roster. Until 3.4 `init` seeded NO personas, so `.add/personas/` was
    # empty on every fresh bundle and the roster's selector — which searches `flow:` then
    # `task-kinds:` — had nothing to search. The teacher corpus could not rescue it: not one
    # of its 232 files carries either key. So "personas carry the expertise" was false by
    # default, and the failure was silent: the agent took the generic fallback and reported
    # success, with nothing in the receipt recording that no expert was ever loaded
    # (R:DEADTIER). These four templates already carried the right keys and were seeded by
    # nothing, while the changelog said they were.
    #
    # They are the PROJECT's from the moment they land (A1): `put` never overwrites, so an
    # edited persona survives every re-init, and deleting one is a legitimate choice.
    seeded = []
    tmpl_dir = Path(__file__).resolve().parent / "templates" / "personas"
    if tmpl_dir.is_dir():
        for tmpl in sorted(tmpl_dir.glob("*.md.tmpl")):
            slug = tmpl.name[: -len(".md.tmpl")]
            body = tmpl.read_text(encoding="utf-8")
            # The templates carry a roster `name:`; a bundle node needs `type: Persona` and a
            # `title:` for the graph to see it at all (R:BADPERSONA reads the TYPE, not the name).
            if body.startswith("---"):
                fm, _, rest = body[3:].partition("---")
                # NOT `title` — that is `init`'s own parameter, and shadowing it here left a
                # trap for whoever next reads the project title after this block.
                lens_title = next((l.split(":", 1)[1].strip() for l in fm.splitlines()
                                   if l.startswith("name:")), slug)
                body = (f"---\ntype: Persona\ntitle: {lens_title}\n"
                        f"{fm.strip()}\n{_stamp()}\n---{rest}")
            before = len(created)
            put(f"personas/{slug}.md", body)
            if len(created) > before:
                seeded.append(slug)

    # Vendor the engine + seed corpus so the bundle runs standalone (the skill's `add` = the vendored
    # `tooling/cli.py` for a project that never had this repo). overwrite=False keeps init idempotent —
    # a re-run never clobbers a human's vendored edit (R:CLOBBER); `doctor --sync` is the refresh path.
    written, could_not = _vendor_tooling(root, overwrite=False)
    created += written

    note = (f"created {len(created)} files ({profile} profile)" if created
            else "bundle already exists — nothing written")
    # Name the roster: a seed nobody is told about is a seed nobody edits (A9).
    if seeded:
        note += (f"\n  seeded {len(seeded)} starting personas ({' · '.join(seeded)}) — they are "
                 f"yours to edit; `init` never overwrites them")
    # Say it plainly: a nested bundle is legal and deliberate, and the reader must know that
    # two bundles now exist so `status` from the wrong directory never surprises them (M4).
    if nested and created and ancestor_bundle(root) is not None:
        note += ("\n  two bundles now exist in this project — `status` reports the one you "
                 "are standing in")
    if could_not:
        note += f"\n  could not vendor (missing source): {', '.join(could_not)}"
    return load(root), created, f"{note}\nnext: add new milestone <slug>"


RE_2X_PHASE = re.compile(r"^phase:\s*(\w+)", re.M)


def upgrade(project_root, by: str = "cli") -> tuple:
    """The guided 2.x → 3.0 clean break (W5). `(report_path, note)` — NO-EXEC, nothing deleted.

    Automates exactly the path proven by hand on the bench, and nothing more: the whole 2.x
    bundle is RENAMED to `.add-2x-archive/` (byte-identical, grep-able, never edited), a fresh
    3.0 bundle is initialised at `.add/`, and `MIGRATION.md` lands in the ARCHIVE — it describes
    the old world, and the new bundle's doctor should not have to classify it. State is not
    translated: 2.x stamps, waivers and phase markers mean things 3.0 deliberately refuses to
    mean (an untranslatable `phase: verify` re-materialising as a 3.0 beat would be a bypass
    with a heritage story), so tasks are re-authored, with the archive open beside the editor.

    A 2.x bundle is recognised by its own bones, any of: the `tooling/add_engine/` package
    (3.0's engine is two flat files), `state.json` (3.0 has no state file), or directory-tasks
    (`tasks/<slug>/PLAN.md`; 3.0 tasks are flat nodes).
    """
    project_root = Path(project_root)
    root = project_root / ".add"
    archive = project_root / ".add-2x-archive"

    def refuse(why: str, fix: str) -> tuple:
        return None, f"cannot upgrade — {why}\nnext: {fix}"

    if not root.is_dir():
        return refuse("no `.add/` bundle here", "add init  # start fresh at 3.0")
    if not ((root / "tooling" / "add_engine").is_dir()
            or (root / "state.json").is_file()
            or any(root.glob("tasks/*/PLAN.md"))):
        return refuse("this bundle is already 3.0 — no 2.x markers found "
                      "(add_engine/ package, state.json, or tasks/<slug>/PLAN.md)",
                      "add status")
    if archive.exists():
        return refuse(f"`{archive.name}/` already exists — a previous upgrade's record is "
                      f"never clobbered",
                      f"move `{archive.name}/` aside yourself, then add upgrade")

    tasks = []
    for plan in sorted(root.glob("tasks/*/PLAN.md")):
        m = RE_2X_PHASE.search(plan.read_text(encoding="utf-8", errors="replace"))
        tasks.append((plan.parent.name, m.group(1) if m else "unknown"))
    title = goal = None       # a bundle with no charter at all reaches init with both unset
    charter = root / "PROJECT.md"
    if charter.is_file():
        text = charter.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^title:\s*(.+)$", text, re.M) \
            or re.search(r"^#\s+(?:PROJECT:\s*)?(.+)$", text, re.M)
        title = m.group(1).strip() if m else None
        # R:CLOBBERGOAL. The 2.x charter carried an authored goal; carrying only `title:`
        # replaced a year of direction with a placeholder and nothing refused it, because no
        # guard reached the root. Matched the same loose way `title:` is, and an ABSENT goal
        # stays absent (E5) — the fresh bundle gets the ordinary placeholder, never a fiction.
        g = re.search(r"^goal:\s*(.+)$", text, re.M)
        goal = g.group(1).strip() if g and not PLACEHOLDER.search(g.group(1)) else None

    root.rename(archive)                      # the ONE move — everything else is additive
    # The engine executing THIS verb lived inside the bundle just archived — its own source
    # paths (TOOLING_SRC/CORPUS_SRC point into the renamed tree) are now gone, so init's
    # vendoring degrades to `could_not` and the fresh bundle would have starter files and NO
    # engine: the report's own `next: add status` dies on a missing cli.py (R:SELFARCHIVE —
    # found live in the v3.0.0 updater test). Restore the installer-managed trees by COPY
    # BEFORE init — never move (the archive stays the complete, byte-identical 2.x record),
    # and init's idempotence then treats the restored files as the human's, exactly right:
    # the archived tooling is by construction the running 3.0 engine, since a 3.0 cli
    # dispatched this verb.
    import shutil
    for tree in ("tooling", "personas-teacher", "personas-index"):
        src = archive / tree
        if src.is_dir() and not (root / tree).exists():
            shutil.copytree(src, root / tree, ignore=shutil.ignore_patterns("__pycache__"))
    init(root, "code", title, goal=goal)

    report = archive / "MIGRATION.md"
    lines = [f"# 2.x → 3.0 migration — recorded {_today()} by {by}", "",
             "Nothing was deleted. This directory is the complete 2.x bundle, byte-identical,",
             "renamed from `.add/`. The fresh 3.0 bundle beside it starts empty on purpose:",
             "2.x state is not translated, because its markers (phase, autonomy, waivers) mean",
             "things 3.0 deliberately refuses to mean. Re-author each task below against its",
             "archived PLAN.md — the direction work transfers; the bypasses do not.", "",
             "## 2.x tasks to re-author", ""]
    lines += [f"- `{slug}` (2.x phase: {phase}) — archived at `tasks/{slug}/PLAN.md`; "
              f"re-author with `add new Task {slug}`" for slug, phase in tasks] \
        or ["- (none found)"]
    lines += ["", "## Next", "",
              "1. `add status` — see the fresh bundle.",
              "2. `add new milestone <slug>` — recreate the active milestone.",
              "3. `add new Task <slug>` per task above, authoring RULES/ASSUMPTIONS/CHECKS",
              "   from the archived PLAN.md's §1–§4.",
              "4. Freeze, brief, build, gate — the 3.0 loop takes it from there."]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    note = (f"2.x bundle archived whole to `{archive.name}/` ({len(tasks)} task(s) recorded in "
            f"MIGRATION.md) · fresh 3.0 bundle initialised at `.add/`"
            f"\nnext: read {archive.name}/MIGRATION.md, then add status")
    return report, note


# ============================================== new · freeze · done — transitions (e4)
#
# One shared write path (`_transition`) serves all three verbs, per amendment A1. Two rules
# decide the shape:
#
# * **A notary refuses to forge, never to record.** `done` will not CREATE a `status: done`
#   that no gate stamp entitles — signing an unsigned document is not notarising it. But it
#   never prevents a human from writing their own stamp with their own authority. That is
#   the line between law 3's notary and the guard it forbids.
# * **Authority is computed, never passed.** A caller cannot argue its way below the floor,
#   because the floor is derived from the node and the index, not from an argument.

AUTHORITY_ORDER = ("process", "ai-verify", "plan", "human")


def claimed_authority(claim, floor: str, verb: str, slug: str):
    """`(authority, refusal)` — a claim may rise above the computed floor, never sink below it.

    `--authority` was declared on `gate`, passed into `gate()`, and then overwritten by the
    computed floor before any read: the flag has never done anything, while GETTING-STARTED
    teaches it on `freeze` for a reason a reader carries straight to the gate — "a ledger of
    process stamps cannot be told apart from an agent approving its own work". `freeze` has the
    opposite bug: it honours ANY value, so `--authority process` silently downgrades a security
    freeze. One reader fixes both. Claiming MORE than the floor is a stronger statement about
    who acted and is recorded as given; claiming LESS is the downgrade the floor exists to
    prevent, and is refused rather than quietly ignored -> "R:FLOORDIVE".
    """
    if claim in (None, ""):
        return floor, None
    claim = str(claim)
    if claim not in AUTHORITY_ORDER:
        return None, (f"unreadable authority {claim!r} — a stamp records who acted, and an "
                      f'unreadable claim is not the lowest one -> "R:FLOORDIVE"'
                      f"\nnext: add {verb} {slug} --authority <{' | '.join(AUTHORITY_ORDER)}>")
    if AUTHORITY_ORDER.index(claim) < AUTHORITY_ORDER.index(floor):
        return None, (f"`--authority {claim}` is below this node's computed floor `{floor}` — a "
                      f"claim may rise above the floor, never sink below it -> \"R:FLOORDIVE\""
                      f"\nnext: add {verb} {slug} --authority {floor}")
    return claim, None
SENSITIVITY_FLOOR = {
    "mechanical": "process",
    "data": "plan",
    "architecture": "plan",
    "security": "human",
}


def sensitivity_floor(value) -> str:
    """The authority floor a `sensitivity:` declares — `human` when it declares something unreadable.

    `SENSITIVITY_FLOOR.get(value, "process")` sent every unrecognised value to the LOWEST floor,
    silently. `high` and `critical` both read `process`, and two real nodes on the affordance-truth
    branch declared `high` and floored to `process` where they meant `plan` (2026-09-01). An
    unreadable declaration is a declaration the engine cannot honour, so it floors UP -> "R:SILENT_FLOOR".
    An ABSENT value is a different fact and keeps the `process` default: declaring nothing is not
    declaring something illegible.
    """
    if value in (None, ""):
        return "process"
    return SENSITIVITY_FLOOR.get(str(value), "human")
TYPE_DIR = {"Task": "tasks", "Milestone": "milestones", "Spec": "specs",
            "Persona": "personas", "Prompt": "prompts", "Run": "runs"}
BODIES = {
    "Task": "## CARD\ngoal: <one line>\nwhy: <why this task exists — optional>\n"
            "beat: scaffold · next: author {slug}'s RULES, ASSUMPTIONS and CHECKS, "
            "then add freeze {slug}\n\n"
            "## RULES\n<must>\n- M1 <the rule that must hold>\n</must>\n<reject>\n"
            "- R:<NAME> <what must never happen> -> \"<NAME>\"\n</reject>\n\n"
            # The line the author fills STARTS from "the request does not say" — the
            # not-said register is the frame, not a suggestion. The n=1 probe run showed
            # why: the sweep forced all four blind-spot questions and every answer came
            # back declarative ("GET /bookings lists every booking", "DELETE is permitted
            # for any caller") — a decision wearing a stated requirement's voice, which is
            # exactly the indistinguishability this section exists to end. With the frame
            # scaffolded, asserting requires DELETING it; before, flagging required
            # composing it. given -> decided -> priced, three slots apart.
            "## ASSUMPTIONS\n"
            "- A1 [who] covers: <S ids> · the request does not say <who may act / whose"
            " data>; taking <reading> -> <cost if wrong>\n"
            "- A2 [which] covers: <S ids> · the request does not say <which rows/cases"
            " are in>; taking <reading> -> <cost if wrong>\n"
            "- A3 [when] covers: <S ids> · the request does not say <where the boundary"
            " falls>; taking <reading> -> <cost if wrong>\n"
            "- A4 [absent] covers: <S ids> · the request does not say <what a missing"
            " value means>; taking <reading> -> <cost if wrong>\n"
            "- A5 [order] covers: <S ids> · the request does not say <what orders /"
            " breaks a tie>; taking <reading> -> <cost if wrong>\n"
            # BOTH halves, deliberately. Either alone is answerable without doing the work:
            # "the controller" names a recipient and stops, "it should be readable" names a
            # quality and nobody. Together they make a claim someone can be wrong about,
            # which is the register this whole section runs in.
            "- A6 [experience] covers: <S ids> · the request does not say <who receives"
            " this and what would make it hard for them>; taking <reading> -> <cost if"
            " wrong>\n"
            "every `gives:` surface is swept on every dimension; "
            "`[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. "
            "`· probe: <what shipped behavior must show>` declares a reading checkable: "
            "cite its A id from CHECKS and the gate holds the PASS to it.\n\n"
            "## PLAN\ncontract: <the shape this publishes>\n"
            "regression: <full | affected · <cmd> · <why> — or none · <why>>\n"
            "- O<n> covers: <M ids> · signal <metric> · window <w> · threshold <t> · action <alert|rollback>\n\n"
            "## EDGES\n- E1 <a boundary or failure case a check must cover — optional>\n\n"
            "## CHECKS\n- <test_name> · covers: M1 · <what it proves>\nred-first: every check MUST fail first.\n\n"
            "## EVIDENCE\nreceipt: <runs/<n>.md>\ngate: <PASS | RISK-ACCEPTED | HARD-STOP>\n\n"
            "## LESSONS\n- <lesson> -> add learn <lens>\n",
    "Milestone": "## CARD\ngoal: <one line>\nwhy: <why this milestone exists — required>\n"
                 "next: add new task <slug>\n\n## SCOPE\nIn:  <what>\nOut: <what not>\n\n"
                 "## GROUND\ntouches: <paths>\nrisks:\n  - <the one that would hurt>\n\n"
                 "## EXIT\n- [ ] <criterion>   (← <task>)\n\n## CLOSE\nevidence: <one row per task>\n",
    # A Persona is a living document (personas.md), never a task — no lifecycle, no freeze/gate.
    # The scaffold is the four machine-readable parts, distilled from a teacher entry (§Seed).
    "Persona": "## Identity\n<the stance, with earned perspective — scars, not a résumé>\n\n"
               "## Critical Rules\n- **<the non-negotiable clause>** — <the why>\n"
               "- **surface the tradeoff** — name the choice and its cost; never silently pick\n"
               "- **qualification gate** — name the simplest baseline that meets the contract; if it wins, stop\n\n"
               "## Default Requirement\n<the one requirement in every deliverable by default>\n\n"
               "## Success Metrics\n- <a measurable invariant> — guards against <the failure it prevents>\n",
}

# The types with a task lifecycle (direction → … → done, or active → done). Every other type —
# Persona, Prompt, Run, Spec — is a record or a living doc: it carries no task `status` and never freezes.
LIFECYCLE_TYPES = ("Task", "Milestone")


def _scope_list(fm) -> list:
    """`scope:` as a list of entries, whatever shape the frontmatter carries.

    A single-entry `scope: src/ui.py` parses as a STRING, and every reader iterated it — so the
    freshness set became one entry per CHARACTER, `/` resolved to the filesystem root, and the
    gate reported a stale file the node never declared (2026-08-28 review). One coercion, at
    every reader, rather than four hand-written isinstance checks.
    """
    scope = (fm or {}).get("scope") or []
    return [scope] if isinstance(scope, str) else list(scope)


def _paths_touch(scope_entry: str, pattern: str) -> bool:
    """True when a declared scope entry and a sensitive pattern can name the same file.

    Containment runs BOTH ways. Matching only `scope ⊆ pattern` made the floor monotonically
    wrong: `scope: src/` did not match `src/auth/*`, so declaring a BROADER, honest scope
    LOWERED authority below one that named the file exactly (2026-08-28 review).
    """
    import fnmatch
    scope_entry, pattern = scope_entry.strip().rstrip("/"), pattern.strip()
    if not scope_entry or not pattern:
        return False          # an empty side matching everything would fire A17 on every node
    if fnmatch.fnmatch(scope_entry, pattern):
        return True
    stem = pattern.replace("**", "").replace("*", "").rstrip("/")
    if not stem:
        return False
    # Whole SEGMENTS, not string prefixes. `srcfoo/secret.yaml`.startswith("src") is true and
    # means nothing, and the dangerous direction is the EXEMPTION clause of
    # R:UNDECLARED_SENSITIVE: read as a prefix, `scope: src` signed for a `srcfoo/` the node
    # never declared, and `secrets_public/` answered for `secrets/**` (2026-09-01 probe).
    return _under(scope_entry, stem) or _under(stem, scope_entry)


def _under(path: str, base: str) -> bool:
    """True when `path` IS `base` or lives beneath it, on `/` boundaries only."""
    return path == base or path.startswith(base + "/")


def _in_bundle_frame(parent, rels):
    """`rels` — repo-root-relative, the way every git command prints them whatever the cwd — as
    the BUNDLE's own entries are written, or None when git cannot say where the bundle sits.

    `scope:` and `sensitive_paths:` are written relative to the bundle PARENT. For any bundle
    below the repo root — this project's own `add-method/.add` is one — the two bases differ, so
    an unnormalised comparison silently matches nothing (the sensitive floor goes inert) or
    everything (a permanent refusal), depending on which side was prefixed. A path ABOVE the
    parent is DROPPED, not merely left unstripped: no entry of this bundle could ever name it.

    ONE reader, because the working-tree walker and the commit walker had this fact twice and it
    was wrong in both, differently: `--show-prefix` is read with `strip=False` and only git's own
    newline removed, since a directory is entitled to a LEADING space and the default strip ate
    it — ` nest/` came back as `nest/`, every path then failed `startswith` and was dropped, and
    the floor went entirely inert for that bundle.
    """
    prefix = _git(parent, "rev-parse", "--show-prefix", strip=False)
    if prefix is None:
        return None
    prefix = prefix.rstrip("\n")
    out = []
    for rel in rels:
        if prefix:
            if not rel.startswith(prefix):
                continue
            rel = rel[len(prefix):]
        if rel:
            out.append(rel)
    return out


def _changed_paths(root) -> list:
    """Repo-relative paths the working tree has touched vs HEAD, or `[]` when git cannot say.

    Uncommitted AND committed-since are both out of reach of a single porcelain call, so this
    reads the one thing that is always true at gate time: the diff against HEAD plus untracked
    files. `[]` on any failure — a non-repo bundle must stay gateable (law 3), so this can only
    ever ADD a refusal where git is present, never invent one where it is not.
    """
    out = _git(root, "status", "--porcelain", "-z", "--untracked-files=all", strip=False)
    if not out:
        return []
    recs, raw, i = out.split("\0"), [], 0
    while i < len(recs):
        rec, i = recs[i], i + 1
        if len(rec) < 4:
            continue
        xy, pending = rec[:2], [rec[3:]]
        # A rename or copy emits `XY <to>\0<from>\0` — the second field is a PATH carrying NO
        # status prefix. Read as a status record it lost three characters, so the guard refused
        # on a path that had never existed, and its own remedy (add it to `scope:`) produced an
        # entry resolving to nothing, which then trips the no-digest degrade.
        if ("R" in xy or "C" in xy) and i < len(recs) and recs[i]:
            pending.append(recs[i])
            i += 1
        raw.extend(pending)
    # `root` IS the bundle parent here — this walker's one caller passes `root.parent`.
    seen = []
    for rel in _in_bundle_frame(root, raw) or []:
        if rel not in seen:
            seen.append(rel)
    return seen


def _fs_epoch(near_path, fallback: float) -> float:
    """`fallback` (the wall clock) expressed the way the FILESYSTEM at `near_path` records time.

    A report written DURING the run read as stale on any filesystem whose mtime granularity is
    coarser than the clock — HFS+, ext3, exFAT, several network and bind mounts — because the
    truncated mtime precedes the wall-clock start. That costs more than an evidence rung:
    emptying the reported IDs leaves every `covers:` referent unbound, so `gate` refuses a node
    whose suite was green and correctly reported (2026-09-01 review).

    Flooring the clock to the second would fix that and blunt the check, letting a report
    forged moments before the command still pass. Taking the reference from a sentinel on the
    SAME filesystem does neither: whatever rounding that filesystem applies to the report was
    applied to this sentinel first, so discrimination stays as fine as the filesystem allows
    and no honest report is ever called stale.
    """
    probe = Path(near_path).parent / f".add-run-epoch-{os.getpid()}"
    try:
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_text("", encoding="utf-8")
        return probe.stat().st_mtime
    except OSError:
        return fallback          # an unwritable directory is not a reason to refuse (law 3)
    finally:
        try:
            probe.unlink()
        except OSError:
            pass


def _report_predates_run(path, started: float) -> bool:
    """True when `path`'s mtime proves it was written BEFORE the run began.

    `started` must be an `_fs_epoch`, not a raw clock reading — see that function for why.
    A missing report is treated as predating: no report is not evidence of THIS run either.
    """
    try:
        return Path(path).stat().st_mtime < started
    except OSError:
        return True


FENCE_MARKER = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$")


def _fence_step(line: str, active):
    """Advance one Markdown fence; an inner marker of another kind is content."""
    m = FENCE_MARKER.match(line)
    if m is None:
        return active, False
    marker, tail = m.groups()
    kind, width = marker[0], len(marker)
    if active is None:
        if kind == "`" and "`" in tail:
            return active, False  # a backtick opener cannot contain backticks in its info string
        return (kind, width), True
    if kind == active[0] and width >= active[1] and not tail.strip():
        closed = None
        return closed, True
    return active, False


def _fence_balanced(text: str) -> bool:
    """True when every real ``` / ~~~ fence in `text` is closed.

    `_box_lines` SKIPS fenced regions, so an unclosed fence silently swallows every box after
    it. For the goal-gate that turned real unchecked criteria into `total == 0` — the "no exit
    criteria" branch, which CLOSES the milestone (2026-09-01 review). A gate that cannot read
    its own input must refuse, never tally zero.
    """
    active = None
    for line in text.splitlines():
        active, _boundary = _fence_step(line, active)
    return active is None


def _oneline(note) -> str:
    """One line, no quote, no brace — safe inside a flow-map stamp.

    An unbalanced `{` in a `--reason` made the parser's list-continuation swallow the FOLLOWING
    stamp: two records written, one read back, from an append-only ledger whose ordering IS the
    trust model (2026-08-28 review). `replan` already normalised its note; `gate` did not.

    EVERY operator-supplied value interpolated into a flow map goes through here, not just
    `reason`. It was applied to that one field for a year while seven writers interpolated `by`
    raw, and an ODD number of `"` in a name then terminated the scalar early: `freeze --by
    'O"Brien'` PRINTED `freeze recorded` and wrote a record that read back carrying `by` alone,
    so `_is_frozen` was False and the seal silently did not exist (2026-09-01). A balanced pair
    round-trips, which is why it survived every real use -> "R:LIE".
    """
    return (" ".join(str(note).split())
            .replace('"', "'").replace("{", "(").replace("}", ")"))


def authority_for(graph: dict, cid: str) -> str:
    """The local floor plus every original obligation carried into this Task.

    A17 is a path match against `index.md`'s `sensitive_paths:`, so a notary may perform it:
    it is mechanical, and it outranks the declared `sensitivity:` in one direction only.
    """
    patterns = ((graph.get("/index.md", {}).get("fm") or {}).get("sensitive_paths")) or []
    def local(key):
        fm = ((graph.get(key) or {}).get("fm") or {})
        floor = sensitivity_floor(fm.get("sensitivity"))
        for entry in _scope_list(fm):
            for pattern in (patterns if isinstance(patterns, list) else [patterns]):
                if _paths_touch(str(entry), str(pattern)):
                    return "human"  # A17 — unstrikeable, and never lowered
        # A refreeze may correct a carry, but deleting its current list cannot erase the
        # authority that accepted it. Keep the strongest historical carried floor.
        for stamp in (fm.get("verified") or []):
            if isinstance(stamp, dict) and stamp.get("act") in ("freeze", "refreeze") \
                    and _has_carry_history_stamp(stamp):
                claim = str(stamp.get("authority") or "")
                if claim in AUTHORITY_ORDER:
                    floor = max((floor, claim), key=AUTHORITY_ORDER.index)
        return floor

    def inherited(key, seen):
        if key in seen:
            return local(key)  # the carry validator reports the cycle before any write
        floor = local(key)
        node = graph.get(key) or {}
        edges, _ = _carry_entries(node.get("fm") or {})
        if key != cid and edges:
            stamp = _latest_freeze_stamp(node.get("fm") or {})
            if str((stamp or {}).get("carries") or "") != carry_digest(node):
                edges = []  # a source's draft or stale carries transfer no authority
        for source, _dest in edges:
            source_cid = source.partition("#")[0]
            if source_cid not in graph:
                continue  # the carry validator reports the dangling address
            stamp = _latest_freeze_stamp((graph[source_cid].get("fm") or {}))
            stamped = str((stamp or {}).get("authority") or "")
            levels = [floor, inherited(source_cid, seen | {key})]
            if stamped in AUTHORITY_ORDER:
                levels.append(stamped)
            floor = max(levels, key=AUTHORITY_ORDER.index)
        return floor

    return inherited(cid, set())


_CARRY_ADDRESS = r"/tasks/[A-Za-z0-9][A-Za-z0-9._-]*\.md#RULES:M[1-9][0-9]*"
_CARRY_EDGE = re.compile(rf"\A({_CARRY_ADDRESS}) -> ({_CARRY_ADDRESS})\Z")


def _latest_freeze_stamp(fm: dict):
    return next((s for s in reversed((fm or {}).get("verified") or [])
                 if isinstance(s, dict) and s.get("act") in ("freeze", "refreeze")), None)


def _human_signer(value) -> bool:
    """A human authority claim needs a named signer, not just its namespace."""
    name = str(value or "")
    return name.startswith("human:") and bool(name[len("human:"):].strip())


def _carry_entries(fm: dict) -> tuple:
    """Parse only the Task carry grammar; malformed values never become partial edges."""
    raw = (fm or {}).get("carries")
    if raw is None or raw == []:
        return [], None
    if not isinstance(raw, list):
        return [], f"R:BAD_CARRY `carries:` must be a list of exact Must mappings; got {raw!r}"
    out = []
    for value in raw:
        if not isinstance(value, str) or not (match := _CARRY_EDGE.fullmatch(value)):
            return [], f"R:BAD_CARRY malformed mapping {value!r}; use /tasks/source.md#RULES:M1 -> /tasks/destination.md#RULES:M1"
        out.append(match.groups())
    return out, None


def carry_digest(node: dict) -> str:
    """Seal the complete authored list with an unambiguous, exact-entry encoding."""
    entries = (node.get("fm") or {}).get("carries") or []
    payload = json.dumps(sorted(entries), ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()[:16]


def _has_carry_history_stamp(stamp: dict) -> bool:
    """A non-empty accepted mapping leaves a durable authority floor."""
    sealed = str(stamp.get("carries") or "")
    return bool(sealed) and sealed != carry_digest({"fm": {"carries": []}})


def _has_carry_history(fm: dict) -> bool:
    return any(isinstance(s, dict) and s.get("act") in ("freeze", "refreeze")
               and _has_carry_history_stamp(s) for s in ((fm or {}).get("verified") or []))


def _carry_problem(graph: dict, cid: str, *, accepted: bool) -> str:
    """Validate one transfer and its original chain without modifying either Task."""
    fm = ((graph.get(cid) or {}).get("fm") or {})
    edges, problem = _carry_entries(fm)
    if problem:
        return problem
    if accepted and _has_carry_history(fm):
        stamp = _latest_freeze_stamp(fm)
        sealed = str((stamp or {}).get("carries") or "")
        if not re.fullmatch(r"sha256:[0-9a-f]{16}", sealed) or sealed != carry_digest(graph[cid]):
            return f"R:UNACCEPTED_CARRY {cid} changed its accepted carries after freeze"
    if not edges:
        return ""
    if fm.get("type") != "Task":
        return f"R:BAD_CARRY {cid} is not a Task"

    claims, targets, edge_by_destination = {}, {}, {}
    for owner, node in graph.items():
        other, _ = _carry_entries((node.get("fm") or {}))
        for source, destination in other:
            claims.setdefault(source, []).append(destination)
            targets.setdefault(destination, []).append(source)
            edge_by_destination[destination] = (source, owner)

    def check_edge(source, destination, owner, require_seal):
        if len(claims[source]) > 1:
            return f"R:DUPLICATE_CARRY {source} is claimed by more than one destination obligation"
        if len(targets[destination]) > 1:
            return f"R:BAD_CARRY {destination} ambiguously accepts several originals"
        if destination.partition("#")[0] != owner:
            return f"R:BAD_CARRY {source} targets {destination}, outside {owner}"
        if source.partition("#")[0] == owner:
            return f"R:CYCLIC_CARRY {source} -> {destination} is a self-edge"
        node = graph.get(owner)
        original = graph.get(source.partition("#")[0])
        if node is None or ((node.get("fm") or {}).get("type") != "Task"):
            return f"R:BAD_CARRY {destination} is not a readable Task Must"
        if original is None or ((original.get("fm") or {}).get("type") != "Task"):
            return f"R:BAD_CARRY {source} is not a readable Task Must"
        for endpoint, locator in ((original, source), (node, destination)):
            ids = list(must_lines(read(endpoint["path"], "T2")["body"]).values())
            if ids.count(locator.rpartition(":")[2]) != 1:
                return f"R:BAD_CARRY {source} -> {destination} names a missing or ambiguous Must"
        source_stamp = _latest_freeze_stamp(original.get("fm") or {})
        direction = str((source_stamp or {}).get("direction") or "")
        if not re.fullmatch(r"sha256:[0-9a-f]{16}", direction) \
                or direction != direction_digest(read(original["path"], "T2")):
            return f"R:UNACCEPTED_CARRY {source} has no readable current freeze-class direction"
        # Removing an intermediate Task's `carries:` after its acceptance must not erase its
        # lineage from the graph. The latest source seal still records what it accepted.
        if _has_carry_history(original.get("fm") or {}) \
                and str((source_stamp or {}).get("carries") or "") != carry_digest(original):
            return f"R:UNACCEPTED_CARRY {source} changed its accepted carries after freeze"
        stamped = str(source_stamp.get("authority") or "")
        if stamped not in AUTHORITY_ORDER or AUTHORITY_ORDER.index(stamped) < AUTHORITY_ORDER.index(authority_for(graph, source.partition("#")[0])):
            return f"R:LOWERED_CARRY_AUTHORITY {source} has no freeze at its inherited floor"
        if stamped == "human" and not _human_signer(source_stamp.get("by")):
            return f"R:LOWERED_CARRY_AUTHORITY {source} has no human freeze signer"
        if require_seal:
            stamp = _latest_freeze_stamp(node.get("fm") or {})
            sealed = str((stamp or {}).get("carries") or "")
            if not re.fullmatch(r"sha256:[0-9a-f]{16}", sealed) or sealed != carry_digest(node):
                return f"R:UNACCEPTED_CARRY {destination} has no latest seal for its current carries"
            if str(stamp.get("direction") or "") != direction_digest(read(node["path"], "T2")):
                return f"R:UNACCEPTED_CARRY {destination} changed its Musts after acceptance"
            dest_authority = str(stamp.get("authority") or "")
            if dest_authority not in AUTHORITY_ORDER or AUTHORITY_ORDER.index(dest_authority) < AUTHORITY_ORDER.index(authority_for(graph, owner)):
                return f"R:LOWERED_CARRY_AUTHORITY {destination} must refreeze at its inherited floor"
            if dest_authority == "human" and not _human_signer(stamp.get("by")):
                return f"R:LOWERED_CARRY_AUTHORITY {destination} has no human freeze signer"
        return ""

    # Shape errors, especially a cycle, precede attestation errors: a self-edge cannot have a
    # valid source freeze yet, but the useful refusal is the identity loop the author must fix.
    for source, destination in edges:
        if source.partition("#")[0] == cid:
            return f"R:CYCLIC_CARRY {source} -> {destination} is a self-edge"
    for _source, destination in edges:
        current, seen = destination, set()
        while current in edge_by_destination:
            if current in seen:
                return f"R:CYCLIC_CARRY {destination} revisits {current}"
            seen.add(current)
            current = edge_by_destination[current][0]

    # Follow the one named obligation through accepted links. Re-entering a Task through a
    # different Must is legal; only revisiting the same Must is a cycle.
    for source, destination in edges:
        current, owner, require_seal = (source, destination), cid, accepted
        while True:
            link_source, link_destination = current
            if (bad := check_edge(link_source, link_destination, owner, require_seal)):
                return bad
            if link_source not in edge_by_destination:
                break
            upstream_source, upstream_owner = edge_by_destination[link_source]
            current, owner, require_seal = (upstream_source, link_source), upstream_owner, True
    return ""


def _transition(root, cid: str, sets: dict = None, appends: list = None) -> tuple:
    """The one write path. Surgical edits on RAW text, then an atomic replace."""
    path = Path(root) / cid.lstrip("/")
    if not path.is_file():
        return None, f"no such node: {cid}"
    node = read(path, "T2")
    raw = node["raw"]
    for key, value in (sets or {}).items():
        raw = set_key(raw, key, value)
    for key, item in (appends or []):
        raw = append_item(raw, key, item)
    write(path, f"---\n{raw}\n---\n{node['body']}")
    return read(path, "T0"), ""


# The two CLOSED routing vocabularies a Persona's frontmatter may draw from. They are the
# single source: the scaffold writes them, `doctor` checks against them, and the skill's prose
# is held equal to them by test. Both were closed sets documented in prose and enforced by
# nothing — a value outside them routes NOTHING, silently, and the agent takes the generic
# fallback while reporting success (R:SILENTMISROUTE). A rule that quantifies over a set has
# to enumerate that set.
#
# `explore` joined the task kinds because `--kind explore` is a whole shipped lane with its own
# freeze refusal and its own gate path; while it was outside the taxonomy the selector's
# `task-kinds:` predicate was unsatisfiable for every explore task ever created — the one rung
# ADD reserves for "do not guess" was the one guaranteed a generic agent.
PERSONA_FLOWS = ("design", "build", "advisor", "verify")
PERSONA_TASK_KINDS = ("feature", "refactor", "test", "docs", "ui", "security", "data",
                      "infra", "release", "integration", "explore")


def _explore_body(scaffold: str) -> str:
    """The build-lane scaffold, re-pointed at the explore lane's sections.

    `--kind explore` is a whole shipped lane — a guide, a freeze refusal that requires a budget,
    a gate path that reads `## FINDINGS` instead of a receipt, and three refusal codes of its own
    — with no front door. It emitted the identical build body, and `freeze` then refused it for a
    `budget:` line the body never offered: a lane whose scaffold produces a node the lane's own
    freeze rejects -> "R:UNBUILDABLE".

    A diff of the build body, not a second template, so the two cannot drift: RULES ask for
    questions, `## PLAN` gains the required budget slot, `## FINDINGS` is added empty. `## CHECKS`
    STAYS — explore.md keeps it in acceptance form, "one line per question, `covers:` bound, each
    judged at the gate against `## FINDINGS` — not by pytest".

    The budget is a SLOT, never a seeded number: the whole point of the line is that it is a
    decision, and a number nobody chose is a budget nobody owns. So a freshly scaffolded explore
    is still refused until its author fills it in — refused for a line it was actually offered.
    """
    scaffold = scaffold.replace(
        "- M1 <the rule that must hold>",
        "- M1 <the question this explore must answer, stated so `answered` is judgeable>")
    scaffold = scaffold.replace(
        "## PLAN\ncontract: <the shape this publishes>\n",
        "## PLAN\ncontract: <what this explore will have settled>\n"
        "budget: <one hard number — tool calls / sources / wall-clock; the loop stops when it is spent>\n")
    scaffold = scaffold.replace(
        "- <test_name> · covers: M1 · <what it proves>\nred-first: every check MUST fail first.",
        "- <acceptance line> · covers: M1 · <what a sufficient answer to M1 looks like>\n"
        "judged at the gate against ## FINDINGS, not by pytest.")
    # Empty on purpose: an explore starts with questions, not answers, and the gate's
    # `hollow_explore` refusal is what makes "unanswered" a recorded outcome rather than a silent
    # one. Pre-filling a finding would fabricate the answer the lane exists to go get.
    return scaffold.replace(
        "\n## LESSONS\n",
        "\n## FINDINGS\n"
        "<empty until the loop runs — then one line per finding:\n"
        " F1 (answers M1) · <what was found> · (evidence: <file:line | url | command>)>\n"
        "\n## LESSONS\n")


# Everything `new` may be handed. `fm.update(fields)` used to let ANY keyword through into
# frontmatter, where it reads as authored data that nothing wrote and no reader consumes
# (R:GHOSTFIELD) — `goal=` was the live instance: accepted, sorted neatly into the key order,
# and leaving the node with one authored goal in frontmatter and one scaffold goal in its CARD.
# The scalar slots this verb owns, PLUS every edge key from the one registry that defines them —
# derived, never a second list (a copied set drifts the moment a key is added, which is the
# `covers:` two-grammar shape one layer up).
NEW_FIELDS = ("title", "goal", "depth", "kind", "sensitivity", "scope", "gives", "persona",
              "vibe", "flow", "task-kinds", "use-when", "not-when", "description",
              "sources") + EDGE_KEYS


def new(root, node_type: str, slug: str, **fields) -> tuple:
    """Create a typed node. A colliding slug reports and writes nothing (R:DUPSLUG)."""
    root = Path(root)
    unknown = sorted(k for k in fields if k not in NEW_FIELDS)
    if unknown:
        return None, (f"`new` does not write {', '.join(unknown)} — an unrecognised field would "
                      f'land in frontmatter as data nothing wrote -> "R:GHOSTFIELD"'
                      f"\nnext: pass one of {' · '.join(NEW_FIELDS)}, or set it after creation "
                      f"with the verb that owns it")
    rel = f"{TYPE_DIR.get(node_type, 'tasks')}/{slug}.md"
    path = root / rel
    # Bundle-wide, not per-directory. `run` writes to `tasks/{slug}.d/runs` and `latest_receipt`
    # reads it, both from the BARE slug — so two nodes sharing a slug share one receipt stream,
    # and a red Task closes on a Milestone's green run with R:GREENLIE reading evidence that was
    # never its own. `_resolve` compounds it: it returns the first scan-order match, silently
    # retargeting every other verb. One slug, one node, and the receipt path is unambiguous
    # by construction -> "R:DUPSLUG".
    for other in sorted(set(TYPE_DIR.values())):
        held = root / other / f"{slug}.md"
        if held.exists():
            return None, (f"slug already taken: {slug} (/{other}/{slug}.md) — a slug names ONE "
                          f"node bundle-wide, because a receipt stream is addressed by slug alone"
                          f'\nnext: pick another slug, or `add status` to see it -> "R:DUPSLUG"')

    # The one slot `new` DOES judge, and deliberately: `sensitivity:` is not free text, it is the
    # enum that computes the authority floor. Recording `high` verbatim floored the node at
    # `process` — the notary stance ("a supplied value is recorded verbatim") is right for prose
    # slots and wrong for an instrument the engine must read back. `init` already refuses an
    # unknown `--profile` for the same reason -> "R:SILENT_FLOOR".
    sens = fields.get("sensitivity")
    if sens not in (None, "") and str(sens) not in SENSITIVITY_FLOOR:
        return None, (f"unreadable sensitivity {str(sens)!r} — the floor it declares cannot be "
                      f'computed, and an unreadable declaration is not the lowest floor -> "R:SILENT_FLOOR"'
                      f"\nnext: add new {node_type} {slug} --sensitivity "
                      f"<{' | '.join(SENSITIVITY_FLOOR)}>")

    # The SECOND slot `new` judges, and for the same reason: `kind:` is not prose, it is the Task
    # side of a routing predicate whose Persona side (`task-kinds:`) is already validated. Held to
    # different standards, the unvalidated side is where the drift lands — `--kind frontend` was
    # accepted and `doctor` reported no findings, so the task silently lost its lens for life.
    # Absence stays legal: `kind:` is optional, and a missing value is not an unreadable one
    # -> "R:SILENT_KIND".
    # The THIRD slot `new` judges: `supersedes:` is the edge that carries closed history forward,
    # and an edge to a node that does not exist is worse than no edge — `show` renders it
    # `— unresolved` and the successor's own provenance is a claim nobody can follow. Resolved
    # HERE, so the key holds a cid whatever the author typed (a bare slug or an address), which is
    # what `edges()` and `neighborhood()` already assume of every EDGE_KEYS value
    # -> "R:PHANTOMPREDECESSOR".
    sup = fields.get("supersedes")
    if sup not in (None, "", []):
        landed = []
        for ref in (sup if isinstance(sup, list) else [sup]):
            target, _ = resolve_ref(root, str(ref))
            if target is None or "#" in target:
                return None, (f"`--supersedes {ref}` resolves to no node — a successor that cannot "
                              f'name its predecessor records no history at all -> "R:PHANTOMPREDECESSOR"'
                              f"\nnext: add status   (it lists what this bundle holds), "
                              f"then add new {node_type} {slug} --supersedes <slug or cid>")
            landed.append(target)
        fields["supersedes"] = landed

    kind = fields.get("kind")
    if kind not in (None, "") and str(kind) not in PERSONA_TASK_KINDS:
        return None, (f"unroutable kind {str(kind)!r} — no persona can declare it in `task-kinds:`, "
                      f'so the node would carry a lens nobody can match -> "R:SILENT_KIND"'
                      f"\nnext: add new {node_type} {slug} --kind "
                      f"<{' | '.join(PERSONA_TASK_KINDS)}>")

    order = ["type", "title", "goal", "status", "depth", "kind", "sensitivity", "vibe", "flow",
             "task-kinds", "use-when", "not-when", "description", "sources",
             "milestone", "scope", "gives"]
    # The CARD is where every reader and every guard looks for a goal, so that is where a seeded
    # goal goes — never frontmatter, which would leave the node carrying two (R:TWOGOALS). The
    # planner holds this one line at creation and had nowhere to put it until now.
    seeded_goal = fields.pop("goal", None)
    fm = {"type": node_type, "title": fields.pop("title", slug)}
    if node_type in LIFECYCLE_TYPES:  # a Persona/Prompt/Run has no lifecycle — no task status
        fm["status"] = "direction"
    # `gives:` is read by the direction digest and by every brief that resolves a `needs:`
    # ref — and it was scaffolded NOWHERE, in neither the body template nor this key order.
    # It came back empty in 3 of 3 live runs for exactly the reason the assumption did:
    # an instruction with no slot to fill is an instruction that does not happen.
    if node_type == "Task" and fields.get("gives") is None:
        fm["gives"] = ["S1 <the surface this publishes — an endpoint, function, or section>"]
    # `scope:` had a slot in `## PLAN` and its only reader is `fm.get("scope")` — so an author who
    # filled the slot the scaffold offered got "the node declares no `scope:`" at the gate, and
    # `phantom_scope` could never fire on a scaffolded node. A slot no reader reads consumes the
    # author's attention and returns nothing; two slots is worse still, because the author fills
    # the nearer one -> "R:DEADSLOT". Tasks only: a Milestone earns no receipt, so a scope on one
    # would be a second dead slot.
    #
    # EMPTY, deliberately — the opposite of `gives:` above, and measured: a placeholder turned 29
    # green tests red. `gives:` is descriptive, so an unfilled placeholder is merely unhelpful;
    # `scope:` is ENFORCED, so a placeholder makes every fresh node DECLARE a scope it cannot
    # satisfy — freshness degrades, and an edit outside it is a violation. The key's presence in
    # frontmatter is the prompt; its emptiness is what every reader already means by "none".
    if node_type == "Task" and fields.get("scope") is None:
        fm["scope"] = []
    # A Persona is discoverable by its `use-when:` — the one field a tool reads to place the lens.
    # The rest of the contract's routing keys (vibe/flow/task-kinds/not-when) plus OKF v0.2's
    # `description:` and provenance `sources:` get slots too — the `gives:` lesson above, learned
    # a second time. Slots, never validation: a supplied value is recorded verbatim, and `new`
    # judges nothing about any slot's content (the engine stays a notary).
    if node_type == "Persona":
        for key, hole in (
                ("vibe", "<one-line essence — what this persona keeps true>"),
                ("flow", "<design | build | advisor | verify — comma-separate if >1>"),
                ("task-kinds", "<from the closed taxonomy, comma-separated>"),
                ("use-when", "<when this lens applies — enumerate triggers>"),
                ("not-when", "<the near-miss that belongs to a named sibling>"),
                ("description", "<one line for a cold catalogue reader — OKF-recommended>"),
                ("sources", ["<teacher file or material distilled from — optional>"]),
        ):
            if fields.get(key) is None:
                fm[key] = hole
    fm.update({k: v for k, v in fields.items() if v is not None})
    lines = []
    for key in order + [k for k in fm if k not in order]:
        if key not in fm:
            continue
        value = fm[key]
        if isinstance(value, list):
            lines.append(f"{key}:\n" + "\n".join(f"  - {v}" for v in value))
        else:
            lines.append(f"{key}: {value}")
    lines += [_stamp(), "verified: []"]

    path.parent.mkdir(parents=True, exist_ok=True)
    # the CARD scaffold carries a `{slug}` marker for the created node's own slug — substitute it,
    # or every new task ships an unexpanded placeholder in its `next:` affordance.
    scaffold = BODIES.get(node_type, "## CARD\ngoal: <one line>\n").replace("{slug}", slug)
    if seeded_goal:
        scaffold = scaffold.replace("goal: <one line>", f"goal: {_oneline(seeded_goal)}", 1)
    if node_type == "Task" and str(fm.get("kind") or "") == "explore":
        scaffold = _explore_body(scaffold)
    write(path, "---\n" + "\n".join(lines) + "\n---\n" + scaffold)
    # freeze is a lifecycle act — a Persona/Prompt/Run is done the moment it is written.
    # A file of placeholders is a scaffold, and `freeze` is guaranteed to refuse one — so the
    # message `new` hands back names the authoring work, not the approval that follows it.
    nxt = (AUTHOR_NEXT.get(node_type, AUTHOR_NEXT["Task"]).format(slug=slug)
           if node_type in LIFECYCLE_TYPES else "add status")
    return "/" + rel, f"created {rel}\nnext: {nxt}"


def freeze(root, cid: str, by: str, authority: str = None) -> tuple:
    """Append a freeze stamp sealing RULES · CHECKS · `gives:`. A second freeze REFREEZES — §3.5,
    history is append-only.

    Refuses an unauthored node. 2.5.0 refused this as `contract_not_drafted`; 3.0 dropped the check
    and stamped anything, which left `gate` as the only place a template was caught — i.e. AFTER the
    whole build. Since freeze is precisely the stamp that says "direction is closed", approving a
    scaffold is the one thing it must never do (constraint 1, "Direction before speed").
    """
    graph = scan(root)
    entry = graph.get(cid) or {}
    if not entry.get("path"):
        return None, f"no such node: {cid}\nnext: add status"
    slug = cid.rsplit("/", 1)[-1][:-3]

    node_t2 = read(entry["path"], "T2")
    if (entry.get("fm") or {}).get("type") == "Milestone":
        # The guard `placeholders_in` could never make: it reads RULES · ASSUMPTIONS · CHECKS and a
        # Milestone body carries none of those three, so it returned [] for EVERY milestone and the
        # ONE human approval was stampable against a node stating no goal and no exit criterion.
        ms_stubs = _milestone_stubs(node_t2)
        if ms_stubs:
            # `None`, like every other rung — this one answered `False` alone, and a caller
            # writing `if node is None` walked straight past it. Two inverted assertions in two
            # test files, hours apart, both by a reader who had checked the OTHER rung
            # -> "R:TWOSHAPES". The message is unchanged.
            return None, (f"cannot freeze `{slug}` — this milestone is still a scaffold: "
                           + " · ".join(ms_stubs)
                           + f"\nnext: {AUTHOR_NEXT['Milestone'].format(slug=slug)}")
    stubs = placeholders_in(node_t2)
    if stubs:
        return None, (f"cannot freeze `{slug}` — the node still carries template placeholders: "
                      + " · ".join(stubs)
                      + f"\nnext: author {slug}'s RULES, ASSUMPTIONS and CHECKS, "
                        f"then add freeze {slug}")
    if (carry_error := _carry_problem(graph, cid, accepted=False)):
        return None, f"cannot freeze `{slug}` — {carry_error}\nnext: repair its `carries:` mapping and source approval"

    # No surfaces would mean nothing to sweep — a one-line off switch for the whole gate.
    if _section_of(node_t2.get("body") or "", "ASSUMPTIONS").strip() \
            and str((node_t2.get("fm") or {}).get("depth") or "standard") != "quick" \
            and gives_unauthored(node_t2):
        return None, (f"cannot freeze `{slug}` — `gives:` is unauthored, so there are no "
                      f"surfaces to sweep"
                      f"\nnext: list what {slug} publishes as `gives:` entries "
                      f"(`- S1 <surface> — <what a caller gets>`), then add freeze {slug}")

    # A collapsed surface is the granularity evasion: several endpoints under one S id
    # shrinks the matrix and the [who]/[which] questions get asked once, about the
    # loudest endpoint. Same exemptions as the sweep (quick depth; no section).
    if _section_of(node_t2.get("body") or "", "ASSUMPTIONS").strip() \
            and str((node_t2.get("fm") or {}).get("depth") or "standard") != "quick":
        collapsed = collapsed_surfaces(node_t2)
        if collapsed:
            return None, (f"cannot freeze `{slug}` — one surface per S id: "
                          + " · ".join(collapsed)
                          + " each name several surfaces (HTTP methods, callables, or "
                            "backticked documents), so the sweep is asking one set of "
                            "questions about several surfaces"
                          f"\nnext: split each into its own `- S<n> <one surface>` "
                          f"entry, re-cover them in ASSUMPTIONS, then add freeze {slug}")

    # Non-empty is not complete. Three live runs each recorded 5-7 real assumptions and
    # all three still shipped a silent decision, because nothing asked whether the list
    # covered every surface. Name the specific gaps: "incomplete" is not actionable, and a
    # refusal an author cannot act on is one they learn to route around.
    unswept = assumption_sweep(node_t2)
    if unswept:
        shown = " · ".join(f"{d}:{m}" for d, m in unswept[:6])
        more = f" (+{len(unswept) - 6} more)" if len(unswept) > 6 else ""
        return None, (f"cannot freeze `{slug}` — these (dimension, surface) pairs are unswept: "
                      f"{shown}{more}"
                      f"\nnext: add an ASSUMPTIONS line `- A<n> [<dim>] covers: <S ids> · …`, "
                      f"or retire a dimension with `[<dim>] n/a · <why>`")

    # M31 recorded this failure three times in ONE milestone. M38 recorded the fourth — on the
    # milestone authored to stop it, an `E` id caught after a full build, a brief and three
    # receipts. The gate is the last place in the loop, so the cost of learning there is the
    # whole build; the obligation is created HERE, and so the refusal belongs here.
    #
    # The `next:` names BINDING first and retiring second, on purpose (R:DELETEPAST). The
    # cheapest way past "no reported passing check" has always been to delete the edge, and a
    # refusal whose easiest exit destroys the obligation teaches exactly the wrong lesson.
    # An explore is exempt, and not as a softening: its gate reads the cited `## FINDINGS`
    # brief directly and takes NO run receipt, so there is no reported check for a `covers:`
    # entry to point at. Requiring one would make the shipped explore scaffold unfreezable
    # once filled exactly as it instructs — the affordance-truth failure, rebuilt.
    uncovered = ([] if str((node_t2.get("fm") or {}).get("kind") or "") == "explore"
                 else uncovered_obligations(node_t2))
    if uncovered:
        return None, (f"cannot freeze `{slug}` — these authored obligations are named by no "
                      f'check: {", ".join(uncovered)} -> "R:UNCOVERED"'
                      f"\nnext: add a `covers:` entry naming each in `## CHECKS` — or retire the "
                      f"obligation itself (drop its `probe:`, or return the edge to its slot) — "
                      f"then add freeze {slug}")

    # R:UNBOUNDED (task sources-receipt) — an explore's approval IS questions plus a budget.
    # Presence only, never arithmetic: the engine is a notary; judging the number stays human,
    # exactly as exit criteria are read but never scored.
    # `[^<\s]` and not `\S`: the scaffold now OFFERS a `budget:` slot, and a slot must never
    # satisfy the requirement it prompts for. `placeholders_in` does not read `## PLAN`, so
    # `budget: <one hard number …>` passed a presence test and froze an explore with no budget —
    # the milestone's own defect class, a well-formed value attesting nothing.
    if str((node_t2.get("fm") or {}).get("kind") or "") == "explore" \
            and not re.search(r"^budget:\s*[^<\s]", _section_of(node_t2.get("body") or "", "PLAN"), re.M):
        return None, (f'cannot freeze `{slug}` — an explore freezes on questions PLUS a budget, '
                      f'and `## PLAN` carries no `budget:` line -> "R:UNBOUNDED"'
                      f"\nnext: add one hard `budget:` line (tool calls · sources · wall-clock) "
                      f"to ## PLAN, then add freeze {slug}")

    # LAST in the ladder, and deliberately (M9): every refusal above says the contract is not
    # finished, and there is no sense putting template text to a human. Everything above checks
    # the DOCUMENT; this is the only one that checks the CONVERSATION.
    #
    # Keyed on the COMPUTED floor, never on the `authority` argument, because the line below is
    # `authority or authority_for(...)`: reading the argument would let `--authority process`
    # switch the interview off on a security node -> the guard would ship with its own off switch.
    # TWO arming conditions, and the second INVERTS the first's rule on purpose. A Milestone
    # carries no `sensitivity:`, so its computed floor is never `human` and a floor-keyed rung
    # would be dead code on exactly the node where the expensive stamp lives. Here the CLAIM is
    # what is guarded: `--authority human` asserts a human read this text, and that assertion is
    # what M34 shows is cheap to write and impossible to withdraw. Claiming `plan` instead is
    # the LOWER, honest claim M34 itself prescribes, so leaving it open is not an off switch
    # (R:OFFSWITCH) — it is the recommended path for an AI driving under a standing go-ahead.
    claims_human = (sfm_type := (node_t2.get("fm") or {}).get("type")) == "Milestone" \
        and str(authority or "") == "human"
    if authority_for(graph, cid) == "human" or claims_human:
        owed = interview_gap(node_t2, entry.get("fm") or {},
                             require_human_signer=(bool(_carry_entries(entry.get("fm") or {})[0])
                             or _has_carry_history(entry.get("fm") or {}))
                             and authority_for(graph, cid) == "human")
        if owed:
            shown = ", ".join(owed[:6]) + (f" (+{len(owed) - 6} more)" if len(owed) > 6 else "")
            forward = (f"\nnext: add interview {slug} — or stamp the honest lower claim, "
                       f'add freeze {slug} --by "<name>" --authority plan'
                       if sfm_type == "Milestone" else f"\nnext: add interview {slug}")
            return None, (f"cannot freeze `{slug}` — the ONE human approval is being asked for "
                          f"decisions no human has been shown: {shown}"
                          f' -> "R:UNINTERVIEWED"' + forward)

    # R:NOFLOOR (regression-floor) — the host suite is a decision the PLAN records, never a memory:
    # the 3.2 cut shipped a task green over a red host because the floor lived in prose. Armed
    # exactly where the refute rung arms, so the mechanical lane, quick depth and an explore never pay.
    if _rung_bound(graph, cid, entry.get("fm") or {}) and regression_floor(node_t2) is None:
        return None, (f"cannot freeze `{slug}` — `## PLAN` carries no regression floor: a rung-bound task "
                      f'says what host suite runs beside its own checks -> "R:NOFLOOR"\nnext: add one line '
                      f"to ## PLAN — `regression: full | affected · <cmd> · <why>` or `regression: none · "
                      f"<why>` — then add freeze {slug}")
    authority, floor_err = claimed_authority(authority, authority_for(graph, cid), "freeze", slug)
    if floor_err:
        code = "R:LOWERED_CARRY_AUTHORITY " if _carry_entries(entry.get("fm") or {})[0] \
            or _has_carry_history(entry.get("fm") or {}) else ""
        return None, f"cannot freeze `{slug}` — " + code + floor_err
    if (_carry_entries(entry.get("fm") or {})[0] or _has_carry_history(entry.get("fm") or {})) \
            and authority == "human" \
            and not _human_signer(by):
        return None, (f"cannot freeze `{slug}` — R:LOWERED_CARRY_AUTHORITY a human-floor carry "
                      f"needs this destination's own `human:` signer\nnext: add freeze {slug} --by \"human:<name>\"")
    stamps = (entry.get("fm") or {}).get("verified") or []
    act = "refreeze" if any(s.get("act") in ("freeze", "refreeze") for s in stamps
                            if isinstance(s, dict)) else "freeze"
    # consumers-go-stale (FORMAT §3.5): the stamp pins the published surface alone and, on a
    # consumer, what it read from each `#gives` it needs — so a moved contract is a digest
    # comparison any later reader can make, with no clock and no stored back-reference.
    prev_gives = next((str(x.get("gives")) for x in reversed(stamps)
                       if isinstance(x, dict) and x.get("act") in ("freeze", "refreeze") and "gives" in x), None)
    new_gives = gives_digest(node_t2)
    pins = needs_pins(graph, cid)
    exit_pin = (f', exit: "{exit_digest(node_t2)}"'
                if (node_t2.get("fm") or {}).get("type") == "Milestone" else "")
    node, err = _transition(root, cid, appends=[
        ("verified", f'{{ by: "{_oneline(by)}", at: {_today()}, act: {act}, authority: {authority}, '
                     f'direction: "{direction_digest(node_t2)}", '
                     f'binding: "{binding_digest(node_t2)}", gives: "{new_gives}", '
                     f'scope: "{scope_seal_digest(node_t2)}"'
                     + (f', carries: "{carry_digest(node_t2)}"' if sfm_type == "Task" else "")
                     + (f', needs: "{pins}"' if pins else "") + exit_pin + " }")])
    if err:
        return None, err + "\nnext: add status"
    stale_note = ""
    if act == "refreeze" and prev_gives and prev_gives != new_gives:
        # The M3 comparison, not a `prev != new` proxy: name exactly the open consumers whose pin
        # differs from the digest just stamped — a round trip back to a pinned digest names none
        # (found by the fourth T2 refute).
        cons = [c for c in consumers_of(graph, cid)
                if (pin := _pins_of(graph, c).get(cid)) and pin != _short(new_gives)]
        if cons:
            slugs = [c.rsplit("/", 1)[-1][:-3] for c in cons]
            stale_note = (f"\nnotice: `gives:` moved — consumers now stale: {', '.join(slugs)} — each "
                          f"re-crosses ({' · '.join(f'add freeze {x}' for x in slugs)})")
    # A NOTICE, never a refusal (two-mode-notice): armed exactly where the refute rung arms, so
    # the mechanical lane never pays for a rule aimed at payments. The stamp above is already
    # written; this line only names what the router asks for and the author can still add.
    notice = ""
    if _rung_bound(graph, cid, entry.get("fm") or {}):
        # A NOTICE, never a refusal: the human floor already REFUSES an unsourced Must through the
        # interview (it is an open decision like any other), and below that floor the tail is a
        # habit being taught, not a gate being added -> "R:SOURCEASREFUSAL".
        # The ONE beat where a human reads the whole node, and only there (A3): below it the slot
        # is a habit being taught, not a gate being added -> "R:OBSERVEASREFUSAL".
        if authority_for(graph, cid) == "human" and not observes(node_t2):
            notice += (f"\nnotice: no observes: line — name the runtime signal that would show "
                       f"M{rules_of(node_t2)[0][1:] if rules_of(node_t2) else '<n>'} broken (PLAN, O<n>)")
        unsourced = [mid for mid, _ in _musts_without_source(node_t2)]
        if unsourced:
            notice += (f"\nnotice: {', '.join(unsourced)} carry no from: — a Must is what you were "
                       f"told; add interview {slug} or write (from: …)")
        single = single_mode_musts(entry)
        if single:
            notice += (f"\nnotice: {', '.join(f'{m} ({w})' for m, w in single)} "
                      f"{'carries' if len(single) == 1 else 'carry'} one evidence mode — a plan-floor "
                      f"Must carries two (direction.md § router)")
    return node, (f"{act} recorded at authority `{authority}`" + notice + stale_note
                  + f"\nnext: add brief {slug} — record the build entry, then build "
                  f"(`add run {slug} -- <cmd>`)")


def done(root, cid: str, override: str = None, by: str = None) -> tuple:
    """Transition to `done` only when a gate stamp entitles it.

    Refusing to create an unsupported record is the notary's duty, not guarding: this never
    prevents a human from writing the stamp themselves with their own authority.
    """
    graph = scan(root)
    node = graph.get(cid)
    if node is None:
        return None, ["node"], f"no such node: {cid}\nnext: add status"

    if (carry_error := _carry_problem(graph, cid, accepted=True)):
        return None, ["carries"], f"cannot record `done` — {carry_error}\nnext: repair and refreeze {cid}"

    required = authority_for(graph, cid)
    if (_carry_entries(node.get("fm") or {})[0] or _has_carry_history(node.get("fm") or {})) \
            and required == "human" and override is not None:
        return None, ["authority"], ("cannot record `done` — R:LOWERED_CARRY_AUTHORITY "
                                      "a security carry's HARD-STOP cannot be overridden")
    stamps = [s for s in ((node["fm"] or {}).get("verified") or []) if isinstance(s, dict)]
    # a reopen RESETS the gate (loop.md): only gates that postdate the last reopen entitle `done`,
    # so a stale pre-reopen PASS cannot re-entitle a task the loop returned to a beat.
    last_reopen = max((i for i, s in enumerate(stamps) if s.get("act") == "reopen"), default=-1)
    gates = [(i, s) for i, s in enumerate(stamps)
             if i > last_reopen and s.get("act") == "gate"]
    # A gate's VERDICT, not merely its existence. A HARD-STOP is a finding written down, not a
    # node that shipped; it entitles nothing. Resolving it is the normal path — record the PASS
    # that answers the finding and this list fills again.
    stopped = [s for _, s in gates if str(s.get("outcome")) == "HARD-STOP"]
    # A stamp with NO readable `outcome` closes. Interviewed 2026-09-03, A4 marked `correct`:
    # an engine that recorded no verdict field left nodes that cannot be re-gated, so this fails
    # OPEN rather than stranding them. Only a verdict that reads as HARD-STOP withholds `done`.
    gates = [(i, s) for i, s in gates
             if s.get("outcome") is None or str(s.get("outcome")) in CLOSING_VERDICTS]
    def gate_rank(stamp):
        claim = str(stamp.get("authority") or "")
        return AUTHORITY_ORDER.index(claim) if claim in AUTHORITY_ORDER else -1

    entitled = [(i, s) for i, s in gates if gate_rank(s) >= AUTHORITY_ORDER.index(required)]
    if (_carry_entries(node.get("fm") or {})[0] or _has_carry_history(node.get("fm") or {})) \
            and required == "human":
        freeze_stamp = _latest_freeze_stamp(node.get("fm") or {})
        if not _human_signer((freeze_stamp or {}).get("by")):
            return None, ["authority"], ("cannot record `done` — R:LOWERED_CARRY_AUTHORITY "
                                          "this destination has no human freeze signer")
        if entitled and not any(_human_signer(s.get("by")) for _, s in entitled):
            return None, ["authority"], ("cannot record `done` — R:LOWERED_CARRY_AUTHORITY "
                                          "this destination has no human closing gate signer")
        entitled = [(i, s) for i, s in entitled if _human_signer(s.get("by"))]
    # The seal, checked at the terminal write. `gate` refuses an unsealed PASS (R:UNSEALED, #206)
    # and — since this task — an unsealed RISK-ACCEPTED too, but `done` is the verb that actually
    # writes `status: done`, and it counted a gate stamp without ever asking whether the ONE
    # approval had happened. Any (re)freeze BEFORE the entitling gate satisfies it; a refreeze
    # recorded afterwards (the re-cross pattern) is not required to.
    seal_at = min((i for i, s in enumerate(stamps)
                   if s.get("act") in ("freeze", "refreeze")), default=None)
    slug = cid.rsplit('/', 1)[-1][:-3]

    missing, fix = [], f"add gate {slug}"
    if not gates and stopped:
        # Interviewed 2026-09-03. A1 was marked `correct` — a human may ship over a finding — but
        # its literal form could not be built: a gate's authority is COMPUTED from the floor, so
        # on a security node EVERY stop is stamped `human` and "human authority closes it" is the
        # original defect wearing a flag. The human resolved it: the force-close is a deliberate
        # ACT carrying its own reason, so the ledger shows a person chose to ship over a finding
        # rather than the floor quietly permitting it. It answers the VERDICT only — the seal
        # below is checked exactly as before, so an override never buys the ONE approval.
        if override is None:
            missing.append("a gate that CLOSES — the latest verdict is `HARD-STOP`, which records "
                           "a finding and stops the node; it does not ship it")
            fix = (f"resolve the finding, then add gate {slug} PASS   (or, to ship over it, "
                   f'add done {slug} --override "<why this is acceptable>")')
        elif not str(override).strip():
            missing.append("a reason for the override — shipping over a recorded finding is "
                           "exactly the decision that has to be explained")
            fix = f'add done {slug} --override "<why this is acceptable>"'
        else:
            gates = [(i, s) for i, s in enumerate(stamps)
                     if i > last_reopen and s.get("act") == "gate"]
            # The seal, on the override's OWN path. The comment above says it is "checked
            # exactly as before"; before this line it was not — the branch reassigned `gates`
            # and fell out of the chain, so the `elif` holding the seal test was unreachable
            # from here. The invariant held only because `gate` refuses a HARD-STOP on an
            # unsealed node upstream, which is one refactor away from absent. A guard that
            # depends on another verb refusing is not a guard on this path (M7).
            if seal_at is None or all(i < seal_at for i, _ in gates):
                missing.append("a freeze preceding the gate — the ONE human approval ADD asks "
                               "for did not happen, so this gate closed a node nobody approved")
                fix = f'add freeze {slug} --by "<name>", then re-gate'
    elif not gates:
        missing.append(f"a gate stamp (none recorded; `{required}` or above is required)")
    elif not entitled:
        missing.append(f"a gate at authority `{required}` — highest recorded is "
                       f"`{max((s for _, s in gates), key=gate_rank).get('authority')}`")
    elif seal_at is None or all(i < seal_at for i, _ in entitled):
        missing.append("a freeze preceding the gate — the ONE human approval ADD asks for did "
                       "not happen, so this gate closed a node nobody ever approved")
        fix = f'add freeze {slug} --by "<name>", then re-gate'
    if missing:
        return None, missing, ("cannot record `done` — " + "; ".join(missing) +
                                f"\nnext: {fix}")

    appends = []
    if override and str(override).strip():
        appends = [("verified", f'{{ by: "{_oneline(by or "process:done")}", at: {_today()}, '
                                 f'act: done, override: "{_oneline(override)}" }}')]
    _transition(root, cid, sets={"status": "done"}, appends=appends)
    render_evidence(root, cid)          # the closed record: `none recorded` is now a fact
    harvest_lessons(root, cid)
    tail = " (override recorded)" if appends else ""
    return True, [], f"{cid} is done{tail}\nnext: add status"


def reopen(root, cid: str, to: str, reason: str) -> tuple:
    """Return a done task to a beat with a reset gate and a recorded reason (loop.md).

    Fired by the loop's judgment when a deepened verify finds a criterion unmet on a task already
    `done`. It records a `reopen` stamp carrying the reason; the gate resets because `done` counts
    only gates that postdate this stamp — a stale PASS cannot re-entitle the reopened task.
    """
    root = Path(root)
    node = scan(root).get(cid)
    if node is None:
        return None, f"no such node: {cid}\nnext: add status"
    fm = node["fm"] or {}
    if fm.get("type") != "Task":
        return None, f"{cid} is not a Task — reopen returns a task to a beat\nnext: add status"
    if fm.get("status") != "done":
        return None, f"only a done task is reopened — {cid} is `{fm.get('status')}`\nnext: add status"
    if to not in ACTIVE_STATES:
        return None, f"`{to}` is not a beat ({' · '.join(ACTIVE_STATES)})\nnext: reopen --to build"
    # loop.md called this "resolved by hand" and pointed at a `status --check` finding the engine
    # never had. A reopen inside a CLOSED milestone rewrites history the goal-gate already
    # published: the milestone's exit boxes were checked against this task being done, and its
    # `verified[]` carries a PASS that the close depended on. The successor form keeps both —
    # the old node stands untouched, the new one names it -> "R:CLOSEDHISTORY".
    ms_ref = fm.get("milestone")
    ms_cid, _ = resolve_ref(root, str(ms_ref)) if ms_ref not in (None, "") else (None, "")
    ms_status = str(((scan(root).get(ms_cid or "") or {}).get("fm") or {}).get("status") or "")
    if ms_status in CLOSED_MILESTONE_STATES:
        slug = cid.rsplit("/", 1)[-1][:-3]
        return None, (f"cannot reopen `{cid}` — its milestone {ms_cid} is `{ms_status}`, and the close "
                      f"that published it counted this task done: reopening rewrites history a goal-gate "
                      f'already answered for -> "R:CLOSEDHISTORY"'
                      f"\nnext: add new Task {slug}-2 --supersedes /tasks/{slug}.md --milestone "
                      f"<an open milestone>   (the old node, its receipts and its PASS stand)")
    # a stamp is a pre-formatted ABF flow-map STRING, not a dict — a dict serialises as Python
    # repr (`{'by': …}`) and parses back with quoted keys, so `s.get("act")` would miss it.
    stamp = f'{{ by: loop, at: {_today()}, act: reopen, to: {to}, reason: "{reason}" }}'
    _transition(root, cid, sets={"status": to}, appends=[("verified", stamp)])
    return True, f"{cid} reopened to {to} — gate reset\nnext: work the {to} beat, then re-gate"


def _box_lines(body: str, section: str = None):
    """(line index, marked, text, section) for every REAL checkbox in `body`.

    Fenced blocks are skipped: a node that quotes `- [x]` as an example (this bundle's own
    milestones do) would otherwise shift every index, so the number a human counts off the
    rendered file would not be the number the verb writes to.
    """
    out, fence, inside, here = [], None, section is None, "body"
    lines = body.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        fence, boundary = _fence_step(line, fence)
        if boundary:
            continue
        if fence is not None:
            continue
        if line.startswith("## "):
            here = stripped[3:].strip()
            if section is not None:
                if inside:
                    break          # `_section_of` reads the FIRST block only; the goal-gate
                                   # tallies through it, so enumerating past it would let
                                   # `check` tick a box the gate can never count.
                inside = here.lower() == section.lower()
            continue
        if not inside:
            continue
        m = BOX.match(line)
        if m:
            out.append((i, m.group(1).lower() == "x", _joined_text(lines, i, m.group(2)), here))
    return out


def _continues(line: str) -> bool:
    """An INDENTED, non-empty line that starts no new box — the rest of a wrapped criterion.

    Criteria in real milestones wrap across source lines. Previewing only the first one leaves
    every row trailing off mid-sentence, and the preview is what an operator picks an index
    from. Joining is display-only: the node keeps its own wrapping, byte for byte.
    """
    return bool(line[:1].isspace() and line.strip()
                and not BOX.match(line)
                and not line.strip().startswith(("```", "~~~", "#")))


def _joined_text(lines, i: int, first: str) -> str:
    parts = [first.strip()]
    for line in lines[i + 1:]:
        if not _continues(line):
            break
        parts.append(line.strip())
    return " ".join(p for p in parts if p)


def _stamp_boxes(moved) -> str:
    """`EXIT:1,3` — the section a box actually lives in, so an audit reads WHERE, not just how many."""
    order, groups = [], {}
    for n, _text, where_box in moved:
        if where_box not in groups:
            order.append(where_box)
            groups[where_box] = []
        groups[where_box].append(str(n))
    return " ".join(f"{s}:{','.join(groups[s])}" for s in order)


def check(root, cid: str, indices, off: bool = False, section: str = None,
          by: str = None, via: str = "process") -> tuple:
    """Mark (or with `off`, unmark) checklist boxes, and record who did it.

    The engine has always READ this tally — `milestone_done` gates a milestone closed on it —
    while offering no way to write one, so every tick was a hand edit to markdown the engine
    parses. This verb deliberately does NOT defend the goal-gate: it ticks any box in any node
    for any caller (decided 2026-08-28). What replaces the defence is attribution — one stamp
    per invocation, and `milestone_done` naming the checkers when it closes.

    Designed for failure: every index is validated BEFORE any line is rewritten, and the write
    is one atomic replace, so a refusal or a crash leaves the node fully old or fully new.
    """
    root = Path(root)
    node = scan(root).get(cid)
    if node is None:
        return None, f"no such node: {cid}\nnext: add status"
    slug = cid.rsplit("/", 1)[-1][:-3]
    path = node["path"]
    doc = read(path, "T2")
    body = doc["body"]

    if section is not None:
        headings = [ln.strip()[3:] for ln in body.splitlines() if ln.startswith("## ")]
        if not any(h.lower() == section.lower() for h in headings):
            carries = ", ".join(headings) if headings else "no `## ` sections at all"
            return None, (f"no `## {section}` section in {cid} — it carries {carries}\n"
                           f"next: add check {slug} <n> --section <one of those>")

    region = _section_of(body, section) if section else body
    where = f"`## {section}`" if section else "its body"
    if not _fence_balanced(region):
        return None, (f"{cid}'s {where} has an unclosed code fence — `check` skips fenced "
                       f"regions, so the index you counted off the file is not the index it would "
                       f"write to; NOTHING was written\n"
                       f"next: close the fence in {cid}, then add check {slug} <n>")

    boxes = _box_lines(body, section)
    if not boxes:
        return None, (f"{cid} carries no checkbox in {where} — nothing to check\n"
                       f"next: add a `- [ ] <criterion>` line first, or check a node that has one")

    listing = "\n".join(f"  {n}. [{'x' if m else ' '}] {text}"
                        for n, (_, m, text, _s) in enumerate(boxes, 1))
    if not indices:
        return None, (f"add check needs an index — {cid} has {len(boxes)} boxes in {where}:\n"
                       f"{listing}\nnext: add check {slug} <n> [<n> …]   (or --all)")

    bad = [n for n in indices if not 1 <= n <= len(boxes)]
    if bad:
        return None, (f"no box {', '.join(str(n) for n in sorted(set(bad)))} in {cid} — "
                       f"it has {len(boxes)} in {where}; NOTHING was written:\n{listing}\n"
                       f"next: add check {slug} <n> with an index in 1..{len(boxes)}")

    # The goal-gate closed on `- [x] <criterion>   (← <task>)` — unauthored scaffold, credited to
    # a named human (2026-08-28 review). The engine has owned a placeholder detector all along and
    # never pointed it at the one gate loop.md calls "the only release".
    if not off:
        template = [(n, boxes[n - 1][2]) for n in sorted(set(indices))
                    if 1 <= n <= len(boxes) and PLACEHOLDER.search(boxes[n - 1][2])]
        if template:
            listed_t = "\n".join(f"  {n}. {text}" for n, text in template)
            return None, (f"box {', '.join(str(n) for n, _ in template)} in {cid} is still "
                           f"template text — checking it would release the gate on an unauthored "
                           f"criterion:\n{listed_t}\n"
                           f"next: author the criterion, then add check {slug} <n>")

    # A moved criterion retains its original obligation. Its index remains visible, but
    # neither `check` nor `uncheck` may silently turn that transfer into an ordinary box.
    moved_indices = [n for n in sorted(set(indices))
                     if BOX.match(body.splitlines()[boxes[n - 1][0]]).group(1) == "~"]
    if moved_indices:
        return None, (f"cannot check moved box {', '.join(map(str, moved_indices))} in {cid} "
                      f"— `[~]` retains its original obligation; NOTHING was written\n"
                      f"next: repair its `moves-to:` and destination `accepts:`, then "
                      f"add milestone-done {slug}")

    want, lines, moved = not off, body.splitlines(keepends=True), []
    for n in sorted(set(indices)):
        i, marked, text, where_box = boxes[n - 1]
        if marked == want:
            continue
        lines[i] = re.sub(r"\[[ xX]\]", "[x]" if want else "[ ]", lines[i], count=1)
        moved.append((n, text, where_box))

    verb = "marked" if want else "unmarked"
    if not moved:
        idle = sorted(set(indices))
        return True, (f"unchanged — box{'es' if len(idle) > 1 else ''} "
                      f"{', '.join(str(n) for n in idle)} in {cid} already {verb}\nnext: add status")

    stamp = (f'{{ by: "{_oneline(by or "process:check")}", at: {_today()}, '
             f'act: {"check" if want else "uncheck"}, '
             f'authority: {authority_for(scan(root), cid)}, '
             f'via: {via}, boxes: "{_stamp_boxes(moved)}" }}')
    raw = append_item(doc["raw"], "verified", stamp)
    write(path, f"---\n{raw}\n---\n" + "".join(lines))

    told = "\n".join(f"  {n}. [{'x' if want else ' '}] {text}" for n, text, _s in moved)
    return True, (f"{len(moved)} box{'es' if len(moved) > 1 else ''} {verb} in {cid} "
                  f"by {by or 'process:check'}:\n{told}\n"
                  f"next: add status")


def milestone_window_anchor(fm: dict):
    """The date a milestone's lesson window OPENS, or None when the engine cannot read one.

    The drafted contract said "`generated.at`, or the first `verified` stamp, whichever is
    earlier". The second clause is dead by construction and the probe says so: a node is created
    before it is stamped, so no stamp can precede creation. One source, and a `None` that means
    UNKNOWN — never today, never epoch (the `_as_date` rule).
    """
    gen = (fm or {}).get("generated")
    return _as_date(gen.get("at")) if isinstance(gen, dict) else None


EXIT_LOCATOR = re.compile(r"\A(/milestones/[A-Za-z0-9][A-Za-z0-9._-]*\.md)#EXIT:(C[1-9][0-9]*)\Z")
EXIT_ID = re.compile(r"\A(C[1-9][0-9]*)\b")


def _exit_link(text: str, name: str):
    """One exact parenthesized locator, or None when the author left it ambiguous."""
    links = re.findall(r"\(\s*" + re.escape(name) + r":\s*([^)]*)\)", text)
    return links[0].strip() if len(links) == 1 and text.count(name + ":") == 1 else None


def _resolve_exit_move(graph, source_cid: str, source_id: str, text: str, seen: set):
    """Follow an accepted move to a terminal criterion; return (reject code, reason)."""
    target = _exit_link(text, "moves-to")
    if target is None:
        return "R:ORPHAN_MOVE", "one exact `(moves-to: ...)` locator is required"
    parsed = EXIT_LOCATOR.fullmatch(target)
    if parsed is None:
        return "R:DANGLING_MOVE", f"invalid Milestone EXIT locator {target!r}"
    target_cid, target_id = parsed.groups()
    key = (target_cid, target_id)
    if key in seen:
        return "R:CYCLIC_MOVE", f"move revisits {target_cid}#EXIT:{target_id}"
    entry = graph.get(target_cid)
    if entry is None or (entry.get("fm") or {}).get("type") != "Milestone":
        return "R:DANGLING_MOVE", f"target {target_cid} is not a real Milestone"
    target_doc = read(entry["path"], "T2")
    target_exit = _section_of(target_doc["body"], "EXIT")
    if not _fence_balanced(target_exit):
        return "R:DANGLING_MOVE", f"target {target_cid} has an unreadable EXIT section"
    boxes = _box_lines(target_exit)
    matches = [(i, criterion) for i, _marked, criterion, _section in boxes
               if (m := EXIT_ID.match(criterion)) and m.group(1) == target_id]
    if len(matches) != 1:
        return "R:DANGLING_MOVE", f"target {target_cid}#EXIT:{target_id} is absent or ambiguous"
    i, criterion = matches[0]
    if _exit_link(criterion, "accepts") != f"{source_cid}#EXIT:{source_id}":
        return "R:REJECTED_MOVE", f"target {target_cid}#EXIT:{target_id} has no reciprocal acceptance"
    stamps = (entry.get("fm") or {}).get("verified") or []
    latest = next((s for s in reversed(stamps) if isinstance(s, dict)
                   and s.get("act") in ("freeze", "refreeze")), None)
    if not latest or latest.get("exit") != exit_digest(target_doc):
        return "R:REJECTED_MOVE", f"target {target_cid}#EXIT:{target_id} has no current EXIT-bound freeze"
    state = BOX.match(target_exit.splitlines()[i]).group(1)
    if state == "~":
        return _resolve_exit_move(graph, target_cid, target_id, criterion, seen | {key})
    return "", ""


def milestone_done(root, cid: str) -> tuple:
    """Close a milestone — but only when its GOAL is met (loop.md's goal-gate).

    A milestone is done when its `## EXIT` criteria are all checked, not when its tasks are.
    The engine reads the `- [x]`/`- [ ]` tally; it never judges the goal — checking the last box
    is the human's single affirmation. Refusing an unmet close is the notary's duty (law 3): a
    human may still write `status: done` by hand with their own authority.
    """
    root = Path(root)
    graph = scan(root)
    node = graph.get(cid)
    if node is None:
        return None, f"no such node: {cid}\nnext: add status"
    if (node["fm"] or {}).get("type") != "Milestone":
        return None, (f"{cid} is not a Milestone — milestone-done closes milestones only\n"
                       f"next: add done <task>  (for a task)")

    slug = cid.rsplit("/", 1)[-1][:-3]
    body = read(node["path"], "T2")["body"]

    # The why-gate (required on milestones): a milestone must state WHY it exists before it closes.
    # An unfilled `<placeholder>` why: is not rationale — refuse it exactly as the goal-gate refuses
    # an unchecked box. `why:` is optional on tasks, so only milestone_done enforces it.
    card = _section(body, "card")
    m = re.search(r"(?mi)^\s*why:\s*(.*)$", card)
    why = (m.group(1).strip() if m else "")
    if not why or PLACEHOLDER.search(why):
        return None, (f"milestone_why_unset — {cid}'s CARD `why:` is still a placeholder\n"
                       f"next: state why {slug} exists in its CARD `why:`, then add milestone-done {slug}")

    exit_body = _section_of(body, "EXIT")
    if not _fence_balanced(exit_body):
        return None, (f"milestone_exit_unreadable — {cid}'s `## EXIT` has an unclosed code fence, "
                       f"so the goal-gate cannot tally its boxes; it does not close on an input it "
                       f"cannot read\nnext: close the fence in {slug}'s `## EXIT`, "
                       f"then add milestone-done {slug}")
    boxes = _box_lines(exit_body)
    lines = exit_body.splitlines()
    moved = [(i, text) for i, _marked, text, _section in boxes
             if BOX.match(lines[i]).group(1) == "~"]
    checked, total = sum(marked for _, marked, _, _ in boxes), len(boxes)
    for i, text in moved:
        ident = EXIT_ID.match(text)
        source_id = ident.group(1) if ident else "C?"
        if ident is None or sum(bool((m := EXIT_ID.match(t)) and m.group(1) == source_id)
                                for _j, _marked, t, _section in boxes) != 1:
            code, reason = "R:ORPHAN_MOVE", "source EXIT identity is absent or duplicated"
        else:
            code, reason = _resolve_exit_move(graph, cid, source_id, text, {(cid, source_id)})
        if code:
            return None, (f"{code} — {cid}#EXIT:{source_id}: {reason}; "
                          f"original tally {checked}/{total}, moved {len(moved)}\n"
                          f"next: repair EXIT {source_id}'s move and accepted destination, "
                          f"then add milestone-done {slug}")

    unchecked = total - checked - len(moved)
    if unchecked:
        return None, (f"milestone_goal_unmet ({checked}/{total} exit criteria)\n"
                       f"next: check the remaining boxes in {cid.lstrip('/')}, then "
                       f"add milestone-done {slug}")

    if (node.get("fm") or {}).get("status") == "done":
        moved_note = (f", moved {len(moved)} ({', '.join(EXIT_ID.match(t).group(1) for _i, t in moved)})"
                      if moved else "")
        return True, (f"{cid} already done ({checked}/{total} exit criteria met{moved_note}) "
                      f"— historical closure unchanged\nnext: add status")

    # The MEMBERS, before the lesson drain: a milestone that closes on its exit criteria while
    # still holding unauthored tasks abandons them, and until now said nothing at all. That is
    # where a graveyard comes from — nobody decides to abandon forty tasks, a milestone just
    # closes and they stop being anybody's -> "R:SILENTABANDON".
    #
    # Three exits, all named (A6). A refusal offering one fix does not present a choice, it
    # applies pressure: name only `drop` and authors drop work they meant to keep.
    left = sorted(c for c, n in graph.items()
                  if (n["fm"] or {}).get("type") == "Task"
                  and str((n["fm"] or {}).get("milestone") or "").strip() == slug
                  and (n["fm"] or {}).get("status") not in ("done", "dropped", "archived")
                  and _is_scaffold(n))
    if left:
        named = "\n".join(f"  · {c.rsplit('/', 1)[-1][:-3]}" for c in left)
        return None, (f'milestone_members_unauthored ({len(left)} never authored) '
                       f'-> "R:SILENTABANDON"\n{named}\n'
                       f'next: for each — author it (add freeze <slug>), drop it '
                       f'(add drop <slug> --reason "<why>"), or re-home it under a live '
                       f'milestone — then add milestone-done {slug}')

    # The drain, LAST (M7): a closer whose goal is still unmet must be told that first, not
    # sent to consolidate lessons for a milestone that is not finished.
    #
    # WINDOWED, and that is the whole design. A rung over every open delta would have met this
    # repo with a 75-lesson backlog and blocked every close until someone drained eighteen
    # milestones of residue in one sitting — so the rung would have been deleted, not obeyed
    # (M22's shape). A milestone is answerable for the lessons IT filed; the backlog stays a
    # `doctor` finding and a `status` count, which is what those exist for.
    anchor, skipped = milestone_window_anchor(node["fm"]), ""
    if anchor is None:
        # R:SILENTSKIP — a close that looks drained and was not is worse than one that admits
        # it could not check. Never guess a date to make the rung fire.
        skipped = (" — the drain rung did not run: this milestone carries no readable creation "
                   "date, so the window its lessons would fall in cannot be computed")
    else:
        # An undated legacy delta has no filing date to place, so it is never in any window
        # (A8, R:BACKLOGBLOCK). Inclusive on the anchor: created and taught on one day is the
        # common case (A6).
        undrained = [d for d in deltas(root, status="open")[0]
                     if _as_date(d.valid_from) and d.valid_from >= anchor]
        if undrained:
            # `Delta` is a 3-tuple by design (spec, comp, text) with the rest riding as
            # attributes — four suites unpack exactly three, so it has no `.lens`/`.text`.
            named = "\n".join(f"  · {delta_address(d[0], d.id)}  {d[2].split(' (evidence:')[0][:88]}"
                              for d in undrained)
            return None, (f'milestone_deltas_undrained ({len(undrained)} filed on or after '
                           f'{anchor}) -> "R:UNDRAINED"\n{named}\n'
                           f'next: resolve each — add fold <lens> "<match>" '
                           f'[--reject | --bind "<the decision it settles>"] — '
                           f'then add milestone-done {slug}')

    _transition(root, cid, sets={"status": "done"})
    # 0 criteria => the goal-gate never fires (loop.md); close, but say the gate was empty.
    empty = "" if total else " — no exit criteria, so the goal-gate did not fire (add criteria to hold one open)"
    # `check` does not defend the goal-gate (2026-08-28), so the close line carries the audit
    # instead: WHO left the boxes marked. No `act: check` stamp means the boxes were hand-edited,
    # which is the honest reading — never a guessed name.
    seen, who = set(), []
    for entry in ((node["fm"] or {}).get("verified") or []):
        if isinstance(entry, dict) and str(entry.get("act")) == "check":
            name = str(entry.get("by") or "process:check")
            # `--by` is free text, so the NAME proves nothing. What it was typed at does:
            # `via: tty` is a person at a terminal, anything else is a process claiming one.
            if str(entry.get("via") or "process") != "tty":
                name += " (unattended)"
            if name not in seen:
                seen.add(name)
                who.append(name)
    credit = f", checked by {', '.join(who)}" if who else ", checked by hand (unstamped)"
    transfer = (f", moved {len(moved)} ({', '.join(EXIT_ID.match(t).group(1) for _i, t in moved)})"
                if moved else "")
    return True, (f"{cid} milestone done ({checked}/{total} exit criteria met{transfer}{credit})"
                  f"{empty}{skipped}\nnext: add status")


def drop(root, cid: str, reason: str) -> tuple:
    """Withdraw a task from the plan: `status: dropped`, with the reason on the record.

    `dropped` was a word the engine READ in three places and no verb could WRITE — vocabulary
    living only in the reader -> "R:DEADWORD". Withdrawing work was therefore something you did
    by deleting a file or by leaving it to rot as a scaffold, and neither leaves a reason behind.

    The reason is required for the same purpose the whole task serves: a task dropped without one
    is the silent abandonment this prevents, merely relocated into a status field (A9). A `done`
    task is refused — that verdict was recorded against a receipt, and the verb for revisiting it
    is `reopen`, which resets the gate rather than overwriting it (A10).
    """
    root = Path(root)
    graph = scan(root)
    node = graph.get(cid)
    if node is None:
        return None, f"no such node: {cid}\nnext: add status"
    fm = node["fm"] or {}
    node_type = fm.get("type")
    if node_type not in LIFECYCLE_TYPES:
        return None, (f'only a lifecycle node can be dropped — `{cid}` is a {node_type}, which '
                       f'has no plan to be withdrawn from -> "R:NOTATASK"\nnext: add status')
    if fm.get("status") == "done":
        return None, (f"`{cid}` is done — a gate recorded that verdict against a receipt, and "
                       f"`drop` would overwrite it with a planning note\n"
                       f"next: add reopen {cid.rsplit('/', 1)[-1][:-3]} --to <beat> --reason "
                       f'"<why>"   # revisits a done task without erasing its gate')
    slug = cid.rsplit("/", 1)[-1][:-3]
    if fm.get("status") == "dropped":
        return None, f"`{slug}` is already dropped\nnext: add status"
    # A stamp is a pre-formatted ABF flow-map STRING, not a dict — `reopen` learned this the
    # hard way; a dict serialises as Python and no reader parses it back.
    stamp = f'{{ by: loop, at: {_today()}, act: drop, reason: "{reason}" }}'
    _transition(root, cid, sets={"status": "dropped"}, appends=[("verified", stamp)])
    return True, (f"`{slug}` dropped — {reason}\n"
                  f"next: add status   # it leaves the worklist; the reason stays on the node")


def milestone_archive(root, cid: str) -> tuple:
    """Retire a done milestone (status → `archived`). Refuses one not done (loop.md).

    `milestone-done` is the only path to `done`; this is the only path past it, and it refuses to
    shelve a milestone whose goal-gate never closed — there is no quiet way around the goal-gate.
    """
    root = Path(root)
    node = scan(root).get(cid)
    if node is None:
        return None, f"no such node: {cid}\nnext: add status"
    fm = node["fm"] or {}
    slug = cid.rsplit("/", 1)[-1][:-3]
    if fm.get("type") != "Milestone":
        return None, f"{cid} is not a Milestone — archive retires milestones only\nnext: add status"
    if fm.get("status") != "done":
        return None, (f"cannot archive — {cid} is `{fm.get('status')}`, not done "
                       f"(close it first: add milestone-done {slug})\nnext: add status")
    _transition(root, cid, sets={"status": "archived"})
    return True, f"{cid} archived\nnext: add status"


# ================================================ status — orientation and its flags (e6)
#
# Everything here reads e2's compiled graph; no verb walks the tree. Three rules bind:
#
# * **Bounded, always** (A12). Output must not grow with the bundle: 20 node lines and a
#   count. A report that becomes a context hazard defeats the format it reports on.
# * **Report, never block** (law 3). The one write here is `render_card`, and it repairs
#   the contradiction e4's transition created rather than displaying it as current.

MAX_LINES = 20
# One row is one line at this width. 100 is the narrowest terminal orientation is expected to
# survive; a wrapped row stops being a row, because the columns after the wrap are not columns.
ROW_WIDTH, SLUG_W = 100, 28
# The widest beat word plus its brackets (`[abandoned]`), so the type column lines up whatever
# the beat is.
BEAT_W = 11
TITLE_FLOOR = 12   # the least a title keeps when a release tag shares its row
BEAT_KEYS = ("beat", "state")
# The one canonical next verb per beat — read by `status`'s frontier hint and `render_card`, so a
# repaired CARD's `next:` matches its beat instead of freezing at the direction-time affordance.
# The authoring beat has NO VERB by design — `direction.md`: "There is no author verb — you fill
# those sections by editing that file directly". So its advice names the WORK and the verb that
# follows it, matching `freeze`'s own refusal sentence word for word, and still carries a runnable
# `add …` continuation so an agent matching on a leading verb keeps a cue (A1).
AUTHOR_NEXT = {
    "Task": "author {slug}'s RULES, ASSUMPTIONS and CHECKS, then add freeze {slug}",
    "Milestone": "author {slug}'s goal, why and EXIT criteria, then add freeze {slug}",
}
# Every `next:` line the engine prints for a beat comes from here, so a wrong idiom here is
# wrong in fourteen places. `build` carried `add run {slug} -- <cmd>`, which yields a receipt
# with `ids: unknown`; a builder who obeyed it then met "no reported passing check" on work that
# was genuinely green, with RISK-ACCEPTED named as the only exit. `verify` carried `add gate
# {slug}`, which is an argparse error — a crash, not a refusal, with nothing to recover from.
# The path appears TWICE on purpose: `run` READS it, the test command WRITES it.
BEAT_NEXT = {"scaffold": AUTHOR_NEXT["Task"], "direction": "add freeze {slug}",
             # braces DOUBLED: both consumers pass this through `.format(slug=…)`, and
             # `${TMPDIR:-/tmp}` would otherwise be read as a format field and raise KeyError.
             # `<test cmd>` is the one slot a NOTARY cannot fill from the bundle — but it need
             # not guess: `run` is handed the real command every time it is called, and now
             # remembers the last one on `index.md`. Until the first run this stays a template;
             # after it, the hint replays that Task's own Run computation at T0.
             "build": ('add run {slug} -- <test cmd> '
                       '--junitxml="${{TMPDIR:-/tmp}}/add-run.xml"'),
             "verify": 'add gate {slug} PASS --by "<name>"', "done": "add status"}
BEAT_NAMES = ("scaffold", "queued", "abandoned", "adrift",
              "direction", "build", "verify", "done")
# What a cold reader needs, in order. `Run` is absent on purpose — see `status`.
ORIENT_RANK = {"Project": 0, "Milestone": 1, "Task": 2, "Spec": 5, "Persona": 6, "Prompt": 7}

# Orientation sorts by how close the work is to needing a HUMAN, never by node type. Ranking by
# type put an archived milestone above every open task, so the one work row on a finished bundle
# was its deadest node while 112 others were withheld. An unrecognised beat sorts FIRST: the
# engine does not know what it is, which is precisely when a person should look.
ATTENTION_RANK = {"verify": 1, "build": 2, "direction": 3,
                  "queued": 4, "abandoned": 5, "adrift": 6, "scaffold": 4}
ANSWERED = ("done", "dropped", "archived")


def _is_frozen(node) -> bool:
    """True once a task carries a freeze/refreeze stamp — the signal that authoring is done and the
    frontier hint should point at `brief` (build), not `freeze`. Status stays `direction` until done,
    so the beat is stamp-derived, not read from the status field."""
    stamps = (node.get("fm") or {}).get("verified") or []
    return any(isinstance(s, dict) and s.get("act") in ("freeze", "refreeze") for s in stamps)


def _milestone_stubs(node: dict) -> list:
    """The Milestone fields still template, among the three the lifecycle actually reads.

    Deliberately narrower than the Task guard (decided 2026-09-01). `milestone_done` already
    refuses on `why:` and on the `## EXIT` tally, so goal · why · EXIT are what the milestone
    lifecycle depends on. A guard reaching SCOPE and GROUND too would refuse real milestones
    whose ground is thin, and a guard everyone learns to widen past is worse than a narrow one
    that holds.
    """
    body = node.get("body") or ""
    out = []
    for line in card_of(body).splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() in ("goal", "why") and is_slot(value):
            out.append(f"CARD `{key.strip()}:`")
    exit_body = _section_of(body, "EXIT")
    boxes = _box_lines(exit_body) if _fence_balanced(exit_body) else []
    if not boxes or any(is_slot(text) for _, _, text, _ in boxes):
        out.append("`## EXIT` criteria")
    return out


def _is_scaffold(node, t2=None) -> bool:
    """True for a node that was created and never authored. ONE definition, two tiers.

    Calls the SAME predicates the refusals call — `gives_unauthored` at T0, `placeholders_in`
    (or `_milestone_stubs`) at T2 — never a copy of them (R:SECOND_TRUTH). Two notions of
    "authored" is exactly how advice and refusal came to disagree, which is the defect one
    layer up.

    The T2 half runs ONLY when the caller already holds the body. `status` must not read a
    single body — that is `build-orient`'s R:T2SCAN, a Reject frozen before this task existed
    and not this task's to weaken — so it gets the T0 answer, while `freeze` and `todo`, which
    both already read the body for their own reasons, get the complete one. The tiers cannot
    disagree in DIRECTION: T0 saying scaffold is always right, and the T2 half only ever adds.

    Residual, recorded rather than hidden: a node with an authored `gives:` but still-template
    RULES reads authored to `status` alone. `todo` and `freeze` both catch it.

    A freeze stamp WINS over any placeholder: a pre-3.0 bundle can carry both, and dragging an
    approved node back into authoring advice would undo an approval that was actually given (A9).
    An unreadable body advises authoring — the conservative direction, since the alternative is
    to recommend a verb whose refusal is the author's first news of the problem (A7).
    """
    if _is_frozen(node):
        return False
    fm = node.get("fm") or {}
    if fm.get("type") not in LIFECYCLE_TYPES:
        return False
    if fm.get("type") == "Task" and gives_unauthored(node):
        return True                      # T0, and enough on its own
    if t2 is None:
        return False                     # the caller holds no body — T0 is the whole answer
    if fm.get("type") == "Milestone":
        return bool(_milestone_stubs(t2))
    return bool(placeholders_in(t2))


def replan(root, cid: str, note: str, by: str = "builder") -> tuple:
    """Record a steering amendment on a frozen task — one additive act stamp, the seal untouched.

    Steering = a change to NO frozen surface (strategy, sequencing, a discovered constraint).
    Anything that would move a frozen `gives:` or a check is a change-request (refreeze), never
    a replan. Refusals: unfrozen (nothing is being steered), blank note (invisible steering),
    done (the trail is closed — the note belongs in LESSONS). R:SILENT_STEER · R:SEAL_TOUCH.
    """
    root = Path(root)
    graph = scan(root)
    node = graph.get(cid)
    if node is None:
        return None, f"no such node: {cid}\nnext: add status"
    slug = cid.rsplit("/", 1)[-1][:-3]
    fm = node.get("fm") or {}
    if fm.get("status") == "done":
        return None, (f"`{slug}` is done — its trail is closed; the note belongs in LESSONS "
                      f'(add learn <dd> "<note>" --evidence {cid})\nnext: add status')
    if not _is_frozen(node):
        return None, (f'nothing is being steered — `{slug}` carries no freeze -> "R:SILENT_STEER"'
                      f'\nnext: author the direction, then add freeze {slug} --by "<name>"')
    if not (note or "").strip():
        return None, ('a replan with no note is invisible steering -> "R:SILENT_STEER"'
                      f'\nnext: add replan {slug} --note "<what changed and why>"')
    # One physical line, always: the stamp lives in a single-line frontmatter entry, so a
    # newline in the note would split it mid-map and take the node's whole trail with it.
    text = " ".join(str(note).split()).replace('"', "'")
    _, err = _transition(root, cid, appends=[
        ("verified", f'{{ by: "{_oneline(by)}", at: {_today()}, act: replan, authority: process, '
                     f'note: "{text}" }}')])
    if err:
        return None, err + "\nnext: add status"
    return cid, (f"replan recorded on `{slug}` — steering noted, the seal untouched"
                 f"\nnext: keep building (`add run {slug} -- <cmd>` when green)")


def card_drift(graph: dict, body_of=None) -> list:
    """Nodes whose `## CARD` contradicts frontmatter — the defect e4's transition created.

    `[(cid, key, card_says, fm_says)]`. Reporting it is the notary's job; `render_card`
    repairs it.

    `body_of` is an optional reader a CALLER that is already walking the same nodes can pass
    so the body is read once rather than twice — `doctor` does. Absent, this reads for itself
    and behaves exactly as before, so the other three callers are unaffected.
    """
    read_body = body_of if body_of is not None else (lambda path: read(path, "T2")["body"])
    out = []
    for cid, node in graph.items():
        if not (node["fm"] or {}).get("status"):
            continue
        # The DERIVED beat, never the raw `status:` field. `freeze` does not move `status:`, so a
        # freshly frozen node advertised `next: add freeze <slug>` — the approval it had just
        # passed — while `todo` and `status` derived `build`, and this reported it CLEAN
        # (2026-08-17 replan, A5 falsified). Two notions of beat, read by different surfaces.
        # The graph goes in for the same reason: `doctor` saying `scaffold` where `status` says
        # `queued` is exactly the second vocabulary M5 exists to prevent.
        beat = _beat_of(node, None, graph)
        card = card_of(read_body(node["path"]))
        for line in card.splitlines():
            key, sep, value = line.partition(":")
            if sep and key.strip() in BEAT_KEYS:
                said = value.split("·")[0].strip()
                if said and said != beat and said in BEAT_NAMES:
                    out.append((cid, key.strip(), said, beat))
    return out


def render_card(root, cid: str) -> tuple:
    """Repair a stale CARD beat line. Surgical: exactly one line changes, or none."""
    graph = scan(root)
    drift = [d for d in card_drift(graph) if d[0] == cid]
    if not drift:
        return False, "card is current"
    _, key, said, status = drift[0]
    path = Path(root) / cid.lstrip("/")
    slug = cid.rsplit("/", 1)[-1][:-3]
    node = read(path, "T2")
    lines = node["body"].splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith(f"{key}:") and said in line:
            # Rebuild the WHOLE beat line, not just the token: the `next:` on it froze at the
            # direction-time affordance, so a done card kept reading `next: add freeze`. Through
            # `_next_verb`, not BEAT_NEXT directly — that is the one map every other surface
            # resolves through, and it alone knows a sealed-but-unbriefed task owes `add brief`
            # before its run (R:UNBRIEFED). Reading the map raw put a third answer on the CARD.
            # Still exactly one line changes (idempotence holds).
            nxt = _next_verb(graph, cid)
            lines[i] = f"{key}: {status} · next: {nxt}\n"
            break
    write(path, f"---\n{node['raw']}\n---\n{''.join(lines)}")
    return True, f"{cid}: {key} {said} -> {status}\nnext: add status"


def tooling_drift(root, graph: dict = None):
    """A warning when the vendored engine is stale, else `None`. The version is the unit of record.

    `init` stamps `tooling_engine:` at the version it vendored; a newer engine running against that
    bundle no longer matches. Compare the recorded string against the running `ENGINE`. A bundle that
    records nothing (never vendored) cannot drift (R:NODRIFT). `graph` may be supplied to avoid a
    second scan. A same-version hand-patch reads as fresh — accepted; the version is the unit.
    """
    graph = scan(root) if graph is None else graph
    recorded = ((graph.get("/index.md") or {}).get("fm") or {}).get("tooling_engine")
    if not recorded or str(recorded) == ENGINE:
        return None
    return (f"vendored engine {recorded} is stale — running {ENGINE} "
            f"(run `add doctor --sync` to refresh `.add/tooling/`)")


def _scope_matches(entry: str, query: str) -> bool:
    """A scope entry matches a query path when they are equal or one is a directory-prefix of
    the other — `src/` matches `src/a.py`, and `src/a.py` matches `src/`."""
    a, b = str(entry).rstrip("/"), str(query).rstrip("/")
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def locate(root, query: str, all: bool = False) -> tuple:
    """Reverse lookup: every node whose `scope:` matches `query` (equal or dir-prefix). Read-only.

    Answers "which node owns this path?" — the everyday navigation `status` cannot. A pure read over
    the graph: `(hits, note)` where `hits` is `[(cid, status, matched_scope_entry), …]`. It never writes.

    `hits` is ALWAYS complete; `all` widens only the rendered note. Measured on the live bundle,
    `add-method/tooling/add.py` had 50 owners of which 48 were `done` — 93% of the answer was a
    list of nodes that had already shipped. The question "who owns this file" is answered by the
    ones still open, so the closed ones are counted and `--all` names itself as the way back
    (M3 · M4 · R:NOWAYBACK). Only `done` collapses: an archived or reopened node is not settled.
    """
    graph = scan(Path(root))
    # The FLOOR first, because the floor is checked FIRST and always wins (A5/A11) and this is the
    # one PRE-EDIT step the direct lane runs — S2's whole promise is that it fires "while changing
    # course is still free". Reading `scope:` alone answered `no node scopes …` for a path the
    # bundle had declared sensitive: a false all-clear on the security half, from the step meant to
    # prevent the very refusal `learn` would hand back after the commit. Same patterns, same
    # matcher as `quick_hit` and A17 — one reader, never a second copy of the rule.
    patterns = ((graph.get("/index.md", {}).get("fm") or {}).get("sensitive_paths")) or []
    floor = next((str(pat) for pat in (patterns if isinstance(patterns, list) else [patterns])
                  if _paths_touch(str(query), str(pat))), None)
    lede = (f"`{query}` matches the sensitive pattern `{floor}` — floor human; a change here is a "
            f"node, however small\n" if floor else "")
    hits = []
    for cid, node in sorted(graph.items()):
        fm = node["fm"] or {}
        scope = _scope_list(fm)
        for entry in (scope if isinstance(scope, list) else [scope]):
            if _scope_matches(entry, query):
                hits.append((cid, fm.get("status", "—"), str(entry)))
                break
    if not hits:
        return [], lede + f"no node scopes `{query}`\nnext: add status"
    listed = hits if all else [h for h in hits if h[1] != "done"]
    closed = len(hits) - len(listed)
    parts = [lede + f"{len(hits)} node(s) scope `{query}`:"]
    parts += [f"  · {cid.rsplit('/', 1)[-1][:-3]:<28} [{st}]  ({entry})" for cid, st, entry in listed]
    if closed:
        parts.append(f"  … {closed} done owner(s) not listed (`--all`)")
    return hits, "\n".join(parts) + "\nnext: add status"


# The node types that HAVE a beat. Every other type (Spec · Persona · Project · Run)
# carries a status that is not a beat, and orientation prints it unchanged (M4).
BEAT_TYPES = ("Task", "Milestone")


SCAFFOLD_KINDS = ("queued", "abandoned", "adrift")
# A milestone in either of these states has stopped queueing anything. `archived` is what happens
# to a milestone AFTER it is done, so a task the plan left behind is abandoned under both.
CLOSED_MILESTONE = ("done", "archived")


def _scaffold_kind(graph: dict, node: dict) -> str:
    """Which of `queued · abandoned · adrift` an UNAUTHORED task is — derived, never stored.

    3.6.0 made a 40-node roadmap legible; every row carried its title and the headline counted the
    unauthored ones. It still could not answer what a reviewer actually asks — is this a queue or a
    graveyard? A task the plan is working toward and one the plan walked away from both read
    `scaffold`.

    The plan that queued a task IS its milestone, so the answer is already on disk in two places
    that cannot disagree: the task's `milestone:` and that milestone's `status:`. Storing a third
    copy would be a field that drifts out of step with the milestone it describes -> "R:NEWFIELD".

    A `milestone:` naming nothing is `adrift`, exactly like no milestone at all: in both cases no
    plan that exists claims this task, and a read verb must not raise on a typo (A4).
    """
    slug = str((node.get("fm") or {}).get("milestone") or "").strip()
    if not slug:
        return "adrift"
    owner = graph.get(f"/milestones/{slug}.md")
    if owner is None:
        return "adrift"
    return "abandoned" if (owner["fm"] or {}).get("status") in CLOSED_MILESTONE else "queued"


def _beat_of(node, t2=None, graph=None) -> str:
    """A task's beat, DERIVED from its stamps — the same reasoning as `_is_frozen`.

    `status` runs `direction → done`: nothing in `freeze`/`run` advances it, so the field cannot
    tell direction from build from verify. Reading it made every open task report `direction`.
    An explicit active status wins, because that is `reopen` naming a beat deliberately.
    """
    fm = node.get("fm") or {}
    st = fm.get("status")
    if st in ("done", "dropped", "archived") or st in ("build", "verify"):
        return st
    stamps = [s for s in (fm.get("verified") or []) if isinstance(s, dict)]
    # A floor stamp (`floor: regression`) never closes the build beat: the narrow run is the
    # receipt that binds CHECKS, and a floor-first run read as `verify` made `status` point at
    # the gate with no narrow receipt at all (found by the second T2 refute of regression-floor,
    # R:FLOORASGATE, E9) — the same filter `_latest_run_cid` and `latest_receipt` apply.
    if any(s.get("act") == "run" and not s.get("floor") for s in stamps):
        return "verify"
    if _is_frozen(node):
        return "build"
    if not _is_scaffold(node, t2):
        return "direction"
    # An unauthored task answers WHICH plan wants it. Every surface that already renders a beat
    # inherits the word with no per-surface edit; a caller with no graph to hand still gets the
    # old vocabulary rather than a wrong provenance.
    return _scaffold_kind(graph, node) if graph is not None else "scaffold"


def _brief_entered(stamps: list, receipt_cid: str = None) -> bool:
    """True when an `act: brief` stamp sits after the last (re)freeze — and, when
    `receipt_cid` names a run stamp, before that run.

    `verified:` is append-only (§3.5), so list order IS chronology — no clock needed.
    A brief recorded before the freeze entered a direction that no longer exists, and a
    brief recorded after the receipt entered nothing: the build it claims was already over.
    """
    stamps = [s for s in stamps if isinstance(s, dict)]
    last_freeze = max((i for i, s in enumerate(stamps)
                       if s.get("act") in ("freeze", "refreeze")), default=-1)
    run_idx = next((i for i, s in enumerate(stamps)
                    if s.get("act") == "run" and str(s.get("receipt", "")) == receipt_cid),
                   None) if receipt_cid else None
    return any(s.get("act") == "brief" and i > last_freeze
               and (run_idx is None or i < run_idx)
               for i, s in enumerate(stamps))


def _refute_of(stamps: list, receipt_cid: str):
    """The outcome of the LATEST `act: refute` stamp citing `receipt_cid`, or None when no stamp does.

    A refute names the receipt it read (FORMAT §8.4), so "after the gated run" is decided by the
    citation, not by a clock: a refute of an earlier green entered nothing for this one, and a
    stamp with no `receipt:` cites nothing. Reads presence and outcome only — never `probes:`, the
    note, or who signed (law 3: a notary that judged a probe would be a guard).
    """
    outcome, tier = None, None
    for s in stamps:
        if isinstance(s, dict) and s.get("act") == "refute" \
                and receipt_cid and str(s.get("receipt", "")) == receipt_cid:
            # The tier travels WITH the outcome, from the same stamp, so the gate cannot read one
            # read's verdict beside another's independence claim. It is a CLAIM and stays one:
            # never `by:`, never `probes:`, never the note, never who signs the gate — an engine
            # that compared names would be judging an identity it cannot verify (R:TIERJUDGED).
            outcome, tier = str(s.get("outcome") or ""), (str(s.get("tier")) if s.get("tier") else None)
    return outcome, tier


def _latest_run_cid(stamps: list):
    """The receipt cid of the newest NARROW `act: run` stamp, or None — read from the record, not the disk.

    A floor stamp (`floor: regression`) is skipped, exactly as `latest_receipt` skips the floor
    receipt: the T2 refute of regression-floor found this reader taking the floor as the latest
    run, so the hint demanded a refute the gate never asked for (R:FLOORASGATE, E7).
    """
    return next((str(s.get("receipt") or "") for s in reversed(stamps)
                 if isinstance(s, dict) and s.get("act") == "run" and not s.get("floor")), None)


def _rung_bound(graph: dict, cid: str, fm: dict) -> bool:
    """Does the refute rung bind this node? standard|deep × computed floor plan|human × not explore."""
    return fm.get("type") == "Task" \
        and str(fm.get("depth") or "standard") != "quick" \
        and str(fm.get("kind") or "") != "explore" \
        and authority_for(graph, cid) in ("plan", "human")


FLOOR_LINE = re.compile(r"^regression:\s*(full|affected|none)\s*·\s*(.*)$", re.M)


def regression_floor(node: dict):
    """`{mode, cmd, why}` from the PLAN's `regression:` line (regression-floor), or None.

    `full | affected · <cmd> · <why>` or `none · <why>`. A template line (`<…>`), a mode with no
    command, or a `none` with no why is no floor — the freeze demands the decision, never the
    slot. `affected` is the AUTHOR's claim about the command: the engine records the word and
    runs what it is handed, and cannot tell a three-test run from a full one (FORMAT §8.5).
    """
    m = FLOOR_LINE.search(_section_of((node or {}).get("body") or "", "PLAN"))
    if not m:
        return None
    mode, rest = m.group(1), m.group(2).strip()
    if "<" in rest:
        return None
    if mode == "none":
        return {"mode": mode, "cmd": "", "why": rest} if rest else None
    cmd, _, why = rest.partition("·")
    cmd, why = cmd.strip(), why.strip()
    return {"mode": mode, "cmd": cmd, "why": why} if (cmd and why) else None


OBSERVE_ACTIONS = ("alert", "rollback")
# `- O<n> covers: <M ids> · signal <text> · window <text> · threshold <text> · action alert|rollback`
# The field ORDER is fixed (A5) so one regex reads every line and the brief prints them the same
# way; the three middle fields are free text (A2) — the engine names a slot, it cannot judge a
# metric. A line that does not match is not an observe: `doctor` names it, `observes` skips it.
OBSERVE_LINE = re.compile(
    r"^\s*-\s*(O\d+)\s+covers:\s*(?P<covers>[^·]+?)\s*·\s*signal\s*(?P<signal>[^·]+?)\s*·\s*"
    r"window\s*(?P<window>[^·]+?)\s*·\s*threshold\s*(?P<threshold>[^·]+?)\s*·\s*"
    r"action\s*(?P<action>\S+)\s*$")
OBSERVE_HEAD = re.compile(r"^\s*-\s*(O\d+)\b")


def observes(node: dict) -> list:
    """`[{id, covers, signal, window, threshold, action}]` for every well-formed observe in PLAN.

    The runtime signal that would show a Must broken — loop.md's "the CHECKS have a second life as
    monitors" given the slot it never had. NOTHING in the engine decides anything from these: a
    monitor's verdict is production's evidence, never the bundle's (R:OBSERVEASGATE). They ride
    `## PLAN`, which no digest seals, so writing one after a freeze is neither drift nor a re-cross.
    """
    out = []
    for line in live_lines(_section_of((node or {}).get("body") or "", "PLAN")):
        m = OBSERVE_LINE.match(str(line))
        if not m or PLACEHOLDER.search(re.sub(r"`[^`]*`", "", str(line))):
            continue
        if m.group("action") not in OBSERVE_ACTIONS:
            continue
        covers = [c.strip() for c in m.group("covers").replace(",", " ").split() if c.strip()]
        if not covers:
            continue
        out.append({"id": m.group(1), "covers": covers, "signal": m.group("signal").strip(),
                    "window": m.group("window").strip(), "threshold": m.group("threshold").strip(),
                    "action": m.group("action")})
    return out


def malformed_observes(node: dict) -> list:
    """`[(id, line)]` for every `- O<n>` line in PLAN that `observes` could not read.

    The other half of one question, asked HERE so the reader that skips and the finding that names
    can never disagree: a line nobody reads and nobody names is the slot silently not working.
    """
    good = {o["id"] for o in observes(node)}
    return [(m.group(1), str(line).strip())
            for line in live_lines(_section_of((node or {}).get("body") or "", "PLAN"))
            if (m := OBSERVE_HEAD.match(str(line))) and m.group(1) not in good]


def gives_digest(node: dict) -> str:
    """The digest over a node's canonical `gives:` list alone (consumers-go-stale, FORMAT §3.5)."""
    gives = (node.get("fm") or {}).get("gives") or []
    gives = [gives] if isinstance(gives, str) else gives           # a scalar is one surface (E15)
    return "sha256:" + hashlib.sha256(_canon("\n".join(str(g) for g in gives)).encode()).hexdigest()[:16]


def scope_seal_digest(node: dict) -> str:
    """Digest the authored `scope:` as a normalized set (scope-in-the-seal, FORMAT §3.5).

    Ordering and duplicate entries do not change what the node declares, so neither may force a
    human refreeze. Entry text remains otherwise exact: changing a path or pattern moves the seal.
    """
    entries = sorted({str(entry) for entry in _scope_list((node or {}).get("fm") or {})})
    payload = json.dumps(entries, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()[:16]


def _latest_scope_seal(node: dict):
    """Latest freeze-class stamp iff it seals this node's current `scope:`; else None.

    Missing, malformed and stale scope seals all fail closed. Only the latest freeze-class stamp
    can authorize current scope; an older matching freeze cannot outrank a later refreeze.
    """
    stamps = (node.get("fm") or {}).get("verified") or []
    latest = next((stamp for stamp in reversed(stamps)
                   if isinstance(stamp, dict) and stamp.get("act") in ("freeze", "refreeze")), None)
    if latest is None:
        return None
    sealed = str(latest.get("scope") or "")
    if not re.fullmatch(r"sha256:[0-9a-f]{16}", sealed):
        return None
    return latest if sealed == scope_seal_digest(node) else None


def _short(digest: str) -> str:
    return str(digest or "").split(":")[-1][:8]


def stamped_gives(graph: dict, cid: str):
    """The `gives:` digest a node's latest (re)freeze stamp attests — None when no stamp carries one.

    This is the ONE unit every pin reader compares against (found by the fourth T2 refute): the
    live `gives:` list is a draft until a freeze seals it, so a provider not yet frozen, or frozen
    before the key existed, pins `?`, and a `gives:` edited without a refreeze moves nothing.
    """
    fm = (graph.get(cid) or {}).get("fm") or {}
    return next((str(x["gives"]) for x in reversed(fm.get("verified") or [])
                 if isinstance(x, dict) and x.get("act") in ("freeze", "refreeze") and x.get("gives")), None)


def _pins_of(graph: dict, cid: str) -> dict:
    """`{provider_cid: pinned8}` from the node's latest (re)freeze stamp — `?` pins and non-`#gives` dropped.

    Empty when the stamp carries no `needs:` key (written before the pin existed — answers
    nothing) or the node is not an open Task.
    """
    fm = (graph.get(cid) or {}).get("fm") or {}
    stamps = [x for x in (fm.get("verified") or []) if isinstance(x, dict) and x.get("act") in ("freeze", "refreeze")]
    if not stamps or "needs" not in stamps[-1] or not _open_task(graph, cid):
        return {}
    out = {}
    for entry in str(stamps[-1].get("needs") or "").split(","):
        # The pin is the text after the LAST `=`: a ref whose own text carried a delimiter was
        # pinned `?` by the writer, and that `?` must read back as `?` (found by the fifth T2
        # refute — `partition` on the first `=` read a pasted digest as attested).
        # … and only an exact `<ref>=<sha8|?>` token counts, `<ref>` carrying no `=` — the writer
        # stripped every delimiter from a ref it could not attest (E16), so any other shape is
        # text nobody stamped.
        m = re.fullmatch(r"([^=,\"'{}\[\]\s]*)=([0-9a-f]{8}|\?)", entry.strip())
        if m and m.group(2) != "?" and m.group(1).endswith("#gives"):
            out.setdefault(_norm(cid, m.group(1)), m.group(2))
    return out


# The pin's delimiters (`,` `=`), the stamp line's (`"` `'` `{` `}` `[` `]`) and whitespace: a ref
# carrying any of them cannot be attested, and is written with them stripped (E16, E17).
_PIN_UNSAFE = re.compile(r"""[,="'{}\[\]\s]""")


def needs_pins(graph: dict, cid: str) -> str:
    """`"<target>#gives=<sha8>[,…]"` — what a consumer froze on, or "" when it declares no `needs:`.

    Only a `#gives` fragment is a frozen contract; any other need (an explore's `#findings`, a
    bare file) is pinned `?` and never reported stale. A target the graph cannot resolve, or one
    with no freeze stamp attesting a `gives:` digest, is `?` too.
    """
    fm = (graph.get(cid) or {}).get("fm") or {}
    needs = fm.get("needs") or []
    out = []
    # Each distinct (resolved node, FRAGMENT) once, under its first-written spelling: a provider
    # named twice, or under two spellings `_norm` resolves alike, is one pair — decided in the
    # writer so no reader has to heal it (found by the second and third T2 refutes: M1, E7, E8).
    # The fragment is part of the key: `#findings` and `#gives` on one node are two pins, and a
    # delimiter-carrying spelling never shadows an honest one (sixth T2 refute, E14).
    seen = {}
    for ref in (str(r).strip() for r in (needs if isinstance(needs, list) else [needs])):
        node_key = _norm(cid, ref) if ".md" in ref else None
        key = (node_key, ref.partition("#")[2]) if node_key else ref
        seen.setdefault(key, ref)
    for ref in seen.values():
        target = _norm(cid, ref) if ".md" in ref else None
        # A ref carrying a pin delimiter (`,` or `=`) cannot be serialized, so it cannot be
        # attested: pinned `?` however it resolves (E13).
        serializable = not _PIN_UNSAFE.search(ref)
        attested = stamped_gives(graph, target) if serializable and ref.endswith("#gives") and target in graph else None
        # An unserializable ref is written with those characters STRIPPED, so no token in the
        # stamp string ever carries an inner `,` or `=` for a reader to split on (E16), nor a
        # `"` or `{` for the flow-map parser to trip on — the pin takes the discipline every
        # interpolated value takes through `_oneline` (E17, eighth T2 refute).
        out.append(f"{ref}={_short(attested)}" if attested else f"{_PIN_UNSAFE.sub('', ref)}=?")
    return ",".join(out)


def stale_needs(graph: dict, cid: str) -> list:
    """`[(provider_cid, pinned8, current8)]` — every `#gives` this node froze on that has since moved.

    Read from the node's latest (re)freeze stamp: a stamp with no `needs:` key was written before
    the pin existed and answers nothing (never a finding, never a refusal). Compared against the
    provider's STAMPED digest (`stamped_gives`), never its live list. Digests decide, never dates
    — two nodes' stamps are not one chronology (R:CLOCKPIN).
    """
    out = []
    for target, pinned in _pins_of(graph, cid).items():
        current = stamped_gives(graph, target)
        if current and _short(current) != pinned:
            out.append((target, pinned, _short(current)))
    # Sorted at the SOURCE, so every reader — doctor, todo, the gate — names each provider once,
    # in cid order; the pin's written order decides nothing (found by the T2 refutes: A5/E6 the
    # order, M3/E7 the unit — `_pins_of` keeps the first pin per resolved target).
    return sorted(out)


def consumers_of(graph: dict, cid: str) -> list:
    """Every open Task whose latest freeze stamp PINS this node's `#gives` — walked from the graph, never stored.

    Sourced from the stamp, like every other pin reader, never from the live `needs:` list: that
    list is unsealed and a draft until a freeze pins it, so the refreeze note and `doctor` name
    the same consumers whatever a hand edit did in between (found by the ninth T2 refute, E18).
    """
    return sorted(c for c in graph if cid in _pins_of(graph, c))


def _open_task(graph: dict, cid: str) -> bool:
    """A Task that can still take `add freeze` — not done, dropped or archived (E9)."""
    fm = (graph.get(cid) or {}).get("fm") or {}
    return fm.get("type") == "Task" and str(fm.get("status") or "") not in ("done", "dropped", "archived")


def _last_test_cmd(root) -> str:
    """The last command `run` was given in this bundle, or "" — remembered, never guessed."""
    index = Path(root) / "index.md"
    if not index.is_file():
        return ""
    return str((read(index, "T0")["fm"] or {}).get("test_cmd") or "").strip()


def _task_test_cmd(graph: dict, cid: str) -> str:
    """Latest narrow Run computation owned by this Task, using scanned frontmatter only."""
    receipt_cid = _latest_run_cid((graph[cid]["fm"] or {}).get("verified") or [])
    run_fm = ((graph.get(receipt_cid or "") or {}).get("fm") or {})
    if run_fm.get("type") != "Run" or str(run_fm.get("task") or "") != cid:
        return ""
    return str(run_fm.get("computation") or "").strip()


def _next_verb(graph: dict, cid: str, t2=None, root=None) -> str:
    """The one runnable next command for a task, by its stamp-derived beat.

    `t2` is the node's body when the caller already holds it — `todo` does. Without it the beat
    is derived at T0, which is what `status` requires (`build-orient`'s R:T2SCAN).
    """
    slug = cid.rsplit("/", 1)[-1][:-3]
    node = graph[cid]
    beat = _beat_of(node, t2, graph)
    fm = node.get("fm") or {}
    # W1 (R:UNBRIEFED): at the build beat the ENTRY comes first — a sealed, unbriefed task
    # points at `add brief`, and moves on to the run the moment the entry is recorded.
    if beat == "build" and fm.get("type") == "Task" \
            and str(fm.get("depth") or "standard") != "quick" \
            and sealed_direction(fm) and not _brief_entered(fm.get("verified") or []):
        return f"add brief {slug}"
    # All three scaffold words mean the same unfinished work — the word says which plan wants it,
    # not what to do about it. `abandoned` and `adrift` still point at authoring, because the OTHER
    # exits (`add drop`, or re-homing it under a live milestone) are named by the milestone rung
    # that produced the word, not by a per-row hint.
    if beat in ("scaffold",) + SCAFFOLD_KINDS:
        return AUTHOR_NEXT.get(str(fm.get("type")), AUTHOR_NEXT["Task"]).format(slug=slug)
    # The floor rung's affordance (regression-floor): a declared host suite with no fresh green
    # receipt is named first, with the PLAN's own command — only when the caller holds the body
    # (`todo` does); `status` scans at T0 and the gate names the same line on refusal.
    if beat == "verify" and t2 is not None and root is not None and _rung_bound(graph, cid, fm):
        floor = regression_floor(t2)
        if floor and floor["mode"] in ("full", "affected"):
            fr, _ = latest_floor_receipt(root, cid)
            if fr is None or str(fr.get("exit")) != "0" or not fresh(fr, Path(root).parent)[0]:
                return f"add run {slug} --floor -- {floor['cmd']}"
    # The refute rung's affordance: at the verify beat a rung-bound task points at `add refute`
    # until a refute cites its latest run — the gate would refuse R:UNREFUTED otherwise, and the
    # first contact with a rung should be a hint, not a refusal.
    if beat == "verify" and _rung_bound(graph, cid, fm):
        stamps = fm.get("verified") or []
        last_run = _latest_run_cid(stamps)
        if last_run and _refute_of(stamps, last_run)[0] is None:
            return f'add refute {slug} --by "<name>" --tier T2 --held|--found "<input>"'
    hint = BEAT_NEXT.get(beat, "add status").format(slug=slug)
    # A global last command belongs to another Task as often as this one. The scanned Run
    # frontmatter carries the exact computation for the Task's own latest narrow stamp.
    if "<test cmd>" in hint:
        owned = _task_test_cmd(graph, cid)
        if not owned:
            return f"add show {slug}"  # inspect its PLAN before supplying a new command
        if any(re.search(rf"(?:^|\s){re.escape(flag)}(?:=|\s)", owned)
               for flag in JUNIT_FLAGS):
            return f"add run {slug} -- {owned}"  # it already writes the report
        hint = hint.replace("<test cmd>", owned)
    return hint


def todo(root, milestone: str = None) -> tuple:
    """The open worklist: active Tasks (direction|build|verify) grouped by beat, each with its next
    verb. Optionally restricted to one milestone. Read-only — `(items, note)`, never a write."""
    graph = scan(Path(root))
    msel = _wave_slug(milestone) if milestone else None
    # ONE body read per open task, reused by the hint loop below — deriving the beat and then
    # re-reading the same file to build its hint read every direction-beat node twice.
    items, bodies = [], {}
    for cid in active(graph):
        fm = graph[cid]["fm"] or {}
        if fm.get("type") != "Task":
            continue
        if msel and _wave_slug(fm.get("milestone")) != msel:
            continue
        # ONE body read per node, handed to both derivations — `todo` is not T0-bound (it already
        # reads the body for the unswept-pairs hint), so its arrow gets the COMPLETE scaffold
        # answer rather than the T0 half `status` must settle for.
        try:
            t2 = read(graph[cid]["path"], "T2")
        except (OSError, ValueError, KeyError, TypeError):
            t2 = None
        bodies[cid] = t2
        items.append((cid, _beat_of(graph[cid], t2, graph), _next_verb(graph, cid, t2, root)))
    if not items:
        where = f" under `{milestone}`" if milestone else ""
        return [], f"nothing open{where}\nnext: add status"
    # `adrift` and `abandoned` sort ABOVE `queued`: a task no live plan wants is the one a reader
    # must decide about, and a queue of forty hides two strays at the bottom of the list.
    order = {"adrift": -3, "abandoned": -2, "queued": -1, "scaffold": -1,
             "direction": 0, "build": 1, "verify": 2}
    items.sort(key=lambda it: (order.get(it[1], 9), it[0]))
    lines, beat = [], None
    for cid, st, nxt in items:
        if st != beat:
            lines.append(f"{st}:")
            beat = st
        hint = ""
        if st == "direction":
            # Progressive, so freeze CONFIRMS work already done instead of ambushing the
            # author with the whole matrix at the moment they expected to be finished. A
            # gate first met as a wall earns a reputation for obstruction, not for catching.
            node_t2 = bodies.get(cid) or read(graph[cid]["path"], "T2")
            if gives_unauthored(node_t2) and _section_of(node_t2.get("body") or "",
                                                         "ASSUMPTIONS").strip():
                hint = "  (gives: unauthored — no surfaces to sweep)"
            elif (collapsed := collapsed_surfaces(node_t2)) and \
                    _section_of(node_t2.get("body") or "", "ASSUMPTIONS").strip() and \
                    str((node_t2.get("fm") or {}).get("depth") or "standard") != "quick":
                hint = f"  (split {' · '.join(collapsed)} — one surface per S id)"
            else:
                # Both counts, appended in ladder order — the sweep refuses first, so it reads
                # first. The uncovered count APPENDS rather than replaces (A6): re-ranking a
                # tuned hint chain would change what an author is told first for reasons that
                # have nothing to do with this rung. A zero shows nothing, like the sweep's.
                bits = []
                left = len(assumption_sweep(node_t2))
                if left:
                    bits.append(f"{left} unswept pair{'s' if left > 1 else ''}")
                if (nocov := len(uncovered_obligations(node_t2))):
                    bits.append(f"{nocov} uncovered")
                if _rung_bound(graph, cid, graph[cid]["fm"] or {}) and (one := len(single_mode_musts(graph[cid]))):
                    bits.append(f"{one} single-mode Must{'s' if one > 1 else ''}")
                if bits:
                    hint = f"  ({' · '.join(bits)})"
        # consumers-go-stale: at any beat, a consumer whose pinned `#gives` moved says so and names
        # the verb; appended after the beat's own hint so a tuned chain keeps its first word.
        for provider, _p, _c in stale_needs(graph, cid):
            hint += (f"  (needs stale: {provider.rsplit('/', 1)[-1][:-3]}#gives moved — "
                     f"add freeze {cid.rsplit('/', 1)[-1][:-3]})")
        lines.append(f"  · {cid.rsplit('/', 1)[-1][:-3]:<24} → {nxt}{hint}")
    where = f" under `{milestone}`" if milestone else ""
    return items, f"{len(items)} open task(s){where}:\n" + "\n".join(lines)


def _title_of(fm: dict, width: int = 0) -> str:
    """A node's authored title, or "" when it has none. Never a placeholder.

    A title still standing in its slot is not a title (M6): rendering `<the surface this
    publishes>` in a listing spends the row and tells the reader nothing they could act on.
    `is_slot` is the one placeholder rule, so this agrees with every other reader by construction.
    """
    t = str((fm or {}).get("title") or "").strip()
    if not t or is_slot(t):
        return ""
    return t if not width or len(t) <= width else t[:width - 1].rstrip() + "…"


def status(root, all: bool = False, check: bool = False) -> str:
    """One bounded orientation report, ending in a runnable `next:` line.

    `check=True` adds the CARD-drift scan. It is OPT-IN because detecting drift requires
    reading every node's CARD, and M1 holds this verb to T0. Orientation must stay cheap;
    the deeper pass belongs to `doctor --sync`.
    """
    # No bundle here → say so, and point at init. Orientation is the resume verb the skill runs
    # first; on a bundle-less dir the honest answer is "create one", not a false empty-orientation
    # (`index.md` is the marker init always writes and nothing else does).
    if not (Path(root) / "index.md").is_file():
        # …unless a 2.x bundle is sitting here. 2.x wrote `state.json` and `tasks/<slug>/PLAN.md`;
        # 3.0 reads `index.md` + `graph.json` and retired `migrate`, so the upgrade is a deliberate
        # clean break. But answering "no bundle here" to someone whose own state.json is in this
        # very directory reads as "the upgrade ate my project" — name the format and say the files
        # are safe. (Neither marker is anything 3.0 writes, so this cannot fire on a 3.0 bundle.)
        if (Path(root) / "state.json").is_file() or (Path(root) / "tasks").is_dir():
            return ("this is an ADD 2.x bundle — 3.0 reads a different format and does not "
                    "convert it\n"
                    "nothing here was deleted: your 2.x files (state.json · tasks/ · specs/) are "
                    "untouched\n"
                    "`add upgrade` archives them to `.add-2x-archive/`, writes MIGRATION.md, "
                    "and initialises a fresh 3.0 bundle beside the record\n"
                    "next: add upgrade")
        # …and unless a bundle is sitting ABOVE us. `cd` into a subdirectory is the most
        # common thing an engineer does; answering "run `add init`" there is confidently
        # wrong, and following it builds a rival bundle (R:MISDIRECT). Name the ancestor and
        # hand back a runnable recovery — the confusion is at its worst exactly here (A6).
        above = ancestor_bundle(root)
        if above is not None:
            project = Path(above).parent
            return (f"no bundle here — but this directory sits inside the ADD project at "
                    f"`{project}`\n"
                    f"nothing is wrong: orientation reads the bundle you are standing in\n"
                    f"next: cd {project} && add status")
        return f"no bundle here — run `add init` to create one\nnext: add init"

    graph = scan(root)
    out = []

    project = next((n for n in graph.values() if (n["fm"] or {}).get("type") == "Project"), None)
    pfm = ((project or {}).get("fm") or {})
    # The goal rides the TITLE line and the lesson tally rides it too, so orientation gains no
    # line at all (A13). Both were on the tally line in the draft; that line only exists when
    # something is hidden, so `--all` would have silently dropped the count it most needs.
    goal = str(pfm.get("goal") or "").strip()
    if not goal or PLACEHOLDER.search(goal):
        goal = "goal unauthored (add doctor)"
    elif len(goal) > 72:
        goal = goal[:71].rstrip() + "…"
    # T0 only (R:T2SCAN): each Spec DECLARES its own open count in frontmatter, so the total
    # costs no body read. One unreadable declaration makes the whole total UNKNOWN rather than
    # a smaller number that looks like an answer — a bundle written before this key existed
    # must not report a clean board over an open pile (R:UNKNOWNCLEAN).
    counts = [declared_open_deltas(n["fm"]) for n in graph.values()
              if (n["fm"] or {}).get("type") == "Spec"]
    total = "?" if (counts and any(c is None for c in counts)) else sum(c for c in counts if c)
    tally = ("" if not counts or total == 0 else
             f"  ·  {total} open delta{'' if total == 1 else 's'} (add deltas)")
    # The count `doctor` already reports, in the headline where a reviewer sees it. A 40-task
    # roadmap shipped with 38 nodes in scaffold and every surface said so EXCEPT the one line a
    # reader starts from. Computed from the same predicate `doctor` uses (A4), so the headline
    # and the report can never disagree — and silent at zero (A9), like the delta clause.
    # Split by the SAME three words the rows show. One count of forty said the roadmap was
    # unfinished; `38 queued · 2 adrift` says which two a reader has to decide about. A `dropped`
    # task is answered, not pending, and is counted in neither (M6).
    pending = [n for n in graph.values()
               if (n["fm"] or {}).get("type") in LIFECYCLE_TYPES
               and (n["fm"] or {}).get("status") != "dropped" and _is_scaffold(n)]
    split = {k: sum(1 for n in pending if _scaffold_kind(graph, n) == k) for k in SCAFFOLD_KINDS}
    shown = " · ".join(f"{c} {k}" for k, c in split.items() if c)
    queued = f"  ·  {shown} (add todo)" if shown else ""
    out.append(f"{pfm.get('title', Path(root).name)} — {goal}"
               f"  ·  {len(graph)} nodes{tally}{queued}")



    # Orientation is about WORK. Receipts are evidence — reachable from the task that owns
    # them, and never the thing a cold reader needs first. Ordering by ORIENT_RANK keeps the
    # 20-line budget spent on milestones and tasks rather than on files named `1.md`.
    def keep(cid):
        fm = graph[cid]["fm"] or {}
        # A receipt and an interview sidecar are RECORDS about a node, not nodes on the board.
        # Registering `Interview` in ABF_TYPES (so `doctor` stops filing a finding against a file
        # the engine wrote) put them in the roster; they belong with `Run`, out of it.
        if fm.get("type") in ("Run", "Interview"):
            return False
        # `archived` was missing from this tuple, so the deadest state in the engine was the one
        # work row a finished bundle showed. Answered is answered.
        return all or fm.get("status") not in ANSWERED

    # A Spec or a Persona carrying no `status:` has no state to BE in — it is a lens, seeded once
    # and never advanced, and it printed a constant `[—]` row every session. Nine of thirteen rows
    # on the live bundle were exactly these. They are the bundle's vocabulary, not its board, so
    # the bare report counts them by type and `--all` still lists every one, unchanged
    # (M1 · M2 · R:NOWAYBACK). A node that carries a real status is never collapsed (R:HIDDENSTATE).
    # A node with no `status:` at all has no state to BE in — it is the bundle's vocabulary, not
    # its board, and it printed a constant `[—]` row every session. This was a TYPE LIST naming
    # Spec and Persona, so `Project` and `index` kept their exemption from the rule written to
    # remove them: on a finished bundle they were two of the three rows shown -> "R:DEADROW".
    # A predicate has no such gaps. A node that carries a real status is never collapsed
    # (R:HIDDENSTATE).
    def constant(cid):
        return not (graph[cid]["fm"] or {}).get("status")

    hidden = [] if all else [c for c in graph if keep(c) and constant(c)]

    def rank(cid):
        # Vocabulary sorts LAST wherever it is shown — under `--all` it is context, never the
        # board. An UNRECOGNISED beat sorts first: the engine does not know what it is, which is
        # exactly when a person should look.
        if constant(cid):
            return 99
        return ATTENTION_RANK.get(_beat_of(graph[cid], None, graph), 0)

    shown = sorted((c for c in graph if keep(c) and c not in set(hidden)),
                   key=lambda c: (rank(c), c))
    work = [c for c in shown if not constant(c)]
    # `--all` is uncapped by design (A3), so it says how big "everything" is before it scrolls.
    if all and shown:
        out[0] += f"  ·  {len(shown)} row{'' if len(shown) == 1 else 's'}"
    for cid in shown[:(len(shown) if all else MAX_LINES)]:
        fm = graph[cid]["fm"] or {}
        # The stamps, never the stored field. `freeze` appends and never `sets`, so
        # `status:` stays at `direction` for the whole life of a frozen task — orientation
        # read it and contradicted `todo`, `doctor` and its own `next:` line in one breath
        # (R:BEATLIE). `_beat_of` is frontmatter-only here, so the T0 read tier holds.
        beat = _beat_of(graph[cid], None, graph) if fm.get("type") in BEAT_TYPES \
            else fm.get("status", "—")
        # The one field a queued node HAS authored. Forty of them shipped for review carrying
        # real titles that no orientation verb rendered, so the roadmap read as forty anonymous
        # slugs and had to be opened file by file. Last in the row (A12), so every column a
        # guard already reads keeps its position, and truncated so the row cannot wrap.
        # One row is ONE line, at ROW_WIDTH. The beat column is PADDED: it used to be bare
        # `[{beat}]`, whose width varies with the word, so the type column after it never lined
        # up — `[queued] Task` against `[direction] Milestone`. Every column is now fixed, and
        # the title takes exactly what is left (M7 · A6).
        slug = cid.rsplit("/", 1)[-1][:-3]
        lead = f"  · {slug[:SLUG_W]:<{SLUG_W}} {('[' + str(beat) + ']'):<{BEAT_W}} " \
               f"{str(fm.get('type', '')):<9} "
        # A released milestone names its tag at the row's end (release-stamp, M5): the newest
        # `act: release` stamp, so "which tag shipped this" is answered without opening the file.
        tag = next((str(st.get("tag")) for st in reversed(fm.get("verified") or [])
                    if isinstance(st, dict) and st.get("act") == "release" and st.get("tag")), "")
        # One row is ONE line (a-roadmap R:ROWBLOAT): the title yields first, down to a floor of
        # TITLE_FLOOR characters, then the tag itself is cut — never a negative width, which
        # sliced the title from its end (found by the T2 refute, E8).
        tail = f" · {tag[:max(0, ROW_WIDTH - len(lead) - 3 - TITLE_FLOOR)]}" if tag else ""
        out.append((lead + _title_of(fm, ROW_WIDTH - len(lead) - len(tail)) + tail).rstrip())
    if not all and len(shown) > MAX_LINES:
        # The hint names a command that RUNS and actually produces the withheld rows. It used to
        # print under `--all` too, advising the flag already in force — a hint that cannot change
        # what it just printed, with no other route to those rows -> "R:DEADHINT" · "R:NOWAYIN".
        out.append(f"  … {len(shown) - MAX_LINES} more of {len(shown)} — add status --all")
    if hidden:
        tally = {}
        for c in hidden:
            # `index.md` is the bundle's MANIFEST, not a node with a missing type. Counting it
            # as `1 ?` invited a hunt for a malformed file that does not exist.
            t = (graph[c]["fm"] or {}).get("type") or (
                "manifest" if c == "/index.md" else "untyped")
            tally[t] = tally.get(t, 0) + 1
        counted = " · ".join(f"{n} {t}" for t, n in sorted(tally.items()))
        out.append(f"  … {counted} carrying no state — not listed (`--all`)")

    # M6: name the last recorded act. Day-only stamps cannot order different nodes, so the
    # append index resolves same-day acts within a node and CID makes cross-node ties stable.
    acts = []
    for cid, n in graph.items():
        for i, st in enumerate((n["fm"] or {}).get("verified") or []):
            if isinstance(st, dict) and st.get("at") and st.get("act"):
                acts.append((str(st["at"]), i, cid, str(st["act"]),
                             cid.rsplit("/", 1)[-1][:-3]))
    if acts:
        when, _, _, act, who = max(acts)
        # Cross-node stamps with the same date have no recorded global order. Name the
        # deterministic representative, but mark the tie rather than claiming chronology.
        tied_nodes = {c for day, _, c, _, _ in acts if day == when}
        suffix = f" · {when}" + (" · day tie" if len(tied_nodes) > 1 else "")
        lead = f"  last: {act} "
        who_room = max(1, ROW_WIDTH - len(lead) - len(suffix))
        shown_who = who if len(who) <= who_room else who[:who_room - 1] + "…"
        out.append(f"{lead}{shown_who}{suffix}")

    drift = card_drift(graph) if check else []
    if drift:
        out.append(f"  ! {len(drift)} node(s) whose CARD contradicts frontmatter — `add doctor --sync`")
    tdrift = tooling_drift(root, graph) if check else None
    if tdrift:
        out.append(f"  ! {tdrift}")

    # A live wave is surfaced at the resume point — WHO is advising WHAT — not left buried in the
    # milestone file. Each token `slug:persona` renders `slug→persona`; a bare slug renders as-is.
    for cid in shown:
        fm = graph[cid]["fm"] or {}
        if fm.get("type") != "Milestone" or not fm.get("active_wave"):
            continue
        raw = fm["active_wave"]
        toks = raw if isinstance(raw, list) else [t.strip() for t in str(raw).strip("[]").split(",") if t.strip()]
        rendered = " · ".join(t.replace(":", "→", 1) if ":" in t else t for t in toks)
        out.append(f"  ~ wave on {cid.rsplit('/', 1)[-1][:-3]}: {rendered}")

    frontier = ready(graph)
    waiting = [c for c in active(graph) if (graph[c]["fm"] or {}).get("status") == "verify"]
    if waiting:
        nxt = f"next: {_next_verb(graph, waiting[0], root=root)}"
    elif frontier:
        f0 = frontier[0]
        # Through `_next_verb`, so this hint and `todo`'s arrow cannot disagree — the stamp test
        # that used to live here was a third reading of the beat, and a node that was created and
        # never authored got advised toward the freeze that is structurally guaranteed to refuse it.
        nxt = f"next: {_next_verb(graph, f0, root=root)}"
    elif any((n["fm"] or {}).get("type") == "Milestone" for n in graph.values()):
        # A slot only the HUMAN can fill — a slug nobody has chosen — is legitimate guidance; the
        # defect R:PLACEHOLDER_NEXT names is a slot the ENGINE could have filled and did not
        # (`<test cmd>`, which `run` now records per Task). Spelled in full, so what is typed
        # around the human-authored slug slot is copy-pasteable.
        nxt = 'next: add new Task <slug> --title "<one line>"'
    else:
        nxt = 'next: add new Milestone <slug> --title "<one line>"' 
    # WORK, not rows: `--all` widens the board with vocabulary, and that must not turn "nothing
    # needs you" into silence (A9). The flag changes what is listed, never what empty means.
    if not work:
        # An empty board is an ANSWER, not an empty list. A finished bundle and a broken read
        # printed the same thing: nothing (A4 · M5).
        answered = sum(1 for c in graph if (graph[c]["fm"] or {}).get("status") in ANSWERED)
        out.append(f"  nothing needs you — {answered} answered, {len(hidden)} carrying no state")

    # The current consequence is per OPEN Task. A later non-gate act remains global activity,
    # but cannot resolve a stopped Task; only a later gate (or reopen) changes that verdict.
    open_tasks = [c for c, n in graph.items()
                  if (n["fm"] or {}).get("type") == "Task"
                  and (n["fm"] or {}).get("status") not in ANSWERED]
    if open_tasks:
        stops = [c for c in open_tasks
                 if str((_effective_gate_stamp(graph[c]["fm"] or {}) or {}).get("outcome"))
                 == "HARD-STOP"]
        if stops:
            now_cid = min(stops, key=lambda c: (rank(c), c))
        else:
            # Follow the existing final runnable route when it names an open Task. A milestone
            # or a human-authored slug slot does not become a made-up current Task.
            route = re.search(r"\badd [a-z][a-z-]* ([a-z0-9][a-z0-9-]*)\b", nxt)
            route_cid = f"/tasks/{route.group(1)}.md" if route else ""
            now_cid = route_cid if route_cid in open_tasks else min(
                open_tasks, key=lambda c: (rank(c), c))
        slug = now_cid.rsplit("/", 1)[-1][:-3]
        beat = _beat_of(graph[now_cid], None, graph)
        gate_stamp = _effective_gate_stamp(graph[now_cid]["fm"] or {})
        verdict = str((gate_stamp or {}).get("outcome") or "none")
        if verdict not in ("PASS", "RISK-ACCEPTED", "HARD-STOP"):
            verdict = "none"
        suffix = f" · beat={beat} · last-gate={verdict}"
        slug_room = max(1, ROW_WIDTH - len("  now: ") - len(suffix))
        shown_slug = slug if len(slug) <= slug_room else slug[:slug_room - 1] + "…"
        out.append(f"  now: {shown_slug}{suffix}")
        if gate_stamp:
            receipt_cid = str(gate_stamp.get("receipt") or "")
            same_task_run = re.fullmatch(
                rf"/tasks/{re.escape(slug)}\.d/runs/(\d+)\.md", receipt_cid)
            receipt_token = (f"runs/{same_task_run.group(1)}.md"
                             if same_task_run else "unrecorded")
            fragment = ("FINDINGS" if gate_stamp.get("kind") == "sources"
                        and not receipt_cid else "verified")
            ref = f"/tasks/{slug}.md#{fragment}"
            lead = f"  evidence: receipt={receipt_token} · ref="
            if len(lead + ref) > ROW_WIDTH:
                room = max(1, ROW_WIDTH - len(lead))
                end = f"#{fragment}"
                ref = (ref[:room - len(end) - 1] + "…" + end
                       if room > len(end) + 1 else end[:room])
            out.append(lead + ref)
    return "\n".join(out + [nxt])


# ============================ run · freshness · learn — the receipt layer (e7)
#
# This module pays the A22 debt. A receipt is fresh when the code it observed is the code
# that exists now, and "now" is decided by CONTENT, not by timestamps:
#
#   `git worktree add` sets every checked-out file's mtime to checkout time. Under the
#   mtime predicate every committed receipt reads stale in a fresh clone, worktree or CI
#   job — deterministically, and hardest on the two designs this format promotes. Blob
#   hashes do not move when a file is checked out, so they answer the question actually
#   being asked: is this the same code?
#
# `run` executes the command the AGENT supplied and notarises the result. It never runs
# anything on its own initiative, and it is always bounded by a timeout — a hang is a
# recorded outcome, not a lost session.

RUN_TIMEOUT = 900


def _git(root, *args, timeout: int = 30, input: str = None, strip: bool = True):
    """Run one git command. Returns None when git is absent or the tree is not a repo.

    `strip=False` for any NUL-delimited stream: porcelain writes `" M path"` for a worktree
    edit that is not staged, and `.strip()` eats that leading status space, so the FIRST
    record parses two characters short and its path loses a character (2026-09-01 review).
    """
    try:
        done = subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                              text=True, timeout=timeout, input=input)
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    return done.stdout.strip() if strip else done.stdout


def _git_blobs(root, rels: list) -> dict:
    """`{rel: sha1}` for every path git could hash — ONE `hash-object --stdin-paths` call.

    The per-file form spawned one subprocess per path, which priced a large freshness set in
    seconds of fork/exec (field receipt: hundreds of entries at the gate). Empty on any batch
    failure — the callers keep their per-file fallback, so a single unhashable path degrades
    exactly as it always did instead of taking the batch with it."""
    if not rels:
        return {}
    out = _git(root, "hash-object", "--stdin-paths", timeout=120,
               input="\n".join(rels) + "\n")
    lines = out.splitlines() if out is not None else []
    return dict(zip(rels, lines)) if len(lines) == len(rels) else {}


def _scope_files(root, entry) -> list:
    """The files ONE `scope:` entry names, as absolute paths — the single reading of what an entry
    covers (M2).

    Lifted out of `scope_digest` so the freshness set and every other question about an entry give
    the SAME answer. A glob is read with `Path.glob`, where `*` does NOT cross a `/`; `fnmatch`'s
    `*` does, and reading an entry that way let one unfrozen node created by anyone —
    `add new Task junk --scope '**'`, exit 0, no freeze, no human — stand the sensitive floor down
    for every path in the bundle, while that node's own freshness set was EMPTY. A node that holds
    no files has routed nothing.
    """
    root, entry = Path(root), str(entry)
    if not entry:
        return []
    try:
        candidates = _scope_candidates(root, entry)
    except (NotImplementedError, ValueError, OSError):
        # An entry no walker can resolve — `/etc/*` is a NotImplementedError from `Path.glob`,
        # `/etc/hosts` a ValueError from `relative_to` — names no file HERE, and that is the whole
        # answer. It must not raise: `learn` now reads EVERY node's scope, so one node anyone can
        # write turned the direct lane's one bundle write into a traceback instead of a refusal
        # (R:LANEBLOCKED), and `gate` reads them too.
        return []
    out = []
    for path in candidates:
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue          # resolved outside the root — no entry of this bundle names it
        # Build noise is not the code under review — hashing it would make the digest flap.
        if "__pycache__" in rel.parts or path.suffix in (".pyc", ".pyo"):
            continue
        out.append(path)
    return out


def _scope_candidates(root, entry: str) -> list:
    """The raw paths one entry expands to, before the file/noise filter."""
    if any(c in entry for c in "*?["):
        candidates = sorted(root.glob(entry))
    else:
        p = root / entry
        # A directory scope entry expands to the files beneath it — otherwise a dir-scoped task
        # gets an empty digest and `gate` cannot establish freshness (field-report finding #6).
        # Enumerated THROUGH git (tracked + untracked-not-ignored), never a raw walk: the
        # project's own .gitignore defines its build noise, so `.next/`, `node_modules/` and
        # friends stay out — a rebuild must not stale a receipt no source edit touched, and
        # walking a dependency tree must not price the notary (field receipt: a dir scope
        # digested a whole turbopack cache). A glob or an explicitly named file is a
        # deliberate declaration and keeps its exact reading.
        if p.is_dir():
            listed = _git(root, "ls-files", "-z", "--cached", "--others",
                          "--exclude-standard", "--", entry)
            candidates = [root / f for f in sorted((listed or "").split("\0")) if f]
        else:
            candidates = [p]
    return candidates


def _scope_holds(root, entry, path) -> bool:
    """Does `entry` cover `path`? The one question, asked of the one reader."""
    return any(f.relative_to(Path(root)).as_posix() == str(path) for f in _scope_files(root, entry))


def scope_digest(root, scope: list) -> list:
    """`[{path, blob}]` — git blob hashes over the freshness set (FORMAT §8.1, A22).

    Outside a git working tree this returns `[]`, and the caller must declare
    `freshness: mtime` rather than pretend to a content digest it cannot compute.
    """
    root = Path(root)
    if _git(root, "rev-parse", "--git-dir") is None:
        return []
    out, rels = [], []
    for entry in sorted(str(s) for s in (scope or [])):
        rels.extend(f.relative_to(root) for f in _scope_files(root, entry))
    hashes = _git_blobs(root, [str(r) for r in rels])
    for rel in rels:
        blob = hashes.get(str(rel)) or _git(root, "hash-object", str(rel))
        if blob:
            out.append({"path": rel.as_posix(), "blob": f"sha1:{blob}"})
    return out


def _tree_blobs(root, tree: str, paths: list) -> dict:
    """`{path: blob}` a git tree-ish holds at each path — ONE read-only `ls-tree`, relative to `root`."""
    listed = _git(root, "ls-tree", "-r", "-z", tree, "--", *[str(p) for p in paths], strip=False)
    held = {}
    for rec in (listed or "").split("\0"):
        if "\t" in rec:
            meta, path = rec.split("\t", 1)
            held[path] = meta.split()[2]
    return held


def _committed_to_head(root, digest: list) -> bool:
    """True iff every `{path, blob}` in `digest` is the blob HEAD's tree holds at that path.

    One `ls-tree` over the digest's paths, output relative to `root` exactly as the digest is.
    A path HEAD does not hold (untracked, or added since) is a difference, so it answers False.
    """
    held = _tree_blobs(root, "HEAD", [d["path"] for d in digest])
    return all(held.get(str(d["path"])) == str(d["blob"]).replace("sha1:", "", 1) for d in digest)


def _tag_tree(root, tag: str):
    """The tree sha a tag (any tree-ish) resolves to, or None — `rev-parse`, read-only."""
    sha = _git(root, "rev-parse", "--verify", "-q", f"{tag}^{{tree}}")
    return sha if sha and re.fullmatch(r"[0-9a-f]{40,64}", sha) else None


def _anchor(root, graph: dict, mcid: str, tree: str) -> tuple:
    """`(ok, detail, receipts, skipped, not_done)` — does `tree` hold every scope blob the milestone's done
    members' gated receipts recorded? (release-stamp, FORMAT §8.6)

    Members are the Tasks whose `milestone:` names this slug, in cid order; the anchor is the
    receipt each done member's NEWEST `act: gate` stamp cites — the one the verdict read, never
    the latest run, which may postdate the verdict red or wider (found by the T2 refute, E7), and
    never a floor receipt (the gate never cites one, A2). A done member whose gated receipt
    carries no content digest, or whose cited receipt is gone, cannot be anchored and refuses by
    name; a member with no gate stamp citing a receipt (an explore, a hand-marked done) is
    skipped by name. The first mismatch refuses, naming the task, the path and both blobs.
    """
    repo = Path(root).parent
    slug = mcid.rsplit("/", 1)[-1][:-3]
    members = sorted(c for c, n in graph.items()
                     if (n["fm"] or {}).get("type") == "Task"
                     and str((n["fm"] or {}).get("milestone") or "").strip() == slug)
    receipts, skipped = [], []
    not_done = [f"{c} ({(graph[c]['fm'] or {}).get('status') or '—'})" for c in members
                if (graph[c]["fm"] or {}).get("status") != "done"]
    for cid in members:
        if (graph[cid]["fm"] or {}).get("status") != "done":
            continue
        # The newest CLOSING gate — the verdict `done` reads — and only one that POSTDATES the
        # member's last `act: reopen`: a reopen resets the gate, so a verdict before it anchors
        # nothing (second and third T2 refutes, E9, E12). A HARD-STOP after the close cites a
        # finding's receipt, not a verdict's, and entitles nothing.
        rcid = None
        for st in reversed((graph[cid]["fm"] or {}).get("verified") or []):
            if not isinstance(st, dict):
                continue
            if st.get("act") == "reopen":
                break
            if st.get("act") == "gate" and st.get("receipt") and str(st.get("outcome") or "PASS") in CLOSING_VERDICTS:
                rcid = str(st.get("receipt"))
                break
        if rcid is None:
            skipped.append(cid.rsplit("/", 1)[-1][:-3])
            continue
        # A cited receipt must be the member's OWN — under `<slug>.d/runs/` — so a hand-edited
        # stamp can neither borrow another task's digest nor read outside the bundle.
        own = f"/tasks/{cid.rsplit('/', 1)[-1][:-3]}.d/runs/"
        if not rcid.startswith(own) or "/../" in rcid or not re.fullmatch(r"\d+\.md", rcid[len(own):]):
            return False, f"{cid} is unanchorable — its gate cites {rcid}, not a receipt of its own ({own}<n>.md)", [], [], []
        rpath = root / rcid.lstrip("/")
        receipt = (read(rpath, "T0")["fm"] or {}).get("receipt") if rpath.is_file() else None
        if not isinstance(receipt, dict):
            return False, f"{cid} is unanchorable — the receipt its gate cites, {rcid}, is gone", [], [], []
        digest = receipt.get("scope_digest") or []
        if not digest or not all(isinstance(d, dict) and d.get("path") and d.get("blob") for d in digest):
            return False, f"{cid} is unanchorable — its receipt {rcid} carries no content digest", [], [], []
        held = _tree_blobs(repo, tree, [d["path"] for d in digest])
        for d in digest:
            want = str(d["blob"]).replace("sha1:", "", 1)
            got = held.get(str(d["path"]))
            if got != want:
                return (False, f"{cid} verified {d['path']} at {want}, the tag's tree holds "
                               f"{got or 'nothing at that path'}", [], [], [])
        receipts.append(rcid)
    # A tree and no receipts is a label, not an anchor (A6, E10): name what kept it empty.
    if not receipts:
        why = (f"no member anchors — not done: {', '.join(not_done)}" if not_done else
               "no member anchors — the milestone has no member Task with a closing gate" if members else
               "no member anchors — the milestone has no member Task")
        return False, why, [], [], []
    return True, "", receipts, skipped, not_done


def release(root, tag: str, milestones: list, by: str, artifact: str = None, build: str = None) -> tuple:
    """`add release <tag> --milestone m …` — bind a tag's tree to the receipts that verified it.

    Appends `{ act: release, tag, tree, receipts }` to each named DONE milestone after proving,
    with READ-ONLY git (`rev-parse`, `ls-tree` — never `tag`, `push`, `publish`: R:OUTWARD), that
    the tag's tree holds every scope blob the members' gated receipts recorded (R:UNANCHORED
    otherwise). `--artifact` and `--build` are recorded verbatim when handed and never verified
    (R:PROVENANCEJUDGED): provenance is the pipeline's to produce and consume. `(stamps, note)`.
    """
    root = Path(root)
    graph = scan(root)

    def refuse(why: str, fix: str) -> tuple:
        return None, f"cannot release `{tag}` — {why}\nnext: {fix}"

    tree = _tag_tree(root.parent, tag)
    if not tree:
        return refuse(f'git resolves no tree for `{tag}` -> "R:NOSUCHTAG"',
                      "git tag -l — the tag is the human's to cut; release records one that exists")
    targets = []
    for m in milestones:
        mcid = m if m.startswith("/") else f"/milestones/{m}.md"
        node = graph.get(mcid)
        if node is None:
            return refuse(f"no such milestone: {m}", "add status --all")
        fm = node["fm"] or {}
        if fm.get("type") != "Milestone":
            return refuse(f"{mcid} is not a Milestone", "add release <tag> --milestone <milestone>")
        if fm.get("status") not in ("done", "archived"):
            return refuse(f'{mcid} is `{fm.get("status") or "—"}`, not done -> "R:NOTDONE"',
                          f"add milestone-done {m.rsplit('/', 1)[-1].removesuffix('.md')}, then add release {tag}")
        ok, detail, receipts, skipped, not_done = _anchor(root, graph, mcid, tree)
        if not ok:
            return refuse(f'{detail} -> "R:UNANCHORED"',
                          "cut the tag on the tree the receipts observed, or re-run and re-gate the task on this tree")
        targets.append((mcid, receipts, skipped, not_done))
    stamps = []
    for mcid, receipts, skipped, not_done in targets:
        extra = "".join([f', artifact: "{_oneline(artifact)}"' if artifact else "",
                         f', build: "{_oneline(build)}"' if build else ""])
        stamp = (f'{{ by: "{_oneline(by)}", at: {_today()}, act: release, authority: process, '
                 f'tag: "{_oneline(tag)}", tree: {tree}, receipts: "{",".join(receipts)}"{extra} }}')
        _, err = _transition(root, mcid, appends=[("verified", stamp)])
        if err:
            return None, err + "\nnext: add status"
        stamps.append((mcid, receipts, skipped, not_done))
    lines = []
    for mcid, receipts, skipped, not_done in stamps:
        slug = mcid.rsplit("/", 1)[-1][:-3]
        # The note is what did NOT anchor; the stamp is what did (third T2 refute, E11).
        lines.append(f"release recorded on {slug}: {tag} → tree {tree[:12]} · anchored by "
                     f"{len(receipts)} receipt{'' if len(receipts) == 1 else 's'}"
                     + (f" · skipped (no receipt): {', '.join(skipped)}" if skipped else "")
                     + (f" · not anchored (not done): {', '.join(not_done)}" if not_done else ""))
    return stamps, "\n".join(lines) + "\nnext: add status --all"


def fresh(receipt: dict, root) -> tuple:
    """`(ok, why)` — THREE states, and the third is the point.

    `True` fresh · `False` stale · `None` freshness cannot be established. Stale is an ANSWER —
    the receipt observed code that has since changed, which is exactly what a caller asked. An
    unmeasurable receipt is not that answer, and collapsing the two would report a clean `stale`
    over a question the engine could not ask (R:UNKNOWNCLEAN, one verb further on).
    """
    root = Path(root)
    recorded = receipt.get("scope_digest") or []
    if receipt.get("freshness") != "content" or not recorded:
        return None, ("receipt carries no content digest — freshness cannot be established "
                       "(the bundle parent was not a git working tree at run time, or the "
                       "node's `scope:` paths did not exist there)")
    # One batched hash over the existing files; the walk below keeps the original per-entry
    # order, so which failure is reported first is byte-identical to the per-file form.
    hashes = _git_blobs(root, [str(e.get("path")) for e in recorded
                               if (root / str(e.get("path"))).is_file()])
    for entry in recorded:
        rel = str(entry.get("path"))
        path = root / rel
        if not path.is_file():
            return False, f"{entry.get('path')} has vanished since the run"
        blob = hashes.get(rel) or _git(root, "hash-object", str(path.relative_to(root)))
        if blob is None or f"sha1:{blob}" != entry.get("blob"):
            return False, f"{entry.get('path')} changed since the run"
    return True, "every file in scope is byte-identical to the run"


JUNIT_FLAGS = ("--junitxml", "--junit-xml")


def _sniff_report(command: list):
    """The JUnit report path the COMMAND already names, or None.

    `--junitxml` on `add run` tells the engine where to READ; the command writes it. So one path
    was typed twice, and the second mention carried no information the engine did not already
    hold — it was a restatement the caller could get wrong, punished with `ids: unknown`, which
    reads as every rule unbound.

    Deliberately narrow. It matches two known flag spellings, in `=path` and two-token form, and
    returns None for anything else -> "R:GUESSPATH". A broader heuristic would bind a receipt to
    a file the command never wrote, which is worse than reading no report at all: an unbound
    receipt is visibly unbound, a wrongly-bound one is not. A runner that names its report
    somewhere else still has the explicit flag.

    LAST occurrence wins (A5) — that is what the runners themselves honour, so taking the first
    would bind a report the command went on to overwrite.
    """
    found = None
    for i, token in enumerate(str(t) for t in command):
        for flag in JUNIT_FLAGS:
            if token.startswith(flag + "="):
                found = token[len(flag) + 1:] or found
            elif token == flag and i + 1 < len(command):
                found = str(command[i + 1])
    return found or None


def run(root, cid: str, command: list, cwd=None, timeout: int = RUN_TIMEOUT, junit=None,
        floor: bool = False) -> dict:
    """Execute the agent's own command, notarise the result as a Run node.

    Never executes anything the caller did not supply. A non-zero exit and a timeout are
    both recorded outcomes — this function does not raise on a failing command (law 3).
    """
    root, cwd = Path(root), Path(cwd or root)
    graph = scan(root)
    # `or {}` was the whole guard, and it made `run` the only verb that invents its subject.
    # A typo'd slug got `receipt 1 recorded (exit 0)`, a green line and a `next:` pointing at
    # nothing, while the real task still had no receipt — and `doctor` then reported the
    # `orphan_receipt` the engine had just manufactured. Refuse like every other verb; the
    # return keeps `run`'s dict shape so `cli.py` prints a note and exits non-zero.
    if cid not in graph:
        return {"path": None, "receipt": {"exit": 1, "ids": "unknown"}, "computation": "",
                "note": f"no such node: {cid} — no receipt written\nnext: add status"}
    node = graph[cid]
    scope = _scope_list(node.get("fm"))
    # The digest root is the BUNDLE PARENT — the identical root `gate` hands `fresh()` — never
    # the cwd. Field finding (hardening tally #1): a cwd below the project computed the digest
    # against paths that did not exist there, so the receipt silently degraded to mtime and the
    # gate refused a PASS with a message naming neither the cause nor the fix. `cwd` stays what
    # it says: the command's working directory, nothing more.
    digest = scope_digest(root.parent, scope)
    # The anchor (receipt-anchored-to-head): HEAD at run START, before the command can move it,
    # and whether every scope blob is the blob HEAD holds at that path. Read from git as observed
    # — never derived from `git status` (R:COMMITTEDBYCLAIM: dirt outside scope is not this
    # receipt's business) and never written when `rev-parse HEAD` did not answer (R:INVENTEDHEAD:
    # an unborn branch has a git dir and no commit). Absent is UNKNOWN to every reader, and
    # `committed` is written only over a non-empty digest — agreement over nothing is the
    # vacuous-check shape.
    in_git = _git(root.parent, "rev-parse", "--git-dir") is not None
    head = _git(root.parent, "rev-parse", "HEAD") if in_git else None
    committed = _committed_to_head(root.parent, digest) if (head and digest) else None

    # A2/A3: the flag is an OVERRIDE, so it is consulted first and a sniffed value can never
    # beat a stated one — a runner may write its report where the command line never names it.
    junit = junit or _sniff_report(command)

    # The reference the report is judged against, read off the filesystem that will record it.
    # Sniffed or stated, it is the same value from here down — staleness included (M4).
    started = time.time()
    if junit:
        started = _fs_epoch(junit, started)
    try:
        done = subprocess.run([str(c) for c in command], cwd=str(cwd),
                              capture_output=True, text=True, timeout=timeout)
        exit_code, stdout, note = done.returncode, done.stdout[-2000:], ""
    except subprocess.TimeoutExpired:
        exit_code, stdout, note = 124, "", f"timeout after {timeout}s — recorded, not raised"
    except OSError as err:
        exit_code, stdout, note = 127, "", f"could not start the command: {err}"

    # A declared scope with no digest is a degrade the gate WILL refuse — saying why belongs on
    # the receipt, at the moment it happens (R:SILENTDEGRADE). Joined, never overwriting: a
    # timeout's diagnosis and the degrade's are both true.
    # `kind: test-ids` was earned by a file's EXISTENCE: `/usr/bin/true` plus a hand-typed XML
    # naming tests that do not exist produced the strongest evidence rung (2026-08-28 review).
    # A report the command did not write is not evidence of THIS run, so it does not promote.
    stale_report = bool(junit) and _report_predates_run(junit, started)
    if stale_report:
        # A MISSING report and a PRE-DATED one are different facts; saying "it predates the
        # command" of a file that was never written is a false diagnosis on the receipt.
        why = ("junit: no report exists at that path after the run, so the receipt does not "
               "claim `test-ids`" if not Path(junit).exists() else
               "junit: the report was not written during this run (it predates the command), so "
               "the receipt does not claim `test-ids` — evidence must come from the run it names")
        note = f"{note}; {why}" if note else why

    if scope and not digest:
        degrade = ("scope: declared but no digest recorded — the bundle parent is not a git "
                   "working tree, or the scope paths do not exist there; freshness degrades to mtime")
        note = f"{note}; {degrade}" if note else degrade
    if scope and in_git and head is None:
        unborn = "head: the tree has no commit yet — no head recorded, committed unknown"
        note = f"{note}; {unborn}" if note else unborn

    slug = cid.rsplit("/", 1)[-1][:-3]
    runs = root / f"tasks/{slug}.d/runs"
    runs.mkdir(parents=True, exist_ok=True)
    # max+1, never count+1: deleting a receipt used to make the next run OVERWRITE an
    # existing one, so a red run could be turned green by arithmetic (2026-08-28 review).
    taken = [int(q.stem) for q in runs.glob("*.md") if q.stem.isdigit()]
    n = (max(taken) + 1) if taken else 1
    # A24: the evidence kind is EARNED, never assumed. `test-ids` requires IDs a runner
    # actually reported — e12 owes that extraction. Until then the honest kind for a bare
    # command is `command-exit`. Freshness is a separate question from evidence, and wiring
    # both to the presence of a digest (as this first did) claims proof that does not exist.
    # A24's ladder is climbed only with real IDs (e12). No report, no promotion.
    ids = extract_ids(junit) if (junit and not stale_report) else {}
    # A24 needs the ID NAMES, not a count: `gate` binds the node's `covers:` against what the
    # runner reported, and "2/2 reported" cannot be bound to anything. Recording every ID of a
    # 113-test suite would bloat the receipt, so this records exactly the evidence the node's
    # own claims need — the IDs it cites that passed — plus EVERY failure, which is always
    # relevant whether the node cites it or not.
    cited = {c for ids_ in covers(read(node["path"], "T2") if node else {}).values() for c in ids_} \
        if node else set()
    # A citation is bare (M5) and an ID is qualified (M1), so membership is resolved through the
    # ID grammar rather than by `in`. A literal `i in cited` matched nothing once IDs carried
    # their module, so every receipt recorded an empty `passed:` and every gate refused — the
    # regression this comment exists to stop being reintroduced.
    keep = {k for c in cited for k in cite_hits(c, ids)}
    passed = sorted(i for i, v in ids.items() if v == "pass" and i in keep)
    failed = sorted(i for i, v in ids.items() if v != "pass")
    receipt = {"kind": "test-ids" if ids else "command-exit",
               "ids": f"{sum(v == 'pass' for v in ids.values())}/{len(ids)} reported" if ids else "unknown",
               "exit": exit_code,
               "freshness": "content" if digest else "mtime", "at": _today(),
               **({"floor": "regression"} if floor else {}),
               **({"head": head} if head else {}),
               **({"committed": committed} if committed is not None else {}),
               "stdout": stdout.strip().splitlines()[-1] if stdout.strip() else "",
               "note": note}
    body = (f"---\ntype: Run\nruntime: process\ntask: {cid}\n"
            f'computation: "{" ".join(str(c) for c in command)}"\n'
            f"receipt:\n" + "".join(f"  {k}: {v!r}\n" if k in ("stdout", "note")
                                    else f"  {k}: {str(v).lower()}\n" if k == "committed"
                                    else f"  {k}: {v}\n"
                                    for k, v in receipt.items()) +
            ("  passed:\n" + "".join(f"    - {i}\n" for i in passed) if passed else "") +
            ("  failed:\n" + "".join(f"    - {i}\n" for i in failed) if failed else "") +
            ("  scope_digest:\n" + "".join(
                f'    - {{ path: {d["path"]}, blob: "{d["blob"]}" }}\n' for d in digest) if digest else "") +
            f"{_stamp('process:run')}\n---\n")
    write(runs / f"{n}.md", body)
    receipt = dict(receipt, passed=passed, failed=failed, scope_digest=digest)  # F3: the returned
    # copy is the receipt, digest included — a caller passing it to `fresh()` must get the truth.
    cid_run = "/" + str((runs / f"{n}.md").relative_to(root))
    # F3: bind the receipt to the task. A receipt no stamp points at is unreachable evidence.
    _transition(root, cid, appends=[("verified",
        f'{{ by: "process:run", at: {_today()}, act: run, authority: process, '
        f'{"floor: regression, " if floor else ""}'
        f'outcome: {"PASS" if exit_code == 0 else "FAIL"}, receipt: {cid_run} }}')])
    # REMEMBER the command. A notary cannot know a project's test command, but it is handed one
    # on every run — so the build hint stops being `<test cmd>` after the first receipt and starts
    # replaying what actually worked here. Recorded, never guessed; a failing run is still the
    # command this project uses, so the exit code does not gate the memory.
    # A FLOOR run is not the project's narrow test command: remembering it made the next build
    # hint replay the full suite as the narrow receipt (found by the T2 refute of regression-floor,
    # R:FLOORASGATE, E8). The narrow command is the one worth replaying; the floor's lives in PLAN.
    index = root / "index.md"
    if index.is_file() and not floor:
        try:
            n_idx = read(index, "T2")
            write(index, f"---\n{set_key(n_idx['raw'], 'test_cmd', ' '.join(str(c) for c in command))}"
                         f"\n---\n{n_idx['body']}")
        except (OSError, ValueError, KeyError, TypeError):
            pass                    # orientation losing a convenience must never fail a receipt
    # The next verb is DERIVED, not hard-coded: at a plan-or-human floor a green owes a refute
    # before the gate (R:UNREFUTED), and the first contact with a rung should be this hint.
    try:
        render_evidence(root, cid)     # the view; the receipt above is the record
    except (OSError, ValueError, KeyError, TypeError):
        pass
    hint = _next_verb(scan(root), cid, root=root) if exit_code == 0 else f"add gate {slug}"
    return {"path": runs / f"{n}.md", "receipt": receipt, "computation": " ".join(str(c) for c in command),
            "note": f"receipt {n} recorded (exit {exit_code})\nnext: {hint}"}


# The living spec ↔ its 5-DD competency tag (deltas.md). A delta's tag names the competency the
# lesson sharpens; the spec filename is where it lands. `learn` writes the tag from the lens.
LENS_COMP = {"domain": "DDD", "system": "SDD", "experience": "UDD", "quality": "TDD", "method": "ADD"}
# The lens ↔ the letter its delta ids carry. The id is scoped to its FILE — the concept address
# is `/specs/<lens>.md#<id>` — so the letter is a mnemonic and the FILE is what disambiguates.
LENS_ID = {"domain": "D", "system": "S", "experience": "X", "quality": "Q", "method": "M"}

DELTA_ARROW = "\u2192"          # U+2192; round-trips through read/write as UTF-8 (probed at direction)
DELTA_STATUSES = ("open", "folded", "rejected")
DELTA_TERMINAL = ("folded", "rejected")   # a terminal status CLOSES the validity interval
# Fragment-safe: the id becomes the `#fragment` of `/specs/<lens>.md#<id>`, so no space, dot or
# punctuation may appear in it. FORMAT §3.3's third resolution form reads a delta id through
# `parse_delta_head` and therefore through exactly this shape (`_delta_ids`) — which is why the
# grammar is stated in the frozen contract and not only in this regex.
DELTA_ID = re.compile(r"\A[A-Za-z][A-Za-z0-9_-]*\Z")
DELTA_DATE = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")
# Every code `deltas()` can put in its malformed report. Enumerated HERE, once: the doc guard reads
# this tuple rather than a hand-kept list, because a second copy of one truth is the defect
# `_oneline` recorded. deltas.md documents every member.
DELTA_REJECTS = ("unparsed", "unknown_status", "unknown_competency", "no_evidence",
                 "bad_id", "bad_date", "bad_interval", "open_carries_close")

# The head is everything inside the brackets; group(2) is an OPEN tail. It stays open deliberately,
# and its reason is now the persona-target hint that already rides it (M11): an anchored tail would
# report every live line carrying a trailing clause `no_evidence`.
#
# The original reason was a PREDICTION — that `typed-relations` would append a `(refines: ...)`
# clause here — and that prediction did not hold: relations landed in FRONTMATTER, because a
# derived index read back as authority breaks law 1 and `doctor --sync` may not write an authored
# node (R:SYNCAUTHORED). The tolerance and its check are kept on the merits above; the stale
# reason is corrected rather than left to be trusted (an engine change invalidates PROSE).
DELTA_LINE = re.compile(r"-\s+\[([^\]]*)\]\s*(.*)")
# A line that LOOKS like a delta — so a plain markdown checkbox is never mistaken for a broken one,
# while a one-field head carrying a real competency tag IS reported rather than skipped.
DELTA_SHAPE = re.compile(r"-\s+\[(?:[^\]]*·[^\]]*|"
                         + "|".join(sorted(LENS_COMP.values())) + r")\]")
# `(evidence: <ptr>)` with something real inside — the template `<ref>` and an empty pointer
# both read as absent, the same discrimination `R:HOLLOW_EXPLORE` makes on a finding. A SEARCH,
# never a match: the clause need not close the line.
DELTA_EVIDENCE = re.compile(r"\(evidence:\s*[^)\s<][^)]*\)")


def parse_delta_head(head: str) -> dict:
    """Read one delta head — the text INSIDE the brackets. `{comp, id, status, valid_from,
    valid_to, code}`, where `code` is None when the head is well formed.

    ONE parser: `deltas()`, `fold()` and the migration all read through here, so the grammar has
    a single home. Dispatch is on the COUNT of `·`-separated fields, never on their shape — two
    fields is the LEGACY head, four is the dated head, anything else is `unparsed`. Shape dispatch
    would send a four-field head with a broken id to `unparsed` and leave `bad_id` a code no
    producer could emit, which is a reject code that names nothing.
    """
    out = {"comp": None, "id": None, "status": None,
           "valid_from": None, "valid_to": None, "code": None}
    fields = [f.strip() for f in str(head).split("·")]
    if len(fields) == 2:                       # LEGACY: `[ADD · open]` — read forever (M6)
        out["comp"], out["status"] = fields
        interval = None
    elif len(fields) == 4:                     # dated: `[ADD · M12 · open · 2026-08-11]`
        out["comp"], out["id"], out["status"], interval = fields
    else:
        out["code"] = "unparsed"
        return out
    if out["status"] not in DELTA_STATUSES:
        out["code"] = "unknown_status"
        return out
    if out["comp"] not in LENS_COMP.values() and out["comp"] not in LENS_COMP:
        out["code"] = "unknown_competency"
        return out
    if out["id"] is not None and not DELTA_ID.match(out["id"]):
        out["code"] = "bad_id"
        return out
    if interval is not None:
        ends = [e.strip() for e in interval.split(DELTA_ARROW)]
        if len(ends) > 2:
            out["code"] = "unparsed"
            return out
        if any(not DELTA_DATE.match(e) for e in ends):
            out["code"] = "bad_date"
            return out
        out["valid_from"] = ends[0]
        if len(ends) == 2:
            # An `open` delta is still carried; a close date on it is a contradiction, and it
            # gets its OWN code because the code is the whole message the author receives.
            if out["status"] not in DELTA_TERMINAL:
                out["code"] = "open_carries_close"
                return out
            if ends[1] < ends[0]:
                out["code"] = "bad_interval"
                return out
            out["valid_to"] = ends[1]
    return out


class Delta(tuple):
    """One carried lesson: `(spec, comp, text)` — with `.id`, `.valid_from`, `.valid_to` riding
    as attributes.

    A three-element tuple deliberately. `cli.py` and four pre-existing suites unpack exactly
    three inside comprehensions (`for _, _, t in items`), and a wider tuple would edit the BODIES
    of the suites this change must prove untouched. Equality and hash stay the tuple's, so the id
    is metadata and never identity — two deltas differing only in id still compare equal, which
    is what keeps every existing comparison meaning what it meant.
    """
    def __new__(cls, spec, comp, text, did=None, valid_from=None, valid_to=None):
        obj = super().__new__(cls, (spec, comp, text))
        obj.id, obj.valid_from, obj.valid_to = did, valid_from, valid_to
        return obj

    def __repr__(self):                       # the inherited tuple repr hides the id and every
        return (f"Delta({self[0]!r}, {self[1]!r}, {self[2]!r}, "   # debug print then lies by
                f"id={self.id!r}, valid_from={self.valid_from!r}, "  # omission
                f"valid_to={self.valid_to!r})")


def joined_deltas(body) -> dict:
    """`{index of a delta's head line: the whole delta's text}` — the grammar's own unit.

    deltas.md: "a long learning may wrap onto continuation lines — they join into ONE delta".
    Every reader was per-physical-line, so a wrapped tail carried a prevention the fold rung could
    not see (sixth T2 refute, E17) and the lister called the grammar's own wrap malformed while
    the counter counted it (seventh T2 refute, E19). One unit, one answer. Takes a body or its
    lines; the keys are indices into those lines, so a caller can retag the head it matched.
    """
    lines = live_lines(body)
    return {head: " ".join(str(lines[i]).strip() for i in idx)
            for head, idx in delta_spans(lines).items()}


def delta_spans(body) -> dict:
    """`{index of a delta's head line: the indices of EVERY line the grammar joins into it}` — the
    ONE reader of which lines belong to a delta.

    `joined_deltas` answers what a delta SAYS; this answers which lines it HOLDS, and a second
    walk would be a second reader of one fact. The membership is what `orphan_tail` needs (E47).
    """
    lines = live_lines(body)
    out, head = {}, None
    for i, line in enumerate(lines):
        stripped = str(line).strip()
        if DELTA_LINE.match(stripped):
            head, out[i] = i, [i]
        # ANY whitespace indents a continuation — an NBSP-indented tail once dropped out of the
        # unit entirely and the escape folded at exit 0 (tenth T2 refute's sibling, E23).
        elif head is not None and stripped and str(line)[:1].isspace():
            out[head].append(i)
        else:
            head = None
    return out


def orphan_tail(body) -> str:
    """The first line that carries an escape's TAIL but belongs to no delta, or `""`.

    A9: a line-boundary character is whitespace AND a split, so indenting a continuation with one
    severs the tail from its head — the head stops being an escape, and it folds at exit 0 beside
    a dangling prevention while `deltas` still prints the tail. No reader can rejoin what the text
    itself splits, so the refusing reading wins (M2): a tail that belongs to no delta is a
    MALFORMED delta, not prose (thirty-third T2 refute, E47).
    """
    lines = live_lines(body)
    # The WRITER's own answer to where the deltas are (`heading_index`), so the reader that refuses
    # and the writer that appends never disagree about the span (E38). Outside it, a tail clause is
    # prose a spec is entitled to write about itself (A10).
    start = heading_index(lines, "deltas")
    if start < 0:
        return ""
    end = next((j for j, (_, level, _) in enumerate(_headings(lines))
                if j > start and level == 2), len(lines))
    held = {i for idx in delta_spans(lines).values() for i in idx}
    for i in range(start + 1, end):
        text = str(lines[i]).strip()
        if i not in held and TAIL_MARK.search(mask_spans(text)):
            return text
    return ""


def open_delta_count(body: str) -> int:
    """How many deltas in a spec body are still OPEN. The ONE oracle behind the counter.

    Reads through `parse_delta_head` like every other consumer, over the same joined unit, and
    applies the SAME predicate `fold` applies when it decides what to retag — so the number
    `status` reports and the set `fold` acts on can never disagree by construction. A malformed
    head (`code` set) is not counted: it is a `doctor` finding of its own, and counting it would
    put an unreadable line into a total a human is asked to drain.
    """
    n = 0
    for text in joined_deltas(body).values():
        m = DELTA_LINE.match(text)
        if m:
            rec = parse_delta_head(m.group(1))
            if rec["code"] is None and rec["status"] == "open":
                n += 1
    return n


def declared_open_deltas(fm: dict):
    """The `open_deltas:` a Spec DECLARES, or None for absent-or-unreadable.

    None is UNKNOWN and never zero (R:UNKNOWNCLEAN). This corpus already records what a silent
    default costs — `_as_date` refuses one for the same reason — and here the cost is exact:
    every bundle written before this key existed would report a clean board over an open pile.
    """
    raw = (fm or {}).get("open_deltas")
    if isinstance(raw, bool) or raw is None:
        return None
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError):
        return None


def _delta_letter(lens: str) -> str:
    return LENS_ID.get(lens) or (str(lens)[:1].upper() or "X")


def _delta_ids_in(lines) -> list:
    """Every id already spelled in these body lines — the floor no mint may land on."""
    out = []
    for raw in live_lines(lines):
        m = DELTA_LINE.match(str(raw).strip())
        if m:
            did = parse_delta_head(m.group(1))["id"]
            if did:
                out.append(did)
    return out


def _delta_high_water(raw_fm: str, lines) -> int:
    """The largest integer any id in this spec has ever carried.

    `max(frontmatter delta_seq, the largest id in the body)`. Both terms are load-bearing:
    `delta_seq` survives deleting the highest delta (an id is an address and must never be
    reused), and the body term catches an id `join` merged in — `_union_into_deltas` writes back
    MAIN's frontmatter, so an incoming stream's counter is discarded at every join.
    """
    high = 0
    seq = re.search(r"^delta_seq:\s*(\d+)\s*(?:#.*)?$", str(raw_fm), re.M)
    if seq:
        high = int(seq.group(1))
    for did in _delta_ids_in(lines):
        tail = re.search(r"(\d+)\Z", did)
        if tail:
            high = max(high, int(tail.group(1)))
    return high


PREVENTION_KINDS = ("check", "monitor", "method", "rule")
# Kind-agnostic on purpose: a malformed kind, arrow or ref is READ and refused, never skipped
# (third T2 refute, E13 — a kind-anchored reader let `alert → …` degrade to "no prevention").
# The LABEL is read case-insensitively — `· Prevention:` is a malformed clause, not an absent
# one (E13 one level up) — while the KIND stays case-sensitive, as E13 binds it.
PREVENTION_TAIL = re.compile(r"·\s*prevention\s*:\s*([^·\n]*?)\s*(?=·|$)", re.M | re.I)


CODE_SPAN = re.compile(r"`[^`\n]*`")
# A marker is a marker however it is punctuated: `· escape:` once degraded to not-an-escape
# and folded beside a dangling prevention — E13's defect one level up (ninth T2 refute, E21).
# And however it is CASED: `re.I` here and nowhere else made `· Escape` not-an-escape while the
# clause one level down read `· Prevention:` as malformed, so one byte folded a dangling escape
# and bound a decision at exit 0 (thirty-third T2 refute, E47). Every site that asks "is this a
# marker" — the reader, `learn`'s value guard, `--bind`'s — asks THIS object, or the tail-forgery
# guards go one way and the rung the other (E14, A8).
ESCAPE_MARK = re.compile(r"·\s*escape\b", re.I)

# An escape's TAIL: what a delta's continuation CARRIES, wherever in the line it falls. Anchoring
# this at `^` enumerated the shape the read that named it produced — a wrap immediately before
# `· escape` — so wrapping one word earlier, the shape E17 blesses, left the orphan starting with
# a word and the head folded at exit 0 (thirty-fourth T2 refute, E48). Read inside `## Deltas` and
# nowhere else (A10), so prose that MENTIONS a clause blocks no fold.
TAIL_MARK = re.compile(r"·\s*(?:escape\b|prevention\s*:|why-missed\s*:)", re.I)


def balance_spans(value: str) -> str:
    """`value` with an unpaired backtick closed, so its code spans can never pair with a NEIGHBOUR's.

    `learn` interpolates several values into one delta and masks each ALONE; the reader masks the
    whole line. One stray backtick in the lesson and one in the why-missed therefore paired across
    the boundary in the reader's view and swallowed the engine's own `· escape` marker — the tail
    was written, printed by `deltas`, and invisible to the rung (eighth T2 refute, E20). Balanced
    values make the two views the same view, the way E15 makes every value one physical line.
    """
    value = str(value)
    return value + "`" if value.count("`") % 2 else value


def mask_spans(text) -> str:
    """`text` with the INSIDE of every backticked span replaced character-for-character by `x`.

    Length-preserving, so an offset into the mask is an offset into the original. Quoting the
    grammar in a code span is how prose writes ABOUT it, and the writer and the reader must agree
    on that or one refuses what the other blessed (seventh T2 refute, E18).
    """
    return CODE_SPAN.sub(lambda m: "`" + "x" * (len(m.group(0)) - 2) + "`", str(text or ""))


def _prevention_of(text: str):
    """The prevention clauses of an ESCAPE's tail — the text from the `· escape` marker on — as a
    list of `(kind, ref, ok)`; None when the delta is not an escape.

    Anchored on the MARKER, never on an evidence clause, and read through ONE view of the text: `learn` writes `· escape` and refuses it
    inside the lesson and inside the evidence, so in a delta the engine wrote it appears once and
    is the engine's own. Keying on the LAST `(evidence:` let a continuation line open a second
    evidence channel and push the tail out of view (seventh T2 refute, E18). A plain lesson
    quoting the grammar is never an escape (E9); an escape with no clause at all returns
    `[("", "", False)]`, because a missing prevention is not "no prevention" (E13).
    """
    raw = str(text or "")
    # An odd backtick count says the spans do not pair as written — a hand edit the writer never
    # balanced. The RAW view is then the one that REFUSES, and it decides every clause, not only
    # the marker: a stray backtick AFTER the marker masked one clause of several and the delta
    # folded beside a dangling ref (twelfth T2 refute, E25). `learn` balances what it writes, so
    # an even count is the author's own pairing and a clause inside a closed span is prose (E18).
    view = raw if raw.count("`") % 2 else mask_spans(raw)
    if ESCAPE_MARK.search(view) is None:
        return None
    # The marker GATES the read; it does not bound it. Scanning from `mark.start()` made the
    # clause's POSITION decide whether it counts, so one written before the marker — which
    # `--evidence` could put there — was folded past unread, and a resolving one written before it
    # was reported absent (ninth T2 refute, E21). A5: the reader looks for `prevention:` anywhere
    # in the delta, never at a position; M2: every clause it finds must resolve.
    out = []
    for hit in PREVENTION_TAIL.finditer(view):
        clause = raw[hit.start(1):hit.end(1)].strip()
        m = re.match(r"(check|monitor|method|rule)\s*(?:→|->)\s*(\S.*)$", clause)
        # A label with nothing after it is a clause the author WROTE: reporting it as no
        # clause at all names the wrong thing to fix (thirteenth T2 refute, E26).
        out.append((m.group(1), m.group(2).strip(), True) if m
                   else (clause or "<nothing after the label>", "", False))
    return out or [("", "", False)]


AUTHORED_SECTIONS = ("RULES", "ASSUMPTIONS", "EDGES", "CHECKS", "OBSERVES", "FINDINGS", "PLAN")

FENCE_RUN = re.compile(r"(`{3,}|~{3,})(.*)$")
LIST_MARKER = re.compile(r"(?:[-*+]|\d{1,9}[.)])\s+")


def _block_at(line: str) -> tuple:
    """`(quote depth, indent in COLUMNS, the text, carried by a list marker)` — the container a
    markdown line sits in.

    A fence is a BLOCK, not a line shape: its closer must sit in the same container, and its own
    content may quote a run without ending it. Matching shapes let an indented run close a fence
    early and left a blockquoted fence open forever (fifteenth T2 refute, E28); measuring indent in
    characters, and reading a list marker as mere indentation, let the fence's own content close it
    (seventeenth T2 refute, E31). A tab is four columns, as every markdown reader counts it.
    """
    i, depth = 0, 0
    while i < len(line):
        j = i
        while j < len(line) and line[j] in " \t":
            j += 1
        if j < len(line) and line[j] == ">":
            depth, i = depth + 1, j + 1 + (1 if line[j + 1:j + 2] == " " else 0)
            continue
        break
    rest, indent, listed = line[i:], 0, False
    while True:
        while rest[:1] in (" ", "\t"):
            indent, rest = (indent + 4 - indent % 4 if rest[0] == "\t" else indent + 1), rest[1:]
        m = LIST_MARKER.match(rest)
        if not m:
            return depth, indent, rest, listed
        indent, rest, listed = indent + m.end(), rest[m.end():], True


# `##` then whitespace or nothing — a heading that NAMES nothing still ends the section it
# follows, and a bare `## ` matching no branch let the walker inherit the previous section's
# authoring state (twenty-first T2 refute, E35). `###` is a sub-heading and opens nothing.
HEADING_LINE = re.compile(r"(#{1,6})(?:[ \t]+(.*?))?\s*$")


def _headings(body: str):
    """`(line, heading level, heading text)` for every line — the ONE reader of what an ATX heading
    IS: fence-masked, at document level, within three columns, level 0 when the line is not one.

    Both the authoring walker and `_section` read through here. Each deciding for itself was the
    *two readers of one fact* shape: `_section` saw a heading inside a fenced example and opened a
    section for a prevention to bind, where the authoring walker refused the very same fence
    (twenty-second T2 refute, E36).
    """
    # A LIST is walked as the caller split it: rebuilding it with `"\n".join(rstrip("\n"))` lost
    # every other line boundary Python knows (\x0b \x0c \x1c \x1d \x1e \x85 \u2028 \u2029), so one such
    # character re-split a line, every index the walkers hand back shifted by one, and `learn`
    # spliced a head between a wrapped escape and its continuation (thirty-second T2 refute, E46).
    lines = (str(body or "").splitlines() if isinstance(body, str)
             else [(str(line).splitlines() or [""])[0] for line in body])
    fence = None
    for line in lines:
        depth, indent, rest, listed = _block_at(line)
        run = FENCE_RUN.match(rest)
        # A fence lives inside the block that opened it: when the blockquote carrying it ends, so
        # does the fence — no closer needed, and the rules after it are authored again (E29).
        if fence and depth < fence[0]:
            fence = None
        if fence:
            # The closer: the same container — a line that opens a list item opens a BLOCK and
            # closes nothing — the same character, at least as long, alone on its line, and
            # indented no more than three columns past its opener. Anything else is content.
            if (run and depth == fence[0] and not listed and indent <= fence[1] + 3
                    and run.group(1)[0] == fence[2][0] and len(run.group(1)) >= len(fence[2])
                    and not run.group(2).strip()):
                fence = None
            yield line, -1, None
            continue
        if run and not (run.group(1)[0] == "`" and "`" in run.group(2)):
            fence = (depth, indent, run.group(1))
            yield line, -1, None
            continue
        # An ATX heading opens a section only at DOCUMENT level, at up to three columns of indent.
        # One inside a blockquote or a list item is QUOTED: it opened the authoring section back
        # up, and an id under `## LESSONS` folded an escape and bound a decision (E29).
        head = HEADING_LINE.match(rest) if not (depth or listed) and indent <= 3 else None
        yield (line, len(head.group(1)), (head.group(2) or "").strip()) if head else (line, 0, None)


def live_lines(body) -> list:
    """The node's lines with every FENCED line blanked — the ONE view of what text a node LIVES.

    A fence quotes; it never authors. `_authored_rules` held that for rule ids, but `resolve`'s
    THIRD fragment form read the raw body, so the same fence that refused a quoted `- E9` handed
    over the quoted delta id beside it and the escape folded and bound a decision — and `deltas`
    listed that example as a real open delta for a human to drain (twenty-third T2 refute, E37).
    Takes a body or its lines and returns one line per input line, so an index still addresses the
    caller's own line.
    """
    return ["" if level < 0 else line for line, level, _ in _headings(body)]


def unreadable_spec(node) -> str:
    """Why a writer cannot land a line in this spec, or None — the ONE reader of that question.

    Three writers learned it one at a time: `learn` (E41), `fold --bind` (E42) and the merge, which
    carries an escape BETWEEN bundles and had no guard at all — it filed a stream's refused escape
    under a fence that never closes at exit 0, where no reader could see it (twenty-ninth T2
    refute, E43). Asked BEFORE the write, because a join that refuses after copying a node is the
    partial merge R:PHANTOMSTREAM forbids.
    """
    if node["raw"] is None:
        return "it has no frontmatter the engine can read (a byte-order mark before the `---` hides it)"
    # A fence still open at EOF blinds every reader past it. The sentinel is a line that can open
    # no fence and name no heading, so it comes back masked only when one is still open.
    if live_lines(str(node["body"]).rstrip("\n") + "\n·")[-1] == "":
        return "a fence in it never closes, and that blinds every reader past it"
    return None


def heading_index(lines, slug: str) -> int:
    """The index of the line that OPENS the `## <slug>` section, or -1 — the ONE way a WRITER finds
    where to write.

    E37 taught every reader to blank a fence and left the writers scanning raw lines, so `learn`
    wrote a new delta INSIDE a fenced example of the grammar: filed at exit 0 and thereafter
    invisible to `deltas`, `search`, `status` and `fold`, which is worse than folding unprevented
    — nobody is ever asked to drain it (twenty-fourth T2 refute, E38). A writer and a reader that
    disagree about where a section starts is the same *two readers of one fact* shape as ever.
    """
    for i, (_, level, name) in enumerate(_headings(lines)):
        if level == 2 and "-".join(re.findall(r"[a-z0-9]+", (name or "").lower())) == slug:
            return i
    return -1


def _authored_rules(body: str) -> str:
    """The sections of a node where a rule is AUTHORED, fenced blocks blanked, headings canonical.

    A prevention resolves to "a RULES/EDGES id whose line is AUTHORED" (M2), and an id merely
    SPELLED under `## LESSONS` — an engine-written view — or quoted inside a fence is neither: it
    named nothing anyone could fail on (tenth T2 refute's sibling, E23). The gate's own `rules_of`
    and `edges_of` read through here too, so "is this id authored" has ONE reader (E30) — and the
    heading it keeps is re-emitted at column zero, so `_section_of` slices what THIS walker
    recognised instead of deciding again for itself (seventeenth T2 refute, E31).
    """
    out, keep = [], False
    for line, level, name in _headings(body):
        # `##` alone opens or ends an authoring section: `###` is a sub-heading and `#` a title,
        # and both are CONTENT of the section they sit in (twenty-first T2 refute, E35). A fenced
        # line arrives here as level 0 with nothing kept — the walker already blanked its meaning.
        if level == 2:
            # A heading that names nothing authors nothing — and never raises: `add fold` must
            # exit a refusal or a record, never a traceback (E24).
            named = (name or "").strip(":;.,").split()
            keep = bool(named) and named[0].upper() in AUTHORED_SECTIONS
            # CANONICAL, not verbatim: `_section_of` matches a heading exactly, so re-emitting
            # `## RULES (frozen)` left `rules_of` and the gate seeing no Musts at all while the
            # fold rung resolved ids under it — the same heading, two readers (E31, E41).
            out.append(f"## {named[0].upper()}" if keep else "")
            continue
        out.append(line if (keep and level == 0) else "")
    return "\n".join(out)


def _prevention_resolves(root, ref: str) -> bool:
    """Does a prevention ref name something the bundle or the repo holds? A bundle address (a node,
    a frontmatter key, a heading, a delta id, or a RULES/EDGES id such as `#M3`) or a repo-relative
    file — a `::<name>` tail names a check inside the file and is not verified (A2)."""
    root = Path(root)
    ref = str(ref or "").strip()
    if ref.startswith("/"):
        graph = scan(root)
        cid, value, why = resolve(graph, ref)
        if why != "edge_unresolved":
            return True
        frag = ref.partition("#")[2].strip()
        node = graph.get(cid)
        if node and frag and re.fullmatch(r"(?:[MAEO]\d+|R:[A-Z0-9_]+|F\d+)", frag):
            # A RULES/EDGES id counts only when its line is authored — a template placeholder
            # `<…>` is a slot, not a rule anyone could fail on (E8).
            body = _authored_rules(read(node["path"], "T2")["body"])
            line = re.search(rf"^\s*-\s*{re.escape(frag)}\b(.*)$", body, re.M)
            # A `<…>` inside a backticked span is prose (the engine's own placeholder detectors
            # strip spans first; 92 live RULES/EDGES lines carry one — second T2 refute, E11).
            # …and it must SAY something: a bare `- M7` is the heading-that-names-nothing one
            # level down — an id anyone could cite and nobody could fail (twelfth T2 refute, E25).
            return (line is not None and line.group(1).strip(" :-\t") != ""
                    and not PLACEHOLDER.search(re.sub(r"`[^`]*`", "", line.group(1))))
        return False
    # A FILE, never a path that merely exists: `.`, a directory, or an empty part before `::`
    # is the check-that-passes-on-nothing shape (T2 refute, E8) — and it lies INSIDE the repo:
    # a path that escapes the root through `..` names nothing the repo holds (E12).
    file_part = ref.split("::", 1)[0].strip()
    if not file_part:
        return False
    repo = root.parent.resolve()
    try:
        target = (repo / file_part).resolve()
        return target.is_file() and repo in target.parents
    except (ValueError, OSError):
        # A path the filesystem itself refuses to look at (an embedded NUL, a name too long) names
        # nothing the repo holds — and a refusal is the answer, never a traceback (E24, E42).
        return False


def _names_an_open_escape(root, ref: str) -> bool:
    """Does `ref` address a delta that is itself an OPEN escape? Then it binds nothing.

    The self-naming case is the obvious one; a two-cycle — each escape naming the other's id —
    binds exactly as much, and folded both at exit 0 (twelfth T2 refute, E25).
    """
    # Split and strip BOTH sides of the `#` exactly as `resolve` does — a second regex of its own
    # admitted no whitespace where `resolve` admits it, so `/specs/method.md# M1` resolved for the
    # ref rung and was invisible to this one, and an escape prevented itself (thirteenth T2
    # refute, E26). Two readers of one address must read it the same way.
    head, sep, frag = str(ref or "").strip().partition("#")
    m = re.fullmatch(r"/specs/([^/#]+)\.md", head.strip()) if sep else None
    frag = frag.strip()
    if not m or not frag:
        return False
    path = Path(root) / "specs" / f"{m.group(1)}.md"
    if not path.is_file():
        return False
    for text in joined_deltas(read(path, "T2")["body"]).values():
        head = DELTA_LINE.match(text)
        if not head:
            continue
        rec = parse_delta_head(head.group(1))
        if rec["id"] == frag and rec["status"] == "open":
            return _prevention_of(head.group(2)) is not None
    return False


QUICK_MARK = re.compile(r"^\s*quick\s*:", re.I)
CLOSED_TASK_STATES = ("done", "dropped", "archived")


def _commit_paths(root, evidence: str):
    """The paths a commit changed, or None when this is not a commit the engine can read.

    Two verbs, both READ-ONLY (R:OUTWARD, E6): `rev-parse` decides whether the evidence IS a
    commit (`--verify -q <ev>^{commit}`), how it sits in the history (`<ev>^@` lists its parents,
    `--is-shallow-repository` says whether git holds that history at all) and where the bundle
    sits (`--show-prefix`); `diff-tree` says what the commit touched. Reading the SHAPE with
    `rev-parse` and not `rev-list` keeps the tripwire to the two verbs E6 enumerates.
    Recognition is git's, never a shape test — a receipt cid, a path and a line of prose are all
    things `rev-parse` declines, and a regex guessing at "looks like a sha" would eventually
    mistake one for the other in the direction that costs the lane its write.

    `_git` already returns None for a missing binary, a tree that is not a repo and a non-zero
    exit, so every flavour of "the engine cannot look" arrives here as one value (A8).
    """
    ev = str(evidence).strip()
    if not _git(root, "rev-parse", "--verify", "-q", f"{ev}^{{commit}}"):
        return None
    # `-z`, because `diff-tree` otherwise renders any path outside ASCII through `core.quotepath`:
    # `src/auth/tokén.py` arrives as the literal string `"src/auth/tok\303\251n.py"`, quotes and
    # octal escapes and all, and matches no pattern a human would write. `_changed_paths` reads
    # `-z` for this exact reason; a floor a non-ASCII filename walks through is not a floor.
    args = ["diff-tree", "--no-commit-id", "--name-only", "-r", "-z"]
    # How the commit sits in the history decides how it can be read at all, and the three shapes
    # need three answers (M1 reads THE COMMIT'S CHANGED PATHS; the flags are how, not what).
    parents = _git(root, "rev-parse", f"{ev}^@")
    if parents is None:
        return None
    parents = parents.split()
    rev = [ev]
    if len(parents) > 1:
        # A MERGE prints NOTHING at all with one argument: `diff-tree` has no single parent to
        # pick, so a merge that carried a sensitive path into the branch read as a commit that
        # changed no files and the lesson landed. A sensitive path arriving by merge is a
        # sensitive path arriving. Against the FIRST parent, though — `-m` unions the diff
        # against EVERY parent, and against any parent but the first that is what the OTHER
        # branch was BEHIND on, so merging a side branch forked before a sensitive path moved on
        # the trunk was refused naming a file the author never touched (E3, and A6's promise with
        # it) — the same shape `--root` broke on a shallow clone, one fix to the left. The first
        # parent is the branch the merge landed ON, so `diff(^1, merge)` is precisely what this
        # commit introduced, and it loses nothing: an OCTOPUS's first parent lacks every other
        # branch's contribution, so the one diff still carries them all.
        rev = [f"{ev}^1", ev]
    elif not parents:
        # Parentless is TWO shapes that git reports identically. A repo's genuine FIRST commit
        # needs `--root` or every path it introduced reads as untouched — and that is the commit
        # most likely to be someone starting a project by dropping their secrets in. A SHALLOW
        # clone's boundary commit is GRAFTED to look parentless, and `--root` there lists the
        # ENTIRE TREE: `git clone --depth 1`, which is what CI checks out by default, turned a
        # clean README-only commit into a refusal naming a file the author never touched. The
        # engine genuinely cannot see that commit's diff, and A8 says every flavour of "cannot
        # look" lands the lesson rather than blocking the lane on it (R:LANEBLOCKED).
        if _git(root, "rev-parse", "--is-shallow-repository") == "true":
            return []
        args.append("--root")
    out = _git(root, *args, *rev, strip=False)
    # …and into the BUNDLE's frame, through the one reader the working-tree walker also uses:
    # reusing A17's MATCHER without A17's FRAME is not "the engine's own match" (M2), and the six
    # checks that shipped green could not see it — every one built its bundle at the repo root,
    # where the two frames coincide by accident. From the bundle PARENT, not the bundle, because
    # `--show-prefix` run inside `.add/` reports one level too deep.
    # NUL-delimited, so each path is taken whole — a `.strip()` here would eat a leading or
    # trailing space a filename is entitled to carry. `^1` can repeat nothing, but an octopus
    # diff may name a path once; the first hit is what `quick_hit` reports either way.
    return _in_bundle_frame(Path(root).parent, [r for r in (out or "").split("\0") if r])


def _scoped_by_any(parent, graph: dict, path: str) -> bool:
    """Does ANY node — whatever its status — declare `scope:` that HOLDS `path`?

    Status-blind, unlike the OWNER half: an owner asks "whose contract is this, now", which only
    an open frozen Task can answer, while the floor asks "was this change routed at all", and a
    done node routed it just as surely as an open one.

    HOLDS, not merely matches: read through `_scope_holds`, the reader M2 names, because this
    answer stands the security floor down. `fnmatch` let `--scope '**'` disarm every sensitive
    path in the bundle while the node held no files at all.

    And frozen AT HUMAN AUTHORITY — floored by THIS floor. A freeze stamp alone buys nothing,
    because a freeze costs no human when A17 cannot see the entry: `authority_for` reads a scope
    entry with `_paths_touch`, where `_paths_touch('**/*', 'src/auth/**')` is False, so the
    interview never arms and a bare `add freeze` stamps `process` — while this function reads the
    SAME entry through the freshness set, where `**/*` holds every file in the tree. The one shape
    invisible to the human-authority gate was exactly the shape that holds everything, and four
    commands with no human anywhere took the sensitive floor down bundle-wide.

    The two readers still disagree. What changes is that the disagreement now fails CLOSED: a node
    A17 reads as `process` routes nothing, however wide its entry, so the only thing that can
    stand this floor down is a node this floor itself demanded a human for. Status stays blind (a
    done node routed its work as surely as an open one); the seal, and who signed it, do not.

    WHO SIGNED IT is a separate question from the computed floor, and reading only the floor left
    the disarm open one gate further left. `freeze` WRITES `authority: human` whenever the floor
    it computes is human — `claimed_authority(None, floor)` returns the floor, the default `--by`
    is `cli`, and `interview_gap` has nothing to put to a human when the author left no open
    decisions, which the author controls. So `add new Persona p --scope src/auth/token.py` then a
    bare `add freeze p` stamped `authority: human` with no person anywhere, and the floor stood
    down on it in two commands (2026-09-13, round seven). A `by:` string is still a claim — a
    notary cannot verify a person — but it is a DELIBERATE claim, and telling `human:<name>` from
    a default `cli` is the same line the ledger already draws everywhere else.
    """
    for cid, node in graph.items():
        fm = node.get("fm") or {}
        seal = _latest_scope_seal(node)
        if seal is None or not str(seal.get("by") or "").startswith("human:") \
                or str(seal.get("authority") or "") != "human":
            continue
        if authority_for(graph, cid) != "human":
            continue
        for entry in _scope_list(fm):
            if _scope_holds(parent, entry, path):
                return True
    return False


def quick_hit(root, graph: dict, paths: list, owners: bool = True):
    """`(kind, path, owner)` for the first path a quick commit had no business touching, or None.

    `kind` is `"sensitive"` (owner: the matching pattern) or `"scope"` (owner: the task cid).
    The floor is read FIRST and wins, because it is unstrikeable and outranks an owner (A5/A11) —
    a path that is both is reported as sensitive, which is the higher answer.

    `owners=False` reads the FLOOR alone (M1, M3). A floor cannot be gated by a prefix the author
    picks, so it reads every lesson; an OWNER is a routing hint, and `learn` takes a commit sha OR
    a task cid as evidence and never both, so a lesson written up about a Task's own work cites
    that Task's own commit — reading the owner half there would refuse the ordinary case.

    Both matchers are the ENGINE's own, not new ones: `_paths_touch` is what `authority_for` uses
    for A17, and `_scope_list` is what every scope reader uses. A second matcher here would be one
    more reader of one fact, which is the defect this milestone has spent six refutes on.
    """
    parent = Path(root).parent
    patterns = ((graph.get("/index.md", {}).get("fm") or {}).get("sensitive_paths")) or []
    for path in paths:
        for pattern in (patterns if isinstance(patterns, list) else [patterns]):
            # …and no node of ANY status scopes it. The tripwire exists to catch a change with NO
            # node; a path some node already owns is a change that WAS routed, and there is nothing
            # left to size up. Without this the widened floor closed the prefix evasion and closed
            # the route for writing up security work with it: an `--escape` post-mortem ABOUT a
            # security fix necessarily cites that fix's commit, and a write-up of work a done Task
            # routed cites that Task's commit — both were refused and told to open a node for a
            # path a node already owned. A refusal an author cannot act on is one they route around.
            if _paths_touch(path, str(pattern)) and not _scoped_by_any(parent, graph, path):
                return "sensitive", path, str(pattern)
    if not owners:
        return None
    # OPEN and FROZEN only (M2, A2): a done task's scope is history, and an unfrozen task's scope
    # is a draft nobody sealed — neither owns anything a quick commit could be trespassing on.
    for cid in sorted(graph):
        fm = (graph[cid].get("fm") or {})
        if fm.get("type") != "Task" or str(fm.get("status") or "") in CLOSED_TASK_STATES:
            continue
        if _latest_scope_seal(graph[cid]) is None:
            continue
        for entry in _scope_list(fm):
            for path in paths:
                # The SAME reader the floor exemption uses, and the one M2 names. If these two
                # ever diverge, both halves can fire on one path and A5's disjointness — which is
                # what makes the corrected ordering true — quietly stops holding.
                if _scope_holds(parent, entry, path):
                    return "scope", path, cid
    return None


def learn(root, lens: str, lesson: str, evidence: str = None, escape: bool = False,
          why_missed: str = None, prevention: str = None) -> tuple:
    """Append a lesson to a spec's `## Deltas` in the frozen delta grammar, `open` by default.

    Grammar (deltas.md): `- [<COMPETENCY> · <ID> · open · <valid-from>] <lesson> (evidence: <ptr>)`.
    The id is the concept address a typed relation can target; the date opens the validity
    interval `fold` later closes. Both come from the engine — there is no parameter through which
    a caller could supply either. Evidence is required, not decorative — a lesson with no evidence
    is an opinion, and a spec full of opinions is the thing this method exists to replace. `open`
    is the only status `learn` writes; a human moves it to `folded`/`rejected` (the AI never
    self-consolidates).
    """
    # Presence, never truthiness: an empty value is a flag the caller GAVE, and the engine's own
    # reader reports an empty evidence clause as `no_evidence` — the writer must not emit one
    # (fifth T2 refute, E16).
    if not str(evidence or "").strip():
        return None, "refused: a lesson needs evidence — cite the receipt or decision that caused it"
    # A delta is ONE physical line and its code spans close inside the value they open in: every
    # reader of the tail is line-based (E15) and masks spans over the WHOLE line (E20), so the
    # writer guarantees both here, before its own guard reads what it wrote.
    lesson = balance_spans(" ".join(str(lesson).split()))
    evidence = balance_spans(" ".join(str(evidence).split()))
    # The marker is the ENGINE's: it cannot ride in through a flag the tail reader later trusts —
    # not the evidence (E14), and not the lesson, which the joined unit made readable too (E18).
    # Inside a `code span` it is prose, exactly as the reader reads it.
    for flag, value in (("--evidence", evidence), ("the lesson", lesson)):
        # `(evidence:` is the grammar's own too — the tail reader keys on it and `_delta_identity`
        # splits a lesson at it, so two genuinely different lessons carrying one collapsed into a
        # single false conflict and `join` dropped both refused escapes (twenty-sixth T2 refute,
        # E40). It was refused in `--why-missed` and the ref (E10) and nowhere else.
        if "(evidence:" in mask_spans(value):
            return None, ('cannot file the lesson — `(evidence:` is the grammar\'s own marker and cannot ride '
                           f'inside {flag} (quote it in a `code span` to write about it) -> "R:UNCAUSED"\n'
                           f'next: add learn {lens} "<lesson>" --evidence <ref>')
        if ESCAPE_MARK.search(mask_spans(value)):
            return None, ('cannot file the lesson — `· escape` is the grammar\'s own marker and cannot ride inside '
                          f'{flag} (an escape is filed with --escape; quote it in a `code span` to write about it) '
                          f'-> "R:UNCAUSED"\nnext: add learn '
                          f'{lens} "<lesson>" --evidence <ref> [--escape --why-missed "…" --prevention "<kind> → <ref>"]')
    # quick-lane-tripwire: the direct lane's ONE bundle write is where the engine can finally look.
    # intake.md routes a small change to the direct lane on the author's own judgement and says the
    # floor is checked FIRST and always wins — and nothing enforced that, so a `quick:` commit into
    # a sensitive path or a frozen scope left no node, no contract and no receipt. Read before the
    # write (A9), so a refused quick line writes nothing at all; and never a default-deny — a
    # bundle that declares no sensitive paths and owns no open scope is a bundle saying there is
    # nothing here to trespass on (A10).
    # The FLOOR reads every lesson; the OWNER half reads the `quick:` line alone (M1, M3, E5). A
    # floor is unstrikeable, so a prefix the author picks cannot gate it — and the refusal used to
    # END by recommending that prefix be dropped, which made "drop `quick:`" the one-token evasion
    # this control advertised to the very people it exists for. An owner is a routing hint, and
    # `learn` takes a commit sha OR a task cid and never both, so a write-up of a Task's own work
    # cites that Task's own commit: reading the owner half there would refuse the ordinary case.
    paths = _commit_paths(root, evidence) if evidence else None
    if paths:
        # The lane is NEVER blocked on the engine's own inability to look (R:LANEBLOCKED, A8): no
        # repo, no git, an unreadable sha and evidence that is simply not a commit all read as
        # "nothing to inspect", and the lesson lands exactly as it did before this rung existed.
        hit = quick_hit(root, scan(root), paths, owners=bool(QUICK_MARK.match(lesson)))
        if hit:
            kind, path, owner = hit
            why = (f"`{path}` matches the sensitive pattern `{owner}` — floor human"
                   if kind == "sensitive" else
                   f"`{path}` lies under {owner}'s frozen `scope:` — that contract owns it")
            # A MERGE says so, because the author probably did not write that path: `git pull` is
            # the ordinary way a colleague's sensitive commit arrives on your branch, and no
            # `diff-tree` flag tells a pull from merging your own work (`-c` reports nothing for
            # either, which is how the carry went unseen to begin with). The detection stays; the
            # ADVICE is what has to be true. A6's own cost-if-wrong is the author dropping the
            # `quick:` prefix, so a refusal that CLOSES on that recommendation teaches the bypass
            # to exactly the people this control exists for — it is named as the lesser route,
            # never as the last word.
            merged = len((_git(root, "rev-parse", f"{str(evidence).strip()}^@") or "").split()) > 1
            arrived = ("the merge it cites brought in" if merged else "the commit it cites touched")
            # Every route named must be one the author can actually take, and none of them is the
            # prefix (M6). The clause that used to sit here recommended dropping `quick:` — which
            # WORKED on an owner hit, handing out the bypass inside the message that refused it,
            # FAILED on a floor hit, and read as a no-op for a lesson that never carried a prefix.
            # Each half names the `next:` that WORKS for it, and the other route as the aside.
            # `add new Task --scope <path>` is the route where no node owns the path — run against
            # the task that already owns it, it creates a colliding node and lands the author back
            # on a byte-identical refusal. M6: every route named must be one they can take.
            if kind == "scope":
                nxt = f'next: add learn <lens> "<lesson>" --evidence {owner}'
                aside = (f"   (or add new Task <slug> --scope {path}, if this is separate work "
                         f"that contract does not own)")
            else:
                nxt = f"next: add new Task <slug> --scope {path}"
                aside = ("   (a merge carries what the branch was behind on — if that path is not "
                         "your change, the commit that made it is what needs the node, not this "
                         "merge)" if merged else
                         "   (then build it under that contract, and file this lesson against it)")
            return None, (f"cannot file the lesson — {arrived} {why}, and "
                          f"the floor is checked FIRST and always wins: a change there is a node, "
                          f'however small -> "R:QUICKSIZEUP"\n'
                          f"{nxt}\n{aside}")

    # escape-with-prevention: an escape carries its why-missed and a bound prevention, or it is
    # not filed — a sentence with no prevention is exactly what folded unprevented before.
    tail = ""
    if escape or why_missed is not None or prevention is not None:
        def uncaused(what: str) -> tuple:
            return None, (f'cannot file an escape — {what} -> "R:UNCAUSED"\nnext: add learn {lens} '
                          f'"quick|<lesson>" --evidence <ref> --escape --why-missed "<why the checks missed it>" '
                          f'--prevention "<check|monitor|method|rule> → <ref>"')
        if not escape:
            return uncaused("--why-missed and --prevention belong to an escape; pass --escape to file one")
        if not str(why_missed or "").strip():
            return uncaused("no --why-missed — an escape says why the checks did not catch it")
        if not str(prevention or "").strip():
            return uncaused("no --prevention — an escape binds what stops the next one")
        # Split on the FIRST arrow of either spelling; the ref keeps whatever follows as given (E7).
        # NON-greedy: `\S+` backtracked to the LAST arrow whenever no space separated them, so
        # `check->tests/x.py->tail` was refused by a message naming a kind nobody wrote — and the
        # spaced control is why the bound check missed it (twenty-eighth T2 refute, E42).
        m = re.match(r"\s*(\S*?)\s*(?:→|->)\s*(.*)$", prevention, re.S)
        kind, ref = (m.group(1), m.group(2).strip()) if m else (prevention.strip(), "")
        if kind not in PREVENTION_KINDS:
            return uncaused(f"prevention kind `{kind}` is not one of {'|'.join(PREVENTION_KINDS)}")
        if not ref:
            return uncaused(f"prevention `{kind} →` names no ref — a check id, a node address, a file")
        # The grammar reserves `·` as the tail's delimiter: inside a flag it would end the clause
        # early and let the reader name a ref nobody bound (T2 refute, E7).
        if "·" in str(why_missed) or "·" in ref:
            return uncaused("`·` is the tail's own delimiter — it cannot appear inside --why-missed or the prevention ref")
        # … and the reader keys the tail on the LAST evidence marker, so an author may not write
        # one either (second T2 refute, E10 — a dangling escape hid behind it and folded).
        if "(evidence:" in str(why_missed) or "(evidence:" in ref:
            return uncaused("`(evidence:` is the grammar's own marker — it cannot appear inside --why-missed or the prevention ref")
        # The ref is an address, never prose: a backtick in it would open a span over the rest of
        # the tail, and the clause the rung reads would be the one nobody wrote (E20).
        if "`" in ref:
            return uncaused("a backtick cannot appear inside the prevention ref — a ref is an address, not prose")
        # …and no control character: a NUL reached the filesystem through the resolver and raised
        # `ValueError: embedded null character`, where every exit is a refusal or a record (E42).
        # Whitespace is NOT a control character here: a line break in the ref is normalised to one
        # line, which E15 and E35 froze — only a character no reader can carry is refused.
        if any((ch < " " or ch == "\x7f") and not ch.isspace() for ch in ref):
            return uncaused("a control character cannot appear inside the prevention ref — a ref is an address")
        tail = (f" · escape · why-missed: {balance_spans(' '.join(str(why_missed).split()))}"
                f" · prevention: {kind} → {' '.join(ref.split())}")
    path = Path(root) / "specs" / f"{lens}.md"
    if not path.is_file():
        lenses = sorted(q.stem for q in (Path(root) / "specs").glob("*.md"))
        return None, (f"no such spec lens: {lens} — the vocabulary is closed: "
                       f"{' | '.join(lenses)}"
                       f"\nnext: add learn <{' | '.join(lenses)}> \"<lesson>\" --evidence <ref>")
    comp = LENS_COMP.get(lens, lens.upper())
    node = read(path, "T2")
    if node["raw"] is None:
        # No frontmatter the reader can find — a BOM before it is the commonest cause, and `set_key`
        # raised `AttributeError` on the None where `doctor` already reports `missing_frontmatter`.
        return None, (f'cannot file the lesson — specs/{lens}.md {unreadable_spec(node)} -> "R:UNREADABLE"'
                       f'\nnext: add doctor   (it names the file), then add learn {lens} "<lesson>" --evidence <ref>')
    lines = node["body"].splitlines(keepends=True)
    seq = _delta_high_water(node["raw"], lines) + 1
    did = f"{_delta_letter(lens)}{seq}"
    entry = f"- [{comp} · {did} · open · {_today()}] {lesson} (evidence: {evidence}){tail}\n"
    i = heading_index(lines, "deltas")
    if i >= 0:
        lines.insert(_delta_insert_at(lines, i), entry)
    else:
        lines += ["\n## Deltas\n\n", entry]
    # The counter rides in frontmatter through `set_key`, which replaces ONE scalar and leaves
    # every other byte — never re-emit the parsed mapping, which would drop comments and order.
    raw = set_key(node["raw"], "delta_seq", str(seq))
    # The counter rides the SAME write as the line it counts (A7). A second pass would make
    # drift the normal state rather than the exception, and `status` would be reporting a
    # number that is merely usually right. Recomputed, never incremented: the oracle is the
    # body, so a hand-edited spec self-corrects on the next `learn`.
    body = "".join(lines)
    # The writer READS BACK the line it just wrote, as `--bind` does (E39): the id `learn` hands
    # the author back must address the delta the readers read. A fence that never closes made
    # every reader blind past it, and both writer branches landed inside it — `deltas` said none,
    # `show` answered R:NOSUCHNODE for the id `learn` had just minted, and the engine wrote
    # `open_deltas: 0` itself (twenty-seventh T2 refute, E41). Asking the property, not the shape:
    # whatever hides the line, the lesson is refused rather than filed into the void.
    if _delta_ids(body).get(did) != entry.strip():
        return None, (f'cannot file the lesson — specs/{lens}.md would not be readable at the line: '
                       f'`{did}` is not addressable in what the write produces (a fence that never closes '
                       f'blinds every reader past it) -> "R:UNREADABLE"'
                       f'\nnext: close the fence in specs/{lens}.md (add doctor names it), then add learn '
                       f'{lens} "<lesson>" --evidence <ref>')
    raw = set_key(raw, "open_deltas", str(open_delta_count(body)))
    write(path, f"---\n{raw}\n---\n{body}")
    hint = ("" if re.search(r"tasks/[^/\s]+\.(md|d/)", str(evidence)) else
            "\n  (a lesson lands on a task's ## LESSONS at close when its evidence cites the "
            "task: --evidence /tasks/<slug>.md)")
    return True, f"recorded on specs/{lens} as {did}{hint}\nnext: add status"


ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _as_date(value):
    """An ISO `YYYY-MM-DD` string, or None when it is absent or unreadable.

    None means UNKNOWN — never epoch-zero and never today (R:TODAYFALLBACK). This corpus
    already records what a silent default costs: `.get(sens, "process")` turned every
    unrecognised sensitivity into the LOWEST authority floor, and an unknown read as clean.
    A date the engine cannot read is a date it does not have, and the listing says so.

    ISO dates compare correctly as strings — fixed width, most-significant first — so no
    parsing beyond the shape check is needed, and no timezone is implied.
    """
    v = (value or "").strip()
    return v if ISO_DATE.match(v) else None


def delta_address(stem: str, delta_id: str = None) -> str:
    """One lesson -> the ONE address every reader cites it by. `/specs/<stem>.md#<id>`.

    Both readers call here. They used to compose it apart — `search` at concept grain, `deltas`
    as a `[ADD X9]` tag that shows the id without making it pasteable — so a reader who found a
    lesson through the wrong door could not cite what they had just read (X4). A legacy head
    carries no id, so its address degrades to the FILE it lives in: the coarser grain still
    resolves, where an empty `#` fragment resolves to nothing.
    """
    cid = "/specs/" + str(stem) + ".md"
    return cid + "#" + str(delta_id) if delta_id else cid


def deltas(root, status: str = "open", lens: str = None,
           since: str = None, as_of: str = None) -> tuple:
    """List every delta at `status` across the five specs. `(items, note)`.

    A reader over the frozen grammar (deltas.md): `open` is the carried inventory the loop reads to
    propose the next tasks; `folded`/`rejected` are decided and stay out of the listing. Never mutates.
    """
    root = Path(root)
    if status not in DELTA_STATUSES:
        return [], (f"`{status}` is not a delta status — the set is closed: "
                    f"{' | '.join(DELTA_STATUSES)}"
                    f"\nnext: add deltas --status <{' | '.join(DELTA_STATUSES)}>")
    lenses = sorted(q.stem for q in (root / "specs").glob("*.md"))
    if lens is not None and lens not in lenses:
        return [], (f"no such spec lens: {lens} — the vocabulary is closed: "
                    f"{' | '.join(lenses)}"
                    f"\nnext: add deltas --lens <{' | '.join(lenses)}>")
    # M6/R:TODAYFALLBACK — an unreadable date argument REFUSES. Falling back to today would
    # answer a question nobody asked, and listing as though unfiltered would answer the
    # opposite one; both read as success.
    for flag, raw in (("--since", since), ("--as-of", as_of)):
        if raw is not None and _as_date(raw) is None:
            return [], (f"`{raw}` is not a date — {flag} takes ISO YYYY-MM-DD, the form the "
                        f"delta grammar writes"
                        f"\nnext: add deltas {flag} <YYYY-MM-DD>")

    items, malformed, undated = [], [], 0
    paths = [q for q in sorted((root / "specs").glob("*.md"))
             if lens is None or q.stem == lens]
    for path in paths:
        # The grammar's unit, not a physical line: a canonically wrapped delta was listed as
        # malformed while the counter counted it and `fold` read it — three answers about one
        # delta (seventh T2 refute, E19).
        for stripped in joined_deltas(read(path, "T2")["body"]).values():
            m = DELTA_LINE.match(stripped)
            # Not every `- [..]` line is a delta; only one that LOOKS like one and fails.
            if m is None or not DELTA_SHAPE.match(stripped):
                continue
            rec = parse_delta_head(m.group(1))
            tail = m.group(2)
            code = rec["code"]
            # `learn` always writes `(evidence: <ptr>)`; a hand-added line that omits it is
            # a claim with no proof, which is the third code deltas.md has always promised.
            if code is None and not DELTA_EVIDENCE.search(tail):
                code = "no_evidence"
            # A delta the engine cannot place is REPORTED; it is never silently dropped. A typo'd
            # status once matched no branch and the line simply disappeared — from the inventory the
            # loop reads to propose the next tasks, with no warning and no doctor finding.
            if code:
                malformed.append((path.stem, code, stripped))
            else:
                start, close = _as_date(rec["valid_from"]), _as_date(rec["valid_to"])
                # M5/M7 — a delta the engine cannot DATE is shown and counted under a time
                # filter, never dropped. A filter that hides what it cannot judge reports a
                # smaller number, and a smaller number reads as success (R:SILENT_DROP).
                unknown = (since is not None or as_of is not None) and start is None
                if unknown:
                    undated += 1
                    if rec["status"] != status:
                        continue
                elif as_of is not None:
                    # M3 — the status it HELD THEN. The interval is half-open [start, close):
                    # a delta closed ON the queried date was not asserted that day (M4/A3).
                    if start > as_of:
                        continue
                    held = "open" if (close is None or as_of < close) else rec["status"]
                    if held != status:
                        continue
                elif since is not None:
                    # M2/A2 — `--since` reads valid_from: when the lesson was FILED.
                    if start < since or rec["status"] != status:
                        continue
                elif rec["status"] != status:
                    continue
                items.append(Delta(path.stem, rec["comp"], tail.strip(),
                                   rec["id"], rec["valid_from"], rec["valid_to"]))
    # A6 — a narrowed listing must ANNOUNCE that it is narrowed, or a planner reads a filtered
    # inventory as the whole one.
    active = "".join([f" · lens {lens}" if lens else "",
                      f" · since {since}" if since else "",
                      f" · as of {as_of}" if as_of else ""])
    rendered = []
    if items:
        rendered.append(f"{status} deltas ({len(items)}){active}:")
        # The address leads beside the competency so a reader can cite a lesson without opening
        # the file; the raw four-field head would push the lesson itself off the line.
        # The address, not a `[ADD X9]` tag: the tag showed the id, this one can be pasted
        # into a `relations:` target. The competency letter is dropped as redundant — the path
        # already names the lens it stood for (X4).
        # Windowed through the SAME path `search` uses (R:SECONDWINDOW). These two verbs render
        # identical records; one was bounded and tested at 300 characters a line and the other
        # was bounded by nothing, at 409 bytes a row against 169. The ADDRESS is emitted whole:
        # it is the way back to the full text, which `show <lens>#<id>` now reads in ~600 bytes.
        rendered += [f"  · {delta_address(i[0], i.id)}  {_snippet(i[2], '')}" for i in items]
        rendered.append("next: at close, fold or reject each (loop.md)")
    else:
        rendered.append(f"no {status} deltas{active}")
    if undated:
        rendered.append(f"— {undated} undated delta(s) shown: a legacy or unreadable date is "
                        f"UNKNOWN, so the time filter cannot judge them and does not hide them")
    if malformed:
        rendered.append(f"! {len(malformed)} malformed delta line(s) — carried by nothing, "
                        f"read by nothing:")
        rendered += [f"  ! {s}: {why} — {text}" for s, why, text in malformed]
        rendered.append("next: fix the line's "
                        "`- [<LENS> · <ID> · open|folded|rejected · <valid-from>] <text>` shape")
    elif not items:
        rendered.append("next: add status")
    return items, "\n".join(rendered)


def _bind_decision(body: str, lens: str, sentence: str, ids: list) -> str:
    """Write one decision into `## Decisions that bind`, citing the lessons it came from.

    PREPENDED (A11): this corpus reads newest-first everywhere a sequence accumulates, and the
    foundation-compaction milestone already settled that question for `## Deltas`. The scaffold
    line is REPLACED rather than pushed down — a section holding one real decision and one
    template slot is still a section `_placeholder_only` would have to special-case, and every
    consumer that filters scaffolding would then need the same rule.

    No new grammar is declared: a `(from: …)` tail mirrors the `(evidence: …)` tail the delta
    line already carries, so `bind_sections`, `brief` and FORMAT are all untouched.
    """
    cite = ", ".join([delta_address(lens, ids[0])] + [f"#{i}" for i in ids[1:]]) if ids else ""
    entry = f"- {sentence.strip()}" + (f" (from: {cite})" if cite else "") + "\n"
    lines = body.splitlines(keepends=True)
    # The section is found the way `_section` — and therefore `brief` — finds it: level two, at
    # document level, never one quoted inside a fence. Deciding for itself made this a FOURTH
    # heading reader, so `--bind` reported "bound 1 decision" at exit 0 into a `###` section or a
    # fenced heading the brief could not see (twenty-fourth T2 refute, E38).
    found = heading_index(lines, "decisions-that-bind")
    start = found + 1 if found >= 0 else None
    if start is None:                        # A10: create it rather than refuse into a hand edit
        at = heading_index(lines, "deltas")
        if at >= 0:
            return "".join(lines[:at] + ["## Decisions that bind\n", "\n", entry, "\n"] + lines[at:])
        return "".join(lines + ["\n## Decisions that bind\n", "\n", entry])
    # One entry per line the caller split, because the walker reads that list itself: the rejoin
    # this replaced could come back SHORTER (a trailing empty line) or LONGER (any other line
    # boundary), and both mis-indexed — one raised IndexError, the other spliced a delta in half
    # (E45, E46).
    levels = [level for _, level, _ in _headings(lines)]
    end = next((j for j in range(start, len(lines)) if levels[j] > 0), len(lines))
    content = [j for j in range(start, end) if lines[j].strip()]
    if content and _placeholder_only("".join(lines[j] for j in content)):
        return "".join(lines[:content[0]] + [entry] + lines[content[-1] + 1:end] + lines[end:])
    at = content[0] if content else start
    return "".join(lines[:at] + [entry] + lines[at:])


def fold(root, lens: str, match: str, reject: bool = False, bind: str = None) -> tuple:
    """Retag the open delta(s) in `lens` whose text contains `match` as `folded`, CLOSING the
    validity interval at today. `(ok, note)`.

    Consolidation is the human's judgment (deltas.md) — the engine only records the status flip, and
    only on a human's call. A fold matching nothing refuses (R:NOMATCH) rather than silently no-op.

    A LEGACY undated head keeps its two-field shape: the engine does not know when that lesson was
    filed, and stamping today as its start would be a fiction. It records what it can and invents
    nothing. Ids retire in place — no fold ever renumbers a survivor, because a renumber silently
    re-points every relation that targets them.
    """
    if reject and bind:
        return None, ('R:REJECTBINDS — a lesson judged wrong cannot also be a decision that binds: '
                       '`--reject` retires it, `--bind` promotes it, and one call may do only one\n'
                       'next: add fold <lens> "<match>" --reject   (or --bind "<decision>")')
    if bind:
        # `--bind` writes into the spec exactly as `learn` does, so it obeys the same two laws: ONE
        # physical line, and the engine's own marker cannot ride in through a flag. A newline in
        # the sentence forged a real open escape at exit 0 — an unguarded delta writer beside the
        # guarded one (twenty-fourth T2 refute, A8, E38).
        bind = balance_spans(" ".join(str(bind).split()))
        # A decision its own readers disown is not written: `brief` renders the section
        # `unauthored="true"` and `doctor` calls it scaffold, and the next `--bind` discards it —
        # the writer refuses instead, naming the span rule E11 already froze (E40).
        if _placeholder_only(f"- {' '.join(str(bind).split())}"):
            return None, ('cannot bind the decision — every reader would call it scaffold: a bare `<…>` is the '
                           'template\'s own placeholder. Quote it in a `code span` to write about it '
                           f'-> "R:UNCAUSED"\nnext: add fold {lens} "{match}" --bind "<decision>"')
        if ESCAPE_MARK.search(mask_spans(bind)):
            return None, ('cannot bind the decision — `· escape` is the grammar\'s own marker and cannot ride '
                           'inside --bind (an escape is filed with `add learn --escape`; quote it in a `code span` '
                           f'to write about it) -> "R:UNCAUSED"\nnext: add fold {lens} "<match>" --bind "<decision>"')
    path = Path(root) / "specs" / f"{lens}.md"
    if not path.is_file():
        lenses = sorted(q.stem for q in (Path(root) / "specs").glob("*.md"))
        return None, (f"no such spec lens: {lens} — the vocabulary is closed: "
                       f"{' | '.join(lenses)}"
                       f"\nnext: add learn <{' | '.join(lenses)}> \"<lesson>\" --evidence <ref>")
    # ONE matcher, two verdicts. `rejected` has been in DELTA_STATUSES since the grammar was
    # frozen and no command could produce it, so the only honest way to retire a wrong lesson
    # was a hand edit — which the method forbids everywhere else. A separate code path would
    # let the two verdicts drift; the verdict is a word, and only the word changes.
    verdict = "rejected" if reject else "folded"
    node = read(path, "T2")
    why = unreadable_spec(node)
    if why:
        # `learn` got this guard and the rung this task is ABOUT did not: plain, `--reject` and
        # `--bind` all raised `AttributeError` at the write (E42's clause, E43's reach).
        return None, (f'cannot fold — specs/{lens}.md would not be readable at the line: {why} -> "R:UNREADABLE"'
                       f'\nnext: add doctor   (it names the file), then add fold {lens} "{match}"')

    whole = joined_deltas(node["body"])
    stray = orphan_tail(node["body"]) if not reject else ""
    if stray:
        return None, (f'cannot fold in specs/{lens}.md — `{stray[:60]}` carries an escape\'s tail but '
                      f'belongs to no delta: a line-boundary character is not an indent -> "R:UNPREVENTED"'
                      f'\nnext: join the tail back onto its delta with a space or a tab, '
                      f'then add fold {lens} "{match}"')
    # escape-with-prevention: an escape folds (or binds) only when its prevention resolves — read
    # over EVERY match first, so one dangling prevention refuses the whole call and nothing is
    # retagged (M3). `--reject` never reads it: a lesson judged wrong has nothing to prevent.
    if not reject:
        for text in whole.values():
            m = DELTA_LINE.match(text)
            if not m:
                continue
            rec = parse_delta_head(m.group(1))
            if rec["code"] is None and rec["status"] == "open" and match in m.group(2):
                for kind, ref, well_formed in (_prevention_of(m.group(2)) or []):
                    if not well_formed:
                        what = (f"its prevention clause `{kind}` is malformed — the form is "
                                f"`prevention: <check|monitor|method|rule> → <ref>`" if kind else
                                "its tail carries `· escape` but no `prevention:` clause")
                    elif _names_an_open_escape(root, ref):
                        # An escape still OPEN stops nothing, so naming one binds nothing: the
                        # lesson itself (E23), or a second escape naming this one back — a cycle
                        # that folded both at exit 0 (twelfth T2 refute, E25).
                        what = (f"its prevention `{kind} → {ref}` names an escape that is itself "
                                f"still open — a prevention binds something that STOPS the next one")
                    elif not _prevention_resolves(root, ref):
                        what = f"its prevention `{kind} → {ref}` resolves to nothing"
                    else:
                        continue
                    return None, (f"cannot fold `{rec['id'] or match}` — {what} -> \"R:UNPREVENTED\""
                                  f"\nnext: write the check|monitor|method|rule it names "
                                  f"(a node address like /tasks/<slug>.md#M1, or a repo file like tests/<file>::<check>), "
                                  f"then add fold {lens} \"{match}\"   (or --reject if the lesson did not hold)")
    out, folded, ids = [], 0, []
    for i, line in enumerate(node["body"].splitlines(keepends=True)):
        m = DELTA_LINE.match(whole.get(i, ""))
        if m:
            rec = parse_delta_head(m.group(1))
            if rec["code"] is None and rec["status"] == "open" and match in m.group(2):
                head = m.group(1)
                if rec["id"] is None:
                    closed = f"{rec['comp']} · {verdict}"
                elif rec["valid_from"]:
                    closed = (f"{rec['comp']} · {rec['id']} · {verdict} · "
                              f"{rec['valid_from']}{DELTA_ARROW}{_today()}")
                else:
                    closed = f"{rec['comp']} · {rec['id']} · {verdict}"
                line = line.replace(f"[{head}]", f"[{closed}]", 1)
                folded += 1
                if rec["id"]:
                    ids.append(rec["id"])
        out.append(line)
    if not folded:
        return None, f"R:NOMATCH — no open delta in {lens} matching '{match}'\nnext: add deltas"
    body = "".join(out)
    # A7: the retag and the decision land in ONE write, so a decision can never cite a lesson
    # the same call failed to retag.
    if bind:
        bound = _bind_decision(body, lens, bind, ids)
        # A8 asks ONE question, and the engine answers it by READING BACK what it is about to
        # write: does the sentence change what the spec's own readers see? `learn` writes its
        # bracket head first, so a caller's value can never lead the line; `--bind` writes the
        # sentence at column zero, and one leading with a fence run opened a real block that
        # blanked the rest of the spec — the dangling escape left `deltas`, `fold` answered
        # R:NOMATCH forever and the engine wrote `open_deltas: 0` itself — while one leading with
        # a delta head forged an open delta nobody filed (twenty-fifth T2 refute, E39). Naming the
        # two shapes would freeze this at the two the read happened to find; the ids and the
        # sections a reader sees are the property itself.
        # The sections are read as a SUBSEQUENCE, never an equality: `_bind_decision` may add the
        # section itself when a spec has none (A10), and that is the engine's own write.
        after = iter([n for _, lv, n in _headings(bound) if lv == 2])
        kept = all(any(n == later for later in after) for _, lv, n in _headings(body) if lv == 2)
        # …and the DECISION lines the readers read. Comparing the ids and the headings was
        # comparing what the guard happened to know about: `_bind_decision` replaces a section its
        # placeholder detector calls scaffold, and that detector cannot tell the engine's own seed
        # line from a decision carrying a bare `<tenant>` — so the next `--bind` deleted one
        # nobody retired, without a word (twenty-sixth T2 refute, E40). The seed line is the one
        # exemption: replacing it is the engine's own write (A10).
        def decisions(text):
            # The engine's own SEED line is the one exemption — a line that is nothing BUT a
            # placeholder. A hand-written decision that merely mentions a `<tenant>` is a
            # decision, and the detector calling it scaffold is what let the clobber through.
            return [l.strip() for l in _section(text, "decisions-that-bind").splitlines()
                    if l.strip() and re.sub(r"<[^>]*>", "", l).strip(" -*·\t") != ""]
        held = all(line in decisions(bound) for line in decisions(body))
        # …and the question `learn`'s own read-back asks and this one did not: is what it WROTE
        # ADDRESSABLE? Preservation is not enough, and under a fence that never closes all three
        # preservation comparisons degrade to empty and pass vacuously — `_bind_decision`'s EOF
        # branch wrote the decision AND the heading it created inside that fence at exit 0, on the
        # very spec where `learn` refuses R:UNREADABLE (twenty-eighth T2 refute, E42).
        if _delta_ids(bound) != _delta_ids(body) or not kept or not held:
            return None, ('cannot bind the decision — the sentence would change what the spec\'s own readers see: '
                           'a decision is one line of prose, never a block a reader stops at (a fence run, a delta '
                           'head). Write it as prose, or quote the markup in a `code span` -> "R:UNCAUSED"\n'
                           f'next: add fold {lens} "{match}" --bind "<decision>"')
        # The read-back E42 gave this writer, asked as the property it was always about: the spec
        # must still be one a writer can LAND in afterwards. Asking only "is my own line
        # addressable" answered yes for a sentence that blinds every LATER writer — the decision
        # sat readable at EOF inside the fence it had just opened, and the next `learn` refused
        # forever (thirty-first T2 refute, E45). One reader, before and after.
        if (blind := unreadable_spec({"raw": node["raw"], "body": bound})):
            return None, (f'cannot bind the decision — specs/{lens}.md would not be readable afterwards: '
                           f'{blind}, so no writer could land a line in it again -> "R:UNREADABLE"'
                           f'\nnext: write the decision as prose (quote any markup in a `code span`), '
                           f'then add fold {lens} "{match}" --bind "<decision>"')
        body = bound
    # Recomputed from the retagged body, so a match that retires three lessons moves the
    # counter by three (E3). A decrement-by-one would be right only for the commonest call.
    raw = set_key(node["raw"], "open_deltas", str(open_delta_count(body)))
    write(path, f"---\n{raw}\n---\n{body}")
    bound = f" · bound 1 decision citing {', '.join(ids)}" if bind else ""
    return True, f"{verdict} {folded} delta(s) in specs/{lens}{bound}\nnext: add status"


# ============================================ search — one lookup, at LESSON granularity
#
# The failure this ends is measurable in this bundle: a lookup that can only answer
# `specs/method.md` points at thirty unrelated lessons, which is why nobody looks anything up.
# So a delta hit is addressed `/specs/<lens>.md#<id>` — the concept address a `relations:` entry
# can target — and the ADDRESS leads the line, because the address is the deliverable.
#
# THREE field classes, and no body. 74 task nodes here carry near-identical scaffold prose, so
# matching bodies makes a query for `gate` hit almost everything — the precise failure lesson
# granularity exists to fix. `type: Run` nodes are skipped BEFORE any deeper read: 115 receipts
# carry a near-identical `computation:` string, and re-parsing their evidence payload is the cost
# FORMAT §4 records removing.

SEARCH_SNIPPET = 96          # the emitted window; the ADDRESS is never truncated
# The tier that leads the total ordering. A delta first — it is the only class carrying its own
# concept address — then node frontmatter, then the CARD goal.
SEARCH_TIERS = {"delta": 0, "title": 1, "description": 1, "tags": 1, "sources": 1, "goal": 2}
SEARCH_FIELDS = ("title", "description", "tags", "sources")


def _snippet(text, query: str) -> str:
    """One physical line, windowed on the first match and marked when elided (R:BODYLEAK).

    A window, never a prefix: a query matching at character 3000 of a 4000-character delta must
    still show the reader WHY it matched. The bound is the whole point — a search that prints
    what it read is a context cost, not a lookup.
    """
    flat = " ".join(str(text).split())
    if len(flat) <= SEARCH_SNIPPET:
        return flat
    i = flat.lower().find(str(query).lower())
    if i < 0:
        return flat[:SEARCH_SNIPPET] + "\u2026"
    start = max(0, i - (SEARCH_SNIPPET - min(len(query), SEARCH_SNIPPET)) // 2)
    end = min(len(flat), start + SEARCH_SNIPPET)
    start = max(0, end - SEARCH_SNIPPET)
    return ("\u2026" if start else "") + flat[start:end] + ("\u2026" if end < len(flat) else "")


def _filter_pass(fm: dict, want_type, status, milestone) -> bool:
    """True when a node satisfies every node-scoped filter that was actually given.

    An ABSENT `status:` matches no `--status` value. Measured on the live bundle: 135 of 220
    nodes carry none, so treating absent as a wildcard would return most of the bundle for
    every status query.
    """
    if want_type and fm.get("type") != want_type:
        return False
    if status and str(fm.get("status") or "") != str(status):
        return False
    if milestone and _wave_slug(fm.get("milestone")) != _wave_slug(milestone):
        return False
    return True


def search(root, query: str = None, as_of: str = None,
           type: str = None, status: str = None, milestone: str = None) -> tuple:
    """Every concept in the bundle matching `query`, narrowed by the node-scoped filters.

    `(hits, note)`. Read-only, never writes.

    `hits` is `[(address, field, snippet), ...]` under a TOTAL order, so two runs over an
    unchanged bundle emit byte-identical output. `hits is None` marks a REFUSAL and only a
    refusal — an empty list is a recorded no-hit outcome (law 3), which is why the CLI exits 0
    on it and 1 on a None.

    `--as-of` is delegated to `deltas()` — called once per status, so the interval arithmetic,
    the half-open [from, to) boundary and the include-what-cannot-be-judged rule are INHERITED
    rather than re-derived. What is NOT reused is that function's own `undated` counter: it
    increments before its status filter, so three calls would treble it. The count below is
    taken from this function's own de-duplicated hit list instead.
    """
    root = Path(root)
    q = str(query or "").strip()
    picked = {k: v for k, v in (("type", type), ("status", status),
                                ("milestone", milestone)) if v}

    # The taxonomy check comes FIRST, ahead of every other rung. A `--type` typo that fell
    # through would answer zero hits, and zero hits reads as "nothing matches" rather than as
    # "you asked for a type that does not exist" — the shape that let an unrecognised
    # `sensitivity:` degrade to the lowest authority floor (M24).
    want_type = None
    if type:
        want_type = next((t for t in ABF_TYPES if t.lower() == str(type).strip().lower()), None)
        if want_type is None:
            # The separator is hoisted OUT of the expression part: py3.10 forbids a backslash
            # there, and this engine's declared floor is 3.10 (SDD S7).
            taxonomy = " \u00b7 ".join(ABF_TYPES)
            return None, (f'`{type}` is not an ADD node type -> "R:UNKNOWNTYPE"'
                          f"\n  the taxonomy: {taxonomy}"
                          "\nnext: add search --type Task")
    if not q and not picked:
        return None, ('an empty query is contained in every string, so it would answer with the '
                      'whole bundle -> "R:EMPTYQUERY"'
                      "\nnext: add search <term>   # or narrow with --type / --status / --milestone")
    # R:TODAYFALLBACK — validated HERE, before the delegation, so the refusal names the verb the
    # operator ran. Falling back to today would answer a question nobody asked.
    if as_of is not None and _as_date(as_of) is None:
        return None, (f"`{as_of}` is not a date — --as-of takes ISO YYYY-MM-DD, the form the "
                      f'delta grammar writes -> "R:TODAYFALLBACK"'
                      f"\nnext: add search <query> --as-of YYYY-MM-DD")

    needle = q.lower()
    # (tier, status, -date, cid, address, field, snippet, dated) — every tie broken, so the
    # listing is diffable and no dict or set order can reach the output.
    found = []
    # A delta carries no `type:` and no `milestone:`, and its open/folded/rejected vocabulary is
    # NOT the node lifecycle — so a node-scoped filter cannot judge one. They are excluded, and
    # the count is carried to the note: an unreported exclusion reports a smaller number, and a
    # smaller number reads as success (R:SILENT_DROP).
    excluded = 0
    for rank, delta_status in enumerate(DELTA_STATUSES):
        for item in deltas(root, status=delta_status, as_of=as_of)[0]:
            # The id is an ADDITIONAL matchable field, never a replacement: a lesson must be
            # findable by the address it is cited at, and text queries must keep working (A3).
            if not needle or not (needle in item[2].lower()
                                  or (item.id and needle == item.id.lower())):
                continue
            if picked:
                excluded += 1
                continue
            cid = delta_address(item[0])
            # A legacy head carries no id, so its address degrades to the file it lives in —
            # shown at the coarser grain rather than dropped from the index.
            address = delta_address(item[0], item.id)
            found.append((0, rank,
                          -int(item.valid_from.replace("-", "")) if item.valid_from else 0,
                          cid, address, f"delta:{delta_status}", _snippet(item[2], q),
                          bool(item.valid_from)))

    for cid, node in scan(root).items():
        fm = node["fm"] or {}
        # A receipt is evidence, not a concept; `index.md`/`log.md` are COMPILED from the nodes
        # and would double every title hit.
        # A receipt is evidence, not a concept — but an EXPLICIT `--type Run` is not the
        # blanket free-text case this exclusion was written for, and answering zero to a
        # request naming a real taxonomy member is R:HIDDENTYPE.
        if (fm.get("type") == "Run" and want_type != "Run") or cid.lstrip("/") in NOT_A_NODE:
            continue
        if not _filter_pass(fm, want_type, status, milestone):
            continue
        if not needle:
            # A filter-only ask: the NODE is the hit. There is no matched text to window, so
            # the snippet is the node's own title.
            label = fm.get("title")
            shown = "" if label is None or _is_template(label) else str(label)
            found.append((1, 0, 0, cid, cid, str(fm.get("type") or "node"),
                          _snippet(shown, "") if shown else "\u2014", False))
            continue
        for field in SEARCH_FIELDS:
            value = fm.get(field)
            if value is None or _is_template(value):
                continue     # an unauthored slot is not an answer
            text = " \u00b7 ".join(str(v) for v in value) if isinstance(value, list) else str(value)
            if text.strip() and needle in text.lower():
                found.append((1, 0, 0, cid, cid, field, _snippet(text, q), False))
        for line in read(node["path"], "T1")["card"].splitlines():
            head, sep, tail = line.strip().partition(":")
            if sep and head.lower() == "goal" and tail.strip() \
                    and not _is_template(tail.strip()) and needle in tail.lower():
                found.append((2, 0, 0, cid, f"{cid}#card", "goal", _snippet(tail, q), False))

    found.sort(key=lambda h: h[:7])
    hits = [(h[4], h[5], h[6]) for h in found]
    active = f" \u00b7 as of {as_of}" if as_of else ""
    sep = " \u00b7 "
    shown_ask = f'"{q}"' if q else sep.join(f"--{k} {v}" for k, v in picked.items())
    if not hits:
        # A typo and an empty slice must not look identical (A12). Naming the statuses the
        # bundle actually holds is what tells the two apart without a second command.
        seen = sorted({str((n["fm"] or {}).get("status")) for n in scan(root).values()
                       if (n["fm"] or {}).get("status")})
        listed = sep.join(seen)
        where = f"\n  statuses in this bundle: {listed}" if status and seen else ""
        return [], (f'no hit for {shown_ask}{active}{where}'
                    "\nnext: add deltas   # the whole carried inventory, unfiltered")
    width = max(len(h[0]) for h in hits)
    fwidth = max(len(h[1]) for h in hits)
    lines = [f"{len(hits)} hit{'s' if len(hits) != 1 else ''} for {shown_ask}{active}:"]
    lines += [f"  \u00b7 {a:<{width}}  {f:<{fwidth}}  {s}" for a, f, s in hits]
    if excluded:
        lines.append(f"\u2014 {excluded} delta hit(s) excluded: a node-scoped filter cannot "
                     f"judge a lesson, which carries no type: or milestone:")
    # A filter that hides what it cannot judge reports a smaller number, and a smaller number
    # reads as success (R:SILENT_DROP). Counted from the hit list, never from `deltas()`.
    # Suppressed when a filter ran: the deltas it could not judge are already reported above,
    # and every surviving hit is a node hit, so the line would count the same removal twice.
    free = sum(1 for h in found if not h[7])
    if as_of and free and not picked:
        lines.append(f"\u2014 {free} hit(s) carry no validity interval (node frontmatter, CARD "
                     f"goals, and legacy undated deltas): --as-of cannot judge them and does "
                     f"not hide them")
    lines.append("next: cite an address above as a relations: target, or add deltas --lens <lens>")
    return hits, "\n".join(lines)


# ================================== the machine surface — one envelope, both read verbs (S1-S4)
#
# `show` and `search` are the two doors a machine reads this bundle through. Both answered only
# in prose until now, so a consumer had to parse a human render and was coupled to wording no
# test pinned. What follows is the second render of the SAME answer — never a second read.
#
# The envelope is `results[] + edges[]` because that is the one shape both verbs fit: `show` is
# one node plus its walk, `search` is N hits and no walk. A later verb returning both fits
# without a third shape, and `search` carries `edges: []` rather than omitting the key, so a
# consumer indexes one shape (A10).
#
# The engine version is DELIBERATELY absent. A payload that carried it would change bytes every
# release, breaking a consumer's pin for no semantic reason; `JSON_SCHEMA` moves only when the
# schema does (M7).

JSON_SCHEMA = "add.read/1"


def read_payload(verb: str, request: dict, ok: bool, note: str,
                 results=(), edges=()) -> dict:
    """The ONE envelope every machine read emits — and the only place its keys are named.

    Both adapters call here. Naming the keys twice is exactly the drift `one-address-per-concept`
    cost a task to undo, one level up (R:TWOSHAPES).

    A request entry whose value is `None` is dropped: the echo says what was ASKED, and a flag
    nobody typed was not part of the ask.
    """
    return {
        "schema": JSON_SCHEMA,
        "verb": verb,
        "ok": bool(ok),
        "request": {k: v for k, v in dict(request).items() if v is not None},
        "results": [dict(r) for r in results],
        "edges": [dict(e) for e in edges],
        "note": note or "",
    }


def as_json(payload: dict) -> str:
    """The one serializer. Sorted keys, two-space indent, one trailing newline, no escaping.

    `sort_keys` is what makes M2 hold: without it a dict that happened to be built in a different
    order emits different bytes, and that failure is INTERMITTENT — the worst way to fail.
    `ensure_ascii=False` keeps a node's own text readable rather than shipping it as escapes.
    """
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2) + "\n"


def _fields(fm: dict) -> dict:
    """A node's frontmatter as the payload carries it — copied AS IT STANDS.

    An absent key stays absent rather than becoming `null`: a key present in the payload means a
    key present in the file, which is the only way a consumer can tell an unauthored slot from
    an authored empty one (A9).
    """
    return {k: v for k, v in dict(fm or {}).items()}


def show_payload(root, ref: str, expand: int = NEIGHBORHOOD_DEFAULT) -> tuple:
    """`show`, rendered for a machine. `(payload, exit_code)`.

    Built AFTER the verb answers, from what it returned — never a second traversal, so the JSON
    and the prose can never describe different reads of the bundle (A7).
    """
    request = {"ref": ref, "expand": expand}
    view, note = show(root, ref, expand)
    if view is None:
        return read_payload("show", request, False, note), 1
    # `match` — what in the concept answered the ask. NOT `kind`: the engine already spends that
    # word on the receipt-evidence ladder, and one word for two vocabularies is a collision a
    # guard cannot see through (it read this literal as a receipt kind the docs never named).
    results = [{"address": view["cid"], "cid": view["cid"], "match": "node",
                "fields": _fields(view["fm"]), "text": view["body"]}]
    edges = [{"depth": d, "direction": direction, "family": family, "label": label,
              "origin": origin, "src": src, "ref": ref_, "target": target}
             for d, direction, family, label, origin, src, ref_, target in view["rows"]]
    # NOT the human render: that would put prose inside the payload and duplicate the stream a
    # `--json` caller asked to be free of it (R:DIRTYSTDOUT). A one-line summary instead.
    summary = f"{view['cid']} \u00b7 {len(edges)} edge(s) within {expand} level(s)"
    return read_payload("show", request, True, summary, results, edges), 0


def search_payload(root, query: str = None, as_of: str = None, type: str = None,
                   status: str = None, milestone: str = None) -> tuple:
    """`search`, rendered for a machine. `(payload, exit_code)`.

    `hits is None` is the verb's refusal marker and an empty list is a recorded no-hit outcome
    (law 3), so a zero-hit search is a SUCCESS with `results: []` — never a refusal (E2).

    A hit's `cid` is its address minus the `#fragment`. `search` already builds that address, and
    `one-address-per-concept` made the node and delta doors build it the same way, so deriving it
    here cannot disagree with the verb (A4).
    """
    request = {"query": query, "as_of": as_of, "type": type,
               "status": status, "milestone": milestone}
    hits, note = search(root, query, as_of=as_of, type=type, status=status, milestone=milestone)
    if hits is None:
        return read_payload("search", request, False, note), 1
    # The VERB's order, unchanged — an adapter that re-sorted would make the two renders
    # disagree about what came first (A13).
    results = [{"address": address, "cid": address.split("#")[0], "match": matched,
                "fields": {}, "text": text} for address, matched, text in hits]
    summary = f"{len(results)} hit(s)"
    return read_payload("search", request, True, summary, results), 0


# ================================== the covers: binding — evidence that earns its name (e12)
#
# A15's finding: `covers:` was a LABEL. A task could claim a Must was proven by a check that
# never ran, and nothing noticed. Here a Must is proven only by a check ID the RUNNER
# reported passing — not by a string in a markdown table.
#
# This also closes the gap e7 left: `test-ids` was unreachable, so every receipt degraded to
# `command-exit`. An evidence kind that can never be earned is not a ladder, it is a label —
# the same defect A15 found, one level up.

# FORMAT §6.1's `covers-grammar`, stated ONCE here and reused. e15 closed F1 by holding
# FORMAT, the validator and this engine to one grammar; a second copy in this file would
# reopen R:DRIFT inside the engine itself.
RULE_ALT = r"M\d+|R:[A-Z0-9_]+|E\d+"
RULE_ID = re.compile(rf"^-\s+({RULE_ALT})\b")
REFERENT = re.compile(rf"\A({RULE_ALT}|goal|G\d+|A\d+)\Z")  # A<n>: a probed assumption (W2)
COVERS_IN_CHECK = re.compile(r"^-\s+(\S+)\s+·\s*covers:\s*([^·]+?)\s*·")


def _section_of(body: str, heading: str) -> str:
    out, inside = [], False
    for line in body.splitlines(keepends=True):
        if line.startswith("## "):
            if inside:
                break
            inside = line.strip().lower() == f"## {heading}".lower()
            continue
        if inside:
            out.append(line)
    return "".join(out)


BOX = re.compile(r"^\s*- \[([ xX~])\]\s?(.*)$")
# The ONE checkbox pattern. `check` writes what `milestone_done` tallies, so a syntax either
# both see or neither does — two patterns would let the verb tick a box the goal-gate cannot
# count, and the tally is what the gate refuses on.


PLACEHOLDER = re.compile(r"<[a-z_][^>]*>")


RE_ASSUMPTION_PLACEHOLDER = re.compile(
    r"^- A\d+ \[\w+\] covers: <S ids>.*$", re.MULTILINE)

# The dimensions a silence hides in. CLOSED and small on purpose: an open vocabulary
# cannot be swept, and a long one will not be. Domain-neutral, because a Task may
# publish an HTTP route, a function, or a document — "endpoint" is one profile's word.
#
#   who         identity · authority · scope — whose data, which caller may act
#   which       inclusion · visibility — which rows/cases are in, which are filtered out
#   when        boundaries · timing — inclusive or exclusive, before or after
#   absent      missing values · defaults — what happens when the field is not supplied
#   order       sequencing · ties — what breaks a tie, what comes first
#   experience  audience · difficulty — who receives this, what makes it hard for them
#
# `who` and `which` are the two the live amb1 runs split on: every rep asked WHICH rows
# `GET /bookings` returns and none asked WHOSE.
#
# `experience` is DISJOINT from `who`, and the distinction is the whole reason it needs
# its own name: `who` is AUTHORIZATION — whose data, which caller may act. `experience`
# is AUDIENCE — who receives the output and what would make it hard to receive. Answer
# one and the other is still open. Without this paragraph the two read as the same
# question asked twice, and the cheap way out of that is `[experience] n/a · duplicate`.
#
# It is last, and appended rather than inserted, so the five existing `A<n>` numbers stay
# where a reader of an already-authored bundle expects to find them.
#
# It exists because the other five all ask whether the output is CORRECT. The `experience`
# lens ships in every profile and maps to UDD in LENS_COMP, but until this dimension the
# only thing in the loop that ever wrote it was `learn` — filed AFTER something had already
# misled someone. A task could be provably correct and unusable and nothing would notice.
# The sweep is where it belongs rather than a beat of its own: it already refuses, it is
# already domain-neutral, and a design-preview step would be screen-shaped — the 1.7-era
# wireframe ceremony said nothing about a reconciliation and quietly rotted away because
# nothing checked it.
SWEEP_DIMENSIONS = ("who", "which", "when", "absent", "order", "experience")

RE_ASSUMPTION_LINE = re.compile(r"^-\s+A\d+\s+\[(\w+)\]\s*(.*)$")


def surfaces_of(node: dict) -> list:
    """The `S<n>` surface ids published in `gives:` — the axis the sweep runs along.

    A surface is what a CALLER touches. Sweeping Musts instead demanded 50-60 pairs on
    real nodes (12, 10 and 11 Musts x 5 dimensions), which is not a checklist but a toll
    — and a toll gets paid with blanket lines that satisfy the gate without doing the
    work. There are far fewer surfaces than rules, and "who may call this, and which rows
    do they see" is a question about a surface, not about a sentence.
    """
    out = []
    for entry in (node.get("fm") or {}).get("gives") or []:
        m = re.match(r"\s*(S\d+)\b", str(entry))
        if m:
            out.append(m.group(1))
    return out


RE_HTTP_METHOD = re.compile(r"\b(?:GET|POST|PUT|DELETE|PATCH)\b")
# W3: an identifier flush against `(` is a callable; whitespace before `(` is prose.
RE_CALLABLE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_.]*)\(")
# W3: only a BACKTICKED file name is a named document artifact — prose mentions stay unjudged.
RE_BACKTICKED_DOC = re.compile(r"`([\w./-]+\.[A-Za-z0-9]{1,4})`")


def collapsed_surfaces(node: dict) -> list:
    """`S<n>` ids whose entry names SEVERAL HTTP methods — several surfaces in one id.

    The probe-2 evasion, verbatim: `S1 the booking HTTP surface — POST/GET /bookings,
    GET/DELETE /bookings/{id}, GET /rooms/{room_id}/waitlist`. Five endpoints in one id
    turns a ~25-pair sweep into a 5-pair one, and the [who]/[which] questions get asked
    once, about the loudest endpoint, while the reads ship unexamined. The enumeration
    rule stood in direction.md throughout — the third consecutive live demonstration
    that a prose rule with no engine checkpoint does not happen.

    STILL PARTIAL, and honest about it (beta-2/W3 widened it, it did not complete it):
    three definitional token shapes are judged and nothing else is. Two HTTP method
    tokens are two caller calls; two DISTINCT `name(` callable tokens are two functions;
    two BACKTICKED file names are two named artifacts. A prose mention without one of
    those shapes — a section, an unbackticked filename, a described behaviour — is never
    judged: a heuristic that guessed at prose shape would be a guard, not a notary.
    Repetition is not multiplicity (`admit()` twice is one surface), and a parenthetical
    like `(paginated)` is not a callable — only an identifier flush against `(` counts.
    """
    out = []
    for entry in (node.get("fm") or {}).get("gives") or []:
        text = str(entry)
        m = re.match(r"\s*(S\d+)\b", text)
        if not m:
            continue
        several = (len(RE_HTTP_METHOD.findall(text)) >= 2
                   or len(set(RE_CALLABLE.findall(text))) >= 2
                   or len(set(RE_BACKTICKED_DOC.findall(text))) >= 2)
        if several:
            out.append(m.group(1))
    return out


def is_slot(text) -> bool:
    """True when a line still stands in template scaffold. The ONE placeholder rule.

    A backticked span is CODE, not a placeholder. Four readers used to answer this question and
    only two applied that exclusion: `placeholders_in` and `_placeholder_only` stripped code
    spans, while `gives_unauthored` and the milestone EXIT box check matched the raw text. So a
    line written in the engine's own vocabulary — a criterion naming `E<n>`, a surface naming a
    `<T>`-parameterised type — read as an unauthored slot, and this milestone's own freeze was
    refused twice by it. One oracle, one rule; the disagreement was the defect.
    """
    return bool(PLACEHOLDER.search(re.sub(r"`[^`]*`", "", str(text))))


def gives_unauthored(node: dict) -> bool:
    """True when `gives:` is missing or still the scaffold — i.e. nothing to sweep.

    Without this the gate has a one-line off switch: delete `gives:`, get no surfaces,
    sweep vacuously clean. Absence is unchanged by the code-span rule (A7): the off switch
    this closes is DELETING the key, which no amount of backticking reaches.
    """
    entries = (node.get("fm") or {}).get("gives") or []
    return not entries or any(is_slot(e) for e in entries)


def assumption_sweep(node: dict) -> list:
    """Unswept `(dimension, surface_id)` pairs — empty when the sweep is complete.

    For every surface and every dimension, some `[dim]` assumption must name that surface
    in its `covers:`, or the dimension must be retired with `n/a` and a reason. That is
    the difference between non-empty and complete: `freeze` used to prove an assumption
    EXISTED, which three live runs satisfied while still shipping a silent decision.

    Exempt, deliberately:
      * `depth: quick` — depth tunes ceremony (SKILL.md). A one-file mechanical edit does
        not earn a five-dimension matrix, and demanding one would push authors toward
        `quick` for work that deserves `standard`.
      * a node with no `## ASSUMPTIONS` section — law 3 reads it as empty, so bundles
        written before the section existed are not retroactively refused.

    WHAT THIS DOES NOT CLAIM: it proves the author LOOKED at every pair, never that they
    looked honestly. A blanket `[who] covers: S1, S2, S3` satisfies it. Writing that line
    still requires scanning every surface under "who", and the blanket reading is then on
    the record where a reviewer can disagree with it — which a silent omission never
    allowed. FORMAT.md §10.
    """
    body = node.get("body") or ""
    section = _section_of(body, "ASSUMPTIONS")
    if not section.strip():
        return []
    if str((node.get("fm") or {}).get("depth") or "standard") == "quick":
        return []
    surfaces = surfaces_of(node)
    if not surfaces:
        return []          # `gives_unauthored` is what refuses this; see freeze()
    covered, waived = {d: set() for d in SWEEP_DIMENSIONS}, set()
    for line in section.splitlines():
        m = RE_ASSUMPTION_LINE.match(line.strip())
        if not m:
            continue
        dim, rest = m.group(1).lower(), m.group(2)
        if dim not in covered:
            continue
        # A waiver states WHY. The docstring above has always promised this ("retired with `n/a`
        # and a reason") and the code checked only for the token, so six bare `n/a` lines were a
        # six-line off switch for the whole six-dimension matrix — each cheaper to type than one
        # honest assumption, which is the shape that gets a guard routed around rather than
        # satisfied. Any non-empty text after the format's own `·` separator counts: a notary
        # cannot judge whether a reason is GOOD, and a bar it cannot judge only teaches padding
        # -> "R:CHEAPSILENCE".
        if re.match(r"^n/?a\b\s*[·,-]\s*\S", rest.strip(), re.I):
            waived.add(dim)
            continue
        if re.match(r"^n/?a\b", rest.strip(), re.I):
            continue   # a silence with no reason retires nothing; the pair stays unswept
        found = re.search(r"covers:\s*([^·]*)", rest)
        if found:
            covered[dim].update(re.findall(r"\bS\d+\b", found.group(1)))
    return [(d, sid) for d in SWEEP_DIMENSIONS if d not in waived
            for sid in surfaces if sid not in covered[d]]


def placeholders_in(node: dict, *, card: bool = True) -> list:
    """Template tokens still standing in a node's RULES, ASSUMPTIONS or CHECKS.

    `new` ships `- M1 <the rule that must hold>` and `- <test_name> · covers: M1`. Those parse as
    a real rule and a real check, so an unauthored node refuses at the gate with "M1 has no
    reported passing check" — true, and it points at RISK-ACCEPTED when the fix is to author the
    node. Naming the placeholder turns a confusing refusal into an actionable one (M4).

    BACKTICKED spans are code, not template tokens. F8, found when this refused e8's fully authored
    node over `<slug>.d/runs/` in a Must — correct machinery reaching a false conclusion. Rewording
    every node that needs to name a path shape would make prose pay a permanent tax to a defective
    oracle. Safe because no placeholder in either `BODIES` template is backticked, which was
    measured across both before the exclusion was added rather than assumed.
    """
    found = []
    # ASSUMPTIONS joins RULES and CHECKS because an instruction with no checkpoint is an
    # instruction that does not happen. SKILL.md and direction.md have asked for the
    # riskiest assumption since 3.0; the live amb1 run recorded none, and skipping it
    # cost nothing at freeze or gate. A node with no assumption section at all still
    # freezes — `_section_of` reads a missing section as empty (law 3) — so bundles
    # authored before this shipped are not retroactively refused.
    for heading in ("RULES", "ASSUMPTIONS", "CHECKS"):
        for line in authored_section(node.get("body") or "", heading).splitlines():
            if line.startswith("- ") and PLACEHOLDER.search(re.sub(r"`[^`]*`", "", line)):
                found.append(line.strip())
    # CARD's `goal:` — a KEYED line, not a `- ` bullet, which is why the loop above could
    # never see it. GETTING-STARTED promised "freeze refuses a node that still carries
    # template placeholders — you cannot approve a scaffold", and a node froze with
    # `goal: <one line>` intact: approving a contract whose one-line statement of intent is
    # still the scaffold's. The goal is what a human is being asked to approve.
    #
    # Scoped to `goal:` alone, and deliberately: EVIDENCE and LESSONS are VIEWS written by
    # `render_evidence` (run · refute · gate) and `harvest_lessons` (the close), neither of
    # which exists at freeze time, so demanding them here would
    # ask for a receipt before the build that produces it (M3, A2). Depth does not exempt
    # this — a quick task states its goal too (E4).
    #
    # `card=` exists for callers that must ask only about the three body sections. It is NOT
    # a second notion of "authored": `_is_scaffold` deliberately asks the FULL question, and
    # `test_authoring_beat` drives advice and `freeze` against the same node to prove they
    # never diverge. A node advised to freeze that `freeze` then refuses is the defect that
    # test exists to catch, and splitting the two questions reintroduces it.
    if card:
        for line in _section_of(node.get("body") or "", "CARD").splitlines():
            if line.startswith("goal:") and PLACEHOLDER.search(re.sub(r"`[^`]*`", "", line)):
                found.append(f"## CARD {line.strip()}")
    return found


def _canon(text: str) -> str:
    """Trailing whitespace and blank lines are not contract changes."""
    return "\n".join(line.rstrip() for line in text.splitlines() if line.strip())


def exit_digest(node: dict) -> str:
    """The authored EXIT direction, excluding completion ticks and formatting."""
    payload = _canon(_section_of(node.get("body") or "", "EXIT"))
    payload = re.sub(r"(?m)^([ \t]*-[ \t]*)\[[ xX]\]", r"\1[ ]", payload)
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()[:16]


def direction_digest(node: dict) -> str:
    """The seal over what a freeze approved: RULES · CHECKS · `gives:`.

    Deliberately scoped to the frozen surface rather than the whole node. A CARD `goal:` reword or
    a new LESSONS line is not a contract change, and sealing those would make ordinary editing
    demand a refreeze until authors refroze reflexively — which is how a seal decays into a rubber
    stamp. Constraint 3 names exactly three things that must not move under a build: the Musts, the
    Rejects, and the published `gives:`. Those, and nothing else.

    This closes only the STRUCTURAL half of constraint 3. Whether a check still *proves* its rule is
    semantic, and a NO-EXEC notary cannot judge it — `assert True` under an unchanged name digests
    identically to the real assertion it replaced. What this makes impossible is the SILENT edit:
    changing the frozen text without the change appearing in the record.
    """
    body = node.get("body") or ""
    gives = (node.get("fm") or {}).get("gives") or []
    payload = "\n".join((_canon(authored_section(body, "RULES")),
                         _canon(authored_section(body, "CHECKS")),
                         _canon("\n".join(str(g) for g in gives))))
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()[:16]


def binding_digest(node: dict) -> str:
    """The seal over what the GATE binds but `direction:` never covered: edges and probed A ids.

    `referents_of` is RULES + `## EDGES` + probed `A<n>`; `direction_digest` is RULES + CHECKS +
    `gives:`. Two of the three bindable classes were outside the seal, so a builder facing
    `these rules have no reported passing check: A1, E1` could DELETE the obligation instead of
    proving it and gate clean — no drift refusal, no refreeze stamp, no doctor finding.

    A second digest rather than a wider `direction:`, for two reasons. Widening would re-digest
    every node already frozen and strand them. And ASSUMPTIONS is pinned out of `direction:` on
    purpose — right when `A<n>` bound nothing, and still right for the prose: this seals the
    REFERENT SET only, so retiring an obligation is drift while rewording one stays free. A seal
    authors refreeze reflexively is a rubber stamp.
    """
    body = node.get("body") or ""
    edges = [m.group(1) for line in authored_section(body, "EDGES").splitlines()
             for m in [RULE_ID.match(line)]
             if m and not PLACEHOLDER.search(re.sub(r"`[^`]*`", "", line))]
    probed = [m.group(1) for line in authored_section(body, "ASSUMPTIONS").splitlines()
              for m in [RE_PROBED_ASSUMPTION.match(line.strip())] if m]
    payload = "\n".join(sorted(edges) + sorted(probed))
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()[:16]


INTERVIEW_VERDICTS = ("confirm", "correct", "defer")


# `- M<n> <the rule> (from: <where you were told> · fails-on: <the plausible wrong reading>)`.
# Either half may stand alone; both are FREE TEXT and neither is resolved — the engine records a
# source as handed, exactly as it records `by:` (R:SOURCEJUDGED). The tail is Must TEXT, so the
# direction digest seals it and every existing reader sees one line as it always did.
MUST_SOURCE = re.compile(r"\((?:from:\s*(?P<src>[^·)]*?))?\s*(?:·\s*)?"
                         r"(?:fails-on:\s*(?P<fails>[^)]*?))?\s*\)\s*$")


def must_source(line: str) -> dict:
    """`{"from": …, "fails_on": …}` for a Must line carrying the tail, else None.

    None is "no tail", and a tail carrying only `fails-on:` answers `{"from": None, …}` — the two
    are different questions, and collapsing them would ask a Must that named its falsifier for a
    source it may already have given in the sentence itself.
    """
    m = MUST_SOURCE.search(str(line or "").rstrip())
    if not m or (m.group("src") is None and m.group("fails") is None):
        return None
    src, fails = m.group("src"), m.group("fails")
    return {"from": (src or "").strip() or None, "fails_on": (fails or "").strip() or None}


def _rules_view(body) -> list:
    """The body's lines with everything outside the authored `## RULES` section blanked — one line
    out per line in, so an index into this view is an index into the body.

    The ONE view of "where a Must may live". `_authored_rules` keeps all seven authored sections,
    so a `- M2 …` line pasted under `## EDGES` read as a Must to the question and the notice while
    `rules_of`, `single_mode_musts`, `uncovered_obligations` and the `covers:` grammar all said it
    was not a rule — two readers of what a Must IS, and the route a duplicate travelled (E12).
    """
    lines = _authored_rules(str(body or "")).splitlines()
    start = heading_index(lines, "rules")
    if start < 0:
        return [""] * len(lines)
    end = next((j for j, (_, level, _) in enumerate(_headings(lines))
                if j > start and level == 2), len(lines))
    return [str(ln) if start < i < end else "" for i, ln in enumerate(lines)]


def must_lines(body) -> dict:
    r"""`{line index in the body: Must id}` for every AUTHORED Must — the ONE reader of which LINE
    is a Must, indexed so a writer can find it again.

    A view of WHERE (`_rules_view`) and a pattern for WHAT (`RULE_ID`), in one place, because
    splitting them is how this task was refuted five times running. `RULE_ID` is the grammar
    FORMAT §6.1 publishes and `rules_of`, `single_mode_musts`, `uncovered_obligations` and the
    `covers:` grammar all read; the question, the freeze notice and the interview's WRITER now read
    it too. The writer had kept its own third pattern — looser on the left (an indent, a dash with
    no space) and stricter on the right (`\s+` where the grammar has `\b`) — so `- M2:` was a Must
    to the gate and to the question and INVISIBLE to the writer: `interview --answer M2=confirm`
    exited 0, wrote nothing, and the node then carried an `act: interview` stamp attesting the
    answer beside a freeze notice saying the Must had no source, forever (twenty-ninth T2 refute).
    """
    out = {}
    for i, line in enumerate(_rules_view(body)):
        m = RULE_ID.match(str(line))
        if m and m.group(1).startswith("M"):
            out[i] = m.group(1)
    return out


def _musts_without_source(node: dict) -> list:
    """`[(id, the whole line)]` for every authored Must that names no source — the ONE reader both
    the interview and the freeze notice ask, so the question and the notice can never disagree."""
    out = []
    lines = _rules_view(node.get("body") or "")
    for i, mid in must_lines(node.get("body") or "").items():
        line = str(lines[i])
        text = line[RULE_ID.match(line).end(1):].strip()
        # A SCAFFOLD line is one the author never wrote over — `- M1 <the rule that must hold>` —
        # not any rule that happens to name a `<placeholder>` in its own sentence. Skipping the
        # latter made a real Must invisible to the question, to the notice and to `confirm`, while
        # M2 and M3 quantify over EVERY Must with no `from:` (E11).
        if not re.fullmatch(r"<[^>]*>", re.sub(r"`[^`]*`", "", text).strip()):
            tail = must_source(text)
            if not (tail and tail["from"]):
                out.append((mid, line.strip()))
    return out


def _open_decisions(node: dict) -> list:
    """The decisions a human never made but will be held to: non-`n/a` assumptions, filled edges, then Rejects.

    An `n/a` retirement already states its own reason, and a Must came FROM the human — re-asking
    either is noise, and an interview people learn to click through buys nothing.
    """
    body = node.get("body") or ""
    out = []
    # A Milestone's decisions are its EXIT criteria, and ONLY those. Its goal and why are the
    # human's own words, and SCOPE and GROUND are not what a stamp attests. Every box counts
    # whether ticked or not (A4): a tick states the criterion was MET, never that anyone
    # approved its wording — reading one as an answer would let the goal-gate quietly satisfy
    # the interview, which is M34's failure with an extra step.
    if (node.get("fm") or {}).get("type") == "Milestone":
        exit_body = _section_of(body, "EXIT")
        for n, (_, _, text, _) in enumerate(
                _box_lines(exit_body) if _fence_balanced(exit_body) else [], start=1):
            out.append({"id": f"C{n}", "of": "criterion", "dim": "criterion",
                        "reading": text.strip(), "cost": "", "text": text.strip()})
        return out
    for line in authored_section(body, "ASSUMPTIONS").splitlines():
        m = re.match(r"\s*-\s*(A\d+)\s*\[([a-z]+)\]\s*(.*)", line)
        if not m or re.search(r"·\s*n/a\b", m.group(3)):
            continue
        rest = m.group(3)
        taking = re.search(r"taking\s+(.*?)\s*->", rest)
        cost = re.search(r"->\s*(.*?)(?:\s*·\s*probe:|$)", rest)
        out.append({"id": m.group(1), "of": "assumption", "dim": m.group(2),
                    "reading": (taking.group(1) if taking else rest).strip(),
                    # the grammar's own "-> if wrong ..." would print as "If wrong: if wrong ..."
                    "cost": re.sub(r"^if wrong,?\s*", "",
                                   (cost.group(1) if cost else "").strip(), flags=re.I),
                    "text": line.strip()})
    # The readable example: a FILLED `E<n>` is a claim the human never made in those words — the
    # AI wrote the Given/When/Then — so it is put to them like an assumption. The scaffold line is
    # not (same placeholder rule `edges_of` uses); backticked spans are code, not placeholders.
    for line in authored_section(body, "EDGES").splitlines():
        m = re.match(r"\s*-\s*(E\d+)\s+(.*)", line)
        if m and not PLACEHOLDER.search(re.sub(r"`[^`]*`", "", line)):
            out.append({"id": m.group(1), "of": "edge", "dim": "edge",
                        "reading": m.group(2).strip(), "cost": "", "text": line.strip()})
    for line in authored_section(body, "RULES").splitlines():
        m = re.match(r"\s*-\s*(R:[A-Z0-9_]+)\s+(.*)", line)
        if m:
            out.append({"id": m.group(1), "of": "reject", "dim": "reject",
                        "reading": m.group(2).split("->")[0].strip(), "cost": "",
                        "text": line.strip()})
    # A Must came FROM the human — so it is never re-asked as a RULE. What is asked is the one
    # thing RULES never recorded: WHO said so. Last, and in Must order, so an interview a human
    # already knows keeps its shape and the new questions come after the old ones (A5).
    for mid, line in _musts_without_source(node):
        out.append({"id": mid, "of": "must", "dim": "source",
                    "reading": re.sub(r"\s*-\s*M\d+\s+", "", line, count=1).strip(),
                    "cost": "", "text": line})
    # A human-floor transfer is a NEW approval of the exact responsibility edge. Including the
    # edge in the ordinary interview digest makes a later carry edit reopen that decision.
    carries, _ = _carry_entries(node.get("fm") or {})
    for n, (source, destination) in enumerate(sorted(carries), start=1):
        edge = f"{source} -> {destination}"
        out.append({"id": f"TC{n}", "of": "carry", "dim": "responsibility",
                    "reading": edge, "cost": "", "text": edge})
    return out


def interview_digest(node: dict) -> str:
    """A digest over exactly what was interviewed — the same shape as `direction:` and `brief:`.

    Scoped to the open decisions themselves, so rewording an assumption re-opens the interview
    while editing a Must does not: the Musts came from the human in the first place.
    """
    payload = "\n".join(_canon(d["text"]) for d in _open_decisions(node))
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()[:16]


def _interview_stamps(fm: dict) -> list:
    return [s for s in (fm.get("verified") or [])
            if isinstance(s, dict) and s.get("act") == "interview"]


def interview_gap(node: dict, fm: dict, *, require_human_signer: bool = False) -> list:
    """Ids still owed an answer for the node AS IT NOW READS, or `[]` when the interview holds.

    Reads the stamp whose digest MATCHES the current text — not the latest. Recency is not
    authority: revert an edit and the earlier interview is the one that answers for this text.
    """
    decisions = _open_decisions(node)
    if not decisions:
        return []                      # nothing to ask is not something to refuse
    # Every pass over THIS text, folded in order — later wins. An interview is a conversation, and
    # two sittings about the same decisions are one interview: reading only the first digest-match
    # meant a human interrupted halfway could never finish, and reading only the last meant a
    # follow-up `correct` was outranked by the earlier `confirm` (found in review, 2026-09-01).
    want = interview_digest(node)
    answered = {}
    for s in _interview_stamps(fm):
        if str(s.get("interview") or "") == want and (not require_human_signer or _human_signer(s.get("by"))):
            answered.update(_answer_map(str(s.get("answers") or "")))
    # `correct` is never an answer that completes — it is cleared by EDITING the item, which moves
    # the digest and re-opens the pass.
    return [d["id"] for d in decisions
            if answered.get(d["id"]) not in ("confirm", "defer")]


def _answer_map(packed: str) -> dict:
    out = {}
    for part in packed.split("|"):
        key, sep, verdict = part.partition("=")
        if sep:
            out[key.strip()] = verdict.strip()
    return out


def interview(root, cid: str, answers: dict = None, by: str = None) -> tuple:
    """Put the node's open decisions to a human, or record their answers.

    With no answers this COMPILES and returns `(questions, note)` — a read, writing nothing. With
    answers it validates, writes a `.d/interviews/<n>.md` sidecar and appends one `act: interview`
    stamp referencing it, returning `(node, note)`.

    The engine is a notary here as everywhere: it records the `--by` name verbatim and cannot know
    a human typed it. R:SELFANSWER is discipline carried by the skill, not a claim made by this
    function.
    """
    root = Path(root)
    graph = scan(root)
    entry = graph.get(cid) or {}
    if not entry.get("path"):
        return None, f"no such node: {cid}\nnext: add status"
    slug = cid.rsplit("/", 1)[-1][:-3]
    node = read(entry["path"], "T2")
    decisions = _open_decisions(node)

    if not answers:
        if not decisions:
            return [], (f"`{slug}` has no open decisions — nothing to put to a human"
                        f"\nnext: add freeze {slug}")
        lines = [f"{len(decisions)} open decision(s) in `{slug}` — "
                 f"answer each `{' | '.join(INTERVIEW_VERDICTS)}`:"]
        for d in decisions:
            lines.append(f"\n{d['id']} [{d['dim']}]")
            lines.append(f"  {'Example' if d['of'] == 'edge' else 'I took'}: {d['reading']}")
            if d["cost"]:
                lines.append(f"  If wrong: {d['cost']}")
        lines.append(f"\nnext: add interview {slug} --answer <id>=<verdict> --by \"<name>\"")
        return decisions, "\n".join(lines)

    if (_carry_entries(entry.get("fm") or {})[0] or _has_carry_history(entry.get("fm") or {})) \
            and authority_for(graph, cid) == "human" \
            and not _human_signer(by):
        return None, (f"cannot interview `{slug}` — R:LOWERED_CARRY_AUTHORITY "
                      f"a human-floor carry needs this destination's named human signer"
                      f"\nnext: add interview {slug} --answer <id>=<verdict> --by \"human:<name>\"")

    ids = {d["id"] for d in decisions}
    bad_id = [k for k in answers if k not in ids]
    if bad_id:
        return None, (f"no such decision in `{slug}`: {', '.join(sorted(bad_id))}"
                      f"\nthe open decisions are: {', '.join(d['id'] for d in decisions)}"
                      f"\nnext: add interview {slug}")
    bad_v = {k: v for k, v in answers.items() if v not in INTERVIEW_VERDICTS}
    if bad_v:
        return None, (f"unknown verdict(s) {', '.join(sorted(set(bad_v.values())))} — "
                      f"answer each decision `{' | '.join(INTERVIEW_VERDICTS)}`"
                      f"\nnext: add interview {slug} --answer <id>=<verdict>")

    # Derived from the node's OWN path, never hardcoded to `tasks/`: a milestone's record filed
    # under the tasks tree is a record nothing can find (R:TASKSIDECAR).
    side_dir = entry["path"].parent / f"{slug}.d" / "interviews"
    side_dir.mkdir(parents=True, exist_ok=True)
    n = len(list(side_dir.glob("*.md"))) + 1
    digest = interview_digest(node)
    # What THIS text had already been answered, before the write below may change it. An answer
    # survives an edit the interview itself made: confirming a Must's source rewrites its line,
    # which moves the digest, and reading only the new one would erase every answer given in an
    # earlier sitting — a human who answers the source question last would be asked everything
    # again (must-carries-source, E2).
    prior = {}
    for st in _interview_stamps(entry.get("fm") or {}):
        if str(st.get("interview") or "") == digest:
            prior.update(_answer_map(str(st.get("answers") or "")))
    # Frontmatter, like a run receipt. Without it `doctor` reported `error missing_frontmatter`
    # against a file the engine had just written correctly — the `orphan_receipt` shape one verb
    # over, a notary manufacturing its own conformance error.
    body = [f"---", f"type: Interview", f"task: {cid}", f"by: {_oneline(by or 'unrecorded')}",
            f"at: {_today()}", f"interview: {digest}", "---",
            f"# interview {n} — {slug}", ""]
    for d in decisions:
        body += [f"## {d['id']} [{d['dim']}]", f"- asked: {d['reading']}"]
        if d["cost"]:
            body.append(f"- if wrong: {d['cost']}")
        body.append(f"- answered: {answers.get(d['id'], 'unanswered')}")
        body.append("")
    (side_dir / f"{n}.md").write_text("\n".join(body), encoding="utf-8")

    # SPARSE, deliberately: only what THIS pass answered. Recording `unanswered` for the rest
    # would make each pass clobber the one before it when `interview_gap` folds them, so a second
    # sitting would erase the first instead of completing it. The sidecar still lists every
    # decision — that is the human-readable record; this is the machine-readable delta.
    # The one write the interview makes to the node's TEXT, and only on `confirm`: the human just
    # said "I told you this", and `interview` is the one source the engine WITNESSED. `defer` and
    # `correct` write nothing — a deferred question is unanswered and a correction is cleared by
    # editing the item, which moves the digest and re-opens the pass.
    confirmed = [d for d in decisions if d["of"] == "must" and answers.get(d["id"]) == "confirm"]
    if confirmed:
        # `keepends`, like the other thirteen body writers: re-joining with `"\n".join` converted
        # every line boundary Python knows but `\n` does not preserve — U+2028, U+2029, U+0085, VT,
        # FF — anywhere in the body, by a verb that touched ONE line (E45, E46's class, E10).
        lines, changed = node["body"].splitlines(keepends=True), False
        # The reader's OWN view, not a looser one: `_musts_without_source` reads `_authored_rules`,
        # which blanks fences AND every line outside the authored sections. Reading `live_lines`
        # here — fence-blind only — let an unfenced copy in `## CARD`, the section before `## RULES`
        # in every live node, take the tail while the authored Must stayed bare (E9). One fact, one
        # reader: the writer asks the reader where the line is.
        live = _rules_view(node["body"])
        # The reader's OWN candidate set, by index — not a third pattern spelled out here. See
        # `must_lines`: the writer asking a looser question than the gate is what made a confirmed
        # answer write nothing at all.
        authored = set(must_lines(node["body"]))
        for d in confirmed:
            for i in sorted(authored):
                if str(live[i]).strip() != d["text"]:
                    continue
                tail = must_source(d["text"])
                if tail and tail["fails_on"]:
                    # The tail is JOINED, never replaced: a Must that named its falsifier keeps it,
                    # and `from:` reads first because that is the order of the sentence (A10). The
                    # replacement is a FUNCTION, not a template: `re.sub` reads `\d`, `\1` and
                    # `\g<0>` in a template string as grammar, so the human's own words were
                    # resolved rather than recorded — `\d` raised out of the verb, `\n` split the
                    # frozen Must in two — which is exactly what R:SOURCEJUDGED forbids (E7).
                    repl = f"(from: interview · fails-on: {tail['fails_on']})"
                    fixed = MUST_SOURCE.sub(lambda _m, r=repl: r, str(lines[i]).rstrip(), count=1)
                else:
                    fixed = str(lines[i]).rstrip() + " (from: interview)"
                raw = str(lines[i])
                lines[i], changed = fixed + raw[len(raw.rstrip("\r\n\x0b\x0c\x1c\x1d\x1e\u0085\u2028\u2029")):], True
                # A line is written ONCE. `live` is the pre-write snapshot, so two Musts sharing an
                # id and a text both matched the first index: the line took two tails and the
                # second Must stayed bare, sealed that way by the freeze (E12).
                authored.discard(i)
                break
        body = "".join(lines)
        if changed:
            write(entry["path"], f"---\n{node['raw']}\n---\n{body}")
            node = read(entry["path"], "T2")
            # The stamp seals the text the interview PRODUCED, and carries forward what this same
            # conversation had already settled — ids that no longer open a decision simply drop.
            digest = interview_digest(node)
            still = {d["id"] for d in _open_decisions(node)}
            answers = {**{k: v for k, v in prior.items() if k in still}, **answers}
            decisions = _open_decisions(node) + [d for d in decisions if d["id"] not in still]
    # Built AFTER the rewrite above, so the stamp packs what the conversation now holds against the
    # digest the same block just recomputed — built before it, the pack named one answer and the
    # digest named the other text, and every earlier sitting was erased.
    packed = "|".join(f"{d['id']}={answers[d['id']]}" for d in decisions if d["id"] in answers)
    node_w, err = _transition(root, cid, appends=[
        ("verified", f'{{ by: "{_oneline(by or "unrecorded")}", at: {_today()}, act: interview, '
                     f'authority: human, interview: "{digest}", '
                     f'receipt: /tasks/{slug}.d/interviews/{n}.md, answers: "{_oneline(packed)}" }}')])
    if err:
        return None, err + "\nnext: add status"
    owed = interview_gap(node, scan(root).get(cid, {}).get("fm") or {})
    tail = (f"\n  still owed: {', '.join(owed)} — a `correct` is cleared by editing the item"
            if owed else "")
    return node_w, (f"interview {n} recorded for `{slug}` ({len(decisions)} decision(s)){tail}"
                    f"\nnext: add freeze {slug}")


def sealed_direction(fm: dict) -> str:
    """The digest carried by the most recent freeze/refreeze, or None.

    None means "cannot verify", not "verified clean": bundles frozen by a pre-seal engine carry no
    digest, and refusing them would retroactively strand every task frozen before this shipped.
    """
    for stamp in reversed((fm or {}).get("verified") or []):
        if isinstance(stamp, dict) and stamp.get("act") in ("freeze", "refreeze"):
            return stamp.get("direction")
    return None


def sealed_binding(fm: dict) -> str:
    """The binding digest carried by the most recent freeze/refreeze, or None.

    None means "cannot verify", not "verified clean" — the same stance `sealed_direction` takes,
    and the reason a node frozen before this field shipped stays gateable instead of stranded.
    """
    for stamp in reversed((fm or {}).get("verified") or []):
        if isinstance(stamp, dict) and stamp.get("act") in ("freeze", "refreeze"):
            return stamp.get("binding")
    return None


def rules_of(node: dict) -> list:
    """Every Must and Reject id AUTHORED in the node's RULES section.

    Through `_authored_rules`, the same reader `fold`'s prevention rung uses: an id quoted inside a
    fence or under a heading a blockquote opened is an example, and the gate demanding coverage of
    an example while `fold` called the same id unauthored was two readers of one fact — the defect
    class this milestone keeps finding (sixteenth T2 refute, E30).
    """
    section = authored_section(read(node["path"], "T2")["body"], "RULES")
    return [m.group(1) for m in (RULE_ID.match(l) for l in section.splitlines()) if m]


def edges_of(node: dict) -> list:
    """The REAL enumerated edge ids (`E<n>`) declared in the node's `## EDGES` section.

    An edge is a first-class `covers:` referent (C7): the gate binds it exactly as a Must. A line
    still carrying the scaffold `<placeholder>` is NOT a real edge — a task that never enumerated
    an edge, or left the scaffold untouched, owes no edge coverage (backward compatible). Backticked
    spans are code, not placeholders (same exclusion `placeholders_in` makes). Read through
    `_authored_rules`, the ONE reader of "is this id authored" the fold rung uses too (E30)."""
    body = _authored_rules(read(node["path"], "T2")["body"])
    out = []
    for line in _section_of(body, "EDGES").splitlines():
        m = RULE_ID.match(line)
        if m and not PLACEHOLDER.search(re.sub(r"`[^`]*`", "", line)):
            out.append(m.group(1))
    return out


RE_PROBED_ASSUMPTION = re.compile(r"^-\s+(A\d+)\s+\[\w+\].*·\s*probe:\s*\S")


def probed_assumptions(node: dict) -> list:
    """`A<n>` ids declared CHECKABLE with `· probe: <what shipped behavior must show>` (W2).

    The sweep makes agents ask; nothing makes the answers right — the campaign record shows
    two of seven readings wrong in every run, and a NO-EXEC notary cannot judge an answer.
    What it CAN do is refuse to call a checkable answer proven while no check reports on it:
    a probed id is a first-class covers referent, the same move as C7 made for edges. Opting
    in is the author's; an unprobed line stays a priced guess on the record, never conscripted
    — the engine enforces exactly what was declared checkable, and nothing else.
    """
    out = []
    for line in _section_of(node.get("body") or "", "ASSUMPTIONS").splitlines():
        m = RE_PROBED_ASSUMPTION.match(line.strip())
        if m:
            out.append(m.group(1))
    return out


def referents_of(node: dict) -> list:
    """Every id a check may bind: Musts + Rejects (RULES), real edges (EDGES), probed A ids."""
    return rules_of(node) + edges_of(node) + probed_assumptions(node)


def covers(node: dict) -> dict:
    """`{rule_id: [check_id, ...]}` — parsed from the CHECKS section, keyed by rule."""
    body = read(node["path"], "T2")["body"]
    out = {}
    for line in _section_of(body, "CHECKS").splitlines():
        match = COVERS_IN_CHECK.match(line.strip())
        if not match:
            continue
        check = match.group(1)
        # Commas OR whitespace (M2). The ASSUMPTIONS reader has always taken both; splitting on
        # commas alone here meant `covers: M1 E1` parsed as ONE rule named "M1 E1", matched no
        # rule, and bound NOTHING while reading as correct — a covers list that binds nothing is
        # the exact defect class this milestone exists to close, hiding inside its own parser.
        for rule in (r.strip() for r in re.split(r"[,\s]+", match.group(2))):
            if rule:
                out.setdefault(rule, []).append(check)
    return out


CHECK_MODES = ("acceptance", "property", "contract", "static", "unit", "e2e", "manual")
# The closed set direction.md's router names. Closed on purpose: an open set would let `unit-ish`
# count as a second kind of evidence. The engine never PARSES a mode for the gate — it reads one
# only to NAME the plan-floor Musts still on a single mode at the freeze (two-mode-notice).


def _check_lines(node: dict) -> list:
    """`[(check_id, [rule, …], mode | None), …]` — one entry per CHECKS line `covers()` parses, in
    order. The mode is the first token after the second `·`, stripped of surrounding backticks or
    parentheses (direction.md renders the list in backticks), lowercased, when it is in
    `CHECK_MODES`. Keyed by LINE, not by id: the T2 refute of two-mode-notice found that two lines
    sharing one id let the last line's mode overwrite the first's, so a Must met by `contract`
    was named as single-mode and a violator's mode was misreported — the count the rule's fate
    rests on, corrupted both ways."""
    body = read(node["path"], "T2")["body"]
    out = []
    for line in _section_of(body, "CHECKS").splitlines():
        match = COVERS_IN_CHECK.match(line.strip())
        if not match:
            continue
        parts = [s.strip() for s in line.strip().split("·")]
        word = (parts[2].split() or [""])[0].strip("`()").lower() if len(parts) > 2 else ""
        rules = [r for r in re.split(r"[,\s]+", match.group(2)) if r]
        out.append((match.group(1), rules, word if word in CHECK_MODES else None))
    return out


def check_modes(node: dict) -> dict:
    """`{check_id: mode | None}` — the mode word of each CHECKS line by its id; when one id is
    written on several lines the LAST line's word wins here, which is why `single_mode_musts`
    reads `_check_lines` and never this map."""
    return {cid: mode for cid, _, mode in _check_lines(node)}


def single_mode_musts(node: dict) -> list:
    """`[(M<n>, mode), …]` — the Musts whose covering checks carry exactly ONE known mode.

    dogfood-and-measure F1: the session that wrote "at a plan floor a Must carries two checks of
    different mode" froze 0 of 10 such Musts one task later — prose nobody follows binds nothing.
    A Must with no known mode is not listed (the author claimed none, and listing it would push
    for a WORD, not a second kind of evidence); two or more modes is the rule met. Musts only.
    """
    by_rule = {}
    for _, rules, mode in _check_lines(node):
        for rule in rules:
            by_rule.setdefault(rule, set())
            if mode:
                by_rule[rule].add(mode)
    out = []
    # `dict.fromkeys`: authored order, each id once — the third T2 refute declared `M1` on two
    # RULES lines and the notice named it twice while `uncovered_obligations` (set-based) did not.
    for rule in dict.fromkeys(rules_of(node)):
        if not re.fullmatch(r"M\d+", rule):
            continue
        known = sorted(by_rule.get(rule, set()))
        if len(known) == 1:
            out.append((rule, known[0]))
    return out


def uncovered_obligations(node: dict) -> list:
    """Every authored obligation that no CHECKS `covers:` list names — Musts, Rejects, filled
    edges, probed assumptions. Sorted.

    Calls the three functions `referents_of` composes — never a copy of the rule
    (R:SECOND_TRUTH), so `freeze` and `gate` can never disagree about what an obligation is.

    `rules_of` was held out until the cost of widening was MEASURED rather than estimated. It was
    measured over this bundle at direction: **0 of 105** nodes carrying RULES have an uncovered
    Must or Reject, and 21 carry no RULES at all. They cannot be uncovered — the GATE already
    refuses one, so nothing could ever have shipped that way. The widening therefore costs
    nothing and buys only the TIMING, which was the whole point: the gate is the wrong place to
    learn a Must has no check, because by then the build is done and the fix is one line of
    authoring that should have been asked for while the author still had the file open
    -> "R:LATEREFUSAL".

    The gate rung is unchanged and stays: `freeze` runs earlier and cannot see a check deleted
    after the seal.
    """
    mapped = covers(node)
    return sorted(set(referents_of(node)) - set(mapped))


def bind(node: dict, reported: dict) -> tuple:
    """`(proven, unproven)` — a rule is proven only by a check the runner reported PASSING.

    `reported` is `{check_id: "pass" | "fail"}` from `extract_ids`. A check that is absent
    did not run; a check that failed did not prove. Neither counts.
    """
    proven, unproven = {}, {}
    for rule, checks in covers(node).items():
        passing = [c for c in checks if resolve_check(c, reported) == "pass"]
        (proven if passing else unproven)[rule] = passing or checks
    return proven, unproven


def unbound(node: dict, reported: dict) -> list:
    """Rules with no passing check — declared but unproven. The honest gap."""
    mapped = covers(node)
    proven, _ = bind(node, reported)
    return sorted(r for r in referents_of(node) if r not in proven or not mapped.get(r))


def qualify(where: str, name: str) -> str:
    """The ONE check-ID grammar: `a.b.c::name` (M1/M3, e16).

    `where` is junit's `classname` or a source path; both normalise to a dotted module so the
    extractor and the compiler cannot drift into two grammars (R:DRIFT — F1's lesson one level
    down). A bare name with no `where` stays bare, which is what makes old receipts readable.
    """
    where = str(where or "")
    if where.endswith(".py"):
        where = where[:-3].replace("\\", "/").replace("/", ".")
    where = where.strip(".")
    return f"{where}::{name}" if where else name


def resolve_check(cite: str, reported: dict) -> str:
    """`pass | fail | skip | ambiguous | absent` for one citation (M4/M5, e16).

    An exact hit wins, so a receipt written before the ID shape changed keeps binding and no
    gated node's citation has to be rewritten (R:SWEEP). Otherwise the citation is matched
    against the tail of every qualified ID: exactly one hit resolves to its outcome; two or
    more are AMBIGUOUS and prove nothing, which is the entire point — a name that means two
    tests cannot entitle a claim about one, and F7's masked failure is exactly that shape.
    """
    if cite in reported:
        return reported[cite]
    hits = [k for k in reported if k.rpartition("::")[2] == cite]
    if len(hits) == 1:
        return reported[hits[0]]
    return "ambiguous" if hits else "absent"


def extract_ids(path) -> dict:
    """`{check_id: "pass"|"fail"|"skip"}` from junit-xml. Unreadable output yields `{}`.

    junit-xml only at v1.0 (amendment A1). A runner that emits nothing usable leaves the
    receipt at a weaker kind, which A24 requires it to say out loud.

    Keyed by `classname::name`, never by the bare name (M1). The bare key let two same-named
    tests in different files collide and the last one parsed win, so a FAILING check could be
    recorded as PASSED — F7, demonstrated on this repo's own `test_sync_is_idempotent`.
    A `skipped` case records `skip` and never `pass` (M6, R:PHANTOM): the old test asked only
    for `failure`/`error`, so a test that never ran proved a Must.
    """
    import xml.etree.ElementTree as ET
    try:
        root = ET.parse(str(path)).getroot()
    except (OSError, ET.ParseError):
        return {}
    out = {}
    for case in root.iter("testcase"):
        name = case.get("name")
        if not name:
            continue
        if case.find("skipped") is not None:
            outcome = "skip"
        elif any(case.find(tag) is not None for tag in ("failure", "error")):
            outcome = "fail"
        else:
            outcome = "pass"
        out[qualify(case.get("classname"), name)] = outcome
    return out


# ================================================== brief — refs, not prose (e5)
#
# One rule decides this whole verb: **T2 is single-node** (FORMAT §4). A brief carries the
# subject's own body, T1 CARDs of its `depends_on`, the `#gives` fragments it `needs:`, and
# the five specs' bind lines. Nothing else can leak in, because nothing else is READ.
#
# Two units live here and they are not the same. FORMAT §7.2 states the ceiling in BYTES;
# PROPOSAL §3d states the lane budgets in TOKENS. The engine has no tokenizer and may not
# acquire one (D-1, stdlib only), so bytes are enforced and tokens are printed at a DECLARED
# ratio. A1 cost this project an amendment for exactly this class of mistake; naming the unit
# in the output is the whole fix.

BRIEF_BUDGET = {"quick": 8_000, "standard": 24_000, "deep": 40_000}
BYTES_PER_TOKEN = 4
PHASE_EVIDENCE = {"direction": "none", "build": "run-receipt",
                  "verify": "run-receipt,covers-bound"}
PHASE_OF = {"direction": "direction", "build": "build", "verify": "verify",
            "done": "verify", "dropped": "verify"}


def brief_budget(depth: str) -> int:
    return BRIEF_BUDGET.get(str(depth or "standard"), BRIEF_BUDGET["standard"])


# The roster's own beat -> `flow:` surface map, exactly as `agents/add-worker.md` §2 states it for a
# SPAWNED agent. Keeping one map means the sequential path cannot route a node to a different lens
# than a delegated one would — which was the whole defect: the selector existed only on the spawn.
LENS_SURFACE = {"direction": "design", "build": "build", "verify": "verify"}
# Verify takes a `flow: verify` lens first and falls back to `advisor` when none declares verify —
# again `add-worker.md` §2's rule, not a second one invented here.
LENS_FALLBACK = {"verify": "advisor"}


def _lens_terms(raw) -> list:
    """A frontmatter list field as terms, whether it arrived as `a, b` or as a real list."""
    items = raw if isinstance(raw, (list, tuple)) else str(raw or "").replace("\u00b7", ",").split(",")
    return [str(t).strip() for t in items if str(t).strip()]


def persona_candidates(graph: dict, node: dict, phase: str) -> list:
    """Roster entries that FIT this node's beat and kind: `(slug, task-kinds)`, sorted by slug.

    PRESENTS, never selects. The engine emits the fitting set and stops — ranking, choosing and
    loading a lens stay the orchestrating agent's judgment, which is `personas.md`'s NO-EXEC floor
    and not an obstacle to route around. Sorted by SLUG for the same reason: an alphabetical list
    is visibly not a ranking, and any other order would be the engine expressing a preference it
    has no basis for (R:ENGINEPICKS).

    Only frontmatter is read. A candidate's body never opens, so a brief cannot grow by the size
    of a persona it did not pick, and D-4 ("the corpus is referenced, never vendored") holds
    structurally rather than by a filter someone could forget.
    """
    fm = node["fm"] or {}
    kind = str(fm.get("kind") or "").strip()

    def fitting(surface: str) -> list:
        if not surface:
            return []
        out = []
        for cid, n in graph.items():
            pfm = n["fm"] or {}
            if pfm.get("type") != "Persona" or surface not in _lens_terms(pfm.get("flow")):
                continue
            kinds = _lens_terms(pfm.get("task-kinds"))
            # `kind:` is OPTIONAL on a Task. Gating the fit on a field most nodes never set would
            # leave the roster dark for most of a bundle, so an absent kind skips the kind gate
            # and `flow:` alone decides.
            if kind and kinds and kind not in kinds:
                continue
            out.append((_wave_slug(cid), ", ".join(kinds)))
        return sorted(out)

    return fitting(LENS_SURFACE.get(str(phase), "")) \
        or fitting(LENS_FALLBACK.get(str(phase), ""))


def bind_sections(root) -> list:
    """The five specs' `Decisions that bind`, sorted — the ONLY spec section a brief may cite.

    Sorted by filename, so A16's determinism is structural: there is no dict order, no
    `set`, and no `glob` order to depend on.
    """
    out = []
    for path in sorted((Path(root) / "specs").glob("*.md")):
        text = _section(read(path, "T2")["body"], "decisions-that-bind")
        if text:
            out.append((f"specs/{path.stem}", text))
    return out


def _flat(value) -> str:
    """A resolved ref's value as text. A `gives:` list renders as a list, not as a repr."""
    if isinstance(value, list):
        return "\n".join(f"- {v}" for v in value)
    if isinstance(value, dict):
        return "\n".join(f"{k}: {v}" for k, v in value.items())
    return str(value)


def _placeholder_only(text: str) -> bool:
    """True when EVERY content line of a resolved section is still `<…>` template scaffold.

    Same exclusion `placeholders_in` makes: a backticked span is code, not a placeholder. An
    empty section is not scaffold — it is empty, and that is a different silence (A8).
    """
    lines = [l for l in str(text).splitlines() if l.strip()]
    return bool(lines) and all(PLACEHOLDER.search(re.sub(r"`[^`]*`", "", l)) for l in lines)


def brief(root, cid: str, phase: str = None, for_subagent: bool = False,
          evidence: list = None) -> dict:
    """Compile the XML brief for one node. Deterministic, budgeted, and self-measuring."""
    root = Path(root)
    graph = scan(root)
    node = graph.get(cid)
    if node is None:
        return {"text": f'<task unresolved="true" id="{cid}"/>\nnext: add status\n',
                "bytes": 0, "hash": "", "nodes": 0, "budget": 0, "degraded": [],
                "phase": phase or "build", "depth": "standard"}

    fm = node["fm"] or {}
    slug = cid.rsplit("/", 1)[-1][:-3]
    ident = cid.strip("/")[:-3]
    # Same reason as `status`: the stored field never advances past `direction`, so a
    # frozen task briefed its DIRECTION beat and a non-Claude agent following the portable
    # `status`/`brief` path re-did direction on a sealed contract. An explicit `phase`
    # argument still wins — that is a caller naming a beat deliberately (A3).
    phase = phase or PHASE_OF.get(_beat_of(node), "build")
    depth = str(fm.get("depth") or "standard")
    budget = brief_budget(depth)
    body = read(node["path"], "T2")["body"]

    cards = []
    for dep in sorted(str(d) for d in (fm.get("depends_on") or [])):
        dcid, dnode, _ = resolve(graph, dep, cid)
        cards.append((dcid.strip("/")[:-3], read(dnode["path"], "T1")["card"] if dnode else None))
    refs = []
    for need in sorted(str(n) for n in (fm.get("needs") or [])):
        _, value, why = resolve(graph, need, cid)
        # Strip `.md` from the PATH only. Applying it to the whole ref ate the fragment's last
        # two characters — `#gives` became `#gi` — and a ref an agent cannot resolve back is
        # not a reference. The suite checked the resolved value and never the id.
        path, _, frag = need.partition("#")
        ident_ref = path.strip("/")[:-3] if path.endswith(".md") else path.strip("/")
        flat = None if why == "edge_unresolved" else _flat(value)
        refs.append((f"{ident_ref}#{frag}" if frag else ident_ref, flat,
                     flat is not None and _placeholder_only(flat)))
    binds = bind_sections(root)

    persona = None
    # BOTH keys. `advise` — the documented way to put a lens on a sequential beat — stamps
    # `advised_by:`, and this read looked only at `persona:`, so an advised node briefed its
    # worker with no lens at all while the gate's R:NOCOVERAGE accepted the same stamp as
    # "who reviewed the security". The gate treats the two as equals; so must the brief.
    lens_ref = fm.get("persona") or fm.get("advised_by")
    if lens_ref:
        # Roster resolution, the way `advise` and `wave` do it — NOT the path grammar. A lens is
        # written as a bare slug (`advise` validates exactly that against the Persona nodes), and
        # `resolve` reads a bare ref RELATIVE TO THE SOURCE: from `/tasks/x.md` the slug
        # `build-craftsman` normalised to `/tasks/build-craftsman`, which is neither a persona
        # nor even a `.md`. It missed every time, so no seeded lens has ever reached a brief.
        # A qualified ref (`/personas/x.md`) still resolves through the general grammar.
        pcid = pnode = None
        for candidate, cnode in graph.items():
            if (cnode["fm"] or {}).get("type") == "Persona" \
                    and _wave_slug(candidate) == str(lens_ref):
                pcid, pnode = candidate, cnode
                break
        if pnode is None:
            pcid, pnode, _ = resolve(graph, str(lens_ref), cid)
        # T0 only — `raw` is the frontmatter text `scan` already holds. The body is never
        # opened, so D-4 ("the corpus is referenced, never vendored") holds structurally
        # rather than by a filter that could be forgotten.
        if pnode:
            persona = (pcid.strip("/")[:-3], pnode["raw"])

    quoted = []
    for src in (evidence or []):
        src = Path(src)
        try:
            origin = str(src.relative_to(root.parent))
        except ValueError:
            origin = src.name          # never an absolute path: it would break A16 per machine
        try:
            quoted.append((origin, src.read_text()))
        except OSError as err:
            quoted.append((origin, f"unreadable: {err}"))

    nodes = 1 + len(cards) + len(binds) + (1 if persona else 0)
    constraints = ("never weaken a check · never edit a frozen `gives` · T2 is single-node · "
                   f"scope: {' · '.join(str(s) for s in (fm.get('scope') or ['—']))}")

    def assemble(drop_specs: bool, drop_cards: bool) -> str:
        out = [f'<task id="{ident}" phase="{phase}" depth="{depth}"'
               + (' standalone="true">' if for_subagent else ">"),
               f"  <objective>{fm.get('goal') or fm.get('title') or ''}</objective>"]
        if persona:
            out.append(f'  <persona ref="{persona[0]}" inject="frontmatter">')
            out += ["    " + l for l in persona[1].splitlines()]
            out.append("  </persona>")
        else:
            # SAY the omission. A brief with no lens was byte-identical to one whose lens had
            # nothing to add, so a worker could not tell "no expert was loaded" from "the expert
            # had no note" — and the receipt recorded neither. The check that was supposed to
            # guard this passed only because its fixture's slug was the literal word `unlensed`,
            # which the brief echoed back; with any other slug it matched nothing.
            # ...and name who COULD fit. The lens could only ever reach a node through `add
            # advise`, a verb no next-hint on the normal path names — the todo row refuses a
            # second verb by design (A12) — so 175 of this bundle's 190 lifecycle nodes carried
            # none. This closes that circle at the one surface that is already the agent's
            # instructions. With nothing to offer it stays byte-identical to what it always was.
            cands = persona_candidates(graph, node, phase)
            note = "no lens resolved for this node — the generic reading is in force"
            if not cands:
                out.append(f'  <persona ref="none" note="{note}" />')
            else:
                out.append(f'  <persona ref="none" note="{note} until one is recorded">')
                out += [f'    <candidate ref="personas/{ps}" task-kinds="{ks}"/>'
                        for ps, ks in cands]
                out.append(f'    <next>add advise {slug} --persona &lt;slug&gt;</next>')
                out.append("  </persona>")
        out.append("  <context>")
        for dcid, card in cards:
            if card is None:
                out.append(f'    <card id="{dcid}" unresolved="true"/>')
            elif drop_cards:
                out.append(f'    <card id="{dcid}" omitted="budget"/>')
            else:
                out.append(f'    <card id="{dcid}">')
                out += ["      " + l for l in card.splitlines()]
                out.append("    </card>")
        for ref, value, unauthored in refs:
            if value is None:
                out.append(f'    <ref id="{ref}" unresolved="true"/>')
            elif unauthored:
                # The section EXISTS and is still the shipped scaffold. Compiling it taught the
                # worker that `<the first decision that constrains the rest>` was a decision that
                # binds — five such blocks rode in every brief (filed as /specs/domain.md#D1).
                # The id stays so the section is still named and still openable (E4 · R:NOWAYBACK);
                # only the placeholder body goes. A short but REAL body is never touched
                # (R:PLACEHOLDERLOSS) — every content line must be scaffold to qualify.
                # The marker carries no prose: `unauthored="true"` reads like its two siblings
                # (`unresolved` · `omitted`), and a sentence explaining itself in every block
                # measured LARGER than the one-line scaffold it replaced — a trim that costs
                # bytes is not a trim.
                out.append(f'    <ref id="{ref}" unauthored="true"/>')
            else:
                out.append(f'    <ref id="{ref}" frozen="true">')
                out += ["      " + l for l in value.splitlines()]
                out.append("    </ref>")
        for scid, text in binds:
            rid = f"{scid}#decisions-that-bind"
            if drop_specs:
                out.append(f'    <ref id="{rid}" omitted="budget"/>')
            elif _placeholder_only(text):
                # The measured case (D1): all five seeded specs ship this section as one line of
                # scaffold, so every brief in a fresh bundle carried five `<ref>` blocks teaching
                # the worker that a placeholder was a decision that binds. Same rule as the
                # `needs:` refs above — the id stays, the scaffold body goes.
                out.append(f'    <ref id="{rid}" unauthored="true"/>')
            else:
                out.append(f'    <ref id="{rid}">')
                out += ["      " + l for l in text.splitlines()]
                out.append("    </ref>")
        out.append("  </context>")
        # The subject is emitted VERBATIM and unindented. R:SILENTCUT forbids trimming it, and
        # reformatting it would be a quieter version of the same thing.
        out.append(f'  <subject id="{ident}">')
        out.append(body.rstrip("\n"))
        out.append("  </subject>")
        obs = observes({"body": body})
        if obs:
            out.append("  <observes>")
            out += [f'    <o id="{o["id"]}" covers="{",".join(o["covers"])}" action="{o["action"]}">'
                    f'{o["signal"]} · {o["window"]} · {o["threshold"]}</o>' for o in obs]
            out.append("  </observes>")
        out.append(f"  <constraints>{constraints}</constraints>")
        out.append(f'  <evidence require="{PHASE_EVIDENCE[phase]}"/>')
        for origin, text in quoted:
            # §7.5 · law L6 — outside content is DATA. It sits outside `<context>`, quoted and
            # labelled, so it can never be read as instruction.
            out.append(f'  <evidence origin="{origin}" trust="data">')
            out += ["  > " + l for l in text.splitlines()]
            out.append("  </evidence>")
        if for_subagent:
            out.append(f"  <close>add run {slug} -- &lt;cmd&gt; · then add gate {slug}</close>")
        out.append("</task>")
        return "\n".join(out) + "\n"

    def finish(payload: str, degraded: list, over: bool) -> tuple:
        # The hash covers the payload only: the cost line quotes the hash, and a hash of a
        # string containing itself does not exist.
        digest = "sha256:" + hashlib.sha256(payload.encode()).hexdigest()[:16]
        tail = (f"cost: ###### B / {budget} B budget · ~##### tok / "
                f"~{budget // BYTES_PER_TOKEN} tok (declared {BYTES_PER_TOKEN} B/tok) · "
                f"{nodes} nodes · {digest}"
                + ("\n  DEGRADED (A5): " + " → ".join(degraded) if degraded else "")
                + ("\n  OVER BUDGET — reported, not truncated (R:SILENTCUT)" if over else "")
                + f"\nnext: add run {slug} -- <cmd>   # then add gate {slug}\n")
        # Fixed-width placeholders: the printed size includes the line printing it, so the
        # substitution must not change the length. One pass, no fixed-point iteration.
        size = len(payload.encode()) + len(tail.encode())
        tail = tail.replace("######", f"{size:>6}", 1).replace("#####", f"{size // BYTES_PER_TOKEN:>5}", 1)
        return payload + tail, size, digest

    ladder = [((False, False), None),
              ((True, False), "specs → refs"),
              ((True, True), "dep cards → refs")]
    degraded, text, size, digest = [], "", 0, ""
    for flags, label in ladder:
        if label:
            degraded.append(label)
        payload = assemble(*flags)
        text, size, digest = finish(payload, degraded, False)
        if size <= budget:
            break
    else:
        text, size, digest = finish(payload, degraded, True)

    return {"text": text, "bytes": size, "hash": digest, "nodes": nodes,
            "budget": budget, "degraded": degraded, "phase": phase, "depth": depth}


def brief_stamp(root, cid: str, by: str = "cli") -> tuple:
    """Record that the brief ENTERED the build: `act: brief` on a frozen Task. `(digest, note)`.

    `brief()` — the FUNCTION — is pure, which is why `gate` may call it; THIS function is the
    write, and the `cli.py` wrapper for `add brief` calls both, so the VERB writes on a frozen
    Task even though the compile does not. Saying "`brief` is read-only" without saying which
    `brief` sent a reviewer to run it against a live bundle during an audit. What is written
    here is what `gate`'s R:UNBRIEFED refusal reads. Only a frozen Task records an
    entry — before the freeze there is no sealed direction for a brief to enter, and depth
    `quick` never demands one (the gate exempts it), though recording one is harmless.
    """
    root = Path(root)
    graph = scan(root)
    node = graph.get(cid)
    if node is None:
        return None, f"no such node: {cid}\nnext: add status"
    fm = node.get("fm") or {}
    slug = cid.rsplit("/", 1)[-1][:-3]
    if fm.get("type") != "Task" or not _is_frozen(node):
        return None, (f"brief compiled, not recorded — only a frozen Task records its build "
                      f"entry, and `{slug}` is not one yet"
                      f"\nnext: add freeze {slug}, then add brief {slug}")
    digest = brief(root, cid)["hash"]
    _transition(root, cid, appends=[("verified",
        f'{{ by: "{_oneline(by)}", at: {_today()}, act: brief, authority: process, '
        f'brief: "{digest}" }}')])
    return digest, (f"brief {digest} recorded as the build entry"
                    f"\nnext: add run {slug} -- <cmd>")


REFUTE_TIERS = ("T1", "T2", "T3")
# The tiers that can SIGN the refute rung — `REFUTE_TIERS` minus the builder's own read.
# Derived, not restated: a literal here would not follow if the ladder ever moved.
SIGNING_TIERS = tuple(t for t in REFUTE_TIERS if t != "T1")
# The tiers a SESSION can sign for. T0 is nobody — no stamp exists to carry it; T4 is a protected
# holdout the builder cannot read, which a prompt cannot provide and so a stamp must not claim
# (verify.md's ladder: "a CI recipe, not shipped"). The engine records the tier as a CLAIM, exactly
# as it records `by:` — dogfood-and-measure F2 found both refutes on the shipping milestone were the
# builder's own read with the tier written in free text inside `--by`, uncountable. A flag makes the
# claim countable; only `by:` beside it says whether it is true.


def refute(root, cid: str, by: str, held: bool, finding: str = None, probes: int = 0,
           note: str = None, tier: str = None, changed: str = None) -> tuple:
    """Record a refute-read of a green: who tried to break it, against which receipt, what they
    found. NO-EXEC — a lens on a green exactly as `advise` is a lens on a beat. `(stamp, note)`.

    The stamp names the receipt it read (`receipt:`), so its place in the chronology is decidable
    from `verified[]` order alone — the argument `brief_stamp` makes for the build entry. It binds
    PRESENCE: a named party tried, when, against which run, with how many probes. It cannot bind
    honesty or the quality of the probes (FORMAT §10); the tier ladder and the persona do that.
    It writes no verdict, moves no `status:`, lowers no floor (R:NOVERDICT).

    `tier:` and `changed:` are recorded when given and absent otherwise — never defaulted, since a
    default would invent a claim nobody made. `changed:` names what the probes moved in the build or
    the spec while the outcome still HELD (no frozen rule forbade it): dogfood-and-measure F4 found
    `--found` alone undercounts what probes do, and the bench trigger reads this key. The gate reads
    neither (`_refute_of`, law 3: a notary that weighed a tier would be a guard).
    """
    root = Path(root)
    # Membership on the RAW value — the T2 refute of this task found the library stripping
    # `" T2 "` to a stamp argparse refuses; the two doors now agree. `""` stays absent (A4).
    tier = tier if tier else None
    if tier is not None and tier not in REFUTE_TIERS:
        return None, (f'`--tier {tier}` names no session that can sign — a tier is one of '
                      f'{" | ".join(REFUTE_TIERS)} (T0 is nobody, T4 is a CI recipe) -> "R:BADTIER"'
                      f"\nnext: add refute {cid.rsplit('/', 1)[-1][:-3]} --tier T2 …")
    graph = scan(root)
    node = graph.get(cid)
    if node is None:
        return None, f"no such node: {cid}\nnext: add status"
    slug = cid.rsplit("/", 1)[-1][:-3]
    fm = node.get("fm") or {}
    if fm.get("type") != "Task":
        return None, (f'R:NOTATASK only a Task carries a run receipt to refute — `{cid}` is a '
                      f'{fm.get("type")} -> "R:NOTATASK"\nnext: add status')
    if not _is_frozen(node):
        return None, (f"`{slug}` was never frozen — there is no approved intent to read the green "
                      f'against -> "R:UNSEALED"\nnext: add freeze {slug}, build, add run {slug}, then refute')
    receipt, receipt_cid = latest_receipt(root, cid)
    if receipt is None:
        return None, (f"`{slug}` has no run receipt — a refute reads a green, and nothing has run "
                      f'-> "R:NORECEIPT"\nnext: add run {slug} -- <cmd>, then add refute {slug}')
    finding = (finding or "").strip()
    if held and finding:
        return None, ('one outcome: `--held` says no input broke it, `--found` names the one that did '
                      f'-> "R:NOFINDING"\nnext: add refute {slug} --held, or --found "<input>"')
    if not held and not finding:
        return None, ('a refutation names the input/state/interleaving that makes the green wrong — '
                      f'a bare "it fails" is a category, not evidence -> "R:NOFINDING"'
                      f'\nnext: add refute {slug} --found "<the input the bound checks never exercise>"')
    text = finding if not held else (note or "").strip()
    text = _oneline(text).replace('"', "'")
    moved = _oneline((changed or "").strip()).replace('"', "'")
    stamp = (f'{{ by: "{_oneline(by)}", at: {_today()}, act: refute, authority: process, '
             f'outcome: {"held" if held else "refuted"}, probes: {int(probes or 0)}, '
             f'receipt: {receipt_cid}' + (f", tier: {tier}" if tier else "")
             + (f', note: "{text}"' if text else "")
             + (f', changed: "{moved}"' if moved else "") + " }")
    _, err = _transition(root, cid, appends=[("verified", stamp)])
    if err:
        return None, err + "\nnext: add status"
    render_evidence(root, cid)
    if held:
        return stamp, (f"refute recorded against {receipt_cid}: held ({int(probes or 0)} probe(s)) — "
                       f"NO-EXEC, no verdict\nnext: add gate {slug} PASS --by \"<name>\"")
    return stamp, (f"refute recorded against {receipt_cid}: REFUTED — {text}\n"
                   f"next: fix the build (or refreeze with the edge this exposes), add run {slug} -- <cmd>, "
                   f"then add refute {slug} again")



# ================================ EVIDENCE and LESSONS — views of the record, never a store
#
# FORMAT §5 said "EVIDENCE receipt / gate · LESSONS harvested at done", the placeholder guard
# skipped both sections because "the run and the close fill them", and nothing did: on this
# bundle 88 of 113 done tasks carried `receipt: <runs/<n>.md>` beside a `verified[]` that named
# the real receipt, and 64 carried `- <lesson> -> add learn <lens>` beside specs full of deltas
# citing them. A promise two readers relied on and no writer kept. The sections are VIEWS — the
# record is `verified[]`, the run files and the specs' `## Deltas`; the verb that makes a fact
# writes its keyed line, and `doctor --sync` recomputes both for the backlog. Two rules bound the
# writer: a line the engine did not produce is never moved (R:TWOHOMES — a human note beside the
# view survives byte-for-byte), and a line the record does not support is never written
# (R:MANUFACTURED — no refute stamp, no `refute:` line; `none recorded` is a fact about a closed
# node, not an invention).

EVIDENCE_KEYS = ("receipt", "refute", "gate")
EVIDENCE_SCAFFOLD = ("<runs/<n>.md>", "<PASS | RISK-ACCEPTED | HARD-STOP>")
LESSON_SCAFFOLD = "<lesson> -> add learn <lens>"
HARVESTED_LINE = re.compile(r"^- (\[[a-z]+ · [A-Za-z0-9?-]+ · (?:open|folded|rejected)\]|none filed\b)")


def _section_span(lines: list, heading: str):
    """`(start, end)` line indexes of the body of `## <heading>` — heading-exclusive, stopping
    at the next `## ` — or `None` when the section is absent. Mirrors `_section_of`."""
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## "):
            if start is not None:
                return start, i
            if line.strip().lower() == f"## {heading}".lower():
                start = i + 1
    return (start, len(lines)) if start is not None else None


def _set_keyed_line(body: str, section: str, key: str, value: str) -> str:
    """Replace the ONE `<key>:` line inside `## <section>` with `<key>: <value>`, or insert it in
    `EVIDENCE_KEYS` order. Every other byte of the body is returned as it was (R:TWOHOMES)."""
    lines = body.splitlines(keepends=True)
    span = _section_span(lines, section)
    if span is None:
        return body
    start, end = span
    new = f"{key}: {value}\n"
    for i in range(start, end):
        if lines[i].startswith(f"{key}:"):
            lines[i] = new
            return "".join(lines)
    order = list(EVIDENCE_KEYS)
    after = [k for k in order[:order.index(key)]] if key in order else []
    at = start
    for i in range(start, end):
        if any(lines[i].startswith(f"{k}:") for k in after):
            at = i + 1
    lines.insert(at, new)
    return "".join(lines)


def _latest_stamp(node: dict, act: str):
    stamps = [s for s in ((node.get("fm") or {}).get("verified") or []) if isinstance(s, dict)]
    return next((s for s in reversed(stamps) if s.get("act") == act), None)


def render_evidence(root, cid: str, graph: dict = None) -> bool:
    """Write the `## EVIDENCE` view from the record. `True` when a byte changed.

    `receipt:` is the newest run, `refute:` the latest refute stamp, `gate:` the latest gate stamp
    — each written only when the record holds it. On a `done` node a key the record never
    produced reads `none recorded`: the record is closed, and its silence is a fact, not a guess.
    """
    root = Path(root)
    graph = scan(root) if graph is None else graph
    node = graph.get(cid)
    if node is None or (node.get("fm") or {}).get("type") != "Task":
        return False
    path = root / cid.lstrip("/")
    n = read(path, "T2")
    body = n["body"]
    if _section_span(body.splitlines(keepends=True), "EVIDENCE") is None:
        return False
    closed = str((node.get("fm") or {}).get("status")) == "done"
    receipt, rcid = latest_receipt(root, cid)
    if receipt is not None:
        body = _set_keyed_line(body, "EVIDENCE", "receipt",
                               f"{rcid} · kind: {receipt.get('kind')} · {receipt.get('ids')} · "
                               f"exit {receipt.get('exit')} · {receipt.get('at')}")
    elif closed:
        body = _set_keyed_line(body, "EVIDENCE", "receipt", "none recorded")
    ref = _latest_stamp(node, "refute")
    if ref is not None:
        body = _set_keyed_line(body, "EVIDENCE", "refute",
                               f"{ref.get('outcome')} · {ref.get('probes', 0)} probe(s)"
                               + (f" · tier {ref['tier']}" if ref.get("tier") else "")
                               + f" · by {ref.get('by')} · against {ref.get('receipt')} · {ref.get('at')}"
                               + (f" · {ref['note']}" if ref.get("note") else "")
                               + (f" · changed: {ref['changed']}" if ref.get("changed") else ""))
    gate_stamp = _latest_stamp(node, "gate")
    if gate_stamp is not None:
        body = _set_keyed_line(body, "EVIDENCE", "gate",
                               f"{gate_stamp.get('outcome')} · authority {gate_stamp.get('authority')} · "
                               f"by {gate_stamp.get('by')}"
                               + (f" · receipt {gate_stamp['receipt']}" if gate_stamp.get("receipt") else "")
                               + f" · {gate_stamp.get('at')}"
                               + (f" · {gate_stamp['reason']}" if gate_stamp.get("reason") else ""))
    elif closed:
        body = _set_keyed_line(body, "EVIDENCE", "gate", "none recorded")
    if body == n["body"]:
        return False
    write(path, f"---\n{n['raw']}\n---\n{body}")
    return True


def _cites_task(evidence: str, slug: str) -> bool:
    """The citation rule: a lesson lands on a task when its evidence names the task's node
    (`/tasks/<slug>.md`) or its sidecar (`/tasks/<slug>.d/`). A test file, a source path or a
    receipt of another task names no task."""
    return re.search(rf"(^|[^A-Za-z0-9_-])tasks/{re.escape(slug)}(\.md|\.d/|#|$|[\s):,])",
                     evidence or "") is not None


def harvest_lessons(root, cid: str) -> bool:
    """Write the `## LESSONS` view: every delta, at any status, whose evidence cites this task.
    Replaces the scaffold line and any previously harvested line; an authored bullet stays.
    `True` when a byte changed. With no citing delta the section says so — `none filed` — and
    never borrows a lesson that cites something else (R:MANUFACTURED)."""
    root = Path(root)
    path = root / cid.lstrip("/")
    slug = cid.rsplit("/", 1)[-1][:-3]
    n = read(path, "T2")
    lines = n["body"].splitlines(keepends=True)
    span = _section_span(lines, "LESSONS")
    if span is None:
        return False
    harvested = []
    for status in DELTA_STATUSES:
        items, _ = deltas(root, status)
        for d in items:
            m = DELTA_EVIDENCE.search(d[2])
            if m and _cites_task(m.group(0), slug):
                harvested.append(f"- [{d[0]} · {d.id or '-'} · {status}] {d[2]}\n")
    if not harvested:
        harvested = [f"- none filed — no lesson cites {cid} "
                     f"(add learn <lens> \"<lesson>\" --evidence {cid})\n"]
    start, end = span
    kept = [l for l in lines[start:end]
            if not (LESSON_SCAFFOLD in l or HARVESTED_LINE.match(l))]
    # trailing blank lines belong to the section's tail, not to its content
    tail = []
    while kept and not kept[-1].strip():
        tail.insert(0, kept.pop())
    new = lines[:start] + kept + harvested + tail + lines[end:]
    body = "".join(new)
    if body == n["body"]:
        return False
    write(path, f"---\n{n['raw']}\n---\n{body}")
    return True


def evidence_scaffold(root, graph: dict = None, body_of=None) -> list:
    """Every `done` Task still carrying an EVIDENCE or LESSONS scaffold line. `[(cid, section)]`.
    `body_of` lets `doctor` share its one-read-per-body cache (R:SECONDSCAN)."""
    root = Path(root)
    graph = scan(root) if graph is None else graph
    body_of = body_of or (lambda path: read(path, "T2")["body"])
    out = []
    for cid, node in sorted(graph.items()):
        fm = node.get("fm") or {}
        if fm.get("type") != "Task" or str(fm.get("status")) != "done":
            continue
        body = body_of(root / cid.lstrip("/"))
        ev = _section_of(body, "EVIDENCE")
        if any(s in ev for s in EVIDENCE_SCAFFOLD):
            out.append((cid, "EVIDENCE"))
        if LESSON_SCAFFOLD in _section_of(body, "LESSONS"):
            out.append((cid, "LESSONS"))
    return out


# ============================================ gate — the verdict, and its refusals (e13)
#
# This verb should have existed since e4. Every gate in this project's history was recorded by
# hand-appending a stamp through the private `_transition`, so none of the three refusals
# PROPOSAL specifies for `gate` had ever run against anything.
#
# It is also where e12's M3 lands. That rule reads "`unbound` is part of every gate's report" —
# and it was gated PASS while no gate report existed. The rule was never wrong; it had nowhere
# to be true.
#
# Refusing is not guarding (law 3). A refusal never stops a human from writing the stamp
# themselves with their own authority; it stops the ENGINE from manufacturing a record that its
# own evidence does not support. The measured case for the strict form: run against this
# project's own history, M2 would have refused 8 gates — exactly the 8 tasks F2 found
# labelled-but-not-proven, and zero of the 7 well-bound M1 tasks. It fires on the defect and
# nothing else, so `RISK-ACCEPTED` with a recorded reason is the only degradation needed.

VERDICTS = ("PASS", "RISK-ACCEPTED", "HARD-STOP")
# The verdicts that CLOSE. `gate` refuses none of the three — a security finding is always a
# HARD-STOP, so recording the stop must never be the hard part — but a stop is not a shipment.
# `done` counted that a gate HAPPENED and never read what it DECIDED, so HARD-STOP, the one
# verdict every integrity refusal deliberately lets through, was also the one that closed a node
# with a red run. The stop stays writable at the gate and stops entitling the terminal write.
CLOSING_VERDICTS = ("PASS", "RISK-ACCEPTED")


def orphans(root, graph: dict = None) -> list:
    """Receipt nodes that no `verified[]` stamp points at — unreachable evidence (R:ORPHAN).

    A receipt IS a node (`type: Run`), so this reads the compiled graph rather than walking
    `runs/*.md`. e8's R:SECONDSCAN is what forced the question, and the graph was always the right
    basis: a receipt outside `runs/` was invisible to the old walk, and a malformed one with no
    frontmatter now surfaces as `missing_frontmatter` instead of being counted as evidence.
    Asserted equal to the directory walk on the live bundle before the basis was changed.
    """
    graph = scan(root) if graph is None else graph
    cited = set()
    for node in graph.values():
        for stamp in ((node["fm"] or {}).get("verified") or []):
            if isinstance(stamp, dict) and stamp.get("receipt"):
                cited.add(str(stamp["receipt"]).lstrip("/"))
    return sorted(cid for cid, node in graph.items()
                  if (node["fm"] or {}).get("type") == "Run" and cid.lstrip("/") not in cited)


def _latest_receipt_where(root, cid: str, floor: bool) -> tuple:
    """Newest receipt of a task that IS (floor=True) or IS NOT a regression-floor receipt."""
    root = Path(root)
    slug = cid.rsplit("/", 1)[-1][:-3]
    runs = sorted((root / f"tasks/{slug}.d/runs").glob("*.md"),
                  key=lambda p: int(p.stem) if p.stem.isdigit() else 0)
    for p in reversed(runs):
        fm = read(p, "T0")["fm"] or {}
        receipt = fm.get("receipt") or {}
        if bool(receipt.get("floor")) == floor:
            return fm.get("receipt"), "/" + str(p.relative_to(root))
    return None, None


def latest_receipt(root, cid: str) -> tuple:
    """`(receipt_dict, cid)` for the newest NARROW receipt of a task, or `(None, None)`.

    A regression-floor receipt (`floor: regression`, regression-floor) is never the gated one:
    the full suite passed off as the bound narrow run would lose the narrow run's binding behind
    it (R:FLOORASGATE). `latest_floor_receipt` answers for the floor.
    """
    return _latest_receipt_where(root, cid, floor=False)


def latest_floor_receipt(root, cid: str) -> tuple:
    """`(receipt_dict, cid)` for the newest regression-floor receipt, or `(None, None)`."""
    return _latest_receipt_where(root, cid, floor=True)


INTEGRITY_REFUSALS = (
    "unsealed", "drift", "placeholders", "undeclared_sensitive", "phantom_scope",
    "explore_drift", "explore_placeholders",
    # R:UNFROZEN_EXPLORE is deliberately NOT here: it refuses UNCONDITIONALLY, HARD-STOP
    # included, which is stricter than this tier. Routing it through `_binds` would have
    # NARROWED an existing refusal to buy tidiness -> "R:WIDEN".
)
EVIDENCE_REFUSALS = (
    "stale_receipt", "failed_run", "unbound_covers", "hollow_explore", "no_security_lens",
    # `unbriefed` sits HERE, not in INTEGRITY, and the placement was decided by another task's
    # frozen contract: brief-gate's M3 is "a verdict is how a node LEAVES a bad state", pinned by
    # `test_non_pass_verdicts_are_never_blocked`. That Reject is not this task's to weaken. It also
    # reads correctly on the merits — a missing brief says the BUILD was driven without the compiled
    # prompt, which is a fact about the run, and the seal, the drift check and the placeholder guard
    # all still bind every verdict, so the RECORD cannot be forged either way.
    "unbriefed",
    # the refute rung: same class, same argument — signing for an unrefuted green is what
    # RISK-ACCEPTED is for, and HARD-STOP must never get harder to write down.
    "unrefuted",
    # the floor rung (regression-floor): same class — a host suite never run is what a signed
    # RISK-ACCEPTED exists to record, and HARD-STOP must never get harder to write down.
    "floor_unrun",
    # consumers-go-stale: same class — a consumer of a moved contract can sign for it knowingly.
    "stale_needs",
)


def _binds(refusal: str, verdict: str) -> bool:
    """Does this refusal run for this verdict?

    Every integrity refusal in `gate` used to be written `verdict == "PASS"`, sixteen times over.
    Measured 2026-09-01: a Task created seconds earlier — still every template slot, never frozen,
    never briefed — reached `done` in three calls (`run -- true`, `gate RISK-ACCEPTED`, `done`).
    That is #206's finding one verdict over: skipping the seal did not FAIL the post-freeze guards,
    it SWITCHED THEM OFF -> "R:HATCH".

    The split is "would a verdict here be a FABRICATED record, or merely an OPTIMISTIC one?"

      * INTEGRITY protects the RECORD — was it frozen, did the contract drift, is the body still a
        template, did the build touch an undeclared sensitive path. Binds every verdict that
        APPROVES or CLOSES. Accepting a risk is not a way around the seal.
      * EVIDENCE judges the RUN — a stale receipt, a non-zero exit, an unbound `covers:`, an open
        question. Binds PASS only: signing for imperfect evidence is precisely what RISK-ACCEPTED
        is FOR, and three of these refusals already name it as their own remedy.

    HARD-STOP is refused by neither. It never closes a task, so refusing it would only stop a
    finding being written down — and a security finding is always a HARD-STOP.
    """
    if verdict == "HARD-STOP":
        # Interviewed 2026-09-03, A3 marked `correct`. The stop still binds NO evidence refusal —
        # writing down a finding must never get hard, and a security finding is always a
        # HARD-STOP. But it is a RECORD against a node, and a record needs the seal that says
        # someone approved the node's existence: 3.3.0 made that argument for RISK-ACCEPTED and
        # it holds here. Everything else stays open.
        return refusal == "unsealed"
    if refusal in INTEGRITY_REFUSALS:
        return True
    if refusal in EVIDENCE_REFUSALS:
        return verdict == "PASS"
    raise KeyError(f"unclassified gate refusal: {refusal!r}")


def gate(root, cid: str, verdict: str, by: str, authority: str = None,
         reason: str = None) -> tuple:
    """Record a verdict, or refuse and say what would make it pass. `(ok, note)`."""
    root = Path(root)
    slug = cid.rsplit("/", 1)[-1][:-3]

    def refuse(why: str, fix: str) -> tuple:
        return None, f"cannot record `{verdict}` — {why}\nnext: {fix}"

    if verdict not in VERDICTS:
        return refuse(f"unknown verdict {verdict!r}",
                      f"add gate {slug} <{' | '.join(VERDICTS)}>")
    graph = scan(root)
    if cid not in graph:
        return refuse(f"no such node: {cid}", "add status")
    if verdict in CLOSING_VERDICTS and (carry_error := _carry_problem(graph, cid, accepted=True)):
        return refuse(carry_error, f"repair and refreeze {slug}'s `carries:` mapping")
    if verdict != "PASS" and not reason:
        return refuse(f"a {verdict} with no reason is a PASS in disguise",
                      f'add gate {slug} {verdict} --reason "<why>"')

    # Both halves of the security floor read the COMPUTED floor, not the literal `sensitivity:` key.
    # `authority_for` is `max(sensitivity floor, A17 sensitive-path floor)`, and `human` is reachable
    # only two ways: `sensitivity: security`, or a `scope:` entry matching `index.md`'s
    # `sensitive_paths:`. Reading the key alone made the bundle's own path classification advisory —
    # a task editing a sensitive path with no declared sensitivity could sign itself away.
    sfm = graph[cid]["fm"] or {}
    security_floored = authority_for(graph, cid) == "human"
    closes = verdict == "PASS"      # the ONE place the verdict is compared; refusals go via _binds
    if (_carry_entries(sfm)[0] or _has_carry_history(sfm)) and security_floored and closes \
            and not _human_signer(by):
        return refuse("R:LOWERED_CARRY_AUTHORITY this destination needs its own human gate signer",
                      f'add gate {slug} PASS --by "human:<name>"')

    # R:SECURITYFOLD — a security risk is a HARD-STOP, never a signed acceptance. The floor already
    # puts authority at `human`; this makes the other half structural rather than prose: the finding
    # cannot be folded into a RISK-ACCEPTED, so no authority level and no persona can buy it back.
    # PASS (a clean review) and HARD-STOP (the stop) are both still open — only sign-it-away closes.
    if verdict == "RISK-ACCEPTED" and security_floored:
        return refuse("a security risk cannot be folded into a RISK-ACCEPTED — the security floor is HARD-STOP",
                      f'resolve it (add gate {slug} PASS) or stop it (add gate {slug} HARD-STOP --reason "<the finding>")')

    # R:NOCOVERAGE (A2) — the coverage half of the security floor. A security-floored node cannot be
    # signed PASS without a named lens (`persona:` or `advised_by:`): "who reviewed the security"
    # becomes a recorded, enforced fact, not a doctor nudge. Mirrors R:SECURITYFOLD — the softer
    # data/architecture floors (`plan`) stay `info` findings in `doctor`. The engine binds lens
    # PRESENCE; whether it is the *right* lens is the AI's selection and the persona's `use-when`.
    if _binds("no_security_lens", verdict) and security_floored \
            and not sfm.get("persona") and not sfm.get("advised_by"):
        return refuse("a security PASS needs a named lens — no `persona:`/`advised_by:` is recorded, "
                      "so no one is on record as having reviewed the security -> \"R:NOCOVERAGE\"",
                      f'assign a security lens (add advise {slug} --persona <p>, or run it in a '
                      f'lensed wave), then add gate {slug} PASS')

    node_body = lambda n: read(n["path"], "T2")["body"]
    receipt, receipt_cid = latest_receipt(root, cid)

    # The sources path (task sources-receipt) — a findings-only explore gates on its cited
    # `## FINDINGS`, not on a run receipt. A recorded receipt keeps the normal path in charge
    # (E3); only Musts bind (E1 — extra findings neither bind nor block). The mechanical half
    # is bound here — every frozen question named and evidenced; whether the answer SUFFICES
    # stays the gate-caller's judgment, exactly as check adequacy does.
    if receipt is None and str(sfm.get("kind") or "") == "explore":
        # Review of PR #197 — the sources path inherits the receipt path's seal discipline.
        # The freeze IS this lane's one human approval (questions + budget, R:UNBOUNDED), so
        # an unfrozen explore has nothing approved to gate against; and a post-freeze edit to
        # a frozen question is the same silent tamper the drift refusal below exists for —
        # the lane whose contract IS the questions cannot be the one lane free to rewrite them.
        sealed_q = sealed_direction(sfm)
        if not sealed_q:
            return refuse("the questions were never frozen — this lane's one human approval "
                          '(questions + budget) has not happened -> "R:UNFROZEN_EXPLORE"',
                          f'add freeze {slug} --by "<name>", then add gate {slug} PASS')
        node = read(graph[cid]["path"], "T2")
        if _binds("explore_drift", verdict) and direction_digest(node) != sealed_q:
            return refuse("RULES/CHECKS drifted after the freeze that approved them — a frozen "
                          "contract changes by refreezing, never by a silent edit",
                          f'add freeze {slug} --by "<name>" to record the change, or '
                          f'add reopen {slug} --to direction --reason "<why the contract moved>"')
        stubs = placeholders_in(node)
        if stubs and _binds("explore_placeholders", verdict):
            return refuse("the node still carries template placeholders: " + " · ".join(stubs),
                          f"author {slug}'s RULES and CHECKS, then add gate {slug} PASS")
        body = node["body"]
        # Through the ONE reader of "is this id authored": `rules_of` and `edges_of` already read
        # here, and this raw findall made the gate demand a finding for an `M9` spelled only inside
        # a fence while the fold rung called the same id unauthored (E30, twenty-sixth refute E40).
        musts = re.findall(r"^-\s*(M\d+)\b", _section_of(_authored_rules(body), "RULES"), re.M)
        findings = _section_of(body, "FINDINGS")
        # A finding closes a question only with a REAL ref — `(evidence: )`, the template's
        # `(evidence: <ref>)`, and prose that merely contains the word all stay open.
        closed = [m for m in musts
                  if re.search(rf"answers {m}\b[^\n]*\(evidence:\s*[^)\s<][^)]*\)", findings)]
        opens = [m for m in musts if m not in closed]
        if _binds("hollow_explore", verdict) and (not musts or opens):
            named = ", ".join(opens) if opens else "(no frozen questions at all)"
            return refuse("open questions hold the PASS — no evidence-carrying finding answers: "
                          f'{named} -> "R:HOLLOW_EXPLORE"',
                          f"write the missing `F<n> (answers M<n>) · <finding> · (evidence: <ref>)` "
                          f"lines in ## FINDINGS, or "
                          f'add gate {slug} RISK-ACCEPTED --reason "open: {named}"')
        authority = authority_for(graph, cid)
        extra = (f', kind: sources, closed: "{len(closed)}/{len(musts)}"'
                 if closes else "")
        stamp = (f'{{ by: "{_oneline(by)}", at: {_today()}, act: gate, authority: {authority}, '
                 f'outcome: {verdict}{extra}'
                 + (f', reason: "{_oneline(reason)}"' if reason else "") + " }")
        _, t_err = _transition(root, cid, appends=[("verified", stamp)])
        if t_err:
            return None, t_err + "\nnext: add status"
        render_evidence(root, cid)
        if closes:
            done(root, cid)
            render_card(root, cid)
            tail = f"{cid} is done"
        else:
            tail = f"{verdict} recorded; {slug} stays in `{sfm.get('status')}`"
        return True, (f"gate {verdict} recorded at authority `{authority}`"
                      f"\n  evidence: sources — {len(closed)}/{len(musts)} questions closed"
                      f"\n{tail}\nnext: add status")

    if receipt is None:
        return refuse("no receipt has been recorded", f"add run {slug} -- <cmd>")

    # Refusal 0 (e17 M1/M2, R:GREENLIE) — the receipt says the run failed.
    #
    # F17: every other refusal here reads what the receipt CLAIMS and none read whether the
    # command survived. A suite can report its checks green while the process exits non-zero
    # — a collection error, a plugin crash, a coverage threshold, a post-run hook — so `bind`
    # is satisfied, `unbound` is empty, and the gate passes over a receipt that says FAILED.
    # Ordered before freshness because a run that failed is the more actionable of the two
    # facts: re-running fixes staleness anyway, and a stale red receipt reported as merely
    # stale sends the author to re-run without saying what to fix.
    # Only PASS is refused (M3, R:TRAP) — a verdict is how a node LEAVES a bad state, and
    # RISK-ACCEPTED already forces a written reason, which is the honest escape hatch.
    # Compared as TEXT, deliberately: `run` records an int and the T0 parser reads it back as
    # `'0'`, so an `exit not in (0, None)` test refuses every gate in the bundle. Caught by the
    # non-regression half of M1 — the check that a green receipt still passes.
    code = str(receipt.get("exit", "0")).strip()
    if _binds("failed_run", verdict) and code not in ("0", "", "None"):
        # `computation:` is a top-level key of the Run node, a sibling of `receipt:` — not a
        # field inside it. Reading it off the receipt dict silently yields None, which is how a
        # refusal loses the one detail that makes it actionable (R:MUTE).
        ran = (read(root / receipt_cid.lstrip("/"), "T0")["fm"] or {}).get("computation")
        return refuse(f"the receipt records a failed run — `{receipt_cid}` exited {code} "
                      f"(`{ran or 'command not recorded'}`)",
                      f"fix the run and re-record it — add run {slug} -- <cmd>, or "
                      f'add gate {slug} RISK-ACCEPTED --reason "<why a failed run is acceptable>"')

    # Refusal 1 (M1) — a verdict over changed code is evidence of nothing.
    #
    # A node declaring no `scope:` has nothing to be stale ABOUT, and §3d's quick and doc lanes
    # both allow one. That is not-applicable, not failed — but it must be SAID, and it must not
    # become a way to dodge freshness: scope declared with no digest recorded stays a refusal.
    declared_scope = _scope_list(graph[cid]["fm"])
    if not declared_scope:
        # A CARD claiming a scope the frontmatter lacks is worse than an honestly unscoped node:
        # the CARD is what a human reads, while `scope_digest` and A17's path floor both match
        # against frontmatter. This gated e13 itself with freshness silently skipped.
        card_scope = [l for l in card_of(node_body(graph[cid])).splitlines()
                      if l.startswith("scope:") and l.partition(":")[2].strip()]
        if card_scope and _binds("phantom_scope", verdict):
            return refuse(f"the CARD claims a scope the frontmatter does not declare "
                          f"({card_scope[0].strip()}) — freshness and A17's path floor both read "
                          f"frontmatter, so both were silently skipped",
                          f"add scope: to {slug}'s frontmatter, then add run {slug} -- <cmd>")
        freshness = "freshness: n/a — the node declares no `scope:`"
    else:
        ok, why = fresh(receipt, root.parent)
        if not ok and _binds("stale_receipt", verdict):
            # In a non-git tree the diagnosis is right and `add run` provably cannot fix it —
            # re-running produces another digest-less receipt, so obeying the line loops. The
            # cause the message already names is the fix it never named.
            fix = BEAT_NEXT["build"].format(slug=slug)
            if "git working tree" in why:
                fix = f"git init   (then {fix})"
            return refuse(f"the receipt is stale — {why}", fix)
        freshness = f"freshness: {'fresh' if ok else 'STALE'} — {why}"

    # Refusal 3 (2026-08-28 review) — the declared scope, checked against what actually changed.
    #
    # A17's floor reads `scope:`, which the node declares about ITSELF, so omitting a path from
    # `scope:` defeated the one floor that does not rest on self-declared sensitivity: edit
    # `src/auth.py`, declare `src/ui.py`, gate at `process`. Deliberately narrow — only a
    # changed file matching `index.md`'s `sensitive_paths:` and covered by NO scope entry is
    # refused. An ordinary undeclared path stays the freshness check's business, because a
    # scope diff that refuses everything would be a scope diff everyone learns to widen past.
    if _binds("undeclared_sensitive", verdict):
        patterns = ((graph.get("/index.md", {}).get("fm") or {}).get("sensitive_paths")) or []
        undeclared = [rel for rel in _changed_paths(root.parent)
                      if any(_paths_touch(rel, str(pat)) for pat in patterns)
                      and not any(_paths_touch(rel, str(e)) or _paths_touch(str(e), rel)
                                  for e in declared_scope)]
        if undeclared:
            return refuse("the build changed a SENSITIVE path this node never declared: "
                          + " · ".join(sorted(undeclared)[:5])
                          + " — the security floor reads `scope:`, so an undeclared sensitive "
                          'edit gated at the wrong authority -> "R:UNDECLARED_SENSITIVE"',
                          f"add the path to {slug}'s `scope:` and re-run "
                          f"(add run {slug} -- <cmd>), or gate the change where it belongs")

    node = read(graph[cid]["path"], "T2")
    stubs = placeholders_in(node)
    if stubs and _binds("placeholders", verdict):
        return refuse("the node still carries template placeholders: " + " · ".join(stubs),
                      f"author {slug}'s RULES and CHECKS, then add gate {slug} PASS")

    # Constraint 3, structurally: what the freeze approved is what the build must have been held to.
    # A missing digest means a pre-seal engine froze this node — unverifiable, so not refusable.
    sealed = sealed_direction(sfm)

    # Refusal 1b (2026-08-28 review) — the ONE approval is not optional.
    #
    # Every post-freeze guard below was keyed off `sealed` with no else: drift detection, the
    # brief entry, R:UNBRIEFED. So a node that skipped `freeze` entirely did not fail those
    # checks — it SWITCHED THEM OFF, and gated PASS with less scrutiny than one that went
    # through the approval. The tolerance above is for a MISSING DIGEST (a pre-seal engine
    # froze it); a missing freeze STAMP is a different fact, and it is refusable. All depths:
    # quick is ceremony-tuned, not approval-exempt — the lane under time pressure is exactly
    # the one that must not be able to skip the human.
    if _binds("unsealed", verdict) and not any(
            isinstance(s, dict) and s.get("act") in ("freeze", "refreeze")
            for s in (sfm.get("verified") or [])):
        return refuse("this node was never frozen — the ONE human approval ADD asks for did "
                      "not happen, and every post-freeze guard (drift, brief entry) is keyed "
                      'off that seal -> "R:UNSEALED"',
                      f'add freeze {slug} --by "<name>", then add gate {slug} PASS')

    if sealed and _binds("drift", verdict) and direction_digest(node) != sealed:
        return refuse("RULES/CHECKS drifted after the freeze that approved them — a frozen contract "
                      "changes by refreezing, never by a silent edit",
                      f'add freeze {slug} --by "<name>" to record the change, or '
                      f'add reopen {slug} --to direction --reason "<why the contract moved>"')

    # The other half of the same seal. `direction:` never covered EDGES or probed `A<n>`, so the
    # cheapest way past `these rules have no reported passing check: A1, E1` was to delete the
    # obligation. Same integrity tier as `drift`: it protects the RECORD, so it binds every
    # verdict, and it is keyed off its own digest so pre-seal freezes stay gateable.
    sealed_b = sealed_binding(sfm)
    if sealed_b and _binds("drift", verdict) and binding_digest(node) != sealed_b:
        return refuse("the frozen obligations changed after the freeze that approved them — an "
                      "edge or a probed assumption was retired, and a contract sheds an "
                      "obligation by refreezing, never by a silent edit",
                      f'add freeze {slug} --by "<name>" to record the change, or '
                      f'add reopen {slug} --to direction --reason "<why the contract moved>"')

    # W1 (beta-2, R:UNBRIEFED) — the brief is Build's ENTRY, not the verdict's garnish.
    # beta-1 stamped a brief hash HERE, at gate time: a record of what the instructions would
    # have been, taken after the build was over. Using the brief during Build was recommended
    # prose, and three probe campaigns each showed what recommended prose becomes. Keyed off
    # the seal (like drift) so pre-seal bundles stay gateable; quick depth is ceremony-tuned
    # out, the same stance as the sweep's exemptions.
    if sealed and _binds("unbriefed", verdict) and sfm.get("type") == "Task" \
            and str(sfm.get("depth") or "standard") != "quick":
        all_stamps = sfm.get("verified") or []
        if not _brief_entered(all_stamps, receipt_cid):
            why = ("the brief was recorded after the receipt — an entry that postdates the "
                   "build entered nothing"
                   if _brief_entered(all_stamps) else
                   "no brief entered this build — the sealed direction was never compiled "
                   "into the working prompt since the last (re)freeze")
            return refuse(why + ' -> "R:UNBRIEFED"',
                          f"add brief {slug} to record the entry, then re-run "
                          f"(add run {slug} -- <cmd>) and add gate {slug} PASS")

    tier_notice = ""                               # refute-tier-floor: set only at a plan floor
    # The refute rung (evidence-over-tests) — a green nobody tried to break is REPORTED, not
    # earned. At a plan-or-higher floor the gate demands a refute stamp citing THIS receipt
    # (R:UNREFUTED) whose outcome is not `refuted` (R:REFUTED). Evidence-class, like `unbriefed`:
    # RISK-ACCEPTED is precisely for signing an unrefuted green knowingly. Quick depth, the
    # process floor and the explore lane are exempt — the rung is aimed at payments, not renames.
    if sealed and _binds("unrefuted", verdict) and _rung_bound(graph, cid, sfm):
        outcome, tier = _refute_of(sfm.get("verified") or [], receipt_cid)
        if outcome is None:
            return refuse("no refute cites this receipt — the green was never read against its "
                          'frozen intent, so it is reported, not earned -> "R:UNREFUTED"',
                          f'add refute {slug} --by "<name>" --tier T2 --held|--found "<input>" '
                          f"(a fresh session; probes derived from RULES/EDGES only), then add gate {slug} PASS")
        if outcome == "refuted":
            return refuse("the latest refute of this receipt found an input that breaks it "
                          '-> "R:REFUTED"',
                          f"fix the build (or refreeze with the edge it exposed), add run {slug} "
                          f"-- <cmd>, then add refute {slug} again")
        # refute-tier-floor: a green the BUILDER read is a prelude, never the rung's answer
        # (verify.md's ladder, which the gate had never read). At a human floor a T1 or tier-less
        # claim is refused; at plan the same state is a notice on the success line, promoted or
        # dropped on the count (R:NOTICEASREFUSAL). The claim is recorded as handed (R:TIERJUDGED),
        # and both earlier gaps — no read at all, a read that broke it — answer first (M4).
        # An ALLOWLIST, not a denylist — `REFUTE_TIERS` minus `T1`, derived from the frozen
        # constant rather than invented. A denylist sent every value it had not enumerated to the
        # permissive branch, so `tier: "T1 "` (one trailing space, inside quotes) rendered in the
        # engine's OWN `## EVIDENCE` view as `tier T1`, drew nothing from `doctor`, and recorded a
        # human-floor PASS: a ledger attesting `T1` beside a control that read the same field and
        # said yes. That is not an unverified claim recorded honestly, it is a well-formed stamp
        # attesting nothing. The sibling law twelve hundred lines up (`sensitivity_floor`,
        # R:SILENT_FLOOR) already says an unreadable declaration is one the engine cannot honour,
        # so it floors UP; a control reads the same way. M1's refuse-clause (T1 or no key) and its
        # pass-clause (T2 or T3) are both satisfied exactly; this only resolves the silence between
        # them, and it resolves it closed (security lens, gate-security-reviewer).
        if tier not in SIGNING_TIERS:
            claim = tier or "no tier"
            # The reason has to be TRUE of the value it read. `T1` is a prelude; `T4` or `t2` is a
            # claim the ladder cannot read at all, and telling that author they read their own
            # green would send them looking for a problem they do not have (A6: the reader is the
            # builder at 2am, and hard for them is a refusal that names the wrong thing).
            # The reason states what is true of the value READ, and the FLOOR is named once, by
            # the site that acts on it. A refusal that says "you read your own green" to someone
            # who typed `T4` sends them looking for a problem they do not have (A6), and
            # R:SILENT_FLOOR is floor-independent — the floor scopes the refusal, never the
            # unreadability. No second dash either: it reads as closing an appositive.
            why = ("a green read by its own builder is a prelude, never the rung's answer"
                   if tier in (None, "", "T1") else
                   "no tier the ladder recognises (T2 is a fresh session, T3 a human), and an "
                   "unreadable claim is one the engine cannot honour")
            if authority_for(graph, cid) == "human":
                return refuse(f"the latest refute of this receipt claims `{claim}` — {why}, and "
                              f'this floor is human -> "R:SELFREFUTE"',
                              f'add refute {slug} --by "<name>" --tier T2 --held|--found "<input>" '
                              f"(a FRESH session, briefed from the frozen node before it reads the "
                              f"diff), then add gate {slug} PASS")
            # M2 quotes this notice VERBATIM, so the T1/no-tier branch is the frozen literal and
            # nothing else: the refusal is free to say more because M1 never quotes it, but a Must
            # that states a string IS that string. The illegible branch carries the new clause
            # because M2 does not cover it — the contract is silent there, not contradicted.
            tier_notice = (f"\nnotice: the refute of this receipt claims `{claim}` — "
                           + ("a green read by its own builder" if tier in (None, "", "T1") else why)
                           + "; a human floor refuses this (R:SELFREFUTE)")

    # The floor rung (regression-floor) — a declared host suite that never ran, ran stale or ran
    # red is not evidence the change left the host standing. Evidence-class like the refute rung
    # and armed with it; the fix is the PLAN's own command, replayed, never guessed.
    if sealed and _binds("floor_unrun", verdict) and _rung_bound(graph, cid, sfm):
        floor = regression_floor(read(graph[cid]["path"], "T2"))
        if floor and floor["mode"] in ("full", "affected"):
            fr, fcid = latest_floor_receipt(root, cid)
            fix = f"add run {slug} --floor -- {floor['cmd']}, then add gate {slug} PASS"
            if fr is None:
                return refuse(f"`## PLAN` declares `regression: {floor['mode']}` and the floor was "
                              'never run -> "R:FLOORUNRUN"', fix)
            if str(fr.get("exit")) != "0":
                return refuse(f"the floor run {fcid} FAILED (exit {fr.get('exit')}) — the host did "
                              'not stand -> "R:FLOORUNRUN"', fix)
            ok, why = fresh(fr, root.parent)
            if not ok:
                return refuse(f"the floor receipt {fcid} is stale — {why} -> \"R:FLOORUNRUN\"", fix)

    # The stale-needs rung (consumers-go-stale, FORMAT §3.5) — a consumer verified against a
    # contract that has since moved is evidence about the old shape. Evidence-class, armed with
    # the refute rung; the provider is never touched by what its consumers pinned.
    if sealed and _binds("stale_needs", verdict) and _rung_bound(graph, cid, sfm):
        if (stale := stale_needs(graph, cid)):
            named = ", ".join(f"{t}#gives ({p} → {c})" for t, p, c in stale)
            return refuse(f"a `#gives` this task froze on has moved — {named} -> \"R:STALENEEDS\"",
                          f"read the new fragment, add freeze {slug}, add brief {slug}, rebuild, add run {slug} "
                          f"-- <cmd>, refute, then add gate {slug} PASS")

    # Refusal 2 (M2) — a Must proven by nothing is a label (A15). e12's M3, landing.
    reported = {i: "pass" for i in (receipt.get("passed") or [])}
    reported.update({i: "fail" for i in (receipt.get("failed") or [])})
    gaps = unbound(node, reported)
    if gaps and _binds("unbound_covers", verdict):
        # Two different situations wore the same refusal. When the receipt reported SOME ids, a
        # gap is a real gap and a signed waiver is the honest exit. When it reported NONE
        # (`ids: unknown` — the command emitted no JUnit report at all), every rule looks unbound
        # no matter how green the run was, and offering only RISK-ACCEPTED made a signed waiver
        # the sole exit from possibly-correct work -> "R:FALSEWAIVER". Name the re-run first.
        if str(receipt.get("ids")) == "unknown":
            return refuse(
                "the receipt carries no check ids at all, so every rule reads as unbound: "
                + ", ".join(gaps),
                f"re-run so the receipt binds — add run {slug} -- <test cmd> "
                f'--junitxml="${{TMPDIR:-/tmp}}/add-run.xml" — then add gate {slug} PASS   '
                f'(or add gate {slug} RISK-ACCEPTED --reason "<why the gap is acceptable>")')
        return refuse("these rules have no reported passing check: " + ", ".join(gaps),
                      f'add gate {slug} RISK-ACCEPTED --reason "<why the gap is acceptable>"')

    authority = authority_for(graph, cid)          # computed, never the caller's claim (M3)
    digest = brief(root, cid)["hash"]              # A16 — the instructions that drove the work
    stamp = (f'{{ by: "{_oneline(by)}", at: {_today()}, act: gate, authority: {authority}, '
             f'outcome: {verdict}, receipt: {receipt_cid}, brief: "{digest}"'
             + (f', reason: "{_oneline(reason)}"' if reason else "") + " }")
    _, t_err = _transition(root, cid, appends=[("verified", stamp)])
    if t_err:
        return None, t_err + "\nnext: add status"
    render_evidence(root, cid)

    if closes:
        done(root, cid)
        render_card(root, cid)
        tail = f"{cid} is done"
    else:
        tail = f"{verdict} recorded; {slug} stays in `{(graph[cid]['fm'] or {}).get('status')}`"
    note = (f"gate {verdict} recorded at authority `{authority}`"
            + tier_notice
            + f"\n  {freshness}"
            + (f"\n  unbound (reported, not blocking): {', '.join(gaps)}" if gaps else "")
            + f"\n  brief {digest} · receipt {receipt_cid}\n{tail}\nnext: add status")
    return True, note


# ================================= checks — the CHECKS section, compiled (e14)
#
# F2 measured this project's own version of the defect: 61 cited test names that were never
# written, across nine gated M0 tasks. Nobody noticed because a plausible test name reads
# exactly like a real one at review speed.
#
# More care at authoring time does not fix it. e13 opened with 12 authored checks and its suite
# finished at 25 — every addition was discovered DURING the build, so the knowledge did not exist
# when the section was written. Extraction is the only fix (L7: compiled beats authored).
#
# Two carriers, because this repo already contains two: a docstring `covers:` (118 tests) and a
# `# --- name · covers: … ---` header above the function (e15's subagent, 5 tests). One author was
# enough for the convention to diverge, so the reader accepts both.

COVERS_IN_TEST = re.compile(r"covers:\s*([^—\n·]+)(?:[—·]\s*(.*))?", re.DOTALL)
HEADER_COVERS = re.compile(r"^#.*?\b(test_\w+)\s*·\s*covers:\s*([^-\n]+?)\s*-*$", re.MULTILINE)


def checks_of(paths) -> dict:
    """`{test_id: (rule_ids, description)}` for every test in `paths`.

    Which names are functions is the PARSER's answer, not a regex's. A regex over source text
    reads `def test_…` out of quoted strings: this verb compiled its own task's node and listed
    three tests that exist only inside fixture string constants. Same defect class as the
    unanchored validator regex e15 fixed, found the same way — by reading the output.

    An unlabelled test maps to `([], doc)` and is REPORTED as unlabelled, never given a rule
    inferred from its name (R:GUESS): `test_m1_something` proves whatever its body proves, which
    may be nothing to do with M1.
    """
    found = {}
    for path in paths:
        try:
            tree = ast.parse(src := Path(path).read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        real = {n.name: (ast.get_docstring(n) or "") for n in ast.walk(tree)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n.name.startswith("test_")}
        # A header citation is honoured only for a name the parser confirms, so a comment inside a
        # string literal cannot smuggle one in either.
        from_header = {m.group(1): m.group(2) for m in HEADER_COVERS.finditer(src)
                       if m.group(1) in real}
        for name, doc in real.items():
            raw, desc = None, ""
            match = COVERS_IN_TEST.search(doc)
            if match:
                raw, desc = match.group(1), match.group(2) or ""
            elif name in from_header:
                raw, desc = from_header[name], doc
            # Every referent is validated against FORMAT §6.1's grammar. A docstring reading
            # "No covers: anywhere" otherwise yields rules named `anywhere. A gap` — found by a
            # fixture that said exactly that, by accident. Prose mentioning the word is not a
            # citation, and the grammar is what tells the two apart.
            rules = [r.strip() for r in (raw or "").split(",") if REFERENT.match(r.strip())]
            # Keyed by `qualify(path, name)` for the same reason `extract_ids` is (M3): the bare
            # key silently lost one of this repo's own two `test_sync_is_idempotent`, so the
            # compiler graded 211 tests against a suite of 212. Consumers that show a citation to
            # a human render the tail — a citation names a TEST, and `covers: test_foo` stays
            # legible (M5).
            found[qualify(path, name)] = (rules, _summarise(desc))
    return found


def cite_hits(cite: str, known) -> list:
    """Every qualified ID a bare citation could mean. 0 = absent, 1 = resolved, >1 = ambiguous."""
    return [k for k in known if k == cite or k.rpartition("::")[2] == cite]


def _summarise(text: str, width: int = 110) -> str:
    """One line, cut at a word and marked as cut. A CHECKS description is a summary of a test,
    never the test — but a cut that does not say so reads as a typo, not as an omission."""
    flat = " ".join(text.split()).strip(' ."')
    if len(flat) <= width:
        return flat
    head = flat[:width].rsplit(" ", 1)[0]
    return f"{head.rstrip(' ,;.')}…"


def unlabelled(paths) -> list:
    """Tests carrying no `covers:` — a visible gap (M3).

    Rendered as bare names for the same reason `_checks_lines` is (M5): this list is read by a
    human and written into a node, and `module::name` there would be the citation sweep e16
    exists to avoid.
    """
    return sorted(name.rpartition("::")[2] for name, (rules, _) in checks_of(paths).items() if not rules)


def _checks_lines(node: dict, paths) -> tuple:
    """`(lines, gaps)` — the compiled CHECKS body for one node, and its unlabelled tests.

    The citation is compiled because a human cannot be trusted to keep it in step with the suite.
    The DESCRIPTION is the opposite: knowledge only the author has. Restating the citation as
    `· proves M1` compiles a line that says nothing twice, so the author's sentence is carried
    through and only its absence is filled in.
    """
    rules, extracted = rules_of(node), checks_of(paths)
    relevant = {t: v for t, v in extracted.items() if any(r in rules for r in v[0])}
    # The TAIL is written, not the qualified id: a citation names a test, and `covers: test_foo`
    # must stay legible to the human reading the node (M5). The qualified form is the reader's
    # business — `resolve_check` — never the written claim's.
    lines = [f"- {t.rpartition('::')[2]} · covers: {', '.join(rs)} · {desc or 'no description in the test'}"
             for t, (rs, desc) in sorted(relevant.items())]
    return lines, sorted(t.rpartition("::")[2] for t, (rs, _) in extracted.items() if not rs)


def checks_verify(root, cid: str, paths, extracted: dict = None) -> list:
    """F2 in BOTH directions, graded. `[{severity, message, rule, test}]` (M2).

    `extracted` is `checks_of(paths)` computed once by a caller checking many nodes. Without it,
    `doctor` re-parsed the whole suite per node — 1,650 ms against 37 ms on this bundle, on the
    verb meant to run in CI. The parameter exists so the cost is paid once, not 59 times.

    Two findings that look identical mean different things, and grading them the same makes the
    report useless:

    * a cited test that does not exist on a node **still in `direction`** is `pending` — the task
      has not been built, and its CHECKS are a plan. Thirteen live nodes reported at first run and
      four were exactly this;
    * the same gap on a node carrying a **gate stamp** is an `error`: a claim was accepted against
      evidence that was not there. That is F2.

    A referent naming no declared rule is always an `error`. Unlike a missing test it cannot come
    true later — it is a claim about the node's own contents, and the node is right there.
    """
    node = scan(Path(root)).get(cid)
    if node is None:
        return []
    full = read(node["path"], "T2")
    stamps = [s for s in ((node["fm"] or {}).get("verified") or []) if isinstance(s, dict)]
    gated = any(s.get("act") == "gate" for s in stamps)
    known, rules = set(extracted if extracted is not None else checks_of(paths)), set(referents_of(full))
    findings = []
    for rule, cited in sorted(covers(full).items()):
        if rule not in rules:
            findings.append({"severity": "error", "rule": rule, "test": None,
                             "message": f"{cid}: `covers: {rule}` names no rule this node declares"})
        for test in cited:
            # A citation is resolved through the ID grammar, not by set membership: `known` is
            # keyed `module::name` (M3) while the citation is bare (M5), so a literal `not in`
            # would report all 394 of this bundle's citations as missing.
            hits = cite_hits(test, known)
            if not hits:
                findings.append({
                    "severity": "error" if gated else "pending", "rule": rule, "test": test,
                    "message": f"{cid}: `{test}` exists in no suite"
                               + ("" if gated else " (node is not gated — its checks are a plan)")})
            elif len(hits) > 1:
                findings.append({
                    "severity": "error" if gated else "pending", "rule": rule, "test": test,
                    "message": f"{cid}: `{test}` names {len(hits)} tests "
                               f"({', '.join(sorted(hits))}) — ambiguous, so it proves nothing"})
    return findings


# ================================= doctor — conformance and repair over the graph (e8)
#
# `doctor` is a REPORTER assembled from oracles that already exist — the graph, `cycles`,
# `card_drift`, `orphans`, `checks_verify` — plus the frontmatter and body rules the M0 validator
# enforces that no verb yet reads. Almost none of this is new logic, and A1 pre-booked the 150-line
# saving on exactly that: it runs over e2's compiled graph and never builds a second scan.
#
# M2 is asymmetric parity, decided before BUILD and recorded on the node. On the validator's own
# seven codes the two must agree finding-for-finding; beyond them `doctor` may report more, because
# it reads STAMPS and the validator cannot. R:DIVERGE means "no CONFORMANCE finding the M0 oracle
# would not also produce", not "no finding at all".

ABF_TYPES = ("Project", "Milestone", "Task", "Spec", "Persona", "Prompt", "Run",
             # `Interview` joins the census because the engine WRITES one: the `.d/interviews/`
             # sidecar is a first-class record of the ONE approval's questions and answers,
             # exactly as `Run` is for a command. A type the engine emits and the type census
             # does not know is a finding the engine files against itself.
             "Interview")
NOT_A_NODE = ("index.md", "log.md")   # the validator's RESERVED — compiled bodies, A11/A20
MD_LINK = re.compile(r"\]\(([^)\s]+\.md)\)")
COMPILED_MARKER = "COMPILED BODY"


def _heading_slugs(body: str) -> set:
    return {re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", line.lstrip("#").strip().lower())).strip("-")
            for line in body.splitlines() if line.startswith("#")}


def doctor(root, graph: dict = None, paths=None) -> list:
    """Every conformance finding for a bundle. `[{severity, code, detail, node}]`. Reports only.

    Law 3 as a signature: nothing here writes. A conformance checker that silently repairs is one
    whose report cannot be trusted, because the reader cannot tell what it found from what it
    changed — `doctor_sync` is the separate, asked-for verb.

    `graph` may be supplied by a caller that already has one (R:SECONDSCAN: doctor never scans
    twice). `paths` is the test suite for M6's F2 check; omitted, that check is skipped rather
    than guessed at.
    """
    root = Path(root)
    strays = []
    graph = scan(root, strays=strays) if graph is None else graph
    out = []

    def find(severity, code, detail, node=None):
        out.append({"severity": severity, "code": code, "detail": detail, "node": node})

    # Three loops below each want a node's T2 body, and before this memo each re-read it:
    # fragment resolution re-read a target once per INCOMING fragment edge, the markdown-link
    # loop read every node again, and the placeholder loop read every lifecycle node a third
    # time. Measured on a 196-node graph: 386 reads and 594 parses, against `status`'s 208 for
    # the same graph. The parser is already hand-optimised; the cost was doing it three times.
    #
    # Scoped to ONE call, deliberately (R:STALEDOC). A module-level cache would let a later
    # `doctor` report a finding computed from a body that has since been repaired — and
    # `doctor --sync` would then act on it. Lazy, never a prefetch (R:PREFETCH): a bundle whose
    # edges carry no fragments reads no target bodies for that loop at all. Bounded by the
    # bundle the verb is already walking: 534KB over 207 nodes here, largest body 21KB.
    _bodies = {}

    def node_of(path) -> dict:
        key = str(path)
        if key not in _bodies:                 # `not in`, never `.get() or` — an empty body
            _bodies[key] = read(path, "T2")    # is a cached value, not a cache miss (A4)
        return _bodies[key]

    def body_of(path) -> str:
        # The memo holds the whole READ, not the body alone: `unreadable_spec` asks about the
        # frontmatter too, and a second reader of the same file would be a second scan (E44).
        return node_of(path)["body"]

    for rel in strays:
        if rel not in NOT_A_NODE:
            find("error", "missing_frontmatter", rel)

    for cid, node in sorted(graph.items()):
        rel, fm = cid.lstrip("/"), node["fm"] or {}
        node_type = fm.get("type")
        if not node_type or not isinstance(node_type, str):
            if rel not in NOT_A_NODE:
                find("error", "type_empty", rel, cid)
        elif node_type not in ABF_TYPES:
            find("info", "unknown_type", f"{rel}: {node_type}", cid)

    # OKF conformance (M8) — the READER that earns the `okf_version` stamp its place.
    #
    # The stamp was removed on 2026-08-08 (baa066ae) because "nothing in the engine, the
    # validator, or the skill ever READS it", and that was true. Re-landing it for the
    # `okf-graph-time` milestone without this would have reversed that decision rather than
    # answered it. The rule the old guard defended — no key that nothing reads — is kept; this
    # is what makes its premise about THIS key false.
    #
    # `info`, never `error`: a bundle declaring no OKF version is a pre-OKF bundle, not a broken
    # one (law 3), so the finding is reported only when there is a declaration to report on. A
    # finding that fired either way would be a reader in name only.
    okf_declared = (graph.get("/index.md", {}).get("fm") or {}).get("okf_version")
    if okf_declared:
        specs = [n for n in graph.values() if (n["fm"] or {}).get("type") == "Spec"]
        described = [n for n in specs if (n["fm"] or {}).get("description")]
        find("info", "okf_conformance",
             f"declared OKF v{okf_declared} — {len(described)}/{len(specs)} Spec nodes carry "
             f"`description:`", "/index.md")

    # consumers-go-stale (FORMAT §3.5): a consumer that froze on a `#gives` whose digest has since
    # moved. `warn`, one per (consumer, provider), sorted by consumer so two runs are byte-identical;
    # a stamp with no pin (pre-3.7) reports nothing.
    for cid, node in sorted(graph.items()):
        if (node.get("fm") or {}).get("type") != "Task":
            continue
        for provider, pinned, current in stale_needs(graph, cid):
            find("warn", "needs_stale",
                 f"{cid} froze on {provider}#gives {pinned}, now {current} — re-read the fragment, "
                 f"then add freeze {cid.rsplit('/', 1)[-1][:-3]}", cid)

    def _target_findings(src, ref, target):
        """Containment first, then §3.3 — the ONE target reader both edge families share.

        Ordered so the fatal decision is made from the ref string and the root path ALONE, before
        anything opens the target. That ordering is what keeps §9 true: every body read below can
        only ever produce `info`, so all three error codes stay decidable from frontmatter.
        """
        rel = src.lstrip("/")
        # Containment is decided on the RAW ref against the real filesystem, NEVER through
        # `_norm`. `_norm` builds a graph CID, and it builds it with `os.path.normpath` on a
        # string that already starts with `/` — where `..` CLAMPS at the root instead of
        # ascending. So a relative escape `../../outside.md` from `/specs/method.md` normalises
        # to `/outside.md`, which is INSIDE the bundle, and `edge_out_of_bundle` — one of the
        # three fatal codes — silently degraded to `edge_unresolved` (info). The M0 oracle never
        # had the bug because it joins against the source file's directory and resolves; this is
        # that computation, so the two agree by construction rather than by coincidence
        # (R:SILENTESCAPE, R:DIVERGE). Found by an adversarial sweep, not by the suite:
        # the absolute form `/specs/../../outside.md` was fatal all along and hid the relative one.
        bare = ref.partition("#")[0].strip()
        resolved = ((root / bare.lstrip("/")) if bare.startswith("/")
                    else (root / src.lstrip("/")).parent.joinpath(bare)).resolve()
        if not resolved.is_relative_to(root.resolve()):
            find("error", "edge_out_of_bundle", f"{rel} -> {ref}", src)
        elif target is None:
            find("info", "edge_unresolved", f"{rel} -> {ref}", src)
        elif (fragment := ref.partition("#")[2]):
            body = body_of(graph[target]["path"])
            if fragment not in (graph[target]["fm"] or {}) \
                    and fragment not in _heading_slugs(body) \
                    and fragment not in _delta_ids(body):
                find("info", "edge_unresolved", f"{rel} -> {ref}", src)

    for src, key, ref, target in edges(graph):
        _target_findings(src, ref, target)

    # The SECOND edge family (§3.2). Its target end goes through the SAME reader above — that is
    # the point: a relation escaping the bundle must report the identical code at the identical
    # severity as a `depends_on:` naming the identical target, and two readers would drift.
    for src, src_id, verb, ref, target in relations(graph):
        rel = src.lstrip("/")
        if verb is None:
            find("info", "relation_malformed", f"{rel} -> {ref}", src)
            continue          # no third field, so no target, so no containment CLAIM either
        if verb not in RELATION_VOCAB:
            # Recorded, never rejected (law 3) — and deliberately NOT a `continue`: an unknown
            # verb must not suppress its own target's containment test, or the only fatal code
            # this family can raise becomes unreachable behind an info finding.
            find("info", "unknown_rel", f"{rel} -> {verb} ({ref})", src)
        if src_id not in _delta_ids(body_of(graph[src]["path"])):
            find("info", "edge_unresolved", f"{rel} -> {src_id}", src)
        _target_findings(src, ref, target)

    for cid, node in sorted(graph.items()):
        for link in MD_LINK.findall(body_of(node["path"])):
            if not link.startswith(("http://", "https://")) \
                    and not (root / cid.lstrip("/")).parent.joinpath(link).exists():
                find("info", "broken_md_link", f"{cid.lstrip('/')} -> {link}", cid)

    declared = (root / ".gitattributes").read_text(encoding="utf-8") \
        if (root / ".gitattributes").is_file() else ""
    for name in NOT_A_NODE:
        path = root / name
        if not path.is_file() or not split(path.read_text(encoding="utf-8"))[1].strip():
            continue  # nothing rendered yet, so nothing a human can lose
        missing = ([f"no `{COMPILED_MARKER}` marker"] if COMPILED_MARKER not in path.read_text() else []) \
            + ([] if any(l.split()[:1] == [name] for l in declared.splitlines()) else ["no .gitattributes entry"])
        if missing:
            find("info", "compiled_undeclared", f"{name}: {', '.join(missing)}")

    # -- beyond the M0 oracle: findings only a reader of STAMPS can make --
    for loop in cycles(graph):
        find("error", "dependency_cycle", " -> ".join(loop), loop[0])
    for cid, key, said, actual in card_drift(graph, body_of=body_of):
        find("info", "card_drift", f"{cid.lstrip('/')}: CARD `{key}` says {said}, status is {actual}", cid)
    # Coverage: a sensitive task with no recorded lens. R:NOLENS floors PARALLEL streams only, so a
    # SEQUENTIAL architecture/security/data task can carry no lens and go unseen. Surface it — info,
    # reports-only, never a gate (that HARD-STOP question is A2, out of scope here).
    # `placeholders_in` is a correct, trusted oracle wired to exactly ONE caller: the gate. So a
    # node standing in its scaffold only ever surfaced at the END of the loop, to someone who had
    # already done the work — never to the newcomer who runs `doctor` to ask whether the bundle is
    # in good shape, and got "no findings" over a bundle nobody had authored -> "R:GREENBUNDLE".
    #
    # `warn`, not `error`: a fresh scaffold is unwritten, not broken, and an error would make
    # `init` produce a red bundle. LIFECYCLE_TYPES only — a Persona has no RULES to author, so a
    # finding against one names nothing its author could clear.
    # The slot's other half: a line the reader SKIPPED is named here, or the slot fails silently
    # and the author never learns the monitor they wrote is not one. `info` — a malformed observe
    # breaks nothing; no gate reads an observe at all (R:OBSERVEASGATE).
    for cid, node in sorted(graph.items()):
        if (node["fm"] or {}).get("type") != "Task":
            continue
        for oid, line in malformed_observes({"body": body_of(node["path"])}):
            find("info", "observe_malformed",
                 f"{cid.lstrip('/')}: {oid} is not an observe — the form is `- O<n> covers: <M ids> "
                 f"· signal <t> · window <t> · threshold <t> · action alert|rollback`: {line[:60]}", cid)
    for cid, node in sorted(graph.items()):
        if (node["fm"] or {}).get("type") not in LIFECYCLE_TYPES:
            continue
        # `scan()` nodes carry frontmatter and no body, and `placeholders_in` reads the body —
        # called on a scan node it returns [] for every node, which is a guard that never fires.
        standing = placeholders_in({**node, "body": body_of(node["path"])})
        if standing:
            find("warn", "unauthored_node",
                 f"{cid.lstrip('/')}: still scaffold — {' · '.join(standing[:3])}", cid)

    # R:GREENROOT. `placeholders_in` is wired to LIFECYCLE_TYPES — exactly the two types whose
    # author already meets a refusal at `freeze`. The bundle ROOT and the five lenses are the
    # files the method tells every agent to read FIRST, and no guard reached either of them:
    # this repo's own PROJECT.md read `state: initialised` for a month after `upgrade` dropped
    # its goal, and all five specs still hold the scaffold line that every `brief` faithfully
    # reports to the worker as `unauthored`. A guard that fires on a malformed thing and never
    # on a missing one is a guard you get past by deleting (M22) — here, by never writing.
    for cid, node in sorted(graph.items()):
        fm = node["fm"] or {}
        if fm.get("type") not in ("Project", "Spec"):
            continue
        body, slots = body_of(node["path"]), []
        if fm.get("type") == "Project":
            if PLACEHOLDER.search(str(fm.get("goal") or "")):
                slots.append("frontmatter `goal:`")
            for line in card_of(body).splitlines():
                key, sep, value = line.partition(":")
                if sep and key.strip() == "goal" and PLACEHOLDER.search(value):
                    slots.append("CARD `goal:`")
            if "invariants" not in fm:
                slots.append("`invariants:` absent")
        else:
            for heading in ("Now", "Decisions that bind"):
                if _placeholder_only(_section_of(body, heading)):
                    slots.append(f"`## {heading}`")
        if slots:
            find("warn", "unauthored_root",
                 f"{cid.lstrip('/')}: still scaffold — {' · '.join(slots[:3])}", cid)

    # Every R:UNREADABLE refusal says "add doctor names it", and doctor named the COUNTER instead
    # — a way out the engine points at and does not provide (thirtieth T2 refute, E44). Read from
    # the DIRECTORY, not the graph: a spec whose frontmatter no reader can find is not in the
    # graph as a Spec at all, which is exactly the state that needs naming.
    blind_specs = {}
    for sp in sorted((root / "specs").glob("*.md")):
        if (blind := unreadable_spec(node_of(sp))):
            blind_specs[sp.resolve()] = blind
            find("warn", "unreadable_spec",
                 f"specs/{sp.stem}: no writer can land a line here — {blind}", f"/specs/{sp.name}")

    # The counter is engine-maintained (A1), so a disagreement with the body is a repairable
    # fact, never a human's mistake: `info`, and `--sync` fixes it. An ABSENT key over an EMPTY
    # body is not drift — it is a bundle that has simply never learned anything (E1). A spec no
    # reader can see is skipped: the drift there is a CONSEQUENCE, and reporting it invited the
    # repair that erased an escape `fold` had refused (E44).
    for cid, node in sorted(graph.items()):
        if (node["fm"] or {}).get("type") != "Spec":
            continue
        if Path(node["path"]).resolve() in blind_specs:
            continue     # its counter cannot be honestly counted; the CAUSE is already reported
        actual = open_delta_count(body_of(node["path"]))
        declared = declared_open_deltas(node["fm"])
        if declared == actual or (declared is None and actual == 0):
            continue
        said = (node["fm"] or {}).get("open_deltas", "nothing")
        find("info", "delta_count_drift",
             f"{cid.lstrip('/')}: `open_deltas:` says {said}, the body holds {actual}", cid)

    for cid, node in sorted(graph.items()):
        fm = node["fm"] or {}
        if fm.get("type") != "Task" or SENSITIVITY_FLOOR.get(fm.get("sensitivity"), "process") == "process":
            continue
        # M1: only a node that can still TAKE a lens. On a closed, gated node the advice this
        # finding carries is unreachable, and 23 of 25 findings on this repo's own bundle were
        # exactly that — a wall of unactionable lines the two real ones sat inside of. A report
        # is read as a worklist whether or not it was written as one.
        # `done` is the ONLY exclusion (A2): a node in `verify` is still advisable before its
        # gate. An ABSENT status is NOT closed (A4, R:BLINDCLOSE) — hiding a finding on a
        # malformed node is the failure this rule is meant to prevent, not an instance of it.
        if fm.get("status") == "done":
            continue
        if not fm.get("persona") and not fm.get("advised_by"):
            # Severity agrees with the gate floor (A2): security is a HARD gate refusal (R:NOCOVERAGE),
            # so doctor says `warn`; the softer data/architecture floors stay `info` nudges.
            severity = "warn" if fm.get("sensitivity") == "security" else "info"
            find(severity, "unadvised_sensitive", f"{cid.lstrip('/')}: {fm.get('sensitivity')}, no lens", cid)
    # W4 (beta-2): the routing index is how a lens is FOUND — the corpus says what each
    # persona is, the index says when to reach for it. A bundle whose corpus moved without
    # its index routes against a roster that no longer exists, silently. "Persona" here is
    # the generator's own definition (a corpus file carrying `description:`), so README/
    # VENDOR/LICENSE never count. Reports only, like everything else in this function.
    teacher = root / "personas-teacher"
    if teacher.is_dir():
        corpus = 0
        for p in teacher.rglob("*.md"):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            fm_text = text.split("---", 2)[1] if text.startswith("---") else ""
            if re.search(r"^description:\s*\S", fm_text, re.M):
                corpus += 1
        index_file = root / "personas-index" / "use-when.md"
        if not index_file.is_file():
            find("warn", "routing_index_missing",
                 f"personas-teacher/ holds {corpus} personas and personas-index/use-when.md "
                 f"is absent — the corpus can be read but never routed to "
                 f"(scripts/build_persona_index.py, then doctor --sync)")
        else:
            entries = sum(1 for l in index_file.read_text(encoding="utf-8").splitlines()
                          if l.startswith("- `"))
            if entries != corpus:
                find("warn", "routing_index_stale",
                     f"personas-index/use-when.md routes {entries} personas; "
                     f"personas-teacher/ holds {corpus} — the corpus moved without the index "
                     f"(scripts/build_persona_index.py, then doctor --sync)")
    # A term outside its closed vocabulary cannot contribute to fit; another valid term may
    # still fit. Info severity: `doctor` reports, never gates (M4). Sorted for stable reports.
    routing = []
    for cid in sorted(graph):
        fm = graph[cid]["fm"] or {}
        if fm.get("type") != "Persona":
            continue                     # the keys are meaningless elsewhere (A1)
        slug = cid.rsplit("/", 1)[-1][:-3]
        for key, allowed in (("flow", PERSONA_FLOWS), ("task-kinds", PERSONA_TASK_KINDS)):
            raw = fm.get(key)
            if not raw:
                continue                 # declaring neither key is legitimate (A2)
            if PLACEHOLDER.search(str(raw)):
                continue                 # an UNTOUCHED scaffold slot: nobody authored a value
                                         # yet, and a guard must never fire on a missing thing.
                                         # (Per-token `<`-prefix checking missed this: splitting
                                         # `<from the closed taxonomy, comma-separated>` on commas
                                         # leaves interior words carrying no bracket at all.)
            values = _lens_terms(raw)  # same scalar/list normalizer as the candidate selector
            bad = [v for v in values if v not in allowed]
            if bad:
                routing.append(
                    f"{slug}: `{key}: {', '.join(bad)}` is outside the closed taxonomy — that term "
                    f"cannot contribute to fit. Allowed: {' · '.join(allowed)}")
    for message in sorted(routing):
        find("info", "persona_routing_key", message)
    for cid, section in evidence_scaffold(root, graph=graph, body_of=body_of):
        find("info", "evidence_scaffold",
             f"{cid.lstrip('/')}: done, but `## {section}` still carries the scaffold — the view "
             f"is written by the verbs since 3.7; `add doctor --sync` backfills it from the record", cid)
    for receipt in orphans(root, graph=graph):
        find("error", "orphan_receipt", receipt, receipt)
    if (tdrift := tooling_drift(root, graph)):
        find("warn", "tooling_drift", tdrift)
    if paths:
        extracted = checks_of(paths)   # once, not once per node — see checks_verify's docstring
        for f in (c for cid in graph for c in checks_verify(root, cid, paths, extracted)):
            if f["severity"] == "error":   # `pending` is a plan, not a defect (e14's grading)
                find("error", "checks_citation", f["message"])
    return out


INDEX_SECTIONS = (("Project", "Project"), ("Specs", "Spec"),
                  ("Milestones", "Milestone"), ("Tasks", "Task"), ("Personas", "Persona"))
INDEX_ENTRY = re.compile(r"^- \[[^\]]*\]\(([^)]+)\)(?:\s+—\s*(.*))?$")


def _render_index(root, graph: dict) -> str:
    """Rebuild `index.md`'s TOC from the nodes, PRESERVING each entry's authored description.

    A11 calls this body compiled, and it mostly is — the link, the title and the status tokens are
    all derivable. But the sentence after them is not: "ten verbs, ≤2,400 lines, dogfooded here"
    was written by a human and exists nowhere else in the bundle. Regenerating the whole body would
    be A23 resolution that silently eats authored prose, which is R:SYNCAUTHORED wearing a helpful
    face. So the mechanical tokens are recomputed and the tail is carried across, keyed by path.
    Frontmatter is never touched: `sensitive_paths` is the A17 floor and no tool may rewrite it.
    """
    path = root / "index.md"
    raw, body = split(path.read_text(encoding="utf-8"))
    kept = {m.group(1): (m.group(2) or "") for line in body.splitlines()
            if (m := INDEX_ENTRY.match(line.strip()))}
    marker = next((l for l in body.splitlines() if COMPILED_MARKER in l),
                  f"<!-- COMPILED BODY (A11) — regenerated by the engine; do not hand-maintain. -->")
    out = [marker, ""]
    for heading, node_type in INDEX_SECTIONS:
        rows = []
        for cid, node in sorted(graph.items()):
            fm = node["fm"] or {}
            if fm.get("type") != node_type:
                continue
            rel = cid.lstrip("/")
            tail = kept.get(rel, "")
            if node_type == "Task":
                # fully mechanical, and it MUST recompute: a preserved `direction` on a gated task
                # is the index lying about the graph, which is the only thing an index is for.
                bits = [f"`{fm.get(k)}`" for k in ("status", "depth", "sensitivity") if fm.get(k)]
                detail = " · ".join(bits)
            elif node_type == "Milestone":
                authored = tail.split("—", 1)[1].strip() if "—" in tail else ""
                detail = f"`{fm.get('status', '?')}`" + (f" — {authored}" if authored else "")
            elif node_type == "Spec":
                # Same STRUCTURAL rule as the Persona row below — frontmatter beats the
                # preserved tail, so the catalogue can never disagree with the node — though
                # not the same key. The fallback is not decoration: a bundle written before
                # `description:` existed keeps the sentence a human authored into the index
                # here, and losing it would be R:SYNCAUTHORED wearing a helpful face
                # (R:TAILEATEN). A Spec with neither renders a bare row, never a dangling `—`.
                detail = str(fm.get("description", "") or "") or tail
            elif node_type == "Persona":
                # A persona's catalogue line is its `use-when:` FRONTMATTER (machine-read), not the
                # preserved index tail — the roster must reflect the node, never a stale hand edit.
                detail = str(fm.get("use-when", "") or "")
            else:
                detail = tail
            rows.append(f"- [{fm.get('title', rel)}]({rel})" + (f" — {detail}" if detail else ""))
        if rows:
            out += [f"## {heading}", ""] + rows + [""]
    return f"---\n{raw}\n---\n\n" + "\n".join(out).rstrip("\n") + "\n"


def doctor_sync(root) -> tuple:
    """Recompute every COMPILED artifact from the nodes. `(changed, note)`.

    A23 merge resolution: a conflicted `index.md` or `log.md` is resolved by recomputation rather
    than by hand. Sound only because L1 makes them views — the same edit to a node body is data
    loss. So this writes exactly what FORMAT declares compiled and nothing else (R:SYNCAUTHORED),
    and it never manufactures history: an orphaned receipt is REPORTED forever, never given the
    stamp it lacks, because a stamp invented now claims a binding that did not happen
    (R:REPAIRAWAY).
    """
    root = Path(root)
    graph, changed = load(root), []
    for cid, key, _said, _actual in card_drift(graph):
        ok, _ = render_card(root, cid)
        if ok:
            changed.append(f"{cid.lstrip('/')} CARD `{key}`")
    # A DERIVED count, so recomputing it is exactly what this verb is for — and never
    # R:SYNCAUTHORED: no authored byte moves, only a number whose oracle is the body beneath it.
    skipped_specs = []
    for path in sorted((root / "specs").glob("*.md")):
        n = read(path, "T2")
        # The counter's oracle is the body, and a body no reader can see is no oracle: recomputing
        # from it wrote `open_deltas: 0` over a spec still holding an escape `fold` had refused —
        # this verb is where the refusals send the author, so it is the one that must not launder
        # the leak (thirtieth T2 refute, E44). Reported, never repaired, and never a traceback.
        if (blind := unreadable_spec(n)):
            skipped_specs.append(f"specs/{path.stem} ({blind})")
            continue
        actual = open_delta_count(n["body"])
        declared = declared_open_deltas(n["fm"])
        if declared == actual or (declared is None and actual == 0):
            continue
        write(path, f"---\n{set_key(n['raw'], 'open_deltas', str(actual))}\n---\n{n['body']}")
        changed.append(f"specs/{path.stem} `open_deltas` -> {actual}")
    # The EVIDENCE and LESSONS views, recomputed from the record (R:MANUFACTURED holds inside
    # the renderers: nothing the stamps and specs do not say is written). Every Task with a
    # record gets its EVIDENCE; the LESSONS harvest is a close-time view, so `done` only.
    for cid, node in sorted(graph.items()):
        fm = node.get("fm") or {}
        if fm.get("type") != "Task":
            continue
        if render_evidence(root, cid, graph=graph):
            changed.append(f"{cid.lstrip('/')} EVIDENCE")
        if str(fm.get("status")) == "done" and harvest_lessons(root, cid):
            changed.append(f"{cid.lstrip('/')} LESSONS")
    if (index := root / "index.md").is_file():
        rebuilt = _render_index(root, graph)
        if rebuilt and rebuilt != index.read_text(encoding="utf-8"):
            write(index, rebuilt)
            changed.append("index.md")
    # A stale vendored engine is a compiled artifact too: refresh it from the running engine and
    # re-stamp the version of record, so `tooling_drift` clears. This is the fix the warning points at.
    if tooling_drift(root, graph):
        _vendor_tooling(root, overwrite=True)
        idx = root / "index.md"
        if idx.is_file():
            n = read(idx, "T2")
            write(idx, f"---\n{set_key(n['raw'], 'tooling_engine', ENGINE)}\n---\n{n['body']}")
        changed.append("tooling engine (re-vendored)")
    # A spec no writer can land in is SAID, never silently stepped over: this verb is where every
    # R:UNREADABLE refusal sends the author, so it must say what it did not repair and why (E44).
    left = ("\n  not repaired (no reader can see the body): " + " · ".join(skipped_specs)
            if skipped_specs else "")
    if not changed:
        return None, ("every compiled artifact already matches the nodes" + left +
                       "\nnext: add doctor  (to see what is reported but not repairable)")
    return True, ("recomputed " + " · ".join(changed) + left +
                  "\nnext: add doctor  (orphaned receipts and gated claims are never repaired)")
