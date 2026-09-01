"""`_changed_paths` must report the paths git actually named, in the base `scope:` is written in.

Every test here was RED against the first cut of the sensitive-path-vs-diff refusal, and each
corresponds to a defect confirmed by execution during the 2026-09-01 pre-merge review. The
unifying defect: the porcelain `-z` stream was read as if every record carried a status prefix
and every path were relative to the bundle parent. Neither is true, so the guard refused on
paths that do not exist and missed the file that was actually edited.
"""
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _repo(tmp_path):
    add._git(tmp_path, "init", "-q", ".")
    add._git(tmp_path, "config", "user.email", "t@t")
    add._git(tmp_path, "config", "user.name", "t")
    return tmp_path


def _commit(root, msg="c"):
    add._git(root, "add", "-A")
    add._git(root, "commit", "-qm", msg)


def test_an_unstaged_first_path_is_not_mangled(tmp_path):
    """`_git`'s `.strip()` ate the leading status space of the FIRST record.

    Porcelain writes `" M path"` for a worktree edit that is not staged — the ordinary state at
    gate time, since you gate after editing and before committing. Stripped, that record is two
    status chars instead of three, and `rec[3:]` chopped a character off the path.
    """
    root = _repo(tmp_path)
    (root / "deploy").mkdir()
    (root / "deploy" / "secrets.yaml").write_text("a\n", encoding="utf-8")
    _commit(root)
    (root / "deploy" / "secrets.yaml").write_text("a\nb\n", encoding="utf-8")

    assert add._changed_paths(root) == ["deploy/secrets.yaml"]


def test_a_rename_reports_both_real_paths(tmp_path):
    """A rename emits `XY <to>\\0<from>\\0` — the second field carries NO status prefix.

    Read as a status record it lost three characters, so the guard refused on a path that had
    never existed, and its own remedy (add it to `scope:`) yields an entry resolving to nothing.
    """
    root = _repo(tmp_path)
    (root / "deploy").mkdir()
    (root / "deploy" / "secrets.yaml").write_text("a\n", encoding="utf-8")
    _commit(root)
    add._git(root, "mv", "deploy/secrets.yaml", "deploy/secrets-prod.yaml")

    assert sorted(add._changed_paths(root)) == ["deploy/secrets-prod.yaml", "deploy/secrets.yaml"]


def test_paths_are_rebased_onto_the_bundle_parent(tmp_path):
    """`git status --porcelain` prints REPO-ROOT-relative paths whatever the cwd.

    `scope:` entries are bundle-parent-relative. For any bundle not at the repo root — this
    project's own `add-method/.add` is one — the two bases differ, so every sensitive edit
    compared a prefixed path against an unprefixed scope entry and refused permanently.
    """
    root = _repo(tmp_path)
    nested = root / "sub" / "deploy"
    nested.mkdir(parents=True)
    (nested / "secrets.yaml").write_text("a\n", encoding="utf-8")
    _commit(root)
    (nested / "secrets.yaml").write_text("a\nb\n", encoding="utf-8")

    # called with the BUNDLE PARENT (`sub/`), exactly as `gate` calls it with `root.parent`
    assert add._changed_paths(root / "sub") == ["deploy/secrets.yaml"]


def test_a_path_outside_the_bundle_parent_is_not_reported(tmp_path):
    """Nothing above the bundle parent can be named by a `scope:` entry, so reporting it could
    only ever produce a refusal no scope value clears."""
    root = _repo(tmp_path)
    (root / "sub").mkdir()
    (root / "sub" / "kept.txt").write_text("a\n", encoding="utf-8")
    (root / "outside.yaml").write_text("a\n", encoding="utf-8")
    _commit(root)
    (root / "outside.yaml").write_text("a\nb\n", encoding="utf-8")

    assert add._changed_paths(root / "sub") == []


def test_a_non_repo_still_answers_empty(tmp_path):
    """Law 3: a bundle that is not a git working tree stays gateable."""
    assert add._changed_paths(tmp_path) == []


def test_a_coarse_filesystem_does_not_fake_a_stale_report(tmp_path):
    """On a 1-second-granularity filesystem BOTH the epoch sentinel and the report truncate to
    the same second, so a report written DURING the run cannot read as older than the run.

    Comparing against the raw wall clock — the first cut — made that comparison lie, and the
    cost is not a lost evidence rung: emptying the reported IDs leaves every `covers:` referent
    unbound, so `gate` refuses a node whose suite was green.
    """
    report = tmp_path / "r.xml"
    report.write_text("<testsuite/>", encoding="utf-8")
    wall = time.time()
    coarse = float(int(wall))                      # what such a filesystem records
    os.utime(report, (coarse, coarse))

    assert add._report_predates_run(report, coarse) is False
    assert coarse < wall, "the raw clock is what the first cut compared against, and it lied"


def test_the_run_epoch_is_taken_from_the_filesystem_and_leaves_nothing_behind(tmp_path):
    target = tmp_path / "sub" / "r.xml"
    epoch = add._fs_epoch(target, 0.0)

    assert epoch > 0.0, "the epoch fell back to the clock instead of reading the filesystem"
    assert not list(tmp_path.rglob(".add-run-epoch-*")), "the sentinel was left behind"


def test_a_report_written_before_the_run_is_still_caught(tmp_path):
    """The coarse-filesystem tolerance must not blunt the check it protects."""
    report = tmp_path / "r.xml"
    report.write_text("<testsuite/>", encoding="utf-8")
    os.utime(report, (1000.0, 1000.0))

    assert add._report_predates_run(report, time.time()) is True


def _milestone_with_exit(tmp_path, slug, exit_body):
    """A Milestone authored far enough to REACH the tally — the goal and why guards fire first."""
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Milestone", slug, title=slug)
    p = tmp_path / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("goal: <one line>", "goal: prove the goal-gate reads its own input")
    t = re.sub(r"why: <[^>]*>", "why: the tally is the only thing standing between open work and a close", t)
    p.write_text(t[:t.index("## EXIT")] + exit_body, encoding="utf-8")
    return cid


def test_an_unclosed_fence_in_exit_refuses_instead_of_closing(tmp_path):
    """`_box_lines` skips fenced regions — so an unclosed fence made the tally EMPTY.

    `total == 0` takes `milestone_done`'s "no exit criteria, so the goal-gate did not fire"
    branch and CLOSES the milestone, with real unchecked criteria sitting in the file. The
    regex this replaced counted them and refused. A gate that cannot read its input must
    refuse, never tally zero.
    """
    cid = _milestone_with_exit(tmp_path, "unreadable-exit",
                              "## EXIT\n```\nan opening fence that never closes\n"
                              "- [ ] a criterion nobody has met\n- [ ] and a second one\n")

    ok, note = add.milestone_done(tmp_path, cid)
    assert ok is False, f"a milestone with an unreadable EXIT closed: {note}"
    assert "unclosed code fence" in note, note


def test_a_balanced_fence_in_exit_still_tallies(tmp_path):
    """The refusal must be about PARITY, not about fences existing — this bundle's own
    milestones quote `- [x]` inside fences, which is why they are skipped at all."""
    cid = _milestone_with_exit(tmp_path, "quoting-exit",
                              "## EXIT\n```\n- [x] an EXAMPLE box, not a criterion\n```\n"
                              "- [ ] the one real criterion\n")

    ok, note = add.milestone_done(tmp_path, cid)
    assert ok is False and "0/1" in note, note        # refuses on the UNMET criterion, not the fence
    assert "unclosed code fence" not in note, note
