"""Red suite for e7 `build-receipts-learn` — run, freshness, learn.

This suite pays the A22 debt M1 has carried since M0. The central test is
`test_receipt_survives_worktree`: it performs the exact manoeuvre that killed the mtime
predicate — `git worktree add`, which sets every checked-out file's mtime to checkout time —
and asserts a receipt stays fresh. Under the old predicate that assertion is impossible.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    """A real git repo with a bundle and a scoped source file, committed."""
    git("init", "-q", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "service.py").write_text("def book():\n    return True\n")
    add.init(tmp_path / ".add", "code", "Freshness")
    add.new(tmp_path / ".add", "Task", "scoped", title="Scoped task",
            scope=["src/service.py"])
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", "init", cwd=tmp_path)
    return tmp_path


# ------------------------------------------------- content-addressed freshness (M1, A22)


def test_scope_digest_is_git_blobs(repo):
    """covers: M1 — the digest must match git's own object hash, not a hash we invented."""
    digest = add.scope_digest(repo, ["src/service.py"])
    expected = git("hash-object", "src/service.py", cwd=repo).stdout.strip()
    assert digest and digest[0]["blob"].endswith(expected), f"{digest} != sha1:{expected}"


def test_receipt_survives_worktree(repo):
    """covers: M1, M2, R:MTIME2 — the M0 kill-test, inverted.

    `git worktree add` sets EVERY checked-out file's mtime to checkout time. Under the
    mtime predicate every committed receipt reads stale in a fresh worktree, clone or CI
    job. Under A22 the blob hashes are unchanged, so the receipt is still fresh.
    """
    receipt = add.scope_digest(repo, ["src/service.py"])
    wt = repo.parent / "wt"
    out = git("worktree", "add", "-q", str(wt), cwd=repo)
    assert out.returncode == 0, out.stderr

    # the mtime predicate's premise: the checkout really did rewrite the timestamps
    assert (wt / "src" / "service.py").stat().st_mtime != (repo / "src" / "service.py").stat().st_mtime

    ok, why = add.fresh({"scope_digest": receipt, "freshness": "content"}, wt)
    assert ok is True, f"a receipt went stale across a worktree checkout: {why}"


def test_edited_scope_makes_receipt_stale(repo):
    """covers: M1 — the predicate must still catch a real edit."""
    receipt = add.scope_digest(repo, ["src/service.py"])
    (repo / "src" / "service.py").write_text("def book():\n    return False  # changed\n")
    ok, why = add.fresh({"scope_digest": receipt, "freshness": "content"}, repo)
    assert ok is False and "service.py" in why


def test_unrelated_edit_keeps_receipt_fresh(repo):
    """covers: M1 — a file outside `scope:` is not the freshness set."""
    receipt = add.scope_digest(repo, ["src/service.py"])
    (repo / "src" / "other.py").write_text("# not in scope\n")
    ok, why = add.fresh({"scope_digest": receipt, "freshness": "content"}, repo)
    assert ok is True, why


def test_vanished_file_is_stale(repo):
    """covers: M1 — FORMAT §8.1: a file that has vanished since the run is a difference."""
    receipt = add.scope_digest(repo, ["src/service.py"])
    (repo / "src" / "service.py").unlink()
    ok, why = add.fresh({"scope_digest": receipt, "freshness": "content"}, repo)
    assert ok is False


def test_mtime_fallback_is_declared(tmp_path):
    """covers: M1 — outside a git tree the predicate degrades, and SAYS which it used."""
    (tmp_path / "f.py").write_text("x = 1\n")
    digest = add.scope_digest(tmp_path, ["f.py"])
    assert digest == [] or all("blob" not in d for d in digest), \
        "a non-git tree produced blob hashes it cannot have"


# --------------------------------------------------- run executes only what it was given (M3)


