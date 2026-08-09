"""`scope_digest` expands a directory scope entry to the files under it (field-report finding #6).

A task whose `scope:` names a directory used to get an empty digest, so `gate` refused with "freshness
cannot be established" — the receipt could only claim `mtime`. A directory scope must contribute the
blobs of the files beneath it (build noise excluded), so a dir-scoped task is content-fresh-gatable.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _git_repo(root):
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    return root


def _paths(digest):
    return {d["path"] for d in digest}


def test_directory_scope_is_hashed(tmp_path):
    """covers: M1 — a scope dir yields one blob per file under it."""
    root = _git_repo(tmp_path)
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text("A\n")
    (root / "src" / "b.py").write_text("B\n")
    digest = add.scope_digest(root, ["src"])
    assert _paths(digest) == {"src/a.py", "src/b.py"}, f"a dir scope must hash its files, got {digest}"
    assert all(d["blob"].startswith("sha1:") for d in digest)


def test_nested_files_are_included(tmp_path):
    """covers: M1 — files in a subdirectory of the scope dir are hashed too."""
    root = _git_repo(tmp_path)
    (root / "src" / "deep").mkdir(parents=True)
    (root / "src" / "top.py").write_text("T\n")
    (root / "src" / "deep" / "inner.py").write_text("I\n")
    assert _paths(add.scope_digest(root, ["src"])) == {"src/top.py", "src/deep/inner.py"}


def test_build_noise_is_excluded(tmp_path):
    """covers: M2 — __pycache__/*.pyc under the dir is not in the digest."""
    root = _git_repo(tmp_path)
    (root / "src" / "__pycache__").mkdir(parents=True)
    (root / "src" / "a.py").write_text("A\n")
    (root / "src" / "__pycache__" / "a.cpython-314.pyc").write_bytes(b"\x00bytecode")
    assert _paths(add.scope_digest(root, ["src"])) == {"src/a.py"}, "bytecode must not pollute the digest"


def test_file_scope_is_unchanged(tmp_path):
    """covers: R:FILEUNCHANGED — a single-file scope still yields exactly its one blob."""
    root = _git_repo(tmp_path)
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text("A\n")
    (root / "src" / "b.py").write_text("B\n")
    digest = add.scope_digest(root, ["src/a.py"])
    assert _paths(digest) == {"src/a.py"}, f"a file scope must hash only that file, got {digest}"


def test_outside_git_returns_empty(tmp_path):
    """covers: R:NOGIT — a non-git dir returns [] (mtime fallback), never a fabricated digest."""
    plain = tmp_path / "not-a-repo"
    (plain / "src").mkdir(parents=True)
    (plain / "src" / "a.py").write_text("A\n")
    assert add.scope_digest(plain, ["src"]) == []
