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
import json
import os
import re
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

# --- constants ---------------------------------------------------------------

ROOT_DIRNAME = ".add"
STATE_FILE = "state.json"
MILESTONE_FILE = "MILESTONE.md"
# The project GOAL (v20) is read live from PROJECT.md — never copied into state.json
# (single-source; the foundation is the truth). A missing/blank source degrades to
# this sentinel so the read-only orientation surfaces never blank or crash.
GOAL_UNSET = "(unset — add a 'goal:' line to PROJECT.md)"
STAGES = ("prototype", "poc", "mvp", "production")
# v22 stage-graduation: the read-only cue `status` shows when the MVP is covered.
# Worded as the ACTION (never a file) so it stands before graduate.md exists.
GRADUATION_CUE = "MVP covered → propose graduation"
PHASES = ("specify", "scenarios", "contract", "tests", "build", "verify", "observe", "done")
GATES = ("none", "PASS", "RISK-ACCEPTED", "HARD-STOP")

# --- independent verification (Generator–Verifier separation) ----------------
# In-context self-critique is unreliable: a model favours its own output
# (self-enhancement bias) and repeats its own errors, so an in-context
# "skeptic" approves it uncritically. The auto-gate decision is therefore computed by the
# engine from STRUCTURED verdicts produced by fresh, context-isolated verifier
# subagents (one per lens) — see skill/add/verify-critic.md. The engine validates
# shape and computes the deterministic decision; it never judges the code itself.
VERDICT_VALUES = ("pass", "fail", "risk")
VERIFY_LENSES = ("wiring", "concurrency-security", "contract-conformance")
MIN_CONSENSUS_LENSES = 3            # distinct lenses required for an auto-PASS (self-consistency)
VERDICT_LEDGER = "verdicts.jsonl"  # append-only, per-task; verdicts are durable, labelled data


def _phase_index(name: str) -> int:
    """Ordinal of a phase in PHASES; used to enforce forward-skip rules."""
    return PHASES.index(name)

# `add.py guide` copy: per-phase (concrete next action, book chapter to read).
# Keep the action wording aligned with each phase's EXIT line in the TASK template.
PHASE_GUIDE = {
    "specify":   ("state every rule — Must / Reject (+ named code) / After; rank assumptions lowest-confidence first and flag the biggest risk",
                  "03-step-1-specify.md"),
    "scenarios": ("write one Given/When/Then per Must AND per Reject; every result observable",
                  "04-step-2-scenarios.md"),
    "contract":  ("freeze the shape — signature, fields, error codes; names match the glossary",
                  "05-step-3-contract.md"),
    "tests":     ("write one failing test per scenario; run them RED for the right reason",
                  "06-step-4-tests.md"),
    "build":     ("write the minimum code to pass the tests; change no test and no contract",
                  "07-step-5-build.md"),
    "verify":    ("run the suite + non-functional checks, then record the gate",
                  "08-step-6-verify.md"),
    "observe":   ("note what to watch + the spec delta for the next loop",
                  "09-the-loop.md"),
    "done":      ("this task is done — pick the next feature",
                  "02-the-flow.md"),
}
# Phase -> who owns it, for the `--json` autonomy signal. An autonomous harness may run a
# phase only when owner=="ai" (stop is false); every other phase is a checkpoint. The map
# follows the book's who-does-what table (Verify is "human only"); `tests`/`build`/`observe`
# are AI-led. A phase missing here is `unmapped_phase` (fail closed) — never defaulted.
PHASE_OWNER = {
    "specify": "human", "scenarios": "human", "contract": "seam",
    "tests": "ai", "build": "ai", "verify": "human", "observe": "ai", "done": "human",
}
SETUP_FILES = ("PROJECT.md", "CONVENTIONS.md", "GLOSSARY.md", "MODEL_REGISTRY.md", "dependencies.allowlist")

# Guideline-injection targets + version-stable markers. NEVER change these marker
# strings: a re-run finds the old block by exact match, so changing them would
# orphan every block written by a prior version (see TASK guideline-inject).
GUIDELINE_FILES = ("AGENTS.md", "CLAUDE.md")
_GUIDE_BEGIN = "<!-- ADD:BEGIN — managed by `add.py sync-guidelines`; do not edit inside -->"
_GUIDE_END = "<!-- ADD:END -->"

# Minimal embedded fallback so the tool still works if templates/ is missing
# (circuit breaker: never hard-fail just because a template file was deleted).
_FALLBACK_TASK = """# TASK: {title}

slug: {slug} · created: {date} · stage: {stage}
phase: specify

## 1 · SPECIFY
Feature:
Framings weighed:
Must:
Reject:
After:
Assumptions — lowest-confidence first:
  ⚠ <most likely wrong> — lowest confidence because <why>; if wrong: <cost>

## 2 · SCENARIOS
## 3 · CONTRACT
Status: DRAFT
## 4 · TESTS
## 5 · BUILD
## 6 · VERIFY
### GATE RECORD
Outcome:
## 7 · OBSERVE
"""


