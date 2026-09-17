"""Red direction check for holds-against-the-commit."""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
from conftest import draft_direction, git  # noqa: E402


def _commit(work, message):
    git("add", "-A", cwd=work)
    git("commit", "-q", "-m", message, cwd=work)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=work, check=True,
                          capture_output=True, text=True).stdout.strip()


def _assert_scope_holds_from_both_checkouts(tmp_path, operation):
    work = tmp_path / operation
    work.mkdir()
    git("init", "-q", cwd=work)
    git("config", "user.email", "t@example.com", cwd=work)
    git("config", "user.name", "T", cwd=work)
    root = work / ".add"
    add.init(root, "code", "commit scope")
    owned = work / "src/owned.py"
    owned.parent.mkdir()
    owned.write_text("owned\n", encoding="utf-8")
    _commit(work, "add owner")
    cid, _ = add.new(root, "Task", "owner", title="owner", scope=["src/owned.py"])
    task = draft_direction(root, cid)
    task.write_text(task.read_text().replace("## PLAN", "## PLAN\nregression: none · fixture", 1), encoding="utf-8")
    assert add.freeze(root, cid, by="plan:T", authority="plan")[0]
    _commit(work, "seal owner")

    if operation == "delete":
        owned.unlink()
    else:
        owned.rename(work / "src/renamed.py")
    evidence = _commit(work, operation)
    for revision, label in ((f"{evidence}^", "before"), (evidence, "after")):
        subprocess.run(["git", "checkout", "-q", revision], cwd=work, check=True)
        landed, note = add.learn(root, "method", "quick: retire owned code", evidence=evidence)
        assert landed is None and "R:QUICKSIZEUP" in note, (
            f"R:WORKTREE_SCOPE — the same {operation} evidence changed outcome on the {label} checkout: {note!r}")


def test_deleted_scope_holds_from_both_checkout_states(tmp_path):
    """covers: M1, R:WORKTREE_SCOPE, E1 — deletion routing is anchored to the cited commit."""
    _assert_scope_holds_from_both_checkouts(tmp_path, "delete")


def test_renamed_scope_holds_from_both_checkout_states(tmp_path):
    """covers: M2, R:WORKTREE_SCOPE, E2 — rename routing is anchored to the cited commit."""
    _assert_scope_holds_from_both_checkouts(tmp_path, "rename")
