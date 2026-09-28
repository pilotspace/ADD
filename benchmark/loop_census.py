#!/usr/bin/env python3
"""loop_census — did an ADD run actually walk the loop? Counted from what the run LEFT.

ADD 4.0 has no engine, so the 3.x engine-call census (`score._engine_call_census`) reads 0
on a perfectly disciplined 4.0 run. What a 4.0 run leaves instead is workspace state, and
this counts it:

* `tasks` — `.add/tasks/*.md` files (top level only: 3.7's `<slug>.d/runs/` receipts are not tasks)
* `freeze_commits` / `refreeze_commits` / `verify_commits` (+ verdicts) — commit SUBJECTS in the
  workspace's own git history, `freeze(<slug>)` · `refreeze(<slug>)` · `verify(<slug>): <verdict>`
* `evidence_verdicts` — task files whose `## EVIDENCE` carries a real verdict line
  (`verdict: PASS` in 4.0, `gate: PASS` in 3.7 — never the `<PASS | …>` template)
* `seals_intact` / `seals_broken` — per sealed slug, did the files of its latest
  freeze/refreeze commit stay byte-identical until its verify commit (or HEAD)?
* `red_first` — from the transcript: did a test run FAIL (assertions, not an import error)
  before the first seal? A 3.x `cli.py freeze` counts as a seal too, so both arms are
  read by the same rule.

The one thing this must never do is return a vacuous zero. A benchmark workspace lives
INSIDE the harness's git repo, so git asked from a workspace without its own repo answers
from the PARENT; a wrong path answers nothing. Either way the result is
`{"measured": False, "reason": ...}` and carries NO counts — so "0 freezes" always means
git was read, in the workspace's own repo, and found none.

A census, never a score: it lands in a record's `artifacts`, not its metrics.

    python3 -m benchmark.loop_census <workspace> [--transcript <transcript.jsonl>]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
from collections import Counter

VERDICTS = ("PASS", "RISK-ACCEPTED", "HARD-STOP")
_FREEZE = re.compile(r"^freeze\(([^)\s]+)\)")
_REFREEZE = re.compile(r"^refreeze\(([^)\s]+)\)")
_VERIFY = re.compile(r"^verify\(([^)\s]+)\)\s*:?\s*(PASS|RISK-ACCEPTED|HARD-STOP)?")
# a verdict line inside ## EVIDENCE: `verdict: PASS` (4.0) · `gate: PASS` (3.7), optionally
# bulleted or bolded. The token must follow the colon directly, so `<PASS | …>` never matches.
_EVIDENCE_LINE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:\*\*)?(?:verdict|gate)(?:\*\*)?\s*:\s*(?:\*\*)?"
    r"(PASS|RISK-ACCEPTED|HARD-STOP)\b", re.IGNORECASE | re.MULTILINE)


class Unmeasurable(Exception):
    """The workspace cannot be read as its own git repo — any count would be a lie."""


def _git(ws: pathlib.Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ws), *args], capture_output=True, text=True,
                          check=check)


def _guard(ws: pathlib.Path) -> None:
    if not ws.is_dir():
        raise Unmeasurable(f"workspace missing: {ws}")
    if not (ws / ".git").exists():
        raise Unmeasurable(f"no workspace git repo: {ws / '.git'} absent — git would answer "
                           "from an enclosing repo, not this run")
    top = _git(ws, "rev-parse", "--show-toplevel", check=False)
    if top.returncode != 0:
        raise Unmeasurable(f"{ws / '.git'} is not a readable git repo: {top.stderr.strip()}")
    if pathlib.Path(top.stdout.strip()).resolve() != ws.resolve():
        raise Unmeasurable(f"git toplevel is {top.stdout.strip()}, not the workspace {ws}")


def _commits(ws: pathlib.Path) -> list[tuple[str, str]]:
    """(sha, subject), oldest first. A repo with no commit yet is a measured empty history."""
    if _git(ws, "rev-parse", "--verify", "-q", "HEAD", check=False).returncode != 0:
        return []
    out = _git(ws, "log", "--reverse", "--format=%H%x1f%s").stdout
    return [tuple(line.split("\x1f", 1)) for line in out.splitlines() if "\x1f" in line]


def _evidence_verdict(text: str) -> str | None:
    """The verdict written under `## EVIDENCE`, or None. Only that section is read."""
    m = re.search(r"^##\s+EVIDENCE\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    if not m:
        return None
    hit = _EVIDENCE_LINE.search(m.group(1))
    return hit.group(1).upper() if hit else None


_CHECK_PATH = re.compile(r"([\w./-]+\.(?:py|js|mjs|cjs|ts|tsx|jsx|go|rs|rb|java|kt|sh))(?:::|\b)")
_NOT_SEALED = re.compile(r"(^|/)__pycache__/|\.pyc$|^\.gitignore$|^\.add/PROJECT\.md$")


def _sealed_files(ws: pathlib.Path, seal: str, slug: str, carried: list[str]) -> list[str]:
    """What SKILL.md seals: the task file plus the files its `## CHECKS` name. Other files that
    rode along in the seal commit (PROJECT.md's test_cmd, a .pyc, .gitignore) are not sealed.
    If the CHECKS name no file the census can recognise, fall back to the carried files minus
    that known infrastructure, so a seal never silently shrinks to nothing."""
    task = f".add/tasks/{slug}.md"
    body = _git(ws, "show", f"{seal}:{task}", check=False).stdout
    checks = body.split("## CHECKS", 1)[1].split("\n## ", 1)[0] if "## CHECKS" in body else ""
    named = set(_CHECK_PATH.findall(checks))
    if named:
        return sorted(f for f in carried if f == task or f in named)
    return sorted(f for f in carried if not _NOT_SEALED.search(f))


def _seal_state(ws: pathlib.Path, commits: list[tuple[str, str]]) -> tuple[list[str], int, list[str]]:
    """Per sealed slug: the latest freeze/refreeze before its verify is the seal; every file its
    seal commits carried must be unchanged from that seal to the verify commit's parent (the
    verify commit is where `status:` and `## EVIDENCE` legitimately change), or to HEAD when
    unverified. A file a later non-seal commit deletes counts as changed."""
    sealed: dict[str, str] = {}
    seal_commits: dict[str, list[str]] = {}
    verified_at: dict[str, str] = {}
    for sha, subject in commits:
        for rx in (_FREEZE, _REFREEZE):
            m = rx.match(subject)
            if m and m.group(1) not in verified_at:
                sealed[m.group(1)] = sha
                seal_commits.setdefault(m.group(1), []).append(sha)
        v = _VERIFY.match(subject)
        if v and v.group(1) in sealed and v.group(1) not in verified_at:
            verified_at[v.group(1)] = sha
    intact, broken = 0, []
    for slug, seal in sorted(sealed.items()):
        end = f"{verified_at[slug]}^" if slug in verified_at else "HEAD"
        # the sealed set is every file ANY of the slug's seal commits carried: a refreeze commit
        # names only what it changed, yet the task file the first freeze sealed stays sealed
        carried = sorted({f for c in seal_commits[slug]
                          for f in _git(ws, "diff-tree", "--root", "--no-commit-id", "--name-only",
                                        "-r", c).stdout.splitlines() if f})
        files = _sealed_files(ws, seal, slug, carried)
        if not files:
            broken.append(slug)          # a seal that sealed nothing is not a seal
            continue
        same = _git(ws, "diff", "--quiet", seal, end, "--", *files, check=False).returncode == 0
        if same:
            intact += 1
        else:
            broken.append(slug)
    return sorted(sealed), intact, broken


# ------------------------------------------------------------ transcript: red before seal

_TEST_CMD = re.compile(r"\bpytest\b|\bunittest\b|\bnpm (?:run )?test\b|\bgo test\b|\bcargo test\b")
# NotImplementedError is a stub saying "behavior absent" — red for the right reason.
_FAILED = re.compile(r"\b\d+ failed\b|FAILED \((?:failures|errors)=|\bFAIL:|\bAssertionError\b|"
                     r"\bNotImplementedError\b")
_ERRORED = re.compile(r"\b\d+ errors?\b|ERROR collecting|ModuleNotFoundError|ImportError|"
                      r"SyntaxError|Interrupted: \d+ errors?")
_SEAL_4 = re.compile(r"git\b[^\n]*\bcommit\b[^\n]*\bfreeze\(")
_SEAL_3 = re.compile(r"(?:\.add/tooling/cli\.py|add\.py)\s+freeze\b")


_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _result_text(content: object) -> str:
    """Tool output with ANSI color codes stripped: unittest/pytest color their markers, and a code
    ending in `m` glued to `AssertionError` defeats the word boundary the patterns rely on."""
    if isinstance(content, str):
        return _ANSI.sub("", content)
    if isinstance(content, list):
        return _ANSI.sub("", "\n".join(str(b.get("text", "")) for b in content if isinstance(b, dict)))
    return ""


def red_first(transcript: pathlib.Path) -> dict:
    """Did a test run fail on ASSERTIONS before the first seal command?

    `red_first` is True/False only when a seal was seen; with no seal (or no transcript) it is
    None — undetectable, never False. An import/collection error is counted apart: SKILL.md
    says a check must fail "because the behavior is absent — not on an import error"."""
    transcript = pathlib.Path(transcript)
    if not transcript.is_file():
        return {"red_first": None, "reason": f"transcript missing: {transcript}"}
    pending: dict[str, str] = {}
    runs = failing = errors = 0
    seal_seen = False
    for line in transcript.read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = event.get("message") if isinstance(event, dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        for block in content if isinstance(content, list) else []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") == "Bash":
                cmd = str((block.get("input") or {}).get("command", ""))
                is_seal = bool(_SEAL_4.search(cmd) or _SEAL_3.search(cmd))
                if is_seal and not _TEST_CMD.search(cmd):
                    seal_seen = True
                    break
                if _TEST_CMD.search(cmd):
                    # a command that runs the checks AND commits the seal (SKILL.md's turn rule):
                    # its test output precedes the commit, so it counts, then the seal is seen
                    pending[str(block.get("id"))] = "seal" if is_seal else cmd
            elif block.get("type") == "tool_result" and str(block.get("tool_use_id")) in pending:
                kind = pending.pop(str(block.get("tool_use_id")))
                text = _result_text(block.get("content"))
                runs += 1
                if _FAILED.search(text):
                    failing += 1
                elif _ERRORED.search(text) or block.get("is_error"):
                    errors += 1
                if kind == "seal":
                    seal_seen = True
                    break
        if seal_seen:
            break
    return {
        "seal_seen": seal_seen,
        "test_runs_before_seal": runs,
        "failing_runs_before_seal": failing,
        "error_runs_before_seal": errors,
        "red_first": (failing > 0) if seal_seen else None,
    }


# ------------------------------------------------------------------------- the census


def census(workspace: pathlib.Path, transcript: pathlib.Path | None = None) -> dict:
    workspace = pathlib.Path(workspace)
    try:
        _guard(workspace)
    except Unmeasurable as exc:
        out = {"measured": False, "reason": str(exc)}
        if transcript is not None:
            out["red_first"] = red_first(transcript)
        return out
    commits = _commits(workspace)
    subjects = [s for _, s in commits]
    tasks_dir = workspace / ".add" / "tasks"
    task_files = sorted(tasks_dir.glob("*.md")) if tasks_dir.is_dir() else []
    evidence = Counter(v for v in (_evidence_verdict(p.read_text(errors="replace"))
                                   for p in task_files) if v)
    verify_verdicts = Counter((m.group(2) or "none") for m in map(_VERIFY.match, subjects) if m)
    sealed, intact, broken = _seal_state(workspace, commits)
    out = {
        "measured": True,
        "bundle_present": (workspace / ".add").is_dir(),
        "commits": len(commits),
        "tasks": len(task_files),
        "freeze_commits": sum(1 for s in subjects if _FREEZE.match(s)),
        "refreeze_commits": sum(1 for s in subjects if _REFREEZE.match(s)),
        "verify_commits": sum(verify_verdicts.values()),
        "verify_verdicts": dict(sorted(verify_verdicts.items())),
        "evidence_verdicts": dict(sorted(evidence.items())),
        "sealed_slugs": sealed,
        "seals_intact": intact,
        "seals_broken": broken,
    }
    if transcript is not None:
        out["red_first"] = red_first(transcript)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="loop_census.py", description=__doc__.splitlines()[0])
    ap.add_argument("workspace")
    ap.add_argument("--transcript", default=None)
    args = ap.parse_args(argv)
    out = census(pathlib.Path(args.workspace),
                 pathlib.Path(args.transcript) if args.transcript else None)
    print(json.dumps(out, indent=2))
    return 0 if out["measured"] else 1


if __name__ == "__main__":
    sys.exit(main())
