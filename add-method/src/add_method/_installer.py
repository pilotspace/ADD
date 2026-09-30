"""Installs the ADD skill. No engine, no prompts, no dependencies.

Twin of bin/cli.js: same flags, same files, same output (tests/test_npm_pip_parity.py runs both
and compares). Rules:
  - what ADD owns (the skill, the persona corpus + index) is refreshed on every run by a
    stage-then-swap, so a crash never leaves a half-copied tree;
  - what the user owns (PROJECT.md, personas, text outside the managed block) is never overwritten;
  - a 3.x engine (.add/tooling/) and ADD's 3.x agents are removed only AFTER the new layout has
    landed, and only when they are recognisably ours;
  - any failure stops the run, says what landed, and exits non-zero. Re-running is safe.
"""
from __future__ import annotations

import importlib.resources
import json
import os
import re
import shutil
import sys
from pathlib import Path

_GUIDE_BEGIN = "<!-- ADD:BEGIN — managed by the ADD installer; do not edit inside -->"
_GUIDE_END = "<!-- ADD:END -->"
_BEGIN_PREFIX = "<!-- ADD:BEGIN"   # also matches a 3.x block, so it is replaced, not duplicated
_RETIRED_AGENTS = ("add-worker", "add-advisor", "add", "add-design", "add-build",
                   "add-verify", "add-persona")
# Other files that may carry an ADD block from 3.x (.clinerules: the 3.x installer + 2.5 engine
# wrote it; the rest defensively). Refreshed only when a whole block is there; never created.
_LEGACY_POINTERS = (".clinerules", "GEMINI.md", ".cursorrules", ".windsurfrules",
                    ".github/copilot-instructions.md")
_IGNORED = ("personas-teacher/", "personas-index/")
_JUNK = shutil.ignore_patterns("__pycache__", ".DS_Store", "*.pyc", "*.pyo")
REQUIRED = ("skill/add/SKILL.md", "personas", "personas-teacher", "personas-index")


class StepError(Exception):
    pass


def _out(msg: str) -> None:
    print(msg, flush=True)


def _row(label: str, text: str) -> None:
    _out("  " + label.ljust(10) + "  " + text)


def _version() -> str:
    from add_method import __version__
    return __version__


def _exists(p: Path) -> bool:
    return os.path.lexists(p)


def _rm(p: Path) -> None:
    if p.is_symlink() or p.is_file():
        p.unlink()
    elif p.is_dir():
        shutil.rmtree(p)


def _bundled_root() -> Path:
    """The packaged payload: src/add_method/_bundled/ (a real folder in a normal wheel install)."""
    return Path(str(importlib.resources.files("add_method") / "_bundled"))


def _replace_tree(src: Path, dest: Path) -> str:
    """Stage a full copy beside dest, then swap it in with two renames — never half-written."""
    if dest.is_symlink():
        return "kept (a symlink - not replaced)"
    parent, base = dest.parent, dest.name
    parent.mkdir(parents=True, exist_ok=True)
    for n in os.listdir(parent):
        if n.startswith(base + ".add-tmp-"):
            _rm(parent / n)                                   # a crashed earlier run
    old = parent / (base + ".add-old")
    if not _exists(dest) and _exists(old):
        os.rename(old, dest)                                  # heal a crash mid-swap
    _rm(old)
    tmp = parent / (base + ".add-tmp-" + str(os.getpid()))
    try:
        shutil.copytree(src, tmp, ignore=_JUNK)
    except BaseException:
        _rm(tmp)
        raise
    had = _exists(dest)
    if had:
        os.rename(dest, old)
    try:
        os.rename(tmp, dest)
    except BaseException:
        if had:
            os.rename(old, dest)
        _rm(tmp)
        raise
    _rm(old)
    return "refreshed" if had else "installed"


def _pointer_block() -> str:
    return "\n".join((
        _GUIDE_BEGIN,
        "## ADD — how to work in this repo",
        "",
        "This project uses **ADD (AI-Driven Development)**. The method is one skill file,",
        "`.claude/skills/add/SKILL.md` — read it and follow it (Claude Code: run `/add`).",
        "State lives in `.add/`: read `.add/PROJECT.md` first each session, then the open work in",
        "`.add/tasks/` and `.add/milestones/`. Your tools are git and this project's test command.",
        "",
        "Size before ceremony: a change of at most 3 adjacent files with no unknowns goes Quick — a failing test, the fix, one commit.",
        "Anything touching security · data · architecture, or a surface other code consumes, is at least a Task.",
        "PROJECT.md `invariants:` bind every change. Never weaken a sealed check to get green; a security finding is a HARD-STOP.",
        "",
        "Edit outside the markers, not inside.",
        _GUIDE_END,
    ))


