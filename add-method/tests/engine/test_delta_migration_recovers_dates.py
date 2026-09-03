"""The legacy delta lines are migrated by a re-runnable script, dated from git — never invented.

A backfill that stamps today on a line it could not date produces a plausible fiction: the whole
point of the interval is answering "was this true in August", and a fabricated August is worse than
no August at all. So the script recovers `valid_from` from git and a line it cannot date comes back
REPORTED and BYTE-IDENTICAL.

The trap this suite exists for: `git blame` on a FOLDED line returns the commit that FOLDED it, not
the commit that FILED it. That is a date genuinely recovered from git and still wrong, and
R:INVENTEDDATE would not catch it — so `valid_from` is recovered by pickaxing the lesson text to its
filing commit, and `valid_to` from the status-changing commit.

covers the node `.add/tasks/dated-addressable-deltas.md`.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BUNDLE_ROOT = REPO.parent / ".add"
sys.path.insert(0, str(REPO / "tooling"))
sys.path.insert(0, str(REPO / "scripts"))
import add  # noqa: E402

DATED_HEAD = re.compile(r"^- \[[A-Z]+ · [A-Za-z][A-Za-z0-9_-]* · \w+ · [\d\-→]+\] ")
ANY_HEAD = re.compile(r"^- \[[A-Z]+ ·")
TERMINAL = ("folded", "rejected")


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=str(cwd), check=True,
                          capture_output=True, text=True).stdout


def _commit(root, message, date):
    stamp = f"{date}T12:00:00+00:00"
    _git(root, "add", "-A")
    subprocess.run(["git", "commit", "-q", "-m", message, "--date", stamp],
                   cwd=str(root), check=True, capture_output=True, text=True,
                   env={**os.environ, "GIT_COMMITTER_DATE": stamp})


def _bundle_repo(tmp_path):
    add.init(tmp_path, "code", "T")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "T")
    return tmp_path


def _append(root, lens, *lines):
    p = root / "specs" / f"{lens}.md"
    p.write_text(p.read_text(encoding="utf-8").rstrip("\n") + "\n" + "\n".join(lines) + "\n",
                 encoding="utf-8")


def test_the_migration_is_rerunnable(tmp_path):
    """covers: M7 — a second run reports nothing changed and rewrites no byte."""
    import migrate_delta_ids

    root = _bundle_repo(tmp_path)
    _append(root, "method", "- [ADD · open] the oldest lesson (evidence: /tasks/a.md)")
    _commit(root, "seed", "2026-08-11")

    assert not [ln for ln in (root / "specs" / "method.md").read_text(encoding="utf-8").splitlines()
                if DATED_HEAD.match(ln)], "the fixture must start with no dated heads"

    first = migrate_delta_ids.migrate(root, repo_root=root)
    assert first["changed"] == 1, first
    text = (root / "specs" / "method.md").read_text(encoding="utf-8")
    assert [ln for ln in text.splitlines() if DATED_HEAD.match(ln)], text

    second = migrate_delta_ids.migrate(root, repo_root=root)
    assert second["changed"] == 0, f"the script is not re-runnable: {second}"
    assert (root / "specs" / "method.md").read_text(encoding="utf-8") == text, \
        "a second run rewrote the file"


def test_the_migration_recovers_a_filing_date_not_a_fold_date(tmp_path):
    """covers: M7, A11 — blame on a folded line dates the FOLD; the interval needs the FILING."""
    import migrate_delta_ids

    root = _bundle_repo(tmp_path)
    _append(root, "method", "- [ADD · open] a lesson filed early (evidence: /tasks/a.md)")
    _commit(root, "file the lesson", "2026-08-11")

    p = root / "specs" / "method.md"
    p.write_text(p.read_text(encoding="utf-8").replace(
        "[ADD · open] a lesson filed early", "[ADD · folded] a lesson filed early"),
        encoding="utf-8")
    _commit(root, "fold the lesson", "2026-09-01")

    blamed = _git(root, "blame", "-L", "/a lesson filed early/,+1", "--date=short",
                  "--", "specs/method.md")
    assert "2026-09-01" in blamed, (
        f"the fixture must reproduce the trap — blame should return the FOLD date:\n{blamed}")

    report = migrate_delta_ids.migrate(root, repo_root=root)
    assert report["changed"] == 1, report
    line = [ln for ln in p.read_text(encoding="utf-8").splitlines()
            if "a lesson filed early" in ln][0]
    assert "2026-08-11→2026-09-01" in line, (
        f"valid_from must be the filing commit and valid_to the fold commit:\n{line}")


def test_the_migration_reports_a_line_it_cannot_date(tmp_path):
    """covers: R:INVENTEDDATE, A10 — an unblamable line is reported and left byte-identical."""
    import migrate_delta_ids

    root = _bundle_repo(tmp_path)
    _append(root, "method", "- [ADD · open] a committed lesson (evidence: e)")
    _commit(root, "seed", "2026-08-11")

    # A spec git has never seen: nothing can be recovered for its lines.
    orphan = root / "specs" / "quality.md"
    _git(root, "rm", "-q", "--cached", "specs/quality.md")
    _append(root, "quality", "- [TDD · open] a lesson git never saw (evidence: e)")
    before = orphan.read_bytes()

    report = migrate_delta_ids.migrate(root, repo_root=root)
    assert any("git never saw" in u for u in report["undated"]), (
        f"an unblamable line must be reported, not stamped: {report}")
    assert orphan.read_bytes() == before, \
        "the migration rewrote a line whose date it could not recover"
    # and the line it COULD date still moved — a report is not an excuse to do nothing
    assert report["changed"] == 1, report
    assert [ln for ln in (root / "specs" / "method.md").read_text(encoding="utf-8").splitlines()
            if DATED_HEAD.match(ln)], "the datable line must still have moved"


@pytest.mark.skipif(not (BUNDLE_ROOT / "specs").is_dir(),
                    reason="no live .add/ bundle beside this package (a fresh install)")
def test_the_live_specs_are_fully_dated_and_no_lesson_was_lost():
    """covers: M7 — every live delta line parses as dated, and the counts reconcile internally.

    Deliberately NOT pinned to a literal count: this very node files its own lessons with
    `add learn` at close, so `== 40` would be red the moment the method worked. The floor is
    that a real corpus was scanned; the claim is that open == scanned - terminal.
    """
    specs = sorted((BUNDLE_ROOT / "specs").glob("*.md"))
    assert len(specs) == 5, f"expected the five living specs, found {[p.name for p in specs]}"

    heads = [(p.name, ln.strip()) for p in specs
             for ln in p.read_text(encoding="utf-8").splitlines() if ANY_HEAD.match(ln.strip())]
    assert len(heads) >= 43, (
        f"only {len(heads)} delta lines were scanned — the corpus held 43 at migration time, "
        f"so this guard is reading the wrong tree")

    legacy = [(n, ln) for n, ln in heads if not DATED_HEAD.match(ln)]
    assert not legacy, f"{len(legacy)} live delta line(s) were never migrated: {legacy[:3]}"

    terminal = [ln for _, ln in heads if any(f" · {s} · " in ln for s in TERMINAL)]
    items, note = add.deltas(BUNDLE_ROOT)
    # The report is identified by its `!` marker, never by the WORD: a live lesson may discuss
    # malformed lines (one does), and a substring search over arbitrary prose reads it as a defect.
    reported = [ln for ln in note.splitlines() if ln.lstrip().startswith("!")]
    assert not reported, f"the migration produced a malformed line:\n" + "\n".join(reported)
    assert len(items) == len(heads) - len(terminal), (
        f"open ({len(items)}) != scanned ({len(heads)}) - terminal ({len(terminal)}) — "
        f"a lesson was lost:\n{note}")
    assert all(i.id and i.valid_from for i in items), \
        [i for i in items if not (i.id and i.valid_from)][:3]
