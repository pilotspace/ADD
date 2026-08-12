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
ACTIVE_STATES = ("direction", "build", "verify")
CACHE_NAME = "graph.json"


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
        node = read(path, "T0")
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


def edges(graph: dict) -> list:
    """`[(src_cid, key, ref, target_cid|None)]` — typed, and only from EDGE_KEYS."""
    out = []
    for cid, node in graph.items():
        for key in EDGE_KEYS:
            value = (node["fm"] or {}).get(key)
            if value is None:
                continue
            for ref in value if isinstance(value, list) else [value]:
                ref = str(ref).strip()
                if ".md" not in ref:
                    continue
                target = _norm(cid, ref)
                out.append((cid, key, ref, target if target in graph else None))
    return out


def _section(body: str, slug: str) -> str:
    """The body section under the heading whose kebab-cased text is `slug`."""
    out, inside = [], False
    for line in body.splitlines(keepends=True):
        if line.startswith("#"):
            if inside:
                break
            text = line.lstrip("#").strip().lower()
            inside = "-".join(re.findall(r"[a-z0-9]+", text)) == slug
            continue
        if inside:
            out.append(line)
    return "".join(out).strip()


def _is_template(value) -> bool:
    """True when a frontmatter value is still scaffold — `<…>` placeholder text.

    An unauthored value must not SHADOW a real one. Scaffolding `gives:` (so it stops
    being a phantom instruction) gave every Task the frontmatter key, and §3.3 resolves
    a frontmatter key before a heading slug — which silently redirected every `#gives`
    ref away from an authored `## GIVES` section to the placeholder above it. A slot
    nobody has filled is not an answer, so resolution falls through to the heading.
    """
    items = value if isinstance(value, list) else [value]
    return bool(items) and all("<" in str(i) and ">" in str(i) for i in items)


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
    # Only now is a body read, and only this one (law 2 — never a bulk scan).
    section = _section(read(node["path"], "T2")["body"], fragment)
    return (cid, section, "heading") if section else (cid, None, "edge_unresolved")


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
    scopes = {s: {str(x) for x in ((members[by_slug[s]]["fm"] or {}).get("scope") or [])} for s in picks}
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


def _delta_lines(body: str) -> list:
    """The append-only delta line-items in a spec body (deltas.md grammar begins `- [`)."""
    return [ln for ln in body.splitlines(keepends=True) if ln.lstrip().startswith("- [")]


def _delta_identity(line: str) -> str:
    """The LESSON of a delta line — what two streams could disagree on the disposition of.

    Grammar `- [<COMP> · <status>] <learning> (evidence: <ptr>)`: identity is `<learning>`, so the
    same lesson filed `open` by one stream and `rejected` by another shares an identity and is a
    conflict, while two genuinely different lessons never collide.
    """
    s = line.strip()
    after = s.split("]", 1)[1] if "]" in s else s
    return after.split("(evidence:", 1)[0].strip()


def _union_into_deltas(path: Path, incoming: list) -> bool:
    """Append each delta line not already present, under `## Deltas` (as `learn` does). Idempotent."""
    node = read(path, "T2")
    lines = node["body"].splitlines(keepends=True)
    present = {ln for ln in lines if ln.lstrip().startswith("- [")}
    fresh = [ln for ln in dict.fromkeys(incoming) if ln not in present]  # dedupe incoming, drop known
    if not fresh:
        return False
    for i, line in enumerate(lines):
        if line.startswith("## Deltas"):
            at = i + 2 if i + 1 < len(lines) else i + 1
            lines[at:at] = fresh
            break
    else:
        lines += ["\n## Deltas\n\n"] + fresh
    write(path, f"---\n{node['raw']}\n---\n{''.join(lines)}")
    return True


def join(root, stream_dirs) -> tuple:
    """Fold N worktree stream bundles back into the main bundle (M1–M4).

    The engine stays NO-EXEC — the skill created the worktrees and spawned the builders; this only
    reconciles their bundles. wave() guaranteed disjoint scope, so streams touched different task
    nodes and the build never raced. Here at the join: node files copy byte-for-byte (disjoint),
    spec deltas union-merge (append-only), graph.json regenerates (rebuildable cache). A HARD-STOP
    stream is never admitted (R:MERGEHARDSTOP); a PASS stream is never dropped (R:DROPPASS).
    """
    root = Path(root)
    merged, skipped, specs_touched, conflicts = [], [], set(), []
    incoming = {}  # spec filename -> delta lines contributed by admitted streams (gathered, then partitioned)

    for d in stream_dirs:
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
                    incoming.setdefault(sp.name, []).extend(_delta_lines(read(sp, "T2")["body"]))

    # Partition the gathered deltas per spec: a lesson filed with two different dispositions across
    # streams is a CONFLICT (flag it, insert neither variant); everything else unions as before.
    for name, lines in incoming.items():
        groups = {}
        for ln in lines:
            groups.setdefault(_delta_identity(ln), []).append(ln)
        clean = []
        for ident, variants in groups.items():
            distinct = list(dict.fromkeys(variants))
            if len(distinct) > 1:
                conflicts.append({"spec": name, "identity": ident, "variants": distinct})
            else:
                clean.append(distinct[0])
        if _union_into_deltas(root / "specs" / name, clean):
            specs_touched.add(name)

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

RESERVED_FILES = ("index.md", "log.md", "PROJECT.md")

# The engine version — one source of truth. `_stamp`, `init`'s `engine:`/`tooling_engine:` stamps,
# and the drift-warn all read this, so a version bump is a single edit (M4).
ENGINE = "add/3.2.0"
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


