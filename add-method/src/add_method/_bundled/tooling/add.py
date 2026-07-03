#!/usr/bin/env python3
"""ADD — minimal scaffolder + state tracker for AI-Driven Development.

One file = one task. This tool generates the per-task TASK.md (which Claude fills
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
    _RULE_REF_LINE, _FALLBACK_TASK, _FALLBACK_TASK_FAST,
    _DEFAULT_WIDTH,
    _DELTA_RE, _PERSONA_TAG_RE, _EVIDENCE_RE, _SPEC_DELTA_RE,   # shared delta regexes (taskdoc + deltas-web lint)
    _SEED_POINTER_RE,   # shared (delta-task-backlink) — reads the `[→ slug]` seed stamp back
    _AUTONOMY_LEVELS,   # shared (autonomy resolvers + _AUTONOMY_ORDER/cmd_autonomy)
    _STREAMS_POSTURES,  # shared (streams resolvers + cmd_streams) — run-mode streams half
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
from add_engine.components import (
    _confined, _components, _cite_region, _contracts, _federation,
    _contract_snapshot, _in_scope,
)

# --- update-nudge version helpers (moved to add_engine/version.py) ----------
from add_engine.version import (
    _read_json_safe, _version_gt, _fetch_latest_version,
)

# --- changelog/RELEASES render helpers (moved to add_engine/release.py) -----
from add_engine.release import (
    _releases_path, _closed_milestones, _key_decisions_for,
    _build_in_flight, _render_changelog_block, _render_releases_row,
)

# --- TASK.md structural readers (moved to add_engine/taskdoc.py) ------------
from add_engine.taskdoc import (
    _task_header, _count_test_defs, _primary_test_files, _tests_count,
    _declared_test_files, _declared_tests_count, _tests_info, _task_prose,
    _phase_spans, _raw_phase_bodies, _spec_delta_entries,
)

# --- autonomy-level resolvers (moved to add_engine/autonomy.py) -------------
from add_engine.autonomy import (
    _autonomy_level, _effective_autonomy, _project_autonomy, _project_autonomy_token,
    _project_streams,   # run-mode streams half (persist-run-mode) — read live from PROJECT.md
)

# --- keyword/substring corpus search (NEW — add_engine/search.py) -----------
from add_engine.search import _search_corpus


def _phase_index(name: str) -> int:
    """Ordinal of a phase in PHASES; used to enforce forward-skip rules."""
    return PHASES.index(name)

# --- low-level IO (moved to add_engine/io_state.py — engine-modularization) -
from add_engine.io_state import (  # re-exported as module globals: callers use bare
    _now, _atomic_write, _atomic_write_bytes, _atomic_write_many,  # names so patches
    find_root, _require_root, _migrate_state, _state_text_or_die,  # on add.<name>
    _die,                                                          # still resolve;
    _CONFLICT_MARKER_RE,                                            # conflict-marker re
    _load_state_for_json,                                          # --json state loader
    _md5_text, _md5_file,                                          # md5 hashing helpers
)


# --- active milestone/task accessors (moved to add_engine/accessors.py) -------
from add_engine.accessors import (
    _active_milestone, _active_task, _set_active_milestone,
    _set_active_task, _activate_milestone, _deactivate_milestone,
)

# --- state load/save (KEPT in add.py: write-path pinned by add._atomic_write tests) -

def load_state(root: Path) -> dict:
    """Load + parse state.json, failing CLOSED. A git-conflicted file dies with a merge-specific
    'state_conflicted'; any other corrupt/unreadable file dies with a clean 'state_invalid'
    message (never a raw traceback), so every command that loads state degrades gracefully
    (design-for-failure). The parsed state is forward-migrated to the multi-active schema."""
    try:
        return _migrate_state(json.loads(_state_text_or_die(root)))
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

    Falls back to a built-in minimal template for TASK.md and the fast-lane TASK.fast.md.
    """
    tmpl = _templates_dir() / f"{name}.tmpl"
    _fallbacks = {"TASK.md": _FALLBACK_TASK, "TASK.fast.md": _FALLBACK_TASK_FAST}
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


# --- TASK.md milestone backlink (task-milestone-backlink) --------------------
# The task↔milestone link is mirrored into the TASK.md header so the file names its
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
    """Rewrite (or insert) the TASK.md header `milestone:` backlink — idempotent.

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
    """The current `milestone:` backlink value in a TASK.md header, or None if absent."""
    m = _MILESTONE_LINE_RE.search(text)
    return m.group(0)[len("milestone:"):].strip() if m else None


# --- MILESTONE.md release backlink (milestone-release-backlink) --------------
# The milestone↔release link is mirrored into the MILESTONE.md header: the template seeds
# `release: pending`; cmd_release STAMPS it to the cut version (the stamp rides the same
# all-or-nothing batch as CHANGELOG + RELEASES). The mirror of _set_milestone_line, one
# scope level up — keying on `^release:`, inserting after the `stage:` line if absent.
_RELEASE_LINE_RE = re.compile(r"(?m)^release:[^\n]*$")
_STAGE_LINE_RE = re.compile(r"(?m)^stage:[^\n]*$")


def _set_release_line(text: str, value: str) -> str:
    """Rewrite (or insert) the MILESTONE.md header `release:` backlink — idempotent.

    A grandfathered file lacking the line gets it inserted right after the `stage:` line;
    with no stage line either, the text is returned unchanged (degrade-safe)."""
    line = f"release: {value}"
    if _RELEASE_LINE_RE.search(text):
        return _RELEASE_LINE_RE.sub(lambda _m: line, text, count=1)
    m = _STAGE_LINE_RE.search(text)
    if not m:
        return text
    return text[:m.end()] + "\n" + line + text[m.end():]


# --- §0 GROUND drift anchor (ground-anchor-sha) -----------------------------
# §0 line numbers rot during BUILD while symbols survive (PR40 audit). The engine SEEDS a
# `Ground SHA:` field (the AI fills it via git — NO-EXEC: add.py never shells out) and `check`
# WARNs when a §0 cites bare line numbers without one, so drift is detectable not silent.
_GROUND_SHA_RE = re.compile(r"(?m)^Ground SHA:[ \t]*(.*?)[ \t]*$")
_LINE_REF_RE = re.compile(r"l\.\d+")


def _ground_section(text: str) -> str:
    """The §0 GROUND block of a TASK.md — from the `## 0` heading to the next `## ` heading."""
    m = re.search(r"(?m)^## 0\b", text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"(?m)^## ", rest)
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


# --- tidy a closed TASK.md (strip-scaffold-at-done) --------------------------
# A live TASK.md carries `<!-- … -->` instruction comments that guide the active phase; once the
# task is `done` they are dead weight (PR40 audit). cmd_gate strips them on a COMPLETING gate.
# Content-safe: fenced code blocks (```…```, incl. the frozen §3) pass through BYTE-EXACT — only
# comments OUTSIDE a fence are removed; idempotent.
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_TRAILING_WS_RE = re.compile(r"(?m)[ \t]+$")
_BLANK_RUN_RE = re.compile(r"\n{3,}")


def _strip_live_scaffold(text: str) -> str:
    """Remove `<!-- … -->` instruction comments from a TASK.md — fences untouched, idempotent.

    Splits on fenced code blocks so a comment inside a ``` fence (e.g. the frozen §3) is never
    touched; in the non-fence segments it drops comment spans, trims the trailing whitespace a
    removal leaves on a line, and collapses 3+ consecutive newlines to one blank line."""
    segs = re.split(r"(```.*?```)", text, flags=re.DOTALL)
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
    _phase_owner, _setup_locked, _milestone_confirmed, _section_unfilled,
    _task_done, _persona_missing, _persona_slug_valid, _rule_coverage_gaps,
)

# --- git-native identity/actor seam (moved to add_engine/identity.py) --------
from add_engine import identity            # qualified calls: identity._whoami(...)
from add_engine.identity import (          # re-exported for `add.<name>` attr compat
    _git_config, _os_user, _whoami, _actor_stamp,
    _render_actor_line, _parse_actor_arg, _actor_matches,
)


def _my_work(state: dict, me: dict, scope_all: bool = False) -> list[dict]:
    """The "my work" lens (multi-active-UX): the NOT-done tasks whose owner OR assignee is `me`.
    By default the lens is the active SET; `scope_all=True` (mine-all-lens) widens it to EVERY
    milestone plus loose (milestone-less) tasks. Returns ordered rows {slug, milestone, phase,
    role} with role in {owner, assignee, both}, sorted by active-milestone order then slug
    (non-active/loose sort after the active block, then by slug). PURE · no I/O."""
    active = list(state.get("active_milestones") or [])
    active_set = set(active)
    tasks = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}
    rows: list[dict] = []
    for slug, t in tasks.items():
        if not isinstance(t, dict) or _task_done(t):
            continue
        if not scope_all and t.get("milestone") not in active_set:
            continue
        owns = identity._actor_matches(t.get("owner"), me)
        assigned = identity._actor_matches(t.get("assignee"), me)
        if not (owns or assigned):
            continue
        role = "both" if owns and assigned else ("owner" if owns else "assignee")
        rows.append({"slug": slug, "milestone": t.get("milestone"),
                     "phase": t.get("phase"), "role": role})
    order = {m: i for i, m in enumerate(active)}
    rows.sort(key=lambda r: (order.get(r["milestone"], len(order)), r["slug"]))
    return rows


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
    f = root / "tasks" / slug / "TASK.md"
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
    # component-aware-add (per-component-verify) + component-registry-fill: record WHICH green-bar
    # the bound task gated against AND the component's verify COMMAND, right after the Outcome line.
    # Unbound / neither declared -> no line (byte-identical). green-bar-only output is unchanged.
    _bar = _task_green_bar(root, slug)
    _vfy = _task_verify(root, slug)
    if _bar or _vfy:
        _parts = [f"component: {_task_component(root, slug)}"]
        if _bar:
            _parts.append(f"expected green-bar: {_bar}")
        if _vfy:
            _parts.append(f"verify: {_vfy}")
        _line = " · ".join(_parts)        # deterministic per task -> idempotent on re-stamp
        if _line not in new:
            new = re.sub(r"(?m)^(Outcome:.*$)", lambda m: m.group(1) + "\n" + _line, new, count=1)
    if new != text:                              # no-op = no write (mtime stable)
        _atomic_write(f, new)


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
    f = root / "tasks" / slug / "TASK.md"
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
            m = re.search(r"(?m)^Framings weighed:[ \t]*(.+)$", bodies.get(1, ""))
            if not m:
                return UN, ""
            chosen, rejected = UN, []
            for p in (s.strip() for s in m.group(1).split("·") if s.strip()):
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
            m = re.search(r"(?m)^Strategy actually used:[ \t]*(.+)$", bodies.get(5, ""))
            if m:
                # UNFILLED is the "<fill at …>" template token; a real value may legitimately
                # contain "<" (quoting `<tag>`, "x < y") and must NOT degrade to the default
                val = m.group(1).strip()
                if val and not val.startswith("<fill"):
                    return val
        except Exception:
            pass
        return "as planned"

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
        strat = _strategy()
        outcome, rev, gate_actor = _gate()
    except Exception:
        return                                   # never block the gate
    rej = f"; rejected {rejected}" if rejected else ""
    lines = [
        f"- [AI] specify — chose {chosen}{rej}",
        f"- [human] freeze — froze §3 @ {fver} (approved by {fby})",
        f"- [AI] build — strategy used: {strat}",
        f"- [{gate_actor}] verify — gate {outcome} (reviewed by {rev})",
    ]
    new = text[:ph_start] + "\n".join(lines) + text[ph_end:]
    if new != text:
        _atomic_write(f, new)


# --- guidelines / CLAUDE.md-injection subsystem (moved to add_engine/guidelines.py) -
from add_engine.guidelines import (
    _guideline_block, _inject_block, _rule_file_mode, _strip_inline_block,
    _insert_rule_reference, _ensure_claude_reference, _inject_guidelines, _is_brownfield,
)
def cmd_init(args: argparse.Namespace) -> None:
    base = Path(args.dir).resolve()
    root = base / ROOT_DIRNAME
    state_path = root / STATE_FILE
    if state_path.exists() and not args.force:
        _die(f"already initialised at {root} (use --force to reset state)")

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

    # survivor-layer files — never clobber an existing one, never write a blank one
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

    # --run-mode: apply the paired autonomy + streams posture into PROJECT.md.
    # ONLY when the flag is explicitly set — absent flag leaves PROJECT.md byte-identical.
    run_mode = getattr(args, "run_mode", None)
    if run_mode is not None:
        _level = run_mode                                           # "auto" | "conservative"
        _posture = "parallel" if run_mode == "auto" else "sequential"
        proj_md = root / "PROJECT.md"
        if proj_md.exists():
            _text = proj_md.read_text(encoding="utf-8")
            _text = _autonomy_decl_line(_text, _level)
            _text = _streams_decl_line(_text, _posture)
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
    for name, action in _inject_guidelines(base, getattr(args, "rule_file", False)):
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
    # setup hygiene (both branches): the .add/ folder IS the shared project state — commit it
    # so the team shares one source of truth; its transient working files are already gitignored.
    print("tip:  commit the .add/ folder to git so your team shares the ADD state "
          "(its transient files are already .gitignored).")


def cmd_sync_guidelines(args: argparse.Namespace) -> None:
    project_root = _require_root().parent
    for name, action in _inject_guidelines(project_root, getattr(args, "rule_file", False)):
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
    task_md = tdir / "TASK.md"
    if task_md.exists() and not args.force:
        _die(f"task '{slug}' already exists (use --force to overwrite TASK.md)")

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

    # SEED (--from-delta): resolve a prior task's FIRST open SPEC delta into THIS task.
    # validate-ALL-then-write — resolve the prior, read its open delta, and compute the
    # seeded flip NOW (before any write); the slug-free check above has already passed, so
    # the only writes below are the new TASK.md, then the prior flip, then state.
    from_delta = getattr(args, "from_delta", None)
    match = getattr(args, "match", None)
    if match and not from_delta:                            # --match targets the PRIOR's delta
        _die("match_requires_from_delta: --match needs --from-delta <prior> (it selects the "
             "prior task's open SPEC delta to seed)")
    feature_override = prior_md = flipped_prior = None
    if from_delta:
        prior = _resolve_task(state, from_delta)            # unknown prior -> _die
        prior_md = root / "tasks" / prior / "TASK.md"
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
    # fast lane (fast-new-task-flag): --fast scaffolds the MINIMAL template instead of the full one.
    # The human opts in explicitly (the engine never guesses ceremony); the freeze floor is held by
    # the freeze-before-build gate's fast arm (cmd_advance), so the lighter shape never drops the trust seam.
    fast = bool(getattr(args, "fast", False))
    rendered = _render_template(
        "TASK.fast.md" if fast else "TASK.md",
        title=title, slug=slug, date=date.today().isoformat(),
        stage=state["stage"], autonomy=autonomy,
        milestone=_milestone_backlink_value(milestone))
    if feature_override:                                     # pre-fill §1 from the seeded delta
        rendered = re.sub(r"(?m)^Feature:.*$",
                          lambda _m: f"Feature: {feature_override}", rendered, count=1)
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
    _atomic_write_many(seed_writes)                         # new TASK.md + consumed source as one commit
    if _project_autonomy_token(root) == "?":
        print("warning: garbled_project_autonomy — PROJECT.md declares an unrecognized "
              f"autonomy token; new task seeded fail-safe '{autonomy}' "
              "(fix it with `add.py autonomy set <level> --project`)", file=sys.stderr)

    # F8 (force-preserve-heal): a --force overwrite RE-CREATES the record; capture the prior
    # MONOTONIC heal counter first so it survives. Else a task that accrued heal attempts (or
    # was HARD-STOP escalated) could launder the cap (HEAL_CAP) to zero by re-creating itself —
    # a zero-human cap bypass (the same invariant _heal_or_escalate guards: "never auto-resets").
    prior_heal = state["tasks"].get(slug, {}).get("heal") if args.force else None
    state["tasks"][slug] = {
        "title": title,
        "phase": "ground",
        "gate": "none",
        "milestone": milestone,
        "depends_on": depends_on,
        "created": _now(),
        "updated": _now(),
    }
    if prior_heal is not None:
        state["tasks"][slug]["heal"] = prior_heal   # monotonic — survives the --force re-create
    if from_delta:
        state["tasks"][slug]["from_delta"] = from_delta     # lineage: seeded from <prior>
    if fast:
        state["tasks"][slug]["fast"] = True                 # durable lane marker (absent == not-fast)
    _set_active_task(state, slug, milestone)
    save_state(root, state)
    print(f"created task '{slug}' -> {task_md}")
    if milestone:
        print(f"linked to milestone '{milestone}'" +
              (f", depends-on {depends_on}" if depends_on else ""))
    elif fast:
        # blessed milestone-free fast lane (standalone-fast-task): a --fast task with no owning
        # milestone is a DELIBERATE low-ceremony lane, not an orphan to nag — AFFIRM it.
        print(f"standalone fast task '{slug}' — milestone-free by design (low-ceremony lane); "
              f"attach later with `add.py set-milestone {slug} --milestone <id>` if it grows")
    else:
        # warn-never-block: the task is created (escape hatch), but nudge back toward the
        # intake -> milestone flow. Speaks of STRUCTURE (not attached), never the act.
        print(f"note: '{slug}' is not attached to a milestone — size it via /add (intake), "
              "or pass --milestone <id>")
    if from_delta:
        print(f"seeded from '{from_delta}' — its open SPEC delta is now "
              f"[SPEC · seeded] … [→ {slug}]; §1 Feature pre-filled.")
    print("active task set. phase: ground. Gather the real codebase (section 0 GROUND).")
    print(_next_footer(root, state))   # converges the old "then: add.py advance" hint


def cmd_drop_delta(args: argparse.Namespace) -> None:
    """DISMISS a task's first open SPEC delta — `[SPEC · open]` -> `[SPEC · dropped]`.

    The dismiss half of the SPEC-delta resolution pair (seed lives on `new-task
    --from-delta`). Validate-then-write: refuse `no_open_spec_delta` before any write;
    text + `(evidence: …)` are byte-preserved by the pure `_resolve_spec_delta`."""
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)                  # unknown task -> _die
    task_md = root / "tasks" / slug / "TASK.md"
    text = task_md.read_text(encoding="utf-8")
    match = getattr(args, "match", None)
    status, idx, _disp = _select_spec_delta(text, match)
    if status == "no_open":
        _die(f"no_open_spec_delta: task '{slug}' has no open SPEC delta to drop")
    if status == "no_match":
        _die(f"no_matching_spec_delta: no open SPEC delta in '{slug}' matches --match '{match}'")
    if status == "ambiguous":
        _die(f"ambiguous_spec_match: --match '{match}' matches multiple open SPEC deltas in "
             f"'{slug}' — narrow it")
    new_text = _resolve_spec_delta(text, "dropped", line_index=idx)
    _atomic_write(task_md, new_text)
    print(f"dropped the {'matched' if match else 'first'} open SPEC delta in '{slug}' -> [SPEC · dropped]")
    print(_next_footer(root, state))


def _open_spec_delta_indices(text: str) -> list[int]:
    """Every splitlines(keepends=True) index of an `[SPEC · open]` line (carry-delta --all). PURE.
    A SPEC flip preserves line count + position, so these indices stay valid across sequential
    flips."""
    return [i for i, ln in enumerate(text.splitlines(keepends=True))
            if (m := _SPEC_DELTA_RE.match(ln.rstrip("\n"))) and m.group(2) == "open"]


def cmd_carry_delta(args: argparse.Namespace) -> None:
    """DEFER a task's open SPEC delta(s) non-lossily — `[SPEC · open]` -> `[SPEC · carried]`
    + a ` [carried: <reason>]` stamp (delta-drain). A carried delta clears the release floor and
    the `status` staleness count but SURVIVES on disk: retrievable via `add.py deltas --carried`
    and re-activatable via `reopen-delta`. `--reason` is REQUIRED (no silent carry); `--all` carries
    every open delta in the task; `--match` targets the unique one. Validate-then-write."""
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)                  # unknown task -> _die
    reason = (getattr(args, "reason", None) or "").strip()
    if not reason:
        _die("carry_reason_required: carry-delta needs a --reason — a deferral must say why "
             "(it is the breadcrumb a future loop reads)")
    task_md = root / "tasks" / slug / "TASK.md"
    text = task_md.read_text(encoding="utf-8")
    stamp = f"[carried: {reason}]"
    if getattr(args, "all", False):
        idxs = _open_spec_delta_indices(text)
        if not idxs:
            _die(f"no_open_spec_delta: task '{slug}' has no open SPEC delta to carry")
        for idx in idxs:                                   # indices stay valid (flip is in-place)
            text = _resolve_spec_delta(text, "carried", line_index=idx, stamp=stamp)
        _atomic_write(task_md, text)
        print(f"carried {len(idxs)} open SPEC delta(s) in '{slug}' -> [SPEC · carried]  ({reason})")
        print(_next_footer(root, state))
        return
    match = getattr(args, "match", None)
    status, idx, _disp = _select_spec_delta(text, match)
    if status == "no_open":
        _die(f"no_open_spec_delta: task '{slug}' has no open SPEC delta to carry")
    if status == "no_match":                               # a --match miss is DISTINCT from no-open
        _die(f"no_matching_spec_delta: no open SPEC delta in '{slug}' matches --match '{match}'")
    if status == "ambiguous":
        _die(f"ambiguous_spec_match: --match '{match}' matches multiple open SPEC deltas in "
             f"'{slug}' — narrow it, or use --all")
    new_text = _resolve_spec_delta(text, "carried", line_index=idx, stamp=stamp)
    _atomic_write(task_md, new_text)
    print(f"carried the {'matched' if match else 'first'} open SPEC delta in '{slug}' -> "
          f"[SPEC · carried]  ({reason})")
    print(_next_footer(root, state))


def cmd_reopen_delta(args: argparse.Namespace) -> None:
    """RE-ACTIVATE a carried SPEC delta — `[SPEC · carried]` -> `[SPEC · open]` (delta-drain).
    The inverse of carry: a deferred delta re-enters the open count + release floor + staleness.
    The ` [carried: …]` breadcrumb is stripped so a re-activated delta reads clean. `--match`
    targets the unique carried delta. Validate-then-write; refuse `no_carried_spec_delta`."""
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    task_md = root / "tasks" / slug / "TASK.md"
    text = task_md.read_text(encoding="utf-8")
    match = getattr(args, "match", None)
    status, idx, _disp = _select_spec_delta(text, match, status="carried")
    if status in ("no_open", "no_match"):
        _die(f"no_carried_spec_delta: task '{slug}' has no carried SPEC delta to reopen"
             + (f" matching --match '{match}'" if status == "no_match" else ""))
    if status == "ambiguous":
        _die(f"ambiguous_spec_match: --match '{match}' matches multiple carried SPEC deltas in "
             f"'{slug}' — narrow it")
    new_text = _resolve_spec_delta(text, "open", line_index=idx, from_status="carried")
    lines = new_text.splitlines(keepends=True)             # drop the carried breadcrumb (no accretion)
    eol = lines[idx][len(lines[idx].rstrip("\n")):]
    lines[idx] = re.sub(r"\s*\[carried:[^\]]*\]\s*$", "", lines[idx].rstrip("\n")) + eol
    _atomic_write(task_md, "".join(lines))
    print(f"reopened the {'matched' if match else 'first'} carried SPEC delta in '{slug}' -> [SPEC · open]")
    print(_next_footer(root, state))


# a §3 still carrying this template placeholder is NOT a drafted contract yet
_CONTRACT_TEMPLATE_RE = re.compile(r"<METHOD>")


def _next_freeze_version(state: dict, slug: str) -> str:
    """v1 on the first freeze; N+1 of the highest prior freeze version recorded on the
    task's state record on a re-freeze (after a change request). PURE — reads state only."""
    prior = ((state.get("tasks") or {}).get(slug) or {}).get("freeze") or {}
    m = re.fullmatch(r"v(\d+)", str(prior.get("version", "")))
    return f"v{int(m.group(1)) + 1}" if m else "v1"


def cmd_freeze(args: argparse.Namespace) -> None:
    """The §3 contract-freeze write command — the 5th engine-WRITTEN human approval (task
    freeze-actor-stamp), joining lock · gate · milestone-done · release. Flips the target
    task's §3 `Status: DRAFT` -> `FROZEN @ vN — approved by <name>` AND records a structured
    actor on the task's state record (mirrors cmd_lock's `setup.actor`), so the audit trail
    has no hole at freeze. The human RUNS it as their approval — never pre-stamped.

    validate-then-write: every refusal fires before any write. Writes TASK.md first, then
    state; a crash between degrades to today's legacy text-only freeze (never corrupt state),
    design-for-failure."""
    root = _require_root()
    state = load_state(root)
    raw_slug = getattr(args, "slug", None)
    if not raw_slug and not _active_task(state):
        _die("no_active_task: no task given and no active task is set")
    slug = _resolve_task(state, raw_slug)                  # unknown slug -> _die
    task_md = root / "tasks" / slug / "TASK.md"
    text = task_md.read_text(encoding="utf-8")
    raw3 = _phase_spans(text).get(3, "")
    phase = (state["tasks"].get(slug) or {}).get("phase", "specify")
    # --- validate (no writes); error precedence: frozen -> not-drafted -> unflagged ---
    if _contract_frozen(raw3):
        _die(f"already_frozen: {slug}'s §3 is already FROZEN — re-freeze only via a change "
             f"request back to SPECIFY")
    if _phase_index(phase) < _phase_index("contract") or _CONTRACT_TEMPLATE_RE.search(raw3):
        _die(f"contract_not_drafted: {slug}'s §3 is not a drafted contract yet — reach the "
             f"`contract` phase and replace the template before freezing")
    if not _flag_well_formed(raw3):
        _die(f"unflagged_freeze: {slug}'s §3 must surface a well-formed lowest-confidence flag "
             f"('Least-sure flag surfaced at freeze:' + a [part] tag) before it freezes")
    # the human declares the risk-CLASS at freeze (risk-sensitivity-taxonomy): a present-but-
    # unknown sensitivity token is refused here (validate-then-write — nothing is written);
    # an absent token is grandfathered (allowed), a valid member proceeds. The engine never
    # classifies — it only validates the human's declaration.
    _valid_sens = _project_sensitivity_values(root)        # base ∪ project GLOSSARY classes (sensitivity-glossary)
    if _task_sensitivity(_task_header(root, slug), valid=_valid_sens) == "?":
        _die(f"sensitivity_invalid: {slug} declares an unknown sensitivity — use one of "
             f"{', '.join(_valid_sens)} (or add the class to GLOSSARY.md's '## Sensitivity classes', "
             "or omit the line)")
    # --- write ---
    ver = _next_freeze_version(state, slug)
    who = args.by or identity._actor_stamp(state)["name"]
    # flip the `Status: DRAFT` line WITHIN the §3 region only — a bare `Status: DRAFT` in
    # §1/§2 prose must never be frozen by mistake (refute-read finding). §3 span runs from
    # its `## 3 ·` heading to the next `## `/`---`/EOF (same boundary as _phase_spans).
    h3 = re.search(r"(?m)^##\s*3\s*·.*$", text)
    if not h3:
        _die(f"contract_not_drafted: {slug}'s TASK.md has no §3 CONTRACT section")
    seg_start = h3.end()
    nxt = re.search(r"(?m)^(?:##\s|---\s*$)", text[seg_start:])
    seg_end = seg_start + (nxt.start() if nxt else len(text) - seg_start)
    new_seg, n = re.subn(r"(?m)^(\s*)Status:\s*DRAFT\s*$",
                         lambda m: f"{m.group(1)}Status: FROZEN @ {ver} — approved by {who}",
                         text[seg_start:seg_end], count=1)
    if n == 0:
        _die(f"contract_not_drafted: {slug}'s §3 has no 'Status: DRAFT' line to freeze")
    new_text = text[:seg_start] + new_seg + text[seg_end:]
    _atomic_write(task_md, new_text)                       # TASK.md first (audit source of truth)
    state["tasks"][slug]["freeze"] = {"version": ver, "frozen_at": _now(),
                                      "approved_by": who, "actor": identity._actor_stamp(state)}
    save_state(root, state)
    print(f"froze §3 of {slug} @ {ver} — approved by {who}")
    print(_next_footer(root, state))


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


