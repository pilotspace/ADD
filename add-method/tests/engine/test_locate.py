"""`add locate <path>` — the scope reverse lookup (B5, recovered verb).

Read-only: `locate(root, query)` returns every node whose `scope:` matches the path (equal, or one a
directory-prefix of the other). It answers "which task owns this file?" without hand-scanning.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
import cli  # noqa: E402


def _run(root, *argv):
    return cli.main(["--root", str(root), *argv])


def _snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Milestone", "m", title="m")
    add.new(tmp_path, "Task", "auth", title="auth", milestone="m", scope=["src/auth.py"])
    add.new(tmp_path, "Task", "api", title="api", milestone="m", scope=["src/api/routes.py"])


def _slugs(hits):
    return {cid.rsplit("/", 1)[-1][:-3] for cid, *_ in hits}


def test_locate_finds_exact_and_prefix(tmp_path):
    """covers: M1, E1 — an exact path and a dir-prefix both locate the owning node."""
    _bundle(tmp_path)
    exact, _ = add.locate(tmp_path, "src/auth.py")
    assert _slugs(exact) == {"auth"}, exact
    under, _ = add.locate(tmp_path, "src/api")      # dir query locates a file scoped beneath it
    assert _slugs(under) == {"api"}, under
    dir_up, _ = add.locate(tmp_path, "src")         # both tasks live under src/
    assert _slugs(dir_up) == {"auth", "api"}, dir_up


def test_locate_no_match_is_empty(tmp_path):
    """covers: E2 — a path no node scopes returns empty hits and a clear note."""
    _bundle(tmp_path)
    hits, note = add.locate(tmp_path, "docs/readme.md")
    assert hits == [], hits
    assert "no node" in note.lower(), note


def test_locate_writes_nothing(tmp_path):
    """covers: M2, R:LOCATEWRITES — a locate mutates no bundle bytes."""
    _bundle(tmp_path)
    before = _snapshot(tmp_path)
    add.locate(tmp_path, "src/auth.py")
    assert _snapshot(tmp_path) == before, "locate must write nothing (law 3)"


def test_locate_cli_dispatches(tmp_path):
    """covers: M3 — `add locate <path>` exits 0 and the anti-seam maps `locate`."""
    _bundle(tmp_path)
    assert _run(tmp_path, "locate", "src/auth.py") == 0
    assert hasattr(add, "locate")