def init(root, profile: str = "code", title: str = None) -> tuple:
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

    put("index.md", f'---\nabf_version: "1.3"\nname: {title}\n'
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
    put("PROJECT.md", f"---\ntype: Project\ntitle: {title}\ngoal: <one sentence — what is true when this ships>\n"
                      f"stage: mvp\nprofile: {profile}\n{_stamp()}\n---\n"
                      f"## CARD\ngoal: <the one line a cold reader needs>\nstate: initialised\n"
                      f"next: add new milestone <slug>\n")
    for slug, goal in lenses.items():
        put(f"specs/{slug}.md",
            f"---\ntype: Spec\ntitle: {slug.title()}\nlens: {slug}\nproject: {title}\n{_stamp()}\n---\n"
            f"## Now\n{goal}\n\n## Decisions that bind\n- <the first decision that constrains the rest>\n\n"
            f"## Deltas\n- <what changed, and the evidence that changed it>\n")

    # Vendor the engine + seed corpus so the bundle runs standalone (the skill's `add` = the vendored
    # `tooling/cli.py` for a project that never had this repo). overwrite=False keeps init idempotent —
    # a re-run never clobbers a human's vendored edit (R:CLOBBER); `doctor --sync` is the refresh path.
    written, could_not = _vendor_tooling(root, overwrite=False)
    created += written

    note = (f"created {len(created)} files ({profile} profile)" if created
            else "bundle already exists — nothing written")
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
    title = None
    charter = root / "PROJECT.md"
    if charter.is_file():
        text = charter.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^title:\s*(.+)$", text, re.M) \
            or re.search(r"^#\s+(?:PROJECT:\s*)?(.+)$", text, re.M)
        title = m.group(1).strip() if m else None

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
    init(root, "code", title)

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
SENSITIVITY_FLOOR = {
    "mechanical": "process",
    "data": "plan",
    "architecture": "plan",
    "security": "human",
}
TYPE_DIR = {"Task": "tasks", "Milestone": "milestones", "Spec": "specs",
            "Persona": "personas", "Prompt": "prompts", "Run": "runs"}
BODIES = {
    "Task": "## CARD\ngoal: <one line>\nwhy: <why this task exists — optional>\n"
            "beat: direction · next: add freeze {slug}\n\n"
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
            "## PLAN\ncontract: <the shape this publishes>\nscope: <files>\n\n"
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


def authority_for(graph: dict, cid: str) -> str:
    """`max(sensitivity floor, A17 sensitive-path floor)` — FORMAT §3.1.

    A17 is a path match against `index.md`'s `sensitive_paths:`, so a notary may perform it:
    it is mechanical, and it outranks the declared `sensitivity:` in one direction only.
    """
    import fnmatch
    node = graph.get(cid) or {}
    fm = node.get("fm") or {}
    floor = SENSITIVITY_FLOOR.get(fm.get("sensitivity"), "process")

    patterns = ((graph.get("/index.md", {}).get("fm") or {}).get("sensitive_paths")) or []
    scope = fm.get("scope") or []
    for entry in (scope if isinstance(scope, list) else [scope]):
        for pattern in (patterns if isinstance(patterns, list) else [patterns]):
            if fnmatch.fnmatch(str(entry), str(pattern)) or str(entry).startswith(
                    str(pattern).replace("**", "").replace("*", "").rstrip("/")):
                return "human"  # A17 — unstrikeable, and never lowered
    return floor


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


def new(root, node_type: str, slug: str, **fields) -> tuple:
    """Create a typed node. A colliding slug reports and writes nothing (R:DUPSLUG)."""
    root = Path(root)
    rel = f"{TYPE_DIR.get(node_type, 'tasks')}/{slug}.md"
    path = root / rel
    if path.exists():
        return None, f"slug already taken: {slug} ({rel})\nnext: pick another slug, or `add status` to see it"

    order = ["type", "title", "goal", "status", "depth", "kind", "sensitivity", "vibe", "flow",
             "task-kinds", "use-when", "not-when", "description", "sources",
             "milestone", "scope", "gives"]
    fm = {"type": node_type, "title": fields.pop("title", slug)}
    if node_type in LIFECYCLE_TYPES:  # a Persona/Prompt/Run has no lifecycle — no task status
        fm["status"] = "direction"
    # `gives:` is read by the direction digest and by every brief that resolves a `needs:`
    # ref — and it was scaffolded NOWHERE, in neither the body template nor this key order.
    # It came back empty in 3 of 3 live runs for exactly the reason the assumption did:
    # an instruction with no slot to fill is an instruction that does not happen.
    if node_type == "Task" and fields.get("gives") is None:
        fm["gives"] = ["S1 <the surface this publishes — an endpoint, function, or section>"]
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
    write(path, "---\n" + "\n".join(lines) + "\n---\n" + scaffold)
    # freeze is a lifecycle act — a Persona/Prompt/Run is done the moment it is written.
    nxt = f"add freeze {slug}" if node_type in LIFECYCLE_TYPES else "add status"
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
    stubs = placeholders_in(node_t2)
    if stubs:
        return None, (f"cannot freeze `{slug}` — the node still carries template placeholders: "
                      + " · ".join(stubs)
                      + f"\nnext: author {slug}'s RULES, ASSUMPTIONS and CHECKS, "
                        f"then add freeze {slug}")

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

    # R:UNBOUNDED (task sources-receipt) — an explore's approval IS questions plus a budget.
    # Presence only, never arithmetic: the engine is a notary; judging the number stays human,
    # exactly as exit criteria are read but never scored.
    if str((node_t2.get("fm") or {}).get("kind") or "") == "explore" \
            and not re.search(r"^budget:\s*\S", _section_of(node_t2.get("body") or "", "PLAN"), re.M):
        return None, (f'cannot freeze `{slug}` — an explore freezes on questions PLUS a budget, '
                      f'and `## PLAN` carries no `budget:` line -> "R:UNBOUNDED"'
                      f"\nnext: add one hard `budget:` line (tool calls · sources · wall-clock) "
                      f"to ## PLAN, then add freeze {slug}")

    authority = authority or authority_for(graph, cid)
    stamps = (entry.get("fm") or {}).get("verified") or []
    act = "refreeze" if any(s.get("act") in ("freeze", "refreeze") for s in stamps
                            if isinstance(s, dict)) else "freeze"
    node, err = _transition(root, cid, appends=[
        ("verified", f'{{ by: "{by}", at: {_today()}, act: {act}, authority: {authority}, '
                     f'direction: "{direction_digest(node_t2)}" }}')])
    if err:
        return None, err + "\nnext: add status"
    return node, (f"{act} recorded at authority `{authority}`"
                  f"\nnext: add brief {slug} — record the build entry, then build "
                  f"(`add run {slug} -- <cmd>`)")


def done(root, cid: str) -> tuple:
    """Transition to `done` only when a gate stamp entitles it.

    Refusing to create an unsupported record is the notary's duty, not guarding: this never
    prevents a human from writing the stamp themselves with their own authority.
    """
    graph = scan(root)
    node = graph.get(cid)
    if node is None:
        return False, ["node"], f"no such node: {cid}\nnext: add status"

    required = authority_for(graph, cid)
    stamps = [s for s in ((node["fm"] or {}).get("verified") or []) if isinstance(s, dict)]
    # a reopen RESETS the gate (loop.md): only gates that postdate the last reopen entitle `done`,
    # so a stale pre-reopen PASS cannot re-entitle a task the loop returned to a beat.
    last_reopen = max((i for i, s in enumerate(stamps) if s.get("act") == "reopen"), default=-1)
    gates = [s for s in stamps[last_reopen + 1:] if s.get("act") == "gate"]
    entitled = [s for s in gates
                if AUTHORITY_ORDER.index(str(s.get("authority", "process"))) >=
                AUTHORITY_ORDER.index(required)]

    missing = []
    if not gates:
        missing.append(f"a gate stamp (none recorded; `{required}` or above is required)")
    elif not entitled:
        missing.append(f"a gate at authority `{required}` — highest recorded is "
                       f"`{max(gates, key=lambda s: AUTHORITY_ORDER.index(str(s.get('authority', 'process')))).get('authority')}`")
    if missing:
        return False, missing, ("cannot record `done` — " + "; ".join(missing) +
                                f"\nnext: add gate {cid.rsplit('/', 1)[-1][:-3]}")

    _transition(root, cid, sets={"status": "done"})
    return True, [], f"{cid} is done\nnext: add status"


def reopen(root, cid: str, to: str, reason: str) -> tuple:
    """Return a done task to a beat with a reset gate and a recorded reason (loop.md).

    Fired by the loop's judgment when a deepened verify finds a criterion unmet on a task already
    `done`. It records a `reopen` stamp carrying the reason; the gate resets because `done` counts
    only gates that postdate this stamp — a stale PASS cannot re-entitle the reopened task.
    """
    root = Path(root)
    node = scan(root).get(cid)
    if node is None:
        return False, f"no such node: {cid}\nnext: add status"
    fm = node["fm"] or {}
    if fm.get("type") != "Task":
        return False, f"{cid} is not a Task — reopen returns a task to a beat\nnext: add status"
    if fm.get("status") != "done":
        return False, f"only a done task is reopened — {cid} is `{fm.get('status')}`\nnext: add status"
    if to not in ACTIVE_STATES:
        return False, f"`{to}` is not a beat ({' · '.join(ACTIVE_STATES)})\nnext: reopen --to build"
    # a stamp is a pre-formatted ABF flow-map STRING, not a dict — a dict serialises as Python
    # repr (`{'by': …}`) and parses back with quoted keys, so `s.get("act")` would miss it.
    stamp = f'{{ by: loop, at: {_today()}, act: reopen, to: {to}, reason: "{reason}" }}'
    _transition(root, cid, sets={"status": to}, appends=[("verified", stamp)])
    return True, f"{cid} reopened to {to} — gate reset\nnext: work the {to} beat, then re-gate"


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
        return False, f"no such node: {cid}\nnext: add status"
    if (node["fm"] or {}).get("type") != "Milestone":
        return False, (f"{cid} is not a Milestone — milestone-done closes milestones only\n"
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
        return False, (f"milestone_why_unset — {cid}'s CARD `why:` is still a placeholder\n"
                       f"next: state why {slug} exists in its CARD `why:`, then add milestone-done {slug}")

    exit_section = _section(body, "exit")
    checked = len(re.findall(r"^\s*- \[x\]", exit_section, re.M | re.I))
    unchecked = len(re.findall(r"^\s*- \[ \]", exit_section, re.M))
    total = checked + unchecked

    if unchecked:
        return False, (f"milestone_goal_unmet ({checked}/{total} exit criteria)\n"
                       f"next: check the remaining boxes in {cid.lstrip('/')}, then "
                       f"add milestone-done {slug}")

    _transition(root, cid, sets={"status": "done"})
    # 0 criteria => the goal-gate never fires (loop.md); close, but say the gate was empty.
    empty = "" if total else " — no exit criteria, so the goal-gate did not fire (add criteria to hold one open)"
    return True, f"{cid} milestone done ({checked}/{total} exit criteria met){empty}\nnext: add status"


def milestone_archive(root, cid: str) -> tuple:
    """Retire a done milestone (status → `archived`). Refuses one not done (loop.md).

    `milestone-done` is the only path to `done`; this is the only path past it, and it refuses to
    shelve a milestone whose goal-gate never closed — there is no quiet way around the goal-gate.
    """
    root = Path(root)
    node = scan(root).get(cid)
    if node is None:
        return False, f"no such node: {cid}\nnext: add status"
    fm = node["fm"] or {}
    slug = cid.rsplit("/", 1)[-1][:-3]
    if fm.get("type") != "Milestone":
        return False, f"{cid} is not a Milestone — archive retires milestones only\nnext: add status"
    if fm.get("status") != "done":
        return False, (f"cannot archive — {cid} is `{fm.get('status')}`, not done "
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
BEAT_KEYS = ("beat", "state")
# The one canonical next verb per beat — read by `status`'s frontier hint and `render_card`, so a
# repaired CARD's `next:` matches its beat instead of freezing at the direction-time affordance.
BEAT_NEXT = {"direction": "add freeze {slug}", "build": "add run {slug} -- <cmd>",
             "verify": "add gate {slug}", "done": "add status"}
# What a cold reader needs, in order. `Run` is absent on purpose — see `status`.
ORIENT_RANK = {"Project": 0, "Milestone": 1, "Task": 2, "Spec": 5, "Persona": 6, "Prompt": 7}


def _is_frozen(node) -> bool:
    """True once a task carries a freeze/refreeze stamp — the signal that authoring is done and the
    frontier hint should point at `brief` (build), not `freeze`. Status stays `direction` until done,
    so the beat is stamp-derived, not read from the status field."""
    stamps = (node.get("fm") or {}).get("verified") or []
    return any(isinstance(s, dict) and s.get("act") in ("freeze", "refreeze") for s in stamps)


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
        ("verified", f'{{ by: "{by}", at: {_today()}, act: replan, authority: process, '
                     f'note: "{text}" }}')])
    if err:
        return None, err + "\nnext: add status"
    return cid, (f"replan recorded on `{slug}` — steering noted, the seal untouched"
                 f"\nnext: keep building (`add run {slug} -- <cmd>` when green)")


def card_drift(graph: dict) -> list:
    """Nodes whose `## CARD` contradicts frontmatter — the defect e4's transition created.

    `[(cid, key, card_says, fm_says)]`. Reporting it is the notary's job; `render_card`
    repairs it.
    """
    out = []
    for cid, node in graph.items():
        status = (node["fm"] or {}).get("status")
        if not status:
            continue
        card = card_of(read(node["path"], "T2")["body"])
        for line in card.splitlines():
            key, sep, value = line.partition(":")
            if sep and key.strip() in BEAT_KEYS:
                said = value.split("·")[0].strip()
                if said and said != status and said in ("direction", "build", "verify", "done"):
                    out.append((cid, key.strip(), said, status))
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
            # direction-time affordance, so a done card kept reading `next: add freeze`. BEAT_NEXT
            # gives the beat its true next verb. Still exactly one line changes (idempotence holds).
            nxt = BEAT_NEXT.get(status, "add status").format(slug=slug)
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


def locate(root, query: str) -> tuple:
    """Reverse lookup: every node whose `scope:` matches `query` (equal or dir-prefix). Read-only.

    Answers "which node owns this path?" — the everyday navigation `status` cannot. A pure read over
    the graph: `(hits, note)` where `hits` is `[(cid, status, matched_scope_entry), …]`. It never writes.
    """
    graph = scan(Path(root))
    hits = []
    for cid, node in sorted(graph.items()):
        fm = node["fm"] or {}
        scope = fm.get("scope") or []
        for entry in (scope if isinstance(scope, list) else [scope]):
            if _scope_matches(entry, query):
                hits.append((cid, fm.get("status", "—"), str(entry)))
                break
    if not hits:
        return [], f"no node scopes `{query}`\nnext: add status"
    lines = [f"  · {cid.rsplit('/', 1)[-1][:-3]:<28} [{st}]  ({entry})" for cid, st, entry in hits]
    return hits, f"{len(hits)} node(s) scope `{query}`:\n" + "\n".join(lines) + "\nnext: add status"


def _beat_of(node) -> str:
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
    if any(s.get("act") == "run" for s in stamps):
        return "verify"
    return "build" if _is_frozen(node) else "direction"


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


def _next_verb(graph: dict, cid: str) -> str:
    """The one runnable next command for a task, by its stamp-derived beat."""
    slug = cid.rsplit("/", 1)[-1][:-3]
    node = graph[cid]
    beat = _beat_of(node)
    fm = node.get("fm") or {}
    # W1 (R:UNBRIEFED): at the build beat the ENTRY comes first — a sealed, unbriefed task
    # points at `add brief`, and moves on to the run the moment the entry is recorded.
    if beat == "build" and fm.get("type") == "Task" \
            and str(fm.get("depth") or "standard") != "quick" \
            and sealed_direction(fm) and not _brief_entered(fm.get("verified") or []):
        return f"add brief {slug}"
    return BEAT_NEXT.get(beat, "add status").format(slug=slug)


def todo(root, milestone: str = None) -> tuple:
    """The open worklist: active Tasks (direction|build|verify) grouped by beat, each with its next
    verb. Optionally restricted to one milestone. Read-only — `(items, note)`, never a write."""
    graph = scan(Path(root))
    msel = _wave_slug(milestone) if milestone else None
    items = []
    for cid in active(graph):
        fm = graph[cid]["fm"] or {}
        if fm.get("type") != "Task":
            continue
        if msel and _wave_slug(fm.get("milestone")) != msel:
            continue
        items.append((cid, _beat_of(graph[cid]), _next_verb(graph, cid)))
    if not items:
        where = f" under `{milestone}`" if milestone else ""
        return [], f"nothing open{where}\nnext: add status"
    order = {"direction": 0, "build": 1, "verify": 2}
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
            node_t2 = read(graph[cid]["path"], "T2")
            if gives_unauthored(node_t2) and _section_of(node_t2.get("body") or "",
                                                         "ASSUMPTIONS").strip():
                hint = "  (gives: unauthored — no surfaces to sweep)"
            elif (collapsed := collapsed_surfaces(node_t2)) and \
                    _section_of(node_t2.get("body") or "", "ASSUMPTIONS").strip() and \
                    str((node_t2.get("fm") or {}).get("depth") or "standard") != "quick":
                hint = f"  (split {' · '.join(collapsed)} — one surface per S id)"
            else:
                left = len(assumption_sweep(node_t2))
                if left:
                    hint = f"  ({left} unswept pair{'s' if left > 1 else ''})"
        lines.append(f"  · {cid.rsplit('/', 1)[-1][:-3]:<24} → {nxt}{hint}")
    where = f" under `{milestone}`" if milestone else ""
    return items, f"{len(items)} open task(s){where}:\n" + "\n".join(lines)


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
                    "archive them as the record of how this was built, then start a 3.0 bundle\n"
                    "next: add init")
        return f"no bundle here — run `add init` to create one\nnext: add init"

    graph = scan(root)
    out = []

    project = next((n for n in graph.values() if (n["fm"] or {}).get("type") == "Project"), None)
    out.append(f"{((project or {}).get('fm') or {}).get('title', Path(root).name)}"
               f"  ·  {len(graph)} nodes")

    # Orientation is about WORK. Receipts are evidence — reachable from the task that owns
    # them, and never the thing a cold reader needs first. Ordering by ORIENT_RANK keeps the
    # 20-line budget spent on milestones and tasks rather than on files named `1.md`.
    def keep(cid):
        fm = graph[cid]["fm"] or {}
        if fm.get("type") == "Run":
            return False
        return all or fm.get("status") not in ("done", "dropped")

    shown = sorted((c for c in graph if keep(c)),
                   key=lambda c: (ORIENT_RANK.get((graph[c]["fm"] or {}).get("type"), 9), c))
    for cid in shown[:MAX_LINES]:
        fm = graph[cid]["fm"] or {}
        out.append(f"  · {cid.rsplit('/', 1)[-1][:-3]:<28} [{fm.get('status', '—')}] {fm.get('type', '')}")
    if len(shown) > MAX_LINES:
        out.append(f"  … {len(shown) - MAX_LINES} more of {len(shown)} (`--all` for done nodes)")

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
        nxt = f"next: add gate {waiting[0].rsplit('/', 1)[-1][:-3]}"
    elif frontier:
        f0 = frontier[0]
        # An unfrozen frontier task still needs its direction authored + frozen; brief would compile a
        # node of placeholders. A frozen one is ready to hand to a builder. Pick the verb by the stamp.
        verb = "brief" if _is_frozen(graph[f0]) else "freeze"
        nxt = f"next: add {verb} {f0.rsplit('/', 1)[-1][:-3]}"
    elif any((n["fm"] or {}).get("type") == "Milestone" for n in graph.values()):
        nxt = "next: add new task <slug>"
    else:
        nxt = "next: add new milestone <slug>"
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


def _git(root, *args, timeout: int = 30, input: str = None):
    """Run one git command. Returns None when git is absent or the tree is not a repo."""
    try:
        done = subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                              text=True, timeout=timeout, input=input)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.strip() if done.returncode == 0 else None


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
        for path in candidates:
            if not path.is_file():
                continue
            rel = path.relative_to(root)
            # Build noise is not the code under review — hashing it would make the digest flap.
            if "__pycache__" in rel.parts or path.suffix in (".pyc", ".pyo"):
                continue
            rels.append(rel)
    hashes = _git_blobs(root, [str(r) for r in rels])
    for rel in rels:
        blob = hashes.get(str(rel)) or _git(root, "hash-object", str(rel))
        if blob:
            out.append({"path": rel.as_posix(), "blob": f"sha1:{blob}"})
    return out