# --- low-level IO (designed for failure: atomic, no silent clobber) ----------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _atomic_write(path: Path, text: str) -> None:
    """Write via a temp file in the same dir, then atomically replace.

    Avoids a half-written file if the process dies mid-write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _templates_dir() -> Path:
    return Path(__file__).resolve().parent / "templates"


def _render_template(name: str, **subs: str) -> str:
    """Load templates/<name>.tmpl and substitute {{key}} tokens.

    Falls back to a built-in minimal template only for TASK.md.
    """
    tmpl = _templates_dir() / f"{name}.tmpl"
    if tmpl.exists():
        text = tmpl.read_text(encoding="utf-8")
    elif name == "TASK.md":
        text = _FALLBACK_TASK.replace("{title}", "{{title}}").replace(
            "{slug}", "{{slug}}").replace("{date}", "{{date}}").replace("{stage}", "{{stage}}")
    else:
        text = ""
    for key, val in subs.items():
        text = text.replace("{{" + key + "}}", val)
    return text


# --- state -------------------------------------------------------------------

def find_root(start: Path | None = None) -> Path | None:
    """Walk up from cwd to find a .add/ project root."""
    cur = (start or Path.cwd()).resolve()
    for d in (cur, *cur.parents):
        if (d / ROOT_DIRNAME / STATE_FILE).exists():
            return d / ROOT_DIRNAME
    return None


def _require_root() -> Path:
    root = find_root()
    if root is None:
        _die("no .add/ project found. Run `add.py init` first.")
    return root


def load_state(root: Path) -> dict:
    """Load + parse state.json, failing CLOSED. A corrupt or unreadable state file
    dies with a clean 'state_invalid' message (never a raw traceback), so every
    command that loads state degrades gracefully (design-for-failure)."""
    try:
        return json.loads((root / STATE_FILE).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        _die(f"state_invalid: {root / STATE_FILE} is corrupt or unreadable "
             f"({e.__class__.__name__}) — restore it from git or a backup")


def _load_state_for_json() -> tuple[Path, dict]:
    """Fail-closed state load for `--json` paths: a missing project or unparseable
    state.json -> `no_state` on stderr + exit 1, with EMPTY stdout (never a partial
    JSON object a harness might parse). Built from State only — reads no docs/ chapter."""
    root = find_root()
    if root is None:
        _die("no_state")
    try:
        return root, json.loads((root / STATE_FILE).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        _die("no_state")


def _phase_owner(phase: str) -> str:
    """Map a phase to its owner (human|seam|ai); `unmapped_phase` if absent (fail closed)."""
    owner = PHASE_OWNER.get(phase)
    if owner is None:
        _die("unmapped_phase")
    return owner


def save_state(root: Path, state: dict) -> None:
    state["updated"] = _now()
    _atomic_write(root / STATE_FILE, json.dumps(state, indent=2) + "\n")


def _setup_locked(state: dict) -> bool:
    """True when the project's setup is locked — i.e. the build-boundary gate is OPEN.

    A state with NO "setup" key is GRANDFATHERED-locked: plain `init` and every legacy
    project are never gated (the lock is opt-in via `init --await-lock`). The gate is
    therefore active in exactly one case: "setup" present AND locked is False."""
    return ("setup" not in state) or (state["setup"].get("locked") is True)


def _die(msg: str, code: int = 1) -> None:
    print(f"add: error: {msg}", file=sys.stderr)
    raise SystemExit(code)


# --- guideline injection (dynamic-by-reference; designed for failure) --------
#
# Inject one stable, marker-delimited ADD block into the project root's AGENTS.md
# and CLAUDE.md. The block is DYNAMIC-BY-REFERENCE: it tells the agent to run
# `add.py status` and read PROJECT.md — it never embeds live state (slug, phase,
# gate). Auto-updated context files measurably hurt (ETH-Zurich: ~3% lower success,
# 20%+ more cost), so the stable pointer is the whole point.

def _guideline_block() -> str:
    """The canonical ADD block (markers + body, no trailing newline).

    Agent-agnostic by design (v14 agent-portability): the routing steps depend
    only on the CLI and plain files, so any agent — Claude, Cursor, Copilot,
    Codex — can follow them. Claude additionally gets the `add` skill."""
    return (
        f"{_GUIDE_BEGIN}\n"
        "## ADD — how to work in this repo\n"
        "\n"
        "This project uses **ADD (AI-Driven Development)**: you, the AI, drive the build;\n"
        "the human owns direction and verification. The loop below works for any agent —\n"
        "Claude, Cursor, Copilot, Codex — through the CLI alone. Before you change code:\n"
        "\n"
        "1. Run `python3 .add/tooling/add.py status` — where the project is and what's\n"
        "   next (the resume point; read it first every session).\n"
        "2. Read `.add/PROJECT.md` — the foundation (domain · spec · UI/UX) every task\n"
        "   builds on.\n"
        "3. Run `python3 .add/tooling/add.py guide` — it names the phase and the exact\n"
        "   phase-guide file to read (the `guide  :` line). Work ONLY that phase — each\n"
        "   guide ends with its exit gate and the command to move on.\n"
        "\n"
        "The flow: INTAKE sizes a request into a milestone; each task runs the\n"
        "**specification bundle** — Spec+Scenarios+Contract+Tests as one bundle,\n"
        "ONE human approval at the frozen contract — then a self-driving build→verify\n"
        "run. Non-negotiable for every agent:\n"
        "Never weaken a test or edit a frozen contract to make a build pass; a security\n"
        "finding is always HARD-STOP — never auto-passed.\n"
        "\n"
        "On Claude Code the `add` skill drives this loop automatically; other agents\n"
        "follow the three steps. The book is in `.add/docs/`. This block is generated\n"
        "by `add.py sync-guidelines`; edit outside the markers, not inside.\n"
        f"{_GUIDE_END}"
    )


def _inject_block(path: Path) -> str:
    """Write the ADD block into `path`. Returns created|updated|unchanged.

    - unchanged: on-disk block already matches -> no write, no .bak (idempotent).
    - updated:   existing content changes -> back up the original to <path>.bak first.
    - created:   file did not exist -> write the block, no .bak.
    User content outside the markers is always preserved.
    """
    block = _guideline_block()
    if path.exists():
        current = path.read_text(encoding="utf-8")
        begin = current.find(_GUIDE_BEGIN)
        if begin != -1:
            end = current.find(_GUIDE_END, begin)
            if end != -1:                      # replace only the marked region
                end += len(_GUIDE_END)
                new = current[:begin] + block + current[end:]
            else:                              # begin without end: corrupt — append fresh
                print(f"add: warning: {path.name}: found an ADD:BEGIN with no ADD:END "
                      "— appending a fresh block; review the result", file=sys.stderr)
                new = current.rstrip("\n") + "\n\n" + block + "\n"
        else:                                  # no block yet — append, keep user content
            new = current.rstrip("\n") + "\n\n" + block + "\n"
        if new == current:
            return "unchanged"
        _atomic_write(Path(str(path) + ".bak"), current)   # rollback path before mutate
        _atomic_write(path, new)
        return "updated"
    _atomic_write(path, block + "\n")
    return "created"


def _inject_guidelines(project_root: Path) -> list[tuple[str, str]]:
    """Inject the block into each guideline file under `project_root`.

    Symlink-dedup: targets resolving (os.path.realpath) to the same inode are
    written once, against the REAL file (never replacing the symlink with a
    regular file). Per-target OSError is isolated (warn+skip) so one unwritable
    file never aborts the run or `init`.
    """
    results: list[tuple[str, str]] = []
    seen: set[str] = set()
    for name in GUIDELINE_FILES:
        target = project_root / name
        real = os.path.realpath(target)
        if real in seen:
            continue
        seen.add(real)
        write_target = Path(real) if target.is_symlink() else target
        try:
            action = _inject_block(write_target)
        except (OSError, UnicodeDecodeError) as exc:
            # design for failure: an unwritable target OR a non-UTF-8 existing file
            # (e.g. a UTF-16 CLAUDE.md from a Windows editor) must not crash init or
            # abort the other target — warn and skip this one.
            print(f"add: warning: could not sync {name} — {exc}; skipped",
                  file=sys.stderr)
            action = "skipped"
        results.append((name, action))
    return results


# --- commands ----------------------------------------------------------------

_INIT_EXCLUDE = {
    ".add", "AGENTS.md", "CLAUDE.md", ".git",
    ".gitignore", ".gitattributes", ".github", ".editorconfig",  # VCS/CI/editor scaffolding — no domain signal
    "LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING",            # legal boilerplate — no domain signal
}  # README/docs/source are NOT excluded: they carry domain content adopt.md maps -> brownfield


def _is_brownfield(base: Path) -> bool:
    """True when `base` already holds project content beyond the tool's own scaffolding.

    Judgment-free: a mechanical fact (does the dir hold a non-excluded entry?), so the
    autonomous-onboarding flow knows to map existing code into the living documentation. INTERPRETING
    that code stays with the AI (skill/add/adopt.md) — the engine only detects + signals."""
    if not base.is_dir():
        return False
    return any(child.name not in _INIT_EXCLUDE for child in base.iterdir())


def cmd_init(args: argparse.Namespace) -> None:
    base = Path(args.dir).resolve()
    root = base / ROOT_DIRNAME
    state_path = root / STATE_FILE
    if state_path.exists() and not args.force:
        _die(f"already initialised at {root} (use --force to reset state)")

    (root / "tasks").mkdir(parents=True, exist_ok=True)
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

    state = {
        "project": proj_name,
        "stage": args.stage,
        "active_task": None,
        "active_milestone": None,
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
    task_md = tdir / "TASK.md"
    if task_md.exists() and not args.force:
        _die(f"task '{slug}' already exists (use --force to overwrite TASK.md)")

    # link to a milestone (explicit, or the active one) — validate before any write
    milestone = getattr(args, "milestone", None) or state.get("active_milestone")
    if milestone and milestone not in state.get("milestones", {}):
        _die("unknown_milestone")
    depends_on = _parse_deps(getattr(args, "depends_on", None))

    (tdir / "tests").mkdir(parents=True, exist_ok=True)
    (tdir / "src").mkdir(parents=True, exist_ok=True)
    title = args.title or slug.replace("-", " ").replace("_", " ").title()
    _atomic_write(task_md, _render_template(
        "TASK.md", title=title, slug=slug, date=date.today().isoformat(), stage=state["stage"]))

    state["tasks"][slug] = {
        "title": title,
        "phase": "specify",
        "gate": "none",
        "milestone": milestone,
        "depends_on": depends_on,
        "created": _now(),
        "updated": _now(),
    }
    state["active_task"] = slug
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
    print("active task set. phase: specify. Fill section 1 (SPECIFY), then: add.py advance")


def _parse_deps(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [d.strip() for d in raw.split(",") if d.strip()]


def _task_done(t: dict) -> bool:
    # Matrix 3: a task is done when Verify reads PASS *or a signed RISK-ACCEPTED*.
    # Both completing gates advance phase to "done" (cmd_gate), and a waiver is
    # signed at gate time — so a verdict gate is enough here; we need not re-read
    # the waiver. HARD-STOP never reaches "done". A bare `phase done` (escape
    # hatch, gate still "none") deliberately does NOT count: completion needs a
    # recorded verdict, not just a phase marker.
    return t.get("phase") == "done" and t.get("gate") in ("PASS", "RISK-ACCEPTED")


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
    slug = slug or state.get("active_task")
    if not slug:
        _die("no task specified and no active task set")
    if slug not in state["tasks"]:
        _die(f"unknown task '{slug}'")
    return slug


def cmd_phase(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    if args.phase not in PHASES:
        _die(f"phase must be one of: {', '.join(PHASES)}")
    state["tasks"][slug]["phase"] = args.phase
    state["tasks"][slug]["updated"] = _now()
    _sync_task_marker(root, slug, args.phase)
    save_state(root, state)
    print(f"task '{slug}' phase -> {args.phase}")


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
    # flag-first freeze guard (task unflagged-freeze): a FROZEN §3 may not cross
    # into build without a WELL-FORMED lowest-confidence flag. On pass, stamp the
    # verified marker so `audit` enforces the flag on THIS record only (open/new
    # freezes — the unmarked predecessors are never retro-redded). REFUSE writes
    # nothing (fail-closed); below the build boundary the flag is never checked.
    if nxt == "build":
        raw3 = _raw_phase_bodies(root, slug).get(3, "")
        if _contract_frozen(raw3):
            if not _flag_well_formed(raw3):
                _die("unflagged_freeze: a frozen §3 must surface a well-formed "
                     "'Least-sure flag surfaced at freeze:' unit (>=1 [part] tag "
                     "+ substantive content; bare 'none' only as 'none material — "
                     "biggest risk: X') before crossing into build")
            state["tasks"][slug]["flag_verified"] = True
    state["tasks"][slug]["phase"] = nxt
    state["tasks"][slug]["updated"] = _now()
    _sync_task_marker(root, slug, nxt)
    save_state(root, state)
    print(f"task '{slug}' phase {cur} -> {nxt}")


# The mechanized high-risk guard (run.md, v14): judging WHAT is high-risk stays
# human — a scope declares `risk: high` in its TASK.md header at the freeze. The
# engine then enforces the pure token contradiction: risk: high WITHOUT
# autonomy: conservative is unguarded, and completion is refused. Tokens are
# read from the header region (text before the first section heading) with HTML
# comments stripped — a documentation comment is never a declaration.
_RISK_HIGH_RE = re.compile(r"\brisk:\s*high\b")
_AUTONOMY_CONSERVATIVE_RE = re.compile(r"\bautonomy:\s*conservative\b")


def _task_header(root: Path, slug: str) -> str:
    """The TASK.md header region — where declared tokens (risk · autonomy)
    live — with HTML comments stripped. Missing file -> '' (no tokens)."""
    try:
        text = (root / "tasks" / slug / "TASK.md").read_text(encoding="utf-8")
    except OSError:
        return ""
    return re.sub(r"<!--.*?-->", "", text.split("\n## ", 1)[0], flags=re.S)


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
        hdr = _task_header(root, slug)
        if _RISK_HIGH_RE.search(hdr) and not _AUTONOMY_CONSERVATIVE_RE.search(hdr):
            _die(f"unguarded_high_risk_auto: task '{slug}' declares risk: high "
                 "without autonomy: conservative — lower the autonomy level in the TASK.md "
                 "header; a human must own a high-risk gate (run.md guard)")
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
        _sync_task_marker(root, slug, "done")
    state["tasks"][slug]["gate"] = args.outcome
    state["tasks"][slug]["updated"] = _now()
    save_state(root, state)
    print(f"task '{slug}' gate -> {args.outcome}")
    if args.outcome == "HARD-STOP":
        print("HARD-STOP recorded: return to BUILD; nothing ships on a failing/security gate.")


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
    if target not in PHASES[:7]:        # specify..observe; never "done", never an unknown name
        _die(f"reopen_target_invalid: --to must be one of {', '.join(PHASES[:7])} (got {target!r})")
    now = _now()
    entry = {"from": "done", "to": target, "reason": reason, "at": now,
             "prior_gate": t.get("gate", "none")}
    if t.get("waiver"):                 # void verdict's waiver -> history, drop the live key
        entry["prior_waiver"] = t.pop("waiver")
    t.setdefault("reopens", []).append(entry)
    t["phase"] = target
    t["gate"] = "none"
    t["updated"] = now
    _sync_task_marker(root, slug, target)
    save_state(root, state)
    print(f"task '{slug}' reopened: done -> {target} (reason recorded); gate reset to none")


# --- independent verification: schema · consensus · ledger · eval ------------

def _validate_verdict(obj: object) -> list[str]:
    """Return a list of shape errors for one verifier verdict ([] == valid).

    A verdict is DATA, not free-form prose: a lens (which independent verifier),
    a call (pass|fail|risk), and non-empty evidence (no shallow 'looks good'). This
    is the structured-output guard — it is what stops a vague auto-PASS."""
    if not isinstance(obj, dict):
        return ["verdict must be a JSON object"]
    errs: list[str] = []
    lens = obj.get("lens")
    if not isinstance(lens, str) or not lens.strip():
        errs.append("lens: required non-empty string (which independent verifier)")
    if obj.get("verdict") not in VERDICT_VALUES:
        errs.append(f"verdict: must be one of {', '.join(VERDICT_VALUES)}")
    ev = obj.get("evidence")
    if not isinstance(ev, str) or not ev.strip():
        errs.append("evidence: required non-empty string (no shallow verify)")
    if "security" in obj and not isinstance(obj["security"], bool):
        errs.append("security: must be a boolean")
    if "refutation" in obj and not isinstance(obj["refutation"], str):
        errs.append("refutation: must be a string")
    return errs


def _consensus(verdicts: list[dict],
               min_lenses: int = MIN_CONSENSUS_LENSES) -> tuple[str, str]:
    """The deterministic auto-gate decision over recorded verdicts → (outcome, reason).

    outcome ∈ {PASS, HARD-STOP, ESCALATE}. The rule, in priority order:
      1. ANY security finding (fail|risk) → HARD-STOP — security is never auto-passed.
      2. ANY refutation (a `fail`)        → HARD-STOP — return to Build.
      3. ANY residue (a `risk`)           → ESCALATE  — human-led gate (principle 2).
      4. all `pass` but < min distinct lenses → ESCALATE — independence too thin.
      5. all `pass` across ≥ min distinct lenses → PASS — self-consistent agreement.
    The engine computes this from data; the resolver still records the gate."""
    if not verdicts:
        return "ESCALATE", "no independent verdicts recorded — an auto-PASS needs evidence"
    for vd in verdicts:
        if vd.get("security") and vd.get("verdict") in ("fail", "risk"):
            return "HARD-STOP", (f"security finding from lens '{vd.get('lens')}' — "
                                 "never auto-passed")
    fails = [vd for vd in verdicts if vd.get("verdict") == "fail"]
    if fails:
        return "HARD-STOP", f"lens '{fails[0].get('lens')}' refuted the build — return to Build"
    risks = [vd for vd in verdicts if vd.get("verdict") == "risk"]
    if risks:
        return "ESCALATE", f"lens '{risks[0].get('lens')}' flagged residue — human-led gate"
    distinct = {str(vd.get("lens", "")).strip()
                for vd in verdicts if str(vd.get("lens", "")).strip()}
    if len(distinct) < min_lenses:
        return "ESCALATE", (f"insufficient independent coverage: {len(distinct)}/{min_lenses} "
                            "distinct lenses passed")
    return "PASS", f"{len(distinct)} independent lenses agree, none refuted"


def _verdict_ledger_path(root: Path, slug: str) -> Path:
    return root / "tasks" / slug / VERDICT_LEDGER


def _load_verdicts(root: Path, slug: str) -> list[dict]:
    """Read the append-only verdict ledger, failing closed on a corrupt line."""
    p = _verdict_ledger_path(root, slug)
    if not p.exists():
        return []
    out: list[dict] = []
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                out.append(json.loads(line))
    except (OSError, json.JSONDecodeError) as e:
        _die(f"verdict_ledger_invalid: {p} is unreadable or corrupt ({e.__class__.__name__})")
    return out


def cmd_verdict(args: argparse.Namespace) -> None:
    """Append one (or, via --file, many) structured verifier verdict(s) to the task ledger.

    The agent records a fresh, context-isolated verifier's call here; the engine
    validates SHAPE before writing (fail closed — a malformed verdict is never stored)."""
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    if args.file:
        try:
            raw = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, json.JSONDecodeError) as e:
            _die(f"verdict_input_invalid: {e.__class__.__name__}: {e}")
        records = data if isinstance(data, list) else [data]
    else:
        if args.lens is None or args.verdict is None or args.evidence is None:
            _die("verdict_incomplete: supply --lens, --verdict and --evidence (or --file)")
        rec: dict = {"lens": args.lens, "verdict": args.verdict, "evidence": args.evidence}
        if args.refutation is not None:
            rec["refutation"] = args.refutation
        if args.security:
            rec["security"] = True
        records = [rec]
    # validate EVERY record before writing ANY (no partial ledger)
    for i, rec in enumerate(records):
        errs = _validate_verdict(rec)
        if errs:
            _die(f"verdict_invalid (record {i}): " + "; ".join(errs))
    now = _now()
    p = _verdict_ledger_path(root, slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as fh:        # append-only ledger
        for rec in records:
            rec = dict(rec)
            rec.setdefault("at", now)
            fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
    print(f"recorded {len(records)} verdict(s) for '{slug}' -> tasks/{slug}/{VERDICT_LEDGER}")


def cmd_consensus(args: argparse.Namespace) -> None:
    """Read-only: compute the auto-gate decision from the recorded independent verdicts.

    The run consults this before `gate`: PASS → `gate PASS`; HARD-STOP → `gate HARD-STOP`
    (return to Build); ESCALATE → human-led gate (no auto-PASS)."""
    root = _require_root()
    state = load_state(root)
    slug = _resolve_task(state, args.slug)
    verdicts = _load_verdicts(root, slug)
    outcome, reason = _consensus(verdicts, args.min_lenses)
    lenses = sorted({str(v.get("lens", "")).strip()
                     for v in verdicts if str(v.get("lens", "")).strip()})
    if getattr(args, "json", False):
        print(json.dumps({"slug": slug, "outcome": outcome, "reason": reason,
                          "verdicts": len(verdicts), "lenses": lenses},
                         separators=(",", ":")))
    else:
        print(f"consensus for '{slug}': {outcome} — {reason}")
        print(f"  {len(verdicts)} verdict(s) across {len(lenses)} lens(es): "
              f"{', '.join(lenses) or '(none)'}")


def cmd_eval(args: argparse.Namespace) -> None:
    """Read-only: score the consensus decision logic against labeled verdict fixtures.

    Each fixture is `{ "verdicts": [...], "label": "PASS|HARD-STOP|ESCALATE" }` — the
    decision the gate SHOULD make for a known build (e.g. a seeded-bad build → HARD-STOP).
    Reports exact accuracy plus a binary 'should-block' confusion: `recall` is the safety
    metric — every seeded-bad build must be caught (fn = 0). This is red/green TDD applied
    to the AI gate's own judgment, not just to the code."""
    root = find_root()
    explicit = args.fixtures is not None
    fixtures_dir = Path(args.fixtures) if explicit else (root / "eval" if root else None)
    files = sorted(fixtures_dir.glob("*.json")) if (fixtures_dir and fixtures_dir.exists()) else []
    if not files:
        # An explicit --fixtures that resolves to nothing is a user error (fail closed).
        # The bare default (no fixtures laid down yet) is a clean no-op, not a failure.
        if explicit:
            _die(f"eval_no_fixtures: no *.json fixtures at {fixtures_dir} — check --fixtures")
        print("eval: no fixtures (default .add/eval/ is empty) — nothing to score")
        return
    valid_labels = ("PASS", "HARD-STOP", "ESCALATE")
    tp = fp = tn = fn = correct = 0
    rows: list[tuple] = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            _die(f"eval_fixture_invalid: {f.name}: {e.__class__.__name__}")
        label = data.get("label")
        if label not in valid_labels:
            _die(f"eval_fixture_invalid: {f.name}: label must be one of {', '.join(valid_labels)}")
        outcome, reason = _consensus(data.get("verdicts", []), args.min_lenses)
        ok = (outcome == label)
        correct += ok
        should_block = (label != "PASS")        # binary safety view: did NOT auto-pass
        did_block = (outcome != "PASS")
        if should_block and did_block:
            tp += 1
        elif should_block and not did_block:
            fn += 1                              # the dangerous miss: a bad build auto-passed
        elif not should_block and did_block:
            fp += 1                              # a false alarm: a good build blocked
        else:
            tn += 1
        rows.append((f.name, label, outcome, ok, reason))
    n = len(files)
    accuracy = correct / n
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    if getattr(args, "json", False):
        print(json.dumps({
            "fixtures": n, "accuracy": accuracy, "precision": precision, "recall": recall,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "rows": [{"fixture": r[0], "label": r[1], "outcome": r[2], "match": r[3]}
                     for r in rows],
        }, separators=(",", ":")))
    else:
        for name, label, outcome, ok, _reason in rows:
            mark = "ok" if ok else "MISMATCH"
            print(f"  {mark:>8}  {name:<28} label={label:<11} consensus={outcome}")
        print(f"eval: {correct}/{n} exact ({accuracy:.0%}) · catch precision={precision:.0%} "
              f"recall={recall:.0%} · missed-bad(fn)={fn}")


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
    state["setup"] = {"locked": True, "locked_at": when, "locked_by": who, "layers": layers}
    save_state(root, state)
    if getattr(args, "json", False):
        print(json.dumps(
            {"locked": True, "locked_at": when, "locked_by": who, "layers": layers},
            separators=(",", ":")))
    else:
        print(f"locked setup ({','.join(layers)}) by {who} @ {when}")


