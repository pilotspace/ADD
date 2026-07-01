"""Core installer — Python analog of bin/cli.js.

DROPS FILES ONLY — does NOT run `add.py init`. Initialisation is deferred to the AI
(via `/add`, which runs `init --await-lock` to arm the v12 lock-down gate) or a CLI user.
A pre-run plain init would grandfather-lock the gate before `/add` runs AND consume the
brownfield signal in the terminal, where the AI never sees it.

Designed for failure:
- Verifies bundled sources exist before touching target.
- Never clobbers an existing skill (skip-if-exists unless --force).
- Uses shutil.copytree with dirs_exist_ok=True so a re-install refreshes
  tooling/docs without destroying the existing project structure.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.resources
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# The managed layer — ship-controlled trees `update` re-materializes from the package.
# (bundled subpath, dest relative to target, strip dev-only test_*.py after copy)
MANAGED = (
    ("skill/add", ".claude/skills/add", False),
    ("tooling", ".add/tooling", True),
    ("docs", ".add/docs", False),
    ("personas-teacher", ".add/personas-teacher", False),
)
# Optional managed trees: an ENHANCEMENT the persona phase reads, not core runtime.
# The real package always ships these (guarded by test_packaging + test_bundle_parity);
# but a malformed/older package missing one must NOT abort the whole install — the core
# (skill/tooling/docs) still lands, and the optional tree is soft-skipped. Design-for-failure.
OPTIONAL = frozenset({"personas-teacher"})
STAMP_FILE = ".add-version"          # records the materialized version, under .add/
# Forward-only, idempotent state migrations keyed by the version that introduces them.
# Empty today — the framework exists so the NEXT schema change is an in-place update,
# never a re-install. Each value is callable(state: dict) -> dict.
MIGRATIONS: dict = {}


def _log(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def _fail(msg: str) -> int:
    sys.stderr.write("error: " + msg + "\n")
    sys.stderr.flush()
    return 1


# --- interactive layer (stdlib input(); npm's clack twin — NO new dependency) ---
# Mirrors bin/cli.js: interactive only on a real terminal, byte-identical plain text
# everywhere else. clack is Node-only, so pip uses a single stdlib input() confirm.
CANCEL = object()  # sentinel: the user aborted before any write


def _interactive(yes: bool, non_interactive: bool) -> bool:
    if yes or non_interactive:
        return False
    seam = os.environ.get("ADD_INSTALLER_FORCE_INTERACTIVE")
    if seam in ("1", "fail"):       # documented test seam (parity with cli.js)
        return True
    return (
        sys.stdin.isatty()
        and sys.stdout.isatty()
        and not os.environ.get("CI")
    )


def _prompt_target(default_path: Path):
    """Confirm the target directory. Enter accepts the default; a typed path overrides.
    A cancel (EOF / Ctrl-C) returns CANCEL — the caller writes nothing.

    Deliberately a SINGLE confirm (npm's clack flow has a second write-confirm step):
    "parity ENOUGH" is the accepted §1 A2 assumption — a richer pip prompt is a deferred
    follow-up per the milestone Out-list, not a parity bug."""
    try:
        resp = input(
            f"Install ADD into target directory [{default_path}] "
            "(Enter to confirm, or type a path): "
        ).strip()
    except (EOFError, KeyboardInterrupt):
        return CANCEL
    if not resp:
        return default_path
    return Path(resp).expanduser().resolve()


# The two install-scope choices — global-first (recommended) vs self-contained. A PURE seam
# (the npm scopeOptions twin) so the recommended pick + its why are hermetically testable.
_SCOPE_OPTIONS = (
    {"value": "global", "label": "Global home + this project",
     "hint": "a shared ~/.add + ~/.claude/skills/add reused by every project "
             "(this project still gets its own copy)",
     "recommended": True},
    {"value": "project", "label": "This project only",
     "hint": "self-contained + git-tracked: nothing is written outside this folder"},
)


def _scope_options():
    """The scope choices, global recommended first. Returns fresh dicts (callers never mutate
    the module constant)."""
    return [dict(o) for o in _SCOPE_OPTIONS]


def _prompt_scope(default_global: bool = True):
    """Global-first scope step on the INTERACTIVE path: show the recommended global home (▶)
    and the project-only alternative, then confirm. Enter accepts the recommended default;
    'n'/'no' picks project-only; a cancel (EOF / Ctrl-C) returns CANCEL — the caller writes
    nothing. Mirrors _prompt_target's single confirm (lean pip UI, npm clack twin)."""
    rec = next(o for o in _scope_options() if o.get("recommended"))
    alt = next(o for o in _scope_options() if not o.get("recommended"))
    caps = _terminal_caps(os.environ)
    arrow = "▶" if caps["unicode"] else ">"      # caps-aware marker; ASCII fallback (design-for-failure)
    _log(f"  {arrow} {rec['label']} - {rec['hint']}")
    _log(f"    {alt['label']} - {alt['hint']}")
    suffix = "[Y/n]" if default_global else "[y/N]"
    try:
        resp = input(f"Set up the global ADD home (recommended)? {suffix} ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return CANCEL
    if not resp:
        return default_global
    if resp in ("y", "yes"):
        return True
    if resp in ("n", "no"):
        return False
    return default_global       # unrecognized input -> the recommended default (never silently global-off)


def _prompt_intent() -> str:
    """Optional LAST step: capture a one-line build intent for `/add` to read. Fully optional —
    Enter / empty / EOF / Ctrl-C all SKIP (return ""); this prompt NEVER cancels (the install has
    already succeeded by the time it runs). Returns the stripped intent, or ""."""
    try:
        return input("What do you want to build first? (optional — Enter to skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def _write_intent_note(target, intent: str) -> bool:
    """Persist `intent` as a NOTE at <target>/.add/.intent for `/add` to read — iff non-empty.
    DEFERRED-INIT: this writes inert text only; it NEVER runs add.py/init and NEVER touches
    state.json. Fail-soft: a write error is swallowed (the note is a best-effort handoff, never
    a reason to fail a successful install). Returns whether the note was written."""
    text = (intent or "").strip()
    if not text:
        return False
    try:
        add_dir = Path(target) / ".add"
        add_dir.mkdir(parents=True, exist_ok=True)      # .add/ exists post-drop; mkdir is a no-op then
        (add_dir / ".intent").write_text(text + "\n", encoding="utf-8")
        return True
    except OSError:
        return False                                    # design-for-failure: never abort the install


def _write_gemini_settings(target) -> str:
    """Merge <target>/.gemini/settings.json so context.fileName includes "AGENTS.md", the pointer
    file ADD writes for the gemini profile. Gemini CLI defaults to GEMINI.md and lets GEMINI.md win
    when both exist, so AGENTS.md must be named in the config to be loaded. Read-merge-write:
    preserves every other key; idempotent (a second run is a no-op); fail-soft (an unparsable or
    unwritable file warns + skips and is left byte-untouched — never raises, never aborts the drop).
    Returns created|updated|unchanged|skipped. Twin of bin/cli.js:writeGeminiSettings."""
    gemini_dir = Path(target) / ".gemini"
    settings = gemini_dir / "settings.json"
    try:
        if settings.exists():
            try:
                data = json.loads(settings.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                sys.stderr.write(f"warn: could not parse {settings} — leaving it untouched; skipped\n")
                return "skipped"
            if not isinstance(data, dict):
                sys.stderr.write(f"warn: {settings} is not a JSON object — leaving it untouched; skipped\n")
                return "skipped"
            created = False
        else:
            data = {}
            created = True
        context = data.get("context")
        if not isinstance(context, dict):
            context = {}
        names = context.get("fileName")
        if isinstance(names, str):
            names = [names]
        elif not isinstance(names, list):
            names = []
        if "AGENTS.md" in names:
            return "unchanged"                          # idempotent: nothing to add
        names = names + ["AGENTS.md"]
        context["fileName"] = names
        data["context"] = context
        gemini_dir.mkdir(parents=True, exist_ok=True)
        settings.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return "created" if created else "updated"
    except OSError as e:
        sys.stderr.write(f"warn: could not write {settings} — {e}; skipped\n")
        return "skipped"                                # design-for-failure: never abort the install


# --- brand + feature showcase (interactive path only; fail-soft) ----------------
# The 7 post-ground ADD phases the showcase names — grounded in the method (the
# PROJECT.md goal + the engine's phase flow), never invented marketing. The wordmark
# glyphs / tagline / accent are a SWAPPABLE content slot, not part of the frozen boundary.
_LOOP = ("Specify", "Scenarios", "Contract", "Tests", "Build", "Verify", "Observe")


def _terminal_caps(env):
    try:
        width = int(env.get("COLUMNS") or 0)
    except (TypeError, ValueError):
        width = 0
    if not width:
        try:
            width = os.get_terminal_size().columns
        except OSError:
            width = 80
    enc = (env.get("LC_ALL") or env.get("LC_CTYPE") or env.get("LANG") or "")
    unicode_ok = "utf" in enc.lower() and not env.get("ADD_INSTALLER_ASCII")
    return {"width": width, "unicode": unicode_ok}


def _brand_lines(caps):
    wide = caps["width"] >= 40
    uni = caps["unicode"]
    head = [
        " █████╗ ██████╗ ██████╗",
        "██╔══██╗██╔══██╗██╔══██╗",
        "███████║██║  ██║██║  ██║",
        "██╔══██║██║  ██║██║  ██║",
        "██║  ██║██████╔╝██████╔╝",
        "╚═╝  ╚═╝╚═════╝ ╚═════╝ ",
    ] if (uni and wide) else ["ADD"]          # plain-ASCII wordmark fallback
    arrow = " → " if uni else " -> "
    dash = " — " if uni else " - "
    return [
        *head,
        "AI-Driven Development",
        "",
        "Spec-and-tests-first development" + dash + "any agent, through the CLI, no lost context.",
        "The loop ADD drives with you:",
        "  " + arrow.join(_LOOP),
        "",
    ]


def _render_brand(env=None, stream=None) -> None:
    """Wordmark + value line + the 7-step loop, on the INTERACTIVE path only. Fail-soft:
    any error is swallowed — a banner must NEVER abort the install. No color is emitted
    (default accent: none). On a non-UTF-8 stream the unicode render is retried as pure
    ASCII so the showcase still appears."""
    env = os.environ if env is None else env
    out = stream if stream is not None else sys.stdout
    caps = _terminal_caps(env)
    for attempt_unicode in (caps["unicode"], False):
        try:
            out.write("\n".join(_brand_lines(dict(caps, unicode=attempt_unicode))) + "\n")
            out.flush()
            return
        except UnicodeEncodeError:
            continue                          # retry as ASCII
        except Exception:
            return                            # fail-soft: never abort the install for a banner


def _bundled_root() -> Path:
    """Return a concrete filesystem path to src/add_method/_bundled/.

    importlib.resources.files() returns a real Path for pip-installed
    (non-zip) wheels. A zip-import scenario is flagged as unsupported.
    """
    ref = importlib.resources.files("add_method") / "_bundled"
    # Materialise to a concrete path — as_file() on a directory is unreliable
    # on Python 3.10/3.11; for non-zip installs the traversable IS a Path.
    path = Path(str(ref))
    if not path.exists():
        raise RuntimeError(
            f"Bundled data not found at {path}. "
            "This may happen if the package was installed from a zip archive "
            "(e.g. a .egg or a zipped wheel). Install from PyPI with pip into "
            "a normal site-packages directory."
        )
    return path


# --- agent detection: which coding agent is invoking the installer -----------
# An ORDERED registry; _detect_agent walks it top->bottom, first match wins, `generic`
# is the fallback. Mirrored by behaviour in bin/cli.js (AGENT_PROFILES). The per-agent
# env SIGNAL is best-effort: a mis-detect degrades to generic (today's working path) and
# is overridable in the interactive confirm — refine via a SPEC delta, never a hard fail.
_GENERIC_NEXT = (
    "open your AI Agent CLI (like Claude Code, Codex, etc.), then run `/add`, and "
    "say what you want to build — the agent sets up the foundation, sizes it into a "
    "milestone, and drives the build with you; you sign off once, at the lock-down."
)
AGENT_PROFILES = (
    {"id": "claude", "label": "Claude Code / Claude app", "integration_file": "CLAUDE.md",
     "env": ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT"), "env_prefix": None,
     "next_step": "Open Claude Code and run `/add` — the skill drives intake -> milestone -> build."},
    {"id": "codex", "label": "Codex", "integration_file": "AGENTS.md",
     "env": ("CODEX_HOME",), "env_prefix": "CODEX_",
     "next_step": "Open Codex — it reads AGENTS.md; run `/add` or say what you want to build."},
    {"id": "opencode", "label": "OpenCode", "integration_file": "AGENTS.md",
     "env": ("OPENCODE",), "env_prefix": "OPENCODE",
     "next_step": "Open OpenCode — it reads AGENTS.md; say what you want to build."},
    {"id": "cursor", "label": "Cursor", "integration_file": "AGENTS.md",
     "env": ("CURSOR_AGENT", "CURSOR_TRACE_ID"), "env_prefix": "CURSOR_",
     "next_step": "Open Cursor — it reads AGENTS.md; say what you want to build."},
    {"id": "windsurf", "label": "Windsurf", "integration_file": "AGENTS.md",
     "env": ("WINDSURF", "WINDSURF_ENV"), "env_prefix": "WINDSURF_",
     "next_step": "Open Windsurf — Cascade reads AGENTS.md; say what you want to build."},
    {"id": "trae", "label": "Trae", "integration_file": "AGENTS.md",
     "env": ("TRAE_AI_IDE",), "env_prefix": "TRAE_",
     "next_step": "Open Trae — it reads AGENTS.md; say what you want to build."},
    {"id": "copilot", "label": "GitHub Copilot", "integration_file": "AGENTS.md",
     "env": ("COPILOT_AGENT",), "env_prefix": None,   # NOT a GITHUB_ prefix — too broad (CI sets GITHUB_*)
     "next_step": "Open GitHub Copilot — it reads AGENTS.md; say what you want to build."},
    {"id": "cline", "label": "Cline", "integration_file": ".clinerules",
     "env": ("CLINE_ACTIVE",), "env_prefix": "CLINE_",
     "next_step": "Open Cline — it reads .clinerules; say what you want to build."},
    {"id": "aider", "label": "Aider", "integration_file": "AGENTS.md",
     "env": (), "env_prefix": "AIDER_",
     "next_step": "Open Aider — add AGENTS.md to its context (`.aider.conf.yml` `read:` or `--read AGENTS.md`), then say what you want to build."},
    {"id": "gemini", "label": "Gemini CLI", "integration_file": "AGENTS.md",
     "env": ("GEMINI_CLI", "GEMINI_SANDBOX"), "env_prefix": "GEMINI_",
     "next_step": "Open Gemini CLI — ADD wired .gemini/settings.json to load AGENTS.md; say what you want to build."},
    {"id": "generic", "label": "your AI agent", "integration_file": "AGENTS.md",
     "env": (), "env_prefix": None, "next_step": _GENERIC_NEXT},
)

# The SAME markers add.py:sync-guidelines uses — so a later `/add`->init->sync-guidelines
# REPLACES this drop-time pointer in place (one block, never a duplicate).
_GUIDE_BEGIN = "<!-- ADD:BEGIN — managed by `add.py sync-guidelines`; do not edit inside -->"
_GUIDE_END = "<!-- ADD:END -->"


def _profile_matches(profile: dict, env) -> bool:
    """A profile matches if any of its env keys is truthy, or any env key carries its prefix."""
    for key in profile["env"]:
        if env.get(key):
            return True
    prefix = profile["env_prefix"]
    if prefix and any(k.startswith(prefix) for k, v in env.items() if v):
        return True
    return False


def _detect_agent(env=None) -> dict:
    """Pure, total, deterministic: same env -> same profile; never throws. Generic last."""
    env = os.environ if env is None else env
    generic = AGENT_PROFILES[-1]
    for profile in AGENT_PROFILES[:-1]:
        if _profile_matches(profile, env):
            return profile
    return generic


def _detect_agent_enriched(env=None, target=None, which=None) -> dict:
    """ADDITIVE enrichment for the INTERACTIVE default — never replaces _detect_agent (which
    stays env-only; test_agent_detect pins it, the non-interactive write uses it). Precedence:
    env signal (authoritative) > a CLAUDE.md in the target (repo signal; AGENTS.md is ambiguous,
    so it does NOT pick) > an installed agent CLI (machine signal; PATH lookup only) > generic.
    Pure + fail-soft: a throwing probe reads as absent."""
    env = os.environ if env is None else env
    which = shutil.which if which is None else which
    base = _detect_agent(env)
    if base["id"] != "generic":
        return base                                    # env signal wins
    by_id = {p["id"]: p for p in AGENT_PROFILES}
    try:
        if target is not None and (Path(target) / "CLAUDE.md").exists():
            return by_id["claude"]                     # repo signal
    except OSError:
        pass
    for agent_id in ("claude", "codex", "opencode", "cursor", "windsurf", "trae", "copilot", "cline", "aider"):
        try:
            if which(agent_id):
                return by_id[agent_id]                 # machine signal (no spawn)
        except OSError:
            continue
    return base                                        # generic


def _readiness_line(env=None, target=None, which=None) -> str:
    """Fail-soft pre-flight summary for the INTERACTIVE path (the caller gates):
    'Pre-flight: git <✓|–> · python3 <✓|–> · agent: <label>'. Each probe is a PATH lookup;
    a failure reads as absent. Never raises."""
    env = os.environ if env is None else env
    which = shutil.which if which is None else which
    caps = _terminal_caps(env)
    tick = "✓" if caps["unicode"] else "+"
    cross = "–" if caps["unicode"] else "-"
    sep = " · " if caps["unicode"] else " | "

    def have(cmd):
        try:
            return bool(which(cmd))
        except OSError:
            return False

    try:
        label = _detect_agent_enriched(env, target, which)["label"]
    except Exception:
        label = "your AI agent"
    mark = lambda ok: tick if ok else cross
    return (f"Pre-flight: git {mark(have('git'))}{sep}"
            f"python3 {mark(have('python3'))}{sep}agent: {label}")


def _agent_pointer_block(profile: dict) -> str:
    """The minimal, transitional drop-time pointer (superseded by the full block at init)."""
    return (
        f"{_GUIDE_BEGIN}\n"
        "## ADD — how to work in this repo\n"
        "\n"
        "This project uses **ADD (AI-Driven Development)**. The engine + book are installed.\n"
        "To begin: run `python3 .add/tooling/add.py status` (the resume point), read\n"
        "`.add/PROJECT.md`, then `python3 .add/tooling/add.py guide` for the current phase.\n"
        "\n"
        f"{profile['next_step']}\n"
        "\n"
        "This pointer is replaced by the full guideline block when `add.py sync-guidelines`\n"
        "runs (at `/add`->init). Edit outside the markers, not inside.\n"
        f"{_GUIDE_END}"
    )


def _write_agent_pointer(target, profile: dict) -> str:
    """Inject the ADD pointer into <target>/<integration_file>, mirroring add.py:_inject_block.

    created|updated|unchanged|skipped. Only the marked region is (re)written; content
    outside the markers is preserved; a real change backs up <file>.bak first. Designed for
    failure: an unwritable or non-UTF-8 target -> warn + 'skipped' (file left untouched)."""
    path = Path(target) / profile["integration_file"]
    block = _agent_pointer_block(profile)
    try:
        if path.exists():
            current = path.read_text(encoding="utf-8")
            begin = current.find(_GUIDE_BEGIN)
            if begin != -1:
                end = current.find(_GUIDE_END, begin)
                if end != -1:
                    end += len(_GUIDE_END)
                    new = current[:begin] + block + current[end:]
                else:                       # begin with no end: corrupt — append fresh
                    new = current.rstrip("\n") + "\n\n" + block + "\n"
            else:                           # no block yet — append, keep user content
                new = current.rstrip("\n") + "\n\n" + block + "\n"
            if new == current:
                return "unchanged"
            Path(str(path) + ".bak").write_text(current, encoding="utf-8")   # rollback path
            path.write_text(new, encoding="utf-8")
            return "updated"
        path.write_text(block + "\n", encoding="utf-8")
        return "created"
    except (OSError, UnicodeDecodeError) as exc:
        sys.stderr.write(f"warn: could not write {profile['integration_file']} — {exc}; skipped\n")
        sys.stderr.flush()
        return "skipped"


# --- rule-file mode: ccsk-style relocation of the CLAUDE.md block ----------------------
# Mirror of add.py's rule-file logic (twins by duplication). For ccsk projects (.ccsk/ dir)
# or an explicit --rule-file, the ADD pointer/block goes to .claude/rules/add-workflows.md
# and CLAUDE.md keeps only a reference bullet. CLAUDE-only: .claude/rules/ is a Claude
# convention, so AGENTS.md/.clinerules are never relocated. The init-time `add.py
# sync-guidelines` later supersedes this drop-time pointer (the rule file it leaves carries
# the mode forward, so re-derivation stays consistent across both install phases).
_RULES_FILE_REL = Path(".claude") / "rules" / "add-workflows.md"
_WORKFLOW_HEADINGS = ("Rules & Workflows", "Workflows", "Rules")
_RULE_REF_LINE = "- ADD (AI-Driven Development) Workflows rules: ./.claude/rules/add-workflows.md"


def _rule_file_mode(project_root, flag: bool = False) -> bool:
    """True when the ADD block belongs in .claude/rules/add-workflows.md instead of inline.
    Re-derived from disk: explicit flag, a ccsk project (.ccsk/), or a rule file already
    present. Pure + fail-soft."""
    if flag:
        return True
    root = Path(project_root)
    try:
        if (root / ".ccsk").is_dir():
            return True
        if (root / _RULES_FILE_REL).exists():
            return True
    except OSError:
        pass
    return False


def _strip_inline_block(text: str) -> str:
    """Remove an inline ADD:BEGIN..END region (migration), collapsing the gap. An unterminated
    BEGIN is left as-is rather than eating the rest of the file."""
    begin = text.find(_GUIDE_BEGIN)
    if begin == -1:
        return text
    end = text.find(_GUIDE_END, begin)
    if end == -1:
        return text
    end += len(_GUIDE_END)
    head = text[:begin].rstrip("\n")
    tail = text[end:].lstrip("\n")
    if head and tail:
        return head + "\n\n" + tail
    return head or tail


def _insert_rule_reference(text: str) -> str:
    """Insert the ADD rule-file bullet under an existing Workflows/Rules heading, or append a
    fresh '## Workflows' section. Caller guarantees the bullet is absent."""
    lines = text.split("\n")
    heading_idx = -1
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if m and any(m.group(2).strip().lower() == h.lower() for h in _WORKFLOW_HEADINGS):
            heading_idx = i
            break
    if heading_idx == -1:
        body = text.rstrip("\n")
        sep = "\n\n" if body else ""
        return f"{body}{sep}## Workflows\n\n{_RULE_REF_LINE}\n"
    level = len(re.match(r"^(#{1,6})", lines[heading_idx]).group(1))
    end = len(lines)
    for j in range(heading_idx + 1, len(lines)):
        m = re.match(r"^(#{1,6})\s+", lines[j])
        if m and len(m.group(1)) <= level:
            end = j
            break
    insert_at = heading_idx + 1
    for j in range(heading_idx + 1, end):
        if lines[j].strip():
            insert_at = j + 1
    lines.insert(insert_at, _RULE_REF_LINE)
    return "\n".join(lines)


def _ensure_claude_reference(claude_md: Path) -> str:
    """Make CLAUDE.md reference the ADD rule file under a Workflows/Rules heading, migrating any
    prior inline ADD block out. created|updated|unchanged|skipped; .bak on change; fail-soft."""
    try:
        existed = claude_md.exists()
        current = claude_md.read_text(encoding="utf-8") if existed else ""
        new = _strip_inline_block(current)
        if "add-workflows.md" not in new:
            new = _insert_rule_reference(new)
        if not new.endswith("\n"):
            new += "\n"
        if new == current:
            return "unchanged"
        if existed:
            Path(str(claude_md) + ".bak").write_text(current, encoding="utf-8")
        claude_md.write_text(new, encoding="utf-8")
        return "updated" if existed else "created"
    except (OSError, UnicodeDecodeError) as exc:
        sys.stderr.write(f"warn: could not write CLAUDE.md — {exc}; skipped\n")
        sys.stderr.flush()
        return "skipped"


def _write_rule_file_pointer(target, profile: dict) -> str:
    """Rule-file variant of _write_agent_pointer for the Claude profile: write the ADD pointer
    block to .claude/rules/add-workflows.md and leave a reference in CLAUDE.md. Fail-soft."""
    root = Path(target)
    rules_path = root / _RULES_FILE_REL
    block = _agent_pointer_block(profile)
    try:
        if rules_path.exists():
            current = rules_path.read_text(encoding="utf-8")
            begin = current.find(_GUIDE_BEGIN)
            if begin != -1:
                end = current.find(_GUIDE_END, begin)
                if end != -1:
                    end += len(_GUIDE_END)
                    new = current[:begin] + block + current[end:]
                else:
                    new = current.rstrip("\n") + "\n\n" + block + "\n"
            else:
                new = current.rstrip("\n") + "\n\n" + block + "\n"
            if new != current:
                Path(str(rules_path) + ".bak").write_text(current, encoding="utf-8")
                rules_path.write_text(new, encoding="utf-8")
        else:
            rules_path.parent.mkdir(parents=True, exist_ok=True)
            rules_path.write_text(block + "\n", encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        sys.stderr.write(f"warn: could not write {_RULES_FILE_REL} — {exc}; skipped\n")
        sys.stderr.flush()
        return "skipped"
    _ensure_claude_reference(root / "CLAUDE.md")
    return "ok"


# --- global home: an OPT-IN shared install of the managed layer (engine+book+skill) ----
# Resolution is PURE + total (never throws); the home MIRRORS the bundled managed layer so
# `update --global` propagation reuses the SAME MANAGED map. Mirrored by behaviour in cli.js.
def resolve_global_home(env=None) -> Path:
    """ADD_HOME (set, non-empty) -> else XDG_DATA_HOME/add -> else <HOME>/.add. Pure · total ·
    never throws · may return a path that doesn't exist yet. Reads HOME from the env mapping
    (defaults to os.environ) — never `$HOME` directly — so tests can inject a hermetic home."""
    env = os.environ if env is None else env
    add_home = env.get("ADD_HOME")
    if add_home:
        return Path(add_home).expanduser()
    xdg = env.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg).expanduser() / "add"
    home = env.get("HOME")
    base = Path(home) if home else Path.home()
    return base / ".add"


def _claude_skills_dir(env=None) -> Path:
    """~/.claude/skills/add — Claude Code's user-global skill dir (HOME from the env mapping)."""
    env = os.environ if env is None else env
    home = env.get("HOME")
    base = Path(home) if home else Path.home()
    return base / ".claude" / "skills" / "add"


def _registry_path(home: Path) -> Path:
    return home / "registry.json"


def _read_registry(home: Path) -> list:
    """A flat list of absolute project-root paths. [] when the file is ABSENT; raises
    ValueError('registry_corrupt') when present-but-unparseable or not a list — the caller
    turns that into a LOUD fail (never a silent empty-list no-op that skips every project)."""
    p = _registry_path(home)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"registry_corrupt: {exc}")
    if not isinstance(data, list):
        raise ValueError("registry_corrupt: not a JSON list")
    return data


def _write_registry(home: Path, paths) -> None:
    """ATOMIC (temp + os.replace) write of a de-duplicated list (first-seen order preserved)."""
    home.mkdir(parents=True, exist_ok=True)
    seen: list = []
    for p in paths:
        if p not in seen:
            seen.append(p)
    target = _registry_path(home)
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_text(json.dumps(seen, indent=2) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(target))   # atomic on POSIX + Windows (same filesystem)


# The home MIRRORS the bundled managed layer (skill/add + tooling + docs at the SAME relative
# paths the package ships) so `_reconcile(project, source=<home>)` reuses MANAGED unchanged.
# (bundled subpath, dest relative to <home>, strip dev-only test_*.py)
_GLOBAL_TREES = (
    ("skill/add", "skill/add", False),
    ("tooling", "tooling", True),
    ("docs", "docs", False),
    ("personas-teacher", "personas-teacher", False),
)


def _reconcile_global(home: Path, claude_dir: Path, bundled_root: Path, no_skill: bool = False) -> None:
    """Clean-replace the bundled managed layer INTO <home> (the canonical mirror), then DEPLOY
    the skill to ~/.claude/skills/add for Claude discovery. Raises OSError if the home or skill
    dir can't be written — the caller turns that into a clean 'home_unwritable' fail. The caller
    verifies the bundled sources exist first (design-for-failure)."""
    for sub, dest_rel, strip in _GLOBAL_TREES:
        if sub in OPTIONAL and not (bundled_root / sub).exists():
            continue   # optional enhancement absent — never abort the global mirror over it
        _clean_replace(bundled_root / sub, home / dest_rel, strip_tests=strip)
    if not no_skill:
        _clean_replace(home / "skill" / "add", claude_dir)


# --- global DATA: an OPT-IN per-project user-data snapshot under <home>/data/<key> ----------
# Strictly additive to the global home; the per-project local + git-tracked default is untouched.
# The snapshot copies ONLY user-data (the managed trees + transient/managed-meta are excluded),
# CLEAN-REPLACED, one-way (project->home). Mirrored by behaviour in cli.js.
LOCK_FILE = ".update.lock"                                         # the `update --global` home lock (never user-data)
_DATA_EXCLUDE = {"tooling", "docs", ".update-cache", STAMP_FILE, LOCK_FILE}   # managed trees + managed-meta + the lock


def data_key(project_abspath) -> str:
    """A filesystem-safe, deterministic, collision-resistant key for an absolute project path:
    `<sanitized-basename>-<sha1(abspath_utf8)[:12]>`. Pure · total · identical on both twins."""
    p = str(project_abspath)
    digest = hashlib.sha1(p.encode("utf-8")).hexdigest()[:12]
    base = Path(p).name or "root"
    safe = "".join(c if (c.isalnum() or c in "-_.") else "_" for c in base)
    return f"{safe}-{digest}"


def _is_user_data(name: str) -> bool:
    """A top-level `.add/` entry is user-data unless it is a managed tree or a transient artifact."""
    if name in _DATA_EXCLUDE:
        return False
    if name.startswith("scope-snapshot"):
        return False
    if "pre-archive-bak" in name:
        return False
    if name.endswith(".bak.json"):
        return False
    return True


def _persist_data(home: Path, project_abspath) -> bool:
    """Clean-replace a project's USER-DATA into <home>/data/<key>. Returns True if persisted,
    False if there is nothing to persist (no .add/ or no user-data — an honest skip, not an
    error). Raises OSError if the data dir can't be written — the caller fails 'data_unwritable'."""
    add_dir = Path(project_abspath) / ".add"
    if not add_dir.exists():
        return False
    entries = [e for e in sorted(add_dir.iterdir()) if _is_user_data(e.name)]
    if not entries:
        return False
    dest = home / "data" / data_key(str(project_abspath))
    if dest.exists():
        shutil.rmtree(dest)                 # clean-replace: a locally-deleted file leaves no orphan
    dest.mkdir(parents=True, exist_ok=True)
    for e in entries:
        target = dest / e.name
        if e.is_dir():
            shutil.copytree(str(e), str(target))
        else:
            shutil.copyfile(str(e), str(target))
    return True


def _restore_data(home: Path, project_abspath, *, force: bool = False) -> bool:
    """Restore a project's USER-DATA from <home>/data/<key> into <project>/.add — the
    NON-DESTRUCTIVE inverse of _persist_data. FILL-GAPS by default: write only entries ABSENT
    in the dest; a present entry is left untouched (no clobber). force=True overwrites a present
    entry, writing a `<name>.bak` sidecar of the original FIRST. Copies only _is_user_data
    entries (a polluted snapshot can't drop managed files); DEREFERENCES symlinks to content (a
    link lands as a regular file/tree — byte parity with the JS twin). Returns True if >=1 entry
    was restored, False if there is nothing to restore (snapshot dir absent or holds no user-data
    — an honest skip, not an error). Raises OSError on an unwritable dest — the caller fails
    'restore_failed'. Mirrored by behaviour in cli.js."""
    proj = Path(project_abspath).resolve()              # snapshots are ALWAYS keyed by the
    src = home / "data" / data_key(str(proj))           # resolved abspath (install resolves first)
    if not src.exists():
        return False
    entries = [e for e in sorted(src.iterdir()) if _is_user_data(e.name)]
    if not entries:
        return False
    add_dir = proj / ".add"
    add_dir.mkdir(parents=True, exist_ok=True)
    restored = False
    for e in entries:
        dest = add_dir / e.name
        if dest.exists() or dest.is_symlink():
            if not force:
                continue                            # fill-gaps: never clobber a present entry
            bak = dest.with_name(dest.name + ".bak")
            if bak.exists() or bak.is_symlink():    # a stale .bak: replace it, don't merge
                if bak.is_dir() and not bak.is_symlink():
                    shutil.rmtree(bak)
                else:
                    bak.unlink()
            os.replace(str(dest), str(bak))         # back up the original BEFORE replacing
        if e.is_dir():
            shutil.copytree(str(e), str(dest), symlinks=False)   # symlinks=False -> deref to content
        else:
            shutil.copyfile(str(e), str(dest))                   # copyfile follows a symlink source
        restored = True
    return restored


def _prune_data(home: Path, *, force: bool = False):
    """Find (and, with force, remove) ORPHANED per-project snapshots under <home>/data. An
    orphan is a <home>/data/<key> dir whose key is owned by NO LIVE registry entry — LIVE = a
    registered project path that still EXISTS on disk. So an UNregistered key AND a registered-
    but-vanished-on-disk key are BOTH orphans (the explicit reclaim — INTENTIONALLY DIVERGES
    from `update --global`, which keeps vanished). Reads the registry FIRST: a
    ValueError('registry_corrupt') propagates (LOUD, before any removal). Returns
    (orphans, removed) as sorted key-name lists; removed == [] on a dry-run, == orphans under
    force (each orphan dir shutil.rmtree'd). Mirrored by behaviour in cli.js."""
    reg = _read_registry(home)                          # corrupt -> ValueError (LOUD, zero removal)
    live = {data_key(p) for p in reg if Path(p).exists()}
    data_dir = home / "data"
    if not data_dir.exists():
        return [], []
    orphans = sorted(d.name for d in data_dir.iterdir() if d.is_dir() and d.name not in live)
    removed: list = []
    if force:
        for key in orphans:
            shutil.rmtree(data_dir / key)
            removed.append(key)
    return orphans, removed


def prune_data(*, force: bool = False, env=None) -> int:
    """`prune-data` command: reclaim ORPHANED per-project snapshots from the shared home.
    Dry-run by default (lists orphans, removes nothing); --force deletes. Resolves the home from
    env; a missing home is no_global_home (fail-closed). A corrupt registry is a LOUD fail with
    nothing removed. Returns 0 on success, 1 on a fail-closed reject. Mirrored by cli.js."""
    env_map = os.environ if env is None else env
    home = resolve_global_home(env_map)
    if not _stamp_path(home).exists():
        return _fail(f"no global ADD install at {home} (.add-version not found) — nothing to prune")
    try:
        orphans, removed = _prune_data(home, force=force)
    except ValueError as exc:
        return _fail(f"global registry {_registry_path(home)} is corrupt — fix or delete it; {exc}")
    if not orphans:
        _log("  no orphaned snapshots — nothing to prune")
        return 0
    if force:
        _log(f"  ✓ {len(removed)} removed")
    else:
        for key in orphans:
            _log(f"  orphan: {key}")
        _log(f"  {len(orphans)} orphan(s); re-run with --force to remove")
    return 0


def _seed_soul_md(target_path: Path, bundled_root: Path) -> None:
    """Seed .add/SOUL.md from the bundled template if it does not yet exist.
    Skip-if-exists (SOUL.md is user-owned — never clobber). Fail-soft: any
    problem logs a warning and returns; the caller's return code is unaffected."""
    dest = target_path / ".add" / "SOUL.md"
    if dest.exists():
        return
    source = bundled_root / "tooling" / "templates" / "SOUL.md.tmpl"
    if not source.exists():
        _log("soul_seed_skipped: SOUL.md.tmpl not found in bundled tooling/templates/")
        return
    try:
        dest.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    except OSError as exc:
        _log(f"soul_seed_skipped: could not write .add/SOUL.md — {exc}")


# kept OUTSIDE add_engine/constants.py / gitignore.tmpl deliberately: the engine's own
# _GITIGNORE_BODY constant must never contain "personas-teacher" (test_engine_unchanged_
# and_handsoff — the engine stays hands-off of the teacher vendor tree). The INSTALLER
# already names that tree explicitly (MANAGED/OPTIONAL), so it is free to seed this one
# extra ignore line itself. Twin of bin/cli.js:INSTALLER_MANAGED_IGNORE_EXTRA.
_INSTALLER_MANAGED_IGNORE_EXTRA = (".add/personas-teacher/",)


def _seed_gitignore(target_path: Path, bundled_root: Path) -> None:
    """Ensure .add/.gitignore lists the engine's transient artifacts + managed vendor trees.
    Seed it from the bundled tooling/templates/gitignore.tmpl (plus
    _INSTALLER_MANAGED_IGNORE_EXTRA) if absent; else APPEND-IF-ABSENT each pattern line that
    combined body carries that the existing file lacks — additive only, never reorders or
    removes user-added lines, idempotent. Comment/blank template lines are not appended to
    an existing file. Fail-soft: any problem logs a warning and returns (rc unaffected).
    Twin of bin/cli.js:seedGitignore."""
    source = bundled_root / "tooling" / "templates" / "gitignore.tmpl"
    if not source.exists():
        _log("gitignore_seed_skipped: gitignore.tmpl not found in bundled tooling/templates/")
        return
    dest = target_path / ".add" / ".gitignore"
    try:
        body = source.read_text(encoding="utf-8")
        if not body.endswith("\n"):
            body += "\n"
        body += "\n".join(_INSTALLER_MANAGED_IGNORE_EXTRA) + "\n"
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(body, encoding="utf-8")            # seed-if-missing
            return
        current = dest.read_text(encoding="utf-8")
        have = {ln.strip() for ln in current.splitlines()}
        missing = [ln for ln in body.splitlines()
                   if ln.strip() and not ln.lstrip().startswith("#") and ln.strip() not in have]
        if not missing:
            return                                             # idempotent — nothing to add
        suffix = "" if current.endswith("\n") or current == "" else "\n"
        dest.write_text(current + suffix + "\n".join(missing) + "\n", encoding="utf-8")
    except OSError as exc:
        _log(f"gitignore_seed_skipped: could not update .add/.gitignore — {exc}")


def install(
    target: str = ".",
    force: bool = False,
    stage: str | None = None,
    name: str | None = None,
    yes: bool = False,
    non_interactive: bool = False,
    bundled: str | None = None,
    env=None,
    as_global: bool = False,
    as_global_data: bool = False,
    as_global_data_restore: bool = False,
    rule_file: bool = False,
) -> int:
    """Install ADD into `target` directory — RECONCILES the managed layer (restore
    missing trees + refresh present ones, sweeping orphans), never touching user data.

    `bundled` injects a synthetic source root (test hook; parity with update()). `env`
    injects the home/skill base for hermetic global tests. `as_global` ALSO installs the
    managed layer to the shared home + registers the project (the per-project drop still runs).
    `as_global_data` IMPLIES `as_global` and ALSO persists the project's user-data to
    <home>/data/<key> (opt-in; one-way snapshot). `as_global_data_restore` is the INVERSE
    (--from-global-data): it rehydrates user-data from <home>/data/<key> into this clone
    (non-destructive fill-gaps; --force overwrites with a .bak). Independent of as_global —
    CONSUME-only: no register, no persist. A missing home is no_global_home (fails fast).
    Returns 0 on success, 1 on error, 130 on a user cancel (nothing written).
    """
    if as_global_data:
        as_global = True            # you cannot persist data without a home to persist into
    target_path = Path(target).resolve()
    if not target_path.exists():
        return _fail(f"target directory does not exist: {target_path}")

    # Interactive confirm (real terminal only) — degrades to the plain path under
    # --yes/--non-interactive, CI, or a pipe. A cancel writes NOTHING (exit 130).
    intent = ""                              # build-intent NOTE — stays "" on the non-interactive path
    if _interactive(yes, non_interactive):
        _render_brand()                      # brand + showcase BEFORE the first prompt (interactive only)
        try:
            _log(_readiness_line(env, target_path))   # pre-flight: git · python3 · agent (fail-soft)
        except Exception:
            pass                             # the pre-flight line is informational — never block the install
        chosen = _prompt_target(target_path)
        if chosen is CANCEL:
            _log("\nInstallation cancelled — nothing was written.")
            return 130
        target_path = chosen
        if not target_path.exists():
            return _fail(f"target directory does not exist: {target_path}")
        # Global-first SCOPE step — only when the scope was not already chosen by an explicit
        # --global/--global-data flag (honored, not re-asked). A cancel writes NOTHING (130).
        if not as_global:
            picked = _prompt_scope()
            if picked is CANCEL:
                _log("\nInstallation cancelled — nothing was written.")
                return 130
            as_global = bool(picked)         # global stays STRICTLY ADDITIVE: the per-project drop still runs
        intent = _prompt_intent()            # LAST optional step; "" on skip/EOF/Ctrl-C (never cancels)

    _log(f"Installing ADD into {target_path}")

    # Locate bundled data (synthetic `bundled` for tests; the wheel's _bundled/ otherwise).
    try:
        bundled_root = Path(bundled) if bundled else _bundled_root()
    except RuntimeError as exc:
        return _fail(str(exc))

    # design-for-failure: verify ALL sources exist BEFORE touching the target.
    for sub, _dest, _strip in MANAGED:
        if sub in OPTIONAL and not (bundled_root / sub).exists():
            continue   # optional enhancement absent — soft-skip, never abort the core install
        if not (bundled_root / sub).exists():
            return _fail(f"missing bundled source: {bundled_root / sub}")

    # OPT-IN restore (--from-global-data): the home MUST already exist — no_global_home is a
    # HARD fail, checked FAST here so nothing is written to the target on a missing home. The
    # restore itself runs AFTER the managed drop (below); consume-only, no register/persist.
    if as_global_data_restore:
        restore_home = resolve_global_home(os.environ if env is None else env)
        if not _stamp_path(restore_home).exists():
            return _fail(
                f"no global ADD install at {restore_home} (.add-version not found) — nothing "
                "to restore from; run `init --global-data` on a source checkout first"
            )

    # OPT-IN global home: install the managed layer ONCE to a shared home + register this
    # project, THEN fall through to the NORMAL per-project drop below (the self-contained
    # default is untouched — global is strictly additive). Fail-closed: an unwritable home or
    # a corrupt registry aborts BEFORE the per-project drop, leaving the package + default usable.
    if as_global:
        env_map = os.environ if env is None else env
        home = resolve_global_home(env_map)
        claude_dir = _claude_skills_dir(env_map)
        try:
            _reconcile_global(home, claude_dir, bundled_root)               # home_unwritable
        except OSError as exc:
            return _fail(f"cannot write global home {home} — {exc}")
        _write_stamp(home, _pkg_version(), channel="global")
        try:
            reg = _read_registry(home)                                      # registry_corrupt
        except ValueError:
            return _fail(
                f"global registry {_registry_path(home)} is corrupt — fix or delete it; not registering"
            )
        reg.append(str(target_path))
        try:
            _write_registry(home, reg)                                      # atomic + dedup
        except OSError as exc:
            return _fail(f"cannot write global registry {_registry_path(home)} — {exc}")
        _log(f"  ✓ global home ready at {home}")
        _log(f"  ✓ registered {target_path} (registry: {len(_read_registry(home))})")

    # RECONCILE: restore missing trees + refresh present ones (sweep orphans). Touches
    # ONLY the managed layer — state.json / PROJECT.md / milestones / tasks are never read.
    _reconcile(target_path, bundled_root)

    _seed_soul_md(target_path, bundled_root)
    _seed_gitignore(target_path, bundled_root)

    # Agent detection: write THE detected agent's integration file (a marker-delimited
    # pointer init's sync-guidelines later supersedes) + tailor the closing next-step.
    # Best-effort + fail-soft — never aborts the successful drop above.
    # The INTERACTIVE path uses the enriched detector (env > CLAUDE.md > installed CLI), already
    # disclosed in the pre-flight line and overridable by cancel+rerun. The NON-interactive path
    # stays env-only (the byte-identical boundary + test_agent_detect pin).
    if _interactive(yes, non_interactive):
        profile = _detect_agent_enriched(env, target_path)
    else:
        profile = _detect_agent(env)
    # Rule-file mode (ccsk projects / --rule-file) relocates the CLAUDE.md pointer to
    # .claude/rules/add-workflows.md + a reference bullet — CLAUDE-only; other agents stay inline.
    if profile["integration_file"] == "CLAUDE.md" and _rule_file_mode(target_path, rule_file):
        if (target_path / ".ccsk").is_dir():
            _log("  ccsk detected — ADD rules go to .claude/rules/add-workflows.md")
        _write_rule_file_pointer(target_path, profile)
    else:
        _write_agent_pointer(target_path, profile)

    # Gemini CLI auto-loads GEMINI.md, not AGENTS.md — so for the gemini profile we ALSO merge
    # .gemini/settings.json (context.fileName) to load the AGENTS.md pointer. Fail-soft + idempotent.
    if profile["id"] == "gemini":
        _write_gemini_settings(target_path)

    # Optional build-intent NOTE for `/add` to read — a NOTE only (no init, no state.json).
    # "" on the non-interactive path or a skipped prompt -> no file written.
    _write_intent_note(target_path, intent)

    # NO step 4: the installer DROPS FILES ONLY (npm ↔ pip parity with bin/cli.js).
    # Initialisation is deferred to the AI (via `/add`) or a CLI user — a pre-run plain
    # `add.py init` would grandfather-lock the v12 lock-down gate before `/add` runs (see
    # the module header). So we do NOT exec add.py here.
    _log("\nDone. The `add` skill + tooling are installed (no project state yet — that's intentional).")
    if profile["id"] == "generic":
        # the generic onramp line — kept literal so the conversational-only handoff is stable
        _log("Next:  open your AI Agent CLI (like Claude Code, Codex, etc.), then run `/add`, and say what you want to build — the agent")
        _log("       sets up the foundation, sizes it into a milestone, and drives the build with you;")
        _log("       you sign off once, at the lock-down.")
    else:
        _log(f"Detected {profile['label']}.")
        _log(f"Next:  {profile['next_step']}")

    # OPT-IN data persist: snapshot this project's USER-DATA under <home>/data/<key> (one-way).
    # A fresh drop has no user-data yet -> honest skip (exit 0). Unwritable -> data_unwritable.
    if as_global_data:
        env_map = os.environ if env is None else env
        home = resolve_global_home(env_map)
        try:
            persisted = _persist_data(home, target_path)
        except OSError as exc:
            return _fail(f"cannot write global data {home / 'data' / data_key(str(target_path))} — {exc}")
        if persisted:
            _log(f"  ✓ persisted data -> {home / 'data' / data_key(str(target_path))}")
        else:
            _log("  (no project data to persist yet — run /add to create one, then re-run --global-data)")

    # OPT-IN restore (consume): rehydrate user-data from <home>/data/<key> into this fresh clone.
    # The home was verified above (no_global_home fails fast). FILL-GAPS unless --force; a missing
    # snapshot is an HONEST skip (exit 0). An unwritable dest -> restore_failed (fail-closed).
    if as_global_data_restore:
        home = resolve_global_home(os.environ if env is None else env)
        snap = home / "data" / data_key(str(target_path))
        try:
            restored = _restore_data(home, target_path, force=force)
        except OSError as exc:
            return _fail(f"restore_failed: cannot write restored data into {target_path / '.add'} — {exc}")
        if restored:
            _log(f"  ✓ restored data <- {snap}")
        else:
            _log(f"  (no snapshot for this project at {snap} — nothing restored)")
    _log("")
    return 0


# --- update: re-materialize the managed layer without a re-install -----------

def _pkg_version() -> str:
    try:
        from add_method import __version__
        return __version__
    except Exception:
        return "0.0.0"


def _stamp_path(add_dir: Path) -> Path:
    return add_dir / STAMP_FILE


def _read_stamp(add_dir: Path) -> dict | None:
    p = _stamp_path(add_dir)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _write_stamp(add_dir: Path, version: str, channel: str = "pip") -> None:
    add_dir.mkdir(parents=True, exist_ok=True)
    _stamp_path(add_dir).write_text(
        json.dumps(
            {
                "version": version,
                "channel": channel,
                "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _tree_files(root: Path) -> set:
    """The set of FILE paths (recursive leaves) under root, RELATIVE to root. ∅ if absent.
    Directories are not counted — only files (the 'manifest' the rollup measures)."""
    if not root.exists():
        return set()
    return {p.relative_to(root) for p in root.rglob("*") if p.is_file()}


def _clean_replace(src: Path, dest: Path, *, strip_tests: bool = False) -> dict:
    """Wipe dest, then copy src -> dest — so a file REMOVED upstream leaves no orphan
    behind (the bug a merge-copy `init --force` had). The managed trees hold no user
    data, so wipe-and-copy is safe.

    Returns a file-level roll-up of the heal: {"restored": N, "refreshed": M} where
    `restored` = a file in the FINAL tree whose relative path was ABSENT before the wipe
    (a fresh or partially-gutted tree heals these), and `refreshed` = a final file that
    was PRESENT before (re-materialized). Orphans (present before, gone after) are swept
    and counted as neither. The counts are pure observation — copy semantics are unchanged."""
    before = _tree_files(dest)                       # snapshot BEFORE the wipe, or it's always ∅
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(str(src), str(dest))
    if strip_tests:
        pyc = dest / "__pycache__"
        if pyc.exists():
            shutil.rmtree(pyc)
        for child in dest.iterdir():
            if child.name.startswith("test_") and child.name.endswith(".py"):
                child.unlink()
    after = _tree_files(dest)                         # the FINAL tree (post-strip)
    return {"restored": len(after - before), "refreshed": len(after & before)}


_TREE_LABEL = {"skill/add": "skill", "tooling": "tooling", "docs": "docs", "personas-teacher": "personas"}


def _managed_status(target_path: Path) -> dict:
    """Per managed tree: 'missing' (dest absent OR empty) or 'present'."""
    status = {}
    for sub, dest_rel, _strip in MANAGED:
        dest = target_path / dest_rel
        present = dest.exists() and any(dest.iterdir())
        status[sub] = "present" if present else "missing"
    return status


def _reconcile(target_path: Path, bundled_root: Path) -> dict:
    """Clean-replace every managed tree (restore-if-missing / refresh-if-present, sweeping
    orphans) and REPORT both per-tree status AND a file-level roll-up. Touches ONLY managed
    trees — never user data. The caller verifies sources exist first (design-for-failure).

    Returns {"restored": N, "refreshed": M, "trees": <pre-status>} — N/M summed across all
    managed trees at FILE granularity, so a PRESENT-but-gutted tree (tree-level "refreshed")
    still surfaces its restored files in the roll-up."""
    status = _managed_status(target_path)
    restored = refreshed = 0
    for sub, dest_rel, strip in MANAGED:
        if sub in OPTIONAL and not (bundled_root / sub).exists():
            continue   # optional enhancement absent from this package — nothing to materialize
        roll = _clean_replace(bundled_root / sub, target_path / dest_rel, strip_tests=strip)
        restored += roll["restored"]
        refreshed += roll["refreshed"]
        if status[sub] == "missing":
            _log(f"  ✓ restored  {_TREE_LABEL[sub]:8s}-> {dest_rel}  (was missing)")
        else:
            _log(f"  ✓ refreshed {_TREE_LABEL[sub]:8s}-> {dest_rel}")
    _log(f"  → {restored} restored · {refreshed} refreshed")
    return {"restored": restored, "refreshed": refreshed, "trees": status}


def _run_migrations(state_file: Path, from_version: str | None, to_version: str) -> None:
    """Apply forward-only, idempotent state migrations. No-op while MIGRATIONS is empty."""
    if not MIGRATIONS or not state_file.exists():
        return
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    changed = False
    for ver, migrate in sorted(MIGRATIONS.items(), key=lambda kv: _vkey(kv[0])):
        if from_version is None or _vkey(from_version) < _vkey(ver) <= _vkey(to_version):
            state = migrate(state)
            changed = True
    if changed:
        state_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _vkey(v: str) -> list:
    """A sortable key for dotted versions (numeric parts compared as ints)."""
    return [(0, int(p)) if p.isdigit() else (1, p) for p in (v or "0").split(".")]


def _add_dir(target_path: Path) -> Path:
    return target_path / ".add"


@contextlib.contextmanager
def _update_lock(home: Path):
    """Serialize `update --global` with an EXCLUSIVE O_EXCL lockfile at <home>/.update.lock —
    the SAME mechanism as the npm twin (cli.js `fs.openSync(.., "wx")`), so a pip-held lock
    blocks an npm run and vice-versa (a `fcntl.flock` would NOT serialize cross-twin: npm holds
    only the file, never the kernel flock). Already present -> raises BlockingIOError (the caller
    maps it to "update_in_progress"). The file is unlinked on exit for success OR exception, so a
    normal/handled exit never outlives the process. A hard crash / SIGKILL may leave a stale
    lockfile -> the update_in_progress message hints to remove it (symmetric with the npm twin)."""
    home.mkdir(parents=True, exist_ok=True)
    lock_path = home / LOCK_FILE
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:            # held -> caught upstream -> update_in_progress
        raise BlockingIOError(f"{lock_path} is held") from exc
    try:
        yield
    finally:
        os.close(fd)
        try:
            os.unlink(str(lock_path))
        except OSError:                       # pragma: no cover — already gone
            pass


def _valid_registry_path(p) -> bool:
    """True iff `os.path.normpath(p)` is an EXISTING ADD project — a dir that contains `.add/`.
    Decides reconcile-vs-drop for an absolute registry entry; absoluteness is the SEPARATE LOUD
    gate in `_update_global` (a relative path is the traversal vector). This is the security
    backstop: a managed-file reconcile NEVER lands in a dir without a `.add/` marker."""
    np = os.path.normpath(str(p))
    return os.path.isdir(np) and os.path.isdir(os.path.join(np, ".add"))


def _update_global(target, *, force=False, bundled=None, version=None, env=None) -> int:
    """`update --global`: under a home lock, refresh the shared home (mirror + skill, re-stamp)
    then propagate to every registered+VALID project via `reconcile(p, source=<home>)`; prune
    vanished projects, DROP existing non-ADD-project entries (warn), and rewrite the registry
    atomically with the surviving NORMALIZED paths. Fail-closed: no home install -> no_global_home;
    a concurrent run -> update_in_progress; a corrupt registry -> registry_corrupt (LEFT INTACT);
    a NON-ABSOLUTE registry entry (the traversal vector) -> unsafe_registry_path (zero mutations,
    read BEFORE any home write). Absolute non-normalized entries are normalized + healed, never LOUD."""
    env_map = os.environ if env is None else env
    home = resolve_global_home(env_map)
    claude_dir = _claude_skills_dir(env_map)
    if not _stamp_path(home).exists():
        return _fail(
            f"no_global_home: no global ADD install at {home} (.add-version not found) — "
            f"run `init --global` first"
        )
    try:
        bundled_root = Path(bundled) if bundled else _bundled_root()
    except RuntimeError as exc:
        return _fail(str(exc))
    for sub, _dest, _strip in MANAGED:
        if sub in OPTIONAL and not (bundled_root / sub).exists():
            continue   # optional enhancement absent — soft-skip, never abort the core install
        if not (bundled_root / sub).exists():
            return _fail(f"missing bundled source: {bundled_root / sub}")
    try:
        with _update_lock(home):
            # Read the registry BEFORE refreshing the home — a corrupt registry fails closed with
            # ZERO writes (never a silent empty-list no-op), leaving the file for the user to fix.
            try:
                reg = _read_registry(home)
            except ValueError:
                return _fail(
                    f"registry_corrupt: global registry {_registry_path(home)} is corrupt — "
                    f"fix or delete it; not propagating"
                )
            # PRE-SCAN (security, BEFORE any write): a NON-ABSOLUTE entry is the traversal vector —
            # it cannot be a trusted abspath, so abort the WHOLE run with zero mutations.
            for p in reg:
                if not os.path.isabs(p):
                    return _fail(
                        f"unsafe_registry_path: registered project {p!r} is not an absolute path — "
                        f"fix or remove it in {_registry_path(home)}; not propagating"
                    )
            new_version = version or _pkg_version()
            try:
                _reconcile_global(home, claude_dir, bundled_root)
            except OSError as exc:
                return _fail(f"cannot write global home {home} — {exc}")
            _write_stamp(home, new_version, channel="global")
            # Propagate from the home mirror to each still-existing ADD project (at its NORMALIZED
            # path); prune the vanished, DROP an existing non-project (the is-.add/ backstop).
            kept: list = []
            pruned = 0
            dropped = 0
            for p in reg:
                np = os.path.normpath(p)                  # absolute (pre-scan) -> lexically normalized
                if not Path(np).exists():
                    _log(f"  ⚠ registered project {np} not found — pruning")
                    pruned += 1
                    continue                              # a vanished project's data snapshot is KEPT
                if not (Path(np) / ".add").is_dir():
                    _log(f"  ⚠ registered path {np} is not an ADD project (no .add/) — dropping")
                    dropped += 1
                    continue                              # NEVER reconcile managed files into a non-project
                _reconcile(Path(np), home)                # standard MANAGED map, sourced from the home mirror
                if (home / "data" / data_key(np)).exists():
                    _persist_data(home, np)               # keep the opted-in project's snapshot current
                kept.append(np)                           # store the NORMALIZED path (heals a bent legit entry)
            _write_registry(home, kept)
            bits = ([f"{pruned} pruned"] if pruned else []) + ([f"{dropped} dropped"] if dropped else [])
            tail = f" ({', '.join(bits)})" if bits else ""
            _log(f"ADD {new_version} · global home + {len(kept)} project(s) reconciled{tail}.")
            return 0
    except BlockingIOError:
        return _fail(
            f"update_in_progress: another `update --global` is already running — retry shortly "
            f"(remove {home / LOCK_FILE} if it is stale)"
        )


def update(
    target: str = ".",
    force: bool = False,
    bundled: str | None = None,
    version: str | None = None,
    channel: str = "pip",
    env=None,
    as_global: bool = False,
) -> int:
    """Re-materialize the managed layer (skill · tooling · docs) from the installed
    package into an EXISTING .add/ project, preserving ALL user data. Idempotent;
    clean-replaces so no orphan files survive a version bump. 0 on success/no-op, 1 on error.

    `as_global` instead refreshes the shared global home + propagates to every registered
    project (see `_update_global`); `env` injects the home/skill base for hermetic tests."""
    if as_global:
        return _update_global(target, force=force, bundled=bundled, version=version, env=env)
    target_path = Path(target).resolve()
    add_dir = _add_dir(target_path)
    if not (add_dir / "tooling").exists() and not (add_dir / "state.json").exists():
        return _fail(f"no ADD project at {target_path} (.add/ not found) — run `init` first")

    try:
        bundled_root = Path(bundled) if bundled else _bundled_root()
    except RuntimeError as exc:
        return _fail(str(exc))
    for sub, _dest, _strip in MANAGED:
        if sub in OPTIONAL and not (bundled_root / sub).exists():
            continue   # optional enhancement absent — soft-skip, never abort the core install
        if not (bundled_root / sub).exists():
            return _fail(f"missing bundled source: {bundled_root / sub}")

    new_version = version or _pkg_version()
    stamp = _read_stamp(add_dir)
    cur_version = stamp.get("version") if stamp else None
    # An optional tree absent from BOTH the package and the project can't be healed, so it
    # never counts as "missing" — otherwise a same-version update would never reach the no-op.
    missing = [sub for sub, st in _managed_status(target_path).items()
               if st == "missing" and not (sub in OPTIONAL and not (bundled_root / sub).exists())]
    # same-version no-op ONLY when nothing is missing — a missing managed tree HEALS
    # even at the current version (heal-reconcile).
    if cur_version == new_version and not force and not missing:
        _log(f"ADD already at {new_version} — nothing to update (use --force to re-materialize).")
        return 0

    # design-for-failure: back up state BEFORE touching anything.
    state_file = add_dir / "state.json"
    if state_file.exists():
        shutil.copyfile(str(state_file), str(add_dir / "pre-update-state.bak.json"))

    roll = _reconcile(target_path, bundled_root)
    _run_migrations(state_file, cur_version, new_version)
    _write_stamp(add_dir, new_version, channel=channel)
    _seed_soul_md(target_path, bundled_root)
    _seed_gitignore(target_path, bundled_root)

    _log(
        f"ADD updated {cur_version or '(unstamped)'} -> {new_version} · "
        f"skill · tooling · docs refreshed "
        f"({roll['restored']} restored · {roll['refreshed']} refreshed) · "
        "your project state untouched."
    )
    return 0


def update_check(target: str = ".", version: str | None = None) -> int:
    """Read-only: compare the project's stamp to the installed package version. No writes."""
    add_dir = _add_dir(Path(target).resolve())
    if not add_dir.exists():
        return _fail("no ADD project here (.add/ not found) — run `init` first")
    new_version = version or _pkg_version()
    stamp = _read_stamp(add_dir)
    cur = stamp.get("version") if stamp else None
    if cur == new_version:
        _log(f"ADD is current: project and package both at {new_version}.")
    elif cur is None:
        _log(f"ADD project is unstamped; installed package is {new_version}. Run `update`.")
    else:
        _log(f"ADD update available: project on {cur}, package is {new_version}. Run `update`.")
    return 0