def fresh(receipt: dict, root) -> tuple:
    """`(ok, why)` — recompute the digest and compare. Any difference is stale."""
    root = Path(root)
    recorded = receipt.get("scope_digest") or []
    if receipt.get("freshness") != "content" or not recorded:
        return False, ("receipt carries no content digest — freshness cannot be established "
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


def run(root, cid: str, command: list, cwd=None, timeout: int = RUN_TIMEOUT, junit=None) -> dict:
    """Execute the agent's own command, notarise the result as a Run node.

    Never executes anything the caller did not supply. A non-zero exit and a timeout are
    both recorded outcomes — this function does not raise on a failing command (law 3).
    """
    root, cwd = Path(root), Path(cwd or root)
    node = (scan(root).get(cid) or {})
    scope = ((node.get("fm") or {}).get("scope")) or []
    # The digest root is the BUNDLE PARENT — the identical root `gate` hands `fresh()` — never
    # the cwd. Field finding (hardening tally #1): a cwd below the project computed the digest
    # against paths that did not exist there, so the receipt silently degraded to mtime and the
    # gate refused a PASS with a message naming neither the cause nor the fix. `cwd` stays what
    # it says: the command's working directory, nothing more.
    digest = scope_digest(root.parent, scope)

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
    if scope and not digest:
        degrade = ("scope: declared but no digest recorded — the bundle parent is not a git "
                   "working tree, or the scope paths do not exist there; freshness degrades to mtime")
        note = f"{note}; {degrade}" if note else degrade

    slug = cid.rsplit("/", 1)[-1][:-3]
    runs = root / f"tasks/{slug}.d/runs"
    runs.mkdir(parents=True, exist_ok=True)
    n = len(list(runs.glob("*.md"))) + 1
    # A24: the evidence kind is EARNED, never assumed. `test-ids` requires IDs a runner
    # actually reported — e12 owes that extraction. Until then the honest kind for a bare
    # command is `command-exit`. Freshness is a separate question from evidence, and wiring
    # both to the presence of a digest (as this first did) claims proof that does not exist.
    # A24's ladder is climbed only with real IDs (e12). No report, no promotion.
    ids = extract_ids(junit) if junit else {}
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
               "stdout": stdout.strip().splitlines()[-1] if stdout.strip() else "",
               "note": note}
    body = (f"---\ntype: Run\nruntime: process\ntask: {cid}\n"
            f'computation: "{" ".join(str(c) for c in command)}"\n'
            f"receipt:\n" + "".join(f"  {k}: {v!r}\n" if k in ("stdout", "note") else f"  {k}: {v}\n"
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
        f'outcome: {"PASS" if exit_code == 0 else "FAIL"}, receipt: {cid_run} }}')])
    return {"path": runs / f"{n}.md", "receipt": receipt, "computation": " ".join(str(c) for c in command),
            "note": f"receipt {n} recorded (exit {exit_code})\nnext: add gate {slug}"}


