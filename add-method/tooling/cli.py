#!/usr/bin/env python3
"""add — the ABF-1 command line (e11).

A thin argparse dispatch over the engine (`add.py`). It graduates the throwaway `spike_cli.py`:
same contract — argv in, the matching engine function, its exit code out — but a real subcommand
surface with `--help`. It lives OUTSIDE the engine budget (PROPOSAL T2) precisely so the CLI can
grow help text without a comment competing with a feature in the notary.

Exit codes: 0 success · 1 an engine refusal (the notary declined to manufacture an unsupported
record) · 2 a usage error (argparse). The dispatch judges nothing; the engine does.

Every verb the skill refers to is wired to a real engine function:
    init · status · new · brief · freeze · run · gate · done · learn · milestone-done ·
    deltas · fold · reopen · milestone-archive · doctor · wave · join · advise · locate · todo
(The anti-seam test in tests/engine/test_cli.py enforces advertised == wired — no phantom verbs.)
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import add  # noqa: E402


# The 5-DD method vocabulary the skill teaches → the spec filename the engine writes.
# Accept both, so `add learn add …` (method vocab) and `add learn method …` (raw) both land.
DD_LENS = {"ddd": "domain", "sdd": "system", "udd": "experience", "tdd": "quality", "add": "method"}


def _resolve(root, ref: str) -> str:
    """A bare slug or a full cid -> a cid ('/tasks/x.md'). A slug resolves via the graph."""
    if "/" in ref or ref.endswith(".md"):
        return "/" + ref.lstrip("/")
    for cid in add.scan(root):
        if cid.rsplit("/", 1)[-1] == f"{ref}.md":
            return cid
    return f"/tasks/{ref}.md"  # best guess; the engine refuses if it is wrong


def _split_run(argv):
    """Return (argv_before_dashdash, cmd_after). `run` passes the test command after `--`."""
    if "--" in argv:
        i = argv.index("--")
        return argv[:i], argv[i + 1:]
    return argv, []


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="add", description="ABF-1 — direction · evidence · a durable bundle")
    p.add_argument("--root", default=".add", help="the bundle root (default: .add)")
    sub = p.add_subparsers(dest="verb", required=True, metavar="<verb>")

    s = sub.add_parser("init", help="create a .add/ bundle")
    s.add_argument("name", nargs="?", help="the project name")
    s.add_argument("--profile", default="code", help="code | doc (default: code)")

    s = sub.add_parser("status", help="resume — read first, every session")
    s.add_argument("--all", action="store_true", help="the full report")
    s.add_argument("--check", action="store_true", help="conformance findings")

    s = sub.add_parser("new", help="create a typed node")
    s.add_argument("type", help="Task | Milestone | Persona | … (any case)")
    s.add_argument("slug")
    s.add_argument("--title")
    s.add_argument("--depth", help="quick | standard | deep")
    s.add_argument("--sensitivity")
    s.add_argument("--kind")
    s.add_argument("--milestone")
    s.add_argument("--scope", action="append",
                   help="paths — repeat the flag and/or comma-separate; occurrences append")

    s = sub.add_parser("brief", help="the composed XML prompt for the active beat")
    s.add_argument("ref")
    s.add_argument("--phase")
    s.add_argument("--for-subagent", action="store_true")
    s.add_argument("--by", default="cli")

    s = sub.add_parser("upgrade", help="archive a 2.x bundle whole, initialise 3.0 beside it")
    s.add_argument("--by", default="cli")

    s = sub.add_parser("freeze", help="the one approval → Build")
    s.add_argument("ref")
    s.add_argument("--by", default="cli")
    s.add_argument("--authority")

    s = sub.add_parser("replan", help="record a steering amendment on a frozen task (the seal untouched)")
    s.add_argument("ref")
    s.add_argument("--note", default="")
    s.add_argument("--by", default="builder")

    s = sub.add_parser("run", help="execute → a fresh, bound receipt (cmd after --)")
    s.add_argument("ref")
    s.add_argument("--junitxml")
    s.add_argument("--cwd")
    s.add_argument("--timeout", type=int, help="ceiling in seconds for the wrapped command "
                   "(default 900 — a build-heavy receipt command needs more)")

    s = sub.add_parser("gate", help="the verdict: PASS · RISK-ACCEPTED · HARD-STOP")
    s.add_argument("ref")
    s.add_argument("verdict")
    s.add_argument("--by", default="cli")
    s.add_argument("--authority")
    s.add_argument("--reason")

    s = sub.add_parser("done", help="close a gated task")
    s.add_argument("ref")

    s = sub.add_parser("learn", help="file a lesson into a living spec (evidence required)")
    s.add_argument("lens", help="ddd | sdd | udd | tdd | add (the spec it sharpens)")
    s.add_argument("lesson")
    s.add_argument("--evidence", help="the receipt or decision that caused it")

    s = sub.add_parser("milestone-done", help="close a milestone — refuses while a goal box is unchecked")
    s.add_argument("ref")

    s = sub.add_parser("deltas", help="list open deltas across the specs (the carried inventory)")
    s.add_argument("--status", default="open", help="open | folded | rejected (default: open)")

    s = sub.add_parser("fold", help="retag a named open delta folded (human consolidation)")
    s.add_argument("lens", help="the spec: domain|system|experience|quality|method")
    s.add_argument("match", help="a substring naming the open delta to fold")

    s = sub.add_parser("reopen", help="return a done task to a beat with a reset gate + reason")
    s.add_argument("ref")
    s.add_argument("--to", required=True, help="the beat: direction | build | verify")
    s.add_argument("--reason", required=True, help="why it is being reopened")

    s = sub.add_parser("milestone-archive", help="retire a done milestone — refuses one not done")
    s.add_argument("ref")

    s = sub.add_parser("doctor", help="conformance findings; --sync repairs compiled artifacts + re-vendors stale tooling")
    s.add_argument("--sync", action="store_true", help="recompute compiled artifacts and re-vendor a stale engine")

    s = sub.add_parser("wave", help="plan a parallel wave from the task DAG (levels; --streams records one)")
    s.add_argument("ref", help="the milestone to plan")
    s.add_argument("--streams", help="comma-separated task slugs to record as the active wave")

    s = sub.add_parser("join", help="fold worktree stream bundles back — PASS-only, union deltas, regen graph")
    s.add_argument("bundles", nargs="+", help="paths to each stream's .add/ bundle (one per worktree)")

    s = sub.add_parser("advise", help="record a persona lens on a sequential beat (NO-EXEC; feeds the coverage floor)")
    s.add_argument("ref", help="the task/milestone to advise")
    s.add_argument("--persona", required=True, help="the Persona slug advising this beat")

    s = sub.add_parser("locate", help="reverse lookup — which node's scope owns a path (read-only)")
    s.add_argument("path", help="the file or directory path to locate")

    s = sub.add_parser("todo", help="the open worklist — active tasks grouped by beat (read-only)")
    s.add_argument("--milestone", help="restrict to one milestone's tasks")

    return p


def dispatch(args, run_cmd) -> int:
    root = Path(args.root)

    if args.verb == "init":
        graph, _, note = add.init(root, args.profile, args.name)
        print(note)
        return 0 if graph else 1

    if args.verb == "status":
        print(add.status(root, all=args.all, check=args.check))
        return 0

    if args.verb == "new":
        fields = {k: getattr(args, k) for k in ("title", "depth", "sensitivity", "kind", "milestone")
                  if getattr(args, k) is not None}
        if args.scope is not None:
            # `action="append"` makes each occurrence a list entry; commas expand in place,
            # so `--scope a.py --scope b.py,c.py` -> [a.py, b.py, c.py] (R:LASTWINS).
            fields["scope"] = [p.strip() for chunk in args.scope
                               for p in chunk.split(",") if p.strip()]
        cid, note = add.new(root, args.type.capitalize(), args.slug, **fields)
        print(note)
        return 0 if cid else 1

    if args.verb == "upgrade":
        # The verb works on the PROJECT, not the bundle: `.add/` is what gets archived.
        report, note = add.upgrade(Path(args.root).resolve().parent, by=args.by)
        print(note)
        return 0 if report else 1

    if args.verb == "brief":
        cid = _resolve(root, args.ref)
        pack = add.brief(root, cid, phase=args.phase, for_subagent=args.for_subagent)
        print(pack["text"])
        # W1 (R:UNBRIEFED): compiling for a frozen Task IS entering the build — record it.
        # The stamp is what `gate` reads; an unfrozen or non-Task compile stays a pure read.
        digest, note = add.brief_stamp(root, cid, by=args.by)
        if digest:
            print(note)
        return 0

    if args.verb == "freeze":
        node, note = add.freeze(root, _resolve(root, args.ref), by=args.by, authority=args.authority)
        print(note)
        return 0 if node else 1

    if args.verb == "replan":
        node, note = add.replan(root, _resolve(root, args.ref), note=args.note, by=args.by)
        print(note)
        return 0 if node else 1

    if args.verb == "run":
        cwd = args.cwd or (root.parent if root.name == ".add" else root)
        result = add.run(root, _resolve(root, args.ref), run_cmd,
                         cwd=Path(cwd), timeout=args.timeout or add.RUN_TIMEOUT,
                         junit=Path(args.junitxml) if args.junitxml else None)
        print(result["note"])
        return 0 if result["receipt"]["exit"] == 0 else 1

    if args.verb == "gate":
        ok, note = add.gate(root, _resolve(root, args.ref), args.verdict,
                            by=args.by, authority=args.authority, reason=args.reason)
        print(note)
        return 0 if ok else 1

    if args.verb == "done":
        ok, _missing, note = add.done(root, _resolve(root, args.ref))
        print(note)
        return 0 if ok else 1

    if args.verb == "learn":
        lens = DD_LENS.get(args.lens.lower(), args.lens)  # 5-DD vocab → spec filename
        ok, note = add.learn(root, lens, args.lesson, evidence=args.evidence)
        print(note)
        return 0 if ok else 1

    if args.verb == "milestone-done":
        ok, note = add.milestone_done(root, _resolve(root, args.ref))
        print(note)
        return 0 if ok else 1

    if args.verb == "deltas":
        _items, note = add.deltas(root, status=args.status)
        print(note)
        return 0

    if args.verb == "fold":
        ok, note = add.fold(root, DD_LENS.get(args.lens.lower(), args.lens), args.match)
        print(note)
        return 0 if ok else 1

    if args.verb == "reopen":
        ok, note = add.reopen(root, _resolve(root, args.ref), args.to, args.reason)
        print(note)
        return 0 if ok else 1

    if args.verb == "milestone-archive":
        ok, note = add.milestone_archive(root, _resolve(root, args.ref))
        print(note)
        return 0 if ok else 1

    if args.verb == "wave":
        streams = args.streams.split(",") if args.streams else None
        plan, note = add.wave(root, _resolve(root, args.ref), streams=streams)
        print(note)
        return 0 if plan is not None else 1

    if args.verb == "join":
        _result, note = add.join(root, [Path(b) for b in args.bundles])
        print(note)  # a skipped HARD-STOP stream is reported in the note, not an engine refusal
        return 0

    if args.verb == "advise":
        out, note = add.advise(root, _resolve(root, args.ref), args.persona)
        print(note)
        return 0 if out else 1

    if args.verb == "locate":
        _hits, note = add.locate(root, args.path)
        print(note)  # a no-match is a valid answer, not an error
        return 0

    if args.verb == "todo":
        _items, note = add.todo(root, milestone=args.milestone)
        print(note)
        return 0

    if args.verb == "doctor":
        if args.sync:
            _changed, note = add.doctor_sync(root)
            print(note)
            return 0
        findings = add.doctor(root)
        for f in findings:
            print(f"  {f['severity']:5} {f['code']}: {f['detail']}")
        print(f"{len(findings)} finding(s) — `add doctor --sync` repairs what it can"
              if findings else "no findings\nnext: add status")
        return 0

    return 2  # unreachable: subparser required=True is the guard


def main(argv) -> int:
    # `run` takes a free-form command after `--`; keep it clear of argparse.
    head, run_cmd = _split_run(list(argv))
    args = build_parser().parse_args(head)
    return dispatch(args, run_cmd)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
