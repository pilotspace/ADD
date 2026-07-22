#!/usr/bin/env python3
"""add_engine.io_state — low-level IO + state primitives for the ADD engine.

The 4 atomic-write primitives (designed for failure: temp-then-rename, no silent
clobber, all-or-nothing for the many-writer). Extracted from add.py (engine-
modularization 2/N); add.py re-exports them as module globals so callers and
monkeypatch sites (`add._atomic_write = spy`) keep resolving unchanged.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from add_engine.constants import ROOT_DIRNAME, STATE_FILE

_CONFLICT_MARKER_RE = re.compile(r"(?m)^(<{7}|={7}|>{7})")  # git merge-conflict markers in state


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


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    """Binary sibling of `_atomic_write` — lands `data` UNCHANGED (no newline translation), so a
    byte-for-byte copy stays exact. Same temp-then-replace crash-safety."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _atomic_write_many(writes: list[tuple[Path, str]]) -> None:
    """True all-or-nothing commit across N files — design-for-failure for a multi-file write.

    Phase 1 STAGES every (path, text) to a sibling `.tmp`, flushing + fsync-ing each, so the
    realistic IO failures (disk full, permission denied) surface HERE, before any target changes —
    and on any stage failure every staged temp is removed, so NOTHING is committed. Phase 2 then
    COMMITS each file by renaming any existing target ASIDE to a sibling `.bak`, then `os.replace`-ing
    the staged `.tmp` into place. If ANY commit rename raises, every file already committed is rolled
    back IN REVERSE (remove the landed new file, rename its `.bak` back, or leave it absent) and the
    original error re-raised — so the whole set is all-or-nothing: either every file holds its new
    text, or every file holds its prior content. Restoring is an atomic rename of an already-written
    `.bak` (no content held in memory, no re-write), the cheapest recovery under failing IO. Leftover
    `.tmp`/`.bak` siblings are removed on every exit path.
    """
    staged: list[tuple[str, Path]] = []
    committed: list[list] = []                    # [path, bak_or_None, new_landed] per committed file
    try:
        for path, text in writes:                 # phase 1: stage every temp (fsync'd before any commit)
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
            staged.append((tmp, path))            # track BEFORE write so a write/fsync failure still cleans it
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
                fh.flush()
                os.fsync(fh.fileno())
        try:
            for tmp, path in staged:              # phase 2: commit via rename-aside
                bak = None
                existed = path.exists()
                if existed:
                    fd2, bak = tempfile.mkstemp(dir=str(path.parent), suffix=".bak")
                    os.close(fd2)
                committed.append([path, bak, False])   # track .bak NOW so cleanup never leaks it
                if existed:
                    os.replace(path, bak)         # move the existing target aside
                os.replace(tmp, path)             # move the new file in
                committed[-1][2] = True
        except OSError:
            for path, bak, landed in reversed(committed):   # roll back, newest-first
                try:
                    if landed and path.exists():
                        os.unlink(path)           # drop the new file we put in
                    if bak is not None and not path.exists():
                        os.replace(bak, path)     # restore the prior target (atomic rename)
                except OSError:
                    pass                          # best-effort restore under already-failing IO
            raise
    finally:
        for tmp, _ in staged:                     # leftover .tmp (failed/aborted stage) never persists
            if os.path.exists(tmp):
                os.unlink(tmp)
        for path, bak, landed in committed:       # leftover .bak (success, or orphaned post-rollback)
            if bak is not None and os.path.exists(bak):
                os.unlink(bak)


# --- root finding + state load/save + the shared error primitive ------------