# The living spec ↔ its 5-DD competency tag (deltas.md). A delta's tag names the competency the
# lesson sharpens; the spec filename is where it lands. `learn` writes the tag from the lens.
LENS_COMP = {"domain": "DDD", "system": "SDD", "experience": "UDD", "quality": "TDD", "method": "ADD"}


def learn(root, lens: str, lesson: str, evidence: str = None) -> tuple:
    """Append a lesson to a spec's `## Deltas` in the frozen delta grammar, `open` by default.

    Grammar (deltas.md): `- [<COMPETENCY> · open] <lesson> (evidence: <pointer>)`. Evidence is
    required, not decorative — a lesson with no evidence is an opinion, and a spec full of opinions
    is the thing this method exists to replace. `open` is the only status `learn` writes; a human
    moves it to `folded`/`rejected` (the AI never self-consolidates).
    """
    if not evidence:
        return False, "refused: a lesson needs evidence — cite the receipt or decision that caused it"
    path = Path(root) / "specs" / f"{lens}.md"
    if not path.is_file():
        return False, f"no such spec lens: {lens}\nnext: add status"
    comp = LENS_COMP.get(lens, lens.upper())
    node = read(path, "T2")
    lines = node["body"].splitlines(keepends=True)
    entry = f"- [{comp} · open] {lesson} (evidence: {evidence})\n"
    for i, line in enumerate(lines):
        if line.startswith("## Deltas"):
            lines.insert(i + 2 if i + 1 < len(lines) else i + 1, entry)
            break
    else:
        lines += ["\n## Deltas\n\n", entry]
    write(path, f"---\n{node['raw']}\n---\n{''.join(lines)}")
    return True, f"recorded on specs/{lens}\nnext: add status"


