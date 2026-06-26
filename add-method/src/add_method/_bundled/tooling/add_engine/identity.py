"""add_engine.identity — the git-native actor/identity seam (engine-modularization 6/N).

The 7 identity/actor functions, moved verbatim from add.py: git/OS actor resolution
(`_git_config` · `_os_user` · `_whoami`), the structured stamp every human-written
action records (`_actor_stamp` · `_render_actor_line`), and ownership parsing/matching
(`_parse_actor_arg` · `_actor_matches`).

NOT a pure-move leaf: add.py commands call `_whoami` BOTH directly and via `_actor_stamp`,
so add.py QUALIFIES its call sites to `identity._whoami(...)` and the identity tests patch
`add_engine.identity.<name>` — one target that reaches every call path (direct + internal).
Stdlib-only deps (getpass/re/shutil/subprocess); no add_engine imports (a leaf).
"""
from __future__ import annotations

import getpass
import re
import shutil
import subprocess


def _git_config(key: str) -> str | None:
    """Read one `git config --get <key>`, STRICTLY fail-soft: the engine's FIRST git call,
    so it never raises, never hangs, never shells. Returns the trimmed value, or None when
    git is absent / errors / times out / the value is empty."""
    if shutil.which("git") is None:
        return None
    try:
        out = subprocess.run(
            ["git", "config", "--get", key],
            capture_output=True, text=True, timeout=2,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError, ValueError):
        # OSError: git vanished between which() and run() / spawn error · SubprocessError:
        # TimeoutExpired · ValueError: a non-UTF-8 config value (latin-1 legacy name) makes
        # text=True decoding raise UnicodeDecodeError (a ValueError) — all fail soft to None.
        return None
    return out or None


def _os_user() -> str:
    """The guaranteed non-empty OS floor. getpass.getuser() reads LOGNAME/USER/... then
    falls back to the passwd database — but in a bare container (no env var AND no passwd
    entry) CPython raises KeyError (OSError only on 3.13+). Catch broadly and return a
    sentinel so _whoami stays TOTAL: it always yields a non-empty name, never crashes."""
    try:
        return getpass.getuser() or "unknown"
    except (KeyError, OSError):
        return "unknown"


def _whoami(state: dict) -> dict:
    """Resolve the current git-native ACTOR -> {name, email, source}. Priority:
    (1) an `actor_override` (whoami --set) with a non-blank name -> source 'override';
    (2) `git config user.name`/`user.email` -> source 'git';
    (3) the OS user (_os_user) -> source 'os', the guaranteed non-empty floor.
    Total: always returns a dict with a non-empty name; `email` may be None."""
    ov = state.get("actor_override")
    if ov and (ov.get("name") or "").strip():
        return {"name": ov["name"], "email": ov.get("email"), "source": "override"}
    name = _git_config("user.name")
    if name:
        return {"name": name, "email": _git_config("user.email"), "source": "git"}
    return {"name": _os_user(), "email": None, "source": "os"}


def _actor_stamp(state: dict) -> dict:
    """The SINGLE source of the structured-actor stamp every engine-WRITTEN human action
    records — lock · gate · milestone-done · release (user-identity actor-stamping). It IS
    `_whoami(state)`: a TOTAL {name,email,source} (always a non-empty name), so a stamp can
    never fail or block a write. Descriptive only — no command's decision reads it."""
    return _whoami(state)


def _render_actor_line(state: dict) -> str:
    """Render the actor stamp as one human-readable line: name, an optional angle-bracketed
    email, then the source in parens — used on the RELEASES.md row (no state.json write)."""
    a = _actor_stamp(state)
    email = f" <{a['email']}>" if a.get("email") else ""
    return f"{a['name']}{email} ({a['source']})"


def _parse_actor_arg(s: str) -> dict:
    """Parse an `assign --owner`/`--assignee` value into a {name, email, source: "assigned"}
    actor (ownership-assignment). "Name <email>" -> both; a bare "Name" -> email None. TOTAL:
    a malformed value (no closing bracket) never raises — the whole stripped string is the name.
    `source` is "assigned" — a human typed this name (not git-resolved nor an ADD override)."""
    m = re.match(r"^\s*(.*?)\s*<([^>]*)>\s*$", s)
    if m:
        return {"name": m.group(1), "email": m.group(2) or None, "source": "assigned"}
    return {"name": s.strip(), "email": None, "source": "assigned"}


def _actor_matches(rec_actor: dict | None, me: dict) -> bool:
    """Does a recorded owner/assignee actor identify the SAME person as `me` (multi-active-UX)?
    Email-first (the stabler key): when BOTH carry a non-empty email, emails decide; otherwise
    fall back to name-equality. Both comparisons are stripped + case-insensitive. TOTAL — a None,
    non-dict, or blank-name record returns False (an unowned/garbage slot is no one's)."""
    if not isinstance(rec_actor, dict):
        return False
    rec_name = (rec_actor.get("name") or "").strip()
    if not rec_name:
        return False
    rec_email = (rec_actor.get("email") or "").strip()
    me_email = (me.get("email") or "").strip()
    if rec_email and me_email:
        return rec_email.lower() == me_email.lower()
    return rec_name.lower() == (me.get("name") or "").strip().lower()
