#!/usr/bin/env python3
"""Backfill a bundle's legacy delta lines with an id and a validity interval. Re-runnable.

    python3 add-method/scripts/migrate_delta_ids.py [--root .add] [--dry-run]

A legacy head — `- [ADD · open] the lesson (evidence: …)` — carries no address and no time. This
walks every `specs/*.md`, recovers each line's dates from git, and rewrites the head as
`- [ADD · M12 · open · 2026-08-11] …`. An already-dated line is left exactly as it is, so a second
run is a no-op and the script can be re-run after a `join` merges undated lines back in.

Two rules it will not bend:

* **A date is recovered, never invented.** If git can tell us nothing about a line, the line is
  reported and left byte-identical. A stamped-today date would be a fiction that reads as evidence,
  and the whole point of the interval is answering "was this true in August".
* **`git blame` on a FOLDED line returns the commit that FOLDED it, not the one that FILED it.**
  That is a date genuinely recovered from git and still wrong — and no honesty check would catch
  it. So `valid_from` comes from pickaxing the lesson TEXT back to the commit that introduced it
  (`git log -S`), and `valid_to`, for a terminal status, from `blame` on the line as it stands now.

Ids are assigned ascending from the BOTTOM of each file upward: `learn` prepends, so the file reads
newest-first and the oldest lesson earns the lowest id. The spec's `delta_seq:` high-water is set to
the largest id assigned, so the next `add learn` cannot collide with anything this wrote.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tooling"))
import add  # noqa: E402


def _git(repo_root, *args):
    """Run a git command, returning stdout — or None when git can tell us nothing."""
    try:
        done = subprocess.run(["git", *args], cwd=str(repo_root),
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def _filed_on(repo_root, rel, lesson):
    """The date the lesson TEXT first entered the file — pickaxed, so a later fold cannot shadow it.

    `git log -S` walks the history for the commit that changed the number of occurrences of this
    string; the LAST such commit in the log is the earliest, which is the filing.
    """
    probe = " ".join(lesson.split())[:120]
    if not probe:
        return None
    out = _git(repo_root, "log", "--format=%ad", "--date=short", "-S", probe, "--", str(rel))
    dates = [ln.strip() for ln in (out or "").splitlines() if ln.strip()]
    return dates[-1] if dates else None


def _line_no(path, exact):
    """The 1-based PHYSICAL line number of `exact` in the file, or None.

    Blame is addressed by number, never by `-L /regex/`: a delta's text is prose and routinely
    holds `[`, `(` and `/`, which are regex metacharacters in git's own dialect. Python's
    `re.escape` does not translate into it (an escaped space, in particular), so a perfectly
    ordinary lesson silently matched nothing and came back undatable. A number cannot be misread.
    """
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip() == exact.strip():
            return n
    return None


def _touched_on(repo_root, rel, path, exact):
    """The date of the COMMIT that last touched this line — its blame.

    An uncommitted line blames to the all-zero sha as "Not Committed Yet", and git dates it TODAY.
    Reading that as a recovered date is the exact fiction R:INVENTEDDATE forbids — it would wear
    git's authority while being nothing but the clock. An unborn line recovers NOTHING.
    """
    n = _line_no(path, exact)
    if n is None:
        return None
    out = _git(repo_root, "blame", "-L", f"{n},{n}", "--date=short", "--", str(rel))
    if not out or re.match(r"\^?0{8,}\b", out.strip()):
        return None
    found = re.search(r"(\d{4}-\d{2}-\d{2})", out)
    return found.group(1) if found else None


def migrate(root, repo_root=None, dry_run: bool = False) -> dict:
    """Migrate every spec under `root`. Returns a report; never raises on a line it cannot date."""
    root = Path(root)
    repo_root = Path(repo_root) if repo_root else root.parent
    report = {"changed": 0, "skipped": 0, "undated": [], "uncorroborated": [], "files": []}

    for path in sorted((root / "specs").glob("*.md")):
        rel = path.relative_to(repo_root) if path.is_relative_to(repo_root) else path
        node = add.read(path, "T2")
        lines = node["body"].splitlines(keepends=True)

        # Bottom-up: the oldest lesson sits last, and earns the lowest id.
        order = [i for i in range(len(lines) - 1, -1, -1)
                 if add.DELTA_LINE.match(lines[i].strip())
                 and add.DELTA_SHAPE.match(lines[i].strip())]
        seq = add._delta_high_water(node["raw"], lines)
        letter = add._delta_letter(path.stem)
        touched = False

        for i in order:
            raw = lines[i]
            m = add.DELTA_LINE.match(raw.strip())
            head, tail = m.group(1), m.group(2)
            rec = add.parse_delta_head(head)
            if rec["id"] is not None or rec["code"] is not None:
                report["skipped"] += 1          # already dated, or malformed — not ours to guess at
                continue

            lesson = tail.split("(evidence:")[0].strip()
            filed = _filed_on(repo_root, rel, lesson) or _touched_on(repo_root, rel, path, raw)
            if not filed:
                # Recovered nothing. Report it and leave the line byte-identical (R:INVENTEDDATE).
                report["undated"].append(f"{path.stem}: {lesson[:90]}")
                continue

            seq += 1
            interval = filed
            if rec["status"] in add.DELTA_TERMINAL:
                closed = _touched_on(repo_root, rel, path, raw)
                if closed and closed >= filed:
                    interval = f"{filed}{add.DELTA_ARROW}{closed}"
                else:
                    # The close is genuinely unknown. A one-ended terminal is tolerated by the
                    # parser precisely so this stays honest rather than becoming a guess.
                    report["undated"].append(f"{path.stem} (close only): {lesson[:90]}")
            new_head = f"{rec['comp']} · {letter}{seq} · {rec['status']} · {interval}"
            lines[i] = raw.replace(f"[{head}]", f"[{new_head}]", 1)
            report["changed"] += 1
            touched = True

            corroborated = _corroborate(root, tail, filed)
            if corroborated is False:
                report["uncorroborated"].append(f"{path.stem}: {lesson[:70]} — blamed {filed}")

        if touched and not dry_run:
            raw_fm = add.set_key(node["raw"], "delta_seq", str(seq))
            add.write(path, f"---\n{raw_fm}\n---\n{''.join(lines)}")
            report["files"].append(path.name)

    return report


def _corroborate(root, tail, blamed):
    """True/False when the delta's evidence names a task node whose own dates agree; None when
    there is nothing independent to check it against.

    A reflow commit would re-date every line in a file at once, and blame would report it with a
    straight face. Where the evidence points at a task node, that node's own stamps are a second,
    independent witness.

    Which stamp, though, matters. Comparing only against `generated.at` raised a false alarm on the
    live corpus: a task authored 2026-08-17 and gated 2026-09-01 files its lessons at CLOSE, so the
    blame date matched the gate and disagreed with the birth. A lesson is filed either when the node
    is written or when it closes, so EVERY date the node carries is a legitimate witness.
    """
    ref = re.search(r"\(evidence:\s*(/tasks/([a-z0-9-]+)(?:\.d/[^)]*)?\.md)\)", tail)
    if not ref:
        return None
    node = Path(root) / "tasks" / f"{ref.group(2)}.md"
    if not node.is_file():
        return None
    head = node.read_text(encoding="utf-8").split("\n---", 2)[0]
    witnesses = re.findall(r"at:\s*(\d{4}-\d{2}-\d{2})", head)
    if not witnesses:
        return None
    from datetime import date
    blamed_on = date.fromisoformat(blamed)
    return any(abs((blamed_on - date.fromisoformat(w)).days) <= 3 for w in witnesses)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".add", help="the bundle root (default: .add)")
    ap.add_argument("--repo-root", default=None, help="the git repo the specs live in")
    ap.add_argument("--dry-run", action="store_true", help="report without writing")
    args = ap.parse_args(argv)

    report = migrate(args.root, repo_root=args.repo_root, dry_run=args.dry_run)
    print(f"migrated {report['changed']} delta line(s); {report['skipped']} already dated")
    for name in report["files"]:
        print(f"  · specs/{name}")
    for line in report["undated"]:
        print(f"  ! no date recoverable, line left untouched — {line}")
    for line in report["uncorroborated"]:
        print(f"  ? blame disagrees with the cited task node's own stamp — {line}")
    if not report["undated"] and not report["uncorroborated"]:
        print("every migrated date was recovered from git; none disagreed with its evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