def _has_production_roadmap(state: dict) -> bool:
    """True iff ≥1 milestone in state has stage == "production" (STATUS-AGNOSTIC).
    The single source of the stage-graduation floor (v22 graduate-guide): the guard counts
    that a production-roadmap RECORD exists — it never judges whether those milestones are
    done/good/sufficient (gather-not-judge). An archived-out-of-state roadmap falls to --force."""
    return any(m.get("stage") == "production"
               for m in state.get("milestones", {}).values())


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


def cmd_status(args: argparse.Namespace) -> None:
    if getattr(args, "json", False):
        root, state = _load_state_for_json()
        tasks = state.get("tasks") or {}
        milestones = state.get("milestones") or {}
        ms_list = []
        for mslug, m in milestones.items():
            members = [t for t in tasks.values() if t.get("milestone") == mslug]
            ms_list.append({"slug": mslug, "status": m.get("status", "active"),
                            "done": sum(1 for t in members if _task_done(t)),
                            "total": len(members)})
        grad_ready, grad_met, grad_total = _graduation_ready(root, state)
        print(json.dumps({
            "project": state.get("project"), "stage": state.get("stage"),
            "active_task": state.get("active_task"),
            "milestones": ms_list,
            "tasks": [{"slug": s, "phase": t.get("phase"), "gate": t.get("gate"),
                       "milestone": t.get("milestone")} for s, t in tasks.items()],
            "graduation_ready": grad_ready,
            "stage_criteria": {"met": grad_met, "total": grad_total}}))
        return
    root = _require_root()
    state = load_state(root)
    active = state.get("active_task")
    tasks = state.get("tasks", {})
    # Compute once: True when setup is present AND locked is False (the lock-gate window).
    # Reuses the canonical helper — do NOT write a parallel predicate.
    unlocked = not _setup_locked(state)
    print(f"project : {state.get('project', '(unknown)')}")
    print(f"stage   : {state.get('stage', '(unknown)')}")
    # project GOAL + active-milestone goal (v20) — the loop's orientation anchor, read
    # LIVE from PROJECT.md / MILESTONE.md (never state.json). Additive: every existing
    # line stays put. A missing source degrades to a sentinel — one never blanks the other.
    print(f"goal    : {_project_goal(root)}")
    _active_ms = state.get("active_milestone")
    if _active_ms:
        print(f"m-goal  : {_milestone_doc(root, _active_ms)[1]}   (← {_active_ms})")
    # foundation pointer — read the cross-milestone context first (anti-rot)
    if (root / "PROJECT.md").exists():
        print("context : .add/PROJECT.md  (foundation: domain · spec · UI/UX — read first)")
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
    active_ms = state.get("active_milestone")
    if milestones:
        print("milestones:")
        for mslug, m in milestones.items():
            members = [t for t in tasks.values() if t.get("milestone") == mslug]
            done = sum(1 for t in members if _task_done(t))
            mark = "*" if mslug == active_ms else " "
            print(f"  {mark} {mslug:<20} {done}/{len(members)} tasks done"
                  f"   status={m.get('status', 'active')}")
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

    print(f"active  : {active or '(none)'}")
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
    for slug, t in tasks.items():
        mark = "*" if slug == active else " "
        deps = t.get("depends_on") or []
        dep_s = f"  deps={','.join(deps)}" if deps else ""
        ms_s = f"  [{t['milestone']}]" if t.get("milestone") else ""
        print(f"  {mark} {slug:<24} phase={t['phase']:<10} gate={t['gate']}{ms_s}{dep_s}")
    # fold-pressure nudge: surface unfolded competency deltas so emission can't
    # silently outrun the human fold (read-only; v11). Silent when none are open.
    open_deltas = sum(len(v) for v in _collect_open_deltas(root).values())
    if open_deltas:
        print(f"deltas  : {open_deltas} open — consolidate at milestone close (add.py deltas)")
    # When the setup is unlocked, the only terminal guidance that matters is
    # review+lock; suppress the generic resume block so it does not compete.
    if unlocked:
        print("\nsetup   : UNLOCKED — review .add/SETUP-REVIEW.md (lowest-confidence first),"
              " then sign: add.py lock")
        print("          (the build-boundary gate is closed until the foundation is locked)")
    elif active and active in tasks:
        ph = tasks[active]["phase"]
        if ph == "done":
            print(f"\nresume  : task '{active}' is done ({tasks[active]['gate']}).")
            print("          start the next feature: add.py new-task <slug>")
        else:
            print(f"\nresume  : task '{active}' is at phase '{ph}'.")
            print(f"          read .add/tasks/{active}/TASK.md and continue that phase.")


