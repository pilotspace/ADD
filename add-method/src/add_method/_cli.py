"""Console-script entry point `pilotspace-add` — the same flags and exit codes as bin/cli.js.

    pilotspace-add [init|update] [dir] [--name <name>]    install into a project
    pilotspace-add --global                               install for this user

Exit codes: 0 ok · 1 the install failed (the output says what landed) · 2 bad usage.
The parser is hand-written, not argparse, so both twins accept and refuse exactly the same input.
"""
from __future__ import annotations

import sys

PROG = "pilotspace-add"


class Usage(Exception):
    pass


def usage() -> str:
    return "\n".join((
        f"usage: {PROG} [init|update] [dir] [--name <name>]",
        f"       {PROG} --global",
        "",
        "Installs the ADD skill into a project (default: the current folder):",
        "  .claude/skills/add/     the skill, refreshed on every run",
        "  .add/                   PROJECT.md, specs/ milestones/ tasks/, personas - never overwritten",
        "  CLAUDE.md, AGENTS.md    a short managed block that points your agent at the skill",
        "Re-running is safe. Over a 3.x project it also removes the vendored engine",
        "(.add/tooling/) and ADD's 3.x agents in .claude/agents/.",
        "",
        "options:",
        "  --name <name>   project name for a new .add/PROJECT.md (default: the folder name)",
        "  --global        install the skill for your user (~/.claude/skills/add), no project",
        "  --version       print the version",
        "  -h, --help      show this help",
    ))


def parse(argv: list[str]) -> dict:
    a = {"positional": [], "name": None, "global": False, "help": False, "version": False}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            a["help"] = True
        elif arg == "--version":
            a["version"] = True
        elif arg == "--global":
            a["global"] = True
        elif arg in ("--yes", "-y", "--non-interactive"):
            pass                                        # 3.x scripts: no prompts now
        elif arg == "--name":
            i += 1
            if i >= len(argv) or argv[i].startswith("-"):
                raise Usage("--name needs a value")
            a["name"] = argv[i]
        elif arg.startswith("-"):
            raise Usage("unknown option " + arg)
        else:
            a["positional"].append(arg)
        i += 1
    pos = a["positional"]
    if pos and pos[0] in ("init", "update", "help"):
        if pos.pop(0) == "help":
            a["help"] = True
    if a["help"] or a["version"]:
        return a
    if pos and pos[0] == "prune-data":
        raise Usage("prune-data was retired in ADD 4.0")
    if len(pos) > 1:
        raise Usage("too many arguments: " + " ".join(pos))
    if a["global"] and pos:
        raise Usage("--global installs for your user and takes no directory")
    return a


def main(argv: list[str] | None = None) -> int:
    try:
        a = parse(list(sys.argv[1:] if argv is None else argv))
    except Usage as exc:
        print(f"error: {exc}\n" + "\n".join(usage().splitlines()[:2]), file=sys.stderr)
        return 2
    if a["help"]:
        print(usage())
        return 0
    if a["version"]:
        from add_method import __version__
        print(__version__)
        return 0
    from add_method._installer import install
    return install(a["positional"][0] if a["positional"] else ".", a["name"], as_global=a["global"])


if __name__ == "__main__":
    sys.exit(main())
