#!/usr/bin/env python3
"""Throwaway spike dispatch — PROPOSAL v6 §3, D-18.

NOT the CLI (`e11`). This wires the eight drive-critical verbs to the engine so the M4 cost
census (`v8`) and the unwrapped drive (`v0'`) can run before the 200-line argparse CLI exists.
It carries no flag surface beyond what a drive needs, keeps `add.py` untouched (so the engine
budget, D-15, is not charged), and is deleted on NARROW/STOP or replaced by `e11` on PASS.

Contract: argv in -> the matching engine function -> its exit code out. Success is 0, an engine
refusal is 1, a usage error is 2. The dispatch judges nothing; the engine does.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import add  # noqa: E402

VERBS = ("init", "status", "new", "freeze", "run", "gate", "done", "brief")


def _opt(argv, name, default=None):
    """Pop `--name value` from argv (in place); return the value, or default."""
    if name in argv:
        i = argv.index(name)
        value = argv[i + 1]
        del argv[i:i + 2]
        return value
    return default


def _flag(argv, name):
    """Pop a bare `--name` from argv (in place); return whether it was present."""
    if name in argv:
        argv.remove(name)
        return True
    return False


def _resolve(root, ref):
    """A bare slug or a full cid -> a cid ('/tasks/x.md'). A slug resolves via the graph."""
    if "/" in ref or ref.endswith(".md"):
        return "/" + ref.lstrip("/")
    for cid in add.scan(root):
        if cid.rsplit("/", 1)[-1] == f"{ref}.md":
            return cid
    return f"/tasks/{ref}.md"  # best guess; the engine refuses if it is wrong


def main(argv):
    if not argv or argv[0] not in VERBS:
        print(f"usage: spike_cli.py <{'|'.join(VERBS)}> [--root DIR] ...", file=sys.stderr)
        return 2
    verb, rest = argv[0], list(argv[1:])
    root = Path(_opt(rest, "--root", ".add"))

    if verb == "init":
        profile = _opt(rest, "--profile", "code")
        _, _, note = add.init(root, profile, rest[0] if rest else None)
        print(note)
        return 0

    if verb == "status":
        print(add.status(root, all=_flag(rest, "--all"), check=_flag(rest, "--check")))
        return 0

    if verb == "new":
        # the node type is a FORMAT vocabulary word (Task/Milestone/…); accept any case so a
        # drive that types `new task` still lands the canonical `type: Task` + its scaffold.
        node_type, slug = rest[0].capitalize(), rest[1]
        fields = {}
        for key in ("--title", "--depth", "--sensitivity", "--kind", "--milestone"):
            value = _opt(rest, key)
            if value is not None:
                fields[key[2:]] = value
        scope = _opt(rest, "--scope")
        if scope is not None:
            fields["scope"] = scope.split(",")
        cid, note = add.new(root, node_type, slug, **fields)
        print(note)
        return 0 if cid else 1

    if verb == "brief":
        cid = _resolve(root, rest[0])
        by = _opt(rest, "--by", "spike")
        pack = add.brief(root, cid, phase=_opt(rest, "--phase"),
                         for_subagent=_flag(rest, "--for-subagent"))
        print(pack["text"])
        # Compiling for a frozen Task IS entering the build, and `gate` reads that stamp
        # (R:UNBRIEFED) — a drive that compiles without recording cannot reach a PASS.
        digest, note = add.brief_stamp(root, cid, by=by)
        if digest:
            print(note)
        return 0

    if verb == "freeze":
        node, note = add.freeze(root, _resolve(root, rest[0]),
                                by=_opt(rest, "--by", "spike"), authority=_opt(rest, "--authority"))
        print(note)
        return 0 if node else 1

    if verb == "run":
        junit = _opt(rest, "--junitxml")
        # scope: is relative to the repo, not the bundle — default cwd to the repo root so a
        # content digest can be taken (an empty digest degrades freshness and refuses the gate).
        cwd = _opt(rest, "--cwd") or (root.parent if root.name == ".add" else root)
        sep = rest.index("--")
        result = add.run(root, _resolve(root, rest[0]), rest[sep + 1:],
                         cwd=Path(cwd), junit=Path(junit) if junit else None)
        print(result["note"])
        return 0 if result["receipt"]["exit"] == 0 else 1

    if verb == "gate":
        ref, verdict = rest[0], rest[1]
        ok, note = add.gate(root, _resolve(root, ref), verdict,
                            by=_opt(rest, "--by", "spike"),
                            authority=_opt(rest, "--authority"), reason=_opt(rest, "--reason"))
        print(note)
        return 0 if ok else 1

    if verb == "done":
        ok, _missing, note = add.done(root, _resolve(root, rest[0]))
        print(note)
        return 0 if ok else 1

    return 2  # unreachable: VERBS is the guard


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
