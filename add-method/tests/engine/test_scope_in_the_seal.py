"""Red direction check for scope-in-the-seal."""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
from conftest import draft_direction  # noqa: E402


def _authored(root, slug, scope):
    cid, _ = add.new(root, "Task", slug, title=slug, scope=scope)
    task = draft_direction(root, cid)
    task.write_text(task.read_text().replace("## PLAN", "## PLAN\nregression: none · fixture", 1),
                    encoding="utf-8")
    return cid, task


def _human_frozen(root, slug, scope):
    """A real human-floor freeze, including the interview the engine requires."""
    cid, task = _authored(root, slug, scope)
    node = add.read(task, "T2")
    add.write(task, f"---\n{add.set_key(node['raw'], 'sensitivity', 'security')}\n---\n{node['body']}")
    questions, note = add.interview(root, cid)
    assert questions, note
    answers = {q["id"]: "confirm" for q in questions}
    assert add.interview(root, cid, answers, by="human:T")[0]
    assert add.freeze(root, cid, by="human:T", authority="human")[0]
    return cid, task


def test_freeze_and_refreeze_stamp_complete_scope(tmp_path):
    """covers: M1 — both writers carry a digest over a multi-entry scope and a changed list re-digests."""
    root = tmp_path / ".add"
    add.init(root, "code", "scope stamp")
    cid, task = _authored(root, "owner", ["src/a.py", "src/b.py"])
    assert add.freeze(root, cid, by="plan:T", authority="plan")[0]
    first = add.read(task, "T2")["fm"]["verified"][-1]
    node = add.read(task, "T2")
    add.write(task, f"---\n{add.set_key(node['raw'], 'scope', ['src/a.py', 'src/c.py'])}\n---\n{node['body']}")
    assert add.freeze(root, cid, by="plan:T", authority="plan")[0]
    second = add.read(task, "T2")["fm"]["verified"][-1]
    assert str(first.get("scope", "")).startswith("sha256:"), f"freeze omitted scope digest: {first!r}"
    assert str(second.get("scope", "")).startswith("sha256:"), f"refreeze omitted scope digest: {second!r}"
    assert first["scope"] != second["scope"], "a changed multi-entry scope kept its prior seal"


def test_scope_digest_normalizes_order_and_duplicates(tmp_path):
    """covers: M1, A2 — order and duplicate entries do not change the authorized path set."""
    root = tmp_path / ".add"
    add.init(root, "code", "scope canonicalization")
    cid, task = _authored(root, "owner", ["src/b.py", "src/a.py", "src/a.py"])
    assert add.freeze(root, cid, by="plan:T", authority="plan")[0]
    first = add.read(task, "T2")["fm"]["verified"][-1]
    node = add.read(task, "T2")
    add.write(task, f"---\n{add.set_key(node['raw'], 'scope', ['src/a.py', 'src/b.py'])}\n---\n{node['body']}")
    assert add.freeze(root, cid, by="plan:T", authority="plan")[0]
    second = add.read(task, "T2")["fm"]["verified"][-1]
    assert first.get("scope") == second.get("scope") and first.get("scope"), (
        "behaviorally identical scope sets produced different or empty seals")


def test_latest_refreeze_wins_and_unchanged_scope_routes(tmp_path):
    """covers: M2, E1 — a matching latest seal routes; an older matching seal never outranks it."""
    root = tmp_path / ".add"
    add.init(root, "code", "latest seal")
    for name in ("a.py", "b.py"):
        path = root.parent / "src" / name
        path.parent.mkdir(exist_ok=True)
        path.write_text(name, encoding="utf-8")
    cid, task = _human_frozen(root, "owner", ["src/a.py"])
    assert add._scoped_by_any(root.parent, add.scan(root), "src/a.py"), "an unchanged human seal did not route"
    node = add.read(task, "T2")
    add.write(task, f"---\n{add.set_key(node['raw'], 'scope', ['src/b.py'])}\n---\n{node['body']}")
    assert add.freeze(root, cid, by="human:T", authority="human")[0]
    assert add._scoped_by_any(root.parent, add.scan(root), "src/b.py"), "the latest matching refreeze did not route"
    node = add.read(task, "T2")
    add.write(task, f"---\n{add.set_key(node['raw'], 'scope', ['src/a.py'])}\n---\n{node['body']}")
    assert not add._scoped_by_any(root.parent, add.scan(root), "src/a.py"), (
        "an older matching freeze outranked the latest refreeze")