DELTA_LINE = re.compile(r"-\s+\[([A-Z]+)\s*·\s*(\w+)\]\s*(.*)")


def deltas(root, status: str = "open") -> tuple:
    """List every delta at `status` across the five specs. `(items, note)`.

    A reader over the frozen grammar (deltas.md): `open` is the carried inventory the loop reads to
    propose the next tasks; `folded`/`rejected` are decided and stay out of the listing. Never mutates.
    """
    root = Path(root)
    items = []
    for path in sorted((root / "specs").glob("*.md")):
        for line in read(path, "T2")["body"].splitlines():
            m = DELTA_LINE.match(line.strip())
            if m and m.group(2) == status:
                items.append((path.stem, m.group(1), m.group(3).strip()))
    if not items:
        return items, f"no {status} deltas\nnext: add status"
    rendered = [f"{status} deltas ({len(items)}):"]
    rendered += [f"  · [{c}] {s}: {t}" for s, c, t in items]
    rendered.append("next: at close, fold or reject each (loop.md)")
    return items, "\n".join(rendered)


def fold(root, lens: str, match: str) -> tuple:
    """Retag the open delta(s) in `lens` whose text contains `match` as `folded`. `(ok, note)`.

    Consolidation is the human's judgment (deltas.md) — the engine only records the status flip, and
    only on a human's call. A fold matching nothing refuses (R:NOMATCH) rather than silently no-op.
    """
    path = Path(root) / "specs" / f"{lens}.md"
    if not path.is_file():
        return False, f"no such spec lens: {lens}\nnext: add status"
    node = read(path, "T2")
    out, folded = [], 0
    for line in node["body"].splitlines(keepends=True):
        m = DELTA_LINE.match(line.strip())
        if m and m.group(2) == "open" and match in m.group(3):
            line = line.replace(f"[{m.group(1)} · open]", f"[{m.group(1)} · folded]", 1)
            folded += 1
        out.append(line)
    if not folded:
        return False, f"R:NOMATCH — no open delta in {lens} matching '{match}'\nnext: add deltas"
    write(path, f"---\n{node['raw']}\n---\n{''.join(out)}")
    return True, f"folded {folded} delta(s) in specs/{lens}\nnext: add status"


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


