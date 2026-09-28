#!/usr/bin/env python3
"""book_lint — structural and vocabulary checks for the ADD book (add-method/docs/).

ADD 4.0 has no engine and no CLI: the method is one skill, run with files, git and the project's
own test command. The book must teach exactly that. These pure-read helpers back
`tests/book/test_book.py` and can be run by hand:

    python3 add-method/scripts/book_lint.py        # exit 1 and a list of problems, or exit 0

Checks:
  * every page named in the repo-root mkdocs.yml nav exists, and every docs page is in the nav;
  * every relative link and image in a page resolves to a file inside docs/;
  * no page tells the reader to run a retired 3.x verb (`add status`, `add freeze`, ...) in a code
    span or code block, and no page names the removed engine files — except the one migration page,
    whose job is to name them.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]          # add-method/
DOCS = PKG / "docs"
MKDOCS = PKG.parent / "mkdocs.yml"

# The page that explains what 4.0 removed. Naming the retired surface is its whole job.
MIGRATION_PAGE = "20-whats-new-in-4.md"

# The 3.x CLI verbs (the same list the skill guard uses, tests/test_skill_only.py).
RETIRED_VERBS = ("status", "init", "new", "brief", "upgrade", "freeze", "interview", "replan",
                 "repair", "run", "gate", "done", "learn", "check", "milestone-done", "deltas",
                 "fold", "drop", "reopen", "milestone-archive", "doctor", "wave", "join", "advise",
                 "refute", "release", "locate", "todo", "show", "search")

# Names of the removed engine and agent roster. Prose that names them points at nothing.
ENGINE_NAMES = ("cli.py", "add.py", ".add/tooling", "add-worker", "add-advisor", "graph.json")

# `add <verb>` as a command: not glued to a path or package name, so `npx @pilotspace/add init`,
# `pilotspace-add update`, `/add status` (the Claude Code skill invocation) and `git add .add/`
# do not read as engine calls.
VERB_RE = re.compile(r"(?<![\w/@.-])add\s+(" + "|".join(map(re.escape, RETIRED_VERBS))
                     + r")(?![\w-])")
CODE_SPAN = re.compile(r"`[^`\n]+`")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
NAV_ENTRY = re.compile(r"^\s*-\s*(?:.*:\s*)?\"?([\w./-]+\.md)\"?\s*$")


def pages(docs: Path = DOCS) -> list[str]:
    """Every markdown page under docs/, as a docs-relative posix path."""
    return sorted(p.relative_to(docs).as_posix() for p in docs.rglob("*.md"))


def nav_pages(mkdocs: Path = MKDOCS) -> list[str]:
    """The .md files the mkdocs nav lists, in order."""
    lines = mkdocs.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("nav:"))
    out = []
    for line in lines[start + 1:]:
        if line and not line.startswith((" ", "-", "#")):
            break                                   # the next top-level key ends the nav
        m = NAV_ENTRY.match(line)
        if m:
            out.append(m.group(1))
    return out


def internal_links(text: str) -> list[str]:
    """Relative link and image targets, anchors stripped. URLs and pure anchors are skipped."""
    out = []
    for target in LINK_RE.findall(text):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        out.append(target.split("#", 1)[0])
    return [t for t in out if t]


def unresolved_links(docs: Path = DOCS) -> list[tuple[str, str]]:
    """(page, target) for every relative link that does not land on a file inside docs/."""
    bad = []
    root = docs.resolve()
    for rel in pages(docs):
        page = docs / rel
        for target in internal_links(page.read_text(encoding="utf-8")):
            dest = (page.parent / target).resolve()
            if not dest.is_file() or root not in dest.parents:
                bad.append((rel, target))
    return bad


def retired_verb_hits(text: str) -> list[tuple[int, str]]:
    """(line, verb) for every retired verb stated as a command — in a code span or a code block."""
    hits, fenced = [], False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        code = line if fenced else " ".join(s.strip("`") for s in CODE_SPAN.findall(line))
        hits.extend((n, v) for v in VERB_RE.findall(code))
    return hits


def engine_name_hits(text: str) -> list[tuple[int, str]]:
    """(line, name) for every mention of a removed engine file or roster agent."""
    return [(n, name) for n, line in enumerate(text.splitlines(), 1)
            for name in ENGINE_NAMES if name in line]


def problems(docs: Path = DOCS, mkdocs: Path = MKDOCS) -> list[str]:
    out = []
    nav, have = nav_pages(mkdocs), set(pages(docs))
    out += [f"nav names a missing page: {p}" for p in nav if p not in have]
    out += [f"page is not in the nav: {p}" for p in sorted(have - set(nav))]
    out += [f"{p}: unresolved link {t}" for p, t in unresolved_links(docs)]
    for rel in sorted(have - {MIGRATION_PAGE}):
        text = (docs / rel).read_text(encoding="utf-8")
        out += [f"{rel}:{n}: retired verb `add {v}`" for n, v in retired_verb_hits(text)]
        out += [f"{rel}:{n}: names removed engine file {x}" for n, x in engine_name_hits(text)]
    return out


if __name__ == "__main__":
    found = problems()
    print("\n".join(found) if found else "book_lint: clean")
    sys.exit(1 if found else 0)