def find_root(start: Path | None = None) -> Path | None:
    """Walk up from cwd to find a .add/ project root.

    Opt-in boundary: when `ADD_ROOT_CEILING` is set, the walk stops at that dir
    (inclusive) and never ascends above it — so a workspace nested under an
    ancestor project resolves ONLY its own root (or None before init), never the
    parent's. Unset (every normal invocation) is the legacy walk to fs-root,
    byte-identical. Both paths are resolved so a symlinked ceiling still matches.
    """
    cur = (start or Path.cwd()).resolve()
    _ceil = os.environ.get("ADD_ROOT_CEILING")
    ceil = Path(_ceil).resolve() if _ceil else None
    for d in (cur, *cur.parents):
        if (d / ROOT_DIRNAME / STATE_FILE).exists():
            return d / ROOT_DIRNAME
        if ceil is not None and d == ceil:
            break
    return None

def _require_root() -> Path:
    root = find_root()
    if root is None:
        # skip-error-ergonomics M2: hand the exact command with its flags — the
        # bare "run init first" hint made every fresh headless agent read
        # `init --help` before its first real call (LOOP-2 re-measure, all reps).
        _die('no .add/ project found — run: add.py init --name "<project>" '
             "--stage <prototype|poc|mvp|production>")
    return root

def _migrate_state(state: dict) -> dict:
    """Forward-migrate a single-active state to the multi-active schema (team-collaboration
    foundation). PURE · idempotent · TOTAL · never raises · no I/O.

    A state lacking the `active_milestones` key gains it — DERIVED from the scalar
    `active_milestone` (grandfather-by-missing-key, mirroring `_setup_locked`): None -> [],
    "x" -> ["x"]. A per-milestone active-task map `active_tasks` is added; the old global
    `active_task` is placed under its owning active milestone only when it genuinely belongs
    there, else it stays as the top-level scalar fallback (orphan rule, FROZEN decision (a)).
    The scalar `active_milestone` / `active_task` keys are KEPT as the N<=1 mirror so the
    not-yet-routed readers keep working. An already-migrated state (key present) is returned
    unchanged — never re-derived, never clobbered. Corrupt parsing stays the loader's job.

    PURE in the observable sense: the caller's dict is NEVER mutated — a state that needs
    migrating is upgraded on a fresh top-level copy (nested objects are shared but only read)."""
    if not isinstance(state, dict) or "active_milestones" in state:
        return state
    migrated = dict(state)
    active_ms = migrated.get("active_milestone")
    migrated["active_milestones"] = [] if active_ms is None else [active_ms]
    active_task = migrated.get("active_task")
    tasks = migrated.get("tasks") or {}
    owns = (active_ms is not None and active_task is not None
            and isinstance(tasks.get(active_task), dict)
            and tasks[active_task].get("milestone") == active_ms)
    migrated["active_tasks"] = {active_ms: active_task} if owns else {}
    return migrated

def _state_text_or_die(root: Path) -> str:
    """Read state.json's raw text, failing CLOSED with a merge-SPECIFIC `state_conflicted`
    message when it carries git conflict markers (an unresolved merge — the major's #1 failure
    mode). A genuine read OSError is NOT swallowed: it propagates to the caller, which maps it
    to its own existing code (state_invalid / no_state). The guard only READS — never writes."""
    text = (root / STATE_FILE).read_text(encoding="utf-8")
    if _CONFLICT_MARKER_RE.search(text):
        _die(f"state_conflicted: {root / STATE_FILE} has unresolved git merge markers "
             f"(<<<<<<< / ======= / >>>>>>>) — resolve them (or "
             f"`git checkout --ours/--theirs {STATE_FILE}`), then run `add.py doctor` to verify")
    return text

# kickoff-truth M3 (contract v2): the dup-failure short-circuit. The 2026-07-13
# transcript audit measured 12-21% of all engine calls as byte-identical repeats of
# a call that had just failed the same way — the agent re-issues the command
# unchanged instead of reading the error. The sig sidecar lives OUTSIDE the project
# tree (OS tmp dir, keyed by md5(root path)): the engine's reject-writes-nothing
# floor pins that a REJECTED command leaves the .add tree byte-identical, so the
# hint state is ephemeral per-project cache, never a tree write. add.main()
# registers each invocation and clears the sidecar on any successful exit, so only
# CONSECUTIVE identical failures short-circuit. Fail-open everywhere: no root /
# unreadable sidecar / any OSError -> no hint, never a block — a hint helper must
# never change an error's outcome.
_INVOCATION: list[str] | None = None    # set by add.main() per dispatch

