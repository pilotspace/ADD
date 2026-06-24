"""Console-script entry point: pilotspace-add.

Mirrors bin/cli.js command structure:
    pilotspace-add init [targetDir] [--force] [--stage STAGE] [--name NAME]
    pilotspace-add help
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    """Entry point registered as the `pilotspace-add` console script."""
    raw = argv if argv is not None else sys.argv[1:]

    # Pull off the subcommand (default: init), matching cli.js behaviour.
    if raw and not raw[0].startswith("-"):
        cmd, rest = raw[0], raw[1:]
    else:
        cmd, rest = "init", raw

    if cmd in ("help", "--help", "-h"):
        print("usage: pilotspace-add <init|update> [targetDir] [--force] [--check] [--global]")
        print("  init    install the ADD skill + tooling + book into a project")
        print("          (--global ALSO installs to a shared home [ADD_HOME|XDG_DATA_HOME/add|"
              "~/.add] + registers the project)")
        print("  update  re-materialize skill/tooling/docs to this package version "
              "(preserves your state)")
        print("          (--global refreshes the shared home + propagates to every registered "
              "project)")
        return 0

    if cmd == "update":
        parser = argparse.ArgumentParser(prog="pilotspace-add update")
        parser.add_argument("target", nargs="?", default=".",
                            help="Target project directory (default: cwd)")
        parser.add_argument("--force", action="store_true",
                            help="re-materialize even when already current")
        parser.add_argument("--check", action="store_true",
                            help="report version drift without writing anything")
        # accepted for CLI-surface parity with init / the npm twin; update is
        # non-interactive by nature, so these are no-ops here.
        parser.add_argument("--yes", "-y", action="store_true", help=argparse.SUPPRESS)
        parser.add_argument("--non-interactive", dest="non_interactive",
                            action="store_true", help=argparse.SUPPRESS)
        parser.add_argument("--global", dest="as_global", action="store_true",
                            help="refresh the shared global home + propagate to every "
                                 "registered project")
        args = parser.parse_args(rest)
        from add_method._installer import update, update_check
        if args.check:
            return update_check(target=args.target)
        return update(target=args.target, force=args.force, channel="pip",
                      as_global=args.as_global)

    if cmd != "init":
        print(f"pilotspace-add: error: unknown command '{cmd}'. Try: pilotspace-add init",
              file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(
        prog="pilotspace-add",
        description="Install the ADD method into a target project.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target project directory (default: cwd)",
    )
    parser.add_argument("--force", action="store_true",
                        help="Overwrite an existing skill tree (never touches project state)")
    parser.add_argument("--stage", default=None,
                        choices=("prototype", "poc", "mvp", "production"),
                        help="Initial project stage for the manual-init hint; "
                             "omit it and `add.py init` itself defaults "
                             "to prototype")
    parser.add_argument("--name", default=None,
                        help="Project name (default: target directory name)")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="skip prompts and take defaults (forces the non-interactive path)")
    parser.add_argument("--non-interactive", dest="non_interactive", action="store_true",
                        help="never prompt; take defaults (same as --yes; what CI / pipes do)")
    parser.add_argument("--global", dest="as_global", action="store_true",
                        help="ALSO install the managed layer to a shared home "
                             "(ADD_HOME|XDG_DATA_HOME/add|~/.add) + register this project")
    parser.add_argument("--global-data", dest="as_global_data", action="store_true",
                        help="(implies --global) ALSO persist this project's user-data "
                             "under <home>/data/<key> keyed by path")
    parser.add_argument("--rule-file", dest="rule_file", action="store_true",
                        help="write the ADD block to .claude/rules/add-workflows.md and "
                             "reference it from CLAUDE.md (auto-on when a .ccsk/ dir is present)")

    args = parser.parse_args(rest)

    from add_method._installer import install
    return install(
        target=args.target,
        force=args.force,
        stage=args.stage,
        name=args.name,
        yes=args.yes,
        non_interactive=args.non_interactive,
        as_global=args.as_global,
        as_global_data=args.as_global_data,
        rule_file=args.rule_file,
    )


if __name__ == "__main__":
    sys.exit(main())