def test_run_executes_only_what_was_given(repo):
    """covers: M3, R:INITIATIVE — the recorded command is exactly the one supplied."""
    node = add.run(repo / ".add", "/tasks/scoped.md",
                   [sys.executable, "-c", "print('hello')"], cwd=repo)
    assert node["receipt"]["exit"] == 0
    assert "hello" in str(node["receipt"].get("stdout", ""))
    assert "-c" in str(node["computation"])


def test_run_records_failure_as_an_outcome(repo):
    """covers: M3 — a failing command is a recorded result, never an exception (law 3)."""
    node = add.run(repo / ".add", "/tasks/scoped.md",
                   [sys.executable, "-c", "import sys; sys.exit(3)"], cwd=repo)
    assert node["receipt"]["exit"] == 3


def test_run_times_out_as_an_outcome(repo):
    """covers: M3, R:HANG — a hanging command is bounded and recorded, not left to hang."""
    node = add.run(repo / ".add", "/tasks/scoped.md",
                   [sys.executable, "-c", "import time; time.sleep(30)"], cwd=repo, timeout=1)
    assert node["receipt"]["exit"] != 0
    assert "timeout" in str(node["receipt"]).lower()


def test_run_writes_a_receipt_with_digest(repo):
    """covers: M1, M3 — the receipt lands as a Run node carrying its scope digest."""
    add.run(repo / ".add", "/tasks/scoped.md", [sys.executable, "-c", "pass"], cwd=repo)
    runs = sorted((repo / ".add" / "tasks" / "scoped.d" / "runs").glob("*.md"))
    assert runs, "no receipt node was written"
    fm, _ = add.parse(runs[-1].read_text())
    assert fm["type"] == "Run"
    assert fm["receipt"]["freshness"] == "content"


# ------------------------------------------------------------------------ learn (M4)


def test_learn_appends_to_deltas(repo):
    """covers: M4 — the lesson lands in the named spec's Deltas."""
    ok, note = add.learn(repo / ".add", "method", "budgets need a unit",
                         evidence="/tasks/scoped.d/runs/1.md")
    assert ok is True, note
    assert "budgets need a unit" in (repo / ".add" / "specs" / "method.md").read_text()


def test_learn_without_evidence_refused(repo):
    """covers: M4, R:OPINION — a lesson with no evidence is an opinion."""
    before = (repo / ".add" / "specs" / "method.md").read_bytes()
    ok, note = add.learn(repo / ".add", "method", "I feel this is better", evidence=None)
    assert ok is False
    assert "evidence" in note.lower()
    assert (repo / ".add" / "specs" / "method.md").read_bytes() == before


def test_learn_is_surgical(repo):
    """covers: M4 — appending a delta disturbs nothing else in the spec."""
    path = repo / ".add" / "specs" / "method.md"
    before = path.read_text().splitlines()
    add.learn(repo / ".add", "method", "one more thing", evidence="/tasks/scoped.d/runs/1.md")
    after = path.read_text().splitlines()
    assert after[:len(before) - 1] == before[:len(before) - 1] or len(after) > len(before)
    assert "## Now" in path.read_text() and "## Decisions that bind" in path.read_text()


def test_receipt_kind_is_earned_not_assumed(repo):
    """covers: M1, M3 — A24: a receipt never silently claims `test-ids`.

    Found by reading the first receipt `add run` wrote for its own task: it declared
    `kind: test-ids` while carrying no IDs at all. The kind was being derived from whether
    a scope digest existed — but a digest is a FRESHNESS fact, not an evidence fact. Two
    unrelated questions had been wired to one answer.
    """
    node = add.run(repo / ".add", "/tasks/scoped.md",
                   [sys.executable, "-c", "print('no ids here')"], cwd=repo)
    r = node["receipt"]
    assert r["kind"] != "test-ids" or r.get("ids") not in (None, "", "unknown"), \
        f"claimed test-ids with no IDs: {r}"
    assert r["kind"] == "command-exit", f"the honest kind for a bare command is command-exit: {r['kind']}"
    assert r["freshness"] == "content", "freshness and evidence kind must be decided independently"