def gives_unauthored(node: dict) -> bool:
    """True when `gives:` is missing or still the scaffold — i.e. nothing to sweep.

    Without this the gate has a one-line off switch: delete `gives:`, get no surfaces,
    sweep vacuously clean.
    """
    entries = (node.get("fm") or {}).get("gives") or []
    return not entries or any("<" in str(e) for e in entries)


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
        if re.match(r"^n/?a\b", rest.strip(), re.I):
            waived.add(dim)
            continue
        found = re.search(r"covers:\s*([^·]*)", rest)
        if found:
            covered[dim].update(re.findall(r"\bS\d+\b", found.group(1)))
    return [(d, sid) for d in SWEEP_DIMENSIONS if d not in waived
            for sid in surfaces if sid not in covered[d]]


def placeholders_in(node: dict) -> list:
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
        for line in _section_of(node.get("body") or "", heading).splitlines():
            if line.startswith("- ") and PLACEHOLDER.search(re.sub(r"`[^`]*`", "", line)):
                found.append(line.strip())
    return found


def _canon(text: str) -> str:
    """Trailing whitespace and blank lines are not contract changes."""
    return "\n".join(line.rstrip() for line in text.splitlines() if line.strip())


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
    payload = "\n".join((_canon(_section_of(body, "RULES")),
                         _canon(_section_of(body, "CHECKS")),
                         _canon("\n".join(str(g) for g in gives))))
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()[:16]


def sealed_direction(fm: dict) -> str:
    """The digest carried by the most recent freeze/refreeze, or None.

    None means "cannot verify", not "verified clean": bundles frozen by a pre-seal engine carry no
    digest, and refusing them would retroactively strand every task frozen before this shipped.
    """
    for stamp in reversed((fm or {}).get("verified") or []):
        if isinstance(stamp, dict) and stamp.get("act") in ("freeze", "refreeze"):
            return stamp.get("direction")
    return None


def rules_of(node: dict) -> list:
    """Every Must and Reject id declared in the node's RULES section."""
    body = read(node["path"], "T2")["body"]
    return [m.group(1) for m in (RULE_ID.match(l) for l in _section_of(body, "RULES").splitlines()) if m]


def edges_of(node: dict) -> list:
    """The REAL enumerated edge ids (`E<n>`) declared in the node's `## EDGES` section.

    An edge is a first-class `covers:` referent (C7): the gate binds it exactly as a Must. A line
    still carrying the scaffold `<placeholder>` is NOT a real edge — a task that never enumerated
    an edge, or left the scaffold untouched, owes no edge coverage (backward compatible). Backticked
    spans are code, not placeholders (same exclusion `placeholders_in` makes)."""
    body = read(node["path"], "T2")["body"]
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
        for rule in (r.strip() for r in match.group(2).split(",")):
            if rule:
                out.setdefault(rule, []).append(check)
    return out


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
    phase = phase or PHASE_OF.get(str(fm.get("status", "")), "build")
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
        refs.append((f"{ident_ref}#{frag}" if frag else ident_ref,
                     None if why == "edge_unresolved" else _flat(value)))
    binds = bind_sections(root)

    persona = None
    if fm.get("persona"):
        pcid, pnode, _ = resolve(graph, str(fm["persona"]), cid)
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
        for ref, value in refs:
            if value is None:
                out.append(f'    <ref id="{ref}" unresolved="true"/>')
            else:
                out.append(f'    <ref id="{ref}" frozen="true">')
                out += ["      " + l for l in value.splitlines()]
                out.append("    </ref>")
        for scid, text in binds:
            rid = f"{scid}#decisions-that-bind"
            if drop_specs:
                out.append(f'    <ref id="{rid}" omitted="budget"/>')
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

    The compile itself stays pure (`brief` is read-only and `gate` calls it); THIS is the
    write, and it is what `gate`'s R:UNBRIEFED refusal reads. Only a frozen Task records an
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
        f'{{ by: "{by}", at: {_today()}, act: brief, authority: process, '
        f'brief: "{digest}" }}')])
    return digest, (f"brief {digest} recorded as the build entry"
                    f"\nnext: add run {slug} -- <cmd>")


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


def latest_receipt(root, cid: str) -> tuple:
    """`(receipt_dict, cid)` for the newest receipt of a task, or `(None, None)`."""
    root = Path(root)
    slug = cid.rsplit("/", 1)[-1][:-3]
    runs = sorted((root / f"tasks/{slug}.d/runs").glob("*.md"),
                  key=lambda p: int(p.stem) if p.stem.isdigit() else 0)
    if not runs:
        return None, None
    fm = read(runs[-1], "T0")["fm"] or {}
    return fm.get("receipt"), "/" + str(runs[-1].relative_to(root))


