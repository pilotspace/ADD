#!/usr/bin/env python3
"""ADD — minimal scaffolder + state tracker for AI-Driven Development.

One file = one task. This tool generates the per-task PLAN.md (which Claude fills
in step by step) and maintains .add/state.json so any fresh session can resume
with `add.py status` instead of re-reading the whole repo. That is the anti-
context-rot core of the ADD method.

Stdlib only. Writes are atomic (temp + os.replace) and refuse to clobber
existing artifacts unless --force is given.
"""
from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:                       # component-aware-add registry parse (Python 3.11+ stdlib)
    import tomllib
except ModuleNotFoundError:   # < 3.11: the registry is unsupported → degrade to opt-out
    tomllib = None

# --- constants (moved to add_engine/constants.py — engine-modularization) ----
from add_engine.constants import *  # noqa: F401,F403  (public constants via __all__)
from add_engine.constants import (  # the _-prefixed names (import * skips them)
    _GITIGNORE_BODY, _GUIDE_BEGIN, _GUIDE_END,
    _FALLBACK_TASK,
    _DEFAULT_WIDTH,
    _DELTA_RE, _PERSONA_TAG_RE, _EVIDENCE_RE, _SPEC_DELTA_RE,   # shared delta regexes (taskdoc + deltas-web lint)
    _SEED_POINTER_RE,   # shared (delta-task-backlink) — reads the `[→ slug]` seed stamp back
    _DIALECT_CLASSES,   # shared (spec-dialect-floor) — crossing warning + check lint
    _AUTONOMY_LEVELS,   # shared (autonomy resolvers + _AUTONOMY_ORDER/cmd_autonomy)
    _SENSITIVITY_VALUES,  # shared (_task_sensitivity + cmd_freeze/status/audit) — risk-class taxonomy
)

# --- terminal-render primitives (moved to add_engine/render.py) -------------
from add_engine.render import (
    _bar, _phase_track, _use_ascii, _color_enabled, _term_width, _colorize, _clip, _wrap,
)

# --- milestone-doc readers (moved to add_engine/milestones.py) --------------
from add_engine.milestones import (
    _has_production_roadmap, _project_goal, _milestone_doc, _exit_criteria,
    _exit_criteria_cited, _stage_criteria, _all_milestones_done,
)

# --- component/federation subsystem (moved to add_engine/components.py) ------
from add_engine.components import (   # kernel-trim: only the generic scope utilities survive
    _confined, _in_scope,
)

# --- update-nudge version helpers (moved to add_engine/version.py) ----------
from add_engine.version import (
    _read_json_safe, _version_gt, _fetch_latest_version,
)

# kernel-trim (ADD 2.0 M5): the release verbs died — add_engine/release.py retired with them.

# --- PLAN.md structural readers (moved to add_engine/taskdoc.py) ------------
from add_engine.taskdoc import (
    _task_header, _count_test_defs, _primary_test_files, _tests_count,
    _declared_test_files, _declared_tests_count, _tests_info, _task_prose,
    _phase_spans, _raw_phase_bodies, _spec_delta_entries,
)

# --- autonomy-level resolvers (moved to add_engine/autonomy.py) -------------
from add_engine.autonomy import (
    _autonomy_level, _effective_autonomy, _project_autonomy, _project_autonomy_token,
)

# --- keyword/substring corpus search (NEW — add_engine/search.py) -----------
from add_engine.search import _search_corpus


def _phase_index(name: str) -> int:
    """Ordinal of a phase in PHASES; used to enforce forward-skip rules.
    Fail-soft on every legacy token (phase-collapse-3): a pre-collapse value computes
    the ordinal of its 3-phase home instead of raising ValueError."""
    return PHASES.index(LEGACY_PHASES.get(name, name))

# --- low-level IO (moved to add_engine/io_state.py — engine-modularization) -
from add_engine.io_state import (  # re-exported as module globals: callers use bare
    _now, _atomic_write, _atomic_write_bytes, _atomic_write_many,  # names so patches
    find_root, _require_root, _migrate_state, _state_text_or_die,  # on add.<name>
    _die,                                                          # still resolve;
    _register_invocation, _clear_last_fail,                        # kickoff-truth M3 dup-failure hooks
    _CONFLICT_MARKER_RE,                                            # conflict-marker re
    _load_state_for_json,                                          # --json state loader
    _md5_text, _md5_file,                                          # md5 hashing helpers
    _personas_unseeded,                                            # persona-seed-nudge predicate
    _real_persona_slugs,                                           # persona-fit-nudge slug listing
)


# --- active milestone/task accessors (moved to add_engine/accessors.py) -------
from add_engine.accessors import (
    _active_milestone, _active_task, _set_active_milestone,
    _set_active_task, _activate_milestone, _deactivate_milestone,
)

# --- state load/save (KEPT in add.py: write-path pinned by add._atomic_write tests) -

def _normalize_phase_tokens(state: dict) -> dict:
    """Rewrite the legacy phase tokens on task records to their 3-phase home
    (phase-collapse-3: specify/scenarios/ground/plan/contract/tests -> direction ·
    observe -> verify) — the ONE read-side accessor the contract's READ MAP names. TOTAL ·
    idempotent · never raises. Only legacy tokens are touched — an already-collapsed
    record is byte-identical, so a second pass changes nothing. Normalizes on READ only;
    state is persisted (migrated) solely when a command legitimately saves — never an
    auto-write (the over-eager persist was the prior attempt's corruption). Task FILES
    (PLAN.md, archive) are never rewritten by this."""
    if not isinstance(state, dict):
        return state
    tasks = state.get("tasks")
    if not isinstance(tasks, dict):
        return state
    for rec in tasks.values():
        if isinstance(rec, dict) and rec.get("phase") in LEGACY_PHASES:
            rec["phase"] = LEGACY_PHASES[rec["phase"]]
    return state


def load_state(root: Path) -> dict:
    """Load + parse state.json, failing CLOSED. A git-conflicted file dies with a merge-specific
    'state_conflicted'; any other corrupt/unreadable file dies with a clean 'state_invalid'
    message (never a raw traceback), so every command that loads state degrades gracefully
    (design-for-failure). The parsed state is forward-migrated to the multi-active schema and
    its legacy phase tokens are normalized (ground->specify, contract->plan)."""
    try:
        return _normalize_phase_tokens(_migrate_state(json.loads(_state_text_or_die(root))))
    except (json.JSONDecodeError, OSError) as e:
        _die(f"state_invalid: {root / STATE_FILE} is corrupt or unreadable "
             f"({e.__class__.__name__}) — restore it from git or a backup")


def save_state(root: Path, state: dict) -> None:
    state["updated"] = _now()
    try:
        _atomic_write(root / STATE_FILE, json.dumps(state, indent=2) + "\n")
    except OSError as e:
        # Fail CLOSED like load_state: a named, recoverable error — never a raw traceback. The
        # atomic temp+replace leaves the prior state.json byte-unchanged, so it is safe to retry.
        _die(f"state_write_failed: could not write {root / STATE_FILE} "
             f"({e.__class__.__name__}) — the prior state.json is intact; "
             "free disk / fix permissions and re-run")


def _templates_dir() -> Path:
    return Path(__file__).resolve().parent / "templates"


def _render_template(name: str, **subs: str) -> str:
    """Load templates/<name>.tmpl and substitute {{key}} tokens.

    Falls back to a built-in minimal template for PLAN.md (template-unify: the fast
    lane is a derived render of that same template, never a second file).
    """
    tmpl = _templates_dir() / f"{name}.tmpl"
    _fallbacks = {"PLAN.md": _FALLBACK_TASK}
    if tmpl.exists():
        text = tmpl.read_text(encoding="utf-8")
    elif name in _fallbacks:
        text = _fallbacks[name].replace("{title}", "{{title}}").replace(
            "{slug}", "{{slug}}").replace("{date}", "{{date}}").replace("{stage}", "{{stage}}")
    else:
        text = ""
    for key, val in subs.items():
        text = text.replace("{{" + key + "}}", val)
    return text


def _seed_spec_file(root: Path, dd: str, *, project: str, stage: str,
                    date_str: str) -> Path:
    """specs-5dd: seed ONE 5-DD spec file under .add/specs/ — never clobber, never
    write blank (the SETUP_FILES survivor idiom). Returns the file's path either
    way so callers (init AND delta-append's on-demand legacy path) share one
    seeding truth instead of two drifting copies."""
    fname, title, lens = SPEC_DDS[dd]
    dest = root / "specs" / fname
    if dest.exists():
        return dest
    rendered = _render_template(
        "specs/SPEC.md", dd=dd.upper(), dd_lower=dd, title=title, lens=lens,
        project=project, stage=stage, date=date_str)
    if not rendered.strip():
        # missing/stale template — skip rather than seed a 0-content survivor
        # (same circuit breaker as the SETUP_FILES loop)
        print(f"add: warning: template for specs/{fname} is missing/blank — skipped",
              file=sys.stderr)
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(dest, rendered)
    return dest


# atomic-node: the ONE template IS the lean render — every lane distinction
# (--fast/--oneshot/--thin scaffolds) retired with the fat sections themselves;
# the AI-verify record block ships in the template (no splice), so an agent-crossed
# freeze (`gate_mode: ai-plan-verify`, declared in the header) finds its checklist.


# --- PLAN.md milestone backlink (task-milestone-backlink) --------------------
# The task↔milestone link is mirrored into the PLAN.md header so the file names its
# own parent. The engine WRITES it (new-task) and MAINTAINS it (set-milestone); a
# milestone-free task reads the "(none)" sentinel, never blank. Keeping it engine-owned
# is what makes it drift-proof — `check` flags a hand-edited line that disagrees.
_MILESTONE_BACKLINK = "(none)"
_MILESTONE_LINE_RE = re.compile(r"(?m)^milestone:[^\n]*$")
_SLUG_LINE_RE = re.compile(r"(?m)^slug:[^\n]*$")


def _milestone_backlink_value(milestone) -> str:
    """The header value for a milestone slug (or the sentinel when milestone-free)."""
    return milestone if milestone else _MILESTONE_BACKLINK


def _set_milestone_line(text: str, value: str) -> str:
    """Rewrite (or insert) the PLAN.md header `milestone:` backlink — idempotent.

    A grandfathered file lacking the line gets it inserted right after `slug:`; with no
    slug line either, the text is returned unchanged (degrade-safe — never corrupts a doc).
    """
    line = f"milestone: {value}"
    if _MILESTONE_LINE_RE.search(text):
        return _MILESTONE_LINE_RE.sub(lambda _m: line, text, count=1)
    m = _SLUG_LINE_RE.search(text)
    if not m:
        return text
    return text[:m.end()] + "\n" + line + text[m.end():]


def _read_milestone_line(text: str):
    """The current `milestone:` backlink value in a PLAN.md header, or None if absent."""
    m = _MILESTONE_LINE_RE.search(text)
    return m.group(0)[len("milestone:"):].strip() if m else None


# kernel-trim (ADD 2.0 M5): the MILESTONE.md release-backlink stamp died with cmd_release.




# --- §0 GROUND drift anchor (ground-anchor-sha) -----------------------------
# §0 line numbers rot during BUILD while symbols survive (PR40 audit). The engine SEEDS a
# `Ground SHA:` field (the AI fills it via git — NO-EXEC: add.py never shells out) and `check`
# WARNs when a §0 cites bare line numbers without one, so drift is detectable not silent.
_GROUND_SHA_RE = re.compile(r"(?m)^Ground SHA:[ \t]*(.*?)[ \t]*$")
_LINE_REF_RE = re.compile(r"l\.\d+")


def _ground_section(text: str) -> str:
    """The grounding block of a PLAN.md — the §3 PLAN `### Grounding` sub-block, from the
    `### Grounding` heading to the next `### ` / `## ` heading (expectations-first: grounding
    moved from a standalone §0 into the plan phase). Legacy `## 0 GROUND` still resolves."""
    m = re.search(r"(?m)^### Grounding\b", text) or re.search(r"(?m)^## 0\b", text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"(?m)^(?:### |## )", rest)
    return rest[:nxt.start()] if nxt else rest


def _read_ground_sha(text: str):
    """The §0 `Ground SHA:` value, or None if absent or still a `<…>` placeholder."""
    m = _GROUND_SHA_RE.search(_ground_section(text))
    if not m:
        return None
    val = m.group(1).strip()
    return None if (not val or val.startswith("<")) else val


def _ground_cites_line_ref(text: str) -> bool:
    """True iff the §0 GROUND block cites a bare line number (the `l.NNN` idiom)."""
    return bool(_LINE_REF_RE.search(_ground_section(text)))


def _seeded_delta_pointers(text: str) -> list[str]:
    """The task slugs `[SPEC · seeded] … [→ <slug>]` lines point at (delta-task-backlink). PURE.

    Walks the delta→task lineage backward: each seeded SPEC delta carries the slug it was seeded
    into (the `[→ <slug>]` stamp `_resolve_spec_delta` appends). `check` flags a pointer that no
    longer resolves to a live or archived task. Order-preserving; open/dropped deltas are ignored."""
    out: list[str] = []
    for ln in text.splitlines():
        m = _SPEC_DELTA_RE.match(ln.rstrip("\n"))
        if not m or m.group(2) != "seeded":
            continue
        p = _SEED_POINTER_RE.search(m.group(3))
        if p:
            out.append(p.group(1))
    return out


def _signals(root: Path) -> list[dict]:
    """signal-model: project the three split observation primitives — todos
    (state["todos"]), SPEC deltas and competency deltas (each task's §7) — into ONE
    unified signal node list. A signal is {id, kind, text, status, edges}: status
    rides the closed lifecycle {advisory, captured, evidenced, resolving, resolved,
    dropped}; edges are (rel, target_slug) with rel in {observed-by, resolves-into,
    blocks}. PURE projection — reads only, adds NO store, rewrites nothing (the graph
    is a VIEW, not a table). Backward-reading: every pre-existing todo/delta maps to a
    status; a malformed line or corrupt entry is SKIPPED, never raised."""
    try:
        state = load_state(root)
    except Exception:
        return []
    out: list[dict] = []
    # todos — state["todos"] {id, text, status: open|done}
    for t in (state.get("todos") or []):
        if not isinstance(t, dict) or "id" not in t:
            continue
        status = {"open": "captured", "done": "resolved"}.get(t.get("status"))
        if status is None:
            continue
        out.append({"id": f"t{t['id']}", "kind": "todo", "text": t.get("text") or "",
                    "status": status, "edges": []})
    # §7 deltas per task — SPEC (open|seeded|dropped|carried) + competency (open|folded|rejected)
    for slug in sorted(state.get("tasks") or {}):
        body = _raw_phase_bodies(root, slug).get(7, "")
        s_n = c_n = 0
        for raw in body.splitlines():
            line = raw.rstrip("\n")
            ms = _SPEC_DELTA_RE.match(line)
            if ms:
                st, text = ms.group(2), ms.group(3)
                edges: list = [("observed-by", slug)]
                if st == "open":
                    status = "evidenced" if _EVIDENCE_RE.match(text) else "captured"
                elif st == "carried":            # still open, carried forward
                    status = "captured"
                elif st == "seeded":
                    status = "resolving"
                    p = _SEED_POINTER_RE.search(text)
                    if p:
                        edges.append(("resolves-into", p.group(1)))
                elif st == "dropped":
                    status = "dropped"
                else:
                    continue
                s_n += 1
                out.append({"id": f"s:{slug}:{s_n}", "kind": "spec-delta",
                            "text": text, "status": status, "edges": edges})
                continue
            mc = _DELTA_RE.match(line)
            if mc:
                status = {"open": "evidenced", "folded": "resolved",
                          "rejected": "dropped"}.get(mc.group(2))
                if status is None:
                    continue
                c_n += 1
                out.append({"id": f"c:{slug}:{c_n}", "kind": "competency-delta",
                            "text": mc.group(3), "status": status,
                            "edges": [("observed-by", slug)]})
    return out


_EXIT_CRITERION_RE = re.compile(r"^\s*- \[([ x])\]\s+(.*)$")
_DELIVERED_BY_RE = re.compile(r"\(←\s*([A-Za-z0-9][A-Za-z0-9_-]*)\s*\)")


def _exit_criterion_nodes(root: Path) -> list[dict]:
    """exit-criterion-nodes: project every milestone's `## Exit criteria` section into
    delivered-by signal nodes — one dict per criterion {ms, idx, text, met, delivered_by}.
    `met` is the `[x]` box; `delivered_by` is the `(← <slug>)` pointer (None if absent).
    PURE read of each MILESTONE.md (never state, never a store); a missing file/section
    contributes nothing (fail-soft) — mirrors _exit_criteria, ADDITIVE beside it."""
    try:
        state = load_state(root)
    except Exception:
        return []
    out: list[dict] = []
    for mslug in sorted(state.get("milestones") or {}):
        f = root / "milestones" / mslug / MILESTONE_FILE
        if not f.exists():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        m = re.search(r"## Exit criteria.*?(?=\n## |\Z)", text, re.S)
        if not m:
            continue
        idx = 0
        for line in m.group(0).splitlines():
            cm = _EXIT_CRITERION_RE.match(line)
            if not cm:
                continue
            idx += 1
            body = cm.group(2)
            p = _DELIVERED_BY_RE.search(body)
            out.append({"ms": mslug, "idx": idx, "text": body,
                        "met": cm.group(1) == "x",
                        "delivered_by": p.group(1) if p else None})
    return out


_NUMBERED_BOLD_RE = re.compile(r"(?m)^\s*\d+\.\s+\*\*(.+?)\*\*")
_PARTS_MARKER_RE = re.compile(r"\(\s*(\d+)\s+parts?\s*\)|(\d+)-part", re.I)
_CATCHALL_KW_RE = re.compile(r"longtail|drain|sweep|catch-all|grab-bag", re.I)


def _scope_parts(root: Path, slug: str) -> list[str]:
    """atomicity-signal: PURE read of a task's §1/§3 body — return the ordered
    independent-Part labels a scope enumerates. A junk-drawer / longtail / drain
    catch-all reads as N>1 Parts; a normal atomic task reads as [] (silence = pass).
    Signals (union, order-preserving, deduped): a numbered-bold list `N. **label**` ·
    a `(N parts)` / `N-part` marker (N>=2) · a catch-all keyword in the slug or title.
    Returns [] when fewer than 2 Parts — never raises (fail-soft on a missing task)."""
    try:
        bodies = _raw_phase_bodies(root, slug)
    except Exception:
        return []
    body = (bodies.get(1, "") + "\n" + bodies.get(3, ""))
    try:
        state = load_state(root)
        title = ((state.get("tasks") or {}).get(slug) or {}).get("title", "") or ""
    except Exception:
        title = ""
    parts: list[str] = []
    for m in _NUMBERED_BOLD_RE.finditer(body):
        label = m.group(1).strip()
        if label and label not in parts:
            parts.append(label)
    if len(parts) < 2:                       # no explicit bold list — try the marker
        mk = _PARTS_MARKER_RE.search(body)
        if mk:
            n = int(mk.group(1) or mk.group(2) or 0)
            if n >= 2:
                parts = [f"part {i}" for i in range(1, n + 1)]
    if len(parts) < 2 and _CATCHALL_KW_RE.search(f"{slug} {title}"):
        parts = ["catch-all", "drain"]       # keyword fires the nudge (recall over a named list)
    return parts if len(parts) >= 2 else []


def _atomicity_signal_seed(root: Path, slug: str):
    """atomicity-signal: when a task's scope reads as >1 independent Part, SEED a
    persistent `captured` signal (a todo in state["todos"], the store _signals already
    projects) instead of an ephemeral print — so the atomicity concern survives after
    the freeze scrolls away and appears in `graph --signals`. Idempotent per slug (a
    re-freeze adds no duplicate); returns the new todo id, or None when <2 Parts /
    already seeded. Writes ONLY the existing todo store — no new store (thin-engine floor).
    Measure-not-block: the freeze caller wraps this fail-open; it never gates a freeze."""
    parts = _scope_parts(root, slug)
    if len(parts) < 2:
        return None
    state = load_state(root)
    todos = state.get("todos")
    if not isinstance(todos, list):
        todos = state["todos"] = []
    tag = f"atomicity: {slug} —"
    for t in todos:
        if isinstance(t, dict) and t.get("status") == "open" \
                and str(t.get("text", "")).startswith(tag):
            return None                      # idempotent — already seeded for this slug
    new_id = max((t.get("id", 0) for t in todos if isinstance(t, dict)), default=0) + 1
    text = (f"{tag} §3 scope reads as {len(parts)} Parts ({', '.join(parts)}); "
            f"consider new-milestone + one task per Part.")
    todos.append({"id": new_id, "text": text, "created": _now(), "status": "open"})
    save_state(root, state)
    print(f"note: seeded atomicity signal #{new_id} — §3 scope reads as {len(parts)} "
          f"Parts (addressable after this freeze)")
    return new_id


# --- tidy a closed PLAN.md (strip-scaffold-at-done) --------------------------
# A live PLAN.md carries `<!-- … -->` instruction comments that guide the active phase; once the
# task is `done` they are dead weight (PR40 audit). cmd_gate strips them on a COMPLETING gate.
# Content-safe: fenced code blocks (```…```, incl. the frozen §3) pass through BYTE-EXACT — only
# comments OUTSIDE a fence are removed; idempotent.
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_TRAILING_WS_RE = re.compile(r"(?m)[ \t]+$")
_BLANK_RUN_RE = re.compile(r"\n{3,}")


def _strip_live_scaffold(text: str) -> str:
    """Remove `<!-- … -->` instruction comments from a PLAN.md — fences untouched, idempotent.

    Splits on fenced code blocks AND an inline single-backtick span that IS itself a whole
    `` `<!--...-->` `` (literal comment syntax quoted as an example in prose) so neither is
    touched; a live comment that merely CONTAINS unrelated backtick-quoted code (e.g. this very
    template's own `` `add.py autonomy set` ``-style asides) is untouched by this exception and
    still stripped whole, exactly as before. In the remaining segments it drops comment spans,
    trims the trailing whitespace a removal leaves on a line, and collapses 3+ consecutive
    newlines to one blank line."""
    segs = re.split(r"(```.*?```|`<!--.*?-->`)", text, flags=re.DOTALL)
    for i in range(0, len(segs), 2):                     # even indices = OUTSIDE any fence
        s = _HTML_COMMENT_RE.sub("", segs[i])
        s = _TRAILING_WS_RE.sub("", s)
        segs[i] = _BLANK_RUN_RE.sub("\n\n", s)
    return "".join(segs)


def _contract_fingerprint(raw3: str) -> str:
    """md5 of the §3 CONTRACT CONTENT — comment-normalized + outer-whitespace-canonical (the
    instruction comment is scaffolding, not contract). Used on BOTH tamper-guard sides
    (_tripwire_snapshot + _tripwire_divergence) so the at-done strip — which removes the §3
    comment and shifts the section's boundary whitespace — never reads as `contract_tampered`,
    while a real fenced-shape edit still does."""
    return _md5_text(_strip_live_scaffold(raw3).strip())

# --- state/markdown predicates (moved to add_engine/predicates.py) -----------
from add_engine.predicates import (
    _phase_owner, _phase_bundle, _setup_locked, _milestone_confirmed, _section_unfilled,
    _task_done, _persona_missing, _persona_quality_warnings, _persona_slug_valid, _rule_coverage_gaps,
    _ai_freeze_allowed, _skip_lane_eligible, _skip_set_allowed,
)

# --- git-native identity/actor seam (moved to add_engine/identity.py) --------
from add_engine import identity            # qualified calls: identity._whoami(...)
from add_engine.identity import (          # re-exported for `add.<name>` attr compat
    _git_config, _os_user, _whoami, _actor_stamp,
    _render_actor_line, _parse_actor_arg, _actor_matches,
)




# A git conflict marker BEGINS a line with 7 of `<`, `=`, or `>` (`(?m)^…`). An unresolved
# merge writes these into state.json, making it invalid JSON; the line-anchor keeps a
# legitimate value (always on an INDENTED JSON line) from false-tripping the guard.


def _stamp_gate_record(root: Path, state: dict, slug: str, outcome: str) -> None:
    """Write-back (gate-record-writeback): mirror the resolved gate verdict into the task's
    §6 `### GATE RECORD`, so the file and state.json never silently diverge (Finding C). Runs
    for EVERY task — the write is ADDITIVE and never refuses, so (unlike the two refusal gates)
    it needs no `--await-confirm` opt-in to protect the census. GRANDFATHER is the safety: a
    GATE RECORD line is rewritten ONLY while it still holds a `<…>` placeholder; a resolved
    (hand-filled) line is byte-untouched. No GATE RECORD block / no placeholder line / an
    unreadable file -> silent no-op, the file stays byte-identical. Called AFTER save_state —
    state is the source of truth; the file only mirrors it, so a write fault never loses a verdict."""
    f = root / "tasks" / slug / "PLAN.md"
    try:
        text = f.read_text(encoding="utf-8")
    except OSError:
        return                                   # unreadable -> no-op (never blocks the gate)
    if "### GATE RECORD" not in text:
        return                                   # nothing to mirror into
    actor = identity._actor_stamp(state)
    today = date.today().isoformat()
    # each rule matches ONLY a line still carrying a `<…>` placeholder -> grandfather a resolved line.
    rules = [
        (r"(?m)^(Outcome:[ \t]*)<[^>\n]*>.*$", f"Outcome: {outcome}"),
        (r"(?m)^Reviewed by:[ \t]*.*<[^>\n]*>.*$",
         f"Reviewed by: {actor['name']} · date: {today}"),
    ]
    if outcome == "RISK-ACCEPTED":
        w = ((state.get("tasks") or {}).get(slug) or {}).get("waiver") or {}
        rules.append((r"(?m)^If RISK-ACCEPTED ->.*<[^>\n]*>.*$",
                      f"If RISK-ACCEPTED -> owner: {w.get('owner', '?')} · "
                      f"ticket: {w.get('ticket', '?')} · expires: {w.get('expires', '?')}"))
    new = text
    for pat, repl in rules:
        new = re.sub(pat, repl, new, count=1)
    if new != text:                              # no-op = no write (mtime stable)
        _atomic_write(f, new)


def _capture_wrapped(label: str, body: str):
    """Capture a `<label>: value` field that may WRAP onto continuation lines (a human writing
    prose in a PLAN.md field routinely wraps past one line). Matches the label's first line, then
    consumes subsequent physical lines while each is non-blank AND does not itself start a new
    field label — `Word Word:` or `Word Word (parenthetical):` (the real template places labels
    like `Safety rule (feature-specific):`/`Persona (optional):` immediately after a wrapped field
    with no blank line; a parenthetical-blind boundary would silently swallow them) — so a wrapped
    value is captured in full without ever bleeding into the next field or past a blank-line
    paragraph break. Returns None if the label is absent, matching the single-line behavior it
    replaces."""
    m = re.search(rf"(?m)^{re.escape(label)}:[ \t]*(.+)$", body)
    if not m:
        return None
    lines = [m.group(1).strip()]
    rest = body[m.end():].split("\n")[1:]
    for line in rest:
        if not line.strip() or re.match(r"^[A-Z][A-Za-z ]*(\([^)]*\))?[ \t]*:", line):
            break
        lines.append(line.strip())
    return " ".join(lines)


def _stamp_adr_record(root: Path, state: dict, slug: str) -> None:
    """Write-back (adr-at-observe): HARVEST a §7 `### Decisions (ADR)` block from the actor-stamps
    ALREADY in the task — §1 framing (AI) · §3 freeze (human) · §5 strategy-actually-used (AI) · §6
    gate (human|AI by autonomy). HARVEST-not-author: every rendered line is sourced from an existing
    stamp; the engine invents no decision content (NO-EXEC). GRANDFATHER like _stamp_gate_record:
    fills ONLY while the block still holds its `<harvested…>` placeholder line; a resolved/absent
    block or an unreadable file -> a byte-identical no-op (legacy + fast tasks untouched). NEVER
    raises: any per-source parse fault renders "<unrecorded>". Called from cmd_gate AFTER
    _stamp_gate_record (so §6 is already mirrored) and AFTER save_state (state is the source of
    truth; the file only mirrors it, so a write fault never loses the verdict).

    §7-OBSERVE-scoped (INV-7): the placeholder is matched ONLY inside the "## 7 · OBSERVE" section,
    so a "<harvested at done…>" line elsewhere — e.g. a §3 contract that ILLUSTRATES this very
    feature — is never touched (a file-wide first-match would corrupt the frozen contract; caught
    by dogfooding adr-harvest on itself)."""
    f = root / "tasks" / slug / "PLAN.md"
    try:
        text = f.read_text(encoding="utf-8")
    except OSError:
        return                                   # unreadable -> no-op
    sec7 = re.search(r"(?ms)^## 7 · OBSERVE\b.*?(?=\n## \d+ ·|\Z)", text)
    if not sec7:
        return                                   # no §7 OBSERVE (fast / legacy) -> no-op
    m = re.search(r"(?m)^<harvested at done[^\n]*>$", sec7.group(0))
    if not m:
        return                                   # resolved (hand-edited) or absent -> grandfather no-op
    ph_start, ph_end = sec7.start() + m.start(), sec7.start() + m.end()
    UN = "<unrecorded>"
    bodies = _raw_phase_bodies(root, slug)

    def _framing():                              # §1 -> [AI]: chosen + rejected
        try:
            val = _capture_wrapped("Framings weighed", bodies.get(1, ""))
            if val is None:
                return UN, ""
            chosen, rejected = UN, []
            for p in (s.strip() for s in val.split("·") if s.strip()):
                cm = re.match(r"(.*?)\s*\(chosen\b.*\)\s*$", p)  # "(chosen)" OR "(chosen — rationale)"
                if cm:
                    chosen = cm.group(1).strip() or UN
                else:
                    rejected.append(p)
            # an UNFILLED §1 is a "<chosen>" placeholder token — degrade to <unrecorded>, but a
            # real framing that merely CONTAINS a "<" (e.g. quoting a type) is kept (faithful capture)
            if chosen is UN or chosen.startswith("<"):
                return UN, ""
            return chosen, " · ".join(rejected)
        except Exception:
            return UN, ""

    def _freeze():                               # §3 -> [human]: "FROZEN @ vN — approved by NAME"
        try:
            m = re.search(r"(?m)^.*FROZEN @ (v\d+).*?approved by ([^\n<]+?)\s*$", bodies.get(3, ""))
            if m:
                return m.group(1), m.group(2).strip()
        except Exception:
            pass
        t = ((state.get("tasks") or {}).get(slug) or {})
        fr = t.get("freeze") or {}
        ver = fr.get("version") or t.get("contract_version")
        return (f"v{ver}" if ver else UN), (fr.get("by") or fr.get("actor") or UN)

    def _strategy():                             # §5 -> [AI]: the value, default "as planned"
        try:
            val = _capture_wrapped("Strategy actually used", bodies.get(5, ""))
            if val:
                # UNFILLED is the "<fill at …>" template token; a real value may legitimately
                # contain "<" (quoting `<tag>`, "x < y") and must NOT degrade to the default
                if not val.startswith("<fill"):
                    return val
        except Exception:
            pass
        return "as planned"

    # §3 Build-strategy facets (facet-adr-harvest): each FILLED facet earns its own [AI] build
    # line, in this order, directly before the strategy-used line. Harvest reads bodies[3]
    # ONLY (the facets moved from §5 into §3's ### Build-strategy sub-block with plan-phase-core;
    # never another section); a LEADING "<" is the template placeholder and stays silent per
    # facet — zero filled facets collapse to the legacy 4-line block exactly.
    _FACETS = (("Approach (domain strategy)", "approach"), ("Data strategy", "data strategy"),
               ("Pattern", "pattern"), ("Optimization stance", "optimization stance"))

    def _facets():                               # §3 Build-strategy -> [AI]: one (key, value) per FILLED facet
        out = []
        try:
            for label, key in _FACETS:
                val = _capture_wrapped(label, bodies.get(3, ""))
                if val and not val.startswith("<"):
                    out.append((key, val))
        except Exception:
            return []
        return out

    def _gate():                                 # §6 -> [human|AI]: outcome + reviewer
        try:
            mo = re.search(r"(?m)^Outcome:[ \t]*(\S+)", bodies.get(6, ""))
            outcome = mo.group(1) if mo else (((state.get("tasks") or {}).get(slug) or {}).get("gate") or UN)
            mr = re.search(r"(?m)^Reviewed by:[ \t]*([^·\n<]+)", bodies.get(6, ""))
            rev = mr.group(1).strip() if mr else UN
        except Exception:
            outcome, rev = UN, UN
        am = re.search(r"(?m)^autonomy:[ \t]*(\w+)", text)
        actor = "AI" if (am and am.group(1) == "auto") else "human"
        return outcome, rev, actor

    try:
        chosen, rejected = _framing()
        fver, fby = _freeze()
        facets = _facets()
        strat = _strategy()
        outcome, rev, gate_actor = _gate()
    except Exception:
        return                                   # never block the gate
    rej = f"; rejected {rejected}" if rejected else ""
    lines = [
        f"- [AI] specify — chose {chosen}{rej}",
        f"- [human] freeze — froze §3 @ {fver} (approved by {fby})",
        *(f"- [AI] build — {key}: {val}" for key, val in facets),
        f"- [AI] build — strategy used: {strat}",
        f"- [{gate_actor}] verify — gate {outcome} (reviewed by {rev})",
    ]
    new = text[:ph_start] + "\n".join(lines) + text[ph_end:]
    if new != text:
        _atomic_write(f, new)


# --- guidelines / CLAUDE.md-injection subsystem (moved to add_engine/guidelines.py) -
from add_engine.guidelines import (
    _guideline_block, _inject_block, _inject_guidelines, _inject_specs_pointers, _is_brownfield,
)
def cmd_init(args: argparse.Namespace) -> None:
    base = Path(args.dir).resolve()
    root = base / ROOT_DIRNAME
    state_path = root / STATE_FILE
    if state_path.exists() and not args.force:
        # idempotent init (init-idempotent-nudge): a re-init is a LOUD NO-OP, not a
        # refusal — exit 0 so a second init costs the agent no recovery call, and
        # write NOTHING (return before any seed). --force still resets (falls
        # through below). The message still names the resume command.
        msg = f"already initialised at {root} — resume: add.py status"
        try:
            _active = _active_task(load_state(root))
            if _active:
                msg += f" (active task: {_active})"
        except Exception:
            pass
        print(f"add: {msg}")
        return

    (root / "tasks").mkdir(parents=True, exist_ok=True)
    # Keep the engine's transient local artifacts out of git. Never-clobber: a
    # human may have customised .add/.gitignore, so an existing one is left as-is
    # (mirrors the SETUP_FILES skip-not-clobber idiom). Writes ONLY this file — no
    # scope-snapshot.json or .bak is created, deleted, or modified.
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        _atomic_write(gitignore, _GITIGNORE_BODY)
    today = date.today().isoformat()
    proj_name = args.name or base.name

    # survivor-layer files — never clobber an existing one, never write a blank one.
    # Remember whether PROJECT.md pre-existed: a --force reinit resets state but must NOT
    # touch a hand-edited survivor, so the specs-pointer wiring below fires ONLY when this
    # init actually scaffolds PROJECT.md fresh (a pre-existing one is retrofitted via `migrate`).
    _project_md_existed = (root / "PROJECT.md").exists()
    for fname in SETUP_FILES:
        dest = root / fname
        if dest.exists():
            continue
        rendered = _render_template(fname, date=today, project=proj_name, stage=args.stage)
        if not rendered.strip():
            # A missing/stale template rendered to nothing. Skip rather than create
            # a 0-content survivor file (design-for-failure; circuit breaker so an
            # upgrade with a stale templates/ dir can't silently produce empty docs).
            print(f"add: warning: template for {fname} is missing/blank — skipped",
                  file=sys.stderr)
            continue
        _atomic_write(dest, rendered)

    # persona-skill: personas are AUTHORED via the persona-author skill (not seeded from a
    # template) — but the location must exist so the first authored persona has a home and the
    # unseeded nudge has a directory to check. Create it empty; the skill fills it.
    (root / "personas").mkdir(parents=True, exist_ok=True)

    # specs-5dd (ADD 2.0 M3): the five living 5-DD specs — same survivor idiom as
    # SETUP_FILES (never clobber, never write blank), ONE template rendered five ways.
    for dd in SPEC_DDS:
        _seed_spec_file(root, dd, project=proj_name, stage=args.stage, date_str=today)

    # foundation-specs-refs: wire the freshly-scaffolded PROJECT.md's thin index to the five
    # specs just seeded (a managed, SPEC_DDS-driven ADD:SPECS block). Guarded on freshness so a
    # --force reinit never mutates a hand-edited survivor — that retrofit is `migrate`'s job.
    if not _project_md_existed:
        _inject_specs_pointers(root / "PROJECT.md")

    # --run-mode: seed the autonomy dial into PROJECT.md. Run mode IS the autonomy posture;
    # concurrency is a per-task subagent (doc-level), never an engine-managed streams line.
    # ONLY when the flag is explicitly set — absent flag leaves PROJECT.md byte-identical.
    run_mode = getattr(args, "run_mode", None)
    if run_mode is not None:
        _level = run_mode                                           # "auto" | "conservative"
        proj_md = root / "PROJECT.md"
        if proj_md.exists():
            _text = proj_md.read_text(encoding="utf-8")
            _text = _autonomy_decl_line(_text, _level)
            _atomic_write(proj_md, _text)

    state = {
        "project": proj_name,
        "stage": args.stage,
        "active_task": None,
        "active_milestone": None,
        "active_milestones": [],
        "active_tasks": {},
        "tasks": {},
        "milestones": {},
        "created": _now(),
        "updated": _now(),
    }
    if getattr(args, "await_lock", False):
        # opt-in: seed an UNLOCKED setup so the build-boundary gate is active until
        # `add.py lock`. Plain init omits this key entirely (grandfathered-locked).
        state["setup"] = {"locked": False, "locked_at": None, "locked_by": None, "layers": []}
    save_state(root, state)
    # zero-config: give any agent a stable pointer into the ADD runtime.
    for name, action in _inject_guidelines(base):
        if action != "unchanged":
            print(f"{action:>9}  {name}")
    print(f"initialised ADD project '{state['project']}' (stage: {state['stage']}) at {root}")
    if _is_brownfield(base):
        # Existing code present — the AI maps it SILENTLY into the survivors (skill/add/adopt.md),
        # then the human locks it down. The engine only flags it; it never reads or fills the code.
        print("brownfield: existing code detected — the `add` skill maps it into your")
        print("            foundation (silent), then you lock it down: add.py lock")
    else:
        print("next: open Claude Code, run `/add`, and say what you want to build —")
        print("      the `add` skill sizes it into a milestone and drives the build with you.")
        # status-guide-fold: name the exact CLI ceremony command for a HEADLESS run
        # (no skill available) so the agent never reads `new-milestone --help`.
        # kickoff-truth M1: the single-task lane leads here too — this hint prints
        # BEFORE the kickoff block, so a milestone-first line here would re-arm the
        # measured bait the kickoff reorder kills.
        print('      or headless, single task: add.py new-task <slug> --title "..." '
              '(declare `gate_mode: ai-plan-verify` in the PLAN.md header for an agent-crossed freeze)')
        print('      or headless, multi-task:  add.py new-milestone <slug> --title "..." --goal "..."')
    # setup hygiene (both branches): the .add/ folder IS the shared project state — commit it
    # so the team shares one source of truth; its transient working files are already gitignored.
    print("tip:  commit the .add/ folder to git so your team shares the ADD state "
          "(its transient files are already .gitignored).")
    # first-call-ergonomics M3: a copy-pasteable, flags-included kickoff hand-off so a
    # headless agent reaches the 3-call walk from init's OWN stdout — zero `--help`
    # reads needed for the ceremony the skill would otherwise narrate.
    # kickoff-truth M1: the single-task lane leads — the cheapest measured benchmark
    # run skipped the milestone entirely; the milestone lines serve multi-task work.
    print("kickoff (single task):")
    print('  add.py new-task <slug> --title "..."')
    print("kickoff (multi-task milestone):")
    print('  add.py new-milestone <slug> --title "..." --goal "..."')
    print('  add.py new-task <slug> --title "..." --milestone <ms>')
    print("then either way (the 3-call walk — phase-collapse-3):")
    print("  add.py freeze --by <name> --cross   (after drafting §1–§4)  ·  add.py gate PASS")


def cmd_sync_guidelines(args: argparse.Namespace) -> None:
    project_root = _require_root().parent
    for name, action in _inject_guidelines(project_root):
        print(f"{action:>9}  {name}")


def cmd_new_task(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    # build-boundary gate: pre-lock, EXACTLY one first task may be drafted; refuse a 2nd.
    if not _setup_locked(state) and state.get("tasks"):
        _die("setup_unlocked: lock the foundation first — add.py lock")
    slug = args.slug
    if not slug.replace("-", "").replace("_", "").isalnum():
        _die("slug must be alphanumeric with - or _ only")
    tdir = root / "tasks" / slug
    task_md = tdir / "PLAN.md"
    if task_md.exists() and not args.force:
        _die(f"task '{slug}' already exists (use --force to overwrite PLAN.md)")

    # link to a milestone (explicit, or the active one) — validate before any write
    milestone = getattr(args, "milestone", None) or _active_milestone(state)
    if milestone and milestone not in state.get("milestones", {}):
        _die("unknown_milestone")
    # confirm-parent gate (OPT-IN): a task may not be detailed before its parent milestone is
    # human-confirmed — but ONLY when the milestone opted in via `new-milestone --await-confirm`.
    # validate-then-write — refuse BEFORE any scaffold/state mutation. A milestone with no
    # `confirmed` key (non-flag + pre-existing) is grandfathered (mirrors the setup-lock).
    if milestone and not _milestone_confirmed(state, milestone):
        _die(f"milestone_unconfirmed: confirm it first — add.py milestone-confirm {milestone}")
    depends_on = _parse_deps(getattr(args, "depends_on", None))
    # edge-truth inherit: no explicit edge -> the milestone's compiled plan is the truth.
    # Verbatim, creation-order-proof (a dangling forward edge is check's warn, never lost).
    if not depends_on and milestone:
        depends_on = list((state["milestones"][milestone].get("planned") or {}).get(slug) or [])
    # relations-surface: two NON-BLOCKING sibling relations, parsed exactly like depends_on
    # (comma-separated slugs). They never gate the wave schedule — legibility + validate only.
    extends = _parse_deps(getattr(args, "extends", None))
    relates_to = _parse_deps(getattr(args, "relates_to", None))

    # SEED (--from-delta): resolve a prior task's FIRST open SPEC delta into THIS task.
    # validate-ALL-then-write — resolve the prior, read its open delta, and compute the
    # seeded flip NOW (before any write); the slug-free check above has already passed, so
    # the only writes below are the new PLAN.md, then the prior flip, then state.
    from_delta = getattr(args, "from_delta", None)
    match = getattr(args, "match", None)
    if match and not from_delta:                            # --match targets the PRIOR's delta
        _die("match_requires_from_delta: --match needs --from-delta <prior> (it selects the "
             "prior task's open SPEC delta to seed)")
    feature_override = prior_md = flipped_prior = None
    if from_delta:
        prior = _resolve_task(state, from_delta)            # unknown prior -> _die
        prior_md = root / "tasks" / prior / "PLAN.md"
        prior_text = prior_md.read_text(encoding="utf-8")
        status, idx, delta_text = _select_spec_delta(prior_text, match)
        if status == "no_open":
            _die(f"no_open_spec_delta: task '{prior}' has no open SPEC delta to seed")
        if status == "no_match":
            _die(f"no_matching_spec_delta: no open SPEC delta in '{prior}' matches --match '{match}'")
        if status == "ambiguous":
            _die(f"ambiguous_spec_match: --match '{match}' matches multiple open SPEC deltas in "
                 f"'{prior}' — narrow it")
        feature_override = f"{delta_text} (from {prior} spec-delta)"
        flipped_prior = _resolve_spec_delta(prior_text, "seeded", pointer=slug, line_index=idx)

    (tdir / "tests").mkdir(parents=True, exist_ok=True)
    (tdir / "src").mkdir(parents=True, exist_ok=True)
    title = args.title or slug.replace("-", " ").replace("_", " ").title()
    # inherit the project's DECLARED autonomy default (task init-auto-default) — fail-SAFE:
    # absent -> auto, garbled -> conservative; the posture is project-scoped, not hardcoded.
    autonomy = _project_autonomy(root)
    # atomic-node: ONE template for every task — the lean render IS the template
    # (lane scaffolds retired). The trust seams are template-borne: the AI-verify
    # record block ships in §3 (an agent-crossed freeze declares `gate_mode:
    # ai-plan-verify` in the header — _ai_freeze_allowed's floor is unchanged),
    # and the §3 Regression floor line makes the host suite an inherited edge.
    sensitivity = (getattr(args, "sensitivity", None) or "").strip().lower()
    rendered = _render_template(
        "PLAN.md",
        title=title, slug=slug, date=date.today().isoformat(),
        stage=state["stage"], autonomy=autonomy,
        milestone=_milestone_backlink_value(milestone))
    if feature_override:                                     # pre-fill §1 from the seeded delta
        rendered = re.sub(r"(?m)^Feature:.*$",
                          lambda _m: f"Feature: {feature_override}", rendered, count=1)
    # phase-collapse-3: the scaffold is born at `direction` (the whole front span). The
    # template's marker line is rewritten here so scaffold and state agree; template-unify
    # later re-words the template itself (this sub is then a no-op on an updated template).
    rendered = re.sub(r"(?m)^phase:\s*\S+(\s*<!--.*?-->)?\s*$",
                      "phase: direction   <!-- direction→build→verify→done; direction drafts "
                      "§1–§4 (rules · change plan · red suite) to the ONE freeze -->",
                      rendered, count=1)
    if from_delta:                                           # delta-task-backlink: §0 reverse link
        # pre-fill the §0 Related-intent PLACEHOLDER only (the `<…>` line a fresh full template
        # carries) — mirrors the §1 Feature pre-fill, gated by from_delta, count=1. The fast
        # template has no §0 Related-intent line, so the sub is a silent no-op there.
        _bl = f"Related intent: seeded from {prior} spec-delta — \"{delta_text}\" [← {prior}]"
        rendered = re.sub(r"(?m)^Related intent:\s*<.*>\s*$",
                          lambda _m: _bl, rendered, count=1)
    seed_writes: list[tuple[Path, str]] = [(task_md, rendered)]
    if flipped_prior is not None:                           # consume the source delta -> seeded
        seed_writes.append((prior_md, flipped_prior))
    _atomic_write_many(seed_writes)                         # new PLAN.md + consumed source as one commit
    if _project_autonomy_token(root) == "?":
        print("warning: garbled_project_autonomy — PROJECT.md declares an unrecognized "
              f"autonomy token; new task seeded fail-safe '{autonomy}' "
              "(fix it with `add.py autonomy set <level> --project`)", file=sys.stderr)

    # F8 (force-preserve-heal): a --force overwrite RE-CREATES the record; capture the prior
    # MONOTONIC heal counter first so it survives. Else a task that accrued heal attempts (or
    # was HARD-STOP escalated) could launder the cap (HEAL_CAP) to zero by re-creating itself —
    # a zero-human cap bypass (the same invariant _heal_or_escalate guards: "never auto-resets").
    prior_heal = state["tasks"].get(slug, {}).get("heal") if args.force else None
    # round-visible-runs: the round record is monotonic the same way — survives a --force re-create.
    prior_rounds = state["tasks"].get(slug, {}).get("rounds") if args.force else None
    state["tasks"][slug] = {
        "title": title,
        "phase": "direction",
        "gate": "none",
        "milestone": milestone,
        "depends_on": depends_on,
        "created": _now(),
        "updated": _now(),
    }
    # relations-surface: persist the non-blocking edges only when declared (absent == [] on read,
    # migration-tolerant like depends_on's `or []`) so old state stays byte-clean.
    if extends:
        state["tasks"][slug]["extends"] = extends
    if relates_to:
        state["tasks"][slug]["relates_to"] = relates_to
    if prior_heal is not None:
        state["tasks"][slug]["heal"] = prior_heal   # monotonic — survives the --force re-create
    if prior_rounds is not None:
        state["tasks"][slug]["rounds"] = prior_rounds   # same monotonic contract as heal
    if from_delta:
        state["tasks"][slug]["from_delta"] = from_delta     # lineage: seeded from <prior>
    if sensitivity:
        state["tasks"][slug]["sensitivity"] = sensitivity   # declared at creation (tiny-plan-small-scope)
    _set_active_task(state, slug, milestone)
    save_state(root, state)
    print(f"created task '{slug}' -> {task_md}")
    if milestone:
        print(f"linked to milestone '{milestone}'" +
              (f", depends-on {depends_on}" if depends_on else ""))
    else:
        # warn-never-block: the task is created (escape hatch), but nudge back toward the
        # intake -> milestone flow. Speaks of STRUCTURE (not attached), never the act.
        print(f"note: '{slug}' is not attached to a milestone — size it via /add (intake), "
              "or pass --milestone <id>")
    if from_delta:
        print(f"seeded from '{from_delta}' — its open SPEC delta is now "
              f"[SPEC · seeded] … [→ {slug}]; §1 Feature pre-filled.")
    print("active task set. phase: direction. Draft the whole Direction bundle top-to-bottom — "
          "§1 rules · §3 the change PLAN (ground + contract + what this task "
          "will do) · §4 red suite (cases live here, in TESTS & SCENARIOS) — then ONE "
          "freeze approval crosses it into build.")
    print(_next_footer(root, state))   # converges the old "then: add.py advance" hint
    # kickoff-truth M2: the remaining engine-call recipe at task birth — the transcript
    # audit measured 6-11 status/guide/--help re-orientation calls per run that this
    # block replaces. Lane-invariant (the freeze/gate floor is the same in every lane);
    # the agent scripts ahead instead of rediscovering.
    #
    # phase-collapse-3 (thin-engine-loop W2): W1's thin recipe is now THE recipe — every
    # lane walks new-task · freeze --cross · gate (3 calls). The full annotated form
    # teaches once at the project's first task; later tasks get the compact line
    # (recipe-dedup, engine-output-trim).
    if len(state.get("tasks") or {}) <= 1:
        print("recipe — this task's remaining engine calls:")
        print("  add.py freeze --by <name> --cross   [approval — freezes the Direction "
              "bundle (§1–§4: rules · change plan · red suite) and crosses "
              "straight to build]")
        print("  add.py gate PASS   (from build — crosses to verify and records the outcome)")
    else:
        print("recipe — remaining calls: add.py freeze --by <name> --cross · add.py gate PASS")












# a §3 still carrying this template placeholder is NOT a drafted contract yet
_CONTRACT_TEMPLATE_RE = re.compile(r"<METHOD>")


def _next_freeze_version(state: dict, slug: str) -> str:
    """v1 on the first freeze; N+1 of the highest prior freeze version recorded on the
    task's state record on a re-freeze (after a change request). PURE — reads state only."""
    prior = ((state.get("tasks") or {}).get(slug) or {}).get("freeze") or {}
    m = re.fullmatch(r"v(\d+)", str(prior.get("version", "")))
    return f"v{int(m.group(1)) + 1}" if m else "v1"


def _scope_echo(root: Path, slug: str) -> None:
    """scope-echo-draft: render the RESOLVED §3 scope declaration at the freeze — the
    approval already happening — so the scope-token grammar's silent mis-resolution
    class (three tasks independently rediscovered it; the shared-rules ledger has the
    full grammar) becomes a zero-call read. Pure read, propose-not-impose: when the declaration is UNDECLARED /
    garbage / entirely MISSING, a Scope line composed from §3 Touches paths is PRINTED,
    never written — the agent/human re-drafts and re-freezes deliberately."""
    resolved = _declared_scope(root, slug)
    rootp = root.parent

    def _touches_paths() -> list[str]:
        # path-heads on the §3 Touches lines that exist in the tree (never speculative)
        paths: list[str] = []
        body = _raw_phase_bodies(root, slug).get(3, "")
        for line in body.splitlines():
            if not line.lstrip().startswith("Touches"):
                continue
            for tok in re.findall(r"([\w.-]+(?:/[\w.-]+)+):", line):
                if tok not in paths and (rootp / tok).exists():
                    paths.append(tok)
        return paths

    missing_all = False
    if resolved is None:
        print("scope: UNDECLARED (grandfathered)")
    elif not resolved:
        print("scope: every token dropped — a garbage declaration grants NO cover")
    else:
        marks = [(rel, (rootp / rel).exists()) for rel in resolved]
        for rel, ok in marks:
            print(f"scope: {rel} [{'ok' if ok else 'MISSING'}]")
            # scope-first-freeze teach note: a MISSING token that resolved UNDER the task
            # dir is almost always the `./…`-grammar trap (2026-07-23 WM1 census, rep1/2:
            # declared `./app/`, built root app/) — name the rule at the freeze read.
            if not ok and rel.startswith(".add/tasks/"):
                print(f"note: {rel} resolves under THIS TASK's dir (the `./…` token rule) — "
                      "a project file wants a root-relative token (e.g. `app/`)")
        missing_all = not any(ok for _, ok in marks)
        # scope-coverage-hint: the too-narrow class behind the measured re-cross
        # repairs — tokens resolve [ok] yet the build's real targets sit outside them.
        uncovered = [tok for tok in _touches_paths() if not _in_scope(tok, resolved)]
        for tok in uncovered:
            print(f"note: §3 Touches cites {tok} outside the declared scope")
        # scope-first-draft: escalate the per-token notes to ONE paste-ready corrected
        # line — declared tokens + the uncovered Touches paths — so the fix is a copy,
        # not a re-derive (turns a post-freeze re-cross repair into a freeze-time edit).
        if uncovered:
            merged = list(resolved) + [u for u in uncovered if u not in resolved]
            print("scope (paste-ready — declared misses §3 Touches): Scope (may touch): "
                  + " ".join(merged))
    if resolved is None or not resolved or missing_all:
        paths = _touches_paths()
        if paths:
            print("scope (proposed from §3 Touches): " + " ".join(f"`{p}`" for p in paths))


def _spec_echo(root: Path, slug: str) -> None:
    """build-entry-spec-echo: re-render WHAT to build at the tick INTO build — the §1
    Must/Reject bullet first-lines + the §3 contract-fence head — so the builder starts
    from the spec on the screen, not from memory. PURE read, prints only; a missing or
    malformed section is silently absent (the _build_entry call site wraps fail-open)."""
    bodies = _raw_phase_bodies(root, slug)

    def _bullets(body: str, key: str) -> list[str]:
        # first line of each `- ` bullet under the top-level `Key:` line; a bullet's
        # continuation lines are skipped; the next top-level line ends the block.
        out: list[str] = []
        lines = body.splitlines()
        starts = [n for n, ln in enumerate(lines) if ln.strip() == f"{key}:"]
        if not starts:
            return out
        for ln in lines[starts[0] + 1:]:
            s = ln.strip()
            if s.startswith("- "):
                out.append(s[2:].strip())
            elif ln[:1].isspace() and s:
                continue
            else:
                break
        return out

    musts = _bullets(bodies.get(1, ""), "Must")
    rejects = _bullets(bodies.get(1, ""), "Reject")
    m = re.search(r"(?ms)^```[^\n]*\n(.*?)^```", bodies.get(3, ""))
    head = ""
    if m:
        head = next((ln.strip() for ln in m.group(1).splitlines() if ln.strip()), "")
    if not (musts or rejects or head):
        return
    print("build to (frozen plan):")
    for item in musts:
        print(f"  must: {item}")
    for item in rejects:
        print(f"  reject: {item}")
    if head:
        print(f"  contract: {head}")


def cmd_freeze(args: argparse.Namespace) -> None:
    """The §3 contract-freeze write command — the 5th engine-WRITTEN human approval (task
    freeze-actor-stamp), joining lock · gate · milestone-done · release. Flips the target
    task's §3 `Status: DRAFT` -> `FROZEN @ vN — approved by <name>` AND records a structured
    actor on the task's state record (mirrors cmd_lock's `setup.actor`), so the audit trail
    has no hole at freeze. The human RUNS it as their approval — never pre-stamped.

    validate-then-write: every refusal fires before any write. Writes PLAN.md first, then
    state; a crash between degrades to today's legacy text-only freeze (never corrupt state),
    design-for-failure."""
    root = _require_root()
    state = load_state(root)
    raw_slug = getattr(args, "slug", None)
    if not raw_slug and not _active_task(state):
        _die("no_active_task: no task given and no active task is set")
    slug = _resolve_task(state, raw_slug)                  # unknown slug -> _die
    task_md = root / "tasks" / slug / "PLAN.md"
    text = task_md.read_text(encoding="utf-8")
    raw3 = _phase_spans(text).get(3, "")
    phase = (state["tasks"].get(slug) or {}).get("phase", "direction")
    # --- validate (no writes); error precedence: frozen -> not-drafted -> unflagged ---
    if _contract_frozen(raw3):
        # first-call-ergonomics M2: an EXACT already-frozen retry is a READ-only exit-0
        # no-op, not a hard error — it restates the frozen version and redirects a real
        # shape change to a change request, and touches zero bytes of PLAN.md/state.json.
        ver_m = re.search(r"FROZEN @ (v\d+)", raw3)
        ver = ver_m.group(1) if ver_m else "?"
        print(f"already frozen @ {ver} — a shape change is a change request back to SPECIFY")
        print(_next_footer(root, state))
        return
    # phase-collapse-3: every lane freezes its whole Direction bundle (§1–§4) at once —
    # the freeze may run anywhere inside the `direction` span; only the drafted-contract
    # + flag floors below decide whether it stamps.
    if _phase_index(phase) < _phase_index("direction") or _CONTRACT_TEMPLATE_RE.search(raw3):
        _die(f"contract_not_drafted: {slug}'s §3 is not a drafted contract yet — reach the "
             f"`contract` phase and replace the template before freezing")
    if not _flag_well_formed(raw3):
        _die(f"unflagged_freeze: {slug}'s §3 must surface a well-formed lowest-confidence flag "
             f"('Least-sure flag surfaced at freeze:' + a [part] tag) before it freezes")
    # quality-floors lever 2 (fast-lane-boundary-line): a §1 `Boundary:` line still carrying
    # the bare template placeholder (or empty) refuses the freeze — the wm2 input-dialect
    # floor at the fast lane's single approval seam. Absent line = grandfathered (legacy
    # fast tasks + the full lane gain no new refusal). Reads the §1 span only, first
    # physical line of the declaration (the _declared_scope convention); a backtick-carrying
    # value is exempt from the placeholder rule (_section_unfilled's fence exemption).
    bnd = re.search(r"(?m)^Boundary:[ \t]*(.*)$", _phase_spans(text).get(1, ""))
    if bnd is not None:
        bval = bnd.group(1).strip()
        if not bval or ("`" not in bval and re.fullmatch(r"<.*>", bval)):
            _die(f"boundary_unfilled: {slug}'s §1 Boundary: line still carries the template "
                 f"placeholder — declare >=1 format-variant per external input shape "
                 f"(or an explicit \"none — ...\"), then re-freeze")
    # scope-first-freeze (wm1-lean-to-twelve): a DECLARED §3 Scope resolving to the EMPTY
    # allowlist would freeze a guaranteed scope_violation — the Scope line lives INSIDE the
    # frozen §3, so every post-freeze fix costs a re-cross (2026-07-23 WM1 census: 3/3 reps
    # paid 2-3 calls to this class). Fail-closed at the cheap seam, validate-then-write:
    # nothing is written on this path. UNDECLARED (None) stays grandfathered; resolvable
    # tokens — [ok] or greenfield [MISSING] — freeze exactly as today.
    if _declared_scope(root, slug) == []:
        _die(f"scope_unresolved: {slug} declares a §3 Scope but every token dropped — "
             "backtick each token (`name/` = project root · `./…` = THIS task's dir · a "
             "directory covers its whole subtree); unbackticked or outside-root tokens "
             "grant NO cover, and the gate would refuse scope_violation after the build. "
             "Fix the Scope line, then freeze again")
    # the human declares the risk-CLASS at freeze (risk-sensitivity-taxonomy): a present-but-
    # unknown sensitivity token is refused here (validate-then-write — nothing is written);
    # an absent token is grandfathered (allowed), a valid member proceeds. The engine never
    # classifies — it only validates the human's declaration.
    #
    # ai-plan-verify-gate v2 (2026-07-09 amendment, change request): this generic "?" guard
    # runs ONLY on the HUMAN path now. On the --ai-plan-verify path it is deliberately SKIPPED
    # here so a malformed token flows into _ai_freeze_allowed instead, which returns the
    # DISTINCT, CLI-reachable "ai_freeze_unknown_sensitivity" code — the AI path's own error
    # taxonomy, never borrowing the human path's "sensitivity_invalid". Both paths still refuse
    # a malformed token (fail-safe preserved); only the error code and precedence position
    # differ. The human (flagless) path below is unchanged — same check, same code, same spot
    # in precedence relative to already_frozen/contract_not_drafted/unflagged_freeze.
    _valid_sens = _project_sensitivity_values(root)        # base ∪ project GLOSSARY classes (sensitivity-glossary)
    ai_plan_verify = getattr(args, "ai_plan_verify", False)
    if not ai_plan_verify and _task_sensitivity(_task_header(root, slug), valid=_valid_sens) == "?":
        _die(f"sensitivity_invalid: {slug} declares an unknown sensitivity — use one of "
             f"{', '.join(_valid_sens)} (or add the class to GLOSSARY.md's '## Sensitivity classes', "
             "or omit the line)")
    # ai-plan-verify-gate: an ADDITIVE branch reached ONLY behind --ai-plan-verify — the
    # flagless path above (and its 4 checks) is byte-identical to today. validate-then-write:
    # every refusal below fires before any write, same discipline as the checks above.
    if ai_plan_verify:
        if not args.by:
            _die("ai_freeze_missing_actor: --ai-plan-verify requires --by AGENT_ID — an AI "
                 "freeze must name its own agent id, never inherit the CLI-runner's identity")
        hdr = _task_header(root, slug)
        ai_ok, ai_code = _ai_freeze_allowed(_task_gate_mode(hdr),
                                            _task_sensitivity(hdr, valid=_valid_sens),
                                            _effective_autonomy(root, state, slug))
        if not ai_ok:
            _die(f"{ai_code}: {slug} does not qualify for an AI-plan-verify freeze")
        if not _ai_verify_checklist_complete(raw3):
            _die(f"ai_freeze_checklist_incomplete: {slug}'s §3 'AI-verify record' must be "
                 f"present with all 4 checklist items '- [x]' and a non-empty 'Verified by:' "
                 f"before an AI freeze")
    # --- write ---
    ver = _next_freeze_version(state, slug)
    who = args.by or identity._actor_stamp(state)["name"]
    ts = _now()
    # flip the `Status: DRAFT` line WITHIN the §3 region only — a bare `Status: DRAFT` in
    # §1/§2 prose must never be frozen by mistake (refute-read finding). §3 span runs from
    # its `## 3 ·` heading to the next `## `/`---`/EOF (same boundary as _phase_spans).
    h3 = re.search(r"(?m)^##\s*3\s*·.*$", text)
    if not h3:
        _die(f"contract_not_drafted: {slug}'s PLAN.md has no §3 CONTRACT section")
    seg_start = h3.end()
    nxt = re.search(r"(?m)^(?:##\s|---\s*$)", text[seg_start:])
    seg_end = seg_start + (nxt.start() if nxt else len(text) - seg_start)
    if ai_plan_verify:
        # additive line directly beneath Status — the human path never writes this line.
        new_seg, n = re.subn(r"(?m)^(\s*)Status:\s*DRAFT\s*$",
                             lambda m: (f"{m.group(1)}Status: FROZEN @ {ver} — approved by {who}\n"
                                        f"{m.group(1)}Freeze mode: ai-plan-verify — verified by {who} at {ts}"),
                             text[seg_start:seg_end], count=1)
    else:
        new_seg, n = re.subn(r"(?m)^(\s*)Status:\s*DRAFT\s*$",
                             lambda m: f"{m.group(1)}Status: FROZEN @ {ver} — approved by {who}",
                             text[seg_start:seg_end], count=1)
    if n == 0:
        _die(f"contract_not_drafted: {slug}'s §3 has no 'Status: DRAFT' line to freeze")
    # derived-stamps: a `Ground SHA:` line still carrying its `<...>` placeholder is
    # filled with the repo's real short HEAD in this SAME atomic write, so the freeze
    # fingerprint hashes the stamped text. Grandfather (a resolved line never matches)
    # + fail-open (no git / git fails -> no substitution), mirroring _stamp_gate_record.
    if re.search(r"(?m)^Ground SHA:[ \t]*<[^>\n]*>", new_seg):
        try:
            _r = subprocess.run(["git", "-C", str(root.parent), "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True, timeout=10)
            _sha = _r.stdout.strip() if _r.returncode == 0 else ""
        except (OSError, subprocess.SubprocessError):
            _sha = ""
        if _sha:
            new_seg = re.sub(r"(?m)^Ground SHA:[ \t]*<[^>\n]*>.*$",
                             f"Ground SHA: {_sha} — stamped by freeze", new_seg, count=1)
    new_text = text[:seg_start] + new_seg + text[seg_end:]
    _atomic_write(task_md, new_text)                       # PLAN.md first (audit source of truth)
    state["tasks"][slug]["freeze"] = {"version": ver, "frozen_at": ts,
                                      "approved_by": who, "actor": identity._actor_stamp(state)}
    if ai_plan_verify:
        state["tasks"][slug]["freeze"]["mode"] = "ai-plan-verify"
        state["tasks"][slug]["freeze"]["verified"] = {"anchors": True, "rules": True,
                                                       "shape": True, "flag": True}
    save_state(root, state)
    print(f"froze §3 of {slug} @ {ver} — approved by {who}")
    try:                                # scope-echo-draft: fail-open, never blocks a freeze
        _scope_echo(root, slug)
    except Exception:
        pass
    try:                                # atomicity-signal: SEED a signal when §3 reads as >1 Part
        _atomicity_signal_seed(root, slug)
    except Exception:
        pass
    # compound-ticks: `--cross` compresses the freeze->build crossing into this same
    # call — OPT-IN (the bare freeze is byte-identical). phase-collapse-3 (W2): W1's
    # Direction-span cross is now THE cross, every lane. The bundle (§1–§4) is drafted
    # pre-freeze, so ONE freeze crosses the whole front into build, reusing
    # _build_entry's floor machinery (freeze gate + tamper tripwire + §5 scope
    # snapshot + the cross-component hold/snapshot) — never a parallel path. The human
    # seam (this freeze) + the verify seam (gate next) stay.
    for _hint in _edge_hints(root, state, slug):
        print(_hint)
    if getattr(args, "cross", False):
        cur = state["tasks"][slug]["phase"]
        if cur == "direction":
            _build_entry(root, state, slug)               # snapshots; §3 was just FROZEN above
            state["tasks"][slug]["phase"] = "build"
            state["tasks"][slug]["updated"] = _now()
            save_state(root, state)                       # durable state FIRST
            _sync_task_marker(root, slug, "build")        # then the PLAN.md mirror
            print("Direction-span freeze — §1–§4 crossed into build in one call")
        else:
            print(f"--cross: only a direction-phase freeze crosses (task is at '{cur}' — no-op)")
    print(_next_footer(root, state))


def _edge_hints(root: Path, state: dict, slug: str) -> list[str]:
    """edge-truth hint (task-graph-native W1): at freeze — scope is declared by now —
    name every DONE task whose declared scope overlaps this one's when NO edge links
    them. Deterministic (the _declared_scope grammar both sides, containment on the
    resolved paths), print-only, capped at 2, and silent on UNDECLARED either side —
    a proposal for the agent/human to ratify, never a refusal (measure-not-block)."""
    mine = _declared_scope(root, slug)
    if not mine:
        return []
    rec = (state.get("tasks") or {}).get(slug) or {}
    linked = set((rec.get("depends_on") or []) + (rec.get("extends") or [])
                 + (rec.get("relates_to") or []))
    hints: list[str] = []
    for other, orec in (state.get("tasks") or {}).items():
        if len(hints) >= 2:
            break
        if other == slug or other in linked or (orec or {}).get("phase") != "done":
            continue
        theirs = _declared_scope(root, other) or []
        shared = next((b for a in mine for b in theirs
                       if a == b or a.startswith(b) or b.startswith(a)), None)
        if shared:
            hints.append(f"edge-hint: scope overlaps done task '{other}' ({shared}) — "
                         f"likely a depends-on edge; ratify: add.py relate {slug} "
                         f"--depends-on {other}")
    return hints


def _parse_deps(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [d.strip() for d in raw.split(",") if d.strip()]


def _archived_task_slugs(state: dict) -> set[str]:
    """Slugs of tasks that left active state via archive — all were PASS-done at
    archive time, so a dep on one of them counts as satisfied (not dangling).

    INVARIANT: this is sound only because cmd_archive_milestone REFUSES to archive a
    milestone with an incomplete member. Any NEW task-removal path (un-archive/restore,
    heavy archive) MUST preserve "archived ⇒ was PASS-done" or `ready` will green-light
    a task whose dependency never completed."""
    out: set[str] = set()
    for rec in state.get("archived", []):
        out.update(rec.get("task_slugs", []))   # .get: pre-v2 records have none
    return out


# --- relations-surface: structured task/milestone relations + an advisory guard ------
# Three relation types: depends_on (BLOCKING, drives the wave schedule — existing) plus two
# NON-BLOCKING siblings, extends (builds on a prior shipped surface) and relates_to (shares
# context). Declared, never inferred. Reads are migration-tolerant (absent key -> []).
_MS_REL_KEYS = (("depends-on", "depends_on"), ("extends", "extends"), ("relates-to", "relates_to"))


def _task_relations(t: dict) -> dict:
    """A task's three relation edge-lists, migration-tolerant (absent key -> []). depends_on is
    BLOCKING; extends/relates_to are non-blocking legibility edges (never enter the schedule DAG)."""
    return {"depends_on": list(t.get("depends_on") or []),
            "extends": list(t.get("extends") or []),
            "relates_to": list(t.get("relates_to") or [])}


def _milestone_relations(root: Path, mslug: str) -> dict:
    """Milestone-level relations, parsed from the MILESTONE.md HEADER — the region BEFORE the
    first '## ' section, so a per-task `depends-on:` row inside `## Tasks` is never mistaken for a
    milestone edge. Fail-safe: a missing/garbled doc, or a milestone with no relation lines (an old
    MILESTONE.md), reads all-empty — never raises."""
    out = {"depends_on": [], "extends": [], "relates_to": []}
    md = root / "milestones" / mslug / MILESTONE_FILE
    try:
        header = re.split(r"(?m)^## ", md.read_text(encoding="utf-8"), maxsplit=1)[0]
    except OSError:
        return out
    for label, key in _MS_REL_KEYS:
        m = re.search(rf"(?mi)^{label}:[ \t]*(.+)$", header)
        if m:
            val = m.group(1).strip()
            if val and val.lower() != "none" and not val.startswith("<"):   # skip a placeholder/none
                out[key] = _parse_deps(val)
    return out


def cmd_relate(args: argparse.Namespace) -> None:
    """edge-truth W1.5: the post-creation edge verb the freeze edge-hint ratifies
    through. ADDITIVE only (append + dedup — dropping an edge is a deliberate state
    edit, not a verb). Validate-then-write on the SOURCE slug; TARGETS may dangle
    (a forward edge is legal while its target is pending — `add.py check` reds the
    dangling ref until it resolves, but no gate ever refuses); a self-edge is
    refused (nonsense input, not a measurement)."""
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)                 # unknown slug -> _die
    rec = state["tasks"][slug]
    changed = False
    for flag, key in (("depends_on", "depends_on"), ("extends", "extends"),
                      ("relates_to", "relates_to")):
        new = _parse_deps(getattr(args, flag, None))
        if not new:
            continue
        if slug in new:
            _die(f"self_relation: '{slug}' cannot relate to itself")
        cur = list(rec.get(key) or [])
        merged = cur + [d for d in new if d not in cur]
        if merged != cur:
            rec[key] = merged
            changed = True
    if not changed:
        _die("relate_noop: pass at least one NEW edge — "
             "--depends-on / --extends / --relates-to <slug,slug>")
    rec["updated"] = _now()
    save_state(root, state)
    rel = _task_relations(rec)
    print(f"related '{slug}' — depends_on {rel['depends_on']} · "
          f"extends {rel['extends']} · relates_to {rel['relates_to']}")
    print(_next_footer(root, state))


def _dependent_closure(state: dict, slug: str) -> list[tuple[str, int, str]]:
    """graph-repair W2: REVERSE reachability over depends_on ∪ extends — every task
    that must re-verify if `slug`'s contract changes (the minimal necessary repair
    subgraph). BFS so depth = shortest interface distance; per-ring sorted so output
    is deterministic. relates_to never enters: context is not interface. DONE
    dependents stay in — settled work re-verifies when its foundation moves."""
    tasks = state.get("tasks") or {}
    rev: dict[str, list[tuple[str, str]]] = {}
    for t, rec in tasks.items():
        rel = _task_relations(rec or {})
        for key in ("depends_on", "extends"):
            for parent in rel[key]:
                rev.setdefault(parent, []).append((t, key.replace("_", "-")))
    out: list[tuple[str, int, str]] = []
    seen, ring, depth = {slug}, [slug], 0
    while ring:
        depth += 1
        nxt: list[str] = []
        for node in ring:
            for child, kind in sorted(rev.get(node, [])):
                if child in seen:
                    continue
                seen.add(child)
                out.append((child, depth, kind))
                nxt.append(child)
        ring = nxt
    return out


def _print_closure(state: dict, slug: str) -> None:
    closure = _dependent_closure(state, slug)
    if not closure:
        print(f"closure of '{slug}': no dependents — no task declares a "
              f"depends-on/extends edge on it")
        return
    print(f"closure of '{slug}' — re-verify these if its contract changes "
          f"(reverse depends-on ∪ extends):")
    tasks = state.get("tasks") or {}
    for child, depth, kind in closure:
        ph = (tasks.get(child) or {}).get("phase", "?")
        print(f"  {child} [{ph}] ({kind}, depth {depth})")


_COVERS_RE = re.compile(
    r"^\s*-\s*(?:`(?P<bt>[^`]+)`|(?P<bare>test_[\w.\[\]-]+))\s*:?.*?covers:\s*(?P<codes>[^\n]+)$",
    re.M)


def _covers_map(root: Path, slug: str) -> dict[str, list[str]]:
    """clause-repair W3: §4's test→clause map, frozen WITH the bundle so it is
    tamper-guarded like the suite it describes. Grammar = the template's OWN
    `<test_plan>` dialect — a §4 bullet naming a test (bare `test_…` or
    backticked) whose line carries `covers: <key>[, <key>…]`. The template's
    unfilled placeholder bullet parses to nothing (a `<…>` key is filtered,
    fail-safe); an unmapped test is a nudge downstream, never a gate."""
    body = _raw_phase_bodies(root, slug).get(4, "")
    out: dict[str, list[str]] = {}
    for m in _COVERS_RE.finditer(body):
        name = (m.group("bt") or m.group("bare") or "").strip()
        keys = [c.strip() for c in m.group("codes").split(",")
                if c.strip() and "<" not in c and ">" not in c]
        if name and keys:
            cur = out.setdefault(name, [])
            cur.extend(k for k in keys if k not in cur)
    return out


def _print_clauses(root: Path, slug: str, test_name: str) -> None:
    """Resolve one failing test through the §4 covers map to the frozen §3 clause
    LINE(s) — literal key match inside the §3 body, never a guess. A key §3
    doesn't carry is reported honestly (the clause lives in §1/§2 prose)."""
    codes = _covers_map(root, slug).get(test_name)
    if not codes:
        print(f"  no covers: entry for `{test_name}` in '{slug}' §4 — map each red "
              f"to the §3 clause key it proves (`- `{test_name}` covers: R-…`)")
        return
    s3 = _raw_phase_bodies(root, slug).get(3, "")
    for code in codes:
        hit = next((ln.strip() for ln in s3.splitlines() if code in ln), None)
        if hit:
            print(f"  clause {code} — §3: {hit[:120]}")
        else:
            print(f"  clause {code} — not literal in '{slug}' §3; the clause lives "
                  f"in §1/§2 prose — re-read the Direction bundle before repairing")


def cmd_locate(args: argparse.Namespace) -> None:
    """graph-repair W2 + clause-repair W3: deterministic failure-location — no LLM,
    read-only. A test PATH maps to its OWNING node (§4 `Tests live in:`
    declarations, falling back to the frozen §5 scope snapshot) plus the failure
    class: `in-node` (owner still live — fix inside it, its frozen suite is the
    floor) vs `interface-regression` (owner DONE — a live change broke a settled
    contract; the repair set is that owner's dependent closure). The pytest
    node-id form `path::test_name` goes one level deeper: the §4 covers map
    resolves the test to its frozen §3 clause line. A task SLUG prints the
    closure directly."""
    root = _require_root()
    state = load_state(root)
    ref = args.ref.strip()
    tasks = state.get("tasks") or {}
    if ref in tasks:
        _print_closure(state, ref)
        return
    test_name = None
    if "::" in ref:
        ref, _, test_name = ref.partition("::")
        test_name = test_name.split("::")[-1].strip() or None   # class::method -> method
    rootp = root.parent.resolve()
    target = (Path(ref) if Path(ref).is_absolute() else root.parent / ref).resolve()
    try:
        relref = target.relative_to(rootp).as_posix()
    except ValueError:
        relref = ref
    owners: list[tuple[str, str]] = []
    for slug in sorted(tasks):
        try:
            if any(f.resolve() == target for f in _declared_test_files(root, slug)):
                owners.append((slug, "§4 Tests-live-in"))
                continue
        except OSError:
            pass
        for tok in ((tasks[slug].get("scope") or {}).get("declared") or []):
            t = str(tok).strip().strip("`")
            t = t[2:] if t.startswith("./") else t
            if t and (relref == t or relref.startswith(t.rstrip("/") + "/")):
                owners.append((slug, "scope snapshot"))
                break
    if not owners:
        print(f"unowned: no task declares `{ref}` — not in any §4 Tests-live-in "
              f"nor frozen scope snapshot; treat it as a host/foreign surface "
              f"(regression floor), or declare it before repairing")
        return
    for slug, prov in owners:
        ph = (tasks.get(slug) or {}).get("phase", "?")
        print(f"owner: {slug} [{ph}] (via {prov})")
        if test_name:
            _print_clauses(root, slug, test_name)
        if ph == "done":
            print(f"class: interface-regression — '{slug}' is settled; a live change "
                  f"broke its contract. Fix the breaker first; if the CONTRACT itself "
                  f"must move, re-verify the closure:")
            _print_closure(state, slug)
        else:
            print(f"class: in-node — fix inside '{slug}'; its frozen suite is the "
                  f"floor (never weaken it to pass)")


_MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"


def _graph_html_page(title: str, mermaid: str, done: int, total: int,
                     met: int, ectot: int, show_ec: bool) -> str:
    """graph-html: wrap the mermaid diagram in a self-rendering, theme-aware HTML page —
    engine-authored chrome (title + done/met status chips + a legend) plus a `<pre
    class="mermaid">` (HTML-escaped so no `<`/`>`/`&` breaks parsing) and a PINNED mermaid
    CDN `<script>`. The 3 MB library rides the CDN, never the 4-way byte-twinned add.py;
    the diagram source is fully embedded (readable offline, renders online)."""
    esc = mermaid.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    ec_chip = (f'<span class="chip ok">{met}/{ectot} exit-criteria met</span>'
               if show_ec else "")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t} · add graph</title>
<style>
  :root {{ --bg:#f6f7f9; --panel:#fff; --plate:#fbfcfd; --ink:#1a1f27; --soft:#5a6472;
          --hair:#e3e7ec; --accent:#1971c2; --met:#2b8a3e;
          --mono:ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;
          --sans:system-ui,-apple-system,"Segoe UI",sans-serif; }}
  @media (prefers-color-scheme:dark) {{ :root {{ --bg:#0e1116; --panel:#161b22;
          --ink:#e6edf3; --soft:#8b949e; --hair:#262c34; --accent:#4a9eea; }} }}
  :root[data-theme="light"] {{ --bg:#f6f7f9; --panel:#fff; --ink:#1a1f27; --soft:#5a6472; --hair:#e3e7ec; --accent:#1971c2; }}
  :root[data-theme="dark"] {{ --bg:#0e1116; --panel:#161b22; --ink:#e6edf3; --soft:#8b949e; --hair:#262c34; --accent:#4a9eea; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font-family:var(--sans); line-height:1.5; }}
  .wrap {{ max-width:1100px; margin:0 auto; padding:36px 24px 56px; }}
  .cmd {{ font-family:var(--mono); font-size:13px; color:var(--soft); }}
  h1 {{ font-family:var(--mono); font-size:clamp(24px,4vw,34px); font-weight:600; margin:8px 0 14px; }}
  .chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:24px; }}
  .chip {{ font-family:var(--mono); font-size:12px; padding:4px 10px; border-radius:999px;
          border:1px solid var(--hair); background:var(--panel); color:var(--soft); }}
  .chip.ok {{ color:var(--met); border-color:color-mix(in srgb,var(--met) 35%,var(--hair)); }}
  .plate {{ background:var(--plate); border:1px solid var(--hair); border-radius:14px;
          padding:20px; overflow-x:auto; box-shadow:0 8px 28px rgba(20,30,50,.06); }}
  .mermaid {{ display:flex; justify-content:center; min-width:560px; }}
  .legend {{ display:flex; flex-wrap:wrap; gap:18px; margin-top:20px; font-family:var(--mono);
          font-size:12px; color:var(--soft); }}
  .legend b {{ color:var(--accent); font-weight:600; }}
</style></head><body>
<div class="wrap">
  <div class="cmd">$ add.py graph</div>
  <h1>{t}</h1>
  <div class="chips">
    <span class="chip ok">{done}/{total} tasks done</span>
    {ec_chip}
  </div>
  <div class="plate"><pre class="mermaid">
{esc}
  </pre></div>
  <div class="legend">
    <span><b>--&gt;</b> depends-on</span>
    <span><b>-.-&gt;</b> observed-by / delivered-by</span>
    <span><b>==&gt;</b> blocks</span>
    <span>green = done / met · blue = signal · grey = planned / unmet</span>
  </div>
</div>
<script src="{_MERMAID_CDN}"></script>
<script>mermaid.initialize({{ startOnLoad: true, securityLevel: "loose" }});</script>
</body></html>
"""


def cmd_graph(args: argparse.Namespace) -> None:
    """graph-views W4: the live board as a mermaid flowchart — deterministic,
    read-only, print-only (paste into any mermaid renderer / GitHub fence).
    Milestone = the scope ROOT: a subgraph wrapping its tasks; depth lives in
    EDGES, never nesting. Styles carry semantics: depends-on solid `-->` ·
    extends dashed `-.->` · relates-to open dashed `-.-`; node class = phase
    (done · live · planned). The compiled plan renders too: a planned-but-
    never-created node appears dashed — drift is visible before it warns."""
    root = _require_root()
    state = load_state(root)
    tasks = state.get("tasks") or {}
    milestones = state.get("milestones") or {}
    archived = _archived_task_slugs(state)
    only = getattr(args, "milestone", None)
    if only and only not in milestones:
        _die(f"unknown_milestone: '{only}'")

    def node_id(slug: str) -> str:
        return ("t_" + slug) if slug in tasks else ("p_" + slug)

    lines = ["flowchart TD"]
    extra_nodes: dict[str, str] = {}       # id -> label, for archived/missing edge targets
    shown: set[str] = set()
    planned_shown: set[str] = set()
    for ms in sorted(milestones):
        if only and ms != only:
            continue
        members = sorted(s for s, t in tasks.items() if t.get("milestone") == ms)
        planned = sorted(k for k in (milestones[ms].get("planned") or {})
                         if k not in tasks and k not in archived)
        if not members and not planned:
            continue
        lines.append(f'  subgraph ms_{ms}["{ms} · milestone"]')
        for slug in members:
            ph = tasks[slug].get("phase", "?")
            lines.append(f'    t_{slug}["{slug} · {ph}"]')
            shown.add(slug)
        for slug in planned:
            lines.append(f'    p_{slug}["{slug} · planned"]')
            planned_shown.add(slug)
        lines.append("  end")
    if not only:
        for slug in sorted(tasks):
            if slug not in shown and not tasks[slug].get("milestone"):
                lines.append(f'  t_{slug}["{slug} · {tasks[slug].get("phase", "?")}"]')
                shown.add(slug)

    edge_style = (("depends_on", "-->", "depends-on"),
                  ("extends", "-.->", "extends"),
                  ("relates_to", "-.-", "relates-to"))
    for slug in sorted(tasks):
        if only and tasks[slug].get("milestone") != only:
            continue
        rel = _task_relations(tasks[slug])
        for key, arrow, label in edge_style:
            for parent in rel[key]:
                pid = node_id(parent)
                if parent not in tasks:
                    note = "archived" if parent in archived else "planned" \
                        if any(parent in (m.get("planned") or {}) for m in milestones.values()) \
                        else "missing"
                    if note != "planned":                      # planned already rendered above
                        pid = "x_" + parent
                        extra_nodes[pid] = f'{pid}["{parent} · {note}"]'
                lines.append(f"  t_{slug} {arrow}|{label}| {pid}")
    lines.extend(f"  {n}" for _, n in sorted(extra_nodes.items()))
    lines.append("  classDef done fill:#d3f9d8,stroke:#2b8a3e")
    lines.append("  classDef live fill:#fff3bf,stroke:#e67700")
    lines.append("  classDef planned fill:none,stroke:#868e96,stroke-dasharray: 4 4")
    for slug in sorted(shown):
        cls = "done" if tasks[slug].get("phase") == "done" else "live"
        lines.append(f"  class t_{slug} {cls}")
    lines.extend(f"  class p_{slug} planned" for slug in sorted(planned_shown))
    # signal overlay (graph-view-signals): opt-in `--signals` layer — LIVE signals
    # (todos + open §7 deltas via _signals) as nodes edged to their task nodes. Pure
    # read; the default (no flag) path above is byte-unchanged. Resolved/dropped omit.
    if getattr(args, "signals", False):
        live = [s for s in _signals(root) if s["status"] not in ("resolved", "dropped")]
        sig_missing: dict[str, str] = {}
        node_lines: list[str] = []
        edge_lines: list[str] = []
        class_lines: list[str] = []
        for s in live:
            obs = [t for r, t in s["edges"] if r == "observed-by"]
            if obs and not any(t in shown for t in obs):
                continue                        # observed-by task filtered out by --milestone
            sid = "sig_" + re.sub(r"[^0-9A-Za-z]", "_", s["id"])
            text = re.sub(r'["\[\]|\n]', " ", s["text"]).strip()[:40]
            node_lines.append(f'  {sid}["{s["kind"]} · {s["status"]}: {text}"]')
            class_lines.append(f"  class {sid} signal")
            for rel, target in s["edges"]:
                arrow = {"observed-by": "-.->", "resolves-into": "-->",
                         "blocks": "==>"}.get(rel)
                if not arrow:
                    continue
                if target in tasks:
                    tid = node_id(target)
                else:                           # missing/archived target -> x_ fallback (never dangling)
                    tid = "x_" + target
                    note = "archived" if target in archived else "missing"
                    sig_missing[tid] = f'  {tid}["{target} · {note}"]'
                edge_lines.append(f"  {sid} {arrow}|{rel}| {tid}")
        if node_lines:
            lines.extend(sorted(sig_missing.values()))
            lines.extend(node_lines)
            lines.extend(edge_lines)
            lines.append("  classDef signal fill:#e7f5ff,stroke:#1971c2")
            lines.extend(class_lines)
        # exit-criterion overlay (exit-criterion-nodes): each milestone exit criterion
        # as a delivered-by node — met/unmet classed, edged to the task that satisfies it
        # (x_ fallback for an unknown slug, no edge when unpointed). Same `--signals` gate.
        ec_nodes = [n for n in _exit_criterion_nodes(root) if not only or n["ms"] == only]
        if ec_nodes:
            ec_missing: dict[str, str] = {}
            ec_node_lines: list[str] = []
            ec_edge_lines: list[str] = []
            ec_class_lines: list[str] = []
            for n in ec_nodes:
                nid = f"ec_{n['ms']}_{n['idx']}"
                glyph = "✓" if n["met"] else "○"
                text = re.sub(r'["\[\]|\n]', " ", n["text"]).strip()[:40]
                ec_node_lines.append(f'  {nid}["{glyph} {text}"]')
                ec_class_lines.append(f"  class {nid} {'ec_met' if n['met'] else 'ec_unmet'}")
                slug = n["delivered_by"]
                if slug:
                    if slug in tasks:
                        tid = node_id(slug)
                    else:                       # unknown slug -> x_ fallback (never dangling)
                        tid = "x_" + slug
                        note = "archived" if slug in archived else "missing"
                        ec_missing[tid] = f'  {tid}["{slug} · {note}"]'
                    ec_edge_lines.append(f"  {nid} -.->|delivered-by| {tid}")
            lines.extend(sorted(ec_missing.values()))
            lines.extend(ec_node_lines)
            lines.extend(ec_edge_lines)
            lines.append("  classDef ec_met fill:#d3f9d8,stroke:#2b8a3e")
            lines.append("  classDef ec_unmet fill:#f1f3f5,stroke:#868e96")
            lines.extend(ec_class_lines)
    mermaid = "\n".join(lines)
    # graph-html: opt-in `--html` wraps the SAME mermaid in a self-rendering page written
    # to a temp file (the board stays read-only; the only write is the requested output).
    if getattr(args, "html", False):
        done = sum(1 for s in shown if tasks[s].get("phase") == "done")
        ecs = [n for n in _exit_criterion_nodes(root) if not only or n["ms"] == only]
        met = sum(1 for n in ecs if n["met"])
        page = _graph_html_page(only or "ADD graph", mermaid, done, len(shown),
                                met, len(ecs), bool(only))
        out = (Path(args.out) if getattr(args, "out", None)
               else Path(tempfile.gettempdir()) / f"add-graph{'-' + only if only else ''}.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print(f"wrote {out}")
        print("open it in a browser to view the rendered graph")
        return
    print(mermaid)


def _relations_health(root: Path, state: dict) -> list[dict]:
    """ADVISORY validate/sync pass over every task's non-blocking relations. Returns findings
    [{slug, relation, target, kind}] — kind in {'dangling','self_relation'}. A target that is a
    known OR archived (PASS-done) task resolves; a target that is neither (unknown or removed) is
    dangling; a self-edge is self_relation. PURE — never writes, never blocks a gate (mirrors the
    SHA-freshness deps line: measured, surfaced, never enforced)."""
    tasks = state.get("tasks") or {}
    archived = _archived_task_slugs(state)
    findings: list[dict] = []
    for slug, t in tasks.items():
        rel = _task_relations(t)
        for rtype in ("extends", "relates_to"):
            for target in rel[rtype]:
                if target == slug:
                    findings.append({"slug": slug, "relation": rtype,
                                     "target": target, "kind": "self_relation"})
                elif target not in tasks and target not in archived:
                    findings.append({"slug": slug, "relation": rtype,
                                     "target": target, "kind": "dangling"})
    return findings


def _milestone_relations_health(root: Path, state: dict) -> list[dict]:
    """ADVISORY validate pass over every milestone's relation edges — the milestone twin of
    _relations_health. Returns [{mslug, relation, target, kind}], kind in {'dangling',
    'self_relation'}: a depends_on/extends/relates_to target that is not a known milestone is
    dangling; a self-edge is self_relation. Milestone edges are cross-milestone LEGIBILITY only
    (never a build DAG, never blocking) so all three edge kinds are validated here — unlike the
    task twin, whose depends_on IS the schedule DAG and is checked there. PURE: reads MILESTONE.md
    headers via _milestone_relations, never writes, never blocks a gate."""
    milestones = state.get("milestones") or {}
    findings: list[dict] = []
    for mslug in milestones:
        rel = _milestone_relations(root, mslug)
        for rtype in ("depends_on", "extends", "relates_to"):
            for target in rel[rtype]:
                if target == mslug:
                    findings.append({"mslug": mslug, "relation": rtype,
                                     "target": target, "kind": "self_relation"})
                elif target not in milestones:
                    findings.append({"mslug": mslug, "relation": rtype,
                                     "target": target, "kind": "dangling"})
    return findings


def _resolve_task(state: dict, slug: str | None) -> str:
    slug = slug or _active_task(state)
    if not slug:
        _die("no task specified and no active task set")
    if slug not in state["tasks"]:
        _die(f"unknown task '{slug}'")
    return slug


def _resolve_milestone(state: dict, slug: str) -> str:
    """The milestone twin of _resolve_task: return `slug` if it names a milestone,
    else `_die("unknown_milestone")` (the exact bare code the callers used inline).
    Only the byte-identical bare-form sites route through here — sites that raise a
    fuller `unknown_milestone: '<x>' is not…` message keep their own wording."""
    if slug not in state.get("milestones", {}):
        _die("unknown_milestone")
    return slug




def _dialect_gaps(root: Path, slug: str) -> list:
    """spec-dialect-floor (quality-floors): the dialect classes the frozen §3 speaks that NO
    declared §4 test file does. PURE — reads PLAN.md + declared test files, writes nothing.
    Fail-open by design: no §3 match, no declared test files, or unreadable files -> [] —
    the floor warns where it can SEE a gap and never invents one (wm2 evidence: the gap it
    exists to catch is a suite speaking a friendlier input dialect than the spec's own
    examples)."""
    body3 = _raw_phase_bodies(root, slug).get(3, "")
    if not body3:
        return []
    files = _declared_test_files(root, slug)
    if not files:
        return []
    corpus = ""
    for f in files:
        try:
            corpus += f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
    gaps = []
    for name, pattern in _DIALECT_CLASSES:
        rx = re.compile(pattern)
        if rx.search(body3) and not rx.search(corpus):
            gaps.append(name)
    return gaps


def _build_entry(root: Path, state: dict, slug: str, skip_freeze: bool = False,
                 require_frozen: bool = False) -> None:
    """The shared tests->build entry guards + snapshots (task phase-build-guard, F4).

    Extracted VERBATIM from cmd_advance's `nxt == "build"` block so BOTH `advance` and the
    `phase build` admin override run the identical gate stack — the freeze gate, the
    unflagged-freeze check + flag stamp, the tamper tripwire, and
    the §5 scope snapshot. validate-then-write: every `_die` precedes the first state mutation,
    so a refused entry leaves the task byte-unchanged. The heal loop sets phase=build DIRECTLY
    and never routes here, so it stays exempt.
    """
    # the crossing guards. validate-then-write — every refusal runs BEFORE the tripwire/scope
    # snapshots below, writing nothing; the task stays at `tests` (the lone exception is the
    # recorded freeze_skipped marker on the explicit --skip-freeze path).
    _ms = state["tasks"][slug].get("milestone")
    _optin = bool(_ms) and (state.get("milestones") or {}).get(_ms, {}).get("await_confirm") is True
    raw3 = _raw_phase_bodies(root, slug).get(3, "")
    # freeze gate — UNIVERSAL (freeze-gate-universal, flow-honesty): closes audit finding H1.
    # The gate used to be opt-in (`_optin or fast`), so a plain-milestone task could cross
    # tests->build on a DRAFT §3 — the method's decision point was engine-enforced for only a
    # subset. It now fires for EVERY task. The ONLY bypass is the RECORDED `--skip-freeze` escape:
    # it stamps an auditable `freeze_skipped` marker (never silent) and never auto-freezes §3
    # (Status stays DRAFT).
    if not _contract_frozen(raw3):
        # a freeze_skipped recorded at the plan->tests gate carries through here (a single
        # --skip-freeze is enough for the whole plan->tests->build run); a still-DRAFT §3 with
        # no prior skip and no --skip-freeze on THIS crossing is refused. require_frozen (re-cross)
        # IGNORES the carry-through marker: a re-cross is a deliberate re-entry that must re-assert
        # the freeze (its contract is "never a freeze bypass"), so a DRAFT §3 always refuses there
        # regardless of any historical skip.
        already_skipped = (not require_frozen) and bool(state["tasks"][slug].get("freeze_skipped"))
        if not skip_freeze and not already_skipped:
            _die("contract_not_frozen: freeze §3 before crossing into build — approve "
                 f"the contract in {slug}'s PLAN.md (Status: FROZEN @ vN), or pass "
                 "--skip-freeze to cross with a recorded skip")
        if not already_skipped:
            state["tasks"][slug]["freeze_skipped"] = {
                "by": identity._actor_stamp(state)["name"],
                "at": _now(),
                "from_phase": state["tasks"][slug].get("phase", "direction"),
            }
    if _contract_frozen(raw3):
        if not _flag_well_formed(raw3):
            _die("unflagged_freeze: a frozen §3 must surface a well-formed "
                 "'Least-sure flag surfaced at freeze:' unit (>=1 [part] tag "
                 "+ substantive content; bare 'none' only as 'none material — "
                 "biggest risk: X') before crossing into build")
        state["tasks"][slug]["flag_verified"] = True
    # persona-routes-depth: record the header route proposal — the freeze IS the
    # ratify. UNCONDITIONAL overwrite (a re-cross re-records); measure-not-block —
    # "unrouted" is a valid record, audit surfaces it (route_unrecorded).
    state["tasks"][slug]["route"] = _route_record(_task_header(root, slug))
    # tamper tripwire (verify-integrity): snapshot the red test files + the frozen
    # §3 md5s so the verify gate can prove the green was EARNED, not edited into
    # place. UNCONDITIONAL overwrite — a legit change-request that re-crosses
    # tests->build re-snapshots cleanly. Co-witnessed by flag_verified (above).
    state["tasks"][slug]["tripwire"] = _tripwire_snapshot(root, slug, raw3)
    # §5 scope gate (build-scope-lock): when the task declares its Scope, freeze
    # the project tree into a sidecar (payload) + a state.json anchor (md5 of the
    # sidecar bytes). Same UNCONDITIONAL-overwrite semantics as the tripwire.
    # UNDECLARED (no Scope line) takes no snapshot — grandfathered, never retro-red
    # — and CLEANS UP a previous declaration's leftovers (v3): a declared->
    # undeclared re-cross pops the stale anchor + unlinks the stale sidecar, so
    # "UNDECLARED is never refused" holds on every path.
    declared = _declared_scope(root, slug)
    side = root / "tasks" / slug / "scope-snapshot.json"
    if declared is not None:
        payload = json.dumps({"version": 1,
                              "files": _scope_walk(root.parent.resolve())},
                             sort_keys=True)
        _atomic_write(side, payload)   # temp+replace, like save_state — a crash can't leave a
                                       # torn sidecar (payload verbatim, no newline → md5 anchor holds)
        state["tasks"][slug]["scope"] = {"declared": declared,
                                         "snapshot_md5": _md5_text(payload)}
        # scope-gate-repair-path M1: the crossing WARNS (never refuses) when the §5
        # Scope line still carries the template placeholder — the default `./src/`
        # resolves to THIS TASK's dir, so it silently arms a guaranteed
        # scope_violation at the gate (the live-benchmark death spiral). Print-only:
        # exit, snapshot, and state above are byte-identical either way.
        _rb5 = _raw_phase_bodies(root, slug)
        m5 = (re.search(r"^\s*Scope \(may touch\):.*$", _rb5.get(3, ""), re.M)
              or re.search(r"^\s*Scope \(may touch\):.*$", _rb5.get(5, ""), re.M))
        # scope-first-freeze: detection accepts BOTH hint eras — the original
        # "<fill before the §3 freeze" wording AND the #38-relabeled "<HARD — fill
        # before the freeze" (the relabel silently killed the original match).
        if m5 and ("<fill before the §3 freeze" in m5.group(0)
                   or "<HARD — fill before the freeze" in m5.group(0)):
            print(f"warning: task '{slug}' §3 Scope is still the template default — "
                  "edit it to the REAL write-set (the default `src/` covers only the "
                  "project-root src/; `./…` = this task's dir) (a note, not a blocker — "
                  "it clears only when the Scope line itself is edited; re-cross does "
                  "not clear it)")
    else:
        state["tasks"][slug].pop("scope", None)
        try:
            side.unlink()
        except OSError:
            pass
    # spec-dialect-floor (quality-floors M3): warn — NEVER refuse — when the frozen §3 speaks
    # a format dialect no declared §4 test file does (benchmark wm2: naive-timestamp tests
    # kept an aware/naive crash green while the spec's own examples were Z-suffixed).
    # Print-only, after every guard and snapshot: exit and state are byte-identical.
    for _cls in _dialect_gaps(root, slug):
        print(f"warning: task '{slug}' frozen §3 carries a '{_cls}' value but no declared "
              "§4 test file speaks that format — a suite testing a friendlier input dialect "
              "than the spec's own examples can stay green through a real crash (benchmark "
              "wm2 evidence). Add one test using the contract's literal format, then "
              "re-snapshot: add.py re-cross --by <name>")
    # build-entry spec echo (six-phase-loop): the tick INTO build re-renders WHAT to
    # build — §1 Must/Reject + the §3 contract head — on BOTH entries (advance and the
    # `phase build` override funnel here). TAIL of the stack, so a refused entry never
    # echoes; fail-open, so exit code, state, and PLAN.md are identical either way.
    try:
        _spec_echo(root, slug)
    except Exception:
        pass
    # kernel-trim (ADD 2.0 M5): the cross-component contract snapshot/pin machinery died with
    # the components pillar — cross-repo shape discipline is the platform-engineer persona's
    # playbook now, not an engine hold.


def cmd_phase(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    # phase-collapse-3 (M6): a legacy phase name is accepted, MAPPED to its 3-phase home,
    # and noted — old scripts and muscle memory keep working; the stored value is always
    # a member of the collapsed PHASES enum.
    if args.phase in LEGACY_PHASES:
        mapped = LEGACY_PHASES[args.phase]
        print(f"note: '{args.phase}' is a legacy phase — mapped to '{mapped}' "
              "(phase-collapse-3: direction·build·verify·done)")
        args.phase = mapped
    if args.phase not in PHASES:
        _die(f"phase must be one of: {', '.join(PHASES)}")
    # phase-build-guard (F4): the admin override is NOT a backdoor around the direction->build
    # gate stack — setting a task to build runs the SAME _build_entry guards `advance` runs
    # (freeze gate · flag check · cross-component hold · tamper tripwire ·
    # scope snapshot), so verify's _tamper_guard is armed and a freeze-gated DRAFT §3 is refused.
    # validate-then-write: a refusal raises BEFORE the phase is set, so nothing moves. The heal
    # loop sets phase=build directly (never via cmd_phase) and so stays exempt.
    # round-visible-runs: --note annotates a verify->build ROUND — refuse it anywhere else,
    # BEFORE any write (validate-then-write; a refused entry leaves state byte-unchanged).
    # The refusal keys on the FLAG being passed (whitespace included) and the note is stored
    # VERBATIM (§1 Boundary); the contract's refusal exit code is 2.
    note = getattr(args, "note", None)
    if note is not None and args.phase != "build":
        _die("phase_note_build_only: --note annotates the verify->build round this return "
             "records — it is only valid with target build", code=2)
    prior = state["tasks"][slug].get("phase")
    if args.phase == "build":
        _build_entry(root, state, slug, skip_freeze=getattr(args, "skip_freeze", False))
    # round-visible-runs: a verify->build return trip IS a round — record it in the SAME
    # save as the phase write (atomic; no round without the return, no return without it).
    if args.phase == "build" and prior == "verify":
        _record_round(state["tasks"][slug], source="phase", note=note)
    state["tasks"][slug]["phase"] = args.phase
    state["tasks"][slug]["updated"] = _now()
    save_state(root, state)                    # F12: durable state FIRST (source of truth) — may _die
    _sync_task_marker(root, slug, args.phase)  # then mirror into PLAN.md (best-effort) — no split-brain
    print(f"task '{slug}' phase -> {args.phase}")
    print(_next_footer(root, state))


def cmd_recross(args: argparse.Namespace) -> None:
    """The RECORDED post-freeze re-cross (bundle-advance): a HUMAN-APPROVED test change after
    the tests->build crossing (e.g. a test added at review) re-arms the tamper tripwire + §5
    scope snapshot by re-running the IDENTICAL _build_entry gate stack — never a freeze bypass
    (a DRAFT §3 still refuses contract_not_frozen). The approver is recorded in state
    (tasks[slug]["recross"] = {by, at, from_phase}) so an audit can tell a signed re-cross
    from silent tampering. Replaces the undocumented `phase tests` + `advance` dance."""
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    cur = state["tasks"][slug]["phase"]
    if cur not in ("build", "verify"):
        _die(f"recross_wrong_phase: re-cross re-arms the tests->build snapshots — only a "
             f"task at build or verify can re-cross (task '{slug}' is at {cur})")
    if not (getattr(args, "by", "") or "").strip():
        _die("recross_unsigned: a post-freeze test change is human-approved — record the "
             "approver with --by <name>")
    _build_entry(root, state, slug, require_frozen=True)   # full gate stack; a DRAFT §3
                                             # always refuses here — re-cross is never a freeze
                                             # bypass, even for a task that earlier --skip-freeze'd
    state["tasks"][slug]["recross"] = {"by": args.by.strip(), "at": _now(),
                                       "from_phase": cur}
    state["tasks"][slug]["phase"] = "build"
    state["tasks"][slug]["updated"] = _now()
    save_state(root, state)                  # durable state FIRST (source of truth)
    _sync_task_marker(root, slug, "build")   # then mirror into PLAN.md — no split-brain
    print(f"task '{slug}' re-crossed tests->build — tripwire + scope re-snapshotted "
          f"(approved by {args.by.strip()})")
    print(_next_footer(root, state))


def _fill_and_advance(args: argparse.Namespace, root: Path, state: dict, slug: str) -> None:
    """`advance --fill` (engine-batch-ops): draft the CURRENT phase's §body and
    advance in ONE call — the round-trip batching the add-lean-loop milestone
    exists for. ALL-OR-NOTHING (human-chosen at freeze): the original PLAN.md
    bytes are snapshotted, the fill is written, and the UNCHANGED advance guard
    stack runs; any refusal (every _die exit path — SystemExit included)
    restores the snapshot byte-identical and re-raises, so no path leaves a
    filled section with an unmoved phase. Section located with the taskdoc
    `^##\\s*<n>\\s*·` grammar — the one canonical scan, never a second parser."""
    cur = state["tasks"][slug]["phase"]
    if cur not in PHASES:
        _die(f"task '{slug}' has unknown phase '{cur}' (state.json corrupted?)")
    if PHASES.index(cur) >= len(PHASES) - 1:
        # first-call-ergonomics M2: advance --fill at an already-`done` task is a
        # READ-only exit-0 no-op (never a hard error) — the fill payload is never
        # even read, so this stays zero-write no matter what --fill names.
        print(f"task '{slug}' is done")
        print(_next_footer(root, state))
        return
    if args.fill == "-":
        payload = sys.stdin.read()
    else:
        try:
            payload = Path(args.fill).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            _die(f"fill_unreadable: {exc}")
    for ln in payload.splitlines():
        # a line-start "## " or bare "---" would truncate the §-section scan
        # (taskdoc._phase_spans KNOWN LIMIT) — refuse before any write.
        if ln.startswith("## ") or re.match(r"^---\s*$", ln):
            _die("fill_body_unparseable: the payload contains a line-start '## ' or a bare "
                 "'---' line — these truncate the §-section scan; reword or indent them")
    n = _PHASE_SECTIONS[cur][0]  # phase → its PRIMARY PLAN.md §-number, via the explicit
                                 # table (never ordinal math — the off-by-one bug class;
                                 # specify owns §1+§2, verify owns §6+§7: --fill targets
                                 # the first, the drafting section)
    f = root / "tasks" / slug / "PLAN.md"
    try:
        original = f.read_bytes()
    except OSError as exc:
        _die(f"fill_unreadable: {exc}")
    lines = original.decode("utf-8").splitlines(keepends=True)
    head = re.compile(rf"^##\s*{n}\s*·")
    start = next((i for i, ln in enumerate(lines) if head.match(ln)), None)
    if start is None:
        _die(f"fill_section_missing: no '## {n} ·' heading for phase '{cur}' in {f}")
    end = start + 1
    while end < len(lines) and not (lines[end].startswith("## ")
                                    or re.match(r"^---\s*$", lines[end])):
        end += 1
    body = "\n" + payload.rstrip("\n") + "\n\n"
    _atomic_write(f, "".join(lines[:start + 1]) + body + "".join(lines[end:]))
    args.fill = None  # consumed — the plain advance below must not re-enter
    try:
        cmd_advance(args)
    except BaseException:
        # all-or-nothing: restore the pre-fill bytes on ANY refusal, then
        # surface the guard's own message unchanged.
        _atomic_write(f, original.decode("utf-8"))
        raise
    print(f"filled §{n} ({cur}) from --fill")


def cmd_advance(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    if getattr(args, "fill", None) is not None:
        if getattr(args, "to", None) is not None:
            _die("fill_with_to_unsupported: --fill drafts ONE section for ONE crossing — "
                 "fast-forward with --to separately")
        _fill_and_advance(args, root, state, slug)
        return
    cur = state["tasks"][slug]["phase"]
    idx = PHASES.index(cur)
    if idx >= len(PHASES) - 1:
        # first-call-ergonomics M2: a bare advance at an already-`done` task is a
        # READ-only exit-0 no-op (never a hard error) — state is untouched.
        print(f"task '{slug}' is done")
        print(_next_footer(root, state))
        return
    # phase-collapse-3: with the front collapsed into `direction`, --to has no bundle
    # bookkeeping left to fast-forward — legacy tokens map to their 3-phase home and a
    # still-inside-the-span target is a friendly no-op; the build crossing is carried by
    # `freeze --cross` (or a plain advance), never fast-forwarded.
    _to = getattr(args, "to", None)
    if _to is not None:
        _to = LEGACY_PHASES.get(_to, _to)
        if _to not in PHASES:
            _die(f"advance_to_invalid: --to must be one of: {', '.join(PHASES)}")
        if PHASES.index(_to) > PHASES.index("direction"):
            _die("advance_to_stops_at_direction: --to fast-forwards bundle bookkeeping only — "
                 "the direction->build crossing carries the gate stack; cross it with "
                 "freeze --by <name> --cross (or a plain advance)")
        if PHASES.index(_to) <= idx:
            print(f"task '{slug}' is already at {cur} — the direction span is one phase; "
                  "draft §1–§4, then freeze --by <name> --cross")
            print(_next_footer(root, state))
            return
    nxt = PHASES[idx + 1]
    # phase-merge-verify: the skip grammar is RETIRED — _SKIPPABLE_PHASES is empty, no
    # crossing runs skip logic (the old M13 placement, now universal). A vestigial
    # `skips:` header declaration is read once, at gate/completion, and noted loud there.
    # build-boundary gate: pre-lock the direction span is allowed, but crossing
    # into build/verify/done is refused until `add.py lock`.
    if not _setup_locked(state) and nxt in ("build", "verify", "done"):
        _die("setup_unlocked: lock the foundation first — add.py lock")
    # flag-first freeze guard (task unflagged-freeze): a FROZEN §3 may not cross
    # into build without a WELL-FORMED lowest-confidence flag. On pass, stamp the
    # verified marker so `audit` enforces the flag on THIS record only (open/new
    # freezes — the unmarked predecessors are never retro-redded). REFUSE writes
    # nothing (fail-closed); below the build boundary the flag is never checked.
    if nxt == "build":
        # the direction->build entry guards + snapshots live in the shared _build_entry helper
        # (task phase-build-guard, F4; phase-collapse-3 moved the cross-component hold +
        # producer-snapshot/consumer-pin there too) so `advance`, `freeze --cross`, and the
        # `phase build` admin override run the IDENTICAL gate stack. `--skip-freeze`
        # (freeze-gate-universal) threads through to the universal freeze gate — the only
        # recorded bypass of the mandatory §3 freeze.
        _build_entry(root, state, slug, skip_freeze=getattr(args, "skip_freeze", False))
    state["tasks"][slug]["phase"] = nxt
    state["tasks"][slug]["updated"] = _now()
    save_state(root, state)             # F12: durable state FIRST (source of truth) — may _die
    _sync_task_marker(root, slug, nxt)  # then mirror into PLAN.md (best-effort) — no split-brain
    print(f"task '{slug}' phase {cur} -> {nxt}")
    # bundle fast-forward: keep stepping (each pass re-loads state and re-runs every
    # crossing guard) until the validated --to target is reached.
    if _to is not None and PHASES.index(nxt) < PHASES.index(_to):
        cmd_advance(args)
        return
    # guide-fold (orientation-honesty): the completing advance carries the LANDED
    # phase's chapter — the ONE `add.py guide` line the footer lacks (the footer
    # already gives command + short why) — so the agent reads the chapter inline
    # and never re-runs `add.py guide`. Suppressed at 'done' (Arm B owns that
    # juncture) and on bundle fast-forward intermediates (they return above). The
    # `.get` guard is fail-soft: a corrupt/unmapped landed phase folds nothing,
    # never a KeyError on an already-saved advance (the footer's own ethos).
    if nxt != "done":
        _entry = PHASE_GUIDE.get(nxt)
        if _entry is not None:
            print(f"guide: {book_url(_entry[1])} — the phase chapter "
                  "(this + the next line ARE `add.py guide`; no separate call)")
    print(_next_footer(root, state))


# The mechanized high-risk guard (run.md, v14; widened by explicit-autonomy-dial):
# judging WHAT is high-risk stays human — a scope declares `risk: high` in its PLAN.md
# header at the freeze. The engine then enforces the pure token contradiction: risk: high
# WITHOUT a lowered autonomy rung (manual or conservative) is unguarded, and completion is
# refused. Tokens are read from the header region (text before the first section heading)
# with HTML comments stripped — a documentation comment is never a declaration. A token
# counts ONLY at a DECLARATION position — line-start (optionally indented) or just after the
# `·` slug-line separator — so a freeform H1 title or quoted prose that happens to contain
# "risk: high" / "autonomy: <x>" is never mistaken for a declaration (a title substring must
# not be able to fool the guard either way).
_RISK_HIGH_RE = re.compile(r"(?:^|·)[ \t]*risk:[ \t]*high\b", re.MULTILINE)
# persona-routes-depth: the header route line — the persona's lane proposal
# (`route: <full|fast|oneshot> · routed-by: <who> — <why>`), parsed at the
# freeze/re-cross which RECORDS it (measure-not-block; audit lints the record).
_ROUTE_LINE_RE = re.compile(r"(?m)^route:\s*(\S+)\s*·\s*routed-by:\s*(\S[^\n]*)$")
_ROUTE_LANES = ("full", "fast", "oneshot")


def _route_record(header: str) -> dict:
    """The header route proposal as a state record: {lane, by}. An absent or
    malformed line (unknown lane token) records lane "unrouted" with by=None —
    the freeze NEVER refuses on route (audit measures: route_unrecorded)."""
    m = _ROUTE_LINE_RE.search(header)
    if m and m.group(1) in _ROUTE_LANES:
        return {"lane": m.group(1), "by": m.group(2).strip()}
    return {"lane": "unrouted", "by": None}

# persona-task-kinds (ADD 2.0 M1): the header kind declaration — the task's slot in the
# closed constants.TASK_KINDS taxonomy, the join key persona performance is scored by.
# Same anchored line grammar family as route:/sensitivity: (a title/prose substring is
# never a declaration). Read LIVE at gate time for the route-outcome trace.
_TASK_KIND_RE = re.compile(r"(?m)^kind:[ \t]*([A-Za-z-]+)[ \t]*$")

def _task_kind(hdr: str):
    """The declared task kind from a PLAN.md header region, lowercased, or None when
    absent (measure-not-block: recorded verbatim; audit/quality lint the vocabulary).
    PURE — the engine never infers a kind."""
    m = _TASK_KIND_RE.search(hdr)
    return m.group(1).lower() if m else None

# sensitivity taxonomy (risk-sensitivity-taxonomy): the risk-CLASS the human declares in the
# TASK header at freeze — same anchored declaration grammar as risk:/autonomy: (line-start or
# `·`, value stops at whitespace/`<`/`#`/`|`), so a title/prose substring is never a declaration.
_SENSITIVITY_RE = re.compile(r"(?:^|·)[ \t]*sensitivity:[ \t]*([^\s<#|]+)", re.MULTILINE)

def _task_sensitivity(hdr: str, valid=None):
    """The declared sensitivity from a PLAN.md header region (HTML comments already stripped by
    _task_header). A member of `valid`, None when no `sensitivity:` line is present, or "?" when a
    REAL token outside `valid` was written. `valid` defaults to _SENSITIVITY_VALUES (the universal
    base — back-compat); callers that honor a project's GLOSSARY domain classes pass
    valid=_project_sensitivity_values(root) (sensitivity-glossary). PURE — the engine validates a
    human-declared token against the project's vocabulary, it never infers it (mirrors _autonomy_level)."""
    if valid is None:
        valid = _SENSITIVITY_VALUES
    m = _SENSITIVITY_RE.search(hdr)
    if not m:
        return None
    tok = m.group(1).strip().lower()
    return tok if tok in valid else "?"


# gate mode (ai-plan-verify-gate): the two-way DIRECTION-freeze declaration — same anchored
# declaration grammar as sensitivity:/autonomy: (line-start or `·`, value stops at whitespace/
# `<`/`#`/`|`), so a title/prose substring is never a declaration.
_GATE_MODE_RE = re.compile(r"(?:^|·)[ \t]*gate_mode:[ \t]*([^\s<#|]+)", re.MULTILINE)


def _task_gate_mode(hdr: str) -> str | None:
    """The declared gate mode from a PLAN.md header region (HTML comments already stripped by
    _task_header). A member of _GATE_MODES, None when no `gate_mode:` line is present (absent —
    every caller treats this as "human", the fail-closed default; a NEW trust-loosening capability
    never silently activates), or "?" when a REAL token outside _GATE_MODES was written. PURE —
    validates a human-declared token, never infers one (mirrors _task_sensitivity/_autonomy_level)."""
    m = _GATE_MODE_RE.search(hdr)
    if not m:
        return None
    tok = m.group(1).strip().lower()
    return tok if tok in _GATE_MODES else "?"


# fast-lane-skips: the AI-declared skip-set — same anchored declaration grammar as
# gate_mode:/sensitivity:/autonomy: (line-start or `·`, value stops at whitespace/`<`/`#`/`|`).
_SKIPS_LINE_RE = re.compile(r"(?:^|·)[ \t]*skips:[ \t]*([^\s<#|]+)", re.MULTILINE)
# phase-merge-specify: header tokens for phases that were MERGED away — a pre-merge
# declaration naming one is ignored with a note, never a die (old boards keep working).
_RETIRED_SKIP_TOKENS = frozenset({"scenarios", "observe"})


def _task_skip_set(hdr: str) -> tuple[frozenset[str], str | None]:
    """The declared skip-set from a PLAN.md header region (HTML comments already stripped by
    _task_header). No `skips:` line -> (frozenset(), None) — the universal, byte-identical
    default. A present line's captured token comma-split, every element a member of
    _SKIPPABLE_PHASES -> (frozenset(elements), None). ANY split element outside
    _SKIPPABLE_PHASES (a typo, another phase's name, an empty element from a double/trailing
    comma) -> (frozenset(), "skip_not_allowed") — the WHOLE declaration is discarded on any
    single bad element, never partially honored (mirrors _ai_freeze_allowed's "?" fail-closed
    philosophy, not _task_sensitivity's "None means absent, default safely" philosophy — a
    malformed CSV element is garbled, not absent). A RETIRED token (`scenarios`, merged into
    specify at phase-merge-specify) is filtered out, never bad — the pre-merge declaration is
    tolerated-and-ignored (cmd_advance prints the advisory note; this stays PURE). PURE."""
    m = _SKIPS_LINE_RE.search(hdr)
    if not m:
        return frozenset(), None
    toks = [t.strip() for t in m.group(1).split(",")]
    toks = [t for t in toks if t not in _RETIRED_SKIP_TOKENS]
    if not toks:
        return frozenset(), None
    bad = [t for t in toks if t not in _SKIPPABLE_PHASES]
    if bad:
        # skip-error-ergonomics M1: the error carries its own repair — the raw
        # declaration, the offending token(s), the COMPUTED allowed set, and the
        # fix — so an agent never trial-and-errors advance or greps this source.
        # The prefix stays `skip_not_allowed` (pinned by callers/tests); the
        # fail-closed whole-declaration discard is unchanged.
        allowed = ", ".join(sorted(_SKIPPABLE_PHASES))
        return frozenset(), (
            f"skip_not_allowed: `skips: {m.group(1)}` — "
            f"{', '.join(repr(t) for t in bad)} cannot be skipped; only "
            f"{allowed} may be skipped (fast/oneshot/benchmark lanes, with a "
            "stated Skip rationale). Correct or remove the `skips:` line in the "
            "PLAN.md header, then re-run add.py advance")
    return frozenset(toks), None


# fast-lane-skips: the §0 GROUND "Skip rationale:" clause extractor — deliberately simpler
# than _flag_well_formed's [part]-tag grammar (no "none material" escape hatch): an irreversible
# phase jump always needs a stated reason, or it never happens.
_SKIP_RATIONALE_LINE_RE = re.compile(r"^[ \t]*Skip rationale:[ \t]*(.*)$", re.MULTILINE)
_SKIP_RATIONALE_CLAUSE_RE = re.compile(r"^\s*(observe)\s*[-—:]\s*(.+)$")




# fast-lane-skips: the project-level benchmark-mode opt-in — mirrors
# _project_autonomy_token's idiom exactly (anchored declaration, HTML comments stripped,
# fail-SAFE default: a NEW ceremony-loosening capability never silently activates).
_BENCHMARK_MODE_RE = re.compile(r"(?:^|·)[ \t]*benchmark_mode:[ \t]*(true|false)",
                                 re.IGNORECASE | re.MULTILINE)


def _project_benchmark_mode(root: Path) -> bool:
    """Whether the project runs in benchmark mode (fast-lane-skips): every task in the project
    is skip-eligible without a per-task opt-in (the lane flags are retired). Fail-SAFE: `true` -> True;
    `false`, absent, an unreadable foundation, or any other token -> False. Read-only and PURE."""
    try:
        text = (root / "PROJECT.md").read_text(encoding="utf-8")
    except OSError:
        return False
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    m = _BENCHMARK_MODE_RE.search(text)
    return bool(m) and m.group(1).strip().lower() == "true"


def _skip_status_line(root: Path, state: dict, slug: str) -> str | None:
    """fast-lane-skips: the additive status/guide line — SHARED by cmd_status and cmd_guide so
    the wording never drifts across the two surfaces. Present-only: None (no line) unless the
    task is skip-eligible AND (a non-empty `skips:` declaration exists OR >=1 skip is already
    recorded) — byte-identical to today for every task without a skip declaration. A malformed
    declaration (skip_not_allowed) degrades to the empty-set reading here (a status line is
    read-only and must never raise; `advance` is the enforcement point)."""
    t = state["tasks"][slug]
    tokens, err = _task_skip_set(_task_header(root, slug))
    if err:
        tokens = frozenset()
    eligible = _skip_lane_eligible(t.get("fast") is True, t.get("oneshot") is True,
                                    _project_benchmark_mode(root))
    recorded = t.get("skips") or []
    if not eligible or not (tokens or recorded):
        return None
    csv = ",".join(p for p in _SKIPPABLE_PHASES if p in tokens)
    done = [p for p in _SKIPPABLE_PHASES if p in {e.get("phase") for e in recorded}]
    return (f"skips   : declared {csv or '(none)'} · skipped so far "
            f"{len(recorded)}/{len(tokens)} ({', '.join(done)})")


# sensitivity-glossary: a project EXTENDS the universal base with domain risk-classes declared in
# GLOSSARY.md's "## Sensitivity classes" section (the AI keeps it current per the skill guide). The
# base four stay method-universal (advisor-gate-relax keys off `mechanical`) — a project never
# REMOVES them. Read live like _project_autonomy (no state.json field). The first
# GLOSSARY reader in the engine; degrade-safe by construction (design-for-failure).
_SENS_CLASSES_HEADING_RE = re.compile(r"(?im)^##[ \t]+sensitivity[ \t]+classes\b.*$")
# a domain line is "- <token>: …" or "- <token> — …"; the token must START with a letter, so a
# placeholder ("- <token>: …") begins with "<" and never matches, and the ": "/"—" separator keeps
# a prose bullet from being read as a class. HTML comments are stripped FIRST (mirrors
# _project_autonomy) so a commented-out template example is never a declaration.
_SENS_CLASS_LINE_RE = re.compile(r"(?m)^[ \t]*-[ \t]+([A-Za-z][\w-]*)[ \t]*(?::|—)")

def _project_sensitivity_domain(root: Path) -> tuple:
    """Domain sensitivity tokens declared in GLOSSARY.md's "## Sensitivity classes" section,
    lowercased and deduped in document order. FAIL-SAFE: no GLOSSARY.md / no section / unreadable
    -> () (the caller always unions the base in, so the vocabulary is never empty)."""
    try:
        text = (root / "GLOSSARY.md").read_text(encoding="utf-8")
    except OSError:
        return ()
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)    # a commented example is never a declaration
    m = _SENS_CLASSES_HEADING_RE.search(text)
    if not m:
        return ()
    body = text[m.end():]
    nxt = re.search(r"(?m)^##[ \t]", body)        # stop at the next section heading
    if nxt:
        body = body[:nxt.start()]
    seen, out = set(), []
    for tok in (t.strip().lower() for t in _SENS_CLASS_LINE_RE.findall(body)):
        if tok and tok not in seen:
            seen.add(tok)
            out.append(tok)
    return tuple(out)

def _project_sensitivity_values(root: Path) -> tuple:
    """The full sensitivity vocabulary for a project: the universal base _SENSITIVITY_VALUES
    (always present, listed first) ∪ the project's GLOSSARY.md domain classes. Base-first, deduped."""
    out = list(_SENSITIVITY_VALUES)
    for tok in _project_sensitivity_domain(root):
        if tok not in out:
            out.append(tok)
    return tuple(out)

# the explicit 3-mode autonomy dial (task explicit-autonomy-dial): an ordered ladder
# manual < conservative < auto, declared as a per-task `autonomy:` header token.
# anchored to a DECLARATION position — line-start `autonomy:` OR the inline slug-line form
# `… · autonomy: conservative` (the `·`-preceded shape) — never a title/prose substring; the
# value stops at space/`<`/`#`/`|` so an unfilled `<manual | … >` placeholder captures nothing
# and reads as UNSET.

# kernel-trim (ADD 2.0 M5): the component:/produces:/consumes: header grammar died with the
# components pillar — a legacy header line is inert prose now, never parsed.


def _autonomy_lowered(hdr: str) -> bool:
    """True iff the declared rung is high-risk-safe (manual or conservative). A
    high-risk scope must be lowered to one of these; `auto` and UNSET are not."""
    return _autonomy_level(hdr) in ("manual", "conservative")


# advisor-gate-relax helpers: read the "### Advisor 3-lens verdict" SUB-SECTION
# of body6, not the whole §6, so the refute-read's Verdict/Residue lines are
# never mistaken for the advisor's fields.  Fail-safe: both return False when the
# advisor block is absent → the guard fires (conservative by design).

def _advisor_slice(body6: str) -> str:
    """Return the '### Advisor 3-lens verdict' sub-section text from §6 body.
    Returns '' when the block is absent (fail-safe)."""
    m = re.search(r"(?m)^### Advisor 3-lens verdict\b", body6)
    if not m:
        return ""
    nxt = re.search(r"(?m)^### ", body6[m.end():])
    end = m.end() + nxt.start() if nxt else len(body6)
    return body6[m.start():end]


def _advisor_verdict_is_pass(body6: str) -> bool:
    """True iff the Advisor 3-lens verdict sub-section declares Verdict: PASS…
    Scoped to the advisor block only — the §6 Refute-read Verdict line is excluded.
    Fail-safe: False when the advisor block is absent (guard fires)."""
    slc = _advisor_slice(body6)
    m = re.search(r"(?m)^Verdict:[ \t]*(\S+)", slc)
    return bool(m) and m.group(1).upper().startswith("PASS")


def _advisor_no_residue(body6: str) -> bool:
    """True iff the Advisor 3-lens verdict sub-section declares Residue: none.
    Fail-safe: False when the advisor block is absent (guard fires)."""
    slc = _advisor_slice(body6)
    m = re.search(r"(?m)^Residue:[ \t]*(\S+)", slc)
    return bool(m) and m.group(1).strip().lower() == "none"


# ai-plan-verify-gate helpers: read the "### AI-verify record" SUB-SECTION of raw3 (§3 body),
# mirroring _advisor_slice's heading-bounded-slice idiom exactly (same shape, different heading/
# section). Fail-safe: both return ''/False when the block is absent (the freeze guard fires).

def _ai_verify_slice(raw3: str) -> str:
    """Return the '### AI-verify record' sub-section text from §3 body.
    Returns '' when the block is absent (fail-safe)."""
    m = re.search(r"(?m)^### AI-verify record\b", raw3)
    if not m:
        return ""
    nxt = re.search(r"(?m)^### ", raw3[m.end():])
    end = m.end() + nxt.start() if nxt else len(raw3)
    return raw3[m.start():end]


def _ai_verify_checklist_complete(raw3: str) -> bool:
    """True iff the §3 'AI-verify record' sub-block is present, carries exactly its 4 checklist
    items all marked '- [x]', and 'Verified by:' has non-empty content. Engine-enforced precondition
    (mirrors _flag_well_formed's style) — not merely advisory prose. Fail-closed: False when the
    block is absent, has any unchecked item, or an empty 'Verified by:'."""
    slc = _ai_verify_slice(raw3)
    if not slc:
        return False
    items = re.findall(r"(?m)^\s*-\s*\[([ xX])\]", slc)
    if len(items) != 4 or not all(c.lower() == "x" for c in items):
        return False
    m = re.search(r"(?m)^\s*Verified by:[ \t]*(.+)$", slc)
    return bool(m and m.group(1).strip())


# step-spawn-hint (advisor-gated-autonomy): the engine's pinned terse copy of each phase
# guide's Advisor hook — one spawn idiom per phase. `done` is ABSENT (closed); the `plan`
# phase carries a design-sweep hint for DRAFTING the change plan even though its freeze is
# one human decision. Advisory ONLY — the engine never spawns; the line just NAMES the agent
# shape a parallel run would use at this step.
_SPAWN_HINTS = {
    "direction": "domain researcher + wide scenario sweep + change-plan design sweep + red-suite test-author",
    "build": "independent well-scoped batch",
    "verify": "earned-green refute-read",
}


def _spawn_hint_line(task: dict, autonomy: str) -> str | None:
    """PURE: the one-line per-step spawn hint for the ACTIVE task, or None. Suppressed when
    the autonomy level is `manual` (the human drives every step) or the phase has no idiom
    (contract/done). The tier reflects declared risk: a `risk: high` task earns `top`
    (your strongest agent), everything else `mid`. Never spawns, never mutates state."""
    phase = task.get("phase")
    if autonomy == "manual" or phase not in _SPAWN_HINTS:
        return None
    tier = "top" if task.get("risk") == "high" else "mid"
    return f"spawn hint: {phase} → {_SPAWN_HINTS[phase]} (tier: {tier})"


def _driver_stop(root: Path, state: dict, slug: str, phase: str) -> bool:
    """True iff a HUMAN owns the next step for `phase` under the effective autonomy — the
    SINGLE source the footer marker and the guide TEXT marker both render (task
    gate-owner-marker). Refines _phase_owner with the autonomy level at exactly ONE phase,
    verify:
        verify -> the human gates UNLESS the run may auto-gate (effective autonomy == auto)
        else   -> the structural owner stops (owner != "ai"), independent of the level
    The frozen machine-state-json JSON `stop` keeps its own structural value (Option F);
    this resolver feeds ONLY the human-facing footer + guide TEXT. _phase_owner still
    _die("unmapped_phase") on a bad phase — the marker invents no default."""
    if phase == "verify":
        return _effective_autonomy(root, state, slug) != "auto"
    return _phase_owner(phase) != "ai"


def _driver_marker(stop: bool) -> str:
    """Render _driver_stop as the reserved-slot word (one leading space each) — the exact
    strings next-footer-engine reserved: ` [human gate]` (a human owns it) / ` [you drive]`."""
    return " [human gate]" if stop else " [you drive]"


def _gate_explain(root: Path, state: dict, slug: str) -> None:
    """gate-explain (method-ergonomics): compose the gate decision from the SAME predicates
    cmd_gate enforces, as a READ-ONLY answer — the agent asks instead of recalling run.md.
    PURE: prints, writes nothing."""
    hdr = _task_header(root, slug)
    body6 = _raw_phase_bodies(root, slug).get(6, "")
    from add_engine.autonomy import _autonomy_level
    level = _autonomy_level(hdr) or "auto"
    high = bool(_RISK_HIGH_RE.search(hdr))
    sens = _task_sensitivity(hdr, valid=_project_sensitivity_values(root)) or "unset"
    adv_pass = _advisor_verdict_is_pass(body6)
    adv_clean = adv_pass and _advisor_no_residue(body6)
    relaxed = sens == "mechanical" and adv_clean
    print(f"gate-explain {slug}")
    print(f"  phase: {state['tasks'][slug].get('phase', '?')}")
    print(f"  autonomy: {level} · risk: {'high' if high else 'unset/low'} · sensitivity: {sens}")
    print(f"  advisor 3-lens: {'PASS, residue none' if adv_clean else ('PASS with residue' if adv_pass else 'unrecorded or non-PASS')}")
    print(f"  advisor-gate-relax: {'applies (mechanical + clean advisor verdict)' if relaxed else 'not applicable'}")
    gate_mode = _task_gate_mode(hdr)
    if gate_mode == "ai-plan-verify":
        ai_ok, ai_code = _ai_freeze_allowed(gate_mode, _task_sensitivity(hdr, valid=_project_sensitivity_values(root)), level)
        print(f"  ai-plan-verify-gate: {'allowed' if ai_ok else f'blocked ({ai_code})'}")
    # fast-lane-skips: a declared (non-empty) skips: outcome is explained REGARDLESS of
    # eligibility — that is the whole point (this is where a BLOCKED declaration surfaces).
    skip_tokens, skip_err = _task_skip_set(hdr)
    if not skip_err and skip_tokens:
        skip_eligible = _skip_lane_eligible(
            state["tasks"][slug].get("fast") is True,
            state["tasks"][slug].get("oneshot") is True,
            _project_benchmark_mode(root))
        skip_ok, skip_code = _skip_set_allowed(skip_tokens, skip_eligible)
        print(f"  skip-set: {'allowed' if skip_ok else f'blocked ({skip_code})'}")
    if _autonomy_lowered(hdr):
        print("  path: HUMAN — the lowered autonomy level puts a person at this verify gate")
    elif high and not relaxed:
        print("  path: REFUSED at completion (unguarded_high_risk_auto) — lower the autonomy "
              "level (`add.py autonomy set conservative`), or for a mechanical task record a "
              "clean Advisor 3-lens verdict")
    elif relaxed:
        print("  path: RELAX — mechanical sensitivity + advisor PASS/none may complete "
              "without a lowered level (advisor-gate-relax)")
    else:
        print("  path: AUTO — may auto-PASS on complete evidence (tests green · no tamper · "
              "loops dry · deep check + refute-read + 3-lens recorded) with no residue")
    print("  floor: a security finding is always HARD-STOP — never auto-passed, on every path")


def _append_route_trace(root: Path, state: dict, slug: str, outcome: str) -> None:
    """persona-perf telemetry (ADD 2.0 M1 persona-core): ONE JSON line per recorded gate
    outcome, appended to `.add/traces/route-outcomes.jsonl` — the evidence stream the
    persona scoreboard and the GEPA fold read. Engine-derivable fields only; degrade-safe:
    state is the source of truth, the trace is telemetry — a failed write NEVER blocks the
    verdict (call sits after save_state)."""
    try:
        t = state["tasks"][slug]
        route = t.get("route") or {}
        lane, by = route.get("lane"), route.get("by")
        if lane in (None, "unrouted") and t.get("oneshot"):
            lane = "oneshot"                         # effective lane: the durable marker
        m = re.search(r"persona:([\w-]+)", by or "")
        try:
            kind = _task_kind(_task_header(root, slug))
        except Exception:
            kind = None                              # a missing PLAN.md never blocks
        age = None
        created = t.get("created")
        if created:
            try:
                age = round((datetime.fromisoformat(_now())
                             - datetime.fromisoformat(created)).total_seconds() / 3600, 2)
            except ValueError:
                pass
        line = {
            "ts": _now(), "task": slug, "milestone": t.get("milestone"),
            "kind": kind, "lane": lane, "routed_by": by,
            "persona": m.group(1) if m else None, "outcome": outcome,
            "heals": (t.get("heal") or {}).get("attempts", 0),
            "rounds": (t.get("rounds") or {}).get("count", 0),   # visible verify->build return trips
            "recross": bool(t.get("recross")), "age_hours": age,
            "target_hit": t.get("target_hit"),          # the §3 Target judgment (plan-core)
            "actor": (t.get("gate_actor") or {}).get("name"),
        }
        tdir = root / "traces"
        tdir.mkdir(parents=True, exist_ok=True)
        with (tdir / "route-outcomes.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(line, ensure_ascii=False) + "\n")
    except OSError:
        pass


def cmd_gate(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    if getattr(args, "explain", False):
        # slug may have landed in the outcome slot (`gate --explain <slug>`)
        cand = args.slug or (args.outcome if args.outcome not in GATES else None)
        _gate_explain(root, state, _resolve_task(state, cand))
        return
    slug = _resolve_task(state, args.slug)
    # build-boundary gate: no verdict may be recorded before the setup is locked.
    if not _setup_locked(state):
        _die("setup_unlocked: lock the foundation first — add.py lock")
    if args.outcome not in GATES:
        _die(f"outcome must be one of: {', '.join(GATES)}")
    # plan-core (ADD 2.0 M2): the §3 Target's judgment — validated BEFORE any write so a
    # typo never half-records a verdict. Optional (absence is conformant, never inferred).
    _thit = getattr(args, "target_hit", None)
    if _thit is not None and _thit not in ("yes", "partial", "no"):
        _die(f"target_hit_invalid: --target-hit must be yes|partial|no (got '{_thit}')")
    # Completing outcomes (PASS, RISK-ACCEPTED) are the VERIFY step's verdict, so they
    # share the verify-phase guard — no silent skips (principle 7). HARD-STOP stays
    # recordable from any phase (a security finding is always HARD-STOP). The
    # deliberate, logged override is `add.py phase verify <slug>`.
    completing = args.outcome in ("PASS", "RISK-ACCEPTED")
    if completing:
        current = state["tasks"][slug]["phase"]
        # compound-ticks: a completing verdict at BUILD auto-crosses build->verify in
        # the same call (the tick between them is pure — no work happens on it), then
        # runs every completion check below unchanged. Phases before build keep their
        # refusal verbatim; HARD-STOP never reaches this branch (recordable anywhere).
        if current == "build":
            state["tasks"][slug]["phase"] = "verify"
            state["tasks"][slug]["updated"] = _now()
            save_state(root, state)                       # durable state FIRST
            _sync_task_marker(root, slug, "verify")       # then the PLAN.md mirror
            print(f"crossed build -> verify (compound tick) — recording {args.outcome}")
            current = "verify"
        if _phase_index(current) < _phase_index("verify"):
            code = ("gate_pass_before_verify" if args.outcome == "PASS"
                    else "gate_risk_accepted_before_verify")
            _die(f"{code}: task '{slug}' is at '{current}'; reach the verify phase "
                 f"first (or `add.py phase verify {slug}` to override)")
        # the mechanized high-risk guard: an unguarded high-risk header refuses
        # COMPLETION (PASS / RISK-ACCEPTED) until the dial is lowered and a human
        # owns the gate. HARD-STOP is never blocked — stopping is always allowed.
        # advisor-gate-relax: a mechanical task whose Advisor 3-lens verdict shows
        # PASS + Residue: none is the one exception — it may auto-complete even
        # without a lowered dial. Only sensitivity:"mechanical" qualifies; security/
        # data/architecture never relax; an absent advisor block is fail-safe False.
        hdr = _task_header(root, slug)
        body6 = _raw_phase_bodies(root, slug).get(6, "")
        _relaxed = (_task_sensitivity(hdr) == "mechanical"
                    and _advisor_verdict_is_pass(body6)
                    and _advisor_no_residue(body6))
        if _RISK_HIGH_RE.search(hdr) and not _autonomy_lowered(hdr) and not _relaxed:
            _die(f"unguarded_high_risk_auto: task '{slug}' declares risk: high "
                 "without a lowered autonomy level — run `add.py autonomy set conservative` "
                 "(or manual); a human must own a high-risk gate (run.md guard)")
        # tamper tripwire (verify-integrity): the method's first mechanical cheat
        # block. A completing outcome is refused if the red suite or the frozen §3
        # changed since the tests->build snapshot. Placed BEFORE the waiver write so
        # a tamper finding is never launderable through RISK-ACCEPTED.
        _tamper_guard(root, state, slug)
        # §5 scope gate (build-scope-lock): touched ⊆ declared, or a named refusal —
        # same placement discipline as the tripwire (before the waiver, never on HARD-STOP).
        _scope_guard(root, state, slug)
    if args.outcome == "RISK-ACCEPTED":
        # A waiver must be SIGNED: owner, ticket, expiry (glossary). Stored in state
        # so a later `check` can read/expire it. Refuse a partial waiver outright.
        missing = [f for f in ("owner", "ticket", "expires") if not getattr(args, f)]
        if missing:
            _die("waiver_incomplete: RISK-ACCEPTED is a signed waiver; supply "
                 + ", ".join("--" + m for m in missing))
        state["tasks"][slug]["waiver"] = {
            "owner": args.owner, "ticket": args.ticket, "expires": args.expires,
        }
    if completing:
        state["tasks"][slug]["phase"] = "done"
    state["tasks"][slug]["gate"] = args.outcome
    if _thit is not None:
        state["tasks"][slug]["target_hit"] = _thit     # the §3 Target judgment (plan-core)
    state["tasks"][slug]["gate_actor"] = identity._actor_stamp(state)   # WHO recorded the verdict (every outcome)
    state["tasks"][slug]["updated"] = _now()
    save_state(root, state)                                # F12: durable state FIRST (source of truth) — may _die
    _append_route_trace(root, state, slug, args.outcome)   # persona-perf telemetry — degrade-safe, never blocks
    if completing:
        _sync_task_marker(root, slug, "done")             # then mirror the phase into PLAN.md — no split-brain
    _stamp_gate_record(root, state, slug, args.outcome)   # mirror the verdict into §6 (Finding C)
    _stamp_adr_record(root, state, slug)                  # adr-at-observe: harvest §7 Decisions (ADR) — AFTER §6 is mirrored
    if completing:                                         # strip-scaffold-at-done: tidy the now-closed
        _tf = root / "tasks" / slug / "PLAN.md"           # PLAN.md LAST (after the stampers) — drop the
        try:                                              # live-phase `<!-- -->` comments; fences untouched.
            _tt = _tf.read_text(encoding="utf-8")
            _st = _strip_live_scaffold(_tt)
            if _st != _tt:
                _atomic_write(_tf, _st)
        except OSError:
            pass                                          # degrade-safe — the verdict is already in state
    print(f"task '{slug}' gate -> {args.outcome}")
    if completing:
        # phase-merge-verify: gate/completion is the ONE seam that reads a vestigial
        # `skips:` header (the grammar is retired — no crossing runs skip logic).
        if _SKIPS_LINE_RE.search(_task_header(root, slug)):
            print("  note: the skip grammar is retired — no phase can be skipped "
                  "(six-phase-loop); the `skips:` declaration is ignored")
        print("  note: record what to watch + this loop's lessons in §7, and file each "
              "into its living spec: add.py delta-append <dd> \"<lesson>\"")
    # the engine-sourced next step (next-footer-engine): a completing gate hands off to the
    # state arm; HARD-STOP routes to "resolve HARD-STOP …" — converging the old bespoke line.
    print(_next_footer(root, state))


# the autonomy level as a first-class verb (task autonomy-command): autonomy was the ONLY mutable,
# security-relevant task/project token WITHOUT a CLI verb — so an agent under `auto`, applying the
# correct "first-class state has a command" model, hallucinated `add.py autonomy` and derailed.
# `show` reads the resolved level; `set` is the FIRST writer of the header token — idempotent (one
# declaration line, trailing comment preserved, NEVER appended), with the raise + risk:high guards
# enforced BEFORE the write. state.json is untouched — autonomy stays a header token.
_AUTONOMY_ORDER = {lvl: i for i, lvl in enumerate(_AUTONOMY_LEVELS)}   # manual(0) < conservative(1) < auto(2)


def _autonomy_decl_line(text: str, level: str) -> str:
    """Rewrite the SINGLE `autonomy:` declaration line to `level`, PRESERVING its trailing comment,
    idempotently (replace in place, count=1 — never a second line). If absent, insert it: after the
    `slug:` line for a task header, else after a leading `#` heading (PROJECT.md), else prepend. PURE
    on the text; the caller does the atomic write."""
    pat = re.compile(r"(?m)^(autonomy:[ \t]*)[^\s<#|]+(.*)$")
    if pat.search(text):
        return pat.sub(lambda m: f"{m.group(1)}{level}{m.group(2)}", text, count=1)
    if re.search(r"(?m)^slug:", text):
        return re.sub(r"(?m)^(slug:.*)$", r"\1\nautonomy: " + level, text, count=1)
    lines = text.splitlines(keepends=True)
    if lines and lines[0].lstrip().startswith("#"):
        return lines[0] + f"autonomy: {level}\n" + "".join(lines[1:])
    return f"autonomy: {level}\n" + text


def _guard_autonomy_raise(current: str, target: str, yes: bool) -> None:
    """RAISING the level toward `auto` is a human-owned trust escalation (run.md: the AI may LOWER
    freely — RECOMMEND-only — but RAISING needs a human). Refuse a raise unless --yes confirms it."""
    if _AUTONOMY_ORDER.get(target, -1) > _AUTONOMY_ORDER.get(current, -1) and not yes:
        _die(f"autonomy_raise_unconfirmed: raising autonomy {current} -> {target} is a human-owned "
             "trust escalation (the AI may LOWER freely; RAISING needs a human) — pass --yes to confirm")


def _print_autonomy(root: Path, state: dict, slug: str) -> None:
    """The read-only level view: declared · effective (fallback-resolved) · project default · the
    verify-gate owner under it (the SAME _driver_stop the footer/guide render). Writes nothing."""
    declared = _autonomy_level(_task_header(root, slug))
    stop = _driver_stop(root, state, slug, "verify")
    print(f"task        : {slug}")
    print(f"declared    : {declared if declared in _AUTONOMY_LEVELS else 'unset'}")
    print(f"effective   : {_effective_autonomy(root, state, slug)}")
    print(f"project     : {_project_autonomy(root)}")
    print(f"verify gate : {'human gate' if stop else 'you drive'}")


def cmd_autonomy(args: argparse.Namespace) -> None:
    """show / set the autonomy level — the verify-gate owner (task autonomy-command)."""
    root = _require_root()                                   # reused -> "no .add/ project found …"
    state = load_state(root)
    if (getattr(args, "action", None) or "show") == "show":
        _print_autonomy(root, state, _resolve_task(state, args.a1))   # reused -> "unknown task '<slug>'"
        return
    # action == "set"
    level = args.a1
    if level not in _AUTONOMY_LEVELS:
        _die("autonomy_level_invalid: level must be one of "
             f"{', '.join(_AUTONOMY_LEVELS)} (got {level!r})")
    if getattr(args, "project", False):
        target = root / "PROJECT.md"
        _guard_autonomy_raise(_project_autonomy(root), level, getattr(args, "yes", False))
        _atomic_write(target, _autonomy_decl_line(target.read_text(encoding="utf-8"), level))
        print(f"project autonomy -> {level}")
        return
    slug = _resolve_task(state, args.a2)                     # reused -> "unknown task '<slug>'"
    task_md = root / "tasks" / slug / "PLAN.md"
    if _RISK_HIGH_RE.search(_task_header(root, slug)) and level not in ("manual", "conservative"):
        _die(f"unguarded_high_risk_auto: task '{slug}' declares risk: high — autonomy must stay "
             f"lowered (manual|conservative); refusing '{level}' (a human must own a high-risk gate)")
    _guard_autonomy_raise(_effective_autonomy(root, state, slug), level, getattr(args, "yes", False))
    _atomic_write(task_md, _autonomy_decl_line(task_md.read_text(encoding="utf-8"), level))
    print(f"task '{slug}' autonomy -> {level}")
    _print_autonomy(root, state, slug)






def cmd_todo(args: argparse.Namespace) -> None:
    """Capture / list / close a lightweight backlog todo (task: todo-capture).

    A todo is a JOTTED IDEA, not a task — it carries no spec/contract/gate. It lets you
    record an intent without sizing it. Promote one to a real task with
    `add.py new-task <slug>` when you decide to build it. Stored in state["todos"]
    as {id (1-based = max+1), text, created, status:"open"|"done"}.
    """
    root = _require_root()                                   # reused -> "no .add/ project found …"
    state = load_state(root)
    todos = state.get("todos")
    if not isinstance(todos, list):                          # absent / corrupt -> fresh list (drift-safe)
        todos = state["todos"] = []
    done_id = getattr(args, "done", None)
    if done_id is not None:                                  # --done <id> : close an OPEN todo
        for t in todos:
            if isinstance(t, dict) and t.get("id") == done_id and t.get("status") == "open":
                t["status"] = "done"
                save_state(root, state)
                print(f"todo #{done_id} done")
                return
        _die(f"todo_unknown: no open todo #{done_id}")
    if args.text is not None:                                # capture attempt (text positional present)
        text = args.text.strip()
        if not text:
            _die("todo_empty: a todo needs text")
        new_id = max((t.get("id", 0) for t in todos if isinstance(t, dict)), default=0) + 1
        todos.append({"id": new_id, "text": text, "created": _now(), "status": "open"})
        save_state(root, state)
        print(f"captured todo #{new_id}: {text}")
        return
    open_todos = [t for t in todos if isinstance(t, dict) and t.get("status") == "open"]
    if not open_todos:                                       # bare `todo` -> list OPEN todos
        print("no open todos")
        return
    for t in open_todos:
        print(f"#{t.get('id')}  {t.get('text')}")


def cmd_reopen(args: argparse.Namespace) -> None:
    """Return an already-`done` task to an earlier phase with a never-silent record.

    The flow already permits backward correction (book ch02: "any phase may return
    to an earlier one"); `done` is terminal EXCEPT via this recorded action. reopen
    sets the phase back, resets the gate to "none" (the task must re-earn its
    verdict), and appends an append-only `reopens` entry recording WHY. A done task
    done via RISK-ACCEPTED carries a live `waiver`; reopen records it inside the entry
    (prior_gate / prior_waiver) and drops the live key, so no signed waiver lingers
    without a verdict. Judgement of WHEN to reopen stays the resolver's; the engine
    only enforces the recorded, coherent transition.
    """
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    t = state["tasks"][slug]
    if t.get("phase") != "done":
        _die(f"reopen_not_done: task '{slug}' is at '{t.get('phase')}', not done — "
             "backward correction inside a live run is `add.py phase` / HARD-STOP, not reopen")
    reason = (args.reason or "").strip()
    if not reason:
        _die("reopen_reason_required: reopen records WHY — supply a non-empty --reason")
    target = LEGACY_PHASES.get(args.to, args.to)   # phase-collapse-3: legacy targets map home
    if target not in PHASES[:-1]:        # direction..verify; never "done", never an unknown name
        _die(f"reopen_target_invalid: --to must be one of {', '.join(PHASES[:-1])} (got {target!r})")
    now = _now()
    entry = {"from": "done", "to": target, "reason": reason, "at": now,
             "prior_gate": t.get("gate", "none")}
    if t.get("waiver"):                 # void verdict's waiver -> history, drop the live key
        entry["prior_waiver"] = t.pop("waiver")
    t.setdefault("reopens", []).append(entry)
    t["phase"] = target
    t["gate"] = "none"
    t["updated"] = now
    save_state(root, state)                # F12: durable state FIRST (source of truth) — may _die
    _sync_task_marker(root, slug, target)  # then mirror into PLAN.md (best-effort) — no split-brain
    print(f"task '{slug}' reopened: done -> {target} (reason recorded); gate reset to none")
    print(_next_footer(root, state))


def cmd_heal(args: argparse.Namespace) -> None:
    """Report a CONFIRMED semantic cheat — an earned-green failure the adversarial refute-read
    found — and enter the bounded self-heal loop (heal-then-escalate). The judgment rubric (the
    specific cheats and how to spot them) lives in 6-verify.md, never the engine.

    The engine cannot SEE a judgment cheat — this is the agent's honest report (honor-system,
    necessary-not-sufficient; the human verify gate stays the real backstop, and the engine
    never spawns the refute-read). It routes through the SAME _heal_or_escalate as the
    mechanical tripwire: return-to-build for an honest redo (≤HEAL_CAP), then a HARD-STOP
    escalation. The refute-read is a verify-gate activity, so the task must be at verify."""
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    reason = (args.reason or "").strip()
    if not reason:
        _die("heal_reason_required: heal records the refute-read finding — supply a "
             "non-empty --reason (never a silent loop)")
    phase = state["tasks"][slug].get("phase")
    if phase != "verify":
        _die(f"heal_not_at_verify: task '{slug}' is at '{phase}', not verify — the "
             "adversarial refute-read is a verify-gate activity; build then advance to "
             "verify before reporting a cheat")
    _heal_or_escalate(root, state, slug, reason="refute-read:" + reason, source="refute-read")


def cmd_lock(args: argparse.Namespace) -> None:
    """The human baseline approval: freeze the autonomously-drafted setup in ONE atomic write.

    Setup-level analog of the contract freeze — the only new human action onboarding
    needs. `add.py lock` is judgment-free (it records the signature; it does NOT inspect
    the artifacts): the human's signature IS the gate."""
    root = _require_root()
    state = load_state(root)
    # idempotent-guarded: the predicate also treats a grandfathered (no "setup" key)
    # project as already locked. first-call-ergonomics M2: an EXACT already-locked
    # retry without --force is a READ-only exit-0 no-op (never a hard error) —
    # --force below is the only path that ever re-writes state.
    if _setup_locked(state) and not args.force:
        print("already locked (use --force to re-lock)")
        print(_next_footer(root, state))
        return
    # parse layers BEFORE any write so an invalid request never half-locks (design-for-failure).
    raw = args.layers if args.layers is not None else "foundation,scope,contract"
    layers = [s.strip() for s in raw.split(",") if s.strip()]
    if not layers:
        _die("layers_invalid: --layers must name at least one lock layer")
    who = args.by or getpass.getuser()
    when = _now()
    # ONE atomic write — no partial lock state.
    state["setup"] = {"locked": True, "locked_at": when, "locked_by": who, "layers": layers,
                      "actor": identity._actor_stamp(state)}   # structured actor alongside the free-text locked_by
    save_state(root, state)
    if getattr(args, "json", False):
        print(json.dumps(
            {"locked": True, "locked_at": when, "locked_by": who, "layers": layers},
            separators=(",", ":")))
    else:
        print(f"locked setup ({','.join(layers)}) by {who} @ {when}")
        print(_next_footer(root, state))










def cmd_stage(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    if args.stage not in STAGES:
        _die(f"stage must be one of: {', '.join(STAGES)}")
    # v22 stage-graduation guard: the →production TRANSITION refuses without a roadmap — a tally
    # check (≥1 production milestone exists), never a readiness judgment. Scoped to production
    # ONLY; every other flip is the existing bare flip, byte-unchanged. --force overrides
    # (precedent: lock --force). The flip is the FINAL, human-confirmed-roadmap step.
    forced = getattr(args, "force", False)
    bypassing = False
    if args.stage == "production":
        roadmap = _has_production_roadmap(state)
        if not roadmap and not forced:
            _die("stage_no_roadmap: no production milestone drafted. Draft ≥1 "
                 "(new-milestone --stage production), or use --force to override.")
        bypassing = forced and not roadmap
    state["stage"] = args.stage
    save_state(root, state)
    print(f"project stage -> {args.stage}")
    if bypassing:
        print("(--force: bypassed roadmap check — no production milestone drafted)")
    print(_next_footer(root, state))


def _done_resume(root: Path, state: dict, slug: str) -> tuple[str, str, str]:
    """At a DONE task, what should the agent do NEXT? Classify from the task's
    milestone exit-criteria tally (_exit_criteria) so the orient surfaces (status,
    guide) STEER into the loop instead of always saying "start the next feature".

    Returns (headline, next_step, chapter) where chapter is a docs/ filename:
      LOOP-JUNCTURE  total>0 and met<total -> name the unmet goal, route to the loop
      GOAL-MET       total>0 and met==total -> point at milestone-done
      PLAIN          no criteria / no milestone / any read error -> today's "next feature"
    PURE and fail-closed (design-for-failure): a missing milestone or unreadable
    MILESTONE.md degrades to PLAIN — it never raises into a status/guide print path."""
    PLAIN = ("this task is done",
             "start the next feature -> add.py new-task <slug>",
             "02-the-flow.md")
    try:
        ms = ((state.get("tasks") or {}).get(slug) or {}).get("milestone")
        if not ms:
            return PLAIN
        met, total = _exit_criteria(root, ms)
    except Exception:                       # noqa: BLE001 — never break orient output
        return PLAIN
    if total > 0 and met < total:
        return (f"milestone '{ms}' goal not met ({met}/{total} exit criteria)",
                "propose the next tasks from open deltas / the unscaffolded plan -> add.py deltas",
                "09-the-loop.md")
    if total > 0 and met == total:
        return (f"milestone '{ms}' goal met ({met}/{total})",
                f"close it -> add.py milestone-done {ms}",
                "09-the-loop.md")
    return PLAIN


_STATUS_PAGE_SIZE = 10  # status-pagination: default cap on milestones:/tasks: lists; --all lifts it


def _sorted_by_updated(items: dict) -> list:
    """Return `items.items()` sorted by each record's `updated` timestamp, newest first.
    Read/serialization-time only — never mutates the caller's dict or state.json order."""
    return sorted(items.items(), key=lambda kv: kv[1].get("updated") or "", reverse=True)


def _ancestor_note() -> str | None:
    """A one-line stderr note when `status` resolved an ANCESTOR project — cwd has
    no .add/ of its own but find_root walked up to one. Hands the exact `init` to
    scope a project HERE (the _require_root skip-error precedent). None (silent) when
    cwd owns a project or no project is reachable (the init flow owns that message)."""
    cwd = Path.cwd().resolve()
    if (cwd / ROOT_DIRNAME / STATE_FILE).exists():
        return None
    root = find_root()
    if root is None:
        return None
    return (f"note: no .add/ here — using the ancestor project at {root.parent}; "
            'run `add.py init --name "<project>" --stage <prototype|poc|mvp|production>` '
            "to scope a project to this directory")


_FOUNDATION_CORE = ("## Domain", "## Spec")   # near-always-needed direction context — kept full
_FOUNDATION_DECISIONS_HEAD = "## Key Decisions"
_FOUNDATION_DECISIONS_KEEP = 3               # newest-first: the recent head at orient; stale tail on demand


def _foundation_selector(heading: str) -> str:
    """A short, stable selector for a `## ` heading — the title phrase before the first
    qualifier punctuation. `## Users (UDD) — …` → `Users`; `## Key Decisions (…` → `Key
    Decisions`. Used for both the pull hint and matching a `--foundation <SECTION>` query."""
    t = heading[3:].strip()
    for cut in ("(", " — ", " / ", " - "):
        i = t.find(cut)
        if i != -1:
            t = t[:i]
    return t.strip()


def _foundation_pull(sel: str) -> str:
    return f'_(collapsed — pull: `add.py status --foundation "{sel}"`)_\n\n'


def _foundation_skeleton(text: str) -> str:
    """The progressive-disclosure foundation MAP for orientation (foundation-slice,
    context/turn lever): PROJECT.md is a cross-milestone read at orient and re-read every
    turn. Disclose the SKELETON — the preamble (title + `invariants:`, the run/entry
    contracts that bind EVERY task) + Domain + Spec IN FULL (near-always-needed direction),
    every OTHER section COLLAPSED to its heading + an on-demand `--foundation "<section>"`
    pull; the newest Key Decisions kept, the stale tail pulled. The agent fleshes out a
    section only when its phase needs it — the same progressive disclosure as the phase
    guides. PURE. Fail-open: a foundation with no `## ` sections returns verbatim (never
    blank it). Invariants are never collapsed, so the contracts that bind every task always
    survive the map."""
    lines = text.splitlines(keepends=True)
    heads = [i for i, l in enumerate(lines) if l.startswith("## ")]
    if not heads:
        return text
    out = list(lines[:heads[0]])                       # preamble — invariants live here
    bounds = heads + [len(lines)]
    for k, start in enumerate(heads):
        head = lines[start]
        body = lines[start:bounds[k + 1]]
        if head.startswith(_FOUNDATION_CORE):
            out.extend(body)                            # Domain · Spec — full
        elif head.startswith(_FOUNDATION_DECISIONS_HEAD):
            out.append(head)
            kept = [l for l in body[1:] if l.strip()][:_FOUNDATION_DECISIONS_KEEP]
            out.extend(kept)
            out.append(f'_(+tail — pull: `add.py status --foundation "{_foundation_selector(head)}"`)_\n\n')
        else:
            out.append(head)                            # heading is the signpost; body on demand
            out.append(_foundation_pull(_foundation_selector(head)))
    return "".join(out)


def _foundation_pick(text: str, query: str):
    """Return ONE section (heading + body, FULL) whose heading matches `query`
    (case-insensitive substring of the heading or its selector), or None if no match —
    the on-demand flesh for the progressive `--foundation` map."""
    lines = text.splitlines(keepends=True)
    heads = [i for i, l in enumerate(lines) if l.startswith("## ")]
    bounds = heads + [len(lines)]
    q = query.strip().lower()
    for k, start in enumerate(heads):
        head = lines[start]
        if q in head.lower() or q in _foundation_selector(head).lower():
            return "".join(lines[start:bounds[k + 1]])
    return None


def cmd_status(args: argparse.Namespace) -> None:
    fnd = getattr(args, "foundation", None)
    if fnd is not None:
        # --foundation (foundation-slice, progressive disclosure): bare prints the MAP
        # (invariants + Domain + Spec full, other sections collapsed to a pull hint); a
        # SECTION value pulls that one section body on demand; --all prints the whole
        # foundation. Raw body only (no banner/footer), mirroring --section. Fail-closed
        # on a missing foundation — never a silent empty read.
        root = _require_root()
        pmd = root / "PROJECT.md"
        if not pmd.exists():
            _die("foundation_missing: no .add/PROJECT.md to read")
        text = pmd.read_text(encoding="utf-8")
        if getattr(args, "all", False):
            print(text, end="")
        elif fnd == "":
            print(_foundation_skeleton(text), end="")
        else:
            body = _foundation_pick(text, fnd)
            if body is None:
                names = ", ".join(_foundation_selector(l) for l in text.splitlines()
                                  if l.startswith("## ")) or "(none)"
                _die(f"foundation_section_unknown: '{fnd}' — sections: {names}")
            print(body, end="")
        return
    _section = getattr(args, "section", None)
    if _section is not None:
        # --section (progressive-task-context): print ONE raw §body of the
        # active task — the agent mid-task reads tens of lines, not the whole
        # growing PLAN.md. Raw body only: no banner, no footer. Wins over
        # --brief/--json when combined (documented precedence, not an error).
        root = _require_root()
        state = load_state(root)
        slug = _resolve_task(state, None)
        tok = _section.strip().lower()
        if tok.isdigit() and int(tok) <= 7:
            n = int(tok)
        elif tok in PHASES and tok != "done":
            n = _PHASE_SECTIONS[tok][0]   # phase → its PRIMARY §-number via the explicit
                                          # table (never ordinal math); digits 0-7 above
                                          # still reach any section directly (§2, §7)
        else:
            _die(f"section_unknown: '{_section}' is not 0-7 or a phase name "
                 f"({', '.join(p for p in PHASES if p != 'done')})")
        bodies = _raw_phase_bodies(root, slug)
        if n not in bodies:
            _die(f"section_missing: no '## {n} ·' heading in tasks/{slug}/PLAN.md")
        print(bodies[n])
        return
    if getattr(args, "brief", False):
        # --brief (engine-batch-ops): the resume essentials ONLY — the agent
        # re-orienting mid-task already holds the foundation in context; the
        # full dump is a per-turn token tax. Plain `status` is unchanged.
        root = _require_root()
        state = load_state(root)
        active = _active_task(state)
        if active and active in (state.get("tasks") or {}):
            print(f"task: {active} · phase: {state['tasks'][active].get('phase', '?')}")
        else:
            print("no active task")
        print(_next_footer(root, state))
        return
    show_all = getattr(args, "all", False)
    if getattr(args, "json", False):
        root, state = _load_state_for_json()
        tasks = state.get("tasks") or {}
        task_slug = getattr(args, "task", None)
        if task_slug:
            t = tasks.get(task_slug)
            if t is None:
                _die("unknown_task")
            print(json.dumps({"slug": task_slug, "phase": t.get("phase"), "gate": t.get("gate"),
                               "milestone": t.get("milestone"),
                               "owner": t.get("owner"), "assignee": t.get("assignee"),
                               "bundle": _phase_bundle(t.get("phase"))}))
            return
        milestones = state.get("milestones") or {}
        sorted_ms = _sorted_by_updated(milestones)
        page_ms = sorted_ms if show_all else sorted_ms[:_STATUS_PAGE_SIZE]
        ms_list = []
        for mslug, m in page_ms:
            members = [t for t in tasks.values() if t.get("milestone") == mslug]
            ms_list.append({"slug": mslug, "status": m.get("status", "active"),
                            "done": sum(1 for t in members if _task_done(t)),
                            "total": len(members),
                            "owner": m.get("owner"), "assignee": m.get("assignee")})
        sorted_tasks = _sorted_by_updated(tasks)
        page_tasks = sorted_tasks if show_all else sorted_tasks[:_STATUS_PAGE_SIZE]
        print(json.dumps({
            "project": state.get("project"), "stage": state.get("stage"),
            "actor": identity._whoami(state),
            "active_task": _active_task(state),
            "active_milestones": list(state.get("active_milestones") or []),
            "active_tasks": dict(state.get("active_tasks") or {}),
            "milestones": ms_list,
            "milestones_total": len(milestones),
            "tasks": [{"slug": s, "phase": t.get("phase"), "gate": t.get("gate"),
                       "milestone": t.get("milestone"),
                       "owner": t.get("owner"), "assignee": t.get("assignee"),
                       "bundle": _phase_bundle(t.get("phase"))}
                      for s, t in page_tasks],
            "tasks_total": len(tasks)}))
        return
    root = _require_root()
    state = load_state(root)
    # status-ancestor-warn: when cwd has no .add/ of its own but find_root walked up
    # to an ANCESTOR project, say so + hand the exact `init` to scope here — a nested
    # agent otherwise spends commands grepping find_root internals ("why is the project
    # the parent's?"). Full-status path only; stderr so --json/--brief/pipes stay clean.
    _anc = _ancestor_note()
    if _anc:
        print(_anc, file=sys.stderr)
    active = _active_task(state)
    tasks = state.get("tasks", {})
    # Compute once: True when setup is present AND locked is False (the lock-gate window).
    # Reuses the canonical helper — do NOT write a parallel predicate.
    unlocked = not _setup_locked(state)
    # init-idempotent-nudge: reaching here means _require_root passed, i.e. state.json
    # is present — open with the do-not-init nudge so an agent re-orienting never
    # re-runs `init` (the double-init call lever). Plain-status path only; the
    # --brief/--json/--section views returned above are unaffected.
    print("project exists — do not re-init (use --force to reset)")
    # status-orientation-diet: lead the plain view with a resume glance card so a SINGLE
    # status read carries phase + next verb + the resume file — the resume block already
    # exists but sits at line ~67 of the dump, driving the measured 3-4x/rep re-reads.
    # Additive (every line below stays put); reuses _next_footer (the ONE next-verb
    # composer, also used by --brief); distinct "now" label so it never collides with the
    # bottom "resume  :" block. Guarded on an active task — no card on setup/no-task paths.
    _now_active = _active_task(state)
    if _now_active and _now_active in (state.get("tasks") or {}):
        _now_ph = (state["tasks"][_now_active] or {}).get("phase", "?")
        # round-visible-runs: a bounced task names its return-trip count; silent at 0.
        _now_r = ((state["tasks"][_now_active] or {}).get("rounds") or {}).get("count", 0)
        _now_rr = f" · round {_now_r}" if _now_r else ""
        print(f"now     : '{_now_active}' · phase={_now_ph}{_now_rr} · {_next_footer(root, state)}")
        print(f"          PLAN.md: .add/tasks/{_now_active}/PLAN.md   ·   re-orient: add.py status --brief")
    print(f"project : {state.get('project', '(unknown)')}")
    # project autonomy default (task init-auto-default): the posture new tasks INHERIT,
    # read LIVE from PROJECT.md so the human sees the project-wide throttle every session.
    print(f"project autonomy: {_project_autonomy(root)}   (default — new tasks inherit)")
    # git-native actor (user-identity): who ADD sees you as this session — the identity every
    # human-owned stamp records. Always present (the resolver is TOTAL). Read-only, no write.
    _who = identity._whoami(state)
    _who_email = f" <{_who['email']}>" if _who.get("email") else ""
    print(f"actor   : {_who['name']}{_who_email} (source: {_who['source']})")
    print(f"stage   : {state.get('stage', '(unknown)')}")
    # project GOAL + active-milestone goal (v20) — the loop's orientation anchor, read
    # LIVE from PROJECT.md / MILESTONE.md (never state.json). Additive: every existing
    # line stays put. A missing source degrades to a sentinel — one never blanks the other.
    # lean default (status-lean-default): the full goal/m-goal PROSE moves behind --all
    # (the `context: .add/PROJECT.md` pointer below already names where the goal lives); the
    # bare view keeps a one-line m-goal pointer + the goal-ready health line.
    if show_all:
        print(f"goal    : {_project_goal(root)}")
    _active_ms = _active_milestone(state)
    if _active_ms:
        if show_all:
            print(f"m-goal  : {_milestone_doc(root, _active_ms)[1]}   (← {_active_ms})")
        else:
            print(f"m-goal  : (← {_active_ms}, full text: status --all)")
        # goal-ready (task goal-auto-ready-gate): is the active milestone's goal AUTO-READY
        # — every exit criterion citing a verifier `(verify: …)` so the engine can self-verify
        # the result against it? Read LIVE from MILESTONE.md; surfaced every session so the
        # human sees the goal-clarity gap. Additive — human-readable only, never the JSON surface.
        _gr_cited, _gr_total = _exit_criteria_cited(root, _active_ms)
        _gr_state = "auto-ready ✓" if _goal_auto_ready(root, _active_ms) else "NOT auto-ready"
        print(f"goal-ready: {_gr_state}   ({_gr_cited}/{_gr_total} exit criteria cite a verifier)")
        # relations-surface: advisory relation health — silent
        # when clean, a one-line count of dangling/self edges when not. Never writes/blocks.
        _rel_bad = _relations_health(root, state)
        if _rel_bad:
            _n_self = sum(1 for f in _rel_bad if f["kind"] == "self_relation")
            _n_dang = sum(1 for f in _rel_bad if f["kind"] == "dangling")
            _parts = [p for p in (f"{_n_dang} dangling" if _n_dang else "",
                                  f"{_n_self} self" if _n_self else "") if p]
            print(f"relations: {' · '.join(_parts)} — run add.py check")
        # milestone-relations health (wire-milestone-relations): the milestone twin of the
        # task relations: line above — one advisory count, silent when clean, human branch only.
        _msrel_bad = _milestone_relations_health(root, state)
        if _msrel_bad:
            _ms_self = sum(1 for f in _msrel_bad if f["kind"] == "self_relation")
            _ms_dang = sum(1 for f in _msrel_bad if f["kind"] == "dangling")
            _ms_parts = [p for p in (f"{_ms_dang} dangling" if _ms_dang else "",
                                     f"{_ms_self} self" if _ms_self else "") if p]
            print(f"milestone-relations: {' · '.join(_ms_parts)} — run add.py check")
    # foundation pointer — read the cross-milestone context first (anti-rot)
    if (root / "PROJECT.md").exists():
        print("context : .add/PROJECT.md  (read-first foundation: goal · invariants · pointers to .add/specs/)")
    # voice pointer — the AI's SOUL (tone · style · trust); read each session, edit freely.
    # Existence-only: no open/parse, so the pointer adds no IO failure path (a non-file is no voice).
    if (root / "SOUL.md").exists():
        print("voice   : .add/SOUL.md  (how I sound & what keeps your trust — read each session)")
    # persona pointer (persona-seed-nudge v2): project-wide, read every session like context/voice
    # above — fires until >=1 REAL persona is seeded, self-clears once one lands. Advisory only;
    # never gates, never touches the --json branch (human-readable orientation surface only).
    # persona-nudge-quiet: the unseeded hint is a DISCOVERY nudge — it fires at the
    # seams (init · new-milestone · idle status), never on every active-task status
    # (benchmark evidence: 20-30 prints/run, 0 personas ever seeded — context noise).
    if _personas_unseeded(root):
        if not _active_task(state):
            print(f"persona : {PERSONA_HINT}")
    else:
        # persona roster (roster-status-line): one frontmatter-sourced line per REAL persona
        # (slug · flow · vibe) so a selector never needs whole-roster body reads. Existence-
        # gated: a persona-less project's output is byte-identical; advisory, never a gate.
        # lean default (status-lean-default): the roster BODY moves behind --all; the bare
        # view keeps a `personas: <N> (status --all)` count/pointer.
        _roster = list(_persona_roster(root))
        if show_all:
            print("personas:")
            for _slug, _flow, _vibe in _roster:
                print(f"  - {_slug} [{_flow}] — {_vibe}")
        else:
            print(f"personas: {len(_roster)} (status --all)")
    # milestone rollup (only when milestones are in use)
    milestones = state.get("milestones") or {}
    active_ms = _active_milestone(state)
    if milestones:
        _sorted_ms = _sorted_by_updated(milestones)
        # lean default (status-lean-default): the per-milestone ROWS move behind --all; the
        # bare view keeps a `milestones: <N active> · <A> archived (status --all)` count line.
        if show_all:
            print("milestones:")
            for mslug, m in _sorted_ms:
                members = [t for t in tasks.values() if t.get("milestone") == mslug]
                done = sum(1 for t in members if _task_done(t))
                mark = "*" if mslug in (state.get("active_milestones") or []) else " "
                print(f"  {mark} {mslug:<20} {done}/{len(members)} tasks done"
                      f"   status={m.get('status', 'active')}")
        else:
            _n_arch = sum(1 for m in milestones.values() if m.get("status") == "archived")
            _n_active = len(milestones) - _n_arch
            print(f"milestones: {_n_active} active · {_n_arch} archived (status --all)")
    # archived rollup — one line keeps state visible without re-bloating status
    archived = state.get("archived") or []
    if archived:
        n = len(archived)
        m_tasks = sum(rec.get("tasks", 0) for rec in archived)
        print(f"archived: {n} milestone{'s' if n != 1 else ''} "
              f"({m_tasks} task{'s' if m_tasks != 1 else ''})")

    # fast-lane marker (fast-new-task-flag): tag an ACTIVE fast task so the lane is visible at a
    # glance. Presentation-only, existence-gated — a plain/absent active task is byte-unchanged.
    _fast_mark = " · fast" if active and tasks.get(active, {}).get("fast") is True else ""
    print(f"active  : {active or '(none)'}{_fast_mark}")
    # parallel streams (parallel-status-view): when >=2 milestones are active, render each as its
    # own stream (active task + phase) so a user working N fronts reads them all at once. ADDITIVE —
    # the N<=1 output above is byte-identical (the standing additive-cue convention); presentation
    # only, no command DECISION changes. Reads the SET/map via the task-2 seam shape.
    _ams = state.get("active_milestones") or []
    if len(_ams) >= 2:
        _primary = _active_milestone(state)
        _order = ([_primary] if _primary in _ams else []) + [m for m in _ams if m != _primary]
        _atasks = state.get("active_tasks") or {}
        # lean default (status-lean-default): keep the `streams : <N> active milestones`
        # header; the per-stream detail rows move behind --all.
        print(f"streams : {len(_ams)} active milestones"
              + ("" if show_all else " (per-stream rows: status --all)"))
        for _m in (_order if show_all else []):
            _tk = _atasks.get(_m)
            _ph = (tasks.get(_tk) or {}).get("phase", "-") if _tk else "-"
            _mk = "▸" if _m == _primary else " "
            _tag = "  (primary)" if _m == _primary else ""
            # per-stream owner (per-stream-owner): the milestone's lead, present-only — a stream
            # whose milestone has no owner (or a blank-name owner) renders byte-identically
            # (additive-cue convention). Guard on the name like `_fmt_ownership`, so a hand-edited
            # blank-name record never emits an `owner:` fragment.
            _owner_rec = (milestones.get(_m) or {}).get("owner") or {}
            _so = _fmt_actor(_owner_rec) if _owner_rec.get("name") else ""
            _own_frag = f"  · owner: {_so}" if _so else ""
            print(f"  {_mk} {_m:<20} task={_tk or '(none)'}  phase={_ph}{_tag}{_own_frag}")
    # queued backlog (queue-resume-surface): surface milestones awaiting promotion so a
    # multi-milestone session resumes cleanly — `active` is what you're on, `queued` is what's
    # next. ADDITIVE + present-only: silent when zero queued (byte-identical), exactly like the
    # release/loose/streams cues; reads state, writes nothing, changes no command decision.
    _queued = [ms for ms, m in milestones.items() if m.get("status") == "queued"]
    if _queued:
        print(f"queued  : {len(_queued)} milestone(s) next — {', '.join(_queued)}")
        print(f"          promote next: add.py activate {_queued[0]}")
    # surface the active task's autonomy level (task explicit-autonomy-dial) so the human
    # reads the throttle every session; "unset" when no explicit `autonomy:` line is present.
    if active and active in tasks:
        print(f"autonomy: {_autonomy_level(_task_header(root, active)) or 'unset'}")
        # the human-declared risk-CLASS (risk-sensitivity-taxonomy): present-only when a valid
        # sensitivity is declared; "unset" cue when absent; "?" surfaces a typo to fix at freeze.
        _sens = _task_sensitivity(_task_header(root, active), valid=_project_sensitivity_values(root))
        print(f"sensitivity: {('unset' if _sens is None else _sens)}")
        # fast-lane-skips: declared/consumed skip-set — present-only (additive-cue convention).
        _skips_line = _skip_status_line(root, state, active)
        if _skips_line:
            print(_skips_line)
        # phase bundle (phase-bundles): which of the 3 agent-owned bundles (DIRECTION/BUILD/
        # VERIFY) the active phase belongs to + the roster agent preferred for THIS phase —
        # additive-cue convention (present-only; silent at "done", the one PHASES member with
        # no owning bundle — _phase_bundle returns None there, never a fabricated name).
        _active_phase = tasks[active].get("phase")
        _bundle = _phase_bundle(_active_phase)
        if _bundle is not None:
            print(f"bundle  : {_bundle}  ({'·'.join(PHASE_GROUPS[_bundle])})"
                  f"  — prefer: {PHASE_AGENT[_active_phase]} agent")
        # step-spawn-hint (advisor-gated-autonomy): one advisory line naming the agent shape a
        # parallel run would fan out at THIS step. Present-only (None → no line): suppressed under
        # the `manual` dial and at contract/done. The tier reflects declared `risk: high`.
        _hint = _spawn_hint_line(
            {"phase": tasks[active].get("phase"),
             "risk": "high" if _RISK_HIGH_RE.search(_task_header(root, active)) else None},
            _project_autonomy(root))
        if _hint:
            print(_hint)
        # owner/assignee of the active task (ownership-assignment) — present-only, never a
        # placeholder; an unassigned active task adds no line (additive-cue convention).
        _own = _fmt_ownership(tasks[active])
        if _own:
            print(f"owned   : {_own}")
        # grounded (task ground-bundle-wiring): does the active task's §0 GROUND map cite the
        # anchors §3 names? measure-not-block, human-readable only (never the JSON surface). A
        # pre-ground / legacy task (no §0) -> _task_grounded None -> NO line, so the surface is
        # purely additive: an existing task's status output is byte-unchanged.
        _g = _task_grounded(root, active)
        if _g is not None:
            print("grounded: " + ("grounded ✓ — §0 cites the anchors §3 names" if _g
                                  else "not yet — fill the §0 GROUND anchors (add.py guide)"))
    if not tasks:
        # First-run panel: a brand-new project's status is the moment a user is most
        # lost. When the setup is unlocked, the only correct next move is review+lock —
        # suppress the generic /add hint and name the two steps that matter.
        print("tasks   : (none yet)")
        print()
        if unlocked:
            print("setup   : UNLOCKED — review .add/SETUP-REVIEW.md (lowest-confidence first),"
                  " then sign: add.py lock")
            print("          (the build-boundary gate is closed until the foundation is locked)")
        else:
            print("next    : you're set up. In Claude Code, run /add and say what you want to")
            print("          build — the `add` skill sizes it into a milestone and drives the")
            print('          build with you. Escape hatch: add.py new-task <slug> --title "..."')
        return
    # lean default (status-lean-default): the per-task ROWS move behind --all; the bare
    # view keeps a `tasks   : <N> (status --all)` count line. The `active :` line above
    # already names the current task, so the resume point is never hidden.
    if show_all:
        print("tasks   :")
        for slug, t in _sorted_by_updated(tasks):
            mark = "*" if slug == active else " "
            deps = t.get("depends_on") or []
            dep_s = f"  deps={','.join(deps)}" if deps else ""
            # relations-surface: the two non-blocking edges, silent when absent (no noise)
            ext = t.get("extends") or []
            rel_slugs = t.get("relates_to") or []
            rel_s = (f"  ext={','.join(ext)}" if ext else "") + (f"  rel={','.join(rel_slugs)}" if rel_slugs else "")
            ms_s = f"  [{t['milestone']}]" if t.get("milestone") else ""
            print(f"  {mark} {slug:<24} phase={t['phase']:<10} gate={t['gate']}{ms_s}{dep_s}{rel_s}")
    else:
        print(f"tasks   : {len(tasks)} (status --all)")
    # fold-pressure nudge: surface unfolded competency deltas so emission can't
    # silently outrun the human fold (read-only; v11). Silent when none are open.
    open_deltas = sum(len(v) for v in _collect_open_deltas(root).values())
    if open_deltas:
        print(f"deltas  : {open_deltas} open — consolidate at milestone close (add.py deltas)")
    # SPEC-delta staleness nudge (project-wide): surface unresolved forward hand-offs as STALE
    # backpressure so they drain instead of silently accumulating (delta-drain). Read-only;
    # PRESENT-ONLY (silent when none → byte-identical). The prefix stays `spec :` (the cue the
    # spec-delta guards pin); kernel-trim (ADD 2.0 M5): the drain surface is now
    # seed-as-task or a manual §7 resolve — the carry/drop verbs died.
    open_spec = len(_collect_open_spec_deltas(root))
    if open_spec:
        noun = "delta" if open_spec == 1 else "deltas"
        print(f"spec    : {open_spec} open SPEC {noun} — stale; drain via add.py deltas "
              "(new-task --from-delta, or resolve in §7)")
    # When the setup is unlocked, the only terminal guidance that matters is
    # review+lock; suppress the generic resume block so it does not compete.
    if unlocked:
        print("\nsetup   : UNLOCKED — review .add/SETUP-REVIEW.md (lowest-confidence first),"
              " then sign: add.py lock")
        print("          (the build-boundary gate is closed until the foundation is locked)")
    elif active and active in tasks:
        ph = tasks[active]["phase"]
        if ph == "done":
            # loop-aware resume (loop-aware-orient): a done task is NOT always "start the
            # next feature" — if its milestone goal is unmet we are at the loop juncture, so
            # STEER into the loop; if met, point at the close. PLAIN stays byte-identical.
            _hl, _nxt, _chap = _done_resume(root, state, active)
            print(f"\nresume  : task '{active}' is done ({tasks[active]['gate']}).")
            if _chap == "02-the-flow.md":
                print("          start the next feature: add.py new-task <slug>")
            else:
                print(f"          {_hl} — {_nxt}")
                print(f"          (the loop: {book_url(_chap)})")
        else:
            # resume-card-dedup (advance-fold follow-through): the top 'now' card
            # already carries slug · phase · the EXACT next verb (via _next_footer,
            # frozen-ness threaded) · re-orient. The bottom block used to RESTATE all
            # of that — a ~230B doubling that re-enters cache on every later turn. Keep
            # ONLY the context ops it uniquely teaches (engine-hint-context-ops): the
            # per-section read + the cheap re-orient (the whole-PLAN.md context-tax
            # drivers). The next verb lives once now — in the card.
            print(f"\nresume  : add.py status --section {ph}  ·  add.py status --brief"
                  "   (read one section / cheap re-orient — whole PLAN.md only if needed)")


# Agent-portability (v14): `guide` names the PHASE PLAYBOOK file — the same
# guides the Claude skill loads, installed as plain markdown by every channel
# at .claude/skills/add/phases/ — so ANY agent (Cursor, Copilot, Codex) can be
# routed there through the CLI alone. Never a dead pointer: the path is printed
# only if the file exists; a missing tree gets an install hint instead.
_PHASE_GUIDE_FILES = {
    # skill-loop-fold: one reference file per beat — the merged 3-file phases/ shape.
    "direction": "direction.md",
    "build": "build.md", "verify": "verify.md",
}
_SKILL_PHASES_DIR = Path(".claude") / "skills" / "add" / "phases"


def _phase_guide_path(project_root: Path, phase: str) -> str | None:
    """Relative path to the phase playbook if it exists, else None.
    done/unknown phases have no playbook (the `then:` line routes onward)."""
    fname = _PHASE_GUIDE_FILES.get(phase)
    if fname is None:
        return None
    rel = _SKILL_PHASES_DIR / fname
    return str(rel) if (project_root / rel).is_file() else None


_POST_FREEZE_DIRECTION_ACTION = (
    "§1–§4 approved — cross into build: add.py advance (runs the full gate stack)")


def cmd_guide(args: argparse.Namespace) -> None:
    """Answer "what do I do next?" for the active (or named) task.

    Strictly read-only: load_state only — never save_state, never writes a PLAN.md.
    """
    if getattr(args, "json", False):
        json_root, state = _load_state_for_json()
        slug = args.slug or _active_task(state)
        if not slug:
            print(json.dumps({"task": None, "phase": None, "owner": "human", "stop": True,
                              "next_step": "start your first feature -> add.py new-task <slug>",
                              "chapter": book_url("02-the-flow.md"), "gate": None,
                              "guide": None, "bundle": None}))
            return
        t = (state.get("tasks") or {}).get(slug)
        if t is None:
            _die(f"unknown task '{slug}'")
        phase = t.get("phase")
        owner = _phase_owner(phase)            # _die unmapped_phase before any stdout
        action, chapter = PHASE_GUIDE[phase]   # phase is mapped, so PHASE_GUIDE has it too
        if phase == "done":                    # loop-aware-orient: steer the --json surface too
            _hl, _nxt, _chap = _done_resume(json_root, state, slug)
            if _chap != "02-the-flow.md":      # loop juncture / goal met; PLAIN stays unchanged
                action, chapter = _nxt, _chap
        elif phase == "direction" and _task_contract_frozen(json_root, slug):
            # the guide never re-teaches an already-passed gate: once §3 is FROZEN the
            # direction step left is the crossing itself, not the freeze approval
            action = _POST_FREEZE_DIRECTION_ACTION
        print(json.dumps({"task": slug, "phase": phase, "owner": owner,
                          "stop": owner != "ai", "next_step": action,
                          "chapter": book_url(chapter), "gate": t.get("gate"),
                          "guide": _phase_guide_path(json_root.parent, phase),
                          "bundle": _phase_bundle(phase)}))
        return
    root = _require_root()
    state = load_state(root)
    slug = args.slug or _active_task(state)
    if not slug:
        print("active : (none)")
        print('next   : start your first feature -> add.py new-task <slug> --title "..."')
        print(f"read   : {book_url('02-the-flow.md')}")
        return
    if slug not in state.get("tasks", {}):
        _die(f"unknown task '{slug}'")
    phase = state["tasks"][slug]["phase"]
    entry = PHASE_GUIDE.get(phase)
    if entry is None:           # corrupted/hand-edited state.json — fail clean, not KeyError
        _die(f"task '{slug}' has unknown phase '{phase}' (state.json corrupted?)")
    action, chapter = entry
    if phase == "done":                        # loop-aware-orient: steer at the loop juncture
        _hl, _nxt, _chap = _done_resume(root, state, slug)
        if _chap != "02-the-flow.md":          # loop juncture / goal met; PLAIN stays unchanged
            action, chapter = _nxt, _chap
    elif phase == "direction" and _task_contract_frozen(root, slug):
        # never re-teach an already-passed gate (first-call-ergonomics): post-freeze the
        # remaining direction step is the crossing, not the freeze approval
        action = _POST_FREEZE_DIRECTION_ACTION
    # the guide names the driver too (task gate-owner-marker) — the SAME _driver_stop the
    # footer renders, on the next-step line. Computed AFTER the unknown-phase guard above,
    # so a bad phase fails clean and never reaches the marker (it invents no default).
    marker = _driver_marker(_driver_stop(root, state, slug, phase))
    print(f"active : {slug}  (phase: {phase})")
    print(f"goal   : {_project_goal(root)}")   # v20 — the next-step surface still shows what the work is FOR
    print(f"next   : {action}{marker}")
    print(f"read   : {book_url(chapter)}")
    gp = _phase_guide_path(root.parent, phase)
    if gp is not None:
        print(f"guide  : {gp}")
    elif phase in _PHASE_GUIDE_FILES:
        print("guide  : (phase guides not installed — npx @pilotspace/add init)")
    # phase bundle (phase-bundles): names the active bundle + states agent-call-preferred —
    # calling the named roster agent for its bundle's phases is the DEFAULT execution mode.
    # Present-only: silent at "done" (_phase_bundle returns None there, never fabricated).
    _bundle = _phase_bundle(phase)
    if _bundle is not None:
        print(f"bundle : {_bundle}  — agent-call-preferred: {PHASE_AGENT[phase]}")
    # fast-lane-skips: declared/consumed skip-set — present-only (additive-cue convention).
    _skips_line = _skip_status_line(root, state, slug)
    if _skips_line:
        print(_skips_line)
    # step-spawn-hint (advisor-gated-autonomy): one advisory line naming the agent shape a parallel
    # run would fan out at THIS step. Present-only: suppressed under `manual` and at contract/done.
    _hint = _spawn_hint_line(
        {"phase": phase,
         "risk": "high" if _RISK_HIGH_RE.search(_task_header(root, slug)) else None},
        _project_autonomy(root))
    if _hint:
        print(_hint)
    # status-guide-fold: the `then:` line reuses the ONE _next_command composer,
    # so guide teaches the SAME exact command as the mutating-verb footer (collapse
    # at front phases, `freeze --by <name>` at contract) — never a divergent hint.
    if phase == "done":
        if chapter != "02-the-flow.md":        # loop juncture / goal met -> the steered command
            print(f"then   : {action}")
        else:
            print('then   : start the next feature -> add.py new-task <slug> --title "..."')
    else:
        # first-call-ergonomics M1: thread the live frozen-ness so guide never
        # re-teaches freeze after §3 is already FROZEN.
        _frozen = phase == "direction" and _task_contract_frozen(root, slug)
        print(f"then   : {_next_command(phase, contract_frozen=_frozen)}")


def _read_task_phase(root: Path, slug: str) -> str | None:
    """Read the `phase:` marker from a task's PLAN.md, or None if absent."""
    task_md = root / "tasks" / slug / "PLAN.md"
    if not task_md.exists():
        return None
    for line in task_md.read_text(encoding="utf-8").splitlines():
        if line.startswith("phase:"):
            rest = line[len("phase:"):].strip()
            return rest.split()[0] if rest else None
    return None


# --- UDD token-layer validator (udd-token-schema) -----------------------------
# A pure, stdlib checker for the compact-DTCG 3-layer token dialect. Returns a
# list of (code, path, detail) violations — [] means valid. NOT wired into
# cmd_check here: udd-check-lint surfaces these as named reds + adds the catalog/
# tree rules (the Fork-A boundary frozen in udd-token-schema §3). The dialect and
# its NAMED divergences from DTCG 2025.10 live in templates/udd-tokens.md.
_TOKEN_LAYERS = ("primitive", "semantic", "component")
_TOKEN_LAYER_CITES = {"semantic": "primitive", "component": "semantic"}
_TOKEN_TYPES = ("color", "dimension", "number", "fontFamily", "fontWeight", "duration")
_TOKEN_HEX_RE = re.compile(r"^#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")
_TOKEN_DIM_RE = re.compile(r"^-?\d+(?:\.\d+)?(?:px|rem|em|%|vh|vw)$")
_TOKEN_DUR_RE = re.compile(r"^\d+(?:\.\d+)?(?:ms|s)$")


def _token_value_form_ok(ttype: str, value: object) -> bool:
    """True if a LITERAL value matches the compact form for its $type."""
    if ttype == "color":
        return isinstance(value, str) and bool(_TOKEN_HEX_RE.match(value))
    if ttype == "dimension":
        return isinstance(value, str) and bool(_TOKEN_DIM_RE.match(value))
    if ttype == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if ttype == "fontWeight":
        return isinstance(value, str) or (
            isinstance(value, int) and not isinstance(value, bool) and 100 <= value <= 900)
    if ttype == "duration":
        return isinstance(value, str) and bool(_TOKEN_DUR_RE.match(value))
    if ttype == "fontFamily":
        return isinstance(value, str) or (
            isinstance(value, list) and bool(value) and all(isinstance(x, str) for x in value))
    return False


def _token_layer_violations(tokens: dict) -> list[tuple[str, str, str]]:
    """Validate a compact-DTCG token dict against the 3-layer citation rules.

    Pure (never mutates `tokens`), stdlib-only, deterministic document order.
    Returns [] when valid, else one (code, path, detail) per violation. The six
    codes are the token-layer named reds udd-check-lint surfaces. A token's LAYER
    is its top-level group name; value forms diverge from DTCG 2025.10 to compact
    scalars (color "#hex", dimension "<n><unit>") — see templates/udd-tokens.md.
    """
    if not isinstance(tokens, dict):
        return [("malformed_value", "", "root is not a JSON object")]

    # index every token (object bearing $value) by dotted path — for alias resolution
    index: dict[str, dict] = {}

    def _index(node: object, path: list[str]) -> None:
        if not isinstance(node, dict):
            return
        if "$value" in node:
            index[".".join(path)] = node
        for key, child in node.items():            # descend even past a token — never skip a subtree
            if not key.startswith("$"):
                _index(child, path + [key])

    for top, node in tokens.items():
        if top in _TOKEN_LAYERS:
            _index(node, [top])

    out: list[tuple[str, str, str]] = []

    def _walk(node: object, path: list[str], layer: str, inherited: "str | None") -> None:
        if not isinstance(node, dict):
            return
        if "$value" in node:                                       # a token
            pathstr = ".".join(path)
            ttype = node.get("$type", inherited)
            value = node.get("$value")
            if ttype not in _TOKEN_TYPES:
                out.append(("unknown_type", pathstr, f"$type {ttype!r} not in {list(_TOKEN_TYPES)}"))
            elif isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                target = value[1:-1]                               # an alias
                if layer == "primitive":
                    out.append(("primitive_has_alias", pathstr,
                                f"a primitive token must hold a literal, not alias {value}"))
                elif target not in index:
                    out.append(("unresolved_alias", pathstr, f"{value} resolves to no token"))
                else:
                    target_layer = target.split(".", 1)[0]
                    if target_layer != _TOKEN_LAYER_CITES[layer]:
                        out.append(("cross_layer_citation", pathstr,
                                    f"{layer} may alias only {_TOKEN_LAYER_CITES[layer]}, not {target_layer}"))
            elif not _token_value_form_ok(ttype, value):           # a literal
                out.append(("malformed_value", pathstr, f"{value!r} is not a valid {ttype}"))
            # a token should be a leaf; if it carries non-$ children, validate them too rather
            # than letting them pass silently (fail-closed — never skip a subtree).
            for key, child in node.items():
                if not key.startswith("$"):
                    _walk(child, path + [key], layer, ttype)
            return
        gtype = node.get("$type", inherited)                       # a group
        for key, child in node.items():
            if not key.startswith("$"):
                _walk(child, path + [key], layer, gtype)

    for top, node in tokens.items():
        if top not in _TOKEN_LAYERS:
            out.append(("unknown_layer", top, f"top-level group {top!r} is not a layer"))
            continue
        _walk(node, [top], top, None)

    return out


# ---- udd-catalog-content-schema (task 2/4): component catalog + content-tree validator ----
_PROPSPEC_LITERALS = ("string", "number", "boolean")


def _propspec_malformed(spec: object) -> "str | None":
    """Return a reason if a catalog PropSpec is malformed, else None.

    A PropSpec is exactly one of: {type: string|number|boolean} ·
    {type: enum, values: [str,…]} · {type: token, token: <$type>} (a task-1 $type).
    """
    if not isinstance(spec, dict):
        return "PropSpec is not an object"
    ptype = spec.get("type")
    if ptype in _PROPSPEC_LITERALS:
        return None
    if ptype == "enum":
        values = spec.get("values")
        if not isinstance(values, list) or not values or not all(isinstance(x, str) for x in values):
            return "enum PropSpec needs a non-empty list of string values"
        return None
    if ptype == "token":
        ttype = spec.get("token")
        if ttype not in _TOKEN_TYPES:
            return f"token PropSpec names unknown $type {ttype!r}"
        return None
    return f"unknown PropSpec type {ptype!r}"


def _prop_value_code(spec: dict, value: object) -> "str | None":
    """Return a violation CODE if a tree prop value mismatches its well-formed PropSpec, else None.

    token props are LAYER-only here (frozen §3 @ v2): the value must be a
    `{semantic.*}` alias. A non-alias literal → prop_type_mismatch; a wrong-layer
    alias → non_semantic_prop_token. Target existence + $type-match defer to
    udd-check-lint (the composer that holds tokens.json).
    """
    ptype = spec.get("type")
    if ptype == "string":
        return None if isinstance(value, str) else "prop_type_mismatch"
    if ptype == "number":
        ok = isinstance(value, (int, float)) and not isinstance(value, bool)
        return None if ok else "prop_type_mismatch"
    if ptype == "boolean":
        return None if isinstance(value, bool) else "prop_type_mismatch"
    if ptype == "enum":
        return None if value in spec.get("values", []) else "prop_type_mismatch"
    if ptype == "token":
        if not (isinstance(value, str) and value.startswith("{") and value.endswith("}")):
            return "prop_type_mismatch"                 # a token prop must be an alias, not a literal
        if value[1:-1].split(".", 1)[0] != "semantic":
            return "non_semantic_prop_token"            # v2: the alias must target the semantic layer
        return None
    return None                                         # unreachable for well-formed specs


def _catalog_tree_violations(catalog: dict, tree: dict) -> list[tuple[str, str, str]]:
    """Validate a json-render content TREE against OUR component CATALOG.

    Pure (never mutates `catalog`/`tree`), stdlib-only, deterministic order. Returns
    [] when valid, else one (code, path, detail) per violation. The eight named reds:
    tree_cites_uncataloged_component · unknown_prop · prop_type_mismatch ·
    non_semantic_prop_token · dangling_child · children_not_allowed · missing_root ·
    malformed_catalog. SEPARATE from _token_layer_violations; udd-check-lint composes
    both. non_semantic_prop_token is LAYER-only (§3 @ v2) — token existence/$type-match
    are udd-check-lint's job (it holds tokens.json). See templates/udd-catalog.md.
    """
    out: list[tuple[str, str, str]] = []

    # 1. catalog PropSpecs (malformed_catalog) — and collect the well-formed specs
    components = catalog.get("components") if isinstance(catalog, dict) else None
    if not isinstance(components, dict):
        out.append(("malformed_catalog", "components", "catalog has no 'components' object"))
        components = {}
    specs: dict[str, dict[str, dict]] = {}              # component -> {prop: well-formed spec}
    declared_names: dict[str, set] = {}                 # component -> all declared prop names
    for cname, comp in components.items():
        if not isinstance(comp, dict):                  # v3: a component entry must be an object
            out.append(("malformed_catalog", f"components.{cname}", "component entry is not an object"))
            declared_names[cname] = set()
            specs[cname] = {}
            continue
        cprops = comp.get("props", {})
        cprops = cprops if isinstance(cprops, dict) else {}
        declared_names[cname] = set(cprops.keys())
        ok: dict[str, dict] = {}
        for pname, spec in cprops.items():
            reason = _propspec_malformed(spec)
            if reason is not None:
                out.append(("malformed_catalog", f"components.{cname}.props.{pname}", reason))
            else:
                ok[pname] = spec
        specs[cname] = ok

    # 2. root (missing_root) — checked before the elements walk
    elements = tree.get("elements") if isinstance(tree, dict) else None
    elements = elements if isinstance(elements, dict) else {}
    root = tree.get("root") if isinstance(tree, dict) else None
    if not isinstance(root, str) or root not in elements:
        out.append(("missing_root", "root", f"root {root!r} is absent from elements"))

    # 3. elements (document key order)
    for eid, el in elements.items():
        if not isinstance(el, dict):                    # v3: an element must be an object
            out.append(("malformed_element", f"elements.{eid}", "element is not an object"))
            continue
        etype = el.get("type")
        cataloged = isinstance(etype, str) and etype in components
        if not cataloged:
            out.append(("tree_cites_uncataloged_component", f"elements.{eid}.type",
                        f"type {etype!r} not in catalog"))

        props = el.get("props")
        if "props" in el and not isinstance(props, dict):   # v3: props must be an object
            out.append(("malformed_element", f"elements.{eid}.props", "props is not an object"))
        elif cataloged and isinstance(props, dict):
            for pname, value in props.items():
                if pname not in declared_names.get(etype, set()):
                    out.append(("unknown_prop", f"elements.{eid}.props.{pname}",
                                f"{pname!r} not declared on {etype}"))
                elif pname in specs.get(etype, {}):     # declared + well-formed spec → value-check
                    code = _prop_value_code(specs[etype][pname], value)
                    if code is not None:
                        out.append((code, f"elements.{eid}.props.{pname}",
                                    f"{value!r} does not satisfy {specs[etype][pname]}"))
                # declared-but-malformed-spec prop: the catalog error is already logged; skip value-check

        children = el.get("children")
        if "children" in el and not isinstance(children, list):   # v3: children must be an array
            out.append(("malformed_element", f"elements.{eid}.children", "children is not an array"))
        elif isinstance(children, list) and children:             # empty list == absent (no violation)
            comp_entry = components.get(etype)
            has_children = (bool(comp_entry.get("hasChildren", False))
                            if cataloged and isinstance(comp_entry, dict) else False)
            if cataloged and not has_children:
                out.append(("children_not_allowed", f"elements.{eid}.children",
                            f"{etype} does not declare hasChildren"))
            else:
                for cid in children:
                    if cid not in elements:
                        out.append(("dangling_child", f"elements.{eid}.children.{cid}",
                                    f"child id {cid!r} absent from elements"))

    return out


# ---- udd-check-lint (task 4/4): the composer + cross-file token resolution ----
# The single holder of tokens + catalog + tree. _catalog_tree_violations checks a
# token-prop alias LAYER-only (it must target `semantic`); here we close the deferral
# task 2 left — resolve that alias against tokens.json for EXISTENCE + $type-match.

def _semantic_token_index(tokens: dict) -> dict[str, "str | None"]:
    """Map each semantic token's dotted path -> its effective $type.

    A token is a node bearing $value; its $type is the nearest $type on its path
    (DTCG group inheritance — $type sits on the GROUP, the leaf carries only $value).
    Keys carry the layer prefix ("semantic.color.accent"), matching the alias body.
    """
    out: dict[str, "str | None"] = {}
    sem = tokens.get("semantic") if isinstance(tokens, dict) else None
    if not isinstance(sem, dict):
        return out

    def _walk(node: object, path: list[str], inherited: "str | None") -> None:
        if not isinstance(node, dict):
            return
        ttype = node.get("$type", inherited)
        if "$value" in node:                       # a token (a leaf bearing $value)
            out[".".join(path)] = ttype
        for key, child in node.items():            # descend even past a token — never skip a subtree
            if not key.startswith("$"):
                _walk(child, path + [key], ttype)

    _walk(sem, ["semantic"], None)
    return out


def _prop_token_resolution_violations(tokens: dict, catalog: dict, tree: dict) -> list[tuple[str, str, str]]:
    """Resolve a tree's semantic token-prop aliases against tokens.json.

    Pure + TOTAL (never mutates inputs; stdlib only; never raises on dict inputs).
    Deterministic document order; [] == every token-prop alias resolves to an
    existing semantic token of the right $type. Acts ONLY on a prop that is BOTH a
    catalog PropSpec {type:token, token:<$type>} AND a tree {semantic.*} alias (the
    props _catalog_tree_violations passed LAYER-only); everything else is task 1/2's.
    Two codes: unresolved_prop_token · prop_token_type_mismatch.
    """
    out: list[tuple[str, str, str]] = []
    sem_index = _semantic_token_index(tokens)
    components = catalog.get("components") if isinstance(catalog, dict) else None
    components = components if isinstance(components, dict) else {}
    elements = tree.get("elements") if isinstance(tree, dict) else None
    elements = elements if isinstance(elements, dict) else {}

    for eid, el in elements.items():
        if not isinstance(el, dict):
            continue                                    # malformed_element — _catalog_tree_violations' job
        etype = el.get("type")
        comp = components.get(etype) if isinstance(etype, str) else None
        if not isinstance(comp, dict):
            continue                                    # uncataloged / malformed — already flagged there
        cprops = comp.get("props")
        cprops = cprops if isinstance(cprops, dict) else {}
        props = el.get("props")
        if not isinstance(props, dict):
            continue
        for pname, value in props.items():
            spec = cprops.get(pname)
            if not isinstance(spec, dict) or spec.get("type") != "token":
                continue                                # only catalog token-props
            if not (isinstance(value, str) and value.startswith("{") and value.endswith("}")):
                continue                                # non-alias literal → task-2's prop_type_mismatch
            target = value[1:-1]
            if target.split(".", 1)[0] != "semantic":
                continue                                # non-semantic alias → task-2's non_semantic_prop_token
            want = spec.get("token")                    # the declared $type
            if want not in _TOKEN_TYPES:
                continue                                # malformed token PropSpec → task-2's malformed_catalog owns it
            path = f"elements.{eid}.props.{pname}"
            if target not in sem_index:
                out.append(("unresolved_prop_token", path, f"{value} resolves to no semantic token"))
                continue
            got = sem_index[target]                     # the resolved token's inherited $type
            if got not in _TOKEN_TYPES:
                continue                                # resolved token's $type malformed → task-1's unknown_type owns it
            if got != want:
                out.append(("prop_token_type_mismatch", path,
                            f"{value} is {got!r}, but prop wants {want!r}"))
    return out


def _udd_named_set_checks(root: Path) -> list[tuple[bool, str, str]]:
    """Lint a project's UDD named set under `.add/design/` (silent when absent).

    Composes _token_layer_violations + _catalog_tree_violations +
    _prop_token_resolution_violations into cmd_check's (ok, desc, reason) checks.
    READ-ONLY; FAIL-CLOSED on malformed JSON (a named code, never a crash). Returns
    [] when no named set exists — so a clean / non-UI project stays untouched.
    """
    design = root / "design"
    tok_path, cat_path = design / "tokens.json", design / "catalog.json"
    proto_dir = design / "prototypes"
    trees = sorted(p for p in proto_dir.glob("*.json") if p.is_file()) if proto_dir.is_dir() else []
    if not (tok_path.exists() or cat_path.exists() or trees):
        return []                                       # silent-when-absent

    def _load(p: Path) -> "tuple[object, str | None]":
        try:
            return json.loads(p.read_text(encoding="utf-8")), None
        except (json.JSONDecodeError, OSError) as e:
            return None, str(e)

    out: list[tuple[bool, str, str]] = []

    tokens = None
    if tok_path.exists():
        tokens, err = _load(tok_path)
        if err is not None:
            out.append((False, "tokens.json parses", f"malformed_tokens_json: {err}"))
            tokens = None
        else:
            v = _token_layer_violations(tokens)
            if not v:
                out.append((True, "tokens.json layer-valid", ""))
            else:
                out += [(False, "tokens.json layer-valid", f"{c}: {p} — {d}") for c, p, d in v]

    catalog = None
    if cat_path.exists():
        catalog, err = _load(cat_path)
        if err is not None:
            out.append((False, "catalog.json parses", f"malformed_catalog_json: {err}"))
            catalog = None

    for tp in trees:
        name = tp.stem
        tree, err = _load(tp)
        if err is not None:
            out.append((False, f"prototype '{name}' parses", f"malformed_prototype_json: {err}"))
            continue
        if catalog is None:
            continue                                    # no catalog to validate a tree against — skip quietly
        v = list(_catalog_tree_violations(catalog, tree))
        if tokens is not None:
            v += _prop_token_resolution_violations(tokens, catalog, tree)
        if not v:
            out.append((True, f"prototype '{name}' valid", ""))
        else:
            out += [(False, f"prototype '{name}' valid", f"{c}: {p} — {d}") for c, p, d in v]

    return out


_CAPTURE_EXTS = ("png", "svg", "jpg", "jpeg", "webp")


def _missing_captures(root: Path) -> list[str]:
    """Prototype names under `.add/design/prototypes/` lacking a design-confirm capture.

    A prototype `<name>.json` is CAPTURED iff a file `.add/design/captures/<name>.<ext>`
    exists (ext in _CAPTURE_EXTS). Returns the uncaptured names in document (sorted) order.
    PURE · TOTAL (missing dirs -> []) · READ-ONLY (never writes, never renders): the engine
    MEASURES capture presence; producing the image is the agent's tool-agnostic choice
    (design.md beat 4; default `@json-render/image`). [] == every prototype captured / none exist.
    """
    proto_dir = root / "design" / "prototypes"
    cap_dir = root / "design" / "captures"
    if not proto_dir.is_dir():
        return []
    names = sorted(p.stem for p in proto_dir.glob("*.json") if p.is_file())
    return [n for n in names
            if not any((cap_dir / f"{n}.{ext}").is_file() for ext in _CAPTURE_EXTS)]








def cmd_search(args: argparse.Namespace) -> None:
    """Read-only keyword/substring search over the milestone/task corpus (active
    + archived) — title/goal/rationale (milestone) or title/Feature (task) lines
    only, never full body, never graph traversal (context-search, search-index).
    Fresh per-call scan via add_engine.search._search_corpus — no persisted
    index/cache. Exit 0 always, including zero matches; --json mirrors
    check/ready's own machine-readable convention."""
    root = find_root()
    if root is None:
        _die("no_project")
    hits = _search_corpus(root, args.keywords)
    if getattr(args, "json", False):
        print(json.dumps([{k: h[k] for k in ("slug", "kind", "status", "snippet")}
                          for h in hits], ensure_ascii=False, indent=2))
        return
    query = " ".join(args.keywords)
    if not hits:
        print(f"no matches for: {query}")
        return
    print(f"{len(hits)} match(es) for: {query}")
    for h in hits:
        print(f"{h['slug']}  [{h['kind']}, {h['status']}]  ({h['count']} match(es))")
        print(f"    {h['snippet']}")


def cmd_check(args: argparse.Namespace) -> None:
    """Read-only integrity check of the .add project. Exit 1 if anything fails."""
    as_json = getattr(args, "json", False)
    if as_json:
        root, state = _load_state_for_json()       # fail closed -> no_state + empty stdout
    else:
        root = find_root()
        if root is None:
            _die("no_project")
        try:
            state = json.loads(_state_text_or_die(root))
        except (json.JSONDecodeError, OSError):
            _die("state_invalid")

    checks: list[tuple[bool, str, str]] = []  # (ok, description, reason-if-failed)
    for key in ("project", "stage", "active_task", "tasks"):
        checks.append((key in state, f"state has key '{key}'", "missing"))

    tasks = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}
    milestones = state.get("milestones") if isinstance(state.get("milestones"), dict) else {}
    archived_slugs = _archived_task_slugs(state)   # archived deps still resolve
    warnings: list[tuple[str, str]] = []  # (name, reason) — nudges that NEVER feed `failed`
    infos: list[tuple[str, str]] = []     # (name, reason) — affirmations; NEVER feed `warned`/`failed`
    for slug, t in tasks.items():
        task_md = root / "tasks" / slug / "PLAN.md"
        checks.append((task_md.exists(), f"task '{slug}' has PLAN.md", "file missing"))
        marker, want = _read_task_phase(root, slug), t.get("phase")
        # a legacy marker name (specify/plan/tests/…) matches its collapsed phase —
        # LEGACY_PHASES is read-side only; task files are never rewritten to the new names
        _marker_norm = LEGACY_PHASES.get(marker, marker)
        checks.append((_marker_norm == LEGACY_PHASES.get(want, want),
                       f"task '{slug}' marker matches state",
                       f"marker={marker!r} state={want!r}"))
        # drift: milestone + dependency references must resolve
        ms = t.get("milestone")
        if ms is not None:
            checks.append((ms in milestones, f"task '{slug}' milestone resolves",
                           f"unknown milestone {ms!r}"))
        elif t.get("fast"):
            # LEGACY state marker (pre-atomic-node --fast tasks): milestone-free was
            # DELIBERATE for these — a soft INFO affirmation, never a WARN/orphan nudge.
            infos.append((f"task '{slug}'", "— standalone fast lane (milestone-free by design)"))
        else:
            # warn-never-block: a task outside a milestone is a structural nudge back toward
            # the intake flow — NOT a failure. Names structure, never the act of intake.
            warnings.append((f"task '{slug}'", "is outside a milestone — size it via the /add "
                                               "intake flow (or attach with --milestone)"))
        # backlink-drift (task-milestone-backlink): the PLAN.md `milestone:` header mirrors state.
        # WARN (never red, warn-never-block) when a PRESENT line disagrees; an ABSENT line is a
        # grandfathered task — silent, never retro-red. Degrade-safe: an unreadable file skips here.
        try:
            _task_text = (root / "tasks" / slug / "PLAN.md").read_text(encoding="utf-8")
        except OSError:
            _task_text = None
        _bl = _read_milestone_line(_task_text) if _task_text is not None else None
        if _bl is not None and _bl != _milestone_backlink_value(ms):
            warnings.append((f"task '{slug}'", f"milestone backlink '{_bl}' disagrees with state "
                             f"'{_milestone_backlink_value(ms)}' — re-run `add.py set-milestone "
                             f"{slug} {ms or 'none'}` to re-sync"))
        # §0 drift anchor (ground-anchor-sha): a §0 that cites bare line numbers (l.NNN) with no
        # `Ground SHA:` has undetectable drift. WARN (never red, warn-never-block); a §0 with a SHA,
        # with no line refs, or an unreadable file is silent. Reuses the read above (one read).
        if _task_text is not None and _ground_cites_line_ref(_task_text) and \
                _read_ground_sha(_task_text) is None:
            warnings.append((f"task '{slug}'", "§0 cites line numbers (l.NNN) with no `Ground SHA:` — "
                             "record `git rev-parse --short HEAD` so drift is detectable"))
        # dangling lineage (delta-task-backlink): a `[SPEC · seeded] … [→ ptr]` whose pointer task
        # is neither live nor archived. WARN (never red); reuses the read above. `_archived_task_slugs`
        # is the same resolver `cmd_ready` trusts (archived ⇒ was PASS-done), so a healthy
        # completed-then-archived seed stays silent.
        if _task_text is not None:
            for _ptr in _seeded_delta_pointers(_task_text):
                if _ptr not in tasks and _ptr not in archived_slugs:
                    warnings.append((f"task '{slug}'", f"seeded SPEC delta points at '{_ptr}' which no "
                                     "longer exists (dangling lineage) — re-point or drop the delta"))
        # rule-id-coverage: a §1 Must/Reject ID with no §2 scenario tag and no §4 `covers:`
        # reference is a coverage gap. WARN only, runs in ANY phase (a gap in already-shipped
        # work must still surface — the whole point of the check); opt-in per task via
        # `_rule_coverage_gaps`'s own tag-presence gate, so a task that never adopted the M#/
        # R:code convention is silently grandfathered — never retro-flagged.
        if _task_text is not None:
            _spans = _phase_spans(_task_text)
            # sec2 still read for legacy §2-bearing boards (fold-scenarios-tests retired the
            # standalone §2; cases now live in §4 — a new doc's §2 span is simply absent/empty).
            for _rid, _kind in _rule_coverage_gaps(_spans.get(1, ""), _spans.get(2, ""), _spans.get(4, "")):
                warnings.append((f"task '{slug}'", f"rule '{_rid}' ({_kind}) has no §4 test "
                                 "covering it (coverage gap) — add a covers: line to the §4 test_plan"))
        # autonomy level (task explicit-autonomy-dial): a REAL out-of-set token is a hard
        # unknown_autonomy_level; a LIVE task (phase before done) with no `autonomy:`
        # line is implicit_autonomy — a WARN, never red. Done predecessors are SKIPPED
        # (a fresh live-only predicate, NOT the audit open-front skip) so the board never floods.
        _alvl = _autonomy_level(_task_header(root, slug))
        checks.append((_alvl != "?", f"task '{slug}' autonomy level recognized",
                       "unknown_autonomy_level (token outside manual|conservative|auto)"))
        if _alvl is None and t.get("phase") != "done":
            warnings.append((f"task '{slug}'", "has no explicit autonomy level (implicit_autonomy) "
                             "— run `add.py autonomy set <level>` to set it"))
        for dep in t.get("depends_on") or []:
            checks.append((dep in tasks or dep in archived_slugs,
                           f"task '{slug}' dep '{dep}' resolves", "unknown task"))
        # relations-surface: the non-blocking edges validate the SAME way (advisory monitor) —
        # a target must resolve (known or archived) and never be a self-edge. Never a gate block.
        for rtype in ("extends", "relates_to"):
            for tgt in t.get(rtype) or []:
                checks.append((tgt != slug,
                               f"task '{slug}' {rtype.replace('_', '-')} '{tgt}' is not a self-relation",
                               "self_relation"))
                checks.append((tgt in tasks or tgt in archived_slugs,
                               f"task '{slug}' {rtype.replace('_', '-')} '{tgt}' resolves", "unknown task"))
        # waiver expiry (Matrix 4): a RISK-ACCEPTED waiver whose `expires` has passed is
        # stale — the gate stored it; `check` is the standing monitor that catches the lapse.
        # Fail-closed: a missing/unparseable expires is a FAIL, never a silent pass.
        if t.get("gate") == "RISK-ACCEPTED":
            exp = (t.get("waiver") or {}).get("expires")
            try:
                ok = exp is not None and date.fromisoformat(exp) >= date.today()
                reason = f"waiver_expired (expires={exp})"
            except (ValueError, TypeError):
                ok, reason = False, f"waiver_expired (unparseable expires={exp!r})"
            checks.append((ok, f"task '{slug}' waiver not expired", reason))
        # delta-lint: validate all OPEN entries in the "### Competency deltas" block.
        # Fail-closed; folded/rejected entries are skipped (open-only). Only emits a
        # check when at least one delta-attempt is present in the block.
        lint_result = _lint_task_deltas(root, slug)
        if lint_result is not None:
            ok, reason = lint_result
            checks.append((ok, f"task '{slug}' deltas well-formed", reason))
        # tamper tripwire standing monitor (verify-integrity): a non-done task whose
        # snapshot has diverged is surfaced EARLY — WARN, never red (the verify GATE
        # is where it bites, HARD-STOP). Fail-closed via _tripwire_divergence.
        if not _task_done(t):
            _tw = t.get("tripwire")
            if _tw and _tripwire_divergence(root, slug, _tw):
                warnings.append((f"task '{slug}'", "tampered since its tests->build "
                                 "snapshot (build_tampered) — a tracked test or the "
                                 "frozen §3 changed; the verify gate will HARD-STOP it"))
            # §5 scope standing monitor (build-scope-lock): a pending out-of-scope
            # touch (or a tampered baseline) surfaces EARLY — WARN, never red; the
            # verify gate is where it bites.
            _sc = t.get("scope")
            if isinstance(_sc, dict):
                _tamper, _out = _scope_findings(root, slug, _sc)
                if _tamper:
                    warnings.append((f"task '{slug}'", "scope-snapshot.json is "
                                     f"{_tamper} against its anchor "
                                     "(scope_snapshot_tampered pending) — the verify "
                                     "gate will refuse it"))
                elif _out:
                    warnings.append((f"task '{slug}'", "touched outside its declared "
                                     f"§5 Scope: {' · '.join(_out[:3])} "
                                     "(scope_violation pending) — the verify gate "
                                     "will refuse it"))

    # persona-setup: validate each persona living doc (.add/personas/*.md) presence-based
    # (measure-not-block) — a missing required key/section is a WARN naming the slug, never a
    # hard failure; a conformant persona is an INFO affirmation. NO-EXEC: pure read + predicate.
    personas_dir = root / "personas"
    if personas_dir.is_dir():
        for pf in sorted(personas_dir.glob("*.md")):
            slug = pf.stem
            if not _persona_slug_valid(slug):
                warnings.append((f"persona '{slug}'",
                                 "persona_slug_invalid — rename to alphanumeric with - or _ only"))
                continue
            try:
                missing = _persona_missing(pf.read_text(encoding="utf-8"))
            except OSError:
                missing = ["(unreadable)"]
            if missing:
                warnings.append((f"persona '{slug}'",
                                 "persona_schema_incomplete: missing " + ", ".join(missing)))
            else:
                infos.append((f"persona '{slug}'", "schema-conformant"))
                # persona-schema-hardening: quality findings the presence check can't see
                # (typo'd flow: value · bare <…> placeholder) — WARN-only (measure-not-block),
                # REAL personas only: any `_`-prefixed scaffold is placeholders by design.
                if not slug.startswith("_"):
                    try:
                        text = pf.read_text(encoding="utf-8")
                    except OSError:
                        text = ""
                    for finding in _persona_quality_warnings(text):
                        warnings.append((f"persona '{slug}'", f"persona_quality: {finding}"))
    # persona-seed-nudge: surface the SAME "no real persona" gap `new-milestone` nudges on, so
    # it is also visible on a plain `check`/`status` sweep — an INFO affirmation-of-absence,
    # never a WARN (measure-not-block; a project with no personas behaves exactly as before).
    if _personas_unseeded(root):
        infos.append(("personas", f"unseeded — {PERSONA_HINT}"))
    else:
        # roster-status-line: the same frontmatter roster as `status`, packed into one INFO
        # row (vibe elided — check is a linter). Advisory; never a WARN, never a gate.
        infos.append(("personas", "roster: " + " · ".join(
            f"{s}[{fl}]" for s, fl, _ in _persona_roster(root))))

    # drift: a done milestone must have no unfinished tasks
    for mslug, m in milestones.items():
        if m.get("status") == "done":
            unfinished = [s for s, t in tasks.items()
                          if t.get("milestone") == mslug and not _task_done(t)]
            checks.append((not unfinished, f"done milestone '{mslug}' fully complete",
                           f"unfinished: {unfinished}"))
        # planned-drift (graph-views W4): a compiled `## Tasks` node with no live task and
        # no archived record. WARN, never red — mid-milestone a planned-not-yet-created node
        # is normal flow; the warning keeps the compiled plan and the board honest with each
        # other (the drift also renders dashed in `add.py graph`).
        ghosts = sorted(k for k in (m.get("planned") or {})
                        if k not in tasks and k not in archived_slugs)
        for g in ghosts:
            warnings.append((f"milestone '{mslug}'", f"planned task '{g}' was never created — "
                             f"`add.py new-task {g}` inherits its planned depends-on "
                             f"(or re-confirm MILESTONE.md without it)"))

    # goal-auto-ready (task goal-auto-ready-gate): nudge the ACTIVE milestone toward a
    # machine-checkable goal — every exit criterion citing a verifier `(verify: …)` so the
    # engine can self-verify the result against it. WARN, NEVER red (measurement, not a gate);
    # fired IFF the goal HAS criteria but not all cite (total >= 1 AND cited < total) — a
    # zero-criteria milestone is shaping's nudge, not this one's. LIVE-ONLY: the OPEN active
    # milestone only — a done-but-not-yet-archived one (still the active pointer until
    # archive clears it) and closed/archived predecessors are never retro-flagged (Must #4).
    _active_ms = _active_milestone(state)
    if _active_ms in milestones and milestones[_active_ms].get("status") != "done":
        _cited, _total = _exit_criteria_cited(root, _active_ms)
        if _total >= 1 and _cited < _total:
            warnings.append(("goal_not_auto_ready",
                             f"milestone '{_active_ms}' goal not auto-ready "
                             f"({_cited}/{_total} exit criteria cite a verifier) — add "
                             "(verify: <test|command|metric>) to each bare criterion"))

    # grounded (task ground-bundle-wiring): the freeze review checklist asks the human to
    # confirm the contract is grounded; this is the standing monitor for the gap. WARN, NEVER
    # red (measure-not-block, mirrors goal_not_auto_ready) — fires IFF the ACTIVE task's §3 is
    # FROZEN AND its §0 GROUND map is ungrounded (the precise "froze without grounding" gap, so
    # no nag during pre-freeze drafting). A pre-ground / legacy task (no §0 -> _grounded_state
    # None) is EXEMPT, never retro-flagged. Rides the existing `warnings` array — no new key.
    _at = _active_task(state)
    if _at in tasks:
        _raw = _raw_phase_bodies(root, _at)
        if _contract_frozen(_raw.get(3, "")) and _grounded_state(_raw) is False:
            warnings.append(("task_not_grounded",
                             f"task '{_at}' froze its contract without grounding — fill the "
                             "§0 GROUND anchors the contract cites (add.py guide)"))

    # sensitivity-glossary: nudge a project to declare its DOMAIN sensitivity classes. WARN, NEVER
    # red (measure-not-block, mirrors goal_not_auto_ready) — the base four always apply; this only
    # invites the project's own risk-class vocabulary into GLOSSARY.md (the AI maintains it per the
    # skill guide). Fires IFF the "## Sensitivity classes" section declares no domain class.
    if not _project_sensitivity_domain(root):
        warnings.append(("sensitivity_classes_unset",
                         "no domain sensitivity classes declared — add the project's risk-class "
                         "vocabulary to GLOSSARY.md's '## Sensitivity classes' section (the base "
                         "security|data|architecture|mechanical always apply; the AI keeps the "
                         "domain classes current — see the sensitivity skill guide)"))

    # spec-dialect-floor (quality-floors M5): the rescannable twin of the crossing warning.
    # WARN, NEVER red (measure-not-block, mirrors goal_not_auto_ready) — lists ACTIVE tasks at
    # build/verify/done whose frozen §3 speaks a dialect class their declared §4 files don't.
    # ACTIVE state only (never archived history): the audit-scan mitigation the freeze flag pinned.
    _dialect_gapped = []
    for _dg_slug in sorted(tasks):
        if (tasks[_dg_slug] or {}).get("phase") not in ("build", "verify", "done"):
            continue
        if _dialect_gaps(root, _dg_slug):
            _dialect_gapped.append(_dg_slug)
    if _dialect_gapped:
        warnings.append(("dialect_gap",
                         f"{len(_dialect_gapped)} task(s) whose frozen §3 speaks a format "
                         f"dialect no declared §4 test file does: {', '.join(_dialect_gapped)} "
                         "— add one test per gap using the contract's literal format "
                         "(spec-dialect floor, benchmark wm2 evidence)"))

    # dependency graph must be acyclic
    cycle = _find_cycle(tasks)
    checks.append((cycle is None, "task dependencies are acyclic",
                   f"cycle: {' -> '.join(cycle)}" if cycle else ""))
    # kernel-trim (ADD 2.0 M5): the wave-ledger, component-registry, cross-component-contract
    # and federation integrity checks died with their pillar verbs — that discipline is the
    # stream-orchestrator / platform-engineer personas' playbook now.

    # UDD foundation (udd-check-lint): lint a project's named set under .add/design/ —
    # composes the token + catalog/tree validators + the cross-file prop-token resolution.
    # Silent when absent; read-only; fail-closed on malformed JSON.
    checks.extend(_udd_named_set_checks(root))

    # capture-evidence: a never-red WARN naming each prototype with no design-confirm capture
    # at .add/design/captures/<name>.<ext>. Measure-never-block — rides `warnings`, NEVER
    # `checks` (so never feeds `failed`); silent-when-absent (no prototypes -> []). The engine
    # MEASURES capture presence; producing the image is the agent's tool-agnostic choice.
    for _pname in _missing_captures(root):
        warnings.append(("missing_capture",
                         f"prototype '{_pname}' has no design-confirm capture at "
                         f".add/design/captures/{_pname}.<png|svg|…> — render + confirm it "
                         "before build (design.md beat 4)"))

    # roster-uninstalled (roster-install-drift): the ADD-managed guideline block cites the agent
    # roster ("agents/*.md" tail — matches both the shipped `add-method/agents/*.md` attribution
    # citation and any older phrasing) but the project may have no roster installed at all — never
    # shipped in the package, synced before this fix, or from a build that regressed the agents/
    # tree — a dead reference with no signal anywhere. WARN, never red (measure-not-block);
    # presence-gated on the citation itself — a project whose guideline files don't cite a roster
    # at all is silently exempt, never retro-flagged.
    _project_root = root.parent
    _cites_roster = False
    for _gname in GUIDELINE_FILES:
        try:
            _gtext = (_project_root / _gname).read_text(encoding="utf-8")
            # roster-distill (ADD 2.0 M1): the block cites `agents/add.md`; the old
            # `agents/*.md` phrasing keeps pre-distill projects covered (never retro-exempt).
            if "agents/add.md" in _gtext or "agents/*.md" in _gtext:
                _cites_roster = True
                break
        except OSError:
            pass
    if _cites_roster:
        _agents_dir = _project_root / ".claude" / "agents"
        if not (_agents_dir.is_dir() and any(_agents_dir.glob("add*.md"))):
            warnings.append(("roster_uninstalled",
                             "guideline file(s) cite the agent roster but no `.claude/agents/"
                             "add*.md` agent is installed — run `add.py update` (or re-run the "
                             "CLI installer) to materialize it"))

    # milestone-relations health (wire-milestone-relations): surface a milestone whose
    # depends-on/extends/relates-to header edge names an unknown milestone (dangling) or
    # itself (self). ADVISORY — feeds `warnings`, NEVER `checks`/`failed` (a cross-milestone
    # legibility edge never blocks). The status one-liner counts the same findings.
    for _mf in _milestone_relations_health(root, state):
        _rlabel = _mf["relation"].replace("_", "-")
        if _mf["kind"] == "self_relation":
            warnings.append((f"milestone '{_mf['mslug']}'", f"{_rlabel} names itself (self_relation)"))
        else:
            warnings.append((f"milestone '{_mf['mslug']}'",
                             f"{_rlabel} '{_mf['target']}' which is not a milestone (dangling)"))

    passed = sum(1 for ok, _, _ in checks if ok)
    failed = len(checks) - passed
    if as_json:
        # `infos`/`informed` are ADDITIVE (standalone-fast-task) — affirmations that never feed
        # `warned`/`failed`; existing keys are untouched so prior consumers keep working.
        print(json.dumps({"passed": passed, "failed": failed,
                          "warned": len(warnings),
                          "warnings": [{"name": name, "reason": reason}
                                       for name, reason in warnings],
                          "informed": len(infos),
                          "infos": [{"name": name, "reason": reason}
                                    for name, reason in infos],
                          "checks": [{"ok": ok, "name": desc,
                                      "reason": reason if not ok else ""}
                                     for ok, desc, reason in checks]}))
    else:
        for ok, desc, reason in checks:
            print(f"PASS  {desc}" if ok else f"FAIL  {desc}: {reason}")
        for name, reason in warnings:
            print(f"WARN  {name} {reason}")
        for name, reason in infos:
            print(f"INFO  {name} {reason}")
        summary = f"check: {passed} passed, {failed} failed"
        if warnings:
            summary += f" ({len(warnings)} warnings)"   # frozen §3: summary gains "(N warnings)"
        print(summary)
    if failed:
        raise SystemExit(1)








# ---------------------------------------------------------------------------
# wave-ledger fork-base enforcement (engine-merge-base-enforcement)
#
# streams.md states the rule; these helpers EXECUTE it (words-exist != method-works).
# The ledger is the hand-written `.add/milestones/<m>/WAVE.md` per the streams.md
# template: a `base: <sha>` line, a `status: live|merging` field on the header line,
# and a `### Roster` table whose 3rd column holds the PASTED `rev-parse HEAD` echo.
# Parsing is FAIL-CLOSED: anything off-grammar names the unparseable piece rather
# than silently passing — a silent skip would un-guard the trust layer.

_WAVE_SHA_RE = re.compile(r"\b[0-9a-f]{7,40}\b")










def cmd_new_milestone(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    if not slug.replace("-", "").replace("_", "").isalnum():
        _die("bad_slug")
    # Prefer a short DESCRIPTIVE slug over a bare version (v2, v1-1, 1.2): a descriptive
    # name keeps the milestones list legible. Advisory only — never blocks (matches the
    # engine's `note:` convention); a deliberate version slug still creates.
    if re.match(r"^v?\d+([._-]\d+)*$", slug, re.IGNORECASE):
        print(f"note: slug '{slug}' looks like a bare version — prefer a short "
              f"descriptive name (e.g. 'payment-retries'). Creating anyway.")
    state.setdefault("milestones", {})
    mdir = root / "milestones" / slug
    mfile = mdir / MILESTONE_FILE
    if mfile.exists() and not args.force:
        _die("milestone_exists")
    mdir.mkdir(parents=True, exist_ok=True)
    title = args.title or slug.replace("-", " ").replace("_", " ").title()
    # One _now() instant feeds BOTH the MILESTONE.md render and the state record, so the
    # human-facing `created:` is a full ISO timestamp provably equal to state.json.
    now = _now()
    # tiny lane (tiny-plan-small-scope): --tiny writes a COMPACT plan — goal + Plan +
    # Done-when only. Human-declared, never engine-elected; the trust floor is untouched
    # (member tasks still freeze/red/gate — only the PLAN artifact shrinks to fit the scope).
    tiny = bool(getattr(args, "tiny", False))
    if tiny:
        _atomic_write(mfile, (
            f"# MILESTONE: {title}\n\n"
            f"goal: {args.goal or '<goal>'}\n"
            f"stage: {args.stage} \u00b7 status: active \u00b7 created: {now} \u00b7 lane: tiny\n"
            f"release: pending\n\n"
            "> Tiny plan \u2014 small scope, one approval. Keep it to a handful of lines; if it\n"
            "> outgrows this shape, recreate without --tiny (the full SDD scaffold).\n\n"
            "## Plan\n\n"
            "## Done when\n"
        ))
    else:
        _atomic_write(mfile, _render_template(
            "MILESTONE.md", title=title, goal=args.goal or "<goal>",
            stage=args.stage, date=now))
    # confirm-parent gate (OPT-IN, mirrors `init --await-lock`): `--await-confirm` seeds the
    # milestone UNCONFIRMED so new-task is held until `add.py milestone-confirm`. WITHOUT the flag
    # NO `confirmed` key is written → grandfathered-confirmed → no gate (so the existing engine
    # tests stay byte-green). The guided skill flow passes the flag at the human-review point.
    await_confirm = bool(getattr(args, "await_confirm", False))
    # --queued (OPT-IN): create the milestone non-active (status=queued) without stealing focus.
    # The active set is left UNCHANGED so the default path (no flag) stays byte-identical. Promote
    # later with `activate` (queued→active). Foundation for roadmap intake (1 active + N queued).
    queued = bool(getattr(args, "queued", False))
    record = {
        "title": title, "goal": args.goal or "", "stage": args.stage,
        "status": "queued" if queued else "active", "created": now, "updated": now,
    }
    if tiny:
        record["tiny"] = True   # durable lane marker (absent == full; grandfather-safe)
    if await_confirm:
        # `await_confirm` is the STABLE opt-in marker (set ONLY here, at creation). `confirmed`
        # alone is NOT a reliable opt-in signal: milestone-confirm stamps confirmed:true on a plain
        # milestone too, so a later build-entry gate must key on `await_confirm`, not `confirmed`.
        record.update(confirmed=False, confirmed_at=None, confirmed_by=None, await_confirm=True)
    state["milestones"][slug] = record
    if not queued:
        # PRESERVE the active SET (new-milestone-add-focus): ADD this milestone + focus it, rather
        # than REPLACING the set and evicting the others. Single-active is identical ([] -> [slug]);
        # a user who already had P active now keeps P active alongside the new primary.
        _activate_milestone(state, slug)
    save_state(root, state)
    print(f"created milestone '{slug}' -> {mfile}")
    if queued:
        print(f"queued (not active) — promote it with: add.py activate {slug}")
        # surface the recorded confirm gate for a queued+await_confirm milestone (queued-await-confirm-hint):
        # additive — prints ONLY when await_confirm, so plain `--queued` output stays byte-identical.
        if await_confirm:
            print(f"  (unconfirmed — after promote: add.py milestone-confirm {slug})")
    else:
        print("active milestone set." + ("" if not await_confirm else
              "  (unconfirmed — show the MILESTONE.md, then: add.py milestone-confirm " + slug + ")"))
        # persona-seed-nudge: a non-blocking hint (never a gate) when this project has no
        # REAL project-fit persona yet — points at the cross-cutting selection/drafting
        # service rather than inventing a second mechanism. Fires only on the ACTIVE arm
        # (a queued milestone isn't yet in flight, so the nudge would be premature there).
        if _personas_unseeded(root):
            print(f"note: {PERSONA_HINT}")
        else:
            # persona-fit-nudge: the opposite branch — ≥1 real persona already exists, so nudge
            # the AI to confirm domain fit (or draft a new one) rather than silently assuming an
            # existing persona covers this brand-new milestone. Existence-only, mutually
            # exclusive with the note above (same predicate, opposite branch — never both).
            slugs = ", ".join(_real_persona_slugs(root))
            print(f"persona-fit: {PERSONA_FIT_HINT_TEMPLATE.format(slugs=slugs)}")
    # milestone-lane-nudge: the WM1 bait point — a single-task request routed here costs
    # ~10 calls of milestone ceremony. Advisory only; the command-point beats wrapper prose.
    print("lane: single task? skip the milestone: add.py new-task <slug> --title \"...\"")
    print(_next_footer(root, state))   # converges the old "Decompose it into tasks: …" hint


_PLAN_LINE_RE = re.compile(r"^-\s*\[.\]\s+(\S+)\s+depends-on:\s*(.*?)\s+—", re.M)


def _compile_task_graph(md_text: str) -> dict[str, list[str]]:
    """edge-truth (task-graph-native W1): compile MILESTONE.md's `## Tasks` list into the
    planned task DAG — the milestone is the scope ROOT; the graph's depth lives in these
    edges. Grammar: `- [ ] <slug>   depends-on: <none | slug, slug>   — <one line>`.
    Placeholder `<slug>` entries and malformed lines are skipped silently (the scaffold
    itself must compile to {}). Pure; the caller persists the result."""
    start = md_text.find("## Tasks")
    if start == -1:
        return {}
    end = md_text.find("\n## ", start + 1)
    section = md_text[start:end if end != -1 else len(md_text)]
    graph: dict[str, list[str]] = {}
    for m in _PLAN_LINE_RE.finditer(section):
        slug, deps_raw = m.group(1), m.group(2).strip()
        if slug.startswith("<"):
            continue
        deps = ([] if deps_raw.lower() == "none"
                else [d.strip() for d in deps_raw.split(",")
                      if d.strip() and not d.strip().startswith("<")])
        graph[slug] = deps
    return graph


def _persist_task_graph(root: Path, state: dict, slug: str) -> None:
    """Compile-and-store the milestone's planned graph; prints the summary when non-empty.
    Runs on confirm AND re-confirm — the plan is living, the compile is idempotent."""
    mfile = root / "milestones" / slug / MILESTONE_FILE
    try:
        md = mfile.read_text(encoding="utf-8")
    except OSError:
        return
    graph = _compile_task_graph(md)
    if not graph:
        return
    state["milestones"][slug]["planned"] = graph
    edges = sum(len(v) for v in graph.values())
    print(f"compiled task graph: {len(graph)} nodes · {edges} edges "
          "(new-task inherits each node's planned depends-on)")
    # cycle warn (measure-not-block): a depends-on cycle deadlocks the wave schedule —
    # name it at compile time, never refuse the confirm (the human just approved the plan;
    # the fix is an edit + re-confirm, and the recompile is idempotent).
    seen: set[str] = set()
    def _visit(n: str, path: tuple) -> tuple | None:
        if n in path:
            return path[path.index(n):] + (n,)
        if n in seen or n not in graph:
            return None
        seen.add(n)
        for d in graph[n]:
            found = _visit(d, path + (n,))
            if found:
                return found
        return None
    for node in graph:
        cyc = _visit(node, ())
        if cyc:
            print(f"warning: graph_cycle — depends-on cycle {' -> '.join(cyc)} "
                  "would deadlock the wave schedule; edit MILESTONE.md and re-confirm")
            break


def cmd_milestone_confirm(args: argparse.Namespace) -> None:
    """The human gate that opens new-task for a milestone (confirm-parent). Mirrors `cmd_lock`
    one level down: the human reviews the filled MILESTONE.md, then RECORDS confirmation here.
    The engine never self-confirms. Validate-then-write; re-confirm is an idempotent note."""
    root = _require_root()
    state = load_state(root)
    slug = _resolve_milestone(state, args.slug)
    m = state["milestones"][slug]
    if m.get("confirmed") is True:
        _persist_task_graph(root, state, slug)     # the plan is living — recompile
        save_state(root, state)
        print(f"milestone '{slug}' already confirmed (by {m.get('confirmed_by', '?')}).")
        return
    # contract-fill gate (flow-enforcement, OPTED-IN only): a milestone that opted into
    # --await-confirm (carries a `confirmed` key) may not be confirmed until its cross-task
    # `## Shared / risky contracts` section is filled — so "confirmed" MEANS the contracts
    # were present at confirm time. A grandfathered no-key milestone keeps the plain stamp
    # (gate skipped — keeps the census + existing flows green). Validate-then-write.
    if "confirmed" in m:
        mfile = root / "milestones" / slug / MILESTONE_FILE
        md = mfile.read_text(encoding="utf-8") if mfile.exists() else ""
        if m.get("tiny"):
            # tiny-plan gate (tiny-plan-small-scope): a tiny milestone has no contracts
            # scaffold — its fill floor is the compact plan itself (Plan + Done-when).
            if (_section_unfilled(md, "## Plan")
                    or _section_unfilled(md, "## Done when")):
                _die("tiny_plan_unfilled: fill '## Plan' and '## Done when' of "
                     f"{slug}'s tiny MILESTONE.md before confirming")
        elif _section_unfilled(md, "## Shared / risky contracts"):
            _die("milestone_contracts_unfilled: fill the '## Shared / risky contracts' "
                 f"section of {slug}'s MILESTONE.md before confirming")
    who = getattr(args, "by", None) or getpass.getuser()
    m["confirmed"] = True
    m["confirmed_at"] = _now()
    m["confirmed_by"] = who
    m["actor"] = identity._actor_stamp(state)   # structured actor alongside the free-text confirmed_by
    m["updated"] = _now()
    _persist_task_graph(root, state, slug)      # edge-truth: the confirm IS the compile
    save_state(root, state)
    print(f"confirmed milestone '{slug}' (by {who}) — new-task is now open for it.")
    print(_next_footer(root, state))






















def cmd_milestone_done(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = _resolve_milestone(state, args.slug)
    members = {s: t for s, t in state.get("tasks", {}).items() if t.get("milestone") == slug}
    blockers = [s for s, t in members.items() if not _task_done(t)]
    if not members:
        _die("milestone_incomplete")  # nothing attached -> nothing proven
    if blockers:
        print(f"milestone '{slug}' has unfinished tasks:", file=sys.stderr)
        for s in blockers:
            t = members[s]
            print(f"  - {s} (phase={t.get('phase')}, gate={t.get('gate')})", file=sys.stderr)
        _die("milestone_incomplete")
    # Goal-gate (v20 dynamic-task-loop): a milestone holds until its exit criteria are
    # met. The engine READS the checkbox tally (the human's goal-met affirmation, like a
    # gate=PASS) — it never judges the goal. Fires ONLY when criteria exist, so a
    # criteria-less milestone and every pre-v20 close path stay valid. milestone-done is
    # the SOLE status->done transition; archive-milestone/compact already refuse a
    # non-done milestone, so this single gate has no back door. Refuse BEFORE any write.
    met, total = _exit_criteria(root, slug)
    if total > 0 and met < total:
        _die(f"milestone_goal_unmet: milestone '{slug}' has {met}/{total} exit criteria met "
             f"— check the remaining boxes in MILESTONE.md (the goal-gate holds the loop "
             f"open) or propose the next tasks (add.py deltas)")
    # Stamp WHO closed it BEFORE rendering the retro, so the persisted exit report records
    # the closer (identity-in-status: the retro IS the report `report <ms>` re-renders, so both
    # must reflect the same final state). In-memory only here — save_state below commits it.
    state["milestones"][slug]["done_actor"] = identity._actor_stamp(state)
    # Fail-closed: render+persist the exit report (RETRO.md) BEFORE committing the
    # status flip, so a write failure rolls back naturally (status never commits ->
    # no done-without-retro state). The retro step is read-only on state.json.
    try:
        retro_path = _write_retro(root, state, slug)
    except OSError:
        _die("retro_write_failed")
    state["milestones"][slug]["status"] = "done"
    state["milestones"][slug]["updated"] = _now()
    save_state(root, state)
    waived = [s for s, t in members.items() if t.get("gate") == "RISK-ACCEPTED"]
    tail = f" ({len(waived)} via a signed RISK-ACCEPTED waiver)" if waived else ""
    print(f"milestone '{slug}' -> done ({len(members)} tasks complete{tail}).")
    print(f"wrote {retro_path.relative_to(root.parent)}  (milestone exit report)")
    # close-time delta nudge (kernel-trim: the fold/compact ceremony died — lessons land
    # in-flight via delta-append; the close just COUNTS what §7 still holds open).
    by_comp = _collect_open_deltas(root)
    open_deltas = sum(len(v) for v in by_comp.values())
    if open_deltas:
        noun = "delta" if open_deltas == 1 else "deltas"
        print(f"note: {open_deltas} open {noun} in §7 blocks — file each into its living spec: "
              "add.py delta-append <dd> \"<lesson>\"  (review: add.py deltas)")
    open_spec = len(_collect_open_spec_deltas(root))
    if open_spec:
        noun = "delta" if open_spec == 1 else "deltas"
        print(f"note: {open_spec} open SPEC {noun} to resolve (seed as tasks, or close in §7) — review: add.py deltas")
    # the engine-sourced next step (converges the old "Confirm … archive/start the next" hint)
    print(_next_footer(root, state))


def cmd_archive_milestone(args: argparse.Namespace) -> None:
    """Light archive: collapse a DONE milestone out of active state (files stay)."""
    root = _require_root()
    state = load_state(root)
    # validate before any mutation — a reject must leave state.json byte-for-byte unchanged
    slug = _resolve_milestone(state, args.slug)
    ms = state["milestones"][slug]
    if ms.get("status") != "done":
        _die("milestone_not_done")        # run `add.py milestone-done` first; never lose live work
    tasks = state.get("tasks", {})
    members = [s for s, t in tasks.items() if t.get("milestone") == slug]
    # the status flag can go stale (a task attached AFTER milestone-done is still
    # live); re-check now so archive can never silently delete unfinished work.
    incomplete = [s for s in members if not _task_done(tasks[s])]
    if incomplete:
        print(f"milestone '{slug}' has live unfinished tasks:", file=sys.stderr)
        for s in incomplete:
            t = tasks[s]
            print(f"  - {s} (phase={t.get('phase')}, gate={t.get('gate')})", file=sys.stderr)
        _die("milestone_has_incomplete_tasks")
    # pre-archive snapshot (design-for-failure): the archived record below keeps only a
    # slug-list, so capture the full milestone + member task records to a .bak BEFORE the
    # destructive deletes — an accidental archive stays recoverable (phase/gate/waiver/deps
    # the record drops). Mirrors the .bak the guideline injector writes before mutating.
    _atomic_write(
        root / "milestones" / slug / "pre-archive-state.bak.json",
        json.dumps({"milestone": ms, "tasks": {s: tasks[s] for s in members},
                    "archived_at": _now()}, indent=2) + "\n",
    )
    # a slug-list summary (never task bodies) so the active state can't regrow,
    # yet cross-milestone deps on these tasks still resolve (see _archived_task_slugs)
    state.setdefault("archived", []).append({
        "slug": slug,
        "title": ms.get("title", slug),
        "tasks": len(members),
        "task_slugs": members,
        "archived": date.today().isoformat(),
    })
    del state["milestones"][slug]
    for s in members:
        del tasks[s]
    _deactivate_milestone(state, slug)   # drop from the active SET + pop its task entry, repointing the primary focus
    if _active_task(state) in members:   # N<=1 oracle: a NON-primary archive (new-milestone replace-to-focus leaves
        state["active_task"] = None      # active_task pointing at m1's task while primary is m2) would dangle at a deleted task
    save_state(root, state)
    print(f"archived milestone '{slug}' ({len(members)} tasks) — removed from active state.")
    print("files on disk are untouched; see `add.py status` for the archived rollup.")
    print(_next_footer(root, state))




def cmd_set_milestone(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    task = args.task
    if task not in state.get("tasks", {}):
        _die("unknown_task")
    if args.milestone == "none":
        new = None
    elif args.milestone in state.get("milestones", {}):
        new = args.milestone
    else:
        _die("unknown_milestone")
    state["tasks"][task]["milestone"] = new
    state["tasks"][task]["updated"] = _now()
    save_state(root, state)
    # keep the PLAN.md `milestone:` backlink in lockstep with state (task-milestone-backlink):
    # rewrite the header line (insert it if a grandfathered file lacks it). Degrade-safe — a
    # missing/unreadable PLAN.md never blocks the move (state is already the source of truth).
    task_md = root / "tasks" / task / "PLAN.md"
    try:
        _txt = task_md.read_text(encoding="utf-8")
        _new_txt = _set_milestone_line(_txt, _milestone_backlink_value(new))
        if _new_txt != _txt:
            _atomic_write(task_md, _new_txt)
    except OSError:
        pass
    print(f"task '{task}' -> milestone '{new}'" if new else f"task '{task}' -> milestone (none)")
    print(_next_footer(root, state))


def cmd_activate(args: argparse.Namespace) -> None:
    """Add a milestone to the active working SET and focus it — how a user works N milestones
    in parallel. Idempotent (re-activating just refocuses). Validates before mutating."""
    root = _require_root()
    state = load_state(root)
    slug = _resolve_milestone(state, args.slug)
    if state["milestones"][slug].get("status") == "done":
        _die("milestone_done")
    # PROMOTE a queued milestone: activating it flips queued→active (human-gated promotion —
    # the chosen verb, reusing `activate` rather than a separate `promote`). An already-active
    # milestone is just refocused (status unchanged), keeping the default path byte-identical.
    if state["milestones"][slug].get("status") == "queued":
        state["milestones"][slug]["status"] = "active"
    _activate_milestone(state, slug)
    save_state(root, state)
    print(f"activated '{slug}' — active: {', '.join(state['active_milestones'])}")
    print(_next_footer(root, state))


def cmd_deactivate(args: argparse.Namespace) -> None:
    """Remove a milestone from the active working SET (its files + status are untouched);
    repoints the primary focus to a remaining member. Validates before mutating."""
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    if slug not in (state.get("active_milestones") or []):
        _die("milestone_not_active")
    _deactivate_milestone(state, slug)
    save_state(root, state)
    remaining = state.get("active_milestones") or []
    print(f"deactivated '{slug}' — active: {', '.join(remaining) if remaining else '(none)'}")
    print(_next_footer(root, state))


def cmd_use(args: argparse.Namespace) -> None:
    """Set the active task to an EXISTING task (switch focus) without scaffolding a new
    one or hand-editing state.json. advance/gate/phase still take an explicit slug; `use`
    just moves the default focus, closing the only gap that forced manual state edits.
    Milestone-aware: focuses the task's OWN milestone (activating it into the set) so the
    active task is switched WITHIN that milestone, not mislabeled under a stale primary."""
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    if slug not in state.get("tasks", {}):
        _die("unknown_task")
    ms = state["tasks"][slug].get("milestone")
    if ms is not None and ms in state.get("milestones", {}):
        _activate_milestone(state, ms)        # focus the task's milestone (adds to the set if needed)
        _set_active_task(state, slug, ms)
    else:
        _set_active_task(state, slug)         # milestone-less task: scalar only (back-compat)
    save_state(root, state)
    print(f"active task -> '{slug}' (phase={state['tasks'][slug]['phase']})")
    print(_next_footer(root, state))


def _find_cycle(tasks: dict) -> list[str] | None:
    """Return a cycle path in the depends_on graph, or None. Ignores unknown deps."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {s: WHITE for s in tasks}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        color[node] = GRAY
        stack.append(node)
        for dep in tasks[node].get("depends_on") or []:
            if dep not in tasks:
                continue
            if color[dep] == GRAY:
                return stack[stack.index(dep):] + [dep]
            if color[dep] == WHITE:
                found = visit(dep)
                if found:
                    return found
        color[node] = BLACK
        stack.pop()
        return None

    for s in tasks:
        if color[s] == WHITE:
            found = visit(s)
            if found:
                return found
    return None


def _sync_task_marker(root: Path, slug: str, phase: str) -> None:
    """Keep the `phase:` line inside PLAN.md in sync with state.json."""
    task_md = root / "tasks" / slug / "PLAN.md"
    if not task_md.exists():
        return
    lines = task_md.read_text(encoding="utf-8").splitlines()
    changed = False
    for i, line in enumerate(lines):
        if line.startswith("phase:"):
            comment = ""
            if "<!--" in line:
                comment = "   " + line[line.index("<!--"):]
            lines[i] = f"phase: {phase}{comment}"
            changed = True
            break
    if changed:
        _atomic_write(task_md, "\n".join(lines) + "\n")


# --- arg parsing -------------------------------------------------------------

# --- report: the read-only "what happened" dashboard (v9) --------------------
#
# A milestone digest a human can scan: banner header · per-task PHASE TRACK ·
# rollup footer (exit-criteria · waivers · carried deltas). render_report() is
# PURE — it performs NO writes — so v9's retro-artifact can persist the SAME
# string to RETRO.md. Structured fields (phase/gate/waiver/status) come from
# state.json; prose (observe delta, deltas) is parsed from each PLAN.md and
# fails CLOSED to `(unknown)` rather than omitting silently.

# Two glyph tiers. Alignment is correct only with ASCII in column-positioned
# cells (every ASCII char is 1 display cell); Unicode glyphs sit at line-END
# (the PROGRESS track) or in non-aligned rows, where width can't break columns.
_UNICODE = {"reached": "●", "current": "◉", "pending": "○", "h": "═", "rule": "─", "bullet": "•"}
_ASCII = {"reached": "#", "current": ">", "pending": ".", "h": "=", "rule": "-", "bullet": "*"}
_GATE_SHORT = {"PASS": "PASS", "RISK-ACCEPTED": "RISK", "HARD-STOP": "STOP", "none": "—"}
# A non-empty `(verify: <citation>)` on an exit-criterion line — at least one non-whitespace
# char inside, so a bare `(verify:)`/`(verify: )` does NOT count (the mid-text substring trap).
def _goal_auto_ready(root: Path, mslug: str) -> bool:
    """True iff the milestone goal is AUTO-READY: its Exit criteria has >= 1 criterion
    AND every one cites a verifier (cited == total) — so the engine can self-verify the
    result against the goal without human judgement. A zero-criteria goal is NOT
    auto-ready (you cannot self-verify against nothing). PURE."""
    cited, total = _exit_criteria_cited(root, mslug)
    return total >= 1 and cited == total




def _resolved_test_files(root: Path, slug: str) -> list[Path]:
    """The file set the engine treats as this task's tests — the PRIMARY set wins
    when it yields any test defs, else the §4-declared set (mirrors _tests_info's
    selection). The tamper tripwire hashes exactly THIS set, never a fresh glob."""
    primary = _primary_test_files(root, slug)
    if sum(_count_test_defs(f) for f in primary) > 0:
        return primary
    return _declared_test_files(root, slug)


def _tripwire_snapshot(root: Path, slug: str, raw3: str) -> dict:
    """Freeze the md5 of the resolved red test files + the frozen §3 contract — the
    tamper baseline (verify-integrity). Keys are project-root-relative paths (stable
    across the snapshot->gate window). Tool-agnostic: hashes bytes only, never runs
    tests or measures coverage."""
    rootp = root.parent.resolve()
    tests: dict[str, str] = {}
    for f in _resolved_test_files(root, slug):
        h = _md5_file(f)
        if h is None:
            continue
        try:
            rel = str(f.resolve().relative_to(rootp))
        except (ValueError, OSError):
            rel = str(f)
        tests[rel] = h
    # strip-scaffold-at-done: fingerprint the contract CONTENT (comment-normalized, see
    # _contract_fingerprint) so the at-done comment strip is invisible to the tamper guard; a real
    # fenced-shape edit still changes it. Mirrored byte-for-byte in _tripwire_divergence.
    return {"contract_md5": _contract_fingerprint(raw3), "tests": tests}


def _tripwire_divergence(root: Path, slug: str, tw: dict) -> list[str]:
    """Tamper codes for a PRESENT snapshot; [] means clean. Re-reads each tracked
    path directly (never re-globs), so a weakened, deleted, or unreadable test file
    and an edited frozen §3 all surface. Fail-closed: an unreadable file -> diverged."""
    diffs: list[str] = []
    # compare the contract CONTENT fingerprint (strip-scaffold-at-done) — same normalization as the
    # snapshot, so the at-done comment strip never reads as tampering; a real shape edit still does.
    if _contract_fingerprint(_raw_phase_bodies(root, slug).get(3, "")) != tw.get("contract_md5"):
        diffs.append("contract_tampered")
    rootp = root.parent.resolve()
    for rel, snap in (tw.get("tests") or {}).items():
        if _md5_file(rootp / rel) != snap:
            diffs.append(f"build_tampered:{rel}")
    return diffs


# ── §5 scope gate (build-scope-lock): touched ⊆ declared, from bytes alone ──────────
# The walk's NAMED exclusion set — ONE constant; widening it is an additive
# change-request, never silent. `.add` is engine domain (tripwire + audit guard it);
# the rest is VCS/bytecode/OS junk + code-intelligence tool caches + gitignored BUILD
# ARTIFACTS, none with build signal. `.serena` holds a symbol index that re-writes itself
# whenever a source file changes (md5 churn from a build edit must never read as an
# out-of-scope touch — the dogfooding lesson that added it). A regenerated artifact is
# likewise NOT a source touch — counting one produced repeated false `scope_violation`s in
# consuming projects (`.next/`, `coverage/`, `tsconfig.tsbuildinfo`, whose `incremental`
# rewrite even races a clean re-snapshot), so they are pruned here too.
# `.claude` is an agent-tool internal dir (config/skills/worktrees) like `.serena` — never a
# task's declared source; without it, the walk descends into `.claude/worktrees/<wt>/` (linked
# git worktrees: full branch checkouts) and their churn produces false `scope_violation`s.
_SCOPE_EXCLUDE_DIRS = (".git", ".add", ".claude", "__pycache__", "node_modules", ".serena",
                       ".next", "coverage", "test-results", ".pytest_cache",
                       # tool-owned python dirs (scope-walk-prune): an in-workspace
                       # virtualenv read as out-of-scope writes in 3/3 re-measure reps.
                       # dist/build stay WATCHED — they can be a project's real write-set.
                       ".venv", "venv", ".tox", ".mypy_cache", ".ruff_cache", ".eggs")
_SCOPE_EXCLUDE_FILES = (".DS_Store", ".coverage")      # plus *.pyc / *.tsbuildinfo by suffix
_SCOPE_EXCLUDE_SUFFIXES = (".pyc", ".tsbuildinfo")


# ── component registry (component-aware-add): declared components + task binding ─────
# OPT-IN + DEGRADE-SAFE: with no .add/components.toml every reader is byte-identical to
# pre-component ADD. A read NEVER raises (absent/unreadable/malformed → {} / dropped
# cover); the loud surface is _component_findings, consumed by the scope gate (cmd_check).










# ── cross-component contracts (cross-component-contract) ──────────────────────────────────
# OPT-IN + DEGRADE-SAFE, like the component readers: no [contract.*] / no produces|consumes
# header ⇒ every path below is byte-identical to pre-contract ADD. A read NEVER raises.












# kernel-trim (ADD 2.0 M5): the components.toml schema-lint died with the components pillar.
_SCHEMA_TYPENAME = {str: "a string", list: "a list"}




def _declared_scope(root: Path, slug: str) -> list[str] | None:
    """Resolve the §5 'Scope (may touch):' declaration to project-root-relative
    strings (directory tokens keep a trailing '/'). The frozen scope-decl-template
    grammar: the §4 token rules — backticked spans on the FIRST declaring line ·
    './…' -> task dir · contains '/' -> project root · bare -> sibling of the
    previous token's dir · v2 confinement drops everything outside the project
    root, fail-closed — with ONE divergence: a directory token covers its WHOLE
    subtree (containment, judged by _in_scope). None = no Scope line (UNDECLARED,
    grandfathered — never retro-red); [] = a line whose every token was dropped
    (a garbage declaration grants NO cover).

    kernel-trim (ADD 2.0 M5): the component-root scope join died with the components
    pillar — only the explicit backticked declaration grants cover now."""
    _rb = _raw_phase_bodies(root, slug)
    # expectations-first: Scope moved into §3 PLAN's `### Build-strategy`; read §3 first,
    # then a legacy §5 body (this task + pre-reorder tasks keep Scope in §5).
    m = (re.search(r"^\s*Scope \(may touch\):.*$", _rb.get(3, ""), re.M)
         or re.search(r"^\s*Scope \(may touch\):.*$", _rb.get(5, ""), re.M))
    if not m:
        return None
    tdir = root / "tasks" / slug
    rootp = root.parent.resolve()
    out: list[str] = []
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
            rp = p.resolve()
            rel = str(rp.relative_to(rootp))
            if tok.endswith("/") or rp.is_dir():
                prev_dir, rel = p, rel.rstrip("/") + "/"
            else:
                prev_dir = p.parent
        except OSError:
            continue
        if rel not in out:
            out.append(rel)
    return out


def _scope_walk(rootp: Path) -> dict[str, str]:
    """{project-root-relative path: md5} over the project tree, pruning
    _SCOPE_EXCLUDE_DIRS at any depth and skipping bytecode/OS junk +
    gitignored build artifacts (_SCOPE_EXCLUDE_FILES/_SCOPE_EXCLUDE_SUFFIXES). A file
    unreadable at SNAPSHOT time is skipped; at the GATE the resulting absence
    reads as a touch (fail-closed at the biting end). Bytes only — no git."""
    files: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(rootp):
        # *.egg-info is PROJECT-DERIVED (app.egg-info) — no literal covers it; suffix-prune
        # (egg-info-prune: 3/3 run-3 reps tripped scope_violation on pip install -e .'s output).
        dirnames[:] = [d for d in dirnames
                       if d not in _SCOPE_EXCLUDE_DIRS and not d.endswith(".egg-info")]
        for name in filenames:
            if name in _SCOPE_EXCLUDE_FILES or name.endswith(_SCOPE_EXCLUDE_SUFFIXES):
                continue
            p = Path(dirpath) / name
            h = _md5_file(p)
            if h is None:
                continue
            try:
                files[str(p.relative_to(rootp))] = h
            except ValueError:
                continue
    return files


def _scope_findings(root: Path, slug: str, anchor: dict) -> tuple[str | None, list[str]]:
    """(tamper_reason, out_of_scope_touches) for a scope-anchored task. PURE read.
    The sidecar is integrity-checked against the state.json anchor BEFORE it is
    trusted; touched = modified ∪ added ∪ deleted vs the snapshot."""
    side = root / "tasks" / slug / "scope-snapshot.json"
    try:
        raw = side.read_text(encoding="utf-8")
    except OSError:
        return "missing", []
    if _md5_text(raw) != anchor.get("snapshot_md5"):
        return "diverged", []
    try:
        snap = json.loads(raw).get("files", {})
    except (ValueError, AttributeError):
        return "unparseable", []
    if not isinstance(snap, dict):
        return "unparseable", []
    now = _scope_walk(root.parent.resolve())
    touched = sorted({k for k, v in snap.items() if now.get(k) != v}
                     | {k for k in now if k not in snap})
    declared = anchor.get("declared") or []
    return None, [p for p in touched if not _in_scope(p, declared)]


def _scope_guard(root: Path, state: dict, slug: str) -> None:
    """Refuse a COMPLETING gate when the build touched outside its declared §5
    Scope (build-scope-lock). The anchor (state.json) and the sidecar co-witness
    each other — born in the same tests->build crossing, so EITHER single-file
    erase is caught (v2, refute-driven): an anchor-less task whose sidecar still
    EXISTS is scope_anchor_missing, never a silent skip. Both absent -> UNDECLARED
    or legacy: silent, the grandfather rule (the simultaneous two-file erase is
    the explicitly accepted floor — the tripwire shares it). Sits directly after
    _tamper_guard, BEFORE the waiver write, so a violation is never launderable
    through RISK-ACCEPTED; HARD-STOP never calls it (stopping is always allowed).

    Routing (scope-violation-heal, build-scope-lock 3/3) — tripwire-parity: the
    RECOVERABLE findings (an out-of-scope touch, a present-but-wrong sidecar) are
    fixable from BUILD, so they enter the SAME bounded self-heal loop the tamper
    tripwire uses (_heal_or_escalate, shared HEAL_CAP) — return to build for an
    honest redo (exit 3), then HARD-STOP at the cap. The ERASED baselines stay
    die-in-place (exit 1, no heal): a redo cannot recreate an erased anchor or a
    deleted sidecar — that is tripwire_missing parity. Every heal reason CARRIES
    its named code, so the existing refusal-token assertions still match."""
    anchor = state["tasks"][slug].get("scope")
    if not isinstance(anchor, dict):
        if (root / "tasks" / slug / "scope-snapshot.json").exists():
            _die(f"scope_anchor_missing: task '{slug}' carries a scope-snapshot.json "
                 "but no state.json anchor — the touch baseline was erased from "
                 "state; re-establish it (re-advance through tests->build) before "
                 "completing")
        return
    tamper, out = _scope_findings(root, slug, anchor)
    if tamper == "missing":
        # erased baseline — a redo cannot recreate the evidence (tripwire_missing parity)
        _die(f"scope_snapshot_tampered: task '{slug}' — scope-snapshot.json is "
             "missing against its state.json anchor; the touch baseline is "
             "evidence and must survive the build untouched")
    if tamper:
        # diverged | unparseable — present-but-wrong bytes are revertable from build
        _heal_or_escalate(root, state, slug, source="scope-tamper",
                          reason=(f"scope_snapshot_tampered: task '{slug}' — "
                                  f"scope-snapshot.json is {tamper} against its "
                                  "state.json anchor; revert it to the snapshot bytes"))
    if out:
        shown = " · ".join(out[:5])
        _heal_or_escalate(root, state, slug, source="scope",
                          reason=(f"scope_violation: task '{slug}' touched outside its "
                                  f"declared §5 Scope — {shown} ({len(out)} total)"))


def _record_round(task: dict, *, source: str, note: str | None = None) -> None:
    """Record ONE verify->build return trip — a visible 'round' (round-visible-runs).

    Uncapped and OBSERVATIONAL: rounds never gate, never cap, never move a phase — they
    make a dynamic verify->fix workflow legible in status and the route traces. Distinct
    from the heal counter (the CHEAT-classed, capped subset); a heal return records BOTH.
    Caller owns the save — the increment rides the same atomic write as the phase move."""
    r = task.setdefault("rounds", {"count": 0, "history": []})
    r["count"] = r.get("count", 0) + 1
    r.setdefault("history", []).append({"at": _now(), "source": source, "note": note})


def _heal_or_escalate(root: Path, state: dict, slug: str, *, reason: str, source: str) -> None:
    """The bounded self-heal router (verify-integrity, heal-then-escalate). Called ONLY when
    a cheat is CONFIRMED at this point — mechanical (tripwire divergence, source "tamper") or
    semantic (an agent-reported refute-read finding, source "refute-read").

    attempts < HEAL_CAP -> record the attempt, return the task to BUILD for an honest redo,
    exit 3 (a redo signal, NOT a completing outcome). The phase is set DIRECTLY (never via
    advance) so the tripwire baseline is not re-snapshotted mid-loop. The increment is saved
    BEFORE the exit, so a re-run never grants a free attempt (atomic, fail-closed).

    attempts >= HEAL_CAP -> the next confirmed cheat: record gate = HARD-STOP and escalate to
    the human (_die). A gamed green is NEVER auto-passed; the loop is never unbounded. The
    counter is MONOTONIC — it never auto-resets (cmd_phase is unguarded, so a reset would be a
    zero-human cap bypass)."""
    t = state["tasks"][slug]
    heal = t.setdefault("heal", {"attempts": 0, "history": []})
    entry = {"at": _now(), "reason": reason, "source": source}
    if heal.get("attempts", 0) >= HEAL_CAP:
        heal.setdefault("history", []).append(entry)
        t["gate"] = "HARD-STOP"               # never a completing outcome; phase stays put
        t["updated"] = _now()
        save_state(root, state)               # the escalation verdict is durable
        _die(f"heal_exhausted: task '{slug}' — a confirmed cheat ({reason}) persisted past "
             f"{HEAL_CAP} honest re-build attempts. HARD-STOP escalated to the human: fix the "
             "spec (change-request -> re-freeze) or abandon. A gamed green is never auto-passed.")
    heal["attempts"] = heal.get("attempts", 0) + 1
    heal.setdefault("history", []).append(entry)
    _record_round(t, source=source)           # a heal return is ALSO a visible round (uncapped view)
    t["phase"] = "build"                      # DIRECT — never via advance (no re-snapshot)
    t["updated"] = _now()
    _sync_task_marker(root, slug, "build")
    save_state(root, state)                   # the increment is durable BEFORE the exit
    # scope-gate-repair-path M2: the advice tail branches by SOURCE. A scope
    # violation's honest repair is usually a WRONG/DEFAULT §5 declaration, not a
    # tampered file — the generic revert advice sent the live-benchmark agent
    # source-diving for ~10 turns to discover `re-cross`. Message layer only:
    # counter/exit/history above are identical for every source.
    if source == "scope":
        advice = ("repair: 1. edit the §5 Scope line to cover the real paths the "
                  "build touches · 2. add.py re-cross --by <name> (re-snapshots "
                  "scope + tripwire) · 3. add.py advance, then add.py gate PASS. "
                  "If the touch was genuinely out of bounds, revert it instead and "
                  "advance back to verify.")
    else:
        advice = ("Revert the tampered file or rebuild src honestly, then advance "
                  "back to verify.")
    print(f"return_to_build: task '{slug}' — cheat detected ({reason}); RETURN TO BUILD for an "
          f"HONEST redo, attempt {heal['attempts']} of {HEAL_CAP}. {advice}")
    raise SystemExit(3)                       # redo signal (distinct from _die's 1, argparse's 2)




def _tamper_guard(root: Path, state: dict, slug: str) -> None:
    """HARD-STOP a COMPLETING gate when the tripwire shows tampering — the method's
    first mechanical cheat block (verify-integrity). Tri-state, co-witnessed by
    flag_verified: present+diverged -> stop; absent+flag_verified -> suspicious stop
    (the snapshot was crossed-then-erased); absent+not-verified -> skip (a legacy task
    or one that never crossed tests->build). A cheat is HARD-STOP-class — this runs
    for RISK-ACCEPTED too, BEFORE the waiver is recorded, so it is never launderable."""
    t = state["tasks"][slug]
    tw = t.get("tripwire")
    if tw is None:
        if t.get("flag_verified"):
            _die(f"tripwire_missing: task '{slug}' crossed tests->build "
                 "(flag_verified) but carries no tamper snapshot — the evidence "
                 "baseline was erased. Re-establish it (reopen -> re-advance through "
                 "tests->build) before completing; a missing baseline is HARD-STOP.")
        return  # legacy: predates the tripwire, or never crossed tests->build
    diffs = _tripwire_divergence(root, slug, tw)
    if diffs:
        # heal-then-escalate (verify-integrity): a mechanical cheat no longer dies on sight —
        # it enters the bounded self-heal loop (≤HEAL_CAP honest re-build attempts, then a
        # HARD-STOP escalation). Still HARD-STOP-class: never auto-passed, never launderable
        # (this runs BEFORE the waiver write). The router returns to build or escalates.
        _heal_or_escalate(root, state, slug,
                          reason="tamper_detected:" + ",".join(diffs), source="tamper")


def report_data(root: Path, state: dict, mslug: str) -> dict:
    """The single source of FACTS for a milestone report — pure, NO writes.
    Both the text dashboard (render_report) and `report --json` render from this,
    so the human view and the raw data can never disagree. This is the 'raw data
    capture' the agent formats into a templated report."""
    ms = (state.get("milestones") or {}).get(mslug, {})
    title, goal = _milestone_doc(root, mslug)
    tasks = state.get("tasks") or {}
    members = [(s, t) for s, t in tasks.items() if t.get("milestone") == mslug]
    met, total_ec = _exit_criteria(root, mslug)

    task_rows, waivers, all_deltas = [], [], []
    for slug, t in members:
        observe, deltas = _task_prose(root, slug)
        phase = t.get("phase", "direction")
        gate = t.get("gate", "none")
        n_tests, t_declared = _tests_info(root, slug)
        row = {
            "slug": slug,
            "title": t.get("title", slug),
            "phase": phase,
            "phase_index": PHASES.index(phase) if phase in PHASES else 0,
            "done": _task_done(t),
            "gate": gate,
            "gate_actor": t.get("gate_actor"),   # WHO recorded the verdict (None when unstamped)
            "owner": t.get("owner"),             # WHO is accountable (None when unassigned)
            "assignee": t.get("assignee"),       # WHO is working it (None when unassigned)
            "tests": n_tests,
            "tests_declared": t_declared,
            "observe": observe,
            "deltas": deltas,
            "waiver": t.get("waiver"),
        }
        task_rows.append(row)
        if t.get("waiver"):
            w = t["waiver"]
            waivers.append({"slug": slug, "owner": w.get("owner", "?"),
                            "ticket": w.get("ticket", "?"), "expires": w.get("expires", "?")})
        all_deltas.extend(deltas)

    return {
        "milestone": {"slug": mslug, "title": title, "goal": goal,
                      "status": ms.get("status", "active"),
                      "done_actor": ms.get("done_actor"),    # WHO closed it (None when unstamped/open)
                      "owner": ms.get("owner"),              # WHO is accountable for the milestone
                      "assignee": ms.get("assignee")},       # WHO is working it (None when unassigned)
        "summary": {
            "tasks_done": sum(1 for r in task_rows if r["done"]),
            "tasks_total": len(task_rows),
            "gates": {"PASS": sum(1 for r in task_rows if r["gate"] == "PASS"),
                      "RISK-ACCEPTED": sum(1 for r in task_rows if r["gate"] == "RISK-ACCEPTED"),
                      "HARD-STOP": sum(1 for r in task_rows if r["gate"] == "HARD-STOP")},
            "exit_criteria": {"met": met, "total": total_ec},
            # project-wide open SPEC-delta count (uniform with status/milestone-done/compact)
            "open_spec": len(_collect_open_spec_deltas(root)),
        },
        "tasks": task_rows,
        "waivers": waivers,
        "deltas": all_deltas,
        # additive (v13-1): MILESTONE.md-planned slugs with no PLAN.md yet —
        # the plan-vs-state diff DECIDE NEXT was blind to; [] when none
        "planned_unscaffolded": _planned_unscaffolded(root, mslug),
    }


def _clean_phase_body(body: str) -> str:
    """Strip HTML comments (which include the `EXIT:` markers) and surrounding blank
    lines from a §N body. A body that is empty or ONLY `<...>` angle-placeholders after
    cleaning -> "(empty)" (fail-closed; never a silent gap). Otherwise the cleaned text
    is returned with its internal line structure intact (scenarios/code stay readable)."""
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    lines = [ln.rstrip() for ln in body.split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    meaningful = [ln for ln in lines
                  if ln.strip() and not re.fullmatch(r"\s*<.*>\s*", ln)]
    return "\n".join(lines) if meaningful else "(empty)"


# phase-merge-specify: the PLAN.md §-sections each work phase OWNS. Sections never
# renumber (§3 is the frozen contract everywhere); the phase list shrank instead, so
# specify owns two sections. Explicit — never derive a section from a phase index.
_PHASE_SECTIONS = {"direction": (1, 2, 3, 4),
                   "build": (5,), "verify": (6, 7)}


def task_phases(root: Path, slug: str) -> list[dict]:
    """The frozen per-task PHASE-DETAIL shape (v9-1): parse the task section blocks into
    the non-terminal phases specify→verify. PURE — NO writes. Each entry is
    { "phase": <name>, "n": <0..len(names)-1>, "body": <cleaned text | "(empty)"> }.

    The heading scan lives in _phase_spans (shared with the decide digest); this view
    CLEANS each body. Missing file / missing section / placeholder-only body ->
    "(empty)" (fail-closed). The bound tracks len(names) so it follows PHASES length."""
    names = PHASES[:-1]  # specify..verify; "done" is a terminal STATE, not a section
    f = root / "tasks" / slug / "PLAN.md"
    try:
        text = f.read_text(encoding="utf-8")
    except OSError:   # missing OR unreadable -> every phase fail-closed to "(empty)"
        return [{"phase": names[n], "n": n, "body": "(empty)"} for n in range(len(names))]
    spans = _phase_spans(text)
    # spans is keyed by the PLAN.md SECTION number (§1 SPECIFY .. §7 OBSERVE). The §-sections
    # are the stable API and KEEP their numbers; the phase list no longer aligns 1:1 with
    # them (phase-merge-specify: the specify phase owns §1 AND §2) — so the mapping is an
    # explicit table, never derived from the phase index (the off-by-one bug class).
    out = []
    for n, name in enumerate(names):
        parts = [_clean_phase_body(spans[s]) for s in _PHASE_SECTIONS[name] if s in spans]
        parts = [b for b in parts if b != "(empty)"]
        out.append({"phase": name, "n": n, "body": "\n\n".join(parts) if parts else "(empty)"})
    return out


def _task_title(root: Path, slug: str) -> str:
    """The task's display title from PLAN.md line 1 `# PLAN: <title>` (fail-soft: the
    slug if the file or the header line is missing)."""
    f = root / "tasks" / slug / "PLAN.md"
    try:
        text = f.read_text(encoding="utf-8")
    except OSError:   # missing OR unreadable -> fail-soft to the slug
        return slug
    for ln in text.splitlines():
        m = re.match(r"^#\s*TASK:\s*(.+)", ln)
        if m:
            return m.group(1).strip()
    return slug


def _detail_body(body: str, width: int) -> list[str]:
    """Indent a phase body under its block, soft-wrapping over-long physical lines on
    spaces while preserving blank lines + each line's leading indent (so scenarios and
    contract code keep their shape). Fenced ``` blocks are exempt: delimiter lines and
    everything inside an open fence emit BYTE-VERBATIM (indent + raw — no wrap, no
    whitespace collapse, even past width) so a copied contract round-trips after
    stripping the uniform indent; an unclosed fence runs verbatim to the §body end
    (fail-open). Drill-down = reading is the point, never clipped."""
    indent = "   "
    out: list[str] = []
    fenced = False
    for raw in body.split("\n"):
        is_delim = raw.lstrip().startswith("```")
        if fenced or is_delim:
            fenced = fenced != is_delim   # delimiter toggles; content keeps state
            out.append(indent + raw if raw.strip() else "")
            continue
        if not raw.strip():
            out.append("")
            continue
        if len(indent) + len(raw) <= width:
            out.append(indent + raw)
            continue
        lead = raw[: len(raw) - len(raw.lstrip())]
        prefix = indent + lead
        cur = ""
        for w in raw.split():
            cand = f"{cur} {w}".strip()
            if cur and len(prefix) + len(cand) > width:
                out.append(prefix + cur)
                cur = w
            else:
                cur = cand
        if cur:
            out.append(prefix + cur)
    return out


def render_task_detail(root: Path, state: dict, mslug: str, slug: str, *,
                       width: int = _DEFAULT_WIDTH, ascii: bool = False) -> str:
    """Format ONE task's pre-done phase blocks (specify→verify) as the read-only PHASE
    DETAIL: each block shows its number+name, a reached/current/pending marker (from the
    task's state phase), and its captured §N body (fail-closed to "(empty)"). The verify
    block additionally prints the recorded GATE from state.json — authoritative, NEVER
    parsed from prose. Returns PLAIN text (no ANSI); color is a tty-only skin in
    cmd_report. PURE — NO writes (the v9 read-only discipline, carried)."""
    g = _ASCII if ascii else _UNICODE
    W = width
    banner, rule = g["h"] * W, " " + g["rule"] * (W - 1)
    t = (state.get("tasks") or {}).get(slug, {})
    phase = t.get("phase", "direction")
    gate = t.get("gate", "none")
    ci = PHASES.index(phase) if phase in PHASES else 0

    L = [banner, f" {mslug} · {slug} · {_task_title(root, slug)}", banner]
    L.append(f" PHASE {phase}    GATE {gate}")
    L.append(banner)
    for p in task_phases(root, slug):
        i = p["n"]   # n IS the PHASES index now (specify=0 .. verify=4)
        mk = (g["reached"] if (phase == "done" or i < ci)
              else g["current"] if i == ci else g["pending"])
        L.append("")
        L.append(f" {mk} {p['n']} {p['phase'].upper()}")
        L.append(rule)
        if p["phase"] == "verify":   # the recorded gate, sourced from state (not prose)
            L.append(f"   GATE  {gate}")
        if p["body"] == "(empty)":
            L.append("   (empty)")
        else:
            L.extend(_detail_body(p["body"], W))
    L.append(banner)
    return "\n".join(L)


def _fmt_actor(actor: dict | None) -> str:
    """Format a recorded actor stamp `{name,email,source}` as `name [<email>]` for the
    report surface — "" when absent (user-identity: present-only render, no placeholder)."""
    if not actor:
        return ""
    email = f" <{actor['email']}>" if actor.get("email") else ""
    return f"{actor.get('name', '')}{email}"


def _fmt_ownership(rec: dict) -> str:
    """Format a record's owner/assignee as `owner: <name> · assignee: <name>` for the
    surface (ownership-assignment) — present-only: each role appears only when set, and
    "" when neither is. Reuses _fmt_actor to render each `{name,email,source}` actor."""
    bits = [f"{role}: {_fmt_actor(rec[role])}" for role in ("owner", "assignee")
            if rec.get(role) and rec[role].get("name")]   # skip a hand-edited blank-name record
    return " · ".join(bits)


def render_report(root: Path, state: dict, mslug: str, *,
                  width: int = _DEFAULT_WIDTH, ascii: bool = False) -> str:
    """Format the FACTS (report_data) as the text DASHBOARD — verdict-first header,
    left-aligned ASCII columns (alignment-safe on any locale), Unicode/ASCII glyph
    tier, one legend. Returns PLAIN text (no ANSI); color is a tty-only layer in
    cmd_report so the persisted RETRO.md string stays plain. NO writes."""
    d = report_data(root, state, mslug)
    g = _ASCII if ascii else _UNICODE
    W = width
    banner, rule = g["h"] * W, g["rule"] * W
    m, s = d["milestone"], d["summary"]
    done, total = s["tasks_done"], s["tasks_total"]
    gates, ec = s["gates"], s["exit_criteria"]

    verdict = ("BLOCKED" if gates["HARD-STOP"]
               else "DONE" if total and done == total else "ACTIVE")
    gbits = []
    if gates["PASS"]:
        gbits.append(f"{gates['PASS']} PASS")
    if gates["RISK-ACCEPTED"]:
        gbits.append(f"{gates['RISK-ACCEPTED']} RISK")
    if gates["HARD-STOP"]:
        gbits.append(f"{gates['HARD-STOP']} STOP")
    gate_txt = " ".join(gbits) if gbits else "none"
    waiver_txt = f"{len(d['waivers'])}" if d["waivers"] else "none"

    # Header: title in the banner, then a 2-col aligned label grid (ASCII-safe cells,
    # so no width breakage) — VERDICT leads on its own line for emphasis.
    L = [banner, f" {m['slug']} · {m['title']}", banner]
    L.append(f" {'VERDICT':<9} {verdict}")
    L.append(f" {'TASKS':<9} {f'{done}/{total} done':<18} {'CRITERIA':<9} {ec['met']}/{ec['total']} met")
    L.append(f" {'GATES':<9} {gate_txt:<18} {'WAIVERS':<9} {waiver_txt}")
    L.append("")
    L.extend(_wrap(m["goal"], W - 7, " goal  "))
    # who closed the milestone (user-identity) — present-only, never a placeholder
    if m.get("done_actor"):
        L.append(f" closed by {_fmt_actor(m['done_actor'])}")
    # who owns/works the milestone (ownership-assignment) — present-only
    _ms_own = _fmt_ownership(m)
    if _ms_own:
        L.append(f" owned by {_ms_own}")
    L.append("")
    if d["tasks"]:
        L.append(f" {'TASK':<27} {'PHASE':<9} {'GATE':<4} {'TESTS':<5} PROGRESS")
        L.append(" " + g["rule"] * (W - 1))
        for r in d["tasks"]:
            slug = _clip(r["slug"], 27)
            gate = _GATE_SHORT.get(r["gate"], r["gate"])
            tests = f"{r['tests']}†" if r.get("tests_declared") else str(r["tests"])
            L.append(f" {slug:<27} {r['phase']:<9} {gate:<4} "
                     f"{tests:<5} {_phase_track(r['phase'], g)}")
        L.append(f" legend  {g['reached']} reached  {g['current']} current  "
                 f"{g['pending']} pending   spec→…→done")
        if any(r.get("tests_declared") for r in d["tasks"]):
            L.append(" † counted at the §4-declared path")
        # who recorded each verdict (user-identity) — present-only audit trail
        gated = [r for r in d["tasks"] if r.get("gate_actor")]
        if gated:
            L.append("")
            L.append(" GATED BY")
            for r in gated:
                short = _GATE_SHORT.get(r["gate"], r["gate"])
                L.append(f"   {_clip(r['slug'], 24):<24} {short:<4} {_fmt_actor(r['gate_actor'])}")
        # who owns/works each task (ownership-assignment) — present-only, mirror of GATED BY
        owned = [r for r in d["tasks"] if r.get("owner") or r.get("assignee")]
        if owned:
            L.append("")
            L.append(" OWNED BY")
            for r in owned:
                L.append(f"   {_clip(r['slug'], 24):<24} {_fmt_ownership(r)}")
    else:
        L.append(" (no tasks yet)")
    L.append("")
    L.append(f" EXIT CRITERIA  {_bar(ec['met'], ec['total'], 10, g)} {ec['met']}/{ec['total']} met")
    if d["waivers"]:   # header grid carries the count; show DETAILS here only when present
        L.append("")
        L.append(f" WAIVERS ({len(d['waivers'])})")
        for w in d["waivers"]:
            L.extend(_wrap(f"{w['slug']}: {w['owner']} · {w['ticket']} · expires {w['expires']}",
                           W - 5, f"   {g['bullet']} "))
    L.append("")
    if d["deltas"]:    # the retro's payload — word-wrapped to FULL readable text, never clipped
        L.append(f" LEARNINGS ({len(d['deltas'])} carried)")
        for x in d["deltas"]:
            L.extend(_wrap(x, W - 5, f"   {g['bullet']} "))
    else:
        L.append(" LEARNINGS      none")
    if d.get("summary", {}).get("open_spec"):   # project-wide open SPEC-delta nudge (read-only)
        n = d["summary"]["open_spec"]
        noun = "delta" if n == 1 else "deltas"
        L.append("")
        L.append(f" SPEC DELTAS    {n} open {noun} — resolve: new-task --from-delta (or close in §7)")
    L.append("")   # DECIDE NEXT footer (v13): always present, APPEND-ONLY
    L.extend(_wrap(_decide_next_base(state, d), W - 15, " DECIDE NEXT  "))
    if _planned_hint(d):   # own segment so the phrase never splits mid-token
        L.extend(_wrap(_planned_hint(d).removeprefix(" — "), W - 15, " " * 14))
    L.append(banner)
    return "\n".join(L)


# ---- decide digest (v13 decide-digest, frozen §3) ---------------------------
# Decision markers: prose conventions surfaced VERBATIM. The engine EXTRACTS; it
# never interprets, scores, or filters — add.py stays judgment-free, the human
# signature is the gate.
_MARKER_PREFIXES = (("⚠", "⚠"), ("- [~]", "[~]"), ("- [ ]", "[ ]"))
_FRONT_PHASES = ("direction",)   # phase-collapse-3: the whole front is one span


def _decision_markers(body: str, section: int) -> list[dict]:
    """Extract decision markers from a RAW §body: a line whose first non-space chars
    are `⚠` / `- [~]` / `- [ ]`, PLUS its continuation lines (immediately following
    non-blank lines indented deeper than the marker). text is BYTE-VERBATIM — never
    re-wrapped, never clipped. Fail-open by design (a differently-worded item is
    missed); the always-printed count keeps that visible."""
    items: list[dict] = []
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i]
        stripped = ln.lstrip()
        tag = next((t for p, t in _MARKER_PREFIXES if stripped.startswith(p)), None)
        if tag is None:
            i += 1
            continue
        indent = len(ln) - len(stripped)
        block = [ln]
        j = i + 1
        while j < len(lines):
            nxt = lines[j]
            ns = nxt.lstrip()
            if ns and (len(nxt) - len(ns)) > indent:
                block.append(nxt)
                j += 1
            else:
                break
        items.append({"marker": tag, "section": section, "text": "\n".join(block)})
        i = j
    return items


def _contract_frozen(raw3: str) -> bool:
    """§3's `Status:` line is the freeze signal (v12 precedent: the freeze is
    artifact-observable; no engine flag). Missing Status -> DRAFT (fail-closed)."""
    return any(re.match(r"\s*Status:\s*FROZEN", ln) for ln in raw3.splitlines())


def _section0_anchors(body: str) -> str | None:
    """The value of a body's "Anchors the contract cites:" line, stripped. None when the
    body carries no such line. PURE. (expectations-first: the line lives in the §3 PLAN
    `### Grounding` sub-block now; still reads a legacy §0 body the same way.)"""
    for ln in body.splitlines():
        m = re.match(r"\s*Anchors the contract cites:\s*(.*)$", ln)
        if m:
            return m.group(1).strip()
    return None


def _grounded_state(raw: dict[int, str]) -> bool | None:
    """Tri-state grounding measure over a task's RAW §bodies (measure-not-block):
      True  — the §3 PLAN "Anchors the contract cites:" line is filled (real content)
      False — the line exists but is the "<…>" placeholder / empty
      None  — no grounding sub-block (a pre-plan / legacy task), OR no Anchors line
    Reads §3 PLAN first, then a legacy §0 GROUND body (fallback). PURE; fail-open (an
    unparseable body -> None, never a false False). The freeze review checklist asks the
    human to confirm True; status/check surface it, never block on it."""
    for n in (3, 0):
        body = raw.get(n)
        if body is None:
            continue
        anchors = _section0_anchors(body)
        if anchors is not None:
            return bool(anchors) and not anchors.startswith("<")
    return None


def _task_grounded(root: Path, slug: str) -> bool | None:
    """`_grounded_state` for one task by slug (reads its RAW §bodies). Read-only."""
    return _grounded_state(_raw_phase_bodies(root, slug))


_FLAG_LABEL_RE = re.compile(r"Least-sure flag surfaced at freeze\s*:", re.I)
_FLAG_PART_RE = re.compile(
    r"\[(?:spec|scenario|contract|test)(?:/(?:spec|scenario|contract|test))*\]")
_FLAG_NONE_ESCAPE_RE = re.compile(
    r"none material\s*[—-]+\s*biggest risk\s*:\s*\S", re.I)


def _flag_well_formed(raw3: str) -> bool:
    """A FROZEN §3 must surface a WELL-FORMED lowest-confidence flag — the unit
    that NAMES which part of the bundle is least certain. Well-formed := the label
    phrase + a unit carrying >=1 [part] tag (part in spec/scenario/contract/test,
    slash-joinable like [spec/contract]) + substantive content. A bare 'none' is
    refused unless it takes the honest escape 'none material — biggest risk: X'.
    why/cost stay a human-read convention, never machine keywords (evidence: the
    lived flags use em-dash/prose, never literal because/if-wrong). HTML comments
    (template hints) never count. Fence-aware (mirrors _strip_live_scaffold): a
    frozen §3 may legitimately quote a bare `<!--` inside its own fenced code
    block (documenting an HTML-comment invariant) — that must never merge with
    an unrelated `-->` found later in the raw text. PURE — fail-closed on a
    missing label."""
    segs = re.split(r"(```.*?```)", raw3, flags=re.DOTALL)
    for i in range(0, len(segs), 2):      # even indices = OUTSIDE any fence
        segs[i] = re.sub(r"<!--.*?-->", "", segs[i], flags=re.S)
    body = "".join(segs)
    m = _FLAG_LABEL_RE.search(body)
    if not m:
        return False
    unit = body[m.end():].strip()
    if not unit:
        return False
    if _FLAG_NONE_ESCAPE_RE.search(unit):    # the honest-none escape — no tag needed
        return True
    if not _FLAG_PART_RE.search(unit):       # must name WHICH part is uncertain
        return False
    residue = _FLAG_PART_RE.sub("", unit).replace("⚠", "").strip(" -—·\n\t")
    return len(residue) >= 3                  # substantive content beyond the tag(s)


# plan-in-report: the §3 Build-strategy plan-of-action fields, in a fixed order, surfaced at
# the freeze so the human approves HOW (not just the contract SHAPE). Each field is authored on
# its OWN physical line in the template, so the value is captured single-line (NOT via
# _capture_wrapped — its `Word Word:` continuation boundary doesn't recognize a label like
# "Known-problem fixes:" and would bleed one field's value into the next). A field whose value
# is a template placeholder (leading "<", or the bare "./src/" Scope default) is skipped; a
# trailing "   <hint>" on a real value is stripped. PURE.
_PLAN_FIELDS = ("Scope (may touch)", "Strategy (ordered batches)", "Approach (domain strategy)",
                "Persona (optional)", "Spawn isolation (default)", "Known-problem fixes")


def _build_plan(raw3: str) -> list[dict]:
    out: list[dict] = []
    for label in _PLAN_FIELDS:
        m = re.search(rf"(?m)^{re.escape(label)}:[ \t]*(.*)$", raw3)   # this label's line ONLY
        if not m and label == "Persona (optional)":                   # legacy tasks froze it "(required)"
            m = re.search(r"(?m)^Persona \(required\):[ \t]*(.*)$", raw3)
        if not m:
            continue
        val = m.group(1).strip()
        hint = re.search(r"\s+<[^>]*>\s*$", val)      # strip a trailing "   <template hint>"
        if hint:
            val = val[:hint.start()].strip()
        if not val or val.startswith("<"):            # a bare placeholder is not a plan
            continue
        core = val.strip("`").strip()
        if core.startswith("./src/") or core == "src/":   # the untouched Scope defaults (legacy `./src/` · current `src/`)
            continue
        out.append({"label": label, "value": val})
    return out


def decide_data(root: Path, state: dict, mslug: str, slug: str) -> dict:
    """FACTS for the task-level decision-point digest (frozen shape). The decision comes
    from STATE ONLY: recorded (gate set / done) · front (specify→tests) ·
    gate (build/verify). judgment = extracted markers, byte-verbatim. PURE."""
    tasks = state.get("tasks") or {}
    t = tasks.get(slug, {})
    phase = t.get("phase", "direction")
    gate = t.get("gate", "none")
    if gate != "none" or phase == "done":
        seam = "recorded"
    elif phase in _FRONT_PHASES:
        seam = "front"
    else:
        seam = "gate"
    raw = _raw_phase_bodies(root, slug)
    frozen = _contract_frozen(raw.get(3, ""))
    if seam == "gate":   # the items closest to the gate lead: §6 first, then §1
        judgment = _decision_markers(raw.get(6, ""), 6) + _decision_markers(raw.get(1, ""), 1)
    elif seam == "front" and not frozen:
        judgment = _decision_markers(raw.get(1, ""), 1) + _decision_markers(raw.get(3, ""), 3)
    else:
        judgment = []

    members = [x for x in tasks.values() if x.get("milestone") == mslug]
    done, total = sum(1 for x in members if _task_done(x)), len(members)
    facts = {"phase": phase, "gate": gate,
             "deps": [{"slug": d, "gate": tasks.get(d, {}).get("gate", "none")}
                      for d in t.get("depends_on", [])],
             "tests": _tests_info(root, slug)[0]}

    if seam == "gate":
        unlocks = f"gate PASS -> task done -> milestone {min(done + 1, total)}/{total}"
        decide = "add.py gate PASS | RISK-ACCEPTED | HARD-STOP"
    elif seam == "front" and not frozen:
        unlocks = "freeze §3 -> the auto run takes build -> verify (autonomy: auto by default)"
        decide = "approve -> freeze §3 (Status: FROZEN @ v1) -> auto run"
    elif seam == "front":
        unlocks = "none"
        decide = "no decision pending — frozen; the run owns it. next decision point: verify gate"
    else:
        unlocks = "none"
        decide = f"no decision pending — recorded gate: {gate}"
    plan = _build_plan(raw.get(3, "")) if (seam == "front" and not frozen) else []
    return {"seam": seam, "milestone": mslug, "task": slug, "phase": phase,
            "gate": gate, "judgment": judgment, "facts": facts,
            "unlocks": unlocks, "decide": decide, "plan": plan}


def render_decide(root: Path, state: dict, mslug: str, slug: str, *,
                  width: int = _DEFAULT_WIDTH, ascii: bool = False) -> str:
    """Text view of the decision-point digest — decisive facts FIRST: NEEDS YOUR
    JUDGMENT (markers byte-verbatim, section-tagged) -> [front: §3 verbatim] ->
    ENGINE FACTS -> UNLOCKS -> DECIDE. PURE — no writes; plain text (color is a
    tty-only skin in cmd_report, like every report view)."""
    d = decide_data(root, state, mslug, slug)
    g = _ASCII if ascii else _UNICODE
    banner = g["h"] * width
    seam_label = {"gate": "VERIFY GATE", "front": "PLAN",
                  "recorded": "RECORDED"}[d["seam"]]
    L = [banner, f" DECIDE · {mslug or '—'} · {slug} · decision point: {seam_label}", banner]
    if d["decide"].startswith("no decision pending"):
        L.append(f" {d['decide']}")
        L.append(f" GATE  {d['gate']}")
        L.append(banner)
        return "\n".join(L)
    L.append(f" NEEDS YOUR JUDGMENT ({len(d['judgment'])})")
    for item in d["judgment"]:
        L.append(f"   [§{item['section']}]")
        L.extend(item["text"].split("\n"))     # byte-verbatim — never wrapped/clipped
    if d["seam"] == "front":
        L.append("")
        L.append(" CONTRACT (§3 verbatim)")
        L.extend(_raw_phase_bodies(root, slug).get(3, "").split("\n"))
        L.append(" STATUS DRAFT")
    if d["plan"]:                          # plan-in-report: the legible plan-of-action
        L.append("")
        L.append(" BUILD PLAN (§3 · how the AI will build)")
        w = max(len(e["label"]) for e in d["plan"])
        for e in d["plan"]:
            L.append(f"   {e['label']:<{w}} : {e['value']}")
    f = d["facts"]
    deps_txt = " ".join(f"{x['slug']}:{x['gate']}" for x in f["deps"]) or "none"
    L.append("")
    L.append(f" ENGINE FACTS  phase {f['phase']} · gate {f['gate']} · "
             f"deps {deps_txt} · tests {f['tests']}")
    L.append(f" UNLOCKS       {d['unlocks']}")
    L.append(f" DECIDE        {d['decide']}")
    L.append(banner)
    return "\n".join(L)


def _planned_unscaffolded(root: Path, mslug: str) -> list[str]:
    """Slugs MILESTONE.md plans (rows `- [ ] <slug> …`) that have no PLAN.md yet —
    the plan-vs-state diff. Only valid-slug first-tokens match (a template
    placeholder like <slug> never does); file order, deduped; fail-closed []."""
    md = root / "milestones" / mslug / "MILESTONE.md"
    try:
        text = md.read_text(encoding="utf-8")
    except OSError:
        return []
    out: list[str] = []
    for sec in re.split(r"^## ", text, flags=re.M)[1:]:
        if not sec.startswith("Tasks"):    # only the Tasks list — never exit criteria
            continue
        for m in re.finditer(r"^- \[[ x~]\] ([A-Za-z0-9_-]+)\b", sec, re.M):
            slug = m.group(1)
            if slug not in out and not (root / "tasks" / slug / "PLAN.md").is_file():
                out.append(slug)
    return out


def _decide_next(state: dict, d: dict) -> str:
    """The rollup's DECIDE NEXT line (frozen precedence): HARD-STOP -> consolidate+archive
    -> first decision-blocked task (ACTIVE task first, then state order) -> run-in-
    progress. v2: when d carries planned_unscaffolded, the line gains a
    plan-vs-state suffix — precedence itself stays state-only."""
    return _decide_next_base(state, d) + _planned_hint(d)


def _planned_hint(d: dict) -> str:
    """The plan-vs-state suffix ('' when nothing is missing). Text renders emit it
    as its OWN wrapped segment so the phrase never splits mid-token; the JSON
    'decide' string carries it inline via _decide_next."""
    planned = d.get("planned_unscaffolded") or []
    if not planned:
        return ""
    return f" — {len(planned)} planned not yet scaffolded: " + " · ".join(planned)


def _decide_next_pair(state: dict, d: dict) -> tuple[str, bool]:
    """(next-step text, human_stop) over the active-milestone rollup. `human_stop` is the
    driver behind the step (task gate-owner-marker): True for every DECISION point a human
    owns — decompose · resolve HARD-STOP · goal-not-met · consolidate/archive · approve
    contract · gate — and False ONLY for the run-in-progress fallthrough, the one branch
    where the AI just continues an in-flight run. Derived from the rollup `d`, never from
    the rendered prose (the §5 safety rule). The bare string is `_decide_next_base` below."""
    ms = d["milestone"]["slug"]
    rows = d["tasks"]
    if not rows:
        # command-first (next-footer-engine): an empty milestone's next step is to
        # decompose it — name the command WITH its --title flag (status-guide-fold)
        # so a headless agent never reads `new-task --help`.
        return f'decompose into tasks — add.py new-task {ms} --title "..."', True
    stopped = [r for r in rows if r["gate"] == "HARD-STOP"]
    if stopped:
        return f"resolve HARD-STOP on {stopped[0]['slug']}", True
    s = d["summary"]
    if s["tasks_done"] == s["tasks_total"]:
        # tasks complete — but the milestone holds while the goal (exit criteria) is
        # unmet (v20). Point at the feed-forward inventory the loop draws from, instead
        # of "archive". Fires only when criteria exist; else the prompt is unchanged.
        ec = s.get("exit_criteria") or {}
        met, total = ec.get("met", 0), ec.get("total", 0)
        if total > 0 and met < total:
            return (f"goal not met ({met}/{total} exit criteria) — propose next tasks "
                    f"from open deltas / the unscaffolded plan (add.py deltas)"), True
        return f"consolidate learnings + archive-milestone {ms}", True
    active = _active_task(state)
    order = sorted(rows, key=lambda r: 0 if r["slug"] == active else 1)  # stable
    for r in order:
        if r["done"]:
            continue
        if r["phase"] in _FRONT_PHASES:
            return (f"approve the contract of {r['slug']} — "
                    f"add.py report {ms} {r['slug']} --decide"), True
        if r["phase"] == "verify" and r["gate"] == "none":
            return f"gate {r['slug']} — add.py report {ms} {r['slug']} --decide", True
    r = next(x for x in order if not x["done"])
    return f"none — run in progress ({r['slug']} at {r['phase']})", False


def _decide_next_base(state: dict, d: dict) -> str:
    """The next-step TEXT only — the thin str wrapper the report rollup/digest callers use.
    The driver behind it (human_stop) is in _decide_next_pair, read by the footer Arm B."""
    return _decide_next_pair(state, d)[0]


def _next_command(phase: str, *, contract_frozen: bool = False) -> str:
    """The ONE exact next CLI command for an in-flight task at `phase` (the
    status/guide next-step unifier task). PURE — the single composer
    `_next_footer` (Arm A),
    `cmd_guide`'s `then:` line, and plain `status`'s next-command all reuse, so
    the three surfaces can never drift. Front drafting phases teach the collapsed
    `advance --to` bundle (advance-chain-collapse); contract names the freeze gate
    WITH its `--by` flag so a headless agent never reads `freeze --help`.

    ADDITIVE (first-call-ergonomics, M1): `contract_frozen` (default False) keeps
    every existing call valid; at `phase=="contract"` it distinguishes the TWO real
    states a bare phase string can't — a still-DRAFT §3 keeps teaching `freeze --by`,
    a FROZEN §3 names the true next step (`advance`), so a completing freeze never
    tells the very agent that just ran it to run it again."""
    if phase == "verify":
        return "add.py gate PASS | RISK-ACCEPTED | HARD-STOP"
    if phase == "direction":
        # phase-collapse-3: the whole front is one span — a frozen §3 crosses with a
        # plain advance; an unfrozen one names the freeze WITH --cross (the 3-call walk).
        return ("add.py advance" if contract_frozen
                else "add.py freeze --by <name> --cross   (approves §1–§4, crosses to build)")
    if phase == "build":
        # advance-fold (ceremony-turn-cut): a green build steers STRAIGHT to the completing
        # gate — `gate PASS` compound-ticks build->verify in ONE call (cmd_gate), so a separate
        # `advance` here is a pure-bookkeeping turn (~85k cache-read) we drop. Trust floor intact:
        # the gate runs the full verify completion checks; build->verify carries no human seam.
        return "add.py gate PASS | RISK-ACCEPTED | HARD-STOP   (from build — compound-crosses to verify)"
    return "add.py advance"


def _task_contract_frozen(root: Path, slug: str) -> bool:
    """Whether `slug`'s §3 CONTRACT is FROZEN right now, read fresh from its PLAN.md —
    the ONE frozen-ness read the 3 next-command surfaces (footer/status/guide) share
    (first-call-ergonomics, M1). Fail-closed: a missing/unreadable PLAN.md reads as
    NOT frozen via `_raw_phase_bodies`'s own OSError guard, never a crash."""
    return _contract_frozen(_raw_phase_bodies(root, slug).get(3, ""))


def _next_footer(root: Path, state: dict) -> str:
    """The single engine-sourced `next:` line a COMPLETING (exit-0) mutating verb prints
    as its last stdout (task next-footer-engine). ONE resolver, two arms — reusing the
    guide path, never a parallel next-step source:

      Arm A — an active IN-FLIGHT task (gate == "none" AND phase != "done"): the phase's
              own command (advance, or the gate verbs at verify) + its PHASE_GUIDE why.
              The gate=="none" guard is precise — a HARD-STOPped task keeps gate=="HARD-STOP"
              (never done) so it falls to Arm B and is never told to re-gate itself.
      Arm B — otherwise: `_decide_next_base` over the active milestone's rollup — the SAME
              precedence the report dashboard renders (HARD-STOP -> "resolve HARD-STOP …",
              empty milestone -> "decompose … add.py new-task <ms>").

    Fail-soft (design-for-failure): the footer is computed AFTER save_state, so a
    resolution error — no active milestone, an unreadable doc, a corrupt rollup — must
    NEVER turn a saved mutation into a crash; it degrades to one generic re-orient line.
    Pure render: it writes nothing. The trailing MARKER slot (task gate-owner-marker) names
    the driver — ` [you drive]` (the AI proceeds) / ` [human gate]` (a human owns it) — from
    `_driver_stop`: Arm A by phase×autonomy, Arm B by the rollup's own decision (human_stop).
    The fail-soft line carries NO marker — never assert a driver that could not be computed.
    """
    try:
        slug = _active_task(state)
        t = (state.get("tasks") or {}).get(slug) if slug else None
        if t and t.get("gate", "none") == "none" and t.get("phase") != "done":
            phase = t.get("phase")
            why = PHASE_GUIDE[phase][0].split(" — ")[0].strip()   # the short phase clause
            # engine-hint-batch-ops: drafting phases teach the batch form at the
            # moment of use (enforced-rerun census: the lean ops went unused when
            # only the guides named them — the footer is read every turn).
            # first-call-ergonomics M1: thread live frozen-ness so a completing
            # freeze's OWN footer never re-teaches `freeze --by` on itself — and once
            # frozen, the why/driver halves flip WITH the command (the human seam is
            # behind us; advancing into tests is AI-owned, never a stale [human gate]).
            _frozen = phase == "direction" and _task_contract_frozen(root, slug)
            command = _next_command(phase, contract_frozen=_frozen)
            if _frozen:
                return f"next: {command} — §3 frozen; cross into tests{_driver_marker(False)}"
            marker = _driver_marker(_driver_stop(root, state, slug, phase))
            return f"next: {command} — {why}{marker}"
        mslug = _active_milestone(state)
        if mslug:
            d = report_data(root, state, mslug)
            text, human_stop = _decide_next_pair(state, d)
            return "next: " + text + _driver_marker(human_stop)
    except Exception:
        pass   # a footer never aborts the verb that already saved its state
    return "next: add.py status — re-orient"


def render_decide_next(root: Path, state: dict, mslug: str, *,
                       width: int = _DEFAULT_WIDTH, ascii: bool = False) -> str:
    """`report <ms> --decide`: ONLY the DECIDE NEXT block (no rollup table). PURE."""
    g = _ASCII if ascii else _UNICODE
    banner = g["h"] * width
    d = report_data(root, state, mslug)
    L = [banner, f" {mslug} · DECIDE NEXT", banner]
    L.extend(_wrap(_decide_next_base(state, d), width - 4, "   "))
    if _planned_hint(d):   # own segment so the phrase never splits mid-token
        L.extend(_wrap(_planned_hint(d).removeprefix(" — "), width - 4, "   "))
    L.append(banner)
    return "\n".join(L)


def _write_retro(root: Path, state: dict, mslug: str) -> Path:
    """Persist the milestone's CANONICAL render to .add/milestones/<mslug>/RETRO.md
    (the spec'd 'Milestone exit report', appendix-f). Reuses the ONE frozen renderer
    at its canonical args (width 72, ascii=False) so the doc is byte-identical to a
    piped `report <mslug>`. PURE on state: reads via render_report, writes exactly
    this one file with explicit utf-8 (the canonical carries Unicode glyphs — never
    trust the locale default), never mutates state.json."""
    content = render_report(root, state, mslug, width=_DEFAULT_WIDTH, ascii=False)
    path = root / "milestones" / mslug / "RETRO.md"
    _atomic_write(path, content)   # honor the module's atomic-write contract (no half-write)
    return path


_COMPETENCY_ORDER = ("DDD", "SDD", "UDD", "TDD", "ADD")
_DELTA_STATUSES = ("open", "folded", "rejected")

# Canonical delta grammar — the single compiled source for the enumerated
# competency · status shape. Leading \s* is PERMISSIVE so _task_prose can feed
# un-stripped lines directly; callers that pre-strip their input
# (e.g. _collect_open_deltas, _lint_task_deltas) match the same way (\s*
# matches zero). Anchored at line-start via re.match.

# SPEC-delta track — a SEPARATE resolution lifecycle from the competency deltas
# above. SPEC shares the "- [TAG · status]" LINE shape but its statuses are
# DISJOINT (open|seeded|dropped) and it resolves into a TASK (seeded) or is
# dismissed (dropped) — never consolidated into the foundation. _STATUS_SETS keys each
# tag to its legal status set so the ONE lint can reject a cross-set pairing
# ([SPEC · folded], [SDD · seeded]) without a parallel grammar.
_SPEC_STATUSES = ("open", "seeded", "dropped", "carried")
_STATUS_SETS = {**{c: _DELTA_STATUSES for c in _COMPETENCY_ORDER}, "SPEC": _SPEC_STATUSES}

# Broad structural tag detector: finds ANY "- [tok · tok]" line (valid OR malformed).
# A line with a `· ` bracket separator is a delta-attempt. Does NOT enumerate
# competencies or statuses — a different abstraction from _DELTA_RE (no DRY violation).
_TAG_BROAD_RE = re.compile(r"^\s*-\s*\[\s*([^\]·]+?)\s*·\s*([^\]·]+?)\s*\]\s*(.*)$")


def _lint_task_deltas(root: Path, slug: str) -> tuple[bool, str] | None:
    """Lint all open delta entries in a task's '### Competency deltas' AND '### Spec delta' blocks.

    Returns:
        None                    — no delta-attempts found; no check emitted.
        (True, "")              — all open entries pass.
        (False, "<code> -> <tag line>") — first failing entry with its failure code.

    Contract rules (frozen §3, spec-delta-grammar v1):
    - SKIP HTML-comment lines and blank lines (they are never tag lines).
    - Group lines into ENTRIES across both blocks: a broad tag line starts an entry;
      following lines until next tag / blank / block boundary are its continuation.
    - A line without a '· ' separator inside brackets (e.g. '- [x]') is NOT a tag.
    - Validation is TAG-SCOPED via _STATUS_SETS: each tag carries its own legal
      status set (the competency statuses for DDD…ADD, the SPEC statuses for SPEC).
      A status drawn from the wrong set (e.g. a competency-only status on SPEC, or
      `seeded` on a competency tag) is unknown_status.
    - Skip an entry whose status is RESOLVED for its tag (open-only — history not
      retrofitted). Validate the rest: tag known, status legal, non-empty text, and
      '(evidence:' present — evidence is required on an OPEN entry of ANY tag.
    - Fail-closed: an unparseable attempt FAILS (never silently passes).
    """
    task_md = root / "tasks" / slug / "PLAN.md"
    if not task_md.exists():
        return None
    try:
        text = task_md.read_text(encoding="utf-8")
    except OSError:
        return None

    # Locate BOTH delta blocks — "### Competency deltas" and the SPEC track
    # "### Spec delta". Each contributes entries to the same tag-scoped validation.
    blocks = []
    for pat in (r"###\s*Competency deltas\s*\n(.*?)(?=\n##|\Z)",
                r"###\s*Spec delta\s*\n(.*?)(?=\n##|\Z)"):
        bm = re.search(pat, text, re.S)
        if bm:
            blocks.append(bm.group(1))
    if not blocks:
        return None

    # First pass: collect entries (tag line + continuations). HTML-comment and blank
    # lines never start an entry; a block boundary closes any open entry.
    entries: list[tuple[str, list[str]]] = []  # (tag_line, [tag_line, *continuations])
    for block in blocks:
        current: list[str] | None = None
        for raw_line in block.splitlines():
            stripped = raw_line.strip()
            if stripped.startswith("<!--"):
                continue
            if not stripped:
                current = None
                continue
            if _TAG_BROAD_RE.match(raw_line):
                current = [stripped]
                entries.append((stripped, current))
            elif current is not None:
                current.append(stripped)

    if not entries:
        return None  # no delta-attempts → no check emitted

    # Second pass: validate each entry, TAG-SCOPED. The status set is per-tag
    # (_STATUS_SETS): competency → open|folded|rejected, SPEC → open|seeded|dropped.
    for tag_line, unit_lines in entries:
        m = _TAG_BROAD_RE.match(tag_line)
        if not m:
            return False, f"malformed_delta -> {tag_line}"  # fail-closed
        raw_comp = m.group(1).strip()
        raw_status = m.group(2).strip()
        tail = m.group(3).strip()

        # Skip RESOLVED (non-open) entries — history is not retrofitted. Resolved is
        # tag-scoped (folded|rejected · seeded|dropped); an unknown tag defaults to the
        # competency set so a legacy folded/rejected line still skips cleanly.
        resolved = set(_STATUS_SETS.get(raw_comp, _DELTA_STATUSES)) - {"open"}
        if raw_status in resolved:
            continue

        legal = _STATUS_SETS.get(raw_comp)
        if legal is None:
            return False, f"unknown_competency -> {tag_line}"
        if raw_status not in legal:
            return False, f"unknown_status -> {tag_line}"
        if not tail:
            return False, f"malformed_delta -> {tag_line}"
        if "(evidence:" not in " ".join(unit_lines):     # required on open of ANY tag
            return False, f"no_evidence -> {tag_line}"

    return True, ""


def _collect_open_deltas(root: Path) -> dict[str, list[dict]]:
    """Scan every .add/tasks/*/PLAN.md for open lessons learned.

    Returns a dict keyed by competency in canonical order; each value is a list
    of {task, text, evidence} dicts. READ-ONLY — never mutates any file."""
    by_comp: dict[str, list[dict]] = {c: [] for c in _COMPETENCY_ORDER}
    tasks_dir = root / "tasks"
    if not tasks_dir.is_dir():
        return by_comp
    for task_md in sorted(tasks_dir.glob("*/PLAN.md")):
        slug = task_md.parent.name
        try:
            text = task_md.read_text(encoding="utf-8")
        except OSError:
            continue
        # Locate the "### Competency deltas" block (may appear anywhere in the file).
        block_match = re.search(r"###\s*Competency deltas\s*\n(.*?)(?=\n##|\Z)", text, re.S)
        if not block_match:
            continue
        block = block_match.group(1)
        # Group lines into entries (tag line + continuations) so a multi-line delta —
        # whose learning wraps and whose (evidence: …) may land on a later line — is read
        # in FULL, not truncated to its first line. A tag line starts an entry; a line
        # that does not begin a new "- " list item continues it; a blank/comment or a
        # new "- " item ends it (a trailing malformed item can't pollute a delta's text).
        entries: list[list[str]] = []
        current: list[str] | None = None
        for line in block.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("<!--"):
                current = None
                continue
            if _DELTA_RE.match(stripped):
                current = [stripped]
                entries.append(current)
            elif current is not None and not stripped.startswith("-"):
                current.append(stripped)  # genuine wrap of the current learning
            else:
                current = None             # a new / malformed list item ends the run
        for unit in entries:
            m = _DELTA_RE.match(unit[0])
            comp, status = m.group(1), m.group(2)
            if status != "open":
                continue
            # Join the tag line's tail with any continuation lines, then split evidence.
            tail = " ".join([m.group(3).strip(), *unit[1:]]).strip()
            em = _EVIDENCE_RE.match(tail)
            if em:
                delta_text, evidence = em.group(1).strip(), em.group(2).strip()
            else:
                delta_text, evidence = tail, ""
            # OPTIONAL persona target + section hint (persona-self-improve) — None for a plain lesson.
            pm = _PERSONA_TAG_RE.search(unit[0])
            persona = pm.group(1).strip() if pm else None
            hint = pm.group(2).strip() if pm else None
            by_comp[comp].append({"task": slug, "text": delta_text, "evidence": evidence,
                                  "persona": persona, "hint": hint})
    return by_comp


def _collect_spec_deltas(root: Path, status: str = "open") -> list[dict]:
    """Scan every .add/tasks/*/PLAN.md "### Spec delta" block for SPEC deltas of `status`.

    Returns a FLAT list of {task, text, evidence} dicts (SPEC is one tag, never bucketed by
    competency). A SPEC delta is a forward hand-off that resolves into a TASK (seeded), is
    dismissed (dropped), or is DEFERRED non-lossily (carried) — the open/carried VIEWS are this
    one scan keyed on `status`. READ-ONLY; never mutates any file."""
    out: list[dict] = []
    tasks_dir = root / "tasks"
    if not tasks_dir.is_dir():
        return out
    for task_md in sorted(tasks_dir.glob("*/PLAN.md")):
        slug = task_md.parent.name
        try:
            text = task_md.read_text(encoding="utf-8")
        except OSError:
            continue
        for unit in _spec_delta_entries(text):
            m = _SPEC_DELTA_RE.match(unit[0])
            if m.group(2) != status:         # other statuses are excluded from this view
                continue
            tail = " ".join([m.group(3).strip(), *unit[1:]]).strip()
            em = _EVIDENCE_RE.match(tail)
            if em:
                delta_text, evidence = em.group(1).strip(), em.group(2).strip()
            else:
                delta_text, evidence = tail, ""
            out.append({"task": slug, "text": delta_text, "evidence": evidence})
    return out


def _collect_open_spec_deltas(root: Path) -> list[dict]:
    """Open SPEC deltas — the release-floor + `deltas` + `status` count source (a thin view)."""
    return _collect_spec_deltas(root, "open")


def _persona_roster(root: Path) -> list[tuple[str, str, str]]:
    """(slug, flow, vibe) per REAL persona under `.add/personas/` — the frontmatter-only
    roster read behind the status/check roster lines (roster-status-line): agents pick a
    persona from this line instead of whole-roster body reads. Fail-soft like its
    `_real_persona_slugs` sibling: a parse miss degrades that field to "?", never raises."""
    rows = []
    for slug in _real_persona_slugs(root):
        flow = vibe = "?"
        try:
            text = (root / "personas" / f"{slug}.md").read_text(encoding="utf-8")
            fm = re.match(r"\s*---\s*\n(.*?)\n---\s*\n", text, re.S)
            body = fm.group(1) if fm else ""
            m = re.search(r"(?m)^\s*flow\s*:\s*(.+)$", body)
            if m:
                flow = m.group(1).strip()
            m = re.search(r"(?m)^\s*vibe\s*:\s*(.+)$", body)
            if m:
                vibe = m.group(1).strip()
        except OSError:
            pass
        if vibe != "?" and len(vibe) > 70:
            vibe = vibe[:70] + "…"
        rows.append((slug, flow, "" if vibe == "?" else vibe))
    return rows






# The FIRST writer of the seeded/dropped/carried statuses (task 1 only TOLERATED them on read).
# seed-and-drop's resolution verbs AND delta-drain's carry/reopen all route through here. The token
# regex matches ANY current SPEC status, so the flip works in either direction (open->carried,
# carried->open) — not only away from open.
_SPEC_STATUS_TOKEN_RE = re.compile(r"(\[\s*SPEC\s*·\s*)(?:open|seeded|dropped|carried)(\s*\])")


def _resolve_spec_delta(text: str, new_status: str, pointer: str | None = None,
                        line_index: int | None = None, *, from_status: str = "open",
                        stamp: str | None = None) -> str | None:
    """Flip ONE `[SPEC · <from_status>]` line in `text` to `new_status`; return the new text.

    PURE — no IO. With `line_index` (a splitlines(keepends=True) index, as `_select_spec_delta`
    returns) flip THAT line; without it, flip the FIRST `from_status` delta (back-compat;
    `from_status` defaults to "open"). Only the status token changes (+ a trailing ` [→ <pointer>]`
    seed stamp, or a free-form ` <stamp>` e.g. `[carried: <reason>]`); the entry's text and
    `(evidence: …)` are byte-preserved. Returns None when there is NO matching delta to flip —
    the caller then refuses and writes nothing. Mirrors the `_autonomy_decl_line` pure-transform."""
    lines = text.splitlines(keepends=True)
    target = line_index
    if target is None:                             # back-compat: the FIRST from_status delta
        for i, ln in enumerate(lines):
            m = _SPEC_DELTA_RE.match(ln.rstrip("\n"))
            if m and m.group(2) == from_status:
                target = i
                break
        if target is None:
            return None
    ln = lines[target]
    eol = ln[len(ln.rstrip("\n")):]                # preserve the exact line ending
    body = _SPEC_STATUS_TOKEN_RE.sub(rf"\g<1>{new_status}\g<2>", ln.rstrip("\n"), count=1)
    if pointer:
        body = f"{body} [→ {pointer}]"
    if stamp:
        body = f"{body} {stamp}"
    lines[target] = body + eol
    return "".join(lines)


def _select_spec_delta(text: str, match: str | None = None,
                       status: str = "open") -> tuple[str, int | None, str | None]:
    """Pick the SPEC delta (of `status`, default "open") to resolve (delta-match-selector). PURE.

    `match=None` -> the FIRST such delta. `match=<substr>` -> the UNIQUE one whose display text
    (status token + `(evidence: …)` excluded) contains <substr>, case-insensitive. Returns
    (result, line_index, display_text) where result is one of: "ok" (line_index/display set),
    "no_open" (none of `status` at all), "no_match" (--match hit zero), "ambiguous" (--match hit >1).
    line_index is a splitlines(keepends=True) index, the same `_resolve_spec_delta` flips. (The
    "no_open" token is status-agnostic; the carried-track caller maps it to `no_carried_spec_delta`.)"""
    opens: list[tuple[int, str]] = []
    for i, ln in enumerate(text.splitlines(keepends=True)):
        m = _SPEC_DELTA_RE.match(ln.rstrip("\n"))
        if not m or m.group(2) != status:
            continue
        tail = m.group(3).strip()
        cut = tail.find("(evidence:")             # exclude the evidence tail even if its paren is unclosed
        opens.append((i, (tail[:cut].strip() if cut != -1 else tail)))
    if not opens:
        return ("no_open", None, None)
    if match is None:
        return ("ok", opens[0][0], opens[0][1])
    needle = match.lower()
    hits = [(i, d) for i, d in opens if needle in d.lower()]
    if not hits:
        return ("no_match", None, None)
    if len(hits) > 1:
        return ("ambiguous", None, None)
    return ("ok", hits[0][0], hits[0][1])


# kernel-trim (ADD 2.0 M5): the `fold` mechanized-consolidation verb + its routing tables died —
# lessons land in-flight via delta-append into the living specs; the human folds a spec's Deltas
# inbox upward by editing the spec itself (deltas.md's [folded] retag), no engine transcription.




















_AUDIT_STAMP_RE = re.compile(r"Status:\s*FROZEN @ v\d+\s*[—-]+\s*approved by\s+\S+")
_AUDIT_OUTCOME_RE = re.compile(r"^Outcome:\s*(PASS|RISK-ACCEPTED|HARD-STOP)\b", re.M)
_AUDIT_SECURITY_RE = re.compile(
    r"^\s*- \[[ x~]\] no exposed secrets.*(?:\n(?!\s*- \[|#).*)*", re.M)
_AUDIT_REVIEWED_RE = re.compile(r"^Reviewed by:(.*)$", re.M)






# Any `risk:` declaration in the header (high|normal|low|…) — read from the `·`-delimited header
# region only (mirrors _RISK_HIGH_RE's anchoring so a title substring can never look like one).
_RISK_ANY_RE = re.compile(r"(?:^|·)[ \t]*risk:[ \t]*\S", re.MULTILINE)

# A single `Reported:` line (report-rendered-trace) — scoped to ONE phase body at a time by the
# caller (bodies.get(3, "")/bodies.get(6, "")), so §3 and §6 never cross-contaminate each other.
_REPORTED_LINE_RE = re.compile(r"(?m)^Reported:[ \t]*(.*)$")
































_OUTCOME_ORDER = ("PASS", "RISK-ACCEPTED", "HARD-STOP")


def _route_scoreboard(root: Path) -> dict:
    """persona-gepa-loop (ADD 2.0 M7): roll `.add/traces/route-outcomes.jsonl` up per
    LANE — gated count · outcome mix · heal total · median age. The READ side of the
    M1 telemetry stream: evidence for the PM persona's GEPA reflection. Read-only and
    degrade-safe (a malformed line is skipped, an unreadable file is an empty board);
    {} when there are no traces."""
    p = root / "traces" / "route-outcomes.jsonl"
    try:
        text = p.read_text(encoding="utf-8") if p.exists() else ""
    except OSError:
        return {}
    lanes: dict[str, dict] = {}
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            rec = json.loads(ln)
        except ValueError:
            continue                                  # telemetry, never a crash
        if not isinstance(rec, dict):
            continue
        row = lanes.setdefault(rec.get("lane") or "unrouted",
                               {"gated": 0, "outcomes": {}, "heals": 0, "_ages": []})
        row["gated"] += 1
        oc = str(rec.get("outcome") or "?")
        row["outcomes"][oc] = row["outcomes"].get(oc, 0) + 1
        try:
            row["heals"] += int(rec.get("heals") or 0)
        except (TypeError, ValueError):
            pass
        age = rec.get("age_hours")
        if isinstance(age, (int, float)):
            row["_ages"].append(float(age))
    for row in lanes.values():
        ages = sorted(row.pop("_ages"))
        n = len(ages)
        row["median_age_hours"] = (None if not n else round(
            ages[n // 2] if n % 2 else (ages[n // 2 - 1] + ages[n // 2]) / 2, 1))
    return lanes


def _print_route_scoreboard(board: dict) -> None:
    total = sum(r["gated"] for r in board.values())
    print(f"route scoreboard ({total} gated · .add/traces/route-outcomes.jsonl):")
    width = max(len(k) for k in board)
    for lane in sorted(board, key=lambda k: -board[k]["gated"]):
        r = board[lane]
        mix = " · ".join(f"{oc} {r['outcomes'][oc]}"
                         for oc in (*_OUTCOME_ORDER, *sorted(set(r["outcomes"]) - set(_OUTCOME_ORDER)))
                         if oc in r["outcomes"])
        med = f" · median {r['median_age_hours']}h" if r["median_age_hours"] is not None else ""
        print(f"  {lane:<{width}} : {r['gated']} gated · {mix} · heals {r['heals']}{med}")
    print("  reflect (GEPA): keep routes that cut heals/age without gate regressions, prune")
    print('  rules that never fired — propose: add.py delta-append add "<route-rule>";')
    print("  a human folds ratified rules into .add/personas/ (the engine never edits a persona)")


def cmd_deltas(args: argparse.Namespace) -> None:
    """Read-only: report open competency lessons AND open SPEC deltas, SEPARATELY.

    Scans every .add/tasks/*/PLAN.md: '### Competency deltas' → open lessons grouped by competency
    (DDD·SDD·UDD·TDD·ADD), and '### Spec delta' → open forward hand-offs in their own section (a SPEC
    delta resolves into a task, never consolidates). kernel-trim: the carried-lifecycle retrieval
    (--carried/--all) died with the drop/carry/reopen verbs — a `carried` status token in an
    archived task is still read-tolerated, just no longer a queryable backlog.
    --json emits one object. Exit 0 ALWAYS. Writes NOTHING."""
    root = _require_root()
    by_comp = _collect_open_deltas(root)
    total = sum(len(v) for v in by_comp.values())
    spec = _collect_open_spec_deltas(root)
    board = _route_scoreboard(root)          # persona-gepa-loop: the traces' read side

    if getattr(args, "json", False):
        print(json.dumps({
            "total": total,
            "by_competency": {c: v for c, v in by_comp.items() if v},
            "spec": spec,
            "spec_total": len(spec),
            "routes": board,
        }, ensure_ascii=False))
        return

    printed = False
    if total:
        print(f"open lessons learned ({total} total):")
        for comp in _COMPETENCY_ORDER:
            entries = by_comp[comp]
            if not entries:
                continue
            print(f"  {comp} ({len(entries)}):")
            for e in entries:
                print(f"    - {e['text']}  [{e['task']}]")
        printed = True
    if spec:
        print(f"open spec deltas ({len(spec)} total):")
        for e in spec:
            print(f"    - {e['text']}  [{e['task']}]")
        printed = True
    if not printed:
        print("no open deltas.")
    if board:                                # silent at zero — telemetry, never noise
        _print_route_scoreboard(board)


def cmd_delta_append(args: argparse.Namespace) -> None:
    """specs-5dd (ADD 2.0 M3): append ONE lesson to its living 5-DD spec, in-flight.

    `delta-append <dd> "<text>"` — dd ∈ ddd|sdd|udd|tdd|add routes to its spec file
    (constants.SPEC_DDS); the line is prepended directly UNDER the `## Deltas`
    heading (newest first), tagged `[open · <date>]`, stamped with the active task
    (or `--task`; no task -> no stamp, never inferred). An unknown dd refuses
    BEFORE any write (delta_dd_unknown). Legacy tolerance: a pre-2.0 project with
    no .add/specs/ gets the TARGET file seeded on demand via the same
    _seed_spec_file init uses — the verb never dies on a missing dir; a customised
    spec that lost its Deltas heading gets one appended rather than an error."""
    root = _require_root()
    dd = (args.dd or "").strip().lower()
    if dd not in SPEC_DDS:
        _die(f"delta_dd_unknown: '{args.dd}' — dd must be one of {'|'.join(SPEC_DDS)} "
             "(ddd=domain · sdd=system · udd=experience · tdd=quality · add=method)")
    text = " ".join((args.text or "").split())
    if not text:
        _die("delta_text_empty: give the lesson as one quoted line")
    state = load_state(root)
    slug = getattr(args, "task", None) or _active_task(state)
    today = date.today().isoformat()
    spec_path = _seed_spec_file(root, dd, project=state.get("project") or root.parent.name,
                                stage=state.get("stage") or "mvp", date_str=today)
    line = f"- [open · {today}] {text}" + (f" (task:{slug})" if slug else "")
    if spec_path.exists():
        body = spec_path.read_text(encoding="utf-8")
        idx = body.find("## Deltas")
        if idx == -1:
            body = body.rstrip("\n") + "\n\n## Deltas (newest first)\n" + line + "\n"
        else:
            nl = body.find("\n", idx)
            insert_at = (nl + 1) if nl != -1 else len(body.rstrip("\n")) + 1
            if nl == -1:
                body = body + "\n" + line + "\n"
            else:
                body = body[:insert_at] + line + "\n" + body[insert_at:]
    else:
        # seed skipped (blank/missing template) — still capture the delta; a lost
        # lesson costs more than a header-less file (design-for-failure)
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        body = f"# {SPEC_DDS[dd][1]} — the {dd.upper()} spec\n\n## Deltas (newest first)\n{line}\n"
    _atomic_write(spec_path, body)
    stamp = f" (task:{slug})" if slug else ""
    print(f"delta-append [{dd}] -> .add/specs/{SPEC_DDS[dd][0]}{stamp}")


def cmd_migrate(args: argparse.Namespace) -> None:
    """One-shot 1.x -> 2.0 board conversion (ADD 2.0 M6).

    Two mechanical moves, both idempotent (a second run is a loud no-op):
      1. rename every task doc TASK.md -> PLAN.md — live tasks
         (.add/tasks/<slug>/) AND archived ones (.add/archive/<ms>/tasks/<slug>/),
         so the engine's PLAN.md readers see the whole history uniformly;
      2. seed any missing living 5-DD spec under .add/specs/ (same
         _seed_spec_file init uses — never clobbers an existing spec).
    A slug carrying BOTH files is ambiguous state — refuse (migrate_conflict)
    before renaming anything, tree untouched (validate-all-then-write)."""
    root = _require_root()
    state = load_state(root)
    task_dirs = sorted((root / "tasks").glob("*/")) if (root / "tasks").is_dir() else []
    task_dirs += sorted((root / "archive").glob("*/tasks/*/")) if (root / "archive").is_dir() else []
    renames: list[Path] = []
    for d in task_dirs:
        old, new = d / "TASK.md", d / "PLAN.md"
        if old.exists() and new.exists():
            _die(f"migrate_conflict: {d.relative_to(root.parent)} carries BOTH TASK.md and "
                 "PLAN.md — resolve by hand (keep one), then re-run; nothing was renamed")
        if old.exists():
            renames.append(old)
    for old in renames:
        old.rename(old.with_name("PLAN.md"))
    today = date.today().isoformat()
    seeded = []
    for dd in SPEC_DDS:
        p = root / "specs" / SPEC_DDS[dd][0]
        if not p.exists():
            _seed_spec_file(root, dd, project=state.get("project") or root.parent.name,
                            stage=state.get("stage") or "mvp", date_str=today)
            if p.exists():
                seeded.append(SPEC_DDS[dd][0])
    # foundation-specs-refs: wire PROJECT.md's thin index to the five specs (idempotent —
    # a pre-pointer PROJECT.md gets the managed ADD:SPECS block; an up-to-date one is a no-op).
    pointer_action = _inject_specs_pointers(root / "PROJECT.md")
    if not renames and not seeded and pointer_action in ("unchanged", "absent"):
        print("already 2.0 — nothing to migrate (task docs are PLAN.md; the 5 living specs exist; "
              "PROJECT.md points at them)")
        return
    if renames:
        print(f"migrated {len(renames)} task doc(s) TASK.md -> PLAN.md")
    if seeded:
        print(f"seeded {len(seeded)} living spec(s): {', '.join(seeded)}")
    if pointer_action in ("created", "updated"):
        print(f"{pointer_action} PROJECT.md → .add/specs/ pointer block (the 5-DD standing picture)")
    print("next: add.py status — re-orient on the 2.0 board")


def cmd_project(args: argparse.Namespace) -> None:
    """Read-only: print .add/PROJECT.md (the read-first foundation) in one command.

    Fail-closed: a missing foundation dies with a clear stderr message + a non-zero
    exit, never a silent empty print. Writes NOTHING."""
    root = _require_root()
    foundation = root / "PROJECT.md"
    if not foundation.exists():
        _die("missing foundation: .add/PROJECT.md (run `add.py init` to scaffold it)")
    print(foundation.read_text(encoding="utf-8"), end="")


def cmd_report(args: argparse.Namespace) -> None:
    """Read-only: capture a milestone's raw data (--json) or render the text
    dashboard (color on a tty, ASCII when the terminal can't do Unicode, --plain
    forces the pipe/screen-reader-safe tier). Writes nothing, never mutates state."""
    root = _require_root()
    state = load_state(root)
    milestones = state.get("milestones") or {}
    tasks = state.get("tasks") or {}
    name = args.milestone       # 1st positional (SMART: milestone-first, else task)
    task = getattr(args, "task", None)

    # Resolve to a ROLLUP (mslug) or a DRILL (mslug + drill_task). Drill path is purely
    # additive; the rollup branches are byte-for-byte the v9 behavior.
    drill_task = None
    if task is not None:                          # explicit `report <m> <task>`
        mslug = name
        if mslug not in milestones:
            _die(f"unknown_milestone: '{mslug}' is not a milestone")
        if tasks.get(task, {}).get("milestone") != mslug:
            _die(f"unknown_task: '{task}' is not a task of milestone '{mslug}'")
        drill_task = task
    elif name is not None:                        # smart single positional
        if name in milestones:
            mslug = name                          # -> rollup (unchanged)
        elif name in tasks:                       # -> drill by task name
            drill_task = name
            mslug = tasks[name].get("milestone")
            if not mslug:
                _die(f"unknown_milestone: task '{name}' is not attached to a milestone")
        else:
            _die(f"unknown_milestone: '{name}' is not a milestone")
    elif getattr(args, "decide", False):          # bare --decide -> the ACTIVE TASK
        slug = _active_task(state)
        if not slug or slug not in tasks:
            _die("no_active_task — name one: add.py report <milestone> <task> --decide")
        drill_task = slug
        mslug = tasks[slug].get("milestone") or ""
    else:                                         # no positional -> active milestone
        mslug = _active_milestone(state)
        if not mslug:
            _die("no_active_milestone: no milestone given and none is active; "
                 "try `add.py report <milestone>`")
        if mslug not in milestones:
            _die(f"unknown_milestone: '{mslug}' is not a milestone")

    if getattr(args, "decide", False):
        # Decision-seam digest (v13): task -> seam digest; milestone -> DECIDE NEXT
        # block only. PURE, like every report path.
        if getattr(args, "json", False):
            if drill_task:
                payload = decide_data(root, state, mslug, drill_task)
            else:   # milestone altitude: same frozen key set, task null
                d = report_data(root, state, mslug)
                payload = {"seam": "milestone", "milestone": mslug, "task": None,
                           "phase": "", "gate": "none", "judgment": [],
                           "facts": {"phase": "", "gate": "none", "deps": [], "tests": 0},
                           "unlocks": "", "decide": _decide_next(state, d), "plan": []}
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return
        plain = getattr(args, "plain", False)
        interactive = sys.stdout.isatty() and not plain
        width = _term_width() if interactive else _DEFAULT_WIDTH
        use_ascii = plain or _use_ascii()
        out = (render_decide(root, state, mslug, drill_task, width=width, ascii=use_ascii)
               if drill_task else
               render_decide_next(root, state, mslug, width=width, ascii=use_ascii))
        if not plain and _color_enabled():
            out = _colorize(out)
        print(out)
        return

    if getattr(args, "json", False):
        # POLYMORPHIC by path: drill -> task_phases list; rollup -> report_data dict.
        payload = task_phases(root, drill_task) if drill_task \
            else report_data(root, state, mslug)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    plain = getattr(args, "plain", False)
    interactive = sys.stdout.isatty() and not plain
    width = _term_width() if interactive else _DEFAULT_WIDTH
    use_ascii = plain or _use_ascii()
    out = (render_task_detail(root, state, mslug, drill_task, width=width, ascii=use_ascii)
           if drill_task else
           render_report(root, state, mslug, width=width, ascii=use_ascii))
    if not plain and _color_enabled():
        out = _colorize(out)
    print(out)


_FLOW_MAP = (
    "ADD — spec-and-tests-first; you drive, the human owns direction.\n"
    "start here: add.py status   — where you are + your exact next command\n"
    "flow:  init → new-task → advance → freeze → gate\n"
    '  add.py init --name "<project>" --stage mvp     start a project in this directory\n'
    '  add.py new-task <slug> --title "..."           a task (ONE atomic template, every lane)\n'
    "  add.py advance                                 cross to the next phase (status names the exact form)\n"
    '  add.py freeze --by "<name>" --cross            approve the frozen §3 contract (the one human gate)\n'
    "  add.py gate PASS                               record the verify outcome\n"
    "a command's flags: add.py <command> -h\n"
)


def _compact_commands(parser: argparse.ArgumentParser) -> str:
    """help-diet: a COMPACT one-block list of every subcommand NAME (no per-command
    help paragraph), wrapped, with the per-command flags pointer. Keeps discoverability
    while cutting the top `--help` from ~121 lines to a handful."""
    import textwrap
    names: list[str] = []
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name in action.choices:            # dict preserves add_parser() order
                if name not in names:              # dedupe any aliases, keep order
                    names.append(name)
            break
    block = textwrap.fill("  ".join(names), width=78,
                          initial_indent="  ", subsequent_indent="  ",
                          break_on_hyphens=False, break_long_words=False)
    return ("commands (flags: add.py <command> -h):\n" + block + "\n")


class _AddArgParser(argparse.ArgumentParser):
    """help-habit-kill: on an unknown TOP-LEVEL command, argparse dumps the full
    ~50-choice usage — unreadable at a glance, so the agent's reflex is `--help` or a
    re-read (the measured 1/rep call lever). Intercept ONLY that case (`prog == 'add.py'`
    + an "invalid choice" message) with a concise "unknown command 'X' — did you mean
    '<near>'?" plus a pointer to `add.py status`. Every other parse error — a subcommand's
    own invalid choice, a missing positional, unrecognized arguments — delegates to
    argparse's default, so those surfaces stay byte-identical.

    orient-map: the top parser's `--help` (and a bare `add.py` with no subcommand) LEAD
    with the flow map above instead of the alphabet-soup dump — the agent's first
    orientation is one cheap read. Both are guarded to the TOP parser (`prog == 'add.py'`):
    a subcommand's own `--help`/errors (prog "add.py <cmd>") stay byte-identical argparse."""

    def format_help(self) -> str:
        # help-diet: top parser leads with the flow map, then a COMPACT command-NAME list
        # (not argparse's ~111-line per-command dump) — every name stays discoverable, but the
        # re-read cache-weight drops (the dump was 17% of an ADD run's engine_output, one early
        # call). A subcommand's own help (prog "add.py <cmd>") stays byte-identical argparse.
        if self.prog == "add.py":
            return _FLOW_MAP + "\n" + _compact_commands(self)
        return super().format_help()

    def error(self, message: str):
        if self.prog == "add.py" and "the following arguments are required" in message:
            # bare `add.py` (no subcommand): orient, don't dump the raw usage.
            sys.stderr.write(_FLOW_MAP + "\nrun: add.py status\n")
            raise SystemExit(2)
        m = re.search(r"invalid choice: '([^']*)'", message)
        if m is not None and self.prog == "add.py":
            import difflib
            bad = m.group(1)
            choices: list[str] = []
            for action in self._actions:
                if isinstance(action, argparse._SubParsersAction):
                    choices = list(action.choices)
                    break
            near = difflib.get_close_matches(bad, choices, n=1)
            hint = f" — did you mean '{near[0]}'?" if near else ""
            sys.stderr.write(f"add.py: unknown command '{bad}'{hint}\n")
            sys.stderr.write("see where you are + all commands: add.py status\n")
            raise SystemExit(2)
        super().error(message)


def build_parser() -> argparse.ArgumentParser:
    p = _AddArgParser(prog="add.py", description="ADD scaffolder + state tracker")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("init", help="create a .add/ project here")
    pi.add_argument("--dir", default=".", help="target directory (default: cwd)")
    pi.add_argument("--name", default=None, help="project name (default: dir name)")
    pi.add_argument("--stage", default="prototype", choices=STAGES)
    pi.add_argument("--force", action="store_true", help="reset state.json if present")
    pi.add_argument("--await-lock", dest="await_lock", action="store_true",
                    help="seed an unlocked setup; gates new-task/advance/gate until `add.py lock`")
    pi.add_argument("--run-mode", dest="run_mode", default=None,
                    choices=["auto", "conservative"],
                    help="seed autonomy+streams posture: auto→parallel, conservative→sequential "
                         "(absent: PROJECT.md is byte-identical to a plain init)")
    pi.set_defaults(func=cmd_init)

    pl = sub.add_parser("lock",
                        help="freeze the autonomous setup (the human baseline approval) and open the build")
    pl.add_argument("--by", default=None, help="who is locking (default: current OS user)")
    pl.add_argument("--layers", default=None,
                    help="comma-separated lock layers (default: foundation,scope,contract)")
    pl.add_argument("--force", action="store_true", help="re-lock an already-locked project")
    pl.add_argument("--json", action="store_true", help="emit one JSON object instead of text")
    pl.set_defaults(func=cmd_lock)

    pfz = sub.add_parser("freeze",
                         help="freeze a task's §3 contract (the human approval) — stamps "
                              "FROZEN @ vN + a structured actor on the task record")
    pfz.add_argument("slug", nargs="?", default=None,
                     help="task to freeze (default: the active task)")
    pfz.add_argument("--by", default=None, help="approver name (default: the resolved actor); "
                     "REQUIRED (an agent id) with --ai-plan-verify")
    pfz.add_argument("--cross", action="store_true",
                     help="compound tick: after a plan-phase freeze stamps, land in tests "
                          "in the same call (opt-in; a non-plan or refused freeze never crosses)")
    pfz.add_argument("--ai-plan-verify", action="store_true", dest="ai_plan_verify",
                     help="AI-plan-verify-gate: let an AI agent (--by AGENT_ID) perform this "
                          "freeze in place of a human — refused unless gate_mode: ai-plan-verify, "
                          "autonomy: auto, sensitivity outside {security,data,architecture}, and "
                          "a complete §3 'AI-verify record' checklist")
    pfz.set_defaults(func=cmd_freeze)

    pn = sub.add_parser("new-task", help="scaffold a new task (PLAN.md + tests/ + src/)")
    pn.add_argument("slug")
    pn.add_argument("--title", default=None)
    pn.add_argument("--milestone", default=None, help="attach to a milestone (default: active)")
    pn.add_argument("--depends-on", dest="depends_on", default=None,
                    help="comma-separated task slugs this task depends on (BLOCKING)")
    pn.add_argument("--extends", dest="extends", default=None,
                    help="comma-separated task slugs this task extends (non-blocking: builds on their shipped surface)")
    pn.add_argument("--relates-to", dest="relates_to", default=None,
                    help="comma-separated task slugs this task relates to (non-blocking: shares context)")
    pn.add_argument("--from-delta", dest="from_delta", default=None, metavar="PRIOR",
                    help="SEED PRIOR's open SPEC delta into this task (pre-fills §1 "
                         "Feature, flips the source -> [SPEC · seeded] [→ this])")
    pn.add_argument("--match", default=None, metavar="SUBSTR",
                    help="with --from-delta: target the UNIQUE open SPEC delta whose text "
                         "contains SUBSTR (case-insensitive) instead of the first")
    pn.add_argument("--force", action="store_true", help="overwrite PLAN.md if present")
    pn.add_argument("--sensitivity", default=None, metavar="CLASS",
                    help="declare the task's risk class at creation (base: security|data|"
                         "architecture|mechanical \u222a GLOSSARY classes); a base non-mechanical "
                         "class blocks any AI-crossed freeze (_ai_freeze_allowed's human floor)")
    pn.set_defaults(func=cmd_new_task)

    pr = sub.add_parser("relate", help="declare task-graph edges AFTER creation "
                        "(the edge-hint's ratify path; additive, never drops)")
    pr.add_argument("slug")
    pr.add_argument("--depends-on", dest="depends_on",
                    help="comma-separated task slugs this task depends on (BLOCKING)")
    pr.add_argument("--extends", help="comma-separated slugs this task extends (non-blocking)")
    pr.add_argument("--relates-to", dest="relates_to",
                    help="comma-separated slugs this task relates to (non-blocking)")
    pr.set_defaults(func=cmd_relate)

    plc = sub.add_parser("locate", help="failure-location: a test path -> owning node "
                         "+ class (in-node vs interface-regression); a slug -> its "
                         "dependent closure (who re-verifies on a contract change)")
    plc.add_argument("ref", help="test path (project-root-relative), pytest node-id "
                     "path::test_name (adds the §4 covers -> frozen §3 clause map), "
                     "or task slug")
    plc.set_defaults(func=cmd_locate)

    pgr = sub.add_parser("graph", help="render the task DAG as a mermaid flowchart "
                         "(milestone subgraphs; edge style = edge type; dashed = "
                         "planned-but-never-created)")
    pgr.add_argument("--milestone", help="limit to one milestone's subgraph")
    pgr.add_argument("--signals", action="store_true",
                     help="overlay LIVE signals (todos + open §7 deltas) as nodes edged "
                          "to their tasks (observed-by/resolves-into/blocks)")
    pgr.add_argument("--html", action="store_true",
                     help="write a self-rendering HTML page (chrome + pinned-CDN mermaid) "
                          "to a temp file and print its path, instead of raw mermaid")
    pgr.add_argument("--out", default=None,
                     help="with --html, the output path (default: a stable file under the "
                          "system temp dir; a missing parent dir is created)")
    pgr.set_defaults(func=cmd_graph)

    pdap = sub.add_parser("delta-append",
                          help="append one lesson to its living 5-DD spec under .add/specs/ "
                               "(specs-5dd kernel verb — in-flight, newest first)")
    pdap.add_argument("dd", help="target lens: ddd=domain · sdd=system · udd=experience · "
                                 "tdd=quality · add=method")
    pdap.add_argument("text", help="the lesson, one quoted line")
    pdap.add_argument("--task", default=None, metavar="SLUG",
                      help="stamp this task slug (default: the active task; none -> no stamp)")
    pdap.set_defaults(func=cmd_delta_append)

    pmig = sub.add_parser("migrate",
                          help="one-shot 1.x -> 2.0 board conversion: rename task docs "
                               "TASK.md -> PLAN.md (live + archived) and seed any missing "
                               "living 5-DD spec (idempotent)")
    pmig.set_defaults(func=cmd_migrate)

    pm = sub.add_parser("new-milestone", help="scaffold a milestone (SDD living doc)")
    pm.add_argument("slug")
    pm.add_argument("--title", default=None)
    pm.add_argument("--goal", default=None, help="one-sentence outcome")
    pm.add_argument("--stage", default="mvp", choices=STAGES)
    pm.add_argument("--force", action="store_true", help="overwrite MILESTONE.md if present")
    pm.add_argument("--tiny", action="store_true",
                    help="tiny plan for small scope: compact MILESTONE.md (goal + Plan + "
                         "Done-when, no contracts scaffold). Human-declared; the "
                         "freeze/red/gate floor is unchanged.")
    pm.add_argument("--queued", action="store_true",
                    help="create the milestone QUEUED (status=queued), not active: it is recorded "
                         "and its MILESTONE.md written, but the active focus is unchanged. Promote it "
                         "later with `activate <slug>`. Foundation for roadmap intake (1 active + N queued).")
    pm.add_argument("--await-confirm", action="store_true",
                    help="opt into the confirm-parent gate: seed the milestone unconfirmed so "
                         "new-task is held until `milestone-confirm` (mirrors `init --await-lock`); "
                         "the guided skill flow passes this at the human-review point")
    pm.set_defaults(func=cmd_new_milestone)

    pmc = sub.add_parser("milestone-confirm",
                         help="confirm a milestone (the human gate that opens new-task for it)")
    pmc.add_argument("slug")
    pmc.add_argument("--by", default=None, help="free-text confirmer name (defaults to the OS user)")
    pmc.set_defaults(func=cmd_milestone_confirm)

    pmd = sub.add_parser("milestone-done", help="exit-gate a milestone (all tasks must PASS)")
    pmd.add_argument("slug")
    pmd.set_defaults(func=cmd_milestone_done)

    psm = sub.add_parser("set-milestone", help="attach/move/detach an existing task")
    psm.add_argument("task")
    psm.add_argument("milestone", help="milestone slug, or 'none' to detach")
    psm.set_defaults(func=cmd_set_milestone)

    pu = sub.add_parser("use", help="set the active task to an existing one (switch focus)")
    pu.add_argument("slug")
    pu.set_defaults(func=cmd_use)

    pac = sub.add_parser("activate",
                         help="add a milestone to the active working SET and focus it (parallel milestones)")
    pac.add_argument("slug")
    pac.set_defaults(func=cmd_activate)

    pdac = sub.add_parser("deactivate",
                          help="remove a milestone from the active working SET (its files stay on disk)")
    pdac.add_argument("slug")
    pdac.set_defaults(func=cmd_deactivate)

    pam = sub.add_parser("archive-milestone",
                         help="collapse a done milestone out of active state (files stay on disk)")
    pam.add_argument("slug")
    pam.set_defaults(func=cmd_archive_milestone)

    pp = sub.add_parser("phase", help="set a task's phase explicitly")
    # phase-collapse-3: legacy tokens stay accepted at the parser (mapped + noted in
    # cmd_phase) so pre-collapse scripts keep working; the stored value is always canonical.
    pp.add_argument("phase", choices=PHASES + tuple(LEGACY_PHASES))
    pp.add_argument("slug", nargs="?", default=None)
    pp.add_argument("--note", default=None,
                    help="annotate the verify->build round this return records (build target only)")
    pp.add_argument("--skip-freeze", action="store_true",
                    help="cross direction->build on a DRAFT §3, recording an auditable freeze_skipped "
                         "marker (the universal freeze gate's only bypass; never auto-freezes §3)")
    pp.set_defaults(func=cmd_phase, _opt_positionals=("slug",))

    pa = sub.add_parser("advance", help="move a task to the next phase")
    pa.add_argument("slug", nargs="?", default=None)
    pa.add_argument("--skip-freeze", action="store_true",
                    help="cross direction->build on a DRAFT §3, recording an auditable freeze_skipped "
                         "marker (the universal freeze gate's only bypass; never auto-freezes §3)")
    pa.add_argument("--to", default=None,
                    help="legacy fast-forward (the direction span is one phase now); "
                         "legacy tokens map to their 3-phase home")
    pa.add_argument("--fill", default=None, metavar="PATH",
                    help="draft the CURRENT phase's PLAN.md section from PATH (or '-' for stdin) "
                         "and advance in one call; all-or-nothing — a refused crossing restores "
                         "PLAN.md byte-identical (incompatible with --to)")
    pa.set_defaults(func=cmd_advance, _opt_positionals=("slug",))

    prx = sub.add_parser("re-cross", help="re-arm the tests->build snapshots after a "
                                          "HUMAN-APPROVED post-freeze test change")
    prx.add_argument("slug", nargs="?", default=None)
    prx.add_argument("--by", default="",
                     help="the human approver (required — a post-freeze test change is human-approved)")
    prx.set_defaults(func=cmd_recross, _opt_positionals=("slug",))

    pg = sub.add_parser("gate", help="record a verify gate outcome")
    pg.add_argument("outcome", nargs="?", default=None)   # validated in cmd_gate (gate-explain
    pg.add_argument("slug", nargs="?", default=None)      # made it optional under --explain)
    pg.add_argument("--explain", action="store_true",
                    help="READ-ONLY: print the composed auto-pass/escalation path for the task "
                         "(autonomy · risk · sensitivity · advisor verdict), then exit")
    pg.add_argument("--target-hit", dest="target_hit", default=None,
                    help="the §3 Target judgment: yes|partial|no (plan-core; recorded in "
                         "state + the route-outcome trace; omit when no Target declared)")
    pg.add_argument("--owner", help="RISK-ACCEPTED waiver: accountable owner")
    pg.add_argument("--ticket", help="RISK-ACCEPTED waiver: tracking ticket/link")
    pg.add_argument("--expires", help="RISK-ACCEPTED waiver: expiry date")
    pg.set_defaults(func=cmd_gate, _opt_positionals=("slug",))

    pan = sub.add_parser("autonomy", help="show or set the autonomy level (the verify-gate owner)")
    pan.add_argument("action", nargs="?", choices=("show", "set"), default="show")
    pan.add_argument("a1", nargs="?", default=None, help="set: <level>; show: [slug]")
    pan.add_argument("a2", nargs="?", default=None, help="set: [slug]")
    pan.add_argument("--project", action="store_true",
                     help="set the PROJECT.md default instead of a task header")
    pan.add_argument("--yes", action="store_true",
                     help="confirm a RAISE toward auto (a human-owned trust escalation)")
    pan.set_defaults(func=cmd_autonomy, _opt_positionals=("a1", "a2"))

    pto = sub.add_parser("todo", help="capture / list / close a lightweight backlog todo (jot an idea)")
    pto.add_argument("text", nargs="?", default=None,
                     help="todo text to capture; omit to LIST open todos")
    pto.add_argument("--done", type=int, default=None, metavar="ID",
                     help="close an open todo by id")
    pto.set_defaults(func=cmd_todo)

    pr = sub.add_parser("reopen", help="return a done task to an earlier phase with a recorded reason")
    pr.add_argument("slug", nargs="?", default=None)
    # --to / --reason are validated in-body (not argparse choices) so the named reject
    # codes fire (reopen_target_invalid / reopen_reason_required), not a bare exit-2.
    pr.add_argument("--to", default=None, help="target phase (specify..verify)")
    pr.add_argument("--reason", default="", help="why the task is reopened (required, non-empty)")
    pr.set_defaults(func=cmd_reopen, _opt_positionals=("slug",))

    ph = sub.add_parser("heal", help="report a confirmed cheat: bounded return-to-build, then escalate")
    ph.add_argument("slug", nargs="?", default=None)
    # --reason validated in-body so the named rejects fire (heal_reason_required /
    # heal_not_at_verify), not a bare argparse usage-2.
    ph.add_argument("--reason", default="", help="the refute-read finding (required, non-empty)")
    ph.set_defaults(func=cmd_heal, _opt_positionals=("slug",))

    ps = sub.add_parser("stage", help="set the project stage")
    ps.add_argument("stage", choices=STAGES)
    ps.add_argument("--force", action="store_true",
                    help="override the →production roadmap guard (stage_no_roadmap)")
    ps.set_defaults(func=cmd_stage)

    pst = sub.add_parser("status", help="print where the project is (resume point)")
    pst.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pst.add_argument("--task", metavar="SLUG", help="with --json, filter to one task's "
                      "{slug, phase, gate, milestone, owner, assignee} object")
    pst.add_argument("--all", action="store_true", help="show every milestone/task "
                      "(default: top 10 by most-recently-updated)")
    pst.add_argument("--brief", action="store_true",
                     help="resume essentials only: the active task's slug · phase + the next: hint")
    pst.add_argument("--section", default=None, metavar="N|PHASE",
                     help="print ONE raw §body (0-7 or a phase name) of the active task — "
                          "read a section, not the whole PLAN.md")
    pst.add_argument("--foundation", nargs="?", const="", default=None, metavar="SECTION",
                     help="scoped PROJECT.md read (progressive disclosure): bare = the map "
                          "(invariants + Domain + Spec full, other sections collapsed to a pull "
                          "hint); SECTION = pull one section body on demand; --all = the whole foundation")
    pst.set_defaults(func=cmd_status)

    pck = sub.add_parser("check", help="read-only integrity check of the .add project")
    pck.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pck.set_defaults(func=cmd_check)

    psrch = sub.add_parser("search", help="keyword/substring search over the "
                            "milestone/task corpus (active + archived) — "
                            "title/goal/rationale lines only, never the full body")
    psrch.add_argument("keywords", nargs="+", metavar="KEYWORD",
                       help="one or more keywords (case-insensitive substring, OR-combined)")
    psrch.add_argument("--json", action="store_true", help="machine-readable JSON output")
    psrch.set_defaults(func=cmd_search)

    psg = sub.add_parser("sync-guidelines",
                         help="(re)write the ADD guideline block into AGENTS.md + CLAUDE.md")
    psg.set_defaults(func=cmd_sync_guidelines)

    pgd = sub.add_parser("guide", help="print the one concrete next step for the active task")
    pgd.add_argument("slug", nargs="?", default=None, help="task slug (default: active task)")
    pgd.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pgd.set_defaults(func=cmd_guide, _opt_positionals=("slug",))

    prp = sub.add_parser("report",
                         help="capture/render a milestone's what-happened report (read-only)")
    prp.add_argument("milestone", nargs="?", default=None,
                     help="milestone slug for the rollup, OR a task slug to drill into "
                          "(smart: tried as a milestone first, then as a task); "
                          "default: active milestone")
    prp.add_argument("task", nargs="?", default=None,
                     help="explicit `report <milestone> <task>`: render that task's "
                          "per-phase detail instead of the milestone rollup")
    prp.add_argument("--json", action="store_true",
                     help="emit raw structured data (rollup -> report_data dict; "
                          "drill -> task_phases list of 7 phase dicts)")
    prp.add_argument("--plain", action="store_true",
                     help="ASCII, no color, fixed width (pipe / CI / screen-reader safe)")
    prp.add_argument("--decide", action="store_true",
                     help="decision-point digest: what needs the human's judgment NOW "
                          "(task -> decision digest; milestone -> DECIDE NEXT only; "
                          "bare -> the active task)")
    prp.set_defaults(func=cmd_report, _opt_positionals=("milestone", "task"))

    pdt = sub.add_parser("deltas",
                         help="read-only report: open lessons learned grouped by competency")
    pdt.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pdt.set_defaults(func=cmd_deltas)

    ppj = sub.add_parser("project", help="print .add/PROJECT.md (the read-first foundation)")
    ppj.set_defaults(func=cmd_project)

    return p


def _rebind_optional_positionals(parser: argparse.ArgumentParser,
                                 args: argparse.Namespace,
                                 extras: list[str]) -> argparse.Namespace:
    """argv portability (py<=3.12): argparse cannot bind an optional positional that
    trails value-taking flags once a REQUIRED positional was consumed in an earlier
    block — `gate RISK-ACCEPTED --owner X --ticket Y --expires Z <slug>` dies
    `unrecognized arguments: <slug>` on 3.10/3.11/3.12 (3.13+ parses it natively).
    Fix at main(): parse_known_args leaves the stranded slug in `extras`; re-bind
    non-flag extras into UNFILLED (still-default-None) optional positionals, in the
    order each subparser declared via set_defaults(_opt_positionals=...).
    Safety rule (frozen §3, engine-argv-portability): ANY flag-like extra refuses the
    WHOLE re-bind, and leftover extras re-raise the stock exit-2 error — a typo'd
    flag's value must never be mis-bound as a slug (that would gate the WRONG task)."""
    slots = [name for name in getattr(args, "_opt_positionals", ())
             if getattr(args, name, None) is None]
    if any(tok.startswith("-") for tok in extras) or len(extras) > len(slots):
        parser.error("unrecognized arguments: " + " ".join(extras))
    for name, value in zip(slots, extras):
        setattr(args, name, value)
    return args


# --- agent-agnostic update nudge --------------------------------------------
# ADD is agent-agnostic: ANY agent (Claude Code · Gemini CLI · Codex) is told by the
# guideline block to run `add.py status`/`guide` FIRST, every session. That is the one
# universal chokepoint to tell a stale install to refresh — a plain line on STDERR the
# agent reads and acts on. Bounded + fail-open by design (see _maybe_nudge_update).
#
# This is the engine's ONE deliberate, isolated network touch. It is justified narrowly:
# an agent that is offline cannot run at all, so when the network is unreachable this
# silently does nothing and nothing is lost. It NEVER changes a command's stdout or exit.
_UPDATE_CACHE = ".update-cache.json"
_UPDATE_TTL = timedelta(hours=24)          # hit the registry at most once / day
def _write_json_safe(path: Path, obj) -> None:
    try:
        path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def _cached_latest(add_dir: Path):
    """The registry's latest version, throttled: served from .update-cache.json within
    the TTL, else refreshed over the network (fail-open). None when unknown."""
    cache = _read_json_safe(add_dir / _UPDATE_CACHE)
    if cache and cache.get("latest") and cache.get("checked_at"):
        try:
            ts = datetime.fromisoformat(cache["checked_at"])
            if datetime.now(timezone.utc) - ts < _UPDATE_TTL:
                return cache["latest"]                     # fresh -> no network
        except ValueError:
            pass
    latest = _fetch_latest_version()
    if latest:
        _write_json_safe(add_dir / _UPDATE_CACHE, {
            "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "latest": latest,
        })
        return latest
    return cache.get("latest") if cache else None          # stale beats nothing


def _maybe_nudge_update(args: argparse.Namespace) -> None:
    """If the tooling is stale, print an ACTION-REQUIRED line to STDERR so the agent
    updates before the user's task. Fully bounded + fail-open — never raises, never
    touches stdout or the exit code."""
    try:
        if os.environ.get("ADD_NO_UPDATE_CHECK"):
            return
        fn = getattr(args, "func", None)
        # orientation reads only — never a mid-run mutating verb (gate/advance/...)
        if getattr(fn, "__name__", "") not in ("cmd_status", "cmd_guide"):
            return
        add_dir = find_root()
        if add_dir is None:
            return
        stamp = _read_json_safe(add_dir / ".add-version")
        current = (stamp or {}).get("version")
        if not current:
            return            # no launcher stamp -> inert (engine-only/test projects)
        latest = _cached_latest(add_dir)
        if not latest or not _version_gt(latest, current):
            return
        cmd = ("pipx run pilotspace-add update"
               if (stamp or {}).get("channel") == "pip"
               else "npx @pilotspace/add@latest update")
        sys.stderr.write(
            f"\n⚠ ADD is out of date: this project is on {current}, latest is {latest}.\n"
            f"  ACTION REQUIRED before the user's task: run `{cmd}`, then re-read the "
            f"guide from disk, then continue.\n\n")
    except Exception:
        return                # a nudge must NEVER break a command (design-for-failure)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args, extras = parser.parse_known_args(argv)
    if extras:
        args = _rebind_optional_positionals(parser, args, extras)
    # kickoff-truth M3: register the true invocation for the dup-failure fingerprint
    # (explicit argv in-process, sys.argv from the CLI), and clear the sidecar on any
    # successful exit so only CONSECUTIVE identical failures short-circuit.
    _register_invocation(sys.argv[1:] if argv is None else list(argv))
    _maybe_nudge_update(args)        # advisory preamble; stderr-only, fail-open
    args.func(args)
    _clear_last_fail()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