def _read(p: Path) -> str:
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def _write(p: Path, text: str) -> None:
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def _write_pointer(path: Path) -> str:
    """Rewrite only the managed block; text outside it is never touched. created|updated|unchanged."""
    path = Path(path)
    block = _pointer_block()
    if not _exists(path):
        _write(path, block + "\n")
        return "created"
    cur = _read(path)
    end = cur.rfind(_GUIDE_END)
    begin = -1 if end == -1 else cur.rfind(_BEGIN_PREFIX, 0, end)
    if begin != -1:
        nxt = cur[:begin] + block + cur[end + len(_GUIDE_END):]
    elif cur.strip() == "":
        nxt = block + "\n"
    else:
        nxt = cur.rstrip("\n") + "\n\n" + block + "\n"
    if nxt == cur:
        return "unchanged"
    _write(path.with_name(path.name + ".bak"), cur)            # a rollback copy before any real change
    _write(path, nxt)
    return "updated"


def _has_block(file: Path) -> bool:
    """A whole managed block (BEGIN ... END) is present. Unreadable or non-UTF-8 reads as no block."""
    try:
        if not file.is_file():
            return False
        text = _read(file)
    except (OSError, UnicodeDecodeError):
        return False
    end = text.rfind(_GUIDE_END)
    return end != -1 and text.rfind(_BEGIN_PREFIX, 0, end) != -1