def test_legacy_and_changed_scopes_fail_closed(tmp_path):
    """covers: R:LEGACY_SCOPE, R:STALE_SCOPE, E2 — absent, malformed, and stale seals route nothing."""
    root = tmp_path / ".add"
    add.init(root, "code", "scope seal")
    (root.parent / "src/auth").mkdir(parents=True)
    (root.parent / "src/auth/b.py").write_text("b\n", encoding="utf-8")
    index = add.read(root / "index.md", "T2")
    add.write(root / "index.md", "---\n" + add.set_key(index["raw"], "sensitive_paths", "[src/auth/**]")
              + "\n---\n" + index["body"])
    cid, _ = add.new(root, "Task", "legacy", title="legacy", scope=["src/auth/b.py"],
                     sensitivity="security")
    path = root / cid.lstrip("/")
    node = add.read(path, "T2")
    raw = node["raw"].replace("verified: []", "verified:\n  - { by: \"human:T\", at: 2026-09-14, act: freeze, authority: human }")
    add.write(path, f"---\n{raw}\n---\n{node['body']}")
    assert not add._scoped_by_any(root.parent, add.scan(root), "src/auth/b.py"), (
        "R:LEGACY_SCOPE — a stamp without scope coverage routed a sensitive path")

    node = add.read(path, "T2")
    raw = node["raw"].replace("authority: human }", "authority: human, scope: malformed }")
    add.write(path, f"---\n{raw}\n---\n{node['body']}")
    assert not add._scoped_by_any(root.parent, add.scan(root), "src/auth/b.py"), (
        "R:LEGACY_SCOPE — a malformed scope seal routed a sensitive path")

    (root.parent / "src/auth/a.py").write_text("a\n", encoding="utf-8")
    cid, task = _human_frozen(root, "changed", ["src/auth/a.py"])
    node = add.read(task, "T2")
    add.write(task, f"---\n{add.set_key(node['raw'], 'scope', ['src/auth/b.py'])}\n---\n{node['body']}")
    assert not add._scoped_by_any(root.parent, add.scan(root), "src/auth/b.py"), (
        "R:STALE_SCOPE — changing scope after a sealed freeze routed the new path")

    # Quoted YAML preserves whitespace inside the value, and the scope reader preserves it too.
    # Trimming only in the seal would let a behavior-changing edit keep the same digest.
    cid, task = _authored(root, "spaced", ["src/auth/b.py"])
    node = add.read(task, "T2")
    raw = node["raw"].replace("  - src/auth/b.py", '  - " src/auth/b.py "', 1)
    raw = add.set_key(raw, "sensitivity", "security")
    add.write(task, f"---\n{raw}\n---\n{node['body']}")
    questions, note = add.interview(root, cid)
    assert questions, note
    assert add.interview(root, cid, {q["id"]: "confirm" for q in questions}, by="human:T")[0]
    assert add.freeze(root, cid, by="human:T", authority="human")[0]
    assert not add._scoped_by_any(root.parent, add.scan(root), "src/auth/b.py"), \
        "the padded entry unexpectedly held the unpadded path"
    node = add.read(task, "T2")
    add.write(task, f"---\n{add.set_key(node['raw'], 'scope', ['src/auth/b.py'])}\n---\n{node['body']}")
    assert not add._scoped_by_any(root.parent, add.scan(root), "src/auth/b.py"), (
        "R:STALE_SCOPE — trimming quoted entry whitespace changed routing under the old seal")

    # Joining entries with a newline makes one block-scalar entry collide with two list entries.
    cid, task = _authored(root, "block", ["src/auth/a.py", "src/auth/b.py"])
    node = add.read(task, "T2")
    raw = node["raw"].replace(
        "scope:\n  - src/auth/a.py\n  - src/auth/b.py",
        "scope: |\n  src/auth/a.py\n  src/auth/b.py", 1)
    raw = add.set_key(raw, "sensitivity", "security")
    add.write(task, f"---\n{raw}\n---\n{node['body']}")
    questions, note = add.interview(root, cid)
    assert questions, note
    assert add.interview(root, cid, {q["id"]: "confirm" for q in questions}, by="human:T")[0]
    assert add.freeze(root, cid, by="human:T", authority="human")[0]
    assert not add._scoped_by_any(root.parent, add.scan(root), "src/auth/a.py"), \
        "the block scalar unexpectedly held either embedded path"
    node = add.read(task, "T2")
    add.write(task, f"---\n{add.set_key(node['raw'], 'scope', ['src/auth/a.py', 'src/auth/b.py'])}\n---\n{node['body']}")
    assert not add._scoped_by_any(root.parent, add.scan(root), "src/auth/a.py"), (
        "R:STALE_SCOPE — block scalar and entry list collided under one scope seal")


def test_scope_owner_reads_refreeze_and_open_closed_states(tmp_path):
    """covers: M3 — a valid refreeze owns every entry on an open Task; a closed Task is history."""
    root = tmp_path / ".add"
    add.init(root, "code", "refreeze owner")
    (root.parent / "src").mkdir()
    (root.parent / "src/b.py").write_text("b\n", encoding="utf-8")
    cid, task = _authored(root, "owner", ["src/missing.py", "src/b.py"])
    assert add.freeze(root, cid, by="plan:T", authority="plan")[0]
    assert add.freeze(root, cid, by="plan:T", authority="plan")[0]
    node = add.read(task, "T2")
    # Keep only the latest seal. Current routing looks only for `act: freeze`; the repair must
    # recognize the valid `refreeze` record it just wrote.
    raw = re.sub(r"\n  - \{[^\n]*act: freeze,[^\n]*\}", "", node["raw"], count=1)
    add.write(task, f"---\n{raw}\n---\n{node['body']}")
    hit = add.quick_hit(root, add.scan(root), ["src/b.py"])
    assert hit == ("scope", "src/b.py", cid), f"an open refreeze did not own its scope: {hit!r}"
    node = add.read(task, "T2")
    add.write(task, f"---\n{add.set_key(node['raw'], 'status', 'done')}\n---\n{node['body']}")
    assert add.quick_hit(root, add.scan(root), ["src/b.py"]) is None, "a closed Task still owned a quick path"
