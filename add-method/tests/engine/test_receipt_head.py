"""Red suite for `receipt-anchored-to-head` — a run receipt names the commit it ran against.

A receipt records the blobs it observed and not the commit, so nothing in the bundle can say
whether a tag shipped the tree a PASS verified. `run` now records `head:` (HEAD at run START)
and `committed:` (every scope blob equals HEAD's blob for that path). Outside git, or on an
unborn branch, neither key is written and the receipt's note says why (FORMAT §8.1).

Driven as `.add/tasks/receipt-anchored-to-head.md` under milestone `loop-that-closes`.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

SHA = re.compile(r"\A[0-9a-f]{40}\Z")


def git(*args, cwd):
    return subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=T", *args],
                          cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


def _bundle(tmp_path, scope):
    bundle = tmp_path / ".add"
    add.init(bundle, "code", "P")
    cid, _ = add.new(bundle, "Task", "scoped", title="Scoped", scope=scope)
    return bundle, cid


@pytest.fixture
def committed(tmp_path):
    """A repo with ONE commit holding src/a.py and an unrelated other.py; bundle at .add/."""
    git("init", "-q", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n")
    (tmp_path / "other.py").write_text("y = 2\n")
    git("add", "src/a.py", "other.py", cwd=tmp_path)
    git("commit", "-q", "-m", "one", cwd=tmp_path)
    bundle, cid = _bundle(tmp_path, ["src/a.py"])
    return tmp_path, bundle, cid, git("rev-parse", "HEAD", cwd=tmp_path)


def _run(bundle, cid, cwd, cmd="pass"):
    return add.run(bundle, cid, [sys.executable, "-c", cmd], cwd=cwd)["receipt"]


def test_receipt_records_head_sha(committed):
    """covers: M1, E1 — `head` is HEAD's 40-hex sha, on the returned receipt AND in the Run node."""
    root, bundle, cid, sha = committed
    node = add.run(bundle, cid, [sys.executable, "-c", "pass"], cwd=root)
    assert node["receipt"].get("head") == sha, \
        f"receipt names no commit — head={node['receipt'].get('head')!r}, HEAD={sha}"
    assert SHA.match(str(node["receipt"]["head"]))
    written = Path(node["path"]).read_text()
    assert f"  head: {sha}\n" in written, "the Run node on disk does not carry the head line"


def test_committed_true_when_scope_matches_head(committed):
    """covers: M2, E1 — a clean scope file → `committed` is the bool True."""
    root, bundle, cid, _ = committed
    r = _run(bundle, cid, root)
    assert r.get("committed") is True, f"committed={r.get('committed')!r} on a clean scope"


def test_committed_false_when_scope_edited(committed):
    """covers: M2, E2 — an uncommitted edit inside scope → False, and head does not move."""
    root, bundle, cid, sha = committed
    (root / "src" / "a.py").write_text("x = 2\n")
    r = _run(bundle, cid, root)
    assert r.get("committed") is False, f"committed={r.get('committed')!r} over an edited scope file"
    assert r.get("head") == sha


def test_unrelated_dirt_does_not_flip_committed(committed):
    """covers: R:COMMITTEDBYCLAIM, E4, A2 — dirt OUTSIDE scope is not this receipt's business."""
    root, bundle, cid, _ = committed
    (root / "other.py").write_text("y = 3\n")
    (root / "untracked.py").write_text("z = 4\n")
    r = _run(bundle, cid, root)
    assert r.get("committed") is True, \
        "`committed` read the whole tree (git status) instead of the scope blobs -> R:COMMITTEDBYCLAIM"


def test_no_head_on_unborn_branch_or_outside_git(tmp_path):
    """covers: M3, E3, R:INVENTEDHEAD — no commit, or no git: neither key, and the note says so."""
    # unborn branch: git init, nothing committed
    born = tmp_path / "unborn"
    born.mkdir()
    git("init", "-q", cwd=born)
    (born / "src").mkdir()
    (born / "src" / "a.py").write_text("x = 1\n")
    bundle, cid = _bundle(born, ["src/a.py"])
    r = _run(bundle, cid, born)
    assert "head" not in r and "committed" not in r, \
        f"a sha nobody observed was written on an unborn branch: {r.get('head')!r} -> R:INVENTEDHEAD"
    assert "commit" in str(r.get("note", "")), f"the note does not say why: {r.get('note')!r}"
    # outside git entirely
    plain = tmp_path / "plain"
    (plain / "src").mkdir(parents=True)
    (plain / "src" / "a.py").write_text("x = 1\n")
    bundle, cid = _bundle(plain, ["src/a.py"])
    r = _run(bundle, cid, plain)
    assert "head" not in r and "committed" not in r
    assert "git" in str(r.get("note", ""))


def test_head_read_before_the_command_runs(committed):
    """covers: A3 (probe) — a command that commits mid-run cannot move the anchor."""
    root, bundle, cid, sha = committed
    (root / "src" / "a.py").write_text("x = 5\n")
    cmd = ("import subprocess; subprocess.run(['git','-c','user.email=t@e.c','-c','user.name=T',"
           "'commit','-q','-am','mid-run'], check=True)")
    r = _run(bundle, cid, root, cmd)
    assert r.get("head") == sha, "head was read after the command — it names a commit the digest never saw"
    assert git("rev-parse", "HEAD", cwd=root) != sha, "fixture: the mid-run commit did not happen"


def test_format_states_head_and_committed():
    """covers: M4 — FORMAT §8.1 documents both keys and the absence rule."""
    text = (REPO / "FORMAT.md").read_text()
    sec = text.split("### §8.1", 1)[1].split("### §8.2", 1)[0]
    assert "`head`" in sec or "head:" in sec, "FORMAT §8.1 never names `head`"
    assert "committed" in sec, "FORMAT §8.1 never names `committed`"
    assert "unborn" in sec.lower() or "no commit" in sec.lower(), \
        "FORMAT §8.1 does not state the absence rule for a tree with no commit"