def gate(root, cid: str, verdict: str, by: str, authority: str = None,
         reason: str = None) -> tuple:
    """Record a verdict, or refuse and say what would make it pass. `(ok, note)`."""
    root = Path(root)
    slug = cid.rsplit("/", 1)[-1][:-3]

    def refuse(why: str, fix: str) -> tuple:
        return False, f"cannot record `{verdict}` — {why}\nnext: {fix}"

    if verdict not in VERDICTS:
        return refuse(f"unknown verdict {verdict!r}",
                      f"add gate {slug} <{' | '.join(VERDICTS)}>")
    graph = scan(root)
    if cid not in graph:
        return refuse(f"no such node: {cid}", "add status")
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
    if verdict == "PASS" and security_floored \
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
        if verdict == "PASS" and direction_digest(node) != sealed_q:
            return refuse("RULES/CHECKS drifted after the freeze that approved them — a frozen "
                          "contract changes by refreezing, never by a silent edit",
                          f'add freeze {slug} --by "<name>" to record the change, or '
                          f'add reopen {slug} --to direction --reason "<why the contract moved>"')
        stubs = placeholders_in(node)
        if stubs and verdict == "PASS":
            return refuse("the node still carries template placeholders: " + " · ".join(stubs),
                          f"author {slug}'s RULES and CHECKS, then add gate {slug} PASS")
        body = node["body"]
        musts = re.findall(r"^-\s*(M\d+)\b", _section_of(body, "RULES"), re.M)
        findings = _section_of(body, "FINDINGS")
        # A finding closes a question only with a REAL ref — `(evidence: )`, the template's
        # `(evidence: <ref>)`, and prose that merely contains the word all stay open.
        closed = [m for m in musts
                  if re.search(rf"answers {m}\b[^\n]*\(evidence:\s*[^)\s<][^)]*\)", findings)]
        opens = [m for m in musts if m not in closed]
        if verdict == "PASS" and (not musts or opens):
            named = ", ".join(opens) if opens else "(no frozen questions at all)"
            return refuse("open questions hold the PASS — no evidence-carrying finding answers: "
                          f'{named} -> "R:HOLLOW_EXPLORE"',
                          f"write the missing `F<n> (answers M<n>) · <finding> · (evidence: <ref>)` "
                          f"lines in ## FINDINGS, or "
                          f'add gate {slug} RISK-ACCEPTED --reason "open: {named}"')
        authority = authority_for(graph, cid)
        extra = (f', kind: sources, closed: "{len(closed)}/{len(musts)}"'
                 if verdict == "PASS" else "")
        stamp = (f'{{ by: "{by}", at: {_today()}, act: gate, authority: {authority}, '
                 f'outcome: {verdict}{extra}'
                 + (f', reason: "{reason}"' if reason else "") + " }")
        _, t_err = _transition(root, cid, appends=[("verified", stamp)])
        if t_err:
            return False, t_err + "\nnext: add status"
        if verdict == "PASS":
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
    if verdict == "PASS" and code not in ("0", "", "None"):
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
    declared_scope = (graph[cid]["fm"] or {}).get("scope") or []
    if not declared_scope:
        # A CARD claiming a scope the frontmatter lacks is worse than an honestly unscoped node:
        # the CARD is what a human reads, while `scope_digest` and A17's path floor both match
        # against frontmatter. This gated e13 itself with freshness silently skipped.
        card_scope = [l for l in card_of(node_body(graph[cid])).splitlines()
                      if l.startswith("scope:") and l.partition(":")[2].strip()]
        if card_scope and verdict == "PASS":
            return refuse(f"the CARD claims a scope the frontmatter does not declare "
                          f"({card_scope[0].strip()}) — freshness and A17's path floor both read "
                          f"frontmatter, so both were silently skipped",
                          f"add scope: to {slug}'s frontmatter, then add run {slug} -- <cmd>")
        freshness = "freshness: n/a — the node declares no `scope:`"
    else:
        ok, why = fresh(receipt, root.parent)
        if not ok and verdict == "PASS":
            return refuse(f"the receipt is stale — {why}", f"add run {slug} -- <cmd>")
        freshness = f"freshness: {'fresh' if ok else 'STALE'} — {why}"

    node = read(graph[cid]["path"], "T2")
    stubs = placeholders_in(node)
    if stubs and verdict == "PASS":
        return refuse("the node still carries template placeholders: " + " · ".join(stubs),
                      f"author {slug}'s RULES and CHECKS, then add gate {slug} PASS")

    # Constraint 3, structurally: what the freeze approved is what the build must have been held to.
    # A missing digest means a pre-seal engine froze this node — unverifiable, so not refusable.
    sealed = sealed_direction(sfm)
    if sealed and verdict == "PASS" and direction_digest(node) != sealed:
        return refuse("RULES/CHECKS drifted after the freeze that approved them — a frozen contract "
                      "changes by refreezing, never by a silent edit",
                      f'add freeze {slug} --by "<name>" to record the change, or '
                      f'add reopen {slug} --to direction --reason "<why the contract moved>"')

    # W1 (beta-2, R:UNBRIEFED) — the brief is Build's ENTRY, not the verdict's garnish.
    # beta-1 stamped a brief hash HERE, at gate time: a record of what the instructions would
    # have been, taken after the build was over. Using the brief during Build was recommended
    # prose, and three probe campaigns each showed what recommended prose becomes. Keyed off
    # the seal (like drift) so pre-seal bundles stay gateable; quick depth is ceremony-tuned
    # out, the same stance as the sweep's exemptions.
    if sealed and verdict == "PASS" and sfm.get("type") == "Task" \
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

    # Refusal 2 (M2) — a Must proven by nothing is a label (A15). e12's M3, landing.
    reported = {i: "pass" for i in (receipt.get("passed") or [])}
    reported.update({i: "fail" for i in (receipt.get("failed") or [])})
    gaps = unbound(node, reported)
    if gaps and verdict == "PASS":
        return refuse("these rules have no reported passing check: " + ", ".join(gaps),
                      f'add gate {slug} RISK-ACCEPTED --reason "<why the gap is acceptable>"')

    authority = authority_for(graph, cid)          # computed, never the caller's claim (M3)
    digest = brief(root, cid)["hash"]              # A16 — the instructions that drove the work
    stamp = (f'{{ by: "{by}", at: {_today()}, act: gate, authority: {authority}, '
             f'outcome: {verdict}, receipt: {receipt_cid}, brief: "{digest}"'
             + (f', reason: "{reason}"' if reason else "") + " }")
    _, t_err = _transition(root, cid, appends=[("verified", stamp)])
    if t_err:
        return False, t_err + "\nnext: add status"

    if verdict == "PASS":
        done(root, cid)
        render_card(root, cid)
        tail = f"{cid} is done"
    else:
        tail = f"{verdict} recorded; {slug} stays in `{(graph[cid]['fm'] or {}).get('status')}`"
    note = (f"gate {verdict} recorded at authority `{authority}`"
            + f"\n  {freshness}"
            + (f"\n  unbound (reported, not blocking): {', '.join(gaps)}" if gaps else "")
            + f"\n  brief {digest} · receipt {receipt_cid}\n{tail}\nnext: add status")
    return True, note