def _register_invocation(argv: list[str]) -> None:
    global _INVOCATION
    _INVOCATION = list(argv)

def _last_fail_path() -> Path | None:
    root = find_root()
    if root is None:
        return None
    key = hashlib.md5(str(root.resolve()).encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / f"add-last-fail-{key}.json"

def _clear_last_fail() -> None:
    try:
        side = _last_fail_path()
        if side is not None:
            side.unlink(missing_ok=True)
    except OSError:
        pass                            # hygiene only — success must never fail on it

def _dup_fail_hint(msg: str) -> str | None:
    try:
        side = _last_fail_path()
        if side is None:
            return None
        argv = _INVOCATION if _INVOCATION is not None else sys.argv[1:]
        code_head = msg.split(":", 1)[0].strip()
        sig = hashlib.md5((" ".join(argv) + "\n" + code_head).encode("utf-8")).hexdigest()
        hint = None
        if side.exists() and json.loads(side.read_text(encoding="utf-8")).get("sig") == sig:
            hint = ("hint: this exact call already failed with the same error — change "
                    "the command or input before retrying (add.py status shows the true state)")
        side.write_text(json.dumps({"sig": sig}), encoding="utf-8")
        return hint
    except (OSError, ValueError):
        return None

def _die(msg: str, code: int = 1) -> None:
    hint = _dup_fail_hint(msg)          # kickoff-truth M3 — fail-open, never raises
    print(f"add: error: {msg}", file=sys.stderr)
    if hint:
        print(hint, file=sys.stderr)
    raise SystemExit(code)


def _load_state_for_json() -> tuple[Path, dict]:
    """Fail-closed state load for `--json` paths: a missing project or unparseable
    state.json -> `no_state` on stderr + exit 1, with EMPTY stdout (never a partial
    JSON object a harness might parse). Built from State only — reads no docs/ chapter.
    The parsed state is forward-migrated to the multi-active schema before it is returned."""
    root = find_root()
    if root is None:
        _die("no_state")
    try:
        return root, _migrate_state(json.loads(_state_text_or_die(root)))
    except (json.JSONDecodeError, OSError):
        _die("no_state")


def _md5_text(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def _md5_file(p: Path) -> str | None:
    """md5 of a file's bytes; None on ANY read error (fail-closed — a tracked file
    that cannot be read counts as DIVERGED at the gate, never a crash)."""
    try:
        return hashlib.md5(p.read_bytes()).hexdigest()
    except OSError:
        return None


def _personas_unseeded(root: Path) -> bool:
    """True when `.add/personas/` has no REAL (non-template) authored persona: the
    directory is absent, empty, or holds only a `_template.md` scaffold (personas are
    authored via the persona-author skill, not seeded). Fail-soft: an unreadable directory
    counts as unseeded rather than raising — this feeds a `note:`/INFO hint, never a gate."""
    d = root / "personas"
    if not d.is_dir():
        return True
    try:
        return not any(p.stem != "_template" for p in d.glob("*.md"))
    except OSError:
        return True


def _real_persona_slugs(root: Path) -> list[str]:
    """Sorted slugs of REAL (non-template) personas under `.add/personas/` — the existence-only
    listing persona-fit-nudge names in its hint. Fail-soft: an unreadable/absent dir is empty,
    mirroring `_personas_unseeded`'s own fail-soft convention."""
    d = root / "personas"
    if not d.is_dir():
        return []
    try:
        return sorted(p.stem for p in d.glob("*.md") if p.stem != "_template")
    except OSError:
        return []