def _write_gemini(folder: Path) -> str:
    """Gemini CLI reads GEMINI.md unless told otherwise; name AGENTS.md in its settings."""
    file = folder / "settings.json"
    data: object = {}
    if _exists(file):
        try:
            data = json.loads(_read(file))
        except ValueError:
            return "skipped (not valid JSON)"
        if not isinstance(data, dict):
            return "skipped (not a JSON object)"
    ctx = data.get("context") if isinstance(data.get("context"), dict) else {}
    names = ctx.get("fileName")
    names = [names] if isinstance(names, str) else names if isinstance(names, list) else []
    if "AGENTS.md" in names:
        return "unchanged"
    ctx["fileName"] = names + ["AGENTS.md"]
    data["context"] = ctx
    created = not _exists(file)
    _write(file, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return "created" if created else "updated"


def _project_card(name: str) -> str:
    title = name if re.fullmatch(r"[\w .\-/()]+", name, re.ASCII) else json.dumps(name, ensure_ascii=False)
    return "\n".join((
        "---", "type: Project", "title: " + title,
        "goal: <one line — what this project is for>",
        "invariants: []",
        "test_cmd: <the full test suite command>",
        "stage: prototype",
        "---", "## CARD",
        "goal: <the goal, in plain words>",
        "state: ADD installed — no work yet",
        "next: open your agent and run /add", "",
    ))


def _is_our_agent(file: Path, stem: str) -> bool:
    """An agent file is ours only if its frontmatter names itself after a retired ADD agent."""
    try:
        lines = re.split(r"\r?\n", _read(file))
    except (OSError, UnicodeDecodeError):
        return False
    if lines[0].strip() != "---":
        return False
    for line in lines[1:]:
        if line.strip() == "---":
            return False
        m = re.match(r"""^name:\s*["']?([^"'\s]+)["']?\s*$""", line)
        if m:
            return m.group(1) == stem
    return False


def _retire_agents(agents_dir: Path, shown) -> None:
    for stem in _RETIRED_AGENTS:
        file = agents_dir / (stem + ".md")
        if not file.is_symlink() and file.is_file() and _is_our_agent(file, stem):
            _rm(file)
            _row("removed", shown(stem + ".md") + " (3.x agent)")


def _step(what: str, fn):
    try:
        return fn()
    except (OSError, UnicodeDecodeError) as exc:
        raise StepError(f"could not write {what}: {exc}") from exc


def _install_project(target: Path, name: str | None, root: Path) -> None:
    def at(p: str) -> Path:
        return target.joinpath(*p.split("/"))

    _out(f"Installing ADD {_version()} into {target}")
    _row("skill", ".claude/skills/add/ " + _step(".claude/skills/add", lambda: _replace_tree(root / "skill" / "add", at(".claude/skills/add"))))
    _row("personas", ".add/personas-teacher/ " + _step(".add/personas-teacher", lambda: _replace_tree(root / "personas-teacher", at(".add/personas-teacher"))))
    _row("routing", ".add/personas-index/ " + _step(".add/personas-index", lambda: _replace_tree(root / "personas-index", at(".add/personas-index"))))

    def seed() -> None:
        added = kept = 0
        at(".add/personas").mkdir(parents=True, exist_ok=True)
        for src in sorted((root / "personas").iterdir(), key=lambda p: p.name):
            if not src.name.endswith(".md") or not src.is_file():
                continue
            dest = at(".add/personas") / src.name
            if _exists(dest):
                kept += 1
                continue
            shutil.copyfile(src, dest)
            added += 1
        _row("starters", f".add/personas/: {added} added, {kept} kept")
    _step(".add/personas", seed)

    def card() -> None:
        had = _exists(at(".add/PROJECT.md"))
        if not had:
            _write(at(".add/PROJECT.md"), _project_card(name or target.name))
        _row("project", ".add/PROJECT.md " + ("kept" if had else "created"))
    _step(".add/PROJECT.md", card)

    for d in ("specs", "milestones", "tasks"):
        def folder(d: str = d) -> None:
            at(".add/" + d).mkdir(parents=True, exist_ok=True)
            if not os.listdir(at(".add/" + d)):
                _write(at(".add/" + d + "/.gitkeep"), "")
        _step(".add/" + d, folder)
    _row("folders", ".add/specs/ .add/milestones/ .add/tasks/ ready")

    def gitignore() -> None:
        file = at(".add/.gitignore")
        if not _exists(file):
            _write(file, "# vendored copies the ADD installer refreshes - not project-authored\n" + "\n".join(_IGNORED) + "\n")
            return
        cur = _read(file)
        have = {line.strip() for line in re.split(r"\r?\n", cur)}
        missing = [line for line in _IGNORED if line not in have]
        if missing:
            _write(file, cur + ("" if cur == "" or cur.endswith("\n") else "\n") + "\n".join(missing) + "\n")
    _step(".add/.gitignore", gitignore)

    for f in ("CLAUDE.md", "AGENTS.md"):
        _row("guidance", f + " " + _step(f, lambda f=f: _write_pointer(at(f))))
    for f in _LEGACY_POINTERS:
        if _has_block(at(f)):
            _row("guidance", f + " " + _step(f, lambda f=f: _write_pointer(at(f))))
    if at(".gemini").is_dir():
        _row("gemini", ".gemini/settings.json " + _step(".gemini/settings.json", lambda: _write_gemini(at(".gemini"))))

    def tooling() -> None:                                    # 3.x leftovers go last
        t = at(".add/tooling")
        if t.is_symlink() or (t.is_dir() and (_exists(t / "add.py") or _exists(t / "cli.py"))):
            _rm(t)
            _row("removed", ".add/tooling/ (the 3.x engine)")
    _step(".add/tooling", tooling)
    _step(".claude/agents", lambda: _retire_agents(at(".claude/agents"), lambda n: ".claude/agents/" + n))
    _out("Done. Next: open your agent in this folder and run /add")
    _out("      (no slash commands? ask it to follow .claude/skills/add/SKILL.md)")


def _install_global(env, root: Path) -> None:
    home = Path(env.get("HOME") or Path.home())
    skill_dir = home / ".claude" / "skills" / "add"
    _out(f"Installing ADD {_version()} for this user")
    _row("skill", f"{skill_dir} " + _step(str(skill_dir), lambda: _replace_tree(root / "skill" / "add", skill_dir)))
    agents_dir = home / ".claude" / "agents"
    _step(str(agents_dir), lambda: _retire_agents(agents_dir, lambda n: str(agents_dir / n)))
    old_home = (Path(os.path.abspath(env["ADD_HOME"])) if env.get("ADD_HOME")
                else Path(os.path.abspath(env["XDG_DATA_HOME"])) / "add" if env.get("XDG_DATA_HOME")
                else home / ".add")
    if _exists(old_home / ".add-version"):
        _row("note", f"{old_home} is the 3.x global home; ADD 4.0 does not use it.")
        _row("", "Delete it once you no longer need anything in it (its data/ holds 3.x snapshots).")
    _out("Done. Next: open your agent in any project and run /add")


def _err(msg: str) -> None:
    print("error: " + msg, file=sys.stderr, flush=True)


def install(target: str = ".", name: str | None = None, *, as_global: bool = False,
            env=None, bundled: str | None = None) -> int:
    """Install ADD into `target` (or for this user with `as_global`). 0 ok · 1 failed."""
    root = Path(bundled) if bundled else _bundled_root()
    for p in REQUIRED:
        if not _exists(root / p):
            _err(f"the package is incomplete - missing {root / p}")
            return 1
    target_path = Path(os.path.abspath(target))
    if not as_global and not target_path.is_dir():
        _err(f"target directory does not exist: {target_path}")
        return 1
    try:
        if as_global:
            _install_global(os.environ if env is None else env, root)
        else:
            _install_project(target_path, name, root)
    except StepError as exc:
        _err(str(exc))
        _err("the install stopped part-way (the lines above landed); fix the cause and re-run - re-running is safe")
        return 1
    return 0