# Agent-portability (v14): `guide` names the PHASE PLAYBOOK file — the same
# guides the Claude skill loads, installed as plain markdown by every channel
# at .claude/skills/add/phases/ — so ANY agent (Cursor, Copilot, Codex) can be
# routed there through the CLI alone. Never a dead pointer: the path is printed
# only if the file exists; a missing tree gets an install hint instead.
_PHASE_GUIDE_FILES = {
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
        slug = args.slug or state.get("active_task")
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
        print(json.dumps({"task": slug, "phase": phase, "owner": owner,
                          "stop": owner != "ai", "next_step": action,
                          "chapter": f".add/docs/{chapter}", "gate": t.get("gate"),
                          "guide": _phase_guide_path(json_root.parent, phase)}))
        return
    root = _require_root()
    state = load_state(root)
    slug = args.slug or state.get("active_task")
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
    print(f"active : {slug}  (phase: {phase})")
    print(f"goal   : {_project_goal(root)}")   # v20 — the next-step surface still shows what the work is FOR
    print(f"next   : {action}")
    print(f"read   : .add/docs/{chapter}")
    gp = _phase_guide_path(root.parent, phase)
    if gp is not None:
        print(f"guide  : {gp}")
    elif phase in _PHASE_GUIDE_FILES:
        print("guide  : (phase guides not installed — npx @pilotspace/add init)")
    if phase == "verify":
        print("then   : add.py gate PASS | RISK-ACCEPTED | HARD-STOP")
    elif phase == "done":
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
            state = json.loads((root / STATE_FILE).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            _die("state_invalid")

    checks: list[tuple[bool, str, str]] = []  # (ok, description, reason-if-failed)
    for key in ("project", "stage", "active_task", "tasks"):
        checks.append((key in state, f"state has key '{key}'", "missing"))

    tasks = state.get("tasks") if isinstance(state.get("tasks"), dict) else {}
    milestones = state.get("milestones") if isinstance(state.get("milestones"), dict) else {}
    archived_slugs = _archived_task_slugs(state)   # archived deps still resolve
    warnings: list[tuple[str, str]] = []  # (name, reason) — nudges that NEVER feed `failed`
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
        else:
            # warn-never-block: a task outside a milestone is a structural nudge back toward
            # the intake flow — NOT a failure. Names structure, never the act of intake.
            warnings.append((f"task '{slug}'", "is outside a milestone — size it via the /add "
                                               "intake flow (or attach with --milestone)"))
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

    # drift: a done milestone must have no unfinished tasks
    for mslug, m in milestones.items():
        if m.get("status") == "done":
            unfinished = [s for s, t in tasks.items()
                          if t.get("milestone") == mslug and not _task_done(t)]
            checks.append((not unfinished, f"done milestone '{mslug}' fully complete",
                           f"unfinished: {unfinished}"))

    # dependency graph must be acyclic
    cycle = _find_cycle(tasks)
    checks.append((cycle is None, "task dependencies are acyclic",
                   f"cycle: {' -> '.join(cycle)}" if cycle else ""))

    passed = sum(1 for ok, _, _ in checks if ok)
    failed = len(checks) - passed
    if as_json:
        print(json.dumps({"passed": passed, "failed": failed,
                          "warned": len(warnings),
                          "warnings": [{"name": name, "reason": reason}
                                       for name, reason in warnings],
                          "checks": [{"ok": ok, "name": desc,
                                      "reason": reason if not ok else ""}
                                     for ok, desc, reason in checks]}))
    else:
        for ok, desc, reason in checks:
            print(f"PASS  {desc}" if ok else f"FAIL  {desc}: {reason}")
        for name, reason in warnings:
            print(f"WARN  {name} {reason}")
        summary = f"check: {passed} passed, {failed} failed"
        if warnings:
            summary += f" ({len(warnings)} warnings)"   # frozen §3: summary gains "(N warnings)"
        print(summary)
    if failed:
        raise SystemExit(1)


def cmd_new_milestone(args: argparse.Namespace) -> None:
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    if not slug.replace("-", "").replace("_", "").isalnum():
        _die("bad_slug")
    state.setdefault("milestones", {})
    mdir = root / "milestones" / slug
    mfile = mdir / MILESTONE_FILE
    if mfile.exists() and not args.force:
        _die("milestone_exists")
    mdir.mkdir(parents=True, exist_ok=True)
    title = args.title or slug.replace("-", " ").replace("_", " ").title()
    _atomic_write(mfile, _render_template(
        "MILESTONE.md", title=title, goal=args.goal or "<goal>",
        stage=args.stage, date=date.today().isoformat()))
    state["milestones"][slug] = {
        "title": title, "goal": args.goal or "", "stage": args.stage,
        "status": "active", "created": _now(), "updated": _now(),
    }
    state["active_milestone"] = slug
    save_state(root, state)
    print(f"created milestone '{slug}' -> {mfile}")
    print(f"active milestone set. Decompose it into tasks: add.py new-task <slug> --depends-on ...")


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
        print(f"  {slug}{suffix}")


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
    print("Confirm the MILESTONE.md exit criteria are checked, then archive/start the next.")
    # fold-pressure nudge: milestone close is the natural fold point for open deltas (v11)
    open_deltas = sum(len(v) for v in _collect_open_deltas(root).values())
    if open_deltas:
        noun = "delta" if open_deltas == 1 else "deltas"
        print(f"note: {open_deltas} open {noun} to consolidate into the foundation "
              f"— review with: add.py deltas")


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
    if state.get("active_milestone") == slug:
        state["active_milestone"] = None
    if state.get("active_task") in members:
        state["active_task"] = None
    save_state(root, state)
    print(f"archived milestone '{slug}' ({len(members)} tasks) — removed from active state.")
    print("files on disk are untouched; see `add.py status` for the archived rollup.")


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
    save_state(root, state)
    total = sum(n for _, n in moved)
    print(f"compacted milestone '{slug}' -> .add/archive/{slug}/ "
          f"({len(members)} task dirs, {total} files moved)")
    for path, n in moved:
        print(f"  moved {path} ({n} files)")
    print("recovery: reverse the moves (mv the bundle's parts back) — state needs no edit.")


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
    print(f"task '{task}' -> milestone '{new}'" if new else f"task '{task}' -> milestone (none)")


def cmd_use(args: argparse.Namespace) -> None:
    """Set the active task to an EXISTING task (switch focus) without scaffolding a new
    one or hand-editing state.json. advance/gate/phase still take an explicit slug; `use`
    just moves the default focus, closing the only gap that forced manual state edits."""
    root = _require_root()
    state = load_state(root)
    slug = args.slug
    if slug not in state.get("tasks", {}):
        _die("unknown_task")
    state["active_task"] = slug
    save_state(root, state)
    print(f"active task -> '{slug}' (phase={state['tasks'][slug]['phase']})")


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

_DEFAULT_WIDTH = 72       # fixed width for the persisted/canonical render (RETRO.md)
# Two glyph tiers. Alignment is correct only with ASCII in column-positioned
# cells (every ASCII char is 1 display cell); Unicode glyphs sit at line-END
# (the PROGRESS track) or in non-aligned rows, where width can't break columns.
_UNICODE = {"reached": "●", "current": "◉", "pending": "○", "h": "═", "rule": "─", "bullet": "•"}
_ASCII = {"reached": "#", "current": ">", "pending": ".", "h": "=", "rule": "-", "bullet": "*"}
_GATE_SHORT = {"PASS": "PASS", "RISK-ACCEPTED": "RISK", "HARD-STOP": "STOP", "none": "—"}
_ANSI = {"green": "\x1b[32m", "yellow": "\x1b[33m", "red": "\x1b[31m",
         "dim": "\x1b[2m", "reset": "\x1b[0m"}


def _bar(num: int, den: int, cells: int, g: dict) -> str:
    """A progress bar; 0/0 -> all-empty (no divide-by-zero)."""
    filled = 0 if den <= 0 else round(num / den * cells)
    filled = max(0, min(cells, filled))
    return g["reached"] * filled + g["pending"] * (cells - filled)


def _phase_track(phase: str, g: dict) -> str:
    """Compact 8-cell pipeline (no labels — a single legend explains it):
    reached · current · pending. A done task -> all reached."""
    try:
        ci = PHASES.index(phase)
    except ValueError:
        ci = 0
    cells = []
    for i in range(len(PHASES)):
        if phase == "done" or i < ci:
            cells.append(g["reached"])
        elif i == ci:
            cells.append(g["current"])
        else:
            cells.append(g["pending"])
    return "".join(cells)


def _use_ascii() -> bool:
    """ASCII tier when the terminal can't render Unicode (non-UTF-8 / dumb)."""
    enc = (getattr(sys.stdout, "encoding", "") or "").lower()
    return ("utf" not in enc) or (os.environ.get("TERM") == "dumb")


def _color_enabled() -> bool:
    """Color only on an interactive tty, honoring NO_COLOR and TERM."""
    return (sys.stdout.isatty() and not os.environ.get("NO_COLOR")
            and os.environ.get("TERM", "") not in ("dumb", ""))


def _term_width() -> int:
    try:
        import shutil
        return min(max(shutil.get_terminal_size().columns, 64), 100)
    except Exception:
        return _DEFAULT_WIDTH


def _colorize(s: str) -> str:
    """Apply ANSI to status tokens — redundant to the text, never the sole signal.
    Applied ONLY to tty stdout; the persisted RETRO.md string stays plain."""
    c = _ANSI
    s = re.sub(r"\bDONE\b", c["green"] + "DONE" + c["reset"], s)
    s = re.sub(r"\bBLOCKED\b", c["red"] + "BLOCKED" + c["reset"], s)
    s = re.sub(r"\bPASS\b", c["green"] + "PASS" + c["reset"], s)
    s = re.sub(r"\bRISK\b", c["yellow"] + "RISK" + c["reset"], s)
    s = re.sub(r"\bSTOP\b", c["red"] + "STOP" + c["reset"], s)
    return s


def _project_goal(root: Path) -> str:
    """The project GOAL — the value of the first `goal:` line in PROJECT.md, else
    GOAL_UNSET. Read-only and fail-closed: a missing/unreadable foundation or a
    blank value degrades to the sentinel (orientation never raises). Mirrors how
    _milestone_doc reads the milestone goal — the foundation is the single source."""
    f = root / "PROJECT.md"
    try:
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("goal:"):
                return line.split(":", 1)[1].strip() or GOAL_UNSET
    except OSError:
        pass
    return GOAL_UNSET


def _milestone_doc(root: Path, mslug: str) -> tuple[str, str]:
    """(title, goal) from MILESTONE.md; ('(unknown)','(unknown)') if the doc is gone."""
    f = root / "milestones" / mslug / MILESTONE_FILE
    if not f.exists():
        return "(unknown)", "(unknown)"
    title, goal = "(unknown)", "(unknown)"
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.startswith("# MILESTONE:"):
            title = line.split(":", 1)[1].strip() or "(unknown)"
        elif line.startswith("goal:"):
            goal = line.split(":", 1)[1].strip() or "(unknown)"
            break
    return title, goal


def _exit_criteria(root: Path, mslug: str) -> tuple[int, int]:
    """(met, total) checkbox tally inside MILESTONE.md's 'Exit criteria' section."""
    f = root / "milestones" / mslug / MILESTONE_FILE
    if not f.exists():
        return 0, 0
    m = re.search(r"## Exit criteria.*?(?=\n## |\Z)", f.read_text(encoding="utf-8"), re.S)
    if not m:
        return 0, 0
    sec = m.group(0)
    met = len(re.findall(r"- \[x\]", sec))
    total = met + len(re.findall(r"- \[ \]", sec))
    return met, total


def _stage_criteria(root: Path) -> tuple[int, int]:
    """(met, total) checkbox tally inside PROJECT.md's 'Stage goal criteria' section — the
    PROJECT.md analog of _exit_criteria (v22): the human's stage-covered affirmation. Read-only
    and fail-closed to (0, 0): a missing file, a missing section, or any read error never raises
    and never fabricates a cue (so an unreadable foundation withholds graduation, design-for-failure)."""
    try:
        text = (root / "PROJECT.md").read_text(encoding="utf-8")
    except OSError:
        return 0, 0
    m = re.search(r"## Stage goal criteria.*?(?=\n## |\Z)", text, re.S)
    if not m:
        return 0, 0
    sec = m.group(0)
    met = len(re.findall(r"- \[x\]", sec))
    total = met + len(re.findall(r"- \[ \]", sec))
    return met, total


def _all_milestones_done(state: dict) -> bool:
    """True when the project HAS milestones and EVERY one is status=done (v22). Archived
    milestones are absent from state['milestones'] (removed by the archive lifecycle), so they
    do not count; a project with zero milestones is not 'covered' and returns False."""
    ms = state.get("milestones") or {}
    return bool(ms) and all(m.get("status") == "done" for m in ms.values())


def _graduation_ready(root: Path, state: dict) -> tuple[bool, int, int]:
    """(ready, met, total) for the stage-graduation cue (v22): every milestone done AND the
    human's stage-goal-criteria all checked (total>0 and met==total). The SINGLE source the
    text and --json status branches share, so the cue and the json signal can never disagree."""
    met, total = _stage_criteria(root)
    ready = _all_milestones_done(state) and total > 0 and met == total
    return ready, met, total


def _count_test_defs(f: Path) -> int:
    """`def test_` occurrences in one file — the ONE counting regex (primary and
    §4-declared fallback share it by construction). OSError -> 0, fail-closed."""
    try:
        return len(re.findall(r"^\s*def test_", f.read_text(encoding="utf-8"), re.M))
    except OSError:
        return 0


def _tests_count(root: Path, slug: str) -> int:
    d = root / "tasks" / slug / "tests"
    if not d.is_dir():
        return 0
    return sum(_count_test_defs(f) for f in d.glob("*.py"))


def _confined(p: Path, rootp: Path) -> bool:
    """True only if p resolves (symlinks followed) inside rootp; errors -> False.
    The v2 confinement check — no read is attempted on a path that fails it."""
    try:
        return p.resolve().is_relative_to(rootp)
    except OSError:
        return False


def _declared_tests_count(root: Path, slug: str) -> int:
    """Count tests at the §4 'Tests live in:' declared path(s). PURE, fail-closed 0.
    Tokens are the backticked spans on the FIRST declaring line of the raw §4 body.
    Resolution: './…' -> task dir · contains '/' -> project root (parent of .add) ·
    bare name -> sibling of the previous resolved token (else task dir). A directory
    token counts the *.py files directly inside it; resolved files are deduped.
    v2 confinement: every file read must resolve inside the project root — '..'
    traversal, absolute tokens, and symlink escapes all contribute 0, fail-closed."""
    body = _raw_phase_bodies(root, slug).get(4, "")
    m = re.search(r"^\s*Tests live in:.*$", body, re.M)
    if not m:
        return 0
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
    return sum(_count_test_defs(f) for f in files)


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
    lines = (m7.group(0) if m7 else text).splitlines()
    # observe: the field value + continuation lines until a blank line / heading / list
    observe = "(unknown)"
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


def _clip(s: str, maxlen: int) -> str:
    """Trim a string to fit a fixed-width frame, ellipsizing if it overruns."""
    return s if len(s) <= maxlen else s[:maxlen - 1].rstrip() + "…"


def _wrap(text: str, width: int, label: str) -> list[str]:
    """Wrap `text` to `width`; the first line carries `label`, continuations are
    blank-indented to the same width (so a multi-line goal shows 'goal' once)."""
    cont = " " * len(label)
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    lines = lines or ["(unknown)"]
    return [(label if i == 0 else cont) + ln for i, ln in enumerate(lines)]


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
                      "status": ms.get("status", "active")},
        "summary": {
            "tasks_done": sum(1 for r in task_rows if r["done"]),
            "tasks_total": len(task_rows),
            "gates": {"PASS": sum(1 for r in task_rows if r["gate"] == "PASS"),
                      "RISK-ACCEPTED": sum(1 for r in task_rows if r["gate"] == "RISK-ACCEPTED"),
                      "HARD-STOP": sum(1 for r in task_rows if r["gate"] == "HARD-STOP")},
            "exit_criteria": {"met": met, "total": total_ec},
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
            if 1 <= n <= 7 and n not in starts:
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


def task_phases(root: Path, slug: str) -> list[dict]:
    """The frozen per-task PHASE-DETAIL shape (v9-1): parse TASK.md §1–§7 into seven
    blocks specify→observe. PURE — NO writes. Each entry is
    { "phase": <name>, "n": <1..7>, "body": <cleaned text | "(empty)"> }.

    The heading scan lives in _phase_spans (shared with the decide digest); this view
    CLEANS each body. Missing file / missing section / placeholder-only body ->
    "(empty)" (fail-closed)."""
    names = PHASES[:7]  # specify..observe; "done" is a terminal STATE, not a section
    f = root / "tasks" / slug / "TASK.md"
    try:
        text = f.read_text(encoding="utf-8")
    except OSError:   # missing OR unreadable -> every phase fail-closed to "(empty)"
        return [{"phase": names[n - 1], "n": n, "body": "(empty)"} for n in range(1, 8)]
    spans = _phase_spans(text)
    return [{"phase": names[n - 1], "n": n,
             "body": _clean_phase_body(spans[n]) if n in spans else "(empty)"}
            for n in range(1, 8)]


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
        i = p["n"] - 1
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
    (template hints) never count. PURE — fail-closed on a missing label."""
    body = re.sub(r"<!--.*?-->", "", raw3, flags=re.S)
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


def _decide_next_base(state: dict, d: dict) -> str:
    ms = d["milestone"]["slug"]
    rows = d["tasks"]
    if not rows:
        return "none — no tasks yet"
    stopped = [r for r in rows if r["gate"] == "HARD-STOP"]
    if stopped:
        return f"resolve HARD-STOP on {stopped[0]['slug']}"
    s = d["summary"]
    if s["tasks_done"] == s["tasks_total"]:
        # tasks complete — but the milestone holds while the goal (exit criteria) is
        # unmet (v20). Point at the feed-forward inventory the loop draws from, instead
        # of "archive". Fires only when criteria exist; else the prompt is unchanged.
        ec = s.get("exit_criteria") or {}
        met, total = ec.get("met", 0), ec.get("total", 0)
        if total > 0 and met < total:
            return (f"goal not met ({met}/{total} exit criteria) — propose next tasks "
                    f"from open deltas / the unscaffolded plan (add.py deltas)")
        return f"consolidate learnings + archive-milestone {ms}"
    active = state.get("active_task")
    order = sorted(rows, key=lambda r: 0 if r["slug"] == active else 1)  # stable
    for r in order:
        if r["done"]:
            continue
        if r["phase"] in _FRONT_PHASES:
            return (f"approve the contract of {r['slug']} — "
                    f"add.py report {ms} {r['slug']} --decide")
        if r["phase"] == "verify" and r["gate"] == "none":
            return f"gate {r['slug']} — add.py report {ms} {r['slug']} --decide"
    r = next(x for x in order if not x["done"])
    return f"none — run in progress ({r['slug']} at {r['phase']})"


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
_DELTA_RE = re.compile(
    r"\s*-\s*\[\s*(DDD|SDD|UDD|TDD|ADD)\s*·\s*(open|folded|rejected)\s*\]\s*(.+)$"
)
_EVIDENCE_RE = re.compile(r"^(.*?)\s*\(evidence:\s*(.*?)\)\s*$")

# Broad structural tag detector: finds ANY "- [tok · tok]" line (valid OR malformed).
# A line with a `· ` bracket separator is a delta-attempt. Does NOT enumerate
# competencies or statuses — a different abstraction from _DELTA_RE (no DRY violation).
_TAG_BROAD_RE = re.compile(r"^\s*-\s*\[\s*([^\]·]+?)\s*·\s*([^\]·]+?)\s*\]\s*(.*)$")


def _lint_task_deltas(root: Path, slug: str) -> tuple[bool, str] | None:
    """Lint all open delta entries in a task's '### Competency deltas' block.

    Returns:
        None                    — no delta-attempts found; no check emitted.
        (True, "")              — all open entries pass.
        (False, "<code> -> <tag line>") — first failing entry with its failure code.

    Contract rules (frozen §3, v1):
    - SKIP HTML-comment lines and blank lines (they are never tag lines).
    - Group lines into ENTRIES: a broad tag line starts an entry; following lines
      until next tag / blank / end-of-block are its continuation.
    - A line without a '· ' separator inside brackets (e.g. '- [x]') is NOT a tag.
    - For each entry, skip folded/rejected (open-only — history not retrofitted).
    - Validate the remaining (open) entries: COMP in _COMPETENCY_ORDER,
      status in _DELTA_STATUSES, and '(evidence:' present SOMEWHERE in the unit.
    - Fail-closed: an unparseable attempt FAILS (never silently passes).
    """
    task_md = root / "tasks" / slug / "TASK.md"
    if not task_md.exists():
        return None
    try:
        text = task_md.read_text(encoding="utf-8")
    except OSError:
        return None

    # Locate the "### Competency deltas" block.
    block_match = re.search(r"###\s*Competency deltas\s*\n(.*?)(?=\n##|\Z)", text, re.S)
    if not block_match:
        return None

    block = block_match.group(1)
    raw_lines = block.splitlines()

    # First pass: collect entries (tag line + continuations).
    # HTML-comment lines are skipped entirely (invisible to the guard).
    # Blank lines terminate the current entry, but are not tags themselves.
    entries: list[tuple[str, list[str]]] = []  # (tag_line, [tag_line, *continuations])
    current: list[str] | None = None
    for raw_line in raw_lines:
        stripped = raw_line.strip()
        # Skip HTML-comment lines.
        if stripped.startswith("<!--"):
            continue
        # Blank line terminates the current entry.
        if not stripped:
            current = None
            continue
        # Broad tag detection: any "- [tok · tok]" line starts a new entry.
        m = _TAG_BROAD_RE.match(raw_line)
        if m:
            current = [stripped]
            entries.append((stripped, current))
        elif current is not None:
            # Continuation line of the current entry.
            current.append(stripped)
        # else: non-blank, non-comment, non-tag line with no prior entry — ignore.

    if not entries:
        return None  # no delta-attempts → no check emitted

    # Second pass: validate each entry.
    for tag_line, unit_lines in entries:
        m = _TAG_BROAD_RE.match(tag_line)
        if not m:
            # Should not happen, but fail-closed.
            return False, f"malformed_delta -> {tag_line}"
        raw_comp = m.group(1).strip()
        raw_status = m.group(2).strip()

        # Step 1: skip historical entries (folded/rejected) — open-only enforcement.
        # MUST happen before competency/status validation per §3: "history not retrofitted".
        if raw_status in ("folded", "rejected"):
            continue

        # Step 2: use _DELTA_RE (the canonical grammar, single source of truth) to test
        # whether the tag line is a fully-valid delta shape. If it matches, check evidence
        # only. If it fails, classify the failure via the raw tokens (never a parallel grammar).
        unit_text = " ".join(unit_lines)
        if _DELTA_RE.match(tag_line):
            # Valid comp + status + non-empty tail — check evidence in the joined unit.
            if "(evidence:" not in unit_text:
                return False, f"no_evidence -> {tag_line}"
        else:
            # Classify why _DELTA_RE rejected it (open entries only — folded/rejected skipped).
            if raw_comp not in _COMPETENCY_ORDER:
                return False, f"unknown_competency -> {tag_line}"
            if raw_status not in _DELTA_STATUSES:
                return False, f"unknown_status -> {tag_line}"
            # Comp and status are valid but the line still failed _DELTA_RE (e.g. empty tail).
            return False, f"malformed_delta -> {tag_line}"

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
            by_comp[comp].append({"task": slug, "text": delta_text, "evidence": evidence})
    return by_comp


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
        sec = _AUDIT_SECURITY_RE.search(s6)
        marked = bool(sec and ("NOTE" in sec.group(0) or "⚠" in sec.group(0)))
        rev = _AUDIT_REVIEWED_RE.search(s6)
        if marked and rev and "auto-gate" in rev.group(1):
            f(slug, "unescalated_security_note",
              "security-line note (NOTE/⚠) with an auto-gate reviewer")
        # F7 unguarded_high_risk_auto (task high-risk-signal, v14): a declared
        # high-risk record must show a guarded dial AND a human at the gate —
        # catches post-gate header tampering and auto-resolved high-risk gates.
        hdr = _task_header(root, slug)
        if _RISK_HIGH_RE.search(hdr):
            if not _AUTONOMY_CONSERVATIVE_RE.search(hdr):
                f(slug, "unguarded_high_risk_auto",
                  "risk: high declared but autonomy is not 'conservative'")
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
    return checked, findings


def cmd_audit(args: argparse.Namespace) -> None:
    """Read-only: audit recorded human decision points for well-formedness. Exit 0 clean,
    exit 1 with findings — the enforcement gate CI consumes (audit-ci). Writes
    NOTHING; every other command is byte-identical."""
    root = _require_root()
    checked, findings = _audit_findings(root, load_state(root))
    if getattr(args, "json", False):
        print(json.dumps({"checked": checked, "findings": findings},
                         ensure_ascii=False, indent=2))
    else:
        if findings:
            for x in findings:
                print(f"audit: {x['code']} {x['task']} — {x['detail']}")
        else:
            print(f"audit: clean ({checked} tasks checked)")
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


def cmd_deltas(args: argparse.Namespace) -> None:
    """Read-only: report all open lessons learned grouped by competency.

    Scans every .add/tasks/*/TASK.md '### Competency deltas' block for lines
    matching the delta grammar; shows only `open` entries in canonical competency
    order (DDD·SDD·UDD·TDD·ADD). --json emits one JSON object. Exit 0 ALWAYS.
    Writes NOTHING."""
    root = _require_root()
    by_comp = _collect_open_deltas(root)
    total = sum(len(v) for v in by_comp.values())

    if getattr(args, "json", False):
        payload: dict = {
            "total": total,
            "by_competency": {c: v for c, v in by_comp.items() if v},
        }
        print(json.dumps(payload, ensure_ascii=False))
        return

    if total == 0:
        print("no open deltas.")
        return

    print(f"open lessons learned ({total} total):")
    for comp in _COMPETENCY_ORDER:
        entries = by_comp[comp]
        if not entries:
            continue
        print(f"  {comp} ({len(entries)}):")
        for e in entries:
            print(f"    - {e['text']}  [{e['task']}]")


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
        slug = state.get("active_task")
        if not slug or slug not in tasks:
            _die("no_active_task — name one: add.py report <milestone> <task> --decide")
        drill_task = slug
        mslug = tasks[slug].get("milestone") or ""
    else:                                         # no positional -> active milestone
        mslug = state.get("active_milestone")
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
    pi.set_defaults(func=cmd_init)

    pl = sub.add_parser("lock",
                        help="freeze the autonomous setup (the human baseline approval) and open the build")
    pl.add_argument("--by", default=None, help="who is locking (default: current OS user)")
    pl.add_argument("--layers", default=None,
                    help="comma-separated lock layers (default: foundation,scope,contract)")
    pl.add_argument("--force", action="store_true", help="re-lock an already-locked project")
    pl.add_argument("--json", action="store_true", help="emit one JSON object instead of text")
    pl.set_defaults(func=cmd_lock)

    pn = sub.add_parser("new-task", help="scaffold a new task (TASK.md + tests/ + src/)")
    pn.add_argument("slug")
    pn.add_argument("--title", default=None)
    pn.add_argument("--milestone", default=None, help="attach to a milestone (default: active)")
    pn.add_argument("--depends-on", dest="depends_on", default=None,
                    help="comma-separated task slugs this task depends on")
    pn.add_argument("--force", action="store_true", help="overwrite TASK.md if present")
    pn.set_defaults(func=cmd_new_task)

    pm = sub.add_parser("new-milestone", help="scaffold a milestone (SDD living doc)")
    pm.add_argument("slug")
    pm.add_argument("--title", default=None)
    pm.add_argument("--goal", default=None, help="one-sentence outcome")
    pm.add_argument("--stage", default="mvp", choices=STAGES)
    pm.add_argument("--force", action="store_true", help="overwrite MILESTONE.md if present")
    pm.set_defaults(func=cmd_new_milestone)

    pr = sub.add_parser("ready", help="list tasks whose dependencies are satisfied")
    pr.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pr.set_defaults(func=cmd_ready)

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

    pam = sub.add_parser("archive-milestone",
                         help="collapse a done milestone out of active state (files stay on disk)")
    pam.add_argument("slug")
    pam.set_defaults(func=cmd_archive_milestone)

    pco = sub.add_parser("compact",
                         help="heavy archive: move an archived milestone's files into "
                              ".add/archive/<slug>/ (recoverable reverse move)")
    pco.add_argument("slug")
    pco.set_defaults(func=cmd_compact)

    pp = sub.add_parser("phase", help="set a task's phase explicitly")
    pp.add_argument("phase", choices=PHASES)
    pp.add_argument("slug", nargs="?", default=None)
    pp.set_defaults(func=cmd_phase)

    pa = sub.add_parser("advance", help="move a task to the next phase")
    pa.add_argument("slug", nargs="?", default=None)
    pa.set_defaults(func=cmd_advance)

    pg = sub.add_parser("gate", help="record a verify gate outcome")
    pg.add_argument("outcome", choices=GATES)
    pg.add_argument("slug", nargs="?", default=None)
    pg.add_argument("--owner", help="RISK-ACCEPTED waiver: accountable owner")
    pg.add_argument("--ticket", help="RISK-ACCEPTED waiver: tracking ticket/link")
    pg.add_argument("--expires", help="RISK-ACCEPTED waiver: expiry date")
    pg.set_defaults(func=cmd_gate)

    pr = sub.add_parser("reopen", help="return a done task to an earlier phase with a recorded reason")
    pr.add_argument("slug", nargs="?", default=None)
    # --to / --reason are validated in-body (not argparse choices) so the named reject
    # codes fire (reopen_target_invalid / reopen_reason_required), not a bare exit-2.
    pr.add_argument("--to", default=None, help="target phase (specify..observe)")
    pr.add_argument("--reason", default="", help="why the task is reopened (required, non-empty)")
    pr.set_defaults(func=cmd_reopen)

    ps = sub.add_parser("stage", help="set the project stage")
    ps.add_argument("stage", choices=STAGES)
    ps.add_argument("--force", action="store_true",
                    help="override the →production roadmap guard (stage_no_roadmap)")
    ps.set_defaults(func=cmd_stage)

    pst = sub.add_parser("status", help="print where the project is (resume point)")
    pst.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pst.set_defaults(func=cmd_status)

    pck = sub.add_parser("check", help="read-only integrity check of the .add project")
    pck.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pck.set_defaults(func=cmd_check)

    psg = sub.add_parser("sync-guidelines",
                         help="(re)write the ADD guideline block into AGENTS.md + CLAUDE.md")
    psg.set_defaults(func=cmd_sync_guidelines)

    pgd = sub.add_parser("guide", help="print the one concrete next step for the active task")
    pgd.add_argument("slug", nargs="?", default=None, help="task slug (default: active task)")
    pgd.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pgd.set_defaults(func=cmd_guide)

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
    prp.set_defaults(func=cmd_report)

    pdt = sub.add_parser("deltas",
                         help="read-only report: open lessons learned grouped by competency")
    pdt.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pdt.set_defaults(func=cmd_deltas)

    pgr = sub.add_parser("graduation-report",
                         help="read-only: gather the MVP loop's evidence (deltas · waivers · RETROs · "
                              "residue · coverage gaps) for a graduation interview — gathers, never judges")
    pgr.add_argument("--json", action="store_true", help="emit the frozen JSON facts interface")
    pgr.add_argument("--plain", action="store_true", help="ASCII/pipe-safe text (output is plain by default)")
    pgr.set_defaults(func=cmd_graduation_report)

    pau = sub.add_parser("audit",
                         help="read-only: verify recorded human decision points left well-formed records "
                              "(exit 1 on findings — the CI enforcement gate)")
    pau.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pau.set_defaults(func=cmd_audit)

    ppj = sub.add_parser("project", help="print .add/PROJECT.md (the read-first foundation)")
    ppj.set_defaults(func=cmd_project)

    # --- independent verification (Generator–Verifier auto-gate) -------------
    pvd = sub.add_parser("verdict",
                         help="record an independent verifier's structured verdict "
                              "(append-only ledger; validated before write)")
    pvd.add_argument("slug", nargs="?", default=None)
    pvd.add_argument("--lens", default=None,
                     help="which independent verifier (e.g. wiring, concurrency-security, "
                          "contract-conformance)")
    pvd.add_argument("--verdict", choices=VERDICT_VALUES, default=None, help="this lens's call")
    pvd.add_argument("--evidence", default=None,
                     help="what the verifier observed (required — no shallow verify)")
    pvd.add_argument("--refutation", default=None,
                     help="the strongest counter-argument it tried and the result")
    pvd.add_argument("--security", action="store_true",
                     help="mark this a security finding (forces HARD-STOP, never auto-passed)")
    pvd.add_argument("--file", default=None,
                     help="read a verdict object or JSON array from a file ('-' = stdin)")
    pvd.set_defaults(func=cmd_verdict)

    pcs = sub.add_parser("consensus",
                         help="read-only: compute the auto-gate decision "
                              "(PASS · HARD-STOP · ESCALATE) from recorded verdicts")
    pcs.add_argument("slug", nargs="?", default=None)
    pcs.add_argument("--min-lenses", type=int, default=MIN_CONSENSUS_LENSES, dest="min_lenses",
                     help="distinct lenses required for an auto-PASS (self-consistency)")
    pcs.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pcs.set_defaults(func=cmd_consensus)

    pev = sub.add_parser("eval",
                         help="read-only: score the consensus decision logic against "
                              "labeled verdict fixtures (recall = no seeded-bad build slips through)")
    pev.add_argument("--fixtures", default=None,
                     help="dir of *.json fixtures ({verdicts, label}); default .add/eval/")
    pev.add_argument("--min-lenses", type=int, default=MIN_CONSENSUS_LENSES, dest="min_lenses")
    pev.add_argument("--json", action="store_true", help="machine-readable JSON output")
    pev.set_defaults(func=cmd_eval)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