def _resolve_task(state: dict, slug: str | None) -> str:
    slug = slug or _active_task(state)
    if not slug:
        _die("no task specified and no active task set")
    if slug not in state["tasks"]:
        _die(f"unknown task '{slug}'")
    return slug


def _build_entry(root: Path, state: dict, slug: str, skip_freeze: bool = False) -> None:
    """The shared tests->build entry guards + snapshots (task phase-build-guard, F4).

    Extracted VERBATIM from cmd_advance's `nxt == "build"` block so BOTH `advance` and the
    `phase build` admin override run the identical gate stack — the freeze gate, the
    build-expectations gate, the unflagged-freeze check + flag stamp, the tamper tripwire, and
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
    # (Status stays DRAFT). Still PRECEDES build-expectations: freeze §3 before pre-declaring §6.
    if not _contract_frozen(raw3):
        if not skip_freeze:
            _die("contract_not_frozen: freeze §3 before crossing into build — approve "
                 f"the contract in {slug}'s TASK.md (Status: FROZEN @ vN), or pass "
                 "--skip-freeze to cross with a recorded skip")
        state["tasks"][slug]["freeze_skipped"] = {
            "by": identity._actor_stamp(state)["name"],
            "at": _now(),
            "from_phase": state["tasks"][slug].get("phase", "tests"),
        }
    # build-expectations gate (flow-enforcement): an opted-in task may not enter build until
    # its §6 `### Build expectations` are pre-declared — so verify checks the build is RIGHT,
    # not just green. Same opt-in switch as the contract-fill gate, one level out.
    if _optin:
        if _section_unfilled(_raw_phase_bodies(root, slug).get(6, ""), "### Build expectations"):
            _die("build_expectations_unfilled: fill the §6 '### Build expectations' block "
                 f"of {slug}'s TASK.md before crossing into build")
    if _contract_frozen(raw3):
        if not _flag_well_formed(raw3):
            _die("unflagged_freeze: a frozen §3 must surface a well-formed "
                 "'Least-sure flag surfaced at freeze:' unit (>=1 [part] tag "
                 "+ substantive content; bare 'none' only as 'none material — "
                 "biggest risk: X') before crossing into build")
        state["tasks"][slug]["flag_verified"] = True
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
    else:
        state["tasks"][slug].pop("scope", None)
        try:
            side.unlink()
        except OSError:
            pass


def cmd_phase(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    if args.phase not in PHASES:
        _die(f"phase must be one of: {', '.join(PHASES)}")
    # phase-build-guard (F4): the admin override is NOT a backdoor around the tests->build gate
    # stack — setting a task to build runs the SAME _build_entry guards `advance` runs (freeze
    # gate · build-expectations · flag check · tamper tripwire · scope snapshot), so verify's
    # _tamper_guard is armed and a freeze-gated DRAFT §3 is refused. Other targets are unchanged.
    # validate-then-write: a refusal raises BEFORE the phase is set, so nothing moves. The heal
    # loop sets phase=build directly (never via cmd_phase) and so stays exempt.
    if args.phase == "build":
        _build_entry(root, state, slug, skip_freeze=getattr(args, "skip_freeze", False))
    # cross-component-recency: the `phase contract` override runs the SAME consumer HOLD `advance`
    # runs (existence + recency), so it is not a backdoor around producer_contract_unfrozen/_stale.
    if args.phase == "contract":
        _consumer_contract_hold(root, state, slug)
    state["tasks"][slug]["phase"] = args.phase
    state["tasks"][slug]["updated"] = _now()
    save_state(root, state)                    # F12: durable state FIRST (source of truth) — may _die
    _sync_task_marker(root, slug, args.phase)  # then mirror into TASK.md (best-effort) — no split-brain
    print(f"task '{slug}' phase -> {args.phase}")
    print(_next_footer(root, state))


def cmd_advance(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    cur = state["tasks"][slug]["phase"]
    idx = PHASES.index(cur)
    if idx >= len(PHASES) - 1:
        _die(f"task '{slug}' already at final phase ({cur})")
    nxt = PHASES[idx + 1]
    # build-boundary gate: pre-lock the front (specify..tests) is allowed, but crossing
    # into build/verify/observe/done is refused until `add.py lock`.
    if not _setup_locked(state) and nxt in ("build", "verify", "observe", "done"):
        _die("setup_unlocked: lock the foundation first — add.py lock")
    # intra-milestone cross-component HOLD (cross-component-milestone): a consumer of a DECLARED
    # contract may not enter §3 (scenarios->contract) until its producer froze — proven by the
    # snapshot the producer's contract->tests crossing writes (task 3). This orders a BE→FE slice
    # inside ONE milestone (the FE stays downstream of the frozen endpoint). Validate-before-write:
    # the HARD-STOP precedes the phase bump, so the task stays at `scenarios`. Undeclared id / no
    # `consumes:` header -> no hold (byte-identical; a typo'd id is a cmd_check registry finding).
    if nxt == "contract":
        # existence + RECENCY (cross-component-recency): a missing snapshot HARD-STOPs
        # producer_contract_unfrozen; a present-but-stale leftover (live producer drifted/unfroze)
        # HARD-STOPs producer_contract_stale. Shared with cmd_phase so the override is no backdoor.
        _consumer_contract_hold(root, state, slug)
    # flag-first freeze guard (task unflagged-freeze): a FROZEN §3 may not cross
    # into build without a WELL-FORMED lowest-confidence flag. On pass, stamp the
    # verified marker so `audit` enforces the flag on THIS record only (open/new
    # freezes — the unmarked predecessors are never retro-redded). REFUSE writes
    # nothing (fail-closed); below the build boundary the flag is never checked.
    if nxt == "build":
        # the tests->build entry guards + snapshots now live in the shared _build_entry helper
        # (task phase-build-guard, F4) so `advance` and the `phase build` admin override run the
        # IDENTICAL gate stack. `--skip-freeze` (freeze-gate-universal) threads through to the
        # universal freeze gate — the only recorded bypass of the now-mandatory §3 freeze.
        _build_entry(root, state, slug, skip_freeze=getattr(args, "skip_freeze", False))
    # cross-component contract artifact (cross-component-contract): the contract->tests crossing
    # is the producer's freeze-approval moment. A `produces:` task WRITES the immutable snapshot;
    # a `consumes:` task PINS the live hash — a missing/unreadable snapshot HARD-STOPS here (the
    # phase stays at `contract`, nothing pinned), so a consumer never builds against a guessed
    # shape. No role / no contracts ⇒ neither branch is taken (byte-identical).
    if nxt == "tests":
        _prod = _task_produces(root, slug)
        if _prod:
            raw3c = _raw_phase_bodies(root, slug).get(3, "")
            vm = re.search(r"FROZEN @ (v\d+)", raw3c)
            snap = {"id": _prod, "producer": (_contracts(root).get(_prod) or {}).get("producer", "?"),
                    "task": slug, "version": vm.group(1) if vm else "?",
                    "frozen": date.today().isoformat(), "hash": _contract_body_hash(raw3c)}
            sp = _contract_snapshot(root, _prod)
            cur_snap = None
            if sp.exists():
                try:
                    cur_snap = json.loads(sp.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    cur_snap = None
            # idempotent: re-write only when the shape-hash or version actually changed (so a
            # no-op re-cross leaves the file — and its `frozen` date — byte-identical).
            if not (cur_snap and cur_snap.get("hash") == snap["hash"]
                    and cur_snap.get("version") == snap["version"]):
                sp.parent.mkdir(parents=True, exist_ok=True)
                _atomic_write(sp, json.dumps(snap, sort_keys=True))
        _cons = _task_consumes(root, slug)
        if _cons:
            sp = _contract_snapshot(root, _cons)
            try:
                pinned = json.loads(sp.read_text(encoding="utf-8")).get("hash")
            except (OSError, ValueError, AttributeError):
                pinned = None
            if not pinned:        # absent / unreadable / valid-JSON-but-no-hash all fail loud
                _die(f"contract_snapshot_missing: no readable hashed .add/contracts/{_cons}.json — the "
                     f"producer of '{_cons}' must freeze its contract first "
                     "(never build against a guessed shape)")
            state["tasks"][slug]["contract_pin"] = {"id": _cons, "hash": pinned}
    state["tasks"][slug]["phase"] = nxt
    state["tasks"][slug]["updated"] = _now()
    save_state(root, state)             # F12: durable state FIRST (source of truth) — may _die
    _sync_task_marker(root, slug, nxt)  # then mirror into TASK.md (best-effort) — no split-brain
    print(f"task '{slug}' phase {cur} -> {nxt}")
    if nxt == "observe":
        # OBSERVE is where this loop's lessons get captured (TASK.md §7) — suggest routing
        # them into PROJECT.md right away (a per-task fold is engine-legal; otherwise the
        # lessons sit unconsolidated until milestone close). Additive: fires only at this
        # one transition, and the human still decides whether/when to run it. The verb word
        # is interpolated via _FOLD_VERB so the domain wording-lint sees no bare slang.
        print("  note: record the lessons this loop taught the foundation in §7 "
              "OBSERVE, then update PROJECT.md when ready:")
        print(f"    add.py {_FOLD_VERB} --task {slug}   (review first: add.py deltas)")
    print(_next_footer(root, state))


# The mechanized high-risk guard (run.md, v14; widened by explicit-autonomy-dial):
# judging WHAT is high-risk stays human — a scope declares `risk: high` in its TASK.md
# header at the freeze. The engine then enforces the pure token contradiction: risk: high
# WITHOUT a lowered autonomy rung (manual or conservative) is unguarded, and completion is
# refused. Tokens are read from the header region (text before the first section heading)
# with HTML comments stripped — a documentation comment is never a declaration. A token
# counts ONLY at a DECLARATION position — line-start (optionally indented) or just after the
# `·` slug-line separator — so a freeform H1 title or quoted prose that happens to contain
# "risk: high" / "autonomy: <x>" is never mistaken for a declaration (a title substring must
# not be able to fool the guard either way).
_RISK_HIGH_RE = re.compile(r"(?:^|·)[ \t]*risk:[ \t]*high\b", re.MULTILINE)

# sensitivity taxonomy (risk-sensitivity-taxonomy): the risk-CLASS the human declares in the
# TASK header at freeze — same anchored declaration grammar as risk:/autonomy: (line-start or
# `·`, value stops at whitespace/`<`/`#`/`|`), so a title/prose substring is never a declaration.
_SENSITIVITY_RE = re.compile(r"(?:^|·)[ \t]*sensitivity:[ \t]*([^\s<#|]+)", re.MULTILINE)

def _task_sensitivity(hdr: str, valid=None):
    """The declared sensitivity from a TASK.md header region (HTML comments already stripped by
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


# sensitivity-glossary: a project EXTENDS the universal base with domain risk-classes declared in
# GLOSSARY.md's "## Sensitivity classes" section (the AI keeps it current per the skill guide). The
# base four stay method-universal (advisor-gate-relax keys off `mechanical`) — a project never
# REMOVES them. Read live like _project_autonomy/_project_streams (no state.json field). The first
# GLOSSARY reader in the engine; degrade-safe by construction (design-for-failure).
_SENS_CLASSES_HEADING_RE = re.compile(r"(?im)^##[ \t]+sensitivity[ \t]+classes\b.*$")
# a domain line is "- <token>: …" or "- <token> — …"; the token must START with a letter, so a
# placeholder ("- <token>: …") begins with "<" and never matches, and the ": "/"—" separator keeps
# a prose bullet from being read as a class. HTML comments are stripped FIRST (mirrors _project_
# autonomy/_project_streams) so a commented-out template example is never a declaration.
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

# component-aware-add: a task binds to a registered component via a `component: <name>`
# header token — the SAME anchored grammar as autonomy (line-start or the `·`-inline
# slug-line form), and an unfilled `<name>` placeholder captures nothing (reads UNBOUND).
_COMPONENT_LINE_RE = re.compile(r"(?:^|·)[ \t]*component:[ \t]*([^\s<#|]+)", re.MULTILINE)
# cross-component-contract: a task's role in a cross-component seam — same anchored grammar.
_PRODUCES_LINE_RE = re.compile(r"(?:^|·)[ \t]*produces:[ \t]*([^\s<#|]+)", re.MULTILINE)
_CONSUMES_LINE_RE = re.compile(r"(?:^|·)[ \t]*consumes:[ \t]*([^\s<#|]+)", re.MULTILINE)


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


# step-spawn-hint (advisor-gated-autonomy): the engine's pinned terse copy of each phase
# guide's Advisor hook — one spawn idiom per phase. contract/done are ABSENT (no batch to
# fan out: a freeze is one human decision; done is closed). Advisory ONLY — the engine never
# spawns; the line just NAMES the agent shape a parallel run would use at this step.
_SPAWN_HINTS = {
    "ground": "broad sweep",
    "specify": "domain researcher",
    "scenarios": "wide scenario sweep",
    "tests": "red-suite test-author",
    "build": "independent well-scoped batch",
    "verify": "earned-green refute-read",
    "observe": "lessons-mining reviewer",
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


def cmd_gate(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    # build-boundary gate: no verdict may be recorded before the setup is locked.
    if not _setup_locked(state):
        _die("setup_unlocked: lock the foundation first — add.py lock")
    if args.outcome not in GATES:
        _die(f"outcome must be one of: {', '.join(GATES)}")
    # Completing outcomes (PASS, RISK-ACCEPTED) are the VERIFY step's verdict, so they
    # share the verify-phase guard — no silent skips (principle 7). HARD-STOP stays
    # recordable from any phase (a security finding is always HARD-STOP). The
    # deliberate, logged override is `add.py phase verify <slug>`.
    completing = args.outcome in ("PASS", "RISK-ACCEPTED")
    if completing:
        current = state["tasks"][slug]["phase"]
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
        # consumer-stale gate (consumer-stale-gate): a `consumes:` task whose pinned producer
        # contract hash has drifted from the live snapshot built against an out-of-date shape —
        # refuse the completing outcome (same before-the-waiver discipline). Re-pin to recover.
        _consumer_stale_guard(root, state, slug)
        # per-component verify (component-aware-add): a component-bound task with a declared
        # green_bar must CITE that bar in its §6 evidence before a completing outcome — the
        # engine never runs the suite, it checks the right bar was recorded. Unbound / no
        # green_bar -> _bar is None -> this is skipped (byte-identical). HARD-STOP never here.
        _bar = _task_green_bar(root, slug)
        # the cite must live in the user-authored Build-expectations evidence region (_cite_region,
        # v3): excludes the §6 checklist boilerplate + the GATE RECORD template/stamp, works for both
        # the standard and fast-lane §6 shapes. Unbound / no green_bar -> _bar None -> skipped.
        if _bar and _bar not in _cite_region(_raw_phase_bodies(root, slug).get(6, "")):
            _die(f"component_green_bar_uncited: task '{slug}' is bound to component "
                 f"'{_task_component(root, slug)}'; its §6 Build-expectations must cite the "
                 f"green-bar '{_bar}' — record the evidence that bar was met before PASS")
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
    state["tasks"][slug]["gate_actor"] = identity._actor_stamp(state)   # WHO recorded the verdict (every outcome)
    state["tasks"][slug]["updated"] = _now()
    save_state(root, state)                                # F12: durable state FIRST (source of truth) — may _die
    if completing:
        _sync_task_marker(root, slug, "done")             # then mirror the phase into TASK.md — no split-brain
    _stamp_gate_record(root, state, slug, args.outcome)   # mirror the verdict into §6 (Finding C)
    _stamp_adr_record(root, state, slug)                  # adr-at-observe: harvest §7 Decisions (ADR) — AFTER §6 is mirrored
    if completing:                                         # strip-scaffold-at-done: tidy the now-closed
        _tf = root / "tasks" / slug / "TASK.md"           # TASK.md LAST (after the stampers) — drop the
        try:                                              # live-phase `<!-- -->` comments; fences untouched.
            _tt = _tf.read_text(encoding="utf-8")
            _st = _strip_live_scaffold(_tt)
            if _st != _tt:
                _atomic_write(_tf, _st)
        except OSError:
            pass                                          # degrade-safe — the verdict is already in state
    print(f"task '{slug}' gate -> {args.outcome}")
    _gbar = _task_green_bar(root, slug)                   # per-component-verify: surface the bound bar
    if _gbar:
        print(f"component: {_task_component(root, slug)} · expected green-bar: {_gbar}")
    _vfy = _task_verify(root, slug)                       # component-registry-fill: surface the verify command
    if _vfy:
        print(f"verify: {_vfy}   # run this suite — the engine does not (NO-EXEC)")
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


def _streams_decl_line(text: str, posture: str) -> str:
    """Rewrite the SINGLE `streams:` declaration line to `posture`, PRESERVING its trailing comment,
    idempotently (replace in place, count=1 — never a second line). If absent, insert it after a
    leading `#` heading (PROJECT.md), else prepend. PURE on the text; the caller does the atomic
    write. Mirrors _autonomy_decl_line — streams is project-scoped, so there is no slug-line branch."""
    pat = re.compile(r"(?m)^(streams:[ \t]*)[^\s<#|]+(.*)$")
    if pat.search(text):
        return pat.sub(lambda m: f"{m.group(1)}{posture}{m.group(2)}", text, count=1)
    lines = text.splitlines(keepends=True)
    if lines and lines[0].lstrip().startswith("#"):
        return lines[0] + f"streams: {posture}\n" + "".join(lines[1:])
    return f"streams: {posture}\n" + text


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
    task_md = root / "tasks" / slug / "TASK.md"
    if _RISK_HIGH_RE.search(_task_header(root, slug)) and level not in ("manual", "conservative"):
        _die(f"unguarded_high_risk_auto: task '{slug}' declares risk: high — autonomy must stay "
             f"lowered (manual|conservative); refusing '{level}' (a human must own a high-risk gate)")
    _guard_autonomy_raise(_effective_autonomy(root, state, slug), level, getattr(args, "yes", False))
    _atomic_write(task_md, _autonomy_decl_line(task_md.read_text(encoding="utf-8"), level))
    print(f"task '{slug}' autonomy -> {level}")
    _print_autonomy(root, state, slug)


def cmd_streams(args: argparse.Namespace) -> None:
    """show / set the project STREAMS posture — the parallel-vs-sequential half of the run mode
    (persist-run-mode). Project-scoped (parallelism is ACROSS tasks, so there is no per-task posture)
    and unguarded by a raise (parallel drops no human gate — it only overlaps builds). The setter
    mirrors cmd_autonomy's --project branch: a PURE _streams_decl_line + atomic write into PROJECT.md.
    state.json is UNTOUCHED — the posture lives in PROJECT.md beside autonomy."""
    root = _require_root()                                   # reused -> "no .add/ project found …"
    if (getattr(args, "action", None) or "show") == "show":
        print(f"streams: {_project_streams(root)}")
        return
    posture = args.posture
    if posture not in _STREAMS_POSTURES:
        _die("streams_posture_invalid: posture must be one of "
             f"{', '.join(_STREAMS_POSTURES)} (got {posture!r})")
    target = root / "PROJECT.md"
    _atomic_write(target, _streams_decl_line(target.read_text(encoding="utf-8"), posture))
    print(f"project streams -> {posture}")


def cmd_todo(args: argparse.Namespace) -> None:
    """Capture / list / close a lightweight backlog todo (task: todo-capture).

    A todo is a JOTTED IDEA, not a task — it carries no spec/contract/gate. It lets you
    record an intent without sizing it. Promote one to a real task with
    `add.py new-task <slug> --fast` when you decide to build it. Stored in state["todos"]
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
    target = args.to
    if target not in PHASES[:-1]:        # ground..observe; never "done", never an unknown name
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
    _sync_task_marker(root, slug, target)  # then mirror into TASK.md (best-effort) — no split-brain
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
    # project as already locked, so a bare re-lock there refuses too.
    if _setup_locked(state) and not args.force:
        _die("already_locked: setup is already locked (use --force to re-lock)")
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


def cmd_whoami(args: argparse.Namespace) -> None:
    """Show / set / unset the git-native ACTOR — the identity every human-owned stamp reads.
    No flags: print the resolved actor (override -> git -> os). --name/--email: store an
    override. --unset: clear it. Validates before mutating (a reject leaves state unchanged)."""
    root = _require_root()
    state = load_state(root)
    if args.unset:
        if "actor_override" not in state:
            _die("no_actor_override")
        del state["actor_override"]
        save_state(root, state)
    elif args.name is not None:
        if not args.name.strip():
            _die("actor_name_blank")
        state["actor_override"] = {"name": args.name, "email": args.email or None}
        save_state(root, state)
    who = identity._whoami(state)
    if getattr(args, "json", False):
        print(json.dumps(who, separators=(",", ":")))
        return
    email = f" <{who['email']}>" if who.get("email") else ""
    print(f"actor : {who['name']}{email} (source: {who['source']})")


def _ownership_record(state: dict, slug: str) -> dict | None:
    """Resolve the record a slug names for ownership — a TASK first, else a MILESTONE
    (tasks win, matching cmd_use/report precedent). None if neither exists."""
    rec = state.get("tasks", {}).get(slug)
    if rec is not None:
        return rec
    return state.get("milestones", {}).get(slug)


def cmd_assign(args: argparse.Namespace) -> None:
    """Assign an OWNER (accountable) and/or ASSIGNEE (working it) to a task or milestone
    (ownership-assignment). No role flag -> set BOTH to the resolved self (_whoami); --owner/
    --assignee "Name <email>" -> set that role only (partial update). Descriptive, never a gate.
    Validate-before-mutate: a reject leaves state.json byte-identical (no partial write)."""
    root = _require_root()
    state = load_state(root)
    rec = _ownership_record(state, args.slug)
    if rec is None:
        _die("unknown_slug")
    # parse + validate ALL flags BEFORE the first write — a blank name is rejected on the
    # PARSED name (so "<>" or " <a@x.io>", whose name parses empty, is caught like "   ").
    parsed_owner = identity._parse_actor_arg(args.owner) if args.owner is not None else None
    parsed_assignee = identity._parse_actor_arg(args.assignee) if args.assignee is not None else None
    if parsed_owner is not None and not parsed_owner["name"].strip():
        _die("owner_name_blank")
    if parsed_assignee is not None and not parsed_assignee["name"].strip():
        _die("assignee_name_blank")
    if parsed_owner is None and parsed_assignee is None:
        who = identity._whoami(state)
        rec["owner"] = dict(who)
        rec["assignee"] = dict(who)
    else:
        if parsed_owner is not None:
            rec["owner"] = parsed_owner
        if parsed_assignee is not None:
            rec["assignee"] = parsed_assignee
    save_state(root, state)
    parts = [f"{role}: {rec[role]['name']}" for role in ("owner", "assignee") if role in rec]
    print(f"assigned {args.slug} -> " + " · ".join(parts))


def cmd_unassign(args: argparse.Namespace) -> None:
    """Clear the OWNER and/or ASSIGNEE of a task or milestone (ownership-assignment). No role
    flag -> clear BOTH; --owner/--assignee -> clear that role only. Reject not_assigned if the
    targeted role(s) are already absent. Validate-before-mutate (a reject changes nothing)."""
    root = _require_root()
    state = load_state(root)
    rec = _ownership_record(state, args.slug)
    if rec is None:
        _die("unknown_slug")
    if args.owner or args.assignee:
        roles = [r for r in ("owner", "assignee") if getattr(args, r)]
    else:
        roles = ["owner", "assignee"]
    if not all(r in rec for r in roles):   # every targeted role must exist (frozen: "both must exist")
        _die("not_assigned")
    for r in roles:
        rec.pop(r, None)
    save_state(root, state)
    print(f"unassigned {args.slug} ({', '.join(roles)})")


def cmd_stage(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    if args.stage not in STAGES:
        _die(f"stage must be one of: {', '.join(STAGES)}")
    # v22 stage-graduation guard: the →production TRANSITION refuses without a roadmap — a tally
    # check (≥1 production milestone exists), never a readiness judgment. Scoped to production
    # ONLY; every other flip is the existing bare flip, byte-unchanged. --force overrides
    # (precedent: lock --force). The flip is graduate.md's FINAL, confirmed-roadmap step.
    forced = getattr(args, "force", False)
    bypassing = False
    if args.stage == "production":
        roadmap = _has_production_roadmap(state)
        if not roadmap and not forced:
            _die("stage_no_roadmap: no production milestone drafted. Draft ≥1 via "
                 "graduate.md (new-milestone --stage production), or use --force to override.")
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


def cmd_status(args: argparse.Namespace) -> None:
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
                               "owner": t.get("owner"), "assignee": t.get("assignee")}))
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
        grad_ready, grad_met, grad_total = _graduation_ready(root, state)
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
                       "owner": t.get("owner"), "assignee": t.get("assignee")}
                      for s, t in page_tasks],
            "tasks_total": len(tasks),
            "graduation_ready": grad_ready,
            "stage_criteria": {"met": grad_met, "total": grad_total}}))
        return
    root = _require_root()
    state = load_state(root)
    active = _active_task(state)
    tasks = state.get("tasks", {})
    # Compute once: True when setup is present AND locked is False (the lock-gate window).
    # Reuses the canonical helper — do NOT write a parallel predicate.
    unlocked = not _setup_locked(state)
    print(f"project : {state.get('project', '(unknown)')}")
    # project autonomy default (task init-auto-default): the posture new tasks INHERIT,
    # read LIVE from PROJECT.md so the human sees the project-wide throttle every session.
    print(f"project autonomy: {_project_autonomy(root)}   (default — new tasks inherit)")
    # run mode (persist-run-mode): the combined streams + autonomy posture, both read LIVE from
    # PROJECT.md so the human sees the whole run-mode throttle every session. Advisory; engine never spawns.
    print(f"run mode: {_project_streams(root)} + {_project_autonomy(root)}")
    # git-native actor (user-identity): who ADD sees you as this session — the identity every
    # human-owned stamp records. Always present (the resolver is TOTAL). Read-only, no write.
    _who = identity._whoami(state)
    _who_email = f" <{_who['email']}>" if _who.get("email") else ""
    print(f"actor   : {_who['name']}{_who_email} (source: {_who['source']})")
    print(f"stage   : {state.get('stage', '(unknown)')}")
    # project GOAL + active-milestone goal (v20) — the loop's orientation anchor, read
    # LIVE from PROJECT.md / MILESTONE.md (never state.json). Additive: every existing
    # line stays put. A missing source degrades to a sentinel — one never blanks the other.
    print(f"goal    : {_project_goal(root)}")
    _active_ms = _active_milestone(state)
    if _active_ms:
        print(f"m-goal  : {_milestone_doc(root, _active_ms)[1]}   (← {_active_ms})")
        # goal-ready (task goal-auto-ready-gate): is the active milestone's goal AUTO-READY
        # — every exit criterion citing a verifier `(verify: …)` so the engine can self-verify
        # the result against it? Read LIVE from MILESTONE.md; surfaced every session so the
        # human sees the goal-clarity gap. Additive — human-readable only, never the JSON surface.
        _gr_cited, _gr_total = _exit_criteria_cited(root, _active_ms)
        _gr_state = "auto-ready ✓" if _goal_auto_ready(root, _active_ms) else "NOT auto-ready"
        print(f"goal-ready: {_gr_state}   ({_gr_cited}/{_gr_total} exit criteria cite a verifier)")
        # dag-plan snapshot freshness (persist-dag-plan): per-active-milestone, read-only —
        # fresh ✓ / stale / none / unreadable vs the LIVE depends_on edges. Advisory; never writes.
        print(_dag_plan_status_line(root, state, _active_ms))
    # foundation pointer — read the cross-milestone context first (anti-rot)
    if (root / "PROJECT.md").exists():
        print("context : .add/PROJECT.md  (foundation: domain · spec · UI/UX — read first)")
    # voice pointer — the AI's SOUL (tone · style · trust); read each session, edit freely.
    # Existence-only: no open/parse, so the pointer adds no IO failure path (a non-file is no voice).
    if (root / "SOUL.md").exists():
        print("voice   : .add/SOUL.md  (how I sound & what keeps your trust — read each session)")
    # wave resume hint — a live ledger outranks memory (streams.md "Wave ledger").
    # Existence-only: no open/read/parse, so the hint adds no IO failure path; a
    # non-file at the path is not a ledger. One line PER live ledger — more than
    # one live wave is an anomaly the orchestrator must see, never a line we hide.
    for _wave in sorted((root / "milestones").glob("*/WAVE.md")):
        if _wave.is_file():
            print(f"wave    : LIVE — .add/milestones/{_wave.parent.name}/WAVE.md"
                  "  (wave resume point — re-orient from the ledger first)")

    # milestone rollup (only when milestones are in use)
    milestones = state.get("milestones") or {}
    active_ms = _active_milestone(state)
    if milestones:
        print("milestones:")
        _sorted_ms = _sorted_by_updated(milestones)
        _page_ms = _sorted_ms if show_all else _sorted_ms[:_STATUS_PAGE_SIZE]
        for mslug, m in _page_ms:
            members = [t for t in tasks.values() if t.get("milestone") == mslug]
            done = sum(1 for t in members if _task_done(t))
            mark = "*" if mslug in (state.get("active_milestones") or []) else " "
            print(f"  {mark} {mslug:<20} {done}/{len(members)} tasks done"
                  f"   status={m.get('status', 'active')}")
        if not show_all and len(_sorted_ms) > _STATUS_PAGE_SIZE:
            print(f"  … {len(_sorted_ms) - _STATUS_PAGE_SIZE} more (see status --all)")
        # graduation cue (v22): project-global + read-only. Fires only when every milestone
        # is done AND the human's PROJECT.md stage-goal-criteria are all checked — additive
        # (a new line solely when ready; the non-ready output is byte-identical to before).
        grad_ready, _gm, _gt = _graduation_ready(root, state)
        if grad_ready:
            print(f"  → {GRADUATION_CUE}")

    # archived rollup — one line keeps state visible without re-bloating status
    archived = state.get("archived") or []
    if archived:
        n = len(archived)
        m_tasks = sum(rec.get("tasks", 0) for rec in archived)
        print(f"archived: {n} milestone{'s' if n != 1 else ''} "
              f"({m_tasks} task{'s' if m_tasks != 1 else ''})")

    # release cue (release-altitude): project-global + read-only. Fires when ≥1 CLOSED
    # milestone (live-done OR archived) is not yet attributed to a RELEASES.md row — so it
    # stands even with no live milestones. Additive: a line solely when releasable; the
    # ledger read is fail-open (a vanished ledger never silences the cue). See release.md.
    _rel = _releasable(root, state)
    if _rel:
        print(f"  → {RELEASABLE_CUE.format(n=len(_rel))}")
    # loose-task release cue (loose-task-release): a SEPARATE additive line — done milestone-free
    # tasks not yet attributed to a RELEASES.md `loose tasks:` row. Peer to the milestone cue (its
    # constant is untouched); fires even with zero releasable milestones. Fail-open ledger read.
    _loose = _releasable_loose_tasks(root, state)
    if _loose:
        print(f"  → releasable: {len(_loose)} loose task(s) since last release")

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
        print(f"streams : {len(_ams)} active milestones")
        for _m in _order:
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
    print("tasks   :")
    _sorted_tasks = _sorted_by_updated(tasks)
    _page_tasks = _sorted_tasks if show_all else _sorted_tasks[:_STATUS_PAGE_SIZE]
    for slug, t in _page_tasks:
        mark = "*" if slug == active else " "
        deps = t.get("depends_on") or []
        dep_s = f"  deps={','.join(deps)}" if deps else ""
        ms_s = f"  [{t['milestone']}]" if t.get("milestone") else ""
        print(f"  {mark} {slug:<24} phase={t['phase']:<10} gate={t['gate']}{ms_s}{dep_s}")
    if not show_all and len(_sorted_tasks) > _STATUS_PAGE_SIZE:
        print(f"  … {len(_sorted_tasks) - _STATUS_PAGE_SIZE} more (see status --all)")
    # fold-pressure nudge: surface unfolded competency deltas so emission can't
    # silently outrun the human fold (read-only; v11). Silent when none are open.
    open_deltas = sum(len(v) for v in _collect_open_deltas(root).values())
    if open_deltas:
        print(f"deltas  : {open_deltas} open — consolidate at milestone close (add.py deltas)")
    # SPEC-delta staleness nudge (project-wide): surface unresolved forward hand-offs as STALE
    # backpressure so they drain instead of silently accumulating (delta-drain). Read-only;
    # PRESENT-ONLY (silent when none → byte-identical). The prefix stays `spec :` (the cue the
    # spec-delta guards pin); the wording now names the staleness + the drain surface, which now
    # includes carry-delta (defer non-lossily) beside seed/drop.
    open_spec = len(_collect_open_spec_deltas(root))
    if open_spec:
        noun = "delta" if open_spec == 1 else "deltas"
        print(f"spec    : {open_spec} open SPEC {noun} — stale; drain via add.py deltas "
              "(carry-delta / new-task --from-delta / drop-delta)")
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
                print(f"          (the loop: .add/docs/{_chap})")
        else:
            print(f"\nresume  : task '{active}' is at phase '{ph}'.")
            print(f"          read .add/tasks/{active}/TASK.md and continue that phase.")


# Agent-portability (v14): `guide` names the PHASE PLAYBOOK file — the same
# guides the Claude skill loads, installed as plain markdown by every channel
# at .claude/skills/add/phases/ — so ANY agent (Cursor, Copilot, Codex) can be
# routed there through the CLI alone. Never a dead pointer: the path is printed
# only if the file exists; a missing tree gets an install hint instead.
_PHASE_GUIDE_FILES = {
    "ground": "0-ground.md",
    "specify": "1-specify.md", "scenarios": "2-scenarios.md",
    "contract": "3-contract.md", "tests": "4-tests.md",
    "build": "5-build.md", "verify": "6-verify.md", "observe": "7-observe.md",
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


def cmd_guide(args: argparse.Namespace) -> None:
    """Answer "what do I do next?" for the active (or named) task.

    Strictly read-only: load_state only — never save_state, never writes a TASK.md.
    """
    if getattr(args, "json", False):
        json_root, state = _load_state_for_json()
        slug = args.slug or _active_task(state)
        if not slug:
            print(json.dumps({"task": None, "phase": None, "owner": "human", "stop": True,
                              "next_step": "start your first feature -> add.py new-task <slug>",
                              "chapter": ".add/docs/02-the-flow.md", "gate": None,
                              "guide": None}))
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
        print(json.dumps({"task": slug, "phase": phase, "owner": owner,
                          "stop": owner != "ai", "next_step": action,
                          "chapter": f".add/docs/{chapter}", "gate": t.get("gate"),
                          "guide": _phase_guide_path(json_root.parent, phase)}))
        return
    root = _require_root()
    state = load_state(root)
    slug = args.slug or _active_task(state)
    if not slug:
        print("active : (none)")
        print('next   : start your first feature -> add.py new-task <slug> --title "..."')
        print("read   : .add/docs/02-the-flow.md")
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
    # the guide names the driver too (task gate-owner-marker) — the SAME _driver_stop the
    # footer renders, on the next-step line. Computed AFTER the unknown-phase guard above,
    # so a bad phase fails clean and never reaches the marker (it invents no default).
    marker = _driver_marker(_driver_stop(root, state, slug, phase))
    print(f"active : {slug}  (phase: {phase})")
    print(f"goal   : {_project_goal(root)}")   # v20 — the next-step surface still shows what the work is FOR
    print(f"next   : {action}{marker}")
    print(f"read   : .add/docs/{chapter}")
    gp = _phase_guide_path(root.parent, phase)
    if gp is not None:
        print(f"guide  : {gp}")
    elif phase in _PHASE_GUIDE_FILES:
        print("guide  : (phase guides not installed — npx @pilotspace/add init)")
    # step-spawn-hint (advisor-gated-autonomy): one advisory line naming the agent shape a parallel
    # run would fan out at THIS step. Present-only: suppressed under `manual` and at contract/done.
    _hint = _spawn_hint_line(
        {"phase": phase,
         "risk": "high" if _RISK_HIGH_RE.search(_task_header(root, slug)) else None},
        _project_autonomy(root))
    if _hint:
        print(_hint)
    if phase == "verify":
        print("then   : add.py gate PASS | RISK-ACCEPTED | HARD-STOP")
    elif phase == "done":
        if chapter != "02-the-flow.md":        # loop juncture / goal met -> the steered command
            print(f"then   : {action}")
        else:
            print("then   : start the next feature -> add.py new-task <slug>")
    else:
        print("then   : add.py advance")


def _read_task_phase(root: Path, slug: str) -> str | None:
    """Read the `phase:` marker from a task's TASK.md, or None if absent."""
    task_md = root / "tasks" / slug / "TASK.md"
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


def _federation_source_confined(root: Path, source: str) -> bool:
    """True iff a federation manifest `source` resolves INSIDE the sibling-repo allowlist — the
    workspace dir (root.parent.parent) that holds this project and its sibling checkouts. A legit
    cross-repo source is one level up + down (`../<repo>/…`); an absolute path or a `../../` escape
    resolves OUTSIDE and returns False. PURE + TOTAL — never raises (every error, incl. an embedded
    NUL, → False, fail-closed), so cmd_federate can gate on it BEFORE any read (federation-harden)."""
    try:
        allow = root.parent.parent.resolve()
        return _confined(root.parent / source, allow)
    except (OSError, ValueError):
        return False


def cmd_federate(args: argparse.Namespace) -> None:
    """Multi-repo federation: pull a producer repo's published, immutable contract snapshot into
    this repo. Mono vs multi-repo differ ONLY in snapshot-transport — this lands the byte-copy at
    the SAME local `.add/contracts/<id>.json` the monorepo path (tasks 3/4) already reads, so a
    `consumes: <id>` task then holds/pins identically. Designed-for-failure: unknown / escaping /
    missing / invalid / version-mismatched sources HARD-STOP and land NOTHING (never build blind)."""
    root = find_root()
    if root is None:
        _die("no_project")
    fid = args.id
    fed = _federation(root)
    if fid not in fed:
        _die(f"federation_unknown: no [federation.{fid}] in components.toml — declare the producer "
             f"repo's published snapshot source before pulling")
    # federation-harden: confine the source to the sibling-repo allowlist BEFORE any read — an
    # absolute path or a `../../` traversal must HARD-STOP and land nothing (never read a path
    # that escapes the project's sibling repos). Checked after the id lookup, before read_bytes.
    if not _federation_source_confined(root, fed[fid]["source"]):
        _die(f"federation_source_escapes: the source '{fed[fid]['source']}' for '{fid}' resolves "
             f"outside the sibling-repo allowlist (the workspace dir) — refusing to read a path "
             f"that escapes the project's sibling repos")
    source = (root.parent / fed[fid]["source"])
    try:
        raw = source.read_bytes()       # bytes — the landed snapshot must be a byte-for-byte copy
    except OSError:
        _die(f"federation_source_missing: cannot read the producer snapshot at '{fed[fid]['source']}' "
             f"(resolved {source}) — publish/commit it in the producer repo first")
    try:
        snap = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
        snap = None
    if not isinstance(snap, dict) or snap.get("id") != fid or not snap.get("hash"):
        _die(f"federation_snapshot_invalid: the source for '{fid}' is not a valid contract snapshot "
             f"(needs JSON with matching id + a hash) — refusing to land a guessed shape")
    pin = fed[fid]["pin"]
    if pin and snap.get("version") != pin:
        _die(f"federation_version_mismatch: [federation.{fid}] pins '{pin}' but the source is "
             f"'{snap.get('version')}' — bump the pin or wait for the producer to publish {pin}")
    _atomic_write_bytes(_contract_snapshot(root, fid), raw)
    print(f"federated '{fid}' {snap.get('version', '?')} {snap['hash']} from {fed[fid]['source']}")


def cmd_components(args: argparse.Namespace) -> None:
    """Read-only: print + validate the component registry (.add/components.toml).

    Opt-in — with no registry this is a friendly single-component no-op (exit 0). Prints
    the parsed components/contracts/federation, then the existing RED integrity findings
    (_component_findings + _contract_findings), then the new schema-lint WARNs
    (_component_schema_findings); exits 1 IFF a RED finding exists (a typo/WARN never fails).
    NO-EXEC — `verify` is shown as data, never run. Reads no docs/ chapter."""
    root = find_root()
    if root is None:
        _die("no_project")
    if not (root / "components.toml").exists():
        print("single-component project (no components.toml) — nothing to validate")
        return
    comps, cons, feds = _components(root), _contracts(root), _federation(root)
    for name in sorted(comps):
        c = comps[name]
        print(f"component {name}  root={c['root']}  verify={c.get('verify') or '-'}  "
              f"green_bar={c.get('green_bar') or '-'}  language={c.get('language') or '-'}")
    for cid in sorted(cons):
        c = cons[cid]
        print(f"contract {cid}  producer={c['producer']}  consumers={c['consumers']}")
    for fid in sorted(feds):
        f = feds[fid]
        print(f"federation {fid}  source={f['source']}  pin={f.get('pin') or '-'}")
    reds = sorted(_component_findings(root) + _contract_findings(root))
    warns = sorted(_component_schema_findings(root))
    for code, detail in reds:
        print(f"ERROR {code}: {detail}")
    for code, detail in warns:
        print(f"WARN {code}: {detail}")
    head = f"components: {len(comps)} · contracts: {len(cons)} · federation: {len(feds)}"
    if reds or warns:
        seg = ([f"{len(reds)} error(s)"] if reds else []) + ([f"{len(warns)} warning(s)"] if warns else [])
        print(f"{head} — {', '.join(seg)}")
    else:
        print(f"{head} — valid")
    if reds:
        raise SystemExit(1)


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
        task_md = root / "tasks" / slug / "TASK.md"
        checks.append((task_md.exists(), f"task '{slug}' has TASK.md", "file missing"))
        marker, want = _read_task_phase(root, slug), t.get("phase")
        checks.append((marker == want, f"task '{slug}' marker matches state",
                       f"marker={marker!r} state={want!r}"))
        # drift: milestone + dependency references must resolve
        ms = t.get("milestone")
        if ms is not None:
            checks.append((ms in milestones, f"task '{slug}' milestone resolves",
                           f"unknown milestone {ms!r}"))
        elif t.get("fast"):
            # blessed milestone-free fast lane (standalone-fast-task): a --fast task with no
            # milestone is DELIBERATE — a soft INFO affirmation, never a WARN/orphan nudge.
            infos.append((f"task '{slug}'", "— standalone fast lane (milestone-free by design)"))
        else:
            # warn-never-block: a task outside a milestone is a structural nudge back toward
            # the intake flow — NOT a failure. Names structure, never the act of intake.
            warnings.append((f"task '{slug}'", "is outside a milestone — size it via the /add "
                                               "intake flow (or attach with --milestone)"))
        # backlink-drift (task-milestone-backlink): the TASK.md `milestone:` header mirrors state.
        # WARN (never red, warn-never-block) when a PRESENT line disagrees; an ABSENT line is a
        # grandfathered task — silent, never retro-red. Degrade-safe: an unreadable file skips here.
        try:
            _task_text = (root / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")
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
            _arch = _archived_task_slugs(state)
            for _ptr in _seeded_delta_pointers(_task_text):
                if _ptr not in tasks and _ptr not in _arch:
                    warnings.append((f"task '{slug}'", f"seeded SPEC delta points at '{_ptr}' which no "
                                     "longer exists (dangling lineage) — re-point or drop the delta"))
        # rule-id-coverage: a §1 Must/Reject ID with no §2 scenario tag and no §4 `covers:`
        # reference is a coverage gap. WARN only, runs in ANY phase (a gap in already-shipped
        # work must still surface — the whole point of the check); opt-in per task via
        # `_rule_coverage_gaps`'s own tag-presence gate, so a task that never adopted the M#/
        # R:code convention is silently grandfathered — never retro-flagged.
        if _task_text is not None:
            _spans = _phase_spans(_task_text)
            for _rid, _kind in _rule_coverage_gaps(_spans.get(1, ""), _spans.get(2, ""), _spans.get(4, "")):
                warnings.append((f"task '{slug}'", f"rule '{_rid}' ({_kind}) has no §2 scenario tag "
                                 "and no §4 test covering it (coverage gap) — add a scenario tag "
                                 "or a covers: line"))
        # autonomy level (task explicit-autonomy-dial): a REAL out-of-set token is a hard
        # unknown_autonomy_level; a LIVE task (phase before done/observe) with no `autonomy:`
        # line is implicit_autonomy — a WARN, never red. Done/observe predecessors are SKIPPED
        # (a fresh live-only predicate, NOT the audit open-front skip) so the board never floods.
        _alvl = _autonomy_level(_task_header(root, slug))
        checks.append((_alvl != "?", f"task '{slug}' autonomy level recognized",
                       "unknown_autonomy_level (token outside manual|conservative|auto)"))
        if _alvl is None and t.get("phase") not in ("done", "observe"):
            warnings.append((f"task '{slug}'", "has no explicit autonomy level (implicit_autonomy) "
                             "— run `add.py autonomy set <level>` to set it"))
        # per-component-verify: a bound task whose component declares no green_bar can't be
        # gated on a bar — surface it (WARN, never red). Unbound / "?" -> silent.
        _tc = _task_component(root, slug)
        if _tc and _tc != "?" and not (_components(root).get(_tc) or {}).get("green_bar"):
            warnings.append((f"task '{slug}'", f"component_green_bar_unset — bound component '{_tc}' "
                             "declares no green_bar; the per-component gate cannot check a bar"))
        # cross-component-contract: a consumer whose pinned hash drifted from the live snapshot
        # (the producer re-froze a CHANGED shape) — the §7-stale cue. Degrade-safe (unreadable
        # snapshot ⇒ no finding here; the missing-snapshot HARD-STOP lives at the advance crossing).
        _pin = t.get("contract_pin")
        if _pin:
            try:
                _live = json.loads(_contract_snapshot(root, _pin["id"]).read_text(encoding="utf-8")).get("hash")
            except (OSError, ValueError, KeyError, TypeError, AttributeError):
                _live = None
            if _live is None:                # missing / corrupt / hash-less ⇒ SURFACE, never mask
                warnings.append((f"task '{slug}'", f"contract_snapshot_unreadable — pinned contract "
                                 f"'{_pin.get('id')}' snapshot is missing or corrupt; re-publish the "
                                 "producer contract (cannot confirm the pin is current)"))
            elif _live != _pin.get("hash"):
                warnings.append((f"task '{slug}'", f"contract_consumer_stale — pinned contract "
                                 f"'{_pin.get('id')}' changed shape since pin; re-pin (re-cross contract→tests) "
                                 "after reviewing the producer's new frozen shape"))
        # cross-component-recency: a consumer whose landed snapshot's LIVE producer drifted/unfroze
        # since the snapshot — surfaced EARLY (never red) before the consumer re-enters §3, the
        # check twin of the producer_contract_stale advance HARD-STOP. Degrade-safe.
        _ccons = _task_consumes(root, slug)
        if _ccons and _ccons in _contracts(root):
            _csnap = _contract_snapshot(root, _ccons)
            if _csnap.exists():
                try:
                    _chash = json.loads(_csnap.read_text(encoding="utf-8")).get("hash")
                except (OSError, ValueError, AttributeError):
                    _chash = None
                if _chash is None:
                    # cross-component-recency R1: a present-but-hash-less snapshot degrades the
                    # recency check to existence-only (frozen behavior) — SURFACE the blind spot
                    # (never red) so a hand-tampered/hash-stripped snapshot is not silently trusted.
                    warnings.append((f"task '{slug}'", f"contract_snapshot_hashless — the landed "
                                     f"snapshot for '{_ccons}' carries no hash; recency cannot be "
                                     "verified (re-publish the producer contract / re-cross contract→tests)"))
                elif _producer_snapshot_stale(root, _ccons, _chash):
                    warnings.append((f"task '{slug}'", f"contract_producer_stale — the live producer "
                                     f"of '{_ccons}' changed or re-opened its §3 since the landed "
                                     "snapshot; re-cross the producer contract→tests, then re-enter"))
        for dep in t.get("depends_on") or []:
            checks.append((dep in tasks or dep in archived_slugs,
                           f"task '{slug}' dep '{dep}' resolves", "unknown task"))
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

    # drift: a done milestone must have no unfinished tasks
    for mslug, m in milestones.items():
        if m.get("status") == "done":
            unfinished = [s for s, t in tasks.items()
                          if t.get("milestone") == mslug and not _task_done(t)]
            checks.append((not unfinished, f"done milestone '{mslug}' fully complete",
                           f"unfinished: {unfinished}"))

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

    # wave-ledger fork-base (engine-merge-base-enforcement): the engine EXECUTES the
    # streams.md rule — every roster echo must match `base:`. A FILLED mismatch is red at
    # ANY status; a pending row is red at `status: merging` (merge-time strictness) but only
    # a WARN at `status: live` (measure-not-block: step-0 echoes land mid-wave). An
    # unparseable ledger is fail-closed (`wave_ledger_malformed`) — never a silent skip.
    for _wp in _wave_ledgers(root):
        _wm = _wp.parent.name
        _w = _parse_wave_ledger(_wp)
        if _w.get("error"):
            checks.append((False, f"wave '{_wm}' ledger parses",
                           f"wave_ledger_malformed: {_w['error']}"))
            continue
        _bad = [r["task"] for r in _w["rows"] if r["filled"] and not r["matched"]]
        _pending = [r["task"] for r in _w["rows"] if not r["filled"]]
        if _w["status"] == "merging":
            _bad += _pending           # merge-time strictness: pending == unverified
            _pending = []
        checks.append((not _bad, f"wave '{_wm}' fork-base echoes match base",
                       "unverified_fork_base: " + ", ".join(_bad)))
        for _t in _pending:
            warnings.append(("fork_base_pending",
                             f"wave '{_wm}' roster row '{_t}' awaits its step-0 echo"))

    # dependency graph must be acyclic
    cycle = _find_cycle(tasks)
    checks.append((cycle is None, "task dependencies are acyclic",
                   f"cycle: {' -> '.join(cycle)}" if cycle else ""))

    # component registry (component-aware-add): a malformed .add/components.toml, a root
    # escaping the project, or a task binding an unregistered component are integrity FAILS
    # — fail-closed RED (like wave_ledger_malformed), loud but never a crash (the readers
    # themselves degrade-safe). Silent when there is no components.toml.
    for _ccode, _cdetail in _component_findings(root):
        checks.append((False, f"component registry ({_ccode})", _cdetail))
    # cross-component-contract: a [contract.<id>] naming an unregistered producer is an
    # integrity FAIL (same fail-closed RED discipline; the readers stay degrade-safe).
    for _ccode, _cdetail in _contract_findings(root):
        checks.append((False, f"contract registry ({_ccode})", _cdetail))
    # multirepo-federation: a declared [federation.<id>] whose producer-repo source is unreadable
    # is a BROKEN JOIN — surface it EARLY as a WARN (never red alone; `federate pull` is where it
    # HARD-STOPs). Silent when no federation is declared (opt-in / byte-identical).
    for _fid, _fspec in _federation(root).items():
        if not _federation_source_confined(root, _fspec["source"]):
            # federation-harden: an out-of-allowlist source surfaced EARLY as a never-red WARN
            # (escape takes precedence over unreadable — a real /etc/passwd passes is_file()).
            warnings.append((f"federation '{_fid}'",
                             f"federation_source_escapes — '{_fspec['source']}' resolves outside the "
                             f"sibling-repo allowlist; `federate pull {_fid}` will HARD-STOP"))
        elif not (root.parent / _fspec["source"]).is_file():
            warnings.append((f"federation '{_fid}'",
                             f"federation_source_unreadable — the producer snapshot at "
                             f"'{_fspec['source']}' is missing/unreadable; `federate pull {_fid}` "
                             "will hard-stop until the producer repo publishes it"))
    # components-validator: the schema-lint (typo'd/unknown key · wrong-type value · unknown
    # table) is a never-red WARN — measure-not-block, forward-compat-safe. Rides `warnings`,
    # NEVER `checks`/`failed`. Silent when no components.toml. `add.py components` is the
    # richer surface; this catches the same typos EARLY in CI without failing the build.
    for _scode, _sdetail in _component_schema_findings(root):
        warnings.append((_scode, _sdetail))

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
            if "agents/*.md" in (_project_root / _gname).read_text(encoding="utf-8"):
                _cites_roster = True
                break
        except OSError:
            pass
    if _cites_roster:
        _agents_dir = _project_root / ".claude" / "agents"
        if not (_agents_dir.is_dir() and any(_agents_dir.glob("add-*.md"))):
            warnings.append(("roster_uninstalled",
                             "guideline file(s) cite the agent roster but no `.claude/agents/"
                             "add-*.md` files are installed — run `add.py update` (or re-run the "
                             "CLI installer) to materialize them"))

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


def _doctor_findings(root: Path) -> list[str]:
    """Read-only diagnosis of state.json: each item is "<problem> — fix: <fix>".

    Reads the RAW text with its OWN try/except — NEVER through the dying load_state — so a
    conflicted/corrupt state is REPORTED, not aborted on (the proactive counterpart to the
    merge-guard load guard, which fails fast at the first problem). Reports the FIRST blocking
    class then stops (can't parse deeper): missing/unreadable file -> conflict markers -> bad
    JSON. On a PARSEABLE state (normalized through `_migrate_state` so the canonical multi-active
    shape is judged) it appends EVERY referential violation. PURE: reads only, returns the list."""
    try:
        text = (root / STATE_FILE).read_text(encoding="utf-8")
    except OSError:
        return ["state.json missing/unreadable — fix: restore it from git/backup"]
    if _CONFLICT_MARKER_RE.search(text):
        return ["state.json has unresolved git merge markers — fix: resolve "
                "<<<<<<< / ======= / >>>>>>> (or git checkout --ours/--theirs), then re-run doctor"]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return ["state.json is not valid JSON — fix: restore it from git/backup"]

    state = _migrate_state(parsed)
    findings: list[str] = []
    milestones = state.get("milestones") if isinstance(state.get("milestones"), dict) else {}
    tasks = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}

    active_ms = state.get("active_milestones") if isinstance(state.get("active_milestones"), list) else []
    active_tasks = state.get("active_tasks") if isinstance(state.get("active_tasks"), dict) else {}
    for am in active_ms:
        if am not in milestones:
            findings.append(f"active milestone '{am}' has no record — fix: deactivate it or "
                            "recreate the milestone")
    for ms, t in active_tasks.items():
        if not t:
            continue
        if t not in tasks:
            findings.append(f"active task '{t}' (milestone '{ms}') has no record — fix: use a "
                            "real task or clear the active pointer")
        elif (tasks[t].get("milestone") if isinstance(tasks[t], dict) else None) != ms:
            findings.append(f"active task '{t}' is mislabeled under '{ms}' — fix: re-use it "
                            "under its own milestone")
    for slug, t in tasks.items():
        m = t.get("milestone") if isinstance(t, dict) else None
        if m is not None and m not in milestones:
            findings.append(f"task '{slug}' references missing milestone '{m}' — fix: set its "
                            "milestone to a real one (or none)")
    # value-domain checks (doctor-value-checks): gate/phase enum (required) · owner/assignee
    # shape (optional) · archived consistency. Present-but-invalid + missing-required only;
    # absent owner/assignee is fine. Pure/total — .get-guarded, isinstance-checked, never raises.
    for slug, t in tasks.items():
        if not isinstance(t, dict):
            continue
        g = t.get("gate")
        if g is None:
            findings.append(f"task '{slug}' is missing its gate — fix: one of {', '.join(GATES)}")
        elif g not in GATES:
            findings.append(f"task '{slug}' has invalid gate '{g}' — fix: one of {', '.join(GATES)}")
        p = t.get("phase")
        if p is None:
            findings.append(f"task '{slug}' is missing its phase — fix: one of {', '.join(PHASES)}")
        elif p not in PHASES:
            findings.append(f"task '{slug}' has invalid phase '{p}' — fix: one of {', '.join(PHASES)}")
        for role in ("owner", "assignee"):
            v = t.get(role)
            if v is not None and not (isinstance(v, dict) and isinstance(v.get("name"), str) and v.get("name")):
                findings.append(f"task '{slug}' has a malformed {role} — fix: an actor object "
                                "{name, email, source} or remove it")
    archived = state.get("archived") if isinstance(state.get("archived"), list) else []
    for a in archived:
        if not isinstance(a, dict):
            continue
        aslug = a.get("slug")
        if aslug is not None and aslug in milestones:
            findings.append(f"archived milestone '{aslug}' is also a live milestone — fix: remove "
                            "the live duplicate or the archived entry")
        ts = a.get("task_slugs")
        if isinstance(ts, list) and isinstance(a.get("tasks"), int) and a.get("tasks") != len(ts):
            findings.append(f"archived milestone '{aslug}' task count {a.get('tasks')} ≠ {len(ts)} "
                            "listed — fix: reconcile its task_slugs")
    return findings


def cmd_doctor(args: argparse.Namespace) -> None:
    """Read-only `add.py doctor`: PASS + exit 0 on a healthy state, else report each problem +
    fix to stdout and exit non-zero. NEVER mutates state (detect, never auto-resolve)."""
    root = find_root()
    if root is None:
        _die("no_project")
    findings = _doctor_findings(root)
    if not findings:
        print("doctor: PASS — state.json is healthy (parseable · conflict-free · references intact)")
        return
    print(f"doctor: {len(findings)} problem(s):")
    for f in findings:
        print(f"  ✗ {f}")
    raise SystemExit(1)


def cmd_mine(args: argparse.Namespace) -> None:
    """Read-only `add.py mine`: the not-done tasks owned-by or assigned-to the resolved actor
    (`_whoami`, or `--actor "Name <email>"`). Default lens is the active SET; `--all` widens it
    to EVERY milestone plus loose (milestone-less) tasks. Text or `--json`. An empty queue is a
    plain exit-0 line, not an error. NEVER writes state."""
    root = find_root()
    if root is None:
        _die("no_project")
    state = load_state(root)
    me = identity._parse_actor_arg(args.actor) if getattr(args, "actor", None) else identity._whoami(state)
    scope_all = getattr(args, "all", False)
    rows = _my_work(state, me, scope_all=scope_all)
    if getattr(args, "json", False):
        print(json.dumps({"actor": me, "tasks": rows}))
        return
    scope = "all" if scope_all else "active"
    who = _fmt_actor(me) or me.get("name", "you")
    if not rows:
        print(f"mine: no open tasks for {who} across {scope} milestones")
        return
    print(f"mine: {who} — {len(rows)} open task(s) across {scope} milestones:")
    for r in rows:
        loc = f"[{r['milestone']}]" if r["milestone"] else "[loose]"
        print(f"  {r['slug']:<24} {loc}  phase={r['phase']}  ({r['role']})")


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


def _sha_match(a: str, b: str) -> bool:
    """Exact or prefix match, both tokens >=7 hex chars (git short-sha tolerant)."""
    if len(a) < 7 or len(b) < 7:
        return False
    return a == b or a.startswith(b) or b.startswith(a)


def _wave_ledgers(root: Path) -> list:
    """Every live wave ledger, stable order (the same glob as the status hint)."""
    return sorted(p for p in (root / "milestones").glob("*/WAVE.md") if p.is_file())


def _parse_wave_ledger(path: Path) -> dict:
    """Parse a WAVE.md against the streams.md template grammar. Fail-closed: a dict
    with an "error" key names exactly the piece that did not parse."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return {"error": f"unreadable ({e.__class__.__name__})"}
    # status is read ONLY from the FIRST `wave:` line — the header. Body text must
    # never rescue a malformed/invalid header: not free prose (heal-1 FG-2, an
    # unanchored search) and not a later wave:-prefixed line either (heal-2 FG-3 —
    # `(?m)^wave:.*?status:` happily skipped a status-less header to a body line).
    m_header = re.search(r"(?m)^wave:.*$", text)
    if not m_header:
        return {"error": "no 'wave:' header line"}
    # the status value is the EXACT token after `status:`, terminated only by
    # whitespace, the `·` separator, or end-of-line (v3): `\b` is not a token
    # terminator on hand-written input — it fires at `|` and `-`, so the unfilled
    # template placeholder `live|merging` (and drift like `live-ish`) parsed as
    # its valid prefix and greened an unfilled ledger (5th refute pass). The
    # `status:` label must itself START a field — start-of-line, whitespace, or
    # `·` before it (v4): an embedded `substatus:` is not a status field
    # (6th refute pass, N12).
    m_status = re.search(r"(?:^|[\s·])status:[ \t]*([^\s·]*)", m_header.group(0))
    if not m_status:
        return {"error": "no 'status: live|merging' on the wave: header line"}
    if m_status.group(1) not in ("live", "merging"):
        return {"error": "status token "
                f"{m_status.group(1)!r} is not exactly live or merging"}
    # base is read ONLY from the FIRST `base:` line, token on THAT line (heal-3 Pex:
    # `(?m)^base:\s*(\S+)` let \s cross the newline, so an EMPTY base: line parsed
    # as filled with whatever token the next line started with).
    m_base_line = re.search(r"(?m)^base:.*$", text)
    base = ""
    if m_base_line:
        m_tok = re.search(r"base:[ \t]*(\S+)", m_base_line.group(0))
        base = m_tok.group(1) if m_tok else ""
    if not re.fullmatch(r"[0-9a-f]{7,40}", base):
        return {"error": "no parseable 'base:' sha (7-40 hex)"}
    rows, in_roster, echo_col = [], False, None
    for line in text.splitlines():
        if line.startswith("### "):
            in_roster = line.lower().startswith("### roster")
            echo_col = None
            continue
        if not in_roster or not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if echo_col is None:
            # the column-header row MUST name the fork-base column, and the echo is
            # read from WHEREVER that label sits (heal-3: a hardcoded cells[2] let an
            # extra leading column hide the echo, and a headerless roster silently
            # swallowed its first DATA row as the header — a silent skip, refused).
            # EXACTLY one label may match (v2 ambiguity refusal): first-wins on a
            # hand-written artifact is fail-open — a second matching label such as
            # "fork-base-prev" would steal the echo and green a mismatched roster
            # (4th refute pass, N1/N10).
            matches = [i for i, c in enumerate(cells) if "fork-base" in c.lower()]
            if not matches:
                return {"error": "roster column-header row names no 'fork-base' column"}
            if len(matches) > 1:
                labels = ", ".join(cells[i] for i in matches)
                return {"error": f"ambiguous fork-base columns: {labels}"}
            echo_col = matches[0]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue                            # the |---| separator row
        if len(cells) <= echo_col:
            return {"error": f"roster row with no fork-base cell: {line.strip()!r}"}
        shas = _WAVE_SHA_RE.findall(cells[echo_col])
        # fail-closed cell semantics (heal-1 FG-1): the cell must BE the pasted echo,
        # so EVERY sha token in it must match base — `any()` would green a drift note
        # ("<alien-sha> synced-to <base-prefix>") that documents the very mismatch
        # this gate exists to refuse. One alien token -> the row is NOT verified.
        rows.append({"task": cells[0], "filled": bool(shas),
                     "matched": bool(shas) and all(_sha_match(s, base) for s in shas)})
    if not rows:
        return {"error": "no roster row"}
    return {"status": m_status.group(1), "base": base, "rows": rows}


def cmd_wave_verify(args: argparse.Namespace) -> None:
    """The explicit merge-time gate: strict at any status, read-only, judgment-free.
    Exit 0 only when EVERY roster echo matches `base:` — run before the first
    merge-back. Never mutates the ledger, its status field, or state.json."""
    root = _require_root()
    if args.milestone:
        target = root / "milestones" / args.milestone / "WAVE.md"
        if not target.is_file():
            _die(f"wave_not_found: no WAVE.md for milestone '{args.milestone}'")
    else:
        ledgers = _wave_ledgers(root)
        if not ledgers:
            _die("wave_not_found: no WAVE.md under .add/milestones/ — nothing to verify")
        if len(ledgers) > 1:
            _die("wave_ambiguous: " + ", ".join(p.parent.name for p in ledgers)
                 + " — name one: add.py wave-verify <milestone>")
        target = ledgers[0]
    w = _parse_wave_ledger(target)
    if w.get("error"):
        _die(f"wave_ledger_malformed: {w['error']} ({target.parent.name}/WAVE.md)")
    bad = []
    for r in w["rows"]:
        verdict = "ok" if r["matched"] else ("MISMATCH" if r["filled"] else "PENDING")
        print(f"  {r['task']}: {verdict}")
        if not r["matched"]:
            bad.append(r["task"])
    if bad:
        _die("unverified_fork_base: " + ", ".join(bad)
             + f" — every roster echo must match base {w['base'][:12]} before merge-back")
    print(f"wave '{target.parent.name}' verified — every fork-base echo matches base "
          f"{w['base'][:12]}; merge-back may proceed (the ledger is untouched).")


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
    print(_next_footer(root, state))   # converges the old "Decompose it into tasks: …" hint


def cmd_milestone_confirm(args: argparse.Namespace) -> None:
    """The human gate that opens new-task for a milestone (confirm-parent). Mirrors `cmd_lock`
    one level down: the human reviews the filled MILESTONE.md, then RECORDS confirmation here.
    The engine never self-confirms. Validate-then-write; re-confirm is an idempotent note."""
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    if slug not in state.get("milestones", {}):
        _die("unknown_milestone")
    m = state["milestones"][slug]
    if m.get("confirmed") is True:
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
        if _section_unfilled(md, "## Shared / risky contracts"):
            _die("milestone_contracts_unfilled: fill the '## Shared / risky contracts' "
                 f"section of {slug}'s MILESTONE.md before confirming")
    who = getattr(args, "by", None) or getpass.getuser()
    m["confirmed"] = True
    m["confirmed_at"] = _now()
    m["confirmed_by"] = who
    m["actor"] = identity._actor_stamp(state)   # structured actor alongside the free-text confirmed_by
    m["updated"] = _now()
    save_state(root, state)
    print(f"confirmed milestone '{slug}' (by {who}) — new-task is now open for it.")
    print(_next_footer(root, state))


def cmd_ready(args: argparse.Namespace) -> None:
    if getattr(args, "json", False):
        _, state = _load_state_for_json()
        tasks = state.get("tasks") or {}
        archived = _archived_task_slugs(state)

        def _ok(d: str) -> bool:
            return d in archived or (d in tasks and _task_done(tasks[d]))

        ready, blocked = [], []
        for slug, t in tasks.items():
            if _task_done(t):
                continue
            unmet = [d for d in (t.get("depends_on") or []) if not _ok(d)]
            (blocked.append({"slug": slug, "waiting_on": unmet})
             if unmet else ready.append(slug))
        print(json.dumps({"ready": ready, "blocked": blocked}))
        return
    root = _require_root()
    state = load_state(root)
    tasks = state.get("tasks", {})
    archived_slugs = _archived_task_slugs(state)   # an archived dep was PASS-done

    def _dep_satisfied(d: str) -> bool:
        if d in archived_slugs:
            return True                            # archived ⇒ complete when archived
        return d in tasks and _task_done(tasks[d]) # in-state dep must be done; else blocked

    ready = []
    for slug, t in tasks.items():
        if _task_done(t):
            continue
        deps = t.get("depends_on") or []
        if all(_dep_satisfied(d) for d in deps):
            ready.append(slug)
    if not ready:
        print("ready: (none — all tasks are done or blocked)")
        return
    print("ready to start (deps satisfied):")
    for slug in ready:
        deps = tasks[slug].get("depends_on") or []
        suffix = f"  (after {', '.join(deps)})" if deps else ""
        # cross-active legibility (cross-active-waves): name the stream each ready task belongs
        # to, present-only — a milestone-less task gets no bracket (byte-identical).
        _ms = tasks[slug].get("milestone")
        ms_frag = f"  [{_ms}]" if _ms else ""
        print(f"  {slug}{ms_frag}{suffix}")


def _wave_schedule(state: dict, mslug: str) -> dict:
    """One-element wrapper: a single milestone's schedule is the merge over just [mslug].
    Output is byte-identical to the historical per-milestone scheduler (the suite is the oracle)."""
    return _wave_schedule_merged(state, [mslug])


def _wave_schedule_merged(state: dict, mslugs: list[str]) -> dict:
    """Pure, total: derive ONE DAG schedule over the UNION of open members across `mslugs`
    (a single-element list is the historical per-milestone case) — never mutates, never raises
    on dict input. Returns one of:
      {"cycle": [slug, ...]}                                       — unschedulable cycle
      {"waves", "critical_path", "critical_path_len", "tiers", "blocked"}  — a schedule

    A dep is SATISFIED (does not block) if it is archived or `_task_done` — the SAME
    predicate cmd_ready uses. A not-done dep that is an OPEN MEMBER of ANY target milestone
    forces a later wave (so a cross-milestone dep ORDERS, it does not block). A not-done dep
    that is NOT an open member of any target (external/unknown) is UNSATISFIABLE here -> the
    task is `blocked`, never scheduled. Critical path is the longest chain (most tasks) through
    the scheduled sub-DAG; ties break by sorted slug. Tier is advisory: `top` on the critical
    path, `mid` elsewhere (scheduled tasks only)."""
    tasks = state.get("tasks") or {}
    archived = _archived_task_slugs(state)
    targetset = set(mslugs)

    def _ok(d: str) -> bool:                       # satisfied externally / already done
        return d in archived or (d in tasks and _task_done(tasks[d]))

    open_members = {s: t for s, t in tasks.items()
                    if t.get("milestone") in targetset and not _task_done(t)}

    # partition open members into blocked vs schedulable — to a FIXED POINT, so blocking
    # propagates transitively: a task is blocked if any dep is unsatisfiable here, where
    # unsatisfiable = not _ok AND not a STILL-schedulable member. A dep on an already-blocked
    # member is itself unsatisfiable, so the dependent blocks too (it would otherwise be
    # mis-reported as wave-1-ready while its only dep can never complete).
    blocked: dict[str, list[str]] = {}
    changed = True
    while changed:
        changed = False
        for s, t in open_members.items():
            if s in blocked:
                continue
            bad = [d for d in (t.get("depends_on") or [])
                   if not _ok(d) and not (d in open_members and d not in blocked)]
            if bad:
                blocked[s] = sorted(set(bad))
                changed = True
    schedulable = {s for s in open_members if s not in blocked}
    blocked_sorted = {k: blocked[k] for k in sorted(blocked)}
    if not schedulable:
        # nothing to schedule (all-done, empty, or every open task externally blocked)
        return {"waves": [], "critical_path": [], "critical_path_len": 0,
                "tiers": {}, "blocked": blocked_sorted}

    def _member_deps(s: str) -> set[str]:          # deps that are open members forcing order
        return {d for d in (open_members[s].get("depends_on") or []) if d in schedulable}

    # Kahn waves over the schedulable sub-DAG
    waves: list[list[str]] = []
    placed: set[str] = set()
    remaining = set(schedulable)
    while remaining:
        wave = sorted(s for s in remaining if _member_deps(s) <= placed)
        if not wave:                               # no progress => a cycle among the remaining
            sub = {s: tasks[s] for s in remaining}
            cyc = _find_cycle(sub) or sorted(remaining)
            return {"cycle": cyc}
        waves.append(wave)
        placed.update(wave)
        remaining -= set(wave)

    # critical path = longest chain by memoized depth over member-deps
    depth: dict[str, int] = {}
    pick: dict[str, str | None] = {}

    def _depth(s: str) -> int:
        if s in depth:
            return depth[s]
        best_d, best_dep = 0, None
        for d in sorted(_member_deps(s)):
            dd = _depth(d)
            if dd > best_d or (dd == best_d and (best_dep is None or d < best_dep)):
                best_d, best_dep = dd, d
        depth[s] = 1 + best_d
        pick[s] = best_dep
        return depth[s]

    leaf = min(schedulable, key=lambda s: (-_depth(s), s))  # deepest, tie -> smallest slug
    chain: list[str] = []
    cur: str | None = leaf
    while cur is not None:
        chain.append(cur)
        cur = pick.get(cur)
    critical = list(reversed(chain))               # root -> leaf order
    crit_set = set(critical)
    tiers = {s: ("top" if s in crit_set else "mid") for s in sorted(schedulable)}
    return {"waves": waves, "critical_path": critical, "critical_path_len": len(critical),
            "tiers": tiers, "blocked": blocked_sorted}


def _wave_block_lines(state: dict, mslug: str, sched: dict) -> list[str]:
    """The exact text lines `waves` renders for ONE milestone's schedule (cross-active-waves
    extracts this so a single target stays byte-identical and N targets each get a block)."""
    lines = [f"milestone: {mslug}"]
    if not sched["waves"]:
        if sched["blocked"]:
            for s in sched["blocked"]:
                lines.append(f"blocked: {s} (waiting on {', '.join(sched['blocked'][s])})")
        else:
            lines.append("all tasks done — nothing to schedule")
        return lines
    scheduled_set = {x for w in sched["waves"] for x in w}
    for i, wave in enumerate(sched["waves"], start=1):
        parts = []
        for s in wave:
            md = sorted(d for d in (state["tasks"][s].get("depends_on") or [])
                        if d in scheduled_set)
            parts.append(f"{s} (deps: {', '.join(md)})" if md else s)
        lines.append(f"wave {i}: {', '.join(parts)}")
    crit = sched["critical_path"]
    lines.append(f"critical path: {' → '.join(crit)}  ({sched['critical_path_len']} tasks)")
    tops = [s for s, tier in sched["tiers"].items() if tier == "top"]
    mids = [s for s, tier in sched["tiers"].items() if tier == "mid"]
    lines.append(f"tier hint: top → {', '.join(tops)}; mid → {', '.join(mids) or '(none)'}")
    for s in sched["blocked"]:
        lines.append(f"blocked: {s} (waiting on {', '.join(sched['blocked'][s])})")
    return lines


def _wave_block_lines_merged(state: dict, mslugs: list[str], sched: dict) -> list[str]:
    """The text lines `waves --merge` renders for ONE unified schedule over the milestone SET:
    a `merged: …` header naming the set + each scheduled task tagged with its `[milestone]` so
    cross-milestone tasks are unambiguous. Critical-path / tier-hint / blocked lines mirror
    `_wave_block_lines`."""
    n = len(mslugs)
    lines = [f"merged: {' + '.join(mslugs)} ({n} milestone{'s' if n != 1 else ''})"]
    if not sched["waves"]:
        if sched["blocked"]:
            for s in sched["blocked"]:
                lines.append(f"blocked: {s} (waiting on {', '.join(sched['blocked'][s])})")
        else:
            lines.append("all tasks done — nothing to schedule")
        return lines
    scheduled_set = {x for w in sched["waves"] for x in w}
    for i, wave in enumerate(sched["waves"], start=1):
        parts = []
        for s in wave:
            label = f"{s} [{state['tasks'][s].get('milestone')}]"
            md = sorted(d for d in (state["tasks"][s].get("depends_on") or [])
                        if d in scheduled_set)
            parts.append(f"{label} (deps: {', '.join(md)})" if md else label)
        lines.append(f"wave {i}: {', '.join(parts)}")
    crit = sched["critical_path"]
    lines.append(f"critical path: {' → '.join(crit)}  ({sched['critical_path_len']} tasks)")
    tops = [s for s, tier in sched["tiers"].items() if tier == "top"]
    mids = [s for s, tier in sched["tiers"].items() if tier == "mid"]
    lines.append(f"tier hint: top → {', '.join(tops)}; mid → {', '.join(mids) or '(none)'}")
    for s in sched["blocked"]:
        lines.append(f"blocked: {s} (waiting on {', '.join(sched['blocked'][s])})")
    return lines


def cmd_waves(args: argparse.Namespace) -> None:
    """READ-ONLY DAG scheduler: print the topological waves, critical path, advisory tier hint,
    and blocked set. With no --milestone it spans EVERY active milestone (cross-active-waves)
    as SEPARATE streams; a single target / --milestone renders byte-identically. With --merge it
    unifies the active SET into ONE schedule so cross-milestone deps order, not block.
    Writes nothing; no `next:` footer."""
    is_json = getattr(args, "json", False)
    if is_json:
        _, state = _load_state_for_json()
    else:
        state = load_state(_require_root())
    mslug_arg = getattr(args, "milestone", None)
    if getattr(args, "merge", False):
        if mslug_arg:                                  # explicit target → a 1-milestone merge (NOT a conflict)
            if mslug_arg not in (state.get("milestones") or {}):
                _die(f"unknown_milestone: '{mslug_arg}' is not a milestone in this project")
            targets = [mslug_arg]
        else:
            primary = _active_milestone(state)
            if not primary:
                _die("no_active_milestone: no active milestone and no --milestone given")
            targets = [primary] + [m for m in (state.get("active_milestones") or [])
                                   if m != primary]
        sched = _wave_schedule_merged(state, targets)
        if "cycle" in sched:
            _die(f"dependency_cycle: not-done deps form a cycle "
                 f"({' -> '.join(sched['cycle'])}) — no valid schedule")
        if is_json:
            print(json.dumps({"merged": targets, **sched}))
        else:
            print("\n".join(_wave_block_lines_merged(state, targets, sched)))
        return
    if mslug_arg:
        targets = [mslug_arg]                          # explicit single target — unchanged
    else:
        primary = _active_milestone(state)             # the SCALAR is the gate (test relies on it)
        if not primary:
            _die("no_active_milestone: no active milestone and no --milestone given")
        # additively widen to the other active milestones (cross-active); primary first
        targets = [primary] + [m for m in (state.get("active_milestones") or [])
                               if m != primary]
    scheds = []
    for t in targets:
        if t not in (state.get("milestones") or {}):
            _die(f"unknown_milestone: '{t}' is not a milestone in this project")
        sched = _wave_schedule(state, t)
        if "cycle" in sched:
            _die(f"dependency_cycle: not-done deps form a cycle "
                 f"({' -> '.join(sched['cycle'])}) — no valid schedule")
        scheds.append(sched)

    if is_json:
        if len(targets) == 1:
            print(json.dumps({"milestone": targets[0], **scheds[0]}))   # unchanged shape
        else:
            print(json.dumps({"streams": [{"milestone": t, **s}
                                          for t, s in zip(targets, scheds)]}))
        return

    if len(targets) == 1:
        print("\n".join(_wave_block_lines(state, targets[0], scheds[0])))   # byte-identical
        return
    print(f"active streams: {len(targets)}")
    for i, (t, s) in enumerate(zip(targets, scheds)):
        if i:
            print()
        print("\n".join(_wave_block_lines(state, t, s)))


# --- persisted DAG-plan snapshot (persist-dag-plan) --------------------------------
# `waves` recomputes the schedule live and is the authority; `dag-plan` MATERIALIZES that
# computed schedule into a committed, auditable per-milestone snapshot + a freshness check
# against the live edges. The snapshot is NEVER the authority — only a checkable projection.
def _dag_plan_path(root: Path, mslug: str) -> Path:
    return root / "milestones" / mslug / "dag-plan.json"


def _edges_fingerprint(state: dict, mslug: str) -> str:
    """md5 over the EDGE STRUCTURE: every member's (done OR open) sorted depends_on. PURE.
    Invariant under a task COMPLETING (phase/gate change, not edges) — so completion is NOT
    drift — and changes only when a dep is added/removed/redirected or a member added/removed."""
    tasks = state.get("tasks") or {}
    edges = {s: sorted(t.get("depends_on") or [])
             for s, t in tasks.items() if t.get("milestone") == mslug}
    return _md5_text(json.dumps(edges, sort_keys=True))


def _dag_plan_freshness(root: Path, state: dict, mslug: str) -> tuple[str, dict | None]:
    """Read the snapshot and compare its stored fingerprint to the live one. Fail-safe:
    absent -> ("none", None) · unreadable/garbled -> ("unreadable", None) · match -> "fresh"
    · mismatch -> "stale". Never raises on a missing/corrupt file (no traceback to the user)."""
    sp = _dag_plan_path(root, mslug)
    if not sp.exists():
        return ("none", None)
    try:
        snap = json.loads(sp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ("unreadable", None)
    if not isinstance(snap, dict) or "edges_fingerprint" not in snap:
        return ("unreadable", None)
    live = _edges_fingerprint(state, mslug)
    return (("fresh" if snap.get("edges_fingerprint") == live else "stale"), snap)


def _dag_plan_status_line(root: Path, state: dict, mslug: str) -> str:
    """The single `dag-plan:` line cmd_status prints for the active milestone."""
    fresh, snap = _dag_plan_freshness(root, state, mslug)
    if fresh == "fresh":
        return "dag-plan: fresh ✓"
    if fresh == "stale":
        return f"dag-plan: stale (edges changed since {(snap or {}).get('generated', '?')})"
    if fresh == "unreadable":
        return "dag-plan: unreadable — run add.py dag-plan"
    return "dag-plan: none — run add.py dag-plan"


def cmd_dag_plan(args: argparse.Namespace) -> None:
    """RECORD-ONLY: materialize the active (or --milestone) milestone's computed DAG schedule
    into a committed snapshot + an edge fingerprint. Reuses cmd_waves' rejects; writes NOTHING
    on any reject. Idempotent: an unchanged fingerprint leaves the file byte-identical."""
    root = _require_root()
    state = load_state(root)
    mslug = getattr(args, "milestone", None) or _active_milestone(state)
    if not mslug:
        _die("no_active_milestone: no active milestone and no --milestone given")
    if mslug not in (state.get("milestones") or {}):
        _die(f"unknown_milestone: '{mslug}' is not a milestone in this project")
    sched = _wave_schedule(state, mslug)
    if "cycle" in sched:
        _die(f"dependency_cycle: not-done deps form a cycle "
             f"({' -> '.join(sched['cycle'])}) — no valid schedule")
    live_fp = _edges_fingerprint(state, mslug)
    sp = _dag_plan_path(root, mslug)
    # idempotent: an unchanged fingerprint leaves the snapshot (and its `generated` date) untouched
    if sp.exists():
        try:
            cur = json.loads(sp.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cur = None
        if isinstance(cur, dict) and cur.get("edges_fingerprint") == live_fp:
            print(f"dag-plan: {mslug} already fresh ✓ (generated {cur.get('generated', '?')})")
            return
    snap = {"milestone": mslug, "generated": date.today().isoformat(),
            "edges_fingerprint": live_fp, "schedule": sched}
    sp.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(sp, json.dumps(snap, indent=2, sort_keys=True) + "\n")
    nwaves = len(sched.get("waves") or [])
    ntasks = sum(len(w) for w in (sched.get("waves") or []))
    print(f"dag-plan: wrote {mslug} — {nwaves} wave(s), {ntasks} task(s) (fresh ✓)")


def cmd_milestone_done(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    if slug not in state.get("milestones", {}):
        _die("unknown_milestone")
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
    # fold-pressure nudge: milestone close is the natural fold point for open deltas (v11)
    by_comp = _collect_open_deltas(root)
    open_deltas = sum(len(v) for v in by_comp.values())
    if open_deltas:
        noun = "delta" if open_deltas == 1 else "deltas"
        print(f"note: {open_deltas} open {noun} ready to {_FOLD_VERB} into the foundation:")
        for comp in _COMPETENCY_ORDER:
            for e in by_comp[comp]:
                print(f"    ({comp}) {e['text']}  [{e['task']}]")
        print(f"  run: add.py {_FOLD_VERB}   (review first: add.py deltas)")
    # SPEC-delta nudge (project-wide): the close is also a natural prompt to RESOLVE the
    # forward hand-offs (seed/drop) so none is orphaned at the eventual compaction.
    open_spec = len(_collect_open_spec_deltas(root))
    if open_spec:
        noun = "delta" if open_spec == 1 else "deltas"
        print(f"note: {open_spec} open SPEC {noun} to resolve (seed/drop) — review: add.py deltas")
    # the engine-sourced next step (converges the old "Confirm … archive/start the next" hint)
    print(_next_footer(root, state))


def cmd_archive_milestone(args: argparse.Namespace) -> None:
    """Light archive: collapse a DONE milestone out of active state (files stay)."""
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    # validate before any mutation — a reject must leave state.json byte-for-byte unchanged
    if slug not in state.get("milestones", {}):
        _die("unknown_milestone")
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


def cmd_compact(args: argparse.Namespace) -> None:
    """Heavy archive (step two, after `archive-milestone`): move a light-archived
    milestone's files — MILESTONE.md + siblings + every rollup-member task dir — into
    one recovery bundle `.add/archive/<slug>/`. Validate-all-then-move: any reject
    leaves the tree AND state.json byte-for-byte unchanged. Compact never deletes,
    only renames; recovery = reverse move, no state edit (state already dropped these
    at light archive). Preserves the _archived_task_slugs invariant: `task_slugs` is
    never touched — archived ⇒ was PASS-done keeps resolving cross-milestone deps."""
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    # validate before any mutation — a reject must leave tree + state byte-for-byte unchanged
    if slug in state.get("milestones", {}):
        _die(f"milestone_not_archived: '{slug}' is still active — "
             f"run `add.py archive-milestone {slug}` first (light archive is step one)")
    entry = next((e for e in state.get("archived", []) if e.get("slug") == slug), None)
    if entry is None:
        _die("unknown_milestone")
    if entry.get("compacted"):
        _die(f"already_compacted: '{slug}' was compacted {entry['compacted']} — "
             f"see .add/archive/{slug}/")
    dest = root / "archive" / slug
    if dest.exists():
        _die(f"archive_destination_exists: .add/archive/{slug}/ exists without a "
             "compacted stamp — resolve the collision by hand before compacting")
    ms_dir = root / "milestones" / slug
    members = list(entry.get("task_slugs") or [])
    missing = [str(p.relative_to(root)) for p in
               [ms_dir, *(root / "tasks" / t for t in members)] if not p.is_dir()]
    if missing:
        _die("source_files_missing: " + " · ".join(missing))
    # deltas folded first: an `open` lesson inside the bundle would silently vanish
    # from `add.py deltas` (_collect_open_deltas globs tasks/*/TASK.md) once moved.
    member_set = set(members)
    offenders = sorted({e["task"] for v in _collect_open_deltas(root).values()
                        for e in v if e["task"] in member_set})
    if offenders:
        _die("open_deltas_unfolded: consolidate the open lessons first (`add.py deltas`) — "
             "open in: " + " · ".join(offenders))
    # SPEC-delta guard (PROJECT-WIDE, by the §3 freeze decision): a SPEC delta is a forward
    # hand-off that resolves into a task, not a foundation lesson — an open one ANYWHERE would
    # be orphaned at the next compaction. Deliberately broader than the member-scoped competency
    # guard above. Still validate-before-move: refuses BEFORE the first rename.
    # --force overrides THIS guard ONLY (never a structural reject above) — the escape hatch
    # for a settled milestone blocked by an unrelated open SPEC delta elsewhere. Bypass is
    # loud (warns + records `force_bypassed_spec_deltas`), never silent.
    forced = getattr(args, "force", False)
    spec_offenders = sorted({d["task"] for d in _collect_open_spec_deltas(root)})
    if spec_offenders and not forced:
        _die("open_spec_deltas_unresolved: resolve every open SPEC delta first "
             "(`add.py deltas`; seed with `new-task --from-delta`, or `drop-delta`; "
             "or re-run with --force to compact past them) — "
             "open in: " + " · ".join(spec_offenders))
    # every precondition passed — move (same-filesystem renames, never a delete)
    def _files(d: Path) -> int:
        return sum(1 for f in d.rglob("*") if f.is_file())
    moved: list[tuple[str, int]] = []
    (root / "archive").mkdir(exist_ok=True)
    n = _files(ms_dir)
    ms_dir.rename(dest)                       # the milestone dir becomes the bundle root
    moved.append((f"milestones/{slug}/", n))
    (dest / "tasks").mkdir(exist_ok=True)
    for t in members:
        src = root / "tasks" / t
        n = _files(src)
        src.rename(dest / "tasks" / t)
        moved.append((f"tasks/{t}/", n))
    # state write is the LAST step: additive stamp only — task_slugs untouched
    entry["compacted"] = date.today().isoformat()
    if spec_offenders:                       # forced is implied (un-forced would have _die'd)
        entry["force_bypassed_spec_deltas"] = spec_offenders
    save_state(root, state)
    if spec_offenders:
        print("⚠ --force bypassed open SPEC delta(s) in: " + " · ".join(spec_offenders) +
              " — recorded as force_bypassed_spec_deltas; resolve them before the next release.")
    total = sum(n for _, n in moved)
    print(f"compacted milestone '{slug}' -> .add/archive/{slug}/ "
          f"({len(members)} task dirs, {total} files moved)")
    for path, n in moved:
        print(f"  moved {path} ({n} files)")
    print("recovery: reverse the moves (mv the bundle's parts back) — state needs no edit.")
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
    # keep the TASK.md `milestone:` backlink in lockstep with state (task-milestone-backlink):
    # rewrite the header line (insert it if a grandfathered file lacks it). Degrade-safe — a
    # missing/unreadable TASK.md never blocks the move (state is already the source of truth).
    task_md = root / "tasks" / task / "TASK.md"
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
    slug = args.slug
    if slug not in state.get("milestones", {}):
        _die("unknown_milestone")
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
    """Keep the `phase:` line inside TASK.md in sync with state.json."""
    task_md = root / "tasks" / slug / "TASK.md"
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
# state.json; prose (observe delta, deltas) is parsed from each TASK.md and
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


def _graduation_ready(root: Path, state: dict) -> tuple[bool, int, int]:
    """(ready, met, total) for the stage-graduation cue (v22): every milestone done AND the
    human's stage-goal-criteria all checked (total>0 and met==total). The SINGLE source the
    text and --json status branches share, so the cue and the json signal can never disagree."""
    met, total = _stage_criteria(root)
    ready = _all_milestones_done(state) and total > 0 and met == total
    return ready, met, total


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
                       ".next", "coverage", "test-results")
_SCOPE_EXCLUDE_FILES = (".DS_Store",)                  # plus *.pyc / *.tsbuildinfo by suffix
_SCOPE_EXCLUDE_SUFFIXES = (".pyc", ".tsbuildinfo")


# ── component registry (component-aware-add): declared components + task binding ─────
# OPT-IN + DEGRADE-SAFE: with no .add/components.toml every reader is byte-identical to
# pre-component ADD. A read NEVER raises (absent/unreadable/malformed → {} / dropped
# cover); the loud surface is _component_findings, consumed by the scope gate (cmd_check).
def _component_root(root: Path, name: str) -> str | None:
    """Project-root-relative path (trailing '/') of component `name`'s root, or None
    when the name is absent OR the root escapes the project (fail-closed — grants no
    scope cover, mirroring _declared_scope's _confined drop). PURE."""
    spec = _components(root).get(name)
    if not spec:
        return None
    rootp = root.parent.resolve()
    p = root.parent / spec["root"]
    if not _confined(p, rootp):
        return None
    try:
        return str(p.resolve().relative_to(rootp)).rstrip("/") + "/"
    except (OSError, ValueError):
        return None


def _task_component(root: Path, slug: str):
    """The component a task binds to via its `component:` header token (anchored like
    autonomy). None = no line / unfilled `<…>` placeholder; "?" = a real token absent
    from the registry; otherwise the component name. PURE."""
    m = _COMPONENT_LINE_RE.search(_task_header(root, slug))
    if not m:
        return None
    tok = m.group(1).strip()
    return tok if tok in _components(root) else "?"


def _task_green_bar(root: Path, slug: str) -> str | None:
    """The green_bar phrase of the task's bound component (per-component-verify), else
    None — unbound, "?", or no green_bar declared all yield None. PURE."""
    comp = _task_component(root, slug)
    if not comp or comp == "?":
        return None
    return (_components(root).get(comp) or {}).get("green_bar") or None


def _task_verify(root: Path, slug: str) -> str | None:
    """The `verify` COMMAND of the task's bound component (component-registry-fill) — the literal
    suite the operator runs at the gate. Twin of _task_green_bar: unbound / "?" / no verify
    declared all yield None. PURE. SURFACED as data only — the engine NEVER executes it (NO-EXEC)."""
    comp = _task_component(root, slug)
    if not comp or comp == "?":
        return None
    return (_components(root).get(comp) or {}).get("verify") or None


def _component_findings(root: Path) -> list[tuple[str, str]]:
    """The loud gate surface for the registry — the codes a degrade-safe read passes
    over silently. Consumed by cmd_check (the scope_violation surface). [] when clean."""
    findings: list[tuple[str, str]] = []
    try:
        raw = (root / "components.toml").read_bytes()
    except OSError:
        return findings                       # absent/unreadable = opt-out, nothing to report
    data = None
    if tomllib is None:
        findings.append(("components_malformed", "components.toml present but tomllib unavailable (Python < 3.11)"))
    else:
        try:
            data = tomllib.loads(raw.decode("utf-8"))
        except (tomllib.TOMLDecodeError, UnicodeDecodeError, ValueError) as e:
            findings.append(("components_malformed", f"components.toml: {e}"))
    if data is not None:
        rootp = root.parent.resolve()
        for name, spec in (data.get("component") or {}).items():
            if name == "?":
                findings.append(("components_malformed", "component name '?' is reserved (the unknown-binding sentinel)"))
                continue
            if not isinstance(spec, dict) or not isinstance(spec.get("root"), str):
                findings.append(("components_malformed", f"[component.{name}] missing required `root`"))
                continue
            if not _confined(root.parent / spec["root"], rootp):
                findings.append(("component_root_outside", f"[component.{name}] root {spec['root']!r} escapes the project"))
    known = set(_components(root))
    try:
        task_dirs = sorted(p for p in (root / "tasks").iterdir() if p.is_dir())
    except OSError:
        task_dirs = []                       # unreadable tasks/ degrades safe — never crash a read
    for d in task_dirs:
        tc = _task_component(root, d.name)
        if tc is not None and tc not in known:      # "?" or a stale name
            findings.append(("component_unknown", f"task {d.name} binds an unregistered component"))
    return findings


# ── cross-component contracts (cross-component-contract) ──────────────────────────────────
# OPT-IN + DEGRADE-SAFE, like the component readers: no [contract.*] / no produces|consumes
# header ⇒ every path below is byte-identical to pre-contract ADD. A read NEVER raises.
def _task_produces(root: Path, slug: str) -> str | None:
    m = _PRODUCES_LINE_RE.search(_task_header(root, slug))
    return m.group(1).strip() if m else None


def _task_consumes(root: Path, slug: str) -> str | None:
    m = _CONSUMES_LINE_RE.search(_task_header(root, slug))
    return m.group(1).strip() if m else None


def _producer_snapshot_stale(root: Path, cid: str, snap_hash: str | None) -> bool:
    """True IFF a LIVE producer task backs `cid` (some task under root/tasks/ whose header carries
    `produces: cid`) AND that producer's current §3 is NOT frozen, OR its frozen body-hash differs
    from `snap_hash` (the landed snapshot's hash) — i.e. the producer re-opened/changed its contract
    since the snapshot was written (cross-component-recency). No live producer task (archived in a
    prior milestone, or a federation/external snapshot) -> False = existence-only, recency is the
    producer repo's job via the federation version pin. snap_hash None / unreadable §3 -> False (not
    confirmable here). PURE + TOTAL — never raises (a read error is a non-confirmation, not a block)."""
    if snap_hash is None:
        return False
    tasks_dir = root / "tasks"
    if not tasks_dir.is_dir():
        return False
    try:
        producers = sorted(td.name for td in tasks_dir.iterdir() if td.is_dir())
    except OSError:
        return False
    for pslug in producers:
        if _task_produces(root, pslug) != cid:
            continue
        raw3 = _raw_phase_bodies(root, pslug).get(3, "")
        if "FROZEN @" not in raw3:
            return True                                  # live producer exists but its §3 is not frozen
        return _contract_body_hash(raw3) != snap_hash    # frozen but drifted from the landed snapshot
    return False                                         # no live producer backs cid -> existence-only


def _consumer_contract_hold(root: Path, state: dict, slug: str) -> None:
    """The cross-component consumer HOLD at the §3 boundary, shared by cmd_advance (nxt=="contract")
    and cmd_phase (phase=="contract") so the admin override is not a backdoor (mirrors the
    phase build -> _build_entry precedent). A `consumes: <cid>` task targeting a DECLARED contract:
    a MISSING snapshot HARD-STOPs `producer_contract_unfrozen` (producer hasn't frozen); a PRESENT
    snapshot whose live producer has drifted/unfrozen HARD-STOPs `producer_contract_stale`
    (cross-component-recency — a stale leftover must not admit a consumer). No consumes / undeclared
    id -> return (byte-identical; a typo'd id is a cmd_check finding). `state` is accepted for call-site
    symmetry with _build_entry (unused here — the hold reads the task + contract files). Validate-
    then-write: every _die precedes the caller's phase bump, so a refused task does not move."""
    cid = _task_consumes(root, slug)
    if not cid:
        return
    cmap = _contracts(root)
    if cid not in cmap:
        return
    snap = _contract_snapshot(root, cid)
    if not snap.exists():
        _die(f"producer_contract_unfrozen: the producer '{cmap[cid].get('producer', '?')}' of "
             f"contract '{cid}' must freeze its contract before you write §3 — wait for "
             f".add/contracts/{cid}.json")
    try:
        snap_hash = json.loads(snap.read_text(encoding="utf-8")).get("hash")
    except (OSError, ValueError, AttributeError):
        snap_hash = None
    if _producer_snapshot_stale(root, cid, snap_hash):
        _die(f"producer_contract_stale: the live producer of contract '{cid}' changed or re-opened "
             f"its §3 since the landed .add/contracts/{cid}.json — re-cross the producer "
             "contract->tests to refresh the snapshot, then re-enter (never build against a stale shape)")


def _contract_body_hash(raw3: str) -> str:
    """md5 of the §3 contract SHAPE — the first ```fenced``` block, whitespace-normalized. The
    version stamp + freeze flags are excluded (fallback strips Status:/flag/change-request lines)
    so a pure version bump does NOT churn pinned consumers stale. PURE."""
    m = re.search(r"```(.*?)```", raw3, re.DOTALL)
    body = m.group(1) if m else re.sub(r"(?m)^(Status:|.*surfaced at freeze:|v\d+ CHANGE REQUEST).*$", "", raw3)
    return _md5_text(re.sub(r"\s+", " ", body).strip())


def _contract_findings(root: Path) -> list[tuple[str, str]]:
    """The loud gate surface for cross-component contracts — [] when clean / opted-out."""
    findings: list[tuple[str, str]] = []
    known = set(_components(root))
    for cid, spec in _contracts(root).items():
        if spec["producer"] not in known:
            findings.append(("contract_producer_unknown",
                             f"[contract.{cid}] producer {spec['producer']!r} is not a declared component"))
    return findings


# ── components.toml schema-lint (components-validator) ─────────────────────────────────
# The SOFT typo surface: the keys/tables a DEGRADE-SAFE read silently drops. All three
# codes are WARN-severity (measure-not-block) — forward-compat-safe (an older engine
# reading a newer file flags, never fails). Surfaced at `check` (as warnings) AND by
# `add.py components`. PURE · DEGRADE-SAFE · NO-EXEC: reads only .add/components.toml,
# never raises, never executes `verify`. A parse break is _component_findings' RED job.
_SCHEMA_KNOWN_KEYS: dict[str, tuple[str, ...]] = {
    "component": ("root", "verify", "green_bar", "language"),
    "contract": ("producer", "consumers"),
    "federation": ("source", "pin"),
}
_SCHEMA_KEY_TYPES: dict[str, dict[str, type]] = {
    # `root` is intentionally absent — a missing/non-str root is already RED `components_malformed`
    "component": {"verify": str, "green_bar": str, "language": str},
    "contract": {"producer": str, "consumers": list},
    "federation": {"source": str, "pin": str},
}
_SCHEMA_TYPENAME = {str: "a string", list: "a list"}


def _component_schema_findings(root: Path) -> list[tuple[str, str]]:
    """Schema-lint the components.toml registry for typos a degrade-safe read drops:
    an unknown/misspelled key, a wrong-type value on a known key, or an unrecognized
    top-level table. Returns [(code, detail)] (deterministic file order); [] when the
    file is absent / opted-out / unparseable (no double-report with the RED surface).
    All codes WARN: component_unknown_key · component_type_mismatch · component_unknown_table."""
    if tomllib is None:
        return []
    try:
        data = tomllib.loads((root / "components.toml").read_bytes().decode("utf-8"))
    except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError, ValueError):
        return []                       # a parse break is _component_findings' RED job
    if not isinstance(data, dict):
        return []
    out: list[tuple[str, str]] = []
    for top in data:                    # 1. unrecognized top-level tables/keys
        if top not in _SCHEMA_KNOWN_KEYS:
            out.append(("component_unknown_table",
                        f"top-level [{top}] is not a known table "
                        f"(expected one of: {', '.join(_SCHEMA_KNOWN_KEYS)})"))
    for table, known in _SCHEMA_KNOWN_KEYS.items():     # 2/3. per-entry keys + value types
        entries = data.get(table)
        if not isinstance(entries, dict):
            continue
        types = _SCHEMA_KEY_TYPES[table]
        for name, spec in entries.items():
            if not isinstance(spec, dict):
                continue                # a non-table entry is the RED surface's job
            for key, val in spec.items():
                if key not in known:
                    out.append(("component_unknown_key",
                                f"[{table}.{name}] has unknown key {key!r} "
                                f"(known: {', '.join(known)})"))
                elif key in types and not isinstance(val, types[key]):
                    out.append(("component_type_mismatch",
                                f"[{table}.{name}].{key} should be "
                                f"{_SCHEMA_TYPENAME.get(types[key], types[key].__name__)}, "
                                f"got {type(val).__name__}"))
    return out


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

    component-aware-add: when the task binds a known `component:` (_task_component),
    that component's root subtree (_component_root) is APPENDED to the resolved tokens
    (dedup) — composing with the explicit declaration, never redrawing token resolution.
    A bound task with NO Scope line returns [component_root] (not None); an UNBOUND task
    is byte-identical to before."""
    comp = _task_component(root, slug)
    croot = _component_root(root, comp) if comp and comp != "?" else None
    body = _raw_phase_bodies(root, slug).get(5, "")
    m = re.search(r"^\s*Scope \(may touch\):.*$", body, re.M)
    if not m:
        return [croot] if croot else None
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
    if croot and croot not in out:        # component-aware-add: compose, never redraw
        out.append(croot)
    return out


def _scope_walk(rootp: Path) -> dict[str, str]:
    """{project-root-relative path: md5} over the project tree, pruning
    _SCOPE_EXCLUDE_DIRS at any depth and skipping bytecode/OS junk +
    gitignored build artifacts (_SCOPE_EXCLUDE_FILES/_SCOPE_EXCLUDE_SUFFIXES). A file
    unreadable at SNAPSHOT time is skipped; at the GATE the resulting absence
    reads as a touch (fail-closed at the biting end). Bytes only — no git."""
    files: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(rootp):
        dirnames[:] = [d for d in dirnames if d not in _SCOPE_EXCLUDE_DIRS]
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
    t["phase"] = "build"                      # DIRECT — never via advance (no re-snapshot)
    t["updated"] = _now()
    _sync_task_marker(root, slug, "build")
    save_state(root, state)                   # the increment is durable BEFORE the exit
    print(f"return_to_build: task '{slug}' — cheat detected ({reason}); RETURN TO BUILD for an "
          f"HONEST redo, attempt {heal['attempts']} of {HEAL_CAP}. Revert the tampered file or "
          "rebuild src honestly, then advance back to verify.")
    raise SystemExit(3)                       # redo signal (distinct from _die's 1, argparse's 2)


def _consumer_stale_guard(root: Path, state: dict, slug: str) -> None:
    """Refuse a COMPLETING gate when a `consumes:` task's pinned producer contract hash is STALE
    (the producer re-froze a CHANGED shape since the pin) — the consumer built against an
    out-of-date contract (consumer-stale-gate, the gate twin of cmd_check's contract_consumer_stale
    warning). Recoverable, not a cheat: re-pin by re-crossing contract->tests after reviewing the
    new frozen shape. Degrade-safe — an unreadable/missing live snapshot is NOT decided here (it
    stays a cmd_check warning + the advance-time contract_snapshot_missing HARD-STOP); only a
    CONFIRMED hash drift blocks. Placed with the other completing guards, BEFORE the waiver write,
    so a stale pin is never launderable through RISK-ACCEPTED; HARD-STOP never reaches here."""
    pin = state["tasks"][slug].get("contract_pin")
    if not pin:
        return
    try:
        live = json.loads(_contract_snapshot(root, pin["id"]).read_text(encoding="utf-8")).get("hash")
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return  # unreadable -> surfaced by cmd_check, not confirmable as stale here
    if live is not None and live != pin.get("hash"):
        _die(f"contract_consumer_stale: task '{slug}' pinned contract '{pin['id']}' changed shape "
             "since the pin (the producer re-froze) — re-pin by re-crossing contract->tests after "
             "reviewing the producer's new frozen shape; never complete against a stale contract")


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
        phase = t.get("phase", "specify")
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
        # additive (v13-1): MILESTONE.md-planned slugs with no TASK.md yet —
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


def task_phases(root: Path, slug: str) -> list[dict]:
    """The frozen per-task PHASE-DETAIL shape (v9-1): parse TASK.md §0–§7 into eight
    blocks ground→observe. PURE — NO writes. Each entry is
    { "phase": <name>, "n": <0..7>, "body": <cleaned text | "(empty)"> }.

    The heading scan lives in _phase_spans (shared with the decide digest); this view
    CLEANS each body. Missing file / missing section / placeholder-only body ->
    "(empty)" (fail-closed)."""
    names = PHASES[:-1]  # ground..observe; "done" is a terminal STATE, not a section
    f = root / "tasks" / slug / "TASK.md"
    try:
        text = f.read_text(encoding="utf-8")
    except OSError:   # missing OR unreadable -> every phase fail-closed to "(empty)"
        return [{"phase": names[n], "n": n, "body": "(empty)"} for n in range(0, 8)]
    spans = _phase_spans(text)
    return [{"phase": names[n], "n": n,
             "body": _clean_phase_body(spans[n]) if n in spans else "(empty)"}
            for n in range(0, 8)]


def _task_title(root: Path, slug: str) -> str:
    """The task's display title from TASK.md line 1 `# TASK: <title>` (fail-soft: the
    slug if the file or the header line is missing)."""
    f = root / "tasks" / slug / "TASK.md"
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
    """Format ONE task's seven phase blocks (specify→observe) as the read-only PHASE
    DETAIL: each block shows its number+name, a reached/current/pending marker (from the
    task's state phase), and its captured §N body (fail-closed to "(empty)"). The verify
    block additionally prints the recorded GATE from state.json — authoritative, NEVER
    parsed from prose. Returns PLAIN text (no ANSI); color is a tty-only skin in
    cmd_report. PURE — NO writes (the v9 read-only discipline, carried)."""
    g = _ASCII if ascii else _UNICODE
    W = width
    banner, rule = g["h"] * W, " " + g["rule"] * (W - 1)
    t = (state.get("tasks") or {}).get(slug, {})
    phase = t.get("phase", "specify")
    gate = t.get("gate", "none")
    ci = PHASES.index(phase) if phase in PHASES else 0

    L = [banner, f" {mslug} · {slug} · {_task_title(root, slug)}", banner]
    L.append(f" PHASE {phase}    GATE {gate}")
    L.append(banner)
    for p in task_phases(root, slug):
        i = p["n"]   # n IS the PHASES index now (ground=0 .. observe=7)
        mk = (g["reached"] if (phase == "done" or i < ci)
              else g["current"] if i == ci else g["pending"])
        L.append("")
        L.append(f" {mk} {p['n']} {p['phase'].upper()}")
        L.append(rule)
        if p["n"] == 6:   # verify: the recorded gate, sourced from state (not prose)
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
        L.append(f" SPEC DELTAS    {n} open {noun} — resolve: new-task --from-delta / drop-delta")
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
_FRONT_PHASES = ("specify", "scenarios", "contract", "tests")


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


def _section0_anchors(raw0: str) -> str | None:
    """The value of the §0 GROUND "Anchors the contract cites:" line, stripped.
    None when the §0 body carries no such line (no §0, or a malformed map). PURE."""
    for ln in raw0.splitlines():
        m = re.match(r"\s*Anchors the contract cites:\s*(.*)$", ln)
        if m:
            return m.group(1).strip()
    return None


def _grounded_state(raw: dict[int, str]) -> bool | None:
    """Tri-state grounding measure over a task's RAW §bodies (measure-not-block):
      True  — the §0 "Anchors the contract cites:" line is filled (real content)
      False — the §0 section exists but its Anchors line is the "<…>" placeholder / empty
      None  — no §0 section (a pre-ground / legacy task), OR a §0 with no Anchors line
    PURE; fail-open (an unparseable §0 -> None, never a false False). The freeze review
    checklist asks the human to confirm True; status/check surface it, never block on it."""
    if 0 not in raw:
        return None
    anchors = _section0_anchors(raw[0])
    if anchors is None:
        return None
    return bool(anchors) and not anchors.startswith("<")


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


def decide_data(root: Path, state: dict, mslug: str, slug: str) -> dict:
    """FACTS for the task-level decision-point digest (frozen shape). The decision comes
    from STATE ONLY: recorded (gate set / observe / done) · front (specify→tests) ·
    gate (build/verify). judgment = extracted markers, byte-verbatim. PURE."""
    tasks = state.get("tasks") or {}
    t = tasks.get(slug, {})
    phase = t.get("phase", "specify")
    gate = t.get("gate", "none")
    if gate != "none" or phase in ("observe", "done"):
        seam = "recorded"
    elif phase == "ground":
        seam = "ground"
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
    elif seam == "ground":
        judgment = _decision_markers(raw.get(0, ""), 0)
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
    elif seam == "ground":
        unlocks = "gather the codebase -> advance to specify"
        decide = "gather the real codebase (the section 0 GROUND map), then: add.py advance"
    else:
        unlocks = "none"
        decide = f"no decision pending — recorded gate: {gate}"
    return {"seam": seam, "milestone": mslug, "task": slug, "phase": phase,
            "gate": gate, "judgment": judgment, "facts": facts,
            "unlocks": unlocks, "decide": decide}


def render_decide(root: Path, state: dict, mslug: str, slug: str, *,
                  width: int = _DEFAULT_WIDTH, ascii: bool = False) -> str:
    """Text view of the decision-point digest — decisive facts FIRST: NEEDS YOUR
    JUDGMENT (markers byte-verbatim, section-tagged) -> [front: §3 verbatim] ->
    ENGINE FACTS -> UNLOCKS -> DECIDE. PURE — no writes; plain text (color is a
    tty-only skin in cmd_report, like every report view)."""
    d = decide_data(root, state, mslug, slug)
    g = _ASCII if ascii else _UNICODE
    banner = g["h"] * width
    seam_label = {"gate": "VERIFY GATE", "front": "CONTRACT APPROVAL",
                  "recorded": "RECORDED", "ground": "GROUND"}[d["seam"]]
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
    """Slugs MILESTONE.md plans (rows `- [ ] <slug> …`) that have no TASK.md yet —
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
            if slug not in out and not (root / "tasks" / slug / "TASK.md").is_file():
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
        # decompose it — name the command, not the dead-end "none — no tasks yet".
        return f"decompose into tasks — add.py new-task {ms}", True
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
            command = ("add.py gate PASS | RISK-ACCEPTED | HARD-STOP"
                       if phase == "verify" else "add.py advance")
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
    task_md = root / "tasks" / slug / "TASK.md"
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
    """Scan every .add/tasks/*/TASK.md for open lessons learned.

    Returns a dict keyed by competency in canonical order; each value is a list
    of {task, text, evidence} dicts. READ-ONLY — never mutates any file."""
    by_comp: dict[str, list[dict]] = {c: [] for c in _COMPETENCY_ORDER}
    tasks_dir = root / "tasks"
    if not tasks_dir.is_dir():
        return by_comp
    for task_md in sorted(tasks_dir.glob("*/TASK.md")):
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
    """Scan every .add/tasks/*/TASK.md "### Spec delta" block for SPEC deltas of `status`.

    Returns a FLAT list of {task, text, evidence} dicts (SPEC is one tag, never bucketed by
    competency). A SPEC delta is a forward hand-off that resolves into a TASK (seeded), is
    dismissed (dropped), or is DEFERRED non-lossily (carried) — the open/carried VIEWS are this
    one scan keyed on `status`. READ-ONLY; never mutates any file."""
    out: list[dict] = []
    tasks_dir = root / "tasks"
    if not tasks_dir.is_dir():
        return out
    for task_md in sorted(tasks_dir.glob("*/TASK.md")):
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


def _collect_carried_spec_deltas(root: Path) -> list[dict]:
    """Carried (deferred, non-lossy) SPEC deltas — the `deltas --carried` retrieval surface."""
    return _collect_spec_deltas(root, "carried")


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


# ── add.py fold — mechanized competency-lesson consolidation ────────────────────────────────
# The HUMAN-AUTHORIZED reversal of the prior "the engine stays judgment-free; there is no
# add.py fold" principle (foundation-update-loop re-frozen @ v3). The engine now mechanizes ONE
# consolidation session — flip + stamp + route + version-bump — but only ever TRANSCRIBES a
# lesson's own captured text into its routed home; it NEVER composes or merges prose (that
# editorial judgment stays the human's, via the compaction door). `fold`/`folded` are Group C
# machine tokens here (the subcommand name + the status value), referenced by NAME inside output
# strings so the ubiquitous-language prose lint sees no slang — only the two defs below carry the
# literal, both exempt via MACHINE_CONSTANTS.
_FOLD_VERB = "fold"        # the subcommand / decision-record verb
_FOLDED = "folded"         # the resolved status value
# group(2) carries any OPTIONAL persona annotation (`· persona:<slug> · <hint>`) so flipping
# open->folded preserves it byte-for-byte (persona-self-improve).
_COMP_OPEN_TOKEN_RE = re.compile(
    r"(\[\s*(?:DDD|SDD|UDD|TDD|ADD)\s*·\s*)open"
    r"(\s*(?:·\s*persona:[^\s·\]]+\s*·\s*[^·\]]+?\s*)?\])")

# competency -> (foundation file, section-heading PREFIX) — fold.md's routing table. DDD/SDD/UDD
# land in PROJECT.md sections; TDD/ADD in CONVENTIONS.md (they ARE the engine). Total over the five.
_FOLD_ROUTES = {
    "DDD": ("PROJECT.md", "## Domain"),
    "SDD": ("PROJECT.md", "## Spec"),
    "UDD": ("PROJECT.md", "## Users"),
    "TDD": ("CONVENTIONS.md", "## Method learnings"),
    "ADD": ("CONVENTIONS.md", "## Method learnings"),
}
_KEY_DECISIONS_HEADING = "## Key Decisions"   # the universal audit-trail section (every session adds one row)
_TABLE_SEP_RE = re.compile(r"\s*\|[-\s|]+\|\s*$")

# persona-self-improve: a `persona:<slug>` lesson routes into `.add/personas/<slug>.md` instead of a
# foundation file. The section HINT picks the growable section; only these two are routable.
_PERSONA_FOLD_SECTIONS = {
    "critical-rule": "## Critical Rules",
    "success-metric": "## Success Metrics",
}


def _fold_competency_delta(text: str, version: int, comps=None) -> str | None:
    """Flip EVERY open competency lesson in `text` to resolved + append ` [<resolved> foundation-version N]`.

    PURE — no IO. Mirrors `_resolve_spec_delta`: only the status token changes plus the trailing
    stamp; the line's text + `(evidence: …)` are byte-preserved. `comps` (a set of competency tags)
    narrows which to flip; None = all five. Returns the new text, or None when NOTHING was open to
    flip (the caller then refuses / skips — validate-all-then-write)."""
    lines = text.splitlines(keepends=True)
    flipped = False
    for i, ln in enumerate(lines):
        m = _DELTA_RE.match(ln.rstrip("\n"))
        if not m or m.group(2) != "open":
            continue
        if comps is not None and m.group(1) not in comps:
            continue
        eol = ln[len(ln.rstrip("\n")):]                       # preserve the exact line ending
        body = _COMP_OPEN_TOKEN_RE.sub(rf"\g<1>{_FOLDED}\g<2>", ln.rstrip("\n"), count=1)
        body = f"{body} [{_FOLDED} foundation-version {version}]"
        lines[i] = body + eol
        flipped = True
    return "".join(lines) if flipped else None


def _section_present(text: str, heading_prefix: str) -> bool:
    return any(ln.startswith(heading_prefix) for ln in text.splitlines())


def _prepend_to_section(text: str, heading_prefix: str, bullet: str) -> str:
    """Insert `bullet` immediately after the first line starting with `heading_prefix`
    (newest-first, at the TOP of the section). Caller guarantees the heading exists."""
    lines = text.splitlines(keepends=True)
    for i, ln in enumerate(lines):
        if ln.startswith(heading_prefix):
            lines.insert(i + 1, bullet if bullet.endswith("\n") else bullet + "\n")
            return "".join(lines)
    return text


def _prepend_key_decision_row(text: str, row: str) -> str:
    """Insert `row` just below the §Key Decisions table separator (newest-first); if the table
    separator is absent, fall back to right after the heading. Caller guarantees the heading."""
    lines = text.splitlines(keepends=True)
    head = next((i for i, ln in enumerate(lines)
                 if ln.startswith(_KEY_DECISIONS_HEADING)), None)
    if head is None:
        return text
    at = head + 1
    for j in range(head + 1, min(head + 6, len(lines))):
        if _TABLE_SEP_RE.match(lines[j].rstrip("\n")):
            at = j + 1
            break
    lines.insert(at, row if row.endswith("\n") else row + "\n")
    return "".join(lines)


def cmd_fold(args: argparse.Namespace) -> None:
    """Mechanize ONE competency-lesson consolidation session — flip + stamp + route + bump, atomic.

    Collect every OPEN competency lesson (optionally narrowed by --task/--comp), flip each to the
    resolved status + ` [<resolved> foundation-version N]`, transcribe it VERBATIM into its routed
    foundation section, prepend one §Key Decisions row, and bump `foundation-version` ONCE.
    Validate-ALL-then-write: every precondition is checked and every new body built in memory BEFORE
    any write, so a reject leaves the whole tree byte-unchanged. The engine transcribes — it never
    composes/merges prose (the human's consolidation, via the compaction door). Running the command
    IS the human's confirmation; it never self-approves WHICH lessons to keep."""
    root = _require_root()
    state = load_state(root)

    by_comp = _collect_open_deltas(root)
    want_task = getattr(args, "task", None)
    want_comp = getattr(args, "comp", None)
    selected = []
    for comp in _COMPETENCY_ORDER:
        if want_comp and comp != want_comp:
            continue
        for it in by_comp.get(comp, []):
            if want_task and it["task"] != want_task:
                continue
            selected.append({**it, "comp": comp})
    if not selected:
        scope = (f"task '{want_task}'" if want_task else "the project") + \
                (f", competency {want_comp}" if want_comp else "")
        _die(f"no_open_deltas: no open lesson to consolidate in {scope} (see `add.py deltas`)")

    # version — one bump for the whole session; every stamp carries the SAME N.
    project_md = root / "PROJECT.md"
    project_text = project_md.read_text(encoding="utf-8")
    vm = re.search(r"foundation-version:\s*(\d+)", project_text)
    if not vm:
        _die("no_foundation_version: PROJECT.md has no parseable 'foundation-version:' header to bump")
    prev_v = int(vm.group(1))
    new_v = prev_v + 1

    # A lesson with a `persona:<slug>` target routes to a persona living doc, NOT a foundation file
    # (persona-self-improve). Partition first so the foundation-route checks skip persona lessons.
    persona_sel = [it for it in selected if it.get("persona")]
    found_sel = [it for it in selected if not it.get("persona")]

    # routing — every FOUNDATION lesson's destination section (and the audit-trail section) must exist.
    conventions_md = root / "CONVENTIONS.md"
    conventions_text = conventions_md.read_text(encoding="utf-8") if conventions_md.exists() else ""
    file_text = {"PROJECT.md": project_text, "CONVENTIONS.md": conventions_text}
    for it in found_sel:
        fname, heading = _FOLD_ROUTES[it["comp"]]
        if not _section_present(file_text[fname], heading):
            _die(f"missing_route_section: {fname} has no '{heading}' section for a "
                 f"{it['comp']} lesson — add the section header and re-run")
    if not _section_present(project_text, _KEY_DECISIONS_HEADING):
        _die(f"missing_route_section: PROJECT.md has no '{_KEY_DECISIONS_HEADING}' "
             "section for the audit-trail row — add the section header and re-run")

    # persona routing — validate fail-closed BEFORE any write (design-for-failure): the section hint
    # must be routable and the target persona file must exist. No network, no child launch — pure IO.
    persona_paths: dict[str, Path] = {}
    for it in persona_sel:
        hint = (it.get("hint") or "").strip()
        if hint not in _PERSONA_FOLD_SECTIONS:
            _die(f"persona_section_unroutable: '{hint or '(none)'}' is not a growable persona "
                 f"section — use one of {', '.join(_PERSONA_FOLD_SECTIONS)}")
        slug = it["persona"]
        ppath = root / "personas" / f"{slug}.md"
        if not _persona_slug_valid(slug) or not ppath.is_file():
            _die(f"missing_persona_target: no .add/personas/{slug}.md for a persona lesson — "
                 "seed the persona first (setup) or fix the slug")
        persona_paths[slug] = ppath

    # ── build EVERY edit in memory before writing anything ──────────────────────────────────────
    comps_filter = {want_comp} if want_comp else None
    task_new: dict[str, str] = {}
    for slug in dict.fromkeys(it["task"] for it in selected):
        tmd = root / "tasks" / slug / "TASK.md"
        flipped = _fold_competency_delta(tmd.read_text(encoding="utf-8"), new_v, comps_filter)
        if flipped is None:                                   # defensive: selected ⇒ ≥1 open here
            _die(f"no_open_deltas: task '{slug}' lost its open lesson mid-session")
        task_new[slug] = flipped

    def _bullet(it):
        ev = f" (evidence: {it['evidence']})" if it["evidence"] else ""
        return (f"- ({it['comp']}) {it['text']}{ev}  "
                f"[{_FOLDED} foundation-version {new_v} · from {it['task']}]")

    def _persona_bullet(it):
        ev = f" (evidence: {it['evidence']})" if it["evidence"] else ""
        return (f"- {it['text']}{ev}  "
                f"[{_FOLDED} {date.today().isoformat()} · from {it['task']}]")

    # transcribe FOUNDATION lessons verbatim (reverse so canonical-order first lands on top, newest-first).
    proj_text, conv_text = project_text, conventions_text
    for it in reversed(found_sel):
        fname, heading = _FOLD_ROUTES[it["comp"]]
        if fname == "PROJECT.md":
            proj_text = _prepend_to_section(proj_text, heading, _bullet(it))
        else:
            conv_text = _prepend_to_section(conv_text, heading, _bullet(it))

    # transcribe PERSONA lessons into their living docs — PREPEND newest-first under the hinted
    # section, NEVER clobbering (every prior persona line survives; the schema stays conformant).
    from collections import Counter
    persona_new: dict[str, str] = {}
    for it in reversed(persona_sel):
        slug = it["persona"]
        before = persona_new.get(slug) or persona_paths[slug].read_text(encoding="utf-8")
        heading = _PERSONA_FOLD_SECTIONS[it["hint"].strip()]
        if not _section_present(before, heading):           # defensive: a conformant persona has it
            _die(f"persona_section_unroutable: .add/personas/{slug}.md has no '{heading}' section")
        after = _prepend_to_section(before, heading, _persona_bullet(it))
        # never-clobber INVARIANT: every pre-existing line must survive the merge.
        if Counter(before.splitlines()) - Counter(after.splitlines()):
            _die(f"persona_clobber_forbidden: consolidating into {slug}.md would drop existing content")
        # post-merge INVARIANT: the four required persona sections survive.
        if _persona_missing(after):
            _die(f"persona_clobber_forbidden: consolidating into {slug}.md broke the persona schema "
                 f"(missing {', '.join(_persona_missing(after))})")
        persona_new[slug] = after

    counts = {c: sum(1 for it in selected if it["comp"] == c) for c in _COMPETENCY_ORDER}
    count_str = " · ".join(f"{c} {counts[c]}" for c in _COMPETENCY_ORDER if counts[c])
    scope = "all" if not (want_task or want_comp) else " ".join(
        filter(None, [f"--task {want_task}" if want_task else "",
                      f"--comp {want_comp}" if want_comp else ""]))
    row = (f"| {date.today().isoformat()} | {_FOLD_VERB} {scope} → foundation-version {new_v} "
           f"({count_str}) | consolidate captured OBSERVE lessons into the versioned foundation "
           f"| {len(selected)} lessons open→{_FOLDED}; +{len(selected)} routed bullets; {prev_v}→{new_v} |")
    proj_text = _prepend_key_decision_row(proj_text, row)
    proj_text = re.sub(r"foundation-version:\s*\d+", f"foundation-version: {new_v}", proj_text, count=1)

    # ── all bodies built; commit ALL via the all-or-nothing multi-file primitive: a stage failure
    #    (disk-full / permission) writes nothing, and a mid-commit rename failure rolls back every
    #    already-committed file — so the foundation never advances while a TASK.md stays unflipped. ─
    writes: list[tuple[Path, str]] = [(project_md, proj_text)]
    touched = ["PROJECT.md"]
    if conv_text != conventions_text:
        writes.append((conventions_md, conv_text))
        touched.append("CONVENTIONS.md")
    for slug, body in task_new.items():
        writes.append((root / "tasks" / slug / "TASK.md", body))
    touched.append(f"{len(task_new)} TASK.md")
    for slug, body in persona_new.items():
        writes.append((persona_paths[slug], body))
    if persona_new:
        touched.append(f"{len(persona_new)} persona")
    _atomic_write_many(writes)

    print(f"{_FOLDED} {len(selected)} lessons -> foundation-version {new_v}")
    print(f"  {count_str}")
    print(f"  bumped PROJECT.md  {prev_v} -> {new_v}")
    print(f"  files: {', '.join(touched)}")
    print(_next_footer(root, state))


_AUDIT_STAMP_RE = re.compile(r"Status:\s*FROZEN @ v\d+\s*[—-]+\s*approved by\s+\S+")
_AUDIT_OUTCOME_RE = re.compile(r"^Outcome:\s*(PASS|RISK-ACCEPTED|HARD-STOP)\b", re.M)
_AUDIT_SECURITY_RE = re.compile(
    r"^\s*- \[[ x~]\] no exposed secrets.*(?:\n(?!\s*- \[|#).*)*", re.M)
_AUDIT_REVIEWED_RE = re.compile(r"^Reviewed by:(.*)$", re.M)


def _audit_findings(root: Path, state: dict) -> tuple[int, list[dict]]:
    """The gate-audit core: verify that human decision points left WELL-FORMED records.
    Judgment-free — checks record SHAPE (a named human at the freeze, exactly one
    gate outcome, prose ≡ state, a marked security note never auto-reviewed),
    never re-decides an outcome. Scope: active tasks done/observe or gated; open
    fronts skipped. PURE — reads only. Honest limit: shape, not engagement — a
    forged name passes; CI wiring makes forgery explicit and attributable."""
    tasks = state.get("tasks") or {}
    checked, findings = 0, []

    def f(slug: str, code: str, detail: str) -> None:
        findings.append({"task": slug, "code": code, "detail": detail})

    for slug in sorted(tasks):
        t = tasks[slug]
        phase, gate = t.get("phase", "specify"), t.get("gate", "none")
        if phase not in ("done", "observe") and gate == "none":
            continue   # the front is still open — nothing recorded to audit
        checked += 1
        raw = _raw_phase_bodies(root, slug)
        s3, s6 = raw.get(3, ""), raw.get(6, "")
        if not _AUDIT_STAMP_RE.search(s3):
            f(slug, "unstamped_freeze",
              "§3 lacks 'Status: FROZEN @ vN — approved by <name>'")
        # verified-marker discriminator (task unflagged-freeze): enforce the
        # lowest-confidence flag ONLY on records that crossed the guard (flag_verified).
        # A marked record whose flag was deleted/corrupted post-freeze is
        # tampering; unmarked predecessors are skipped — the board is never
        # retro-redded.
        if t.get("flag_verified") and not _flag_well_formed(s3):
            f(slug, "unflagged_freeze",
              "flag_verified record lost its well-formed "
              "'Least-sure flag surfaced at freeze:' unit")
        outcomes = _AUDIT_OUTCOME_RE.findall(s6)
        if len(outcomes) != 1:
            f(slug, "malformed_gate_record",
              f"{len(outcomes)} Outcome lines in §6 (need exactly 1)")
        elif gate != "none" and outcomes[0] != gate:
            f(slug, "gate_record_mismatch",
              f"§6 records {outcomes[0]} but state.json records {gate}")
        elif gate == "none":
            # F13 ungated_verdict: §6 carries a verdict the engine never gated.
            # cmd_gate is the ONLY writer of `gate` (it also marks done), so a
            # done/observe task at gate=="none" reached its verdict without the
            # engine — a hand-stamped §6 or an `advance` past verify. Constraint 4
            # requires a RECORDED outcome; a §6 verdict without one is not trusted.
            f(slug, "ungated_verdict",
              f"§6 records {outcomes[0]} but state.json recorded no gate (gate=none) — "
              f"the verdict was written without the engine gate")
        sec = _AUDIT_SECURITY_RE.search(s6)
        marked = bool(sec and ("NOTE" in sec.group(0) or "⚠" in sec.group(0)))
        rev = _AUDIT_REVIEWED_RE.search(s6)
        if marked and rev and "auto-gate" in rev.group(1):
            f(slug, "unescalated_security_note",
              "security-line note (NOTE/⚠) with an auto-gate reviewer")
        # F7 unguarded_high_risk_auto (task high-risk-signal, v14): a declared
        # high-risk record must show a guarded dial AND a human at the gate —
        # catches post-gate header tampering and auto-resolved high-risk gates.
        # advisor-gate-relax: a mechanical task whose Advisor 3-lens verdict shows
        # PASS + Residue: none is exempt — the outer condition is False so both
        # sub-branches are skipped.  Non-mechanical (security/data/architecture)
        # never relax; an absent advisor block is fail-safe False → guard fires.
        hdr = _task_header(root, slug)
        if _RISK_HIGH_RE.search(hdr) and not (_task_sensitivity(hdr) == "mechanical"
                and _advisor_verdict_is_pass(s6)
                and _advisor_no_residue(s6)):
            if not _autonomy_lowered(hdr):
                f(slug, "unguarded_high_risk_auto",
                  "risk: high declared but autonomy is not lowered (manual or conservative)")
            elif rev and "auto-gate" in rev.group(1):
                f(slug, "unguarded_high_risk_auto",
                  "risk: high task whose GATE RECORD reviewer is the auto-gate")
        if outcomes == ["RISK-ACCEPTED"]:
            if marked:
                f(slug, "risk_accepted_security",
                  "a waiver on a marked security item is never allowed")
            if not all(re.search(rf"{k}:\s*(?!<)\S", s6)
                       for k in ("owner", "ticket", "expires")):
                f(slug, "waiver_incomplete",
                  "RISK-ACCEPTED needs owner · ticket · expires")
        # adr-at-observe: a gated/done task whose §7 Decisions (ADR) block STILL holds its bare
        # <harvested…> placeholder never harvested its decision record. GRANDFATHER (INV-1): a §7
        # with NO block is legacy → skipped. BARE-LINE probe (INV-2, the same regex _stamp_adr_record
        # writes through) → harvested prose that merely quotes "<harvested at done" is not a false hit.
        s7 = raw.get(7, "")
        if "### Decisions (ADR)" in s7 and re.search(r"(?m)^<harvested at done[^\n]*>$", s7):
            f(slug, "adr_record_missing",
              "§7 Decisions (ADR) block still holds its <harvested…> placeholder (never harvested at gate)")
    return checked, findings


def _freeze_skip_notices(state: dict) -> list[dict]:
    """The recorded `--skip-freeze` crossings (freeze-gate-universal): tasks that crossed
    tests->build on a DRAFT §3 via the explicit escape. SURFACED by `add.py audit` so no skip is
    silent — but NOT a finding: a recorded, sanctioned bypass never fails CI; the human judges it.
    PURE — reads only."""
    out = []
    for slug in sorted(state.get("tasks") or {}):
        mark = (state["tasks"][slug] or {}).get("freeze_skipped")
        if isinstance(mark, dict):
            out.append({"task": slug, "by": mark.get("by", "?"),
                        "at": mark.get("at", "?"), "from_phase": mark.get("from_phase", "?")})
    return out


# Any `risk:` declaration in the header (high|normal|low|…) — read from the `·`-delimited header
# region only (mirrors _RISK_HIGH_RE's anchoring so a title substring can never look like one).
_RISK_ANY_RE = re.compile(r"(?:^|·)[ \t]*risk:[ \t]*\S", re.MULTILINE)

# A single `Reported:` line (report-rendered-trace) — scoped to ONE phase body at a time by the
# caller (bodies.get(3, "")/bodies.get(6, "")), so §3 and §6 never cross-contaminate each other.
_REPORTED_LINE_RE = re.compile(r"(?m)^Reported:[ \t]*(.*)$")


def _reported_unrecorded(body_text: str) -> bool:
    """True iff a 'Reported:' line is PRESENT but still an unfilled `<...>` placeholder or blank.
    ABSENT line -> False (grandfathered — a pre-existing task's TASK.md predates this template
    field), mirroring _section_unfilled's absent-block convention."""
    m = _REPORTED_LINE_RE.search(body_text)
    if m is None:
        return False
    val = m.group(1).strip()
    return (not val) or bool(re.fullmatch(r"<[^>\n]*>", val))


def _guarantee_lint_notices(root: Path, state: dict) -> dict:
    """PRESENCE-ONLY, MEASURE-NOT-BLOCK lints SURFACED (never failed-on) by `add.py audit`
    (guarantee-audit-lints). For tasks that reached verify (phase ∈ {verify, observe, done}):
      shallow[]          = §6 '### Deep checks' block present-but-unfilled (_section_unfilled; an
                           ABSENT block grandfathers a legacy task — never retro-flagged);
      risk_unset[]       = the header carries NO `risk:` token (an undeclared risk level at verify);
      sensitivity_unset[]= the header carries NO valid `sensitivity:` token (risk-sensitivity-taxonomy);
      refute_unrecorded[]= §6 '### Refute-read verdict' block present-but-unfilled (self-grading-
                           refute-record, M4) — the earned-green verdict the AI must record under
                           `auto`; ABSENT block grandfathers exactly like shallow. MEASURE-NOT-BLOCK:
                           never auto-blocks a gate, only surfaced here for review + a human spot-audit.
      rule_coverage_gap[]= this task's OWN §1 Must/Reject IDs have >=1 rule with no §2 scenario tag
                           and no §4 `covers:` line (_rule_coverage_gaps — same opt-in-by-tag-presence
                           grandfather as `add.py check`'s whole-project sweep) — surfaced the moment
                           THIS task reaches verify, not only via a separate `check` invocation someone
                           has to remember to run; `check` still owns the per-rule detail.
      contract_report_unrecorded[] = §3's `Reported:` line present-but-unfilled (report-rendered-
                           trace) — the freeze report (banner/ARC/SHAPE) was cited by the guide but
                           never recorded as rendered; ABSENT line grandfathers a pre-field task.
      verify_report_unrecorded[]   = §6's `Reported:` line present-but-unfilled — the gate report
                           (banner/ARC) was never recorded as rendered; same grandfather rule.
    Honest visibility for six verify guarantees; NEVER a finding (audit stays exit 0). PURE — reads
    TASK.md + state only, writes nothing."""
    shallow, risk_unset, refute_unrecorded, sensitivity_unset = [], [], [], []
    advisor_verdict_unrecorded = []
    advisor_reviewer_is_author = []
    advisor_residue_on_mechanical_mis_tier = []
    rule_coverage_gap = []
    contract_report_unrecorded = []
    verify_report_unrecorded = []
    for slug in sorted(state.get("tasks") or {}):
        if (state["tasks"][slug] or {}).get("phase") not in ("verify", "observe", "done"):
            continue
        bodies = _raw_phase_bodies(root, slug)
        body3 = bodies.get(3, "")
        body6 = bodies.get(6, "")
        hdr = _task_header(root, slug)
        if _section_unfilled(body6, "### Deep checks"):
            shallow.append(slug)
        if _section_unfilled(body6, "### Refute-read verdict"):
            refute_unrecorded.append(slug)
        if _section_unfilled(body6, "### Advisor 3-lens verdict"):
            advisor_verdict_unrecorded.append(slug)
        if _reported_unrecorded(body3):
            contract_report_unrecorded.append(slug)
        if _reported_unrecorded(body6):
            verify_report_unrecorded.append(slug)
        if not _RISK_ANY_RE.search(hdr):
            risk_unset.append(slug)
        # sensitivity_unset (risk-sensitivity-taxonomy): a verify-reached task with no
        # human-declared sensitivity — MEASURE-NOT-BLOCK, same class as risk_unset.
        if _task_sensitivity(hdr) is None:
            sensitivity_unset.append(slug)
        # rule_coverage_gap (verify-traceability-glint): this task's own §1 Must/Reject vs
        # §2/§4 tags — the SAME predicate `check` uses project-wide, scoped to just this task
        # and surfaced right at verify, not only via a separate whole-project sweep.
        if _rule_coverage_gaps(bodies.get(1, ""), bodies.get(2, ""), bodies.get(4, "")):
            rule_coverage_gap.append(slug)
        # advisor_reviewer_is_author / advisor_residue_on_mechanical_mis_tier
        # (advisor-verdict-audit): MEASURE-NOT-BLOCK lints on the filled advisor block.
        # Both require the block to be PRESENT AND FILLED (not just unfilled).
        # Extract ONLY the advisor sub-section to avoid false matches from
        # the Refute-read verdict block (which also carries Verdict:/Residue: lines).
        _advisor_body = ""
        _adv_idx = body6.find("### Advisor 3-lens verdict")
        if _adv_idx != -1:
            _adv_rest = body6[_adv_idx + len("### Advisor 3-lens verdict"):]
            _next_hdr = re.search(r"\n###", _adv_rest)
            _advisor_body = _adv_rest[:_next_hdr.start()] if _next_hdr else _adv_rest
        _advisor_filled = (_adv_idx != -1
                           and not _section_unfilled(body6, "### Advisor 3-lens verdict"))
        if _advisor_filled:
            _ma = re.search(r"(?m)^Advisor:(.*)$", _advisor_body)
            _advisor_name = _ma.group(1).strip() if _ma else ""
            _gate_name = (state["tasks"][slug].get("gate_actor") or {}).get("name", "").strip()
            if (_advisor_name and _gate_name
                    and _advisor_name.lower() == _gate_name.lower()):
                advisor_reviewer_is_author.append(slug)
            _sens = _task_sensitivity(hdr)
            if _sens == "mechanical":
                _mr = re.search(r"(?m)^Residue:(.*)$", _advisor_body)
                _mv = re.search(r"(?m)^Verdict:(.*)$", _advisor_body)
                _residue = _mr.group(1).strip() if _mr else ""
                _verdict = _mv.group(1).strip() if _mv else ""
                if (_residue and _residue.lower() != "none"
                        and _verdict.upper().startswith("PASS")):
                    advisor_residue_on_mechanical_mis_tier.append(slug)
    return {"shallow": shallow, "risk_unset": risk_unset, "refute_unrecorded": refute_unrecorded,
            "sensitivity_unset": sensitivity_unset,
            "advisor_verdict_unrecorded": advisor_verdict_unrecorded,
            "advisor_reviewer_is_author": advisor_reviewer_is_author,
            "advisor_residue_on_mechanical_mis_tier": advisor_residue_on_mechanical_mis_tier,
            "rule_coverage_gap": rule_coverage_gap,
            "contract_report_unrecorded": contract_report_unrecorded,
            "verify_report_unrecorded": verify_report_unrecorded}


def cmd_audit(args: argparse.Namespace) -> None:
    """Read-only: audit recorded human decision points for well-formedness. Exit 0 clean,
    exit 1 with findings — the enforcement gate CI consumes (audit-ci). Also SURFACES (never
    fails on) recorded `--skip-freeze` crossings, so a skipped freeze is visible in review.
    Writes NOTHING; every other command is byte-identical."""
    root = _require_root()
    state = load_state(root)
    checked, findings = _audit_findings(root, state)
    skips = _freeze_skip_notices(state)
    glints = _guarantee_lint_notices(root, state)
    if getattr(args, "json", False):
        print(json.dumps({"checked": checked, "findings": findings, "freeze_skips": skips,
                          "guarantee_lints": glints}, ensure_ascii=False, indent=2))
    else:
        for x in findings:
            print(f"audit: {x['code']} {x['task']} — {x['detail']}")
        for s in skips:
            print(f"audit: freeze_skipped {s['task']} — crossed tests->build with a DRAFT §3 "
                  f"(by {s['by']} at {s['at']})")
        for slug in glints["shallow"]:
            print(f"audit: shallow_deep_check {slug} — §6 Deep-checks block unfilled "
                  f"(a shallow verify, not a pass)")
        if glints["risk_unset"]:
            rs = glints["risk_unset"]
            print(f"audit: risk_unset — {len(rs)} task(s) reached verify with no risk: "
                  f"declaration: {', '.join(rs)}")
        if glints["refute_unrecorded"]:
            ru = glints["refute_unrecorded"]
            print(f"audit: refute_unrecorded — {len(ru)} task(s): {', '.join(ru)} "
                  f"— record the earned-green refute verdict (§6); a spot-audit is the backstop")
        if glints["advisor_verdict_unrecorded"]:
            av = glints["advisor_verdict_unrecorded"]
            print(f"audit: advisor_verdict_unrecorded — {len(av)} task(s): {', '.join(av)} "
                  f"— record the 3-lens advisor verdict (§6); a spot-audit is the backstop")
        if glints["rule_coverage_gap"]:
            rc = glints["rule_coverage_gap"]
            print(f"audit: rule_coverage_gap — {len(rc)} task(s): {', '.join(rc)} "
                  f"— a §1 Must/Reject has no §2 scenario tag or §4 covers: line "
                  f"(run `add.py check` for the per-rule detail)")
        if glints["sensitivity_unset"]:
            su = glints["sensitivity_unset"]
            print(f"audit: sensitivity_unset — {len(su)} task(s) reached verify with no "
                  f"sensitivity: declaration: {', '.join(su)}")
        if glints["advisor_reviewer_is_author"]:
            ar = glints["advisor_reviewer_is_author"]
            print(f"audit: advisor_reviewer_is_author — {len(ar)} task(s): {', '.join(ar)} "
                  f"— advisor and gate actor are the same identity")
        if glints["advisor_residue_on_mechanical_mis_tier"]:
            am = glints["advisor_residue_on_mechanical_mis_tier"]
            print(f"audit: advisor_residue_on_mechanical_mis_tier — {len(am)} task(s): "
                  f"{', '.join(am)} — mechanical tier with non-none residue and PASS verdict "
                  f"is incoherent; consider re-tiering")
        if glints["contract_report_unrecorded"]:
            cr = glints["contract_report_unrecorded"]
            print(f"audit: contract_report_unrecorded — {len(cr)} task(s): {', '.join(cr)} "
                  f"— record the rendered freeze report (§3 `Reported: yes`); a spot-audit is the backstop")
        if glints["verify_report_unrecorded"]:
            vr = glints["verify_report_unrecorded"]
            print(f"audit: verify_report_unrecorded — {len(vr)} task(s): {', '.join(vr)} "
                  f"— record the rendered gate report (§6 `Reported: yes`); a spot-audit is the backstop")
        if not findings and not skips and not glints["shallow"] and not glints["risk_unset"] \
                and not glints["refute_unrecorded"] and not glints["advisor_verdict_unrecorded"] \
                and not glints["sensitivity_unset"] \
                and not glints["advisor_reviewer_is_author"] \
                and not glints["advisor_residue_on_mechanical_mis_tier"] \
                and not glints["rule_coverage_gap"] \
                and not glints["contract_report_unrecorded"] \
                and not glints["verify_report_unrecorded"]:
            print(f"audit: clean ({checked} tasks checked)")
    # MEASURE-NOT-BLOCK: only real findings raise the exit code; notices never do.
    if findings:
        sys.exit(1)


def _retro_carried(path: Path) -> int:
    """Parse the 'LEARNINGS (N carried)' count from a RETRO.md; absent/unreadable -> 0.
    READ-ONLY (the graduation harvest's carried-delta facet for the consolidated tier)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return 0
    m = re.search(r"LEARNINGS \((\d+) carried\)", text)
    return int(m.group(1)) if m else 0


def graduation_data(root: Path, state: dict) -> dict:
    """The single source of FACTS for the graduation harvest — PURE, NO writes (mirrors
    report_data). Both the `graduation-report` text dashboard and `--json` render from this
    one dict, so the human view and the machine view can never disagree.

    GATHER, never JUDGE: every value is a RECORD the human verifies by looking; there is no
    readiness/score/ranking field by construction (would_be_judging is structurally impossible).
    Two tiers: LIVE = in-state (state + on-disk TASK.md); CONSOLIDATED = compacted milestones,
    a RETRO record only. A missing/unreadable source is SKIPPED, never a crash (fail-closed)."""
    tasks = state.get("tasks") or {}
    milestones = state.get("milestones") or {}
    archived = state.get("archived") or []

    # a — open deltas by competency (reuse the project-wide harvester; compacted folded out)
    by_comp = _collect_open_deltas(root)
    open_deltas = {"total": sum(len(v) for v in by_comp.values()),
                   "by_competency": {c: v for c, v in by_comp.items() if v}}

    # b — open RISK-ACCEPTED waivers, soonest expiry first (missing/unparseable expiry sorts LAST)
    waivers = []
    for slug, t in tasks.items():
        if t.get("gate") == "RISK-ACCEPTED" and t.get("waiver"):
            w = t["waiver"]
            waivers.append({"slug": slug, "owner": w.get("owner", "?"),
                            "ticket": w.get("ticket", "?"), "expires": w.get("expires", "?")})

    def _exp_key(wv):
        try:
            return (0, date.fromisoformat(wv["expires"]).isoformat())
        except (ValueError, TypeError):
            return (1, "")          # unparseable/missing -> after every real date
    waivers.sort(key=_exp_key)

    # c — RETRO records: LIVE under milestones/, CONSOLIDATED under archive/ (the compacted backbone)
    retros = []
    for sub_dir, tier in ((root / "milestones", "live"), (root / "archive", "consolidated")):
        if sub_dir.is_dir():
            for retro in sorted(sub_dir.glob("*/RETRO.md")):
                if retro.is_file():     # a directory at the path is not a ledger (fail-closed)
                    retros.append({"milestone": retro.parent.name,
                                   "path": str(retro.relative_to(root)),
                                   "carried_deltas": _retro_carried(retro), "tier": tier})

    # d-i — residue gate records: the residue-class facet (RISK-ACCEPTED shares the waivers[] record)
    residue_gates = [{"slug": s, "gate": t.get("gate")} for s, t in tasks.items()
                     if t.get("gate") in ("RISK-ACCEPTED", "HARD-STOP")]

    # d-ii — §6 disclosed residue: in-state tasks' '- [⚠]' VERIFY list items (the pinned rule)
    # e   — coverage-gaps proxy: in-state §7 Watch still the '<error rate' placeholder head
    residue_disclosed, coverage_gaps = [], []
    for slug in tasks:
        try:
            text = (root / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")
        except OSError:
            continue                 # unreadable TASK.md -> skip this task's prose records
        m = re.search(r"##\s*6\b.*?(?=\n##\s*\d|\Z)", text, re.S)   # the VERIFY section only
        for line in (m.group(0) if m else "").splitlines():
            st = line.strip()
            if st.startswith("- [⚠]"):
                residue_disclosed.append({"slug": slug, "line": st[len("- [⚠]"):].strip()})
        for line in text.splitlines():
            if line.startswith("Watch") and "<error rate" in line:  # unfilled <…> template head
                coverage_gaps.append({"slug": slug})
                break

    return {
        "open_deltas": open_deltas,
        "waivers": waivers,
        "retros": retros,
        "residue_gates": residue_gates,
        "residue_disclosed": residue_disclosed,
        "coverage_gaps": coverage_gaps,
        "summary": {
            "open_deltas": open_deltas["total"], "waivers": len(waivers), "retros": len(retros),
            "residue_gates": len(residue_gates), "residue_disclosed": len(residue_disclosed),
            "coverage_gaps": len(coverage_gaps),
            "milestones_live": len(milestones), "milestones_consolidated": len(archived),
        },
    }


def cmd_graduation_report(args: argparse.Namespace) -> None:
    """Read-only: GATHER the MVP loop's evidence into five labeled record-sets for the
    graduate.md interview. text (default) or --json (the frozen JSON facts interface). Exit 0 ALWAYS —
    a gather, not a gate; the ONLY non-zero exit is no_project. Judges nothing. NO writes."""
    root = find_root()
    if root is None:                 # frozen contract: fail-closed with a no_project signal
        _die("no_project: no .add/ project found. Run `add.py init` first.")
    state = load_state(root)
    d = graduation_data(root, state)

    if getattr(args, "json", False):
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return

    s = d["summary"]
    L = ["GRADUATION REPORT — MVP-loop evidence (gather, not judge)", ""]
    L.append(f"Open deltas ({s['open_deltas']}) — unfolded lessons by competency:")
    for comp, entries in d["open_deltas"]["by_competency"].items():
        for e in entries:
            L.append(f"  - [{comp}] {e['text']}  [{e['task']}]")
    L.append("")
    L.append(f"Waivers ({s['waivers']}) — open RISK-ACCEPTED, soonest expiry first:")
    for w in d["waivers"]:
        L.append(f"  - {w['slug']}: {w['owner']} · {w['ticket']} · expires {w['expires']}")
    L.append("")
    _live_retros = sum(1 for r in d["retros"] if r["tier"] == "live")
    _cons_retros = s["retros"] - _live_retros
    L.append(f"RETRO records ({s['retros']}: {_live_retros} live · {_cons_retros} consolidated) — "
             f"milestones: {s['milestones_live']} live · "
             f"{s['milestones_consolidated']} represented by RETRO record:")
    for r in d["retros"]:
        L.append(f"  - {r['milestone']} [{r['tier']}]: {r['path']} ({r['carried_deltas']} carried)")
    L.append("")
    L.append(f"Verify residue — gate records ({s['residue_gates']}, RISK-ACCEPTED/HARD-STOP):")
    for g in d["residue_gates"]:
        L.append(f"  - {g['slug']}: {g['gate']}")
    L.append(f"Verify residue — disclosed §6 lines ({s['residue_disclosed']}):")
    for r in d["residue_disclosed"]:
        L.append(f"  - {r['slug']}: {r['line']}")
    L.append("")
    L.append(f"Coverage gaps ({s['coverage_gaps']}) — PROXY (monitor not declared; §7 Watch unfilled):")
    for c in d["coverage_gaps"]:
        L.append(f"  - {c['slug']}")
    print("\n".join(L))


def _released_milestones(root: Path) -> set[str]:
    """Slugs already attributed to a release — the union of every `milestones:` row in
    RELEASES.md. Fail-OPEN: a missing/unreadable/malformed ledger yields the empty set, so
    every closed milestone reads as still-releasable (a vanished ledger never hides work).
    READ-ONLY."""
    try:
        text = _releases_path(root).read_text(encoding="utf-8")
    except OSError:
        return set()                         # no ledger (or a dir at the path) -> nothing released yet
    out: set[str] = set()
    for line in text.splitlines():
        st = line.strip()
        if st.lower().startswith("milestones:"):
            for tok in re.split(r"[,\s]+", st.split(":", 1)[1]):
                tok = tok.strip()
                if tok and tok.lower() != "none":
                    out.add(tok)
    return out


def _releasable(root: Path, state: dict) -> list[dict]:
    """Closed milestones NOT yet attributed to any RELEASES.md row — the cut's candidate
    bundle. Drives BOTH the `→ releasable: N` status cue and release-report. READ-ONLY."""
    released = _released_milestones(root)
    return [m for m in _closed_milestones(state) if m["slug"] not in released]


def _released_loose_tasks(root: Path) -> set[str]:
    """Slugs already attributed to a release as LOOSE tasks — the union of every
    `loose tasks:` row in RELEASES.md. The exact parallel of _released_milestones:
    fail-OPEN (a missing/unreadable/malformed ledger yields the empty set, so every
    done loose task reads as still-releasable). READ-ONLY."""
    try:
        text = _releases_path(root).read_text(encoding="utf-8")
    except OSError:
        return set()                         # no ledger -> nothing released yet
    out: set[str] = set()
    for line in text.splitlines():
        st = line.strip()
        if st.lower().startswith("loose tasks:"):
            for tok in re.split(r"[,\s]+", st.split(":", 1)[1]):
                tok = tok.strip()
                if tok and tok.lower() != "none":
                    out.add(tok)
    return out


def _releasable_loose_tasks(root: Path, state: dict) -> list[dict]:
    """Done milestone-free tasks NOT yet attributed to any RELEASES.md `loose tasks:` row —
    the loose half of the cut's candidate bundle, peer to _releasable. A loose task is a
    first-class releasable item: milestone-free (a standalone, fast OR full) AND done (a
    completing gate). Drives the loose status cue + release_data["loose"]. READ-ONLY."""
    released = _released_loose_tasks(root)
    out: list[dict] = []
    for slug, t in (state.get("tasks") or {}).items():
        if (isinstance(t, dict) and t.get("milestone") is None and _task_done(t)
                and slug not in released):
            out.append({"slug": slug, "title": t.get("title", slug)})
    return out


def release_data(root: Path, state: dict) -> dict:
    """The single source of FACTS for a release cut — PURE, NO writes (mirrors graduation_data).
    Both the `release-report` text dashboard and `--json` render from this one dict, so the human
    view and the machine view can never disagree.

    GATHER, never JUDGE: every value is a RECORD the human verifies by looking; there is no
    readiness/score/ranking field by construction. Five record-sets feed the release.md flow:
      releasable — closed-but-unreleased milestones (the bundle candidate; the cue's count)
      changed    — per releasable milestone: RETRO path + carried-delta count + §Key-Decisions rows
      waivers    — open RISK-ACCEPTED riding into the cut (soonest expiry first)
      blockers   — open HARD-STOP gate records (the security stop the floor will refuse on)
      monitors   — declared §7 Watch lines to carry into the post-cut watch step
    A source is read fail-closed (skip on error); the ledger is read fail-OPEN (see _releasable)."""
    tasks = state.get("tasks") or {}
    releasable = _releasable(root, state)

    # changed — the consolidated learning trail per releasable milestone (the changelog source)
    changed = []
    for m in releasable:
        slug = m["slug"]
        retro = None
        for sub in ("milestones", "archive"):
            cand = root / sub / slug / "RETRO.md"
            if cand.is_file():               # a directory at the path is not a ledger (fail-closed)
                retro = str(cand.relative_to(root))
                break
        changed.append({"milestone": slug, "key_decisions": _key_decisions_for(root, slug),
                        "retro": retro,
                        "carried_deltas": _retro_carried(root / retro) if retro else 0})

    # waivers — open RISK-ACCEPTED riding into the cut, soonest expiry first (mirrors graduation_data)
    waivers = []
    for slug, t in tasks.items():
        if t.get("gate") == "RISK-ACCEPTED" and t.get("waiver"):
            w = t["waiver"]
            waivers.append({"slug": slug, "owner": w.get("owner", "?"),
                            "ticket": w.get("ticket", "?"), "expires": w.get("expires", "?")})

    def _exp_key(wv):
        try:
            return (0, date.fromisoformat(wv["expires"]).isoformat())
        except (ValueError, TypeError):
            return (1, "")                   # unparseable/missing -> after every real date
    waivers.sort(key=_exp_key)

    # blockers — open HARD-STOP gate records (the un-forceable security stop the floor enforces)
    blockers = [{"slug": s, "gate": t.get("gate")} for s, t in tasks.items()
                if t.get("gate") == "HARD-STOP"]

    # monitors — declared §7 Watch lines (filled, not the `<…>` template) for the watch step
    monitors = []
    for slug in tasks:
        try:
            text = (root / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")
        except OSError:
            continue                         # unreadable TASK.md -> skip this task's monitor record
        for line in text.splitlines():
            st = line.strip()
            if st.startswith("Watch") and "<" not in st and st != "Watch":
                monitors.append({"slug": slug, "watch": st})
                break

    # loose — done milestone-free tasks not yet attributed (the cut's loose bundle, peer to releasable)
    loose = _releasable_loose_tasks(root, state)

    # open_spec_deltas — unresolved SPEC deltas riding into the cut (the forceable floor's count
    # source; one record-set so the floor + release-report can never disagree). GATHER, never judge.
    # LIVE-only: a SPEC delta blocks the cut only while its task is in active state. Archived tasks
    # are PASS-done history (their deltas stay preserved + visible PROJECT-WIDE in `add.py deltas` /
    # the `status` cue, but never block a fresh release — they cannot be cleared by the live-scoped
    # carry/drop verbs). This makes the floor count == the set the CLI can actually drain.
    live_tasks = state.get("tasks") or {}
    open_deltas = [d for d in _collect_open_spec_deltas(root) if d["task"] in live_tasks]

    return {
        "releasable": releasable,
        "changed": changed,
        "waivers": waivers,
        "blockers": blockers,
        "monitors": monitors,
        "loose": loose,
        "open_spec_deltas": {"count": len(open_deltas),
                             "items": [{"task": d["task"], "text": d["text"]} for d in open_deltas]},
        "summary": {
            "releasable": len(releasable), "changed": len(changed), "waivers": len(waivers),
            "blockers": len(blockers), "monitors": len(monitors), "loose": len(loose),
            "open_spec_deltas": len(open_deltas),
        },
    }


def cmd_release_report(args: argparse.Namespace) -> None:
    """Read-only: GATHER the release inventory into five labeled record-sets for the release.md
    flow. text (default) or --json (the frozen JSON facts interface). Exit 0 ALWAYS — a gather,
    not a gate; the ONLY non-zero exit is no_project. Judges nothing. NO writes."""
    root = find_root()
    if root is None:                 # frozen contract: fail-closed with a no_project signal
        _die("no_project: no .add/ project found. Run `add.py init` first.")
    state = load_state(root)
    d = release_data(root, state)

    if getattr(args, "json", False):
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return

    s = d["summary"]
    L = ["RELEASE REPORT — release inventory (gather, not judge)", ""]
    L.append(f"Releasable ({s['releasable']}) — closed milestones not yet in {RELEASES_FILE}:")
    for m in d["releasable"]:
        L.append(f"  - {m['slug']} [{m['tier']}]: {m['title']}")
    L.append("")
    L.append(f"Changed ({s['changed']}) — the consolidated learning trail per milestone:")
    for c in d["changed"]:
        L.append(f"  - {c['milestone']}: {c['retro'] or '(no RETRO record)'} "
                 f"({c['carried_deltas']} carried · {len(c['key_decisions'])} key decision(s))")
    L.append("")
    L.append(f"Waivers ({s['waivers']}) — open RISK-ACCEPTED riding into the cut, soonest expiry first:")
    for w in d["waivers"]:
        L.append(f"  - {w['slug']}: {w['owner']} · {w['ticket']} · expires {w['expires']}")
    L.append("")
    L.append(f"Blockers ({s['blockers']}) — open HARD-STOP (the un-forceable security stop):")
    for b in d["blockers"]:
        L.append(f"  - {b['slug']}: {b['gate']}")
    L.append("")
    L.append(f"Monitors ({s['monitors']}) — declared §7 Watch lines to carry into the watch step:")
    for mo in d["monitors"]:
        L.append(f"  - {mo['slug']}: {mo['watch']}")
    print("\n".join(L))


def _prepend_block(existing: str, header: str, block: str) -> str:
    """Newest-first prepend: insert `block` directly under the top H1 `header`, creating the
    header when `existing` is empty / headerless. Existing content is preserved VERBATIM
    (append-only). `block` is expected to end in a blank-line separator."""
    if not existing.strip():
        return f"{header}\n\n{block}"
    if existing.lstrip().startswith(header):
        after = existing.split(header, 1)[1].lstrip("\n")
        return f"{header}\n\n{block}{after}"
    return f"{block}{existing}"               # no recognized header -> block goes on top, verbatim tail


def cmd_release(args: argparse.Namespace) -> None:
    """GUARDED, record-only: cut a version. Enforce the 4-code readiness floor, then RECORD by
    prepending CHANGELOG.md + an append-only RELEASES.md row (whose `milestones:` line attributes
    the bundle). The engine RECORDS; it NEVER tags / publishes / deploys / bumps a version source /
    writes state.json. Validate-before-write: a reject leaves both files + state.json byte-unchanged.
    A failed second write rolls back the first (release_write_failed)."""
    root = find_root()
    if root is None:                 # frozen contract: fail-closed with a no_project signal
        _die("no_project: no .add/ project found. Run `add.py init` first.")
    state = load_state(root)
    d = release_data(root, state)
    forced = getattr(args, "force", False)
    disclosed = getattr(args, "with_waivers", False)

    # ── FLOOR — all checks BEFORE any write (validate-before-write) ──────────────────────────
    if d["blockers"]:                # the UN-FORCEABLE reject — security is never shipped
        _die("release_security_open: an open HARD-STOP blocks the cut — a security finding is "
             "never shipped. Resolve it (a change request back to Specify) before releasing. "
             "--force does NOT override this.")
    if not forced and _build_in_flight(state):
        _die("release_build_in_flight: a build is in flight without a recorded green gate — finish "
             "and gate it first, or pass --force to override.")
    bundle = _releasable(root, state)
    loose_bundle = _releasable_loose_tasks(root, state)
    if not forced and not bundle and not loose_bundle:
        _die("release_no_closed_milestone: nothing closed-and-unreleased to bundle — the cut "
             "would be a no-op. Close a milestone (or a standalone task) first, or pass --force "
             "to override.")
    if not forced and d["waivers"] and not disclosed:
        _die("release_undisclosed_waiver: a RISK-ACCEPTED waiver rides into this release — pass "
             "--with-waivers to disclose it in the notes, or --force to override.")
    open_spec = d["open_spec_deltas"]["count"]
    if not forced and open_spec > 0:
        _die(f"release_open_spec_deltas: {open_spec} open SPEC delta(s) unresolved — drain them "
             "first (carry-delta / new-task --from-delta / drop-delta; see `add.py deltas`), or "
             "pass --force to cut anyway (they ride into the release unresolved). Unlike "
             "release_security_open, this floor IS forceable.")

    # ── RECORD — build both contents in memory, then write CHANGELOG, then RELEASES (commit) ──
    day = date.today().isoformat()
    changed_by_slug = {c["milestone"]: c for c in d["changed"]}
    waiver_slugs = [w["slug"] for w in d["waivers"]] if disclosed else []
    changelog_path = root.parent / "CHANGELOG.md"
    releases_path = _releases_path(root)
    cl_before = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else None
    rel_before = releases_path.read_text(encoding="utf-8") if releases_path.exists() else ""
    new_cl = _prepend_block(cl_before or "", "# Changelog",
                            _render_changelog_block(args.version, day, bundle, changed_by_slug))
    new_rel = _prepend_block(rel_before, "# Releases",
                             _render_releases_row(args.version, day, bundle, waiver_slugs,
                                                  getattr(args, "evidence", None),
                                                  identity._render_actor_line(state), loose_bundle))
    # milestone-release-backlink: STAMP each bundled milestone's MILESTONE.md `release:` line to
    # the cut version. Built in memory NOW and appended to the SAME atomic batch as the ledgers,
    # so the stamp commits all-or-nothing with them (a failed write rolls back everything). Only
    # `bundle` (closed-and-unreleased) milestones are stamped; a missing/unreadable file is skipped
    # (degrade-safe — the ledger attribution stays the source of truth).
    stamp_writes: list[tuple[Path, str]] = []
    for m in bundle:
        mfile = root / "milestones" / m["slug"] / "MILESTONE.md"
        try:
            _mtxt = mfile.read_text(encoding="utf-8")
        except OSError:
            continue
        _stamped = _set_release_line(_mtxt, args.version)
        if _stamped != _mtxt:
            stamp_writes.append((mfile, _stamped))
    try:                                              # CHANGELOG + RELEASES + milestone stamps: one all-or-nothing commit
        _atomic_write_many([(changelog_path, new_cl), (releases_path, new_rel)] + stamp_writes)
    except OSError as e:
        _die(f"release_write_failed: the ledger write failed ({e}); nothing was recorded — both "
             "files were rolled back to their prior content. Retry the release.")

    # NO save_state — attribution lives in RELEASES.md (the cue re-reads it), never state.json
    ms = ", ".join(m["slug"] for m in bundle) if bundle else "none"
    lt = ", ".join(t["slug"] for t in loose_bundle) if loose_bundle else "none"
    print(f"released {args.version} — recorded {len(bundle)} milestone(s): {ms} "
          f"+ {len(loose_bundle)} loose task(s): {lt}")
    print("  CHANGELOG.md + RELEASES.md updated (project root). The engine records; "
          "you run the tag / publish / deploy.")
    if forced:
        print("  (--force: forceable floor rejects were bypassed — release_security_open is never bypassable)")
    print(_next_footer(root, state))


def cmd_deltas(args: argparse.Namespace) -> None:
    """Read-only: report open competency lessons AND open SPEC deltas, SEPARATELY — plus, with
    `--carried`/`--all`, the carried (deferred, non-lossy) SPEC deltas as a RETRIEVAL surface.

    Scans every .add/tasks/*/TASK.md: '### Competency deltas' → open lessons grouped by competency
    (DDD·SDD·UDD·TDD·ADD), and '### Spec delta' → open forward hand-offs in their own section (a SPEC
    delta resolves into a task, never consolidates). `--carried` lists the carried deltas (re-activate
    via `reopen-delta`); `--all` shows open + carried. Bare output is BYTE-IDENTICAL to before.
    --json emits one object (carried keys only when requested). Exit 0 ALWAYS. Writes NOTHING."""
    root = _require_root()
    by_comp = _collect_open_deltas(root)
    total = sum(len(v) for v in by_comp.values())
    spec = _collect_open_spec_deltas(root)
    only_carried = getattr(args, "carried", False)
    want_carried = only_carried or getattr(args, "all", False)
    want_open = not only_carried                          # --carried hides open; --all keeps it
    carried = _collect_carried_spec_deltas(root) if want_carried else []

    if getattr(args, "json", False):
        payload: dict = {
            "total": total,
            "by_competency": {c: v for c, v in by_comp.items() if v},
            "spec": spec,
            "spec_total": len(spec),
        }
        if want_carried:
            payload["carried"] = carried
            payload["carried_total"] = len(carried)
        print(json.dumps(payload, ensure_ascii=False))
        return

    printed = False
    if want_open:
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
    if want_carried:
        if carried:
            print(f"carried spec deltas ({len(carried)} total — reopen via add.py reopen-delta):")
            for e in carried:
                print(f"    - {e['text']}  [{e['task']}]")
            printed = True
        elif only_carried:                                # --carried alone, nothing carried
            print("no carried spec deltas.")
            printed = True
    if not printed:
        print("no open deltas.")


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
                           "unlocks": "", "decide": _decide_next(state, d)}
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


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="add.py", description="ADD scaffolder + state tracker")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("init", help="create a .add/ project here")
    pi.add_argument("--dir", default=".", help="target directory (default: cwd)")
    pi.add_argument("--name", default=None, help="project name (default: dir name)")
    pi.add_argument("--stage", default="prototype", choices=STAGES)
    pi.add_argument("--force", action="store_true", help="reset state.json if present")
    pi.add_argument("--await-lock", dest="await_lock", action="store_true",
                    help="seed an unlocked setup; gates new-task/advance/gate until `add.py lock`")
    pi.add_argument("--rule-file", dest="rule_file", action="store_true",
                    help="write the ADD block to .claude/rules/add-workflows.md and reference it "
                         "from CLAUDE.md (auto-on for ccsk projects with a .ccsk/ dir)")
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
    pfz.add_argument("--by", default=None, help="approver name (default: the resolved actor)")
    pfz.set_defaults(func=cmd_freeze)

    pwho = sub.add_parser("whoami",
                          help="show / set the git-native actor (git config -> OS user; --name to override)")
    # --name (set) and --unset (clear) are mutually exclusive — argparse rejects the
    # contradiction (exit 2) before any state read, so neither silently wins.
    pwho_mut = pwho.add_mutually_exclusive_group()
    pwho_mut.add_argument("--name", default=None, help="set an actor override (name)")
    pwho_mut.add_argument("--unset", action="store_true", help="clear the actor override")
    pwho.add_argument("--email", default=None, help="set the override email (with --name)")
    pwho.add_argument("--json", action="store_true", help="emit one JSON object instead of text")
    pwho.set_defaults(func=cmd_whoami)

    pas = sub.add_parser("assign",
                         help="assign an owner/assignee to a task or milestone (no flag = self)")
    pas.add_argument("slug")
    pas.add_argument("--owner", default=None, metavar="\"Name <email>\"",
                     help="set the accountable owner (default with no flag: self)")
    pas.add_argument("--assignee", default=None, metavar="\"Name <email>\"",
                     help="set the working assignee (default with no flag: self)")
    pas.set_defaults(func=cmd_assign)

    pun = sub.add_parser("unassign",
                         help="clear the owner/assignee of a task or milestone (no flag = both)")
    pun.add_argument("slug")
    pun.add_argument("--owner", action="store_true", help="clear only the owner")
    pun.add_argument("--assignee", action="store_true", help="clear only the assignee")
    pun.set_defaults(func=cmd_unassign)

    pn = sub.add_parser("new-task", help="scaffold a new task (TASK.md + tests/ + src/)")
    pn.add_argument("slug")
    pn.add_argument("--title", default=None)
    pn.add_argument("--milestone", default=None, help="attach to a milestone (default: active)")
    pn.add_argument("--depends-on", dest="depends_on", default=None,
                    help="comma-separated task slugs this task depends on")
    pn.add_argument("--from-delta", dest="from_delta", default=None, metavar="PRIOR",
                    help="SEED PRIOR's open SPEC delta into this task (pre-fills §1 "
                         "Feature, flips the source -> [SPEC · seeded] [→ this])")
    pn.add_argument("--match", default=None, metavar="SUBSTR",
                    help="with --from-delta: target the UNIQUE open SPEC delta whose text "
                         "contains SUBSTR (case-insensitive) instead of the first")
    pn.add_argument("--force", action="store_true", help="overwrite TASK.md if present")
    pn.add_argument("--fast", action="store_true",
                    help="opt into the fast lane: scaffold the minimal TASK.fast.md template + "
                         "hold the task to the freeze floor under any milestone")
    pn.set_defaults(func=cmd_new_task)

    pdd = sub.add_parser("drop-delta",
                         help="dismiss a task's open SPEC delta -> [SPEC · dropped]")
    pdd.add_argument("slug", help="task whose open SPEC delta to drop")
    pdd.add_argument("--match", default=None, metavar="SUBSTR",
                     help="target the UNIQUE open SPEC delta whose text contains SUBSTR "
                          "(case-insensitive) instead of the first")
    pdd.set_defaults(func=cmd_drop_delta)

    pcd = sub.add_parser("carry-delta",
                         help="defer a task's open SPEC delta non-lossily -> [SPEC · carried]")
    pcd.add_argument("slug", help="task whose open SPEC delta to carry (defer)")
    pcd.add_argument("--reason", default=None, metavar="TEXT",
                     help="REQUIRED — why it is deferred (the breadcrumb a future loop reads)")
    grp = pcd.add_mutually_exclusive_group()
    grp.add_argument("--match", default=None, metavar="SUBSTR",
                     help="target the UNIQUE open SPEC delta whose text contains SUBSTR "
                          "(case-insensitive) instead of the first")
    grp.add_argument("--all", action="store_true",
                     help="carry EVERY open SPEC delta in the task")
    pcd.set_defaults(func=cmd_carry_delta)

    prd = sub.add_parser("reopen-delta",
                         help="re-activate a carried SPEC delta -> [SPEC · open]")
    prd.add_argument("slug", help="task whose carried SPEC delta to reopen")
    prd.add_argument("--match", default=None, metavar="SUBSTR",
                     help="target the UNIQUE carried SPEC delta whose text contains SUBSTR "
                          "(case-insensitive) instead of the first")
    prd.set_defaults(func=cmd_reopen_delta)

    pm = sub.add_parser("new-milestone", help="scaffold a milestone (SDD living doc)")
    pm.add_argument("slug")
    pm.add_argument("--title", default=None)
    pm.add_argument("--goal", default=None, help="one-sentence outcome")
    pm.add_argument("--stage", default="mvp", choices=STAGES)
    pm.add_argument("--force", action="store_true", help="overwrite MILESTONE.md if present")
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

    pr = sub.add_parser("ready", help="list tasks whose dependencies are satisfied")
    pr.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pr.set_defaults(func=cmd_ready)

    pwa = sub.add_parser("waves", help="read-only DAG schedule of a milestone: topological "
                                       "waves + critical path + advisory tier hint")
    pwa.add_argument("--milestone", default=None,
                     help="milestone slug to schedule (default: the active milestone)")
    pwa.add_argument("--merge", action="store_true",
                     help="unify the active SET into ONE schedule (cross-milestone deps order, not block)")
    pwa.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pwa.set_defaults(func=cmd_waves)

    pdp = sub.add_parser("dag-plan", help="record a committed snapshot of the milestone's computed "
                                          "DAG schedule (waves + critical path + tiers) + a freshness "
                                          "check vs the live depends_on edges")
    pdp.add_argument("--milestone", default=None,
                     help="milestone slug to snapshot (default: the active milestone)")
    pdp.set_defaults(func=cmd_dag_plan)

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

    pco = sub.add_parser("compact",
                         help="heavy archive: move an archived milestone's files into "
                              ".add/archive/<slug>/ (recoverable reverse move)")
    pco.add_argument("slug")
    pco.add_argument("--force", action="store_true",
                     help="compact past an unrelated open SPEC delta (the open_spec_deltas_unresolved "
                          "guard ONLY; never a structural reject) — bypass is warned + recorded")
    pco.set_defaults(func=cmd_compact)

    pp = sub.add_parser("phase", help="set a task's phase explicitly")
    pp.add_argument("phase", choices=PHASES)
    pp.add_argument("slug", nargs="?", default=None)
    pp.add_argument("--skip-freeze", action="store_true",
                    help="cross tests->build on a DRAFT §3, recording an auditable freeze_skipped "
                         "marker (the universal freeze gate's only bypass; never auto-freezes §3)")
    pp.set_defaults(func=cmd_phase, _opt_positionals=("slug",))

    pa = sub.add_parser("advance", help="move a task to the next phase")
    pa.add_argument("slug", nargs="?", default=None)
    pa.add_argument("--skip-freeze", action="store_true",
                    help="cross tests->build on a DRAFT §3, recording an auditable freeze_skipped "
                         "marker (the universal freeze gate's only bypass; never auto-freezes §3)")
    pa.set_defaults(func=cmd_advance, _opt_positionals=("slug",))

    pg = sub.add_parser("gate", help="record a verify gate outcome")
    pg.add_argument("outcome", choices=GATES)
    pg.add_argument("slug", nargs="?", default=None)
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

    pst = sub.add_parser("streams", help="show or set the project streams posture (parallel|sequential)")
    pst.add_argument("action", nargs="?", choices=("show", "set"), default="show")
    pst.add_argument("posture", nargs="?", default=None, help="set: <parallel|sequential>")
    pst.set_defaults(func=cmd_streams, _opt_positionals=("posture",))

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
    pr.add_argument("--to", default=None, help="target phase (ground..observe)")
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
    pst.set_defaults(func=cmd_status)

    pck = sub.add_parser("check", help="read-only integrity check of the .add project")
    pck.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pck.set_defaults(func=cmd_check)

    pcomp = sub.add_parser("components",
                           help="read-only: print + validate the component registry "
                                "(.add/components.toml) — RED integrity errors + schema-lint typo warnings")
    pcomp.set_defaults(func=cmd_components)

    psrch = sub.add_parser("search", help="keyword/substring search over the "
                            "milestone/task corpus (active + archived) — "
                            "title/goal/rationale lines only, never the full body")
    psrch.add_argument("keywords", nargs="+", metavar="KEYWORD",
                       help="one or more keywords (case-insensitive substring, OR-combined)")
    psrch.add_argument("--json", action="store_true", help="machine-readable JSON output")
    psrch.set_defaults(func=cmd_search)

    pfed = sub.add_parser("federate", help="multi-repo: pull a producer repo's published, immutable "
                                           "contract snapshot into this repo (fail-loud)")
    pfedsub = pfed.add_subparsers(dest="action", required=True)
    pfedpull = pfedsub.add_parser("pull", help="land [federation.<id>].source at the local "
                                               ".add/contracts/<id>.json (hard-stops on a bad source)")
    pfedpull.add_argument("id", help="the contract id declared under [federation.<id>]")
    pfedpull.set_defaults(func=cmd_federate)

    pdoc = sub.add_parser("doctor", help="read-only diagnosis of state.json integrity + "
                                         "referential consistency (run after a git merge)")
    pdoc.set_defaults(func=cmd_doctor)

    pmine = sub.add_parser("mine", help="read-only: my not-done tasks (owner or assignee) "
                                        "across all active milestones")
    pmine.add_argument("--actor", default=None, metavar="\"Name <email>\"",
                       help="inspect another actor's queue instead of your own")
    pmine.add_argument("--json", action="store_true", help="emit one JSON object instead of text")
    pmine.add_argument("--all", action="store_true",
                       help="widen past the active SET: every milestone + loose tasks, not just active")
    pmine.set_defaults(func=cmd_mine)

    pwv = sub.add_parser("wave-verify",
                         help="read-only merge-time gate: every WAVE.md roster echo must match "
                              "base (refuses unverified_fork_base) — run before the first merge-back")
    pwv.add_argument("milestone", nargs="?", default=None,
                     help="milestone whose WAVE.md to verify (default: the single live ledger)")
    pwv.set_defaults(func=cmd_wave_verify, _opt_positionals=("milestone",))

    psg = sub.add_parser("sync-guidelines",
                         help="(re)write the ADD guideline block into AGENTS.md + CLAUDE.md")
    psg.add_argument("--rule-file", dest="rule_file", action="store_true",
                     help="relocate CLAUDE.md's block to .claude/rules/add-workflows.md + reference "
                          "it (auto-on for ccsk projects)")
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
    pdt_g = pdt.add_mutually_exclusive_group()
    pdt_g.add_argument("--carried", action="store_true",
                       help="list the carried (deferred) SPEC deltas instead of the open ones")
    pdt_g.add_argument("--all", action="store_true",
                       help="list open AND carried SPEC deltas")
    pdt.set_defaults(func=cmd_deltas)

    pfo = sub.add_parser(_FOLD_VERB,
                         help="record one retrospective consolidation of open lessons into the "
                              "versioned foundation (stamp + route + version-bump, atomic)")
    pfo.add_argument("--task", help="narrow to one task's open lessons")
    pfo.add_argument("--comp", choices=_COMPETENCY_ORDER, help="narrow to one competency's open lessons")
    pfo.set_defaults(func=cmd_fold)

    pgr = sub.add_parser("graduation-report",
                         help="read-only: gather the MVP loop's evidence (deltas · waivers · RETROs · "
                              "residue · coverage gaps) for a graduation interview — gathers, never judges")
    pgr.add_argument("--json", action="store_true", help="emit the frozen JSON facts interface")
    pgr.add_argument("--plain", action="store_true", help="ASCII/pipe-safe text (output is plain by default)")
    pgr.set_defaults(func=cmd_graduation_report)

    prr = sub.add_parser("release-report",
                         help="read-only: gather the release inventory (releasable milestones · "
                              "changed/RETROs · waivers · HARD-STOP blockers · monitors) for a "
                              "release cut — gathers, never judges")
    prr.add_argument("--json", action="store_true", help="emit the frozen JSON facts interface")
    prr.add_argument("--plain", action="store_true", help="ASCII/pipe-safe text (output is plain by default)")
    prr.set_defaults(func=cmd_release_report)

    prl = sub.add_parser("release",
                         help="guarded, record-only: cut a version — enforce the readiness floor, "
                              "then prepend CHANGELOG.md + an append-only RELEASES.md row (the "
                              "engine records; you tag/publish). Security HARD-STOP is un-forceable")
    prl.add_argument("version", help="the version string to cut (free-form: semver / calver / any)")
    prl.add_argument("--force", action="store_true",
                     help="override the forceable floor rejects (NEVER release_security_open)")
    prl.add_argument("--with-waivers", action="store_true", dest="with_waivers",
                     help="disclose riding RISK-ACCEPTED waivers (records them on the ledger row)")
    prl.add_argument("--evidence", default=None, help="the RELEASES.md row's evidence line")
    prl.set_defaults(func=cmd_release)

    pau = sub.add_parser("audit",
                         help="read-only: verify recorded human decision points left well-formed records "
                              "(exit 1 on findings — the CI enforcement gate)")
    pau.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pau.set_defaults(func=cmd_audit)

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
    _maybe_nudge_update(args)        # advisory preamble; stderr-only, fail-open
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