def quick(root, slug: str, title: str, cmd: list, by: str, cwd=None,
          depth: str = "quick", **fields) -> tuple:
    """§3d's quick lane: new + freeze + run + gate in ONE engine call.

    Refused above `quick` depth. A one-call lane that works at `deep` is not a lane, it is a
    bypass of every control this engine has.
    """
    if depth != "quick":
        return False, (f"the one-call lane is `quick` depth only; this is `{depth}`"
                       f"\nnext: add new task {slug} --depth {depth}")
    root = Path(root)
    cid, _ = new(root, "Task", slug, title=title, depth="quick", **fields)
    # A quick task's evidence is its exit code, not a covers-bound suite (§3d: "rename a flag;
    # add a log line"). The standard template's placeholder Musts would make the one-call lane
    # unclosable by construction, so the quick body declares none.
    path = root / cid.lstrip("/")
    stub = read(path, "T2")
    write(path, f"---\n{stub['raw']}\n---\n## CARD\ngoal: {title}\n"
                f"beat: build · next: add run {slug} -- <cmd>\n\n"
                f"## EVIDENCE\nreceipt: <runs/<n>.md>\ngate: <PASS>\n")
    freeze(root, cid, by=by)
    node = run(root, cid, cmd, cwd=cwd or root.parent)
    if node["receipt"]["exit"] != 0:
        return False, (f"the command exited {node['receipt']['exit']} — a red command earns no gate"
                       f"\nnext: fix, then add run {slug} -- <cmd>")
    ok, note = gate(root, cid, "PASS", by=by)
    return ok, f"quick lane: {slug} opened, run and gated in one call\n{note}"


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


def checks_sync(root, cid: str, paths) -> tuple:
    """Rewrite one node's CHECKS from the suite. `(changed, note)`.

    Refuses a node carrying a gate stamp (R:SILENTFIX). That is the §3.6 asymmetry F2 turned on:
    e12's own CHECKS were corrected freely because nothing had been stamped, and M0's nine cannot
    be, because a gate was taken against them. Refusing to repair is not refusing to REPORT —
    `checks_verify` still speaks.
    """
    # Materialised once: this function walks `paths` to compile and again to report how many files
    # it read, and a generator makes the second walk empty. The section came out correct and the
    # note said "from 0 suite files" — a true report is not optional in a notary.
    root, paths = Path(root), list(paths)
    node = scan(root).get(cid)
    if node is None:
        return False, f"no such node: {cid}\nnext: add status"
    if any(s.get("act") == "gate" for s in ((node["fm"] or {}).get("verified") or [])
           if isinstance(s, dict)):
        return False, (f"{cid} carries a gate stamp — a gated claim is recorded, not repaired "
                       f"(§3.6, R:SILENTFIX)\nnext: add checks {cid.rsplit('/', 1)[-1][:-3]} --verify")

    full = read(node["path"], "T2")
    lines, gaps = _checks_lines(full, paths)
    body = full["body"]
    start = body.find("## CHECKS")
    if start < 0:
        return False, f"{cid} has no `## CHECKS` section to compile into\nnext: add status"
    rest = body[start:]
    end = start + (rest.find("\n## ", 1) if "\n## " in rest[1:] else len(rest))
    section = ("## CHECKS\n" + "\n".join(lines) +
               "\nred-first: every check above MUST fail for the right reason before BUILD.\n" +
               (f"unlabelled: {', '.join(gaps)} — carry no `covers:`; reported, never inferred (M3)\n"
                if gaps else "") +
               "<!-- COMPILED from the suite (e14). Do not author here: a citation edited by hand\n"
               "     cannot be distinguished from one that was never true (F2). -->\n")
    new_body = body[:start] + section + body[end:]
    if new_body == body:
        return False, f"{cid}'s CHECKS already match the suite\nnext: add status"
    write(node["path"], f"---\n{full['raw']}\n---\n{new_body}")
    return True, (f"{cid}: {len(lines)} checks compiled from {len(list(paths))} suite files"
                  + (f" · {len(gaps)} unlabelled" if gaps else "") + "\nnext: add status")


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

ABF_TYPES = ("Project", "Milestone", "Task", "Spec", "Persona", "Prompt", "Run")
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

    for src, key, ref, target in edges(graph):
        rel = src.lstrip("/")
        resolved = (root / _norm(src, ref).lstrip("/")).resolve()
        if not resolved.is_relative_to(root.resolve()):
            find("error", "edge_out_of_bundle", f"{rel} -> {ref}", src)
        elif target is None:
            find("info", "edge_unresolved", f"{rel} -> {ref}", src)
        elif (fragment := ref.partition("#")[2]):
            body = read(graph[target]["path"], "T2")["body"]
            if fragment not in (graph[target]["fm"] or {}) and fragment not in _heading_slugs(body):
                find("info", "edge_unresolved", f"{rel} -> {ref}", src)

    for cid, node in sorted(graph.items()):
        for link in MD_LINK.findall(read(node["path"], "T2")["body"]):
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
    for cid, key, said, actual in card_drift(graph):
        find("info", "card_drift", f"{cid.lstrip('/')}: CARD `{key}` says {said}, status is {actual}", cid)
    # Coverage: a sensitive task with no recorded lens. R:NOLENS floors PARALLEL streams only, so a
    # SEQUENTIAL architecture/security/data task can carry no lens and go unseen. Surface it — info,
    # reports-only, never a gate (that HARD-STOP question is A2, out of scope here).
    for cid, node in sorted(graph.items()):
        fm = node["fm"] or {}
        if fm.get("type") != "Task" or SENSITIVITY_FLOOR.get(fm.get("sensitivity"), "process") == "process":
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
    if not changed:
        return False, ("every compiled artifact already matches the nodes\n"
                       "next: add doctor  (to see what is reported but not repairable)")
    return True, ("recomputed " + " · ".join(changed) +
                  "\nnext: add doctor  (orphaned receipts and gated claims are never repaired)")
